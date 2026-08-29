# -*- coding: utf-8 -*-
import json

with open(r'h:\github\cowkb\discover\newwiki2\quality_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

general_b = [f for f in report['files'] if f['parent'] == 'general' and f.get('grade') == 'B']
print(f'general/ B级文件数: {len(general_b)}')
print()
for f in sorted(general_b, key=lambda x: x['word_count'], reverse=True):
    title = f.get('h1', '无标题')
    if len(title) > 35:
        title = title[:35] + '...'
    print(f"  {f['name']:40s} {f['word_count']:>5d}字  {title}")
