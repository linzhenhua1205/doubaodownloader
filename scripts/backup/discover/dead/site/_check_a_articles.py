import json
from pathlib import Path

results = json.loads(Path(r'h:\github\cowkb\discover\site\quality_scan_results.json').read_text(encoding='utf-8'))

a_articles = [a for a in results['articles'] if a['quality'] == 'A']
print(f'A级文章: {len(a_articles)} 篇')
print()
for a in a_articles:
    print(f'  [{a["category"]}] {a["title"]}')
    print(f'    字数: {a["content_len"]}')
    print(f'    类型: {a["article_type"]}')
    print(f'    章节数: {a["section_count"]}')
    print(f'    表格数: {a["table_count"]}')
    print()
