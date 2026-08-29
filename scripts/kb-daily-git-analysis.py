#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# kb-daily-git-analysis.py v1 — 日报 Git 综合分析器
#
# 用途：对日报时间窗口内的 git 提交做综合分析，输出供日报
#       「Git 综合分析」模块消费的结构化 Markdown 片段。
#       识别 AI 提交（message 以 [AI] 开头）与人工提交，
#       统计提交次数、代码变更、目录热点、修改特征，并给出
#       规则驱动的改进点建议。
#
# 时间窗口：[REPORT_DATE 08:00 → (REPORT_DATE+1) 08:10]
#   - 与 kb-daily-files.sh / kb-daily-survey-scan.sh 完全对齐
#
# 用法：
#   ./scripts/kb-daily-git-analysis.py                    # 上一日
#   ./scripts/kb-daily-git-analysis.py 2026-08-06         # 指定日期
#
# 输出：
#   - stdout：Markdown 片段（供日报直接嵌入）
#   - tmp/kb-daily-git-analysis-{REPORT_DATE}.md：同内容落盘
#
# 变更日志：
#   2026-08-07 v1 created（日报升级：新增 Git 综合分析模块）
#================================================================

import subprocess
import sys
import os
import re
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta

WORKSPACE = os.path.expanduser("~/cow")


def parse_date(report_date):
    """解析报告日期，返回 (report_date, next_day)"""
    d = datetime.strptime(report_date, "%Y-%m-%d")
    return d, d + timedelta(days=1)


def git_log(report_date, next_day):
    """获取时间窗口内全部提交的原始信息"""
    after = f"{report_date}T08:00:00"
    before = f"{next_day}T08:10:00"
    cmd = [
        "git", "log",
        f"--after={after}", f"--before={before}",
        "--format=%H%x1f%an%x1f%ae%x1f%ad%x1f%s%x1f%b",
        "--date=format:%Y-%m-%d %H:%M:%S",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE)
    if result.returncode != 0:
        print(f"⚠️ git log 失败: {result.stderr}", file=sys.stderr)
        return []
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\x1f")
        if len(parts) < 6:
            continue
        commits.append({
            "hash": parts[0][:12],
            "author": parts[1],
            "email": parts[2],
            "date": parts[3],
            "subject": parts[4],
            "body": parts[5].strip(),
        })
    return commits


def classify(commit):
    """按 message 前缀分类 AI/人工提交"""
    if commit["subject"].startswith("[AI]"):
        return "AI"
    if commit["subject"].startswith("[manual]"):
        return "manual"
    return "manual"


def parse_commit_type(subject):
    """从 subject 提取 type(scope)，如 '[AI] docs(01_survey): xxx' → ('docs','01_survey')"""
    s = subject.replace("[AI]", "").replace("[manual]", "").strip()
    m = re.match(r"^([a-z]+)(?:\(([^)]*)\))?[::]\s*(.*)", s)
    if m:
        return m.group(1), (m.group(2) or "none"), m.group(3)
    # 特殊前缀（中文 emoji 型）
    m2 = re.match(r"^(📥|🔧|📦|✨|🛠|schedule)\s*(.*)", s)
    if m2:
        return "ingest", "none", m2.group(2)
    return "other", "none", s


def get_commit_stats(commits):
    """获取每个提交的文件变更统计（插入/删除行数 + 文件列表）"""
    stats = {}
    for c in commits:
        cmd = ["git", "show", "--format=", "--numstat", c["hash"]]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE)
        files = []
        total_add = total_del = 0
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                added, deleted, fpath = parts[0], parts[1], parts[2]
                try:
                    a = int(added) if added != "-" else 0
                    d = int(deleted) if deleted != "-" else 0
                except ValueError:
                    a = d = 0
                total_add += a
                total_del += d
                files.append({"path": fpath, "add": a, "del": d})
        stats[c["hash"]] = {"add": total_add, "del": total_del, "files": files}
    return stats


def render(commits, stats, report_date, next_day):
    lines = []
    total = len(commits)
    ai_commits = [c for c in commits if classify(c) == "AI"]
    manual_commits = [c for c in commits if classify(c) == "manual"]
    n_ai, n_manual = len(ai_commits), len(manual_commits)

    # 文件/行统计
    total_add = sum(s["add"] for s in stats.values())
    total_del = sum(s["del"] for s in stats.values())
    all_files = [f["path"] for s in stats.values() for f in s["files"]]
    n_files = len(set(all_files))

    # 区分业务路径与治理路径（归档/重命名/迁移噪音）
    def is_governance(path):
        return any(k in path for k in ["_archive", "/bak", "=>", "tmp/bak", "archive"])

    biz_files = [f for f in all_files if not is_governance(f)]
    gov_files = [f for f in all_files if is_governance(f)]

    # 目录热点（二级目录，排除治理噪音）
    dir_counter = Counter()
    for f in biz_files:
        parts = f.split("/")
        if len(parts) >= 2:
            dir_counter["/".join(parts[:2])] += 1
        else:
            dir_counter[parts[0]] += 1
    top_dirs = dir_counter.most_common(12)

    # 提交类型分布
    type_counter = Counter()
    scope_counter = Counter()
    for c in commits:
        t, scope, _ = parse_commit_type(c["subject"])
        type_counter[t] += 1
        scope_counter[scope] += 1

    # 提交规模分布（按变更行数）
    size_buckets = {"<50行": 0, "50-200行": 0, "200-1000行": 0, ">1000行": 0}
    for s in stats.values():
        total_lines = s["add"] + s["del"]
        if total_lines < 50:
            size_buckets["<50行"] += 1
        elif total_lines < 200:
            size_buckets["50-200行"] += 1
        elif total_lines < 1000:
            size_buckets["200-1000行"] += 1
        else:
            size_buckets[">1000行"] += 1

    # 平均每提交文件数
    avg_files = sum(len(s["files"]) for s in stats.values()) / max(total, 1)

    # 改进点（规则驱动）
    improvements = []
    # 1. 提交信息规范性
    nonstd = [c for c in commits if parse_commit_type(c["subject"])[0] == "other"]
    if nonstd:
        improvements.append(
            f"⚠️ 不规范提交信息 {len(nonstd)} 条（{len(nonstd)*100//max(total,1)}%）："
            f"建议统一为 `type(scope): summary` 格式（如 ingest/docs/fix/chore）"
        )
    # 超大提交（区分治理型 vs 业务型）
    big_commits = []
    gov_big = 0
    for c in commits:
        s = stats[c["hash"]]
        if s["add"] + s["del"] > 1000:
            paths = [f["path"] for f in s["files"]]
            if paths and all(is_governance(p) for p in paths):
                gov_big += 1
            else:
                big_commits.append((c, s))
    if big_commits:
        names = "、".join(f"`{c['subject'][:40]}...`({s['add']}+/{s['del']}-)" for c, s in big_commits[:3])
        improvements.append(f"⚠️ 业务型超大提交 {len(big_commits)} 个（>1000 行）：{names}——建议按主题拆分便于审查")
    if gov_big:
        improvements.append(f"ℹ️ 治理型超大提交 {gov_big} 个（归档/迁移/重命名，>1000 行）——批量治理属正常，建议 commit message 标注 `(governance)`")
    # 3. 无正文提交
    no_body = [c for c in commits if not c["body"]]
    if no_body and len(no_body) > total * 0.5:
        improvements.append(
            f"ℹ️ {len(no_body)}/{total} 提交无正文——重要变更建议补充文件清单/要点"
        )
    # 4. 目录集中度
    if top_dirs:
        top1_ratio = top_dirs[0][1] * 100 // max(len(all_files), 1)
        if top1_ratio > 40:
            improvements.append(
                f"⚠️ 变更高度集中在 `{top_dirs[0][0]}`（{top1_ratio}%）——"
                f"若为批量治理（重命名/格式修复）属正常，若为业务产出建议关注分布均衡"
            )
    # 5. 人工提交分布
    if n_manual == 0:
        improvements.append("ℹ️ 当日无人工提交——全部 AI 自动提交，建议抽验关键产出质量")
    elif n_manual > 0:
        pass
    # 6. AI/人工比例异常
    if n_ai > 0 and n_manual > 0:
        ratio = n_ai * 100 // max(n_ai + n_manual, 1)
        improvements.append(
            f"ℹ️ AI 提交占比 {ratio}%——健康区间约 60-90%；"
            f"过低=AI 未充分接管例行产出，过高=需关注人工校验是否充分"
        )
    if not improvements:
        improvements.append("✅ 未发现明显改进点，提交习惯健康")

    # 输出 Markdown
    lines.append(f"### 📊 Git 提交综合分析（{report_date}）")
    lines.append("")
    lines.append(f"> 统计窗口: {report_date} 08:00 → {next_day} 08:10（与日报窗口对齐）")
    lines.append("")
    lines.append(f"**总提交 {total}** | AI 自动提交 {n_ai} | 人工提交 {n_manual} | "
                 f"变更文件 {n_files}（业务 {len(set(biz_files))} + 治理 {len(set(gov_files))}）| "
                 f"插入 +{total_add} / 删除 -{total_del} 行 | 平均每提交 {avg_files:.1f} 文件")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|:-----|:----:|")
    lines.append(f"| 提交总数 | {total} |")
    lines.append(f"| AI 提交（[AI] 前缀） | {n_ai} |")
    lines.append(f"| 人工提交 | {n_manual} |")
    lines.append(f"| 变更文件数 | {n_files} |")
    lines.append(f"| 插入行数 | +{total_add} |")
    lines.append(f"| 删除行数 | -{total_del} |")
    lines.append(f"| 平均每提交文件数 | {avg_files:.1f} |")
    lines.append("")

    # AI vs 人工特征
    lines.append(f"**AI 提交特征**（{n_ai} 条）：")
    ai_types = Counter(parse_commit_type(c["subject"])[0] for c in ai_commits)
    lines.append("- " + "、".join(f"{t}×{n}" for t, n in ai_types.most_common(6)) + "（日报型批量产出为主）")
    lines.append(f"**人工提交特征**（{n_manual} 条）：")
    if manual_commits:
        man_types = Counter(parse_commit_type(c["subject"])[0] for c in manual_commits)
        lines.append("- " + "、".join(f"{t}×{n}" for t, n in man_types.most_common(6)) + "（归档/修复/配置为主）")
        # 人工提交内容示例
        samples = [f"`{c['subject'][:60]}`" for c in manual_commits[:5]]
        lines.append("- 示例：" + "；".join(samples))
    else:
        lines.append("- 无")
    lines.append("")

    # 目录热点
    lines.append(f"**目录热点 Top {min(10, len(top_dirs))}**（按变更文件数）：")
    lines.append("")
    lines.append("| 目录 | 文件数 |")
    lines.append("|:-----|:------:|")
    for d, n in top_dirs[:10]:
        lines.append(f"| `{d}` | {n} |")
    lines.append("")

    # 提交规模分布
    lines.append(f"**提交规模分布**（按变更行数）：")
    lines.append("")
    lines.append("| 规模 | 提交数 |")
    lines.append("|:-----|:------:|")
    for k, v in size_buckets.items():
        bar = "█" * (v * 20 // max(max(size_buckets.values()), 1))
        lines.append(f"| {k} | {v} {bar} |")
    lines.append("")

    # 改进点
    lines.append(f"**识别改进点（{len(improvements)} 条）**：")
    for imp in improvements:
        lines.append(f"- {imp}")
    lines.append("")

    return "\n".join(lines)


def main():
    report_date = sys.argv[1] if len(sys.argv) > 1 else (
        datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    d, next_day = parse_date(report_date)
    commits = git_log(report_date, next_day.strftime("%Y-%m-%d"))
    if not commits:
        print(f"⚠️ 时间窗口 {report_date} 08:00 → {next_day.strftime('%Y-%m-%d')} 08:10 内无提交")
        return
    stats = get_commit_stats(commits)
    md = render(commits, stats, report_date, next_day.strftime("%Y-%m-%d"))

    # 落盘
    os.makedirs(f"{WORKSPACE}/tmp", exist_ok=True)
    out_path = f"{WORKSPACE}/tmp/kb-daily-git-analysis-{report_date}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print(f"\n<!-- ✅ 已保存: {out_path} -->", file=sys.stderr)


if __name__ == "__main__":
    main()
