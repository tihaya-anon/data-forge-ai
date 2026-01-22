"""
Unit tests for Elasticsearch keyword retriever
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.rag.retrieval.keyword.elasticsearch_retriever import ElasticsearchRetriever


@pytest.fixture
def mock_es_retriever():
    """Create a mock ElasticsearchRetriever for testing"""
    retriever = ElasticsearchRetriever(hosts="test_host:9200", index_name="test_index")
    # Replace the actual client with a mock
    retriever.client = AsyncMock()
    return retriever


@pytest.mark.asyncio
async def test_initialization():
    """Test basic initialization of ElasticsearchRetriever"""
    retriever = ElasticsearchRetriever()
    assert retriever.hosts == "localhost:9200"
    assert retriever.index_name == "documents"


@pytest.mark.asyncio
async def test_initialize_index(mock_es_retriever):
    """Test index initialization"""
    mock_es_retriever.client.indices.exists.return_value = False
    mock_es_retriever.client.indices.create = AsyncMock()
    
    result = await mock_es_retriever.initialize_index()
    assert result is True
    mock_es_retriever.client.indices.create.assert_called_once()


@pytest.mark.asyncio
async def test_add_document(mock_es_retriever):
    """Test adding a document"""
    mock_es_retriever.client.index = AsyncMock()
    
    result = await mock_es_retriever.add_document(
        doc_id="test_id", 
        title="Test Title", 
        content="Test Content", 
        metadata={"source": "test"}
    )
    
    assert result is True
    mock_es_retriever.client.index.assert_called_once()


@pytest.mark.asyncio
async def test_search_basic(mock_es_retriever):
    """Test basic search functionality"""
    # Mock search response
    mock_response = {
        "hits": {
            "hits": [
                {
                    "_id": "test_id",
                    "_score": 0.9,
                    "_source": {
                        "title": "Test Title",
                        "content": "Test Content",
                        "metadata": {"source": "test"}
                    },
                    "highlight": {
                        "content": ["This is a <mark>test</mark> content"]
                    }
                }
            ]
        }
    }
    
    mock_es_retriever.client.search = AsyncMock(return_value=mock_response)
    
    results = await mock_es_retriever.search("test query", top_k=5)
    
    assert len(results) == 1
    assert results[0]["id"] == "test_id"
    assert results[0]["title"] == "Test Title"
    assert results[0]["score"] == 0.9
    assert "highlights" in results[0]


@pytest.mark.asyncio
async def test_search_with_filters(mock_es_retriever):
    """Test search with filters"""
    mock_es_retriever.client.search = AsyncMock()
    
    await mock_es_retriever.search("test query", filters={"source": "wikipedia"})
    
    # Verify that the search was called with filter parameters
    args, kwargs = mock_es_retriever.client.search.call_args
    assert "body" in kwargs
    body = kwargs["body"]
    assert "query" in body
    assert "bool" in body["query"]
    assert "filter" in body["query"]["bool"]


@pytest.mark.asyncio
async def test_close_client(mock_es_retriever):
    """Test closing the ES client"""
    mock_es_retriever.client.close = AsyncMock()
    
    await mock_es_retriever.close()
    
    mock_es_retriever.client.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])