import os
import re
from pathlib import Path

base_dir = Path(r"h:\github\cowkb\discover\newwiki2")
dirs = ["server-hardware", "服务器硬件"]

def count_words(text):
    chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
    english = len(re.findall(r'[a-zA-Z]+', text))
    return chinese + english

results = []

for d in dirs:
    dir_path = base_dir / d
    if not dir_path.exists():
        continue
    for f in sorted(dir_path.glob("*.md")):
        if f.name == "index.md":
            continue
        try:
            text = f.read_text(encoding='utf-8')
        except:
            continue
        
        words = count_words(text)
        
        quality = "未知"
        if "quality_level: S" in text[:300] or "status: S级" in text[:300]:
            quality = "S"
        elif "quality_level: A" in text[:300]:
            quality = "A"
        elif "quality_level: B" in text[:300]:
            quality = "B"
        elif words < 1000:
            quality = "C/D"
        elif words < 2000:
            quality = "B/C"
        elif words < 3500:
            quality = "B"
        else:
            quality = "A/B"
        
        has_table = "| " in text and "---|" in text
        has_ascii_diagram = "```" in text
        
        module_count = 0
        if "知识体系" in text or "知识全景" in text: module_count += 1
        if "核心技术" in text or "技术深度" in text: module_count += 1
        if "对比" in text or "比较" in text: module_count += 1
        if "选型" in text or "决策" in text: module_count += 1
        if "最新进展" in text or "2025" in text: module_count += 1
        if "案例" in text or "最佳实践" in text: module_count += 1
        if "学习路径" in text or "学习资源" in text: module_count += 1
        
        results.append({
            "dir": d,
            "file": f.name,
            "words": words,
            "quality": quality,
            "has_table": has_table,
            "has_diagram": has_ascii_diagram,
            "module_count": module_count
        })

print(f"{'目录':<20} {'文件名':<25} {'字数':<8} {'质量':<6} {'表格':<4} {'架构图':<6} {'模块数':<6}")
print("-" * 85)

for r in results:
    print(f"{r['dir']:<20} {r['file']:<25} {r['words']:<8} {r['quality']:<6} {'是' if r['has_table'] else '否':<4} {'是' if r['has_diagram'] else '否':<6} {r['module_count']:<6}")

print("\n" + "=" * 85)
print(f"总文件数: {len(results)}")
print(f"S级: {sum(1 for r in results if r['quality']=='S')}")
print(f"A级: {sum(1 for r in results if r['quality']=='A')}")
print(f"B级: {sum(1 for r in results if r['quality']=='B')}")
print(f"A/B级: {sum(1 for r in results if r['quality']=='A/B')}")
print(f"B/C级: {sum(1 for r in results if r['quality']=='B/C')}")
print(f"C/D级: {sum(1 for r in results if r['quality']=='C/D')}")
print(f"未知: {sum(1 for r in results if r['quality']=='未知')}")
print(f"有表格: {sum(1 for r in results if r['has_table'])}")
print(f"有架构图: {sum(1 for r in results if r['has_diagram'])}")

total_words = sum(r['words'] for r in results)
print(f"\n总字数: {total_words}")
print(f"平均字数: {int(total_words/len(results))}")
