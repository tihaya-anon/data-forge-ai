"""
Tests for the document processing module.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.rag.document import (
    Document,
    DocumentProcessor,
    load_and_process_document
)


class TestDocument(unittest.TestCase):
    """Tests for the Document class."""

    def test_document_creation_with_content(self):
        """Test creating a document with content."""
        content = "This is a test document."
        doc = Document(content=content)
        
        self.assertEqual(doc.content, content)
        self.assertIsNotNone(doc.id)
        self.assertIsInstance(doc.metadata, dict)
        self.assertEqual(len(doc.metadata), 0)

    def test_document_creation_with_metadata(self):
        """Test creating a document with metadata."""
        content = "This is a test document."
        metadata = {"author": "Test Author", "date": "2023-01-01"}
        doc = Document(content=content, metadata=metadata)
        
        self.assertEqual(doc.content, content)
        self.assertEqual(doc.metadata, metadata)
        self.assertIsNotNone(doc.id)

    def test_document_id_generation(self):
        """Test that document IDs are generated consistently."""
        content = "This is a test document."
        doc1 = Document(content=content)
        doc2 = Document(content=content)
        
        # Same content should generate same ID
        self.assertEqual(doc1.id, doc2.id)

        # Different content should generate different IDs
        doc3 = Document(content="Different content")
        self.assertNotEqual(doc1.id, doc3.id)


class TestDocumentProcessor(unittest.TestCase):
    """Tests for the DocumentProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = DocumentProcessor()
        
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test text file
        self.txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.txt_file, 'w', encoding='utf-8') as f:
            f.write("This is a test document.\nIt has multiple lines.\nFor testing purposes.")
        
        # Create test document object
        self.test_document = Document(
            content="This is a sample document content. It contains multiple sentences. "
                     "We will use this for testing chunking functionality.",
            metadata={"source": "test", "author": "tester"}
        )

    def tearDown(self):
        """Clean up temporary files."""
        # Clean up temp files
        if os.path.exists(self.txt_file):
            os.remove(self.txt_file)

    def test_parse_txt_file(self):
        """Test parsing a text file."""
        doc = self.processor.parse_document(self.txt_file)
        
        self.assertEqual(doc.metadata['source_file'], "test.txt")
        self.assertEqual(doc.metadata['file_type'], ".txt")
        self.assertIn("This is a test document", doc.content)

    def test_fixed_chunking(self):
        """Test fixed-length chunking."""
        chunks = self.processor.chunk_document(
            self.test_document,
            chunk_size=30,
            chunk_overlap=5,
            method='fixed'
        )
        
        self.assertGreater(len(chunks), 1)  # Should be split into multiple chunks
        for i, chunk in enumerate(chunks):
            self.assertIn('chunk_index', chunk.metadata)
            self.assertEqual(chunk.metadata['chunk_index'], i)
            self.assertTrue(len(chunk.content) <= 30 or i == len(chunks)-1)  # Last chunk may be longer

    def test_semantic_chunking(self):
        """Test semantic chunking."""
        chunks = self.processor.chunk_document(
            self.test_document,
            chunk_size=100,
            chunk_overlap=10,
            method='semantic'
        )
        
        self.assertGreater(len(chunks), 0)
        for i, chunk in enumerate(chunks):
            self.assertIn('chunk_index', chunk.metadata)
            self.assertEqual(chunk.metadata['chunk_index'], i)
            self.assertIn('chunk_method', chunk.metadata)
            self.assertEqual(chunk.metadata['chunk_method'], 'semantic')

    def test_invalid_chunking_method(self):
        """Test invalid chunking method raises error."""
        with self.assertRaises(ValueError):
            self.processor.chunk_document(
                self.test_document,
                method='invalid_method'
            )

    @patch('os.path.exists', return_value=True)
    @patch('os.stat')
    def test_extract_metadata(self, mock_stat, mock_exists):
        """Test metadata extraction."""
        # Mock file stats
        mock_stat.return_value.st_size = 1024
        mock_stat.return_value.st_ctime = 1234567890
        mock_stat.return_value.st_mtime = 1234567890
        
        metadata = self.processor.extract_metadata(self.txt_file)
        
        self.assertEqual(metadata['source_file'], "test.txt")
        self.assertEqual(metadata['file_type'], ".txt")
        self.assertEqual(metadata['file_size'], 1024)

    def test_deduplicate_documents(self):
        """Test document deduplication."""
        # Create some documents - two identical, one different
        doc1 = Document(content="Same content here.", metadata={"id": 1})
        doc2 = Document(content="Same content here.", metadata={"id": 2})  # Duplicate
        doc3 = Document(content="Different content here.", metadata={"id": 3})

        documents = [doc1, doc2, doc3]
        unique_docs = self.processor.deduplicate_documents(documents)

        # Should have removed the duplicate
        self.assertEqual(len(unique_docs), 2)
        self.assertIn(doc1, unique_docs)
        self.assertIn(doc3, unique_docs)
        # Only one of doc1 or doc2 should remain (they're identical content)
        self.assertTrue((doc1 in unique_docs) != (doc2 in unique_docs))


class TestConvenienceFunctions(unittest.TestCase):
    """Tests for convenience functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test text file
        self.txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.txt_file, 'w', encoding='utf-8') as f:
            f.write("This is a test document content for the convenience function test. "
                    "It should be long enough to be chunked into multiple parts.")

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.txt_file):
            os.remove(self.txt_file)

    def test_load_and_process_document(self):
        """Test the load_and_process_document function."""
        chunks = load_and_process_document(
            self.txt_file,
            chunk_size=50,
            chunk_overlap=10,
            chunk_method='fixed'
        )
        
        self.assertGreater(len(chunks), 1)  # Should be chunked
        for i, chunk in enumerate(chunks):
            self.assertIn('chunk_index', chunk.metadata)
            self.assertEqual(chunk.metadata['chunk_index'], i)


if __name__ == '__main__':
    unittest.main()