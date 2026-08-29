#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统计增强结果"""

from pathlib import Path
import re

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

def main():
    total_articles = 0
    with_metadata = 0
    with_key_points = 0
    with_reading_more = 0
    with_duplicate_note = 0
    categories = {}
    duplicates = set()
    
    for cat_dir in BASE_DIR.iterdir():
        if not cat_dir.is_dir():
            continue
        if cat_dir.name.startswith("."):
            continue
        
        category = cat_dir.name
        cat_count = 0
        
        for md_file in cat_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue
            
            total_articles += 1
            cat_count += 1
            
            try:
                content = md_file.read_text(encoding="utf-8")
                
                if "📅 **发布时间**" in content:
                    with_metadata += 1
                if "## 💡 核心要点" in content:
                    with_key_points += 1
                if "## 📚 延伸阅读" in content:
                    with_reading_more += 1
                if "🔄 **注意**" in content:
                    with_duplicate_note += 1
                    
                    # 提取重复文章对
                    match = re.search(r'本文与 \[([^\]]+)\]', content)
                    if match:
                        pair = tuple(sorted([md_file.name, match.group(1)]))
                        duplicates.add(pair)
            except:
                pass
        
        categories[category] = cat_count
    
    # 统计精选文章数
    total_featured = 0
    for cat_dir in BASE_DIR.iterdir():
        if not cat_dir.is_dir():
            continue
        index_path = cat_dir / "index.md"
        if not index_path.exists():
            continue
        try:
            content = index_path.read_text(encoding="utf-8")
            if "## 🌟 精选文章" in content:
                # 数精选列表项
                lines = content.split("\n")
                in_featured = False
                for line in lines:
                    if "## 🌟 精选文章" in line:
                        in_featured = True
                        continue
                    if in_featured and line.startswith("## "):
                        break
                    if in_featured and re.match(r'^\d+\.', line):
                        total_featured += 1
        except:
            pass
    
    print("=" * 60)
    print("文章质量提升 - 最终统计")
    print("=" * 60)
    print(f"\n📊 总体数据")
    print(f"  处理文章总数: {total_articles}")
    print(f"  添加元数据头部: {with_metadata}")
    print(f"  添加核心要点: {with_key_points}")
    print(f"  添加延伸阅读: {with_reading_more}")
    print(f"  发现重复文章对: {len(duplicates)}")
    print(f"  标记重复文章: {with_duplicate_note}")
    print(f"  精选文章总数: {total_featured}")
    
    print(f"\n📁 分类分布")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} 篇")
    
    print(f"\n🔄 重复文章对列表:")
    for p1, p2 in sorted(duplicates):
        print(f"  - {p1} <-> {p2}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
