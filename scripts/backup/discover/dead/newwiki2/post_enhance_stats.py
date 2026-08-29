import os
import re
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

target_dirs = [
    'programming',
    '编程语言',
    '软件架构',
    'project-mgmt',
    'security',
    '算法优化',
    '研究与论文',
    'research',
    'papers-research',
]

def count_words(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'---.*?---', '', text, flags=re.DOTALL)
    text = re.sub(r'[#*>\-\|\[\]()`]', '', text)
    text = re.sub(r'\s+', '', text)
    return len(text)

def get_frontmatter(text):
    match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).strip().split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm

all_files = []
total_words = 0

for dirname in target_dirs:
    dir_path = BASE_DIR / dirname
    if not dir_path.exists():
        continue
    for f in sorted(dir_path.glob('*.md')):
        if f.name == 'index.md':
            continue
        content = f.read_text(encoding='utf-8')
        fm = get_frontmatter(content)
        wc = count_words(content)
        total_words += wc
        all_files.append({
            'dir': dirname,
            'name': f.name,
            'path': str(f.relative_to(BASE_DIR)),
            'word_count': wc,
            'quality_level': fm.get('quality_level', '未知'),
            'status': fm.get('status', ''),
        })

s_files = sorted([f for f in all_files if f['quality_level'] == 'S' or f['quality_level'] == 'S级'], key=lambda x: -x['word_count'])
a_files = sorted([f for f in all_files if f['quality_level'] == 'A' or f['quality_level'] == 'A级'], key=lambda x: -x['word_count'])
b_files = sorted([f for f in all_files if f['quality_level'] == 'B' or f['quality_level'] == 'B级'], key=lambda x: -x['word_count'])
c_files = sorted([f for f in all_files if f['quality_level'] == 'C' or f['quality_level'] == 'C级'], key=lambda x: -x['word_count'])

print("=" * 70)
print("7大开发与管理目录 - 质量等级分布统计")
print("=" * 70)
print()
print(f"总文件数: {len(all_files)}")
print(f"总字数: {total_words:,} 字")
print()
print(f"S级: {len(s_files)} 个文件")
print(f"A级: {len(a_files)} 个文件")
print(f"B级: {len(b_files)} 个文件")
print(f"C级: {len(c_files)} 个文件")
print()

print("-" * 70)
print("【S级文件列表】(按字数降序)")
print("-" * 70)
for i, f in enumerate(s_files[:20], 1):
    print(f"{i:2d}. {f['path']:50s} {f['word_count']:>6,}字  {f['status']}")

print()
print("-" * 70)
print("【各目录统计】")
print("-" * 70)
dir_stats = {}
for f in all_files:
    d = f['dir']
    if d not in dir_stats:
        dir_stats[d] = {'count': 0, 'words': 0, 'S': 0, 'A': 0, 'B': 0, 'C': 0}
    dir_stats[d]['count'] += 1
    dir_stats[d]['words'] += f['word_count']
    q = f['quality_level']
    if q in ('S', 'S级'):
        dir_stats[d]['S'] += 1
    elif q in ('A', 'A级'):
        dir_stats[d]['A'] += 1
    elif q in ('B', 'B级'):
        dir_stats[d]['B'] += 1
    elif q in ('C', 'C级'):
        dir_stats[d]['C'] += 1

for d, s in sorted(dir_stats.items()):
    print(f"  {d:15s}: {s['count']:3d}个文件, {s['words']:>7,}字  (S:{s['S']:2d} A:{s['A']:2d} B:{s['B']:2d} C:{s['C']:2d})")
