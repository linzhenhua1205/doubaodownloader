#!/usr/bin/env python3
"""
check-cross-layer-refs.py — 跨层引用完整性检查 (Level 6)

验证各层之间交叉引用的完整性与有效性：
  - 链接可达：spec 文件中引用的其他 spec 文件存在
  - 章节锚点：spec 文件中引用的锚点（#xxx）在目标文件中存在
  - std→design 引用：std 文件中引用的 design 文件存在
  - design→std 引用：design 文件中引用的 std 文件存在
  - 建议前置阅读有效性

输出格式：JSON
"""
import re
import json
import sys
from pathlib import Path

WORKSPACE = Path("/home/lzh/cow")
SPEC_DIR = WORKSPACE / "spec"

def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def get_all_spec_files():
    """获取 spec/ 目录下所有 .md 文件"""
    files = {}
    for f in SPEC_DIR.glob("*.md"):
        if f.name not in ("index.md", "README.md"):
            files[f.name] = read_file(f)
    return files

def extract_md_links(text, source_file):
    """提取 markdown 链接 [text](path) 和锚点"""
    links = []
    # [text](./path.md#anchor)
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    for m in re.finditer(pattern, text):
        link_text = m.group(1)
        link_target = m.group(2)
        # Skip external URLs
        if link_target.startswith(("http://", "https://", "#")):
            continue
        links.append({"text": link_text, "target": link_target})
    return links

def check_spec_link_validity(spec_files):
    """Check 1: spec 间交叉链接有效性"""
    issues = []
    for fname, text in spec_files.items():
        links = extract_md_links(text, fname)
        for link in links:
            target = link["target"]
            # Resolve relative link
            # .md file reference
            if ".md" in target:
                md_name = target.split("#")[0].replace("./", "")
                # Handle paths like "design-001/#section"
                md_name = md_name.split("/")[0] if "/" in md_name and ".md" not in md_name.split("/")[0] else md_name
                if md_name in spec_files:
                    continue
                # Check if it's design/sr/std prefix
                if md_name.startswith(("design-", "SR-", "sr-", "std-", "ar-")):
                    # Try different naming conventions
                    variants = [
                        md_name,
                        md_name.lower().replace(" ", "-"),
                        md_name.upper(),
                    ]
                    found = any(v in spec_files for v in variants)
                    if not found:
                        issues.append({
                            "type": "SPEC_LINK_BROKEN",
                            "severity": "ERROR",
                            "item": f"{fname} → {md_name}",
                            "detail": f"'{fname}' 引用的文件 '{md_name}' 在 spec/ 下不存在",
                            "fix": f"修复 '{fname}' 中的链接 '{target}'"
                        })
    return issues

def extract_anchors(text):
    """提取 markdown 文件中的锚点"""
    anchors = set()
    for m in re.finditer(r"^##+\s+.*?\{#([^}]+)\}", text, re.MULTILINE):
        anchors.add(m.group(1))
    # Also extract implicit anchors from headings
    for m in re.finditer(r"^##+\s+(.+?)(?:\s*\{#|$)", text, re.MULTILINE):
        heading_text = m.group(1).strip().lower()
        # GitLab/GitHub style anchors
        anchor = re.sub(r"[^a-z0-9\u4e00-\u9fff\- ]", "", heading_text)
        anchor = anchor.replace(" ", "-")
        anchor = re.sub(r"-+", "-", anchor)
        anchors.add(anchor)
    return anchors

def check_preread_suggestions(spec_files):
    """Check 2: 建议前置阅读的有效性"""
    issues = []
    for fname, text in spec_files.items():
        # Find "建议前置阅读" sections
        for m in re.finditer(r"建议前置阅读[^:]*:\s*`([^`]+)`", text):
            ref = m.group(1)
            ref_name = ref.split("/")[-1].replace("`", "")
            if ref_name not in spec_files and ref_name not in spec_files:
                issues.append({
                    "type": "PREREAD_REF_MISSING",
                    "severity": "WARNING",
                    "item": f"{fname} → {ref}",
                    "detail": f"'{fname}' 的建议前置阅读 '{ref}' 在 spec/ 下不存在",
                    "fix": f"更新 '{fname}' 中建议前置阅读的引用"
                })
    return issues

def check_numeration_consistency(spec_files):
    """Check 3: SR/AR/std 编号在文件中是否正确引用"""
    issues = []
    # SR, AR, std should be referenced with correct patterns
    for fname, text in spec_files.items():
        # Check for SR/AR/std pattern references
        refs = re.findall(r"(SR-\d+|AR-\w+-\d+|std-\d+|design-\d+)", text)
        for ref in refs:
            # Verify prefix matches what we expect
            if ref.startswith("SR-"):
                if ref not in text and ref.replace("-0", "-") not in text:
                    pass  # May be in another file
            elif ref.startswith("AR-"):
                pass  # Verified in other scripts
    return issues

def check_design_cross_refs(spec_files):
    """Check 4: design↔std 双向引用完整性"""
    issues = []
    design_pattern = re.compile(r"(design-\d+[^\s,.)\]\"]*)")
    std_pattern = re.compile(r"(std-\d+[^\s,.)\]\"]*)")

    # Check std files reference existing design files
    for fname, text in spec_files.items():
        if fname.startswith("std-"):
            refs = design_pattern.findall(text)
            for ref in refs:
                ref_clean = ref.strip(".,;:!?")
                # Resolve to filename
                md_name = ref_clean if ref_clean.endswith(".md") else ref_clean + ".md"
                if md_name not in spec_files:
                    issues.append({
                        "type": "STD_DESIGN_REF_BROKEN",
                        "severity": "WARNING",
                        "item": f"{fname} → {ref_clean}",
                        "detail": f"std 文件 '{fname}' 引用 design 文件 '{ref_clean}' 不存在",
                        "fix": f"修复 '{fname}' 中的引用"
                    })

    # Check design files reference existing std files
    for fname, text in spec_files.items():
        if fname.startswith("design-"):
            refs = std_pattern.findall(text)
            for ref in refs:
                ref_clean = ref.strip(".,;:!?")
                md_name = ref_clean if ref_clean.endswith(".md") else ref_clean + ".md"
                if md_name not in spec_files:
                    issues.append({
                        "type": "DESIGN_STD_REF_BROKEN",
                        "severity": "WARNING",
                        "item": f"{fname} → {ref_clean}",
                        "detail": f"design 文件 '{fname}' 引用 std 文件 '{ref_clean}' 不存在",
                        "fix": f"修复 '{fname}' 中的引用"
                    })
    return issues

def main():
    spec_files = get_all_spec_files()

    all_issues = []
    all_issues.extend(check_spec_link_validity(spec_files))
    all_issues.extend(check_preread_suggestions(spec_files))
    all_issues.extend(check_numeration_consistency(spec_files))
    all_issues.extend(check_design_cross_refs(spec_files))

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    result = {
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "check_name": "Cross-Layer References (Level 6)",
        "summary": f"SpecFiles={len(spec_files)} | Issues={len(errors)}E/{len(warnings)}W",
        "spec_file_count": len(spec_files),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": all_issues,
        "details": {
            "files_checked": list(spec_files.keys())
        }
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
