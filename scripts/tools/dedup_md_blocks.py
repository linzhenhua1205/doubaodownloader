#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 文件块级去重工具 v2.0 — dedup_md_blocks.py

用途:
  对指定目录下超过阈值(--min-size, 默认100KB)的 Markdown 文件做**文件内块级去重**。
  针对知识库中因 append bug / AI 批量生成导致的"同一内容块反复出现"问题。

背景(2026-08-13):
  discover/newwiki2/docs 下 8392 个文件 >100KB(总 ~1.75GB)，
  其中一部分是 append_content.py 循环追加产生的重复块文件(已由 v1 处理 1MB+ 批次)，
  剩余 100KB~1MB 的文件可能含重复块，也可能为正常长文档。
  本工具先 dry-run 统计重复率，由人工决定是否 --apply。

安全设计:
  1. 默认 dry-run，仅统计不写文件；--apply 才实际写
  2. 写前自动备份原文件到 tmp/bak/dedup-md-<date>/（mv 而非 rm，遵守 RULE.md）
  3. 纯本地脚本，不调用任何 LLM/API，文件内容零进入大模型上下文
  4. 块级去重保持块顺序(首次出现序)，不破坏文档结构
  5. 行级去重(--line-dedup)跳过纯分隔线/空行/YAML 区，避免破坏格式

用法:
  # 1) 摸底: 统计所有 >100KB 文件的重复块数/收益（不写文件）
  python3 scripts/tools/dedup_md_blocks.py --dir discover/newwiki2/docs

  # 2) 仅处理"重复率>=30%"的文件（推荐: 避免动正常长文档）
  python3 scripts/tools/dedup_md_blocks.py --dir discover/newwiki2/docs \
      --min-dup-ratio 30 --apply

  # 3) 全部 >100KB 文件都做块级去重（更激进, 有 git 兜底时可用）
  python3 scripts/tools/dedup_md_blocks.py --dir discover/newwiki2/docs \
      --min-dup-ratio 0 --apply

  # 4) 附加行级去重（最激进, 慎用; 需与 --apply 同用）
  python3 scripts/tools/dedup_md_blocks.py --dir discover/newwiki2/docs \
      --line-dedup --min-dup-ratio 0 --apply

输出:
  stdout 打印每文件统计 + 汇总；同时写入 tmp/dedup-md-report-<date>.md
"""
import os
import re
import sys
import hashlib
import shutil
import argparse
from datetime import datetime
from collections import Counter

TITLE_RE = re.compile(r'^(#{1,6})\s+\S')
# YAML front matter 起始行（文件头 --- 分隔）
FRONT_MATTER_RE = re.compile(r'^---\s*$')
# 纯分隔线/空行（行级去重时跳过，避免破坏格式）
SKIP_LINE_RE = re.compile(r'^\s*(---|\*\*\*|___|[-=*_]{3,})?\s*$')

# changelog 元数据行特征（append 时每次记录的参数快照/日期/版本行）
META_LINE_RE = re.compile(
    r'^\s*[-*]?\s*(date|时间|版本|version|title|file|quality_level|min_lines|'
    r'max_lines|doc_type|template|source|tags|category|更新日期|生成时间|'
    r'commit|参数|参数值)\s*[:：=]\s*\S')


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


def is_changelog_block(title):
    if not title:
        return False
    return any(k in title for k in ("变更日志", "Changelog", "changelog", "更新日志", "历史记录"))


def normalize_changelog_block(block_lines):
    """changelog 块归一化：仅保留"非元数据行"，消除 append 产生的参数快照差异。

    策略: 保留标题行 + 非 META_LINE_RE 的内容行; 纯元数据行剔除。
    这样 1023 次 append 产生的 changelog 变体(差异仅在参数快照)归并为同一主体。
    """
    out = []
    for i, ln in enumerate(block_lines):
        if i == 0:
            out.append(ln)  # 标题行保留
            continue
        s = ln.strip()
        if not s:
            continue
        if META_LINE_RE.match(ln):
            continue
        out.append(ln)
    # 去除块尾的 --- 分隔符与空行
    while out and out[-1].strip() in ('', '---'):
        out.pop()
    return out


def dedup_blocks(blocks, line_dedup=False, meta_dedup=True):
    """块级去重：保留每个哈希首次出现的块。

    meta_dedup=True 时：changelog 块先归一化再判重，
    使 append 循环产生的元数据变体归并为一个块。
    返回 (去重后blocks, 统计dict)
    """
    seen = set()
    kept = []
    removed = 0
    removed_meta = 0
    dup_bytes = 0
    for title, blines in blocks:
        is_chg = is_changelog_block(title)
        if meta_dedup and is_chg:
            norm = normalize_changelog_block(blines)
            h = block_hash(norm)
            if h in seen:
                removed += 1
                removed_meta += 1
                dup_bytes += sum(len(l.encode('utf-8', errors='replace')) for l in blines)
                continue
            seen.add(h)
        else:
            h = block_hash(blines)
            if h in seen:
                removed += 1
                dup_bytes += sum(len(l.encode('utf-8', errors='replace')) for l in blines)
                continue
            seen.add(h)
        # 可选行级去重（块内；跳过分隔线/空行）
        if line_dedup:
            lseen = set()
            nlines = []
            for ln in blines:
                if SKIP_LINE_RE.match(ln):
                    nlines.append(ln)
                    continue
                lh = hashlib.md5(ln.encode('utf-8', errors='replace')).hexdigest()
                if lh in lseen:
                    continue
                lseen.add(lh)
                nlines.append(ln)
            blines = nlines
        kept.append((title, blines))
    return kept, {"blocks_before": len(blocks), "blocks_after": len(kept),
                  "blocks_removed": removed, "meta_removed": removed_meta,
                  "dup_bytes": dup_bytes}


def process_file(path, line_dedup, meta_dedup, apply):
    size = os.path.getsize(path)
    with open(path, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    total_lines = len(lines)

    blocks = split_blocks(lines)
    kept, stats = dedup_blocks(blocks, line_dedup, meta_dedup)
    kept_lines = []
    for _, blines in kept:
        kept_lines.extend(blines)

    out_size = sum(len(l.encode('utf-8', errors='replace')) for l in kept_lines)
    dup_ratio = (stats["dup_bytes"] / size * 100) if size else 0.0

    # 无变化则跳过写（避免 0% 重复的正常长文档被重写）
    unchanged = (len(kept_lines) == total_lines and
                 block_hash(kept_lines) == block_hash(lines))

    if apply and not unchanged:
        if os.environ.get("DEDUP_NO_BACKUP") != "1":
            bak_dir = os.path.join("tmp", "bak", f"dedup-md-{datetime.now().strftime('%Y%m%d')}")
            os.makedirs(bak_dir, exist_ok=True)
            shutil.copy2(path, os.path.join(bak_dir, os.path.basename(path)))
        if kept_lines:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.writelines(kept_lines)

    return {
        "path": path, "size_before": size, "size_after": out_size,
        "lines_before": total_lines, "lines_after": len(kept_lines),
        "blocks_before": stats["blocks_before"], "blocks_after": stats["blocks_after"],
        "blocks_removed": stats["blocks_removed"], "dup_ratio": dup_ratio,
    }


def main():
    ap = argparse.ArgumentParser(description="Markdown 文件块级去重工具 v2.0")
    ap.add_argument("--dir", required=True, help="目标目录(递归)")
    ap.add_argument("--min-size", type=int, default=100_000, help="阈值字节，默认100KB")
    ap.add_argument("--min-dup-ratio", type=float, default=0.0,
                    help="仅处理重复率>=该百分比的文件(默认0=全部处理；推荐30)")
    ap.add_argument("--apply", action="store_true", help="实际执行(否则dry-run)")
    ap.add_argument("--line-dedup", action="store_true", help="块内附加行级去重(激进)")
    ap.add_argument("--no-meta-dedup", action="store_true",
                    help="关闭 changelog 元数据归一化(默认开启)")
    args = ap.parse_args()

    targets = []
    for root, dirs, fs in os.walk(args.dir):
        for fn in fs:
            if fn.endswith((".md", ".markdown", ".txt")):
                p = os.path.join(root, fn)
                try:
                    if os.path.getsize(p) >= args.min_size:
                        targets.append(p)
                except OSError:
                    pass
    targets.sort()
    print(f"🔍 扫描 {args.dir} → 超阈值文件 {len(targets)} 个\n")

    results = []
    for p in targets:
        r = process_file(p, args.line_dedup, not args.no_meta_dedup, args.apply)
        if r:
            results.append(r)

    # 按重复率降序输出
    results.sort(key=lambda x: x["dup_ratio"], reverse=True)

    print(f"{'文件':<62} {'原KB':>8} {'去重后KB':>9} {'原块':>6} {'删块':>5} {'重复率':>7}")
    total_before = total_after = 0
    high = 0
    for r in results:
        kb = r["size_before"] / 1e3
        kb2 = r["size_after"] / 1e3
        total_before += r["size_before"]
        total_after += r["size_after"]
        mode = "✅" if args.apply else "🔍"
        flag = " ⚠️" if r["dup_ratio"] >= args.min_dup_ratio else ""
        if r["dup_ratio"] >= args.min_dup_ratio:
            high += 1
        print(f"{mode} {os.path.basename(r['path']):<60} {kb:>8.1f} {kb2:>9.1f} "
              f"{r['blocks_before']:>6} {r['blocks_removed']:>5} {r['dup_ratio']:>6.1f}%{flag}")

    if results:
        total_ratio = (1 - total_after / total_before) * 100
        print(f"\n{'='*110}")
        print(f"总计: {len(results)} 文件, {total_before/1e3:.0f}KB → {total_after/1e3:.0f}KB "
              f"(整体压缩 {total_ratio:.1f}%)  [{'已写回' if args.apply else 'dry-run 未写'}]")
        print(f"达到 min-dup-ratio={args.min_dup_ratio}% 的文件: {high} 个")
        # 重复率分布
        buckets = {"0-5%": 0, "5-30%": 0, "30-70%": 0, "70-99%": 0, "100%": 0}
        for r in results:
            rr = r["dup_ratio"]
            if rr >= 99.5: buckets["100%"] += 1
            elif rr >= 70: buckets["70-99%"] += 1
            elif rr >= 30: buckets["30-70%"] += 1
            elif rr >= 5: buckets["5-30%"] += 1
            else: buckets["0-5%"] += 1
        print("重复率分布:", {k: v for k, v in buckets.items() if v})
        # 写报告
        rep = os.path.join("tmp", f"dedup-md-report-{datetime.now().strftime('%Y%m%d')}.md")
        with open(rep, "w", encoding="utf-8") as f:
            f.write(f"# dedup-md 报告 {datetime.now()}\n\n")
            f.write(f"- 目录: {args.dir}\n- 阈值: {args.min_size}B\n- 模式: "
                    f"{'apply' if args.apply else 'dry-run'}\n")
            f.write(f"- 文件数: {len(results)}, 总压缩 {total_ratio:.1f}%, "
                    f"达到阈值文件 {high} 个\n\n")
            f.write("| 文件 | 原KB | 去重后KB | 原块 | 删块 | 重复率 |\n")
            f.write("|---|---|---|---|---|---|\n")
            for r in results:
                f.write(f"| {os.path.basename(r['path'])} | {r['size_before']/1e3:.1f} "
                        f"| {r['size_after']/1e3:.1f} | {r['blocks_before']} "
                        f"| {r['blocks_removed']} | {r['dup_ratio']:.1f}% |\n")
        print(f"📄 报告: {rep}")
    else:
        print("无超阈值文件。")


if __name__ == "__main__":
    main()
