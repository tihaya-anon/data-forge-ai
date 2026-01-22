"""
Elasticsearch BM25 Keyword Retriever Module

Implementation of keyword-based retrieval using Elasticsearch BM25 algorithm,
with query construction, result sorting, and highlighting support.
"""

import asyncio
from typing import List, Dict, Any, Optional
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError


class ElasticsearchRetriever:
    """
    A keyword retriever using Elasticsearch BM25 algorithm.
    
    Supports query construction, result sorting, and highlighting.
    """
    
    def __init__(self, hosts: str = "localhost:9200", index_name: str = "documents"):
        """
        Initialize the ElasticsearchRetriever.
        
        Args:
            hosts: Elasticsearch hosts (default: localhost:9200)
            index_name: Name of the index to search in (default: documents)
        """
        self.hosts = hosts
        self.index_name = index_name
        self.client = AsyncElasticsearch(hosts=[hosts])
    
    async def initialize_index(self, mappings: Optional[Dict] = None) -> bool:
        """
        Initialize the Elasticsearch index with specified mappings.
        
        Args:
            mappings: Optional mapping definition for the index
            
        Returns:
            True if successful, False otherwise
        """
        if mappings is None:
            # Default mapping for document storage
            mappings = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "metadata": {"type": "object", "enabled": True}
                    }
                }
            }
        
        try:
            # Check if index exists
            if not await self.client.indices.exists(index=self.index_name):
                # Create index with mappings
                await self.client.indices.create(index=self.index_name, body=mappings)
                return True
            return True
        except Exception as e:
            print(f"Error initializing index: {e}")
            return False
    
    async def add_document(self, doc_id: str, title: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a document to the Elasticsearch index.
        
        Args:
            doc_id: Document identifier
            title: Document title
            content: Document content
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if metadata is None:
            metadata = {}
            
        try:
            await self.client.index(
                index=self.index_name,
                id=doc_id,
                body={
                    "title": title,
                    "content": content,
                    "metadata": metadata
                }
            )
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    async def bulk_add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Bulk add documents to the Elasticsearch index.
        
        Args:
            documents: List of documents in the form of 
                      {'id': ..., 'title': ..., 'content': ..., 'metadata': ...}
                      
        Returns:
            True if successful, False otherwise
        """
        try:
            actions = []
            for doc in documents:
                actions.append({
                    "_index": self.index_name,
                    "_id": doc['id'],
                    "_source": {
                        "title": doc.get('title', ''),
                        "content": doc.get('content', ''),
                        "metadata": doc.get('metadata', {})
                    }
                })
                
            # Using bulk API for efficient indexing
            from elasticsearch.helpers import async_bulk
            _, errors = await async_bulk(self.client, actions)
            
            if errors:
                print(f"Bulk add errors: {errors}")
                return False
            return True
        except Exception as e:
            print(f"Error during bulk add: {e}")
            return False
    
    async def search(
        self,
        query_text: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
        highlight: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search documents using Elasticsearch BM25 algorithm.
        
        Args:
            query_text: Query text to search for
            top_k: Number of top results to return (default: 10)
            filters: Optional filters to apply to the search
            highlight: Whether to include highlights in results (default: True)
            
        Returns:
            List of documents with scores, sorted by relevance
        """
        # Build the query
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query_text,
                                "fields": ["title^2", "content"],  # Boost title field
                                "type": "best_fields",
                                "operator": "and"
                            }
                        }
                    ]
                }
            },
            "size": top_k,
            "sort": [{"_score": {"order": "desc"}}]
        }
        
        # Add filters if provided
        if filters:
            query_body["query"]["bool"]["filter"] = []
            for key, value in filters.items():
                if isinstance(value, list):
                    query_body["query"]["bool"]["filter"].append({
                        "terms": {f"metadata.{key}": value}
                    })
                else:
                    query_body["query"]["bool"]["filter"].append({
                        "term": {f"metadata.{key}": value}
                    })
        
        # Add highlighting if requested
        if highlight:
            query_body["highlight"] = {
                "fields": {
                    "title": {},
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                },
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"]
            }
        
        try:
            response = await self.client.search(index=self.index_name, body=query_body)
            
            results = []
            for hit in response['hits']['hits']:
                result = {
                    "id": hit["_id"],
                    "title": hit["_source"].get("title", ""),
                    "content": hit["_source"].get("content", ""),
                    "metadata": hit["_source"].get("metadata", {}),
                    "score": hit["_score"],
                }
                
                # Add highlights if available
                if highlight and "highlight" in hit:
                    result["highlights"] = hit["highlight"]
                
                results.append(result)
                
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def close(self):
        """Close the Elasticsearch client connection."""
        await self.client.close()
    
    async def delete_index(self) -> bool:
        """
        Delete the Elasticsearch index.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.client.indices.delete(index=self.index_name)
            return True
        except NotFoundError:
            # Index doesn't exist, which is fine
            return True
        except Exception as e:
            print(f"Error deleting index: {e}")
            return False