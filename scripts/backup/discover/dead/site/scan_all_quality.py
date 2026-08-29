#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import yaml
from pathlib import Path
from collections import defaultdict, Counter

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

ALL_CATEGORIES = [
    "AI与机器学习",
    "系统与运维",
    "编程与开发",
    "数据库与存储",
    "云计算",
    "知识管理",
    "产品与设计",
    "人文社会",
    "行业动态",
    "其他",
]


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


def assess_article_quality(content, body, title):
    content_len = len(body)
    score = 0

    if content_len > 5000:
        score += 25
    elif content_len > 3000:
        score += 20
    elif content_len > 2000:
        score += 15
    elif content_len > 1000:
        score += 10
    elif content_len > 500:
        score += 5

    h2_count = len(re.findall(r'^## ', body, re.MULTILINE))
    score += min(h2_count * 2, 10)

    h3_count = len(re.findall(r'^### ', body, re.MULTILINE))
    score += min(h3_count * 1, 5)

    deep_keywords = ["深度解析", "技术架构", "原理", "实现", "源码", "算法", "性能", "对比",
                     "白皮书", "研报", "全景", "格局", "趋势", "选型指南", "实战", "全解析"]
    keyword_count = sum(1 for kw in deep_keywords if kw in title)
    score += keyword_count * 3

    if re.search(r'202[56]', title):
        score += 5

    table_count = body.count("| --- |")
    score += min(table_count * 2, 6)

    if score >= 35:
        return "S"
    elif score >= 25:
        return "A"
    elif score >= 15:
        return "B"
    else:
        return "C"


def get_sections(content):
    sections = []
    for s in ["背景与上下文", "核心要点", "深度解读", "最新进展", "更新记录", 
              "相关素材", "相关文章", "延伸阅读", "技术原理", "行业影响",
              "案例补充", "参考来源", "全景分析", "技术演进", "对比分析",
              "实践指南", "风险与挑战"]:
        if s in content:
            sections.append(s)
    return sections


def main():
    all_articles = {}
    category_articles = defaultdict(list)
    quality_dist = Counter()
    category_quality = defaultdict(Counter)
    c_articles = []
    b_articles = []
    a_articles = []
    s_articles = []

    for category in ALL_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue

        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(content)
                title = fm.get("title", md_file.stem)
                quality = assess_article_quality(content, body, title)
                sections = get_sections(content)
                content_len = len(body)

                info = {
                    "title": title,
                    "path": str(md_file),
                    "category": category,
                    "quality": quality,
                    "content_len": content_len,
                    "sections": sections,
                    "has_background": "背景与上下文" in content,
                    "has_deep": "深度解读" in content,
                    "has_latest": "最新进展" in content or "更新记录" in content,
                    "has_materials": "相关素材" in content,
                    "has_related": "相关文章" in content,
                    "has_reference": "参考来源" in content,
                }

                all_articles[str(md_file)] = info
                category_articles[category].append(info)
                quality_dist[quality] += 1
                category_quality[category][quality] += 1

                if quality == "C":
                    c_articles.append(info)
                elif quality == "B":
                    b_articles.append(info)
                elif quality == "A":
                    a_articles.append(info)
                elif quality == "S":
                    s_articles.append(info)

            except Exception as e:
                print(f"读取失败 {md_file}: {e}")

    print("=" * 70)
    print("全量文章质量扫描报告")
    print("=" * 70)
    print(f"\n总文章数: {len(all_articles)}")
    print(f"\n质量分布:")
    for q in ["S", "A", "B", "C"]:
        print(f"  {q}级: {quality_dist[q]} 篇 ({quality_dist[q]/len(all_articles)*100:.1f}%)")

    print(f"\n各分类质量分布:")
    for cat in ALL_CATEGORIES:
        if cat not in category_articles:
            continue
        total = len(category_articles[cat])
        q = category_quality[cat]
        print(f"\n  【{cat}】({total}篇)")
        print(f"    S={q['S']}, A={q['A']}, B={q['B']}, C={q['C']}")

    print(f"\n" + "=" * 70)
    print(f"C级文章列表 ({len(c_articles)}篇) - 需升级到B级")
    print("=" * 70)
    for a in sorted(c_articles, key=lambda x: (x["category"], x["title"])):
        print(f"  [{a['category']}] {a['title']} ({a['content_len']}字)")

    print(f"\n" + "=" * 70)
    print(f"B级文章列表 ({len(b_articles)}篇) - 需升级到A级")
    print("=" * 70)
    for a in sorted(b_articles, key=lambda x: (x["category"], x["title"])):
        print(f"  [{a['category']}] {a['title']} ({a['content_len']}字)")

    result = {
        "total": len(all_articles),
        "quality_distribution": dict(quality_dist),
        "category_quality": {k: dict(v) for k, v in category_quality.items()},
        "c_articles": c_articles,
        "b_articles": b_articles,
        "a_articles": a_articles,
        "s_articles": s_articles,
    }

    with open(BASE_DIR / "full_quality_scan.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n📁 详细数据已保存至: full_quality_scan.json")


if __name__ == "__main__":
    main()
