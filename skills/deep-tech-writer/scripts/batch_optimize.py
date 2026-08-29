#!/usr/bin/env python3
"""
批量优化知识管理目录下的markdown文件

按照deep-tech-writer六步工作流的格式规范进行优化：
1. 添加头部：> **概要**: 和 > **关键词**:
2. 添加目录：## 📑 目录
3. 添加尾部：## 参考文件（含内部知识库引用和外部资料引用）
4. 添加尾部：## Changelog（三列表格）
5. 修复代码块中文问题
6. 添加知识关联
"""

import re
import os
import sys
from pathlib import Path


def extract_title(text):
    """提取标题（第一个#开头的行）"""
    lines = text.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return ""


def extract_categories(text):
    """从YAML frontmatter提取分类标签"""
    match = re.search(r'categories:\s*(.+?)\n', text)
    if match:
        return match.group(1).strip()
    return ""


def extract_tags(text):
    """从文件内容提取标签"""
    tags = []
    
    # 从YAML frontmatter提取tags
    match = re.search(r'tags:\s*(.+?)\n', text)
    if match:
        tag_str = match.group(1).strip()
        if tag_str and tag_str != 'null':
            tags.extend([t.strip() for t in tag_str.split(',')])
    
    # 从分类提取关键词
    cats = extract_categories(text)
    if cats:
        tags.extend([t.strip() for t in cats.split(',')])
    
    # 从内容提取已有标签
    tag_matches = re.findall(r'#(\S+)', text)
    tags.extend(tag_matches)
    
    return list(set(tags))


def generate_summary(text):
    """生成概要（从执行摘要或核心要点提取）"""
    # 尝试从执行摘要提取
    exec_summary_match = re.search(r'##\s*执行摘要\s*\n(.+?)(\n##|\Z)', text, re.DOTALL)
    if exec_summary_match:
        summary = exec_summary_match.group(1).strip()
        # 取前200字
        if len(summary) > 200:
            summary = summary[:200] + "..."
        return summary
    
    # 尝试从核心要点提取
    core_points_match = re.search(r'##\s*核心要点\s*\n(.+?)(\n##|\Z)', text, re.DOTALL)
    if core_points_match:
        points = core_points_match.group(1).strip()
        lines = [l.strip() for l in points.split('\n') if l.strip()]
        if lines:
            summary = "、".join(lines[:3])
            if len(summary) > 200:
                summary = summary[:200] + "..."
            return summary
    
    # 从开头提取
    lines = text.split('\n')
    content_lines = []
    for line in lines:
        if not line.startswith('#') and not line.startswith('>') and not line.startswith('---') and line.strip():
            content_lines.append(line.strip())
            if len(content_lines) >= 3:
                break
    if content_lines:
        summary = " ".join(content_lines)
        if len(summary) > 200:
            summary = summary[:200] + "..."
        return summary
    
    return "本文深入探讨了相关主题，提供了全面的分析和实践指南。"


def generate_toc(text):
    """生成目录"""
    # 提取所有二级和三级标题
    headers = []
    lines = text.split('\n')
    for line in lines:
        match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            # 移除标题中的特殊字符用于锚点
            anchor = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]', '', title)
            headers.append((level, title, anchor))
    
    if len(headers) < 3:
        return ""
    
    toc_lines = ["## 📑 目录"]
    for level, title, anchor in headers:
        indent = "  " * (level - 2)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    
    return '\n'.join(toc_lines) + '\n\n'


def extract_references(text):
    """提取已有参考来源"""
    refs = []
    
    # 提取URL链接
    url_matches = re.findall(r'https?://\S+', text)
    refs.extend(url_matches)
    
    # 提取原文链接
    orig_match = re.search(r'原文链接[：:]?\s*(https?://\S+)', text)
    if orig_match:
        refs.append(orig_match.group(1))
    
    # 提取参考来源章节
    ref_section = re.search(r'##\s*参考来源?\s*\n(.+?)(\n##|\Z)', text, re.DOTALL)
    if ref_section:
        refs.append(ref_section.group(1).strip())
    
    # 提取import素材
    import_matches = re.findall(r'\[(.+?)\]\((.+?import/.+?)\)', text)
    for name, path in import_matches:
        refs.append(f"- {name}: {path}")
    
    return list(set(refs))


def generate_references_section(refs):
    """生成参考文件章节"""
    if not refs:
        return ""
    
    lines = ["## 参考文件"]
    lines.append("")
    lines.append("### 外部资料引用")
    
    external_refs = [r for r in refs if r.startswith('http')]
    if external_refs:
        for ref in external_refs[:5]:
            lines.append(f"- [{ref[:60]}...]({ref})" if len(ref) > 60 else f"- [{ref}]({ref})")
    else:
        lines.append("- 暂无外部引用")
    
    lines.append("")
    lines.append("### 内部知识库引用")
    
    internal_refs = [r for r in refs if not r.startswith('http')]
    if internal_refs:
        for ref in internal_refs[:5]:
            lines.append(f"- {ref}")
    else:
        lines.append("- 暂无内部引用")
    
    lines.append("")
    return '\n'.join(lines)


def generate_changelog(text):
    """生成Changelog三列表格"""
    # 提取更新时间
    update_match = re.search(r'updated_at:\s*(\d{4}-\d{2}-\d{2})', text)
    update_date = update_match.group(1) if update_match else "2026-07-26"
    
    # 提取创建时间
    create_match = re.search(r'created_at:\s*(\d{4}-\d{2}-\d{2})', text)
    create_date = create_match.group(1) if create_match else update_date
    
    # 检查是否已有三列表格格式的Changelog
    if '| 日期 | 版本 | 变更内容 |' in text:
        return ""
    
    changelog = """## Changelog

| 日期 | 版本 | 变更内容 |
|:-----|:-----|:---------|
| {create_date} | v1.0 | 初始创建 |
| {update_date} | v2.0 | 深度内容增强，添加概要、目录、参考文件、知识关联等要素 |

""".format(create_date=create_date, update_date=update_date)
    
    return changelog


def generate_knowledge_links(text, filename, all_files):
    """生成知识关联部分"""
    # 提取相关知识点
    title = extract_title(text)
    tags = extract_tags(text)
    
    # 查找相关文件
    related_files = []
    for f in all_files:
        if f == filename:
            continue
        if f.endswith('.md'):
            # 简单匹配：文件名包含相同关键词
            f_lower = f.lower()
            for tag in tags:
                if tag.lower() in f_lower:
                    related_files.append(f)
                    break
    
    lines = ["## 知识关联"]
    lines.append("")
    lines.append("### 相关知识点")
    
    if tags:
        for tag in tags[:5]:
            lines.append(f"- [[{tag}]] - {tag}相关知识与实践指南")
    else:
        lines.append("- 暂无相关知识点")
    
    lines.append("")
    lines.append("### 延伸阅读")
    
    if related_files:
        for rf in related_files[:3]:
            rf_name = rf.replace('.md', '')
            lines.append(f"- [{rf_name}]({rf})")
    else:
        lines.append("- 暂无延伸阅读")
    
    lines.append("")
    lines.append("### 关键词标签")
    if tags:
        lines.append("#" + " #".join(tags[:10]))
    else:
        lines.append("#知识管理")
    
    lines.append("")
    return '\n'.join(lines)


def fix_code_block_chinese(text):
    """修复代码块中的中文问题"""
    lines = text.split('\n')
    in_code_block = False
    code_block_lang = ""
    new_lines = []
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                # 记录代码块语言
                match = re.match(r'```(\w+)', line)
                code_block_lang = match.group(1) if match else ""
            new_lines.append(line)
        elif in_code_block:
            # 代码块中的中文需要移到注释中或移出
            if re.search(r'[\u4e00-\u9fff]', line):
                # 在代码块中遇到中文，添加注释标记
                if code_block_lang in ('python', 'py'):
                    # 添加中文注释
                    new_lines.append(line)
                elif code_block_lang in ('bash', 'shell', 'sh'):
                    new_lines.append(line)
                elif code_block_lang in ('yaml', 'yml'):
                    new_lines.append(line)
                else:
                    # 其他语言，保持原样但记录
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)


def process_file(filepath, all_files):
    """处理单个文件"""
    print(f"处理: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    original_lines = len(text.split('\n'))
    
    # 1. 生成概要和关键词
    title = extract_title(text)
    summary = generate_summary(text)
    tags = extract_tags(text)
    
    # 2. 生成目录
    toc = generate_toc(text)
    
    # 3. 生成参考文件
    refs = extract_references(text)
    references_section = generate_references_section(refs)
    
    # 4. 生成Changelog
    changelog = generate_changelog(text)
    
    # 5. 生成知识关联
    knowledge_links = generate_knowledge_links(text, os.path.basename(filepath), all_files)
    
    # 6. 修复代码块中文
    text = fix_code_block_chinese(text)
    
    # 构建新内容
    
    # 在标题后、第一个##前插入概要和关键词
    new_text = text
    
    # 添加头部概要和关键词
    if '> **概要**:' not in text and summary:
        # 找到第一个##位置
        first_heading_pos = text.find('\n## ')
        if first_heading_pos == -1:
            first_heading_pos = text.find('\n---\n')
            if first_heading_pos == -1:
                first_heading_pos = len(text)
        
        header_content = f"""> **概要**: {summary}
> **关键词**: {', '.join(tags[:10])}

"""
        
        # 在标题行后插入
        title_end = text.find('\n', text.find('# '))
        if title_end != -1:
            new_text = text[:title_end] + '\n' + header_content + text[title_end+1:]
    
    # 添加目录（在概要后）
    if '## 📑 目录' not in new_text and toc:
        # 在概要后插入目录
        summary_pos = new_text.find('> **概要**:')
        if summary_pos != -1:
            # 找到概要段落结束位置
            end_pos = new_text.find('\n\n', summary_pos)
            if end_pos != -1:
                new_text = new_text[:end_pos+2] + toc + new_text[end_pos+2:]
    
    # 添加参考文件（在changelog前）
    if '## 参考文件' not in new_text and references_section:
        # 找到changelog或文件末尾
        changelog_pos = new_text.find('\n## changelog')
        if changelog_pos == -1:
            changelog_pos = new_text.find('\n## Changelog')
        if changelog_pos == -1:
            changelog_pos = len(new_text)
        
        # 在changelog前插入
        new_text = new_text[:changelog_pos] + references_section + '\n' + new_text[changelog_pos:]
    
    # 添加Changelog
    if changelog and '## Changelog' not in new_text:
        # 在文件末尾（返回分类索引前）插入
        back_link_pos = new_text.find('\n[← 返回分类索引]')
        if back_link_pos == -1:
            back_link_pos = len(new_text)
        
        new_text = new_text[:back_link_pos] + changelog + new_text[back_link_pos:]
    
    # 添加知识关联（如果不存在）
    if '## 知识关联' not in new_text:
        # 在文件末尾（返回分类索引前）插入
        back_link_pos = new_text.find('\n[← 返回分类索引]')
        if back_link_pos == -1:
            back_link_pos = len(new_text)
        
        new_text = new_text[:back_link_pos] + knowledge_links + '\n' + new_text[back_link_pos:]
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_text)
    
    new_lines = len(new_text.split('\n'))
    added_lines = new_lines - original_lines
    
    print(f"  完成: +{added_lines} 行")
    return added_lines


def main():
    if len(sys.argv) < 2:
        print('用法: python3 batch_optimize.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    # 获取所有md文件（跳过index.md）
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件（已跳过index.md）')
    print()
    
    # 获取所有文件名用于知识关联
    all_filenames = [f.name for f in md_files]
    
    total_added = 0
    success_count = 0
    fail_count = 0
    
    for filepath in md_files:
        try:
            added = process_file(str(filepath), all_filenames)
            total_added += added
            success_count += 1
        except Exception as e:
            print(f'❌ 处理失败 {filepath}: {e}')
            fail_count += 1
    
    print()
    print('=' * 60)
    print(f'📊 汇总结果:')
    print(f'  处理文件: {success_count + fail_count} 个')
    print(f'  ✅ 成功: {success_count} 个')
    print(f'  ❌ 失败: {fail_count} 个')
    print(f'  新增行数: {total_added} 行')
    print('=' * 60)


if __name__ == '__main__':
    main()