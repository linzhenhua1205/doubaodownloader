#!/usr/bin/env python3
"""
learn-manager.py — 模式学习暂存管理器（tech-learn 配套）

audit-002 封闭性加固：落地 learn_saver/learn_lister 设计承诺。
extract（从会话提取模式）是语义任务由 LLM 完成，save/list 是确定性操作由脚本完成。

用法:
  python3 scripts/tools/learn-manager.py save <pattern_name> --desc "..." --file <来源文件>
  python3 scripts/tools/learn-manager.py list [--tag TAG]
  python3 scripts/tools/learn-manager.py status <pattern_name>

存储: ~/cow/02_rd/00_shared/02_concepts/learned-patterns/<pattern_name>.md
（结构化知识，符合 knowledge-wiki 归档规范）
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
PATTERNS_DIR = WORKSPACE / "knowledge" / "concepts" / "learned-patterns"
INDEX_FILE = PATTERNS_DIR / "index.json"


def ensure_dir():
    PATTERNS_DIR.mkdir(parents=True, exist_ok=True)


def load_index() -> dict:
    ensure_dir()
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_index(index: dict):
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_name(name: str) -> str:
    return name.replace(" ", "-").replace("/", "-").replace(":", "-")


def cmd_save(args):
    ensure_dir()
    name = safe_name(args.name)
    p = PATTERNS_DIR / f"{name}.md"
    now = datetime.datetime.now().isoformat(timespec="seconds")
    content = f"""# 模式: {args.name}

> **来源**: {args.file or "会话分析"} | **保存**: {now}
> **标签**: {args.tag or "通用"}

## 描述

{args.desc or "（待补充）"}

## 复用场景

（待补充）

## 验证记录

- 首次保存: {now}
"""
    p.write_text(content, encoding="utf-8")
    # 更新索引
    index = load_index()
    index[name] = {"name": args.name, "file": str(p), "saved_at": now, "tag": args.tag or "通用"}
    save_index(index)
    print(f"✅ 模式已保存: {args.name} → {p}")


def cmd_list(args):
    index = load_index()
    if not index:
        print("(无已保存模式)")
        return
    for name, meta in sorted(index.items()):
        tag = meta.get("tag", "通用")
        if args.tag and tag != args.tag:
            continue
        print(f"  📌 {name} [{tag}] — {meta.get('saved_at', '')}")


def cmd_status(args):
    name = safe_name(args.name)
    p = PATTERNS_DIR / f"{name}.md"
    if not p.exists():
        print(f"❌ 模式不存在: {args.name}")
        sys.exit(1)
    content = p.read_text(encoding="utf-8")
    # 显示头部
    for line in content.split("\n")[:12]:
        print(line)


def main():
    parser = argparse.ArgumentParser(description="模式学习暂存管理器")
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="保存模式")
    p_save.add_argument("name")
    p_save.add_argument("--desc", default="")
    p_save.add_argument("--file", default="")
    p_save.add_argument("--tag", default="")
    p_save.set_defaults(func=cmd_save)

    p_list = sub.add_parser("list", help="列出模式")
    p_list.add_argument("--tag", default="")
    p_list.set_defaults(func=cmd_list)

    p_status = sub.add_parser("status", help="查看模式")
    p_status.add_argument("name")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
