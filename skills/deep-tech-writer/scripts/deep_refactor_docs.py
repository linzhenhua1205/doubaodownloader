#!/usr/bin/env python3
"""
深度重构 markdown 文档 - 基于 deep-tech-writer 六步工作流

核心重构功能：
1. 清理重复内容 - 删除重复的H1标题和模板化垃圾内容
2. 重写高质量概要 - 基于正文核心内容生成一句话概要
3. 重写高质量关键词 - 提取3-5个核心关键词
4. 重构内容结构 - 合并重复章节，优化章节标题命名
5. 标准化格式 - 统一的头部、目录、尾部结构
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime


TEMPLATE_SECTION_MARKERS = [
    '📋 快速导读',
    '💡 核心要点',
    '🌐 背景与上下文',
    '🔍 深度解读',
    '🆕 2025-2026 最新进展',
    '📚 相关技术资源',
    '📖 延伸阅读',
    '📝 参考来源',
    '📎 相关素材',
    '🔗 相关文章',
    '🔗 知识关联',
    '知识关联',
    '参考文件',
    'Changelog',
    'changelog',
    '📑 目录',
]

TEMPLATE_HEADING_PATTERNS = [
    r'^##\s*📋\s*快速导读',
    r'^##\s*💡\s*核心要点',
    r'^##\s*🌐\s*背景与上下文',
    r'^##\s*🔍\s*深度解读',
    r'^##\s*🆕\s*2025-2026',
    r'^##\s*📚\s*相关技术资源',
    r'^##\s*📖\s*延伸阅读',
    r'^##\s*📝\s*参考来源',
    r'^##\s*📎\s*相关素材',
    r'^##\s*🔗\s*相关文章',
    r'^##\s*🔗\s*知识关联',
    r'^##\s*知识关联',
    r'^##\s*参考文件',
    r'^##\s*Changelog',
    r'^##\s*changelog',
    r'^##\s*📑\s*目录',
]


def extract_yaml_frontmatter(text):
    """提取 YAML frontmatter，返回 (frontmatter内容, 结束位置)"""
    if not text.startswith('---\n'):
        return "", 0
    
    end_pos = text.find('\n---\n', 4)
    if end_pos == -1:
        return "", 0
    
    fm = text[4:end_pos]
    return fm, end_pos + 5


def extract_title_from_frontmatter(fm):
    """从 YAML frontmatter 提取标题"""
    for line in fm.split('\n'):
        if line.startswith('title:'):
            return line[6:].strip()
    return ""


def extract_created_at(fm):
    """从 YAML frontmatter 提取创建日期"""
    for line in fm.split('\n'):
        if line.startswith('created_at:'):
            match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if match:
                return match.group(1)
    return "2026-01-01"


def is_template_heading(heading_text):
    """判断一个二级标题是否是模板章节"""
    for pattern in TEMPLATE_HEADING_PATTERNS:
        if re.match(pattern, heading_text):
            return True
    return False


def parse_sections(text):
    """
    解析 markdown 文本为章节列表
    返回: [(heading_line, heading_text, section_content), ...]
    其中第一部分是前置内容（第一个##之前的内容）
    """
    lines = text.split('\n')
    sections = []
    current_heading = None
    current_heading_line = ""
    current_content = []
    
    preamble_lines = []
    found_first_h2 = False
    
    for line in lines:
        if line.startswith('## '):
            if not found_first_h2:
                found_first_h2 = True
                sections.append(("", "", '\n'.join(preamble_lines)))
            
            if current_heading is not None:
                sections.append((current_heading_line, current_heading, '\n'.join(current_content)))
            
            current_heading_line = line
            current_heading = line[3:].strip()
            current_content = []
        else:
            if not found_first_h2:
                preamble_lines.append(line)
            else:
                current_content.append(line)
    
    if current_heading is not None:
        sections.append((current_heading_line, current_heading, '\n'.join(current_content)))
    elif not found_first_h2:
        sections.append(("", "", '\n'.join(preamble_lines)))
    
    return sections


def filter_template_sections(sections):
    """过滤掉模板章节，只保留核心内容章节"""
    core_sections = []
    for heading_line, heading_text, content in sections:
        if heading_line == "":
            continue
        if is_template_heading(heading_line):
            continue
        core_sections.append((heading_line, heading_text, content))
    return core_sections


def extract_h3_from_content(content):
    """从章节内容中提取三级标题"""
    h3_headings = []
    for line in content.split('\n'):
        if line.startswith('### '):
            h3_text = line[4:].strip()
            h3_text = re.sub(r'^\*\*', '', h3_text)
            h3_text = re.sub(r'\*\*$', '', h3_text)
            h3_text = re.sub(r'^[一二三四五六七八九十]+、', '', h3_text)
            h3_text = re.sub(r'^\d+\.', '', h3_text)
            h3_text = re.sub(r'^\(\d+\)', '', h3_text)
            h3_text = re.sub(r'^[（(][一二三四五六七八九十]+[）)]', '', h3_text)
            h3_text = h3_text.strip()
            if h3_text:
                h3_headings.append(h3_text)
    return h3_headings


def generate_anchor(title):
    """生成 markdown 锚点"""
    anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', title)
    return anchor


def generate_toc(headings):
    """生成目录"""
    if not headings:
        return ""
    
    lines = ["## 📑 目录", ""]
    for title in headings:
        anchor = generate_anchor(title)
        lines.append(f"- [{title}](#{anchor})")
    
    return '\n'.join(lines) + '\n'


def clean_title_emojis(title):
    """清理标题中的emoji"""
    return re.sub(r'[📚📝🛠️🚀📊📦🔍💡🌐🆕📋📎🔗❓🛠️📌💻🎯⚡🔥✨]', '', title).strip()


def generate_summary(title, core_sections):
    """生成高质量的一句话概要（≤100字）"""
    clean_title = clean_title_emojis(title)
    title_main = re.sub(r'[：:].*$', '', clean_title).strip()
    
    if not core_sections:
        return f"本文深入解析{title_main}技术原理与实践方法，提供系统化的技术知识指南。"
    
    section_titles = [s[1] for s in core_sections[:4]]
    
    for i, st in enumerate(section_titles):
        st_clean = clean_title_emojis(st)
        st_clean = re.sub(r'^[一二三四五六七八九十]+、', '', st_clean)
        st_clean = re.sub(r'^\d+\.', '', st_clean)
        st_clean = re.sub(r'^[（(][一二三四五六七八九十]+[）)]', '', st_clean)
        st_clean = re.sub(r'（.*?）', '', st_clean)
        st_clean = re.sub(r'\(.*?\)', '', st_clean)
        st_clean = st_clean.strip()
        section_titles[i] = st_clean
    
    section_titles = [s for s in section_titles if s]
    
    if len(section_titles) >= 3:
        aspects = "、".join(section_titles[:3])
        summary = f"本文围绕{title_main}，从{aspects}等方面进行系统解析，帮助读者掌握核心技术与实践方法。"
    elif len(section_titles) == 2:
        summary = f"本文聚焦{title_main}，从{section_titles[0]}与{section_titles[1]}两方面深入分析，提供实用的技术指导。"
    elif section_titles:
        summary = f"本文详细解析{title_main}的{section_titles[0]}，结合实例提供实用的技术方案与最佳实践。"
    else:
        summary = f"本文深入探讨{title_main}相关技术，提供全面的分析与实践指南。"
    
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary


def generate_keywords(title, core_sections):
    """生成高质量的核心关键词（3-5个，用·分隔）"""
    keywords = []
    
    clean_title = clean_title_emojis(title)
    title_main = re.sub(r'[：:].*$', '', clean_title).strip()
    
    title_words = re.findall(r'[\u4e00-\u9fffA-Za-z0-9_\+#\.]+', title_main)
    stop_words = {'详解', '深度', '解析', '指南', '介绍', '分析', '研究', '实践', '应用', 
                  '技术', '架构', '核心', '全面', '完整', '入门', '基础', '高级',
                  '最佳', '实战', '全解析', '全景', '精选', '记录', '分享', '汇总',
                  '什么是', '如何', '为什么', '的', '与', '和', '及', '及其',
                  '错误', '内部', '服务器', '解决方案'}
    
    for w in title_words:
        if len(w) >= 2 and w not in stop_words:
            keywords.append(w)
    
    for heading_line, heading_text, content in core_sections:
        h3_headings = extract_h3_from_content(content)
        for h3 in h3_headings:
            h3_clean = clean_title_emojis(h3)
            h3_clean = re.sub(r'^[一二三四五六七八九十]+、', '', h3_clean)
            h3_clean = re.sub(r'^\d+\.', '', h3_clean)
            h3_clean = re.sub(r'^[（(][一二三四五六七八九十]+[）)]', '', h3_clean)
            h3_clean = re.sub(r'（.*?）', '', h3_clean)
            h3_clean = re.sub(r'\(.*?\)', '', h3_clean)
            h3_clean = h3_clean.strip()
            words = re.findall(r'[\u4e00-\u9fffA-Za-z0-9_\+#]{2,}', h3_clean)
            for w in words:
                if w not in keywords and w not in stop_words and len(w) >= 2:
                    keywords.append(w)
                    if len(keywords) >= 5:
                        break
            if len(keywords) >= 5:
                break
        if len(keywords) >= 5:
            break
    
    if not keywords:
        keywords = [title_main[:4] if title_main else "技术"]
    
    final_keywords = keywords[:5]
    return ' · '.join(final_keywords)


def extract_external_urls(text):
    """提取外部链接"""
    urls = re.findall(r'https?://[^\s\)\]\>]+', text)
    return list(dict.fromkeys(urls))


def generate_references_section(urls):
    """生成参考文件章节"""
    lines = ["## 参考文件", ""]
    lines.append("### 外部资料引用")
    lines.append("")
    
    if urls:
        for url in urls[:5]:
            display = url[:50] + "..." if len(url) > 50 else url
            lines.append(f"- [{display}]({url})")
    else:
        lines.append("- 暂无外部引用")
    
    lines.append("")
    return '\n'.join(lines)


def generate_changelog(create_date):
    """生成 Changelog 三列表格"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    return f"""## Changelog

| 日期 | 版本 | 变更内容 |
|:-----|:-----|:---------|
| {create_date} | v1.0 | 初始创建 |
| {today} | v2.0 | 深度重构：清理重复内容、优化概要关键词、重构内容结构、标准化格式 |

"""


def remove_h1_from_body(text):
    """删除正文中的H1标题（第一个#开头的行）"""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# '):
            del lines[i]
            return '\n'.join(lines)
    return text


def remove_meta_blockquotes(text):
    """删除正文中的元信息引用块（发布时间、分类、原文链接等）"""
    lines = text.split('\n')
    new_lines = []
    
    meta_patterns = [
        r'^>\s*📅',
        r'^>\s*🏷️',
        r'^>\s*🔗',
        r'^>\s*📝',
        r'^>\s*⭐',
        r'^>\s*🔄',
    ]
    
    for line in lines:
        is_meta = False
        for pat in meta_patterns:
            if re.match(pat, line):
                is_meta = True
                break
        if not is_meta:
            new_lines.append(line)
    
    return '\n'.join(new_lines)


def clean_empty_lines(text):
    """清理多余空行和残留分割线"""
    lines = text.split('\n')
    result = []
    empty_count = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped == '':
            empty_count += 1
            if empty_count <= 2:
                result.append(line)
        elif re.match(r'^[-=*_]{3,}\s*$', stripped):
            continue
        else:
            empty_count = 0
            result.append(line)
    
    return '\n'.join(result)


def promote_h3_to_h2_in_content_section(heading_text, content):
    """
    如果章节标题是"内容"之类的泛化标题，将其下的三级标题提升为二级标题
    返回: (新的二级标题列表, 新的内容列表)
    """
    generic_names = {'内容', '正文', '主要内容', '核心内容'}
    
    if heading_text not in generic_names:
        return None
    
    h3_headings = []
    segments = []
    current_h3 = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('### '):
            if current_h3 is not None:
                segments.append((current_h3, '\n'.join(current_content)))
            h3_text = line[4:].strip()
            h3_text = re.sub(r'^\*\*', '', h3_text)
            h3_text = re.sub(r'\*\*$', '', h3_text)
            current_h3 = h3_text
            current_content = []
        else:
            if current_h3 is not None:
                current_content.append(line)
    
    if current_h3 is not None:
        segments.append((current_h3, '\n'.join(current_content)))
    
    if segments:
        return segments
    
    return None


def process_file(filepath):
    """处理单个文件"""
    print(f"\n处理: {filepath.name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    original_lines = len(original_text.split('\n'))
    
    fm, fm_end = extract_yaml_frontmatter(original_text)
    
    if not fm:
        print(f"  ⚠️  无 YAML frontmatter，跳过")
        return False, 0
    
    title = extract_title_from_frontmatter(fm)
    create_date = extract_created_at(fm)
    
    if not title:
        print(f"  ⚠️  无标题，跳过")
        return False, 0
    
    body = original_text[fm_end:]
    
    body = remove_h1_from_body(body)
    
    body = remove_meta_blockquotes(body)
    
    sections = parse_sections(body)
    
    core_sections_raw = filter_template_sections(sections)
    
    final_sections = []
    for heading_line, heading_text, content in core_sections_raw:
        promoted = promote_h3_to_h2_in_content_section(heading_text, content)
        if promoted:
            for h3_title, h3_content in promoted:
                final_sections.append((f"## {h3_title}", h3_title, h3_content))
        else:
            clean_heading = clean_title_emojis(heading_text)
            clean_heading = re.sub(r'^[一二三四五六七八九十]+、', '', clean_heading)
            clean_heading = re.sub(r'^\d+\.', '', clean_heading).strip()
            final_sections.append((f"## {clean_heading}", clean_heading, content))
    
    all_urls = extract_external_urls(body)
    
    summary = generate_summary(title, final_sections)
    keywords = generate_keywords(title, final_sections)
    
    section_titles = [s[1] for s in final_sections]
    toc = generate_toc(section_titles)
    
    references = generate_references_section(all_urls)
    changelog = generate_changelog(create_date)
    
    output_parts = []
    
    output_parts.append(f"# {title}")
    output_parts.append("")
    output_parts.append(f"> **概要**: {summary}")
    output_parts.append(f"> **关键词**: {keywords}")
    output_parts.append("")
    
    if toc:
        output_parts.append(toc)
        output_parts.append("")
    
    for heading_line, heading_text, content in final_sections:
        output_parts.append(heading_line)
        output_parts.append("")
        content_clean = content.strip()
        if content_clean:
            output_parts.append(content_clean)
            output_parts.append("")
    
    output_parts.append(references)
    output_parts.append("")
    output_parts.append(changelog)
    
    final_body = '\n'.join(output_parts)
    final_body = clean_empty_lines(final_body)
    
    final_text = f"---\n{fm}\n---\n\n{final_body}"
    
    if not final_text.endswith('\n'):
        final_text += '\n'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    new_lines = len(final_text.split('\n'))
    line_diff = new_lines - original_lines
    
    print(f"  ✅ 完成 (行数: {original_lines} → {new_lines}, 变化: {line_diff:+d})")
    print(f"  📝 概要: {summary}")
    print(f"  🏷️  关键词: {keywords}")
    print(f"  📑 核心章节: {len(final_sections)} 个")
    
    return True, line_diff


def main():
    if len(sys.argv) < 2:
        print('用法: python3 deep_refactor_docs.py <文件路径或目录路径>')
        sys.exit(1)
    
    target = sys.argv[1]
    
    if not os.path.exists(target):
        print(f'❌ 路径不存在: {target}')
        sys.exit(1)
    
    if os.path.isfile(target):
        md_files = [Path(target)]
    else:
        md_files = sorted([f for f in Path(target).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件')
    print(f'📋 开始深度重构...')
    print('=' * 60)
    
    success_count = 0
    fail_count = 0
    total_line_diff = 0
    
    for filepath in md_files:
        try:
            success, line_diff = process_file(filepath)
            if success:
                success_count += 1
                total_line_diff += line_diff
            else:
                fail_count += 1
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
    
    print()
    print('=' * 60)
    print('📊 深度重构完成统计:')
    print(f'  总文件数: {len(md_files)} 个')
    print(f'  ✅ 成功: {success_count} 个')
    print(f'  ❌ 失败: {fail_count} 个')
    print(f'  📏 总行数变化: {total_line_diff:+d} 行')
    print('=' * 60)


if __name__ == '__main__':
    main()
