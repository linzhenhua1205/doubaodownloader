#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库 SQLite 查询工具 (Knowledge Base Query Tool)
====================================================

对 knowledge_graph.db 进行多维度查询，全面表达文件间关系。

用法：
  python db_query.py file <路径或文件名>       # 查询文件详情+引用+相似
  python db_query.py refs <路径或文件名>        # 查询引用关系（出站+入站）
  python db_query.py similar <路径或文件名>     # 查询相似/重复文件
  python db_query.py keyword <关键词>           # 按关键词查文件
  python db_query.py hub [--top N]              # 核心枢纽文件（被引用最多）
  python db_query.py dup [--top N]              # 高度重复文件对
  python db_query.py dir <目录路径>             # 目录内文件列表+关系
  python db_query.py cross <目录1> <目录2>      # 跨目录关联文件
  python db_query.py stats                      # 数据库统计
  python db_query.py export <输出文件>          # 导出全量关系为 Markdown
"""

import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT

DB_PATH = str(WORKSPACE_ROOT / "scripts" / "indexkb" / "knowledge_graph.db")
KNOWLEDGE_ROOT = str(KNOWLEDGE_ROOT)


def get_conn():
    if not Path(DB_PATH).exists():
        print(f"❌ 数据库不存在: {DB_PATH}")
        print("   请先运行: python db_builder.py")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def find_file_id(cur, name_or_path: str) -> int:
    """通过路径或文件名模糊查找文件 ID"""
    name_or_path = name_or_path.replace("\\", "/").strip("/")

    # 精确路径
    cur.execute("SELECT id FROM files WHERE path = ?", (name_or_path,))
    row = cur.fetchone()
    if row:
        return row["id"]

    # 以路径结尾
    cur.execute("SELECT id FROM files WHERE path LIKE ?", (f"%{name_or_path}",))
    row = cur.fetchone()
    if row:
        return row["id"]

    # 文件名匹配
    cur.execute("SELECT id FROM files WHERE name = ? OR filename = ?",
                (name_or_path, name_or_path))
    row = cur.fetchone()
    if row:
        return row["id"]

    # 文件名模糊
    cur.execute("SELECT id, path FROM files WHERE name LIKE ? OR path LIKE ?",
                (f"%{name_or_path}%", f"%{name_or_path}%"))
    rows = cur.fetchall()
    if len(rows) == 1:
        return rows[0]["id"]
    elif len(rows) > 1:
        print(f"⚠️  匹配到 {len(rows)} 个文件，请更精确指定:")
        for r in rows[:10]:
            print(f"   - {r['path']}")
        if len(rows) > 10:
            print(f"   ... 还有 {len(rows)-10} 个")
        return None

    print(f"❌ 未找到文件: {name_or_path}")
    return None


def fmt_size_level(level):
    return {"giant": "📕巨篇", "long": "📗长文",
            "medium": "📘中篇", "short": "📙短篇"}.get(level, level)


def cmd_file(cur, args):
    """查询文件详情 + 引用 + 相似"""
    fid = find_file_id(cur, args.target)
    if fid is None:
        return

    # 文件详情
    cur.execute("SELECT * FROM files WHERE id = ?", (fid,))
    f = cur.fetchone()
    if not f:
        print("❌ 文件不存在")
        return

    print("=" * 70)
    print(f"📄 {f['name']}")
    print("=" * 70)
    print(f"  路径:     {f['path']}")
    print(f"  目录:     {f['dir']}")
    print(f"  规模:     {fmt_size_level(f['size_level'])}（约 {f['word_count']:,} 字）")
    print(f"  概要:     {f['summary']}")

    headings = json.loads(f["headings"]) if f["headings"] else []
    if headings:
        print(f"  标题结构: {' → '.join(headings[:5])}")

    # 关键词
    cur.execute("""
        SELECT keyword, frequency, rank FROM keywords
        WHERE file_id = ? ORDER BY rank
    """, (fid,))
    kws = cur.fetchall()
    if kws:
        print(f"\n  🔑 关键词 ({len(kws)} 个):")
        for kw in kws[:10]:
            print(f"     {kw['rank']:>2}. {kw['keyword']} (freq={kw['frequency']})")

    # 引用关系
    cur.execute("""
        SELECT target_path FROM file_refs WHERE source_file_id = ?
    """, (fid,))
    out_refs = [r["target_path"] for r in cur.fetchall()]

    cur.execute("""
        SELECT source_path FROM file_refs WHERE target_file_id = ?
    """, (fid,))
    in_refs = [r["source_path"] for r in cur.fetchall()]

    print(f"\n  🔗 引用关系:")
    print(f"     📤 引用了 {len(out_refs)} 个文件:")
    for p in out_refs[:10]:
        print(f"        → {p}")
    if len(out_refs) > 10:
        print(f"        ... 还有 {len(out_refs)-10} 个")

    print(f"     📥 被引用 {len(in_refs)} 次:")
    for p in in_refs[:10]:
        print(f"        ← {p}")
    if len(in_refs) > 10:
        print(f"        ... 还有 {len(in_refs)-10} 个")

    # 相似度
    cur.execute("""
        SELECT file1_id, file2_id, file1_path, file2_path, similarity,
               overlap_keywords, same_dir, relation_type
        FROM similarity
        WHERE file1_id = ? OR file2_id = ?
        ORDER BY similarity DESC
    """, (fid, fid))
    sims = cur.fetchall()

    if sims:
        print(f"\n  📐 相似文件 ({len(sims)} 个):")
        for s in sims[:15]:
            other = s["file2_path"] if s["file1_id"] == fid else s["file1_path"]
            overlap = json.loads(s["overlap_keywords"]) if s["overlap_keywords"] else []
            loc = "同目录" if s["same_dir"] else "跨目录"
            rtype = {"duplicate": "🔴重复",
                     "complementary": "🟡互补",
                     "related": "🟢相关"}.get(s["relation_type"], "")
            print(f"     {rtype} {s['similarity']:.0%} [{loc}] {other}")
            if overlap:
                print(f"            共同: {', '.join(overlap[:5])}")
    else:
        print(f"\n  📐 相似文件: 无")

    print()


def cmd_refs(cur, args):
    """仅查询引用关系"""
    fid = find_file_id(cur, args.target)
    if fid is None:
        return

    cur.execute("SELECT path FROM files WHERE id = ?", (fid,))
    f = cur.fetchone()
    print(f"\n🔗 引用关系: {f['path']}\n")

    # 出站
    cur.execute("""
        SELECT r.target_path, f.name, f.dir, f.word_count
        FROM file_refs r
        JOIN files f ON r.target_file_id = f.id
        WHERE r.source_file_id = ?
        ORDER BY f.word_count DESC
    """, (fid,))
    out = cur.fetchall()
    print(f"📤 引用了 {len(out)} 个文件:")
    for r in out:
        print(f"   → [{r['dir']}] {r['name']} ({r['word_count']:,}字)")

    # 入站
    cur.execute("""
        SELECT r.source_path, f.name, f.dir, f.word_count
        FROM file_refs r
        JOIN files f ON r.source_file_id = f.id
        WHERE r.target_file_id = ?
        ORDER BY f.word_count DESC
    """, (fid,))
    inc = cur.fetchall()
    print(f"\n📥 被引用 {len(inc)} 次:")
    for r in inc:
        print(f"   ← [{r['dir']}] {r['name']} ({r['word_count']:,}字)")
    print()


def cmd_similar(cur, args):
    """查询相似/重复文件"""
    fid = find_file_id(cur, args.target)
    if fid is None:
        return

    cur.execute("SELECT path, name, dir FROM files WHERE id = ?", (fid,))
    f = cur.fetchone()
    print(f"\n📐 相似文件: {f['path']}\n")

    cur.execute("""
        SELECT file1_id, file2_id, file1_path, file2_path, similarity,
               overlap_keywords, same_dir, relation_type
        FROM similarity
        WHERE file1_id = ? OR file2_id = ?
        ORDER BY similarity DESC
    """, (fid, fid))
    sims = cur.fetchall()

    if not sims:
        print("  无相似文件")
        return

    for s in sims:
        other_path = s["file2_path"] if s["file1_id"] == fid else s["file1_path"]
        other_name = Path(other_path).stem
        overlap = json.loads(s["overlap_keywords"]) if s["overlap_keywords"] else []
        loc = "同目录" if s["same_dir"] else "跨目录"
        rtype = {"duplicate": "🔴高度重复",
                 "complementary": "🟡互补",
                 "related": "🟢相关"}.get(s["relation_type"], "")

        print(f"  {rtype} {s['similarity']:.0%} [{loc}]")
        print(f"     文件: {other_path}")
        if overlap:
            print(f"     共同关键词: {', '.join(overlap)}")
        print()


def cmd_keyword(cur, args):
    """按关键词查文件"""
    kw = args.keyword
    print(f"\n🏷️  关键词 '{kw}' 的文件列表\n")

    cur.execute("""
        SELECT f.path, f.name, f.dir, f.word_count, k.frequency, k.rank
        FROM keywords k
        JOIN files f ON k.file_id = f.id
        WHERE k.keyword = ?
        ORDER BY k.frequency DESC
    """, (kw,))
    rows = cur.fetchall()

    if not rows:
        # 模糊匹配
        cur.execute("""
            SELECT DISTINCT k.keyword, COUNT(*) as cnt
            FROM keywords k
            WHERE k.keyword LIKE ?
            GROUP BY k.keyword
            ORDER BY cnt DESC
            LIMIT 10
        """, (f"%{kw}%",))
        suggestions = cur.fetchall()
        print(f"  未找到精确匹配。相似关键词:")
        for s in suggestions:
            print(f"     {s['keyword']} ({s['cnt']}个文件)")
        return

    print(f"  共 {len(rows)} 个文件包含此关键词:\n")
    print(f"  {'#':>3}  {'频率':>4}  {'排名':>4}  {'字数':>7}  目录/文件")
    print(f"  {'-'*3}  {'-'*4}  {'-'*4}  {'-'*7}  {'-'*40}")
    for i, r in enumerate(rows, 1):
        print(f"  {i:>3}  {r['frequency']:>4}  {r['rank']:>4}  {r['word_count']:>7,}  [{r['dir']}] {r['name']}")
    print()


def cmd_hub(cur, args):
    """核心枢纽文件"""
    top = args.top or 20
    print(f"\n🔗 核心枢纽文件 Top {top}（被引用最多）\n")

    cur.execute("""
        SELECT f.path, f.name, f.dir,
               COALESCE(b.backlink_count, 0) AS bc,
               COALESCE(o.outlink_count, 0) AS oc
        FROM files f
        LEFT JOIN v_backlinks b ON f.id = b.file_id
        LEFT JOIN v_outlinks o ON f.id = o.file_id
        ORDER BY bc DESC
        LIMIT ?
    """, (top,))
    rows = cur.fetchall()

    print(f"  {'#':>3}  {'被引':>4}  {'引用':>4}  目录/文件")
    print(f"  {'-'*3}  {'-'*4}  {'-'*4}  {'-'*50}")
    for i, r in enumerate(rows, 1):
        print(f"  {i:>3}  {r['bc']:>4}  {r['oc']:>4}  [{r['dir']}] {r['name']}")
    print()


def cmd_dup(cur, args):
    """高度重复文件对"""
    top = args.top or 20
    print(f"\n🔴 高度重复文件对 Top {top}\n")

    cur.execute("""
        SELECT file1_path, file2_path, similarity, overlap_keywords,
               same_dir, relation_type
        FROM similarity
        WHERE relation_type = 'duplicate'
        ORDER BY similarity DESC
        LIMIT ?
    """, (top,))
    rows = cur.fetchall()

    if not rows:
        print("  无高度重复文件")
        return

    print(f"  {'相似度':>6}  {'位置':>4}  文件A ↔ 文件B")
    print(f"  {'-'*6}  {'-'*4}  {'-'*60}")
    for r in rows:
        loc = "同目录" if r["same_dir"] else "跨目录"
        overlap = json.loads(r["overlap_keywords"]) if r["overlap_keywords"] else []
        print(f"  {r['similarity']:>5.0%}  {loc:>4}  {r['file1_path']}")
        print(f"  {'':>6}  {'':>4}  ↔ {r['file2_path']}")
        if overlap:
            print(f"  {'':>6}  {'':>4}  共同: {', '.join(overlap[:5])}")
        print()


def cmd_dir(cur, args):
    """目录内文件列表"""
    d = args.directory.replace("\\", "/").strip("/")
    print(f"\n📂 目录: {d}\n")

    cur.execute("""
        SELECT path, name, word_count, size_level, summary
        FROM files
        WHERE dir = ?
        ORDER BY word_count DESC
    """, (d,))
    rows = cur.fetchall()

    if not rows:
        print(f"  目录不存在或无文件: {d}")
        return

    # 目录统计
    cur.execute("""
        SELECT file_count, total_words FROM directories WHERE path = ?
    """, (d,))
    stat = cur.fetchone()
    if stat:
        print(f"  文件数: {stat['file_count']}  总字数: {stat['total_words']:,}")
    print()

    for i, r in enumerate(rows, 1):
        print(f"  {i:>3}. {fmt_size_level(r['size_level'])} {r['name']} ({r['word_count']:,}字)")
        print(f"       概要: {r['summary']}")

    # 目录内相似对
    cur.execute("""
        SELECT file1_path, file2_path, similarity, overlap_keywords, relation_type
        FROM similarity
        WHERE same_dir = 1
          AND file1_path LIKE ?
          AND file2_path LIKE ?
        ORDER BY similarity DESC
        LIMIT 10
    """, (f"{d}/%", f"{d}/%"))
    sims = cur.fetchall()
    if sims:
        print(f"\n  📐 目录内相似文件对:")
        for s in sims:
            n1 = Path(s["file1_path"]).name
            n2 = Path(s["file2_path"]).name
            rtype = {"duplicate": "🔴", "complementary": "🟡",
                     "related": "🟢"}.get(s["relation_type"], "")
            print(f"     {rtype} {s['similarity']:.0%} {n1} ↔ {n2}")
    print()


def cmd_cross(cur, args):
    """跨目录关联"""
    d1 = args.dir1.replace("\\", "/").strip("/")
    d2 = args.dir2.replace("\\", "/").strip("/")
    print(f"\n🌐 跨目录关联: {d1} ↔ {d2}\n")

    cur.execute("""
        SELECT s.file1_path, s.file2_path, s.similarity,
               s.overlap_keywords, s.relation_type
        FROM similarity s
        WHERE s.same_dir = 0
          AND (
            (s.file1_path LIKE ? AND s.file2_path LIKE ?)
            OR
            (s.file1_path LIKE ? AND s.file2_path LIKE ?)
          )
        ORDER BY s.similarity DESC
        LIMIT 30
    """, (f"{d1}/%", f"{d2}/%", f"{d2}/%", f"{d1}/%"))
    rows = cur.fetchall()

    if not rows:
        print("  无跨目录关联文件")
        return

    print(f"  共 {len(rows)} 对关联:\n")
    for s in rows:
        n1 = Path(s["file1_path"]).name
        n2 = Path(s["file2_path"]).name
        overlap = json.loads(s["overlap_keywords"]) if s["overlap_keywords"] else []
        rtype = {"duplicate": "🔴重复", "complementary": "🟡互补",
                 "related": "🟢相关"}.get(s["relation_type"], "")
        print(f"  {rtype} {s['similarity']:.0%}")
        print(f"     {n1} ({s['file1_path']})")
        print(f"     ↔ {n2} ({s['file2_path']})")
        if overlap:
            print(f"     共同: {', '.join(overlap[:5])}")
        print()


def cmd_stats(cur):
    """数据库统计"""
    print("=" * 60)
    print("📊 数据库统计")
    print("=" * 60)

    for table in ["files", "directories", "keywords", "file_refs", "similarity"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table:15s}: {cur.fetchone()[0]:>6}")

    print()
    cur.execute("""
        SELECT relation_type, COUNT(*) FROM similarity
        GROUP BY relation_type ORDER BY COUNT(*) DESC
    """)
    print("  相似度分布:")
    for rtype, cnt in cur.fetchall():
        label = {"duplicate": "🔴 高度重复", "complementary": "🟡 互补",
                 "related": "🟢 相关"}.get(rtype, rtype)
        print(f"     {label}: {cnt}")

    print()
    cur.execute("""
        SELECT COUNT(*) FROM files
        WHERE id NOT IN (SELECT DISTINCT target_file_id FROM file_refs)
    """)
    orphan = cur.fetchone()[0]
    print(f"  未被任何文件引用的文件: {orphan}")

    cur.execute("""
        SELECT COUNT(*) FROM files
        WHERE id NOT IN (SELECT DISTINCT source_file_id FROM file_refs)
    """)
    no_out = cur.fetchone()[0]
    print(f"  不引用任何文件的文件:   {no_out}")


def cmd_export(cur, args):
    """导出全量关系为 Markdown"""
    out_path = args.output
    print(f"导出到: {out_path}")

    lines = ["# 知识库关系全量导出\n"]
    lines.append(f"> 生成时间: {__import__('datetime').datetime.now().isoformat()}\n")

    # 文件列表
    lines.append("## 文件列表\n")
    lines.append("| # | 路径 | 目录 | 字数 | 规模 | 概要 |")
    lines.append("|:--|:-----|:-----|-----:|:-----|:-----|")
    cur.execute("SELECT * FROM files ORDER BY dir, name")
    for i, f in enumerate(cur.fetchall(), 1):
        lines.append(f"| {i} | {f['path']} | {f['dir']} | {f['word_count']:,} | "
                      f"{fmt_size_level(f['size_level'])} | {f['summary'][:40]} |")
    lines.append("")

    # 引用关系
    lines.append("## 引用关系\n")
    lines.append("| 源文件 | 目标文件 |")
    lines.append("|:-------|:---------|")
    cur.execute("SELECT source_path, target_path FROM file_refs ORDER BY source_path")
    for r in cur.fetchall():
        lines.append(f"| {r['source_path']} | {r['target_path']} |")
    lines.append("")

    # 相似度
    lines.append("## 相似度关系\n")
    lines.append("| 文件A | 文件B | 相似度 | 关系类型 | 共同关键词 |")
    lines.append("|:------|:------|:------:|:---------|:-----------|")
    cur.execute("""
        SELECT file1_path, file2_path, similarity, overlap_keywords, relation_type
        FROM similarity ORDER BY similarity DESC
    """)
    for s in cur.fetchall():
        overlap = json.loads(s["overlap_keywords"]) if s["overlap_keywords"] else []
        lines.append(f"| {s['file1_path']} | {s['file2_path']} | "
                      f"{s['similarity']:.0%} | {s['relation_type']} | "
                      f"{', '.join(overlap[:4])} |")
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ 已导出: {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="知识库 SQLite 查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
查询示例:
  python db_query.py file 02_rd/03_hardware/05_AIServer/nvidia-gb200-nvl72.md
  python db_query.py refs deepseek
  python db_query.py similar moe
  python db_query.py keyword GPU
  python db_query.py hub --top 10
  python db_query.py dup
  python db_query.py dir 02_rd/03_hardware/05_AIServer
  python db_query.py cross 02_rd/03_hardware/05_AIServer 03_AI/agent-engineering
  python db_query.py stats
  python db_query.py export relations.md
""")

    sub = parser.add_subparsers(dest="command", help="查询命令")

    p_file = sub.add_parser("file", help="查询文件详情+引用+相似")
    p_file.add_argument("target", help="文件路径或名称")

    p_refs = sub.add_parser("refs", help="查询引用关系")
    p_refs.add_argument("target", help="文件路径或名称")

    p_sim = sub.add_parser("similar", help="查询相似/重复文件")
    p_sim.add_argument("target", help="文件路径或名称")

    p_kw = sub.add_parser("keyword", help="按关键词查文件")
    p_kw.add_argument("keyword", help="关键词")

    p_hub = sub.add_parser("hub", help="核心枢纽文件")
    p_hub.add_argument("--top", type=int, default=20, help="显示数量")

    p_dup = sub.add_parser("dup", help="高度重复文件对")
    p_dup.add_argument("--top", type=int, default=20, help="显示数量")

    p_dir = sub.add_parser("dir", help="目录内文件列表")
    p_dir.add_argument("directory", help="目录路径")

    p_cross = sub.add_parser("cross", help="跨目录关联")
    p_cross.add_argument("dir1", help="目录1")
    p_cross.add_argument("dir2", help="目录2")

    p_stats = sub.add_parser("stats", help="数据库统计")

    p_export = sub.add_parser("export", help="导出全量关系")
    p_export.add_argument("output", help="输出文件路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_conn()
    cur = conn.cursor()

    if args.command == "file":
        cmd_file(cur, args)
    elif args.command == "refs":
        cmd_refs(cur, args)
    elif args.command == "similar":
        cmd_similar(cur, args)
    elif args.command == "keyword":
        cmd_keyword(cur, args)
    elif args.command == "hub":
        cmd_hub(cur, args)
    elif args.command == "dup":
        cmd_dup(cur, args)
    elif args.command == "dir":
        cmd_dir(cur, args)
    elif args.command == "cross":
        cmd_cross(cur, args)
    elif args.command == "stats":
        cmd_stats(cur)
    elif args.command == "export":
        cmd_export(cur, args)

    conn.close()


if __name__ == "__main__":
    main()
