"""
日志和指标模块使用示例
演示如何在实际应用中使用日志和指标收集功能
"""

from dataforge_ai.common.logging import setup_logging, get_logger, log_with_fields
from dataforge_ai.common.metrics import (
    get_metrics_collector,
    init_prometheus_metrics,
    PrometheusMetricsCollector
)
import time


def setup_application_monitoring():
    """
    设置应用程序监控
    """
    # 设置结构化日志
    logger = setup_logging("my-service")
    
    # 初始化Prometheus指标收集器
    try:
        prometheus_collector = init_prometheus_metrics()
        print("Prometheus metrics collector initialized")
    except RuntimeError as e:
        print(f"Failed to initialize Prometheus collector: {e}")
        # 使用默认的noop收集器
        pass
    
    return logger


def demonstrate_logging(logger):
    """
    演示日志功能
    """
    # 普通日志记录
    logger.info("Application started")
    logger.warning("This is a warning message")
    logger.error("An error occurred")
    
    # 带有自定义字段的日志
    log_with_fields(
        logger,
        level=20,  # INFO
        msg="Processing completed",
        duration_ms=150,
        records_processed=1000,
        user_id="user-123"
    )
    
    # 在函数内部记录带上下文的日志
    try:
        # 模拟一些操作
        result = 10 / 2
        log_with_fields(
            logger,
            level=20,
            msg="Division operation completed",
            dividend=10,
            divisor=2,
            result=result
        )
    except Exception as e:
        logger.error(f"Error during division: {str(e)}", exc_info=True)


def demonstrate_metrics():
    """
    演示指标收集功能
    """
    collector = get_metrics_collector()
    
    # 注册指标
    collector.register_counter(
        "app_requests_total",
        "Total number of requests",
        label_names=["method", "endpoint"]
    )
    
    collector.register_gauge(
        "app_active_users",
        "Number of active users"
    )
    
    collector.register_histogram(
        "app_request_duration_seconds",
        "Request duration in seconds",
        label_names=["method", "endpoint"],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
    )
    
    # 使用指标
    # 增加请求计数
    collector.increment_counter(
        "app_requests_total",
        labels={"method": "GET", "endpoint": "/api/users"}
    )
    
    # 设置活跃用户数
    collector.set_gauge("app_active_users", 42)
    
    # 记录请求持续时间
    start_time = time.time()
    time.sleep(0.1)  # 模拟处理时间
    duration = time.time() - start_time
    
    collector.observe_histogram(
        "app_request_duration_seconds",
        duration,
        labels={"method": "GET", "endpoint": "/api/users"}
    )


if __name__ == "__main__":
    print("Setting up application monitoring...")
    app_logger = setup_application_monitoring()
    
    print("\nDemonstrating logging functionality:")
    demonstrate_logging(app_logger)
    
    print("\nDemonstrating metrics functionality:")
    demonstrate_metrics()
    
    print("\nLogging and metrics infrastructure is ready!")