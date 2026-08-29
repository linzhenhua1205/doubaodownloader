import os
p = r'\\?\D:\123\cowkb\discover\newwiki2\docs\其他_后端开发_backup'
entries = os.listdir(p)
chinese = [e for e in entries if any('\u4e00' <= c <= '\u9fff' for c in e)]
for e in chinese:
    print(f'len={len(e)}')
    print(f'last 30: {repr(e[-30:])}')
    print(f'first 60: {repr(e[:60])}')
    print(f'lower endswith .md: {e.lower().endswith(".md")}')
    print()

p2 = r'\\?\D:\123\cowkb\discover\newwiki2\docs\AI-Agent技术架构'
entries2 = os.listdir(p2)
chinese2 = [e for e in entries2 if any('\u4e00' <= c <= '\u9fff' for c in e)]
print('=== aag ===')
for e in chinese2:
    print(f'len={len(e)}')
    print(f'last 30: {repr(e[-30:])}')
    print(f'lower endswith .md: {e.lower().endswith(".md")}')
    print(f'lower endswith md: {e.lower().endswith("md")}')
    print()
