# 任务管理工作流（使用 Git Worktree 并行开发）

> 使用任务 DAG 规划 + Git Worktree 多工作区并行执行

## 概述

本项目使用结构化的任务管理方法：
- **任务清单** (`tasks.yaml`) - 集中定义所有任务及依赖关系
- **DAG 分析** - 自动计算并行度、关键路径
- **Git Worktree 并行执行** - 多个 AI Agent 在独立工作区并行完成任务

## 目录结构

```
ai-context/
├── CONTEXT.md              # 项目上下文
├── PARALLEL_DEV.md         # 本文档
├── tasks/
│   └── tasks.yaml          # 任务清单（核心文件）
└── scripts/
    └── task_dag.py         # DAG 分析脚本
```

## 快速开始

### 1. 查看任务概览

```bash
# 查看所有任务及状态
make task-list

# 查看任务完成进度
make task-status

# 查看下一个可执行的任务
make task-next
```

### 2. 分析任务结构

```bash
# 查看完整分析报告（并行度、关键路径）
make task-analyze

# 生成 DAG 可视化图
make task-dag
```

### 3. 设置并行开发环境

AI Agents 会：
1. 读取 `tasks.yaml` 了解任务结构和依赖关系
2. 根据分析结果创建独立的 Git Worktree
3. 在各自的工作区中并行执行任务
4. 完成后更新主分支的 `tasks.yaml` 中的状态

---

## 任务清单格式

任务定义在 `ai-context/tasks/tasks.yaml`：

```yaml
任务:
  - 编号: "T-001"           # 唯一标识
    名称: "Docker 基础配置"  # 简短描述
    工时: 2                  # 预估小时数
    依赖: []                 # 前置任务编号列表
    状态: "待处理"           # 待处理 | 进行中 | 已完成 | 已阻塞
    范围:                    # 允许修改的路径
      - "docker/"
    描述: |                  # 详细说明
      配置 Docker 网络、卷、基础存储服务
```

### 状态流转

```
待处理 → 进行中 → 已完成
           ↓
        已阻塞 → 进行中
```

---

## 命令参考

```bash
# === 任务查看 ===
make task-list         # 列出所有任务及状态
make task-next         # 显示下一个可执行的任务
make task-status       # 显示任务完成进度
make task-edit         # 编辑任务清单

# === 并行开发 ===
make parallel-setup AGENTS=3   # 创建 3 个工作树用于并行开发
make parallel-status           # 查看工作树状态
make parallel-sync             # 同步所有工作树的最新更改
make parallel-delete-all       # 删除所有并行工作树

# === DAG 分析 ===
make task-analyze      # 分析并行度和关键路径
make task-dag          # 生成 DAG 可视化图
```

---

## Git Worktree 并行开发工作流

### 1. 初始化并行环境

```bash
# 分析任务并行度，获取建议的 Agent 数量
make task-analyze

# 创建多个工作树用于并行开发（例如，创建3个工作树）
make parallel-setup AGENTS=3
```

这将创建类似如下的目录结构：
```
project-root/
├── .git/
├── ai-context/
├── main-workspace/          # 主工作区
├── agent-workspace-1/       # Agent 1 的独立工作区
├── agent-workspace-2/       # Agent 2 的独立工作区
└── agent-workspace-3/       # Agent 3 的独立工作区
```

### 2. 分配任务给不同 Agent

根据 DAG 分析结果，将无依赖的任务分配给不同的 Agent：

```bash
# 查看可并行执行的任务
make task-next
```

输出示例：
```
============================================================
  下一个可执行的任务
============================================================

📋 T-001: Docker 基础配置
   工时: 2 小时
   状态: 待处理
   范围: docker/compose.base.yml, docker/compose.storage.yml
   描述: 配置 Docker 网络、卷、基础存储服务

📋 T-002: Makefile 框架搭建
   工时: 2 小时
   状态: 待处理
   范围: Makefile, makefiles/*.mk
   描述: 完善 Makefile 命令结构

📋 T-003: CI/CD 流水线
   工时: 2 小时
   状态: 待处理
   范围: .github/workflows/
   描述: 配置 GitHub Actions，自动测试、构建、生成文档
```

### 3. Agent 独立执行任务

每个 Agent 在其独立的工作树中执行分配的任务：

```bash
# Agent 1 在其工作树中执行 T-001
cd agent-workspace-1
# 修改指定范围内的文件
git add .
git commit -m "[T-001] 完成 Docker 基础配置"

# Agent 2 在其工作树中执行 T-002
cd agent-workspace-2
# 修改指定范围内的文件
git add .
git commit -m "[T-002] 完成 Makefile 框架搭建"

# Agent 3 在其工作树中执行 T-003
cd agent-workspace-3
# 修改指定范围内的文件
git add .
git commit -m "[T-003] 完成 CI/CD 流水线配置"
```

### 4. 同步和合并更改

```bash
# 各 Agent 将更改推送到主工作区
# 在主项目根目录执行
make parallel-sync
```

### 5. 更新任务状态

- 完成任务后，相关 Agent 更新主分支 `tasks.yaml` 中的状态为 "已完成"
- 各工作树会定期同步最新的任务分配情况

---

## Git Worktree 管理

### 创建工作树

```bash
# 创建单个工作树
git worktree add ../agent-workspace-1 agent-1

# 脚本化创建多个工作树
make parallel-setup AGENTS=3  # 创建 3 个并行工作树
```

### 查看工作树状态

```bash
# 查看所有工作树
git worktree list

# 使用项目命令查看
make parallel-status
```

### 同步工作树

```bash
# 拉取所有最新更改
make parallel-sync

# 手动同步特定工作树
cd agent-workspace-1
git pull origin main
```

### 清理工作树

```bash
# 删除所有并行工作树
make parallel-delete-all

# 手动删除特定工作树
git worktree remove agent-workspace-1
```

---

## DAG 分析详解

### 并行度指标

| 指标           | 说明                   |
| -------------- | ---------------------- |
| **最大并行度** | 同时可执行的最多任务数 |
| **平均并行度** | 各层级并行度的平均值   |
| **加权平均**   | 按工时加权的并行度     |

### 关键路径

关键路径是 DAG 中最长的路径，决定了项目最短完成时间。

```
关键路径: T-001 → T-004 → T-007 → T-009 → T-011
总工时: 26 小时
```

---

## 最佳实践

### 任务设计

- ✅ 每个任务 **2-8 小时**
- ✅ 明确的 **文件边界**（范围不重叠）
- ✅ 清晰的 **依赖关系**
- ❌ 避免多任务修改同一文件

### 依赖管理

1. **先定义接口** - 共享的类/函数先确定签名
2. **独立目录** - 每个任务对应独立目录
3. **避免全局修改** - 不要在并行任务中格式化/重构

### Worktree 协作

1. **频繁同步** - 定期从主分支拉取最新更改
2. **小步提交** - 频繁提交小的、集中的更改
3. **清晰提交信息** - 包含任务编号的提交消息
4. **避免冲突** - 严格遵守分配的文件范围

---

## 与 Claude Code 单会话的区别

| 方面     | 原工作流（Claude Code） | 新工作流（Git Worktree） |
| -------- | ----------------------- | ------------------------ |
| 执行模型 | 单个 AI 会话            | 多个独立 AI Agent        |
| 工作区   | 单个工作区              | 多个 Git Worktree        |
| 并行方式 | Task tool 子 agent      | 物理隔离的工作树         |
| 协调方式 | 会话内上下文            | 通过 tasks.yaml 文件     |
| 适用场景 | Claude Code 专用        | 多 Agent 并行开发        |

---

## 示例：完整工作流

```bash
# 1. 查看任务结构
make task-analyze
# 输出: 11 个任务，5 层，推荐 2 个并行度

# 2. 创建并行工作环境
make parallel-setup AGENTS=2

# 3. 查看可执行任务
make task-next
# 输出: T-001, T-002, T-003 可以开始

# 4. Agent 分别在独立工作树中工作
# Agent 1 在 agent-workspace-1 处理 T-001
# Agent 2 在 agent-workspace-2 处理 T-002
# Agent 3 在主工作区处理 T-003

# 5. 各 Agent 完成任务后提交更改
# 在各自的工作树中执行
git add .
git commit -m "[T-XXX] 完成具体任务"
git push origin <branch>

# 6. 同步所有更改并更新任务状态
make parallel-sync
# 更新 ai-context/tasks/tasks.yaml 中的状态为 "已完成"

# 7. 查看进度
make task-status
# 输出: 3/11 已完成 (27.3%)

# 8. 继续下一批任务
make task-next
# 输出: T-004, T-005, T-006 现在可以开始
```

---

## 提交规范

```bash
git commit -m "[T-004] 实现 Kafka Producer 基础结构"
git commit -m "[T-004] 添加重试机制"
git commit -m "[T-004] 完成单元测试"
```

---

## 常见问题

**Q: 为什么使用 Git worktree？**
A: Git worktree 为每个 AI Agent 提供了物理隔离的工作空间，允许多个 Agent 同时处理不同的任务而不会相互干扰。每个工作树都是独立的 Git 工作目录，有自己的分支状态和暂存区。

**Q: 如何处理任务依赖？**
A: `make task-next` 会自动检查依赖，只显示前置任务已完成的任务。并行执行的 Agent 需要定期同步主分支，确保依赖状态是最新的。

**Q: 如何防止多个 Agent 之间的冲突？**
A: 通过明确的任务范围定义和文件边界控制来避免冲突。每个任务都有明确的 [范围](file:///home/smsmu/remote_env/data-forge-ai/ai-context/tasks/tasks.yaml#L205-L205) 字段，限制了可修改的文件路径。

**Q: 如何添加新任务？**
A: 编辑 `tasks.yaml`，添加新任务定义，运行 `make task-dag` 更新可视化图。

**Q: 如何处理合并冲突？**
A: 定期执行 `make parallel-sync` 同步所有更改；如果发生冲突，使用 `git merge` 或 `git rebase` 手动解决；建议将大型更改分解为多个小任务以减少冲突概率。