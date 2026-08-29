#!/usr/bin/env python3
"""
extract-content-metadata.py — 知识内容文件元数据提取工具

基于 spec/KNOWLEDGE_CONTENT_FORMAT.md 规范，提取内容文件的元数据：
  - title, summary, keywords
  - toc_entries
  - references (internal + external)
  - changelog
  - lines, size_kb

Output JSON to knowledge/weekly-reports/07_kb_stat/content-metadata-YYYY-MM-DD.json

Usage:
    python scripts/check/extract-content-metadata.py knowledge/ --all
    python scripts/check/extract-content-metadata.py knowledge/02_rd --module 02_rd
    python scripts/check/extract-content-metadata.py <file.md>
    python scripts/check/extract-content-metadata.py knowledge/ --all --filter "summary=(待补充)"
"""
import sys
import re
import json
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime

# Windows console encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

from scripts.shared.workspace import WORKSPACE_ROOT as REPO_ROOT, KNOWLEDGE_ROOT, SCRIPTS_DIR

SCRIPT_DIR = SCRIPTS_DIR / "check"
OUTPUT_DIR = KNOWLEDGE_ROOT / "weekly-reports" / "07_kb_stat"

# === Reuse parsing functions from content-format-normalizer.py ===
def _load_normalizer():
    src = SCRIPT_DIR / 'content-format-normalizer.py'
    spec = importlib.util.spec_from_file_location('content_format_normalizer', src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

norm = _load_normalizer()

# === Regex for extraction ===
RE_SUMMARY = re.compile(r'^>\s*\*\*概要\*\*:\s*(.+?)\s*$', re.MULTILINE)
RE_KEYWORDS = re.compile(r'^>\s*\*\*关键词\*\*:\s*(.+?)\s*$', re.MULTILINE)
RE_INTERNAL_LINK = re.compile(r'^-\s*\[([^\]]+)\]\(([^)]+)\)\s*[—-]?\s*(.*)$')
RE_EXTERNAL_LINK = re.compile(r'^-\s*(?:来源\d*[:：]\s*)?(.+)$')
RE_CHANGELOG_ROW = re.compile(r'^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*(?:\|[^|]*)?\|\s*$')
RE_TOC_ENTRY = re.compile(r'^(\s*)-\s+\[([^\]]+)\]\(([^)]+)\)')


def extract_metadata(filepath: Path) -> dict:
    """Extract full metadata from a content file."""
    rel_to_repo = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    rel_to_kb = str(filepath.relative_to(KNOWLEDGE_ROOT)).replace('\\', '/')

    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return {
            'file': rel_to_kb,
            'path': rel_to_repo,
            'error': str(e),
        }

    lines = content.split('\n')
    parsed = norm.parse_file(content)

    # Title
    title = parsed['title'] or filepath.stem

    # Summary
    summary = ''
    m = RE_SUMMARY.search(content)
    if m:
        summary = m.group(1).strip()

    # Keywords
    keywords_str = ''
    m = RE_KEYWORDS.search(content)
    if m:
        keywords_str = m.group(1).strip()
    keywords = []
    if keywords_str and keywords_str != '(待补充)':
        keywords = [k.strip() for k in re.split(r'\s*·\s*', keywords_str) if k.strip()]

    # TOC entries
    toc_entries = []
    if parsed['toc_start'] >= 0:
        for i in range(parsed['toc_start'] + 1, parsed['toc_end']):
            m = RE_TOC_ENTRY.match(lines[i])
            if m:
                indent = len(m.group(1))
                level = 2 + (indent // 2)
                toc_entries.append({
                    'level': level,
                    'title': m.group(2),
                    'anchor': m.group(3),
                })

    # References
    internal_refs = []
    external_refs = []
    if parsed['refs_start'] >= 0:
        internal_refs, external_refs = norm.extract_refs_from_section(
            lines, parsed['refs_start'], parsed['refs_end']
        )

    # Changelog
    changelog = []
    if parsed['changelog_start'] >= 0:
        changelog = norm.extract_changelog_from_section(
            lines, parsed['changelog_start'], parsed['changelog_end']
        )

    return {
        'file': rel_to_kb,
        'path': rel_to_repo,
        'title': title,
        'summary': summary,
        'keywords': keywords,
        'keywords_str': keywords_str,
        'toc_count': len(toc_entries),
        'toc_entries': toc_entries,
        'references': {
            'internal': internal_refs,
            'external': external_refs,
        },
        'internal_ref_count': len(internal_refs),
        'external_ref_count': len(external_refs),
        'changelog': changelog,
        'changelog_count': len(changelog),
        'lines': len(lines),
        'size_kb': round(filepath.stat().st_size / 1024, 1),
    }


def generate_summary_report(results: list, output_path: Path):
    """Generate a markdown summary report."""
    total = len(results)
    has_summary = sum(1 for r in results if r.get('summary') and r['summary'] != '(待补充)')
    has_keywords = sum(1 for r in results if r.get('keywords'))
    has_internal_refs = sum(1 for r in results if r.get('internal_ref_count', 0) > 0)
    has_external_refs = sum(1 for r in results if r.get('external_ref_count', 0) > 0)
    has_changelog = sum(1 for r in results if r.get('changelog_count', 0) > 0)
    needs_fill = sum(1 for r in results if not r.get('summary') or r['summary'] == '(待补充)')

    # By directory
    from collections import defaultdict
    dir_stats = defaultdict(lambda: {'total': 0, 'has_summary': 0, 'has_keywords': 0, 'needs_fill': 0})
    for r in results:
        top = r['file'].split('/')[0] if '/' in r['file'] else '(root)'
        dir_stats[top]['total'] += 1
        if r.get('summary') and r['summary'] != '(待补充)':
            dir_stats[top]['has_summary'] += 1
        if r.get('keywords'):
            dir_stats[top]['has_keywords'] += 1
        if not r.get('summary') or r['summary'] == '(待补充)':
            dir_stats[top]['needs_fill'] += 1

    lines = [
        f'# 内容文件元数据提取汇总报告',
        '',
        f'> 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'> 文件总数: {total}',
        '',
        '## 📊 总体统计',
        '',
        '| 指标 | 数量 | 占比 |',
        '|:-----|-----:|-----:|',
        f'| 有概要 | {has_summary} | {has_summary/total*100:.1f}% |' if total else '',
        f'| 有关键词 | {has_keywords} | {has_keywords/total*100:.1f}% |' if total else '',
        f'| 有内部引用 | {has_internal_refs} | {has_internal_refs/total*100:.1f}% |' if total else '',
        f'| 有外部引用 | {has_external_refs} | {has_external_refs/total*100:.1f}% |' if total else '',
        f'| 有Changelog | {has_changelog} | {has_changelog/total*100:.1f}% |' if total else '',
        f'| **需AI补全** | **{needs_fill}** | **{needs_fill/total*100:.1f}%** |' if total else '',
        '',
        '## 📁 按目录统计',
        '',
        '| 目录 | 总数 | 有概要 | 有关键词 | 需补全 |',
        '|:-----|-----:|------:|--------:|------:|',
    ]
    for dir_name in sorted(dir_stats.keys()):
        s = dir_stats[dir_name]
        lines.append(f'| {dir_name} | {s["total"]} | {s["has_summary"]} | {s["has_keywords"]} | {s["needs_fill"]} |')

    output_path.write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='知识内容文件元数据提取工具')
    parser.add_argument('target', nargs='?', default='knowledge/', help='目标文件或目录')
    parser.add_argument('--all', action='store_true', help='处理 knowledge/ 下全部内容文件')
    parser.add_argument('--module', help='处理指定模块目录')
    parser.add_argument('--filter', help='过滤条件，如 "summary=(待补充)"')
    parser.add_argument('--output', help='输出文件路径（默认自动生成）')
    args = parser.parse_args()

    # Determine target
    if args.all:
        target = KNOWLEDGE_ROOT
    elif args.module:
        target = KNOWLEDGE_ROOT / args.module
    else:
        target = Path(args.target).resolve()
        if not target.is_absolute():
            target = REPO_ROOT / args.target

    if not target.exists():
        print(f'Error: {target} 不存在')
        sys.exit(1)

    files = norm.collect_files(target)
    if not files:
        print(f'No content files found under {target}')
        sys.exit(0)

    print(f'Extracting metadata from {len(files)} files...')

    # Extract metadata
    results = []
    for f in files:
        meta = extract_metadata(f)
        results.append(meta)

    # Apply filter
    if args.filter:
        filtered = []
        for r in results:
            if args.filter.startswith('summary='):
                val = args.filter[len('summary='):]
                if r.get('summary', '') == val:
                    filtered.append(r)
            elif args.filter.startswith('keywords='):
                val = args.filter[len('keywords='):]
                if r.get('keywords_str', '') == val:
                    filtered.append(r)
        results = filtered
        print(f'After filter "{args.filter}": {len(results)} files')

    # Output
    today = datetime.now().strftime('%Y-%m-%d')
    if args.output:
        output_path = Path(args.output)
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / f'content-metadata-{today}.json'

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f'\nJSON output: {output_path}')
    print(f'Total entries: {len(results)}')

    # Summary report
    if not args.filter:
        summary_path = output_path.with_name(output_path.stem + '-summary.md')
        generate_summary_report(results, summary_path)
        print(f'Summary report: {summary_path}')


if __name__ == '__main__':
    main()
