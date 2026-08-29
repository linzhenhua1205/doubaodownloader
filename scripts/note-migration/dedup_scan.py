#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dedup_scan.py — 迁移后去重扫描

对暂存区 (import/migration/) 的 Markdown 做重复检测:
  1. 标题归一化相似 (去掉标点/空格/日期前缀)
  2. 内容哈希 + 两两相似度 (difflib SequenceMatcher)

策略: 相似度 >= 0.8 只标记不删除, 输出候选清单, 人工确认。

用法:
  python3 dedup_scan.py <目录> [--threshold 0.8] [--csv out.csv]

纯标准库。
"""
import argparse
import hashlib
import os
import re
import sys
from difflib import SequenceMatcher


def norm_title(s: str) -> str:
    """标题归一化: 去标点/空白/常见前缀"""
    s = s.strip().lower()
    s = re.sub(r"^\d{4}-\d{2}-\d{2}[-_]", "", s)   # 日期前缀
    s = re.sub(r"[\W_]+", "", s)                    # 非字母数字
    return s


def content_hash(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def load_md_files(root: str):
    """读取目录下所有 .md, 返回 [(path, title, body, hash)]"""
    result = []
    for dirpath, _, filenames in os.walk(root):
        for fn in sorted(filenames):
            if not fn.lower().endswith(".md"):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, encoding="utf-8") as f:
                    text = f.read()
            except (OSError, UnicodeDecodeError) as e:
                print(f"⚠️ 跳过 {fp}: {e}")
                continue
            # 标题 = 第一个 # 行或文件名
            m = re.search(r"^#\s+(.+)$", text, re.M)
            title = m.group(1).strip() if m else fn
            body = text
            result.append({"path": fp, "title": title,
                           "norm": norm_title(title),
                           "hash": content_hash(body), "body": body})
    return result


def main():
    ap = argparse.ArgumentParser(description="Markdown 去重扫描")
    ap.add_argument("root", help="要扫描的目录")
    ap.add_argument("--threshold", type=float, default=0.8,
                    help="相似度阈值 (默认 0.8, 只标记不删)")
    ap.add_argument("--csv", help="输出候选清单 CSV")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"❌ 目录不存在: {args.root}")
        sys.exit(1)

    print(f"🔍 扫描: {args.root}")
    docs = load_md_files(args.root)
    print(f"📄 共 {len(docs)} 个 Markdown 文件")

    # 1. 完全相同 (hash 一致)
    hash_groups = {}
    for d in docs:
        hash_groups.setdefault(d["hash"], []).append(d["path"])
    exact_dups = [g for g in hash_groups.values() if len(g) > 1]

    # 2. 标题相同
    title_groups = {}
    for d in docs:
        if d["norm"]:
            title_groups.setdefault(d["norm"], []).append(d["path"])
    title_dups = [g for g in title_groups.values() if len(g) > 1]

    # 3. 内容相似 (抽样对比, 避免 O(n²) 爆炸: 最多 500 篇互比)
    similar = []
    n = len(docs)
    if n <= 500:
        for i in range(n):
            for j in range(i + 1, n):
                a, b = docs[i], docs[j]
                if a["hash"] == b["hash"]:
                    continue
                short_a = a["body"][:2000]
                short_b = b["body"][:2000]
                ratio = SequenceMatcher(None, short_a, short_b).ratio()
                if ratio >= args.threshold:
                    similar.append((round(ratio, 3), a["path"], b["path"]))

    print(f"\n{'=' * 60}")
    print(f"🔴 完全相同: {len(exact_dups)} 组")
    for g in exact_dups[:10]:
        print(f"   - {g[0]}")
        for p in g[1:]:
            print(f"     = {p}")

    print(f"\n🟠 标题相同: {len(title_dups)} 组")
    for g in title_dups[:10]:
        print(f"   - {g[0]}")
        for p in g[1:]:
            print(f"     ≈ {p}")

    print(f"\n🟡 内容相似 (>= {args.threshold}): {len(similar)} 对")
    for ratio, p1, p2 in sorted(similar, reverse=True)[:20]:
        print(f"   {ratio:.2f}  {p1}")
        print(f"         {p2}")

    if args.csv:
        with open(args.csv, "w", encoding="utf-8") as fp:
            fp.write("type,score,path_a,path_b\n")
            for g in exact_dups:
                for p in g[1:]:
                    fp.write(f"exact,1.0,{g[0]},{p}\n")
            for g in title_dups:
                for p in g[1:]:
                    fp.write(f"title,1.0,{g[0]},{p}\n")
            for ratio, p1, p2 in similar:
                fp.write(f"similar,{ratio},{p1},{p2}\n")
        print(f"\n📄 候选清单已存: {args.csv}")

    print("\n⚠️ 提示: 以上仅标记, 未删除任何文件。去重合并请人工确认后再操作。")


if __name__ == "__main__":
    main()
