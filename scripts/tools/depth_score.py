#!/usr/bin/env python3
"""
depth_score.py — 内容深度启发式评分器 v1（depth-completer 配套）

audit-002 封闭性加固：把文档承诺的 depth_score 从"设计承诺"落为真实实现。
**设计原则**: 可机械量化的深度信号用脚本检测，语义判断（原理是否正确、
对比是否恰当）留给 LLM/人工 —— 脚本给"线索分"，不冒充"结论分"。

**类型适用性**: 六维对"原理分析/技术调研"类文档最有效；"workflow/流程/
审计/清单"类文档 D1（原理）天然低分属正常特征，请勿误判为缺陷。

六维启发式评分（每维 0-5）:
  D1 原理溯源: 原理词密度（为什么/原理/机制/本质/第一性/物理/数学/信息论）
  D2 量化支撑: 数字+单位密度（GB/s/ns/ms/W/C°/%等）
  D3 对比基线: 对比词密度（对比/相比/优于/vs/相较于/基线）
  D4 边界条件: 边界词密度（适用于/不适用/局限/阈值/条件/场景/例外）
  D5 推导链:   推导连接词密度（因此/所以/因为/推导/意味着/从而）
  D6 结构完整: 标题层级/段落长度/来源引用

规则（depth-completer SKILL.md §6 描述）:
  ① 某层得分 ≤1 → 标记深度不足（需补齐）
  ② 某层≥4且另一相关层≤2 → 标记深度失衡
  ③ 整体在某方向极深且其他方向极浅 → 标记方向锁定

用法:
  python3 scripts/tools/depth_score.py <文件.md>
  python3 scripts/tools/depth_score.py <文件.md> --verbose
  python3 scripts/tools/depth_score.py <目录> --summary
"""

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent

# 六维关键词
DIMENSIONS = {
    "D1 原理溯源": re.compile(r"(为什么|原理|机制|本质|第一性|物理极限|信息论|经济规律|推导出|根因|底层逻辑)", re.I),
    "D2 量化支撑": re.compile(r"\d+(?:\.\d+)?\s*(?:GB/s|TB/s|Gb/s|Gbps|ns|ms|μs|us|s|W|kW|MW|°C|%|GB|TB|MB|KB|nm|GHz|MHz|倍|x\b)", re.I),
    "D3 对比基线": re.compile(r"(对比|相比|相较于|优于|逊于|vs\.?|versus|基线|benchmark|对标|差距|优势在于)", re.I),
    "D4 边界条件": re.compile(r"(适用于|不适用|适用场景|局限|边界|阈值|条件|例外|前提|假设|何时失效|限制)", re.I),
    "D5 推导链":   re.compile(r"(因此|所以|因为|推导|意味着|从而|进而|由此|得出结论|等价于)", re.I),
    "D6 结构完整": re.compile(r"(##|###|参考文献|参考资料|来源|changelog|TOC|目录)", re.I),
}


def score_text(text: str) -> dict:
    """返回 {dim: (count, score)}，score = min(5, count // threshold)"""
    results = {}
    for dim, pattern in DIMENSIONS.items():
        count = len(pattern.findall(text))
        # 绝对命中数评分（v1.2: 长文档天然命中多，按绝对数分级）
        # ≤2 次 → 0分；3-5 → 1；6-9 → 2；10-14 → 3；15-19 → 4；≥20 → 5
        if count <= 2:
            score = 0
        elif count <= 5:
            score = 1
        elif count <= 9:
            score = 2
        elif count <= 14:
            score = 3
        elif count <= 19:
            score = 4
        else:
            score = 5
        results[dim] = (count, score)
    return results


def diagnose(results: dict) -> list:
    """应用三条诊断规则"""
    issues = []
    scores = {dim: s for dim, (c, s) in results.items()}
    # ① 某层≤1 → 深度不足
    for dim, s in scores.items():
        if s <= 1:
            issues.append(f"🔴 深度不足: {dim} (score={s}) — 需优先补齐")
    # ② 某层≥4且另一相关层≤2 → 失衡
    strong = [d for d, s in scores.items() if s >= 4]
    weak = [d for d, s in scores.items() if s <= 2]
    if strong and weak:
        issues.append(f"🟡 深度失衡: {', '.join(strong)} 强 vs {', '.join(weak)} 弱 — 建议补弱")
    # ③ 方向锁定: 最强维 - 最弱维 ≥ 4
    vals = list(scores.values())
    if max(vals) - min(vals) >= 4:
        issues.append(f"🟠 方向锁定: 极差 {max(vals)-min(vals)} — 单方向极深，需均衡")
    return issues


def scan_file(path: Path, verbose: bool = False) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    results = score_text(text)
    issues = diagnose(results)
    total = sum(s for _, s in results.values())

    if verbose:
        print(f"\n📄 {path.name} — 六维深度评分 (总分 {total}/30)")
        for dim, (count, score) in results.items():
            bar = "█" * score + "░" * (5 - score)
            print(f"  {dim}: {bar} {score}/5 (命中 {count} 次)")
        for issue in issues:
            print(f"  {issue}")
    return {"path": str(path), "total": total, "dimensions": results, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description="内容深度启发式评分器")
    parser.add_argument("target", help="文件或目录")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"❌ 不存在: {target}")
        sys.exit(1)

    if target.is_file():
        scan_file(target, verbose=True)
        sys.exit(0)

    # 目录: 扫描 .md 文件
    files = sorted(target.rglob("*.md"))
    # 排除 tmp/bak/_archive
    files = [f for f in files if "tmp/" not in str(f) and "_archive" not in str(f) and "bak" not in str(f)]
    if not files:
        print("(无 md 文件)")
        sys.exit(0)

    all_results = [scan_file(f, verbose=False) for f in files]
    weak = [r for r in all_results if r["total"] <= 12]
    all_results.sort(key=lambda r: r["total"])

    print(f"\n📊 目录扫描: {len(files)} 个 md 文件")
    print(f"   平均深度分: {sum(r['total'] for r in all_results)/len(all_results):.1f}/30")
    print(f"   🔴 薄弱文件 (≤12分): {len(weak)} 个")
    for r in weak[:10]:
        print(f"     {r['total']:>2}/30 {os.path.relpath(r['path'], WORKSPACE)}")
    if args.summary and weak:
        print(f"\n   （共 {len(weak)} 个薄弱文件，用 --verbose 查看单文件六维详情）")


if __name__ == "__main__":
    main()
