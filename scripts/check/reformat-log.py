#!/usr/bin/env python3
"""
Reformat knowledge log.md files into a consistent changelog format.

Standardizes (per workspace RULE.md):
  - Date headers: `## YYYY-MM-DD` (no suffixes, no sub-levels ###)
  - Entry format:  `- **操作** 📍 `路径` — 说明`
  - Chronological order (oldest first, 2026-08-15 起全局统一正序)
  - Merges duplicate date sections
  - Converts blockquotes (>), tables (|), plain bullets (- date:) to standard format
  - Date ranges (`## YYYY-MM-DD ~ YYYY-MM-DD`) preserved and placed at the end

Usage:
    python scripts/check/reformat-log.py knowledge/02_rd/log.md
    python scripts/check/reformat-log.py --all          # all knowledge/*/log.md
    python scripts/check/reformat-log.py --dry-run PATH # preview only
    python scripts/check/reformat-log.py --verify PATH  # check without writing
"""

import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

from scripts.shared.workspace import WORKSPACE_ROOT as REPO_ROOT

# Fix Windows console encoding (GBK can't handle emojis)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass


# === Regex patterns ===

# Date headers: ## 2026-07-01, ## 2026-07-01 — suffix, ### 2026-07-01
DATE_HEADER_RE = re.compile(r'^#{2,3}\s+(\d{4}-\d{2}-\d{2})(?:\s*[—\-–]\s*(.+))?\s*$')

# Date range: ## 2026-06-22 ~ 2026-06-17
DATE_RANGE_RE = re.compile(r'^#{2,3}\s+(\d{4}-\d{2}-\d{2})\s*[~～]\s*(\d{4}-\d{2}-\d{2})\s*.*$')

# Table row starting with date: | 2026-06-30 14:30 | path | op | desc |
TABLE_DATE_RE = re.compile(r'^\|\s*(\d{4}-\d{2}-\d{2})\s')

# Plain bullet with embedded date: - 2026-07-02: 新增...
PLAIN_DATE_BULLET_RE = re.compile(r'^-\s*(\d{4}-\d{2}-\d{2})[：:]\s*(.+)$')

# Date embedded in path/text (for inferring dates of undated entries)
FILE_DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')

# Standard entry: - **op** emoji `path` — desc
STANDARD_ENTRY_RE = re.compile(r'^-\s+\*\*(.+?)\*\*')

# Table separator row: |:---|:---|
TABLE_SEP_RE = re.compile(r'^\|[\s:|-]+\|*\s*$')

# Emoji to strip from log entries (align with index-log-normalizer: no-emoji rule)
EMOJI_RE = re.compile(
    '['
    '\U0001F300-\U0001F9FF'
    '\U0001FA00-\U0001FAFF'
    '\u2600-\u27BF'
    '\U0001F000-\U0001F02F'
    ']', flags=re.UNICODE)


def strip_emoji(s: str) -> str:
    """Remove emoji and collapse extra spaces (no-emoji rule per SKILL.md)."""
    return re.sub(r'\s+', ' ', EMOJI_RE.sub('', s)).strip()


def parse_log(content):
    """Parse log.md content into (header_lines, entries_by_date, range_sections).

    Returns:
        header_lines: list of lines to preserve verbatim (title + rules + ---)
        entries_by_date: dict {date_str: [entry_line, ...]} for single dates
        range_sections: list of (range_str, [entry_lines]) for date ranges
    """
    lines = content.split('\n')

    # 1. Extract header: everything before first date header or first `---`
    header_end = 0
    found_sep = False
    for i, line in enumerate(lines):
        if line.strip() == '---':
            header_end = i + 1
            found_sep = True
            break
        if DATE_HEADER_RE.match(line) or DATE_RANGE_RE.match(line):
            header_end = i
            found_sep = True
            break
        if i > 80:  # safety: header should be < 80 lines
            header_end = i
            found_sep = True
            break
    if not found_sep:
        header_end = 0

    header_lines = lines[:header_end]
    body_lines = lines[header_end:]

    # 2. Parse body
    entries_by_date = defaultdict(list)
    range_sections = []
    range_order = []  # track insertion order for ranges

    current_date = None
    current_entries = []
    is_range = False

    i = 0
    while i < len(body_lines):
        line = body_lines[i]

        # --- Date range header ---
        m = DATE_RANGE_RE.match(line)
        if m:
            # Flush previous section
            if current_date:
                if is_range:
                    range_sections.append((current_date, current_entries))
                else:
                    entries_by_date[current_date].extend(current_entries)
            current_date = f"{m.group(1)} ~ {m.group(2)}"
            current_entries = []
            is_range = True
            i += 1
            continue

        # --- Single date header (with or without suffix) ---
        m = DATE_HEADER_RE.match(line)
        if m:
            if current_date:
                if is_range:
                    range_sections.append((current_date, current_entries))
                else:
                    entries_by_date[current_date].extend(current_entries)
            current_date = m.group(1)  # strip suffix
            current_entries = []
            is_range = False
            i += 1
            continue

        # --- Plain bullet with date: "- 2026-07-02: text" ---
        m = PLAIN_DATE_BULLET_RE.match(line)
        if m:
            date = m.group(1)
            text = m.group(2)
            entry = f"- **新增** 📝 {text}"
            entries_by_date[date].append(entry)
            i += 1
            continue

        # --- Table row: "| date time | path | op | desc |" OR "| time | path | op | desc |" ---
        # Skip data/comparison tables (e.g., "| 升级维度 | 升级前 | 升级后 |")
        # by checking if the row looks like a log entry (path-like 2nd col + known op 3rd col)
        if line.startswith('|') and not TABLE_SEP_RE.match(line):
            parts = [p.strip() for p in line.split('|')]
            # parts[0] is empty (before first |), parts[-1] is empty (after last |)
            if len(parts) >= 5:
                first_col = parts[1]
                path = parts[2]
                op = parts[3]
                desc = parts[4]
                # Skip header rows
                if op.lower() in ('op', 'operation', '操作') or path.lower() in ('file', 'path', '文件', '文件/目录'):
                    i += 1
                    continue
                # Detect data/comparison tables: if 2nd col doesn't look like a path
                # AND 3rd col isn't a known op, treat as content (preserve as-is)
                looks_like_path = bool(re.search(r'[/\\]|\.\w{1,5}$|\.md$', path))
                known_ops = {'move', 'create', 'rename', 'merge', 'update', 'add',
                             'delete', 'archive', '移动', '创建', '重命名',
                             '合并', '更新', '新增', '删除', '归档', '迁入', '迁出', '新建'}
                is_known_op = op.lower() in known_ops
                # Also accept if first_col has a date (log entry table)
                first_has_date = bool(FILE_DATE_RE.search(first_col))
                if not first_has_date and not looks_like_path and not is_known_op:
                    # Data table row — preserve as continuation of current section
                    if current_date:
                        current_entries.append(line)
                    else:
                        entries_by_date['UNKNOWN'].append(line)
                    i += 1
                    continue
                # Determine date: from first column if it has date, else from current_date
                date_match = FILE_DATE_RE.search(first_col)
                if date_match:
                    date = date_match.group(1)
                elif current_date and not is_range:
                    date = current_date
                else:
                    i += 1
                    continue
                op_map = {'move': '移动', 'create': '创建', 'rename': '重命名',
                          'merge': '合并', 'update': '更新', 'add': '新增',
                          'delete': '删除', 'archive': '归档'}
                op_zh = op_map.get(op.lower(), op)
                emoji_map = {'移动': '📍', '创建': '🆕', '重命名': '📍',
                             '合并': '🔀', '更新': '🔄', '新增': '🆕',
                             '删除': '🗑️', '归档': '📦'}
                emoji = emoji_map.get(op_zh, '📍')
                # Include time if present in first column
                time_str = ''
                time_match = re.search(r'(\d{2}:\d{2})', first_col)
                if time_match:
                    time_str = f' (@{time_match.group(1)})'
                entry = f"- **{op_zh}** {emoji} `{path}` — {desc}{time_str}"
                entries_by_date[date].append(entry)
            i += 1
            continue

        # --- Blockquote entry: "> 🆕 path — desc" ---
        if line.startswith('>'):
            text = line.lstrip('>').strip()
            if not text:
                i += 1
                continue
            # Try to infer date from embedded date in path
            date_match = FILE_DATE_RE.search(text)
            if date_match:
                date = date_match.group(1)
                # Normalize: strip leading emoji if present, prepend standard format
                entry = f"- **新增** {text}"
                entries_by_date[date].append(entry)
            elif current_date:
                # Assign to current section
                current_entries.append(f"- **新增** {text}")
            else:
                entries_by_date['UNKNOWN'].append(f"- **新增** {text}")
            i += 1
            continue

        # --- Standard bullet entry: "- **op** emoji `path` — desc" ---
        if line.startswith('- '):
            if current_date:
                current_entries.append(line)
            else:
                # No date context — try to infer from content
                date_match = FILE_DATE_RE.search(line)
                if date_match:
                    entries_by_date[date_match.group(1)].append(line)
                else:
                    entries_by_date['UNKNOWN'].append(line)
            i += 1
            continue

        # --- Continuation lines (indented, sub-bullets, etc.) ---
        # Attach to the most recent entry in the current section
        if line.strip() and current_date:
            if current_entries:
                # Append as continuation
                current_entries.append(line)
            else:
                # Orphan line — try to infer date
                date_match = FILE_DATE_RE.search(line)
                if date_match:
                    entries_by_date[date_match.group(1)].append(f"- **更新** 📝 {line.strip()}")
                else:
                    current_entries.append(line)
        elif line.strip() and not current_date:
            # Orphan before any date header
            date_match = FILE_DATE_RE.search(line)
            if date_match:
                entries_by_date[date_match.group(1)].append(f"- **新增** 📝 {line.strip()}")

        # Skip empty lines
        i += 1

    # Flush last section
    if current_date:
        if is_range:
            range_sections.append((current_date, current_entries))
        else:
            entries_by_date[current_date].extend(current_entries)

    return header_lines, entries_by_date, range_sections


def sort_dates_asc(dates):
    """Sort dates chronologically (oldest first, 2026-08-15 起全局统一正序). Non-date strings go last."""
    dated = []
    other = []
    for d in dates:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', d):
            dated.append(d)
        else:
            other.append(d)
    dated.sort(reverse=False)
    # UNKNOWN always last
    other_sorted = sorted(other)
    if 'UNKNOWN' in other_sorted:
        other_sorted.remove('UNKNOWN')
        other_sorted.append('UNKNOWN')
    return dated + other_sorted


def reformat(content):
    """Reformat log.md content into clean changelog."""
    header, entries_by_date, range_sections = parse_log(content)

    out = list(header)
    # Ensure blank line after header
    if out and out[-1] != '' and out[-1] != '---':
        out.append('')

    # Single dates (sorted chronological, oldest first)
    for date in sort_dates_asc(entries_by_date.keys()):
        entries = entries_by_date[date]
        # Filter out empty entries; strip emoji to comply with no-emoji rule
        entries = [strip_emoji(e) for e in entries if e.strip()]
        entries = [e for e in entries if e]
        if not entries:
            continue
        if date == 'UNKNOWN':
            out.append('## 未知日期')
        else:
            out.append(f'## {date}')
        out.append('')
        out.extend(entries)
        out.append('')

    # Date ranges (sorted by start date, ascending)
    range_sections.sort(key=lambda x: x[0].split(' ~ ')[0], reverse=False)
    for range_str, entries in range_sections:
        entries = [strip_emoji(e) for e in entries if e.strip()]
        entries = [e for e in entries if e]
        if not entries:
            continue
        out.append(f'## {range_str}')
        out.append('')
        out.extend(entries)
        out.append('')

    # Trim trailing blank lines, add final newline
    while len(out) > 1 and out[-1] == '':
        out.pop()
    out.append('')

    return '\n'.join(out)


def verify(content):
    """Check format issues without modifying. Returns list of issues."""
    issues = []
    lines = content.split('\n')
    seen_dates = set()
    prev_date = None
    in_header = True

    for i, line in enumerate(lines, 1):
        # Header detection
        if in_header:
            if line.strip() == '---':
                in_header = False
            continue

        m = DATE_HEADER_RE.match(line)
        if m:
            date = m.group(1)
            suffix = m.group(2)
            if suffix:
                issues.append(f"L{i}: date header has suffix '— {suffix}' (should be plain `## {date}`)")
            if date in seen_dates:
                issues.append(f"L{i}: duplicate date header `## {date}` (should be merged)")
            seen_dates.add(date)
            if prev_date and date > prev_date:
                issues.append(f"L{i}: out-of-order date `{date}` (after `{prev_date}`, should be chronological (oldest first))")
            prev_date = date
            continue

        m = DATE_RANGE_RE.match(line)
        if m:
            prev_date = m.group(1)
            continue

        # Sub-level date header
        if re.match(r'^###\s+\d{4}-\d{2}-\d{2}', line):
            issues.append(f"L{i}: sub-level date header `###` (should be `##`)")
            continue

        # Blockquote entry in body
        if line.startswith('>') and line.strip() != '>' and not line.startswith('> -'):
            issues.append(f"L{i}: blockquote entry `> ...` (should be `- **新增** ...`)")
            continue

        # Table row in body
        if line.startswith('|') and not TABLE_SEP_RE.match(line):
            issues.append(f"L{i}: table row (should be converted to bullet entry)")

    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Reformat knowledge log.md files into consistent changelog format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python scripts/check/reformat-log.py knowledge/02_rd/log.md
  python scripts/check/reformat-log.py --all
  python scripts/check/reformat-log.py --dry-run knowledge/02_rd/log.md
  python scripts/check/reformat-log.py --verify knowledge/02_rd/log.md
""")
    parser.add_argument('path', nargs='?', help='Path to log.md file')
    parser.add_argument('--all', action='store_true', help='Process all knowledge/*/log.md files')
    parser.add_argument('--dry-run', action='store_true', help='Preview result without writing')
    parser.add_argument('--verify', action='store_true', help='Check for format issues without modifying')
    args = parser.parse_args()

    if args.all:
        repo_root = REPO_ROOT
        kb_dir = repo_root / 'knowledge'
        files = sorted(kb_dir.glob('*/log.md'))
        if not files:
            print(f"No log.md files found under {kb_dir}")
            sys.exit(1)
    elif args.path:
        files = [Path(args.path)]
        if not files[0].exists():
            print(f"File not found: {files[0]}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    for log_file in files:
        print(f"\n📄 {log_file}")
        content = log_file.read_text(encoding='utf-8')
        orig_lines = content.count('\n') + 1

        if args.verify:
            issues = verify(content)
            if issues:
                print(f"   ⚠️  {len(issues)} format issue(s) found:")
                for issue in issues[:20]:
                    print(f"      {issue}")
                if len(issues) > 20:
                    print(f"      ... and {len(issues) - 20} more")
            else:
                print("   ✅ No format issues found")
            continue

        new_content = reformat(content)
        new_lines = new_content.count('\n') + 1
        print(f"   {orig_lines} → {new_lines} lines")

        if args.dry_run:
            # Show first 30 lines of result
            print("   --- Preview (first 30 lines) ---")
            for line in new_content.split('\n')[:30]:
                print(f"   | {line}")
            print("   ---")
            print("   (dry-run, no changes written)")
        else:
            log_file.write_text(new_content, encoding='utf-8')
            print("   ✅ Reformatted")


if __name__ == '__main__':
    main()
