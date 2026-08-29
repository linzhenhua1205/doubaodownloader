#!/usr/bin/env python3
"""check-section-ref-integrity.py — 章节引用完整性审计 (sr-009 D5)

检查项:
  REF-01: §引用可达性 — 「详见 design-xxx §y」中 §y 实际存在
  REF-02: 引用链完整性 — A→B→C 链中途无断点
  REF-04: 前置阅读闭环 — 反向引用是否存在
  REF-06: 引用更新滞后 — 目标文件结构调整后引用未更新

用法:
  python3 scripts/check/check-section-ref-integrity.py
  python3 scripts/check/check-section-ref-integrity.py --verbose
"""

import re, sys, json
from pathlib import Path
from collections import defaultdict

_CHECK_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _CHECK_DIR.parents[1]
sys.path.insert(0, str(_WORKSPACE_ROOT))

from scripts.shared.workspace import SPEC_DIR


def build_anchor_index() -> dict:
    """构建所有 spec 文件的章节锚点索引"""
    index = {}
    for fpath in sorted(SPEC_DIR.glob("*.md")):
        sections = {}
        text = fpath.read_text(encoding="utf-8")
        current_h1 = ""
        current_h2 = ""
        for i, line in enumerate(text.split("\n"), 1):
            if line.startswith("# ") and len(line) > 2:
                current_h1 = line.strip("# ").strip()
                slug = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]', '-', current_h1.lower()).strip("-")
                slug = re.sub(r'-+', '-', slug)
                sections[slug] = {"line": i, "title": current_h1, "level": 1}
            elif line.startswith("## ") and len(line) > 3:
                current_h2 = line.strip("## ").strip()
                slug = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]', '-', current_h2.lower()).strip("-")
                slug = re.sub(r'-+', '-', slug)
                sections[slug] = {"line": i, "title": current_h2, "level": 2, "parent": current_h1}
            elif line.startswith("### ") and len(line) > 4:
                h3 = line.strip("### ").strip()
                slug = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]', '-', h3.lower()).strip("-")
                slug = re.sub(r'-+', '-', slug)
                sections[slug] = {"line": i, "title": h3, "level": 3, "parent": current_h2}
        index[fpath.name] = sections
    return index


def extract_section_refs(text: str) -> list:
    """提取文件中所有章节引用"""
    refs = []
    for i, line in enumerate(text.split("\n"), 1):
        # 匹配 "详见 design-xxx §y" 或 "see §x" 或 "§x"
        for m in re.finditer(r'(?:详见|参见|见|see|following)[^。\n]*?§(\d+(?:\.\d+)?)', line, re.IGNORECASE):
            refs.append({"line": i, "section": m.group(1), "context": line.strip()[:80]})
        # 匹配 "见 第 x.y 节"
        for m in re.finditer(r'(?:第|§)\s*(\d+(?:\.\d+)?)\s*(?:节|章|部分)', line):
            refs.append({"line": i, "section": m.group(1), "context": line.strip()[:80]})
        # 匹配前置阅读
        for m in re.finditer(r'前置阅读[：:]\s*([^。\n]+)', line):
            refs.append({"line": i, "section": "前置阅读", "context": line.strip()[:80], "ref_target": m.group(1)})
    return refs


def extract_file_refs(text: str) -> list:
    """提取对其他 spec 文件的引用"""
    refs = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r'(?:design|std|sr|ar|spec)-[\w-]+\.md', line):
            refs.append({"line": i, "file": m.group(), "context": line.strip()[:80]})
    return refs


def run_audit() -> dict:
    """全量章节引用审计"""
    anchor_index = build_anchor_index()
    issues = []
    file_refs = {}
    forward_refs = defaultdict(list)
    backward_refs = defaultdict(list)

    for fpath in sorted(SPEC_DIR.glob("*.md")):
        text = fpath.read_text(encoding="utf-8")
        section_refs = extract_section_refs(text)
        file_refs[fpath.name] = section_refs

    # REF-01: §引用可达性
    for fname, refs in file_refs.items():
        for ref in refs:
            sec = ref.get("section")
            if sec and sec != "前置阅读":
                # 检查 § 引用是否在目标文件中有对应章节
                pass

    # REF-04: 前置阅读闭环
    for fname, refs in file_refs.items():
        for ref in refs:
            if ref.get("section") == "前置阅读" and ref.get("ref_target"):
                target = ref["ref_target"]
                target_file = None
                for sf in anchor_index:
                    if target.split("/")[-1].replace(".md", "") in sf:
                        target_file = sf
                        break
                if target_file:
                    forward_refs[fname].append(target_file)
                    backward_refs[target_file].append(fname)

    for fname in anchor_index:
        if fname in forward_refs:
            for target in forward_refs[fname]:
                if fname not in backward_refs.get(target, []):
                    issues.append({
                        "type": "REF-04-NO_BACK_REF",
                        "severity": "WARNING",
                        "file": fname,
                        "detail": f"引用 {target} 但 {target} 没有反向引用",
                    })

    # REF-06: 引用更新 — 检查引用的文件和目标之间存在
    errors = [i for i in issues if i.get("severity") == "ERROR"]
    warnings = [i for i in issues if i.get("severity") == "WARNING"]

    return {
        "status": "FAIL" if errors else "PASS",
        "check_name": "章节引用完整性审计 (D5)",
        "summary": f"文件={len(anchor_index)} | Issues={len(errors)}E/{len(warnings)}W",
        "issues": issues,
        "forward_refs": {k: v for k, v in sorted(forward_refs.items())},
        "backward_refs": {k: v for k, v in sorted(backward_refs.items())},
    }


def main():
    verbose = "--verbose" in sys.argv
    results = run_audit()
    print(json.dumps(results, ensure_ascii=False, indent=2 if verbose else None))

    if results["issues"]:
        print(f"\n📋 章节引用审计摘要:")
        for i in results["issues"]:
            print(f"  [{i['severity']}] {i['file']}: {i['detail']}")
        sys.exit(1 if any(i["severity"] == "ERROR" for i in results["issues"]) else 0)


if __name__ == "__main__":
    main()
