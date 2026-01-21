"""
Example script demonstrating advanced features of DataForge Kafka Producer.

This script showcases:
- Batch sending optimization
- Retry mechanism with exponential backoff
- Monitoring metrics
- Compression support
"""

import time
import json
from dataforge_ai.pipeline.kafka.producer import (
    DataForgeKafkaProducer,
    KafkaProducerConfig,
    create_kafka_producer
)


def demonstrate_batch_sending():
    """Demonstrate the batch sending feature."""
    print("=== Demonstrating Batch Sending ===")
    
    # Create producer configuration with advanced options
    config = KafkaProducerConfig(
        bootstrap_servers=["localhost:9092"],
        retries=3,
        retry_backoff_ms=200,
        compression_type="snappy",
        batch_size=16384,
        linger_ms=10,
        enable_metrics=True
    )
    
    # Create producer instance
    producer = DataForgeKafkaProducer(config)
    
    # Prepare batch of messages
    messages = [
        {"value": "Hello from batch message 1!", "key": "key1"},
        {"value": "Hello from batch message 2!", "key": "key2"},
        {"value": json.dumps({"event": "user_action", "userId": 123, "action": "click"}), "key": "event_key"},
        {"value": "Another batch message", "key": "key4"},
        {"value": "Final batch message", "key": "key5"}
    ]
    
    print(f"Sending {len(messages)} messages in batch...")
    
    # Send batch of messages
    start_time = time.time()
    result = producer.send_batch("test-topic", messages)
    duration = time.time() - start_time
    
    print(f"Batch send completed in {duration:.2f}s")
    print(f"Successful sends: {result['successful_sends']}")
    print(f"Failed sends: {result['failed_sends']}")
    print(f"Total messages: {result['total_messages']}")
    print(f"Duration: {result['duration_seconds']:.2f}s")
    
    # Clean up
    producer.close()
    print("Producer closed.\n")


def demonstrate_retry_mechanism():
    """Demonstrate the retry mechanism with exponential backoff."""
    print("=== Demonstrating Retry Mechanism ===")
    
    config = KafkaProducerConfig(
        bootstrap_servers=["localhost:9092"],
        retries=5,
        retry_backoff_ms=100,
        compression_type="gzip"
    )
    
    producer = DataForgeKafkaProducer(config)
    
    # Send messages individually to demonstrate retry logic
    print("Sending messages with potential retry...")
    
    success1 = producer.send_sync("test-topic", "Message with sync send", "sync-key")
    success2 = producer.send_async("test-topic", "Message with async send", "async-key")
    
    print(f"Sync send result: {success1}")
    print(f"Async send result: {success2}")
    
    # Clean up
    producer.close()
    print("Producer closed.\n")


def demonstrate_factory_function():
    """Demonstrate using the factory function."""
    print("=== Demonstrating Factory Function ===")
    
    config_dict = {
        "bootstrap_servers": ["localhost:9092"],
        "retries": 3,
        "retry_backoff_ms": 150,
        "compression_type": "lz4",
        "enable_metrics": True
    }
    
    # Create producer using factory function
    producer = create_kafka_producer(config_dict)
    
    print("Producer created using factory function")
    print(f"Bootstrap servers: {producer.config.bootstrap_servers}")
    print(f"Retries: {producer.config.retries}")
    print(f"Retry backoff: {producer.config.retry_backoff_ms}ms")
    print(f"Compression: {producer.config.compression_type}")
    
    # Clean up
    producer.close()
    print("Producer closed.\n")


def demonstrate_compression_and_metrics():
    """Demonstrate compression and metrics features."""
    print("=== Demonstrating Compression and Metrics ===")
    
    config = KafkaProducerConfig(
        bootstrap_servers=["localhost:9092"],
        compression_type="snappy",  # Using Snappy compression
        enable_metrics=True
    )
    
    producer = DataForgeKafkaProducer(config)
    
    # Send a larger message to see compression benefits
    large_message = {
        "timestamp": time.time(),
        "eventType": "large_payload",
        "data": "x" * 1000,  # Large payload to showcase compression
        "metadata": {
            "source": "demo_script",
            "version": "1.0",
            "compressed": True
        }
    }
    
    print("Sending message with compression enabled...")
    success = producer.send_sync("test-topic", large_message, "compressed-message")
    
    print(f"Send result: {success}")
    
    # Clean up
    producer.close()
    print("Producer closed.\n")


if __name__ == "__main__":
    print("DataForge Kafka Producer - Advanced Features Demo\n")
    
    # Note: In a real environment, make sure Kafka is running
    # This demo shows the usage patterns of the new features
    
    try:
        demonstrate_batch_sending()
        demonstrate_retry_mechanism()
        demonstrate_factory_function()
        demonstrate_compression_and_metrics()
        
        print("Demo completed! All advanced features demonstrated.")
        print("\nKey features added:")
        print("- Batch sending optimization: Send multiple messages efficiently")
        print("- Retry mechanism with exponential backoff: Automatic recovery from transient failures")
        print("- Monitoring metrics: Track latency and throughput")
        print("- Compression support: Reduce network bandwidth usage")
        
    except Exception as e:
        print(f"An error occurred during the demo: {e}")
        print("Note: This could be because Kafka is not running on localhost:9092")