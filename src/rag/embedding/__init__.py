"""
Embedding Service Module for DataForge AI

This module provides functionality for:
- BGE model integration
- Batch embedding
- Vector caching
- Milvus storage integration
"""

from typing import List, Dict, Any, Optional
import numpy as np
import hashlib
from pathlib import Path


class EmbeddingModel:
    """Abstract base class for embedding models."""
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Convert a list of texts to their embeddings."""
        raise NotImplementedError
    
    def embed_query(self, text: str) -> List[float]:
        """Convert a single text to its embedding."""
        raise NotImplementedError


class BGEEmbedding(EmbeddingModel):
    """BGE (BAAI General Embedding) model integration."""
    
    def __init__(self, model_name: str = "BAAI/bge-large-zh", normalize_embeddings: bool = True):
        self.model_name = model_name
        self.normalize_embeddings = normalize_embeddings
        self._model = None
        self._tokenizer = None
    
    def _load_model(self):
        """Load the BGE model and tokenizer."""
        try:
            from transformers import AutoTokenizer, AutoModel
        except ImportError:
            raise ImportError(
                "Transformers is required to use BGE model. "
                "Install it with: pip install transformers torch"
            )
        
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModel.from_pretrained(self.model_name)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Convert a list of texts to their embeddings using BGE model."""
        if not self._model or not self._tokenizer:
            self._load_model()
        
        import torch
        
        # Tokenize the input texts
        encoded_input = self._tokenizer(
            texts, 
            padding=True, 
            truncation=True, 
            return_tensors='pt',
            max_length=512
        )
        
        # Compute token embeddings
        with torch.no_grad():
            model_output = self._model(**encoded_input)
            # Get the embeddings of the first token (CLS token)
            sentence_embeddings = model_output.last_hidden_state[:, 0]
        
        # Normalize embeddings if required
        if self.normalize_embeddings:
            sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        
        # Convert to list of lists
        embeddings_list = sentence_embeddings.tolist()
        
        return embeddings_list
    
    def embed_query(self, text: str) -> List[float]:
        """Convert a single text to its embedding."""
        return self.embed_texts([text])[0]


class VectorCache:
    """Simple cache for storing computed embeddings."""
    
    def __init__(self):
        self.cache = {}
    
    def _hash_key(self, text: str) -> str:
        """Generate a hash key for the given text."""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache if exists."""
        key = self._hash_key(text)
        return self.cache.get(key)
    
    def put(self, text: str, embedding: List[float]) -> None:
        """Put embedding into cache."""
        key = self._hash_key(text)
        self.cache[key] = embedding
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()


class EmbeddingService:
    """Main class for embedding service."""
    
    def __init__(self, embedding_model: EmbeddingModel = None, cache: VectorCache = None):
        self.embedding_model = embedding_model or BGEEmbedding()
        self.cache = cache or VectorCache()
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
    
    def batch_embed_texts(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Batch convert texts to embeddings with optional caching."""
        if not texts:
            return []
        
        results = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for idx, text in enumerate(texts):
            if use_cache:
                cached_embedding = self.cache.get(text)
                if cached_embedding is not None:
                    results.append(cached_embedding)
                    continue
            
            # Mark for processing
            uncached_texts.append(text)
            uncached_indices.append(idx)
            # Placeholder for result to maintain order
            results.append(None)
        
        # Process uncached texts
        if uncached_texts:
            embeddings = self.embedding_model.embed_texts(uncached_texts)
            
            # Update cache and results
            for i, (orig_idx, text, emb) in enumerate(zip(uncached_indices, uncached_texts, embeddings)):
                results[orig_idx] = emb
                if use_cache:
                    self.cache.put(text, emb)
        
        return results
    
    def embed_documents(self, documents: List[Dict[str, Any]], use_cache: bool = True) -> List[Dict[str, Any]]:
        """Embed documents and return enriched documents with embeddings."""
        if not documents:
            return []
        
        texts = [doc.get('content', '') for doc in documents]
        embeddings = self.batch_embed_texts(texts, use_cache)
        
        # Create enriched documents
        enriched_docs = []
        for doc, embedding in zip(documents, embeddings):
            enriched_doc = doc.copy()
            enriched_doc['embedding'] = embedding
            enriched_docs.append(enriched_doc)
        
        return enriched_docs
    
    def store_embeddings_in_milvus(
        self, 
        documents: List[Dict[str, Any]], 
        collection_name: str,
        recreate_collection: bool = False
    ):
        """Store embeddings in Milvus vector database."""
        if not self.milvus_client:
            raise RuntimeError("Not connected to Milvus. Call connect_to_milvus first.")
        
        try:
            from pymilvus import (
                Collection, 
                FieldSchema, 
                CollectionSchema, 
                DataType,
                connections,
                utility
            )
        except ImportError:
            raise ImportError(
                "PyMilvus is required to store embeddings in Milvus. "
                "Install it with: pip install pymilvus"
            )
        
        # Prepare data
        texts = [doc.get('content', '') for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        embeddings = [doc.get('embedding') for doc in documents]
        
        # If embedding is not present, compute it
        if any(not emb for emb in embeddings):
            embeddings = self.batch_embed_texts(texts)
            # Update documents with embeddings
            for doc, emb in zip(documents, embeddings):
                doc['embedding'] = emb
        
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),  # Assuming BGE-large
        ]
        
        # Add metadata fields if available
        if metadatas and isinstance(metadatas[0], dict):
            for key, value in metadatas[0].items():
                if isinstance(value, str):
                    fields.append(FieldSchema(name=f"metadata_{key}", dtype=DataType.VARCHAR, max_length=65535))
                elif isinstance(value, int):
                    fields.append(FieldSchema(name=f"metadata_{key}", dtype=DataType.INT64))
                elif isinstance(value, float):
                    fields.append(FieldSchema(name=f"metadata_{key}", dtype=DataType.DOUBLE))
                else:
                    # Default to string for other types
                    fields.append(FieldSchema(name=f"metadata_{key}", dtype=DataType.VARCHAR, max_length=65535))
        
        schema = CollectionSchema(fields=fields, description="Document embeddings")
        
        # Create or recreate collection
        if recreate_collection and utility.has_collection(collection_name):
            Collection(collection_name).drop()
        
        if not utility.has_collection(collection_name):
            collection = Collection(name=collection_name, schema=schema)
        else:
            collection = Collection(collection_name)
        
        # Prepare data for insertion
        insert_data = []
        insert_data.append(texts)  # text field
        insert_data.append(embeddings)  # embedding field
        
        # Add metadata fields
        if metadatas and isinstance(metadatas[0], dict):
            for key in metadatas[0].keys():
                col_data = []
                for metadata in metadatas:
                    val = metadata.get(key, "")
                    col_data.append(str(val))  # Convert all values to strings to prevent type errors
                insert_data.append(col_data)
        
        # Insert data
        collection.insert(insert_data)
        
        # Create index if not exists
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 128}
        }
        
        if not collection.has_index():
            collection.create_index(field_name="embedding", index_params=index_params)
        
        # Load collection for searching
        collection.load()
        
        return {"status": "success", "count": len(documents), "collection": collection_name}


# Convenience function for common operations

def create_embeddings_for_documents(
    documents: List[Dict[str, Any]], 
    use_cache: bool = True,
    model_name: str = "BAAI/bge-large-zh"
) -> List[Dict[str, Any]]:
    """
    Create embeddings for a list of documents in one step.
    
    Args:
        documents: List of documents with 'content' field
        use_cache: Whether to use caching
        model_name: Name of the BGE model to use
        
    Returns:
        List of documents with added 'embedding' field
    """
    embedding_service = EmbeddingService(BGEEmbedding(model_name=model_name))
    return embedding_service.embed_documents(documents, use_cache=use_cache)