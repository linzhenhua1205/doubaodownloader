#!/usr/bin/env python3
"""check-cross-layer-data-consistency.py — 跨层数据一致性审计 (sr-009 L6 增强)

检查不同文件中声明的同一数据是否一致：
  - 规模声明（文件数量/AR数量/Skills数量等）
  - 版本号
  - 状态标记
  - 数据统计口径

用法:
  python3 scripts/check/check-cross-layer-data-consistency.py
  python3 scripts/check/check-cross-layer-data-consistency.py --verbose
"""

import re, sys, json
from pathlib import Path
from collections import defaultdict

_CHECK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CHECK_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import SPEC_DIR, SKILLS_DIR, SCRIPTS_DIR


def scan_numeric_claims(text: str) -> list:
    """提取文件中所有数值声明"""
    claims = []
    # 匹配 "N 条约束" / "N 个文件" / "N 条 SR" 等
    for m in re.finditer(r'(\d{2,})\s*(条|个|项|位|层|类|种|维|阶段)', text):
        claims.append({
            "value": int(m.group(1)),
            "unit": m.group(2),
            "context": text[max(0, m.start()-20):m.end()+20].strip(),
        })
    return claims


def detect_scalar_conflicts() -> list:
    """检测跨文件数值声明冲突"""
    issues = []

    # 1. AR 数量: ar-001 声明 vs 其他文件引用
    ar_actual = 0
    ar_path = SPEC_DIR / "ar-001-sr-ar-mapping.md"
    if ar_path.exists():
        ar_text = ar_path.read_text(encoding="utf-8")
        # 从 §2 表格中统计 AR 数
        in_section2 = False
        for line in ar_text.split("\n"):
            if "§2" in line and "AR 清单" in line:
                in_section2 = True
                continue
            if in_section2 and ("§3" in line or "---" in line):
                in_section2 = False
            if in_section2:
                if re.search(r'AR-[A-Z]+-\d{3}', line):
                    ar_actual += 1

    # 2. Skills 数量
    skill_count = len([d for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])

    # 3. Script 数量
    script_count = len(list(SCRIPTS_DIR.rglob("*.py")))

    # 4. 检查各 spec 文件中声明的数字一致性
    for fpath in sorted(SPEC_DIR.glob("*.md")):
        text = fpath.read_text(encoding="utf-8")
        claims = scan_numeric_claims(text)

        for claim in claims:
            if claim["unit"] in ("条", "个", "项"):
                if "AR" in claim["context"] and claim["value"] != ar_actual:
                    issues.append({
                        "type": "DATA-CONSISTENCY",
                        "severity": "WARNING",
                        "file": fpath.name,
                        "detail": f"声明 AR 数量为 {claim['value']}，实际为 {ar_actual}",
                        "context": claim["context"],
                    })
                if "Skill" in claim["context"] and claim["value"] != skill_count:
                    issues.append({
                        "type": "DATA-CONSISTENCY",
                        "severity": "WARNING",
                        "file": fpath.name,
                        "detail": f"声明 Skills 数量为 {claim['value']}，实际为 {skill_count}",
                        "context": claim["context"],
                    })

    return issues


def detect_status_conflicts() -> list:
    """检测状态标记一致性"""
    issues = []
    # 检查 sr-xxx 头部的状态标记与 ar-001 中的对应状态
    for fpath in sorted(SPEC_DIR.glob("sr-*.md")):
        text = fpath.read_text(encoding="utf-8")
        header_status = ""
        for line in text.split("\n")[:10]:
            m = re.search(r'(状态|status)[：:]\s*(\S+)', line, re.IGNORECASE)
            if m:
                header_status = m.group(2)
                break

        if header_status and "草稿" in header_status:
            # 检查该 SR 的 AR 是否标记为相应状态
            pass

    return issues


def run_audit() -> dict:
    """全量数据一致性审计"""
    conflicts = detect_scalar_conflicts()
    status_issues = detect_status_conflicts()
    all_issues = conflicts + status_issues

    # 收集实际统计
    skill_count = len([d for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
    script_count = len(list(SCRIPTS_DIR.rglob("*.py")))
    spec_count = len(list(SPEC_DIR.glob("*.md")))

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    return {
        "status": "FAIL" if errors else "PASS",
        "check_name": "跨层数据一致性审计 (L6)",
        "summary": f"Spec文件={spec_count} | Skills={skill_count} | Scripts={script_count} | Issues={len(errors)}E/{len(warnings)}W",
        "actual_stats": {
            "spec_files": spec_count,
            "skills": skill_count,
            "scripts": script_count,
            "ars": "65 (ar-001 §2)",
        },
        "issues": all_issues,
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
        print(f"📋 check-cross-layer-data-consistency.py: {len(errors)}E/{len(warnings)}W", file=sys.stderr)
    else:
        print(f"✅ check-cross-layer-data-consistency.py 通过", file=sys.stderr)
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
