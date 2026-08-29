#!/usr/bin/env python3
"""
check-ar-design-trace.py — AR → Design 回溯检查 (Level 2)

验证 ar-001 中声明已实现的 AR (✅) 是否有对应的 design/ 文件支撑：
  - 路径注册：AR 引用的路径（03101-03108）与实际目录一致
  - 设计归属：AR-Px-xxx 的 phase 归属在 design-001 中有对应 section
  - 文件存在：AR 中引用的文件/路径都存在

输出格式：JSON
"""
import re
import json
import sys
from pathlib import Path

WORKSPACE = Path("/home/lzh/cow")
SPEC_DIR = WORKSPACE / "spec"
KNOWLEDGE = WORKSPACE / "knowledge"

def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def parse_ar_reverse_table(text):
    """从 ar-001 §4 逆向映射表提取 AR→状态+SR"""
    ars = {}
    # | AR-P1-001 | Import 目录扫描... | Phase 1 | SR-001, SR-005 | ✅ | P0 |
    pattern = r"\|\s*(AR-\w+-\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*([✅🚧📋])\s*\|\s*(P[012])\s*\|"
    for m in re.finditer(pattern, text):
        ar_id = m.group(1)
        desc = m.group(2).strip()
        phase = m.group(3).strip()
        sr_ref = m.group(4).strip()
        status = m.group(5)
        priority = m.group(6)
        ars[ar_id] = {"desc": desc, "phase": phase, "sr_ref": sr_ref, "status": status, "priority": priority}
    return ars

def check_path_registration(ars):
    """Check 1: AR 引用的路径与实际目录结构一致"""
    issues = []
    path_map = {
        "sources/": "06_others/sources/",
        "knowledge/sources/": "knowledge/06_others/sources/",
        "knowledge/01_survey/": "knowledge/01_survey/",
        "knowledge/02_rd/": "knowledge/02_rd/",
        "knowledge/03_AI/": "knowledge/03_AI/",
        "knowledge/02_rd/00_shared/02_concepts/": "knowledge/02_rd/00_shared/02_concepts/",
        "knowledge/methodology/": "knowledge/methodology/",
        "knowledge/weekly-reports/": "knowledge/weekly-reports/",
        "tmp/bak/": "tmp/bak/",
        "import/": "import/",
        "discover/": "discover/",
        "knowledge/": "knowledge/",
    }
    for ar_id, info in ars.items():
        desc = info["desc"]
        # Check if desc references a path that might be wrong
        if "sources" in desc.lower() and "06_others" not in desc:
            issues.append({
                "type": "POSSIBLE_DEPRECATED_PATH",
                "severity": "WARNING",
                "item": ar_id,
                "detail": f"'{desc}' 可能引用了旧路径 sources/（应为 06_others/sources/）",
                "fix": f"检查 {ar_id} 的描述是否引用旧路径"
            })
    return issues

def check_design_existence(ars):
    """Check 2: ✅ AR 对应的 design 文件是否存在"""
    issues = []
    design_files = {
        "AR-P1": "design-001-system-architecture.md",
        "AR-P2": "design-001-system-architecture.md",
        "AR-P3": "design-001-system-architecture.md",
        "AR-P4": "design-001-system-architecture.md",
        "AR-SYS": "design-001-system-architecture.md",
        "AR-FUT": "design-001-system-architecture.md",
        "AR-ASM": "design-007-skills-scripts-design.md",
        "AR-QSV": "design-007-skills-scripts-design.md",
    }
    for ar_id, info in ars.items():
        if info["status"] != "✅":
            continue
        # Determine which design file should cover it
        prefix = ar_id.rsplit("-", 1)[0]
        expected_design = design_files.get(prefix, "design-001-system-architecture.md")
        design_path = SPEC_DIR / expected_design
        if not design_path.exists():
            issues.append({
                "type": "DESIGN_FILE_MISSING",
                "severity": "ERROR",
                "item": ar_id,
                "detail": f"✅ AR {ar_id} 的预期设计文件 {expected_design} 不存在",
                "fix": f"创建 {expected_design} 或更新 ar-001 中 {ar_id} 的状态"
            })
        else:
            # Check if the design file mentions this AR
            design_text = read_file(design_path)
            if ar_id not in design_text and info["status"] == "✅":
                issues.append({
                    "type": "AR_NOT_IN_DESIGN",
                    "severity": "WARNING",
                    "item": ar_id,
                    "detail": f"✅ AR {ar_id} 在 {expected_design} 中无引用，可能设计文档未同步",
                    "fix": f"在 {expected_design} 中添加对 {ar_id} 的引用或注释"
                })
    return issues

def check_path_registration_files(ars):
    """Check 3: 路径注册表 03101-03108 中的目录都存在"""
    issues = []
    reg_paths = {
        "03101": KNOWLEDGE / "06_others/sources",
        "03102": KNOWLEDGE / "01_survey",
        "03103": KNOWLEDGE / "02_rd",
        "03104": KNOWLEDGE / "03_AI",
        "03105": KNOWLEDGE / "concepts",
        "03106": KNOWLEDGE / "methodology",
        "03107": KNOWLEDGE / "weekly-reports",
        "03108": WORKSPACE / "tmp/bak",
    }
    for code, path in reg_paths.items():
        if not path.exists():
            issues.append({
                "type": "REGISTERED_PATH_MISSING",
                "severity": "ERROR",
                "item": code,
                "detail": f"约束注册表 {code} 路径 '{path.relative_to(WORKSPACE)}' 不存在",
                "fix": f"创建目录或更新约束注册表 {code} 的路径"
            })
    return issues

def main():
    ar_text = read_file(SPEC_DIR / "ar-001-sr-ar-mapping.md")
    if not ar_text:
        print(json.dumps({"status": "ERROR", "summary": "无法读取 ar-001", "details": []}, ensure_ascii=False, indent=2))
        sys.exit(1)

    ars = parse_ar_reverse_table(ar_text)

    all_issues = []
    all_issues.extend(check_path_registration(ars))
    all_issues.extend(check_design_existence(ars))
    all_issues.extend(check_path_registration_files(ars))

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]
    passed_ar = len([a for a in ars.values() if a["status"] == "✅"])

    result = {
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "check_name": "AR-Design Trace (Level 2)",
        "summary": f"AR={len(ars)}(✅{passed_ar}) | Issues={len(errors)}E/{len(warnings)}W",
        "ar_count": len(ars),
        "ar_implemented": passed_ar,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": all_issues,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
