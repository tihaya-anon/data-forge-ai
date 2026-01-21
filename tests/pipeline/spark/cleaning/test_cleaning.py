"""
数据清洗作业测试
测试文本规范化、长度过滤、重复率检测和特殊字符处理功能
"""
import pytest
from unittest.mock import MagicMock
from src.pipeline.spark.cleaning import DataCleaningJob, create_cleaning_job
from src.pipeline.spark.base import SparkConfig
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType


def test_normalize_text():
    """测试文本规范化功能"""
    config = SparkConfig(app_name="test-normalize", master_url="local[*]")
    job = DataCleaningJob(config)
    
    # 创建测试数据
    spark = SparkSession.builder.appName("test").master("local[*]").getOrCreate()
    test_data = [("  HELLO World!  ",), ("  PySpark Test  ",), ("  DATA Engineering  ",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark.createDataFrame(test_data, schema)
    
    # 执行文本规范化
    result_df = job.normalize_text(df)
    result_rows = result_df.collect()
    
    # 验证结果
    assert result_rows[0][0] == "hello world!"
    assert result_rows[1][0] == "pyspark test"
    assert result_rows[2][0] == "data engineering"
    
    spark.stop()


def test_handle_special_characters():
    """测试特殊字符处理功能"""
    config = SparkConfig(app_name="test-special-chars", master_url="local[*]")
    job = DataCleaningJob(config)
    
    # 创建测试数据
    spark = SparkSession.builder.appName("test").master("local[*]").getOrCreate()
    test_data = [("Hello@#$World123!",), ("Special%*()Characters",), ("NormalText",)]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark.createDataFrame(test_data, schema)
    
    # 执行特殊字符处理
    result_df = job.handle_special_characters(df)
    result_rows = result_df.collect()
    
    # 验证结果
    assert result_rows[0][0] == "HelloWorld123!"  # 特殊字符被移除
    assert result_rows[1][0] == "SpecialCharacters"  # 特殊字符被移除
    assert result_rows[2][0] == "NormalText"  # 无变化
    
    spark.stop()


def test_length_filter():
    """测试长度过滤功能"""
    config = SparkConfig(app_name="test-length-filter", master_url="local[*]")
    job = DataCleaningJob(config)
    
    # 创建测试数据
    spark = SparkSession.builder.appName("test").master("local[*]").getOrCreate()
    test_data = [("short",), ("this is a medium length text",), ("very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very")]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark.createDataFrame(test_data, schema)
    
    # 执行长度过滤（最小长度为3，最大长度为50）
    filtered_df = job.length_filter(df, min_length=3, max_length=50)
    result_rows = filtered_df.collect()
    
    # 验证结果 - 只有符合长度要求的记录才会被保留
    assert len(result_rows) == 2  # "short" 和 "this is a medium length text" 符合要求
    assert result_rows[0][0] == "short"
    assert result_rows[1][0] == "this is a medium length text"
    
    spark.stop()


def test_remove_duplicates():
    """测试重复行检测与去除功能"""
    config = SparkConfig(app_name="test-duplicates", master_url="local[*]")
    job = DataCleaningJob(config)
    
    # 创建测试数据
    spark = SparkSession.builder.appName("test").master("local[*]").getOrCreate()
    test_data = [("duplicate test",), ("duplicate test",), ("unique text",), ("another unique",), ("duplicate test",)]
    schema = StructType([StructField("cleaned_text", StringType(), True)])
    df = spark.createDataFrame(test_data, schema)
    
    # 执行重复行去除
    unique_df, duplicates_count = job.remove_duplicates(df)
    unique_rows = unique_df.collect()
    
    # 验证结果
    assert len(unique_rows) == 3  # 3条唯一记录
    assert duplicates_count == 2  # 2条重复记录被移除
    
    spark.stop()


def test_run_method():
    """测试运行整个数据清洗流程"""
    config = SparkConfig(app_name="test-run", master_url="local[*]")
    job = DataCleaningJob(config)
    
    # 创建测试数据
    spark = SparkSession.builder.appName("test").master("local[*]").getOrCreate()
    test_data = [
        ("  HELLO@#$World123!  ",),  # 需要规范化和特殊字符处理
        ("  HELLO@#$World123!  ",),  # 重复项
        ("Short",),                  # 正常文本
        ("",),                       # 空字符串，会被长度过滤掉
        ("A very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very
    ]
    schema = StructType([StructField("text", StringType(), True)])
    df = spark.createDataFrame(test_data, schema)
    
    # 运行数据清洗流程
    result = job.run(df)
    
    # 验证结果
    assert result['initial_records'] == 5
    assert result['final_records'] == 2  # 去重后剩余的记录数
    assert result['duplicates_removed'] == 1  # 去除的重复记录数
    assert result['processed_successfully'] is True
    
    spark.stop()


def test_create_cleaning_job():
    """测试创建数据清洗作业实例"""
    job = create_cleaning_job()
    
    assert isinstance(job, DataCleaningJob)
    assert job.config.app_name == "data-cleaning-job"
    assert job.config.master_url == "local[*]"
    
    # 测试自定义配置
    custom_config = SparkConfig(app_name="custom-job", master_url="yarn")
    custom_job = create_cleaning_job(custom_config)
    
    assert custom_job.config.app_name == "custom-job"
    assert custom_job.config.master_url == "yarn"