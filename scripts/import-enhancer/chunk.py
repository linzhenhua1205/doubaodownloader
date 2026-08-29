#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chunk.py — 分片器（核心组件，零依赖纯标准库）
==================================================
设计约束: 本地 LLM 上下文上限 32K，单请求 payload 必须 ≤16K tokens。
规则（对应设计文档 §6）:
  - 触发阈值: 文件 >10K tokens(≈20KB 中文)才分片
  - 分片大小: 目标 8-12K tokens/片
  - 分片锚点: 章节标题(#/##/###) > 空行 > 段落边界; 禁止切断句子
  - 片间一致性: 每片带文档上下文头(标题+大纲 1-2K)
  - 重叠: 相邻片重叠 overlap_tokens(默认 200)
  - 小文件(≤5KB): 整文件处理, 不分片

用法:
  from chunk import chunk_file, estimate_tokens
  chunks = chunk_file("path/to/doc.md", max_tokens=12000)
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

# ---------- token 估算 ----------
# 中文 1 字 ≈ 1.5 token; 英文 1 词 ≈ 1.3 token; 混合保守 ~500 tok/KB
# 用字节数估算: UTF-8 下 1 字节 ≈ 0.5 token（中文 3 字节/字 → 1.5 tok/字）
def estimate_tokens(text: str) -> int:
    """粗略估算 token 数（±20% 精度足够用于分片决策）"""
    return max(1, len(text.encode("utf-8")) // 2)


# ---------- 数据结构 ----------
@dataclass
class Chunk:
    index: int                # 片序号(0-based)
    content: str              # 片内容(不含上下文头)
    doc_context_head: str = ""  # 文档上下文头(标题+大纲摘要)
    start_char: int = 0       # 在原文中的起始字符偏移
    end_char: int = 0         # 在原文中的结束字符偏移

    @property
    def payload(self) -> str:
        """最终送入 LLM 的 payload = 上下文头 + 分隔 + 正文"""
        if self.doc_context_head:
            return f"{self.doc_context_head}\n\n---\n\n{self.content}"
        return self.content

    @property
    def tokens(self) -> int:
        return estimate_tokens(self.payload)


# ---------- 文档上下文头 ----------
HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")

def build_doc_context_head(doc_text: str, max_head_tokens: int = 1500) -> str:
    """
    构建文档上下文头: 标题 + 大纲(前若干章节标题) + 全文摘要统计。
    作用: 分片后每片仍知道"这是哪篇文档的哪部分"(片间一致性)。
    """
    lines = doc_text.splitlines()
    title = ""
    outline: List[str] = []
    total = 0
    for ln in lines:
        m = HEADING_RE.match(ln.strip())
        if m:
            level, text = m.group(1), m.group(2)
            if not title:
                title = text
            outline.append(f"{'  ' * (len(level) - 1)}- {text}")
        total += 1
    # 控制大纲长度
    budget = max_head_tokens
    head_lines = [f"# 文档: {title or '<无标题>'}", f"# 总行数: {total} | 章节: {len(outline)}"]
    for o in outline:
        if estimate_tokens("\n".join(head_lines + [o])) > budget:
            head_lines.append(f"... 共 {len(outline)} 个章节")
            break
        head_lines.append(o)
    return "\n".join(head_lines)


# ---------- 锚点切分 ----------
def _split_at_anchors(text: str) -> List[str]:
    """
    按锚点优先级切分: 章节标题 > 空行 > 段落边界。
    返回候选块列表(每块一行或多行, 以换行结尾)。
    """
    lines = text.splitlines(keepends=True)
    blocks: List[str] = []
    cur: List[str] = []
    for ln in lines:
        cur.append(ln)
        stripped = ln.strip()
        # 章节标题或空行作为切分点
        if HEADING_RE.match(stripped) or not stripped:
            blocks.append("".join(cur))
            cur = []
    if cur:
        blocks.append("".join(cur))
    return blocks


def _merge_blocks(blocks: List[str], max_chars: int) -> List[str]:
    """贪心合并候选块到目标大小（不切断句子，只在块边界切）"""
    merged: List[str] = []
    cur = ""
    for b in blocks:
        if cur and len(cur) + len(b) > max_chars:
            merged.append(cur)
            cur = b
        else:
            cur += b
    if cur:
        # 尾部小块(< 1/2 目标)并入前块, 避免碎片片
        if merged and len(cur) < max_chars // 2:
            merged[-1] += cur
        else:
            merged.append(cur)
    return merged


# ---------- 主入口 ----------
def chunk_file(
    filepath: str,
    max_tokens: int = 12000,
    overlap_tokens: int = 200,
    doc_context: bool = True,
) -> List[Chunk]:
    """
    将文件切分为 Chunk 列表。

    参数:
      filepath:       输入文件路径
      max_tokens:     每片目标 token 上限(默认 12000, 留输出空间)
      overlap_tokens: 相邻片重叠 token 数(防边界信息丢失)
      doc_context:    是否附加文档上下文头

    返回:
      List[Chunk] —— 单文件(≤10K tokens)时返回单块且无上下文头
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    total_tok = estimate_tokens(text)
    if total_tok <= max_tokens:
        # 小文件: 整文件处理, 不分片
        return [Chunk(index=0, content=text, end_char=len(text))]

    max_chars = max(4000, int(len(text) * max_tokens // total_tok * 0.85))
    overlap_chars = max(50, len(text) * overlap_tokens // total_tok)

    blocks = _split_at_anchors(text)
    merged = _merge_blocks(blocks, max_chars)

    head = build_doc_context_head(text) if doc_context else ""

    chunks: List[Chunk] = []
    pos = 0
    for i, m in enumerate(merged):
        start = pos
        end = pos + len(m)
        content = m
        # 重叠: 非首块在头部并入上一块尾部 overlap_chars 字符
        if i > 0 and overlap_chars > 0:
            prev = merged[i - 1]
            tail = prev[-overlap_chars:]
            content = tail + content
        chunks.append(Chunk(
            index=i, content=content, doc_context_head=head,
            start_char=start, end_char=end,
        ))
        pos = end
    return chunks


def chunk_text(
    text: str,
    max_tokens: int = 12000,
    overlap_tokens: int = 200,
    doc_context: bool = True,
) -> List[Chunk]:
    """对内存文本直接分片（供 enhancer.py 复用）"""
    total_tok = estimate_tokens(text)
    if total_tok <= max_tokens:
        return [Chunk(index=0, content=text, end_char=len(text))]

    max_chars = max(4000, int(len(text) * max_tokens // total_tok * 0.85))
    overlap_chars = max(50, len(text) * overlap_tokens // total_tok)
    blocks = _split_at_anchors(text)
    merged = _merge_blocks(blocks, max_chars)
    head = build_doc_context_head(text) if doc_context else ""

    chunks: List[Chunk] = []
    pos = 0
    for i, m in enumerate(merged):
        start = pos
        end = pos + len(m)
        content = m
        if i > 0 and overlap_chars > 0:
            content = merged[i - 1][-overlap_chars:] + content
        chunks.append(Chunk(index=i, content=content, doc_context_head=head,
                            start_char=start, end_char=end))
        pos = end
    return chunks


# ---------- 自测 ----------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    max_tok = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
    chunks = chunk_file(path, max_tokens=max_tok)
    print(f"文件: {path} | 总 tokens(估): {estimate_tokens(open(path, encoding='utf-8', errors='replace').read())}")
    print(f"分片数: {len(chunks)}")
    for c in chunks:
        print(f"  [片{c.index}] tokens={c.tokens} 起止=({c.start_char},{c.end_char}) 上下文头={'有' if c.doc_context_head else '无'}")
        if c.content[:60].strip():
            print(f"      开头: {c.content[:60].strip()!r}")
