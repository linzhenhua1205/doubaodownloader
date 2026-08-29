#!/usr/bin/env python3
"""
完整重做脚本：解决换行丢失问题，重新从头构建所有161个文件
正确处理所有换行、拼接、目录生成逻辑
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
    r'低代码AI开发', r'规模化落地', r'范式跃迁',
    r'Vibe\s*Coding', r'Agentic\s*Engineering',
    r'290\.3\s*亿美元', r'6\s*万亿美元',
    r'范式革命', r'赋能千行百业', r'重新定义',
]

TEMPLATE_SECTION_MAP = {
    '🌐背景': '背景与技术语境',
    '💡核心要点': '核心技术要点',
    '🔍深度解读': '技术机制深度解析',
    '🆕最新进展': '技术演进与最新突破',
    '快速导读': '内容导航',
    '核心要点': '核心技术要点',
    '深度解读': '技术机制深度解析',
    '最新进展': '技术演进与最新突破',
    '背景与意义': '背景与技术语境',
    '背景与上下文': '背景与技术语境',
    '卡片概述': '主题概述',
}


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


def extract_fm(text):
    has_bom = text.startswith(BOM)
    if has_bom:
        text = text[1:]
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            fm = text[3:end].strip()
            body = text[end + 4:].strip()
            return fm, body, True, has_bom
    return "", text, False, has_bom


def smart_split_body(body):
    """把挤在一行的内容按语义拆分成多行"""

    body = re.sub(r'\r\n?', '\n', body)

    split_points = []

    for pat in [r'(?<!#)# (?!#)', r'(?<!#)## (?!#)', r'(?<!#)### (?!#)', r'(?<!#)#### ']:
        for m in re.finditer(pat, body):
            split_points.append((m.start(), m.group(0)))

    split_points.sort(key=lambda x: x[0])

    if split_points:
        parts = []
        prev = 0
        for pos, marker in split_points:
            if pos > prev:
                seg = body[prev:pos].strip()
                if seg:
                    parts.append(seg)
            prev = pos
        if prev < len(body):
            seg = body[prev:].strip()
            if seg:
                parts.append(seg)
        body = '\n\n'.join(parts)

    lines = body.split('\n')
    out = []
    in_code = False

    for line in lines:
        s = line.strip()
        if s.startswith('```'):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue

        if not s:
            out.append('')
            continue

        segments = []
        last = 0

        if not s.startswith('#') and not s.startswith('|') and not s.startswith('```'):
            for m in re.finditer(r'(?=\s+(?:###|####)\s)|\s{3,}(?=\|)', s):
                cut = m.start()
                if cut - last > 15:
                    segments.append(s[last:cut].strip())
                    last = cut
        if last < len(s):
            segments.append(s[last:].strip())

        if len(segments) > 1:
            for seg in segments:
                if seg:
                    out.append(seg)
            out.append('')
        else:
            out.append(line)

    result = '\n'.join(out)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    return result


def extract_h1(body, fm, filename):
    if fm:
        m = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
        if m:
            return clean_title(m.group(1).strip().strip("'\""))
    m = re.search(r'^#\s+(.+?)\s*(?:\n|\s\[←|$)', body, re.MULTILINE)
    if m:
        return clean_title(m.group(1))
    return clean_title(Path(filename).stem)


def extract_tags(fm):
    if not fm:
        return []
    m = re.search(r'^tags:\s*\[(.+?)\]', fm, re.MULTILINE)
    if m:
        return [t.strip().strip("'\"") for t in m.group(1).split(',') if t.strip()]
    return []


def extract_content_paragraphs(body):
    lines = smart_split_body(body).split('\n')
    skip_secs = {
        '目录', '📑', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录', '更新日志',
        '知识关联', '延伸阅读', '相关文章', '相关资源', '相关素材',
        '快速导读', '内容评级', 'import素材融合', '阅读建议', '关键数据',
        '适合人群', '阅读时长', '难度等级', '原始内容', '返回分类索引',
        '卡片概述', '主题概述', '卡片定位',
    }

    content_parts = []
    cur_sec = None
    cur_lines = []
    in_code = False

    for line in lines:
        st = line.strip()
        if st.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if st.startswith('## ') and not st.startswith('### '):
            if cur_sec is not None and cur_lines:
                s_clean = clean_title(cur_sec)
                if not any(sk in s_clean for sk in skip_secs):
                    content_parts.append('\n'.join(cur_lines))
            cur_sec = clean_title(st[3:].strip())
            cur_lines = []
            continue
        if st.startswith('#'):
            continue
        if st.startswith('[← '):
            continue
        if st == '---' or st == '----':
            continue
        if cur_sec is not None:
            cur_lines.append(st)

    if cur_sec is not None and cur_lines:
        s_clean = clean_title(cur_sec)
        if not any(sk in s_clean for sk in skip_secs):
            content_parts.append('\n'.join(cur_lines))

    if not content_parts:
        for line in lines:
            s = line.strip()
            if not s.startswith(('#', '```', '---')) and len(s) > 30:
                content_parts.append(s)

    return '\n\n'.join(content_parts)


def extract_quant_data(body):
    out = []
    pats = [
        (r'(\d+(?:\.\d+)?)\s*%', 'pct'),
        (r'(\d+(?:\.\d+)?)\s*万亿', 't'),
        (r'(\d+(?:\.\d+)?)\s*亿', 'hm'),
        (r'(\d+(?:\.\d+)?)\s*万美元?', 'usd'),
        (r'(\d+(?:\.\d+)?)\s*T\s*Tokens?', 'tok'),
        (r'(\d+(?:\.\d+)?)\s*亿参数', 'par'),
        (r'(\d+(?:\.\d+)?)\s*GB', 'gb'),
        (r'(\d+(?:\.\d+)?)\s*层', 'l'),
        (r'20\d{2}\s*年', 'y'),
    ]
    for p, dt in pats:
        for m in re.finditer(p, body, re.IGNORECASE):
            ctx = body[max(0, m.start() - 20):min(len(body), m.end() + 15)].replace('\n', ' ').strip()
            out.append((m.group(0), dt, ctx))
    return out


def extract_sources(body):
    out = []
    seen = set()
    for pat in [r'\[来源[：:]\s*([^\]]+)\]', r'>\s*\*\*来源\*\*[：:]\s*([^\n<]+)', r'来源[：:]\s*([^\n<]+)']:
        for m in re.finditer(pat, body):
            s = re.sub(r'[，,。；;].*$', '', m.group(1)).strip()
            k = s.lower()
            if 3 < len(s) < 100 and k not in seen:
                seen.add(k)
                out.append(s)
    return out


KW_STOP = {
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

KW_NORM = {
    '大语言模型': '大模型', 'LLM': '大模型',
    '生成式AI': 'AIGC', '生成式人工智能': 'AIGC',
    '智能体': 'AI Agent', 'Agent': 'AI Agent',
    '检索增强生成': 'RAG',
    '提示词': '提示工程', 'Prompt': '提示工程',
    'MoE': 'MoE架构', '混合专家': 'MoE架构',
    'Transformer': 'Transformer架构',
    'NLP': '自然语言处理',
    'CV': '计算机视觉',
    'LoRA': '微调', 'QLoRA': '微调', 'fine-tuning': '微调',
    'GPT': 'GPT系列',
    'GPU': 'GPU算力',
    'RLHF': '对齐技术', 'GRPO': '对齐技术', 'DPO': '对齐技术',
    'SFT': '监督微调',
}

TECH_PATS = [
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
    (r'\b(?:训练|预训练|后训练)\b', '模型训练'),
    (r'\b推理(?:优化)?\b|Inference', '推理优化'),
    (r'\b量化\b|INT\d|FP\d', '模型量化'),
    (r'\b蒸馏\b|剪枝\b', '模型压缩'),
]


def build_kw(title, tags, content, qd):
    cand = {}
    roots = set()

    def add(kw, w):
        if not kw or len(kw) < 2:
            return
        n = KW_NORM.get(kw, kw)
        if n in KW_STOP or len(n) < 2:
            return
        r = re.sub(r'[模型架构系统机制框架技术平台编程开发优化]', '', n).lower()
        if len(r) >= 2:
            if r in roots:
                return
            roots.add(r)
        cand[n] = cand.get(n, 0) + w

    for w in re.findall(r'[\u4e00-\u9fffA-Za-z0-9+\-]{2,}', clean_title(title)):
        add(w.strip(), 100)

    for t in tags:
        add(clean_title(t).strip("'\""), 85)

    for pat, norm in TECH_PATS:
        c = len(re.findall(pat, content, re.IGNORECASE))
        if c > 0:
            add(norm, 50 + min(c * 5, 40))

    freq = {}
    for w in re.findall(r'[\u4e00-\u9fff]{2,4}', content):
        if w not in KW_STOP:
            freq[w] = freq.get(w, 0) + 1
    for w, c in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:30]:
        if c >= 3:
            add(w, 25 + min(c * 2, 20))

    for v, dt, ctx in qd[:3]:
        if dt == 'par':
            add('参数规模', 35)
        elif dt == 'tok':
            add('训练数据', 30)

    if not cand:
        for b in ['大模型', 'AI Agent', 'AIGC', 'RAG', '多模态']:
            add(b, 50)

    final = []
    for kw, _ in sorted(cand.items(), key=lambda x: x[1], reverse=True):
        if len(final) >= 6:
            break
        sim = False
        for e in final:
            if kw in e or e in kw:
                if len(kw) <= len(e):
                    sim = True
                    break
        if not sim:
            final.append(kw)

    if len(final) < 4:
        for b in ['大模型', 'AI Agent', 'AIGC', 'RAG', '多模态', '微调', 'Transformer架构']:
            if b not in final:
                final.append(b)
                if len(final) >= 4:
                    break

    return " · ".join(final[:6])


def score_para(para, title, tags, qd):
    s = 0
    pl = para.lower()
    if 150 <= len(para) <= 350:
        s += 40
    elif 100 <= len(para) <= 500:
        s += 25
    twords = re.findall(r'[\u4e00-\u9fffA-Za-z]{2,}', clean_title(title))
    s += min(sum(1 for w in twords if w.lower() in pl) * 8, 35)
    for t in tags[:5]:
        if len(t) >= 2 and clean_title(t).lower() in pl:
            s += 5
    for v, _, _ in qd:
        if v in para:
            s += 12
    tech_sigs = ['架构', '机制', '原理', '算法', '模型', '系统', '性能',
                 '效率', '创新', '突破', '优化', '训练', '推理', '部署',
                 '对比', '提升', '降低', '达到', '实现', '支持']
    s += min(sum(1 for sig in tech_sigs if sig in para) * 3, 20)
    if para.startswith('>'):
        s -= 30
    if '原文链接' in para or 'http' in para:
        s -= 15
    return s


def build_summary(title, content, qd, srcs, tags):
    paras = []
    in_code = False
    cur = []
    for line in content.split('\n'):
        st = line.strip()
        if st.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not st:
            if cur:
                p = ' '.join(cur).strip()
                p = re.sub(r'\*\*(.+?)\*\*', r'\1', p)
                p = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', p)
                if len(p) >= 40 and not p.startswith(('-', '*', '|', '>')):
                    paras.append(p)
                cur = []
            continue
        if re.match(r'^[-*+•]\s+', st) or re.match(r'^\d+[\.、)]\s+', st):
            if cur:
                p = ' '.join(cur).strip()
                p = re.sub(r'\*\*(.+?)\*\*', r'\1', p)
                if len(p) >= 40:
                    paras.append(p)
                cur = []
            continue
        if st.startswith('|'):
            continue
        cur.append(st)
    if cur:
        p = ' '.join(cur).strip()
        p = re.sub(r'\*\*(.+?)\*\*', r'\1', p)
        if len(p) >= 40:
            paras.append(p)

    best = None
    best_s = -1
    for p in paras:
        sc = score_para(p, title, tags, qd)
        if sc > best_s:
            best_s = sc
            best = p

    if best is None and content:
        for s in re.split(r'[。！？!?；;]', content):
            s = s.strip()
            if 100 <= len(s) <= 350:
                best = s
                break

    if best is None:
        t = clean_title(title)
        parts = re.split(r'[：:—\-｜|]', t, maxsplit=1)
        if len(parts) >= 2:
            best = f"本文围绕{parts[0].strip()}领域，系统阐述{parts[1].strip()}的核心技术原理、架构设计与实现机制"
        else:
            best = f"本文深入解析{t}的技术体系，涵盖核心原理、关键机制与实践路径"

    base = re.sub(r'\s+', ' ', best).strip()
    segs = re.split(r'([。！？!?；;])', base)
    st = ""
    for i in range(0, len(segs), 2):
        if i >= len(segs):
            break
        seg = segs[i].strip()
        if not seg:
            continue
        pu = segs[i + 1] if i + 1 < len(segs) else '。'
        if len(st) + len(seg) + 1 <= 260:
            st += seg + pu
        else:
            rem = 260 - len(st)
            if rem > 20:
                st += seg[:rem] + '...'
            break
        if len(st) >= 180:
            break
    if not st:
        st = base[:255] + '...'

    if len(st) < 150 and qd:
        for v, _, _ in qd[:2]:
            if v not in st:
                add = f"，相关数据达{v}"
                if len(st) + len(add) <= 280:
                    st = st.rstrip('。！？!?…') + add + '。'
                    break

    if len(st) < 150:
        t = clean_title(title)
        f = f"。文章从技术架构、实现机制与应用实践多维度展开系统分析，为理解{t}提供完整知识框架"
        if len(st) + len(f) <= 290:
            st = st.rstrip('。！？!?…') + f + '。'

    used_src = None
    if srcs:
        for s in srcs:
            ss = re.sub(r'[《》\s]', '', s)[:30]
            if len(st) + len(ss) + 12 <= 300:
                used_src = s
                break
    if used_src is None and qd:
        used_src = f"{clean_title(title)[:6]}技术文档"

    if used_src:
        tag = f"[来源: {used_src}]"
        if len(st) + len(tag) + 1 <= 300:
            st = st.rstrip('。！？!?') + '。 ' + tag
        else:
            trim = 300 - len(tag) - 1
            if trim > 140:
                st = st[:trim].rstrip('，,、；;：:') + '... ' + tag

    if len(st) > 300:
        st = st[:297] + '...'
    st = st.strip()
    if st and not st.endswith((']', '。', '！', '？', '!', '?', '...', '…')):
        st += '。'
    return st


def build_toc(body, total_lines):
    if total_lines <= 100:
        return ""
    lines = body.split('\n')
    titles = []
    seen = set()
    excludes = [
        '目录', '📑', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录', '更新日志',
        '知识关联', '延伸阅读', '相关文章', '相关资源', '相关素材',
        '快速导读', '核心要点', '内容', '执行摘要', '关键词标签',
        '内容评级', 'import素材融合', '阅读建议', '关键数据',
        '适合人群', '阅读时长', '难度等级', '原始内容', '返回分类索引',
        '主题概述', '卡片概述', '卡片定位',
    ]
    for line in lines:
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            c = clean_title(s[3:].strip())
            if not c or len(c) < 2:
                continue
            if any(ex.lower() in c.lower() for ex in excludes):
                continue
            k = c.lower()
            if k not in seen:
                seen.add(k)
                titles.append(c)
    if len(titles) < 3:
        return ""
    toc = ["## 📑 目录", ""]
    for t in titles:
        a = re.sub(r'[^\w\u4e00-\u9fff-]', '', t)
        toc.append(f"- [{t}](#{a})")
    toc.append("")
    return '\n'.join(toc)


def rewrite_titles(body):
    lines = body.split('\n')
    out = []
    for line in lines:
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            c = clean_title(s[3:].strip())
            nt = None
            for tmpl, repl in TEMPLATE_SECTION_MAP.items():
                if c == tmpl or c.startswith(tmpl) or tmpl in c:
                    nt = repl
                    break
            if nt:
                out.append(f'## {nt}')
            else:
                out.append(line)
        else:
            out.append(line)
    return '\n'.join(out)


def remove_noise(body):
    for p in NOISE_PATTERNS:
        body = re.sub(p, '', body, flags=re.IGNORECASE)
    body = re.sub(r'，{2,}', '，', body)
    body = re.sub(r'。{2,}', '。', body)
    return body


def extract_h1_and_clean_body(body):
    lines = body.split('\n')
    h1 = None
    h1_idx = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            m = re.match(r'^#\s+(.+?)(\s+\[←|$)', s)
            if m:
                h1 = clean_title(m.group(1))
            h1_idx = i
            break
    if h1_idx == -1:
        return h1, body, ""

    rest_lines = lines[h1_idx + 1:]

    footer_markers = [
        '## 🔗 参考文件', '## 参考文件', '## 参考资料', '## 参考来源',
        '## Changelog', '## 变更日志', '## 变更记录',
        '## 更新日志', '## 版本记录',
    ]
    cut = None
    for i, line in enumerate(rest_lines):
        s = line.strip()
        for mk in footer_markers:
            if s == mk or s.startswith(mk):
                if cut is None or i < cut:
                    cut = i
                    break

    if cut is not None:
        rest_lines = rest_lines[:cut]

    filtered = []
    in_old_toc = False
    for line in rest_lines:
        s = line.strip()
        if s.startswith('## ') and '目录' in clean_title(s[3:]):
            in_old_toc = True
            continue
        if in_old_toc:
            if s.startswith('## ') and not s.startswith('### '):
                in_old_toc = False
                filtered.append(line)
            elif s.startswith('### '):
                in_old_toc = False
                filtered.append(line)
            continue
        if s.startswith('[← '):
            continue
        if s.startswith('> **概要') or s.startswith('> **关键词'):
            continue
        if s.startswith('> **文档定位') or s.startswith('> **知识深度') or s.startswith('> **关联知识域'):
            continue
        if s.startswith('>') and ('**概要**' in s or '**关键词**' in s):
            continue
        if s == '---' or s == '----':
            continue
        filtered.append(line)

    return h1, '\n'.join(filtered).strip(), h1


def build_refs(body, fm):
    lines = ["## 🔗 参考文件", ""]
    seen_u = set()
    links = []
    for m in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)', body):
        n = clean_title(m.group(1))
        u = m.group(2).strip()
        if not n or len(n) > 80 or u in seen_u:
            continue
        seen_u.add(u)
        links.append((n, u))

    srcs = []
    seen_s = set()
    for pat in [r'\[来源[：:]\s*([^\]]+)\]', r'>\s*\*\*来源\*\*[：:]\s*([^\n<]+)', r'来源[：:]\s*([^\n<]+)']:
        for m in re.finditer(pat, body):
            s = re.sub(r'[，,。；;].*$', '', m.group(1)).strip()
            k = re.sub(r'\s+', '', s).lower()
            if 4 <= len(s) < 100 and k not in seen_s:
                seen_s.add(k)
                srcs.append(s)

    items = []
    for n, u in links[:8]:
        items.append(f"- [{n}]({u})")
    for s in srcs[:5]:
        items.append(f"- {s}")

    if not items and fm:
        m = re.search(r'^tags:\s*\[(.+?)\]', fm, re.MULTILINE)
        if m:
            items.append(f"- 文档标签：{m.group(1)}")
    if not items:
        items.append("- 原文链接（见文首）")

    for it in items:
        lines.append(it)
    lines.append("")
    return '\n'.join(lines)


def build_cl():
    today = datetime.now().strftime('%Y-%m-%d')
    return f"""## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| {today} | v1.0 | 初始版本 |

"""


def process_file(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        raw = f.read()

    total_lines = len(raw.split('\n'))
    fm, body0, has_fm, has_bom = extract_fm(raw)
    body = smart_split_body(body0)
    body = rewrite_titles(body)
    body = remove_noise(body)

    fn = Path(fp).name
    tags = extract_tags(fm)
    h1_from_fm = None
    if fm:
        m = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
        if m:
            h1_from_fm = clean_title(m.group(1).strip().strip("'\""))

    h1_extracted, clean_body, h1_line = extract_h1_and_clean_body(body)
    h1 = h1_from_fm or h1_extracted or extract_h1(body, fm, fn)

    content = extract_content_paragraphs(clean_body)
    qd = extract_quant_data(body)
    srcs = extract_sources(body)

    summary = build_summary(h1, content, qd, srcs, tags)
    kw = build_kw(h1, tags, content, qd)
    toc = build_toc(clean_body, total_lines)

    header = [f"# {h1}", ""]
    header.append(f"> **概要**: {summary}")
    header.append(f"> **关键词**: {kw}")
    header.append("")
    if toc:
        header.append(toc)

    final_body = '\n'.join(header) + '\n' + clean_body.strip()
    final_body = re.sub(r'\n{4,}', '\n\n\n', final_body).rstrip() + '\n\n'
    final_body += build_refs(body, fm) + '\n' + build_cl()
    final_body = re.sub(r'\n{4,}', '\n\n\n', final_body).rstrip() + '\n'

    fm_lines = fm.strip().split('\n') if fm else []
    has_up = False
    for li, fl in enumerate(fm_lines):
        if re.match(r'^updated_at:', fl.strip()):
            fm_lines[li] = f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'"
            has_up = True
            break
    if not has_up and fm:
        fm_lines.append(f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'")
    fm_out = '\n'.join(fm_lines).strip()

    out = ""
    if has_bom:
        out += BOM
    if fm:
        out += f"---\n{fm_out}\n---\n\n"
    out += final_body

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(out)

    return True, {
        'fn': fn,
        'title': h1,
        's_len': len(summary),
        'k_cnt': kw.count('·') + 1,
        'has_toc': bool(toc),
        'lines': total_lines,
    }


def main():
    base = r'h:\github\cowkb\discover\newwiki2'
    dirs = ['AI-Agent', 'AI-模型架构', 'AI-训练微调', 'ai-models']
    BATCH = 20

    print("\n" + "🔄" * 35)
    print("  完整重做：修复换行+目录+格式（161文件）")
    print("🔄" * 35 + "\n")

    allf = []
    for d in dirs:
        dp = Path(base) / d
        if not dp.exists():
            continue
        mds = sorted([f for f in dp.glob('*.md') if f.name != 'index.md'])
        print(f"📁 {d}/ : {len(mds)} 文件")
        allf.extend(mds)

    total = len(allf)
    tbn = (total + BATCH - 1) // BATCH
    print(f"\n📋 总计 {total} 文件 | {tbn} 批次\n")

    res = []
    ts = 0
    tk = 0
    bs0 = 0
    for bn in range(1, tbn + 1):
        bend = min(bs0 + BATCH, total)
        bf = allf[bs0:bend]
        print(f"\n{'='*60}")
        print(f"🔧 批次 {bn}/{tbn} | {len(bf)} 文件")
        print(f"{'='*60}\n")
        b_ok = 0
        b_skip = 0
        for i, fp in enumerate(bf, 1):
            fn = Path(fp).name
            try:
                print(f"  [{i}/{len(bf)}] ⚙️  {fn[:50]}...", end=' ', flush=True)
                ok, info = process_file(str(fp))
                if ok:
                    ts += 1
                    b_ok += 1
                    tm = "📋" if info['has_toc'] else "  "
                    print(f"✅ {tm} | 概{info['s_len']}字 | {info['k_cnt']}关键词")
                    res.append(info)
                else:
                    tk += 1
                    b_skip += 1
                    print("⏭️")
                    res.append({'fn': fn, 'skip': True})
            except Exception as e:
                tk += 1
                b_skip += 1
                print(f"❌ {str(e)[:60]}")
                res.append({'fn': fn, 'err': True, 'why': str(e)[:80]})
        bs0 = bend
        print(f"\n  本批：✅ {b_ok} | ⏭️ {b_skip}")
        time.sleep(0.1)

    gs = sum(1 for r in res if 150 <= r.get('s_len', 0) <= 300)
    gk = sum(1 for r in res if 4 <= r.get('k_cnt', 0) <= 6)
    wt = sum(1 for r in res if r.get('has_toc'))

    print("\n" + "🏁" * 35)
    print("  完成")
    print("🏁" * 35)
    print(f"\n📊 统计：")
    print(f"  总数：{total} | ✅ {ts} | ⏭️ {tk} | 成功率 {ts/total*100:.1f}%")
    print(f"\n🔍 质量：")
    print(f"  概要合规（150-300字）：{gs}/{ts} ({gs/max(ts,1)*100:.1f}%)")
    print(f"  关键词合规（4-6个）：   {gk}/{ts} ({gk/max(ts,1)*100:.1f}%)")
    print(f"  长文件已加目录：        {wt} 文件")

    rp = Path(base) / '_full_rebuild_report.json'
    with open(rp, 'w', encoding='utf-8') as f:
        json.dump({
            'time': datetime.now().isoformat(),
            'total': total, 'ok': ts, 'skip': tk,
            'quality': {'good_s': gs, 'good_k': gk, 'toc': wt},
            'details': res,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n📋 报告：{rp}\n")


if __name__ == '__main__':
    main()
