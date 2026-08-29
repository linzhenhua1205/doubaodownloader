#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# kb-daily-survey-coverage.py v1 — 日报 调研领域覆盖检查器
#
# 用途：扫描 knowledge/01_survey/ 各调研领域在日报时间窗口内的
#       产出情况，输出覆盖矩阵。供日报「调研跟踪摘要」模块判断
#       「全面覆盖」是否达成——哪些领域有产出、哪些空白、哪些
#       仅占位，并提示当日未被覆盖但应在跟踪清单内的领域。
#
# 时间窗口：[REPORT_DATE 08:00 → (REPORT_DATE+1) 08:10]
#   匹配策略：匹配 REPORT_DATE* 和 REPORT_DATE+1* 两类文件名
#   （与 kb-daily-survey-scan.sh 一致，覆盖 00:00~08:10 时段）
#
# 用法：
#   ./scripts/kb-daily-survey-coverage.py                    # 上一日
#   ./scripts/kb-daily-survey-coverage.py 2026-08-06         # 指定日期
#
# 输出：
#   - stdout：Markdown 覆盖矩阵（供日报直接嵌入）
#   - tmp/kb-daily-survey-coverage-{REPORT_DATE}.md：同内容落盘
#
# 变更日志：
#   2026-08-07 v1 created（日报升级：调研领域覆盖检查）
#================================================================

import os
import sys
import re
from datetime import datetime, timedelta

WORKSPACE = os.path.expanduser("~/cow")
SURVEY_ROOT = os.path.join(WORKSPACE, "knowledge", "01_survey")

# 调研领域清单（SSOT，与 research_topics.json / 定时任务对齐）
DOMAINS = [
    ("ai-apps", "AI应用", "🤖"),
    ("ai-frameworks", "AI框架", "🧩"),
    ("ai-solutions", "智算方案", "🏛️"),
    ("ai-dev-tools", "AI研发工具", "🛠️"),
    ("bmc-system", "BMC系统", "⚙️"),
    ("bom-supply-chain", "BOM成本与供应链", "🏭"),
    ("chip-market", "芯片与市场格局", "🏭"),
    ("cloud-native", "云原生", "☸️"),
    ("cluster-training", "集群训练", "⚡"),
    ("components-storage", "部件存储", "💾"),
    ("compute-platform", "算力平台", "🧮"),
    ("data-analysis", "数据分析", "📊"),
    ("data-center", "数据中心", "🏭"),
    ("distributed-os", "分布式OS", "🔗"),
    ("enterprise-mgmt", "企业/产品管理", "🎯"),
    ("github", "GitHub开源", "📊"),
    ("industry-research", "行业调研", "📊"),
    ("interconnect-optics", "互联光通信", "🔀"),
    ("internet-infra", "互联网大厂基础设施", "🏢"),
    ("linux-os", "Linux OS", "🐧"),
    ("llm-trends", "大模型动态", "🧠"),
    ("moe-hardware", "MoE→硬件", "🏭"),
    ("ops-platform", "运维平台", "🛠️"),
    ("ops-system", "运维运营", "🛠️"),
    ("policy-industry", "政策与产业", "🏛️"),
    ("power-architecture", "电源架构", "⚡"),
    ("product-dev", "产品研发", "🏭"),
    ("project-mgmt", "项目管理", "📐"),
    ("rd-management", "研发管理", "📋"),
    ("reliability-testing", "可靠性测试", "🔬"),
    ("server-form-factor", "服务器形态散热", "🏭"),
    ("server-hardware", "服务器硬件", "🖥️"),
    ("standards-finance-media", "标准财经媒体", "📐"),
    ("supernode", "超节点", "🌟"),
    ("switch", "交换机AI网络", "🔀"),
    ("tools", "工具", "🛠️"),
    ("vendor-ecosystem", "厂商运营商生态", "🏭"),
]


def collect_domains():
    """从 01_survey/ 实际目录动态收集领域（以实际为准，DOMAINS 为兜底）"""
    actual = set()
    if os.path.isdir(SURVEY_ROOT):
        actual = {d for d in os.listdir(SURVEY_ROOT)
                  if os.path.isdir(os.path.join(SURVEY_ROOT, d)) and not d.startswith(".")}
    return actual


def scan_window(report_date, next_day):
    """扫描窗口内各领域产出文件"""
    coverage = {}  # domain -> list of (file, size)
    # 匹配两类日期前缀
    prefixes = (report_date, next_day)
    for domain in collect_domains():
        dpath = os.path.join(SURVEY_ROOT, domain)
        files = []
        try:
            for fname in os.listdir(dpath):
                if not fname.endswith(".md"):
                    continue
                if any(fname.startswith(p) for p in prefixes):
                    fpath = os.path.join(dpath, fname)
                    size = os.path.getsize(fpath)
                    lines = sum(1 for _ in open(fpath, encoding="utf-8", errors="ignore"))
                    files.append((fname, size, lines))
        except FileNotFoundError:
            pass
        coverage[domain] = files
    return coverage


def render(coverage, report_date, next_day):
    lines = []
    produced = [(d, f) for d, fl in coverage.items() for f in fl]
    n_produced = len(produced)
    n_domains = len(coverage)
    n_blank = sum(1 for d, fl in coverage.items() if not fl)

    lines.append(f"### 📡 调研领域覆盖检查（{report_date}）")
    lines.append("")
    lines.append(f"> 窗口: {report_date} 08:00 → {next_day} 08:10 | "
                 f"覆盖 {n_domains} 领域 | 有产出 {n_produced} 个文件 | 空白领域 {n_blank} 个")
    lines.append("")
    lines.append("| 领域 | 产出 | 规模 |")
    lines.append("|:-----|:----:|:-----|")
    for d, fl in sorted(coverage.items()):
        name = d
        for dom, label, emoji in DOMAINS:
            if dom == d:
                name = f"{emoji} {label}"
                break
        if fl:
            fname, size, lcount = max(fl, key=lambda x: x[1])  # 取最大文件
            lines.append(f"| {name} | ✅ {len(fl)} | {fname[11:16]}·{lcount}行 |")
        else:
            lines.append(f"| {name} | ⬜ 空白 | — |")
    lines.append("")

    # 空白领域提示（供 AI 判断是否需补充调研）
    blank_domains = [d for d, fl in sorted(coverage.items()) if not fl]
    if blank_domains:
        blank_names = "、".join(
            next((f"{e}{l}" for dom, l, e in DOMAINS if dom == d), d)
            for d in blank_domains
        )
        lines.append(f"**空白领域（{len(blank_domains)}）**: {blank_names}")
        lines.append("> 💡 空白原因可能=无增量/任务未执行/源不可达，AI 判断是否需补采或标注")
        lines.append("")
    else:
        lines.append("**✅ 全部领域有产出，覆盖完整**")
        lines.append("")
    return "\n".join(lines)


def main():
    report_date = sys.argv[1] if len(sys.argv) > 1 else (
        datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (datetime.strptime(report_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    coverage = scan_window(report_date, next_day)
    md = render(coverage, report_date, next_day)

    os.makedirs(f"{WORKSPACE}/tmp", exist_ok=True)
    out_path = f"{WORKSPACE}/tmp/kb-daily-survey-coverage-{report_date}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print(f"\n<!-- ✅ 已保存: {out_path} -->", file=sys.stderr)


if __name__ == "__main__":
    main()
