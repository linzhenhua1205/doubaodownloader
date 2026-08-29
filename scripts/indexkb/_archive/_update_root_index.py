#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新根目录 index.md 的知识图谱总览部分
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"h:\github\cowkb\knowledge")

# 只排除用户指定的三个目录
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
    
    body_cn = re.findall(r'[\u4e00-\u9fa5]{2,6}', body[:20000])
    for w in body_cn[:200]:
        word_count[w] += 1
    
    stopwords = {"的", "是", "在", "和", "了", "与", "及", "等", "为", "对", "从", "到",
                 "一个", "一种", "可以", "进行", "通过", "需要", "以及", "不同", "主要",
                 "相关", "方法", "系统", "技术", "设计", "分析", "实现", "开发", "使用",
                 "目录", "文件", "内容", "说明", "章节", "概述", "引言", "背景", "总结"}
    
    filtered = [(w, c) for w, c in word_count.items() if w not in stopwords and len(w) >= 2]
    filtered.sort(key=lambda x: -x[1])
    
    return [w for w, c in filtered[:top_n]]


def count_chinese_words(text: str) -> int:
    cn_chars = re.findall(r'[\u4e00-\u9fa5]', text)
    en_words = re.findall(r'[A-Za-z]+', text)
    return len(cn_chars) + len(en_words)


def scan_files():
    files = {}
    for md_file in ROOT.rglob("*.md"):
        if is_excluded(md_file):
            continue
        rel_path = str(md_file.relative_to(ROOT)).replace("\\", "/")
        try:
            text = md_file.read_text(encoding="utf-8")
        except:
            continue
        
        word_count = count_chinese_words(text)
        headings = extract_headings(text)
        keywords = extract_keywords(text)
        internal_links = extract_internal_links(text, rel_path)
        
        files[rel_path] = {
            "path": rel_path,
            "name": md_file.stem,
            "size": len(text),
            "word_count": word_count,
            "headings": headings,
            "internal_links": internal_links,
            "keywords": keywords,
            "dir": os.path.dirname(rel_path)
        }
    
    return files


def build_backlinks(files):
    backlinks = defaultdict(set)
    for path, info in files.items():
        for link in info["internal_links"]:
            if link in files:
                backlinks[link].add(path)
    return {k: list(v) for k, v in backlinks.items()}


def get_similarity(f1, f2):
    k1 = set(f1["keywords"])
    k2 = set(f2["keywords"])
    if not k1 or not k2:
        return 0, []
    overlap = k1 & k2
    union = k1 | k2
    sim = len(overlap) / len(union) if union else 0
    return sim, list(overlap)[:6]


def generate_root_overview(files, backlinks):
    """生成根目录知识图谱总览内容"""
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
    
    # 高度相似/可能重复文件（跨目录）
    all_pairs = []
    file_list = list(files.keys())
    for i in range(len(file_list)):
        for j in range(i+1, len(file_list)):
            p1, p2 = file_list[i], file_list[j]
            f1, f2 = files[p1], files[p2]
            if f1["dir"] == f2["dir"]:
                continue  # 同目录的不在总览里重复展示
            sim, overlap = get_similarity(f1, f2)
            if sim >= 0.5:
                all_pairs.append((p1, p2, sim, overlap))
    
    all_pairs.sort(key=lambda x: -x[2])
    
    lines.append("### ⚠️ 高度相似/可能重复文件（跨目录）")
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
    cross_pairs = [(p1, p2, sim, overlap) for p1, p2, sim, overlap in all_pairs if sim >= 0.35]
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
    
    # 核心主题领域
    all_keywords = defaultdict(int)
    keyword_files = defaultdict(list)
    for path, info in files.items():
        for kw in info["keywords"][:5]:
            all_keywords[kw] += 1
            if len(keyword_files[kw]) < 3:
                keyword_files[kw].append(path)
    
    top_keywords = sorted(all_keywords.items(), key=lambda x: -x[1])[:30]
    
    lines.append("### 🏷️ 核心主题领域")
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
    
    # 主题聚类（基于关键词的大致分类）
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
        cluster_files = set()
        for path, info in files.items():
            for kw in info["keywords"]:
                if kw in cluster_kws:
                    cluster_files.add(path)
                    break
        lines.append(f"- **{cluster_name}**: ~{len(cluster_files)} 个文件")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)


def main():
    print("正在扫描文件...")
    files = scan_files()
    print(f"扫描到 {len(files)} 个文件")
    
    backlinks = build_backlinks(files)
    print(f"有反向引用的文件: {len(backlinks)} 个")
    
    print("\n正在生成根目录知识图谱总览...")
    overview_content = generate_root_overview(files, backlinks)
    
    # 读取现有 index.md
    index_path = ROOT / "index.md"
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 如果已有知识图谱总览，先删除旧的
    if "## 🕸️ 知识图谱总览" in content:
        # 删除从知识图谱总览开始到文件末尾的部分
        content = content.split("## 🕸️ 知识图谱总览")[0].rstrip()
    
    # 追加新的知识图谱总览
    content += overview_content
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✓ 根目录 index.md 已更新")
    print(f"\n统计数据:")
    print(f"  - 总文件数: {len(files)}")
    print(f"  - 总目录数: {len(set(info['dir'] for info in files.values()))}")
    print(f"  - 总字数: {sum(info['word_count'] for info in files.values())/10000:.1f} 万字")
    print(f"  - 枢纽文件数: {len(backlinks)}")


if __name__ == "__main__":
    main()
