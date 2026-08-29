#!/usr/bin/env python3
"""
KB Global Index Generator — 生成 knowledge/index.md 全局文件索引。

背景（2026-08-03 治理决策）:
  废弃 02_rd/03_AI/04_person/05_tools/06_others/07_industry-research 及其子目录的
  分布式 index.md / log.md 机制（共 281 个文件），统一为:
    - knowledge/index.md : 全局文件索引（本脚本自动生成，机器维护）
    - knowledge/log.md   : 全局变更日志（kb-global-log.py 合并生成）
  全库统一根 index.md（2026-08-19 起：01_survey/ 与 weekly-reports/ 分布式 index.md 均已移除，无保留目录）。

规则:
  - 覆盖范围: 上述 6 个模块（随时调整的目录）
  - 排除: index.md/log.md/README.md（索引/导航）、bak/oldbak/90-bak/assets/images/media 等资源目录
  - 输出: knowledge/index.md（AUTO-GENERATED 头，勿手工编辑）
  - knowledge/README.md 为人工 SSOT 导航壳 + 条目库（摘要注入源），只引用本文件
  - 摘要来源: 优先 knowledge/README.md 条目库的人工摘要（高价值），缺省用文件 H1

Usage:
  python scripts/tools/kb-global-index.py            # 生成 knowledge/index.md
  python scripts/tools/kb-global-index.py --dry-run  # 预览统计不写文件
  python scripts/tools/kb-global-index.py --verify   # 校验 index.md 是否最新
"""
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.workspace import KNOWLEDGE_ROOT

# === 配置 ===
OUTPUT_FILE = KNOWLEDGE_ROOT / "index.md"
# 2026-08-19 起无保留目录：全库统一根 index.md（01_survey/weekly-reports 分布式 index.md 已移除）
KEEP_DISTRIBUTED = set()
# 纳入全局索引的模块（随时调整）
MODULES = ["02_rd", "03_AI", "04_person", "05_tools", "06_others", "07_industry-research"]
# 排除的资源目录名（任何层级命中即跳过）
EXCLUDE_DIRNAMES = {"bak", "oldbak", "90-bak", "assets", "images", "media", "files",
                    "_files", ".git", "node_modules", "old", ".venv", "__pycache__"}
# 排除的索引/日志文件名
EXCLUDE_FILENAMES = {"index.md", "log.md", "README.md"}
# 人工条目库（摘要注入源）
README_PATH = KNOWLEDGE_ROOT / "README.md"
# 条目库中文件名 → 摘要 的正则
README_ENTRY_RE = re.compile(r"^\s*-\s*(?:⭐\s*)?`([^`]+)`\s*\|\s*(.+?)\s*$")


def load_manual_summaries() -> dict:
    """解析 knowledge/README.md 条目库，返回 文件名 → 人工摘要 映射。

    条目格式: `- [⭐] `file.md` | 摘要`（design-010 V3 条目库）。
    注: 条目库只记录 文件名+摘要（无路径），故按文件名匹配。
    """
    summaries = {}
    if not README_PATH.exists():
        return summaries
    try:
        text = README_PATH.read_text(encoding="utf-8", errors="replace")
        # 逐行匹配（^/$ 为行锚点，避免整文 finditer 失效）
        for line in text.splitlines():
            m = README_ENTRY_RE.match(line)
            if not m:
                continue
            fname = m.group(1).strip()
            summary = m.group(2).strip()
            if fname.endswith(".md") and summary:
                summaries.setdefault(fname, summary)
    except Exception:
        pass
    return summaries

MODULE_DESC = {
    "02_rd": "研发知识库（产品×项目矩阵）",
    "03_AI": "AI 架构与生态分析",
    "04_person": "个人知识管理",
    "05_tools": "工具与技能",
    "06_others": "其他归档",
    "07_industry-research": "行业研究专题",
}


def is_excluded_dir(p: Path) -> bool:
    """目录或其祖先命中排除名单。"""
    for part in p.parts:
        if part in EXCLUDE_DIRNAMES:
            return True
    return False


def safe_truncate(s: str, n: int = 80) -> str:
    """安全截断：避免切断多字节字符/emoji 变体选择符/组合字符。"""
    if len(s) <= n:
        return s
    s = s[:n]
    # 去掉尾部不完整代理对
    if s and 0xD800 <= ord(s[-1]) <= 0xDFFF:
        s = s[:-1]
    # 去掉尾部 emoji 变体选择符/ZWJ/肤色修饰等（可能属于被切断的 emoji）
    s = re.sub(r'[\ufe0f\u200d\U0001F3FB-\U0001F3FF]+$', '', s)
    return s


def extract_title(f: Path) -> str:
    """从文件首行 H1 提取标题；失败则用文件名。"""
    try:
        with open(f, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                m = re.match(r"^#\s+(.+)$", line)
                if m:
                    t = m.group(1).strip()
                    t = re.sub(r"[#*`]", "", t).strip()
                    if t:
                        return safe_truncate(t)
                # 第一行非 H1（如 --- frontmatter），继续找最多 3 行
                break
    except Exception:
        pass
    return f.stem


def collect_files(module: str):
    """收集模块下所有 .md 文件（排除索引/日志/资源目录），返回 [(相对路径, 标题)]。"""
    base = KNOWLEDGE_ROOT / module
    files = []
    if not base.is_dir():
        return files
    for f in sorted(base.rglob("*.md")):
        rel = f.relative_to(KNOWLEDGE_ROOT).as_posix()
        if f.name in EXCLUDE_FILENAMES:
            continue
        if is_excluded_dir(f):
            continue
        files.append((rel, extract_title(f)))
    return files


def group_by_second_level(files):
    """按 模块/二级目录 分组。二级目录取路径第 2 段；直接文件归 '__root__'。"""
    groups = {}
    for rel, title in files:
        parts = rel.split("/")
        if len(parts) >= 3:
            key = f"{parts[0]}/{parts[1]}"
        else:
            key = f"{parts[0]}/__root__"
        groups.setdefault(key, []).append((rel, title))
    return groups


def build_index() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    manual = load_manual_summaries()   # 文件名 → 人工摘要（README.md 条目库）
    lines = []
    lines.append("# knowledge 全局文件索引（INDEX）")
    lines.append("")
    lines.append("> ⚠️ **AUTO-GENERATED** — 由 `scripts/tools/kb-global-index.py` 自动生成，请勿手工编辑。")
    lines.append("> 文件新增/移动/删除后，运行 `python3 scripts/tools/kb-global-index.py` 重新生成。")
    lines.append("> 变更记录统一见 [`log.md`](log.md)；顶层导航+人工条目库见 [`README.md`](README.md)（人工维护）。")
    lines.append("> 摘要来源: 优先 README.md 人工摘要，缺省用文件 H1。")
    lines.append("")
    lines.append("> **覆盖范围**: `02_rd` / `03_AI` / `04_person` / `05_tools` / `06_others` / `07_industry-research`"
                 "（随时调整的目录）。")
    lines.append("> **索引机制**: 全库统一根 index.md（2026-08-19 起：01_survey/weekly-reports 分布式 index.md 已移除，无保留目录）。")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 统计
    total = 0
    stats = []
    for mod in MODULES:
        files = collect_files(mod)
        groups = group_by_second_level(files)
        n = len(files)
        total += n
        stats.append((mod, n, len(groups)))
    lines.append(f"> 📊 **统计**: 共 **{total} 个文件** | {len(MODULES)} 个模块 | 生成时间 {now}")
    lines.append("")
    lines.append("## 📁 模块一览")
    lines.append("")
    lines.append("| 模块 | 说明 | 文件数 | 二级分组 |")
    lines.append("|:-----|:-----|:------:|:--------:|")
    for mod, n, g in stats:
        desc = MODULE_DESC.get(mod, "")
        lines.append(f"| [`{mod}/`](#{mod.lower().replace('_', '')}) | {desc} | {n} | {g} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 各模块分节
    for mod, n, g in stats:
        files = collect_files(mod)
        groups = group_by_second_level(files)
        lines.append(f"## {mod}/")
        lines.append("")
        lines.append(f"> 文件数: **{n}** | 二级分组: {g} 组")
        lines.append("")
        for key in sorted(groups):
            sub = key.split("/", 1)[1]
            if sub == "__root__":
                lines.append(f"### {mod}/ 直接文件")
            else:
                lines.append(f"### {mod}/{sub}/")
            lines.append("")
            lines.append("| 文件 | 摘要 |")
            lines.append("|:-----|:-----|")
            for rel, title in sorted(groups[key]):
                fname = rel.rsplit("/", 1)[-1]
                summary = manual.get(fname, title)   # 人工摘要优先，缺省 H1
                lines.append(f"| [`{fname}`]({rel}) | {summary} |")
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("> 本文件由 `kb-global-index.py` 生成，最后更新: " + now)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate knowledge/index.md global file index")
    parser.add_argument("--dry-run", action="store_true", help="preview stats only")
    parser.add_argument("--verify", action="store_true", help="check if index.md is up-to-date")
    args = parser.parse_args()

    content = build_index()

    if args.dry_run:
        total = sum(len(collect_files(m)) for m in MODULES)
        print(f"[dry-run] 将生成 index.md: {total} 文件, {len(content.splitlines())} 行")
        return

    if args.verify:
        if OUTPUT_FILE.exists() and OUTPUT_FILE.read_text(encoding="utf-8") == content:
            print("✅ index.md 已是最新")
            return 0
        print("⚠️ index.md 已过期，请运行 kb-global-index.py 重新生成")
        return 1

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    total = content.count("\n| [`")
    print(f"✅ 已生成 {OUTPUT_FILE}（{len(content.splitlines())} 行，{total} 个文件条目）")


if __name__ == "__main__":
    sys.exit(main())
