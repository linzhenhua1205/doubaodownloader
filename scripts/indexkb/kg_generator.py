#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库知识图谱生成器 (Knowledge Graph Generator)
==================================================

功能：
  - 扫描 knowledge 目录下所有文件（排除指定目录）
  - 提取每个文件的概要、关键词、内部链接
  - 分析文件间的引用关系、互补关系、重复关系
  - 为每个目录生成/更新 index.md 知识图谱
  - 生成根目录跨目录整合总览

用法：
  python kg_generator.py              # 完整生成（默认）
  python kg_generator.py --incremental # 增量更新（仅处理变化的文件）
  python kg_generator.py --verify     # 仅验证覆盖率
  python kg_generator.py --stats      # 仅显示统计信息
  python kg_generator.py --dir 02_rd  # 仅处理指定目录

配置：
  修改下方 CONFIG 字典即可调整参数。
"""

import os
import re
import sys
import json
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ============================================================
# 配置
# ============================================================

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT, relpath

CONFIG = {
    "knowledge_root": str(KNOWLEDGE_ROOT),
    
    "exclude_dirs": {"01_survey", "bak", "import-modules", "oldbak"},
    
    "exclude_files": {"index.md", "log.md", "README.md", "TRACKING.md"},
    
    # 相似度阈值
    "similarity": {
        "high": 0.60,       # ≥ 此值：高度相似/可能重复
        "medium": 0.35,     # ≥ 此值且 < high：强关联/互补
        "low": 0.25,        # ≥ 此值且 < medium：相关/同目录内互补
    },
    
    # 关键词提取
    "keywords": {
        "top_n_per_file": 10,
        "top_n_overview": 5,
    },
    
    # 文件规模分级（字数）
    "size_levels": {
        "giant": 10000,     # 📕 巨篇
        "long": 5000,       # 📗 长文
        "medium": 2000,     # 📘 中篇
        # 以下为 📙 短篇
    },
    
    # 展示限制
    "limits": {
        "top_dirs": 15,
        "top_hubs": 20,
        "top_keywords": 30,
        "top_cross_pairs": 20,
        "top_duplicates": 15,
        "similar_per_file": 6,
        "cross_per_file": 5,
        "high_sim_per_file": 3,
    },
    
    # 缓存文件
    "cache_file": "_kg_cache.json",
}


# ============================================================
# 工具函数
# ============================================================

def get_file_hash(filepath: Path) -> str:
    """计算文件 MD5 哈希，用于增量更新检测"""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def count_chinese_words(text: str) -> int:
    """估算中文字数（中文字符 + 英文单词）"""
    cn_chars = re.findall(r'[\u4e00-\u9fa5]', text)
    en_words = re.findall(r'[A-Za-z]+', text)
    return len(cn_chars) + len(en_words)


def get_size_label(word_count: int) -> str:
    """根据字数获取规模标签"""
    levels = CONFIG["size_levels"]
    if word_count >= levels["giant"]:
        return "📕 巨篇"
    elif word_count >= levels["long"]:
        return "📗 长文"
    elif word_count >= levels["medium"]:
        return "📘 中篇"
    else:
        return "📙 短篇"


# ============================================================
# 文本提取
# ============================================================

def extract_frontmatter(text: str) -> dict:
    """提取 YAML frontmatter"""
    if not text.startswith("---"):
        return {}
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip()
    return fm


def extract_headings(text: str, max_count: int = 6) -> list:
    """提取 Markdown 标题"""
    headings = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            if heading and heading not in headings:
                headings.append(heading)
                if len(headings) >= max_count:
                    break
    return headings


def extract_internal_links(text: str, current_path: str, all_files: set) -> list:
    """提取文件中的内部 .md 链接（已解析为绝对路径）"""
    links = []
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    current_dir = os.path.dirname(current_path)
    
    for match in re.finditer(pattern, text):
        link_path = match.group(2)
        if link_path.startswith(("http://", "https://", "#")):
            continue
        if not link_path.endswith(".md"):
            continue
        
        resolved = os.path.normpath(os.path.join(current_dir, link_path))
        resolved = resolved.replace("\\", "/")
        if resolved in all_files:
            links.append(resolved)
    
    return list(set(links))


# 中文停用词
_STOPWORDS = {
    "的", "是", "在", "和", "了", "与", "及", "等", "为", "对", "从", "到",
    "一个", "一种", "可以", "进行", "通过", "需要", "以及", "不同", "主要",
    "相关", "方法", "系统", "技术", "设计", "分析", "实现", "开发", "使用",
    "目录", "文件", "内容", "说明", "章节", "概述", "引言", "背景", "总结",
    "问题", "方案", "模式", "架构", "功能", "数据", "平台", "工具", "模型",
    "我们", "这个", "那个", "什么", "怎么", "为什么", "如何",
}


def extract_keywords(text: str, top_n: int = 10) -> list:
    """从标题和正文中提取关键词"""
    # 去掉 frontmatter
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    
    headings = extract_headings(body, 20)
    heading_text = " ".join(headings)
    
    # 标题中的词权重更高
    word_count = defaultdict(int)
    
    # 中文词组（2-6字）
    for w in re.findall(r'[\u4e00-\u9fa5]{2,6}', heading_text):
        word_count[w] += 2
    # 英文单词
    for w in re.findall(r'[A-Za-z][A-Za-z0-9_-]{2,}', heading_text):
        word_count[w] += 2
    
    # 正文前 30000 字符中的词
    for w in re.findall(r'[\u4e00-\u9fa5]{2,6}', body[:30000]):
        word_count[w] += 1
    
    # 过滤停用词并排序
    filtered = [(w, c) for w, c in word_count.items() 
                if w not in _STOPWORDS and len(w) >= 2]
    filtered.sort(key=lambda x: -x[1])
    
    return [w for w, c in filtered[:top_n]]


# ============================================================
# 相似度计算
# ============================================================

def calc_similarity(f1_keywords: list, f2_keywords: list) -> tuple:
    """基于关键词 Jaccard 相似度计算"""
    k1 = set(f1_keywords)
    k2 = set(f2_keywords)
    if not k1 or not k2:
        return 0.0, []
    overlap = k1 & k2
    union = k1 | k2
    sim = len(overlap) / len(union) if union else 0.0
    return round(sim, 2), list(overlap)[:6]


# ============================================================
# 扫描与分析
# ============================================================

def is_excluded(path: Path, root: Path) -> bool:
    """判断路径是否在排除列表中"""
    parts = path.relative_to(root).parts
    for part in parts:
        if part in CONFIG["exclude_dirs"]:
            return True
    if path.name in CONFIG["exclude_files"]:
        return True
    return False


def scan_files(root: Path, cache: dict = None) -> tuple:
    """
    扫描所有文件并提取信息。
    返回 (files_dict, changed_count)
    files_dict: {rel_path: file_info}
    """
    files = {}
    changed = 0
    count = 0
    
    print("  扫描文件中...")
    for md_file in root.rglob("*.md"):
        if is_excluded(md_file, root):
            continue
        
        count += 1
        rel_path = str(md_file.relative_to(root)).replace("\\", "/")
        
        # 增量更新：检查缓存
        if cache and rel_path in cache:
            cached = cache[rel_path]
            if cached.get("size") == md_file.stat().st_size:
                # 大小一致，用哈希验证
                if cached.get("hash") == get_file_hash(md_file):
                    files[rel_path] = cached["info"]
                    continue
        
        # 读取并分析
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"    警告: 无法读取 {rel_path}: {e}")
            continue
        
        word_count = count_chinese_words(text)
        headings = extract_headings(text)
        keywords = extract_keywords(text, CONFIG["keywords"]["top_n_per_file"])
        frontmatter = extract_frontmatter(text)
        
        file_info = {
            "path": rel_path,
            "name": md_file.stem,
            "size": len(text),
            "word_count": word_count,
            "frontmatter": frontmatter,
            "summary": headings[0] if headings else md_file.stem,
            "headings": headings,
            "keywords": keywords,
            "dir": os.path.dirname(rel_path),
            "internal_links_raw": [],  # 稍后填充
        }
        
        files[rel_path] = file_info
        changed += 1
        
        if count % 200 == 0:
            print(f"    已扫描 {count} 个文件...")
    
    print(f"    共扫描 {len(files)} 个文件 (新增/变更: {changed})")
    return files, changed


def build_directory_index(files: dict) -> dict:
    """按目录组织文件"""
    dirs = defaultdict(dict)
    for path, info in files.items():
        d = info["dir"]
        dirs[d][path] = info
    return dict(dirs)


def build_backlinks(files: dict) -> dict:
    """构建反向引用索引 {target_path: [source_paths]}"""
    backlinks = defaultdict(set)
    all_paths = set(files.keys())
    
    # 先填充所有文件的 internal_links
    for path, info in files.items():
        # 重新读取文件提取链接（因为 scan 阶段还没有 all_paths）
        # 优化：从 info 中已有的信息构建
        pass
    
    # 重新扫描链接（因为需要 all_paths 集合）
    root = Path(CONFIG["knowledge_root"])
    for path, info in files.items():
        full_path = root / path
        try:
            text = full_path.read_text(encoding="utf-8")
            links = extract_internal_links(text, path, all_paths)
            info["internal_links"] = links
            for target in links:
                backlinks[target].add(path)
        except:
            info["internal_links"] = []
    
    return {k: sorted(list(v)) for k, v in backlinks.items()}


# ============================================================
# 内容生成
# ============================================================

def generate_dir_graph(dir_path: str, dir_files: dict, all_files: dict, backlinks: dict) -> str:
    """生成单个目录的知识图谱内容"""
    lines = []
    parts = dir_path.split("/")
    dir_name = parts[-1] if dir_path and dir_path != "." else "根目录"
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"# 📚 {dir_name} 目录知识图谱")
    lines.append("")
    lines.append(f"> 📊 本目录共 **{len(dir_files)}** 个文件")
    lines.append("")
    
    sorted_files = sorted(dir_files.items(), key=lambda x: -x[1]["word_count"])
    sim_thresholds = CONFIG["similarity"]
    limits = CONFIG["limits"]
    
    # 第一部分：文件概要总览表
    lines.append("---")
    lines.append("")
    lines.append("## 📋 文件概要总览")
    lines.append("")
    lines.append("| # | 文件 | 规模 | 核心主题 | 关键词 |")
    lines.append("|:--:|:-----|:----:|:---------|:-------|")
    
    top_n = CONFIG["keywords"]["top_n_overview"]
    for i, (path, info) in enumerate(sorted_files, 1):
        size_label = get_size_label(info["word_count"])
        theme = info["headings"][0] if info["headings"] else info["name"]
        theme = theme[:25] + "..." if len(theme) > 25 else theme
        keywords = "、".join(info["keywords"][:top_n])
        fname = Path(path).name
        link = f"[{info['name']}]({fname})"
        lines.append(f"| {i} | {link} | {size_label} | {theme} | {keywords} |")
    
    lines.append("")
    
    # 第二部分：文件详情与关系图谱
    lines.append("---")
    lines.append("")
    lines.append("## 📖 文件详情与关系图谱")
    lines.append("")
    
    for path, info in sorted_files:
        fname = Path(path).name
        size_label = get_size_label(info["word_count"])
        
        lines.append(f"### 📄 {info['name']}")
        lines.append("")
        lines.append(f"- **规模**: {size_label}（约 {info['word_count']:,} 字）")
        lines.append(f"- **路径**: `{path}`")
        lines.append("")
        
        # 内容概要
        lines.append("**📝 内容概要**")
        lines.append("")
        if info["headings"]:
            summary_text = " → ".join(info["headings"][:4])
            lines.append(f"> 主要章节：{summary_text}")
        else:
            lines.append(f"> {info['summary']}")
        lines.append("")
        
        # 核心关键词
        if info["keywords"]:
            lines.append(f"**🔑 核心关键词**: {'、'.join(info['keywords'][:8])}")
            lines.append("")
        
        # 引用关系
        has_links = False
        internal_links = info.get("internal_links", [])
        if internal_links:
            has_links = True
            lines.append("**🔗 引用关系**")
            lines.append("")
            link_strs = [f"[{Path(l).name}](../{l})" for l in internal_links[:8]]
            more = f"（共{len(internal_links)}个）" if len(internal_links) > 8 else ""
            lines.append(f"- 📤 **引用了**{more}: {'、'.join(link_strs)}")
        
        if path in backlinks:
            bl = backlinks[path]
            if bl:
                if not has_links:
                    lines.append("**🔗 引用关系**")
                    lines.append("")
                    has_links = True
                # 按被引用次数排序
                bl_sorted = sorted(bl, key=lambda x: -len(backlinks.get(x, [])))
                link_strs = [f"[{Path(l).name}](../{l})" for l in bl_sorted[:8]]
                more = f"（共{len(bl)}个）" if len(bl) > 8 else ""
                lines.append(f"- 📥 **被引用**{more}: {'、'.join(link_strs)}")
        
        if has_links:
            lines.append("")
        
        # 目录内互补/相关文件
        similar_in_dir = []
        for other_path, other_info in dir_files.items():
            if other_path == path:
                continue
            sim, overlap = calc_similarity(info["keywords"], other_info["keywords"])
            if sim_thresholds["low"] <= sim < sim_thresholds["high"]:
                similar_in_dir.append((other_path, sim, overlap))
        
        similar_in_dir.sort(key=lambda x: -x[1])
        
        if similar_in_dir:
            lines.append("**🤝 目录内互补/相关文件**")
            lines.append("")
            for other_path, sim, overlap in similar_in_dir[:limits["similar_per_file"]]:
                oname = Path(other_path).name
                lines.append(f"- [{oname}]({oname}) — 相似度 {int(sim*100)}%（共同主题：{'、'.join(overlap)}）")
            lines.append("")
        
        # 跨目录相关文件
        cross_dir_similar = []
        for other_path, other_info in all_files.items():
            if other_path == path:
                continue
            if other_info["dir"] == info["dir"]:
                continue
            sim, overlap = calc_similarity(info["keywords"], other_info["keywords"])
            if sim >= sim_thresholds["medium"]:
                cross_dir_similar.append((other_path, sim, overlap))
        
        cross_dir_similar.sort(key=lambda x: -x[1])
        
        if cross_dir_similar:
            lines.append("**🌐 跨目录相关文件**")
            lines.append("")
            for other_path, sim, overlap in cross_dir_similar[:limits["cross_per_file"]]:
                oname = Path(other_path).name
                lines.append(f"- [{oname}](../{other_path}) — 相似度 {int(sim*100)}%（共同主题：{'、'.join(overlap)}）")
            lines.append("")
        
        # 高度相似/重复预警
        high_similar = []
        for other_path, other_info in dir_files.items():
            if other_path == path:
                continue
            sim, overlap = calc_similarity(info["keywords"], other_info["keywords"])
            if sim >= sim_thresholds["high"]:
                high_similar.append((other_path, sim, overlap))
        
        if high_similar:
            lines.append("**⚠️ 高度相似/可能重复**")
            lines.append("")
            for other_path, sim, overlap in high_similar[:limits["high_sim_per_file"]]:
                oname = Path(other_path).name
                lines.append(f"- [{oname}]({oname}) — 相似度 {int(sim*100)}%（共同主题：{'、'.join(overlap)}）")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 第三部分：高度重复文件汇总
    high_sim_pairs = []
    file_paths = list(dir_files.keys())
    for i in range(len(file_paths)):
        for j in range(i+1, len(file_paths)):
            p1, p2 = file_paths[i], file_paths[j]
            sim, overlap = calc_similarity(
                dir_files[p1]["keywords"], dir_files[p2]["keywords"])
            if sim >= sim_thresholds["high"]:
                high_sim_pairs.append((p1, p2, sim, overlap))
    
    if high_sim_pairs:
        high_sim_pairs.sort(key=lambda x: -x[2])
        lines.append("## ⚠️ 高度重复文件预警")
        lines.append("")
        lines.append("| 文件 A | 文件 B | 相似度 | 共同关键词 |")
        lines.append("|:-------|:-------|:------:|:-----------|")
        for p1, p2, sim, overlap in high_sim_pairs[:10]:
            n1 = Path(p1).name
            n2 = Path(p2).name
            lines.append(f"| [{n1}]({n1}) | [{n2}]({n2}) | {int(sim*100)}% | {'、'.join(overlap[:4])} |")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def generate_root_overview(files: dict, backlinks: dict) -> str:
    """生成根目录跨目录知识图谱总览"""
    lines = []
    
    total_files = len(files)
    total_dirs = len(set(info["dir"] for info in files.values()))
    total_words = sum(info["word_count"] for info in files.values())
    limits = CONFIG["limits"]
    sim_thresholds = CONFIG["similarity"]
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🕸️ 知识图谱总览")
    lines.append("")
    lines.append(f"> 基于 **{total_files}** 个文件、**{total_dirs}** 个目录的自动分析")
    lines.append("")
    
    # 知识库规模
    lines.append("### 📊 知识库规模")
    lines.append("")
    lines.append(f"- 📄 **总文件数**: {total_files} 个")
    lines.append(f"- 📁 **总目录数**: {total_dirs} 个")
    lines.append(f"- ✏️ **总字数**: 约 {total_words/10000:.1f} 万字")
    lines.append(f"- 🔗 **有引用关系的文件**: {len(backlinks)} 个")
    lines.append("")
    
    # 目录规模 Top N
    dir_file_counts = defaultdict(int)
    dir_representative = {}
    for path, info in files.items():
        d = info["dir"]
        dir_file_counts[d] += 1
        if d not in dir_representative or info["word_count"] > dir_representative[d]["word_count"]:
            dir_representative[d] = info
    
    top_dirs = sorted(dir_file_counts.items(), key=lambda x: -x[1])[:limits["top_dirs"]]
    
    lines.append(f"### 📁 目录规模 Top {limits['top_dirs']}")
    lines.append("")
    lines.append("| # | 目录 | 文件数 | 代表主题 |")
    lines.append("|:--:|:-----|:------:|:---------|")
    for i, (d, count) in enumerate(top_dirs, 1):
        rep = dir_representative[d]
        theme = rep["headings"][0] if rep["headings"] else rep["name"]
        theme = theme[:25] + "..." if len(theme) > 25 else theme
        dir_link = f"[{d.split('/')[-1]}]({d}/index.md)"
        lines.append(f"| {i} | {dir_link} | {count} | {theme} |")
    lines.append("")
    
    # 核心枢纽文件 Top N
    hub_files = []
    for path, bl in backlinks.items():
        if path in files:
            hub_files.append((path, len(bl), files[path]))
    
    hub_files.sort(key=lambda x: -x[1])
    top_hubs = hub_files[:limits["top_hubs"]]
    
    lines.append(f"### 🔗 核心枢纽文件 Top {limits['top_hubs']}")
    lines.append("")
    lines.append("| # | 文件 | 被引用次数 | 所属目录 |")
    lines.append("|:--:|:-----|:----------:|:---------|")
    for i, (path, count, info) in enumerate(top_hubs, 1):
        name = info["name"]
        d = info["dir"]
        lines.append(f"| {i} | [{name}]({path}) | {count} | {d} |")
    lines.append("")
    
    # 跨目录高度相似文件
    print("  计算跨目录相似度...")
    cross_high_sim = []
    file_list = list(files.keys())
    
    for i in range(len(file_list)):
        p1 = file_list[i]
        f1 = files[p1]
        for j in range(i+1, len(file_list)):
            p2 = file_list[j]
            f2 = files[p2]
            if f1["dir"] == f2["dir"]:
                continue
            sim, overlap = calc_similarity(f1["keywords"], f2["keywords"])
            if sim >= 0.5:
                cross_high_sim.append((p1, p2, sim, overlap))
    
    cross_high_sim.sort(key=lambda x: -x[2])
    
    lines.append(f"### ⚠️ 高度相似/可能重复文件（跨目录 Top {limits['top_duplicates']}）")
    lines.append("")
    lines.append("| 相似度 | 文件 A | 文件 B | 关系判断 |")
    lines.append("|:------:|:-------|:-------|:---------|")
    
    for p1, p2, sim, overlap in cross_high_sim[:limits["top_duplicates"]]:
        n1 = Path(p1).name
        n2 = Path(p2).name
        if sim >= 0.7:
            relation = "🔴 高度重复"
        elif sim >= 0.6:
            relation = "🟡 内容重叠较多"
        else:
            relation = "🟢 主题相关互补"
        lines.append(f"| {int(sim*100)}% | [{n1}]({p1}) | [{n2}]({p2}) | {relation} |")
    lines.append("")
    
    # 跨目录强关联对
    cross_pairs = [(p1, p2, s, o) for p1, p2, s, o in cross_high_sim if s >= sim_thresholds["medium"]]
    if not cross_pairs:
        cross_pairs = cross_high_sim[:limits["top_cross_pairs"]]
    cross_pairs.sort(key=lambda x: -x[2])
    
    lines.append(f"### 🤝 跨目录强关联对 Top {limits['top_cross_pairs']}")
    lines.append("")
    lines.append("| 相似度 | 文件 A | 文件 B | 共同主题 |")
    lines.append("|:------:|:-------|:-------|:---------|")
    
    for p1, p2, sim, overlap in cross_pairs[:limits["top_cross_pairs"]]:
        n1 = Path(p1).name
        n2 = Path(p2).name
        common = "、".join(overlap[:4])
        lines.append(f"| {int(sim*100)}% | [{n1}]({p1}) | [{n2}]({p2}) | {common} |")
    lines.append("")
    
    # 核心主题领域 Top N
    all_keywords = defaultdict(int)
    keyword_files = defaultdict(list)
    for path, info in files.items():
        for kw in info["keywords"][:5]:
            all_keywords[kw] += 1
            if len(keyword_files[kw]) < 3:
                keyword_files[kw].append(path)
    
    top_keywords = sorted(all_keywords.items(), key=lambda x: -x[1])[:limits["top_keywords"]]
    
    lines.append(f"### 🏷️ 核心主题领域 Top {limits['top_keywords']}")
    lines.append("")
    lines.append("| # | 关键词 | 出现文件数 | 代表文件 |")
    lines.append("|:--:|:-------|:----------:|:---------|")
    for i, (kw, count) in enumerate(top_keywords, 1):
        rep_links = []
        for rp in keyword_files[kw][:2]:
            rn = Path(rp).name
            rep_links.append(f"[{rn}]({rp})")
        lines.append(f"| {i} | **{kw}** | {count} | {'、'.join(rep_links)} |")
    lines.append("")
    
    # 主题聚类概览
    lines.append("### 🗂️ 主题聚类概览")
    lines.append("")
    
    clusters = {
        "🏗️ 硬件架构与设计": ["服务器", "架构", "硬件", "PCB", "单板", "结构", "散热", "供电", "信号", "EMC"],
        "🤖 AI 与大模型": ["大模型", "LLM", "AI", "Agent", "GPT", "训练", "推理", "Transformer", "MoE", "RAG"],
        "💻 软件与系统": ["Linux", "内核", "OS", "分布式", "云原生", "K8s", "BMC", "OpenBMC", "固件", "驱动"],
        "🔌 互联与网络": ["PCIe", "互连", "网络", "以太网", "CXL", "NVLink", "SerDes", "I2C", "SPI"],
        "💾 存储与内存": ["存储", "SSD", "DDR", "HBM", "内存", "NAND", "KV-Cache", "CXL"],
        "📊 管理与方法论": ["管理", "项目", "研发", "IPD", "流程", "质量", "可靠性", "方法论", "决策"],
        "🔬 芯片与半导体": ["芯片", "GPU", "CPU", "NVIDIA", "AMD", "制程", "封装", "RISC-V"],
        "🏭 供应链与制造": ["供应链", "生产", "制造", "BOM", "成本", "国产", "替代", "工艺"],
    }
    
    for cluster_name, cluster_kws in clusters.items():
        cluster_set = set()
        for path, info in files.items():
            for kw in info["keywords"]:
                if kw in cluster_kws:
                    cluster_set.add(path)
                    break
        lines.append(f"- **{cluster_name}**: ~{len(cluster_set)} 个文件")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


# ============================================================
# 主流程
# ============================================================

def write_index_graph(root: Path, dir_path: str, graph_content: str) -> bool:
    """写入目录 index.md 的知识图谱部分"""
    index_path = root / dir_path / "index.md"
    
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        # 移除旧的知识图谱（可能有多次重复追加的历史版本）
        if "## 📖 文件详情与关系图谱" in content:
            # 查找所有 "# 📚 " 出现的位置
            positions = []
            start = 0
            while True:
                pos = content.find("# 📚 ", start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            # 第 1 个是索引标题，第 2 个起是知识图谱（可能重复多次）
            if len(positions) >= 2:
                content = content[:positions[1]].rstrip()
            elif len(positions) == 1 and positions[0] > 0:
                content = content[:positions[0]].rstrip()
        # 移除末尾多余的 ---
        content = content.rstrip()
        while content.endswith("---"):
            content = content[:-3].rstrip()
        content = content.rstrip()
        # 追加知识图谱
        content += "\n\n---\n"
        # graph_content 开头也有 ---，所以去掉第一个
        graph_to_append = graph_content.lstrip("\n")
        if graph_to_append.startswith("---"):
            graph_to_append = graph_to_append[3:].lstrip("\n")
        content += graph_to_append
    else:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        dir_name = dir_path.split("/")[-1]
        content = f"# 📚 {dir_name} 目录索引\n\n> **文件数**: 详见下方知识图谱\n"
        content += graph_content
    
    index_path.write_text(content, encoding="utf-8")
    return True


def write_root_overview(root: Path, overview_content: str):
    """写入根目录知识图谱总览"""
    index_path = root / "index.md"
    content = index_path.read_text(encoding="utf-8")
    
    # 移除旧的总览
    if "## 🕸️ 知识图谱总览" in content:
        idx = content.find("## 🕸️ 知识图谱总览")
        content = content[:idx].rstrip()
    
    # 移除末尾多余的 ---
    content = content.rstrip()
    while content.endswith("---"):
        content = content[:-3].rstrip()
    content = content.rstrip()
    
    # 追加总览
    content += "\n\n---\n"
    # overview_content 开头也有 ---，所以去掉第一个
    overview_to_append = overview_content.lstrip("\n")
    if overview_to_append.startswith("---"):
        overview_to_append = overview_to_append[3:].lstrip("\n")
    content += overview_to_append
    
    index_path.write_text(content, encoding="utf-8")


def load_cache(cache_path: Path) -> dict:
    """加载缓存"""
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_cache(cache_path: Path, files: dict):
    """保存缓存"""
    cache = {}
    root = Path(CONFIG["knowledge_root"])
    for path, info in files.items():
        full_path = root / path
        try:
            cache[path] = {
                "size": full_path.stat().st_size,
                "hash": get_file_hash(full_path),
                "info": info,
            }
        except:
            pass
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)


def verify_coverage(root: Path) -> dict:
    """验证知识图谱覆盖率"""
    dirs_with_content = set()
    dirs_with_graph = set()
    
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        if rel == ".":
            continue
        
        # 检查是否排除
        excluded = False
        for part in Path(rel).parts:
            if part in CONFIG["exclude_dirs"]:
                excluded = True
                break
        if excluded:
            continue
        
        md_files = [f for f in filenames 
                    if f.endswith(".md") and f not in CONFIG["exclude_files"]]
        if not md_files:
            continue
        
        dirs_with_content.add(rel)
        
        if "index.md" in filenames:
            idx_path = os.path.join(dirpath, "index.md")
            with open(idx_path, "r", encoding="utf-8") as f:
                if "文件详情与关系图谱" in f.read():
                    dirs_with_graph.add(rel)
    
    return {
        "total": len(dirs_with_content),
        "covered": len(dirs_with_graph),
        "missing": dirs_with_content - dirs_with_graph,
        "coverage": len(dirs_with_graph) / len(dirs_with_content) * 100 if dirs_with_content else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="知识库知识图谱生成器")
    parser.add_argument("--incremental", "-i", action="store_true", help="增量更新模式")
    parser.add_argument("--verify", "-v", action="store_true", help="仅验证覆盖率")
    parser.add_argument("--stats", "-s", action="store_true", help="仅显示统计信息")
    parser.add_argument("--dir", "-d", type=str, help="仅处理指定目录")
    parser.add_argument("--no-cache", action="store_true", help="不使用缓存")
    args = parser.parse_args()
    
    root = Path(CONFIG["knowledge_root"])
    cache_path = root / CONFIG["cache_file"]
    
    print("=" * 60)
    print("📚 知识库知识图谱生成器")
    print("=" * 60)
    print(f"📁 知识根目录: {root}")
    print(f"🚫 排除目录: {', '.join(CONFIG['exclude_dirs'])}")
    print()
    
    # 验证模式
    if args.verify:
        print("【验证模式】")
        result = verify_coverage(root)
        print(f"  有内容的目录: {result['total']}")
        print(f"  有知识图谱: {result['covered']}")
        print(f"  覆盖率: {result['coverage']:.1f}%")
        if result["missing"]:
            print(f"\n  缺失的目录 ({len(result['missing'])}):")
            for d in sorted(result["missing"]):
                print(f"    - {d}")
        return
    
    # 统计模式
    if args.stats:
        print("【统计模式】")
        cache = load_cache(cache_path)
        if cache:
            print(f"  缓存文件数: {len(cache)}")
            total_words = sum(v["info"]["word_count"] for v in cache.values())
            print(f"  总字数: {total_words/10000:.1f} 万字")
        else:
            print("  无缓存，请先运行生成")
        return
    
    # 生成模式
    mode = "增量更新" if args.incremental else "完整生成"
    print(f"【{mode}模式】")
    print()
    
    # 加载缓存
    cache = {}
    if args.incremental and not args.no_cache:
        cache = load_cache(cache_path)
        print(f"  已加载缓存: {len(cache)} 个文件")
    
    # 1. 扫描文件
    print("【1/4】扫描文件并提取信息")
    files, changed = scan_files(root, cache if args.incremental else None)
    print()
    
    # 指定目录过滤
    if args.dir:
        target = args.dir.strip("/")
        files = {p: i for p, i in files.items() if p.startswith(target + "/") or p.startswith(target + "\\")}
        print(f"  过滤后文件数: {len(files)} (目录: {target})")
        print()
    
    # 2. 构建索引
    print("【2/4】构建目录索引和引用关系")
    dirs = build_directory_index(files)
    backlinks = build_backlinks(files)
    print(f"  目录数: {len(dirs)}")
    print(f"  有反向引用的文件数: {len(backlinks)}")
    print()
    
    # 3. 生成各目录知识图谱
    print("【3/4】生成各目录知识图谱")
    updated = 0
    created = 0
    
    for dir_path in sorted(dirs.keys()):
        dir_files = dirs[dir_path]
        if not dir_files:
            continue
        
        graph_content = generate_dir_graph(dir_path, dir_files, files, backlinks)
        index_path = root / dir_path / "index.md"
        
        if index_path.exists():
            updated += 1
        else:
            created += 1
        
        write_index_graph(root, dir_path, graph_content)
        
        if (updated + created) % 20 == 0:
            print(f"    已处理 {updated + created}/{len(dirs)} 个目录...")
    
    print(f"  更新 index.md: {updated} 个")
    print(f"  新建 index.md: {created} 个")
    print()
    
    # 4. 更新根目录总览
    if not args.dir:  # 仅在完整生成时更新根目录
        print("【4/4】更新根目录知识图谱总览（跨目录整合）")
        overview = generate_root_overview(files, backlinks)
        write_root_overview(root, overview)
        print("  ✓ 根目录 index.md 已更新")
    else:
        print("【4/4】跳过根目录总览（单目录模式）")
    print()
    
    # 保存缓存
    if not args.no_cache and not args.dir:
        print("💾 保存缓存...")
        save_cache(cache_path, files)
        print(f"  ✓ 缓存已保存到 {CONFIG['cache_file']}")
        print()
    
    # 验证
    print("🔍 验证覆盖率...")
    result = verify_coverage(root)
    print(f"  覆盖率: {result['coverage']:.1f}% ({result['covered']}/{result['total']})")
    if result["missing"]:
        print(f"  ⚠️  缺失 {len(result['missing'])} 个目录")
    print()
    
    print("=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print(f"\n📊 总文件数: {len(files)}")
    print(f"📁 总目录数: {len(dirs)}")
    total_words = sum(i["word_count"] for i in files.values())
    print(f"✏️  总字数: {total_words/10000:.1f} 万字")
    print(f"🔗 有引用关系: {len(backlinks)} 个文件")


if __name__ == "__main__":
    main()
