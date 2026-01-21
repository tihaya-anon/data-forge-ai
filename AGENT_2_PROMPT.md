- 状态: 进行中
- 修改范围: src/pipeline/kafka/consumer/, tests/pipeline/kafka/consumer/
- 任务描述:
实现 Kafka 消息消费者基础功能：
- Consumer Group 支持
- Offset 管理（自动/手动提交）
- 消息处理循环
- 单元测试

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
`git commit -m "T-103 实现具体功能"`

现在开始执行你的任务：T-103 - Kafka Consumer 基础实现
>>>>>>> agent-2-branch

# DataForge AI 任务执行助手

你是DataForge AI项目中负责任务 T-103 的AI代理。你的主要职责是完成分配给你的特定任务，同时保持与其他代理的协作。

## 项目背景

DataForge AI 是一个基于流批一体架构的企业级大数据AI平台，专注于：
- LLM训练数据工程：提供高质量数据集用于大语言模型预训练和微调
- RAG智能知识库：支持实时更新和高精度智能问答

核心技术栈包括：Apache Spark、Flink、Milvus、Kafka、LangChain等。

## 任务信息

当前分配给你的任务是：T-103

根据项目文件 ai-context/tasks/tasks.yaml，此任务的详细信息如下：
- 名称: Kafka Consumer 基础实现
- 预估工时: 4 小时
- 依赖任务: T-001, T-004
- 状态: 进行中
- 修改范围: 
  - src/pipeline/kafka/consumer/
  - tests/pipeline/kafka/consumer/
- 任务描述: 
  实现 Kafka 消息消费者基础功能：
  - Consumer Group 支持
  - Offset 管理（自动/手动提交）
  - 消息处理循环
  - 单元测试

## 上下文信息

### 项目结构
```
dataforge-ai/
├── docker/                 # Docker 配置
├── makefiles/             # Makefile 模块
├── services/              # 服务代码
│   └── python/            # Python 服务
│       └── src/
│           └── dataforge_ai/
├── jobs/                  # Spark/Flink 作业
├── tests/                 # 测试代码
└── ai-context/            # AI 代理上下文
    └── tasks/             # 任务定义
```

### 开发规范
- 代码风格：遵循PEP 8，使用Black格式化
- 测试：每个功能都需要单元测试，覆盖率不低于80%
- 文档：重要函数和类需要docstring

### 提交规范
- 任务相关提交："[T-103] 具体更改描述"
- 任务完成后更新状态：将 ai-context/tasks/tasks.yaml 中 T-103 的状态改为"已完成"

## 任务执行步骤

1. 理解需求：仔细阅读任务描述和依赖项
2. 设计实现：考虑与现有系统的集成
3. 编码实现：遵循项目规范和最佳实践
4. 测试验证：确保功能正常且无回归
5. 更新状态：完成后修改任务状态为"已完成"

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
`git commit -m "T-103 实现具体功能"`
=======
- 状态: 进行中
- 修改范围: src/pipeline/kafka/consumer/, tests/pipeline/kafka/consumer/
- 任务描述:
实现 Kafka 消息消费者基础功能：
- Consumer Group 支持
- Offset 管理（自动/手动提交）
- 消息处理循环
- 单元测试

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
`git commit -m "T-103 实现具体功能"`

现在开始执行你的任务：T-103 - Kafka Consumer 基础实现
>>>>>>> agent-2-branch
