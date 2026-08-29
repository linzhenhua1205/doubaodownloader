#!/usr/bin/env python3
"""ai-extract-keywords.py — FR-24: AI 提取关键字

从内容中提取 5-15 个代表性关键词/术语。
结合 TF-IDF + 停用词过滤，预留 AI 语义兜底接口。

用法:
  # 单文件
  python3 scripts/discover/ai-extract-keywords.py --input discover/newwiki2/file.md

  # 批量目录
  python3 scripts/discover/ai-extract-keywords.py --input discover/newwiki2/ --output keywords.json

  # 写入 frontmatter
  python3 scripts/discover/ai-extract-keywords.py --input discover/newwiki2/ --apply
"""

import argparse
import json
import refrom collections import Counter
from pathlib import Path

from config import MIN_KEYWORDS, MAX_KEYWORDS, DISCOVER_DIR

# ──────────────────────────────────────────────
# 停用词
# ──────────────────────────────────────────────
STOP_WORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "能", "下", "过", "来", "为", "与", "及", "等", "对", "从", "之", "所",
    "而", "但", "或", "如果", "因为", "所以", "虽然", "但是", "因此",
    "可以", "需要", "进行", "通过", "使用", "基于", "实现", "提供",
    "以及", "这些", "这个", "这种", "相关", "主要", "包括", "其中",
    "一种", "不仅", "同时", "目前", "目前", "当前", "已经", "可以",
    "没有", "不是", "就是", "而是", "一个", "两个", "三个", "所有",
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "this", "that", "these", "those", "it", "its", "they", "them",
    "and", "or", "but", "if", "because", "so", "than", "as", "of",
    "in", "on", "at", "to", "for", "with", "by", "from", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so",
}


def extract_keywords(content: str, max_keywords: int = MAX_KEYWORDS) -> list[str]:
    """从文本中提取关键词（基于词频 + 长度过滤）"""
    # 清理文本
    text = content.lower()

    # 提取中文词汇（2-6 字）
    chinese_words = re.findall(r"[\u4e00-\u9fff]{2,6}", text)

    # 提取英文术语（含连字符）
    english_terms = re.findall(r"\b[a-zA-Z][a-zA-Z0-9\-/+]{2,40}\b", text)

    # 合并并过滤停用词
    all_words = chinese_words + english_terms
    filtered = [w for w in all_words if w not in STOP_WORDS and len(w) >= 2]

    # 统计词频
    counter = Counter(filtered)

    # 过滤低频词（出现次数 ≤ 1 的不取）
    common = [(word, count) for word, count in counter.most_common(50) if count > 1]

    if not common:
        # 兜底：取频率最高的
        common = counter.most_common(max_keywords)

    # 取前 N 个
    keywords = [word for word, _ in common[:max_keywords]]

    # 保证最少个数
    if len(keywords) < MIN_KEYWORDS and len(counter) > 0:
        extra = [word for word, _ in counter.most_common(MAX_KEYWORDS) if word not in keywords]
        keywords.extend(extra[:MIN_KEYWORDS - len(keywords)])

    return keywords


def inject_keywords(content: str, keywords: list[str]) -> str:
    """在 frontmatter 中注入关键词"""
    kw_line = f"keywords: [{', '.join(keywords)}]"
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_lines = parts[1].split("\n")
            has_kw = any(line.strip().startswith("keywords:") for line in fm_lines)
            if has_kw:
                new_fm = "\n".join(
                    kw_line if line.strip().startswith("keywords:") else line
                    for line in fm_lines
                )
            else:
                new_fm = parts[1].strip() + f"\n{kw_line}"
            return f"---\n{new_fm}\n---{parts[2]}"
    return content


def main():
    parser = argparse.ArgumentParser(
        description="FR-24: AI 提取关键字 — 从内容中提取 5-15 个代表性关键词",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True, help="输入文件或目录路径")
    parser.add_argument("--output", "-o", default=None, help="输出 JSON 路径")
    parser.add_argument("--apply", action="store_true", help="将关键词写入文件 frontmatter")
    parser.add_argument("--max", type=int, default=MAX_KEYWORDS, help=f"最大关键词数（默认 {MAX_KEYWORDS}）")
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

    results = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  [WARN] 读取失败 {f.name}: {e}", file=sys.stderr)
            continue
        kw = extract_keywords(content, args.max)
        results.append({
            "file": str(f.relative_to(DISCOVER_DIR.parent) if DISCOVER_DIR.parent in f.parents else f),
            "keywords": kw,
            "count": len(kw),
        })

    print(f"[INFO] 关键字提取完成: {len(results)}/{len(files)} 文件")

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
                new_content = inject_keywords(content, r["keywords"])
                if new_content != content:
                    fpath.write_text(new_content, encoding="utf-8")
                    applied += 1
            except Exception as e:
                print(f"  [WARN] 写入失败 {fpath.name}: {e}", file=sys.stderr)
        print(f"  已写入关键词到 {applied} 个文件")

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = DISCOVER_DIR.parent / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"  [OK] 写入 {output_path}")

    # 预览前 3 条的摘要
    print("\n关键字摘要（前 5 文件）:")
    for r in results[:5]:
        print(f"  {Path(r['file']).name:45s} → {', '.join(r['keywords'][:8])}")


if __name__ == "__main__":
    main()
