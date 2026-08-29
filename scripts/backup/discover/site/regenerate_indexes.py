#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成分类索引
从文章内容中提取原文标题作为简要说明
"""

import re
from pathlib import Path
from urllib.parse import quote
import sys

sys.path.insert(0, str(Path(__file__).parent))
from enhance_articles import (
    BASE_DIR, KEY_CATEGORIES, calculate_star_rating, 
    get_article_quality_score, parse_frontmatter
)


def extract_original_title(body):
    """从文章内容中提取原文标题"""
    pattern = r'原文[：:]\s*\[([^\]]+)\]\([^)]+\)'
    match = re.search(pattern, body)
    if match:
        return match.group(1)
    return ""


def regenerate_indexes():
    """重新生成分类索引"""
    
    total_featured = 0
    
    for category_dir in BASE_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        if category_dir.name.startswith("."):
            continue
        
        category = category_dir.name
        index_path = category_dir / "index.md"
        if not index_path.exists():
            continue
        
        print(f"处理 {category}/index.md ...")
        
        # 读取当前索引（保留分类说明等前面的内容）
        index_content = index_path.read_text(encoding="utf-8")
        
        # 收集所有文章的信息
        articles = []
        for md_file in category_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(content)
                title = fm.get("title", md_file.stem)
                stars = calculate_star_rating(title, body, fm)
                quality_score = get_article_quality_score(title, body, fm, stars)
                
                # 提取原文标题作为简要说明
                original_title = extract_original_title(body)
                desc = f"原文：{original_title}" if original_title else ""
                
                articles.append({
                    "path": md_file,
                    "name": md_file.name,
                    "title": title,
                    "stars": stars,
                    "quality_score": quality_score,
                    "desc": desc,
                })
            except Exception as e:
                print(f"  读取失败 {md_file.name}: {e}")
        
        # 按质量分排序
        articles.sort(key=lambda x: x["quality_score"], reverse=True)
        
        # 构建新的表格
        new_table = "## 文章清单\n\n"
        new_table += f"共 **{len(articles)}** 篇文章\n\n"
        new_table += "| 序号 | 质量 | 文章标题 | 简要说明 |\n"
        new_table += "|:----:|:----:|:---------|:---------|\n"
        
        for idx, art in enumerate(articles, 1):
            fname = art["name"]
            encoded_name = quote(fname)
            stars_display = "⭐" * art["stars"]
            
            new_table += f"| {idx} | {stars_display} | [{art['title']}]({encoded_name}) | {art['desc']} |\n"
        
        # 精选文章
        featured_block = ""
        if category in KEY_CATEGORIES:
            n_featured = KEY_CATEGORIES[category]
            featured = articles[:n_featured]
            total_featured += len(featured)
            
            featured_block = f"\n## 🌟 精选文章\n\n"
            featured_block += f"精选 {len(featured)} 篇高质量文章，优先阅读：\n\n"
            for idx, art in enumerate(featured, 1):
                fname = art["name"]
                encoded_name = quote(fname)
                stars_display = "⭐" * art["stars"]
                featured_block += f"{idx}. [{art['title']}]({encoded_name}) {stars_display}\n"
            featured_block += "\n"
        
        # 找到上层入口的位置
        upper_entry = index_content.find("## 上层入口")
        if upper_entry == -1:
            upper_entry = len(index_content)
        
        # 找到文章清单开始位置
        desc_end = index_content.find("## 文章清单")
        if desc_end == -1:
            print(f"  未找到文章清单，跳过")
            continue
        
        new_index = index_content[:desc_end]
        new_index += new_table
        new_index += featured_block
        new_index += "\n" + index_content[upper_entry:]
        
        index_path.write_text(new_index, encoding="utf-8")
        print(f"  完成，共 {len(articles)} 篇文章")
    
    print(f"\n精选文章总数: {total_featured}")


if __name__ == "__main__":
    regenerate_indexes()
