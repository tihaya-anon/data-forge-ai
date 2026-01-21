# DataForge AI - Development Environment Setup

## Prerequisites

- Python 3.10+ (managed via `uv`)
- Docker & Docker Compose
- Git

## Quick Start

### 1. Install Python Dependencies

This project uses `uv` for fast Python package management:

```bash
# Install all dependencies
uv sync

# Install with specific extras
uv sync --extra dev          # Development tools
uv sync --extra spark        # Spark dependencies
uv sync --extra flink        # Flink dependencies
uv sync --extra rag          # RAG/LLM dependencies
uv sync --all-extras         # Everything
```

### 2. Start Infrastructure Services

```bash
# Start minimal environment (Kafka + Redis)
make dev-minimal

# Start RAG development environment
make dev-rag

# Start data pipeline environment
make dev-pipeline

# Start test environment with mock services
make dev-test
```

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/pipeline/kafka/test_producer.py
```

## Environment Configuration

### Python Environment

The project uses `uv` for dependency management. Key features:

- **Fast installation**: 10-100x faster than pip
- **Reproducible builds**: Lock file ensures consistency
- **Virtual environment**: Automatically managed by uv

### Docker Services

Available service profiles:

| Profile      | Services                       | Use Case                  |
| ------------ | ------------------------------ | ------------------------- |
| `minimal`    | Kafka, Redis                   | Quick testing             |
| `rag`        | + Milvus, Elasticsearch, MinIO | RAG development           |
| `pipeline`   | + Spark, Flink, MinIO          | Data pipeline development |
| `monitoring` | Prometheus, Grafana            | Monitoring setup          |

### Configuration Files

- `pyproject.toml` - Python project configuration
- `config/default.yaml` - Default application config
- `docker/compose.*.yml` - Docker service definitions
- `.env` - Environment variables (create from `.env.example`)

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Install Dependencies

```bash
uv sync --all-extras
```

### 3. Start Required Services

```bash
make dev-rag  # or dev-pipeline, dev-minimal
make docker-wait  # Wait for services to be healthy
```

### 4. Run Development Server

```bash
# Example: Run Kafka producer
uv run python -m src.pipeline.kafka.producer

# Example: Run tests
uv run pytest tests/
```

### 5. Code Quality Checks

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## Project Structure

```
dataforge-ai/
├── src/                    # Source code
│   ├── pipeline/          # Data pipeline modules
│   ├── rag/               # RAG modules
│   └── common/            # Shared utilities
├── tests/                 # Test files
├── config/                # Configuration files
├── docker/                # Docker configurations
├── docs/                  # Documentation
└── pyproject.toml         # Python project config
```

## Troubleshooting

### uv not found

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Docker services not starting

```bash
# Check service status
make docker-status

# View logs
make docker-logs SERVICE=kafka

# Reset services
make docker-reset-all
```

### Import errors

```bash
# Ensure you're using uv's Python environment
uv run python your_script.py

# Or activate the virtual environment
source .venv/bin/activate
```

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Project Architecture](docs/ARCHITECTURE.md)
- [Task Management](ai-context/PARALLEL_DEV.md)
