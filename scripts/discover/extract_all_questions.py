"""Extract all questions and answers from newwiki/ markdown files.

Supports multiple question formats:
- **Q1: ...** / **Q1. ...** - bold questions
- ## Q1 ... / ### Q1 ... - heading questions
- 1. ... / 一、... / (1) ... / 1) ... - numbered list questions
- **大模型必问Top10**: followed by numbered items
- **问题**: / **疑问**: - standalone question markers

Output: JSON file with all Q&A pairs, categorized by source file.
"""
import json
import re
import os
from pathlib import Path
from datetime import datetime

DISCOVER_NEWWIKI = Path(r"d:\123\cowkb\discover\newwiki")
OUTPUT_FILE = Path(r"d:\123\cowkb\discover\newwiki2\all_questions.json")

BOLD_Q_PATTERNS = [
    re.compile(r'\*\*Q(\d+):\s*(.+?)\*\*'),
    re.compile(r'\*\*Q(\d+)\.\s*(.+?)\*\*'),
    re.compile(r'\*\*Q:\s*(.+?)\*\*'),
]

HEADING_Q_PATTERNS = [
    re.compile(r'^##\s*Q(\d+):?\s*(.+)$'),
    re.compile(r'^###\s*Q(\d+):?\s*(.+)$'),
    re.compile(r'^####\s*Q(\d+):?\s*(.+)$'),
]

LIST_ITEM_PATTERNS = [
    re.compile(r'^(\d+)\.\s+(.+)$'),
    re.compile(r'^(\d+)\)\s+(.+)$'),
    re.compile(r'^\((\d+)\)\s+(.+)$'),
]

CHINESE_NUM_PATTERN = re.compile(r'^([一二三四五六七八九十]+)[、.．]\s+(.+)$')

QUESTION_KEYWORDS = ['问题', '疑问', '问答', '必问', 'FAQ', '常见问题', '核心问题']


def is_question_line(line):
    """Check if a line looks like a question."""
    line = line.strip()
    if not line:
        return False
    
    for pattern in BOLD_Q_PATTERNS + HEADING_Q_PATTERNS:
        if pattern.search(line):
            return True
    
    if LIST_ITEM_PATTERNS[0].match(line):
        match = LIST_ITEM_PATTERNS[0].match(line)
        text = match.group(2) if match else ''
        if len(text) > 10 and ('？' in text or '?' in text):
            return True
    
    if CHINESE_NUM_PATTERN.match(line):
        match = CHINESE_NUM_PATTERN.match(line)
        text = match.group(2) if match else ''
        if len(text) > 10 and ('？' in text or '?' in text):
            return True
    
    return False


def extract_questions_from_file(filepath):
    """Extract all Q&A pairs from a single markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []
    lines = content.split('\n')
    
    in_answer = False
    current_q_num = None
    current_q_text = None
    current_answer_lines = []
    question_counter = 0
    
    for i, line in enumerate(lines):
        matched = False
        
        for pattern in BOLD_Q_PATTERNS:
            match = pattern.search(line)
            if match:
                if in_answer and current_q_text:
                    questions.append({
                        'q_num': current_q_num,
                        'question': current_q_text.strip(),
                        'answer': '\n'.join(current_answer_lines).strip(),
                        'start_line': i - len(current_answer_lines),
                        'end_line': i - 1
                    })
                
                q_num = match.group(1) if len(match.groups()) > 1 else str(question_counter + 1)
                q_text = match.group(len(match.groups()))
                
                question_counter += 1
                current_q_num = q_num
                current_q_text = q_text
                current_answer_lines = []
                in_answer = True
                matched = True
                break
        
        if not matched:
            for pattern in HEADING_Q_PATTERNS:
                match = pattern.match(line)
                if match:
                    if in_answer and current_q_text:
                        questions.append({
                            'q_num': current_q_num,
                            'question': current_q_text.strip(),
                            'answer': '\n'.join(current_answer_lines).strip(),
                            'start_line': i - len(current_answer_lines),
                            'end_line': i - 1
                        })
                    
                    q_num = match.group(1)
                    q_text = match.group(2)
                    
                    question_counter += 1
                    current_q_num = q_num
                    current_q_text = q_text
                    current_answer_lines = []
                    in_answer = True
                    matched = True
                    break
        
        if not matched and in_answer:
            current_answer_lines.append(line)
    
    if in_answer and current_q_text:
        questions.append({
            'q_num': current_q_num,
            'question': current_q_text.strip(),
            'answer': '\n'.join(current_answer_lines).strip(),
            'start_line': len(lines) - len(current_answer_lines),
            'end_line': len(lines) - 1
        })

    return questions


def extract_list_questions(content):
    """Extract questions from numbered lists."""
    lines = content.split('\n')
    questions = []
    in_question_section = False
    section_title = ''
    q_counter = 0
    
    for i, line in enumerate(lines):
        line_clean = line.strip()
        
        if any(kw in line_clean for kw in QUESTION_KEYWORDS):
            if '**' in line_clean:
                in_question_section = True
                section_title = line_clean.replace('**', '')
                q_counter = 0
                continue
        
        if in_question_section:
            for pattern in LIST_ITEM_PATTERNS:
                match = pattern.match(line_clean)
                if match:
                    q_counter += 1
                    q_text = match.group(2)
                    questions.append({
                        'q_num': str(q_counter),
                        'question': q_text.strip(),
                        'answer': '',
                        'start_line': i,
                        'end_line': i,
                        'section': section_title
                    })
                    break
            
            if not line_clean.startswith(tuple(str(n) + '.' for n in range(1, 20))) and \
               not line_clean.startswith(tuple(str(n) + ')' for n in range(1, 20))) and \
               not line_clean.startswith(tuple('(' + str(n) + ')' for n in range(1, 20))) and \
               line_clean:
                if line_clean.startswith('#'):
                    in_question_section = False
    
    return questions


def main():
    md_files = sorted(DISCOVER_NEWWIKI.glob('*.md'))
    
    all_data = {
        'generated_at': datetime.now().isoformat(),
        'total_files': 0,
        'total_questions': 0,
        'categories': {}
    }

    for md_file in md_files:
        if md_file.name in ['index.md', 'findings.md', 'progress.md', 'task_plan.md',
                           'deep_quality_upgrade.py', 'final_enhancement_report.json',
                           'final_quality_report.json', 'frontmatter_add_results.json',
                           'frontmatter_cleanup_results.json', 'frontmatter_cleanup_v2_results.json',
                           'quality_assessment_results.json', 'quality_check_v2_results.json',
                           's_level_enhancement_stats.json', 'template_markers_cleanup_stats.json',
                           '深度增强质量复核报告.md', '质量提升成果总结.md']:
            continue
        
        category_name = md_file.stem
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        questions1 = extract_questions_from_file(md_file)
        questions2 = extract_list_questions(content)
        
        combined = {}
        for q in questions1:
            key = q['question'][:50]
            combined[key] = q
        for q in questions2:
            key = q['question'][:50]
            if key not in combined:
                combined[key] = q
        
        final_questions = list(combined.values())
        
        if final_questions:
            all_data['categories'][category_name] = {
                'file': str(md_file.relative_to(DISCOVER_NEWWIKI)),
                'question_count': len(final_questions),
                'questions': final_questions
            }
            all_data['total_files'] += 1
            all_data['total_questions'] += len(final_questions)
            
            print(f"✓ {md_file.name}: {len(final_questions)} questions")
        else:
            print(f"✗ {md_file.name}: no questions found")

    OUTPUT_FILE.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"\n=== Summary ===")
    print(f"Files processed: {all_data['total_files']}")
    print(f"Total questions: {all_data['total_questions']}")
    print(f"Output saved: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
