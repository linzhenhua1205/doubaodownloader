#!/usr/bin/env python3
"""
深度重构最终版 - 一次性完成所有重构工作

核心功能：
1. 清理重复H1标题（只保留一个）
2. 合并重复的二级章节
3. 生成高质量概要（从正文提取完整的一句话，≤100字）
4. 生成高质量关键词（3-5个，用 · 分隔）
5. 生成目录（只包含核心二级标题）
6. 清理标题中的emoji
7. 标准化格式（参考文件、Changelog）
8. 保留frontmatter、原文链接等元信息
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


def remove_emoji(text):
    """移除emoji"""
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
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()


def clean_heading_for_compare(heading):
    """清理标题用于比较"""
    h = remove_emoji(heading)
    h = re.sub(r'^[\s]*\d+[\.、\s]+', '', h)
    h = h.lstrip(' -—·•')
    return h.strip().lower()


def get_heading_display_name(heading):
    """获取清理后的显示标题"""
    h = heading.strip()
    h_clean = remove_emoji(h)
    return h_clean if h_clean else h


def deduplicate_h1(body, canonical_title):
    """移除重复H1，只保留第一个，并返回重复数量"""
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
            # 跳过这个H1以及后面跟着的元信息引用块（> 开头的行）
            j = i + 1
            while j < len(lines):
                s = lines[j].strip()
                if s.startswith('>') or s == '':
                    j += 1
                else:
                    break
            i = j
            continue
        
        new_lines.append(lines[i])
        i += 1
    
    return '\n'.join(new_lines), h1_count - 1


def deduplicate_h2_sections(body):
    """合并重复的二级章节"""
    lines = body.split('\n')
    
    sections = []
    current_start = None
    current_title = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            if current_title is not None:
                sections.append({
                    'clean': clean_heading_for_compare(current_title),
                    'display': get_heading_display_name(current_title),
                    'start': current_start,
                    'end': i - 1,
                    'original': current_title
                })
            
            current_start = i
            current_title = stripped[3:].strip()
    
    if current_title is not None:
        sections.append({
            'clean': clean_heading_for_compare(current_title),
            'display': get_heading_display_name(current_title),
            'start': current_start,
            'end': len(lines) - 1,
            'original': current_title
        })
    
    if len(sections) <= 1:
        return body, 0
    
    # 找出重复的（保留第一个出现的）
    seen = {}
    duplicates = []
    
    for idx, sec in enumerate(sections):
        key = sec['clean']
        if key in seen:
            duplicates.append(idx)
        else:
            seen[key] = idx
    
    if not duplicates:
        return body, 0
    
    # 重建
    new_lines = []
    dup_set = set(duplicates)
    prev_end = -1
    
    for idx, sec in enumerate(sections):
        if idx in dup_set:
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
        last_end = sections[-1]['end']
        for i in range(last_end + 1, len(lines)):
            new_lines.append(lines[i])
    
    return '\n'.join(new_lines), len(duplicates)


def generate_summary(body, title):
    """生成高质量的一句话概要（≤100字）"""
    
    # 收集所有候选段落
    candidates = []
    
    # 按优先级遍历各个章节
    priority_section_patterns = [
        r'##\s*(?:🌐\s*)?(?:背景与意义|背景介绍|研究背景|项目背景|文章背景)',
        r'##\s*(?:📋\s*)?(?:执行摘要|内容摘要|核心摘要|报告摘要|市场分析)',
        r'##\s*(?:📊\s*)?(?:市场规模|行业现状|发展现状|市场格局|产业现状)',
        r'##\s*(?:📖\s*)?(?:概述|简介|前言|引言|总览)',
        r'##\s*(?:🔬\s*)?(?:核心技术解析|技术解析|技术原理|核心技术)',
        r'##\s*(?:💼\s*)?(?:企业案例|应用实践|落地案例|案例分析)',
        r'##\s*(?:内容|正文|文章内容)',
    ]
    
    for pattern in priority_section_patterns:
        match = re.search(pattern + r'[^\n]*\n(.+?)(?=\n## |\Z)', body, re.DOTALL)
        if not match:
            continue
        
        section_text = match.group(1)
        
        # 从章节中提取段落
        paragraphs = extract_paragraphs(section_text)
        
        for para in paragraphs:
            if is_good_summary_paragraph(para):
                candidates.append(para)
        
        if candidates:
            break
    
    # 如果没找到，遍历所有章节找第一个好段落
    if not candidates:
        all_sections = re.finditer(r'##\s+(.+?)\n(.+?)(?=\n## |\Z)', body, re.DOTALL)
        for sec_match in all_sections:
            sec_title = sec_match.group(1)
            sec_content = sec_match.group(2)
            
            # 跳过目录、快速导读等
            sec_clean = clean_heading_for_compare(sec_title)
            if any(kw in sec_clean for kw in ['目录', '快速导读', '核心要点', '参考文件', 'changelog', '知识关联', '延伸阅读']):
                continue
            
            paragraphs = extract_paragraphs(sec_content)
            for para in paragraphs:
                if is_good_summary_paragraph(para):
                    candidates.append(para)
                    break
            
            if candidates:
                break
    
    # 如果还没找到，从核心要点中提取并整合成一句话
    if not candidates:
        core_match = re.search(
            r'##\s*(?:📋\s*)?(?:核心要点|快速导读)[^\n]*\n(.+?)(?=\n## |\Z)',
            body, re.DOTALL
        )
        if core_match:
            bullets = re.findall(r'[-*•]\s+\**([^*]+?)\**[：:]?\s*(.+?)(?=\n|$)', core_match.group(1))
            if bullets:
                first_bullet = bullets[0]
                text = first_bullet[0] + '：' + first_bullet[1] if first_bullet[1] else first_bullet[0]
                candidates.append(text)
    
    # 选择最好的段落
    best = ""
    if candidates:
        # 评分：长度适中、包含数据、包含核心概念
        scored = []
        for c in candidates:
            score = len(c)
            if re.search(r'\d+[%万亿亿元美元]', c):
                score += 50
            if any(kw in c for kw in ['市场', '产业', '技术', '增长', '发展', '趋势', '规模']):
                score += 30
            scored.append((c, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        best = scored[0][0]
    
    if not best:
        best = f"本文围绕{title}主题展开深入分析，涵盖技术原理、应用实践与行业趋势等核心内容。"
    
    # 清理和格式化
    summary = format_summary(best)
    return summary


def extract_paragraphs(text):
    """从文本中提取段落（非列表、非表格）"""
    paragraphs = []
    current = []
    in_code_block = False
    
    for line in text.split('\n'):
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        if not stripped:
            if current:
                para = ' '.join(current).strip()
                if para:
                    paragraphs.append(para)
                current = []
            continue
        
        # 跳过列表项
        if re.match(r'^[-*•]\s+', stripped) or re.match(r'^\d+[\.、)]\s+', stripped):
            if current:
                para = ' '.join(current).strip()
                if para:
                    paragraphs.append(para)
                current = []
            continue
        
        # 跳过表格
        if stripped.startswith('|'):
            continue
        
        # 跳过引用的元信息
        if re.match(r'^>\s*[📅🏷️🔗📝⭐]', stripped):
            continue
        
        # 跳过原文链接
        if re.match(r'^原文[：:]\s*\[', stripped):
            continue
        
        # 跳过小标题（加粗的短语）
        if re.match(r'^\*\*[^*]+\*\*[：:]\s*$', stripped):
            continue
        
        current.append(stripped)
    
    if current:
        para = ' '.join(current).strip()
        if para:
            paragraphs.append(para)
    
    return paragraphs


def is_good_summary_paragraph(text):
    """判断是否适合作为概要"""
    if not text or len(text) < 30:
        return False
    
    # 排除原文链接
    if text.startswith('原文') and 'http' in text:
        return False
    
    # 排除太短的
    if len(text) < 30:
        return False
    
    return True


def format_summary(text):
    """格式化概要为完整的一句话，≤100字"""
    if not text:
        return text
    
    # 移除markdown格式
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 提取第一个完整句子
    sentences = re.split(r'([。！？!?；;])', text)
    result = ""
    
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        
        sent = sentences[i].strip()
        if not sent:
            continue
        
        punct = sentences[i + 1] if i + 1 < len(sentences) else '。'
        
        if len(result) + len(sent) + len(punct) <= 95:
            result += sent + punct
        else:
            remaining = 95 - len(result)
            if remaining > 10:
                result += sent[:remaining] + '...'
            break
        
        # 有一个完整句子就可以了
        if result.endswith(('。', '！', '？', '!', '?')) and len(result) >= 25:
            break
    
    if not result:
        result = text[:97] + '...'
    
    # 确保结尾正确
    result = result.strip()
    if not result.endswith(('。', '！', '？', '!', '?', '…', '...')):
        if len(result) < 98:
            result += '。'
        else:
            result = result[:96] + '...'
    
    # 最终长度检查
    if len(result) > 100:
        result = result[:97] + '...'
    
    return result


def generate_keywords(body, title, fm):
    """生成3-5个高质量关键词"""
    candidates = []  # (keyword, priority)
    seen = set()
    
    def add(kw, prio):
        kw = normalize_keyword(kw.strip())
        if kw and kw not in seen and is_valid_keyword(kw):
            candidates.append((kw, prio))
            seen.add(kw)
    
    # 1. 从标题中提取技术词汇（最高优先级）
    title_clean = remove_emoji(title)
    
    title_tech_terms = [
        '大模型', 'LLM', 'GPT', 'Claude', 'Gemini', 'Llama', 'DeepSeek',
        '通义千问', 'Qwen', 'OLMo', 'MoE', 'Transformer', 'RAG',
        'Agent', '智能体', 'AIGC', '生成式AI', '机器学习', '深度学习',
        '神经网络', '微调', 'Prompt', '提示词', '多模态', '算力',
        'Token', 'AI编程', '代码生成', '医疗AI', 'AI电商',
        '具身智能', '自动驾驶', '知识图谱', '自然语言处理',
        '端侧推理', '企业级应用'
    ]
    
    for term in title_tech_terms:
        if term.lower() in title_clean.lower():
            add(term, 100)
    
    # 2. 从frontmatter tags提取（高优先级）
    tags_match = re.search(r'^tags:\s*(.+?)(?=^\w+:|\Z)', fm, re.MULTILINE | re.DOTALL)
    if tags_match:
        tags_text = tags_match.group(1)
        tag_items = re.findall(r'-\s*(.+)', tags_text)
        if not tag_items:
            tag_items = [t.strip() for t in tags_text.split(',')]
        for t in tag_items:
            t = t.strip()
            if t and t != 'null':
                add(t, 80)
    
    # 3. 从正文高频技术词提取（中优先级）
    tech_patterns = [
        (r'大模型|大语言模型', 5, '大模型'),
        (r'GPT(?:-\d+)?', 4, 'GPT'),
        (r'Claude', 4, 'Claude'),
        (r'Gemini', 4, 'Gemini'),
        (r'Llama', 4, 'Llama'),
        (r'DeepSeek|深度求索', 4, 'DeepSeek'),
        (r'通义千问|Qwen', 4, '通义千问'),
        (r'OLMo', 4, 'OLMo'),
        (r'MoE|混合专家', 4, 'MoE架构'),
        (r'Transformer', 4, 'Transformer架构'),
        (r'RAG|检索增强生成', 4, 'RAG'),
        (r'Agent|智能体', 5, 'AI Agent'),
        (r'AIGC|生成式AI', 4, 'AIGC'),
        (r'机器学习', 3, '机器学习'),
        (r'深度学习', 3, '深度学习'),
        (r'神经网络', 3, '神经网络'),
        (r'微调', 3, '微调'),
        (r'Prompt|提示词|提示工程', 3, '提示工程'),
        (r'多模态', 4, '多模态'),
        (r'算力', 3, '算力'),
        (r'Token', 2, 'Token'),
        (r'AI编程|代码生成', 4, 'AI编程'),
        (r'开源', 3, '开源'),
        (r'GPU', 3, 'GPU'),
        (r'端侧推理', 3, '端侧推理'),
        (r'企业级|私有化部署', 3, '企业级应用'),
        (r'知识图谱', 3, '知识图谱'),
        (r'自然语言处理|NLP', 3, '自然语言处理'),
        (r'计算机视觉|CV', 3, '计算机视觉'),
        (r'医疗AI', 4, '医疗AI'),
        (r'AI电商|电商AI', 4, 'AI电商'),
        (r'自动驾驶', 3, '自动驾驶'),
        (r'具身智能', 3, '具身智能'),
    ]
    
    freq_scores = {}
    for pattern, weight, norm in tech_patterns:
        count = len(re.findall(pattern, body))
        if count > 0:
            score = count * weight
            if norm in freq_scores:
                freq_scores[norm] += score
            else:
                freq_scores[norm] = score
    
    sorted_tech = sorted(freq_scores.items(), key=lambda x: x[1], reverse=True)
    for kw, score in sorted_tech:
        if score >= 15:
            add(kw, 60 + min(score, 40))
    
    # 4. 从标题提取领域/主题词（低优先级）
    title_main = re.split(r'[：:—\-｜|]', title_clean)[0].strip()
    title_main = re.sub(r'^\d+[_]?\s*', '', title_main)
    
    domain_keywords = re.findall(r'[\u4e00-\u9fff]{2,}', title_main)
    for kw in domain_keywords:
        if is_valid_keyword(kw):
            add(kw, 40)
    
    # 选择最终关键词
    final = []
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    for kw, prio in candidates:
        if len(final) >= 5:
            break
        
        # 避免过于相似的
        too_similar = False
        for existing in final:
            if kw in existing or existing in kw:
                if len(kw) < len(existing):
                    too_similar = True
                    break
        
        if too_similar:
            continue
        
        final.append(kw)
    
    # 确保至少3个
    if len(final) < 3:
        backups = ['大模型', 'AI Agent', 'AIGC', 'RAG', '多模态']
        for b in backups:
            if b not in final:
                final.append(b)
                if len(final) >= 3:
                    break
    
    return " · ".join(final[:5])


def normalize_keyword(kw):
    """规范化关键词"""
    kw = kw.strip('[ ]()（）')
    mapping = {
        '大语言模型': '大模型',
        'LLM': '大模型',
        '生成式AI': 'AIGC',
        '智能体': 'AI Agent',
        'Agent': 'AI Agent',
        '检索增强生成': 'RAG',
        '提示词': '提示工程',
        'Prompt': '提示工程',
        'MoE': 'MoE架构',
        '混合专家': 'MoE架构',
        'Transformer': 'Transformer架构',
        'NLP': '自然语言处理',
        'CV': '计算机视觉',
    }
    return mapping.get(kw, kw)


def is_valid_keyword(kw):
    """判断是否是有效关键词"""
    if not kw or len(kw) < 2:
        return False
    
    # 纯数字
    if re.match(r'^\d+$', kw):
        return False
    
    # 年份
    if re.match(r'^(19|20)\d{2}$', kw):
        return False
    
    # 停用词
    stopwords = {
        '分析', '指南', '详解', '深度', '全面', '最新', '报告', '研究',
        '技术', '应用', '发展', '趋势', '实践', '案例', '综述', '概览',
        '入门', '进阶', '高级', '基础', '原理', '实战', '教程', '手册',
        '大全', '合集', '精选', '推荐', '汇总', '盘点', '揭秘', '洞察',
        '思考', '解读', '观察', '评论', '观点', '看法', '经验', '心得',
        'AI', '人工智能', '行业动态', '产品与设计',
        '编程与开发', '系统与运维', '数据库', '知识管理',
        '核心要点', '关键数据', '阅读建议',
        '全景', '深度分析', '全面解析', '最新进展',
        '行业报告', '市场分析', '技术分析',
        '什么是', '如何', '怎么', '为什么',
    }
    
    if kw in stopwords:
        return False
    
    return True


def generate_toc(body):
    """生成目录（只含核心二级标题）"""
    lines = body.split('\n')
    headings = []
    
    non_core_keywords = [
        '目录', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '延伸阅读', '相关文章', '相关素材',
        '快速导读', '核心要点', '内容', '执行摘要', '关键词标签',
        '内容评级', 'import素材融合', '阅读建议', '关键数据',
    ]
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            clean = clean_heading_for_compare(title)
            display = get_heading_display_name(title)
            
            is_non_core = False
            for kw in non_core_keywords:
                if kw.lower() in clean:
                    is_non_core = True
                    break
            
            if not is_non_core and display and len(display) > 1:
                headings.append(display)
    
    # 去重
    seen = set()
    unique = []
    for h in headings:
        h_clean = h.lower()
        if h_clean not in seen:
            seen.add(h_clean)
            unique.append(h)
    
    if len(unique) < 3:
        return ""
    
    toc = ["## 📑 目录", ""]
    for h in unique:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', h)
        toc.append(f"- [{h}](#{anchor})")
    
    toc.append("")
    return '\n'.join(toc)


def extract_references(body):
    """提取参考资料"""
    internal = []
    external = []
    
    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', body):
        text = match.group(1)
        url = match.group(2)
        
        if url.startswith('http'):
            external.append((text, url))
        elif url.endswith('.md') or 'import/' in url or 'knowledge/' in url or '../' in url:
            internal.append((text, url))
    
    # 去重
    seen_e = set()
    unique_e = []
    for t, u in external:
        if u not in seen_e:
            seen_e.add(u)
            unique_e.append((t, u))
    
    seen_i = set()
    unique_i = []
    for t, u in internal:
        if u not in seen_i:
            seen_i.add(u)
            unique_i.append((t, u))
    
    return unique_i[:10], unique_e[:10]


def build_reference_section(internal, external):
    """构建参考文件章节"""
    lines = ["## 参考文件", ""]
    
    lines.append("### 内部知识库引用")
    if internal:
        for text, url in internal[:8]:
            display = text[:60] + "..." if len(text) > 60 else text
            lines.append(f"- [{display}]({url})")
    else:
        lines.append("- 暂无内部引用")
    
    lines.append("")
    lines.append("### 外部资料引用")
    if external:
        for text, url in external[:8]:
            display = text[:60] + "..." if len(text) > 60 else text
            lines.append(f"- [{display}]({url})")
    else:
        lines.append("- 暂无外部引用")
    
    lines.append("")
    return '\n'.join(lines)


def build_changelog(fm):
    """构建Changelog"""
    create_date = "2025-01-01"
    update_date = datetime.now().strftime('%Y-%m-%d')
    
    m = re.search(r'^created_at:\s*(\d{4}-\d{2}-\d{2})', fm, re.MULTILINE)
    if m:
        create_date = m.group(1)
    
    return f"""## Changelog

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| {update_date} | v2.0 | 深度重构：清理重复H1、合并重复章节、重写概要关键词、标准化格式 |
| {create_date} | v1.0 | 初始创建 |

"""


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
            result['error'] = '无frontmatter'
            print(f"  ⚠️  无frontmatter")
            return result
        
        title = extract_title_from_fm(fm)
        if not title:
            for line in body.split('\n'):
                s = line.strip()
                if s.startswith('# ') and not s.startswith('## '):
                    title = s[2:].strip()
                    break
        if not title:
            title = filename.replace('.md', '')
        
        # 1. 去重H1
        body, h1_dupes = deduplicate_h1(body, title)
        result['h1_duplicates'] = h1_dupes
        
        # 2. 去重H2章节
        body, h2_dupes = deduplicate_h2_sections(body)
        result['h2_duplicates'] = h2_dupes
        
        # 3. 清理标题emoji
        lines = body.split('\n')
        cleaned = []
        for line in lines:
            s = line.strip()
            if s.startswith('#'):
                level = 0
                idx = 0
                while idx < len(s) and s[idx] == '#':
                    level += 1
                    idx += 1
                title_text = s[idx:].strip()
                clean_title = get_heading_display_name(title_text)
                if clean_title:
                    cleaned.append('#' * level + ' ' + clean_title)
                else:
                    cleaned.append(line)
            else:
                cleaned.append(line)
        body = '\n'.join(cleaned)
        
        # 4. 生成概要
        summary = generate_summary(body, title)
        result['summary'] = summary
        
        # 5. 生成关键词
        keywords = generate_keywords(body, title, fm)
        result['keywords'] = keywords
        
        # 6. 生成目录
        toc = generate_toc(body)
        
        # 7. 提取参考资料
        internal, external = extract_references(body)
        ref_section = build_reference_section(internal, external)
        
        # 8. 构建Changelog
        changelog = build_changelog(fm)
        
        # 9. 移除body中旧的格式元素
        body = re.sub(r'^> \*\*概要\*\*:.*?\n', '', body, flags=re.MULTILINE)
        body = re.sub(r'^> \*\*关键词\*\*:.*?\n', '', body, flags=re.MULTILINE)
        body = re.sub(r'^##\s*(?:📑\s*)?目录.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        body = re.sub(r'^##\s*(?:📝\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        body = re.sub(r'^##\s*[Cc]hangelog.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        body = re.sub(r'^##\s*(?:🔗\s*)?知识关联.*?(?=\n## |\Z)', '', body, flags=re.MULTILINE | re.DOTALL)
        
        body = re.sub(r'\n{3,}', '\n\n', body).strip()
        
        # 10. 组装最终文档
        parts = []
        
        # 更新frontmatter的updated_at
        new_fm = re.sub(
            r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
            f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'",
            fm,
            flags=re.MULTILINE
        )
        parts.append(f"---\n{new_fm}\n---")
        parts.append("")
        parts.append(f"# {title}")
        parts.append("")
        parts.append(f"> **概要**: {summary}")
        parts.append(f"> **关键词**: {keywords}")
        parts.append("")
        
        if toc:
            parts.append(toc)
        
        parts.append(body)
        parts.append("")
        parts.append(ref_section)
        parts.append(changelog)
        
        final_text = '\n'.join(parts)
        final_text = re.sub(r'\n{4,}', '\n\n\n', final_text)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        result['success'] = True
        print(f"  ✅ 完成 - H1重复: {h1_dupes}, H2重复: {h2_dupes}")
        print(f"     概要: {summary[:65]}...")
        print(f"     关键词: {keywords}")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"  ❌ 失败: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def main():
    if len(sys.argv) < 2:
        print('用法: python3 deep_refactor_final.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件（已跳过index.md）')
    print()
    
    results = []
    success = 0
    fail = 0
    total_h1 = 0
    total_h2 = 0
    
    for fp in md_files:
        r = process_file(str(fp))
        results.append(r)
        if r['success']:
            success += 1
            total_h1 += r['h1_duplicates']
            total_h2 += r['h2_duplicates']
        else:
            fail += 1
    
    print()
    print('=' * 70)
    print('📊 深度重构完成统计（最终版）')
    print('=' * 70)
    print(f'  处理文件总数: {len(md_files)} 个')
    print(f'  ✅ 成功: {success} 个')
    print(f'  ❌ 失败: {fail} 个')
    print()
    print(f'  🗑️  清理重复H1标题: {total_h1} 个')
    print(f'  📑 合并重复二级章节: {total_h2} 个')
    print()
    
    if fail > 0:
        print('  ❌ 失败文件:')
        for r in results:
            if not r['success']:
                print(f'    - {Path(r["file"]).name}: {r["error"]}')
        print()
    
    print('=' * 70)
    
    report_path = os.path.join(target_dir, '_refactor_final_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'📝 详细报告: {report_path}')


if __name__ == '__main__':
    main()
