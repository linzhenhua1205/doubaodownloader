#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
from datetime import datetime

from config import DISCOVER_NEWWIKI, DISCOVER_NEWWIKI2

def extract_questions_from_file(filepath):
    questions = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return questions

    category = Path(filepath).stem

    patterns = [
        (r'^\*\*Q(\d+)[\.:：、]\s*(.+?)\*\*\s*$', 'bold_line'),
        (r'^###\s+Q(\d+)[\.:：、]\s*(.+?)\s*$', 'heading3'),
        (r'^##\s+Q(\d+)[\.:：、]\s*(.+?)\s*$', 'heading2'),
    ]

    seen = set()

    for pattern, fmt in patterns:
        for match in re.finditer(pattern, content, re.MULTILINE):
            q_num = int(match.group(1))
            q_title = match.group(2).strip()

            if q_title.endswith('**'):
                q_title = q_title[:-2].strip()

            key = (fmt, q_num, q_title[:50])
            if key in seen:
                continue
            seen.add(key)

            questions.append({
                'q_num': q_num,
                'title': q_title,
                'category': category,
                'source_file': str(filepath),
                'position': match.start(),
                'format': fmt
            })

    questions.sort(key=lambda x: (x['format'], x['q_num']))

    return questions

def extract_all_questions(source_dir, output_file):
    all_questions = []
    source_path = Path(source_dir)

    md_files = sorted(source_path.glob('*.md'))
    exclude_files = ['index.md', 'findings.md', 'progress.md', 'task_plan.md',
                     '深度增强质量复核报告.md', '质量提升成果总结.md',
                     'final_enhancement_report.json', 'final_stats.py']
    md_files = [f for f in md_files if f.name not in exclude_files and f.suffix == '.md']

    print(f"Found {len(md_files)} markdown files to process")

    for md_file in md_files:
        print(f"Processing: {md_file.name}")
        questions = extract_questions_from_file(md_file)
        all_questions.extend(questions)
        print(f"  Extracted {len(questions)} questions")

    all_questions.sort(key=lambda x: (x['category'], x['format'], x['q_num']))

    output_data = {
        'extracted_at': datetime.now().isoformat(),
        'total_count': len(all_questions),
        'categories': {},
        'format_breakdown': {},
        'questions': all_questions
    }

    categories = {}
    formats = {}
    for q in all_questions:
        cat = q['category']
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1

        fmt = q['format']
        if fmt not in formats:
            formats[fmt] = 0
        formats[fmt] += 1

    output_data['categories'] = categories
    output_data['format_breakdown'] = formats

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nTotal questions extracted: {len(all_questions)}")
    print(f"Saved to: {output_file}")
    print(f"\nFormat breakdown:")
    for fmt, count in sorted(formats.items()):
        print(f"  {fmt}: {count}")
    print("\nCategory breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    return all_questions

if __name__ == '__main__':
    source_dir = DISCOVER_NEWWIKI
    output_file = DISCOVER_NEWWIKI2 / "questions_list.json"
    extract_all_questions(str(source_dir), str(output_file))
