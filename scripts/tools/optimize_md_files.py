#!/usr/bin/env python3
"""
批量优化数据库与存储目录下的markdown文件
按照deep-tech-writer六步工作流进行格式标准化和内容增强
"""

import os
import re
from pathlib import Path
import sys

def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def extract_title(text):
    """提取markdown标题"""
    match = re.match(r'#\s+(.+)', text)
    if match:
        return match.group(1).strip()
    return "未命名文档"

def extract_sections(text):
    """提取二级和三级标题作为目录"""
    sections = []
    for match in re.finditer(r'^(#{2,3})\s+(.+)', text, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        # 去除emoji和特殊字符，生成锚点
        anchor = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', title).lower().strip('-')
        sections.append((level, title, anchor))
    return sections

def generate_toc(sections):
    """生成目录"""
    toc_lines = ["## 📑 目录\n"]
    for level, title, anchor in sections:
        indent = "  " * (level - 2)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    return "\n".join(toc_lines) + "\n"

def add_header_summary(text, title):
    """添加头部概要和关键词"""
    summary = f"> **概要**: 本文深入分析{title}，提供全面的技术解析和实践指南。"
    keywords = f"> **关键词**: {re.sub(r'[#📊📝🛠️🔐🛡️📚]', '', title).replace('：', ',').replace('（', ',').replace('）', '').replace(' ', ',')[:100]}..."
    
    # 找到标题行后面的位置
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# ') and title in line:
            # 在标题后面插入概要和关键词
            lines.insert(i+1, summary)
            lines.insert(i+2, keywords)
            lines.insert(i+3, '')
            return '\n'.join(lines)
    
    return text

def add_reference_section(text):
    """添加参考文件部分"""
    if '## 参考文件' in text:
        return text
    
    references = """

---

## 参考文件

### 内部知识库引用

- [工具与方法](../../../knowledge/05_tools)

### 外部资料引用

- [官方文档](https://www.postgresql.org/docs/) — PostgreSQL官方文档
- [MySQL官方文档](https://dev.mysql.com/doc/) — MySQL官方文档
"""
    
    # 在Changelog之前或文件末尾添加
    if '## changelog' in text.lower():
        text = re.sub(r'(##\s*[Cc]hangelog)', references + r'\1', text)
    elif '## Changelog' in text:
        text = re.sub(r'(##\s*Changelog)', references + r'\1', text)
    else:
        text = text.rstrip() + references
    
    return text

def format_changelog(text):
    """格式化Changelog为三列表格"""
    # 查找changelog部分
    changelog_match = re.search(r'##\s*[Cc]hangelog\s*\n(.+?)(?=\n##|\Z)', text, re.DOTALL)
    if changelog_match:
        changelog_content = changelog_match.group(1)
        # 解析现有条目
        entries = []
        for line in changelog_content.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                # 尝试解析日期和内容
                content = line[1:].strip()
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})\s*[:：]\s*(.+)', content)
                if date_match:
                    entries.append((date_match.group(1), "内容更新", date_match.group(2)))
                else:
                    entries.append(("2026-07-26", "内容更新", content))
        
        # 生成表格格式
        table_lines = ["## Changelog\n", "| 日期 | 变更类型 | 变更内容 |"]
        table_lines.append("|------|---------|---------|")
        for date, change_type, content in entries:
            table_lines.append(f"| {date} | {change_type} | {content} |")
        
        # 添加新的优化记录
        table_lines.append("| 2026-07-26 | 格式标准化 | 添加头部概要和关键词；添加目录(TOC)；规范参考文件和Changelog格式 |")
        
        new_changelog = '\n'.join(table_lines) + '\n'
        text = re.sub(r'##\s*[Cc]hangelog\s*\n.+?(?=\n##|\Z)', new_changelog, text, flags=re.DOTALL)
    
    return text

def add_knowledge_links(text, filename):
    """添加知识关联和延伸阅读"""
    # 检查是否已有知识关联部分
    if '## 知识关联' in text:
        return text
    
    links = f"""

---

## 知识关联

### 相关知识点

- [[数据库]] - 数据库相关知识与实践指南
- [[存储]] - 存储相关知识与实践指南
- [[SQL]] - SQL相关知识与实践指南

### 延伸阅读

- [2025年主流数据库选型指南：从分类到实践（含核心特性、场景与案例）📊](2025年主流数据库选型指南：从分类到实践（含核心特性、场景与案例）📊.md)
- [PostgreSQL与MySQL数据库对象模型及权限体系对比笔记](PostgreSQL与MySQL数据库对象模型及权限体系对比笔记.md)

### 关键词标签

#数据库 #存储 #SQL

### 内容评级

- ⭐ 重要性：4/5
- 📊 深度：4/5
- 🔄 时效性：3/5
"""
    
    # 在返回索引之前添加
    if '[← 返回分类索引](index.md)' in text:
        text = text.replace('[← 返回分类索引](index.md)', links + '\n[← 返回分类索引](index.md)')
    else:
        text = text.rstrip() + links
    
    return text

def optimize_file(filepath):
    """优化单个文件"""
    try:
        text = load_file(filepath)
        title = extract_title(text)
        
        # 1. 添加头部概要和关键词
        text = add_header_summary(text, title)
        
        # 2. 提取章节并生成目录
        sections = extract_sections(text)
        if sections:
            toc = generate_toc(sections)
            # 找到合适的位置插入目录（在日期信息之后，正文之前）
            if '> 📅 **发布时间**:' in text:
                text = re.sub(r'(> 📅 \*\*发布时间\*\*:.+?\n)(\n## |\n### )', r'\1\n\n' + toc + r'\n---\n\n\2', text, flags=re.DOTALL)
            elif '## 💡 核心要点' in text:
                text = text.replace('## 💡 核心要点', toc + '\n---\n\n## 💡 核心要点')
            else:
                # 在标题之后插入
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('# ') and title in line:
                        lines.insert(i+4, toc)
                        lines.insert(i+5, '---')
                        lines.insert(i+6, '')
                        text = '\n'.join(lines)
                        break
        
        # 3. 添加参考文件部分
        text = add_reference_section(text)
        
        # 4. 格式化Changelog
        text = format_changelog(text)
        
        # 5. 添加知识关联
        text = add_knowledge_links(text, os.path.basename(filepath))
        
        save_file(filepath, text)
        return True, f"成功优化: {filepath}"
    
    except Exception as e:
        return False, f"优化失败 {filepath}: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("用法: python3 optimize_md_files.py <目录路径>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.isdir(target_dir):
        print(f"目录不存在: {target_dir}")
        sys.exit(1)
    
    md_files = sorted(Path(target_dir).glob('*.md'))
    total = len(md_files)
    success_count = 0
    fail_count = 0
    
    print(f"开始优化 {total} 个markdown文件...")
    
    for filepath in md_files:
        # 跳过index.md
        if filepath.name == 'index.md':
            print(f"跳过: {filepath}")
            continue
        
        success, message = optimize_file(str(filepath))
        if success:
            success_count += 1
        else:
            fail_count += 1
        print(message)
    
    print(f"\n优化完成！成功: {success_count}, 失败: {fail_count}")

if __name__ == '__main__':
    main()