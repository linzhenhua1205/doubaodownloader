"""
索引更新模块

职责: 自动更新 knowledge/README.md（人工条目库，v1.1 起由 index.md 更名）和 knowledge/log.md（操作日志）。
注意: 全局索引以 knowledge/index.md 为默认操作对象（自动生成）；本模块只向 README.md 条目库按 V3 格式追加。
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import KNOWLEDGE_DIR


# ============================================================
# 更新单个文件
# ============================================================


def update_index_and_log(
    target_dir: str,
    filename: str,
    title: str,
    source_type: str,
    operation: str = "add",
) -> None:
    """
    更新 log.md；README.md 条目库不再更新（2026-08-19 规则：全库无保留目录，日常不动子目录 index/readme，由 kb-global-index.py 批量刷新）。
    保留 _update_index 函数供批量/专项维护时显式调用。

    Args:
        target_dir: 目标子目录（如 "ai-apps"）
        filename: 文件名（如 "2026-06-23-some-topic.md"）
        title: 显示标题
        source_type: 来源类型（doubao/md/fetched/pdf）
        operation: 操作类型（add/update/delete）
    """
    _update_log(operation, f"{target_dir}/{filename}", f"导入: {title} ({source_type})")


def update_index_bulk(
    entries: list[dict],
    batch_name: str = "批量导入",
) -> None:
    """
    批量更新 README.md 条目库和 log.md。

    Args:
        entries: 每个元素是 {"target_dir": ..., "filename": ..., "title": ..., "source_type": ...}
        batch_name: 批次标识
    """
    # 按 target_dir 分组
    groups: dict[str, list[dict]] = {}
    for e in entries:
        groups.setdefault(e["target_dir"], []).append(e)

    # 更新 log.md (每个文件一条)；README.md 条目库不更新（2026-08-19 规则：全库无保留目录，AI/脚本日常不动 index/readme，由 kb-global-index.py 批量刷新）
    for e in entries:
        _update_log(
            "add",
            f"{e['target_dir']}/{e['filename']}",
            f"导入: {e['title']} ({e['source_type']})",
        )


# ============================================================
# README.md 条目库更新（V3: 文件名+摘要·按日期分节）
# ============================================================


def _update_index(
    target_dir: str,
    filename: str,
    title: str,
    source_type: str,
    is_bulk: bool = False,
    count: int = 1,
) -> None:
    """
    在 README.md 条目库的当日日期分节追加 V3 条目。

    V3 条目格式: `- [⭐] `file.md` | 摘要`
    按日期分节（## YYYY-MM-DD），oldest first（正序，2026-08-15 起）；当日分节不存在则追加在末尾。
    摘要从 title 派生（导入来源标注），人工可后续精修。
    ⚠️ 2026-08-19：knowledge/README.md 已精简为纯导航（条目库移入 log.md）；全库无保留目录，本函数保留兼容。
    """
    index_path = KNOWLEDGE_DIR / "README.md"
    if not index_path.exists():
        _create_index(index_path)

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    today = datetime.now().strftime("%Y-%m-%d")
    rel_path = f"{target_dir}/{filename}"
    if is_bulk:
        # title 已含批量信息（调用方传入: "{batch_name} → {dir_name}"）
        summary = f"{title}（{count} 文件）"
    else:
        summary = f"{title}（{source_type}导入）"
    line_to_add = f"- `{filename}` | {summary}\n"

    # 当日分节: ## YYYY-MM-DD
    section_re = re.compile(rf"^## {today}\s*$", re.MULTILINE)
    m = section_re.search(content)
    if m:
        # 在分节标题后插入（该分节内最前）
        insert_pos = m.end()
        content = content[:insert_pos] + "\n" + line_to_add + content[insert_pos:]
    else:
        # 新建分节，插入到「📝 文件条目库」区块起始（或文件开头第一个 ## 前）
        anchor = "## 📝 文件条目库"
        if anchor in content:
            pos = content.index(anchor)
            # 找 anchor 行尾，插入新分节
            eol = content.index("\n", pos)
            content = content[:eol+1] + f"\n### {today}\n\n{line_to_add}" + content[eol+1:]
        else:
            content += f"\n### {today}\n\n{line_to_add}"

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)


def _create_index(path: Path) -> None:
    """创建初始 README.md（V3 条目库骨架）"""
    content = """# knowledge 目录导航（README）

> 自动创建 · 知识库自动化工具集维护
> 全局文件索引（默认操作对象）见 index.md（由 kb-global-index.py 生成）

---

## 📝 文件条目库（文件名+摘要 · 按日期追加 · 无路径）

"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.format(date=_now()))


# ============================================================
# log.md 更新
# ============================================================


def _update_log(operation: str, file_path: str, description: str) -> None:
    """在 log.md 追加一条操作记录"""
    log_path = KNOWLEDGE_DIR / "log.md"
    if not log_path.exists():
        _create_log(log_path)

    now = _now()
    line = f"| {now} | {operation} | {file_path} | {description} |\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def _create_log(path: Path) -> None:
    """创建初始 log.md"""
    content = """# 📝 知识库操作日志

> 自动记录 · 由知识库自动化工具维护

| 时间 | 操作 | 文件 | 说明 |
|:-----|:-----|:-----|:-----|
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# 辅助
# ============================================================


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")
