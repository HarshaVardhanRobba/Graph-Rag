import json
import logging
import os
import time
from typing import Dict, List

from google import genai

from ontology import (
    RELATIONSHIP_PROMPT,
    is_valid_relation,
    normalize_entity,
)

logger = logging.getLogger(__name__)


class RelationshipExtractionError(RuntimeError):
    """Raised when the configured relationship-extraction service is unavailable."""

RELATIONSHIP_EXTRACTION_PROMPT = """
You are an expert Knowledge Graph extraction system.

Your task is to identify ONLY relationships between the given entities.

Allowed Relationship Types:

{relationship_types}

Entities:

{entities}

Instructions:

1. Only use the entities provided.
2. Do not invent new entities.
3. Do not invent new relationship types.
4. Return ONLY JSON.

Output Format:

{{
    "relationships":[
        {{
            "source":"K-Means",
            "relation":"USES",
            "target":"Centroid"
        }}
    ]
}}

TEXT:

{chunk}
"""


class RelationshipExtractor:
    """
    Extracts relationships between previously extracted entities.
    """

    def __init__(self):

        try:

            self.client = genai.Client(
                api_key=os.getenv("gemini_api_key")
            )

            self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
            self.request_delay_seconds = float(
                os.getenv("GEMINI_REQUEST_DELAY_SECONDS", "4")
            )
            self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))

        except Exception as e:

            logger.exception(
                f"Failed to initialize Gemini client: {e}"
            )

            self.client = None
            self.model = None

    # --------------------------------------------------
    # Step 1 : Extract Relationships
    # --------------------------------------------------

    def extract(
        self,
        chunk: str,
        entities: List[Dict],
    ) -> str:

        if self.client is None:

            logger.error("Gemini client is not initialized.")

            return ""

        if not isinstance(chunk, str):

            logger.error("Chunk must be a string.")

            return ""

        chunk = chunk.strip()

        if not chunk:

            logger.warning("Empty chunk received.")

            return ""

        if not entities:

            logger.warning(
                "No entities found. Skipping relationship extraction."
            )

            return ""

        entity_names = "\n".join(

            entity["name"]

            for entity in entities

            if "name" in entity

        )

        prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(

            relationship_types=RELATIONSHIP_PROMPT,

            entities=entity_names,

            chunk=chunk,

        )

        try:
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                    )
                    time.sleep(self.request_delay_seconds)
                    break
                except Exception as error:
                    if "429" not in str(error) or attempt == self.max_retries:
                        raise
                    wait_seconds = self.request_delay_seconds * (2 ** attempt)
                    logger.warning(
                        "Gemini rate limit reached; retrying in %s seconds.",
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)

            if response is None:

                logger.warning("Gemini returned no response.")

                return ""

            answer = response.text

            if not answer:

                logger.warning(
                    "Gemini returned an empty response."
                )

                return ""

            return answer.strip()

        except Exception as e:
            raise RelationshipExtractionError(
                "Gemini relationship extraction failed "
                f"({type(e).__name__}: {e})."
            ) from e

    # --------------------------------------------------
    # Step 2 : Parse JSON
    # --------------------------------------------------

    def parse(
        self,
        response: str,
    ) -> List[Dict]:

        if not response:

            return []

        try:

            response = response.strip()

            response = response.replace(
                "```json",
                "",
            )

            response = response.replace(
                "```",
                "",
            )

            response = response.strip()

            data = json.loads(response)

            relationships = data.get(
                "relationships",
                [],
            )

            if not isinstance(
                relationships,
                list,
            ):

                logger.warning(
                    "'relationships' is not a list."
                )

                return []

            return relationships

        except json.JSONDecodeError as e:

            logger.exception(
                f"Failed to parse relationship JSON: {e}"
            )

            return []

        except Exception as e:

            logger.exception(
                f"Unexpected parsing error: {e}"
            )

            return []

    # --------------------------------------------------
    # Step 3 : Validate Relationships
    # --------------------------------------------------

    def validate(
        self,
        relationships: List[Dict],
    ) -> List[Dict]:

        validated = []

        if not isinstance(
            relationships,
            list,
        ):

            return validated

        for relationship in relationships:

            if not isinstance(
                relationship,
                dict,
            ):

                continue

            source = relationship.get("source")

            target = relationship.get("target")

            relation = relationship.get("relation")

            if not source or not target or not relation:

                continue

            try:

                source = normalize_entity(source)

                target = normalize_entity(target)

            except Exception as e:

                logger.exception(
                    f"Failed to normalize relationship: {e}"
                )

                continue

            if not is_valid_relation(relation):

                logger.warning(

                    "Skipping invalid relationship: %s",

                    relation,

                )

                continue

            validated.append(

                {

                    "source": source,

                    "relation": relation,

                    "target": target,

                }

            )

        return validated

    # --------------------------------------------------
    # Complete Pipeline
    # --------------------------------------------------

    def run(
        self,
        chunk: str,
        entities: List[Dict],
    ) -> List[Dict]:

        raw_response = self.extract(
            chunk,
            entities,
        )

        if not raw_response:

            return []

        parsed_relationships = self.parse(
            raw_response
        )

        if not parsed_relationships:

            return []

        validated_relationships = self.validate(
            parsed_relationships
        )

        return validated_relationships
