#!/usr/bin/env python3
"""
深度重构markdown文件 v2 - 优化版本

修复v1问题：
1. 更好地识别"内容"章节中的隐式标题（emoji+加粗）
2. 更智能的概要和关键词生成
3. 彻底清除章节标题中的emoji前缀
4. 修复日期格式
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


def remove_emoji(text):
    """去除文本中的所有emoji和特殊符号"""
    emoji_pattern = re.compile(
        "["
        u"\U0001F300-\U0001F6FF"
        u"\U0001F600-\U0001F64F"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U00002600-\U000027BF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"
        u"\u3030"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()


def clean_title(title):
    """清理标题：移除emoji、markdown标记等"""
    title = remove_emoji(title)
    title = title.replace('**', '').strip()
    title = title.strip(' -—·:：')
    return title.strip()


def is_template_section(title):
    """判断是否为模板化垃圾章节"""
    template_titles = [
        '快速导读', '核心要点', '相关素材', '相关文章', '知识关联',
        '案例补充', '实践指南', '行业影响', '延伸阅读', '相关资源',
        '背景与上下文', '深度解读', '最新进展', '2025-2026 最新进展',
        '挑战与风险', '趋势与展望', '企业案例与应用实践', '案例启示',
        '参考来源', '内容评级', '关键词标签', '相关知识点',
        'newwiki 主题知识库', 'newwiki2 知识卡片', 'knowledge 专题目录',
        '内部知识库引用', '外部资料引用', '阅读建议', '关键数据',
        '标杆案例', '创新案例', '落地实践建议', '避坑提醒',
    ]
    title_clean = clean_title(title).lower()
    for t in template_titles:
        if t.lower() in title_clean:
            return True
    return False


def extract_sections_from_content(content_text):
    """
    从内容章节中提取子章节。
    支持两种格式：
    1. 显式三级标题 (### 标题)
    2. 隐式标题 (emoji + **加粗标题** 或 emoji + 标题)
    """
    lines = content_text.split('\n')
    sections = []
    current_title = None
    current_content = []
    
    # 跳过 "内容" 二级标题行和空行
    start_idx = 0
    for i, line in enumerate(lines):
        if re.match(r'^##\s+', line):
            start_idx = i + 1
            break
    
    # 隐式标题模式：emoji + 可选加粗 + 标题
    implicit_title_pattern = re.compile(
        r'^[\s]*'  # 前导空白
        r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF📑💡📋🌐🔍🆕📚📎🔗📖⚠️🔮💼🛠️🌍📈🚩🔧📌]'  # emoji
        r'[\s*]*'  # 空白或星号
        r'(.+?)'  # 标题内容
        r'[\s*]*$'  # 结尾空白或星号
    )
    
    for line in lines[start_idx:]:
        stripped = line.strip()
        
        if not stripped:
            if current_title:
                current_content.append(line)
            continue
        
        # 检测显式三级标题
        h3_match = re.match(r'^###\s+(.+)$', line)
        if h3_match:
            if current_title:
                sections.append((current_title, '\n'.join(current_content).strip()))
            title = clean_title(h3_match.group(1))
            current_title = title
            current_content = []
            continue
        
        # 检测四级及以下标题，降级为三级
        h4_match = re.match(r'^####+\s+(.+)$', line)
        if h4_match and current_title:
            title = clean_title(h4_match.group(1))
            current_content.append(f'### {title}')
            continue
        
        # 检测隐式标题（emoji开头 + 加粗/短标题）
        # 条件：以emoji开头，整行较短，或有加粗标记
        is_implicit_title = False
        title_text = ""
        
        # 模式1: emoji + **标题**
        bold_implicit = re.match(
            r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF📑💡📋🌐🔍🆕📚📎🔗📖⚠️🔮💼🛠️🌍📈🚩🔧📌]\s*\*\*(.+?)\*\*$',
            stripped
        )
        if bold_implicit:
            is_implicit_title = True
            title_text = clean_title(bold_implicit.group(1))
        
        # 模式2: emoji + 短标题（<20字，无句号结尾）
        if not is_implicit_title:
            short_implicit = re.match(
                r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF📑💡📋🌐🔍🆕📚📎🔗📖⚠️🔮💼🛠️🌍📈🚩🔧📌]\s+(.+)$',
                stripped
            )
            if short_implicit:
                candidate = short_implicit.group(1).strip()
                candidate = candidate.replace('**', '').strip()
                if len(candidate) <= 25 and not candidate.endswith(('。', '，', '：', '；', '、')):
                    is_implicit_title = True
                    title_text = clean_title(candidate)
        
        if is_implicit_title and title_text:
            if current_title:
                sections.append((current_title, '\n'.join(current_content).strip()))
            current_title = title_text
            current_content = []
            continue
        
        if current_title:
            current_content.append(line)
    
    if current_title:
        sections.append((current_title, '\n'.join(current_content).strip()))
    
    return sections


def extract_all_h2_sections(body):
    """提取所有二级章节"""
    lines = body.split('\n')
    sections = []
    current_title = None
    current_content = []
    
    for line in lines:
        h2_match = re.match(r'^##\s+(.+)$', line)
        if h2_match:
            if current_title:
                sections.append((current_title, '\n'.join(current_content)))
            title = h2_match.group(1).strip()
            current_title = title
            current_content = [line]
            continue
        
        if current_title:
            current_content.append(line)
    
    if current_title:
        sections.append((current_title, '\n'.join(current_content)))
    
    return sections


def find_content_section(sections):
    """找到'内容'章节"""
    for title, content in sections:
        clean = clean_title(title)
        if clean == '内容' or clean == '正文':
            return content
    return None


def clean_body_text(text):
    """清理正文中的模板垃圾内容"""
    lines = text.split('\n')
    cleaned = []
    
    skip_patterns = [
        '[← 返回分类索引]',
        '本文由Wiki系统自动生成',
        '*本文由Wiki系统自动生成*',
    ]
    
    for line in lines:
        stripped = line.strip()
        skip = False
        for pattern in skip_patterns:
            if pattern in stripped:
                skip = True
                break
        if skip:
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


def generate_toc(section_titles):
    """生成目录"""
    toc_lines = ['## 📑 目录', '']
    for title in section_titles:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', title)
        toc_lines.append(f'- [{title}](#{anchor})')
    toc_lines.append('')
    return '\n'.join(toc_lines)


def generate_references_section(links):
    """生成参考文件章节"""
    lines = ['## 参考文件', '']
    if links:
        lines.append('### 外部资料引用')
        lines.append('')
        for name, url in links[:10]:
            name = clean_title(name)
            lines.append(f'- [{name}]({url})')
    else:
        lines.append('- 原文链接（见文首）')
    lines.append('')
    return '\n'.join(lines)


def extract_dates_from_fm(fm):
    """从frontmatter提取创建和更新日期"""
    created_at = ""
    updated_at = ""
    
    for line in fm.split('\n'):
        line = line.strip().strip("'\"")
        if line.startswith('created_at:'):
            val = line.split(':', 1)[1].strip().strip("'\"")
            # 提取日期部分
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', val)
            if date_match:
                created_at = date_match.group(1)
        elif line.startswith('updated_at:'):
            val = line.split(':', 1)[1].strip().strip("'\"")
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', val)
            if date_match:
                updated_at = date_match.group(1)
    
    if not created_at:
        created_at = '2025'
    if not updated_at:
        updated_at = datetime.now().strftime('%Y-%m-%d')
    
    return created_at, updated_at


def generate_changelog(fm):
    """生成Changelog三列表格"""
    created_at, updated_at = extract_dates_from_fm(fm)
    
    changelog = f"""## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| {created_at} | v1.0 | 初始版本，原文基础内容 |
| {updated_at} | v2.0 | 深度重构：清理模板垃圾、优化结构、提升内容质量 |

"""
    return changelog


def generate_summary_and_keywords(title, sections):
    """
    智能生成概要和关键词
    
    概要：从第一段正文内容中提取，生成一句话总结（≤100字）
    关键词：从标题和内容中提取3-5个核心关键词
    """
    full_text = '\n'.join([content for _, content in sections])
    
    # === 提取关键词 ===
    keywords = []
    
    # 从标题提取
    title_clean = clean_title(title)
    # 按常见分隔符拆分
    title_parts = re.split(r'[：，、\s丨｜|]+', title_clean)
    stop_words = [
        '的', '与', '和', '及', '全', '解析', '分析', '指南', '深度', '全景',
        '完整', '攻略', '方案', '研究', '技术', '市场', '行业', '应用',
        '发展', '趋势', '创新', '企业', '产品', '数据', '影响', '现状',
        '挑战', '机遇', '问题', '解决方案', '全面', '最新', '记录',
    ]
    
    for part in title_parts:
        part = part.strip()
        if len(part) >= 2 and len(part) <= 12 and part not in stop_words:
            # 过滤掉纯英文缩写以外的过短词汇
            if not (len(part) <= 2 and not re.search(r'[A-Z]', part)):
                keywords.append(part)
    
    # 去重并限制数量
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    
    keywords = unique_keywords[:5]
    
    # 如果关键词不够，从内容中补充
    if len(keywords) < 3:
        # 从第一段内容提取高频名词
        first_section_content = sections[0][1] if sections else full_text
        # 简单提取：找出现次数多的专业术语
        tech_terms = [
            'AI', '人工智能', '大模型', 'BERT', 'Transformer', '深度学习',
            '机器学习', '芯片', '半导体', '存储', '内存', 'DRAM', 'DDR5',
            '云服务', '云计算', '数据中心', '服务器', 'GPU', 'CPU',
            '开源', '区块链', '元宇宙', 'VR', 'AR', '智能眼镜',
            '数字人', '具身智能', '机器人', '自动驾驶', '物联网',
            '5G', '6G', 'WiFi', '网络安全', '加密', '密码学',
            'Python', 'Java', 'JavaScript', 'Ansible', 'DevOps',
        ]
        for term in tech_terms:
            if term in full_text and term not in keywords:
                keywords.append(term)
                if len(keywords) >= 5:
                    break
    
    keywords = keywords[:5]
    
    # === 生成概要 ===
    summary = ""
    
    # 从第一段有意义的文本提取
    first_content = sections[0][1] if sections else full_text
    content_lines = first_content.split('\n')
    
    first_meaningful = ""
    for line in content_lines:
        stripped = line.strip()
        # 跳过标题、链接行、空行
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('>'):
            continue
        if stripped.startswith('原文') and 'http' in stripped:
            continue
        if stripped.startswith('---'):
            continue
        if len(stripped) < 10:
            continue
        # 找第一个完整句子
        first_meaningful = stripped
        break
    
    if first_meaningful:
        # 清理markdown标记
        summary = re.sub(r'\*\*(.+?)\*\*', r'\1', first_meaningful)
        summary = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', summary)
        summary = remove_emoji(summary).strip()
        
        # 截取到第一个句号或100字
        if len(summary) > 100:
            # 尝试在句号处截断
            period_idx = summary.find('。')
            if period_idx > 0 and period_idx <= 100:
                summary = summary[:period_idx + 1]
            else:
                summary = summary[:97] + '...'
    else:
        summary = f'本文围绕{title}展开深入分析，探讨相关技术要点与行业影响。'
        if len(summary) > 100:
            summary = summary[:97] + '...'
    
    # 确保概要不超过100字
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
    
    # 2. 提取标题（从第一个H1）
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if title_match:
        title = clean_title(title_match.group(1))
    else:
        title = filename.replace('.md', '')
        title = clean_title(title)
    
    # 3. 提取所有二级章节
    all_sections = extract_all_h2_sections(body)
    
    # 4. 找到"内容"章节，提取内部子章节
    content_text = find_content_section(all_sections)
    new_sections = []
    
    if content_text:
        # 从内容章节提取子章节（支持显式和隐式标题）
        subsections = extract_sections_from_content(content_text)
        if subsections:
            for sub_title, sub_content in subsections:
                # 清理子内容
                sub_content = clean_body_text(sub_content)
                if sub_content:
                    new_sections.append((sub_title, sub_content))
        else:
            # 没有子章节，直接使用内容文本
            content_clean = clean_body_text(content_text)
            # 移除 "## 内容" 开头
            content_lines = content_clean.split('\n')
            filtered = []
            for l in content_lines:
                if re.match(r'^##\s+', l):
                    continue
                filtered.append(l)
            content_clean = '\n'.join(filtered).strip()
            # 清理"原文：[xxx]"行
            content_lines = content_clean.split('\n')
            filtered = []
            for l in content_lines:
                stripped = l.strip()
                if stripped.startswith('原文') and 'http' in stripped:
                    continue
                filtered.append(l)
            content_clean = '\n'.join(filtered).strip()
            if content_clean:
                new_sections.append(('核心内容', content_clean))
    else:
        # 没有"内容"章节，过滤掉模板章节，保留有效内容
        for sec_title, sec_content in all_sections:
            clean_sec_title = clean_title(sec_title)
            if is_template_section(clean_sec_title):
                continue
            
            # 移除章节标题行，清理内容
            content_lines = sec_content.split('\n')[1:]  # 跳过标题行
            content_clean = clean_body_text('\n'.join(content_lines)).strip()
            
            if content_clean:
                new_sections.append((clean_sec_title, content_clean))
    
    # 5. 去重：移除重复的章节
    seen_titles = set()
    unique_sections = []
    for sec_title, sec_content in new_sections:
        if sec_title not in seen_titles and sec_content.strip():
            seen_titles.add(sec_title)
            unique_sections.append((sec_title, sec_content))
    
    new_sections = unique_sections
    
    # 6. 提取参考链接
    ref_links = extract_reference_links(body)
    
    # 7. 生成概要和关键词
    summary, keywords = generate_summary_and_keywords(title, new_sections)
    
    # 8. 构建新的文档
    result = '---\n'
    result += fm + '\n' if fm else ''
    result += '---\n\n'
    
    # 标题 + 概要 + 关键词
    result += f'# {title}\n'
    result += f'> **概要**: {summary}\n'
    result += f'> **关键词**: {" · ".join(keywords)}\n\n'
    
    # 目录（核心二级标题 + 参考文件 + Changelog）
    toc_titles = [s[0] for s in new_sections] + ['参考文件', 'Changelog']
    result += generate_toc(toc_titles)
    
    # 正文章节
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
        print('用法: python3 deep_refactor_v2.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    # 先从备份恢复原始文件（因为v1已经改过了）
    backup_dir = os.path.join(target_dir, '_backup_original')
    if os.path.exists(backup_dir):
        print('🔄 从备份恢复原始文件...')
        import shutil
        for f in Path(backup_dir).glob('*.md'):
            shutil.copy2(str(f), target_dir)
        print('✅ 原始文件已恢复')
        print()
    
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
            import traceback
            traceback.print_exc()
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
    print('📊 重构完成统计 (v2)')
    print('=' * 70)
    print(f'  总文件数: {len(md_files)}')
    print(f'  ✅ 成功: {success_count} 个')
    print(f'  ❌ 失败: {fail_count} 个')
    print(f'  总行数: {total_original} → {total_new} (减少 {total_original - total_new} 行)')
    print(f'  平均章节数: {total_sections / max(success_count, 1):.1f} 个/篇')
    print('=' * 70)
    
    # 保存详细结果
    report_path = os.path.join(target_dir, '_refactor_report_v2.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\n📋 详细报告已保存至: {report_path}')


if __name__ == '__main__':
    main()
