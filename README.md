# Graph RAG Knowledge Pipeline

## Overview

This project is a local prototype for Graph Retrieval-Augmented Generation (Graph RAG). It ingests PDF or text content, extracts structured entities and relationships, builds an in-memory knowledge graph, and answers user questions by combining graph reasoning with document retrieval.

The current implementation is built to run locally for the Transformer paper `Attention is all you need.pdf`, but it is designed so the architecture can be extended to enterprise-grade graph + vector search systems.

## What this project solves

Traditional retrieval from documents often loses the structure and meaning of relationships between concepts. This project solves that by:

- extracting entities and relationship facts from text,
- storing them in a graph-like structure,
- using graph context to support more precise answers,
- and combining that with document retrieval for source evidence.

This hybrid approach is useful when users need answers that are grounded in both structured concept relationships and unstructured document passages.

## Why Graph RAG

A normal RAG system uses a vector search index to retrieve document chunks relevant to a question, then conditions an LLM on those chunks to generate an answer.

Graph RAG extends that approach by adding an explicit knowledge graph layer:

- graph extraction captures entities and rich semantic relationships from text,
- graph retrieval can answer questions about connections, dependencies, and multi-hop semantics,
- graph context provides a more explainable path from question to answer,
- hybrid retrieval combines graph evidence with text evidence for more robust responses.

## How this differs from standard RAG

Standard RAG
- relies primarily on vector embeddings and similarity search,
- treats content as a bag of text chunks,
- can struggle with multi-step reasoning over relationships,
- returns answers that are often hard to trace back to specific concepts.

Graph RAG
- explicitly models entities and relations,
- can traverse concept relationships and infer structured answers,
- preserves source structure for better interpretability,
- supports graph-based query reasoning as well as text retrieval.

## Why this matters for enterprise applications

Enterprise knowledge work benefits from Graph RAG because organizations need:

- explainable insights from complex documents,
- structured understanding of concepts, products, processes, and dependencies,
- the ability to answer multi-hop questions across connected knowledge,
- a combination of graph knowledge and source document evidence.

This project demonstrates how a graph layer can improve enterprise use cases like:

- technical documentation QA,
- research and patents analysis,
- compliance and policy understanding,
- customer support knowledge bases,
- decision support systems.

## Architecture and core components

- `code.py` — application entrypoint.
  - loads a PDF or text file,
  - extracts entities and relationships,
  - builds an in-memory graph,
  - runs graph and vector retrieval,
  - generates an answer.

- `ontology.py` — entity and relationship ontology.
  - defines entity types and relationship types,
  - normalizes labels and aliases for Transformer paper concepts.

- `entity_extractor.py` — entity extraction.
  - identifies domain entities from text,
  - validates extracted entity schema.

- `relationship_extractor.py` — relationship extraction.
  - identifies relationships between entities,
  - validates relation structure.

- `neo4j_loader.py` — in-memory graph store.
  - stores entities and relationships,
  - supports simple graph lookup and traversal.

- `graph_retrieval.py` — graph-based retrieval logic.
  - looks up entities,
  - builds subgraphs,
  - formats graph context for answer generation.

- `vector_retrival.py` — lightweight vector-style retrieval.
  - scores document chunks by token overlap,
  - returns supporting passages.

- `hybrid_retrieval.py` — combines graph and vector evidence.

- `context_builder.py` — assembles the answer context.

- `answer_generator.py` — creates the final answer text.

- `evaluator.py` — tracks query metrics and retrieval counts.

- `logger.py` — writes UTF-8 JSONL logs for queries and errors.

## Running the project

From the repository root, run:

```powershell
python code.py "C:\Users\robba\Downloads\Attention is all you need.pdf"
```

Or with a text file:

```powershell
python code.py "C:\path\to\your\file.txt"
```

You can also set an environment variable before running:

```powershell
set KG_RAG_INPUT=C:\Users\robba\Downloads\Attention is all you need.pdf
python code.py
```

After startup, type your question and press Enter. Enter `exit` or `quit` to stop.

## Key differences in this implementation

- this repo is runnable locally without an external LLM or a real Neo4j database,
- it replaces missing modules and broken imports from the original scaffold,
- it adds PDF normalization and UTF-8-safe logging to reduce encoding issues,
- it is tuned for Transformer / attention paper concepts while preserving a general graph-RAG architecture.

## Limitations

- graph storage is an in-memory shim, not a production graph database,
- retrieval uses token overlap instead of real embedding search,
- answer generation is template-based rather than driven by a full LLM,
- extraction heuristics are simplified and tuned to the Transformer paper.

## Future improvements

- add a real Neo4j or graph database backend,
- use actual embeddings for vector search,
- connect to a real LLM for answer generation,
- add enterprise-grade tests and documentation,
- improve extraction quality for broader domains.
