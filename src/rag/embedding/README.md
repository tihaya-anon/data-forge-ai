# Embedding Service

Embedding service for the DataForge AI platform. Provides functionality for converting text to vector embeddings using state-of-the-art models.

## Features

- **BGE Model Integration**: Uses BAAI's General Embedding (BGE) models for high-quality text embeddings
- **Batch Processing**: Efficiently processes multiple texts in a single batch
- **Vector Caching**: Caches computed embeddings to avoid redundant computation
- **Milvus Integration**: Stores embeddings in Milvus vector database for fast similarity search

## Components

### BGEEmbedding

The `BGEEmbedding` class integrates with the Hugging Face Transformers library to provide access to BGE models. It supports various BGE model variants including `bge-large-zh` for Chinese text and `bge-large-en` for English text.

### VectorCache

A simple in-memory cache that stores previously computed embeddings, keyed by the SHA256 hash of the input text. This avoids recomputing embeddings for frequently processed texts.

### EmbeddingService

The main service class that orchestrates embedding creation, caching, and storage. Provides methods for:

- Batch embedding of texts
- Embedding of document collections
- Storing embeddings in Milvus vector database

## Usage

### Basic Usage

```python
from src.rag.embedding import EmbeddingService, BGEEmbedding

# Initialize the service
embedding_service = EmbeddingService()

# Embed a single text
single_embedding = embedding_service.embedding_model.embed_query("Hello, world!")

# Embed multiple texts
texts = ["First sentence", "Second sentence", "Third sentence"]
embeddings = embedding_service.batch_embed_texts(texts)

print(f"Generated {len(embeddings)} embeddings")
```

### Using with Documents

```python
from src.rag.embedding import EmbeddingService

# Initialize the service
embedding_service = EmbeddingService()

# Prepare documents
documents = [
    {"content": "This is the first document", "metadata": {"source": "doc1"}},
    {"content": "This is the second document", "metadata": {"source": "doc2"}}
]

# Generate embeddings for documents
enriched_documents = embedding_service.embed_documents(documents)
```

### Storing in Milvus

```python
from src.rag.embedding import EmbeddingService

# Initialize the service
embedding_service = EmbeddingService()

# Connect to Milvus
embedding_service.connect_to_milvus(host="localhost", port=19530)

# Store embeddings in Milvus
result = embedding_service.store_embeddings_in_milvus(
    documents=enriched_documents,
    collection_name="my_collection"
)

print(result)  # {'status': 'success', 'count': 2, 'collection': 'my_collection'}
```

### Using Custom Configuration

```python
from src.rag.embedding.config import EmbeddingConfig, load_embedding_config
from src.rag.embedding import EmbeddingService, BGEEmbedding

# Load custom configuration
config = load_embedding_config()

# Initialize service with custom model
custom_model = BGEEmbedding(
    model_name=config.model_name,
    normalize_embeddings=config.normalize_embeddings
)

embedding_service = EmbeddingService(embedding_model=custom_model)
```

## Configuration

The embedding service can be configured using the `EmbeddingConfig` class:

- `model_name`: The name of the Hugging Face model to use (default: "BAAI/bge-large-zh")
- `normalize_embeddings`: Whether to normalize embeddings to unit vectors (default: True)
- `max_seq_length`: Maximum sequence length for the model (default: 512)
- `cache_enabled`: Whether to enable caching (default: True)
- `cache_max_size`: Maximum number of entries in the cache (default: 10000)
- `batch_size`: Number of texts to process in each batch (default: 32)
- `milvus_host`: Host address of the Milvus server (default: "localhost")
- `milvus_port`: Port of the Milvus server (default: 19530)
- `collection_name`: Name of the Milvus collection (default: "document_embeddings")

## Requirements

- Python >= 3.8
- transformers
- torch
- pymilvus
- numpy

Install dependencies with:

```bash
pip install transformers torch pymilvus numpy
```

## Performance Tips

1. Use batch processing when possible to maximize throughput
2. Enable caching to avoid recomputing embeddings for frequently processed texts
3. Adjust batch size based on available GPU memory when using GPU acceleration
4. Monitor cache hit rate and adjust cache size accordingly

## Troubleshooting

If you encounter issues with model loading:

1. Ensure transformers and torch are installed
2. Verify that the model name is correct and accessible
3. Check that you have sufficient memory for the model

For Milvus connectivity issues:

1. Ensure Milvus server is running
2. Verify host and port configuration
3. Check network connectivity to the Milvus server