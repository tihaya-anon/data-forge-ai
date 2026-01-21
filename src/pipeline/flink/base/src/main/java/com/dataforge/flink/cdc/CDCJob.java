package com.dataforge.flink.cdc;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.restartstrategy.RestartStrategies;
import org.apache.flink.api.common.time.Time;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.CheckpointConfig;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;
import java.util.concurrent.TimeUnit;

/**
 * Flink CDC作业主类
 * 用于处理变更数据捕获(CDC)任务
 */
public class CDCJob {
    
    private static final Logger logger = LoggerFactory.getLogger(CDCJob.class);
    
    public static void main(String[] args) throws Exception {
        // 创建流执行环境
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 配置环境参数
        configureEnvironment(env);
        
        // 设置检查点
        configureCheckpoint(env);
        
        // 设置重启策略
        configureRestartStrategy(env);
        
        // 创建CDC源
        DataStreamSource<String> source = createCdcSource(env);
        
        // 添加水印策略
        DataStreamSource<String> streamWithWatermarks = source.assignTimestampsAndWatermarks(
                WatermarkStrategy.<String>forMonotonousTimestamps()
                        .withTimestampAssigner((event, timestamp) -> System.currentTimeMillis())
        );
        
        // 输出到Kafka
        KafkaSink<String> kafkaSink = createKafkaSink();
        streamWithWatermarks.sinkTo(kafkaSink);
        
        // 执行作业
        logger.info("Starting CDC Job...");
        env.execute("DataForge Flink CDC Job");
    }

    /**
     * 配置流执行环境
     */
    private static void configureEnvironment(StreamExecutionEnvironment env) {
        // 启用并行执行
        env.setParallelism(2);
        
        // 全局配置
        Properties props = new Properties();
        props.setProperty("pipeline.name", "DataForge CDC Pipeline");
        
        // 设置其他配置
        env.getConfig().setGlobalJobParameters(props);
        logger.info("StreamExecutionEnvironment configured successfully");
    }

    /**
     * 配置检查点
     */
    private static void configureCheckpoint(StreamExecutionEnvironment env) {
        // 启用检查点
        env.enableCheckpointing(5000); // 每5秒进行一次检查点
        
        CheckpointConfig checkpointConfig = env.getCheckpointConfig();
        checkpointConfig.setCheckpointingMode(org.apache.flink.streaming.api.checkpoint.CheckpointingMode.EXACTLY_ONCE);
        checkpointConfig.setMinPauseBetweenCheckpoints(2000);
        checkpointConfig.setCheckpointTimeout(10000);
        checkpointConfig.setMaxConcurrentCheckpoints(1);
        checkpointConfig.enableExternalizedCheckpoints(
                CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
        );
        
        logger.info("Checkpoint configured successfully");
    }

    /**
     * 配置重启策略
     */
    private static void configureRestartStrategy(StreamExecutionEnvironment env) {
        // 设置固定延迟重启策略
        env.setRestartStrategy(RestartStrategies.fixedDelayRestart(
                3, // 尝试重启次数
                Time.of(10, TimeUnit.SECONDS) // 重启间隔
        ));
        
        logger.info("Restart strategy configured successfully");
    }

    /**
     * 创建CDC源
     */
    private static DataStreamSource<String> createCdcSource(StreamExecutionEnvironment env) {
        // 这里我们创建一个模拟的CDC源，实际实现会连接到数据库的变更日志
        // 在真实场景中，这里会是类似Debezium连接器的实现
        
        logger.info("Creating CDC source...");
        
        // 为了演示目的，返回一个简单的源
        // 在实际实现中，这里会连接到MySQL、PostgreSQL等数据库的CDC源
        return env.fromCollection(java.util.Arrays.asList("Sample CDC event"));
    }

    /**
     * 创建Kafka Sink
     */
    private static KafkaSink<String> createKafkaSink() {
        return KafkaSink.<String>builder()
                .setBootstrapServers("localhost:9092") // 在生产环境中应从配置获取
                .setRecordSerializer(org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema.builder()
                        .setTopic("cdc-output-topic")
                        .setValueSerializationSchema(new org.apache.flink.api.common.serialization.SimpleStringSchema())
                        .build()
                )
                .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
                .build();
    }
}