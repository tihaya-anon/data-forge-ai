package com.dataforge.kafka.consumer;

import org.apache.kafka.clients.consumer.ConsumerConfig as KafkaConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;

import java.util.Properties;

/**
 * Kafka Consumer配置类
 */
public class ConsumerConfig {
    
    private final Properties properties;
    
    public ConsumerConfig(String bootstrapServers, String groupId) {
        this.properties = new Properties();
        this.properties.put(KafkaConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        this.properties.put(KafkaConsumerConfig.GROUP_ID_CONFIG, groupId);
        this.properties.put(KafkaConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        this.properties.put(KafkaConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        this.properties.put(KafkaConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        this.properties.put(KafkaConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false"); // 默认手动提交
    }
    
    /**
     * 启用自动提交offset
     */
    public ConsumerConfig enableAutoCommit() {
        this.properties.put(KafkaConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "true");
        return this;
    }
    
    /**
     * 设置自动提交间隔（毫秒）
     */
    public ConsumerConfig setAutoCommitInterval(int intervalMs) {
        this.properties.put(KafkaConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, String.valueOf(intervalMs));
        return this;
    }
    
    /**
     * 设置session超时时间（毫秒）
     */
    public ConsumerConfig setSessionTimeout(int timeoutMs) {
        this.properties.put(KafkaConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, String.valueOf(timeoutMs));
        return this;
    }
    
    /**
     * 设置心跳间隔（毫秒）
     */
    public ConsumerConfig setHeartbeatInterval(int heartbeatIntervalMs) {
        this.properties.put(KafkaConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, String.valueOf(heartbeatIntervalMs));
        return this;
    }
    
    public Properties getProperties() {
        return this.properties;
    }
}