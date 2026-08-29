#!/usr/bin/env python3
"""
stderr-logger.py — 标准化错误日志记录器 (sr-006 X-12)

将所有脚本的错误/警告/调试输出写入 logs/ 目录，带时间戳和源文件标记。

用法:
  # 作为模块引用
  from scripts.tools.stderr-logger import Logger
  log = Logger("my-script")
  log.info("开始处理...")
  log.warn("配置未指定，使用默认值")
  log.error("文件不存在", exc_info=True)

  # CLI 模式 — 查看/清理日志
  python3 scripts/tools/stderr-logger.py list            # 列出最近的日志文件
  python3 scripts/tools/stderr-logger.py view <file>     # 查看日志内容
  python3 scripts/tools/stderr-logger.py clean --days 7  # 清理7天前的日志
  python3 scripts/tools/stderr-logger.py status           # 日志目录状态

日志目录结构:
  logs/
  ├── stderr/                  # 脚本运行日志
  │   ├── YYYY-MM-DD/          # 按日期分目录
  │   │   ├── <script-name>.log
  │   │   └── ...
  │   └── latest/              # 最新日志的符号链接
  └── README.md                # 日志说明
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

# ── 路径 ──
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = REPO_ROOT / 'logs' / 'stderr'
MAX_LOG_AGE_DAYS = 30      # 默认日志保留天数
MAX_LOG_SIZE_MB = 10       # 单日志文件最大 MB
MAX_LOG_FILES = 200        # 最多保留文件数

# ── 颜色 (仅在终端启用时) ──
_USE_COLOR = os.isatty(sys.stderr.fileno())


def _color(code: int, text: str) -> str:
    if _USE_COLOR:
        return f"\033[{code}m{text}\033[0m"
    return text


GREEN = lambda t: _color(32, t)
YELLOW = lambda t: _color(33, t)
RED = lambda t: _color(31, t)
CYAN = lambda t: _color(36, t)
BOLD = lambda t: _color(1, t)
DIM = lambda t: _color(2, t)


class Logger:
    """标准化日志记录器 — 同时输出到 stderr 和日志文件"""

    LEVELS = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "FATAL": 4}
    LEVEL_COLORS = {
        "DEBUG": DIM,
        "INFO": GREEN,
        "WARN": YELLOW,
        "ERROR": RED,
        "FATAL": lambda t: RED(BOLD(t)),
    }

    def __init__(self, name: str = "default", level: str = "INFO",
                 log_to_file: bool = True, echo: bool = True):
        """
        初始化日志器。

        参数:
            name:        日志器名称（通常是脚本名，不含 .py）
            level:       最低输出级别 (DEBUG/INFO/WARN/ERROR/FATAL)
            log_to_file: 是否写入日志文件
            echo:        是否同时输出到 stderr
        """
        self.name = name
        self.level = self.LEVELS.get(level.upper(), 1)
        self.log_to_file = log_to_file
        self.echo = echo

        # 日志文件路径
        date_str = datetime.now().strftime("%Y-%m-%d")
        self._date_str = date_str
        self._log_path = LOG_DIR / date_str / f"{name}.log"

        if log_to_file:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_log_file()

    def _init_log_file(self):
        """初始化日志文件（写 header）"""
        if self._log_path.exists() and self._log_path.stat().st_size > 0:
            return  # 已有内容不重复 header
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = (
            f"# ═══════════════════════════════════════════\n"
            f"# 日志器: {self.name}\n"
            f"# 启动:   {ts}\n"
            f"# PID:    {os.getpid()}\n"
            f"# ═══════════════════════════════════════════\n"
        )
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._log_path, 'a', encoding='utf-8') as f:
                f.write(header)
        except OSError as e:
            # 日志文件写入失败时 fallback 到 stderr
            print(f"⚠️  无法写入日志文件 {self._log_path}: {e}", file=sys.stderr)

    def _log(self, level: str, message: str, *, exc_info: bool = False):
        """核心日志方法"""
        level_int = self.LEVELS.get(level, 1)
        if level_int < self.level:
            return

        ts = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{ts}] [{level:5s}] [{self.name}] {message}"

        # 写入文件
        if self.log_to_file:
            try:
                with open(self._log_path, 'a', encoding='utf-8') as f:
                    f.write(f"{log_line}\n")
                    if exc_info:
                        import traceback
                        traceback.print_exc(file=f)
            except OSError:
                pass  # fallback silent

            # 日志轮转（检查大小）
            self._check_rotate()

        # 输出到 stderr
        if self.echo:
            color_fn = self.LEVEL_COLORS.get(level, lambda t: t)
            timestamp_color = CYAN(ts)
            level_padded = f"{level:5s}"
            colored_level = color_fn(level_padded) if level in self.LEVEL_COLORS else level_padded
            colored_msg = color_fn(message) if level in ("ERROR", "FATAL", "WARN") else message
            print(f"{timestamp_color} [{colored_level}] [{self.name}] {colored_msg}", file=sys.stderr)
            if exc_info:
                import traceback
                traceback.print_exc(file=sys.stderr)

    def _check_rotate(self):
        """检查日志文件大小，超过限制时滚动"""
        try:
            size_mb = self._log_path.stat().st_size / (1024 * 1024)
            if size_mb > MAX_LOG_SIZE_MB:
                # 重命名当前文件
                ts = datetime.now().strftime("%H%M%S")
                rotated = self._log_path.with_name(
                    f"{self.name}.{ts}.log"
                )
                self._log_path.rename(rotated)
                self._init_log_file()  # 创建新文件
                self._log("INFO", f"日志文件已达 {size_mb:.1f}MB，已滚动至 {rotated.name}")
        except OSError:
            pass

    def debug(self, message: str):
        self._log("DEBUG", message)

    def info(self, message: str):
        self._log("INFO", message)

    def warn(self, message: str):
        self._log("WARN", message)

    def error(self, message: str, *, exc_info: bool = False):
        self._log("ERROR", message, exc_info=exc_info)

    def fatal(self, message: str, *, exc_info: bool = False):
        self._log("FATAL", message, exc_info=exc_info)
        sys.exit(1)

    # ── 上下文管理器支持 ──
    def section(self, title: str):
        """返回一个上下文管理器，自动记录开始/结束"""
        return _LogSection(self, title)


class _LogSection:
    """日志段落上下文管理器"""
    def __init__(self, logger: Logger, title: str):
        self.logger = logger
        self.title = title
        self.start = datetime.now()

    def __enter__(self):
        ts = self.start.strftime("%H:%M:%S")
        self.logger.info(f"▶ {self.title}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start).total_seconds()
        status = "✅ 完成" if exc_type is None else "❌ 失败"
        self.logger.info(f"{status} {self.title} ({elapsed:.1f}s)")
        if exc_type is not None:
            self.logger.error(f"  异常: {exc_type.__name__}: {exc_val}")


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def cmd_list(args):
    """列出最近的日志文件"""
    log_root = LOG_DIR
    if not log_root.exists():
        print("📭 日志目录为空")
        return

    all_logs = sorted(log_root.rglob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not all_logs:
        print("📭 无日志文件")
        return

    print(f"📋 日志文件 ({len(all_logs)} 个):")
    displayed = 0
    for p in all_logs[:args.limit]:
        rel = p.relative_to(REPO_ROOT)
        size_kb = p.stat().st_size / 1024
        mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%m-%d %H:%M")
        print(f"  {rel}  ({size_kb:.0f}KB)  [{mtime}]")
        displayed += 1
    if len(all_logs) > args.limit:
        print(f"  ... 及其他 {len(all_logs) - args.limit} 个")


def cmd_view(args):
    """查看日志内容"""
    log_path = LOG_DIR / args.file
    if not log_path.exists():
        print(f"❌ 日志文件不存在: {log_path}")
        return

    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    if args.tail:
        lines = lines[-args.tail:]

    print(f"📄 {log_path.relative_to(REPO_ROOT)} ({len(lines)} 行):")
    print("─" * 60)
    for line in lines:
        print(line)
    print("─" * 60)


def cmd_clean(args):
    """清理旧日志"""
    cutoff = datetime.now().timestamp() - args.days * 86400
    removed = 0
    size_freed = 0

    for p in sorted(LOG_DIR.rglob("*.log")):
        if p.stat().st_mtime < cutoff:
            size_freed += p.stat().st_size
            if not args.dry_run:
                p.unlink()
            removed += 1

    # 清理空目录
    if not args.dry_run:
        for d in sorted(LOG_DIR.rglob("*"), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()

    mb_freed = size_freed / (1024 * 1024)
    print(f"{'🔍 [dry-run]' if args.dry_run else '🗑️'} 清理完成:")
    print(f"  删除: {removed} 个文件")
    print(f"  释放: {mb_freed:.1f} MB")
    print(f"  条件: {args.days} 天前")


def cmd_status(args):
    """日志目录状态"""
    log_root = LOG_DIR
    if not log_root.exists():
        print("📭 日志目录不存在")
        return

    all_logs = sorted(log_root.rglob("*.log"))
    total_size = sum(p.stat().st_size for p in all_logs)
    total_mb = total_size / (1024 * 1024)

    # 按天统计
    daily = {}
    for p in all_logs:
        date_part = p.parent.name if p.parent.parent == log_root else "other"
        daily[date_part] = daily.get(date_part, 0) + 1

    print(f"📊 日志目录状态:")
    print(f"  总文件: {len(all_logs)}")
    print(f"  总大小: {total_mb:.1f} MB")
    print(f"  按日期:")
    for date, count in sorted(daily.items(), reverse=True)[:10]:
        size = sum(p.stat().st_size for p in all_logs if p.parent.name == date)
        print(f"    {date}: {count} 个 ({size/1024:.0f} KB)")


def main():
    parser = argparse.ArgumentParser(
        description="标准化错误日志管理器 (sr-006 X-12)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # list
    p_list = subparsers.add_parser("list", help="列出最近日志文件")
    p_list.add_argument("--limit", type=int, default=30, help="显示数量上限")

    # view
    p_view = subparsers.add_parser("view", help="查看日志内容")
    p_view.add_argument("file", help="日志文件名（相对于 logs/stderr/）")
    p_view.add_argument("--tail", type=int, default=0, help="仅查看最后 N 行")

    # clean
    p_clean = subparsers.add_parser("clean", help="清理旧日志")
    p_clean.add_argument("--days", type=int, default=MAX_LOG_AGE_DAYS, help="保留天数")
    p_clean.add_argument("--dry-run", action="store_true", help="仅预览，不执行")

    # status
    p_status = subparsers.add_parser("status", help="日志目录状态")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "view":
        cmd_view(args)
    elif args.command == "clean":
        cmd_clean(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
