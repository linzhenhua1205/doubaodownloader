#!/usr/bin/env python3
import re
from pathlib import Path

def extract_headings(content):
    headings = []
    pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
    for match in pattern.finditer(content):
        level = len(match.group(1))
        title = match.group(2).strip()
        if level <= 3:
            headings.append((level, title))
    return headings

def generate_toc(headings):
    toc_lines = ["## 📑 目录", ""]
    for level, title in headings:
        link = title.replace(' ', '-').replace(':', '').replace('？', '').replace('！', '').replace('（', '').replace('）', '')
        link = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\-]', '', link).lower()
        indent = "  " * (level - 1)
        toc_lines.append(f"{indent}- [{title}](#{link})")
    toc_lines.append("")
    return '\n'.join(toc_lines)

def force_add_toc(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        first_h2_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('## ') and i > 10:
                first_h2_idx = i
                break
        
        if first_h2_idx == -1:
            return False, f"未找到合适的插入位置: {filepath}"
        
        new_toc = generate_toc(extract_headings(content))
        
        lines.insert(first_h2_idx, '')
        lines.insert(first_h2_idx, new_toc)
        
        new_content = '\n'.join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"成功添加目录: {filepath}"
    except Exception as e:
        return False, f"失败: {filepath} - {str(e)}"

def main():
    directory = r'h:\github\cowkb\discover\site\行业动态'
    md_files = sorted(Path(directory).glob('*.md'))
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    for filepath in md_files:
        if filepath.name == 'index.md':
            skipped_count += 1
            continue
        
        print(f"正在处理: {filepath.name}")
        success, msg = force_add_toc(str(filepath))
        
        if success:
            success_count += 1
        else:
            fail_count += 1
            print(f"  {msg}")
    
    print("\n" + "="*60)
    print("强制添加目录完成报告")
    print("="*60)
    print(f"总文件数: {len(md_files)}")
    print(f"跳过(index.md): {skipped_count}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print("="*60)

if __name__ == '__main__':
    main()