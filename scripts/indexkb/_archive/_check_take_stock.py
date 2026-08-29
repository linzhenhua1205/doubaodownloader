import json
from pathlib import Path

ROOT = Path(r"h:\github\cowkb\knowledge")

with open(ROOT / "_knowledge_graph_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

files = data["files"]

# 检查 take_stock 目录
take_stock_files = [p for p in files.keys() if '20260720_take_stock' in p]
print(f"take_stock 相关文件: {len(take_stock_files)} 个")
for f in sorted(take_stock_files):
    print(f"  - {f}")

print()

# 检查 topics 子目录
topics_files = [p for p in files.keys() if 'take_stock/topics' in p]
print(f"topics 子目录文件: {len(topics_files)} 个")
for f in sorted(topics_files):
    print(f"  - {f}")
