#!/usr/bin/env python3
"""ai-batch-extract-questions.py — FR-25: AI 批量提取问题

对一批文件用同一提示词提取/推理问题。
与 extract-questions.py 互补——后者提取已有问题，本脚本从陈述中推理可提问的问题。

用法:
  python3 scripts/discover/ai-batch-extract-questions.py --input discover/site/ --output questions.json
  python3 scripts/discover/ai-batch-extract-questions.py --input discover/newwiki2/ --batch-size 5
  python3 scripts/discover/ai-batch-extract-questions.py --input discover/site/AI与机器学习/ --prompt-file prompt.txt
"""

import argparse
import json
import refrom datetime import datetime
from pathlib import Path

from config import DISCOVER_DIR, DEFAULT_BATCH_SIZE

# 默认推理提示词模板
DEFAULT_PROMPT = """基于以下内容，推理出 3-5 个有深度的可研究问题。
要求：
1. 问题要有实际价值，能引发技术讨论或深入研究
2. 问题要有明确的回答边界，不是开放性空泛问题
3. 优先从内容中的"创新点"、"争议点"、"未解决"、"挑战"等关键词附近找
4. 每个问题附 1-2 句问什么 / 为什么重要

内容：
{content}
"""


def infer_questions(content: str, filename: str = "") -> list[dict]:
    """从内容中推理可提问的问题（基于规则，预留 AI 接口）"""
    questions = []
    text = content[:8000]

    # 1. 从"挑战"/"问题"/"难点"等章节提取
    challenge_sections = re.findall(
        r"(?:挑战|问题|难点|局限|不足|未解决|待解决|瓶颈|痛点)[：:】]?\s*(.*?)(?=\n##|\Z)",
        text, re.DOTALL
    )
    for section in challenge_sections:
        sentences = re.split(r"[。！？!?；;]", section.strip())
        for s in sentences[:3]:
            s = s.strip()
            if len(s) > 10 and len(s) < 200:
                questions.append({
                    "question": f"如何解决 {s[:80]}？",
                    "source": "challenge_section",
                    "context": s[:120],
                    "importance": "high",
                })

    # 2. 从"创新"/"关键"/"核心"附近找
    key_sentences = re.findall(
        r"[。！？!?]([^。！？!?]{10,120}(?:创新|关键|核心|突破|首创)[^。！？!?]{10,120})[。！？!?]",
        text
    )
    for s in key_sentences[:3]:
        s = s.strip()
        if len(s) > 15:
            questions.append({
                "question": f"{s[:80]} 的原理和实施路径是什么？",
                "source": "key_sentence",
                "context": s[:120],
                "importance": "medium",
            })

    # 3. 从比较/对比处找
    compare_sections = re.findall(
        r"(?:对比|比较|区别|差异|vs|versus|相比于|相对于)[^。！？!?]{20,150}",
        text
    )
    for s in compare_sections[:2]:
        questions.append({
            "question": f"{s[:80]} 的深度对比分析？",
            "source": "comparison",
            "context": s[:120],
            "importance": "medium",
        })

    # 4. 从量化数据附近找追问点
    data_mentions = re.findall(
        r"[^。！？!?]{10,60}(\d+[.%倍xXsS/GgBbKkMm]?[^。！？!?]{10,60})[。！？!?]",
        text
    )
    for s in data_mentions[:2]:
        s = s.strip()
        if len(s) > 15:
            questions.append({
                "question": f"{s[:80]} 这个数据的验证方法和场景边界是什么？",
                "source": "data_mention",
                "context": s[:120],
                "importance": "low",
            })

    # 去重
    seen = set()
    unique = []
    for q in questions:
        key = q["question"][:40]
        if key not in seen:
            seen.add(key)
            unique.append(q)

    return unique[:5]


def main():
    parser = argparse.ArgumentParser(
        description="FR-25: AI 批量提取问题 — 从陈述中推理可提问的问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True, help="输入文件或目录路径")
    parser.add_argument("--output", "-o", default=None, help="输出 JSON 路径")
    parser.add_argument("--prompt-file", "-p", default=None, help="自定义提示词文件（可选）")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help=f"批次大小（默认 {DEFAULT_BATCH_SIZE}）")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = DISCOVER_DIR.parent / input_path

    if not input_path.exists():
        print(f"[ERROR] 路径不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    files = []
    if input_path.is_dir():
        files = sorted(input_path.rglob("*.md"))
    else:
        files = [input_path]

    if not files:
        print("[WARN] 未找到 .md 文件")
        sys.exit(0)

    # 加载提示词
    prompt_template = DEFAULT_PROMPT
    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if prompt_path.exists():
            prompt_template = prompt_path.read_text(encoding="utf-8")
            print(f"[INFO] 使用自定义提示词: {args.prompt_file}")

    # 批量处理
    all_questions = []
    batch_count = 0
    for i in range(0, len(files), args.batch_size):
        batch = files[i:i + args.batch_size]
        batch_questions = []
        for f in batch:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                print(f"  [WARN] 读取失败 {f.name}: {e}", file=sys.stderr)
                continue
            qs = infer_questions(content, f.name)
            for q in qs:
                q["source_file"] = str(f.relative_to(DISCOVER_DIR.parent) if DISCOVER_DIR.parent in f.parents else f.name)
            batch_questions.extend(qs)
            all_questions.extend(qs)
        batch_count += 1
        print(f"  批次 {batch_count}: {len(batch)} 文件 → {len(batch_questions)} 问题")

    print(f"\n[INFO] 共推理出 {len(all_questions)} 个问题，来自 {len(files)} 文件")

    if args.dry_run:
        print("\n预览（前 10）:")
        for q in all_questions[:10]:
            print(f"  [{q['importance']}] {q['question']}")
        return

    # 写入
    batch_id = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    output = {
        "batch_id": batch_id,
        "source": str(input_path),
        "total_files": len(files),
        "questions_extracted": len(all_questions),
        "questions": all_questions,
    }

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = DISCOVER_DIR / "questions" / f"inferred_{batch_id}.json"

    if not output_path.is_absolute():
        output_path = DISCOVER_DIR.parent / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 写入 {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
