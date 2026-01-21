"""
Kafka Consumer configuration and base classes for DataForge AI.

This module defines the configuration models for Kafka consumers with advanced features:
- Batch processing
- Dead Letter Queue support
- Graceful shutdown
- Metrics collection
"""

import logging
from typing import Any, Dict, List, Optional, Union, Callable
from pydantic import BaseModel, Field
from enum import Enum


logger = logging.getLogger(__name__)


class AutoOffsetReset(Enum):
    EARLIEST = "earliest"
    LATEST = "latest"
    NONE = "none"


class IsolationLevel(Enum):
    READ_COMMITTED = "read_committed"
    READ_UNCOMMITTED = "read_uncommitted"


class KafkaConsumerConfig(BaseModel):
    """Configuration for Kafka Consumer with advanced features."""
    
    bootstrap_servers: Union[str, List[str]] = Field(
        default=["localhost:9092"],
        description="List of bootstrap servers"
    )
    group_id: str = Field(
        ..., 
        description="Consumer group ID"
    )
    topics: List[str] = Field(
        default=[],
        description="List of topics to subscribe to"
    )
    auto_offset_reset: AutoOffsetReset = Field(
        default=AutoOffsetReset.EARLIEST,
        description="What to do when there is no initial offset or offset is out of range"
    )
    enable_auto_commit: bool = Field(
        default=True,
        description="If true the consumer's offset will be periodically committed"
    )
    auto_commit_interval_ms: int = Field(
        default=5000,
        description="Frequency in milliseconds that the consumer offsets are auto-committed"
    )
    client_id: Optional[str] = Field(
        default=None,
        description="Optional client identifier"
    )
    max_poll_records: int = Field(
        default=100,
        description="Max number of records returned in a single poll"
    )
    max_poll_interval_ms: int = Field(
        default=300000,  # 5 minutes
        description="Maximum poll interval in milliseconds"
    )
    session_timeout_ms: int = Field(
        default=10000,
        description="Session timeout in milliseconds"
    )
    heartbeat_interval_ms: int = Field(
        default=3000,
        description="Heartbeat interval in milliseconds"
    )
    isolation_level: IsolationLevel = Field(
        default=IsolationLevel.READ_COMMITTED,
        description="Controls the visibility of transactional records"
    )
    
    # Advanced features configuration
    batch_processing_enabled: bool = Field(
        default=False,
        description="Enable batch processing of messages"
    )
    batch_size: int = Field(
        default=100,
        description="Maximum number of messages to process in a batch"
    )
    batch_timeout_ms: int = Field(
        default=5000,
        description="Maximum time to wait for a batch to fill before processing"
    )
    
    dead_letter_queue_enabled: bool = Field(
        default=False,
        description="Enable dead letter queue for failed messages"
    )
    dead_letter_queue_topic: Optional[str] = Field(
        default=None,
        description="Topic to send failed messages to"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for a message before sending to DLQ"
    )
    
    metrics_enabled: bool = Field(
        default=False,
        description="Enable metrics collection"
    )
    metrics_prefix: str = Field(
        default="dataforge.kafka.consumer",
        description="Prefix for metrics names"
    )


class ConsumerStatus(Enum):
    """Enumeration of consumer statuses."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"