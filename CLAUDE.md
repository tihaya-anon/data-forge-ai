# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataForge AI is an enterprise-grade big data AI platform architecture project focused on LLM training data engineering and RAG (Retrieval-Augmented Generation) intelligent knowledge bases. This is primarily a **documentation and architecture design project** using D2 diagrams to illustrate system design - there is no implementation code yet.

## Key Commands

### Diagram Generation
```bash
# Generate all SVG diagrams from D2 source files
make diagrams

# Generate PNG diagrams
make diagrams-png

# Watch for changes and auto-regenerate
make diagrams-watch

# Preview a specific diagram with live reload
make diagrams-preview FILE=architecture

# Generate diagrams using Docker (no local D2 installation required)
make diagrams-docker

# List all diagram files
make diagrams-list

# Clean generated diagrams
make diagrams-clean
```

### Docker Services
```bash
# Start all services (full stack)
make docker-up

# Start specific service groups
make docker-storage      # Kafka, Milvus, Redis, Elasticsearch, MinIO
make docker-compute      # Spark, Flink
make docker-orchestration # Airflow
make docker-analytics    # Doris
make docker-monitoring   # Prometheus, Grafana

# Stop services
make docker-down

# View service status
make docker-status

# View logs (all services or specific: make docker-logs SERVICE=kafka)
make docker-logs

# Show all service URLs and credentials
make docker-urls

# Clean everything including volumes
make docker-clean
```

### Development
```bash
# Initialize project for first-time use
make dev-init

# Setup development environment
make dev-setup

# Check dependencies
make dev-check

# Quick start (storage + monitoring)
make start

# Show project structure
make tree

# Clean temporary files
make clean
```

## Architecture

### System Layers
1. **Application Layer**: RAG Q&A service, training data service, analytics dashboards
2. **Service Layer**: Retrieval, embedding, data processing pipelines, schedulers
3. **Compute Layer**: Spark (batch), Flink (streaming), Ray (distributed ML), Trino (federated queries)
4. **Storage Layer**: Paimon (data lake), Milvus (vector DB), Redis (cache), Doris (OLAP)
5. **Infrastructure Layer**: Kubernetes, Kafka, MinIO/S3, Prometheus

### Two Core Modules

**Module 1: LLM Training Data Engineering**
- Data ingestion via Kafka
- Spark-based processing pipeline: cleaning → deduplication (MinHash/LSH) → quality filtering → PII removal
- Storage in Paimon data lake with versioning
- Quality filters: length, perplexity (KenLM), toxicity detection, quality scoring (fastText)

**Module 2: RAG Knowledge Base**
- Real-time updates via Flink CDC (<5s latency)
- Hybrid retrieval: vector search (Milvus) + keyword search (BM25/Elasticsearch) + RRF fusion
- Reranking with BGE-Reranker (cross-encoder)
- LLM generation with citation tracing

### Data Flow

**Training Data Flow**: Raw sources → Kafka → Spark processing → Paimon/Doris/MinIO → Training frameworks

**RAG Data Flow**:
- Real-time: CDC/Webhook → Kafka → Flink ETL → Embedding → Milvus
- Batch: Scheduled sync → Spark processing → Batch embedding → Milvus
- Query: User query → API → Retrieval (Milvus + ES) → Rerank → LLM → Response

### Key Technical Decisions

- **Paimon over Iceberg/Delta**: Native stream-batch unification, superior Flink integration, changelog support
- **Milvus over Pinecone/Qdrant**: Private deployment, trillion-scale capability, rich features
- **BGE-large-zh**: Primary embedding model (1024-dim) for Chinese text with domain fine-tuning support

## Directory Structure

```
docs/
├── diagrams/          # D2 source files for architecture diagrams
├── images/            # Generated SVG/PNG diagrams
├── ARCHITECTURE.md    # Detailed technical architecture (Chinese)
└── RESUME_DESCRIPTION.md  # Resume/interview preparation material

docker/
├── compose.*.yml      # Modular Docker Compose files by service group
└── monitoring/        # Grafana/Prometheus configurations

makefiles/
├── diagrams.mk        # Diagram generation targets
├── docker.mk          # Docker operations
└── dev.mk             # Development utilities
```

## D2 Diagram Configuration

Diagrams use these settings (configurable in makefiles/diagrams.mk):
- Theme: 200
- Layout: elk
- Padding: 20

All D2 source files are in `docs/diagrams/`, output goes to `docs/images/`.

## Service Access

When services are running via Docker Compose:
- Kafka UI: http://localhost:8080
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)
- Spark UI: http://localhost:8081
- Flink UI: http://localhost:8082
- Airflow: http://localhost:8083 (admin/admin)
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

## Important Notes

- This is a **design/documentation project** - no Python/Java/Scala implementation code exists yet
- Focus is on architecture diagrams and comprehensive technical documentation
- Docker Compose files define the intended infrastructure stack but services may not have full configurations
- The project demonstrates expertise in big data architecture, LLM infrastructure, and RAG systems
