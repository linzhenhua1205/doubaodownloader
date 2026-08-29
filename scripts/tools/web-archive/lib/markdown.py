#!/usr/bin/env python3
"""Markdown 生成器 — 图片 web 链接化 + 结构化骨架 + 批判分析章节"""
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from lib.extractor import ExtractedArticle


def slugify_title(title: str, max_len: int = 60) -> str:
    """标题 → 英文 slug (kebab-case)。

    策略(优先序):
      1. 提取标题中的英文/数字词 (KVCache/LLM/305GB) 作为主干
      2. 中文词优先查技术关键词映射表 → 英文 (架构→architecture)
      3. 未覆盖中文 → pypinyin 拼音; 全部英文标题 → 直接 kebab
    """
    t = title.strip()

    # 技术关键词中英映射 (覆盖高频技术词, 保证英文描述质量)
    CN_TERM_MAP = {
        "架构": "architecture", "演进": "evolution", "全景": "panorama",
        "分析": "analysis", "深度": "deep", "技术": "tech", "大模型": "llm",
        "模型": "model", "缓存": "cache", "存储": "storage", "网络": "network",
        "服务器": "server", "算力": "compute", "推理": "inference",
        "训练": "training", "市场": "market", "报告": "report", "指南": "guide",
        "优化": "optimization", "压缩": "compression", "量化": "quantization",
        "安全": "security", "系统": "system", "平台": "platform", "框架": "framework",
        "研究": "research", "实践": "practice", "落地": "landing", "应用": "application",
        "国产化": "domestic-substitution", "芯片": "chip", "互联": "interconnect",
        "液冷": "liquid-cooling", "供电": "power", "内存": "memory", "数据库": "database",
        "对比": "comparison", "方案": "solution", "设计": "design", "原理": "principle",
        "跑通": "running", "落地全景": "landing-panorama", "全景落地": "landing-panorama",
        "企业": "enterprise", "液冷": "liquid-cooling", "数据中心": "datacenter",
        "智能": "intelligent", "时代": "era", "趋势": "trend", "洞察": "insight",
        "解读": "interpretation", "盘点": "review", "总结": "summary", "展望": "outlook",
        "挑战": "challenge", "机遇": "opportunity", "生态": "ecosystem", "标准": "standard",
    }

    # 1. 英文/数字词: 保留字母词(KVCache/LLM); 数字带单位保留(305GB); 纯数字丢弃
    eng_parts = []
    for w in re.findall(r"[A-Za-z][A-Za-z0-9]*|\d+(?:\.\d+)?[A-Za-z]+", t):
        wl = w.lower()
        if wl in ("gb", "tb", "mb", "kb", "g", "t", "m"):  # 单位词丢弃(由数字组合保留)
            continue
        if re.match(r"^\d", wl) and not re.search(r"[a-z]", wl):
            continue
        if len(wl) >= 2:
            eng_parts.append(wl)

    # 2. 中文词 → 英文映射 / 拼音 (消耗式匹配: 命中后移除原文, 避免子词重复)
    CN_STOPWORDS = {"从", "到", "的", "之", "与", "和", "及", "在", "于",
                    "为", "以", "是", "了", "就", "也", "更", "仅", "入", "局"}
    cn_parts = []
    for seg in re.findall(r"[\u4e00-\u9fff]+", t):
        seg_clean = "".join(ch for ch in seg if ch not in CN_STOPWORDS)
        if not seg_clean:
            continue
        # 消耗式匹配: 按 key 长度降序, 命中即移除原文 (防 大模型→llm+model 重复)
        remaining = seg_clean
        hit_any = False
        for cn, en in sorted(CN_TERM_MAP.items(), key=lambda kv: -len(kv[0])):
            if cn in remaining:
                cn_parts.append(en)
                remaining = remaining.replace(cn, "", 1)
                hit_any = True
        if hit_any:
            continue
        try:
            from pypinyin import lazy_pinyin
            py = "".join(lazy_pinyin(seg_clean))
            if len(py) >= 4:
                cn_parts.append(py[:24])  # 拼音段截断
        except ImportError:
            pass

    # 3. 组合: 英文技术词优先打头 (KVCache 而非 305), 去重保序
    parts = []
    seen = set()
    for p in eng_parts + cn_parts:
        if p and p not in seen:
            parts.append(p)
            seen.add(p)
    # 若纯数字单位词打头, 将首个字母词提到前面 (如 305gb-kvcache → kvcache-305gb)
    if parts and re.match(r"^\d", parts[0]):
        for i, p in enumerate(parts):
            if re.match(r"^[a-z]", p):
                parts.insert(0, parts.pop(i))
                break

    slug = "-".join(parts)
    slug = re.sub(r"[^a-z0-9-]", "-", slug.lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    if not slug:
        slug = "web-archive"
    return slug


def render_markdown(article: ExtractedArticle, url: str, out_path: Path = None) -> str:
    """渲染归档 Markdown (含批判分析章节占位)。"""
    today = datetime.now().strftime("%Y-%m-%d")
    site = urlparse(url).netloc.replace("www.", "")

    lines = []
    lines.append(f"# {article.title}")
    lines.append("")
    lines.append(f"> **Source**: <{url}>")
    lines.append(f"> **Site**: {site} | **Archived**: {today}"
                 f"{' | **Author**: ' + article.author if article.author else ''}"
                 f"{' | **Published**: ' + article.published if article.published else ''}")
    lines.append(f"> **Adapter**: {article.adapter_name}")
    lines.append("")
    if article.description:
        lines.append("## 内容摘要")
        lines.append("")
        lines.append(article.description[:300])
        lines.append("")
    lines.append("---")
    lines.append("")

    # 核心内容
    lines.append("## 原文核心内容")
    lines.append("")
    lines.append(article.text.strip() if article.text else "(正文提取失败)")
    lines.append("")

    # 图片 (web 链接方式, 不下载)
    if article.images:
        lines.append("## 图片（web 链接）")
        lines.append("")
        for i, img in enumerate(article.images, 1):
            alt = img["alt"] or f"图{i}"
            lines.append(f"![{alt}]({img['src']})")
            if img["alt"]:
                lines.append(f"*{img['alt']}*")
        lines.append("")

    # 批判辩证分析 (由 enhance_analysis 填充; 此处给占位)
    lines.append("## 批判辩证分析")
    lines.append("")
    if getattr(article, "analysis", None):
        lines.append(article.analysis)
    else:
        lines.append("> ⚠️ 未执行批判分析 (使用 --no-analyze 或增强失败)")
    lines.append("")

    # 底层原理补充
    lines.append("## 底层原理补充")
    lines.append("")
    if getattr(article, "principles", None):
        lines.append(article.principles)
    else:
        lines.append("> ⚠️ 未补充底层原理")
    lines.append("")

    # 市场机会
    lines.append("## 市场机会")
    lines.append("")
    if getattr(article, "opportunities", None):
        lines.append(article.opportunities)
    else:
        lines.append("> ⚠️ 未补充市场机会")
    lines.append("")

    # 原文链接
    lines.append("## 原文链接")
    lines.append("")
    lines.append(f"- 原始文章: <{url}>")
    for i, l in enumerate(article.links[:20], 1):
        if l.startswith(("http", "/")):
            lines.append(f"- 相关链接 {i}: <{l}>")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"> 📥 Archived by web-archive v2.0 | {today} | 站点适配器: {article.adapter_name}")
    lines.append("")

    return "\n".join(lines)
