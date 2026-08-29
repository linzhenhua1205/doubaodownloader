#!/usr/bin/env python3
"""
深度重构 v3 - 重点优化概要和关键词质量

改进点：
1. 更智能的概要生成 - 从正文核心段落提取，跳过原文链接
2. 更精准的关键词提取 - 过滤数字、年份等无意义词汇
3. 保留目录在正确的位置
4. 更好的章节去重逻辑
"""

import re
import os
import sys
import json
from pathlib import Path
from datetime import datetime


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[3:end_pos].strip()
            body = text[end_pos+4:].strip()
            return fm, body
    return "", text


def extract_title_from_fm(fm):
    match = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def extract_all_h1_titles(body):
    titles = []
    lines = body.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            titles.append(stripped[2:].strip())
    return titles


def remove_emoji(text):
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
    h = remove_emoji(heading)
    h = re.sub(r'^[\s]*\d+[\.、\s]+', '', h)
    h = h.lstrip(' -—·•📋📊🔬💼⚠️🔮🛠️🔗📚📖📎💡🆕🌐📝⚙️🔍📈')
    return h.strip().lower()


def get_heading_display_name(heading):
    h = heading.strip()
    h_clean = remove_emoji(h)
    if h_clean:
        return h_clean
    return h


def is_meaningful_paragraph(text):
    """判断是否是有意义的正文段落"""
    if not text or len(text) < 30:
        return False
    # 跳过原文链接
    if text.startswith('原文') and 'http' in text:
        return False
    if text.startswith('本文') and '基于' in text and '素材' in text:
        return False
    # 跳过纯链接行
    if text.startswith('[') and '](http' in text:
        return False
    # 跳过引用的原文链接
    if re.match(r'^原文[：:]\s*\[', text):
        return False
    return True


def generate_summary(body, title):
    """生成高质量的一句话概要（≤100字）"""
    lines = body.split('\n')
    
    # 策略1: 找第一个真正有意义的正文段落
    content_paragraphs = []
    in_content = False
    skip_until_next_heading = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 遇到标题，重置跳过状态
        if stripped.startswith('#'):
            skip_until_next_heading = False
            # 跳过"快速导读"、"核心要点"等非正文章节
            clean_title = clean_heading_for_compare(stripped.lstrip('#'))
            if any(kw in clean_title for kw in ['快速导读', '核心要点', '目录', '内容提要', '摘要']):
                skip_until_next_heading = True
            continue
        
        if skip_until_next_heading:
            continue
        
        # 跳过引用块的元信息
        if stripped.startswith('> 📅') or stripped.startswith('> 🏷️') or stripped.startswith('> 🔗') or stripped.startswith('> 📝') or stripped.startswith('> ⭐'):
            continue
        if stripped.startswith('> **'):
            continue
        
        # 跳过分隔线
        if stripped == '---':
            continue
        
        # 跳过列表项
        if stripped.startswith(('- ', '* ', '• ')) and len(stripped) < 50:
            continue
        
        # 跳过表格
        if stripped.startswith('|'):
            continue
        
        # 跳过"原文链接"行
        if stripped.startswith('原文') and 'http' in stripped:
            continue
        
        # 找到真正的段落
        if is_meaningful_paragraph(stripped):
            content_paragraphs.append(stripped)
            if len(content_paragraphs) >= 3:
                break
    
    # 策略2: 从"核心要点"或"背景"章节提取关键信息
    core_insights = []
    background_section = re.search(
        r'##\s*(?:🌐\s*)?(?:背景与意义|背景介绍|文章背景|研究背景)[^\n]*\n(.+?)(?=\n## |\Z)',
        body, re.DOTALL
    )
    if background_section:
        bg_text = background_section.group(1)
        # 提取非列表的段落
        bg_paragraphs = [p.strip() for p in bg_text.split('\n') 
                        if p.strip() and not p.strip().startswith(('-', '*', '•', '|')) 
                        and len(p.strip()) > 30]
        if bg_paragraphs:
            content_paragraphs = bg_paragraphs + content_paragraphs
    
    # 构建概要
    summary = ""
    
    if content_paragraphs:
        # 选择第一个最好的段落
        best_para = content_paragraphs[0]
        for p in content_paragraphs:
            if len(p) > len(best_para) and '市场规模' in p or '产业' in p or '技术' in p:
                best_para = p
                break
        
        first_para = best_para
        
        # 尝试截取完整的句子
        if len(first_para) > 100:
            # 按句号、感叹号、问号分割
            sentences = re.split(r'([。！？!?；;])', first_para)
            current = ""
            for i in range(0, len(sentences), 2):
                if i < len(sentences):
                    sent = sentences[i]
                    if i + 1 < len(sentences):
                        sent += sentences[i+1]
                    sent = sent.strip()
                    if sent:
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
    else:
        # 退而求其次：从标题和核心要点生成
        summary = f"本文围绕{title}主题展开深入分析，涵盖技术原理、应用实践与发展趋势等核心内容。"
    
    # 确保不超过100字
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    # 确保是完整的一句话（以句号结尾）
    summary = summary.strip()
    if not summary.endswith(('。', '！', '？', '!', '?', '…')):
        if len(summary) < 98:
            summary += "。"
        else:
            summary = summary[:96] + "..."
    
    return summary.strip()


def is_good_keyword(kw):
    """判断是否是好的关键词"""
    if not kw or len(kw) < 2:
        return False
    
    # 纯数字
    if re.match(r'^\d+$', kw):
        return False
    
    # 纯年份
    if re.match(r'^(19|20)\d{2}$', kw):
        return False
    
    # 以数字开头且很短
    if re.match(r'^\d+', kw) and len(kw) < 4:
        return False
    
    # 常见的无意义词汇
    bad_keywords = {
        '分析', '指南', '详解', '深度', '全面', '最新', '报告', '研究',
        '技术', '应用', '发展', '趋势', '实践', '案例', '综述', '概览',
        '入门', '进阶', '高级', '基础', '原理', '实战', '教程', '手册',
        '大全', '合集', '精选', '推荐', '汇总', '盘点', '揭秘', '洞察',
        '思考', '解读', '观察', '评论', '观点', '看法', '经验', '心得',
        '什么是', '如何', '怎么', '为什么', '哪些', '几个',
        'AI', '人工智能', 'AI与机器学习', '行业动态', '产品与设计',
        '编程与开发', '系统与运维', '数据库', '云计算与DevOps',
        '核心要点', '关键数据', '阅读建议',
        '全景', '深度分析', '全面解析', '深度解析', '最新进展',
        '研究报告', '行业报告', '市场分析', '技术分析',
        '知识管理',  # 太泛化
    }
    
    if kw in bad_keywords:
        return False
    
    # 包含特殊符号且不是正常的技术词汇
    if '%' in kw and not kw.startswith('100%'):
        return False
    
    # 太短的缩写（2个字符以下）
    if len(kw) < 2:
        return False
    
    return True


def generate_keywords(body, title, fm):
    """生成3-5个高质量核心关键词（用 · 分隔）"""
    candidates = []
    seen = set()
    
    def add_keyword(kw, source='unknown'):
        kw_clean = kw.strip()
        if kw_clean and kw_clean not in seen and is_good_keyword(kw_clean):
            candidates.append((kw_clean, source))
            seen.add(kw_clean)
    
    # 1. 从标题提取核心主题（优先度最高）
    title_clean = remove_emoji(title)
    # 移除文件序号前缀
    title_clean = re.sub(r'^\d+[_]?\s*', '', title_clean)
    # 按冒号、破折号等分割，取主标题部分
    title_main = re.split(r'[：:—\-｜|]', title_clean)[0].strip()
    
    # 从主标题提取名词短语
    # 移除"的"等助词结尾的
    title_keywords = []
    
    # 先尝试找明显的技术词汇
    tech_in_title = re.findall(
        r'(?:大模型|LLM|GPT|Claude|Gemini|Llama|DeepSeek|Qwen|通义千问|'
        r'OLMo|MoE|Transformer|RAG|Agent|智能体|AIGC|生成式AI|'
        r'机器学习|深度学习|神经网络|微调|Prompt|提示词|多模态|'
        r'算力|Token|大语言模型|AI编程|开源大模型)',
        title_clean
    )
    for kw in tech_in_title:
        add_keyword(kw, 'title_tech')
    
    # 再提取标题中的其他有意义词汇
    title_parts = re.split(r'[：:、，,\s与及和]+', title_main)
    for part in title_parts:
        part = part.strip()
        if is_good_keyword(part):
            add_keyword(part, 'title')
    
    # 2. 从frontmatter的tags提取（高质量）
    tags_match = re.search(r'^tags:\s*(.+?)(?=^\w+:|\Z)', fm, re.MULTILINE | re.DOTALL)
    if tags_match:
        tags_text = tags_match.group(1)
        tag_items = re.findall(r'-\s*(.+)', tags_text)
        if not tag_items:
            tag_items = [t.strip() for t in tags_text.split(',')]
        for t in tag_items:
            t = t.strip()
            if t and t != 'null':
                add_keyword(t, 'fm_tags')
    
    # 3. 从正文提取高频技术关键词（频次加权）
    tech_kw_freq = {}
    
    # 定义技术关键词模式
    tech_patterns = [
        (r'大模型', 5),
        (r'LLM', 5),
        (r'GPT(?:-\d+)?', 4),
        (r'Claude', 4),
        (r'Gemini', 4),
        (r'Llama', 4),
        (r'DeepSeek', 4),
        (r'通义千问|Qwen', 4),
        (r'OLMo', 4),
        (r'MoE|混合专家', 4),
        (r'Transformer', 4),
        (r'RAG|检索增强生成', 4),
        (r'Agent|智能体', 5),
        (r'AIGC|生成式AI', 4),
        (r'机器学习', 3),
        (r'深度学习', 3),
        (r'神经网络', 3),
        (r'微调', 3),
        (r'Prompt|提示词', 3),
        (r'多模态', 4),
        (r'算力', 3),
        (r'Token', 3),
        (r'AI编程|代码生成', 4),
        (r'开源', 3),
        (r'闭源', 2),
        (r'推理', 2),
        (r'训练', 2),
        (r'GPU', 3),
        (r'端侧推理', 3),
        (r'私有化部署', 3),
        (r'企业级', 2),
        (r'知识图谱', 3),
        (r'自然语言处理|NLP', 3),
        (r'计算机视觉|CV', 3),
        (r'AI电商', 3),
        (r'医疗AI', 3),
        (r'自动驾驶', 3),
        (r'具身智能', 3),
    ]
    
    for pattern, weight in tech_patterns:
        count = len(re.findall(pattern, body))
        if count > 0:
            # 用第一个匹配作为关键词（规范化）
            first_match = re.search(pattern, body)
            if first_match:
                kw = first_match.group(0)
                # 规范化一些词汇
                if kw.lower() == 'llm':
                    kw = '大模型'
                elif kw == 'Transformer':
                    kw = 'Transformer架构'
                elif kw == 'RAG' or kw == '检索增强生成':
                    kw = 'RAG'
                elif kw == 'Agent' or kw == '智能体':
                    kw = 'AI Agent'
                elif kw == 'AIGC' or kw == '生成式AI':
                    kw = 'AIGC'
                elif kw == 'MoE' or kw == '混合专家':
                    kw = 'MoE架构'
                elif kw == 'Prompt' or kw == '提示词':
                    kw = '提示工程'
                elif kw == 'NLP' or kw == '自然语言处理':
                    kw = '自然语言处理'
                elif kw == 'CV' or kw == '计算机视觉':
                    kw = '计算机视觉'
                
                tech_kw_freq[kw] = count * weight
    
    # 按权重排序
    sorted_tech = sorted(tech_kw_freq.items(), key=lambda x: x[1], reverse=True)
    for kw, score in sorted_tech:
        if score >= 10:  # 至少有一定的出现频次
            add_keyword(kw, 'body_tech')
    
    # 4. 从frontmatter的categories提取（优先级较低）
    cats_match = re.search(r'^categories:\s*(.+?)$', fm, re.MULTILINE)
    if cats_match:
        cats = [c.strip() for c in cats_match.group(1).split(',')]
        for c in cats:
            if c and is_good_keyword(c):
                add_keyword(c, 'fm_cats')
    
    # 构建最终关键词列表
    final_keywords = []
    
    # 优先选标题中的技术词汇
    for kw, src in candidates:
        if src == 'title_tech' and len(final_keywords) < 3:
            final_keywords.append(kw)
    
    # 然后是frontmatter tags
    for kw, src in candidates:
        if src == 'fm_tags' and kw not in final_keywords and len(final_keywords) < 4:
            final_keywords.append(kw)
    
    # 然后是正文高频技术词
    for kw, src in candidates:
        if src == 'body_tech' and kw not in final_keywords and len(final_keywords) < 5:
            final_keywords.append(kw)
    
    # 最后补充标题中的其他词汇
    for kw, src in candidates:
        if src == 'title' and kw not in final_keywords and len(final_keywords) < 5:
            final_keywords.append(kw)
    
    # 如果还是不够，用其他候选补充
    if len(final_keywords) < 3:
        for kw, src in candidates:
            if kw not in final_keywords:
                final_keywords.append(kw)
                if len(final_keywords) >= 3:
                    break
    
    # 确保至少3个，最多5个
    final_keywords = final_keywords[:5]
    
    if len(final_keywords) < 3:
        # 保底方案
        backup = ['大模型', 'AI Agent', 'AIGC']
        for kw in backup:
            if kw not in final_keywords:
                final_keywords.append(kw)
                if len(final_keywords) >= 3:
                    break
    
    return " · ".join(final_keywords)


def extract_core_h2_headings(body):
    """提取核心二级标题（用于生成目录）"""
    lines = body.split('\n')
    headings = []
    
    non_core_keywords = [
        '目录', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '相关知识点', '延伸阅读', '相关文章',
        '相关素材', '关键词标签', '内容评级', 'import素材融合',
        '快速导读', '核心要点', '内容',
    ]
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            clean_title = clean_heading_for_compare(title)
            display_title = get_heading_display_name(title)
            
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
    
    # 去重
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
    """提取参考资料"""
    internal_refs = []
    external_refs = []
    
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    all_links = link_pattern.findall(body)
    
    for text, url in all_links:
        if url.startswith('http'):
            external_refs.append((text, url))
        elif url.endswith('.md') or 'import/' in url or 'knowledge/' in url or '../' in url:
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
    """移除重复的H1标题和开头的重复元信息"""
    lines = body.split('\n')
    new_lines = []
    h1_count = 0
    
    first_h1_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            first_h1_idx = i
            break
    
    if first_h1_idx == -1:
        return body, 0
    
    new_lines.append(f"# {canonical_title}")
    h1_count = 1
    
    i = first_h1_idx + 1
    while i < len(lines):
        stripped = lines[i].strip()
        
        if stripped.startswith('# ') and not stripped.startswith('## '):
            h1_count += 1
            j = i + 1
            while j < len(lines) and (lines[j].strip().startswith('>') or lines[j].strip() == ''):
                j += 1
            i = j
            continue
        
        new_lines.append(lines[i])
        i += 1
    
    return '\n'.join(new_lines), h1_count - 1


def remove_duplicate_h2_sections(body):
    """合并重复的二级章节"""
    lines = body.split('\n')
    
    sections = []
    current_section_start = None
    current_title = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
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
    
    seen = {}
    duplicates = []
    first_occurrence = {}
    
    for idx, sec in enumerate(sections):
        key = sec['clean']
        if key in first_occurrence:
            duplicates.append(idx)
        else:
            first_occurrence[key] = idx
    
    if not duplicates:
        return body, 0
    
    new_lines = []
    sections_to_remove = set(duplicates)
    
    prev_end = -1
    for idx, sec in enumerate(sections):
        if idx in sections_to_remove:
            continue
        
        start = sec['start']
        if prev_end >= 0:
            start = prev_end + 1
        
        for i in range(start, sec['start']):
            new_lines.append(lines[i])
        
        new_lines.append(f"## {sec['display']}")
        
        for i in range(sec['start'] + 1, sec['end'] + 1):
            new_lines.append(lines[i])
        
        prev_end = sec['end']
    
    if sections:
        last_sec_end = sections[-1]['end']
        for i in range(last_sec_end + 1, len(lines)):
            new_lines.append(lines[i])
    
    return '\n'.join(new_lines), len(duplicates)


def remove_trailing_sections(body):
    """移除末尾重复的章节"""
    patterns_to_clean = [
        (r'##\s*(?:📚\s*)?延伸阅读.*?(?=\n## |\Z)', '延伸阅读'),
        (r'##\s*(?:🔗\s*)?知识关联.*?(?=\n## |\Z)', '知识关联'),
        (r'##\s*(?:📎\s*)?相关素材.*?(?=\n## |\Z)', '相关素材'),
        (r'##\s*(?:🔗\s*)?相关文章.*?(?=\n## |\Z)', '相关文章'),
    ]
    
    for pattern, name in patterns_to_clean:
        matches = list(re.finditer(pattern, body, re.DOTALL | re.IGNORECASE))
        if len(matches) > 1:
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
        fm, body = extract_frontmatter(text)
        
        if not fm:
            print(f"  ⚠️  无frontmatter，跳过")
            result['error'] = '无frontmatter'
            return result
        
        title = extract_title_from_fm(fm)
        if not title:
            h1_titles = extract_all_h1_titles(body)
            if h1_titles:
                title = h1_titles[0]
            else:
                title = Path(filepath).stem
        
        body, h1_dupes = remove_duplicate_h1_and_metadata(body, title)
        result['h1_duplicates'] = h1_dupes
        
        body, h2_dupes = remove_duplicate_h2_sections(body)
        result['h2_duplicates'] = h2_dupes
        
        body = remove_trailing_sections(body)
        body = clean_heading_emojis(body)
        
        summary = generate_summary(body, title)
        result['summary'] = summary
        
        keywords = generate_keywords(body, title, fm)
        result['keywords'] = keywords
        
        toc = generate_toc(body)
        
        internal_refs, external_refs = extract_and_clean_references(body)
        ref_section = build_reference_section(internal_refs, external_refs)
        
        changelog = build_changelog(fm)
        
        # 从body中移除旧的格式元素
        body = re.sub(r'^> \*\*概要\*\*:.*?\n', '', body, flags=re.MULTILINE)
        body = re.sub(r'^> \*\*关键词\*\*:.*?\n', '', body, flags=re.MULTILINE)
        body = re.sub(r'^##\s*(?:📑\s*)?目录.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        body = re.sub(r'^##\s*(?:📝\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        body = re.sub(r'^##\s*[Cc]hangelog.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        body = re.sub(r'^##\s*(?:🔗\s*)?知识关联.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        
        body = re.sub(r'\n{3,}', '\n\n', body)
        body = body.strip()
        
        # 组装新文档
        new_parts = []
        
        new_fm = re.sub(
            r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
            f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'",
            fm,
            flags=re.MULTILINE
        )
        new_parts.append(f"---\n{new_fm}\n---")
        new_parts.append("")
        new_parts.append(f"# {title}")
        new_parts.append("")
        new_parts.append(f"> **概要**: {summary}")
        new_parts.append(f"> **关键词**: {keywords}")
        new_parts.append("")
        
        if toc:
            new_parts.append(toc)
        
        new_parts.append(body)
        new_parts.append("")
        new_parts.append(ref_section)
        new_parts.append(changelog)
        
        final_text = '\n'.join(new_parts)
        final_text = re.sub(r'\n{4,}', '\n\n\n', final_text)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        result['success'] = True
        print(f"  ✅ 完成 - 重复H1: {h1_dupes}个, 重复H2: {h2_dupes}个")
        print(f"     概要: {summary[:60]}...")
        print(f"     关键词: {keywords}")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"  ❌ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def main():
    if len(sys.argv) < 2:
        print('用法: python3 deep_refactor_ai_docs_v3.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
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
    print('📊 深度重构完成统计 (v3)')
    print('=' * 70)
    print(f'  处理文件总数: {len(md_files)} 个')
    print(f'  ✅ 成功: {success_count} 个')
    print(f'  ❌ 失败: {fail_count} 个')
    print()
    print(f'  🗑️  清理重复H1标题: {total_h1_dupes} 个')
    print(f'  📑 合并重复二级章节: {total_h2_dupes} 个')
    print()
    
    if fail_count > 0:
        print('  ❌ 失败文件:')
        for r in results:
            if not r['success']:
                print(f'    - {Path(r["file"]).name}: {r["error"]}')
        print()
    
    print('=' * 70)
    
    report_path = os.path.join(target_dir, '_refactor_report_v3.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'📝 详细报告已保存到: {report_path}')


if __name__ == '__main__':
    main()
