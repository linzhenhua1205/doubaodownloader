#!/usr/bin/env python3
"""
content-format-normalizer.py — 知识内容文件格式检查/修复工具

基于 spec/KNOWLEDGE_CONTENT_FORMAT.md 规范，检查/修复知识库内容文件的五大要素：
  - 概要 (H2): > **概要**:
  - 关键词 (H3): > **关键词**:
  - 目录 (T1): ## 📑 目录
  - 参考文件 (R1/R2/R3): ## 参考文件 + ### 内部知识库引用 + ### 外部资料引用
  - Changelog (C1/C2): ## Changelog + 三列表格

Modes:
  --check    Report violations, exit code 1 if any found
  --fix      Rewrite files to conform (migrate existing info + add scaffolding)
  --dry-run  Preview what --fix would change (no writes)
  --all      Process all content files under knowledge/ (except excluded)
  --module   Process a specific module directory

Usage:
    python scripts/check/content-format-normalizer.py knowledge/02_rd --check
    python scripts/check/content-format-normalizer.py knowledge/ --all --check
    python scripts/check/content-format-normalizer.py knowledge/ --all --dry-run
    python scripts/check/content-format-normalizer.py knowledge/ --all --fix
    python scripts/check/content-format-normalizer.py <file.md> --check
    python scripts/check/content-format-normalizer.py <file.md> --fix
"""
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime

# Ensure workspace root is on Python path (sr-008)
_SCRIPT_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import WORKSPACE_ROOT as REPO_ROOT, KNOWLEDGE_ROOT, SCRIPTS_DIR

SCRIPT_DIR = SCRIPTS_DIR / "check"

# === Constants ===
EXCLUDED_DIRNAMES = {'bak', 'oldbak', 'import-modules', '.git', '__pycache__', 'node_modules', '.bak'}
EXCLUDED_TOPDIRS = {'01_survey'}  # entire top-level dirs excluded
INDEX_NAMES = {'index.md', 'log.md', 'README.md', 'TRACKING.md'}

# === Regex patterns for extraction ===
RE_TITLE = re.compile(r'^# (.+?)\s*$', re.MULTILINE)
RE_SUMMARY = re.compile(r'^>\s*\*\*概要\*\*:\s*(.+?)\s*$', re.MULTILINE)
RE_KEYWORDS = re.compile(r'^>\s*\*\*关键词\*\*:\s*(.+?)\s*$', re.MULTILINE)

# Legacy summary patterns to migrate
RE_LEGACY_SUMMARY = [
    re.compile(r'^>\s*\*\*定位\*\*:\s*(.+?)\s*$', re.MULTILINE),
    re.compile(r'^>\s*📄\s*核心探索[：:]\s*(.+?)\s*$', re.MULTILINE),
    re.compile(r'^>\s*\*\*专题\*\*:\s*(.+?)\s*$', re.MULTILINE),
    re.compile(r'^>\s*Source:\s*(.+?)\s*$', re.MULTILINE),
    re.compile(r'^>\s*\*\*核心探索\*\*[：:]\s*(.+?)\s*$', re.MULTILINE),
]

# Legacy keywords
RE_LEGACY_KEYWORDS = re.compile(r'^>\s*\*\*关键词\*\*[：:]\s*(.+?)\s*$', re.MULTILINE)

# Section headers (normalized + legacy variants)
SECTION_TOC = r'^## 📑 目录\s*$'
SECTION_TOC_LEGACY = [r'^## 目录\s*$', r'^## TOC\s*$', r'^## 📑目录\s*$']
SECTION_REFS = r'^## 参考文件\s*$'
SECTION_REFS_LEGACY = [r'^## 参考来源\s*$', r'^## References\s*$', r'^## 参考\s*$', r'^## 相关文件\s*$',
                        r'^## 相关文档\s*$', r'^## 关联文档\s*$']
SECTION_CHANGELOG = r'^## Changelog\s*$'
SECTION_CHANGELOG_LEGACY = [r'^## 修订记录\s*$', r'^## 变更日志\s*$', r'^## 修改记录\s*$', r'^## CHANGELOG\s*$',
                             r'^## 更新历史\s*$']

SUBSECTION_INTERNAL = r'^### 内部知识库引用\s*$'
SUBSECTION_EXTERNAL = r'^### 外部资料引用\s*$'

# Header blockquote legacy patterns for references
RE_HEADER_REFS = re.compile(r'^>\s*\*\*(?:关联文档|前置阅读|相关文档|参考文档)\*\*[：:]\s*$', re.MULTILINE)
RE_HEADER_SOURCES = re.compile(r'^>\s*\*\*(?:素材来源|数据来源|来源)\*\*[：:]\s*(.*)$', re.MULTILINE)
RE_HEADER_SOURCE_LINE = re.compile(r'^>\s*Source:\s*(.+?)\s*$', re.MULTILINE)

# Inline link reference: > 🔗 [xxx](xxx) or > - [xxx](xxx)
RE_INLINE_LINK = re.compile(r'^>\s*🔗?\s*-?\s*\[([^\]]+)\]\(([^)]+)\)\s*[—-]?\s*(.*)$')
# Markdown link in general
RE_MD_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Changelog table row (flexible: date | any | any, supports 2-4 column formats)
RE_CHANGELOG_ROW = re.compile(r'^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*(?:\|[^|]*)?\|\s*$')

# Header changelog (blockquote table)
RE_HEADER_CHANGELOG = re.compile(r'^>\s*\*\*CHANGELOG\*\*[：:]\s*$', re.MULTILINE)


def is_excluded(rel_path: str) -> bool:
    """Check if a relative path should be excluded."""
    parts = rel_path.replace('\\', '/').split('/')
    # Remove 'knowledge' prefix if present (rel_path may be from repo root)
    if parts and parts[0] == 'knowledge':
        parts = parts[1:]
    for excl in EXCLUDED_TOPDIRS:
        if parts and parts[0] == excl:
            return True
    for part in parts:
        if part in EXCLUDED_DIRNAMES:
            return True
    return False


def collect_files(target: Path) -> list:
    """Collect all content .md files under target (excluding index/log/README/excluded)."""
    files = []
    if target.is_file() and target.suffix == '.md':
        if target.name not in INDEX_NAMES:
            rel = str(target.relative_to(REPO_ROOT))
            if not is_excluded(rel):
                files.append(target)
    elif target.is_dir():
        for p in sorted(target.rglob('*.md')):
            if p.name in INDEX_NAMES:
                continue
            rel = str(p.relative_to(REPO_ROOT))
            if is_excluded(rel):
                continue
            files.append(p)
    return files


# === Parsing ===

def find_section_range(lines: list, header_patterns: list, start_idx: int = 0) -> tuple:
    """Find a section's (start, end) line indices. end is exclusive (next ## or EOF)."""
    for i in range(start_idx, len(lines)):
        for pat in header_patterns:
            if re.match(pat, lines[i]):
                # Found section start; find end (next ## at same or higher level, or ---, or EOF)
                start = i
                end = len(lines)
                for j in range(i + 1, len(lines)):
                    line = lines[j]
                    # End at next ## heading (not ###) or horizontal rule
                    if re.match(r'^##\s', line) and not re.match(r'^###\s', line):
                        end = j
                        break
                return (start, end)
    return (-1, -1)


def parse_header_blockquote(lines: list, title_idx: int) -> tuple:
    """Parse the blockquote block after the title. Returns (blockquote_lines, end_idx)."""
    bq_lines = []
    i = title_idx + 1
    # Skip blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    # Collect blockquote lines
    while i < len(lines) and lines[i].strip().startswith('>'):
        bq_lines.append(lines[i])
        i += 1
    return (bq_lines, i)


def extract_summary_from_blockquote(bq_lines: list) -> str:
    """Extract summary text from blockquote, checking unified then legacy patterns."""
    text = '\n'.join(bq_lines)
    # Unified
    m = RE_SUMMARY.search(text)
    if m:
        return m.group(1).strip()
    # Legacy
    for pat in RE_LEGACY_SUMMARY:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return ''


def extract_keywords_from_blockquote(bq_lines: list) -> str:
    """Extract keywords string from blockquote."""
    text = '\n'.join(bq_lines)
    m = RE_KEYWORDS.search(text)
    if m:
        return m.group(1).strip()
    m = RE_LEGACY_KEYWORDS.search(text)
    if m:
        return m.group(1).strip()
    return ''


def extract_internal_refs_from_blockquote(bq_lines: list) -> list:
    """Extract internal knowledge references from header blockquote (关联文档/前置阅读 sections)."""
    refs = []
    in_refs_section = False
    for line in bq_lines:
        stripped = line.strip()
        # Detect start of refs section
        if RE_HEADER_REFS.search(line) or re.match(r'^>\s*\*\*(?:前置阅读|相关文档|参考文档)\*\*[：:]\s*$', stripped):
            in_refs_section = True
            continue
        # Detect end of refs section (next > **xxx**: header)
        if in_refs_section and re.match(r'^>\s*\*\*[^*]+\*\*[：:]', stripped) and not stripped.startswith('> -'):
            in_refs_section = False
            continue
        # Extract links
        if in_refs_section or stripped.startswith('> 🔗') or stripped.startswith('> - 🔗'):
            m = RE_INLINE_LINK.match(line)
            if m:
                label, path, relation = m.group(1), m.group(2), m.group(3).strip()
                # Only internal links (relative paths, not http)
                if not path.startswith('http') and not path.startswith('#'):
                    refs.append({'label': label, 'path': path, 'relation': relation or '关联'})
            else:
                # Try plain link in blockquote
                for lm in RE_MD_LINK.finditer(line):
                    label, path = lm.group(1), lm.group(2)
                    if not path.startswith('http') and not path.startswith('#'):
                        refs.append({'label': label, 'path': path, 'relation': '关联'})
    return refs


def extract_external_refs_from_blockquote(bq_lines: list) -> list:
    """Extract external references from header blockquote (素材来源/Source)."""
    refs = []
    text = '\n'.join(bq_lines)
    # 素材来源: xxx · yyy
    m = RE_HEADER_SOURCES.search(text)
    if m and m.group(1).strip():
        parts = re.split(r'[·,，;；]', m.group(1))
        for part in parts:
            part = part.strip().strip('`')
            if part and len(part) > 2:
                refs.append({'source': part, 'type': 'doc'})
    # Source: xxx
    for m in RE_HEADER_SOURCE_LINE.finditer(text):
        val = m.group(1).strip()
        if val:
            refs.append({'source': val, 'type': 'url'})
    return refs


def extract_changelog_from_blockquote(bq_lines: list) -> list:
    """Extract changelog entries from header blockquote (> **CHANGELOG**: table)."""
    entries = []
    in_changelog = False
    for line in bq_lines:
        if RE_HEADER_CHANGELOG.search(line):
            in_changelog = True
            continue
        if in_changelog:
            stripped = line.strip()
            # Table row in blockquote: > | date | col2 | col3 | (flexible)
            m = re.match(r'^>\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*(?:\|[^|]*)?\|\s*$', stripped)
            if m:
                date = m.group(1)
                col2 = m.group(2).strip()
                col3 = m.group(3).strip()
                if re.match(r'^v[\d.]+', col2):
                    version, change = col2, col3
                else:
                    version = 'v1.0'
                    change = col2 + (f' ({col3})' if col3 and col3 != '小龙猫' else '')
                entries.append({'date': date, 'version': version, 'change': change})
            elif stripped.startswith('> **') and not stripped.startswith('> |'):
                # Next header field
                in_changelog = False
    return entries


def extract_changelog_from_section(lines: list, start: int, end: int) -> list:
    """Extract changelog entries from a ## Changelog section. Handles flexible column formats."""
    entries = []
    for i in range(start, end):
        m = RE_CHANGELOG_ROW.match(lines[i])
        if m:
            date = m.group(1)
            col2 = m.group(2).strip()
            col3 = m.group(3).strip()
            # Determine version vs change: if col2 looks like vX.Y, it's version
            if re.match(r'^v[\d.]+', col2):
                version = col2
                change = col3
            else:
                # col2 is the change description, no explicit version
                version = 'v1.0'
                change = f'{col2}' + (f' ({col3})' if col3 and col3 != '小龙猫' and not col3.startswith('作者') else '')
            entries.append({'date': date, 'version': version, 'change': change})
    return entries


def extract_refs_from_section(lines: list, start: int, end: int) -> tuple:
    """Extract internal and external refs from a references section. Returns (internal, external)."""
    internal = []
    external = []
    current_sub = None
    in_table = False
    table_header_seen = False
    for i in range(start + 1, end):
        line = lines[i]
        stripped = line.strip()
        if re.match(SUBSECTION_INTERNAL, stripped):
            current_sub = 'internal'
            in_table = False
            continue
        if re.match(SUBSECTION_EXTERNAL, stripped):
            current_sub = 'external'
            in_table = False
            continue
        if stripped.startswith('### '):
            current_sub = None
            in_table = False
            continue
        if not stripped:
            continue
        if stripped.startswith('>'):
            continue
        # Table row: | col1 | col2 | col3 | ...
        if stripped.startswith('|'):
            # Skip separator rows
            if re.match(r'^\|[\s:|-]+\|\s*$', stripped):
                continue
            cols = [c.strip() for c in stripped.strip('|').split('|')]
            # Skip header rows (contain 来源/类型/层级/文件/标题 etc.)
            if not table_header_seen and any(h in cols for h in ['来源', '类型', '层级', '文件', '标题', '#']):
                table_header_seen = True
                in_table = True
                continue
            if in_table and cols:
                # Extract source from the most descriptive column (usually col[1] or col[0])
                source_text = ''
                for col in cols[1:] if len(cols) > 1 else cols:
                    if col and not re.match(r'^[\d#🥇🥈🥉📄]+$', col) and len(col) > 3:
                        source_text = col
                        break
                if not source_text and cols[0]:
                    source_text = cols[0]
                if source_text and source_text != '(无)':
                    external.append({'source': source_text, 'type': 'doc'})
            continue
        # Internal link: - [label](path) — relation
        m = re.match(r'^-\s*\[([^\]]+)\]\(([^)]+)\)\s*[—-]?\s*(.*)$', stripped)
        if m:
            label, path, relation = m.group(1), m.group(2), m.group(3).strip()
            if path.startswith('http'):
                external.append({'source': f"[{label}]({path}) — {relation}".strip(' —'), 'type': 'url'})
            else:
                internal.append({'label': label, 'path': path, 'relation': relation or '关联'})
            continue
        # External: - 来源: xxx or - xxx
        m = re.match(r'^-\s*(?:来源\d*[:：]\s*)?(.+)$', stripped)
        if m and m.group(1).strip() != '(无)':
            val = m.group(1).strip()
            if val:
                external.append({'source': val, 'type': 'doc'})
    return (internal, external)


def collect_body_links(lines: list, body_start: int, body_end: int) -> list:
    """Collect markdown links to .md files from body content (for internal refs)."""
    refs = []
    seen_paths = set()
    for i in range(body_start, body_end):
        for m in RE_MD_LINK.finditer(lines[i]):
            label, path = m.group(1), m.group(2)
            if path.endswith('.md') and not path.startswith('http') and not path.startswith('#'):
                if path not in seen_paths:
                    seen_paths.add(path)
                    refs.append({'label': label, 'path': path, 'relation': '关联'})
    return refs


def generate_toc(lines: list, body_start: int, body_end: int) -> list:
    """Generate TOC entries from ## and ### headings in body."""
    entries = []
    for i in range(body_start, body_end):
        line = lines[i]
        m2 = re.match(r'^(##+)\s+(.+?)\s*$', line)
        if m2:
            level = len(m2.group(1))
            title = m2.group(2).strip()
            # Skip TOC itself, 参考文件, Changelog (added separately)
            if re.match(SECTION_TOC, line) or re.match(SECTION_REFS, line) or re.match(SECTION_CHANGELOG, line):
                continue
            if any(re.match(p, line) for p in SECTION_TOC_LEGACY + SECTION_REFS_LEGACY + SECTION_CHANGELOG_LEGACY):
                continue
            # Generate anchor
            anchor = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', title.lower())
            anchor = re.sub(r'\s+', '-', anchor.strip())
            entries.append({'level': level, 'title': title, 'anchor': anchor})
    return entries


def parse_file(content: str) -> dict:
    """Parse a markdown file into structured components."""
    lines = content.split('\n')

    # Find title
    title_idx = -1
    title = ''
    for i, line in enumerate(lines):
        if re.match(r'^# ', line) and not re.match(r'^## ', line):
            title = line[2:].strip()
            title_idx = i
            break

    # Parse header blockquote
    bq_lines = []
    bq_end = title_idx + 1 if title_idx >= 0 else 0
    if title_idx >= 0:
        bq_lines, bq_end = parse_header_blockquote(lines, title_idx)

    # Find sections
    toc_start, toc_end = find_section_range(lines, [SECTION_TOC] + SECTION_TOC_LEGACY, bq_end)
    refs_start, refs_end = find_section_range(lines, [SECTION_REFS] + SECTION_REFS_LEGACY, bq_end)
    changelog_start, changelog_end = find_section_range(lines, [SECTION_CHANGELOG] + SECTION_CHANGELOG_LEGACY, bq_end)

    # Body is between (blockquote end OR TOC end) and the first of (refs/changelog) that comes after
    # body_start: after blockquote, after TOC if TOC exists
    body_start = bq_end
    if toc_start >= 0:
        body_start = toc_end

    # body_end: start of refs or changelog (whichever comes first AND is after body_start), or EOF
    body_end_candidates = [s for s in [refs_start, changelog_start] if s >= 0 and s > body_start]
    body_end = min(body_end_candidates) if body_end_candidates else len(lines)

    return {
        'lines': lines,
        'title': title,
        'title_idx': title_idx,
        'bq_lines': bq_lines,
        'bq_end': bq_end,
        'toc_start': toc_start,
        'toc_end': toc_end,
        'refs_start': refs_start,
        'refs_end': refs_end,
        'changelog_start': changelog_start,
        'changelog_end': changelog_end,
        'body_start': body_start,
        'body_end': body_end,
    }


# === Checking ===

def check_file(parsed: dict) -> list:
    """Check parsed file for compliance. Returns list of (check_id, status, message)."""
    issues = []
    lines = parsed['lines']

    # H1: title exists
    if not parsed['title']:
        issues.append(('H1', 'FAIL', '缺少 H1 标题（# 标题）'))

    # H2: summary
    summary = extract_summary_from_blockquote(parsed['bq_lines'])
    if not summary:
        issues.append(('H2', 'FAIL', '缺少 > **概要**: 标记'))
    elif summary == '(待补充)':
        issues.append(('H2', 'WARN', '概要为占位符 (待补充)'))

    # H3: keywords
    keywords = extract_keywords_from_blockquote(parsed['bq_lines'])
    if not keywords:
        issues.append(('H3', 'FAIL', '缺少 > **关键词**: 标记'))
    elif keywords == '(待补充)':
        issues.append(('H3', 'WARN', '关键词为占位符 (待补充)'))

    # T1: TOC
    if parsed['toc_start'] < 0:
        issues.append(('T1', 'FAIL', '缺少 ## 📑 目录 章节'))
    else:
        # Check title is normalized
        if not re.match(SECTION_TOC, lines[parsed['toc_start']]):
            issues.append(('T1', 'WARN', f'目录标题非标准格式: {lines[parsed["toc_start"]].strip()}'))

    # R1: references section
    if parsed['refs_start'] < 0:
        issues.append(('R1', 'FAIL', '缺少 ## 参考文件 章节'))
    else:
        if not re.match(SECTION_REFS, lines[parsed['refs_start']]):
            issues.append(('R1', 'WARN', f'参考文件标题非标准格式: {lines[parsed["refs_start"]].strip()}'))

    # R2: internal refs subsection
    has_internal = False
    if parsed['refs_start'] >= 0:
        for i in range(parsed['refs_start'], parsed['refs_end']):
            if re.match(SUBSECTION_INTERNAL, lines[i]):
                has_internal = True
                break
    if not has_internal:
        issues.append(('R2', 'FAIL', '缺少 ### 内部知识库引用 子节'))

    # R3: external refs subsection
    has_external = False
    if parsed['refs_start'] >= 0:
        for i in range(parsed['refs_start'], parsed['refs_end']):
            if re.match(SUBSECTION_EXTERNAL, lines[i]):
                has_external = True
                break
    if not has_external:
        issues.append(('R3', 'FAIL', '缺少 ### 外部资料引用 子节'))

    # C1: changelog
    if parsed['changelog_start'] < 0:
        issues.append(('C1', 'FAIL', '缺少 ## Changelog 章节'))
    else:
        if not re.match(SECTION_CHANGELOG, lines[parsed['changelog_start']]):
            issues.append(('C1', 'WARN', f'Changelog标题非标准格式: {lines[parsed["changelog_start"]].strip()}'))

    # C2: changelog table format
    if parsed['changelog_start'] >= 0:
        entries = extract_changelog_from_section(lines, parsed['changelog_start'], parsed['changelog_end'])
        if not entries:
            # Check if there's a blockquote changelog
            bq_entries = extract_changelog_from_blockquote(parsed['bq_lines'])
            if not bq_entries:
                issues.append(('C2', 'FAIL', 'Changelog 无有效表格行'))

    return issues


# === Fixing ===

def fix_file(parsed: dict, filepath: Path) -> str:
    """Fix a parsed file. Returns new content string."""
    lines = parsed['lines']
    today = datetime.now().strftime('%Y-%m-%d')

    # === 1. Extract/migrate existing info ===
    title = parsed['title'] or filepath.stem.replace('-', ' ').replace('_', ' ')
    summary = extract_summary_from_blockquote(parsed['bq_lines'])
    keywords = extract_keywords_from_blockquote(parsed['bq_lines'])

    # Normalize keywords separator to ' · '
    if keywords and keywords != '(待补充)':
        parts = re.split(r'\s*[·,，;；|/]\s*', keywords)
        parts = [p.strip() for p in parts if p.strip()]
        keywords = ' · '.join(parts) if parts else '(待补充)'

    # Extract references
    internal_refs = extract_internal_refs_from_blockquote(parsed['bq_lines'])
    external_refs = extract_external_refs_from_blockquote(parsed['bq_lines'])

    # Extract from existing refs section
    if parsed['refs_start'] >= 0:
        sec_internal, sec_external = extract_refs_from_section(lines, parsed['refs_start'], parsed['refs_end'])
        # Merge (dedupe by path)
        seen_paths = {r['path'] for r in internal_refs}
        for r in sec_internal:
            if r['path'] not in seen_paths:
                internal_refs.append(r)
                seen_paths.add(r['path'])
        seen_sources = {r['source'] for r in external_refs}
        for r in sec_external:
            if r['source'] not in seen_sources:
                external_refs.append(r)
                seen_sources.add(r['source'])

    # Extract changelog
    changelog_entries = extract_changelog_from_blockquote(parsed['bq_lines'])
    if parsed['changelog_start'] >= 0:
        sec_entries = extract_changelog_from_section(lines, parsed['changelog_start'], parsed['changelog_end'])
        seen_dates = {e['date'] for e in changelog_entries}
        for e in sec_entries:
            if e['date'] not in seen_dates:
                changelog_entries.append(e)
                seen_dates.add(e['date'])

    # Collect body links as additional internal refs (only if no refs yet)
    if not internal_refs:
        body_links = collect_body_links(lines, parsed['body_start'], parsed['body_end'])
        internal_refs = body_links[:10]  # limit to 10

    # === 2. Build new content ===

    # 2a. Title
    new_lines = [f'# {title}', '']

    # 2b. Header blockquote (概要 + 关键词 only)
    new_lines.append(f'> **概要**: {summary or "(待补充)"}')
    new_lines.append('>')
    new_lines.append(f'> **关键词**: {keywords or "(待补充)"}')
    new_lines.append('')

    # 2c. Separator
    new_lines.append('---')
    new_lines.append('')

    # 2d. TOC
    new_lines.append('## 📑 目录')
    new_lines.append('')
    toc_entries = generate_toc(lines, parsed['body_start'], parsed['body_end'])
    for entry in toc_entries:
        indent = '  ' * (entry['level'] - 2)
        new_lines.append(f'{indent}- [{entry["title"]}]({entry["anchor"]})')
    new_lines.append('- [参考文件](#参考文件)')
    new_lines.append('- [Changelog](#changelog)')
    new_lines.append('')

    # 2e. Separator
    new_lines.append('---')
    new_lines.append('')

    # 2f. Body content (exclude old TOC, refs, changelog sections)
    body_lines = []
    skip_ranges = []
    if parsed['toc_start'] >= 0:
        skip_ranges.append((parsed['toc_start'], parsed['toc_end']))
    if parsed['refs_start'] >= 0:
        skip_ranges.append((parsed['refs_start'], parsed['refs_end']))
    if parsed['changelog_start'] >= 0:
        skip_ranges.append((parsed['changelog_start'], parsed['changelog_end']))

    for i in range(parsed['body_start'], parsed['body_end']):
        # Check if in skip range
        skip = False
        for s, e in skip_ranges:
            if s <= i < e:
                skip = True
                break
        if skip:
            continue
        body_lines.append(lines[i])

    # Clean up body: remove leading/trailing empty lines and trailing separators
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    while body_lines and (not body_lines[-1].strip() or body_lines[-1].strip() == '---'):
        body_lines.pop()

    new_lines.extend(body_lines)
    new_lines.append('')
    new_lines.append('---')
    new_lines.append('')

    # 2g. References section
    new_lines.append('## 参考文件')
    new_lines.append('')
    new_lines.append('> 本文件调用的外部文件与资料（不含被引用情况）。')
    new_lines.append('')

    # Internal refs
    new_lines.append('### 内部知识库引用')
    new_lines.append('')
    if internal_refs:
        for r in internal_refs:
            relation = r.get('relation', '关联') or '关联'
            new_lines.append(f'- [{r["label"]}]({r["path"]}) — {relation}')
    else:
        new_lines.append('- (无)')
    new_lines.append('')

    # External refs
    new_lines.append('### 外部资料引用')
    new_lines.append('')
    if external_refs:
        for r in external_refs:
            new_lines.append(f'- 来源: {r["source"]}')
    else:
        new_lines.append('- (无)')
    new_lines.append('')

    # 2h. Separator
    new_lines.append('---')
    new_lines.append('')

    # 2i. Changelog
    new_lines.append('## Changelog')
    new_lines.append('')
    new_lines.append('| 日期 | 版本 | 变更说明 |')
    new_lines.append('|:----|:----|:-----|')
    if changelog_entries:
        for e in changelog_entries:
            new_lines.append(f'| {e["date"]} | {e["version"]} | {e["change"]} |')
    else:
        new_lines.append(f'| {today} | v1.0 | 初始版本 |')
    new_lines.append('')

    return '\n'.join(new_lines)


# === Main ===

def main():
    parser = argparse.ArgumentParser(description='知识内容文件格式检查/修复工具')
    parser.add_argument('target', help='目标文件或目录路径')
    parser.add_argument('--check', action='store_true', help='检查模式，报告违规')
    parser.add_argument('--fix', action='store_true', help='修复模式，重写文件')
    parser.add_argument('--dry-run', action='store_true', help='预览修复变更，不写入')
    parser.add_argument('--all', action='store_true', help='处理 knowledge/ 下全部内容文件')
    parser.add_argument('--module', help='处理指定模块目录')
    args = parser.parse_args()

    if not any([args.check, args.fix, args.dry_run]):
        args.check = True  # default mode

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

    files = collect_files(target)
    if not files:
        print(f'No content files found under {target}')
        sys.exit(0)

    total_issues = 0
    fixed_count = 0
    would_fix_count = 0

    for f in files:
        try:
            content = f.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            print(f'  ERROR reading {f}: {e}')
            continue

        parsed = parse_file(content)
        issues = check_file(parsed)
        fail_issues = [i for i in issues if i[1] == 'FAIL']

        rel = str(f.relative_to(REPO_ROOT)).replace('\\', '/')

        if args.check:
            if fail_issues:
                total_issues += len(fail_issues)
                print(f'  FAIL  {rel}')
                for cid, status, msg in fail_issues:
                    print(f'        [{cid}] {msg}')
            # Silent on pass for brevity in --all mode

        if args.dry_run or args.fix:
            # Always run fix_file (idempotent); changed flag determines if write needed
            new_content = fix_file(parsed, f)
            changed = new_content != content
            if changed:
                if args.dry_run:
                    would_fix_count += 1
                    print(f'  WOULD FIX  {rel}  ({len(fail_issues)} FAIL issues)')
                elif args.fix:
                    try:
                        f.write_text(new_content, encoding='utf-8')
                        fixed_count += 1
                        print(f'  FIXED  {rel}')
                    except Exception as e:
                        print(f'  ERROR writing {f}: {e}')

    # Summary
    print()
    print(f'=== Summary ===')
    print(f'Total files: {len(files)}')
    if args.check:
        print(f'Files with FAIL issues: {total_issues}')
    if args.dry_run:
        print(f'Files that would be fixed: {would_fix_count}')
    if args.fix:
        print(f'Files fixed: {fixed_count}')

    if args.check and total_issues > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
