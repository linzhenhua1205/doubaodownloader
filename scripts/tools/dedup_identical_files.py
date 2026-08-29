#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重复文件去重工具 v1.0 — dedup_identical_files.py

用途:
  扫描目录，按 (文件大小, md5) 分组，找出内容完全相同的重复文件。
  每组保留 1 个文件（**优先保留英文名/非中文名**），
  其余重复文件 mv 到 tmp/bak/ 回收站（遵守 RULE.md 永不 rm）。

背景(2026-08-13):
  discover/newwiki2/docs 下同一内容常存在两个版本:
    中文标题版: sha_q27_这几天刷面试题其实有时候会对整.md
    英文 slug 版: sha_q27_overall_pace.md
  两者大小+md5 完全一致，需要优先删除中文名版本。

安全设计:
  1. 默认 dry-run，仅统计不移动；--apply 才实际执行
  2. 移动目标为 tmp/bak/dedup-dup-<date>/（mv 而非 rm，可恢复）
  3. 纯本地脚本，不调用任何 LLM/API，文件内容零进入大模型上下文
  4. 重复判定用 (size, md5) 双重校验，不会误删唯一文件

用法:
  # 1) 摸底: 统计重复组（不移动）
  python3 scripts/tools/dedup_identical_files.py --dir discover/newwiki2/docs

  # 2) 执行: 删中文名重复（默认模式: 只处理含中文名的组，英文名保留）
  python3 scripts/tools/dedup_identical_files.py --dir discover/newwiki2/docs --apply

  # 3) 激进: 所有重复组都去重到 1 个（含全英文重复组）
  python3 scripts/tools/dedup_identical_files.py --dir discover/newwiki2/docs --all-groups --apply

输出:
  stdout 打印每组保留/删除明细 + 汇总；同时写入 tmp/dedup-dup-report-<date>.md
"""
import os
import re
import sys
import hashlib
import shutil
import argparse
from datetime import datetime
from collections import defaultdict

# CJK 字符（中文/日文/韩文）判定
CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')


def is_chinese_name(path):
    """文件名（不含目录）是否含中文字符"""
    return bool(CJK_RE.search(os.path.basename(path)))


def file_md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def pick_keep(files):
    """从一组重复文件中选保留者：优先非中文名，其次名字短，再按字母序。"""
    non_cn = [f for f in files if not is_chinese_name(f)]
    pool = non_cn if non_cn else files
    return min(pool, key=lambda p: (len(os.path.basename(p)), p.lower()))


def scan_duplicates(root_dir, exts):
    """返回 [(keep_path, [dup_path...]), ...] 列表（按保留路径排序）。"""
    # 第一层: 按文件大小分组（避免对全库算 md5）
    size_groups = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 跳过隐藏目录
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for fn in filenames:
            if exts and not fn.lower().endswith(exts):
                continue
            p = os.path.join(dirpath, fn)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            if sz == 0:
                continue  # 空文件不处理
            size_groups[sz].append(p)

    groups = []
    for sz, files in size_groups.items():
        if len(files) < 2:
            continue
        # 第二层: 同大小内按 md5 分组
        md5_groups = defaultdict(list)
        for f in files:
            try:
                md5_groups[file_md5(f)].append(f)
            except OSError:
                continue
        for md5, same_files in md5_groups.items():
            if len(same_files) < 2:
                continue
            keep = pick_keep(same_files)
            dups = [f for f in same_files if f != keep]
            groups.append((keep, dups))
    groups.sort(key=lambda g: g[0].lower())
    return groups


def main():
    ap = argparse.ArgumentParser(description="重复文件去重工具 (size+md5 判定)")
    ap.add_argument("--dir", required=True, help="目标目录(递归)")
    ap.add_argument("--apply", action="store_true", help="实际移动(否则dry-run)")
    ap.add_argument("--all-groups", action="store_true",
                    help="所有重复组都去重到1个（默认只处理含中文名的组）")
    ap.add_argument("--ext", default=".md,.markdown,.txt",
                    help="处理的扩展名列表(逗号分隔，默认 .md,.markdown,.txt; 空=全部)")
    args = ap.parse_args()

    exts = tuple(e.strip().lower() for e in args.ext.split(",") if e.strip())
    groups = scan_duplicates(args.dir, exts)

    # 过滤: 默认模式只处理含中文名的重复组
    filtered = []
    for keep, dups in groups:
        if args.all_groups or any(is_chinese_name(d) for d in dups):
            filtered.append((keep, dups))
    groups = filtered

    print(f"🔍 扫描 {args.dir} → 重复组 {len(groups)} 个\n")

    # 统计
    total_dups = sum(len(d) for _, d in groups)
    cn_dups = sum(1 for _, d in groups for f in d if is_chinese_name(f))
    total_bytes = sum(os.path.getsize(d) for _, d in groups for d in d)

    # 执行移动
    if args.apply:
        bak_dir = os.path.join("tmp", "bak",
                               f"dedup-dup-{datetime.now().strftime('%Y%m%d')}")
        os.makedirs(bak_dir, exist_ok=True)

    print(f"{'保留(keep)':<72} {'删除(→bak)':<52} 中文?")
    print("-" * 140)
    moved = 0
    for keep, dups in groups:
        keep_short = os.path.basename(keep)
        for d in dups:
            tag = "中" if is_chinese_name(d) else "英"
            print(f"  {keep_short:<70} {os.path.basename(d):<50} {tag}")
            if args.apply:
                dst = os.path.join(bak_dir, os.path.basename(d))
                # 避免 bak 内重名覆盖：加序号
                n = 1
                base, ext = os.path.splitext(dst)
                while os.path.exists(dst):
                    dst = f"{base}_{n}{ext}"
                    n += 1
                shutil.move(d, dst)
                moved += 1

    print("-" * 140)
    print(f"总计: {len(groups)} 组, {total_dups} 个重复文件"
          f"（其中中文名 {cn_dups} 个）, 释放空间 {total_bytes/1e6:.1f}MB  "
          f"[{'已移动到 ' + bak_dir if args.apply else 'dry-run 未移动'}]")

    # 写报告
    rep = os.path.join("tmp", f"dedup-dup-report-{datetime.now().strftime('%Y%m%d')}.md")
    with open(rep, "w", encoding="utf-8") as f:
        f.write(f"# 重复文件去重报告 {datetime.now()}\n\n")
        f.write(f"- 目录: {args.dir}\n- 模式: {'apply' if args.apply else 'dry-run'}\n")
        f.write(f"- 重复组: {len(groups)}, 重复文件: {total_dups} (中文名 {cn_dups}), "
                f"释放 {total_bytes/1e6:.1f}MB\n\n")
        f.write("| 保留 | 删除(→bak) | 中文名 |\n|---|---|---|\n")
        for keep, dups in groups:
            for d in dups:
                f.write(f"| {keep} | {d} | {'是' if is_chinese_name(d) else '否'} |\n")
    print(f"📄 报告: {rep}")


if __name__ == "__main__":
    main()
