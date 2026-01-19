# makefiles/parallel.mk - Parallel AI Agent Development
# 并行开发工作区管理

# 项目名称（用于 worktree 目录命名）
PROJECT_NAME := data-forge-ai

# 默认并行 agent 数量
AGENTS ?= 3

# ============================================================================
# Worktree 管理
# ============================================================================

.PHONY: parallel-setup
parallel-setup: ## 创建并行开发工作区 (AGENTS=3)
	@printf "$(CYAN)Creating $(AGENTS) parallel worktrees...$(NC)\n"
	@for i in $$(seq 1 $(AGENTS)); do \
		WORKTREE_PATH="../$(PROJECT_NAME)-agent$$i"; \
		BRANCH_NAME="agent/workspace-$$i"; \
		if [ -d "$$WORKTREE_PATH" ]; then \
			printf "$(YELLOW)⚠ Worktree already exists: $$WORKTREE_PATH$(NC)\n"; \
		else \
			git worktree add "$$WORKTREE_PATH" -b "$$BRANCH_NAME" 2>/dev/null || \
			git worktree add "$$WORKTREE_PATH" "$$BRANCH_NAME"; \
			printf "$(GREEN)✓ Created: $$WORKTREE_PATH (branch: $$BRANCH_NAME)$(NC)\n"; \
		fi; \
	done
	@printf "\n$(GREEN)✓ Parallel environment ready!$(NC)\n"
	@printf "$(CYAN)Open each directory in a separate IDE window.$(NC)\n"

.PHONY: parallel-status
parallel-status: ## 显示所有工作区状态
	@printf "$(CYAN)=== Git Worktrees ===$(NC)\n"
	@git worktree list
	@printf "\n$(CYAN)=== Branch Status ===$(NC)\n"
	@for worktree in $$(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do \
		if [ "$$worktree" != "$$(pwd)" ]; then \
			BRANCH=$$(git -C "$$worktree" branch --show-current 2>/dev/null); \
			CHANGES=$$(git -C "$$worktree" status --porcelain 2>/dev/null | wc -l | tr -d ' '); \
			COMMITS=$$(git -C "$$worktree" rev-list --count HEAD ^main 2>/dev/null || echo "?"); \
			printf "$(YELLOW)%-40s$(NC) branch: $(GREEN)%-20s$(NC) changes: %s commits: %s\n" \
				"$$worktree" "$$BRANCH" "$$CHANGES" "$$COMMITS"; \
		fi; \
	done

.PHONY: parallel-clean
parallel-clean: ## 清理所有 agent 工作区 (保留分支)
	@printf "$(RED)This will remove all agent worktrees!$(NC)\n"
	@printf "Branches will be preserved. Continue? [y/N] "; \
	read confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		for i in $$(seq 1 10); do \
			WORKTREE_PATH="../$(PROJECT_NAME)-agent$$i"; \
			if [ -d "$$WORKTREE_PATH" ]; then \
				git worktree remove "$$WORKTREE_PATH" --force 2>/dev/null && \
				printf "$(GREEN)✓ Removed: $$WORKTREE_PATH$(NC)\n" || \
				printf "$(RED)✗ Failed to remove: $$WORKTREE_PATH$(NC)\n"; \
			fi; \
		done; \
		git worktree prune; \
		printf "$(GREEN)✓ Cleanup complete$(NC)\n"; \
	else \
		printf "$(YELLOW)Cancelled$(NC)\n"; \
	fi

.PHONY: parallel-clean-all
parallel-clean-all: ## 清理工作区并删除分支 (危险!)
	@printf "$(RED)WARNING: This will remove all agent worktrees AND delete branches!$(NC)\n"
	@printf "Continue? [y/N] "; \
	read confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		for i in $$(seq 1 10); do \
			WORKTREE_PATH="../$(PROJECT_NAME)-agent$$i"; \
			BRANCH_NAME="agent/workspace-$$i"; \
			if [ -d "$$WORKTREE_PATH" ]; then \
				git worktree remove "$$WORKTREE_PATH" --force 2>/dev/null; \
				printf "$(GREEN)✓ Removed worktree: $$WORKTREE_PATH$(NC)\n"; \
			fi; \
			git branch -D "$$BRANCH_NAME" 2>/dev/null && \
			printf "$(GREEN)✓ Deleted branch: $$BRANCH_NAME$(NC)\n" || true; \
		done; \
		git worktree prune; \
		printf "$(GREEN)✓ Full cleanup complete$(NC)\n"; \
	else \
		printf "$(YELLOW)Cancelled$(NC)\n"; \
	fi

# ============================================================================
# 单个 Worktree 操作
# ============================================================================

.PHONY: worktree-add
worktree-add: ## 添加单个工作区 (NAME=xxx BRANCH=xxx)
ifndef NAME
	@printf "$(RED)Error: NAME is required$(NC)\n"
	@printf "Usage: make worktree-add NAME=agent1 BRANCH=feature/xxx\n"
	@exit 1
endif
ifndef BRANCH
	@printf "$(RED)Error: BRANCH is required$(NC)\n"
	@printf "Usage: make worktree-add NAME=agent1 BRANCH=feature/xxx\n"
	@exit 1
endif
	@WORKTREE_PATH="../$(PROJECT_NAME)-$(NAME)"; \
	git worktree add "$$WORKTREE_PATH" -b "$(BRANCH)" 2>/dev/null || \
	git worktree add "$$WORKTREE_PATH" "$(BRANCH)"; \
	printf "$(GREEN)✓ Created: $$WORKTREE_PATH (branch: $(BRANCH))$(NC)\n"

.PHONY: worktree-remove
worktree-remove: ## 删除单个工作区 (NAME=xxx)
ifndef NAME
	@printf "$(RED)Error: NAME is required$(NC)\n"
	@printf "Usage: make worktree-remove NAME=agent1\n"
	@exit 1
endif
	@WORKTREE_PATH="../$(PROJECT_NAME)-$(NAME)"; \
	git worktree remove "$$WORKTREE_PATH" --force && \
	printf "$(GREEN)✓ Removed: $$WORKTREE_PATH$(NC)\n"

# ============================================================================
# 任务管理
# ============================================================================

.PHONY: task-new
task-new: ## 创建新任务文件 (NAME=xxx)
ifndef NAME
	@printf "$(RED)Error: NAME is required$(NC)\n"
	@printf "Usage: make task-new NAME=implement-kafka-producer\n"
	@exit 1
endif
	@TASK_FILE=".ai-context/tasks/$(NAME).yaml"; \
	if [ -f "$$TASK_FILE" ]; then \
		printf "$(RED)Error: Task file already exists: $$TASK_FILE$(NC)\n"; \
		exit 1; \
	fi; \
	cp .ai-context/tasks/_template.yaml "$$TASK_FILE"; \
	printf "$(GREEN)✓ Created: $$TASK_FILE$(NC)\n"; \
	printf "$(CYAN)Edit the file to define your task.$(NC)\n"

.PHONY: task-list
task-list: ## 列出所有任务文件
	@printf "$(CYAN)=== Task Files ===$(NC)\n"
	@for f in .ai-context/tasks/*.yaml; do \
		if [ "$$(basename $$f)" != "_template.yaml" ] && [ "$$(basename $$f)" != "_example.yaml" ]; then \
			NAME=$$(grep -m1 "^  name:" "$$f" 2>/dev/null | cut -d'"' -f2); \
			STATUS=$$(grep -m1 "^  status:" "$$f" 2>/dev/null | awk '{print $$2}'); \
			AGENT=$$(grep -m1 "agent:" "$$f" 2>/dev/null | head -1 | cut -d'"' -f2); \
			case $$STATUS in \
				pending) COLOR="$(YELLOW)" ;; \
				in_progress) COLOR="$(CYAN)" ;; \
				completed) COLOR="$(GREEN)" ;; \
				blocked) COLOR="$(RED)" ;; \
				*) COLOR="$(NC)" ;; \
			esac; \
			printf "%-40s $$COLOR%-12s$(NC) agent: %s\n" "$$f" "$$STATUS" "$$AGENT"; \
		fi; \
	done 2>/dev/null || printf "$(YELLOW)No tasks found$(NC)\n"

.PHONY: task-status
task-status: ## 显示任务状态概览
	@printf "$(CYAN)=== Task Status Overview ===$(NC)\n"
	@PENDING=0; IN_PROGRESS=0; COMPLETED=0; BLOCKED=0; \
	for f in .ai-context/tasks/*.yaml; do \
		if [ "$$(basename $$f)" != "_template.yaml" ] && [ "$$(basename $$f)" != "_example.yaml" ]; then \
			STATUS=$$(grep -m1 "^  status:" "$$f" 2>/dev/null | awk '{print $$2}'); \
			case $$STATUS in \
				pending) PENDING=$$((PENDING+1)) ;; \
				in_progress) IN_PROGRESS=$$((IN_PROGRESS+1)) ;; \
				completed) COMPLETED=$$((COMPLETED+1)) ;; \
				blocked) BLOCKED=$$((BLOCKED+1)) ;; \
			esac; \
		fi; \
	done 2>/dev/null; \
	printf "$(YELLOW)Pending:     %d$(NC)\n" $$PENDING; \
	printf "$(CYAN)In Progress: %d$(NC)\n" $$IN_PROGRESS; \
	printf "$(GREEN)Completed:   %d$(NC)\n" $$COMPLETED; \
	printf "$(RED)Blocked:     %d$(NC)\n" $$BLOCKED

# ============================================================================
# 合并操作
# ============================================================================

.PHONY: parallel-merge
parallel-merge: ## 合并指定分支到当前分支 (BRANCH=xxx)
ifndef BRANCH
	@printf "$(RED)Error: BRANCH is required$(NC)\n"
	@printf "Usage: make parallel-merge BRANCH=agent/task-1\n"
	@exit 1
endif
	@printf "$(CYAN)Merging $(BRANCH) into $$(git branch --show-current)...$(NC)\n"
	@git merge $(BRANCH) --no-ff -m "Merge $(BRANCH)" && \
	printf "$(GREEN)✓ Merge successful$(NC)\n" || \
	printf "$(RED)✗ Merge failed - resolve conflicts manually$(NC)\n"

.PHONY: parallel-diff
parallel-diff: ## 查看所有 agent 分支与 main 的差异
	@printf "$(CYAN)=== Branch Differences ===$(NC)\n"
	@for branch in $$(git branch --list 'agent/*' | tr -d ' *'); do \
		AHEAD=$$(git rev-list --count main..$$branch 2>/dev/null || echo "?"); \
		BEHIND=$$(git rev-list --count $$branch..main 2>/dev/null || echo "?"); \
		printf "$(YELLOW)%-30s$(NC) +$$AHEAD / -$$BEHIND (ahead/behind main)\n" "$$branch"; \
	done

.PHONY: parallel-sync
parallel-sync: ## 将 main 的更新同步到所有工作区
	@printf "$(CYAN)Syncing main to all worktrees...$(NC)\n"
	@for worktree in $$(git worktree list --porcelain | grep "^worktree" | cut -d' ' -f2); do \
		if [ "$$worktree" != "$$(pwd)" ]; then \
			printf "$(YELLOW)Syncing: $$worktree$(NC)\n"; \
			git -C "$$worktree" fetch origin main && \
			git -C "$$worktree" rebase origin/main && \
			printf "$(GREEN)✓ Synced: $$worktree$(NC)\n" || \
			printf "$(RED)✗ Sync failed: $$worktree$(NC)\n"; \
		fi; \
	done
