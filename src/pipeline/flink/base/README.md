# Flink CDC 作业框架

DataForge AI 的 Flink CDC（Change Data Capture，变更数据捕获）作业框架，用于实时捕获数据库变更并将其流式传输到下游系统。

## 功能特点

- **StreamExecutionEnvironment 配置**: 预设了最佳实践的环境配置，包括并行度、检查点、重启策略等。
- **CDC Source 集成**: 提供了多种数据库的CDC源连接器（MySQL、PostgreSQL、SQL Server）。
- **状态管理**: 内置状态管理功能，用于跟踪处理进度和偏移量。
- **测试基础设施**: 包含单元测试和集成测试模板。

## 架构概览

该框架由以下几个核心组件构成：

- `CDCJob`: 主作业类，配置和启动整个CDC流程
- `CDCConfiguration`: 配置管理类，处理所有配置参数
- `CDCStateManager`: 状态管理器，跟踪处理进度和偏移量
- `CDCSourceConnector`: CDC源连接器抽象类及其实现

## 使用方法

### 1. 编译项目

```bash
cd src/pipeline/flink/base
mvn clean compile
```

### 2. 打包项目

```bash
mvn package
```

### 3. 运行CDC作业

```bash
flink run \
  -c com.dataforge.flink.cdc.CDCJob \
  target/dataforge-flink-cdc-1.0-SNAPSHOT.jar
```

## 配置

可以通过修改[CDCConfiguration](src/main/java/com/dataforge/flink/cdc/CDCConfiguration.java)类来调整各种参数，包括：

- 数据库连接参数
- 表名
- Kafka输出参数
- 检查点和重启策略

## 测试

运行单元测试:

```bash
mvn test
```

运行集成测试:

```bash
mvn verify
```

## 依赖

- Apache Flink 1.18.0
- Debezium CDC Connectors
- Kafka Client

## 注意事项

- 在生产环境中，需要根据实际资源情况调整并行度和内存设置
- 需要确保目标数据库已启用binlog（MySQL）或相应变更日志功能
- 网络配置需要允许Flink集群访问数据库和Kafka集群