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

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {}
    result['char_count'] = len(content)
    result['word_count'] = len(re.findall(r'[\u4e00-\u9fa5]', content))
    
    result['has_frontmatter'] = content.startswith('---')
    
    fm = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm:
        fm_content = fm.group(1)
        result['frontmatter'] = {}
        for line in fm_content.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                result['frontmatter'][key.strip()] = val.strip()
    
    result['h1_count'] = len(re.findall(r'^# .+$', content, re.MULTILINE))
    result['h2_count'] = len(re.findall(r'^## .+$', content, re.MULTILINE))
    result['h3_count'] = len(re.findall(r'^### .+$', content, re.MULTILINE))
    
    table_lines = len(re.findall(r'^\|.*\|$', content, re.MULTILINE))
    result['table_count'] = table_lines // 2 if table_lines > 0 else 0
    
    result['code_block_count'] = len(re.findall(r'^```', content, re.MULTILINE)) // 2
    
    template_patterns = [
        r'问题总数.*\d+',
        r'构建时间.*\d{4}-\d{2}-\d{2}',
        r'关联素材.*\d+',
        r'本专题聚焦.*领域，共收录.*个有效问题',
    ]
    result['template_issues'] = []
    for pat in template_patterns:
        if re.search(pat, content[:3000]):
            result['template_issues'].append(pat)
    
    fake_case_patterns = [
        r'某企业',
        r'某公司',
        r'某创业公司',
        r'某互联网公司',
        r'某金融机构',
    ]
    result['fake_cases'] = []
    for pat in fake_case_patterns:
        matches = re.findall(pat, content)
        if matches:
            result['fake_cases'].extend(matches)
    
    result['quality_score'] = 0
    
    if result['char_count'] > 10000:
        result['quality_score'] += 20
    elif result['char_count'] > 5000:
        result['quality_score'] += 15
    elif result['char_count'] > 2000:
        result['quality_score'] += 10
    else:
        result['quality_score'] += 5
    
    if result['h2_count'] >= 6:
        result['quality_score'] += 15
    elif result['h2_count'] >= 4:
        result['quality_score'] += 10
    elif result['h2_count'] >= 2:
        result['quality_score'] += 5
    
    if result['table_count'] >= 5:
        result['quality_score'] += 20
    elif result['table_count'] >= 3:
        result['quality_score'] += 15
    elif result['table_count'] >= 1:
        result['quality_score'] += 10
    
    if result['code_block_count'] >= 3:
        result['quality_score'] += 15
    elif result['code_block_count'] >= 1:
        result['quality_score'] += 10
    
    if result['has_frontmatter'] and result.get('frontmatter', {}).get('quality_level'):
        result['quality_score'] += 15
    elif result['has_frontmatter']:
        result['quality_score'] += 10
    
    if not result['template_issues']:
        result['quality_score'] += 15
    else:
        result['quality_score'] -= 10
    
    if result['fake_cases']:
        result['quality_score'] -= 5
    
    if result['quality_score'] >= 90:
        result['quality_grade'] = 'S+'
    elif result['quality_score'] >= 80:
        result['quality_grade'] = 'S'
    elif result['quality_score'] >= 70:
        result['quality_grade'] = 'A'
    elif result['quality_score'] >= 60:
        result['quality_grade'] = 'B'
    elif result['quality_score'] >= 50:
        result['quality_grade'] = 'C'
    else:
        result['quality_grade'] = 'D'
    
    return result

results = {}

for filename in main_files:
    filepath = os.path.join(wiki_dir, filename)
    if os.path.exists(filepath):
        try:
            analysis = analyze_file(filepath)
            results[filename] = analysis
            grade = analysis['quality_grade']
            tables = analysis['table_count']
            chars = analysis['char_count']
            h2 = analysis['h2_count']
            fm = '✅' if analysis['has_frontmatter'] else '❌'
            tmpl = '❌' if analysis['template_issues'] else '✅'
            print(f"{fm} {tmpl} [{grade}] {filename:25s} | {chars:>6,}字 | {h2:2d}章 | {tables:2d}表")
        except Exception as e:
            print(f"❌❌ {filename}: {e}")
    else:
        print(f"⚠️  {filename}: 不存在")

print("\n" + "="*80)
print("统计汇总:")
print("="*80)

grades = {}
total_tables = 0
total_chars = 0
files_with_fm = 0
files_clean = 0

for filename, analysis in results.items():
    grade = analysis['quality_grade']
    grades[grade] = grades.get(grade, 0) + 1
    total_tables += analysis['table_count']
    total_chars += analysis['char_count']
    if analysis['has_frontmatter']:
        files_with_fm += 1
    if not analysis['template_issues']:
        files_clean += 1

for grade in ['S+', 'S', 'A', 'B', 'C', 'D']:
    count = grades.get(grade, 0)
    if count > 0:
        print(f"  {grade} 级: {count} 个文件")

print(f"\n处理文件总数: {len(results)}")
print(f"总字数: {total_chars:,} 字")
print(f"对比表格总数: {total_tables} 个")
print(f"平均每个文件表格数: {total_tables/len(results):.1f} 个")
print(f"有 frontmatter: {files_with_fm}/{len(results)} ({files_with_fm/len(results)*100:.0f}%)")
print(f"无模板化内容: {files_clean}/{len(results)} ({files_clean/len(results)*100:.0f}%)")

s_plus_files = [f for f, a in results.items() if a['quality_grade'] == 'S+']
s_files = [f for f, a in results.items() if a['quality_grade'] == 'S']
a_files = [f for f, a in results.items() if a['quality_grade'] == 'A']
b_files = [f for f, a in results.items() if a['quality_grade'] == 'B']
c_or_lower = [f for f, a in results.items() if a['quality_grade'] in ['C', 'D']]

print(f"\nS+级文件 ({len(s_plus_files)}):")
for f in s_plus_files:
    print(f"  - {f}")

print(f"\nS级文件 ({len(s_files)}):")
for f in s_files:
    print(f"  - {f}")

if a_files:
    print(f"\nA级文件 ({len(a_files)}):")
    for f in a_files:
        print(f"  - {f}")

if b_files:
    print(f"\nB级文件 ({len(b_files)}):")
    for f in b_files:
        print(f"  - {f}")

if c_or_lower:
    print(f"\nC级及以下文件 ({len(c_or_lower)}):")
    for f in c_or_lower:
        print(f"  - {f}")

fake_case_files = [(f, len(a['fake_cases'])) for f, a in results.items() if a['fake_cases']]
if fake_case_files:
    print(f"\n含模糊案例的文件 ({len(fake_case_files)}):")
    for f, count in fake_case_files:
        print(f"  - {f}: {count} 处")

with open(os.path.join(wiki_dir, 'final_quality_report.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n详细报告已保存到 final_quality_report.json")
