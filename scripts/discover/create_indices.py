#!/usr/bin/env python3
import os
import re
from pathlib import Path
from datetime import datetime

from config import DISCOVER_NEWWIKI2_DOCS

def create_category_index(docs_dir):
    docs_path = Path(docs_dir)

    for cat_dir in sorted(docs_path.iterdir()):
        if not cat_dir.is_dir():
            continue

        category = cat_dir.name
        md_files = sorted(cat_dir.glob('*.md'))

        docs = []
        for md_file in md_files:
            if md_file.name == 'index.md':
                continue
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(800)

                title_match = re.search(r'title:\s*(.+)', content)
                quality_match = re.search(r'quality_level:\s*(\S+)', content)
                qnum_match = re.search(r'question_num:\s*(\d+)', content)

                title = title_match.group(1).strip() if title_match else md_file.stem
                quality = quality_match.group(1) if quality_match else 'B'
                q_num = qnum_match.group(1) if qnum_match else '?'

                docs.append({
                    'filename': md_file.name,
                    'title': title,
                    'quality': quality,
                    'q_num': q_num
                })
            except Exception as e:
                docs.append({
                    'filename': md_file.name,
                    'title': md_file.stem,
                    'quality': '?',
                    'q_num': '?'
                })

        a_count = sum(1 for d in docs if d['quality'] == 'A')
        b_count = sum(1 for d in docs if d['quality'] == 'B')

        index_content = f"""# {category} 目录索引

> **文档数量**: {len(docs)} 篇
> **质量分布**: A级 {a_count} 篇 | B级 {b_count} 篇
> **更新时间**: {datetime.now().strftime('%Y-%m-%d')}

---

## 文档清单

| # | 标题 | 质量等级 |
|--:|:-----|:--------:|
"""

        for i, doc in enumerate(docs, 1):
            index_content += f"| {i} | [{doc['title'][:80]}]({doc['filename']}) | {doc['quality']} |\n"

        index_content += f"""
---

## 说明

本目录下所有技术专题文档均基于 [deep-tech-writer](../../skills/deep-tech-writer/SKILL.md) 方法论生成。

**质量等级说明**:
- **A级**: 已基于原始问答内容进行深度增强，包含完整的技术解答
- **B级**: 文档框架已生成，内容待进一步增强

---

*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        index_path = cat_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)

        print(f"  {category}: {len(docs)} docs (A:{a_count}, B:{b_count})")

def create_main_index(docs_dir):
    docs_path = Path(docs_dir)
    categories = []

    for cat_dir in sorted(docs_path.iterdir()):
        if cat_dir.is_dir():
            md_files = list(cat_dir.glob('*.md'))
            categories.append({
                'name': cat_dir.name,
                'count': len(md_files) - 1  # exclude index.md
            })

    total = sum(c['count'] for c in categories)

    content = f"""# NewWiki2 技术专题知识库

> **定位**: 基于 deep-tech-writer 方法论生成的深度技术专题文档库
> **生成时间**: {datetime.now().strftime('%Y-%m-%d')}
> **文档总数**: {total} 个技术专题
> **来源**: newwiki 知识库问答对

---

## 目录

"""

    for cat in categories:
        content += f"- [{cat['name']}]({cat['name']}/index.md) - {cat['count']} 篇文档\n"

    content += f"""
---

## 文档质量标准

本知识库遵循 [deep-tech-writer](../skills/deep-tech-writer/SKILL.md) 六步工作流：

1. **搜集权威源** - 优先论文/标准/官方白皮书
2. **原理深潜** - 深入协议/芯片/物理层次
3. **强逻辑结构** - 论点→论据→数据→结论
4. **量化数据+来源标注** - 数值+单位+基线+条件
5. **外审迭代** - 自检+外部视角+反馈处理
6. **格式打磨** - TOC、changelog、交叉链接

### 质量等级

| 等级 | 说明 | 数量 |
|:----:|:-----|-----:|
| **A级** | 已基于原始问答内容深度增强 | - |
| **B级** | 文档框架已生成，内容待增强 | - |

---

## 文档结构

每篇技术专题文档包含以下章节：

1. **概述** - 问题背景与核心要点
2. **核心概念与定义** - 关键术语解释
3. **原理深度解析** - 技术原理与核心机制
4. **技术实现细节** - 实现架构与关键技术点
5. **应用场景与最佳实践** - 典型场景与选型建议
6. **性能与优化** - 性能指标与优化策略
7. **发展趋势与前沿** - 技术演进与未来展望
8. **原始问答参考** - 原始问题与回答
9. **参考来源** - 资料来源与引用

---

## 使用指南

### 如何查找内容？

1. 按分类浏览：点击上方分类链接进入对应目录
2. 按主题搜索：使用文件搜索功能查找关键词
3. 按质量筛选：优先阅读 A 级文档

### 如何贡献内容？

所有 B 级文档均可进一步增强。增强时请遵循 deep-tech-writer 质量标准。

---

*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    index_path = docs_path / 'README.md'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nMain index created: {index_path}")

if __name__ == '__main__':
    docs_dir = DISCOVER_NEWWIKI2_DOCS

    print("Creating category indices...")
    create_category_index(str(docs_dir))

    print("\nCreating main index...")
    create_main_index(str(docs_dir))

    print("\nDone!")
