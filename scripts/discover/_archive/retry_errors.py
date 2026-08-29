import json
from pathlib import Path

from generate_docs import generate_tech_doc
from config import DISCOVER_NEWWIKI2, DISCOVER_NEWWIKI2_DOCS

questions_file = DISCOVER_NEWWIKI2 / "questions_list.json"
output_dir = DISCOVER_NEWWIKI2_DOCS

with open(questions_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

questions = data['questions']
error_indices = [1208, 2128, 2178]

print("Retrying failed documents:")
for idx in error_indices:
    q = questions[idx]
    print(f"\n  [{idx}] Q{q['q_num']}: {q['title'][:60]}")
    result_path, status = generate_tech_doc(q, output_dir)
    print(f"    Status: {status}")
    print(f"    Path: {result_path}")

print("\nDone!")
