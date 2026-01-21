"""
Example usage of the quality filtering module for DataForge AI platform.
Demonstrates how to use the quality filtering components together.
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType
from .quality_filter import QualityFilter


def create_sample_data(spark):
    """
    Create sample data for demonstration purposes
    
    Args:
        spark: Spark session instance
        
    Returns:
        Sample DataFrame with text data
    """
    # Define sample data
    sample_texts = [
        "This is a high quality text with good information and structure.",
        "This text contains some toxic words like hate and stupid.",
        "Short text.",
        "This is another good quality text with useful information for the reader.",
        "A very very very very very repetitive text text text that doesn't add much value value value.",
        "This text has lots of CAPS LOCK WORDS and EXCLAMATIONS!!!",
        "Normal text with standard quality and average information value."
    ]
    
    # Create DataFrame
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("text", StringType(), True)
    ])
    
    rows = [(str(i), text) for i, text in enumerate(sample_texts)]
    df = spark.createDataFrame(rows, schema)
    
    return df


def main():
    """
    Main function demonstrating the quality filtering module
    """
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("DataForge AI - Quality Filtering Example") \
        .master("local[*]") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    # Configuration for quality filtering
    config = {
        'max_toxicity': 0.5,          # Max allowed toxicity score
        'min_quality_score': 0.3,     # Min required quality score
        'max_perplexity': 1000.0      # Max allowed perplexity
    }
    
    # Initialize quality filter
    quality_filter = QualityFilter(spark, config)
    
    # Create sample data
    print("Creating sample data...")
    df = create_sample_data(spark)
    
    print("\nOriginal data:")
    df.show(truncate=False)
    
    # Apply quality filters
    print("\nApplying quality filters...")
    filtered_df = quality_filter.apply_filters(df, 'text')
    
    print("\nFiltered data (only high-quality entries):")
    filtered_df.show(truncate=False)
    
    # Generate quality report
    print("\nGenerating quality report...")
    report = quality_filter.get_quality_report(df, 'text')
    
    print(f"\nQuality Report:")
    print(f"- Total documents: {report['total_documents']}")
    print(f"- Passed documents: {report['passed_documents']}")
    print(f"- Pass rate: {report['pass_rate']:.2%}")
    print(f"- Average perplexity: {report['avg_perplexity']:.2f}")
    print(f"- Average toxicity: {report['avg_toxicity']:.2f}")
    print(f"- Average quality score: {report['avg_quality_score']:.2f}")
    
    # Stop Spark session
    spark.stop()
    
    print("\nQuality filtering example completed successfully!")


if __name__ == "__main__":
    main()