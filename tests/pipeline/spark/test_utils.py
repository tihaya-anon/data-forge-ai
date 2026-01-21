"""
测试Spark工具函数
测试utils模块中的各种工具函数
"""
import pytest
from unittest.mock import Mock
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from src.pipeline.spark.base.utils import (
    create_dataframe_with_schema,
    validate_required_columns,
    get_df_size,
    sample_data,
    log_df_info,
    deduplicate_df,
    join_dataframes,
    safe_union_dataframes
)


class TestSparkUtils:
    """测试Spark工具函数"""
    
    @pytest.fixture(scope="class")
    def spark_session(self):
        """创建测试用的SparkSession"""
        spark = (
            SparkSession
            .builder
            .appName("test-utils")
            .master("local[2]")
            .config("spark.sql.shuffle.partitions", "2")
            .getOrCreate()
        )
        yield spark
        spark.stop()
    
    def test_create_dataframe_with_schema(self, spark_session):
        """测试使用Schema创建DataFrame"""
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True)
        ])
        
        data = [(1, "Alice"), (2, "Bob")]
        
        df = create_dataframe_with_schema(spark_session, data, schema)
        
        assert df.count() == 2
        assert "id" in df.columns
        assert "name" in df.columns
        
    def test_create_dataframe_without_schema(self, spark_session):
        """测试不使用Schema创建DataFrame"""
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        
        df = create_dataframe_with_schema(spark_session, data)
        
        assert df.count() == 2
        assert "id" in df.columns
        assert "name" in df.columns
        
    def test_validate_required_columns_valid(self, spark_session):
        """测试验证必需列（有效情况）"""
        data = [{"id": 1, "name": "Alice", "age": 25}]
        df = spark_session.createDataFrame(data)
        
        required_columns = ["id", "name"]
        result = validate_required_columns(df, required_columns)
        
        assert result is True
        
    def test_validate_required_columns_invalid(self, spark_session):
        """测试验证必需列（无效情况）"""
        data = [{"id": 1, "name": "Alice"}]
        df = spark_session.createDataFrame(data)
        
        required_columns = ["id", "name", "age"]
        result = validate_required_columns(df, required_columns)
        
        assert result is False
        
    def test_get_df_size(self, spark_session):
        """测试获取DataFrame大小"""
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        df = spark_session.createDataFrame(data)
        
        size = get_df_size(df)
        
        assert size == 2
        
    def test_sample_data(self, spark_session):
        """测试数据采样"""
        data = []
        for i in range(100):
            data.append({"id": i, "value": f"value_{i}"})
        
        df = spark_session.createDataFrame(data)
        
        sampled_df = sample_data(df, 0.1, seed=42)  # 采样10%
        sampled_size = get_df_size(sampled_df)
        
        # 由于随机性，采样结果可能略有不同，但我们期望接近10%
        assert 5 <= sampled_size <= 15  # 允许一定范围内的变化
        
    def test_sample_data_invalid_fraction(self, spark_session):
        """测试数据采样（无效比例）"""
        data = [{"id": 1, "value": "value_1"}]
        df = spark_session.createDataFrame(data)
        
        with pytest.raises(ValueError):
            sample_data(df, 1.5)  # 比例大于1
            
        with pytest.raises(ValueError):
            sample_data(df, -0.1)  # 比例小于0
            
    def test_log_df_info(self, spark_session, caplog):
        """测试记录DataFrame信息"""
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        df = spark_session.createDataFrame(data)
        
        # 测试日志记录
        with caplog.at_level("INFO"):
            log_df_info(df, "test_df")
            
        # 验证日志中包含DataFrame信息
        assert "test_df:" in caplog.text
        assert "2 行" in caplog.text
        assert "2 列" in caplog.text
        
    def test_deduplicate_df(self, spark_session):
        """测试DataFrame去重"""
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 1, "name": "Alice"},  # 重复行
            {"id": 2, "name": "Bob"}
        ]
        df = spark_session.createDataFrame(data)
        
        deduplicated_df = deduplicate_df(df)
        
        assert get_df_size(deduplicated_df) == 2  # 应该只剩2行
        
    def test_join_dataframes(self, spark_session):
        """测试DataFrame连接"""
        left_data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        right_data = [{"id": 1, "age": 25}, {"id": 2, "age": 30}]
        
        left_df = spark_session.createDataFrame(left_data)
        right_df = spark_session.createDataFrame(right_data)
        
        joined_df = join_dataframes(left_df, right_df, "id")
        
        assert get_df_size(joined_df) == 2
        assert "name" in joined_df.columns
        assert "age" in joined_df.columns
        
    def test_safe_union_dataframes(self, spark_session):
        """测试安全合并DataFrame"""
        data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        data2 = [{"id": 3, "name": "Charlie"}, {"id": 4, "name": "David"}]
        
        df1 = spark_session.createDataFrame(data1)
        df2 = spark_session.createDataFrame(data2)
        
        result_df = safe_union_dataframes([df1, df2])
        
        assert get_df_size(result_df) == 4  # 应该有4行
        
    def test_safe_union_dataframes_empty_list(self):
        """测试空DataFrame列表合并"""
        with pytest.raises(ValueError):
            safe_union_dataframes([])