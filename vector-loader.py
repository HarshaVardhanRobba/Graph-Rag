from phi.embedder.ollama import OllamaEmbedder
from phi.vectordb.pgvector import PgVector


class VectorLoader:

    """
    Handles embedding generation and storage
    inside the vector database.
    """

    def __init__(
        self,
        db_url,
        table_name="pdf_documents",
    ):

        self.embedder = OllamaEmbedder(
            id="nomic-embed-text"
        )

        self.vector_db = PgVector(
            table_name=table_name,
            db_url=db_url,
        )

    def build_metadata(
        self,
        chunk_id,
        page,
        entities,
        relationships,
    ):

        return {

            "chunk_id": chunk_id,

            "page": page,

            "entities": [
                entity["name"]
                for entity in entities
            ],

            "entity_types": [
                entity["type"]
                for entity in entities
            ],

            "relationships": relationships,

        }

    def create_embedding(
        self,
        graph_chunk,
    ):

        return self.embedder.get_embedding(
            graph_chunk
        )

    def store(
        self,
        graph_chunk,
        chunk_id,
        page,
        entities,
        relationships,
    ):

        metadata = self.build_metadata(
            chunk_id,
            page,
            entities,
            relationships,
        )

        embedding = self.create_embedding(
            graph_chunk
        )

        self.vector_db.insert(
            text=graph_chunk,
            embedding=embedding,
            metadata=metadata,
        )