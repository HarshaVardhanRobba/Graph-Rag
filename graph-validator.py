from neo4j_loader import GraphDatabase


class Neo4jLoader:
    """
    Handles storing entities and relationships
    in the Neo4j Knowledge Graph.
    """

    def __init__(
        self,
        uri,
        username,
        password,
    ):
        # Create a connection to the Neo4j database
        self.driver = GraphDatabase.driver(
            uri,
            auth=(username, password)
        )

    def close(self):
        """Close the Neo4j database connection."""
        self.driver.close()

    def create_entity(
        self,
        entity,
    ):
        """
        Create an entity node if it does not already exist.
        Updates the entity type if the node already exists.
        """

        query = """

        MERGE (e:Entity {name:$name})

        SET e.type=$type

        """

        with self.driver.session() as session:

            session.run(

                query,

                name=entity["name"],

                type=entity["type"]

            )

    def create_relationship(
        self,
        relationship,
    ):
        """
        Create a relationship between two existing entities.
        The relationship is merged to avoid duplicates.
        """

        query = """

        MATCH (a:Entity {name:$source})

        MATCH (b:Entity {name:$target})

        MERGE (a)-[r:RELATION {
            type:$relation
        }]->(b)

        """

        with self.driver.session() as session:

            session.run(

                query,

                source=relationship["source"],

                target=relationship["target"],

                relation=relationship["relation"]

            )

    def load_entities(
        self,
        entities,
    ):
        """
        Iterate through the extracted entities
        and insert them into Neo4j.
        """

        for entity in entities:

            self.create_entity(entity)

    def load_relationships(
        self,
        relationships,
    ):
        """
        Iterate through the extracted relationships
        and insert them into Neo4j.
        """

        for relationship in relationships:

            self.create_relationship(
                relationship
            )

    def load(
        self,
        entities,
        relationships,
    ):
        """
        Load the complete Knowledge Graph by first
        creating all entity nodes and then connecting
        them using relationships.
        """

        self.load_entities(
            entities
        )

        self.load_relationships(
            relationships
        )

    def verify_node_creation(self):
        """
        Verify that all entity nodes have been
        created successfully.
        """

        query = """

        MATCH (e:Entity)

        RETURN
            COUNT(e) AS total_nodes,
            COUNT(e.name) AS named_nodes,
            COUNT(e.type) AS typed_nodes

        """

        with self.driver.session() as session:

            result = session.run(query).single()

            print("\nNode Verification")
            print("-----------------")
            print(f"Total Nodes : {result['total_nodes']}")
            print(f"Named Nodes : {result['named_nodes']}")
            print(f"Typed Nodes : {result['typed_nodes']}")

            duplicate_query = """

            MATCH (e:Entity)

            WITH e.name AS name,
                 COUNT(*) AS occurrences

            WHERE occurrences > 1

            RETURN name, occurrences

            """

            duplicates = list(session.run(duplicate_query))

            if duplicates:

                print("\nDuplicate Nodes Found:")

                for node in duplicates:

                    print(
                        f"{node['name']} -> {node['occurrences']}"
                    )

            else:

                print("\nNo Duplicate Nodes Found.")

    def verify_relationship_creation(self):
        """
        Verify that all relationships
        have been created successfully.
        """

        query = """

        MATCH (a)-[r:RELATION]->(b)

        RETURN COUNT(r) AS total_relationships

        """

        with self.driver.session() as session:

            result = session.run(query).single()

            print("\nRelationship Verification")
            print("-------------------------")
            print(
                f"Total Relationships : {result['total_relationships']}"
            )

            invalid_query = """

            MATCH (a)-[r:RELATION]->(b)

            WHERE
                r.type IS NULL
                OR a.name IS NULL
                OR b.name IS NULL

            RETURN a,r,b

            """

            invalid = list(session.run(invalid_query))

            if invalid:

                print("\nInvalid Relationships Found.")

            else:

                print("\nAll Relationships Are Valid.")

    def validate_graph_integrity(self):
        """
        Perform integrity checks on the graph.
        """

        with self.driver.session() as session:

            orphan_query = """

            MATCH (e:Entity)

            WHERE NOT (e)--()

            RETURN e.name AS orphan

            """

            orphans = list(session.run(orphan_query))

            print("\nGraph Integrity")
            print("----------------")

            if orphans:

                print("Orphan Nodes:")

                for node in orphans:

                    print(node["orphan"])

            else:

                print("No Orphan Nodes Found.")

    def validate(
        self,
    ):
        """
        Execute all graph validation steps.
        """

        self.verify_node_creation()

        self.verify_relationship_creation()

        self.validate_graph_integrity()