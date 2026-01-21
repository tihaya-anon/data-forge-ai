"""
Kafka Producer implementation for DataForge AI.

This module provides a wrapper around kafka-python's KafkaProducer with:
- Connection management and configuration
- Synchronous and asynchronous message sending
- Basic error handling
"""

import json
import logging
from typing import Any, Dict, Optional, Union, Callable
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError, NoBrokersAvailable
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class KafkaProducerConfig(BaseModel):
    """Configuration for Kafka Producer."""
    
    bootstrap_servers: Union[str, list] = Field(
        default=["localhost:9092"], 
        description="List of bootstrap servers"
    )
    client_id: Optional[str] = Field(default=None, description="Client identifier")
    acks: Union[str, int] = Field(
        default="all", 
        description="Number of acknowledgments the producer requires"
    )
    retries: int = Field(default=3, description="Number of retry attempts")
    batch_size: int = Field(default=16384, description="Batch size in bytes")
    linger_ms: int = Field(default=5, description="Linger time in milliseconds")
    buffer_memory: int = Field(default=33554432, description="Buffer memory in bytes")
    compression_type: Optional[str] = Field(
        default="snappy", 
        description="Compression type (none, gzip, snappy, lz4, zstd)"
    )
    key_serializer: Optional[Callable] = Field(
        default=None, 
        description="Function to serialize keys"
    )
    value_serializer: Optional[Callable] = Field(
        default=None, 
        description="Function to serialize values"
    )


class DataForgeKafkaProducer:
    """
    A Kafka producer wrapper for DataForge AI with connection management,
    synchronous/asynchronous sending capabilities, and basic error handling.
    """
    
    def __init__(self, config: KafkaProducerConfig):
        """
        Initialize the Kafka producer with the given configuration.
        
        Args:
            config: Configuration object for the Kafka producer
        """
        self.config = config
        self._producer: Optional[KafkaProducer] = None
        
        # Set up serializers if not provided
        key_serializer = config.key_serializer or str.encode
        value_serializer = config.value_serializer or (
            lambda x: json.dumps(x).encode('utf-8') if isinstance(x, dict) else x.encode('utf-8')
        )
        
        try:
            self._producer = KafkaProducer(
                bootstrap_servers=config.bootstrap_servers,
                client_id=config.client_id,
                acks=config.acks,
                retries=config.retries,
                batch_size=config.batch_size,
                linger_ms=config.linger_ms,
                buffer_memory=config.buffer_memory,
                compression_type=config.compression_type,
                key_serializer=key_serializer,
                value_serializer=value_serializer,
                request_timeout_ms=30000,  # 30 seconds timeout
                max_block_ms=5000         # 5 seconds to wait for metadata
            )
            logger.info(f"Kafka producer initialized successfully with {config.bootstrap_servers}")
        except NoBrokersAvailable:
            logger.error("Could not connect to Kafka brokers. Check if Kafka is running.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            raise
    
    def send_sync(self, topic: str, value: Any, key: Optional[str] = None) -> bool:
        """
        Synchronously send a message to Kafka.
        
        Args:
            topic: Topic name to send the message to
            value: Message value to send
            key: Optional message key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Send message synchronously by waiting for the future
            future = self._producer.send(topic, value=value, key=key)
            record_metadata = future.get(timeout=10)  # Wait up to 10 seconds
            
            logger.debug(
                f"Message sent successfully to topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, offset={record_metadata.offset}"
            )
            return True
            
        except KafkaTimeoutError:
            logger.error(f"Timeout while sending message to topic '{topic}'")
            return False
        except KafkaError as e:
            logger.error(f"Kafka error while sending message to topic '{topic}': {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending message to topic '{topic}': {str(e)}")
            return False
    
    def send_async(self, topic: str, value: Any, key: Optional[str] = None, 
                   callback: Optional[Callable] = None) -> bool:
        """
        Asynchronously send a message to Kafka.
        
        Args:
            topic: Topic name to send the message to
            value: Message value to send
            key: Optional message key
            callback: Optional callback function to execute after sending
            
        Returns:
            True if the message was accepted for sending, False otherwise
        """
        try:
            self._producer.send(topic, value=value, key=key, callback=callback)
            logger.debug(f"Asynchronous message sent to topic '{topic}'")
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error while sending message to topic '{topic}': {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending message to topic '{topic}': {str(e)}")
            return False
    
    def flush(self):
        """
        Flush all pending messages to Kafka.
        """
        if self._producer:
            self._producer.flush()
            logger.debug("All pending messages flushed to Kafka")
    
    def close(self):
        """
        Close the Kafka producer and clean up resources.
        """
        if self._producer:
            self._producer.close()
            logger.info("Kafka producer closed successfully")
            self._producer = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_kafka_producer(config_dict: Dict[str, Any]) -> DataForgeKafkaProducer:
    """
    Factory function to create a Kafka producer instance from a dictionary configuration.
    
    Args:
        config_dict: Dictionary containing producer configuration
        
    Returns:
        DataForgeKafkaProducer instance
    """
    config = KafkaProducerConfig(**config_dict)
    return DataForgeKafkaProducer(config)