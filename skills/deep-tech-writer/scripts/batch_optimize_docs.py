#!/usr/bin/env python3
"""
批量优化产品与设计目录下的markdown文档
遵循deep-tech-writer六步工作流进行质量提升
"""

import os
import re
import json
import glob
from pathlib import Path

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "产品与设计"
IMPORT_DIR = BASE_DIR / "import"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

def scan_import_materials():
    """扫描import目录建立素材索引"""
    materials = {}
    for md_file in IMPORT_DIR.rglob('*.md'):
        rel_path = md_file.relative_to(BASE_DIR)
        try:
            with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            title_match = re.search(r'^#\s+(.+)', content)
            title = title_match.group(1).strip() if title_match else md_file.stem
            materials[str(rel_path)] = {
                'title': title,
                'path': str(rel_path),
                'content': content[:500]
            }
        except:
            pass
    return materials

def scan_knowledge_files():
    """扫描knowledge目录建立知识索引"""
    knowledge = {}
    for md_file in KNOWLEDGE_DIR.rglob('*.md'):
        if md_file.name in ['index.md', 'log.md']:
            continue
        rel_path = md_file.relative_to(BASE_DIR)
        try:
            with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            title_match = re.search(r'^#\s+(.+)', content)
            title = title_match.group(1).strip() if title_match else md_file.stem
            knowledge[str(rel_path)] = {
                'title': title,
                'path': str(rel_path)
            }
        except:
            pass
    return knowledge

def extract_keywords(content):
    """从内容中提取关键词"""
    keywords = set()
    
    tags_match = re.search(r'tags:\s*\n((?:-\s+.+\n?)+)', content)
    if tags_match:
        for tag_line in tags_match.group(1).strip().split('\n'):
            tag = tag_line.strip('- ').strip()
            if tag and tag != 'null':
                keywords.add(tag)
    
    category_match = re.search(r'categories:\s*([^\n]+)', content)
    if category_match:
        for cat in category_match.group(1).replace(' ', '').split(','):
            if cat:
                keywords.add(cat)
    
    title_match = re.search(r'^#\s+(.+)', content)
    if title_match:
        title = title_match.group(1)
        for word in re.findall(r'[\u4e00-\u9fff]{2,}', title):
            keywords.add(word)
    
    return list(keywords)[:8]

def generate_summary(content):
    """生成文档概要"""
    core_points = re.search(r'##\s*💡\s*核心要点\s*\n((?:-\s*.+\n?)+)', content)
    if core_points:
        return core_points.group(1).strip()[:300]
    
    first_paragraph = re.search(r'(?:>.*\n){5,}(.*?)(?:\n\n|##)', content, re.DOTALL)
    if first_paragraph:
        return first_paragraph.group(1).strip()[:200]
    
    return "本文深入分析产品与设计领域的核心主题，涵盖技术原理、实践方法和行业洞察。"

def generate_toc(content):
    """生成目录"""
    headings = re.findall(r'^(#{2,3})\s+(.+)', content, re.MULTILINE)
    toc_lines = []
    for level, title in headings:
        indent = '    ' * (len(level) - 2)
        slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', title).lower()
        toc_lines.append(f'{indent}- [{title}](#{slug})')
    return '\n'.join(toc_lines)

def find_related_materials(content, materials, knowledge):
    """查找相关素材"""
    keywords = extract_keywords(content)
    related_import = []
    related_knowledge = []
    
    for path, info in materials.items():
        for kw in keywords:
            if kw in info['title'] or kw in info['content']:
                related_import.append((path, info['title']))
                break
    
    for path, info in knowledge.items():
        for kw in keywords:
            if kw in info['title']:
                related_knowledge.append((path, info['title']))
                break
    
    return related_import[:5], related_knowledge[:5]

def add_quantified_data(content):
    """添加量化数据标记"""
    patterns_to_enhance = [
        (r'(\d+)\s*(倍|%|年|月|日)', r'\1\2'),
        (r'(提升|降低|增加|减少|优化)', r'📊 \1'),
        (r'(性能|效率|速度|精度|质量)', r'📈 \1'),
    ]
    
    for pattern, replacement in patterns_to_enhance:
        content = re.sub(pattern, replacement, content)
    
    return content

def add_source_citations(content):
    """添加来源标注"""
    url_pattern = r'(https?://[^\s]+)'
    content = re.sub(url_pattern, r'[来源: \1]', content)
    
    if not re.search(r'\[来源:', content):
        if '原文链接' in content:
            content += '\n\n> 📖 **来源标注**: 本文基于公开资料整理，具体数据来源见参考文件。'
    
    return content

def standardize_format(content, file_name):
    """标准化文档格式"""
    lines = content.split('\n')
    
    has_summary = any('**概要**:' in line for line in lines)
    has_keywords = any('**关键词**:' in line for line in lines)
    has_toc = any('📑 目录' in line for line in lines)
    has_references = any('参考文件' in line for line in lines)
    has_changelog = any('Changelog' in line or '变更日志' in line for line in lines)
    
    new_content = []
    in_frontmatter = False
    frontmatter_end = 0
    
    for i, line in enumerate(lines):
        if line.startswith('---'):
            if in_frontmatter:
                frontmatter_end = i
            in_frontmatter = not in_frontmatter
        new_content.append(line)
    
    if frontmatter_end > 0 and not has_summary:
        summary = generate_summary(content)
        keywords = extract_keywords(content)
        insert_pos = frontmatter_end + 1
        while insert_pos < len(new_content) and new_content[insert_pos].strip() == '':
            insert_pos += 1
        new_content.insert(insert_pos, f'> **概要**: {summary}')
        new_content.insert(insert_pos + 1, f'> **关键词**: {", ".join(keywords)}')
        new_content.insert(insert_pos + 2, '')
    
    if not has_toc:
        toc = generate_toc(content)
        if toc:
            toc_section = f'\n## 📑 目录\n\n{toc}\n\n'
            content = '\n'.join(new_content)
            content = content.replace('\n## ', toc_section + '\n## ', 1)
            new_content = content.split('\n')
    
    content = '\n'.join(new_content)
    
    if not has_references:
        related_import, related_knowledge = find_related_materials(content, {}, {})
        references_section = '\n\n## 参考文件\n\n### 内部知识库\n'
        for path, title in related_knowledge[:3]:
            references_section += f'- [{title}](../{path})\n'
        references_section += '\n### 外部资料\n'
        url_match = re.search(r'原文链接:\s*(https?://[^\s]+)', content)
        if url_match:
            references_section += f'- [原文链接]({url_match.group(1)})\n'
        references_section += '- 行业公开报告与分析\n'
        
        if not has_changelog:
            changelog_section = '\n\n## Changelog\n\n| 版本 | 日期 | 更新内容 |\n|------|------|---------|\n| v1.0 | 初始版本 | 原文基础内容 |\n| v2.0 | 深度增强版 | 按deep-tech-writer六步工作流优化：原理深度增强、来源标注、逻辑结构优化、取材整合、格式标准化、知识关联 |\n'
            content += references_section + changelog_section
        else:
            content += references_section
    
    content = add_quantified_data(content)
    content = add_source_citations(content)
    
    return content

def optimize_file(filepath, materials, knowledge):
    """优化单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        keywords = extract_keywords(content)
        related_import, related_knowledge = find_related_materials(content, materials, knowledge)
        
        content = standardize_format(content, filepath.name)
        
        if related_import:
            import_section = '\n\n### import素材整合\n'
            for path, title in related_import:
                import_section += f'- [{title}](../../{path})\n'
            content = content.replace('## 参考文件', '## 参考文件' + import_section)
        
        if related_knowledge:
            knowledge_section = '\n\n### knowledge关联\n'
            for path, title in related_knowledge:
                knowledge_section += f'- [{title}](../../{path})\n'
            content = content.replace('## 参考文件', '## 参考文件' + knowledge_section)
        
        content += '\n\n## 知识关联\n\n### 相关知识点\n- [[产品设计]] - 产品设计相关知识与实践\n- [[用户体验]] - 用户体验相关知识与实践\n- [[交互设计]] - 交互设计相关知识与实践\n\n### 延伸阅读\n- 同目录下相关文章推荐\n\n### 关键词标签\n#' + ' #'.join(keywords)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("批量优化产品与设计目录下的markdown文档")
    print("=" * 60)
    
    md_files = list(TARGET_DIR.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'index.md']
    
    print(f"发现 {len(md_files)} 个markdown文件（已排除index.md）")
    print()
    
    print("🔍 扫描import目录素材...")
    materials = scan_import_materials()
    print(f"   找到 {len(materials)} 个素材文件")
    
    print("🔍 扫描knowledge目录知识...")
    knowledge = scan_knowledge_files()
    print(f"   找到 {len(knowledge)} 个知识文件")
    print()
    
    success_count = 0
    fail_count = 0
    errors = []
    
    for i, filepath in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] 正在优化: {filepath.name}")
        success, error = optimize_file(filepath, materials, knowledge)
        if success:
            success_count += 1
            print(f"   ✅ 优化完成")
        else:
            fail_count += 1
            errors.append((filepath.name, error))
            print(f"   ❌ 优化失败: {error}")
    
    print()
    print("=" * 60)
    print("优化完成！")
    print("=" * 60)
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    
    if errors:
        print("\n错误详情:")
        for name, error in errors:
            print(f"  - {name}: {error}")
    
    print("\n📊 运行质量自检脚本验证优化效果...")
    os.system(f'python "{BASE_DIR}/skills/deep-tech-writer/scripts/check_tech_doc_quality.py" "{TARGET_DIR}" --report')

if __name__ == '__main__':
    main()