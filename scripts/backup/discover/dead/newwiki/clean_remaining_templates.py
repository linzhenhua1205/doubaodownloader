import os
import re
import json

wiki_dir = r"h:\github\cowkb\discover\newwiki"

a_level_files = [
    "AI应用与落地实践.md",
    "大模型技术与原理.md",
    "技术选型与方案对比.md",
    "数据与存储技术.md",
    "方法论与工具.md",
    "服务器与硬件架构.md",
    "其他_数学算法.md",
    "其他_综合技术.md",
]

old_section_titles = {
    "概述", "相关主题", "知识体系结构", "快速导航", "核心概念",
    "问题解答", "技术要点", "实践指南", "延伸资源", "变更记录",
    "知识体系框架图", "常见问题", "扩展资源", "2025-2026最新进展",
    "问题列表", "问答列表", "全部问题", "精选问题",
    "知识框架", "知识图谱", "思维导图",
    "目录", "导航", "索引",
}

def clean_old_sections(content):
    lines = content.split('\n')
    result_lines = []
    skip_mode = False
    in_code_block = False
    found_h1 = False
    in_frontmatter = False
    frontmatter_lines = []
    
    for line in lines:
        if line.startswith('---') and not in_frontmatter and not found_h1:
            in_frontmatter = True
            frontmatter_lines.append(line)
            continue
        
        if in_frontmatter:
            frontmatter_lines.append(line)
            if line.startswith('---') and len(frontmatter_lines) > 2:
                in_frontmatter = False
                result_lines.extend(frontmatter_lines)
                result_lines.append('')
            continue
        
        if not found_h1:
            if line.startswith('# '):
                found_h1 = True
                result_lines.append(line)
                result_lines.append('')
            continue
        
        if line.startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue
        
        if in_code_block:
            result_lines.append(line)
            continue
        
        if line.startswith('## '):
            section_title = line[3:].strip()
            clean_title = re.sub(r'^[📌🌟🎭🌐💼🔬📊🎯🏢📚🧬🏗️\s\d一二三四五六七八九十]+', '', section_title).strip()
            clean_title = re.sub(r'^[、\.\s]+', '', clean_title).strip()
            
            should_skip = False
            for old_title in old_section_titles:
                if clean_title == old_title or clean_title.startswith(old_title):
                    should_skip = True
                    break
            
            if should_skip:
                skip_mode = True
                continue
            else:
                skip_mode = False
        
        if not skip_mode:
            result_lines.append(line)
    
    result = '\n'.join(result_lines)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    return result

def update_frontmatter(content, quality_level=None):
    lines = content.split('\n')
    char_count = len(content)
    in_fm = False
    fm_end = -1
    
    for i, line in enumerate(lines):
        if line.startswith('---'):
            if not in_fm:
                in_fm = True
            else:
                fm_end = i
                break
    
    if fm_end == -1:
        return content
    
    for i in range(1, fm_end):
        if lines[i].startswith('word_count:'):
            lines[i] = f'word_count: 约{char_count:,}字'
        if quality_level and lines[i].startswith('quality_level:'):
            lines[i] = f'quality_level: {quality_level}'
    
    return '\n'.join(lines)

stats = []

for filename in a_level_files:
    filepath = os.path.join(wiki_dir, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_len = len(content)
            
            new_content = clean_old_sections(content)
            new_len = len(new_content)
            
            removed = original_len - new_len
            
            new_content = update_frontmatter(new_content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            stats.append({
                "filename": filename,
                "original": original_len,
                "new": new_len,
                "removed": removed,
                "status": "success"
            })
            print(f"✅ {filename}: -{removed:,} 字 (清理模板)")
        except Exception as e:
            stats.append({
                "filename": filename,
                "error": str(e),
                "status": "error"
            })
            print(f"❌ {filename}: {e}")

print(f"\n处理完成: {len(stats)} 个文件")
total_removed = sum(s["removed"] for s in stats if s["status"] == "success")
print(f"共清理模板内容: {total_removed:,} 字")

with open(os.path.join(wiki_dir, 'clean_remaining_stats.json'), 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
