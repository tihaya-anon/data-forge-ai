# ===========================================
# DataForge AI - Main Makefile
# ===========================================
# LLM Training Data + RAG Knowledge Platform
#
# Usage:
#   make help          - Show all available commands
#   make docker-up     - Start all services
#   make diagrams      - Generate architecture diagrams
#
# Structure:
#   Makefile           - Main entry point (this file)
#   makefiles/
#     ├── diagrams.mk  - Diagram generation targets
#     ├── docker.mk    - Docker compose operations
#     └── dev.mk       - Development utilities

# -------------------------------------------
# Configuration
# -------------------------------------------
.DEFAULT_GOAL := help
SHELL := /bin/bash

# Colors for output (use with printf)
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
CYAN := \033[0;36m
NC := \033[0m

# -------------------------------------------
# Include Modular Makefiles
# -------------------------------------------
include makefiles/diagrams.mk
include makefiles/docker.mk
include makefiles/dev.mk

# -------------------------------------------
# Help Target (Auto-generated from comments)
# -------------------------------------------
.PHONY: help
help: ## Show this help message
	@printf "\n"
	@printf "$(CYAN)═══════════════════════════════════════════════════════════$(NC)\n"
	@printf "$(CYAN)  DataForge AI - Available Commands$(NC)\n"
	@printf "$(CYAN)═══════════════════════════════════════════════════════════$(NC)\n"
	@printf "\n"
	@printf "$(GREEN)Diagrams:$(NC)\n"
	@grep -hE '^diagrams[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | \
		sed 's/:.*## /:/' | \
		awk 'BEGIN {FS = ":"}; {printf "  $(YELLOW)%-24s$(NC) %s\n", $$1, $$2}'
	@printf "\n"
	@printf "$(GREEN)Docker - Full Stack:$(NC)\n"
	@grep -hE '^docker-(up|down|restart|status|logs|clean|urls):.*?## .*$$' $(MAKEFILE_LIST) | \
		sed 's/:.*## /:/' | \
		awk 'BEGIN {FS = ":"}; {printf "  $(YELLOW)%-24s$(NC) %s\n", $$1, $$2}'
	@printf "\n"
	@printf "$(GREEN)Docker - Service Groups:$(NC)\n"
	@grep -hE '^docker-(storage|compute|orchestration|analytics|monitoring):.*?## .*$$' $(MAKEFILE_LIST) | \
		sed 's/:.*## /:/' | \
		awk 'BEGIN {FS = ":"}; {printf "  $(YELLOW)%-24s$(NC) %s\n", $$1, $$2}'
	@printf "\n"
	@printf "$(GREEN)Docker - Infrastructure:$(NC)\n"
	@grep -hE '^docker-(network|volumes):.*?## .*$$' $(MAKEFILE_LIST) | \
		sed 's/:.*## /:/' | \
		awk 'BEGIN {FS = ":"}; {printf "  $(YELLOW)%-24s$(NC) %s\n", $$1, $$2}'
	@printf "\n"
	@printf "$(GREEN)Development:$(NC)\n"
	@grep -hE '^(dev-|lint|format|test|docs-|clean|tree)[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | \
		sed 's/:.*## /:/' | \
		awk 'BEGIN {FS = ":"}; {printf "  $(YELLOW)%-24s$(NC) %s\n", $$1, $$2}'
	@printf "\n"
	@printf "$(GREEN)Quick Aliases:$(NC)\n"
	@printf "  $(YELLOW)up$(NC)                       Alias for docker-up\n"
	@printf "  $(YELLOW)down$(NC)                     Alias for docker-down\n"
	@printf "  $(YELLOW)status$(NC)                   Alias for docker-status\n"
	@printf "  $(YELLOW)logs$(NC)                     Alias for docker-logs\n"
	@printf "  $(YELLOW)urls$(NC)                     Alias for docker-urls\n"
	@printf "  $(YELLOW)start$(NC)                    Quick start (storage + monitoring)\n"
	@printf "  $(YELLOW)stop$(NC)                     Stop all services\n"
	@printf "\n"

# -------------------------------------------
# Quick Start Aliases
# -------------------------------------------
.PHONY: up down status logs urls

up: docker-up
down: docker-down
status: docker-status
logs: docker-logs
urls: docker-urls

# -------------------------------------------
# Default Development Workflow
# -------------------------------------------
.PHONY: start stop

start: dev-setup docker-storage docker-monitoring ## Quick start: setup + storage + monitoring
	@printf "\n"
	@printf "$(GREEN)✓ Minimal development environment started!$(NC)\n"
	@printf "$(CYAN)Run 'make docker-compute' to add Spark/Flink$(NC)\n"
	@printf "$(CYAN)Run 'make urls' to see service URLs$(NC)\n"

stop: docker-down ## Stop all services
