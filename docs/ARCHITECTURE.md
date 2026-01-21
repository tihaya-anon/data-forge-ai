# DataForge AI - 技术架构设计文档

## 1. 概述

本文档详细描述 DataForge AI 平台的技术架构设计，包括系统分层、核心组件、数据流转、关键技术选型等。

---

## 2. 系统分层架构

![System Layers Architecture](../docs/images/system-layers.svg)
```

---

## 3. 核心模块设计

### 3.1 数据采集模块

#### 3.1.1 架构设计

![Data Ingestion Architecture](../docs/images/data-ingestion.svg)

#### 3.1.2 Kafka Topic 设计

| Topic 名称        | 分区数 | 副本数 | 保留时间 | 用途           |
| ----------------- | ------ | ------ | -------- | -------------- |
| `raw-documents`   | 16     | 3      | 7d       | 原始文档       |
| `cdc-mysql-*`     | 8      | 3      | 3d       | MySQL CDC 事件 |
| `processed-docs`  | 16     | 3      | 7d       | 处理后文档     |
| `embedding-tasks` | 8      | 3      | 1d       | 向量化任务     |
| `dlq-*`           | 4      | 3      | 30d      | 死信队列       |

---

### 3.2 训练数据处理模块

#### 3.2.1 Spark 作业设计

```python
# 数据处理 Pipeline 伪代码

class TrainingDataPipeline:
    """训练数据处理主 Pipeline"""
    
    def __init__(self, spark: SparkSession, config: PipelineConfig):
        self.spark = spark
        self.config = config
        
    def run(self, input_path: str, output_path: str):
        # Stage 1: 数据加载
        raw_df = self.load_data(input_path)
        
        # Stage 2: 数据清洗
        cleaned_df = (raw_df
            .transform(self.normalize_encoding)
            .transform(self.remove_html_tags)
            .transform(self.filter_by_language)
            .transform(self.standardize_format))
        
        # Stage 3: 去重
        deduped_df = self.deduplicate(cleaned_df)
        
        # Stage 4: 质量过滤
        filtered_df = (deduped_df
            .transform(self.filter_by_length)
            .transform(self.filter_by_perplexity)
            .transform(self.filter_by_toxicity))
        
        # Stage 5: PII 处理
        safe_df = self.remove_pii(filtered_df)
        
        # Stage 6: 保存到数据湖
        self.save_to_paimon(safe_df, output_path)
```

#### 3.2.2 去重算法设计

![MinHash Deduplication Algorithm](../docs/images/minhash-dedup.svg)

#### 3.2.3 数据质量过滤规则

| 过滤器     | 类型 | 阈值                 | 说明                |
| ---------- | ---- | -------------------- | ------------------- |
| 长度过滤   | 规则 | 50 < tokens < 100000 | 过滤过短或过长文档  |
| 行重复率   | 规则 | < 30%                | 行级重复内容占比    |
| 段落重复率 | 规则 | < 30%                | 段落级重复内容占比  |
| 特殊字符   | 规则 | < 20%                | 非字母数字字符占比  |
| 困惑度     | 模型 | PPL < 1000           | KenLM 语言模型评估  |
| 毒性分数   | 模型 | < 0.7                | 毒性内容检测        |
| 质量分数   | 模型 | > 0.5                | fastText 质量分类器 |

---

### 3.3 RAG 检索模块

#### 3.3.1 检索架构

![RAG Retrieval Architecture](../docs/images/rag-retrieval.svg)

#### 3.3.2 Milvus Collection 设计

```python
# Milvus Schema 定义

from pymilvus import CollectionSchema, FieldSchema, DataType

# 字段定义
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=32),
    FieldSchema(name="created_at", dtype=DataType.INT64),
    FieldSchema(name="updated_at", dtype=DataType.INT64),
]

# Schema
schema = CollectionSchema(
    fields=fields,
    description="Knowledge base document embeddings"
)

# 索引配置
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {
        "M": 16,
        "efConstruction": 256
    }
}
```

#### 3.3.3 检索策略对比

| 策略          | 召回率 | 精确率 | 延迟 | 适用场景   |
| ------------- | ------ | ------ | ---- | ---------- |
| 纯向量检索    | 85%    | 70%    | 20ms | 语义相似   |
| 纯关键词检索  | 75%    | 80%    | 15ms | 精确匹配   |
| 混合检索      | 92%    | 78%    | 35ms | 通用场景   |
| 混合 + Rerank | 95%    | 88%    | 80ms | 高精度要求 |

---

### 3.4 数据湖存储设计

#### 3.4.1 Paimon 表设计

```sql
-- 训练数据表
CREATE TABLE training_data (
    doc_id STRING,
    content STRING,
    source STRING,
    language STRING,
    domain STRING,
    quality_score DOUBLE,
    token_count INT,
    created_at TIMESTAMP,
    processed_at TIMESTAMP,
    version INT,
    PRIMARY KEY (doc_id) NOT ENFORCED
) WITH (
    'bucket' = '16',
    'changelog-producer' = 'input',
    'merge-engine' = 'deduplicate',
    'sequence.field' = 'version',
    'snapshot.time-retained' = '7d'
);

-- 知识库文档表
CREATE TABLE knowledge_documents (
    chunk_id STRING,
    doc_id STRING,
    content STRING,
    embedding ARRAY<FLOAT>,
    metadata MAP<STRING, STRING>,
    source_url STRING,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (chunk_id) NOT ENFORCED
) WITH (
    'bucket' = '8',
    'changelog-producer' = 'lookup',
    'merge-engine' = 'partial-update',
    'partial-update.merge-columns' = 'content,embedding,metadata,updated_at'
);
```

#### 3.4.2 数据分区策略

```
数据湖目录结构:
s3://dataforge-lake/
├── training_data/
│   ├── domain=general/
│   │   ├── dt=2024-01-01/
│   │   ├── dt=2024-01-02/
│   │   └── ...
│   ├── domain=code/
│   ├── domain=math/
│   └── domain=instruction/
│
├── knowledge_base/
│   ├── source=confluence/
│   ├── source=git/
│   └── source=docs/
│
└── metadata/
    ├── data_quality/
    └── lineage/
```

![Data Lake Directory Structure](../docs/images/data-lake-structure.svg)

---

## 4. 数据流转设计

### 4.1 训练数据流

![Training Data Flow](../docs/images/training-data-flow.svg)

### 4.2 RAG 数据流

![RAG Data Flow](../docs/images/rag-data-flow.svg)

---

## 5. 关键技术决策

### 5.1 为什么选择 Paimon 而不是 Iceberg/Delta?

| 维度       | Paimon          | Iceberg        | Delta Lake      |
| ---------- | --------------- | -------------- | --------------- |
| 流批一体   | ⭐⭐⭐⭐⭐ 原生支持  | ⭐⭐⭐ 需额外组件 | ⭐⭐⭐ 需额外组件  |
| Flink 集成 | ⭐⭐⭐⭐⭐ 原生      | ⭐⭐⭐ 连接器     | ⭐⭐ 有限支持     |
| 实时更新   | ⭐⭐⭐⭐⭐ Changelog | ⭐⭐⭐ Row-level  | ⭐⭐⭐⭐ DML        |
| 社区活跃度 | ⭐⭐⭐ 快速增长    | ⭐⭐⭐⭐⭐ 最活跃   | ⭐⭐⭐⭐ Databricks |

**决策**: 主要使用 Paimon (流批一体优势)，同时支持 Iceberg (兼容性)

### 5.2 为什么选择 Milvus 而不是 Pinecone/Qdrant?

| 维度       | Milvus       | Pinecone | Qdrant |
| ---------- | ------------ | -------- | ------ |
| 私有部署   | ✅ 支持       | ❌ 仅云   | ✅ 支持 |
| 扩展性     | ⭐⭐⭐⭐⭐ 万亿级 | ⭐⭐⭐⭐     | ⭐⭐⭐    |
| 功能丰富度 | ⭐⭐⭐⭐⭐        | ⭐⭐⭐      | ⭐⭐⭐⭐   |
| 社区生态   | ⭐⭐⭐⭐⭐ LF AI  | ⭐⭐⭐ 商业 | ⭐⭐⭐    |

**决策**: 选择 Milvus (私有部署 + 扩展性 + 功能全面)

### 5.3 Embedding 模型选型

| 模型             | 维度 | 中文效果 | 速度 | 使用场景 |
| ---------------- | ---- | -------- | ---- | -------- |
| BGE-large-zh     | 1024 | ⭐⭐⭐⭐⭐    | 中   | 生产主力 |
| m3e-base         | 768  | ⭐⭐⭐⭐     | 快   | 轻量场景 |
| text-embedding-3 | 1536 | ⭐⭐⭐⭐     | 慢   | 多语言   |
| 领域微调模型     | 1024 | ⭐⭐⭐⭐⭐    | 中   | 特定领域 |

**决策**: BGE-large-zh 为主，支持自训练领域模型

---

## 6. 性能优化策略

### 6.1 Spark 优化

```python
# Spark 配置优化
spark_conf = {
    # 内存配置
    "spark.executor.memory": "8g",
    "spark.executor.memoryOverhead": "2g",
    "spark.memory.fraction": "0.8",
    
    # 并行度
    "spark.default.parallelism": "200",
    "spark.sql.shuffle.partitions": "200",
    
    # 数据倾斜优化
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",
    
    # 序列化
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    
    # 动态资源分配
    "spark.dynamicAllocation.enabled": "true",
    "spark.dynamicAllocation.minExecutors": "10",
    "spark.dynamicAllocation.maxExecutors": "100",
}
```

### 6.2 Milvus 优化

```python
# 搜索参数优化
search_params = {
    "metric_type": "COSINE",
    "params": {
        "ef": 128,  # 搜索时的候选集大小
        "nprobe": 16  # IVF 索引的探测数
    }
}

# 批量插入优化
insert_batch_size = 10000  # 批量插入大小
flush_interval = 60  # 刷新间隔(秒)
```

### 6.3 缓存策略

![Multi-Level Cache Architecture](../docs/images/cache-hierarchy.svg)

---

## 7. 监控与告警

### 7.1 核心监控指标

| 类别         | 指标            | 告警阈值 |
| ------------ | --------------- | -------- |
| **数据处理** | 处理延迟        | > 1 小时 |
|              | 处理失败率      | > 1%     |
|              | 数据质量分数    | < 0.7    |
| **RAG 服务** | 检索延迟 P99    | > 100ms  |
|              | 端到端延迟 P99  | > 1s     |
|              | 错误率          | > 0.1%   |
| **存储**     | Milvus 查询延迟 | > 50ms   |
|              | Kafka 消费延迟  | > 10000  |
|              | 磁盘使用率      | > 80%    |

### 7.2 Grafana 看板

- 数据处理 Pipeline 监控
- RAG 服务性能监控
- 基础设施资源监控
- 数据质量趋势分析

---

## 8. 部署架构

### 8.1 Kubernetes 部署

```
# 生产环境资源规划
resources:
  spark:
    driver:
      cpu: 4
      memory: 16Gi
    executor:
      instances: 10-100 (auto-scaling)
      cpu: 4
      memory: 8Gi
  
  flink:
    jobmanager:
      cpu: 2
      memory: 4Gi
    taskmanager:
      instances: 4-20 (auto-scaling)
      cpu: 4
      memory: 8Gi
      slots: 4
  
  milvus:
    proxy:
      replicas: 3
      cpu: 2
      memory: 4Gi
    queryNode:
      replicas: 5
      cpu: 8
      memory: 32Gi
    dataNode:
      replicas: 3
      cpu: 4
      memory: 16Gi
```

---

## 9. 总结

DataForge AI 平台通过流批一体的架构设计，实现了从原始数据到训练数据集、从知识库到智能问答的完整数据链路。核心技术选型包括：

- **计算引擎**: Spark (批处理) + Flink (流处理)
- **数据存储**: Paimon (数据湖) + Milvus (向量)
- **消息队列**: Kafka
- **编排调度**: Airflow
- **监控**: Prometheus + Grafana

该架构具备高扩展性、高可用性和高性能，能够满足企业级 AI 数据基础设施的需求。
