#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤1: 建立文章和素材索引
"""
import os, re, json
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

BASE_DIR = Path(r"h:\github\cowkb\discover\site")
IMPORT_DIR = Path(r"h:\github\cowkb\import")

print("=" * 60)
print("步骤1: 建立文章索引")
print("=" * 60)

all_articles = {}
category_articles = defaultdict(list)

for item in BASE_DIR.iterdir():
    if not item.is_dir():
        continue
    category = item.name
    if category.startswith(".") or category == "__pycache__":
        continue
    
    count = 0
    for md_file in item.glob("*.md"):
        if md_file.name == "index.md":
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            
            # 提取frontmatter
            fm = {}
            body = content
            if content.startswith("---"):
                match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
                if match:
                    body = content[match.end():]
                    try:
                        import yaml
                        fm = yaml.safe_load(match.group(1)) or {}
                    except:
                        fm = {}
            
            title = fm.get("title", md_file.stem)
            
            all_articles[str(md_file)] = {
                "title": title,
                "category": category,
                "content_len": len(content),
                "path": str(md_file),
                "dir_path": str(item),
                "name": md_file.name,
            }
            category_articles[category].append(str(md_file))
            count += 1
        except Exception as e:
            print(f"  错误: {md_file.name}: {e}")
    
    print(f"  {category}: {count} 篇")

print(f"\n总计: {len(all_articles)} 篇文章")

# 保存文章索引
with open(BASE_DIR / "articles_index.json", "w", encoding="utf-8") as f:
    json.dump({
        "articles": all_articles,
        "categories": {k: v for k, v in category_articles.items()},
    }, f, ensure_ascii=False, indent=2)

print(f"\n文章索引已保存到 articles_index.json")

print("\n" + "=" * 60)
print("步骤2: 建立import素材索引")
print("=" * 60)

materials = []
import_dirs = {
    "cnblogs": IMPORT_DIR / "cnblogs",
    "doubao": IMPORT_DIR / "doubao",
    "work_jinghua": IMPORT_DIR / "work" / "精华",
    "qianwen": IMPORT_DIR / "千问",
}

for source_name, dir_path in import_dirs.items():
    if not dir_path.exists():
        print(f"  跳过不存在的目录: {dir_path}")
        continue
    
    count = 0
    for md_file in dir_path.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            title = md_file.stem
            
            # 计算相对路径
            rel_path = str(md_file.relative_to(BASE_DIR.parent.parent)).replace("\\", "/")
            
            materials.append({
                "title": title,
                "source": source_name,
                "path": str(md_file),
                "rel_path": rel_path,
                "content_preview": content[:1000],
                "content_len": len(content),
            })
            count += 1
        except Exception as e:
            pass
    
    print(f"  {source_name}: {count} 个文件")

print(f"\n总计: {len(materials)} 个素材文件")

# 保存素材索引
with open(BASE_DIR / "materials_index.json", "w", encoding="utf-8") as f:
    json.dump(materials, f, ensure_ascii=False, indent=2)

print(f"\n素材索引已保存到 materials_index.json")

print("\n" + "=" * 60)
print("步骤3: 检测重复文章")
print("=" * 60)

duplicates = []
articles_list = list(all_articles.items())

for i in range(len(articles_list)):
    path1, info1 = articles_list[i]
    for j in range(i + 1, len(articles_list)):
        path2, info2 = articles_list[j]
        
        if info1["category"] != info2["category"]:
            continue
        
        title_sim = SequenceMatcher(None, info1["title"], info2["title"]).ratio()
        
        if title_sim > 0.65:
            duplicates.append({
                "path1": path1,
                "path2": path2,
                "title1": info1["title"],
                "title2": info2["title"],
                "title_sim": title_sim,
                "len1": info1["content_len"],
                "len2": info2["content_len"],
                "category": info1["category"],
            })

print(f"发现 {len(duplicates)} 对重复/相似文章")
for dup in duplicates[:15]:
    print(f"  [{dup['category']}] {dup['title1'][:40]} <-> {dup['title2'][:40]} (相似度: {dup['title_sim']:.2f})")

# 保存重复文章列表
with open(BASE_DIR / "duplicates.json", "w", encoding="utf-8") as f:
    json.dump(duplicates, f, ensure_ascii=False, indent=2)

print(f"\n重复文章列表已保存到 duplicates.json")

print("\n✅ 步骤1-3完成！")
