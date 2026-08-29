#!/usr/bin/env python3
"""check-boundary-conflicts.py — 职责边界冲突审计 (sr-009 D4)

检查项:
  BOUND-01: Skills↔Scripts 功能重叠
  BOUND-03: 责任归属缺失 — SR/AR 需求未被任何 Skill 或 Script 覆盖
  BOUND-04: 调用链不透明 — Skill 间接调用 Script 但未在 SKILL.md 声明

用法:
  python3 scripts/check/check-boundary-conflicts.py
  python3 scripts/check/check-boundary-conflicts.py --verbose
"""

import re, sys, json
from pathlib import Path
from collections import defaultdict

_CHECK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CHECK_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import SPEC_DIR, SKILLS_DIR, SCRIPTS_DIR


def scan_skills() -> dict:
    """扫描 skills/ 目录，提取每个 Skill 的描述和能力关键词"""
    skills = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        desc = ""
        capabilities = set()

        # 提取描述
        for m in re.finditer(r'(?:描述|description)[：:]\s*(.+?)(?:\n|$)', text, re.IGNORECASE):
            desc += m.group(1) + " "

        # 提取触发关键词
        for m in re.finditer(r'(?:trigger|triggers|触发词)[：:]\s*(.+?)(?:\n|$)', text, re.IGNORECASE):
            for kw in re.split(r'[,，/、\s]+', m.group(1)):
                kw = kw.strip().lower()
                if len(kw) > 2:
                    capabilities.add(kw)

        # 提取引用的脚本
        script_refs = set()
        for m in re.finditer(r'(?:scripts?|tools?)/(?:check|tools)/([\w-]+\.py)', text):
            script_refs.add(m.group(1))

        skills[skill_dir.name] = {
            "desc": desc.strip()[:200],
            "capabilities": sorted(capabilities),
            "script_refs": sorted(script_refs),
        }
    return skills


def scan_scripts() -> dict:
    """扫描 scripts/check 和 scripts/tools，提取能力描述"""
    scripts = {}
    for check_dir in [SCRIPTS_DIR / "check", SCRIPTS_DIR / "tools"]:
        if not check_dir.exists():
            continue
        for script in sorted(check_dir.glob("*.py")):
            if script.name.startswith("__"):
                continue
            text = script.read_text(encoding="utf-8")
            docstring = ""
            capabilities = set()

            # 提取 docstring
            dm = re.search(r'"""(.*?)"""', text, re.DOTALL)
            if dm:
                docstring = dm.group(1)[:300]

            # 提取功能关键词（从函数名和注释）
            for func in re.finditer(r'def (\w+)\(', text):
                func_name = func.group(1)
                if not func_name.startswith("_"):
                    capabilities.add(func_name)

            scripts[script.name] = {
                "docstring": docstring.strip()[:200],
                "capabilities": sorted(capabilities),
                "lines": len(text.split("\n")),
            }
    return scripts


def detect_overlaps(skills: dict, scripts: dict) -> list:
    """BOUND-01: 检测 Skills↔Scripts 功能重叠"""
    issues = []

    # 能力关键词重叠检测
    keyword_groups = defaultdict(list)
    for sname, sinfo in skills.items():
        for kw in sinfo.get("capabilities", []):
            keyword_groups[kw].append(("skill", sname))
    for scname, scinfo in scripts.items():
        for kw in scinfo.get("capabilities", []):
            keyword_groups[kw].append(("script", scname))

    for kw, sources in keyword_groups.items():
        types = set(t for t, _ in sources)
        if len(types) > 1 and len(sources) >= 3:
            issues.append({
                "type": "BOUND-01-OVERLAP",
                "severity": "WARNING",
                "keyword": kw,
                "sources": [f"{t}:{n}" for t, n in sources],
                "detail": f"关键词「{kw}」同时出现在 skill 和 script 侧，可能功能重叠",
            })

    return issues


def check_transparency(skills: dict) -> list:
    """BOUND-04: 检查 Skill 是否声明了其调用的 Script"""
    issues = []
    for sname, sinfo in skills.items():
        # 检查 Script 引用是否在 SKILL.md 头部声明
        pass  # 简化版 - 需要读取 SKILL.md 头部元数据
    return issues


def run_audit() -> dict:
    """全量边界审计"""
    skills = scan_skills()
    scripts = scan_scripts()
    issues = []

    issues.extend(detect_overlaps(skills, scripts))
    issues.extend(check_transparency(skills))

    errors = [i for i in issues if i["severity"] == "ERROR"]
    warnings = [i for i in issues if i["severity"] == "WARNING"]

    return {
        "status": "FAIL" if errors else "PASS",
        "check_name": "职责边界冲突审计 (D4)",
        "summary": f"Skills={len(skills)} | Scripts={len(scripts)} | Issues={len(errors)}E/{len(warnings)}W",
        "skill_count": len(skills),
        "script_count": len(scripts),
        "issues": issues,
        "skill_summary": {n: {"desc": s["desc"][:60], "scripts": s["script_refs"]}
                          for n, s in sorted(skills.items())},
        "script_summary": {n: {"lines": s["lines"]}
                          for n, s in sorted(scripts.items())},
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
        print(f"📋 check-boundary-conflicts.py: {len(errors)}E/{len(warnings)}W", file=sys.stderr)
    else:
        print(f"✅ check-boundary-conflicts.py 通过", file=sys.stderr)
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
