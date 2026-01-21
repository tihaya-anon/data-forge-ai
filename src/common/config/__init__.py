from typing import Optional, Dict, Any
import os
import yaml
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError


class KafkaConfig(BaseModel):
    """Kafka configuration settings"""
    bootstrap_servers: str = Field(default="localhost:9092", description="Kafka bootstrap servers")
    topic_prefix: str = Field(default="dataforge", description="Kafka topic prefix")


class StorageConfig(BaseModel):
    """Storage configuration settings"""
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO endpoint")
    minio_access_key: str = Field(default="minioadmin", description="MinIO access key")
    minio_secret_key: str = Field(default="minioadmin123", description="MinIO secret key")


class RedisConfig(BaseModel):
    """Redis configuration settings"""
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")


class MilvusConfig(BaseModel):
    """Milvus configuration settings"""
    host: str = Field(default="localhost", description="Milvus host")
    port: int = Field(default=19530, description="Milvus port")


class ElasticsearchConfig(BaseModel):
    """Elasticsearch configuration settings"""
    host: str = Field(default="localhost", description="Elasticsearch host")
    port: int = Field(default=9200, description="Elasticsearch port")


class DataForgeConfig(BaseModel):
    """Main configuration model for DataForge AI"""
    env: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=True, description="Debug mode flag")
    
    kafka: KafkaConfig = Field(default_factory=KafkaConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    milvus: MilvusConfig = Field(default_factory=MilvusConfig)
    elasticsearch: ElasticsearchConfig = Field(default_factory=ElasticsearchConfig)


class ConfigManager:
    """Configuration manager with support for multiple sources"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Optional path to a custom configuration file
        """
        self.config_path = config_path or "config/default.yaml"
        self._config: Optional[DataForgeConfig] = None
    
    @property
    def config(self) -> DataForgeConfig:
        """Get the loaded configuration, loading it if necessary"""
        if self._config is None:
            self.load_config()
        return self._config
    
    def load_config(self) -> DataForgeConfig:
        """Load configuration from YAML file and environment variables"""
        # Load base configuration from YAML
        config_dict = self._load_yaml_config()
        
        # Override with environment variables
        config_dict = self._apply_environment_overrides(config_dict)
        
        # Validate and create configuration object
        try:
            self._config = DataForgeConfig(**config_dict)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")
        
        return self._config
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = Path(self.config_path)
        
        if not config_path.exists():
            # If config file doesn't exist, return defaults
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _apply_environment_overrides(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to the configuration"""
        # Apply top-level environment variables
        if os.getenv("ENVIRONMENT"):
            config_dict["env"] = os.getenv("ENVIRONMENT")
        if os.getenv("DEBUG") is not None:
            config_dict["debug"] = os.getenv("DEBUG").lower() in ("true", "1", "yes")
        
        # Apply Kafka config environment variables
        kafka_config = config_dict.get("kafka", {})
        if os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
            kafka_config["bootstrap_servers"] = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        if os.getenv("KAFKA_TOPIC_PREFIX"):
            kafka_config["topic_prefix"] = os.getenv("KAFKA_TOPIC_PREFIX")
        config_dict["kafka"] = kafka_config
        
        # Apply Storage config environment variables
        storage_config = config_dict.get("storage", {})
        if os.getenv("MINIO_ENDPOINT"):
            storage_config["minio_endpoint"] = os.getenv("MINIO_ENDPOINT")
        if os.getenv("MINIO_ACCESS_KEY"):
            storage_config["minio_access_key"] = os.getenv("MINIO_ACCESS_KEY")
        if os.getenv("MINIO_SECRET_KEY"):
            storage_config["minio_secret_key"] = os.getenv("MINIO_SECRET_KEY")
        config_dict["storage"] = storage_config
        
        # Apply Redis config environment variables
        redis_config = config_dict.get("redis", {})
        if os.getenv("REDIS_HOST"):
            redis_config["host"] = os.getenv("REDIS_HOST")
        if os.getenv("REDIS_PORT"):
            redis_config["port"] = int(os.getenv("REDIS_PORT"))
        config_dict["redis"] = redis_config
        
        # Apply Milvus config environment variables
        milvus_config = config_dict.get("milvus", {})
        if os.getenv("MILVUS_HOST"):
            milvus_config["host"] = os.getenv("MILVUS_HOST")
        if os.getenv("MILVUS_PORT"):
            milvus_config["port"] = int(os.getenv("MILVUS_PORT"))
        config_dict["milvus"] = milvus_config
        
        # Apply Elasticsearch config environment variables
        es_config = config_dict.get("elasticsearch", {})
        if os.getenv("ELASTICSEARCH_HOST"):
            es_config["host"] = os.getenv("ELASTICSEARCH_HOST")
        if os.getenv("ELASTICSEARCH_PORT"):
            es_config["port"] = int(os.getenv("ELASTICSEARCH_PORT"))
        config_dict["elasticsearch"] = es_config
        
        return config_dict
    
    def reload(self) -> DataForgeConfig:
        """Reload the configuration"""
        self._config = None
        return self.config


# Global instance for easy access
config_manager = ConfigManager()


def get_config(config_path: Optional[str] = None) -> DataForgeConfig:
    """Get the current configuration"""
    if config_path:
        return ConfigManager(config_path).config
    return config_manager.config