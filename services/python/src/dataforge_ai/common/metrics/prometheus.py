"""
Prometheus指标收集器实现
实现MetricsCollector接口，提供Prometheus指标收集功能
"""

from typing import Union, Dict, Any, Optional
from dataforge_ai.common.metrics.interface import MetricsCollector, MetricType, get_metrics_collector, set_metrics_collector
from dataforge_ai.common.logging.logger import get_logger

try:
    from prometheus_client import Counter, Gauge, Histogram, Summary, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # 定义虚拟类以避免导入失败
    class Counter:
        def __init__(self, name: str, documentation: str, labelnames: tuple = ()):
            pass
        def inc(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
            pass

    class Gauge:
        def __init__(self, name: str, documentation: str, labelnames: tuple = ()):
            pass
        def set(self, value: float):
            pass

    class Histogram:
        def __init__(self, name: str, documentation: str, labelnames: tuple = (), buckets: Optional[list] = None):
            pass
        def observe(self, value: float):
            pass

    class Summary:
        def __init__(self, name: str, documentation: str, labelnames: tuple = ()):
            pass
        def observe(self, value: float):
            pass

    class CollectorRegistry:
        def __init__(self):
            pass


class PrometheusMetricsCollector(MetricsCollector):
    """Prometheus指标收集器实现"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        初始化Prometheus指标收集器
        
        Args:
            registry: Prometheus收集器注册表，如果为None则使用默认注册表
        """
        if not PROMETHEUS_AVAILABLE:
            raise RuntimeError(
                "Prometheus client library is not installed. "
                "Please install it with: pip install prometheus-client"
            )
        
        self.registry = registry or CollectorRegistry()
        self._metrics = {}
        self._logger = get_logger(__name__)
        
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """
        增加计数器值
        """
        metric_key = f"{name}_counter"
        if metric_key not in self._metrics:
            self._logger.warning(f"Counter {metric_key} not registered before incrementing")
            return
            
        counter = self._metrics[metric_key]
        if labels:
            counter.labels(**labels).inc(value)
        else:
            counter.inc(value)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        设置仪表盘值
        """
        metric_key = f"{name}_gauge"
        if metric_key not in self._metrics:
            self._logger.warning(f"Gauge {metric_key} not registered before setting")
            return
            
        gauge = self._metrics[metric_key]
        if labels:
            gauge.labels(**labels).set(value)
        else:
            gauge.set(value)
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        观察直方图指标
        """
        metric_key = f"{name}_histogram"
        if metric_key not in self._metrics:
            self._logger.warning(f"Histogram {metric_key} not registered before observing")
            return
            
        histogram = self._metrics[metric_key]
        if labels:
            histogram.labels(**labels).observe(value)
        else:
            histogram.observe(value)
    
    def observe_summary(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """
        观察摘要指标
        """
        metric_key = f"{name}_summary"
        if metric_key not in self._metrics:
            self._logger.warning(f"Summary {metric_key} not registered before observing")
            return
            
        summary = self._metrics[metric_key]
        if labels:
            summary.labels(**labels).observe(value)
        else:
            summary.observe(value)
    
    def register_counter(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        """
        注册计数器指标
        """
        metric_key = f"{name}_counter"
        label_names_tuple = tuple(label_names) if label_names else ()
        self._metrics[metric_key] = Counter(
            name, 
            description, 
            labelnames=label_names_tuple,
            registry=self.registry
        )
    
    def register_gauge(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        """
        注册仪表盘指标
        """
        metric_key = f"{name}_gauge"
        label_names_tuple = tuple(label_names) if label_names else ()
        self._metrics[metric_key] = Gauge(
            name, 
            description, 
            labelnames=label_names_tuple,
            registry=self.registry
        )
    
    def register_histogram(self, name: str, description: str, label_names: Optional[list] = None, buckets: Optional[list] = None) -> None:
        """
        注册直方图指标
        """
        metric_key = f"{name}_histogram"
        label_names_tuple = tuple(label_names) if label_names else ()
        kwargs = {'registry': self.registry}
        if buckets:
            kwargs['buckets'] = buckets
        self._metrics[metric_key] = Histogram(
            name, 
            description, 
            labelnames=label_names_tuple,
            **kwargs
        )
    
    def register_summary(self, name: str, description: str, label_names: Optional[list] = None) -> None:
        """
        注册摘要指标
        """
        metric_key = f"{name}_summary"
        label_names_tuple = tuple(label_names) if label_names else ()
        self._metrics[metric_key] = Summary(
            name, 
            description, 
            labelnames=label_names_tuple,
            registry=self.registry
        )


def init_prometheus_metrics() -> PrometheusMetricsCollector:
    """
    初始化Prometheus指标收集器并设置为全局实例
    
    Returns:
        初始化的PrometheusMetricsCollector实例
    """
    collector = PrometheusMetricsCollector()
    set_metrics_collector(collector)
    return collector