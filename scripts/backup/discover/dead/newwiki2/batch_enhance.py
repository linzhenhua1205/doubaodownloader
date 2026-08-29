#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量增强脚本 - 为AI技术目录的文件添加标准化模块
"""

import os
import re
from pathlib import Path

def count_chinese_chars(text):
    """统计中文字符数"""
    return len(re.findall(r'[\u4e00-\u9fa5]', text))

def get_file_info(filepath):
    """获取文件基本信息"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {
        'path': filepath,
        'name': os.path.basename(filepath),
        'chars': count_chinese_chars(content),
        'has_ascii': bool(re.search(r'```[a-z]*\n[\s\S]*?[+\-|=][\s\S]*?\n```', content)),
        'has_table': bool(re.search(r'\|.*\|.*\|', content)),
        'has_seven_modules': all([
            '一、' in content or '## 一' in content,
            '二、' in content or '## 二' in content,
            '三、' in content or '## 三' in content,
            '四、' in content or '## 四' in content,
            '五、' in content or '## 五' in content,
            '六、' in content or '## 六' in content,
            '七、' in content or '## 七' in content,
        ]),
        'is_note_index': '知识索引页' in content or '卡片概览' in content,
        'content': content
    }
    return info

def scan_directory(dirpath):
    """扫描目录下所有md文件"""
    files = []
    for f in sorted(os.listdir(dirpath)):
        if f.endswith('.md') and f != 'index.md':
            filepath = os.path.join(dirpath, f)
            info = get_file_info(filepath)
            files.append(info)
    return files

def print_summary(files, dirname):
    """打印目录摘要"""
    print(f"\n{'='*60}")
    print(f"目录: {dirname}")
    print(f"{'='*60}")
    print(f"总文件数: {len(files)}")
    
    s_level = [f for f in files if f['chars'] >= 5000]
    a_level = [f for f in files if 3000 <= f['chars'] < 5000]
    b_level = [f for f in files if 1500 <= f['chars'] < 3000]
    c_level = [f for f in files if f['chars'] < 1500]
    
    print(f"S级(≥5000字): {len(s_level)} 个")
    print(f"A级(3000-5000字): {len(a_level)} 个")
    print(f"B级(1500-3000字): {len(b_level)} 个")
    print(f"C级(<1500字): {len(c_level)} 个")
    
    note_index_files = [f for f in files if f['is_note_index']]
    print(f"\n笔记索引页: {len(note_index_files)} 个")
    
    print(f"\n文件详情:")
    for f in files:
        level = 'S' if f['chars'] >= 5000 else 'A' if f['chars'] >= 3000 else 'B' if f['chars'] >= 1500 else 'C'
        flags = []
        if f['is_note_index']:
            flags.append('笔记索引')
        if not f['has_table']:
            flags.append('无表格')
        if not f['has_ascii']:
            flags.append('无ASCII图')
        flag_str = f" ({', '.join(flags)})" if flags else ''
        print(f"  {level:2s} | {f['chars']:5d}字 | {f['name']}{flag_str}")

if __name__ == '__main__':
    base_dir = r'h:\github\cowkb\discover\newwiki2'
    
    dirs = [
        ('AI-模型架构', os.path.join(base_dir, 'AI-模型架构')),
        ('AI-训练微调', os.path.join(base_dir, 'AI-训练微调')),
        ('AI-Agent', os.path.join(base_dir, 'AI-Agent')),
    ]
    
    all_files = []
    for dirname, dirpath in dirs:
        files = scan_directory(dirpath)
        print_summary(files, dirname)
        all_files.extend(files)
    
    print(f"\n\n{'='*60}")
    print(f"三个目录总计: {len(all_files)} 个文件")
    print(f"{'='*60}")
    
    total_chars = sum(f['chars'] for f in all_files)
    s_count = sum(1 for f in all_files if f['chars'] >= 5000)
    a_count = sum(1 for f in all_files if 3000 <= f['chars'] < 5000)
    b_count = sum(1 for f in all_files if 1500 <= f['chars'] < 3000)
    c_count = sum(1 for f in all_files if f['chars'] < 1500)
    
    print(f"总字数: {total_chars:,} 字")
    print(f"S级: {s_count} 个")
    print(f"A级: {a_count} 个")
    print(f"B级: {b_count} 个")
    print(f"C级: {c_count} 个")
    
    note_count = sum(1 for f in all_files if f['is_note_index'])
    print(f"笔记索引页: {note_count} 个")
