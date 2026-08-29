#!/usr/bin/env python3
"""extract-questions.py — FR-22: 从 import/ 素材中提取用户问题

继承自 scripts/tools/extract-user-questions.py 的核心逻辑，增加 argparse CLI。

用法:
  # 全量提取
  python3 scripts/discover/extract-questions.py --source import/ --output discover/questions/

  # 指定来源
  python3 scripts/discover/extract-questions.py --source import/doubao/ --output discover/questions/doubao/

  # 预览
  python3 scripts/discover/extract-questions.py --source import/cnblogs/ --dry-run
"""

import argparse
import json
import refrom datetime import datetime
from pathlib import Path


def extract_questions_from_file(file_path: Path) -> list[dict]:
    """从文件中提取用户问题（继承自 tools/extract-user-questions.py 逻辑）"""
    questions = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        lines = content.split("\n")
        prev_line = ""

        # AI 回复特征模式 — 前面的行可能是用户提问
        ai_response_patterns = [
            r"^我将.*",
            r"^即将开始.*",
            r"^接下来将为你生成报告：",
            r"^为了给你提供更有针对性的",
            r"^为了更好地支持您的",
            r"^为了更准确地分析您的",
            r"^创建时间：",
            r"^需要我.*吗[？?]$",
            r"^补充内容已覆盖各维度",
            r"^我将严格按照你给出的",
        ]

        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                prev_line = line
                continue

            # 检查上一行是否是 AI 回复特征
            is_prev_ai = any(re.match(p, prev_line) for p in ai_response_patterns)

            # 当前行是否可能是问题
            is_question = False
            if line.endswith("？") or line.endswith("?"):
                is_question = True
            elif line.startswith("如何") or line.startswith("怎么") or line.startswith("怎样"):
                is_question = True
            elif line.startswith("什么是") or line.startswith("什么是") or line.startswith("啥是"):
                is_question = True
            elif re.match(r"^[为什么干啥为何].*[？?]?$", line):
                is_question = True

            if is_question or is_prev_ai:
                questions.append({
                    "text": line[:120],
                    "source_file": str(file_path.relative_to(file_path.parents[2]) if len(file_path.parents) > 2 else file_path.name),
                    "line": lines.index(line) + 1 if line in lines else 0,
                    "type": "question" if is_question else "statement",
                })

            prev_line = line

    except Exception as e:
        print(f"  [WARN] 读取失败 {file_path.name}: {e}", file=sys.stderr)

    return questions


def deduplicate(questions: list[dict]) -> list[dict]:
    """基于问题文本去重"""
    seen = set()
    result = []
    for q in questions:
        text_key = q["text"].strip().lower()[:60]
        if text_key not in seen:
            seen.add(text_key)
            result.append(q)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="FR-22: 从 import/ 素材中提取用户问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n  %(prog)s --source import/doubao/ --output discover/questions/\n  %(prog)s --source import/ --dedup --dry-run",
    )
    parser.add_argument("--source", "-s", default="import/", help="源目录路径（默认: import/）")
    parser.add_argument("--output", "-o", default=None, help="输出目录（默认: discover/questions/）")
    parser.add_argument("--dedup", action="store_true", help="启用内容去重")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入文件")
    parser.add_argument("--batch-size", type=int, default=50, help="每批次文件数（默认 50）")
    args = parser.parse_args()

    # 解析路径
    project_root = Path(__file__).parent.parent.parent
    source_dir = Path(args.source)
    if not source_dir.is_absolute():
        source_dir = project_root / source_dir

    if not source_dir.exists():
        print(f"[ERROR] 源目录不存在: {source_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir = None
    if args.output:
        output_dir = Path(args.output)
        if not output_dir.is_absolute():
            output_dir = project_root / output_dir
    else:
        output_dir = project_root / "discover" / "questions"

    # 扫描文件
    md_files = sorted(source_dir.rglob("*.md"))
    print(f"[INFO] 扫描到 {len(md_files)} 个 .md 文件: {source_dir}")

    if not md_files:
        print("[WARN] 未找到 .md 文件", file=sys.stderr)
        sys.exit(0)

    # 批量提取
    all_questions = []
    batch_count = 0
    for i in range(0, len(md_files), args.batch_size):
        batch = md_files[i:i + args.batch_size]
        batch_questions = []
        for f in batch:
            qs = extract_questions_from_file(f)
            batch_questions.extend(qs)
            all_questions.extend(qs)
        batch_count += 1
        print(f"  批次 {batch_count}: {len(batch)} 文件 → {len(batch_questions)} 问题")

    # 去重
    before_dedup = len(all_questions)
    if args.dedup:
        all_questions = deduplicate(all_questions)
        print(f"  去重: {before_dedup} → {len(all_questions)} ({len(all_questions)/before_dedup*100:.0f}% 保留)")

    # 统计
    stats = {
        "batch_id": datetime.now().strftime("%Y-%m-%d-%H%M%S"),
        "source": str(source_dir),
        "total_files": len(md_files),
        "questions_extracted": len(all_questions),
        "dedup_rate": round(1 - len(all_questions)/before_dedup, 2) if before_dedup > 0 else 1.0,
    }

    print(f"\n[RESULT]")
    print(f"  总文件: {stats['total_files']}")
    print(f"  提取问题: {stats['questions_extracted']}")
    print(f"  去重率: {stats['dedup_rate']*100:.0f}%")

    if args.dry_run:
        print("\n[DRY-RUN] 预览前 10 条问题:")
        for q in all_questions[:10]:
            print(f"  [{q['type']}] {q['text']}")
        print("  ... (预览模式，未写入)")
        return

    # 写入
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"questions_{stats['batch_id']}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": stats,
            "questions": all_questions,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 写入 {output_file}")
    print(f"  大小: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
