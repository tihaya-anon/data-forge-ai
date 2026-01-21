"""
Spark作业基础框架
包含SparkSession管理、作业配置加载和通用工具函数
"""
from typing import Optional, Dict, Any
from pyspark.sql import SparkSession
from pydantic import BaseModel, Field
import os


class SparkConfig(BaseModel):
    """Spark作业配置模型"""
    app_name: str = Field(default="dataforge-spark-job", description="应用名称")
    master_url: str = Field(default="local[*]", description="Spark Master URL")
    executor_memory: str = Field(default="2g", description="Executor内存大小")
    executor_cores: int = Field(default=2, description="每个Executor的核心数")
    num_executors: int = Field(default=2, description="Executor数量")
    driver_memory: str = Field(default="1g", description="Driver内存大小")
    driver_cores: int = Field(default=1, description="Driver核心数")
    additional_configs: Dict[str, Any] = Field(default_factory=dict, description="额外的Spark配置")

    class Config:
        extra = "allow"


class SparkJob:
    """Spark作业基类"""
    
    def __init__(self, config: SparkConfig):
        """
        初始化Spark作业
        :param config: Spark配置对象
        """
        self.config = config
        self.spark_session: Optional[SparkSession] = None
    
    def create_spark_session(self) -> SparkSession:
        """
        创建Spark会话
        :return: SparkSession实例
        """
        if self.spark_session is None:
            builder = (
                SparkSession
                .builder
                .appName(self.config.app_name)
                .master(self.config.master_url)
                .config("spark.executor.memory", self.config.executor_memory)
                .config("spark.executor.cores", self.config.executor_cores)
                .config("spark.executor.instances", self.config.num_executors)
                .config("spark.driver.memory", self.config.driver_memory)
                .config("spark.driver.cores", self.config.driver_cores)
            )
            
            # 添加额外配置
            for key, value in self.config.additional_configs.items():
                builder = builder.config(key, value)
                
            self.spark_session = builder.getOrCreate()
        
        return self.spark_session
    
    def get_or_create_spark_session(self) -> SparkSession:
        """
        获取现有的或创建新的Spark会话
        :return: SparkSession实例
        """
        if self.spark_session is None:
            return self.create_spark_session()
        return self.spark_session
    
    def stop_spark_session(self):
        """停止Spark会话"""
        if self.spark_session:
            self.spark_session.stop()
            self.spark_session = None
    
    def run(self):
        """执行作业的主方法，子类需要实现此方法"""
        raise NotImplementedError("子类必须实现run方法")
    
    def cleanup(self):
        """清理资源的方法，可以在子类中重写"""
        self.stop_spark_session()


def load_spark_config_from_dict(config_dict: Dict[str, Any]) -> SparkConfig:
    """
    从字典加载Spark配置
    :param config_dict: 配置字典
    :return: SparkConfig实例
    """
    return SparkConfig(**config_dict)


def load_spark_config_from_env() -> SparkConfig:
    """
    从环境变量加载Spark配置
    :return: SparkConfig实例
    """
    config_data = {}
    
    # 从环境变量获取配置值
    env_mapping = {
        'app_name': 'SPARK_APP_NAME',
        'master_url': 'SPARK_MASTER_URL',
        'executor_memory': 'SPARK_EXECUTOR_MEMORY',
        'executor_cores': 'SPARK_EXECUTOR_CORES',
        'num_executors': 'SPARK_NUM_EXECUTORS',
        'driver_memory': 'SPARK_DRIVER_MEMORY',
        'driver_cores': 'SPARK_DRIVER_CORES'
    }
    
    for attr_name, env_var in env_mapping.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            # 对于数字类型的值进行转换
            if attr_name in ['executor_cores', 'num_executors', 'driver_cores']:
                try:
                    config_data[attr_name] = int(env_value)
                except ValueError:
                    print(f"警告: 无法将 {env_var}={env_value} 转换为整数，使用默认值")
            else:
                config_data[attr_name] = env_value
    
    return SparkConfig(**config_data)