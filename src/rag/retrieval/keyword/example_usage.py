"""
Example usage of the Elasticsearch keyword retriever
"""

import asyncio
from .elasticsearch_retriever import ElasticsearchRetriever


async def example():
    """Example of using the ElasticsearchRetriever"""
    # Initialize the retriever
    retriever = ElasticsearchRetriever(hosts="localhost:9200", index_name="example_docs")
    
    # Initialize the index
    await retriever.initialize_index()
    
    # Add some sample documents
    sample_docs = [
        {
            "id": "doc1",
            "title": "Introduction to Elasticsearch",
            "content": "Elasticsearch is a distributed search and analytics engine built on Apache Lucene.",
            "metadata": {"category": "search", "level": "beginner"}
        },
        {
            "id": "doc2",
            "title": "BM25 Algorithm Explained",
            "content": "BM25 is a bag-of-words retrieval function used as a ranking function in information retrieval.",
            "metadata": {"category": "algorithm", "level": "intermediate"}
        },
        {
            "id": "doc3",
            "title": "Keyword Search Techniques",
            "content": "Effective keyword search techniques involve understanding tokenization and scoring algorithms.",
            "metadata": {"category": "search", "level": "advanced"}
        }
    ]
    
    # Add documents to the index
    await retriever.bulk_add_documents(sample_docs)
    
    # Perform a search
    results = await retriever.search(
        query_text="Elasticsearch BM25 search algorithm",
        top_k=5,
        filters={"category": "search"},
        highlight=True
    )
    
    # Print results
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Title: {result['title']}")
        print(f"   Score: {result['score']:.2f}")
        print(f"   Content: {result['content'][:100]}...")
        if 'highlights' in result:
            print(f"   Highlights: {result['highlights']}")
        print()
    
    # Close the connection
    await retriever.close()


if __name__ == "__main__":
    asyncio.run(example())