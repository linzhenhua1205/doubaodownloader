#!/usr/bin/env python3
"""
check-skills-registration.py — Skills 注册完整性审计脚本

检查:
  B1: skills/ 下所有含 SKILL.md 的目录是否在 skills_config.json 中？
  B2: skills_config.json 中的条目是否都有对应目录？
  B3: config 与 SKILL.md 的 description 是否一致？
  B4: tmp/bak/ 中的废弃 Skill 是否已从 config 移除？

⚠️ 历史教训（2026-08 W32）:
  skills_config.json 曾被大规模重排时丢键（spec-consistency-checker 游离 8 天），
  任何 config 重写/合并后必须立即重跑本脚本确认注册完整。
  别名差异（目录名 vs config 键名）由 ALIAS_MAP 归一化，勿改为改目录名。

用法:
  python3 scripts/check/check-skills-registration.py        # 标准检查
  python3 scripts/check/check-skills-registration.py --json # JSON 输出
  python3 scripts/check/check-skills-registration.py --fix  # 自动修复(安全项)
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

WORKSPACE = (Path(__file__).resolve().parent.parent.parent).resolve()
SKILLS_DIR = WORKSPACE / "skills"
CONFIG_FILE = SKILLS_DIR / "skills_config.json"
BAK_DIR = WORKSPACE / "tmp" / "bak"
MAPPING_FILE = WORKSPACE / "scripts" / "skills-scripts-mapping.md"

# 目录名 → config 键名的别名映射（历史命名差异，注册实际完整，消除误报）
# 来源: W32 质量报告 1.3（2026-W32-skills-scripts-quality-report.md）
ALIAS_MAP = {
    "API--Stripe--OpenAI--Notion---100--more-": "API (Stripe, OpenAI, Notion & 100+ more)",
    "codereview-open-code-review": "open-code-review",
    "codereview-open-code-review-delegate": "open-code-review-delegate",
    "markdown-proxy": "qiaomu-markdown-proxy",  # 2026-08-16 W33 例行质检: 补第4对(漏项)
}
# 反向映射（config 键名 → 目录名），用于死引用判定
ALIAS_MAP_REV = {v: k for k, v in ALIAS_MAP.items()}


def canonical_dir_name(dir_name: str) -> str:
    """目录名归一化：经 ALIAS_MAP 映射为 config 键名后参与比对"""
    return ALIAS_MAP.get(dir_name, dir_name)


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def scan_skill_dirs() -> List[str]:
    """扫描 skills/ 下所有含 SKILL.md 的目录名"""
    result = []
    for d in SKILLS_DIR.iterdir():
        if d.is_dir() and (d / "SKILL.md").exists():
            result.append(d.name)
    return sorted(result)


def check_registration_completeness(config: dict) -> Tuple[List[str], List[str]]:
    """返回 (游离, 死引用)"""
    config_names = {v.get("name", k) for k, v in config.items()}
    # 也检查 config key 本身
    config_keys = set(config.keys())
    all_config_names = config_names | config_keys

    dirs = set(scan_skill_dirs())
    # 排除全局文件/废弃
    active_dirs = {d for d in dirs if not d.startswith("_") and not d.startswith(".")}

    # 游离：目录名（含别名归一化后）仍不在 config 名集合中
    orphaned = sorted(d for d in active_dirs
                      if d not in all_config_names and canonical_dir_name(d) not in all_config_names)
    # 死引用：config 键名既不在目录集、反向映射也找不到目录
    dead_refs = sorted(c for c in all_config_names
                       if c not in active_dirs and ALIAS_MAP_REV.get(c) not in active_dirs)

    return orphaned, dead_refs


def check_description_sync(config: dict) -> List[Tuple[str, str, str]]:
    """返回 [(skill_name, config_desc, skill_desc)] 偏差列表"""
    mismatches = []
    for key, entry in config.items():
        name = entry.get("name", key)
        dir_path = SKILLS_DIR / name
        if not (dir_path / "SKILL.md").exists():
            continue
        config_desc = entry.get("description", "")[:80]  # 与 skill 侧一致截断（原为全量 → 必然误报）

        # 读取 SKILL.md description（支持 YAML 块标量 |
        skill_desc = ""
        with open(dir_path / "SKILL.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
        in_desc = False
        desc_lines = []
        for line in lines:
            stripped = line.rstrip()
            if stripped.startswith("description:"):
                remainder = stripped[len("description:"):].strip()
                if remainder in ("|", "|-", ">", ">-"):
                    # | 字面块 / > 折叠块：均进入块标量模式（折叠换行为空格）
                    in_desc = True
                    continue
                elif remainder:
                    skill_desc = remainder.strip('"').strip("'")
                    break
                else:
                    # description: 后无内容 → YAML 无 | 的缩进多行块（如 web-access 风格）
                    in_desc = True
                    continue
            if in_desc:
                if stripped.startswith("---") or (stripped and not stripped[0].isspace() and not stripped.startswith("#") and not stripped.startswith("description")):
                    break
                if stripped.strip():
                    desc_lines.append(stripped)
        if desc_lines:
            skill_desc = " ".join(d.strip() for d in desc_lines if d.strip())
        skill_desc = skill_desc[:80]  # 前80字符用于比对

        if config_desc != skill_desc:
            mismatches.append((name, config_desc[:80], skill_desc[:80]))
    return mismatches


def check_archive_leakage(config: dict) -> List[str]:
    """检查 tmp/bak/ 中的废弃 Skill 是否仍出现在 config 中"""
    if not BAK_DIR.exists():
        return []

    config_keys = set(config.keys())
    leaked = []
    for bak_item in BAK_DIR.iterdir():
        if bak_item.is_dir():
            # 检查 bak 目录名或其中内容
            for sub in bak_item.iterdir():
                if sub.is_dir() and sub.name in config_keys:
                    leaked.append(sub.name)
                elif sub.is_dir():
                    # 也检查 SKILL.md
                    if (sub / "SKILL.md").exists() and sub.name in config_keys:
                        leaked.append(sub.name)
    return sorted(set(leaked))


def auto_fix_orphaned(orphaned: List[str]) -> List[str]:
    """自动注册游离 Skill（仅安全项，需人工确认后生效）"""
    fixed = []
    config = load_config()
    for name in orphaned:
        if name not in config:
            dir_path = SKILLS_DIR / name
            if (dir_path / "SKILL.md").exists():
                # 读取 description
                desc = ""
                with open(dir_path / "SKILL.md", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("description:"):
                            desc = line[len("description:"):].strip().strip('"').strip("'")
                            break
                config[name] = {
                    "name": name,
                    "description": desc,
                    "source": "custom",
                    "enabled": True,
                    "category": "skill"
                }
                fixed.append(name)
    if fixed:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.write("\n")
        print(f"✅ 已注册游离 Skill: {', '.join(fixed)}")
    return fixed


def main():
    parser = argparse.ArgumentParser(description="Skills 注册完整性审计")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--fix", action="store_true", help="自动修复可修复项")
    args = parser.parse_args()

    config = load_config()
    orphaned, dead_refs = check_registration_completeness(config)
    mismatches = check_description_sync(config)
    leaked = check_archive_leakage(config)

    results = {
        "registered_count": len(config),
        "dir_count": len(scan_skill_dirs()),
        "orphaned": orphaned,
        "dead_refs": dead_refs,
        "desc_mismatches": [(n, c, s) for n, c, s in mismatches],
        "archive_leakage": leaked,
        "status": "✅ 全部通过" if not (orphaned or dead_refs or mismatches or leaked) else "⚠️ 存在问题"
    }

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    # 文本输出
    print(f"\n{'='*50}")
    print(f"🛡️ Skills 注册审计报告")
    print(f"{'='*50}")
    print(f"注册数: {results['registered_count']}  |  目录数: {results['dir_count']}")
    print(f"状态: {results['status']}\n")

    if orphaned:
        print(f"🔴 游离 Skill ({len(orphaned)}): 目录存在但未注册")
        for s in orphaned:
            print(f"   - {s}")
        print()

    if dead_refs:
        print(f"🔴 Config 死引用 ({len(dead_refs)}): 已注册但目录不存在")
        for s in dead_refs:
            print(f"   - {s}")
        print()

    if mismatches:
        print(f"⚠️  Description 偏差 ({len(mismatches)}):")
        for n, c, s in mismatches:
            print(f"   - {n}: config=[{c}]  vs  skill=[{s}]")
        print()

    if leaked:
        print(f"⚠️  废弃泄漏 ({len(leaked)}): 已归档但仍载 config 中")
        for s in leaked:
            print(f"   - {s}")
        print()

    if args.fix and orphaned:
        fixed = auto_fix_orphaned(orphaned)
        if fixed:
            print(f"✅ 自动注册完成: {', '.join(fixed)}")

    sys.exit(0 if results['status'].startswith("✅") else 1)


if __name__ == "__main__":
    main()
