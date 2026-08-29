#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库 SQLite 数据库构建器 (Knowledge Base Database Builder)
==============================================================

构建一个 SQLite 数据库，全面表达各文件的：
  - 要点（概要、标题结构）
  - 关键字（带频率和排名）
  - 所在目录
  - 与周边文件的调用关系：
      * 引用关系（引用了谁 / 被谁引用）
      - 重叠度（基于关键词 Jaccard 相似度，含重复/互补/相关分级）

数据库表结构：
  files        — 文件元信息（路径、名称、目录、字数、概要、标题、规模分级）
  directories  — 目录统计（文件数、总字数）
  keywords     — 关键词（文件ID、关键词、频率、排名）
  file_refs   — 引用关系（源文件→目标文件）
  similarity   — 相似度（文件对、相似度、共同关键词、关系类型）
  views        — 视图（v_backlinks 被引用统计、v_file_relations 关系汇总）

用法：
  python db_builder.py                    # 完整构建
  python db_builder.py --db path/to.db    # 指定数据库路径
  python db_builder.py --stats            # 显示数据库统计
"""

import os
import re
import sys
import json
import hashlib
import sqlite3
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
    "db_path": str(WORKSPACE_ROOT / "scripts" / "indexkb" / "knowledge_graph.db"),
    "exclude_dirs": {"01_survey", "bak", "import-modules", "oldbak"},
    "exclude_files": {"index.md", "log.md", "README.md", "TRACKING.md"},
    "similarity": {
        "high": 0.60,
        "medium": 0.35,
        "low": 0.25,
    },
    "keywords_top_n": 15,
    "size_levels": {"giant": 10000, "long": 5000, "medium": 2000},
}

_STOPWORDS = {
    "的", "是", "在", "和", "了", "与", "及", "等", "为", "对", "从", "到",
    "一个", "一种", "可以", "进行", "通过", "需要", "以及", "不同", "主要",
    "相关", "方法", "系统", "技术", "设计", "分析", "实现", "开发", "使用",
    "目录", "文件", "内容", "说明", "章节", "概述", "引言", "背景", "总结",
    "问题", "方案", "模式", "架构", "功能", "数据", "平台", "工具", "模型",
    "我们", "这个", "那个", "什么", "怎么", "为什么", "如何",
}


# ============================================================
# 文本提取函数
# ============================================================

def get_file_hash(filepath: Path) -> str:
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def count_words(text: str) -> int:
    cn = len(re.findall(r'[\u4e00-\u9fa5]', text))
    en = len(re.findall(r'[A-Za-z]+', text))
    return cn + en


def get_size_label(word_count: int) -> str:
    lv = CONFIG["size_levels"]
    if word_count >= lv["giant"]:
        return "giant"
    elif word_count >= lv["long"]:
        return "long"
    elif word_count >= lv["medium"]:
        return "medium"
    else:
        return "short"


def extract_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def extract_headings(text: str, max_count: int = 10) -> list:
    headings = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("#"):
            h = line.lstrip("#").strip()
            if h and h not in headings:
                headings.append(h)
                if len(headings) >= max_count:
                    break
    return headings


def extract_keywords_with_freq(text: str, top_n: int = 15) -> list:
    """提取关键词，返回 [(keyword, frequency), ...]"""
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    headings = extract_headings(body, 20)
    heading_text = " ".join(headings)

    wc = defaultdict(int)
    for w in re.findall(r'[\u4e00-\u9fa5]{2,6}', heading_text):
        wc[w] += 2
    for w in re.findall(r'[A-Za-z][A-Za-z0-9_-]{2,}', heading_text):
        wc[w] += 2
    for w in re.findall(r'[\u4e00-\u9fa5]{2,6}', body[:30000]):
        wc[w] += 1

    filtered = [(w, c) for w, c in wc.items()
                if w not in _STOPWORDS and len(w) >= 2]
    filtered.sort(key=lambda x: -x[1])
    return filtered[:top_n]


def extract_internal_links(text: str, current_path: str, all_files: set) -> list:
    links = []
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    current_dir = os.path.dirname(current_path)
    for m in re.finditer(pattern, text):
        link_path = m.group(2)
        if link_path.startswith(("http://", "https://", "#")):
            continue
        if not link_path.endswith(".md"):
            continue
        resolved = os.path.normpath(os.path.join(current_dir, link_path))
        resolved = resolved.replace("\\", "/")
        if resolved in all_files:
            links.append(resolved)
    return list(set(links))


def calc_similarity(kw1: list, kw2: list) -> tuple:
    """返回 (相似度, 共同关键词列表)"""
    s1, s2 = set(kw1), set(kw2)
    if not s1 or not s2:
        return 0.0, []
    overlap = s1 & s2
    union = s1 | s2
    sim = len(overlap) / len(union) if union else 0.0
    return round(sim, 4), sorted(list(overlap))[:8]


def classify_relation(sim: float, same_dir: bool) -> str:
    """根据相似度和是否同目录分类关系类型"""
    th = CONFIG["similarity"]
    if sim >= th["high"]:
        return "duplicate"        # 高度重复
    elif sim >= th["medium"]:
        return "complementary"    # 互补
    elif sim >= th["low"]:
        return "related"          # 相关
    return None


# ============================================================
# 数据库 Schema
# ============================================================

SCHEMA_SQL = """
-- 文件表
CREATE TABLE IF NOT EXISTS files (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    path        TEXT UNIQUE NOT NULL,       -- 相对路径 (如 02_rd/03_hardware/foo.md)
    name        TEXT NOT NULL,              -- 文件名 (无扩展名)
    filename    TEXT NOT NULL,              -- 完整文件名
    dir         TEXT NOT NULL,              -- 所在目录 (相对路径)
    size        INTEGER,                    -- 文件大小 (字节)
    word_count  INTEGER,                    -- 字数
    size_level  TEXT,                       -- 规模分级: giant/long/medium/short
    summary     TEXT,                       -- 概要 (首个标题)
    headings    TEXT,                       -- 标题列表 (JSON)
    keywords    TEXT,                       -- 关键词列表 (JSON, 简化)
    frontmatter TEXT,                       -- frontmatter (JSON)
    md5_hash    TEXT,                       -- 文件 MD5
    scanned_at  TEXT                        -- 扫描时间
);

-- 目录表
CREATE TABLE IF NOT EXISTS directories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    path        TEXT UNIQUE NOT NULL,       -- 目录相对路径
    name        TEXT NOT NULL,              -- 目录名
    parent      TEXT,                       -- 父目录
    file_count  INTEGER DEFAULT 0,          -- 文件数
    total_words INTEGER DEFAULT 0           -- 总字数
);

-- 关键词表 (每个文件每个关键词一行，便于查询)
CREATE TABLE IF NOT EXISTS keywords (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id     INTEGER NOT NULL,
    keyword     TEXT NOT NULL,
    frequency   INTEGER,                    -- 在文件中的权重频率
    rank        INTEGER,                    -- 在文件内的排名 (1=最高)
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);

-- 引用关系表 (源文件引用目标文件)
CREATE TABLE IF NOT EXISTS file_refs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file_id  INTEGER NOT NULL,       -- 引用方文件 ID
    target_file_id  INTEGER NOT NULL,       -- 被引用方文件 ID
    source_path     TEXT NOT NULL,
    target_path     TEXT NOT NULL,
    FOREIGN KEY (source_file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (target_file_id) REFERENCES files(id) ON DELETE CASCADE
);

-- 相似度表 (文件对的相似度/重叠度)
CREATE TABLE IF NOT EXISTS similarity (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    file1_id        INTEGER NOT NULL,
    file2_id        INTEGER NOT NULL,
    file1_path      TEXT NOT NULL,
    file2_path      TEXT NOT NULL,
    similarity      REAL NOT NULL,           -- 相似度 0~1
    overlap_keywords TEXT,                   -- 共同关键词 (JSON)
    same_dir        INTEGER DEFAULT 0,       -- 是否同目录
    relation_type   TEXT,                    -- duplicate/complementary/related
    FOREIGN KEY (file1_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (file2_id) REFERENCES files(id) ON DELETE CASCADE
);

-- 视图: 被引用统计 (每个文件被多少文件引用)
CREATE VIEW IF NOT EXISTS v_backlinks AS
    SELECT
        target_file_id   AS file_id,
        target_path      AS path,
        COUNT(*)         AS backlink_count
    FROM file_refs
    GROUP BY target_file_id;

-- 视图: 引用统计 (每个文件引用了多少文件)
CREATE VIEW IF NOT EXISTS v_outlinks AS
    SELECT
        source_file_id   AS file_id,
        source_path      AS path,
        COUNT(*)         AS outlink_count
    FROM file_refs
    GROUP BY source_file_id;

-- 视图: 文件关系汇总 (引用+被引用+相似度)
CREATE VIEW IF NOT EXISTS v_file_relations AS
    SELECT
        f.id   AS file_id,
        f.path AS path,
        f.name AS name,
        f.dir  AS dir,
        COALESCE(o.outlink_count, 0)  AS outlink_count,
        COALESCE(b.backlink_count, 0) AS backlink_count,
        (SELECT COUNT(*) FROM similarity s
         WHERE s.file1_id = f.id OR s.file2_id = f.id) AS similar_count,
        (SELECT COUNT(*) FROM similarity s
         WHERE (s.file1_id = f.id OR s.file2_id = f.id)
           AND s.relation_type = 'duplicate') AS duplicate_count,
        (SELECT COUNT(*) FROM similarity s
         WHERE (s.file1_id = f.id OR s.file2_id = f.id)
           AND s.relation_type = 'complementary') AS complementary_count
    FROM files f
    LEFT JOIN v_outlinks o ON f.id = o.file_id
    LEFT JOIN v_backlinks b ON f.id = b.file_id;

-- 索引
CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
CREATE INDEX IF NOT EXISTS idx_files_dir ON files(dir);
CREATE INDEX IF NOT EXISTS idx_files_name ON files(name);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_keywords_file_id ON keywords(file_id);
CREATE INDEX IF NOT EXISTS idx_refs_source ON file_refs(source_file_id);
CREATE INDEX IF NOT EXISTS idx_refs_target ON file_refs(target_file_id);
CREATE INDEX IF NOT EXISTS idx_sim_file1 ON similarity(file1_id);
CREATE INDEX IF NOT EXISTS idx_sim_file2 ON similarity(file2_id);
CREATE INDEX IF NOT EXISTS idx_sim_type ON similarity(relation_type);
CREATE INDEX IF NOT EXISTS idx_dirs_path ON directories(path);
"""


# ============================================================
# 构建逻辑
# ============================================================

def is_excluded(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    for part in parts:
        if part in CONFIG["exclude_dirs"]:
            return True
    return path.name in CONFIG["exclude_files"]


def scan_all_files(root: Path) -> dict:
    """扫描所有文件，返回 {rel_path: file_info}"""
    files = {}
    count = 0
    print("  扫描文件中...")
    for md_file in root.rglob("*.md"):
        if is_excluded(md_file, root):
            continue
        count += 1
        rel_path = str(md_file.relative_to(root)).replace("\\", "/")
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"    警告: 无法读取 {rel_path}: {e}")
            continue

        wc = count_words(text)
        headings = extract_headings(text)
        kw_freq = extract_keywords_with_freq(text, CONFIG["keywords_top_n"])
        fm = extract_frontmatter(text)

        files[rel_path] = {
            "path": rel_path,
            "name": md_file.stem,
            "filename": md_file.name,
            "dir": os.path.dirname(rel_path),
            "size": len(text),
            "word_count": wc,
            "size_level": get_size_label(wc),
            "summary": headings[0] if headings else md_file.stem,
            "headings": headings,
            "keywords_freq": kw_freq,
            "keywords": [w for w, _ in kw_freq],
            "frontmatter": fm,
            "md5_hash": get_file_hash(md_file),
        }
        if count % 200 == 0:
            print(f"    已扫描 {count} 个文件...")

    print(f"    共扫描 {len(files)} 个文件")
    return files


def build_database(files: dict, db_path: str):
    """构建 SQLite 数据库"""
    print(f"\n  构建数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    # 创建表结构
    print("  创建表结构...")
    cur.executescript(SCHEMA_SQL)
    conn.commit()

    # 清空旧数据（完整重建）
    for table in ["similarity", "file_refs", "keywords", "files", "directories"]:
        cur.execute(f"DELETE FROM {table}")
    conn.commit()

    now = datetime.now().isoformat()

    # 1. 插入文件
    print("  插入文件记录...")
    path_to_id = {}
    for path, info in files.items():
        cur.execute("""
            INSERT INTO files (path, name, filename, dir, size, word_count,
                              size_level, summary, headings, keywords,
                              frontmatter, md5_hash, scanned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            info["path"], info["name"], info["filename"], info["dir"],
            info["size"], info["word_count"], info["size_level"],
            info["summary"],
            json.dumps(info["headings"], ensure_ascii=False),
            json.dumps(info["keywords"], ensure_ascii=False),
            json.dumps(info["frontmatter"], ensure_ascii=False),
            info["md5_hash"], now,
        ))
        path_to_id[path] = cur.lastrowid
    conn.commit()
    print(f"    已插入 {len(path_to_id)} 个文件")

    # 2. 插入目录统计
    print("  插入目录统计...")
    dir_stats = defaultdict(lambda: {"count": 0, "words": 0})
    for info in files.values():
        d = info["dir"]
        dir_stats[d]["count"] += 1
        dir_stats[d]["words"] += info["word_count"]

    for d, stats in dir_stats.items():
        parts = d.split("/")
        name = parts[-1] if d else "root"
        parent = "/".join(parts[:-1]) if len(parts) > 1 else ""
        cur.execute("""
            INSERT INTO directories (path, name, parent, file_count, total_words)
            VALUES (?, ?, ?, ?, ?)
        """, (d, name, parent, stats["count"], stats["words"]))
    conn.commit()
    print(f"    已插入 {len(dir_stats)} 个目录")

    # 3. 插入关键词
    print("  插入关键词...")
    kw_count = 0
    for path, info in files.items():
        fid = path_to_id[path]
        for rank, (kw, freq) in enumerate(info["keywords_freq"], 1):
            cur.execute("""
                INSERT INTO keywords (file_id, keyword, frequency, rank)
                VALUES (?, ?, ?, ?)
            """, (fid, kw, freq, rank))
            kw_count += 1
    conn.commit()
    print(f"    已插入 {kw_count} 条关键词记录")

    # 4. 插入引用关系
    print("  提取并插入引用关系...")
    all_paths = set(files.keys())
    ref_count = 0
    root = Path(CONFIG["knowledge_root"])

    for path, info in files.items():
        full_path = root / path
        try:
            text = full_path.read_text(encoding="utf-8")
            links = extract_internal_links(text, path, all_paths)
        except:
            links = []

        src_id = path_to_id[path]
        for target in links:
            if target in path_to_id:
                tgt_id = path_to_id[target]
                cur.execute("""
                    INSERT INTO file_refs (source_file_id, target_file_id,
                                           source_path, target_path)
                    VALUES (?, ?, ?, ?)
                """, (src_id, tgt_id, path, target))
                ref_count += 1
    conn.commit()
    print(f"    已插入 {ref_count} 条引用关系")

    # 5. 计算并插入相似度
    print("  计算相似度（重叠度）...")
    sim_count = 0
    th = CONFIG["similarity"]
    path_list = list(files.keys())
    total_pairs = len(path_list) * (len(path_list) - 1) // 2
    processed = 0

    for i in range(len(path_list)):
        p1 = path_list[i]
        f1 = files[p1]
        id1 = path_to_id[p1]
        for j in range(i + 1, len(path_list)):
            p2 = path_list[j]
            f2 = files[p2]
            id2 = path_to_id[p2]

            sim, overlap = calc_similarity(f1["keywords"], f2["keywords"])
            same_dir = 1 if f1["dir"] == f2["dir"] else 0
            rel_type = classify_relation(sim, same_dir)

            if rel_type is not None:
                cur.execute("""
                    INSERT INTO similarity (file1_id, file2_id, file1_path,
                                           file2_path, similarity,
                                           overlap_keywords, same_dir,
                                           relation_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (id1, id2, p1, p2, sim,
                      json.dumps(overlap, ensure_ascii=False),
                      same_dir, rel_type))
                sim_count += 1

            processed += 1
            if processed % 200000 == 0:
                conn.commit()
                print(f"    已处理 {processed}/{total_pairs} 对...")

    conn.commit()
    print(f"    已插入 {sim_count} 条相似度记录")

    conn.close()
    return {
        "files": len(files),
        "directories": len(dir_stats),
        "keywords": kw_count,
        "file_refs": ref_count,
        "similarity": sim_count,
    }


def show_stats(db_path: str):
    """显示数据库统计信息"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("=" * 60)
    print("📊 数据库统计信息")
    print("=" * 60)

    for table in ["files", "directories", "keywords", "file_refs", "similarity"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {table:15s}: {count:>6} 条")

    print()
    print("--- 规模分级 ---")
    cur.execute("SELECT size_level, COUNT(*) FROM files GROUP BY size_level ORDER BY COUNT(*) DESC")
    for level, cnt in cur.fetchall():
        print(f"  {level:10s}: {cnt:>6} 个文件")

    print()
    print("--- 被引用最多 Top 10 ---")
    cur.execute("""
        SELECT f.path, f.name, COALESCE(b.backlink_count, 0) AS bc
        FROM files f
        LEFT JOIN v_backlinks b ON f.id = b.file_id
        ORDER BY bc DESC
        LIMIT 10
    """)
    for path, name, bc in cur.fetchall():
        print(f"  {bc:>3}次 ← {name} ({path})")

    print()
    print("--- 高度重复文件对 Top 10 ---")
    cur.execute("""
        SELECT file1_path, file2_path, similarity
        FROM similarity
        WHERE relation_type = 'duplicate'
        ORDER BY similarity DESC
        LIMIT 10
    """)
    for p1, p2, sim in cur.fetchall():
        print(f"  {sim:.0%} | {p1} ↔ {p2}")

    print()
    print("--- 高频关键词 Top 15 ---")
    cur.execute("""
        SELECT keyword, COUNT(DISTINCT file_id) AS file_count
        FROM keywords
        GROUP BY keyword
        ORDER BY file_count DESC
        LIMIT 15
    """)
    for kw, cnt in cur.fetchall():
        print(f"  {cnt:>4}个文件 | {kw}")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="知识库 SQLite 数据库构建器")
    parser.add_argument("--db", type=str, default=CONFIG["db_path"],
                        help="数据库路径")
    parser.add_argument("--stats", action="store_true",
                        help="仅显示数据库统计")
    args = parser.parse_args()

    db_path = args.db
    root = Path(CONFIG["knowledge_root"])

    if args.stats:
        if not Path(db_path).exists():
            print(f"❌ 数据库不存在: {db_path}")
            print("   请先运行: python db_builder.py")
            return
        show_stats(db_path)
        return

    print("=" * 60)
    print("📚 知识库 SQLite 数据库构建器")
    print("=" * 60)
    print(f"  知识根目录: {root}")
    print(f"  数据库路径: {db_path}")
    print(f"  排除目录:   {', '.join(CONFIG['exclude_dirs'])}")
    print()

    # 1. 扫描文件
    print("【1/3】扫描文件并提取信息")
    files = scan_all_files(root)
    print()

    # 2. 构建数据库
    print("【2/3】构建数据库")
    stats = build_database(files, db_path)
    print()

    # 3. 显示统计
    print("【3/3】数据库统计")
    show_stats(db_path)

    print()
    print("=" * 60)
    print("✅ 数据库构建完成！")
    print("=" * 60)
    print(f"  📁 数据库: {db_path}")
    print(f"  📄 文件:   {stats['files']}")
    print(f"  📂 目录:   {stats['directories']}")
    print(f"  🏷️  关键词: {stats['keywords']}")
    print(f"  🔗 引用:   {stats['file_refs']}")
    print(f"  📐 相似度: {stats['similarity']}")


if __name__ == "__main__":
    main()
