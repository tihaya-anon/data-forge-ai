"""
Spark作业通用工具函数
包含常用的数据处理和验证工具
"""
from typing import List, Union, Optional
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
from pyspark.sql.functions import lit
import logging


def create_dataframe_with_schema(
    spark: SparkSession, 
    data: List, 
    schema: Optional[Union[StructType, str]] = None
) -> DataFrame:
    """
    根据Schema创建DataFrame
    :param spark: SparkSession实例
    :param data: 输入数据
    :param schema: Schema定义
    :return: DataFrame实例
    """
    if schema:
        return spark.createDataFrame(data, schema)
    else:
        return spark.createDataFrame(data)


def safe_union_dataframes(dfs: List[DataFrame], allow_missing_columns: bool = False) -> DataFrame:
    """
    安全地合并多个DataFrame
    :param dfs: DataFrame列表
    :param allow_missing_columns: 是否允许缺失列
    :return: 合并后的DataFrame
    """
    if not dfs:
        raise ValueError("DataFrame列表不能为空")
    
    if len(dfs) == 1:
        return dfs[0]
    
    result_df = dfs[0]
    for df in dfs[1:]:
        if allow_missing_columns:
            # 如果允许缺失列，则对齐列
            all_cols = set(result_df.columns) | set(df.columns)
            for col in all_cols:
                if col not in result_df.columns:
                    result_df = result_df.withColumn(col, lit(None))
                if col not in df.columns:
                    df = df.withColumn(col, lit(None))
            # 确保列顺序一致
            result_df = result_df.select(sorted(all_cols))
            df = df.select(sorted(all_cols))
        
        result_df = result_df.union(df)
    
    return result_df


def validate_required_columns(df: DataFrame, required_columns: List[str]) -> bool:
    """
    验证DataFrame是否包含必需的列
    :param df: DataFrame
    :param required_columns: 必需的列名列表
    :return: True如果包含所有必需的列，否则False
    """
    df_columns = set(df.columns)
    required_set = set(required_columns)
    
    missing_columns = required_set - df_columns
    if missing_columns:
        logging.error(f"缺少必需的列: {missing_columns}")
        return False
    
    return True


def get_df_size(df: DataFrame) -> int:
    """
    获取DataFrame的行数
    :param df: DataFrame
    :return: DataFrame的行数
    """
    return df.count()


def sample_data(df: DataFrame, fraction: float, seed: Optional[int] = 42) -> DataFrame:
    """
    对DataFrame进行采样
    :param df: DataFrame
    :param fraction: 采样比例 (0.0 - 1.0)
    :param seed: 随机种子
    :return: 采样后的DataFrame
    """
    if fraction <= 0.0 or fraction > 1.0:
        raise ValueError("采样比例必须在(0.0, 1.0]范围内")
    
    return df.sample(fraction=fraction, seed=seed)


def save_partitioned_df(df: DataFrame, path: str, partition_by: List[str]):
    """
    保存分区DataFrame
    :param df: DataFrame
    :param path: 保存路径
    :param partition_by: 分区列列表
    """
    writer = df.write.mode("overwrite")
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    
    writer.parquet(path)


def read_parquet_with_partitions(spark: SparkSession, path: str, partitions: Optional[List[str]] = None):
    """
    读取分区Parquet文件
    :param spark: SparkSession
    :param path: 文件路径
    :param partitions: 分区列表
    :return: DataFrame
    """
    df = spark.read.parquet(path)
    
    if partitions:
        # 如果指定了分区列，则只选择这些列
        available_cols = set(df.columns)
        valid_partitions = [col for col in partitions if col in available_cols]
        if valid_partitions:
            df = df.select(*valid_partitions)
    
    return df


def log_df_info(df: DataFrame, name: str = "DataFrame"):
    """
    记录DataFrame的基本信息
    :param df: DataFrame
    :param name: DataFrame名称
    """
    row_count = get_df_size(df)
    col_count = len(df.columns)
    
    logging.info(f"{name}: {row_count} 行, {col_count} 列")
    logging.info(f"{name} 列名: {df.columns}")


def deduplicate_df(df: DataFrame, subset: Optional[List[str]] = None) -> DataFrame:
    """
    对DataFrame去重
    :param df: DataFrame
    :param subset: 用于比较重复的列列表，如果为None则使用所有列
    :return: 去重后的DataFrame
    """
    if subset:
        return df.dropDuplicates(subset=subset)
    else:
        return df.dropDuplicates()


def join_dataframes(
    left_df: DataFrame, 
    right_df: DataFrame, 
    join_keys: Union[str, List[str]], 
    join_type: str = "inner"
) -> DataFrame:
    """
    连接两个DataFrame
    :param left_df: 左DataFrame
    :param right_df: 右DataFrame
    :param join_keys: 连接键
    :param join_type: 连接类型，默认为"inner"
    :return: 连接后的DataFrame
    """
    return left_df.join(right_df, on=join_keys, how=join_type)


# 导入必须的函数
# from pyspark.sql.functions import lit  # 已在文件顶部导入