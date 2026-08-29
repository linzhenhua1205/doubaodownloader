#!/usr/bin/env python3
"""
atomic-writer.py — 原子化写操作工具 (sr-006 X-06)

对 index/log 的更新用事务式写入：先写临时文件，确认成功后再替换原文件。
单个文件写入失败不影响整个批次。支持回滚。

用法:
  # 作为模块引用
  from scripts.tools.atomic_writer import AtomicWriter, atomic_write

  # 方式一: 简易函数
  atomic_write("knowledge/README.md", content)
  atomic_write("knowledge/log.md", log_entry, append=True)  # 追加模式

  # 方式二: 事务上下文管理器
  with AtomicWriter() as tx:
      tx.write("knowledge/log.md", log_entry)  # 全局日志
      tx.write("knowledge/log.old.md", archive_entry)  # 归档日志
  # 退出上下文时自动提交所有写入

  # 方式三: 批量写入 + 确认
  tx = AtomicWriter()
  tx.write("file1.md", content1)
  tx.write("file2.md", content2)
  tx.commit()  # 一次性提交
  # 或 tx.rollback()  # 撤销所有

  # CLI 模式
  python3 scripts/tools/atomic-writer.py write <path> <content> [--append]
  python3 scripts/tools/atomic-writer.py batch <path1>=<content> <path2>=<content>
  python3 scripts/tools/atomic-writer.py verify <path>...
"""

import sys
import os
import json
import tempfile
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TMP_DIR = REPO_ROOT / 'tmp' / 'atomic-writes'


class AtomicWriteError(Exception):
    """原子写操作异常"""
    pass


class AtomicWriter:
    """
    原子写事务管理器。

    用法:
        with AtomicWriter() as tx:
            tx.write("path/to/file.md", "content")
            tx.append("path/to/log.md", "new line\\n")
        # 自动 commit
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        参数:
            base_dir: 基准目录（默认仓库根目录），所有相对路径基于此
        """
        self.base_dir = Path(base_dir or REPO_ROOT)
        self._pending: List[Tuple[Path, Path, str, bool]] = []
        # (target_path, tmp_path, operation_type, is_append)
        self._committed = False
        self._rolled_back = False
        self._backups: Dict[str, Optional[str]] = {}  # path → original_content

    def _resolve(self, path: str) -> Path:
        """解析路径为绝对路径"""
        p = Path(path)
        if not p.is_absolute():
            p = self.base_dir / p
        return p.resolve()

    def _create_temp(self) -> Path:
        """创建临时文件"""
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            suffix='.tmp',
            prefix=f'aw_{datetime.now().strftime("%H%M%S")}_',
            dir=str(TMP_DIR)
        )
        os.close(fd)
        return Path(tmp_path)

    def write(self, path: str, content: str):
        """
        准备一个原子写操作。

        参数:
            path:    目标文件路径（相对或绝对）
            content: 写入内容

        注意: 写入尚未执行，调用 commit() 才真正写入
        """
        target = self._resolve(path)
        tmp = self._create_temp()

        # 写入临时文件
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(content)
        except OSError as e:
            tmp.unlink(missing_ok=True)
            raise AtomicWriteError(f"写入临时文件失败: {e}") from e

        # 备份原文件
        if target.exists():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    self._backups[str(target)] = f.read()
            except OSError:
                self._backups[str(target)] = None  # 无法备份
        else:
            self._backups[str(target)] = None

        self._pending.append((target, tmp, "write", False))

    def append(self, path: str, content: str):
        """
        准备一个原子追加操作。

        合并原文件内容 + 新追加内容到临时文件。
        """
        target = self._resolve(path)
        tmp = self._create_temp()

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            # 读取原文件
            existing = ""
            if target.exists():
                with open(target, 'r', encoding='utf-8') as f:
                    existing = f.read()

            # 合并
            full_content = existing + content
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(full_content)
        except OSError as e:
            tmp.unlink(missing_ok=True)
            raise AtomicWriteError(f"追加写入临时文件失败: {e}") from e

        # 备份
        if target.exists():
            try:
                with open(target, 'r', encoding='utf-8') as f:
                    self._backups[str(target)] = f.read()
            except OSError:
                self._backups[str(target)] = None
        else:
            self._backups[str(target)] = None

        self._pending.append((target, tmp, "append", True))

    def commit(self) -> List[str]:
        """
        提交所有未完成的写入操作。

        返回已写入的文件路径列表。
        """
        if self._committed:
            raise AtomicWriteError("已提交，不可重复 commit")
        if self._rolled_back:
            raise AtomicWriteError("已回滚，不可 commit")

        committed_files = []
        errors = []

        for target, tmp, op_type, _ in self._pending:
            try:
                # 原子替换：rename 在同一个文件系统是原子的
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(tmp), str(target))
                committed_files.append(str(target))
            except OSError as e:
                errors.append((str(target), str(e)))
                tmp.unlink(missing_ok=True)

        self._committed = True

        if errors:
            # 部分失败：回滚已成功的写入
            for committed in committed_files:
                self._rollback_file(committed)
            error_msg = "; ".join(f"{p}: {e}" for p, e in errors)
            raise AtomicWriteError(f"提交失败（已回滚）: {error_msg}")

        # 清理临时文件
        for _, tmp, _, _ in self._pending:
            tmp.unlink(missing_ok=True)

        return committed_files

    def rollback(self):
        """回滚所有未提交的操作"""
        if self._committed:
            raise AtomicWriteError("已提交，不可回滚")

        self._rolled_back = True

        for target, tmp, _, _ in self._pending:
            tmp.unlink(missing_ok=True)
            # 恢复备份
            self._rollback_file(str(target))

        self._pending.clear()

    def _rollback_file(self, path: str):
        """回滚单个文件"""
        original = self._backups.get(path)
        p = Path(path)
        if original is not None:
            try:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(original)
            except OSError:
                print(f"⚠️  回滚失败: {path}", file=sys.stderr)
        elif p.exists():
            try:
                p.unlink()
            except OSError:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and not self._committed and not self._rolled_back:
            self.commit()
        elif exc_type is not None and not self._committed:
            self.rollback()


# ══════════════════════════════════════════════════════════
#  便捷函数
# ══════════════════════════════════════════════════════════

def atomic_write(path: str, content: str, *, append: bool = False) -> str:
    """
    原子写：写文件，失败回滚。

    返回已写入的文件路径。
    """
    writer = AtomicWriter()
    if append:
        writer.append(path, content)
    else:
        writer.write(path, content)
    files = writer.commit()
    return files[0] if files else ""


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="原子化写操作工具 (sr-006 X-06)",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    p_write = subparsers.add_parser("write", help="写入文件")
    p_write.add_argument("path", help="目标路径")
    p_write.add_argument("content", help="内容（或使用 --file 从文件读取）")
    p_write.add_argument("--file", help="从文件读取内容")
    p_write.add_argument("--append", action="store_true", help="追加模式")
    p_write.add_argument("--confirm", action="store_true", help="写入前确认")

    p_batch = subparsers.add_parser("batch", help="批量写入")
    p_batch.add_argument("pairs", nargs="+", help="path=content 对")
    p_batch.add_argument("--confirm", action="store_true", help="确认")

    p_verify = subparsers.add_parser("verify", help="验证文件完整性")
    p_verify.add_argument("paths", nargs="+", help="文件路径")

    args = parser.parse_args()

    if args.command == "write":
        content = args.content
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except OSError as e:
                print(f"❌ 读取文件失败: {e}", file=sys.stderr)
                sys.exit(1)

        try:
            result = atomic_write(args.path, content, append=args.append)
            print(f"✅ 已写入: {result}")
        except AtomicWriteError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "batch":
        writer = AtomicWriter()
        for pair in args.pairs:
            if '=' not in pair:
                print(f"⚠️  跳过无效对: {pair}", file=sys.stderr)
                continue
            path, content = pair.split('=', 1)
            writer.write(path, content)

        try:
            files = writer.commit()
            print(f"✅ 已写入 {len(files)} 个文件:")
            for f in files:
                print(f"  - {f}")
        except AtomicWriteError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "verify":
        ok = True
        for path in args.paths:
            p = Path(path)
            if not p.exists():
                print(f"❌ 不存在: {path}")
                ok = False
            elif p.stat().st_size == 0:
                print(f"⚠️  空文件: {path}")
            else:
                print(f"✅ {path} ({p.stat().st_size} 字节)")
        sys.exit(0 if ok else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
