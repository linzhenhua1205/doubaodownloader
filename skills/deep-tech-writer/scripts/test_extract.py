#!/usr/bin/env python3
"""测试内容提取逻辑"""

import re
from pathlib import Path

BASE_DIR = Path("h:/github/cowkb")
TEST_FILE = BASE_DIR / "discover" / "site" / "数据库与存储" / "MySQL 8_0查询缓存_Query Cache_功能深度解析：移除原因与替代方案.md"

def extract_frontmatter(content):
    """提取YAML frontmatter"""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        return match.group(0), match.group(1), content[match.end():]
    return '', '', content


def clean_section_title(title):
    """清理章节标题：去除emoji、编号等"""
    emoji_pattern = r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\s]+'
    title = re.sub(emoji_pattern, '', title).strip()
    title = re.sub(r'^[0-9]+[.、\s]+', '', title)
    return title.strip()


def find_content_section(body):
    """找到"内容"章节的位置和内容"""
    lines = body.split('\n')
    in_content_section = False
    content_lines = []
    content_start = -1
    content_end = -1
    
    for i, line in enumerate(lines):
        # 匹配二级标题
        if line.startswith('## '):
            title = line[3:].strip()
            clean_title = clean_section_title(title)
            
            if '内容' == clean_title or clean_title.endswith('内容'):
                in_content_section = True
                content_start = i
                continue
            
            if in_content_section:
                # 遇到下一个二级标题，结束
                content_end = i
                break
        
        if in_content_section and content_start >= 0:
            content_lines.append(line)
    
    if in_content_section and content_end == -1:
        content_end = len(lines)
    
    return content_start, content_end, '\n'.join(content_lines)


def elevate_headings(content_text):
    """将三级标题提升为二级标题，四级提升为三级"""
    lines = content_text.split('\n')
    result = []
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            result.append(line)
            continue
        
        if in_code_block:
            result.append(line)
            continue
        
        if line.startswith('### '):
            heading_text = line[4:].strip()
            clean_heading = clean_section_title(heading_text)
            result.append(f'## {clean_heading}')
        elif line.startswith('#### '):
            heading_text = line[5:].strip()
            clean_heading = clean_section_title(heading_text)
            result.append(f'### {clean_heading}')
        else:
            result.append(line)
    
    return '\n'.join(result)


def main():
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter_full, frontmatter_content, body = extract_frontmatter(content)
    
    print("=" * 60)
    print(f"Frontmatter长度: {len(frontmatter_full)}")
    print(f"Body长度: {len(body)}")
    print("=" * 60)
    
    # 找"内容"章节
    start, end, content_text = find_content_section(body)
    print(f"\n内容章节位置: 第{start}行 - 第{end}行")
    print(f"内容章节长度: {len(content_text)} 字符")
    
    if content_text:
        print("\n" + "=" * 60)
        print("内容章节前500字符:")
        print("=" * 60)
        print(content_text[:500])
        
        # 测试提升标题
        elevated = elevate_headings(content_text)
        print("\n" + "=" * 60)
        print("提升标题后的前500字符:")
        print("=" * 60)
        print(elevated[:500])
        
        # 提取二级标题
        h2_pattern = r'^##\s+(.+?)\s*$'
        h2_matches = re.findall(h2_pattern, elevated, re.MULTILINE)
        print(f"\n提升后的二级标题数量: {len(h2_matches)}")
        for i, t in enumerate(h2_matches):
            print(f"  {i+1}. {t}")


if __name__ == '__main__':
    main()
