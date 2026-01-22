"""
Configuration module for Elasticsearch keyword retrieval service
"""

from typing import Optional
from pydantic import BaseModel, Field


class ElasticsearchConfig(BaseModel):
    """Configuration for Elasticsearch keyword retrieval service"""
    
    hosts: str = Field(default="localhost:9200", description="Elasticsearch hosts")
    index_name: str = Field(default="documents", description="Index name to use")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_on_timeout: bool = Field(default=True, description="Whether to retry on timeout")
    sniff_on_start: bool = Field(default=False, description="Sniff on start")
    sniff_on_connection_fail: bool = Field(default=False, description="Sniff on connection failure")
    sniffer_timeout: Optional[int] = Field(default=None, description="Sniffer timeout")
    http_auth: Optional[str] = Field(default=None, description="HTTP authentication credentials")
    use_ssl: bool = Field(default=False, description="Use SSL connection")
    verify_certs: bool = Field(default=True, description="Verify SSL certificates")
    ca_certs: Optional[str] = Field(default=None, description="Path to CA certificates")
    client_cert: Optional[str] = Field(default=None, description="Path to client certificate")
    client_key: Optional[str] = Field(default=None, description="Path to client key")
    
    class Config:
        """Pydantic config"""
        extra = "forbid"