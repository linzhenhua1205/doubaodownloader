#!/usr/bin/env python3
"""
check-design-impl-trace.py — Design → Implementation 验证 (Level 3)

验证 design/ 文档中声明的 Skills 和 Scripts 是否确实存在：
  - Skills 存在性：design 中引用的每个 skill 在 skills/ 下存在
  - Scripts 存在性：design 中引用的每个 script 在 scripts/ 下存在  
  - 路径正确性：design 中描述的写入路径与实际一致
  - 映射审计：design-007 §4 的 mapping 表与实际扫描一致

输出格式：JSON
"""
import re
import json
import sys
from pathlib import Path

WORKSPACE = Path("/home/lzh/cow")
SPEC_DIR = WORKSPACE / "spec"
SKILLS_DIR = WORKSPACE / "skills"
SCRIPTS_DIR = WORKSPACE / "scripts"

def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def find_skills_dir():
    """扫描 skills/ 下所有有效的 skill 目录"""
    skills = set()
    for p in SKILLS_DIR.iterdir():
        if p.is_dir() and (p / "SKILL.md").exists():
            skills.add(p.name)
    return skills

def find_scripts():
    """扫描 scripts/ 下所有可执行脚本"""
    # Known script directories
    script_dirs = ["check", "tools", "git", "intent_analysis", "discover", "autokb"]
    scripts = set()
    for d in script_dirs:
        p = SCRIPTS_DIR / d
        if p.exists():
            for f in p.iterdir():
                if f.suffix in (".py", ".sh") and f.name != "__init__.py":
                    scripts.add(f"{d}/{f.name}")
    # Root scripts
    for f in SCRIPTS_DIR.iterdir():
        if f.suffix in (".py", ".sh") and f.name != "__init__.py":
            scripts.add(f.name)
    return scripts

def extract_skill_refs(text, source_name):
    """从文本中提取 skill 引用"""
    issues = []
    # Pattern: skill names
    skill_patterns = re.findall(r'(?:skill|技能)\s*[`"\']?([a-z][a-z0-9_-]+[a-z0-9])[`"\']?', text.lower())
    # Also match from SKILL.md paths
    path_patterns = re.findall(r'skills/([a-z][a-z0-9_-]+[a-z0-9])/', text.lower())
    return set(skill_patterns + path_patterns)

def extract_script_refs(text, source_name):
    """从文本中提取 script 引用"""
    issues = []
    # Pattern: scripts/ paths
    script_paths = re.findall(r'scripts/([a-z][a-z0-9_/-]+\.(?:py|sh))', text.lower())
    # Pattern: script names
    script_names = re.findall(r'(?:script|脚本)\s*[`"\']?([a-z][a-z0-9_-]+\.(?:py|sh))[`"\']?', text.lower())
    return set(script_paths + script_names)

def check_skills_existence(design_texts):
    """Check 1: Design 中引用的 skill 存在性"""
    issues = []
    actual_skills = find_skills_dir()
    for fname, text in design_texts.items():
        refs = extract_skill_refs(text, fname)
        for ref in refs:
            # Normalize: remove .md, etc.
            skill_name = ref.replace(".md", "").replace("SKILL", "").strip("-")
            if skill_name in actual_skills:
                continue
            # Check partial match
            matched = [s for s in actual_skills if skill_name in s or s in skill_name]
            if not matched:
                issues.append({
                    "type": "SKILL_NOT_FOUND",
                    "severity": "WARNING",
                    "item": ref,
                    "source": fname,
                    "detail": f"file '{fname}' 引用的 skill '{ref}' 在 skills/ 下不存在",
                    "fix": f"检查引用名称或创建缺失的 skill '{ref}'"
                })
    return issues

def check_scripts_existence(design_texts):
    """Check 2: Design 中引用的 script 存在性"""
    issues = []
    actual_scripts = find_scripts()
    for fname, text in design_texts.items():
        refs = extract_script_refs(text, fname)
        for ref in refs:
            if ref in actual_scripts:
                continue
            # Try root level
            if ref.split("/")[-1] in actual_scripts:
                continue
            issues.append({
                "type": "SCRIPT_NOT_FOUND",
                "severity": "WARNING",
                "item": ref,
                "source": fname,
                "detail": f"file '{fname}' 引用的 script '{ref}' 在 scripts/ 下不存在",
                "fix": f"检查引用名称或创建缺失的 script '{ref}'"
            })
    return issues

def check_design_paths(design_texts):
    """Check 3: Design 中描述的路径与实际一致"""
    issues = []
    path_checks = {
        "knowledge/06_others/sources/": (WORKSPACE / "knowledge/06_others/sources").exists(),
        "knowledge/01_survey/": (WORKSPACE / "knowledge/01_survey").exists(),
        "knowledge/02_rd/": (WORKSPACE / "knowledge/02_rd").exists(),
        "knowledge/weekly-reports/": (WORKSPACE / "knowledge/weekly-reports").exists(),
        "tmp/bak/": (WORKSPACE / "tmp/bak").exists(),
        "import/": (WORKSPACE / "import").exists(),
        "discover/": (WORKSPACE / "discover").exists(),
        "scripts/check/": (SCRIPTS_DIR / "check").exists(),
        "scripts/tools/": (SCRIPTS_DIR / "tools").exists(),
        "spec/": SPEC_DIR.exists(),
        "knowledge/02_rd/00_shared/02_concepts/": (WORKSPACE / "knowledge/02_rd/00_shared/02_concepts").exists(),
        "knowledge/methodology/": (WORKSPACE / "knowledge/methodology").exists(),
        "skills/": SKILLS_DIR.exists(),
    }
    # Check paths referenced in design-007 mapping section
    d7_text = design_texts.get("design-007-skills-scripts-design.md", "")
    mapping_text = d7_text
    for path_str, exists in path_checks.items():
        if path_str in mapping_text and not exists:
            issues.append({
                "type": "PATH_REFERENCED_BUT_NOT_EXISTS",
                "severity": "ERROR",
                "item": path_str,
                "source": "design-007-skills-scripts-design.md",
                "detail": f"mapping 表引用路径 '{path_str}' 但实际不存在",
                "fix": f"创建路径 '{path_str}' 或更新设计文档引用"
            })
    return issues

def check_mapping_audit(design_texts):
    """Check 4: design-007 §4 mapping 表中 path 引用的目录存在"""
    issues = []
    d7_text = design_texts.get("design-007-skills-scripts-design.md", "")
    # Extract script paths from mapping tables
    script_refs = set(re.findall(r'scripts/([^\s\)\]\|]+)', d7_text))
    for ref in script_refs:
        p = SCRIPTS_DIR / ref
        if not p.exists():
            issues.append({
                "type": "MAPPING_SCRIPT_MISSING",
                "severity": "ERROR",
                "item": f"scripts/{ref}",
                "source": "design-007-skills-scripts-design.md",
                "detail": f"design-007 §4 mapping 表引用的 scripts/{ref} 不存在",
                "fix": f"创建缺失脚本或更新 mapping 表"
            })
    return issues

def main():
    design_files = [
        "design-001-system-architecture.md",
        "design-003-knowledge-directory-design.md",
        "design-004-knowledge-strategies.md",
        "design-005-scheduler-reliability.md",
        "design-006-token-optimization.md",
        "design-007-skills-scripts-design.md",
        "meth-001-architecture-methodology.md",
    ]
    design_texts = {}
    for f in design_files:
        text = read_file(SPEC_DIR / f)
        if text:
            design_texts[f] = text

    all_issues = []
    all_issues.extend(check_skills_existence(design_texts))
    all_issues.extend(check_scripts_existence(design_texts))
    all_issues.extend(check_design_paths(design_texts))
    all_issues.extend(check_mapping_audit(design_texts))

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    actual_skills = find_skills_dir()
    actual_scripts = find_scripts()

    result = {
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "check_name": "Design-Implementation Trace (Level 3)",
        "summary": f"DesignFiles={len(design_files)} | Skills={len(actual_skills)} | Scripts={len(actual_scripts)} | Issues={len(errors)}E/{len(warnings)}W",
        "design_file_count": len(design_files),
        "actual_skills_count": len(actual_skills),
        "actual_scripts_count": len(actual_scripts),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": all_issues,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
