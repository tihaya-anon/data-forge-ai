# makefiles/parallel.mk - 并行 AI Agent 开发
# 并行开发工作区管理命令

# 项目名称（用于 worktree 目录命名）
PROJECT_NAME := data-forge-ai

# 默认并行 agent 数量
AGENTS ?= 3

# 任务文件路径
TASKS_FILE := .ai-context/tasks/tasks.yaml
DAG_SCRIPT := .ai-context/scripts/task_dag.py
DAG_OUTPUT := docs/diagrams/task-dag.d2

# ============================================================================
# 任务 DAG 分析
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

.PHONY: task-edit
task-edit: ## 编辑任务清单文件
	@$${EDITOR:-vim} $(TASKS_FILE)

# ============================================================================
# 工作区管理
# ============================================================================

.PHONY: parallel-setup
parallel-setup: ## 创建并行开发工作区 (AGENTS=3)
	@printf "$(CYAN)正在创建 $(AGENTS) 个并行工作区...$(NC)\n"
	@for i in $$(seq 1 $(AGENTS)); do \
		WORKTREE_PATH="../$(PROJECT_NAME)-agent$$i"; \
		BRANCH_NAME="agent/workspace-$$i"; \
		if [ -d "$$WORKTREE_PATH" ]; then \
			printf "$(YELLOW)⚠ 工作区已存在: $$WORKTREE_PATH$(NC)\n"; \
		else \
			git worktree add "$$WORKTREE_PATH" -b "$$BRANCH_NAME" 2>/dev/null || \
			git worktree add "$$WORKTREE_PATH" "$$BRANCH_NAME"; \
			printf "$(GREEN)✓ 已创建: $$WORKTREE_PATH (分支: $$BRANCH_NAME)$(NC)\n"; \
		fi; \
	done
	@printf "\n$(GREEN)✓ 并行开发环境已就绪！$(NC)\n"
	@printf "$(CYAN)请在独立的 IDE 窗口中打开各工作区目录。$(NC)\n"

.PHONY: parallel-status
parallel-status: ## 显示所有工作区状态
	@printf "$(CYAN)=== Git 工作区列表 ===$(NC)\n"
	@git worktree list
	@printf "\n$(CYAN)=== 分支状态 ===$(NC)\n"
	@for worktree in $$(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do \
		if [ "$$worktree" != "$$(pwd)" ]; then \
			BRANCH=$$(git -C "$$worktree" branch --show-current 2>/dev/null); \
			CHANGES=$$(git -C "$$worktree" status --porcelain 2>/dev/null | wc -l | tr -d ' '); \
			COMMITS=$$(git -C "$$worktree" rev-list --count HEAD ^main 2>/dev/null || echo "?"); \
			printf "$(YELLOW)%-40s$(NC) 分支: $(GREEN)%-20s$(NC) 改动: %s 提交: %s\n" \
				"$$worktree" "$$BRANCH" "$$CHANGES" "$$COMMITS"; \
		fi; \
	done

.PHONY: parallel-clean
parallel-clean: ## 清理所有 agent 工作区（保留分支）
	@printf "$(RED)这将删除所有 agent 工作区！$(NC)\n"
	@printf "分支会被保留。是否继续？[y/N] "; \
	read confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		for i in $$(seq 1 10); do \
			WORKTREE_PATH="../$(PROJECT_NAME)-agent$$i"; \
			if [ -d "$$WORKTREE_PATH" ]; then \
				git worktree remove "$$WORKTREE_PATH" --force 2>/dev/null && \
				printf "$(GREEN)✓ 已删除: $$WORKTREE_PATH$(NC)\n" || \
				printf "$(RED)✗ 删除失败: $$WORKTREE_PATH$(NC)\n"; \
			fi; \
		done; \
		git worktree prune; \
		printf "$(GREEN)✓ 清理完成$(NC)\n"; \
	else \
		printf "$(YELLOW)已取消$(NC)\n"; \
	fi

.PHONY: parallel-clean-all
parallel-clean-all: ## 清理工作区并删除分支（危险！）
	@printf "$(RED)警告：这将删除所有 agent 工作区和分支！$(NC)\n"
	@printf "是否继续？[y/N] "; \
	read confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		for i in $$(seq 1 10); do \
			WORKTREE_PATH="../$(PROJECT_NAME)-agent$$i"; \
			BRANCH_NAME="agent/workspace-$$i"; \
			if [ -d "$$WORKTREE_PATH" ]; then \
				git worktree remove "$$WORKTREE_PATH" --force 2>/dev/null; \
				printf "$(GREEN)✓ 已删除工作区: $$WORKTREE_PATH$(NC)\n"; \
			fi; \
			git branch -D "$$BRANCH_NAME" 2>/dev/null && \
			printf "$(GREEN)✓ 已删除分支: $$BRANCH_NAME$(NC)\n" || true; \
		done; \
		git worktree prune; \
		printf "$(GREEN)✓ 完全清理完成$(NC)\n"; \
	else \
		printf "$(YELLOW)已取消$(NC)\n"; \
	fi

# ============================================================================
# 单个工作区操作
# ============================================================================

.PHONY: worktree-add
worktree-add: ## 添加单个工作区 (NAME=xxx BRANCH=xxx)
ifndef NAME
	@printf "$(RED)错误：需要 NAME 参数$(NC)\n"
	@printf "用法: make worktree-add NAME=agent1 BRANCH=feature/xxx\n"
	@exit 1
endif
ifndef BRANCH
	@printf "$(RED)错误：需要 BRANCH 参数$(NC)\n"
	@printf "用法: make worktree-add NAME=agent1 BRANCH=feature/xxx\n"
	@exit 1
endif
	@WORKTREE_PATH="../$(PROJECT_NAME)-$(NAME)"; \
	git worktree add "$$WORKTREE_PATH" -b "$(BRANCH)" 2>/dev/null || \
	git worktree add "$$WORKTREE_PATH" "$(BRANCH)"; \
	printf "$(GREEN)✓ 已创建: $$WORKTREE_PATH (分支: $(BRANCH))$(NC)\n"

.PHONY: worktree-remove
worktree-remove: ## 删除单个工作区 (NAME=xxx)
ifndef NAME
	@printf "$(RED)错误：需要 NAME 参数$(NC)\n"
	@printf "用法: make worktree-remove NAME=agent1\n"
	@exit 1
endif
	@WORKTREE_PATH="../$(PROJECT_NAME)-$(NAME)"; \
	git worktree remove "$$WORKTREE_PATH" --force && \
	printf "$(GREEN)✓ 已删除: $$WORKTREE_PATH$(NC)\n"

# ============================================================================
# 合并操作
# ============================================================================

.PHONY: parallel-merge
parallel-merge: ## 合并指定分支到当前分支 (BRANCH=xxx)
ifndef BRANCH
	@printf "$(RED)错误：需要 BRANCH 参数$(NC)\n"
	@printf "用法: make parallel-merge BRANCH=agent/task-1\n"
	@exit 1
endif
	@printf "$(CYAN)正在合并 $(BRANCH) 到 $$(git branch --show-current)...$(NC)\n"
	@git merge $(BRANCH) --no-ff -m "合并 $(BRANCH)" && \
	printf "$(GREEN)✓ 合并成功$(NC)\n" || \
	printf "$(RED)✗ 合并失败 - 请手动解决冲突$(NC)\n"

.PHONY: parallel-diff
parallel-diff: ## 查看所有 agent 分支与 main 的差异
	@printf "$(CYAN)=== 分支差异 ===$(NC)\n"
	@for branch in $$(git branch --list 'agent/*' | tr -d ' *'); do \
		AHEAD=$$(git rev-list --count main..$$branch 2>/dev/null || echo "?"); \
		BEHIND=$$(git rev-list --count $$branch..main 2>/dev/null || echo "?"); \
		printf "$(YELLOW)%-30s$(NC) +$$AHEAD / -$$BEHIND (领先/落后 main)\n" "$$branch"; \
	done

.PHONY: parallel-sync
parallel-sync: ## 将 main 的更新同步到所有工作区
	@printf "$(CYAN)正在同步 main 到所有工作区...$(NC)\n"
	@for worktree in $$(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do \
		if [ "$$worktree" != "$$(pwd)" ]; then \
			printf "$(YELLOW)同步中: $$worktree$(NC)\n"; \
			git -C "$$worktree" fetch origin main && \
			git -C "$$worktree" rebase origin/main && \
			printf "$(GREEN)✓ 已同步: $$worktree$(NC)\n" || \
			printf "$(RED)✗ 同步失败: $$worktree$(NC)\n"; \
		fi; \
	done
