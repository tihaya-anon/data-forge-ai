# 并行 AI Agent 开发指南

> 使用 Git Worktree + 任务 DAG 实现多 AI Agent 高效并行开发

## 概述

本项目支持多个 AI Agent 同时进行开发工作：
- **任务清单** (`tasks.yaml`) - 集中定义所有任务及依赖关系
- **DAG 分析** - 自动计算并行度、关键路径、推荐 agent 数量
- **Git Worktree** - 为每个 agent 创建独立工作区

## 目录结构

```
.ai-context/
├── CONTEXT.md              # 项目上下文
├── PARALLEL_DEV.md         # 本文档
├── tasks/
│   └── tasks.yaml          # 任务清单（核心文件）
└── scripts/
    └── task_dag.py         # DAG 分析脚本

~/projects/
├── data-forge-ai/          # 主仓库 (main 分支)
├── data-forge-ai-agent1/   # Agent 1 工作区
├── data-forge-ai-agent2/   # Agent 2 工作区
└── data-forge-ai-agent3/   # Agent 3 工作区
```

## 快速开始

### 1. 分析任务并行度

```bash
# 查看完整分析报告
make task-analyze

# 输出示例：
# 📊 基本统计
#    总任务数:     11
#    总工时:       55 小时
#
# 📈 并行度分析
#    最大并行度:   3 (出现 2 次)
#    平均并行度:   2.2
#
# 🤖 Agent 数量建议
#    推荐:    2 个 ⭐
#    最多:    3 个
```

### 2. 生成 DAG 可视化

```bash
# 生成 D2 文件和 SVG 图
make task-dag

# 输出: docs/diagrams/task-dag.d2
#       docs/images/task-dag.svg
```

### 3. 创建并行工作区

```bash
# 根据建议创建工作区（假设建议 2 个）
make parallel-setup AGENTS=2

# 创建结果：
# ../data-forge-ai-agent1/  (分支: agent/workspace-1)
# ../data-forge-ai-agent2/  (分支: agent/workspace-2)
```

### 4. 分配任务给 Agent

编辑 `tasks.yaml`，为每个任务分配 agent：

```yaml
任务:
  - 编号: "T-001"
    名称: "Docker 基础配置"
    分配: "agent1"    # 添加分配
    状态: "进行中"    # 更新状态
    # ...
```

### 5. 启动 Agent

在独立 IDE 窗口中打开各工作区，AI Agent 会读取：
- `.ai-context/CONTEXT.md` - 项目上下文
- `.ai-context/tasks/tasks.yaml` - 找到自己的任务

### 6. 合并成果

```bash
# 查看进度
make parallel-status

# 合并完成的分支
make parallel-merge BRANCH=agent/workspace-1

# 清理
make parallel-clean
```

---

## 任务清单格式

任务定义在 `.ai-context/tasks/tasks.yaml`：

```yaml
任务:
  - 编号: "T-001"           # 唯一标识
    名称: "Docker 基础配置"  # 简短描述
    工时: 2                  # 预估小时数
    依赖: []                 # 前置任务编号列表
    状态: "待处理"           # 待处理 | 进行中 | 已完成 | 已阻塞
    分配: ""                 # agent 编号（执行时填写）
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

## DAG 分析详解

### 并行度指标

| 指标 | 说明 |
|------|------|
| **最大并行度** | 同时可执行的最多任务数 |
| **平均并行度** | 各层级并行度的平均值 |
| **加权平均** | 按工时加权的并行度，更准确 |

### 为什么不用最大并行度？

```
示例：5 层任务，最大并行度 5，但只在第 1 层出现一次

第 0 层: [5 个任务] ← 最大并行度
第 1 层: [2 个任务]
第 2 层: [2 个任务]
第 3 层: [2 个任务]
第 4 层: [1 个任务]

如果配置 5 个 agent：
- 第 0 层后，3 个 agent 空闲
- 资源利用率低

建议使用加权平均（如 2-3 个 agent）
```

### 关键路径

关键路径是 DAG 中最长的路径，决定了项目最短完成时间。

```
关键路径: T-001 → T-004 → T-007 → T-009 → T-011
总工时: 26 小时

即使无限多 agent，也至少需要 26 小时
```

---

## 命令参考

```bash
# === DAG 分析 ===
make task-analyze      # 分析并行度和关键路径
make task-dag          # 生成 DAG 可视化图
make task-edit         # 编辑任务清单

# === 工作区管理 ===
make parallel-setup AGENTS=3    # 创建 N 个并行工作区
make parallel-status            # 查看所有工作区状态
make parallel-clean             # 清理工作区（保留分支）
make parallel-clean-all         # 清理工作区和分支

# === 合并操作 ===
make parallel-merge BRANCH=xxx  # 合并指定分支
make parallel-diff              # 查看分支差异
make parallel-sync              # 同步主分支更新
```

---

## AI Agent 工作指引

### 1. 识别自己的任务

查看 `tasks.yaml` 中 `分配` 字段与自己匹配的任务：

```yaml
- 编号: "T-004"
  分配: "agent1"    # 如果你是 agent1，这是你的任务
  状态: "进行中"
```

### 2. 遵守范围

只修改任务 `范围` 中指定的路径：

```yaml
范围:
  - "src/pipeline/kafka/producer/"
  - "tests/pipeline/kafka/producer/"
```

### 3. 检查依赖

确保 `依赖` 中的任务已完成：

```yaml
依赖: ["T-001", "T-006"]  # 必须等这两个完成
```

### 4. 更新状态

完成后更新 `tasks.yaml`：

```yaml
状态: "已完成"
```

### 5. 提交规范

```bash
git commit -m "[T-004] 实现 Kafka Producer 基础结构"
git commit -m "[T-004] 添加重试机制"
git commit -m "[T-004] 完成单元测试"
```

---

## 最佳实践

### 任务设计

- ✅ 每个任务 **2-8 小时**
- ✅ 明确的 **文件边界**（范围不重叠）
- ✅ 清晰的 **依赖关系**
- ❌ 避免多任务修改同一文件

### Agent 数量选择

| 场景 | 建议 |
|------|------|
| 快速完成 | 使用最大并行度 |
| 资源有限 | 使用推荐值（加权平均） |
| 稳定优先 | 使用最少值 |

### 依赖冲突预防

1. **先定义接口** - 共享的类/函数先确定签名
2. **独立目录** - 每个任务对应独立目录
3. **避免全局修改** - 不要在并行任务中格式化/重构

---

## 示例：完整工作流

```bash
# 1. 查看分析
make task-analyze
# 输出: 推荐 2 个 agent

# 2. 生成 DAG 图（可选，用于审查）
make task-dag

# 3. 编辑任务分配
make task-edit
# 将第 0 层任务分配给 agent1、agent2

# 4. 创建工作区
make parallel-setup AGENTS=2

# 5. 打开 IDE
# - 窗口 1: ../data-forge-ai-agent1/
# - 窗口 2: ../data-forge-ai-agent2/

# 6. Agent 开始工作...

# 7. 查看进度
make parallel-status

# 8. 合并
make parallel-merge BRANCH=agent/workspace-1
make parallel-merge BRANCH=agent/workspace-2

# 9. 清理
make parallel-clean
```
