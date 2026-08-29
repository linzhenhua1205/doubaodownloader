#!/usr/bin/env python3
"""
kb_index_format.py — README.md 条目库格式的共用解析模块（design-010 V3）。
（2026-08-03 v1.1: 条目库文件由 knowledge/index.md 更名 knowledge/README.md）

供 kb-index-extract.py（提取）与 kb-index-check.py（check/fix）共用，
避免两处正则漂移。

条目格式（design-010 §4.1）:
    - `文件名.md` | 摘要（≤120 字符）
    - ⭐ `文件名.md` | 摘要          （⭐ = 高价值标记）

日期分节:
    ## YYYY-MM-DD

规则:
  - 条目必须位于 `## YYYY-MM-DD` 分节内
  - 摘要人工撰写"内容讲了什么"；机器 H1 仅作兜底
  - 文件名允许带目录段（同名消歧：`dir/name.md`）

解析结果（Entry）:
    date    : 所在日期分节（'YYYY-MM-DD' 或 None 表示游离条目）
    star    : 是否高价值（⭐）
    file    : 文件名（可能含目录段）
    summary : 摘要文本
    raw     : 原始行
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

# ── 常量 ──────────────────────────────────────────────────────────────────────

DATE_SECTION_RE = re.compile(r'^#{1,3}\s+(\d{4}-\d{2}-\d{2})\s*$')
# 条目：`- ` [⭐ ] `file.md` | summary
ENTRY_RE = re.compile(
    r'^\-\s*'
    r'(?P<star>⭐\s*)?'
    r'`(?P<file>[^`]+\.md)`'
    r'\s*\|\s*'
    r'(?P<summary>.+)$'
)
MAX_SUMMARY_LEN = 120

# 排除的目录名（与 kb-global-index.py 保持一致）
EXCLUDE_DIRNAMES = {
    "bak", "oldbak", "90-bak", "assets", "images", "media", "files",
    "_files", ".git", "node_modules", "old", ".venv", "__pycache__",
}


@dataclass
class Entry:
    date: Optional[str]              # 日期分节；None = 游离（不在任何分节）
    star: bool                       # 高价值标记
    file: str                        # 文件名（可能含目录段）
    summary: str                     # 摘要
    raw: str = ""                    # 原始行
    line_no: int = 0                 # 行号（1-based）
    section_headers: List[str] = field(default_factory=list)  # 所在小节标题（# 层级）


def parse_index(text: str) -> tuple[List[Entry], List[str]]:
    """
    解析 README.md 条目库文本。

    返回:
        entries : 按出现顺序的 Entry 列表（date=None 表示游离条目）
        warnings: 解析警告（无法识别的疑似条目行）
    """
    entries: List[Entry] = []
    warnings: List[str] = []
    current_date: Optional[str] = None
    section_headers: List[str] = []
    in_code = False

    for line_no, line in enumerate(text.split('\n'), start=1):
        stripped = line.strip()
        if not stripped:
            continue

        # 代码块围栏（``` 或 ~~~），内部内容跳过
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code = not in_code
            continue
        if in_code:
            continue

        # 日期分节
        m = DATE_SECTION_RE.match(stripped)
        if m:
            current_date = m.group(1)
            continue

        # 小节标题（# 层级，作为上下文，不阻断日期）
        if stripped.startswith('#'):
            section_headers.append(stripped)
            continue

        # 表格行（`| ... |`）：导航表/职责表等，非条目，忽略
        if stripped.startswith('|'):
            continue

        # 条目
        m = ENTRY_RE.match(stripped)
        if m:
            star = bool(m.group('star'))
            fname = m.group('file').strip()
            summary = m.group('summary').strip()
            entries.append(Entry(
                date=current_date, star=star, file=fname, summary=summary,
                raw=stripped, line_no=line_no,
            ))
            continue

        # 疑似条目但格式不符 → 警告（仅 - 开头且位于日期分节内）
        # 头部规则说明（日期分节前）也用 - 开头，属正常内容，不警告
        if stripped.startswith('- ') and current_date is not None:
            warnings.append(f"L{line_no}: 疑似条目但格式不符: {stripped[:80]}")

    return entries, warnings


def is_excluded_rel(rel_path: str) -> bool:
    """判断相对路径是否命中排除目录（bak/assets 等）。"""
    for part in rel_path.split('/'):
        if part in EXCLUDE_DIRNAMES:
            return True
    return False


def normalize_summary(summary: str) -> str:
    """摘要规范化：去首尾空白、压缩多空白、截断到 MAX_SUMMARY_LEN（安全多字节截断）。"""
    s = re.sub(r'\s+', ' ', summary).strip()
    if len(s) <= MAX_SUMMARY_LEN:
        return s
    # 安全截断：避免切断多字节字符（历史教训：U+FFFD 损坏）
    cut = s[:MAX_SUMMARY_LEN]
    while cut and not cut[-1].isascii() and len(s[:MAX_SUMMARY_LEN+4].encode('utf-8')) > MAX_SUMMARY_LEN * 3:
        cut = cut[:-1]
    return cut.rstrip() + '…'


def format_entry(file: str, summary: str, star: bool = False) -> str:
    """按规范生成条目行。"""
    prefix = '⭐ ' if star else ''
    return f"- {prefix}`{file}` | {normalize_summary(summary)}"


def load_index_file(path) -> tuple[List[Entry], List[str]]:
    """从文件加载并解析 README.md 条目库。path: Path 或 str。"""
    from pathlib import Path
    p = Path(path)
    text = p.read_text(encoding='utf-8', errors='replace')
    return parse_index(text)


if __name__ == '__main__':
    import sys
    from pathlib import Path
    if len(sys.argv) < 2:
        print("用法: python3 scripts/shared/kb_index_format.py <README.md>")
        sys.exit(1)
    entries, warnings = load_index_file(sys.argv[1])
    print(f"条目数: {len(entries)} | 警告: {len(warnings)}")
    for w in warnings[:10]:
        print("  WARN:", w)
    for e in entries[:10]:
        print(f"  {e.date} | {'⭐' if e.star else ' '} | {e.file} | {e.summary[:40]}")
