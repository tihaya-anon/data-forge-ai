"""
Quality filtering module for DataForge AI platform.
Implements a comprehensive filter system that applies various quality checks.
"""
import logging
from typing import List, Dict, Any, Optional
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, udf
from pyspark.sql.types import BooleanType, DoubleType

from .perplexity_calculator import PerplexityCalculator
from .toxicity_detector import ToxicityDetector
from .quality_scorer import QualityScorer


class QualityFilter:
    """
    Main quality filtering class that orchestrates various quality checks
    including perplexity calculation, toxicity detection, and quality scoring.
    """

    def __init__(self, spark_session, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the quality filter with required components
        
        Args:
            spark_session: Spark session instance
            config: Optional configuration dictionary
        """
        self.spark = spark_session
        self.config = config or {}
        
        # Initialize sub-components
        self.perplexity_calculator = PerplexityCalculator()
        self.toxicity_detector = ToxicityDetector()
        self.quality_scorer = QualityScorer()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Default thresholds
        self.thresholds = {
            'max_toxicity': self.config.get('max_toxicity', 0.5),
            'min_quality_score': self.config.get('min_quality_score', 0.3),
            'max_perplexity': self.config.get('max_perplexity', 1000.0)
        }

    def apply_filters(self, df: DataFrame, text_column: str = 'text') -> DataFrame:
        """
        Apply all quality filters to the input dataframe
        
        Args:
            df: Input DataFrame
            text_column: Name of the column containing text to filter
            
        Returns:
            Filtered DataFrame
        """
        self.logger.info("Starting quality filtering process...")
        
        # Add quality metrics columns
        df_with_metrics = self._add_quality_metrics(df, text_column)
        
        # Apply filtering rules based on thresholds
        filtered_df = self._apply_threshold_filters(df_with_metrics, text_column)
        
        self.logger.info(f"Quality filtering completed. Original rows: {df.count()}, "
                         f"filtered rows: {filtered_df.count()}")
        
        return filtered_df

    def _add_quality_metrics(self, df: DataFrame, text_column: str) -> DataFrame:
        """
        Add quality metrics to the dataframe
        
        Args:
            df: Input DataFrame
            text_column: Name of the text column
            
        Returns:
            DataFrame with added quality metric columns
        """
        # Register UDFs for quality metrics
        calculate_perplexity_udf = udf(
            lambda text: float(self.perplexity_calculator.calculate(text)), 
            DoubleType()
        )
        
        detect_toxicity_udf = udf(
            lambda text: float(self.toxicity_detector.detect(text)), 
            DoubleType()
        )
        
        calculate_quality_score_udf = udf(
            lambda text: float(self.quality_scorer.score(text)), 
            DoubleType()
        )
        
        # Add quality metrics columns
        df_with_metrics = df.withColumn(
            'perplexity', calculate_perplexity_udf(col(text_column))
        ).withColumn(
            'toxicity_score', detect_toxicity_udf(col(text_column))
        ).withColumn(
            'quality_score', calculate_quality_score_udf(col(text_column))
        )
        
        return df_with_metrics

    def _apply_threshold_filters(self, df: DataFrame, text_column: str) -> DataFrame:
        """
        Apply threshold-based filters to the dataframe
        
        Args:
            df: DataFrame with quality metrics
            text_column: Name of the text column
            
        Returns:
            Filtered DataFrame
        """
        # Apply filters based on thresholds
        filtered_df = df.filter(
            (col('toxicity_score') <= self.thresholds['max_toxicity']) &
            (col('quality_score') >= self.thresholds['min_quality_score']) &
            (col('perplexity') <= self.thresholds['max_perplexity'])
        )
        
        return filtered_df

    def get_quality_report(self, df: DataFrame, text_column: str = 'text') -> Dict[str, Any]:
        """
        Generate a quality report for the input data
        
        Args:
            df: Input DataFrame
            text_column: Name of the text column
            
        Returns:
            Dictionary containing quality metrics report
        """
        df_with_metrics = self._add_quality_metrics(df, text_column)
        
        # Calculate statistics
        stats = df_with_metrics.select(
            'perplexity', 'toxicity_score', 'quality_score'
        ).agg(
            {'perplexity': 'avg', 'toxicity_score': 'avg', 'quality_score': 'avg'}
        ).collect()[0]
        
        total_count = df.count()
        filtered_count = self.apply_filters(df, text_column).count()
        
        report = {
            'total_documents': total_count,
            'passed_documents': filtered_count,
            'pass_rate': filtered_count / total_count if total_count > 0 else 0,
            'avg_perplexity': stats['avg(perplexity)'],
            'avg_toxicity': stats['avg(toxicity_score)'],
            'avg_quality_score': stats['avg(quality_score)']
        }
        
        return report