#!/usr/bin/env python3
"""
深度重构系统与运维目录下的markdown文档
遵循 deep-tech-writer 六步工作流进行质量提升
"""

import os
import re
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path("h:/github/cowkb")
TARGET_DIR = BASE_DIR / "discover" / "site" / "系统与运维"

STOP_WORDS = {
    "的", "是", "在", "和", "了", "与", "为", "以", "及", "等", "也", "都", "而",
    "其", "该", "此", "这", "那", "一个", "一种", "可以", "需要", "通过", "使用",
    "进行", "实现", "提供", "支持", "包括", "基于", "相关", "应用", "系统",
    "技术", "功能", "管理", "服务", "平台", "方案", "工具", "模块",
}

def extract_frontmatter(content):
    """提取YAML frontmatter"""
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return content[:end+3], content[end+3:].strip()
    return '', content

def count_h1_titles(content):
    """统计H1标题数量"""
    h1s = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
    return len(h1s), h1s

def remove_duplicate_h1(content):
    """删除重复的H1标题，只保留第一个"""
    lines = content.split('\n')
    h1_count = 0
    new_lines = []
    first_h1 = None
    
    for line in lines:
        if re.match(r'^#\s+.+$', line):
            h1_count += 1
            if h1_count == 1:
                first_h1 = line
                new_lines.append(line)
            # 跳过重复的H1
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines), h1_count - 1  # 返回删除的数量

def remove_wrong_template_sections(content):
    """删除错误的模板内容（快速导读、核心要点中的语义驱动等）"""
    lines = content.split('\n')
    new_lines = []
    skip_mode = None
    skip_depth = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 检测并删除 "## 📋 快速导读" 整个区块
        if re.match(r'^##\s*📋\s*快速导读', line):
            skip_mode = 'quick_guide'
            skip_depth = 0
            i += 1
            continue
        
        # 检测并删除 "## 💡 核心要点" 区块（如果内容是错误模板）
        if re.match(r'^##\s*💡\s*核心要点', line):
            # 检查后续内容是否是错误的模板
            j = i + 1
            is_wrong = False
            while j < len(lines) and j < i + 10:
                if '语义驱动' in lines[j] or '意图驱动' in lines[j] or '数据瓶颈' in lines[j]:
                    is_wrong = True
                    break
                if re.match(r'^##\s+', lines[j]):
                    break
                j += 1
            
            if is_wrong:
                skip_mode = 'core_points'
                skip_depth = 0
                i += 1
                continue
        
        # 在跳过模式下
        if skip_mode:
            # 检查是否遇到下一个二级标题
            if re.match(r'^##\s+', line) and not re.match(r'^###\s+', line):
                skip_mode = None
                new_lines.append(line)
            i += 1
            continue
        
        # 单独删除核心要点的错误内容行
        if ('语义驱动' in line and '告警降噪' in line) or \
           ('意图驱动' in line and '自然语言' in line) or \
           ('数据瓶颈' in line and '60%项目' in line):
            i += 1
            continue
        
        # 删除 "关键数据" 部分的错误内容
        if re.match(r'###\s*关键数据', line):
            # 检查下几行是否是错误模板
            j = i + 1
            is_wrong = False
            while j < len(lines) and j < i + 5:
                if '70%-99%压缩' in lines[j] or '60%项目' in lines[j]:
                    is_wrong = True
                    break
                if re.match(r'^#{1,3}\s+', lines[j]):
                    break
                j += 1
            if is_wrong:
                # 跳过整个关键数据小节
                i = j
                continue
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines)

def extract_main_content(content):
    """提取正文核心内容用于生成概要"""
    # 移除frontmatter
    _, body = extract_frontmatter(content)
    
    # 移除代码块
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    
    # 移除标题行和特殊行
    lines = []
    for line in body.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('>'):
            continue
        if stripped.startswith('|'):
            continue
        if stripped.startswith('-') and len(stripped) < 20:
            continue
        if '原文链接' in stripped or '原文：' in stripped:
            continue
        if '发布时间' in stripped or '分类' in stripped or '内容类型' in stripped:
            continue
        if '素材价值' in stripped:
            continue
        lines.append(stripped)
    
    return ' '.join(lines[:50])  # 取前50行

def generate_summary(title, content):
    """基于内容生成高质量一句话概要（≤100字）"""
    main_text = extract_main_content(content)
    
    # 提取关键句子
    sentences = re.split(r'[。！？\n]', main_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    # 优先选择包含核心动词的句子
    key_verbs = ['实现', '提供', '支持', '包括', '基于', '通过', '解决', '优化',
                 '部署', '配置', '管理', '监控', '分析', '集成', '构建']
    
    best_sentence = None
    best_score = 0
    
    for s in sentences[:10]:
        score = 0
        if len(s) > 30 and len(s) < 100:
            score += 5
        for verb in key_verbs:
            if verb in s:
                score += 2
        if score > best_score:
            best_score = score
            best_sentence = s
    
    if best_sentence and len(best_sentence) <= 100:
        return best_sentence
    
    # 如果没有找到好的句子，基于标题和内容生成
    # 提取关键词
    words = extract_keywords_from_text(main_text, 8)
    
    # 构建概要
    title_clean = re.sub(r'[🛠️🌐📊📦🚀🖥️🐳]', '', title).strip()
    
    if len(sentences) > 0:
        first_part = sentences[0][:60]
        summary = f"本文{first_part}"
    else:
        summary = f"本文介绍{title_clean}的核心内容与实践方法"
    
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary

def extract_keywords_from_text(text, count=5):
    """从文本中提取关键词"""
    # 提取中文词汇（2-6字）
    words = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
    
    # 过滤停用词
    words = [w for w in words if w not in STOP_WORDS and len(w) >= 2]
    
    # 词频统计
    word_counts = Counter(words)
    
    # 提取技术术语（大写英文缩写）
    acronyms = re.findall(r'\b[A-Z]{2,8}\b', text)
    acronym_counts = Counter(acronyms)
    
    # 合并排序
    combined = {}
    for word, cnt in word_counts.most_common(50):
        combined[word] = cnt
    for acr, cnt in acronym_counts.most_common(20):
        combined[acr] = cnt * 2  # 缩写权重更高
    
    sorted_keywords = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    
    result = []
    seen = set()
    for kw, _ in sorted_keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            result.append(kw)
            if len(result) >= count:
                break
    
    return result

def extract_title_and_keywords(content, title):
    """从标题和内容中提取3-5个核心关键词"""
    main_text = extract_main_content(content)
    
    # 从标题提取
    title_words = re.findall(r'[\u4e00-\u9fff]{2,}|[A-Za-z]+(?:[A-Za-z0-9])*', title)
    title_keywords = [w for w in title_words if w not in STOP_WORDS and len(w) >= 2]
    
    # 从正文提取
    content_keywords = extract_keywords_from_text(main_text, 10)
    
    # 合并：标题关键词优先，然后补充内容关键词
    result = []
    seen = set()
    
    for kw in title_keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen and len(kw) >= 2:
            seen.add(kw_lower)
            result.append(kw)
            if len(result) >= 3:
                break
    
    for kw in content_keywords:
        kw_lower = kw.lower()
        if kw_lower not in seen:
            seen.add(kw_lower)
            result.append(kw)
            if len(result) >= 5:
                break
    
    # 确保3-5个
    if len(result) < 3:
        # 补充通用技术词
        common = ['运维', '监控', '自动化', '部署', '配置']
        for c in common:
            if c not in seen:
                result.append(c)
                if len(result) >= 3:
                    break
    
    return result[:5]

def generate_toc(content):
    """生成目录（只列核心二级标题）"""
    h2_headings = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    
    # 过滤掉不需要的标题
    exclude_patterns = ['📑 目录', '📋 快速导读', '💡 核心要点', '参考文件', 
                        'Changelog', '变更日志', '知识关联', '重定向说明']
    
    filtered = []
    for h in h2_headings:
        h_clean = h.strip()
        skip = False
        for pat in exclude_patterns:
            if pat in h_clean:
                skip = True
                break
        if not skip:
            filtered.append(h_clean)
    
    if not filtered:
        return ''
    
    toc_lines = []
    for title in filtered:
        # 生成锚点（中文转小写，移除特殊字符）
        slug = re.sub(r'[^\w\u4e00-\u9fff-]', '-', title).lower()
        slug = re.sub(r'-+', '-', slug).strip('-')
        toc_lines.append(f'- [{title}](#{slug})')
    
    return '\n'.join(toc_lines)

def extract_references(content):
    """提取参考文件/链接"""
    # 提取URL
    urls = re.findall(r'https?://[^\s\)\]]+', content)
    
    # 提取原文链接
    original_links = re.findall(r'原文[链接：:]*\s*\[?([^\]]+)\]?\(?(https?://[^\s\)]+)\)?', content)
    
    return list(set(urls)), original_links

def build_changelog():
    """构建Changelog表格"""
    return """## Changelog

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v2.0 | 2026-07-27 | 深度重构版：按deep-tech-writer六步工作流优化，清理重复内容，重写概要和关键词，标准化格式 |
| v1.0 | 初始版本 | 原文基础内容 |
"""

def rebuild_document(content, filepath):
    """重构整个文档"""
    filepath = Path(filepath)
    filename = filepath.name
    
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
    
    # 删除错误的模板内容
    body = remove_wrong_template_sections(body)
    
    # 生成高质量概要
    summary = generate_summary(title, body)
    
    # 提取核心关键词
    keywords = extract_title_and_keywords(body, title)
    keywords_str = ' · '.join(keywords)
    
    # 生成目录
    toc = generate_toc(body)
    
    # 提取参考链接
    urls, original_links = extract_references(body)
    
    # 移除正文中已有的概要、关键词、目录、参考文件、changelog
    # 我们将重新构建标准结构
    
    # 提取正文主体（移除frontmatter后，在第一个##之前的内容，以及各章节）
    lines = body.split('\n')
    
    # 找到第一个##的位置
    first_h2_idx = -1
    for i, line in enumerate(lines):
        if re.match(r'^##\s+', line):
            first_h2_idx = i
            break
    
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
    # 从第一个##开始，直到参考文件或Changelog之前
    content_start = first_h2_idx if first_h2_idx >= 0 else 0
    content_lines = []
    skip_sections = ['参考文件', 'Changelog', '变更日志', '知识关联']
    
    i = content_start
    while i < len(lines):
        line = lines[i]
        # 检查是否是需要跳过的二级标题
        h2_match = re.match(r'^##\s+(.+)$', line)
        if h2_match:
            section_title = h2_match.group(1).strip()
            should_skip = False
            for skip in skip_sections:
                if skip in section_title:
                    should_skip = True
                    break
            if should_skip:
                # 跳过整个章节，直到下一个##
                i += 1
                while i < len(lines) and not re.match(r'^##\s+', lines[i]):
                    i += 1
                continue
        
        # 清理空行（连续多个空行只保留一个）
        if line.strip() == '':
            if content_lines and content_lines[-1].strip() == '':
                i += 1
                continue
        content_lines.append(line)
        i += 1
    
    # 清理开头和结尾的空行
    while content_lines and content_lines[0].strip() == '':
        content_lines.pop(0)
    while content_lines and content_lines[-1].strip() == '':
        content_lines.pop()
    
    new_content.extend(content_lines)
    new_content.append('')
    
    # 6. 参考文件
    new_content.append('## 参考文件')
    new_content.append('')
    if original_links:
        for link_text, link_url in original_links[:3]:
            new_content.append(f'- [{link_text}]({link_url})')
    elif urls:
        for i, url in enumerate(urls[:5]):
            new_content.append(f'- [来源{i+1}]({url})')
    else:
        new_content.append('- 公开技术资料与官方文档')
    new_content.append('')
    
    # 7. Changelog
    new_content.append(build_changelog())
    
    return '\n'.join(new_content), {
        'dup_h1_removed': dup_h1_count,
        'summary_length': len(summary),
        'keyword_count': len(keywords),
        'title': title,
    }

def process_file(filepath):
    """处理单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content, stats = rebuild_document(content, filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, stats
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("深度重构系统与运维目录下的markdown文档")
    print("=" * 70)
    
    md_files = sorted(TARGET_DIR.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'index.md']
    
    print(f"发现 {len(md_files)} 个markdown文件（已排除index.md）")
    print()
    
    # 先运行一次前置检查
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
            print(f"   ✅ 完成 | 概要{result['summary_length']}字 | 关键词{result['keyword_count']}个 | 删除重复H1:{result['dup_h1_removed']}")
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
    print(f"   平均概要长度: {avg_summary_len:.1f} 字")
    print(f"   平均关键词数: {avg_keyword_cnt:.1f} 个")
    print()
    
    return 0 if fail_count == 0 else 1

if __name__ == '__main__':
    exit(main())
