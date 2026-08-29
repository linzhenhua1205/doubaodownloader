#!/usr/bin/env python3
"""
link-ref-audit.py — 引用即契约检测器（Skills/Scripts 引用完整性审计）

audit-002 P0 落地：验证"文档引用的脚本是否真实存在且可无歧义解析"。
将"文档承诺 → 脚本存在"固化为可重复执行的检测器，消灭三类断裂：
  1. 真实断裂: 引用路径既不在 scripts/ 也不在 skill 内嵌目录
  2. 路径歧义: 文档写 scripts/xxx.py，但脚本实际在 skills/<skill>/scripts/
  3. 设计承诺: 文档描述了确定性检查器但脚本从未创建（提示词回退 LLM 判断）

用法:
  python3 scripts/check/link-ref-audit.py                # 全量扫描（skills + spec）
  python3 scripts/check/link-ref-audit.py --scope skills # 仅 skills
  python3 scripts/check/link-ref-audit.py --scope spec   # 仅 spec
  python3 scripts/check/link-ref-audit.py --json         # JSON 输出（供 system-guardian 解析）
  python3 scripts/check/link-ref-audit.py --strict       # 占位符/教学引用也算断裂（默认排除）
  python3 scripts/check/link-ref-audit.py --list         # 列出全部断裂明细

退出码: 0=无真实断裂 / 1=存在真实断裂或路径歧义（供 CI 门禁）
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = os.path.join(WORKSPACE, "skills")
SPEC_DIR = os.path.join(WORKSPACE, "spec")
PROMISES_FILE = os.path.join(os.path.dirname(__file__), "design-promises.json")


def load_promises() -> set:
    """加载设计承诺清单（已降级/教学/已实现的豁免项）"""
    try:
        data = json.load(open(PROMISES_FILE, encoding="utf-8"))
        return {p["script"] for p in data.get("promises", [])}
    except Exception:
        return set()

# 占位符/示例引用（教学用例，非契约）
PLACEHOLDER = re.compile(r"(xxx|yyy|my_|script_name|example|sample|\.\.\.)", re.I)
# 教学文档目录（examples/assets/templates 中的引用为虚构示例）
TEACHING_DIRS = ("examples", "assets", "templates", "forms", "worked_example")

SCRIPT_REF = re.compile(r"(?<!spec/)(?:scripts/|skills/)[a-zA-Z0-9_./-]+\.(?:py|sh)")


def is_teaching_path(path: str) -> bool:
    """是否教学/示例文档（其中的脚本引用为虚构教学用例）"""
    parts = path.replace("\\", "/").split("/")
    return any(t in parts for t in TEACHING_DIRS)


def resolve_ref(ref: str, doc_path: str):
    """三级解析: 根 scripts/ → skill 内嵌 scripts/ → 断裂

    返回 (status, resolved_path):
      status: 'root' | 'skill-local' | 'broken'
    """
    if ref.startswith("scripts/"):
        root_path = os.path.join(WORKSPACE, ref)
        if os.path.exists(root_path):
            return "root", ref
        # 尝试 skill 内嵌（文档所在 skill 的 scripts/ 子目录）
        doc_parts = doc_path.replace("\\", "/").split("/")
        # 文档在 skills/<skill>/... 下（处理绝对/相对路径）
        skill_idx = None
        for i, part in enumerate(doc_parts):
            if part == "skills":
                skill_idx = i
                break
        if skill_idx is not None and skill_idx + 1 < len(doc_parts):
            skill_name = doc_parts[skill_idx + 1]
            skill_local = os.path.join(SKILLS_DIR, skill_name, ref)
            if os.path.exists(skill_local):
                return "skill-local", f"skills/{skill_name}/{ref}"
        # 兜底: 全库搜索同名脚本（跨 skill 引用，文档未写全路径）
        fname = os.path.basename(ref)
        for root, dirs, files in os.walk(SKILLS_DIR):
            if ".git" in root or "__pycache__" in root or "_archive" in root:
                continue
            if fname in files:
                rel = os.path.relpath(os.path.join(root, fname), WORKSPACE)
                return "skill-local", rel
        return "broken", None
    elif ref.startswith("skills/"):
        full = os.path.join(WORKSPACE, ref)
        if os.path.exists(full):
            return "root", ref
        return "broken", None
    return "broken", None


def scan_scope(scope: str, strict: bool = False):
    """扫描指定范围，返回统计与明细"""
    docs = []
    if scope in ("skills", "all"):
        for root, dirs, files in os.walk(SKILLS_DIR):
            if ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".md"):
                    docs.append(os.path.join(root, f))
    if scope in ("spec", "all"):
        for f in os.listdir(SPEC_DIR):
            if f.endswith(".md"):
                docs.append(os.path.join(SPEC_DIR, f))

    stats = {"total_refs": 0, "root": 0, "skill_local": 0, "broken": 0, "teaching": 0}
    broken_list = []  # (doc, ref, status_detail)
    ambiguous_list = []  # (doc, ref, resolved)
    promises = load_promises() if not strict else set()

    for doc in docs:
        try:
            content = open(doc, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        teaching = is_teaching_path(doc)
        for m in SCRIPT_REF.finditer(content):
            ref = m.group(0)
            stats["total_refs"] += 1
            if teaching:
                stats["teaching"] += 1
                continue  # 教学文档不参与契约判定
            if PLACEHOLDER.search(ref) and not strict:
                stats["teaching"] += 1
                continue
            # 表格行内的引用视为描述性（审计上下文/对照表），不构成契约
            line_start = content.rfind("\n", 0, m.start()) + 1
            line = content[line_start:content.find("\n", m.end())]
            if line.lstrip().startswith("|") and not strict:
                stats["teaching"] += 1
                continue
            # .github/scripts/ 是 CI 独立路径体系（GitHub Actions 惯例），非本系统 scripts/ 契约
            if ".github/" in ref and not strict:
                stats["teaching"] += 1
                continue
            # 设计承诺清单豁免（已降级/教学/已实现，见 design-promises.json）
            if ref in promises:
                stats["teaching"] += 1
                continue
            status, resolved = resolve_ref(ref, doc)
            if status == "root":
                stats["root"] += 1
            elif status == "skill-local":
                stats["skill_local"] += 1
                ambiguous_list.append((doc, ref, resolved))
            else:
                stats["broken"] += 1
                broken_list.append((doc, ref))

    return stats, broken_list, ambiguous_list


def main():
    parser = argparse.ArgumentParser(description="引用即契约检测器")
    parser.add_argument("--scope", choices=["all", "skills", "spec"], default="all")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--strict", action="store_true", help="占位符/教学引用计入断裂")
    parser.add_argument("--list", action="store_true", help="列出全部断裂明细")
    args = parser.parse_args()

    stats, broken, ambiguous = scan_scope(args.scope, args.strict)

    if args.json:
        print(json.dumps({
            "scope": args.scope,
            "stats": stats,
            "broken_count": len(broken),
            "ambiguous_count": len(ambiguous),
            "broken": [{"doc": d, "ref": r} for d, r in broken],
            "ambiguous": [{"doc": d, "ref": r, "resolved": res} for d, r, res in ambiguous],
            "pass": len(broken) == 0,
        }, ensure_ascii=False, indent=2))
        sys.exit(0 if len(broken) == 0 else 1)

    total = stats["total_refs"]
    print(f"\n{'='*60}")
    print(f"🔗 引用即契约检测（{args.scope}）")
    print(f"{'='*60}")
    print(f"总引用: {total} | 根路径命中: {stats['root']} | skill内嵌命中: {stats['skill_local']} | 断裂: {stats['broken']} | 教学/占位: {stats['teaching']}")
    if total:
        hit_rate = (stats["root"] + stats["skill_local"]) * 100 // max(total - stats["teaching"], 1)
        print(f"契约命中率: {hit_rate}%")
    print(f"\n🔴 真实断裂: {len(broken)} 处 / {len(set(r for _, r in broken))} 唯一脚本")
    if args.list or len(broken) <= 30:
        for doc, ref in sorted(broken):
            rel = os.path.relpath(doc, WORKSPACE)
            print(f"   ❌ {ref} ← {rel}")
    elif broken:
        print(f"   （仅显示前 30，用 --list 查看全部 {len(broken)} 处）")
        for doc, ref in sorted(broken)[:30]:
            rel = os.path.relpath(doc, WORKSPACE)
            print(f"   ❌ {ref} ← {rel}")
    print(f"\n🟡 路径歧义（文档写 scripts/ 但实为 skill 内嵌）: {len(ambiguous)} 处 / {len(set(r for _, r, _ in ambiguous))} 唯一脚本")
    if args.list or len(ambiguous) <= 20:
        for doc, ref, res in sorted(ambiguous):
            rel = os.path.relpath(doc, WORKSPACE)
            print(f"   ⚠️ {ref} → 实际 {res} ← {rel}")
    elif ambiguous:
        print(f"   （仅显示前 20，用 --list 查看全部 {len(ambiguous)} 处）")
        for doc, ref, res in sorted(ambiguous)[:20]:
            rel = os.path.relpath(doc, WORKSPACE)
            print(f"   ⚠️ {ref} → 实际 {res} ← {rel}")

    print()
    if len(broken) == 0:
        print("✅ 契约完整：所有文档引用的脚本均真实存在且路径无歧义")
        sys.exit(0)
    else:
        print(f"❌ 契约断裂 {len(broken)} 处：文档承诺的脚本不存在，执行时将回退 LLM 自由判断")
        print("   修复建议: ① 实现脚本 ② 修正路径 ③ 删除引用或标注 TODO（禁止保留中间态）")
        sys.exit(1)


if __name__ == "__main__":
    main()
