#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path

DOC_DIR = r"h:\github\cowkb\discover\site\人文社会"
SKIP_FILES = {"index.md"}


def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def clean_duplicate_summary(text):
    pattern = r'(> \*\*概要\*\*: .+\n> \*\*关键词\*\*: .+\n)'
    matches = list(re.finditer(pattern, text))
    if len(matches) >= 2:
        first_match = matches[0]
        text = text[:first_match.end()] + text[matches[-1].end():]
    return text


def main():
    doc_files = sorted(Path(DOC_DIR).glob('*.md'))
    cleaned_count = 0
    
    for filepath in doc_files:
        if filepath.name in SKIP_FILES:
            continue
        
        text = load_file(filepath)
        original_text = text
        
        text = clean_duplicate_summary(text)
        
        if text != original_text:
            save_file(filepath, text)
            cleaned_count += 1
            print(f"✅ 已清理重复内容: {filepath.name}")
        else:
            print(f"ℹ️ 无需清理: {filepath.name}")
    
    print(f"\n📊 完成！共清理 {cleaned_count} 个文件")


if __name__ == "__main__":
    main()
