"""
Retrieval Router

Responsibilities:
1. Graph Only Retrieval
2. Vector Only Retrieval
3. Hybrid Retrieval
"""

from typing import Dict


class RetrievalRouter:
    """
    Routes the query to the appropriate retrieval strategy.
    """

    def __init__(
        self,
        graph_retriever,
        vector_retriever,
        hybrid_retriever,
    ):
        self.graph_retriever = graph_retriever
        self.vector_retriever = vector_retriever
        self.hybrid_retriever = hybrid_retriever

    # --------------------------------------------------
    # Graph Only
    # --------------------------------------------------

    def graph_only(
        self,
        structured_query: Dict,
    ) -> Dict:
        """
        Graph-only retrieval.
        """

        return self.graph_retriever.run(
            structured_query
        )

    # --------------------------------------------------
    # Vector Only
    # --------------------------------------------------

    def vector_only(
        self,
        structured_query: Dict,
    ) -> Dict:
        """
        Vector-only retrieval.
        """

        return self.vector_retriever.run(
            structured_query
        )

    # --------------------------------------------------
    # Hybrid
    # --------------------------------------------------

    def hybrid(
        self,
        structured_query: Dict,
    ) -> Dict:
        """
        Hybrid retrieval.
        """

        return self.hybrid_retriever.run(
            structured_query
        )

    # --------------------------------------------------
    # Router
    # --------------------------------------------------

    def run(
        self,
        structured_query: Dict,
        mode: str = "hybrid",
    ) -> Dict:

        mode = mode.lower()

        if mode == "graph":
            return self.graph_only(structured_query)

        elif mode == "vector":
            return self.vector_only(structured_query)

        return self.hybrid(structured_query)