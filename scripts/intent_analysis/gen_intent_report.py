#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图分析报告生成器 — 基于用户问题 CSV 生成报告骨架+数据统计

统计维度:
  1. 总量与时间范围 / 通道分布 / 按天分布
  2. 意图粗分类(关键词匹配, 参考 session-intent-analysis 意图分类体系)
  3. 话题关键词 TopN

输出: 报告 markdown (含元信息+统计+待LLM解析的章节骨架)

用法:
  python3 scripts/intent_analysis/gen_intent_report.py --csv <file.csv> --out <report.md>
"""
import csv
import os
import re
import sys
import argparse
from datetime import datetime
from collections import Counter

# 意图分类体系 (与 skill 一致)
INTENTS = [
    ("知识体系构建", ["知识库", "归档", "写入", "保存", "导入", "构建", "创建", "整理"]),
    ("深度技术分析", ["深度分析", "原理", "推导", "对比", "分析", "解析", "拆解", "解读", "设计"]),
    ("方法论制定与固化", ["方法论", "MECE", "框架", "流程", "规范", "体系", "标准化", "方案"]),
    ("技术纠错与审查", ["审查", "修正", "纠错", "检查", "校验", "验证", "审查", "复核"]),
    ("工具链优化", ["脚本", "工具", "优化", "自动化", "集成", "skill", "skills", "安装"]),
    ("信息获取与跟踪", ["调研", "搜索", "跟踪", "追踪", "日报", "周报", "监测", "动态"]),
    ("技术讨论与交流", ["讨论", "观点", "看法", "评估", "建议", "方案对比", "选型"]),
]


def classify_intent(q: str) -> str:
    ql = q.lower()
    scores = []
    for name, kws in INTENTS:
        s = sum(1 for k in kws if k.lower() in ql)
        scores.append((s, name))
    scores.sort(reverse=True)
    return scores[0][1] if scores[0][0] > 0 else "其他/未分类"


def extract_topics(q: str, n=8):
    """粗提取技术话题词"""
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}|[\u4e00-\u9fff]{2,6}", q)
    stop = {"深度分析", "分析", "提供", "输出", "进行", "后续", "使用", "完成",
            "相关", "方案", "设计", "python", "https", "github", "com"}
    cnt = Counter(w for w in words if w not in stop and len(w) >= 3)
    return cnt.most_common(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.csv, encoding="utf-8-sig")))
    total = len(rows)
    channels = Counter(r["输入通道"] for r in rows)
    days = Counter(r["用户输入时间"][:10] for r in rows)
    intents = Counter(classify_intent(r["问题描述"]) for r in rows)
    topics = extract_topics(" ".join(r["问题描述"] for r in rows))

    t0 = rows[0]["用户输入时间"] if rows else "-"
    t1 = rows[-1]["用户输入时间"] if rows else "-"

    out = f"""# 会话意图分析报告 {t0[:10]} ~ {t1[:10]}

> **概要**: 基于会话日志的用户提问意图分析（{total} 条），覆盖通道分布、意图分类、话题热点与 LLM 深度解析。
>
> **版本**: v1.0 | **日期**: {datetime.now().strftime('%Y-%m-%d')} | **状态**: 骨架(待Agent补LLM解析)

---

## 一、数据概览

| 指标 | 值 |
|:-----|:---|
| 用户提问总数 | {total} |
| 时间范围 | {t0} ~ {t1} |
| 输入通道 | {', '.join(f'{c}({n})' for c, n in channels.most_common())} |
| 日均提问 | {total / max(len(days), 1):.1f} 条/天 |

### 按天分布

| 日期 | 提问数 |
|:-----|:------:|
"""
    for d in sorted(days):
        out += f"| {d} | {days[d]} |\n"

    out += f"""
## 二、意图分类统计

| 意图类型 | 条数 | 占比 |
|:---------|:----:|:----:|
"""
    for name, n in intents.most_common():
        out += f"| {name} | {n} | {n/total*100:.1f}% |\n"

    out += f"""
## 三、话题热点 Top{n}
"""
    for w, n in topics:
        out += f"- `{w}` ×{n}\n"

    out += """
## 四、用户问题明细（最近 20 条）

| 时间 | 通道 | 问题 |
|:-----|:-----|:-----|
"""
    for r in rows[-20:]:
        q = r["问题描述"].replace("|", "\\|").replace("\n", " ")[:60]
        out += f"| {r['用户输入时间']} | {r['输入通道']} | {q} |\n"

    out += """
---

## 五、LLM 深度解析（待 Agent 补充）

### 意图分布解读
<!-- 为何某意图占比高？背后的用户需求模式 -->

### 决策模式洞察
<!-- 用户工作习惯、决策偏好 -->

### 技术关注演化
<!-- 技术维度关注优先级变化 -->

### 对话主线提炼
<!-- 典型工作流场景 -->

### 优化建议增强

| 优先级 | 建议 | 执行路径 | 依据 |
|:-:|:-----|:---------|:-----|
| P0 | - | - | - |

---

## 数据来源

- 数据库: `memory/long-term/index.db` (sessions/messages 表)
- CSV: `{args.csv}`
- 生成: `scripts/intent_analysis/export_user_questions_csv.py` + `gen_intent_report.py`
"""

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"✅ 报告骨架生成: {args.out} ({total} 条)")


if __name__ == "__main__":
    main()
