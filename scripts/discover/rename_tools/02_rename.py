"""Rename markdown files to short English filenames (<=30 chars total).

Format: <cat_code>_q<N>_<keyword_slug>.md
- cat_code: 3-letter English code per category
- N: question number extracted from original filename
- keyword_slug: 1-2 English keywords derived from frontmatter title via jieba + dict

Side effects:
- Renames files in-place
- Writes rename_map.json (old_path -> new_path) and rename_report.json (stats)
- Does NOT touch index.md / README.md (separate step)
- Does NOT convert line endings (separate step)
"""
import json
import os
import re
import unicodedata
import sys
from pathlib import Path
from collections import Counter, defaultdict

import jieba

DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    DISCOVER_NEWWIKI2_DOCS,
    CATEGORY_CODES, STOPWORDS, TERM_DICT, lookup,
    MAX_SHORT_FILENAME_LEN, FILENAME_EXT
)

DOCS = DISCOVER_NEWWIKI2_DOCS
TOOLS = Path(__file__).parent

MAX_LEN = MAX_SHORT_FILENAME_LEN
EXT = FILENAME_EXT

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TITLE_RE = re.compile(r'^title:\s*(.+?)\s*$', re.MULTILINE)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
QNUM_RE = re.compile(r'_Q(\d+)_')

# Files we should NEVER rename (helpers, indices, planning artifacts)
PROTECTED_NAMES = {
    "index.md", "README.md",
    "findings.md", "progress.md", "task_plan.md",  # planning artifacts
    "error_log.json", "generation_progress.json",  # metadata
}


def extract_title(path: Path) -> str:
    """Get title from frontmatter, fallback to H1, fallback to filename stem."""
    try:
        # Use errors='replace' for files with encoding issues
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return path.stem
    m = FRONTMATTER_RE.match(text)
    if m:
        tm = TITLE_RE.search(m.group(1))
        if tm:
            return tm.group(1).strip().strip('"').strip("'")
    h1 = H1_RE.search(text)
    if h1:
        return h1.group(1).strip()
    return path.stem


def extract_q_number(filename: str) -> str:
    """Extract the Q number from original filename, e.g., 'xxx_Q10_xxx.md' -> '10'."""
    m = QNUM_RE.search(filename)
    return m.group(1) if m else "0"


def tokenize_title(title: str):
    """Tokenize a Chinese title using jieba, return list of meaningful tokens."""
    # First strip punctuation / special chars
    # Remove English/ASCII punctuation
    cleaned = re.sub(r'[，。？！、；：\u201c\u201d\u2018\u2019《》（）【】「」()\[\]{},.!?:;\'"\\/]', ' ', title)
    # Split on numbers and english / chinese boundary
    tokens = []
    for raw in jieba.cut(cleaned, HMM=True):
        t = raw.strip()
        if not t or t == ' ':
            continue
        tokens.append(t)
    return tokens


def is_chinese_char(ch):
    return 'CJK' in unicodedata.name(ord(ch), '')


def slugify_token(tok):
    """Try to map a token to an English slug.

    Strategy (longest-match first):
    1. Exact lookup in TERM_DICT
    2. If token is pure ASCII alphanumeric, lowercase and use directly
    3. Try sliding-window longest match against TERM_DICT keys
    4. Fallback: pypinyin first letters (acronym)
    """
    tok = tok.strip()
    if not tok:
        return None

    # Exact dict lookup
    direct = lookup(tok)
    if direct:
        return direct

    # Pure ASCII token (English / number)
    if all(ord(c) < 128 for c in tok):
        # strip non-alphanumeric
        slug = re.sub(r'[^a-z0-9]+', '_', tok.lower()).strip('_')
        if slug and len(slug) <= 12:
            return slug
        return None

    # Longest-match sliding window: try longest dict keys first
    keys = sorted(TERM_DICT.keys(), key=len, reverse=True)
    matches = []
    pos = 0
    while pos < len(tok):
        found = False
        for k in keys:
            if k and tok.startswith(k, pos):
                matches.append(TERM_DICT[k])
                pos += len(k)
                found = True
                break
        if not found:
            pos += 1
    if matches:
        # dedupe while preserving order
        seen = set()
        out = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                out.append(m)
        return "_".join(out[:2])  # at most 2 sub-tokens

    # Fallback: pypinyin acronym
    try:
        from pypinyin import lazy_pinyin, Style
        parts = lazy_pinyin(tok, style=Style.NORMAL)
        # Take first letter of each syllable for very long tokens
        acronym = "".join(p[0] for p in parts if p)
        if acronym and acronym.isalpha():
            return acronym[:8]
    except Exception:
        pass
    return None


def build_keyword_slug(title, max_chars=18):
    """Pick the best 1-2 English keywords from the title."""
    tokens = tokenize_title(title)

    # Score each token: prefer tech/domain terms (in dict), prefer medium length
    candidates = []  # (score, slug, original_token)
    for tok in tokens:
        if tok in STOPWORDS:
            continue
        if len(tok) <= 1 and not tok.isascii():
            continue
        slug = slugify_token(tok)
        if not slug:
            continue
        # Skip pure numbers
        if slug.isdigit():
            continue
        # Score: dict hit > 5, dict-acquired slug > 3, fallback > 1
        score = 0
        if tok in TERM_DICT or tok.lower() in TERM_DICT:
            score = 10
        elif all(ord(c) < 128 for c in tok):
            score = 5  # english token
        else:
            score = 2  # fallback
        # Prefer slugs length 4-10
        if 4 <= len(slug) <= 10:
            score += 2
        elif len(slug) > 10:
            score -= 1
        candidates.append((score, slug, tok))

    if not candidates:
        return None

    # Take top 3 by score, then re-sort by position
    candidates_by_pos = sorted(enumerate(candidates), key=lambda x: x[0])
    ranked = sorted(
        candidates_by_pos,
        key=lambda x: (-x[1][0], x[0])
    )
    selected = ranked[:2]
    selected.sort(key=lambda x: x[0])
    slug_parts = [s[1][1] for s in selected]

    # Dedupe consecutive duplicates (e.g., protocol_protocol)
    deduped = []
    for s in slug_parts:
        if not deduped or deduped[-1] != s:
            deduped.append(s)
    slug_parts = deduped

    # Try to fit; if too long, drop the lowest-score one (last)
    while slug_parts:
        slug = "_".join(slug_parts)
        if len(slug) <= max_chars:
            return slug
        slug_parts.pop()

    if slug_parts:
        return slug_parts[0][:max_chars]
    return None


def build_filename(cat_code, qnum, slug):
    """Construct filename: <cat>_q<N>_<slug>.md, truncated to <=30 chars.

    Truncation cuts at word boundaries (underscore-separated parts), never mid-word.
    """
    qpart = f"q{qnum}"
    if slug:
        base = f"{cat_code}_{qpart}_{slug}"
    else:
        base = f"{cat_code}_{qpart}"

    max_base = MAX_LEN - len(EXT)
    if len(base) <= max_base:
        return base + EXT

    # Too long: progressively drop slug sub-words (split by _)
    if slug:
        prefix = f"{cat_code}_{qpart}_"
        slug_budget = max_base - len(prefix)
        if slug_budget >= 4:
            parts = slug.split("_")
            kept = []
            for p in parts:
                trial = "_".join(kept + [p]) if kept else p
                if len(trial) <= slug_budget:
                    kept.append(p)
                else:
                    break
            if kept:
                base = f"{prefix}{'_'.join(kept)}"
                return base + EXT
        # Fallback: only the prefix
        return f"{cat_code}_{qpart}{EXT}"
    return base[:max_base].rstrip("_") + EXT


def collect_files():
    """Return list of (category, file_path) tuples to rename."""
    targets = []
    skipped = []
    for cat_dir in sorted(DOCS.iterdir()):
        if not cat_dir.is_dir():
            continue
        cat_name = cat_dir.name
        if cat_name not in CATEGORY_CODES:
            skipped.append(cat_name)
            continue
        cat_code = CATEGORY_CODES[cat_name]
        for fp in sorted(cat_dir.iterdir()):
            if not fp.is_file():
                continue
            if fp.name in PROTECTED_NAMES:
                continue
            if fp.suffix.lower() != ".md":
                continue
            targets.append((cat_name, cat_code, fp))
    return targets, skipped


def ensure_unique(folder: Path, desired: str, used: set):
    """Ensure filename uniqueness within folder. Append _2, _3, ... if needed.

    When a uniqueness suffix is needed, the stem is truncated at word boundaries
    (underscore-separated) so we never cut a word in half.
    """
    name = desired
    stem, ext = os.path.splitext(name)
    counter = 2
    while name in used or (folder / name).exists():
        suffix = f"_{counter}"
        max_stem_len = MAX_LEN - len(ext) - len(suffix)
        # Truncate at word boundary: progressively drop last word
        parts = stem.split("_")
        truncated_stem = stem
        while parts and len("_".join(parts)) + len(suffix) > max_stem_len:
            parts.pop()
            truncated_stem = "_".join(parts)
        if not parts:
            # Even one part doesn't fit; fall back to hash
            import hashlib
            h = hashlib.md5(desired.encode()).hexdigest()[:4]
            truncated_stem = stem[:max_stem_len - 5]
            name = f"{truncated_stem}_{h}{ext}"
            break
        name = f"{truncated_stem}{suffix}{ext}"
        counter += 1
        if counter > 99:
            # Last resort: hash suffix
            import hashlib
            h = hashlib.md5(desired.encode()).hexdigest()[:4]
            name = f"{stem[:max_stem_len - 5]}_{h}{ext}"
            break
    used.add(name)
    return name


def main():
    print("Initializing jieba...")
    # Warm up jieba
    list(jieba.cut("测试"))

    targets, skipped = collect_files()
    print(f"Found {len(targets)} files to rename across {len(set(t[0] for t in targets))} categories")
    if skipped:
        print(f"Skipped categories (no code mapping): {skipped}")

    rename_map = []  # list of dicts {old, new, cat, qnum, title, slug}
    per_cat_stats = defaultdict(lambda: {"total": 0, "renamed": 0, "fallback": 0, "no_slug": 0})
    used_names = defaultdict(set)  # folder -> set of used names

    # Pre-pass: collect all desired names per folder with uniqueness resolution
    for cat_name, cat_code, fp in targets:
        title = extract_title(fp)
        qnum = extract_q_number(fp.name)
        slug = build_keyword_slug(title)
        desired = build_filename(cat_code, qnum, slug)
        unique = ensure_unique(fp.parent, desired, used_names[fp.parent])

        rename_map.append({
            "old_path": str(fp),
            "new_path": str(fp.parent / unique),
            "old_name": fp.name,
            "new_name": unique,
            "category": cat_name,
            "cat_code": cat_code,
            "qnum": qnum,
            "title": title,
            "slug": slug or "",
            "renamed": unique != fp.name,
        })
        stats = per_cat_stats[cat_name]
        stats["total"] += 1
        if not slug:
            stats["no_slug"] += 1

    # Write the plan first (dry-run artifact)
    plan_path = TOOLS / "rename_plan.json"
    plan_path.write_text(
        json.dumps(rename_map, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Plan written: {plan_path}")

    # Show some samples
    print("\n=== Sample mappings ===")
    for r in rename_map[:8]:
        print(f"  [{r['cat_code']} q{r['qnum']}] slug='{r['slug']}' -> {r['new_name']}")
        print(f"      title: {r['title'][:80]}")

    # Stats
    no_slug_count = sum(1 for r in rename_map if not r["slug"])
    too_long = sum(1 for r in rename_map if len(r["new_name"]) > MAX_LEN)
    renamed_count = sum(1 for r in rename_map if r["renamed"])
    print(f"\n=== Stats ===")
    print(f"  Total target files: {len(rename_map)}")
    print(f"  To rename (name differs): {renamed_count}")
    print(f"  No slug extracted: {no_slug_count}")
    print(f"  Names exceeding {MAX_LEN} chars: {too_long}")

    print("\n=== Per-category stats ===")
    for cat, s in sorted(per_cat_stats.items()):
        code = CATEGORY_CODES.get(cat, "?")
        print(f"  {code} | {cat}: total={s['total']}, no_slug={s['no_slug']}")

    # Confirm length constraints
    assert too_long == 0, f"{too_long} names exceed {MAX_LEN} chars"
    # Sanity: all new names unique within their folders
    by_folder = defaultdict(list)
    for r in rename_map:
        by_folder[r["old_path"].rsplit("\\", 1)[0]].append(r["new_name"])
    dups = {f: n for f, n in by_folder.items() if len(n) != len(set(n))}
    assert not dups, f"Duplicate new names in folders: {dups}"

    # === EXECUTE RENAMES ===
    if DRY_RUN:
        print("\n=== DRY RUN: not executing renames ===")
        print(f"Would rename {renamed_count} files. Plan saved at: {plan_path}")
        return
    print(f"\n=== Executing {renamed_count} renames ===")
    success = 0
    errors = []
    for r in rename_map:
        if not r["renamed"]:
            continue
        try:
            old = Path(r["old_path"])
            new = Path(r["new_path"])
            old.rename(new)
            success += 1
        except Exception as e:
            errors.append({"old": r["old_path"], "new": r["new_path"], "error": str(e)})
    print(f"Renamed: {success}/{renamed_count}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors[:5]:
            print(f"  {e}")
        (TOOLS / "rename_errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # Write final map (post-rename: old_name -> new_name within folder)
    (TOOLS / "rename_map.json").write_text(
        json.dumps(rename_map, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Final map written: {TOOLS / 'rename_map.json'}")
    print("DONE")


if __name__ == "__main__":
    main()
