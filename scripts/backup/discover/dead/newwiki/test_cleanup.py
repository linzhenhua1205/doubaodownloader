import os
import re

wiki_dir = r"h:\github\cowkb\discover\newwiki"
filename = '其他_后端开发.md'
filepath = os.path.join(wiki_dir, filename)

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_section_keywords = [
    "概述", "相关主题", "知识体系结构", "快速导航", "核心概念",
    "问题解答", "技术要点", "实践指南", "延伸资源", "变更记录",
    "知识体系框架图", "常见问题", "扩展资源", "2025-2026最新进展"
]

lines = content.split('\n')
result_lines = []
skip_mode = False
in_code_block = False
found_h1 = False
h1_line = ''

for line in lines:
    if not found_h1:
        if line.startswith('# '):
            found_h1 = True
            h1_line = line
        continue
    
    if line.startswith('```'):
        in_code_block = not in_code_block
        result_lines.append(line)
        continue
    
    if in_code_block:
        result_lines.append(line)
        continue
    
    if line.startswith('## '):
        section_title = line[3:].strip()
        is_old = any(kw in section_title for kw in old_section_keywords)
        if is_old:
            skip_mode = True
            continue
        else:
            skip_mode = False
    
    if not skip_mode:
        result_lines.append(line)

final = h1_line + '\n\n' + '\n'.join(result_lines)
final = re.sub(r'\n{4,}', '\n\n\n', final)

sections = re.findall(r'^##\s+(.+)$', final, re.MULTILINE)
print(f'清理后章节数: {len(sections)}')
for i, s in enumerate(sections):
    print(f'  {i+1}. {s}')
print(f'\n清理后字数: {len(final)}')
print(f'\n原始字数: {len(content)}')
print(f'移除: {len(content) - len(final)} 字')
