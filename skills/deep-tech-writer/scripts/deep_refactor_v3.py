#!/usr/bin/env python3
"""
深度重构markdown文件 v3 - 简洁可靠版

核心功能：
1. 保留YAML frontmatter
2. 清理模板化垃圾章节
3. 提取"内容"章节中的有效内容（支持显式三级标题和隐式emoji标题）
4. 重写概要和关键词
5. 标准化格式
"""

import re
import os
import sys
import json
import shutil
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


EMOJI_CHARS = '📑💡📋🌐🔍🆕📚📎🔗📖⚠️🔮💼🛠️🌍📈🚩🔧📌📊📉🕶️🤖📱🥇🥈🥉✅❌👉⏱️🎯📌🔑💡⭐🏆🔥💪🚀💻📱🔬🎓'


def remove_emoji(text):
    """移除文本中的emoji"""
    for c in EMOJI_CHARS:
        text = text.replace(c, '')
    return text.strip()


def clean_title(title):
    """清理标题"""
    title = remove_emoji(title)
    title = title.replace('**', '').strip()
    title = title.strip(' -—·:：')
    return title.strip()


# 模板化垃圾章节列表
TEMPLATE_SECTIONS = [
    '快速导读', '核心要点', '相关素材', '相关文章', '知识关联',
    '案例补充', '实践指南', '行业影响', '延伸阅读', '相关资源',
    '背景与上下文', '深度解读', '最新进展', '2025-2026 最新进展',
    '挑战与风险', '趋势与展望', '企业案例与应用实践', '案例启示',
    '参考来源', '内容评级', '关键词标签', '相关知识点',
    'newwiki 主题知识库', 'newwiki2 知识卡片', 'knowledge 专题目录',
    '内部知识库引用', '外部资料引用', '阅读建议', '关键数据',
    '标杆案例', '创新案例', '落地实践建议', '避坑提醒',
    '企业案例', '案例',
]


def is_template_section(title):
    """判断是否为模板化垃圾章节"""
    title_clean = clean_title(title).lower()
    for t in TEMPLATE_SECTIONS:
        if t.lower() in title_clean:
            return True
    return False


def split_h2_sections(body):
    """按二级标题拆分内容，返回 [(标题, 内容), ...]"""
    lines = body.split('\n')
    sections = []
    current_title = None
    current_lines = []
    
    for line in lines:
        # 检测二级标题
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
    """找到'内容'章节"""
    for title, content in sections:
        clean = clean_title(title)
        if clean == '内容' or clean == '正文':
            return content
    return None


def extract_implicit_sections(content_text):
    """
    从内容文本中提取隐式章节（emoji + 标题格式）。
    返回 [(标题, 内容), ...]
    """
    lines = content_text.split('\n')
    sections = []
    current_title = None
    current_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # 检测显式三级标题
        if stripped.startswith('### '):
            if current_title is not None and current_lines:
                sections.append((current_title, '\n'.join(current_lines).strip()))
            title = clean_title(stripped[4:])
            current_title = title
            current_lines = []
            continue
        
        # 检测隐式标题：emoji + 加粗标题 或 emoji + 短标题
        is_title = False
        title_text = ""
        
        # 模式1: emoji + **标题**
        m = re.match(r'^[' + re.escape(EMOJI_CHARS) + r']\s*\*\*(.+?)\*\*\s*$', stripped)
        if m:
            is_title = True
            title_text = clean_title(m.group(1))
        
        # 模式2: emoji + 短标题（<25字，非句子结尾）
        if not is_title:
            m = re.match(r'^[' + re.escape(EMOJI_CHARS) + r']\s+(.+)$', stripped)
            if m:
                candidate = m.group(1).strip()
                candidate = candidate.replace('**', '').strip()
                if len(candidate) <= 25 and not candidate.endswith(('。', '，', '：', '；', '、', '.')):
                    # 确保不是列表项（不以-开头）
                    if not candidate.startswith('- ') and not candidate.startswith('* '):
                        is_title = True
                        title_text = clean_title(candidate)
        
        if is_title and title_text:
            if current_title is not None and current_lines:
                sections.append((current_title, '\n'.join(current_lines).strip()))
            current_title = title_text
            current_lines = []
            continue
        
        # 普通内容行
        if current_title is not None:
            current_lines.append(line)
    
    if current_title is not None and current_lines:
        sections.append((current_title, '\n'.join(current_lines).strip()))
    
    return sections


def clean_content(content):
    """清理内容中的模板垃圾"""
    lines = content.split('\n')
    cleaned = []
    
    skip_phrases = [
        '[← 返回分类索引]',
        '本文由Wiki系统自动生成',
        '*本文由Wiki系统自动生成*',
        '原文链接：',
        '原文：',
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
        cleaned.append(line)
    
    return '\n'.join(cleaned).strip()


def extract_dates(fm):
    """从frontmatter提取日期"""
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


def generate_summary_keywords(title, sections):
    """生成概要和关键词"""
    # 合并所有内容
    full_text = '\n'.join([content for _, content in sections])
    
    # === 关键词 ===
    keywords = []
    
    # 从标题提取
    title_clean = clean_title(title)
    # 按分隔符拆分
    parts = re.split(r'[：，、\s丨｜|]+', title_clean)
    stop_words = [
        '的', '与', '和', '及', '全', '解析', '分析', '指南', '深度', '全景',
        '完整', '攻略', '方案', '研究', '技术', '市场', '行业', '应用',
        '发展', '趋势', '创新', '企业', '产品', '数据', '影响', '现状',
        '挑战', '机遇', '问题', '解决方案', '全面', '最新', '记录',
        '一个', '一种', '不同', '相关', '多个', '各种',
    ]
    
    for part in parts:
        part = part.strip()
        if len(part) >= 2 and part not in stop_words:
            if not re.match(r'^\d+$', part):  # 排除纯数字
                keywords.append(part)
    
    # 去重
    seen = set()
    unique_kw = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_kw.append(kw)
    keywords = unique_kw[:5]
    
    # 补充专业术语
    if len(keywords) < 3:
        tech_terms = [
            'AI', '人工智能', '大模型', 'BERT', 'Transformer', '深度学习',
            '机器学习', '芯片', '半导体', '存储', '内存', 'DRAM', 'DDR5',
            '云服务', '云计算', '数据中心', '服务器', 'GPU', 'CPU',
            '开源', 'VR', 'AR', '智能眼镜',
            '数字人', '具身智能', '机器人', '物联网',
            '网络安全', '加密', '密码学',
            'Ansible', 'DevOps', 'Python', 'Java',
        ]
        for term in tech_terms:
            if term in full_text and term not in keywords:
                keywords.append(term)
                if len(keywords) >= 5:
                    break
    
    keywords = keywords[:5]
    
    # === 概要 ===
    summary = ""
    
    # 找第一段有意义的文本
    first_content = sections[0][1] if sections else full_text
    content_lines = first_content.split('\n')
    
    first_meaningful = ""
    for line in content_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('>'):
            continue
        if stripped.startswith('---'):
            continue
        if stripped.startswith('- ') or stripped.startswith('* '):
            continue
        if len(stripped) < 15:
            continue
        first_meaningful = stripped
        break
    
    if first_meaningful:
        # 清理markdown标记
        s = re.sub(r'\*\*(.+?)\*\*', r'\1', first_meaningful)
        s = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', s)
        s = remove_emoji(s).strip()
        
        # 截断到句号或100字
        if len(s) > 100:
            period_pos = s.find('。')
            if period_pos > 0 and period_pos <= 95:
                summary = s[:period_pos + 1]
            else:
                summary = s[:97] + '...'
        else:
            summary = s
    else:
        summary = f'本文围绕{clean_title(title)}展开分析，探讨相关核心内容与关键要点。'
        if len(summary) > 100:
            summary = summary[:97] + '...'
    
    if len(summary) > 100:
        summary = summary[:97] + '...'
    
    return summary, keywords


def generate_toc(titles):
    """生成目录"""
    lines = ['## 📑 目录', '']
    for t in titles:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', t)
        lines.append(f'- [{t}](#{anchor})')
    lines.append('')
    return '\n'.join(lines)


def generate_references(links):
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


def generate_changelog(fm):
    """生成Changelog"""
    created, updated = extract_dates(fm)
    return f"""## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| {created} | v1.0 | 初始版本，原文基础内容 |
| {updated} | v2.0 | 深度重构：清理模板垃圾、优化结构、提升内容质量 |

"""


def extract_links(body):
    """提取参考链接"""
    links = []
    # 原文链接
    m = re.search(r'原文[：:]\s*\[(.+?)\]\((https?://\S+)\)', body)
    if m:
        links.append((m.group(1), m.group(2)))
    # 其他链接
    for name, url in re.findall(r'\[(.+?)\]\((https?://\S+)\)', body):
        if not any(u == url for _, u in links):
            links.append((name, url))
    return links


def refactor_file(filepath):
    """重构单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    orig_lines = len(text.split('\n'))
    
    # 1. 提取frontmatter
    fm, body = extract_frontmatter(text)
    
    # 2. 提取标题
    title_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if title_match:
        title = clean_title(title_match.group(1))
    else:
        title = clean_title(Path(filepath).stem)
    
    # 3. 拆分二级章节
    h2_sections = split_h2_sections(body)
    
    # 4. 找到"内容"章节并提取子章节
    content_text = find_content_section(h2_sections)
    sections = []
    
    if content_text:
        # 从内容章节提取隐式子章节
        implicit = extract_implicit_sections(content_text)
        if implicit:
            for sec_title, sec_content in implicit:
                sec_content = clean_content(sec_content)
                if sec_content:
                    sections.append((sec_title, sec_content))
        else:
            # 没有子章节，作为整体内容
            content_clean = clean_content(content_text)
            if content_clean:
                sections.append(('核心内容', content_clean))
    else:
        # 没有"内容"章节，过滤模板章节，保留其他
        for sec_title, sec_content in h2_sections:
            if is_template_section(sec_title):
                continue
            sec_title_clean = clean_title(sec_title)
            sec_content_clean = clean_content(sec_content)
            if sec_content_clean:
                sections.append((sec_title_clean, sec_content_clean))
    
    # 5. 去重
    seen = set()
    unique_sections = []
    for sec_title, sec_content in sections:
        if sec_title not in seen and sec_content.strip():
            seen.add(sec_title)
            unique_sections.append((sec_title, sec_content))
    sections = unique_sections
    
    # 6. 提取链接
    links = extract_links(body)
    
    # 7. 生成概要和关键词
    summary, keywords = generate_summary_keywords(title, sections)
    
    # 8. 构建新文档
    result = '---\n'
    if fm:
        result += fm + '\n'
    result += '---\n\n'
    
    result += f'# {title}\n'
    result += f'> **概要**: {summary}\n'
    result += f'> **关键词**: {" · ".join(keywords)}\n\n'
    
    # 目录
    toc_titles = [s[0] for s in sections] + ['参考文件', 'Changelog']
    result += generate_toc(toc_titles)
    
    # 正文
    for sec_title, sec_content in sections:
        result += f'## {sec_title}\n\n'
        result += sec_content + '\n\n'
    
    # 参考文件
    result += generate_references(links)
    
    # Changelog
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
        print('用法: python3 deep_refactor_v3.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    # 从备份恢复
    backup_dir = os.path.join(target_dir, '_backup_original')
    if os.path.exists(backup_dir):
        print('🔄 从备份恢复原始文件...')
        for f in Path(backup_dir).glob('*.md'):
            shutil.copy2(str(f), target_dir)
        print('✅ 原始文件已恢复')
        print()
    
    # 获取文件列表
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
    
    # 统计
    total_orig = sum(r['original_lines'] for r in results if r['success'])
    total_new = sum(r['new_lines'] for r in results if r['success'])
    total_secs = sum(r['sections_count'] for r in results if r['success'])
    
    print()
    print('=' * 70)
    print('📊 重构完成统计 (v3)')
    print('=' * 70)
    print(f'  总文件数: {len(md_files)}')
    print(f'  ✅ 成功: {success} 个')
    print(f'  ❌ 失败: {fail} 个')
    print(f'  总行数: {total_orig} → {total_new} (减少 {total_orig - total_new} 行)')
    print(f'  平均章节: {total_secs / max(success, 1):.1f} 个/篇')
    print('=' * 70)
    
    report_path = os.path.join(target_dir, '_refactor_report_v3.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\n📋 报告: {report_path}')


if __name__ == '__main__':
    main()
