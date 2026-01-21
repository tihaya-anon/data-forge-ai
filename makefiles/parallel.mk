# makefiles/parallel.mk - 任务管理（优化为 Claude Code 工作流）
# 任务规划和跟踪命令

# 任务文件路径
TASKS_FILE := .ai-context/tasks/tasks.yaml
DAG_SCRIPT := .ai-context/scripts/task_dag.py
DAG_OUTPUT := docs/diagrams/task-dag.d2

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
