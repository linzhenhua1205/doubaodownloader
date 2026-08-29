#!/usr/bin/env python3
"""
Link augmenter: detect bare file-name references in markdown and convert them to links.

Scans all .md files under knowledge/, builds a filename index, then for each file
finds mentions of other file titles / stems that appear as plain text and wraps them
in markdown links, pointing to the correct relative path.

Safe by default: use --dry-run first; use --fix to apply changes.

Usage:
    python scripts/check/link-augmenter.py --dry-run
    python scripts/check/link-augmenter.py --fix
    python scripts/check/link-augmenter.py --module 02_rd --fix
    python scripts/check/link-augmenter.py --file 02_rd/some-page.md --dry-run
"""
import sys
import re
import argparse
from pathlib import Path
from collections import defaultdict

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

SKIP_DIRS = {'bak', 'import-modules', 'node_modules', '.git', '.bak', 'oldbak', 'archive', 'archived'}
SKIP_FILES = {'index.md', 'log.md', 'README.md'}

# Keys that look like these patterns will be skipped (too noisy / not meaningful as bare refs)
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TRACKING_PATTERN = re.compile(r'^tracking$', re.IGNORECASE)
# Skip very common English words that are unlikely to be intentional file references
COMMON_WORDS = {
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her',
    'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its',
    'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its',
    'set', 'put', 'say', 'she', 'too', 'use', 'than', 'then', 'this', 'will',
    'your', 'from', 'they', 'been', 'have', 'were', 'that', 'with', 'what',
    'when', 'make', 'just', 'like', 'time', 'very', 'know', 'take', 'into',
    'year', 'some', 'them', 'also', 'only', 'come', 'over', 'such', 'work',
    'world', 'still', 'should', 'could', 'about', 'these', 'first', 'after',
}

# Regex for markdown inline elements we must NOT modify
# We will split the line into "code zones" and "text zones", and only
# augment links in text zones.
CODE_FENCE_RE = re.compile(r'^```')
INLINE_CODE_RE = re.compile(r'`[^`]+`')
EXISTING_LINK_TEXT_RE = re.compile(r'\[([^\]]+)\]\([^)]+\)')
IMAGE_RE = re.compile(r'!\[[^\]]*\]\([^)]+\)')
HEADING_RE = re.compile(r'^(#{1,6}\s+)')
TABLE_ROW_RE = re.compile(r'^\s*\|.*\|\s*$')
HTML_TAG_RE = re.compile(r'<[^>]+>')
URL_RE = re.compile(r'https?://\S+')


def extract_title(filepath: Path) -> str:
    """Extract the H1 title from a markdown file, or return stem."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''
    for line in content.split('\n')[:20]:
        if line.startswith('# ') and not line.startswith('## '):
            return line[2:].strip()
    return filepath.stem


CHINESE_CHAR_RE = re.compile(r'[\u4e00-\u9fff]')


def _is_noisy_key(key: str) -> bool:
    """Return True if a key is too noisy/common to be used for link augmentation.

    Quality heuristic:
    - Keys with Chinese characters: usually good (titles, technical terms)
    - English-only keys: need to be long enough and not common words
    """
    k = key.strip().lower()
    if not k:
        return True
    if DATE_PATTERN.match(k):
        return True
    if TRACKING_PATTERN.match(k):
        return True
    if k in COMMON_WORDS:
        return True
    if k.isdigit():
        return True
    digits = sum(1 for c in k if c.isdigit())
    if len(k) > 0 and digits / len(k) > 0.5:
        return True
    if len(k) < 4:
        return True

    # Check if key contains Chinese characters
    has_chinese = bool(CHINESE_CHAR_RE.search(k))

    if has_chinese:
        # Chinese keys are usually meaningful — keep them if >= 4 chars
        return len(k) < 4
    else:
        # English-only keys are risky — require longer length AND hyphens/underscores
        # to avoid matching common words like "aggregation", "performance", etc.
        if len(k) < 12:
            return True
        # Require at least one hyphen or underscore (suggests a file name / technical term)
        if '-' not in k and '_' not in k:
            return True
        return False


def build_file_index(knowledge_dir: Path, titles_only: bool = False) -> dict:
    """Build a lookup from filename stems / titles to list of (relative_path, title).
    Multiple files may share a stem; we resolve ambiguity later.

    Args:
        titles_only: if True, only index by title (not by stem).
            More precise but fewer matches. Recommended for first pass.
    """
    index = defaultdict(list)  # key -> list of (rel_path, title)
    all_files = {}

    for p in sorted(knowledge_dir.rglob('*.md')):
        if p.name in SKIP_FILES:
            continue
        if any(skip in p.parts for skip in SKIP_DIRS):
            continue
        rel = str(p.relative_to(knowledge_dir)).replace('\\', '/')
        title = extract_title(p)
        all_files[rel] = (p, title)

        stem = p.stem
        # Index by title (always preferred — more unique)
        if title and len(title) >= 4 and not _is_noisy_key(title):
            index[title.lower()].append((rel, title))

        # Index by stem only if not titles_only and stem is meaningful
        if not titles_only and not _is_noisy_key(stem):
            index[stem.lower()].append((rel, title))

    return dict(index), all_files


def find_best_match(source_rel: str, candidates: list) -> str:
    """Pick the best candidate file path for a reference in source_rel.
    Preference: same directory > same module > shortest path.
    """
    if len(candidates) == 1:
        return candidates[0][0]

    source_parts = source_rel.split('/')
    source_module = source_parts[0] if len(source_parts) > 1 else ''

    def score(cand):
        cand_rel = cand[0]
        cand_parts = cand_rel.split('/')
        cand_module = cand_parts[0] if len(cand_parts) > 1 else ''
        s = 0
        if cand_module == source_module:
            s += 100
        if len(cand_parts) == len(source_parts):
            s += 10
        s -= len(cand_parts)
        return s

    best = max(candidates, key=score)
    return best[0]


def relative_link_from(source_rel: str, target_rel: str) -> str:
    """Compute relative path from source file to target file."""
    src_parts = source_rel.split('/')
    tgt_parts = target_rel.split('/')

    # Find common prefix
    common = 0
    for a, b in zip(src_parts[:-1], tgt_parts):
        if a == b:
            common += 1
        else:
            break

    up = len(src_parts) - 1 - common
    down = tgt_parts[common:]
    parts = ['..'] * up + down
    if not parts:
        return tgt_parts[-1]
    return '/'.join(parts)


def iter_text_spans(line: str) -> list:
    """Return list of (start, end) tuples for text regions (not inside code/links/images/html).
    These are regions where we may add links.
    """
    # Collect all "forbidden" spans
    forbidden = []

    # Inline code
    for m in INLINE_CODE_RE.finditer(line):
        forbidden.append((m.start(), m.end()))

    # Existing markdown links — we should NOT add links inside link text,
    # but the link TEXT is text. However, adding a link inside link text
    # would produce nested links which is invalid. So we skip the whole
    # [text](url) span.
    for m in EXISTING_LINK_TEXT_RE.finditer(line):
        forbidden.append((m.start(), m.end()))

    # Images
    for m in IMAGE_RE.finditer(line):
        forbidden.append((m.start(), m.end()))

    # URLs
    for m in URL_RE.finditer(line):
        forbidden.append((m.start(), m.end()))

    # HTML tags
    for m in HTML_TAG_RE.finditer(line):
        forbidden.append((m.start(), m.end()))

    if not forbidden:
        return [(0, len(line))]

    forbidden.sort()
    spans = []
    cursor = 0
    for start, end in forbidden:
        if cursor < start:
            spans.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < len(line):
        spans.append((cursor, len(line)))
    return spans


_combined_pattern_cache = {}
_key_cache = {}


def build_combined_pattern(file_index: dict, min_key_len: int = 3) -> tuple:
    """Build a single combined regex pattern from all keys in file_index.
    Returns (compiled_pattern, sorted_keys_by_len_desc).
    Cached for performance.
    """
    cache_key = (id(file_index), min_key_len)
    if cache_key in _combined_pattern_cache:
        return _combined_pattern_cache[cache_key]

    # Filter keys by min length and sort by length DESC (longer matches first)
    keys = [k for k in file_index.keys() if len(k) >= min_key_len]
    keys.sort(key=lambda k: -len(k))

    # Build alternation pattern — longer keys first so they match first
    escaped = [re.escape(k) for k in keys]
    pattern = re.compile(r'(?<![A-Za-z0-9/\\.])(' + '|'.join(escaped) + r')(?![A-Za-z0-9])',
                         re.IGNORECASE)

    _combined_pattern_cache[cache_key] = (pattern, keys)
    return pattern, keys


def augment_line(line: str, source_rel: str, file_index: dict, all_files: dict,
                 min_key_len: int = 3) -> tuple:
    """Augment a single line. Returns (new_line, added_count).

    Uses a single combined regex for all keys — much faster than per-key iteration.
    Longer keys are matched first (regex alternation ordered by length desc).
    """
    if not line.strip():
        return line, 0

    if HEADING_RE.match(line):
        return line, 0

    text_spans = iter_text_spans(line)
    if not text_spans:
        return line, 0

    pattern, _ = build_combined_pattern(file_index, min_key_len)

    replacements = []

    for span_start, span_end in text_spans:
        segment = line[span_start:span_end]
        for m in pattern.finditer(segment):
            abs_start = span_start + m.start()
            abs_end = span_start + m.end()

            overlap = False
            for rs, re_, _ in replacements:
                if abs_start < re_ and abs_end > rs:
                    overlap = True
                    break
            if overlap:
                continue

            matched_key = m.group(0).lower()
            matched_text = m.group(0)

            # Check if match is followed by .md — if so, extend the match to include it
            ext = ''
            if line[abs_end:abs_end+3] == '.md':
                ext = '.md'
                abs_end += 3
                matched_text_full = matched_text + ext
            else:
                matched_text_full = matched_text

            candidates = file_index.get(matched_key, [])
            if not candidates:
                continue

            target_rel = find_best_match(source_rel, candidates)

            if target_rel == source_rel:
                continue

            rel_path = relative_link_from(source_rel, target_rel)
            replacement = f'[{matched_text_full}]({rel_path})'
            replacements.append((abs_start, abs_end, replacement))

    if not replacements:
        return line, 0

    replacements.sort(key=lambda x: x[0], reverse=True)
    new_line = line
    for start, end, repl in replacements:
        new_line = new_line[:start] + repl + new_line[end:]

    return new_line, len(replacements)


def augment_file(filepath: Path, rel_path: str, file_index: dict, all_files: dict,
                 dry_run: bool = True, min_key_len: int = 6) -> int:
    """Augment links in a single file. Returns count of links added."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return 0

    lines = content.split('\n')
    new_lines = []
    total_added = 0
    in_code_fence = False

    for i, line in enumerate(lines):
        # Track code fences
        if CODE_FENCE_RE.match(line.strip()):
            in_code_fence = not in_code_fence
            new_lines.append(line)
            continue

        if in_code_fence:
            new_lines.append(line)
            continue

        new_line, added = augment_line(line, rel_path, file_index, all_files, min_key_len=min_key_len)
        new_lines.append(new_line)
        total_added += added

    if total_added > 0 and not dry_run:
        filepath.write_text('\n'.join(new_lines), encoding='utf-8')

    return total_added


def main():
    parser = argparse.ArgumentParser(
        description='Detect bare file references and add markdown links',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python link-augmenter.py --dry-run
  python link-augmenter.py --fix
  python link-augmenter.py --module 02_rd --fix
  python link-augmenter.py --file 02_rd/page.md --dry-run
        """
    )
    parser.add_argument('--dry-run', action='store_true', help='Preview changes (default)')
    parser.add_argument('--fix', action='store_true', help='Apply changes to files')
    parser.add_argument('--module', '-m', help='Only scan a specific module directory')
    parser.add_argument('--file', '-f', help='Only scan a specific file (relative to knowledge/)')
    parser.add_argument('--knowledge-dir', default='knowledge',
                        help='Path to knowledge directory (default: knowledge/)')
    parser.add_argument('--min-len', type=int, default=6,
                        help='Minimum key length to consider (default: 6)')
    parser.add_argument('--titles-only', action='store_true',
                        help='Only match by file title (not by filename stem). More precise.')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show details for each modified file')

    args = parser.parse_args()

    knowledge_dir = Path(args.knowledge_dir)
    if not knowledge_dir.is_dir():
        print(f"Error: {knowledge_dir} is not a directory")
        sys.exit(1)

    dry_run = not args.fix  # default is dry-run

    print(f"Building file index from {knowledge_dir}...", file=sys.stderr)
    file_index, all_files = build_file_index(knowledge_dir, titles_only=args.titles_only)
    print(f"  Indexed {len(all_files)} files, {len(file_index)} keys", file=sys.stderr)

    # Determine which files to process
    if args.file:
        target_files = [args.file]
    elif args.module:
        # Include all .md files in module, even index.md/log.md (they need links too)
        target_files = []
        mod_dir = knowledge_dir / args.module
        if mod_dir.is_dir():
            for p in sorted(mod_dir.rglob('*.md')):
                if any(skip in p.parts for skip in SKIP_DIRS):
                    continue
                rel = str(p.relative_to(knowledge_dir)).replace('\\', '/')
                target_files.append(rel)
    else:
        # Process all content files (skip index.md/log.md from target, but they're indexed for matching)
        target_files = list(all_files.keys())

    print(f"Processing {len(target_files)} file(s)...", file=sys.stderr)

    total_added = 0
    modified_files = 0

    for rel_path in sorted(target_files):
        if rel_path in all_files:
            filepath, _ = all_files[rel_path]
        else:
            filepath = knowledge_dir / rel_path
            if not filepath.exists():
                continue
        added = augment_file(filepath, rel_path, file_index, all_files,
                             dry_run=dry_run, min_key_len=args.min_len)
        if added > 0:
            total_added += added
            modified_files += 1
            if args.verbose or dry_run:
                action = 'Would add' if dry_run else 'Added'
                print(f"  {action} {added} link(s) in {rel_path}")

    mode = 'DRY-RUN' if dry_run else 'FIXED'
    print()
    print(f"## Link Augmentation Report [{mode}]")
    print()
    print(f"| 指标 | 数量 |")
    print(f"|:-----|-----:|")
    print(f"| 扫描文件数 | {len(target_files)} |")
    print(f"| 被修改文件 | {modified_files} |")
    print(f"| 新增链接数 | {total_added} |")
    print()

    if dry_run and modified_files > 0:
        print("> Run with --fix to apply these changes.")
        print()

    sys.exit(0)


if __name__ == '__main__':
    main()
