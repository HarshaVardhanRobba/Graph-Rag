import json

from phi.model.google import gemini

from ontology import (
    RELATIONSHIP_PROMPT,
    is_valid_relation,
    normalize_entity
)

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

# relationship extractor class
class RelationshipExtractor:
    
    # gemini model initialization
    def __init__(self):

        self.model = gemini(
            id="gemini-2.5-flash"
        )

    # extract relationships

    def extract(self, chunk: str, entities):

        entity_names = "\n".join(
            [entity["name"] for entity in entities]
        )

        prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(

            relationship_types=RELATIONSHIP_PROMPT,

            entities=entity_names,

            chunk=chunk,

        )

        response = self.model.response(prompt)

        return response.content

    # parse JSON

    def parse(self, response):

        try:

            data = json.loads(response)

            return data.get("relationships", [])

        except Exception as e:

            print(f"JSON Parsing Error: {e}")

            return []

    # validate relationships

    def validate(self, relationships):

        valid_relationships = []

        for relationship in relationships:

            source = normalize_entity(
                relationship["source"]
            )

            target = normalize_entity(
                relationship["target"]
            )

            relation = relationship["relation"]

            if not is_valid_relation(relation):

                print(
                    f"Skipping invalid relationship: {relation}"
                )

                continue

            valid_relationships.append(

                {
                    "source": source,
                    "relation": relation,
                    "target": target,
                }

            )

        return valid_relationships

    # complete pipeline

    def run(self, chunk, entities):

        raw_relationship_response = self.extract(chunk, entities)

        parsed_relationships = self.parse(raw_relationship_response)

        validated_relationships = self.validate(parsed_relationships)

        return validated_relationships

