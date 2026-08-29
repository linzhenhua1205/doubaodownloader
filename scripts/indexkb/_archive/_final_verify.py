import os
from pathlib import Path

ROOT = Path(r"h:\github\cowkb\knowledge")

EXCLUDE_DIRS = {"01_survey", "bak", "import-modules"}
EXCLUDE_FILES = {"index.md", "log.md", "README.md", "TRACKING.md"}

# 统计
has_graph = []
no_graph = []
no_index = []
total_files = 0

for root, dirs, files in os.walk(ROOT):
    rel = os.path.relpath(root, ROOT).replace("\\", "/")
    
    # 检查是否在排除目录中
    parts = Path(rel).parts
    excluded = False
    for part in parts:
        if part in EXCLUDE_DIRS:
            excluded = True
            break
    if excluded:
        continue
    
    # 统计内容文件数
    md_files = [f for f in files if f.endswith('.md') and f not in EXCLUDE_FILES]
    total_files += len(md_files)
    
    if not md_files:
        continue
    
    if 'index.md' in files:
        idx_path = os.path.join(root, 'index.md')
        with open(idx_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '文件详情与关系图谱' in content:
                has_graph.append((rel, len(md_files)))
            else:
                no_graph.append((rel, len(md_files)))
    else:
        no_index.append((rel, len(md_files)))

print("=" * 60)
print("知识图谱覆盖情况最终验证")
print("=" * 60)
print(f"\n📊 总内容文件数: {total_files}")
print(f"📁 有内容文件的目录数: {len(has_graph) + len(no_graph) + len(no_index)}")
print()
print(f"✅ 已有知识图谱: {len(has_graph)} 个目录")
print(f"❌ 无知识图谱: {len(no_graph)} 个目录")
print(f"📄 无 index.md: {len(no_index)} 个目录")
print()

if no_graph:
    print("❌ 无知识图谱的目录:")
    for d, c in sorted(no_graph):
        print(f"   - {d} ({c} 个文件)")
    print()

if no_index:
    print("📄 无 index.md 的目录:")
    for d, c in sorted(no_index):
        print(f"   - {d} ({c} 个文件)")
    print()

# 覆盖率
total_dirs = len(has_graph) + len(no_graph) + len(no_index)
coverage = len(has_graph) / total_dirs * 100 if total_dirs > 0 else 0
print(f"\n📈 覆盖率: {coverage:.1f}%")

# 验证根目录
root_idx = ROOT / "index.md"
if root_idx.exists():
    content = root_idx.read_text(encoding='utf-8')
    has_overview = '知识图谱总览' in content
    print(f"📊 根目录知识图谱总览: {'✅ 存在' if has_overview else '❌ 缺失'}")
