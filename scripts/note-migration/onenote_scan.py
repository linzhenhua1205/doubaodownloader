#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""onenote_scan.py — OneNote 数据目录构成扫描

用途: 探查 OneNote ~100G 里 文本分区 vs 附件/图片/嵌入文件 的占比,
     为"文本优先导出 + 附件清单化"决策提供数据支撑。

OneNote 笔记本在本地的一般位置:
  - Windows: %USERPROFILE%\Documents\OneNote Notebooks 或 OneDrive\文档\OneNote 笔记本
  - 文件形态: 每个分区一个 .one 文件; 分区内嵌附件存放在 .one 内部 (无法直接读)
  - 注意: 本地 .one 是二进制, 本脚本只做"文件清单+大小统计+附件占位识别",
          实际导出文本请用 OneNote 桌面客户端 "导出" 功能 (见 onenote_export_guide.md)

用法:
  python3 onenote_scan.py <笔记本根目录>
  python3 onenote_scan.py <根目录> --csv out.csv

纯标准库。
"""
import argparse
import os
import sys
from collections import defaultdict

# 常见附件/媒体扩展名 (用于估算非文本占比)
ATTACH_EXTS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
               ".zip", ".rar", ".7z", ".exe", ".msi", ".iso",
               ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff",
               ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac", ".mkv",
               ".eml", ".msg", ".vsdx", ".drawio", ".svg"}


def scan(root: str):
    """扫描目录, 返回统计 dict"""
    stats = defaultdict(lambda: {"count": 0, "size": 0})
    total_files = 0
    total_size = 0
    one_files = []
    attach_files = []

    for dirpath, dirnames, filenames in os.walk(root):
        # 跳过隐藏目录
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            total_files += 1
            total_size += size
            ext = os.path.splitext(fn)[1].lower()
            stats[ext if ext else "(无扩展名)"]["count"] += 1
            stats[ext if ext else "(无扩展名)"]["size"] += size
            if ext == ".one":
                one_files.append((fp, size))
            if ext in ATTACH_EXTS:
                attach_files.append((fp, size))

    return {
        "root": root,
        "total_files": total_files,
        "total_size": total_size,
        "stats": stats,
        "one_files": one_files,
        "attach_files": attach_files,
    }


def fmt_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def main():
    ap = argparse.ArgumentParser(description="OneNote 目录构成扫描")
    ap.add_argument("root", help="OneNote 笔记本根目录")
    ap.add_argument("--csv", help="输出附件清单 CSV 路径")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"❌ 目录不存在: {args.root}")
        sys.exit(1)

    print(f"🔍 扫描中: {args.root} ...")
    r = scan(args.root)

    print(f"\n{'=' * 60}")
    print(f"📊 总览: {r['total_files']} 个文件, 共 {fmt_size(r['total_size'])}")
    print(f"{'=' * 60}")
    print(f"{'扩展名':<12} {'数量':>8} {'大小':>12} {'占比':>8}")
    print("-" * 44)
    for ext, s in sorted(r["stats"].items(), key=lambda x: -x[1]["size"]):
        pct = s["size"] / r["total_size"] * 100 if r["total_size"] else 0
        print(f"{ext:<12} {s['count']:>8} {fmt_size(s['size']):>12} {pct:>7.1f}%")

    n_one = len(r["one_files"])
    one_size = sum(s for _, s in r["one_files"])
    n_att = len(r["attach_files"])
    att_size = sum(s for _, s in r["attach_files"])
    print("-" * 44)
    print(f"📓 .one 分区文件: {n_one} 个, {fmt_size(one_size)}")
    print(f"📎 附件/媒体文件: {n_att} 个, {fmt_size(att_size)} "
          f"({att_size / r['total_size'] * 100:.1f}% 若存在)")
    print(f"\n💡 判断: 若 .one 占大头 → 文本在分区内部, 用 OneNote 客户端导出")
    print(f"         若附件占大头 → 附件清单化, 按需取用 (见 onenote_export_guide.md)")

    if args.csv and r["attach_files"]:
        with open(args.csv, "w", encoding="utf-8") as fp:
            fp.write("path,size_bytes\n")
            for p, s in sorted(r["attach_files"], key=lambda x: -x[1]):
                fp.write(f"{p},{s}\n")
        print(f"\n📄 附件清单已存: {args.csv}")

    if not r["one_files"] and not r["attach_files"]:
        print("\n⚠️ 未发现 .one 或附件文件, 请确认目录是否是 OneNote 笔记本根目录")
        print("   尝试: %USERPROFILE%\\Documents\\OneNote Notebooks")


if __name__ == "__main__":
    main()
