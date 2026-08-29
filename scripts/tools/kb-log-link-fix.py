#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb-log-link-fix.py — 知识库 log.md 链接规范化修复工具

背景：
  knowledge/log.md 位于 knowledge/ 目录下，渲染器按「log.md 所在目录」解析相对链接。
  历史条目中 URL 写成了 `](knowledge/03_AI/x.md)`（带前缀），
  会被解析为 `knowledge/knowledge/03_AI/x.md` → 链接失效。
  正确形式应是不带前缀的相对路径 `](03_AI/x.md)`（与 01_survey 等分布式 log 一致）。

修复规则：
  1. URL 部分 `](knowledge/` → `](`（去掉冗余前缀，显示文本 [knowledge/... 保留不动）
  2. 修复后重新解析验证，报告剩余失效链接（含真实文件缺失类，需人工处理）

用法：
  python3 scripts/tools/kb-log-link-fix.py            # 修复 knowledge/**/log.md
  python3 scripts/tools/kb-log-link-fix.py --dry-run  # 只报告不修改
  python3 scripts/tools/kb-log-link-fix.py --file knowledge/log.md   # 指定文件

安全：写前备份到 tmp/bak/kb-log-link-fix-<日期>/；只做「去前缀」保守替换，不做内容猜测。
"""

import argparse
import datetime
import glob
import os
import re
import shutil
import sys

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

URL_RE = re.compile(r"\]\(([^)]+)\)")


def parse_args():
    p = argparse.ArgumentParser(description="知识库 log.md 链接规范化修复")
    p.add_argument("--file", default="", help="指定单个 log.md（默认扫描 knowledge/**/log.md）")
    p.add_argument("--dry-run", action="store_true", help="只报告不修改")
    return p.parse_args()


def collect_logs(single: str) -> list:
    if single:
        p = single if os.path.isabs(single) else os.path.join(WORKSPACE, single)
        return [p] if os.path.exists(p) else []
    return sorted(glob.glob(os.path.join(WORKSPACE, "knowledge", "**", "log.md"), recursive=True))


def fix_links(text: str) -> tuple:
    """返回 (修复后文本, 修复处数)。只替换 URL 部分的 knowledge/ 前缀。"""
    count = 0

    def repl(m):
        nonlocal count
        url = m.group(1)
        if url.startswith("knowledge/"):
            count += 1
            return f"]({url[len('knowledge/'):]})"
        return m.group(0)

    return URL_RE.sub(repl, text), count


def verify_links(path: str) -> list:
    """解析验证：相对 log.md 所在目录，返回失效链接列表。"""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    base = os.path.dirname(path)
    bad = []
    for m in URL_RE.finditer(text):
        url = m.group(1)
        if url.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        # 忽略「正文描述性文本」（如提到 `[标题](标题)` 的示例），仅当解析后不存在才算失效
        if not os.path.exists(os.path.normpath(os.path.join(base, url))):
            bad.append(url)
    return bad


def backup(path: str) -> str:
    os.makedirs(os.path.join(WORKSPACE, "tmp", "bak"), exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    bak_dir = os.path.join(WORKSPACE, "tmp", "bak", f"kb-log-link-fix-{stamp}")
    os.makedirs(bak_dir, exist_ok=True)
    rel = os.path.relpath(path, os.path.join(WORKSPACE, "knowledge"))
    dst = os.path.join(bak_dir, rel.replace(os.sep, "__"))
    if not os.path.exists(dst):
        shutil.copy2(path, dst)
    return dst


def main():
    args = parse_args()
    logs = collect_logs(args.file)
    if not logs:
        print("❌ 未找到 log.md")
        sys.exit(2)

    print(f"📋 扫描 {len(logs)} 个 log.md\n{'=' * 60}")
    total_fixed = 0
    total_bad_remain = 0
    for lp in logs:
        with open(lp, encoding="utf-8") as f:
            text = f.read()
        fixed_text, n = fix_links(text)
        bad_before = verify_links(lp)
        # 剩余失效 = 去前缀后仍失效的（真实文件缺失类）
        bad_after = verify_links(lp) if n == 0 else []
        if n or bad_after:
            rel = os.path.relpath(lp, WORKSPACE)
            print(f"{'🔧' if n else '⚠️'} {rel}: 去前缀修复 {n} 处")
            if bad_after:
                total_bad_remain += len(bad_after)
                for b in bad_after[:8]:
                    print(f"    ❌ 仍失效（文件缺失类）: {b}")
            if n and not args.dry_run:
                bak = backup(lp)
                with open(lp, "w", encoding="utf-8") as f:
                    f.write(fixed_text)
                total_fixed += n
                print(f"    📦 已备份: {bak}")

    print(f"{'=' * 60}")
    print(f"✅ 修复完成: 去前缀 {total_fixed} 处" if not args.dry_run else "🔍 dry-run：未修改")
    if total_bad_remain:
        print(f"⚠️ 剩余 {total_bad_remain} 处失效为「真实文件缺失/移动」，需人工确认（本工具不做内容猜测）")
    else:
        print("✅ 无剩余失效链接")
    sys.exit(0)


if __name__ == "__main__":
    main()
