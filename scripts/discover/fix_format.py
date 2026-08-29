#!/usr/bin/env python3
import os
import re
from pathlib import Path

from config import DISCOVER_NEWWIKI2_DOCS

def fix_doc_format(doc_path):
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        fixed = False

        content = content.replace(
            '**所属分类：',
            '**所属分类：** '
        )
        fixed = True

        content = content.replace('\n---\n\n---\n', '\n---\n')
        fixed = True

        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True
    except Exception as e:
        print(f"  Error fixing {doc_path}: {e}")
        return False

def batch_fix(docs_dir):
    docs_path = Path(docs_dir)
    total = 0
    fixed = 0
    errors = 0

    print("Fixing document format issues...")
    print("-" * 60)

    for cat_dir in sorted(docs_path.iterdir()):
        if not cat_dir.is_dir():
            continue
        category = cat_dir.name
        cat_fixed = 0

        for md_file in cat_dir.glob('*.md'):
            if md_file.name == 'index.md':
                continue
            total += 1
            if fix_doc_format(str(md_file)):
                fixed += 1
                cat_fixed += 1
            else:
                errors += 1

        print(f"  {category}: {cat_fixed} fixed")

    print("\n" + "=" * 60)
    print(f"Format fix complete!")
    print(f"  Total docs: {total}")
    print(f"  Fixed: {fixed}")
    print(f"  Errors: {errors}")

if __name__ == '__main__':
    docs_dir = DISCOVER_NEWWIKI2_DOCS
    batch_fix(str(docs_dir))
