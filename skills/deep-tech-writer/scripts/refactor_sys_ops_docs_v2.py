#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度重构系统与运维目录下的markdown文档 - V2 彻底清理版
清理所有模板化垃圾内容，保留真正有价值的原文内容
"""

import os
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "系统与运维"

STOP_WORDS = {
    "的", "是", "在", "和", "了", "与", "为", "以", "及", "等", "也", "都", "而",
    "其", "该", "此", "这", "那", "一个", "一种", "可以", "需要", "通过", "使用",
    "进行", "实现", "提供", "支持", "包括", "基于", "相关", "应用", "系统",
    "技术", "功能", "管理", "服务", "服务", "平台", "方案", "工具", "模块",
    "本文", "详细", "全面", "深入", "深度", "指南", "详解", "解析", "分析", "实践",
    "配置", "部署", "安装", "配置", "管理", "运维", "监控", "自动化",
    "核心", "要点", "内容", "问题", "方法", "方式", "过程", "结果",
}


def extract_frontmatter(content):
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return content[:end+3], content[end+3:].strip()
    return '', content


def clean_title(title):
    """清理标题中的emoji和特殊字符"""
    emoji_chars = '🛠️🌐📊📦🚀🖥️🐳📋💡📑🔍📝'
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
                # 跳过模板化的标题
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
    
    # 移除markdown标记
    text = re.sub(r'#{1,6}\s+', '', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'\[(.+?)\(.+?\)', r'\1', text)
    
    # 移除特殊行
    lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('>'):
            continue
        if stripped.startswith('|'):
            continue
        if stripped.startswith('-') and len(stripped) < 15:
            continue
        if '原文' in stripped and '链接' in stripped:
            continue
        if stripped.startswith('📝') or stripped.startswith('🔗') or stripped.startswith('⚙️'):
            continue
        lines.append(stripped)
    
    return ' '.join(lines[:100])  # 取前100行


def generate_summary(title, real_content):
    """生成高质量一句话概要（≤100字）"""
    text = extract_real_text(real_content)
    
    # 提取句子
    sentences = re.split(r'[。！？；\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
    
    # 评分选择最佳句子
    key_verbs = ['实现', '提供', '支持', '包括', '基于', '通过', '解决', '优化',
                 '部署', '配置', '管理', '监控', '分析', '集成', '构建', '介绍',
                 '详解', '解析', '指南', '方法', '原理', '机制', '方式']
    
    best_sentence = None
    best_score = 0
    
    for s in sentences[:15]:
        score = 0
        if 30 <= len(s) <= 90:
            score += 10
        elif 20 <= len(s) < 30:
            score += 5
        for verb in key_verbs:
            if verb in s:
                score += 3
        if best_score < score:
            best_score = score
            best_sentence = s
    
    if best_sentence and len(best_sentence) <= 100:
        return best_sentence
    
    # 备用方案：基于标题和前几句生成
    title_clean = clean_title(title)
    
    if sentences:
        # 取第一句的前70字
        first = sentences[0][:70]
        summary = f"本文介绍{title_clean}，{first}"
    else:
        summary = f"本文详细介绍{title_clean}的核心内容与实践方法"
    
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary


def extract_keywords(title, real_content):
    """提取3-5个核心关键词"""
    text = extract_real_text(real_content)
    title_clean = clean_title(title)
    
    # 从标题提取关键词（用中文词和英文缩写）
    title_words = []
    # 英文缩写
    title_acronyms = re.findall(r'\b[A-Z]{2,8}\b', title_clean)
    title_words.extend(title_acronyms)
    
    # 中文词（2-4字）
    title_cn = re.findall(r'[\u4e00-\u9fff]{2,4}', title_clean)
    for w in title_cn:
        if w not in STOP_WORDS:
            title_words.append(w)
    
    # 从正文提取高频词
    cn_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
    cn_words = [w for w in cn_words if w not in STOP_WORDS]
    word_counts = Counter(cn_words)
    
    # 英文缩写
    acronyms = re.findall(r'\b[A-Z]{2,8}\b', text)
    acronym_counts = Counter(acronyms)
    
    # 合并排序：标题词优先
    result = []
    seen = set()
    
    # 先加标题中的词
    for w in title_words:
        w_lower = w.lower()
        if w_lower not in seen and len(w) >= 2:
            seen.add(w_lower)
            result.append(w)
            if len(result) >= 3:
                break
    
    # 再加正文高频词
    combined = {}
    for w, c in word_counts.most_common(30):
        combined[w] = c
    for a, c in acronym_counts.most_common(15):
        combined[a] = c * 2
    
    sorted_kw = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    
    for kw, _ in sorted_kw:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            result.append(kw)
            if len(result) >= 5:
                break
    
    # 确保3-5个
    if len(result) < 3:
        result.append('运维')
    if len(result) < 3:
        result.append('技术')
    
    return result[:5]


def extract_h2_titles(real_content):
    """提取真正的二级标题"""
    h2s = re.findall(r'^##\s+(.+)$', real_content, re.MULTILINE)
    
    # 清理标题
    cleaned = []
    for h in h2s:
        h = h.strip()
        # 跳过模板标题
        if h in ['内容', '参考文件', 'Changelog', '变更日志']:
            continue
        # 跳过emoji开头的模板
        if re.match(r'^[🌐🔍🆕📚📖📝📎🔗💼🛠️🌍]', h):
            continue
        cleaned.append(h)
    
    # 如果没有二级标题，看看三级标题
    if not cleaned:
        h3s = re.findall(r'^###\s+(.+)$', real_content, re.MULTILINE)
        for h in h3s[:6]:
            h = h.strip()
            if len(h) < 30:
                cleaned.append(h)
    
    return cleaned[:8]  # 最多8个


def generate_toc(h2_titles):
    """生成目录"""
    if not h2_titles:
        return ''
    
    toc_lines = []
    for title in h2_titles:
        # 生成锚点
        slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', title).lower()
        slug = re.sub(r'-+', '-', slug).strip('-')
        toc_lines.append(f'- [{title}](#{slug})')
    
    return '\n'.join(toc_lines)


def extract_original_url(content):
    """提取原文链接"""
    # 匹配多种格式
    patterns = [
        r'原文[链接：:]*\s*\[([^\]]+)\]\((https?://[^\s\)]+)\)',
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
    
    # 提取二级标题用于目录
    h2_titles = extract_h2_titles(real_content)
    toc = generate_toc(h2_titles)
    
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
    # 清理一下内容开头的 "## 内容" 标题
    content_clean = real_content
    content_clean = re.sub(r'^##\s*内容\s*\n', '', content_clean).strip()
    # 清理连续空行
    content_clean = re.sub(r'\n{3,}', '\n\n', content_clean)
    
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
        'h2_count': len(h2_titles),
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
    print("深度重构系统与运维目录下的markdown文档 V2 - 彻底清理版")
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
    print("🚀 开始深度重构（清理模板化垃圾内容）...")
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
            print(f"   ✅ 完成 | 概要{result['summary_length']}字 | 关键词{result['keyword_count']}个 | H2标题{result['h2_count']}个 | 删除重复H1:{result['dup_h1_removed']}")
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
    avg_h2_cnt = sum(s['h2_count'] for s in all_stats) / max(len(all_stats), 1)
    print(f"   平均概要长度: {avg_summary_len:.1f} 字")
    print(f"   平均关键词数: {avg_keyword_cnt:.1f} 个")
    print(f"   平均H2标题数: {avg_h2_cnt:.1f} 个")
    print()
    
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    exit(main())
