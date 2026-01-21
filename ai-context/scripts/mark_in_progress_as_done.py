#!/usr/bin/env python3
"""
将所有"进行中"的任务标记为"已完成"
"""

import yaml
import sys
from pathlib import Path


def mark_in_progress_as_done(tasks_file_path):
    """将所有"进行中"的任务标记为"已完成" """
    # 读取任务文件
    with open(tasks_file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # 更新任务状态
    updated = 0
    for task in data.get('任务', []):
        if task.get('状态') == '进行中':
            task['状态'] = '已完成'
            print(f"Updated: {task['编号']} - {task['名称']}")
            updated += 1

    # 写回文件
    with open(tasks_file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    print(f'\n✅ 总共更新了 {updated} 个任务的状态')
    return updated


def main():
    if len(sys.argv) != 2:
        print("用法: python mark_in_progress_as_done.py <任务文件路径>")
        sys.exit(1)

    tasks_file_path = sys.argv[1]
    mark_in_progress_as_done(tasks_file_path)


if __name__ == '__main__':
    main()