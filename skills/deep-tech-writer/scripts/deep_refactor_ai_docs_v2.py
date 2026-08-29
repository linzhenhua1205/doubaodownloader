#!/usr/bin/env python3
"""
深度重构 AI与机器学习 目录下的markdown文件 v2

修复v1的问题：
1. 正确保留frontmatter中的标题（包括特殊字符如%）
2. 改进去重逻辑，不破坏内容结构
3. 正确生成概要和关键词
4. 保留原有章节的完整性
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
    match = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def extract_all_h1_titles(body):
    """提取所有H1标题"""
    titles = []
    lines = body.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            titles.append(stripped[2:].strip())
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


def clean_heading_for_compare(heading):
    """清理标题用于比较（移除emoji、序号、特殊符号前缀）"""
    h = remove_emoji(heading)
    h = re.sub(r'^[\s]*\d+[\.、\s]+', '', h)
    h = h.lstrip(' -—·•📋📊🔬💼⚠️🔮🛠️🔗📚📖📎💡🆕🌐📝')
    return h.strip().lower()


def get_heading_display_name(heading):
    """获取清理后的显示标题名（移除emoji前缀）"""
    h = heading.strip()
    # 移除开头的emoji和空格
    h_clean = remove_emoji(h)
    # 如果移除emoji后还有内容，用清理后的；否则用原标题
    if h_clean:
        return h_clean
    return h


def generate_summary(body, title):
    """生成高质量的一句话概要（≤100字）"""
    # 找到第一个真正的内容段落（跳过标题、目录、引用块等）
    lines = body.split('\n')
    content_paragraphs = []
    in_content = False
    skip_next = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 跳过各种标题
        if stripped.startswith('#'):
            continue
        # 跳过引用块开头的元信息
        if stripped.startswith('>'):
            continue
        # 跳过分隔线
        if stripped == '---':
            continue
        # 跳过目录
        if stripped == '## 📑 目录' or stripped == '## 目录':
            skip_next = True
            continue
        if skip_next:
            if stripped.startswith('-') or stripped.startswith('  '):
                continue
            else:
                skip_next = False
        
        # 跳过列表项
        if stripped.startswith(('- ', '* ', '• ')):
            continue
        
        # 跳过表格
        if stripped.startswith('|'):
            continue
        
        # 找到真正的段落
        if stripped and len(stripped) > 20:
            content_paragraphs.append(stripped)
            if len(content_paragraphs) >= 3:
                break
    
    # 也尝试从"核心要点"或"快速导读"提取关键信息
    core_insights = []
    
    # 查找核心要点/快速导读章节
    core_section_match = re.search(
        r'##\s*(?:📋\s*)?(?:核心要点|快速导读|内容摘要|核心结论)[^\n]*\n(.+?)(?=\n## |\Z)',
        body, re.DOTALL
    )
    if core_section_match:
        core_text = core_section_match.group(1)
        bullet_points = re.findall(r'[-*•]\s*\**([^*]+)\**', core_text)
        if not bullet_points:
            bullet_points = re.findall(r'[-*•]\s+(.+)', core_text)
        for bp in bullet_points:
            bp_clean = bp.strip()
            if bp_clean and len(bp_clean) > 10:
                core_insights.append(bp_clean)
                if len(core_insights) >= 3:
                    break
    
    # 构建概要
    summary = ""
    
    if content_paragraphs:
        first_para = content_paragraphs[0]
        # 尝试截取完整的句子
        if len(first_para) > 100:
            # 找第一个句号、感叹号、问号
            sentences = re.split(r'([。！？!?])', first_para)
            current = ""
            for i in range(0, len(sentences), 2):
                if i < len(sentences):
                    sent = sentences[i]
                    if i + 1 < len(sentences):
                        sent += sentences[i+1]
                    if len(current) + len(sent) <= 95:
                        current += sent
                    else:
                        break
            if current:
                summary = current
            else:
                summary = first_para[:97] + "..."
        else:
            summary = first_para
    elif core_insights:
        summary = f"本文介绍{title}，核心要点包括：{'；'.join(core_insights[:2])}"
    else:
        summary = f"本文围绕{title}主题展开深入分析，提供了全面的行业洞察和实践指导。"
    
    # 确保不超过100字
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary.strip()


def generate_keywords(body, title, fm):
    """生成3-5个高质量核心关键词（用 · 分隔）"""
    candidates = []
    seen = set()
    
    def add_keyword(kw):
        kw_clean = kw.strip()
        if kw_clean and len(kw_clean) >= 2 and kw_clean not in seen:
            candidates.append(kw_clean)
            seen.add(kw_clean)
    
    # 1. 从标题提取（优先）
    # 移除emoji和文件后缀
    title_clean = remove_emoji(title)
    # 按冒号、破折号等分割，取核心主题
    title_parts = re.split(r'[：:—\-｜|]', title_clean)
    for part in title_parts:
        part = part.strip()
        if part and len(part) >= 2:
            # 进一步按空格和顿号分割
            sub_parts = re.split(r'[、，,\s]+', part)
            for sp in sub_parts:
                sp = sp.strip()
                if sp and len(sp) >= 2:
                    add_keyword(sp)
    
    # 2. 从frontmatter的tags提取
    tags_match = re.search(r'^tags:\s*(.+?)(?=^\w+:|\Z)', fm, re.MULTILINE | re.DOTALL)
    if tags_match:
        tags_text = tags_match.group(1)
        tag_items = re.findall(r'-\s*(.+)', tags_text)
        if not tag_items:
            tag_items = [t.strip() for t in tags_text.split(',')]
        for t in tag_items:
            t = t.strip()
            if t and t != 'null':
                add_keyword(t)
    
    # 3. 从frontmatter的categories提取
    cats_match = re.search(r'^categories:\s*(.+?)$', fm, re.MULTILINE)
    if cats_match:
        cats = [c.strip() for c in cats_match.group(1).split(',')]
        for c in cats:
            if c and len(c) >= 2:
                add_keyword(c)
    
    # 4. 从正文提取高频技术关键词
    tech_kw_freq = {}
    tech_patterns = [
        r'(?:大模型|LLM|GPT|Claude|Gemini|Llama|DeepSeek|Qwen|通义千问|文心一言|星火|MoE|Transformer)',
        r'(?:RAG|Agent|智能体|微调|Fine-tuning|预训练|Prompt|提示词工程|多模态)',
        r'(?:AIGC|生成式AI|机器学习|深度学习|神经网络|强化学习|自然语言处理)',
        r'(?:推理算力|训练算力|GPU|TPU|显存|算力|Token|上下文)',
        r'(?:开源|闭源|企业级|私有化部署|AI编程|代码生成)',
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, body)
        for m in matches:
            m_clean = m.strip()
            if len(m_clean) >= 2:
                tech_kw_freq[m_clean] = tech_kw_freq.get(m_clean, 0) + 1
    
    # 按频次排序，添加到候选
    sorted_tech = sorted(tech_kw_freq.items(), key=lambda x: x[1], reverse=True)
    for kw, freq in sorted_tech:
        if freq >= 3:  # 至少出现3次
            add_keyword(kw)
    
    # 过滤无意义的停用词
    stop_words = {
        '分析', '指南', '详解', '深度', '全面', '最新', '报告', '研究',
        '技术', '应用', '发展', '趋势', '实践', '案例', '综述', '概览',
        '入门', '进阶', '高级', '基础', '原理', '实战', '教程', '手册',
        '大全', '合集', '精选', '推荐', '汇总', '盘点', '揭秘', '洞察',
        '思考', '解读', '观察', '评论', '观点', '看法', '经验', '心得',
        '什么是', '如何', '怎么', '为什么', '哪些', '几个',
        'AI', '人工智能', 'AI与机器学习', '行业动态', '产品与设计',
        '编程与开发', '系统与运维', '数据库',
        '核心要点', '关键数据', '阅读建议',
    }
    
    filtered = [kw for kw in candidates if kw not in stop_words and len(kw) >= 2]
    
    # 如果过滤后太少，从候选中补充
    if len(filtered) < 3:
        for kw in candidates:
            if kw not in filtered and len(kw) >= 2:
                filtered.append(kw)
                if len(filtered) >= 3:
                    break
    
    # 取前3-5个
    result_keywords = filtered[:5]
    if len(result_keywords) < 3:
        result_keywords = candidates[:5]
    
    return " · ".join(result_keywords[:5])


def extract_core_h2_headings(body):
    """提取核心二级标题（用于生成目录）"""
    lines = body.split('\n')
    headings = []
    
    # 非核心章节标题（过滤用）
    non_core_keywords = [
        '目录', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '相关知识点', '延伸阅读', '相关文章',
        '相关素材', '关键词标签', '内容评级', 'import素材融合',
        '快速导读', '核心要点',
    ]
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            # 清理用于比较
            clean_title = clean_heading_for_compare(title)
            display_title = get_heading_display_name(title)
            
            # 检查是否是非核心章节
            is_non_core = False
            for kw in non_core_keywords:
                if kw.lower() in clean_title:
                    is_non_core = True
                    break
            
            if not is_non_core and display_title:
                headings.append({
                    'display': display_title,
                    'clean': clean_title
                })
    
    return headings


def generate_toc(body):
    """生成目录（只包含核心二级标题）"""
    headings = extract_core_h2_headings(body)
    
    if not headings:
        return ""
    
    # 去重（保留第一次出现）
    seen = set()
    unique_headings = []
    for h in headings:
        if h['clean'] not in seen:
            seen.add(h['clean'])
            unique_headings.append(h)
    
    if len(unique_headings) < 3:
        return ""
    
    toc_lines = ["## 📑 目录", ""]
    for h in unique_headings:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', h['display'])
        toc_lines.append(f"- [{h['display']}](#{anchor})")
    
    toc_lines.append("")
    return '\n'.join(toc_lines)


def extract_and_clean_references(body):
    """提取参考资料，同时从正文中清除旧的参考章节"""
    internal_refs = []
    external_refs = []
    
    # 提取所有markdown链接
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    # 从全文提取链接（不删除）
    all_links = link_pattern.findall(body)
    
    for text, url in all_links:
        if url.startswith('http'):
            external_refs.append((text, url))
        elif url.endswith('.md') or 'import/' in url or 'knowledge/' in url or '../' in url:
            internal_refs.append((text, url))
    
    # 去重（按URL）
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
        for text, url in internal_refs[:8]:
            display_text = text[:60] + "..." if len(text) > 60 else text
            lines.append(f"- [{display_text}]({url})")
    else:
        lines.append("- 暂无内部引用")
    
    lines.append("")
    lines.append("### 外部资料引用")
    if external_refs:
        for text, url in external_refs[:8]:
            display_text = text[:60] + "..." if len(text) > 60 else text
            lines.append(f"- [{display_text}]({url})")
    else:
        lines.append("- 暂无外部引用")
    
    lines.append("")
    return '\n'.join(lines)


def build_changelog(fm):
    """构建Changelog"""
    create_date = "2025-01-01"
    update_date = datetime.now().strftime('%Y-%m-%d')
    
    created_match = re.search(r'^created_at:\s*(\d{4}-\d{2}-\d{2})', fm, re.MULTILINE)
    if created_match:
        create_date = created_match.group(1)
    
    changelog = f"""## Changelog

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| {update_date} | v2.0 | 深度重构：清理重复H1、合并重复章节、重写概要关键词、标准化格式 |
| {create_date} | v1.0 | 初始创建 |

"""
    return changelog


def remove_duplicate_h1_and_metadata(body, canonical_title):
    """
    移除重复的H1标题和开头的重复元信息
    返回清理后的body和重复H1数量
    """
    lines = body.split('\n')
    new_lines = []
    h1_count = 0
    meta_block_found = False
    
    # 找到第一个H1之前的所有内容（可能包含重复的元信息块）
    first_h1_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            first_h1_idx = i
            break
    
    if first_h1_idx == -1:
        return body, 0
    
    # 从第一个H1之后开始处理
    # 先添加规范的H1
    new_lines.append(f"# {canonical_title}")
    h1_count = 1
    
    # 继续处理后面的内容
    i = first_h1_idx + 1
    while i < len(lines):
        stripped = lines[i].strip()
        
        # 跳过重复的H1
        if stripped.startswith('# ') and not stripped.startswith('## '):
            h1_count += 1
            # 检查后面是否跟着元信息引用块（> 开头的几行）
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('>'):
                j += 1
            i = j
            continue
        
        new_lines.append(lines[i])
        i += 1
    
    return '\n'.join(new_lines), h1_count - 1


def remove_duplicate_h2_sections(body):
    """
    合并重复的二级章节
    返回清理后的body和移除的重复章节数
    """
    lines = body.split('\n')
    
    # 找出所有二级标题及其位置
    sections = []  # (clean_title, start_idx, end_idx, original_title)
    current_section_start = None
    current_title = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            # 保存上一个章节
            if current_title is not None:
                sections.append({
                    'clean': clean_heading_for_compare(current_title),
                    'display': get_heading_display_name(current_title),
                    'start': current_section_start,
                    'end': i - 1,
                    'original': current_title
                })
            
            current_section_start = i
            current_title = stripped[3:].strip()
    
    # 保存最后一个章节
    if current_title is not None:
        sections.append({
            'clean': clean_heading_for_compare(current_title),
            'display': get_heading_display_name(current_title),
            'start': current_section_start,
            'end': len(lines) - 1,
            'original': current_title
        })
    
    if len(sections) <= 1:
        return body, 0
    
    # 找出重复章节（clean名称相同的）
    seen = {}
    duplicates = []  # 要删除的章节索引
    first_occurrence = {}
    
    for idx, sec in enumerate(sections):
        key = sec['clean']
        if key in first_occurrence:
            duplicates.append(idx)
        else:
            first_occurrence[key] = idx
    
    if not duplicates:
        return body, 0
    
    # 构建新的行列表
    new_lines = []
    sections_to_remove = set(duplicates)
    
    prev_end = -1
    for idx, sec in enumerate(sections):
        if idx in sections_to_remove:
            continue
        
        # 添加这个章节之前的内容
        start = sec['start']
        if prev_end >= 0:
            start = prev_end + 1
        
        for i in range(start, sec['start']):
            new_lines.append(lines[i])
        
        # 添加章节标题（用清理后的显示名）
        new_lines.append(f"## {sec['display']}")
        
        # 添加章节内容
        for i in range(sec['start'] + 1, sec['end'] + 1):
            new_lines.append(lines[i])
        
        prev_end = sec['end']
    
    # 添加最后一个章节之后的内容
    if sections:
        last_sec_end = sections[-1]['end']
        for i in range(last_sec_end + 1, len(lines)):
            new_lines.append(lines[i])
    
    return '\n'.join(new_lines), len(duplicates)


def remove_trailing_sections(body):
    """
    移除末尾重复的章节（知识关联、延伸阅读等），保留最好的一份
    """
    # 需要清理的章节模式
    patterns_to_clean = [
        (r'##\s*(?:📚\s*)?延伸阅读.*?(?=\n## |\Z)', '延伸阅读'),
        (r'##\s*(?:🔗\s*)?知识关联.*?(?=\n## |\Z)', '知识关联'),
        (r'##\s*(?:📎\s*)?相关素材.*?(?=\n## |\Z)', '相关素材'),
        (r'##\s*(?:🔗\s*)?相关文章.*?(?=\n## |\Z)', '相关文章'),
    ]
    
    for pattern, name in patterns_to_clean:
        matches = list(re.finditer(pattern, body, re.DOTALL | re.IGNORECASE))
        if len(matches) > 1:
            # 保留最后一个（通常内容更丰富），移除前面的
            # 从后往前处理
            for match in matches[:-1]:
                body = body[:match.start()] + body[match.end():]
    
    return body


def clean_heading_emojis(body):
    """清理所有标题中的emoji前缀"""
    lines = body.split('\n')
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            # 计算#号数量
            level = 0
            idx = 0
            while idx < len(stripped) and stripped[idx] == '#':
                level += 1
                idx += 1
            
            title_text = stripped[idx:].strip()
            clean_title = get_heading_display_name(title_text)
            
            if clean_title:
                new_lines.append('#' * level + ' ' + clean_title)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)


def process_file(filepath):
    """处理单个文件"""
    filename = Path(filepath).name
    print(f"处理: {filename}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = {
        'file': str(filepath),
        'success': False,
        'h1_duplicates': 0,
        'h2_duplicates': 0,
        'error': None,
        'summary': '',
        'keywords': ''
    }
    
    try:
        # 1. 提取frontmatter
        fm, body = extract_frontmatter(text)
        
        if not fm:
            print(f"  ⚠️  无frontmatter，跳过")
            result['error'] = '无frontmatter'
            return result
        
        # 2. 获取规范标题（从frontmatter）
        title = extract_title_from_fm(fm)
        if not title:
            h1_titles = extract_all_h1_titles(body)
            if h1_titles:
                title = h1_titles[0]
            else:
                title = Path(filepath).stem
        
        # 3. 移除重复H1和重复的元信息块
        body, h1_dupes = remove_duplicate_h1_and_metadata(body, title)
        result['h1_duplicates'] = h1_dupes
        
        # 4. 移除重复的二级章节
        body, h2_dupes = remove_duplicate_h2_sections(body)
        result['h2_duplicates'] = h2_dupes
        
        # 5. 移除末尾重复的章节（延伸阅读、知识关联等）
        body = remove_trailing_sections(body)
        
        # 6. 清理标题中的emoji
        body = clean_heading_emojis(body)
        
        # 7. 生成高质量概要
        summary = generate_summary(body, title)
        result['summary'] = summary
        
        # 8. 生成高质量关键词
        keywords = generate_keywords(body, title, fm)
        result['keywords'] = keywords
        
        # 9. 生成目录（只含核心二级标题）
        toc = generate_toc(body)
        
        # 10. 提取参考资料
        internal_refs, external_refs = extract_and_clean_references(body)
        ref_section = build_reference_section(internal_refs, external_refs)
        
        # 11. 构建Changelog
        changelog = build_changelog(fm)
        
        # 12. 构建最终文档
        new_parts = []
        
        # frontmatter（更新updated_at）
        new_fm = re.sub(
            r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
            f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'",
            fm,
            flags=re.MULTILINE
        )
        new_parts.append(f"---\n{new_fm}\n---")
        new_parts.append("")
        
        # 标题、概要、关键词、目录放在一起，然后是清理后的正文
        # 但首先需要从body中移除已有的旧版本这些元素
        
        # 移除旧的概要和关键词（> **概要**: 格式）
        body = re.sub(r'^> \*\*概要\*\*:.*?\n', '', body, flags=re.MULTILINE)
        body = re.sub(r'^> \*\*关键词\*\*:.*?\n', '', body, flags=re.MULTILINE)
        
        # 移除旧的目录
        body = re.sub(r'^##\s*(?:📑\s*)?目录.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        
        # 移除旧的参考文件/参考资料/参考来源
        body = re.sub(r'^##\s*(?:📝\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        
        # 移除旧的changelog
        body = re.sub(r'^##\s*[Cc]hangelog.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        
        # 移除旧的知识关联
        body = re.sub(r'^##\s*(?:🔗\s*)?知识关联.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        
        # 清理过多空行
        body = re.sub(r'\n{3,}', '\n\n', body)
        body = body.strip()
        
        # 组装新文档
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
        
        # 正文
        new_parts.append(body)
        new_parts.append("")
        
        # 参考文件
        new_parts.append(ref_section)
        
        # Changelog
        new_parts.append(changelog)
        
        # 组合最终内容
        final_text = '\n'.join(new_parts)
        
        # 最终清理：移除过多空行
        final_text = re.sub(r'\n{4,}', '\n\n\n', final_text)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        result['success'] = True
        print(f"  ✅ 完成 - 重复H1: {h1_dupes}个, 重复H2: {h2_dupes}个")
        print(f"     概要: {summary[:50]}...")
        print(f"     关键词: {keywords}")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"  ❌ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def main():
    if len(sys.argv) < 2:
        print('用法: python3 deep_refactor_ai_docs_v2.py <目录路径>')
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
    print('📊 深度重构完成统计 (v2)')
    print('=' * 70)
    print(f'  处理文件总数: {len(md_files)} 个')
    print(f'  ✅ 成功: {success_count} 个')
    print(f'  ❌ 失败: {fail_count} 个')
    print()
    print(f'  🗑️  清理重复H1标题: {total_h1_dupes} 个')
    print(f'  📑 合并重复二级章节: {total_h2_dupes} 个')
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
    report_path = os.path.join(target_dir, '_refactor_report_v2.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'📝 详细报告已保存到: {report_path}')


if __name__ == '__main__':
    main()
