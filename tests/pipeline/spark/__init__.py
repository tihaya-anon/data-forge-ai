"""
Spark测试基础设施
提供用于测试Spark作业的基础组件
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from pyspark.sql import SparkSession
from unittest.mock import Mock


class SparkTestHelper:
    """
    Spark测试辅助类
    提供创建测试用的SparkSession和其他测试工具
    """
    
    @staticmethod
    def create_test_spark_session(app_name: str = "test-spark-app") -> SparkSession:
        """
        创建用于测试的SparkSession
        :param app_name: 应用名称
        :return: SparkSession实例
        """
        spark = (
            SparkSession
            .builder
            .appName(app_name)
            .master("local[2]")  # 使用2个核心进行测试
            .config("spark.sql.shuffle.partitions", "2")  # 减少分区数以加快测试
            .config("spark.default.parallelism", "2")
            .config("spark.sql.warehouse.dir", tempfile.mkdtemp())  # 使用临时目录
            .getOrCreate()
        )
        
        # 设置日志级别为WARN以减少输出
        spark.sparkContext.setLogLevel("WARN")
        
        return spark
    
    @staticmethod
    def cleanup_test_session(spark: SparkSession):
        """
        清理测试用的SparkSession
        :param spark: SparkSession实例
        """
        spark.catalog.clearCache()
        spark.stop()
    
    @staticmethod
    def create_temp_path() -> str:
        """
        创建临时路径用于测试
        :return: 临时路径字符串
        """
        return tempfile.mkdtemp()


class DataFrameTestCase:
    """
    DataFrame测试用例基类
    提供常用的DataFrame断言方法
    """
    
    def __init__(self):
        self.spark: Optional[SparkSession] = None
    
    def setUp(self, app_name: str = "test-case"):
        """
        设置测试环境
        :param app_name: 应用名称
        """
        self.spark = SparkTestHelper.create_test_spark_session(app_name)
    
    def tearDown(self):
        """清理测试环境"""
        if self.spark:
            SparkTestHelper.cleanup_test_session(self.spark)
            self.spark = None
    
    def assert_df_equal(self, df1, df2, msg: Optional[str] = None):
        """
        断言两个DataFrame相等
        :param df1: 第一个DataFrame
        :param df2: 第二个DataFrame
        :param msg: 自定义错误消息
        """
        if msg is None:
            msg = "DataFrames不相等"
        
        # 比较行数
        count1, count2 = df1.count(), df2.count()
        assert count1 == count2, f"{msg}: 行数不匹配 ({count1} vs {count2})"
        
        # 比较列数
        cols1, cols2 = df1.columns, df2.columns
        assert len(cols1) == len(cols2), f"{msg}: 列数不匹配"
        
        # 比较列名
        assert set(cols1) == set(cols2), f"{msg}: 列名不匹配"
        
        # 比较内容 - 通过计算差集来判断
        diff1 = df1.subtract(df2)
        diff2 = df2.subtract(df1)
        
        diff_count1 = diff1.count()
        diff_count2 = diff2.count()
        
        assert diff_count1 == 0 and diff_count2 == 0, \
            f"{msg}: DataFrame内容不相同，差异行数: {diff_count1 + diff_count2}"
    
    def assert_df_count(self, df, expected_count: int, msg: Optional[str] = None):
        """
        断言DataFrame的行数
        :param df: DataFrame
        :param expected_count: 期望的行数
        :param msg: 自定义错误消息
        """
        actual_count = df.count()
        if msg is None:
            msg = f"行数不匹配: 期望 {expected_count}, 实际 {actual_count}"
        assert actual_count == expected_count, msg
    
    def assert_df_contains_columns(self, df, columns: list, msg: Optional[str] = None):
        """
        断言DataFrame包含指定的列
        :param df: DataFrame
        :param columns: 列名列表
        :param msg: 自定义错误消息
        """
        missing_cols = set(columns) - set(df.columns)
        if msg is None:
            msg = f"缺少列: {missing_cols}"
        assert not missing_cols, msg


def create_sample_data():
    """
    创建示例数据用于测试
    :return: 示例数据列表
    """
    return [
        {"id": 1, "name": "Alice", "age": 25},
        {"id": 2, "name": "Bob", "age": 30},
        {"id": 3, "name": "Charlie", "age": 35}
    ]


def assert_spark_job_result(job_result, expected_result):
    """
    断言Spark作业结果
    :param job_result: 作业实际结果
    :param expected_result: 期望结果
    """
    assert job_result == expected_result, \
        f"作业结果不符合预期: 期望 {expected_result}, 实际 {job_result}"