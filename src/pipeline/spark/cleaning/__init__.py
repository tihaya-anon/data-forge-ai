"""
数据清洗Spark作业
实现文本规范化、长度过滤、重复率检测和特殊字符处理功能
"""
from typing import Dict, Any, Optional, List
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, regexp_replace, trim, length, lower, upper, size, split
from pyspark.sql.types import StructType, StructField, StringType, LongType
from ...base import SparkJob, SparkConfig


class DataCleaningJob(SparkJob):
    """
    数据清洗作业类
    实现文本规范化、长度过滤、重复率检测和特殊字符处理功能
    """

    def __init__(self, config: SparkConfig, input_col: str = "text", output_col: str = "cleaned_text"):
        super().__init__(config)
        self.input_col = input_col
        self.output_col = output_col

    def run(self, input_df: Optional[DataFrame] = None) -> Dict[str, Any]:
        """
        执行数据清洗作业的主要方法
        :param input_df: 输入DataFrame，如果不提供则需要在子类中实现数据加载逻辑
        :return: 包含作业执行结果的字典
        """
        spark = self.get_or_create_spark_session()

        if input_df is None:
            # 如果没有提供输入DataFrame，这里应该实现数据加载逻辑
            # 为了演示目的，我们创建一个示例DataFrame
            sample_data = [
                ("  Hello World!  ",),
                ("Special@#$Characters123",),
                ("normal text",),
                ("duplicate test",),
                ("duplicate test",),
                ("",),
                ("A very long text that might exceed the maximum allowed length for demonstration purposes",)
            ]
            schema = StructType([StructField(self.input_col, StringType(), True)])
            input_df = spark.createDataFrame(sample_data, schema)

        # 执行数据清洗流程
        cleaned_df = input_df
        stats = {}

        # 1. 文本规范化
        cleaned_df = self.normalize_text(cleaned_df)
        stats['after_normalization'] = self._get_df_size(cleaned_df)

        # 2. 特殊字符处理
        cleaned_df = self.handle_special_characters(cleaned_df)
        stats['after_special_char_handling'] = self._get_df_size(cleaned_df)

        # 3. 长度过滤 (默认最小长度为1，最大长度为1000)
        cleaned_df = self.length_filter(cleaned_df, min_length=1, max_length=1000)
        stats['after_length_filtering'] = self._get_df_size(cleaned_df)

        # 4. 重复行检测与去除
        unique_df, duplicates_count = self.remove_duplicates(cleaned_df)
        stats['unique_records'] = self._get_df_size(unique_df)
        stats['duplicates_removed'] = duplicates_count

        # 最终结果统计
        stats['initial_records'] = self._get_df_size(input_df)
        stats['final_records'] = self._get_df_size(unique_df)
        stats['processed_successfully'] = True

        return stats

    def normalize_text(self, df: DataFrame) -> DataFrame:
        """
        文本规范化：去除首尾空格，统一大小写等
        :param df: 输入DataFrame
        :return: 规范化后的DataFrame
        """
        # 如果输出列与输入列不同，创建新列，否则更新原列
        if self.input_col != self.output_col:
            return df.withColumn(self.output_col, 
                                trim(lower(col(self.input_col))))
        else:
            return df.withColumn(self.input_col, 
                                trim(lower(col(self.input_col))))

    def handle_special_characters(self, df: DataFrame) -> DataFrame:
        """
        处理特殊字符：移除或替换特殊字符
        :param df: 输入DataFrame
        :return: 处理后的DataFrame
        """
        output_col = self.output_col if self.input_col != self.output_col else self.input_col
        # 移除特殊字符，保留字母、数字、空格和基本标点
        return df.withColumn(output_col,
                            regexp_replace(col(output_col), r'[^\w\s\.\,\!\?\-\:\;\(\)]', ''))

    def length_filter(self, df: DataFrame, min_length: int = 1, max_length: int = 1000) -> DataFrame:
        """
        长度过滤：过滤掉长度不在指定范围内的记录
        :param df: 输入DataFrame
        :param min_length: 最小长度
        :param max_length: 最大长度
        :return: 过滤后的DataFrame
        """
        output_col = self.output_col if self.input_col != self.output_col else self.input_col
        return df.filter(length(col(output_col)) >= min_length).filter(length(col(output_col)) <= max_length)

    def remove_duplicates(self, df: DataFrame) -> tuple:
        """
        去除重复行并返回唯一记录和重复记录数
        :param df: 输入DataFrame
        :return: (去重后的DataFrame, 重复记录数)
        """
        initial_count = self._get_df_size(df)
        unique_df = df.dropDuplicates([self.output_col if self.input_col != self.output_col else self.input_col])
        final_count = self._get_df_size(unique_df)
        duplicates_count = initial_count - final_count
        return unique_df, duplicates_count

    def _get_df_size(self, df: DataFrame) -> int:
        """
        获取DataFrame的行数
        :param df: DataFrame
        :return: DataFrame的行数
        """
        return df.count()


def create_cleaning_job(config: Optional[SparkConfig] = None) -> DataCleaningJob:
    """
    创建数据清洗作业实例
    :param config: Spark配置，如果不提供则使用默认配置
    :return: DataCleaningJob实例
    """
    if config is None:
        config = SparkConfig(
            app_name="data-cleaning-job",
            master_url="local[*]",
            executor_memory="2g",
            executor_cores=2,
            num_executors=2,
            additional_configs={
                "spark.sql.adaptive.enabled": "true",
                "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
            }
        )

    return DataCleaningJob(config)


if __name__ == "__main__":
    # 演示如何运行作业
    job = create_cleaning_job()
    
    try:
        result = job.run()
        print(f"数据清洗作业执行结果: {result}")
    finally:
        job.cleanup()