#!/usr/bin/env python3
"""
token-estimator.py — Token 预估算工具 (sr-006 X-08)

执行前估算 token 消耗，超阈值预警。支持多种估算模型。

用法:
  # 作为模块引用
  from scripts.tools.token_estimator import estimate, human_readable

  # 估算文本
  tokens = estimate("这是一段中文文本，包含了一些技术术语如HBM4、NVLink6")
  print(f"预估: {tokens} tokens")

  # 估算文件
  tokens = estimate_file("knowledge/README.md")

  # 估算所有文件
  totals = estimate_files(["file1.md", "file2.md", "file3.md"])

  # 检查阈值
  if check_threshold(tokens, warn_at=4000, error_at=8000):
      print("Token 预算安全")
  else:
      print("⚠️  Token 超限")

  # CLI 模式
  python3 scripts/tools/token-estimator.py text "要估算的文本"
  python3 scripts/tools/token-estimator.py file <path> [--warn 4000] [--error 8000]
  python3 scripts/tools/token-estimator.py batch <path>... [--summary]
  python3 scripts/tools/token-estimator.py context <path>... [--include-skills]
  python3 scripts/tools/token-estimator.py dir <dir-path> [--ext .md]
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ── 估算常量 ──
# 基于常见 LLM Tokenizer 的估算
# 中文: 约 1.5-1.8 chars/token | 英文: 约 4 chars/token
# 代码/数字: 约 3 chars/token | Markdown 标点: 约 2 chars/token
CHARS_PER_TOKEN_CN = 1.6     # 中文字符
CHARS_PER_TOKEN_EN = 4.0     # 英文字符
CHARS_PER_TOKEN_CODE = 3.0   # 代码/数字
CHARS_PER_TOKEN_PUNCT = 2.0  # 标点/空格

# ── 默认阈值 ──
DEFAULT_WARN_THRESHOLD = 4000    # 警告阈值 (≈ GPT-3.5 context 的 10%)
DEFAULT_ERROR_THRESHOLD = 8000   # 错误阈值 (≈ GPT-3.5 context 的 20%)

# ── 上下文模板开销 (估算) ──
CONTEXT_OVERHEAD = {
    "system_prompt": 1500,    # 系统提示词
    "tools": 2000,            # 工具定义
    "per_skill_md": 800,      # 每个 SKILL.md
    "per_file_ref": 50,       # 每个文件引用
}


def _classify_char(c: str) -> str:
    """分类字符类型"""
    if '\u4e00' <= c <= '\u9fff' or '\u3000' <= c <= '\u303f':
        return 'cn'
    if c.isalpha():
        return 'en'
    if c.isdigit() or c in '+-*/=<>{}[]()&|!~^%':
        return 'code'
    return 'punct'


def estimate(text: str, model: str = "default") -> int:
    """
    估算文本的 token 消耗。

    参数:
        text:  要估算的文本
        model: 估算模型 ("default" / "conservative" / "aggressive")

    返回: 预估 token 数
    """
    if not text:
        return 0

    total_chars = len(text)

    # 按字符类型分组估算
    cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    en_chars = sum(1 for c in text if c.isalpha() and not ('\u4e00' <= c <= '\u9fff'))
    digit_chars = sum(1 for c in text if c.isdigit())
    space_chars = sum(1 for c in text if c.isspace())
    punct_chars = total_chars - cn_chars - en_chars - digit_chars - space_chars

    # 加权估算
    tokens = (
        cn_chars / CHARS_PER_TOKEN_CN +
        en_chars / CHARS_PER_TOKEN_EN +
        (digit_chars + space_chars) / CHARS_PER_TOKEN_CODE +
        punct_chars / CHARS_PER_TOKEN_PUNCT
    )

    # 特殊标记调整
    # Markdown 链接: [[link]] 或 [text](url) — 额外开销
    link_count = len(re.findall(r'\[\[.*?\]\]|\[.*?\]\(.*?\)', text))
    tokens += link_count * 0.5

    # 代码块: ``` 内的内容更密集
    code_block_count = text.count('```') // 2
    tokens += code_block_count * 20  # 代码块边界开销

    # 模型系数
    factors = {
        "default": 1.0,
        "conservative": 1.2,  # 保险估算
        "aggressive": 0.85,   # 乐观估算
    }
    factor = factors.get(model, 1.0)

    return max(1, int(tokens * factor))


def estimate_file(path: str, model: str = "default") -> Optional[int]:
    """
    估算文件的 token 消耗。

    返回: 预估 token 数，失败返回 None
    """
    p = Path(path)
    if not p.is_absolute():
        p = REPO_ROOT / p
    try:
        with open(p, 'r', encoding='utf-8') as f:
            content = f.read()
        return estimate(content, model)
    except (OSError, UnicodeDecodeError) as e:
        print(f"⚠️  无法读取 {path}: {e}", file=sys.stderr)
        return None


def estimate_files(paths: List[str], model: str = "default") -> Dict[str, Optional[int]]:
    """批量估算多个文件"""
    results = {}
    for path in paths:
        results[path] = estimate_file(path, model)
    return results


def check_threshold(tokens: int, warn_at: int = DEFAULT_WARN_THRESHOLD,
                    error_at: int = DEFAULT_ERROR_THRESHOLD) -> Tuple[bool, str]:
    """
    检查 token 是否超阈值。

    返回: (是否通过, 状态描述)
    """
    if tokens >= error_at:
        return False, f"❌ 超出错误阈值 ({tokens} >= {error_at})"
    if tokens >= warn_at:
        return False, f"⚠️  超出警告阈值 ({tokens} >= {warn_at})"
    return True, f"✅ 安全 ({tokens} < {warn_at})"


def estimate_context(paths: List[str], include_skills: bool = False,
                     skill_count: int = 0) -> dict:
    """
    估算完整上下文开销。

    包括: system_prompt + tools + 文件内容 + SKILL.md

    返回详细的 Token 预算表。
    """
    details = {}

    # 系统固定开销
    details["系统提示词"] = CONTEXT_OVERHEAD["system_prompt"]
    details["工具定义"] = CONTEXT_OVERHEAD["tools"]

    # SKILL.md 开销
    if include_skills and skill_count > 0:
        skill_cost = skill_count * CONTEXT_OVERHEAD["per_skill_md"]
        details[f"Skills ({skill_count} 个)"] = skill_cost

    # 文件内容开销
    file_tokens = 0
    for path in paths:
        t = estimate_file(path)
        if t is not None:
            file_tokens += t
            details[f"📄 {Path(path).name}"] = t
        else:
            details[f"📄 {Path(path).name}"] = 0

    details["📊 文件合计"] = file_tokens

    total = sum(details.values())
    details["📊 总计"] = total

    return details


def human_readable(token_count: int) -> str:
    """将 token 数转为人类可读格式"""
    if token_count < 1000:
        return f"{token_count} tokens"
    if token_count < 1000000:
        return f"{token_count / 1000:.1f}K tokens"
    return f"{token_count / 1000000:.1f}M tokens"


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Token 预估算工具 (sr-006 X-08)",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    p_text = subparsers.add_parser("text", help="估算文本")
    p_text.add_argument("text", help="要估算的文本")
    p_text.add_argument("--model", default="default",
                        choices=["default", "conservative", "aggressive"])

    p_file = subparsers.add_parser("file", help="估算文件")
    p_file.add_argument("path", help="文件路径")
    p_file.add_argument("--model", default="default")
    p_file.add_argument("--warn", type=int, default=DEFAULT_WARN_THRESHOLD)
    p_file.add_argument("--error", type=int, default=DEFAULT_ERROR_THRESHOLD)

    p_batch = subparsers.add_parser("batch", help="批量估算")
    p_batch.add_argument("paths", nargs="+", help="文件路径")
    p_batch.add_argument("--summary", action="store_true", help="仅显示汇总")
    p_batch.add_argument("--model", default="default")

    p_context = subparsers.add_parser("context", help="估算上下文")
    p_context.add_argument("paths", nargs="+", help="文件路径")
    p_context.add_argument("--include-skills", action="store_true", help="包含 Skills 开销")
    p_context.add_argument("--skill-count", type=int, default=0, help="SKILL.md 数量")

    p_dir = subparsers.add_parser("dir", help="估算目录")
    p_dir.add_argument("dir", help="目录路径")
    p_dir.add_argument("--ext", default=".md", help="文件扩展名")
    p_dir.add_argument("--model", default="default")

    args = parser.parse_args()

    if args.command == "text":
        tokens = estimate(args.text, args.model)
        print(f"📊 Token 估算 ({args.model}):")
        print(f"  文本长度: {len(args.text)} 字符")
        print(f"  预估:     {human_readable(tokens)}")
        ok, msg = check_threshold(tokens)
        print(f"  状态:     {msg}")

    elif args.command == "file":
        tokens = estimate_file(args.path, args.model)
        if tokens is None:
            sys.exit(1)
        print(f"📊 文件 Token 估算: {args.path}")
        print(f"  预估: {human_readable(tokens)}")
        ok, msg = check_threshold(tokens, args.warn, args.error)
        print(f"  状态: {msg}")

    elif args.command == "batch":
        results = estimate_files(args.paths, args.model)
        total = 0
        print(f"📊 批量 Token 估算 ({len(args.paths)} 个文件):")
        print("─" * 50)
        for path, tokens in results.items():
            if tokens is not None:
                total += tokens
                if not args.summary:
                    print(f"  {human_readable(tokens):>10s}  {path}")
            else:
                print(f"      ❌  {path}")
        print("─" * 50)
        print(f"  {human_readable(total):>10s}  合计")

    elif args.command == "context":
        details = estimate_context(
            args.paths,
            include_skills=args.include_skills,
            skill_count=args.skill_count,
        )
        total = details.get("📊 总计", 0)
        print(f"📊 上下文 Token 预算:")
        print("─" * 50)
        for label, tokens in details.items():
            bar = "█" * max(1, tokens // 500)
            print(f"  {human_readable(tokens):>10s}  {bar}  {label}")
        print("─" * 50)
        print(f"  总计: {human_readable(total)}")

    elif args.command == "dir":
        d = Path(args.dir)
        if not d.is_absolute():
            d = REPO_ROOT / d
        if not d.exists():
            print(f"❌ 目录不存在: {d}", file=sys.stderr)
            sys.exit(1)

        files = sorted(d.rglob(f"*{args.ext}"))
        paths = [str(f) for f in files]
        results = estimate_files(paths, args.model)
        total = 0
        large_files = []

        print(f"📊 目录 Token 估算: {d}")
        print(f"  文件数: {len(files)}")
        print("─" * 50)
        for path, tokens in results.items():
            if tokens is not None:
                total += tokens
                if tokens > DEFAULT_WARN_THRESHOLD:
                    large_files.append((path, tokens))
        print(f"  合计: {human_readable(total)}")

        if large_files:
            print(f"\n⚠️  大文件 (> {human_readable(DEFAULT_WARN_THRESHOLD)}):")
            for path, tokens in sorted(large_files, key=lambda x: -x[1])[:10]:
                rel = Path(path).relative_to(d)
                print(f"  {human_readable(tokens):>10s}  {rel}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
