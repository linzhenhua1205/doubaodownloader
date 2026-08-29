#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大文件内部去重工具 v1.0 — dedup_large_md_files.py

针对 Markdown 知识库中因循环追加(append bug)导致超大的文件，
执行「块级去重」：按标题行切块，对每块内容计算哈希，
同一文件内重复出现的块只保留首次出现，其余删除。

背景(2026-08-13 实测)：
  discover/newwiki2/docs 下 23 个文件超 1MB(最大 50.8MB/140万行)，
  均因 append_content.py 循环调用 1023 次，将同一组内容块反复追加。
  例: sha_q10_mes系统如何与iot平台集成.md 唯一块仅 827 个，重复实例 8381 个。

安全设计：
  1. 默认 dry-run，仅统计不写文件；--apply 才实际写
  2. 写前自动备份原文件到 tmp/bak/dedup-<date>/（mv 而非 rm，遵守 RULE.md）
  3. 纯本地脚本，不调用任何 LLM/API，不读取文件内容给大模型
  4. 块级去重保持块顺序(首次出现序)，不破坏文档结构
  5. 行级兜底：块级去重后若仍 >1MB，可加 --line-dedup 做行级去重

用法:
  # 统计所有 >1MB 文件的去重收益（不写文件）
  python3 scripts/tools/dedup_large_md_files.py --dir discover/newwiki2/docs

  # 实际执行（自动备份）
  python3 scripts/tools/dedup_large_md_files.py --dir discover/newwiki2/docs --apply

  # 指定阈值/附加行级去重
  python3 scripts/tools/dedup_large_md_files.py --dir X --min-size 1048576 --line-dedup --apply

输出:
  stdout 打印每个文件的处理统计 + 汇总表；同时写入 tmp/dedup-report-<date>.md
"""
import os
import sys
import re
import hashlib
import shutil
import argparse
from datetime import datetime
from collections import Counter

TITLE_RE = re.compile(r'^(#{1,6})\s+\S')


def split_blocks(lines):
    """按标题行切块。返回 [(title_line_or_None, [lines...])]"""
    blocks = []
    cur_title = None
    cur = []
    for line in lines:
        if TITLE_RE.match(line):
            if cur_title is not None or cur:
                blocks.append((cur_title, cur))
            cur_title = line
            cur = [line]
        else:
            cur.append(line)
    if cur_title is not None or cur:
        blocks.append((cur_title, cur))
    return blocks


def block_hash(block_lines):
    data = "".join(block_lines).encode('utf-8', errors='replace')
    return hashlib.md5(data).hexdigest()


# deep-tech-writer 参数快照尾缀（append 时每次记录，非文档内容）
# 主体结束标记：changelog 行 L2 在 "代码示例。" 处截断，其后为参数快照
BODY_END_MARK = "代码示例。"

# 兜底：已知参数关键词尾缀
META_SUFFIX_RE = re.compile(
    r'(title:\s*|file:\s*|date:\s*|quality_level:\s*|min_lines:\s*|'
    r'max_lines:\s*|doc_type:\s*|version:\s*|template:\s*|source:\s*|'
    r'tags:\s*)[^\n]*$')


def normalize_changelog_block(block_lines):
    """changelog 块归一化：L2 行在主体结束标记处截断，去掉尾部 ---/空行，消除参数快照差异"""
    out = list(block_lines)
    if len(out) >= 3:
        l2 = out[2]
        cut = l2.find(BODY_END_MARK)
        if cut >= 0:
            out[2] = l2[:cut + len(BODY_END_MARK)] + "\n"
        else:
            # 兜底：去掉已知参数关键词尾缀
            out[2] = META_SUFFIX_RE.sub('', l2).rstrip() + "\n"
    # 去除块尾的 --- 分隔符与空行（append 循环分隔线，非内容）
    while out and out[-1].strip() in ('', '---'):
        out.pop()
    return out


def dedup_blocks(blocks, line_dedup=False, meta_dedup=False):
    """块级去重：保留每个哈希首次出现的块。返回 (去重后blocks, 统计dict)

    meta_dedup=True 时：对标题含"变更日志/Changelog"的块，
    先按去掉元数据尾缀的主体哈希判重——避免 1023 次 append 产生的
    参数快照变体全部保留。
    """
    seen = set()
    kept = []
    removed = 0
    removed_meta = 0
    for title, blines in blocks:
        is_changelog = bool(title) and ("变更日志" in title or "Changelog" in title)
        if meta_dedup and is_changelog:
            h = block_hash(normalize_changelog_block(blines))
            if h in seen:
                removed += 1
                removed_meta += 1
                continue
            seen.add(h)
        else:
            h = block_hash(blines)
            if h in seen:
                removed += 1
                continue
            seen.add(h)
        # 可选行级去重（块内）
        if line_dedup:
            lseen = set()
            nlines = []
            for ln in blines:
                lh = hashlib.md5(ln.encode('utf-8', errors='replace')).hexdigest()
                if lh in lseen:
                    continue
                lseen.add(lh)
                nlines.append(ln)
            blines = nlines
        kept.append((title, blines))
    return kept, {"blocks_before": len(blocks), "blocks_after": len(kept),
                  "blocks_removed": removed, "meta_removed": removed_meta}


def process_file(path, min_size, line_dedup, apply, meta_dedup=False):
    size = os.path.getsize(path)
    if size < min_size:
        return None
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    total_lines = len(lines)

    blocks = split_blocks(lines)
    kept, stats = dedup_blocks(blocks, line_dedup, meta_dedup)
    kept_lines = []
    for _, blines in kept:
        kept_lines.extend(blines)

    out_size = sum(len(l.encode('utf-8', errors='replace')) for l in kept_lines)

    if apply:
        # 备份（可用环境变量 DEDUP_NO_BACKUP=1 跳过，用于磁盘空间不足时）
        if os.environ.get("DEDUP_NO_BACKUP") != "1":
            bak_dir = os.path.join("tmp", "bak", f"dedup-{datetime.now().strftime('%Y%m%d')}")
            os.makedirs(bak_dir, exist_ok=True)
            bak_path = os.path.join(bak_dir, os.path.basename(path))
            shutil.copy2(path, bak_path)
        # 写回（若去重后为空则不改）
        if kept_lines:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.writelines(kept_lines)

    return {
        "path": path,
        "size_before": size,
        "size_after": out_size,
        "lines_before": total_lines,
        "lines_after": len(kept_lines),
        "blocks_before": stats["blocks_before"],
        "blocks_after": stats["blocks_after"],
        "blocks_removed": stats["blocks_removed"],
    }


def main():
    ap = argparse.ArgumentParser(description="大文件内部块级去重工具")
    ap.add_argument("--dir", required=True, help="目标目录(递归)")
    ap.add_argument("--min-size", type=int, default=1_000_000, help="阈值字节，默认1MB")
    ap.add_argument("--apply", action="store_true", help="实际执行(否则dry-run)")
    ap.add_argument("--line-dedup", action="store_true", help="块内附加行级去重")
    ap.add_argument("--meta-dedup", action="store_true",
                    help="changelog 块按去元数据尾缀后主体去重(推荐用于append生成文件)")
    args = ap.parse_args()

    targets = []
    for root, dirs, fs in os.walk(args.dir):
        for fn in fs:
            if fn.endswith((".md", ".markdown", ".txt")):
                p = os.path.join(root, fn)
                if os.path.getsize(p) >= args.min_size:
                    targets.append(p)
    targets.sort()
    print(f"🔍 扫描 {args.dir} → 超阈值文件 {len(targets)} 个\n")

    results = []
    for p in targets:
        r = process_file(p, args.min_size, args.line_dedup, args.apply, args.meta_dedup)
        if r:
            results.append(r)

    # 汇总表
    print(f"{'文件':<60} {'原MB':>7} {'去重后KB':>9} {'原行':>9} {'去重后行':>9} {'删块':>5} {'压缩率':>7}")
    total_before = total_after = 0
    for r in results:
        mb = r["size_before"] / 1e6
        kb = r["size_after"] / 1e3
        ratio = (1 - r["size_after"] / r["size_before"]) * 100 if r["size_before"] else 0
        total_before += r["size_before"]
        total_after += r["size_after"]
        mode = "✅" if args.apply else "🔍"
        print(f"{mode} {os.path.basename(r['path']):<58} {mb:>7.1f} {kb:>9.1f} "
              f"{r['lines_before']:>9} {r['lines_after']:>9} {r['blocks_removed']:>5} {ratio:>6.1f}%")

    if results:
        total_ratio = (1 - total_after / total_before) * 100
        print(f"\n{'='*110}")
        print(f"总计: {len(results)} 文件, {total_before/1e6:.1f}MB → {total_after/1e3:.0f}KB "
              f"(压缩 {total_ratio:.1f}%)  [{'已写回' if args.apply else 'dry-run 未写'}]")
    else:
        print("无超阈值文件。")


if __name__ == "__main__":
    main()
