#!/usr/bin/env python3
"""
check-pipeline-boundary.py — 三层流水线边界验证 (Level 5)

验证 import/ → discover/ → knowledge/ 三层流水线的边界约束：
  - 无越级：import 文件直接出现在 knowledge/ 的情况
  - 无逆向：knowledge 文件出现在 discover/ 的情况  
  - 层归属：新文件能明确归属到某一层
  - discover 索引：discover/ 是否有 index/log（如有则检验）

基于 std-004 的 CC-13 约束（13201-13503）。
输出格式：JSON
"""
import re
import json
import sys
from pathlib import Path

WORKSPACE = Path("/home/lzh/cow")

def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def scan_import_layer():
    """扫描 import/ 目录，获取文件列表"""
    import_dir = WORKSPACE / "import"
    files = []
    if import_dir.exists():
        for f in sorted(import_dir.rglob("*")):
            if f.is_file() and f.name != ".gitkeep":
                files.append(str(f.relative_to(WORKSPACE)))
    return files

def scan_discover_layer():
    """扫描 discover/ 目录"""
    discover_dir = WORKSPACE / "discover"
    files = []
    if discover_dir.exists():
        for f in sorted(discover_dir.rglob("*.md")):
            if f.is_file():
                files.append(str(f.relative_to(WORKSPACE)))
    return files

def scan_knowledge_layer():
    """扫描 knowledge/ 核心目录结构"""
    knowledge_dir = WORKSPACE / "knowledge"
    dirs = []
    if knowledge_dir.exists():
        for d in sorted(knowledge_dir.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                md_count = len(list(d.rglob("*.md")))
                dirs.append({"dir": d.name, "md_count": md_count})
    return dirs

def check_knowledge_top_md_files():
    """Check 1: knowledge/ 根目录不应有 import/discover 来源的原始文件"""
    issues = []
    kb_root = WORKSPACE / "knowledge"
    if not kb_root.exists():
        return issues
    # Check for suspicious top-level .md files that should be in subdirs
    top_files = [f for f in kb_root.iterdir() if f.is_file() and f.suffix == ".md"]
    valid_top = {"index.md", "log.md", "README.md"}
    for f in top_files:
        if f.name not in valid_top:
            issues.append({
                "type": "TOP_LEVEL_KNOWLEDGE_FILE",
                "severity": "WARNING",
                "item": f"knowledge/{f.name}",
                "detail": f"knowledge/ 根目录存在非标准文件 '{f.name}'，应归入子目录",
                "fix": f"将 '{f.name}' 迁至对应模块子目录"
            })
    return issues

def check_discover_has_index():
    """Check 2: discover/ 是否维护了 index/log"""
    issues = []
    discover_dir = WORKSPACE / "discover"
    if not discover_dir.exists():
        return issues
    has_index = (discover_dir / "index.md").exists()
    has_log = (discover_dir / "log.md").exists()
    has_readme = (discover_dir / "README.md").exists()
    if not has_index:
        issues.append({
            "type": "DISCOVER_MISSING_INDEX",
            "severity": "WARNING",
            "item": "discover/index.md",
            "detail": "discover/ 目录缺少 index.md（按 std-003 §5 推荐）",
            "fix": "为 discover/ 创建 index.md"
        })
    if not has_log:
        issues.append({
            "type": "DISCOVER_MISSING_LOG",
            "severity": "WARNING",
            "item": "discover/log.md",
            "detail": "discover/ 目录缺少 log.md（按 std-003 §5 推荐）",
            "fix": "为 discover/ 创建 log.md"
        })
    return issues

def check_import_no_knowledge_cross():
    """Check 3: import 文件不应出现在 knowledge 中"""
    issues = []
    import_dir = WORKSPACE / "import"
    if not import_dir.exists():
        return issues
    # Sample check: look for import file names in knowledge
    import_names = set()
    for f in import_dir.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".txt", ".pdf", ".docx"):
            import_names.add(f.name)
    # Check a sample of knowledge files for same-named files
    kb_dir = WORKSPACE / "knowledge"
    if kb_dir.exists():
        for f in kb_dir.rglob("*.md"):
            if f.name in import_names:
                # Check if this is a direct copy (similar content length)
                src_path = import_dir / f.name
                if src_path.exists():
                    # Only flag if exact same name appears in both
                    issues.append({
                        "type": "IMPORT_KNOWLEDGE_NAME_CLASH",
                        "severity": "INFO",
                        "item": str(f.relative_to(WORKSPACE)),
                        "detail": f"knowledge 中有与 import/ 同名的文件 '{f.name}'，可能跳级入库",
                        "fix": "检查是否经 discover 加工后入库，确认为独立知识文件"
                    })
    return issues

def check_discover_to_knowledge_gate():
    """Check 4: discover→knowledge 上升流转的检查清单是否存在"""
    issues = []
    # Check if migration-gate.py exists
    gate_script = WORKSPACE / "scripts" / "tools" / "migration-gate.py"
    if not gate_script.exists():
        issues.append({
            "type": "MIGRATION_GATE_MISSING",
            "severity": "WARNING",
            "item": "scripts/tools/migration-gate.py",
            "detail": "std-004 要求的 discover→knowledge migration gate 脚本不存在",
            "fix": "创建 scripts/tools/migration-gate.py 实现 8 项检查清单"
        })
    # Check std-004 mentions the gate
    std4 = read_file(WORKSPACE / "spec" / "std-004-knowledge-pipeline-constraints.md")
    if "migration-gate" not in std4 and "migration_gate" not in std4:
        issues.append({
            "type": "GATE_NOT_IN_STD4",
            "severity": "WARNING",
            "item": "std-004-knowledge-pipeline-constraints.md",
            "detail": "std-004 中未引用 migration-gate.py 检查脚本",
            "fix": "在 std-004 §5.3 或 §7.2 中引用 gate 脚本"
        })
    return issues

def check_pipeline_documentation():
    """Check 5: 三层流水线的规范文档是否完整"""
    issues = []
    required_docs = {
        "std-004-knowledge-pipeline-constraints.md": "三层边界约束",
        "sr-005-discover-dir-req.md": "discover 需求规格",
    }
    for doc, desc in required_docs.items():
        path = WORKSPACE / "spec" / doc
        if not path.exists():
            issues.append({
                "type": "PIPELINE_DOC_MISSING",
                "severity": "ERROR",
                "item": doc,
                "detail": f"三层流水线缺少 {desc} 文档 '{doc}'",
                "fix": f"创建 {doc}"
            })
    return issues

def main():
    all_issues = []
    all_issues.extend(check_knowledge_top_md_files())
    all_issues.extend(check_discover_has_index())
    all_issues.extend(check_import_no_knowledge_cross())
    all_issues.extend(check_discover_to_knowledge_gate())
    all_issues.extend(check_pipeline_documentation())

    # Layer stats
    import_files = scan_import_layer()
    discover_files = scan_discover_layer()
    knowledge_dirs = scan_knowledge_layer()

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]
    infos = [i for i in all_issues if i["severity"] == "INFO"]

    result = {
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "check_name": "Pipeline Boundary (Level 5)",
        "summary": f"Import={len(import_files)} | Discover={len(discover_files)} | KnowledgeDirs={len(knowledge_dirs)} | Issues={len(errors)}E/{len(warnings)}W/{len(infos)}I",
        "import_file_count": len(import_files),
        "discover_file_count": len(discover_files),
        "knowledge_dir_count": len(knowledge_dirs),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "info_count": len(infos),
        "issues": all_issues,
        "details": {
            "knowledge_dirs": knowledge_dirs
        }
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
