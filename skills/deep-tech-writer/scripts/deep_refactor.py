#!/usr/bin/env python3
"""
深度重构markdown文件 - 清理重复内容、模板垃圾、重构结构

按照 deep-tech-writer 六步工作流进行深度重构：
1. 清理重复内容（重复H1、重复章节、模板化垃圾）
2. 重构内容结构
3. 标准化格式
"""

import re
import os
import sys
import json
from pathlib import Path
from datetime import datetime


def extract_frontmatter(text):
    """提取YAML frontmatter"""
    if text.startswith('---'):
        end = text.find('---', 3)
        if end != -1:
            fm = text[3:end].strip()
            body = text[end+3:].strip()
            return fm, body
    return "", text


def remove_emoji_prefix(title):
    """去除标题中的emoji前缀"""
    # 匹配emoji或特殊符号开头的标题
    pattern = r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF📑💡📋🌐🔍🆕📚📎🔗📖⚠️🔮💼🛠️🌍]\s*'
    return re.sub(pattern, '', title).strip()


def is_template_section(title):
    """判断是否为模板化垃圾章节"""
    template_titles = [
        '快速导读', '核心要点', '相关素材', '相关文章', '知识关联',
        '案例补充', '实践指南', '行业影响', '延伸阅读', '相关资源',
        '背景与上下文', '深度解读', '最新进展', '2025-2026 最新进展',
        '挑战与风险', '趋势与展望', '企业案例与应用实践', '案例启示',
        '参考来源', '内容评级', '关键词标签', '相关知识点',
        'newwiki 主题知识库', 'newwiki2 知识卡片', 'knowledge 专题目录',
        '内部知识库引用', '外部资料引用',
    ]
    title_clean = remove_emoji_prefix(title).lower()
    for t in template_titles:
        if t.lower() in title_clean:
            return True
    return False


def extract_content_sections(body):
    """提取正文内容，跳过模板章节"""
    lines = body.split('\n')
    sections = []
    current_section = None
    current_content = []
    
    for line in lines:
        # 检测二级标题
        h2_match = re.match(r'^##\s+(.+)$', line)
        if h2_match:
            if current_section:
                sections.append((current_section, '\n'.join(current_content)))
            title = h2_match.group(1).strip()
            current_section = title
            current_content = [line]
            continue
        
        # 检测三级及以下标题
        h3_match = re.match(r'^###+\s+(.+)$', line)
        if h3_match and current_section:
            current_content.append(line)
            continue
        
        if current_section:
            current_content.append(line)
    
    if current_section:
        sections.append((current_section, '\n'.join(current_content)))
    
    return sections


def find_content_section(sections):
    """找到'内容'章节并提取其内部的标题"""
    for title, content in sections:
        clean_title = remove_emoji_prefix(title)
        if clean_title == '内容':
            return content
    return None


def extract_subsections_from_content(content_text):
    """从内容章节中提取三级标题，提升为二级标题"""
    lines = content_text.split('\n')
    subsections = []
    current_title = None
    current_content = []
    
    # 跳过 "内容" 二级标题行
    start_idx = 0
    for i, line in enumerate(lines):
        if re.match(r'^##\s+', line):
            start_idx = i + 1
            break
    
    for line in lines[start_idx:]:
        # 检测三级标题
        h3_match = re.match(r'^###\s+(.+)$', line)
        if h3_match:
            if current_title:
                subsections.append((current_title, '\n'.join(current_content).strip()))
            title = h3_match.group(1).strip()
            title = remove_emoji_prefix(title)
            # 移除标题中的 ** 加粗标记
            title = title.replace('**', '').strip()
            current_title = title
            current_content = []
            continue
        
        # 检测四级及以下标题，降级为三级
        h4_match = re.match(r'^####+\s+(.+)$', line)
        if h4_match and current_title:
            title = h4_match.group(1).strip()
            title = remove_emoji_prefix(title)
            title = title.replace('**', '').strip()
            current_content.append(f'### {title}')
            continue
        
        if current_title:
            current_content.append(line)
    
    if current_title:
        subsections.append((current_title, '\n'.join(current_content).strip()))
    
    return subsections


def clean_content_text(text):
    """清理正文中的模板内容"""
    lines = text.split('\n')
    cleaned = []
    skip_until_next_heading = False
    
    for line in lines:
        stripped = line.strip()
        
        # 跳过返回分类索引
        if '[← 返回分类索引]' in stripped:
            continue
        
        # 跳过"本文由Wiki系统自动生成"
        if '本文由Wiki系统自动生成' in stripped:
            continue
        
        # 跳过分隔线后的模板内容
        if stripped == '---' and skip_until_next_heading:
            continue
        
        cleaned.append(line)
    
    return '\n'.join(cleaned)


def extract_reference_links(body):
    """提取正文中的参考链接"""
    links = []
    # 提取原文链接
    orig_match = re.search(r'原文[：:]\s*\[(.+?)\]\((https?://\S+)\)', body)
    if orig_match:
        links.append((orig_match.group(1), orig_match.group(2)))
    
    # 提取其他URL
    url_matches = re.findall(r'\[(.+?)\]\((https?://\S+)\)', body)
    for name, url in url_matches:
        if not any(l[1] == url for l in links):
            links.append((name, url))
    
    return links


def generate_toc(sections):
    """生成目录（只列核心二级标题）"""
    toc_lines = ['## 📑 目录', '']
    for title, _ in sections:
        clean_title = remove_emoji_prefix(title)
        # 生成锚点：移除特殊字符
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', clean_title)
        toc_lines.append(f'- [{clean_title}](#{anchor})')
    toc_lines.append('')
    return '\n'.join(toc_lines)


def generate_references_section(links):
    """生成参考文件章节"""
    if not links:
        return '## 参考文件\n\n- 原文链接（见文首）\n'
    
    lines = ['## 参考文件', '']
    lines.append('### 外部资料引用')
    lines.append('')
    for name, url in links[:10]:
        lines.append(f'- [{name}]({url})')
    lines.append('')
    return '\n'.join(lines)


def generate_changelog(fm):
    """生成Changelog三列表格"""
    # 从frontmatter提取日期
    created_at = ""
    updated_at = ""
    
    for line in fm.split('\n'):
        if line.startswith('created_at:'):
            created_at = line.split(':', 1)[1].strip()[:10]
        elif line.startswith('updated_at:'):
            updated_at = line.split(':', 1)[1].strip()[:10]
    
    if not created_at:
        created_at = '2025'
    if not updated_at:
        updated_at = datetime.now().strftime('%Y-%m-%d')
    
    changelog = f"""## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| {created_at} | v1.0 | 初始版本，原文基础内容 |
| {updated_at} | v2.0 | 深度重构：清理模板垃圾、优化结构、提升内容质量 |

"""
    return changelog


def generate_summary_and_keywords(title, body):
    """生成概要和关键词（基于内容提取）"""
    # 提取第一段有意义的内容
    lines = body.split('\n')
    first_paragraph = ""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('>') and not stripped.startswith('---'):
            if len(stripped) > 20:
                first_paragraph = stripped
                break
    
    # 从标题提取关键词
    keywords = []
    title_words = re.split(r'[：，、\s]+', title)
    for w in title_words:
        w = w.strip()
        if len(w) >= 2 and len(w) <= 10 and w not in ['的', '与', '和', '及', '全', '解析', '分析', '指南', '深度', '全景']:
            keywords.append(w)
    
    # 如果关键词不够，从内容中提取高频词
    if len(keywords) < 3:
        # 简单提取：找出现次数多的名词
        text = body[:2000]
        common_terms = ['技术', '市场', '产品', '应用', '发展', '趋势', '创新', '行业', '企业', '数据']
        for term in common_terms:
            if term in text and term not in keywords:
                keywords.append(term)
                if len(keywords) >= 5:
                    break
    
    keywords = keywords[:5]
    
    # 生成概要
    if first_paragraph:
        summary = first_paragraph
        if len(summary) > 100:
            summary = summary[:97] + '...'
    else:
        summary = f'本文深度解析{title}相关内容，提供全面的技术分析和行业洞察。'
        if len(summary) > 100:
            summary = summary[:97] + '...'
    
    return summary, keywords


def refactor_file(filepath):
    """深度重构单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    original_lines = len(text.split('\n'))
    filename = os.path.basename(filepath)
    
    # 1. 提取frontmatter
    fm, body = extract_frontmatter(text)
    
    # 2. 提取标题
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # 移除标题中的emoji
        title = remove_emoji_prefix(title)
    else:
        title = filename.replace('.md', '')
    
    # 3. 提取所有二级章节
    sections = extract_content_sections(body)
    
    # 4. 找到"内容"章节，提取其内部三级标题提升为二级
    content_text = find_content_section(sections)
    new_sections = []
    
    if content_text:
        # 从内容章节提取子章节
        subsections = extract_subsections_from_content(content_text)
        if subsections:
            # 有子章节，用提升后的子章节替代
            for sub_title, sub_content in subsections:
                new_sections.append((sub_title, sub_content))
        else:
            # 没有三级标题，保留内容但去除"内容"标题
            # 直接使用内容文本
            content_clean = clean_content_text(content_text)
            # 移除开头的 "## 内容" 行
            content_lines = content_clean.split('\n')
            content_lines = [l for l in content_lines if not re.match(r'^##\s+', l)]
            content_clean = '\n'.join(content_lines).strip()
            if content_clean:
                new_sections.append(('正文', content_clean))
    else:
        # 没有"内容"章节，过滤掉模板章节
        for sec_title, sec_content in sections:
            clean_title = remove_emoji_prefix(sec_title)
            if not is_template_section(clean_title):
                # 清理内容中的模板
                content_clean = clean_content_text(sec_content)
                # 移除章节标题行
                content_lines = content_clean.split('\n')
                content_lines = [l for l in content_lines[1:]]  # 跳过标题行
                content_clean = '\n'.join(content_lines).strip()
                if content_clean:
                    new_sections.append((clean_title, content_clean))
    
    # 5. 去重：移除重复的章节
    seen_titles = set()
    unique_sections = []
    for sec_title, sec_content in new_sections:
        if sec_title not in seen_titles:
            seen_titles.add(sec_title)
            unique_sections.append((sec_title, sec_content))
    
    new_sections = unique_sections
    
    # 6. 提取参考链接
    ref_links = extract_reference_links(body)
    
    # 7. 生成概要和关键词
    full_body_text = '\n'.join([c for _, c in new_sections])
    summary, keywords = generate_summary_and_keywords(title, full_body_text)
    
    # 8. 构建新的文档结构
    # YAML frontmatter
    result = '---\n'
    result += fm + '\n' if fm else ''
    result += '---\n\n'
    
    # 标题 + 概要 + 关键词
    result += f'# {title}\n'
    result += f'> **概要**: {summary}\n'
    result += f'> **关键词**: {" · ".join(keywords)}\n\n'
    
    # 目录
    # 加上参考文件和changelog
    toc_sections = new_sections + [('参考文件', ''), ('Changelog', '')]
    result += generate_toc(toc_sections)
    
    # 正文
    for sec_title, sec_content in new_sections:
        result += f'## {sec_title}\n\n'
        result += sec_content + '\n\n'
    
    # 参考文件
    result += generate_references_section(ref_links)
    
    # Changelog
    result += generate_changelog(fm)
    
    new_lines = len(result.split('\n'))
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)
    
    return {
        'filename': filename,
        'original_lines': original_lines,
        'new_lines': new_lines,
        'sections_count': len(new_sections),
        'summary': summary,
        'keywords': keywords,
        'success': True
    }


def main():
    if len(sys.argv) < 2:
        print('用法: python3 deep_refactor.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    # 获取所有md文件（跳过index.md）
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件（已跳过index.md）')
    print()
    
    results = []
    success_count = 0
    fail_count = 0
    
    for filepath in md_files:
        try:
            print(f'处理: {filepath.name}...', end=' ')
            result = refactor_file(str(filepath))
            results.append(result)
            success_count += 1
            print(f'✅ ({result["original_lines"]}行 → {result["new_lines"]}行, {result["sections_count"]}个章节)')
        except Exception as e:
            print(f'❌ 失败: {e}')
            fail_count += 1
            results.append({
                'filename': filepath.name,
                'success': False,
                'error': str(e)
            })
    
    # 统计
    total_original = sum(r['original_lines'] for r in results if r['success'])
    total_new = sum(r['new_lines'] for r in results if r['success'])
    total_sections = sum(r['sections_count'] for r in results if r['success'])
    
    print()
    print('=' * 70)
    print('📊 重构完成统计')
    print('=' * 70)
    print(f'  总文件数: {len(md_files)}')
    print(f'  ✅ 成功: {success_count} 个')
    print(f'  ❌ 失败: {fail_count} 个')
    print(f'  总行数: {total_original} → {total_new} (减少 {total_original - total_new} 行)')
    print(f'  平均章节数: {total_sections / max(success_count, 1):.1f} 个/篇')
    print('=' * 70)
    
    # 保存详细结果
    report_path = os.path.join(target_dir, '_refactor_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\n📋 详细报告已保存至: {report_path}')


if __name__ == '__main__':
    main()
