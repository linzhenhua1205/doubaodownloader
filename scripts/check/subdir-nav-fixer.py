#!/usr/bin/env python3
"""
Subdirectory Navigation Consistency Fixer

Ensures that all subdirectory index.md files have:
  - A "上层入口" link back to the parent index.md
  - Consistent header format with positioning info

Usage:
  python subdir-nav-fixer.py <dir_path> [--dry-run] [--fix]
  python subdir-nav-fixer.py <dir_path> --recursive
"""

import argparse
import re
import sys
from pathlib import Path


HEADER_PATTERN = re.compile(r'^#\s+(.+)$', re.MULTILINE)
POSITION_LINE = re.compile(r'^>\s*\*\*定位\*\*[:：]', re.MULTILINE)
PARENT_LINK_LINE = re.compile(r'上层入口|parent.*index', re.IGNORECASE)


def has_parent_link(content: str) -> bool:
    """Check if content already has a parent directory link."""
    return bool(PARENT_LINK_LINE.search(content))


def add_parent_link(filepath: Path, parent_name: str, parent_path: str) -> str:
    """Add a '上层入口' line to the header blockquote section."""
    lines = filepath.read_text(encoding='utf-8').splitlines()

    # Find the header blockquote section (lines starting with '>' after H1)
    in_header = False
    insert_idx = -1
    last_quote_line = -1

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# ') and not in_header:
            in_header = True
            continue
        if in_header and stripped.startswith('>'):
            last_quote_line = i
        elif in_header and last_quote_line >= 0 and not stripped.startswith('>'):
            # End of blockquote section
            insert_idx = last_quote_line + 1
            break

    if insert_idx < 0:
        # No blockquote found - insert after H1
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                insert_idx = i + 1
                # Add a blank line and then the blockquote
                new_lines = lines[:insert_idx]
                new_lines.append('')
                new_lines.append(f'> **上层入口**: [{parent_name}]({parent_path})')
                new_lines.extend(lines[insert_idx:])
                return '\n'.join(new_lines)

    # Insert into existing blockquote section
    new_line = f'> **上层入口**: [{parent_name}]({parent_path})'
    lines.insert(insert_idx, new_line)
    return '\n'.join(lines)


def process_directory(root_dir: Path, dry_run: bool = True, recursive: bool = False) -> dict:
    """Process all subdirectories under root_dir."""
    stats = {
        'subdirs_with_index': 0,
        'subdirs_no_index': 0,
        'fixed': 0,
        'already_ok': 0,
        'files': [],
    }

    for item in sorted(root_dir.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith('.'):
            continue

        index_file = item / 'index.md'
        if not index_file.exists():
            stats['subdirs_no_index'] += 1
            continue

        stats['subdirs_with_index'] += 1

        content = index_file.read_text(encoding='utf-8')
        if has_parent_link(content):
            stats['already_ok'] += 1
            stats['files'].append({'path': str(index_file), 'status': 'ok'})
            continue

        # Needs fixing
        parent_path = '../index.md'
        parent_name = root_dir.name

        if not dry_run:
            new_content = add_parent_link(index_file, parent_name, parent_path)
            index_file.write_text(new_content, encoding='utf-8')

        stats['fixed'] += 1
        stats['files'].append({'path': str(index_file), 'status': 'fixed'})

        # Recurse into sub-subdirectories
        if recursive:
            sub_stats = process_directory(item, dry_run, recursive)
            for k, v in sub_stats.items():
                if isinstance(v, int) and k in stats:
                    stats[k] += v
                elif k == 'files':
                    stats['files'].extend(v)

    return stats


def main():
    parser = argparse.ArgumentParser(description='Subdirectory navigation consistency fixer')
    parser.add_argument('dir_path', help='Root directory path')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default is dry-run)')
    parser.add_argument('--recursive', action='store_true', help='Recurse into all subdirectories')
    args = parser.parse_args()

    root_dir = Path(args.dir_path).resolve()
    if not root_dir.is_dir():
        print(f"Error: {root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    dry_run = not args.fix  # default to dry-run

    print(f"🔍 Checking navigation links under {root_dir}")
    if dry_run:
        print("   (DRY-RUN mode: use --fix to apply changes)")
    print()

    stats = process_directory(root_dir, dry_run=dry_run, recursive=args.recursive)

    print(f"📊 统计：")
    print(f"   有 index 的子目录: {stats['subdirs_with_index']}")
    print(f"   无 index 的子目录: {stats['subdirs_no_index']}")
    print(f"   已有上层入口: {stats['already_ok']}")
    print(f"   已修复/需修复: {stats['fixed']}")
    print()

    if stats['files']:
        print("📋 详情：")
        for f in stats['files']:
            status_icon = '✅' if f['status'] == 'ok' else '🔧'
            action = '已存在' if f['status'] == 'ok' else ('已修复' if not dry_run else '需修复')
            print(f"   {status_icon} {f['path']} — {action}")

    if not dry_run and stats['fixed'] > 0:
        print(f"\n✅ 已修复 {stats['fixed']} 个子目录的上层入口链接")
    elif dry_run and stats['fixed'] > 0:
        print(f"\n💡 需修复 {stats['fixed']} 个文件，使用 --fix 应用更改")


if __name__ == '__main__':
    main()
