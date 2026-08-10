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
import argparse

from dotenv import load_dotenv

print("Loaded .env:", load_dotenv())

# -----------------------------
# PhiData
# -----------------------------

from phi.agent import Agent
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.vectordb.pgvector import PgVector
from phi.storage.agent.postgres import PgAgentStorage
from google import genai
from phi.embedder.ollama import OllamaEmbedder

# -----------------------------
# Your Modules
# -----------------------------

from entity_extractor import EntityExtractor, EntityExtractionError
from relationship_extractor import RelationshipExtractor, RelationshipExtractionError
from neo4j_loader import Neo4jLoader
from query_processor import QueryProcessor

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
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

required_settings = {
    "gemini_api_key": GOOGLE_API_KEY,
    "db_url": DATABASE_URL,
    "NEO4J_URI": os.getenv("NEO4J_URI"),
    "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME"),
    "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
}
missing_settings = [name for name, value in required_settings.items() if not value]
if missing_settings:
    raise RuntimeError(
        "Missing required environment variables: " + ", ".join(missing_settings)
    )

# ======================================================
# Knowledge Base
# ======================================================

import traceback
from sqlalchemy import create_engine, text

print("\n" + "=" * 60)
print("KNOWLEDGE BASE INITIALIZATION")
print("=" * 60)

pdf_path = r"C:\Users\robba\OneDrive\Desktop\Graph RAG\Attention is all you need.pdf"

# ------------------------------------------------------
# Step 1 - Check PDF
# ------------------------------------------------------

print("\n[STEP 1] Checking PDF...")

if os.path.exists(pdf_path):
    print(f"✅ PDF Found: {pdf_path}")
else:
    print(f"❌ PDF Not Found: {pdf_path}")
    exit()

# ------------------------------------------------------
# Step 2 - Create Embedder
# ------------------------------------------------------

print("\n[STEP 2] Creating Embedder...")

embedder = OllamaEmbedder(model="nomic-embed-text")

print("✅ Embedder Created")

# ------------------------------------------------------
# Step 3 - Verify Embedding Dimension
# ------------------------------------------------------

print("\n[STEP 3] Testing Embedding...")

embedding = embedder.get_embedding("Hello World")

if not isinstance(embedding, list) or not embedding:
    raise RuntimeError(
        "Ollama did not return an embedding. Start Ollama and ensure "
        "the 'nomic-embed-text' model is installed."
    )

print(f"✅ Embedding Generated")
print(f"Embedding Dimension = {len(embedding)}")

# ------------------------------------------------------
# Step 4 - Test PostgreSQL Connection
# ------------------------------------------------------

print("\n[STEP 4] Testing PostgreSQL Connection...")

try:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    print("✅ PostgreSQL Connected")

except Exception as e:
    print("❌ PostgreSQL Connection Failed")
    print(e)
    exit()

# ------------------------------------------------------
# Step 5 - Create Knowledge Base
# ------------------------------------------------------

print("\n[STEP 5] Creating Knowledge Base...")

knowledge_base = PDFKnowledgeBase(
    path=pdf_path,
    reader=PDFReader(chunk=True),
    vector_db=PgVector(
        table_name="pdf_documents",
        db_url=DATABASE_URL,
        embedder=embedder,
    ),
)

print("✅ Knowledge Base Created")

# ------------------------------------------------------
# Step 6 - Load Knowledge Base
# ------------------------------------------------------

print("\n[STEP 6] Loading Knowledge Base...")

try:
    knowledge_base.load(recreate=False)

    print("✅ Knowledge Base Loaded Successfully")

except Exception as e:

    print("\n❌ KNOWLEDGE BASE LOAD FAILED")
    print(f"Exception Type : {type(e).__name__}")
    print(f"Exception      : {e}")

    print("\nFull Traceback:\n")
    traceback.print_exc()

    exit()

print("=" * 60)
print("KNOWLEDGE BASE READY")
print("=" * 60)

# ======================================================
# Agent
# ======================================================

storage = PgAgentStorage(
    table_name="pdf_sessions",
    db_url=DATABASE_URL,
)

from phi.model.google import Gemini

agent = Agent(
    model=Gemini(
        id=GEMINI_MODEL,
        api_key=os.getenv("gemini_api_key"),
    ),
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

query_processor = QueryProcessor(entity_extractor=entity_extractor)

relationship_extractor = RelationshipExtractor()

neo4j = Neo4jLoader(
    uri=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

graph_retriever = GraphRetriever(neo4j)

vector_retriever = VectorRetriever(
    embedder=embedder,
    vector_db=knowledge_base.vector_db,
)

hybrid_retriever = HybridRetriever(
    graph_retriever=graph_retriever,
    vector_retriever=vector_retriever,
)

context_builder = ContextBuilder()

answer_generator = AnswerGenerator(
    api_key=os.getenv("gemini_api_key"),
    model_name=GEMINI_MODEL,
)

# ======================================================
# Build Knowledge Graph
# ======================================================

parser = argparse.ArgumentParser()
parser.add_argument(
    "--rebuild-graph",
    action="store_true",
    help="Re-extract the PDF and merge results into Neo4j.",
)
args = parser.parse_args()

if neo4j.has_entities() and not args.rebuild_graph:
    print(
        "Knowledge Graph already contains entities; skipping extraction. "
        "Use --rebuild-graph to run extraction again."
    )
else:
    print("Building Knowledge Graph...")

    all_entities = []
    all_relationships = []

    for document_list in knowledge_base.document_lists:

        for document in document_list:

            chunk = document.content

            try:
                entities = entity_extractor.run(chunk)
                relationships = relationship_extractor.run(chunk, entities)
            except (EntityExtractionError, RelationshipExtractionError) as error:
                neo4j.close()
                raise SystemExit(f"Graph build stopped: {error}") from None

            all_entities.extend(entities)
            all_relationships.extend(relationships)

    neo4j.load(
        all_entities,
        all_relationships,
    )

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
        # Query Processing
        # -----------------------------

        structured_query = query_processor.run(query)

        # -----------------------------
        # Retrieval
        # -----------------------------

        retrieval = hybrid_retriever.run(structured_query)

        graph_results = retrieval["graph_results"]
        vector_results = retrieval["vector_results"]

        log_retrieval(
            len(graph_results.get("matched_nodes", [])),
            len(vector_results.get("retrieved_chunks", [])),
        )

        # -----------------------------
        # Context Construction
        # -----------------------------

        prompt = context_builder.build(
            query=query,
            graph_results=graph_results.get("subgraph", {}).get("edges", []),
            vector_results=vector_results.get("retrieved_chunks", []),
        )

        # -----------------------------
        # Answer Generation
        # -----------------------------

        result = answer_generator.generate(
            prompt=prompt,
            sources=vector_results.get("retrieved_chunks", []),
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

        print("\nSources\n")
        print(result["sources"])

        print("\nEvaluation\n")
        print(metrics)

    except Exception as e:

        log_error(e)
        print(f"\nError: {e}")
