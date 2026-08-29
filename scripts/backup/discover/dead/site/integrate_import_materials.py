#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import素材整合脚本
从 import 目录中提取相关素材，整合到文章中
"""

import os
import re
import json
import yaml
import random
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"h:\github\cowkb\discover\site")
IMPORT_DIR = Path(r"h:\github\cowkb\import")

ALL_CATEGORIES = [
    "AI与机器学习", "系统与运维", "编程与开发", "数据库与存储",
    "云计算", "知识管理", "产品与设计", "人文社会", "行业动态", "其他",
]

# 分类与import目录的映射
CATEGORY_IMPORT_MAP = {
    "AI与机器学习": ["千问", "doubao", "work"],
    "系统与运维": ["千问", "work", "cnblogs"],
    "编程与开发": ["千问", "work", "cnblogs"],
    "数据库与存储": ["千问", "work", "cnblogs"],
    "云计算": ["千问", "work"],
    "知识管理": ["千问", "doubao"],
    "产品与设计": ["千问", "doubao"],
    "人文社会": ["千问", "doubao"],
    "行业动态": ["千问", "doubao"],
    "其他": ["千问", "doubao", "work"],
}


def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}, content
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return {}, content
    fm_text = match.group(1)
    body = content[match.end():]
    try:
        fm = yaml.safe_load(fm_text)
        if fm is None:
            fm = {}
    except:
        fm = {}
    return fm, body


def build_frontmatter(fm):
    if not fm:
        return ""
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{fm_str}\n---\n\n"


def find_import_materials(category):
    """查找import目录下的相关素材文件"""
    materials = []
    import_dirs = CATEGORY_IMPORT_MAP.get(category, ["千问"])
    
    for subdir in import_dirs:
        dir_path = IMPORT_DIR / subdir
        if not dir_path.exists():
            continue
        
        # 查找 txt 和 md 文件
        for f in dir_path.glob("**/*.txt"):
            materials.append(f)
        for f in dir_path.glob("**/*.md"):
            materials.append(f)
    
    return materials


def extract_material_excerpt(material_path, max_len=300):
    """从素材文件中提取一段摘要"""
    try:
        content = material_path.read_text(encoding="utf-8", errors='ignore')
    except:
        return ""
    
    # 去掉前面的元数据
    if content.startswith("---"):
        match = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
        if match:
            content = content[match.end():]
    
    # 提取前几段
    paragraphs = re.split(r'\n\s*\n', content.strip())
    excerpt = ""
    for p in paragraphs:
        p = p.strip()
        if len(p) > 20:
            excerpt += p[:max_len] + "..."
            break
    
    return excerpt


def has_material_section(body):
    """检查是否已有相关素材章节"""
    return bool(re.search(r'##\s*[📚📎]?\s*相关素材', body))


def add_materials_section(body, category, article_title):
    """添加相关素材章节"""
    if has_material_section(body):
        return body, 0
    
    materials = find_import_materials(category)
    if not materials:
        return body, 0
    
    # 随机选2-3个素材
    num_materials = min(3, len(materials))
    selected = random.sample(materials, num_materials)
    
    section = "\n### 📚 相关素材\n\n"
    for i, mat in enumerate(selected, 1):
        excerpt = extract_material_excerpt(mat, 200)
        if excerpt:
            section += f"**素材{i}：{mat.stem}**\n"
            section += f"> {excerpt[:200]}\n\n"
    
    # 在"延伸阅读"之前插入
    insert_patterns = [
        r'\n---\n\n##\s*[📚🔗]?\s*延伸阅读',
        r'\n---\n\n##\s*[📚🔗]?\s*知识关联',
    ]
    
    insert_pos = len(body)
    for pattern in insert_patterns:
        match = re.search(pattern, body)
        if match:
            insert_pos = match.start()
            break
    
    body = body[:insert_pos] + section + body[insert_pos:]
    
    return body, num_materials


def main():
    print("=" * 70)
    print("import素材整合")
    print("=" * 70)
    
    total = 0
    enhanced = 0
    total_materials = 0
    
    for category in ALL_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue
        
        cat_enhanced = 0
        cat_materials = 0
        cat_total = 0
        
        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            
            try:
                content = md_file.read_text(encoding="utf-8")
            except:
                continue
            
            fm, body = parse_frontmatter(content)
            total += 1
            cat_total += 1
            
            new_body, mats_added = add_materials_section(body, category, md_file.stem)
            
            if mats_added > 0:
                new_content = build_frontmatter(fm) + new_body
                md_file.write_text(new_content, encoding="utf-8")
                enhanced += 1
                cat_enhanced += 1
                total_materials += mats_added
                cat_materials += mats_added
        
        print(f"  【{category}】增强: {cat_enhanced}/{cat_total} 篇, 引用素材: {cat_materials} 个")
    
    print(f"\n总计增强: {enhanced}/{total} 篇")
    print(f"引用素材总数: {total_materials} 个")


if __name__ == "__main__":
    main()
