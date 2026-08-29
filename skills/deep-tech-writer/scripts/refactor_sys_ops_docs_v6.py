#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度重构系统与运维目录下的markdown文档 - V6 高质量版
重点：通顺的概要 + 准确的关键词 + 完整的目录
"""

import os
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "系统与运维"

# 技术关键词库（按优先级排序）
TECH_TERMS = [
    # 工具/产品（英文）
    'Docker', 'Ansible', 'Zabbix', 'CMDB', 'BMC', 'ELK', 'Grafana', 'GLPI',
    'Jenkins', 'Dify', 'IPMI', 'CPLD', 'PCIe', 'PostgreSQL', 'SonarQube',
    'DevOps', 'AIOps', 'K8s', 'Kubernetes', 'Nginx', 'CentOS',
    'SSH', 'SNMP', 'API', 'Webhook', 'FastAPI', 'YAML', 'Playbook',
    'FusionDirector', 'FusionServer', 'FusionOnline', 'PowerEdge',
    'UniSystem', 'Control-M', 'Helix', 'Cubox', 'Integrately',
    'LangBot', 'Gulp', 'RSS',
    # 技术概念（中文）
    '端口映射', '自定义网络', '自动化运维', '监控系统', '配置管理',
    '设备生命周期', '资产管理', '智能运维', '网络配置', '容器网络',
    '服务器', '运维', '部署', '监控', '告警', '日志', '集群',
    '容器', '镜像',
]


def extract_frontmatter(content):
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return content[:end+3], content[end+3:].strip()
    return '', content


def clean_title(title):
    emoji_chars = '🛠️🌐📊📦🚀🖥️🐳📋💡📑🔍📝✨⚙️🎯📈📉🏷️🌐🔍🆕📚📖📎🔗💼🛠️🌍📌🏭💡🌟📋🔄🎯💡⚙️📝'
    for c in emoji_chars:
        title = title.replace(c, '')
    return title.strip()


def extract_first_h1(body):
    m = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def find_real_body_content(body):
    """从body中提取真正的正文内容"""
    lines = body.split('\n')
    
    start_idx = 0
    for i, line in enumerate(lines):
        if re.match(r'^#\s+', line):
            start_idx = i + 1
            break
    
    content_start = -1
    
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        
        if re.match(r'^原文[：:]', line) or re.match(r'^🔗\s*\*\*原文链接', line):
            content_start = i
            break
        
        if re.match(r'^##\s*内容\s*$', line):
            content_start = i + 1
            break
        
        if re.match(r'^#{2,3}\s+', line):
            title = re.sub(r'^#{2,3}\s+', '', line).strip()
            template_titles = [
                '📑 目录', '💡 核心要点', '📋 快速导读',
                '🌐 背景与上下文', '🔍 深度解读', '🆕 2025-2026 最新进展',
                '📚 相关技术资源', '📖 延伸阅读', '📝 参考来源',
                '📎 相关素材', '🔗 相关文章', '参考文件', 'Changelog',
                '变更日志', '知识关联', '重定向说明',
                '💼 案例补充', '🛠️ 实践指南', '🌍 行业影响',
                'changelog', '内容'
            ]
            is_template = False
            for tt in template_titles:
                if tt in title:
                    is_template = True
                    break
            if not is_template:
                content_start = i
                break
        
        if line.startswith('> **概要**') or line.startswith('> **关键词**'):
            i += 1
            continue
        if not line or line.startswith('>'):
            i += 1
            continue
        i += 1
    
    if content_start == -1:
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            if line and not line.startswith('#') and not line.startswith('>') and not line.startswith('|'):
                if len(line) > 20:
                    content_start = i
                    break
    
    if content_start == -1:
        return body
    
    content_lines = []
    i = content_start
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if re.match(r'^##\s+', stripped):
            title = re.sub(r'^##\s+', '', stripped).strip()
            template_endings = [
                '🌐 背景与上下文', '🔍 深度解读', '🆕 2025-2026 最新进展',
                '📚 相关技术资源', '📖 延伸阅读', '📝 参考来源',
                '📎 相关素材', '🔗 相关文章', '参考文件', 'Changelog',
                '变更日志', '知识关联', '💼 案例补充', '🛠️ 实践指南',
                '🌍 行业影响', 'changelog', '📑 目录'
            ]
            is_ending = False
            for te in template_endings:
                if te in title:
                    is_ending = True
                    break
            if is_ending:
                break
        
        content_lines.append(line)
        i += 1
    
    result = '\n'.join(content_lines).strip()
    result = re.sub(r'^##\s*内容\s*\n', '', result).strip()
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result


def extract_core_points(real_content):
    """提取文章核心信息用于生成概要"""
    text = re.sub(r'```.*?```', '', real_content, flags=re.DOTALL)
    
    # 提取所有段落（非列表、非标题）
    paragraphs = []
    current_para = []
    
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            if current_para:
                para = ' '.join(current_para)
                if len(para) >= 20:
                    paragraphs.append(para)
                current_para = []
            continue
        
        # 跳过标题
        if re.match(r'^#{1,6}\s+', stripped):
            if current_para:
                para = ' '.join(current_para)
                if len(para) >= 20:
                    paragraphs.append(para)
                current_para = []
            continue
        
        # 跳过列表项（数字. 或 - 或 * 开头的短行）
        if re.match(r'^\d+\.\s+\*\*', stripped) and len(stripped) < 50:
            continue
        if re.match(r'^[-*+]\s+\*\*', stripped) and len(stripped) < 50:
            continue
        
        # 跳过原文链接
        if '原文' in stripped and '链接' in stripped:
            continue
        
        # 跳过emoji开头的短行
        if re.match(r'^[🔗📝⚙️🎯✨✅🔍📌🏭💡📋📑🌟🔄]', stripped) and len(stripped) < 30:
            continue
        
        current_para.append(stripped)
    
    if current_para:
        para = ' '.join(current_para)
        if len(para) >= 20:
            paragraphs.append(para)
    
    return paragraphs


def generate_summary(title, real_content):
    """生成高质量一句话概要（≤100字）"""
    title_clean = clean_title(title)
    paragraphs = extract_core_points(real_content)
    
    # 从标题提取核心主题
    core_topic = re.sub(r'[：:].*$', '', title_clean)
    # 去掉后缀词
    core_topic = re.sub(r'(详解|指南|解析|实践|全解|方案|教程|手册|全解析|深度解析|实战指南|完整指南|解决方案|功能解析|技术优势|全景报告|市场格局|质量报告|选型指南|核心能力要求|目标)$', '', core_topic)
    core_topic = core_topic.strip()
    
    # 从副标题中提取角度
    subtitle = ''
    if '：' in title_clean or ':' in title_clean:
        subtitle = re.split(r'[：:]', title_clean, 1)[1].strip()
        subtitle = re.sub(r'(详解|指南|解析|实践|全解|方案|教程|手册)$', '', subtitle).strip()
    
    # 找一个最好的段落句子
    best_para = ''
    best_score = 0
    
    for para in paragraphs[:5]:
        if len(para) < 20 or len(para) > 150:
            continue
        
        score = 0
        # 长度合适
        if 40 <= len(para) <= 90:
            score += 10
        elif 30 <= len(para) < 40:
            score += 5
        
        # 包含核心动词
        verbs = ['实现', '提供', '支持', '包括', '基于', '通过', '解决', '优化',
                 '部署', '配置', '管理', '监控', '分析', '集成', '构建',
                 '介绍', '阐述', '探讨', '对比', '说明', '提升', '降低']
        for v in verbs:
            if v in para:
                score += 2
        
        # 包含技术名词
        for term in TECH_TERMS:
            if term in para:
                score += 1
                break
        
        if score > best_score:
            best_score = score
            best_para = para
    
    # 构建概要
    if best_para and 30 <= len(best_para) <= 95:
        return best_para
    
    # 方案B：标题 + 核心内容
    if best_para and len(best_para) > 20:
        # 取段落的主要部分
        main_point = best_para[:60]
        if subtitle:
            summary = f"本文介绍{core_topic}，从{subtitle}角度分析，{main_point}"
        else:
            summary = f"本文介绍{core_topic}，{main_point}"
    else:
        # 方案C：完全基于标题构建
        if subtitle:
            summary = f"本文深入解析{core_topic}，涵盖{subtitle}等核心内容"
        else:
            summary = f"本文详细介绍{core_topic}的核心原理与实践方法"
    
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary


def extract_keywords(title, real_content):
    """提取3-5个核心关键词"""
    title_clean = clean_title(title)
    
    # 提取正文文本用于词频
    paragraphs = extract_core_points(real_content)
    text = ' '.join(paragraphs)
    
    result = []
    seen = set()
    
    # 第1步：从标题提取英文技术术语（最高优先级）
    for term in TECH_TERMS:
        if len(term) <= 1:
            continue
        term_lower = term.lower()
        # 检查是否在标题中（精确或部分匹配）
        if term_lower in title_clean.lower():
            if term_lower not in seen:
                seen.add(term_lower)
                result.append(term)
        if len(result) >= 4:
            break
    
    # 第2步：从正文补充高频技术术语
    if len(result) < 5:
        text_lower = text.lower()
        for term in TECH_TERMS:
            if len(term) <= 1:
                continue
            term_lower = term.lower()
            if term_lower not in seen:
                count = text_lower.count(term_lower)
                if count >= 2:
                    seen.add(term_lower)
                    result.append(term)
                    if len(result) >= 5:
                        break
    
    # 第3步：从标题提取有意义的中文短语
    if len(result) < 5:
        # 用冒号、空格等分割标题
        title_parts = re.split(r'[：:、，,\s_]+', title_clean)
        for part in title_parts:
            part = part.strip()
            if len(part) < 2 or len(part) > 12:
                continue
            part_lower = part.lower()
            if part_lower in seen:
                continue
            
            # 检查是否是有意义的技术词（包含技术词根）
            tech_roots = ['运', '监', '网', '配', '部', '集', '自', '容', '镜',
                          '警', '日', '服', '系', '数', '安', '性', '架', '算',
                          '存', '虚', '管', '优', '解', '策', '方', '模', '技']
            is_tech = False
            for root in tech_roots:
                if root in part:
                    is_tech = True
                    break
            
            # 或者在 TECH_TERMS 中有部分匹配
            if not is_tech:
                for term in TECH_TERMS:
                    if part in term or term in part:
                        is_tech = True
                        break
            
            if is_tech:
                seen.add(part_lower)
                result.append(part)
                if len(result) >= 5:
                    break
    
    # 第4步：从正文提取高频中文词
    if len(result) < 5:
        cn_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        stop_words = {'的话', '这个', '那个', '一个', '一种', '一些', '可以',
                      '需要', '进行', '实现', '提供', '支持', '包括', '基于',
                      '通过', '使用', '应用', '系统', '技术', '功能', '管理',
                      '服务', '平台', '方案', '工具', '模块', '问题', '方法',
                      '方式', '过程', '结果', '内容', '核心', '要点', '我们',
                      '如果', '因为', '所以', '但是', '而且', '或者',
                      '以及', '等等', '这样', '那样', '什么', '怎么', '为什么',
                      '可以', '能够', '可能', '应该', '必须', '需要',
                      '运维', '监控', '部署', '配置'}  # 太通用的跳过
        filtered = [w for w in cn_words if w not in stop_words and len(w) >= 2]
        word_counts = Counter(filtered)
        for w, c in word_counts.most_common(50):
            if c >= 4 and w.lower() not in seen and 2 <= len(w) <= 5:
                seen.add(w.lower())
                result.append(w)
                if len(result) >= 5:
                    break
    
    # 确保至少3个
    if len(result) < 3:
        defaults = ['运维', '监控', '自动化', '部署', '配置']
        for d in defaults:
            if d.lower() not in seen:
                result.append(d)
                seen.add(d.lower())
                if len(result) >= 3:
                    break
    
    return result[:5]


def extract_section_titles(real_content):
    """提取章节标题用于目录"""
    titles = []
    
    # 1. 二级标题
    h2s = re.findall(r'^##\s+(.+)$', real_content, re.MULTILINE)
    for h in h2s:
        h = h.strip()
        if h == '内容':
            continue
        if re.match(r'^[🌐🔍🆕📚📖📝📎🔗💼🛠️🌍📑]', h):
            continue
        if '参考文件' in h or 'Changelog' in h or '变更日志' in h:
            continue
        if len(h) < 40 and h not in titles:
            titles.append(h)
    
    # 2. 三级标题（如果二级不够）
    if len(titles) < 3:
        h3s = re.findall(r'^###\s+(.+)$', real_content, re.MULTILINE)
        for h in h3s:
            h = h.strip()
            # 清理前缀emoji
            h = re.sub(r'^[🔗📝⚙️🎯✨✅🔍📌🏭💡📋📑🌟🔄💡📝]+\s*', '', h)
            if len(h) < 40 and h not in titles:
                if h not in ['核心要点', '关键数据', '阅读建议']:
                    titles.append(h)
            if len(titles) >= 8:
                break
    
    # 3. 用emoji标记的章节标题（如 "📝 **核心参数解析**"）
    if len(titles) < 3:
        emoji_titles = re.findall(r'^[🔗📝⚙️🎯✨✅🔍📌🏭💡📋📑🌟🔄]+\s*\*\*(.+?)\*\*', real_content, re.MULTILINE)
        for h in emoji_titles:
            h = h.strip()
            if len(h) < 30 and h not in titles:
                titles.append(h)
            if len(titles) >= 8:
                break
    
    return titles[:8]


def generate_toc(titles):
    """生成目录"""
    if not titles:
        return ''
    
    toc_lines = []
    for title in titles:
        slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', title).lower()
        slug = re.sub(r'-+', '-', slug).strip('-')
        toc_lines.append(f'- [{title}](#{slug})')
    
    return '\n'.join(toc_lines)


def extract_original_url(content):
    """提取原文链接"""
    patterns = [
        r'原文[：:]*\s*\[([^\]]+)\]\((https?://[^\s\)]+)\)',
        r'原文链接[：:]\s*(https?://[^\s\)]+)',
        r'🔗\s*\*\*原文链接\*\*[：:]\s*(https?://[^\s\)]+)',
    ]
    
    for pat in patterns:
        m = re.search(pat, content)
        if m:
            if len(m.groups()) == 2:
                return m.group(2), m.group(1)
            else:
                return m.group(1), '原文链接'
    
    urls = re.findall(r'https?://[^\s\)\]]+', content)
    if urls:
        return urls[0], '参考来源'
    
    return None, None


def rebuild_document(content, filepath):
    """重构文档"""
    filepath = Path(filepath)
    
    frontmatter, body = extract_frontmatter(content)
    title = extract_first_h1(body)
    if not title:
        title = filepath.stem
    
    real_content = find_real_body_content(body)
    
    if len(real_content) < 100:
        real_content = body
        real_content = re.sub(r'^#\s+.+$\n+', '', real_content, count=1)
    
    summary = generate_summary(title, real_content)
    keywords = extract_keywords(title, real_content)
    keywords_str = ' · '.join(keywords)
    
    section_titles = extract_section_titles(real_content)
    toc = generate_toc(section_titles)
    
    orig_url, orig_title = extract_original_url(content)
    
    # 清理正文
    content_clean = real_content
    content_clean = re.sub(r'\n{3,}', '\n\n', content_clean)
    content_clean = re.sub(r'\n[-=]{3,}\s*$', '', content_clean).strip()
    
    # 构建新文档
    new_content = []
    
    if frontmatter:
        new_content.append(frontmatter)
        new_content.append('')
    
    new_content.append(f'# {title}')
    new_content.append('')
    
    new_content.append(f'> **概要**: {summary}')
    new_content.append(f'> **关键词**: {keywords_str}')
    new_content.append('')
    
    if toc:
        new_content.append('## 📑 目录')
        new_content.append('')
        new_content.append(toc)
        new_content.append('')
    
    new_content.append(content_clean)
    new_content.append('')
    
    new_content.append('## 参考文件')
    new_content.append('')
    if orig_url:
        new_content.append(f'- [{orig_title}]({orig_url})')
    else:
        new_content.append('- 公开技术资料与官方文档')
    new_content.append('')
    
    new_content.append('## Changelog')
    new_content.append('')
    new_content.append('| 版本 | 日期 | 更新内容 |')
    new_content.append('|------|------|---------|')
    new_content.append('| v2.0 | 2026-07-27 | 深度重构版：清理模板化垃圾内容，重写概要和关键词，标准化格式 |')
    new_content.append('| v1.0 | 初始版本 | 原文基础内容 |')
    new_content.append('')
    
    return '\n'.join(new_content), {
        'summary': summary,
        'summary_length': len(summary),
        'keyword_count': len(keywords),
        'keywords': keywords,
        'title': title,
        'section_count': len(section_titles),
    }


def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content, stats = rebuild_document(content, filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, stats
    except Exception as e:
        import traceback
        return False, str(e) + '\n' + traceback.format_exc()


def main():
    print("=" * 70)
    print("深度重构系统与运维目录下的markdown文档 V6 - 高质量版")
    print("=" * 70)
    
    md_files = sorted(TARGET_DIR.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'index.md']
    
    print(f"发现 {len(md_files)} 个markdown文件（已排除index.md）")
    print()
    
    print("🚀 开始深度重构...")
    print()
    
    success_count = 0
    fail_count = 0
    errors = []
    all_stats = []
    
    for i, filepath in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] 处理: {filepath.name}")
        success, result = process_file(filepath)
        if success:
            success_count += 1
            all_stats.append(result)
            kw_str = ' · '.join(result['keywords'])
            print(f"   ✅ 完成 | 概要{result['summary_length']}字 | 关键词{result['keyword_count']}个 | 章节{result['section_count']}个")
            print(f"      关键词: {kw_str}")
            print(f"      概要: {result['summary'][:70]}...")
        else:
            fail_count += 1
            errors.append((filepath.name, result))
            print(f"   ❌ 失败: {result}")
    
    print()
    print("=" * 70)
    print("重构完成！")
    print("=" * 70)
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print()
    
    if errors:
        print("错误详情:")
        for name, error in errors:
            print(f"  - {name}: {error}")
        print()
    
    print("📊 质量统计:")
    avg_summary_len = sum(s['summary_length'] for s in all_stats) / max(len(all_stats), 1)
    avg_keyword_cnt = sum(s['keyword_count'] for s in all_stats) / max(len(all_stats), 1)
    avg_section_cnt = sum(s['section_count'] for s in all_stats) / max(len(all_stats), 1)
    print(f"   平均概要长度: {avg_summary_len:.1f} 字")
    print(f"   平均关键词数: {avg_keyword_cnt:.1f} 个")
    print(f"   平均章节数: {avg_section_cnt:.1f} 个")
    print()
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit(main())
