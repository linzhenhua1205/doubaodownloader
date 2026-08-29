#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度重构系统与运维目录下的markdown文档 - V7 最终稳定版
策略：保守可靠，确保质量底线
"""

import os
import re
from pathlib import Path

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "系统与运维"

# 技术关键词库（经过验证的准确术语）
TECH_TERMS = [
    'Docker', 'Ansible', 'Zabbix', 'CMDB', 'BMC', 'ELK', 'Grafana', 'GLPI',
    'Jenkins', 'Dify', 'IPMI', 'CPLD', 'PCIe', 'PostgreSQL', 'SonarQube',
    'DevOps', 'AIOps', 'Kubernetes', 'K8s', 'Nginx', 'CentOS',
    'SSH', 'SNMP', 'API', 'Webhook', 'FastAPI', 'YAML', 'Playbook',
    'FusionDirector', 'FusionServer', 'FusionOnline', 'PowerEdge',
    'UniSystem', 'Control-M', 'Helix', 'Cubox', 'Integrately',
    'LangBot', 'Gulp', 'RSS',
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


def find_intro_paragraph(real_content):
    """找引言段落（用于生成概要）"""
    text = re.sub(r'```.*?```', '', real_content, flags=re.DOTALL)
    
    paragraphs = []
    current_para = []
    
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            if current_para:
                para = ' '.join(current_para)
                if len(para) >= 30:
                    paragraphs.append(para)
                current_para = []
            continue
        
        # 跳过标题
        if re.match(r'^#{1,6}\s+', stripped):
            if current_para:
                para = ' '.join(current_para)
                if len(para) >= 30:
                    paragraphs.append(para)
                current_para = []
            continue
        
        # 跳过列表项（短行）
        if re.match(r'^\d+\.\s+\*\*', stripped) and len(stripped) < 60:
            continue
        if re.match(r'^[-*+]\s+\*\*', stripped) and len(stripped) < 60:
            continue
        
        # 跳过原文链接
        if re.match(r'^原文[：:]', stripped):
            continue
        
        # 跳过emoji开头的短行
        if re.match(r'^[🔗📝⚙️🎯✨✅🔍📌🏭💡📋📑🌟🔄]+\s*\*\*', stripped):
            continue
        
        # 跳过代码行
        if '```' in stripped:
            continue
        
        current_para.append(stripped)
    
    if current_para:
        para = ' '.join(current_para)
        if len(para) >= 30:
            paragraphs.append(para)
    
    # 返回第一个合适的段落（长度在30-95字之间）
    for para in paragraphs:
        if 30 <= len(para) <= 95:
            # 检查是否是完整通顺的句子（有句号或结尾词）
            if '。' in para or '了' in para or '的' in para:
                return para
    
    return None


def generate_summary(title, real_content):
    """生成高质量一句话概要（≤100字）"""
    title_clean = clean_title(title)
    
    # 方法1：找引言段落
    intro = find_intro_paragraph(real_content)
    if intro and 30 <= len(intro) <= 95:
        return intro
    
    # 方法2：基于标题生成通顺概要
    # 提取核心主题和角度
    if '：' in title_clean or ':' in title_clean:
        parts = re.split(r'[：:]', title_clean, maxsplit=1)
        topic = parts[0].strip()
        angle = parts[1].strip()
        # 清理角度的后缀
        angle = re.sub(r'(详解|指南|解析|实践|全解|方案|教程|手册|深度解析|全景报告|市场格局|选型指南|核心能力要求)$', '', angle).strip()
        
        if angle:
            summary = f"本文深入解析{topic}，涵盖{angle}等核心内容"
        else:
            summary = f"本文详细介绍{topic}的核心原理与实践方法"
    else:
        topic = title_clean
        # 去掉后缀
        topic = re.sub(r'(详解|指南|解析|实践|全解|方案|教程|手册|全解析|深度解析|实战指南|完整指南|解决方案|功能解析|技术优势)$', '', topic).strip()
        summary = f"本文详细介绍{topic}的核心原理与实践应用"
    
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary


def extract_keywords(title, real_content):
    """提取3-5个核心关键词（保守策略：只用验证过的术语）"""
    title_clean = clean_title(title)
    
    result = []
    seen = set()
    
    # 第1步：从标题中匹配已知技术术语（最高优先级）
    title_lower = title_clean.lower()
    for term in TECH_TERMS:
        if len(term) <= 1:
            continue
        term_lower = term.lower()
        if term_lower in title_lower:
            if term_lower not in seen:
                seen.add(term_lower)
                result.append(term)
        if len(result) >= 5:
            break
    
    # 第2步：从标题提取英文缩写（可能不在词库中）
    if len(result) < 5:
        acronyms = re.findall(r'\b[A-Z]{2,8}(?:\s*[&+]\s*[A-Z]{2,8})?\b', title_clean)
        for a in acronyms:
            a = a.strip()
            if a.lower() not in seen and len(a) >= 2:
                # 检查是否是合理的缩写（全部大写或含特殊字符）
                if re.match(r'^[A-Z&+ -]{2,}$', a):
                    seen.add(a.lower())
                    result.append(a)
            if len(result) >= 5:
                break
    
    # 第3步：从正文中补充已知技术术语（出现频率高的）
    if len(result) < 5:
        text = re.sub(r'```.*?```', '', real_content, flags=re.DOTALL)
        text_lower = text.lower()
        for term in TECH_TERMS:
            if len(term) <= 1:
                continue
            term_lower = term.lower()
            if term_lower not in seen:
                count = text_lower.count(term_lower)
                if count >= 3:
                    seen.add(term_lower)
                    result.append(term)
                    if len(result) >= 5:
                        break
    
    # 第4步：确保3-5个，用通用术语补充
    defaults = ['运维', '监控', '自动化', '部署', '配置管理']
    if len(result) < 3:
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
    
    # 2. 三级标题
    if len(titles) < 3:
        h3s = re.findall(r'^###\s+(.+)$', real_content, re.MULTILINE)
        for h in h3s:
            h = h.strip()
            h = re.sub(r'^[🔗📝⚙️🎯✨✅🔍📌🏭💡📋📑🌟🔄]+\s*', '', h)
            if len(h) < 40 and h not in titles:
                if h not in ['核心要点', '关键数据', '阅读建议']:
                    titles.append(h)
            if len(titles) >= 8:
                break
    
    # 3. emoji加粗标题
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
    print("深度重构系统与运维目录下的markdown文档 V7 - 最终稳定版")
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
            print(f"      概要: {result['summary']}")
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
