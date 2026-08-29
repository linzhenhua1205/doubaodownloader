import os
from pathlib import Path

base = Path(r'h:\github\cowkb\discover\newwiki2\docs')
exclude_names = {'index.md', 'progress.md', 'task_plan.md', 'findings.md'}

dirs = ['AI-Agent技术架构', 'AI伦理与安全', 'AI应用与落地实践']
total_valid = 0
for d in dirs:
    dpath = base / d
    if not dpath.exists():
        print(f'{d}: 目录不存在')
        continue
    all_files = list(dpath.rglob('*.md'))
    filtered = []
    for f in all_files:
        if f.name in exclude_names:
            continue
        if f.name.startswith('_'):
            continue
        if 'JSON' in str(f):
            continue
        filtered.append(f)
    total_valid += len(filtered)
    
    sizes = [(f, os.path.getsize(f)) for f in filtered]
    sizes.sort(key=lambda x: x[1])
    
    lines_dist = {'<20': 0, '20-100': 0, '>100': 0}
    for f, s in sizes:
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                lc = len(fp.readlines())
            if lc < 20:
                lines_dist['<20'] += 1
            elif lc <= 100:
                lines_dist['20-100'] += 1
            else:
                lines_dist['>100'] += 1
        except:
            pass
    
    print(f'\n{d}:')
    print(f'  总md文件: {len(all_files)}')
    print(f'  有效文件: {len(filtered)}')
    print(f'  行数分布: {lines_dist}')
    if sizes:
        print(f'  最小3个: {[(f.name, s, sum(1 for _ in open(f, encoding="utf-8", errors="ignore"))) for f,s in sizes[:3]]}')
        print(f'  最大3个: {[(f.name, s, sum(1 for _ in open(f, encoding="utf-8", errors="ignore"))) for f,s in sizes[-3:]]}')

print(f'\n\n总计有效文件: {total_valid}')
