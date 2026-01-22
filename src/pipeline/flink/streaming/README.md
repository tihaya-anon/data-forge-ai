# Flink 实时数据处理作业

## 概述

这是一个基于 Apache Flink 的实时数据处理作业，实现了以下功能：

- 数据清洗转换
- 窗口聚合
- 状态更新
- 输出到 Kafka 和 Milvus

## 功能特性

### 1. 数据清洗转换

- 过滤空值和无效数据
- 清理非 ASCII 字符
- 标准化数据格式

### 2. 窗口聚合

- 使用滚动窗口对数据进行聚合
- 计算每个窗口内的记录数量和总大小
- 支持可配置的窗口大小

### 3. 状态管理

- 跟踪处理的记录数量
- 记录处理时间戳
- 维护窗口状态

### 4. 输出

- 将聚合结果输出到 Kafka
- 支持输出到 Milvus 向量数据库（待实现）

## 配置参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `sourceTopic` | Kafka 源主题 | raw-input-topic |
| `sinkTopic` | Kafka 目标主题 | processed-output-topic |
| `kafkaBootstrapServers` | Kafka 服务器地址 | localhost:9092 |
| `milvusUri` | Milvus 服务器地址 | - |
| `milvusCollection` | Milvus 集合名称 | - |
| `windowSizeSeconds` | 窗口大小（秒） | 10 |
| `parallelism` | 并行度 | 2 |

## 使用方法

### 1. 编译

```bash
mvn clean package
```

### 2. 运行

```bash
# 使用 Flink CLI 运行作业
flink run target/flink-streaming-1.0-SNAPSHOT.jar
```

### 3. 从 Socket 输入测试

```bash
# 启动 socket 服务器（用于测试）
nc -lk 9999

# 然后运行 Flink 作业
flink run target/flink-streaming-1.0-SNAPSHOT.jar
```

## 架构设计

```
[数据源] -> [过滤] -> [清洗] -> [按键分区] -> [窗口聚合] -> [输出到 Kafka/Milvus]
```

## 依赖项

- Apache Flink 1.17+
- Kafka 连接器
- Jackson JSON 处理
- SLF4J 日志框架

## 注意事项

- 该作业使用检查点确保精确一次语义
- 实现了重启策略以应对故障
- 窗口大小可通过配置调整
- Milvus 输出功能待实现（需要额外的 Milvus 连接器依赖）

## 测试

单元测试和集成测试位于 `tests/pipeline/flink/streaming/` 目录下。