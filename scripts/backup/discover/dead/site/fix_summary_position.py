#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复快速导读位置 - 移到文章最开头
"""

import os
import re
import yaml
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

ALL_CATEGORIES = [
    "AI与机器学习", "系统与运维", "编程与开发", "数据库与存储",
    "云计算", "知识管理", "产品与设计", "人文社会", "行业动态", "其他",
]


def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}, content
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return {}, content
    fm_text = match.group(1)
    body = content[match.end():]
    try:
        fm = yaml.safe_load(fm_text)
        if fm is None:
            fm = {}
    except:
        fm = {}
    return fm, body


def build_frontmatter(fm):
    if not fm:
        return ""
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{fm_str}\n---\n\n"


def extract_and_remove_summary(body):
    """提取快速导读部分并从原文中移除"""
    # 匹配"快速导读"整个章节（从## 快速导读 到下一个 --- 或 ## 或 结尾
    pattern = r'(\n*---\n*\n*)?##\s*[📋🎯]?\s*快速导读.*?(?=\n---\n|\n##\s|\Z)'
    match = re.search(pattern, body, re.DOTALL)
    if match:
        summary_text = match.group(0)
        # 清理开头的换行和---
        summary_text = re.sub(r'^\n*---\n*\n*', '', summary_text)
        summary_text = summary_text.strip()
        # 从原文中移除
        body = body[:match.start()] + body[match.end():]
        return body, summary_text
    return body, None


def insert_summary_at_top(body, summary):
    """在文章开头插入快速导读（在第一个一级标题之后的元信息之后）"""
    # 找到第一个一级标题和其后的引用块（>开头的> 行）
    # 模式：# 标题\n> ... > ... \n\n 然后是正文
    pattern = r'(^#\s+.+?\n(?:>.*?\n)*\n*)'
    match = re.search(pattern, body, re.MULTILINE | re.DOTALL)
    if match:
        insert_pos = match.end()
        # 在插入点之后可能有空行，跳过
        while insert_pos < len(body) and body[insert_pos] in '\n\r':
            insert_pos += 1
        return body[:insert_pos] + '\n' + summary + '\n\n' + body[insert_pos:]
    return body


def main():
    print("=" * 70)
    print("修复快速导读位置")
    print("=" * 70)
    
    total = 0
    fixed = 0
    
    for category in ALL_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue
        
        cat_fixed = 0
        
        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            
            try:
                content = md_file.read_text(encoding="utf-8")
            except:
                continue
            
            fm, body = parse_frontmatter(content)
            total += 1
            
            # 检查快速导读位置
            summary_pos = body.find("快速导读")
            if summary_pos == -1:
                continue  # 没有快速导读，跳过
            
            # 检查是否在开头位置（前2000字符内）
            if summary_pos < 2000:
                continue  # 已经在开头了
            
            # 提取并移动
            new_body, summary = extract_and_remove_summary(body)
            if summary:
                new_body = insert_summary_at_top(new_body, summary)
                new_content = build_frontmatter(fm) + new_body
                md_file.write_text(new_content, encoding="utf-8")
                fixed += 1
                cat_fixed += 1
        
        print(f"  【{category}】修复: {cat_fixed} 篇")
    
    print(f"\n总计修复完成: {fixed}/{total} 篇")


if __name__ == "__main__":
    main()
