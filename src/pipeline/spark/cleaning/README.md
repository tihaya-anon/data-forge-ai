# 数据清洗Spark作业

此模块实现了用于数据清洗的Spark作业，主要包括以下几个功能：

## 功能特性

1. **文本规范化**：去除首尾空格，统一大小写
2. **特殊字符处理**：移除或替换特殊字符
3. **长度过滤**：过滤掉长度不在指定范围内的记录
4. **重复行检测与去除**：识别并去除重复记录

## 使用方法

```python
from src.pipeline.spark.cleaning import DataCleaningJob, create_cleaning_job
from src.pipeline.spark.base import SparkConfig
from pyspark.sql import DataFrame

# 方法1：使用默认配置创建作业
job = create_cleaning_job()
result = job.run(your_input_dataframe)
print(result)

# 方法2：自定义配置
config = SparkConfig(
    app_name="my-data-cleaning-job",
    master_url="yarn",
    executor_memory="4g",
    executor_cores=4,
    num_executors=4
)
job = DataCleaningJob(config, input_col="raw_text", output_col="cleaned_text")
result = job.run(your_input_dataframe)
print(result)
```

## 主要类和方法

### DataCleaningJob 类

- `normalize_text(df)` - 文本规范化
- `handle_special_characters(df)` - 特殊字符处理
- `length_filter(df, min_length, max_length)` - 长度过滤
- `remove_duplicates(df)` - 重复行检测与去除

### 辅助函数

- `create_cleaning_job(config=None)` - 创建数据清洗作业实例

## 输出结果

数据清洗作业会返回一个字典，包含以下统计信息：

- `initial_records` - 初始记录数
- `after_normalization` - 文本规范化后记录数
- `after_special_char_handling` - 特殊字符处理后记录数
- `after_length_filtering` - 长度过滤后记录数
- `unique_records` - 唯一记录数
- `duplicates_removed` - 移除的重复记录数
- `final_records` - 最终记录数
- `processed_successfully` - 是否处理成功