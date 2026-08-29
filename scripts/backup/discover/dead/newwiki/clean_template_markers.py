import os
import re
import json

wiki_dir = r"h:\github\cowkb\discover\newwiki"

main_files = [
    "AI-Agent技术架构.md",
    "AI伦理与安全.md",
    "AI应用与落地实践.md",
    "AI技能与职业发展.md",
    "AI编程与开发工具.md",
    "企业管理与运营.md",
    "大模型技术与原理.md",
    "技术选型与方案对比.md",
    "数据与存储技术.md",
    "数据中心与基础设施.md",
    "方法论与工具.md",
    "服务器与硬件架构.md",
    "网络与系统运维.md",
    "行业趋势与洞察.md",
    "其他_后端开发.md",
    "其他_安全防护.md",
    "其他_数学算法.md",
    "其他_数据科学.md",
    "其他_生活文化.md",
    "其他_综合技术.md",
    "其他_编程语言.md",
    "其他_网络协议.md",
    "其他_职场管理.md",
]

def clean_template_markers(content):
    original = content
    
    content = re.sub(r'^> 构建时间:.*\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^> 问题总数:.*\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^> 关联素材:.*\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^> 素材等级:.*\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^> 定位:.*\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^> knowledge目录映射:.*\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^> 关联主题:.*\n', '', content, flags=re.MULTILINE)
    
    content = re.sub(r'^本专题聚焦\*\*.*?\*\*领域，共收录.*?个有效问题。\n', '', content, flags=re.MULTILINE)
    
    content = re.sub(r'^\*\*主题分布\*\*：.*\n', '', content, flags=re.MULTILINE)
    
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    removed = len(original) - len(content)
    return content, removed

stats = []
total_removed = 0
cleaned_count = 0

for filename in main_files:
    filepath = os.path.join(wiki_dir, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content, removed = clean_template_markers(content)
            
            if removed > 0:
                char_count = len(new_content)
                lines = new_content.split('\n')
                in_fm = False
                fm_end = -1
                for i, line in enumerate(lines):
                    if line.startswith('---'):
                        if not in_fm:
                            in_fm = True
                        else:
                            fm_end = i
                            break
                
                if fm_end > 0:
                    for i in range(1, fm_end):
                        if lines[i].startswith('word_count:'):
                            lines[i] = f'word_count: 约{char_count:,}字'
                            break
                
                new_content = '\n'.join(lines)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                cleaned_count += 1
                total_removed += removed
            
            stats.append({
                "filename": filename,
                "removed": removed,
                "status": "success"
            })
            status = "✅" if removed > 0 else "⏭️"
            print(f"{status} {filename}: 清理 {removed:,} 字")
        except Exception as e:
            stats.append({
                "filename": filename,
                "error": str(e),
                "status": "error"
            })
            print(f"❌ {filename}: {e}")

print(f"\n处理完成: {len(stats)} 个文件")
print(f"清理了模板标记的文件: {cleaned_count} 个")
print(f"共清理模板内容: {total_removed:,} 字")

with open(os.path.join(wiki_dir, 'template_markers_cleanup_stats.json'), 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
