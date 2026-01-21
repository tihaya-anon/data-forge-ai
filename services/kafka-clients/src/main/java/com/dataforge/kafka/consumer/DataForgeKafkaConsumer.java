package com.dataforge.kafka.consumer;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.errors.WakeupException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CountDownLatch;

/**
 * DataForge Kafka消费者实现
 * 支持自动/手动offset管理，消费者组等功能
 */
public class DataForgeKafkaConsumer {
    
    private static final Logger logger = LoggerFactory.getLogger(DataForgeKafkaConsumer.class);
    
    private final KafkaConsumer<String, String> consumer;
    private final String groupId;
    private final boolean autoCommitEnabled;
    private volatile boolean running = false;
    private Thread consumeThread;
    
    public DataForgeKafkaConsumer(ConsumerConfig config) {
        this.consumer = new KafkaConsumer<>(config.getProperties());
        this.groupId = (String) config.getProperties().get(org.apache.kafka.clients.consumer.ConsumerConfig.GROUP_ID_CONFIG);
        this.autoCommitEnabled = Boolean.parseBoolean(
            (String) config.getProperties().get(org.apache.kafka.clients.consumer.ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG)
        );
        logger.info("Created Kafka consumer for group: {}", this.groupId);
    }
    
    /**
     * 订阅指定主题
     */
    public void subscribe(String... topics) {
        consumer.subscribe(java.util.Arrays.asList(topics));
        logger.info("Subscribed to topics: {}, group: {}", java.util.Arrays.toString(topics), this.groupId);
    }
    
    /**
     * 订阅指定主题列表
     */
    public void subscribe(Collection<String> topics) {
        consumer.subscribe(topics);
        logger.info("Subscribed to topics: {}, group: {}", topics, this.groupId);
    }
    
    /**
     * 开始消费消息，使用提供的处理器处理每条消息
     */
    public void startConsuming(int pollDurationMs, MessageHandler handler) {
        if (running) {
            logger.warn("Consumer is already running");
            return;
        }
        
        running = true;
        consumeThread = new Thread(() -> {
            try {
                while (running) {
                    try {
                        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(pollDurationMs));
                        
                        for (ConsumerRecord<String, String> record : records) {
                            try {
                                handler.handle(record);
                                
                                // 如果是手动提交，则在处理完消息后提交
                                if (!autoCommitEnabled) {
                                    Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
                                    offsets.put(new TopicPartition(record.topic(), record.partition()), 
                                              new OffsetAndMetadata(record.offset() + 1));
                                    consumer.commitSync(offsets);
                                }
                            } catch (Exception e) {
                                logger.error("Error processing message: {}", record.value(), e);
                                // 可以选择将失败的消息发送到死信队列
                                handleProcessingError(record, e);
                            }
                        }
                    } catch (WakeupException e) {
                        // 正常关闭时抛出的异常
                        if (!running) {
                            break;
                        }
                    } catch (Exception e) {
                        logger.error("Unexpected error during consumption", e);
                    }
                }
            } finally {
                try {
                    consumer.close();
                    logger.info("Consumer closed for group: {}", this.groupId);
                } catch (Exception e) {
                    logger.error("Error closing consumer", e);
                }
            }
        });
        
        consumeThread.start();
        logger.info("Started consuming messages for group: {}", this.groupId);
    }
    
    /**
     * 异步停止消费者
     */
    public void stopConsuming() {
        if (!running) {
            return;
        }
        
        running = false;
        consumer.wakeup(); // 唤醒轮询线程以便退出
        
        if (consumeThread != null && consumeThread.isAlive()) {
            try {
                consumeThread.join(5000); // 等待最多5秒让线程结束
            } catch (InterruptedException e) {
                logger.warn("Interrupted while waiting for consumer thread to finish", e);
                Thread.currentThread().interrupt();
            }
        }
        
        logger.info("Stopped consuming messages for group: {}", this.groupId);
    }
    
    /**
     * 手动提交当前offset
     */
    public void commitSync() {
        try {
            consumer.commitSync();
            logger.debug("Manually committed offsets for group: {}", this.groupId);
        } catch (Exception e) {
            logger.error("Error committing offsets for group: {}", this.groupId, e);
            throw e;
        }
    }
    
    /**
     * 异步提交当前offset
     */
    public void commitAsync() {
        consumer.commitAsync();
        logger.debug("Asynchronously committed offsets for group: {}", this.groupId);
    }
    
    /**
     * 处理消息处理错误
     */
    private void handleProcessingError(ConsumerRecord<String, String> record, Exception e) {
        // 这里可以实现将失败的消息发送到死信队列的逻辑
        logger.error("Sending failed message to DLQ: topic={}, partition={}, offset={}", 
                    record.topic(), record.partition(), record.offset());
    }
    
    /**
     * 消息处理器接口
     */
    @FunctionalInterface
    public interface MessageHandler {
        void handle(ConsumerRecord<String, String> record) throws Exception;
    }
    
    /**
     * 获取底层Kafka消费者实例（仅供测试使用）
     */
    protected KafkaConsumer<String, String> getConsumer() {
        return consumer;
    }
}