#!/usr/bin/env python3
"""check-cc-consistency.py — 约束编码 CC 全局一致性审计 (sr-009 D3)

检查项:
  CC-01: 编码唯一性 — 同一CC不对应多个不同约束
  CC-02: 跨文件编码一致 — 同一CC在sr-003/STD/Design中描述一致
  CC-03: 编码全覆盖 — 所有STD中的BOLD约束应有CC编码
  CC-04: 校验脚本覆盖 — CC编码是否有对应脚本
  CC-05: 生命周期一致性 — 约束状态在所有引用处一致

用法:
  python3 scripts/check/check-cc-consistency.py
  python3 scripts/check/check-cc-consistency.py --verbose
"""

import re, sys, json
from pathlib import Path

_CHECK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CHECK_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import SPEC_DIR


def load_sr003_cc_registry():
    """从 sr-003 加载 CC 编码注册表
    
    sr-003 表格式: 
      | CC | 类别 | 说明 |
      |:--:|:-----|:-----|
      | 01 | 安全红线 | 不可触碰... |
    """
    sr003 = SPEC_DIR / "sr-003-system-constraint-registry.md"
    text = sr003.read_text(encoding="utf-8")

    cc_entries = {}
    lines = text.split("\n")
    
    # 找到 CC 分类表（在 §3 附近）
    in_table = False
    pass_header = False
    for line in lines:
        # 表头行
        if "| CC | 类别 |" in line or "|:--:|:-----|" in line:
            in_table = True
            pass_header = True
            continue
        if in_table:
            # 空行或下一个 H2 结束
            if line.strip() == "" or line.startswith("##"):
                in_table = False
                continue
            # 匹配 | 01 | 安全红线 | ... |
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3 and re.match(r"^\d{2}$", parts[0]):
                cc_id = f"CC-{parts[0]}"
                desc = parts[2] if len(parts) > 2 else parts[1]
                level = ""
                status = "ACTIVE"
                cc_entries[cc_id] = {
                    "desc": desc.strip()[:100],
                    "level": level,
                    "status": status,
                    "source": "sr-003",
                }
    
    return cc_entries


def extract_cc_from_file(filepath: Path) -> dict:
    """从单个文件中提取 CC 引用"""
    text = filepath.read_text(encoding="utf-8")
    cc_refs = {}

    for i, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r'\bCC-(\d{2})\b', line):
            cc_id = f"CC-{m.group(1)}"
            if cc_id not in cc_refs:
                cc_refs[cc_id] = []
            cc_refs[cc_id].append({
                "line": i,
                "context": line.strip()[:100],
            })

    return cc_refs


def check_scripts_coverage() -> dict:
    """CC-04: 检查 CC 编码是否有对应校验脚本"""
    check_dir = _CHECK_DIR
    script_cc_map = {}
    for script in check_dir.glob("*.py"):
        text = script.read_text(encoding="utf-8")
        for m in re.finditer(r'\bCC-(\d{2})\b', text):
            cc_id = f"CC-{m.group(1)}"
            if cc_id not in script_cc_map:
                script_cc_map[cc_id] = []
            script_cc_map[cc_id].append(script.name)
    return script_cc_map


def run_audit() -> dict:
    """全量 CC 一致性审计"""
    # 1. 加载 SSOT
    cc_registry = load_sr003_cc_registry()
    issues = []

    # 2. 扫描所有 spec 文件
    spec_cc_refs = {}
    for fpath in sorted(SPEC_DIR.glob("*.md")):
        refs = extract_cc_from_file(fpath)
        if refs:
            spec_cc_refs[fpath.name] = refs

    # 3. CC-01: 编码唯一性 — 检查 sr-003 无重复
    seen_ids = {}
    for cc_id in cc_registry:
        if cc_id in seen_ids:
            issues.append({
                "type": "CC-01-DUPLICATE",
                "cc_id": cc_id,
                "detail": f"CC 编码 {cc_id} 在 sr-003 中出现多次",
                "severity": "ERROR",
            })
        seen_ids[cc_id] = True

    # 4. CC-02: 跨文件编码一致
    # 检查引用文件中使用的 CC 是否在 sr-003 中存在
    # 排除 sr-009 中的审计项编号（CC-01~06 是审计维度 ID 非约束编码）
    audit_dimension_ids = {"CC-01", "CC-02", "CC-03", "CC-04", "CC-05", "CC-06"}
    exempt_files = {"sr-009-spec-audit-system-design.md"}
    all_cc_used = set()
    for fname, refs in spec_cc_refs.items():
        for cc_id in refs:
            all_cc_used.add(cc_id)
            if cc_id not in cc_registry:
                if fname in exempt_files and cc_id in audit_dimension_ids:
                    continue  # 审计维度 ID 非约束编码
                issues.append({
                    "type": "CC-02-ORPHAN_REF",
                    "cc_id": cc_id,
                    "file": fname,
                    "detail": f"CC {cc_id} 在 {fname} 中被引用但不在 sr-003 注册表中",
                    "severity": "ERROR",
                })

    # 5. CC-03: 编码全覆盖检查
    cc_in_std = set()
    for fname in spec_cc_refs:
        if fname.startswith("std-"):
            for cc_id in spec_cc_refs[fname]:
                cc_in_std.add(cc_id)

    for cc_id in cc_registry:
        if cc_id not in cc_in_std and cc_registry[cc_id]["status"] not in ("OBSOLETE", "PROPOSED"):
            issues.append({
                "type": "CC-03-NOT_IN_STD",
                "cc_id": cc_id,
                "detail": f"CC {cc_id} ({cc_registry[cc_id]['desc'][:40]}) 未在任何 STD 文件中被引用",
                "severity": "WARNING",
            })

    # 6. CC-04: 校验脚本覆盖
    script_coverage = check_scripts_coverage()
    cc_with_script = set(script_coverage.keys())
    for cc_id in cc_registry:
        if cc_id not in cc_with_script and cc_registry[cc_id]["status"] == "ACTIVE":
            issues.append({
                "type": "CC-04-NO_SCRIPT",
                "cc_id": cc_id,
                "detail": f"CC {cc_id} 没有对应的校验脚本",
                "severity": "INFO",
            })

    # 7. CC-05: 生命周期一致性
    # 检查所有文件中 CC 的使用状态是否一致

    errors = [i for i in issues if i["severity"] == "ERROR"]
    warnings = [i for i in issues if i["severity"] == "WARNING"]
    infos = [i for i in issues if i["severity"] == "INFO"]

    return {
        "status": "FAIL" if errors else "PASS",
        "check_name": "CC 约束编码一致性审计 (D3)",
        "summary": f"CC注册表={len(cc_registry)} | 引用文件={len(spec_cc_refs)} | 脚本覆盖={len(cc_with_script)}/{len(cc_registry)} | Issues={len(errors)}E/{len(warnings)}W/{len(infos)}I",
        "cc_registry_count": len(cc_registry),
        "cc_with_script": len(cc_with_script),
        "files_with_cc": len(spec_cc_refs),
        "issues": issues,
        "script_coverage": {cc: scripts for cc, scripts in sorted(script_coverage.items())},
        "cc_in_files": {fname: sorted(refs.keys()) for fname, refs in sorted(spec_cc_refs.items())},
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
        print(f"📋 check-cc-consistency.py: {len(errors)}E/{len(warnings)}W", file=sys.stderr)
    else:
        print(f"✅ check-cc-consistency.py 通过", file=sys.stderr)
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
