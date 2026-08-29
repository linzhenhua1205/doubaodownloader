import os
import re
import sys
from pathlib import Path

BASE_DIR = r"h:\github\cowkb\discover\newwiki2"

INDEX_DIRS = [
    "AI-模型架构",
    "AI-训练微调",
    "AI-Agent",
    "ai-models",
]

TEMPLATE_SECTIONS = [
    "## 卡片概述",
    "## 核心要点",
    "## 内容详解",
    "### 一、基础概念",
    "### 二、核心原理", 
    "### 三、实践方法",
    "## 2025-2026 年最新进展",
    "### 1. 技术发展趋势",
    "### 2. 应用场景扩展",
    "## 应用场景",
    "### 1. 技术开发",
    "### 2. 学习与成长",
    "## 相关资源",
    "### 相关卡片",
    "### 推荐阅读",
    "## 参考来源",
    "## 卡片概览",
]

def parse_frontmatter(content):
    if not content.startswith('---'):
        return {}, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    fm_text = parts[1].strip()
    body = parts[2].lstrip()
    fm = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                val = val[1:-1].split(',')
                val = [v.strip() for v in val]
            fm[key] = val
    return fm, body

def dump_frontmatter(fm):
    lines = ['---']
    for key, val in fm.items():
        if isinstance(val, list):
            val_str = ', '.join(val)
            lines.append(f'{key}: [{val_str}]')
        else:
            lines.append(f'{key}: {val}')
    lines.append('---')
    return '\n'.join(lines) + '\n'

def is_index_page(body):
    index_markers = ['本卡片为知识索引页', '收录了相关主题的多条笔记摘要']
    return any(marker in body for marker in index_markers)

def estimate_word_count(text):
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    en_words = len(re.findall(r'[a-zA-Z]+', text))
    return cn_chars + en_words

def clean_template_content(body):
    lines = body.split('\n')
    result = []
    skip = False
    skip_until_next_section = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        is_template_section = False
        for section in TEMPLATE_SECTIONS:
            if line.strip() == section.strip():
                is_template_section = True
                break
        
        if is_template_section:
            skip = True
            i += 1
            continue
        
        if skip:
            if line.startswith('## ') or line.startswith('---'):
                skip = False
            else:
                i += 1
                continue
        
        if not skip:
            result.append(line)
        i += 1
    
    cleaned = '\n'.join(result)
    
    cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)
    
    return cleaned.strip()

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm, body = parse_frontmatter(content)
    
    if not is_index_page(body):
        return False, "不是知识索引页"
    
    original_word_count = estimate_word_count(body)
    
    cleaned_body = clean_template_content(body)
    new_word_count = estimate_word_count(cleaned_body)
    
    if new_word_count >= original_word_count * 0.7:
        return False, f"清理后字数变化不大（{original_word_count} -> {new_word_count}），可能不是模板化问题"
    
    title = fm.get('title', '未知')
    category = fm.get('category', '')
    
    index_intro = f"""---

## 卡片概述

> **本卡片为知识索引页**，收录了与「{title}」相关的多条笔记摘要。
>
> 索引页的定位是**知识导航与快速概览**，帮助读者快速了解相关主题有哪些笔记、大致讲了什么。点击每条笔记的源文件链接可查看完整内容。

- **主题分类**: {category}
- **收录笔记**: {count_notes(cleaned_body)} 条
- **内容形式**: 笔记摘要合集
- **适用场景**: 快速扫览、主题导航、灵感启发

---

"""
    
    final_body = index_intro + cleaned_body
    
    if '## 更新日志' in final_body:
        pass
    else:
        final_body += f"""

---

## 更新日志

- **2026-07-22**: B 级基础增强 — 清理模板化空内容，优化索引页结构与导航体验。
"""
    
    if final_body.strip().endswith('*'):
        pass
    else:
        final_body += f"""

---

*卡片质量等级：B级（知识索引页） | 更新日期：2026-07-22*
"""
    
    fm['quality_level'] = 'B级（知识索引页）'
    fm['word_count'] = f'约 {new_word_count} 字'
    fm['status'] = 'B级基础增强完成（知识索引页）'
    
    new_content = dump_frontmatter(fm) + '\n' + final_body
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"清理完成：{original_word_count}字 -> {new_word_count}字"

def count_notes(body):
    count = 0
    lines = body.split('\n')
    for line in lines:
        if re.match(r'^## \d+\.', line.strip()):
            count += 1
    return max(count, 1)

def main():
    total_processed = 0
    total_skipped = 0
    results = []
    
    for dirname in INDEX_DIRS:
        dirpath = os.path.join(BASE_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue
        
        for filename in os.listdir(dirpath):
            if not filename.endswith('.md'):
                continue
            if filename == 'index.md':
                continue
            
            filepath = os.path.join(dirpath, filename)
            success, msg = process_file(filepath)
            
            rel_path = os.path.join(dirname, filename)
            if success:
                total_processed += 1
                results.append(f"✅ {rel_path}: {msg}")
            else:
                total_skipped += 1
                results.append(f"⏭️  {rel_path}: {msg}")
    
    print("\n" + "="*70)
    print("批量清理知识索引页模板化内容")
    print("="*70)
    print(f"处理成功: {total_processed} 个")
    print(f"跳过: {total_skipped} 个")
    print("="*70)
    print("\n详细结果：")
    for r in results:
        print(r)

if __name__ == '__main__':
    main()
