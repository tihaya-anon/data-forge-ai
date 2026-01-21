"""
DataForge AI 通用配置管理模块
使用 Pydantic 配置模型进行配置管理
"""
from typing import Optional
import os
from pathlib import Path
from pydantic import BaseSettings, Field


class KafkaSettings(BaseSettings):
    """Kafka 配置设置"""
    
    bootstrap_servers: str = Field(
        default="localhost:9092",
        env="KAFKA_BOOTSTRAP_SERVERS",
        description="Kafka 服务器地址列表"
    )
    client_id: str = Field(
        default="dataforge-client",
        env="KAFKA_CLIENT_ID",
        description="Kafka 客户端ID"
    )
    request_timeout_ms: int = Field(
        default=30000,
        env="KAFKA_REQUEST_TIMEOUT_MS",
        description="请求超时时间(毫秒)"
    )
    retry_backoff_ms: int = Field(
        default=100,
        env="KAFKA_RETRY_BACKOFF_MS",
        description="重试间隔(毫秒)"
    )
    max_in_flight_requests_per_connection: int = Field(
        default=5,
        env="KAFKA_MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION",
        description="每连接最大并发请求数"
    )

    class Config:
        env_prefix = 'KAFKA_'


class LoggingSettings(BaseSettings):
    """日志配置设置"""
    
    level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="日志级别"
    )
    format: str = Field(
        default='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        env="LOG_FORMAT",
        description="日志格式"
    )
    json_format: bool = Field(
        default=False,
        env="LOG_JSON_FORMAT",
        description="是否使用 JSON 格式日志"
    )
    
    class Config:
        env_prefix = 'LOG_'


class DatabaseSettings(BaseSettings):
    """数据库配置设置"""
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="Redis 连接 URL"
    )
    milvus_host: str = Field(
        default="localhost",
        env="MILVUS_HOST",
        description="Milvus 服务器主机"
    )
    milvus_port: int = Field(
        default=19530,
        env="MILVUS_PORT",
        description="Milvus 服务器端口"
    )
    
    class Config:
        env_prefix = 'DB_'


class Settings(BaseSettings):
    """综合配置设置"""
    
    app_name: str = Field(
        default="DataForge AI",
        env="APP_NAME",
        description="应用名称"
    )
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="运行环境"
    )
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="调试模式"
    )
    
    # 子模块配置
    kafka: KafkaSettings = KafkaSettings()
    logging: LoggingSettings = LoggingSettings()
    database: DatabaseSettings = DatabaseSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局设置实例
settings = Settings()