"""
测试日志功能模块
"""

import json
import logging
import unittest
from unittest.mock import patch
from io import StringIO

from dataforge_ai.common.logging import setup_logging, get_logger, log_with_fields
from dataforge_ai.common.logging.config import get_log_config, LogLevel


class TestLogging(unittest.TestCase):
    """日志功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.log_stream = StringIO()
        self.handler = logging.StreamHandler(self.log_stream)
        
        # 临时替换logger的处理器
        self.test_logger = get_logger("test_logger")
        for handler in self.test_logger.handlers[:]:
            self.test_logger.removeHandler(handler)
        self.test_logger.addHandler(self.handler)
        self.test_logger.setLevel(logging.DEBUG)
        
    def tearDown(self):
        """测试后清理"""
        self.handler.close()
    
    def test_setup_logging_creates_json_logger(self):
        """测试设置日志是否创建了JSON格式的日志记录器"""
        logger = setup_logging("test_service")
        
        # 记录一条日志
        logger.info("Test message")
        
        # 获取日志输出
        log_output = self.log_stream.getvalue().strip()
        
        # 验证是否为JSON格式
        try:
            parsed = json.loads(log_output)
            self.assertIn('timestamp', parsed)
            self.assertIn('level', parsed)
            self.assertIn('message', parsed)
            self.assertEqual(parsed['message'], 'Test message')
        except json.JSONDecodeError:
            self.fail("Log output is not valid JSON")
    
    def test_log_with_fields_adds_custom_properties(self):
        """测试带字段的日志记录功能"""
        logger = setup_logging("test_service")
        
        # 记录带字段的日志
        log_with_fields(
            logger,
            level=logging.INFO,
            msg="Test with fields",
            custom_field="custom_value",
            numeric_field=123
        )
        
        # 获取日志输出
        log_output = self.log_stream.getvalue().strip()
        parsed = json.loads(log_output)
        
        # 验证自定义字段是否正确添加
        self.assertEqual(parsed['message'], 'Test with fields')
        self.assertEqual(parsed['custom_field'], 'custom_value')
        self.assertEqual(parsed['numeric_field'], 123)
    
    def test_different_log_levels(self):
        """测试不同日志级别"""
        logger = setup_logging("test_service")
        
        # 测试各个级别的日志
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # 获取所有日志输出
        log_outputs = self.log_stream.getvalue().strip().split('\n')
        
        # 解析每条日志
        for i, log_output in enumerate(log_outputs):
            if log_output:  # 跳过空行
                parsed = json.loads(log_output)
                expected_messages = [
                    "Debug message",
                    "Info message", 
                    "Warning message",
                    "Error message"
                ]
                
                if i < len(expected_messages):
                    self.assertEqual(parsed['message'], expected_messages[i])
    
    def test_log_config_access(self):
        """测试日志配置访问"""
        config = get_log_config()
        
        # 验证配置对象具有正确的属性
        self.assertTrue(hasattr(config, 'log_level'))
        self.assertTrue(hasattr(config, 'service_name'))
        self.assertTrue(hasattr(config, 'enable_json_format'))
        
        # 验证日志级别是枚举类型
        self.assertIsInstance(config.log_level, LogLevel)


if __name__ == '__main__':
    unittest.main()