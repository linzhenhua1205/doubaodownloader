#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终质量检查与统计报告
"""

import re
import json
from pathlib import Path
from collections import defaultdict, Counter

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

TECH_CATEGORIES = [
    "AI与机器学习",
    "系统与运维",
    "编程与开发",
    "数据库与存储",
    "云计算",
    "知识管理",
]

REQUIRED_SECTIONS = [
    "背景与上下文",
    "深度解读",
    "2025-2026 最新进展",
    "相关技术资源",
    "延伸阅读",
    "参考来源",
    "changelog",
]


def assess_quality_level(content, title):
    """评估文章质量等级"""
    score = 0
    content_len = len(content)

    # 内容长度评分
    if content_len > 8000:
        score += 25
    elif content_len > 5000:
        score += 20
    elif content_len > 3000:
        score += 15
    elif content_len > 2000:
        score += 10
    elif content_len > 1000:
        score += 5

    # 章节数量评分
    h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
    score += min(h2_count * 2, 10)

    # 标题关键词评分
    deep_keywords = ["深度解析", "技术架构", "原理", "实现", "源码", "算法", "性能", "对比",
                     "白皮书", "研报", "全景", "格局", "趋势", "选型指南", "实战", "指南"]
    keyword_count = sum(1 for kw in deep_keywords if kw in title)
    score += keyword_count * 3

    # 增强内容评分
    enhance_chars = 0
    for section in ["背景与上下文", "深度解读", "最新进展", "相关技术资源"]:
        pos = content.find(section)
        if pos > 0:
            enhance_chars += 200
    score += min(enhance_chars // 100, 15)

    if score >= 35:
        return "S"
    elif score >= 25:
        return "A"
    elif score >= 15:
        return "B"
    else:
        return "C"


def check_article(file_path, category):
    """检查单篇文章的质量"""
    try:
        content = file_path.read_text(encoding="utf-8")
        title = file_path.stem

        result = {
            "filename": file_path.name,
            "title": title,
            "category": category,
            "content_length": len(content),
            "sections": {},
            "quality_level": assess_quality_level(content, title),
        }

        # 检查各章节
        for section in REQUIRED_SECTIONS:
            result["sections"][section] = section in content

        # 检查 import 素材引用
        result["has_import_materials"] = "import 相关素材" in content or "import/千问" in content or "import/cnblogs" in content or "import/doubao" in content
        # 检查 newwiki 引用
        result["has_newwiki"] = "newwiki" in content
        # 检查 knowledge 引用
        result["has_knowledge"] = "knowledge" in content

        # 统计新增字数（估算）
        enhance_section_chars = 0
        for section_name in ["背景与上下文", "深度解读", "2025-2026 最新进展", "相关技术资源", "延伸阅读", "参考来源"]:
            pos = content.find(section_name)
            if pos > 0:
                # 粗略估算每个增强章节的字数
                next_h2 = content.find("\n## ", pos + 10)
                if next_h2 > 0:
                    enhance_section_chars += (next_h2 - pos)
                else:
                    enhance_section_chars += 300
        result["estimated_enhanced_chars"] = enhance_section_chars

        return result
    except Exception as e:
        print(f"检查失败 {file_path}: {e}")
        return None


def main():
    print("=" * 80)
    print("技术类目录深度增强质量检查报告")
    print("=" * 80)

    all_results = []
    by_category = defaultdict(list)
    quality_distribution = Counter()
    section_completeness = Counter()

    total_articles = 0
    total_enhanced_chars = 0

    for category in TECH_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue

        print(f"\n检查分类: {category}")

        for md_file in cat_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue

            result = check_article(md_file, category)
            if result:
                all_results.append(result)
                by_category[category].append(result)
                quality_distribution[result["quality_level"]] += 1
                total_articles += 1
                total_enhanced_chars += result["estimated_enhanced_chars"]

                # 统计章节完整性
                complete = all(result["sections"].values())
                if complete:
                    section_completeness["complete"] += 1
                else:
                    section_completeness["incomplete"] += 1

    print("\n" + "=" * 80)
    print("📊 总体统计")
    print("=" * 80)
    print(f"文章总数: {total_articles} 篇")
    print(f"章节完整: {section_completeness.get('complete', 0)}/{total_articles}")
    print(f"预估新增总字数: 约 {total_enhanced_chars:,} 字")
    print(f"平均每篇新增: 约 {total_enhanced_chars // total_articles if total_articles else 0:,} 字")

    print(f"\n📈 质量等级分布:")
    for level in ["S", "A", "B", "C"]:
        count = quality_distribution.get(level, 0)
        pct = count / total_articles * 100 if total_articles else 0
        bar = "█" * int(pct / 2)
        print(f"  {level}级: {count:3d} 篇 ({pct:5.1f}%) {bar}")

    print(f"\n📋 各分类详情:")
    for category in TECH_CATEGORIES:
        articles = by_category.get(category, [])
        if not articles:
            continue
        cat_quality = Counter(a["quality_level"] for a in articles)
        cat_enhanced = sum(a["estimated_enhanced_chars"] for a in articles)
        complete = sum(1 for a in articles if all(a["sections"].values()))
        print(f"\n  【{category}】共 {len(articles)} 篇")
        print(f"    完整度: {complete}/{len(articles)} | 新增字数: 约 {cat_enhanced:,} 字")
        print(f"    质量分布: S={cat_quality.get('S',0)}, A={cat_quality.get('A',0)}, B={cat_quality.get('B',0)}, C={cat_quality.get('C',0)}")

    # 素材引用统计
    print(f"\n🔗 素材引用统计:")
    has_import = sum(1 for r in all_results if r["has_import_materials"])
    has_newwiki = sum(1 for r in all_results if r["has_newwiki"])
    has_knowledge = sum(1 for r in all_results if r["has_knowledge"])
    print(f"  引用 import 素材: {has_import}/{total_articles} ({has_import/total_articles*100:.1f}%)")
    print(f"  引用 newwiki: {has_newwiki}/{total_articles} ({has_newwiki/total_articles*100:.1f}%)")
    print(f"  引用 knowledge: {has_knowledge}/{total_articles} ({has_knowledge/total_articles*100:.1f}%)")

    # 章节完整性详情
    print(f"\n✅ 章节覆盖率:")
    for section in REQUIRED_SECTIONS:
        count = sum(1 for r in all_results if r["sections"][section])
        pct = count / total_articles * 100 if total_articles else 0
        print(f"  {section}: {count}/{total_articles} ({pct:.1f}%)")

    # 保存详细统计
    stats = {
        "total_articles": total_articles,
        "total_enhanced_chars": total_enhanced_chars,
        "quality_distribution": dict(quality_distribution),
        "section_completeness": {
            "complete": section_completeness.get("complete", 0),
            "incomplete": section_completeness.get("incomplete", 0),
        },
        "by_category": {
            cat: {
                "count": len(articles),
                "quality": dict(Counter(a["quality_level"] for a in articles)),
                "enhanced_chars": sum(a["estimated_enhanced_chars"] for a in articles),
                "complete": sum(1 for a in articles if all(a["sections"].values())),
            }
            for cat, articles in by_category.items()
        },
        "section_coverage": {
            section: sum(1 for r in all_results if r["sections"][section])
            for section in REQUIRED_SECTIONS
        },
        "material_references": {
            "import_materials": has_import,
            "newwiki": has_newwiki,
            "knowledge": has_knowledge,
        },
    }

    stats_path = BASE_DIR / "final_quality_report.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n📁 详细报告已保存至: {stats_path}")
    print("\n" + "=" * 80)
    print("质量检查完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
