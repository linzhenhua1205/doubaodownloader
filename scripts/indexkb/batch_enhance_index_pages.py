import os
import re
import sys
from pathlib import Path

BASE_DIR = r"h:\github\cowkb\discover\newwiki2"

INDEX_DIRS = [
    "AI-模型架构",
    "AI-训练微调",
    "AI-Agent",
    "ai-models",
]

TEMPLATE_MARKERS = [
    "AI时代ExponTech存储革命的基础知识和核心定义。",
    "AI时代ExponTech存储革命的底层机制和工作原理。",
    "AI时代ExponTech存储革命的应用方法和实践技巧。",
    "基础概念：理解",
    "核心原理：掌握",
    "实践应用：了解",
    "发展趋势：关注",
    "相关联系：建立与其他知识领域的关联认知",
    "技术持续演进，性能和效率不断提升",
    "AI 技术融合加速，智能化水平提高",
    "开源生态持续繁荣，工具链日益成熟",
    "从传统场景向更多新兴领域渗透",
    "与云计算、大数据、AI 等技术结合更紧密",
    "系统设计与架构决策",
    "技术选型与方案评估",
    "性能优化与问题排查",
    "知识体系构建",
    "技术面试准备",
    "持续学习与进阶",
    "相关领域经典书籍与教材",
    "技术白皮书与官方文档",
    "优质技术博客与专栏文章",
    "相关领域经典教材与权威著作",
    "技术社区高质量文章与讨论",
    "官方技术文档与白皮书",
    "行业研究报告与分析",
    "前沿论文与学术研究",
]

def parse_frontmatter(content):
    if not content.startswith('---'):
        return {}, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    fm_text = parts[1].strip()
    body = parts[2].lstrip()
    fm = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                val = val[1:-1].split(',')
                val = [v.strip() for v in val]
            fm[key] = val
    return fm, body

def dump_frontmatter(fm):
    lines = ['---']
    for key, val in fm.items():
        if isinstance(val, list):
            val_str = ', '.join(val)
            lines.append(f'{key}: [{val_str}]')
        else:
            lines.append(f'{key}: {val}')
    lines.append('---')
    return '\n'.join(lines) + '\n'

def is_index_page(body):
    index_markers = ['本卡片为知识索引页', '收录了相关主题的多条笔记摘要']
    return any(marker in body for marker in index_markers)

def has_templated_content(body):
    count = 0
    for marker in TEMPLATE_MARKERS:
        if marker in body:
            count += 1
    return count >= 3

def estimate_word_count(text):
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    en_words = len(re.findall(r'[a-zA-Z]+', text))
    return cn_chars + en_words

def count_notes(body):
    count = 0
    lines = body.split('\n')
    for line in lines:
        if re.match(r'^## \d+\.', line.strip()):
            count += 1
    return max(count, 1)

def clean_template_sections(body):
    lines = body.split('\n')
    result = []
    skip = False
    
    template_section_starts = [
        "## 卡片概述",
        "## 核心要点", 
        "## 内容详解",
        "## 2025-2026 年最新进展",
        "## 应用场景",
        "## 相关资源",
        "## 参考来源",
        "## 卡片概览",
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        is_template_start = False
        for sec in template_section_starts:
            if line.strip() == sec.strip():
                is_template_start = True
                break
        
        if is_template_start:
            skip = True
            i += 1
            continue
        
        if skip:
            if line.startswith('---') or (line.startswith('## ') and not any(
                line.strip() == sec.strip() for sec in template_section_starts
            )):
                skip = False
            else:
                i += 1
                continue
        
        if not skip:
            result.append(line)
        i += 1
    
    cleaned = '\n'.join(result)
    cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)
    return cleaned.strip()

def enhance_index_page(filepath, fm, body):
    title = fm.get('title', '未知主题')
    category = fm.get('category', '')
    
    note_count = count_notes(body)
    word_count = estimate_word_count(body)
    
    cleaned_body = clean_template_sections(body)
    
    intro = f"""---

## 卡片概述

> **本卡片为知识索引页**，收录了与「{title}」相关的多条笔记摘要。
>
> 📌 **定位说明**：索引页的核心价值是**知识导航与快速概览**——帮助读者快速了解相关主题有哪些笔记、大致讲了什么。点击每条笔记下方的源文件链接可查看完整内容。

| 属性 | 说明 |
|:-----|:-----|
| **主题分类** | {category} |
| **收录笔记** | {note_count} 条 |
| **内容形式** | 笔记摘要合集（索引页） |
| **适用场景** | 快速扫览、主题导航、灵感启发 |
| **建议阅读方式** | 先浏览标题找兴趣点，再点源文件看全文 |

---

"""
    
    final_body = intro + cleaned_body
    
    has_update_log = '## 更新日志' in final_body
    
    if not has_update_log:
        final_body += f"""

---

## 更新日志

- **2026-07-22**: B 级基础增强 — 优化索引页结构，清理模板化内容，完善导航信息。
"""
    
    if not final_body.strip().endswith('*'):
        final_body += f"""

---

*卡片质量等级：B级（知识索引页） | 更新日期：2026-07-22*
"""
    
    fm['quality_level'] = 'B级（知识索引页）'
    fm['word_count'] = f'约 {word_count} 字'
    fm['status'] = 'B级基础增强完成（知识索引页）'
    if 'card_count' not in fm:
        fm['card_count'] = str(note_count)
    
    new_content = dump_frontmatter(fm) + '\n' + final_body
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"索引页优化：{note_count}条笔记，{word_count}字"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm, body = parse_frontmatter(content)
    
    if is_index_page(body):
        return enhance_index_page(filepath, fm, body)
    
    if has_templated_content(body):
        return False, "有模板化内容但非索引页，需手动处理"
    
    return False, "无需处理"

def main():
    total_processed = 0
    total_templated = 0
    results = []
    
    for dirname in INDEX_DIRS:
        dirpath = os.path.join(BASE_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue
        
        for filename in sorted(os.listdir(dirpath)):
            if not filename.endswith('.md'):
                continue
            if filename == 'index.md':
                continue
            
            filepath = os.path.join(dirpath, filename)
            success, msg = process_file(filepath)
            
            rel_path = os.path.join(dirname, filename)
            if success:
                total_processed += 1
                results.append(f"✅ {rel_path}: {msg}")
            elif "模板化" in msg:
                total_templated += 1
                results.append(f"⚠️  {rel_path}: {msg}")
    
    print("\n" + "="*70)
    print("批量优化知识索引页")
    print("="*70)
    print(f"索引页优化成功: {total_processed} 个")
    print(f"有模板化需手动处理: {total_templated} 个")
    print("="*70)
    print("\n详细结果：")
    for r in results:
        print(r)

if __name__ == '__main__':
    main()
