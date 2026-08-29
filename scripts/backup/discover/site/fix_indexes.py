#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复分类索引中的简要说明
"""

import re
from pathlib import Path
from urllib.parse import unquote, quote
import sys

sys.path.insert(0, str(Path(__file__).parent))
from enhance_articles import (
    BASE_DIR, KEY_CATEGORIES, calculate_star_rating, 
    get_article_quality_score, parse_frontmatter
)


def fix_category_indexes():
    """修复分类索引的简要说明"""
    
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
        
        # 读取当前索引
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
                articles.append({
                    "path": md_file,
                    "name": md_file.name,
                    "title": title,
                    "stars": stars,
                    "quality_score": quality_score,
                })
            except Exception as e:
                print(f"  读取失败 {md_file.name}: {e}")
        
        # 按质量分排序
        articles.sort(key=lambda x: x["quality_score"], reverse=True)
        
        # 从原始索引中提取简要说明
        # 用原始文件中的行来匹配 - 通过URL编码后的文件名匹配
        desc_map = {}  # filename -> desc
        
        lines = index_content.split("\n")
        in_table = False
        for line in lines:
            if line.startswith("| 序号 |") and "文章标题" in line:
                in_table = True
                continue
            if in_table and line.startswith("|") and ".md" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    # 根据列数判断
                    # 新格式: | 序号 | 质量 | 文章标题 | 简要说明 | -> parts有6个(含首尾空)
                    # 旧格式: | 序号 | 文章标题 | 简要说明 | -> parts有5个(含首尾空)
                    if "质量" in line or len(parts) >= 6:
                        # 新格式，第4列是标题，第5列是说明
                        title_col = parts[3]
                        desc_col = parts[4]
                    else:
                        # 旧格式，第3列是标题，第4列是说明
                        title_col = parts[2]
                        desc_col = parts[3]
                    
                    # 从标题列提取文件名
                    file_match = re.search(r'\]\(([^)]+)\)', title_col)
                    if file_match:
                        fname_encoded = file_match.group(1)
                        try:
                            fname_decoded = unquote(fname_encoded)
                        except:
                            fname_decoded = fname_encoded
                        # 用解码后的文件名作为key
                        desc_map[fname_decoded] = desc_col
                        # 也用编码后的存一份
                        desc_map[fname_encoded] = desc_col
        
        print(f"  提取到 {len(desc_map)} 条简要说明")
        
        # 构建新的表格
        new_table = "## 文章清单\n\n"
        new_table += f"共 **{len(articles)}** 篇文章\n\n"
        new_table += "| 序号 | 质量 | 文章标题 | 简要说明 |\n"
        new_table += "|:----:|:----:|:---------|:---------|\n"
        
        for idx, art in enumerate(articles, 1):
            fname = art["name"]
            encoded_name = quote(fname)
            stars_display = "⭐" * art["stars"]
            
            # 查找简要说明
            desc = ""
            # 先用原始文件名找
            if fname in desc_map:
                desc = desc_map[fname]
            # 再用URL编码的找
            elif encoded_name in desc_map:
                desc = desc_map[encoded_name]
            # 再模糊匹配
            if not desc:
                for k, v in desc_map.items():
                    if k and fname and (k in fname or fname in k):
                        desc = v
                        break
            
            new_table += f"| {idx} | {stars_display} | [{art['title']}]({encoded_name}) | {desc} |\n"
        
        # 精选文章
        featured_block = ""
        if category in KEY_CATEGORIES:
            n_featured = KEY_CATEGORIES[category]
            featured = articles[:n_featured]
            
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
        print(f"  完成")


if __name__ == "__main__":
    fix_category_indexes()
