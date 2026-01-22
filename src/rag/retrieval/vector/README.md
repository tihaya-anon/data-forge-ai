# Vector Retrieval Service

向量检索服务模块，提供基于Milvus的高效向量相似度搜索功能。

## 功能特点

- **Milvus查询接口**：与Milvus向量数据库集成，提供高效的向量相似度搜索
- **相似度计算**：支持多种相似度计算方法（余弦相似度、欧几里得距离、点积）
- **Top-K检索**：支持返回最相似的K个结果
- **过滤条件支持**：支持对元数据字段进行过滤

## 使用示例

```python
from src.rag.retrieval.vector import VectorRetrievalService

# 初始化检索服务
retrieval_service = VectorRetrievalService()

# 连接到Milvus
retrieval_service.connect_to_milvus(host="localhost", port=19530)

# 执行相似度搜索
results = retrieval_service.similarity_search(
    query="如何使用Python进行数据分析？",
    collection_name="my_docs",
    top_k=5,
    filters={"category": "data_science"}  # 可选的过滤条件
)

# 计算两个向量之间的相似度
similarity = retrieval_service.calculate_similarity(
    vector_a=[0.1, 0.2, 0.3],
    vector_b=[0.15, 0.25, 0.35],
    metric="cosine"
)
```

## API说明

### VectorRetrievalService类

#### 方法

- `connect_to_milvus(host, port)`：连接到Milvus数据库
- `similarity_search(query, collection_name, top_k, filters, embedding_model)`：执行相似度搜索
- `calculate_similarity(vector_a, vector_b, metric)`：计算两个向量之间的相似度
- `hybrid_search(query, collection_name, top_k, filters, weight_vector, weight_text)`：执行混合搜索（向量+文本）

## 配置

向量检索服务可以通过配置文件进行自定义设置，包括：

- Milvus连接参数
- 默认Top-K值
- 相似度度量方法
- 缓存设置
- 过滤选项

## 依赖

- `pymilvus`：用于与Milvus数据库通信
- `numpy`：用于数值计算
- `transformers`：用于嵌入模型（通过embedding模块）