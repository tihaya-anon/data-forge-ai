package com.dataforge.flink.cdc;

import org.apache.flink.configuration.Configuration;

import java.util.Properties;

/**
 * CDC作业配置类
 * 管理CDC作业的各种配置参数
 */
public class CDCConfiguration {
    
    private Configuration flinkConfig;
    private Properties cdcProperties;
    private String databaseUrl;
    private String databaseUser;
    private String databasePassword;
    private String tableName;
    private String kafkaBootstrapServers;
    private String outputTopic;
    
    public CDCConfiguration() {
        this.flinkConfig = new Configuration();
        this.cdcProperties = new Properties();
    }
    
    /**
     * 获取Flink配置
     */
    public Configuration getFlinkConfiguration() {
        return flinkConfig;
    }
    
    /**
     * 获取CDC连接属性
     */
    public Properties getCdcProperties() {
        return cdcProperties;
    }
    
    /**
     * 设置数据库连接参数
     */
    public CDCConfiguration setDatabaseConnection(String url, String user, String password) {
        this.databaseUrl = url;
        this.databaseUser = user;
        this.databasePassword = password;
        return this;
    }
    
    /**
     * 设置表名
     */
    public CDCConfiguration setTableName(String tableName) {
        this.tableName = tableName;
        return this;
    }
    
    /**
     * 设置Kafka输出参数
     */
    public CDCConfiguration setKafkaOutput(String bootstrapServers, String topic) {
        this.kafkaBootstrapServers = bootstrapServers;
        this.outputTopic = topic;
        return this;
    }
    
    /**
     * 获取数据库URL
     */
    public String getDatabaseUrl() {
        return databaseUrl;
    }
    
    /**
     * 获取数据库用户名
     */
    public String getDatabaseUser() {
        return databaseUser;
    }
    
    /**
     * 获取数据库密码
     */
    public String getDatabasePassword() {
        return databasePassword;
    }
    
    /**
     * 获取表名
     */
    public String getTableName() {
        return tableName;
    }
    
    /**
     * 获取Kafka引导服务器
     */
    public String getKafkaBootstrapServers() {
        return kafkaBootstrapServers;
    }
    
    /**
     * 获取输出主题
     */
    public String getOutputTopic() {
        return outputTopic;
    }
}