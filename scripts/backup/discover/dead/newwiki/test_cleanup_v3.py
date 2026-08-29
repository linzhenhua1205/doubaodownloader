import os
import re

wiki_dir = r"h:\github\cowkb\discover\newwiki"

test_files = ['其他_网络协议.md', 'AI伦理与安全.md', '其他_生活文化.md']

old_section_titles = {
    "概述", "相关主题", "知识体系结构", "快速导航", "核心概念",
    "问题解答", "技术要点", "实践指南", "延伸资源", "变更记录",
    "知识体系框架图", "常见问题", "扩展资源", "2025-2026最新进展"
}

for filename in test_files:
    filepath = os.path.join(wiki_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    result_lines = []
    skip_mode = False
    in_code_block = False
    found_h1 = False
    h1_line = ''
    skipped_sections = []
    kept_sections = []
    
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
            
            clean_title = re.sub(r'^[📌🌟🎭🌐💼🔬📊🎯🏢📚🧬🏗️]+', '', section_title).strip()
            
            if clean_title in old_section_titles:
                skip_mode = True
                skipped_sections.append(section_title)
                continue
            else:
                skip_mode = False
                kept_sections.append(section_title)
        
        if not skip_mode:
            result_lines.append(line)
    
    final = h1_line + '\n\n' + '\n'.join(result_lines)
    final = re.sub(r'\n{4,}', '\n\n\n', final)
    
    print(f'\n=== {filename} ===')
    print(f'原始字数: {len(content):,}')
    print(f'清理后字数: {len(final):,}')
    print(f'移除: {len(content) - len(final):,} 字')
    print(f'保留章节: {len(kept_sections)} 个')
    for i, s in enumerate(kept_sections[:10]):
        print(f'  {i+1}. {s}')
    if len(kept_sections) > 10:
        print(f'  ... 还有 {len(kept_sections)-10} 个')
    print(f'跳过章节: {len(skipped_sections)} 个')
    for i, s in enumerate(skipped_sections[:10]):
        print(f'  {i+1}. {s}')
