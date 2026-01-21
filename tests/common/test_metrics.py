"""
测试指标功能模块
"""

import unittest
from unittest.mock import MagicMock
from dataforge_ai.common.metrics import (
    MetricsCollector,
    NoOpMetricsCollector,
    get_metrics_collector,
    set_metrics_collector,
    PrometheusMetricsCollector
)


class TestMetricsCollector(MetricsCollector):
    """用于测试的指标收集器实现"""
    
    def __init__(self):
        self.data = {}
        
    def increment_counter(self, name: str, value: float = 1.0, labels=None) -> None:
        key = f"{name}_counter"
        if key not in self.data:
            self.data[key] = 0
        self.data[key] += value
    
    def set_gauge(self, name: str, value: float, labels=None) -> None:
        key = f"{name}_gauge"
        self.data[key] = value
    
    def observe_histogram(self, name: str, value: float, labels=None) -> None:
        key = f"{name}_histogram"
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(value)
    
    def observe_summary(self, name: str, value: float, labels=None) -> None:
        key = f"{name}_summary"
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(value)
    
    def register_counter(self, name: str, description: str, label_names=None) -> None:
        key = f"{name}_counter"
        self.data[key] = 0
    
    def register_gauge(self, name: str, description: str, label_names=None) -> None:
        key = f"{name}_gauge"
        self.data[key] = 0
    
    def register_histogram(self, name: str, description: str, label_names=None, buckets=None) -> None:
        key = f"{name}_histogram"
        self.data[key] = []
    
    def register_summary(self, name: str, description: str, label_names=None) -> None:
        key = f"{name}_summary"
        self.data[key] = []


class TestMetrics(unittest.TestCase):
    """指标功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 保存原始收集器
        self.original_collector = get_metrics_collector()
        
    def tearDown(self):
        """测试后清理"""
        # 恢复原始收集器
        set_metrics_collector(self.original_collector)
    
    def test_no_op_metrics_collector(self):
        """测试NoOp指标收集器"""
        collector = NoOpMetricsCollector()
        
        # 确保这些操作不会抛出异常
        collector.increment_counter("test_counter")
        collector.set_gauge("test_gauge", 10.0)
        collector.observe_histogram("test_histogram", 5.0)
        collector.observe_summary("test_summary", 3.0)
        
        # NoOp收集器不应该有任何数据
        # (这应该静默执行，没有错误)
    
    def test_custom_metrics_collector(self):
        """测试自定义指标收集器功能"""
        test_collector = TestMetricsCollector()
        set_metrics_collector(test_collector)
        
        # 注册指标
        test_collector.register_counter("requests", "Number of requests")
        test_collector.register_gauge("active_users", "Number of active users")
        test_collector.register_histogram("response_time", "Response time in seconds")
        test_collector.register_summary("processing_time", "Processing time in seconds")
        
        # 使用指标
        test_collector.increment_counter("requests", 1.0)
        test_collector.set_gauge("active_users", 42.0)
        test_collector.observe_histogram("response_time", 0.15)
        test_collector.observe_summary("processing_time", 0.25)
        
        # 验证数据是否正确记录
        self.assertEqual(test_collector.data["requests_counter"], 1.0)
        self.assertEqual(test_collector.data["active_users_gauge"], 42.0)
        self.assertIn(0.15, test_collector.data["response_time_histogram"])
        self.assertIn(0.25, test_collector.data["processing_time_summary"])
    
    def test_get_set_metrics_collector(self):
        """测试获取和设置指标收集器"""
        original = get_metrics_collector()
        
        # 创建新的收集器并设置
        new_collector = TestMetricsCollector()
        set_metrics_collector(new_collector)
        
        # 验证获取的是新设置的收集器
        self.assertIs(get_metrics_collector(), new_collector)
        
        # 恢复原始收集器
        set_metrics_collector(original)
        self.assertIs(get_metrics_collector(), original)
    
    def test_prometheus_metrics_collector_initialization(self):
        """测试Prometheus指标收集器初始化"""
        # 不管Prometheus是否可用，都应该能处理初始化
        try:
            # 尝试初始化Prometheus收集器
            prometheus_collector = PrometheusMetricsCollector()
            
            # 验证收集器被正确创建
            self.assertIsNotNone(prometheus_collector)
            
            # 验证收集器是MetricsCollector的实例
            self.assertIsInstance(prometheus_collector, MetricsCollector)
            
        except RuntimeError:
            # 如果Prometheus不可用，至少应能处理这个错误
            pass


if __name__ == '__main__':
    unittest.main()