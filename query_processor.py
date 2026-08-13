from typing import Dict


class QueryProcessor:

    def __init__(self, entity_extractor=None):
        self.entity_extractor = entity_extractor

    def run(self, query: str) -> Dict:

        entities = []

        if self.entity_extractor:
            entities = self.entity_extractor.run(query)

        return {
            "query": query,
            "entities": entities,
            "intent": "qa",
        }
