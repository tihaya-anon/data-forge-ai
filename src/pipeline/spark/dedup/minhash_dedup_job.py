"""
MinHash去重作业
实现基于MinHash LSH算法的文档相似度检测和去重功能
"""
from typing import Dict, Any, Optional
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, hash, rand, size, array_min, array_max
from pyspark.sql.types import ArrayType, IntegerType, StructField, StringType
from src.pipeline.spark.base import SparkJob, SparkConfig
from src.pipeline.spark.base.utils import log_df_info, get_df_size
import math


class MinHashDedupJob(SparkJob):
    """
    MinHash去重作业
    使用MinHash算法生成文档签名，再使用LSH进行相似文档检测和去重
    """
    
    def __init__(self, config: SparkConfig, num_hash_functions: int = 100, num_bands: int = 20, 
                 signature_length: int = 100, similarity_threshold: float = 0.8):
        """
        初始化MinHash去重作业
        :param config: Spark配置
        :param num_hash_functions: 哈希函数数量
        :param num_bands: LSH带的数量
        :param signature_length: 签名长度
        :param similarity_threshold: 相似度阈值
        """
        super().__init__(config)
        self.num_hash_functions = num_hash_functions
        self.num_bands = num_bands
        self.signature_length = signature_length
        self.similarity_threshold = similarity_threshold
        self.r = self.signature_length // self.num_bands  # 每个band的行数
        
        # 验证参数
        if self.signature_length % self.num_bands != 0:
            raise ValueError("签名长度必须可以被带数量整除")
    
    def run(self) -> Dict[str, Any]:
        """
        执行MinHash去重作业
        :return: 包含作业执行结果的字典
        """
        spark = self.get_or_create_spark_session()
        
        # TODO: 此处应从实际数据源加载数据，这里使用模拟数据
        # 在实际实现中，应从配置的输入路径加载数据
        input_path = self.config.additional_configs.get('input_path', None)
        output_path = self.config.additional_configs.get('output_path', None)
        
        if input_path:
            df = spark.read.parquet(input_path)
        else:
            # 创建示例数据
            df = self._create_sample_data(spark)
        
        log_df_info(df, "输入数据")
        
        # 预处理文本数据
        processed_df = self._preprocess_text(df)
        log_df_info(processed_df, "预处理后数据")
        
        # 生成MinHash签名
        minhash_df = self._generate_minhash_signatures(processed_df)
        log_df_info(minhash_df, "生成MinHash签名后")
        
        # 构建LSH索引并检测相似文档
        similar_pairs_df = self._build_lsh_and_find_similar(minhash_df)
        log_df_info(similar_pairs_df, "找到的相似文档对")
        
        # 执行去重
        deduplicated_df = self._perform_deduplication(processed_df, similar_pairs_df)
        log_df_info(deduplicated_df, "去重后数据")
        
        # 保存结果
        if output_path:
            deduplicated_df.write.mode("overwrite").parquet(output_path)
            print(f"去重结果已保存到: {output_path}")
        
        # 计算统计信息
        original_count = get_df_size(df)
        final_count = get_df_size(deduplicated_df)
        removed_count = original_count - final_count
        
        result = {
            "original_records": original_count,
            "final_records": final_count,
            "removed_records": removed_count,
            "similarity_threshold": self.similarity_threshold,
            "signature_length": self.signature_length,
            "num_hash_functions": self.num_hash_functions,
            "processed_successfully": True
        }
        
        return result
    
    def _create_sample_data(self, spark):
        """
        创建示例数据用于测试
        """
        from pyspark.sql.types import StructType, StructField, StringType, IntegerType
        
        schema = StructType([
            StructField("id", StringType(), True),
            StructField("text", StringType(), True)
        ])
        
        # 示例文档，包含一些相似文档用于测试去重效果
        data = [
            ("doc1", "This is a sample document about machine learning algorithms."),
            ("doc2", "This is a sample document about machine learning algorithms with minor changes."),
            ("doc3", "Another completely different document about data science."),
            ("doc4", "Yet another document about big data processing techniques."),
            ("doc5", "This is a sample document about machine learning algorithms."),  # 重复
            ("doc6", "Completely different text about software engineering."),
            ("doc7", "This is a sample document about ML algorithms."),  # 类似于doc1
        ]
        
        return spark.createDataFrame(data, schema)
    
    def _preprocess_text(self, df: DataFrame) -> DataFrame:
        """
        预处理文本数据
        - 分词
        - 转小写
        - 去除停用词（简化处理，仅去除常见词）
        """
        from pyspark.sql.functions import split, lower, regexp_replace, trim, array_remove
        
        # 简化的文本预处理
        processed_df = df.withColumn("words", 
                                   split(
                                       regexp_replace(
                                           regexp_replace(lower(col("text")), "[^a-zA-Z\\s]", ""),
                                           "\\s+", " "
                                       ), 
                                       "\\s+"
                                   ))
        
        # 移除空字符串元素
        processed_df = processed_df.withColumn("words", 
                                             array_remove(col("words"), ""))
        
        return processed_df
    
    def _generate_minhash_signatures(self, df: DataFrame) -> DataFrame:
        """
        生成MinHash签名
        """
        from pyspark.sql.functions import expr, array, collect_list, udf
        from pyspark.sql.types import ArrayType, IntegerType
        import random
        
        # 生成随机哈希函数参数
        random.seed(42)  # 固定种子以便复现
        hash_a = [random.randint(1, 1000000) for _ in range(self.signature_length)]
        hash_b = [random.randint(1, 1000000) for _ in range(self.signature_length)]
        prime_modulus = 2147483647  # 大质数
        
        # 定义生成MinHash签名的UDF
        def minhash_signature_udf(words):
            if not words:
                return [2147483647] * self.signature_length
            
            # 将词汇转换为哈希值集合
            word_hashes = set()
            for word in words:
                if word:  # 确保单词非空
                    word_hashes.add(hash(word) % prime_modulus)
            
            if not word_hashes:
                return [2147483647] * self.signature_length
            
            # 为每个哈希函数计算最小值
            signature = []
            for i in range(self.signature_length):
                min_val = min((word_hash * hash_a[i] + hash_b[i]) % prime_modulus 
                             for word_hash in word_hashes)
                signature.append(min_val)
            
            return signature
        
        # 注册UDF
        minhash_udf = udf(minhash_signature_udf, ArrayType(IntegerType()))
        
        # 应用UDF生成签名
        result_df = df.withColumn("minhash_signature", minhash_udf(col("words")))
        
        return result_df
    
    def _build_lsh_and_find_similar(self, df: DataFrame) -> DataFrame:
        """
        使用LSH构建索引并找出相似文档对
        """
        from pyspark.sql.functions import udf, floor, col, concat, lit
        from pyspark.sql.types import StringType
        import hashlib
        
        # 定义提取bands的UDF
        def extract_bands_udf(signature):
            bands = []
            for band_idx in range(self.num_bands):
                start_idx = band_idx * self.r
                end_idx = start_idx + self.r
                band = signature[start_idx:end_idx]
                # 将band转换为可哈希的字符串
                band_str = "-".join(map(str, band))
                # 使用MD5生成更短的哈希值
                band_hash = hashlib.md5(band_str.encode()).hexdigest()
                bands.append(f"band_{band_idx}_{band_hash}")
            return bands
        
        extract_bands_func = udf(extract_bands_udf, ArrayType(StringType()))
        df_with_bands = df.withColumn("bands", extract_bands_func(col("minhash_signature")))
        
        # 展开bands，使每个文档-band对成为一行
        from pyspark.sql.functions import explode
        expanded_df = df_with_bands.select("id", "text", explode("bands").alias("band_key"))
        
        # 自连接查找相同band的文档对
        joined_df = expanded_df.alias("a").join(
            expanded_df.alias("b"),
            (col("a.band_key") == col("b.band_key")) & (col("a.id") < col("b.id"))
        ).select(
            col("a.id").alias("doc_id_1"),
            col("b.id").alias("doc_id_2"),
            col("a.text").alias("text_1"),
            col("b.text").alias("text_2"),
            col("a.band_key")
        )
        
        # 去重可能的重复对（由于多个bands匹配）
        distinct_pairs = joined_df.dropDuplicates(["doc_id_1", "doc_id_2"])
        
        return distinct_pairs
    
    def _perform_deduplication(self, original_df: DataFrame, similar_pairs_df: DataFrame) -> DataFrame:
        """
        执行去重操作
        这里简单地移除相似文档对中的第二个文档，实际应用中可能需要更复杂的策略
        """
        # 获取所有需要移除的文档ID
        docs_to_remove = similar_pairs_df.select("doc_id_2").distinct()
        
        # 从原数据中过滤掉这些文档
        deduplicated_df = original_df.join(
            docs_to_remove,
            original_df["id"] == docs_to_remove["doc_id_2"],
            "left_anti"  # left anti join 保留左表中不匹配右表的数据
        )
        
        return deduplicated_df


def create_minhash_dedup_job(num_hash_functions: int = 100, num_bands: int = 20, 
                           signature_length: int = 100, similarity_threshold: float = 0.8) -> MinHashDedupJob:
    """
    创建MinHash去重作业实例
    :param num_hash_functions: 哈希函数数量
    :param num_bands: LSH带的数量
    :param signature_length: 签名长度
    :param similarity_threshold: 相似度阈值
    :return: MinHashDedupJob实例
    """
    config = SparkConfig(
        app_name="minhash-deduplication-job",
        master_url="local[*]",
        executor_memory="2g",
        executor_cores=2,
        num_executors=2,
        additional_configs={
            "spark.sql.adaptive.enabled": "true",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            "spark.sql.execution.arrow.pyspark.enabled": "true"
        }
    )
    
    return MinHashDedupJob(
        config=config,
        num_hash_functions=num_hash_functions,
        num_bands=num_bands,
        signature_length=signature_length,
        similarity_threshold=similarity_threshold
    )


if __name__ == "__main__":
    # 演示如何运行作业
    job = create_minhash_dedup_job()
    
    try:
        result = job.run()
        print(f"MinHash去重作业执行结果: {result}")
    finally:
        job.cleanup()