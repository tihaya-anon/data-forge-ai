# DataForge AI - 项目上下文

> 通用的 AI 助手上下文文件，适用于任何 AI 编程工具。

## 项目概览

| 项目     | 说明                                   |
| -------- | -------------------------------------- |
| **名称** | DataForge AI                           |
| **类型** | 作品集 / 演示项目                      |
| **目的** | 展示大数据 + AI/LLM 技术能力，用于求职 |
| **状态** | 仅供演示，非生产代码                   |

### 本项目展示的能力

1. **LLM 训练数据工程** - 大规模数据处理流水线，用于 LLM 预训练
2. **RAG 智能知识库** - 企业级智能问答系统，支持混合检索

## 开发环境

本项目使用双机开发环境：

| 机器     | 系统                       | 用途                    | 连接方式      |
| -------- | -------------------------- | ----------------------- | ------------- |
| **本机** | macOS                      | 主开发机、IDE、Git 操作 | -             |
| **远程** | Windows WSL (Ubuntu 24.04) | Docker 服务、重计算任务 | `ssh dev-win` |

### 远程机器使用

```bash
# 连接远程机器
ssh dev-win

# 在远程执行命令（单次）
ssh dev-win "cd /path/to/project && make docker-up"

# 同步代码到远程（如需要）
rsync -avz --exclude '.git' ./ dev-win:/path/to/project/
```

### 服务部署建议

| 服务         | 建议部署位置   | 原因                 |
| ------------ | -------------- | -------------------- |
| Docker 容器  | 远程 (dev-win) | 资源充足、不影响本机 |
| IDE / 编辑器 | 本机 (Mac)     | 体验流畅             |
| Git 操作     | 本机 (Mac)     | SSH key 配置         |
| 重计算任务   | 远程 (dev-win) | CPU/内存资源         |

## 技术栈

| 层级       | 技术                  |
| ---------- | --------------------- |
| 消息队列   | Apache Kafka          |
| 流处理     | Apache Flink          |
| 批处理     | Apache Spark          |
| 数据湖     | Apache Paimon + MinIO |
| 向量数据库 | Milvus                |
| 全文检索   | Elasticsearch         |
| 缓存       | Redis                 |
| OLAP       | Apache Doris          |
| 编排调度   | Apache Airflow        |
| 监控       | Prometheus + Grafana  |
| 图表       | D2 (Diagrams as Code) |

## 项目结构

```
.
├── Makefile                    # 主入口，引入 makefiles/*.mk
├── makefiles/
│   ├── diagrams.mk             # D2 图表生成
│   ├── docker.mk               # Docker Compose 操作
│   ├── dev.mk                  # 开发工具
│   └── parallel.mk             # 并行开发支持
├── docker/
│   ├── compose.base.yml        # 网络和卷定义
│   ├── compose.storage.yml     # Kafka, Milvus, Redis, ES, MinIO
│   ├── compose.compute.yml     # Spark, Flink
│   ├── compose.orchestration.yml # Airflow
│   ├── compose.analytics.yml   # Doris
│   ├── compose.monitoring.yml  # Prometheus, Grafana
│   └── monitoring/             # Prometheus/Grafana 配置
├── docs/
│   ├── diagrams/*.d2           # D2 图表源文件
│   ├── images/                 # 生成的 SVG（gitignore，由 CI 构建）
│   ├── ARCHITECTURE.md         # 详细技术架构
│   └── RESUME_DESCRIPTION.md   # 简历模板和面试准备
├── .ai-context/                # AI 助手上下文（本目录）
│   ├── CONTEXT.md              # 主上下文文件（本文件）
│   ├── PARALLEL_DEV.md         # 并行开发指南
│   ├── conventions.yaml        # 结构化规范数据
│   └── tasks/                  # 任务定义目录
├── .github/workflows/
│   └── generate-diagrams.yml   # 推送时自动生成图表
└── README.md                   # 项目文档
```

## 常用命令

```bash
# 显示所有命令
make help

# 启动特定服务组
make docker-storage      # Kafka, Milvus, Redis, ES, MinIO
make docker-compute      # Spark, Flink
make docker-monitoring   # Prometheus, Grafana

# 启动全部服务
make docker-up
make docker-down         # 停止全部服务

# 本地生成图表
make diagrams

# 显示服务地址
make urls

# 并行开发
make parallel-setup AGENTS=3   # 创建 3 个并行工作区
make parallel-status           # 查看工作区状态
make task-analyze              # 分析任务 DAG
```

### 远程执行命令

```bash
# 在远程启动 Docker 服务
ssh dev-win "cd ~/remote-env/data-forge-ai && make docker-up"

# 在远程查看日志
ssh dev-win "cd ~/remote-env/data-forge-ai && make docker-logs"

# 在远程停止服务
ssh dev-win "cd ~/remote-env/data-forge-ai && make docker-down"
```

## 代码规范

### Makefile

- 使用 `printf`（不是 `echo`）输出带 ANSI 颜色的文本
- 每个 target 添加 `## 注释` 会自动出现在 `make help`
- 预定义颜色：`$(GREEN)`, `$(YELLOW)`, `$(CYAN)`, `$(RED)`, `$(NC)`
- 模块化结构：主 `Makefile` 引入 `makefiles/*.mk`

### Docker Compose

- 每个文件**独立完整**（文件间不能使用 YAML anchor 引用）
- 网络名称：`dataforge`
- 容器命名规范：`dataforge-<服务名>`
- **所有服务必须包含健康检查**

### D2 图表

- 主题：`200`
- 布局：`elk`
- 内边距：`20`
- **避免**：外部图标 URL（会导致 403 错误）
- **避免**：`near: right`（无效，使用 `near: top-center` 或 `near: bottom-center`）
- **注意**：markdown 块 `|md ... |` 后不要有特殊字符

### 通用

- 中文注释和标签是允许的
- 重点展示架构设计，而非实现细节

## 架构亮点

### LLM 训练数据流水线

**流程**：数据清洗 → 去重（MinHash）→ 质量过滤 → PII 脱敏 → 数据混合

**关键指标**（面试参考）：
- 吞吐量：50TB+/天
- 去重能力：10亿文档 4小时内完成

### RAG 智能知识库

**处理方式**：
- 实时路径：Apache Flink
- 批处理路径：Apache Spark

**检索策略**：
- 向量检索（Milvus）+ BM25（ES）+ RRF 融合 + 重排序

**关键指标**：
- 同步延迟：<5秒
- 向量检索 P99：<50ms
- 端到端延迟：<500ms

## 修改指南

| 任务             | 操作                                                      |
| ---------------- | --------------------------------------------------------- |
| 添加 Docker 服务 | 创建/修改 `docker/compose.*.yml`                          |
| 添加图表         | 在 `docs/diagrams/` 创建 `.d2` 文件，运行 `make diagrams` |
| 添加 Make 命令   | 在 `makefiles/*.mk` 添加 target 并加上 `## 注释`          |
| 修改架构         | 同时更新图表和 `docs/ARCHITECTURE.md`                     |

## 重要说明

1. **SVG 文件不提交** - 由 GitHub Actions CI 生成
2. **这是演示项目** - 非生产级代码
3. **开发语言**：YAML、Markdown、D2，后续会有 Python/Java/Scala 实现
4. **双机开发** - 本机编码，远程运行服务
