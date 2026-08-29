#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库知识图谱完整生成脚本
- 扫描所有文件，提取概要、关键词、引用关系
- 为每个目录的 index.md 追加知识图谱
- 更新根目录知识图谱总览
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"h:\github\cowkb\knowledge")

EXCLUDE_DIRS = {"01_survey", "bak", "import-modules"}
EXCLUDE_FILES = {"index.md", "log.md", "README.md", "TRACKING.md"}


def is_excluded(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    if path.name in EXCLUDE_FILES:
        return True
    return False


def extract_frontmatter(text: str) -> dict:
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


def extract_internal_links(text: str, current_path: str) -> list:
    links = []
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(pattern, text):
        link_path = match.group(2)
        if link_path.startswith("http://") or link_path.startswith("https://"):
            continue
        if link_path.startswith("#"):
            continue
        if not link_path.endswith(".md"):
            continue
        current_dir = os.path.dirname(current_path)
        resolved = os.path.normpath(os.path.join(current_dir, link_path))
        resolved = resolved.replace("\\", "/")
        links.append(resolved)
    return list(set(links))


def extract_keywords(text: str, top_n: int = 10) -> list:
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    headings = extract_headings(body, 20)
    heading_text = " ".join(headings)
    
    cn_words = re.findall(r'[\u4e00-\u9fa5]{2,6}', heading_text)
    en_words = re.findall(r'[A-Za-z][A-Za-z0-9_-]{2,}', heading_text)
    
    word_count = defaultdict(int)
    for w in cn_words:
        word_count[w] += 2
    for w in en_words:
        word_count[w] += 2
    
    body_cn = re.findall(r'[\u4e00-\u9fa5]{2,6}', body[:30000])
    for w in body_cn[:300]:
        word_count[w] += 1
    
    stopwords = {"的", "是", "在", "和", "了", "与", "及", "等", "为", "对", "从", "到",
                 "一个", "一种", "可以", "进行", "通过", "需要", "以及", "不同", "主要",
                 "相关", "方法", "系统", "技术", "设计", "分析", "实现", "开发", "使用",
                 "目录", "文件", "内容", "说明", "章节", "概述", "引言", "背景", "总结",
                 "问题", "方案", "模式", "架构", "功能", "数据", "平台", "工具", "模型"}
    
    filtered = [(w, c) for w, c in word_count.items() if w not in stopwords and len(w) >= 2]
    filtered.sort(key=lambda x: -x[1])
    
    return [w for w, c in filtered[:top_n]]


def count_chinese_words(text: str) -> int:
    cn_chars = re.findall(r'[\u4e00-\u9fa5]', text)
    en_words = re.findall(r'[A-Za-z]+', text)
    return len(cn_chars) + len(en_words)


def get_file_size_label(word_count):
    if word_count >= 10000:
        return "📕 巨篇"
    elif word_count >= 5000:
        return "📗 长文"
    elif word_count >= 2000:
        return "📘 中篇"
    else:
        return "📙 短篇"


def get_similarity(f1, f2):
    k1 = set(f1["keywords"])
    k2 = set(f2["keywords"])
    if not k1 or not k2:
        return 0, []
    overlap = k1 & k2
    union = k1 | k2
    sim = len(overlap) / len(union) if union else 0
    return sim, list(overlap)[:6]


def scan_files():
    print("  扫描文件中...")
    files = {}
    count = 0
    for md_file in ROOT.rglob("*.md"):
        if is_excluded(md_file):
            continue
        count += 1
        if count % 100 == 0:
            print(f"    已扫描 {count} 个文件...")
        
        rel_path = str(md_file.relative_to(ROOT)).replace("\\", "/")
        try:
            text = md_file.read_text(encoding="utf-8")
        except:
            continue
        
        word_count = count_chinese_words(text)
        headings = extract_headings(text)
        keywords = extract_keywords(text)
        internal_links = extract_internal_links(text, rel_path)
        frontmatter = extract_frontmatter(text)
        
        summary = headings[0] if headings else md_file.stem
        
        files[rel_path] = {
            "path": rel_path,
            "name": md_file.stem,
            "size": len(text),
            "word_count": word_count,
            "frontmatter": frontmatter,
            "summary": summary,
            "headings": headings,
            "internal_links": internal_links,
            "keywords": keywords,
            "dir": os.path.dirname(rel_path)
        }
    
    print(f"    共扫描 {len(files)} 个文件")
    return files


def build_directories(files):
    dirs = defaultdict(dict)
    for path, info in files.items():
        d = info["dir"]
        dirs[d][path] = info
    return dict(dirs)


def build_backlinks(files):
    backlinks = defaultdict(set)
    for path, info in files.items():
        for link in info["internal_links"]:
            if link in files:
                backlinks[link].add(path)
    return {k: list(v) for k, v in backlinks.items()}


def generate_dir_graph(dir_path, dir_files, all_files, backlinks):
    """生成一个目录的知识图谱内容"""
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
    
    # 第一部分：文件概要总览表
    lines.append("---")
    lines.append("")
    lines.append("## 📋 文件概要总览")
    lines.append("")
    lines.append("| # | 文件 | 规模 | 核心主题 | 关键词 |")
    lines.append("|:--:|:-----|:----:|:---------|:-------|")
    
    for i, (path, info) in enumerate(sorted_files, 1):
        size_label = get_file_size_label(info["word_count"])
        theme = info["headings"][0] if info["headings"] else info["name"]
        theme = theme[:25] + "..." if len(theme) > 25 else theme
        keywords = "、".join(info["keywords"][:5])
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
        size_label = get_file_size_label(info["word_count"])
        
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
        
        # 出站引用
        out_links = [l for l in info["internal_links"] if l in all_files]
        if out_links:
            if not has_links:
                lines.append("**🔗 引用关系**")
                lines.append("")
                has_links = True
            link_strs = []
            for l in out_links[:8]:
                lname = Path(l).name
                link_strs.append(f"[{lname}](../{l})")
            more = f"（共{len(out_links)}个）" if len(out_links) > 8 else ""
            lines.append(f"- 📤 **引用了**{more}: {'、'.join(link_strs)}")
        
        # 入站引用（被引用）
        if path in backlinks:
            bl = backlinks[path]
            if bl:
                if not has_links:
                    lines.append("**🔗 引用关系**")
                    lines.append("")
                    has_links = True
                link_strs = []
                for l in sorted(bl, key=lambda x: -len(backlinks.get(x, [])))[:8]:
                    lname = Path(l).name
                    link_strs.append(f"[{lname}](../{l})")
                more = f"（共{len(bl)}个）" if len(bl) > 8 else ""
                lines.append(f"- 📥 **被引用**{more}: {'、'.join(link_strs)}")
        
        if has_links:
            lines.append("")
        
        # 目录内互补/相关文件
        similar_in_dir = []
        for other_path, other_info in dir_files.items():
            if other_path == path:
                continue
            sim, overlap = get_similarity(info, other_info)
            if 0.25 <= sim < 0.6:
                similar_in_dir.append((other_path, sim, overlap))
        
        similar_in_dir.sort(key=lambda x: -x[1])
        
        if similar_in_dir:
            lines.append("**🤝 目录内互补/相关文件**")
            lines.append("")
            for other_path, sim, overlap in similar_in_dir[:6]:
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
            sim, overlap = get_similarity(info, other_info)
            if sim >= 0.35:
                cross_dir_similar.append((other_path, sim, overlap))
        
        cross_dir_similar.sort(key=lambda x: -x[1])
        
        if cross_dir_similar:
            lines.append("**🌐 跨目录相关文件**")
            lines.append("")
            for other_path, sim, overlap in cross_dir_similar[:5]:
                oname = Path(other_path).name
                lines.append(f"- [{oname}](../{other_path}) — 相似度 {int(sim*100)}%（共同主题：{'、'.join(overlap)}）")
            lines.append("")
        
        # 高度相似/重复预警
        high_similar = []
        for other_path, other_info in dir_files.items():
            if other_path == path:
                continue
            sim, overlap = get_similarity(info, other_info)
            if sim >= 0.6:
                high_similar.append((other_path, sim, overlap))
        
        if high_similar:
            lines.append("**⚠️ 高度相似/可能重复**")
            lines.append("")
            for other_path, sim, overlap in high_similar[:3]:
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
            sim, overlap = get_similarity(dir_files[p1], dir_files[p2])
            if sim >= 0.6:
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


def generate_root_overview(files, backlinks):
    """生成根目录知识图谱总览"""
    lines = []
    
    total_files = len(files)
    total_dirs = len(set(info["dir"] for info in files.values()))
    total_words = sum(info["word_count"] for info in files.values())
    
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
    
    # 目录规模 Top 15
    dir_file_counts = defaultdict(int)
    dir_representative = {}
    for path, info in files.items():
        d = info["dir"]
        dir_file_counts[d] += 1
        if d not in dir_representative or info["word_count"] > dir_representative[d]["word_count"]:
            dir_representative[d] = info
    
    top_dirs = sorted(dir_file_counts.items(), key=lambda x: -x[1])[:15]
    
    lines.append("### 📁 目录规模 Top 15")
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
    
    # 核心枢纽文件 Top 20
    hub_files = []
    for path, bl in backlinks.items():
        if path in files:
            hub_files.append((path, len(bl), files[path]))
    
    hub_files.sort(key=lambda x: -x[1])
    top_hubs = hub_files[:20]
    
    lines.append("### 🔗 核心枢纽文件 Top 20")
    lines.append("")
    lines.append("| # | 文件 | 被引用次数 | 所属目录 |")
    lines.append("|:--:|:-----|:----------:|:---------|")
    for i, (path, count, info) in enumerate(top_hubs, 1):
        name = info["name"]
        d = info["dir"]
        lines.append(f"| {i} | [{name}]({path}) | {count} | {d} |")
    lines.append("")
    
    # 高度相似/重复文件（跨目录）
    print("  计算跨目录相似度...")
    all_pairs = []
    file_list = list(files.keys())
    total_pairs = len(file_list) * (len(file_list) - 1) // 2
    processed = 0
    
    for i in range(len(file_list)):
        for j in range(i+1, len(file_list)):
            p1, p2 = file_list[i], file_list[j]
            f1, f2 = files[p1], files[p2]
            if f1["dir"] == f2["dir"]:
                continue
            sim, overlap = get_similarity(f1, f2)
            if sim >= 0.5:
                all_pairs.append((p1, p2, sim, overlap))
            processed += 1
    
    all_pairs.sort(key=lambda x: -x[2])
    
    lines.append("### ⚠️ 高度相似/可能重复文件（跨目录 Top 15）")
    lines.append("")
    lines.append("| 相似度 | 文件 A | 文件 B | 关系判断 |")
    lines.append("|:------:|:-------|:-------|:---------|")
    
    for p1, p2, sim, overlap in all_pairs[:15]:
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
    
    # 跨目录强关联对 Top 20
    cross_pairs = [(p1, p2, sim, overlap) for p1, p2, sim, overlap in all_pairs if sim >= 0.4]
    if not cross_pairs:
        cross_pairs = all_pairs[:20]
    cross_pairs.sort(key=lambda x: -x[2])
    
    lines.append("### 🤝 跨目录强关联对 Top 20")
    lines.append("")
    lines.append("| 相似度 | 文件 A | 文件 B | 共同主题 |")
    lines.append("|:------:|:-------|:-------|:---------|")
    
    for p1, p2, sim, overlap in cross_pairs[:20]:
        n1 = Path(p1).name
        n2 = Path(p2).name
        common = "、".join(overlap[:4])
        lines.append(f"| {int(sim*100)}% | [{n1}]({p1}) | [{n2}]({p2}) | {common} |")
    lines.append("")
    
    # 核心主题领域 Top 30
    all_keywords = defaultdict(int)
    keyword_files = defaultdict(list)
    for path, info in files.items():
        for kw in info["keywords"][:5]:
            all_keywords[kw] += 1
            if len(keyword_files[kw]) < 3:
                keyword_files[kw].append(path)
    
    top_keywords = sorted(all_keywords.items(), key=lambda x: -x[1])[:30]
    
    lines.append("### 🏷️ 核心主题领域 Top 30")
    lines.append("")
    lines.append("| # | 关键词 | 出现文件数 | 代表文件 |")
    lines.append("|:--:|:-------|:----------:|:---------|")
    for i, (kw, count) in enumerate(top_keywords, 1):
        rep_files = keyword_files[kw]
        rep_links = []
        for rp in rep_files[:2]:
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
        cluster_file_set = set()
        for path, info in files.items():
            for kw in info["keywords"]:
                if kw in cluster_kws:
                    cluster_file_set.add(path)
                    break
        lines.append(f"- **{cluster_name}**: ~{len(cluster_file_set)} 个文件")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("知识库知识图谱完整生成")
    print("=" * 60)
    print()
    
    # 1. 扫描文件
    print("【1/4】扫描文件并提取信息")
    files = scan_files()
    print()
    
    # 2. 构建目录和反向引用
    print("【2/4】构建目录索引和引用关系")
    dirs = build_directories(files)
    backlinks = build_backlinks(files)
    print(f"  目录数: {len(dirs)}")
    print(f"  有反向引用的文件数: {len(backlinks)}")
    print()
    
    # 3. 为每个目录生成知识图谱
    print("【3/4】为各目录生成知识图谱")
    updated = 0
    created = 0
    skipped = 0
    
    for dir_path in sorted(dirs.keys()):
        dir_files = dirs[dir_path]
        if not dir_files:
            continue
        
        index_path = ROOT / dir_path / "index.md"
        graph_content = generate_dir_graph(dir_path, dir_files, files, backlinks)
        
        if index_path.exists():
            # 读取现有内容
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 如果已有知识图谱，先删除旧的
            if "## 📖 文件详情与关系图谱" in content:
                # 找到知识图谱开始的位置
                idx = content.find("# 📚 ")
                if idx > 0:
                    content = content[:idx].rstrip()
                updated += 1
            else:
                updated += 1
            
            # 追加新的知识图谱
            content += graph_content
            
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # 创建新的 index.md
            index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(f"# 📚 {dir_path.split('/')[-1]} 目录索引\n")
                f.write(f"\n> **文件数**: {len(dir_files)}\n")
                f.write(graph_content)
            created += 1
        
        if (updated + created) % 20 == 0:
            print(f"    已处理 {updated + created}/{len(dirs)} 个目录...")
    
    print(f"  更新: {updated} 个")
    print(f"  新建: {created} 个")
    print(f"  跳过: {skipped} 个")
    print()
    
    # 4. 更新根目录知识图谱总览
    print("【4/4】更新根目录知识图谱总览（跨目录整合）")
    overview_content = generate_root_overview(files, backlinks)
    
    root_index = ROOT / "index.md"
    with open(root_index, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 如果已有知识图谱总览，先删除旧的
    if "## 🕸️ 知识图谱总览" in content:
        idx = content.find("## 🕸️ 知识图谱总览")
        content = content[:idx].rstrip()
    
    content += overview_content
    
    with open(root_index, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("  ✓ 根目录 index.md 已更新")
    print()
    
    # 保存完整数据
    print("保存分析数据...")
    data = {
        "total_files": len(files),
        "total_dirs": len(dirs),
        "total_backlinks": len(backlinks),
        "files": files,
        "directories": {k: list(v.keys()) for k, v in dirs.items()},
        "backlinks": backlinks
    }
    
    with open(ROOT / "_knowledge_graph_results.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("  ✓ 数据已保存到 _knowledge_graph_results.json")
    print()
    
    print("=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print(f"\n📊 总文件数: {len(files)}")
    print(f"📁 总目录数: {len(dirs)}")
    print(f"✏️  总字数: {sum(info['word_count'] for info in files.values())/10000:.1f} 万字")
    print(f"🔗 有引用关系: {len(backlinks)} 个文件")


if __name__ == "__main__":
    main()
