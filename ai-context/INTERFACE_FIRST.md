# 接口优先开发指南

## 概述

在并行开发中，接口定义是协调多个团队/Agent 的关键。本指南说明如何在 DataForge AI 项目中实施接口优先开发。

## 何时需要接口优先

当满足以下任一条件时，必须先定义接口：

1. **跨服务通信**: 两个服务需要通过网络通信
2. **跨语言集成**: Java/Scala/Python 组件需要交换数据
3. **并行开发**: 多个任务同时开发且有依赖关系
4. **消息队列**: 通过 Kafka 等消息系统传递数据

## 接口定义方式

### 1. REST API (OpenAPI/Swagger)

**适用**: Python FastAPI 服务

**位置**: `docs/api/[service-name].yaml`

**示例**: RAG API

```yaml
# docs/api/rag-api.yaml
openapi: 3.0.0
info:
  title: RAG Query API
  version: 1.0.0

paths:
  /query:
    post:
      summary: Query RAG system
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QueryResponse'

components:
  schemas:
    QueryRequest:
      type: object
      required: [question]
      properties:
        question:
          type: string
          minLength: 1
          maxLength: 1000
        top_k:
          type: integer
          default: 10
          minimum: 1
          maximum: 100

    QueryResponse:
      type: object
      required: [answer, sources]
      properties:
        answer:
          type: string
        sources:
          type: array
          items:
            $ref: '#/components/schemas/Source'
        confidence:
          type: number
          minimum: 0
          maximum: 1

    Source:
      type: object
      required: [document_id, content]
      properties:
        document_id:
          type: string
        content:
          type: string
        score:
          type: number
```

**生成代码**:
```bash
# Python
openapi-generator generate -i docs/api/rag-api.yaml -g python -o services/python/generated

# Java
openapi-generator generate -i docs/api/rag-api.yaml -g java -o services/kafka-clients/generated
```

### 2. Protocol Buffers

**适用**: 跨语言高性能通信

**位置**: `schemas/[entity-name].proto`

**示例**: 训练数据消息

```protobuf
// schemas/training_data.proto
syntax = "proto3";

package dataforge.training;

message TrainingDataMessage {
  string message_id = 1;
  int64 timestamp = 2;
  string source = 3;
  string content = 4;
  map<string, string> metadata = 5;
  QualityMetrics quality = 6;
}

message QualityMetrics {
  double perplexity = 1;
  double toxicity_score = 2;
  double quality_score = 3;
  int32 length = 4;
}
```

**生成代码**:
```bash
# Python
protoc --python_out=services/python/src schemas/training_data.proto

# Java
protoc --java_out=services/kafka-clients/src/main/java schemas/training_data.proto

# Scala
protoc --scala_out=jobs/spark/src/main/scala schemas/training_data.proto
```

### 3. JSON Schema

**适用**: Kafka 消息、配置文件

**位置**: `schemas/[entity-name].json`

**示例**: Kafka 消息格式

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TrainingDataMessage",
  "type": "object",
  "required": ["message_id", "timestamp", "content"],
  "properties": {
    "message_id": {
      "type": "string",
      "format": "uuid"
    },
    "timestamp": {
      "type": "integer",
      "minimum": 0
    },
    "source": {
      "type": "string",
      "enum": ["web", "books", "papers", "code"]
    },
    "content": {
      "type": "string",
      "minLength": 1
    },
    "metadata": {
      "type": "object",
      "additionalProperties": {"type": "string"}
    }
  }
}
```

**验证**:
```python
# Python
from jsonschema import validate
import json

with open('schemas/training_data.json') as f:
    schema = json.load(f)

validate(instance=message, schema=schema)
```

### 4. Avro Schema

**适用**: Kafka Schema Registry

**位置**: `schemas/[entity-name].avsc`

**示例**:

```json
{
  "type": "record",
  "name": "TrainingDataMessage",
  "namespace": "com.dataforge.training",
  "fields": [
    {"name": "message_id", "type": "string"},
    {"name": "timestamp", "type": "long"},
    {"name": "source", "type": "string"},
    {"name": "content", "type": "string"},
    {"name": "metadata", "type": {"type": "map", "values": "string"}}
  ]
}
```

## 接口优先开发流程

### 场景: T-101 (Kafka Producer) 和 T-103 (Kafka Consumer) 并行开发

#### Day 1: 接口定义

**1. 创建消息 schema**

```bash
# 创建 schema 文件
cat > schemas/training_data.json << 'EOF'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TrainingDataMessage",
  ...
}
EOF
```

**2. 定义接口契约**

```markdown
# docs/interfaces/kafka-training-data.md

## Kafka Topic: training-data

### Producer (T-101)
- **Service**: Kafka Producer (Java)
- **Responsibility**: 发送训练数据到 Kafka
- **Message Format**: schemas/training_data.json
- **Topic**: `dataforge.training.raw`
- **Partitioning**: By source type
- **Guarantees**: At-least-once delivery

### Consumer (T-103)
- **Service**: Kafka Consumer (Java)
- **Responsibility**: 消费训练数据并转发到 Spark
- **Consumer Group**: `spark-processor`
- **Offset Management**: Auto-commit (5s interval)
- **Error Handling**: DLQ to `dataforge.training.dlq`

### Message Example
\`\`\`json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1705881600000,
  "source": "web",
  "content": "Sample training text...",
  "metadata": {
    "url": "https://example.com",
    "crawl_date": "2024-01-21"
  }
}
\`\`\`

### Error Codes
- `INVALID_FORMAT`: Message doesn't match schema
- `MISSING_REQUIRED_FIELD`: Required field missing
- `CONTENT_TOO_LARGE`: Content exceeds 1MB limit
```

**3. 生成代码骨架**

```bash
# 从 schema 生成 Java 类
make generate-schemas
```

**4. 创建 Mock 实现**

```python
# tests/mocks/kafka_producer_mock.py
class MockKafkaProducer:
    def send(self, topic, message):
        # 验证 schema
        validate_schema(message, TRAINING_DATA_SCHEMA)
        return MockFuture(success=True)
```

#### Day 2-3: 并行开发

**T-101 开发者**:
```java
// 使用生成的消息类
TrainingDataMessage message = TrainingDataMessage.builder()
    .messageId(UUID.randomUUID().toString())
    .timestamp(System.currentTimeMillis())
    .content(content)
    .build();

producer.send("dataforge.training.raw", message);
```

**T-103 开发者**:
```java
// 使用相同的消息类
consumer.subscribe("dataforge.training.raw");
while (true) {
    ConsumerRecords<String, TrainingDataMessage> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, TrainingDataMessage> record : records) {
        process(record.value());
    }
}
```

**关键**: 两个开发者使用相同的生成代码，保证兼容性

#### Day 4: Contract Testing

```java
// tests/contract/KafkaContractTest.java
@Test
public void testProducerConsumerContract() {
    // Producer 发送消息
    TrainingDataMessage sent = createTestMessage();
    producer.send("test-topic", sent);

    // Consumer 接收消息
    ConsumerRecords<String, TrainingDataMessage> records = consumer.poll(Duration.ofSeconds(5));
    TrainingDataMessage received = records.iterator().next().value();

    // 验证契约
    assertEquals(sent.getMessageId(), received.getMessageId());
    assertEquals(sent.getContent(), received.getContent());
    validateSchema(received);
}
```

#### Day 5: 集成测试

```bash
# 启动真实 Kafka
make dev-minimal

# 运行集成测试
cd services/kafka-clients
mvn verify -P integration-tests
```

## 接口版本管理

### 版本策略

- **v1**: 初始版本
- **v2**: 向后兼容的变更（新增字段）
- **v3**: 破坏性变更（删除字段、修改类型）

### 版本化方式

**1. URL 版本化** (REST API)
```
/v1/query
/v2/query
```

**2. Header 版本化**
```
Accept: application/vnd.dataforge.v1+json
```

**3. Schema 版本化** (Kafka)
```
schemas/training_data_v1.json
schemas/training_data_v2.json
```

### 兼容性规则

**向后兼容的变更** (可以直接部署):
- 添加新的可选字段
- 添加新的 API 端点
- 放宽验证规则

**破坏性变更** (需要协调部署):
- 删除字段
- 修改字段类型
- 重命名字段
- 收紧验证规则

## 工具和自动化

### Schema 验证

```bash
# 验证 JSON Schema
make validate-schemas

# 验证 OpenAPI
make validate-api-specs

# 验证 Protocol Buffers
make validate-protos
```

### 代码生成

```bash
# 生成所有语言的代码
make generate-all

# 只生成 Python
make generate-python

# 只生成 Java
make generate-java
```

### Contract Testing

```bash
# 运行所有 contract tests
make test-contracts

# 生成 contract test 报告
make contract-report
```

## 最佳实践

1. **Schema First**: 先定义 schema，再写代码
2. **版本控制**: 所有 schema 纳入版本控制
3. **自动生成**: 使用工具生成代码，不要手写
4. **验证严格**: 生产环境严格验证所有消息
5. **文档同步**: Schema 即文档，保持同步
6. **向后兼容**: 优先考虑向后兼容的设计
7. **Contract Testing**: 自动化测试接口契约
8. **Mock 优先**: 使用 Mock 解除依赖阻塞

## 示例项目结构

```
dataforge-ai/
├── schemas/                    # Schema 定义
│   ├── training_data.json     # JSON Schema
│   ├── training_data.proto    # Protocol Buffers
│   └── training_data.avsc     # Avro Schema
│
├── docs/
│   ├── api/                   # OpenAPI 规范
│   │   ├── rag-api.yaml
│   │   └── admin-api.yaml
│   └── interfaces/            # 接口文档
│       ├── kafka-training-data.md
│       └── milvus-vectors.md
│
├── services/
│   ├── python/
│   │   └── generated/         # 生成的代码
│   └── kafka-clients/
│       └── generated/         # 生成的代码
│
└── tests/
    ├── contract/              # Contract tests
    └── mocks/                 # Mock 实现
```

## 参考资料

- [OpenAPI Specification](https://swagger.io/specification/)
- [Protocol Buffers](https://protobuf.dev/)
- [JSON Schema](https://json-schema.org/)
- [Contract Testing with Pact](https://pact.io/)
