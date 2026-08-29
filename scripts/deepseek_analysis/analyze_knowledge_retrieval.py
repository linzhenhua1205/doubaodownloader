#!/usr/bin/env python3
"""
🔍 知识库检索健康度分析脚本 v1.0
=================================
从知识库真实数据出发，量化分析检索效率、内容重复度、元数据覆盖率、
文件交联密度等关键指标，输出健康度报告。

使用方法:
  python3 spec/scripts/analyze_knowledge_retrieval.py              # 完整分析
  python3 spec/scripts/analyze_knowledge_retrieval.py --daily      # 每日简报
  python3 spec/scripts/analyze_knowledge_retrieval.py --dupes      # 仅去重扫描

依赖:
  pip install numpy
  (可选: sentence-transformers → 启用语义去重)
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

# ============================================================
# 配置
# ============================================================
WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KNOWLEDGE_DIR = os.path.join(WORKSPACE, "knowledge")
OUTPUT_DIR = os.path.join(KNOWLEDGE_DIR, "weekly-reports", "07_kb_stat")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


# ============================================================
# 分析函数
# ============================================================

def scan_knowledge_files():
    """扫描所有 knowledge 文件, 收集元数据"""
    results = []
    for root, dirs, files in os.walk(KNOWLEDGE_DIR):
        # 跳过 hidden drectories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, WORKSPACE)
            try:
                with open(fpath, "r", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            lines = content.count("\n") + 1
            chars = len(content)

            # 检测 frontmatter
            fm = None
            if content.startswith("---"):
                fm_end = content.find("---", 3)
                if fm_end > 0:
                    fm_text = content[3:fm_end].strip()
                    fm = _parse_frontmatter(fm_text)

            # 统计链接
            wiki_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            internal_links = [l for l in wiki_links if l[1].startswith("knowledge/")]

            # 检测 index/log 文件
            is_index = fname == "index.md"
            is_log = fname == "log.md"

            results.append({
                "path": rel,
                "fname": fname,
                "dir": os.path.relpath(root, KNOWLEDGE_DIR),
                "lines": lines,
                "chars": chars,
                "size_kb": os.path.getsize(fpath) / 1024,
                "has_frontmatter": fm is not None,
                "frontmatter": fm or {},
                "wiki_links": len(wiki_links),
                "internal_links": len(internal_links),
                "is_index": is_index,
                "is_log": is_log,
            })

    return results


def _parse_frontmatter(text):
    """简易 YAML frontmatter 解析"""
    fm = {}
    current_key = None
    current_list = None
    for line in text.split("\n"):
        # 列表项
        if line.strip().startswith("- "):
            val = line.strip()[2:].strip()
            if current_key and isinstance(current_list, list):
                # 去掉引号
                val = val.strip("\"'")
                current_list.append(val)
            continue
        # key: value
        m = re.match(r'^(\w[\w_]*)\s*:\s*(.*)', line)
        if m:
            current_key = m.group(1)
            raw_val = m.group(2).strip()
            if not raw_val:
                current_list = []
                fm[current_key] = current_list
            else:
                raw_val = raw_val.strip("\"'")
                # 尝试解析列表 [a, b, c]
                if raw_val.startswith("[") and raw_val.endswith("]"):
                    items = [x.strip().strip("\"'") for x in raw_val[1:-1].split(",")]
                    fm[current_key] = items
                elif raw_val.lower() == "true":
                    fm[current_key] = True
                elif raw_val.lower() == "false":
                    fm[current_key] = False
                else:
                    fm[current_key] = raw_val
                current_list = None
    return fm


def analyze_frontmatter_coverage(files):
    """分析 frontmatter 覆盖率"""
    total = len(files)
    has_fm = [f for f in files if f["has_frontmatter"]]
    pct = len(has_fm) / total * 100 if total else 0

    # 按目录统计
    dir_coverage = defaultdict(list)
    for f in files:
        top_dir = f["dir"].split("/")[0] if f["dir"] else "root"
        dir_coverage[top_dir].append(f["has_frontmatter"])

    dir_stats = {}
    for d, vals in sorted(dir_coverage.items()):
        dir_stats[d] = {
            "total": len(vals),
            "has_fm": sum(vals),
            "pct": sum(vals) / len(vals) * 100,
        }

    # 各 frontmatter 字段覆盖率
    field_counts = Counter()
    for f in has_fm:
        for key in f["frontmatter"]:
            field_counts[key] += 1

    field_coverage = {
        k: {"count": v, "pct": v / len(has_fm) * 100 if has_fm else 0}
        for k, v in field_counts.most_common()
    }

    return {
        "total": total,
        "has_frontmatter": len(has_fm),
        "pct": round(pct, 1),
        "dir_stats": dir_stats,
        "field_coverage": field_coverage,
        "ssot_count": sum(1 for f in has_fm if f["frontmatter"].get("ssot") == True),
    }


def analyze_link_density(files):
    """分析文件间链接密度"""
    # 排除 index/log
    content_files = [f for f in files if not f["is_index"] and not f["is_log"]]
    total = len(content_files)
    total_links = sum(f["internal_links"] for f in content_files)
    total_wiki = sum(f["wiki_links"] for f in content_files)

    # 无链接的文件
    no_links = [f for f in content_files if f["internal_links"] == 0]

    # 链接分布
    link_counts = sorted([f["internal_links"] for f in content_files])

    def percentile(data, p):
        if not data:
            return 0
        idx = int(len(data) * p / 100)
        return data[min(idx, len(data) - 1)]

    return {
        "total_content_files": total,
        "total_internal_links": total_links,
        "avg_links_per_file": round(total_links / total, 2) if total else 0,
        "median_links": percentile(link_counts, 50) if link_counts else 0,
        "p25_links": percentile(link_counts, 25),
        "p75_links": percentile(link_counts, 75),
        "files_with_zero_links": len(no_links),
        "zero_link_pct": round(len(no_links) / total * 100, 1) if total else 0,
        "total_wiki_links": total_wiki,
    }


def analyze_file_size_distribution(files):
    """分析文件大小分布"""
    content_files = [f for f in files if not f["is_index"] and not f["is_log"]]
    sizes = sorted([f["lines"] for f in content_files])
    chars_sorted = sorted([f["chars"] for f in content_files])
    n = len(sizes)

    def percentile(data, p):
        if not data:
            return 0
        idx = int(len(data) * p / 100)
        return data[min(idx, len(data) - 1)]

    return {
        "total_content_files": n,
        "size_distribution": {
            f"P{p}": {
                "lines": percentile(sizes, p),
                "chars": percentile(chars_sorted, p),
            }
            for p in [10, 25, 50, 75, 90, 95, 99]
        },
        "large_files_50k": len([f for f in content_files if f["chars"] > 50000]),
        "large_files_100k": len([f for f in content_files if f["chars"] > 100000]),
        "small_files_1k": len([f for f in content_files if f["chars"] < 1000]),
    }


def analyze_duplicate_names(files):
    """检测同名文件分布 (index/log 除外)"""
    name_map = defaultdict(list)
    for f in files:
        if f["is_index"] or f["is_log"]:
            continue
        name_map[f["fname"]].append(f["path"])

    # 只保留出现 2 次以上的
    dupes = {k: v for k, v in name_map.items() if len(v) > 1}
    return {
        "total_duplicate_names": len(dupes),
        "duplicates": sorted(dupes.items(), key=lambda x: -len(x[1]))[:30],
    }


def analyze_ssot_health(files):
    """分析 SSOT 标注健康状况"""
    content_files = [f for f in files if not f["is_index"] and not f["is_log"]]
    with_fm = [f for f in content_files if f["has_frontmatter"]]
    ssot_files = [f for f in with_fm if f["frontmatter"].get("ssot") == True]
    conflicts = []
    superseded = []

    # 检测冲突: 同一 ssot_of 有多个 ssot=True
    ssot_by_topic = defaultdict(list)
    for f in ssot_files:
        topic = f["frontmatter"].get("ssot_of", "")
        if topic:
            ssot_by_topic[topic].append(f["path"])
    for topic, paths in ssot_by_topic.items():
        if len(paths) > 1:
            conflicts.append({"topic": topic, "files": paths})

    # 检测被取代而未标记
    for f in ssot_files:
        if f["frontmatter"].get("status") == "superseded":
            superseded.append(f["path"])

    return {
        "total_ssot": len(ssot_files),
        "unique_ssot_topics": len(set(
            f["frontmatter"].get("ssot_of", "") for f in ssot_files if f["frontmatter"].get("ssot_of")
        )),
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "superseded_count": len(superseded),
        "superseded_files": superseded,
    }


def scan_content_overlap_basic(files):
    """
    基础内容重叠检测 (基于文件名和目录相似度)
    不依赖 embedding, 纯文本分析
    """
    content_files = [f for f in files if not f["is_index"] and not f["is_log"]]

    # 逐文件提取关键词 (从路径和文件名)
    topics = defaultdict(list)
    for f in content_files:
        # 从路径提取有意义的词
        path_parts = f["dir"].split("/") + [f["fname"].replace(".md", "")]
        meaningful = [p for p in path_parts if len(p) > 3
                      and p not in ("index", "knowledge")]
        for p in meaningful:
            topics[p].append(f["path"])

    # 找到在不同子目录下讨论同一主题的文件
    cross_dir = {k: v for k, v in topics.items()
                 if len(v) > 1 and len(set(
                     os.path.dirname(p) for p in v
                 )) > 1}

    return {
        "cross_directory_topics": len(cross_dir),
        "top_cross_topics": sorted(
            cross_dir.items(), key=lambda x: -len(x[1])
        )[:20],
    }


# ============================================================
# 报告输出
# ============================================================

def generate_report(files, cov, links, size_dist, dupes, ssot, overlap):
    """生成完整 Markdown 报告"""
    lines = []
    def w(s=""):
        lines.append(s)

    w("# 🔍 知识库检索健康度分析报告")
    w()
    w(f"> **自动生成**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    w(f"> **扫描范围**: `knowledge/` — {len(files)} 文件")
    w()

    # ========== 1. 概要 ==========
    w("## 1. 🎯 核心指标速览")
    w()
    w("| 指标 | 数值 | 状态 |")
    w("|:-----|:----:|:----:|")
    w(f"| 总文件数 | {len(files)} | — |")
    w(f"| 有效内容文件 | {links['total_content_files']} | — |")
    w(f"| Frontmatter 覆盖率 | {cov['pct']}% | "
      f"{'✅' if cov['pct'] > 50 else '⚠️' if cov['pct'] > 10 else '🔴'} |")
    w(f"| SSOT 标注数 | {ssot['total_ssot']} | "
      f"{'✅' if ssot['total_ssot'] > 50 else '⚠️' if ssot['total_ssot'] > 10 else '🔴'} |")
    w(f"| SSOT 主题冲突 | {ssot['conflict_count']} | "
      f"{'✅' if ssot['conflict_count'] == 0 else '🔴'} |")
    w(f"| 平均交叉链接/文件 | {links['avg_links_per_file']} | "
      f"{'✅' if links['avg_links_per_file'] > 1 else '⚠️'} |")
    w(f"| 零链接文件 | {links['files_with_zero_links']} ({links['zero_link_pct']}%) | "
      f"{'⚠️' if links['zero_link_pct'] > 50 else '✅'} |")
    w(f"| 同名文件分布 | {dupes['total_duplicate_names']} 组 | "
      f"{'⚠️' if dupes['total_duplicate_names'] > 10 else '✅'} |")
    w(f"| 跨目录同主题 | {overlap['cross_directory_topics']} 个 | "
      f"{'⚠️' if overlap['cross_directory_topics'] > 20 else '✅'} |")
    w(f"| 超大文件 (>100KB) | {size_dist['large_files_100k']} | "
      f"{'🔴' if size_dist['large_files_100k'] > 10 else '⚠️'} |")
    w()

    # ========== 2. 元数据覆盖 ==========
    w("## 2. 📋 元数据 (Frontmatter) 覆盖率")
    w()
    w(f"### 2.1 总体覆盖率")
    w()
    w(f"| 指标 | 数值 |")
    w(f"|:-----|:----:|")
    w(f"| 总文件数 | {cov['total']} |")
    w(f"| 含 frontmatter | {cov['has_frontmatter']} |")
    w(f"| 覆盖率 | **{cov['pct']}%** |")
    w(f"| SSOT 标注 | {cov['ssot_count']} |")
    w()

    w("### 2.2 按顶层目录覆盖率")
    w()
    w("| 目录 | 总文件 | 含 FM | 覆盖率 |")
    w("|:-----|:------:|:-----:|:------:|")
    for d, stats in cov["dir_stats"].items():
        emoji = "✅" if stats["pct"] > 50 else ("⚠️" if stats["pct"] > 10 else "🔴")
        w(f"| {d} | {stats['total']} | {stats['has_fm']} | {emoji} {stats['pct']:.0f}% |")
    w()

    w("### 2.3 字段覆盖率 (已有 FM 的文件中)")
    w()
    w("| 字段 | 出现次数 | 覆盖率 |")
    w("|:-----|:-------:|:------:|")
    for field, stats in cov["field_coverage"].items():
        w(f"| `{field}` | {stats['count']} | {stats['pct']:.0f}% |")
    w()

    # ========== 3. 链接密度 ==========
    w("## 3. 🔗 文件间链接密度")
    w()
    w("| 指标 | 数值 |")
    w("|:-----|:----:|")
    w(f"| 有效内容文件 | {links['total_content_files']} |")
    w(f"| 总内部链接数 | {links['total_internal_links']:,} |")
    w(f"| 平均链接/文件 | {links['avg_links_per_file']} |")
    w(f"| 中位数链接 | {links['median_links']} |")
    w(f"| P25 | {links['p25_links']} | P75: {links['p75_links']} |")
    w(f"| 零链接文件 | {links['files_with_zero_links']} ({links['zero_link_pct']}%) |")
    w(f"| 总 Wiki 链接 | {links['total_wiki_links']:,} |")
    w()

    w(f"> **诊断**: 中位数链接数 = {links['median_links']} 说明多数文件几乎无交叉引用。"
      f"零链接文件占比 {links['zero_link_pct']}% 说明信息孤岛严重。"
      f"建议: 每个文件至少 1-3 个 internal link 到相关文档。")
    w()

    # ========== 4. 文件大小 ==========
    w("## 4. 📏 文件大小分布")
    w()
    w("| 百分位 | 行数 | 字符数 |")
    w("|:------:|:----:|:------:|")
    for p, vals in size_dist["size_distribution"].items():
        w(f"| {p} | {vals['lines']:,} | {vals['chars']:,} |")
    w()
    w(f"| 超大文件 (>100KB) | **{size_dist['large_files_100k']}** 🔴 |")
    w(f"| 大文件 (50-100KB) | {size_dist['large_files_50k']} |")
    w(f"| 微小文件 (<1KB) | {size_dist['small_files_1k']} |")
    w()

    # ========== 5. 同名重复检测 ==========
    w("## 5. 🗂️ 同名文件分布")
    w()
    w(f"发现 **{dupes['total_duplicate_names']}** 组同名文件 (不含 index/log):")
    w()
    w("| 文件名 | 出现次数 | 路径 |")
    w("|:-------|:--------:|:-----|")
    for name, paths in dupes["duplicates"][:20]:
        for i, p in enumerate(paths):
            marker = "└─" if i == len(paths) - 1 else "├─" if i == 0 else "│ "
            w(f"| {'**' + name + '**' if i == 0 else ''} | {len(paths) if i == 0 else ''} | {marker} {p} |")
    w()

    # ========== 6. SSOT 健康度 ==========
    w("## 6. ✅ SSOT 标注健康度")
    w()
    w(f"| 指标 | 数值 |")
    w(f"|:-----|:----:|")
    w(f"| SSOT 文档数 | {ssot['total_ssot']} |")
    w(f"| 唯一子题数 | {ssot['unique_ssot_topics']} |")
    w(f"| 冲突数 (同 topic 多个 SSOT) | **{ssot['conflict_count']}** "
      f"{'🔴' if ssot['conflict_count'] > 0 else '✅'} |")
    w(f"| 已废弃文档 | {ssot['superseded_count']} |")
    w()

    if ssot["conflicts"]:
        w("**SSOT 冲突详情:**")
        w()
        for c in ssot["conflicts"]:
            w(f"- `{c['topic']}`: 多个 SSOT — {'; '.join(c['files'])}")
        w()

    # ========== 7. 跨目录主题 ==========
    w("## 7. 🔄 跨目录主题分布")
    w()
    w(f"发现 **{overlap['cross_directory_topics']}** 个主题词出现在多个目录:")
    w()
    w("| 主题词 | 出现次数 | 涉及目录数 | 路径 |")
    w("|:-------|:--------:|:----------:|:-----|")
    for topic, paths in overlap["top_cross_topics"][:20]:
        dirs = set(os.path.dirname(p) for p in paths)
        w(f"| {topic} | {len(paths)} | {len(dirs)} | {', '.join(paths[:3])}... |")
    w()

    # ========== 8. 综合建议 ==========
    w("## 8. 📋 综合建议与优先级")
    w()

    issues = []

    # 基于数据生成建议
    if cov["pct"] < 50:
        issues.append({
            "p": "P0 🚨",
            "issue": f"Frontmatter 覆盖率仅 {cov['pct']}%",
            "action": "批量补全元数据, 优先覆盖高频访问文件",
        })

    if links["zero_link_pct"] > 50:
        issues.append({
            "p": "P0 🚨",
            "issue": f"零链接文件占比 {links['zero_link_pct']}%",
            "action": "至少为每个文件添加 1-3 个 internal link",
        })

    if ssot["conflict_count"] > 0:
        issues.append({
            "p": "P0 🚨",
            "issue": f"SSOT 冲突 {ssot['conflict_count']} 处",
            "action": "人工裁决冲突, 确保每主题唯一 SSOT",
        })

    if size_dist["large_files_100k"] > 10:
        issues.append({
            "p": "P1 🟠",
            "issue": f"超大文件 {size_dist['large_files_100k']} 个 (>100KB)",
            "action": "拆分到子文件, 单文件 < 50KB",
        })

    if dupes["total_duplicate_names"] > 10:
        issues.append({
            "p": "P1 🟠",
            "issue": f"同名文件 {dupes['total_duplicate_names']} 组",
            "action": "检查是否内容重复, 合并或重命名",
        })

    if ssot["total_ssot"] < 30:
        issues.append({
            "p": "P1 🟠",
            "issue": f"SSOT 标注仅 {ssot['total_ssot']} 个",
            "action": "增加 SSOT 标注覆盖核心主题",
        })

    w("| 优先级 | 问题 | 建议行动 |")
    w("|:------:|:-----|:---------|")
    for issue in sorted(issues, key=lambda x: {"P0 🚨": 0, "P1 🟠": 1, "P2 🟡": 2}.get(x["p"], 99)):
        w(f"| {issue['p']} | {issue['issue']} | {issue['action']} |")

    if not issues:
        w("✅ 未发现严重问题, 知识库健康度良好!")
    w()

    # ========== 9. 附录 ==========
    w("## 9. 📎 附录：原始数据")
    w()
    w(f"| 字段 | 值 |")
    w(f"|:-----|:---|")
    w(f"| 生成时间 | {datetime.now().strftime('%Y-%m-%d %H:%M')} |")
    w(f"| 扫描范围 | {KNOWLEDGE_DIR} |")
    w(f"| 总文件 | {len(files)} |")
    w(f"| 有效内容文件 | {links['total_content_files']} |")
    w(f"| 设计文档参考 | `spec/design-008-knowledge-retrieval-framework.md` |")
    w()

    return "\n".join(lines)


def save_report(report):
    """保存报告"""
    fname = f"{TIMESTAMP}-kb-retrieval-health-report.md"
    fpath = os.path.join(OUTPUT_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(report)
    return fname, fpath


def run_full_analysis():
    """执行完整分析"""
    print(f"🔍 知识库检索健康度分析 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  扫描目录: {KNOWLEDGE_DIR}")
    print()

    print("📂 扫描文件...", end=" ", flush=True)
    files = scan_knowledge_files()
    print(f"完成 ({len(files)} 文件)")

    print("📋 分析 frontmatter 覆盖率...", end=" ", flush=True)
    cov = analyze_frontmatter_coverage(files)
    print(f"完成 ({cov['pct']}%)")

    print("🔗 分析链接密度...", end=" ", flush=True)
    links = analyze_link_density(files)
    print(f"完成 (平均 {links['avg_links_per_file']} 链接/文件)")

    print("📏 分析文件大小分布...", end=" ", flush=True)
    size_dist = analyze_file_size_distribution(files)
    print(f"完成 ({size_dist['large_files_100k']} 个超大文件)")

    print("🗂️ 检测同名文件...", end=" ", flush=True)
    dupes = analyze_duplicate_names(files)
    print(f"完成 ({dupes['total_duplicate_names']} 组)")

    print("✅ 分析 SSOT 健康度...", end=" ", flush=True)
    ssot = analyze_ssot_health(files)
    print(f"完成 ({ssot['total_ssot']} 个 SSOT, {ssot['conflict_count']} 处冲突)")

    print("🔄 分析跨目录主题...", end=" ", flush=True)
    overlap = scan_content_overlap_basic(files)
    print(f"完成 ({overlap['cross_directory_topics']} 个跨目录主题)")

    print()
    print("📝 生成报告...", end=" ", flush=True)
    report = generate_report(files, cov, links, size_dist, dupes, ssot, overlap)
    fname, fpath = save_report(report)
    print(f"完成")
    print()
    print(f"✅ 报告: {os.path.relpath(fpath, WORKSPACE)}")
    print()

    # 摘要输出
    print("=" * 60)
    print("📊 核心健康指标:")
    print(f"   文件数: {len(files)}")
    print(f"   Frontmatter: {cov['pct']}% {'✅' if cov['pct'] > 50 else '⚠️'}")
    print(f"   平均链接: {links['avg_links_per_file']} {'✅' if links['avg_links_per_file'] > 1 else '⚠️'}")
    print(f"   零链接: {links['files_with_zero_links']} ({links['zero_link_pct']}%) {'🔴' if links['zero_link_pct'] > 50 else '⚠️'}")
    print(f"   SSOT: {ssot['total_ssot']} 个, 冲突 {ssot['conflict_count']} 处")
    print(f"   同名重复: {dupes['total_duplicate_names']} 组")
    print(f"   超大文件: {size_dist['large_files_100k']}")
    print("=" * 60)


if __name__ == "__main__":
    if "--daily" in sys.argv:
        files = scan_knowledge_files()
        cov = analyze_frontmatter_coverage(files)
        links = analyze_link_density(files)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] KB 健康: "
              f"FM={cov['pct']}% 链接={links['avg_links_per_file']}/文件 "
              f"SSOT={cov['ssot_count']}个 "
              f"零链接={links['files_with_zero_links']}个")
    elif "--dupes" in sys.argv:
        files = scan_knowledge_files()
        dupes = analyze_duplicate_names(files)
        print(f"同名文件重复组: {dupes['total_duplicate_names']}")
        for name, paths in dupes["duplicates"]:
            print(f"  {name} ({len(paths)}次):")
            for p in paths:
                print(f"    - {p}")
    else:
        run_full_analysis()
