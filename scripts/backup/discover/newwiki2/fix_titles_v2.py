#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二轮修复：修复引导语和ASCII图中的标题
"""

import re
import os

def fix_file_v2(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath).replace('.md', '')
    
    # 获取正确的标题
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return False, '无frontmatter'
    fm_content = fm_match.group(1)
    title_match = re.search(r'title:\s*(.+)', fm_content)
    if not title_match:
        return False, '无title'
    title = title_match.group(1).strip()
    
    # 1. 修复引导语
    content = re.sub(
        r'> \*\*本卡片为B级增强知识文档\*\*，系统梳理.*?的核心概念、方法框架',
        f'> **本卡片为B级增强知识文档**，系统梳理{title}的核心概念、方法框架',
        content
    )
    
    # 2. 修复ASCII图中的标题行
    lines = content.split('\n')
    in_code_block = False
    code_block_start = -1
    
    for i, line in enumerate(lines):
        if line.startswith('```'):
            if in_code_block:
                # 代码块结束
                in_code_block = False
            else:
                # 代码块开始
                in_code_block = True
                code_block_start = i
            continue
        
        if in_code_block and '知识体系' in line and '│' in line:
            # 检查是不是标题行（只有两个竖线，中间是标题）
            if line.count('│') == 2 and line.startswith('│') and line.endswith('│'):
                # 替换标题
                new_title = title + '知识体系'
                # 计算填充空格
                total_width = 76
                pad = total_width - len(new_title)
                left_pad = pad // 2
                right_pad = pad - left_pad
                lines[i] = '│' + ' ' * left_pad + new_title + ' ' * right_pad + '│'
            elif '┌' in line and '┐' in line:
                # 顶部边框行，长度可能需要调整，但不用改内容
                pass
    
    content = '\n'.join(lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True, '修复完成'

if __name__ == '__main__':
    dir_path = 'programming'
    
    files = [
        '01-ai-pair-programming.md',
        '02-software-architecture-patterns.md',
        '03-lachat-architecture.md',
        'paperclip.md',
        'rise.md',
        'sherwood.md',
        'ubuntutoucho.md',
        'windows.md',
        '三体阅读心境.md',
        '企业周均工时.md',
        '叙事六要素.md',
        '古文讲解与原.md',
        '备件快速响应.md',
        '大学生就业趋.md',
        '审计步骤核心.md',
        '属性辨析.md',
        '市场份额对.md',
        '开发代码版本.md',
        '归纳过程可视.md',
        '快速理解开源.md',
        '支持度与置信.md',
        '数学证明解析.md',
        '服务器软件趋.md',
        '生产标物料转.md',
        '知乎文章无法.md',
        '股权.md',
        '螺旋模型优化.md',
        '行人路权受侵.md',
        '解构思维解决.md',
        '认知托付框架.md',
        '链接解析失败.md',
        '阿里云光模块.md',
        '阿里云王坚.md',
        '附件链接失效.md',
    ]
    
    success_count = 0
    for filename in files:
        filepath = os.path.join(dir_path, filename)
        if not os.path.exists(filepath):
            print(f'{filename:40s} 跳过（文件不存在）')
            continue
        
        success, msg = fix_file_v2(filepath)
        status = '成功' if success else '失败'
        print(f'{filename:40s} {status} {msg}')
        if success:
            success_count += 1
    
    print()
    print(f'共处理 {len(files)} 个文件，成功 {success_count} 个')
