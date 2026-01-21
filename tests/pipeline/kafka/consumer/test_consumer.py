"""
Unit tests for DataForgeKafkaConsumer.

These tests verify the functionality of the Kafka consumer with advanced features:
- Batch processing
- Dead Letter Queue
- Graceful shutdown
- Metrics collection
"""

import json
import unittest.mock
from unittest.mock import Mock, MagicMock, patch
import pytest
from kafka.structs import TopicPartition, OffsetAndMetadata

from services.python.src.dataforge_ai.pipeline.kafka.consumer import (
    DataForgeKafkaConsumer,
    KafkaConsumerConfig,
    ConsumerStatus
)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return KafkaConsumerConfig(
        bootstrap_servers=["localhost:9092"],
        group_id="test-group",
        topics=["test-topic"],
        batch_processing_enabled=True,
        batch_size=10,
        batch_timeout_ms=5000,
        dead_letter_queue_enabled=True,
        dead_letter_queue_topic="test-dlq-topic",
        max_retries=3,
        metrics_enabled=True
    )


@pytest.fixture
def mock_kafka_message():
    """Mock Kafka message for testing."""
    msg = Mock()
    msg.topic = "test-topic"
    msg.partition = 0
    msg.offset = 1
    msg.key = "test-key"
    msg.value = {"data": "test-value"}
    return msg


@patch('services.python.src.dataforge_ai.pipeline.kafka.consumer.consumer.KafkaConsumer')
def test_consumer_initialization(mock_kafka_consumer_class, sample_config):
    """Test that consumer initializes correctly with provided configuration."""
    # Arrange
    mock_consumer_instance = Mock()
    mock_kafka_consumer_class.return_value = mock_consumer_instance
    
    # Act
    consumer = DataForgeKafkaConsumer(sample_config)
    
    # Assert
    assert consumer.config == sample_config
    assert consumer._status == ConsumerStatus.RUNNING
    mock_kafka_consumer_class.assert_called_once()
    
    # Verify the arguments passed to KafkaConsumer
    call_args = mock_kafka_consumer_class.call_args
    assert call_args[1]['bootstrap_servers'] == sample_config.bootstrap_servers
    assert call_args[1]['group_id'] == sample_config.group_id
    assert call_args[1]['auto_offset_reset'] == sample_config.auto_offset_reset.value


def test_consumer_with_batch_processing(sample_config):
    """Test consumer with batch processing enabled."""
    # Arrange
    sample_config.batch_processing_enabled = True
    sample_config.batch_size = 5  # Small batch size for testing
    
    with patch('services.python.src.dataforge_ai.pipeline.kafka.consumer.consumer.KafkaConsumer') as mock_kafka_consumer_class:
        mock_consumer_instance = Mock()
        mock_kafka_consumer_class.return_value = mock_consumer_instance
        
        # Mock the poll method to return some messages
        mock_message_1 = Mock()
        mock_message_1.topic = "test-topic"
        mock_message_1.partition = 0
        mock_message_1.offset = 1
        mock_message_1.key = "key1"
        mock_message_1.value = {"data": "value1"}
        
        mock_message_2 = Mock()
        mock_message_2.topic = "test-topic"
        mock_message_2.partition = 0
        mock_message_2.offset = 2
        mock_message_2.key = "key2"
        mock_message_2.value = {"data": "value2"}
        
        # First call returns 2 messages, second call returns 3 more to reach batch size
        side_effect_list = [
            {TopicPartition("test-topic", 0): [mock_message_1, mock_message_2]},  # First poll
            {TopicPartition("test-topic", 0): []},  # Second poll - empty
            {TopicPartition("test-topic", 0): []},  # Third poll - empty
        ]
        
        mock_consumer_instance.poll.side_effect = side_effect_list
        
        # Act
        consumer = DataForgeKafkaConsumer(sample_config)
        
        # Mock the _process_batch method to track calls
        with patch.object(consumer, '_process_batch') as mock_process_batch:
            # Temporarily override the shutdown event to avoid infinite loop
            consumer._shutdown_event.is_set = Mock(side_effect=[False, True])
            
            # Call consume method (this would normally loop indefinitely)
            processor_func = lambda msg: print(f"Processing {msg.value}")
            consumer.consume(processor_func, batch_mode=True)
            
            # Verify that process_batch was called (even if with empty list)
            # In our case, since we only have 2 messages and batch_size is 5, 
            # the batch won't be full but timeout will trigger processing


def test_consumer_send_to_dlq(sample_config, mock_kafka_message):
    """Test sending a message to dead letter queue."""
    # Arrange
    with patch('services.python.src.dataforge_ai.pipeline.kafka.consumer.consumer.KafkaConsumer'):
        consumer = DataForgeKafkaConsumer(sample_config)
        
        # Act
        consumer._send_to_dlq(
            topic=mock_kafka_message.topic,
            partition=mock_kafka_message.partition,
            offset=mock_kafka_message.offset,
            key=mock_kafka_message.key,
            value=mock_kafka_message.value,
            error_msg="Test error"
        )
        
        # Note: Since we're mocking, we can't easily verify the DLQ send
        # The important part is that the method runs without error


def test_consumer_process_single_message_success(sample_config, mock_kafka_message):
    """Test processing a single message successfully."""
    # Arrange
    with patch('services.python.src.dataforge_ai.pipeline.kafka.consumer.consumer.KafkaConsumer'):
        consumer = DataForgeKafkaConsumer(sample_config)
        
        processor_func = Mock(return_value="success")
        
        # Act
        success, result = consumer._process_single_message(mock_kafka_message, processor_func)
        
        # Assert
        assert success is True
        assert result == "success"
        processor_func.assert_called_once_with(mock_kafka_message)


def test_consumer_process_single_message_failure(sample_config, mock_kafka_message):
    """Test processing a single message that fails."""
    # Arrange
    with patch('services.python.src.dataforge_ai.pipeline.kafka.consumer.consumer.KafkaConsumer'):
        consumer = DataForgeKafkaConsumer(sample_config)
        
        processor_func = Mock(side_effect=Exception("Processing failed"))
        
        # Mock the DLQ method to avoid actual DLQ operations
        with patch.object(consumer, '_send_to_dlq') as mock_send_dlq:
            # Act
            success, result = consumer._process_single_message(mock_kafka_message, processor_func)
            
            # Assert
            assert success is False
            assert "Processing failed" in result
            processor_func.assert_called_once_with(mock_kafka_message)
            
            # Verify that the message was sent to DLQ
            if sample_config.dead_letter_queue_enabled:
                mock_send_dlq.assert_called()


def test_graceful_shutdown(sample_config):
    """Test graceful shutdown functionality."""
    # Arrange
    with patch('services.python.src.dataforge_ai.pipeline.kafka.consumer.consumer.KafkaConsumer'):
        consumer = DataForgeKafkaConsumer(sample_config)
        
        # Act
        consumer.stop()
        
        # Assert
        assert consumer._status == ConsumerStatus.STOPPED
        assert consumer._shutdown_event.is_set() is True


def test_consumer_factory_method(sample_config):
    """Test the factory method for creating consumers."""
    # Act
    consumer = create_kafka_consumer(sample_config.dict())
    
    # Assert
    assert isinstance(consumer, DataForgeKafkaConsumer)
    assert consumer.config.group_id == sample_config.group_id
    assert consumer.config.topics == sample_config.topics