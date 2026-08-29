#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入脚本：遍历给定目录，将 txt/md 文件导入到 import 目录下

功能：
  1. 遍历给定目录，获取所有 .txt 和 .md 文件
  2. 导入到 import/<目录英文名>/ 下，保持原有相对路径结构
  3. 重名文件自动追加 _日期_流水号 区分

用法:
  python scripts/import_files.py D:\\some\\path
  python scripts/import_files.py D:\\some\\path --name custom_name
  python scripts/import_files.py D:\\some\\path --move          # 移动而非复制
  python scripts/import_files.py D:\\some\\path --dry-run       # 预览不执行
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
IMPORT_DIR = PROJECT_ROOT / "import"

TARGET_EXTENSIONS = {".txt", ".md"}


def to_long_path(path_obj):
    """
    将路径转换为 Windows 长路径格式（带 \\?\ 前缀）。
    - 普通路径 D:\\... -> \\\\?\\D:\\...
    - UNC 路径 \\\\server\\share\\... -> \\\\?\\UNC\\server\\share\\...
    - 非 Windows 系统直接返回原路径字符串
    """
    if os.name != 'nt':
        return str(path_obj)
    s = str(path_obj)
    if s.startswith('\\\\?\\'):
        return s
    if s.startswith('\\\\'):
        # UNC 路径: \\server\share -> \\?\UNC\server\share
        return '\\\\?\\UNC\\' + s[2:]
    return '\\\\?\\' + s


def get_target_dir_name(source_dir, custom_name=None):
    """
    获取目标目录名：
    - 优先使用 --name 参数
    - 否则取源目录的最后一个目录名
    """
    if custom_name:
        return custom_name

    source_path = Path(source_dir).resolve()
    name = source_path.name
    if name:
        return name

    # 根目录（如 Z:\ 或 UNC 根）的 name 为空，用盘符或主机名
    drive = source_path.drive  # 如 "Z:" 或 "\\TCGC203"
    if drive:
        # Z: -> z_drive, \\TCGC203 -> tCGC203
        clean = drive.replace(":", "").replace("\\", "").replace("/", "")
        return f"{clean}_drive" if clean else "root_import"

    return "root_import"


def find_files(source_dir):
    """遍历目录，返回所有 .txt/.md 文件的相对路径列表"""
    source_path = Path(source_dir).resolve()
    if not source_path.exists():
        print(f"[错误] 目录不存在: {source_dir}")
        sys.exit(1)

    files = []
    dir_count = 0
    for root, dirs, filenames in os.walk(source_path):
        dir_count += 1
        if dir_count % 500 == 0:
            print(f"\r  扫描中... 已遍历 {dir_count} 个目录, 找到 {len(files)} 个文件", end="", flush=True)
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in TARGET_EXTENSIONS:
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, source_path)
                files.append((full_path, rel_path))

    if dir_count >= 500:
        print()  # 换行
    return files


def resolve_conflict(dst_path):
    """
    目标文件已存在时，追加 _YYYYMMDD_NNN 区分
    例: report.md -> report_20260711_001.md
    """
    if not dst_path.exists():
        return dst_path

    stem = dst_path.stem
    ext = dst_path.suffix
    parent = dst_path.parent
    date_str = datetime.now().strftime("%Y%m%d")

    for seq in range(1, 1000):
        candidate = parent / f"{stem}_{date_str}_{seq:03d}{ext}"
        if not candidate.exists():
            return candidate

    # 理论上不会走到这里
    return parent / f"{stem}_{date_str}_999{ext}"


def import_files(source_dir, target_name=None, move=False, dry_run=False, skip_existing=False):
    """执行导入"""
    source_path = Path(source_dir).resolve()
    target_dir_name = get_target_dir_name(source_dir, target_name)
    target_root = IMPORT_DIR / target_dir_name

    print(f"{'=' * 60}")
    print(f"  源目录:   {source_path}")
    print(f"  目标目录: {target_root}")
    print(f"  模式:     {'移动' if move else '复制'}")
    print(f"  预览:     {'是' if dry_run else '否'}")
    print(f"  跳过已存在: {'是' if skip_existing else '否'}")
    print(f"{'=' * 60}")

    files = find_files(source_dir)
    print(f"\n找到 {len(files)} 个 txt/md 文件\n")

    if not files:
        print("无文件可导入。")
        return

    imported = 0
    skipped = 0
    renamed = 0
    skipped_existing = 0
    total = len(files)

    for idx, (src_full, rel_path) in enumerate(files, 1):
        src = Path(src_full)
        dst = target_root / rel_path

        # 跳过已存在且同大小的文件（断点续传）
        if skip_existing and dst.exists():
            try:
                src_size = src.stat().st_size
                dst_size = dst.stat().st_size
                if src_size == dst_size:
                    skipped_existing += 1
                    if skipped_existing % 500 == 0:
                        print(f"\r  续传跳过... 已跳过 {skipped_existing} 个已存在文件, "
                              f"已复制 {imported} 个 ({idx}/{total})", end="", flush=True)
                    continue
            except OSError:
                pass  # 大小读取失败，继续走正常流程

        # 检查冲突
        final_dst = resolve_conflict(dst)
        was_renamed = final_dst != dst

        if dry_run:
            status = "重命名" if was_renamed else "新建"
            print(f"  [{status}] {rel_path}")
            if was_renamed:
                print(f"           -> {final_dst.name}")
            imported += 1
            continue

        try:
            # 创建目录（支持长路径）
            dst_parent = final_dst.parent
            os.makedirs(to_long_path(dst_parent), exist_ok=True)

            if move:
                shutil.move(to_long_path(src), to_long_path(final_dst))
            else:
                shutil.copy2(to_long_path(src), to_long_path(final_dst))

            imported += 1
            if was_renamed:
                renamed += 1
            # 进度报告（每500个文件）
            if imported % 500 == 0:
                print(f"\r  复制中... 已复制 {imported} 个, 跳过 {skipped_existing} 个, "
                      f"失败 {skipped} 个 ({idx}/{total})", end="", flush=True)
        except Exception as e:
            print(f"\n  [失败] {rel_path}: {e}")
            skipped += 1

    if imported >= 500 or skipped_existing >= 500:
        print()  # 换行

    print(f"\n{'=' * 60}")
    print(f"  导入完成: {imported} 成功, {renamed} 重命名, {skipped} 失败, "
          f"{skipped_existing} 跳过已存在")
    print(f"  目标: {target_root}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(
        description='导入 txt/md 文件到 import 目录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/import_files.py D:\\docs\\notes
  python scripts/import_files.py D:\\docs\\notes --name mynotes
  python scripts/import_files.py D:\\docs\\notes --move
  python scripts/import_files.py D:\\docs\\notes --dry-run
        """
    )
    parser.add_argument('source_dir', help='源目录路径')
    parser.add_argument('--name', default=None,
                        help='目标目录名（默认取源目录最后一级名）')
    parser.add_argument('--move', action='store_true',
                        help='移动文件而非复制')
    parser.add_argument('--dry-run', action='store_true',
                        help='预览模式，不实际操作')
    parser.add_argument('--skip-existing', action='store_true',
                        help='跳过已存在且同大小的文件（断点续传）')

    args = parser.parse_args()
    import_files(args.source_dir, args.name, args.move, args.dry_run,
                 args.skip_existing)


if __name__ == '__main__':
    main()
