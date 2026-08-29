#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库知识图谱分析器
- 提取每个文件的概要描述
- 分析文件间的引用关系、互补关系、重复关系
- 生成结构化的 index.md
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


def extract_summary(text: str, max_len: int = 200) -> str:
    """提取文件概要：优先用 frontmatter 的 description/summary，否则取第一个正文段落"""
    fm = extract_frontmatter(text)
    if fm.get("description"):
        return fm["description"][:max_len]
    if fm.get("summary"):
        return fm["summary"][:max_len]

    # 去掉 frontmatter
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    # 找第一个非标题、非空行的段落
    lines = body.split("\n")
    para = []
    for line in lines:
        line = line.strip()
        if not line:
            if para:
                break
            continue
        if line.startswith("#"):
            if para:
                break
            continue
        if line.startswith(">"):
            if para:
                break
            continue
        if line.startswith("|"):
            if para:
                break
            continue
        if line.startswith("-") or line.startswith("*"):
            if para:
                break
            para.append(line.lstrip("-* "))
            continue
        para.append(line)
        if sum(len(p) for p in para) > max_len:
            break

    summary = " ".join(para)
    return summary[:max_len]


def extract_headings(text: str) -> list:
    """提取所有标题，用于判断内容结构"""
    headings = []
    for line in text.split("\n"):
        m = re.match(r"^(#{1,4})\s+(.+)", line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append((level, title))
    return headings


def extract_internal_links(text: str, current_file: Path) -> list:
    """提取文件中的内部链接（相对路径的 .md 文件）"""
    links = set()
    # 匹配 markdown 链接 [text](path)
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+\.md[^)]*)\)", text):
        link_path = m.group(2).split("#")[0].split("?")[0].strip()
        if link_path.startswith("http"):
            continue
        if not link_path.endswith(".md"):
            continue
        # 解析相对路径
        try:
            resolved = (current_file.parent / link_path).resolve()
            rel = resolved.relative_to(ROOT)
            links.add(str(rel).replace("\\", "/"))
        except Exception:
            continue
    return list(links)


def extract_keywords(text: str, num: int = 10) -> list:
    """提取关键词（简单的高频名词短语）"""
    # 去掉代码块和markdown标记
    clean = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    clean = re.sub(r"[#>*`|]", "", clean)
    # 提取2-4字的中文短语或英文术语
    words = re.findall(r"[\u4e00-\u9fa5]{2,6}|[A-Za-z][A-Za-z0-9_-]{2,}", clean)
    freq = defaultdict(int)
    stop = {"的", "和", "与", "在", "是", "为", "对", "等", "中", "了", "将", "从", "到", "也", "都", "不", "有", "及", "或", "其", "这", "那", "一个", "一种", "可以", "需要", "通过", "进行", "使用", "基于", "以及"}
    for w in words:
        if w in stop or len(w) < 2:
            continue
        freq[w] += 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:num]]


def scan_all_files() -> dict:
    """扫描所有文件并提取元信息"""
    files = {}
    for md_file in ROOT.rglob("*.md"):
        if is_excluded(md_file):
            continue
        rel_path = str(md_file.relative_to(ROOT)).replace("\\", "/")
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        size = len(text)
        fm = extract_frontmatter(text)
        summary = extract_summary(text)
        headings = extract_headings(text)
        links = extract_internal_links(text, md_file)
        keywords = extract_keywords(text)
        word_count = len(re.findall(r"[\u4e00-\u9fa5]|[A-Za-z]+", text))

        files[rel_path] = {
            "path": rel_path,
            "name": md_file.stem,
            "size": size,
            "word_count": word_count,
            "frontmatter": fm,
            "summary": summary,
            "headings": [h[1] for h in headings[:10]],
            "internal_links": links,
            "keywords": keywords,
            "dir": str(Path(rel_path).parent).replace("\\", "/"),
        }
    return files


def analyze_relationships(files: dict) -> dict:
    """分析文件间关系"""
    # 反向引用：谁引用了我
    backlinks = defaultdict(list)
    for path, info in files.items():
        for link in info["internal_links"]:
            if link in files:
                backlinks[link].append(path)

    # 内容相似度（基于关键词重叠）
    similarity = {}
    file_list = list(files.keys())
    for i in range(len(file_list)):
        for j in range(i + 1, len(file_list)):
            p1, p2 = file_list[i], file_list[j]
            k1 = set(files[p1]["keywords"])
            k2 = set(files[p2]["keywords"])
            if not k1 or not k2:
                continue
            overlap = k1 & k2
            union = k1 | k2
            sim = len(overlap) / len(union) if union else 0
            if sim >= 0.3:
                similarity[(p1, p2)] = {
                    "similarity": round(sim, 2),
                    "common_keywords": list(overlap)[:8],
                }

    return {
        "backlinks": {k: v for k, v in backlinks.items()},
        "similarity": similarity,
    }


def group_by_directory(files: dict) -> dict:
    """按目录分组"""
    dirs = defaultdict(dict)
    for path, info in files.items():
        d = info["dir"]
        dirs[d][path] = info
    return dirs


def detect_duplicates(files: dict, similarity: dict) -> list:
    """检测高度重复的文件（相似度>0.6）"""
    dupes = []
    for (p1, p2), sim in similarity.items():
        if sim["similarity"] >= 0.6:
            dupes.append((p1, p2, sim))
    dupes.sort(key=lambda x: -x[2]["similarity"])
    return dupes


def detect_complementary(files: dict, similarity: dict) -> list:
    """检测互补关系（相似度0.2-0.5，且有明确引用或同目录）"""
    comp = []
    for (p1, p2), sim in similarity.items():
        if 0.2 <= sim["similarity"] <= 0.5:
            f1, f2 = files[p1], files[p2]
            # 同目录视为更可能互补
            if f1["dir"] == f2["dir"]:
                comp.append((p1, p2, sim, "同目录主题互补"))
            # 有引用关系的互补
            elif p2 in f1["internal_links"] or p1 in f2["internal_links"]:
                comp.append((p1, p2, sim, "引用式互补"))
    comp.sort(key=lambda x: -x[2]["similarity"])
    return comp


def main():
    print("📂 扫描文件中...")
    files = scan_all_files()
    print(f"✅ 共扫描到 {len(files)} 个有效文件")

    print("🔗 分析关系中...")
    rels = analyze_relationships(files)

    print("📁 按目录分组...")
    dirs = group_by_directory(files)

    print("🔍 检测重复与互补...")
    dupes = detect_duplicates(files, rels["similarity"])
    comps = detect_complementary(files, rels["similarity"])

    # 保存分析结果
    result = {
        "total_files": len(files),
        "total_dirs": len(dirs),
        "total_backlinks": len(rels["backlinks"]),
        "total_similar_pairs": len(rels["similarity"]),
        "duplicate_pairs": len(dupes),
        "complementary_pairs": len(comps),
        "files": files,
        "directories": {d: list(fs.keys()) for d, fs in dirs.items()},
        "backlinks": rels["backlinks"],
        "duplicates": [(p1, p2, s) for p1, p2, s in dupes[:30]],
        "complementary": [(p1, p2, s, t) for p1, p2, s, t in comps[:50]],
    }

    out_file = ROOT / "_knowledge_graph_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n📊 分析完成！结果已保存到: {out_file}")
    print(f"   - 总文件数: {len(files)}")
    print(f"   - 目录数: {len(dirs)}")
    print(f"   - 有反向引用的文件: {len(rels['backlinks'])}")
    print(f"   - 相似内容对: {len(rels['similarity'])}")
    print(f"   - 高度重复对 (≥0.6): {len(dupes)}")
    print(f"   - 互补内容对 (0.2-0.5): {len(comps)}")

    # 打印 Top 10 目录
    print("\n📁 文件数 Top 10 目录:")
    top_dirs = sorted(dirs.items(), key=lambda x: -len(x[1]))[:10]
    for d, fs in top_dirs:
        print(f"   {d}: {len(fs)} 个文件")

    # 打印重复度最高的文件对
    if dupes:
        print(f"\n⚠️  高度重复 Top 10:")
        for p1, p2, sim in dupes[:10]:
            print(f"   {sim['similarity']:.2f} | {Path(p1).name} ↔ {Path(p2).name}")
            print(f"         共同关键词: {', '.join(sim['common_keywords'][:5])}")

    return result


if __name__ == "__main__":
    main()
