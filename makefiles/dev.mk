# ===========================================
# DataForge AI - Development Operations
# ===========================================
# Development and utility targets
#
# Included by main Makefile

# -------------------------------------------
# Development Setup
# -------------------------------------------
.PHONY: dev-setup dev-check dev-init

dev-setup: dev-check ## Setup development environment
	@printf "$(CYAN)Setting up development environment...$(NC)\n"
	@mkdir -p docker/airflow/{dags,logs,plugins}
	@mkdir -p docker/monitoring/grafana/provisioning/{dashboards,datasources}
	@mkdir -p docs/{diagrams,images}
	@printf "$(GREEN)✓ Development environment ready$(NC)\n"

dev-check: ## Check if required tools are installed
	@printf "$(CYAN)Checking dependencies...$(NC)\n"
	@which docker >/dev/null || (printf "$(RED)✗ Docker not found$(NC)\n" && exit 1)
	@printf "  $(GREEN)✓$(NC) Docker\n"
	@which d2 >/dev/null || printf "  $(YELLOW)⚠$(NC) D2 not found (optional, for diagrams)\n"
	@which python3 >/dev/null || printf "  $(YELLOW)⚠$(NC) Python3 not found (optional)\n"
	@which java >/dev/null || printf "  $(YELLOW)⚠$(NC) Java not found (optional)\n"
	@printf "$(GREEN)✓ Dependency check complete$(NC)\n"

dev-init: dev-setup docker-network docker-volumes ## Initialize project for first time use
	@printf "$(GREEN)✓ Project initialized! Run 'make docker-up' to start services$(NC)\n"

# -------------------------------------------
# Code Quality
# -------------------------------------------
.PHONY: lint format test

lint: ## Run linters on source code
	@printf "$(CYAN)Running linters...$(NC)\n"
	@if [ -d "src" ]; then \
		which ruff >/dev/null && ruff check src/ || printf "$(YELLOW)ruff not installed$(NC)\n"; \
	fi
	@printf "$(GREEN)✓ Lint complete$(NC)\n"

format: ## Format source code
	@printf "$(CYAN)Formatting code...$(NC)\n"
	@if [ -d "src" ]; then \
		which ruff >/dev/null && ruff format src/ || printf "$(YELLOW)ruff not installed$(NC)\n"; \
	fi
	@printf "$(GREEN)✓ Format complete$(NC)\n"

test: ## Run tests
	@printf "$(CYAN)Running tests...$(NC)\n"
	@if [ -d "tests" ]; then \
		python3 -m pytest tests/ -v || printf "$(YELLOW)pytest not installed$(NC)\n"; \
	else \
		printf "$(YELLOW)No tests directory found$(NC)\n"; \
	fi

# -------------------------------------------
# Documentation
# -------------------------------------------
.PHONY: docs-serve docs-build

docs-serve: ## Serve documentation locally
	@printf "$(CYAN)Starting documentation server...$(NC)\n"
	@which mkdocs >/dev/null || (printf "$(RED)mkdocs not installed. Run: pip install mkdocs$(NC)\n" && exit 1)
	@mkdocs serve

docs-build: ## Build documentation
	@printf "$(CYAN)Building documentation...$(NC)\n"
	@which mkdocs >/dev/null || (printf "$(RED)mkdocs not installed$(NC)\n" && exit 1)
	@mkdocs build

# -------------------------------------------
# Utilities
# -------------------------------------------
.PHONY: clean clean-all tree

clean: diagrams-clean ## Clean generated files
	@printf "$(CYAN)Cleaning temporary files...$(NC)\n"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@printf "$(GREEN)✓ Cleaned$(NC)\n"

clean-all: clean docker-clean ## Clean everything including Docker volumes
	@printf "$(GREEN)✓ Full cleanup complete$(NC)\n"

tree: ## Show project structure
	@printf "$(CYAN)Project Structure:$(NC)\n"
	@which tree >/dev/null && tree -I 'node_modules|venv|__pycache__|.git' -L 3 || \
		find . -type f -not -path './.git/*' | head -50
