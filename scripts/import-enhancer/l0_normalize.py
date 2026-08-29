#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
l0_normalize.py — L0 格式规范化脚本（零依赖，立即可用）
=========================================================
设计约束: 不修改源文件; 产物写入独立输出目录(镜像结构)。
功能(对应设计文档 §4 L0):
  1. 编码修复: GB18030/BOM → UTF-8 (文件被错误解码时)
  2. frontmatter 补全: 无 YAML frontmatter 则生成空模板
  3. 标题清洗: 去除控制字符/重复空行/行尾空白
  4. manifest.json: 文件清单(路径映射/编码状态/大小/行数) —— 供 L1/L2 调度

用法:
  python3 l0_normalize.py --input import --output import-enhanced
  python3 l0_normalize.py --input import --output import-enhanced --dry-run
  python3 l0_normalize.py --input import/server --output import-enhanced/server --limit 50
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------- 编码检测 ----------
def detect_and_decode(raw: bytes) -> tuple[str, str]:
    """返回 (解码文本, 检测到的编码)。依次尝试 UTF-8/GB18030/latin-1(兜底)。"""
    for enc in ("utf-8-sig", "gb18030"):
        try:
            return raw.decode(enc), enc
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8-replace"


# ---------- 文本清理 ----------
CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

def clean_text(text: str) -> str:
    """轻量规范化: 去控制字符/行尾空白/多余空行。不做内容改写。"""
    text = CTRL_RE.sub("", text)
    lines = [ln.rstrip() for ln in text.splitlines()]
    # 合并 3 个以上连续空行为 2 个
    out: list[str] = []
    blank = 0
    for ln in lines:
        if not ln.strip():
            blank += 1
            if blank <= 2:
                out.append("")
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip() + "\n"


FM_RE = re.compile(r"^---\s*\n.*?\n---\s*\n?", re.DOTALL)

def ensure_frontmatter(text: str, src_rel: str, mtime: str) -> str:
    """若无 frontmatter 则生成空模板(只含可从文件系统推断的信息)。"""
    if FM_RE.match(text):
        return text
    fm = (
        "---\n"
        f"title: ''\n"          # 由 L1 填充(从内容推断)
        f"source: {src_rel}\n"
        f"date: {mtime[:10]}\n"
        f"tags: []\n"           # 由 L1 填充
        "status: unprocessed\n"  # unprocessed → L1/L2 已处理 → reviewed
        "---\n\n"
    )
    return fm + text


# ---------- 主流程 ----------
TEXT_EXTS = {".md", ".markdown", ".txt"}
SRC_EXTS = TEXT_EXTS | {".cpp", ".cc", ".h", ".hpp", ".c", ".py", ".json", ".yaml", ".yml"}

def process_tree(args) -> None:
    src_root = Path(args.input).resolve()
    out_root = Path(args.output).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    exts = SRC_EXTS if args.include_src else TEXT_EXTS
    manifest: list[dict] = []
    ok = fail = skip = 0
    files = sorted(src_root.rglob("*"))
    if args.limit:
        files = files[: args.limit]

    for p in files:
        if not p.is_file():
            continue
        if p.suffix.lower() not in exts:
            skip += 1
            continue
        rel = p.relative_to(src_root)
        dst = out_root / rel
        entry = {
            "src": str(p), "dst": str(dst), "rel": str(rel),
            "size": p.stat().st_size, "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
        }
        try:
            raw = p.read_bytes()
        except OSError as e:
            entry["status"] = "error"; entry["error"] = str(e)
            manifest.append(entry); fail += 1
            continue

        text, enc = detect_and_decode(raw)
        if "\x00" in text or text.count("\x00") > 0 and p.suffix.lower() in (".png", ".jpg", ".pdf"):
            # 二进制文件跳过
            entry["status"] = "binary-skip"
            manifest.append(entry); skip += 1
            continue

        clean = clean_text(text)
        entry["encoding"] = enc
        entry["was_binary"] = bool("\x00" in text)
        if enc != "utf-8-sig" and enc != "utf-8":
            entry["encoding_fixed"] = True
        if not FM_RE.match(clean):
            entry["frontmatter_added"] = True
            clean = ensure_frontmatter(clean, str(rel), datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d"))
        entry["lines"] = len(clean.splitlines())
        entry["status"] = "ok"

        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(clean, encoding="utf-8")
        manifest.append(entry)
        ok += 1

    # manifest 落盘
    mf = {
        "generated": datetime.now().isoformat(),
        "src_root": str(src_root), "out_root": str(out_root),
        "counts": {"ok": ok, "fail": fail, "binary_skip": skip},
        "files": manifest,
    }
    mf_path = out_root / "manifest.json"
    if not args.dry_run:
        mf_path.write_text(json.dumps(mf, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[L0] 完成: ok={ok} fail={fail} binary_skip={skip}")
    print(f"[L0] manifest: {mf_path if not args.dry_run else '(dry-run 不写盘)'}")
    if fail:
        print("[L0] 警告: 有失败文件, 详见 manifest.json", file=sys.stderr)


def main() -> None:
    ap = argparse.ArgumentParser(description="L0 格式规范化: 编码修复 + frontmatter + 清洗 (不修改源文件)")
    ap.add_argument("--input", required=True, help="源目录 (如 import 或 import/server)")
    ap.add_argument("--output", required=True, help="输出目录 (镜像结构, 不覆盖源)")
    ap.add_argument("--limit", type=int, default=0, help="仅处理前 N 个文件(调试用)")
    ap.add_argument("--include-src", action="store_true", help="额外处理源码类(cpp/h/json等)")
    ap.add_argument("--dry-run", action="store_true", help="只统计不写盘")
    args = ap.parse_args()
    process_tree(args)


if __name__ == "__main__":
    main()
