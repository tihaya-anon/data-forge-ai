# Kafka Clients

DataForge AI 的 Kafka 客户端库，使用 Java 编写。

## 模块

- **producer**: Kafka 消息生产者
- **consumer**: Kafka 消息消费者

## 构建

```bash
mvn clean compile
mvn test
mvn install  # 安装到本地仓库
```

## 使用

```java
import com.dataforge.kafka.producer.DataForgeProducer;

DataForgeProducer producer = new DataForgeProducer(config);
producer.send("topic", "key", "value");
```

## 依赖

详见 `pom.xml`
