import os

ai_dir = r'site\AI与机器学习'
articles = []

for f in os.listdir(ai_dir):
    if f.endswith('.md') and f != 'index.md':
        filepath = os.path.join(ai_dir, f)
        with open(filepath, 'r', encoding='utf-8') as fh:
            content = fh.read()
        
        char_count = len(content.replace(' ', '').replace('\n', ''))
        table_count = content.count('|:---')
        has_template = '规模化落地：2026年AI从技术验证转向生产级应用' in content
        
        quality_level = 'unknown'
        if 'quality_level: S' in content:
            quality_level = 'S'
        elif 'quality_level: A' in content:
            quality_level = 'A'
        elif 'quality_level: B' in content:
            quality_level = 'B'
        
        articles.append({
            'file': f,
            'chars': char_count,
            'tables': table_count,
            'quality': quality_level,
            'template': has_template
        })

# 按字数升序排列，找字数较少需要提升的
articles.sort(key=lambda x: x['chars'])

print('=== AI与机器学习目录全部文章（按字数升序） ===')
for a in articles[:30]:
    print(f"  {a['file'][:55]:55s} | 字数:{a['chars']:5d} | 表格:{a['tables']:2d} | 质量:{a['quality']} | 模板化:{a['template']}")

print(f'\n总计: {len(articles)} 篇')
