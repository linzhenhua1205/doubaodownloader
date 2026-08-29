import os
import re
import json

wiki_dir = r"h:\github\cowkb\discover\newwiki"

s_level_files = [
    "AI伦理与安全.md",
    "AI技能与职业发展.md",
    "其他_后端开发.md",
    "其他_安全防护.md",
    "其他_生活文化.md",
    "其他_网络协议.md",
    "其他_职场管理.md",
]

file_metadata = {
    "AI伦理与安全.md": {
        "title": "AI 伦理与安全",
        "quality_level": "S",
        "category": "人工智能",
        "tags": ["AI伦理", "AI安全", "对齐技术", "模型安全", "监管合规"]
    },
    "AI技能与职业发展.md": {
        "title": "AI 技能与职业发展",
        "quality_level": "S",
        "category": "职业发展",
        "tags": ["AI职业", "技能提升", "学习路径", "转型指南", "人才市场"]
    },
    "其他_后端开发.md": {
        "title": "后端开发技术",
        "quality_level": "S",
        "category": "软件开发",
        "tags": ["后端开发", "服务端架构", "微服务", "云原生", "API设计"]
    },
    "其他_安全防护.md": {
        "title": "安全防护技术",
        "quality_level": "S",
        "category": "网络安全",
        "tags": ["网络安全", "安全防护", "渗透测试", "漏洞防护", "安全运维"]
    },
    "其他_生活文化.md": {
        "title": "生活与文化",
        "quality_level": "S",
        "category": "综合知识",
        "tags": ["生活百科", "文化历史", "社会观察", "人文素养", "思维方式"]
    },
    "其他_网络协议.md": {
        "title": "网络协议",
        "quality_level": "S",
        "category": "网络技术",
        "tags": ["网络协议", "TCP/IP", "HTTP", "DNS", "网络安全"]
    },
    "其他_职场管理.md": {
        "title": "职场管理",
        "quality_level": "S",
        "category": "职业发展",
        "tags": ["职场技能", "管理方法", "职业发展", "沟通技巧", "团队协作"]
    }
}

old_section_keywords = [
    "概述", "相关主题", "知识体系结构", "快速导航", "核心概念",
    "问题解答", "技术要点", "实践指南", "延伸资源", "变更记录",
    "知识体系框架图", "常见问题", "扩展资源"
]

def clean_old_sections(content):
    lines = content.split('\n')
    result_lines = []
    h1_title = ""
    found_h1 = False
    skip_mode = False
    first_seven_count = 0
    
    for line in lines:
        if not found_h1:
            if line.startswith('# '):
                h1_title = line
                found_h1 = True
            continue
        
        if line.startswith('## '):
            section_title = line[3:].strip()
            
            is_old = False
            for kw in old_section_keywords:
                if kw in section_title:
                    is_old = True
                    break
            
            if is_old:
                skip_mode = True
                continue
            else:
                if first_seven_count < 7:
                    first_seven_count += 1
                skip_mode = False
        
        if not skip_mode:
            result_lines.append(line)
    
    final_lines = [h1_title, ""] + result_lines
    result = '\n'.join(final_lines)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    return result.strip() + '\n'

def add_frontmatter(content, metadata):
    char_count = len(content)
    word_count_est = char_count
    
    frontmatter = f"""---
title: {metadata['title']}
date: 2026-07-22
quality_level: {metadata['quality_level']}
word_count: 约{word_count_est:,}字
category: {metadata['category']}
tags: [{', '.join(metadata['tags'])}]
---

"""
    return frontmatter + content

def process_file(filename, metadata):
    filepath = os.path.join(wiki_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    
    if content.startswith('---\n'):
        parts = content.split('---\n', 2)
        if len(parts) >= 3:
            content = parts[2].lstrip('\n')
    
    content = clean_old_sections(content)
    content = add_frontmatter(content, metadata)
    
    new_len = len(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return original_len, new_len

results = []

for filename in s_level_files:
    if filename in file_metadata and os.path.exists(os.path.join(wiki_dir, filename)):
        try:
            orig_len, new_len = process_file(filename, file_metadata[filename])
            removed = orig_len - new_len
            results.append({
                "filename": filename,
                "original_chars": orig_len,
                "new_chars": new_len,
                "removed_chars": removed,
                "status": "success"
            })
            print(f"✅ {filename} - 完成 (移除 {removed:,} 字)")
        except Exception as e:
            results.append({
                "filename": filename,
                "error": str(e),
                "status": "error"
            })
            print(f"❌ {filename} - 错误: {e}")
    else:
        print(f"⚠️  {filename} - 跳过")

print(f"\n处理完成: {len(results)} 个文件")
total_removed = sum(r['removed_chars'] for r in results if r['status'] == 'success')
print(f"共移除旧模板内容: {total_removed:,} 字")

with open(os.path.join(wiki_dir, 's_level_cleanup_results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
