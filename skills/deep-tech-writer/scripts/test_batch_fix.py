# -*- coding: utf-8 -*-
"""小规模测试：每个目录处理前10个文件"""

import sys
sys.path.insert(0, r'h:\github\cowkb\skills\deep-tech-writer\scripts')

from pathlib import Path
from batch_fix_structure import process_file, has_header_block, has_ref_section, has_changelog_section

def test_dir(dir_path, label, limit=10):
    print(f'\n{"="*60}')
    print(f'测试目录: {label}')
    print(f'{"="*60}')
    
    dir_path = Path(dir_path)
    files = sorted([f for f in dir_path.glob('*.md') 
                   if f.name not in ('index.md', 'progress.md')])[:limit]
    
    for f in files:
        # 处理前检查
        with open(f, 'rb') as fh:
            raw = fh.read()
        if raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        content_before = raw.decode('utf-8', errors='replace')
        
        h_before = has_header_block(content_before)
        r_before = has_ref_section(content_before)
        c_before = has_changelog_section(content_before)
        
        stats = process_file(f)
        
        # 处理后检查
        with open(f, 'rb') as fh:
            raw = fh.read()
        if raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        content_after = raw.decode('utf-8', errors='replace')
        
        h_after = has_header_block(content_after)
        r_after = has_ref_section(content_after)
        c_after = has_changelog_section(content_after)
        
        status_parts = []
        if stats['error']:
            status_parts.append(f'ERR: {stats["error"]}')
        else:
            if not h_before and h_after:
                status_parts.append('✓ 新增概要/关键词')
            elif h_before and h_after:
                status_parts.append('— 已有概要/关键词')
            else:
                status_parts.append('✗ 概要/关键词仍缺失!')
            
            if not r_before and r_after:
                status_parts.append('✓ 新增参考文件')
            elif r_before and r_after:
                status_parts.append('— 已有参考文件')
            else:
                status_parts.append('✗ 参考文件仍缺失!')
            
            if not c_before and c_after:
                status_parts.append('✓ 新增Changelog')
            elif c_before and c_after:
                status_parts.append('— 已有Changelog')
            else:
                status_parts.append('✗ Changelog仍缺失!')
        
        print(f'  {f.name}: {" | ".join(status_parts)}')

if __name__ == '__main__':
    base = Path(r'h:\github\cowkb\discover\newwiki2\docs')
    test_dir(base / 'AI应用与落地实践', 'AI应用与落地实践')
    test_dir(base / '方法论与工具', '方法论与工具')
    test_dir(base / '行业趋势与洞察', '行业趋势与洞察')
