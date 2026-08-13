from neo4j import GraphDatabase


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
        """
        Initialize Neo4j connection.
        """

        try:
            self.driver = GraphDatabase.driver(
                uri,
                auth=(username, password)
            )

            # Verify database connectivity
            self.driver.verify_connectivity()

            print("Connected to Neo4j successfully.")

        except Exception as e:

            print(f"Failed to connect to Neo4j: {e}")

            self.driver = None

    def close(self):
        """
        Close the Neo4j database connection.
        """

        try:

            if self.driver is not None:

                self.driver.close()

                print("Neo4j connection closed.")

        except Exception as e:

            print(f"Error closing Neo4j connection: {e}")

    def has_entities(self) -> bool:
        """Return whether the graph already contains extracted entity nodes."""

        if self.driver is None:
            return False

        with self.driver.session() as session:
            result = session.run("MATCH (:Entity) RETURN count(*) AS count")
            return result.single()["count"] > 0

    # --------------------------------------------------
    # Create Entity
    # --------------------------------------------------

    def create_entity(
        self,
        entity,
    ):
        """
        Create an entity node if it does not already exist.
        """

        if self.driver is None:

            print("Neo4j driver is not initialized.")

            return

        if not isinstance(entity, dict):

            print("Invalid entity format.")

            return

        name = entity.get("name")

        entity_type = entity.get("type")

        if not name or not entity_type:

            print(f"Skipping invalid entity: {entity}")

            return

        query = """

        MERGE (e:Entity {name:$name})

        SET e.type=$type

        """

        try:

            with self.driver.session() as session:

                session.run(

                    query,

                    name=name,

                    type=entity_type,

                )

        except Exception as e:

            print(f"Failed to create entity '{name}': {e}")

    # --------------------------------------------------
    # Create Relationship
    # --------------------------------------------------

    def create_relationship(
        self,
        relationship,
    ):
        """
        Create a relationship between two existing entities.
        """

        if self.driver is None:

            print("Neo4j driver is not initialized.")

            return

        if not isinstance(relationship, dict):

            print("Invalid relationship format.")

            return

        source = relationship.get("source")

        target = relationship.get("target")

        relation = relationship.get("relation")

        if not source or not target or not relation:

            print(f"Skipping invalid relationship: {relationship}")

            return

        query = """

        MATCH (a:Entity {name:$source})

        MATCH (b:Entity {name:$target})

        MERGE (a)-[r:RELATION {
            type:$relation
        }]->(b)

        """

        try:

            with self.driver.session() as session:

                session.run(

                    query,

                    source=source,

                    target=target,

                    relation=relation,

                )

        except Exception as e:

            print(
                f"Failed to create relationship "
                f"{source} -[{relation}]-> {target}: {e}"
            )

    # --------------------------------------------------
    # Load Entities
    # --------------------------------------------------

    def load_entities(
        self,
        entities,
    ):
        """
        Load all entities into Neo4j.
        """

        if not isinstance(entities, list):

            print("Entities must be a list.")

            return

        for entity in entities:

            self.create_entity(entity)

    # --------------------------------------------------
    # Load Relationships
    # --------------------------------------------------

    def load_relationships(
        self,
        relationships,
    ):
        """
        Load all relationships into Neo4j.
        """

        if not isinstance(relationships, list):

            print("Relationships must be a list.")

            return

        for relationship in relationships:

            self.create_relationship(
                relationship
            )

    # --------------------------------------------------
    # Complete Pipeline
    # --------------------------------------------------

    def load(
        self,
        entities,
        relationships,
    ):
        """
        Load the complete Knowledge Graph.
        """

        if self.driver is None:

            print("Neo4j is unavailable.")

            return

        try:

            self.load_entities(
                entities
            )

            self.load_relationships(
                relationships
            )

            print("Knowledge Graph loaded successfully.")

        except Exception as e:

            print(f"Knowledge Graph loading failed: {e}")
