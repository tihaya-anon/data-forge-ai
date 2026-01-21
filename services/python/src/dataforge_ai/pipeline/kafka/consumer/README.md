# DataForge AI Kafka Consumer

This module provides a robust Kafka consumer implementation with advanced features designed for enterprise use cases in the DataForge AI platform.

## Features

- **Batch Processing**: Efficiently process messages in batches to improve throughput
- **Dead Letter Queue (DLQ)**: Automatically route failed messages to a separate topic for later inspection
- **Graceful Shutdown**: Properly handle termination signals to ensure no message loss
- **Metrics Collection**: Built-in support for Prometheus metrics to monitor consumer performance

## Installation

This module is part of the DataForge AI services package. Ensure you have installed the required dependencies as specified in the main `pyproject.toml`.

## Usage

### Basic Usage

```python
from dataforge_ai.pipeline.kafka.consumer import DataForgeKafkaConsumer, KafkaConsumerConfig

# Define consumer configuration
config = KafkaConsumerConfig(
    bootstrap_servers=["localhost:9092"],
    group_id="my-consumer-group",
    topics=["input-topic"],
    auto_offset_reset="earliest"
)

# Create and use the consumer
with DataForgeKafkaConsumer(config) as consumer:
    def process_message(message):
        print(f"Processing message: {message.value}")
        # Your processing logic here
    
    consumer.consume(process_message)
```

### With Batch Processing

```python
from dataforge_ai.pipeline.kafka.consumer import DataForgeKafkaConsumer, KafkaConsumerConfig

config = KafkaConsumerConfig(
    bootstrap_servers=["localhost:9092"],
    group_id="my-batch-consumer-group",
    topics=["input-topic"],
    batch_processing_enabled=True,
    batch_size=100,  # Process up to 100 messages per batch
    batch_timeout_ms=5000  # Max wait time for batch to fill
)

with DataForgeKafkaConsumer(config) as consumer:
    def process_batch(messages):
        for message in messages:
            print(f"Processing message: {message.value}")
        # Process all messages in the batch
    
    consumer.consume(process_batch, batch_mode=True)
```

### With Dead Letter Queue

```python
from dataforge_ai.pipeline.kafka.consumer import DataForgeKafkaConsumer, KafkaConsumerConfig

config = KafkaConsumerConfig(
    bootstrap_servers=["localhost:9092"],
    group_id="my-dlq-consumer-group",
    topics=["input-topic"],
    dead_letter_queue_enabled=True,
    dead_letter_queue_topic="my-dlq-topic",
    max_retries=3
)

with DataForgeKafkaConsumer(config) as consumer:
    def process_message(message):
        # If this raises an exception, the message will be sent to the DLQ
        if some_error_condition:
            raise ValueError("Something went wrong")
        print(f"Successfully processed: {message.value}")
    
    consumer.consume(process_message)
```

### With Metrics Collection

```python
from dataforge_ai.pipeline.kafka.consumer import DataForgeKafkaConsumer, KafkaConsumerConfig

config = KafkaConsumerConfig(
    bootstrap_servers=["localhost:9092"],
    group_id="my-metrics-consumer-group",
    topics=["input-topic"],
    metrics_enabled=True,
    metrics_prefix="myapp.kafka.consumer"
)

with DataForgeKafkaConsumer(config) as consumer:
    def process_message(message):
        print(f"Processing: {message.value}")
    
    consumer.consume(process_message)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bootstrap_servers` | `Union[str, List[str]]` | `["localhost:9092"]` | Kafka broker addresses |
| `group_id` | `str` | - | Consumer group identifier |
| `topics` | `List[str]` | `[]` | Topics to subscribe to |
| `auto_offset_reset` | `str` | `"earliest"` | Initial offset reset strategy |
| `enable_auto_commit` | `bool` | `True` | Whether to auto-commit offsets |
| `max_poll_records` | `int` | `100` | Max records to return per poll |
| `batch_processing_enabled` | `bool` | `False` | Enable batch processing mode |
| `batch_size` | `int` | `100` | Max messages per batch |
| `batch_timeout_ms` | `int` | `5000` | Max wait time for batch to fill |
| `dead_letter_queue_enabled` | `bool` | `False` | Enable dead letter queue |
| `dead_letter_queue_topic` | `str` | `None` | Topic for failed messages |
| `max_retries` | `int` | `3` | Max retries before sending to DLQ |
| `metrics_enabled` | `bool` | `False` | Enable Prometheus metrics |
| `metrics_prefix` | `str` | `"dataforge.kafka.consumer"` | Prefix for metric names |

## Metrics

When metrics are enabled, the following metrics are available:

- `dataforge.kafka.consumer_messages_consumed_total` - Total messages consumed
- `dataforge.kafka.consumer_messages_failed_total` - Total messages that failed processing
- `dataforge.kafka.consumer_messages_dlq_total` - Total messages sent to dead letter queue
- `dataforge.kafka.consumer_batches_processed_total` - Total batches processed
- `dataforge.kafka.consumer_message_process_duration_seconds` - Time spent processing individual messages
- `dataforge.kafka.consumer_batch_process_duration_seconds` - Time spent processing batches
- `dataforge.kafka.consumer_active_consumers` - Number of active consumers

## Error Handling

The consumer includes comprehensive error handling:

- Failed message processing can be automatically routed to a dead letter queue
- Retry mechanisms with configurable limits
- Proper resource cleanup during shutdown
- Detailed logging for debugging

## Contributing

Please follow the general project contribution guidelines. For Kafka consumer-specific changes, ensure all tests pass and metrics continue to work as expected.

## License

This project is licensed under the terms specified in the main repository.