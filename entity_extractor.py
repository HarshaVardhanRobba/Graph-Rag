import json
import os
# import gemini
from typing import List, Dict, Any
from phi.model.google import Gemini

# import ontology and helpers
from ontology import (
    ENTITY_TYPE_PROMPT,
    is_valid_entity_type,
    normalize_entity
)

# initialize gemini
model = Gemini(
    id="gemini-2.5-pro",
    api_key=os.getenv("gemini_api_key"),
    temperature=0.5,
    top_p=1.0
)

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

{
    "entities":[
        {
            "name":"K-Means",
            "type":"Algorithm"
        }
    ]
}

TEXT:

{chunk}
"""

# extractor class
class EntityExtractor:

    # gemini model initialization
    def __init__(self):

        self.model = gemini(
            id="gemini-2.5-flash"
        )

    # -------------------------------
    # Step 5: Extract Entities
    # -------------------------------
    def extract(self, chunk: str):

        prompt = ENTITY_EXTRACTION_PROMPT.format(
            entity_types=ENTITY_TYPE_PROMPT,
            chunk=chunk,
        )

        response = self.model.response(prompt)

        return response.content

    # -------------------------------
    # Step 6: Parse JSON
    # -------------------------------
    def parse(self, response: str):

        try:

            data = json.loads(response)

            return data.get("entities", [])

        except Exception as e:

            print(f"JSON Parsing Error: {e}")

            return []

    # -------------------------------
    # Step 7: Validate Entities
    # -------------------------------
    def validate(self, entities):

        valid_entities = []

        for entity in entities:

            name = normalize_entity(entity["name"])

            entity_type = entity["type"]

            if not is_valid_entity_type(entity_type):

                print(f"Skipping invalid entity type: {entity_type}")

                continue

            valid_entities.append(
                {
                    "name": name,
                    "type": entity_type,
                }
            )

        return valid_entities

    # -------------------------------
    # Step 8: Complete Pipeline
    # -------------------------------
    def run(self, chunk: str):

        raw_response = self.extract(chunk)

        parsed_entities = self.parse(raw_response)

        validated_entities = self.validate(parsed_entities)

        return validated_entities