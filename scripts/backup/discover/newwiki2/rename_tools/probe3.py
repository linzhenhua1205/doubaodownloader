import json, os, re
from pathlib import Path

m = json.load(open(r'd:\123\cowkb\discover\newwiki2\rename_tools\rename_map.json', encoding='utf-8'))

# Build lookup
lookup = {}
for r in m:
    folder = os.path.dirname(r['old_path'])
    lookup[(folder, r['old_name'])] = r['new_name']

# Test the index file
idx = Path(r'd:\123\cowkb\discover\newwiki2\docs\AI伦理与安全\index.md')
text = idx.read_text(encoding='utf-8', errors='replace')

MD_LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+\.md)\)')
matches = MD_LINK_RE.findall(text)
print(f'Found {len(matches)} md links')
for label, target in matches[:3]:
    print(f'  label: {label[:50]!r}')
    print(f'  target: {target!r}')
    target_full = (idx.parent / target).resolve()
    key = (str(target_full.parent), target_full.name)
    print(f'  key folder: {key[0]!r}')
    print(f'  key name: {key[1]!r}')
    print(f'  in lookup: {key in lookup}')
    if key not in lookup:
        # Try to find similar entries
        for (f, n), v in lookup.items():
            if n.startswith('AI伦理与安全_Q1'):
                print(f'    lookup entry: folder={f!r}, name={n!r}')
                break
    print()
