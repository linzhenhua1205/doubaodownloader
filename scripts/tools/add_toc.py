import os
import re
import sys

def extract_h2_headings(content):
    pattern = r'^##\s+(.+?)\s*$'
    headings = []
    for line in content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            heading_text = match.group(1).strip()
            if heading_text != '📑 目录':
                headings.append(heading_text)
    return headings

def generate_anchor(text):
    result = text.lower()
    result = re.sub(r'[^\w\s-]', '', result)
    result = re.sub(r'\s+', '-', result)
    result = re.sub(r'-+', '-', result)
    result = result.strip('-')
    return result

def find_toc_position(content):
    lines = content.split('\n')
    in_front_matter = False
    h1_found = False
    keywords_found = False
    
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == '---':
            in_front_matter = True
            continue
        if in_front_matter:
            if line.strip() == '---':
                in_front_matter = False
            continue
        if line.startswith('# ') and not h1_found:
            h1_found = True
            continue
        if h1_found and (line.startswith('> **关键词**:') or line.startswith('> **关键词**：')):
            keywords_found = True
            continue
        if keywords_found and line.strip() == '':
            return i + 1
    
    first_h2_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith('## '):
            first_h2_index = i
            break
    if first_h2_index is None:
        return len(lines)
    return first_h2_index

def has_existing_toc(content):
    return '## 📑 目录' in content

def remove_existing_toc(content):
    lines = content.split('\n')
    new_lines = []
    skip_mode = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == '## 📑 目录':
            skip_mode = True
            i += 1
            continue
        if skip_mode:
            if line.strip().startswith('## '):
                skip_mode = False
            else:
                i += 1
                continue
        new_lines.append(line)
        i += 1
    return '\n'.join(new_lines)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    if has_existing_toc(content):
        content = remove_existing_toc(content)
    
    headings = extract_h2_headings(content)
    if not headings:
        return 'skipped_no_h2'
    
    toc_lines = ['## 📑 目录', '']
    for heading in headings:
        anchor = generate_anchor(heading)
        toc_lines.append(f'- [{heading}](#{anchor})')
    toc_lines.append('')
    
    toc_content = '\n'.join(toc_lines)
    
    insert_pos = find_toc_position(content)
    lines = content.split('\n')
    
    new_lines = lines[:insert_pos] + [toc_content] + lines[insert_pos:]
    new_content = '\n'.join(new_lines)
    
    if new_content == original_content:
        return 'skipped_no_change'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    if has_existing_toc(original_content):
        return 'updated'
    else:
        return 'added'

def main():
    if len(sys.argv) < 2:
        print('用法: python add_toc.py <目录路径>')
        sys.exit(1)
    
    dir_path = sys.argv[1]
    
    if not os.path.isdir(dir_path):
        print(f'错误: {dir_path} 不是有效的目录')
        sys.exit(1)
    
    md_files = [f for f in os.listdir(dir_path) if f.endswith('.md') and f != 'index.md']
    
    print(f'找到 {len(md_files)} 个 Markdown 文件（跳过 index.md）')
    print('-' * 60)
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for filename in sorted(md_files):
        filepath = os.path.join(dir_path, filename)
        try:
            result = process_file(filepath)
            if result == 'added':
                added_count += 1
                print(f'✅ 添加: {filename}')
            elif result == 'updated':
                updated_count += 1
                print(f'🔄 更新: {filename}')
            elif result == 'skipped_no_h2':
                skipped_count += 1
                print(f'⚠️  无二级标题: {filename}')
            elif result == 'skipped_no_change':
                skipped_count += 1
        except Exception as e:
            error_count += 1
            print(f'❌ 失败 ({e}): {filename}')
    
    print('-' * 60)
    print(f'📊 统计结果:')
    print(f'   新增目录: {added_count}')
    print(f'   更新目录: {updated_count}')
    print(f'   跳过: {skipped_count}')
    print(f'   失败: {error_count}')
    print(f'   总计处理: {added_count + updated_count + skipped_count + error_count}')

if __name__ == '__main__':
    main()
