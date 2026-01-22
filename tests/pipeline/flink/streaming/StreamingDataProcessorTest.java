package tests.pipeline.flink.streaming;

import com.dataforge.flink.streaming.StreamingDataProcessor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.test.util.junit.extensions.FlinkMiniClusterExtension;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(FlinkMiniClusterExtension.class)
public class StreamingDataProcessorTest {

    @Test
    public void testDataFilter() throws Exception {
        // 创建测试数据
        List<String> inputData = Arrays.asList("valid data", "", "another valid data", null, "more data");

        // 创建流执行环境
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 创建数据流
        DataStream<String> source = env.fromCollection(inputData);
        
        // 应用过滤器
        DataStream<String> filteredStream = source.filter(new StreamingDataProcessor.DataFilter());
        
        // 收集结果
        List<String> result = filteredStream.collectAsync().join();
        
        // 验证结果 - 应该过滤掉空字符串和null值
        assertEquals(3, result.size());
        assertTrue(result.contains("valid data"));
        assertTrue(result.contains("another valid data"));
        assertTrue(result.contains("more data"));
    }

    @Test
    public void testDataCleaner() throws Exception {
        // 测试数据清洗功能
        String input = "  some data with non-ascii: ñç  ";
        
        StreamingDataProcessor.DataCleaner cleaner = new StreamingDataProcessor.DataCleaner();
        StreamingDataProcessor.ProcessedData result = cleaner.map(input);
        
        // 验证数据被正确清洗
        assertNotNull(result);
        assertNotNull(result.getKey());
        assertEquals("  some data with non-ascii: ", result.getValue()); // 非ASCII字符被移除
        assertTrue(result.getTimestamp() > 0);
    }

    @Test
    public void testAggregationFunction() throws Exception {
        // 测试聚合功能
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // 准备测试数据
        List<StreamingDataProcessor.ProcessedData> inputData = Arrays.asList(
            new StreamingDataProcessor.ProcessedData("key1", "value1", System.currentTimeMillis()),
            new StreamingDataProcessor.ProcessedData("key1", "value2", System.currentTimeMillis()),
            new StreamingDataProcessor.ProcessedData("key1", "value3", System.currentTimeMillis())
        );
        
        // 创建数据流
        DataStream<StreamingDataProcessor.ProcessedData> source = env.fromCollection(inputData);
        
        // 按键分组并应用窗口聚合
        DataStream<StreamingDataProcessor.AggregatedData> aggregatedStream = 
            source.keyBy(data -> data.getKey())
                  .window(org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows.of(
                      org.apache.flink.streaming.api.windowing.time.Time.seconds(1)))
                  .process(new StreamingDataProcessor.AggregationFunction());
        
        // 收集聚合结果
        List<StreamingDataProcessor.AggregatedData> result = aggregatedStream.collectAsync().join();
        
        // 验证聚合结果
        assertFalse(result.isEmpty());
        StreamingDataProcessor.AggregatedData aggregationResult = result.get(0);
        assertEquals("key1", aggregationResult.getKey());
        assertEquals(3, aggregationResult.getCount()); // 应该聚合了3条记录
    }
}