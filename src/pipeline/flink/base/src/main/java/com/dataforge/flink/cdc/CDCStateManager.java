package com.dataforge.flink.cdc;

import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;

import java.util.HashMap;
import java.util.Map;

/**
 * CDC状态管理器
 * 负责管理CDC作业中的各种状态信息
 */
public class CDCStateManager extends KeyedProcessFunction<String, String, String> {

    // 用于跟踪处理进度的状态
    private ValueState<Long> processedRecordsCount;
    private ValueState<Long> lastProcessedTimestamp;
    private ValueState<Map<String, Object>> tableOffsets;
    
    @Override
    public void open(Configuration parameters) throws Exception {
        super.open(parameters);
        
        // 初始化处理记录数状态
        ValueStateDescriptor<Long> processedRecordsCountDesc = 
            new ValueStateDescriptor<>("processedRecordsCount", TypeInformation.of(Long.class));
        processedRecordsCount = getRuntimeContext().getState(processedRecordsCountDesc);
        
        // 初始化最后处理时间戳状态
        ValueStateDescriptor<Long> lastProcessedTimestampDesc = 
            new ValueStateDescriptor<>("lastProcessedTimestamp", TypeInformation.of(Long.class));
        lastProcessedTimestamp = getRuntimeContext().getState(lastProcessedTimestampDesc);
        
        // 初始化表偏移量状态
        ValueStateDescriptor<Map<String, Object>> tableOffsetsDesc = 
            new ValueStateDescriptor<>("tableOffsets", TypeInformation.of(Map.class));
        tableOffsets = getRuntimeContext().getState(tableOffsetsDesc);
    }
    
    @Override
    public void processElement(String value, Context ctx, Collector<String> out) throws Exception {
        // 更新处理记录数
        Long currentCount = processedRecordsCount.value();
        if (currentCount == null) {
            currentCount = 0L;
        }
        currentCount++;
        processedRecordsCount.update(currentCount);
        
        // 更新最后处理时间戳
        lastProcessedTimestamp.update(System.currentTimeMillis());
        
        // 这里可以根据实际业务逻辑处理CDC事件
        // 比如解析JSON，提取变更类型等
        out.collect(value);
    }
    
    /**
     * 获取已处理记录数
     */
    public Long getProcessedRecordsCount() throws Exception {
        return processedRecordsCount.value();
    }
    
    /**
     * 获取最后处理时间戳
     */
    public Long getLastProcessedTimestamp() throws Exception {
        return lastProcessedTimestamp.value();
    }
    
    /**
     * 获取表偏移量状态
     */
    public Map<String, Object> getTableOffsets() throws Exception {
        Map<String, Object> offsets = tableOffsets.value();
        if (offsets == null) {
            offsets = new HashMap<>();
        }
        return offsets;
    }
    
    /**
     * 更新表偏移量
     */
    public void updateTableOffset(String table, Object offset) throws Exception {
        Map<String, Object> offsets = getTableOffsets();
        offsets.put(table, offset);
        tableOffsets.update(offsets);
    }
}