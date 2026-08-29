#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度重构系统与运维目录下的markdown文档 - V3 优化版
重点改进：关键词提取、概要生成、目录提取
"""

import os
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "系统与运维"

# 技术关键词词典（用于匹配）
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
    """清理标题中的emoji和特殊字符"""
    emoji_chars = '🛠️🌐📊📦🚀🖥️🐳📋💡📑🔍📝✨⚙️🎯📈📉🏷️'
    for c in emoji_chars:
        title = title.replace(c, '')
    return title.strip()


def find_real_content_section(body):
    """找到真正的内容区块"""
    lines = body.split('\n')
    
    # 找到 "## 内容" 章节的位置
    content_start = -1
    for i, line in enumerate(lines):
        if re.match(r'^##\s*内容\s*$', line.strip()):
            content_start = i + 1
            break
    
    if content_start == -1:
        # 如果没有"内容"章节，找第一个非模板的二级标题开始
        for i, line in enumerate(lines):
            if re.match(r'^##\s+', line):
                title = line.strip()
                skip_patterns = ['📋 快速导读', '💡 核心要点', '📑 目录', 
                            '📋 快速导读', '🌐 背景与上下文', '🔍 深度解读',
                            '🆕 2025-2026 最新进展', '📚 相关技术资源',
                            '📖 延伸阅读', '📝 参考来源', 'changelog',
                            '📎 相关素材', '🔗 相关文章', '参考文件',
                            'Changelog', '变更日志', '知识关联', '重定向说明',
                            '💼 案例补充', '🛠️ 实践指南', '🌍 行业影响']
                should_skip = False
                for pat in skip_patterns:
                    if pat in title:
                        should_skip = True
                        break
                if not should_skip:
                    content_start = i
                    break
    
    if content_start == -1:
        return body
    
    # 从 content_start 开始，找内容，直到遇到模板化的二级标题
    content_lines = []
    i = content_start
    while i < len(lines):
        line = lines[i]
        if re.match(r'^##\s+', line):
            title = line.strip()
            skip_patterns = ['🌐 背景与上下文', '🔍 深度解读',
                            '🆕 2025-2026 最新进展', '📚 相关技术资源',
                            '📖 延伸阅读', '📝 参考来源', 'changelog',
                            '📎 相关素材', '🔗 相关文章', '参考文件',
                            'Changelog', '变更日志', '知识关联',
                            '💼 案例补充', '🛠️ 实践指南', '🌍 行业影响',
                            '风险与挑战', '行业影响分析', '技术原理补充',
                            '实践指南', '案例补充']
            should_skip = False
            for pat in skip_patterns:
                if pat in title:
                    should_skip = True
                    break
            if should_skip:
                break
        content_lines.append(line)
        i += 1
    
    return '\n'.join(content_lines).strip()


def count_h1_titles(content):
    h1s = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
    return len(h1s), h1s


def remove_duplicate_h1(content):
    """删除重复的H1标题，只保留第一个"""
    lines = content.split('\n')
    h1_count = 0
    new_lines = []
    
    for line in lines:
        if re.match(r'^#\s+.+$', line):
            h1_count += 1
            if h1_count == 1:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines), h1_count - 1


def extract_real_text(content):
    """从内容中提取纯文本用于生成概要和关键词"""
    # 移除代码块
    text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        # 跳过标题行
        if re.match(r'^#{1,6}\s+', stripped):
            continue
        # 跳过引用
        if stripped.startswith('>'):
            continue
        # 跳过表格
        if stripped.startswith('|'):
            continue
        # 跳过原文链接行
        if '原文' in stripped and ('链接' in stripped or '：' in stripped or ':' in stripped):
            continue
        # 跳过只有emoji开头的短行
        if re.match(r'^[🔗📝⚙️🎯✨✅🔍📌🏭💡]', stripped) and len(stripped) < 20:
            continue
        # 跳过分隔线
        if re.match(r'^[-=]{3,}$', stripped):
            continue
        
        lines.append(stripped)
    
    return ' '.join(lines[:80])


def generate_summary(title, real_content):
    """生成高质量一句话概要（≤100字）"""
    text = extract_real_text(real_content)
    title_clean = clean_title(title)
    
    # 提取句子
    sentences = re.split(r'[。！？；\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 12]
    
    # 评分选择最佳句子
    key_verbs = ['实现', '提供', '支持', '包括', '基于', '通过', '解决', '优化',
                 '部署', '配置', '管理', '监控', '分析', '集成', '构建',
                 '详解', '介绍', '阐述', '探讨', '对比', '解析']
    
    best_sentence = None
    best_score = 0
    
    for s in sentences[:12]:
        # 跳过包含 "原文" 的句子
        if '原文' in s:
            continue
        # 跳过太短的
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
    
    # 备用方案：基于标题+前几句内容构建
    if len(sentences) >= 2:
        # 找一个好的开头
        for s in sentences[:5]:
            if '本文' in s or '介绍' in s or '详解' in s or '阐述' in s:
                if 20 <= len(s) <= 100:
                    return s[:100]
    
    # 最后方案：用标题+通用描述
    # 从标题提取核心主题
    core_topic = title_clean
    # 去掉 "详解"、"指南"、"解析" 等后缀
    core_topic = re.sub(r'[：:].*$', '', core_topic)
    core_topic = re.sub(r'(详解|指南|解析|实践|全解|方案|教程|手册|全解析)$', '', core_topic)
    
    summary = f"本文详细介绍{core_topic}的核心原理、实践方法与应用场景"
    
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary


def extract_keywords(title, real_content):
    """提取3-5个核心关键词"""
    title_clean = clean_title(title)
    text = extract_real_text(real_content)
    
    result = []
    seen = set()
    
    # 第1步：从标题中提取英文缩写和技术术语（优先级最高）
    # 英文缩写
    acronyms = re.findall(r'\b[A-Z]{2,8}(?:\s*[&+]\s*[A-Z]{2,8})?\b', title_clean)
    for a in acronyms:
        a = a.strip()
        if a.lower() not in seen:
            seen.add(a.lower())
            result.append(a)
    
    # 从标题中提取已知的技术关键词
    title_lower = title_clean.lower()
    for kw in TECH_KEYWORDS:
        if kw.lower() in title_lower and kw.lower() not in seen:
            seen.add(kw.lower())
            result.append(kw)
    
    # 第2步：从正文中提取已知的技术关键词
    text_lower = text.lower()
    for kw in TECH_KEYWORDS:
        if kw.lower() in text_lower and kw.lower() not in seen:
            # 统计出现次数
            count = text_lower.count(kw.lower())
            if count >= 2:  # 至少出现2次
                seen.add(kw.lower())
                result.append(kw)
                if len(result) >= 5:
                    break
    
    # 第3步：从标题中用分隔符提取中文短语
    # 用标点符号分割标题
    title_parts = re.split(r'[：:、，,\s]+', title_clean)
    for part in title_parts:
        part = part.strip()
        if 2 <= len(part) <= 8 and part not in seen:
            # 检查是否是有意义的词（不是单个字的组合问题）
            # 简单过滤：包含已知词根
            has_meaning = False
            for kw in TECH_KEYWORDS:
                if kw in part or part in kw:
                    has_meaning = True
                    break
            if has_meaning and part.lower() not in seen:
                seen.add(part.lower())
                result.append(part)
    
    # 第4步：从正文提取高频中文词（2-4字）
    if len(result) < 5:
        cn_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        # 过滤
        filtered = []
        for w in cn_words:
            if len(w) < 2:
                continue
            # 跳过常见无意义词
            stop = ['的话', '这个', '那个', '一个', '一种', '一些', '可以',
                    '需要', '进行', '实现', '提供', '支持', '包括', '基于',
                    '通过', '使用', '应用', '系统', '技术', '功能', '管理',
                    '服务', '平台', '方案', '工具', '模块', '问题', '方法',
                    '方式', '过程', '结果', '内容', '核心', '要点']
            if w in stop:
                continue
            filtered.append(w)
        
        word_counts = Counter(filtered)
        for w, c in word_counts.most_common(20):
            if c >= 3 and w.lower() not in seen:
                seen.add(w.lower())
                result.append(w)
                if len(result) >= 5:
                    break
    
    # 确保3-5个
    if len(result) < 3:
        # 从标题再提取一些
        for part in re.split(r'[：:、，,\s]+', title_clean):
            part = part.strip()
            if 2 <= len(part) <= 10 and part.lower() not in seen:
                seen.add(part.lower())
                result.append(part)
                if len(result) >= 3:
                    break
    
    # 最后兜底
    if len(result) < 3:
        if '运维' not in seen:
            result.append('运维')
        if '监控' not in seen and len(result) < 3:
            result.append('监控')
    
    return result[:5]


def extract_section_titles(real_content):
    """提取章节标题用于目录"""
    titles = []
    
    # 优先提取二级标题
    h2s = re.findall(r'^##\s+(.+)$', real_content, re.MULTILINE)
    for h in h2s:
        h = h.strip()
        if h == '内容':
            continue
        if re.match(r'^[🌐🔍🆕📚📖📝📎🔗💼🛠️🌍]', h):
            continue
        if len(h) < 40:
            titles.append(h)
    
    # 如果二级标题太少，提取三级标题
    if len(titles) < 3:
        h3s = re.findall(r'^###\s+(.+)$', real_content, re.MULTILINE)
        for h in h3s:
            h = h.strip()
            if len(h) < 40 and h not in titles:
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
        # 生成锚点
        slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', title).lower()
        slug = re.sub(r'-+', '-', slug).strip('-')
        toc_lines.append(f'- [{title}](#{slug})')
    
    return '\n'.join(toc_lines)


def extract_original_url(content):
    """提取原文链接"""
    # 匹配多种格式
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
    
    # 找第一个URL
    urls = re.findall(r'https?://[^\s\)\]]+', content)
    if urls:
        return urls[0], '参考来源'
    
    return None, None


def rebuild_document(content, filepath):
    """彻底重构文档"""
    filepath = Path(filepath)
    
    # 提取frontmatter
    frontmatter, body = extract_frontmatter(content)
    
    # 获取标题
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = filepath.stem
    
    # 清理重复H1
    body, dup_h1_count = remove_duplicate_h1(body)
    
    # 提取真正的内容
    real_content = find_real_content_section(body)
    
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
    
    # 5. 真正的正文内容
    # 清理开头的 "## 内容" 标题
    content_clean = real_content
    content_clean = re.sub(r'^##\s*内容\s*\n', '', content_clean).strip()
    # 清理连续空行
    content_clean = re.sub(r'\n{3,}', '\n\n', content_clean)
    # 清理末尾的分隔线
    content_clean = re.sub(r'\n[-=]{3,}\s*$', '', content_clean)
    
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
        'dup_h1_removed': dup_h1_count,
        'summary_length': len(summary),
        'keyword_count': len(keywords),
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
    print("深度重构系统与运维目录下的markdown文档 V3 - 关键词优化版")
    print("=" * 70)
    
    md_files = sorted(TARGET_DIR.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'index.md']
    
    print(f"发现 {len(md_files)} 个markdown文件（已排除index.md）")
    print()
    
    # 前置检查
    print("🔍 前置质量检查...")
    total_h1_issues = 0
    files_with_issues = []
    
    for f in md_files:
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
        h1_count, _ = count_h1_titles(content)
        if h1_count > 1:
            total_h1_issues += h1_count - 1
            files_with_issues.append((f.name, h1_count))
    
    print(f"   发现 {len(files_with_issues)} 个文件有重复H1，共 {total_h1_issues} 个重复H1")
    for name, cnt in files_with_issues:
        print(f"   - {name}: {cnt}个H1")
    print()
    
    # 开始重构
    print("🚀 开始深度重构...")
    print()
    
    success_count = 0
    fail_count = 0
    errors = []
    total_dup_h1 = 0
    all_stats = []
    
    for i, filepath in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] 处理: {filepath.name}")
        success, result = process_file(filepath)
        if success:
            success_count += 1
            total_dup_h1 += result['dup_h1_removed']
            all_stats.append(result)
            kws = ' · '.join(extract_keywords(result['title'], find_real_content_section(
                open(filepath, 'r', encoding='utf-8').read())))
            print(f"   ✅ 完成 | 概要{result['summary_length']}字 | 关键词{result['keyword_count']}个 | 章节{result['section_count']}个")
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
    print(f"🗑️  删除重复H1: {total_dup_h1} 个")
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
