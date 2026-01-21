"""
测试Spark基础模块
测试SparkConfig、SparkJob类和配置加载功能
"""
import pytest
from src.pipeline.spark.base import (
    SparkConfig, 
    SparkJob, 
    load_spark_config_from_dict,
    load_spark_config_from_env
)
from pyspark.sql import SparkSession
import os


class TestSparkConfig:
    """测试SparkConfig模型"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = SparkConfig()
        
        assert config.app_name == "dataforge-spark-job"
        assert config.master_url == "local[*]"
        assert config.executor_memory == "2g"
        assert config.executor_cores == 2
        assert config.num_executors == 2
        assert config.driver_memory == "1g"
        assert config.driver_cores == 1
        
    def test_custom_config(self):
        """测试自定义配置"""
        custom_config = {
            "app_name": "my-custom-app",
            "master_url": "spark://localhost:7077",
            "executor_memory": "4g",
            "executor_cores": 4,
            "num_executors": 4,
            "driver_memory": "2g",
            "driver_cores": 2,
            "additional_configs": {"spark.sql.adaptive.enabled": "true"}
        }
        
        config = SparkConfig(**custom_config)
        
        assert config.app_name == "my-custom-app"
        assert config.executor_memory == "4g"
        assert config.executor_cores == 4
        assert "spark.sql.adaptive.enabled" in config.additional_configs


class TestSparkJob:
    """测试SparkJob类"""
    
    def test_initialization(self):
        """测试初始化"""
        config = SparkConfig(app_name="test-app")
        job = SparkJob(config)
        
        assert job.config == config
        assert job.spark_session is None
        
    def test_create_spark_session(self, mocker):
        """测试创建SparkSession"""
        # Mock SparkSession相关方法
        mock_builder = mocker.Mock()
        mock_app = mocker.Mock()
        mock_master = mocker.Mock()
        mock_config = mocker.Mock()
        mock_get_or_create = mocker.Mock()
        
        # 设置mock链
        mock_builder.appName.return_value = mock_app
        mock_app.master.return_value = mock_master
        mock_master.config.return_value = mock_config
        mock_config.config.return_value = mock_config
        mock_config.getOrCreate.return_value = mock_get_or_create
        
        mocker.patch('src.pipeline.spark.base.SparkSession', mocker.Mock(builder=mock_builder))
        
        config = SparkConfig(
            app_name="test-app",
            master_url="local[*]",
            executor_memory="2g",
            executor_cores=2,
            num_executors=2,
            driver_memory="1g",
            driver_cores=1
        )
        
        job = SparkJob(config)
        session = job.create_spark_session()
        
        # 验证是否正确调用了SparkSession的构建方法
        assert session == mock_get_or_create
        assert job.spark_session == mock_get_or_create
        
    def test_get_or_create_spark_session(self, mocker):
        """测试获取或创建SparkSession"""
        mock_session = mocker.Mock()
        mocker.patch('src.pipeline.spark.base.SparkSession')
        
        config = SparkConfig(app_name="test-app")
        job = SparkJob(config)
        
        # 模拟已经创建了session的情况
        job.spark_session = mock_session
        
        session = job.get_or_create_spark_session()
        assert session == mock_session
        
    def test_stop_spark_session(self, mocker):
        """测试停止SparkSession"""
        mock_session = mocker.Mock()
        config = SparkConfig(app_name="test-app")
        job = SparkJob(config)
        job.spark_session = mock_session
        
        job.stop_spark_session()
        
        mock_session.stop.assert_called_once()
        assert job.spark_session is None
        
    def test_run_method_raises_not_implemented(self):
        """测试run方法抛出NotImplementedError异常"""
        config = SparkConfig(app_name="test-app")
        job = SparkJob(config)
        
        with pytest.raises(NotImplementedError):
            job.run()


class TestConfigLoading:
    """测试配置加载功能"""
    
    def test_load_spark_config_from_dict(self):
        """测试从字典加载配置"""
        config_dict = {
            "app_name": "loaded-app",
            "master_url": "spark://host:port",
            "executor_memory": "4g",
            "executor_cores": 3,
            "num_executors": 3,
            "driver_memory": "2g",
            "driver_cores": 2
        }
        
        config = load_spark_config_from_dict(config_dict)
        
        assert config.app_name == "loaded-app"
        assert config.master_url == "spark://host:port"
        assert config.executor_cores == 3
        assert config.num_executors == 3
        
    def test_load_spark_config_from_env(self, monkeypatch):
        """测试从环境变量加载配置"""
        # 设置环境变量
        monkeypatch.setenv("SPARK_APP_NAME", "env-test-app")
        monkeypatch.setenv("SPARK_MASTER_URL", "local[4]")
        monkeypatch.setenv("SPARK_EXECUTOR_MEMORY", "3g")
        monkeypatch.setenv("SPARK_EXECUTOR_CORES", "3")
        monkeypatch.setenv("SPARK_NUM_EXECUTORS", "3")
        monkeypatch.setenv("SPARK_DRIVER_MEMORY", "1.5g")
        monkeypatch.setenv("SPARK_DRIVER_CORES", "2")
        
        config = load_spark_config_from_env()
        
        assert config.app_name == "env-test-app"
        assert config.master_url == "local[4]"
        assert config.executor_memory == "3g"
        assert config.executor_cores == 3
        assert config.num_executors == 3
        assert config.driver_memory == "1.5g"
        assert config.driver_cores == 2