import json, os
m = json.load(open(r'd:\123\cowkb\discover\newwiki2\rename_tools\rename_map.json', encoding='utf-8'))
print('Sample entries:')
for r in m[:3]:
    folder = os.path.dirname(r['old_path'])
    print('  folder:', repr(folder))
    print('  old_name:', repr(r['old_name']))
    print('  new_name:', repr(r['new_name']))
    print()

# Read a sample index.md and check what links look like
idx = r'd:\123\cowkb\discover\newwiki2\docs\AI伦理与安全\index.md'
with open(idx, 'r', encoding='utf-8') as f:
    text = f.read()
print('=== AI伦理与安全/index.md (first 800 chars) ===')
print(text[:800])
