package com.dataforge.kafka.consumer;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.KafkaContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.assertTrue;

@Testcontainers
public class KafkaConsumerIT {
    
    @Container
    static KafkaContainer kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:latest"));

    @Test
    void testConsumerIntegration() throws InterruptedException {
        String topic = "test-integration-topic";
        String groupId = "test-integration-group";
        
        // 创建生产者发送测试消息
        Properties producerProps = new Properties();
        producerProps.put("bootstrap.servers", kafka.getBootstrapServers());
        producerProps.put("key.serializer", StringSerializer.class.getName());
        producerProps.put("value.serializer", StringSerializer.class.getName());
        
        try (KafkaProducer<String, String> producer = new KafkaProducer<>(producerProps)) {
            // 发送一条测试消息
            producer.send(new ProducerRecord<>(topic, "test-key", "test-value")).get();
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        // 创建消费者配置
        ConsumerConfig config = new ConsumerConfig(kafka.getBootstrapServers(), groupId);
        
        // 创建DataForgeKafkaConsumer
        DataForgeKafkaConsumer consumer = new DataForgeKafkaConsumer(config);
        
        // 订阅主题
        consumer.subscribe(topic);
        
        // 使用CountDownLatch等待消息处理
        CountDownLatch latch = new CountDownLatch(1);
        
        // 启动消费
        consumer.startConsuming(1000, record -> {
            System.out.println("Received record: " + record.key() + ", " + record.value());
            latch.countDown(); // 收到消息后减少计数
        });
        
        // 等待消息被处理
        boolean processed = latch.await(10, TimeUnit.SECONDS);
        
        // 停止消费者
        consumer.stopConsuming();
        
        // 验证消息已被处理
        assertTrue(processed, "消息应在规定时间内被处理");
    }
}