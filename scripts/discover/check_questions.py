import json
from pathlib import Path

from config import DISCOVER_NEWWIKI2

with open(DISCOVER_NEWWIKI2 / "questions_list.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Total:', data['total_count'])
print('\nFirst 20 questions:')
for i, q in enumerate(data['questions'][:20]):
    print(f"  [{i}] Q{q['q_num']}: {q['title'][:70]} ({q['format']})")

print('\nCategory stats:')
for cat, count in sorted(data['categories'].items()):
    print(f"  {cat}: {count}")
