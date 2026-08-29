
import os
import re
import json

results = []
for filename in sorted(os.listdir('.')):
    if not filename.endswith('.md'):
        continue
    if filename in ['task_plan.md', 'findings.md', 'progress.md', 'scan_files.py', 'AGENTS.md']:
        continue
    
    filepath = os.path.join('.', filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        frontmatter = {}
        if fm_match:
            fm_text = fm_match.group(1)
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    frontmatter[key.strip()] = val.strip()
        
        text = content
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        quality = frontmatter.get('quality_level', '未评级')
        title = frontmatter.get('title', filename.replace('.md', ''))
        wc = frontmatter.get('word_count', f'约{chinese_chars + english_words}字')
        
        results.append({
            'filename': filename,
            'title': title,
            'quality_level': quality,
            'word_count_fm': wc,
            'file_size_kb': round(os.path.getsize(filepath) / 1024, 1),
            'chinese_chars': chinese_chars,
            'english_words': english_words,
        })
    except Exception as e:
        results.append({
            'filename': filename,
            'title': 'ERROR',
            'quality_level': str(e),
            'word_count_fm': '',
            'file_size_kb': 0,
            'chinese_chars': 0,
            'english_words': 0,
        })

quality_order = {'S+级': 0, 'S级': 1, 'A级': 2, 'B级': 3, 'C级': 4, 'D级': 5, '未评级': 6}
results.sort(key=lambda x: (quality_order.get(x['quality_level'], 99), x['filename']))

print('=' * 110)
print(f'共 {len(results)} 个文件')
print('=' * 110)
print(f'{"文件名":<35} {"标题":<22} {"质量等级":<10} {"大小":<8} {"中文字数":<8} {"英文单词":<8}')
print('-' * 110)

from collections import Counter
quality_counter = Counter()

for r in results:
    title_short = r['title'][:20]
    print(f'{r["filename"]:<35} {title_short:<22} {r["quality_level"]:<10} {r["file_size_kb"]:>6.1f}KB {r["chinese_chars"]:>6} {r["english_words"]:>6}')
    quality_counter[r['quality_level']] += 1

print('=' * 110)
print('\n质量等级分布:')
for q in ['S+级', 'S级', 'A级', 'B级', 'C级', 'D级', '未评级']:
    if quality_counter[q] > 0:
        print(f'  {q}: {quality_counter[q]} 个')

print(f'\n总计: {len(results)} 个文件')

# 保存到 JSON
with open('_scan_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('\n结果已保存到 _scan_results.json')
