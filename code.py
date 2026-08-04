"""
Main Entry Point

Pipeline:
1. Load Environment Variables
2. Initialize Knowledge Base
3. Initialize Agent
4. Build Knowledge Graph
5. Start Query Loop
"""

import os
import time

from dotenv import load_dotenv

# -----------------------------
# PhiData
# -----------------------------

from phi.agent import Agent
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.pgvector import PgVector
from phi.storage.agent.postgres import PgAgentStorage
from phi.model.google import Gemini
from phi.embedder.ollama import OllamaEmbedder

# -----------------------------
# Your Modules
# -----------------------------

from entity_extractor import EntityExtractor
from relationship_extractor import RelationshipExtractor
from neo4j_loader import Neo4jLoader

from graph_retrieval import GraphRetriever
from vector_retrival import VectorRetriever
from hybrid_retrieval import HybridRetriever

from context_builder import ContextBuilder
from answer_generator import AnswerGenerator

from evaluator import evaluate

from logger import (
    log_query,
    log_retrieval,
    log_generation,
    log_error,
)

# ======================================================
# Load Environment Variables
# ======================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("gemini_api_key")
DATABASE_URL = os.getenv("db_url")

# ======================================================
# Knowledge Base
# ======================================================

knowledge_base = PDFKnowledgeBase(
    path="C:\\Users\\robba\\OneDrive\\Desktop\\Graph RAG\\CS5380-4380-Ch7-Basic-Cluster-Analysis (1).pdf",
    reader=PDFReader(chunk=True),
    vector_db=PgVector(
        table_name="pdf_documents",
        db_url=DATABASE_URL,
        embedder=OllamaEmbedder(model="nomic-embed-text"),
    ),
)

knowledge_base.load(recreate=True)

# ======================================================
# Agent
# ======================================================

storage = PgAgentStorage(
    table_name="pdf_sessions",
    db_url=DATABASE_URL,
)

agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    knowledge=knowledge_base,
    storage=storage,
    search_knowledge=True,
    user_id="pdf_user",
    show_tool_calls=True,
    markdown=True,
    read_chat_history=True,
    search_knowledge_on_tool_calls=True,
    session_id="pdf_session",
)

# ======================================================
# Custom Modules
# ======================================================

entity_extractor = EntityExtractor()

relationship_extractor = RelationshipExtractor()

neo4j = Neo4jLoader()

graph_retriever = GraphRetriever(neo4j)

vector_retriever = VectorRetriever(knowledge_base)

hybrid_retriever = HybridRetriever()

context_builder = ContextBuilder()

answer_generator = AnswerGenerator(
    api_key=GOOGLE_API_KEY
)

# ======================================================
# Build Knowledge Graph
# ======================================================

print("Building Knowledge Graph...")

chunks = knowledge_base.document_lists

entities = entity_extractor.extract(chunks)

relationships = relationship_extractor.extract(chunks)

neo4j.store_entities(entities)

neo4j.store_relationships(relationships)

print("Knowledge Graph Ready.")

# ======================================================
# Query Loop
# ======================================================

while True:

    query = input("\nQuestion: ")

    if query.lower() in ["exit", "quit"]:
        break

    start_time = time.time()

    try:

        # -----------------------------
        # Logging
        # -----------------------------

        log_query(query)

        # -----------------------------
        # Retrieval
        # -----------------------------

        graph_results = graph_retriever.retrieve(query)

        vector_results = vector_retriever.retrieve(query)

        log_retrieval(
            len(graph_results),
            len(vector_results),
        )

        retrieval = hybrid_retriever.retrieve(
            graph_results,
            vector_results,
        )

        # -----------------------------
        # Context Construction
        # -----------------------------

        prompt = context_builder.build(
            query=query,
            graph_results=retrieval["graph"],
            vector_results=retrieval["vector"],
        )

        # -----------------------------
        # Answer Generation
        # -----------------------------

        result = answer_generator.generate(
            prompt=prompt,
            sources=retrieval["vector"],
        )

        log_generation()

        # -----------------------------
        # Evaluation
        # -----------------------------

        metrics = evaluate(
            query=query,
            graph_results=graph_results,
            vector_results=vector_results,
            answer=result["answer"],
            start_time=start_time,
        )

        print("\nAnswer\n")
        print(result["answer"])

        print("\nSources")
        print(result["sources"])

        print("\nEvaluation")
        print(metrics)

    except Exception as e:

        log_error(e)
        print(f"\nError: {e}")