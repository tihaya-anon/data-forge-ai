"""
通用配置模块
提供全局配置访问功能
"""

import os
from typing import Any, Dict, Optional


def get_config() -> Dict[str, Any]:
    """
    获取应用程序配置
    
    Returns:
        包含配置项的字典
    """
    config = {}
    
    # 日志相关配置
    config["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")
    config["SERVICE_NAME"] = os.getenv("SERVICE_NAME", "dataforge_ai")
    config["LOG_JSON_FORMAT"] = os.getenv("LOG_JSON_FORMAT", "true").lower() == "true"
    config["LOG_TO_CONSOLE"] = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
    config["LOG_TO_FILE"] = os.getenv("LOG_TO_FILE")
    
    # 指标相关配置
    config["ENABLE_METRICS"] = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    config["METRICS_NAMESPACE"] = os.getenv("METRICS_NAMESPACE", "dataforge_ai")
    config["PROMETHEUS_ENABLED"] = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"
    
    # 服务相关配置
    config["APP_ENV"] = os.getenv("APP_ENV", "development")
    config["SERVICE_HOST"] = os.getenv("SERVICE_HOST", "localhost")
    config["SERVICE_PORT"] = int(os.getenv("SERVICE_PORT", "8000"))
    
    return config


def get_config_value(key: str, default: Any = None) -> Any:
    """
    获取单个配置值
    
    Args:
        key: 配置键名
        default: 默认值
        
    Returns:
        配置值，如果不存在则返回默认值
    """
    config = get_config()
    return config.get(key, default)