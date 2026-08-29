#!/usr/bin/env python3
"""
knowledge_health_check.py — Knowledge Base Health & Integrity Checker

Scans knowledge/ directory for:
  (A) LOG ORDER        — log.md files have time-descending entries in list format
  (B) LINK VALIDITY    — all local markdown links resolve to existing files
  (C) TABLE FORMAT     — markdown tables have consistent column counts and valid separators
  (D) FILE LOCATION    — files are in plausible directories based on naming patterns
  (E) MARKDOWN FORMAT  — box-drawing chars, CJK in code blocks, missing TOC/changelog
  (F) SUMMARY REPORT   — aggregated result with pass/fail per file per category

Usage:
  python3 knowledge_health_check.py                    # Check entire knowledge/
  python3 knowledge_health_check.py --path knowledge/  # Specific path
  python3 knowledge_health_check.py --categories A,B   # Only specific checks
  python3 knowledge_health_check.py --json             # JSON output
  python3 knowledge_health_check.py --verbose          # Show all, including passes
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

# ── Constants ──────────────────────────────────────────────────────────

# Knowledge base root (scripts/check/kb-health.py → knowledge/)
# Module directories (relative to knowledge/)
MODULES = {
    "01_survey":            {"label": "调研跟踪", "pattern": r"\d{4}-\d{2}-\d{2}"},
    "02_rd":                {"label": "研发"},
    "02_rd/00_rd-management": {"label": "研发管理"},
    "02_rd/01_basic-concepts": {"label": "基本概念"},
    "02_rd/02_system":      {"label": "系统设计"},
    "02_rd/03_hardware":    {"label": "硬件设计"},
    "02_rd/04_fullstack":   {"label": "全栈分析"},
    "02_rd/05_software":    {"label": "软件技术"},
    "02_rd/06_O&M":         {"label": "运维运营"},
    "02_rd/07_manufacturing": {"label": "生产制造"},
    "02_rd/08_chip":        {"label": "芯片"},
    "02_rd/09_supply-chain": {"label": "供应链"},
    "02_rd/21_solution":    {"label": "解决方案"},
    "02_rd/92_patent":      {"label": "专利"},
    "03_AI":                {"label": "AI技术原理"},
    "04_person":            {"label": "个人"},
    "05_tools":             {"label": "工具与行业"},
    "06_others":            {"label": "其他归档"},
    "07_industry-research": {"label": "行业调研跟踪"},
    "methodology":          {"label": "方法论"},
}

# Naming → expected module hints (file location reasonableness)
LOCATION_HINTS = [
    # Server/RD-related names → 02_rd
    (r'\b(server|ipd|tr\d|rd-management|hardware|bmc|firmware|redfish|pcie?|pci-express|'
     r'nvlink|nvswitch|cxl|cache-coherence|ddr|dram|hbm|ras\b|signal-integrity|serdes|'
     r'power-supply|liquid-cool|thermal|cable|connector|supernode|rdma|gpu-direct|'
     r'nccl|xccl|microservice|prometheus|dragonfly|linux-os|cloud-native|port-forward|'
     r'board-design|pcb|bom|hld|design-review|fru|cmdb|asset-management)',
     "02_rd"),

    # AI-related names → 03_AI
    (r'\b(ai-|agent|llm|llama|gpt|transformer|attention|kv-cache|moE|pagedattention|'
     r'vllm|rag|graphrag|embedding|vector-db|fine-tun|quantization|lora|nvidia-cmx|'
     r'cluster-training|inference|distributed-training|checkpoint|gemini|grok|'
     r'openai|claude|deepseek|moe-hardware|enterprise-ai)',
     "03_AI"),

    # Tool-related names → 05_tools
    (r'\b(git|github|gitlab|gitnexus|docker|playwright|linkedin-scraper|'
     r'numpy|goroutine|mutex|golang|rust-install|database-audit|etcd-raft|'
     r'openstack|ceph|event-wall|software-technology)',
     "05_tools"),

    # Other/misc → 06_others
    (r'\b(emoji-usage|职业发展|各年代大学生|camouflage-communication|'
     r'energy-storage|from-storage-to-energy)',
     "06_others"),
]

# Skip dirs
SKIP_DIRS = {'node_modules', '.git', '__pycache__', 'bak', 'site', 'tmp', '.history', 'weekly-reports'}

# Markdown link pattern: [text](path) but not ![image](path)
LINK_RE = re.compile(r'(?<!!)\[([^\]]*)\]\(([^)]+)\)')

# Date pattern for log files
DATE_HEADER_RE = re.compile(r'^##\s+(\d{4}-\d{2}-\d{2})')

# Log entry pattern
LOG_ENTRY_RE = re.compile(r'^- \*\*(.+?)\*\*')

# ── Report Data Structure ──────────────────────────────────────────────

class HealthReport:
    """Collects all issues found during scanning."""
    def __init__(self):
        self.issues = []   # list of dicts: {file, line, category, severity, code, msg, suggestion}
        self.stats = defaultdict(int)  # category → count

    def add(self, filepath, line, category, severity, code, message, suggestion=None):
        rel_path = str(filepath.relative_to(KNOWLEDGE_ROOT)) if KNOWLEDGE_ROOT in filepath.parents else str(filepath)
        self.issues.append({
            "file": rel_path,
            "line": line,
            "category": category,
            "severity": severity,
            "code": code,
            "message": message,
            "suggestion": suggestion or "",
        })
        self.stats[category] += 1

    def merge(self, other):
        self.issues.extend(other.issues)
        for k, v in other.stats.items():
            self.stats[k] += v

    def by_category(self, category):
        return [i for i in self.issues if i["category"] == category]

    def by_severity(self, severity):
        return [i for i in self.issues if i["severity"] == severity]

# ── Check (A): Log Order ──────────────────────────────────────────────

def check_log_order(filepath):
    """Verify log.md has time-descending order and proper entry format."""
    report = HealthReport()
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Extract date sections
    date_sections = []  # (line_number, date_string)
    for i, line in enumerate(lines):
        m = DATE_HEADER_RE.match(line.strip())
        if m:
            date_sections.append((i + 1, m.group(1)))

    # (A1) Check time-descending order
    dates = [d for _, d in date_sections]
    if dates:
        sorted_dates_desc = sorted(dates, reverse=True)
        if dates != sorted_dates_desc:
            for i in range(1, len(dates)):
                if dates[i] > dates[i-1]:
                    report.add(
                        filepath, date_sections[i][0], "A.LOG_ORDER", "ERROR", "A1-DATE-ORDER",
                        f"Date '{dates[i]}' appears before '{dates[i-1]}' (must be time-descending)",
                        f"Move section '## {dates[i]}' after '## {dates[i-1]}' or merge entries"
                    )

    # (A2) Check entries within date sections are in list format
    # For each date section, check the lines between this section and the next
    for idx, (start_line, date) in enumerate(date_sections):
        # Find end: next date section or end of file
        end_line = date_sections[idx + 1][0] if idx + 1 < len(date_sections) else len(lines) + 1

        for line_num in range(start_line, end_line - 1):
            line = lines[line_num - 1].strip()
            if not line or line.startswith('#') or line.startswith('>'):
                continue
            # Check if it looks like content but not in proper list format
            if not line.startswith('- ') and not line.startswith('  ') and not line.startswith('|'):
                # Could be a stray description line
                pass

    # (A3) Check for blank date sections (no entries)
    for idx, (start_line, date) in enumerate(date_sections):
        end_line = date_sections[idx + 1][0] if idx + 1 < len(date_sections) else len(lines) + 1
        has_entry = False
        for line_num in range(start_line + 1, end_line - 1):
            line = lines[line_num - 1].strip()
            if line.startswith('- '):
                has_entry = True
                break
        if not has_entry:
            report.add(
                filepath, start_line, "A.LOG_ORDER", "WARN", "A3-EMPTY-SECTION",
                f"Date section '## {date}' has no entries",
                "Add at least one entry or remove the empty section"
            )

    # (A4) Check entry format consistency (each top-level entry should start with - **...**)
    for idx, (start_line, date) in enumerate(date_sections):
        end_line = date_sections[idx + 1][0] if idx + 1 < len(date_sections) else len(lines) + 1
        for line_num in range(start_line + 1, end_line - 1):
            line = lines[line_num - 1]
            stripped = line.strip()
            # Skip blank, headers, blockquotes, and indented sub-items (2+ spaces)
            if not stripped or stripped.startswith('#') or stripped.startswith('>'):
                continue
            orig_indent = len(line) - len(line.lstrip())
            # Only check top-level list items (not indented sub-items)
            if stripped.startswith('- ') and orig_indent == 0:
                if not re.match(r'^- \*\*', stripped):
                    report.add(
                        filepath, line_num, "A.LOG_ORDER", "WARN", "A4-ENTRY-FORMAT",
                        f"Top-level entry not in bold-format. Expected: '- **操作** ...'",
                        f"Format entries as: '- **操作** 📍 `path` — description'"
                    )

    return report

# ── Check (B): Link Validity ──────────────────────────────────────────

def check_links(filepath):
    """Scan file for local markdown links and verify they resolve."""
    report = HealthReport()
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        for match in LINK_RE.finditer(line):
            text, link = match.group(1), match.group(2)

            # Skip URLs, anchors, absolute paths starting with /
            if link.startswith(('http://', 'https://', 'ftp://', 'mailto:', '#', '/')):
                continue
            if '://' in link:
                continue

            # Skip non-.md files (images, etc.)
            ext = Path(link).suffix.lower()
            if ext and ext not in ('.md', '.py', '.sh', '.json', '.yaml', '.yml', '.txt', '.csv'):
                continue

            # Remove anchor
            clean_link = link.split('#')[0]
            if not clean_link:
                continue

            # Resolve relative to file's directory
            resolved = (filepath.parent / clean_link).resolve()

            # Try with .md if no extension
            if not resolved.suffix:
                for try_ext in ['.md', '.py', '.sh']:
                    candidate = resolved.with_suffix(try_ext)
                    if candidate.exists():
                        resolved = candidate
                        break

            if not resolved.exists():
                report.add(
                    filepath, i, "B.LINKS", "ERROR", "B1-BROKEN-LINK",
                    f"Broken link: [{text}]({link}) → not found at {resolved}",
                    f"Expected target: `{resolved}`"
                )

    return report

# ── Check (C): Table Format ───────────────────────────────────────────

def check_tables(filepath):
    """Validate markdown table structure."""
    report = HealthReport()
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    in_table = False
    table_start = 0
    first_row_cols = 0
    has_separator = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect table row: must start with |
        if stripped.startswith('|') and stripped.endswith('|'):
            cols = len([c for c in stripped.split('|') if c.strip() or c == ''])

            # Check if it's a separator row (contains ---)
            is_separator = '---' in stripped or '---' in stripped.replace(' ', '')

            if not in_table:
                in_table = True
                table_start = i
                first_row_cols = cols
                has_separator = False
            else:
                if is_separator:
                    has_separator = True
                    # Check separator format: | --- | --- | or | :--- | :--: | ---: |
                    sep_parts = [p.strip() for p in stripped.split('|')][1:-1]
                    for j, part in enumerate(sep_parts):
                        valid_sep = re.match(r'^:?-{3,}:?$', part.replace(' ', '')) if part else False
                        if part and not valid_sep and part != '':
                            report.add(
                                filepath, i, "C.TABLES", "WARN", "C1-BAD-SEPARATOR",
                                f"Invalid table separator: '{part}' in column {j+1}",
                                "Use | --- | :--- | :--: | ---: | format"
                            )

                    # Check column count matches first row
                    if cols != first_row_cols:
                        report.add(
                            filepath, i, "C.TABLES", "ERROR", "C2-COL-MISMATCH",
                            f"Table separator has {cols} columns but header has {first_row_cols}",
                            f"Adjust separator to have {first_row_cols} columns"
                        )
                else:
                    # Data row: check column count matches
                    if cols != first_row_cols and has_separator:
                        report.add(
                            filepath, i, "C.TABLES", "ERROR", "C2-COL-MISMATCH",
                            f"Table row has {cols} columns but header has {first_row_cols}",
                            f"Add or remove columns to match: expected {first_row_cols}"
                        )
        else:
            if in_table:
                # Table ended, verify we had a separator
                if not has_separator and first_row_cols > 1:
                    report.add(
                        filepath, table_start, "C.TABLES", "WARN", "C3-NO-SEPARATOR",
                        f"Table starting at line {table_start} has no separator row",
                        "Add a separator row after the header: | --- | --- |"
                    )
                in_table = False
                first_row_cols = 0
                has_separator = False

    return report

# ── Check (D): File Location Reasonableness ───────────────────────────

def check_location(filepath):
    """Check if file is in a plausible directory based on its name."""
    report = HealthReport()
    rel_path = filepath.relative_to(KNOWLEDGE_ROOT)
    parts = list(rel_path.parts)

    # Only check files in known modules
    if not parts or parts[0] not in MODULES:
        return report

    current_module = parts[0]
    filename = filepath.stem  # without extension

    # Skip index.md, log.md, README.md, GUIDE.md
    if filename in ('index', 'log', 'README', 'guide', 'GUIDE'):
        return report

    # Skip tracking logs (YYYY-MM-DD format)
    if re.match(r'^\d{4}-\d{2}-\d{2}', filename):
        return report

    # Check each location hint
    for pattern, expected_module in LOCATION_HINTS:
        if re.search(pattern, filename, re.IGNORECASE):
            if current_module == "03_AI" and expected_module == "02_server":
                # AI files about server should be in AI if they're AI-related
                continue
            if current_module != expected_module:
                report.add(
                    filepath, 1, "D.LOCATION", "WARN", "D1-MISPLACED",
                    f"File '{filename}' matches pattern for {expected_module}/ "
                    f"but is in {current_module}/",
                    f"Consider moving to knowledge/{expected_module}/"
                )
            break  # Only report first match

    return report

# ── Check (E): Markdown Format ────────────────────────────────────────

def check_markdown_format(filepath):
    """Check markdown formatting issues: box-drawing, CJK in code, TOC/changelog."""
    report = HealthReport()
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    total_lines = len(lines)

    in_code_block = False
    code_lang = ''

    BOX_DRAWING = set('┌┐└┘├┤─│╋━┃┏┛┗┓┳╋╂╇▔▁┃')
    BLOCK_FILLERS = set('░█▓▌▐▀▄▖▗▘▙▚▛▜▝▞▟')
    CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3000-\u303f\uff00-\uffef]')

    for i, line in enumerate(lines, 1):
        # Track code blocks
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lang = line[3:].strip()
            else:
                in_code_block = False
            continue

        if in_code_block:
            # (E1) Box-drawing Unicode in code blocks
            if any(ch in BOX_DRAWING for ch in line):
                report.add(
                    filepath, i, "E.FORMAT", "ERROR", "E1-BOX-DRAW",
                    "Box-drawing Unicode character found in code block",
                    "Replace with ASCII: '+' '-' '|' '='"
                )

            # (E2) Block fillers
            if any(ch in BLOCK_FILLERS for ch in line):
                report.add(
                    filepath, i, "E.FORMAT", "ERROR", "E2-BLOCK-FILL",
                    "Block filler character in code block",
                    "Replace with '#' or '.'"
                )

            # (E3) Chinese in code block
            if CJK_RE.search(line) and not line.strip().startswith('>'):
                stripped = line.strip()
                if stripped and not stripped.startswith('|') and not stripped.startswith('#'):
                    report.add(
                        filepath, i, "E.FORMAT", "WARN", "E3-CJK-IN-CODE",
                        "Chinese text in code block (will cause misalignment)",
                        "Move Chinese outside ``` block; use English inside"
                    )

    # (E4) Missing TOC in long files (>100 lines)
    if total_lines > 100:
        head = '\n'.join(lines[:40]).lower()
        has_toc = any(kw in head for kw in
            ['目录', 'toc', 'table of contents', 'content', 'navigation',
             '## 1.', '## 2.', '## 一、', '## 二、'])
        if not has_toc and not filepath.name.endswith('log.md'):
            report.add(
                filepath, 1, "E.FORMAT", "WARN", "E4-NO-TOC",
                f"File with {total_lines} lines lacks Table of Contents",
                "Add a TOC section at top with links to major sections"
            )

    # (E5) Missing changelog in very long files (>200 lines, not log.md)
    if total_lines > 200 and not filepath.name.endswith('log.md') and \
       filepath.parent.name not in ('bak',):
        tail = '\n'.join(lines[-30:]).lower()
        has_cl = any(kw in tail for kw in
            ['changelog', 'change log', '变更记录', '修订记录', '修订历史',
             '版本历史', '历史记录', '版本记录'])
        if not has_cl:
            report.add(
                filepath, 1, "E.FORMAT", "WARN", "E5-NO-CHANGELOG",
                f"File with {total_lines} lines lacks changelog at bottom",
                "Add '## 📝 变更记录' section at bottom with time-stamped entries"
            )

    # (E6) Code block without language specified
    in_block = False
    for i, line in enumerate(lines, 1):
        if line.startswith('```'):
            if not in_block:
                in_block = True
                lang = line[3:].strip()
                if not lang:
                    report.add(
                        filepath, i, "E.FORMAT", "WARN", "E6-NO-LANG",
                        "Code fence without language specification",
                        "Add language: ```python, ```bash, ```yaml, etc."
                    )
            else:
                in_block = False

    return report

# ── Scanner ────────────────────────────────────────────────────────────

def scan_file(filepath, categories):
    """Run all applicable checks on a single file."""
    report = HealthReport()

    if filepath.suffix != '.md':
        return report

    rel_path = str(filepath.relative_to(KNOWLEDGE_ROOT))

    # Skip non-content directories
    if any(part in SKIP_DIRS for part in filepath.parts):
        return report
    if filepath.parent.name in SKIP_DIRS:
        return report

    # (A) Log checks — only for *log.md files
    if 'A' in categories and filepath.name == 'log.md':
        r = check_log_order(filepath)
        report.merge(r)

    # (B) Link checks — all .md files
    if 'B' in categories and filepath.name not in ('log.md',):
        r = check_links(filepath)
        report.merge(r)

    # (C) Table checks — all .md files
    if 'C' in categories:
        r = check_tables(filepath)
        report.merge(r)

    # (D) Location checks — all .md files
    if 'D' in categories:
        r = check_location(filepath)
        report.merge(r)

    # (E) Format checks — all .md files
    if 'E' in categories:
        r = check_markdown_format(filepath)
        report.merge(r)

    return report

# ── Reporters ──────────────────────────────────────────────────────────

def format_report(report, verbose=False):
    """Generate a human-readable health check report."""
    lines = []
    lines.append("=" * 68)
    lines.append("  📋 Knowledge Base Health Check Report")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 68)
    lines.append("")

    # Summary by category
    cat_labels = {
        "A.LOG_ORDER":  "A. Log Order",
        "B.LINKS":      "B. Link Validity",
        "C.TABLES":     "C. Table Format",
        "D.LOCATION":   "D. File Location",
        "E.FORMAT":     "E. Markdown Format",
    }

    if report.stats:
        lines.append("  📊 Summary by Check Category:")
        lines.append(f"  {'Category':<25} {'Issues':>8} {'Files':>8}")
        lines.append(f"  {'─'*25} {'─'*8} {'─'*8}")
        for cat_key, label in cat_labels.items():
            count = report.stats.get(cat_key, 0)
            files_in_cat = len(set(i["file"] for i in report.issues if i["category"] == cat_key))
            if count > 0 or verbose:
                lines.append(f"  {label:<25} {count:>8} {files_in_cat:>8}")
        lines.append("")
        lines.append(f"  ** Total: {len(report.issues)} issues in "
                     f"{len(set(i['file'] for i in report.issues))} files **")
    else:
        lines.append("  ✅ No issues found!")
    lines.append("")

    # Issues by severity
    errors = report.by_severity("ERROR")
    warns = report.by_severity("WARN")

    if errors:
        lines.append(f"  🔴 ERRORS ({len(errors)}):")
        lines.append(f"  {'─'*60}")
        for i in errors:
            lines.append(f"  [{i['code']}] {i['file']}:{i['line']}")
            lines.append(f"     {i['message']}")
            if i['suggestion']:
                lines.append(f"     💡 {i['suggestion']}")
            lines.append("")
    else:
        lines.append("  ✅ No errors found.")
        lines.append("")

    if warns:
        lines.append(f"  🟡 WARNINGS ({len(warns)}):")
        lines.append(f"  {'─'*60}")
        for i in warns:
            lines.append(f"  [{i['code']}] {i['file']}:{i['line']}")
            lines.append(f"     {i['message']}")
            if i['suggestion']:
                lines.append(f"     💡 {i['suggestion']}")
            lines.append("")

    # Per-file summary (if verbose)
    if verbose:
        files_with_issues = defaultdict(list)
        for issue in report.issues:
            files_with_issues[issue["file"]].append(issue)

        if files_with_issues:
            lines.append(f"  {'─'*60}")
            lines.append("  📁 Per-File Summary:")
            for fname in sorted(files_with_issues.keys()):
                issues = files_with_issues[fname]
                n_err = sum(1 for i in issues if i["severity"] == "ERROR")
                n_warn = sum(1 for i in issues if i["severity"] == "WARN")
                status = "❌" if n_err > 0 else "⚠️" if n_warn > 0 else "✅"
                lines.append(f"  {status} {fname} ({n_err}E/{n_warn}W)")
            lines.append("")

    lines.append("=" * 68)
    return '\n'.join(lines)


def json_report(report):
    """Generate JSON output."""
    return json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total_issues": len(report.issues),
        "affected_files": len(set(i["file"] for i in report.issues)),
        "by_category": dict(report.stats),
        "issues": report.issues,
    }, indent=2, ensure_ascii=False)


def print_file_summary(report):
    """Print a compact one-line-per-file summary."""
    files = defaultdict(lambda: {"errors": 0, "warns": 0})
    for issue in report.issues:
        files[issue["file"]][issue["severity"].lower() + "s"] += 1

    print(f"{'Status':<8} {'Errors':<8} {'Warns':<8} File")
    print("-" * 60)
    for fname in sorted(files.keys()):
        f = files[fname]
        status = "❌" if f["errors"] > 0 else "⚠️" if f["warns"] > 0 else "✅"
        print(f"{status:<8} {f['errors']:<8} {f['warns']:<8} {fname}")
    print()
    total_err = sum(f["errors"] for f in files.values())
    total_warn = sum(f["warns"] for f in files.values())
    print(f"Total: {total_err} errors, {total_warn} warnings in {len(files)} files")


# ── Main ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Knowledge Base Health & Integrity Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 knowledge_health_check.py                        # Full check
  python3 knowledge_health_check.py --path knowledge/03_AI # Check one module
  python3 knowledge_health_check.py --categories B,C       # Links + Tables only
  python3 knowledge_health_check.py --json                 # JSON output
  python3 knowledge_health_check.py --verbose              # Show all details
  python3 knowledge_health_check.py --summary              # Compact per-file
  python3 knowledge_health_check.py --fix-log              # Auto-fix log.md order
        """
    )
    parser.add_argument('--path', help='Specific file or directory to check (relative to knowledge/)')
    parser.add_argument('--categories', help='Comma-separated categories: A(Log), B(Links), C(Tables), D(Location), E(Format)')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all details including passes')
    parser.add_argument('--summary', action='store_true', help='Print compact per-file summary')
    parser.add_argument('--fix-log', action='store_true', help='Auto-reorder log.md sections to time-descending')
    args = parser.parse_args()

    # Determine scan path
    if args.path:
        p = args.path
        # Accept knowledge/xxx, ./knowledge/xxx, or just xxx (relative to knowledge/)
        p = p.replace('./knowledge/', '').replace('knowledge/', '')
        scan_path = (KNOWLEDGE_ROOT / p).resolve()
        if not scan_path.exists():
            print(f"❌ Path not found: {scan_path}", file=sys.stderr)
            return 1
    else:
        scan_path = KNOWLEDGE_ROOT

    # Determine categories
    if args.categories:
        cats = set(args.categories.upper().replace(' ', '').split(','))
        valid = {'A', 'B', 'C', 'D', 'E'}
        cats = cats & valid
    else:
        cats = {'A', 'B', 'C', 'D', 'E'}

    # Collect files
    files = []
    if scan_path.is_file():
        files.append(scan_path)
    else:
        for p in scan_path.rglob('*.md'):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            files.append(p)

    files.sort(key=lambda p: str(p))
    print(f"🔍 Scanning {len(files)} markdown files... (categories: {','.join(sorted(cats))})")
    print(f"   Knowledge root: {KNOWLEDGE_ROOT}")
    print()

    # Scan all files
    report = HealthReport()
    for f in files:
        r = scan_file(f, cats)
        report.merge(r)

    # Handle --fix-log
    if args.fix_log:
        fixed = fix_log_order(files)
        if fixed > 0:
            print(f"🔧 Auto-fixed {fixed} log.md files")

    # Output
    if args.json:
        print(json_report(report))
    elif args.summary:
        print_file_summary(report)
    else:
        print(format_report(report, args.verbose))

    return 0 if len(report.issues) == 0 else 1


def fix_log_order(files):
    """Auto-reorder log.md sections to time-descending order."""
    fixed_count = 0
    for filepath in files:
        if filepath.name != 'log.md':
            continue
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Find all date sections
        sections = []  # [(start_idx, date, content_lines)]
        current_start = None
        current_date = None
        current_lines = []

        for i, line in enumerate(lines):
            m = DATE_HEADER_RE.match(line.strip())
            if m:
                if current_start is not None:
                    sections.append((current_start, current_date, current_lines))
                current_start = i
                current_date = m.group(1)
                current_lines = [line]
            else:
                if current_start is not None:
                    current_lines.append(line)

        if current_start is not None:
            sections.append((current_start, current_date, current_lines))

        # Check if already sorted
        dates = [s[1] for s in sections]
        if dates == sorted(dates, reverse=True):
            continue  # Already correct order

        # Check if there's a preamble (lines before first date section)
        preamble = lines[:sections[0][0]] if sections else lines

        # Sort sections by date descending
        sections.sort(key=lambda s: s[1], reverse=True)

        # Rebuild
        new_lines = list(preamble)
        for _, _, section_lines in sections:
            new_lines.extend(section_lines)

        # Don't add trailing newline
        while new_lines and new_lines[-1] == '':
            new_lines.pop()

        filepath.write_text('\n'.join(new_lines), encoding='utf-8')
        fixed_count += 1
        print(f"   ✅ Fixed: {filepath.relative_to(KNOWLEDGE_ROOT)}")

    return fixed_count


if __name__ == '__main__':
    sys.exit(main())
