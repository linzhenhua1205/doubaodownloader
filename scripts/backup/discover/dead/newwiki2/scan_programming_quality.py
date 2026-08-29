import os
import re
import json

BASE_DIR = r'h:\github\cowkb\discover\newwiki2\programming'

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {
        'filename': os.path.basename(filepath),
        'title': '',
        'word_count': 0,
        'chinese_chars': 0,
        'english_words': 0,
        'quality': '',
        'structure_score': 0,
        'has_table': False,
        'has_code': False,
        'has_placeholder': False,
        'frontmatter_level': '',
        'issues': []
    }
    
    # 提取 frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        level_match = re.search(r'level\s*:\s*(\S+)', fm)
        if level_match:
            info['frontmatter_level'] = level_match.group(1)
    
    # 提取标题
    h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if h1_match:
        info['title'] = h1_match.group(1).strip()
    
    # 统计字数
    info['chinese_chars'] = len(re.findall(r'[\u4e00-\u9fff]', content))
    info['english_words'] = len(re.findall(r'[a-zA-Z]+', content))
    info['word_count'] = info['chinese_chars'] + info['english_words']
    
    # 结构检查
    structure_keywords = [
        '核心概念', '技术原理', '深度解析', '技术详解',
        '对比', '选型', '应用场景', '案例',
        '最新进展', '学习资源', '总结'
    ]
    present = 0
    for kw in structure_keywords:
        if kw in content:
            present += 1
    info['structure_score'] = present
    
    # 检查表格
    info['has_table'] = bool(re.search(r'\|.*\|.*\|', content))
    
    # 检查代码块
    info['has_code'] = bool(re.search(r'```', content))
    
    # 检查占位符（方案A/B/C、某公司、等等）
    placeholder_patterns = [
        r'方案[ABCD甲乙丙丁]',
        r'某(公司|企业|项目)',
        r'待补充',
        r'占位符',
        r'TODO',
        r'xxxx',
    ]
    for pat in placeholder_patterns:
        if re.search(pat, content):
            info['has_placeholder'] = True
            break
    
    # 质量评级
    issues = []
    if info['word_count'] >= 2000 and present >= 7 and info['has_table'] and info['has_code']:
        info['quality'] = 'S'
    elif info['word_count'] >= 1200 and present >= 5:
        info['quality'] = 'A'
    elif info['word_count'] >= 600 and present >= 3:
        info['quality'] = 'B'
    elif info['word_count'] >= 200:
        info['quality'] = 'C'
    else:
        info['quality'] = 'D'
    
    # 检测具体问题
    if info['has_placeholder']:
        issues.append('有占位符内容')
    if info['word_count'] < 300:
        issues.append('内容过短')
    if present < 3:
        issues.append('结构不完整')
    if not info['has_table'] and info['word_count'] > 500:
        issues.append('缺少对比表格')
    if not info['has_code'] and info['word_count'] > 500 and any(kw in info['filename'].lower() for kw in ['lua', 'python', 'rust', 'c', 'java', 'code', 'git', 'sql', 'api']):
        issues.append('缺少代码示例')
    
    info['issues'] = issues
    
    return info

def main():
    files = [f for f in os.listdir(BASE_DIR) if f.endswith('.md') and f != 'index.md']
    files.sort()
    
    all_info = []
    for f in files:
        filepath = os.path.join(BASE_DIR, f)
        info = analyze_file(filepath)
        all_info.append(info)
    
    # 统计
    quality_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for info in all_info:
        quality_counts[info['quality']] += 1
    
    print('=' * 70)
    print('  programming/ 目录质量扫描报告')
    print('=' * 70)
    print(f'  总文件数: {len(all_info)}')
    print()
    print('  质量等级分布:')
    for q in ['S', 'A', 'B', 'C', 'D']:
        bar = '█' * quality_counts[q]
        print(f'    {q}级: {quality_counts[q]:2d} 个 {bar}')
    print()
    
    # 按等级分组输出
    for q in ['D', 'C', 'B', 'A', 'S']:
        group = [info for info in all_info if info['quality'] == q]
        if group:
            print(f'\n  --- {q}级文件 ({len(group)}个) ---')
            for info in sorted(group, key=lambda x: x['word_count']):
                issues_str = f" | 问题: {', '.join(info['issues'])}" if info['issues'] else ''
                print(f"    {info['filename']:30s} | {info['word_count']:5d}字 | 结构{info['structure_score']:2d}/11{issues_str}")
    
    # 保存JSON
    with open(os.path.join(BASE_DIR, '..', 'programming_quality_scan.json'), 'w', encoding='utf-8') as f:
        json.dump(all_info, f, ensure_ascii=False, indent=2)
    
    print('\n' + '=' * 70)
    print(f'  详细数据已保存到 programming_quality_scan.json')
    print('=' * 70)

if __name__ == '__main__':
    main()
