"""
Configuration for Vector Retrieval Service Module
"""

from typing import Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VectorRetrievalConfig:
    """Configuration for vector retrieval service."""
    
    # Milvus connection settings
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    default_collection_name: str = "document_embeddings"
    
    # Search settings
    default_top_k: int = 10
    similarity_metric: str = "cosine"  # cosine, euclidean, dot_product
    search_params: dict = None  # Additional search parameters for Milvus
    
    # Performance settings
    num_parallel_queries: int = 4
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600  # Time to live for cache entries
    
    # Filter settings
    enable_metadata_filters: bool = True
    enable_full_text_filters: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.default_top_k <= 0:
            raise ValueError("default_top_k must be positive")
        
        if not (1 <= self.milvus_port <= 65535):
            raise ValueError("milvus_port must be between 1 and 65535")
        
        if self.similarity_metric not in ["cosine", "euclidean", "dot_product"]:
            raise ValueError(f"similarity_metric must be one of: cosine, euclidean, dot_product")
        
        if self.cache_ttl_seconds <= 0:
            raise ValueError("cache_ttl_seconds must be positive")
        
        if self.search_params is None:
            self.search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }


def load_vector_retrieval_config(config_path: Optional[str] = None) -> VectorRetrievalConfig:
    """
    Load vector retrieval configuration from file or return default.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        VectorRetrievalConfig instance
    """
    # In a real implementation, we would load from a file
    # For now, returning default configuration
    return VectorRetrievalConfig()


def get_default_vector_retrieval_config() -> VectorRetrievalConfig:
    """
    Get default vector retrieval configuration.
    
    Returns:
        VectorRetrievalConfig instance with default values
    """
    return VectorRetrievalConfig()