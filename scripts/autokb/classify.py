"""
内容分类模块

职责: 根据文件内容+元数据，确定 target_knowledge_dir、生成 slug 文件名。
支持: 规则匹配（关键词权重）+ AI辅助（预留接口）。
"""

import re
import hashlib
from pathlib import Path
from typing import Optional
from .config import CLASSIFICATION_RULES, KNOWLEDGE_DIR, MAX_FILENAME_LEN, SLUG_SEPARATOR
from .discover import SourceFile, parse_content, extract_title, extract_date


# ============================================================
# 核心分类函数
# ============================================================


def classify(sf: SourceFile) -> str:
    """
    确定目标 knowledge 子目录。

    策略:
    1. 遍历 CLASSIFICATION_RULES，按权重从高到低匹配关键词
    2. 如果内容为空，先尝试从文件名匹配
    3. 如果都匹配不上，返回 "notes/imported" 兜底
    """
    if not sf.content:
        sf = parse_content(sf)

    # 优先匹配文件名
    name_score = _match_filename(sf)
    if name_score:
        return name_score

    # 匹配内容
    content_score = _match_content(sf.content)
    if content_score:
        return content_score

    # 兜底
    if sf.source_type == "doubao" or sf.source_type == "doubao20260523":
        return "notes/imported-doubao"
    elif sf.source_type == "fetched_markdown":
        return "notes/imported-web"
    else:
        return "notes/imported"


def generate_slug(sf: SourceFile) -> str:
    """
    生成知识库文件名。

    格式: YYYY-MM-DD-short-slug.md
    规则: 取标题前30个有效字符 → 拼音/英文/数字 slug
    """
    title = extract_title(sf.content, sf.title) if sf.content else sf.title
    date = extract_date(sf.content, sf.path.name) or "unknown-date"

    # 清洗标题 → slug
    slug = _to_slug(title)

    # 取前 max len
    max_title_len = MAX_FILENAME_LEN - len(date) - len(".md") - 3  # 3 for --
    slug = slug[:max_title_len].rstrip(SLUG_SEPARATOR)

    # 处理重复: 哈希后4位
    if sf.fingerprint:
        short_hash = sf.fingerprint[:6]
        return f"{date}-{slug}-{short_hash}.md"
    return f"{date}-{slug}.md"


def generate_frontmatter(sf: SourceFile, target_dir: str) -> str:
    """生成知识页的 YAML frontmatter"""
    title = extract_title(sf.content, sf.title) if sf.content else sf.title
    date = extract_date(sf.content, sf.path.name) or "unknown"
    file_type = _estimate_type(sf)

    lines = [
        "---",
        f"title: \"{_escape_yaml(title)}\"",
        f"source: \"{sf.source_type}\"",
        f"source_file: \"{sf.path.name}\"",
        f"import_date: \"{_today()}\"",
    ]
    if date != "unknown":
        lines.append(f"date: \"{date}\"")
    if file_type:
        lines.append(f"type: \"{file_type}\"")
    if sf.size_bytes:
        lines.append(f"size_bytes: {sf.size_bytes}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ============================================================
# 辅助分类
# ============================================================


def _match_filename(sf: SourceFile) -> Optional[str]:
    """从文件名匹配目标目录"""
    name_lower = sf.path.name.lower()
    name_lower += " " + sf.path.stem.lower()

    # 遍历规则
    sorted_rules = sorted(CLASSIFICATION_RULES, key=lambda r: r[0], reverse=True)
    for weight, keywords, target in sorted_rules:
        for kw in keywords:
            if kw.lower() in name_lower:
                return target
    return None


def _match_content(content: str) -> Optional[str]:
    """从内容匹配目标目录"""
    content_lower = content.lower()
    sorted_rules = sorted(CLASSIFICATION_RULES, key=lambda r: r[0], reverse=True)
    for weight, keywords, target in sorted_rules:
        score = 0
        for kw in keywords:
            if kw.lower() in content_lower:
                score += 1
        # 需要至少匹配2个关键词，或权重90+且匹配1个
        if score >= 2 or (weight >= 90 and score >= 1):
            return target
    return None


def _to_slug(text: str) -> str:
    """
    将标题转为英文 slug。

    策略:
    1. 先提取标题中的英文/数字关键词
    2. 再替换常见中文关键词为英文
    3. 如果全是中文，使用简短描述 + 哈希
    """
    slug = text.lower().strip()

    # Step 1: 如果标题含有足够多的 ASCII 字符，直接处理
    ascii_count = sum(1 for c in slug if c.isascii() and (c.isalnum() or c in "-_. "))
    total_chars = len(slug.replace(" ", ""))

    if ascii_count >= 3 or total_chars < 20:
        # 有足够多的英文/数字，用传统方式
        # 替换常见中文词为英文
        cn_en_map = [
            ("最佳实践", "best-practice-"),
            ("分布式", "distributed-"),
            ("云原生", "cloud-native-"),
            ("高性能", "high-perf-"),
            ("服务器", "server-"),
            ("大模型", "llm-"),
            ("架构", "arch-"),
            ("设计", "design-"),
            ("分析", "analysis-"),
            ("报告", "report-"),
            ("对比", "comparison-"),
            ("指南", "guide-"),
            ("教程", "tutorial-"),
            ("调研", "research-"),
            ("方案", "solution-"),
            ("技术", "tech-"),
            ("部署", "deploy-"),
            ("性能", "perf-"),
            ("测试", "test-"),
            ("管理", "mgmt-"),
            ("存储", "storage-"),
            ("网络", "network-"),
            ("安全", "security-"),
            ("容器", "container-"),
            ("入门", "start-"),
            ("最新", "latest-"),
            ("配置", "config-"),
            ("安装", "install-"),
            ("运维", "ops-"),
            ("综述", "survey-"),
            ("使用", "usage-"),
            ("详细", "detail-"),
            ("完整", "full-"),
            ("深度", "deep-"),
        ]
        for cn, en in cn_en_map:
            slug = slug.replace(cn, en)

        # 提取所有长度 >= 2 的字母数字 token
        tokens = re.findall(r"[a-z0-9]{2,}", slug)
        if tokens:
            seen: set[str] = set()
            selected = []
            for t in tokens:
                if t not in seen:
                    seen.add(t)
                    selected.append(t)
                if len(selected) >= 6:
                    break
            return SLUG_SEPARATOR.join(selected)

    # 纯中文 → 取前 4 个不重复汉字
    chinese_chars: list[str] = []
    for c in text:
        if "\u4e00" <= c <= "\u9fff" and c not in chinese_chars:
            chinese_chars.append(c)
        if len(chinese_chars) >= 4:
            break
    if chinese_chars:
        return f"cn-{''.join(chinese_chars)}"
    return "imported"


def _escape_yaml(text: str) -> str:
    """转义 YAML 特殊字符"""
    return text.replace('"', '\\"').replace("\n", " ").strip()


def _today() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def _estimate_type(sf: SourceFile) -> str:
    """估算文档类型"""
    if not sf.content:
        return "imported"
    if sf.source_type in ("doubao", "doubao20260523"):
        return "doubao_dialogue"
    if sf.source_type == "fetched_markdown":
        return "web_article"
    if sf.source_type == "pdf":
        return "pdf_import"
    return "imported"
