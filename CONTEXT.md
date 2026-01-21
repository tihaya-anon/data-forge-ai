# DataForge AI - 项目上下文入口

欢迎来到DataForge AI项目！这是一个基于流批一体架构的企业级大数据AI平台，专为解决大模型时代的数据工程挑战而设计。

## 项目概述

DataForge AI旨在提供一个综合解决方案，涵盖两个核心模块：

1. **LLM训练数据工程平台** - 用于准备高质量的训练数据集
2. **RAG智能知识库平台** - 支持实时更新和高精度智能问答

该项目具备以下关键特性：
- 流批一体架构（使用Flink + Spark + Paimon）
- PB级处理能力（支持千万级文档处理，十亿级向量检索）
- 实时更新（通过CDC实时捕获，秒级同步）
- 高精度RAG（混合检索 + 引用溯源，准确率达95%+）

## 技术栈

- **计算引擎**: Apache Spark 3.5.x, Apache Flink 1.18.x, Ray 2.9.x
- **存储**: Milvus 2.3.x (向量数据库), Redis 7.x, MinIO, Apache Paimon 0.7.x
- **消息队列**: Apache Kafka 3.6.x, Debezium 2.4.x
- **分析查询**: Apache Doris 2.1.x, Trino 435, Elasticsearch 8.x
- **AI/ML**: LangChain 0.1.x, Sentence Transformers 2.2.x, vLLM 0.3.x

## 性能指标

- 日处理数据量: 50TB+
- 去重处理速度: 10亿文档 / 4小时
- 文档更新延迟: < 5秒
- 向量检索延迟: P99 < 50ms
- 端到端延迟 (P99): 500ms

## 深入了解项目

要全面了解项目，请参阅以下目录：

### [ai-context](./ai-context/) 
这是AI代理的主要上下文中心，包含：

- [CONTEXT.md](./ai-context/CONTEXT.md) - 项目详细上下文
- [INTERFACE_FIRST.md](./ai-context/INTERFACE_FIRST.md) - 接口优先开发策略
- [DEVELOPMENT_WORKFLOW.md](./ai-context/DEVELOPMENT_WORKFLOW.md) - 开发工作流程
- [PARALLEL_DEV.md](./ai-context/PARALLEL_DEV.md) - 并行开发指南
- [tasks/tasks.yaml](./ai-context/tasks/tasks.yaml) - 任务清单和依赖关系
- [conventions.yaml](./ai-context/conventions.yaml) - 项目约定和规范

### [docs](./docs/)
这是项目文档中心，包含：

- [architecture.svg](./docs/images/architecture.svg) - 系统架构图
- [diagrams/](./docs/diagrams/) - 各种系统图表
- [images/](./docs/images/) - 项目相关图像资源

## 开发环境

项目需要以下工具：
- Docker & Docker Compose
- Python 3.10+
- Java 11+
- D2 (可选，用于生成图表)

## 重要开发指令

- `make diagrams` - 生成所有SVG图表
- `make docker-up` - 启动所有服务
- `make docker-down` - 停止所有服务
- `make start` - 快速启动最小环境
- `make urls` - 查看服务URL

## 任务管理系统

项目使用任务DAG（有向无环图）规划 + Git Worktree并行开发，具体请参考：
- [ai-context/PARALLEL_DEV.md](./ai-context/PARALLEL_DEV.md)
- [makefiles/parallel.mk](./makefiles/parallel.mk)

---

**下一步行动**: 请仔细阅读[ai-context](./ai-context/)目录下的所有文档，然后查看[docs](./docs/)目录中的架构图和技术文档，以获得完整的项目理解。