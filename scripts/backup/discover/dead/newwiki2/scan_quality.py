import os
import re
import json

BASE_DIR = r'h:\github\cowkb\discover\newwiki2\ai-models'
files = [f for f in os.listdir(BASE_DIR) if f.endswith('.md') and f != 'index.md']

stats = {
    'total': len(files),
    'S级': 0,
    'A级': 0,
    'B级': 0,
    'C级': 0,
    'D级': 0,
    'files': []
}

for f in files:
    filepath = os.path.join(BASE_DIR, f)
    with open(filepath, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    word_count = len(content)
    
    quality = 'D级'
    if 'quality_level: S级' in content or word_count > 3000:
        quality = 'S级'
    elif 'quality_level: A级' in content or word_count > 1500:
        quality = 'A级'
    elif 'quality_level: B级' in content or word_count > 500:
        quality = 'B级'
    elif 'quality_level: C级' in content or word_count > 200:
        quality = 'C级'
    
    stats[quality] += 1
    stats['files'].append({
        'file': f,
        'quality': quality,
        'word_count': word_count
    })

print(f'总文件数: {stats["total"]}')
print(f'S级: {stats["S级"]}')
print(f'A级: {stats["A级"]}')
print(f'B级: {stats["B级"]}')
print(f'C级: {stats["C级"]}')
print(f'D级: {stats["D级"]}')
print()
print('C级及以下文件:')
for f in sorted(stats['files'], key=lambda x: x['word_count']):
    if f['quality'] in ['C级', 'D级']:
        print(f'  {f["file"]} ({f["word_count"]}字, {f["quality"]})')
