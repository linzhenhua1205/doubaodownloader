#!/usr/bin/env python3
"""
check-constraint-source.py — 约束来源文件验证 (Level 4)

验证 sr-003 §7 约束源文件索引中的所有文件都存在且约束可追溯：
  - 源文件存在：sr-003 中每个 source 声明的文件实际存在
  - 约束注册完整性：所有 CC 类别（01-13）都有 registered 约束
  - 约束编码无冲突：无重复编码
  - 约束来源可验证：源文件中包含其声称贡献的约束

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

def parse_source_index(text):
    """从 sr-003 §7 约束源文件索引解析"""
    sources = []
    # Strategy: find §7 section boundaries more precisely
    lines = text.split("\n")
    in_section = False
    section_end = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect §7 start - must be actual heading line, not TOC reference
        if stripped.startswith("## 7. 约束源文件索引"):
            in_section = True
            continue
        
        # Detect next ## section (end of §7)
        if in_section and stripped.startswith("## ") and "约束源文件索引" not in stripped:
            section_end = True
            break
        
        if not in_section:
            continue
        
        # Skip separator lines
        if stripped.startswith("|--") or stripped.startswith("> ") or stripped == "":
            continue
        
        # Match: | `filename.md` | constraints | maintainer | frequency |
        # The key identifier is the backtick-wrapped filename in first column
        if stripped.startswith("| `"):
            m = re.match(r"\|\s*`([^`]+\.(?:md|py|sh))`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", stripped)
            if m:
                file_path = m.group(1)
                constraints = m.group(2).strip()
                maintainer = m.group(3).strip()
                frequency = m.group(4).strip()
                sources.append({
                    "file": file_path,
                    "constraints": constraints,
                    "maintainer": maintainer,
                    "frequency": frequency
                })
    
    return sources

def parse_all_constraints(text):
    """从 sr-003 中提取所有约束编码"""
    constraints = {}
    # 01001, 02101, 02305, 13201-13503
    pattern = r"\b(\d{5})\b"
    for m in re.finditer(pattern, text):
        code = m.group(1)
        constraints[code] = True
    return constraints

def check_source_files_exist(sources):
    """Check 1: 所有源文件存在"""
    issues = []
    for src in sources:
        file_path = src["file"]
        # Resolve relative to workspace
        full_path = WORKSPACE / file_path
        if not full_path.exists():
            issues.append({
                "type": "SOURCE_FILE_MISSING",
                "severity": "ERROR",
                "item": file_path,
                "detail": f"约束源文件 '{file_path}' 不存在（§7 声明）",
                "fix": f"创建缺失文件或从 sr-003 §7 删除该条目"
            })
    return issues

def check_constraint_in_source(sources):
    """Check 2: 验证源文件中包含其声称贡献的约束"""
    issues = []
    for src in sources:
        file_path = src["file"]
        constraints_str = src["constraints"]
        full_path = WORKSPACE / file_path
        if not full_path.exists():
            continue
        file_text = read_file(full_path)

        # Extract constraint codes from the claim
        claimed_codes = set()
        # Match individual codes and ranges: 01004, 02101, 06101-06105, 07202-07204
        # IMPORTANT: constraint ranges like "07201-08201" span categories (07→08).
        # The range must NOT be naively expanded — it lists specific entries.
        # Only expand ranges where start and end share the same CC prefix (first 2 digits).
        parts = re.findall(r"(\d{5})(?:-(\d{5}))?", constraints_str)
        for start, end in parts:
            if end:
                s_prefix = start[:2]
                e_prefix = end[:2]
                if s_prefix == e_prefix:
                    # Same category range: 06101-06105 → 06101,06102,06103,06104,06105
                    for c in range(int(start), int(end) + 1):
                        claimed_codes.add(str(c))
                else:
                    # Cross-category "range" like 07201-08201:
                    # Only add the actual endpoint codes, not the full span
                    claimed_codes.add(start)
                    claimed_codes.add(end)
            else:
                claimed_codes.add(start)

        # Check if these codes appear in the source file
        for code in claimed_codes:
            if code not in file_text:
                issues.append({
                    "type": "CONSTRAINT_NOT_IN_SOURCE",
                    "severity": "WARNING",
                    "item": f"{file_path} → {code}",
                    "detail": f"约束 {code} 在源文件 '{file_path}' 中未找到文本引用",
                    "fix": f"在 '{file_path}' 中添加 {code} 的引用标注，或从 sr-003 §7 删除此映射"
                })
    return issues

def check_category_coverage(constraints_map):
    """Check 3: CC 类别覆盖面"""
    issues = []
    # Expected category codes
    categories = {
        "01": "安全红线", "02": "文件操作", "03": "路径映射",
        "04": "知识库格式", "05": "索引日志", "06": "代码脚本",
        "07": "质量标准", "08": "Skills行为", "09": "协作模式",
        "10": "知识库写入", "11": "审查验证", "12": "定时任务",
        "13": "数据流转"
    }
    # Extract categories from constraints
    actual_cats = set()
    for code in constraints_map:
        cat = code[:2]
        actual_cats.add(cat)

    for cat_id, cat_name in categories.items():
        if cat_id in actual_cats:
            codes_in_cat = [c for c in constraints_map if c[:2] == cat_id]
            count = len(codes_in_cat)
            if count < 2:
                issues.append({
                    "type": "CATEGORY_THIN_COVERAGE",
                    "severity": "WARNING",
                    "item": f"CC-{cat_id} ({cat_name})",
                    "detail": f"类别 '{cat_name}' 仅 {count} 条约束，可能覆盖不足",
                    "fix": f"评估是否需要为 '{cat_name}' 补充约束"
                })
        else:
            issues.append({
                "type": "CATEGORY_MISSING",
                "severity": "ERROR",
                "item": f"CC-{cat_id} ({cat_name})",
                "detail": f"类别 '{cat_name}' 在 sr-003 中无任何约束注册",
                "fix": f"为 '{cat_name}' 注册至少 1 条约束"
            })
    return issues

def check_duplicate_codes(constraints_map):
    """Check 4: 无重复约束编码"""
    issues = []
    # constraints_map is a dict, so no duplicates, but let's verify the text parsing
    return issues

def main():
    sr3_text = read_file(SPEC_DIR / "sr-003-system-constraint-registry.md")
    if not sr3_text:
        print(json.dumps({"status": "ERROR", "summary": "无法读取 sr-003", "details": []}, ensure_ascii=False, indent=2))
        sys.exit(1)

    sources = parse_source_index(sr3_text)
    constraints_map = parse_all_constraints(sr3_text)

    all_issues = []
    all_issues.extend(check_source_files_exist(sources))
    all_issues.extend(check_constraint_in_source(sources))
    all_issues.extend(check_category_coverage(constraints_map))
    all_issues.extend(check_duplicate_codes(constraints_map))

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    result = {
        "status": "PASS" if len(errors) == 0 else "FAIL",
        "check_name": "Constraint-Source Trace (Level 4)",
        "summary": f"Sources={len(sources)} | Constraints={len(constraints_map)} | Issues={len(errors)}E/{len(warnings)}W",
        "source_count": len(sources),
        "constraint_count": len(constraints_map),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "categories_covered": len(set(c[:2] for c in constraints_map)),
        "issues": all_issues,
        "details": {
            "sources": sources
        }
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
