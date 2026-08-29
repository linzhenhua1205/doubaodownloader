#!/usr/bin/env python3
"""
quality-gate.py — 低质量跳过工具 (sr-006 X-10)

对明显无价值的输入（空文件/模板壳/纯目录索引/无实质内容）跳过 AI 处理。

用法:
  # 作为模块引用
  from scripts.tools.quality_gate import QualityGate

  gate = QualityGate()
  result = gate.evaluate("path/to/file.md")
  # => {"pass": True/False, "score": 0-100, "reasons": [...]}

  # 批量评估
  results = gate.batch(["file1.md", "file2.md"])

  # CLI 模式
  python3 scripts/tools/quality-gate.py <path>...              # 评估文件
  python3 scripts/tools/quality-gate.py dir <dir> [--ext .md]  # 评估目录
  python3 scripts/tools/quality-gate.py check <path>           # 快速检查
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ── 低质量判定阈值 ──
MIN_CONTENT_LINES = 5           # 最少有效内容行数（非空、非标题空壳）
MIN_CONTENT_CHARS = 100         # 最少有效字符数
MAX_EMPTY_RATIO = 0.6           # 空行占比上限
MAX_TEMPLATE_RATIO = 0.5        # 模板结构占比上限
MIN_MEANINGFUL_RATIO = 0.15     # 有效内容占比下限
MIN_UNIQUE_WORDS = 10           # 最少不重复词数

# ── 低质量模式（正则） ──
TEMPLATE_PATTERNS = [
    r'^#\s+(题目|标题|Title|Topic)',
    r'^(摘要|Abstract|概述|Overview)\s*$',
    r'^##\s+(引言|Introduction|背景|Background)',
    r'^\*\*版本\*\*.*\|.*\*\*更新\*\*',
    r'^-\s+\[ \]',  # 空 checkbox
    r'^(待完成|TODO|待补充|TBD)',
    r'^\|.*\|.*\|$',  # 单个空表格行
    r'^```$',          # 空代码块
    r'^---\s*$',       # 分隔线
    r'^\[//\]: # ',    # comment tag
    r'^<!--.*-->$',    # HTML comment
]

INDEX_ONLY_PATTERNS = [
    r'^\[.*\]\(.*\)',      # 全链接
    r'^\|.*\[.*\].*\|',    # 含链接的表格
    r'^-\s+\[.*\]\(.*\)',  # 列表中的链接
]

# ── 缓存 ──
TEMPLATE_REGEX = re.compile('|'.join(TEMPLATE_PATTERNS), re.MULTILINE)
INDEX_REGEX = re.compile('|'.join(INDEX_ONLY_PATTERNS))


class QualityGate:
    """
    内容质量门禁。

    评估策略:
      1. 基础检查: 行数/字符数/空行比
      2. 模板检测: 是否只有框架没有实质内容
      3. 索引检测: 是否纯目录/链接集合
      4. 内容密度: 有效内容占比 / 唯一词数量
    """

    def __init__(self, min_lines: int = MIN_CONTENT_LINES,
                 min_chars: int = MIN_CONTENT_CHARS,
                 max_empty_ratio: float = MAX_EMPTY_RATIO,
                 max_template_ratio: float = MAX_TEMPLATE_RATIO):
        self.min_lines = min_lines
        self.min_chars = min_chars
        self.max_empty_ratio = max_empty_ratio
        self.max_template_ratio = max_template_ratio

    def evaluate(self, path: str) -> dict:
        """
        评估单个文件的质量。

        返回:
            pass:   是否通过质量门禁
            score:  质量评分 (0-100)
            reasons: 未通过原因列表
            details: 详细统计
        """
        p = Path(path)
        if not p.is_absolute():
            p = REPO_ROOT / p

        if not p.exists():
            return {
                "pass": False,
                "score": 0,
                "reasons": [f"文件不存在: {path}"],
                "details": {}
            }

        try:
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            return {
                "pass": False,
                "score": 0,
                "reasons": [f"读取失败: {e}"],
                "details": {}
            }

        reasons = []
        lines = content.splitlines()
        non_empty_lines = [l for l in lines if l.strip()]
        total_lines = len(lines)
        non_empty_count = len(non_empty_lines)
        total_chars = len(content)
        empty_ratio = 1 - (non_empty_count / max(total_lines, 1))

        # 统计
        template_lines = sum(1 for l in lines if TEMPLATE_REGEX.search(l))
        index_lines = sum(1 for l in lines if INDEX_REGEX.search(l))
        unique_words = len(set(re.findall(r'\b\w+\b', content.lower())))

        # 评估项
        details = {
            "total_lines": total_lines,
            "non_empty_lines": non_empty_count,
            "total_chars": total_chars,
            "empty_ratio": round(empty_ratio, 3),
            "template_lines": template_lines,
            "index_lines": index_lines,
            "unique_words": unique_words,
        }

        score = 100.0

        # 1. 基础检查
        if non_empty_count < self.min_lines:
            reasons.append(f"有效行数不足: {non_empty_count} < {self.min_lines}")
            score -= 30

        if total_chars < self.min_chars:
            reasons.append(f"内容过短: {total_chars} chars < {self.min_chars}")
            score -= 20

        # 2. 空行比
        if empty_ratio > self.max_empty_ratio:
            reasons.append(f"空行占比过高: {empty_ratio:.0%} > {self.max_empty_ratio:.0%}")
            score -= 15

        # 3. 模板检测
        if non_empty_count > 0:
            template_ratio = template_lines / non_empty_count
            if template_ratio > self.max_template_ratio:
                reasons.append(f"模板结构占比过高: {template_ratio:.0%}")
                score -= 20

        # 4. 索引检测: 全链接的内容
        if non_empty_count > 0:
            index_ratio = index_lines / non_empty_count
            if index_ratio > 0.7:  # 70%+ 是链接
                reasons.append(f"纯索引/链接集合: {index_ratio:.0%} 行为链接")
                score -= 25

        # 5. 内容密度
        meaningful_chars = sum(
            len(l) for l in non_empty_lines
            if not TEMPLATE_REGEX.search(l) and not INDEX_REGEX.search(l)
        )
        if total_chars > 0:
            meaningful_ratio = meaningful_chars / total_chars
            if meaningful_ratio < MIN_MEANINGFUL_RATIO:
                reasons.append(f"有效内容占比过低: {meaningful_ratio:.1%}")
                score -= 15

        # 6. 唯一词
        if unique_words < MIN_UNIQUE_WORDS and total_chars > self.min_chars:
            reasons.append(f"词汇多样性不足: {unique_words} 个唯一词")
            score -= 10

        # 7. 特殊检测: 只有分隔线和空壳
        if non_empty_count <= 3 and total_chars < 200:
            reasons.append("近乎空文件")
            score -= 40

        score = max(0, min(100, score))
        passed = score >= 50 and len(reasons) <= 3

        return {
            "pass": passed,
            "score": round(score, 0),
            "reasons": reasons[:5],  # 最多返回 5 个原因
            "details": details,
        }

    def batch(self, paths: List[str]) -> Dict[str, dict]:
        """批量评估"""
        results = {}
        for path in paths:
            results[path] = self.evaluate(path)
        return results

    def filter_low_quality(self, paths: List[str],
                           threshold: float = 50) -> Tuple[List[str], List[dict]]:
        """
        过滤低质量文件。

        返回: (通过的文件列表, 未通过的评估结果列表)
        """
        passed = []
        failed_info = []
        results = self.batch(paths)
        for path, result in results.items():
            if result["pass"] and result["score"] >= threshold:
                passed.append(path)
            else:
                failed_info.append({
                    "path": path,
                    "score": result["score"],
                    "reasons": result["reasons"],
                })
        return passed, failed_info

    def summary(self, paths: List[str]) -> dict:
        """生成质量摘要"""
        results = self.batch(paths)
        total = len(results)
        passed = sum(1 for r in results.values() if r["pass"])
        failed = total - passed
        avg_score = sum(r["score"] for r in results.values()) / max(total, 1)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / max(total, 1) * 100, 1),
            "avg_score": round(avg_score, 0),
            "failures": [
                {"path": p, "score": r["score"], "reasons": r["reasons"]}
                for p, r in sorted(results.items(), key=lambda x: x[1]["score"])
                if not r["pass"]
            ][:20],  # 最多显示 20 个失败
        }


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="内容质量门禁工具 (sr-006 X-10)",
    )
    parser.add_argument("paths", nargs="*", help="文件路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--threshold", type=float, default=50, help="通过阈值 (0-100)")

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    p_dir = subparsers.add_parser("dir", help="评估目录")
    p_dir.add_argument("dir", help="目录路径")
    p_dir.add_argument("--ext", default=".md", help="文件扩展名")
    p_dir.add_argument("--threshold", type=float, default=50)
    p_dir.add_argument("--json", action="store_true")

    p_check = subparsers.add_parser("check", help="快速检查")
    p_check.add_argument("path", help="文件路径")

    p_summary = subparsers.add_parser("summary", help="目录质量概要")
    p_summary.add_argument("dir", help="目录路径")
    p_summary.add_argument("--ext", default=".md")

    args = parser.parse_args()
    gate = QualityGate()

    if args.command == "dir" or (args.command is None and not args.paths):
        # 目录模式
        if args.command == "dir":
            target_dir = args.dir
            ext = args.ext
            threshold = args.threshold
            json_output = args.json
        else:
            parser.print_help()
            return

        d = Path(target_dir)
        if not d.is_absolute():
            d = REPO_ROOT / d
        files = sorted(d.rglob(f"*{ext}"))
        paths = [str(f) for f in files]

        print(f"📊 质量门禁扫描: {d}")
        print(f"  文件数: {len(files)}")
        print("─" * 50)

        passed, failed = gate.filter_low_quality(paths, threshold=threshold)
        for f in failed:
            rel = Path(f["path"]).relative_to(REPO_ROOT)
            print(f"  ❌ [{f['score']:.0f}] {rel}")
            for r in f["reasons"]:
                print(f"       ↳ {r}")

        if not failed:
            print(f"  ✅ 所有文件通过 ({len(passed)} 个)")

        print(f"  通过: {len(passed)} | 未通过: {len(failed)}")

        if json_output:
            import json as _json
            print(_json.dumps({
                "passed": [str(Path(p).relative_to(REPO_ROOT)) for p in passed],
                "failed": [
                    {
                        "path": str(Path(f["path"]).relative_to(REPO_ROOT)),
                        "score": f["score"],
                        "reasons": f["reasons"],
                    }
                    for f in failed
                ],
            }, ensure_ascii=False, indent=2))

    elif args.command == "check":
        result = gate.evaluate(args.path)
        rel = Path(args.path).relative_to(REPO_ROOT) if Path(args.path).exists() else args.path

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            status = "✅ 通过" if result["pass"] else "❌ 未通过"
            print(f"📊 质量评估: {rel}")
            print(f"  状态: {status} (评分: {result['score']}/100)")
            if result["reasons"]:
                print(f"  原因:")
                for r in result["reasons"]:
                    print(f"    ↳ {r}")
            if result["details"]:
                d = result["details"]
                print(f"  详情: {d.get('total_lines',0)} 行 | "
                      f"{d.get('non_empty_lines',0)} 有效行 | "
                      f"{d.get('total_chars',0)} 字符 | "
                      f"{d.get('unique_words',0)} 唯一词")

    elif args.command == "summary":
        d = Path(args.dir)
        if not d.is_absolute():
            d = REPO_ROOT / d
        files = sorted(d.rglob(f"*{args.ext}"))
        paths = [str(f) for f in files]
        s = gate.summary(paths)

        print(f"📊 质量概要: {d}")
        print(f"  总文件: {s['total']}")
        print(f"  通过:   {s['passed']} ({s['pass_rate']}%)")
        print(f"  未通过: {s['failed']}")
        print(f"  平均分: {s['avg_score']}/100")
        if s["failures"]:
            print(f"\n  低质量文件 (前 {min(20, len(s['failures']))} 个):")
            for f in s["failures"][:10]:
                rel = str(Path(f["path"]).relative_to(REPO_ROOT))
                print(f"    [{f['score']:.0f}] {rel}")
                for r in f["reasons"][:2]:
                    print(f"      ↳ {r}")

    else:
        # 直接文件评估
        if not args.paths:
            parser.print_help()
            return

        for path in args.paths:
            result = gate.evaluate(path)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                status = "✅ 通过" if result["pass"] else "❌ 未通过"
                print(f"{status} [{result['score']:.0f}/100] {path}")


if __name__ == "__main__":
    main()
