#!/usr/bin/env python3
"""
深度分析文档提取脚本 v2 — 基于目录/文件类型/行数的综合扫描
v2 改进: 不再依赖文件名关键词匹配，基于目录结构和文件特征判断

用法:
  python3 scripts/kb-stat/extract-deep-analysis-docs.py

输出:
  - knowledge/weekly-reports/07_kb_stat/deep-analysis-docs-metadata-v2.json
"""

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

WORKSPACE = Path(os.environ.get('COW_HOME', '/home/lzh/cow'))
KNOWLEDGE = WORKSPACE / 'knowledge'
OUTPUT_DIR = WORKSPACE / 'knowledge' / 'weekly-reports' / '07_kb_stat'


def load_git_file_dates_batch():
    """批量获取所有文件的首次提交日期（一次 git log 调用）"""
    dates = {}
    try:
        result = subprocess.run(
            ['git', 'log', '--diff-filter=A', '--name-only', '--format=%aI', '--', 'knowledge/'],
            capture_output=True, text=True, cwd=WORKSPACE, timeout=30
        )
        current_date = None
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            if 'T' in line and len(line) > 10:
                current_date = line[:10]
            elif line.endswith('.md'):
                dates[line] = current_date
    except Exception as e:
        print(f"  [warn] git log batch failed: {e}")
    return dates


def load_git_migrations():
    """批量获取目录变迁（rename 记录）"""
    migrations = []
    try:
        result = subprocess.run(
            ['git', 'log', '--name-status', '--diff-filter=R', '--format=%aI', '--since=2026-06-01', '--', 'knowledge/'],
            capture_output=True, text=True, cwd=WORKSPACE, timeout=30
        )
        current_date = None
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            if 'T' in line and len(line) > 10:
                current_date = line[:10]
            elif line.startswith('R'):
                parts = line.split('\t')
                if len(parts) >= 3:
                    migrations.append({
                        'date': current_date,
                        'from': parts[1],
                        'to': parts[2],
                    })
    except:
        pass
    return migrations


def is_deep_analysis_doc(rel_path, fname, lines, size):
    """判断是否为深度分析文档的核心规则"""
    
    # L1：硬排除
    if fname in ('index.md', 'log.md', 'README.md', 'TRACKING.md'):
        return False
    if lines < 50:
        return False
    if '/oldbak/' in rel_path or rel_path.endswith('/oldbak'):
        return False
    # bak 已迁至 tmp/bak/（2026-07-24），但保留检查以防残留引用
    if '/bak/' in rel_path:
        return False
    
    # L2：目录级判断（这些目录下所有文件都是深度分析）
    deep_dirs = [
        '/02_rd/', '/03_AI/', '/07_industry-research/',
        '/04_person/', '/05_tools/',
    ]
    for dd in deep_dirs:
        if dd in rel_path:
            return True
    
    # concepts/ 和 methodology/ 顶层目录
    if rel_path.startswith('knowledge/02_rd/00_shared/02_concepts/') or rel_path.startswith('knowledge/methodology/'):
        return True
    
    # 06_others/ 排除 oldbak 后保留
    if '/06_others/' in rel_path and '/oldbak/' not in rel_path:
        return True
    
    # L3：survey 专题模板（非日期文件）
    if '/01_survey/industry-research/' in rel_path:
        if not re.match(r'^\d{4}-\d{2}-\d{2}', fname):
            return True
    if '/01_survey/' in rel_path and not re.match(r'^\d{4}-\d{2}-\d{2}', fname):
        if fname not in ('README.md', 'TRACKING.md'):
            return True
    
    # L4：weekly-reports 排除日报
    if '/weekly-reports/' in rel_path:
        if '/00_daily/' in rel_path:
            return False
        return True
    
    return False


def extract_heading_hierarchy(content, max_lines=60):
    """提取标题层级结构"""
    lines = content.split('\n')
    hierarchy = []
    for i, line in enumerate(lines):
        if i > max_lines:
            break
        if line.startswith('# '):
            hierarchy.append(('h1', line.strip('# ').strip()))
        elif line.startswith('## '):
            hierarchy.append(('h2', line.strip('# ').strip()))
        elif line.startswith('### '):
            hierarchy.append(('h3', line.strip('# ').strip()))
        elif line.startswith('#### '):
            hierarchy.append(('h4', line.strip('# ').strip()))
    return hierarchy


def extract_cross_references(content, filepath):
    """提取文件引用的 knowledge/ 下其他 md 文件"""
    refs = set()
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)', content):
        target = m.group(2).split('#')[0].split('?')[0]
        text = m.group(1).strip()
        if '.md' in target and 'http' not in target:
            if 'knowledge/' in target:
                refs.add((text, target))
            elif not target.startswith('/'):
                # 相对路径转绝对
                rel_dir = os.path.dirname(filepath)
                full = os.path.normpath(os.path.join(rel_dir, target))
                if 'knowledge/' in full:
                    refs.add((text, full))
    return sorted(refs)


def extract_summary(content):
    """提取文档概要"""
    head = content[:2000]
    patterns = [
        r'>\s*\*{0,2}概要\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
        r'>\s*\*{0,2}摘要\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
        r'>\s*\*{0,2}概述\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
        r'>\s*Summary\s*[：:]\s*(.+?)(?:\n|$)',
        r'>\s*Abstract\s*[：:]\s*(.+?)(?:\n|$)',
        r'>\s*\*{0,2}关键词\*{0,2}\s*[：:]\s*(.+?)(?:\n|$)',
    ]
    for pat in patterns:
        m = re.search(pat, head, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def get_category(rel_path):
    """获取主题分类"""
    path = rel_path.replace('knowledge/', '', 1)
    sub_map = {
        '03_hardware': '🔧 硬件设计', '05_software': '💻 系统软件',
        '06_O&M': '🔍 运维管理', '08_chip': '🔬 芯片设计',
        '02_system': '🏗️ 系统架构', '00_rd-management': '📋 研发管理',
        '01_basic-concepts': '📚 基础概念', '04_fullstack': '🔄 全栈分析',
        '92_patent': '📜 专利布局', '09_supply-chain': '📦 供应链',
        '08_ai-engineering': '🤖 AI工程', '07_manufacturing': '🏭 制造工艺',
        '21_solution': '💡 解决方案',
    }
    if path.startswith('02_rd/'):
        sub = path.split('/')[1] if '/' in path else ''
        return sub_map.get(sub, f'🗂️ 02_rd/{sub}')
    if path.startswith('07_industry-research/'): return '🏭 行业调研'
    if path.startswith('03_AI/'): return '🤖 AI技术'
    if path.startswith('concepts/'): return '🧠 概念原理'
    if path.startswith('methodology/'): return '📐 方法论'
    if path.startswith('04_person/'): return '👤 个人发展'
    if path.startswith('05_tools/'): return '🛠️ 工具技能'
    if path.startswith('weekly-reports/'): return '📊 周报报告'
    if path.startswith('07_industry-research/03_server/'): return '🖥️ 服务器行业研究'
    if path.startswith('01_survey/'): return '📡 调研专题'
    if path.startswith('06_others/'): return '📂 其他'
    return '📂 其他'


def extract_date(fpath, fname):
    """从文件路径或名称提取日期"""
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', fname)
    if m: return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    for p in fpath.split('/'):
        m = re.search(r'(\d{4})-(\d{2})-(\d{2})', p)
        if m: return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def check_toc(content):
    """检查是否有目录结构"""
    return bool(re.search(r'[-*]\s*\[.*\]\(#.*\)', content[:3000]))


def check_ref_section(content):
    """检查末尾是否有参考区块"""
    tail = content[-2000:] if len(content) > 2000 else content
    return bool(re.search(r'(参考|来源|references|related)', tail, re.IGNORECASE))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("⚡ 批量加载 git 历史...")
    git_dates = load_git_file_dates_batch()
    migrations = load_git_migrations()
    print(f"   获得 {len(git_dates)} 个文件的创建日期, {len(migrations)} 条变迁记录")
    
    print("\n📂 扫描 knowledge/ 目录...")
    deep_docs = []
    stats = {'total': 0, 'idx_log': 0, 'small': 0, 'oldbak': 0, 'survey': 0, 'other_excluded': 0}
    
    for root, dirs, files in os.walk(KNOWLEDGE):
        if '/bak/' in root or root.endswith('/bak') or '/oldbak/' in root:
            dirs[:] = []
            continue
        for f in files:
            if not f.endswith('.md'):
                continue
            stats['total'] += 1
            fpath = os.path.join(root, f)
            rel_path = os.path.relpath(fpath, WORKSPACE)
            
            try:
                size = os.path.getsize(fpath)
                with open(fpath, 'r', errors='ignore') as fh:
                    content = fh.read()
                lines = content.count('\n') + 1
            except:
                continue
            
            if not is_deep_analysis_doc(rel_path, f, lines, size):
                if f in ('index.md', 'log.md', 'README.md', 'TRACKING.md'):
                    stats['idx_log'] += 1
                elif lines < 50:
                    stats['small'] += 1
                elif '/oldbak/' in rel_path or '/bak/' in rel_path:
                    stats['oldbak'] += 1
                elif re.match(r'^\d{4}-\d{2}-\d{2}', f) and '/01_survey/' in rel_path:
                    stats['survey'] += 1
                else:
                    stats['other_excluded'] += 1
                continue
            
            # 提取标题
            title_m = re.search(r'^# (.+)', content, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else ''
            
            summary = extract_summary(content)
            hierarchy = extract_heading_hierarchy(content)
            refs = extract_cross_references(content, rel_path)
            date = extract_date(rel_path, f)
            git_date = git_dates.get(rel_path)
            cat = get_category(rel_path)
            has_toc = check_toc(content)
            has_ref_section = check_ref_section(content)
            
            # 提取关键词（从 h2/h3 标题中取前 15 个）
            kws = [h for lv, h in hierarchy if lv in ('h2', 'h3')][:15]
            
            deep_docs.append({
                'path': rel_path, 'fname': f, 'title': title,
                'category': cat, 'lines': lines, 'size': size,
                'date': date, 'git_date': git_date,
                'summary': summary,
                'has_toc': has_toc, 'has_ref_section': has_ref_section,
                'keywords': kws, 'hierarchy': hierarchy[:25],
                'cross_refs': [(t, p) for t, p in refs[:30]],
                'cross_ref_count': len(refs),
            })
            
            if len(deep_docs) % 300 == 0:
                print(f"  已找到 {len(deep_docs)} 篇...")
    
    print(f"\n✅ 扫描完成!")
    print(f"  总扫描: {stats['total']} .md 文件")
    print(f"  深度分析文档: {len(deep_docs)} 篇")
    print(f"  排除 index/log: {stats['idx_log']}")
    print(f"  排除小文件: {stats['small']}")
    print(f"  排除 oldbak: {stats['oldbak']}")
    print(f"  排除 survey追踪: {stats['survey']}")
    print(f"  排除其他: {stats['other_excluded']}")
    
    # 分类统计
    by_cat = defaultdict(list)
    for doc in deep_docs:
        by_cat[doc['category']].append(doc)
    print(f"\n📊 分类统计:")
    for cat, docs in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        print(f"  {cat}: {len(docs)} 篇, {sum(d['lines'] for d in docs):,} 行")
    
    # 按日期排序
    deep_docs.sort(key=lambda d: d.get('date') or d.get('git_date') or '0000-00-00')
    
    # 保存
    metadata = {
        'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_scanned': stats['total'],
        'excluded': stats,
        'total_deep_docs': len(deep_docs),
        'total_lines': sum(d['lines'] for d in deep_docs),
        'docs': deep_docs,
        'migrations': migrations,
        'by_category': {cat: {'count': len(docs), 'lines': sum(d['lines'] for d in docs)}
                        for cat, docs in sorted(by_cat.items(), key=lambda x: -len(x[1]))},
    }
    
    out_path = OUTPUT_DIR / 'deep-analysis-docs-metadata-v2.json'
    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(metadata, fh, ensure_ascii=False, indent=1)
    
    print(f"\n💾 元数据已保存: {out_path}")
    print(f"总深度分析文档: {len(deep_docs)} 篇")
    print(f"总行数: {sum(d['lines'] for d in deep_docs):,}")
    
    return deep_docs, by_cat, migrations


if __name__ == '__main__':
    main()
