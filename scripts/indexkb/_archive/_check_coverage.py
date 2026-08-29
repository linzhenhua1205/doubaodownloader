import os
import json

base = r'h:\github\cowkb\knowledge'

# 读取分析结果
with open(os.path.join(base, '_knowledge_graph_results.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# 统计分析过的目录
analyzed_dirs = set()
for path, info in data['files'].items():
    d = os.path.dirname(path)
    analyzed_dirs.add(d)

print(f'=== 分析结果统计 ===')
print(f'分析文件数: {data["total_files"]}')
print(f'涉及目录数: {data["total_dirs"]}')
print(f'有反向引用的文件数: {data["total_backlinks"]}')
print(f'相似内容对: {data["total_similar_pairs"]}')
print(f'高度重复对: {data["duplicate_pairs"]}')
print(f'互补/相关对: {data["complementary_pairs"]}')
print()

# 统计有多少 index.md 已经有知识图谱
has_graph = []
no_graph = []
no_index = []

for root, dirs, files in os.walk(base):
    rel = os.path.relpath(root, base)
    rel = rel.replace('\\', '/')
    if rel.startswith('01_survey') or rel.startswith('bak') or rel.startswith('import-modules') or rel == '.':
        continue
    
    # 只统计有实际内容文件的目录
    has_md = any(f.endswith('.md') and f not in ('index.md', 'log.md') for f in files)
    if not has_md:
        continue
    
    if 'index.md' in files:
        idx_path = os.path.join(root, 'index.md')
        with open(idx_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '文件详情与关系图谱' in content:
                has_graph.append(rel)
            else:
                no_graph.append(rel)
    else:
        no_index.append(rel)

print(f'=== index.md 知识图谱覆盖情况 ===')
print(f'已有知识图谱: {len(has_graph)} 个目录')
print(f'无知识图谱: {len(no_graph)} 个目录')
print(f'无 index.md: {len(no_index)} 个目录')
print()

if no_graph:
    print('无知识图谱的目录:')
    for d in sorted(no_graph):
        # 统计该目录下的md文件数
        d_path = os.path.join(base, d)
        md_count = len([f for f in os.listdir(d_path) if f.endswith('.md') and f not in ('index.md', 'log.md')])
        print(f'  - {d} ({md_count} 个文件)')
    print()

if no_index:
    print(f'无 index.md 的目录 ({len(no_index)} 个):')
    for d in sorted(no_index):
        print(f'  - {d}')
