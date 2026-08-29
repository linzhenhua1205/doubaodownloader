#!/usr/bin/env python3
"""
Directory Architecture Analyzer & Index Generator

Analyzes a knowledge directory, classifies files into MECE layers,
generates a structured index.md with:
  - Directory overview & statistics
  - MECE layered structure with file classification
  - Cross-domain coupling matrix (keyword-based)
  - Reading path recommendations
  - Decision framework index
  - Consistency guidelines
  - Known issues

Usage:
  python directory-architect.py <dir_path> [--output index.md] [--dry-run]
  python directory-architect.py <dir_path> --analyze-only
  python directory-architect.py <dir_path> --json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime


# ── 跳过的目录 ──────────────────────────────────────────────
SKIP_DIRS = {
    'bak', 'import-modules', 'node_modules', '.git',
    '.bak', 'oldbak', 'archive', 'archived'
}

# ── 分层规则：按文件名/标题关键词自动归类 ────────────────────
LAYER_RULES = [
    {
        'id': 'L1',
        'name': '总纲层',
        'name_en': 'Overview',
        'icon': '📚',
        'description': '系统级总纲、跨域框架、设计方法论',
        'keywords_title': ['核心', '总纲', '系统观', '方法论', '架构总览', '全景'],
        'keywords_filename': ['core', 'overview', 'methodology', '02-core'],
    },
    {
        'id': 'L2',
        'name': '专题概述层',
        'name_en': 'Topic Overview',
        'icon': '🗂️',
        'description': '各领域高层概览——是什么、为什么、怎么选',
        'keywords_title': ['专题', '概述', '扩充版', '行业趋势', '国产化', '供应链', '研发流程'],
        'keywords_filename': [
            '03-', '05-', '08-', '09-', '10-', '12-', '13-', '14-', '15-',
            'interconnect', 'cooling', 'power', 'thermal', 'rack',
        ],
    },
    {
        'id': 'L3',
        'name': '设计指南层',
        'name_en': 'Design Guide',
        'icon': '📐',
        'description': '详细设计指南——怎么做、选型、常见坑',
        'keywords_title': ['设计指南', '设计规范', '深潜', '剖析', '系统设计', '设计方案'],
        'keywords_filename': [
            'design-guide', 'deep-dive', 'deep-analysis',
            '16-', '17-', '18-', '19-', '20-', '21-', '23-', '24-',
            '25-', '26-', '27-', '28-', '29-', '30-', '31-', '32-',
            'standards', 'guide', 'ddr5', 'emc', 'esd', 'gpio',
            'i2c', 'clock', 'usb', 'pcie', 'connector',
        ],
    },
    {
        'id': 'L4',
        'name': '审查/Checklist 层',
        'name_en': 'Review & Checklist',
        'icon': '✅',
        'description': '各阶段审查清单——确保不漏项、跨域不脱节',
        'keywords_title': ['checklist', 'Checklist', '审查', '互审', '评审'],
        'keywords_filename': [
            'checklist', 'review', '33-', '34-', '35-',
        ],
    },
    {
        'id': 'L5',
        'name': '深度分析层',
        'name_en': 'Deep Analysis',
        'icon': '🔬',
        'description': '特定主题深度技术分析——前沿技术、架构权衡',
        'keywords_title': ['深度解读', '深度分析', '权衡分析', '规范分析'],
        'keywords_filename': [
            'deep-dive', 'spec-analysis', 'tradeoff', 'gpu-clk',
            'ocp-ubb',
        ],
    },
]

# ── 归档目录（L6 归档素材层）──────────────────────────────
ARCHIVE_DIR_PREFIX = '_'

# ── 领域关键词（用于关联矩阵）───────────────────────────────
DOMAIN_KEYWORDS = {
    '互联': ['interconnect', 'pcie', 'nvlink', 'serdes', 'topology', '互联', '拓扑', '链路', '接口', '连接器', '线缆', 'usb'],
    '供电': ['power', 'vr', 'level-shifter', '供电', '电源', '时序', '电压', '电流'],
    '散热': ['cooling', 'thermal', 'liquid', '散热', '液冷', '风冷', '热'],
    '信号': ['signal', 'si', 'integrity', '眼图', '信号', '高速'],
    '结构': ['mechanical', 'structure', 'chassis', 'rack', '结构', '机械', '机箱', '机柜'],
    'EMC': ['emc', 'esd', '电磁', '静电'],
    '时钟': ['clock', 'clk', '时钟', 'pll'],
    '内存': ['ddr', 'memory', '内存'],
    'DFX': ['dfx', 'dfm', 'dft', 'dfa', '可测试', '可制造', '可装配'],
    '管理': ['i2c', 'gpio', 'management', 'cpld', 'bmc', '管理', '调试', 'debug'],
}


# ── 工具函数 ──────────────────────────────────────────────

def extract_title(filepath: Path) -> str:
    """Extract H1 title from a markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
    except Exception:
        pass
    return filepath.stem


def extract_summary(filepath: Path, max_len: int = 80) -> str:
    """Extract a one-line summary from a markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_header = True
        for line in lines[:30]:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('#'):
                continue
            if stripped.startswith('>'):
                continue
            if stripped.startswith('---'):
                in_header = not in_header
                continue
            if stripped.startswith('|'):
                continue
            if re.match(r'^\d+[\.、]', stripped):
                continue
            if stripped.startswith('##'):
                break
            if in_header:
                if stripped.startswith('>'):
                    continue
            # Clean markdown
            clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', stripped)
            clean = re.sub(r'[#*`>]', '', clean).strip()
            if clean and len(clean) > 10:
                if len(clean) > max_len:
                    clean = clean[:max_len] + '…'
                return clean
    except Exception:
        pass
    return ''


def extract_header_metadata(filepath: Path) -> dict:
    """Extract metadata from the header section (first 15 lines)."""
    meta = {
        'has_positioning': False,
        'has_related': False,
        'has_version': False,
        'related_docs': [],
    }
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i > 20:
                    break
                stripped = line.strip()
                if '定位' in stripped or 'Position' in stripped:
                    meta['has_positioning'] = True
                if '关联' in stripped or 'Related' in stripped or 'refer' in stripped.lower():
                    meta['has_related'] = True
                if '版本' in stripped or 'version' in stripped.lower() or '更新' in stripped:
                    meta['has_version'] = True
                # Extract linked files from header
                if stripped.startswith('>') and ('[' in stripped and '](' in stripped):
                    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', stripped)
                    for text, url in links:
                        if url.endswith('.md') and not url.startswith('http'):
                            meta['related_docs'].append(url)
    except Exception:
        pass
    return meta


def count_lines(filepath: Path) -> int:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def classify_layer(filename: str, title: str) -> str:
    """Classify a file into a layer based on filename and title."""
    fname_lower = filename.lower()
    title_lower = title.lower()

    for rule in LAYER_RULES:
        for kw in rule['keywords_filename']:
            if kw.lower() in fname_lower:
                return rule['id']
        for kw in rule['keywords_title']:
            if kw.lower() in title_lower:
                return rule['id']
    return 'L5'  # default to deep analysis if unsure


def detect_domains(filepath: Path, title: str, summary: str) -> list:
    """Detect which domains a file covers (for coupling matrix)."""
    content = title + ' ' + summary
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content += ' ' + f.read(2000)  # read first 2KB
    except Exception:
        pass
    content_lower = content.lower()

    domains = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw.lower() in content_lower)
        if count >= 2:  # at least 2 keyword hits
            domains.append((domain, count))
    domains.sort(key=lambda x: x[1], reverse=True)
    return [d[0] for d in domains[:3]]  # top 3 domains


# ── 主分析函数 ────────────────────────────────────────────

def analyze_directory(dir_path: Path) -> dict:
    """Analyze a directory and return structured data."""
    all_files = []
    subdirs = []
    archive_files = []

    for item in sorted(dir_path.iterdir()):
        if item.is_dir():
            if item.name.startswith(ARCHIVE_DIR_PREFIX):
                # Archive directory - collect files
                arch_files = []
                for f in sorted(item.rglob('*.md')):
                    if f.name == 'index.md':
                        continue
                    rel = f.relative_to(dir_path)
                    arch_files.append({
                        'path': str(rel),
                        'filename': f.name,
                        'title': extract_title(f),
                        'summary': extract_summary(f),
                        'lines': count_lines(f),
                        'size_kb': round(f.stat().st_size / 1024, 1),
                    })
                archive_files.append({
                    'name': item.name,
                    'path': item.name,
                    'files': arch_files,
                    'file_count': len(arch_files),
                    'has_index': (item / 'index.md').exists(),
                })
            elif item.name in SKIP_DIRS:
                continue
            else:
                subdirs.append(item.name)
        elif item.suffix == '.md' and item.name not in ('index.md', 'log.md'):
            filepath = item
            title = extract_title(filepath)
            summary = extract_summary(filepath)
            layer = classify_layer(item.name, title)
            meta = extract_header_metadata(filepath)
            domains = detect_domains(filepath, title, summary)
            all_files.append({
                'path': item.name,
                'filename': item.name,
                'title': title,
                'summary': summary,
                'layer': layer,
                'lines': count_lines(filepath),
                'size_kb': round(filepath.stat().st_size / 1024, 1),
                'has_positioning': meta['has_positioning'],
                'has_related': meta['has_related'],
                'has_version': meta['has_version'],
                'domains': domains,
            })

    # Group by layer
    layers = defaultdict(list)
    for f in all_files:
        layers[f['layer']].append(f)

    # Compute consistency stats
    total = len(all_files)
    with_pos = sum(1 for f in all_files if f['has_positioning'])
    with_rel = sum(1 for f in all_files if f['has_related'])
    with_ver = sum(1 for f in all_files if f['has_version'])

    # Compute domain coupling matrix
    domain_counts = defaultdict(int)
    for f in all_files:
        for d in f['domains']:
            domain_counts[d] += 1

    coupling = {}
    for f in all_files:
        doms = f['domains']
        for i, d1 in enumerate(doms):
            for d2 in doms[i+1:]:
                key = tuple(sorted([d1, d2]))
                coupling[key] = coupling.get(key, 0) + 1

    # Decision frameworks found in files
    framework_keywords = [
        '决策', '选型', '权衡', '框架', 'checklist', '决策树',
        '原则', '方法论', '流程', '路径',
    ]
    decision_frameworks = []
    for f in all_files:
        title_lower = f['title'].lower()
        for kw in framework_keywords:
            if kw in title_lower:
                decision_frameworks.append(f)
                break

    return {
        'dir_path': str(dir_path),
        'dir_name': dir_path.name,
        'total_files': total,
        'subdirs': subdirs,
        'archive_dirs': archive_files,
        'files': all_files,
        'layers': dict(layers),
        'layer_order': [r['id'] for r in LAYER_RULES],
        'layer_info': {r['id']: r for r in LAYER_RULES},
        'consistency': {
            'total': total,
            'with_positioning': with_pos,
            'with_related': with_rel,
            'with_version': with_ver,
            'pct_positioning': round(with_pos / total * 100, 1) if total else 0,
            'pct_related': round(with_rel / total * 100, 1) if total else 0,
            'pct_version': round(with_ver / total * 100, 1) if total else 0,
        },
        'domain_counts': dict(domain_counts),
        'coupling': {f"{k[0]}↔{k[1]}": v for k, v in coupling.items()},
        'decision_frameworks': decision_frameworks,
    }


# ── Index.md 生成 ────────────────────────────────────────

def generate_index_md(data: dict) -> str:
    """Generate a comprehensive index.md from directory analysis data."""
    dir_name = data['dir_name']
    total = data['total_files']
    archive_count = sum(d['file_count'] for d in data['archive_dirs'])
    grand_total = total + archive_count

    lines = []

    # ── 标题与元数据 ──
    lines.append(f"# 📂 {dir_name} 知识目录")
    lines.append("")
    lines.append(f"> **文件数**: {grand_total} 篇（根目录 {total} + 归档 {archive_count}）")
    lines.append(f"> **子目录**: {len(data['subdirs']) + len(data['archive_dirs'])} 个")
    lines.append(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"> **分析工具**: directory-architect.py")
    lines.append("")

    # ── 目录导航 ──
    lines.append("---")
    lines.append("")
    lines.append("## 📑 目录")
    lines.append("")
    sections = [
        ("1 整体架构图", "#1-整体架构图"),
        ("2 MECE 分层结构", "#2-mece-分层结构"),
        ("3 跨领域关联矩阵", "#3-跨领域关联矩阵"),
        ("4 推荐阅读路径", "#4-推荐阅读路径"),
        ("5 核心参考速查", "#5-核心参考速查"),
        ("6 决策框架索引", "#6-决策框架索引"),
        ("7 一致性评估与规范", "#7-一致性评估与规范"),
        ("8 变更记录", "#8-变更记录"),
    ]
    for name, anchor in sections:
        lines.append(f"- [{name}]({anchor})")

    # Layer sections
    for layer_id in data['layer_order']:
        if layer_id not in data['layers']:
            continue
        info = data['layer_info'][layer_id]
        lines.append(f"  - [{layer_id} {info['name']}](#{layer_id}-{info['name']})")

    lines.append("")

    # ── 1 整体架构图 ──
    lines.append("---")
    lines.append("")
    lines.append("## 1 整体架构图")
    lines.append("")
    lines.append("```")
    lines.append(f"         ┌──────────────────────────────┐")
    lines.append(f"         │  L1 总纲层                   │")
    lines.append(f"         │  ({len(data['layers'].get('L1', []))} 文件)                 │")
    lines.append(f"         └──────────────┬───────────────┘")
    lines.append(f"                        ↓")
    lines.append(f"         ┌──────────────────────────────┐")
    lines.append(f"         │  L2 专题概述层               │")
    lines.append(f"         │  ({len(data['layers'].get('L2', []))} 文件)                 │")
    lines.append(f"         └──────────────┬───────────────┘")
    lines.append(f"                        ↓")
    lines.append(f"         ┌──────────────────────────────┐")
    lines.append(f"         │  L3 设计指南层               │")
    lines.append(f"         │  ({len(data['layers'].get('L3', []))} 文件)                 │")
    lines.append(f"         └──────────────┬───────────────┘")
    lines.append(f"                        ↓")
    lines.append(f"         ┌──────────────────────────────┐")
    lines.append(f"         │  L4 审查/Checklist 层        │")
    lines.append(f"         │  ({len(data['layers'].get('L4', []))} 文件)                 │")
    lines.append(f"         └──────────────┬───────────────┘")
    lines.append(f"                        ↓")
    lines.append(f"         ┌──────────────────────────────┐")
    lines.append(f"         │  L5 深度分析层               │")
    lines.append(f"         │  ({len(data['layers'].get('L5', []))} 文件)                 │")
    lines.append(f"         └──────────────┬───────────────┘")
    lines.append(f"                        ↓")
    lines.append(f"         ┌──────────────────────────────┐")
    lines.append(f"         │  L6 归档素材层               │")
    lines.append(f"         │  ({archive_count} 文件)                 │")
    lines.append(f"         └──────────────────────────────┘")
    lines.append("```")
    lines.append("")

    # ── 2 MECE 分层结构 ──
    lines.append("---")
    lines.append("")
    lines.append("## 2 MECE 分层结构")
    lines.append("")

    for layer_id in data['layer_order']:
        if layer_id not in data['layers']:
            continue
        info = data['layer_info'][layer_id]
        files = data['layers'][layer_id]
        lines.append(f"### {layer_id} {info['name']}")
        lines.append("")
        lines.append(f"> {info['icon']} **{info['description']}**")
        lines.append(f"> 文件数：{len(files)}")
        lines.append("")
        lines.append("| 文件 | 标题 | 摘要 | 大小 |")
        lines.append("|:-----|:-----|:-----|-----:|")
        for f in sorted(files, key=lambda x: x['filename']):
            summary = f['summary'] or '—'
            if len(summary) > 50:
                summary = summary[:50] + '…'
            lines.append(f"| [{f['filename']}]({f['path']}) | {f['title'][:40]} | {summary} | {f['size_kb']}KB |")
        lines.append("")

    # ── L6 归档素材层 ──
    if data['archive_dirs']:
        lines.append("### L6 归档素材层")
        lines.append("")
        lines.append("> 📦 历史素材、深度专题归档——作为参考资料，不直接用于设计落地")
        lines.append("")
        for arch in data['archive_dirs']:
            idx_link = f"[index.md]({arch['path']}/index.md)" if arch['has_index'] else '（无 index）'
            lines.append(f"- **[{arch['name']}/]({arch['path']}/)** — {arch['file_count']} 个文件，{idx_link}")
        lines.append("")

    # ── 3 跨领域关联矩阵 ──
    lines.append("---")
    lines.append("")
    lines.append("## 3 跨领域关联矩阵")
    lines.append("")
    lines.append("基于文件内容的关键词分析，识别各领域间的耦合程度：")
    lines.append("")

    domains = sorted(data['domain_counts'].keys(), key=lambda d: data['domain_counts'][d], reverse=True)
    if domains:
        # Build matrix
        n = len(domains)
        lines.append("| 领域 | " + " | ".join(domains[:8]) + " | 文件数 |")
        lines.append("|:-----|" + "|".join(["-----:" for _ in domains[:8]]) + "|-----:|")
        for i, d1 in enumerate(domains[:8]):
            row = [f"**{d1}**"]
            for j, d2 in enumerate(domains[:8]):
                if i == j:
                    row.append("█")
                else:
                    key = tuple(sorted([d1, d2]))
                    key_str = f"{key[0]}↔{key[1]}"
                    count = data['coupling'].get(key_str, 0)
                    if count >= 5:
                        row.append("███")
                    elif count >= 3:
                        row.append("██")
                    elif count >= 1:
                        row.append("█")
                    else:
                        row.append("·")
            row.append(str(data['domain_counts'][d1]))
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")
        lines.append("> 耦合强度：███ 强（≥5 共现） · ██ 中（≥3） · █ 弱（≥1）")
        lines.append("")

        # Top couplings
        top_couplings = sorted(data['coupling'].items(), key=lambda x: x[1], reverse=True)[:6]
        if top_couplings:
            lines.append("**最强耦合对**：")
            lines.append("")
            for pair, count in top_couplings:
                lines.append(f"- {pair} — {count} 个文件同时涉及")
            lines.append("")

    # ── 4 推荐阅读路径 ──
    lines.append("---")
    lines.append("")
    lines.append("## 4 推荐阅读路径")
    lines.append("")

    # Path A: Beginner
    lines.append("### 🛤️ 路径 A：入门路径（新人上手）")
    lines.append("")
    l1_files = data['layers'].get('L1', [])
    l2_files = data['layers'].get('L2', [])
    l4_files = data['layers'].get('L4', [])

    path_a = []
    if l1_files:
        path_a.append(l1_files[0])
    for f in l2_files[:3]:
        path_a.append(f)
    if l2_files:
        # pick first overview file
        for f in l2_files:
            if any(kw in f['filename'].lower() for kw in ['03', 'interconnect', '互联']):
                if f not in path_a:
                    path_a.append(f)
                break

    if path_a:
        for i, f in enumerate(path_a):
            connector = "↓" if i < len(path_a) - 1 else "↓"
            lines.append(f"{i+1}. [{f['title'][:40]}]({f['path']})")
        lines.append("")

    # Path B: Deep dive
    lines.append("### 🔬 路径 B：深潜路径（专家方向）")
    lines.append("")
    l3_files = data['layers'].get('L3', [])
    l5_files = data['layers'].get('L5', [])
    path_b = l3_files[:4] + l5_files[:2]
    if path_b:
        for i, f in enumerate(path_b):
            lines.append(f"{i+1}. [{f['title'][:40]}]({f['path']})")
        lines.append("")

    # Path C: Project flow
    lines.append("### 📋 路径 C：项目实战（从需求到出图）")
    lines.append("")
    path_c = []
    # requirement → overview → design guides → review checklists
    if l1_files:
        path_c.append(l1_files[0])
    for f in l4_files:
        if 'hld' in f['filename'].lower() or '概要' in f['title']:
            path_c.append(f)
            break
    for f in l3_files[:3]:
        path_c.append(f)
    for f in l4_files:
        if 'review' in f['filename'].lower() or '审查' in f['title']:
            path_c.append(f)
            break
    if path_c:
        for i, f in enumerate(path_c):
            lines.append(f"{i+1}. [{f['title'][:40]}]({f['path']})")
        lines.append("")

    # ── 5 核心参考速查 ──
    lines.append("---")
    lines.append("")
    lines.append("## 5 核心参考速查")
    lines.append("")

    # Largest files = most comprehensive
    largest = sorted(data['files'], key=lambda x: x['lines'], reverse=True)[:5]
    lines.append("### 最详尽文档（按行数）")
    lines.append("")
    lines.append("| 文件 | 行数 | 大小 |")
    lines.append("|:-----|-----:|-----:|")
    for f in largest:
        lines.append(f"| [{f['title'][:40]}]({f['path']}) | {f['lines']} | {f['size_kb']}KB |")
    lines.append("")

    # Checklist files
    if l4_files:
        lines.append("### Checklist 汇总")
        lines.append("")
        for f in sorted(l4_files, key=lambda x: x['filename']):
            lines.append(f"- [{f['title'][:50]}]({f['path']})")
        lines.append("")

    # ── 6 决策框架索引 ──
    lines.append("---")
    lines.append("")
    lines.append("## 6 决策框架索引")
    lines.append("")
    lines.append("本知识库中包含的可直接用于设计评审和方案选择的决策框架：")
    lines.append("")

    if data['decision_frameworks']:
        lines.append("| 决策框架 | 所在文件 | 层级 |")
        lines.append("|:---------|:---------|:----:|")
        for f in data['decision_frameworks']:
            lines.append(f"| {f['title'][:40]} | [{f['filename']}]({f['path']}) | {f['layer']} |")
        lines.append("")
    else:
        lines.append("_暂未识别到明确的决策框架文档_")
        lines.append("")

    # ── 7 一致性评估与规范 ──
    lines.append("---")
    lines.append("")
    lines.append("## 7 一致性评估与规范")
    lines.append("")

    cons = data['consistency']
    lines.append("### 7.1 头部元数据一致性")
    lines.append("")
    lines.append("| 指标 | 已具备 | 占比 |")
    lines.append("|:-----|------:|-----:|")
    lines.append(f"| 定位说明 | {cons['with_positioning']}/{cons['total']} | {cons['pct_positioning']}% |")
    lines.append(f"| 关联文档 | {cons['with_related']}/{cons['total']} | {cons['pct_related']}% |")
    lines.append(f"| 版本/日期 | {cons['with_version']}/{cons['total']} | {cons['pct_version']}% |")
    lines.append("")

    lines.append("### 7.2 交叉引用约定")
    lines.append("")
    lines.append("每个文件应在头部引用块中包含：")
    lines.append("1. **定位** — 本文在知识体系中的位置")
    lines.append("2. **范围** — 覆盖什么、不覆盖什么")
    lines.append("3. **关联文档** — 上下游及相关文件链接")
    lines.append("4. **版本/日期** — 便于追踪更新")
    lines.append("")

    lines.append("### 7.3 内容分层原则")
    lines.append("")
    lines.append("为避免重复和保证 MECE，内容按以下规则分层：")
    lines.append("")
    lines.append("| 层级 | 粒度 | 详细程度 | 典型读者 |")
    lines.append("|:-----|:-----|:---------|:---------|")
    for r in LAYER_RULES:
        lines.append(f"| {r['id']} {r['name']} | — | — | — |")
    if data['archive_dirs']:
        lines.append("| L6 归档素材 | 原始级 | 历史资料+原始数据 | 研究员/归档 |")
    lines.append("")
    lines.append("> **核心原则**：上层讲\"为什么\"和\"选什么\"，下层讲\"怎么做\"。上层引用下层做深入，下层引用上层做上下文。")
    lines.append("")

    lines.append("### 7.4 已知问题与待完善")
    lines.append("")
    issues = []
    if cons['pct_positioning'] < 80:
        issues.append(f"部分文件（{cons['total'] - cons['with_positioning']} 个）缺少「定位」说明")
    if cons['pct_related'] < 70:
        issues.append(f"部分文件（{cons['total'] - cons['with_related']} 个）缺少「关联文档」交叉引用")
    if cons['pct_version'] < 80:
        issues.append(f"部分文件（{cons['total'] - cons['with_version']} 个）缺少版本/日期标记")
    if not issues:
        issues.append("暂无明显一致性问题 ✅")
    for issue in issues:
        lines.append(f"- [ ] {issue}")
    lines.append("")

    # ── 8 变更记录 ──
    lines.append("---")
    lines.append("")
    lines.append("## 8 变更记录")
    lines.append("")
    lines.append("| 日期 | 版本 | 变更 |")
    lines.append("|:----|:----|:-----|")
    lines.append(f"| {datetime.now().strftime('%Y-%m-%d')} | v1.0 | 由 directory-architect.py 自动生成：建立 MECE 分层架构、关联矩阵、阅读路径、决策框架索引 |")
    lines.append("")

    return "\n".join(lines)


# ── 主入口 ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Directory Architecture Analyzer & Index Generator')
    parser.add_argument('dir_path', help='Path to the knowledge directory')
    parser.add_argument('--output', '-o', help='Output file path (default: <dir>/index.md)')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze, don\'t generate index')
    parser.add_argument('--json', action='store_true', help='Output JSON instead of markdown')
    parser.add_argument('--dry-run', action='store_true', help='Generate but don\'t write file')
    parser.add_argument('--force', action='store_true', help='Overwrite existing index.md')
    args = parser.parse_args()

    dir_path = Path(args.dir_path).resolve()
    if not dir_path.is_dir():
        print(f"Error: {dir_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Analyze
    print(f"📊 Analyzing {dir_path}...")
    data = analyze_directory(dir_path)

    print(f"   根目录文件: {data['total_files']}")
    print(f"   归档文件: {sum(d['file_count'] for d in data['archive_dirs'])}")
    print(f"   子目录: {len(data['subdirs'])}")
    print(f"   归档目录: {len(data['archive_dirs'])}")

    # Print layer summary
    print()
    print("📂 MECE 分层：")
    for layer_id in data['layer_order']:
        if layer_id in data['layers']:
            info = data['layer_info'][layer_id]
            print(f"   {layer_id} {info['name']}: {len(data['layers'][layer_id])} 文件")
    if data['archive_dirs']:
        print(f"   L6 归档素材: {sum(d['file_count'] for d in data['archive_dirs'])} 文件")

    # Print consistency
    cons = data['consistency']
    print()
    print("✅ 一致性评估：")
    print(f"   定位说明: {cons['pct_positioning']}% ({cons['with_positioning']}/{cons['total']})")
    print(f"   关联文档: {cons['pct_related']}% ({cons['with_related']}/{cons['total']})")
    print(f"   版本日期: {cons['pct_version']}% ({cons['with_version']}/{cons['total']})")

    if args.analyze_only:
        return

    if args.json:
        # Convert non-serializable parts
        print("\n" + json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return

    # Generate index.md
    index_content = generate_index_md(data)

    output_path = Path(args.output) if args.output else dir_path / 'index.md'

    if args.dry_run:
        print(f"\n📝 DRY-RUN: Would generate {output_path} ({len(index_content)} chars)")
        print("--- Preview (first 500 chars) ---")
        print(index_content[:500])
        print("...")
        return

    if output_path.exists() and not args.force:
        print(f"\n⚠️  {output_path} already exists. Use --force to overwrite.")
        print("Use --dry-run to preview first.")
        sys.exit(1)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"\n✅ Generated: {output_path}")
    print(f"   Total size: {len(index_content)} chars")


if __name__ == '__main__':
    main()
