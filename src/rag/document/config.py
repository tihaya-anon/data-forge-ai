"""
Configuration for the document processing module.
"""

from pydantic import BaseModel
from typing import Optional


class DocumentProcessingConfig(BaseModel):
    """Configuration for document processing."""
    
    # Default chunking settings
    default_chunk_size: int = 512
    default_chunk_overlap: int = 50
    default_chunk_method: str = 'fixed'
    
    # Deduplication settings
    deduplication_threshold: float = 0.95
    
    # Supported file formats
    supported_formats: list = ['.pdf', '.docx', '.txt']
    
    # Semantic chunking options
    enable_semantic_chunking: bool = True
    sentence_separator: str = r'[.!?]+\s+'
    
    class Config:
        extra = "forbid"