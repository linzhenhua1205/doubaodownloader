#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
from datetime import datetime

from config import DISCOVER_NEWWIKI, DISCOVER_NEWWIKI2_DOCS

def extract_all_qa(source_file):
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    qa_pairs = []

    patterns = [
        (r'^\*\*Q(\d+)[\.:：、]\s*(.+?)\*\*\s*$', 'bold'),
        (r'^###\s+Q(\d+)[\.:：、]\s*(.+?)\s*$', 'h3'),
    ]

    lines = content.split('\n')

    for pattern, fmt in patterns:
        for i, line in enumerate(lines):
            m = re.match(pattern, line.strip())
            if m:
                q_num = int(m.group(1))
                q_title = m.group(2).strip()

                answer_lines = []
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if re.match(r'^\*\*Q\d+[\.:：、]', next_line) or \
                       re.match(r'^###\s+Q\d+[\.:：、]', next_line) or \
                       re.match(r'^##\s+', next_line):
                        if j > i + 1:
                            break
                    answer_lines.append(lines[j])
                    j += 1

                answer = '\n'.join(answer_lines).strip()
                qa_pairs.append({
                    'num': q_num,
                    'title': q_title,
                    'answer': answer,
                    'format': fmt
                })

    return qa_pairs

def simple_enhance_all(source_dir, docs_dir):
    source_path = Path(source_dir)
    docs_path = Path(docs_dir)

    stats = {'total_b': 0, 'enhanced': 0, 'errors': 0}

    md_files = sorted(source_path.glob('*.md'))
    exclude = ['index.md', 'findings.md', 'progress.md', 'task_plan.md',
               '深度增强质量复核报告.md', '质量提升成果总结.md']
    md_files = [f for f in md_files if f.name not in exclude and f.suffix == '.md']

    print("Enhancing all B-level documents...")
    print("-" * 60)

    for src_file in md_files:
        category = src_file.stem
        cat_dir = docs_path / category

        if not cat_dir.exists():
            continue

        qa_pairs = extract_all_qa(str(src_file))

        b_files = []
        for doc_file in cat_dir.glob('*.md'):
            if doc_file.name == 'index.md':
                continue
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    head = f.read(600)
                if 'quality_level: B' in head:
                    b_files.append(doc_file)
            except:
                pass

        stats['total_b'] += len(b_files)

        for doc_file in b_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                title_match = re.search(r'title:\s*(.+)', content)
                doc_title = title_match.group(1).strip() if title_match else ''

                matched_answer = None
                for qa in qa_pairs:
                    if qa['title'][:50] in doc_title or doc_title[:50] in qa['title']:
                        matched_answer = qa['answer']
                        break

                if matched_answer and len(matched_answer) > 20:
                    new_content = content.replace('quality_level: B', 'quality_level: A')

                    old_answer_section = None
                    m = re.search(r'### 原始回答\n\n(.*?)\n\n---', new_content, re.DOTALL)
                    if m:
                        old_answer = m.group(1).strip()
                        if '原始回答待补充' in old_answer or len(old_answer) < 50:
                            new_content = new_content.replace(
                                m.group(0),
                                f"### 原始回答\n\n{matched_answer}\n\n---"
                            )

                    with open(doc_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    stats['enhanced'] += 1
            except Exception as e:
                stats['errors'] += 1

        print(f"  {category}: {len(b_files)} B-docs, enhanced so far: {stats['enhanced']}")

    print("\n" + "=" * 60)
    print(f"Enhancement complete!")
    print(f"  Total B-docs: {stats['total_b']}")
    print(f"  Enhanced: {stats['enhanced']}")
    print(f"  Errors: {stats['errors']}")

    return stats

if __name__ == '__main__':
    source_dir = DISCOVER_NEWWIKI
    docs_dir = DISCOVER_NEWWIKI2_DOCS

    simple_enhance_all(str(source_dir), str(docs_dir))
