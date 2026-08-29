#!/usr/bin/env python3
"""ai-classify.py — FR-23: AI 分类

对 discover/ 内容按预设分类体系自动归类。
关键词规则匹配 + AI 语义兜底（预留接口）。

用法:
  # 分析并输出 JSON
  python3 scripts/discover/ai-classify.py --input discover/site/ --output tags.json

  # 写入 YAML frontmatter
  python3 scripts/discover/ai-classify.py --input discover/newwiki2/ --apply

  # 统计分类分布
  python3 scripts/discover/ai-classify.py --input discover/site/ --stats
"""

import argparse
import jsonfrom collections import Counter
from pathlib import Path

from config import CLASSIFICATION_SYSTEM, DISCOVER_DIR


def classify_content(content: str, filename: str = "") -> str:
    """基于关键词权重匹配分类（后续可加 AI 语义兜底）"""
    text = content.lower()[:5000] + " " + filename.lower()
    scores: dict[str, int] = {}

    for category, info in CLASSIFICATION_SYSTEM.items():
        if category == "其他":
            continue  # 兜底
        score = 0
        for kw in info["keywords"]:
            score += text.count(kw.lower()) * 2
        if score > 0:
            scores[category] = score

    if not scores:
        return "其他"

    return max(scores, key=scores.get)


def extract_frontmatter(content: str) -> dict:
    """提取已有的 YAML frontmatter"""
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter[k.strip()] = v.strip()
    return frontmatter


def inject_classification(content: str, category: str) -> str:
    """在 frontmatter 中注入或更新分类标签"""
    tag_line = f"category: {category}"
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
            fm_lines = parts[1].split("\n")
            # 检查是否已有 category
            has_cat = any(line.strip().startswith("category:") for line in fm_lines)
            if has_cat:
                new_fm = "\n".join(
                    tag_line if line.strip().startswith("category:") else line
                    for line in fm_lines
                )
            else:
                new_fm = parts[1].strip() + f"\n{tag_line}"
            return f"---\n{new_fm}\n---{body}"
    else:
        return f"---\n{tag_line}\n---\n{content}"
    return content


def main():
    parser = argparse.ArgumentParser(
        description="FR-23: AI 分类 — 对 discover/ 内容自动归类",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True, help="输入文件或目录路径")
    parser.add_argument("--output", "-o", default=None, help="输出 JSON 路径（默认: 终端输出）")
    parser.add_argument("--apply", action="store_true", help="将分类标签写入文件 frontmatter")
    parser.add_argument("--stats", action="store_true", help="仅输出分类分布统计")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = DISCOVER_DIR.parent / input_path

    if not input_path.exists():
        print(f"[ERROR] 路径不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 收集文件
    files = []
    if input_path.is_dir():
        files = sorted(input_path.rglob("*.md"))
    else:
        files = [input_path]

    if not files:
        print("[WARN] 未找到 .md 文件")
        sys.exit(0)

    # 分类
    results = []
    counter = Counter()
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  [WARN] 读取失败 {f.name}: {e}", file=sys.stderr)
            continue
        cat = classify_content(content, f.name)
        counter[cat] += 1
        results.append({
            "file": str(f.relative_to(DISCOVER_DIR.parent) if DISCOVER_DIR.parent in f.parents else f),
            "category": cat,
            "size_bytes": f.stat().st_size,
        })

    if args.stats:
        print(f"\n=== 分类分布 ({len(files)} 文件) ===\n")
        for cat, count in counter.most_common():
            target = CLASSIFICATION_SYSTEM.get(cat, {}).get("knowledge_target", "-")
            print(f"  {cat:12s} → {count:4d} 文件 ({count/len(files)*100:5.1f}%)  → {target}")
        return

    print(f"\n[INFO] 分类完成: {len(results)}/{len(files)} 文件")

    if args.apply:
        applied = 0
        for r in results:
            fpath = Path(r["file"])
            if not fpath.is_absolute():
                fpath = DISCOVER_DIR.parent / fpath
            if not fpath.exists():
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
                new_content = inject_classification(content, r["category"])
                if new_content != content:
                    fpath.write_text(new_content, encoding="utf-8")
                    applied += 1
            except Exception as e:
                print(f"  [WARN] 写入失败 {fpath.name}: {e}", file=sys.stderr)
        print(f"  已写入分类到 {applied} 个文件")

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = DISCOVER_DIR.parent / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "total": len(results),
                "distribution": dict(counter.most_common()),
                "results": results,
            }, f, ensure_ascii=False, indent=2)
        print(f"  [OK] 写入 {output_path}")
    else:
        # 终端输出摘要
        print("\n分类分布:")
        for cat, count in counter.most_common():
            print(f"  {cat:12s} → {count:4d}")


if __name__ == "__main__":
    main()
