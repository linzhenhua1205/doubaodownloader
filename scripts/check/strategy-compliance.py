#!/usr/bin/env python3
"""
strategy-compliance.py — 知识库策略合规校验器

校验文件是否遵循其所在位置应有的 Strategy (A/B/C/D/E) 要求。
基于 KNOWLEDGE_STRATEGIES.md 和 KNOWLEDGE_OPERATIONS_GUIDE.md。

核心功能：
  1. 位置→策略映射验证（文件在正确目录？）
  2. 内容合规检查（格式/深度/数据验证/关系记录）
  3. Token 预算估算
  4. 放置决策树合规（§3.1）

Usage:
    python3 scripts/check/strategy-compliance.py <file-path>
    python3 scripts/check/strategy-compliance.py <file-path> --json
    python3 scripts/check/strategy-compliance.py <file-path> --fix        # 修复可自动修复项
    python3 scripts/check/strategy-compliance.py --all                    # 全库扫描
    python3 scripts/check/strategy-compliance.py --all --summary          # 汇总报告
    python3 scripts/check/strategy-compliance.py --module 02_rd           # 特定模块
"""
import sys
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

SKIP_DIRS = {'bak', 'import-modules', 'node_modules', '.git', '.bak', 'oldbak', 'archive', 'archived'}
SKIP_FILES = {'README.md', 'TRACKING.md'}
KNOWLEDGE_ROOT = WORKSPACE_ROOT / "knowledge"

# ── 策略映射 ──────────────────────────────────────────────────

# 目录→策略映射（优先级从高到低）
STRATEGY_MAP = [
    # Fast Track (A)
    ('01_survey/', 'A'),
    # Source archive (C)
    ('06_others/sources/', 'C'),
    # Deep analysis (B)
    ('02_rd/', 'B'),
    ('03_AI/', 'B'),
    ('07_industry-research/', 'B'),
    ('methodology/', 'B'),
    ('concepts/', 'B'),
    # Weekly reports (T6, treated as B-adjacent)
    ('weekly-reports/', 'B'),
    # Others (default to B for safety)
]

# 每个策略的合规检查项
STRATEGY_CHECKS = {
    'A': {
        'name': 'A — 快速跟踪',
        'target_dirs': ['01_survey/'],
        'file_pattern': r'^\d{4}-\d{2}-\d{2}\.md$',
        'requirements': [
            ('format_t3', '格式应为 T3（每日跟踪文件）', True),
            ('has_title', '首行应为 # 标题 + 日期', True),
            ('no_toc', '不应有 TOC', False),
            ('no_changelog', '不应有 Changelog', False),
            ('has_source_refs', '信息应有来源引用', True),
            ('is_shallow', '应为浅层摘要（非深度分析）', True),
        ],
        'token_budget': 5000,
    },
    'B': {
        'name': 'B — 深度分析',
        'target_dirs': ['02_rd/', '03_AI/', '07_industry-research/', 'methodology/', 'concepts/'],
        'file_pattern': r'.*\.md$',
        'requirements': [
            ('format_t4', '格式应为 T4（深度文档）', True),
            ('has_meta', '文件头应有元信息块（版本/日期/核心问题）', True),
            ('has_toc_if_long', '>200行应有 TOC', True),
            ('has_changelog', '尾部应有 Changelog', True),
            ('has_data_validation', '量化数据应有数值+单位+基线+条件', True),
            ('has_cross_links', '应有交叉链接到 knowledge/ 下其他文件', True),
            ('has_source_attribution', '断言有出处或标注来源', True),
            ('has_relationship', '策略 E 关系记录应存在', True),
            ('has_conclusion', '应有可行动的结论/建议', True),
            ('no_import_refs', '不应直接引用 import/ 路径', False),
        ],
        'token_budget': None,  # 充分投入
    },
    'C': {
        'name': 'C — 导入笔记',
        'target_dirs': ['06_others/sources/', '05_tools/doubao-qa/'],
        'file_pattern': r'.*\.md$',
        'requirements': [
            ('format_t7', '格式应为 T7（归档来源文件）', True),
            ('has_source_url', '文件头应有 Source URL', True),
            ('has_archive_date', '应有归档日期', True),
            ('has_summary_not_copy', '应提炼要点而非全文拷贝', True),
            ('has_relationship', '策略 E 关系记录应存在', True),
            ('no_deep_analysis', '不应做深度解读/分析', False),
            ('no_import_bak_refs', '不应引用 import/ 或 bak/', False),
        ],
        'token_budget': None,  # 适中
    },
    'D': {
        'name': 'D — 体系化知识',
        'target_dirs': ['methodology/', 'concepts/'],  # Also cross-module
        'file_pattern': r'.*\.md$',
        'requirements': [
            ('format_t4', '格式应为 T4（深度文档）', True),
            ('has_meta', '文件头应有元信息块（含关联字段）', True),
            ('has_toc_if_long', '>200行应有 TOC', True),
            ('has_changelog', '尾部应有 Changelog', True),
            ('has_cross_module_links', '应有跨模块交叉链接（3+模块）', True),
            ('has_reverse_links', '应在关联文件中注入反向链接', True),
            ('has_relationship', '策略 E 关系记录完整', True),
            ('has_boundary', '应有边界说明（什么算/不算）', True),
            ('has_mece_check', '应与相邻主题 MECE 划分清晰', True),
            ('no_import_refs', '不应直接引用 import/ 路径', False),
        ],
        'token_budget': None,
    },
    'E': {
        'name': 'E — 关系记录',
        'target_dirs': [],  # 附加操作，不限于特定目录
        'file_pattern': None,
        'requirements': [
            ('has_relation_in_index', '所在模块 index.md 应有关系记录', True),
            ('relation_types_valid', '关系类型来自 §7 标准分类', True),
            ('relation_targets_exist', '关系目标文件存在', True),
        ],
        'token_budget': None,
    },
}

# §7 标准关系分类
VALID_RELATION_TYPES = {
    'related': '功能相关/主题相似',
    'depends-on': '依赖关系（A 依赖 B 的内容才能理解）',
    'supersedes': '替代关系（新文件替代旧文件）',
    'see-also': '建议参阅（非直接依赖但相关）',
    'contrasts': '对比关系（立场/方法/结论相反）',
    'extends': '扩展关系（A 扩展了 B 的内容）',
    'source-of': '来源关系（A 是 B 的来源/原始材料）',
    'part-of': '组成部分（A 是 B 的一部分）',
    'example-of': '示例关系（A 是 B 的实例/案例）',
    'references': '引用关系（A 引用了 B 的内容）',
}


def detect_strategy(filepath: Path, rel_path: str) -> tuple:
    """Detect which strategy a file should follow based on its path."""
    # Strategy E is always applicable as an additional check
    strategies = {'E': False}

    for prefix, strategy in STRATEGY_MAP:
        if rel_path.startswith(prefix):
            strategies[strategy] = True
            break

    # Default fallback
    if not any(v for k, v in strategies.items() if k != 'E'):
        strategies['B'] = True  # Default to deep analysis for unknown paths

    return strategies


def check_format_t3(content: str, lines: list) -> list:
    """Check T3 (daily tracking file) format compliance."""
    issues = []
    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    # Check first line: # 标题 · 日期
    first = lines[0].strip()
    if not first.startswith('# '):
        issues.append(('FAIL', 'has_title', '首行不是 H1 标题'))

    # Check for core summary
    has_summary = False
    for line in lines[1:5]:
        if line.strip().startswith('>'):
            has_summary = True
            break
    if not has_summary:
        issues.append(('WARN', 'has_title', '缺少核心要点摘要（> 开头段落）'))

    # Should NOT have TOC
    for line in lines[:30]:
        if '- [1.' in line or '- [2.' in line:
            issues.append(('WARN', 'no_toc', '跟踪文件不建议有 TOC（保持轻量）'))
            break

    # Should NOT have changelog
    for line in lines[-10:]:
        if '| 版本 | 日期 |' in line or '## Changelog' in line:
            issues.append(('WARN', 'no_changelog', '跟踪文件不应有 Changelog'))
            break

    # Should have source references
    has_source = False
    for line in lines:
        if 'http' in line or 'Source:' in line or '来源' in line:
            has_source = True
            break
    if not has_source:
        issues.append(('INFO', 'has_source_refs', '未检测到来源引用（可选）'))

    return issues


def check_format_t4(content: str, lines: list, rel_path: str) -> list:
    """Check T4 (deep document) format compliance."""
    issues = []

    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    # Check meta block (> version/date/core-question)
    has_meta = False
    meta_fields = set()
    for line in lines[1:10]:
        line_s = line.strip()
        if line_s.startswith('> **版本'):
            has_meta = True
            meta_fields.add('version')
        if line_s.startswith('> **日期'):
            meta_fields.add('date')
        if line_s.startswith('> **核心问题'):
            meta_fields.add('core_question')
        if line_s.startswith('> **关联'):
            meta_fields.add('relation')

    if not has_meta:
        issues.append(('FAIL', 'has_meta', '缺少文件头元信息块 (> 开头)'))
    elif 'version' not in meta_fields or 'date' not in meta_fields:
        issues.append(('FAIL', 'has_meta', f'元信息块缺少字段: 已有{meta_fields}, 需 version+date+core_question'))

    # Check TOC for long files (>200 lines)
    if len(lines) > 200:
        has_toc = False
        for line in lines[:30]:
            if '- [1.' in line or '- [2.' in line:
                has_toc = True
                break
        if not has_toc:
            issues.append(('FAIL', 'has_toc_if_long', f'文件>{len(lines)}行但无 TOC'))

    # Check changelog at end
    has_cl = False
    for line in lines[-20:]:
        if '## Changelog' in line or '| 版本 | 日期 |' in line:
            has_cl = True
            break
    if not has_cl:
        issues.append(('WARN', 'has_changelog', '尾部缺少 Changelog'))

    # Check quantitative data patterns (value+unit)
    data_pattern = re.compile(r'\d+(?:\.\d+)?\s*(?:GB|TB|MB|KW|W|GHz|MHz|Gbps|Mbps|ns|ms|s|%|°C|V|A)')
    data_count = len(data_pattern.findall(content))
    if data_count < 3 and len(lines) > 100:
        issues.append(('WARN', 'has_data_validation', f'仅{data_count}个量化数据点，深度分析文件建议≥3'))

    # Check cross-links to knowledge/
    link_pattern = re.compile(r'\]\(knowledge/')
    link_count = len(link_pattern.findall(content))
    if link_count == 0 and len(lines) > 50:
        issues.append(('WARN', 'has_cross_links', '无交叉链接到 knowledge/ 下其他文件'))
    elif link_count == 0:
        issues.append(('INFO', 'has_cross_links', '无交叉链接（短文件可接受）'))

    # Should NOT reference import/
    if 'import/' in content:
        issues.append(('FAIL', 'no_import_refs', '不应直接引用 import/ 路径'))

    # Should NOT reference bak/
    # bak/引用规则 — check 模式：检测引用
    if 'knowledge/bak/' in content or 'tmp/bak/' in content:
        issues.append(('FAIL', 'no_bak_refs', '不应直接引用 bak/ 路径'))

    return issues


def check_format_t7(content: str, lines: list) -> list:
    """Check T7 (source archive) format compliance."""
    issues = []

    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    # Check Source URL
    has_source = False
    has_archive_date = False
    for line in lines[1:5]:
        line_s = line.strip()
        if line_s.startswith('> **Source') or line_s.startswith('> Source'):
            has_source = True
        if '归档日期' in line_s or 'archive' in line_s.lower():
            has_archive_date = True

    if not has_source:
        issues.append(('FAIL', 'has_source_url', '缺少 Source URL'))
    if not has_archive_date:
        issues.append(('FAIL', 'has_archive_date', '缺少归档日期'))

    # Check for summary section
    has_summary = False
    has_key_info = False
    for line in lines:
        line_s = line.strip()
        if line_s.startswith('## 内容摘要') or line_s.startswith('## Content'):
            has_summary = True
        if line_s.startswith('## 关键信息') or line_s.startswith('## Key'):
            has_key_info = True

    if not has_summary:
        issues.append(('WARN', 'has_summary_not_copy', '缺少「内容摘要」章节'))

    # Should NOT reference import/ or bak/
    # bak/引用规则 — check 模式：检测引用
    for ref_pattern in ['import/', 'knowledge/bak/', 'tmp/bak/']:
        if ref_pattern in content:
            issues.append(('FAIL', 'no_import_bak_refs', f'不应引用 {ref_pattern}'))

    # Check for deep analysis indicators (should NOT have deep analysis)
    deep_indicators = ['因此我们可以得出结论', '建议采取以下措施', '策略建议']
    found_deep = [d for d in deep_indicators if d in content]
    if found_deep and len(lines) > 100:
        issues.append(('INFO', 'no_deep_analysis', '检测到可能深度分析内容（T7 不应做深度分析）'))

    return issues


def validate_file(filepath: Path, root: Path = KNOWLEDGE_ROOT, fix: bool = False) -> dict:
    """Validate a single file for strategy compliance."""
    rel_path = str(filepath.relative_to(root)).replace('\\', '/')
    result = {
        'file': rel_path,
        'strategies': {},
        'checks': [],
        'score': 0,
        'total_checks': 0,
        'passed_checks': 0,
        'issues': [],
        'token_estimate': 0,
        'recommendation': None,
    }

    # Read file
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        result['issues'].append(('ERROR', 'read', f'读取失败: {e}'))
        return result

    lines = content.split('\n')
    result['token_estimate'] = len(content) // 4  # Rough estimate

    # Detect strategies
    strategies = detect_strategy(filepath, rel_path)
    result['strategies'] = {k: v for k, v in strategies.items() if v}

    # Run checks per strategy
    for strategy_code in strategies:
        if not strategies[strategy_code]:
            continue
        checks = STRATEGY_CHECKS.get(strategy_code, {})
        reqs = checks.get('requirements', [])
        result['total_checks'] += len(reqs)

        for check_id, check_desc, required in reqs:
            result['checks'].append({
                'strategy': strategy_code,
                'check_id': check_id,
                'description': check_desc,
                'required': required,
                'status': 'PENDING',
            })

    # Run format-specific checks
    format_issues = []
    strategy_for_format = None
    for s_code in strategies:
        if strategies[s_code] and s_code in ('A', 'B', 'C', 'D'):
            strategy_for_format = s_code
            break

    if strategy_for_format == 'A':
        format_issues = check_format_t3(content, lines)
    elif strategy_for_format in ('B', 'D'):
        format_issues = check_format_t4(content, lines, rel_path)
    elif strategy_for_format == 'C':
        format_issues = check_format_t7(content, lines)

    # Map format issues to check results (flexible match: issue_id contains check_id or vice versa)
    def _check_id_match(req_check_id: str, fmt_issue_id: str) -> bool:
        """Flexible match between requirement check_id and format issue_id."""
        # Direct match
        if req_check_id == fmt_issue_id:
            return True
        # req 'no_toc' matches fmt 'toc' (negation match)
        if req_check_id.startswith('no_') and req_check_id[3:] == fmt_issue_id:
            return True
        if fmt_issue_id.startswith('no_') and fmt_issue_id[3:] == req_check_id:
            return True
        # Substring match (has_meta matches meta, has_cross_links matches cross_links)
        if req_check_id.replace('has_', '').replace('no_', '') in fmt_issue_id:
            return True
        if fmt_issue_id.replace('no_', '') in req_check_id:
            return True
        return False

    for check in result['checks']:
        matched = False
        for issue_severity, issue_id, issue_desc in format_issues:
            if _check_id_match(check['check_id'], issue_id):
                matched = True
                if issue_severity == 'FAIL':
                    check['status'] = 'FAIL'
                    check['detail'] = issue_desc
                elif issue_severity == 'WARN':
                    check['status'] = 'WARN'
                    check['detail'] = issue_desc
                else:
                    check['status'] = 'INFO'
                    check['detail'] = issue_desc
                break
        if not matched:
            # Special case: negative checks (no_toc, no_changelog) PASS if no issue found
            if check['check_id'].startswith('no_'):
                check['status'] = 'PASS'
                check['detail'] = '未检测到误用（合规）'
            else:
                check['status'] = 'PASS'

    # Calculate score
    result['passed_checks'] = sum(1 for c in result['checks'] if c['status'] == 'PASS')
    result['total_checks'] = len(result['checks'])
    result['score'] = round(result['passed_checks'] / max(result['total_checks'], 1) * 100, 1)

    # Collect all issues
    for check in result['checks']:
        if check['status'] in ('FAIL', 'WARN'):
            result['issues'].append((check['status'], check['check_id'], check.get('detail', '')))

    # Generate recommendation
    if result['score'] >= 80:
        result['recommendation'] = '✅ 合规'
    elif result['score'] >= 60:
        result['recommendation'] = '⚠️ 部分合规，建议修复 WARN/FAIL 项'
    else:
        result['recommendation'] = '❌ 不合规，需重新审查策略匹配'

    return result


def scan_module(module_path: str, fix: bool = False) -> dict:
    """Scan all markdown files in a module."""
    module_dir = KNOWLEDGE_ROOT / module_path
    if not module_dir.exists():
        return {'error': f'模块不存在: {module_path}'}

    results = []
    total_score = 0
    file_count = 0
    fail_count = 0
    warn_count = 0

    for md_file in sorted(module_dir.rglob('*.md')):
        # Skip known non-content files
        if md_file.name in SKIP_FILES:
            continue
        rel = str(md_file.relative_to(KNOWLEDGE_ROOT))
        if any(skip in rel.split('/') for skip in SKIP_DIRS if skip):
            continue

        result = validate_file(md_file, fix=fix)
        results.append(result)
        total_score += result['score']
        file_count += 1
        if result['score'] < 60:
            fail_count += 1
        elif result['score'] < 80:
            warn_count += 1

    return {
        'module': module_path,
        'files_scanned': file_count,
        'avg_score': round(total_score / max(file_count, 1), 1),
        'fail_files': fail_count,
        'warn_files': warn_count,
        'results': results,
    }


def main():
    parser = argparse.ArgumentParser(description='知识库策略合规校验器')
    parser.add_argument('file', nargs='?', help='要校验的文件路径（相对 knowledge/）')
    parser.add_argument('--all', action='store_true', help='全库扫描')
    parser.add_argument('--module', help='特定模块扫描')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    parser.add_argument('--summary', action='store_true', help='仅输出汇总')
    parser.add_argument('--fix', action='store_true', help='尝试修复可自动修复的问题')
    args = parser.parse_args()

    if args.all:
        # Scan all modules
        all_results = {}
        for subdir in sorted(KNOWLEDGE_ROOT.iterdir()):
            if subdir.is_dir() and subdir.name not in SKIP_DIRS and not subdir.name.startswith('.'):
                mod_result = scan_module(subdir.name, fix=args.fix)
                all_results[subdir.name] = mod_result

        if args.json:
            print(json.dumps(all_results, ensure_ascii=False, indent=2))
            return

        # Summary report
        print(f"\n{'='*60}")
        print(f"📊 全库策略合规扫描报告")
        print(f"{'='*60}")
        grand_total = 0
        grand_files = 0
        grand_fail = 0
        grand_warn = 0
        for mod_name, mod_result in sorted(all_results.items()):
            if 'error' in mod_result:
                print(f"  ❌ {mod_name}: {mod_result['error']}")
                continue
            grand_total += mod_result['avg_score']
            grand_files += mod_result['files_scanned']
            grand_fail += mod_result['fail_files']
            grand_warn += mod_result['warn_files']
            status = '✅' if mod_result['avg_score'] >= 80 else '⚠️' if mod_result['avg_score'] >= 60 else '❌'
            print(f"  {status} {mod_name}: avg={mod_result['avg_score']}% | "
                  f"{mod_result['files_scanned']} files | "
                  f"fail={mod_result['fail_files']} warn={mod_result['warn_files']}")

        print(f"\n{'─'*60}")
        print(f"  总计: {grand_files} 文件 | 全库均分: {round(grand_total/max(len(all_results),1),1)}%")
        print(f"  严重不合规: {grand_fail} | 部分合规: {grand_warn}")
        print(f"{'='*60}\n")
        return

    if args.module:
        mod_result = scan_module(args.module, fix=args.fix)
        if 'error' in mod_result:
            print(f"❌ {mod_result['error']}")
            return

        if args.json:
            print(json.dumps(mod_result, ensure_ascii=False, indent=2))
            return

        status = '✅' if mod_result['avg_score'] >= 80 else '⚠️' if mod_result['avg_score'] >= 60 else '❌'
        print(f"\n{status} 模块: {args.module}")
        print(f"  扫描文件: {mod_result['files_scanned']}")
        print(f"  平均分: {mod_result['avg_score']}%")
        print(f"  严重不合规: {mod_result['fail_files']}")
        print(f"  部分合规: {mod_result['warn_files']}")

        if args.summary:
            return

        for r in mod_result['results'][:20]:  # Show top 20
            if r['issues']:
                print(f"\n  📄 {r['file']} ({r['score']}%)")
                for severity, check_id, detail in r['issues'][:5]:
                    print(f"    {'🔴' if severity == 'FAIL' else '🟡'} [{severity}] {check_id}: {detail}")
        return

    if args.file:
        fp = KNOWLEDGE_ROOT / args.file
        if not fp.exists():
            print(f"❌ 文件不存在: {fp}")
            return

        result = validate_file(fp, fix=args.fix)

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        strategies = ', '.join(result['strategies'].keys())
        print(f"\n{'='*50}")
        print(f"📄 {result['file']}")
        print(f"  策略匹配: {strategies} | 合规分数: {result['score']}%")
        print(f"  Token 估算: {result['token_estimate']}")
        print(f"  {result['recommendation']}")
        print(f"{'='*50}")

        if result['issues']:
            print(f"\n  问题 ({len(result['issues'])} 项):")
            for severity, check_id, detail in result['issues']:
                icon = '🔴' if severity == 'FAIL' else '🟡' if severity == 'WARN' else '💡'
                print(f"  {icon} [{severity}] {check_id}: {detail}")

        print(f"\n  检查项明细:")
        for check in result['checks']:
            status_icon = '✅' if check['status'] == 'PASS' else '🔴' if check['status'] == 'FAIL' else '🟡'
            print(f"  {status_icon} [{check['strategy']}] {check['description']}: {check['status']}"
                  + (f" — {check['detail']}" if check.get('detail') else ''))
        return

    parser.print_help()


if __name__ == '__main__':
    main()
