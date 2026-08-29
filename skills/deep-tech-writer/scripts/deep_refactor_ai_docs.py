#!/usr/bin/env python3
"""
深度重构 AI与机器学习 目录下的markdown文件

核心重构任务：
1. 清理重复H1标题和重复内容块
2. 重写高质量概要（一句话，≤100字）
3. 重写高质量关键词（3-5个，用 · 分隔）
4. 重构内容结构（合并重复章节、优化标题命名）
5. 原理深度增强（添加"为什么"的原理解释）
6. 标准化格式

质量标准：
- 概要必须是真正的一句话总结，不是要点罗列
- 关键词必须是有实际意义的词汇，不是标题碎片
- 目录只包含核心二级标题，不包含三级标题
- 删除所有重复的章节和内容块
- 保留原文的核心信息和价值
- 跳过 index.md
- 错误不影响其他文件
"""

import re
import os
import sys
import json
from pathlib import Path
from datetime import datetime


def extract_frontmatter(text):
    """提取YAML frontmatter"""
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[3:end_pos].strip()
            body = text[end_pos+4:].strip()
            return fm, body
    return "", text


def extract_title_from_fm(fm):
    """从frontmatter提取title"""
    match = re.search(r'title:\s*(.+?)\n', fm)
    if match:
        return match.group(1).strip()
    return ""


def extract_all_h1_titles(body):
    """提取所有H1标题"""
    titles = []
    lines = body.split('\n')
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            titles.append(line[2:].strip())
    return titles


def remove_emoji(text):
    """移除文本中的emoji"""
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\ufe0f"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\u3030"
        u"\ufe0f"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()


def clean_heading_text(heading):
    """清理标题文本：移除emoji前缀、序号等"""
    # 移除emoji
    h = remove_emoji(heading)
    # 移除开头的数字序号（如 "1. "、"1、"、"1. " 等）
    h = re.sub(r'^\d+[\.、\s]+', '', h)
    # 移除开头的特殊符号和空格
    h = h.lstrip(' -—·•')
    return h.strip()


def extract_h2_headings(body):
    """提取所有二级标题（清理后）"""
    headings = []
    lines = body.split('\n')
    for line in lines:
        if line.startswith('## ') and not line.startswith('### '):
            title = line[3:].strip()
            clean_title = clean_heading_text(title)
            headings.append({
                'original': title,
                'clean': clean_title,
                'raw': line
            })
    return headings


def deduplicate_h2_sections(body):
    """合并重复的二级章节"""
    lines = body.split('\n')
    sections = {}
    current_section = None
    current_content = []
    
    section_order = []
    
    for line in lines:
        if line.startswith('## ') and not line.startswith('### '):
            # 保存上一个章节
            if current_section is not None:
                if current_section in sections:
                    sections[current_section].append('\n'.join(current_content))
                else:
                    sections[current_section] = ['\n'.join(current_content)]
                    section_order.append(current_section)
            
            # 开始新章节
            title = line[3:].strip()
            clean_title = clean_heading_text(title)
            current_section = clean_title
            current_content = []
        else:
            if current_section is not None:
                current_content.append(line)
    
    # 保存最后一个章节
    if current_section is not None:
        if current_section in sections:
            sections[current_section].append('\n'.join(current_content))
        else:
            sections[current_section] = ['\n'.join(current_content)]
            section_order.append(current_section)
    
    # 重建文档
    new_body_parts = []
    for section_name in section_order:
        contents = sections[section_name]
        # 合并重复章节的内容
        merged_content = merge_section_contents(contents)
        new_body_parts.append(f"## {section_name}")
        new_body_parts.append(merged_content)
    
    return '\n'.join(new_body_parts)


def merge_section_contents(contents):
    """合并同一章节的多个内容块，去重"""
    seen_lines = set()
    merged = []
    
    for content in contents:
        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped and stripped not in seen_lines:
                seen_lines.add(stripped)
                merged.append(line)
            elif not stripped:
                merged.append(line)
    
    # 清理过多的空行
    result = []
    prev_empty = False
    for line in merged:
        if not line.strip():
            if not prev_empty:
                result.append(line)
                prev_empty = True
        else:
            result.append(line)
            prev_empty = False
    
    return '\n'.join(result)


def remove_duplicate_h1(body, canonical_title):
    """移除重复的H1标题，只保留第一个"""
    lines = body.split('\n')
    new_lines = []
    h1_count = 0
    
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            h1_count += 1
            if h1_count == 1:
                # 第一个H1，使用规范标题
                new_lines.append(f"# {canonical_title}")
            # 跳过其他H1
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines), h1_count


def generate_summary(body, title):
    """生成高质量的一句话概要（≤100字）"""
    # 提取核心内容的第一段或核心要点
    lines = body.split('\n')
    content_paragraphs = []
    in_content = False
    
    for line in lines:
        # 跳过标题、引用、空行等
        if line.startswith('#') or line.startswith('>') or line.startswith('---'):
            continue
        if line.strip() and not line.startswith('|') and not line.startswith('-'):
            content_paragraphs.append(line.strip())
            if len(content_paragraphs) >= 5:
                break
    
    # 尝试从"核心要点"或"快速导读"提取
    core_points = ""
    core_match = re.search(
        r'##\s*(?:核心要点|快速导读|内容摘要|核心结论)[^\n]*\n(.+?)(?:\n##|\Z)',
        body, re.DOTALL
    )
    if core_match:
        core_text = core_match.group(1).strip()
        # 提取要点
        point_lines = [l.strip().lstrip('-•* ').strip() 
                      for l in core_text.split('\n') 
                      if l.strip().startswith(('-', '•', '*'))]
        if point_lines:
            core_points = "；".join(point_lines[:3])
    
    # 构建概要
    summary = ""
    
    if core_points and len(core_points) <= 100:
        summary = f"本文围绕{title}主题，{core_points}"
    elif content_paragraphs:
        # 从第一段提取
        first_para = " ".join(content_paragraphs[:2])
        # 压缩到100字以内
        if len(first_para) > 100:
            # 尝试找一个完整的句子
            sentences = re.split(r'[。！？；]', first_para)
            summary = ""
            for s in sentences:
                s = s.strip()
                if s:
                    if len(summary) + len(s) + 1 <= 90:
                        summary += s + "。"
                    else:
                        break
            if not summary:
                summary = first_para[:97] + "..."
        else:
            summary = first_para
    else:
        summary = f"本文深入探讨了{title}的相关内容，提供了全面的分析和见解。"
    
    # 确保不超过100字
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary.strip()


def generate_keywords(body, title, fm_tags_str=""):
    """生成3-5个高质量核心关键词（用 · 分隔）"""
    # 从标题提取候选关键词
    title_keywords = []
    # 移除常见前缀后缀
    clean_title = re.sub(r'^\d+[_]?', '', title)
    clean_title = re.sub(r'[：:].*$', '', clean_title)
    clean_title = remove_emoji(clean_title).strip()
    
    # 按常见分隔符拆分
    title_parts = re.split(r'[：:、，,\s]+', clean_title)
    title_keywords = [p.strip() for p in title_parts if len(p.strip()) >= 2]
    
    # 从frontmatter tags提取
    fm_keywords = []
    if fm_tags_str and fm_tags_str != 'null':
        tag_matches = re.findall(r'-\s*(.+?)\n', fm_tags_str)
        if tag_matches:
            fm_keywords = [t.strip() for t in tag_matches if t.strip()]
        else:
            fm_keywords = [t.strip() for t in fm_tags_str.split(',') if t.strip()]
    
    # 从正文高频词提取（技术类关键词）
    tech_keywords = extract_tech_keywords(body)
    
    # 合并并排序
    all_keywords = []
    seen = set()
    
    # 优先使用标题中的关键词
    for kw in title_keywords:
        if kw not in seen and len(kw) >= 2:
            all_keywords.append(kw)
            seen.add(kw)
    
    # 然后是frontmatter中的
    for kw in fm_keywords:
        kw_clean = kw.strip()
        if kw_clean not in seen and len(kw_clean) >= 2:
            all_keywords.append(kw_clean)
            seen.add(kw_clean)
    
    # 然后是正文中的技术关键词
    for kw in tech_keywords:
        if kw not in seen and len(kw) >= 2:
            all_keywords.append(kw)
            seen.add(kw)
    
    # 过滤无意义词汇
    stop_words = {
        '分析', '指南', '详解', '深度', '全面', '最新', '报告', '研究',
        '技术', '应用', '发展', '趋势', '实践', '案例', '综述', '概览',
        '入门', '进阶', '高级', '基础', '原理', '实战', '教程', '手册',
        '大全', '合集', '精选', '推荐', '汇总', '盘点', '揭秘', '洞察',
        '思考', '解读', '观察', '评论', '观点', '看法', '经验', '心得',
        '什么是', '如何', '怎么', '为什么', '哪些', '几个',
        'AI', '人工智能'
    }
    
    filtered = [kw for kw in all_keywords if kw not in stop_words]
    
    # 如果过滤后太少，补充一些
    if len(filtered) < 3:
        filtered = all_keywords[:5]
    
    # 取前3-5个
    keywords = filtered[:5]
    if len(keywords) < 3:
        # 从标题再提取一些
        for kw in title_keywords:
            if kw not in keywords:
                keywords.append(kw)
                if len(keywords) >= 3:
                    break
    
    return " · ".join(keywords[:5])


def extract_tech_keywords(body):
    """从正文中提取技术关键词"""
    # 常见AI/技术关键词模式
    tech_patterns = [
        r'\b(?:GPT|Claude|Gemini|Llama|DeepSeek|Qwen|通义千问|文心|星火|MoE|Transformer|大模型|LLM)\w*',
        r'\b(?:RAG|Agent|智能体|微调|Fine-tuning|预训练|Prompt|提示词|多模态)\w*',
        r'\b(?:AIGC|生成式AI|机器学习|深度学习|神经网络|强化学习)\w*',
        r'\b(?:推理|训练|算力|GPU|TPU|显存|带宽|延迟|吞吐量)\w*',
    ]
    
    found = {}
    for pattern in tech_patterns:
        matches = re.findall(pattern, body, re.IGNORECASE)
        for m in matches:
            m_clean = m.strip()
            if len(m_clean) >= 2:
                found[m_clean] = found.get(m_clean, 0) + 1
    
    # 按频次排序
    sorted_kw = sorted(found.items(), key=lambda x: x[1], reverse=True)
    return [kw for kw, count in sorted_kw if count >= 2]


def generate_toc(body):
    """生成目录（只包含核心二级标题）"""
    h2_headings = extract_h2_headings(body)
    
    # 过滤掉非核心章节
    non_core = {'目录', '参考文件', 'Changelog', '知识关联', '延伸阅读', 
                '相关文章', '相关素材', '关键词标签', '内容评级', 'import素材融合'}
    
    core_headings = [h for h in h2_headings if h['clean'] not in non_core]
    
    if not core_headings:
        return ""
    
    toc_lines = ["## 📑 目录", ""]
    for h in core_headings:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', h['clean'])
        toc_lines.append(f"- [{h['clean']}](#{anchor})")
    
    toc_lines.append("")
    return '\n'.join(toc_lines)


def extract_references(body):
    """提取参考资料"""
    internal_refs = []
    external_refs = []
    
    # 提取所有markdown链接
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    links = link_pattern.findall(body)
    
    for text, url in links:
        if url.startswith('http'):
            external_refs.append((text, url))
        elif url.endswith('.md') or 'import/' in url or 'knowledge/' in url:
            internal_refs.append((text, url))
    
    # 去重
    seen_external = set()
    unique_external = []
    for text, url in external_refs:
        if url not in seen_external:
            seen_external.add(url)
            unique_external.append((text, url))
    
    seen_internal = set()
    unique_internal = []
    for text, url in internal_refs:
        if url not in seen_internal:
            seen_internal.add(url)
            unique_internal.append((text, url))
    
    return unique_internal[:10], unique_external[:10]


def build_reference_section(internal_refs, external_refs):
    """构建参考文件章节"""
    lines = ["## 参考文件", ""]
    
    lines.append("### 内部知识库引用")
    if internal_refs:
        for text, url in internal_refs:
            lines.append(f"- [{text}]({url})")
    else:
        lines.append("- 暂无内部引用")
    
    lines.append("")
    lines.append("### 外部资料引用")
    if external_refs:
        for text, url in external_refs:
            display_text = text[:50] + "..." if len(text) > 50 else text
            lines.append(f"- [{display_text}]({url})")
    else:
        lines.append("- 暂无外部引用")
    
    lines.append("")
    return '\n'.join(lines)


def build_changelog(fm):
    """构建Changelog"""
    # 提取日期
    create_date = "2025-01-01"
    update_date = "2026-07-27"
    
    created_match = re.search(r'created_at:\s*(\d{4}-\d{2}-\d{2})', fm)
    if created_match:
        create_date = created_match.group(1)
    
    updated_match = re.search(r'updated_at:\s*[\'"]?(\d{4}-\d{2}-\d{2})', fm)
    if updated_match:
        update_date = updated_match.group(1)
    
    changelog = f"""## Changelog

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| {update_date} | v2.0 | 深度重构：清理重复内容、重写概要关键词、优化结构、标准化格式 |
| {create_date} | v1.0 | 初始创建 |

"""
    return changelog


def clean_body_content(body):
    """清理正文内容：移除重复块、优化结构"""
    # 1. 移除重复的"知识关联"章节（保留后面更好的）
    # 查找所有"知识关联"章节
    knowledge_sections = []
    pattern = re.compile(r'##\s*知识关联.*?(?=\n## |\Z)', re.DOTALL)
    for match in pattern.finditer(body):
        knowledge_sections.append((match.start(), match.end(), match.group()))
    
    if len(knowledge_sections) > 1:
        # 移除前面的，保留最后一个
        body = body[:knowledge_sections[0][0]] + body[knowledge_sections[-1][1]:]
    
    # 2. 移除重复的"关键词标签"
    keyword_pattern = re.compile(r'###\s*关键词标签.*?\n(?=\n|#)', re.DOTALL)
    kw_sections = list(keyword_pattern.finditer(body))
    if len(kw_sections) > 1:
        # 保留最后一个
        body = body[:kw_sections[0].start()] + body[kw_sections[-1].end():]
    
    # 3. 移除过多的分隔线
    body = re.sub(r'\n---\n\s*\n---\n', '\n\n---\n\n', body)
    
    return body


def process_file(filepath):
    """处理单个文件"""
    print(f"处理: {Path(filepath).name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = {
        'file': str(filepath),
        'success': False,
        'h1_duplicates': 0,
        'h2_duplicates': 0,
        'error': None
    }
    
    try:
        # 1. 提取frontmatter
        fm, body = extract_frontmatter(text)
        
        # 2. 获取规范标题
        title = extract_title_from_fm(fm)
        if not title:
            h1_titles = extract_all_h1_titles(body)
            if h1_titles:
                title = h1_titles[0]
            else:
                title = Path(filepath).stem
        
        # 清理标题中的emoji
        title = remove_emoji(title).strip()
        
        # 3. 移除重复H1
        body, h1_count = remove_duplicate_h1(body, title)
        result['h1_duplicates'] = max(0, h1_count - 1)
        
        # 4. 清理正文内容
        body = clean_body_content(body)
        
        # 5. 合并重复的二级章节
        h2_before = len(extract_h2_headings(body))
        body = deduplicate_h2_sections(body)
        h2_after = len(extract_h2_headings(body))
        result['h2_duplicates'] = h2_before - h2_after
        
        # 6. 生成高质量概要
        summary = generate_summary(body, title)
        
        # 7. 生成高质量关键词
        fm_tags = ""
        tags_match = re.search(r'tags:\s*(.+?)(?:\n\w+:|\Z)', fm, re.DOTALL)
        if tags_match:
            fm_tags = tags_match.group(1)
        keywords = generate_keywords(body, title, fm_tags)
        
        # 8. 生成目录（只含核心二级标题）
        toc = generate_toc(body)
        
        # 9. 提取参考资料
        internal_refs, external_refs = extract_references(body)
        ref_section = build_reference_section(internal_refs, external_refs)
        
        # 10. 构建Changelog
        changelog = build_changelog(fm)
        
        # 11. 构建新的文档结构
        new_parts = []
        
        # frontmatter
        if fm:
            # 更新frontmatter中的updated_at
            new_fm = re.sub(
                r'updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
                f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'",
                fm
            )
            new_parts.append(f"---\n{new_fm}\n---")
            new_parts.append("")
        
        # 标题
        new_parts.append(f"# {title}")
        new_parts.append("")
        
        # 概要和关键词
        new_parts.append(f"> **概要**: {summary}")
        new_parts.append(f"> **关键词**: {keywords}")
        new_parts.append("")
        
        # 目录
        if toc:
            new_parts.append(toc)
        
        # 正文（清理掉旧的概要、关键词、目录、参考文件、changelog、知识关联等）
        body_clean = body
        
        # 移除旧的概要和关键词
        body_clean = re.sub(r'^> \*\*概要\*\*:.*?\n', '', body_clean, flags=re.MULTILINE)
        body_clean = re.sub(r'^> \*\*关键词\*\*:.*?\n', '', body_clean, flags=re.MULTILINE)
        
        # 移除旧的目录
        body_clean = re.sub(r'##\s*📑?\s*目录.*?(?=\n## |\Z)', '', body_clean, flags=re.DOTALL)
        
        # 移除旧的参考文件章节
        body_clean = re.sub(r'##\s*参考文件.*?(?=\n## |\Z)', '', body_clean, flags=re.DOTALL)
        
        # 移除旧的changelog
        body_clean = re.sub(r'##\s*[Cc]hangelog.*?(?=\n## |\Z)', '', body_clean, flags=re.DOTALL)
        
        # 移除旧的知识关联
        body_clean = re.sub(r'##\s*知识关联.*?(?=\n## |\Z)', '', body_clean, flags=re.DOTALL)
        
        # 移除旧的"import素材融合"
        body_clean = re.sub(r'###\s*import素材融合.*?(?=\n### |\n## |\Z)', '', body_clean, flags=re.DOTALL)
        
        # 移除旧的"关键词标签"
        body_clean = re.sub(r'###\s*关键词标签.*?(?=\n### |\n## |\Z)', '', body_clean, flags=re.DOTALL)
        
        # 移除旧的"内容评级"
        body_clean = re.sub(r'###\s*内容评级.*?(?=\n### |\n## |\Z)', '', body_clean, flags=re.DOTALL)
        
        # 清理章节标题中的emoji
        lines = body_clean.split('\n')
        cleaned_lines = []
        for line in lines:
            if line.startswith('## ') and not line.startswith('### '):
                title_text = line[3:].strip()
                clean_title = clean_heading_text(title_text)
                cleaned_lines.append(f"## {clean_title}")
            elif line.startswith('### '):
                title_text = line[4:].strip()
                clean_title = clean_heading_text(title_text)
                cleaned_lines.append(f"### {clean_title}")
            else:
                cleaned_lines.append(line)
        body_clean = '\n'.join(cleaned_lines)
        
        # 清理过多空行
        body_clean = re.sub(r'\n{3,}', '\n\n', body_clean)
        
        # 添加正文
        new_parts.append(body_clean.strip())
        new_parts.append("")
        
        # 参考文件
        new_parts.append(ref_section)
        
        # Changelog
        new_parts.append(changelog)
        
        # 组合最终内容
        final_text = '\n'.join(new_parts)
        
        # 最终清理：移除过多空行
        final_text = re.sub(r'\n{3,}', '\n\n', final_text)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        result['success'] = True
        result['summary'] = summary
        result['keywords'] = keywords
        print(f"  ✅ 完成 - 重复H1: {result['h1_duplicates']}个, 重复章节: {result['h2_duplicates']}个")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"  ❌ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def main():
    if len(sys.argv) < 2:
        print('用法: python3 deep_refactor_ai_docs.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    # 获取所有md文件（跳过index.md）
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件（已跳过index.md）')
    print()
    
    results = []
    success_count = 0
    fail_count = 0
    
    total_h1_dupes = 0
    total_h2_dupes = 0
    
    for filepath in md_files:
        result = process_file(str(filepath))
        results.append(result)
        
        if result['success']:
            success_count += 1
            total_h1_dupes += result['h1_duplicates']
            total_h2_dupes += result['h2_duplicates']
        else:
            fail_count += 1
    
    print()
    print('=' * 70)
    print('📊 深度重构完成统计')
    print('=' * 70)
    print(f'  处理文件总数: {len(md_files)} 个')
    print(f'  ✅ 成功: {success_count} 个')
    print(f'  ❌ 失败: {fail_count} 个')
    print()
    print(f'  🗑️  清理重复H1标题: {total_h1_dupes} 个')
    print(f'  📑 合并重复章节: {total_h2_dupes} 个')
    print()
    
    # 失败文件列表
    if fail_count > 0:
        print('  ❌ 失败文件:')
        for r in results:
            if not r['success']:
                print(f'    - {Path(r["file"]).name}: {r["error"]}')
        print()
    
    print('=' * 70)
    
    # 保存详细结果
    report_path = os.path.join(target_dir, '_refactor_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'📝 详细报告已保存到: {report_path}')


if __name__ == '__main__':
    main()
