import os
import re
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

PRIORITY_DIRS = [
    "server-hardware",
    "AI-模型架构", 
    "AI-Agent",
    "ai-models",
    "programming",
]

DIR_NAMES = {
    "server-hardware": "服务器硬件",
    "AI-模型架构": "AI模型架构",
    "AI-Agent": "AI智能体",
    "ai-models": "AI模型库",
    "programming": "编程开发",
}

def count_chinese_chars(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def count_words(text):
    chinese = count_chinese_chars(text)
    english = len(re.findall(r'[a-zA-Z]+', text))
    return chinese + english

def extract_sections(text):
    sections = []
    current_title = None
    current_content = []
    
    in_body = False
    for line in text.split('\n'):
        if not in_body:
            if line.startswith('---') and not in_body:
                in_body = True
                continue
            continue
        
        match = re.match(r'^##\s+\d+\.\s*(.+)$', line)
        if match:
            if current_title:
                sections.append({
                    'title': current_title,
                    'content': '\n'.join(current_content).strip()
                })
            current_title = match.group(1).strip()
            current_content = []
        elif current_title is not None:
            current_content.append(line)
    
    if current_title:
        sections.append({
            'title': current_title,
            'content': '\n'.join(current_content).strip()
        })
    
    return sections

def get_section_summary(section):
    content = section['content']
    content = re.sub(r'>\s*`[^`]+`', '', content)
    content = re.sub(r'\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'https?://\S+', '', content)
    content = re.sub(r'#+', '', content)
    content = re.sub(r'\|.*?\|', '', content)
    content = re.sub(r'-{3,}', '', content)
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    if lines:
        first = lines[0]
        if len(first) > 150:
            first = first[:150] + '...'
        return first
    return section['title']

def deep_enhance_file(filepath):
    try:
        text = filepath.read_text(encoding='utf-8')
    except:
        return False
    
    if '## 深度导读' in text:
        return False
    
    sections = extract_sections(text)
    if not sections:
        return False
    
    summaries = []
    for sec in sections[:8]:
        summary = get_section_summary(sec)
        if summary and len(summary) > 10:
            summaries.append(f"- **{sec['title']}**: {summary}")
    
    if len(summaries) < 2:
        return False
    
    insert_pos = text.find('## 卡片概览')
    if insert_pos == -1:
        return False
    
    deep_guide = f"""## 深度导读

本卡片聚合了 {len(sections)} 条相关主题的知识笔记，涵盖以下核心内容：

{chr(10).join(summaries)}

> **阅读建议**: 点击每条笔记下方的源文件链接，可查看完整内容。建议从感兴趣的主题入手，逐步构建知识体系。

"""
    
    new_text = text[:insert_pos] + deep_guide + text[insert_pos:]
    
    filepath.write_text(new_text, encoding='utf-8')
    return True

def main():
    results = {}
    
    for dir_name in PRIORITY_DIRS:
        dir_path = BASE_DIR / dir_name
        if not dir_path.exists():
            continue
        
        files = []
        for md_file in dir_path.glob('*.md'):
            if md_file.name == 'index.md':
                continue
            try:
                text = md_file.read_text(encoding='utf-8')
            except:
                continue
            wc = count_words(text)
            secs = extract_sections(text)
            files.append((md_file, wc, len(secs)))
        
        files.sort(key=lambda x: x[1], reverse=True)
        
        top_files = files[:5]
        enhanced = 0
        
        for fpath, wc, sec_count in top_files:
            if deep_enhance_file(fpath):
                enhanced += 1
                print(f"  深度增强: {fpath.name} ({wc}字, {sec_count}条)")
        
        results[dir_name] = {
            'total': len(files),
            'enhanced': enhanced,
            'top_files': [f.name for f, _, _ in top_files],
        }
    
    print("\n=== 重点目录深度增强统计 ===")
    for d, info in results.items():
        print(f"{DIR_NAMES.get(d, d)}: 共{info['total']}个文件, 深度增强{info['enhanced']}个")
    
    with open(BASE_DIR / 'deep_enhance_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
