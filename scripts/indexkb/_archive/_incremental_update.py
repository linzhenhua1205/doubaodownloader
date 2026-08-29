#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量更新：为遗漏的目录生成知识图谱
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
    # 匹配 markdown 链接 [text](path)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(pattern, text):
        link_text = match.group(1)
        link_path = match.group(2)
        # 跳过外部链接
        if link_path.startswith("http://") or link_path.startswith("https://"):
            continue
        if link_path.startswith("#"):
            continue
        # 只保留 .md 链接
        if not link_path.endswith(".md"):
            continue
        # 解析相对路径
        current_dir = os.path.dirname(current_path)
        resolved = os.path.normpath(os.path.join(current_dir, link_path))
        resolved = resolved.replace("\\", "/")
        links.append(resolved)
    return list(set(links))


def extract_keywords(text: str, top_n: int = 10) -> list:
    # 简单的关键词提取：取中文/英文单词，过滤停用词
    # 去掉 frontmatter
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    # 提取标题
    headings = extract_headings(body, 20)
    heading_text = " ".join(headings)
    
    # 提取所有中文字符（2-4字词组）
    cn_words = re.findall(r'[\u4e00-\u9fa5]{2,6}', heading_text)
    
    # 提取英文单词（标题中的）
    en_words = re.findall(r'[A-Za-z][A-Za-z0-9_-]{2,}', heading_text)
    
    # 统计频率
    word_count = defaultdict(int)
    for w in cn_words:
        word_count[w] += 2  # 标题中的词权重高
    for w in en_words:
        word_count[w] += 2
    
    # 从正文中提取一些高频词
    body_cn = re.findall(r'[\u4e00-\u9fa5]{2,6}', body[:20000])
    for w in body_cn[:200]:
        word_count[w] += 1
    
    # 过滤常见停用词
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
    """扫描所有文件并提取信息"""
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
        frontmatter = extract_frontmatter(text)
        
        # 提取概要（第一个标题 + 前几个二级标题）
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
    
    return files


def build_directories(files):
    """按目录组织文件"""
    dirs = defaultdict(list)
    for path, info in files.items():
        d = info["dir"]
        dirs[d].append(path)
    return dict(dirs)


def build_backlinks(files):
    """构建反向引用"""
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


def find_similar_pairs(files, dirs):
    """查找相似/互补/重复文件对"""
    pairs = []
    file_list = list(files.keys())
    
    for i in range(len(file_list)):
        for j in range(i+1, len(file_list)):
            p1, p2 = file_list[i], file_list[j]
            f1, f2 = files[p1], files[p2]
            sim, overlap = get_similarity(f1, f2)
            if sim >= 0.2:
                same_dir = f1["dir"] == f2["dir"]
                pairs.append({
                    "file1": p1,
                    "file2": p2,
                    "similarity": round(sim, 2),
                    "overlap": overlap,
                    "same_dir": same_dir
                })
    
    pairs.sort(key=lambda x: -x["similarity"])
    return pairs


def generate_dir_graph_content(dir_path, dir_files, all_files, backlinks):
    """生成一个目录的知识图谱内容（追加到 index.md 末尾）"""
    lines = []
    dir_name = dir_path.split("/")[-1] if dir_path and dir_path != "." else "根目录"
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"# 📚 {dir_name} 目录知识图谱")
    lines.append("")
    lines.append(f"> 📊 本目录共 **{len(dir_files)}** 个文件")
    lines.append("")
    
    # 按文件大小排序
    sorted_files = sorted(dir_files.items(), key=lambda x: -x[1]["word_count"])
    
    # 文件概要总览表
    lines.append("---")
    lines.append("")
    lines.append("## 📋 文件概要总览")
    lines.append("")
    lines.append("| # | 文件 | 规模 | 核心主题 | 关键词 |")
    lines.append("|:--:|:-----|:----:|:---------|:-------|")
    
    for i, (path, info) in enumerate(sorted_files, 1):
        fname = Path(path).name
        size_label = get_file_size_label(info["word_count"])
        theme = info["headings"][0] if info["headings"] else info["name"]
        theme = theme[:25] + "..." if len(theme) > 25 else theme
        keywords = "、".join(info["keywords"][:5])
        link = f"[{info['name']}]({Path(path).name})"
        lines.append(f"| {i} | {link} | {size_label} | {theme} | {keywords} |")
    
    lines.append("")
    
    # 文件详情与关系图谱
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
        if info["internal_links"]:
            # 筛选同目录内的引用
            same_dir_links = [l for l in info["internal_links"] if l in all_files and os.path.dirname(l) == info["dir"]]
            if same_dir_links:
                if not has_links:
                    lines.append("**🔗 引用关系**")
                    lines.append("")
                    has_links = True
                link_strs = []
                for l in same_dir_links[:6]:
                    lname = Path(l).name
                    link_strs.append(f"[{lname}](../{l})")
                lines.append(f"- 📤 **引用了**（{len(same_dir_links)}个）: {'、'.join(link_strs)}")
        
        if path in backlinks:
            bl = backlinks[path]
            same_dir_bl = [l for l in bl if os.path.dirname(l) == info["dir"]]
            if same_dir_bl:
                if not has_links:
                    lines.append("**🔗 引用关系**")
                    lines.append("")
                    has_links = True
                link_strs = []
                for l in same_dir_bl[:6]:
                    lname = Path(l).name
                    link_strs.append(f"[{lname}](../{l})")
                lines.append(f"- 📥 **被引用**（{len(same_dir_bl)}个）: {'、'.join(link_strs)}")
        
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
            for other_path, sim, overlap in similar_in_dir[:5]:
                oname = Path(other_path).name
                lines.append(f"- [{oname}]({Path(other_path).name}) — 相似度 {int(sim*100)}%（共同主题：{'、'.join(overlap)}）")
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
                lines.append(f"- [{oname}]({Path(other_path).name}) — 相似度 {int(sim*100)}%（共同主题：{'、'.join(overlap)}）")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # 高度重复文件汇总
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
            lines.append(f"| [{n1}]({Path(p1).name}) | [{n2}]({Path(p2).name}) | {int(sim*100)}% | {'、'.join(overlap[:4])} |")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def get_file_size_label(word_count):
    if word_count >= 10000:
        return "📕 巨篇"
    elif word_count >= 5000:
        return "📗 长文"
    elif word_count >= 2000:
        return "📘 中篇"
    else:
        return "📙 短篇"


def main():
    print("正在扫描文件...")
    files = scan_files()
    print(f"扫描到 {len(files)} 个文件")
    
    dirs = build_directories(files)
    print(f"涉及 {len(dirs)} 个目录")
    
    backlinks = build_backlinks(files)
    print(f"有反向引用的文件: {len(backlinks)} 个")
    
    # 找出需要新增的目录（之前没覆盖到的）
    target_dirs = {}
    
    # 1. 20260720_take_stock 目录
    take_stock_dir = "07_industry-research/03_server/20260720_take_stock"
    if take_stock_dir in dirs:
        target_dirs[take_stock_dir] = dirs[take_stock_dir]
    
    # 2. take_stock/topics 子目录
    topics_dir = "07_industry-research/03_server/20260720_take_stock/topics"
    if topics_dir in dirs:
        target_dirs[topics_dir] = dirs[topics_dir]
    
    # 3. 06_others/oldbak 及其子目录
    for d in dirs:
        if "oldbak" in d or "sources" in d:
            target_dirs[d] = dirs[d]
    
    print(f"\n需要新增知识图谱的目录: {len(target_dirs)} 个")
    for d in sorted(target_dirs.keys()):
        print(f"  - {d} ({len(target_dirs[d])} 个文件)")
    
    # 为每个目录生成知识图谱
    print("\n正在生成知识图谱...")
    
    for dir_path in sorted(target_dirs.keys()):
        dir_files_dict = {p: files[p] for p in target_dirs[dir_path] if p in files}
        if not dir_files_dict:
            continue
        
        index_path = ROOT / dir_path / "index.md"
        
        # 检查是否已有知识图谱
        if index_path.exists():
            existing_content = index_path.read_text(encoding="utf-8")
            if "文件详情与关系图谱" in existing_content:
                print(f"  跳过 {dir_path} (已有知识图谱)")
                continue
        
        graph_content = generate_dir_graph_content(dir_path, dir_files_dict, files, backlinks)
        
        if index_path.exists():
            # 追加到现有 index.md
            with open(index_path, "a", encoding="utf-8") as f:
                f.write(graph_content)
            print(f"  ✓ {dir_path} (已追加)")
        else:
            # 创建新的 index.md
            index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(f"# 📚 {dir_path.split('/')[-1]} 目录索引\n")
                f.write(f"\n> **文件数**: {len(dir_files_dict)}\n")
                f.write(graph_content)
            print(f"  ✓ {dir_path} (新建)")
    
    print("\n完成！")


if __name__ == "__main__":
    main()
