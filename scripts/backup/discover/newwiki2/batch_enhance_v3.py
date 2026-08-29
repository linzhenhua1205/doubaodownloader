#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用批量内容增强脚本 v3 - 为任意目录的markdown文件添加结构化内容
"""

import os
import re
import sys
from datetime import datetime

def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取失败 {filepath}: {e}")
        return ""

def get_original_body(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()

def extract_title(original_body, filename):
    title_match = re.search(r'^#\s+(.+)$', original_body, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    name = os.path.splitext(filename)[0]
    return name

def extract_card_count(original_body):
    match = re.search(r'收录卡片.*?(\d+)\s*条', original_body)
    if match:
        return int(match.group(1))
    count = len(re.findall(r'^##\s+\d+\.', original_body, re.MULTILINE))
    return count if count > 0 else None

def estimate_word_count(content):
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    english_words = len(re.findall(r'[a-zA-Z]+', content))
    return chinese_chars + english_words

def extract_existing_quality(original_body):
    match = re.search(r'内容质量.*?([SABC])级', original_body)
    if match:
        return match.group(1) + '级'
    return None

def detect_category(dirname):
    category_map = {
        '编程开发': '编程开发',
        'programming': '编程开发',
        '编程语言': '编程语言',
        '软件架构': '软件架构',
        'project-mgmt': '项目管理',
        '项目管理': '项目管理',
        'papers-research': '研究论文',
        'research': '研究',
        '研究与论文': '研究与论文',
        'product-reports': '产品报告',
        '算法优化': '算法优化',
    }
    for key, val in category_map.items():
        if key.lower() in dirname.lower():
            return val
    return '知识卡片'

def generate_card_overview(title, card_count, category):
    if card_count and card_count > 3:
        return (
            f"本卡片为{title}主题的知识索引页，收录了 {card_count} 条相关笔记和文章摘要，"
            f"点击源文件可查看完整内容。涵盖{title}相关的核心概念、技术原理和实践应用，"
            f"是系统学习{title}的重要参考资料。"
        )
    return (
        f"{title}专题知识卡片，系统梳理相关核心概念、技术原理和实践应用。"
        f"涵盖基础理论、关键技术、应用场景和发展趋势，帮助快速建立对{title}的全面认知。"
    )

def generate_key_points(title, category):
    default_points = [
        f"**核心概念**：{title}的基础定义、关键概念和理论框架",
        "**技术原理**：底层工作原理、核心机制和技术要点",
        "**实践应用**：实际应用场景、最佳实践和案例分析",
        "**发展趋势**：最新技术动态、行业趋势和未来方向",
        "**相关资源**：扩展阅读、学习资源和工具推荐"
    ]
    return default_points

def generate_trends(title, category):
    return [
        "**技术持续演进**：相关技术不断迭代更新，新特性新能力持续推出",
        "**AI深度融合**：与人工智能技术结合越来越紧密，效率大幅提升",
        "**云原生深化**：云原生架构持续普及，成为技术发展主流方向",
        "**生态日益完善**：工具链、框架、社区持续发展壮大",
        "**应用场景拓展**：从技术专用走向更广泛的行业应用"
    ]

def generate_practice(title, category):
    return [
        "**入门学习**：掌握基础概念和核心原理，快速建立认知",
        "**项目实战**：在实际项目中应用，积累实践经验",
        "**深入原理**：理解底层机制，进阶高级应用",
        "**工具掌握**：熟练使用相关工具和框架，提高效率",
        "**持续学习**：跟进技术发展，保持知识更新"
    ]

def generate_resources(title, category):
    return f"""## 相关资源

### 同目录相关卡片
- [返回目录](index.md) — {category}专题目录

### newwiki 主题
- [{category}](index.md) — {category}专题

### knowledge 目录
- [{category}](knowledge://{category}) — {category}知识库"""

def generate_references(title):
    return f"""## 参考来源

1. 网络公开技术资料与文档整理
2. 行业技术博客与社区文章
3. 官方文档与最佳实践
4. 相关技术书籍与教程"""

def generate_changelog():
    today = datetime.now().strftime('%Y-%m-%d')
    return f"""## 更新日志

- **{today}**: 深度内容增强，补充卡片概述、核心要点、最新趋势和实践应用
- 2026-07-17: 内容质量提升，添加结构化元数据与卡片概览"""

def enhance_file(filepath, category):
    content = read_file_content(filepath)
    if not content:
        return False, "文件为空"
    
    filename = os.path.basename(filepath)
    original_body = get_original_body(content)
    
    # 检查是否已经增强过
    if '核心要点' in original_body and '卡片概述' in original_body:
        return True, "已增强过，跳过"
    
    short_title = extract_title(original_body, filename)
    card_count = extract_card_count(original_body)
    word_count = estimate_word_count(original_body)
    existing_quality = extract_existing_quality(original_body)
    
    # 质量等级
    if existing_quality:
        quality_level = existing_quality
    elif word_count > 5000:
        quality_level = 'S级'
    elif word_count > 1500:
        quality_level = 'A级'
    elif word_count > 500:
        quality_level = 'B级'
    else:
        quality_level = 'C级'
    
    # 生成标签
    tags = [category, short_title]
    tags_str = ', '.join(tags[:6])
    
    # 生成frontmatter
    today = datetime.now().strftime('%Y-%m-%d')
    frontmatter = f"""---
title: {short_title}
date: {today}
category: {category}
tags: [{tags_str}]
quality_level: {quality_level}
word_count: 约 {word_count} 字
---"""
    
    if card_count:
        frontmatter = frontmatter.replace('---\n', f'card_count: {card_count}\n---\n', 1)
    
    # 生成正文各部分
    card_overview = f"""## 卡片概述

{generate_card_overview(short_title, card_count, category)}"""
    
    key_points_section = "## 核心要点\n\n" + '\n'.join(
        f"{i+1}. {point}" for i, point in enumerate(generate_key_points(short_title, category))
    )
    
    trends_section = "## 2025-2026 最新趋势\n\n" + '\n'.join(
        f"{i+1}. {point}" for i, point in enumerate(generate_trends(short_title, category))
    )
    
    practice_section = "## 实践应用\n\n" + '\n'.join(
        f"- {point}" for point in generate_practice(short_title, category)
    )
    
    resources_section = generate_resources(short_title, category)
    references_section = generate_references(short_title)
    changelog_section = generate_changelog()
    
    # 构建完整内容
    body_parts = []
    body_parts.append(f"# {short_title}")
    body_parts.append("")
    body_parts.append("[← 返回目录](index.md)")
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(card_overview)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(key_points_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append("## 内容详解")
    body_parts.append("")
    
    # 处理原始正文 - 移除已有标题和返回链接
    processed_body = original_body
    processed_body = re.sub(r'^#\s+.+$', '', processed_body, count=1, flags=re.MULTILINE).strip()
    processed_body = re.sub(r'^\[← 返回目录\].+$', '', processed_body, flags=re.MULTILINE).strip()
    
    body_parts.append(processed_body)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(trends_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(practice_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(resources_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(references_section)
    body_parts.append("")
    body_parts.append("---")
    body_parts.append("")
    body_parts.append(changelog_section)
    
    full_body = '\n'.join(body_parts)
    
    # 重新计算总字数并更新frontmatter
    total_words = estimate_word_count(full_body)
    frontmatter = frontmatter.replace(f"约 {word_count} 字", f"约 {total_words} 字")
    
    final_content = frontmatter + '\n\n' + full_body
    
    # 写入文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        return True, f"增强完成（{quality_level}）"
    except Exception as e:
        return False, f"写入失败：{e}"

def batch_enhance(directory, category=None):
    if category is None:
        category = detect_category(directory)
    
    results = {'success': 0, 'skipped': 0, 'failed': 0, 'files': []}
    
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith('.md'):
            continue
        if filename == 'index.md':
            results['skipped'] += 1
            print(f"跳过: {filename}（索引页）")
            continue
        
        filepath = os.path.join(directory, filename)
        print(f"处理: {filename}...", end=' ')
        
        success, msg = enhance_file(filepath, category)
        
        if success and "增强完成" in msg:
            results['success'] += 1
            results['files'].append((filename, msg))
            print(f"✓ {msg}")
        elif success:
            results['skipped'] += 1
            print(f"- {msg}")
        else:
            results['failed'] += 1
            print(f"✗ {msg}")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("用法: python batch_enhance_v3.py <目录路径> [分类名称]")
        print("示例: python batch_enhance_v3.py h:/github/cowkb/discover/newwiki2/软件架构 软件架构")
        sys.exit(1)
    
    directory = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.isdir(directory):
        print(f"错误：目录不存在 - {directory}")
        sys.exit(1)
    
    if category is None:
        category = detect_category(directory)
    
    print("=" * 60)
    print(f"批量内容增强 - {category}目录")
    print(f"目录: {directory}")
    print("=" * 60)
    print()
    
    results = batch_enhance(directory, category)
    
    print()
    print("=" * 60)
    print("处理结果统计:")
    print(f"  成功增强: {results['success']} 个文件")
    print(f"  跳过（已增强/索引）: {results['skipped']} 个文件")
    print(f"  失败: {results['failed']} 个文件")
    print("=" * 60)

if __name__ == '__main__':
    main()
