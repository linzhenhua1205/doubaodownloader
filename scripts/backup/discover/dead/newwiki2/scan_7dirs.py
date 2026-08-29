import os
import re
import json
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

TARGET_DIRS = [
    "programming",
    "编程语言",
    "软件架构",
    "project-mgmt",
    "security",
    "安全",
    "算法优化",
    "研究与论文",
    "research",
    "papers-research",
]

def count_chinese_chars(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def count_words(text):
    chinese = count_chinese_chars(text)
    english = len(re.findall(r'[a-zA-Z]+', text))
    return chinese + english

def extract_frontmatter(text):
    if not text.startswith('---'):
        return {}
    match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm

def classify_by_words(word_count):
    if word_count >= 4000:
        return 'S'
    elif word_count >= 2000:
        return 'A'
    elif word_count >= 1000:
        return 'B'
    else:
        return 'C'

def scan_dir(dirname):
    dirpath = BASE_DIR / dirname
    if not dirpath.exists():
        return []
    
    files = []
    for md_file in sorted(dirpath.glob('*.md')):
        if md_file.name == 'index.md':
            continue
        try:
            text = md_file.read_text(encoding='utf-8')
        except:
            continue
        
        fm = extract_frontmatter(text)
        wc = count_words(text)
        
        quality = fm.get('quality_level', '')
        if not quality:
            quality = classify_by_words(wc)
        
        tables = len(re.findall(r'\|.*?\|', text)) // 2
        code_blocks = len(re.findall(r'```', text)) // 2
        
        has_mermaid = 'mermaid' in text
        has_ascii_art = '```' in text and ('──' in text or '│' in text)
        
        files.append({
            'name': md_file.name,
            'path': str(md_file.relative_to(BASE_DIR)),
            'word_count': wc,
            'quality_level': quality,
            'tables': tables,
            'code_blocks': code_blocks,
            'has_mermaid': has_mermaid,
            'title': fm.get('title', ''),
            'status': fm.get('status', ''),
        })
    
    return files

def main():
    all_files = []
    dir_stats = {}
    
    for dirname in TARGET_DIRS:
        files = scan_dir(dirname)
        all_files.extend(files)
        
        if not files:
            continue
        
        stats = {
            'total': len(files),
            'S': sum(1 for f in files if f['quality_level'] == 'S'),
            'A': sum(1 for f in files if f['quality_level'] == 'A'),
            'B': sum(1 for f in files if f['quality_level'] == 'B'),
            'C': sum(1 for f in files if f['quality_level'] == 'C'),
            'total_words': sum(f['word_count'] for f in files),
            'files': files,
        }
        dir_stats[dirname] = stats
    
    print("=" * 80)
    print("7个开发与管理目录 - 现状统计")
    print("=" * 80)
    print()
    
    grand_total = 0
    grand_words = 0
    grand_quality = {'S': 0, 'A': 0, 'B': 0, 'C': 0}
    
    for dirname, stats in dir_stats.items():
        grand_total += stats['total']
        grand_words += stats['total_words']
        for k in ['S', 'A', 'B', 'C']:
            grand_quality[k] += stats[k]
        
        avg_words = stats['total_words'] // max(stats['total'], 1)
        print(f"【{dirname}】")
        print(f"  文件数: {stats['total']} 个")
        print(f"  总字数: {stats['total_words']:,} 字")
        print(f"  平均字数: {avg_words:,} 字")
        print(f"  质量分布: S级 {stats['S']} | A级 {stats['A']} | B级 {stats['B']} | C级 {stats['C']}")
        print()
        print("  文件列表:")
        for f in sorted(files := stats['files'], key=lambda x: x['word_count'], reverse=True):
            flag = "★" if f['quality_level'] == 'S' else "☆" if f['quality_level'] == 'A' else "○"
            print(f"    {flag} [{f['quality_level']}] {f['name']:30s} {f['word_count']:>5,}字  表{f['tables']:2d} 码{f['code_blocks']:2d}")
        print()
    
    print("=" * 80)
    print("【汇总统计】")
    print(f"  目录数: {len(dir_stats)}")
    print(f"  文件总数: {grand_total} 个")
    print(f"  总字数: {grand_words:,} 字")
    print(f"  平均字数: {grand_words // max(grand_total, 1):,} 字")
    print(f"  质量分布: S级 {grand_quality['S']} | A级 {grand_quality['A']} | B级 {grand_quality['B']} | C级 {grand_quality['C']}")
    print("=" * 80)
    
    with open(BASE_DIR / 'scan_7dirs_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'dir_stats': {k: {kk: vv for kk, vv in v.items() if kk != 'files'} for k, v in dir_stats.items()},
            'all_files': all_files,
            'grand_total': grand_total,
            'grand_words': grand_words,
            'grand_quality': grand_quality,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细数据已保存到 scan_7dirs_results.json")

if __name__ == '__main__':
    main()
