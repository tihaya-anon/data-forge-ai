# Spark Jobs

DataForge AI 的 Spark 批处理作业，使用 Scala 编写。

## 作业列表

- **cleaning**: 数据清洗作业
- **dedup**: MinHash LSH 去重作业
- **quality**: 质量过滤作业

## 构建

```bash
sbt compile
sbt test
sbt assembly  # 打包 JAR
```

## 运行

```bash
spark-submit \
  --class com.dataforge.spark.CleaningJob \
  --master spark://localhost:7077 \
  target/scala-2.12/dataforge-spark-assembly-0.1.0.jar
```

## 依赖

详见 `build.sbt`
