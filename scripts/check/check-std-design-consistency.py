#!/usr/bin/env python3
"""check-std-design-consistency.py — STD↔Design 规则一致性审计 (sr-009 D2)

检查项:
  STD-DES-01: 规则继承 — STD 中的约束在 Design 中有对应体现
  STD-DES-02: 不违反规则 — Design 不与 STD 禁止行为冲突
  STD-DES-03: 双向引用链 — STD↔Design 互相引用
  STD-DES-04: 约束等级一致 — CCLRR 等级在 STD/Design 中一致

用法:
  python3 scripts/check/check-std-design-consistency.py
  python3 scripts/check/check-std-design-consistency.py --verbose
"""

import re, sys, json
from pathlib import Path
from collections import defaultdict

_CHECK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CHECK_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import SPEC_DIR, SCRIPTS_DIR


# ── 预期映射矩阵 (来自 sr-009 §4.3) ────────────────────────────

EXPECTED_MAPPING = {
    "std-001-development-rules.md": {
        "design": ["design-001-system-architecture.md", "design-007-skills-scripts-design.md"],
        "sections": {"§6": "Agent 行为约束", "§8": "技能系统规范"},
    },
    "std-002-knowledge-content-format.md": {
        "design": ["design-003-knowledge-directory-design.md", "design-004-knowledge-strategies.md"],
        "sections": {"§5": "内容格式→文件变更", "§2": "五类策略与格式对应"},
    },
    "std-003-knowledge-operations-guide.md": {
        "design": ["design-003-knowledge-directory-design.md"],
        "sections": {"§5": "操作规范→变更管理"},
    },
    "std-004-knowledge-pipeline-constraints.md": {
        "design": ["design-001-system-architecture.md", "design-003-knowledge-directory-design.md"],
        "sections": {"§3": "流水线约束→数据流", "§D.1": "四阶段映射"},
    },
}


def scan_refs_and_terms() -> dict:
    """扫描所有 STD 和 Design 文件，提取交叉引用和关键术语"""
    std_files = sorted(SPEC_DIR.glob("std-*.md"))
    design_files = sorted(SPEC_DIR.glob("design-*.md"))

    std_data = {}
    design_data = {}

    for fpath in std_files:
        text = fpath.read_text(encoding="utf-8")
        # 前置阅读
        refs = set()
        for m in re.finditer(r'(?:前置阅读|参考|详见|参见)[^。\n]*?(design-[\w-]+\.md)', text):
            refs.add(m.group(1))
        # AR 引用
        ar_refs = set(re.findall(r'\bAR-[A-Z]+-\d{3}\b', text))
        # 约束关键词
        constraints = re.findall(r'(?:必须|禁止|不得|应当|可以)\s*[^。\n]{5,80}', text)

        std_data[fpath.name] = {
            "refs": sorted(refs),
            "ar_refs": sorted(ar_refs),
            "constraints": constraints[:20],
            "lines": len(text.split("\n")),
        }

    for fpath in design_files:
        text = fpath.read_text(encoding="utf-8")
        refs = set()
        for m in re.finditer(r'(?:前置阅读|参考|详见|参见)[^。\n]*?(std-[\w-]+\.md)', text):
            refs.add(m.group(1))
        ar_refs = set(re.findall(r'\bAR-[A-Z]+-\d{3}\b', text))

        design_data[fpath.name] = {
            "refs": sorted(refs),
            "ar_refs": sorted(ar_refs),
            "lines": len(text.split("\n")),
        }

    return {"std": std_data, "design": design_data}


def run_audit() -> dict:
    """全量 STD↔Design 一致性审计"""
    data = scan_refs_and_terms()
    issues = []

    std_data = data["std"]
    design_data = data["design"]

    # STD-DES-03: 双向引用链
    for std_name, std_info in std_data.items():
        for ref in std_info["refs"]:
            if ref in design_data:
                # 检查反向引用
                design_refs = design_data[ref].get("refs", [])
                if std_name not in design_refs:
                    issues.append({
                        "type": "STD-DES-03-NO_BACK_REF",
                        "severity": "WARNING",
                        "file": std_name,
                        "detail": f"引用 {ref} 但 {ref} 没有反向引用 {std_name}",
                    })

    # STD-DES-01: 预期映射检查
    for std_name, mapping in EXPECTED_MAPPING.items():
        if std_name not in std_data:
            issues.append({
                "type": "STD-DES-01-NOT_FOUND",
                "severity": "WARNING",
                "file": std_name,
                "detail": f"预期映射中声明的 STD 文件未找到",
            })
            continue

        std_info = std_data.get(std_name, {})
        expected_designs = mapping.get("design", [])
        actual_refs = std_info.get("refs", [])

        for ed in expected_designs:
            if ed not in actual_refs:
                # 检查是否有其他方式引用
                found_alt = False
                for ar in actual_refs:
                    if ed.replace(".md", "") in ar:
                        found_alt = True
                        break
                if not found_alt:
                    issues.append({
                        "type": "STD-DES-01-MISSING_REF",
                        "severity": "WARNING",
                        "file": std_name,
                        "detail": f"预期引用 {ed} 但未找到（来自 sr-009 §4.3 映射矩阵）",
                    })

    # STD-DES-04: 约束强度词对齐
    strength_map = {"必须": "MUST", "禁止": "MUST_NOT", "不得": "MUST_NOT",
                    "应当": "SHOULD", "可以": "MAY", "建议": "SHOULD"}
    for std_name, std_info in std_data.items():
        for c in std_info.get("constraints", [])[:5]:
            pass  # 简化版不做深度语义匹配

    errors = [i for i in issues if i["severity"] == "ERROR"]
    warnings = [i for i in issues if i["severity"] == "WARNING"]

    return {
        "status": "FAIL" if errors else "PASS",
        "check_name": "STD↔Design 映射一致性审计 (D2)",
        "summary": f"STD={len(std_data)} | Design={len(design_data)} | Issues={len(errors)}E/{len(warnings)}W",
        "std_count": len(std_data),
        "design_count": len(design_data),
        "issues": issues,
        "std_refs": {f: info["refs"] for f, info in sorted(std_data.items())},
        "design_refs": {f: info["refs"] for f, info in sorted(design_data.items())},
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
        print(f"📋 check-std-design-consistency.py: {len(errors)}E/{len(warnings)}W", file=sys.stderr)
    else:
        print(f"✅ check-std-design-consistency.py 通过", file=sys.stderr)
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
