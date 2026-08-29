import os
import re
import json

wiki_dir = r"h:\github\cowkb\discover\newwiki"

exclude_files = {
    "task_plan.md", "findings.md", "progress.md", "index.md",
    "深度增强质量复核报告.md", "quality_assessment.py", "final_stats.py",
    "enhance_wiki.py", "quality_check_v2.py"
}

def count_tables(content):
    return len(re.findall(r'^\|.*\|$', content, re.MULTILINE)) // 2

def count_mermaid(content):
    return len(re.findall(r'```mermaid', content))

def count_code_blocks(content):
    return len(re.findall(r'```', content)) // 2

def has_frontmatter(content):
    return content.startswith('---\n')

def count_cases(content):
    keywords = ['案例', '案例研究', '企业案例', '实战案例', '典型案例', '应用案例']
    count = 0
    for kw in keywords:
        count += len(re.findall(r'^##.*' + kw, content, re.MULTILINE))
        count += len(re.findall(r'^###.*' + kw, content, re.MULTILINE))
    return count

def check_template_content(content):
    template_patterns = [
        r'问题总数.*\d+',
        r'构建时间.*\d{4}-\d{2}-\d{2}',
        r'关联素材.*\d+',
        r'素材等级.*⭐',
        r'主题分布.*技术实现',
        r'核心要点.*定义',
    ]
    found = []
    for pat in template_patterns:
        if re.search(pat, content[:2000]):
            found.append(pat)
    return found

def check_empty_phrases(content):
    phrases = [
        '某企业', '某公司', '相关企业', '业内人士',
        '众所周知', '不言而喻', '值得一提的是',
        '需要指出的是', '可以说', '总的来说'
    ]
    count = 0
    for p in phrases:
        count += content.count(p)
    return count

def check_sections(content):
    sections = re.findall(r'^##\s+', content, re.MULTILINE)
    return len(sections)

results = []

for filename in sorted(os.listdir(wiki_dir)):
    if not filename.endswith('.md'):
        continue
    if filename in exclude_files:
        continue
    
    filepath = os.path.join(wiki_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    char_count = len(content)
    table_count = count_tables(content)
    mermaid_count = count_mermaid(content)
    code_count = count_code_blocks(content)
    fm = has_frontmatter(content)
    case_count = count_cases(content)
    template_issues = check_template_content(content)
    empty_count = check_empty_phrases(content)
    section_count = check_sections(content)
    
    results.append({
        "filename": filename,
        "char_count": char_count,
        "table_count": table_count,
        "mermaid_count": mermaid_count,
        "code_blocks": code_count,
        "has_frontmatter": fm,
        "case_sections": case_count,
        "template_issues_count": len(template_issues),
        "empty_phrases_count": empty_count,
        "section_count": section_count,
        "template_issues": template_issues
    })

print("=" * 120)
print(f"{'文件名':<25} {'字数':>8} {'表格':>6} {'Mermaid':>8} {'代码块':>6} {'Frontmatter':>12} {'案例数':>6} {'模板问题':>8} {'空话数':>6} {'章节数':>6}")
print("=" * 120)

for r in results:
    print(f"{r['filename']:<25} {r['char_count']:>8,} {r['table_count']:>6} {r['mermaid_count']:>8} {r['code_blocks']:>6} {str(r['has_frontmatter']):>12} {r['case_sections']:>6} {r['template_issues_count']:>8} {r['empty_phrases_count']:>6} {r['section_count']:>6}")

print("=" * 120)
print(f"\n总计: {len(results)} 个文件")
print(f"有 frontmatter: {sum(1 for r in results if r['has_frontmatter'])} 个")
print(f"有模板问题: {sum(1 for r in results if r['template_issues_count'] > 0)} 个")
print(f"总表格数: {sum(r['table_count'] for r in results)}")
print(f"总 Mermaid 图数: {sum(r['mermaid_count'] for r in results)}")

with open(os.path.join(wiki_dir, 'quality_check_v2_results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n详细结果已保存到 quality_check_v2_results.json")
