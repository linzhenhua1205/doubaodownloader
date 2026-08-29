import os
import re
import sys

BASE_DIR = r"h:\github\cowkb\discover\newwiki2"

INDEX_DIRS = [
    "AI-模型架构",
    "AI-训练微调",
    "AI-Agent",
    "ai-models",
]

TEMPLATE_MARKERS = [
    "是一个重要的知识主题。本卡片系统梳理了相关的核心概念、关键原理和实践应用，帮助读者快速建立认知框架。",
    "相关应用场景和实践案例",
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

def estimate_word_count(text):
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    en_words = len(re.findall(r'[a-zA-Z]{3,}', text))
    return cn_chars + en_words

def count_tables(text):
    lines = text.split('\n')
    count = 0
    for line in lines:
        if '|' in line and ('---' in line or ':---' in line):
            count += 1
    return count

def has_template_residue(body):
    count = 0
    for marker in TEMPLATE_MARKERS:
        if marker in body:
            count += 1
    return count >= 1

def clean_template_residue(body):
    lines = body.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if '## 卡片概述' in line or '卡片概述' == line.strip():
            j = i + 1
            while j < len(lines):
                if lines[j].startswith('---') or lines[j].startswith('## '):
                    break
                j += 1
            if j < len(lines) and lines[j].startswith('---'):
                j += 1
            i = j
            continue
        
        if '## 应用场景' in line or '## 典型应用场景' in line:
            j = i + 1
            all_placeholder = True
            while j < len(lines):
                if lines[j].startswith('---') or lines[j].startswith('## '):
                    break
                l = lines[j].strip()
                if l and not l.startswith('### ') and not l.startswith('- ') and '相关应用场景' not in l:
                    all_placeholder = False
                if '相关应用场景和实践案例' in l:
                    all_placeholder = True
                j += 1
            
            if all_placeholder:
                i = j
                if i < len(lines) and lines[i].startswith('---'):
                    i += 1
                continue
        
        if '## 原始笔记' in line:
            j = i
            while j < len(lines):
                if lines[j].startswith('## 更新日志'):
                    break
                j += 1
            if j < len(lines):
                i = j
                continue
        
        if '深度扩展：' in line and '大模型技术基础' in line:
            j = i
            while j < len(lines):
                if lines[j].startswith('## 2025-2026') or lines[j].startswith('---'):
                    break
                j += 1
            i = j
            continue
        
        result.append(line)
        i += 1
    
    cleaned = '\n'.join(result)
    cleaned = re.sub(r'\n{4,}', '\n\n\n', cleaned)
    return cleaned.strip()

def real_quality_level(body):
    words = estimate_word_count(body)
    tables = count_tables(body)
    h2 = len(re.findall(r'^## ', body, re.MULTILINE))
    
    if '本卡片为知识索引页' in body:
        return 'B级（知识索引页）' if words > 1000 else 'C级（知识索引页）'
    
    if words >= 2500 and tables >= 3 and h2 >= 6:
        return 'S级'
    elif words >= 1800 and tables >= 2 and h2 >= 5:
        return 'A级'
    elif words >= 1000 and h2 >= 4 and (tables >= 1 or '```' in body):
        return 'B级'
    elif words >= 500 and h2 >= 2:
        return 'C级'
    else:
        return 'D级'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm, body = parse_frontmatter(content)
    
    original_level = fm.get('quality_level', '未知')
    original_words = estimate_word_count(body)
    
    if not has_template_residue(body):
        return False, "无模板化残留"
    
    cleaned_body = clean_template_residue(body)
    new_words = estimate_word_count(cleaned_body)
    new_level = real_quality_level(cleaned_body)
    
    if new_words >= original_words * 0.9:
        return False, f"清理后内容变化不大（{original_words} -> {new_words}）"
    
    if '更新日志' in cleaned_body:
        pass
    else:
        cleaned_body += f"""

---

## 更新日志

- **2026-07-22**: B 级质量提升 — 清理模板化残留内容，修正质量评级。
"""
    
    if cleaned_body.strip().endswith('*'):
        cleaned_body = re.sub(r'\*卡片质量等级：[^*]+\*$', f'*卡片质量等级：{new_level} | 更新日期：2026-07-22*', cleaned_body.strip())
    else:
        cleaned_body += f"""

---

*卡片质量等级：{new_level} | 更新日期：2026-07-22*
"""
    
    fm['quality_level'] = new_level
    fm['word_count'] = f'约 {new_words} 字'
    fm['status'] = f'{new_level}质量提升完成'
    
    new_content = dump_frontmatter(fm) + '\n' + cleaned_body + '\n'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"{original_level} → {new_level}，字数 {original_words} → {new_words}"

def main():
    total_processed = 0
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
    
    print("\n" + "="*70)
    print("批量清理模板化残留内容")
    print("="*70)
    print(f"处理成功: {total_processed} 个")
    print("="*70)
    if results:
        print("\n详细结果：")
        for r in results:
            print(r)

if __name__ == '__main__':
    main()
