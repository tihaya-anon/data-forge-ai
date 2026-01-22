"""
Tests for Vector Retrieval Service Module
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from src.rag.retrieval.vector import VectorRetrievalService
from src.rag.embedding import BGEEmbedding


class TestVectorRetrievalService(unittest.TestCase):
    """Test cases for VectorRetrievalService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_embedding_model = Mock(spec=BGEEmbedding)
        self.service = VectorRetrievalService(embedding_model=self.mock_embedding_model)
        
        # Mock Milvus client
        self.mock_milvus_client = Mock()
        self.service.milvus_client = self.mock_milvus_client
    
    @patch('src.rag.retrieval.vector.Collection')
    def test_similarity_search(self, mock_collection_class):
        """Test similarity search functionality."""
        # Setup mock collection
        mock_collection = Mock()
        mock_collection_class.return_value = mock_collection
        
        # Mock search results
        mock_hit = Mock()
        mock_hit.id = 1
        mock_hit.distance = 0.8
        mock_hit.entity = {'text': 'test document'}
        
        mock_result = [[mock_hit]]
        mock_collection.search.return_value = mock_result
        
        # Mock embedding generation
        self.mock_embedding_model.embed_query.return_value = [0.1, 0.2, 0.3]
        
        # Perform search
        results = self.service.similarity_search(
            query="test query",
            collection_name="test_collection",
            top_k=1
        )
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["distance"], 0.8)
        self.assertIn("entity", results[0])
        
        # Verify embedding was called
        self.mock_embedding_model.embed_query.assert_called_once_with("test query")
        
        # Verify search was called with correct params
        mock_collection.search.assert_called_once()
        args, kwargs = mock_collection.search.call_args
        self.assertIn("data", kwargs)
        self.assertIn("anns_field", kwargs)
        self.assertIn("param", kwargs)
        self.assertIn("limit", kwargs)
    
    def test_build_filter_expression_string_value(self):
        """Test building filter expression for string values."""
        filters = {"category": "technology"}
        expr = self.service._build_filter_expression(filters)
        self.assertEqual(expr, 'category == "technology"')
    
    def test_build_filter_expression_numeric_value(self):
        """Test building filter expression for numeric values."""
        filters = {"rating": 4.5}
        expr = self.service._build_filter_expression(filters)
        self.assertEqual(expr, 'rating == 4.5')
    
    def test_build_filter_expression_list_value(self):
        """Test building filter expression for list values."""
        filters = {"category": ["tech", "science"]}
        expr = self.service._build_filter_expression(filters)
        self.assertEqual(expr, 'category in ["tech", "science"]')
    
    def test_build_filter_expression_multiple_filters(self):
        """Test building filter expression for multiple filters."""
        filters = {
            "category": "technology",
            "rating": 4.5,
            "tags": ["ai", "ml"]
        }
        expr = self.service._build_filter_expression(filters)
        expected_parts = [
            'category == "technology"',
            'rating == 4.5',
            'tags in ["ai", "ml"]'
        ]
        for part in expected_parts:
            self.assertIn(part, expr)
        self.assertEqual(expr.count(" and "), 2)  # Two connectors for three conditions
    
    def test_calculate_similarity_cosine(self):
        """Test cosine similarity calculation."""
        vector_a = [1, 0, 0]
        vector_b = [1, 1, 0]
        
        # Expected cosine similarity: dot(a,b)/(norm(a)*norm(b)) = 1/(1*sqrt(2)) = 1/sqrt(2) ≈ 0.707
        expected_similarity = 1 / np.sqrt(2)
        
        similarity = self.service.calculate_similarity(vector_a, vector_b, "cosine")
        
        self.assertAlmostEqual(similarity, expected_similarity, places=3)
    
    def test_calculate_similarity_euclidean(self):
        """Test euclidean similarity calculation."""
        vector_a = [0, 0]
        vector_b = [3, 4]
        
        # Distance = sqrt((3-0)^2 + (4-0)^2) = 5
        # Similarity = 1/(1+distance) = 1/6 ≈ 0.167
        expected_similarity = 1 / 6
        
        similarity = self.service.calculate_similarity(vector_a, vector_b, "euclidean")
        
        self.assertAlmostEqual(similarity, expected_similarity, places=3)
    
    def test_calculate_similarity_dot_product(self):
        """Test dot product similarity calculation."""
        vector_a = [1, 2]
        vector_b = [3, 4]
        
        # Dot product = 1*3 + 2*4 = 11
        expected_similarity = 11
        
        similarity = self.service.calculate_similarity(vector_a, vector_b, "dot_product")
        
        self.assertEqual(similarity, expected_similarity)
    
    def test_calculate_similarity_invalid_metric(self):
        """Test that invalid similarity metric raises error."""
        with self.assertRaises(ValueError) as context:
            self.service.calculate_similarity([1, 2], [3, 4], "invalid_metric")
        
        self.assertIn("Unsupported similarity metric", str(context.exception))


if __name__ == "__main__":
    unittest.main()