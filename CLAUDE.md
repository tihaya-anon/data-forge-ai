# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataForge AI is an enterprise-grade big data AI platform focused on LLM training data engineering and RAG (Retrieval-Augmented Generation) intelligent knowledge bases. This is a **polyglot implementation project** using Python, Java, and Scala.

**Current Stage**: Phase 1 完成，Phase 2 开发中

## Technology Stack

- **Python**: RAG services, APIs, configuration management (FastAPI, LangChain)
- **Java**: Kafka clients, Flink streaming jobs
- **Scala**: Spark batch processing jobs
- **SQL**: Spark SQL for data transformations

See [docs/TECH_STACK.md](docs/TECH_STACK.md) for detailed technology decisions.

## Development Workflow

**CRITICAL**: Read [.ai-context/DEVELOPMENT_WORKFLOW.md](.ai-context/DEVELOPMENT_WORKFLOW.md) before starting any task.

### Key Principles

1. **Interface-First**: Define APIs/schemas before parallel implementation
2. **Test After Each Task**: Unit + integration tests required
3. **Deploy and Verify**: Deploy to test environment after each task
4. **Quality Gates**: All tasks must pass quality checks before completion

### Task Workflow

```bash
# 1. Check available tasks
make task-next

# 2. For tasks with data interaction: Define interface first
# Create: docs/api/[service].yaml or schemas/[entity].proto

# 3. Implement with tests
# Python: cd services/python && uv run pytest
# Java: cd services/kafka-clients && mvn test
# Scala: cd jobs/spark && sbt test

# 4. Deploy and verify
make deploy-test
make smoke-test

# 5. Update task status in .ai-context/tasks/tasks.yaml
# 状态: 待处理 -> 已完成

# 6. Commit
git commit -m "[T-XXX] Task description"
```

## Key Commands

### Task Management
```bash
make task-next      # Show next available tasks
make task-analyze   # Analyze task dependencies and parallelism
make task-status    # Show completion progress
```

### Development Profiles
```bash
make dev-minimal    # Kafka + Redis (fastest, 3 services)
make dev-rag        # RAG stack (7 services)
make dev-pipeline   # Data pipeline stack (9 services)
make dev-test       # Test environment with mocks

make docker-wait    # Wait for services to be healthy
make docker-status  # Check service status
make docker-urls    # Show service URLs
```

### Service Reset
```bash
make docker-reset-kafka    # Reset Kafka only
make docker-reset-milvus   # Reset Milvus only
make docker-reset-storage  # Reset all storage
make docker-reset-all      # Nuclear option
```

### Python Services
```bash
cd services/python
uv sync              # Install dependencies
uv run pytest        # Run tests
uv run python -m dataforge_ai.rag.api  # Start service
```

### Java Services
```bash
cd services/kafka-clients
mvn clean compile    # Build
mvn test            # Run tests
mvn install         # Install to local repo
```

### Scala Jobs
```bash
cd jobs/spark
sbt compile         # Build
sbt test           # Run tests
sbt assembly       # Package JAR
```

## Architecture

### System Layers
1. **Application Layer**: RAG Q&A service, training data service, analytics dashboards
2. **Service Layer**: Retrieval, embedding, data processing pipelines, schedulers
3. **Compute Layer**: Spark (batch), Flink (streaming), Ray (distributed ML)
4. **Storage Layer**: Paimon (data lake), Milvus (vector DB), Redis (cache), Doris (OLAP)
5. **Infrastructure Layer**: Kubernetes, Kafka, MinIO/S3, Prometheus

### Two Core Modules

**Module 1: LLM Training Data Engineering**
- Data ingestion via Kafka
- Spark-based processing: cleaning → deduplication (MinHash/LSH) → quality filtering
- Storage in Paimon data lake with versioning

**Module 2: RAG Knowledge Base**
- Real-time updates via Flink CDC (<5s latency)
- Hybrid retrieval: vector (Milvus) + keyword (Elasticsearch) + RRF fusion
- Reranking with BGE-Reranker
- LLM generation with citation tracing

## Project Structure

```
dataforge-ai/
├── services/           # Microservices
│   ├── python/        # Python services (RAG, API, config)
│   ├── kafka-clients/ # Java Kafka clients
│   └── monitoring/    # Monitoring services
├── jobs/              # Data processing jobs
│   ├── spark/        # Scala Spark jobs
│   └── flink/        # Java Flink jobs
├── docker/           # Docker configurations
├── docs/             # Documentation
├── tests/            # Tests
└── config/           # Configuration files
```

## Quality Requirements

Every task must meet:
- [ ] Unit tests pass (coverage >= 80%)
- [ ] Integration tests pass
- [ ] Code style checks pass
- [ ] Type checks pass (Python)
- [ ] Security scan clean
- [ ] Documentation updated
- [ ] Deployed to test environment
- [ ] Smoke tests pass

## Service Access

When services are running:
- Kafka UI: http://localhost:8080
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)
- Spark UI: http://localhost:8081
- Flink UI: http://localhost:8082
- Airflow: http://localhost:8083 (admin/admin)
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Mock LLM: http://localhost:8000

## Important Notes

- **Polyglot Project**: Use appropriate language for each component
- **Interface-First**: Define contracts before parallel development
- **Test Everything**: No code without tests
- **Deploy Frequently**: Verify in test environment after each task
- **Quality Gates**: All checks must pass before task completion

## Documentation

- [Development Environment](docs/DEVELOPMENT.md)
- [Technology Stack](docs/TECH_STACK.md)
- [Development Workflow](.ai-context/DEVELOPMENT_WORKFLOW.md)
- [Task Management](.ai-context/PARALLEL_DEV.md)
- [Architecture](docs/ARCHITECTURE.md)


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
