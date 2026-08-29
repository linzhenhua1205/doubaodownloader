#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhancer.py — 增强调度主入口（状态机 + 断点续传）
====================================================
设计约束: 无状态批处理(不依赖会话记忆), 文件级状态机落盘, 不覆盖源文件。
流程(对应设计文档 §10):
  1. 扫描输入目录(优先级排序: 小文件优先 / A类目录优先)
  2. 分级: L1(≤5KB 整文件) / L2(>20KB 分片)  —— L0 由 l0_normalize.py 先行
  3. 每文件: 读 → 分片 → 组装 payload(指令头+上下文头+正文) → LLM → 写产物
  4. 状态机: pending → processing → done / failed(重试2次后跳过)
  5. state.json 落盘, 断点可续(重复运行自动跳过 done)

用法:
  python3 enhancer.py --input import-enhanced/server --output enhanced/out \
      --level L2 --limit 10 --dry-run
  python3 enhancer.py --input import-enhanced --output enhanced/out --small-first
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from chunk import chunk_file, estimate_tokens
from llm_client import LLMClient

# ---------- 常量 ----------
SMALL_FILE_TOKENS = 2500     # ≤5KB 中文 ≈ 2.5K tokens → L1 整文件
CHUNK_MAX_TOKENS = 12000     # L2 每片目标(留指令头+输出空间)
RETRY_LIMIT = 2

LEVELS = ("L1", "L2")


# ---------- 状态管理 ----------
class StateStore:
    """文件级状态机: {rel_path: {status, level, tries, mtime, error}}"""

    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.data: dict = {}
        if state_path.exists():
            try:
                self.data = json.loads(state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.data = {}

    def save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")

    def get(self, rel: str) -> dict:
        return self.data.get(rel, {"status": "pending", "tries": 0})

    def set(self, rel: str, **kw):
        self.data.setdefault(rel, {"status": "pending", "tries": 0})
        self.data[rel].update(kw)
        self.save()


# ---------- 指令头模板 ----------
PROMPT_DIR = Path(__file__).parent / "prompts"

def load_instruction(level: str) -> str:
    """加载指令头(L1_summary.md / L2_enhance.md), 缓存。"""
    path = PROMPT_DIR / f"{level}_enhance.md"
    if not path.exists():
        # 兜底: 内嵌极简指令
        return ("[任务] 对给定文本做内容提炼与标准化。\n"
                "[约束] 只基于原文, 禁止引入外部事实; 补充内容用【补】标记。\n"
                "[输出] Markdown。")
    return path.read_text(encoding="utf-8").strip()


_INSTR_CACHE: dict = {}

def instruction_for(level: str) -> str:
    if level not in _INSTR_CACHE:
        _INSTR_CACHE[level] = load_instruction(level)
    return _INSTR_CACHE[level]


# ---------- 主流程 ----------
def scan_files(src_root: Path, small_first: bool) -> list[Path]:
    """扫描所有 .md 文件, 按优先级排序。"""
    files = [p for p in src_root.rglob("*") if p.is_file() and p.suffix.lower() in (".md", ".markdown", ".txt")]
    if small_first:
        # 小文件优先(吞吐最大化)
        files.sort(key=lambda p: p.stat().st_size)
    return files


def pick_level(p: Path) -> str:
    """分级: ≤5KB → L1 整文件; >20KB → L2 分片; 中间 → L1(保守)。"""
    size = p.stat().st_size
    if size <= 5 * 1024:
        return "L1"
    if size >= 20 * 1024:
        return "L2"
    return "L1"


def process_file(p: Path, rel: str, level: str, client: LLMClient,
                 out_root: Path, dry_run: bool) -> str:
    """处理单文件, 返回 'ok' 或异常信息。"""
    if dry_run:
        # dry-run: 只走分片/分级逻辑, 不调 LLM 不写盘
        return "ok(dry-run)"
    text = p.read_text(encoding="utf-8", errors="replace")
    instr = instruction_for(level)

    if level == "L1":
        # 整文件: 指令头 + 正文(≤5KB 时总 payload 远低于 16K)
        payload = f"{instr}\n\n---\n\n{text}"
        result = client.generate(payload, model_key="L1")
        pieces = [result]
    else:
        # L2: 分片处理, 逐片调用, 脚本拼接
        chunks = chunk_file(str(p), max_tokens=CHUNK_MAX_TOKENS)
        pieces = []
        for c in chunks:
            payload = f"{instr}\n\n---\n\n{c.payload}"
            pieces.append(client.generate(payload, model_key="L2"))
        result = "\n\n<!-- chunk-break -->\n\n".join(pieces)

    if dry_run:
        return "ok(dry-run)"

    # 产物: out_root/<rel> (不覆盖源文件)
    dst = out_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    header = (f"<!-- enhanced by import-enhancer | level={level} | "
              f"time={datetime.now().isoformat()} -->\n")
    dst.write_text(header + result + "\n", encoding="utf-8")
    return "ok"


def run(args) -> None:
    src_root = Path(args.input).resolve()
    out_root = Path(args.output).resolve()
    state = StateStore(out_root / "state.json")

    if not src_root.exists():
        sys.exit(f"[错误] 输入目录不存在: {src_root}")

    client = LLMClient() if not args.dry_run else None
    if client and not client.health():
        sys.exit("[错误] Ollama 未在线。请先启动: ollama serve (并拉取模型)")

    files = scan_files(src_root, args.small_first)
    if args.limit:
        files = files[: args.limit]

    print(f"[增强] 扫描到 {len(files)} 个文件 | 级别: {args.level or 'auto'} | dry_run={args.dry_run}")
    t0 = time.time()
    stats = {"ok": 0, "skip": 0, "fail": 0, "tokens": 0}

    for p in files:
        rel = str(p.relative_to(src_root))
        st = state.get(rel)

        # 断点续传: done 跳过
        if st["status"] == "done":
            stats["skip"] += 1
            continue
        # 失败重试限制
        if st["status"] == "failed" and st.get("tries", 0) >= RETRY_LIMIT:
            stats["skip"] += 1
            continue

        level = args.level if args.level in LEVELS else pick_level(p)
        state.set(rel, status="processing", level=level, mtime=str(p.stat().st_mtime))

        try:
            msg = process_file(p, rel, level, client, out_root, args.dry_run)
            if msg.startswith("ok"):
                state.set(rel, status="done", tries=st.get("tries", 0) + 0)
                stats["ok"] += 1
            else:
                state.set(rel, status="failed", tries=st.get("tries", 0) + 1, error=msg)
                stats["fail"] += 1
        except Exception as e:
            tries = st.get("tries", 0) + 1
            state.set(rel, status="failed", tries=tries, error=str(e))
            stats["fail"] += 1
            print(f"  [失败] {rel}: {e}")

        # 进度
        done = stats["ok"] + stats["fail"] + stats["skip"]
        if done % 20 == 0 or done == len(files):
            el = time.time() - t0
            print(f"  进度 {done}/{len(files)} | ok={stats['ok']} fail={stats['fail']} "
                  f"skip={stats['skip']} | {el:.0f}s")

    print(f"[增强] 完成: ok={stats['ok']} fail={stats['fail']} skip={stats['skip']} "
          f"耗时={time.time()-t0:.0f}s")
    print(f"[增强] 状态: {out_root / 'state.json'}")
    if stats["fail"]:
        print("[增强] 失败文件见 state.json (status=failed), 可修复后重跑续传")


def main() -> None:
    ap = argparse.ArgumentParser(description="import 目录增强调度器 (L1 轻增强/L2 深增强)")
    ap.add_argument("--input", required=True, help="L0 规范化后的输入目录")
    ap.add_argument("--output", required=True, help="增强产物目录(镜像结构)")
    ap.add_argument("--level", choices=LEVELS, default=None, help="强制级别(默认 auto: ≤5KB→L1, ≥20KB→L2)")
    ap.add_argument("--small-first", action="store_true", help="小文件优先")
    ap.add_argument("--limit", type=int, default=0, help="仅处理前 N 个(调试用)")
    ap.add_argument("--dry-run", action="store_true", help="只走流程不调 LLM 不写盘")
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
