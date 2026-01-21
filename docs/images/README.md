# Generated Images

This directory contains auto-generated diagram images from D2 source files.

## How it works

1. D2 source files are located in `docs/diagrams/`
2. Images are generated using `make diagrams`
3. GitHub Actions automatically regenerates images on push

## Available diagrams

| Diagram                  | Description                     |
| ------------------------ | ------------------------------- |
| `architecture.svg`       | System architecture overview    |
| `training-pipeline.svg`  | LLM training data pipeline      |
| `rag-pipeline.svg`       | RAG knowledge base pipeline     |
| `data-flow.svg`          | Data flow overview              |
| `dedup-algorithm.svg`    | MinHash deduplication algorithm |
| `retrieval-strategy.svg` | Hybrid retrieval strategy       |

## Regenerate locally

```bash
# Install D2 first
curl -fsSL https://d2lang.com/install.sh | sh -s --

# Generate all diagrams
make diagrams

# Or use Docker
make docker-diagrams
```

## Note

These files are auto-generated. Do not edit directly - modify the `.d2` source files instead.
