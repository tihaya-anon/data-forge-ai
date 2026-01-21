"""
指标收集接口定义
定义统一的指标收集接口，为Prometheus集成做准备
"""

from abc import ABC, abstractmethod
from typing import Union, Dict, Any, Optional
from enum import Enum


class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricsCollector(ABC):
    """指标收集器抽象基类"""
    
    @abstractmethod
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """
        增加计数器值
        
        Args:
            name: 指标名称
            value: 增加的值，默认为1.0
            labels: 标签字典
        """
        pass
    
    @abstractmethod
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        设置仪表盘值
        
        Args:
            name: 指标名称
            value: 设置的值
            labels: 标签字典
        """
        pass
    
    @abstractmethod
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        观察直方图指标
        
        Args:
            name: 指标名称
            value: 观察值
            labels: 标签字典
        """
        pass
    
    @abstractmethod
    def observe_summary(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        观察摘要指标
        
        Args:
            name: 指标名称
            value: 观察值
            labels: 标签字典
        """
        pass
    
    @abstractmethod
    def register_counter(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        """
        注册计数器指标
        
        Args:
            name: 指标名称
            description: 指标描述
            label_names: 标签名称列表
        """
        pass
    
    @abstractmethod
    def register_gauge(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        """
        注册仪表盘指标
        
        Args:
            name: 指标名称
            description: 指标描述
            label_names: 标签名称列表
        """
        pass
    
    @abstractmethod
    def register_histogram(self, name: str, description: str, label_names: Optional[list] = None, buckets: Optional[list] = None) -> None:
        """
        注册直方图指标
        
        Args:
            name: 指标名称
            description: 指标描述
            label_names: 标签名称列表
            buckets: 桶边界列表
        """
        pass
    
    @abstractmethod
    def register_summary(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        """
        注册摘要指标
        
        Args:
            name: 指标名称
            description: 指标描述
            label_names: 标签名称列表
        """
        pass


class NoOpMetricsCollector(MetricsCollector):
    """空操作指标收集器，用于测试或禁用指标收集时"""
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        pass
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        pass
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        pass
    
    def observe_summary(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        pass
    
    def register_counter(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        pass
    
    def register_gauge(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        pass
    
    def register_histogram(self, name: str, description: str, label_names: Optional[list] = None, buckets: Optional[list] = None) -> None:
        pass
    
    def register_summary(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        pass


# 全局指标收集器实例
_metrics_collector: MetricsCollector = NoOpMetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器实例"""
    return _metrics_collector


def set_metrics_collector(collector: MetricsCollector) -> None:
    """设置全局指标收集器实例"""
    global _metrics_collector
    _metrics_collector = collector