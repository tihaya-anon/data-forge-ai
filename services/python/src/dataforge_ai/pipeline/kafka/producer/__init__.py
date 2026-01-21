"""
DataForge AI Kafka Producer Module

This package provides a high-level Kafka producer implementation with:
- Connection management and configuration
- Synchronous and asynchronous message sending
- Batch sending optimization
- Retry mechanism with exponential backoff
- Monitoring metrics (latency, throughput)
- Compression support

Main classes and functions:
- KafkaProducerConfig: Configuration model for the Kafka producer
- DataForgeKafkaProducer: Main Kafka producer class
- create_kafka_producer: Factory function to create producer instances
"""

from .producer import (
    KafkaProducerConfig,
    DataForgeKafkaProducer,
    create_kafka_producer
)

__all__ = [
    'KafkaProducerConfig',
    'DataForgeKafkaProducer',
    'create_kafka_producer'
]