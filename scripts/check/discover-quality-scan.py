#!/usr/bin/env python3
"""
discover-quality-scan.py — discover 内容质量扫描 (sr-007 近似版)

实现 sr-007 §5 四维质量近似检测规则，生成 discover/report/ 质量报告。

功能:
  - T1 格式符合度: 五要素检查 + 禁止引用检测
  - T2 内容深度: 行数/字符数/空行比/模板比
  - T3 版本成熟度: Changelog + 更新日期 + 占位符
  - T4 内部一致性: 交叉链接 + 禁止引用 + 链接有效
  - 综合评分 + 四级分级 (⭐⭐⭐/⭐⭐/⭐/❌)
  - 输出 Markdown 报告 + JSON 详细数据

用法:
  python3 scripts/check/discover-quality-scan.py                           # 全量扫描
  python3 scripts/check/discover-quality-scan.py --dir discover/newwiki2/  # 指定目录
  python3 scripts/check/discover-quality-scan.py --threshold 60           # 自定义通过线
  python3 scripts/check/discover-quality-scan.py --json-only              # 仅输出 JSON
  python3 scripts/check/discover-quality-scan.py --sample 50              # 抽样 50 个
  python3 scripts/check/discover-quality-scan.py --report-dir discover/report/
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Tuple

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DISCOVER_DIR = REPO_ROOT / 'discover'
REPORT_DIR = REPO_ROOT / 'discover' / 'report'
TODAY = datetime.now(timezone.utc).strftime('%Y-%m-%d')
CURRENT_YEAR = datetime.now(timezone.utc).year

# ── T1: 五要素正则 ──
PAT_SUMMARY = re.compile(r'>\s*\*\*(概要|定位|Summary|Description)\*\*')
PAT_KEYWORDS = re.compile(r'>\s*\*\*关键词\*\*|>\s*\*\*Keywords?\*\*')
PAT_TOC = re.compile(r'##\s*[📑]?\s*目录|##\s*[📑]?\s*Table\s+of\s+Contents|##\s*TOC')
PAT_REFS = re.compile(r'##\s*(参考文件|参考资料|References?|参考)')
PAT_CLOG = re.compile(r'##\s*(Changelog|变更记录|更新历史|版本记录)')
PAT_SEPARATOR = re.compile(r'^---$', re.MULTILINE)
PAT_VERSION = re.compile(r'>\s*\*\*版本\*\*|>\s*\*\*Version?\*\*')
PAT_UPDATE = re.compile(r'>\s*\*\*更新\*\*|>\s*\*\*Update\s*[Dd]ate\*\*')
PAT_FORBIDDEN_IMPORT = re.compile(r'import/')
PAT_FORBIDDEN_BAK = re.compile(r'(?:knowledge/bak|tmp/bak)/')

# ── T2: 模板/索引模式 ──
TEMPLATE_PATTERNS = re.compile(
    r'^(#\s+(题目|标题|Title|Topic)'
    r'|(摘要|Abstract|概述|Overview)\s*$'
    r'|##\s+(引言|Introduction|背景|Background)'
    r'|\*\*版本\*\*.*\|\s*\*\*更新\*\*'
    r'|- \[ \]'
    r'|^(待完成|TODO|待补充|TBD)'
    r'|^\|.*\|$'
    r'|^>\s*\*\*)', re.MULTILINE
)
INDEX_PATTERNS = re.compile(r'^\s*[-*]\s*\[.+\]\(.+\)\s*$', re.MULTILINE)

# ── T3: 占位符 ──
PLACEHOLDER_PATTERNS = re.compile(r'待补充|TODO|TBD|待完成|[??]{3,}')

# ── T4: 内部链接 ──
LINK_KNOWLEDGE = re.compile(r'\]\(knowledge/[^)]+\)')


def read_file_safe(path: Path) -> Tuple[str, List[str], str]:
    """安全读取文件。返回 (raw_content, lines_list, error_or_empty)"""
    try:
        content = path.read_text(encoding='utf-8', errors='replace')
        lines = content.splitlines()
        return content, lines, ''
    except Exception as e:
        return '', [], f'读取失败: {e}'


def scan_t1(content: str, lines: List[str]) -> dict:
    """T1 格式符合度近似评分 (sr-007 §5.2)"""
    score = 0
    checks = {}

    # 1. 概要/定位 (15)
    has_summary = bool(PAT_SUMMARY.search(content))
    checks['summary'] = {'pass': has_summary, 'score': 15 if has_summary else 0}
    score += checks['summary']['score']

    # 2. 关键词 (10)
    has_keywords = bool(PAT_KEYWORDS.search(content))
    checks['keywords'] = {'pass': has_keywords, 'score': 10 if has_keywords else 0}
    score += checks['keywords']['score']

    # 3. TOC (15)
    has_toc = bool(PAT_TOC.search(content))
    checks['toc'] = {'pass': has_toc, 'score': 15 if has_toc else 0}
    score += checks['toc']['score']

    # 4. 参考文件 (15)
    has_refs = bool(PAT_REFS.search(content))
    checks['references'] = {'pass': has_refs, 'score': 15 if has_refs else 0}
    score += checks['references']['score']

    # 5. Changelog (15)
    has_clog = bool(PAT_CLOG.search(content))
    checks['changelog'] = {'pass': has_clog, 'score': 15 if has_clog else 0}
    score += checks['changelog']['score']

    # 6. 分隔线 (5)
    has_sep = bool(PAT_SEPARATOR.search(content))
    checks['separator'] = {'pass': has_sep, 'score': 5 if has_sep else 0}
    score += checks['separator']['score']

    # 7. 无禁止引用 (15)
    no_import = not PAT_FORBIDDEN_IMPORT.search(content)
    no_bak = not PAT_FORBIDDEN_BAK.search(content)
    forbidden_clean = no_import and no_bak
    checks['no_forbidden_refs'] = {'pass': forbidden_clean, 'score': 15 if forbidden_clean else 0}
    score += checks['no_forbidden_refs']['score']

    # 8. 版本+更新 (10)
    has_ver = bool(PAT_VERSION.search(content))
    has_upd = bool(PAT_UPDATE.search(content))
    has_version_info = has_ver and has_upd
    checks['version_info'] = {'pass': has_version_info, 'score': 10 if has_version_info else 0}
    score += checks['version_info']['score']

    return {'score': min(score, 100), 'checks': checks}


def scan_t2(content: str, lines: List[str]) -> dict:
    """T2 内容深度近似评分 (sr-007 §5.3)"""
    score = 0
    checks = {}

    total_lines = len(lines)
    non_empty = [l for l in lines if l.strip()]
    non_empty_count = len(non_empty)
    total_chars = len(content)

    # 1. 总行数 (40)
    if total_lines >= 500:
        line_score = 40
    elif total_lines >= 200:
        line_score = 25
    elif total_lines >= 50:
        line_score = 10
    else:
        line_score = 0
    checks['total_lines'] = {'value': total_lines, 'score': line_score}
    score += line_score

    # 2. 非空行占比 (20)
    empty_ratio = 1 - (non_empty_count / max(total_lines, 1))
    if empty_ratio <= 0.3:
        empty_score = 20
    elif empty_ratio <= 0.5:
        empty_score = 10
    else:
        empty_score = 0
    checks['non_empty_ratio'] = {'value': f'{1-empty_ratio:.0%}', 'score': empty_score}
    score += empty_score

    # 3. 有效字符数 (25)
    if total_chars >= 10000:
        char_score = 25
    elif total_chars >= 3000:
        char_score = 15
    elif total_chars >= 500:
        char_score = 5
    else:
        char_score = 0
    checks['total_chars'] = {'value': total_chars, 'score': char_score}
    score += char_score

    # 4. 模板行占比 (15)
    template_matches = TEMPLATE_PATTERNS.findall(content)
    # 使用 set 去重（findall 返回 groups 元组，取第一个非空元素）
    template_lines_count = len(set(m[0] if isinstance(m, tuple) else m for m in template_matches))
    template_ratio = template_lines_count / max(non_empty_count, 1)
    if template_ratio < 0.2:
        tpl_score = 15
    elif template_ratio < 0.4:
        tpl_score = 8
    else:
        tpl_score = 0
    checks['template_ratio'] = {'value': f'{template_ratio:.0%}', 'score': tpl_score}
    score += tpl_score

    return {'score': min(score, 100), 'checks': checks}


def scan_t3(content: str, lines: List[str]) -> dict:
    """T3 版本成熟度近似评分 (sr-007 §5.4)"""
    score = 0
    checks = {}

    # 1. Changelog 存在 (30)
    has_clog = bool(PAT_CLOG.search(content))
    checks['changelog_exists'] = {'pass': has_clog, 'score': 30 if has_clog else 0}
    score += checks['changelog_exists']['score']

    # 2. Changelog 条目数 (35)
    clog_entries = 0
    if has_clog:
        # 取 Changelog 之后的所有行，统计版本行 | 日期 |
        clog_match = PAT_CLOG.search(content)
        after_clog = content[clog_match.end():]
        clog_entries = len(re.findall(r'^\|.*\|.*\|', after_clog, re.MULTILINE))

    if clog_entries >= 3:
        entry_score = 35
    elif clog_entries >= 2:
        entry_score = 20
    elif clog_entries >= 1:
        entry_score = 10
    else:
        entry_score = 0
    checks['changelog_entries'] = {'value': clog_entries, 'score': entry_score}
    score += entry_score

    # 3. 最后一次更新年份 (20)
    # 从 Changelog 或头部版本日期提取
    year_matches = re.findall(r'20\d{2}', content)
    has_current_year = any(y == str(CURRENT_YEAR) for y in year_matches)
    has_last_year = any(y == str(CURRENT_YEAR - 1) for y in year_matches)

    if has_current_year:
        year_score = 20
    elif has_last_year:
        year_score = 10
    else:
        year_score = 0
    checks['recent_year'] = {'value': '当前年' if has_current_year else '去年' if has_last_year else '更早',
                             'score': year_score}
    score += year_score

    # 4. 无占位符 (15)
    placeholders = PLACEHOLDER_PATTERNS.findall(content)
    ph_count = len(placeholders)
    if ph_count == 0:
        ph_score = 15
    elif ph_count <= 3:
        ph_score = 5
    else:
        ph_score = 0
    checks['no_placeholders'] = {'value': ph_count, 'score': ph_score}
    score += ph_score

    return {'score': min(score, 100), 'checks': checks}


def scan_t4(content: str, lines: List[str], file_path: Path) -> dict:
    """T4 内部一致性近似评分 (sr-007 §5.5)"""
    score = 0
    checks = {}

    # 1. 交叉链接数 (30)
    links = LINK_KNOWLEDGE.findall(content)
    link_count = len(links)
    if link_count >= 5:
        link_score = 30
    elif link_count >= 2:
        link_score = 15
    elif link_count >= 1:
        link_score = 8
    else:
        link_score = 0
    checks['cross_links'] = {'value': link_count, 'score': link_score}
    score += link_score

    # 2. 无 import/ 引用 (20)
    no_import = not PAT_FORBIDDEN_IMPORT.search(content)
    checks['no_import_refs'] = {'pass': no_import, 'score': 20 if no_import else 0}
    score += checks['no_import_refs']['score']

    # 3. 无 bak/ 引用 (20)
    no_bak = not PAT_FORBIDDEN_BAK.search(content)
    checks['no_bak_refs'] = {'pass': no_bak, 'score': 20 if no_bak else 0}
    score += checks['no_bak_refs']['score']

    # 4. 内部链接有效性 (30)
    # 提取 knowledge/ 内部链接的目标路径
    valid_links = 0
    total_links = 0
    for link in links:
        total_links += 1
        # 提取路径: ](knowledge/...)
        target = re.search(r'\]\(knowledge/([^)]+)\)', link)
        if target:
            target_path = REPO_ROOT / 'knowledge' / target.group(1)
            if target_path.exists():
                valid_links += 1

    if total_links > 0:
        valid_ratio = valid_links / total_links
        if valid_ratio >= 0.8:
            link_valid_score = 30
        elif valid_ratio >= 0.5:
            link_valid_score = 15
        else:
            link_valid_score = 0
    else:
        link_valid_score = 0
    checks['link_validity'] = {
        'value': f'{valid_links}/{total_links}',
        'score': link_valid_score
    }
    score += link_valid_score

    return {'score': min(score, 100), 'checks': checks}


def evaluate_file(file_path: Path) -> dict:
    """对单个文件执行四维质量评估"""
    content, lines, error = read_file_safe(file_path)
    if error:
        return {'file': str(file_path), 'error': error,
                'level': 'ERROR', 'overall': 0}

    t1 = scan_t1(content, lines)
    t2 = scan_t2(content, lines)
    t3 = scan_t3(content, lines)
    t4 = scan_t4(content, lines, file_path)

    # 综合评分 (sr-007 §3.6)
    overall = (t1['score'] * 0.25 + t2['score'] * 0.35 +
               t3['score'] * 0.15 + t4['score'] * 0.25)

    # 等级映射 (8 级精细版, sr-007 §5.6 扩展)
    if overall >= 85:
        level = '⭐⭐⭐'
        sub_label = 'S-卓越'
    elif overall >= 75:
        level = '⭐⭐⭐'
        sub_label = 'A-优质'
    elif overall >= 65:
        level = '⭐⭐'
        sub_label = 'B-达标'
    elif overall >= 55:
        level = '⭐'
        sub_label = 'C-接近'
    elif overall >= 45:
        level = '⭐'
        sub_label = 'D-待提'
    elif overall >= 35:
        level = '⭐'
        sub_label = 'E-基础'
    elif overall >= 25:
        level = '❌'
        sub_label = 'F-薄弱'
    else:
        level = '❌'
        sub_label = 'G-废弃'

    # 综合等级标记: 分级+二级细分
    full_label = f'{level} {sub_label}'

    return {
        'file': str(file_path.relative_to(REPO_ROOT)),
        'level': level,
        'sub_label': sub_label,
        'full_label': full_label,
        'overall': round(overall, 1),
        't1': {'score': t1['score'], 'checks': t1['checks']},
        't2': {'score': t2['score'], 'checks': t2['checks']},
        't3': {'score': t3['score'], 'checks': t3['checks']},
        't4': {'score': t4['score'], 'checks': t4['checks']},
    }


def scan_directory(target_dir: Path, sample: int = 0) -> List[dict]:
    """扫描目录下的所有 .md 文件"""
    files = sorted(target_dir.rglob('*.md'))
    # 排除非内容文件: index.md, log.md, README.md
    files = [f for f in files if f.name not in ('index.md', 'log.md', 'README.md')]
    # 排除运营目录: plan/, process/, report/
    files = [f for f in files if not any(p in f.parts for p in ('plan', 'process', 'report'))]

    if sample > 0:
        import random
        random.seed(42)
        files = random.sample(files, min(sample, len(files)))

    results = []
    total = len(files)
    for i, fpath in enumerate(files, 1):
        result = evaluate_file(fpath)
        results.append(result)
        if i % 100 == 0:
            print(f"  📊 进度: {i}/{total}", file=sys.stderr)

    return results


def generate_report(results: List[dict], target_dir: str, threshold: float) -> str:
    """生成 Markdown 质量扫描报告 (sr-007 §7.1, 8 级精细版)"""

    # 8 级分层定义
    TIERS = [
        ('S-卓越', '⭐⭐⭐', 85, '可直接迁移 knowledge/'),
        ('A-优质', '⭐⭐⭐', 75, '少量修补后迁移'),
        ('B-达标', '⭐⭐', 65, '补元数据后迁移'),
        ('C-接近', '⭐', 55, '少量 AI 增强'),
        ('D-待提', '⭐', 45, '需 AI 增强管线'),
        ('E-基础', '⭐', 35, '需大幅增强/退回 import'),
        ('F-薄弱', '❌', 25, '重写或废弃'),
        ('G-废弃', '❌', 0, '直接废弃'),
    ]
    TIER_KEYS = [t[0] for t in TIERS]

    # 按 sub_label 分组
    sub_levels = {k: [] for k in TIER_KEYS}
    main_levels = {'⭐⭐⭐': [], '⭐⭐': [], '⭐': [], '❌': [], 'ERROR': []}

    for r in results:
        sl = r.get('sub_label', 'ERROR')
        if sl in sub_levels:
            sub_levels[sl].append(r)
        else:
            sub_levels.setdefault('ERROR', []).append(r)
        ml = r.get('level', 'ERROR')
        if ml in main_levels:
            main_levels[ml].append(r)
        else:
            main_levels['ERROR'].append(r)

    total = len(results)
    report = []
    report.append(f"# discover 内容质量扫描报告 — {TODAY}")
    report.append("")
    report.append(f"> **扫描范围**: `{target_dir}`")
    report.append(f"> **文件总数**: {total}")
    report.append(f"> **扫描时间**: {TODAY}")
    report.append("")

    # ── 概览仪表盘 ──
    report.append("## 📊 概览仪表盘")
    report.append("")

    def pct(c):
        return f"{c/total*100:.1f}%" if total > 0 else "0%"

    # 主分级
    report.append("### 主分级")
    report.append("")
    report.append("| 等级 | 数量 | 占比 | 建议动作 |")
    report.append("|:----|:----:|:----:|:---------|")
    report.append(f"| ⭐⭐⭐ 优质 | {len(main_levels['⭐⭐⭐'])} | {pct(len(main_levels['⭐⭐⭐']))} | 可直接/少量修补后迁移 |")
    report.append(f"| ⭐⭐ 达标 | {len(main_levels['⭐⭐'])} | {pct(len(main_levels['⭐⭐']))} | 补元数据后迁移 |")
    report.append(f"| ⭐ 待提升 | {len(main_levels['⭐'])} | {pct(len(main_levels['⭐']))} | 需 AI 增强管线 |")
    report.append(f"| ❌ 不合格 | {len(main_levels['❌'])} | {pct(len(main_levels['❌']))} | 重写/归档至 tmp/bak/ |")
    report.append("")

    # 8 级细分
    report.append("### 8 级细分")
    report.append("")
    report.append("| 子级 | Badge | 分数区间 | 数量 | 占比 | 累计占比 |")
    report.append("|:----:|:-----|:--------:|:----:|:----:|:--------:|")
    cumulative = 0
    for sl_key, badge, min_score, _ in TIERS:
        cnt = len(sub_levels[sl_key])
        cumulative += cnt
        report.append(f"| {sl_key} | {badge} | ≥{min_score} | {cnt} | {pct(cnt)} | {pct(cumulative)} |")
    report.append("")

    # ── S/A 级文件清单 ──
    top_tiers = [k for k in TIER_KEYS if k in ('S-卓越', 'A-优质')]
    top_files = []
    for k in top_tiers:
        top_files.extend(sub_levels[k])
    if top_files:
        report.append("## ⭐⭐⭐ 优质文件")
        report.append("")
        report.append("| # | 子级 | 文件 | 综合分 | T1 | T2 | T3 | T4 |")
        report.append("|:-:|:----:|:-----|:------:|:--:|:--:|:--:|:--:|")
        for i, r in enumerate(sorted(top_files, key=lambda x: -x['overall']), 1):
            report.append(f"| {i} | {r['sub_label']} | `{r['file']}` | {r['overall']} | "
                          f"{r['t1']['score']} | {r['t2']['score']} | {r['t3']['score']} | {r['t4']['score']} |")
        report.append("")

    # ── B 级文件清单 ──
    b_files = sub_levels.get('B-达标', [])
    if b_files:
        report.append(f"## ⭐⭐ B-达标文件（共 {len(b_files)} 个，列举全部）")
        report.append("")
        report.append("| # | 文件 | 综合分 | T1 | T2 | T3 | T4 | 主要缺失 |")
        report.append("|:-:|:-----|:------:|:--:|:--:|:--:|:--:|:---------|")
        for i, r in enumerate(sorted(b_files, key=lambda x: -x['overall']), 1):
            missing = []
            for dim_key in ['t1', 't2', 't3', 't4']:
                checks = r[dim_key]['checks']
                for ck, cv in checks.items():
                    if isinstance(cv, dict):
                        sc = cv.get('score', 0)
                        if sc == 0:
                            missing.append(ck)
            miss_str = ', '.join(missing[:6]) or '—'
            report.append(f"| {i} | `{r['file']}` | {r['overall']} | {r['t1']['score']} | "
                          f"{r['t2']['score']} | {r['t3']['score']} | {r['t4']['score']} | {miss_str} |")
        report.append("")

    # ── C/D/E 级抽样 ──
    for sl_key, badge, _, _ in TIERS:
        if sl_key not in ('C-接近', 'D-待提', 'E-基础'):
            continue
        files = sub_levels.get(sl_key, [])
        if not files:
            continue
        report.append(f"## {badge} {sl_key}（共 {len(files)} 个，列举前 10）")
        report.append("")
        report.append("| # | 文件 | 综合分 | T1 | T2 | T3 | T4 |")
        report.append("|:-:|:-----|:------:|:--:|:--:|:--:|:--:|")
        for i, r in enumerate(sorted(files, key=lambda x: -x['overall'])[:10], 1):
            report.append(f"| {i} | `{r['file']}` | {r['overall']} | {r['t1']['score']} | "
                          f"{r['t2']['score']} | {r['t3']['score']} | {r['t4']['score']} |")
        report.append("")

    # ── F/G 级（不合格） ──
    for sl_key, badge, _, _ in TIERS:
        if sl_key not in ('F-薄弱', 'G-废弃'):
            continue
        files = sub_levels.get(sl_key, [])
        if not files:
            continue
        report.append(f"## ❌ {sl_key}（共 {len(files)} 个，列举前 10）")
        report.append("")
        report.append("| # | 文件 | 综合分 | T1 | T2 | T3 | T4 |")
        report.append("|:-:|:-----|:------:|:--:|:--:|:--:|:--:|")
        for i, r in enumerate(sorted(files, key=lambda x: -x['overall'])[:10], 1):
            report.append(f"| {i} | `{r['file']}` | {r['overall']} | {r['t1']['score']} | "
                          f"{r['t2']['score']} | {r['t3']['score']} | {r['t4']['score']} |")
        report.append("")

    # ── 维度短板分析 ──
    report.append("## 📉 维度短板分析")
    report.append("")
    dim_avgs = {'T1': 0, 'T2': 0, 'T3': 0, 'T4': 0}
    for r in results:
        dim_avgs['T1'] += r['t1']['score']
        dim_avgs['T2'] += r['t2']['score']
        dim_avgs['T3'] += r['t3']['score']
        dim_avgs['T4'] += r['t4']['score']
    for k in dim_avgs:
        dim_avgs[k] = round(dim_avgs[k] / max(total, 1), 1)

    report.append("| 维度 | 平均分 | 满分 | 得分率 | 短板判定 |")
    report.append("|:----|:------:|:----:|:------:|:---------|")
    for dim_key, dim_name in [('T1', '格式符合度'), ('T2', '内容深度'),
                               ('T3', '版本成熟度'), ('T4', '内部一致性')]:
        avg = dim_avgs[dim_key]
        verdict = '⚠️ 严重短板' if avg < 30 else '🔶 待提升' if avg < 50 else '✅ 良好'
        report.append(f"| {dim_key} {dim_name} | {avg} | 100 | {avg}% | {verdict} |")
    report.append("")

    # ── 汇总 ──
    report.append("## 📋 汇总")
    report.append("")
    report.append("| 指标 | 数值 |")
    report.append("|:-----|:----:|")
    report.append(f"| 扫描总数 | {total} |")
    s_cnt = len(sub_levels['S-卓越']) + len(sub_levels['A-优质'])
    report.append(f"| ⭐⭐⭐ 可迁移 (S+A) | {s_cnt} ({pct(s_cnt)}) |")
    b_cnt = len(sub_levels['B-达标'])
    report.append(f"| ⭐⭐ 补元数据 (B) | {b_cnt} ({pct(b_cnt)}) |")
    cde_cnt = len(sub_levels['C-接近']) + len(sub_levels['D-待提']) + len(sub_levels['E-基础'])
    report.append(f"| ⭐ AI 增强 (C+D+E) | {cde_cnt} ({pct(cde_cnt)}) |")
    fg_cnt = len(sub_levels['F-薄弱']) + len(sub_levels['G-废弃'])
    report.append(f"| ❌ 不合格 (F+G) | {fg_cnt} ({pct(fg_cnt)}) |")
    weakest = min(dim_avgs, key=dim_avgs.get)
    strongest = max(dim_avgs, key=dim_avgs.get)
    report.append(f"| 维度短板 | {weakest} ({dim_avgs[weakest]}) |")
    report.append(f"| 维度长板 | {strongest} ({dim_avgs[strongest]}) |")
    report.append("")
    report.append("## 📌 建议行动")
    report.append("")
    report.append(f"1. **S/A ({s_cnt} 个)**: 人工终审后迁移至 `knowledge/`")
    report.append(f"2. **B ({b_cnt} 个)**: 批量补充头部元数据后迁移")
    report.append(f"3. **C+D+E ({cde_cnt} 个)**: 进入 AI 增强管线，按 C→D→E 优先级")
    report.append(f"4. **F+G ({fg_cnt} 个)**: 人工判断重写或 `tmp/bak/`")
    report.append("")
    report.append("---")
    report.append("")
    report.append(f"*报告自动生成: {TODAY} | 工具: discover-quality-scan.py v2 (8-level) | 标准: sr-007 §5 近似版*")

    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(
        description='discover 内容质量扫描 — sr-007 近似版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python3 scripts/check/discover-quality-scan.py                    # 全量扫描
  python3 scripts/check/discover-quality-scan.py --dir discover/newwiki2/
  python3 scripts/check/discover-quality-scan.py --sample 100      # 抽样 100
  python3 scripts/check/discover-quality-scan.py --json-only       # 仅 JSON
  python3 scripts/check/discover-quality-scan.py --sub-level 'A-优质'  # 只查 A-优质
  python3 scripts/check/discover-quality-scan.py --by-dir         # 按目录分组统计""")
    parser.add_argument('--dir', '-d', default='discover/',
                        help='扫描目录（默认 discover/）')
    parser.add_argument('--threshold', '-t', type=float, default=60,
                        help='门禁阈值（默认 60，即 ⭐⭐ 以上通过）')
    parser.add_argument('--sample', '-s', type=int, default=0,
                        help='抽样文件数（0=全量）')
    parser.add_argument('--sub-level', '-l', default='',
                        help='按子级过滤: S-卓越/A-优质/B-达标/C-接近/D-待提/E-基础/F-薄弱/G-废弃')
    parser.add_argument('--by-dir', action='store_true',
                        help='输出按目录分组的细分统计')
    parser.add_argument('--json-only', action='store_true',
                        help='仅输出 JSON 到 stdout')
    parser.add_argument('--report-dir', default='discover/report/',
                        help='报告输出目录（默认 discover/report/）')
    args = parser.parse_args()

    target_dir = REPO_ROOT / args.dir
    if not target_dir.exists():
        print(f"[ERROR] 目录不存在: {target_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 开始质量扫描: {target_dir}", file=sys.stderr)
    if args.sample > 0:
        print(f"📊 抽样模式: {args.sample} 个文件", file=sys.stderr)

    results = scan_directory(target_dir, sample=args.sample)

    print(f"✅ 扫描完成: {len(results)} 个文件", file=sys.stderr)

    # ── 按子级过滤 ──
    if args.sub_level:
        target_sl = args.sub_level.strip()
        filtered = [r for r in results if r.get('sub_label') == target_sl]
        print(f"🔎 过滤: {target_sl} → {len(filtered)} 个文件", file=sys.stderr)
        if not filtered:
            print(f"[WARN] 无匹配 '{target_sl}' 的文件。有效值: S-卓越/A-优质/B-达标/C-接近/D-待提/E-基础/F-薄弱/G-废弃")
            return
        results = filtered

    # ── 按目录分组统计 ──
    if args.by_dir and results:
        from collections import defaultdict
        dir_stats = defaultdict(lambda: {'total': 0, 'counts': defaultdict(int), 'avg': 0, 'scores': []})
        for r in results:
            rel = r['file']
            # 取 discover/ 后的第一级子目录
            parts = rel.split('/')
            top_dir = parts[1] if len(parts) > 2 else '(root)'
            dir_stats[top_dir]['total'] += 1
            dir_stats[top_dir]['counts'][r.get('sub_label', '?')] += 1
            dir_stats[top_dir]['scores'].append(r['overall'])
        for d in dir_stats:
            scores = dir_stats[d]['scores']
            dir_stats[d]['avg'] = round(sum(scores) / max(len(scores), 1), 1)
            del dir_stats[d]['scores']

        print(f"\n{'=' * 80}", file=sys.stderr)
        print(f"📂 按目录分组统计", file=sys.stderr)
        print(f"{'=' * 80}", file=sys.stderr)
        header = f"{'目录':<30} {'总数':>6} {'平均分':>7}  "
        for sl_key in ['S-卓越','A-优质','B-达标','C-接近','D-待提','E-基础','F-薄弱','G-废弃']:
            header += f"{sl_key[:4]:>6}"
        print(header, file=sys.stderr)
        print('-' * len(header), file=sys.stderr)
        for d in sorted(dir_stats.keys()):
            ds = dir_stats[d]
            line = f"{d:<30} {ds['total']:>6} {ds['avg']:>7.1f}  "
            for sl_key in ['S-卓越','A-优质','B-达标','C-接近','D-待提','E-基础','F-薄弱','G-废弃']:
                line += f"{ds['counts'].get(sl_key, 0):>6}"
            print(line, file=sys.stderr)
        print(file=sys.stderr)

    # 生成 JSON
    json_data = {
        'scan_time': TODAY,
        'target_dir': str(target_dir),
        'total_files': len(results),
        'threshold': args.threshold,
        'results': results,
    }

    if args.json_only:
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
        return

    # 生成 Markdown 报告
    report_md = generate_report(results, str(target_dir), args.threshold)

    # 保存报告
    report_dir = REPO_ROOT / args.report_dir
    report_dir.mkdir(parents=True, exist_ok=True)

    md_path = report_dir / f'{TODAY}-quality-scan.md'
    json_path = report_dir / f'{TODAY}-quality-scan.json'

    md_path.write_text(report_md, encoding='utf-8')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"📄 Markdown 报告: {md_path}", file=sys.stderr)
    print(f"📊 JSON 详细数据: {json_path}", file=sys.stderr)
    print(f"\n{report_md}")


if __name__ == '__main__':
    main()
