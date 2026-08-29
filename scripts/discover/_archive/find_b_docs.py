import json
from pathlib import Path
import re

from config import DISCOVER_NEWWIKI2_DOCS

def find_b_level_docs(docs_dir):
    docs_path = Path(docs_dir)
    b_docs = []

    for cat_dir in sorted(docs_path.iterdir()):
        if not cat_dir.is_dir():
            continue
        for md_file in cat_dir.glob('*.md'):
            if md_file.name == 'index.md':
                continue
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                match = re.search(r'quality_level:\s*(\S+)', content)
                if match and match.group(1) == 'B':
                    title_match = re.search(r'title:\s*(.+)', content)
                    title = title_match.group(1).strip() if title_match else md_file.stem
                    b_docs.append({
                        'path': str(md_file),
                        'category': cat_dir.name,
                        'title': title
                    })
            except:
                pass

    return b_docs

if __name__ == '__main__':
    docs_dir = DISCOVER_NEWWIKI2_DOCS
    b_docs = find_b_level_docs(str(docs_dir))

    print(f"Total B-level docs: {len(b_docs)}")
    print("\nFirst 20 B-level docs:")
    for i, doc in enumerate(b_docs[:20]):
        print(f"  [{i}] {doc['category']}: {doc['title'][:70]}")
