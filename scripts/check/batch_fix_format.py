#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量修复 newwiki2 三类格式一致性问题"""

import os
import re
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")
DOCS_DIR = BASE_DIR / "docs"
AI_AGENT_DIR = DOCS_DIR / "AI-Agent技术架构"
SERVER_HW_DIR = DOCS_DIR / "服务器与硬件架构"

CHANGELOG_APPEND = """
## 🔗 参考文件

| 类型 | 文件 | 说明 |
|------|------|------|
| 📚 题库材料 | aag_系列问答库 | AI-Agent技术架构分类问答题库 |
| 📖 分类索引 | [index.md](index.md) | 本分类总目录 |
| 🏠 知识库首页 | [README.md](../../README.md) | 知识库总览 |

## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| 2026-07-29 | v1.0 | deep-tech-writer 大模型深度优化：重写概要/关键词/核心要点，清理噪声内容，补充来源标注与量化数据，添加TOC和参考文件 |
"""

CHANGELOG_ONLY = """
## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| 2026-07-29 | v1.0 | deep-tech-writer 大模型深度优化：重写概要/关键词/核心要点，清理噪声内容，补充来源标注与量化数据，添加TOC和参考文件 |
"""


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def write_file(path: Path, content: str) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(content)


def has_changelog(content: str) -> bool:
    patterns = [r"##\s*Changelog", r"##\s*更新日志", r"##\s*更新记录"]
    for p in patterns:
        if re.search(p, content):
            return True
    return False


def has_ref_section(content: str) -> bool:
    return bool(re.search(r"##\s*🔗?\s*参考文件", content))


def fix_problem1() -> int:
    """问题1：AI-Agent技术架构 目录文件缺少 Changelog 章节"""
    count = 0
    if not AI_AGENT_DIR.exists():
        print(f"[WARN] 目录不存在: {AI_AGENT_DIR}")
        return 0

    for md_file in AI_AGENT_DIR.glob("*.md"):
        name = md_file.name.lower()
        if name in ("index.md", "progress.md"):
            continue

        try:
            content = read_file(md_file)
            if has_changelog(content):
                continue

            if has_ref_section(content):
                new_content = content.rstrip() + "\n" + CHANGELOG_ONLY
            else:
                new_content = content.rstrip() + "\n" + CHANGELOG_APPEND

            write_file(md_file, new_content)
            count += 1
        except Exception as e:
            print(f"[ERROR] 问题1处理失败 {md_file}: {e}")
            continue

    print(f"[问题1] 修复 {count} 个文件 (AI-Agent缺少Changelog)")
    return count


def fix_problem2() -> int:
    """问题2：服务器与硬件架构 全角冒号替换为半角冒号"""
    count = 0
    if not SERVER_HW_DIR.exists():
        print(f"[WARN] 目录不存在: {SERVER_HW_DIR}")
        return 0

    for md_file in SERVER_HW_DIR.glob("*.md"):
        try:
            content = read_file(md_file)
            original = content
            content = content.replace("> **概要**：", "> **概要**:")
            content = content.replace("> **关键词**：", "> **关键词**:")
            if content != original:
                write_file(md_file, content)
                count += 1
        except Exception as e:
            print(f"[ERROR] 问题2处理失败 {md_file}: {e}")
            continue

    print(f"[问题2] 修复 {count} 个文件 (服务器与硬件全角冒号)")
    return count


def fix_problem3() -> int:
    """问题3：docs/ 所有子目录 参考文件章节标题无空格"""
    count = 0
    if not DOCS_DIR.exists():
        print(f"[WARN] 目录不存在: {DOCS_DIR}")
        return 0

    for md_file in DOCS_DIR.rglob("*.md"):
        try:
            content = read_file(md_file)
            original = content
            content = content.replace("## 🔗参考文件", "## 🔗 参考文件")
            if content != original:
                write_file(md_file, content)
                count += 1
        except Exception as e:
            print(f"[ERROR] 问题3处理失败 {md_file}: {e}")
            continue

    print(f"[问题3] 修复 {count} 个文件 (参考文件emoji空格)")
    return count


def sample_verify(p1_count: int, p2_count: int, p3_count: int) -> None:
    """抽样验证"""
    print("\n" + "=" * 60)
    print("【抽样验证】")

    if p1_count > 0 and AI_AGENT_DIR.exists():
        print("\n--- 问题1抽样 (AI-Agent Changelog) ---")
        files = [f for f in AI_AGENT_DIR.glob("*.md")
                 if f.name.lower() not in ("index.md", "progress.md")]
        samples = files[:3]
        for f in samples:
            try:
                c = read_file(f)
                has_cl = has_changelog(c)
                has_ref = has_ref_section(c)
                print(f"  {f.name}: Changelog={has_cl}, RefSection={has_ref}")
            except Exception as e:
                print(f"  {f.name}: 读取失败 {e}")

    if p2_count > 0 and SERVER_HW_DIR.exists():
        print("\n--- 问题2抽样 (全角冒号) ---")
        files = list(SERVER_HW_DIR.glob("*.md"))[:3]
        for f in files:
            try:
                c = read_file(f)
                has_full = "**概要**：" in c or "**关键词**：" in c
                has_half = "**概要**:" in c or "**关键词**:" in c
                print(f"  {f.name}: 残留全角={has_full}, 半角存在={has_half}")
            except Exception as e:
                print(f"  {f.name}: 读取失败 {e}")

    if p3_count > 0 and DOCS_DIR.exists():
        print("\n--- 问题3抽样 (emoji空格) ---")
        found = 0
        for f in DOCS_DIR.rglob("*.md"):
            try:
                c = read_file(f)
                if "## 🔗 参考文件" in c:
                    print(f"  {f.relative_to(DOCS_DIR)}: 已修正格式")
                    found += 1
                    if found >= 3:
                        break
            except Exception:
                continue
        # 检查是否有残留
        remains = 0
        for f in DOCS_DIR.rglob("*.md"):
            try:
                c = read_file(f)
                if "## 🔗参考文件" in c:
                    print(f"  ⚠️  {f.relative_to(DOCS_DIR)}: 仍有残留!")
                    remains += 1
                    if remains >= 3:
                        break
            except Exception:
                continue
        if remains == 0:
            print("  未发现残留无空格格式")


def main():
    print("=" * 60)
    print("newwiki2 格式一致性批量修复脚本")
    print(f"基准目录: {BASE_DIR}")
    print("=" * 60)

    p1 = fix_problem1()
    p2 = fix_problem2()
    p3 = fix_problem3()

    sample_verify(p1, p2, p3)

    print("\n" + "=" * 60)
    print("【修复统计汇总】")
    print(f"  问题1 (AI-Agent缺少Changelog)   : {p1} 个文件")
    print(f"  问题2 (服务器与硬件全角冒号)      : {p2} 个文件")
    print(f"  问题3 (参考文件emoji空格)         : {p3} 个文件")
    print(f"  合计修复                          : {p1 + p2 + p3} 个文件次")
    print("=" * 60)


if __name__ == "__main__":
    main()
