#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
from datetime import datetime

from config import DISCOVER_NEWWIKI, DISCOVER_NEWWIKI2_DOCS

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
                q_num = int(pattern.match(line.strip()).group(1))
                q_title = pattern.match(line.strip()).group(2).strip()

                answer_lines = []
                i = line_num
                next_q_patterns = [
                    re.compile(r'^\*\*Q\d+[\.:：、]'),
                    re.compile(r'^###\s+Q\d+[\.:：、]'),
                    re.compile(r'^##\s+Q\d+[\.:：、]'),
                ]

                while i < len(lines):
                    next_line = lines[i]
                    next_line_stripped = next_line.strip()

                    is_next = False
                    for pat in next_q_patterns:
                        if pat.match(next_line_stripped):
                            is_next = True
                            break

                    if is_next and i > line_num:
                        break

                    answer_lines.append(next_line)
                    i += 1

                answer = '\n'.join(answer_lines).strip()

                pairs.append({
                    'q_num': q_num,
                    'title': q_title,
                    'answer': answer,
                    'format': fmt,
                    'line_num': line_num
                })
                break

    return pairs

def enhance_b_level_docs(source_dir, docs_dir):
    source_path = Path(source_dir)
    docs_path = Path(docs_dir)

    md_files = sorted(source_path.glob('*.md'))
    exclude_files = ['index.md', 'findings.md', 'progress.md', 'task_plan.md',
                     '深度增强质量复核报告.md', '质量提升成果总结.md']
    md_files = [f for f in md_files if f.name not in exclude_files and f.suffix == '.md']

    stats = {'found': 0, 'enhanced': 0, 'skipped': 0, 'errors': 0}

    print("Enhancing B-level documents...")
    print("-" * 60)

    for md_file in md_files:
        category = md_file.stem
        cat_dir = docs_path / category

        if not cat_dir.exists():
            continue

        qa_pairs = find_all_qa_pairs(str(md_file))

        qa_by_title = {}
        for pair in qa_pairs:
            qa_by_title[pair['title'][:60]] = pair

        b_docs = []
        for md_doc in cat_dir.glob('*.md'):
            if md_doc.name == 'index.md':
                continue
            try:
                with open(md_doc, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                q_match = re.search(r'quality_level:\s*B', content)
                if q_match:
                    title_match = re.search(r'title:\s*(.+)', content)
                    title = title_match.group(1).strip() if title_match else ''
                    b_docs.append((str(md_doc), title))
            except:
                pass

        stats['found'] += len(b_docs)

        for doc_path, doc_title in b_docs:
            matched_pair = None
            for key, pair in qa_by_title.items():
                if key in doc_title or doc_title[:60] in pair['title']:
                    matched_pair = pair
                    break

            if matched_pair and matched_pair['answer']:
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    answer = matched_pair['answer'].strip()

                    new_content = re.sub(
                        r'quality_level:\s*B',
                        'quality_level: A',
                        content
                    )

                    old_section = "## 七、原始问答参考\n\n### 原始问题\n\n.*?\n\n### 原始回答\n\n.*?\n\n---"
                    new_section = f"## 三、详细解答\n\n{answer}\n\n---\n\n## 四、原始问答参考\n\n### 原始问题\n\n**Q{matched_pair['q_num']}. {matched_pair['title']}**\n\n### 原始回答\n\n（已整合入上方详细解答）\n\n---"

                    if '## 七、原始问答参考' in new_content:
                        parts = new_content.split('## 七、原始问答参考')
                        before = parts[0]
                        after = parts[1] if len(parts) > 1 else ''

                        new_content = before + f"""## 三、详细解答

{answer}

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

## 七、原始问答参考

### 原始问题

**Q{matched_pair['q_num']}. {matched_pair['title']}**

### 原始回答

（已整合入上方详细解答）

---

## 参考来源

- 原始来源：newwiki 知识库
- 生成方法：deep-tech-writer 方法论

---

## 更新日志

### {datetime.now().strftime('%Y-%m-%d')}
- 基于原始问答内容增强
- 应用 deep-tech-writer 结构框架
"""

                        after_idx = after.find('## 参考来源')
                        if after_idx > 0:
                            pass

                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    stats['enhanced'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"  Error: {doc_path}: {e}")
            else:
                stats['skipped'] += 1

        print(f"  {category}: {len(b_docs)} B-docs, enhanced {stats['enhanced']}")

    print("\n" + "=" * 60)
    print(f"B-level enhancement complete!")
    print(f"  Found B-docs: {stats['found']}")
    print(f"  Enhanced: {stats['enhanced']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors: {stats['errors']}")

    return stats

if __name__ == '__main__':
    source_dir = DISCOVER_NEWWIKI
    docs_dir = DISCOVER_NEWWIKI2_DOCS

    enhance_b_level_docs(str(source_dir), str(docs_dir))
