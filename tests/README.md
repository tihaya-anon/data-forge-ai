# DataForge AI - Testing Guide

## Overview

This directory contains mock services and test data for local development and testing.

## Mock Services

### Mock LLM Service

A lightweight Flask-based mock LLM service that simulates OpenAI-compatible API responses.

**Location**: `tests/mock-services/mock-llm.py`

**Features**:
- OpenAI-compatible `/v1/chat/completions` endpoint
- Keyword-based response generation
- Health check endpoint

**Usage**:
```bash
# Start with test environment
make dev-test

# Test the mock LLM
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "如何配置 Flink CDC?"}
    ]
  }'
```

## Test Data

### Training Data Sample

**Location**: `tests/mock-data/training-data-sample.jsonl`

Sample training data in JSONL format with quality scores.

### RAG Documents

**Location**: `tests/mock-data/sample-documents.json`

Sample documents for RAG testing with metadata.

## Running Tests

```bash
# Start minimal test environment
make dev-test

# This starts:
# - Kafka (message queue)
# - Redis (cache)
# - Mock LLM (simulated language model)
```

## Adding New Mock Services

1. Create service implementation in `tests/mock-services/`
2. Add Dockerfile if needed
3. Update `docker/compose.testing.yml`
4. Add documentation here
