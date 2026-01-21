"""
Spark作业示例
展示如何使用Spark作业框架创建具体的作业
"""
from . import SparkJob, SparkConfig
from .utils import create_dataframe_with_schema, log_df_info, get_df_size
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from typing import Dict, Any


class SampleProcessingJob(SparkJob):
    """
    示例处理作业
    演示如何继承SparkJob基类实现具体的业务逻辑
    """
    
    def __init__(self, config: SparkConfig):
        super().__init__(config)
    
    def run(self) -> Dict[str, Any]:
        """
        执行作业的主要方法
        :return: 包含作业执行结果的字典
        """
        spark = self.get_or_create_spark_session()
        
        # 创建示例数据
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("department", StringType(), True)
        ])
        
        data = [
            (1, "Alice", "Engineering"),
            (2, "Bob", "Marketing"),
            (3, "Charlie", "Engineering"),
            (4, "Diana", "Sales"),
            (5, "Evan", "Engineering")
        ]
        
        df = create_dataframe_with_schema(spark, data, schema)
        log_df_info(df, "原始数据")
        
        # 进行一些简单的处理 - 例如筛选Engineer部门的员工
        engineering_df = df.filter(df.department == "Engineering")
        log_df_info(engineering_df, "筛选后的数据")
        
        # 计算结果
        total_count = get_df_size(df)
        engineering_count = get_df_size(engineering_df)  # 修复：原来是get_df_info
        
        result = {
            "total_records": total_count,
            "engineering_records": engineering_count,
            "processed_successfully": True
        }
        
        return result


def create_sample_job() -> SampleProcessingJob:
    """
    创建示例作业实例
    :return: SampleProcessingJob实例
    """
    config = SparkConfig(
        app_name="sample-processing-job",
        master_url="local[*]",
        executor_memory="1g",
        executor_cores=1,
        num_executors=1,
        additional_configs={
            "spark.sql.adaptive.enabled": "true",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
        }
    )
    
    return SampleProcessingJob(config)


if __name__ == "__main__":
    # 演示如何运行作业
    job = create_sample_job()
    
    try:
        result = job.run()
        print(f"作业执行结果: {result}")
    finally:
        job.cleanup()