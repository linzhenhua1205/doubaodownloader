#!/usr/bin/env python3
"""
深度重构markdown文件 v7 - 最终质量优化版

修复v6问题：
1. 概要中标题重复问题（去掉前缀的标题重复）
2. 优化列表型概要，使其更自然流畅
3. 确保所有概要都是真正有信息量的一句话
"""

import re
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime


def extract_frontmatter(text):
    if text.startswith('---'):
        end = text.find('---', 3)
        if end != -1:
            fm = text[3:end].strip()
            body = text[end+3:].strip()
            return fm, body
    return "", text


def is_emoji_char(c):
    code = ord(c)
    ranges = [
        (0x1F300, 0x1FAFF),
        (0x2600, 0x27BF),
        (0x1F600, 0x1F64F),
        (0x1F680, 0x1F6FF),
        (0x1F900, 0x1F9FF),
        (0x1F1E0, 0x1F1FF),
    ]
    for start, end in ranges:
        if start <= code <= end:
            return True
    single_chars = [
        0x2757, 0x2753, 0x2714, 0x2716, 0x2728, 0x274C, 0x274E,
        0x2755, 0x2757, 0x27A1, 0x27B0, 0x2600, 0x26A0, 0x2601,
        0x21AA, 0x21A9, 0x23EB, 0x23EC, 0x23F0, 0x23F3,
    ]
    if code in single_chars:
        return True
    return False


def starts_with_emoji(s):
    if not s:
        return False, 0
    i = 0
    while i < len(s) and s[i].isspace():
        i += 1
    if i >= len(s):
        return False, 0
    if is_emoji_char(s[i]):
        emoji_end = i + 1
        if emoji_end < len(s) and ord(s[emoji_end]) == 0xFE0F:
            emoji_end += 1
        return True, emoji_end
    return False, 0


def remove_emoji(text):
    result = []
    i = 0
    while i < len(text):
        c = text[i]
        if is_emoji_char(c):
            i += 1
            if i < len(text) and ord(text[i]) == 0xFE0F:
                i += 1
            continue
        result.append(c)
        i += 1
    return ''.join(result).strip()


def clean_title(title):
    title = remove_emoji(title)
    title = title.replace('**', '').strip()
    title = title.strip(' -—·:：')
    return title.strip()


TEMPLATE_SECTIONS = [
    '快速导读', '核心要点', '相关素材', '相关文章', '知识关联',
    '案例补充', '实践指南', '行业影响', '延伸阅读', '相关资源',
    '背景与上下文', '深度解读', '最新进展', '2025-2026 最新进展',
    '挑战与风险', '趋势与展望', '企业案例与应用实践', '案例启示',
    '参考来源', '内容评级', '关键词标签', '相关知识点',
    'newwiki 主题知识库', 'newwiki2 知识卡片', 'knowledge 专题目录',
    '内部知识库引用', '外部资料引用', '阅读建议', '关键数据',
    '标杆案例', '创新案例', '落地实践建议', '避坑提醒',
    '企业案例', '案例', '目录', '📑 目录', '返回分类索引',
]


def is_template_section(title):
    title_clean = clean_title(title).lower()
    for t in TEMPLATE_SECTIONS:
        if t.lower() in title_clean:
            return True
    return False


def split_h2_sections(body):
    lines = body.split('\n')
    sections = []
    current_title = None
    current_lines = []
    for line in lines:
        if line.startswith('## '):
            if current_title is not None:
                sections.append((current_title, '\n'.join(current_lines)))
            current_title = line[3:].strip()
            current_lines = []
        else:
            if current_title is not None:
                current_lines.append(line)
    if current_title is not None:
        sections.append((current_title, '\n'.join(current_lines)))
    return sections


def find_content_section(sections):
    for title, content in sections:
        clean = clean_title(title)
        if clean == '内容' or clean == '正文':
            return content
    return None


def extract_implicit_sections(content_text):
    lines = content_text.split('\n')
    sections = []
    current_title = None
    current_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('### ') and not stripped.startswith('#### '):
            if current_title is not None and current_lines:
                sections.append((current_title, '\n'.join(current_lines).strip()))
            title = clean_title(stripped[4:])
            current_title = title
            current_lines = []
            continue
        if stripped.startswith('####'):
            i = 0
            while i < len(stripped) and stripped[i] == '#':
                i += 1
            title_text = clean_title(stripped[i:].strip())
            if current_title is not None:
                current_lines.append(f'### {title_text}')
            continue
        is_title = False
        title_text = ""
        has_emoji, emoji_end = starts_with_emoji(stripped)
        if has_emoji:
            after_emoji = stripped[emoji_end:].strip()
            m = re.match(r'^\*\*(.+?)\*\*\s*$', after_emoji)
            if m:
                is_title = True
                title_text = clean_title(m.group(1))
            if not is_title:
                candidate = after_emoji.replace('**', '').strip()
                if (len(candidate) <= 30 and 
                    not candidate.endswith(('。', '，', '：', '；', '、', '.')) and
                    not candidate.startswith('- ') and 
                    not candidate.startswith('* ')):
                    is_title = True
                    title_text = clean_title(candidate)
        if is_title and title_text:
            if current_title is not None and current_lines:
                sections.append((current_title, '\n'.join(current_lines).strip()))
            current_title = title_text
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)
    if current_title is not None and current_lines:
        sections.append((current_title, '\n'.join(current_lines).strip()))
    return sections


def clean_content(content):
    lines = content.split('\n')
    cleaned = []
    skip_phrases = [
        '[← 返回分类索引]',
        '本文由Wiki系统自动生成',
        '*本文由Wiki系统自动生成*',
    ]
    for line in lines:
        stripped = line.strip()
        skip = False
        for phrase in skip_phrases:
            if phrase in stripped:
                skip = True
                break
        if skip:
            continue
        if stripped == '---' or stripped == '----':
            continue
        cleaned.append(line)
    return '\n'.join(cleaned).strip()


def extract_dates(fm):
    created = ''
    updated = ''
    for line in fm.split('\n'):
        line = line.strip().strip("'\"")
        if line.startswith('created_at:'):
            val = line.split(':', 1)[1].strip().strip("'\"")
            m = re.match(r'(\d{4}-\d{2}-\d{2})', val)
            if m:
                created = m.group(1)
        elif line.startswith('updated_at:'):
            val = line.split(':', 1)[1].strip().strip("'\"")
            m = re.match(r'(\d{4}-\d{2}-\d{2})', val)
            if m:
                updated = m.group(1)
    if not created:
        created = '2025'
    if not updated:
        updated = datetime.now().strftime('%Y-%m-%d')
    return created, updated


def clean_list_item_text(item):
    """清理列表项文本，提取有意义的内容"""
    item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
    item = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', item)
    item = remove_emoji(item).strip()
    # 去掉开头的标签如 "时间：" "核心驱动：" 等
    item = re.sub(r'^[^：:]{1,8}[：:]\s*', '', item)
    return item.strip()


def generate_summary_from_lists(title, sections):
    """从列表型内容中生成概要（优化版，去掉标题重复）"""
    title_clean = clean_title(title)
    
    # 收集所有列表项
    all_items = []
    first_section_items = []
    
    for i, (sec_title, sec_content) in enumerate(sections):
        lines = sec_content.split('\n')
        for line in lines:
            stripped = line.strip()
            m = re.match(r'^[-*+]\s*(.+)$', stripped)
            if m:
                item = m.group(1).strip()
                item_clean = clean_list_item_text(item)
                if item_clean and len(item_clean) > 8:
                    all_items.append(item_clean)
                    if i == 0:
                        first_section_items.append(item_clean)
    
    # 策略1：找一个信息量最大的列表项作为开头
    best_item = None
    for item in all_items:
        if 20 <= len(item) <= 80:
            if best_item is None or len(item) > len(best_item):
                best_item = item
    
    if best_item:
        summary = best_item
        if not summary.endswith('。'):
            summary += '。'
        if len(summary) <= 100:
            return summary
    
    # 策略2：组合前3个要点
    if first_section_items:
        items = first_section_items[:3]
        short_items = []
        for it in items:
            if len(it) > 25:
                short_items.append(it[:25] + '...')
            else:
                short_items.append(it)
        combined = '、'.join(short_items)
        summary = f'涵盖{combined}等核心内容。'
        if len(summary) <= 100:
            return summary
    
    # 策略3：基于章节标题组合（不重复标题）
    sec_titles = [s[0] for s in sections[:3] if s[0] not in ['核心内容', '正文']]
    if sec_titles:
        secs_text = '、'.join(sec_titles)
        summary = f'从{secs_text}等维度展开分析。'
        if len(summary) <= 100:
            return summary
    
    # 策略4：通用描述（不重复标题）
    summary = '系统梳理核心内容与关键信息，涵盖主要观点与数据支撑。'
    return summary


def generate_summary_keywords(title, sections):
    full_text = '\n'.join([content for _, content in sections])
    
    # === 关键词 ===
    keywords = []
    title_clean = clean_title(title)
    parts = re.split(r'[：，、\s丨｜|]+', title_clean)
    
    stop_words = set([
        '的', '与', '和', '及', '全', '解析', '分析', '指南', '深度', '全景',
        '完整', '攻略', '方案', '研究', '技术', '市场', '行业', '应用',
        '发展', '趋势', '创新', '企业', '产品', '数据', '影响', '现状',
        '挑战', '机遇', '问题', '解决方案', '全面', '最新', '记录',
        '一个', '一种', '不同', '相关', '多个', '各种', '时代', '里程碑',
        '核心', '原理', '机制', '结构', '对比', '主流', '模型',
        '年', '款', '款', '月', '日', '第', '期',
    ])
    
    for part in parts:
        part = part.strip()
        if (len(part) >= 2 and len(part) <= 12 and 
            part.lower() not in stop_words and 
            not re.match(r'^\d+$', part) and
            part != title_clean):
            keywords.append(part)
    
    seen = set()
    unique_kw = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_kw.append(kw)
    keywords = unique_kw
    
    if len(keywords) < 5:
        tech_terms = [
            'AI', '人工智能', '大模型', 'BERT', 'Transformer', '深度学习',
            '机器学习', '芯片', '半导体', '存储', '内存', 'DRAM', 'DDR5',
            '云服务', '云计算', '数据中心', '服务器', 'GPU', 'CPU',
            '开源', 'VR', 'AR', '智能眼镜', 'MR',
            '数字人', '具身智能', '机器人', '物联网',
            '网络安全', '加密', '密码学', 'Ansible', 'DevOps',
            'Python', 'Java', 'NLP', 'MLM', 'NAS', 'AutoML',
            'RISC-V', 'ARM', 'x86', 'PCIe', 'NVMe', 'CXL',
            'RFID', '可穿戴', '智慧城市', '双11', 'Cloudflare',
            'Apache', '许可证', '开源协议', 'Argon2',
            'AST2700', 'AST2600', 'BMC',
            'AMD', 'MI400', 'MI450',
            'iMac', '扩展显示器',
            'Random Forest', '随机森林', 'RSS',
            'Bagualu', '一体机', '软件栈',
            '数学家', '数学猜想',
            '开源项目', '数字人',
            '服饰', '智能穿戴',
            '晶圆代工', '英特尔',
            '跨平台', '技术选型',
            '学术会议', '论文',
            'PDF', 'Markdown',
            '网页抓取', '爬虫',
            '就业市场', '职业路径',
            '资情留言板', '36氪',
            '网站结构',
        ]
        for term in tech_terms:
            if len(keywords) >= 5:
                break
            if re.search(re.escape(term), full_text, re.IGNORECASE) and term not in keywords:
                keywords.append(term)
    
    keywords = keywords[:5]
    
    if len(keywords) < 3:
        fallback = ['技术', '行业', '市场']
        for fb in fallback:
            if fb not in keywords:
                keywords.append(fb)
                if len(keywords) >= 3:
                    break
    
    keywords = keywords[:5]
    
    # === 概要 ===
    summary = ""
    
    # 先找完整段落
    all_paragraphs = []
    for _, content in sections:
        paras = content.split('\n\n')
        for p in paras:
            p = p.strip()
            if not p:
                continue
            if p.startswith('#') or p.startswith('>'):
                continue
            p_clean = re.sub(r'\*\*(.+?)\*\*', r'\1', p)
            p_clean = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', p_clean)
            p_clean = remove_emoji(p_clean).strip()
            if (len(p_clean) >= 30 and 
                not p_clean.startswith(('- ', '* ', '1.', '2.', '3.', '4.', '5.')) and
                not p_clean.startswith('|') and
                not p_clean.startswith('+ ') and
                not p_clean.startswith('```') and
                not p_clean.startswith('    ')):
                all_paragraphs.append(p_clean)
    
    if all_paragraphs:
        first_para = all_paragraphs[0]
        period_idx = first_para.find('。')
        if period_idx > 10 and period_idx <= 95:
            summary = first_para[:period_idx + 1]
        elif len(first_para) <= 100:
            summary = first_para
        else:
            search_end = min(98, len(first_para))
            last_period = first_para[:search_end].rfind('。')
            if last_period > 10:
                summary = first_para[:last_period + 1]
            else:
                summary = first_para[:97] + '...'
    else:
        # 没有完整段落，用列表型内容生成
        summary = generate_summary_from_lists(title, sections)
    
    if len(summary) > 100:
        period_idx = summary[:98].rfind('。')
        if period_idx > 10:
            summary = summary[:period_idx + 1]
        else:
            summary = summary[:97] + '...'
    
    if len(summary) < 15:
        summary = '系统梳理核心内容与关键信息，涵盖主要观点与数据支撑。'
    
    return summary, keywords


def generate_toc(titles):
    lines = ['## 📑 目录', '']
    for t in titles:
        t_clean = clean_title(t)
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', t_clean)
        lines.append(f'- [{t_clean}](#{anchor})')
    lines.append('')
    return '\n'.join(lines)


def generate_references(links):
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


def generate_changelog(fm):
    created, updated = extract_dates(fm)
    return f"""## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| {created} | v1.0 | 初始版本，原文基础内容 |
| {updated} | v2.0 | 深度重构：清理模板垃圾、优化结构、提升内容质量 |

"""


def extract_links(body):
    links = []
    patterns = [
        r'原文[：:]\s*\[(.+?)\]\((https?://\S+)\)',
        r'原文链接[：:]\s*(https?://\S+)',
        r'原文链接[：:]\s*\[(.+?)\]\((https?://\S+)\)',
    ]
    for pat in patterns:
        m = re.search(pat, body)
        if m:
            if len(m.groups()) == 2:
                name, url = m.group(1), m.group(2)
            else:
                name, url = '原文链接', m.group(1)
            if not any(u == url for _, u in links):
                links.append((name, url))
            break
    
    for name, url in re.findall(r'\[(.+?)\]\((https?://\S+)\)', body):
        if not any(u == url for _, u in links):
            links.append((name, url))
    
    return links


def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    orig_lines = len(text.split('\n'))
    
    fm, body = extract_frontmatter(text)
    
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if title_match:
        title = clean_title(title_match.group(1))
    else:
        title = clean_title(Path(filepath).stem)
    
    h2_sections = split_h2_sections(body)
    
    content_text = find_content_section(h2_sections)
    sections = []
    
    if content_text:
        implicit = extract_implicit_sections(content_text)
        if implicit:
            for sec_title, sec_content in implicit:
                sec_title_clean = clean_title(sec_title)
                sec_content_clean = clean_content(sec_content)
                if sec_content_clean:
                    sections.append((sec_title_clean, sec_content_clean))
        else:
            content_clean = clean_content(content_text)
            content_lines = content_clean.split('\n')
            filtered = []
            for l in content_lines:
                s = l.strip()
                if s.startswith('原文') and ('http' in s or '链接' in s):
                    continue
                if re.match(r'^##\s+', s):
                    continue
                filtered.append(l)
            content_clean = '\n'.join(filtered).strip()
            if content_clean:
                sections.append(('核心内容', content_clean))
    else:
        for sec_title, sec_content in h2_sections:
            if is_template_section(sec_title):
                continue
            sec_title_clean = clean_title(sec_title)
            sec_content_clean = clean_content(sec_content)
            if sec_content_clean:
                sections.append((sec_title_clean, sec_content_clean))
    
    seen = set()
    unique_sections = []
    for sec_title, sec_content in sections:
        sec_title_clean = clean_title(sec_title)
        if sec_title_clean not in seen and sec_content.strip():
            seen.add(sec_title_clean)
            unique_sections.append((sec_title_clean, sec_content))
    sections = unique_sections
    
    links = extract_links(body)
    
    summary, keywords = generate_summary_keywords(title, sections)
    
    result = '---\n'
    if fm:
        result += fm + '\n'
    result += '---\n\n'
    
    result += f'# {title}\n'
    result += f'> **概要**: {summary}\n'
    result += f'> **关键词**: {" · ".join(keywords)}\n\n'
    
    toc_titles = [s[0] for s in sections] + ['参考文件', 'Changelog']
    result += generate_toc(toc_titles)
    
    for sec_title, sec_content in sections:
        sec_title_clean = clean_title(sec_title)
        result += f'## {sec_title_clean}\n\n'
        result += sec_content + '\n\n'
    
    result += generate_references(links)
    
    result += generate_changelog(fm)
    
    new_lines = len(result.split('\n'))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)
    
    return {
        'filename': Path(filepath).name,
        'original_lines': orig_lines,
        'new_lines': new_lines,
        'sections_count': len(sections),
        'summary': summary,
        'keywords': keywords,
        'success': True
    }


def main():
    if len(sys.argv) < 2:
        print('用法: python3 deep_refactor_v7.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    backup_dir = os.path.join(target_dir, '_backup_original')
    if os.path.exists(backup_dir):
        print('🔄 从备份恢复原始文件...')
        for f in Path(backup_dir).glob('*.md'):
            shutil.copy2(str(f), target_dir)
        print('✅ 原始文件已恢复')
        print()
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    print(f'🔍 发现 {len(md_files)} 个markdown文件')
    print()
    
    results = []
    success = 0
    fail = 0
    
    for filepath in md_files:
        try:
            print(f'处理: {filepath.name}...', end=' ')
            r = refactor_file(str(filepath))
            results.append(r)
            success += 1
            print(f'✅ ({r["original_lines"]}→{r["new_lines"]}行, {r["sections_count"]}章节)')
        except Exception as e:
            print(f'❌ {e}')
            import traceback
            traceback.print_exc()
            fail += 1
            results.append({'filename': filepath.name, 'success': False, 'error': str(e)})
    
    total_orig = sum(r['original_lines'] for r in results if r['success'])
    total_new = sum(r['new_lines'] for r in results if r['success'])
    total_secs = sum(r['sections_count'] for r in results if r['success'])
    
    print()
    print('=' * 70)
    print('📊 重构完成统计 (v7)')
    print('=' * 70)
    print(f'  总文件数: {len(md_files)}')
    print(f'  ✅ 成功: {success} 个')
    print(f'  ❌ 失败: {fail} 个')
    print(f'  总行数: {total_orig} → {total_new} (减少 {total_orig - total_new} 行)')
    print(f'  平均章节: {total_secs / max(success, 1):.1f} 个/篇')
    print('=' * 70)
    
    report_path = os.path.join(target_dir, '_refactor_report_v7.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\n📋 报告: {report_path}')


if __name__ == '__main__':
    main()
