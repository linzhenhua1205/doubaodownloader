#!/usr/bin/env python3
"""
最终修复版 - 高质量概要生成

从正文中提取真正的段落，确保概要是完整的一句话，≤100字
"""

import re
import os
import sys
from pathlib import Path


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[:end_pos+4]
            body = text[end_pos+4:].strip()
            return fm, body
    return "", text


def get_title(body):
    for line in body.split('\n'):
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            return stripped[2:].strip()
    return ""


def generate_high_quality_summary(body, title):
    """生成高质量的一句话概要"""
    
    lines = body.split('\n')
    
    # 收集所有有意义的段落
    good_paragraphs = []
    
    # 策略：遍历所有二级章节，找到第一个有实质内容的段落
    current_section = ""
    current_para_lines = []
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        # 遇到二级标题，保存之前的段落
        if stripped.startswith('## ') and not stripped.startswith('### '):
            if current_para_lines:
                para = ' '.join(current_para_lines).strip()
                if is_good_paragraph(para):
                    good_paragraphs.append((current_section, para))
                current_para_lines = []
            current_section = stripped[3:].strip()
            continue
        
        # 跳过各种不需要的内容
        if not stripped:
            if current_para_lines:
                para = ' '.join(current_para_lines).strip()
                if is_good_paragraph(para):
                    good_paragraphs.append((current_section, para))
                current_para_lines = []
            continue
        
        # 跳过列表项
        if stripped.startswith(('- ', '* ', '• ', '1. ', '2. ', '3. ', '4. ', '5. ')):
            continue
        
        # 跳过表格
        if stripped.startswith('|'):
            continue
        
        # 跳过引用块的元信息
        if re.match(r'^>\s*[\U0001F300-\U0001FAFF📅🏷️🔗📝⭐]', stripped):
            continue
        
        # 跳过"原文："链接
        if re.match(r'^原文[：:]\s*\[', stripped):
            continue
        
        # 跳过加粗的小标题（如 "**市场规模**："）
        # 但保留后面的内容
        
        current_para_lines.append(stripped)
    
    # 处理最后一个段落
    if current_para_lines:
        para = ' '.join(current_para_lines).strip()
        if is_good_paragraph(para):
            good_paragraphs.append((current_section, para))
    
    # 选择最好的段落
    best_para = ""
    
    # 优先选择这些章节中的段落
    priority_sections = [
        '背景与意义', '背景介绍', '研究背景', '项目背景',
        '执行摘要', '内容摘要', '核心摘要', '报告摘要',
        '概述', '简介', '前言', '引言',
        '市场规模', '行业现状', '发展现状', '市场格局',
        '产业规模与增长', '市场规模与增长',
    ]
    
    for section_name, para in good_paragraphs:
        section_clean = re.sub(r'[\U0001F300-\U0001FAFF\ufe0f]', '', section_name).strip()
        for prio in priority_sections:
            if prio in section_clean:
                best_para = para
                break
        if best_para:
            break
    
    # 如果没找到，用第一个好段落
    if not best_para and good_paragraphs:
        best_para = good_paragraphs[0][1]
    
    # 如果还没找到，用标题生成一个
    if not best_para:
        best_para = f"本文围绕{title}主题展开深入分析，涵盖技术原理、应用实践与行业趋势等核心内容。"
    
    # 清理和格式化
    summary = clean_summary(best_para)
    
    return summary


def is_good_paragraph(text):
    """判断是否是好的正文段落"""
    if not text or len(text) < 40:
        return False
    
    # 包含原文链接
    if text.startswith('原文') and 'http' in text:
        return False
    
    # 纯列表项
    if re.match(r'^[-*\d\.]', text) and len(text) < 60:
        return False
    
    # 太短
    if len(text) < 40:
        return False
    
    return True


def clean_summary(text):
    """清理概要文本，确保是完整的一句话，≤100字"""
    if not text:
        return text
    
    # 移除markdown加粗
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # 移除markdown链接，保留文本
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 找到第一个完整的句子（句号、感叹号、问号结尾）
    sentences = re.split(r'([。！？!?；;])', text)
    first_sentence = ""
    
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        sent = sentences[i].strip()
        if i + 1 < len(sentences):
            punct = sentences[i + 1]
        else:
            punct = '。'
        
        if not sent:
            continue
        
        if len(first_sentence) + len(sent) + len(punct) <= 95:
            first_sentence += sent + punct
        else:
            # 截断
            remaining = 95 - len(first_sentence)
            if remaining > 10:
                first_sentence += sent[:remaining] + '...'
            break
        
        # 已经有一个完整的句子了，看看要不要再加
        if first_sentence.endswith(('。', '！', '？', '!', '?')) and len(first_sentence) >= 30:
            break
    
    if not first_sentence:
        first_sentence = text[:97] + '...'
    
    # 确保以正确的标点结尾
    first_sentence = first_sentence.strip()
    if not first_sentence.endswith(('。', '！', '？', '!', '?', '…', '...')):
        if len(first_sentence) < 98:
            first_sentence += '。'
        else:
            first_sentence = first_sentence[:96] + '...'
    
    # 最终长度检查
    if len(first_sentence) > 100:
        first_sentence = first_sentence[:97] + '...'
    
    return first_sentence


def fix_toc(body):
    """修复目录"""
    lines = body.split('\n')
    h2_headings = []
    
    non_core = {'目录', '参考文件', '参考资料', '参考来源', '参考文献',
                'Changelog', '变更日志', '变更记录', '版本记录',
                '知识关联', '延伸阅读', '相关文章', '相关素材',
                '快速导读', '核心要点', '内容', '执行摘要', '关键词标签',
                '内容评级', 'import素材融合'}
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            title_clean = re.sub(r'[\U0001F300-\U0001FAFF\U00002700-\U000027BF\ufe0f]', '', title).strip()
            title_lower = title_clean.lower()
            
            is_non_core = False
            for kw in non_core:
                if kw.lower() in title_lower:
                    is_non_core = True
                    break
            
            if not is_non_core and title_clean and len(title_clean) > 1:
                h2_headings.append(title_clean)
    
    seen = set()
    unique_headings = []
    for h in h2_headings:
        if h not in seen:
            seen.add(h)
            unique_headings.append(h)
    
    if len(unique_headings) < 3:
        return ""
    
    toc_lines = ["## 📑 目录", ""]
    for h in unique_headings:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', h)
        toc_lines.append(f"- [{h}](#{anchor})")
    
    toc_lines.append("")
    return '\n'.join(toc_lines)


def process_file(filepath):
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    
    title = get_title(body)
    if not title:
        title = filename.replace('.md', '')
    
    # 生成新的概要
    new_summary = generate_high_quality_summary(body, title)
    
    # 生成新的目录
    new_toc = fix_toc(body)
    
    # 提取现有关键词
    keywords = "大模型 · AI Agent · AIGC"
    kw_match = re.search(r'> \*\*关键词\*\*:\s*(.+)', body)
    if kw_match:
        keywords = kw_match.group(1).strip()
    
    # 重建body
    lines = body.split('\n')
    
    # 找到标题位置
    title_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('# ') and not line.strip().startswith('## '):
            title_idx = i
            break
    
    if title_idx == -1:
        return False
    
    # 找到正文开始位置（跳过概要、关键词、目录）
    content_start = title_idx + 1
    
    # 跳过旧的概要、关键词、目录
    in_toc = False
    for i in range(title_idx + 1, min(title_idx + 50, len(lines))):
        stripped = lines[i].strip()
        if stripped.startswith('> **概要**:'):
            content_start = i + 1
            continue
        if stripped.startswith('> **关键词**:'):
            content_start = i + 1
            continue
        if stripped == '## 📑 目录' or stripped == '## 目录':
            in_toc = True
            content_start = i + 1
            continue
        if in_toc:
            if stripped.startswith('## ') and not stripped.startswith('### '):
                in_toc = False
                content_start = i
                break
            content_start = i + 1
            continue
        if stripped and not stripped.startswith('>') and not in_toc:
            # 找到第一个非空、非引用、非目录的行
            content_start = i
            break
    
    # 构建新的body
    new_body_lines = []
    new_body_lines.append(lines[title_idx])
    new_body_lines.append("")
    new_body_lines.append(f"> **概要**: {new_summary}")
    new_body_lines.append(f"> **关键词**: {keywords}")
    new_body_lines.append("")
    
    if new_toc:
        new_body_lines.append(new_toc)
    
    # 添加正文
    for i in range(content_start, len(lines)):
        new_body_lines.append(lines[i])
    
    new_body = '\n'.join(new_body_lines)
    
    final_text = fm + '\n' + new_body if fm else new_body
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"  ✅ {filename[:45]}...")
    print(f"     {new_summary[:70]}...")
    return True


def main():
    if len(sys.argv) < 2:
        print('用法: python3 final_fix_summary.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件')
    print()
    
    success = 0
    fail = 0
    
    for filepath in md_files:
        try:
            if process_file(str(filepath)):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ❌ {Path(filepath).name}: {e}")
            import traceback
            traceback.print_exc()
            fail += 1
    
    print()
    print('=' * 60)
    print(f'📊 完成: {success} 成功, {fail} 失败')
    print('=' * 60)


if __name__ == '__main__':
    main()
