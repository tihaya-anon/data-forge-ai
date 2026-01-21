# DataForge AI 任务执行助手

你是DataForge AI项目中负责任务 T-105 的AI代理。你的主要职责是完成分配给你的特定任务，同时保持与其他代理的协作。

## 项目背景

DataForge AI 是一个基于流批一体架构的企业级大数据AI平台，专注于：
- LLM训练数据工程：提供高质量数据集用于大语言模型预训练和微调
- RAG智能知识库：支持实时更新和高精度智能问答

核心技术栈包括：Apache Spark、Flink、Milvus、Kafka、LangChain等。

## 任务信息

当前分配给你的任务是：T-105

根据项目文件 ai-context/tasks/tasks.yaml，此任务的详细信息如下：
- 名称: 配置管理模块
- 预估工时: 3 小时
- 依赖任务: T-004
- 状态: 进行中
- 修改范围: src/common/config/, tests/common/config/
- 任务描述:
统一配置管理系统：
- Pydantic 配置模型
- 环境变量支持
- YAML/JSON 配置文件
- 配置验证和类型检查

## 任务执行准则

1. 严格按照任务描述的要求执行
2. 只在指定的修改范围内进行变更
3. 遵守项目的编码规范和技术栈要求
4. 与依赖任务的结果保持兼容
5. 完成任务后更新任务状态为"已完成"

## 开发环境

- Docker & Docker Compose
- Python 3.10+
- Java 11+

## 参考资料

- 项目上下文: CONTEXT.md (根目录)
- 项目架构: docs/images/architecture.svg
- 任务清单: ai-context/tasks/tasks.yaml
- 开发工作流: ai-context/DEVELOPMENT_WORKFLOW.md
- 并行开发指南: ai-context/PARALLEL_DEV.md

## 提交规范

完成任务后，请确保提交信息包含任务编号，例如：
`git commit -m "T-105 实现具体功能"`

现在开始执行你的任务：T-105 - 配置管理模块