#!/usr/bin/env python3
"""
快速修复脚本 - 修复概要换行和目录问题

修复：
1. 概要中包含换行和列表的问题（确保是纯文本一句话）
2. 目录中重复条目的问题
3. 确保概要≤100字且是完整的一句话
"""

import re
import os
import sys
from pathlib import Path


def fix_summary(body):
    """修复概要：提取第一个真正的正文段落，确保是一句话"""
    
    # 找到"背景与意义"、"执行摘要"、"概述"等章节
    priority_sections = [
        r'##\s*(?:🌐\s*)?(?:背景与意义|背景介绍|文章背景|研究背景)',
        r'##\s*(?:📋\s*)?(?:执行摘要|内容摘要|核心摘要|报告摘要)',
        r'##\s*(?:📖\s*)?(?:概述|简介|前言|引言)',
        r'##\s*(?:📊\s*)?(?:市场规模|行业现状|发展现状|市场格局)',
    ]
    
    best_paragraph = ""
    
    for pattern in priority_sections:
        match = re.search(pattern + r'[^\n]*\n(.+?)(?=\n## |\Z)', body, re.DOTALL)
        if match:
            section_text = match.group(1)
            # 提取段落
            paragraphs = []
            current_para = []
            
            for line in section_text.split('\n'):
                stripped = line.strip()
                if stripped and not stripped.startswith(('-', '*', '•', '|', '###', '>')):
                    current_para.append(stripped)
                elif current_para:
                    para = ' '.join(current_para)
                    if len(para) > 50:
                        paragraphs.append(para)
                    current_para = []
            
            if current_para:
                para = ' '.join(current_para)
                if len(para) > 50:
                    paragraphs.append(para)
            
            if paragraphs:
                # 选择最长且最有意义的段落
                best_paragraph = max(paragraphs, key=len)
                break
    
    # 如果没找到，尝试找第一个正文段落
    if not best_paragraph:
        lines = body.split('\n')
        skip_until_heading = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('#'):
                skip_until_heading = False
                clean = stripped.lstrip('#').strip().lower()
                if any(kw in clean for kw in ['快速导读', '核心要点', '目录', '关键词', '概要']):
                    skip_until_heading = True
                continue
            
            if skip_until_heading:
                continue
            
            if not stripped or stripped.startswith(('---', '|', '- ', '* ', '• ', '> ')):
                continue
            
            if len(stripped) > 60:
                best_paragraph = stripped
                break
    
    if not best_paragraph:
        best_paragraph = "本文深入分析了相关主题，提供了全面的行业洞察和技术解读。"
    
    # 清理概要
    summary = best_paragraph
    
    # 移除加粗标记
    summary = re.sub(r'\*\*(.+?)\*\*', r'\1', summary)
    
    # 只保留第一个句子（或前100字）
    sentences = re.split(r'([。！？!?；;])', summary)
    first_sentence = ""
    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sent = sentences[i]
            if i + 1 < len(sentences):
                sent += sentences[i+1]
            sent = sent.strip()
            if sent:
                if len(first_sentence) + len(sent) <= 95:
                    first_sentence += sent
                else:
                    break
        if first_sentence and len(first_sentence) >= 30:
            break
    
    if not first_sentence:
        first_sentence = summary[:97] + "..."
    
    # 确保以句号结尾
    first_sentence = first_sentence.strip()
    if not first_sentence.endswith(('。', '！', '？', '!', '?', '…')):
        if len(first_sentence) < 98:
            first_sentence += '。'
        else:
            first_sentence = first_sentence[:96] + '...'
    
    # 确保不超过100字
    if len(first_sentence) > 100:
        first_sentence = first_sentence[:97] + '...'
    
    return first_sentence


def fix_toc(body):
    """修复目录：确保只包含核心二级标题"""
    lines = body.split('\n')
    h2_headings = []
    
    non_core = {'目录', '参考文件', '参考资料', '参考来源', '参考文献',
                'Changelog', '变更日志', '变更记录', '版本记录',
                '知识关联', '延伸阅读', '相关文章', '相关素材',
                '快速导读', '核心要点', '内容', '执行摘要', '关键词标签'}
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            # 移除emoji
            title_clean = re.sub(r'[\U0001F300-\U0001FAFF\U00002700-\U000027BF\ufe0f]', '', title).strip()
            title_lower = title_clean.lower()
            
            is_non_core = False
            for kw in non_core:
                if kw in title_lower:
                    is_non_core = True
                    break
            
            if not is_non_core and title_clean and len(title_clean) > 1:
                h2_headings.append(title_clean)
    
    # 去重
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
    """处理单个文件"""
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 分离frontmatter和body
    fm = ""
    body = text
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[:end_pos+4]
            body = text[end_pos+4:].strip()
    
    # 修复概要
    new_summary = fix_summary(body)
    
    # 修复目录
    new_toc = fix_toc(body)
    
    # 替换旧的概要和关键词
    # 找到标题后的概要和关键词部分
    lines = body.split('\n')
    
    # 找到标题行
    title_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('# ') and not line.strip().startswith('## '):
            title_idx = i
            break
    
    if title_idx == -1:
        print(f"  ⚠️  未找到标题: {filename}")
        return False
    
    # 找到概要行和关键词行
    summary_idx = -1
    keywords_idx = -1
    toc_start_idx = -1
    toc_end_idx = -1
    
    for i in range(title_idx + 1, min(title_idx + 20, len(lines))):
        stripped = lines[i].strip()
        if stripped.startswith('> **概要**:'):
            summary_idx = i
        elif stripped.startswith('> **关键词**:'):
            keywords_idx = i
        elif stripped == '## 📑 目录' or stripped == '## 目录':
            toc_start_idx = i
            # 找到目录结束位置
            for j in range(i + 1, min(i + 30, len(lines))):
                if lines[j].strip().startswith('## ') and not lines[j].strip().startswith('### '):
                    toc_end_idx = j - 1
                    break
            if toc_end_idx == -1:
                toc_end_idx = min(i + 20, len(lines) - 1)
    
    # 提取关键词
    keywords = "大模型 · AI Agent · AIGC"
    if keywords_idx != -1:
        kw_line = lines[keywords_idx]
        match = re.search(r'> \*\*关键词\*\*:\s*(.+)', kw_line)
        if match:
            keywords = match.group(1).strip()
    
    # 重建body（从标题开始）
    new_body_lines = []
    
    # 添加标题
    new_body_lines.append(lines[title_idx])
    new_body_lines.append("")
    
    # 添加概要和关键词
    new_body_lines.append(f"> **概要**: {new_summary}")
    new_body_lines.append(f"> **关键词**: {keywords}")
    new_body_lines.append("")
    
    # 添加目录
    if new_toc:
        new_body_lines.append(new_toc)
    
    # 找到正文开始位置（目录结束后或关键词后第一个正文章节）
    content_start = title_idx + 1
    
    # 跳过旧的概要、关键词、目录
    if toc_end_idx != -1:
        content_start = toc_end_idx + 1
    elif keywords_idx != -1:
        content_start = keywords_idx + 1
    
    # 继续跳过空行
    while content_start < len(lines) and not lines[content_start].strip():
        content_start += 1
    
    # 添加剩余内容
    for i in range(content_start, len(lines)):
        new_body_lines.append(lines[i])
    
    new_body = '\n'.join(new_body_lines)
    
    # 组合最终文本
    final_text = fm + '\n' + new_body if fm else new_body
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"  ✅ {filename[:50]}...")
    print(f"     概要: {new_summary[:60]}...")
    return True


def main():
    if len(sys.argv) < 2:
        print('用法: python3 fix_summary_toc.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件')
    print()
    
    success_count = 0
    fail_count = 0
    
    for filepath in md_files:
        try:
            if process_file(str(filepath)):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  ❌ {Path(filepath).name}: {e}")
            fail_count += 1
    
    print()
    print('=' * 60)
    print(f'📊 修复完成: {success_count} 成功, {fail_count} 失败')
    print('=' * 60)


if __name__ == '__main__':
    main()
