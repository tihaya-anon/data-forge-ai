"""
Kafka Consumer implementation for DataForge AI with advanced features.

This module provides a wrapper around kafka-python's KafkaConsumer with:
- Batch processing capabilities
- Dead Letter Queue support
- Graceful shutdown handling
- Metrics collection
"""

import asyncio
import json
import logging
import signal
import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from kafka import KafkaConsumer
from kafka.structs import TopicPartition, OffsetAndMetadata
from prometheus_client import Counter, Histogram, Gauge

from . import KafkaConsumerConfig, ConsumerStatus
from ...common.metrics.prometheus import get_metrics_collector


logger = logging.getLogger(__name__)


class DataForgeKafkaConsumer:
    """
    A Kafka consumer wrapper for DataForge AI with advanced features:
    - Batch processing of messages
    - Dead letter queue for failed messages
    - Graceful shutdown handling
    - Metrics collection
    """

    def __init__(self, config: KafkaConsumerConfig):
        """
        Initialize the Kafka consumer with the given configuration.
        
        Args:
            config: Configuration object for the Kafka consumer
        """
        self.config = config
        self._consumer: Optional[KafkaConsumer] = None
        self._status = ConsumerStatus.INITIALIZING
        self._shutdown_event = threading.Event()
        self._processing_thread: Optional[threading.Thread] = None
        self._batch_buffer = []
        self._dlq_producer = None
        
        # Initialize metrics if enabled
        if config.metrics_enabled:
            self._setup_metrics()
        
        # Set up deserializers
        key_deserializer = lambda x: x.decode('utf-8') if x else None
        value_deserializer = lambda x: json.loads(x.decode('utf-8')) if x else None

        try:
            self._consumer = KafkaConsumer(
                bootstrap_servers=config.bootstrap_servers,
                group_id=config.group_id,
                auto_offset_reset=config.auto_offset_reset.value,
                enable_auto_commit=config.enable_auto_commit,
                auto_commit_interval_ms=config.auto_commit_interval_ms,
                client_id=config.client_id,
                max_poll_records=config.max_poll_records,
                max_poll_interval_ms=config.max_poll_interval_ms,
                session_timeout_ms=config.session_timeout_ms,
                heartbeat_interval_ms=config.heartbeat_interval_ms,
                isolation_level=config.isolation_level.value,
                key_deserializer=key_deserializer,
                value_deserializer=value_deserializer
            )
            
            # Subscribe to topics
            if config.topics:
                self._consumer.subscribe(topics=config.topics)
                logger.info(f"Kafka consumer subscribed to topics: {config.topics}")
            
            self._status = ConsumerStatus.RUNNING
            logger.info(f"Kafka consumer initialized successfully with group {config.group_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {str(e)}")
            raise
    
    def _setup_metrics(self):
        """Initialize Prometheus metrics collectors."""
        prefix = self.config.metrics_prefix
        
        # Counters
        self.messages_consumed_counter = Counter(
            f"{prefix}_messages_consumed_total",
            "Total number of consumed messages",
            ["topic", "group"]
        )
        
        self.messages_failed_counter = Counter(
            f"{prefix}_messages_failed_total",
            "Total number of failed messages",
            ["topic", "group"]
        )
        
        self.messages_dlq_counter = Counter(
            f"{prefix}_messages_dlq_total",
            "Total number of messages sent to dead letter queue",
            ["topic", "group"]
        )
        
        self.batch_processed_counter = Counter(
            f"{prefix}_batches_processed_total",
            "Total number of batches processed",
            ["topic", "group"]
        )
        
        # Histograms
        self.message_process_duration_histogram = Histogram(
            f"{prefix}_message_process_duration_seconds",
            "Time spent processing messages",
            ["topic", "group"]
        )
        
        self.batch_process_duration_histogram = Histogram(
            f"{prefix}_batch_process_duration_seconds",
            "Time spent processing batches",
            ["topic", "group"]
        )
        
        # Gauges
        self.active_consumers_gauge = Gauge(
            f"{prefix}_active_consumers",
            "Number of active consumers",
            ["group"]
        )
        self.active_consumers_gauge.inc()

    def _send_to_dlq(self, topic: str, partition: int, offset: int, key: Any, value: Any, error_msg: str):
        """Send a failed message to the dead letter queue."""
        if not self.config.dead_letter_queue_enabled or not self.config.dead_letter_queue_topic:
            logger.warning(f"No DLQ configured, dropping failed message from {topic}[{partition}:{offset}]")
            return

        dlq_message = {
            "original_topic": topic,
            "partition": partition,
            "offset": offset,
            "key": key,
            "value": value,
            "error": error_msg,
            "timestamp": datetime.utcnow().isoformat(),
            "retry_count": self._get_retry_count(value)
        }

        try:
            # We would typically use a producer to send to the DLQ topic
            # For now, log the event
            logger.error(f"Sending message to DLQ: {dlq_message}")
            if hasattr(self, 'messages_dlq_counter'):
                self.messages_dlq_counter.labels(
                    topic=self.config.dead_letter_queue_topic,
                    group=self.config.group_id
                ).inc()
        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {str(e)}")

    def _get_retry_count(self, value: Any) -> int:
        """Extract retry count from message headers or value."""
        if isinstance(value, dict) and "_retry_count" in value:
            return value["_retry_count"] + 1
        return 1

    def _process_single_message(self, msg, processor_func: Callable):
        """Process a single message with error handling."""
        start_time = time.time()
        try:
            result = processor_func(msg)
            if hasattr(self, 'message_process_duration_histogram'):
                self.message_process_duration_histogram.labels(
                    topic=msg.topic,
                    group=self.config.group_id
                ).observe(time.time() - start_time)
            
            if hasattr(self, 'messages_consumed_counter'):
                self.messages_consumed_counter.labels(
                    topic=msg.topic,
                    group=self.config.group_id
                ).inc()
                
            return True, result
        except Exception as e:
            logger.error(f"Error processing message from {msg.topic}[{msg.partition}:{msg.offset}]: {str(e)}")
            
            if hasattr(self, 'messages_failed_counter'):
                self.messages_failed_counter.labels(
                    topic=msg.topic,
                    group=self.config.group_id
                ).inc()
            
            # Send to DLQ if enabled
            if self.config.dead_letter_queue_enabled:
                self._send_to_dlq(
                    topic=msg.topic,
                    partition=msg.partition,
                    offset=msg.offset,
                    key=msg.key,
                    value=msg.value,
                    error_msg=str(e)
                )
            
            return False, str(e)

    def _process_batch(self, batch: List, processor_func: Callable):
        """Process a batch of messages."""
        if not batch:
            return

        start_time = time.time()
        logger.info(f"Processing batch of {len(batch)} messages")
        
        for msg in batch:
            self._process_single_message(msg, processor_func)
        
        if hasattr(self, 'batch_process_duration_histogram'):
            self.batch_process_duration_histogram.labels(
                topic=batch[0].topic if batch else "unknown",
                group=self.config.group_id
            ).observe(time.time() - start_time)
        
        if hasattr(self, 'batch_processed_counter'):
            # Increment by number of batches processed (not messages)
            self.batch_processed_counter.labels(
                topic=batch[0].topic if batch else "unknown",
                group=self.config.group_id
            ).inc()

    def consume(self, processor_func: Callable, batch_mode: bool = None):
        """
        Start consuming messages and process them with the provided function.
        
        Args:
            processor_func: Function to process each message
            batch_mode: Whether to use batch mode (overrides config if specified)
        """
        if self._consumer is None:
            raise RuntimeError("Consumer not initialized")
        
        use_batch_mode = batch_mode if batch_mode is not None else self.config.batch_processing_enabled
        
        logger.info(f"Starting consumption in {'batch' if use_batch_mode else 'single'} mode")
        
        try:
            while not self._shutdown_event.is_set():
                if use_batch_mode:
                    # Batch processing mode
                    batch = []
                    batch_start_time = time.time()
                    
                    # Collect messages for batch
                    while len(batch) < self.config.batch_size and \
                          (time.time() - batch_start_time) * 1000 < self.config.batch_timeout_ms and \
                          not self._shutdown_event.is_set():
                        
                        # Poll for messages with short timeout to allow checking shutdown event
                        polled_msgs = self._consumer.poll(timeout_ms=1000)
                        
                        for topic_partition, messages in polled_msgs.items():
                            for msg in messages:
                                batch.append(msg)
                                if len(batch) >= self.config.batch_size:
                                    break
                            if len(batch) >= self.config.batch_size:
                                break
                
                    # Process the collected batch
                    if batch:
                        self._process_batch(batch, processor_func)
                        
                else:
                    # Single message processing mode
                    polled_msgs = self._consumer.poll(timeout_ms=1000)
                    
                    for topic_partition, messages in polled_msgs.items():
                        for msg in messages:
                            if self._shutdown_event.is_set():
                                break
                            self._process_single_message(msg, processor_func)
                            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down gracefully...")
        except Exception as e:
            logger.error(f"Error during consumption: {str(e)}")
        finally:
            self.stop()

    def stop(self):
        """Stop the consumer and perform cleanup."""
        logger.info("Stopping Kafka consumer...")
        self._status = ConsumerStatus.STOPPING
        self._shutdown_event.set()
        
        if self._consumer:
            self._consumer.close()
            logger.info("Kafka consumer closed")
        
        # Update metrics
        if hasattr(self, 'active_consumers_gauge'):
            self.active_consumers_gauge.dec()
        
        self._status = ConsumerStatus.STOPPED
        logger.info("Kafka consumer stopped")

    def graceful_shutdown(self, signum, frame):
        """Handle graceful shutdown when receiving termination signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()

    def __enter__(self):
        """Context manager entry."""
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def create_kafka_consumer(config_dict: Dict[str, Any]) -> DataForgeKafkaConsumer:
    """
    Factory function to create a Kafka consumer instance from a dictionary configuration.
    
    Args:
        config_dict: Dictionary containing consumer configuration
        
    Returns:
        DataForgeKafkaConsumer instance
    """
    config = KafkaConsumerConfig(**config_dict)
    return DataForgeKafkaConsumer(config)