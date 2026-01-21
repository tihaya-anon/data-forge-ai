# Quality Filtering Module

This module provides comprehensive text quality filtering capabilities for the DataForge AI platform. It includes components for perplexity calculation, toxicity detection, and quality scoring.

## Components

### 1. Perplexity Calculator
Uses KenLM for calculating text perplexity. Perplexity measures how well a probability model predicts a sample. Lower perplexity indicates better fluency and coherence.

#### Features:
- Supports loading custom KenLM models
- Fallback heuristic implementation when KenLM is unavailable
- Batch processing capability

### 2. Toxicity Detector
Detects toxic content in text using pattern matching and ML-based approaches.

#### Features:
- Pattern-based toxicity detection
- Support for ML model integration (e.g., transformer-based classifiers)
- Threshold-based classification
- Batch processing capability

### 3. Quality Scorer
Calculates text quality using fastText models or heuristic approaches.

#### Features:
- Supports loading fastText models
- Heuristic-based scoring when ML models unavailable
- Quality classification (low/medium/high)
- Batch processing capability

### 4. Quality Filter (Main Orchestrator)
Combines all quality components into a unified filtering pipeline.

#### Features:
- Applies all quality checks to Spark DataFrames
- Configurable thresholds for filtering
- Quality reporting capabilities
- Integration with Spark UDFs for distributed processing

## Installation

The module requires the following dependencies:

```bash
pip install pyspark
pip install kenlm  # Optional: for perplexity calculation
pip install fasttext  # Optional: for quality scoring
pip install transformers torch  # Optional: for toxicity detection
```

## Usage

### Basic Usage

```python
from pyspark.sql import SparkSession
from src.pipeline.spark.quality import QualityFilter

# Initialize Spark session
spark = SparkSession.builder.appName("Quality Filter").getOrCreate()

# Configuration
config = {
    'max_toxicity': 0.5,          # Max allowed toxicity score
    'min_quality_score': 0.3,     # Min required quality score
    'max_perplexity': 1000.0      # Max allowed perplexity
}

# Initialize quality filter
quality_filter = QualityFilter(spark, config)

# Apply filters to your DataFrame
filtered_df = quality_filter.apply_filters(your_dataframe, 'text_column')

# Generate quality report
report = quality_filter.get_quality_report(your_dataframe, 'text_column')
```

### Example Usage

Run the example script to see the module in action:

```bash
cd /path/to/project
python -m src.pipeline.spark.quality.example_usage
```

## Testing

Run the unit tests:

```bash
python -m pytest tests/pipeline/spark/quality/test_quality_filter.py -v
```

## Configuration

The quality filter accepts the following configuration options:

- `max_toxicity`: Maximum allowed toxicity score (0.0-1.0)
- `min_quality_score`: Minimum required quality score (0.0-1.0)
- `max_perplexity`: Maximum allowed perplexity value

## Performance Considerations

- The quality filter is designed to work with Spark DataFrames for distributed processing
- ML-based components can be computationally expensive; consider using cluster resources
- For large datasets, consider partitioning strategies to optimize performance

## Extensibility

The module is designed to be extensible:

- New quality metrics can be added by implementing the appropriate interfaces
- Custom models can be integrated by modifying the individual components
- Thresholds and rules can be adjusted through configuration