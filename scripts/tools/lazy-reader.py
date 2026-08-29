#!/usr/bin/env python3
"""
lazy-reader.py — 懒加载策略工具 (sr-006 X-07)

对大文件（>500 行）按需分段读取，避免一次加载全部内容到内存/上下文。

用法:
  # 作为模块引用
  from scripts.tools.lazy_reader import LazyReader

  # 打开大文件
  reader = LazyReader("knowledge/README.md")

  # 迭代所有行（内部按块加载）
  for line in reader:
      process(line)

  # 读取特定行范围
  section = reader.read_lines(100, 150)  # 100-150 行

  # 读取头部 N 行
  header = reader.head(50)

  # 读取尾部 N 行
  tail = reader.tail(30)

  # 按块迭代
  for chunk in reader.chunks(chunk_size=100):
      process(chunk)

  # 分割为段落（按 ## 或 --- 分隔）
  sections = reader.sections()

  # 搜索关键词所在行
  matches = reader.grep("优化建议")

  # 统计信息
  info = reader.info()

  # CLI 模式
  python3 scripts/tools/lazy-reader.py head <path> -n 10        # 头部
  python3 scripts/tools/lazy-reader.py tail <path> -n 10        # 尾部
  python3 scripts/tools/lazy-reader.py section <path> 100 150   # 行范围
  python3 scripts/tools/lazy-reader.py grep <path> <keyword>    # 搜索
  python3 scripts/tools/lazy-reader.py chunks <path> [--size 50] # 分块
  python3 scripts/tools/lazy-reader.py sections <path>          # 按标题分割
  python3 scripts/tools/lazy-reader.py info <path>              # 文件信息
  python3 scripts/tools/lazy-reader.py toc <path> [--depth 2]   # 目录提取
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import Optional, List, Iterator, Tuple, Generator

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# 大文件阈值
LARGE_FILE_LINES = 500


class LazyReader:
    """
    懒加载文件读取器。

    不会一次性将整个文件装入内存，而是按需分块读取。
    """

    def __init__(self, path: str, encoding: str = 'utf-8',
                 chunk_size: int = 100):
        """
        参数:
            path:       文件路径（相对或绝对）
            encoding:   文件编码
            chunk_size:  默认块大小（行数）
        """
        self.path = self._resolve(path)
        self.encoding = encoding
        self.chunk_size = chunk_size
        self._total_lines: Optional[int] = None

        if not self.path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        if not self.path.is_file():
            raise IsADirectoryError(f"不是文件: {path}")

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        return p.resolve()

    def _count_lines(self) -> int:
        """计算文件总行数（流式，不加载到内存）"""
        if self._total_lines is not None:
            return self._total_lines
        count = 0
        with open(self.path, 'r', encoding=self.encoding) as f:
            for _ in f:
                count += 1
        self._total_lines = count
        return count

    @property
    def total_lines(self) -> int:
        return self._count_lines()

    @property
    def is_large(self) -> bool:
        """是否是大文件"""
        return self.total_lines > LARGE_FILE_LINES

    def read_lines(self, start: int, end: Optional[int] = None) -> List[str]:
        """
        读取指定的行范围（1-indexed，闭区间）。

        参数:
            start: 起始行号 (1-indexed)
            end:   结束行号 (1-indexed, inclusive), 默认为 start

        返回: 行列表（不含换行符）
        """
        if end is None:
            end = start

        result = []
        with open(self.path, 'r', encoding=self.encoding) as f:
            for line_no, line in enumerate(f, 1):
                if line_no > end:
                    break
                if line_no >= start:
                    result.append(line.rstrip('\n\r'))
        return result

    def head(self, n: int = 50) -> List[str]:
        """读取头部 N 行"""
        return self.read_lines(1, n)

    def tail(self, n: int = 50) -> List[str]:
        """读取尾部 N 行（从文件末尾往回读）"""
        total = self.total_lines
        start = max(1, total - n + 1)
        return self.read_lines(start, total)

    def __iter__(self) -> Iterator[str]:
        """迭代所有行（逐行 yield，不加载全部到内存）"""
        with open(self.path, 'r', encoding=self.encoding) as f:
            for line in f:
                yield line.rstrip('\n\r')

    def chunks(self, chunk_size: Optional[int] = None) -> Generator[List[str], None, None]:
        """
        按块迭代。

        参数:
            chunk_size: 每块行数（默认使用初始化时的值）

        Yields: 行列表
        """
        size = chunk_size or self.chunk_size
        chunk = []
        with open(self.path, 'r', encoding=self.encoding) as f:
            for line in f:
                chunk.append(line.rstrip('\n\r'))
                if len(chunk) >= size:
                    yield chunk
                    chunk = []
        if chunk:
            yield chunk

    def sections(self, heading_pattern: str = r'^##\s|^#\s') -> List[Tuple[str, int, List[str]]]:
        """
        按标题分割文件内容。

        返回: [(标题, 起始行号, 内容行列表), ...]
        """
        pattern = re.compile(heading_pattern)
        sections = []
        current_title = "(前置)"
        current_start = 1
        current_lines = []

        with open(self.path, 'r', encoding=self.encoding) as f:
            for line_no, line in enumerate(f, 1):
                stripped = line.rstrip('\n\r')
                if pattern.match(stripped):
                    if current_lines:
                        sections.append((current_title, current_start, current_lines))
                    current_title = stripped[:80]
                    current_start = line_no
                    current_lines = []
                current_lines.append(stripped)

        if current_lines:
            sections.append((current_title, current_start, current_lines))

        return sections

    def grep(self, keyword: str, context: int = 0,
             case_sensitive: bool = True) -> List[Tuple[int, str, List[str]]]:
        """
        搜索关键词所在行。

        参数:
            keyword:       搜索关键词
            context:       上下文行数（前后各 N 行）
            case_sensitive: 是否大小写敏感

        返回: [(行号, 匹配行, [上下文行]), ...]
        """
        results = []
        all_lines: List[str] = []
        flag = 0 if case_sensitive else re.IGNORECASE

        # 先加载全部到内存（搜索场景下是需要的）
        with open(self.path, 'r', encoding=self.encoding) as f:
            all_lines = [line.rstrip('\n\r') for line in f]

        for i, line in enumerate(all_lines):
            if re.search(keyword, line, flag):
                ctx_start = max(0, i - context)
                ctx_end = min(len(all_lines), i + context + 1)
                context_lines = all_lines[ctx_start:ctx_end]
                results.append((i + 1, line, context_lines))

        return results

    def toc(self, depth: int = 2) -> List[Tuple[int, str, int]]:
        """
        提取目录结构（扫描标题行）。

        返回: [(行号, 标题文本, 级别), ...]
        """
        pattern = re.compile(r'^(#{1,%d})\s+(.+)$' % depth)
        toc_entries = []
        with open(self.path, 'r', encoding=self.encoding) as f:
            for line_no, line in enumerate(f, 1):
                m = pattern.match(line)
                if m:
                    level = len(m.group(1))
                    title = m.group(2).strip()
                    toc_entries.append((line_no, title, level))
        return toc_entries

    def info(self) -> dict:
        """文件信息"""
        total = self.total_lines
        size_bytes = self.path.stat().st_size
        size_kb = size_bytes / 1024
        is_large = total > LARGE_FILE_LINES

        # 估算章节数
        section_count = 0
        with open(self.path, 'r', encoding=self.encoding) as f:
            for line in f:
                if line.startswith('## '):
                    section_count += 1

        return {
            "path": str(self.path),
            "lines": total,
            "size_bytes": size_bytes,
            "size_kb": round(size_kb, 1),
            "is_large": is_large,
            "sections": section_count,
            "encoding": self.encoding,
        }

    def print_info(self):
        """打印文件信息"""
        info = self.info()
        print(f"📄 文件信息: {info['path']}")
        print(f"  行数:     {info['lines']}")
        print(f"  大小:     {info['size_kb']} KB ({info['size_bytes']} 字节)")
        print(f"  编码:     {info['encoding']}")
        print(f"  大文件:   {'✅ 是' if info['is_large'] else '否'}")
        print(f"  ## 章节:  {info['sections']} 个")


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="懒加载文件读取工具 (sr-006 X-07)",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    p_head = subparsers.add_parser("head", help="读取头部")
    p_head.add_argument("path", help="文件路径")
    p_head.add_argument("-n", type=int, default=10, help="行数")

    p_tail = subparsers.add_parser("tail", help="读取尾部")
    p_tail.add_argument("path", help="文件路径")
    p_tail.add_argument("-n", type=int, default=10, help="行数")

    p_section = subparsers.add_parser("section", help="行范围")
    p_section.add_argument("path", help="文件路径")
    p_section.add_argument("start", type=int, help="起始行")
    p_section.add_argument("end", type=int, nargs="?", help="结束行")

    p_grep = subparsers.add_parser("grep", help="搜索关键词")
    p_grep.add_argument("path", help="文件路径")
    p_grep.add_argument("keyword", help="关键词")
    p_grep.add_argument("-c", "--context", type=int, default=0, help="上下文行数")
    p_grep.add_argument("-i", "--ignore-case", action="store_true", help="忽略大小写")

    p_chunks = subparsers.add_parser("chunks", help="分块显示")
    p_chunks.add_argument("path", help="文件路径")
    p_chunks.add_argument("--size", type=int, default=50, help="块大小")

    p_sections = subparsers.add_parser("sections", help="按标题分割")
    p_sections.add_argument("path", help="文件路径")

    p_info = subparsers.add_parser("info", help="文件信息")
    p_info.add_argument("path", help="文件路径")

    p_toc = subparsers.add_parser("toc", help="目录提取")
    p_toc.add_argument("path", help="文件路径")
    p_toc.add_argument("--depth", type=int, default=2, help="标题深度")

    args = parser.parse_args()

    try:
        if args.command == "head":
            reader = LazyReader(args.path)
            lines = reader.head(args.n)
            print(f"📄 {args.path} 前 {args.n} 行:")
            print("─" * 40)
            for i, line in enumerate(lines, 1):
                print(f"  {i:4d} | {line}")

        elif args.command == "tail":
            reader = LazyReader(args.path)
            lines = reader.tail(args.n)
            total = reader.total_lines
            print(f"📄 {args.path} 后 {args.n} 行 (共 {total} 行):")
            print("─" * 40)
            for i, line in enumerate(lines, total - len(lines) + 1):
                print(f"  {i:4d} | {line}")

        elif args.command == "section":
            reader = LazyReader(args.path)
            end = args.end or args.start
            lines = reader.read_lines(args.start, end)
            print(f"📄 {args.path} [{args.start}-{end}]:")
            print("─" * 40)
            for i, line in enumerate(lines, args.start):
                print(f"  {i:4d} | {line}")

        elif args.command == "grep":
            reader = LazyReader(args.path)
            matches = reader.grep(args.keyword, context=args.context,
                                  case_sensitive=not args.ignore_case)
            print(f"🔍 '{args.keyword}' 找到 {len(matches)} 处:")
            print("─" * 60)
            for line_no, line, ctx in matches[:30]:
                print(f"  L{line_no:5d} | {line[:100]}")
                if ctx and len(ctx) > 1:
                    for cl in ctx:
                        print(f"         | {cl[:80]}")
                    print(f"  {'─' * 50}")
            if len(matches) > 30:
                print(f"  ... 及其他 {len(matches) - 30} 处")

        elif args.command == "chunks":
            reader = LazyReader(args.path)
            for i, chunk in enumerate(reader.chunks(args.size)):
                print(f"\n📦 块 #{i + 1} ({len(chunk)} 行):")
                for line in chunk[:10]:
                    print(f"  {line[:80]}")
                if len(chunk) > 10:
                    print(f"  ... 及其他 {len(chunk) - 10} 行")

        elif args.command == "sections":
            reader = LazyReader(args.path)
            secs = reader.sections()
            print(f"📑 {args.path} 章节结构 ({len(secs)} 个):")
            print("─" * 60)
            for title, start, lines in secs:
                print(f"  L{start:5d} | {title[:70]} ({len(lines)} 行)")

        elif args.command == "info":
            reader = LazyReader(args.path)
            reader.print_info()

        elif args.command == "toc":
            reader = LazyReader(args.path)
            entries = reader.toc(args.depth)
            print(f"📑 {args.path} 目录 (深度 ≤ {args.depth}):")
            print("─" * 60)
            for line_no, title, level in entries:
                indent = "  " * (level - 1)
                print(f"  L{line_no:5d} | {indent}{'#' * level} {title}")

        else:
            parser.print_help()

    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
