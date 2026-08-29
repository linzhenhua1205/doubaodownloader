#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from extract_user_questions import export_user_questions
from analyze_topic_boundaries import analyze_topic_boundaries
from generate_intent_report import generate_intent_report


def main():
    parser = argparse.ArgumentParser(description='会话意图分析工具')
    parser.add_argument('--step', choices=['extract', 'analyze', 'report', 'all'], 
                        default='all', help='执行步骤')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("会话意图分析工具 v1.0")
    print("=" * 60)
    
    if args.step in ['extract', 'all']:
        print("\n[步骤1] 提取用户问题（去除定时任务）")
        print("-" * 40)
        if not args.dry_run:
            export_user_questions()
        else:
            print("模拟模式：跳过提取")
    
    if args.step in ['analyze', 'all']:
        print("\n[步骤2] 分析话题边界和任务切换")
        print("-" * 40)
        if not args.dry_run:
            analyze_topic_boundaries()
        else:
            print("模拟模式：跳过分析")
    
    if args.step in ['report', 'all']:
        print("\n[步骤3] 生成意图分析报告")
        print("-" * 40)
        if not args.dry_run:
            generate_intent_report()
        else:
            print("模拟模式：跳过报告生成")
    
    print("\n" + "=" * 60)
    print("分析流程完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()