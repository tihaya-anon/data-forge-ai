"""
Unit tests for the quality filtering module.
Tests for quality filtering functionality including perplexity, toxicity, and quality scoring.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the source directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../../..'))

from src.pipeline.spark.quality.quality_filter import QualityFilter
from src.pipeline.spark.quality.perplexity_calculator import PerplexityCalculator
from src.pipeline.spark.quality.toxicity_detector import ToxicityDetector
from src.pipeline.spark.quality.quality_scorer import QualityScorer


class TestQualityFilter(unittest.TestCase):
    """Test cases for QualityFilter class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock spark session for testing
        self.mock_spark = Mock()
        self.config = {
            'max_toxicity': 0.5,
            'min_quality_score': 0.3,
            'max_perplexity': 1000.0
        }
        self.quality_filter = QualityFilter(self.mock_spark, self.config)

    def test_initialization(self):
        """Test initialization of QualityFilter."""
        self.assertIsInstance(self.quality_filter.perplexity_calculator, PerplexityCalculator)
        self.assertIsInstance(self.quality_filter.toxicity_detector, ToxicityDetector)
        self.assertIsInstance(self.quality_filter.quality_scorer, QualityScorer)
        self.assertEqual(self.quality_filter.thresholds['max_toxicity'], 0.5)

    @patch('pyspark.sql.DataFrame.withColumn')
    @patch('pyspark.sql.DataFrame.filter')
    def test_apply_filters(self, mock_filter, mock_with_column):
        """Test applying filters to a DataFrame."""
        # Create a mock DataFrame
        mock_df = Mock()
        mock_df.count.return_value = 100
        
        # Call the method
        result = self.quality_filter.apply_filters(mock_df, 'text')
        
        # Assertions
        self.assertIsNotNone(result)
        # Verify that the methods were called appropriately
        mock_with_column.assert_called()
        mock_filter.assert_called()


class TestPerplexityCalculator(unittest.TestCase):
    """Test cases for PerplexityCalculator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.calculator = PerplexityCalculator()

    def test_calculate_empty_text(self):
        """Test perplexity calculation with empty text."""
        result = self.calculator.calculate("")
        self.assertEqual(result, float('inf'))

    def test_calculate_simple_text(self):
        """Test perplexity calculation with simple text."""
        result = self.calculator.calculate("This is a simple text.")
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)


class TestToxicityDetector(unittest.TestCase):
    """Test cases for ToxicityDetector class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = ToxicityDetector()

    def test_detect_empty_text(self):
        """Test toxicity detection with empty text."""
        result = self.detector.detect("")
        self.assertEqual(result, 0.0)

    def test_detect_safe_text(self):
        """Test toxicity detection with safe text."""
        safe_text = "This is a completely safe and friendly text."
        result = self.detector.detect(safe_text)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)

    def test_detect_toxic_text(self):
        """Test toxicity detection with potentially toxic text."""
        toxic_text = "This text contains some toxic words like hate and stupid."
        result = self.detector.detect(toxic_text)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)

    def test_is_toxic_method(self):
        """Test the is_toxic helper method."""
        result = self.detector.is_toxic("A harmless text", threshold=0.5)
        self.assertFalse(result)  # Should be non-toxic with default threshold


class TestQualityScorer(unittest.TestCase):
    """Test cases for QualityScorer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.scorer = QualityScorer()

    def test_score_empty_text(self):
        """Test quality scoring with empty text."""
        result = self.scorer.score("")
        self.assertEqual(result, 0.0)

    def test_score_short_text(self):
        """Test quality scoring with very short text."""
        result = self.scorer.score("Hi.")
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)

    def test_score_longer_text(self):
        """Test quality scoring with longer text."""
        text = "This is a longer text that has more meaningful content. It includes multiple sentences " \
               "and demonstrates better structure and coherence than shorter texts."
        result = self.scorer.score(text)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)

    def test_classify_quality(self):
        """Test quality classification."""
        text = "This is a reasonably good quality text."
        result = self.scorer.classify_quality(text)
        self.assertIn(result, ['low', 'medium', 'high'])


if __name__ == '__main__':
    # Run the tests
    unittest.main()