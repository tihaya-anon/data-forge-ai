# Kafka Producer Module

This module provides a robust and easy-to-use Kafka producer implementation for the DataForge AI platform. It includes connection management, support for both synchronous and asynchronous message sending, and comprehensive error handling.

## Features

- **Connection Management**: Automatic handling of Kafka broker connections with configurable parameters
- **Sync/Async Sending**: Support for both synchronous (with confirmation) and asynchronous message publishing
- **Error Handling**: Comprehensive error handling for various failure scenarios
- **Configuration**: Pydantic-based configuration with validation and type safety
- **Context Manager**: Supports use with `with` statement for automatic resource cleanup

## Usage

### Basic Usage

```python
from src.pipeline.kafka.producer.producer import DataForgeKafkaProducer, KafkaProducerConfig

# Create configuration
config = KafkaProducerConfig(
    bootstrap_servers=["localhost:9092"],
    client_id="my-producer",
    retries=3
)

# Create producer instance
producer = DataForgeKafkaProducer(config)

# Synchronous message sending
success = producer.send_sync("my-topic", {"message": "Hello Kafka!"})
if success:
    print("Message sent successfully!")

# Asynchronous message sending
def delivery_callback(err, msg):
    if err:
        print(f"Message failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

producer.send_async("my-topic", {"async_message": "Hello Async!"}, callback=delivery_callback)

# Clean up
producer.close()
```

### Using Context Manager

```python
from src.pipeline.kafka.producer.producer import DataForgeKafkaProducer, KafkaProducerConfig

config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])

with DataForgeKafkaProducer(config) as producer:
    success = producer.send_sync("my-topic", {"message": "Hello Kafka!"})
    if success:
        print("Message sent successfully!")
    # Producer automatically closes when exiting the context
```

### Using Factory Function

```python
from src.pipeline.kafka.producer.producer import create_kafka_producer

config_dict = {
    "bootstrap_servers": ["localhost:9092"],
    "client_id": "factory-producer",
    "compression_type": "snappy"
}

producer = create_kafka_producer(config_dict)
success = producer.send_sync("my-topic", {"message": "Created via factory!"})
producer.close()
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| bootstrap_servers | str or list | `["localhost:9092"]` | List of Kafka bootstrap servers |
| client_id | str | `None` | Client identifier for tracking requests |
| acks | str or int | `"all"` | Number of acknowledgments required |
| retries | int | 3 | Number of retry attempts |
| batch_size | int | 16384 | Batch size in bytes |
| linger_ms | int | 5 | Time to linger before sending batches |
| buffer_memory | int | 33554432 | Total memory for buffering |
| compression_type | str | `"snappy"` | Compression algorithm to use |

## Error Handling

The producer handles several types of errors:

- **KafkaTimeoutError**: Occurs when operations take longer than the configured timeout
- **KafkaError**: General Kafka-related errors
- **NoBrokersAvailable**: Raised during initialization when no Kafka brokers are available
- **Generic Exceptions**: Other unexpected errors

Both sync and async sending methods handle these errors appropriately and log them for debugging purposes.

## Testing

To run the unit tests:

```bash
cd services/python
uv run pytest tests/pipeline/kafka/producer/test_producer.py -v
```

The tests cover all major functionality including initialization, sync/async sending, error conditions, and resource cleanup.