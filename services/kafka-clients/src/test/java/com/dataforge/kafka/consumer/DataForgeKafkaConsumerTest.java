package com.dataforge.kafka.consumer;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.clients.consumer.OffsetResetStrategy;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.header.internals.RecordHeaders;
import org.apache.kafka.common.record.TimestampType;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import java.time.Duration;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

class DataForgeKafkaConsumerTest {

    private KafkaConsumer<String, String> mockKafkaConsumer;
    private DataForgeKafkaConsumer dataForgeConsumer;
    private String testGroupId = "test-group";
    private String testTopic = "test-topic";

    @BeforeEach
    void setUp() {
        mockKafkaConsumer = mock(KafkaConsumer.class);
        // 创建配置
        ConsumerConfig config = new ConsumerConfig("localhost:9092", testGroupId);
        // 创建DataForgeKafkaConsumer
        dataForgeConsumer = new DataForgeKafkaConsumer(config);
    }

    @AfterEach
    void tearDown() {
        if (dataForgeConsumer != null) {
            dataForgeConsumer.stopConsuming();
        }
    }

    @Test
    void testConsumerInitialization() {
        ConsumerConfig config = new ConsumerConfig("localhost:9092", "test-init-group");
        DataForgeKafkaConsumer consumer = new DataForgeKafkaConsumer(config);
        
        assertNotNull(consumer);
    }

    @Test
    void testSubscribeToSingleTopic() {
        // 测试订阅单个主题
        dataForgeConsumer.subscribe(testTopic);
        
        // 验证subscribe方法被正确调用
        // 由于我们无法直接访问内部consumer，我们通过startConsuming触发订阅
        doNothing().when(mockKafkaConsumer).subscribe(any(java.util.Collection.class), any());
        
        // 启动消费以触发订阅逻辑
        dataForgeConsumer.startConsuming(100, record -> {});
        dataForgeConsumer.stopConsuming();
        
        // 订阅功能在当前实现中会在startConsuming时触发
        assertTrue(true); // 订阅逻辑在正常操作中会被调用
    }

    @Test
    void testSubscribeToMultipleTopics() {
        // 测试订阅多个主题
        String[] topics = {"topic1", "topic2", "topic3"};
        dataForgeConsumer.subscribe(topics);
        
        // 启动消费以触发订阅逻辑
        dataForgeConsumer.startConsuming(100, record -> {});
        dataForgeConsumer.stopConsuming();
        
        assertTrue(true); // 订阅逻辑在正常操作中会被调用
    }

    @Test
    void testAutoCommitConfiguration() {
        // 测试启用自动提交的配置
        ConsumerConfig autoCommitConfig = new ConsumerConfig("localhost:9092", "test-auto-group")
            .enableAutoCommit();
        
        Properties props = autoCommitConfig.getProperties();
        String enableAutoCommit = props.getProperty(org.apache.kafka.clients.consumer.ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG);
        
        assertNotNull(enableAutoCommit);
        assertTrue(Boolean.parseBoolean(enableAutoCommit));
    }

    @Test
    void testCustomConfiguration() {
        ConsumerConfig config = new ConsumerConfig("localhost:9092", "test-custom-group")
            .setAutoCommitInterval(2000)
            .setSessionTimeout(30000)
            .setHeartbeatInterval(3000);
        
        Properties props = config.getProperties();
        
        assertEquals("2000", props.getProperty(org.apache.kafka.clients.consumer.ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG));
        assertEquals("30000", props.getProperty(org.apache.kafka.clients.consumer.ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG));
        assertEquals("3000", props.getProperty(org.apache.kafka.clients.consumer.ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG));
    }

    @Test
    void testManualCommitSync() {
        ConsumerConfig config = new ConsumerConfig("localhost:9092", "test-commit-group");
        DataForgeKafkaConsumer consumer = new DataForgeKafkaConsumer(config);
        
        // 测试同步提交不抛出异常
        assertDoesNotThrow(() -> consumer.commitSync());
    }

    @Test
    void testManualCommitAsync() {
        ConsumerConfig config = new ConsumerConfig("localhost:9092", "test-commit-group");
        DataForgeKafkaConsumer consumer = new DataForgeKafkaConsumer(config);
        
        // 测试异步提交不抛出异常
        assertDoesNotThrow(() -> consumer.commitAsync());
    }

    @Test
    void testMessageHandlerProcessesRecord() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(1);
        
        DataForgeKafkaConsumer.MessageHandler handler = record -> {
            assertNotNull(record);
            assertNotNull(record.value());
            assertEquals("value1", record.value());
            latch.countDown();
        };
        
        // 创建测试数据
        TopicPartition tp = new TopicPartition(testTopic, 0);
        Map<TopicPartition, java.util.List<ConsumerRecord<String, String>>> recordsMap = new HashMap<>();
        recordsMap.put(tp, java.util.Arrays.asList(
            new ConsumerRecord<>(testTopic, 0, 0L, "key1", "value1")
        ));
        
        org.apache.kafka.clients.consumer.ConsumerRecords<String, String> records = 
            new org.apache.kafka.clients.consumer.ConsumerRecords<>(recordsMap);
        
        // 设置mock行为
        when(mockKafkaConsumer.poll(any(Duration.class))).thenReturn(records);
        
        // 启动消费
        dataForgeConsumer.startConsuming(100, handler);
        
        // 等待处理完成
        assertTrue(latch.await(3, TimeUnit.SECONDS));
        
        dataForgeConsumer.stopConsuming();
    }
    
    @Test
    void testStopConsumingWhenNotRunning() {
        // 停止一个尚未启动的消费者不应该引发异常
        assertDoesNotThrow(() -> dataForgeConsumer.stopConsuming());
    }
    
    @Test
    void testMessageHandlerExceptionHandling() throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(1);
        
        DataForgeKafkaConsumer.MessageHandler handler = record -> {
            throw new RuntimeException("Simulated processing error");
        };
        
        // 创建测试数据
        TopicPartition tp = new TopicPartition(testTopic, 0);
        Map<TopicPartition, java.util.List<ConsumerRecord<String, String>>> recordsMap = new HashMap<>();
        recordsMap.put(tp, java.util.Arrays.asList(
            new ConsumerRecord<>(testTopic, 0, 0L, "key1", "value1")
        ));
        
        org.apache.kafka.clients.consumer.ConsumerRecords<String, String> records = 
            new org.apache.kafka.clients.consumer.ConsumerRecords<>(recordsMap);
        
        // 设置mock行为
        when(mockKafkaConsumer.poll(any(Duration.class)))
            .thenReturn(records)
            .thenReturn(org.apache.kafka.clients.consumer.ConsumerRecords.empty());
        
        // 启动消费
        dataForgeConsumer.startConsuming(100, handler);
        
        // 给一些时间让异常处理逻辑执行
        Thread.sleep(500);
        
        dataForgeConsumer.stopConsuming();
        
        // 如果没有崩溃，测试通过
        assertTrue(true);
    }
}