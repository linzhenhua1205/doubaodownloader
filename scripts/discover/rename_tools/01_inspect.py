"""Inspect docs folder: parse frontmatter, check title coverage, sample patterns."""
import os
import re
import json
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DISCOVER_NEWWIKI2_DOCS, DISCOVER_NEWWIKI2_RENAME_TOOLS

DOCS = DISCOVER_NEWWIKI2_DOCS

frontmatter_re = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
title_re = re.compile(r'^title:\s*(.+?)\s*$', re.MULTILINE)
qnum_re = re.compile(r'_Q(\d+)_')

stats = Counter()
samples = []
missing_title = []
no_frontmatter = []
q_distribution = Counter()
category_files = {}

all_md = list(DOCS.rglob("*.md"))
print(f"Total .md files: {len(all_md)}")

for p in all_md:
    rel = p.relative_to(DOCS)
    parts = rel.parts
    if len(parts) == 1:
        # top-level file (README.md)
        stats["top_level"] += 1
        continue
    cat = parts[0]
    fname = parts[-1]
    if fname in ("index.md", "README.md"):
        stats["index_or_readme"] += 1
        continue
    category_files.setdefault(cat, []).append(p)

    try:
        text = p.read_text(encoding="utf-8")
    except Exception as e:
        missing_title.append((str(p), f"read error: {e}"))
        continue
    m = frontmatter_re.match(text)
    if not m:
        no_frontmatter.append(str(p))
        continue
    fm = m.group(1)
    tm = title_re.search(fm)
    if not tm:
        missing_title.append((str(p), "no title field"))
        continue
    title = tm.group(1).strip()
    qm = qnum_re.search(fname)
    qnum = qm.group(1) if qm else "?"
    q_distribution[qnum] += 1
    if len(samples) < 8:
        samples.append({"file": fname, "title": title, "qnum": qnum, "cat": cat})

print(f"\nFiles per category:")
for cat, files in sorted(category_files.items()):
    print(f"  {cat}: {len(files)}")

print(f"\nStats: {dict(stats)}")
print(f"Missing title: {len(missing_title)}")
print(f"No frontmatter: {len(no_frontmatter)}")

print("\nSamples:")
for s in samples:
    print(f"  [{s['cat']}] Q{s['qnum']} | title: {s['title'][:60]}")

# Save samples for design
out = {
    "total": len(all_md),
    "per_category": {c: len(v) for c, v in sorted(category_files.items())},
    "missing_title_count": len(missing_title),
    "no_frontmatter_count": len(no_frontmatter),
    "samples": samples,
    "missing_title_examples": missing_title[:5],
    "no_frontmatter_examples": no_frontmatter[:5],
}
outp = DISCOVER_NEWWIKI2_RENAME_TOOLS / "inspect_report.json"
outp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nReport saved: {outp}")
