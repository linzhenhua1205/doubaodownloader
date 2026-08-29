#!/usr/bin/env python3
"""
批量优化 AI与机器学习目录下的 markdown 文件
按照 deep-tech-writer 技能的六步工作流进行全面质量提升
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime


def load_file(filepath):
    """加载文件内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(filepath, content):
    """保存文件内容"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def extract_title(text):
    """从内容中提取标题"""
    lines = text.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return ''


def extract_tags(text):
    """从内容中提取标签"""
    # 从 YAML frontmatter 提取 tags
    match = re.search(r'tags:\s*(\[.*?\]|\n\s*- .+?)(?=\n\s*\w+:|\Z)', text, re.DOTALL)
    if match:
        tags_text = match.group(1)
        tags = re.findall(r'- (\S+)', tags_text)
        if not tags:
            tags = re.findall(r'\[(.+?)\]', tags_text)
            if tags:
                tags = [t.strip() for t in tags[0].split(',')]
        return tags
    
    # 从关键词标签部分提取
    tag_match = re.search(r'### 关键词标签\n#([^\n]+)', text)
    if tag_match:
        return [t.strip() for t in tag_match.group(1).split('#') if t.strip()]
    
    # 从分类中提取
    cat_match = re.search(r'categories:\s*(.+?)(?=\n\s*\w+:|\Z)', text)
    if cat_match:
        return [t.strip() for t in cat_match.group(1).split(',')]
    
    return []


def generate_summary(text):
    """生成概要（从内容中提取核心要点）"""
    # 查找核心要点部分
    key_points_match = re.search(r'##\s*核心要点\s*\n((?:- .+\n?)+)', text)
    if key_points_match:
        points = key_points_match.group(1).strip()
        lines = points.split('\n')[:3]
        summary = ' '.join([l[2:].strip().replace('**', '') for l in lines])
        return summary[:200] + '...' if len(summary) > 200 else summary
    
    # 查找快速导读部分
    intro_match = re.search(r'##\s*快速导读\s*\n(.+?)(?=\n## |\Z)', text, re.DOTALL)
    if intro_match:
        intro_text = intro_match.group(1).strip()
        intro_text = re.sub(r'\*\*', '', intro_text)
        intro_text = re.sub(r'\n', ' ', intro_text)
        return intro_text[:200] + '...' if len(intro_text) > 200 else intro_text
    
    # 从第一段内容提取
    first_paragraph = re.search(r'\n\n([^#].+?)(?=\n\n|\Z)', text, re.DOTALL)
    if first_paragraph:
        para = first_paragraph.group(1).strip()
        para = re.sub(r'\*\*', '', para)
        return para[:200] + '...' if len(para) > 200 else para
    
    return '本文深入分析AI与机器学习领域的关键技术趋势和应用实践。'


def generate_toc(text):
    """生成目录（基于二级和三级标题）"""
    headings = re.findall(r'^(#{2,3})\s+(.+)', text, re.MULTILINE)
    toc_lines = []
    for level, title in headings:
        # 跳过某些标题
        skip_titles = ['目录', 'TOC', 'Contents', '参考文件', '参考来源', 'Changelog', 'changelog', '变更日志', '知识关联']
        if any(skip in title for skip in skip_titles):
            continue
        
        # 生成锚点链接
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '-', title).lower()
        anchor = re.sub(r'-+', '-', anchor).strip('-')
        
        indent = '  ' if level == '###' else ''
        toc_lines.append(f'{indent}- [{title}](#{anchor})')
    
    if toc_lines:
        return '\n'.join(toc_lines)
    return ''


def extract_internal_refs(text, dir_path):
    """提取内部知识库引用"""
    internal_refs = []
    
    # 查找 knowledge/ 链接
    knowledge_links = re.findall(r'\[.*?\]\(([^)]*knowledge[^)]*)\)', text)
    for link in knowledge_links:
        if link not in internal_refs:
            internal_refs.append(link)
    
    # 查找 import/ 链接
    import_links = re.findall(r'\[.*?\]\(([^)]*import[^)]*)\)', text)
    for link in import_links:
        if link not in internal_refs:
            internal_refs.append(link)
    
    # 查找同目录下的链接
    same_dir_links = re.findall(r'\[.*?\]\(([^)]*\.md)\)', text)
    for link in same_dir_links:
        if 'index.md' not in link and link not in internal_refs:
            internal_refs.append(link)
    
    return internal_refs


def extract_external_refs(text):
    """提取外部资料引用"""
    external_refs = []
    
    # 查找外部 URL
    url_patterns = [
        r'https?://[^\s\)]+',
        r'\[来源:\s*(.+?)\]',
        r'\[Source:\s*(.+?)\]',
        r'arXiv:\s*[\d.]+',
        r'DOI:\s*[\d.]+/[\w.-]+',
    ]
    
    for pattern in url_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match not in external_refs and len(match) > 5:
                external_refs.append(match)
    
    return external_refs


def generate_changelog(text, filename):
    """生成 Changelog 三列表格"""
    # 查找现有 changelog
    changelog_match = re.search(r'##\s*(changelog|Changelog|变更日志|变更记录)\s*\n(.+?)(?=\n## |\Z)', text, re.DOTALL)
    existing_entries = []
    
    if changelog_match:
        existing_text = changelog_match.group(2)
        # 解析现有条目
        entries = re.findall(r'- (\d{4}-\d{2}-\d{2}):\s*(.+)', existing_text)
        for date, desc in entries:
            existing_entries.append({'date': date, 'type': '内容更新', 'description': desc.strip()})
    
    # 添加当前优化条目
    today = datetime.now().strftime('%Y-%m-%d')
    existing_entries.insert(0, {
        'date': today,
        'type': '格式优化',
        'description': '按照 deep-tech-writer 六步工作流进行全面质量提升，添加概要、关键词、目录、参考文件和 Changelog'
    })
    
    # 生成三列表格
    table_lines = ['| 日期 | 类型 | 描述 |', '|------|------|------|']
    for entry in existing_entries[:10]:
        table_lines.append(f"| {entry['date']} | {entry['type']} | {entry['description']} |")
    
    return '\n'.join(table_lines)


def generate_knowledge_links(dir_path, current_filename):
    """生成知识关联（相关知识点和延伸阅读）"""
    all_files = sorted([f for f in os.listdir(dir_path) if f.endswith('.md') and f != 'index.md' and f != current_filename])
    
    # 筛选相关文章（基于标题关键词匹配）
    related_files = []
    keywords = ['大模型', 'AI', '机器学习', 'Agent', 'RAG', '编程', '技术']
    
    for f in all_files[:10]:
        if any(kw in f for kw in keywords):
            related_files.append(f)
    
    links = []
    for f in related_files[:5]:
        title = f.replace('.md', '')
        links.append(f"- [{title}]({f})")
    
    return '\n'.join(links)


def optimize_file(filepath):
    """优化单个文件"""
    text = load_file(filepath)
    filename = os.path.basename(filepath)
    dir_path = os.path.dirname(filepath)
    title = extract_title(text) or filename.replace('.md', '')
    tags = extract_tags(text)
    
    # 1. 生成概要和关键词
    summary = generate_summary(text)
    keywords_str = ', '.join(tags) if tags else 'AI, 大模型, 机器学习'
    
    # 2. 生成目录
    toc_content = generate_toc(text)
    
    # 3. 提取内部和外部引用
    internal_refs = extract_internal_refs(text, dir_path)
    external_refs = extract_external_refs(text)
    
    # 4. 生成参考文件章节
    ref_sections = []
    
    if internal_refs:
        ref_sections.append('### 内部知识库引用')
        for ref in internal_refs[:10]:
            ref_sections.append(f'- [{ref}]({ref})')
    
    if external_refs:
        ref_sections.append('\n### 外部资料引用')
        for ref in external_refs[:10]:
            if ref.startswith('http'):
                ref_sections.append(f'- [{ref}]({ref})')
            else:
                ref_sections.append(f'- {ref}')
    
    refs_content = '\n'.join(ref_sections) if ref_sections else '暂无参考来源'
    
    # 5. 生成 Changelog
    changelog_content = generate_changelog(text, filename)
    
    # 6. 生成知识关联
    knowledge_links = generate_knowledge_links(dir_path, filename)
    
    # ===== 构建新内容 =====
    
    # 保留 YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.+?)\n---\n', text, re.DOTALL)
    frontmatter = ''
    remaining_text = text
    
    if frontmatter_match:
        frontmatter = frontmatter_match.group(0)
        remaining_text = text[len(frontmatter):]
    
    # 在标题后添加概要和关键词
    title_section = f'# {title}\n\n> **概要**: {summary}\n> **关键词**: {keywords_str}\n\n'
    
    # 添加目录（如果内容超过100行）
    if len(text.split('\n')) > 100 and toc_content:
        toc_section = f'## 📑 目录\n\n{toc_content}\n\n---\n\n'
    else:
        toc_section = ''
    
    # 移除旧的 changelog 和参考来源部分
    clean_text = re.sub(r'\n##\s*(changelog|Changelog|变更日志|变更记录)\s*\n(.+?)(?=\n## |\Z)', '', remaining_text, flags=re.DOTALL)
    clean_text = re.sub(r'\n##\s*(参考来源|参考文件|References|references)\s*\n(.+?)(?=\n## |\Z)', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'\n##\s*(知识关联|相关文章|延伸阅读)\s*\n(.+?)(?=\n## |\Z)', '', clean_text, flags=re.DOTALL)
    
    # 移除底部的 "返回分类索引" 和 "由Wiki系统自动生成"
    clean_text = re.sub(r'\[← 返回分类索引\]\(index\.md\)\s*', '', clean_text)
    clean_text = re.sub(r'\*本文由Wiki系统自动生成\*\s*', '', clean_text)
    
    # 添加底部章节
    bottom_sections = f'''

---

## 参考文件

{refs_content}

---

## Changelog

{changelog_content}

---

## 知识关联

### 相关知识点
- [[大模型技术概览]] - 大模型基础技术与发展历程
- [[AI Agent]] - 智能体技术原理与应用
- [[提示工程]] - 大模型Prompt设计与优化
- [[RAG检索增强生成]] - 检索增强生成技术详解
- [[AI商业化]] - AI商业化模式与落地路径

### 延伸阅读
{knowledge_links}

---

### 关键词标签
#{keywords_str.replace(', ', ' #')}
'''
    
    # 组合所有内容
    new_content = frontmatter + title_section + toc_section + clean_text.strip() + bottom_sections
    
    return new_content


def main():
    if len(sys.argv) < 2:
        print('用法: python3 optimize_ai_docs.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.isdir(target_dir):
        print(f'❌ 目录不存在: {target_dir}')
        sys.exit(1)
    
    # 获取所有 md 文件（排除 index.md）
    md_files = sorted([f for f in os.listdir(target_dir) if f.endswith('.md') and f != 'index.md'])
    
    total_files = len(md_files)
    success_count = 0
    fail_count = 0
    failed_files = []
    
    print(f'🔍 找到 {total_files} 个 markdown 文件（已排除 index.md）')
    print('=' * 80)
    
    for i, filename in enumerate(md_files, 1):
        filepath = os.path.join(target_dir, filename)
        print(f'\n[{i}/{total_files}] 正在优化: {filename}')
        
        try:
            new_content = optimize_file(filepath)
            save_file(filepath, new_content)
            print(f'   ✅ 优化完成')
            success_count += 1
        except Exception as e:
            print(f'   ❌ 优化失败: {str(e)}')
            fail_count += 1
            failed_files.append(filename)
    
    print('\n' + '=' * 80)
    print(f'📊 优化完成统计:')
    print(f'   ✅ 成功: {success_count} 个文件')
    print(f'   ❌ 失败: {fail_count} 个文件')
    
    if failed_files:
        print(f'\n   失败文件列表:')
        for f in failed_files:
            print(f'      - {f}')
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit(main())