#!/usr/bin/env python3
"""
gen-spec-consistency-report.py — Spec 一致性检测报告生成器

编排 6 个 check 脚本，聚合结果为综合报告，输出至：
  knowledge/weekly-reports/07_kb_stat/YYYY-MM-DD-spec-consistency-report.md

层级链：
  Level 1-6: 原 6 层检测链
  Domain D1: SR↔AR 内容语义对齐
  Domain D2: STD↔Design 规则一致性
  Domain D3: 约束编码 CC 映射一致性
  Domain D4: 职责边界冲突审计
  Domain D5: 章节对应关系断层审计
  Format:   文件格式基线检查 (F1-F12)
  Term:     核心术语全局一致性 (G6)
  Mapping:  Spec 映射一致性校验
  Data:     跨层数据一致性审计

Usage:
    python3 scripts/tools/gen-spec-consistency-report.py                    # 运行所有检查并输出到日报
    python3 scripts/tools/gen-spec-consistency-report.py --stdout           # 只输出到 stdout
    python3 scripts/tools/gen-spec-consistency-report.py --level 1,2,3     # 只运行指定层级
    python3 scripts/tools/gen-spec-consistency-report.py --json            # JSON 输出
"""
import subprocess
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/lzh/cow")
CHECK_DIR = WORKSPACE / "scripts" / "check"
OUTPUT_DIR = WORKSPACE / "knowledge" / "weekly-reports" / "07_kb_stat"

CHECK_SCRIPTS = [
    ("check-sr-ar-trace.py", "Level 1: SR → AR 映射完整性"),
    ("check-ar-design-trace.py", "Level 2: AR → Design 回溯"),
    ("check-design-impl-trace.py", "Level 3: Design → Implementation"),
    ("check-constraint-source.py", "Level 4: 约束来源验证"),
    ("check-pipeline-boundary.py", "Level 5: 流水线边界"),
    ("check-cross-layer-refs.py", "Level 6: 跨层引用"),
    # 新增 D1-D5 审计域 (sr-009)
    ("check-sr-ar-content-align.py", "Domain D1: SR↔AR 内容语义对齐"),
    ("check-std-design-consistency.py", "Domain D2: STD↔Design 规则一致性"),
    ("check-cc-consistency.py", "Domain D3: 约束编码 CC 映射一致性"),
    ("check-boundary-conflicts.py", "Domain D4: 职责边界冲突审计"),
    ("check-section-ref-integrity.py", "Domain D5: 章节对应关系断层审计"),
    # 新增格式/术语检查
    ("check-spec-format-standards.py", "Format: 文件格式基线检查 (F1-F12)"),
    ("check-terms-consistency.py", "Term: 核心术语全局一致性 (G6)"),
    ("spec-mapping-validator.py", "Mapping: Spec 映射一致性校验 (Markdown 输出)"),
    ("check-cross-layer-data-consistency.py", "Data: 跨层数据一致性审计"),
]

def run_check(script_name, description):
    """运行单个 check 脚本，返回结果"""
    script_path = CHECK_DIR / script_name
    if not script_path.exists():
        return {
            "status": "ERROR",
            "check_name": description,
            "summary": f"脚本 {script_name} 不存在",
            "error": True
        }

    try:
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return {
                "status": "FAIL",
                "check_name": description,
                "summary": f"脚本执行失败 (exit={result.returncode})",
                "stderr": result.stderr[:500],
                "error": True
            }
        data = json.loads(result.stdout)
        data["check_name"] = description
        data["error"] = False
        return data
    except json.JSONDecodeError as e:
        return {
            "status": "FAIL",
            "check_name": description,
            "summary": f"JSON 解析失败: {e}",
            "raw_output": result.stdout[:500],
            "error": True
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "FAIL",
            "check_name": description,
            "summary": "执行超时 (120s)",
            "error": True
        }
    except FileNotFoundError:
        return {
            "status": "ERROR",
            "check_name": description,
            "summary": "python3 未找到",
            "error": True
        }

def generate_report(results, report_date):
    """生成 Markdown 报告"""
    now = report_date.strftime("%Y-%m-%d %H:%M")
    date_str = report_date.strftime("%Y-%m-%d")

    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = sum(1 for r in results if r.get("status") == "FAIL")
    errors = sum(1 for r in results if r.get("error"))
    total_e = sum(r.get("error_count", 0) for r in results)
    total_w = sum(r.get("warning_count", 0) for r in results)

    lines = []
    lines.append(f"# Spec 一致性检测报告 — {date_str}")
    lines.append("")
    lines.append(f"> **生成时间**: {now} | **检测项**: {total} | **通过**: {passed}/{total} | **错误**: {total_e} | **警告**: {total_w}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary table
    lines.append("## 📊 综合摘要")
    lines.append("")
    lines.append("| 层级 | 检查项 | 状态 | 概要 |")
    lines.append("|:----:|:-------|:----:|:-----|")
    for r in results:
        status_icon = "✅" if r.get("status") == "PASS" else "❌" if r.get("status") == "FAIL" else "⚠️"
        name = r.get("check_name", r.get("check_name", "?"))
        summary = r.get("summary", "N/A")
        lines.append(f"| {name.split(':')[0].strip()} | {name} | {status_icon} | {summary} |")
    lines.append("")

    # Detail per level
    for r in results:
        lines.append(f"---")
        lines.append("")
        status_icon = "✅" if r.get("status") == "PASS" else "❌" if r.get("status") == "FAIL" else "⚠️"
        name = r.get("check_name", "Unknown")
        lines.append(f"## {status_icon} {name}")
        lines.append("")
        lines.append(f"- **状态**: {r.get('status', 'UNKNOWN')}")
        lines.append(f"- **概要**: {r.get('summary', 'N/A')}")
        lines.append(f"- **错误**: {r.get('error_count', 0)} | **警告**: {r.get('warning_count', 0)}")
        lines.append("")

        issues = r.get("issues", [])
        if issues:
            lines.append("### 发现的问题")
            lines.append("")
            lines.append("| 类型 | 严重级 | 项目 | 详情 | 修复建议 |")
            lines.append("|:-----|:------:|:-----|:------|:---------|")
            for iss in issues:
                itype = iss.get("type", "?")
                sev = iss.get("severity", "INFO")
                sev_icon = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🔵"}.get(sev, "⚪")
                item = iss.get("item", "?")
                detail = iss.get("detail", "")[:80]
                fix = iss.get("fix", "")[:60]
                lines.append(f"| {itype} | {sev_icon} {sev} | {item} | {detail} | {fix} |")
            lines.append("")
        else:
            lines.append("> ✅ 未发现问题")
            lines.append("")

    # Summary section
    lines.append("---")
    lines.append("")
    lines.append("## 📈 汇总统计")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|:-----|:----:|")
    for r in results:
        name = r.get("check_name", "?")
        lines.append(f"| {name} — 检查项 | {r.get('check_name', 'N/A')} |")
        lines.append(f"| {name} — 通过 | {r.get('status', '?') == 'PASS'} |")
        lines.append(f"| {name} — 错误数 | {r.get('error_count', 0)} |")
        lines.append(f"| {name} — 警告数 | {r.get('warning_count', 0)} |")
    lines.append(f"| **合计** — 检查项 | {total} |")
    lines.append(f"| **合计** — 通过项 | {passed}/{total} |")
    lines.append(f"| **合计** — 错误 | {total_e} |")
    lines.append(f"| **合计** — 警告 | {total_w} |")
    lines.append("")

    # Changelog
    lines.append("---")
    lines.append("")
    lines.append(f"## Changelog")
    lines.append("")
    lines.append(f"| 日期 | 版本 | 变更说明 |")
    lines.append(f"|:-----|:-----|:---------|")
    lines.append(f"| {date_str} | v1.0 | 首次 Spec 一致性检测报告 |")
    lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Spec 一致性检测报告生成器")
    parser.add_argument("--stdout", action="store_true", help="输出到 stdout 而非文件")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--level", type=str, default="all", help="要运行的层级，逗号分隔如 1,2,3 或 'all'（默认全部）")
    args = parser.parse_args()

    # Select levels
    if args.level == "all":
        selected_scripts = CHECK_SCRIPTS
    else:
        selected = [int(x.strip()) for x in args.level.split(",")]
        selected_scripts = [(s, d) for i, (s, d) in enumerate(CHECK_SCRIPTS, 1) if i in selected]

    # Run checks
    results = []
    for script, desc in selected_scripts:
        print(f"▶ Running: {desc}...", file=sys.stderr)
        result = run_check(script, desc)
        results.append(result)
        status_icon = "✅" if result.get("status") == "PASS" else "❌"
        print(f"  {status_icon} {result.get('summary', 'N/A')}", file=sys.stderr)

    # Generate output
    report_date = datetime.now()
    if args.json:
        report = {
            "report_date": report_date.strftime("%Y-%m-%d"),
            "report_time": report_date.strftime("%H:%M"),
            "total_checks": len(results),
            "passed": sum(1 for r in results if r.get("status") == "PASS"),
            "failed": sum(1 for r in results if r.get("status") == "FAIL"),
            "total_errors": sum(r.get("error_count", 0) for r in results),
            "total_warnings": sum(r.get("warning_count", 0) for r in results),
            "results": results
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    report_text = generate_report(results, report_date)

    if args.stdout:
        print(report_text)
        return

    # Write to file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"{report_date.strftime('%Y-%m-%d')}-spec-consistency-report.md"
    report_path.write_text(report_text, encoding="utf-8")

    print(f"\n✅ 报告已生成: {report_path}", file=sys.stderr)

    # Update index
    index_path = OUTPUT_DIR / "index.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")
        report_line = f"| {len(results)} | [{report_path.name}]({report_path.name}) | 📋 一致性检测 | spec 层间依赖关系一致性审计 |"
        if report_path.name not in index_text:
            # Add before the last log line
            if "|" in index_text:
                # Simple append before Changelog
                lines = index_text.split("\n")
                insert_idx = len(lines)
                for i, line in enumerate(lines):
                    if line.strip().startswith("## Changelog"):
                        insert_idx = i
                        break
                lines.insert(insert_idx, report_line)
                index_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        index_text = f"""# 📚 07_kb_stat 专项报告：Spec 一致性

> **更新日期**: {report_date.strftime('%Y-%m-%d')}
> **报告数**: 1

| # | 报告 | 类型 | 说明 |
|:--:|:-----|:----|:------|
| 1 | [{report_path.name}]({report_path.name}) | 📋 一致性检测 | spec 层间依赖关系一致性审计 |

## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| {report_date.strftime('%Y-%m-%d')} | v1.0 | 创建 |

"""
        index_path.write_text(index_text, encoding="utf-8")
        print(f"  📄 index.md 已创建: {index_path}", file=sys.stderr)

if __name__ == "__main__":
    main()
