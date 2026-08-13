"""
Context Builder

Responsibilities:
1. Build Graph Context
2. Build Vector Context
3. Add Citations
4. Assemble Final Prompt
5. Manage Token Limit
"""

from typing import List, Dict


class ContextBuilder:
    """
    Builds the final prompt for the LLM from the retrieved graph
    context and vector context.
    """

    def __init__(self, max_chars: int = 30000):
        # Simple character limit as an approximation for token budget.
        self.max_chars = max_chars

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def build(
        self,
        query: str,
        graph_results: List[Dict],
        vector_results: List[Dict],
    ) -> str:
        """
        Returns the final prompt.
        """

        graph_context = self.build_graph_context(graph_results)
        vector_context = self.build_vector_context(vector_results)

        prompt = self.assemble_prompt(
            query=query,
            graph_context=graph_context,
            vector_context=vector_context,
        )

        prompt = self.manage_token_limit(prompt)

        return prompt

    # ---------------------------------------------------------
    # Graph Context
    # ---------------------------------------------------------

    def build_graph_context(self, graph_results: List[Dict]) -> str:
        """
        Converts graph retrieval output into readable text.
        """

        if not graph_results:
            return "No graph context available."

        lines = ["## Knowledge Graph\n"]

        for item in graph_results:
            entity = item.get("entity", "Unknown")
            relationship = item.get("relationship", "")
            target = item.get("target", "")

            if relationship and target:
                lines.append(
                    f"- {entity} --[{relationship}]--> {target}"
                )
            else:
                lines.append(f"- {entity}")

        return "\n".join(lines)

    # ---------------------------------------------------------
    # Vector Context
    # ---------------------------------------------------------

    def build_vector_context(self, vector_results: List[Dict]) -> str:
        """
        Formats retrieved document chunks with citations.
        """

        if not vector_results:
            return "No document context available."

        lines = ["## Relevant Documents\n"]

        for i, chunk in enumerate(vector_results, start=1):

            text = chunk.get("text", "")
            source = chunk.get("source", "Unknown Document")
            page = chunk.get("page", "N/A")

            lines.append(
                f"[{i}] {text}\n"
                f"Source: {source}, Page: {page}\n"
            )

        return "\n".join(lines)

    # ---------------------------------------------------------
    # Prompt Assembly
    # ---------------------------------------------------------

    def assemble_prompt(
        self,
        query: str,
        graph_context: str,
        vector_context: str,
    ) -> str:
        """
        Combines all retrieved context into a single prompt.
        """

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question ONLY using the provided context.
If the answer is not present, say you do not know.

==================================================

Question:
{query}

==================================================

{graph_context}

==================================================

{vector_context}

==================================================

Provide a clear and concise answer.
Include citations like [1], [2] whenever applicable.
"""

        return prompt.strip()

    # ---------------------------------------------------------
    # Token Management
    # ---------------------------------------------------------

    def manage_token_limit(self, prompt: str) -> str:
        """
        Simple prompt size management.

        Uses character count as a lightweight approximation.
        """

        if len(prompt) <= self.max_chars:
            return prompt

        return prompt[: self.max_chars]