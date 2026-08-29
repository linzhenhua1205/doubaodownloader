import os
from pathlib import Path

ROOT = Path(r'h:\github\cowkb\knowledge')
EXCLUDE_DIRS = {'01_survey', 'bak', 'import-modules'}

dup_count = 0
dup_examples = []
idx_count = 0
total_words = 0
files_with_graph = 0
cache_files = []

for idx_file in ROOT.rglob('index.md'):
    rel = idx_file.relative_to(ROOT)
    parts = rel.parts
    if any(p in EXCLUDE_DIRS for p in parts):
        continue
    idx_count += 1
    content = idx_file.read_text(encoding='utf-8')
    if '---\n---' in content:
        dup_count += 1
        if len(dup_examples) < 3:
            dup_examples.append(str(rel))
    if '文件详情与关系图谱' in content:
        files_with_graph += 1

# 检查缓存文件
cache_path = ROOT / '_kg_cache.json'
if cache_path.exists():
    cache_files.append('_kg_cache.json')

# 统计内容文件总字数
for md_file in ROOT.rglob('*.md'):
    parts = md_file.relative_to(ROOT).parts
    if any(p in EXCLUDE_DIRS for p in parts):
        continue
    if md_file.name in {'index.md', 'log.md', 'README.md', 'TRACKING.md'}:
        continue
    try:
        text = md_file.read_text(encoding='utf-8')
        import re
        cn = len(re.findall(r'[\u4e00-\u9fa5]', text))
        en = len(re.findall(r'[A-Za-z]+', text))
        total_words += cn + en
    except:
        pass

print(f'index.md 总数: {idx_count}')
print(f'有知识图谱的 index.md: {files_with_graph}')
print(f'重复 --- 的 index.md: {dup_count}')
if dup_examples:
    print('重复示例:')
    for e in dup_examples:
        print(f'  - {e}')
print(f'残留缓存文件: {cache_files if cache_files else "无"}')
print(f'内容文件总字数: {total_words/10000:.1f} 万字')
