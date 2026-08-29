import os
import re
import sys
from pathlib import Path

BASE_DIR = r"h:\github\cowkb\discover\newwiki2"

INDEX_DIRS = [
    "AI-模型架构",
    "AI-训练微调",
    "AI-Agent",
    "ai-models",
]

EXCLUDE_FILES = {
    'index.md', 'task_plan.md', 'findings.md', 'progress.md',
}

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
            key = key.strip()
            val = val.strip()
            if val.startswith('[') and val.endswith(']'):
                val = val[1:-1].split(',')
                val = [v.strip() for v in val]
            fm[key] = val
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

def count_sections(body):
    h1 = len(re.findall(r'^# ', body, re.MULTILINE))
    h2 = len(re.findall(r'^## ', body, re.MULTILINE))
    h3 = len(re.findall(r'^### ', body, re.MULTILINE))
    return h1, h2, h3

def is_index_page(body):
    return '本卡片为知识索引页' in body or '收录了相关主题的多条笔记摘要' in body

def has_substance(body):
    h1, h2, h3 = count_sections(body)
    tables = count_tables(body)
    words = estimate_word_count(body)
    
    has_structure = h2 >= 4
    has_content = words >= 800
    has_tables_or_code = tables >= 1 or '```' in body
    
    return has_structure and has_content and has_tables_or_code

def assess_quality(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm, body = parse_frontmatter(content)
    
    words = estimate_word_count(body)
    tables = count_tables(body)
    h1, h2, h3 = count_sections(body)
    is_index = is_index_page(body)
    substantial = has_substance(body)
    
    real_level = 'C级'
    
    if is_index:
        note_count = len(re.findall(r'^## \d+\.', body, re.MULTILINE))
        if tables >= 3 and h2 >= 5:
            real_level = 'B级（知识索引页）'
        elif words >= 800 and (tables >= 2 or note_count >= 3):
            real_level = 'B级（知识索引页）'
        elif note_count >= 10 and words >= 3000:
            real_level = 'B级（知识索引页）'
        elif note_count >= 5 and words >= 1000:
            real_level = 'B级（知识索引页）'
        else:
            real_level = 'C级（知识索引页）'
    else:
        if words >= 2500 and tables >= 3 and h2 >= 6:
            real_level = 'S级'
        elif words >= 1800 and tables >= 2 and h2 >= 5:
            real_level = 'A级'
        elif h2 >= 6 and tables >= 2:
            real_level = 'B级'
        elif (words >= 800 and tables >= 1 and h2 >= 4) or (words >= 1200 and h2 >= 5):
            real_level = 'B级'
        elif words >= 500 and h2 >= 2:
            real_level = 'C级'
        else:
            real_level = 'D级'
    
    self_level = fm.get('quality_level', fm.get('status', '未知'))
    
    level_map = {'D级': 0, 'C级': 1, 'C级（知识索引页）': 1, 
                 'B级': 2, 'B级（知识索引页）': 2, 'B级基础增强完成（知识索引页）': 2,
                 'A级': 3, 'S级': 4, '高质量': 4}
    
    def get_level_num(lvl_str):
        for k, v in level_map.items():
            if k in lvl_str:
                return v
        return -1
    
    self_num = get_level_num(self_level)
    real_num = level_map.get(real_level, -1)
    
    is_overrated = self_num > real_num + 1
    
    return {
        'file': filepath,
        'words': words,
        'tables': tables,
        'h2': h2,
        'is_index': is_index,
        'self_level': self_level,
        'real_level': real_level,
        'is_overrated': is_overrated,
    }

def main():
    all_files = []
    
    for dirname in INDEX_DIRS:
        dirpath = os.path.join(BASE_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue
        
        for filename in sorted(os.listdir(dirpath)):
            if not filename.endswith('.md'):
                continue
            if filename in EXCLUDE_FILES:
                continue
            
            filepath = os.path.join(dirpath, filename)
            info = assess_quality(filepath)
            info['rel_path'] = os.path.join(dirname, filename)
            all_files.append(info)
    
    below_b = [f for f in all_files if f['real_level'] in ['C级', 'D级', 'C级（知识索引页）']]
    overrated = [f for f in all_files if f['is_overrated']]
    
    print("\n" + "="*80)
    print("AI 相关文件质量状态总览（修正评估标准后）")
    print("="*80)
    print(f"总文件数: {len(all_files)}")
    
    for level in ['S级', 'A级', 'B级', 'B级（知识索引页）', 'C级', 'C级（知识索引页）', 'D级']:
        count = len([f for f in all_files if f['real_level'] == level])
        if count > 0:
            print(f"  {level}: {count} 个")
    
    print(f"\n未达 B 级: {len(below_b)} 个")
    print(f"自评虚高: {len(overrated)} 个")
    print("="*80)
    
    if below_b:
        print("\n📉 未达 B 级的文件：")
        for f in sorted(below_b, key=lambda x: x['words']):
            print(f"  [{f['real_level']}] {f['rel_path']} ({f['words']}等效字, {f['tables']}表, {f['h2']}个二级标题)")
    
    if overrated:
        print("\n⚠️  自评虚高的文件：")
        for f in overrated:
            print(f"  自评{f['self_level']} → 实际{f['real_level']}: {f['rel_path']}")

if __name__ == '__main__':
    main()
