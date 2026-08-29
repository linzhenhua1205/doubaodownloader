#!/usr/bin/env python3
"""
Analyze and fix index.md coverage for knowledge modules.
Find missing files, invalid references, generate index entries, and auto-fix coverage gaps.

Usage:
    python3 scripts/check/analyze-index-coverage.py knowledge/<module>
    python3 scripts/check/analyze-index-coverage.py knowledge/<module> --generate-entries
    python3 scripts/check/analyze-index-coverage.py --all
    python3 scripts/check/analyze-index-coverage.py --all --fix
    python3 scripts/check/analyze-index-coverage.py --all --json
"""
import sys
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

# Skip these directories when scanning
SKIP_DIRS = {'bak', 'import-modules', 'node_modules', '.git', '.bak', 'oldbak', 'archive', 'archived'}


def extract_metadata(filepath: Path, root: Path) -> dict:
    """Extract title and summary from a markdown file."""
    rel_path = str(filepath.relative_to(root)).replace('\\', '/')
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return {'path': rel_path, 'title': '', 'summary': '(read error)', 'lines': 0, 'size_kb': 0}

    lines = content.split('\n')
    title = ''
    summary = ''

    for line in lines[:20]:
        if line.startswith('# ') and not line.startswith('## '):
            title = line[2:].strip()
            break

    found_title = False
    for line in lines[:50]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('# ') and not stripped.startswith('## '):
            found_title = True
            continue
        if found_title or not title:
            if stripped.startswith('>'): continue
            if stripped.startswith('---'): continue
            if stripped.startswith('|'): continue
            if stripped.startswith('```'): continue
            if stripped.startswith('!['): continue
            if stripped.startswith('-'): continue
            if stripped.startswith('*'): continue
            if not summary and len(stripped) > 10:
                summary = stripped[:200]
                break

    if not title:
        title = filepath.stem.replace('-', ' ').replace('_', ' ')

    if summary:
        summary = re.sub(r'\*\*([^*]+)\*\*', r'\1', summary)
        summary = re.sub(r'`([^`]+)`', r'\1', summary)
        summary = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', summary)
        summary = summary.rstrip('。.')

    return {
        'path': rel_path,
        'title': title,
        'summary': summary or '(无描述)',
        'lines': len(lines),
        'size_kb': round(filepath.stat().st_size / 1024, 1)
    }


def collect_content_files(module_dir: Path) -> tuple:
    """Collect all content .md files and their metadata."""
    all_files = set()
    file_data = {}
    for p in sorted(module_dir.rglob('*.md')):
        if p.name in ('index.md', 'log.md', 'README.md'):
            continue
        if any(skip in p.parts for skip in SKIP_DIRS):
            continue
        rel = str(p.relative_to(module_dir)).replace('\\', '/')
        all_files.add(rel)
        file_data[rel] = extract_metadata(p, module_dir)
    return all_files, file_data


def parse_index_references(idx_path: Path) -> set:
    """Parse all .md file references from index.md."""
    if not idx_path.exists():
        return set()
    idx_content = idx_path.read_text(encoding='utf-8')
    referenced = set(re.findall(r'\]\(([^)]+\.md)\)', idx_content))
    return {p.replace('\\', '/') for p in referenced
            if not p.startswith('../') and not p.startswith('http')}


def analyze_module(module_dir: Path) -> dict:
    """Analyze a single module's index.md coverage.
    Returns dict with: total, covered, missing, extra, coverage, missing_by_dir, file_data
    """
    all_files, file_data = collect_content_files(module_dir)
    referenced = parse_index_references(module_dir / 'index.md')

    missing = sorted(all_files - referenced)
    extra = sorted(referenced - all_files)
    covered = all_files & referenced

    missing_by_dir = defaultdict(list)
    for f in missing:
        parts = f.split('/')
        if len(parts) >= 2:
            group = '/'.join(parts[:2])
        else:
            group = parts[0]
        missing_by_dir[group].append(f)

    coverage = len(covered) * 100 // len(all_files) if all_files else 100

    return {
        'module': module_dir.name,
        'path': str(module_dir).replace('\\', '/'),
        'total': len(all_files),
        'covered': len(covered),
        'missing_count': len(missing),
        'extra_count': len(extra),
        'coverage': coverage,
        'missing': missing,
        'extra': extra,
        'missing_by_dir': dict(missing_by_dir),
        'file_data': file_data,
        'has_index': (module_dir / 'index.md').exists(),
    }


def print_single_report(result: dict, generate_entries: bool = False):
    """Print analysis report for a single module."""
    print(f"# Index Coverage Analysis: {result['module']}")
    print()
    print(f"| 指标 | 数量 |")
    print(f"|:-----|-----:|")
    print(f"| 内容文件总数 | {result['total']} |")
    print(f"| 已纳管文件 | {result['covered']} |")
    print(f"| **缺失文件** | **{result['missing_count']}** |")
    print(f"| 无效引用 | {result['extra_count']} |")
    print(f"| 覆盖率 | {result['coverage']}% |")
    print()

    if result['missing_by_dir']:
        print(f"## 缺失文件按目录分布")
        print()
        for group in sorted(result['missing_by_dir'].keys()):
            files = result['missing_by_dir'][group]
            print(f"- **{group}**: {len(files)} 个文件")
        print()

    if result['extra']:
        print(f"## 无效引用（{len(result['extra'])} 个）")
        print()
        for f in result['extra'][:30]:
            print(f"- `{f}`")
        if len(result['extra']) > 30:
            print(f"- ... 还有 {len(result['extra'])-30} 个")
        print()

    if generate_entries and result['missing']:
        print(f"## 生成的 index 条目（用于补全缺失文件）")
        print()
        for group in sorted(result['missing_by_dir'].keys()):
            files = result['missing_by_dir'][group]
            print(f"### {group} ({len(files)} 个)")
            print()
            print(f"| 文件 | 标题 | 摘要 | 行数 | 大小 |")
            print(f"|:-----|:-----|:------|-----:|-----:|")
            for f in files:
                d = result['file_data'][f]
                title = d['title'][:50]
                summary = d['summary'][:80]
                print(f"| [`{d['path']}`]({d['path']}) | {title} | {summary} | {d['lines']} | {d['size_kb']}KB |")
            print()


def print_all_report(results: list):
    """Print summary report for all modules."""
    total_files = sum(r['total'] for r in results)
    total_covered = sum(r['covered'] for r in results)
    total_missing = sum(r['missing_count'] for r in results)
    total_extra = sum(r['extra_count'] for r in results)
    overall_coverage = total_covered * 100 // total_files if total_files else 100

    print(f"# Knowledge Base Index Coverage Report")
    print(f"> Generated: 自动生成")
    print()
    print(f"## 总览")
    print()
    print(f"| 指标 | 数量 |")
    print(f"|:-----|-----:|")
    print(f"| 模块数 | {len(results)} |")
    print(f"| 内容文件总数 | {total_files} |")
    print(f"| 已纳管文件 | {total_covered} |")
    print(f"| **缺失文件** | **{total_missing}** |")
    print(f"| 无效引用 | {total_extra} |")
    print(f"| 整体覆盖率 | {overall_coverage}% |")
    print()

    print(f"## 各模块详情")
    print()
    print(f"| 模块 | 总文件 | 已纳管 | 缺失 | 覆盖率 |")
    print(f"|:-----|-------:|-------:|-----:|-------:|")
    for r in sorted(results, key=lambda x: x['coverage']):
        status = '🟢' if r['coverage'] >= 95 else ('🟡' if r['coverage'] >= 70 else '🔴')
        print(f"| {status} **{r['module']}** | {r['total']} | {r['covered']} | {r['missing_count']} | {r['coverage']}% |")
    print()

    # 列出覆盖率不足的模块的缺失文件概览
    low_coverage = [r for r in results if r['coverage'] < 100]
    if low_coverage:
        print(f"## 覆盖率不足的模块")
        print()
        for r in sorted(low_coverage, key=lambda x: x['coverage']):
            print(f"### {r['module']} — {r['coverage']}%（缺 {r['missing_count']} 个）")
            if r['missing_by_dir']:
                for group, files in sorted(r['missing_by_dir'].items()):
                    print(f"- {group}: {len(files)} 个")
            print()


def append_entries_to_index(module_dir: Path, result: dict) -> bool:
    """Append missing file entries to the end of index.md.
    Returns True if changes were made.
    """
    if not result['missing']:
        return False

    idx_path = module_dir / 'index.md'
    if not idx_path.exists():
        return False

    idx_content = idx_path.read_text(encoding='utf-8')

    # Build entries grouped by top-level directory
    missing_by_top = defaultdict(list)
    for f in result['missing']:
        top = f.split('/')[0]
        missing_by_top[top].append(f)

    entries_md = []
    entries_md.append(f"")
    entries_md.append(f"---")
    entries_md.append(f"")
    entries_md.append(f"## 补全条目（自动生成）")
    entries_md.append(f"")
    entries_md.append(f"> 以下条目由 analyze-index-coverage.py 自动生成，建议人工审核后归入对应章节。")
    entries_md.append(f"")

    for top_dir in sorted(missing_by_top.keys()):
        files = missing_by_top[top_dir]
        entries_md.append(f"### {top_dir}/（{len(files)} 个）")
        entries_md.append(f"")
        entries_md.append(f"| 文件 | 标题 | 摘要 |")
        entries_md.append(f"|:-----|:-----|:------|")
        for f in files:
            d = result['file_data'][f]
            title = d['title'][:60]
            summary = d['summary'][:100]
            entries_md.append(f"| [`{d['path']}`]({d['path']}) | {title} | {summary} |")
        entries_md.append(f"")

    new_content = idx_content.rstrip() + '\n' + '\n'.join(entries_md) + '\n'
    idx_path.write_text(new_content, encoding='utf-8')

    # Also update the file count in header
    new_count = result['total']
    # Try to update the total count in the header
    new_content = idx_path.read_text(encoding='utf-8')
    new_content = re.sub(
        r'共\s*\*\*\d+\*\*\s*个文件',
        f'共 **{new_count}** 个文件',
        new_content,
        count=1
    )
    idx_path.write_text(new_content, encoding='utf-8')

    return True


def find_all_modules(knowledge_dir: Path) -> list:
    """Find all modules (directories with index.md) under knowledge/."""
    modules = []
    for p in sorted(knowledge_dir.iterdir()):
        if p.is_dir() and (p / 'index.md').exists():
            if p.name in SKIP_DIRS:
                continue
            modules.append(p)
    return modules


def main():
    parser = argparse.ArgumentParser(
        description='Analyze and fix index.md coverage for knowledge modules',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze-index-coverage.py knowledge/02_rd
  python analyze-index-coverage.py knowledge/02_rd --generate-entries
  python analyze-index-coverage.py --all
  python analyze-index-coverage.py --all --fix
  python analyze-index-coverage.py --all --json
        """
    )
    parser.add_argument('module', nargs='?', help='Module directory path (e.g. knowledge/02_rd)')
    parser.add_argument('--all', action='store_true', help='Scan all modules under knowledge/')
    parser.add_argument('--generate-entries', action='store_true',
                        help='Generate index entries for missing files (single module mode)')
    parser.add_argument('--fix', action='store_true',
                        help='Auto-fix: append missing entries to index.md')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--knowledge-dir', default='knowledge',
                        help='Path to knowledge directory (default: knowledge/)')

    args = parser.parse_args()

    if not args.all and not args.module:
        parser.print_help()
        print("\nError: provide either a module path or --all")
        sys.exit(1)

    knowledge_dir = Path(args.knowledge_dir)

    if args.all:
        modules = find_all_modules(knowledge_dir)
        results = []
        fixed_count = 0
        for mod_dir in modules:
            result = analyze_module(mod_dir)
            results.append(result)
            if args.fix and result['missing_count'] > 0:
                if append_entries_to_index(mod_dir, result):
                    fixed_count += 1
                    print(f"✅ Fixed {result['module']}: added {result['missing_count']} entries", file=sys.stderr)

        if args.json:
            # Strip file_data for JSON output to keep size manageable
            json_results = []
            for r in results:
                jr = {k: v for k, v in r.items() if k != 'file_data'}
                json_results.append(jr)
            print(json.dumps(json_results, ensure_ascii=False, indent=2))
        else:
            print_all_report(results)
            if args.fix and fixed_count > 0:
                print(f"\n🔧 Fixed {fixed_count} modules.")
                print("Note: entries appended under '补全条目' section; manually review and categorize.")

        total_missing = sum(r['missing_count'] for r in results)
        sys.exit(0 if total_missing == 0 else 1)
    else:
        module_dir = Path(args.module)
        if not module_dir.is_dir():
            print(f"Error: {module_dir} is not a directory")
            sys.exit(1)

        result = analyze_module(module_dir)

        if args.fix and result['missing_count'] > 0:
            if append_entries_to_index(module_dir, result):
                print(f"✅ Fixed {result['module']}: added {result['missing_count']} entries", file=sys.stderr)
                # Re-analyze after fix
                result = analyze_module(module_dir)

        if args.json:
            jr = {k: v for k, v in result.items() if k != 'file_data'}
            print(json.dumps(jr, ensure_ascii=False, indent=2))
        else:
            print_single_report(result, args.generate_entries)

        sys.exit(0 if result['missing_count'] == 0 else 1)


if __name__ == '__main__':
    main()
