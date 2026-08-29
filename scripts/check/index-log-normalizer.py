#!/usr/bin/env python3
"""
Index/Log Normalizer — enforce per-directory index.md / log.md rules.

Rules (per .trae/rules/RULE.md & skills/knowledge-wiki/SKILL.md):
  1. Every directory has index.md + log.md (except bak/oldbak/import-modules)
  2. index.md / log.md only describe the OWN directory (not subdirectory internals)
  3. index.md only lists files/subdirs + summary; NO reference relationships
  4. Format: index = table + minimal emoji (📁/📄); log = heading-list, no table/emoji

Modes:
  --check    Report violations, exit code 1 if any found
  --fix      Rewrite index.md + log.md to conform (backup old to tmp/bak/)
  --init     Create missing index.md / log.md templates only
  --dry-run  Preview what --fix would change (no writes)
  --all      Process all directories under knowledge/ (except excluded)

Usage:
  python scripts/check/index-log-normalizer.py knowledge/07_industry-research --check
  python scripts/check/index-log-normalizer.py knowledge/ --all --check
  python scripts/check/index-log-normalizer.py knowledge/ --all --dry-run
  python scripts/check/index-log-normalizer.py knowledge/ --all --init
  python scripts/check/index-log-normalizer.py knowledge/ --all --fix
"""
import sys
import re
import argparse
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from scripts.shared.workspace import WORKSPACE_ROOT as REPO_ROOT, KNOWLEDGE_ROOT, SCRIPTS_DIR

SCRIPT_DIR = SCRIPTS_DIR / "check"

# === Reuse extract_metadata from extract-index-metadata.py (importlib, hyphenated name) ===
def _load_extract_metadata():
    src = SCRIPT_DIR / 'extract-index-metadata.py'
    spec = importlib.util.spec_from_file_location('extract_index_metadata', src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.extract_metadata

extract_metadata = _load_extract_metadata()

# === Reuse parse_log from reformat-log.py ===
def _load_parse_log():
    src = SCRIPT_DIR / 'reformat-log.py'
    spec = importlib.util.spec_from_file_location('reformat_log', src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_log

parse_log = _load_parse_log()

# === Constants ===
EXCLUDED_DIRNAMES = {'bak', 'oldbak', 'import-modules', '.git', '__pycache__', 'node_modules'}
# 2026-08-03 治理决策: 以下模块的分布式 index.md/log.md 已废弃，
# 统一由 knowledge/index.md（kb-global-index.py 生成）+ knowledge/log.md（kb-global-log.py 合并）管理。
# 仅 01_survey/ 与 weekly-reports/ 保留分布式机制。
NO_INDEX_LOG_MODULES = {'02_rd', '03_AI', '04_person', '05_tools', '06_others', '07_industry-research'}
INDEX_NAMES = {'index.md', 'log.md', 'README.md'}
OP_KEYWORDS = ['新增', '创建', '更新', '修改', '修订', '删除', '移除', '迁移', '移动', '修复', '修正', '整理', '重构', '重命名',
               'add', 'create', 'update', 'delete', 'remove', 'migrate', 'move', 'fix', 'reorganize', 'refactor', 'rename']
OP_CANONICAL = {
    '新增': '新增', '创建': '新增', 'add': '新增', 'create': '新增',
    '更新': '更新', '修改': '更新', '修订': '更新', 'update': '更新',
    '删除': '删除', '移除': '删除', 'delete': '删除', 'remove': '删除',
    '迁移': '迁移', '移动': '迁移', 'migrate': '迁移', 'move': '迁移',
    '修复': '修复', '修正': '修复', 'fix': '修复',
    '整理': '整理', '重构': '整理', '重命名': '整理', 'reorganize': '整理', 'refactor': '整理', 'rename': '整理',
}

# Emoji ranges (broad strip for log entries)
EMOJI_RE = re.compile(
    '['
    '\U0001F300-\U0001F9FF'  # symbols & pictographs
    '\U0001FA00-\U0001FAFF'
    '\u2600-\u27BF'          # misc symbols, dingbats
    '\U0001F000-\U0001F02F'
    ']', flags=re.UNICODE)

DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')
MD_FILE_RE = re.compile(r'`([^`]+\.md)`|(?<![\w/])([A-Za-z0-9_\-\u4e00-\u9fa5]+\.md)(?![\w/])')


# === Directory collection ===

def uses_global_index(d: Path) -> bool:
    """目录是否属于全局索引机制模块（其 index/log 已废弃，不再检查）。"""
    try:
        rel = d.relative_to(KNOWLEDGE_ROOT)
    except ValueError:
        return False
    if not rel.parts:
        return False
    return rel.parts[0] in NO_INDEX_LOG_MODULES


def is_excluded(d: Path) -> bool:
    """True if directory should be skipped (bak/oldbak/import-modules/hidden/global-index modules)."""
    if uses_global_index(d):
        return True
    name = d.name
    if name in EXCLUDED_DIRNAMES:
        return True
    if name.startswith('.'):
        return True
    # also skip if any path part is excluded (nested)
    for part in d.relative_to(REPO_ROOT).parts if REPO_ROOT in d.parents or d == REPO_ROOT else []:
        if part in EXCLUDED_DIRNAMES:
            return True
    # check parts directly
    parts = d.parts
    for ex in EXCLUDED_DIRNAMES:
        if ex in parts:
            return True
    return False


def collect_dirs(root: Path):
    """Yield all target directories under root (excluding bak/oldbak/import-modules)."""
    if not root.is_dir():
        return
    for d in sorted(root.rglob('*')):
        if d.is_dir() and not is_excluded(d):
            yield d


# === Index generation ===

def get_subdir_summary(subdir: Path) -> str:
    """One-line summary for a subdirectory: from its index.md description, else its name."""
    idx = subdir / 'index.md'
    if idx.exists():
        try:
            content = idx.read_text(encoding='utf-8', errors='replace')
            lines = content.split('\n')
            # Prefer first blockquote description line
            for line in lines[:15]:
                s = line.strip()
                if s.startswith('>') and len(s) > 3 and not s.startswith('> #'):
                    desc = s.lstrip('>').strip()
                    if desc and not desc.startswith('**') and len(desc) > 4:
                        return desc[:120]
            # Fallback: first # title
            for line in lines[:10]:
                if line.startswith('# '):
                    return line[2:].strip()[:120]
        except Exception:
            pass
    return subdir.name


def generate_index(dir_path: Path) -> str:
    """Generate clean index.md content for a directory (own files + own subdirs only)."""
    dir_name = dir_path.name or 'knowledge'

    # Immediate subdirectories (non-excluded)
    subdirs = sorted([d for d in dir_path.iterdir()
                      if d.is_dir() and not is_excluded(d) and not d.name.startswith('.')])
    # Immediate .md files (excluding index/log/README)
    files = sorted([f for f in dir_path.iterdir()
                    if f.is_file() and f.suffix == '.md' and f.name not in INDEX_NAMES])

    lines = []
    lines.append(f'# {dir_name} 目录索引')
    lines.append('')
    lines.append('> 本目录直接文件与子目录清单。子目录内容见各子目录 index.md。')
    lines.append('')

    if subdirs:
        lines.append('## 📁 子目录')
        lines.append('')
        lines.append('| 目录 | 说明 |')
        lines.append('|:-----|:-----|')
        for sd in subdirs:
            summary = get_subdir_summary(sd)
            idx_link = f'{sd.name}/index.md' if (sd / 'index.md').exists() else f'{sd.name}/'
            lines.append(f'| [{sd.name}/]({idx_link}) | {summary} |')
        lines.append('')

    if files:
        lines.append('## 📄 文件')
        lines.append('')
        lines.append('| 文件 | 标题 | 摘要 |')
        lines.append('|:-----|:-----|:-----|')
        for f in files:
            meta = extract_metadata(f, dir_path)
            title = (meta.get('title') or f.stem).replace('|', '\\|')
            summary = (meta.get('summary') or '(无描述)').replace('|', '\\|').replace('\n', ' ')
            if len(summary) > 80:
                summary = summary[:80] + '…'
            lines.append(f'| [{f.name}]({f.name}) | {title} | {summary} |')
        lines.append('')

    # Ensure file ends with single newline
    while len(lines) > 1 and lines[-1] == '':
        lines.pop()
    lines.append('')
    return '\n'.join(lines)


# === Log generation ===

def normalize_entry(line: str, own_files: set):
    """Normalize a log entry line to `- **op** | `file` — desc`.

    Returns (normalized_line, op, filename, is_cross_dir) or (None,...) if not a log entry.
    """
    raw = line.rstrip()
    if not raw.strip():
        return (None, None, None, False)
    # Strip leading list marker
    s = raw.lstrip()
    s = re.sub(r'^[-*]\s+', '', s)
    s = re.sub(r'^\d+\.\s+', '', s)
    # Strip table syntax if it's a table row
    if s.startswith('|'):
        cells = [c.strip() for c in s.strip('|').split('|')]
        # Try to find op, file, desc among cells
        # keep non-empty cells
        cells = [c for c in cells if c]
        if not cells:
            return (None, None, None, False)
        s = ' '.join(cells)

    # Strip emoji
    s = EMOJI_RE.sub('', s).strip()
    s = re.sub(r'\s+', ' ', s)

    # Extract operation — must be at the START of the entry (anchored),
    # never matched mid-sentence (avoids false positives from summaries containing 更新/修复 etc.)
    op = None
    # 1) bold op at start: **新增** ...
    op_match = re.match(r'\*\*(.+?)\*\*', s)
    if not op_match:
        op_match = re.search(r'^\s*\*\*(.+?)\*\*', s)
    if op_match and s.index(op_match.group(0)) < 5:
        op_candidate = op_match.group(1).strip()
        for kw, canon in OP_CANONICAL.items():
            if kw in op_candidate or kw in op_candidate.lower():
                op = canon
                break
        if op:
            s = s.replace(op_match.group(0), '', 1).strip()
            s = re.sub(r'^[|·:：\-\s]+', '', s)
    if op is None:
        # 2) bare keyword at the very start (after markers already stripped)
        for kw, canon in OP_CANONICAL.items():
            if re.match(rf'{re.escape(kw)}(?![\w/])', s) or re.match(rf'{re.escape(kw)}[：:\s|]', s):
                op = canon
                s = re.sub(rf'^{re.escape(kw)}[：:\s|]*', '', s, count=1).strip()
                break
    if op is None:
        # Not a recognizable log entry — return None to keep original handling
        return (None, None, None, False)

    # Extract filename (backtick, bare .md, path-like, or markdown link)
    filename = None
    bt = re.search(r'`([^`]+)`', s)
    if bt:
        candidate = bt.group(1)
        # accept if looks like a file/path
        if '.' in candidate or '/' in candidate or candidate.endswith('.md'):
            filename = candidate
            s = s.replace(bt.group(0), '').strip()
    if not filename:
        m = MD_FILE_RE.search(s)
        if m:
            filename = m.group(1) or m.group(2)
            s = s.replace(filename, '', 1).strip()
    if not filename:
        # try path-like reference: subdir/file.md, a/b/c.md
        path_m = re.search(r'(?<![\w/])([A-Za-z0-9_\-\u4e00-\u9fa5]+/[A-Za-z0-9_\-\u4e00-\u9fa5/.]+\.md)', s)
        if path_m:
            filename = path_m.group(1)
            s = s.replace(filename, '', 1).strip()
    if not filename:
        # try markdown link
        lk = re.search(r'\[([^\]]+)\]\([^)]+\)', s)
        if lk:
            filename = lk.group(1)
            s = s.replace(lk.group(0), '').strip()

    # Clean description: strip leading separators
    desc = re.sub(r'^[|·:：\-\s]+', '', s).strip()
    desc = re.sub(r'\s+', ' ', desc)
    if desc and desc.startswith('—'):
        desc = desc[1:].strip()
    if not desc:
        desc = '(无说明)'

    # Cross-dir check: filename references a path not in own_files
    is_cross = _is_cross_ref(filename, own_files) if filename else False

    fn_display = filename if filename else '(本目录)'
    normalized = f'- **{op}** | `{fn_display}` — {desc}'
    return (normalized, op, filename, is_cross)


def extract_loglike_from_index(index_content: str, own_files: set):
    """Scan old index.md for EXPLICIT log-like lines to preserve into log.

    Conservative: only captures lines that are clearly log entries — bold-op bullets,
    🔥 markers, or table rows whose FIRST cell is an operation keyword. Skips file-listing
    table rows (| [file.md](...) | title | summary |) to avoid false positives from
    summaries that happen to contain op words like 更新/修复.

    Returns list of (date, normalized_line).
    """
    results = []
    current_date = None
    in_log_section = False
    for line in index_content.split('\n'):
        stripped = line.strip()
        # Track section context
        if stripped.startswith('#'):
            heading = stripped.lstrip('#').strip()
            in_log_section = bool(re.search(r'日志|变更|更新日志|修订记录|🔥', heading))
            # date in heading?
            dm = DATE_RE.search(stripped)
            if dm:
                current_date = dm.group(1)
            continue
        dm = DATE_RE.search(stripped)
        if dm:
            current_date = dm.group(1)

        # Skip file-listing table rows: | [file.md](...) | ... |
        if re.match(r'^\|\s*\[[^\]]+\]\([^)]+\)\s*\|', stripped):
            continue
        # Skip pure separator/header rows
        if re.match(r'^\|[\s:|-]+\|*\s*$', stripped):
            continue
        if stripped.startswith('| 文件') or stripped.startswith('| 目录') or stripped.startswith('| 模块'):
            continue

        # Only accept lines that explicitly look like log entries
        is_log_line = (
            re.match(r'^[-*]\s*\*\*(新增|更新|删除|迁移|修复|整理|创建|修改|修订|移除|移动|重构|重命名)', stripped)
            or '🔥' in stripped
            or re.match(r'^\|\s*(新增|更新|删除|迁移|修复|整理|创建|修改|修订|移除|移动|重构|重命名)\s*\|', stripped)
        )
        if not is_log_line:
            continue
        # If not in a log section and no 🔥 marker, require bold-op (stricter)
        if not in_log_section and '🔥' not in stripped:
            if not re.match(r'^[-*]\s*\*\*(新增|更新|删除|迁移|修复|整理|创建|修改|修订|移除|移动|重构|重命名)', stripped):
                continue
        norm, op, fn, is_cross = normalize_entry(line, own_files)
        if norm and op:
            d = current_date or datetime.now().strftime('%Y-%m-%d')
            results.append((d, norm))
    return results


def _strip_own_header(content: str) -> str:
    """Remove this normalizer's own header/placeholder blockquote lines so that
    re-parsing a normalized log does not convert them into phantom entries.
    (parse_log in reformat-log.py turns any `>` blockquote into a `- **新增**` entry.)
    """
    out = []
    for line in content.split('\n'):
        s = line.strip()
        if re.match(r'^# .+ 变更日志\s*$', s):
            continue
        if s == '> 本目录下文件的变更记录。':
            continue
        if s.startswith('> 暂无变更记录'):
            continue
        if s.startswith('> 以下条目引用了非本目录文件'):
            continue
        out.append(line)
    return '\n'.join(out)


def parse_log_strict(content: str):
    """Deterministic parse for ALREADY-normalized logs.

    Captures ONLY `## <YYYY-MM-DD>` date headings + `## 待迁移` section, collecting
    `- ` bullet lines under each. Ignores blockquotes, tables, headers, orphan lines.
    Returns dict {date_str: [bullet_lines]}; special key '__CROSS__' for the 待迁移 section.

    This is idempotent: a normalized log re-parses to identical entries.
    """
    entries = defaultdict(list)
    current = None
    for line in content.split('\n'):
        m = re.match(r'^##\s+(\d{4}-\d{2}-\d{2})(?:\s|$)', line)
        if m:
            current = m.group(1)
            continue
        if re.match(r'^##\s+待迁移', line):
            current = '__CROSS__'
            continue
        # Other ## headings end a section's bullet collection
        if re.match(r'^##\s+', line) and current == '__CROSS__':
            current = None
            continue
        if current and line.startswith('- '):
            entries[current].append(line)
    return entries


def _is_normalized_log(content: str) -> bool:
    """Detect if a log.md was produced by this normalizer.

    Signature: first non-empty line is `# <name> 变更日志`.
    Used to branch between strict (idempotent) and full (migrating) parsers.
    """
    for line in content.split('\n'):
        s = line.strip()
        if not s:
            continue
        return bool(re.match(r'^# .+ 变更日志\s*$', s))
    return False


NORMALIZED_ENTRY_RE = re.compile(
    r'^-\s+\*\*(.+?)\*\*\s*\|\s*`([^`]*)`\s*—\s*(.+)$')


def parse_normalized_entry(line: str):
    """Parse an already-normalized log entry: `- **op** | `file` — desc`.

    Returns (op, filename, desc) or None if not in standard format.
    Does NOT re-normalize — used for idempotent re-processing.
    """
    m = NORMALIZED_ENTRY_RE.match(line.strip())
    if not m:
        return None
    return (m.group(1).strip(), m.group(2).strip(), m.group(3).strip())


def _is_cross_ref(filename: str, own_files: set) -> bool:
    """Check if a filename reference points outside the own directory.

    `filename` is the value extracted from a log entry (may be a path like
    `subdir/file.md`, a bare name like `file.md`, or `(本目录)` placeholder).
    `own_files` is the set of immediate file + subdir names in this directory.
    """
    if not filename or filename == '(本目录)':
        return False
    bare = filename.split('/')[-1].split('\\')[-1]
    if '/' in filename or '\\' in filename:
        # References a path — cross-dir unless the bare name is an own file
        return bare not in own_files
    # Bare name — cross-dir if not an own file/dir
    return bare not in own_files and not filename.endswith('/')


def generate_log(dir_path: Path, existing_log_content: str, extra_entries=None):
    """Generate clean log.md content (heading-list format, oldest-first 正序, 2026-08-15 起)."""
    # For cross-dir checking: include ALL .md files (index.md/log.md/README.md
    # are own files too — log entries about them are NOT cross-directory).
    own_files = {f.name for f in dir_path.iterdir()
                 if f.is_file() and f.suffix == '.md'}
    own_files |= {d.name for d in dir_path.iterdir() if d.is_dir() and not is_excluded(d)}

    entries_by_date = defaultdict(list)  # date -> list of (normalized, is_cross)
    cross_entries = []

    # Parse existing log — branch on whether it's already normalized by us.
    # Idempotency contract: a normalized log re-parses to identical entries.
    if existing_log_content and existing_log_content.strip():
        if _is_normalized_log(existing_log_content):
            # Already normalized — use STRICT parser (only ## date + ## 待迁移 + - bullets).
            # parse_log (full) mishandles ## 待迁移 (treats it as continuation of prev date)
            # and turns our header blockquotes into phantom - **新增** entries.
            strict_entries = parse_log_strict(existing_log_content)
            for date_key, entry_lines in strict_entries.items():
                if date_key == '__CROSS__':
                    # Cross-entries: "- [date] {norm}" format.
                    # Strip ALL accumulated [date]/[UNKNOWN] prefixes from prior runs
                    # (old normalizer could prepend - [未知日期] on each run).
                    # Also discard phantom entries generated from our own blockquotes.
                    PHANTOM_MARKERS = ('以下条目引用了非本目录文件',
                                       '本目录下文件的变更记录',
                                       '暂无变更记录')
                    for line in entry_lines:
                        content = line
                        extracted_date = None
                        # Recursively strip leading "- [xxx]" prefixes
                        while True:
                            m = re.match(
                                r'^-\s*\[(\d{4}-\d{2}-\d{2}|未知日期|UNKNOWN)\]\s*-\s*(.+)$',
                                content)
                            if not m:
                                m = re.match(
                                    r'^-\s*\[(\d{4}-\d{2}-\d{2}|未知日期|UNKNOWN)\]\s+(.+)$',
                                    content)
                            if not m:
                                break
                            d = m.group(1)
                            if re.match(r'\d{4}-\d{2}-\d{2}$', d):
                                extracted_date = d
                            content = m.group(2)
                        # Skip phantom entries (echoes of our own header/blockquotes)
                        if any(pm in content for pm in PHANTOM_MARKERS):
                            continue
                        if not extracted_date:
                            extracted_date = '未知日期'
                        cross_entries.append((extracted_date, content))
                else:
                    for line in entry_lines:
                        # Strip stale [date] prefix if present (from old normalizer)
                        line_clean = re.sub(
                            r'^-\s*\[\d{4}-\d{2}-\d{2}\]\s*', '', line)
                        # Already-normalized line: parse WITHOUT re-normalizing
                        # (re-normalizing doubles `(本目录)` placeholders etc.)
                        parsed = parse_normalized_entry(line_clean)
                        if parsed:
                            _, filename, _ = parsed
                            # Cross-dir check only — keep original line verbatim
                            is_cross = _is_cross_ref(filename, own_files)
                            if is_cross:
                                cross_entries.append((date_key, line_clean))
                            else:
                                entries_by_date[date_key].append(line_clean)
                        else:
                            # Not in standard format but captured by strict parser;
                            # keep as-is (already emoji-free per prior normalization)
                            entries_by_date[date_key].append(line_clean)
        else:
            # Not yet normalized — use FULL parser (handles tables/blockquotes/plain bullets)
            try:
                header, entries_by_date_raw, range_sections = parse_log(
                    _strip_own_header(existing_log_content))
            except Exception:
                entries_by_date_raw = {}
                range_sections = []
            for date, entry_lines in entries_by_date_raw.items():
                for line in entry_lines:
                    norm, op, fn, is_cross = normalize_entry(line, own_files)
                    if norm:
                        if is_cross:
                            cross_entries.append((date, norm))
                        else:
                            entries_by_date[date].append(norm)
                    else:
                        # keep unparseable lines as-is (preserve info) under the date,
                        # but strip emoji so the result conforms to no-emoji rule
                        stripped = EMOJI_RE.sub('', line).strip()
                        stripped = re.sub(r'\s+', ' ', stripped)
                        if stripped and not stripped.startswith('#') and not stripped.startswith('|') \
                                and not stripped.startswith('>') and stripped != '---':
                            entries_by_date[date].append(stripped)
            for range_str, entry_lines in range_sections:
                start = range_str.split(' ~ ')[0] if ' ~ ' in range_str else range_str
                for line in entry_lines:
                    norm, op, fn, is_cross = normalize_entry(line, own_files)
                    if norm:
                        if is_cross:
                            cross_entries.append((start, norm))
                        else:
                            entries_by_date[start].append(norm)

    # Merge extra entries (from old index.md log-like content)
    if extra_entries:
        for date, norm in extra_entries:
            entries_by_date[date].append(norm)

    dir_name = dir_path.name or 'knowledge'
    lines = []
    lines.append(f'# {dir_name} 变更日志')
    lines.append('')
    lines.append('> 本目录下文件的变更记录。')
    lines.append('')

    # Sort dates ascending (oldest first, 2026-08-15 起统一正序). Unknown goes last.
    def date_key(d):
        if re.match(r'\d{4}-\d{2}-\d{2}', d):
            return (0, d)
        return (1, d)
    sorted_dates = sorted(entries_by_date.keys(), key=date_key, reverse=False)

    for date in sorted_dates:
        ents = entries_by_date[date]
        # dedupe preserving order
        seen = set()
        deduped = []
        for e in ents:
            if e not in seen:
                seen.add(e)
                deduped.append(e)
        if not deduped:
            continue
        display = date if re.match(r'\d{4}-\d{2}-\d{2}', date) else '未知日期'
        lines.append(f'## {display}')
        lines.append('')
        lines.extend(deduped)
        lines.append('')

    # Cross-directory entries (待迁移) — dedupe by (date, norm) pair
    if cross_entries:
        lines.append('## 待迁移')
        lines.append('')
        lines.append('> 以下条目引用了非本目录文件，待人工迁移至对应目录的 log.md。')
        lines.append('')
        seen_cross = set()
        cross_deduped = []
        for date, norm in cross_entries:
            key = (date, norm)
            if key not in seen_cross:
                seen_cross.add(key)
                cross_deduped.append((date, norm))
        cross_sorted = sorted(cross_deduped, key=lambda x: x[0], reverse=False)
        for date, norm in cross_sorted:
            lines.append(f'- [{date}] {norm}')
        lines.append('')

    # If completely empty, add a placeholder note
    if not sorted_dates and not cross_entries:
        lines.append(f'> 暂无变更记录。文件初始化于 {datetime.now().strftime("%Y-%m-%d")}。')
        lines.append('')

    while len(lines) > 1 and lines[-1] == '':
        lines.pop()
    lines.append('')
    return '\n'.join(lines)


# === Checking ===

def check_index(dir_path: Path, content: str) -> list:
    """Return list of violation strings for index.md."""
    issues = []
    if content is None:
        return issues
    # Reference-relationship markers
    ref_markers = ['关联矩阵', '交叉引用', '引用关系', '反向链接', '知识图谱总览', '跨领域关联', '阅读路径']
    for marker in ref_markers:
        if marker in content:
            issues.append(f'index.md 含引用关系内容: 「{marker}」')
            break
    # Log-like content — only flag when markers appear as SECTION/line markers
    # (line starts with 🔥 / - 🔥 / > 🔥, or explicit "🔥 新增"), NOT when 🔥 is embedded
    # inside a table cell (file summary), since regenerated indexes store summaries in tables.
    log_section_markers = ['迁移入', '迁移出', '更新日志', '变更记录']
    for marker in log_section_markers:
        if marker in content:
            issues.append(f'index.md 含日志类内容: 「{marker}」(应移至 log.md)')
            break
    # 🔥 as a line marker (not inside table cells)
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('|'):
            continue  # table row — 🔥 here is part of a file summary, not a log marker
        if stripped.startswith('🔥') or stripped.startswith('- 🔥') or stripped.startswith('> 🔥'):
            issues.append('index.md 含日志类标记: 「🔥」(应移至 log.md)')
            break
    # Subdirectory file listings: paths like subdir/file.md in tables (not just subdir/ links)
    # Look for markdown links to files inside subdirs: ](subdir/something.md)
    subdir_file_links = re.findall(r'\]\(([^)]+\.md)\)', content)
    own_files = {f.name for f in dir_path.iterdir()
                 if f.is_file() and f.suffix == '.md' and f.name not in INDEX_NAMES}
    own_subdirs = {d.name for d in dir_path.iterdir() if d.is_dir() and not is_excluded(d)}
    for link in subdir_file_links:
        # normalize: strip anchor
        path = link.split('#')[0]
        if '/' in path:
            top = path.split('/')[0]
            if top in own_subdirs and not path.endswith('/index.md') and not path.endswith('/'):
                # links to a file inside an own subdir (not the subdir's index)
                issues.append(f'index.md 描述了子目录内文件: `{link}`')
                break
    # Format: should have a table (| 文件 | or | 目录 |)
    if files_exist := bool(own_files):
        if '| 文件 |' not in content and '| 文件' not in content and '| 标题 |' not in content:
            # may still be list-based
            if not re.search(r'\|\s*文件', content) and not re.search(r'\|\s*标题', content):
                issues.append('index.md 文件清单未用表格格式 (应为 | 文件 | 标题 | 摘要 |)')
    return issues


def check_log(dir_path: Path, content: str) -> list:
    """Return list of violation strings for log.md."""
    issues = []
    if content is None:
        return issues
    own_files = {f.name for f in dir_path.iterdir()
                 if f.is_file() and f.suffix == '.md' and f.name not in INDEX_NAMES}
    own_subdirs = {d.name for d in dir_path.iterdir() if d.is_dir() and not is_excluded(d)}
    lines = content.split('\n')
    in_header = True
    for i, line in enumerate(lines, 1):
        if in_header:
            if line.strip() == '---':
                in_header = False
            continue
        # Tables in body
        if line.startswith('|') and not re.match(r'^\|[\s:|-]+\|*\s*$', line):
            issues.append(f'L{i}: log.md 含表格行 (应为标题列表格式)')
            break
    # Emoji in entries
    for line in lines:
        if line.strip().startswith('-') and EMOJI_RE.search(line):
            issues.append('log.md 条目含 emoji (应去除)')
            break
    return issues


def check_directory(dir_path: Path) -> list:
    """Return list of violations for a directory."""
    issues = []
    idx_path = dir_path / 'index.md'
    log_path = dir_path / 'log.md'
    if not idx_path.exists():
        issues.append('缺失 index.md')
    else:
        content = idx_path.read_text(encoding='utf-8', errors='replace')
        issues.extend(check_index(dir_path, content))
    if not log_path.exists():
        issues.append('缺失 log.md')
    else:
        content = log_path.read_text(encoding='utf-8', errors='replace')
        issues.extend(check_log(dir_path, content))
    return issues


# === Fixing ===

def backup_file(src: Path, backup_root: Path):
    """Copy src to backup_root mirroring relative path."""
    if not src.exists():
        return
    try:
        rel = src.relative_to(REPO_ROOT)
    except ValueError:
        rel = Path(src.name)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def fix_directory(dir_path: Path, dry_run: bool, backup_root: Path = None, report: list = None):
    """Rewrite index.md + log.md for a directory. Returns (index_changed, log_changed)."""
    idx_path = dir_path / 'index.md'
    log_path = dir_path / 'log.md'

    old_index = idx_path.read_text(encoding='utf-8', errors='replace') if idx_path.exists() else ''
    old_log = log_path.read_text(encoding='utf-8', errors='replace') if log_path.exists() else ''

    own_files = {f.name for f in dir_path.iterdir()
                 if f.is_file() and f.suffix == '.md'}

    # Preserve log-like info from old index
    extra_entries = extract_loglike_from_index(old_index, own_files) if old_index else []

    new_index = generate_index(dir_path)
    new_log = generate_log(dir_path, old_log, extra_entries)

    index_changed = (new_index != old_index)
    log_changed = (new_log != old_log)

    if dry_run:
        if index_changed:
            report.append(f'  [index.md] 将重写 ({len(old_index)} → {len(new_index)} chars)')
        if log_changed:
            report.append(f'  [log.md] 将重写 ({len(old_log)} → {len(new_log)} chars)')
        return (index_changed, log_changed)

    # Backup before write
    if backup_root is not None:
        if index_changed and old_index:
            backup_file(idx_path, backup_root)
        if log_changed and old_log:
            backup_file(log_path, backup_root)

    if index_changed:
        idx_path.write_text(new_index, encoding='utf-8')
    if log_changed:
        log_path.write_text(new_log, encoding='utf-8')
    return (index_changed, log_changed)


def init_directory(dir_path: Path, report: list = None):
    """Create missing index.md / log.md templates."""
    idx_path = dir_path / 'index.md'
    log_path = dir_path / 'log.md'
    created = []
    if not idx_path.exists():
        idx_path.write_text(generate_index(dir_path), encoding='utf-8')
        created.append('index.md')
    if not log_path.exists():
        log_path.write_text(generate_log(dir_path, ''), encoding='utf-8')
        created.append('log.md')
    if created and report is not None:
        report.append(f'  创建: {", ".join(created)}')
    return created


# === Main ===

def main():
    parser = argparse.ArgumentParser(
        description='Index/Log normalizer — enforce per-directory index.md/log.md rules',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('path', nargs='?', help='Target directory (or knowledge/ root with --all)')
    parser.add_argument('--all', action='store_true', help='Process all dirs under knowledge/ (except excluded)')
    parser.add_argument('--check', action='store_true', help='Report violations, exit 1 if any')
    parser.add_argument('--fix', action='store_true', help='Rewrite index.md + log.md to conform')
    parser.add_argument('--init', action='store_true', help='Create missing index.md/log.md only')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes, no writes')
    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        sys.exit(1)

    target = Path(args.path).resolve()
    if not target.exists():
        print(f'Error: {target} does not exist')
        sys.exit(1)

    # Determine directories to process
    if args.all:
        # target should be knowledge/ root; collect all subdirs + root itself
        dirs = [target] + list(collect_dirs(target))
    else:
        if target.is_dir():
            dirs = [target]
        else:
            print(f'Error: {target} is not a directory')
            sys.exit(1)

    # Filter excluded
    dirs = [d for d in dirs if not is_excluded(d)]

    mode = 'check' if args.check else ('fix' if args.fix else ('init' if args.init else 'dry-run'))
    if not (args.check or args.fix or args.init):
        args.dry_run = True  # default to dry-run if no mode

    print(f'🔧 Index/Log Normalizer — mode: {mode}, dirs: {len(dirs)}')

    if args.check:
        total_violations = 0
        dirs_with_issues = 0
        for d in dirs:
            issues = check_directory(d)
            if issues:
                dirs_with_issues += 1
                total_violations += len(issues)
                rel = d.relative_to(REPO_ROOT) if REPO_ROOT in d.parents or d == REPO_ROOT else d
                print(f'\n⚠️  {rel}')
                for iss in issues:
                    print(f'   - {iss}')
        print(f'\n{"="*50}')
        print(f'检查完成: {dirs_with_issues}/{len(dirs)} 目录有违规, 共 {total_violations} 条')
        sys.exit(1 if total_violations else 0)

    if args.init:
        created_count = 0
        for d in dirs:
            report = []
            created = init_directory(d, report)
            if created:
                created_count += len(created)
                rel = d.relative_to(REPO_ROOT) if REPO_ROOT in d.parents or d == REPO_ROOT else d
                print(f'📄 {rel}')
                for r in report:
                    print(r)
        print(f'\n{"="*50}')
        print(f'初始化完成: 创建 {created_count} 个文件')
        sys.exit(0)

    # fix or dry-run
    backup_root = None
    if args.fix:
        backup_root = REPO_ROOT / 'knowledge' / 'bak' / f'index-log-fix-{datetime.now().strftime("%Y-%m-%d")}'
    index_changed_count = 0
    log_changed_count = 0
    for d in dirs:
        report = []
        ic, lc = fix_directory(d, args.dry_run, backup_root, report)
        if ic or lc:
            rel = d.relative_to(REPO_ROOT) if REPO_ROOT in d.parents or d == REPO_ROOT else d
            print(f'📄 {rel}')
            for r in report:
                print(r)
            if ic:
                index_changed_count += 1
            if lc:
                log_changed_count += 1
    print(f'\n{"="*50}')
    if args.dry_run:
        print(f'预览完成: {index_changed_count} index.md, {log_changed_count} log.md 将变更 (dry-run, 未写入)')
    else:
        print(f'修复完成: 重写 {index_changed_count} index.md, {log_changed_count} log.md')
        if backup_root:
            print(f'备份位置: {backup_root}')
    sys.exit(0)


if __name__ == '__main__':
    main()
