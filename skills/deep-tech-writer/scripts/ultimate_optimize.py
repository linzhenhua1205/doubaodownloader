#!/usr/bin/env python3
"""
终极优化版 - 从文章特有内容提取概要和关键词

核心改进：
1. 跳过通用模板内容（核心要点、快速导读、背景与上下文、深度解读等模板章节）
2. 从"内容"章节提取文章特有信息
3. 结合标题生成精准的概要和关键词
"""

import re
import os
import sys
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
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()


def clean_heading(text):
    t = remove_emoji(text)
    t = t.lstrip(' -—·•')
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def extract_article_specific_content(body):
    """提取文章特有内容（跳过通用模板章节）"""
    
    # 通用模板章节关键词（这些是每个文件都有的重复内容）
    template_section_keywords = [
        '核心要点', '快速导读', '背景与意义', '背景与上下文', '深度解读',
        '主流大模型对比', '挑战与风险', '趋势与展望', '建议与行动指南',
        '企业案例与应用实践', '核心技术解析', '现状与格局',
        '关键数据', '阅读建议', '适合人群', '阅读时长', '难度等级',
        '内容评级', 'import素材融合', '知识关联',
    ]
    
    # 优先从"内容"章节提取
    content_match = re.search(
        r'##\s*(?:📋\s*)?内容[^\n]*\n(.+?)(?=\n## |\Z)',
        body, re.DOTALL
    )
    
    if content_match:
        content_text = content_match.group(1)
        # 移除原文链接行
        content_text = re.sub(r'^原文[：:].*?\n', '', content_text, flags=re.MULTILINE)
        content_text = content_text.strip()
        if len(content_text) > 100:
            return content_text
    
    # 如果没有"内容"章节，收集所有非模板章节的内容
    all_sections = re.finditer(r'##\s+(.+?)\n(.+?)(?=\n## |\Z)', body, re.DOTALL)
    
    specific_parts = []
    for sec in all_sections:
        sec_title = clean_heading(sec.group(1))
        sec_content = sec.group(2)
        
        # 检查是否是模板章节
        is_template = False
        for kw in template_section_keywords:
            if kw in sec_title:
                is_template = True
                break
        
        if not is_template and sec_title not in ['目录', '参考文件', 'Changelog', '参考资料']:
            specific_parts.append(sec_content)
    
    if specific_parts:
        return '\n\n'.join(specific_parts)
    
    # 如果都没有，返回全部内容
    return body


def generate_summary_from_specific_content(specific_content, title):
    """从文章特有内容生成概要"""
    
    best_sentence = ""
    best_score = -1
    
    # 提取段落
    paragraphs = extract_paragraphs(specific_content)
    
    for para in paragraphs:
        score = score_sentence(para, title)
        if score > best_score:
            best_score = score
            best_sentence = para
    
    # 如果没找到好的段落，尝试从列表项中提取
    if best_score < 30:
        bullets = re.findall(r'[-*•]\s+\**([^*]+?)\**[：:]\s*(.+?)(?=\n|$)', specific_content)
        for bullet_title, bullet_content in bullets:
            combined = bullet_title.strip() + '：' + bullet_content.strip()
            score = score_sentence(combined, title)
            if score > best_score:
                best_score = score
                best_sentence = combined
    
    if not best_sentence:
        # 基于标题生成
        best_sentence = generate_summary_from_title(title)
    
    return format_summary(best_sentence)


def extract_paragraphs(text):
    """提取文本中的段落"""
    paragraphs = []
    current = []
    in_code = False
    
    for line in text.split('\n'):
        s = line.strip()
        
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        
        if not s:
            if current:
                para = ' '.join(current).strip()
                if is_valid_para(para):
                    paragraphs.append(para)
                current = []
            continue
        
        # 跳过列表项
        if re.match(r'^[-*•]\s+', s) or re.match(r'^\d+[\.、)]\s+', s):
            if current:
                para = ' '.join(current).strip()
                if is_valid_para(para):
                    paragraphs.append(para)
                current = []
            continue
        
        # 跳过表格
        if s.startswith('|'):
            continue
        
        # 跳过加粗小标题
        if re.match(r'^\*\*[^*]{2,15}\*\*[：:]\s*$', s):
            continue
        
        # 跳过引用元信息
        if re.match(r'^>\s*[📅🏷️🔗📝⭐]', s):
            continue
        
        current.append(s)
    
    if current:
        para = ' '.join(current).strip()
        if is_valid_para(para):
            paragraphs.append(para)
    
    return paragraphs


def is_valid_para(text):
    if not text or len(text) < 20:
        return False
    if text.startswith('原文') and 'http' in text:
        return False
    if text.startswith('>'):
        return False
    return True


def score_sentence(text, title):
    """给句子打分"""
    score = 0
    
    # 长度
    if 40 <= len(text) <= 90:
        score += 30
    elif 25 <= len(text) <= 110:
        score += 15
    
    # 包含数据
    if re.search(r'\d+[%万亿亿元美元万]', text):
        score += 25
    
    # 包含年份
    if re.search(r'20\d{2}', text):
        score += 10
    
    # 与标题相关
    title_words = re.findall(r'[\u4e00-\u9fff]{2,}', title)
    title_relevance = 0
    for w in title_words:
        if w in text:
            title_relevance += 5
    score += min(title_relevance, 25)
    
    # 包含特有概念（不是通用模板词）
    template_words = ['规模化落地', '技术验证', '生产级应用', 'ROI', '效率优先', 'Agent崛起',
                      '参数规模', '推理效率', '大模型', 'AI']
    specific_count = 0
    total_content_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    for w in total_content_words:
        if w not in template_words and len(w) >= 2:
            specific_count += 1
    
    score += min(specific_count * 2, 20)
    
    # 减分项
    if text.startswith('>'):
        score -= 50
    if text.startswith('原文'):
        score -= 50
    if text.startswith('-') or text.startswith('*'):
        score -= 10
    
    return score


def generate_summary_from_title(title):
    """基于标题生成概要"""
    title_clean = remove_emoji(title)
    
    # 提取主题
    parts = re.split(r'[：:—\-｜|]', title_clean)
    
    if len(parts) >= 2:
        main_topic = parts[0].strip()
        sub_topic = parts[1].strip()
        return f"本文围绕{main_topic}主题，深入探讨{sub_topic}的核心内容、技术要点与实践价值。"
    else:
        return f"本文围绕{title_clean}展开深度分析，涵盖技术原理、应用实践与行业趋势等核心内容。"


def format_summary(text):
    """格式化为一句话，≤100字"""
    if not text:
        return text
    
    # 清理markdown
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 移除开头符号
    text = re.sub(r'^[>+▶️🔍📊\s\-•*]+', '', text)
    
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
        
        if result.endswith(('。', '！', '？', '!', '?')) and len(result) >= 25:
            break
    
    if not result:
        result = text[:97] + '...'
    
    result = result.strip()
    if not result.endswith(('。', '！', '？', '!', '?', '…', '...')):
        if len(result) < 98:
            result += '。'
        else:
            result = result[:96] + '...'
    
    if len(result) > 100:
        result = result[:97] + '...'
    
    return result


def generate_keywords_specific(specific_content, title, fm):
    """从文章特有内容生成关键词"""
    candidates = []  # (keyword, priority)
    seen = set()
    
    def add(kw, prio):
        kw = normalize_kw(kw.strip())
        if kw and kw not in seen and is_valid_kw(kw):
            candidates.append((kw, prio))
            seen.add(kw)
    
    # 1. 从标题提取（最高优先级）
    title_clean = remove_emoji(title)
    
    # 提取标题中的专有名词和技术术语
    title_terms = [
        'OLMo', 'Zabbix', 'WAIC', 'IDEA', 'T-EDGE', 'AWS', 're:Invent',
        'Dify', 'LLaMA', 'KTransformers', 'GPT', 'Claude', 'Gemini',
        'DeepSeek', 'Qwen', '通义千问', 'Llama',
        '京东双11', '天猫双11', '双11', '云栖大会', '乌镇峰会',
        '世界互联网大会', '世界人工智能大会',
        '医疗AI', 'AI电商', 'AI编程', '银发AI', '适老化',
        '提示词', '提示工程', 'RAG', 'Agent', '智能体',
        'MoE', 'Transformer', '微调', '多模态', '算力',
        '端侧推理', '企业级应用', '知识图谱',
        '具身智能', '自动驾驶', 'AIGC', '大模型',
        '开源', 'GPU', 'Token', 'NLP', 'CV',
        '程序员薪资', '裁员潮', 'AI股票',
        '飞书知识库', 'VSCode', 'PPT工具', '编程助手',
        'AI日报', 'AI周报', 'AI月报',
    ]
    
    for term in title_terms:
        if term.lower() in title_clean.lower():
            add(term, 100)
    
    # 从标题冒号后面的部分提取
    parts = re.split(r'[：:—\-｜|]', title_clean)
    if len(parts) >= 2:
        subtitle = parts[1].strip()
        # 提取2-4字词
        sub_words = re.findall(r'[\u4e00-\u9fff]{2,4}', subtitle)
        for w in sub_words:
            if is_valid_kw(w):
                add(w, 70)
    
    # 2. 从特有内容中提取高频技术词
    tech_patterns = [
        (r'OLMo', 10, 'OLMo'),
        (r'Zabbix', 10, 'Zabbix'),
        (r'WAIC|世界人工智能大会', 8, 'WAIC'),
        (r'Dify', 8, 'Dify'),
        (r'KTransformers', 10, 'KTransformers'),
        (r'LLaMA[-\s]?Factory', 8, 'LLaMA-Factory'),
        (r'GPT(?:-\d+(?:\.\d+)?)?', 6, 'GPT'),
        (r'Claude(?:\s*\d+\.?\d*)?', 6, 'Claude'),
        (r'Gemini(?:\s*\d+\.?\d*)?', 6, 'Gemini'),
        (r'DeepSeek|深度求索', 6, 'DeepSeek'),
        (r'通义千问|Qwen', 6, '通义千问'),
        (r'Llama|Llama\s*\d+', 6, 'Llama'),
        (r'MoE|混合专家', 5, 'MoE架构'),
        (r'Transformer', 5, 'Transformer架构'),
        (r'RAG|检索增强生成', 6, 'RAG'),
        (r'Agent|智能体', 5, 'AI Agent'),
        (r'AIGC|生成式AI', 5, 'AIGC'),
        (r'提示词|提示工程|Prompt', 5, '提示工程'),
        (r'多模态', 5, '多模态'),
        (r'微调|fine-tuning|LoRA|QLoRA', 5, '微调'),
        (r'算力', 4, '算力'),
        (r'GPU', 4, 'GPU'),
        (r'Token', 3, 'Token'),
        (r'大模型|大语言模型|LLM', 4, '大模型'),
        (r'开源', 4, '开源'),
        (r'医疗AI', 6, '医疗AI'),
        (r'AI电商|电商AI', 6, 'AI电商'),
        (r'AI编程|代码生成', 5, 'AI编程'),
        (r'银发AI|老年AI|适老化', 6, '银发AI'),
        (r'端侧推理', 4, '端侧推理'),
        (r'企业级|私有化部署', 4, '企业级应用'),
        (r'知识图谱', 4, '知识图谱'),
        (r'具身智能', 4, '具身智能'),
        (r'自动驾驶', 4, '自动驾驶'),
        (r'自然语言处理|NLP', 3, '自然语言处理'),
        (r'计算机视觉|CV', 3, '计算机视觉'),
        (r'云栖大会', 5, '云栖大会'),
        (r'乌镇峰会|世界互联网大会', 5, '乌镇峰会'),
        (r'双11|双十一', 5, '双11'),
        (r'程序员薪资', 5, '程序员薪资'),
        (r'裁员', 4, '科技裁员'),
        (r'AI股票', 4, 'AI股票'),
        (r'飞书', 4, '飞书知识库'),
        (r'VSCode', 5, 'VSCode'),
        (r'PPT', 4, 'AI生成PPT'),
        (r'编程助手|编码助手', 4, 'AI编程助手'),
    ]
    
    freq_scores = {}
    for pattern, weight, norm in tech_patterns:
        count = len(re.findall(pattern, specific_content, re.IGNORECASE))
        if count > 0:
            score = count * weight
            if norm in freq_scores:
                freq_scores[norm] += score
            else:
                freq_scores[norm] = score
    
    sorted_tech = sorted(freq_scores.items(), key=lambda x: x[1], reverse=True)
    for kw, score in sorted_tech:
        if score >= 10:
            add(kw, 50 + min(score, 30))
    
    # 3. 从特有内容中提取领域关键词
    domain_keywords = re.findall(r'[\u4e00-\u9fff]{2,4}', specific_content)
    domain_freq = {}
    for w in domain_keywords:
        if is_valid_kw(w) and len(w) >= 2:
            domain_freq[w] = domain_freq.get(w, 0) + 1
    
    sorted_domain = sorted(domain_freq.items(), key=lambda x: x[1], reverse=True)
    for kw, count in sorted_domain[:20]:
        if count >= 3:
            add(kw, 30 + min(count * 2, 20))
    
    # 选择最终关键词
    final = []
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    for kw, prio in candidates:
        if len(final) >= 5:
            break
        
        # 避免过于相似
        too_similar = False
        for existing in final:
            if kw in existing or existing in kw:
                # 保留更长、更具体的
                if len(kw) <= len(existing):
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


def normalize_kw(kw):
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
        'LoRA': '微调',
        'QLoRA': '微调',
        'fine-tuning': '微调',
    }
    return mapping.get(kw, kw)


def is_valid_kw(kw):
    if not kw or len(kw) < 2:
        return False
    if re.match(r'^\d+$', kw):
        return False
    if re.match(r'^(19|20)\d{2}$', kw):
        return False
    
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
        '内容', '文章', '本文', '我们', '他们',
        '可以', '能够', '需要', '已经', '正在',
        '一个', '一种', '一些', '这个', '那个',
        '以及', '还有', '包括', '包含', '涉及',
        '通过', '基于', '对于', '关于', '随着',
        '因此', '所以', '但是', '然而', '而且',
        '市场', '产业', '行业', '企业', '公司',
        '产品', '服务', '用户', '客户',
        '功能', '性能', '效果', '效率',
        '问题', '挑战', '风险', '机遇',
        '未来', '当前', '目前', '现在',
        '中国', '全球', '世界', '美国',
        '大会', '峰会', '论坛', '展会',
        '发布', '推出', '上线', '开源',
        '合作', '投资', '融资', '收购',
        '增长', '下降', '提升', '降低',
    }
    
    if kw in stopwords:
        return False
    
    return True


def fix_toc(body):
    """修复目录"""
    lines = body.split('\n')
    headings = []
    
    exclude = [
        '目录', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '延伸阅读', '相关文章', '相关素材',
        '快速导读', '核心要点', '内容', '执行摘要', '关键词标签',
        '内容评级', 'import素材融合', '阅读建议', '关键数据',
        '适合人群', '阅读时长', '难度等级',
    ]
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            clean = clean_heading(title)
            
            if not clean or len(clean) < 2:
                continue
            
            should_exclude = False
            for kw in exclude:
                if kw.lower() in clean.lower():
                    should_exclude = True
                    break
            
            if not should_exclude:
                headings.append(clean)
    
    seen = set()
    unique = []
    for h in headings:
        if h.lower() not in seen:
            seen.add(h.lower())
            unique.append(h)
    
    if len(unique) < 3:
        return ""
    
    toc = ["## 📑 目录", ""]
    for h in unique:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', h)
        toc.append(f"- [{h}](#{anchor})")
    
    toc.append("")
    return '\n'.join(toc)


def clean_h2_headings(body):
    """清理二级及以下标题的emoji"""
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
            
            if level >= 2:
                title_text = s[idx:].strip()
                clean_title = clean_heading(title_text)
                if clean_title:
                    cleaned.append('#' * level + ' ' + clean_title)
                else:
                    cleaned.append(line)
            else:
                cleaned.append(line)
        else:
            cleaned.append(line)
    
    return '\n'.join(cleaned)


def process_file(filepath):
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    
    if not fm:
        print(f"  ⚠️  无frontmatter: {filename}")
        return False
    
    # 提取标题
    title_match = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename.replace('.md', '')
    
    # 1. 清理二级标题emoji
    body = clean_h2_headings(body)
    
    # 2. 提取文章特有内容
    specific_content = extract_article_specific_content(body)
    
    # 3. 生成概要（从特有内容）
    summary = generate_summary_from_specific_content(specific_content, title)
    
    # 4. 生成关键词（从特有内容）
    keywords = generate_keywords_specific(specific_content, title, fm)
    
    # 5. 修复目录
    toc = fix_toc(body)
    
    # 6. 重建文档
    lines = body.split('\n')
    h1_idx = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            h1_idx = i
            break
    
    if h1_idx == -1:
        print(f"  ⚠️  无H1: {filename}")
        return False
    
    # 找到正文开始
    content_start = h1_idx + 1
    in_toc = False
    for i in range(h1_idx + 1, min(h1_idx + 80, len(lines))):
        stripped = lines[i].strip()
        
        if stripped.startswith('> **概要**:') or stripped.startswith('> **关键词**:'):
            content_start = i + 1
            continue
        
        if stripped.startswith('## ') and '目录' in clean_heading(stripped[3:]):
            in_toc = True
            content_start = i + 1
            continue
        
        if in_toc:
            if stripped.startswith('## ') and not stripped.startswith('### '):
                in_toc = False
                content_start = i
                break
            content_start = i + 1
            continue
        
        if stripped and not stripped.startswith('>') and not in_toc:
            content_start = i
            break
    
    # 构建新body
    new_body = [f"# {title}", ""]
    new_body.append(f"> **概要**: {summary}")
    new_body.append(f"> **关键词**: {keywords}")
    new_body.append("")
    
    if toc:
        new_body.append(toc)
    
    for i in range(content_start, len(lines)):
        new_body.append(lines[i])
    
    new_body_text = '\n'.join(new_body)
    
    # 更新frontmatter
    new_fm = re.sub(
        r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
        f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'",
        fm,
        flags=re.MULTILINE
    )
    
    final_text = f"---\n{new_fm}\n---\n\n{new_body_text}"
    final_text = re.sub(r'\n{4,}', '\n\n\n', final_text)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"  ✅ {filename[:50]}...")
    print(f"     概要: {summary[:65]}...")
    print(f"     关键词: {keywords}")
    return True


def main():
    if len(sys.argv) < 2:
        print('用法: python3 ultimate_optimize.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件')
    print()
    
    success = 0
    fail = 0
    
    for fp in md_files:
        try:
            if process_file(str(fp)):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ❌ {Path(fp).name}: {e}")
            import traceback
            traceback.print_exc()
            fail += 1
    
    print()
    print('=' * 60)
    print(f'📊 终极优化完成: {success} 成功, {fail} 失败')
    print('=' * 60)


if __name__ == '__main__':
    main()
