#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kb-dir-registry.py — 知识库目录注册表查询/检测脚本
SSOT: spec/std-005-kb-directory-registry.md（本脚本内嵌快照，两者需同步更新）

用法:
  python3 scripts/tools/kb-dir-registry.py --tree          # 目录树+性质标注（只读实际目录）
  python3 scripts/tools/kb-dir-registry.py --suggest KEY   # 按关键词/意图建议归档路径
  python3 scripts/tools/kb-dir-registry.py --diff          # 注册表 vs 实际目录树漂移检测

原则: 默认不跑脚本（skill 内置轻量规则判定），仅在批量/不确定/需全貌时使用。
"""
import json
import os
import sys
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KNOWLEDGE = os.path.join(ROOT, "knowledge")

# ── 注册表快照（与 std-005 §2/§3/§4 同步）────────────────────────────
# 格式: [顶层模块, 性质说明, [子目录...]]；子目录为 (路径, 说明) 或纯路径
REGISTRY = {
    "01_survey": {
        "desc": "调研与行业跟踪（时间序，分布式 index/log）",
        "sub": [
            ("server-hardware", "服务器硬件跟踪"), ("supernode", "超节点跟踪"),
            ("llm-trends", "大模型动态"), ("cluster-training", "万卡集群与训推"),
            ("components-storage", "存储/内存/HBM"), ("data-center", "数据中心(风火水电)"),
            ("interconnect-optics", "互联与光通信"), ("power-architecture", "电源架构(HVDC/BBU)"),
            ("chip-market", "芯片与市场格局"), ("github", "GitHub 开源活动日报"),
            ("ops-platform", "运维平台(AIOps)"), ("ops-system", "运维系统"),
        ],
    },
    "02_rd": {
        "desc": "服务器研发知识库（产品×项目矩阵）",
        "sub": [
            ("00_shared", "跨产品共享: 01_architecture/02_concepts/03_process/04_quality/05_fault-diagnosis/kbbase"),
            ("01_product", "产品研发: 00_hardware(硬件)/01_software(软件)/02_documentation(规格)"),
            ("02_project", "项目: 01_superpod/02_om-system/03_kb_cowagent"),
            ("03_hardware", "硬件专项（现仅 kv-cache）"),
            ("03_management", "研发管理: 01_product/02_project/03_team/05_supply/06_manufacturing/07_ai/08_competitive"),
            ("04_chip", "芯片: amd/base/ocp/risc-v/test"),
            ("92_patent", "专利交底书"),
        ],
    },
    "03_AI": {
        "desc": "AI 架构与生态分析",
        "sub": [
            ("agent-engineering", "Agent 工程"), ("llm-techniques-principles", "LLM 原理与技术"),
            ("ai-principles", "AI 原理"), ("knowledge-system", "知识系统"),
            ("methodology", "AI 方法论"), ("train", "培训材料"),
        ],
    },
    "04_person": {
        "desc": "个人知识管理",
        "sub": [("career", "职业"), ("cognition", "认知"), ("conflict-resolution", "冲突解决"), ("wealth", "财富")],
    },
    "05_tools": {
        "desc": "工具与技能",
        "sub": [
            ("ai-tools", "AI 工具"), ("git", "Git"), ("golang", "Go"),
            ("scrapy", "爬虫"), ("database", "数据库"), ("devops", "运维"),
            ("knowledge-management", "知识管理"), ("testing", "测试"), ("observability", "可观测性"),
        ],
    },
    "06_others": {
        "desc": "其他归档",
        "sub": [("ideas", "想法/灵感暂存(idea-vault)"), ("sources", "外部来源归档(web-archive/doubao)")],
    },
    "07_industry-research": {
        "desc": "行业研究专题（深度报告）",
        "sub": [
            ("03_server", "服务器(厂商/资本/会议/行业/储能/管理)"),
            ("04_ai", "AI 专题"), ("10_supernode-rack", "超节点/整机柜"),
            ("16_market-competition", "市场竞争"), ("18_methodology-framework", "方法论框架"),
            ("19_governance-permissions", "治理权限"), ("20_engineering-role-evolution", "工程角色演进"),
        ],
    },
    "weekly-reports": {
        "desc": "定期报告（时间序，分布式 index/log）",
        "sub": [
            ("00_daily", "日报"), ("01_weekly", "周报(周日15:00)"), ("02_monthly", "月报"),
            ("03_q", "季度"), ("04_yearly", "年度"), ("06_memory", "记忆蒸馏"),
            ("07_kb_stat", "知识库可观测与分析中心"),
            ("08_ai", "AI 归档"), ("09_other", "其他"),
        ],
    },
    "07_kb_stat": {
        "desc": "知识库可观测中心（weekly-reports 下）",
        "sub": [
            ("00.token-consumption-analysis", "资源-TOKEN 分析"),
            ("02_dir_optiz", "目录优化"), ("03_skills_scripts", "Skills/Scripts 审计"),
            ("04_task", "定时任务 RCA"), ("05_kbsys", "KB 系统分析/Bug"),
            ("06_conversation", "会话分析"), ("07_git_footstep", "Git 足迹(定时)"),
            ("08_dir_review", "目录评审"), ("99_data", "数据层(原始 metadata JSON)"),
        ],
    },
}

# ── 意图关键词 → 路径 映射（轻量规则，与 std-005 §6 对应）─────────────
INTENT_MAP = [
    # (关键词列表, 建议路径, 说明)
    (["外部", "url", "链接", "文章", "网页", "豆包", "归档"], "knowledge/06_others/sources/", "外部来源归档"),
    (["想法", "灵感", "点子", "暂存", "idea"], "knowledge/06_others/ideas/", "想法暂存"),
    (["方法论", "方法", "框架", "规范", "标准"], "spec/meth-* 或 spec/std-*", "可复用方法论/规范"),
    (["报告", "统计", "周报", "月报", "日报", "可观测"], "knowledge/weekly-reports/", "定期报告/统计"),
    (["行业", "专题", "深度报告", "五看三定"], "knowledge/07_industry-research/", "行业深度专题"),
    (["跟踪", "新闻", "动态", "调研"], "knowledge/01_survey/<主题>/", "日常调研跟踪"),
    (["gpu", "故障", "诊断", "ras", "可靠性"], "knowledge/02_rd/00_shared/05_fault-diagnosis/", "故障诊断"),
    (["硬件", "单板", "电路", "pcb", "散热", "供电"], "knowledge/02_rd/01_product/00_hardware/", "硬件研发"),
    (["芯片", "cpu", "gpu芯片", "制程"], "knowledge/02_rd/04_chip/", "芯片"),
    (["专利", "交底书", "软著"], "knowledge/02_rd/92_patent/", "专利"),
    (["超节点", "superpod", "集群", "互联"], "knowledge/02_rd/02_project/01_superpod/", "超节点项目"),
    (["管理", "项目", "团队", "供应链", "竞品"], "knowledge/02_rd/03_management/", "研发管理"),
    (["agent", "harness", "编排"], "knowledge/03_AI/agent-engineering/", "Agent 工程"),
    (["llm", "大模型", "推理", "kv"], "knowledge/03_AI/llm-techniques-principles/", "LLM 原理"),
    (["工具", "教程", "git", "golang", "爬虫"], "knowledge/05_tools/", "工具教程"),
    (["职业", "认知", "财富", "冲突"], "knowledge/04_person/", "个人管理"),
]


def tree():
    """输出实际目录树（带注册表性质标注）"""
    for top in sorted(os.listdir(KNOWLEDGE)):
        full = os.path.join(KNOWLEDGE, top)
        if not os.path.isdir(full):
            continue
        desc = REGISTRY.get(top, {}).get("desc", "")
        print(f"{top}/  {'— ' + desc if desc else ''}")
        for sub in sorted(os.listdir(full)):
            if os.path.isdir(os.path.join(full, sub)) and not sub.startswith("."):
                print(f"  ├─ {sub}/")
    if os.path.isdir(os.path.join(KNOWLEDGE, "weekly-reports", "07_kb_stat")):
        print("weekly-reports/07_kb_stat/  — 知识库可观测中心")
        for sub in sorted(os.listdir(os.path.join(KNOWLEDGE, "weekly-reports", "07_kb_stat"))):
            if os.path.isdir(os.path.join(KNOWLEDGE, "weekly-reports", "07_kb_stat", sub)):
                print(f"  ├─ {sub}/")


def suggest(keyword):
    """按关键词/意图建议路径"""
    kw = keyword.lower()
    hits = []
    for kws, path, note in INTENT_MAP:
        if any(k in kw for k in kws):
            hits.append((path, note))
    if hits:
        print(f"🔍 「{keyword}」 建议路径（命中 {len(hits)} 条规则）:")
        for path, note in hits:
            print(f"  → {path}  ({note})")
    else:
        print(f"🔍 「{keyword}」 未命中意图规则，按目录性质判定：")
        for top, info in REGISTRY.items():
            if kw in top or any(kw in s[0] if isinstance(s, tuple) else kw in s for s in info["sub"]):
                print(f"  → knowledge/{top}/  ({info['desc']})")
    print("\n💡 仍不确定 → knowledge/06_others/ + 头部 `> Pending: 待重新分类`")


def diff():
    """注册表 vs 实际目录树漂移检测"""
    print("═" * 60)
    print("注册表中有、实际不存在的目录（注册表需删/改）:")
    found = False
    for top, info in REGISTRY.items():
        if top == "07_kb_stat":
            base = os.path.join(KNOWLEDGE, "weekly-reports", "07_kb_stat")
            if not os.path.isdir(base):
                print(f"  ❌ knowledge/weekly-reports/07_kb_stat/")
                found = True
        else:
            base = KNOWLEDGE
            if not os.path.isdir(os.path.join(base, top)):
                print(f"  ❌ knowledge/{top}/")
                found = True
        for sub in info["sub"]:
            subname = sub[0] if isinstance(sub, tuple) else sub
            subpath = os.path.join(base, subname) if top == "07_kb_stat" else os.path.join(base, top, subname)
            if not os.path.isdir(subpath):
                shown = f"knowledge/weekly-reports/07_kb_stat/{subname}/" if top == "07_kb_stat" else f"knowledge/{top}/{subname}/"
                print(f"  ❌ {shown}")
                found = True
    if not found:
        print("  ✅ 注册表目录全部存在")
    print("\n实际存在、注册表未登记的目录（注册表需补充）:")
    found = False
    for top in sorted(os.listdir(KNOWLEDGE)):
        if top in REGISTRY or top in ("index.md", "log.md", "README.md"):
            continue
        if os.path.isdir(os.path.join(KNOWLEDGE, top)):
            print(f"  ⚠️ knowledge/{top}/")
            found = True
    if not found:
        print("  ✅ 无未登记目录")


def main():
    ap = argparse.ArgumentParser(description="知识库目录注册表查询/检测")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tree", action="store_true", help="输出目录树")
    g.add_argument("--suggest", metavar="KEY", help="按关键词建议路径")
    g.add_argument("--diff", action="store_true", help="漂移检测")
    args = ap.parse_args()
    if args.tree:
        tree()
    elif args.suggest:
        suggest(args.suggest)
    elif args.diff:
        diff()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"⚠️ 执行失败: {e}", file=sys.stderr)
        sys.exit(1)
