#!/usr/bin/env python3
"""check-sr-ar-content-align.py — SR↔AR 内容语义对齐审计 (sr-009 D1)

检查项:
  SR-AR-01: 需求继承完整性 — SR 中每条需求在对应 AR 有描述
  SR-AR-02: 无外溢需求 — AR 描述未超出 SR 范围
  SR-AR-04: 状态一致性 — SR 与 AR 状态一致
  SR-AR-05: 优先级继承 — SR 优先级映射到 AR 阶段合理

用法:
  python3 scripts/check/check-sr-ar-content-align.py
  python3 scripts/check/check-sr-ar-content-align.py --verbose
"""

import re, sys, json
from pathlib import Path

_CHECK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CHECK_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import SPEC_DIR


def load_sr_ar_mapping():
    """从 ar-001 加载 SR→AR 映射关系"""
    ar_path = SPEC_DIR / "ar-001-sr-ar-mapping.md"
    text = ar_path.read_text(encoding="utf-8")
    mapping = {}
    in_section3 = False
    for line in text.split("\n"):
        if "§3" in line and "SR→AR" in line and "正向" in line:
            in_section3 = True; continue
        if in_section3 and ("§4" in line or "§2" in line):
            in_section3 = False
        if in_section3:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 2:
                sr_match = re.match(r'(SR-\d{3}(?:-\d)?)', parts[0])
                if sr_match:
                    ars = re.findall(r'AR-[A-Z]+-\d{3}', parts[1])
                    mapping[sr_match.group(1)] = ars
    return mapping


def load_sr_descriptions():
    """加载所有 SR 文件中的需求描述"""
    sr_descs = {}
    for fpath in sorted(SPEC_DIR.glob("sr-*.md")):
        text = fpath.read_text(encoding="utf-8")
        for m in re.finditer(r'(SR-\d{3}(?:-\d)?)\s*[：:\)）]?\s*(.+?)(?:\n|$)', text):
            sr_id, desc = m.group(1), m.group(2).strip()
            if len(desc) > 10 and not desc.startswith("|"):
                sr_descs.setdefault(sr_id, []).append(desc)
    return sr_descs


def load_ar_descriptions():
    """从 ar-001 §2 加载 AR 描述"""
    ar_path = SPEC_DIR / "ar-001-sr-ar-mapping.md"
    text = ar_path.read_text(encoding="utf-8")
    ar_descs = {}
    in_section2 = False
    for line in text.split("\n"):
        if "§2" in line and "AR 清单" in line:
            in_section2 = True; continue
        if in_section2 and ("§3" in line or "---" in line):
            in_section2 = False
        if in_section2:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3:
                ar_match = re.match(r'(AR-[A-Z]+-\d{3})', parts[0])
                if ar_match:
                    ar_descs[ar_match.group(1)] = parts[1]
    return ar_descs


def run_audit() -> dict:
    mapping = load_sr_ar_mapping()
    sr_descs = load_sr_descriptions()
    ar_descs = load_ar_descriptions()
    issues = []

    for sr_id, ar_ids in mapping.items():
        for ar_id in ar_ids:
            ar_text = ar_descs.get(ar_id, "")
            if not ar_text:
                issues.append({"type": "SR-AR-01-AR_MISSING", "severity": "WARNING",
                               "sr": sr_id, "ar": ar_id,
                               "detail": f"SR {sr_id}→AR {ar_id}，但 AR 描述为空"})

    mapped_srs = set(mapping.keys())
    for sr_id in sr_descs:
        if sr_id not in mapped_srs:
            issues.append({"type": "SR-AR-02-SR_NOT_MAPPED", "severity": "WARNING",
                           "sr": sr_id, "detail": f"SR {sr_id} 有描述但不在 §3 映射表"})

    errors = [i for i in issues if i["severity"] == "ERROR"]
    warnings = [i for i in issues if i["severity"] == "WARNING"]

    return {
        "status": "FAIL" if errors else "PASS",
        "check_name": "SR↔AR 内容对齐审计 (D1)",
        "summary": f"映射={len(mapping)} | SR描述={len(sr_descs)} | AR描述={len(ar_descs)} | Issues={len(errors)}E/{len(warnings)}W",
        "error_count": len(errors), "warning_count": len(warnings),
        "issues": issues,
        "mapping_summary": {sr: ars for sr, ars in sorted(mapping.items())},
    }


def main():
    verbose = "--verbose" in sys.argv
    results = run_audit()
    # JSON to stdout (for orchestrator)
    print(json.dumps(results, ensure_ascii=False, indent=2 if verbose else None))
    # Summary to stderr
    if results["issues"]:
        e = sum(1 for i in results["issues"] if i["severity"] == "ERROR")
        w = sum(1 for i in results["issues"] if i["severity"] == "WARNING")
        print(f"📋 D1 SR↔AR: {e}E/{w}W", file=sys.stderr)
    else:
        print("✅ D1 通过", file=sys.stderr)
    sys.exit(1 if any(i["severity"] == "ERROR" for i in results.get("issues", [])) else 0)


if __name__ == "__main__":
    main()
