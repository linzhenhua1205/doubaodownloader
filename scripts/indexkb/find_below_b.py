import os
import re

BASE_DIR = r"h:\github\cowkb\discover\newwiki2"
INDEX_DIRS = ["AI-模型架构", "AI-训练微调", "AI-Agent", "ai-models"]

def parse_frontmatter(content):
    if not content.startswith('---'):
        return {}, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    fm_text = parts[1].strip()
    body = parts[2].lstrip()
    fm = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm, body

def estimate_word_count(text):
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    en_words = len(re.findall(r'[a-zA-Z]{3,}', text))
    code_lines = len(re.findall(r'^[a-zA-Z#].*[{}();]', text, re.MULTILINE))
    return cn_chars + en_words + code_lines * 2

def count_tables(text):
    lines = text.split('\n')
    count = 0
    for line in lines:
        if '|' in line and ('---' in line or ':---' in line):
            count += 1
    return count

def is_index_page(body):
    return '本卡片为知识索引页' in body

def assess_quality(body):
    words = estimate_word_count(body)
    tables = count_tables(body)
    h2 = len(re.findall(r'^## ', body, re.MULTILINE))
    is_index = is_index_page(body)
    
    if is_index:
        note_count = len(re.findall(r'^## \d+\.', body, re.MULTILINE))
        if tables >= 3 and h2 >= 5:
            return 'B级（知识索引页）'
        elif words >= 800 and (tables >= 2 or note_count >= 3):
            return 'B级（知识索引页）'
        elif note_count >= 10 and words >= 3000:
            return 'B级（知识索引页）'
        else:
            return 'C级（知识索引页）'
    else:
        if words >= 2500 and tables >= 3 and h2 >= 6:
            return 'S级'
        elif words >= 1800 and tables >= 2 and h2 >= 5:
            return 'A级'
        elif h2 >= 6 and tables >= 2:
            return 'B级'
        elif (words >= 800 and tables >= 1 and h2 >= 4) or (words >= 1200 and h2 >= 5):
            return 'B级'
        elif words >= 500 and h2 >= 2:
            return 'C级'
        else:
            return 'D级'

def main():
    for dirname in INDEX_DIRS:
        dirpath = os.path.join(BASE_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue
        for filename in sorted(os.listdir(dirpath)):
            if not filename.endswith('.md') or filename == 'index.md':
                continue
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            fm, body = parse_frontmatter(content)
            real_level = assess_quality(body)
            if real_level in ['D级', 'C级']:
                words = estimate_word_count(body)
                tables = count_tables(body)
                h2 = len(re.findall(r'^## ', body, re.MULTILINE))
                print(f"[{real_level}] {dirname}/{filename} ({words}字, {tables}表, {h2}h2)")

if __name__ == '__main__':
    main()
