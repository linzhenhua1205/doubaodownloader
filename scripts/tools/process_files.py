#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一处理脚本：遍历目录，转换PDF/Word为Markdown，复制TXT/MD文件

功能：
  1. 遍历给定目录，识别文件类型
  2. PDF/DOC/DOCX/HTML → 调用 convert-to-markdown.py 转换
  3. TXT/MD → 直接复制到目标目录（跳过已存在同大小文件）
  4. 保持原有目录结构
  5. 错误跳过并记录到日志文件

用法:
  python scripts/process_files.py Z:\\
  python scripts/process_files.py Z:\\ --dry-run
"""

import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
IMPORT_DIR = PROJECT_ROOT / "import" / "TCGC203new_info_drive"
CONVERT_SCRIPT = SCRIPT_DIR / "convert-to-markdown.py"

CONVERT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.html', '.htm'}
COPY_EXTENSIONS = {'.txt', '.md'}

LOG_FILE = PROJECT_ROOT / "tmp" / "process_errors.log"


def to_long_path(path_obj):
    if os.name != 'nt':
        return str(path_obj)
    s = str(path_obj)
    if s.startswith('\\\\?\\'):
        return s
    if s.startswith('\\\\'):
        return '\\\\?\\UNC\\' + s[2:]
    return '\\\\?\\' + s


def log_error(rel_path, error_msg):
    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} | {rel_path} | {error_msg}\n")


def find_files(source_dir):
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
            if ext in CONVERT_EXTENSIONS or ext in COPY_EXTENSIONS:
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, source_path)
                files.append((full_path, rel_path, ext))

    if dir_count >= 500:
        print()
    return files


def convert_file(src_path, rel_path):
    src = Path(src_path)
    dst_dir = IMPORT_DIR / rel_path.parent
    dst_file = dst_dir / rel_path.with_suffix('.md')

    if dst_file.exists():
        src_mtime = src.stat().st_mtime
        dst_mtime = dst_file.stat().st_mtime
        if dst_mtime > src_mtime:
            return 'skip_newer'

    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [sys.executable, str(CONVERT_SCRIPT),
             '--input', str(src),
             '--output', str(dst_file.parent)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            if 'error' in result.stderr.lower():
                log_error(rel_path, f"转换失败: {result.stderr[:200]}")
                return 'fail'
        if dst_file.exists() and dst_file.stat().st_size > 0:
            return 'success'
        else:
            log_error(rel_path, "转换后文件为空")
            return 'fail'
    except subprocess.TimeoutExpired:
        log_error(rel_path, "转换超时(5分钟)")
        return 'fail'
    except Exception as e:
        log_error(rel_path, f"转换异常: {e}")
        return 'fail'


def copy_file(src_path, rel_path):
    src = Path(src_path)
    dst = IMPORT_DIR / rel_path

    if dst.exists():
        try:
            src_size = src.stat().st_size
            dst_size = dst.stat().st_size
            if src_size == dst_size:
                return 'skip_exist'
        except OSError:
            pass

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(to_long_path(src), to_long_path(dst))
        return 'success'
    except Exception as e:
        log_error(rel_path, f"复制失败: {e}")
        return 'fail'


def process_directory(source_dir, dry_run=False):
    source_path = Path(source_dir).resolve()

    print(f"{'=' * 60}")
    print(f"  源目录:   {source_path}")
    print(f"  目标目录: {IMPORT_DIR}")
    print(f"  模式:     {'预览' if dry_run else '执行'}")
    print(f"{'=' * 60}")

    files = find_files(source_dir)
    print(f"\n找到 {len(files)} 个文件")

    stats = {
        'total': len(files),
        'convert_success': 0,
        'convert_skip': 0,
        'convert_fail': 0,
        'copy_success': 0,
        'copy_skip': 0,
        'copy_fail': 0,
    }

    if dry_run:
        convert_count = sum(1 for _, _, ext in files if ext in CONVERT_EXTENSIONS)
        copy_count = sum(1 for _, _, ext in files if ext in COPY_EXTENSIONS)
        print(f"  - 待转换(PDF/DOC/DOCX/HTML): {convert_count}")
        print(f"  - 待复制(TXT/MD): {copy_count}")
        return

    for idx, (src_full, rel_path, ext) in enumerate(files, 1):
        if ext in CONVERT_EXTENSIONS:
            result = convert_file(src_full, rel_path)
            if result == 'success':
                stats['convert_success'] += 1
            elif result == 'skip_newer':
                stats['convert_skip'] += 1
            else:
                stats['convert_fail'] += 1
        else:
            result = copy_file(src_full, rel_path)
            if result == 'success':
                stats['copy_success'] += 1
            elif result == 'skip_exist':
                stats['copy_skip'] += 1
            else:
                stats['copy_fail'] += 1

        if idx % 100 == 0:
            print(f"\r  处理中... {idx}/{len(files)} | 转换:{stats['convert_success']}({stats['convert_skip']}) | "
                  f"复制:{stats['copy_success']}({stats['copy_skip']}) | 失败:{stats['convert_fail']+stats['copy_fail']}",
                  end="", flush=True)

    print()
    print(f"\n{'=' * 60}")
    print(f"  处理完成")
    print(f"  总计: {stats['total']}")
    print(f"  转换成功: {stats['convert_success']}, 跳过: {stats['convert_skip']}, 失败: {stats['convert_fail']}")
    print(f"  复制成功: {stats['copy_success']}, 跳过: {stats['copy_skip']}, 失败: {stats['copy_fail']}")
    if stats['convert_fail'] + stats['copy_fail'] > 0:
        print(f"  错误日志: {LOG_FILE}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description='统一处理脚本：转换PDF/Word，复制TXT/MD')
    parser.add_argument('source_dir', help='源目录路径')
    parser.add_argument('--dry-run', action='store_true', help='预览模式')
    args = parser.parse_args()

    if args.source_dir.lower() == 'z:\\' or args.source_dir.lower() == 'z:':
        LOG_FILE.parent.mkdir(exist_ok=True)
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | 开始处理 Z:\\\n")

    process_directory(args.source_dir, args.dry_run)


if __name__ == '__main__':
    main()
