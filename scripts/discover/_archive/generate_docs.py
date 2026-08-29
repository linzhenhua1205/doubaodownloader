#!/usr/bin/env python3
import os
import re
import jsonimport hashlib
from pathlib import Path
from datetime import datetime

from config import DISCOVER_NEWWIKI2, DISCOVER_NEWWIKI2_DOCS

def sanitize_filename(title):
    invalid_chars = '\\/:*?"<>|\t\n\r'
    for ch in invalid_chars:
        title = title.replace(ch, '_')
    title = title.replace('\t', '_').replace('\n', '_').replace('\r', '_')
    title = title.strip()
    title = title[:80] if len(title) > 80 else title
    if not title:
        title = 'untitled'
    return title

def generate_doc_id(category, q_num, title):
    raw = f"{category}_{q_num}_{title}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()[:12]

def read_original_answer(source_file, q_num, q_format):
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return ""

    lines = content.split('\n')
    answer_lines = []
    found = False
    next_q_pattern = re.compile(r'^(\*\*Q\d+[\.:：、]|^###\s+Q\d+[\.:：、]|^##\s+Q\d+[\.:：、])')

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        if not found:
            if q_format == 'bold_line':
                if re.match(rf'^\*\*Q{q_num}[\.:：、]', line_stripped):
                    found = True
                    continue
            elif q_format in ('heading3', 'heading2'):
                prefix = '###' if q_format == 'heading3' else '##'
                if re.match(rf'^{prefix}\s+Q{q_num}[\.:：、]', line_stripped):
                    found = True
                    continue
        else:
            if next_q_pattern.match(line_stripped) and not line_stripped.startswith('**A'):
                break
            answer_lines.append(line)

    return '\n'.join(answer_lines).strip()

def generate_tech_doc(question, output_dir):
    q_num = question['q_num']
    title = question['title']
    category = question['category']
    source_file = question['source_file']
    q_format = question['format']

    doc_id = generate_doc_id(category, q_num, title)
    safe_title = sanitize_filename(title)
    filename = f"{category}_Q{q_num}_{safe_title}.md"

    category_dir = Path(output_dir) / category
    category_dir.mkdir(parents=True, exist_ok=True)

    output_path = category_dir / filename

    if output_path.exists():
        return str(output_path), 'skipped'

    original_answer = read_original_answer(source_file, q_num, q_format)

    doc_content = f"""---
title: {title}
date: {datetime.now().strftime('%Y-%m-%d')}
category: {category}
question_num: {q_num}
doc_id: {doc_id}
source_file: {source_file}
quality_level: B
---

# {title}

## 概述

**问题编号**：Q{q_num}
**所属分类**：{category}
**来源文件**：{Path(source_file).name}

---

## 一、核心概念与定义

### 1.1 问题背景

本问题聚焦于「{title[:50]}」这一技术主题。

### 1.2 关键术语

| 术语 | 定义 |
|:-----|:-----|
| 待补充 | 待补充 |

---

## 二、原理深度解析

### 2.1 技术原理

### 2.2 核心机制

### 2.3 设计权衡

| 维度 | 方案A | 方案B | 权衡点 |
|:-----|:------|:------|:-------|
| 性能 | - | - | - |
| 成本 | - | - | - |
| 复杂度 | - | - | - |

---

## 三、技术实现细节

### 3.1 实现架构

### 3.2 关键技术点

### 3.3 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|:-----|:-----|:---------|
| 待补充 | 待补充 | 待补充 |

---

## 四、应用场景与最佳实践

### 4.1 典型应用场景

### 4.2 最佳实践

### 4.3 选型决策框架

| 维度 | 适用场景 | 不适用场景 |
|:-----|:---------|:-----------|
| 待补充 | 待补充 | 待补充 |

---

## 五、性能与优化

### 5.1 性能指标

### 5.2 优化策略

### 5.3 瓶颈分析

---

## 六、发展趋势与前沿

### 6.1 技术演进路线

### 6.2 前沿方向

### 6.3 未来展望

---

## 七、原始问答参考

### 原始问题

**Q{q_num}. {title}**

### 原始回答

{original_answer if original_answer else '（原始回答待补充）'}

---

## 参考来源

- [待补充] 原始来源：{Path(source_file).name}

---

## 更新日志

### {datetime.now().strftime('%Y-%m-%d')}
- 初始版本创建
- 基于 deep-tech-writer 六步工作流生成框架
"""

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        return str(output_path), 'created'
    except Exception as e:
        return str(output_path), f'error: {str(e)}'

def batch_generate(questions_file, output_dir, start_index=0, end_index=None, batch_size=50):
    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    questions = data['questions']
    total = len(questions)

    if end_index is None:
        end_index = total

    questions = questions[start_index:end_index]
    batch_total = len(questions)

    print(f"Total questions: {total}")
    print(f"Processing range: {start_index} - {end_index} ({batch_total} questions)")
    print(f"Output directory: {output_dir}")
    print("-" * 60)

    stats = {
        'created': 0,
        'skipped': 0,
        'error': 0,
        'errors': []
    }

    progress_file = Path(output_dir) / 'generation_progress.json'

    for i, q in enumerate(questions):
        global_idx = start_index + i
        result_path, status = generate_tech_doc(q, output_dir)

        if status == 'created':
            stats['created'] += 1
        elif status == 'skipped':
            stats['skipped'] += 1
        else:
            stats['error'] += 1
            stats['errors'].append({
                'index': global_idx,
                'question': q['title'],
                'error': status
            })

        if (i + 1) % batch_size == 0 or i == batch_total - 1:
            progress = {
                'last_updated': datetime.now().isoformat(),
                'start_index': start_index,
                'current_index': global_idx,
                'end_index': end_index,
                'total': total,
                'processed': i + 1,
                'remaining': batch_total - i - 1,
                'stats': stats
            }
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)

            print(f"[{global_idx + 1}/{total}] Created: {stats['created']}, Skipped: {stats['skipped']}, Errors: {stats['error']}")

    print("-" * 60)
    print(f"Generation complete!")
    print(f"  Created: {stats['created']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['error']}")

    if stats['errors']:
        error_log = Path(output_dir) / 'error_log.json'
        with open(error_log, 'w', encoding='utf-8') as f:
            json.dump(stats['errors'], f, ensure_ascii=False, indent=2)
        print(f"  Error log: {error_log}")

    return stats

if __name__ == '__main__':
    questions_file = DISCOVER_NEWWIKI2 / "questions_list.json"
    output_dir = DISCOVER_NEWWIKI2_DOCS

    batch_generate(str(questions_file), str(output_dir))
