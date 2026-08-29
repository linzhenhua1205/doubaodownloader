#!/usr/bin/env python3
import json, os, re, random

BASE_DIR = r'h:\github\cowkb'
PROGRESS_FILE = os.path.join(BASE_DIR, '_optimize_progress.json')
DOCS_ROOT = os.path.join(BASE_DIR, 'discover', 'newwiki2', 'docs')
TARGET_DIRS = ['AI编程与开发工具', '企业管理与运营']
EXCLUDE_FILES = {'index.md', 'progress.md', 'task_plan.md', 'findings.md'}

with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
    progress = json.load(f)

print('='*70)
print('📊 1135文件全面深度优化 - 质量检查报告')
print('='*70)
print()
print(f'✅ 进度文件记录: {len(progress["processed"])} 个文件已处理')
print()

all_files = []
for subdir in TARGET_DIRS:
    dir_path = os.path.join(DOCS_ROOT, subdir)
    for root, dirs, files in os.walk(dir_path):
        for fname in sorted(files):
            if fname.endswith('.md') and fname not in EXCLUDE_FILES:
                fpath = os.path.join(root, fname)
                all_files.append({'path': fpath, 'dir': subdir, 'name': fname})

ai_total = sum(1 for f in all_files if f['dir'] == 'AI编程与开发工具')
emo_total = sum(1 for f in all_files if f['dir'] == '企业管理与运营')
ai_done = sum(1 for p in progress['processed'].keys() if 'AI编程' in p)
emo_done = sum(1 for p in progress['processed'].keys() if '企业管理' in p)

print('📁 按目录统计:')
print(f'  🅰️  AI编程与开发工具: {ai_done}/{ai_total} ({100*ai_done/max(1,ai_total):.1f}%)')
print(f'  🅱️  企业管理与运营:   {emo_done}/{emo_total} ({100*emo_done/max(1,emo_total):.1f}%)')
print(f'  📊 总计:             {ai_done+emo_done}/{len(all_files)} ({100*(ai_done+emo_done)/len(all_files):.1f}%)')
print()

checks = {'summary_block': 0, 'keywords_block': 0, 'source_tag': 0, 'toc_ok': 0, 'toc_need': 0, 'ref_section': 0, 'changelog': 0, 'v1_changelog': 0, 'dup_h1_fixed': 0}
sample_errors = []
random.seed(42)
sample_count = min(30, len(all_files))
samples = random.sample(all_files, sample_count)

for f in samples:
    fpath = f['path']
    with open(fpath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    lines = content.split('\n')
    line_count = len(lines)
    needs_toc = line_count > 100
    
    has_summary = bool(re.search(r'>\s*\*?\*?概要\*?\*?[:：]', content))
    has_keywords = bool(re.search(r'>\s*\*?\*?关键词\*?\*?[:：]', content))
    has_source = '[来源:' in content
    has_ref = '## 🔗 参考文件' in content
    has_cl = '## Changelog' in content
    has_v1 = 'v1.0' in content and '2026-07-29' in content
    has_toc = '## 📑 目录' in content
    
    h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
    no_dup_h1 = h1_count <= 1
    
    if has_summary: checks['summary_block'] += 1
    if has_keywords: checks['keywords_block'] += 1
    if has_source: checks['source_tag'] += 1
    if has_ref: checks['ref_section'] += 1
    if has_cl: checks['changelog'] += 1
    if has_v1: checks['v1_changelog'] += 1
    if no_dup_h1: checks['dup_h1_fixed'] += 1
    if needs_toc:
        checks['toc_need'] += 1
        if has_toc: checks['toc_ok'] += 1
    
    missing = []
    if not has_summary: missing.append('概要')
    if not has_keywords: missing.append('关键词')
    if not has_source: missing.append('来源标注')
    if needs_toc and not has_toc: missing.append('目录')
    if not has_ref: missing.append('参考文件')
    if not has_cl: missing.append('Changelog')
    if missing:
        sample_errors.append((f['name'], missing, f['dir']))

print(f'--- 抽样质量检查 ({sample_count}个随机样本) ---')
print(f'  概要blockquote:    {checks["summary_block"]:>2}/{sample_count} ({100*checks["summary_block"]/sample_count:.0f}%)')
print(f'  关键词blockquote:  {checks["keywords_block"]:>2}/{sample_count} ({100*checks["keywords_block"]/sample_count:.0f}%)')
print(f'  [来源:] 标注:      {checks["source_tag"]:>2}/{sample_count} ({100*checks["source_tag"]/sample_count:.0f}%)')
if checks['toc_need'] > 0:
    print(f'  >100行文件含目录: {checks["toc_ok"]:>2}/{checks["toc_need"]} ({100*checks["toc_ok"]/max(1,checks["toc_need"]):.0f}%)')
else:
    print(f'  >100行文件含目录: N/A (样本中无)')
print(f'  参考文件章节:     {checks["ref_section"]:>2}/{sample_count} ({100*checks["ref_section"]/sample_count:.0f}%)')
print(f'  Changelog章节:    {checks["changelog"]:>2}/{sample_count} ({100*checks["changelog"]/sample_count:.0f}%)')
print(f'  v1.0+日期正确:    {checks["v1_changelog"]:>2}/{sample_count} ({100*checks["v1_changelog"]/sample_count:.0f}%)')
print(f'  无重复H1标题:     {checks["dup_h1_fixed"]:>2}/{sample_count} ({100*checks["dup_h1_fixed"]/sample_count:.0f}%)')
print()

if sample_errors:
    print(f'⚠️  发现问题 ({len(sample_errors)}个):')
    for name, missing, d in sample_errors[:5]:
        tag = '🅰️' if 'AI编程' in d else '🅱️'
        print(f'  {tag} {name[:45]} 缺少: {", ".join(missing)}')
else:
    print('✅ 全部抽样检查通过！')
print()

print('--- 全局统计 ---')
total_noise = sum(v.get('noise_removed', 0) for v in progress['processed'].values())
toc_total = sum(1 for v in progress['processed'].values() if v.get('has_toc'))
minimal_total = sum(1 for v in progress['processed'].values() if v.get('is_minimal'))
avg_lines = sum(v.get('line_count', 0) for v in progress['processed'].values()) / max(1, len(progress['processed']))

print(f'  累计清理噪声词: {total_noise} 处')
print(f'  添加目录文件:   {toc_total} 个 (>100行自动加)')
print(f'  极简文件处理:   {minimal_total} 个 (<20行只加三条)')
print(f'  平均文件行数:   {avg_lines:.1f} 行')
print()

print('--- 高频关键词 TOP 15 ---')
from collections import Counter
all_kw = Counter()
for v in progress['processed'].values():
    kws = v.get('keywords', '')
    for kw in re.split(r'\s*·\s*', kws):
        kw = kw.strip()
        if kw and len(kw) >= 2:
            all_kw[kw] += 1
max_c = max(all_kw.values()) if all_kw else 1
for kw, c in all_kw.most_common(15):
    bar = '█' * (c * 30 // max_c)
    print(f'  {kw:<18s} {c:>4} {bar}')

print()
print('='*70)
print('✅ 质量检查完成')
print('='*70)
