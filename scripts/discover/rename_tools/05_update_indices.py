"""Update markdown link references in index.md and README.md files.

For each index.md under docs/<category>/, find markdown links of the form
[label](old_filename.md) and rewrite them to use the new English filename.

Also handles cross-references between content files (one .md linking to another
.md in the same folder).
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DISCOVER_NEWWIKI2_DOCS, DISCOVER_NEWWIKI2_RENAME_TOOLS

TOOLS = DISCOVER_NEWWIKI2_RENAME_TOOLS
DOCS = DISCOVER_NEWWIKI2_DOCS


def long_path(p):
    abs_p = os.path.abspath(str(p))
    if abs_p.startswith("\\\\?\\"):
        return abs_p
    return "\\\\?\\" + abs_p


def load_rename_map():
    """Build (folder_path, old_basename) -> new_basename lookup.

    Path keys are case-normalized (Windows is case-insensitive but Python dict
    lookup is not).
    """
    map_path = TOOLS / "rename_map.json"
    if not map_path.exists():
        print("rename_map.json not found")
        return {}
    data = json.loads(map_path.read_text(encoding="utf-8"))
    lookup = {}
    for r in data:
        folder = os.path.dirname(r["old_path"])
        # os.path.normcase lowercases paths on Windows
        key = (os.path.normcase(folder), r["old_name"])
        lookup[key] = r["new_name"]
    return lookup


MD_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+\.md)\)')


def rewrite_links(text, folder_path, lookup):
    """Rewrite markdown links in text. folder_path is the folder containing the file."""
    changes = 0

    def repl(m):
        nonlocal changes
        label, target = m.group(1), m.group(2)
        # Strip any URL fragment (e.g., 'file.md#section')
        if '#' in target:
            target_path, frag = target.split('#', 1)
            frag = '#' + frag
        else:
            target_path, frag = target, ''
        # target_path may be relative like 'foo.md' or 'sub/foo.md'
        # Resolve relative to folder_path
        target_full = (Path(folder_path) / target_path).resolve()
        target_folder = os.path.normcase(str(target_full.parent))
        target_name = target_full.name
        key = (target_folder, target_name)
        if key in lookup:
            new_name = lookup[key]
            # Keep the same relative path structure
            new_target = target_path.replace(target_name, new_name) + frag
            changes += 1
            return f'[{label}]({new_target})'
        return m.group(0)

    new_text = MD_LINK_RE.sub(repl, text)
    return new_text, changes


def main():
    lookup = load_rename_map()
    print(f"Loaded {len(lookup)} rename entries")

    total_files = 0
    total_changes = 0
    files_changed = 0

    # Walk every .md file under docs (including index.md and README.md)
    for fp in DOCS.rglob("*.md"):
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            # Try long-path
            try:
                with open(long_path(fp), "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except Exception as e2:
                print(f"  SKIP (read err): {fp} : {e2}")
                continue
        new_text, changes = rewrite_links(text, str(fp.parent), lookup)
        total_files += 1
        if changes > 0:
            files_changed += 1
            total_changes += changes
            try:
                fp.write_text(new_text, encoding="utf-8", newline="")  # preserve existing
            except Exception:
                with open(long_path(fp), "w", encoding="utf-8", newline="") as f:
                    f.write(new_text)
            print(f"  {fp.relative_to(DOCS)}: {changes} link(s) updated")

    print(f"\n=== Summary ===")
    print(f"  Scanned: {total_files} .md files")
    print(f"  Modified: {files_changed}")
    print(f"  Total link updates: {total_changes}")

    # Also: rebuild each index.md's table from scratch using new filenames
    # so that any newly-discovered files or stale references are reconciled.
    # For now we just trust the link rewrite above. If user wants a full
    # rebuild, that's a separate step.
    print("DONE")


if __name__ == "__main__":
    main()
