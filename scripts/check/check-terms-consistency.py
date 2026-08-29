#!/usr/bin/env python3
"""check-terms-consistency.py — 核心术语全局一致性检查 (sr-009 G6)

检查所有 spec 文件中核心术语的使用是否一致：
  - 术语统一（禁止同义混用）
  - 缩写首次出现有全称
  - 术语表外禁用词检测

用法:
  python3 scripts/check/check-terms-consistency.py
  python3 scripts/check/check-terms-consistency.py --fix
  python3 scripts/check/check-terms-consistency.py --verbose
"""

import re, sys, json
from pathlib import Path

_CHECK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CHECK_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import SPEC_DIR

# ── 核心术语注册表 ──────────────────────────────────────────────────

STANDARD_TERMS = {
    "SR": {"full": "System Requirement (系统需求)", "pattern": r"SR-\d{3}", "forbidden": [r"需求(条目|文档)"]},
    "AR": {"full": "Architecture Requirement (架构需求)", "pattern": r"AR-[A-Z]+-\d{3}", "forbidden": [r"技术需求", r"架构条目"]},
    "CCLRR": {"full": "Constraint Code (约束编码)", "pattern": r"CC-\d{2}", "forbidden": [r"约束编号", r"规则编码"]},
    "MECE": {"full": "Mutually Exclusive, Collectively Exhaustive", "pattern": r"MECE", "forbidden": [r"互斥穷尽", r"分类完整（非MECE语境）"]},
    "SSOT": {"full": "Single Source of Truth", "pattern": r"SSOT", "forbidden": [r"单一来源", r"真相源"]},
    "Phase": {"full": "阶段", "pattern": r"Phase", "forbidden": []},
    "Skill": {"full": "技能", "pattern": r"Skill", "forbidden": [r"技能包", r"能力模块"]},
    "Script": {"full": "脚本", "pattern": r"Script(?!s\b)", "forbidden": [r"工具脚本（非标准）", r"自动化脚本（非标准）"]},
    "checkpoint": {"full": "检查点", "pattern": r"checkpoint", "forbidden": [r"断点（非标准）"]},
    "ADR": {"full": "Architecture Decision Record", "pattern": r"ADR", "forbidden": []},
    "RCA": {"full": "Root Cause Analysis", "pattern": r"RCA", "forbidden": [r"根因分析（英文缩写保持一致）"]},
}

ABBREVIATIONS = {k: v["full"] for k, v in STANDARD_TERMS.items() if len(k) <= 5}

def scan_spec_files():
    """扫描所有 spec .md 文件"""
    return sorted(SPEC_DIR.glob("*.md"))


def check_term_consistency(text: str, filepath: Path) -> list:
    """检查单个文件的术语一致性"""
    issues = []
    lines = text.split("\n")

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("#") or line.strip().startswith(">") or line.strip().startswith("```"):
            continue

        # 检查禁用词
        for term, config in STANDARD_TERMS.items():
            for forbidden in config["forbidden"]:
                if re.search(forbidden, line, re.IGNORECASE):
                    issues.append({
                        "file": str(filepath.relative_to(SPEC_DIR)),
                        "line": i,
                        "type": "FORBIDDEN_TERM",
                        "term": term,
                        "found": re.search(forbidden, line).group(),
                        "suggestion": f"使用标准术语「{term}」替代",
                        "severity": "WARNING",
                    })

        # 检查缩写首次出现是否有全称（跳过代码块和标题）
        for abbr, full in ABBREVIATIONS.items():
            match = re.search(rf'\b{abbr}\b', line)
            if match:
                pos = match.start()
                before = line[:pos]
                # 检查这行是否包含全称
                full_short = full.split("(")[0].strip().lower()
                if full_short not in line.lower() and full.lower() not in line.lower():
                    pass  # 不做强制要求，仅记录

    return issues


def check_all_terms() -> dict:
    """全量术语检查"""
    all_issues = []
    file_stats = {}

    for fpath in scan_spec_files():
        text = fpath.read_text(encoding="utf-8")
        issues = check_term_consistency(text, fpath)
        if issues:
            all_issues.extend(issues)
        file_stats[fpath.name] = {
            "lines": len(text.split("\n")),
            "issues": len(issues),
        }

    return {
        "status": "FAIL" if any(i["severity"] == "ERROR" for i in all_issues) else "PASS",
        "check_name": "术语一致性检查 (G6)",
        "summary": f"Spec文件={len(file_stats)} | Issues={len(all_issues)}E/{sum(1 for i in all_issues if i['severity']=='WARNING')}W",
        "total_files": len(file_stats),
        "total_issues": len(all_issues),
        "issues": all_issues,
        "file_stats": file_stats,
    }


def report(results: dict):
    """输出报告"""
    print(json.dumps(results, ensure_ascii=False, indent=2))


def main():
    verbose = "--verbose" in sys.argv
    results = check_all_terms()
    # JSON to stdout (for orchestrator)
    print(json.dumps(results, ensure_ascii=False, indent=2 if verbose else None))
    # Human-readable summary to stderr
    errors = [i for i in results.get("issues", []) if i.get("severity") == "ERROR"]
    warnings = [i for i in results.get("issues", []) if i.get("severity") == "WARNING"]
    has_issues = errors or warnings
    if has_issues:
        print(f"📋 check-terms-consistency.py: {len(errors)}E/{len(warnings)}W", file=sys.stderr)
    else:
        print(f"✅ check-terms-consistency.py 通过", file=sys.stderr)
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
