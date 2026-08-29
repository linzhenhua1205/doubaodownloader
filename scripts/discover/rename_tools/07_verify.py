"""Verify: check that every link in every index.md points to an existing file.

Also produces a final summary of the rename operation.
"""
import json
import os
import re
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DISCOVER_NEWWIKI2_DOCS, DISCOVER_NEWWIKI2_RENAME_TOOLS

DOCS = DISCOVER_NEWWIKI2_DOCS
TOOLS = DISCOVER_NEWWIKI2_RENAME_TOOLS

MD_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+\.md)(#[^)]*)?\)')


def main():
    # Final state check
    total_md = 0
    chinese_name = 0
    longest_name = 0
    longest_path = 0
    crlf_count = 0

    for fp in DOCS.rglob("*"):
        if not fp.is_file():
            continue
        if fp.suffix.lower() == ".md":
            total_md += 1
        if any('\u4e00' <= c <= '\u9fff' for c in fp.name):
            chinese_name += 1
        if len(fp.name) > longest_name:
            longest_name = len(fp.name)
            longest_name_file = fp.name
        if len(str(fp)) > longest_path:
            longest_path = len(str(fp))
            longest_path_file = fp

        # Check line endings for .md files
        if fp.suffix.lower() == ".md":
            try:
                with open(fp, "rb") as f:
                    data = f.read(8192)
                if b"\r\n" in data:
                    crlf_count += 1
            except Exception:
                pass

    print(f"=== Final State ===")
    print(f"  Total .md files: {total_md}")
    print(f"  Files with Chinese in name: {chinese_name}")
    print(f"  Longest filename: {longest_name} chars ({longest_name_file})")
    print(f"  Longest full path: {longest_path} chars")
    print(f"  Files still using CRLF: {crlf_count}")

    # Validate index.md links
    print(f"\n=== Index link validation ===")
    broken_links = []
    total_links = 0
    for idx in DOCS.rglob("index.md"):
        try:
            text = idx.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in MD_LINK_RE.finditer(text):
            label, target, frag = m.group(1), m.group(2), m.group(3) or ""
            total_links += 1
            # Resolve target relative to idx
            target_path = (idx.parent / target).resolve()
            if not target_path.exists():
                broken_links.append({
                    "index": str(idx.relative_to(DOCS)),
                    "target": target,
                    "label": label[:50],
                })

    print(f"  Total md links in index files: {total_links}")
    print(f"  Broken links: {len(broken_links)}")
    for b in broken_links[:5]:
        print(f"    {b['index']} -> {b['target']}  ({b['label']})")

    # Check rename_map completeness
    map_path = TOOLS / "rename_map.json"
    if map_path.exists():
        m = json.loads(map_path.read_text(encoding="utf-8"))
        # Verify each new_path exists
        missing = 0
        for r in m:
            if not Path(r["new_path"]).exists():
                missing += 1
        print(f"\n=== Rename map verification ===")
        print(f"  Entries: {len(m)}")
        print(f"  Missing new_path files: {missing}")


if __name__ == "__main__":
    main()
