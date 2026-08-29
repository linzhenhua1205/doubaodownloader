import sys
sys.path.insert(0, r'd:\123\cowkb\scripts\discover')

from enhance_engine import load_questions, DOCS_DIR, QUESTIONS_FILE

print(f"DOCS_DIR: {DOCS_DIR}")
print(f"QUESTIONS_FILE: {QUESTIONS_FILE}")
print(f"QUESTIONS_FILE exists: {QUESTIONS_FILE.exists()}")

if QUESTIONS_FILE.exists():
    q = load_questions()
    print(f"Total questions: {q.get('total_questions', 0)}")
    print(f"Categories: {list(q.get('categories', {}).keys())}")

files = list(DOCS_DIR.rglob('*.md'))
print(f"\nTotal md files: {len(files)}")

small_files = [f for f in files if f.stat().st_size < 500 and f.name != 'index.md']
print(f"Small files (<500 bytes): {len(small_files)}")

if small_files:
    print(f"First small file: {small_files[0]}")
    content = small_files[0].read_text(encoding='utf-8', errors='ignore')
    print(f"Content preview:\n{content[:300]}")