#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# compress-skill-descriptions.py v1 — SKILL.md description 批量压缩器
#
# 用途：压缩 skills/*/SKILL.md frontmatter 的 description 字段，
#       减少系统提示词/读取时的 token 消耗。与 CowAgent formatter
#       的 _condense_description_for_prompt 同源策略：
#       「核心动作 + 触发关键词」，保留匹配信号、删冗余表述。
#
# 处理对象：
#   - 一级 skills：skills/*/SKILL.md（不含 lowfreq/）
#   - 二级 skills：skills/lowfreq/*/SKILL.md
#   仅压缩长度 > MAX_CHARS 的 description；保留原有格式（单行/双引号）。
#
# 用法：
#   python3 scripts/compress-skill-descriptions.py            # 压缩超长
#   python3 scripts/compress-skill-descriptions.py --dry-run  # 仅预览不写
#   python3 scripts/compress-skill-descriptions.py --max 150  # 阈值
#
# 输出：
#   - 压缩前后统计（chars/tokens 节省）
#   - 变更文件清单（写入 tmp/compress-skill-desc-report-{date}.md）
#
# 变更日志：
#   2026-08-14 v1 created
#================================================================

import argparse
import os
import re
import sys
from datetime import datetime

WORKSPACE = os.path.expanduser("~/cow")
SKILLS_DIR = os.path.join(WORKSPACE, "skills")

# ─────────────────────────────────────────────
# 与 CowAgent formatter 同源的压缩逻辑
# ─────────────────────────────────────────────
def condense_description(desc: str, max_chars: int = 180) -> str:
    """压缩 description：核心动作 + 触发关键词（保留信号、删冗余）"""
    text = desc.replace("\n", " ").strip()
    if len(text) <= max_chars:
        return text

    # ── 提取触发关键词 ──────────────────────────────
    trigger_keywords = []
    # 引导语/无信息量词（不作为触发关键词）
    TRIGGER_STOPWORDS = {
        "the user asks to", "user asks to", "asks to", "the user", "when",
        "include", "includes", "including", "such as", "also use when",
        "or", "and", "use when", "if", "for example", "e.g.", "etc",
        "triggers include", "trigger", "triggers", "when the user",
    }
    # Use when / Triggers / 触发词 引导的触发列表（冒号或空格分隔均可）
    for pattern in (
        re.compile(r"(?:Use when|USE WHEN|Triggers?|Trig|When)[:：]?\s+(.*?)$", re.DOTALL),
        re.compile(r"(?:触发词|触发场景|触发)[：:]\s*(.*?)$", re.DOTALL),
        re.compile(r"(?:当用户|当.*?时)(.*?)$", re.DOTALL),
    ):
        match = pattern.search(text)
        if match:
            raw = match.group(1).strip()
            # 按逗号/分号/括号编号/顿号分割
            parts = re.split(
                r"(?:[,;，；、]|(?:\s*[•\-]\s*)|\s+(?=[\(\[\]?\d+[\)\.]))\s*",
                raw,
            )
            for p in parts:
                p = p.strip()
                if not p or len(p) < 3:
                    continue
                # 去掉开头编号 (1) 1. 1) ①
                p = re.sub(r"^\d+\s*[\)\.]\s*", "", p).strip()
                p = re.sub(r"^\(\d+\)\s*", "", p).strip()
                p = re.sub(r"^\[\d+\]\s*", "", p).strip()
                p = re.sub(r"^[①-⑩]\s*", "", p).strip()
                if not p or len(p) < 3:
                    continue
                # 去掉结尾编号残留
                p = re.sub(r"\s*\d+[\)\.]?\s*$", "", p).strip()
                p = re.sub(r"\s*[\(\[][\d\w]+[\)\]]\s*$", "", p).strip()
                p = p.rstrip(".。,:：;；")
                p = p[:36].strip()
                pl = p.lower()
                if (p and p not in trigger_keywords
                        and pl not in TRIGGER_STOPWORDS
                        and not any(w in pl for w in ("asks to", "include"))):
                    trigger_keywords.append(p)
                if len(trigger_keywords) >= 6:
                    break
            if trigger_keywords:
                break

    # 无 "Use when" 结构 → 触发词模式兜底
    if not trigger_keywords:
        match = re.search(r"当用户(.*?)时", text)
        if match:
            kw_text = match.group(1).strip()
            parts = re.split(r"[,;，；、](?:\s*(?:\d+[\)\.])\s*)?", kw_text)
            for p in parts:
                p = p.strip()
                if not p or len(p) < 3:
                    continue
                p = p[:32].strip()
                if p and p not in trigger_keywords:
                    trigger_keywords.append(p)
                if len(trigger_keywords) >= 6:
                    break

    # ── 提取核心动作句 ──────────────────────────────
    core = text
    for pat in (r"\s+Use when", r"\s+USE WHEN", r"\s+Triggers?",
                r"\s+触发词", r"\s+触发场景", r"\s+当用户"):
        m = re.search(pat, text)
        if m:
            core = text[: m.start()].strip()
            break
    if len(core) > 90:
        sents = re.split(r"(?<=[。！？.!?])\s+(?=[A-Z\u4e00-\u9fff])", core)
        if len(sents) > 1 and len(sents[0]) <= 90:
            core = sents[0]
    if len(core) > 90:
        core = core[:87] + "..."

    # ── 组装 ─────────────────────────────────────────
    result = core
    if trigger_keywords:
        result += " | " + ", ".join(trigger_keywords)
    if len(result) > max_chars:
        result = result[: max_chars - 3] + "..."
    return result


# ─────────────────────────────────────────────
# frontmatter 解析/写入
# ─────────────────────────────────────────────
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef]")

def est_tokens(text: str) -> int:
    cjk = len(CJK_RE.findall(text))
    return int(round(cjk * 0.7 + (len(text) - cjk) / 4.0))

def extract_desc(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            head = f.read(5000)
    except Exception:
        return ""
    # 块标量保护：description: | 或 > 开头（多行 YAML）→ 不按单行处理，返回空（跳过压缩）
    if re.search(r'^description:\s*[|>][-+]?\s*$', head, re.M):
        return ""
    m = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', head, re.M)
    if m:
        return m.group(1)
    m2 = re.search(r"^description:\s*(.+)$", head, re.M)
    return m2.group(1) if m2 else ""

def replace_desc_in_frontmatter(path: str, new_desc: str) -> bool:
    """在 frontmatter 中替换 description 字段值，保留引号风格。"""
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False

    # 定位 frontmatter 中的 description 行
    m = re.search(r"^description:\s*(.*)$", content, re.M)
    if not m:
        return False

    old_val = m.group(1)
    # 判断原引号风格
    if old_val.startswith('"') and old_val.endswith('"'):
        # 多行双引号（YAML block scalar）→ 转单行双引号
        new_line = f'description: "{new_desc}"'
    elif old_val.startswith("'") and old_val.endswith("'"):
        new_line = f"description: '{new_desc}'"
    else:
        # 无引号单行：若含特殊字符则加双引号
        if ":" in new_desc or "," in new_desc or "#" in new_desc:
            new_line = f'description: "{new_desc}"'
        else:
            new_line = f"description: {new_desc}"

    content = content[: m.start()] + new_line + content[m.end():]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def collect_skill_files():
    """收集所有 SKILL.md（一级 + lowfreq 二级）"""
    files = []
    for root, _, names in os.walk(SKILLS_DIR):
        if "SKILL.md" in names:
            files.append(os.path.join(root, "SKILL.md"))
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description="SKILL.md description 批量压缩")
    ap.add_argument("--dry-run", action="store_true", help="仅预览不写入")
    ap.add_argument("--max", type=int, default=180, help="超过该 chars 才压缩（默认 180）")
    args = ap.parse_args()

    files = collect_skill_files()
    changed = []
    total_before = total_after = 0
    total_before_tok = total_after_tok = 0

    for path in files:
        desc = extract_desc(path)
        if not desc:
            continue
        total_before += len(desc)
        total_before_tok += est_tokens(desc)
        if len(desc) <= args.max:
            total_after += len(desc)
            total_after_tok += est_tokens(desc)
            continue
        new_desc = condense_description(desc, max_chars=args.max)
        changed.append((path, len(desc), len(new_desc), desc, new_desc))
        total_after += len(new_desc)
        total_after_tok += est_tokens(new_desc)

    print(f"共扫描 {len(files)} 个 SKILL.md")
    print(f"需压缩: {len(changed)} 个（> {args.max} chars）")
    print(f"压缩前: {total_before:,} chars / ~{total_before_tok:,} tokens")
    print(f"压缩后: {total_after:,} chars / ~{total_after_tok:,} tokens")
    print(f"节省: {total_before - total_after:,} chars / ~{total_before_tok - total_after_tok:,} tokens "
          f"({100*(total_before_tok-total_after_tok)//max(1,total_before_tok)}%)")
    print("")

    # 预览前 8 个变更
    for path, bl, al, old, new in changed[:8]:
        rel = os.path.relpath(path, WORKSPACE)
        print(f"── {rel}")
        print(f"  {bl}→{al} chars | {est_tokens(old)}→{est_tokens(new)} tokens")
        print(f"  旧: {old[:120]}...")
        print(f"  新: {new[:120]}")
        print("")

    if args.dry_run:
        print("[dry-run] 未写入")
        return

    # 写入
    ok = 0
    for path, bl, al, old, new in changed:
        if replace_desc_in_frontmatter(path, new):
            ok += 1
    print(f"✅ 已写入 {ok}/{len(changed)} 个文件")

    # 变更报告
    report_dir = os.path.join(WORKSPACE, "tmp")
    os.makedirs(report_dir, exist_ok=True)
    report = os.path.join(report_dir, f"compress-skill-desc-report-{datetime.now():%Y-%m-%d}.md")
    with open(report, "w", encoding="utf-8") as f:
        f.write(f"# SKILL.md description 压缩报告（{datetime.now():%Y-%m-%d}）\n\n")
        f.write(f"- 扫描: {len(files)} 个 SKILL.md\n")
        f.write(f"- 压缩: {len(changed)} 个（阈值 >{args.max} chars）\n")
        f.write(f"- 节省: {total_before - total_after:,} chars / ~{total_before_tok - total_after_tok:,} tokens\n\n")
        f.write("| 文件 | 压缩前(ch) | 压缩后(ch) | 节省(tok) |\n")
        f.write("|:-----|:----------:|:----------:|:---------:|\n")
        for path, bl, al, old, new in changed:
            rel = os.path.relpath(path, WORKSPACE)
            f.write(f"| {rel} | {bl} | {al} | {est_tokens(old)-est_tokens(new)} |\n")
    print(f"📄 报告: {report}")


if __name__ == "__main__":
    main()
