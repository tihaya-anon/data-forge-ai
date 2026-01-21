# makefiles/parallel.mk - 任务管理（使用 Git Worktree 并行开发）
# 任务规划和跟踪命令，支持多AI Agent并行开发

# 任务文件路径
TASKS_FILE := ai-context/tasks/tasks.yaml
DAG_SCRIPT := ai-context/scripts/task_dag.py
DAG_OUTPUT := docs/diagrams/task-dag.d2

# 工作树相关变量
WORKTREE_BASE_DIR ?= $(shell pwd)/../agent-workspace-
MAIN_BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)

# ============================================================================
# 任务分析与规划
# ============================================================================

.PHONY: task-dag
task-dag: ## 生成任务依赖 DAG 图
	@printf "$(CYAN)生成任务 DAG...$(NC)\n"
	@python3 $(DAG_SCRIPT) --tasks $(TASKS_FILE) --output $(DAG_OUTPUT)
	@if command -v d2 >/dev/null 2>&1; then \
		d2 $(DAG_OUTPUT) docs/images/task-dag.svg && \
		printf "$(GREEN)✓ SVG 已生成: docs/images/task-dag.svg$(NC)\n"; \
	else \
		printf "$(YELLOW)提示: 安装 d2 可生成 SVG 图片 (brew install d2)$(NC)\n"; \
	fi

.PHONY: task-analyze
task-analyze: ## 分析任务并行度和关键路径
	@python3 $(DAG_SCRIPT) --tasks $(TASKS_FILE) --analyze-only

.PHONY: task-next
task-next: ## 显示下一个可执行的任务
	@python3 $(DAG_SCRIPT) --tasks $(TASKS_FILE) --next-tasks

.PHONY: task-list
task-list: ## 列出所有任务及状态
	@python3 $(DAG_SCRIPT) --tasks $(TASKS_FILE) --list-all

.PHONY: task-edit
task-edit: ## 编辑任务清单文件
	@$${EDITOR:-vim} $(TASKS_FILE)

# ============================================================================
# 任务状态管理
# ============================================================================

.PHONY: task-status
task-status: ## 显示任务完成进度
	@python3 $(DAG_SCRIPT) --tasks $(TASKS_FILE) --status

# ============================================================================
# Git Worktree 并行开发
# ============================================================================

.PHONY: parallel-setup
parallel-setup: ## 创建并行开发工作树 (usage: make parallel-setup AGENTS=3)
	@if [ -z "$(AGENTS)" ]; then \
		echo "$(RED)错误: 请指定 agent 数量 (usage: make parallel-setup AGENTS=N)$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)正在为 $(AGENTS) 个 agent 设置并行开发环境...$(NC)"
	for i in $$(seq 1 $(AGENTS)); do \
		WORKTREE_DIR="$(WORKTREE_BASE_DIR)$${i}"; \
		if [ -d "$$WORKTREE_DIR" ]; then \
			echo "$(YELLOW)警告: $$WORKTREE_DIR 已存在，跳过创建$(NC)"; \
		else \
			echo "$(GREEN)创建工作树: $$WORKTREE_DIR$(NC)"; \
			git worktree add "$$WORKTREE_DIR" -b "agent-$${i}-branch" || exit 1; \
		fi; \
	done
	@echo "$(GREEN)✓ 并行开发环境设置完成$(NC)"

.PHONY: parallel-status
parallel-status: ## 查看工作树状态
	@printf "$(CYAN)当前工作树状态:$(NC)\n"
	@git worktree list

.PHONY: parallel-sync
parallel-sync: ## 同步所有工作树的更改
	@echo "$(CYAN)正在同步所有工作树更改...$(NC)"
	@for dir in $(WORKTREE_BASE_DIR)*; do \
		if [ -d "$$dir" ] && [ -d "$$dir/.git" ]; then \
			echo "$(GREEN)同步 $$dir$(NC)"; \
			cd "$$dir" && git add . && git commit -m "Sync changes" 2>/dev/null || echo "No changes to commit in $$dir"; \
			git checkout $(MAIN_BRANCH) && git pull origin $(MAIN_BRANCH); \
			cd - > /dev/null; \
		fi; \
	done
	@echo "$(GREEN)✓ 所有工作树同步完成$(NC)"

.PHONY: parallel-delete-all
parallel-delete-all: ## 删除所有并行工作树
	@echo "$(CYAN)正在删除所有并行工作树...$(NC)"
	@git worktree list --porcelain | grep worktree | cut -d' ' -f2 | while read worktree; do \
		if [[ "$$worktree" =~ agent-workspace- ]]; then \
			echo "$(RED)删除工作树: $$worktree$(NC)"; \
			git worktree remove --force "$$worktree"; \
		fi; \
	done
	@echo "$(GREEN)✓ 所有并行工作树已删除$(NC)"

.PHONY: parallel-delete-unused
parallel-delete-unused: ## 删除未使用的工作树
	@echo "$(CYAN)正在删除未使用的工作树...$(NC)"
	@git worktree list --porcelain | grep worktree | cut -d' ' -f2 | while read worktree; do \
		if [[ "$$worktree" =~ agent-workspace- ]] && [ ! -d "$$worktree" ]; then \
			echo "$(RED)删除损坏的工作树引用: $$worktree$(NC)"; \
			git worktree remove --force "$$worktree" 2>/dev/null || true; \
		fi; \
	done
	@echo "$(GREEN)✓ 未使用的工作树清理完成$(NC)"