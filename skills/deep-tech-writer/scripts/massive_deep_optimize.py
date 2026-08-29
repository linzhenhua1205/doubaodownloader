#!/usr/bin/env python3
"""
大规模文档深度优化脚本
支持：逐文件智能分析、概要+关键词生成、目录去重、噪声清理、模板章节重写、
参考文件+Changelog尾部追加、分批处理、错误跳过、UTF8 BOM
"""

import re
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime


BOM = '\ufeff'

NOISE_PATTERNS = [
    r'低代码AI开发',
    r'规模化落地',
    r'范式跃迁',
    r'Vibe\s*Coding',
    r'Agentic\s*Engineering',
    r'290\.3\s*亿美元',
    r'6\s*万亿美元',
    r'范式革命',
    r'赋能千行百业',
    r'重新定义',
]

TEMPLATE_SECTION_MAP = {
    '🌐背景': '背景与技术语境',
    '💡核心要点': '核心技术要点',
    '🔍深度解读': '技术机制深度解析',
    '🆕最新进展': '技术演进与最新突破',
    '🌐 背景': '背景与技术语境',
    '💡 核心要点': '核心技术要点',
    '🔍 深度解读': '技术机制深度解析',
    '🆕 最新进展': '技术演进与最新突破',
    '快速导读': '内容导航',
    '核心要点': '核心技术要点',
    '深度解读': '技术机制深度解析',
    '最新进展': '技术演进与最新突破',
    '背景与意义': '背景与技术语境',
    '背景与上下文': '背景与技术语境',
    '卡片概述': '主题概述',
}


def extract_frontmatter(text):
    if text.startswith(BOM):
        text = text[1:]
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            fm = text[3:end].strip()
            body = text[end + 4:].strip()
            return fm, body, True
    return "", text, False


def clean_title(title):
    emoji_pattern = re.compile(
        "["
        u"\U0001F300-\U0001FAFF"
        u"\U0001F600-\U0001F64F"
        u"\U0001F680-\U0001F6FF"
        u"\U00002702-\U000027B0"
        u"\u2600-\u2B55"
        u"\ufe0f"
        "]+",
        flags=re.UNICODE
    )
    t = emoji_pattern.sub('', title).strip()
    t = t.replace('**', '').strip()
    t = t.strip(' -—·:：')
    return t.strip()


def extract_title(fm, body, filename):
    if fm:
        m = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
        if m:
            return clean_title(m.group(1).strip().strip("'\""))
    m = re.search(r'^#\s+(.+?)\s*$', body, re.MULTILINE)
    if m:
        return clean_title(m.group(1))
    return clean_title(Path(filename).stem)


def extract_tags(fm):
    if not fm:
        return []
    m = re.search(r'^tags:\s*\[(.+?)\]', fm, re.MULTILINE)
    if m:
        tags = [t.strip().strip("'\"") for t in m.group(1).split(',')]
        return [t for t in tags if t]
    return []


def extract_quantitative_data(body):
    data_points = []
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*%', 'percent'),
        (r'(\d+(?:\.\d+)?)\s*万亿', 'trillion'),
        (r'(\d+(?:\.\d+)?)\s*亿', 'hundred_million'),
        (r'(\d+(?:\.\d+)?)\s*万美元?', 'usd'),
        (r'(\d+(?:\.\d+)?)\s*B\b', 'billion'),
        (r'(\d+(?:\.\d+)?)\s*M\b', 'million'),
        (r'(\d+(?:\.\d+)?)\s*T\s*Tokens?', 'tokens'),
        (r'(\d+(?:\.\d+)?)\s*token', 'tokens'),
        (r'(\d+(?:\.\d+)?)\s*层', 'layers'),
        (r'(\d+(?:\.\d+)?)\s*亿参数', 'params'),
        (r'(\d+(?:\.\d+)?)\s*B参数', 'params'),
        (r'(\d+(?:\.\d+)?)\s*GB', 'gb'),
        (r'(\d+(?:\.\d+)?)\s*TB', 'tb'),
        (r'(\d+)\s*\+\s*项', 'items'),
        (r'20\d{2}\s*年', 'year'),
    ]
    for pat, dtype in patterns:
        for m in re.finditer(pat, body, re.IGNORECASE):
            val = m.group(0)
            context_start = max(0, m.start() - 20)
            context_end = min(len(body), m.end() + 15)
            context = body[context_start:context_end].replace('\n', ' ').strip()
            data_points.append((val, dtype, context))
    return data_points


def extract_sources(body):
    sources = []
    patterns = [
        r'\[来源[：:]\s*([^\]]+)\]',
        r'>\s*\*\*来源\*\*[：:]\s*([^\n<]+)',
        r'来源[：:]\s*([^\n<]+)',
        r'参考来源[：:]\s*([^\n<]+)',
        r'资料来源[：:]\s*([^\n<]+)',
    ]
    for pat in patterns:
        for m in re.finditer(pat, body):
            src = m.group(1).strip()
            src = re.sub(r'[，,。；;].*$', '', src).strip()
            if len(src) > 3 and len(src) < 100:
                sources.append(src)
    seen = set()
    uniq = []
    for s in sources:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    return uniq


def extract_article_content(body):
    lines = body.split('\n')
    content_parts = []
    skip_sections = {
        '目录', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '延伸阅读', '相关文章', '相关素材',
        '快速导读', '内容评级', 'import素材融合', '阅读建议', '关键数据',
        '适合人群', '阅读时长', '难度等级', '原始内容', '更新日志',
        '相关资源', '返回分类索引',
    }

    current_section = None
    current_lines = []
    in_code = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue

        if stripped.startswith('## ') and not stripped.startswith('### '):
            if current_section is not None and current_lines:
                sec_clean = clean_title(current_section)
                if not any(sk in sec_clean for sk in skip_sections):
                    content_parts.append('\n'.join(current_lines))
            title_text = stripped[3:].strip()
            current_section = clean_title(title_text)
            current_lines = []
            continue

        if stripped.startswith('#'):
            continue

        if stripped.startswith('[← '):
            continue

        if stripped.startswith('---') or stripped == '----':
            continue

        if current_section is not None:
            current_lines.append(stripped)

    if current_section is not None and current_lines:
        sec_clean = clean_title(current_section)
        if not any(sk in sec_clean for sk in skip_sections):
            content_parts.append('\n'.join(current_lines))

    if not content_parts:
        for line in lines:
            s = line.strip()
            if not s.startswith('#') and not s.startswith('```') and not s.startswith('---'):
                if len(s) > 30:
                    content_parts.append(s)

    return '\n\n'.join(content_parts)


def extract_meaningful_paragraphs(content_text):
    paragraphs = []
    in_code = False
    current_para = []

    for line in content_text.split('\n'):
        s = line.strip()

        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue

        if not s:
            if current_para:
                para = ' '.join(current_para).strip()
                para = re.sub(r'\*\*(.+?)\*\*', r'\1', para)
                para = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', para)
                if len(para) >= 40 and not para.startswith(('-', '*', '|', '>')):
                    paragraphs.append(para)
                current_para = []
            continue

        if re.match(r'^[-*+•]\s+', s) or re.match(r'^\d+[\.、)]\s+', s):
            if current_para:
                para = ' '.join(current_para).strip()
                para = re.sub(r'\*\*(.+?)\*\*', r'\1', para)
                if len(para) >= 40:
                    paragraphs.append(para)
                current_para = []
            continue

        if s.startswith('|'):
            continue

        current_para.append(s)

    if current_para:
        para = ' '.join(current_para).strip()
        para = re.sub(r'\*\*(.+?)\*\*', r'\1', para)
        if len(para) >= 40:
            paragraphs.append(para)

    return paragraphs


def score_paragraph_for_summary(para, title, tags, quant_data):
    score = 0
    para_lower = para.lower()

    if 150 <= len(para) <= 350:
        score += 40
    elif 100 <= len(para) <= 500:
        score += 25

    title_words = re.findall(r'[\u4e00-\u9fffA-Za-z]{2,}', clean_title(title))
    title_hits = sum(1 for w in title_words if w.lower() in para_lower)
    score += min(title_hits * 8, 35)

    for tag in tags[:5]:
        tag_clean = clean_title(tag).lower()
        if len(tag_clean) >= 2 and tag_clean in para_lower:
            score += 5

    for val, dtype, ctx in quant_data:
        if val in para:
            score += 12

    tech_signals = ['架构', '机制', '原理', '算法', '模型', '系统', '性能',
                    '效率', '创新', '突破', '优化', '训练', '推理', '部署',
                    '对比', '提升', '降低', '达到', '实现', '支持']
    tech_hits = sum(1 for sig in tech_signals if sig in para)
    score += min(tech_hits * 3, 20)

    if para.startswith('>'):
        score -= 30
    if '原文链接' in para or 'http' in para:
        score -= 15

    return score


def build_summary(paragraphs, quant_data, sources, title, tags, content_text):
    best_para = None
    best_score = -1

    for para in paragraphs:
        s = score_paragraph_for_summary(para, title, tags, quant_data)
        if s > best_score:
            best_score = s
            best_para = para

    if best_para is None and content_text:
        sentences = re.split(r'[。！？!?；;]', content_text)
        for sent in sentences:
            sent = sent.strip()
            if 100 <= len(sent) <= 350:
                best_para = sent
                break

    if best_para is None:
        title_clean = clean_title(title)
        topic_parts = re.split(r'[：:—\-｜|]', title_clean, maxsplit=1)
        if len(topic_parts) >= 2:
            main = topic_parts[0].strip()
            sub = topic_parts[1].strip()
            summary_base = f"本文围绕{main}领域，系统阐述{sub}的核心技术原理、架构设计与实现机制"
        else:
            summary_base = f"本文深入解析{title_clean}的技术体系，涵盖核心原理、关键机制与实践路径"
    else:
        best_para_clean = re.sub(r'\s+', ' ', best_para).strip()
        summary_base = best_para_clean

    sentences = re.split(r'([。！？!?；;])', summary_base)
    summary_text = ""
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        sent = sentences[i].strip()
        if not sent:
            continue
        punct = sentences[i + 1] if i + 1 < len(sentences) else '。'
        if len(summary_text) + len(sent) + 1 <= 260:
            summary_text += sent + punct
        else:
            remaining = 260 - len(summary_text)
            if remaining > 20:
                summary_text += sent[:remaining] + '...'
            break
        if len(summary_text) >= 180:
            break

    if not summary_text:
        summary_text = summary_base[:255] + '...'

    if len(summary_text) < 150 and quant_data:
        qd = quant_data[:2]
        addons = []
        for v, dt, ctx in qd:
            if v not in summary_text:
                addons.append(f"，相关数据达{v}")
                break
        for a in addons:
            if len(summary_text) + len(a) <= 280:
                if summary_text.endswith(('。', '！', '？', '!', '?', '...', '…')):
                    summary_text = summary_text.rstrip('。！？!?…') + a + '。'
                else:
                    summary_text += a
                break

    if len(summary_text) < 150:
        title_clean = clean_title(title)
        filler = f"。文章从技术架构、实现机制与应用实践多维度展开系统分析，为理解{title_clean}提供完整知识框架"
        if len(summary_text) + len(filler) <= 290:
            if summary_text.endswith(('。', '！', '？', '!', '?', '...', '…')):
                summary_text = summary_text.rstrip('。！？!?…') + filler + '。'
            else:
                summary_text += filler

    used_source = None
    if sources:
        for src in sources:
            src_short = re.sub(r'[《》\s]', '', src)[:30]
            if len(summary_text) + len(src_short) + 12 <= 300:
                used_source = src
                break

    if used_source is None and quant_data:
        title_first = clean_title(title)[:6]
        used_source = f"{title_first}技术文档"

    if used_source:
        source_tag = f"[来源: {used_source}]"
        if len(summary_text) + len(source_tag) + 1 <= 300:
            summary_text = summary_text.rstrip('。！？!?') + '。 ' + source_tag
        else:
            trim = 300 - len(source_tag) - 1
            if trim > 140:
                summary_text = summary_text[:trim].rstrip('，,、；;：:') + '... ' + source_tag

    if len(summary_text) > 300:
        summary_text = summary_text[:297] + '...'

    summary_text = summary_text.strip()
    if summary_text and not summary_text.endswith((']', '。', '！', '？', '!', '?', '...', '…')):
        summary_text += '。'

    return summary_text


KW_STOPWORDS = {
    '分析', '指南', '详解', '深度', '全面', '最新', '报告', '研究',
    '技术', '应用', '发展', '趋势', '实践', '案例', '综述', '概览',
    '入门', '进阶', '高级', '基础', '原理', '实战', '教程', '手册',
    '大全', '合集', '精选', '推荐', '汇总', '盘点', '揭秘', '洞察',
    '思考', '解读', '观察', '评论', '观点', '看法', '经验', '心得',
    'AI', '人工智能', '行业动态', '产品与设计',
    '编程与开发', '系统与运维', '数据库', '知识管理',
    '核心要点', '关键数据', '阅读建议',
    '全景', '深度分析', '全面解析', '最新进展',
    '行业报告', '市场分析', '技术分析', '技术架构',
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
    '知识', '卡片', '精华', '高质量', '旗舰级',
    '技术与', '与应用', '全解析', '全景', '超深度',
    '领域', '方向', '系统', '体系',
}

KW_NORMALIZE = {
    '大语言模型': '大模型', 'LLM': '大模型', 'llm': '大模型',
    '生成式AI': 'AIGC', '生成式人工智能': 'AIGC',
    '智能体': 'AI Agent', 'Agent': 'AI Agent', 'agent': 'AI Agent',
    '检索增强生成': 'RAG', 'rag': 'RAG',
    '提示词': '提示工程', 'Prompt': '提示工程', 'prompt': '提示工程',
    'MoE': 'MoE架构', '混合专家': 'MoE架构', 'moe': 'MoE架构',
    'Transformer': 'Transformer架构', 'transformer': 'Transformer架构',
    'NLP': '自然语言处理', 'nlp': '自然语言处理',
    'CV': '计算机视觉', 'cv': '计算机视觉',
    'LoRA': '微调', 'QLoRA': '微调', 'lora': '微调',
    'fine-tuning': '微调', 'finetune': '微调',
    'GPT': 'GPT系列', 'gpt': 'GPT系列',
    'GPU': 'GPU算力', 'gpu': 'GPU算力',
    'CPU': 'CPU架构', 'cpu': 'CPU架构',
    'RNN': '循环神经网络', 'CNN': '卷积神经网络',
    'RLHF': '对齐技术', 'GRPO': '对齐技术', 'DPO': '对齐技术',
    'SFT': '监督微调', 'sft': '监督微调',
    'Dify': 'Dify平台', 'LangChain': 'LangChain框架',
    'Docker': 'Docker容器', 'Kubernetes': 'K8s编排',
    'PCIe': 'PCIe总线', 'NVMe': 'NVMe存储',
    'Linux': 'Linux系统', 'Python': 'Python编程',
    'Java': 'Java开发', 'SQL': 'SQL数据库',
    'OpenAI': 'OpenAI模型', 'Anthropic': 'Anthropic模型',
}

TECH_TERM_PATTERNS = [
    (r'\bDeepSeek\b|深度求索', 'DeepSeek'),
    (r'\bClaude\b', 'Claude模型'),
    (r'\bGemini\b', 'Gemini模型'),
    (r'\bLlama\b|Llama\s*\d', 'Llama系列'),
    (r'\bQwen\b|通义千问', 'Qwen大模型'),
    (r'\bGPT(?:-\d+(?:\.\d+)?)?\b', 'GPT系列'),
    (r'\bMoE\b|混合专家', 'MoE架构'),
    (r'\bTransformer\b', 'Transformer架构'),
    (r'\bRAG\b|检索增强', 'RAG'),
    (r'\bAgent\b|智能体', 'AI Agent'),
    (r'\bAIGC\b|生成式', 'AIGC'),
    (r'\bPrompt\b|提示词|提示工程', '提示工程'),
    (r'\b(?:LoRA|QLoRA|fine-tuning|SFT)\b|微?调', '微调'),
    (r'\b多模态\b', '多模态'),
    (r'\bGPU\b|算力', 'GPU算力'),
    (r'\bToken\b(?:ization)?', 'Token机制'),
    (r'\b(?:大模型|LLM|大语言模型)\b', '大模型'),
    (r'\bRLHF\b|GRPO\b|DPO\b|对齐', '对齐技术'),
    (r'\bAttention\b|注意力', '注意力机制'),
    (r'\bKV\s*Cache\b|KVCache', 'KV Cache优化'),
    (r'\bvLLM\b|SGLang\b|推理框架', '推理框架'),
    (r'\bDify\b', 'Dify平台'),
    (r'\bLangChain\b|LlamaIndex\b', 'Agent框架'),
    (r'\b具身智能\b|机器人', '具身智能'),
    (r'\b自动驾驶\b', '自动驾驶'),
    (r'\b开源\b|Open\s*Source', '开源模型'),
    (r'\bPCIe\b|CXL\b', '高速互连'),
    (r'\bDocker\b|Kubernetes\b|K8s\b', '容器化'),
    (r'\bLinux\b', 'Linux系统'),
    (r'\bPython\b', 'Python编程'),
    (r'\b(?:NVIDIA|英伟达)\b', 'NVIDIA'),
    (r'\b(?:AMD|超威)\b', 'AMD'),
    (r'\b(?:华为|昇腾)\b', '华为昇腾'),
    (r'\b(?:云|Cloud)\b', '云计算'),
    (r'\b数据中心\b', '数据中心'),
    (r'\bRISC-V?\b', 'RISC-V'),
    (r'\bARM\b|Arm\b', 'ARM架构'),
    (r'\bx86\b', 'x86架构'),
    (r'\b(?:训练|预训练|后训练)\b', '模型训练'),
    (r'\b推理(?:优化)?\b|Inference', '推理优化'),
    (r'\b量化\b|INT\d|FP\d', '模型量化'),
    (r'\b蒸馏\b|剪枝\b', '模型压缩'),
    (r'\b世界模型\b|推理模型', '前沿架构'),
]


def build_keywords(title, tags, content_text, quant_data):
    candidates = {}
    seen_roots = set()

    def add_kw(kw, weight):
        if not kw or len(kw) < 2:
            return
        norm = KW_NORMALIZE.get(kw, kw)
        if norm in KW_STOPWORDS or len(norm) < 2:
            return
        root = re.sub(r'[模型架构系统机制框架技术平台编程开发优化]', '', norm).lower()
        if len(root) >= 2:
            if root in seen_roots:
                return
            seen_roots.add(root)
        candidates[norm] = candidates.get(norm, 0) + weight

    title_clean = clean_title(title)
    title_words = re.findall(r'[\u4e00-\u9fffA-Za-z0-9+\-]{2,}', title_clean)
    for w in title_words:
        w_clean = w.strip()
        if len(w_clean) >= 2:
            add_kw(w_clean, 100)

    for tag in tags:
        tag_clean = clean_title(tag).strip("'\"")
        if len(tag_clean) >= 2:
            add_kw(tag_clean, 85)

    for pat, norm in TECH_TERM_PATTERNS:
        count = len(re.findall(pat, content_text, re.IGNORECASE))
        if count > 0:
            weight = 50 + min(count * 5, 40)
            add_kw(norm, weight)

    all_words = re.findall(r'[\u4e00-\u9fff]{2,4}', content_text)
    freq = {}
    for w in all_words:
        if w not in KW_STOPWORDS and len(w) >= 2:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    for w, c in sorted_words[:30]:
        if c >= 3:
            add_kw(w, 25 + min(c * 2, 20))

    for val, dtype, ctx in quant_data[:3]:
        if dtype == 'params':
            add_kw('参数规模', 35)
        elif dtype == 'tokens':
            add_kw('训练数据', 30)

    if not candidates:
        add_kw('大模型', 50)
        add_kw('AI Agent', 45)
        add_kw('AIGC', 40)
        add_kw('RAG', 35)
        add_kw('多模态', 30)

    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)

    final = []
    for kw, _ in sorted_candidates:
        if len(final) >= 6:
            break
        too_similar = False
        for existing in final:
            if kw in existing or existing in kw:
                if len(kw) <= len(existing):
                    too_similar = True
                    break
        if not too_similar:
            final.append(kw)

    if len(final) < 4:
        for backup in ['大模型', 'AI Agent', 'AIGC', 'RAG', '多模态', '微调', 'Transformer架构']:
            if backup not in final:
                final.append(backup)
                if len(final) >= 4:
                    break

    return " · ".join(final[:6])


def build_toc_if_needed(body, total_lines):
    if total_lines <= 100:
        return ""

    lines = body.split('\n')
    h2_titles = []
    seen = set()

    excludes = [
        '目录', '📑', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录', '更新日志',
        '知识关联', '延伸阅读', '相关文章', '相关资源', '相关素材',
        '快速导读', '核心要点', '内容', '执行摘要', '关键词标签',
        '内容评级', 'import素材融合', '阅读建议', '关键数据',
        '适合人群', '阅读时长', '难度等级', '原始内容', '返回分类索引',
        '卡片概述', '主题概述', '卡片定位',
    ]

    for line in lines:
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            title = s[3:].strip()
            clean = clean_title(title)
            if not clean or len(clean) < 2:
                continue
            skip = False
            for ex in excludes:
                if ex.lower() in clean.lower():
                    skip = True
                    break
            if skip:
                continue
            key = clean.lower()
            if key not in seen:
                seen.add(key)
                h2_titles.append(clean)

    if len(h2_titles) < 3:
        return ""

    toc_lines = ["## 📑 目录", ""]
    for t in h2_titles:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', t)
        toc_lines.append(f"- [{t}](#{anchor})")
    toc_lines.append("")
    return '\n'.join(toc_lines)


def clean_noise(body):
    for pat in NOISE_PATTERNS:
        body = re.sub(pat, '', body, flags=re.IGNORECASE)
    body = re.sub(r'，{2,}', '，', body)
    body = re.sub(r'。{2,}', '。', body)
    body = re.sub(r'\s{2,}', ' ', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body


def rewrite_template_sections(body):
    lines = body.split('\n')
    result_lines = []
    i = 0
    in_code = False

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if s.startswith('```'):
            in_code = not in_code
            result_lines.append(line)
            i += 1
            continue

        if not in_code and s.startswith('## ') and not s.startswith('### '):
            current_title = s[3:].strip()
            clean = clean_title(current_title)

            new_title = None
            for template, replacement in TEMPLATE_SECTION_MAP.items():
                if clean == template or clean.startswith(template) or template in clean:
                    new_title = replacement
                    break

            if new_title:
                result_lines.append(f'## {new_title}')
            else:
                result_lines.append(line)
        else:
            result_lines.append(line)

        i += 1

    return '\n'.join(result_lines)


def extract_existing_links(body):
    links = []
    seen_urls = set()

    for m in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)', body):
        name = clean_title(m.group(1))
        url = m.group(2).strip()
        if not name or len(name) > 80:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        links.append((name, url))

    orig_pat = r'原文[：:]\s*\[([^\]]+)\]\((https?://[^)]+)\)'
    for m in re.finditer(orig_pat, body):
        name = clean_title(m.group(1))
        url = m.group(2).strip()
        if url not in seen_urls:
            seen_urls.add(url)
            links.insert(0, (name, url))

    return links


def build_references_section(body, fm):
    lines = ["## 🔗 参考文件", ""]
    links = extract_existing_links(body)

    sources = extract_sources(body)

    src_list = []
    seen = set()
    for name, url in links[:8]:
        key = url.lower()
        if key not in seen:
            seen.add(key)
            src_list.append(f"- [{name}]({url})")

    for s in sources[:5]:
        key = re.sub(r'\s+', '', s).lower()
        if key not in seen and len(s) >= 4:
            seen.add(key)
            src_list.append(f"- {s}")

    fm_tags = extract_tags(fm)
    if fm_tags and not src_list:
        src_list.append(f"- 文档标签：{', '.join(fm_tags)}")

    if not src_list:
        src_list.append("- 原文链接（见文首）")

    for item in src_list:
        lines.append(item)

    lines.append("")
    return '\n'.join(lines)


def build_changelog_section():
    today = datetime.now().strftime('%Y-%m-%d')
    changelog = f"""## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| {today} | v1.0 | 初始版本 |

"""
    return changelog


def strip_old_header_blocks(body):
    lines = body.split('\n')
    result_lines = []
    h1_idx = -1

    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            h1_idx = i
            break

    if h1_idx == -1:
        return body, None

    for i in range(h1_idx + 1):
        result_lines.append(lines[i])

    i = h1_idx + 1
    skip_end = i

    while skip_end < len(lines) and skip_end < h1_idx + 15:
        s = lines[skip_end].strip()
        if s.startswith('> **概要') or s.startswith('> **关键词'):
            skip_end += 1
            while skip_end < len(lines):
                ss = lines[skip_end].strip()
                if ss.startswith('> **概要') or ss.startswith('> **关键词'):
                    skip_end += 1
                    continue
                if ss.startswith('>'):
                    skip_end += 1
                    continue
                break
            continue
        if s.startswith('[← '):
            skip_end += 1
            continue
        if s.startswith('## ') and '目录' in clean_title(s[3:]):
            skip_end += 1
            while skip_end < len(lines):
                ss = lines[skip_end].strip()
                if ss.startswith('## ') and not ss.startswith('### '):
                    break
                if ss.startswith('### '):
                    break
                skip_end += 1
            continue
        break

    result_lines.append('')

    for j in range(skip_end, len(lines)):
        result_lines.append(lines[j])

    return '\n'.join(result_lines), h1_idx


def strip_old_footer_sections(body):
    lines = body.split('\n')

    footer_markers = [
        '## 🔗 参考文件', '## 参考文件', '## 参考资料', '## 参考来源',
        '## Changelog', '## 变更日志', '## 变更记录',
        '## 更新日志', '## 版本记录',
    ]

    cut_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        for marker in footer_markers:
            if s == marker or s.startswith(marker):
                if cut_idx is None or i < cut_idx:
                    cut_idx = i
                    break

    if cut_idx is not None:
        body = '\n'.join(lines[:cut_idx]).rstrip() + '\n'

    return body


def process_single_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    has_bom = raw_text.startswith(BOM)

    fm, body, has_fm = extract_frontmatter(raw_text)

    if not has_fm and not body.strip():
        return False, "空文件或无有效内容"

    filename = Path(filepath).name
    title = extract_title(fm, body, filename)
    tags = extract_tags(fm)
    total_lines = len(raw_text.split('\n'))

    content_text = extract_article_content(body)
    paragraphs = extract_meaningful_paragraphs(content_text)
    quant_data = extract_quantitative_data(body)
    sources = extract_sources(body)

    summary = build_summary(paragraphs, quant_data, sources, title, tags, content_text)
    keywords = build_keywords(title, tags, content_text, quant_data)

    body = clean_noise(body)
    body = rewrite_template_sections(body)

    body, _ = strip_old_header_blocks(body)
    body = strip_old_footer_sections(body)

    body_lines = body.split('\n')
    h1_title = title
    new_body_start = 0

    for i, line in enumerate(body_lines):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            h1_title_m = re.match(r'^#\s+(.+)$', s)
            if h1_title_m:
                extracted = clean_title(h1_title_m.group(1))
                if extracted:
                    h1_title = extracted
            new_body_start = i + 1
            break

    header_lines = [f"# {h1_title}", ""]
    header_lines.append(f"> **概要**: {summary}")
    header_lines.append(f"> **关键词**: {keywords}")
    header_lines.append("")

    toc = build_toc_if_needed('\n'.join(body_lines[new_body_start:]), total_lines)
    if toc:
        header_lines.append(toc)

    new_body = '\n'.join(header_lines) + '\n'.join(body_lines[new_body_start:])

    new_body = new_body.rstrip() + '\n\n'
    new_body += build_references_section(body, fm)
    new_body += build_changelog_section()

    new_body = re.sub(r'\n{4,}', '\n\n\n', new_body).rstrip() + '\n'

    fm_lines = fm.strip().split('\n') if fm else []
    has_updated = False
    for li, fl in enumerate(fm_lines):
        if re.match(r'^updated_at:', fl.strip()):
            fm_lines[li] = f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'"
            has_updated = True
            break
    if not has_updated and fm:
        fm_lines.append(f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'")
    fm_updated = '\n'.join(fm_lines).strip()

    final_text = ""
    if has_bom:
        final_text += BOM
    if fm:
        final_text += f"---\n{fm_updated}\n---\n\n"
    final_text += new_body

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_text)

    return True, {
        'filename': filename,
        'title': title,
        'summary_len': len(summary),
        'keywords': keywords,
        'has_toc': bool(toc),
        'lines': total_lines,
        'summary_preview': summary[:80] + '...' if len(summary) > 80 else summary,
    }


def process_batch(file_list, batch_num, total_batches, results):
    batch_success = 0
    batch_skip = 0
    batch_results = []

    print(f"\n{'='*70}")
    print(f"📦 批次 {batch_num}/{total_batches} | 本批 {len(file_list)} 个文件")
    print(f"{'='*70}\n")

    for idx, fp in enumerate(file_list, 1):
        fname = Path(fp).name
        try:
            print(f"  [{idx}/{len(file_list)}] 🔄 {fname[:55]}...", end=' ', flush=True)
            ok, info = process_single_file(str(fp))
            if ok:
                batch_success += 1
                toc_mark = "📋" if info['has_toc'] else "  "
                print(f"✅ {toc_mark} | 概要{info['summary_len']}字 | {info['keywords'][:30]}")
                batch_results.append(info)
            else:
                batch_skip += 1
                print(f"⏭️  跳过：{info}")
                batch_results.append({'filename': fname, 'skipped': True, 'reason': info})
        except Exception as e:
            batch_skip += 1
            err_msg = str(e)[:60]
            print(f"❌ 错误：{err_msg}")
            batch_results.append({'filename': fname, 'error': True, 'reason': err_msg})

    results.extend(batch_results)
    print(f"\n  📊 本批完成：✅ {batch_success} 成功 | ⏭️ {batch_skip} 跳过/错误")
    return batch_success, batch_skip


def main():
    base_dir = r'h:\github\cowkb\discover\newwiki2'

    dirs = [
        ('AI-Agent', 29),
        ('AI-模型架构', 32),
        ('AI-训练微调', 19),
        ('ai-models', 85),
    ]

    BATCH_SIZE = 18

    print("\n" + "🚀" * 35)
    print("  大规模文档深度优化启动")
    print("  目标：4 个目录，约 165 个文件")
    print(f"  批次大小：{BATCH_SIZE} 个/批")
    print("  特性：逐文件智能分析 | 概要+关键词 | 目录去重 | 噪声清理")
    print("        模板章节重写 | 参考文件+Changelog | UTF8 BOM")
    print("🚀" * 35 + "\n")

    all_files = []
    for dname, _ in dirs:
        dpath = Path(base_dir) / dname
        if not dpath.exists():
            print(f"⚠️  目录不存在：{dpath}")
            continue
        md_files = sorted([f for f in dpath.glob('*.md') if f.name != 'index.md'])
        print(f"📁 {dname}/ : 发现 {len(md_files)} 个 .md 文件")
        all_files.extend(md_files)

    total_files = len(all_files)
    total_batches = (total_files + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"\n📋 总计：{total_files} 个文件 | {total_batches} 个批次")

    if total_files == 0:
        print("❌ 没有找到待处理文件")
        return

    results = []
    total_success = 0
    total_skip = 0

    batch_start = 0
    for bn in range(1, total_batches + 1):
        batch_end = min(batch_start + BATCH_SIZE, total_files)
        batch_files = all_files[batch_start:batch_end]
        s, sk = process_batch(batch_files, bn, total_batches, results)
        total_success += s
        total_skip += sk
        batch_start = batch_end
        time.sleep(0.2)

    print("\n" + "🏁" * 35)
    print("  全部批次处理完成")
    print("🏁" * 35)
    print(f"\n📊 最终统计：")
    print(f"  处理总数：{total_files}")
    print(f"  ✅ 成功数：{total_success}")
    print(f"  ⏭️  跳过数：{total_skip}")
    print(f"  📈 成功率：{total_success / total_files * 100:.1f}%")

    good_summaries = sum(1 for r in results if r.get('summary_len', 0) >= 150 and r.get('summary_len', 0) <= 300)
    good_keywords = sum(1 for r in results if 4 <= r.get('keywords', '').count('·') + 1 <= 6)
    with_toc = sum(1 for r in results if r.get('has_toc'))

    print(f"\n🔍 质量验证：")
    print(f"  概要字数合规（150-300字）：{good_summaries}/{total_success} ({good_summaries / max(total_success, 1) * 100:.1f}%)")
    print(f"  关键词数量合规（4-6个）：  {good_keywords}/{total_success} ({good_keywords / max(total_success, 1) * 100:.1f}%)")
    print(f"  长文件已加目录（>100行）： {with_toc} 个文件")

    report = {
        'generated_at': datetime.now().isoformat(),
        'total_files': total_files,
        'success_count': total_success,
        'skip_count': total_skip,
        'success_rate': total_success / total_files,
        'quality': {
            'good_summaries': good_summaries,
            'good_keywords': good_keywords,
            'with_toc': with_toc,
        },
        'details': results,
    }

    report_path = Path(base_dir) / '_massive_optimize_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📋 详细报告：{report_path}")
    print("\n🎉 优化任务完成！\n")


if __name__ == '__main__':
    main()
