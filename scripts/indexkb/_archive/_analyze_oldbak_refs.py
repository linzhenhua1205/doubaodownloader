#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 oldbak 入站引用：外部文件 → oldbak 文件
"""
import sqlite3
import json
from collections import defaultdict

DB_PATH = r"h:\github\cowkb\scripts\indexkb\knowledge_graph.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. 查找所有 oldbak 文件
print("=" * 70)
print("📊 oldbak 文件清单")
print("=" * 70)
cur.execute("""
    SELECT id, path, name FROM files
    WHERE dir LIKE '06_others/oldbak%' OR path LIKE '06_others/oldbak%'
    ORDER BY path
""")
oldbak_files = cur.fetchall()
oldbak_paths = {r["path"] for r in oldbak_files}
oldbak_ids = {r["id"] for r in oldbak_files}
print(f"  oldbak 文件总数: {len(oldbak_files)}")

# 2. 查找所有外部→oldbak 的入站引用
print()
print("=" * 70)
print("📊 外部文件引用 oldbak 的入站引用")
print("=" * 70)
cur.execute("""
    SELECT r.source_path, r.target_path, r.source_file_id, r.target_file_id,
           f_source.name AS src_name, f_source.dir AS src_dir,
           f_target.name AS tgt_name
    FROM file_refs r
    JOIN files f_source ON r.source_file_id = f_source.id
    JOIN files f_target ON r.target_file_id = f_target.id
    WHERE r.target_path LIKE '06_others/oldbak%'
      AND r.source_path NOT LIKE '06_others/oldbak%'
    ORDER BY r.target_path, r.source_path
""")
inbound_refs = cur.fetchall()
print(f"  入站引用总数: {len(inbound_refs)}")

# 3. 按被引用的 oldbak 文件分组统计
print()
print("=" * 70)
print("📊 oldbak 文件被外部引用次数（按被引次数排序）")
print("=" * 70)
ref_by_target = defaultdict(list)
for r in inbound_refs:
    ref_by_target[r["target_path"]].append(r["source_path"])

print(f"  {'被引次数':>4}  oldbak 文件")
print(f"  {'-'*4}  {'-'*60}")
for target, sources in sorted(ref_by_target.items(), key=lambda x: -len(x[1])):
    print(f"  {len(sources):>4}  {target}")
    for s in sources[:3]:
        print(f"       ← {s}")
    if len(sources) > 3:
        print(f"       ... 还有 {len(sources)-3} 个引用方")

# 4. 查找 oldbak→oldbak 内部引用
print()
print("=" * 70)
print("📊 oldbak 内部引用（保留不动）")
print("=" * 70)
cur.execute("""
    SELECT COUNT(*) FROM file_refs
    WHERE source_path LIKE '06_others/oldbak%'
      AND target_path LIKE '06_others/oldbak%'
""")
internal = cur.fetchone()[0]
print(f"  内部引用: {internal}")

# 5. 查找 oldbak→外部 出站引用（保留不动）
cur.execute("""
    SELECT COUNT(*) FROM file_refs
    WHERE source_path LIKE '06_others/oldbak%'
      AND target_path NOT LIKE '06_others/oldbak%'
""")
outbound = cur.fetchone()[0]
print(f"  出站引用: {outbound}")

# 6. 查找 oldbak 文件的重复对应文件
print()
print("=" * 70)
print("📊 oldbak → 正式文件 映射表（从相似度表获取）")
print("=" * 70)
cur.execute("""
    SELECT file1_path, file2_path, similarity, relation_type
    FROM similarity
    WHERE (file1_path LIKE '06_others/oldbak%' AND file2_path NOT LIKE '06_others/oldbak%')
       OR (file2_path LIKE '06_others/oldbak%' AND file1_path NOT LIKE '06_others/oldbak%')
    ORDER BY similarity DESC
""")
mapping = {}
for r in cur.fetchall():
    if r["file1_path"].startswith("06_others/oldbak"):
        oldbak_path = r["file1_path"]
        canonical_path = r["file2_path"]
    else:
        oldbak_path = r["file2_path"]
        canonical_path = r["file1_path"]
    if oldbak_path not in mapping or r["similarity"] > mapping[oldbak_path][1]:
        mapping[oldbak_path] = (canonical_path, r["similarity"], r["relation_type"])

print(f"  找到 {len(mapping)} 个 oldbak 文件有对应正式文件:")
print(f"  {'相似度':>6}  oldbak 文件 → 正式文件")
print(f"  {'-'*6}  {'-'*50}")
for oldbak_path in sorted(mapping.keys()):
    canonical, sim, rtype = mapping[oldbak_path]
    print(f"  {sim:>5.0%}  {oldbak_path}")
    print(f"         → {canonical}")

# 7. 统计哪些被引用的 oldbak 文件有对应正式文件，哪些没有
print()
print("=" * 70)
print("📊 被引用 oldbak 文件的可重定向性")
print("=" * 70)
redirectable = 0
not_redirectable = 0
for target_path in ref_by_target:
    if target_path in mapping:
        redirectable += 1
    else:
        not_redirectable += 1
        print(f"  ⚠️ 无对应正式文件: {target_path} (被引{len(ref_by_target[target_path])}次)")
print(f"\n  可重定向: {redirectable} 个 oldbak 文件")
print(f"  无对应文件: {not_redirectable} 个 oldbak 文件")

# 输出映射 JSON 供重定向脚本使用
output = {
    "inbound_refs": [
        {"source": r["source_path"], "target": r["target_path"]}
        for r in inbound_refs
    ],
    "mapping": {
        oldbak: {"canonical": canonical, "similarity": sim, "type": rtype}
        for oldbak, (canonical, sim, rtype) in mapping.items()
    }
}
with open(r"h:\github\cowkb\scripts\indexkb\_oldbak_refs.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\n✅ 映射数据已保存到 _oldbak_refs.json")

conn.close()
