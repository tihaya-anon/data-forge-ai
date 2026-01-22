package com.dataforge.flink.streaming;

import org.apache.flink.configuration.Configuration;

import java.util.Properties;

/**
 * 实时数据处理作业配置类
 * 管理流处理作业的各种配置参数
 */
public class StreamingJobConfig {
    
    private Configuration flinkConfig;
    private Properties streamingProperties;
    private String sourceTopic;
    private String sinkTopic;
    private String kafkaBootstrapServers;
    private String milvusUri;
    private String milvusCollection;
    private int windowSizeSeconds;
    private int parallelism;
    
    public StreamingJobConfig() {
        this.flinkConfig = new Configuration();
        this.streamingProperties = new Properties();
        // 默认窗口大小为10秒
        this.windowSizeSeconds = 10;
        // 默认并行度为2
        this.parallelism = 2;
    }
    
    /**
     * 获取Flink配置
     */
    public Configuration getFlinkConfiguration() {
        return flinkConfig;
    }
    
    /**
     * 获取流处理属性
     */
    public Properties getStreamingProperties() {
        return streamingProperties;
    }
    
    /**
     * 设置Kafka源和目标主题
     */
    public StreamingJobConfig setKafkaTopics(String sourceTopic, String sinkTopic) {
        this.sourceTopic = sourceTopic;
        this.sinkTopic = sinkTopic;
        return this;
    }
    
    /**
     * 设置Kafka服务器地址
     */
    public StreamingJobConfig setKafkaBootstrapServers(String kafkaBootstrapServers) {
        this.kafkaBootstrapServers = kafkaBootstrapServers;
        return this;
    }
    
    /**
     * 设置Milvus配置
     */
    public StreamingJobConfig setMilvusConfig(String milvusUri, String milvusCollection) {
        this.milvusUri = milvusUri;
        this.milvusCollection = milvusCollection;
        return this;
    }
    
    /**
     * 设置窗口大小（秒）
     */
    public StreamingJobConfig setWindowSizeSeconds(int windowSizeSeconds) {
        this.windowSizeSeconds = windowSizeSeconds;
        return this;
    }
    
    /**
     * 设置并行度
     */
    public StreamingJobConfig setParallelism(int parallelism) {
        this.parallelism = parallelism;
        return this;
    }
    
    /**
     * 获取源主题
     */
    public String getSourceTopic() {
        return sourceTopic;
    }
    
    /**
     * 获取目标主题
     */
    public String getSinkTopic() {
        return sinkTopic;
    }
    
    /**
     * 获取Kafka引导服务器
     */
    public String getKafkaBootstrapServers() {
        return kafkaBootstrapServers;
    }
    
    /**
     * 获取Milvus URI
     */
    public String getMilvusUri() {
        return milvusUri;
    }
    
    /**
     * 获取Milvus集合名称
     */
    public String getMilvusCollection() {
        return milvusCollection;
    }
    
    /**
     * 获取窗口大小（秒）
     */
    public int getWindowSizeSeconds() {
        return windowSizeSeconds;
    }
    
    /**
     * 获取并行度
     */
    public int getParallelism() {
        return parallelism;
    }
}