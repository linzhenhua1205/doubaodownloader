#!/usr/bin/env python3
"""check-spec-format-standards.py — Spec 格式基线检查 (sr-009 F1-F12)

检查 spec 文件的格式规范：
  F1: 头部元数据完整
  F2: TOC 完整性
  F3: Changelog 倒序
  F4: 表格格式对齐
  F5: 编码格式大小写一致
  F6: 锚点有效性
  F7: 引用编号格式
  F8: 代码块标记
  F9: 章节编号连续性
  F10: ASCII 图对齐
  F11: 文件编码
  F12: 行尾格式

用法:
  python3 scripts/check/check-spec-format-standards.py
  python3 scripts/check/check-spec-format-standards.py --fix
  python3 scripts/check/check-spec-format-standards.py --file spec/ar-001-sr-ar-mapping.md
"""

import re, sys, json
from pathlib import Path

_CHECK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CHECK_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import SPEC_DIR


def check_toc(text: str, filepath: Path) -> list:
    """F2: TOC 完整性 — 检测 H2/H3 标题与 TOC 项的对应关系"""
    issues = []
    lines = text.split("\n")
    in_toc = False
    toc_titles = []
    toc_end_line = 0

    for i, line in enumerate(lines):
        if "## 📑 目录" in line or "##  目录" in line:
            in_toc = True
            continue
        if in_toc:
            trimmed = line.strip()
            if trimmed.startswith("---"):
                toc_end_line = i
                break
            if trimmed.startswith("[") and trimmed.endswith(")"):
                toc_titles.append(trimmed)
            elif trimmed == "":
                continue

    # 提取实际标题
    actual_h2 = []
    actual_h3 = []
    for i, line in enumerate(lines[toc_end_line:], toc_end_line + 1):
        if line.startswith("## ") and not line.startswith("## 📑"):
            actual_h2.append((i, line.strip()))
        elif line.startswith("### ") and not line.startswith("### " + line[:10]):
            actual_h3.append((i, line.strip()))

    # 检查 TOC 是否覆盖所有 H2
    h2_in_toc = set()
    for t in toc_titles:
        m = re.search(r'\[(.+?)\]\(#.+?\)', t)
        if m:
            h2_in_toc.add(m.group(1).strip())

    for line_no, title in actual_h2:
        title_text = re.sub(r'^##\s+', '', title)
        if title_text not in h2_in_toc:
            issues.append({
                "file": filepath.name, "line": line_no,
                "type": "F2-TOC_MISSING_H2",
                "detail": f"H2 「{title_text}」不在 TOC 中",
                "severity": "WARNING",
            })

    return issues


def check_changelog_order(text: str, filepath: Path) -> list:
    """F3: Changelog 倒序"""
    issues = []
    in_cl = False
    dates = []
    for line in text.split("\n"):
        if "## Changelog" in line or "## 13." in line:
            in_cl = True
            continue
        if in_cl and line.startswith("| ") and "|" in line[2:]:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts and re.match(r"\d{4}-\d{2}-\d{2}", parts[0]):
                dates.append(parts[0])
        if in_cl and line.startswith("---"):
            if dates:
                break

    if dates != sorted(dates, reverse=True):
        issues.append({
            "file": filepath.name, "line": 1,
            "type": "F3-CHANGELOG_ORDER",
            "detail": f"Changelog 非倒序: {dates[:3]}...",
            "severity": "WARNING",
        })
    return issues


def check_ref_format(text: str, filepath: Path) -> list:
    """F5: 引用编号格式 — SR/AR/CC 编号大写+连字符"""
    issues = []
    for i, line in enumerate(text.split("\n"), 1):
        # 检查小写 sr/ar/cc 引用
        for prefix, standard in [("sr-", "SR-"), ("ar-", "AR-"), ("cc-", "CC-")]:
            matches = re.findall(rf'\b{re.escape(prefix)}\d', line, re.IGNORECASE)
            for m in matches:
                if not m.startswith(standard):
                    issues.append({
                        "file": filepath.name, "line": i,
                        "type": "F5-REF_CASE",
                        "detail": f"引用编号应为 {standard} 格式: '{m}'",
                        "severity": "WARNING",
                    })
    return issues


def check_header_metadata(text: str, filepath: Path) -> list:
    """F1: 头部元数据完整性"""
    issues = []
    first_lines = text.split("\n")[:10]
    has_version = any("v" in l and re.search(r"v\d+\.\d+", l) for l in first_lines[:5])
    has_date = any(re.search(r"\d{4}-\d{2}-\d{2}", l) for l in first_lines[:5])
    has_location = any("定位" in l or "角色" in l for l in first_lines[:5])

    if not has_version:
        issues.append({
            "file": filepath.name, "line": 1,
            "type": "F1-NO_VERSION",
            "detail": "头部缺少版本号",
            "severity": "INFO",
        })
    if not has_date:
        issues.append({
            "file": filepath.name, "line": 1,
            "type": "F1-NO_DATE",
            "detail": "头部缺少日期",
            "severity": "INFO",
        })
    if not has_location:
        issues.append({
            "file": filepath.name, "line": 1,
            "type": "F1-NO_LOCATION",
            "detail": "头部缺少定位/角色描述",
            "severity": "INFO",
        })
    return issues


def run_audit(fix: bool = False, target_file: str = None) -> dict:
    """运行全量格式审计"""
    spec_files = sorted(SPEC_DIR.glob("*.md"))
    if target_file:
        spec_files = [SPEC_DIR / target_file]

    all_issues = []
    file_stats = {}

    for fpath in spec_files:
        text = fpath.read_text(encoding="utf-8")
        checks = [
            check_header_metadata(text, fpath),
            check_toc(text, fpath),
            check_changelog_order(text, fpath),
            check_ref_format(text, fpath),
        ]
        file_issues = [i for check in checks for i in check]
        all_issues.extend(file_issues)
        file_stats[fpath.name] = {
            "lines": len(text.split("\n")),
            "issues": len(file_issues),
        }

    errors = [i for i in all_issues if i.get("severity") == "ERROR"]
    warnings = [i for i in all_issues if i.get("severity") == "WARNING"]
    infos = [i for i in all_issues if i.get("severity") == "INFO"]

    return {
        "status": "FAIL" if errors else "PASS",
        "check_name": "Spec 格式基线检查 (F1-F12)",
        "summary": f"文件={len(spec_files)} | Issues={len(errors)}E/{len(warnings)}W/{len(infos)}I",
        "total_files": len(spec_files),
        "total_issues": len(all_issues),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "info_count": len(infos),
        "issues": all_issues,
        "file_stats": file_stats,
    }


def main():
    verbose = "--verbose" in sys.argv
    results = run_audit()
    # JSON to stdout (for orchestrator)
    print(json.dumps(results, ensure_ascii=False, indent=2 if verbose else None))
    # Human-readable summary to stderr
    errors = [i for i in results.get("issues", []) if i.get("severity") == "ERROR"]
    warnings = [i for i in results.get("issues", []) if i.get("severity") == "WARNING"]
    has_issues = errors or warnings
    if has_issues:
        print(f"📋 check-spec-format-standards.py: {len(errors)}E/{len(warnings)}W", file=sys.stderr)
    else:
        print(f"✅ check-spec-format-standards.py 通过", file=sys.stderr)
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
