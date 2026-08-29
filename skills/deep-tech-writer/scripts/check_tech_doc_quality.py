#!/usr/bin/env python3
"""
深度技术文档质量自检脚本

对照 deep-tech-writer 六步工作流的质量标准，逐项检查文档。
用法:
    python3 check_tech_doc_quality.py <markdown文件路径>
    python3 check_tech_doc_quality.py <路径> --fix          # 自动修复部分问题
    python3 check_tech_doc_quality.py <路径> --report       # 仅输出报告不检查
"""

import re
import sys
import os
from pathlib import Path


def load_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        return text.splitlines(keepends=True), text


def count_chinese(text):
    """统计中文字符数"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def has_source_citation(filepath, text):
    """检查是否有来源标注"""
    patterns = [
        r'\[来源:', r'\[Source:', r'\[来源:',
        r'^\[[0-9]+\]',           # [1], [2] 等引用格式
        r'https?://',              # URL
        r'参见\s*\[',             # 参见[xxx]
        r'references', r'reference',
        r'参考文献', r'参考来源',
        r'arXiv:', r'ACM\b', r'IEEE',
        r'DOI:',
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def has_changelog(text):
    """检查是否有底部changelog"""
    # 检查最后200行是否有 changelog 或 变更日志 标识
    lines = text.split('\n')
    tail = '\n'.join(lines[-200:])
    patterns = [
        r'#+.*changelog', r'#+.*变更日志', r'#+.*变更记录',
        r'#+.*Changelog', r'#+.*版本记录',
    ]
    for p in patterns:
        if re.search(p, tail, re.IGNORECASE):
            return True
    return False


def has_toc(text):
    """检查是否有目录"""
    # 检查文档前50行是否有类似目录的结构（多个连续的 [xxx](xxx) 链接行）
    lines = text.split('\n')
    header = '\n'.join(lines[:50])

    # 检查是否为目录模式：多行包含 ](/) 或 ](./ 或 ](# 的markdown链接
    toc_links = re.findall(r'\[.*?\]\([/#]', header)
    if len(toc_links) >= 3:
        return True

    # 检查是否有 TOC/目录/目录 标记
    toc_patterns = [
        r'#+.*目录', r'#+.*Contents', r'#+.*TOC',
        r'#+.*index', r'#+.*导航',
        r'<!--.*TOC', r'\[TOC\]',
    ]
    for p in toc_patterns:
        if re.search(p, header, re.IGNORECASE):
            return True
    return False


def _find_knowledge_root(src_abs: Path):
    """从文件绝对路径向上找 knowledge/ 根目录"""
    for parent in src_abs.parents:
        if parent.name == "knowledge":
            return parent
    return None


def has_cross_links(text, filepath, knowledge_dir):
    """检查是否有交叉链接到 knowledge/ 其他文件

    相对路径链接按引用方目录解析（resolve）后，判断目标是否落在
    knowledge/ 根内且非自身文件——修复旧实现"只认字面量 knowledge/
    前缀"导致的相对链接机械误报（W32 P0，全周污染质量口径）。
    """
    links = re.findall(r"\[.*?\]\((.*?)\)", text)
    src_abs = Path(filepath).resolve()
    kroot = _find_knowledge_root(src_abs)
    if kroot is None:
        return False
    for link in links:
        link = link.strip()
        # 跳过空链/纯锚点/外链
        if not link or link.startswith("#") or link.startswith("http://") or link.startswith("https://"):
            continue
        target = link.split("#")[0].strip()
        if not target:
            continue
        try:
            tgt = (src_abs.parent / target).resolve()
        except Exception:
            continue
        # 目标落在 knowledge/ 内，且非自身文件 → 存在交叉链接
        if str(tgt).startswith(str(kroot)) and tgt != src_abs:
            return True
    return False


def check_quantified_data(lines):
    """检查是否有量化数据（数值+单位模式）"""
    # 寻找 "数字+单位" 的模式
    # 常见技术单位
    unit_pattern = r'\d+[\.\d]*(?:[酣倍%]|[KMGTP]?(?:Hz|bps|B|W|V|A|m|s|g|mm|um|nm|inch))'
    found = 0
    for line in lines:
        if re.search(unit_pattern, line):
            found += 1
            if found >= 3:
                return True, found
    return found >= 3, found


def check_code_block_ascii(lines):
    """检查代码块中是否有中文"""
    in_code_block = False
    issues = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block and re.search(r'[\u4e00-\u9fff]', line):
            issues.append((i, line.strip()[:60]))
    return issues


def check_no_unsourced_claims(lines, text):
    """检查文档是否有大量无来源断言（启发式）"""
    # 标记断言模式
    assertion_patterns = [
        r'提升了?\s*\d+', r'降低[了到]\s*\d+', r'达到[了]?\s*\d+',
        r'支持\s*(PCIe|NVLink|InfiniBand|DDR|HBM|CXL)',
        r'是.*的\s*[0-9]+', r'比.*高\s*\d+',
    ]

    # 如果已经有来源引用，跳过此检查
    if has_source_citation('', text):
        return []

    issues = []
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        for p in assertion_patterns:
            if re.search(p, line_stripped):
                issues.append((i, line_stripped[:80]))
                break

    return issues


def check_doc(filepath):
    """对单个文档执行所有质量检查"""
    result = {
        'path': str(filepath),
        'total_lines': 0,
        'total_bytes': 0,
        'ratings': {},
        'pass': True,
        'issues': [],
    }

    if not os.path.exists(filepath):
        result['error'] = f'文件不存在: {filepath}'
        return result

    lines, text = load_lines(filepath)
    total_lines = len(lines)
    result['total_lines'] = total_lines
    result['total_bytes'] = len(text)
    cn_chars = count_chinese(text)

    # ==================== R0: 基础信息 ====================
    cn_ratio = cn_chars / max(len(text), 1) * 100

    # ==================== R1: 原理深度和量化 ====================
    has_quantified, quant_count = check_quantified_data(lines)
    result['ratings']['R1_quantified_data'] = {
        'pass': has_quantified,
        'detail': f'找到 {quant_count} 处量化数据 ≥3 则合格',
    }
    if not has_quantified:
        result['pass'] = False
        result['issues'].append(f'⚠️ R1: 量化数据不足（仅 {quant_count} 处），建议补充数值+单位+基线的量化表述')

    code_issues = check_code_block_ascii(lines)
    result['ratings']['R1_code_ascii'] = {
        'pass': len(code_issues) == 0,
        'detail': f'代码块中中文问题 {len(code_issues)} 处（0 则合格）',
        'locations': code_issues[:10],
    }
    if code_issues:
        result['pass'] = False
        result['issues'].append(f'⚠️ R1: 代码块中有 {len(code_issues)} 处中文，需移出代码块')

    # ==================== R2: 文档结构规范 ====================
    has_src = has_source_citation(filepath, text)
    result['ratings']['R2_source_citation'] = {
        'pass': has_src,
        'detail': '有来源标注' if has_src else '无来源标注',
    }
    if not has_src:
        result['pass'] = False
        result['issues'].append('⚠️ R2: 缺少来源标注，技术文档必须有参考文献/来源引用')

    # changelog 检查（仅 >200 行文件）
    if total_lines > 200:
        has_cl = has_changelog(text)
        result['ratings']['R2_changelog'] = {
            'pass': has_cl,
            'detail': f'文件 {total_lines} 行（>200需changelog）' + (' ✓ 有' if has_cl else ' ✗ 无'),
        }
        if not has_cl:
            result['pass'] = False
            result['issues'].append(f'⚠️ R2: 文件 {total_lines} 行 > 200，但缺少底部 changelog')

    # TOC 检查（仅 >100 行文件）
    if total_lines > 100:
        has_toc_flag = has_toc(text)
        result['ratings']['R2_toc'] = {
            'pass': has_toc_flag,
            'detail': f'文件 {total_lines} 行（>100需TOC）' + (' ✓ 有' if has_toc_flag else ' ✗ 无'),
        }
        if not has_toc_flag:
            result['pass'] = False
            result['issues'].append(f'⚠️ R2: 文件 {total_lines} 行 > 100，但缺少目录(TOC)')

    # 交叉链接（仅 knowledge/ 下的文件）
    if 'knowledge' in str(filepath):
        has_clinks = has_cross_links(text, filepath, 'knowledge')
        result['ratings']['R2_cross_links'] = {
            'pass': has_clinks,
            'detail': '有交叉链接' if has_clinks else '无交叉链接',
        }
        if not has_clinks:
            result['issues'].append('⚠️ R2: 建议添加指向 knowledge/ 其他文件的交叉链接')

    # ==================== R3: 逻辑与断言 ====================
    unsourced = check_no_unsourced_claims(lines, text)
    result['ratings']['R3_unsourced_assertions'] = {
        'pass': len(unsourced) < 3,
        'detail': f'无来源断言 {len(unsourced)} 处（<3 则合格）',
    }
    if len(unsourced) >= 3:
        result['pass'] = False
        result['issues'].append(f'⚠️ R3: 发现 {len(unsourced)} 处无来源断言，需补充出处')

    # 二元对立检查（启发式：是否用了"vs/或/还是"但只有两个选项）
    binary_patterns = re.findall(r'(要么|only two|two options|二元|非此即彼)', text, re.IGNORECASE)
    result['ratings']['R3_binary_opposition'] = {
        'pass': len(binary_patterns) == 0,
        'detail': f'二元对立表述 {len(binary_patterns)} 处（0 则合格，若有需确认是否遗漏中间方案）',
    }

    # ==================== 汇总 ====================
    # 统计通过率
    total_checks = len(result['ratings'])
    passed_checks = sum(1 for v in result['ratings'].values() if v['pass'])
    result['pass_rate'] = f'{passed_checks}/{total_checks}'
    result['score'] = round(passed_checks / max(total_checks, 1) * 100)

    return result


def print_result(result, show_report_only=False):
    """格式化输出检查结果"""
    if 'error' in result:
        print(f'❌ 错误: {result["error"]}')
        return

    fname = result['path']
    status = '✅ PASS' if result['pass'] else '❌ FAIL'
    print(f'\n{"="*60}')
    print(f'📄 {fname}')
    print(f'{"="*60}')
    print(f'  行数: {result["total_lines"]} | 大小: {result["total_bytes"]/1024:.1f}KB')
    print(f'  综合: {status} (得分: {result["score"]}% | 通过: {result["pass_rate"]})')
    print()

    if result['issues']:
        print(f'⚠️ 发现 {len(result["issues"])} 个问题:')
        for issue in result['issues']:
            print(f'  {issue}')
        print()

    if not show_report_only:
        print(f'📊 逐项评分:')
        for key, val in result['ratings'].items():
            icon = '✅' if val['pass'] else '❌'
            detail = val['detail']
            print(f'  {icon} {key}: {detail}')
            if not val['pass'] and 'locations' in val and val['locations']:
                for loc_line, loc_text in val['locations'][:5]:
                    print(f'      → 第{loc_line}行: {loc_text}')

    print('=' * 60)
    print()


def main():
    if len(sys.argv) < 2:
        print('用法: python3 check_tech_doc_quality.py <路径> [--fix] [--report]')
        sys.exit(1)

    target = sys.argv[1]
    show_report_only = '--report' in sys.argv
    enable_fix = '--fix' in sys.argv

    if not os.path.exists(target):
        print(f'❌ 路径不存在: {target}')
        sys.exit(1)

    if os.path.isfile(target):
        results = [check_doc(target)]
    else:
        # 遍历目录下所有 .md 文件
        md_files = list(Path(target).rglob('*.md'))
        results = []
        for f in md_files:
            r = check_doc(str(f))
            results.append(r)
        print(f'🔍 扫描 {len(md_files)} 个文件...')

    # 统计
    total = len(results)
    passed = sum(1 for r in results if r.get('pass', False))
    total_issues = sum(len(r.get('issues', [])) for r in results)

    for r in results:
        print_result(r, show_report_only)

    # 汇总
    print(f'\n{"="*60}')
    print(f'📊 汇总: {passed}/{total} 通过 | {total_issues} 个问题')
    print(f'{"="*60}')
    for r in results:
        issue_count = len(r.get('issues', []))
        icon = '✅' if r.get('pass') else '❌'
        print(f'  {icon} {r["path"]} — {r["score"]}% ({r["pass_rate"]}) [问题: {issue_count}]')

    return 0 if passed == total else 1


if __name__ == '__main__':
    exit(main())
