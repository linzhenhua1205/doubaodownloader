import json
from pathlib import Path
from collections import Counter

results = json.loads(Path(r'h:\github\cowkb\discover\site\quality_scan_results.json').read_text(encoding='utf-8'))

b_articles = [a for a in results['articles'] if a['quality'] == 'B']
print(f'B级文章总数: {len(b_articles)}')
print()

# 统计缺少哪些章节
important_sections = [
    "核心要点", "背景与上下文", "深度解读", "最新进展",
    "相关素材", "延伸阅读", "参考来源", "案例补充",
    "技术原理", "行业影响", "实践指南", "风险与挑战"
]

missing_counter = Counter()
for a in b_articles:
    section_set = set(a['sections'])
    for s in important_sections:
        if s not in section_set:
            missing_counter[s] += 1

print('B级文章缺少的章节统计:')
for sec, count in missing_counter.most_common():
    pct = count / len(b_articles) * 100
    print(f'  {sec}: {count} 篇 ({pct:.1f}%)')

print()
print(f'有快速导读: {sum(1 for a in b_articles if a["has_summary"])} 篇')
print(f'有知识增强: {sum(1 for a in b_articles if a["has_knowledge"])} 篇')
print(f'平均字数: {int(sum(a["content_len"] for a in b_articles) / len(b_articles))}')
