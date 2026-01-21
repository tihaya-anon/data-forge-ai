"""
Kafka Producer implementation for DataForge AI.

This module provides a wrapper around kafka-python's KafkaProducer with:
- Connection management and configuration
- Synchronous and asynchronous message sending
- Batch sending optimization
- Retry mechanism with exponential backoff
- Monitoring metrics (latency, throughput)
- Compression support
"""

import json
import logging
import time
from typing import Any, Dict, Optional, Union, Callable, List
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError, NoBrokersAvailable
from pydantic import BaseModel, Field

# Try to import metrics collectors, but make them optional
try:
    from dataforge_ai.common.metrics.interface import MetricsCollector
    from dataforge_ai.common.metrics.prometheus import PrometheusMetricsCollector
    METRICS_AVAILABLE = True
except ImportError:
    logging.warning("Metrics libraries not available. Continuing without metrics support.")
    MetricsCollector = None
    PrometheusMetricsCollector = None
    METRICS_AVAILABLE = False


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
    retry_backoff_ms: int = Field(default=100, description="Retry backoff in milliseconds")
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
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")


class NoOpMetricsCollector:
    """A no-op metrics collector to use when metrics are disabled or unavailable."""
    
    def record_latency(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a latency measurement."""
        pass
    
    def increment_counter(self, metric_name: str, labels: Dict[str, str] = None, value: float = 1.0):
        """Increment a counter."""
        pass


class DataForgeKafkaProducer:
    """
    A Kafka producer wrapper for DataForge AI with connection management,
    synchronous/asynchronous sending capabilities, batch optimization,
    retry mechanism with exponential backoff, monitoring metrics, and compression support.
    """
    
    def __init__(self, config: KafkaProducerConfig, metrics_collector: Optional['MetricsCollector'] = None):
        """
        Initialize the Kafka producer with the given configuration.
        
        Args:
            config: Configuration object for the Kafka producer
            metrics_collector: Optional metrics collector for monitoring
        """
        self.config = config
        self._producer: Optional[KafkaProducer] = None
        
        # Setup metrics collector
        if config.enable_metrics and METRICS_AVAILABLE and metrics_collector is None:
            try:
                self._metrics_collector = PrometheusMetricsCollector()
            except RuntimeError:
                # If Prometheus is not available, log warning and continue without metrics
                logger.warning("Prometheus metrics not available. Continuing without metrics support.")
                self._metrics_collector = NoOpMetricsCollector()
        elif metrics_collector:
            self._metrics_collector = metrics_collector
        else:
            self._metrics_collector = NoOpMetricsCollector()
        
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
                retry_backoff_ms=config.retry_backoff_ms,
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
        start_time = time.time()
        success = False
        
        try:
            # Send message synchronously by waiting for the future
            future = self._producer.send(topic, value=value, key=key)
            record_metadata = future.get(timeout=10)  # Wait up to 10 seconds
            
            logger.debug(
                f"Message sent successfully to topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, offset={record_metadata.offset}"
            )
            success = True
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
        finally:
            # Record metrics
            duration = time.time() - start_time
            if self._metrics_collector and success:
                self._metrics_collector.record_latency("kafka_producer_send_duration", duration, {"topic": topic})
                self._metrics_collector.increment_counter("kafka_producer_messages_sent_total", {"topic": topic})
    
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
        start_time = time.time()
        
        try:
            self._producer.send(topic, value=value, key=key, callback=callback)
            logger.debug(f"Asynchronous message sent to topic '{topic}'")
            
            # Record metrics
            duration = time.time() - start_time
            if self._metrics_collector:
                self._metrics_collector.record_latency("kafka_producer_send_duration", duration, {"topic": topic})
                self._metrics_collector.increment_counter("kafka_producer_messages_sent_total", {"topic": topic})
            
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error while sending message to topic '{topic}': {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending message to topic '{topic}': {str(e)}")
            return False

    def send_batch(self, topic: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send a batch of messages to Kafka with retry mechanism.
        
        Args:
            topic: Topic name to send the messages to
            messages: List of message dictionaries with 'value' and optional 'key'
            
        Returns:
            Dictionary with success count, failure count, and total duration
        """
        start_time = time.time()
        successful_sends = 0
        failed_sends = 0
        
        for i, msg in enumerate(messages):
            value = msg.get('value')
            key = msg.get('key')
            
            # Apply exponential backoff for retries
            success = False
            attempt = 0
            backoff_time = self.config.retry_backoff_ms / 1000.0  # Convert to seconds
            
            while attempt <= self.config.retries and not success:
                try:
                    future = self._producer.send(topic, value=value, key=key)
                    record_metadata = future.get(timeout=10)
                    
                    logger.debug(
                        f"Message {i} sent successfully to topic={record_metadata.topic}, "
                        f"partition={record_metadata.partition}, offset={record_metadata.offset}"
                    )
                    success = True
                    successful_sends += 1
                except KafkaTimeoutError:
                    logger.warning(f"Attempt {attempt+1} failed for message {i} due to timeout")
                    if attempt < self.config.retries:
                        time.sleep(backoff_time)
                        # Exponential backoff: double the wait time after each failure
                        backoff_time *= 2
                    attempt += 1
                except KafkaError as e:
                    logger.error(f"Kafka error for message {i}: {str(e)}")
                    if attempt < self.config.retries:
                        time.sleep(backoff_time)
                        backoff_time *= 2
                    attempt += 1
                except Exception as e:
                    logger.error(f"Unexpected error for message {i}: {str(e)}")
                    break  # Don't retry on unexpected errors
            
            if not success:
                logger.error(f"All retry attempts failed for message {i}")
                failed_sends += 1
        
        duration = time.time() - start_time
        
        # Record batch metrics
        if self._metrics_collector:
            self._metrics_collector.record_latency("kafka_producer_batch_send_duration", duration, {
                "topic": topic, 
                "message_count": str(len(messages))
            })
            self._metrics_collector.increment_counter("kafka_producer_batches_sent_total", {"topic": topic})
            self._metrics_collector.increment_counter("kafka_producer_messages_sent_total", {
                "topic": topic
            }, successful_sends)
            self._metrics_collector.increment_counter("kafka_producer_messages_failed_total", {
                "topic": topic
            }, failed_sends)
        
        return {
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "total_messages": len(messages),
            "duration_seconds": duration
        }

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


def create_kafka_producer(config_dict: Dict[str, Any], metrics_collector: Optional['MetricsCollector'] = None) -> DataForgeKafkaProducer:
    """
    Factory function to create a Kafka producer instance from a dictionary configuration.
    
    Args:
        config_dict: Dictionary containing producer configuration
        metrics_collector: Optional metrics collector for monitoring
        
    Returns:
        DataForgeKafkaProducer instance
    """
    config = KafkaProducerConfig(**config_dict)
    return DataForgeKafkaProducer(config, metrics_collector)