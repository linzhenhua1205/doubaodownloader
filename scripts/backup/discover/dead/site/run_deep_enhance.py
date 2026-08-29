#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按分类执行深度内容增强
用法: python run_deep_enhance.py "AI与机器学习"
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import random

# 导入深度增强模块
from deep_enhance_full import (
    load_all_articles,
    assess_article_quality,
    build_material_index,
    match_materials,
    build_enhanced_content,
)

BASE_DIR = Path(r"h:\github\cowkb\discover\site")


def enhance_category(category_name, all_articles, category_articles, article_quality, all_materials):
    print(f"\n{'='*80}")
    print(f"开始增强分类: {category_name}")
    print(f"{'='*80}")

    files = category_articles.get(category_name, [])
    if not files:
        print(f"分类 {category_name} 没有找到文章")
        return 0

    pending_files = []
    for f in files:
        if f in all_articles and not all_articles[f]["has_deep_enhance"]:
            pending_files.append(f)

    print(f"\n该分类共 {len(files)} 篇文章，待增强 {len(pending_files)} 篇")

    enhanced_count = 0
    materials_used = 0

    for idx, file_path in enumerate(pending_files, 1):
        try:
            info = all_articles[file_path]
            quality = article_quality.get(file_path, "B")

            print(f"  [{idx}/{len(pending_files)}] 处理: {info['title'][:50]}... ({quality}级)")

            matched = match_materials(info, all_materials, top_n=6)
            materials_used += len(matched)

            new_content = build_enhanced_content(
                info, quality, matched, category_articles, all_articles
            )

            file_path.write_text(new_content, encoding="utf-8")
            enhanced_count += 1

            all_articles[file_path]["content"] = new_content
            all_articles[file_path]["has_deep_enhance"] = True

        except Exception as e:
            print(f"    ❌ 处理失败: {e}")

    print(f"\n✅ {category_name} 增强完成: 共增强 {enhanced_count} 篇文章")
    print(f"   使用素材: {materials_used} 篇次")

    return enhanced_count, materials_used


def main():
    if len(sys.argv) < 2:
        print("用法: python run_deep_enhance.py <分类名称>")
        print("可用分类: AI与机器学习, 系统与运维, 编程与开发, 数据库与存储, 云计算, 知识管理")
        print("或使用 'all' 增强所有分类")
        return

    category_arg = sys.argv[1]

    print("=" * 80)
    print("深度内容增强执行器")
    print("=" * 80)

    print("\n📚 加载文章数据...")
    all_articles, category_articles = load_all_articles()
    print(f"  共加载 {len(all_articles)} 篇文章")

    print("\n📊 评估文章质量...")
    article_quality = {}
    for path, info in all_articles.items():
        article_quality[path] = assess_article_quality(info)
    print("  质量评估完成")

    print("\n📦 构建素材索引...")
    all_materials = build_material_index()
    print(f"  共索引 {len(all_materials)} 个素材文件")

    total_enhanced = 0
    total_materials = 0

    if category_arg == "all":
        categories = ["AI与机器学习", "系统与运维", "编程与开发", "数据库与存储", "云计算", "知识管理"]
    else:
        categories = [category_arg]

    results = {}
    for cat in categories:
        count, mats = enhance_category(cat, all_articles, category_articles, article_quality, all_materials)
        results[cat] = {"enhanced": count, "materials_used": mats}
        total_enhanced += count
        total_materials += mats

    print("\n" + "=" * 80)
    print("📊 增强完成统计")
    print("=" * 80)
    print(f"总计增强文章: {total_enhanced} 篇")
    print(f"总计使用素材: {total_materials} 篇次")
    print("\n各分类详情:")
    for cat, res in results.items():
        print(f"  - {cat}: {res['enhanced']} 篇, 使用素材 {res['materials_used']} 篇次")

    stats_path = BASE_DIR / "deep_enhancement_full_stats.json"
    stats = {
        "total_enhanced": total_enhanced,
        "total_materials_used": total_materials,
        "by_category": results,
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\n📁 统计结果已保存至: {stats_path}")


if __name__ == "__main__":
    main()
