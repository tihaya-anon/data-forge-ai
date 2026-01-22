"""
Vector Retrieval Service Module for DataForge AI

This module provides functionality for:
- Milvus query interface
- Similarity calculation
- Top-K retrieval
- Filter condition support
"""

from typing import List, Dict, Any, Optional, Union
import numpy as np
from ...embedding import BGEEmbedding, EmbeddingModel


class VectorRetrievalService:
    """Service class for vector retrieval operations."""
    
    def __init__(self, embedding_model: Optional[EmbeddingModel] = None):
        self.embedding_model = embedding_model or BGEEmbedding()
        self.milvus_client = None
    
    def connect_to_milvus(self, host: str = "localhost", port: int = 19530):
        """Connect to Milvus vector database."""
        try:
            from pymilvus import connections
            connections.connect(alias="default", host=host, port=port)
            self.milvus_client = connections.get_connection(alias="default")
        except ImportError:
            raise ImportError(
                "PyMilvus is required to connect to Milvus. "
                "Install it with: pip install pymilvus"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Milvus: {str(e)}")
    
    def similarity_search(
        self,
        query: str,
        collection_name: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        embedding_model: Optional[EmbeddingModel] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search in Milvus collection.
        
        Args:
            query: Query text to search for similar vectors
            collection_name: Name of the Milvus collection
            top_k: Number of top results to return
            filters: Optional filters to apply during search
            embedding_model: Optional embedding model to use
            
        Returns:
            List of dictionaries containing search results with distance scores
        """
        if not self.milvus_client:
            raise RuntimeError("Not connected to Milvus. Call connect_to_milvus first.")
        
        # Generate embedding for the query
        model = embedding_model or self.embedding_model
        query_embedding = model.embed_query(query)
        
        # Perform search in Milvus
        try:
            from pymilvus import Collection
        except ImportError:
            raise ImportError(
                "PyMilvus is required to perform similarity search. "
                "Install it with: pip install pymilvus"
            )
        
        collection = Collection(collection_name)
        
        # Prepare search parameters
        search_params = {
            "data": [query_embedding],
            "anns_field": "embedding",
            "param": {"metric_type": "COSINE", "params": {"nprobe": 10}},
            "limit": top_k,
            "output_fields": ["text", "id"],  # Add other fields as needed
        }
        
        # Apply filters if provided
        if filters:
            filter_expr = self._build_filter_expression(filters)
            search_params["expr"] = filter_expr
        
        # Execute search
        results = collection.search(**search_params)
        
        # Format results
        formatted_results = []
        for i, hit in enumerate(results[0]):  # Results are organized by query (we have 1)
            result = {
                "id": hit.id,
                "distance": hit.distance,
                "entity": dict(hit.entity) if hasattr(hit, 'entity') else {}
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def _build_filter_expression(self, filters: Dict[str, Any]) -> str:
        """
        Build a filter expression string from a dictionary of filters.
        
        Args:
            filters: Dictionary of field-value pairs to filter on
            
        Returns:
            Filter expression string compatible with Milvus
        """
        expressions = []
        for field, value in filters.items():
            if isinstance(value, str):
                expressions.append(f'{field} == "{value}"')
            elif isinstance(value, (int, float)):
                expressions.append(f'{field} == {value}')
            elif isinstance(value, list):
                # Handle list of values (IN clause)
                if all(isinstance(v, str) for v in value):
                    values_str = ", ".join([f'"{v}"' for v in value])
                    expressions.append(f'{field} in [{values_str}]')
                else:
                    values_str = ", ".join([str(v) for v in value])
                    expressions.append(f'{field} in [{values_str}]')
            else:
                expressions.append(f'{field} == "{str(value)}"')
        
        return " and ".join(expressions) if expressions else ""
    
    def calculate_similarity(
        self, 
        vector_a: List[float], 
        vector_b: List[float], 
        metric: str = "cosine"
    ) -> float:
        """
        Calculate similarity between two vectors.
        
        Args:
            vector_a: First vector
            vector_b: Second vector
            metric: Similarity metric to use ('cosine', 'euclidean', 'dot_product')
            
        Returns:
            Similarity score as a float
        """
        vec_a = np.array(vector_a)
        vec_b = np.array(vector_b)
        
        if metric == "cosine":
            # Cosine similarity
            dot_product = np.dot(vec_a, vec_b)
            norm_a = np.linalg.norm(vec_a)
            norm_b = np.linalg.norm(vec_b)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return float(dot_product / (norm_a * norm_b))
        elif metric == "euclidean":
            # Euclidean distance (convert to similarity)
            distance = np.linalg.norm(vec_a - vec_b)
            # Convert distance to similarity (higher value = more similar)
            return float(1 / (1 + distance))
        elif metric == "dot_product":
            # Dot product
            return float(np.dot(vec_a, vec_b))
        else:
            raise ValueError(f"Unsupported similarity metric: {metric}")
    
    def hybrid_search(
        self,
        query: str,
        collection_name: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        weight_vector: float = 0.7,
        weight_text: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and text-based search.
        NOTE: This is a placeholder for future implementation.
        """
        # This method would combine vector search with keyword search
        # For now, we'll just delegate to similarity_search
        return self.similarity_search(query, collection_name, top_k, filters)