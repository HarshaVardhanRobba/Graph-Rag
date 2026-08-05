class GraphChunker:

    """
    Creates graph-aware chunks by enriching
    document chunks with graph information.
    """

    def create_graph_chunk(
        self,
        chunk,
        entities,
        relationships,
    ):

        graph_chunk = chunk

        if entities:

            graph_chunk += "\n\nEntities:\n"

            for entity in entities:

                graph_chunk += (
                    f"- {entity['name']} ({entity['type']})\n"
                )

        if relationships:

            graph_chunk += "\nRelationships:\n"

            for relation in relationships:

                graph_chunk += (
                    f"- {relation['source']} "
                    f"{relation['relation']} "
                    f"{relation['target']}\n"
                )

        return graph_chunk