#vector_retrieval.py
"""
Vector Retrieval Pipeline

Responsibilities:
1. Embed Query
2. Semantic Search
3. Retrieve Top-K Chunks
"""

from typing import Dict, List


class VectorRetriever:
    """
    Orchestrates the complete vector retrieval pipeline.
    """

    def __init__(
        self,
        embedder,
        vector_db,
        top_k: int = 5,
    ):
        """
        embedder:
            Embedding model used during ingestion.

        vector_db:
            Vector database client (PgVector, Chroma, FAISS, etc.)

        top_k:
            Number of chunks to retrieve.
        """
        # ERROR HANDLING: embedder might be None or invalid
        # ERROR HANDLING: vector_db might be None or invalid
        # ERROR HANDLING: top_k might be negative or zero
        # ACTION: Validate inputs, set defaults, log warnings
        
        if embedder is None:
            print("Error: embedder is None")
            # ACTION: Set a default or raise exception
            self.embedder = None
        else:
            self.embedder = embedder
            
        if vector_db is None:
            print("Error: vector_db is None")
            self.vector_db = None
        else:
            self.vector_db = vector_db
            
        # ERROR HANDLING: top_k validation
        if not isinstance(top_k, int) or top_k < 1:
            print(f"Warning: Invalid top_k value {top_k}, defaulting to 5")
            self.top_k = 5
        elif top_k > 100:
            print(f"Warning: top_k {top_k} is very high, consider reducing")
            self.top_k = top_k
        else:
            self.top_k = top_k

    # --------------------------------------------------
    # Step 1 : Embed Query
    # --------------------------------------------------

    def embed_query(
        self,
        query: str,
    ) -> List[float]:
        """
        Generate embedding for the user query.
        """
        # ERROR HANDLING: query might be None, empty, or invalid type
        # ERROR HANDLING: embedder might be None
        # ERROR HANDLING: embedder.get_embedding might fail
        # ACTION: Validate query, check embedder, handle errors gracefully
        
        if not query:
            print("Error: Query is empty or None")
            return []
            
        if not isinstance(query, str):
            print(f"Error: Query must be a string, got {type(query)}")
            return []
            
        if self.embedder is None:
            print("Error: Embedder is not initialized")
            return []

        try:
            # TODO:
            # Generate embedding using the same
            # embedding model used during ingestion.

            #
            # Example:
            #
            # embedding = self.embedder.get_embedding(query)
            #

            # ERROR HANDLING: embedder might not have get_embedding method
            # ERROR HANDLING: embedding generation might fail due to API/network issues
            # ERROR HANDLING: embedding might be None or empty
            
            embedding = []
            
            # Check if embedder has the required method
            if hasattr(self.embedder, 'get_embedding'):
                embedding = self.embedder.get_embedding(query)
            else:
                print("Error: embedder does not have get_embedding method")
                return []
                
            # Validate embedding
            if not embedding:
                print("Warning: Generated embedding is empty")
                return []
                
            if not isinstance(embedding, list):
                print(f"Warning: Embedding is not a list, got {type(embedding)}")
                return []
                
            return embedding
            
        except AttributeError as e:
            print(f"Error: Embedder missing required method: {e}")
            return []
            
        except Exception as e:
            # ERROR HANDLING: Catch all embedding errors
            print(f"Error generating embedding: {e}")
            return []

    # --------------------------------------------------
    # Step 2 : Semantic Search
    # --------------------------------------------------

    def semantic_search(
        self,
        query: str,
    ) -> List[Dict]:
        """
        Perform similarity search in the vector database.
        """
        # ERROR HANDLING: query_embedding might be None or empty
        # ERROR HANDLING: vector_db might be None
        # ERROR HANDLING: vector_db.search might fail
        # ERROR HANDLING: Search might return None or invalid results
        # ACTION: Validate embedding, check vector_db, handle search errors
        
        if not query:
            print("Error: Query is empty or None")
            return []
            
        if not isinstance(query, str):
            print(f"Error: query must be a string, got {type(query)}")
            return []
            
        if self.vector_db is None:
            print("Error: Vector database is not initialized")
            return []

        try:
            if hasattr(self.vector_db, 'search'):
                results = self.vector_db.search(
                    query=query,
                    limit=self.top_k,
                )
            else:
                print("Error: vector_db does not have search method")
                return []
                
            # Validate results
            if results is None:
                print("Warning: Search returned None")
                return []
                
            if not isinstance(results, list):
                print(f"Warning: Search results not a list, got {type(results)}")
                # Try to convert to list if possible
                try:
                    results = list(results)
                except:
                    return []
                    
            return results
            
        except Exception as e:
            # ERROR HANDLING: Catch all search errors
            print(f"Error during semantic search: {e}")
            return []

    # --------------------------------------------------
    # Step 3 : Retrieve Top-K Chunks
    # --------------------------------------------------

    def retrieve_top_k(
        self,
        results: List[Dict],
    ) -> List[Dict]:
        """
        Extract the most relevant chunks.
        """
        # ERROR HANDLING: results might be None or empty
        # ERROR HANDLING: Results might not have required keys
        # ERROR HANDLING: Result values might be invalid
        # ACTION: Validate results, handle missing keys, skip invalid results
        
        if not results:
            print("Warning: No results to process")
            return []
            
        if not isinstance(results, list):
            print(f"Error: results must be a list, got {type(results)}")
            return []

        chunks = []
        
        # ERROR HANDLING: Limit number of chunks to top_k
        # ACTION: Only process up to top_k results
        results_to_process = results[:self.top_k]

        for idx, result in enumerate(results_to_process):
            try:
                if isinstance(result, dict):
                    chunk = {
                        "chunk_id": result.get("chunk_id", f"chunk_{idx}"),
                        "score": result.get("score", 0.0),
                        "text": result.get("text", ""),
                        "metadata": result.get("metadata", {}),
                    }
                else:
                    chunk = {
                        "chunk_id": getattr(result, "id", f"chunk_{idx}"),
                        "score": getattr(result, "reranking_score", 0.0) or 0.0,
                        "text": getattr(result, "content", ""),
                        "metadata": getattr(result, "meta_data", {}) or {},
                    }
                
                # ERROR HANDLING: Validate that text is not empty
                if not chunk["text"]:
                    print(f"Warning: Empty text in chunk at index {idx}")
                    # Still include it but with warning
                    
                chunks.append(chunk)
                
            except Exception as e:
                # ERROR HANDLING: Unexpected error processing result
                print(f"Error processing result at index {idx}: {e}")
                continue

        return chunks

    # --------------------------------------------------
    # Build Vector Context
    # --------------------------------------------------

    def build_vector_context(
        self,
        chunks: List[Dict],
    ) -> str:
        """
        Merge retrieved chunks into a single context.
        """
        # ERROR HANDLING: chunks might be None or empty
        # ERROR HANDLING: Chunks might not have 'text' key
        # ERROR HANDLING: Text might be None or not a string
        # ACTION: Validate chunks, skip invalid ones, return empty string if needed
        
        if not chunks:
            print("Warning: No chunks to build context from")
            return ""
            
        if not isinstance(chunks, list):
            print(f"Error: chunks must be a list, got {type(chunks)}")
            return ""

        context = []
        
        for idx, chunk in enumerate(chunks):
            # ERROR HANDLING: chunk might not be a dict
            if not isinstance(chunk, dict):
                print(f"Warning: Skipping non-dict chunk at index {idx}")
                continue
                
            # ERROR HANDLING: chunk might not have 'text' key
            chunk_text = chunk.get("text")
            
            if chunk_text is None:
                print(f"Warning: Missing 'text' key in chunk at index {idx}")
                continue
                
            if not isinstance(chunk_text, str):
                print(f"Warning: Converting non-string text to string at index {idx}")
                chunk_text = str(chunk_text)
                
            if not chunk_text.strip():
                print(f"Warning: Empty text in chunk at index {idx}")
                continue
                
            context.append(chunk_text)

        # ERROR HANDLING: Join with proper separator
        if not context:
            print("Warning: No valid text found in chunks")
            return ""
            
        try:
            return "\n\n".join(context)
        except Exception as e:
            # ERROR HANDLING: Join operation might fail
            print(f"Error building context: {e}")
            return ""

    # --------------------------------------------------
    # Complete Pipeline
    # --------------------------------------------------

    def run(
        self,
        structured_query: Dict,
    ) -> Dict:
        """
        Complete vector retrieval pipeline.
        """
        # ERROR HANDLING: structured_query might be None or missing 'query'
        # ERROR HANDLING: Any pipeline step might fail
        # ACTION: Validate input, implement try-except for each step
        
        if not structured_query:
            print("Error: Empty structured_query provided")
            return {
                "query_embedding": [],
                "retrieved_chunks": [],
                "vector_context": ""
            }
            
        if not isinstance(structured_query, dict):
            print(f"Error: structured_query must be a dictionary, got {type(structured_query)}")
            return {
                "query_embedding": [],
                "retrieved_chunks": [],
                "vector_context": ""
            }
            
        if "query" not in structured_query:
            print("Warning: structured_query missing 'query' key")
            structured_query["query"] = ""
            
        query = structured_query.get("query", "")
        
        # ERROR HANDLING: query might be None or empty
        if not query:
            print("Warning: Empty query in structured_query")
            # Return default structure instead of failing
            return {
                "query_embedding": [],
                "retrieved_chunks": [],
                "vector_context": ""
            }

        try:
            query_embedding = self.embed_query(query)
            
            # ERROR HANDLING: Check if embedding was successful
            if not query_embedding:
                print("Warning: Failed to generate query embedding")
                return {
                    "query_embedding": [],
                    "retrieved_chunks": [],
                    "vector_context": ""
                }

            search_results = self.semantic_search(query)
            
            # ERROR HANDLING: Search might return None
            if search_results is None:
                print("Warning: Semantic search returned None")
                search_results = []

            retrieved_chunks = self.retrieve_top_k(search_results)
            
            # ERROR HANDLING: Retrieved chunks might be None
            if retrieved_chunks is None:
                print("Warning: retrieve_top_k returned None")
                retrieved_chunks = []

            vector_context = self.build_vector_context(retrieved_chunks)
            
            # ERROR HANDLING: Vector context might be None
            if vector_context is None:
                print("Warning: build_vector_context returned None")
                vector_context = ""

            return {
                "query_embedding": query_embedding,
                "retrieved_chunks": retrieved_chunks,
                "vector_context": vector_context,
            }
            
        except Exception as e:
            # ERROR HANDLING: Catch-all for pipeline errors
            print(f"Vector retrieval pipeline failed: {e}")
            return {
                "query_embedding": [],
                "retrieved_chunks": [],
                "vector_context": ""
            }
