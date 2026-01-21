"""
MinHash去重作业单元测试
"""
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# 添加项目路径到sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.pipeline.spark.dedup.minhash_dedup_job import MinHashDedupJob, create_minhash_dedup_job
from src.pipeline.spark.base import SparkConfig


class TestMinHashDedupJob(unittest.TestCase):
    """MinHash去重作业测试类"""

    def setUp(self):
        """设置测试环境"""
        self.config = SparkConfig(
            app_name="test-minhash-deduplication",
            master_url="local[*]",
            executor_memory="1g",
            executor_cores=1,
            num_executors=1,
            additional_configs={}
        )

    def test_initialization(self):
        """测试初始化参数"""
        job = MinHashDedupJob(
            self.config,
            num_hash_functions=100,
            num_bands=20,
            signature_length=100,
            similarity_threshold=0.8
        )

        self.assertEqual(job.num_hash_functions, 100)
        self.assertEqual(job.num_bands, 20)
        self.assertEqual(job.signature_length, 100)
        self.assertEqual(job.similarity_threshold, 0.8)
        self.assertEqual(job.r, 5)  # 100 // 20 = 5

    def test_invalid_parameters(self):
        """测试无效参数"""
        with self.assertRaises(ValueError):
            MinHashDedupJob(
                self.config,
                num_hash_functions=100,
                num_bands=7,  # 不能被100整除
                signature_length=100,
                similarity_threshold=0.8
            )

    def test_create_minhash_dedup_job(self):
        """测试创建MinHash去重作业实例"""
        job = create_minhash_dedup_job(
            num_hash_functions=50,
            num_bands=10,
            signature_length=50,
            similarity_threshold=0.7
        )

        self.assertIsInstance(job, MinHashDedupJob)
        self.assertEqual(job.num_hash_functions, 50)
        self.assertEqual(job.num_bands, 10)
        self.assertEqual(job.signature_length, 50)
        self.assertEqual(job.similarity_threshold, 0.7)

    @patch('src.pipeline.spark.base.SparkJob.get_or_create_spark_session')
    def test_run_method_structure(self, mock_get_spark_session):
        """测试运行方法的结构"""
        # 创建Mock SparkSession和DataFrame
        mock_spark_session = Mock()
        mock_get_spark_session.return_value = mock_spark_session

        # 创建Mock DataFrame链
        mock_df = Mock()
        mock_processed_df = Mock()
        mock_minhash_df = Mock()
        mock_similar_pairs_df = Mock()
        mock_deduplicated_df = Mock()

        # 设置返回链
        mock_spark_session.read.parquet.return_value = mock_df
        mock_df.withColumn.side_effect = [
            mock_processed_df,  # 第一次withColumn调用
            mock_processed_df   # 第二次withColumn调用
        ]
        mock_processed_df.withColumn.side_effect = [
            mock_minhash_df     # 生成minhash signature
        ]

        job = MinHashDedupJob(self.config)

        # 模拟内部方法调用
        with patch.object(job, '_preprocess_text', return_value=mock_processed_df), \
             patch.object(job, '_generate_minhash_signatures', return_value=mock_minhash_df), \
             patch.object(job, '_build_lsh_and_find_similar', return_value=mock_similar_pairs_df), \
             patch.object(job, '_perform_deduplication', return_value=mock_deduplicated_df), \
             patch('src.pipeline.spark.base.utils.get_df_size', side_effect=[100, 80]), \
             patch('builtins.print'):
            result = job.run()

        # 验证结果结构
        self.assertIn("original_records", result)
        self.assertIn("final_records", result)
        self.assertIn("removed_records", result)
        self.assertIn("processed_successfully", result)
        self.assertTrue(result["processed_successfully"])

    def test_get_or_create_spark_session(self):
        """测试获取或创建Spark会话"""
        job = MinHashDedupJob(self.config)
        session = job.get_or_create_spark_session()

        self.assertIsNotNone(session)
        self.assertEqual(session.conf.get("spark.app.name"), self.config.app_name)

    def tearDown(self):
        """清理测试环境"""
        pass


if __name__ == '__main__':
    unittest.main()