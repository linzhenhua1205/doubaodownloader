import json
from pathlib import Path
import os

from config import DISCOVER_NEWWIKI2_DOCS

def count_docs_by_category(docs_dir):
    docs_path = Path(docs_dir)
    stats = {}
    total = 0

    for cat_dir in sorted(docs_path.iterdir()):
        if cat_dir.is_dir():
            md_files = list(cat_dir.glob('*.md'))
            count = len(md_files)
            stats[cat_dir.name] = count
            total += count

    return stats, total

def count_by_quality(docs_dir):
    docs_path = Path(docs_dir)
    quality_stats = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'unknown': 0}

    for cat_dir in docs_path.iterdir():
        if cat_dir.is_dir():
            for md_file in cat_dir.glob('*.md'):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                    import re
                    match = re.search(r'quality_level:\s*(\S+)', content)
                    if match:
                        level = match.group(1)
                        if level in quality_stats:
                            quality_stats[level] += 1
                        else:
                            quality_stats['unknown'] += 1
                    else:
                        quality_stats['unknown'] += 1
                except:
                    quality_stats['unknown'] += 1

    return quality_stats

if __name__ == '__main__':
    docs_dir = DISCOVER_NEWWIKI2_DOCS

    cat_stats, total = count_docs_by_category(str(docs_dir))
    quality_stats = count_by_quality(docs_dir)

    print("=" * 60)
    print("NewWiki2 文档统计")
    print("=" * 60)
    print(f"\n总文档数: {total}")
    print(f"\n分类统计:")
    for cat, count in sorted(cat_stats.items()):
        print(f"  {cat}: {count}")

    print(f"\n质量等级统计:")
    for level, count in quality_stats.items():
        print(f"  {level}: {count}")
