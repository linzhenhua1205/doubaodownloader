"""Fix 3 edge-case files that the main rename scripts missed:

1. Two aag files with malformed extension '.。md' (Chinese full-stop + 'md').
   The file content is markdown but the extension is malformed.

2. One obd "file" that's actually a directory (original filename had a backslash
   that Windows interpreted as a path separator). The real .md file is nested inside.

Each gets a proper English filename following the same naming convention.
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

TOOLS = DISCOVER_NEWWIKI2_RENAME_TOOLS
DOCS = DISCOVER_NEWWIKI2_DOCS
MAX_LEN = MAX_SHORT_FILENAME_LEN
EXT = FILENAME_EXT


def long_path(p):
    abs_p = os.path.abspath(str(p))
    if abs_p.startswith("\\\\?\\"):
        return abs_p
    return "\\\\?\\" + abs_p


def read_text_long(p):
    with open(long_path(p), "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def extract_title(text, fallback_stem):
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
    return [t.strip() for t in jieba.cut(cleaned, HMM=True) if t.strip()]


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


def rename_via_long(src, dst):
    """Rename src -> dst using long-path prefix. src/dst can be Path or str."""
    src_lp = long_path(src)
    dst_lp = long_path(dst)
    os.rename(src_lp, dst_lp)


def load_used_names():
    """Load per-folder used filenames from existing rename_map.json."""
    used = {}
    map_path = TOOLS / "rename_map.json"
    if map_path.exists():
        prev = json.loads(map_path.read_text(encoding="utf-8"))
        for r in prev:
            folder = os.path.dirname(r["new_path"])
            used.setdefault(folder, set()).add(r["new_name"])
    return used


def main():
    print("Warming up jieba...")
    list(jieba.cut("test"))
    used = load_used_names()
    new_entries = []

    # === Case 1: aag files with malformed extension '.。md' ===
    aag_dir = DOCS / "AI-Agent技术架构"
    aag_entries = os.listdir(long_path(aag_dir))
    aag_bad = [
        e for e in aag_entries
        if e.endswith("。md") and any('\u4e00' <= c <= '\u9fff' for c in e)
    ]
    print(f"\n[1] Found {len(aag_bad)} aag files with malformed extension '.。md'")
    for fname in aag_bad:
        src = aag_dir / fname
        try:
            text = read_text_long(src)
        except Exception as e:
            print(f"  READ FAIL: {fname[:50]}... : {e}")
            continue
        title = extract_title(text, fname)
        m = re.search(r'_Q(\d+)_', fname)
        qnum = m.group(1) if m else "0"
        slug = build_slug(title)
        desired = build_filename("aag", qnum, slug)
        used_set = used.setdefault(str(aag_dir), set())
        new_name = ensure_unique_in(aag_dir, desired, used_set)
        new_path = aag_dir / new_name
        try:
            rename_via_long(src, new_path)
            print(f"  OK: {new_name}  (slug='{slug}', title='{title[:60]}')")
            new_entries.append({
                "old_path": str(src), "new_path": str(new_path),
                "old_name": fname, "new_name": new_name,
                "category": "AI-Agent技术架构", "cat_code": "aag",
                "qnum": qnum, "title": title, "slug": slug or "",
                "renamed": True,
                "note": "malformed extension '.。md' fixed",
            })
        except Exception as e:
            print(f"  RENAME FAIL: {fname[:50]}... : {e}")

    # === Case 2: obd file inside an accidentally-created directory ===
    # The original filename had a backslash, which Windows interpreted as a path
    # separator, creating a directory + nested file. We need to:
    #   a) Move the nested .md file to the obd folder with a new English name
    #   b) Remove the now-empty directory
    obd_dir = DOCS / "其他_后端开发_backup"
    obd_entries = os.listdir(long_path(obd_dir))
    # Find directories that look like the Drive OS issue (have Chinese chars
    # and contain a .md file inside)
    obd_subdirs = []
    for entry in obd_entries:
        if not any('\u4e00' <= c <= '\u9fff' for c in entry):
            continue
        full = obd_dir / entry
        if os.path.isdir(long_path(full)):
            obd_subdirs.append(full)

    print(f"\n[2] Found {len(obd_subdirs)} obd 'directory' entries (likely backslash artifacts)")
    for subdir in obd_subdirs:
        try:
            inner_files = os.listdir(long_path(subdir))
        except Exception as e:
            print(f"  LIST FAIL: {subdir.name[:50]}... : {e}")
            continue
        md_files = [f for f in inner_files if f.lower().endswith(".md")]
        if not md_files:
            print(f"  No .md files inside {subdir.name[:50]}..., skipping")
            continue
        for inner_fname in md_files:
            inner_src = subdir / inner_fname
            try:
                text = read_text_long(inner_src)
            except Exception as e:
                print(f"  READ FAIL: {inner_fname}: {e}")
                continue
            title = extract_title(text, inner_fname)
            # Q number from the parent directory name (it was the original filename)
            m = re.search(r'_Q(\d+)_', subdir.name)
            qnum = m.group(1) if m else "0"
            slug = build_slug(title)
            desired = build_filename("obd", qnum, slug)
            used_set = used.setdefault(str(obd_dir), set())
            new_name = ensure_unique_in(obd_dir, desired, used_set)
            new_path = obd_dir / new_name
            try:
                # Move file out of subdir to obd_dir with new name
                rename_via_long(inner_src, new_path)
                print(f"  OK: {new_name}  (slug='{slug}', title='{title[:60]}')")
                new_entries.append({
                    "old_path": str(inner_src),
                    "new_path": str(new_path),
                    "old_name": f"{subdir.name}/{inner_fname}",
                    "new_name": new_name,
                    "category": "其他_后端开发_backup", "cat_code": "obd",
                    "qnum": qnum, "title": title, "slug": slug or "",
                    "renamed": True,
                    "note": "extracted from accidental subdir (backslash in name)",
                })
            except Exception as e:
                print(f"  MOVE FAIL: {inner_fname} -> {new_name}: {e}")
                continue
            # Try to remove the now-empty subdir
            try:
                os.rmdir(long_path(subdir))
                print(f"  Removed empty subdir: {subdir.name[:50]}...")
            except Exception as e:
                print(f"  WARN: could not remove subdir: {e}")

    # === Append to rename_map.json ===
    if new_entries:
        map_path = TOOLS / "rename_map.json"
        prev = json.loads(map_path.read_text(encoding="utf-8")) if map_path.exists() else []
        prev.extend(new_entries)
        map_path.write_text(
            json.dumps(prev, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"\nAppended {len(new_entries)} entries to {map_path}")
    print(f"\nTotal edge cases processed: {len(new_entries)}")
    print("DONE")


if __name__ == "__main__":
    main()
