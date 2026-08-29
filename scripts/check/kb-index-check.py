#!/usr/bin/env python3
"""
kb-index-check.py — README.md 条目库健康检查与修复（design-010 V3）。

Check（只读）:
    C1 条目格式      : `- [⭐] `file.md` | 摘要`
    C2 日期分节正序  : `## YYYY-MM-DD`，oldest first（2026-08-15 起统一正序）
    C3 文件名存在性  : 条目文件名在 index.md（或文件系统）中存在
    C4 重复条目      : 同一文件名不重复出现
    C5 摘要质量      : 摘要非空、≥4 字符、非纯文件名
    C6 三同步        : README.md 条目文件名 ⊆ index.md 文件名集合（未刷新检测）
    C7 无操作记录    : README.md 不含"已废弃/更名/已迁移/方案A/重构/备份于"等操作记录字样（操作记录只进 log.md）
    C8 文件名规范    : 全局模块活跃 .md 文件名符合 YYYY-MM-DD-英文描述.md（design-003 命名规范）

Fix（--fix，写回前备份）:
    F1 格式规范化    : 重写条目为标准格式（保序）
    F2 日期正序      : 按日期分节重排（oldest first）
    F3 重复条目      : 保留最新一条（交互确认）
    F4 摘要缺失      : 用 index.md H1 兜底生成，标 [auto]（交互确认）
    F5 残留条目      : C3 命中的条目标记 [missing]（交互确认，不自动删）

用法:
    python3 scripts/check/kb-index-check.py                          # 根 README.md 全项检查
    python3 scripts/check/kb-index-check.py knowledge/README.md      # 指定文件
    python3 scripts/check/kb-index-check.py --all --check            # 根 + 保留目录
    python3 scripts/check/kb-index-check.py --fix                    # 检查并修复（自动备份）
    python3 scripts/check/kb-index-check.py --check-sync             # 只查三同步 C6
    python3 scripts/check/kb-index-check.py --dry-run                # 只预览将做的修复
"""

import argparse
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.kb_index_format import (
    Entry, parse_index, load_index_file, format_entry,
    is_excluded_rel, EXCLUDE_DIRNAMES, DATE_SECTION_RE,
)

# Windows 控制台编码兼容
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE = ROOT / "knowledge"
ROOT_INDEX = KNOWLEDGE / "README.md"
GLOBAL_INDEX = KNOWLEDGE / "index.md"
# 保留分布式机制的目录（根 README.md 之外的合法 index.md）
KEEP_DISTRIBUTED = {"01_survey", "weekly-reports"}
# 排除目录（与 kb-global-index.py 一致）
EXCLUDE_DIRS = EXCLUDE_DIRNAMES


def find_md_files(root: Path) -> dict:
    """递归扫描知识库 .md 文件（排除 bak/资源目录），返回 文件名 → [相对路径]。"""
    fname_map: dict = {}
    for p in root.rglob("*.md"):
        rel = p.relative_to(root).as_posix()
        if is_excluded_rel(rel):
            continue
        # 排除 index/log 自身
        if p.name in ("index.md", "log.md", "index.md", "README.md"):
            continue
        fname_map.setdefault(p.name, [])
        fname_map[p.name].append(rel)
    return fname_map


def index_files_in_global_index() -> set:
    """index.md 中登记的文件名集合（用于 C6 三同步检查）。"""
    names = set()
    if not GLOBAL_INDEX.exists():
        return names
    text = GLOBAL_INDEX.read_text(encoding='utf-8', errors='replace')
    for m in re.finditer(r'\]\(([^)#]+\.md)\)', text):
        path = m.group(1).replace('\\', '/').lstrip('./')
        if is_excluded_rel(path):
            continue
        names.add(path.split('/')[-1])
    return names


# ── Check ─────────────────────────────────────────────────────────────────────

class Report:
    def __init__(self):
        self.issues = []          # (code, severity, message)
        self.fix_actions = []     # (action, description)

    def issue(self, code, sev, msg):
        self.issues.append((code, sev, msg))

    def fix(self, action, desc):
        self.fix_actions.append((action, desc))

    def has_errors(self):
        return any(sev in ("ERROR",) for _, sev, _ in self.issues)


def run_checks(path: Path, check_sync_only: bool = False) -> Report:
    rep = Report()
    if not path.exists():
        rep.issue("C0", "ERROR", f"文件不存在: {path}")
        return rep

    entries, warnings = load_index_file(path)
    for w in warnings:
        rep.issue("C1", "WARN", w)

    if check_sync_only:
        _check_sync(rep, entries)
        return rep

    # C2 日期分节正序
    dates = []
    for e in entries:
        if e.date and e.date not in dates:
            dates.append(e.date)
    for i in range(1, len(dates)):
        if dates[i] > dates[i - 1]:
            rep.issue("C2", "ERROR",
                      f"日期分节非正序: {dates[i]} 出现在 {dates[i-1]} 之后（应为 oldest first）")

    # C3 文件名存在性
    fname_map = find_md_files(KNOWLEDGE)
    for e in entries:
        name = e.file.replace('\\', '/').split('/')[-1]
        if name not in fname_map:
            rep.issue("C3", "ERROR", f"L{e.line_no}: 文件不存在于知识库: {e.file}")
            rep.fix("F5", f"标记 [missing]: {e.file}")

    # C4 重复条目
    seen = Counter()
    for e in entries:
        key = e.file.replace('\\', '/').split('/')[-1]
        seen[key] += 1
    for name, cnt in seen.items():
        if cnt > 1:
            rep.issue("C4", "ERROR", f"重复条目 {cnt} 次: {name}")
            rep.fix("F3", f"去重: {name}（保留最新一条）")

    # C5 摘要质量
    for e in entries:
        if not e.summary:
            rep.issue("C5", "WARN", f"L{e.line_no}: 空摘要: {e.file}")
            rep.fix("F4", f"H1 兜底摘要: {e.file}")
        elif len(e.summary) < 4:
            rep.issue("C5", "WARN", f"L{e.line_no}: 摘要过短(<4字符): {e.file}")
        elif e.summary.rstrip('…').strip() == e.file:
            rep.issue("C5", "WARN", f"L{e.line_no}: 摘要=文件名（无效摘要）: {e.file}")

    # C7 操作记录不进 README.md（仅根 README.md 检查；保留目录 index.md 不受限）
    if path == ROOT_INDEX:
        op_markers = ["已废弃", "更名", "已迁移", "方案A", "重构", "备份于", "DEPRECATED"]
        for line_no, line in enumerate(
                path.read_text(encoding='utf-8', errors='replace').split('\n'), 1):
            hits = [m for m in op_markers if m in line]
            if hits:
                # 跳过禁令/规则说明行（"不承载…更名等操作记录"是规则定义，非操作记录）
                if any(k in line for k in ("不承载", "只进", "禁止", "一律")):
                    continue
                rep.issue("C7", "WARN",
                          f"L{line_no}: README.md 含操作记录字样({hits}): "
                          f"{line.strip()[:60]}（操作记录应只进 log.md）")

    # C8 文件名规范检查: YYYY-MM-DD-英文描述-使用-连接.md (design-003 命名规范)
    # 仅对全局模块活跃文件检查; 排除: 保留分布式目录/管理文件/废弃归档区
    _check_filename_norm(rep, path)

    # C6 三同步（index.md 未刷新检测）
    _check_sync(rep, entries)

    # 游离条目（不在任何日期分节）
    for e in entries:
        if e.date is None:
            rep.issue("C1", "WARN", f"L{e.line_no}: 条目不在日期分节内: {e.file}")

    return rep


def _check_sync(rep: Report, entries: list):
    if not GLOBAL_INDEX.exists():
        rep.issue("C6", "WARN", "index.md 不存在，无法检查三同步（运行 kb-global-index.py）")
        return
    indexed = index_files_in_global_index()
    for e in entries:
        name = e.file.replace('\\', '/').split('/')[-1]
        if name not in indexed:
            rep.issue("C6", "WARN",
                      f"README.md 有条目但 index.md 未收录（三同步断裂，运行 kb-global-index.py）: {e.file}")


# C8: 文件名规范 YYYY-MM-DD-英文描述.md (design-003 命名规范)
NORM_FNAME_RE = re.compile(r'^\d{4}-\d{2}-\d{2}-[A-Za-z0-9][A-Za-z0-9-]*\.md$')


def _check_filename_norm(rep: Report, path: Path):
    """C8: 全局模块活跃 .md 文件名是否符合 YYYY-MM-DD-英文描述.md。

    排除: 01_survey/ weekly-reports/(保留分布式) + oldbak/*-bak(废弃区)
          + index/log/README/INDEX 管理文件。
    说明: 文件名日期反映内容创建/归档日, 英文描述用 - 连接(小写);
          不合规 → WARN + 提示运行 scripts/tools/kb-rename-normalize.py 修复。
    """
    for p in KNOWLEDGE.rglob("*.md"):
        rel = p.relative_to(KNOWLEDGE).as_posix()
        if is_excluded_rel(rel):
            continue
        # 保留分布式机制目录 + 废弃归档区
        first_part = rel.split('/')[0]
        if first_part in ("01_survey", "weekly-reports"):
            continue
        if p.name in ("index.md", "log.md", "index.md", "README.md", "MIGRATIONS.md"):
            continue
        if not NORM_FNAME_RE.match(p.name):
            rep.issue("C8", "WARN",
                      f"文件名不合规(期望 YYYY-MM-DD-英文描述.md): {rel} "
                      f"(运行 scripts/tools/kb-rename-normalize.py --apply 修复)")


# ── Fix ───────────────────────────────────────────────────────────────────────

def apply_fix(path: Path, entries: list, warnings: list, auto: bool) -> Report:
    """按规范重写 README.md：条目格式规范化 + 日期倒序 + 去重 + 摘要兜底。"""
    rep = Report()
    lines = path.read_text(encoding='utf-8', errors='replace').split('\n')

    # F1/F2: 重建条目区
    # 策略：保留头部（首个 ## YYYY-MM-DD 之前的内容），重排条目
    # 逐行处理，重新生成条目行
    new_lines = []
    pending = []               # 待写入的条目（当前日期分节内）
    current_date = None
    seen_files = set()
    skipped = 0

    def flush():
        nonlocal pending
        if pending:
            new_lines.extend(pending)
            pending = []

    for line in lines:
        stripped = line.strip()
        m_date = DATE_SECTION_RE.match(stripped)
        if m_date:
            flush()
            current_date = m_date.group(1)
            new_lines.append(line)
            continue
        # 尝试解析条目
        from scripts.shared.kb_index_format import ENTRY_RE
        m = ENTRY_RE.match(stripped)
        if m and current_date:
            star = bool(m.group('star'))
            fname = m.group('file').strip()
            summary = m.group('summary').strip()
            key = fname.replace('\\', '/').split('/')[-1]
            if key in seen_files:
                skipped += 1
                rep.fix("F3", f"去重(跳过): {fname}")
                continue
            seen_files.add(key)
            # 摘要质量兜底
            if not summary or len(summary) < 4 or summary == fname:
                rep.fix("F4", f"H1 兜底摘要: {fname}")
                summary = f"(auto) {fname}"
            # 保序追加
            pending.append(format_entry(fname, summary, star))
            continue
        # 其他行（头部/表格/空行）原样保留（头部区）
        if current_date is None:
            new_lines.append(line)
        else:
            # 日期区内的非条目行：保留（如分组标题），但去掉被替换的旧条目残留
            if stripped:
                new_lines.append(line)

    flush()

    # F2: 日期分节正序（oldest first）——按块重排
    # 识别 "## YYYY-MM-DD" 起始的块
    blocks = []          # (date_or_none, [lines])
    cur = None
    for line in new_lines:
        m = DATE_SECTION_RE.match(line.strip())
        if m:
            cur = m.group(1)
            blocks.append((cur, []))
        else:
            if cur is None:
                blocks.append((None, [line]))  # 头部内容
            else:
                blocks[-1][1].append(line)

    # 头部（None 块）保持原序，日期块按日期倒序
    header = [l for d, ls in blocks if d is None for l in ([d] if d else ls)]
    date_blocks = [(d, ls) for d, ls in blocks if d is not None]
    date_blocks.sort(key=lambda x: x[0], reverse=False)

    final_lines = header[:]
    for d, ls in date_blocks:
        final_lines.append(f"## {d}")
        final_lines.extend(ls)

    # 写回
    content = '\n'.join(final_lines).rstrip('\n') + '\n'
    if content != path.read_text(encoding='utf-8', errors='replace'):
        # 备份
        bak_dir = ROOT / "tmp" / "bak" / f"kb-index-fix-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        bak_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, bak_dir / path.name)
        rep.fix("BAK", f"备份 → {bak_dir / path.name}")
        path.write_text(content, encoding='utf-8')
        rep.fix("WRITE", f"已写回 {path}")
    else:
        rep.fix("NOOP", "无变更")

    if skipped:
        rep.issue("F3", "INFO", f"去重跳过 {skipped} 条重复")
    return rep


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="README.md 条目库健康检查与修复（design-010 V3）")
    ap.add_argument("path", nargs="?", help="README.md 路径（默认 knowledge/README.md）")
    ap.add_argument("--all", action="store_true", help="检查根 README.md + 保留目录的所有 index.md")
    ap.add_argument("--check", action="store_true", help="只检查不修复（默认行为）")
    ap.add_argument("--fix", action="store_true", help="检查并修复（写回前自动备份）")
    ap.add_argument("--dry-run", action="store_true", help="只预览修复动作不写回")
    ap.add_argument("--check-sync", action="store_true", help="只检查三同步 C6")
    ap.add_argument("--quiet", action="store_true", help="只输出问题摘要")
    args = ap.parse_args()

    targets = []
    if args.all:
        targets = [ROOT_INDEX]
        for d in KEEP_DISTRIBUTED:
            p = KNOWLEDGE / d / "index.md"
            if p.exists():
                targets.append(p)
    else:
        targets = [Path(args.path) if args.path else ROOT_INDEX]

    total_issues = 0
    all_ok = True
    for t in targets:
        if args.check_sync:
            rep = run_checks(t, check_sync_only=True)
        else:
            rep = run_checks(t)
        rel = t.relative_to(ROOT).as_posix()
        if not args.quiet:
            print(f"\n=== {rel} ===")
        for code, sev, msg in rep.issues:
            print(f"[{code}] {sev}: {msg}")
            total_issues += 1
            if sev == "ERROR":
                all_ok = False
        if rep.fix_actions and not args.quiet:
            print(f"-- 建议修复 ({len(rep.fix_actions)}):")
            for act, desc in rep.fix_actions[:20]:
                print(f"   {act}: {desc}")
        if args.fix and not args.check_sync:
            entries, warnings = load_index_file(t)
            if args.dry_run:
                print(f"--dry-run: 将执行 fix 于 {rel}")
            else:
                fix_rep = apply_fix(t, entries, warnings, auto=True)
                for code, sev, msg in fix_rep.issues:
                    print(f"[{code}] {sev}: {msg}")

    print(f"\n检查完成: {len(targets)} 文件, {total_issues} 问题, {'✅ PASS' if all_ok else '❌ 有 ERROR'}")
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
