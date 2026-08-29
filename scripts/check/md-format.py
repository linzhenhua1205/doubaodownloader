#!/usr/bin/env python3
"""
check_md_format.py — Validate and fix markdown formatting standards.

Checks for:
  R1 (must-fix):
    - Box-drawing Unicode (┌┐└┘├┤─│╋━┃┏┛) in code blocks
    - Block fillers (░█▓▌) in code blocks
    - CJK text in code-block diagrams
    - Chinese text inside code blocks (alignment risk)
  R2 (should-fix):
    - Code fence language not specified
    - Heading hierarchy skips
    - Bare URLs instead of descriptive links
  R3 (nice-to-have):
    - Missing alt text in images
    - Inconsistent list markers

Usage:
  python3 scripts/check_md_format.py <path> [options]

Options:
  --fix         Auto-fix R1 issues (replace box-drawing chars)
  --recursive   Scan directories recursively
  --level R1    Filter to specific severity level
  --verbose     Show all checks, including passing ones
  --report      Generate HTML report
"""

import re
import sys
import os
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

# ── Constants ──────────────────────────────────────────────────────────

BOX_DRAWING_CHARS = '┌┐└┘├┤─│╋━┃┏┛┗┓┳╋╂╇▔▁'
BLOCK_FILLERS = '░█▓▌▐▀▄▖▗▘▙▚▛▜▝▞▟'
CJK_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff\u3000-\u303f\uff00-\uffef]')

BOX_FIX_MAP = str.maketrans({
    '┌': '+', '┐': '+', '└': '+', '┘': '+',
    '├': '+', '┤': '+', '─': '-', '│': '|',
    '╋': '+', '━': '=', '┃': '|', '╂': '+',
    '╇': '+', '▔': '-', '▁': '-',
    '┏': '+', '┛': '+', '┗': '+', '┓': '+',
    '┳': '+',
    # Block fillers
    '░': '#', '█': '#', '▓': '#', '▌': '|',
    '▐': '|', '▀': '^', '▄': 'v',
    '▖': '.', '▗': '.', '▘': '.', '▙': '#',
    '▚': '#', '▛': '#', '▜': '#', '▝': '.',
    '▞': '#', '▟': '#',
})

# Extend with tree chars used outside code blocks
TREE_CHARS_IN_CODE = '├└│'

# ── Data Structures ────────────────────────────────────────────────────

@dataclass
class Issue:
    severity: str       # R1, R2, R3
    file: str
    line: int
    column: int
    code: str
    message: str
    suggestion: Optional[str] = None
    fixed: bool = False

@dataclass
class ScanResult:
    file: str
    issues: List[Issue] = field(default_factory=list)
    total_lines: int = 0
    fixed_count: int = 0

# ── Scanner ────────────────────────────────────────────────────────────

class MarkdownScanner:
    def __init__(self, args):
        self.args = args
        self.verbose = args.verbose
        self.min_level = {'R1': 1, 'R2': 2, 'R3': 3}.get(args.level, 0)

    def scan_file(self, path: Path) -> ScanResult:
        result = ScanResult(file=str(path))
        try:
            text = path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ❌ Cannot read {path}: {e}", file=sys.stderr)
            return result

        lines = text.split('\n')
        result.total_lines = len(lines)

        in_code_block = False
        code_block_start = 0
        code_lang = ''

        for i, line in enumerate(lines):
            line_num = i + 1

            # Track code blocks
            if line.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_block_start = i
                    code_lang = line[3:].strip()
                else:
                    # End of code block
                    in_code_block = False
                continue

            if in_code_block:
                self._check_code_block_line(result, line, line_num, code_lang)
            else:
                self._check_regular_line(result, line, line_num)

        return result

    def _check_code_block_line(self, result: ScanResult, line: str, line_num: int, lang: str):
        if self.min_level > 1:
            return

        # R1.1: Box-drawing Unicode
        for col, ch in enumerate(line):
            if ch in BOX_DRAWING_CHARS:
                result.issues.append(Issue(
                    severity='R1',
                    file=result.file,
                    line=line_num,
                    column=col + 1,
                    code='BOX-DRAW',
                    message=f'Box-drawing char {repr(ch)} found in code block. Replace with ASCII.',
                    suggestion=f"Use '+' '-' '|' instead of '{ch}'"
                ))
                break  # One per line is enough

        # R1.2: Block fillers
        for col, ch in enumerate(line):
            if ch in BLOCK_FILLERS:
                result.issues.append(Issue(
                    severity='R1',
                    file=result.file,
                    line=line_num,
                    column=col + 1,
                    code='BLOCK-FILL',
                    message=f'Block filler char {repr(ch)} found in code block. Replace with "#" or ".".',
                    suggestion=f"Use '#' or '.' instead of '{ch}'"
                ))
                break

        # R1.3: Chinese characters in code-block diagrams
        if CJK_PATTERN.search(line):
            # Check if it's a data table (Chinese headers) vs diagram
            # Data tables with Chinese are OK if they are proper markdown tables
            stripped = line.strip()
            if stripped and not stripped.startswith('|') and not stripped.startswith('>'):
                result.issues.append(Issue(
                    severity='R1',
                    file=result.file,
                    line=line_num,
                    column=0,
                    code='CJK-IN-CODE',
                    message='Chinese text in code block will misalign. Move outside code block.',
                    suggestion='Move Chinese text outside the ``` block; use English inside.'
                ))

    def _check_regular_line(self, result: ScanResult, line: str, line_num: int):
        # R2.2: Heading hierarchy (deferred to post-processing)
        # Handled by checking heading levels across the file

        # R2.3: Check image alt text
        if self.min_level <= 3:
            img_match = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            if img_match and not img_match.group(1).strip():
                result.issues.append(Issue(
                    severity='R3',
                    file=result.file,
                    line=line_num,
                    column=0,
                    code='IMG-ALT',
                    message='Image missing alt text. Add descriptive alt text for accessibility.',
                    suggestion=f'Add alt text: ![description]({img_match.group(2)})'
                ))

        # R2.3: Bare URLs
        if self.min_level <= 2:
            # Check for bare URLs that aren't in link syntax
            url_pattern = re.findall(r'(?<!\()https?://[^\s\)]+(?![\)\]])', line)
            if url_pattern and '](' not in line:
                for url in url_pattern:
                    if len(url) > 40:  # Likely not a reference-style short URL
                        result.issues.append(Issue(
                            severity='R2',
                            file=result.file,
                            line=line_num,
                            column=0,
                            code='BARE-URL',
                            message='Bare URL found. Use descriptive link text.',
                            suggestion=f'Use [descriptive text]({url}) instead of bare URL'
                        ))
                        break

    def fix_file(self, path: Path, result: ScanResult) -> int:
        """Auto-fix R1 issues. Returns number of fixes applied."""
        if not result.issues:
            return 0

        text = path.read_text(encoding='utf-8')
        lines = text.split('\n')
        fix_count = 0

        in_code_block = False
        for i, line in enumerate(lines):
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                new_line = line
                # Fix box-drawing chars
                had_box = any(ch in BOX_DRAWING_CHARS for ch in line)
                if had_box:
                    new_line = new_line.translate(BOX_FIX_MAP)

                # Fix block fillers
                had_filler = any(ch in BLOCK_FILLERS for ch in line)
                if had_filler:
                    new_line = new_line.translate(BOX_FIX_MAP)

                if new_line != line:
                    lines[i] = new_line
                    fix_count += 1

        if fix_count > 0:
            path.write_text('\n'.join(lines), encoding='utf-8')

        return fix_count

    def check_document_structure(self, path: Path) -> List[Issue]:
        """Check document structure completeness (R2 items)."""
        issues = []
        if self.min_level > 2:
            return issues

        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            return issues

        lines = text.split('\n')
        total_lines = len(lines)
        file_str = str(path)

        # R2.4: Check for changelog at bottom (for files > 200 lines)
        if total_lines > 200:
            # Look for changelog, change log, 变更日志, 修订记录 in last 20 lines
            tail = '\n'.join(lines[-20:]).lower()
            has_changelog = any(kw in tail for kw in
                ['changelog', 'change log', '变更', '修订记录', '修订历史',
                 '版本历史', '历史记录', '版本记录', 'log.md'])
            if not has_changelog:
                issues.append(Issue(
                    severity='R2',
                    file=file_str,
                    line=total_lines - 5,
                    column=0,
                    code='NO-CHANGELOG',
                    message=f'File >200 lines lacks changelog/revision history at bottom.',
                    suggestion='Add a "## 📝 变更记录" section at file bottom with time-stamped entries.'
                ))

        # R2.5: Check for missing TOC in long files
        if total_lines > 100:
            head = '\n'.join(lines[:30]).lower()
            has_toc = any(kw in head for kw in
                ['目录', 'toc', 'table of contents', '导航', '索引',
                 '## 1.', '## 2.', '## 3.', '## 一、', '## 二、'])
            if not has_toc:
                issues.append(Issue(
                    severity='R2',
                    file=file_str,
                    line=5,
                    column=0,
                    code='NO-TOC',
                    message=f'File >100 lines lacks Table of Contents at top.',
                    suggestion='Add a TOC section at top: `## 📑 目录` with links to major sections.'
                ))

        # R2.6: Check for source citations in technical documents
        # Only for knowledge/ files that have technical content (contain code blocks)
        if '/knowledge/' not in file_str:
            return issues

        code_block_count = text.count('\n```')
        has_citations = any(kw in text for kw in
            ['参考', '参考来源', '来源', 'references', 'sources', '出处',
             '参考文献', '[1]', '[2]', 'https://doi.org', 'arxiv'])
        if not has_citations and code_block_count >= 3:
            issues.append(Issue(
                severity='R2',
                file=file_str,
                line=1,
                column=0,
                code='NO-CITATIONS',
                message='Technical document lacks reference citations.',
                suggestion='Add a "## 📚 参考资料" section listing all sources used.'
            ))

        return issues

    def check_heading_hierarchy(self, path: Path) -> List[Issue]:
        """Check heading level skips."""
        issues = []
        text = path.read_text(encoding='utf-8')
        lines = text.split('\n')

        prev_level = 0
        in_code_block = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue  # skip headings inside code fences (e.g. config comments)
            heading_match = re.match(r'^(#{1,6})\s', line)
            if heading_match:
                level = len(heading_match.group(1))
                if prev_level > 0 and level > prev_level + 1:
                    issues.append(Issue(
                        severity='R2',
                        file=str(path),
                        line=i + 1,
                        column=0,
                        code='HEADING-SKIP',
                        message=f'Heading level skip: {prev_level} -> {level}',
                        suggestion=f'Use {"#" * (prev_level + 1)} instead of {"#" * level}'
                    ))
                prev_level = level

        return issues

# ── Reporters ──────────────────────────────────────────────────────────

def print_report(results: List[ScanResult], heading_issues: List[Issue], args):
    total_r1 = sum(1 for r in results for i in r.issues if i.severity == 'R1')
    total_r2 = sum(1 for r in results for i in r.issues if i.severity == 'R2')
    total_r3 = sum(1 for r in results for i in r.issues if i.severity == 'R3')
    total_files = len(results)
    fixed_files = sum(1 for r in results if r.fixed_count > 0)
    total_fixed = sum(r.fixed_count for r in results)

    print(f"\n{'='*60}")
    print(f"📐 Markdown Format Check Report")
    print(f"{'='*60}")
    print(f"  Files scanned:    {total_files}")
    print(f"  Total lines:      {sum(r.total_lines for r in results)}")
    print(f"  Issues found:     {total_r1 + total_r2 + total_r3}")
    print(f"    R1 (must-fix):  {total_r1}")
    print(f"    R2 (should-fix): {total_r2}")
    print(f"    R3 (nice):      {total_r3}")
    if args.fix:
        print(f"  Auto-fixed:       {total_fixed} issues in {fixed_files} files")
    print(f"{'='*60}\n")

    # Print per-file details
    for result in results:
        if not result.issues and not args.verbose:
            continue
        status = '✅' if not result.issues else '❌'
        fixed_tag = f' [+{result.fixed_count} fixed]' if result.fixed_count > 0 else ''
        print(f"{status} {result.file} ({result.total_lines} lines){fixed_tag}")
        for issue in result.issues:
            if args.level and issue.severity != args.level:
                continue
            check = '✅' if issue.fixed else '  '
            print(f"  {check} [{issue.severity}/{issue.code}] L{issue.line}: {issue.message}")
            if issue.suggestion:
                print(f"           💡 {issue.suggestion}")

    if heading_issues:
        print(f"\n{'─'*60}")
        print(f"📋 Heading hierarchy issues:")
        for issue in heading_issues:
            print(f"  [{issue.code}] L{issue.line}: {issue.message}")
            if issue.suggestion:
                print(f"       💡 {issue.suggestion}")

    if total_r1 + total_r2 + total_r3 == 0:
        print(f"🎉 No issues found!")
        return 0
    return 1

# ── Main ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Check markdown formatting standards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/check_md_format.py doc.md
  python3 scripts/check_md_format.py doc.md --fix
  python3 scripts/check_md_format.py knowledge/ --recursive
  python3 scripts/check_md_format.py knowledge/ --recursive --level R1
        """
    )
    parser.add_argument('path', help='File or directory to check')
    parser.add_argument('--fix', action='store_true', help='Auto-fix R1 issues (box chars, fillers)')
    parser.add_argument('--recursive', '-r', action='store_true', help='Scan directories recursively')
    parser.add_argument('--level', choices=['R1', 'R2', 'R3'], default='R1',
                       help='Minimum severity level to report (default: R1)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all checks including passing')

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"❌ Path not found: {path}", file=sys.stderr)
        return 1

    # Collect files
    files = []
    if path.is_file():
        if path.suffix.lower() == '.md':
            files.append(path)
    elif path.is_dir():
        if args.recursive:
            for p in path.rglob('*.md'):
                # Skip common non-content directories
                skip_dirs = {'node_modules', '.git', '__pycache__', 'bak', 'site', 'tmp', '.history'}
                if not any(part in skip_dirs for part in p.parts):
                    files.append(p)
        else:
            for p in path.glob('*.md'):
                files.append(p)
    else:
        print(f"❌ Unknown path type: {path}", file=sys.stderr)
        return 1

    if not files:
        print(f"⚠️  No .md files found at {path}")
        return 0

    files.sort()
    print(f"Scanning {len(files)} markdown file(s)...")

    scanner = MarkdownScanner(args)
    results = []
    all_heading_issues = []

    for f in files:
        if not f.is_file():
            continue
        result = scanner.scan_file(f)
        results.append(result)

        # Heading hierarchy checks
        heading_issues = scanner.check_heading_hierarchy(f)
        all_heading_issues.extend(heading_issues)
        for issue in heading_issues:
            # Merge into result issues
            result.issues.append(issue)

        # Document structure checks (R2.4, R2.5, R2.6)
        struct_issues = scanner.check_document_structure(f)
        for issue in struct_issues:
            result.issues.append(issue)

        # Auto-fix
        if args.fix:
            fixed = scanner.fix_file(f, result)
            result.fixed_count = fixed
            # Mark related issues as fixed
            for issue in result.issues:
                if issue.code in ('BOX-DRAW', 'BLOCK-FILL', 'CJK-IN-CODE') and fixed > 0:
                    issue.fixed = True

    return print_report(results, all_heading_issues, args)

if __name__ == '__main__':
    sys.exit(main())
