#!/usr/bin/env python3
"""
format-audit.py — knowledge/ 全库格式审查与安全修复（排除 01_survey / weekly-reports）

定位：对"业务深度调研"目录（02_rd/03_AI/04_person/05_tools/06_others/07_industry-research）
做格式全面审查 + 机械安全修复。设计原则：
  - 只修"绝对安全"项：行尾空格 / 缺失末尾换行 / CRLF→LF / 连续空行(>3→2)
  - 不修"有歧义"项：HEADING-SKIP（改标题=改锚点=破坏交叉链接）→ 仅报告
  - 防内容丢失：修复前后"每行 rstrip 后哈希"必须一致（证明只改了空白）
  - 备份先行：--fix 前全部备份到 tmp/bak/format-audit-<date>/

用法：
  python3 scripts/check/format-audit.py                      # 审查模式（只报告，不改）
  python3 scripts/check/format-audit.py --fix                # 修复模式（备份→修复→验证）
  python3 scripts/check/format-audit.py --fix --commit       # 修复 + git 提交
  python3 scripts/check/format-audit.py --duplicates         # 仅重复文件报告
  python3 scripts/check/format-audit.py --dir knowledge/02_rd # 指定目录
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

# 目标目录（业务深度调研，排除 01_survey / weekly-reports）
DEFAULT_DIRS = [
    "knowledge/02_rd",
    "knowledge/03_AI",
    "knowledge/04_person",
    "knowledge/05_tools",
    "knowledge/06_others",
    "knowledge/07_industry-research",
]

EXCLUDE_PARTS = {"01_survey", "weekly-reports", "bak", "oldbak", "tmp", ".git"}


def is_target(path: Path, root: Path) -> bool:
    """排除 01_survey / weekly-reports / 归档目录。"""
    rel = path.relative_to(root).parts
    return not any(p in EXCLUDE_PARTS for p in rel)


def list_md_files(dirs):
    files = []
    for d in dirs:
        root = Path(d)
        if not root.exists():
            continue
        for p in root.rglob("*.md"):
            if p.is_file() and is_target(p, root):
                files.append(p)
    return files


def content_hash(path: Path) -> str:
    """非空白内容哈希：每行 rstrip + 去空行后 md5。用于验证修复未丢失内容。"""
    h = hashlib.md5()
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.rstrip()
            if stripped.strip():
                h.update(stripped.encode("utf-8", errors="replace"))
                h.update(b"\n")
    return h.hexdigest()


def audit_file(path: Path) -> dict:
    """审查单个文件，返回问题清单。"""
    issues = {"trailing_ws": 0, "no_eof_newline": False, "crlf": False, "blank_runs": 0, "empty": False, "heading_skips": []}
    try:
        raw = path.read_bytes()
        if len(raw) == 0:
            issues["empty"] = True
            return issues
        if b"\r\n" in raw or b"\r" in raw:
            issues["crlf"] = True
        text = raw.decode("utf-8", errors="replace")
        lines = text.split("\n")
        if lines and lines[-1] != "" and text and not text.endswith("\n"):
            issues["no_eof_newline"] = True
        # 行尾空格 & 标题层级（流式跟踪，与 check_md_format 一致：不因正文重置）
        prev_level = 0
        blank_run = 0
        for i, line in enumerate(lines, 1):
            if re.search(r"[ \t]+$", line):
                issues["trailing_ws"] += 1
            m = re.match(r"^(#{1,6})\s", line)
            if m:
                level = len(m.group(1))
                if prev_level and level > prev_level + 1:
                    issues["heading_skips"].append((i, prev_level, level))
                prev_level = level
            else:
                if line.strip() == "":
                    blank_run += 1
                    if blank_run > 3:
                        issues["blank_runs"] += 1
                else:
                    blank_run = 0
    except Exception as e:
        issues["error"] = str(e)
    return issues


def fix_file(path: Path, issues: dict) -> int:
    """修复安全项，返回修改行数。"""
    changed = 0
    text = path.read_text(encoding="utf-8", errors="replace")
    new_text = text
    # 1) CRLF → LF
    if issues["crlf"]:
        new_text = new_text.replace("\r\n", "\n").replace("\r", "\n")
    # 2) 行尾空格
    if issues["trailing_ws"]:
        new_text = re.sub(r"[ \t]+$", "", new_text, flags=re.M)
    # 3) 连续空行 >3 → 2
    if issues["blank_runs"]:
        new_text = re.sub(r"\n{4,}", "\n\n\n", new_text)
    # 4) 末尾换行补齐
    if issues["no_eof_newline"] and new_text:
        new_text = new_text.rstrip("\n") + "\n"
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        changed = sum(1 for a, b in zip(text.split("\n"), new_text.split("\n")) if a != b)
        changed = max(changed, 1)
    return changed


def backup(files: list, bak_root: Path) -> dict:
    """备份文件到 bak 目录，返回 {file: backup_path}。"""
    mapping = {}
    for f in files:
        rel = f.relative_to(".") if str(f).startswith(".") else f
        dst = bak_root / str(f).lstrip("./")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        mapping[f] = dst
    return mapping


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", nargs="+", default=DEFAULT_DIRS, help="目标目录（默认全部业务目录）")
    ap.add_argument("--fix", action="store_true", help="执行安全修复")
    ap.add_argument("--commit", action="store_true", help="修复后 git 提交")
    ap.add_argument("--duplicates", action="store_true", help="仅输出重复文件报告")
    args = ap.parse_args()

    files = list_md_files(args.dir)
    print(f"📁 扫描目录: {', '.join(args.dir)}")
    print(f"📄 发现 md 文件: {len(files)}\n")

    # ── 重复文件报告 ──
    hashmap = {}
    for f in files:
        h = content_hash(f)
        hashmap.setdefault(h, []).append(f)
    dups = {h: v for h, v in hashmap.items() if len(v) > 1}
    if dups:
        print(f"🔁 内容完全相同（md5）: {len(dups)} 组")
        for h, v in sorted(dups.items(), key=lambda x: -len(x[1])):
            print(f"  [{len(v)} files] " + "\n    ".join(str(p) for p in v))
    else:
        print("🔁 内容完全相同: 无")
    if args.duplicates:
        return

    # ── 逐文件审查 ──
    summary = {"trailing_ws_files": 0, "trailing_ws_lines": 0, "no_eof": 0, "crlf": 0,
               "blank_runs_files": 0, "empty": 0, "heading_files": 0, "heading_issues": 0}
    to_fix = []
    heading_report = []
    for f in files:
        iss = audit_file(f)
        if iss.get("error"):
            print(f"  ⚠️ 读取失败 {f}: {iss['error']}")
            continue
        if iss["trailing_ws"]:
            summary["trailing_ws_files"] += 1
            summary["trailing_ws_lines"] += iss["trailing_ws"]
        if iss["no_eof_newline"]:
            summary["no_eof"] += 1
        if iss["crlf"]:
            summary["crlf"] += 1
        if iss["blank_runs"]:
            summary["blank_runs_files"] += 1
        if iss["empty"]:
            summary["empty"] += 1
        if iss["heading_skips"]:
            summary["heading_files"] += 1
            summary["heading_issues"] += len(iss["heading_skips"])
            if len(iss["heading_skips"]) <= 3:
                for (ln, pl, lv) in iss["heading_skips"]:
                    heading_report.append(f"    {f}:{ln}  #{pl} → #{lv}")
        if args.fix and (iss["trailing_ws"] or iss["no_eof_newline"] or iss["crlf"] or iss["blank_runs"]):
            to_fix.append(f)

    print("\n" + "=" * 60)
    print("📋 审查报告（仅报告，未改动）" if not args.fix else "🔧 修复前审查基线")
    print("=" * 60)
    print(f"  行尾空格: {summary['trailing_ws_files']} 文件 / {summary['trailing_ws_lines']} 行")
    print(f"  缺失末尾换行: {summary['no_eof']} 文件")
    print(f"  CRLF: {summary['crlf']} 文件")
    print(f"  连续空行>3: {summary['blank_runs_files']} 文件")
    print(f"  空文件: {summary['empty']} 文件")
    print(f"  HEADING-SKIP(仅报告不修): {summary['heading_files']} 文件 / {summary['heading_issues']} 处")
    if heading_report:
        print("  --- 标题跳级明细（前若干）---")
        print("\n".join(heading_report[:30]))

    if not args.fix:
        print("\nℹ️  运行 --fix 执行安全修复（备份→修复→内容哈希验证）")
        return

    # ── 修复模式 ──
    print(f"\n🔧 待修复文件: {len(to_fix)}")
    if not to_fix:
        print("  无需修复 ✅")
        return

    bak_root = Path(f"tmp/bak/format-audit-{date.today().isoformat()}")
    bak_root.mkdir(parents=True, exist_ok=True)
    print(f"📦 备份目录: {bak_root}/")

    before_hash = {f: content_hash(f) for f in to_fix}
    backup(to_fix, bak_root)

    changed_files = []
    for f in to_fix:
        iss = audit_file(f)
        n = fix_file(f, iss)
        if n:
            changed_files.append(f)

    # ── 内容不丢失验证 ──
    print(f"\n✅ 修复完成: {len(changed_files)} 文件")
    print("🔍 内容不丢失验证（非空白哈希对比）...")
    lost = []
    for f in changed_files:
        after = content_hash(f)
        if after != before_hash[f]:
            lost.append(f)
            print(f"  ❌ 内容变化! {f}")
    if lost:
        print(f"\n🚨 {len(lost)} 个文件内容被改动（非空白差异），从备份恢复...")
        for f in lost:
            src = bak_root / str(f).lstrip("./")
            shutil.copy2(src, f)
        print("  已恢复 ✅")
    else:
        print(f"  ✅ 全部 {len(changed_files)} 文件内容哈希一致（仅空白字符被清理）")

    # ── 汇总 ──
    print("\n" + "=" * 60)
    print("📊 修复汇总")
    print("=" * 60)
    print(f"  修复文件数: {len(changed_files)}")
    print(f"  备份位置: {bak_root}/")
    print(f"  未修复(需人工): HEADING-SKIP {summary['heading_issues']} 处 / 重复文件 {len(dups)} 组")

    if args.commit and changed_files:
        print("\n🚀 git 提交...")
        subprocess.run(["git", "add"] + [str(f) for f in changed_files], check=False)
        r = subprocess.run(["git", "commit", "-m",
                            f"chore(format): 全库格式审查与安全修复 {len(changed_files)} 文件 "
                            f"(行尾空格/EOF/CRLF/连续空行，非空白哈希验证通过，HEADING-SKIP仅报告)"],
                           capture_output=True, text=True)
        print(r.stdout[-500:] if r.stdout else r.stderr[-500:])
        print("\n📈 提交统计:")
        subprocess.run(["git", "show", "--stat", "HEAD"], check=False)


if __name__ == "__main__":
    main()
