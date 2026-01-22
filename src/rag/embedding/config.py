"""
Configuration for Embedding Service Module
"""

from typing import Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EmbeddingConfig:
    """Configuration for embedding service."""
    
    # Model settings
    model_name: str = "BAAI/bge-large-zh"
    normalize_embeddings: bool = True
    max_seq_length: int = 512
    
    # Cache settings
    cache_enabled: bool = True
    cache_max_size: int = 10000
    
    # Batch processing settings
    batch_size: int = 32
    enable_batch_processing: bool = True
    
    # Milvus connection settings
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    collection_name: str = "document_embeddings"
    
    # Performance settings
    num_workers: int = 4
    use_gpu: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.max_seq_length <= 0:
            raise ValueError("max_seq_length must be positive")
        
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        
        if self.cache_max_size <= 0:
            raise ValueError("cache_max_size must be positive")
        
        if not (1 <= self.milvus_port <= 65535):
            raise ValueError("milvus_port must be between 1 and 65535")


def load_embedding_config(config_path: Optional[str] = None) -> EmbeddingConfig:
    """
    Load embedding configuration from file or return default.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        EmbeddingConfig instance
    """
    # In a real implementation, we would load from a file
    # For now, returning default configuration
    return EmbeddingConfig()


def get_default_embedding_config() -> EmbeddingConfig:
    """
    Get default embedding configuration.
    
    Returns:
        EmbeddingConfig instance with default values
    """
    return EmbeddingConfig()