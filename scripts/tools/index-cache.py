#!/usr/bin/env python3
"""
index-cache.py — 批量读缓存工具 (sr-006 X-05)

对高频读取的 index.md 文件提供内存+磁盘两层缓存，避免重复 I/O。

用法:
  # 作为模块引用
  from scripts.tools.index_cache import IndexCache
  cache = IndexCache()

  # 读取 README.md（根索引导航/条目库）
  content = cache.read("knowledge/README.md")
  # 读取 index.md（默认操作对象：全局文件索引）
  content = cache.read("knowledge/index.md")

  # 读取多个 index 文件（批量加载）
  contents = cache.batch_read([
      "knowledge/README.md",
      "knowledge/index.md",
  ])

  # 强制刷新
  cache.refresh("knowledge/README.md")
  cache.refresh_all()

  # 统计
  cache.stats()

  # CLI 模式
  python3 scripts/tools/index-cache.py read <path>        # 读取（使用缓存）
  python3 scripts/tools/index-cache.py batch <path>...    # 批量读取
  python3 scripts/tools/index-cache.py refresh <path>     # 刷新缓存
  python3 scripts/tools/index-cache.py refresh-all        # 全刷新
  python3 scripts/tools/index-cache.py stats              # 缓存统计
  python3 scripts/tools/index-cache.py warmup             # 预热公共 index
"""

import sys
import os
import json
import time
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = REPO_ROOT / 'logs' / 'cache'
CACHE_TTL_SEC = 300  # 缓存 TTL: 5 分钟
WARMUP_PATHS = [
    "knowledge/README.md",     # 根导航 + 人工条目库（v1.1 由 index.md 更名）
    "knowledge/index.md",      # 全局文件索引（默认操作对象）
    "knowledge/log.md",
    "skills/README.md",
]

# ── 内存缓存 (进程内共享) ──
_memory_cache: Dict[str, Tuple[float, str, str]] = {}
#   key: 规范化的绝对路径
#   value: (mtime, content, md5)


class IndexCache:
    """双层缓存：内存 (L1) + 磁盘 (L2)"""

    def __init__(self, ttl_sec: int = CACHE_TTL_SEC, use_l2: bool = True):
        self.ttl_sec = ttl_sec
        self.use_l2 = use_l2
        if use_l2:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._hits_l1 = 0
        self._hits_l2 = 0
        self._misses = 0

    def _normalize(self, path: str) -> Path:
        """规范化路径为绝对路径"""
        p = Path(path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        return p.resolve()

    def _cache_key(self, path: Path) -> str:
        """缓存键（文件路径的 MD5）"""
        return hashlib.md5(str(path).encode()).hexdigest()

    def _l2_path(self, cache_key: str) -> Path:
        """L2 缓存文件路径"""
        return CACHE_DIR / f"{cache_key}.json"

    def read(self, path: str) -> Optional[str]:
        """
        读取文件内容（使用缓存）。

        返回文件内容字符串，失败时返回 None。
        """
        full_path = self._normalize(path)

        if not full_path.exists():
            self._misses += 1
            return None

        # 获取文件 mtime
        current_mtime = full_path.stat().st_mtime
        key = self._cache_key(full_path)

        # L1: 内存缓存
        if key in _memory_cache:
            mtime, content, _ = _memory_cache[key]
            if mtime == current_mtime and (time.time() - mtime) < self.ttl_sec:
                self._hits_l1 += 1
                return content

        # L2: 磁盘缓存
        if self.use_l2:
            l2p = self._l2_path(key)
            if l2p.exists():
                try:
                    with open(l2p, 'r', encoding='utf-8') as f:
                        cached = json.load(f)
                    if cached.get("mtime") == current_mtime and \
                       (time.time() - cached.get("time", 0)) < self.ttl_sec:
                        content = cached.get("content", "")
                        # 写回 L1
                        _memory_cache[key] = (current_mtime, content,
                                              hashlib.md5(content.encode()).hexdigest())
                        self._hits_l2 += 1
                        return content
                except (json.JSONDecodeError, OSError):
                    pass

        # Miss: 实际读取
        self._misses += 1
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  读取失败 {full_path}: {e}", file=sys.stderr)
            return None

        md5 = hashlib.md5(content.encode()).hexdigest()
        # 写回 L1
        _memory_cache[key] = (current_mtime, content, md5)
        # 写回 L2
        if self.use_l2:
            try:
                with open(self._l2_path(key), 'w', encoding='utf-8') as f:
                    json.dump({
                        "path": str(full_path),
                        "mtime": current_mtime,
                        "time": time.time(),
                        "content": content,
                        "md5": md5,
                        "lines": len(content.splitlines()),
                    }, f, ensure_ascii=False, indent=2)
            except OSError:
                pass

        return content

    def batch_read(self, paths: List[str]) -> Dict[str, Optional[str]]:
        """批量读取多个文件"""
        result = {}
        for p in paths:
            result[p] = self.read(p)
        return result

    def refresh(self, path: str):
        """强制刷新单个缓存"""
        full_path = self._normalize(path)
        key = self._cache_key(full_path)

        # 清除 L1
        if key in _memory_cache:
            del _memory_cache[key]

        # 清除 L2
        if self.use_l2:
            l2p = self._l2_path(key)
            if l2p.exists():
                l2p.unlink()

        # 重新读取
        self.read(path)

    def refresh_all(self):
        """清空所有缓存"""
        _memory_cache.clear()
        if self.use_l2 and CACHE_DIR.exists():
            count = 0
            for p in CACHE_DIR.iterdir():
                if p.suffix == '.json':
                    p.unlink()
                    count += 1
            print(f"🗑️  已清空 {count} 个 L2 缓存文件")

    def stats(self) -> dict:
        """缓存统计"""
        total = self._hits_l1 + self._hits_l2 + self._misses
        hit_rate = (self._hits_l1 + self._hits_l2) / total * 100 if total > 0 else 0
        return {
            "l1_hits": self._hits_l1,
            "l2_hits": self._hits_l2,
            "misses": self._misses,
            "total": total,
            "hit_rate_pct": round(hit_rate, 1),
            "l1_size": len(_memory_cache),
            "l2_count": len(list(CACHE_DIR.glob("*.json"))) if CACHE_DIR.exists() else 0,
        }

    def warmup(self, paths: Optional[List[str]] = None):
        """预热缓存"""
        targets = paths or WARMUP_PATHS
        loaded = 0
        for p in targets:
            content = self.read(p)
            if content is not None:
                loaded += 1
                print(f"  ✅ {p} ({len(content.splitlines())} 行)")
            else:
                print(f"  ⚠️  {p} 不存在")
        print(f"\n📦 已预热 {loaded}/{len(targets)} 个文件")

    def print_stats(self):
        """打印统计"""
        s = self.stats()
        print(f"\n📊 索引缓存统计:")
        print(f"  L1 命中:     {s['l1_hits']}")
        print(f"  L2 命中:     {s['l2_hits']}")
        print(f"  未命中:      {s['misses']}")
        print(f"  总请求:      {s['total']}")
        print(f"  命中率:      {s['hit_rate_pct']}%")
        print(f"  L1 大小:     {s['l1_size']} 项")
        print(f"  L2 文件数:   {s['l2_count']}")


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="批量读缓存工具 (sr-006 X-05)",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    p_read = subparsers.add_parser("read", help="读取（使用缓存）")
    p_read.add_argument("path", help="文件路径")

    p_batch = subparsers.add_parser("batch", help="批量读取")
    p_batch.add_argument("paths", nargs="+", help="文件路径列表")

    p_refresh = subparsers.add_parser("refresh", help="刷新缓存")
    p_refresh.add_argument("path", help="文件路径")

    subparsers.add_parser("refresh-all", help="清空所有缓存")
    subparsers.add_parser("stats", help="缓存统计")
    subparsers.add_parser("warmup", help="预热公共 index")

    args = parser.parse_args()
    cache = IndexCache()

    if args.command == "read":
        content = cache.read(args.path)
        if content is not None:
            print(content)
        else:
            print(f"❌ 无法读取: {args.path}")
            sys.exit(1)

    elif args.command == "batch":
        results = cache.batch_read(args.paths)
        for path, content in results.items():
            if content is not None:
                lines = len(content.splitlines())
                print(f"✅ {path} ({lines} 行)")
            else:
                print(f"❌ {path} 失败")

    elif args.command == "refresh":
        cache.refresh(args.path)
        print(f"🔄 已刷新: {args.path}")

    elif args.command == "refresh-all":
        cache.refresh_all()

    elif args.command == "stats":
        cache.print_stats()

    elif args.command == "warmup":
        cache.warmup()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
