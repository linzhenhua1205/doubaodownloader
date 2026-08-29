#!/usr/bin/env python3
"""
confirm-diff.py — 操作确认点工具 (sr-006 X-13)

在破坏性操作（移动/覆盖/删除/批量修改）前输出结构性 diff 并请求确认。

用法:
  # 作为模块引用
  from scripts.tools.confirm_diff import confirm_diff, confirm_operation

  # 文件级别的 diff 确认
  if not confirm_diff("old.txt", "new.txt", label="修改 config"):
      print("用户取消")
      sys.exit(4)

  # 路径级操作确认
  if not confirm_operation(
      action="移动文件",
      target="knowledge/01_survey/old.md",
      dest="knowledge/07_industry-research/old.md",
      details="将调研报告移入行业研究目录"
  ):
      sys.exit(4)

  # CLI 模式
  python3 scripts/tools/confirm-diff.py file <old> <new> [--label "修改原因"]
  python3 scripts/tools/confirm-diff.py op --action "删除" --target <path> [--details ...]

环境变量:
  CONFIRM_DIFF_ALWAYS_YES=1   — 跳过所有确认（批量/自动化模式）
  CONFIRM_DIFF_SHOW_DIFF=1    — 始终显示 diff（默认仅交互式终端显示）
"""

import sys
import os
import difflib
import argparse
from pathlib import Path
from typing import Optional, List

# ── 环境变量控制 ──
ALWAYS_YES = os.environ.get("CONFIRM_DIFF_ALWAYS_YES", "0") == "1"
SHOW_DIFF = os.environ.get("CONFIRM_DIFF_SHOW_DIFF", "0") == "1"
_IS_TTY = os.isatty(sys.stdin.fileno()) and os.isatty(sys.stdout.fileno())


def _color(text: str, code: int = 0) -> str:
    if _IS_TTY:
        return f"\033[{code}m{text}\033[0m"
    return text


RED = lambda t: _color(t, 31)
GREEN = lambda t: _color(t, 32)
YELLOW = lambda t: _color(t, 33)
CYAN = lambda t: _color(t, 36)
BOLD = lambda t: _color(t, 1)
DIM = lambda t: _color(t, 2)


def _read_file(path: str) -> Optional[List[str]]:
    """读取文件内容，返回行列表或 None"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"⚠️  读取失败 {path}: {e}", file=sys.stderr)
        return None


def compute_diff(old_path: str, new_path: str,
                 old_label: str = "原文件",
                 new_label: str = "新文件") -> List[str]:
    """
    计算两个文件之间的结构性 diff。

    返回 diff 行列表（带颜色）。
    """
    old_lines = _read_file(old_path)
    new_lines = _read_file(new_path)

    if old_lines is None and new_lines is None:
        return ["[两个文件均无法读取]"]
    if old_lines is None:
        return [GREEN(f"[新增文件: {new_path}]")]
    if new_lines is None:
        return [RED(f"[删除文件: {old_path}]")]

    # 生成 unified diff
    diff_lines = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=old_label, tofile=new_label,
        n=3  # 上下文行数
    ))

    if not diff_lines:
        return ["[无差异]"]

    # 着色
    colored = []
    for line in diff_lines[:100]:  # 最多显示 100 行
        if line.startswith('+'):
            colored.append(GREEN(line.rstrip()))
        elif line.startswith('-'):
            colored.append(RED(line.rstrip()))
        elif line.startswith('@@'):
            colored.append(CYAN(line.rstrip()))
        else:
            colored.append(DIM(line.rstrip()))

    if len(diff_lines) > 100:
        colored.append(DIM(f"... 及 {len(diff_lines) - 100} 行差异"))
        colored.append(DIM(f"  完整 diff: diff -u '{old_path}' '{new_path}'"))

    return colored


def print_diff(old_path: str, new_path: str,
               old_label: str = "原文件", new_label: str = "新文件"):
    """打印 diff 到 stderr"""
    diff_lines = compute_diff(old_path, new_path, old_label, new_label)
    print(f"\n{'─' * 60}", file=sys.stderr)
    print(f"📋 Diff: {old_label} ↔ {new_label}", file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)
    for line in diff_lines:
        print(line, file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)


def confirm_diff(old_path: str, new_path: str, *,
                 label: str = "确认操作",
                 old_label: str = "原文件",
                 new_label: str = "新文件") -> bool:
    """
    在文件修改前进行 diff 确认。

    返回:
        True  — 用户确认继续
        False — 用户取消 / 非交互式终端且无 ALWAYS_YES
    """
    # 自动模式：跳过确认
    if ALWAYS_YES:
        return True

    # 计算 diff
    diff_lines = compute_diff(old_path, new_path, old_label, new_label)
    has_diff = any(not l.startswith('[') for l in diff_lines)

    if not has_diff or diff_lines == ["[无差异]"]:
        return True  # 无差异，无需确认

    # 显示 diff
    print(f"\n{'═' * 60}", file=sys.stderr)
    print(f"🛑 {BOLD(label)}", file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)
    for line in diff_lines:
        print(line, file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)

    # 非交互式终端 → 拒绝
    if not _IS_TTY and not ALWAYS_YES:
        print("⚠️  非交互式终端，操作已拒绝。", file=sys.stderr)
        print("  设置 CONFIRM_DIFF_ALWAYS_YES=1 以跳过确认。", file=sys.stderr)
        return False

    # 交互式确认
    print(file=sys.stderr)
    try:
        response = input(f"{YELLOW('?')} 确认执行? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        return False

    if response in ('y', 'yes'):
        return True
    else:
        print("⏭️  操作已取消。", file=sys.stderr)
        return False


def confirm_operation(action: str, target: str, *,
                      dest: str = "", details: str = "",
                      items_count: int = 0) -> bool:
    """
    对破坏性操作（非文件修改）进行确认。

    参数:
        action:      操作类型（"移动"/"删除"/"覆盖"/"批量修改"等）
        target:      操作目标路径
        dest:        目标路径（移动/复制时）
        details:     操作说明
        items_count: 涉及文件数（批量操作时）

    返回:
        True — 确认继续 | False — 取消
    """
    if ALWAYS_YES:
        return True

    print(f"\n{'═' * 60}", file=sys.stderr)
    print(f"🛑 {BOLD(f'确认: {action}')}", file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)
    print(f"  操作: {action}", file=sys.stderr)
    print(f"  目标: {target}", file=sys.stderr)
    if dest:
        print(f"  目标位置: {dest}", file=sys.stderr)
    if details:
        print(f"  说明: {details}", file=sys.stderr)
    if items_count > 0:
        print(f"  涉及文件: {items_count} 个", file=sys.stderr)
    print(f"{'─' * 60}", file=sys.stderr)

    if not _IS_TTY and not ALWAYS_YES:
        print("⚠️  非交互式终端，操作已拒绝。", file=sys.stderr)
        print("  设置 CONFIRM_DIFF_ALWAYS_YES=1 以跳过确认。", file=sys.stderr)
        return False

    print(file=sys.stderr)
    try:
        response = input(f"{YELLOW('?')} 确认执行? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        return False

    if response in ('y', 'yes'):
        return True
    else:
        print("⏭️  操作已取消。", file=sys.stderr)
        return False


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="操作确认点工具 (sr-006 X-13)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # file — diff 确认
    p_file = subparsers.add_parser("file", help="基于文件 diff 的确认")
    p_file.add_argument("old", help="原文件路径")
    p_file.add_argument("new", help="新文件路径")
    p_file.add_argument("--label", default="确认修改", help="操作标签")
    p_file.add_argument("--old-label", default="原文件", help="原文件标签")
    p_file.add_argument("--new-label", default="新文件", help="新文件标签")

    # op — 操作确认
    p_op = subparsers.add_parser("op", help="通用操作确认")
    p_op.add_argument("--action", required=True, help="操作类型")
    p_op.add_argument("--target", required=True, help="操作目标")
    p_op.add_argument("--dest", default="", help="目标位置")
    p_op.add_argument("--details", default="", help="操作说明")
    p_op.add_argument("--count", type=int, default=0, help="涉及文件数")

    # auto — 自动模式设置
    p_auto = subparsers.add_parser("auto", help="设置自动模式")
    p_auto.add_argument("--yes", action="store_true", help="跳过所有确认")
    p_auto.add_argument("--no", action="store_true", help="恢复交互式确认")

    args = parser.parse_args()

    if args.command == "file":
        result = confirm_diff(
            args.old, args.new,
            label=args.label,
            old_label=args.old_label,
            new_label=args.new_label,
        )
        sys.exit(0 if result else 4)

    elif args.command == "op":
        result = confirm_operation(
            action=args.action,
            target=args.target,
            dest=args.dest,
            details=args.details,
            items_count=args.count,
        )
        sys.exit(0 if result else 4)

    elif args.command == "auto":
        if args.yes:
            print("🔧 设置 CONFIRM_DIFF_ALWAYS_YES=1 — 将跳过所有确认")
            print("   如需持久化，请加入 .bashrc 或环境变量配置")
        elif args.no:
            print("🔧 取消 CONFIRM_DIFF_ALWAYS_YES — 恢复交互式确认")
        # 提示用户设置环境变量
        print("\n   export CONFIRM_DIFF_ALWAYS_YES=1   # 跳过确认")
        print("   export CONFIRM_DIFF_SHOW_DIFF=1    # 始终显示 diff")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
