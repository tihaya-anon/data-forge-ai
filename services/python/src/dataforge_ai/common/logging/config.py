"""
日志配置模块
定义日志系统的配置选项和默认值
"""

import os
from typing import Optional
from enum import Enum


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogConfig:
    """日志配置类"""
    
    def __init__(self):
        self._log_level: LogLevel = self._parse_log_level(
            os.getenv("LOG_LEVEL", LogLevel.INFO.value)
        )
        self._service_name: str = os.getenv("SERVICE_NAME", "dataforge_ai")
        self._enable_json_format: bool = os.getenv("LOG_JSON_FORMAT", "true").lower() == "true"
        self._log_to_console: bool = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
        self._log_to_file: Optional[str] = os.getenv("LOG_TO_FILE")
        
    @property
    def log_level(self) -> LogLevel:
        """获取日志级别"""
        return self._log_level
        
    @log_level.setter
    def log_level(self, level: LogLevel) -> None:
        """设置日志级别"""
        self._log_level = level
        
    @property
    def service_name(self) -> str:
        """获取服务名称"""
        return self._service_name
        
    @property
    def enable_json_format(self) -> bool:
        """是否启用JSON格式日志"""
        return self._enable_json_format
        
    @property
    def log_to_console(self) -> bool:
        """是否输出到控制台"""
        return self._log_to_console
        
    @property
    def log_to_file(self) -> Optional[str]:
        """日志文件路径，None表示不输出到文件"""
        return self._log_to_file
        
    def _parse_log_level(self, level_str: str) -> LogLevel:
        """解析字符串形式的日志级别"""
        try:
            return LogLevel(level_str.upper())
        except ValueError:
            return LogLevel.INFO


# 全局日志配置实例
_log_config = LogConfig()


def get_log_config() -> LogConfig:
    """获取全局日志配置实例"""
    return _log_config