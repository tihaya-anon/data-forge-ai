# Flink Jobs

DataForge AI 的 Flink 流处理作业，使用 Java 编写。

## 作业列表

- **streaming**: 实时数据处理作业
- **cdc**: CDC 数据捕获作业

## 构建

```bash
mvn clean compile
mvn test
mvn package  # 打包 JAR
```

## 运行

```bash
flink run \
  -c com.dataforge.flink.StreamingJob \
  target/dataforge-flink-1.0-SNAPSHOT.jar
```

## 依赖

详见 `pom.xml`
