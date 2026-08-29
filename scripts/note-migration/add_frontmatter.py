#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""add_frontmatter.py — 批量给迁移的 Markdown 补 frontmatter

为暂存区每个 .md 文件头部插入 YAML frontmatter, 记录来源/迁移信息:
  ---
  source: <源名>            # one of: markdown/xml/xmind/freemind/onenote/feishu/ai-doc/dedao/paper
  original_path: <原始路径>
  migrated: <日期>
  value: <A|B|C|D>          # 价值分级 (人工后续修改)
  ---

已带 frontmatter 的文件自动跳过。

用法:
  python3 add_frontmatter.py <目录> --source onenote
  python3 add_frontmatter.py <目录> --source xmind --dry-run

纯标准库。
"""
import argparse
import os
import sys
from datetime import date

SOURCES = {"markdown", "xml", "xmind", "freemind", "onenote",
           "feishu", "ai-doc", "dedao", "paper"}


def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n")


def add_fm(path: str, source: str, dry: bool):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if has_frontmatter(text):
        return "skip"
    rel = os.path.relpath(path)
    fm = (f"---\nsource: {source}\n"
          f"original_path: {rel}\n"
          f"migrated: {date.today().isoformat()}\n"
          f"value: null  # TODO: A/B/C/D 人工分级\n"
          f"---\n\n")
    if not dry:
        with open(path, "w", encoding="utf-8") as f:
            f.write(fm + text)
    return "add"


def main():
    ap = argparse.ArgumentParser(description="批量补 frontmatter")
    ap.add_argument("root", help="目标目录 (递归)")
    ap.add_argument("--source", required=True, choices=sorted(SOURCES),
                    help="来源标识")
    ap.add_argument("--dry-run", action="store_true", help="只预览不写入")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"❌ 目录不存在: {args.root}")
        sys.exit(1)

    added = skipped = 0
    for dirpath, _, filenames in os.walk(args.root):
        for fn in sorted(filenames):
            if not fn.lower().endswith(".md"):
                continue
            fp = os.path.join(dirpath, fn)
            r = add_fm(fp, args.source, args.dry_run)
            if r == "add":
                added += 1
                print(f"{'[预览] ' if args.dry_run else ''}➕ {fp}")
            else:
                skipped += 1
    print(f"\n{'[dry-run] 将添加 ' if args.dry_run else '完成: 添加 '}{added} 个, "
          f"跳过(已有 frontmatter) {skipped} 个")


if __name__ == "__main__":
    main()
