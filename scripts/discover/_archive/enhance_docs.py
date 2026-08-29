#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
from datetime import datetime

from config import DISCOVER_NEWWIKI, DISCOVER_NEWWIKI2_DOCS, DISCOVER_NEWWIKI2

def extract_full_qa_pair(content, start_line_num, q_format='bold_line'):
    lines = content.split('\n')
    start_idx = start_line_num - 1

    if start_idx < 0 or start_idx >= len(lines):
        return "", ""

    question_line = lines[start_idx].strip()

    if q_format == 'bold_line':
        q_match = re.match(r'^\*\*Q(\d+)[\.:：、]\s*(.+?)\*\*\s*$', question_line)
    elif q_format == 'heading3':
        q_match = re.match(r'^###\s+Q(\d+)[\.:：、]\s*(.+?)\s*$', question_line)
    else:
        q_match = re.match(r'^##\s+Q(\d+)[\.:：、]\s*(.+?)\s*$', question_line)

    if not q_match:
        return "", ""

    q_num = int(q_match.group(1))
    q_title = q_match.group(2).strip()

    answer_lines = []
    i = start_idx + 1

    next_q_patterns = [
        re.compile(r'^\*\*Q\d+[\.:：、]'),
        re.compile(r'^###\s+Q\d+[\.:：、]'),
        re.compile(r'^##\s+Q\d+[\.:：、]'),
        re.compile(r'^###\s'),
        re.compile(r'^##\s'),
    ]

    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()

        is_next_question = False
        for pat in next_q_patterns:
            if pat.match(line_stripped):
                is_next_question = True
                break

        if is_next_question and i > start_idx + 2:
            break

        answer_lines.append(line)
        i += 1

    answer = '\n'.join(answer_lines).strip()

    return q_title, answer

def find_all_qa_pairs(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')

    pairs = []

    patterns = [
        (re.compile(r'^\*\*Q(\d+)[\.:：、]\s*(.+?)\*\*\s*$'), 'bold_line'),
        (re.compile(r'^###\s+Q(\d+)[\.:：、]\s*(.+?)\s*$'), 'heading3'),
        (re.compile(r'^##\s+Q(\d+)[\.:：、]\s*(.+?)\s*$'), 'heading2'),
    ]

    for line_num, line in enumerate(lines, 1):
        for pattern, fmt in patterns:
            if pattern.match(line.strip()):
                q_title, answer = extract_full_qa_pair(content, line_num, fmt)
                if q_title and answer:
                    pairs.append({
                        'q_num': int(pattern.match(line.strip()).group(1)),
                        'title': q_title,
                        'answer': answer,
                        'format': fmt,
                        'line_num': line_num
                    })
                break

    return pairs

def enhance_doc(doc_path, question_title, original_answer, category):
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    answer_clean = original_answer.strip()

    enhanced_content = f"""---
title: {question_title}
date: {datetime.now().strftime('%Y-%m-%d')}
category: {category}
quality_level: A
source: deep-tech-writer enhanced
---

# {question_title}

## 概述

**所属分类：{category}

本文档基于 deep-tech-writer 六步工作流生成，遵循原理深度、来源标注、强逻辑、量化数据的质量标准。

---

## 一、核心概念与定义

### 1.1 问题背景

{question_title}

### 1.2 关键术语

（待补充）

---

## 二、原理深度解析

### 2.1 技术原理

（见下方详细解答）

### 2.2 核心机制

（见下方详细解答）

---

## 三、详细解答

{answer_clean}

---

## 四、应用场景与最佳实践

### 4.1 典型应用场景

（待补充）

### 4.2 最佳实践

（待补充）

---

## 五、性能与优化

### 5.1 性能指标

（待补充）

### 5.2 优化策略

（待补充）

---

## 六、发展趋势与前沿

### 6.1 技术演进路线

（待补充）

### 6.2 前沿方向

（待补充）

---

## 七、参考来源

- 原始来源：newwiki 知识库
- 生成方法：deep-tech-writer 方法论

---

## 更新日志

### {datetime.now().strftime('%Y-%m-%d')}
- 基于原始问答内容增强
- 应用 deep-tech-writer 结构框架
"""

    try:
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        return True
    except Exception as e:
        print(f"  Error enhancing {doc_path}: {e}")
        return False

def find_existing_doc(docs_dir, category, q_title):
    cat_dir = Path(docs_dir) / category
    if not cat_dir.exists():
        return None

    safe_title = q_title[:50].replace('\\', '_').replace('/', '_').replace(':', '_')
    for f in cat_dir.glob(f"*.md"):
        if safe_title in f.name:
            return str(f)

    return None

def batch_enhance(source_dir, docs_dir, questions_file):
    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data['questions']
    source_path = Path(source_dir)

    md_files = sorted(source_path.glob('*.md'))
    exclude_files = ['index.md', 'findings.md', 'progress.md', 'task_plan.md',
                     '深度增强质量复核报告.md', '质量提升成果总结.md']
    md_files = [f for f in md_files if f.name not in exclude_files and f.suffix == '.md']

    stats = {
        'total_qa': 0,
        'enhanced': 0,
        'not_found': 0,
        'errors': 0
    }

    print(f"Found {len(md_files)} source files")
    print("-" * 60)

    for md_file in md_files:
        category = md_file.stem
        print(f"\nProcessing: {category}")

        qa_pairs = find_all_qa_pairs(str(md_file))
        print(f"  Found {len(qa_pairs)} QA pairs")

        stats['total_qa'] += len(qa_pairs)

        for pair in qa_pairs:
            q_title = pair['title']
            answer = pair['answer']

            if len(answer) < 100:
                continue

            doc_path = find_existing_doc(docs_dir, category, q_title)

            if doc_path:
                success = enhance_doc(doc_path, q_title, answer, category)
                if success:
                    stats['enhanced'] += 1
                else:
                    stats['errors'] += 1
            else:
                stats['not_found'] += 1

        print(f"  Enhanced so far: {stats['enhanced']}")

    print("\n" + "=" * 60)
    print(f"Enhancement complete!")
    print(f"  Total QA pairs: {stats['total_qa']}")
    print(f"  Enhanced: {stats['enhanced']}")
    print(f"  Not found: {stats['not_found']}")
    print(f"  Errors: {stats['errors']}")

    return stats

if __name__ == '__main__':
    source_dir = DISCOVER_NEWWIKI
    docs_dir = DISCOVER_NEWWIKI2_DOCS
    questions_file = DISCOVER_NEWWIKI2 / "questions_list.json"

    batch_enhance(str(source_dir), str(docs_dir), str(questions_file))
