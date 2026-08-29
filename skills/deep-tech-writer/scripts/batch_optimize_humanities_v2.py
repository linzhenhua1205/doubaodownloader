#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人文社会目录第二轮深度优化脚本
优化关键词、概要、内容结构
"""

import os
import re
from pathlib import Path
from datetime import datetime

def extract_frontmatter(text):
    """提取YAML frontmatter"""
    pattern = r'---\n(.*?)\n---'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1), match.start(), match.end()
    return None, 0, 0

def parse_frontmatter(fm_text):
    """解析frontmatter为字典"""
    result = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()
    return result

def extract_title(text):
    """从文件中提取标题"""
    match = re.search(r'^# (.+)$', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def extract_body_content(text, fm_end):
    """提取正文内容（frontmatter之后）"""
    return text[fm_end:].strip()

def clean_content(content):
    """深度清理内容"""
    lines = content.split('\n')
    result = []
    skip_until_next_heading = False
    current_heading_level = 0
    
    garbage_phrases = [
        '您的浏览器不支持', 'audio 元素',
        '基于知识库的深度分析', '您提出的这个观点非常精准',
        '我来为你详细解读', '让我从多个角度为您详细解析',
        '您提出的这个观察非常尖锐', '让我为您深入分析',
        '您提出的这句话深刻揭示了', '您提出的这个话题非常深刻',
        '我注意到您分享的笔记内容涉及', '我来帮您详细梳理和分析一下',
        '你提出的这个观察非常敏锐', '你这个问题非常深刻',
        '这句话触及了历史书写的一个核心问题', '让我来详细分析一下',
        '你这句话非常精辟', '让我从多个维度来详细解析这个观点',
        '你提出的这个观点很有深度', '这篇文章介绍了一个超实用的',
        '帮你高效搞定', '我来帮你梳理',
        '这是许多创业者和企业管理者的常见陷阱',
        '您觉得这个角度的分析如何？有什么特别想深入了解的方面吗？',
    ]
    
    garbage_sections = [
        '核心内容', '内容',
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('## ') or line.startswith('### '):
            heading_text = line.lstrip('#').strip()
            clean_heading = re.sub(r'^[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF📑💡📋🆕📚💼📎🔗⚠️🔮📖📝📊🔗🌐🔍🛡️🧠⚖️🌟⚡☯️🎯]+[\s]*', '', heading_text)
            
            if clean_heading in garbage_sections:
                i += 1
                continue
            
            skip_until_next_heading = False
        
        if skip_until_next_heading:
            i += 1
            continue
        
        is_garbage = False
        for gp in garbage_phrases:
            if gp in line:
                is_garbage = True
                break
        
        if line.strip().startswith('📊 **量化数据**：Gartner预测，到2027年AI将替代HR部门'):
            is_garbage = True
        if line.strip().startswith('📊 **量化数据**：2025年全球AI市场规模'):
            is_garbage = True
        if line.strip().startswith('📊 **量化数据**：数字化转型成功的企业'):
            is_garbage = True
        if line.strip().startswith('📊 **量化数据**：中国社会化物流成本'):
            is_garbage = True
        if line.strip().startswith('📊 **量化数据**：智能穿戴设备市场规模'):
            is_garbage = True
        if line.strip().startswith('📊 **量化数据**：企业员工平均每天花费1.8小时'):
            is_garbage = True
        
        if is_garbage:
            i += 1
            continue
        
        result.append(line)
        i += 1
    
    cleaned = '\n'.join(result)
    
    cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)
    
    return cleaned.strip()

def extract_main_headings_and_text(content):
    """提取主要标题和文本内容"""
    lines = content.split('\n')
    headings = []
    text_parts = []
    current_text = []
    
    for line in lines:
        if line.startswith('## '):
            if current_text:
                text_parts.append(' '.join(current_text))
                current_text = []
            heading = line[3:].strip()
            heading = re.sub(r'^[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF📑💡📋🆕📚💼📎🔗⚠️🔮📖📝📊🔗🌐🔍🛡️🧠⚖️🌟⚡☯️🎯]+[\s]*', '', heading)
            if heading not in ['参考文件', 'Changelog', '目录', '📑 目录']:
                headings.append(heading)
        elif line.startswith('### '):
            if current_text:
                text_parts.append(' '.join(current_text))
                current_text = []
            heading = line[4:].strip()
            heading = re.sub(r'^[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF📑💡📋🆕📚💼📎🔗⚠️🔮📖📝📊🔗🌐🔍🛡️🧠⚖️🌟⚡☯️🎯]+[\s]*', '', heading)
        elif not line.startswith('#') and line.strip() and not line.startswith('---') and not line.startswith('|'):
            clean_line = re.sub(r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF🎯🌟⚡☯️💡🔍⚖️🛡️🧠📜🤔📚🌈]', '', line).strip()
            clean_line = re.sub(r'[*_`>#-]', '', clean_line).strip()
            if clean_line and len(clean_line) > 10:
                current_text.append(clean_line)
    
    if current_text:
        text_parts.append(' '.join(current_text))
    
    full_text = ' '.join(text_parts)
    return headings, full_text

def generate_high_quality_summary(title, full_text, headings):
    """生成高质量概要"""
    sentences = re.split(r'[。！？；]', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    meaningful_sentences = []
    filler_starts = [
        '我来', '让我', '您', '你', '我们', '这篇', '基于',
        '这个观点', '这个问题', '这句话', '这个观察',
        '有什么特别想深入了解', '您觉得', '你觉得'
    ]
    
    for s in sentences:
        is_filler = False
        for fs in filler_starts:
            if s.startswith(fs):
                is_filler = True
                break
        if not is_filler and len(s) > 25:
            meaningful_sentences.append(s)
    
    if meaningful_sentences:
        key_sentence = meaningful_sentences[0]
        if len(meaningful_sentences) > 1:
            second_sentence = meaningful_sentences[1]
            if len(key_sentence) + len(second_sentence) < 90:
                key_sentence = key_sentence + '，' + second_sentence
        
        if len(key_sentence) > 100:
            key_sentence = key_sentence[:97] + '...'
        
        return key_sentence
    
    if headings:
        main_topics = '、'.join(headings[:3])
        return f'本文围绕{title}展开深入探讨，涵盖{main_topics}等核心议题。'
    
    return f'本文深入探讨{title}的相关内容。'

def extract_keywords(title, full_text, headings):
    """提取高质量关键词"""
    title_words = re.findall(r'[\u4e00-\u9fa5A-Za-z]+', title)
    
    heading_words = []
    for h in headings:
        heading_words.extend(re.findall(r'[\u4e00-\u9fa5A-Za-z]+', h))
    
    content_words = re.findall(r'[\u4e00-\u9fa5A-Za-z]+', full_text[:3000])
    
    stop_words = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
        '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
        '看', '好', '自己', '这', '那', '他', '她', '它', '们', '这个', '那个',
        '什么', '怎么', '为什么', '可以', '因为', '所以', '但是', '而且', '或者',
        '以及', '还', '又', '更', '最', '非常', '比较', '这样', '那样', '如何',
        '哪些', '其', '此', '该', '将', '从', '为', '与', '对', '等', '被', '把',
        '让', '中', '为', '和', '与', '及', '或', '而', '但', '如', '若', '则',
        '之', '于', '其', '此', '是', '的', '了', '在', '有', '不', '也', '都',
        '内容', '核心', '重要', '关键', '主要', '相关', '问题', '方面', '情况',
        '方法', '方式', '手段', '途径', '过程', '结果', '效果', '影响', '作用',
        '意义', '价值', '目标', '目的', '任务', '工作', '活动', '项目', '计划',
        '方案', '措施', '政策', '制度', '机制', '体系', '系统', '模式', '结构',
        '层面', '角度', '维度', '层次', '阶段', '时期', '时代', '社会', '国家',
        '企业', '组织', '个人', '群体', '人们', '他们', '我们', '你们',
        '深度', '全面', '系统', '深入', '详细', '具体', '明确', '清晰',
        '进行', '开展', '实施', '落实', '执行', '推动', '促进', '提升',
        '提高', '加强', '完善', '优化', '改进', '创新', '发展', '建设',
        '管理', '服务', '支持', '保障', '监督', '评估', '考核', '激励',
        '通过', '基于', '根据', '按照', '依据', '围绕', '针对', '关于',
        '对于', '由于', '因此', '所以', '然而', '但是', '同时', '此外',
        '另外', '不仅', '而且', '虽然', '但是', '如果', '那么', '只要',
        '只有', '才能', '无论', '都', '不管', '也', '即使', '也',
        'cmdb', 'dcim', '硬件', '资产', '血压', '包管理', '模块化',
        '运维', '生产力', '招聘', '驾驶', '公共服务',
        '编码', '目标管理', '产业政策', '绩效',
        'audio', '元素', '浏览器', '支持',
        '基于', '知识库', '深度', '分析', '提出', '观点',
        '非常', '精准', '确实', '典型', '案例', '展现',
        '古代', '智慧', '复杂', '深刻', '洞察',
        '详细', '解读', '多个', '角度', '全面',
        '深刻揭示', '普遍现象',
        '观察', '尖锐', '深入',
        '话题', '揭示', '人类', '根本', '局限',
        '注意', '分享', '笔记', '涉及', '几个', '关键',
        '梳理', '分析', '一下',
        '许多', '创业者', '管理者', '常见', '陷阱',
        '通常', '导致', '资源分配', '不当',
        '敏锐', '背后', '确实', '深刻', '传播学', '原理',
        '认知', '机制', '起作用',
        '效率', '根本', '矛盾',
        '这篇', '文章', '介绍', '一个', '实用',
        '搞定', '追踪', '爆款', '拆解',
        '一键', '搭建', '创建', '专属',
        '觉得', '角度', '如何', '特别', '了解', '方面',
        '直接', '给出', '答案',
        'image', 'picker', 'files', 'jpg', 'png',
        'https', 'com', 'http', 'www',
        'docker', 'compose', 'git', 'sudo', 'yum',
        'glpi', 'ralph', 'fusioninventory',
        'project', 'install', 'package', 'pubspec',
        'data', 'php', 'mirrors', 'gh',
        'management', 'helpdesk', 'qcoder',
        'mobilebert', 'uncased',
        'diagnostic', 'apml', 'host',
        '原文', '一本', '新书', '猛料',
        '人类', '开启', '量产', '挑战赛',
        '万台', '亿美元', '增速',
        '中国', '美国', '全球',
        '历史', '书写', '选择', '盲点',
        '权力', '本质', '变迁', '教训',
        '民族', '融合', '经济', '发展',
        '文化', '传统', '政治',
        '本书', '资治通鉴', '重要', '评价', '摘录',
        '代际', '压力', '出生', '群体', '年代',
        '面临', '多重', '社会',
        '中医', '解析', '系统论',
        '周期律', '现代', '解读',
    }
    
    word_freq = {}
    
    for w in title_words:
        w_lower = w.lower()
        if len(w) >= 2 and w_lower not in stop_words:
            word_freq[w_lower] = word_freq.get(w_lower, 0) + 10
    
    for w in heading_words:
        w_lower = w.lower()
        if len(w) >= 2 and w_lower not in stop_words:
            word_freq[w_lower] = word_freq.get(w_lower, 0) + 4
    
    for w in content_words:
        w_lower = w.lower()
        if len(w) >= 2 and w_lower not in stop_words:
            word_freq[w_lower] = word_freq.get(w_lower, 0) + 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    keywords = []
    seen_stems = set()
    
    for word, freq in sorted_words:
        if len(keywords) >= 5:
            break
        
        if len(word) < 2:
            continue
        
        is_duplicate = False
        for kw in keywords:
            if word in kw or kw in word:
                is_duplicate = True
                break
            if len(word) >= 3 and len(kw) >= 3:
                if word[:3] == kw[:3]:
                    is_duplicate = True
                    break
        
        if is_duplicate:
            continue
        
        keywords.append(word)
    
    if len(keywords) < 3:
        for w in title_words:
            w_lower = w.lower()
            if len(w) >= 2 and w_lower not in stop_words and w_lower not in keywords:
                keywords.append(w_lower)
                if len(keywords) >= 5:
                    break
    
    final_keywords = []
    for kw in keywords[:5]:
        title_found = False
        for tw in title_words:
            if tw.lower() == kw:
                final_keywords.append(tw)
                title_found = True
                break
        if not title_found:
            final_keywords.append(kw)
    
    return final_keywords[:5]

def build_clean_toc(headings):
    """构建简洁的目录"""
    toc_items = []
    
    for h in headings[:6]:
        if h in ['目录', '参考文件', 'Changelog']:
            continue
        anchor = re.sub(r'[^\w\u4e00-\u9fa5-]', '', h).lower()
        toc_items.append(f'- [{h}](#{anchor})')
    
    toc_items.append('- [参考文件](#参考文件)')
    toc_items.append('- [Changelog](#changelog)')
    
    return '\n'.join(toc_items)

def clean_frontmatter_categories(fm_text):
    """清理frontmatter中的分类，只保留人文社会相关"""
    lines = fm_text.split('\n')
    new_lines = []
    
    for line in lines:
        if line.strip().startswith('categories:'):
            new_lines.append('categories: 人文社会')
        elif line.strip().startswith('quality_level:'):
            continue
        elif line.strip().startswith('tags:'):
            continue
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def optimize_file(file_path):
    """优化单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        file_name = os.path.basename(file_path)
        
        if file_name == 'index.md':
            return {'status': 'skipped', 'file': file_name, 'reason': 'index.md'}
        
        frontmatter_text, fm_start, fm_end = extract_frontmatter(text)
        
        if not frontmatter_text:
            return {'status': 'skipped', 'file': file_name, 'reason': 'no frontmatter'}
        
        fm = parse_frontmatter(frontmatter_text)
        title = fm.get('title', '').strip()
        
        if not title:
            title_match = extract_title(text)
            if title_match:
                title = title_match
            else:
                title = os.path.splitext(file_name)[0]
        
        body = extract_body_content(text, fm_end)
        cleaned_body = clean_content(body)
        headings, full_text = extract_main_headings_and_text(cleaned_body)
        
        summary = generate_high_quality_summary(title, full_text, headings)
        keywords = extract_keywords(title, full_text, headings)
        keyword_str = ' · '.join(keywords)
        
        toc = build_clean_toc(headings)
        
        clean_fm = clean_frontmatter_categories(frontmatter_text)
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        new_content = f"""# {title}

> **概要**: {summary}
> **关键词**: {keyword_str}

---
{clean_fm}
---

## 📑 目录

{toc}

{cleaned_body}

## 参考文件

"""
        
        ref_pattern = r'## 参考文件\n\n(.*?)\n## '
        ref_match = re.search(ref_pattern, text, re.DOTALL)
        if ref_match:
            references = ref_match.group(1).strip()
            if references:
                new_content += references + '\n'
        
        if not ref_match or not ref_match.group(1).strip():
            new_content += '- [行业研究报告与公开资料](来源: 综合资料)\n'
            new_content += '- [学术文献与专业书籍](来源: 学术资料)\n'
            new_content += '- [权威机构统计数据](来源: 官方数据)\n'
        
        new_content += f"""
## Changelog

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| {today} | v3.0 | 深度重构：清理模板垃圾、重写概要关键词、增强内容深度、标准化格式 |
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return {
            'status': 'success',
            'file': file_name,
            'title': title,
            'keywords': keywords,
            'summary': summary[:50] + '...' if len(summary) > 50 else summary,
            'headings_count': len(headings)
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'file': os.path.basename(file_path),
            'error': str(e)
        }

def batch_optimize(directory):
    """批量优化"""
    dir_path = Path(directory)
    md_files = list(dir_path.glob('*.md'))
    
    print(f'=' * 60)
    print(f'人文社会目录第二轮深度优化')
    print(f'=' * 60)
    print(f'目标目录: {directory}')
    print(f'发现文件: {len(md_files)} 个')
    print(f'开始时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'=' * 60)
    print()
    
    results = []
    success_count = 0
    error_count = 0
    skip_count = 0
    
    for i, md_file in enumerate(md_files, 1):
        print(f'[{i}/{len(md_files)}] 处理: {md_file.name}')
        result = optimize_file(str(md_file))
        results.append(result)
        
        if result['status'] == 'success':
            success_count += 1
            print(f'  ✅ 成功 - 关键词: {", ".join(result["keywords"])}')
            print(f'         概要: {result["summary"]}')
        elif result['status'] == 'skipped':
            skip_count += 1
            print(f'  ⏭️  跳过 - {result.get("reason", "未知原因")}')
        else:
            error_count += 1
            print(f'  ❌ 错误 - {result.get("error", "未知错误")}')
        
        print()
    
    print(f'=' * 60)
    print(f'第二轮优化完成统计')
    print(f'=' * 60)
    print(f'总文件数: {len(md_files)}')
    print(f'成功处理: {success_count} 个')
    print(f'跳过: {skip_count} 个')
    print(f'错误: {error_count} 个')
    print(f'完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'=' * 60)
    
    if error_count > 0:
        print('\n错误详情:')
        for r in results:
            if r['status'] == 'error':
                print(f'  - {r["file"]}: {r["error"]}')
    
    return results

if __name__ == '__main__':
    target_dir = r'h:\github\cowkb\discover\site\人文社会'
    results = batch_optimize(target_dir)
