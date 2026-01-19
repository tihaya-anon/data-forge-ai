# makefiles/parallel.mk - 并行 AI Agent 开发
# 并行开发工作区管理命令

# 项目名称（用于 worktree 目录命名）
PROJECT_NAME := data-forge-ai

# 默认并行 agent 数量
AGENTS ?= 3

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
# 任务管理
# ============================================================================

.PHONY: task-new
task-new: ## 创建新任务文件 (NAME=xxx)
ifndef NAME
	@printf "$(RED)错误：需要 NAME 参数$(NC)\n"
	@printf "用法: make task-new NAME=implement-kafka-producer\n"
	@exit 1
endif
	@TASK_FILE=".ai-context/tasks/$(NAME).yaml"; \
	if [ -f "$$TASK_FILE" ]; then \
		printf "$(RED)错误：任务文件已存在: $$TASK_FILE$(NC)\n"; \
		exit 1; \
	fi; \
	cp .ai-context/tasks/_template.yaml "$$TASK_FILE"; \
	printf "$(GREEN)✓ 已创建: $$TASK_FILE$(NC)\n"; \
	printf "$(CYAN)请编辑该文件定义你的任务。$(NC)\n"

.PHONY: task-list
task-list: ## 列出所有任务文件
	@printf "$(CYAN)=== 任务文件列表 ===$(NC)\n"
	@for f in .ai-context/tasks/*.yaml; do \
		if [ "$$(basename $$f)" != "_template.yaml" ] && [ "$$(basename $$f)" != "_example.yaml" ]; then \
			NAME=$$(grep -m1 "名称:" "$$f" 2>/dev/null | cut -d'"' -f2); \
			STATUS=$$(grep -m1 "状态:" "$$f" 2>/dev/null | cut -d'"' -f2); \
			AGENT=$$(grep -m1 "agent:" "$$f" 2>/dev/null | head -1 | cut -d'"' -f2); \
			case $$STATUS in \
				待处理) COLOR="$(YELLOW)" ;; \
				进行中) COLOR="$(CYAN)" ;; \
				已完成) COLOR="$(GREEN)" ;; \
				已阻塞) COLOR="$(RED)" ;; \
				*) COLOR="$(NC)" ;; \
			esac; \
			printf "%-40s $$COLOR%-12s$(NC) agent: %s\n" "$$f" "$$STATUS" "$$AGENT"; \
		fi; \
	done 2>/dev/null || printf "$(YELLOW)暂无任务$(NC)\n"

.PHONY: task-status
task-status: ## 显示任务状态概览
	@printf "$(CYAN)=== 任务状态概览 ===$(NC)\n"
	@PENDING=0; IN_PROGRESS=0; COMPLETED=0; BLOCKED=0; \
	for f in .ai-context/tasks/*.yaml; do \
		if [ "$$(basename $$f)" != "_template.yaml" ] && [ "$$(basename $$f)" != "_example.yaml" ]; then \
			STATUS=$$(grep -m1 "状态:" "$$f" 2>/dev/null | cut -d'"' -f2); \
			case $$STATUS in \
				待处理) PENDING=$$((PENDING+1)) ;; \
				进行中) IN_PROGRESS=$$((IN_PROGRESS+1)) ;; \
				已完成) COMPLETED=$$((COMPLETED+1)) ;; \
				已阻塞) BLOCKED=$$((BLOCKED+1)) ;; \
			esac; \
		fi; \
	done 2>/dev/null; \
	printf "$(YELLOW)待处理:   %d$(NC)\n" $$PENDING; \
	printf "$(CYAN)进行中:   %d$(NC)\n" $$IN_PROGRESS; \
	printf "$(GREEN)已完成:   %d$(NC)\n" $$COMPLETED; \
	printf "$(RED)已阻塞:   %d$(NC)\n" $$BLOCKED

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
