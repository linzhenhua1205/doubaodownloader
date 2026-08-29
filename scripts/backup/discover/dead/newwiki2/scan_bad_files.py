import os
import re

BASE_DIR = r'h:\github\cowkb\discover\newwiki2\ai-models'
files = [f for f in os.listdir(BASE_DIR) if f.endswith('.md') and f != 'index.md']

bad_files = []
good_files = []

for f in files:
    filepath = os.path.join(BASE_DIR, f)
    with open(filepath, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    # 检查标题是否损坏（包含链接、特殊符号等）
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else ''
    
    # 标题损坏的标志：包含 ]( 、 # 过多、URL等
    title_broken = False
    if '](' in title or 'http' in title or title.count('#') > 2:
        title_broken = True
    
    # 检查是否有深度解析等完整结构
    has_depth = '深度解析' in content or '技术详解' in content or '技术详情' in content
    has_latest = '最新进展' in content
    has_position = '卡片定位' in content or '卡片概述' in content
    has_points = '核心要点' in content
    has_scenes = '应用场景' in content or '典型应用场景' in content
    
    structure_score = sum([has_depth, has_latest, has_position, has_points, has_scenes])
    
    word_count = len(content)
    
    # 判断是否需要修复
    needs_fix = False
    reason = []
    
    if title_broken:
        needs_fix = True
        reason.append('标题损坏')
    
    if structure_score < 3:
        needs_fix = True
        reason.append(f'结构不完整({structure_score}/5)')
    
    if word_count < 500:
        needs_fix = True
        reason.append(f'字数不足({word_count}字)')
    
    if needs_fix:
        bad_files.append({
            'file': f,
            'title': title[:50],
            'word_count': word_count,
            'structure_score': structure_score,
            'reason': ', '.join(reason)
        })
    else:
        good_files.append(f)

print(f'总文件数: {len(files)}')
print(f'质量良好: {len(good_files)}')
print(f'需要修复: {len(bad_files)}')
print()
print('需要修复的文件:')
for f in sorted(bad_files, key=lambda x: x['word_count']):
    print(f"  {f['file']}")
    print(f"    标题: {f['title']}")
    print(f"    字数: {f['word_count']}, 结构: {f['structure_score']}/5")
    print(f"    问题: {f['reason']}")
    print()
