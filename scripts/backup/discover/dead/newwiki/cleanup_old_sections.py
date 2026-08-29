import os
import re
import json

wiki_dir = r"h:\github\cowkb\discover\newwiki"

exclude_files = {
    "task_plan.md", "findings.md", "progress.md", "index.md",
    "深度增强质量复核报告.md"
}

old_section_patterns = [
    r'^##\s*概述',
    r'^##\s*相关主题',
    r'^##\s*知识体系结构',
    r'^##\s*快速导航',
    r'^##\s*核心概念',
    r'^##\s*问题解答',
    r'^##\s*技术要点',
    r'^##\s*实践指南',
    r'^##\s*延伸资源',
    r'^##\s*变更记录',
    r'^##\s*知识体系框架图',
    r'^##\s*常见问题',
    r'^##\s*扩展资源',
]

def clean_old_sections(content):
    lines = content.split('\n')
    result_lines = []
    skip_mode = False
    
    for line in lines:
        is_h2 = line.startswith('## ')
        
        if is_h2:
            skip_mode = False
            for pat in old_section_patterns:
                if re.match(pat, line):
                    skip_mode = True
                    break
        
        if not skip_mode:
            result_lines.append(line)
    
    result = '\n'.join(result_lines)
    result = re.sub(r'\n{4,}', '\n\n\n', result)
    return result.strip() + '\n'

results = []

for filename in sorted(os.listdir(wiki_dir)):
    if not filename.endswith('.md'):
        continue
    if filename in exclude_files:
        continue
    
    filepath = os.path.join(wiki_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_len = len(content)
        new_content = clean_old_sections(content)
        new_len = len(new_content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        removed = original_len - new_len
        results.append({
            "filename": filename,
            "original_chars": original_len,
            "new_chars": new_len,
            "removed_chars": removed,
            "status": "success"
        })
        print(f"✅ {filename} - 移除 {removed:,} 字")
    except Exception as e:
        results.append({
            "filename": filename,
            "error": str(e),
            "status": "error"
        })
        print(f"❌ {filename} - 错误: {e}")

print(f"\n处理完成: {len(results)} 个文件")
total_removed = sum(r['removed_chars'] for r in results if r['status'] == 'success')
print(f"共移除旧模板内容: {total_removed:,} 字")

with open(os.path.join(wiki_dir, 'cleanup_old_sections_results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
