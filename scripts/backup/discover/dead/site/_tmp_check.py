import json
from pathlib import Path
from collections import defaultdict

results = json.loads(Path(r'h:\github\cowkb\discover\site\quality_scan_results.json').read_text(encoding='utf-8'))

depth_articles = [a for a in results['articles'] if a['article_type'] == 'depth_report']
print(f'深度报告文章总数: {len(depth_articles)}')
print()

by_cat = defaultdict(list)
for a in depth_articles:
    by_cat[a['category']].append(a)

for cat, arts in sorted(by_cat.items()):
    print(f'【{cat}】({len(arts)}篇)')
    for a in sorted(arts, key=lambda x: -x['content_len'])[:3]:
        title = a['title'][:50]
        print(f'  - {title} ({a["content_len"]}字, {a["quality"]}级)')
    print()

# 找出 B 级的深度文章
print('=' * 60)
print('需要重点增强的 B 级深度文章:')
b_depth = [a for a in depth_articles if a['quality'] == 'B']
print(f'共 {len(b_depth)} 篇')
print()
for a in b_depth[:20]:
    title = a['title'][:60]
    print(f'  [{a["category"]}] {title} ({a["content_len"]}字)')
