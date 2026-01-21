# DataForge AI

企业级大数据 AI 平台 - 多语言架构

## 项目结构

```
dataforge-ai/
├── services/           # 微服务
│   ├── python/        # Python 服务 (RAG, API, 配置管理)
│   ├── kafka-clients/ # Kafka 客户端 (Java)
│   └── monitoring/    # 监控服务
│
├── jobs/              # 数据处理作业
│   ├── spark/        # Spark 批处理作业 (Scala)
│   └── flink/        # Flink 流处理作业 (Java)
│
├── docker/           # Docker 配置
├── docs/             # 文档
├── tests/            # 测试
└── config/           # 配置文件
```

## 技术栈

详见 [技术栈决策文档](docs/TECH_STACK.md)

- **Python**: RAG 服务、API、配置管理
- **Java**: Kafka 客户端、Flink 流处理
- **Scala**: Spark 批处理作业
- **SQL**: Spark SQL 数据处理

## 快速开始

### 环境要求

- Python 3.10+ (uv)
- Java 11+ (OpenJDK)
- Scala 2.12+ (sbt)
- Docker & Docker Compose

### 开发环境

```bash
# Python 服务
cd services/python
uv sync

# Spark 作业
cd jobs/spark
sbt compile

# Flink 作业
cd jobs/flink
mvn compile
```

### 启动服务

```bash
# 启动基础设施
make dev-minimal    # Kafka + Redis
make dev-rag        # RAG 开发环境
make dev-pipeline   # 数据管道环境

# 查看服务状态
make docker-status
make docker-urls
```

## 文档

- [开发环境配置](docs/DEVELOPMENT.md)
- [技术栈决策](docs/TECH_STACK.md)
- [架构设计](docs/ARCHITECTURE.md)
- [任务管理](.ai-context/PARALLEL_DEV.md)

## 项目状态

当前阶段: Phase 1 完成，Phase 2 开发中

查看详细任务: `make task-next`
