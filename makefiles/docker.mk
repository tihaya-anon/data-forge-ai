# ===========================================
# DataForge AI - Docker Compose Operations
# ===========================================
# Included by main Makefile

# -------------------------------------------
# Configuration
# -------------------------------------------
DOCKER_DIR := docker
COMPOSE_BASE := $(DOCKER_DIR)/compose.base.yml
COMPOSE_STORAGE := $(DOCKER_DIR)/compose.storage.yml
COMPOSE_COMPUTE := $(DOCKER_DIR)/compose.compute.yml
COMPOSE_ORCHESTRATION := $(DOCKER_DIR)/compose.orchestration.yml
COMPOSE_ANALYTICS := $(DOCKER_DIR)/compose.analytics.yml
COMPOSE_MONITORING := $(DOCKER_DIR)/compose.monitoring.yml

DC_BASE := docker compose -f $(COMPOSE_BASE)
DC_ALL := $(DC_BASE) \
	-f $(COMPOSE_STORAGE) \
	-f $(COMPOSE_COMPUTE) \
	-f $(COMPOSE_ORCHESTRATION) \
	-f $(COMPOSE_ANALYTICS) \
	-f $(COMPOSE_MONITORING)

# -------------------------------------------
# Full Stack Operations
# -------------------------------------------
.PHONY: docker-up docker-down docker-restart docker-status docker-logs docker-clean

docker-up: docker-network docker-volumes ## Start all services
	@printf "$(CYAN)Starting all services...$(NC)\n"
	@$(DC_ALL) up -d
	@printf "$(GREEN)✓ All services started$(NC)\n"
	@$(MAKE) docker-status

docker-down: ## Stop all services
	@printf "$(YELLOW)Stopping all services...$(NC)\n"
	@$(DC_ALL) down
	@printf "$(GREEN)✓ All services stopped$(NC)\n"

docker-restart: docker-down docker-up ## Restart all services

docker-status: ## Show status of all services
	@printf "$(CYAN)Service Status:$(NC)\n"
	@$(DC_ALL) ps

docker-logs: ## View logs from all services (use SERVICE=name for specific)
ifdef SERVICE
	@$(DC_ALL) logs -f $(SERVICE)
else
	@$(DC_ALL) logs -f --tail=100
endif

docker-clean: docker-down ## Stop services and remove volumes
	@printf "$(RED)Removing all volumes...$(NC)\n"
	@docker volume rm -f $$(docker volume ls -q -f name=distribute_ai) 2>/dev/null || true
	@printf "$(GREEN)✓ Cleaned$(NC)\n"

# -------------------------------------------
# Service Group Operations
# -------------------------------------------
.PHONY: docker-storage docker-compute docker-orchestration docker-analytics docker-monitoring

docker-storage: docker-network docker-volumes ## Start storage services only (Kafka, Milvus, Redis, ES)
	@printf "$(CYAN)Starting storage services...$(NC)\n"
	@$(DC_BASE) -f $(COMPOSE_STORAGE) up -d
	@printf "$(GREEN)✓ Storage services started$(NC)\n"

docker-compute: docker-network ## Start compute services only (Spark, Flink)
	@printf "$(CYAN)Starting compute services...$(NC)\n"
	@$(DC_BASE) -f $(COMPOSE_COMPUTE) up -d
	@printf "$(GREEN)✓ Compute services started$(NC)\n"

docker-orchestration: docker-network docker-volumes ## Start orchestration services only (Airflow)
	@printf "$(CYAN)Starting orchestration services...$(NC)\n"
	@$(DC_BASE) -f $(COMPOSE_ORCHESTRATION) up -d
	@printf "$(GREEN)✓ Orchestration services started$(NC)\n"

docker-analytics: docker-network docker-volumes ## Start analytics services only (Doris)
	@printf "$(CYAN)Starting analytics services...$(NC)\n"
	@$(DC_BASE) -f $(COMPOSE_ANALYTICS) up -d
	@printf "$(GREEN)✓ Analytics services started$(NC)\n"

docker-monitoring: docker-network docker-volumes ## Start monitoring services only (Prometheus, Grafana)
	@printf "$(CYAN)Starting monitoring services...$(NC)\n"
	@$(DC_BASE) -f $(COMPOSE_MONITORING) up -d
	@printf "$(GREEN)✓ Monitoring services started$(NC)\n"

# -------------------------------------------
# Stop Service Groups
# -------------------------------------------
.PHONY: docker-storage-down docker-compute-down docker-orchestration-down docker-analytics-down docker-monitoring-down

docker-storage-down: ## Stop storage services
	@$(DC_BASE) -f $(COMPOSE_STORAGE) down

docker-compute-down: ## Stop compute services
	@$(DC_BASE) -f $(COMPOSE_COMPUTE) down

docker-orchestration-down: ## Stop orchestration services
	@$(DC_BASE) -f $(COMPOSE_ORCHESTRATION) down

docker-analytics-down: ## Stop analytics services
	@$(DC_BASE) -f $(COMPOSE_ANALYTICS) down

docker-monitoring-down: ## Stop monitoring services
	@$(DC_BASE) -f $(COMPOSE_MONITORING) down

# -------------------------------------------
# Infrastructure Setup
# -------------------------------------------
.PHONY: docker-network docker-volumes

docker-network: ## Create Docker network
	@docker network inspect dataforge >/dev/null 2>&1 || \
		(printf "$(CYAN)Creating Docker network...$(NC)\n" && \
		 docker network create dataforge)

docker-volumes: ## Create Docker volumes
	@printf "$(CYAN)Ensuring Docker volumes exist...$(NC)\n"
	@docker volume create distribute_ai_kafka-data 2>/dev/null || true
	@docker volume create distribute_ai_minio-data 2>/dev/null || true
	@docker volume create distribute_ai_milvus-etcd-data 2>/dev/null || true
	@docker volume create distribute_ai_milvus-data 2>/dev/null || true
	@docker volume create distribute_ai_redis-data 2>/dev/null || true
	@docker volume create distribute_ai_es-data 2>/dev/null || true
	@docker volume create distribute_ai_airflow-postgres-data 2>/dev/null || true
	@docker volume create distribute_ai_doris-fe-data 2>/dev/null || true
	@docker volume create distribute_ai_doris-be-data 2>/dev/null || true
	@docker volume create distribute_ai_prometheus-data 2>/dev/null || true
	@docker volume create distribute_ai_grafana-data 2>/dev/null || true

# -------------------------------------------
# Service Access Info
# -------------------------------------------
.PHONY: docker-urls

docker-urls: ## Show service URLs
	@printf "$(CYAN)═══════════════════════════════════════════════════════════$(NC)\n"
	@printf "$(CYAN)  DataForge AI - Service URLs$(NC)\n"
	@printf "$(CYAN)═══════════════════════════════════════════════════════════$(NC)\n"
	@printf "\n"
	@printf "  $(GREEN)Storage:$(NC)\n"
	@printf "    Kafka UI:       http://localhost:8080\n"
	@printf "    MinIO Console:  http://localhost:9001  (minioadmin/minioadmin123)\n"
	@printf "    Milvus:         localhost:19530\n"
	@printf "    Redis:          localhost:6379\n"
	@printf "    Elasticsearch:  http://localhost:9200\n"
	@printf "\n"
	@printf "  $(GREEN)Compute:$(NC)\n"
	@printf "    Spark UI:       http://localhost:8081\n"
	@printf "    Flink UI:       http://localhost:8082\n"
	@printf "\n"
	@printf "  $(GREEN)Orchestration:$(NC)\n"
	@printf "    Airflow:        http://localhost:8083  (admin/admin)\n"
	@printf "\n"
	@printf "  $(GREEN)Analytics:$(NC)\n"
	@printf "    Doris FE:       http://localhost:8030\n"
	@printf "    Doris MySQL:    localhost:9030\n"
	@printf "\n"
	@printf "  $(GREEN)Monitoring:$(NC)\n"
	@printf "    Prometheus:     http://localhost:9090\n"
	@printf "    Grafana:        http://localhost:3000  (admin/admin)\n"
	@printf "\n"
