"""
Hybrid Retrieval

Responsibilities:
1. Graph Retrieval
2. Vector Retrieval
3. Merge Graph Context
4. Merge Vector Chunks
5. Remove Duplicates
6. Rank Context
7. Build Final Context
"""

from typing import Dict, List


class HybridRetriever:

    def __init__(
        self,
        graph_retriever,
        vector_retriever,
    ):
        self.graph_retriever = graph_retriever
        self.vector_retriever = vector_retriever

    # --------------------------------------------------
    # Graph Retrieval
    # --------------------------------------------------

    def graph_retrieval(
        self,
        structured_query: Dict,
    ) -> Dict:

        return self.graph_retriever.run(
            structured_query
        )

    # --------------------------------------------------
    # Vector Retrieval
    # --------------------------------------------------

    def vector_retrieval(
        self,
        structured_query: Dict,
    ) -> Dict:

        return self.vector_retriever.run(
            structured_query
        )

    # --------------------------------------------------
    # Merge Graph Context
    # --------------------------------------------------

    def merge_graph_context(
        self,
        graph_results: Dict,
    ) -> List[Dict]:

        return graph_results.get(
            "matched_nodes",
            []
        )

    # --------------------------------------------------
    # Merge Vector Chunks
    # --------------------------------------------------

    def merge_vector_chunks(
        self,
        vector_results: Dict,
    ) -> List[Dict]:

        return vector_results.get(
            "retrieved_chunks",
            []
        )

    # --------------------------------------------------
    # Remove Duplicates
    # --------------------------------------------------

    def remove_duplicates(
        self,
        graph_context: List[Dict],
        vector_chunks: List[Dict],
    ) -> List[Dict]:

        merged = []

        merged.extend(graph_context)
        merged.extend(vector_chunks)

        #
        # TODO
        #

        return merged

    # --------------------------------------------------
    # Rank Context
    # --------------------------------------------------

    def rank_context(
        self,
        merged_context: List[Dict],
    ) -> List[Dict]:

        #
        # TODO
        #

        return merged_context

    # --------------------------------------------------
    # Build Final Context
    # --------------------------------------------------

    def build_context(
        self,
        ranked_context: List[Dict],
    ) -> str:

        context = []

        for item in ranked_context:

            if "text" in item:

                context.append(item["text"])

            elif "description" in item:

                context.append(item["description"])

        return "\n\n".join(context)

    # --------------------------------------------------
    # Pipeline
    # --------------------------------------------------

    def run(
        self,
        structured_query: Dict,
    ) -> Dict:

        graph_results = self.graph_retrieval(
            structured_query
        )

        vector_results = self.vector_retrieval(
            structured_query
        )

        graph_context = self.merge_graph_context(
            graph_results
        )

        vector_chunks = self.merge_vector_chunks(
            vector_results
        )

        merged_context = self.remove_duplicates(
            graph_context,
            vector_chunks,
        )

        ranked_context = self.rank_context(
            merged_context,
        )

        final_context = self.build_context(
            ranked_context,
        )

        return {

            "graph_results": graph_results,

            "vector_results": vector_results,

            "ranked_context": ranked_context,

            "final_context": final_context,

        }