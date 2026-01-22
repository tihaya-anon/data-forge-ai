package com.dataforge.flink.streaming;

import org.apache.flink.api.connector.sink2.Sink;
import org.apache.flink.api.connector.sink2.SinkWriter;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSink;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.io.IOException;
import java.util.Collection;

/**
 * Kafka到Milvus的Sink实现
 * 将聚合后的数据同时输出到Kafka和Milvus
 */
public class KafkaToMilvusSink {
    
    private final StreamingJobConfig config;
    private final ObjectMapper objectMapper;
    
    public KafkaToMilvusSink(StreamingJobConfig config) {
        this.config = config;
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * 添加Kafka和Milvus Sink到数据流
     */
    public <T> void addToDataStream(DataStream<T> dataStream) {
        // 创建Kafka Sink
        KafkaSink<T> kafkaSink = createKafkaSink();
        
        // 将数据流输出到Kafka
        dataStream.sinkTo(kafkaSink);
        
        // TODO: 在实际部署时，需要实现Milvus Sink
        // 由于Milvus连接器可能需要额外的依赖，这里暂时只实现Kafka输出
        // 可以使用Milvus FLINK connector或者自定义SinkWriter
    }
    
    /**
     * 创建Kafka Sink
     */
    private <T> KafkaSink<T> createKafkaSink() {
        KafkaRecordSerializationSchema<T> serializationSchema = KafkaRecordSerializationSchema.builder()
                .setTopic(config.getSinkTopic() != null ? config.getSinkTopic() : "default-output-topic")
                .setValueSerializationSchema(new org.apache.flink.api.common.serialization.SimpleStringSchema())
                .build();
        
        return KafkaSink.<T>builder()
                .setBootstrapServers(config.getKafkaBootstrapServers() != null ? 
                    config.getKafkaBootstrapServers() : "localhost:9092")
                .setRecordSerializer(serializationSchema)
                .setDeliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
                .build();
    }
    
    /**
     * 创建Milvus Sink Writer
     * 这是一个抽象概念，在实际实现中需要根据Milvus的客户端API来实现
     */
    public static class MilvusSinkWriter<T> implements SinkWriter<T, Void, Void> {
        private final StreamingJobConfig config;
        private final ObjectMapper objectMapper;
        
        public MilvusSinkWriter(StreamingJobConfig config, SinkWriterInitializationContext<Void> context) {
            this.config = config;
            this.objectMapper = new ObjectMapper();
        }
        
        @Override
        public void write(T element, Context context) throws IOException, InterruptedException {
            // 在实际实现中，这里会连接到Milvus并将数据插入到指定集合
            // 示例伪代码:
            // MilvusClient client = new MilvusClient(...);
            // InsertRequest insertReq = InsertRequest.newBuilder()
            //     .withCollectionName(config.getMilvusCollection())
            //     .withFields(...)
            //     .build();
            // client.insert(insertReq);
            
            System.out.println("Would insert to Milvus: " + element.toString());
        }
        
        @Override
        public void flush(boolean endOfInput) throws IOException, InterruptedException {
            // 刷新缓冲区
        }
        
        @Override
        public void close() throws Exception {
            // 关闭连接
        }
    }
}