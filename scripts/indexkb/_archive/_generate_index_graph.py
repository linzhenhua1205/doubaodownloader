#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成各目录 index.md 的知识图谱版本
- 每个文件的概要描述
- 目录内文件间关系（引用、互补、重复）
- 跨目录关系
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"h:\github\cowkb\knowledge")

with open(ROOT / "_knowledge_graph_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

files = data["files"]
dirs_raw = data["directories"]
backlinks = data["backlinks"]

# 将 dirs 从 {dir: [paths]} 转为 {dir: {path: file_info}}
dirs = {}
for d, paths in dirs_raw.items():
    dirs[d] = {p: files[p] for p in paths if p in files}

# 重建相似度字典
sim_map = {}
# 从 JSON 中提取（如果有的话）
# 由于 JSON 里 duplicates 和 complementary 只有 Top，我们重新从 files 计算相似度
def get_similarity(f1, f2):
    k1 = set(f1["keywords"])
    k2 = set(f2["keywords"])
    if not k1 or not k2:
        return 0, []
    overlap = k1 & k2
    union = k1 | k2
    sim = len(overlap) / len(union) if union else 0
    return sim, list(overlap)[:6]


def format_file_link(path):
    """生成相对路径的 markdown 链接"""
    name = Path(path).stem
    return f"[{name}]({path})"


def get_file_size_label(word_count):
    if word_count >= 10000:
        return "📕 巨篇"
    elif word_count >= 5000:
        return "📗 长文"
    elif word_count >= 2000:
        return "📘 中篇"
    else:
        return "📙 短篇"


def generate_dir_index(dir_path, dir_files, all_files, backlinks):
    """生成一个目录的 index.md 内容"""
    lines = []
    dir_name = dir_path.split("/")[-1] if dir_path != "." else "根目录"

    lines.append(f"# 📚 {dir_name} 目录知识图谱")
    lines.append("")
    lines.append(f"> 📊 本目录共 **{len(dir_files)}** 个文件")
    lines.append("")

    # 按文件大小排序
    sorted_files = sorted(dir_files.items(), key=lambda x: -x[1]["word_count"])

    # ==========================================
    # 第一部分：文件概要总览表
    # ==========================================
    lines.append("---")
    lines.append("")
    lines.append("## 📋 文件概要总览")
    lines.append("")
    lines.append("| # | 文件 | 规模 | 核心主题 | 关键词 |")
    lines.append("|:--:|:-----|:----:|:---------|:-------|")

    for i, (path, info) in enumerate(sorted_files, 1):
        fname = Path(path).name
        size_label = get_file_size_label(info["word_count"])
        # 从标题提取核心主题
        theme = info["headings"][0] if info["headings"] else info["name"]
        theme = theme[:25] + "..." if len(theme) > 25 else theme
        keywords = "、".join(info["keywords"][:5])
        link = f"[{info['name']}]({Path(path).name})"
        lines.append(f"| {i} | {link} | {size_label} | {theme} | {keywords} |")

    lines.append("")

    # ==========================================
    # 第二部分：各文件详细概要 + 关系
    # ==========================================
    lines.append("---")
    lines.append("")
    lines.append("## 📖 文件详情与关系图谱")
    lines.append("")

    for path, info in sorted_files:
        fname = Path(path).name
        size_label = get_file_size_label(info["word_count"])
        word_count = info["word_count"]

        lines.append(f"### 📄 {info['name']}")
        lines.append("")
        lines.append(f"- **规模**: {size_label}（约 {word_count:,} 字）")
        lines.append(f"- **路径**: `{path}`")
        lines.append("")

        # 概要
        lines.append("**📝 内容概要**")
        lines.append("")
        if info["summary"]:
            lines.append(f"> {info['summary']}")
        elif info["headings"]:
            # 从前 3 个二级标题推断内容
            h2_list = [h for h in info["headings"][:6]]
            if h2_list:
                lines.append("> 主要章节：" + " → ".join(h2_list))
            else:
                lines.append("> （待补充）")
        else:
            lines.append("> （待补充）")
        lines.append("")

        # 关键词
        if info["keywords"]:
            lines.append(f"**🔑 核心关键词**: {'、'.join(info['keywords'][:8])}")
            lines.append("")

        # 引用关系
        out_links = [l for l in info["internal_links"] if l in all_files]
        in_links = backlinks.get(path, [])

        if out_links or in_links:
            lines.append("**🔗 引用关系**")
            lines.append("")
            if out_links:
                out_names = [f"[{Path(l).name}](../{l})" for l in out_links[:8]]
                lines.append(f"- 📤 **引用了**（{len(out_links)}个）: {'、'.join(out_names)}")
            if in_links:
                in_names = [f"[{Path(l).name}](../{l})" for l in in_links[:8]]
                lines.append(f"- 📥 **被引用**（{len(in_links)}个）: {'、'.join(in_names)}")
            lines.append("")

        # 互补关系（同目录内相似度 0.25-0.55 的）
        comps = []
        for other_path, other_info in dir_files.items():
            if other_path == path:
                continue
            sim, common = get_similarity(info, other_info)
            if 0.25 <= sim <= 0.6:
                comps.append((other_path, sim, common))
        comps.sort(key=lambda x: -x[1])

        if comps:
            lines.append("**🤝 目录内互补/相关文件**")
            lines.append("")
            for other_path, sim, common in comps[:5]:
                other_name = Path(other_path).name
                common_str = "、".join(common[:4])
                lines.append(f"- [{other_name}]({other_name}) — 相似度 {sim:.0%}（共同主题：{common_str}）")
            lines.append("")

        # 跨目录相关（相似度高但不在同目录）
        cross = []
        for other_path, other_info in all_files.items():
            if other_path == path:
                continue
            if other_path in dir_files:
                continue
            sim, common = get_similarity(info, other_info)
            if sim >= 0.35:
                cross.append((other_path, sim, common))
        cross.sort(key=lambda x: -x[1])

        if cross:
            lines.append("**🌐 跨目录相关文件**")
            lines.append("")
            for other_path, sim, common in cross[:5]:
                other_name = Path(other_path).name
                other_dir = Path(other_path).parent.name
                common_str = "、".join(common[:4])
                lines.append(f"- [{other_name}](../{other_path}) — 相似度 {sim:.0%}（{other_dir}，共同：{common_str}）")
            lines.append("")

        lines.append("---")
        lines.append("")

    # ==========================================
    # 第三部分：重复/高度相似文件提示
    # ==========================================
    dupes = []
    file_list = list(dir_files.keys())
    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):
            p1, p2 = file_list[i], file_list[j]
            sim, common = get_similarity(dir_files[p1], dir_files[p2])
            if sim >= 0.6:
                dupes.append((p1, p2, sim, common))

    if dupes:
        lines.append("## ⚠️ 高度相似/可能重复的文件")
        lines.append("")
        lines.append("| 文件 A | 文件 B | 相似度 | 共同关键词 |")
        lines.append("|:-------|:-------|:------:|:-----------|")
        for p1, p2, sim, common in dupes:
            n1 = Path(p1).name
            n2 = Path(p2).name
            common_str = "、".join(common[:5])
            lines.append(f"| [{n1}]({p1}) | [{n2}]({p2}) | {sim:.0%} | {common_str} |")
        lines.append("")

    return "\n".join(lines)


def generate_root_index():
    """生成根目录 index.md 的知识图谱部分"""
    lines = []

    lines.append("---")
    lines.append("")
    lines.append("## 🕸️ 知识图谱总览")
    lines.append("")
    lines.append(f"> 基于 **{len(files)}** 个文件、**{len(dirs)}** 个目录的自动分析")
    lines.append("")

    # 总体统计
    total_words = sum(f["word_count"] for f in files.values())
    lines.append("### 📊 知识库规模")
    lines.append("")
    lines.append(f"- 📄 **总文件数**: {len(files)} 个")
    lines.append(f"- 📁 **总目录数**: {len(dirs)} 个")
    lines.append(f"- ✏️ **总字数**: 约 {total_words/10000:.1f} 万字")
    lines.append(f"")

    # 目录规模排行
    lines.append("### 📁 目录规模 Top 15")
    lines.append("")
    lines.append("| # | 目录 | 文件数 | 代表主题 |")
    lines.append("|:--:|:-----|:------:|:---------|")
    top_dirs = sorted(dirs.items(), key=lambda x: -len(x[1]))[:15]
    for i, (d, fs) in enumerate(top_dirs, 1):
        # 找最大文件的标题做代表
        max_f = max(fs, key=lambda x: files[x]["word_count"])
        rep_title = files[max_f]["headings"][0] if files[max_f]["headings"] else files[max_f]["name"]
        rep_title = rep_title[:20] + "..." if len(rep_title) > 20 else rep_title
        dir_link = f"[{d.split('/')[-1]}]({d}/index.md)"
        lines.append(f"| {i} | {dir_link} | {len(fs)} | {rep_title} |")
    lines.append("")

    # 核心枢纽文件（被引用最多）
    lines.append("### 🔗 核心枢纽文件（被引用最多 Top 20）")
    lines.append("")
    lines.append("| # | 文件 | 被引用次数 | 所属目录 | 核心主题 |")
    lines.append("|:--:|:-----|:----------:|:---------|:---------|")

    hub_files = sorted(backlinks.items(), key=lambda x: -len(x[1]))[:20]
    for i, (path, refs) in enumerate(hub_files, 1):
        info = files.get(path)
        if not info:
            continue
        title = info["headings"][0] if info["headings"] else info["name"]
        title = title[:20] + "..." if len(title) > 20 else title
        dir_name = info["dir"].split("/")[-1]
        link = f"[{info['name']}]({path})"
        lines.append(f"| {i} | {link} | {len(refs)} | {dir_name} | {title} |")
    lines.append("")

    # 高度重复的文件
    lines.append("### ⚠️ 高度相似/可能重复文件")
    lines.append("")
    all_dupes = []
    file_list = list(files.keys())
    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):
            p1, p2 = file_list[i], file_list[j]
            sim, common = get_similarity(files[p1], files[p2])
            if sim >= 0.65:
                all_dupes.append((p1, p2, sim, common))
    all_dupes.sort(key=lambda x: -x[2])

    if all_dupes:
        lines.append("| 文件 A | 文件 B | 相似度 | 共同主题 | 关系判断 |")
        lines.append("|:-------|:-------|:------:|:---------|:---------|")
        for p1, p2, sim, common in all_dupes[:15]:
            n1 = f"[{Path(p1).name}]({p1})"
            n2 = f"[{Path(p2).name}]({p2})"
            common_str = "、".join(common[:4])
            # 判断关系
            f1, f2 = files[p1], files[p2]
            if f1["dir"] == f2["dir"]:
                relation = "同目录重复"
            elif abs(f1["word_count"] - f2["word_count"]) / max(f1["word_count"], f2["word_count"]) > 0.5:
                relation = "详略版本"
            else:
                relation = "跨目录重复"
            lines.append(f"| {n1} | {n2} | {sim:.0%} | {common_str} | {relation} |")
        lines.append("")
    else:
        lines.append("（未发现高度重复文件）")
        lines.append("")

    # 跨目录强关联（相似度高但不同目录）
    lines.append("### 🌐 跨目录强关联对（Top 20）")
    lines.append("")
    lines.append("| 领域 A | 文件 A | 领域 B | 文件 B | 相似度 | 共同主题 |")
    lines.append("|:-------|:-----|:-------|:-----|:------:|:---------|")

    cross_pairs = []
    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):
            p1, p2 = file_list[i], file_list[j]
            f1, f2 = files[p1], files[p2]
            if f1["dir"] == f2["dir"]:
                continue
            sim, common = get_similarity(f1, f2)
            if sim >= 0.4:
                cross_pairs.append((p1, p2, sim, common))
    cross_pairs.sort(key=lambda x: -x[2])

    for p1, p2, sim, common in cross_pairs[:20]:
        f1, f2 = files[p1], files[p2]
        dir1 = f1["dir"].split("/")[-1]
        dir2 = f2["dir"].split("/")[-1]
        n1 = f"[{Path(p1).name}]({p1})"
        n2 = f"[{Path(p2).name}]({p2})"
        common_str = "、".join(common[:3])
        lines.append(f"| {dir1} | {n1} | {dir2} | {n2} | {sim:.0%} | {common_str} |")
    lines.append("")

    # 主题聚类（基于关键词）
    lines.append("### 🏷️ 核心主题领域")
    lines.append("")

    # 收集所有关键词并统计
    all_keywords = defaultdict(int)
    for f in files.values():
        for kw in f["keywords"]:
            all_keywords[kw] += 1
    top_keywords = sorted(all_keywords.items(), key=lambda x: -x[1])[:30]

    lines.append("| 主题关键词 | 出现文件数 | 代表文件 |")
    lines.append("|:-----------|:----------:|:---------|")
    for kw, count in top_keywords:
        # 找包含这个关键词的最大文件
        kw_files = [(p, f) for p, f in files.items() if kw in f["keywords"]]
        kw_files.sort(key=lambda x: -x[1]["word_count"])
        rep = kw_files[0] if kw_files else None
        if rep:
            rep_link = f"[{rep[1]['name']}]({rep[0]})"
            lines.append(f"| **{kw}** | {count} | {rep_link} |")
    lines.append("")

    return "\n".join(lines)


def main():
    print("📝 生成各目录 index.md...")

    # 为每个有文件的目录生成 index.md
    generated = 0
    for dir_path, dir_files in dirs.items():
        if not dir_files:
            continue
        content = generate_dir_index(dir_path, dir_files, files, backlinks)
        out_path = ROOT / dir_path / "index.md"

        # 读取原有内容，保留顶部，追加知识图谱
        try:
            existing = out_path.read_text(encoding="utf-8")
        except Exception:
            existing = ""

        # 检查是否已有知识图谱部分
        if "知识图谱" in existing and "文件详情与关系图谱" in existing:
            # 替换知识图谱部分
            parts = existing.split("## 📚")
            if len(parts) > 1:
                new_content = parts[0].rstrip() + "\n\n" + content
            else:
                new_content = existing.rstrip() + "\n\n---\n\n" + content
        else:
            new_content = existing.rstrip() + "\n\n---\n\n" + content

        out_path.write_text(new_content, encoding="utf-8")
        generated += 1
        print(f"   ✅ {dir_path}/index.md")

    print(f"\n✅ 已生成 {generated} 个目录的 index.md")

    # 生成根目录的知识图谱部分
    print("\n📝 生成根目录 index.md 知识图谱...")
    root_graph = generate_root_index()
    root_path = ROOT / "index.md"
    root_content = root_path.read_text(encoding="utf-8")

    # 检查是否已有知识图谱部分
    if "知识图谱总览" in root_content:
        # 替换从"知识图谱总览"开始的部分
        parts = root_content.split("## 🕸️ 知识图谱总览")
        if len(parts) > 1:
            new_root = parts[0].rstrip() + "\n\n" + root_graph
        else:
            new_root = root_content.rstrip() + "\n\n" + root_graph
    else:
        new_root = root_content.rstrip() + "\n\n" + root_graph

    root_path.write_text(new_root, encoding="utf-8")
    print("   ✅ 根目录 index.md 已更新")

    print("\n🎉 全部完成！")


if __name__ == "__main__":
    main()
