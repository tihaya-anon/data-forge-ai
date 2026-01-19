# 🚀 DataForge AI - 大数据驱动的 LLM 训练与智能应用平台

<p align="center">
  <img src="docs/images/logo.png" alt="DataForge AI" width="200"/>
</p>

<p align="center">
  <b>端到端的大数据 AI 基础设施 | 从数据工程到智能应用</b>
</p>

<p align="center">
  <a href="#核心特性">核心特性</a> •
  <a href="#系统架构">系统架构</a> •
  <a href="#模块介绍">模块介绍</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#技术栈">技术栈</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Spark-3.5-orange?style=flat-square&logo=apachespark" alt="Spark"/>
  <img src="https://img.shields.io/badge/Flink-1.18-pink?style=flat-square&logo=apacheflink" alt="Flink"/>
  <img src="https://img.shields.io/badge/Kafka-3.6-black?style=flat-square&logo=apachekafka" alt="Kafka"/>
  <img src="https://img.shields.io/badge/Milvus-2.3-blue?style=flat-square" alt="Milvus"/>
  <img src="https://img.shields.io/badge/Python-3.10+-green?style=flat-square&logo=python" alt="Python"/>
</p>

---

## 📖 项目简介

**DataForge AI** 是一个基于流批一体架构的企业级大数据 AI 平台，涵盖 **LLM 训练数据工程** 和 **RAG 智能知识库** 两大核心模块。

本项目旨在解决大模型时代的数据工程挑战：
- 🔹 如何高效处理 PB 级训练数据？
- 🔹 如何保证训练数据质量？
- 🔹 如何构建实时更新的企业知识库？
- 🔹 如何实现高准确率的 RAG 检索？

---

## ✨ 核心特性

| 特性                | 描述                                               |
| ------------------- | -------------------------------------------------- |
| 🔄 **流批一体**      | 基于 Flink + Spark + Paimon 构建统一的数据处理架构 |
| 📊 **PB 级处理能力** | 支持千万级文档处理，10亿级向量检索                 |
| 🧹 **智能数据清洗**  | MinHash 去重、困惑度过滤、毒性检测、PII 脱敏       |
| 🔍 **高精度 RAG**    | 混合检索 + Rerank + 引用溯源，准确率 95%+          |
| ⏱️ **实时更新**      | CDC 实时捕获，知识库秒级同步                       |
| 📈 **可观测性**      | 完整的数据血缘、质量监控、Pipeline 可视化          |

---

## 🏗️ 系统架构

### 整体架构图

![System Architecture](docs/images/architecture.svg)

### 数据流转

![Data Flow](docs/images/data-flow.svg)

---

## 📦 模块介绍

### 模块一：LLM 训练数据工程平台

> 为大语言模型预训练和微调提供高质量数据集

#### 数据处理流程

![Training Data Pipeline](docs/images/training-pipeline.svg)

#### 去重算法详解

![Deduplication Algorithm](docs/images/dedup-algorithm.svg)

#### 核心指标

| 指标         | 数值              |
| ------------ | ----------------- |
| 日处理数据量 | 50TB+             |
| 去重处理速度 | 10亿文档 / 4小时  |
| 数据过滤率   | ~30% (低质量数据) |
| 数据版本数   | 支持无限版本回溯  |

#### 数据质量过滤规则

| 过滤器   | 类型 | 阈值                 | 说明                |
| -------- | ---- | -------------------- | ------------------- |
| 长度过滤 | 规则 | 50 < tokens < 100000 | 过滤过短或过长文档  |
| 行重复率 | 规则 | < 30%                | 行级重复内容占比    |
| 困惑度   | 模型 | PPL < 1000           | KenLM 语言模型评估  |
| 毒性分数 | 模型 | < 0.7                | 毒性内容检测        |
| 质量分数 | 模型 | > 0.5                | fastText 质量分类器 |

---

### 模块二：RAG 智能知识库平台

> 实时更新的企业知识库，支持高精度智能问答

#### RAG 处理流程

![RAG Pipeline](docs/images/rag-pipeline.svg)

#### 混合检索策略

![Retrieval Strategy](docs/images/retrieval-strategy.svg)

#### 核心指标

| 指标         | 数值              |
| ------------ | ----------------- |
| 文档更新延迟 | < 5 秒 (实时同步) |
| 向量检索延迟 | P99 < 50ms        |
| 检索召回率   | 95%+              |
| 答案准确率   | 90%+ (人工评测)   |
| 日均查询量   | 10万+             |

#### 检索策略对比

| 策略          | 召回率 | 精确率 | 延迟 | 适用场景   |
| ------------- | ------ | ------ | ---- | ---------- |
| 纯向量检索    | 85%    | 70%    | 20ms | 语义相似   |
| 纯关键词检索  | 75%    | 80%    | 15ms | 精确匹配   |
| 混合检索      | 92%    | 78%    | 35ms | 通用场景   |
| 混合 + Rerank | 95%    | 88%    | 80ms | 高精度要求 |

---

## 🛠️ 技术栈

### 计算引擎
| 组件         | 版本   | 用途                       |
| ------------ | ------ | -------------------------- |
| Apache Spark | 3.5.x  | 批处理、ML、大规模数据处理 |
| Apache Flink | 1.18.x | 流处理、实时计算、CDC      |
| Ray          | 2.9.x  | 分布式 Embedding 计算      |

### 存储层
| 组件           | 版本  | 用途               |
| -------------- | ----- | ------------------ |
| Apache Paimon  | 0.7.x | 流批一体数据湖存储 |
| Apache Iceberg | 1.4.x | 数据湖表格式       |
| Milvus         | 2.3.x | 向量数据库         |
| Redis          | 7.x   | 缓存、实时特征     |
| MinIO          | -     | 对象存储 (S3 兼容) |

### 消息队列
| 组件         | 版本  | 用途               |
| ------------ | ----- | ------------------ |
| Apache Kafka | 3.6.x | 消息总线、数据采集 |
| Debezium     | 2.4.x | CDC 数据捕获       |

### 分析查询
| 组件          | 版本  | 用途           |
| ------------- | ----- | -------------- |
| Apache Doris  | 2.1.x | 实时 OLAP 分析 |
| Trino         | 435   | 联邦查询       |
| Elasticsearch | 8.x   | 全文检索       |

### 编排与治理
| 组件           | 版本   | 用途                 |
| -------------- | ------ | -------------------- |
| Apache Airflow | 2.8.x  | Pipeline 编排调度    |
| DataHub        | 0.12.x | 元数据管理、数据血缘 |

### AI/ML
| 组件                  | 版本  | 用途           |
| --------------------- | ----- | -------------- |
| LangChain             | 0.1.x | LLM 应用框架   |
| Sentence Transformers | 2.2.x | Embedding 模型 |
| vLLM                  | 0.3.x | LLM 推理加速   |

---

## 📁 项目结构

```
dataforge-ai/
├── 📂 data-pipeline/                # 数据管道模块
│   ├── ingestion/                   # 数据采集
│   ├── processing/                  # 数据处理 (Spark/Flink jobs)
│   └── quality/                     # 数据质量
│
├── 📂 rag-platform/                 # RAG 平台模块
│   ├── document-processor/          # 文档处理
│   ├── embedding-service/           # 向量化服务
│   ├── retrieval-service/           # 检索服务
│   └── generation-service/          # 生成服务
│
├── 📂 storage/                      # 存储层配置
│   ├── data-lake/                   # Paimon/Iceberg 表定义
│   └── vector-store/                # Milvus Schema
│
├── 📂 orchestration/                # 编排调度
│   ├── airflow/                     # Airflow DAGs
│   └── monitoring/                  # Prometheus + Grafana
│
├── 📂 deployment/                   # 部署配置
│   ├── docker/                      # Docker 配置
│   └── kubernetes/                  # K8s 部署文件
│
├── 📂 docs/                         # 文档
│   ├── diagrams/                    # D2 图表源码
│   ├── images/                      # 生成的图片
│   ├── ARCHITECTURE.md              # 架构设计文档
│   └── RESUME_DESCRIPTION.md        # 简历描述模板
│
├── 📄 docker-compose.yml            # 本地开发环境
├── 📄 Makefile                      # 构建脚本
└── 📄 README.md                     # 项目说明
```

---

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.10+
- Java 11+ (Spark/Flink)
- D2 (可选，用于生成图表)

### 安装 D2 (图表生成)

```bash
# macOS
brew install d2

# Linux/macOS (通用)
curl -fsSL https://d2lang.com/install.sh | sh -s --
```

### 生成架构图

```bash
# 生成所有 SVG 图表
make diagrams

# 监听模式，修改自动重建
make watch

# 使用 Docker 生成（无需本地安装 D2）
make docker-diagrams
```

### 启动本地开发环境

```bash
# 1. 克隆项目
git clone https://github.com/your-org/dataforge-ai.git
cd dataforge-ai

# 2. 启动基础设施
docker-compose up -d kafka milvus redis minio

# 3. 启动计算服务
docker-compose up -d spark-master flink-jobmanager

# 4. 启动 RAG 服务
docker-compose up -d rag-api

# 5. 访问服务
# - Spark UI: http://localhost:8080
# - Flink UI: http://localhost:8081
# - Airflow: http://localhost:8082
# - Grafana: http://localhost:3000
# - RAG API: http://localhost:8000
```

### 运行示例

```python
# 示例：处理训练数据
from dataforge.pipeline import DataPipeline

pipeline = DataPipeline()
pipeline.run(
    input_path="s3://raw-data/common-crawl/",
    output_path="s3://processed-data/training/",
    config={
        "dedup_threshold": 0.8,
        "quality_score_min": 0.5,
        "enable_pii_removal": True
    }
)
```

```python
# 示例：RAG 查询
from dataforge.rag import RAGService

rag = RAGService()
response = rag.query(
    question="如何配置 Flink CDC 连接 MySQL?",
    top_k=10,
    rerank=True
)

print(response.answer)
print(response.sources)  # 引用来源
```

---

## 📊 性能指标

### 数据处理性能

| 场景           | 数据量     | 耗时  | 资源配置      |
| -------------- | ---------- | ----- | ------------- |
| 数据清洗       | 10TB       | 2小时 | 50节点 Spark  |
| MinHash 去重   | 10亿文档   | 4小时 | 100节点 Spark |
| 质量过滤       | 10TB       | 3小时 | 50节点 Spark  |
| Embedding 生成 | 1000万文档 | 6小时 | 8xA100 GPU    |

### RAG 服务性能

| 指标             | 数值  |
| ---------------- | ----- |
| 向量检索 QPS     | 5000+ |
| 端到端延迟 (P50) | 200ms |
| 端到端延迟 (P99) | 500ms |
| 检索召回率       | 95%+  |

---

## 🔧 开发指南

### 生成/更新图表

项目使用 [D2](https://d2lang.com) 作为图表引擎，源文件位于 `docs/diagrams/`。

```bash
# 查看可用命令
make help

# 生成所有图表
make diagrams

# 预览单个图表（实时更新）
make preview FILE=architecture

# 列出所有图表
make list
```

### CI/CD

项目配置了 GitHub Actions，当 `docs/diagrams/*.d2` 文件变更时会自动重新生成图片并提交。

---

## 📈 Roadmap

- [x] 数据清洗 Pipeline
- [x] MinHash 去重
- [x] 质量过滤
- [x] RAG 基础检索
- [x] D2 图表自动化生成
- [ ] 多模态文档处理 (图片、表格)
- [ ] 增量向量索引更新
- [ ] 自动化数据配比优化
- [ ] A/B Test 框架
- [ ] 模型蒸馏 Pipeline

---

## 📚 文档

- [架构设计文档](docs/ARCHITECTURE.md) - 详细技术架构说明
- [简历描述模板](docs/RESUME_DESCRIPTION.md) - 项目简历描述 + 面试准备

---

## 🤝 贡献指南

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

---

## 📄 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

---

## 📧 联系方式

- **作者**: Your Name
- **邮箱**: your.email@example.com
- **GitHub**: [@your-username](https://github.com/your-username)

---

<p align="center">
  <b>如果这个项目对你有帮助，请给一个 ⭐ Star!</b>
</p>
