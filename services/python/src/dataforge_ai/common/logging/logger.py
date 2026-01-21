import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from dataforge_ai.common.config import get_config


class JSONFormatter(logging.Formatter):
    """
    JSON格式化日志记录器
    将日志输出为结构化的JSON格式
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module or '',
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # 如果存在异常信息，添加到日志中
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # 如果有额外属性，也加入日志
        if hasattr(record, 'props'):
            log_entry.update(record.props)
            
        return json.dumps(log_entry)


def setup_logging(service_name: str = "dataforge_ai") -> logging.Logger:
    """
    设置结构化日志记录器
    
    Args:
        service_name: 服务名称，用于标识日志来源
        
    Returns:
        配置好的Logger实例
    """
    config = get_config()
    
    # 获取日志级别配置
    log_level_str = config.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # 创建logger
    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)
    
    # 清除现有处理器以避免重复
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建JSON格式化器
    json_formatter = JSONFormatter()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    
    # 添加处理器到logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的logger实例
    
    Args:
        name: Logger名称
        
    Returns:
        Logger实例
    """
    return logging.getLogger(name)


def log_with_fields(
    logger: logging.Logger, 
    level: int, 
    msg: str, 
    **fields: Any
) -> None:
    """
    记录带有自定义字段的日志
    
    Args:
        logger: Logger实例
        level: 日志级别
        msg: 日志消息
        **fields: 附加的字段
    """
    if logger.isEnabledFor(level):
        # 创建带有额外属性的LogRecord
        record = logger.makeRecord(
            name=logger.name,
            level=level,
            fn="", 
            lno=0,
            msg=msg,
            args=(),
            exc_info=None
        )
        record.props = fields
        logger.handle(record)