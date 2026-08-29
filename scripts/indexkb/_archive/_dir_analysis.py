#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录结构分析脚本 — 从 knowledge_graph.db 提取优化所需数据
"""
import sqlite3
import json
from pathlib import Path
from collections import defaultdict

DB_PATH = r"h:\github\cowkb\scripts\indexkb\knowledge_graph.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=" * 70)
print("📊 目录分布分析（按文件数排序 Top 30）")
print("=" * 70)
cur.execute("""
    SELECT path, name, parent, file_count, total_words
    FROM directories
    ORDER BY file_count DESC
    LIMIT 30
""")
for r in cur.fetchall():
    print(f"  {r['file_count']:>4}文件 {r['total_words']:>8,}字  {r['path']}")

print()
print("=" * 70)
print("📊 L1 顶层模块分布")
print("=" * 70)
cur.execute("""
    SELECT substr(path, 1, instr(path || '/', '/')-1) AS l1,
           SUM(file_count) AS files, SUM(total_words) AS words
    FROM directories
    WHERE path NOT LIKE '%/%' OR path = ''
    GROUP BY l1
    ORDER BY files DESC
""")
# Actually get L1 by looking at top-level dirs
cur.execute("SELECT dir FROM files")
l1_counts = defaultdict(lambda: {"files": 0, "words": 0})
for r in cur.fetchall():
    d = r["dir"]
    l1 = d.split("/")[0] if d else "(root)"
    l1_counts[l1]["files"] += 1
    l1_counts[l1]["words"] += 0

# Get word counts
cur.execute("SELECT dir, SUM(word_count) as wc FROM files GROUP BY dir")
dir_wc = {r["dir"]: r["wc"] for r in cur.fetchall()}

for d, wc in dir_wc.items():
    l1 = d.split("/")[0] if d else "(root)"
    l1_counts[l1]["words"] += wc

print(f"  {'模块':<30s} {'文件数':>6s} {'字数':>10s}")
print(f"  {'-'*30} {'-'*6} {'-'*10}")
for l1, stats in sorted(l1_counts.items(), key=lambda x: -x[1]["files"]):
    print(f"  {l1:<30s} {stats['files']:>6} {stats['words']:>10,}")

print()
print("=" * 70)
print("🔴 高度重复文件对（跨目录，相似度≥60%）")
print("=" * 70)
cur.execute("""
    SELECT file1_path, file2_path, similarity, overlap_keywords, relation_type
    FROM similarity
    WHERE relation_type = 'duplicate' AND same_dir = 0
    ORDER BY similarity DESC
""")
cross_dups = cur.fetchall()
print(f"  共 {len(cross_dups)} 对跨目录重复")
for r in cross_dups[:20]:
    p1 = r["file1_path"]
    p2 = r["file2_path"]
    l1_1 = p1.split("/")[0]
    l1_2 = p2.split("/")[0]
    print(f"  {r['similarity']:.0%} [{l1_1}→{l1_2}]")
    print(f"    A: {p1}")
    print(f"    B: {p2}")

print()
print("=" * 70)
print("🔴 同目录内高度重复文件对")
print("=" * 70)
cur.execute("""
    SELECT file1_path, file2_path, similarity, overlap_keywords, relation_type
    FROM similarity
    WHERE relation_type = 'duplicate' AND same_dir = 1
    ORDER BY similarity DESC
""")
same_dups = cur.fetchall()
print(f"  共 {len(same_dups)} 对同目录重复")
for r in same_dups[:20]:
    p1 = r["file1_path"]
    p2 = r["file2_path"]
    print(f"  {r['similarity']:.0%} {Path(p1).name} ↔ {Path(p2).name}")
    print(f"    {p1}")
    print(f"    {p2}")

print()
print("=" * 70)
print("🟡 跨目录互补文件对（相似度 35%-60%，Top 15）")
print("=" * 70)
cur.execute("""
    SELECT file1_path, file2_path, similarity, overlap_keywords
    FROM similarity
    WHERE relation_type = 'complementary' AND same_dir = 0
    ORDER BY similarity DESC
    LIMIT 15
""")
for r in cur.fetchall():
    p1 = r["file1_path"]
    p2 = r["file2_path"]
    overlap = json.loads(r["overlap_keywords"]) if r["overlap_keywords"] else []
    print(f"  {r['similarity']:.0%} {Path(p1).name} ↔ {Path(p2).name}")
    print(f"    A: {p1}")
    print(f"    B: {p2}")
    print(f"    共同: {', '.join(overlap[:4])}")

print()
print("=" * 70)
print("🏝️ 孤立文件（不引用也不被引用，Top 20 by字数）")
print("=" * 70)
cur.execute("""
    SELECT f.path, f.name, f.dir, f.word_count
    FROM files f
    WHERE f.id NOT IN (SELECT DISTINCT source_file_id FROM file_refs)
      AND f.id NOT IN (SELECT DISTINCT target_file_id FROM file_refs)
    ORDER BY f.word_count DESC
    LIMIT 20
""")
orphans = cur.fetchall()
cur.execute("""
    SELECT COUNT(*) FROM files f
    WHERE f.id NOT IN (SELECT DISTINCT source_file_id FROM file_refs)
      AND f.id NOT IN (SELECT DISTINCT target_file_id FROM file_refs)
""")
total_orphans = cur.fetchone()[0]
print(f"  共 {total_orphans} 个孤立文件（占 {total_orphans/1059*100:.0f}%）")
for r in orphans:
    print(f"  {r['word_count']:>6,}字  [{r['dir']}] {r['name']}")

print()
print("=" * 70)
print("📂 目录深度分析（超3级的目录）")
print("=" * 70)
cur.execute("SELECT DISTINCT dir FROM files ORDER BY dir")
deep_dirs = set()
for r in cur.fetchall():
    d = r["dir"]
    depth = len(d.split("/")) if d else 0
    if depth > 3:
        deep_dirs.add(d)
if deep_dirs:
    print(f"  发现 {len(deep_dirs)} 个超3级目录:")
    for d in sorted(deep_dirs):
        cur.execute("SELECT COUNT(*) FROM files WHERE dir = ?", (d,))
        cnt = cur.fetchone()[0]
        print(f"    {cnt}文件  {d} (深度{len(d.split('/'))})")
else:
    print("  无超3级目录 ✅")

print()
print("=" * 70)
print("📊 单目录文件数 > 50 的目录")
print("=" * 70)
cur.execute("""
    SELECT dir, COUNT(*) as cnt, SUM(word_count) as wc
    FROM files
    GROUP BY dir
    HAVING cnt > 50
    ORDER BY cnt DESC
""")
for r in cur.fetchall():
    print(f"  {r['cnt']:>4}文件 {r['wc']:>8,}字  {r['dir']}")

print()
print("=" * 70)
print("📊 06_others/oldbak 目录分析（归档文件统计）")
print("=" * 70)
cur.execute("""
    SELECT dir, COUNT(*) as cnt, SUM(word_count) as wc
    FROM files
    WHERE dir LIKE '06_others/%'
    GROUP BY dir
    ORDER BY cnt DESC
""")
for r in cur.fetchall():
    print(f"  {r['cnt']:>4}文件 {r['wc']:>8,}字  {r['dir']}")

print()
print("=" * 70)
print("📊 引用最多的文件 Top 15（枢纽节点）")
print("=" * 70)
cur.execute("""
    SELECT f.path, f.name, f.dir,
           COALESCE(b.bc, 0) AS backlinks,
           COALESCE(o.oc, 0) AS outlinks
    FROM files f
    LEFT JOIN (SELECT target_file_id, COUNT(*) AS bc FROM file_refs GROUP BY target_file_id) b
        ON f.id = b.target_file_id
    LEFT JOIN (SELECT source_file_id, COUNT(*) AS oc FROM file_refs GROUP BY source_file_id) o
        ON f.id = o.source_file_id
    ORDER BY backlinks DESC
    LIMIT 15
""")
for r in cur.fetchall():
    print(f"  被引{r['backlinks']:>3} 引出{r['outlinks']:>3}  [{r['dir']}] {r['name']}")

print()
print("=" * 70)
print("📊 交叉引用最多的目录对（跨目录引用 Top 15）")
print("=" * 70)
cur.execute("""
    SELECT
        substr(r.source_path, 1, instr(r.source_path || '/', '/')-1) AS src_l1,
        substr(r.target_path, 1, instr(r.target_path || '/', '/')-1) AS tgt_l1,
        COUNT(*) AS cnt
    FROM file_refs r
    WHERE substr(r.source_path, 1, instr(r.source_path || '/', '/')-1)
       != substr(r.target_path, 1, instr(r.target_path || '/', '/')-1)
    GROUP BY src_l1, tgt_l1
    ORDER BY cnt DESC
    LIMIT 15
""")
for r in cur.fetchall():
    print(f"  {r['cnt']:>4}次  {r['src_l1']} → {r['tgt_l1']}")

conn.close()
print("\n✅ 分析完成")
