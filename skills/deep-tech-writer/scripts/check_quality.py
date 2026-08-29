import os
import re
import glob

def check_quality(directory):
    md_files = glob.glob(os.path.join(directory, '*.md'))
    md_files = [f for f in md_files if os.path.basename(f) != 'index.md']
    
    stats = {
        'total': len(md_files),
        'h1_count': [],
        'summary_len': [],
        'keyword_count': [],
        'h2_count': [],
        'has_toc': 0,
        'has_references': 0,
        'has_changelog': 0,
        'files_with_duplicate_h1': [],
        'files_with_short_summary': [],
        'files_with_few_keywords': [],
    }
    
    for fpath in sorted(md_files):
        fname = os.path.basename(fpath)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        h1_count = len(re.findall(r'^#\s+.+$', content, re.MULTILINE))
        stats['h1_count'].append(h1_count)
        if h1_count > 1:
            stats['files_with_duplicate_h1'].append(fname)
        
        summary_match = re.search(r'^> \*\*概要\*\*:\s*(.+)$', content, re.MULTILINE)
        if summary_match:
            summary_len = len(summary_match.group(1).strip())
            stats['summary_len'].append(summary_len)
            if summary_len < 20:
                stats['files_with_short_summary'].append(fname)
        
        keyword_match = re.search(r'^> \*\*关键词\*\*:\s*(.+)$', content, re.MULTILINE)
        if keyword_match:
            keywords = [k.strip() for k in keyword_match.group(1).split('·')]
            kw_count = len(keywords)
            stats['keyword_count'].append(kw_count)
            if kw_count < 3:
                stats['files_with_few_keywords'].append(fname)
        
        h2_count = len(re.findall(r'^##\s+.+$', content, re.MULTILINE))
        stats['h2_count'].append(h2_count)
        
        if '## 📑 目录' in content or '## 目录' in content:
            stats['has_toc'] += 1
        
        if '## 参考文件' in content:
            stats['has_references'] += 1
        
        if '## Changelog' in content or '## changelog' in content:
            stats['has_changelog'] += 1
    
    print('=' * 60)
    print('📊 质量检查报告')
    print('=' * 60)
    print(f'总文件数: {stats["total"]}')
    print()
    
    print('--- H1 标题 ---')
    print(f'  平均 H1 数量: {sum(stats["h1_count"])/len(stats["h1_count"]):.1f}')
    print(f'  重复 H1 的文件: {len(stats["files_with_duplicate_h1"])} 个')
    if stats['files_with_duplicate_h1']:
        for f in stats['files_with_duplicate_h1']:
            print(f'    - {f}')
    print()
    
    print('--- 概要质量 ---')
    if stats['summary_len']:
        print(f'  平均字数: {sum(stats["summary_len"])/len(stats["summary_len"]):.1f}')
        print(f'  最短: {min(stats["summary_len"])} 字')
        print(f'  最长: {max(stats["summary_len"])} 字')
        print(f'  ≤100字: {sum(1 for x in stats["summary_len"] if x <= 100)}/{len(stats["summary_len"])}')
    print()
    
    print('--- 关键词质量 ---')
    if stats['keyword_count']:
        print(f'  平均数量: {sum(stats["keyword_count"])/len(stats["keyword_count"]):.1f}')
        print(f'  最少: {min(stats["keyword_count"])} 个')
        print(f'  最多: {max(stats["keyword_count"])} 个')
        print(f'  3-5个: {sum(1 for x in stats["keyword_count"] if 3 <= x <= 5)}/{len(stats["keyword_count"])}')
        print(f'  <3个的文件: {len(stats["files_with_few_keywords"])} 个')
    print()
    
    print('--- 章节结构 ---')
    if stats['h2_count']:
        print(f'  平均 H2 数量: {sum(stats["h2_count"])/len(stats["h2_count"]):.1f}')
        print(f'  最少: {min(stats["h2_count"])} 个')
        print(f'  最多: {max(stats["h2_count"])} 个')
    print(f'  有目录的文件: {stats["has_toc"]}/{stats["total"]}')
    print(f'  有参考文件的文件: {stats["has_references"]}/{stats["total"]}')
    print(f'  有Changelog的文件: {stats["has_changelog"]}/{stats["total"]}')
    print()
    
    print('=' * 60)
    print('✅ 检查完成')
    print('=' * 60)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('用法: python check_quality.py <目录路径>')
        sys.exit(1)
    check_quality(sys.argv[1])
