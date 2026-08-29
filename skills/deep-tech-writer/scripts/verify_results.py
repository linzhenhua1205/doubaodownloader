#!/usr/bin/env python3
"""验证人文社会目录重构结果"""

import os
import re

directory = r'h:\github\cowkb\discover\site\人文社会'

total_files = 0
has_summary = 0
has_keywords = 0
has_toc = 0
has_frontmatter = 0
has_references = 0
has_changelog = 0
avg_summary_len = 0
avg_keyword_count = 0
total_original_size = 0
total_new_size = 0

results = []

for f in sorted(os.listdir(directory)):
    if not f.endswith('.md') or f == 'index.md':
        continue
    
    file_path = os.path.join(directory, f)
    total_files += 1
    
    with open(file_path, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    total_new_size += len(content)
    
    file_result = {'file': f, 'size': len(content)}
    
    if '> **概要**:' in content:
        has_summary += 1
        m = re.search(r'> \*\*概要\*\*: (.+)', content)
        if m:
            summary_len = len(m.group(1))
            avg_summary_len += summary_len
            file_result['summary_len'] = summary_len
    
    if '> **关键词**:' in content:
        has_keywords += 1
        m = re.search(r'> \*\*关键词\*\*: (.+)', content)
        if m:
            kw_count = len(m.group(1).split('·'))
            avg_keyword_count += kw_count
            file_result['keyword_count'] = kw_count
    
    if '## 📑 目录' in content:
        has_toc += 1
    
    if re.search(r'^---\n', content) and content.count('---') >= 2:
        has_frontmatter += 1
    
    if '## 参考文件' in content:
        has_references += 1
    
    if '## Changelog' in content:
        has_changelog += 1
    
    results.append(file_result)

print('=' * 70)
print('人文社会目录重构结果验证')
print('=' * 70)
print(f'总文件数: {total_files}')
print()
print('格式标准化:')
print(f'  - 有概要: {has_summary}/{total_files} ({has_summary/total_files*100:.1f}%)')
print(f'  - 有 keywords: {has_keywords}/{total_files} ({has_keywords/total_files*100:.1f}%)')
print(f'  - 有目录: {has_toc}/{total_files} ({has_toc/total_files*100:.1f}%)')
print(f'  - 有 frontmatter: {has_frontmatter}/{total_files} ({has_frontmatter/total_files*100:.1f}%)')
print(f'  - 有参考文件: {has_references}/{total_files} ({has_references/total_files*100:.1f}%)')
print(f'  - 有 Changelog: {has_changelog}/{total_files} ({has_changelog/total_files*100:.1f}%)')
print()
print('内容质量:')
if has_summary > 0:
    print(f'  - 平均概要长度: {avg_summary_len/has_summary:.1f} 字')
if has_keywords > 0:
    print(f'  - 平均关键词数量: {avg_keyword_count/has_keywords:.1f} 个')
print(f'  - 总大小: {total_new_size/1024:.1f} KB')
print()
print('=' * 70)
