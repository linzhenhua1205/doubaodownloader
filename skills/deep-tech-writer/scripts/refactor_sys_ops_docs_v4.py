#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度重构系统与运维目录下的markdown文档 - V4 最终版
正确处理已被多次重构的文件，提取真正的正文内容
"""

import os
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "系统与运维"

TECH_KEYWORDS = [
    'Docker', 'Ansible', 'Zabbix', 'CMDB', 'BMC', 'ELK', 'Grafana', 'GLPI',
    'Jenkins', 'Dify', 'IPMI', 'CPLD', 'PCIe', 'PostgreSQL', 'SonarQube',
    'DevOps', 'AIOps', 'K8s', 'Kubernetes', 'Nginx', 'Linux', 'CentOS',
    'SSH', 'SNMP', 'API', 'Webhook', 'FastAPI', 'YAML', 'Playbook',
    '容器', '镜像', '端口映射', '自动化运维', '监控系统', '配置管理',
    '服务器', '运维', '部署', '监控', '告警', '日志', '集群',
    '设备生命周期', '资产管理', '智能运维', '网络配置',
    'FusionDirector', 'FusionServer', 'FusionOnline', 'H3C', 'DELL',
    'PowerEdge', 'UniSystem', 'Control-M', 'Helix',
    'Cubox', 'Integrately', 'RSS', 'Gulp',
    'LangBot',
]


def extract_frontmatter(content):
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return content[:end+3], content[end+3:].strip()
    return '', content


def clean_title(title):
    emoji_chars = '🛠️🌐📊📦🚀🖥️🐳📋💡📑🔍📝✨⚙️🎯📈📉🏷️🌐🔍🆕📚📖📎🔗💼🛠️🌍📌🏭💡'
    for c in emoji_chars:
        title = title.replace(c, '')
    return title.strip()


def extract_first_h1(body):
    """提取第一个H1标题"""
    m = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def find_real_body_content(body):
    """
    从body中提取真正的正文内容。
    跳过：H1、概要、关键词、目录、模板化章节
    返回：真正的正文（可能包含二级/三级标题）
    """
    lines = body.split('\n')
    
    # 跳过开头的 H1
    start_idx = 0
    for i, line in enumerate(lines):
        if re.match(r'^#\s+', line):
            start_idx = i + 1
            break
    
    # 从 start_idx 开始，找到真正内容的开始
    # 跳过概要、关键词、目录等
    content_start = -1
    
    # 标记：是否在找内容开始
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        
        # 遇到 "原文：" 或 "原文链接" 行，后面就是内容了
        if re.match(r'^原文[：:]', line) or re.match(r'^🔗\s*\*\*原文链接', line):
            content_start = i
            break
        
        # 遇到 "## 内容" 章节
        if re.match(r'^##\s*内容\s*$', line):
            content_start = i + 1
            break
        
        # 遇到第一个非模板、非概要、非目录的二级或三级标题
        if re.match(r'^#{2,3}\s+', line):
            title = re.sub(r'^#{2,3}\s+', '', line).strip()
            # 检查是否是模板化标题
            template_titles = [
                '📑 目录', '💡 核心要点', '📋 快速导读',
                '🌐 背景与上下文', '🔍 深度解读', '🆕 2025-2026 最新进展',
                '📚 相关技术资源', '📖 延伸阅读', '📝 参考来源',
                '📎 相关素材', '🔗 相关文章', '参考文件', 'Changelog',
                '变更日志', '知识关联', '重定向说明',
                '💼 案例补充', '🛠️ 实践指南', '🌍 行业影响',
                '风险与挑战', '行业影响分析', '技术原理补充',
                'changelog', '内容'
            ]
            is_template = False
            for tt in template_titles:
                if tt in title:
                    is_template = True
                    break
            
            if not is_template:
                # 这是真正的内容标题
                content_start = i
                break
        
        # 遇到概要或关键词行，继续跳过
        if line.startswith('> **概要**') or line.startswith('> **关键词**'):
            i += 1
            continue
        
        # 跳过空行和引用行
        if not line or line.startswith('>'):
            i += 1
            continue
        
        i += 1
    
    if content_start == -1:
        # 没找到，尝试找第一个有实质内容的段落
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            if line and not line.startswith('#') and not line.startswith('>') and not line.startswith('|'):
                if len(line) > 20:
                    content_start = i
                    break
    
    if content_start == -1:
        return body  # 实在找不到就返回全部
    
    # 从 content_start 开始，找内容结束位置
    # 遇到模板化的二级标题就停止
    content_lines = []
    i = content_start
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 检查是否是模板化的二级标题（内容结束标记）
        if re.match(r'^##\s+', stripped):
            title = re.sub(r'^##\s+', '', stripped).strip()
            template_endings = [
                '🌐 背景与上下文', '🔍 深度解读', '🆕 2025-2026 最新进展',
                '📚 相关技术资源', '📖 延伸阅读', '📝 参考来源',
                '📎 相关素材', '🔗 相关文章', '参考文件', 'Changelog',
                '变更日志', '知识关联', '💼 案例补充', '🛠️ 实践指南',
                '🌍 行业影响', '风险与挑战', '行业影响分析', '技术原理补充',
                '实践指南', '案例补充', 'changelog', '📑 目录'
            ]
            is_ending = False
            for te in template_endings:
                if te in title:
                    is_ending = True
                    break
            if is_ending:
                break
        
        # 遇到 "---" 分隔符且后面是模板章节，停止
        if stripped == '---' and i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if re.match(r'^##\s+', next_line):
                next_title = re.sub(r'^##\s+', '', next_line).strip()
                template_endings = [
                    '🌐 背景与上下文', '🔍 深度解读', '参考文件', 'Changelog'
                ]
                for te in template_endings:
                    if te in next_title:
                        break
                else:
                    content_lines.append(line)
                    i += 1
                    continue
                break
        
        content_lines.append(line)
        i += 1
    
    result = '\n'.join(content_lines).strip()
    
    # 清理开头的 "## 内容"
    result = re.sub(r'^##\s*内容\s*\n', '', result).strip()
    
    # 清理连续空行
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result


def extract_real_text(content):
    """从内容中提取纯文本"""
    text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    text = re.sub(r'`[^`]+`', '', text)
    
    lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^#{1,6}\s+', stripped):
            continue
        if stripped.startswith('>'):
            continue
        if stripped.startswith('|'):
            continue
        if '原文' in stripped and ('链接' in stripped or '：' in stripped):
            continue
        if re.match(r'^[🔗📝⚙️🎯✨✅🔍📌🏭💡📋📑]', stripped) and len(stripped) < 25:
            continue
        if re.match(r'^[-=]{3,}$', stripped):
            continue
        if stripped.startswith('- [') and '](' in stripped:
            continue
        
        lines.append(stripped)
    
    return ' '.join(lines[:60])


def generate_summary(title, real_content):
    """生成高质量一句话概要（≤100字）"""
    text = extract_real_text(real_content)
    title_clean = clean_title(title)
    
    sentences = re.split(r'[。！？；\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 12]
    
    key_verbs = ['实现', '提供', '支持', '包括', '基于', '通过', '解决', '优化',
                 '部署', '配置', '管理', '监控', '分析', '集成', '构建',
                 '详解', '介绍', '阐述', '探讨', '对比', '解析']
    
    best_sentence = None
    best_score = 0
    
    for s in sentences[:10]:
        if '原文' in s:
            continue
        if len(s) < 20:
            continue
            
        score = 0
        if 30 <= len(s) <= 85:
            score += 10
        elif 20 <= len(s) < 30:
            score += 3
        for verb in key_verbs:
            if verb in s:
                score += 3
        if score > best_score:
            best_score = score
            best_sentence = s
    
    if best_sentence and 15 <= len(best_sentence) <= 100:
        return best_sentence
    
    # 从标题提取核心主题
    core_topic = re.sub(r'[：:].*$', '', title_clean)
    core_topic = re.sub(r'(详解|指南|解析|实践|全解|方案|教程|手册|全解析|深度解析|实战指南|完整指南|解决方案)$', '', core_topic)
    core_topic = core_topic.strip()
    
    # 找一个开头的句子
    for s in sentences[:5]:
        if len(s) >= 15 and '原文' not in s:
            # 组合标题+句子
            summary = f"本文介绍{core_topic}，{s[:60]}"
            if len(summary) <= 100:
                return summary
            break
    
    summary = f"本文详细介绍{core_topic}的核心原理与实践方法"
    return summary[:100]


def extract_keywords(title, real_content):
    """提取3-5个核心关键词"""
    title_clean = clean_title(title)
    text = extract_real_text(real_content)
    
    result = []
    seen = set()
    
    # 第1步：从标题提取英文缩写
    acronyms = re.findall(r'\b[A-Z]{2,8}(?:\s*[&+]\s*[A-Z]{2,8})?\b', title_clean)
    for a in acronyms:
        a = a.strip()
        if a.lower() not in seen:
            seen.add(a.lower())
            result.append(a)
    
    # 第2步：从标题和正文中匹配已知技术关键词
    title_lower = title_clean.lower()
    text_lower = text.lower()
    
    for kw in TECH_KEYWORDS:
        kw_lower = kw.lower()
        if kw_lower in title_lower and kw_lower not in seen:
            seen.add(kw_lower)
            result.append(kw)
        if len(result) >= 4:
            break
    
    # 从正文补充（出现次数多的）
    if len(result) < 5:
        for kw in TECH_KEYWORDS:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                count = text_lower.count(kw_lower)
                if count >= 2:
                    seen.add(kw_lower)
                    result.append(kw)
                    if len(result) >= 5:
                        break
    
    # 第3步：从标题用分隔符提取中文短语
    if len(result) < 5:
        title_parts = re.split(r'[：:、，,\s_]+', title_clean)
        for part in title_parts:
            part = part.strip()
            if 2 <= len(part) <= 8 and part.lower() not in seen:
                # 检查是否是技术相关的
                is_tech = False
                for kw in TECH_KEYWORDS:
                    if kw in part or part in kw:
                        is_tech = True
                        break
                if is_tech or (len(part) >= 3 and not any(c in part for c in '的了是在与和为以')):
                    seen.add(part.lower())
                    result.append(part)
                    if len(result) >= 5:
                        break
    
    # 第4步：从正文提取高频词
    if len(result) < 5:
        cn_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        stop = {'的话', '这个', '那个', '一个', '一种', '一些', '可以',
                '需要', '进行', '实现', '提供', '支持', '包括', '基于',
                '通过', '使用', '应用', '系统', '技术', '功能', '管理',
                '服务', '平台', '方案', '工具', '模块', '问题', '方法',
                '方式', '过程', '结果', '内容', '核心', '要点', '我们',
                '可以', '如果', '因为', '所以', '但是', '而且', '或者',
                '以及', '等等', '这样', '那样', '什么', '怎么', '为什么'}
        filtered = [w for w in cn_words if w not in stop and len(w) >= 2]
        word_counts = Counter(filtered)
        for w, c in word_counts.most_common(30):
            if c >= 3 and w.lower() not in seen and len(w) <= 6:
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
    
    h2s = re.findall(r'^##\s+(.+)$', real_content, re.MULTILINE)
    for h in h2s:
        h = h.strip()
        if h == '内容':
            continue
        if re.match(r'^[🌐🔍🆕📚📖📝📎🔗💼🛠️🌍📑]', h):
            continue
        if '参考文件' in h or 'Changelog' in h or '变更日志' in h:
            continue
        if len(h) < 40:
            titles.append(h)
    
    if len(titles) < 3:
        h3s = re.findall(r'^###\s+(.+)$', real_content, re.MULTILINE)
        for h in h3s:
            h = h.strip()
            if len(h) < 40 and h not in titles:
                # 跳过 "核心要点"、"关键数据"、"阅读建议" 等模板
                if h not in ['核心要点', '关键数据', '阅读建议']:
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
    
    # 提取frontmatter
    frontmatter, body = extract_frontmatter(content)
    
    # 获取标题
    title = extract_first_h1(body)
    if not title:
        title = filepath.stem
    
    # 提取真正的正文内容
    real_content = find_real_body_content(body)
    
    # 如果提取到的内容太少，可能提取错了，用全部内容
    if len(real_content) < 100:
        real_content = body
        # 去掉H1
        real_content = re.sub(r'^#\s+.+$\n+', '', real_content, count=1)
    
    # 生成概要
    summary = generate_summary(title, real_content)
    
    # 提取关键词
    keywords = extract_keywords(title, real_content)
    keywords_str = ' · '.join(keywords)
    
    # 提取章节标题用于目录
    section_titles = extract_section_titles(real_content)
    toc = generate_toc(section_titles)
    
    # 提取原文链接
    orig_url, orig_title = extract_original_url(content)
    
    # 清理正文内容
    content_clean = real_content
    # 清理开头的 "原文：..." 行（但保留原文链接行作为参考）
    # 清理连续空行
    content_clean = re.sub(r'\n{3,}', '\n\n', content_clean)
    # 清理末尾的分隔线
    content_clean = re.sub(r'\n[-=]{3,}\s*$', '', content_clean).strip()
    
    # 构建新文档
    new_content = []
    
    # 1. Frontmatter
    if frontmatter:
        new_content.append(frontmatter)
        new_content.append('')
    
    # 2. H1标题
    new_content.append(f'# {title}')
    new_content.append('')
    
    # 3. 概要和关键词
    new_content.append(f'> **概要**: {summary}')
    new_content.append(f'> **关键词**: {keywords_str}')
    new_content.append('')
    
    # 4. 目录
    if toc:
        new_content.append('## 📑 目录')
        new_content.append('')
        new_content.append(toc)
        new_content.append('')
    
    # 5. 正文内容
    new_content.append(content_clean)
    new_content.append('')
    
    # 6. 参考文件
    new_content.append('## 参考文件')
    new_content.append('')
    if orig_url:
        new_content.append(f'- [{orig_title}]({orig_url})')
    else:
        new_content.append('- 公开技术资料与官方文档')
    new_content.append('')
    
    # 7. Changelog
    new_content.append('## Changelog')
    new_content.append('')
    new_content.append('| 版本 | 日期 | 更新内容 |')
    new_content.append('|------|------|---------|')
    new_content.append('| v2.0 | 2026-07-27 | 深度重构版：清理模板化垃圾内容，重写概要和关键词，标准化格式 |')
    new_content.append('| v1.0 | 初始版本 | 原文基础内容 |')
    new_content.append('')
    
    return '\n'.join(new_content), {
        'summary_length': len(summary),
        'keyword_count': len(keywords),
        'title': title,
        'section_count': len(section_titles),
        'content_length': len(real_content),
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
    print("深度重构系统与运维目录下的markdown文档 V4 - 最终版")
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
            kws = extract_keywords(result['title'], 
                                    find_real_body_content(
                                        re.sub(r'^---.*?---', '', 
                                               open(filepath, 'r', encoding='utf-8').read(), 
                                               flags=re.DOTALL)))
            kw_str = ' · '.join(kws)
            print(f"   ✅ 完成 | 概要{result['summary_length']}字 | 关键词{result['keyword_count']}个 | 章节{result['section_count']}个")
            print(f"      关键词: {kw_str}")
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
    
    # 质量统计
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
