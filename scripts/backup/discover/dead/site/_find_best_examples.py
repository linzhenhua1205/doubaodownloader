#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
找出最满意的5篇增强示例
"""

import json
import random
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

# 各个分类中找一些有代表性的文章
representative_titles = [
    "2025-2030年AI超级周期深度分析：半导体、基础设施与全球技术格局重塑",
    "2025企业级AI Agent标准化白皮书：GraphRAG、MCP与Skills三大支柱重塑智能生",
    "2025年现代Node.js开发模式全解析 🚀",
    "2025年主流知识库系统深度评测：从开源到企业级解决方案全景分析",
    "Dify工作流实战指南：构建自动化研究助手与本地化部署",
]

def main():
    results = json.loads((BASE_DIR / 'quality_scan_results.json').read_text(encoding='utf-8'))
    articles = results['articles']
    
    # 找到这些代表性文章
    print("=" * 70)
    print("🎯 最满意的5篇增强示例")
    print("=" * 70)
    
    found = 0
    for art in articles:
        title = art['title']
        for rep_title in representative_titles:
            if rep_title in title:
                found += 1
                print(f"\n  【{found}】{title}")
                print(f"      分类: {art['category']}")
                print(f"      字数: {art['content_len']:,} 字")
                print(f"      质量: {art['quality_grade']}级 (得分: {art['quality_score']})")
                print(f"      类型: {art['article_type']}")
                print(f"      路径: {art['path']}")
                break
    
    if found < 5:
        # 从S级高分文章中补充
        high_score = sorted(articles, key=lambda x: x['quality_score'], reverse=True)
        for art in high_score:
            if found >= 5:
                break
            title = art['title']
            already = any(rep_title in title for rep_title in representative_titles)
            if not already:
                found += 1
                print(f"\n  【{found}】{title}")
                print(f"      分类: {art['category']}")
                print(f"      字数: {art['content_len']:,} 字")
                print(f"      质量: {art['quality_grade']}级 (得分: {art['quality_score']})")
                print(f"      类型: {art['article_type']}")
                print(f"      路径: {art['path']}")
    
    print("\n" + "=" * 70)
    
    # 读取第一篇示例文章的开头，展示增强效果
    print("\n📝 示例文章增强效果展示（第一篇的前80行）：")
    print("-" * 70)
    first_art = None
    for art in articles:
        if representative_titles[0] in art['title']:
            first_art = art
            break
    
    if first_art:
        content = Path(first_art['path']).read_text(encoding='utf-8')
        lines = content.split('\n')
        for i, line in enumerate(lines[:80]):
            print(f"  {i+1:3d}: {line}")

if __name__ == "__main__":
    main()
