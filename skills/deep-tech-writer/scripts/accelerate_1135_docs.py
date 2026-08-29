#!/usr/bin/env python3
"""
加速版批量处理脚本 - 一次准备N个批次的汇总信息，减少切换开销
用法:
  python accelerate_1135_docs.py prepare <起始批次号> <批次数>  # 准备N批汇总
  python accelerate_1135_docs.py apply <结果JSON>              # 应用多批结果
  python accelerate_1135_docs.py status                        # 查看状态
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = r'h:\github\cowkb'
PROGRESS_FILE = os.path.join(BASE_DIR, '_optimize_progress.json')
DOCS_ROOT = os.path.join(BASE_DIR, 'discover', 'newwiki2', 'docs')
SCRIPT_PATH = os.path.join(BASE_DIR, 'skills', 'deep-tech-writer', 'scripts', 'batch_optimize_1135_docs.py')

EXCLUDE_FILES = {'index.md', 'progress.md', 'task_plan.md', 'findings.md'}
TARGET_DIRS = ['AI编程与开发工具', '企业管理与运营']
BATCH_SIZE = 20


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'processed': {}, 'batches': {}, 'stats': {}}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def collect_all_files():
    all_files = []
    for subdir in TARGET_DIRS:
        dir_path = os.path.join(DOCS_ROOT, subdir)
        for root, dirs, files in os.walk(dir_path):
            for fname in sorted(files):
                if fname.endswith('.md') and fname not in EXCLUDE_FILES:
                    fpath = os.path.join(root, fname)
                    all_files.append({
                        'path': fpath,
                        'dir': subdir,
                        'name': fname,
                    })
    return all_files


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            return text[3:end_pos].strip(), text[end_pos+4:].strip()
    return "", text


def extract_title(fm, body, fname):
    if fm:
        m = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
        if m:
            t = m.group(1).strip().strip('**').strip()
            return re.sub(r'^[\[\(\<]', '', t)
    m = re.search(r'^#\s+(.+?)\s*$', body, re.MULTILINE)
    if m:
        t = m.group(1).strip().strip('**').strip()
        return re.sub(r'^[\[\(\<]', '', t)
    return Path(fname).stem


def extract_q_number(fname):
    m = re.search(r'(adt|emo)_q(\d+)', fname, re.IGNORECASE)
    if m:
        return f"{m.group(1)}_q{m.group(2)}"
    return None


def get_content_signature(body):
    """快速判断内容类型，辅助大模型生成"""
    sigs = []
    if '**所属分类：**' in body:
        sigs.append('规范文档')
    if '## 概述' in body and '## 核心概念解析' in body and '## 原理深度剖析' in body:
        sigs.append('框架模板')
    if '【来源：' in body or '**A' in body:
        sigs.append('问答素材')
    if 'SWE-bench' in body or 'pass@1' in body or '基准' in body:
        sigs.append('评测数据')
    if len(re.findall(r'\|.*\|.*\|', body)) > 5:
        sigs.append('多表格')
    if len(body) < 500 and '...' in body:
        sigs.append('占位框架')
    return ' / '.join(sigs) if sigs else '通用'


def prepare_batches(start_batch, num_batches):
    progress = load_progress()
    all_files = collect_all_files()
    unprocessed = [f for f in all_files if f['path'] not in progress['processed']]
    
    print(f"📋 总文件: {len(all_files)}  已处理: {len(all_files)-len(unprocessed)}  待处理: {len(unprocessed)}")
    
    master_batch = []
    
    for bi in range(num_batches):
        batch_num = start_batch + bi
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(unprocessed))
        
        if start >= len(unprocessed):
            print(f"⚠️  批次 {batch_num+1} 超出范围，停止")
            break
        
        batch_files = unprocessed[start:end]
        print(f"📦 准备批次 {batch_num+1}: 文件 {start+1}-{end} ({len(batch_files)}个)")
        
        for idx, f in enumerate(batch_files):
            with open(f['path'], 'r', encoding='utf-8') as fh:
                text = fh.read()
            
            fm, body = extract_frontmatter(text)
            title = extract_title(fm, body, f['name'])
            q_num = extract_q_number(f['name'])
            line_count = len(body.split('\n'))
            
            preview_lines = []
            chars = 0
            for line in body.split('\n'):
                s = line.strip()
                if not s or s.startswith('#') or s == '---':
                    continue
                preview_lines.append(line)
                chars += len(line)
                if chars >= 500:
                    break
            preview = '\n'.join(preview_lines)[:600]
            
            content_type = get_content_signature(body)
            
            master_batch.append({
                'batch_num': batch_num,
                'global_idx': start + idx,
                'local_idx': idx,
                'name': f['name'],
                'dir': f['dir'],
                'q_number': q_num,
                'title_short': title[:70],
                'line_count': line_count,
                'needs_toc': line_count > 100,
                'content_type': content_type,
                'preview': preview.replace('\n', ' ⏎ ')[:400] if preview else '(无正文预览)',
            })
    
    out_file = os.path.join(BASE_DIR, f'_accelerate_b{start_batch+1}-{start_batch+num_batches}.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(master_batch, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 汇总文件已保存: {out_file}")
    print(f"   共 {len(master_batch)} 个文件，跨 {num_batches} 个子批次")
    print()
    
    for i, item in enumerate(master_batch):
        mark_dir = '🅰️' if item['dir'] == 'AI编程与开发工具' else '🅱️'
        mark_toc = '📑' if item['needs_toc'] else '  '
        ct_tag = f"[{item['content_type']}]"
        print(f"  [{i:3d}] B{item['batch_num']+1}-{item['local_idx']:2d} {mark_dir} {mark_toc} L{item['line_count']:4d} | {item['name'][:45]}")
        print(f"            {ct_tag} {item['title_short'][:60]}")
        if i % 20 == 19:
            print()


def apply_results(result_file):
    progress = load_progress()
    all_files = collect_all_files()
    unprocessed_map = {}
    for f in all_files:
        if f['path'] not in progress['processed']:
            unprocessed_map[f['name']] = f['path']
    
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location("batch_module", SCRIPT_PATH)
    batch_module = module_from_spec(spec)
    spec.loader.exec_module(batch_module)
    
    total_ok = 0
    total_fail = 0
    total_noise = 0
    
    for key, res in results.items():
        if '_' in key and key.split('_')[0].isdigit():
            parts = key.split('_', 1)
            batch_num = int(parts[0])
            local_idx = int(parts[1])
        elif key.isdigit():
            batch_num = 0
            local_idx = int(key)
            continue
        else:
            name = key
            if name not in unprocessed_map:
                print(f"  ⚠️  已处理/找不到: {name}")
                continue
            fpath = unprocessed_map[name]
        name = res.get('name', '')
        if not name and '_' in key:
            continue
        if not name:
            print(f"  ⚠️  缺少文件名: key={key}")
            total_fail += 1
            continue
        if name not in unprocessed_map:
            print(f"  ⏭️  已处理或跳过: {name}")
            continue
        
        fpath = unprocessed_map[name]
        summary = res.get('summary', '').strip()
        keywords = res.get('keywords', '').strip()
        
        if not summary or not keywords:
            print(f"  ❌ 缺少概要/关键词: {name}")
            total_fail += 1
            continue
        
        with open(fpath, 'r', encoding='utf-8') as tf:
            ttxt = tf.read()
        tfm, tbody = batch_module.extract_frontmatter(ttxt)
        ttitle = batch_module.extract_title(tfm, tbody, name)
        tqnum = batch_module.extract_q_number(name)
        
        file_info = {
            'path': fpath,
            'dir': res.get('dir', os.path.dirname(fpath).split(os.sep)[-1]),
            'name': name,
            'is_minimal': len(tbody.split('\n')) < 20,
            'title': ttitle,
            'source_tag': f"题库 {tqnum}" if tqnum else "题库"
        }
        
        try:
            noise, lc, has_toc = batch_module.apply_optimization(file_info, summary, keywords, progress)
            total_ok += 1
            total_noise += noise
            toc_m = "📑" if has_toc else "  "
            n_m = f"🗑️{noise}" if noise > 0 else "    "
            print(f"  ✅ {toc_m} {n_m} {name[:45]}")
        except Exception as e:
            total_fail += 1
            print(f"  ❌ {name[:45]}: {e}")
            import traceback
            traceback.print_exc()
    
    progress.setdefault('stats', {})
    total_processed = len(progress['processed'])
    progress['stats']['summary'] = f"{total_processed}/{len(all_files)} 已完成"
    save_progress(progress)
    
    print()
    print("="*60)
    print(f"📊 本次应用: ✅ {total_ok}  ❌ {total_fail}  🗑️ 清理噪声{total_noise}处")
    print(f"🏁 总体进度: {len(progress['processed'])} / {len(all_files)} ({100*len(progress['processed'])/len(all_files):.1f}%)")
    print("="*60)


def status():
    progress = load_progress()
    all_files = collect_all_files()
    done = len(progress['processed'])
    print(f"📊 处理进度: {done} / {len(all_files)} ({100*done/len(all_files):.1f}%)")
    print(f"⏳ 剩余: {len(all_files) - done} 个文件")
    
    ai_done = sum(1 for p in progress['processed'].values() if 'AI编程' in str(p.get('path','')) or 'AI编程' in str(progress['processed'].get(list(progress['processed'].keys())[0], {}).get('path','')) if False)
    # 更精确统计
    ai_total = sum(1 for f in all_files if f['dir'] == 'AI编程与开发工具')
    emo_total = sum(1 for f in all_files if f['dir'] == '企业管理与运营')
    ai_done_n = sum(1 for p in progress['processed'].keys() if 'AI编程' in p)
    emo_done_n = sum(1 for p in progress['processed'].keys() if '企业管理' in p)
    print(f"  🅰️  AI编程: {ai_done_n}/{ai_total} ({100*ai_done_n/max(1,ai_total):.1f}%)")
    print(f"  🅱️  企业管理: {emo_done_n}/{emo_total} ({100*emo_done_n/max(1,emo_total):.1f}%)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == 'prepare' and len(sys.argv) >= 4:
        prepare_batches(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == 'apply' and len(sys.argv) >= 3:
        apply_results(sys.argv[2])
    elif cmd == 'status':
        status()
    else:
        print(__doc__)
