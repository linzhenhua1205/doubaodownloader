#!/usr/bin/env python3
"""
link-validator.py — Knowledge Base Markdown Link Validator

Scans knowledge/ markdown files for ALL types of reference issues:

  [Rendered Links]  [text](relative/path.md) — standard markdown links
  [Bare Paths]      knowledge/01_survey/xxx.md — text references that should be links
  [External Ref]    ../knowledge/xxx.md — cross-directory references

Classifies broken links into categories for smart fixing:
  DEPTH       — wrong relative path depth (too many/few ../)
  MOVED       — target exists elsewhere in knowledge/
  DIR_RENAME  — directory was renamed
  EXTERNAL    — bare path reference NOT as markdown link
  MISSING     — file truly doesn't exist anywhere in knowledge/

Usage:
    python3 scripts/check/link-validator.py                          # Full scan
    python3 scripts/check/link-validator.py --module 06_superpod     # Per-module
    python3 scripts/check/link-validator.py --file index.md          # Single file
    python3 scripts/check/link-validator.py --report                 # Summary
    python3 scripts/check/link-validator.py --classify               # Classify errors
    python3 scripts/check/link-validator.py --json                   # Machine output
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

# ── Constants ──────────────────────────────────────────────────────────────────

# Knowledge base root (this script is at scripts/check/link-validator.py)
# Link pattern: [text](path) excluding ![image](path)
# NOTE (2026-08-05): URL 可能内含括号（如 `英伟达(NVIDIA)的收购历程.md`），
# 旧正则 `([^)]+)` 会在第一个 `)` 截断 → 修复器降级时产生残缺残留
# （案例：2026-06-23-product-design-guide.md:1214 正则误匹配 BUG，已修复）。
# 现支持一层嵌套括号，完整匹配 URL；`![]` 图片链接仍被负向后行排除。
LINK_RE = re.compile(r'(?<!!)\[([^\]]*)\]\(((?:[^()]|\([^)]*\))+)\)')  # noqa: E501

# 残缺链接残留检测: `.md)` 前最近的 `(` 不构成 `](` 结构 → 修复残留/格式破坏
# （如 `xxx战略演进.md)` 无配对开括号）。用于发现"链接降级截断"类遗留。
TRUNCATED_RE = re.compile(r'\.md\)')

# Bare path pattern: knowledge/xxx.md or ../knowledge/xxx.md references in text
BARE_PATH_RE = re.compile(
    r'(?:^|\s)((?:\w+/)*[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*\.md)(?:\s|$|[,;:.!?])',
    re.MULTILINE
)

# Skip dirs
SKIP_DIRS = {'node_modules', '.git', '__pycache__', 'bak', 'site', 'tmp', '.history', 'weekly-reports', '__pycache__', 'oldbak'}

# Known module directories in knowledge/
KNOWN_MODULES = [
    '01_survey', '02_rd', '03_AI', '04_person', '05_tools',
    '06_others', '07_industry-research', 'methodology',
    'architectures', 'concepts', 'analysis', 'entities'
]

# ── Link Classification ───────────────────────────────────────────────────────

class LinkIssue:
    """A single broken link or bare-path issue found during scan."""
    def __init__(self, filepath, line, link_text, link_path, resolved_path,
                 issue_type='BROKEN', message='', suggestion=''):
        self.filepath = filepath
        self.rel_path = str(filepath.relative_to(KNOWLEDGE_ROOT)) if KNOWLEDGE_ROOT in filepath.parents else str(filepath)
        self.line = line
        self.link_text = link_text       # display text of the link
        self.link_path = link_path       # the original path in the markdown
        self.resolved_path = str(resolved_path)  # what it resolved to (or tried to)
        self.issue_type = issue_type     # DEPTH/MOVED/DIR_RENAME/EXTERNAL/MISSING
        self.message = message
        self.suggestion = suggestion

    def to_dict(self):
        return {
            'file': self.rel_path,
            'line': self.line,
            'text': self.link_text,
            'link': self.link_path,
            'resolved': self.resolved_path,
            'type': self.issue_type,
            'message': self.message,
            'suggestion': self.suggestion,
        }

    def __repr__(self):
        return f"[{self.issue_type}] {self.rel_path}:L{self.line} `{self.link_path}` → {self.message}"


# ── Scan Functions ────────────────────────────────────────────────────────────

def is_external_url(link):
    """Check if link is an external URL."""
    return any(link.startswith(p) for p in ('http://', 'https://', 'ftp://', 'mailto:', 'data:'))


def should_skip_ext(ext):
    """Skip binary/image files."""
    return ext.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
                           '.pdf', '.pptx', '.docx', '.xlsx', '.woff', '.woff2',
                           '.ttf', '.eot', '.mp4', '.mp3', '.webm'} and ext != '.md'


def mask_inline_code(line):
    """把行内代码 `...` 内容替换为等长占位符，避免代码中的链接误报。

    2026-08-05: log.md 中 `[标题](标题)` 是描述 TOC 格式的示例文本（反引号内），
    会被误报为 MISSING。真实链接不受影响（位置保持）。
    """
    return re.sub(r'`[^`]*`', lambda m: '`' + 'x' * max(len(m.group(0)) - 2, 0) + '`', line)


def scan_markdown_links(filepath):
    """Scan a file for markdown links [text](path) and validate them."""
    issues = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return issues

    # Track code blocks (``` fenced) to skip links inside them
    lines_all = content.split('\n')
    in_code_block = False
    for i, line in enumerate(lines_all, 1):
        # Toggle code block state (``` or ~~~ fences)
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue  # Skip everything inside code blocks

        masked_line = mask_inline_code(line)
        for match in LINK_RE.finditer(masked_line):
            text, link = match.group(1), match.group(2)

            # Skip external URLs
            if is_external_url(link):
                continue
            if '://' in link:
                continue
            # Skip anchors
            if link.startswith('#'):
                continue
            # Skip absolute paths
            if link.startswith('/'):
                continue

            # Skip template variables / code-like links: {var}, {a.b}, ${x}
            if re.match(r'^\{[^}]*\}$', link) or '$' in link:
                continue
            # Skip C++/code signatures: contains '&', '(', '{', ';', '=', '<' etc.
            if re.search(r'[&;=<>{}\[\]]', link):
                continue
            # Skip arXiv/paper-style short refs: cs.OS, cs.DC, b8e924030045b536
            if re.match(r'^[a-z]{2}\.[A-Z]{2}$', link):
                continue
            if re.match(r'^[a-f0-9]{16,}$', link):
                continue
            # Skip bare words that are clearly not paths (no slash, no dot, not known file)
            if '/' not in link and '.' not in link and len(link) <= 20 and not re.search(r'[\u4e00-\u9fff]', link):
                continue

            # Remove anchor
            clean_link = link.split('#')[0]
            if not clean_link:
                continue

            # Check extension
            ext = Path(clean_link).suffix.lower()
            if ext and should_skip_ext(ext):
                continue

            # Resolve relative to file's directory
            resolved = (filepath.parent / clean_link).resolve()

            # Try common extensions if no extension
            if not resolved.suffix:
                for try_ext in ['.md', '.py', '.sh', '.json', '.yaml', '.yml', '.txt', '.csv']:
                    candidate = resolved.with_suffix(try_ext)
                    if candidate.exists():
                        resolved = candidate
                        break

            if not resolved.exists():
                # Classify the broken link
                issue = classify_broken_link(filepath, clean_link, resolved, text, i)
                issues.append(issue)
            elif filepath.name != 'log.md' and not link.startswith('../'):
                # Check if link uses short name but target is deep — warn for consistency
                # (Only flag non-cross-module cases)
                pass

    return issues


def scan_bare_paths(filepath):
    """Scan for bare knowledge/xxx.md text references that should be links."""
    issues = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return issues

    # Skip if not markdown
    if filepath.suffix != '.md':
        return issues

    for i, line in enumerate(content.split('\n'), 1):
        for match in BARE_PATH_RE.finditer(line):
            bare_path = match.group(1).strip().rstrip('.,;:!?')

            # Skip if it's already inside a markdown link — check context
            line_before = line[:match.start()]
            if line_before.rstrip().endswith(']('):
                continue  # Already inside a markdown link

            # Check if path looks like a knowledge path
            parts = bare_path.split('/')
            if len(parts) >= 2 and parts[0] in KNOWN_MODULES:
                # It's a knowledge/ reference in text → should be linked
                target = (KNOWLEDGE_ROOT / bare_path).resolve()
                if target.exists():
                    issues.append(LinkIssue(
                        filepath, i, bare_path, bare_path, target,
                        issue_type='EXTERNAL',
                        message=f"Bare knowledge path reference (should be markdown link): `{bare_path}`",
                        suggestion=f"Wrap as `[{bare_path}]({bare_path})`"
                    ))

    return issues


def classify_broken_link(filepath, link_path, resolved, text, line_num):
    """Determine why a link is broken and classify it."""
    link_name = Path(link_path).name
    link_parent = str(Path(link_path).parent)

    # ── Strategy 1: Check if target exists elsewhere in knowledge/ ──
    if link_name.endswith('.md'):
        found = list(KNOWLEDGE_ROOT.rglob(link_name))
        # Exclude matches in bak/
        found = [f for f in found if 'bak/' not in str(f)]
        if found:
            # Calculate correct relative path
            try:
                correct_rel = os.path.relpath(found[0], filepath.parent)
                return LinkIssue(
                    filepath, line_num, text, link_path, found[0],
                    issue_type='MOVED',
                    message=f"Target `{link_name}` exists at `{found[0].relative_to(KNOWLEDGE_ROOT)}`",
                    suggestion=f"Replace `{link_path}` → `{correct_rel}`"
                )
            except ValueError:
                pass

    # ── Strategy 2: Check if it's a depth issue ──
    # Count ../ depth in link
    link_depth = link_path.count('../')
    # Count ../ depth in file location from knowledge/
    if KNOWLEDGE_ROOT in filepath.parents:
        file_depth = len(filepath.relative_to(KNOWLEDGE_ROOT).parent.parts)
    else:
        file_depth = 0

    if link_depth > 0 and abs(file_depth - link_depth) > 1:
        # Try adjusting depth by 1
        for adjustment in [-1, 1]:
            if adjustment == -1 and link_depth > 0:
                adjusted = link_path.replace('../', '', 1)
            elif adjustment == 1:
                adjusted = '../' + link_path
            else:
                continue
            resolved_adj = (filepath.parent / adjusted).resolve()
            if resolved_adj.exists():
                return LinkIssue(
                    filepath, line_num, text, link_path, resolved_adj,
                    issue_type='DEPTH',
                    message=f"Depth mismatch: file is {file_depth} levels deep, link has {link_depth} `../`",
                    suggestion=f"Replace `{link_path}` → `{adjusted}`"
                )

    # ── Strategy 3: Try with/without arch/ prefix ──
    # Pattern: link is `xxx.md` but target is `arch/xxx.md` (file moved into subdir)
    arch_candidates = [
        f"arch/{link_path.lstrip('../')}",
        link_path.replace('arch/', '', 1) if 'arch/' in link_path else None
    ]
    for ac in arch_candidates:
        if ac:
            resolved_ac = (filepath.parent / ac).resolve()
            if resolved_ac.exists():
                return LinkIssue(
                    filepath, line_num, text, link_path, resolved_ac,
                    issue_type='DIR_RENAME',
                    message=f"Target exists with `arch/` prefix adjustment",
                    suggestion=f"Replace `{link_path}` → `{ac}`"
                )

    # ── Strategy 4: Directory rename patterns ──
    rename_rules = [
        ('03_hardware/', '02_firmware/'),
        ('02_rd-management/', '00_rd-management/'),
        ('02_server/', '07_industry-research/03_server/'),
        ('industry-research/', '07_industry-research/'),
    ]
    for old_dir, new_dir in rename_rules:
        if old_dir in link_path:
            adjusted = link_path.replace(old_dir, new_dir)
            resolved_ad = (filepath.parent / adjusted).resolve()
            if resolved_ad.exists():
                return LinkIssue(
                    filepath, line_num, text, link_path, resolved_ad,
                    issue_type='DIR_RENAME',
                    message=f"Directory renamed: `{old_dir}` → `{new_dir}`",
                    suggestion=f"Replace `{link_path}` → `{adjusted}`"
                )

    # ── Strategy 5: Check if target is in a known module at different depth ──
    # For cross-module links: ../../01_survey/... vs ../../../01_survey/...
    for module in KNOWN_MODULES:
        if module in link_path:
            # Try adding or removing one ../ from before the module reference
            idx = link_path.index(module)
            prefix = link_path[:idx]
            if prefix.count('../') > 0:
                # Try with one less ../
                shorter = prefix.replace('../', '', 1) + link_path[idx:]
                resolved_sh = (filepath.parent / shorter).resolve()
                if resolved_sh.exists():
                    return LinkIssue(
                        filepath, line_num, text, link_path, resolved_sh,
                        issue_type='DEPTH',
                        message=f"Cross-module depth wrong for `{module}`",
                        suggestion=f"Replace `{link_path}` → `{shorter}`"
                    )
                # Try with one more ../
                longer = '../' + link_path
                resolved_lo = (filepath.parent / longer).resolve()
                if resolved_lo.exists():
                    return LinkIssue(
                        filepath, line_num, text, link_path, resolved_lo,
                        issue_type='DEPTH',
                        message=f"Cross-module depth wrong for `{module}`",
                        suggestion=f"Replace `{link_path}` → `{longer}`"
                    )

    # ── Strategy 6: Try with/without knowledge/ prefix ──
    if link_path.startswith('../knowledge/'):
        adjusted = link_path.replace('../knowledge/', '', 1)
        resolved_no_kb = (filepath.parent / adjusted).resolve()
        if resolved_no_kb.exists():
            return LinkIssue(
                filepath, line_num, text, link_path, resolved_no_kb,
                issue_type='DEPTH',
                message="Redundant 'knowledge/' prefix in relative link",
                suggestion=f"Replace `{link_path}` → `{adjusted}`"
            )

    # ── All strategies exhausted → truly missing ──
    return LinkIssue(
        filepath, line_num, text, link_path, resolved,
        issue_type='MISSING',
        message=f"File not found at resolved path: {resolved}",
        suggestion="File may not exist in knowledge base; create stub or remove reference"
    )


# ── Scanning Engine ───────────────────────────────────────────────────────────

def scan_truncated(filepath):
    """检测链接修复残留/截断残缺。

    特征: `.md)` 前最近的 `(` 不构成 `](` 结构（无配对开括号）。
    根因: 链接正则 `[^)]+` 遇 URL 内含括号（如 `英伟达(NVIDIA).md`）时截断，
          修复/降级后残留 `xxx.md)` 残缺文本（2026-08-05 案例:
          2026-06-23-product-design-guide.md:1214）。
    """
    issues = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return issues
    if filepath.suffix != '.md':
        return issues

    in_code_block = False
    for i, line in enumerate(content.split('\n'), 1):
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        masked_line = mask_inline_code(line)
        for m in TRUNCATED_RE.finditer(masked_line):
            pre = masked_line[:m.start()]
            # 真残缺判定: `.md)` 前完全无 `(` 才是截断残留
            # - `](path.md)` 前有 ]( → 正常链接
            # - `(SKILL.md)` / `(index.md)` 前有其他 ( → 正文文件名说明, 正常
            # - `xxx战略演进.md)` 前无任何 ( → 正则截断残留（2026-08-05 BUG 特征）
            if pre.rfind('(') >= 0:
                continue
            issues.append(LinkIssue(
                filepath, i, '', m.group(0), '',
                issue_type='TRUNCATED',
                message=f"残缺链接残留: `{m.group(0)}` 前无 `(`（疑似链接正则截断产物）",
                suggestion="降级为纯文本或修复为完整链接"
            ))
    return issues


def scan_file(filepath, detect_external=True):
    """Run all scans on a single file. Returns list of LinkIssue objects."""
    issues = []
    issues.extend(scan_markdown_links(filepath))
    issues.extend(scan_truncated(filepath))
    if detect_external:
        issues.extend(scan_bare_paths(filepath))
    return issues


def collect_files(scan_path, skip_dirs=None):
    """Collect markdown files to scan."""
    if skip_dirs is None:
        skip_dirs = SKIP_DIRS

    files = []
    if scan_path.is_file():
        return [scan_path]
    for p in scan_path.rglob('*.md'):
        if any(part in skip_dirs for part in p.parts):
            continue
        files.append(p)
    return sorted(files, key=lambda x: str(x))


# ── Reports ───────────────────────────────────────────────────────────────────

def generate_report(issues, args):
    """Generate a structured report."""
    lines = []
    separator = "=" * 72
    lines.append(separator)
    lines.append(f"  🔗 Knowledge Link Validation Report")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Scope: {args.scope}")
    lines.append(separator)
    lines.append("")

    # Categorize
    by_type = defaultdict(list)
    for issue in issues:
        by_type[issue.issue_type].append(issue)

    # Summary
    lines.append(f"  📊 Summary:")
    lines.append(f"  {'Type':<15} {'Count':>6}")
    lines.append(f"  {'─'*15} {'─'*6}")
    type_labels = {
        'DEPTH': '🔄 Depth Wrong',
        'MOVED': '📦 File Moved',
        'DIR_RENAME': '📁 Dir Renamed',
        'EXTERNAL': '📝 Bare Path Ref',
        'MISSING': '❌ Truly Missing',
        'TRUNCATED': '✂️ Truncated Residue',
    }
    total = 0
    for t in ['DEPTH', 'MOVED', 'DIR_RENAME', 'EXTERNAL', 'MISSING', 'TRUNCATED']:
        count = len(by_type.get(t, []))
        label = type_labels.get(t, t)
        lines.append(f"  {label:<15} {count:>6}")
        total += count
    lines.append(f"  {'─'*15} {'─'*6}")
    lines.append(f"  {'TOTAL':<15} {total:>6}")
    lines.append("")

    # Files affected
    affected_files = sorted(set(i.rel_path for i in issues))
    lines.append(f"  📁 Files affected: {len(affected_files)}")
    lines.append("")

    # Group by file
    if args.verbose or args.report:
        by_file = defaultdict(list)
        for issue in issues:
            by_file[issue.rel_path].append(issue)

        for fname in sorted(by_file.keys()):
            file_issues = by_file[fname]
            type_counts = defaultdict(int)
            for i in file_issues:
                type_counts[i.issue_type] += 1
            type_summary = ' '.join(f"{t}={c}" for t, c in sorted(type_counts.items()))
            lines.append(f"  📄 {fname}  ({type_summary})")

            for issue in file_issues:
                type_icon = {'DEPTH': '🔄', 'MOVED': '📦', 'DIR_RENAME': '📁',
                            'EXTERNAL': '📝', 'MISSING': '❌', 'TRUNCATED': '✂️'}.get(issue.issue_type, '⚠️')
                lines.append(f"    L{issue.line:>4}  {type_icon} `{issue.link_path}`")
                lines.append(f"          {issue.message}")
                if args.suggest and issue.suggestion:
                    lines.append(f"          💡 {issue.suggestion}")
            lines.append("")

    # Special: list MISSING files separately for easy review
    missing = by_type.get('MISSING', [])
    if missing:
        lines.append(f"  {'─'*72}")
        lines.append(f"  ❌ TRULY MISSING FILES ({len(missing)}):")
        lines.append(f"  {'─'*72}")
        for issue in missing:
            lines.append(f"    {issue.rel_path}:L{issue.line} → `{issue.link_path}`")
        lines.append("")

    lines.append(separator)
    return '\n'.join(lines)


def generate_json(issues):
    """Generate JSON output."""
    return json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total_issues": len(issues),
        "affected_files": len(set(i.rel_path for i in issues)),
        "by_type": dict(
            (t, len([i for i in issues if i.issue_type == t]))
            for t in ['DEPTH', 'MOVED', 'DIR_RENAME', 'EXTERNAL', 'MISSING', 'TRUNCATED']
        ),
        "issues": [i.to_dict() for i in issues],
    }, indent=2, ensure_ascii=False)


# ── Fix Functions ─────────────────────────────────────────────────────────────

def auto_fix(issues, dry_run=False):
    """Apply auto-fix suggestions to files."""
    fixed_count = 0
    fixable_count = 0
    files_modified = set()

    # Group issues by file
    by_file = defaultdict(list)
    for issue in issues:
        if issue.suggestion and 'Replace' in issue.suggestion:
            by_file[issue.rel_path].append(issue)
            fixable_count += 1

    for fname, file_issues in sorted(by_file.items()):
        filepath = KNOWLEDGE_ROOT / fname
        if not filepath.exists():
            # Maybe it's outside knowledge/
            continue

        original = filepath.read_text(encoding='utf-8')
        content = original
        modified = False

        for issue in file_issues:
            # Extract the fix suggestion
            if 'Replace' in issue.suggestion:
                # Pattern: "Replace `old` → `new`"
                m = re.search(r'`([^`]+)`\s*→\s*`([^`]+)`', issue.suggestion)
                if m:
                    old_link = m.group(1)
                    new_link = m.group(2)
                    old_pattern = f'({old_link})'
                    new_pattern = f'({new_link})'

                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern, 1)
                        if not dry_run:
                            pass  # mark for write
                        modified = True
                        fixed_count += 1
                    else:
                        # Try exact match on the link path
                        if old_link in content:
                            content = content.replace(old_link, new_link, 1)
                            modified = True
                            fixed_count += 1

        if modified and not dry_run:
            filepath.write_text(content, encoding='utf-8')
            files_modified.add(fname)
            print(f"  ✅ Fixed: {fname}")

    return fixed_count, len(files_modified)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='🔗 Knowledge Base Link Validator & Fixer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/check/link-validator.py                           # Full scan
  python3 scripts/check/link-validator.py --module 06_superpod      # Per-module
  python3 scripts/check/link-validator.py --file index.md           # Single file
  python3 scripts/check/link-validator.py --report --suggest        # With fix suggestions
  python3 scripts/check/link-validator.py --json                    # Machine output
  python3 scripts/check/link-validator.py --fix                     # Auto-fix where possible
  python3 scripts/check/link-validator.py --fix --dry-run           # Preview fixes
        """
    )
    parser.add_argument('--module', '-m', help='Scan a specific module directory (e.g. 06_superpod)')
    parser.add_argument('--file', '-f', help='Scan a specific file (relative to knowledge/)')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    parser.add_argument('--suggest', '-s', action='store_true', help='Show fix suggestions')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show details per file')
    parser.add_argument('--fix', action='store_true', help='Auto-fix broken links')
    parser.add_argument('--dry-run', action='store_true', help='Preview fixes without applying')
    parser.add_argument('--no-external', action='store_true', help='Skip bare path detection')
    args = parser.parse_args()

    # Determine scan scope
    if args.module:
        scan_path = (KNOWLEDGE_ROOT / args.module).resolve()
        if not scan_path.exists():
            print(f"❌ Module not found: {scan_path}")
            return 1
        args.scope = f"knowledge/{args.module}/"
    elif args.file:
        # Normalize: strip leading knowledge/ prefix or absolute path to avoid
        # double-prefix (KNOWLEDGE_ROOT / 'knowledge/xxx' → knowledge/knowledge/xxx)
        file_arg = args.file
        if file_arg.startswith(str(KNOWLEDGE_ROOT)):
            file_arg = file_arg[len(str(KNOWLEDGE_ROOT)):].lstrip('/')
        elif file_arg.startswith('knowledge/'):
            file_arg = file_arg[len('knowledge/'):]
        scan_path = (KNOWLEDGE_ROOT / file_arg).resolve()
        if not scan_path.exists():
            print(f"❌ File not found: {scan_path}")
            return 1
        args.scope = f"knowledge/{file_arg}"
    else:
        scan_path = KNOWLEDGE_ROOT
        args.scope = "knowledge/ (full)"

    # Collect files
    files = collect_files(scan_path)

    if not args.json:
        print(f"🔍 Scanning {len(files)} files in {args.scope}...")
        print()

    # Scan all files
    all_issues = []
    for f in files:
        issues = scan_file(f, detect_external=not args.no_external)
        all_issues.extend(issues)

    # Output
    if args.json:
        # JSON mode: only output JSON to stdout (no banner)
        print(generate_json(all_issues))
    elif args.fix:
        if not args.json:
            if args.dry_run:
                print(f"🔧 DRY RUN — Previewing fixes for {len([i for i in all_issues if i.suggestion and 'Replace' in i.suggestion])} fixable issues...")
                print()
            else:
                print(f"🔧 Attempting auto-fix...")
        fixed, files_affected = auto_fix(all_issues, dry_run=args.dry_run)
        print()
        print(f"   {'Would fix' if args.dry_run else 'Fixed'} {fixed} links in {files_affected} files")
        if not args.dry_run:
            # Re-scan
            print(f"\n🔍 Re-scanning to verify...")
            remaining = []
            for f in files:
                remaining.extend(scan_file(f, detect_external=not args.no_external))
            if remaining:
                print(f"   ⚠️  {len(remaining)} issues remain (re-run with --report to see details)")
            else:
                print(f"   ✅ All fixed!")
    else:
        print(generate_report(all_issues, args))

    # Return exit code
    return 0 if len(all_issues) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
