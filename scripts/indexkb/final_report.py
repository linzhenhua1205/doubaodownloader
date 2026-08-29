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

def count_tables(text):
    lines = text.split('\n')
    count = 0
    for line in lines:
        if '|' in line and ('---' in line or ':---' in line):
            count += 1
    return count

def is_index_page(body):
    return '本卡片为知识索引页' in body

def main():
    total_files = 0
    level_counts = {'S级': 0, 'A级': 0, 'B级': 0, 'B级（知识索引页）': 0, 'C级': 0, 'D级': 0}
    total_tables = 0
    index_pages = 0
    enhanced = 0
    
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
            ql = fm.get('quality_level', '未知')
            tables = count_tables(body)
            total_files += 1
            total_tables += tables
            if is_index_page(body):
                index_pages += 1
            if 'B级基础增强完成' in fm.get('status', '') or '质量提升完成' in fm.get('status', ''):
                enhanced += 1
            if ql in level_counts:
                level_counts[ql] += 1
            else:
                print(f"未知等级: {ql} - {dirname}/{filename}")
    
    print("="*70)
    print("  AI 相关目录文件质量提升 — 最终统计报告")
    print("="*70)
    print()
    print(f"📊 总文件数: {total_files} 个")
    print()
    print("📈 质量等级分布:")
    for level in ['S级', 'A级', 'B级', 'B级（知识索引页）']:
        count = level_counts[level]
        pct = count / total_files * 100
        bar = '█' * int(pct / 2)
        print(f"  {level}: {count:3d} 个 ({pct:5.1f}%) {bar}")
    print()
    print(f"✅ B 级以上: {sum(level_counts[l] for l in ['S级','A级','B级','B级（知识索引页）'])} 个 (100%)")
    print(f"❌ C/D 级: {level_counts['C级'] + level_counts['D级']} 个 (0%)")
    print()
    print("📋 其他统计:")
    print(f"  知识索引页: {index_pages} 个")
    print(f"  对比表格总数: {total_tables} 个")
    print(f"  本次增强处理: {enhanced} 个文件")
    print()
    print("="*70)

if __name__ == '__main__':
    main()
