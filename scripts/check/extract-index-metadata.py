#!/usr/bin/env python3
"""
Extract metadata (title, description) from all .md files in a knowledge module.
Output a markdown table with file path, title, and one-line summary.

Usage:
    python3 scripts/check/extract-index-metadata.py knowledge/02_rd
    python3 scripts/check/extract-index-metadata.py knowledge/02_rd --format json
"""
import sys
import re
import json
from pathlib import Path

# Windows console encoding fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass


def extract_metadata(filepath: Path, root: Path) -> dict:
    """Extract title and summary from a markdown file."""
    rel_path = str(filepath.relative_to(root)).replace('\\', '/')
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return {'path': rel_path, 'title': '', 'summary': '(read error)', 'lines': 0}

    lines = content.split('\n')
    title = ''
    summary = ''

    # Extract title from first # heading
    for line in lines[:20]:
        if line.startswith('# ') and not line.startswith('## '):
            title = line[2:].strip()
            break

    # Extract summary: first non-empty line after title that's not a rule/metadata
    found_title = False
    for line in lines[:50]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('# ') and not stripped.startswith('## '):
            found_title = True
            continue
        if found_title or not title:
            # Skip metadata lines
            if stripped.startswith('>'): continue
            if stripped.startswith('---'): continue
            if stripped.startswith('|'): continue
            if stripped.startswith('```'): continue
            if stripped.startswith('!['): continue
            if stripped.startswith('-'): continue
            if stripped.startswith('*'): continue
            # Found summary candidate
            if not summary and len(stripped) > 10:
                summary = stripped[:200]
                break

    # Fallback: use filename if no title
    if not title:
        title = filepath.stem.replace('-', ' ').replace('_', ' ')

    # Clean summary
    if summary:
        # Remove markdown formatting
        summary = re.sub(r'\*\*([^*]+)\*\*', r'\1', summary)
        summary = re.sub(r'`([^`]+)`', r'\1', summary)
        summary = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', summary)
        summary = summary.rstrip('。.')  # Remove trailing period for table format

    return {
        'path': rel_path,
        'title': title,
        'summary': summary or '(无描述)',
        'lines': len(lines),
        'size_kb': round(filepath.stat().st_size / 1024, 1)
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: extract-index-metadata.py <module_dir> [--format json|md]")
        sys.exit(1)

    module_dir = Path(sys.argv[1])
    if not module_dir.is_dir():
        print(f"Error: {module_dir} is not a directory")
        sys.exit(1)

    output_format = 'md'
    if '--format' in sys.argv:
        idx = sys.argv.index('--format')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    # Collect all .md files (excluding index.md, log.md, README.md)
    files = []
    for p in sorted(module_dir.rglob('*.md')):
        if p.name in ('index.md', 'log.md', 'README.md'):
            continue
        if '.bak' in p.parts:
            continue
        files.append(p)

    # Extract metadata
    results = []
    for f in files:
        results.append(extract_metadata(f, module_dir))

    # Output
    if output_format == 'json':
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # Group by top-level directory
        from collections import defaultdict
        groups = defaultdict(list)
        for r in results:
            top = r['path'].split('/')[0] if '/' in r['path'] else '(root)'
            groups[top].append(r)

        print(f"# Metadata extraction for {module_dir}")
        print(f"# Total: {len(results)} files")
        print()
        for group_name in sorted(groups.keys()):
            items = groups[group_name]
            print(f"## {group_name} ({len(items)} files)")
            print()
            print(f"| File | Title | Summary | Lines | Size(KB) |")
            print(f"|:-----|:------|:--------|------:|---------:|")
            for r in items:
                print(f"| `{r['path']}` | {r['title'][:60]} | {r['summary'][:100]} | {r['lines']} | {r['size_kb']} |")
            print()


if __name__ == '__main__':
    main()
