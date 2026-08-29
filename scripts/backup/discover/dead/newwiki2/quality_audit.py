import os
import re
import json
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

def count_chinese_chars(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def count_words(text):
    chinese = count_chinese_chars(text)
    english = len(re.findall(r'[a-zA-Z]+', text))
    return chinese + english

def extract_h1(text):
    match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def has_frontmatter(text):
    return text.startswith('---')

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

def is_index_stub(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if len(lines) <= 3:
        return True
    link_lines = sum(1 for l in lines if re.match(r'^[-*]\s+\[.+\]', l) or re.match(r'^[-*]\s+.+\.md', l))
    return link_lines >= len(lines) * 0.7

def classify_quality(filepath, text):
    word_count = count_words(text)
    h1 = extract_h1(text)
    fm = extract_frontmatter(text)
    stub = is_index_stub(text)
    
    has_truncated_title = False
    if h1:
        if h1.endswith('最') or h1.endswith('与') or h1.endswith('和') or h1.endswith('的'):
            has_truncated_title = True
        if len(h1) <= 4 and not filepath.name.startswith('0'):
            has_truncated_title = True
    
    if stub or word_count < 100:
        grade = 'C'
    elif word_count < 500:
        grade = 'B'
    elif word_count < 2000:
        grade = 'A'
    else:
        grade = 'S'
    
    return {
        'path': str(filepath.relative_to(BASE_DIR)),
        'name': filepath.name,
        'parent': filepath.parent.name,
        'word_count': word_count,
        'grade': grade,
        'h1': h1,
        'has_frontmatter': bool(fm),
        'frontmatter': fm,
        'has_truncated_title': has_truncated_title,
        'is_stub': stub,
        'line_count': len(text.split('\n')),
    }

def main():
    all_files = []
    skip_files = {'index.md', 'README.md'}
    
    for md_file in BASE_DIR.rglob('*.md'):
        if md_file.name in skip_files:
            continue
        try:
            text = md_file.read_text(encoding='utf-8')
        except:
            continue
        info = classify_quality(md_file, text)
        all_files.append(info)
    
    total = len(all_files)
    grades = {'S': 0, 'A': 0, 'B': 0, 'C': 0}
    truncated = 0
    no_frontmatter = 0
    stubs = 0
    
    by_dir = {}
    
    for f in all_files:
        grades[f['grade']] += 1
        if f['has_truncated_title']:
            truncated += 1
        if not f['has_frontmatter']:
            no_frontmatter += 1
        if f['is_stub']:
            stubs += 1
        
        d = f['parent']
        if d not in by_dir:
            by_dir[d] = {'total': 0, 'S': 0, 'A': 0, 'B': 0, 'C': 0}
        by_dir[d]['total'] += 1
        by_dir[d][f['grade']] += 1
    
    print(f"总文件数: {total}")
    print(f"S级 (>2000字): {grades['S']}")
    print(f"A级 (500-2000字): {grades['A']}")
    print(f"B级 (100-500字): {grades['B']}")
    print(f"C级 (<100字/索引桩): {grades['C']}")
    print(f"标题截断: {truncated}")
    print(f"无头部元数据: {no_frontmatter}")
    print(f"索引桩文件: {stubs}")
    
    print("\n=== 按目录统计 ===")
    for d in sorted(by_dir.keys()):
        info = by_dir[d]
        print(f"{d}: 总{info['total']} S{info['S']} A{info['A']} B{info['B']} C{info['C']}")
    
    print("\n=== C级文件列表 ===")
    for f in sorted(all_files, key=lambda x: x['path']):
        if f['grade'] == 'C':
            print(f"  [{f['word_count']:4d}字] {f['path']} - {f['h1'] or '无标题'}")
    
    print("\n=== 标题截断文件 ===")
    for f in sorted(all_files, key=lambda x: x['path']):
        if f['has_truncated_title']:
            print(f"  {f['path']} - 「{f['h1']}」")
    
    with open(BASE_DIR / 'quality_report.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total': total,
            'grades': grades,
            'truncated': truncated,
            'no_frontmatter': no_frontmatter,
            'stubs': stubs,
            'by_dir': by_dir,
            'files': all_files,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细报告已保存到 quality_report.json")

if __name__ == '__main__':
    main()
