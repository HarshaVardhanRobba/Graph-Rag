import json
import logging
import os
import time
from typing import List, Dict

from google import genai

from ontology import (
    ENTITY_TYPE_PROMPT,
    is_valid_entity_type,
    normalize_entity,
)

logger = logging.getLogger(__name__)


class EntityExtractionError(RuntimeError):
    """Raised when the configured entity-extraction service is unavailable."""

ENTITY_EXTRACTION_PROMPT = """
You are an expert information extraction system.

Extract every important entity from the text.

Allowed Entity Types:

{entity_types}

Instructions:

1. Return JSON only.
2. Do not explain.
3. Do not create new entity types.
4. Every entity must have:
   - name
   - type

Output format:

{{
    "entities": [
        {{
            "name": "K-Means",
            "type": "Algorithm"
        }}
    ]
}}

TEXT:

{chunk}
"""


class EntityExtractor:
    """
    Extracts entities from a single text chunk.
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

            logger.exception(f"Failed to initialize Gemini client: {e}")

            self.client = None
            self.model = None

    # --------------------------------------------------
    # Step 1 : Extract Entities
    # --------------------------------------------------

    def extract(
        self,
        chunk: str,
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

        prompt = ENTITY_EXTRACTION_PROMPT.format(
            entity_types=ENTITY_TYPE_PROMPT,
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

                logger.warning("Gemini returned an empty response.")

                return ""

            return answer.strip()

        except Exception as e:
            raise EntityExtractionError(
                "Gemini entity extraction failed "
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

            # Remove markdown fences if Gemini returns them
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

            data = json.loads(response)

            entities = data.get("entities", [])

            if not isinstance(entities, list):

                logger.warning("'entities' is not a list.")

                return []

            return entities

        except json.JSONDecodeError as e:

            logger.exception(f"Failed to parse entity JSON: {e}")

            return []

        except Exception as e:

            logger.exception(f"Unexpected parsing error: {e}")

            return []

    # --------------------------------------------------
    # Step 3 : Validate Entities
    # --------------------------------------------------

    def validate(
        self,
        entities: List[Dict],
    ) -> List[Dict]:

        validated = []

        if not isinstance(entities, list):

            return validated

        for entity in entities:

            if not isinstance(entity, dict):

                continue

            name = entity.get("name")
            entity_type = entity.get("type")

            if not name or not entity_type:

                continue

            try:

                name = normalize_entity(name)

            except Exception as e:

                logger.exception(f"Failed to normalize entity: {e}")

                continue

            if not is_valid_entity_type(entity_type):

                logger.warning(
                    "Skipping invalid entity type: %s",
                    entity_type,
                )

                continue

            validated.append(
                {
                    "name": name,
                    "type": entity_type,
                }
            )

        return validated

    # --------------------------------------------------
    # Complete Pipeline
    # --------------------------------------------------

    def run(
        self,
        chunk: str,
    ) -> List[Dict]:

        raw_response = self.extract(chunk)

        if not raw_response:

            return []

        parsed_entities = self.parse(raw_response)

        if not parsed_entities:

            return []

        validated_entities = self.validate(parsed_entities)

        return validated_entities
