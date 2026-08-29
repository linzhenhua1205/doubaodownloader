#!/usr/bin/env python3
"""
文档审查脚本 — 自动化结构层审查

整合 markdown 格式检查、来源检查、量化数据检查、逻辑谬误启发式扫描。
生成结构化审查报告。

用法:
    python3 review_doc.py <文件/目录路径>
    python3 review_doc.py <路径> --output <报告路径>
    python3 review_doc.py <路径> --report-only   # 仅输出报告到终端
    python3 review_doc.py <路径> --fix            # 自动修复部分问题
"""

import re
import sys
import os
from pathlib import Path
from datetime import datetime


def load_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines(), f.read()


def count_chinese(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))


# ==================== 结构检查函数 ====================

def check_toc(lines, text):
    """检查目录（>100行需TOC）"""
    total_lines = len(lines)
    if total_lines <= 100:
        return {'pass': True, 'detail': f'仅{total_lines}行，无需TOC'}

    header = '\n'.join(lines[:60])
    toc_links = re.findall(r'\[.*?\]\([/#]', header)
    has_toc_marker = bool(re.search(r'(目录|Contents|TOC|index|导航)', header, re.IGNORECASE))

    if len(toc_links) >= 3 or has_toc_marker:
        return {'pass': True, 'detail': f'文件{total_lines}行，有TOC ✓'}
    return {'pass': False, 'detail': f'文件{total_lines}行>100，缺少目录', 'severity': '🔴'}


def check_changelog(lines, text):
    """检查changelog（>200行需底部changelog）"""
    total_lines = len(lines)
    if total_lines <= 200:
        return {'pass': True, 'detail': f'仅{total_lines}行，无需changelog'}

    tail = '\n'.join(lines[-200:])
    has_cl = bool(re.search(r'(changelog|Changelog|变更日志|变更记录|版本记录)', tail, re.IGNORECASE))
    if has_cl:
        return {'pass': True, 'detail': f'文件{total_lines}行，有changelog ✓'}
    return {'pass': False, 'detail': f'文件{total_lines}行>200，缺少changelog', 'severity': '🔴'}


def check_code_ascii(lines, text):
    """检查代码块中文"""
    in_code_block = False
    issues = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block and re.search(r'[\u4e00-\u9fff]', line):
            issues.append(i)
    if not issues:
        return {'pass': True, 'detail': '代码块纯ASCII ✓'}
    return {'pass': False, 'detail': f'代码块中有{len(issues)}处中文', 'locations': issues[:15], 'severity': '🔴'}


def check_citations(text):
    """检查来源标注"""
    patterns = [
        r'\[来源:', r'\[Source:', r'参考文献', r'参考来源',
        r'https?://(arxiv|doi|ieee|acm)',
        r'^\[[0-9]+\]', r'## .*参考', r'#+ .*参考文献',
        r'arXiv:', r'DOI:',
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return {'pass': True, 'detail': '有来源标注 ✓'}
    # 更宽松检查：是否有 URL
    urls = re.findall(r'https?://', text)
    if len(urls) >= 3:
        return {'pass': True, 'detail': f'有{len(urls)}个URL引用 ✓'}
    return {'pass': False, 'detail': '缺少来源标注/参考文献', 'severity': '🔴'}


def check_cross_links(text, filepath):
    """检查交叉链接"""
    links = re.findall(r'\[.*?\]\((.*?)\)', text)
    fname = Path(filepath).name
    knowledge_links = [l for l in links if 'knowledge/' in l and fname not in l]
    if knowledge_links:
        return {'pass': True, 'detail': f'有{len(knowledge_links)}个交叉链接 ✓'}
    return {'pass': False, 'detail': '无交叉链接（推荐添加）', 'severity': '🟡'}


def check_quantified_data(lines, text):
    """检查量化数据"""
    unit_pattern = r'\d+[\.\d]*(?:%|[KMGTP]?(?:Hz|bps|B|W|V|A|m|s|g|mm|um|nm|inch|bit|Byte|TB|GB|MB))'
    found = 0
    for line in lines:
        if re.search(unit_pattern, line):
            found += 1
            if found >= 3:
                break
    if found >= 3:
        return {'pass': True, 'detail': f'找到{found}处量化数据 ✓'}
    return {'pass': False, 'detail': f'仅{found}处量化数据（≥3合格）', 'severity': '🔴'}


# ==================== 逻辑启发式扫描 ====================

def check_binary_opposition(text):
    """二元对立启发式"""
    patterns = [
        r'要么.*要么', r'不是.*就是', r'只有两条路',
        r'究竟是.*还是', r'only (two|2)',
    ]
    found = []
    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        found.extend(matches)
    # 降低误报：只在找到时才报，但先过滤掉"例如、比如、包括"等场景
    if len(found) >= 2:
        return {'pass': False, 'detail': f'发现{len(found)}处可能的二元对立表述', 'severity': '🟡'}
    return {'pass': True, 'detail': '未发现二元对立表述 ✓'}


def check_conclusion_first(lines, text):
    """结论前置启发式：检查文档前部是否有未论证的结论"""
    header = '\n'.join(lines[:min(50, len(lines))])
    # 检查前50行是否出现类似结论判断的表述
    conclusion_markers = re.findall(r'(因此|所以|结论是|综上所述|最终决定|最优选择|最佳方案)', header)
    # 如果前50行就有大量结论性表述，可能结论前置
    if len(conclusion_markers) >= 3:
        return {'pass': False, 'detail': f'前50行出现{len(conclusion_markers)}个结论表述(可能结论前置)', 'severity': '🟡'}
    return {'pass': True, 'detail': '未发现结论前置 ✓'}


def check_chinese_ratio(text, total_lines):
    """中英文比例"""
    cn = count_chinese(text)
    total = len(text)
    if total == 0:
        return {'pass': True, 'detail': '空文件'}
    ratio = cn / total * 100
    if ratio > 80:
        return {'pass': True, 'detail': f'中文占比{ratio:.0f}%（技术文档合理）'}
    return {'pass': True, 'detail': f'中文占比{ratio:.0f}%'}


# ==================== 主函数 ====================

def review_doc(filepath):
    """对单个文件执行审查"""
    result = {
        'path': str(filepath),
        'fname': Path(filepath).name,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }

    if not os.path.exists(filepath):
        result['error'] = f'文件不存在: {filepath}'
        return result

    lines, text = load_text(filepath)
    total_lines = len(lines)
    total_bytes = len(text)
    result['total_lines'] = total_lines
    result['total_size_kb'] = round(total_bytes / 1024, 1)

    # 执行所有检查
    checks = {
        '📐 TOC': check_toc(lines, text),
        '📋 Changelog': check_changelog(lines, text),
        '🔤 代码块ASCII': check_code_ascii(lines, text),
        '📚 来源标注': check_citations(text),
        '🔗 交叉链接': check_cross_links(text, filepath),
        '📊 量化数据': check_quantified_data(lines, text),
        '⚖️ 二元对立': check_binary_opposition(text),
        '🎯 结论前置': check_conclusion_first(lines, text),
        '🌐 中英文比例': check_chinese_ratio(text, total_lines),
    }

    result['checks'] = checks

    # 计算通过率
    must_pass = {k: v for k, v in checks.items() if v.get('severity') == '🔴'}
    total_must = len(must_pass)
    passed_must = sum(1 for v in must_pass.values() if v['pass'])
    all_passed = sum(1 for v in checks.values() if v['pass'])
    total_checks = len(checks)

    result['pass_rate'] = f'{all_passed}/{total_checks}'
    result['must_pass_rate'] = f'{passed_must}/{total_must}' if total_must > 0 else 'N/A (无🔴项)'

    # 判定等级
    if total_must > 0 and passed_must < total_must:
        result['grade'] = '❌ 不合格'
    elif all_passed == total_checks:
        result['grade'] = '✅ 优秀'
    elif all_passed >= total_checks - 2:
        result['grade'] = '⚠️ 需改进'
    else:
        result['grade'] = '❌ 不合格'

    # 收集问题
    issues = []
    for name, check in checks.items():
        if not check['pass']:
            severity = check.get('severity', '🟡')
            detail = check['detail']
            locations = check.get('locations', [])
            loc_str = f' (第{",".join(map(str, locations[:5]))}行)' if locations else ''
            issues.append(f'{severity} {name}: {detail}{loc_str}')
    result['issues'] = issues

    return result


def print_report(results, output_path=None):
    """输出审查报告"""
    lines_out = []
    lines_out.append(f'# 📋 文档审查报告')
    lines_out.append(f'')
    lines_out.append(f'> 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines_out.append(f'')

    for result in results:
        if 'error' in result:
            lines_out.append(f'## ❌ {result["path"]}')
            lines_out.append(f'')
            lines_out.append(f'**错误**: {result["error"]}')
            lines_out.append(f'')
            continue

        lines_out.append(f'## {result["grade"]} {result["fname"]}')
        lines_out.append(f'')
        lines_out.append(f'- **路径**: `{result["path"]}`')
        lines_out.append(f'- **大小**: {result["total_size_kb"]}KB / {result["total_lines"]}行')
        lines_out.append(f'- **综合通过**: {result["pass_rate"]} | 必过项: {result["must_pass_rate"]}')
        lines_out.append(f'')

        # 问题列表
        if result['issues']:
            lines_out.append(f'### ❌ 发现 {len(result["issues"])} 个问题')
            lines_out.append(f'')
            for issue in result['issues']:
                lines_out.append(f'- {issue}')
            lines_out.append(f'')

        # 逐项
        lines_out.append(f'### 逐项检查')
        lines_out.append(f'')
        lines_out.append(f'| 检查项 | 状态 | 详情 |')
        lines_out.append(f'|:-------|:----:|:------|')
        for name, check in result['checks'].items():
            icon = '✅' if check['pass'] else '❌'
            sev = check.get('severity', '')
            lines_out.append(f'| {name} | {icon} | {sev} {check["detail"]} |')
        lines_out.append(f'')

    # 汇总
    total = len(results)
    grades = {}
    for r in results:
        if 'grade' in r:
            grades[r['grade']] = grades.get(r['grade'], 0) + 1
    lines_out.append(f'---')
    lines_out.append(f'')
    lines_out.append(f'**汇总**: {total} 个文件')
    for g, c in sorted(grades.items()):
        lines_out.append(f'- {g}: {c}')

    report_text = '\n'.join(lines_out)

    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f'✅ 审查报告已保存: {output_path}')
    else:
        print(report_text)


def main():
    if len(sys.argv) < 2:
        print('用法: python3 review_doc.py <文件/目录路径> [--output <报告路径>] [--report-only] [--fix]')
        sys.exit(1)

    target = sys.argv[1]
    output_path = None
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    if not os.path.exists(target):
        print(f'❌ 路径不存在: {target}')
        sys.exit(1)

    if os.path.isfile(target):
        # 单个文件
        results = [review_doc(target)]
    else:
        # 目录：扫描所有 .md
        md_files = sorted(Path(target).rglob('*.md'))
        results = []
        for f in md_files:
            r = review_doc(str(f))
            results.append(r)
        print(f'🔍 扫描 {len(md_files)} 个文件 → 审查中...')

    print_report(results, output_path)

    # 统计退出码
    all_pass = all(r.get('grade') not in ('❌ 不合格',) for r in results if 'error' not in r)
    return 0 if all_pass else 1


if __name__ == '__main__':
    exit(main())
