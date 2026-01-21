"""
DataForge AI 指标模块
提供指标收集和监控功能
"""

from .interface import (
    MetricsCollector, 
    NoOpMetricsCollector, 
    get_metrics_collector, 
    set_metrics_collector
)
from .prometheus import (
    PrometheusMetricsCollector, 
    init_prometheus_metrics
)

__all__ = [
    "MetricsCollector",
    "NoOpMetricsCollector", 
    "get_metrics_collector",
    "set_metrics_collector",
    "PrometheusMetricsCollector",
    "init_prometheus_metrics"
]