#!/usr/bin/env python3
"""
quantitative-check.py — 量化数据标注合规检查器

基于 sr-006 D-03 建议。扫描知识库文档中的量化断言，
检测是否缺失以下要素：数值+单位+来源+基线条件。

检查规则:
  1. 数字后无单位 — 如 "延迟降低30%" 无单位/基线 → 违规
  2. 断言无来源 — 如 "带宽达 800GB/s" 无参考文献/来源标记 → 需要来源
  3. 比较级无基线 — 如 "提升 40%"/"降低 2x" 无参考基准 → 违规
  4. 百分比无上下文 — 如 "99.9% 可用性" 无时间维度 → 标记
  5. 无单位裸数字 — 如 "内存 256" 无 GB/MB → 违规

用法:
  # 检查单个文件
  python3 scripts/check/quantitative-check.py check --file knowledge/07_industry-research/03_server/cxl-chip-industry-deep-dive.md

  # 检查整个目录
  python3 scripts/check/quantitative-check.py check --dir knowledge/07_industry-research/

  # 全量扫描（所有知识库文件，限 --max-files）
  python3 scripts/check/quantitative-check.py check --all --max-files 50

  # 仅报告严重违规（缺失单位和来源）
  python3 scripts/check/quantitative-check.py check --dir knowledge/07_industry-research/ --strict

  # JSON 格式输出
  python3 scripts/check/quantitative-check.py check --file test.md --json

依赖:
  - errorcodes.py
  - 适用于 .md 格式的技术文档
"""
import sys
import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = REPO_ROOT / 'knowledge'

sys.path.insert(0, str(REPO_ROOT / 'scripts'))
from tools.errorcodes import EC, exit_with

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

# ── 正则 ──

# 数字模式：识别各种量化表达
NUM_PATTERN = re.compile(
    r'(?:\b|约|约|近|超|达|仅|共|总计)(\d+(?:[,\.]\d+)?)\s*(?:\b|倍|%|x|X|G|T|M|K|k|W|A|V|Hz|bps|bit|byte|ps|ns|us|ms|s|m|km|cm|mm|nm|W|kW|MW|dB|dBm|°C|°F|GB|TB|PB|EB|MB|KB|Gbps|Tbps|Mbps|Gbps|GB/s|TB/s|MB/s|GBps|TBps)\b'
)

# 带单位的数字
UNIT_NUM = re.compile(
    r'(\d+(?:[,\.]\d+)?)\s*(倍|%|x|X|[GTMKE]?[Bb](?:ps|yte)?|[mμn]?[sWAVHz]|[kMGTPE]?[WVA]|[°]?[CF]|[kMGTP]?[bB][ps]?/s|Gbps|Tbps|Mbps|GB/s|TB/s|MB/s|GBps|TBps|kHz|MHz|GHz|THz|k?W|m?W|MW|GW|TW|kV|V|mV|A|mA|k?A|ps|ns|us|[μu]s|ms|s|min|h|d|yr|km|m|cm|mm|nm|[μu]m|GB|TB|PB|EB|MB|KB|KiB|MiB|GiB|TiB|PiB)'
)

# 百分比
PCT_PATTERN = re.compile(r'(\d+(?:[,\.]\d+)?)\s*%')

# 比较级关键词
COMPARATIVE_WORDS = r'(提升|降低|减少|增加|下降|增长|缩减|扩大|上升|翻.倍|half|double|triple|2x|3x|2×|3×)'

# 来源标记
SOURCE_PATTERNS = [
    r'\[[\d,，\-\s]+\]',        # [1], [1,2], [1-3]
    r'\[来源:',
    r'\[source:',
    r'\{#[\w-]+\}',              # {#ref-cxl-spec}
    r'^>\s*[—\-].*$',            # > — 来源: xxx
    r'数据来源',
    r'Source:',
    r'ref\s+\d+',
    r'\([Ss]ource:',
]

# ── 常见单位列表（用于识别无单位数字） ──
KNOWN_UNITS = [
    '倍', '%', 'x', 'X', 'GB', 'TB', 'PB', 'EB', 'MB', 'KB',
    'Gbps', 'Tbps', 'Mbps', 'GB/s', 'TB/s', 'MB/s', 'GBps', 'TBps', 'MBps',
    'GHz', 'MHz', 'kHz', 'THz',
    'kW', 'MW', 'GW', 'TW', 'W', 'mW',
    'kV', 'V', 'mV', 'A', 'mA',
    'ns', 'us', 'μs', 'ms', 's', 'min', 'h', 'd',
    'km', 'm', 'cm', 'mm', 'nm', 'μm',
    '°C', '°F', 'C', 'F',
    'dB', 'dBm',
    'GiB', 'TiB', 'MiB', 'KiB',
]


def has_source_context(line: str, context_lines: list, idx: int) -> bool:
    """检查是否有来源标记"""
    # 检查当前行
    for pat in SOURCE_PATTERNS:
        if re.search(pat, line):
            return True

    # 检查上下5行
    start = max(0, idx - 5)
    end = min(len(context_lines), idx + 6)
    for i in range(start, end):
        for pat in SOURCE_PATTERNS:
            if re.search(pat, context_lines[i]):
                return True
    return False


def has_comparative_baseline(line: str, context_lines: list, idx: int) -> bool:
    """检查比较级是否有基线"""
    if not re.search(COMPARATIVE_WORDS, line, re.IGNORECASE):
        return True  # 不是比较级，不检查

    # 检查附近是否有 "从X到Y" 或 "相较于/相比/对比" 表达
    baseline_pats = [
        r'从[\d.,\s]+[倍%xXGTMPKEAWHV]',
        r'由[\d.,\s]+[倍%xXGTMPKEAWHV]',
        r'相较于',
        r'相比',
        r'对比',
        r'相对于',
        r'baseline',
        r'基线',
        r'vs\.?\s+',
        r'对比组',
        r'对照组',
    ]

    start = max(0, idx - 3)
    end = min(len(context_lines), idx + 4)
    for i in range(start, end):
        for pat in baseline_pats:
            if re.search(pat, context_lines[i], re.IGNORECASE):
                return True
    return False


def check_file(filepath: Path, strict: bool = False) -> dict:
    """检查单个文件的量化数据合规性"""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except OSError as e:
        return {"file": str(filepath), "error": str(e), "violations": [], "score": 0}

    lines = content.split('\n')
    violations = []
    issues_by_type = {"no_unit": 0, "no_source": 0, "no_baseline": 0,
                      "bare_pct": 0, "total_claims": 0}

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()

        # 跳过代码块、引用块、注释
        if stripped.startswith('```') or stripped.startswith('<!--') \
                or stripped.startswith('>') or stripped.startswith('|'):
            continue
        # 跳过标题和列表标记
        if stripped.startswith('#') or stripped.startswith('-') and len(stripped) < 3:
            continue

        # ── 检查1: 裸数字（无单位） ──
        bare_nums = re.findall(r'(?<!\w)(\d+)(?:\s*)(?!\s*[%倍xXGTMPKEAWHVsmhdWAV°dBCFb.kμn])', stripped)
        for num in bare_nums:
            # 排除年份、版本号、页码等
            if re.match(r'^20\d{2}$', num):  # 年份
                continue
            if re.match(r'^\d+\.\d+$', num):  # 版本号 1.0
                continue
            if len(num) <= 2 and num.isdigit():  # 小型计数 1,2,3
                continue
            violations.append({
                "type": "no_unit",
                "line": line_num,
                "text": stripped[:120],
                "detail": f"裸数字 '{num}' 缺少单位（应如 256GB、100Gbps）",
            })
            issues_by_type["no_unit"] += 1

        # ── 检查2: 含单位的数字 → 检查来源 ──
        for match in UNIT_NUM.finditer(stripped):
            issues_by_type["total_claims"] += 1
            value = match.group(1)
            unit = match.group(2)

            # 百分比检查
            if unit == '%':
                issues_by_type["bare_pct"] += 1
                if strict:
                    violations.append({
                        "type": "bare_pct",
                        "line": line_num,
                        "text": stripped[:120],
                        "detail": f"数值 '{value}%' 无上下文（如 99.9% 可用性 → 需说明是什么的可用性）",
                    })

            # 来源检查
            if not has_source_context(stripped, lines, i):
                violations.append({
                    "type": "no_source",
                    "line": line_num,
                    "text": stripped[:120],
                    "detail": f"断言 '{value}{unit}' 缺少来源标记（如 [1] 或 数据来源:xxx）",
                })
                issues_by_type["no_source"] += 1

            # 比较级基线检查
            if not has_comparative_baseline(stripped, lines, i):
                if re.search(COMPARATIVE_WORDS, stripped, re.IGNORECASE):
                    violations.append({
                        "type": "no_baseline",
                        "line": line_num,
                        "text": stripped[:120],
                        "detail": f"比较级 '{stripped[:60]}' 缺少参考基线（相对于什么？）",
                    })
                    issues_by_type["no_baseline"] += 1

    # 计算质量评分 (0-100)
    total_issues = sum(issues_by_type.values()) - issues_by_type["total_claims"]
    total_lines = len([l for l in lines if l.strip() and not l.strip().startswith(('```', '<!--'))])

    if issues_by_type["total_claims"] == 0:
        score = 100.0  # 无量纲数据
    else:
        # 分数 = max(0, 100 - 违规数/断言数 * 50)
        violation_rate = total_issues / max(issues_by_type["total_claims"], 1)
        score = max(0, 100 - violation_rate * 50)

    return {
        "file": str(filepath.relative_to(REPO_ROOT) if filepath.is_relative_to(REPO_ROOT) else filepath),
        "total_claims": issues_by_type["total_claims"],
        "violations": violations,
        "issues": {k: v for k, v in issues_by_type.items() if k != "total_claims"},
        "total_violations": len(violations),
        "score": round(score, 1),
        "checked_lines": total_lines,
    }


def print_report(result: dict, strict: bool = False, json_output: bool = False):
    """输出检查报告"""
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    filepath = result["file"]
    score = result["score"]
    violations = result["violations"]
    issues = result["issues"]

    if result.get("error"):
        print(f"  ❌ {filepath} — 读取错误: {result['error']}")
        return

    # 评分指标
    if score >= 90:
        grade = "🟢 优秀"
    elif score >= 70:
        grade = "🟡 良好"
    elif score >= 50:
        grade = "🟠 需改进"
    else:
        grade = "🔴 不合格"

    print(f"\n{'─'*60}")
    print(f"  {grade} {filepath}")
    print(f"  量化断言: {result['total_claims']} 个 | 违规: {result['total_violations']} 处 | 评分: {score}/100")
    print(f"  检查行: {result['checked_lines']} 行")

    if issues.get("no_unit", 0) > 0:
        print(f"  📏 裸数字无单位: {issues['no_unit']}")
    if issues.get("no_source", 0) > 0:
        print(f"  📚 断言缺来源: {issues['no_source']}")
    if issues.get("no_baseline", 0) > 0:
        print(f"  📊 比较级缺基线: {issues['no_baseline']}")
    if issues.get("bare_pct", 0) > 0:
        print(f"  📈 百分比缺上下文: {issues['bare_pct']}")

    if strict:
        # 严格模式只显示 no_unit 和 no_source
        display_vs = [v for v in violations if v["type"] in ("no_unit", "no_source")]
    else:
        display_vs = violations

    if display_vs:
        print(f"\n  违规详情 (前30条):")
        for v in display_vs[:30]:
            emoji = {"no_unit": "📏", "no_source": "📚", "no_baseline": "📊",
                     "bare_pct": "📈"}.get(v["type"], "⚠️")
            print(f"  {emoji} L{v['line']} [{v['type']}] {v['detail'][:100]}")
        if len(display_vs) > 30:
            print(f"  ... 及 {len(display_vs)-30} 条违规（使用 --json 查看全部）")

    print(f"{'─'*60}")


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='量化数据标注合规检查器',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    p_check = subparsers.add_parser("check", help="检查量化数据合规性")
    p_check.add_argument("--file", default="", help="单个文件路径")
    p_check.add_argument("--dir", default="", help="目录路径（扫描所有 .md 文件）")
    p_check.add_argument("--all", action="store_true", help="全库扫描")
    p_check.add_argument("--max-files", type=int, default=30,
                         help="最大扫描文件数（--all 时有效）")
    p_check.add_argument("--strict", action="store_true",
                         help="严格模式：仅报告无单位和无来源的严重违规")
    p_check.add_argument("--json", action="store_true", help="JSON 输出")
    p_check.add_argument("--threshold", type=float, default=50.0,
                         help="评分阈值，低于此值标为不合格 (默认: 50)")

    args = parser.parse_args()

    if args.command != "check":
        parser.print_help()
        exit_with(EC.INVALID_ARGS, "请指定子命令")

    files_to_check = []

    if args.file:
        fp = Path(args.file)
        if not fp.exists():
            fp = REPO_ROOT / args.file
        if fp.exists():
            files_to_check.append(fp)
        else:
            exit_with(EC.FILE_NOT_FOUND, f"文件不存在: {args.file}")

    elif args.dir:
        dp = Path(args.dir)
        if not dp.exists():
            dp = REPO_ROOT / args.dir
        if dp.exists():
            files_to_check.extend(sorted(dp.rglob("*.md")))
        else:
            exit_with(EC.DIR_NOT_FOUND, f"目录不存在: {args.dir}")

    elif args.all:
        files_to_check.extend(sorted(KNOWLEDGE_DIR.rglob("*.md")))
        # 限制数量
        if args.max_files:
            files_to_check = files_to_check[:args.max_files]

    else:
        exit_with(EC.INVALID_ARGS, "请指定 --file、--dir 或 --all")

    if not files_to_check:
        exit_with(EC.NO_OUTPUT, "未找到可检查的文件")

    print(f"📊 量化数据合规检查 ({len(files_to_check)} 个文件)")
    print(f"{'='*60}")

    results = []
    total_issues = 0
    fail_count = 0
    no_claims = 0

    for fp in files_to_check:
        # 跳过 index/log/metadata
        if fp.name in ('index.md', 'log.md', 'MIGRATIONS.md'):
            continue
        result = check_file(fp, strict=args.strict)
        results.append(result)

        if not args.json and not args.all:
            print_report(result, strict=args.strict, json_output=args.json)

        total_issues += result["total_violations"]
        if result["total_claims"] == 0:
            no_claims += 1
        if result["score"] < args.threshold:
            fail_count += 1

        # 全量扫描时只输出概要
        if args.all and not args.json:
            grade = "🟢" if result["score"] >= args.threshold else "🔴"
            print(f"  {grade} {result['file'][:70]:<70} {result['score']:>5}/100  (违规:{result['total_violations']})")

    # 汇总报表
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        avg_score = sum(r["score"] for r in results) / max(len(results), 1)
        print(f"📊 检查汇总 ({len(results)} 个文件)")
        print(f"  平均评分: {avg_score:.1f}/100")
        print(f"  总违规数: {total_issues}")
        print(f"  不合格数: {fail_count} (阈值: {args.threshold})")
        print(f"  无量纲文件: {no_claims} (无量化断言)")
        print(f"{'='*60}")

    # 退出码
    if fail_count > 0:
        exit_with(EC.QA_FAIL, f"{fail_count} 个文件不合格")
    elif total_issues > 0:
        exit_with(EC.QA_WARN, f"{total_issues} 处违规")
    else:
        exit_with(EC.SUCCESS, "全部合格")


if __name__ == "__main__":
    main()
