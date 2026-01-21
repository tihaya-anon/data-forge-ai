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
		printf "$(RED)错误: 请指定 agent 数量 (usage: make parallel-setup AGENTS=N)$(NC)\n"; \
		exit 1; \
	fi
	@printf "$(CYAN)正在为 $(AGENTS) 个 agent 设置并行开发环境...$(NC)\n"
	for i in $$(seq 1 $(AGENTS)); do \
		WORKTREE_DIR="$(WORKTREE_BASE_DIR)$${i}"; \
		if [ -d "$$WORKTREE_DIR" ]; then \
			printf "$(YELLOW)警告: $$WORKTREE_DIR 已存在，跳过创建$(NC)\n"; \
		else \
			printf "$(GREEN)创建工作树: $$WORKTREE_DIR$(NC)\n"; \
			git worktree add "$$WORKTREE_DIR" -b "agent-$${i}-branch" || exit 1; \
		fi; \
	done
	@printf "$(GREEN)✓ 并行开发环境设置完成$(NC)\n"

.PHONY: parallel-status
parallel-status: ## 查看工作树状态
	@printf "$(CYAN)当前工作树状态:$(NC)\n"
	@git worktree list

.PHONY: parallel-sync
parallel-sync: ## 同步所有工作树的更改到主分支
	@printf "$(CYAN)正在同步所有工作树更改到主分支...$(NC)\n"
	@for dir in $(WORKTREE_BASE_DIR)*; do \
		if [ -d "$$dir" ] && [ -d "$$dir/.git" ]; then \
			BRANCH_NAME=$$(cd "$$dir" && git rev-parse --abbrev-ref HEAD); \
			printf "$(GREEN)处理工作树 $$BRANCH_NAME ($$dir)$(NC)\n"; \
			# 检查工作树中是否有更改 \
			if ! (cd "$$dir" && git diff --quiet $(TASKS_FILE)); then \
				printf "$(GREEN)  发现 $(TASKS_FILE) 的更改，正在合并到主分支$(NC)\n"; \
				# 将更改复制到主分支 \
				cp "$$dir/$(TASKS_FILE)" "./$(TASKS_FILE)"; \
			else \
				printf "$(YELLOW)  未发现 $(TASKS_FILE) 的更改$(NC)\n"; \
			fi; \
		fi; \
	done; \
	# 添加并提交更改 \
	if ! git diff --quiet $(TASKS_FILE); then \
		git add $(TASKS_FILE) && \
		git commit -m "Sync task statuses from agent worktrees"; \
		printf "$(GREEN)✓ 已提交任务状态更新$(NC)\n"; \
	else \
		printf "$(YELLOW)没有需要提交的更改$(NC)\n"; \
	fi
	@printf "$(GREEN)✓ 所有工作树同步完成$(NC)\n"
.PHONY: parallel-delete-all
parallel-delete-all: ## 删除所有并行工作树
	@printf "$(CYAN)正在删除所有并行工作树...$(NC)\n"
	@git worktree list --porcelain | grep worktree | cut -d' ' -f2 | while read worktree; do \
		if [[ "$$worktree" =~ agent-workspace- ]]; then \
			printf "$(RED)删除工作树: $$worktree$(NC)\n"; \
			git worktree remove --force "$$worktree"; \
		fi; \
	done
	@git branch -D $$(git branch | grep -P 'agent-\d+-branch')
	@printf "$(GREEN)✓ 所有并行工作树已删除$(NC)\n"

.PHONY: parallel-delete-unused
parallel-delete-unused: ## 删除未使用的工作树
	@printf "$(CYAN)正在删除未使用的工作树...$(NC)\n"
	@git worktree list --porcelain | grep worktree | cut -d' ' -f2 | while read worktree; do \
		if [[ "$$worktree" =~ agent-workspace- ]] && [ ! -d "$$worktree" ]; then \
			printf "$(RED)删除损坏的工作树引用: $$worktree$(NC)\n"; \
			git worktree remove --force "$$worktree" 2>/dev/null || true; \
		fi; \
	done
	@printf "$(GREEN)✓ 未使用的工作树清理完成$(NC)\n"