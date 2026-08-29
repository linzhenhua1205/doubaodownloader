"""Rename leftover long-path / problematic files using \\?\ long path prefix.

These files were skipped by the main rename pass due to:
- Exceeding MAX_PATH (260 chars total path)
- Containing characters that confuse Python's Path.iterdir()

Strategy: use raw os.listdir + os.rename with \\?\ prefix to bypass Windows
path-length limits.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    DISCOVER_NEWWIKI2_DOCS, DISCOVER_NEWWIKI2_RENAME_TOOLS,
    CATEGORY_CODES, STOPWORDS, TERM_DICT,
    MAX_SHORT_FILENAME_LEN, FILENAME_EXT
)

import jieba

DOCS = DISCOVER_NEWWIKI2_DOCS
TOOLS = DISCOVER_NEWWIKI2_RENAME_TOOLS

MAX_LEN = MAX_SHORT_FILENAME_LEN
EXT = FILENAME_EXT

PROTECTED = {"index.md", "README.md", "findings.md", "progress.md",
             "task_plan.md", "error_log.json", "generation_progress.json"}

QNUM_RE = re.compile(r'_Q(\d+)_')


def long_path(p):
    """Convert to Windows long-path UNC form."""
    abs_p = os.path.abspath(p)
    if abs_p.startswith("\\\\?\\"):
        return abs_p
    return "\\\\?\\" + abs_p


def list_dir_long(path):
    """List directory using long-path prefix."""
    return os.listdir(long_path(path))


def read_text_long(path):
    """Read file content using long path."""
    with open(long_path(path), "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def rename_long(src, dst):
    """Rename using long-path prefix for both src and dst."""
    src_lp = long_path(src)
    dst_lp = long_path(dst)
    os.rename(src_lp, dst_lp)


def extract_title(text, fallback_stem):
    """Parse title from frontmatter or H1."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if m:
        tm = re.search(r'^title:\s*(.+?)\s*$', m.group(1), re.MULTILINE)
        if tm:
            return tm.group(1).strip().strip('"').strip("'")
    h1 = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if h1:
        return h1.group(1).strip()
    return fallback_stem


def tokenize(title):
    cleaned = re.sub(
        r'[，。？！、；：\u201c\u201d\u2018\u2019《》（）【】「」()\[\]{},.!?:;\'"\\/]',
        ' ', title)
    tokens = []
    for raw in jieba.cut(cleaned, HMM=True):
        t = raw.strip()
        if t:
            tokens.append(t)
    return tokens


def slugify_token(tok):
    if not tok:
        return None
    if tok in TERM_DICT:
        return TERM_DICT[tok]
    low = tok.lower()
    if low in TERM_DICT:
        return TERM_DICT[low]
    if all(ord(c) < 128 for c in tok):
        slug = re.sub(r'[^a-z0-9]+', '_', low).strip('_')
        if slug and len(slug) <= 12:
            return slug
        return None
    # sliding window longest match
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
        seen = set()
        out = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                out.append(m)
        return "_".join(out[:2])
    try:
        from pypinyin import lazy_pinyin, Style
        parts = lazy_pinyin(tok, style=Style.NORMAL)
        acr = "".join(p[0] for p in parts if p)
        if acr and acr.isalpha():
            return acr[:8]
    except Exception:
        pass
    return None


def build_slug(title, max_chars=18):
    tokens = tokenize(title)
    candidates = []
    for tok in tokens:
        if tok in STOPWORDS:
            continue
        if len(tok) <= 1 and not tok.isascii():
            continue
        slug = slugify_token(tok)
        if not slug or slug.isdigit():
            continue
        score = 0
        if tok in TERM_DICT or tok.lower() in TERM_DICT:
            score = 10
        elif all(ord(c) < 128 for c in tok):
            score = 5
        else:
            score = 2
        if 4 <= len(slug) <= 10:
            score += 2
        elif len(slug) > 10:
            score -= 1
        candidates.append((score, slug, tok))
    if not candidates:
        return None
    candidates_by_pos = sorted(enumerate(candidates), key=lambda x: x[0])
    ranked = sorted(candidates_by_pos, key=lambda x: (-x[1][0], x[0]))
    selected = ranked[:2]
    selected.sort(key=lambda x: x[0])
    slug_parts = [s[1][1] for s in selected]
    deduped = []
    for s in slug_parts:
        if not deduped or deduped[-1] != s:
            deduped.append(s)
    slug_parts = deduped
    while slug_parts:
        slug = "_".join(slug_parts)
        if len(slug) <= max_chars:
            return slug
        slug_parts.pop()
    if slug_parts:
        return slug_parts[0][:max_chars]
    return None


def build_filename(cat_code, qnum, slug):
    qpart = f"q{qnum}"
    if slug:
        base = f"{cat_code}_{qpart}_{slug}"
    else:
        base = f"{cat_code}_{qpart}"
    max_base = MAX_LEN - len(EXT)
    if len(base) <= max_base:
        return base + EXT
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
                return f"{prefix}{'_'.join(kept)}{EXT}"
        return f"{cat_code}_{qpart}{EXT}"
    return base[:max_base].rstrip("_") + EXT


def ensure_unique_in(folder_path, desired, used_set):
    """folder_path is a normal Path (folder); used_set has filenames in that folder."""
    name = desired
    stem, ext = os.path.splitext(name)
    counter = 2
    while name in used_set or os.path.exists(long_path(folder_path / name)):
        suffix = f"_{counter}"
        max_stem_len = MAX_LEN - len(ext) - len(suffix)
        parts = stem.split("_")
        truncated = stem
        while parts and len("_".join(parts)) + len(suffix) > max_stem_len:
            parts.pop()
            truncated = "_".join(parts)
        if not parts:
            import hashlib
            h = hashlib.md5(desired.encode()).hexdigest()[:4]
            truncated = stem[:max_stem_len - 5]
            name = f"{truncated}_{h}{ext}"
            break
        name = f"{truncated}{suffix}{ext}"
        counter += 1
        if counter > 99:
            import hashlib
            h = hashlib.md5(desired.encode()).hexdigest()[:4]
            name = f"{stem[:max_stem_len - 5]}_{h}{ext}"
            break
    used_set.add(name)
    return name


def main():
    print("Warming up jieba...")
    list(jieba.cut("test"))

    # Load previous rename map to know what's already used per folder
    prev_map_path = TOOLS / "rename_map.json"
    if prev_map_path.exists():
        prev = json.loads(prev_map_path.read_text(encoding="utf-8"))
        # Build per-folder used-name set
        used = {}
        for r in prev:
            folder = r["new_path"].rsplit("\\", 1)[0]
            used.setdefault(folder, set()).add(r["new_name"])
    else:
        used = {}

    rename_map_append = []
    targets = []

    # Walk docs using long-path listdir to find any non-renamed files
    for cat_dir in DOCS.iterdir():
        if not cat_dir.is_dir():
            continue
        cat_name = cat_dir.name
        if cat_name not in CATEGORY_CODES:
            continue
        cat_code = CATEGORY_CODES[cat_name]
        # Use long-path listdir
        try:
            entries = list_dir_long(cat_dir)
        except Exception as e:
            print(f"  ERROR listing {cat_dir}: {e}")
            continue
        for entry in entries:
            if not entry.lower().endswith(".md"):
                continue
            if entry in PROTECTED:
                continue
            # Check if entry has any CJK chars (needs rename)
            if not any('\u4e00' <= c <= '\u9fff' for c in entry):
                continue
            fp = cat_dir / entry
            targets.append((cat_name, cat_code, fp, entry))

    print(f"Found {len(targets)} leftover long-path files to rename")
    if not targets:
        print("Nothing to do.")
        return

    # Process each
    for cat_name, cat_code, fp, fname in targets:
        try:
            text = read_text_long(fp)
        except Exception as e:
            print(f"  READ FAIL: {fp} - {e}")
            continue
        title = extract_title(text, fp.stem)
        qnum_match = QNUM_RE.search(fname)
        qnum = qnum_match.group(1) if qnum_match else "0"
        slug = build_slug(title)
        desired = build_filename(cat_code, qnum, slug)

        folder_key = str(fp.parent)
        used_set = used.setdefault(folder_key, set())
        new_name = ensure_unique_in(fp.parent, desired, used_set)
        new_path = fp.parent / new_name

        try:
            rename_long(fp, new_path)
            print(f"  OK: {new_name}  (slug='{slug}', title='{title[:60]}')")
            rename_map_append.append({
                "old_path": str(fp),
                "new_path": str(new_path),
                "old_name": fname,
                "new_name": new_name,
                "category": cat_name,
                "cat_code": cat_code,
                "qnum": qnum,
                "title": title,
                "slug": slug or "",
                "renamed": True,
            })
        except Exception as e:
            print(f"  RENAME FAIL: {fp.name} -> {new_name}: {e}")

    # Append to existing rename_map.json
    if prev_map_path.exists() and rename_map_append:
        prev = json.loads(prev_map_path.read_text(encoding="utf-8"))
        prev.extend(rename_map_append)
        prev_map_path.write_text(
            json.dumps(prev, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"\nAppended {len(rename_map_append)} entries to {prev_map_path}")
    elif rename_map_append:
        prev_map_path.write_text(
            json.dumps(rename_map_append, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    print("DONE")


if __name__ == "__main__":
    main()
