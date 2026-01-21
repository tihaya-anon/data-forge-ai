# Document Processing Module

This module provides functionality for processing various document formats, including parsing, chunking, metadata extraction, and deduplication.

## Features

- **Document Parsing**: Supports PDF, DOCX, and TXT formats
- **Text Chunking**: Fixed-length and semantic chunking methods
- **Metadata Extraction**: Extracts both file system and format-specific metadata
- **Document Deduplication**: Removes duplicate documents based on content similarity

## Installation

To use this module, you'll need to install the required dependencies:

```bash
pip install pypdf2 python-docx
```

## Usage

### Basic Document Loading and Processing

```python
from src.rag.document import load_and_process_document

# Load and process a document with default settings
chunks = load_and_process_document('path/to/document.pdf')

# Load and process with custom settings
chunks = load_and_process_document(
    'path/to/document.pdf',
    chunk_size=1024,
    chunk_overlap=100,
    chunk_method='semantic'
)

for chunk in chunks:
    print(f"Chunk ID: {chunk.id}")
    print(f"Content preview: {chunk.content[:100]}...")
    print(f"Metadata: {chunk.metadata}")
    print("---")
```

### Advanced Usage

```python
from src.rag.document import DocumentProcessor

# Initialize the processor
processor = DocumentProcessor()

# Parse a document
document = processor.parse_document('path/to/document.pdf')

# Extract metadata separately
metadata = processor.extract_metadata('path/to/document.pdf')

# Chunk the document with custom settings
chunks = processor.chunk_document(
    document,
    chunk_size=1024,
    chunk_overlap=100,
    method='semantic'  # or 'fixed'
)

# Deduplicate a list of documents
unique_docs = processor.deduplicate_documents(chunks, threshold=0.90)
```

## API Reference

### Classes

#### `Document`
Represents a processed document with content and metadata.

- `content`: The text content of the document
- `metadata`: A dictionary of metadata
- `id`: Unique identifier for the document

#### `DocumentProcessor`
Main class for processing documents.

##### Methods:
- `parse_document(file_path)`: Parse a document based on its file extension
- `chunk_document(document, chunk_size, chunk_overlap, method)`: Split a document into chunks
- `extract_metadata(file_path)`: Extract metadata from a file
- `deduplicate_documents(documents, threshold)`: Remove duplicate documents based on content similarity

### Functions

#### `load_and_process_document(file_path, chunk_size, chunk_overlap, chunk_method)`
Load, parse, and chunk a document in one step.

## Configuration

The module can be configured using the `DocumentProcessingConfig` class:

```python
from src.rag.document.config import DocumentProcessingConfig

config = DocumentProcessingConfig(
    default_chunk_size=1024,
    default_chunk_overlap=100,
    deduplication_threshold=0.90
)
```

## Supported Formats

- PDF (.pdf) - Requires PyPDF2
- DOCX (.docx) - Requires python-docx
- TXT (.txt) - Built-in support

## Implementation Details

### Text Chunking

The module provides two methods for text chunking:

1. **Fixed-Length Chunking**: Splits text into fixed-size chunks with configurable overlap
2. **Semantic Chunking**: Attempts to split text at meaningful boundaries like sentences

### Metadata Extraction

Extracts both filesystem metadata (file size, creation date, etc.) and format-specific metadata (PDF metadata, DOCX properties, etc.).

### Deduplication

Uses SHA256 hashing to identify and remove exact duplicate documents. For near-duplicate detection, similarity algorithms can be added.