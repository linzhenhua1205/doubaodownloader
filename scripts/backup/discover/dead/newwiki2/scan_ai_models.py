import os
import re
import json

base_dir = r'h:\github\cowkb\discover\newwiki2\ai-models'
files_data = []

for fname in sorted(os.listdir(base_dir)):
    if not fname.endswith('.md'):
        continue
    fpath = os.path.join(base_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chinese = len(re.findall(r'[\u4e00-\u9fa5]', content))
    english = len(re.findall(r'[a-zA-Z]+', content))
    wc = chinese + english
    
    has_overview = '卡片概述' in content or '卡片定位' in content
    has_deep = '深度解析' in content or '技术详情' in content or '技术详解' in content
    has_latest = '最新进展' in content
    
    if wc > 2000 and has_deep:
        level = 'S级'
    elif wc > 800 and has_overview:
        level = 'A级'
    elif wc > 300 and has_overview:
        level = 'B级'
    elif wc > 100:
        level = 'C级'
    else:
        level = 'D级'
    
    files_data.append({
        'name': fname,
        'words': wc,
        'level': level,
        'has_overview': has_overview,
        'has_deep': has_deep,
        'has_latest': has_latest,
    })

files_data.sort(key=lambda x: x['words'], reverse=True)

print('=== ai-models 目录文件质量统计 ===')
print(f'总文件数: {len(files_data)}')
levels = {}
for f in files_data:
    l = f['level']
    levels[l] = levels.get(l, 0) + 1
for l in ['S级', 'A级', 'B级', 'C级', 'D级']:
    if l in levels:
        print(f'{l}: {levels[l]} 个')

print()
print('=== 文件详细列表（按字数降序） ===')
for i, f in enumerate(files_data, 1):
    name = f['name'].ljust(30)
    words = str(f['words']).rjust(5)
    ov = '✓' if f['has_overview'] else '✗'
    dp = '✓' if f['has_deep'] else '✗'
    lt = '✓' if f['has_latest'] else '✗'
    print(f'{i:2d}. {name} | {words}字 | {f["level"]} | 概:{ov} 深:{dp} 新:{lt}')

with open(r'h:\github\cowkb\discover\newwiki2\ai_models_scan.json', 'w', encoding='utf-8') as f:
    json.dump(files_data, f, ensure_ascii=False, indent=2)
print('\n扫描结果已保存到 ai_models_scan.json')
