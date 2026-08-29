#!/usr/bin/env python3
"""
format-validator.py — 知识库文件格式合规校验器 (T1-T7)

基于 KNOWLEDGE_OPERATIONS_GUIDE.md §11 文件格式规范，校验 markdown 文件的
格式符合性。自动检测文件类型（T1-T7）后对照模板逐项检查。

T1 — index.md（索引文件）
T2 — log.md（修订日志）
T3 — 日常跟踪文件 YYYY-MM-DD.md
T4 — 深度知识文档（专题报告/方法论/概念）
T5 — 跟踪框架文件 TRACKING.md
T6 — 周报 weekly-reports/YYYY-Www.md
T7 — 归档来源文件（sources/ 目录）

Usage:
    python3 scripts/check/format-validator.py <file-path>
    python3 scripts/check/format-validator.py <file-path> --json
    python3 scripts/check/format-validator.py --module 02_rd
    python3 scripts/check/format-validator.py --all --summary
    python3 scripts/check/format-validator.py <file-path> --fix
"""
import sys
import re
import json
import argparse
from pathlib import Path

# Ensure workspace root is on Python path (sr-008)
_SCRIPT_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

SKIP_DIRS = {'bak', 'import-modules', 'node_modules', '.git', '.bak', 'oldbak', 'archive', 'archived'}
KNOWLEDGE_ROOT = WORKSPACE_ROOT / "knowledge"


def detect_file_type(filepath: Path, rel_path: str, filename: str) -> str:
    """Detect file type (T1-T7) based on path and name."""
    # T1: index.md
    if filename == 'index.md':
        return 'T1'

    # T2: log.md
    if filename == 'log.md':
        return 'T2'

    # T5: TRACKING.md
    if filename == 'TRACKING.md':
        return 'T5'

    # T6: weekly reports
    if rel_path.startswith('weekly-reports/') and re.match(r'^\d{4}-W\d{2}\.md$', filename):
        return 'T6'

    # T3: daily tracking in 01_survey/
    if rel_path.startswith('01_survey/') and re.match(r'^\d{4}-\d{2}-\d{2}\.md$', filename):
        return 'T3'

    # T7: sources/
    if rel_path.startswith('sources/') or rel_path.startswith('06_others/sources/'):
        return 'T7'

    # T4: deep docs in 02_rd/, 03_AI/, methodology/, concepts/, 07_industry-research/
    if any(rel_path.startswith(p) for p in ['02_rd/', '03_AI/', 'methodology/', 'concepts/',
                                              '07_industry-research/', '04_person/',
                                              '05_tools/', '06_others/']):
        # If it's not already classified as T1-T3/T5-T7
        return 'T4'

    # Default: unknown
    return 'UNKNOWN'


def check_t1_index(lines: list, filename: str) -> list:
    """T1: index.md — 索引文件."""
    issues = []

    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    # Check table format (markdown table)
    table_lines = [i for i, l in enumerate(lines) if '|' in l]
    if len(table_lines) < 3:
        issues.append(('FAIL', 'table', '缺少 markdown 表格（至少需要表头+分隔行+数据行）'))

    # Check separator row
    for i, line in enumerate(lines):
        if '|' in line and '-:' in line or ':--' in line or '---' in line:
            break
    else:
        if table_lines:
            issues.append(('WARN', 'table_sep', '未检测到表格分隔行（|---|）'))

    # Check table headers: expect 文件, 摘要, 日期 (core 3 columns)
    for line in lines[:20]:
        if '|' in line:
            # Column detection
            cols = [c.strip() for c in line.split('|') if c.strip()]
            col_text = ' '.join(cols)
            if '文件' in col_text and '摘要' in col_text and '日期' in col_text:
                break
    else:
        issues.append(('INFO', 'table_headers', '表头缺少「文件|摘要|日期」标准列'))

    # Check links are valid markdown links
    link_count = 0
    for line in lines:
        link_count += line.count('](')
    if link_count == 0 and len(lines) > 5:
        issues.append(('WARN', 'links', '未检测到 markdown 链接'))

    return issues


def check_t2_log(lines: list, rel_path: str) -> list:
    """T2: log.md — 修订日志."""
    issues = []

    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    # Check date headers (## YYYY-MM-DD)
    date_headers = []
    for line in lines:
        m = re.match(r'^##\s+(\d{4}-\d{2}-\d{2})$', line.strip())
        if m:
            date_headers.append(m.group(1))

    if not date_headers:
        issues.append(('FAIL', 'date_headers', '缺少日期分组（## YYYY-MM-DD）'))

    # Check ordering (most recent first)
    if len(date_headers) > 1:
        dates = [datetime.strptime(d, '%Y-%m-%d') for d in date_headers]
        for i in range(len(dates) - 1):
            if dates[i] < dates[i + 1]:
                issues.append(('FAIL', 'date_order', f'日期顺序错误: {date_headers[i]} 在 {date_headers[i+1]} 之前（应为最新在上）'))
                break

    # Check entries have paths (most entries should contain `path/to/file`)
    entry_count = 0
    path_entry_count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- **') or stripped.startswith('- ['):
            entry_count += 1
            if '`' in stripped:
                path_entry_count += 1

    if entry_count > 0 and path_entry_count == 0:
        issues.append(('WARN', 'paths', '日志条目中未检测到路径引用（`path`）'))
    elif entry_count > 3 and path_entry_count / entry_count < 0.3:
        issues.append(('WARN', 'paths_low', f'仅 {path_entry_count}/{entry_count} 条目含路径引用'))

    # Check format style based on module
    is_survey_log = rel_path.startswith('01_survey/')
    if is_survey_log:
        # 01_survey log should use 「跟踪追加」 prefix
        tracking_entries = [l for l in lines if '跟踪追加' in l]
        if entry_count > 0 and not tracking_entries:
            issues.append(('INFO', 'format_survey', '01_survey 日志已统一归档 log.old.md（2026-08-19 起），不再维护分布式 log.md'))

    return issues


def check_t3_daily(lines: list, filename: str) -> list:
    """T3: 日常跟踪文件 YYYY-MM-DD.md."""
    return check_format_t3(lines)  # Reuse from strategy-compliance


def check_t4_deep(lines: list, rel_path: str) -> list:
    """T4: 深度知识文档."""
    return check_format_t4(lines, rel_path)


def check_t5_tracking(lines: list) -> list:
    """T5: 跟踪框架文件 TRACKING.md."""
    issues = []

    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    # Check has scope definition
    has_scope = False
    has_method = False
    has_focus = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## 跟踪范围') or stripped.startswith('## 范围'):
            has_scope = True
        if stripped.startswith('## 跟踪方法') or stripped.startswith('## 方法'):
            has_method = True
        if stripped.startswith('## 关注要点') or stripped.startswith('## 关注'):
            has_focus = True

    if not has_scope:
        issues.append(('FAIL', 'scope', '缺少「跟踪范围与边界」章节'))
    if not has_method:
        issues.append(('WARN', 'method', '缺少「跟踪方法」章节'))
    if not has_focus:
        issues.append(('WARN', 'focus', '缺少「关注要点」章节'))

    # Should NOT have changelog
    for line in lines:
        if '## Changelog' in line:
            issues.append(('INFO', 'changelog', 'TRACKING.md 不需要 Changelog'))
            break

    return issues


def check_t6_weekly(lines: list) -> list:
    """T6: 周报 YYYY-Www.md."""
    issues = []

    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    # Check title format
    first = lines[0].strip()
    if not first.startswith('# '):
        issues.append(('FAIL', 'title', '首行不是 H1 标题'))
    elif '周报' not in first:
        issues.append(('INFO', 'title_weekly', '标题中建议包含「周报」字样'))

    # Check overview paragraph (总览)
    has_overview = False
    for line in lines[1:10]:
        if '总览' in line or '本周' in line or '新增' in line:
            has_overview = True
            break
    if not has_overview:
        issues.append(('WARN', 'overview', '缺少总览段落'))

    # Check module grouping
    module_count = 0
    for line in lines:
        if re.match(r'^## .+', line.strip()):
            module_count += 1
    if module_count < 2:
        issues.append(('WARN', 'modules', f'仅 {module_count} 个章节，建议按模块分组'))

    return issues


def check_t7_source(lines: list) -> list:
    """T7: 归档来源文件."""
    return check_format_t7(lines)


def check_format_t3(lines: list) -> list:
    """Reusable T3 checker."""
    issues = []
    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    first = lines[0].strip()
    if not first.startswith('# '):
        issues.append(('FAIL', 'title', '首行应为 # 标题 + 日期'))

    has_summary = False
    for line in lines[1:5]:
        if line.strip().startswith('>'):
            has_summary = True
            break
    if not has_summary:
        issues.append(('WARN', 'summary', '缺少核心要点摘要'))

    has_return = False
    for line in lines[-3:]:
        if '[返回索引]' in line:
            has_return = True
            break
    if not has_return:
        issues.append(('INFO', 'return_link', '尾部缺少 [返回索引] 链接'))

    return issues


def check_format_t4(lines: list, rel_path: str) -> list:
    """Reusable T4 format checker. Delegates to content-format-normalizer for five-element checks."""
    issues = []

    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    # Delegate five-element checks to content-format-normalizer
    try:
        import importlib.util
        _src = Path(__file__).parent / 'content-format-normalizer.py'
        _spec = importlib.util.spec_from_file_location('content_format_normalizer', _src)
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        content = '\n'.join(lines)
        parsed = _mod.parse_file(content)
        norm_issues = _mod.check_file(parsed)
        for cid, status, msg in norm_issues:
            if status == 'FAIL':
                issues.append(('FAIL', cid.lower(), f'[{cid}] {msg}'))
            elif status == 'WARN':
                issues.append(('WARN', cid.lower(), f'[{cid}] {msg}'))
    except Exception:
        # Fallback to basic checks if normalizer unavailable
        pass

    # Forbidden references
    # bak/引用规则 — check 模式：禁止的引用路径，用于检测而非操作
    content = '\n'.join(lines)
    for forbidden, msg in [('import/', '引用 import/ 路径'), ('tmp/bak/', '引用 bak/ 路径'), ('knowledge/bak/', '引用 旧bak/ 路径')]:
        if forbidden in content:
            issues.append(('FAIL', 'forbidden_ref', msg))

    return issues


def check_format_t7(lines: list) -> list:
    """Reusable T7 checker."""
    issues = []

    if not lines:
        return [('FAIL', 'empty', '文件为空')]

    has_source = False
    has_archive_date = False
    for line in lines[1:6]:
        ls = line.strip()
        if 'Source' in ls and '://' in ls:
            has_source = True
        if '归档日期' in ls or 'Archived' in ls:
            has_archive_date = True

    if not has_source:
        issues.append(('FAIL', 'source_url', '缺少 Source URL'))
    if not has_archive_date:
        issues.append(('FAIL', 'archive_date', '缺少归档日期'))

    has_summary = False
    has_relation = False
    for line in lines:
        ls = line.strip()
        if ls.startswith('## 内容摘要') or ls.startswith('## Content Summary') or ls.startswith('## 摘要'):
            has_summary = True
        if 'knowledge/' in ls and '](' in ls:
            has_relation = True

    if not has_summary:
        issues.append(('WARN', 'summary', '缺少「内容摘要」章节'))

    # Forbidden refs
    # bak/引用规则 — check 模式：禁止引用
    content = '\n'.join(lines)
    for forbidden in ['import/', 'tmp/bak/', 'knowledge/bak/']:
        if forbidden in content:
            issues.append(('FAIL', 'forbidden_ref', f'引用 {forbidden}'))

    return issues


def auto_fix_file(filepath: Path, rel_path: str, lines: list, issues: list) -> bool:
    """尝试自动修复可修复的格式问题。返回是否修改成功。"""
    modified = list(lines)
    fixed_any = False

    for severity, check_id, desc in issues:
        if severity != 'FAIL':
            continue

        # 修复 forbidden_ref: 移除包含禁止路径的行
        if check_id == 'forbidden_ref':
            forbidden_patterns = ['import/', 'tmp/bak/', 'knowledge/bak/']
            before = len(modified)
            for pattern in forbidden_patterns:
                modified = [l for l in modified if pattern not in l]
            if len(modified) != before:
                fixed_any = True

        # 修复 missing_toc: 在第二个 ## 标题后插入目录标记
        if check_id == 'missing_toc':
            heading_count = 0
            for i, line in enumerate(modified):
                if line.startswith('## '):
                    heading_count += 1
                    if heading_count == 2:
                        modified.insert(i, '')
                        modified.insert(i + 1, '> 📑 目录自动生成')
                        modified.insert(i + 2, '')
                        fixed_any = True
                        break

    if fixed_any:
        try:
            filepath.write_text('\n'.join(modified), encoding='utf-8')
            issues.append(('INFO', 'auto_fixed', f'已自动修复：{rel_path}'))
            return True
        except Exception as e:
            issues.append(('WARN', 'auto_fix_failed', f'自动修复失败: {e}'))
            return False

    return False


def validate_format(filepath: Path, rel_path: str, fix: bool = False) -> dict:
    """Validate file format and return report."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return {'file': rel_path, 'error': str(e), 'type': None, 'score': 0, 'issues': []}

    lines = content.split('\n')
    ftype = detect_file_type(filepath, rel_path, filepath.name)
    issues = []

    if ftype == 'T1':
        issues = check_t1_index(lines, filepath.name)
    elif ftype == 'T2':
        issues = check_t2_log(lines, rel_path)
    elif ftype == 'T3':
        issues = check_t3_daily(lines, filepath.name)
    elif ftype == 'T4':
        issues = check_t4_deep(lines, rel_path)
    elif ftype == 'T5':
        issues = check_t5_tracking(lines)
    elif ftype == 'T6':
        issues = check_t6_weekly(lines)
    elif ftype == 'T7':
        issues = check_t7_source(lines)
    else:
        issues = [('INFO', 'unknown_type', '无法检测文件类型，跳过格式检查')]

    # --fix 模式：自动修复可修复项
    if fix and issues:
        auto_fix_file(filepath, rel_path, lines, issues)

    # Calculate score
    total = len(issues) + 3  # Base score
    deductions = sum(3 for s, _, _ in issues if s == 'FAIL') + \
                 sum(1 for s, _, _ in issues if s == 'WARN')
    score = max(0, round((1 - deductions / max(total, 1)) * 100, 1))

    return {
        'file': rel_path,
        'type': ftype,
        'lines': len(lines),
        'score': score,
        'issues': [(severity, check_id, desc) for severity, check_id, desc in issues],
    }


def scan_module(module_path: str) -> dict:
    """Scan all md files in a module for format compliance."""
    module_dir = KNOWLEDGE_ROOT / module_path
    if not module_dir.exists():
        return {'error': f'模块不存在: {module_path}'}

    results = []
    for md_file in sorted(module_dir.rglob('*.md')):
        rel = str(md_file.relative_to(KNOWLEDGE_ROOT))
        if any(skip in rel.split('/') for skip in SKIP_DIRS if skip):
            continue
        results.append(validate_format(md_file, rel))

    fail_count = sum(1 for r in results if r['score'] < 60)
    warn_count = sum(1 for r in results if 60 <= r['score'] < 80)
    avg_score = round(sum(r['score'] for r in results) / max(len(results), 1), 1)

    return {
        'module': module_path,
        'files_scanned': len(results),
        'avg_score': avg_score,
        'fail_files': fail_count,
        'warn_files': warn_count,
        'results': results,
    }


def main():
    parser = argparse.ArgumentParser(description='知识库格式校验器 (T1-T7)')
    parser.add_argument('file', nargs='?', help='文件路径（相对 knowledge/）')
    parser.add_argument('--all', action='store_true', help='全库扫描')
    parser.add_argument('--module', help='特定模块扫描')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    parser.add_argument('--summary', action='store_true', help='仅输出汇总')
    parser.add_argument('--fix', action='store_true', help='尝试修复可自动修复的问题')
    args = parser.parse_args()

    if args.all:
        all_results = {}
        for subdir in sorted(KNOWLEDGE_ROOT.iterdir()):
            if subdir.is_dir() and subdir.name not in SKIP_DIRS:
                mod_result = scan_module(subdir.name)
                all_results[subdir.name] = mod_result

        if args.json:
            print(json.dumps(all_results, ensure_ascii=False, indent=2))
            return

        print(f"\n{'='*60}")
        print(f"📋 全库格式合规扫描报告 (T1-T7)")
        print(f"{'='*60}")
        grand_files = 0
        grand_fail = 0
        grand_warn = 0
        for mod_name, mr in sorted(all_results.items()):
            if 'error' in mr:
                continue
            grand_files += mr['files_scanned']
            grand_fail += mr['fail_files']
            grand_warn += mr['warn_files']
            st = '✅' if mr['avg_score'] >= 80 else '⚠️' if mr['avg_score'] >= 60 else '❌'
            print(f"  {st} {mod_name}: {mr['avg_score']}% | {mr['files_scanned']} files | "
                  f"fail={mr['fail_files']} warn={mr['warn_files']}")

        print(f"\n{'─'*60}")
        print(f"  总计: {grand_files} 文件 | 严重: {grand_fail} | 警告: {grand_warn}")
        print(f"{'='*60}\n")
        return

    if args.module:
        mr = scan_module(args.module)
        if 'error' in mr:
            print(f"❌ {mr['error']}")
            return
        if args.json:
            print(json.dumps(mr, ensure_ascii=False, indent=2))
            return
        st = '✅' if mr['avg_score'] >= 80 else '⚠️' if mr['avg_score'] >= 60 else '❌'
        print(f"\n{st} 模块 {args.module}: avg={mr['avg_score']}% | {mr['files_scanned']} files | "
              f"fail={mr['fail_files']} warn={mr['warn_files']}")
        if not args.summary:
            for r in mr['results'][:15]:
                if r['issues']:
                    print(f"  📄 {r['file']} [{r['type']}] ({r['score']}%)")
                    for sev, cid, desc in r['issues'][:4]:
                        print(f"    {'🔴' if sev == 'FAIL' else '🟡'} [{sev}] {cid}: {desc}")
        return

    if args.file:
        fp = KNOWLEDGE_ROOT / args.file
        if not fp.exists():
            print(f"❌ 文件不存在: {fp}")
            return
        result = validate_format(fp, args.file, fix=args.fix)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        print(f"\n{'='*50}")
        print(f"📄 {result['file']} [{result['type']}]")
        print(f"  行数: {result['lines']} | 合规分数: {result['score']}%")
        print(f"{'='*50}")
        if result['issues']:
            print(f"\n  格式问题 ({len(result['issues'])} 项):")
            for severity, check_id, desc in result['issues']:
                icon = '🔴' if severity == 'FAIL' else '🟡' if severity == 'WARN' else '💡'
                print(f"  {icon} [{severity}] {check_id}: {desc}")
        else:
            print(f"\n  ✅ 格式合规")
        return

    parser.print_help()


if __name__ == '__main__':
    from datetime import datetime
    main()
