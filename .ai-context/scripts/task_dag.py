#!/usr/bin/env python3
"""
任务 DAG 分析工具

功能：
1. 解析 tasks.yaml 生成依赖关系图
2. 生成 D2 格式的可视化 DAG
3. 分析并行度、关键路径
4. 给出 agent 数量建议
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# =============================================================================
# 数据加载
# =============================================================================

def load_tasks(filepath: str) -> dict:
    """加载任务配置文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# =============================================================================
# DAG 分析
# =============================================================================

def build_graph(tasks: List[dict]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], Dict[str, dict]]:
    """
    构建图结构
    返回: (邻接表, 反向邻接表, 任务详情字典)
    """
    graph = defaultdict(list)       # 任务 -> 后继任务列表
    reverse = defaultdict(list)     # 任务 -> 前置任务列表
    details = {}                    # 任务 -> 详情
    
    for task in tasks:
        tid = task['编号']
        details[tid] = task
        for dep in task.get('依赖', []):
            graph[dep].append(tid)
            reverse[tid].append(dep)
    
    return dict(graph), dict(reverse), details


def topological_sort(tasks: List[dict]) -> List[str]:
    """拓扑排序"""
    graph, reverse, _ = build_graph(tasks)
    all_tasks = {t['编号'] for t in tasks}
    
    # 计算入度
    in_degree = {t: 0 for t in all_tasks}
    for tid in all_tasks:
        in_degree[tid] = len(reverse.get(tid, []))
    
    # BFS
    queue = [t for t in all_tasks if in_degree[t] == 0]
    result = []
    
    while queue:
        queue.sort()  # 保证顺序稳定
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result


def compute_levels(tasks: List[dict]) -> Dict[str, int]:
    """
    计算每个任务的层级（最早可开始时间）
    层级 = max(所有前置任务的层级) + 1
    """
    graph, reverse, details = build_graph(tasks)
    all_tasks = {t['编号'] for t in tasks}
    levels = {}
    
    sorted_tasks = topological_sort(tasks)
    
    for tid in sorted_tasks:
        deps = reverse.get(tid, [])
        if not deps:
            levels[tid] = 0
        else:
            levels[tid] = max(levels[dep] for dep in deps) + 1
    
    return levels


def analyze_parallelism(tasks: List[dict]) -> dict:
    """
    分析并行度
    返回每一层的任务数量和统计信息
    """
    levels = compute_levels(tasks)
    _, _, details = build_graph(tasks)
    
    # 按层级分组
    level_tasks = defaultdict(list)
    for tid, level in levels.items():
        level_tasks[level].append(tid)
    
    # 统计
    parallelism_per_level = []
    total_hours_per_level = []
    
    for level in sorted(level_tasks.keys()):
        tids = level_tasks[level]
        parallelism_per_level.append(len(tids))
        hours = sum(details[tid].get('工时', 0) or 0 for tid in tids)
        total_hours_per_level.append(hours)
    
    max_parallelism = max(parallelism_per_level)
    max_count = parallelism_per_level.count(max_parallelism)
    avg_parallelism = sum(parallelism_per_level) / len(parallelism_per_level)
    
    # 计算加权建议（考虑每层的工时）
    weighted_sum = sum(p * h for p, h in zip(parallelism_per_level, total_hours_per_level))
    total_hours = sum(total_hours_per_level)
    weighted_avg = weighted_sum / total_hours if total_hours > 0 else avg_parallelism
    
    return {
        'levels': dict(level_tasks),
        'parallelism_per_level': parallelism_per_level,
        'hours_per_level': total_hours_per_level,
        'max_parallelism': max_parallelism,
        'max_parallelism_count': max_count,
        'avg_parallelism': avg_parallelism,
        'weighted_avg_parallelism': weighted_avg,
        'total_levels': len(level_tasks),
        'total_tasks': len(tasks),
        'total_hours': total_hours,
    }


def find_critical_path(tasks: List[dict]) -> Tuple[List[str], int]:
    """
    找到关键路径（最长路径）
    返回: (路径上的任务列表, 总工时)
    """
    graph, reverse, details = build_graph(tasks)
    all_tasks = {t['编号'] for t in tasks}
    
    # 动态规划计算最长路径
    sorted_tasks = topological_sort(tasks)
    
    dist = {t: details[t].get('工时', 0) or 0 for t in all_tasks}
    parent = {t: None for t in all_tasks}
    
    for tid in sorted_tasks:
        for neighbor in graph.get(tid, []):
            new_dist = dist[tid] + (details[neighbor].get('工时', 0) or 0)
            if new_dist > dist[neighbor]:
                dist[neighbor] = new_dist
                parent[neighbor] = tid
    
    # 找到终点（最大距离的节点）
    end_node = max(dist.keys(), key=lambda x: dist[x])
    
    # 回溯路径
    path = []
    node = end_node
    while node:
        path.append(node)
        node = parent[node]
    path.reverse()
    
    return path, dist[end_node]


def suggest_agents(analysis: dict) -> dict:
    """
    根据分析结果建议 agent 数量
    """
    max_p = analysis['max_parallelism']
    max_count = analysis['max_parallelism_count']
    avg_p = analysis['avg_parallelism']
    weighted_avg = analysis['weighted_avg_parallelism']
    total_levels = analysis['total_levels']
    
    # 建议策略
    suggestions = {
        'minimum': max(1, int(avg_p)),
        'recommended': max(1, round(weighted_avg)),
        'maximum': max_p,
    }
    
    # 理由
    reasons = []
    
    if max_count <= total_levels * 0.2:  # 最大并行度只出现在 20% 的层级
        reasons.append(f"最大并行度 {max_p} 仅在 {max_count}/{total_levels} 层出现")
        reasons.append(f"建议使用 {suggestions['recommended']} 个 agent（加权平均）")
    else:
        reasons.append(f"最大并行度 {max_p} 在 {max_count}/{total_levels} 层出现")
        reasons.append(f"可考虑使用 {max_p} 个 agent 以最大化并行")
    
    # 时间估算
    total_hours = analysis['total_hours']
    serial_time = total_hours
    parallel_time_max = total_hours / max_p if max_p > 0 else total_hours
    parallel_time_rec = total_hours / suggestions['recommended'] if suggestions['recommended'] > 0 else total_hours
    
    suggestions['time_estimate'] = {
        'serial': serial_time,
        'parallel_max': round(parallel_time_max, 1),
        'parallel_recommended': round(parallel_time_rec, 1),
    }
    
    suggestions['reasons'] = reasons
    
    return suggestions


# =============================================================================
# D2 DAG 生成
# =============================================================================

def generate_d2(tasks: List[dict], config: dict, analysis: dict) -> str:
    """生成 D2 格式的 DAG 图"""
    levels = compute_levels(tasks)
    _, _, details = build_graph(tasks)
    
    status_colors = config.get('状态颜色', {})
    
    lines = [
        "# 任务依赖 DAG",
        "# 自动生成，请勿手动编辑",
        "",
        "direction: down",
        "",
    ]
    
    # 定义节点
    lines.append("# 任务节点")
    for task in tasks:
        tid = task['编号']
        name = task['名称']
        hours = task.get('工时', '?')
        status = task.get('状态', '待处理')
        color = status_colors.get(status, '#9E9E9E')
        level = levels[tid]
        
        # 节点定义
        label = f"{tid}\\n{name}\\n({hours}h)"
        lines.append(f'{tid}: "{label}" {{')
        lines.append(f'  style.fill: "{color}"')
        lines.append(f'  style.stroke: "{color}"')
        if status == '已完成':
            lines.append('  style.opacity: 0.6')
        lines.append('}')
    
    lines.append("")
    lines.append("# 依赖关系")
    
    # 定义边
    for task in tasks:
        tid = task['编号']
        for dep in task.get('依赖', []):
            lines.append(f"{dep} -> {tid}")
    
    # 添加图例
    lines.extend([
        "",
        "# 图例",
        "legend: {",
        '  label: "图例"',
        "  near: bottom-center",
        "  待处理: {style.fill: \"#9E9E9E\"}",
        "  进行中: {style.fill: \"#2196F3\"}",
        "  已完成: {style.fill: \"#4CAF50\"}",
        "  已阻塞: {style.fill: \"#F44336\"}",
        "}",
    ])
    
    return '\n'.join(lines)


# =============================================================================
# 报告生成
# =============================================================================

def print_analysis_report(tasks: List[dict], analysis: dict, critical_path: Tuple[List[str], int], suggestions: dict):
    """打印分析报告"""
    _, _, details = build_graph(tasks)
    
    print("\n" + "=" * 60)
    print("  任务 DAG 分析报告")
    print("=" * 60)
    
    # 基本统计
    print(f"\n📊 基本统计")
    print(f"   总任务数:     {analysis['total_tasks']}")
    print(f"   总工时:       {analysis['total_hours']} 小时")
    print(f"   层级数:       {analysis['total_levels']}")
    
    # 并行度分析
    print(f"\n📈 并行度分析")
    print(f"   最大并行度:   {analysis['max_parallelism']} (出现 {analysis['max_parallelism_count']} 次)")
    print(f"   平均并行度:   {analysis['avg_parallelism']:.1f}")
    print(f"   加权平均:     {analysis['weighted_avg_parallelism']:.1f}")
    
    # 每层详情
    print(f"\n📋 各层级任务")
    for level, tids in sorted(analysis['levels'].items()):
        tasks_str = ', '.join(tids)
        hours = sum(details[t].get('工时', 0) or 0 for t in tids)
        print(f"   第 {level} 层: [{len(tids)} 个任务, {hours}h] {tasks_str}")
    
    # 关键路径
    path, path_hours = critical_path
    print(f"\n🔴 关键路径 ({path_hours} 小时)")
    print(f"   {' → '.join(path)}")
    
    # Agent 建议
    print(f"\n🤖 Agent 数量建议")
    print(f"   最少:    {suggestions['minimum']} 个")
    print(f"   推荐:    {suggestions['recommended']} 个 ⭐")
    print(f"   最多:    {suggestions['maximum']} 个")
    
    for reason in suggestions['reasons']:
        print(f"   💡 {reason}")
    
    # 时间估算
    te = suggestions['time_estimate']
    print(f"\n⏱️  时间估算")
    print(f"   串行执行:         {te['serial']} 小时")
    print(f"   {suggestions['recommended']} 个 agent 并行:  ~{te['parallel_recommended']} 小时")
    print(f"   {suggestions['maximum']} 个 agent 并行:  ~{te['parallel_max']} 小时")
    
    print("\n" + "=" * 60 + "\n")


# =============================================================================
# 主函数
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='任务 DAG 分析工具')
    parser.add_argument('--tasks', '-t', default='.ai-context/tasks/tasks.yaml',
                        help='任务配置文件路径')
    parser.add_argument('--output', '-o', default='docs/diagrams/task-dag.d2',
                        help='D2 输出文件路径')
    parser.add_argument('--analyze-only', '-a', action='store_true',
                        help='仅分析，不生成 D2 文件')
    parser.add_argument('--generate-only', '-g', action='store_true',
                        help='仅生成 D2 文件，不打印分析')
    
    args = parser.parse_args()
    
    # 加载数据
    try:
        data = load_tasks(args.tasks)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.tasks}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"错误: YAML 解析失败 - {e}")
        sys.exit(1)
    
    tasks = data.get('任务', [])
    config = data.get('DAG配置', {})
    
    if not tasks:
        print("警告: 没有找到任务定义")
        sys.exit(0)
    
    # 分析
    analysis = analyze_parallelism(tasks)
    critical_path = find_critical_path(tasks)
    suggestions = suggest_agents(analysis)
    
    # 打印报告
    if not args.generate_only:
        print_analysis_report(tasks, analysis, critical_path, suggestions)
    
    # 生成 D2
    if not args.analyze_only:
        d2_content = generate_d2(tasks, config, analysis)
        
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(d2_content)
        
        print(f"✅ D2 文件已生成: {output_path}")
        print(f"   运行 'd2 {output_path}' 生成 SVG 图片")


if __name__ == '__main__':
    main()
