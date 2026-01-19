# Parallel AI Agent Development Guide

> 使用 Git Worktree 实现多 AI Agent 并行开发的规范和流程

## 概述

本项目支持多个 AI Agent 同时进行开发工作，通过 Git Worktree 实现工作区隔离，通过任务文件实现职责划分。

## 目录结构

```
~/projects/
├── data-forge-ai/          # 主仓库 (main branch)
│   ├── .ai-context/
│   │   ├── CONTEXT.md      # 项目上下文
│   │   ├── PARALLEL_DEV.md # 本文档
│   │   └── tasks/          # 任务定义
│   │       ├── _template.yaml
│   │       └── *.yaml      # 各任务文件
│   └── ...
│
├── data-forge-ai-agent1/   # Agent 1 工作区
├── data-forge-ai-agent2/   # Agent 2 工作区
└── data-forge-ai-agent3/   # Agent 3 工作区
```

## 快速开始

### 1. 创建并行工作区

```bash
# 在主仓库目录执行
make parallel-setup AGENTS=3

# 或手动创建
git worktree add ../data-forge-ai-agent1 -b agent/task-1
git worktree add ../data-forge-ai-agent2 -b agent/task-2
```

### 2. 分配任务

在 `.ai-context/tasks/` 目录创建任务文件：

```bash
# 复制模板
cp .ai-context/tasks/_template.yaml .ai-context/tasks/implement-kafka-producer.yaml

# 编辑任务内容
```

### 3. 启动 Agent

每个工作区用独立的 IDE 窗口打开，AI Agent 会自动读取：
- `.ai-context/CONTEXT.md` - 项目整体上下文
- `.ai-context/tasks/<task>.yaml` - 当前任务定义

### 4. 合并成果

```bash
# 回到主仓库
cd data-forge-ai

# 查看各 agent 进度
make parallel-status

# 合并完成的分支
git merge agent/task-1
git merge agent/task-2

# 清理工作区
make parallel-clean
```

---

## 任务分配原则

### ✅ 适合并行的任务

| 类型 | 示例 |
|------|------|
| 独立模块 | 不同的微服务、独立的工具类 |
| 独立文档 | 各自的 README、API 文档 |
| 独立配置 | 不同环境的 Docker Compose |
| 独立测试 | 各模块的单元测试 |

### ❌ 不适合并行的任务

| 类型 | 原因 |
|------|------|
| 共享基础类 | 高冲突风险 |
| 全局配置文件 | 如 package.json、pom.xml |
| 紧密耦合的模块 | 接口变更影响双方 |

### 降低冲突的策略

1. **模块边界清晰** - 每个 agent 负责独立目录
2. **接口先行** - 先定义接口文件，各自实现
3. **避免格式化** - 不要在并行任务中做全局格式化
4. **小步提交** - 频繁提交，早发现冲突

---

## 任务文件规范

任务文件位于 `.ai-context/tasks/`，使用 YAML 格式：

```yaml
# .ai-context/tasks/<task-name>.yaml

task:
  id: "task-001"
  name: "实现 Kafka Producer 模块"
  status: pending  # pending | in_progress | completed | blocked
  
  # 分配信息
  assignment:
    agent: "agent1"           # 对应 worktree 名称
    branch: "agent/task-001"  # Git 分支名
    worktree: "../data-forge-ai-agent1"
  
  # 任务描述
  description: |
    实现 Kafka 消息生产者模块，用于发送训练数据到消息队列。
  
  # 具体目标
  objectives:
    - 创建 KafkaProducerService 类
    - 实现消息序列化
    - 添加重试机制
    - 编写单元测试
  
  # 工作范围（限制 agent 只修改这些路径）
  scope:
    allowed_paths:
      - "src/data-pipeline/kafka/"
      - "tests/data-pipeline/kafka/"
      - "docs/kafka-producer.md"
    forbidden_paths:
      - "src/shared/"
      - "*.lock"
  
  # 依赖关系
  dependencies:
    requires: []              # 前置任务
    blocks: ["task-003"]      # 被此任务阻塞的任务
  
  # 接口约定（与其他任务的协作点）
  interfaces:
    provides:
      - name: "KafkaProducerService"
        type: "class"
        path: "src/data-pipeline/kafka/producer.py"
    consumes:
      - name: "ConfigLoader"
        type: "class"
        from_task: "task-002"
  
  # 验收标准
  acceptance_criteria:
    - "所有测试通过"
    - "代码覆盖率 > 80%"
    - "文档完整"
  
  # 进度记录（Agent 更新）
  progress:
    started_at: null
    completed_at: null
    notes: []
```

---

## 命令参考

```bash
# === 工作区管理 ===
make parallel-setup AGENTS=3    # 创建 3 个并行工作区
make parallel-status            # 查看所有工作区状态
make parallel-clean             # 清理所有工作区

# === 单个工作区 ===
make worktree-add NAME=agent1 BRANCH=feature/xxx
make worktree-remove NAME=agent1

# === 任务管理 ===
make task-new NAME=my-task      # 从模板创建新任务
make task-list                  # 列出所有任务
make task-status                # 显示任务状态概览

# === 合并流程 ===
make parallel-merge BRANCH=agent/task-1  # 合并指定分支
make parallel-merge-all                   # 合并所有已完成任务
```

---

## AI Agent 工作指引

当你作为 AI Agent 在某个工作区工作时：

### 1. 首先阅读

```
.ai-context/CONTEXT.md          # 项目整体上下文
.ai-context/tasks/<your-task>.yaml  # 你的任务定义
```

### 2. 遵守边界

- **只修改** `scope.allowed_paths` 中的文件
- **不要触碰** `scope.forbidden_paths` 中的文件
- 如需修改共享文件，在 `progress.notes` 中记录需求

### 3. 更新进度

任务开始时：
```yaml
progress:
  started_at: "2024-01-20T10:00:00Z"
  notes:
    - "开始分析需求"
```

任务完成时：
```yaml
status: completed
progress:
  completed_at: "2024-01-20T15:00:00Z"
  notes:
    - "开始分析需求"
    - "完成核心实现"
    - "测试全部通过"
```

### 4. 处理依赖

如果依赖其他任务的接口：
1. 检查 `interfaces.consumes` 中定义的接口
2. 如果接口文件不存在，先创建 stub/mock
3. 在 `progress.notes` 中记录依赖状态

### 5. 提交规范

```bash
# 提交信息格式
git commit -m "[task-001] 实现 KafkaProducerService 基础结构"
git commit -m "[task-001] 添加消息序列化逻辑"
git commit -m "[task-001] 完成单元测试"
```

---

## 冲突处理

### 预防

1. 任务设计时划分清晰的文件边界
2. 共享代码提前提取到独立任务
3. 接口文件由专人维护或先于实现确定

### 解决

```bash
# 在主仓库操作
cd data-forge-ai

# 获取最新代码
git fetch --all

# 合并时遇到冲突
git merge agent/task-1
# CONFLICT in src/shared/utils.py

# 查看冲突详情
git diff

# 手动解决后
git add .
git commit -m "Merge agent/task-1, resolve conflicts in utils.py"
```

---

## 最佳实践

### 任务粒度

- ✅ **2-4小时** 可完成的任务
- ❌ 过大（超过1天）或过小（几分钟）的任务

### 并行数量

- **推荐**: 2-4 个并行 agent
- **不推荐**: 超过 5 个（合并成本急剧上升）

### 同步频率

- 每完成一个子目标就提交
- 每天至少同步一次主分支的变更

```bash
# 在 agent 工作区中同步主分支
git fetch origin main
git rebase origin/main
```

---

## 示例：并行开发数据管道

```yaml
# Task 1: Kafka Producer (Agent 1)
scope:
  allowed_paths:
    - "src/pipeline/kafka/producer/"
    - "tests/pipeline/kafka/producer/"

# Task 2: Kafka Consumer (Agent 2)  
scope:
  allowed_paths:
    - "src/pipeline/kafka/consumer/"
    - "tests/pipeline/kafka/consumer/"

# Task 3: Spark Job (Agent 3)
scope:
  allowed_paths:
    - "src/pipeline/spark/"
    - "tests/pipeline/spark/"

# 共享接口（先由主分支定义）
# src/pipeline/interfaces/message.py - 消息格式定义
# src/pipeline/interfaces/config.py  - 配置接口定义
```

这样三个 Agent 可以完全独立工作，最后无冲突合并。
