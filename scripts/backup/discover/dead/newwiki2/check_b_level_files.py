# -*- coding: utf-8 -*-
"""
检查 B 级文件的具体情况，找出可以提升到 A 级的文件
"""
import os
import re
import json
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

with open(BASE_DIR / 'ai_remaining_detailed_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

b_level_files = [f for f in data['all_files'] if f['real_quality'] == 'B级']

print("=" * 80)
print(f"B 级文件清单（共 {len(b_level_files)} 个）")
print("=" * 80)

by_dir = {}
for f in b_level_files:
    d = f['directory']
    if d not in by_dir:
        by_dir[d] = []
    by_dir[d].append(f)

for dir_name, files in by_dir.items():
    print(f"\n【{dir_name}】 ({len(files)} 个)")
    for f in sorted(files, key=lambda x: x['cn_chars'], reverse=True):
        print(f"  {f['filename']:35s} {f['cn_chars']:5d}字  {f['tables']}表  自评:{f['fm_quality']:4s} 状态:{f.get('fm_status', '')[:20]}")

print(f"\n{'='*80}")
print("B 级文件字数分布:")
print(f"{'='*80}")

word_ranges = [
    ('1500+ 字', lambda x: x >= 1500),
    ('1000-1500 字', lambda x: 1000 <= x < 1500),
    ('800-1000 字', lambda x: 800 <= x < 1000),
    ('500-800 字', lambda x: 500 <= x < 800),
    ('< 500 字', lambda x: x < 500),
]

for label, condition in word_ranges:
    count = sum(1 for f in b_level_files if condition(f['cn_chars']))
    print(f"  {label}: {count} 个")

print(f"\n{'='*80}")
print("按目录统计 B 级文件数:")
print(f"{'='*80}")
for dir_name, files in sorted(by_dir.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {dir_name}: {len(files)} 个")
