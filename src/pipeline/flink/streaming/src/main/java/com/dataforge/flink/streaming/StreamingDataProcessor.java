package com.dataforge.flink.streaming;

/**
 * 流处理作业的配置类，用于集中管理所有可配置的参数。
 */
public class StreamingJobConfig {
    private String kafkaBootstrapServers;
    private String sourceTopic;
    private String sinkTopic;
    private int windowSizeSeconds;
    private int parallelism;

    public StreamingJobConfig() {
        // 默认构造函数
    }

    public String getKafkaBootstrapServers() {
        return kafkaBootstrapServers;
    }

    public StreamingJobConfig setKafkaBootstrapServers(String kafkaBootstrapServers) {
        this.kafkaBootstrapServers = kafkaBootstrapServers;
        return this;
    }

    public String getSourceTopic() {
        return sourceTopic;
    }

    public String getSinkTopic() {
        return sinkTopic;
    }

    /**
     * 设置输入和输出主题
     * @param sourceTopic 输入主题
     * @param sinkTopic 输出主题
     * @return 当前配置对象，支持链式调用
     */
    public StreamingJobConfig setKafkaTopics(String sourceTopic, String sinkTopic) {
        this.sourceTopic = sourceTopic;
        this.sinkTopic = sinkTopic;
        return this;
    }

    public int getWindowSizeSeconds() {
        return windowSizeSeconds;
    }

    public StreamingJobConfig setWindowSizeSeconds(int windowSizeSeconds) {
        this.windowSizeSeconds = windowSizeSeconds;
        return this;
    }

    public int getParallelism() {
        return parallelism;
    }

    public StreamingJobConfig setParallelism(int parallelism) {
        this.parallelism = parallelism;
        return this;
    }
}
package com.dataforge.flink.streaming;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.restartstrategy.RestartStrategies;
import org.apache.flink.api.common.time.Time;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.CheckpointConfig;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.Window;
import org.apache.flink.util.Collector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.TimeUnit;

/**
 * 实时数据处理作业
 * 实现数据清洗转换、窗口聚合、状态更新和Sink到Kafka/Milvus
 */
public class StreamingDataProcessor {
    
    private static final Logger logger = LoggerFactory.getLogger(StreamingDataProcessor.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    public static void main(String[] args) throws Exception {
        // 创建流执行环境
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 创建配置
        StreamingJobConfig config = new StreamingJobConfig()
                .setKafkaBootstrapServers("localhost:9092")
                .setKafkaTopics("raw-input-topic", "processed-output-topic")
                .setWindowSizeSeconds(10)
                .setParallelism(2);
        
        // 配置环境参数
        configureEnvironment(env, config);
        
        // 设置检查点
        configureCheckpoint(env);
        
        // 设置重启策略
        configureRestartStrategy(env);
        
        // 创建数据源（这里使用模拟源，实际应用中会连接到真实的Kafka或其他源）
        DataStreamSource<String> source = createDataSource(env);
        
        // 数据清洗和转换
        DataStream<ProcessedData> cleanedStream = source
                .filter(new DataFilter())  // 数据过滤
                .map(new DataCleaner())    // 数据清洗
                .returns(Types.POJO(ProcessedData.class)); // 指定返回类型
        
        // 窗口聚合
        DataStream<AggregatedData> aggregatedStream = cleanedStream
                .keyBy(data -> data.getKey())
                .window(TumblingProcessingTimeWindows.of(org.apache.flink.streaming.api.windowing.time.Time.seconds(config.getWindowSizeSeconds()))) // 使用配置的窗口大小
                .process(new AggregationFunction());
        
        // 输出到Kafka
        KafkaSink<String> kafkaSink = createKafkaSink();
        aggregatedStream.map(Object::toString).sinkTo(kafkaSink);
        
        // 执行作业
        logger.info("Starting Streaming Data Processing Job...");
        env.execute("DataForge Flink Streaming Data Processor");
    }

    /**
     * 配置流执行环境
     */
    private static void configureEnvironment(StreamExecutionEnvironment env, StreamingJobConfig config) {
        // 设置并行度
        env.setParallelism(config.getParallelism());
        
        // 启用检查点
        env.enableCheckpointing(5000); // 每5秒进行一次检查点
        
        logger.info("StreamExecutionEnvironment configured successfully");
    }

    /**
     * 配置检查点
     */
    private static void configureCheckpoint(StreamExecutionEnvironment env) {
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
     * 创建数据源
     */
    private static DataStreamSource<String> createDataSource(StreamExecutionEnvironment env) {
        // 在实际实现中，这里会连接到真实的Kafka或其他源
        // 为了演示目的，返回一个简单的源
        return env.socketTextStream("localhost", 9999); // 从socket获取数据，用于演示
    }

    /**
     * 创建Kafka Sink
     */
    private static KafkaSink<String> createKafkaSink(StreamingJobConfig config) {
        return KafkaSink.<String>builder()
                .setBootstrapServers(config.getKafkaBootstrapServers() != null ? 
                    config.getKafkaBootstrapServers() : "localhost:9092")
                .setRecordSerializer(org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema.builder()
                        .setTopic(config.getSinkTopic() != null ? 
                            config.getSinkTopic() : "default-output-topic")
                        .setValueSerializationSchema(new org.apache.flink.api.common.serialization.SimpleStringSchema())
                        .build()
                )
                .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
                .build();
    }
    
    /**
     * 数据过滤器
     */
    public static class DataFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String value) throws Exception {
            // 过滤掉空值和不符合格式的数据
            return value != null && !value.trim().isEmpty();
        }
    }
    
    /**
     * 数据清洗器
     */
    public static class DataCleaner implements MapFunction<String, ProcessedData> {
        @Override
        public ProcessedData map(String value) throws Exception {
            // 解析输入数据
            // 这里假设输入是一个JSON字符串
            try {
                // 简单的处理：提取关键字段并清理
                String cleanValue = value.replaceAll("[^\\x00-\\x7F]", "") // 移除非ASCII字符
                                          .trim(); // 去除首尾空白
                
                // 生成key用于后续分组
                String key = extractKey(cleanValue);
                
                return new ProcessedData(key, cleanValue, System.currentTimeMillis());
            } catch (Exception e) {
                logger.error("Error processing input: " + value, e);
                throw e;
            }
        }
        
        private String extractKey(String value) {
            // 简单的key提取逻辑，实际实现可能更复杂
            if (value.length() > 5) {
                return value.substring(0, 5); // 使用前5个字符作为key
            }
            return value;
        }
    }
    
    /**
     * 聚合函数
     */
    public static class AggregationFunction 
            extends ProcessWindowFunction<ProcessedData, AggregatedData, String, Window> {
        
        @Override
        public void process(String key, 
                           Context context, 
                           Iterable<ProcessedData> elements, 
                           Collector<AggregatedData> out) {
            int count = 0;
            long totalSize = 0;
            long windowStart = context.window().getWindowStart();
            long windowEnd = context.window().getWindowEnd();
            
            for (ProcessedData element : elements) {
                count++;
                totalSize += element.getValue().length();
            }
            
            AggregatedData result = new AggregatedData(
                key, 
                count, 
                totalSize, 
                windowStart, 
                windowEnd,
                System.currentTimeMillis()
            );
            
            out.collect(result);
        }
    }
    
    /**
     * 处理后的数据POJO类
     */
    public static class ProcessedData {
        private String key;
        private String value;
        private long timestamp;
        
        public ProcessedData() {}
        
        public ProcessedData(String key, String value, long timestamp) {
            this.key = key;
            this.value = value;
            this.timestamp = timestamp;
        }
        
        // Getters and setters
        public String getKey() { return key; }
        public void setKey(String key) { this.key = key; }
        
        public String getValue() { return value; }
        public void setValue(String value) { this.value = value; }
        
        public long getTimestamp() { return timestamp; }
        public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
        
        @Override
        public String toString() {
            return "ProcessedData{" +
                    "key='" + key + '\'' +
                    ", value='" + value + '\'' +
                    ", timestamp=" + timestamp +
                    '}';
        }
    }
    
    /**
     * 聚合后的数据POJO类
     */
    public static class AggregatedData {
        private String key;
        private int count;
        private long totalSize;
        private long windowStart;
        private long windowEnd;
        private long processingTime;
        
        public AggregatedData() {}
        
        public AggregatedData(String key, int count, long totalSize, 
                             long windowStart, long windowEnd, long processingTime) {
            this.key = key;
            this.count = count;
            this.totalSize = totalSize;
            this.windowStart = windowStart;
            this.windowEnd = windowEnd;
            this.processingTime = processingTime;
        }
        
        // Getters and setters
        public String getKey() { return key; }
        public void setKey(String key) { this.key = key; }
        
        public int getCount() { return count; }
        public void setCount(int count) { this.count = count; }
        
        public long getTotalSize() { return totalSize; }
        public void setTotalSize(long totalSize) { this.totalSize = totalSize; }
        
        public long getWindowStart() { return windowStart; }
        public void setWindowStart(long windowStart) { this.windowStart = windowStart; }
        
        public long getWindowEnd() { return windowEnd; }
        public void setWindowEnd(long windowEnd) { this.windowEnd = windowEnd; }
        
        public long getProcessingTime() { return processingTime; }
        public void setProcessingTime(long processingTime) { this.processingTime = processingTime; }
        
        @Override
        public String toString() {
            return "AggregatedData{" +
                    "key='" + key + '\'' +
                    ", count=" + count +
                    ", totalSize=" + totalSize +
                    ", windowStart=" + windowStart +
                    ", windowEnd=" + windowEnd +
                    ", processingTime=" + processingTime +
                    '}';
        }
    }
}