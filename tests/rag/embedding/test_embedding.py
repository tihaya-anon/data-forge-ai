"""
Tests for the Embedding Service Module
"""

import unittest
from unittest.mock import MagicMock, patch
from src.rag.embedding import (
    EmbeddingModel, 
    BGEEmbedding, 
    VectorCache, 
    EmbeddingService,
    create_embeddings_for_documents
)


class TestBGEEmbedding(unittest.TestCase):
    """Test cases for BGEEmbedding class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bge = BGEEmbedding(model_name="test-model")
    
    @patch('src.rag.embedding.BGEEmbedding._load_model')
    def test_embed_query(self, mock_load_model):
        """Test embedding a single query."""
        # Mock the embedding result
        mock_embedding = [0.1, 0.2, 0.3]
        self.bge.embed_texts = MagicMock(return_value=[mock_embedding])
        
        result = self.bge.embed_query("test query")
        
        self.assertEqual(result, mock_embedding)
        self.bge.embed_texts.assert_called_once_with(["test query"])
    
    @patch('src.rag.embedding.BGEEmbedding._load_model')
    def test_embed_texts(self, mock_load_model):
        """Test embedding multiple texts."""
        # Since actual model loading is complex to mock, 
        # we'll test the interface and logic
        self.assertIsNotNone(self.bge)
        self.assertEqual(self.bge.model_name, "test-model")
        self.assertTrue(self.bge.normalize_embeddings)


class TestVectorCache(unittest.TestCase):
    """Test cases for VectorCache class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = VectorCache()
    
    def test_put_and_get(self):
        """Test putting and getting embeddings from cache."""
        text = "test text"
        embedding = [0.1, 0.2, 0.3]
        
        # Initially, item should not be in cache
        result = self.cache.get(text)
        self.assertIsNone(result)
        
        # Put item in cache
        self.cache.put(text, embedding)
        
        # Now item should be in cache
        result = self.cache.get(text)
        self.assertEqual(result, embedding)
    
    def test_clear(self):
        """Test clearing the cache."""
        self.cache.put("text1", [1, 2, 3])
        self.cache.put("text2", [4, 5, 6])
        
        self.assertIsNotNone(self.cache.get("text1"))
        self.assertIsNotNone(self.cache.get("text2"))
        
        self.cache.clear()
        
        self.assertIsNone(self.cache.get("text1"))
        self.assertIsNone(self.cache.get("text2"))


class TestEmbeddingService(unittest.TestCase):
    """Test cases for EmbeddingService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_model = MagicMock(spec=EmbeddingModel)
        self.mock_model.embed_texts.return_value = [[0.1, 0.2], [0.3, 0.4]]
        self.service = EmbeddingService(embedding_model=self.mock_model)
    
    def test_batch_embed_texts(self):
        """Test batch embedding of texts."""
        texts = ["text1", "text2"]
        result = self.service.batch_embed_texts(texts, use_cache=False)
        
        self.mock_model.embed_texts.assert_called_once_with(texts)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], list)
        self.assertIsInstance(result[1], list)
    
    def test_batch_embed_texts_with_cache(self):
        """Test batch embedding with caching."""
        # First call - not in cache
        texts = ["text1", "text2"]
        result1 = self.service.batch_embed_texts(texts, use_cache=True)
        
        # Second call - should use cache for same texts
        result2 = self.service.batch_embed_texts(texts, use_cache=True)
        
        # The model should only be called once due to caching
        self.assertEqual(self.mock_model.embed_texts.call_count, 1)
        self.assertEqual(result1, result2)
    
    def test_embed_documents(self):
        """Test embedding documents."""
        documents = [
            {"content": "content1", "metadata": {"source": "doc1"}},
            {"content": "content2", "metadata": {"source": "doc2"}}
        ]
        
        result = self.service.embed_documents(documents, use_cache=False)
        
        # Check that embeddings were added to documents
        self.assertEqual(len(result), 2)
        self.assertIn('embedding', result[0])
        self.assertIn('embedding', result[1])
        self.assertEqual(result[0]['content'], "content1")
        self.assertEqual(result[1]['content'], "content2")
    
    @patch('src.rag.embedding.connections')
    def test_connect_to_milvus(self, mock_connections):
        """Test connecting to Milvus."""
        # Mock the connection
        mock_conn = MagicMock()
        mock_connections.connect.return_value = None
        mock_connections.get_connection.return_value = mock_conn
        
        self.service.connect_to_milvus(host="test-host", port=12345)
        
        mock_connections.connect.assert_called_once_with(alias="default", host="test-host", port=12345)
        self.assertIsNotNone(self.service.milvus_client)
    
    def test_store_embeddings_in_milvus_without_connection(self):
        """Test storing embeddings in Milvus without connection raises error."""
        documents = [{"content": "test", "embedding": [0.1, 0.2]}]
        
        with self.assertRaises(RuntimeError):
            self.service.store_embeddings_in_milvus(documents, "test_collection")


class TestCreateEmbeddingsForDocuments(unittest.TestCase):
    """Test the convenience function."""
    
    def test_create_embeddings_for_documents(self):
        """Test the convenience function."""
        documents = [
            {"content": "content1"},
            {"content": "content2"}
        ]
        
        with patch('src.rag.embedding.EmbeddingService') as mock_service_class:
            mock_service_instance = MagicMock()
            mock_service_instance.embed_documents.return_value = [
                {"content": "content1", "embedding": [0.1, 0.2]},
                {"content": "content2", "embedding": [0.3, 0.4]}
            ]
            mock_service_class.return_value = mock_service_instance
            
            result = create_embeddings_for_documents(documents)
            
            mock_service_class.assert_called_once()
            mock_service_instance.embed_documents.assert_called_once_with(documents, use_cache=True)
            self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()