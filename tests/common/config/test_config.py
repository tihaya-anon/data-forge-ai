import os
import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch

from src.common.config import (
    DataForgeConfig,
    ConfigManager,
    get_config,
    KafkaConfig,
    StorageConfig,
    RedisConfig,
    MilvusConfig,
    ElasticsearchConfig
)


def test_default_config_creation():
    """Test creating a default configuration"""
    config = DataForgeConfig()
    assert config.env == "development"
    assert config.debug is True
    assert config.kafka.bootstrap_servers == "localhost:9092"
    assert config.storage.minio_endpoint == "localhost:9000"


def test_kafka_config_model():
    """Test Kafka configuration model"""
    kafka_config = KafkaConfig(
        bootstrap_servers="test-server:9092",
        topic_prefix="test-prefix"
    )
    assert kafka_config.bootstrap_servers == "test-server:9092"
    assert kafka_config.topic_prefix == "test-prefix"


def test_storage_config_model():
    """Test Storage configuration model"""
    storage_config = StorageConfig(
        minio_endpoint="test-minio:9000",
        minio_access_key="test-key",
        minio_secret_key="test-secret"
    )
    assert storage_config.minio_endpoint == "test-minio:9000"
    assert storage_config.minio_access_key == "test-key"
    assert storage_config.minio_secret_key == "test-secret"


def test_redis_config_model():
    """Test Redis configuration model"""
    redis_config = RedisConfig(host="test-redis", port=6380)
    assert redis_config.host == "test-redis"
    assert redis_config.port == 6380


def test_milvus_config_model():
    """Test Milvus configuration model"""
    milvus_config = MilvusConfig(host="test-milvus", port=19531)
    assert milvus_config.host == "test-milvus"
    assert milvus_config.port == 19531


def test_elasticsearch_config_model():
    """Test Elasticsearch configuration model"""
    es_config = ElasticsearchConfig(host="test-es", port=9201)
    assert es_config.host == "test-es"
    assert es_config.port == 9201


def test_config_from_dict():
    """Test creating configuration from a dictionary"""
    config_data = {
        "env": "production",
        "debug": False,
        "kafka": {
            "bootstrap_servers": "prod-kafka:9092",
            "topic_prefix": "prod-topic"
        },
        "storage": {
            "minio_endpoint": "prod-minio:9000",
            "minio_access_key": "prod-key",
            "minio_secret_key": "prod-secret"
        }
    }
    
    config = DataForgeConfig(**config_data)
    assert config.env == "production"
    assert config.debug is False
    assert config.kafka.bootstrap_servers == "prod-kafka:9092"
    assert config.storage.minio_endpoint == "prod-minio:9000"


@patch.dict(os.environ, {
    "ENVIRONMENT": "test",
    "DEBUG": "false",
    "KAFKA_BOOTSTRAP_SERVERS": "env-test-kafka:9092",
    "REDIS_HOST": "env-test-redis",
    "MILVUS_PORT": "19532"
})
def test_environment_variable_override():
    """Test that environment variables override config values"""
    temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_config_file.write("""
env: development
debug: true
kafka:
  bootstrap_servers: localhost:9092
  topic_prefix: dataforge
redis:
  host: localhost
  port: 6379
milvus:
  host: localhost
  port: 19530
""")
    temp_config_file.close()
    
    config_manager = ConfigManager(config_path=temp_config_file.name)
    config = config_manager.load_config()
    
    # Check that environment variables took precedence
    assert config.env == "test"
    assert config.debug is False
    assert config.kafka.bootstrap_servers == "env-test-kafka:9092"
    assert config.redis.host == "env-test-redis"
    assert config.milvus.port == 19532
    
    # Clean up
    Path(temp_config_file.name).unlink()


def test_config_manager_with_custom_path():
    """Test ConfigManager with a custom config path"""
    temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_config_file.write("""
env: custom
debug: false
kafka:
  bootstrap_servers: custom-kafka:9092
  topic_prefix: custom-topic
""")
    temp_config_file.close()
    
    config_manager = ConfigManager(config_path=temp_config_file.name)
    config = config_manager.load_config()
    
    assert config.env == "custom"
    assert config.debug is False
    assert config.kafka.bootstrap_servers == "custom-kafka:9092"
    
    # Clean up
    Path(temp_config_file.name).unlink()


def test_global_config_instance():
    """Test getting config from global instance"""
    config = get_config()
    assert isinstance(config, DataForgeConfig)
    assert hasattr(config, 'env')
    assert hasattr(config, 'kafka')
    assert hasattr(config, 'storage')


def test_reload_config():
    """Test reloading configuration"""
    temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_config_file.write("""
env: initial
debug: true
""")
    temp_config_file.close()
    
    config_manager = ConfigManager(config_path=temp_config_file.name)
    
    # Initial load
    config = config_manager.config
    assert config.env == "initial"
    
    # Update the file
    with open(temp_config_file.name, 'w') as f:
        f.write("""
env: updated
debug: false
""")
    
    # Reload
    reloaded_config = config_manager.reload()
    assert reloaded_config.env == "updated"
    assert reloaded_config.debug is False
    
    # Clean up
    Path(temp_config_file.name).unlink()


def test_invalid_config_raises_error():
    """Test that invalid config raises an error"""
    temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml')
    temp_config_file.write("""
env: development
debug: not_a_boolean
""")
    temp_config_file.close()
    
    config_manager = ConfigManager(config_path=temp_config_file.name)
    
    with pytest.raises(ValueError, match="Invalid configuration"):
        config_manager.load_config()
    
    # Clean up
    Path(temp_config_file.name).unlink()