# DataForge AI - 技术栈决策文档

## 概述

DataForge AI 是一个多语言（Polyglot）项目，不同模块根据其特性和性能要求选择最合适的技术栈。

## 技术选型原则

1. **性能优先**: 数据密集型组件使用 JVM 语言（Java/Scala）
2. **生态优势**: AI/ML 组件使用 Python
3. **开发效率**: API 和工具类组件根据团队熟悉度选择
4. **社区成熟度**: 优先选择社区支持好、文档完善的技术

## 模块技术栈

### Phase 2: 核心数据管道

| 模块 | 推荐语言 | 理由 | 备选方案 |
|------|---------|------|---------|
| **Kafka Producer** | Java | 官方客户端，性能最优，功能完整 | Scala, Python (kafka-python) |
| **Kafka Consumer** | Java | 同上，Consumer Group 管理更成熟 | Scala, Python |
| **配置管理** | Python | 简单灵活，Pydantic 验证方便 | Java (Spring Config) |
| **日志监控** | Python | 与 Prometheus/Grafana 集成简单 | Go |

**决策**:
- Kafka 客户端使用 **Java**（性能和稳定性）
- 配置和监控使用 **Python**（开发效率）

### Phase 3: 数据处理作业

| 模块 | 推荐语言 | 理由 | 备选方案 |
|------|---------|------|---------|
| **Spark 批处理** | Scala | 原生支持，性能最优，类型安全 | Java, PySpark |
| **Spark 数据清洗** | Scala/SQL | DataFrame API + Spark SQL | PySpark |
| **Spark MinHash 去重** | Scala | 计算密集型，需要性能 | Java |
| **Spark 质量过滤** | Scala | 同上 | PySpark (如需集成 Python ML 库) |
| **Flink CDC** | Java | Flink CDC 官方支持 Java 最好 | Scala |
| **Flink 流处理** | Java | 状态管理和性能要求高 | Scala |

**决策**:
- Spark 作业使用 **Scala** + **Spark SQL**（性能和表达力）
- Flink 作业使用 **Java**（社区支持和稳定性）
- 如需 Python ML 库集成，可在特定作业中使用 PySpark

### Phase 4: RAG 智能知识库

| 模块 | 推荐语言 | 理由 | 备选方案 |
|------|---------|------|---------|
| **文档处理** | Python | 丰富的文档解析库 (PyPDF2, python-docx) | Java (Apache Tika) |
| **Embedding 服务** | Python | Transformers, Sentence-Transformers 生态 | - |
| **向量检索** | Python | pymilvus 官方客户端 | Go (性能优化版) |
| **关键词检索** | Python | elasticsearch-py 成熟 | Java |
| **混合检索与重排序** | Python | ML 模型集成方便 | - |
| **LLM 生成服务** | Python | OpenAI SDK, LangChain 生态 | - |
| **RAG API** | Python | FastAPI 高性能异步框架 | Go (Gin), Java (Spring Boot) |

**决策**:
- RAG 全栈使用 **Python**（AI/ML 生态优势明显）
- API 使用 **FastAPI**（异步高性能，开发效率高）

### Phase 5: 集成与优化

| 模块 | 推荐语言 | 理由 |
|------|---------|------|
| **集成测试** | Python | pytest 生态完善，易于编写 |
| **性能测试** | Python/Go | Locust (Python) 或 k6 (Go) |
| **监控导出** | Python | Prometheus client 简单 |

## 项目结构

```
dataforge-ai/
├── services/
│   ├── python/              # Python 服务
│   │   ├── pyproject.toml
│   │   ├── rag-api/         # RAG API 服务
│   │   ├── config-service/  # 配置管理
│   │   └── monitoring/      # 监控服务
│   │
│   ├── kafka-clients/       # Kafka 客户端 (Java)
│   │   ├── pom.xml
│   │   ├── producer/
│   │   └── consumer/
│   │
│   └── stream-processing/   # 流处理 (Java)
│       ├── pom.xml
│       └── flink-jobs/
│
├── jobs/
│   ├── spark/               # Spark 作业 (Scala)
│   │   ├── build.sbt
│   │   ├── cleaning/
│   │   ├── dedup/
│   │   └── quality/
│   │
│   └── flink/               # Flink 作业 (Java)
│       ├── pom.xml
│       └── streaming/
│
├── docker/                  # Docker 配置
├── docs/                    # 文档
├── tests/                   # 测试
└── README.md
```

## 构建工具

| 语言 | 构建工具 | 依赖管理 |
|------|---------|---------|
| Python | uv | pyproject.toml |
| Java | Maven | pom.xml |
| Scala | sbt | build.sbt |

## 开发环境要求

### 必需
- Python 3.10+ (uv)
- Java 11+ (OpenJDK)
- Scala 2.12+ (通过 sbt 管理)
- Docker & Docker Compose

### 可选
- IntelliJ IDEA (Java/Scala 开发)
- PyCharm / VS Code (Python 开发)

## 性能考虑

### 为什么 Spark 用 Scala 而不是 PySpark？

1. **性能**: Scala 编译为 JVM 字节码，避免 Python 序列化开销
2. **类型安全**: 编译时类型检查，减少运行时错误
3. **内存效率**: 直接操作 JVM 对象，无需 Python-JVM 数据转换
4. **生态**: Spark MLlib 的 Scala API 更完整

**PySpark 适用场景**:
- 快速原型开发
- 需要集成 Python ML 库（scikit-learn, TensorFlow）
- 数据探索和分析

### 为什么 Flink 用 Java 而不是 PyFlink？

1. **成熟度**: PyFlink 相对较新，功能不完整
2. **状态管理**: Java API 的状态管理更强大
3. **性能**: 关键路径上的性能差异明显
4. **CDC 支持**: Flink CDC 主要支持 Java

## 混合语言集成

### Spark 调用 Python UDF

```scala
// Scala Spark 作业中调用 Python 函数
import org.apache.spark.sql.functions.udf
spark.udf.registerPython("python_quality_score", "quality_scorer.py")
```

### Java 调用 Python 服务

```java
// Java Kafka Consumer 调用 Python Embedding 服务
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://embedding-service:8000/embed"))
    .POST(HttpRequest.BodyPublishers.ofString(json))
    .build();
```

## 部署策略

| 组件类型 | 部署方式 |
|---------|---------|
| Python 服务 | Docker 容器 (FastAPI + Gunicorn) |
| Spark 作业 | spark-submit 提交 JAR |
| Flink 作业 | flink run 提交 JAR |
| Kafka 客户端 | 作为库被其他服务依赖 |

## 后续决策点

以下决策需要在实现时根据实际情况确定：

1. **Kafka 客户端语言**: 如果团队 Python 经验更丰富，可考虑 kafka-python
2. **Spark 作业语言**: 如果需要频繁集成 Python ML 库，可考虑 PySpark
3. **API 性能要求**: 如果 QPS 要求极高（>10k），可考虑 Go 重写 API

## 参考资料

- [Spark Performance Tuning](https://spark.apache.org/docs/latest/tuning.html)
- [Flink vs PyFlink](https://nightlies.apache.org/flink/flink-docs-master/docs/dev/python/overview/)
- [FastAPI Performance](https://fastapi.tiangolo.com/benchmarks/)
