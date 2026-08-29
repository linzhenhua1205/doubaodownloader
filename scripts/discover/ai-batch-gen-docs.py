#!/usr/bin/env python3
"""ai-batch-gen-docs.py — FR-26: AI 批量从问题生成文档

将提取的问题/亮点转化为结构化知识文档（知识卡片），写入 discover/newwiki2/。

用法:
  # 从问题 JSON 生成
  python3 scripts/discover/ai-batch-gen-docs.py --input discover/questions/questions.json --output discover/newwiki2/

  # 指定模板
  python3 scripts/discover/ai-batch-gen-docs.py --input questions.json --template tech
  python3 scripts/discover/ai-batch-gen-docs.py --input questions.json --template opinion

  # 预览模式
  python3 scripts/discover/ai-batch-gen-docs.py --input questions.json --dry-run
"""

import argparse
import json
import refrom datetime import datetime
from pathlib import Path

from config import DISCOVER_DIR, SLUG_SEPARATOR, MAX_FILENAME_LEN

# ──────────────────────────────────────────────
# 文档模板
# ──────────────────────────────────────────────

TEMPLATES = {
    "tech": {
        "description": "技术类知识卡片：问题背景→核心概念→技术细节→关键数据→方案对比",
        "frame": """# {title}

> **来源**: 问题推理管道 · {date}
> **类型**: 技术分析

## 问题背景

{question}

## 核心概念

{concept}

## 技术细节

{detail}

## 关键数据

{data}

## 方案对比

{comparison}

## 参考来源

- 由 {source_file} 推理生成
""",
    },
    "opinion": {
        "description": "观点类：论点→论据→反方观点→结论",
        "frame": """# {title}

> **来源**: 问题推理管道 · {date}
> **类型**: 观点分析

## 核心论点

{question}

## 论据支撑

{evidence}

## 反方观点

{counterpoint}

## 结论

{conclusion}

## 参考来源

- 由 {source_file} 推理生成
""",
    },
    "data": {
        "description": "数据类：数据源→统计方法→关键发现→趋势分析",
        "frame": """# {title}

> **来源**: 问题推理管道 · {date}
> **类型**: 数据分析

## 数据来源

{source}

## 分析方法

{method}

## 关键发现

{findings}

## 趋势分析

{trend}

## 参考来源

- 由 {source_file} 推理生成
""",
    },
}


def generate_slug(title: str) -> str:
    """从标题生成 slug 文件名"""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", SLUG_SEPARATOR, slug)
    slug = slug.strip(SLUG_SEPARATOR)[:MAX_FILENAME_LEN]
    return slug + ".md"


def generate_doc(
    question: dict,
    template_name: str = "tech",
) -> tuple[str, str]:
    """根据问题和模板生成文档内容，返回 (slug, content)"""
    template = TEMPLATES.get(template_name, TEMPLATES["tech"])
    title = question.get("question", "未命名问题")[:60]
    slug = generate_slug(title)

    content = template["frame"].format(
        title=title,
        date=datetime.now().strftime("%Y-%m-%d"),
        question=title,
        concept=f"关于「{title}」的核心概念和技术原理分析。",
        detail="技术细节待补充。",
        data="关键数据待补充。",
        comparison="方案对比待补充。",
        evidence="论据待补充。",
        counterpoint="反方观点待补充。",
        conclusion="结论待补充。",
        source=question.get("source_file", "未知来源"),
        method="分析方法待补充。",
        findings="关键发现待补充。",
        trend="趋势分析待补充。",
        source_file=question.get("source_file", "unknown"),
    )

    return slug, content


def main():
    parser = argparse.ArgumentParser(
        description="FR-26: AI 批量从问题生成文档 — 问题→知识卡片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True, help="问题 JSON 文件路径")
    parser.add_argument("--output", "-o", default=None, help="输出目录（默认 discover/newwiki2/）")
    parser.add_argument("--template", "-t", default="tech",
                        choices=list(TEMPLATES.keys()),
                        help=f"文档模板（默认 tech，可选 {', '.join(TEMPLATES.keys())}）")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入文件")
    args = parser.parse_args()

    # 解析输入
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = DISCOVER_DIR.parent / input_path

    if not input_path.exists():
        print(f"[ERROR] 输入文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 读取问题 JSON
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("questions", [])
    if not questions:
        print("[WARN] 未找到问题数据")
        sys.exit(0)

    print(f"[INFO] 读取到 {len(questions)} 个问题，使用模板: {args.template}")

    # 确定输出目录
    output_dir = Path(args.output) if args.output else DISCOVER_DIR / "newwiki2"
    if not output_dir.is_absolute():
        output_dir = DISCOVER_DIR.parent / output_dir

    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    # 批量生成
    generated = 0
    for i, q in enumerate(questions):
        slug, content = generate_doc(q, args.template)
        output_path = output_dir / slug

        if args.dry_run:
            print(f"\n--- 文档 {i+1}: {slug} ---")
            print(content[:200] + "...\n")
            continue

        # 检查重名
        if output_path.exists():
            slug = slug.replace(".md", f"-{i+1}.md")
            output_path = output_dir / slug

        output_path.write_text(content, encoding="utf-8")
        generated += 1

        if (i + 1) % 20 == 0:
            print(f"  已生成 {i+1}/{len(questions)}")

    if not args.dry_run:
        print(f"\n[OK] 生成 {generated} 个文档 → {output_dir}")

    # 输出摘要
    print(f"\n模板 '{args.template}' 字段映射:")
    for field, desc in TEMPLATES[args.template]["frame"].split("\n"):
        if "{" in field and "}" in field and "title" not in field:
            fname = field.strip().strip("{}")
            print(f"  {{{fname}}}")


if __name__ == "__main__":
    main()
