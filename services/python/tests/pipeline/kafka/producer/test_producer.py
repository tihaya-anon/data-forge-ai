"""
Unit tests for the DataForge Kafka Producer implementation.

Tests cover:
- Connection management and configuration
- Synchronous and asynchronous message sending
- Basic error handling
"""

import pytest
from unittest.mock import MagicMock, patch
from dataforge_ai.pipeline.kafka.producer.producer import (
    DataForgeKafkaProducer,
    KafkaProducerConfig,
    create_kafka_producer
)


class TestKafkaProducerConfig:
    """Test cases for KafkaProducerConfig model."""
    
    def test_default_config_values(self):
        """Test that default configuration values are set correctly."""
        config = KafkaProducerConfig()
        
        assert config.bootstrap_servers == ["localhost:9092"]
        assert config.acks == "all"
        assert config.retries == 3
        assert config.batch_size == 16384
        assert config.linger_ms == 5
        assert config.buffer_memory == 33554432
        assert config.compression_type == "snappy"
    
    def test_custom_config_values(self):
        """Test that custom configuration values are set correctly."""
        config = KafkaProducerConfig(
            bootstrap_servers=["server1:9092", "server2:9092"],
            client_id="test-client",
            acks=1,
            retries=5,
            compression_type="gzip"
        )
        
        assert config.bootstrap_servers == ["server1:9092", "server2:9092"]
        assert config.client_id == "test-client"
        assert config.acks == 1
        assert config.retries == 5
        assert config.compression_type == "gzip"


class TestDataForgeKafkaProducer:
    """Test cases for DataForgeKafkaProducer class."""
    
    @patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer')
    def test_producer_initialization_success(self, mock_kafka_producer):
        """Test that the producer initializes successfully with valid config."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])
        producer = DataForgeKafkaProducer(config)
        
        assert producer.config == config
        assert producer._producer == mock_producer_instance
        mock_kafka_producer.assert_called_once()
    
    @patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer')
    def test_send_sync_success(self, mock_kafka_producer):
        """Test synchronous message sending."""
        mock_producer_instance = MagicMock()
        mock_future = MagicMock()
        mock_future.get.return_value = MagicMock(
            topic='test-topic',
            partition=0,
            offset=1
        )
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])
        producer = DataForgeKafkaProducer(config)
        
        result = producer.send_sync('test-topic', 'test-value', 'test-key')
        
        assert result is True
        mock_producer_instance.send.assert_called_once_with(
            'test-topic', value='test-value', key='test-key'
        )
    
    @patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer')
    def test_send_sync_timeout_error(self, mock_kafka_producer):
        """Test synchronous message sending with timeout."""
        from kafka.errors import KafkaTimeoutError
        
        mock_producer_instance = MagicMock()
        mock_future = MagicMock()
        mock_future.get.side_effect = KafkaTimeoutError("Timeout")
        mock_producer_instance.send.return_value = mock_future
        mock_kafka_producer.return_value = mock_producer_instance
        
        config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])
        producer = DataForgeKafkaProducer(config)
        
        result = producer.send_sync('test-topic', 'test-value', 'test-key')
        
        assert result is False
    
    @patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer')
    def test_send_async_success(self, mock_kafka_producer):
        """Test asynchronous message sending."""
        mock_producer_instance = MagicMock()
        mock_producer_instance.send.return_value = None
        mock_kafka_producer.return_value = mock_producer_instance
        
        config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])
        producer = DataForgeKafkaProducer(config)
        
        result = producer.send_async('test-topic', 'test-value', 'test-key')
        
        assert result is True
        mock_producer_instance.send.assert_called_once_with(
            'test-topic', value='test-value', key='test-key', callback=None
        )
    
    @patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer')
    def test_send_async_with_callback(self, mock_kafka_producer):
        """Test asynchronous message sending with callback."""
        mock_producer_instance = MagicMock()
        mock_producer_instance.send.return_value = None
        mock_kafka_producer.return_value = mock_producer_instance
        
        config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])
        producer = DataForgeKafkaProducer(config)
        
        callback = MagicMock()
        result = producer.send_async('test-topic', 'test-value', 'test-key', callback=callback)
        
        assert result is True
        mock_producer_instance.send.assert_called_once_with(
            'test-topic', value='test-value', key='test-key', callback=callback
        )
    
    @patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer')
    def test_flush_method(self, mock_kafka_producer):
        """Test flush method."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])
        producer = DataForgeKafkaProducer(config)
        
        producer.flush()
        
        mock_producer_instance.flush.assert_called_once()
    
    @patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer')
    def test_close_method(self, mock_kafka_producer):
        """Test close method."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])
        producer = DataForgeKafkaProducer(config)
        
        producer.close()
        
        mock_producer_instance.close.assert_called_once()
    
    def test_context_manager(self):
        """Test context manager functionality."""
        config = KafkaProducerConfig(bootstrap_servers=["localhost:9092"])
        
        with patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer') as mock_kafka_producer:
            mock_producer_instance = MagicMock()
            mock_kafka_producer.return_value = mock_producer_instance
            
            with DataForgeKafkaProducer(config) as producer:
                assert producer._producer is mock_producer_instance
            
            mock_producer_instance.close.assert_called_once()


class TestCreateKafkaProducer:
    """Test cases for the factory function."""
    
    @patch('dataforge_ai.pipeline.kafka.producer.producer.DataForgeKafkaProducer')
    @patch('dataforge_ai.pipeline.kafka.producer.producer.KafkaProducer')
    def test_create_kafka_producer_factory(self, mock_kafka_producer, mock_dataforge_producer):
        """Test the factory function creates a producer correctly."""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance
        mock_dataforge_producer.return_value = MagicMock()
        
        config_dict = {
            "bootstrap_servers": ["localhost:9092"],
            "client_id": "test-factory-client"
        }
        
        producer = create_kafka_producer(config_dict)
        
        # Verify that KafkaProducerConfig was created with the right params
        # and DataForgeKafkaProducer was instantiated
        assert mock_dataforge_producer.called