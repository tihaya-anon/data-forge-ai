"""
Example demonstrating the usage of DataForge Kafka Producer.

This example shows how to:
1. Configure and create a Kafka producer
2. Send messages synchronously
3. Send messages asynchronously
4. Use context manager for resource management
"""

from dataforge_ai.pipeline.kafka.producer.producer import (
    DataForgeKafkaProducer,
    KafkaProducerConfig,
    create_kafka_producer
)


def delivery_callback(err, msg):
    """Callback function for async message delivery."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


def main():
    """Main example function."""
    print("DataForge Kafka Producer Example")
    print("=" * 40)

    # Method 1: Using explicit configuration
    print("\n1. Creating producer with explicit configuration...")
    config = KafkaProducerConfig(
        bootstrap_servers=["localhost:9092"],
        client_id="example-producer",
        retries=3,
        batch_size=16384,
        linger_ms=5
    )

    producer = DataForgeKafkaProducer(config)

    # Send a synchronous message
    print("\n2. Sending synchronous message...")
    success = producer.send_sync(
        topic="test-topic",
        value={"message": "Hello from DataForge Kafka Producer!", "timestamp": "2026-01-21"},
        key="example-key"
    )
    if success:
        print("✓ Synchronous message sent successfully!")
    else:
        print("✗ Failed to send synchronous message")

    # Send an asynchronous message
    print("\n3. Sending asynchronous message...")
    success = producer.send_async(
        topic="test-topic",
        value={"async_message": "Hello from async producer!", "timestamp": "2026-01-21"},
        key="async-example-key",
        callback=delivery_callback
    )
    if success:
        print("✓ Asynchronous message sent successfully!")
    else:
        print("✗ Failed to send asynchronous message")

    # Flush pending messages
    print("\n4. Flushing pending messages...")
    producer.flush()

    # Close the producer
    producer.close()
    print("✓ Producer closed")

    # Method 2: Using the factory function
    print("\n5. Using factory function...")
    config_dict = {
        "bootstrap_servers": ["localhost:9092"],
        "client_id": "factory-producer",
        "retries": 2,
        "compression_type": "snappy"
    }

    producer2 = create_kafka_producer(config_dict)
    success = producer2.send_sync(
        topic="test-topic",
        value={"via_factory": "Message sent via factory function!"},
        key="factory-key"
    )
    if success:
        print("✓ Message sent via factory function!")
    else:
        print("✗ Failed to send message via factory function")
    
    producer2.close()

    # Method 3: Using context manager (recommended approach)
    print("\n6. Using context manager (recommended)...")
    with DataForgeKafkaProducer(config) as producer3:
        success = producer3.send_sync(
            topic="test-topic",
            value={"via_context": "Message sent via context manager!"},
            key="context-key"
        )
        if success:
            print("✓ Message sent via context manager!")
        else:
            print("✗ Failed to send message via context manager")
        
        # Producer is automatically closed when exiting the context
        print("✓ Producer automatically closed via context manager")


if __name__ == "__main__":
    main()