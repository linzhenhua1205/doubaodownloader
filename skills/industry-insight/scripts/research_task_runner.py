#!/usr/bin/env python3
"""
调研定时任务统一执行器 v1.4
===========================

职责: 把散落在 tasks.json 任务描述中的调研规则（源发现/源可靠性/文档质量/内容丰度/
文档格式/输出可靠性/token管理/占位文件/index-log更新）全部下沉到本脚本；**主题配置
（任务ID→搜索源/输出路径/丰度阈值）独立存放于 configs/research_topics.json**，
脚本只负责加载与执行，改配置无需改脚本。

v1.4 变更: 专题独立输出硬规则——10 任务输出从共享文件 industry-research/YYYY-MM-DD.md 拆分为
各自专题目录（组任务→industry-research/<group>/）；update-log 支持子目录相对链接。

v1.5 变更: update-log 自动从当日生产文件提取摘要（前 3 条发现标题），消除悬空" —"空摘要
（08-05/08-06 两次事故：条目以" —"结尾无摘要需人工补全；现提取失败则不写" — "）。

v1.6 变更: URL 真实性硬规则（08-11 教训：3 条推测格式 URL 全 404 且站内搜索 Nothing Found）——
guide ④ 新增「URL 必须来自实际抓取内容、禁止推测编造、写入前逐条 curl 验证 HTTP 200」；verify 增补
URL真实性 INFO 提醒（仅计数不校验可访问性，真实性靠写入前 curl 验证兜底）。

v1.7 变更: 跨组去重硬规则（08-15 教训：hardware/tech/market 三组同日并行致 13 条跨组重复，被迫重写文件+重跑 verify/log/index）——
文档质量要求 + guide ④ 新增「写入前必须 grep 其他组同日文件，已被收录条目→本组剔除+逐条诚实标注，只留本组视角增量」。

v1.8 变更: 分档规则 + 去重软化（08-17 教训: 深度分析被追踪约束压缩——switch 08-11 深度 18.5KB → 08-17 缩至 7.6KB，supernode 两日连降）——
① 产出分档: config 新增 depth 字段（track 默认/深度档可选），deep 档输出≥30KB 无上限/总预算≤60K/可读全文/丰度多维校验（列表+段落+表格），track 档维持 ≤15KB/≤20K/读前30行；
② 跨组去重软化: 「剔除+逐条诚实标注」→「一行交叉引用（已由<组名>收录）」，把篇幅留给本组视角增量。

v1.3 变更: 主题配置从脚本内 TASKS 常量迁移至 configs/research_topics.json；
新增 3 主题（交换机与AI网络/算力平台/运维平台），覆盖服务器/交换机产销研、
算力平台、运维平台与 AI 全栈技术点；支持按任务名模糊匹配 task_id。

使用方式（定时任务 AI 按序执行）:
    python3 research_task_runner.py plan        --task <task_id|任务名>  # ① 生成搜索计划
    ... 按计划用 web_fetch 逐源抓取（每源 1 次，失败跳过）...
    python3 research_task_runner.py register    --task <id> --source <源名> --success|--fail
    python3 research_task_runner.py scaffold    --task <id>   # ② 生成当日文件骨架/章节定位
    ... 将发现写入输出文件（格式/丰度规则见 verify）...
    python3 research_task_runner.py verify      --task <id>   # ③ 输出可靠性/质量/丰度/格式校验
    python3 research_task_runner.py update-log  --task <id>   # ④ 定时调研不写日志（no-op，2026-08-19 起；深度分析走 kb-log-append.py 追加根 log.md）
    python3 research_task_runner.py placeholder --task <id>   # 零产出 → 占位文件
    python3 research_task_runner.py check-gap   --task <id>   # 缺失自愈检查（>=3天升级策略）
    python3 research_task_runner.py guide       --task <id>   # 输出完整执行链（任务描述入口）
    python3 research_task_runner.py list                      # 列出全部任务配置

内建规则（所有任务统一适用）:
────────────────────────────────────────────────────────────────────────
[token 管理·分档（v1.8）]
  · 每个搜索源最多抓取 1 次，失败立即跳过，绝不重试、不换词反复搜索
  · 追踪档(track): 读前 30 行（标题/摘要/关键段落）· 输出 ≤ 15KB · 总预算 ≤ 20K（含计划与校验）
  · 深度档(deep): 可读全文 · 输出目标 ≥30KB 无上限 · 总预算 ≤ 60K（档位由配置 depth 字段控制）
[源可靠性管理]
  · 源优先级: 官方/厂商文档 > 行业媒体(STH/TrendForce/DCD) > 聚合博客/论坛
  · 每条发现必须携带来源 URL（http/https 链接），无链接视为不可信不采纳
  · register 记录每个源的 success/fail，连续失败源进入降级名单（见 tracker health）
[文档质量要求]
  · 每条发现格式: - **来源/标题**（YYYY-MM-DD）: 核心要点（含量化数据；无量化→标注"无量化"）
  · 只记录「有增量价值」的信息（新数据/新动态/新观点），与已有内容重复的不写
  · 去重必须 grep 本专题目录**全量历史期**（所有 YYYY-MM-DD*.md，勿只查近期几期）：
    grep -li "<标题/关键短语>" knowledge/01_survey/<topic>/*.md（含更早月份文件）
    命中即先读原文确认归档深度；已完整归档 → 本期零增量/只记新增细节，禁止再次作为「新发现/新线索」写入
  · **跨组去重（v1.8 软化，08-15 教训: 13 条跨组重复被迫重写）**: 组任务（hardware/tech/market）同日并行执行，
    写入前必须检查**其他组的同日文件**（knowledge/01_survey/industry-research/<其他组>/YYYY-MM-DD.md）：
    条目已被其他组收录 → 本组不再展开，但**用一行交叉引用保留入口**「（已由<组名>收录: <标题>）」
    ——只写一行链接不写大段剔除说明，把篇幅留给本组视角增量；禁跳过检查，写入后 verify 前再复核
  · 关键量化数据（算力/带宽/价格/市占率）须保留原始数值+单位+条件，不二次加工
[内容丰度要求]
  · 每专题/任务至少 min_finds 条有效发现（组任务 3 条/专题，单主题 2 条/任务）
  · 达标不足 → 在专题末尾标注「信息不足」，不许凑数
  · 全部零产出 → 运行 placeholder 生成占位文件（保证日报审计可见）
[文档生成格式]
  · **专题独立输出（硬规则）**: 每个专题任务输出到**自己的目录**（configs/research_topics.json 中 out 指定），
    严禁写入他人目录或共享文件；组任务输出到 industry-research/<group>/ 子目录
  · 共享文件（industry-research/YYYY-MM-DD.md 历史遗留）: 已废弃，不再追加新内容
  · 独立文件（<module>/YYYY-MM-DD.md）: 不存在则用 scaffold 生成标准头部，再写入发现
  · 标准头部含: 执行时间/采集源/源健康/专题概览表（组任务）
[输出可靠性确认]
 · verify 逐项检查: 文件存在 → 非空 → 含来源URL → 丰度达标 → 格式合规
 · 任一 FAIL → 立即修复后重跑 verify，直到全部 PASS 才结束
 · URL 真实性硬规则（08-11 教训: 3 条推测格式 URL 全 404 且站内搜索 Nothing Found）: 每条 URL 必须来自实际抓取内容
   （web_fetch 原文 / curl 提取 HTML / 站内搜索命中），严禁按 URL 格式推测/编造；写入前逐条 curl 验证 HTTP 200，
   404 或站内搜索无法命中的条目必须删除，不得以「看起来像」保留
 · verify 的「含来源URL」仅校验存在性/计数，不校验可访问性——真实性靠写入前 curl 验证兜底
 · 占位文件（含「搜索摘要（无新增内容）」标记）豁免非空/含URL 两项硬校验（08-05 起）
[配套 index/log 修改]
  · update-log 自动把当日记录追加到 knowledge/log.old.md（分节 `### 01_survey/<module> · YYYY-MM-DD`）
  · 2026-08-19 起 01_survey 不再维护分布式 index.md/log.md（已移除），index 登记废弃
  · 无需 AI 手工维护 index，避免格式漂移
[零产出占位]
  · placeholder 生成「📋 搜索摘要（无新增内容）」占位文件，参与日报统计
  · 连续 3 天零产出 → check-gap 提示升级策略（源+2、词×2组、失败可重试1次）
────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

# ============================================================
# 配置加载（主题配置独立于脚本，见 configs/research_topics.json）
# ============================================================
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "configs", "research_topics.json",
)

def load_tasks() -> dict:
    """从 JSON 配置加载全部任务配置。配置缺失/损坏时报错退出（防止静默降级）。"""
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ 主题配置文件缺失: {CONFIG_PATH}")
        print("   请检查 skills/industry-insight/configs/research_topics.json 是否存在")
        sys.exit(1)
    try:
        data = json.load(open(CONFIG_PATH, encoding="utf-8"))
    except Exception as e:
        print(f"❌ 主题配置解析失败: {e}")
        print(f"   配置文件: {CONFIG_PATH}")
        sys.exit(1)
    tasks = data.get("tasks")
    if not isinstance(tasks, dict) or not tasks:
        print("❌ 主题配置缺少 tasks 对象或为空")
        sys.exit(1)
    return tasks


TASKS = load_tasks()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TMP_DIR = os.path.join(BASE_DIR, "tmp")


def resolve_task_id(arg: str) -> str:
    """task_id 解析：支持 8 位 ID 或任务名唯一匹配（防手误，配置变更不改任务描述）。"""
    if arg in TASKS:
        return arg
    matches = [tid for tid, cfg in TASKS.items() if cfg.get("name") == arg]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"❌ 任务名「{arg}」匹配到多个任务: {matches}，请用 task_id 指定")
        sys.exit(1)
    print(f"❌ 未知任务ID/名称: {arg}")
    print(f"   可用: {', '.join(sorted(TASKS.keys()))}")
    print("   或运行 list 查看任务名与 ID 对照")
    sys.exit(1)


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def resolve_out(cfg: dict) -> str:
    """解析输出路径，YYYY-MM-DD 替换为当天日期。"""
    return os.path.join(BASE_DIR, cfg["out"].replace("YYYY-MM-DD", today()))


def module_of(cfg: dict) -> str:
    """从输出路径推断 module 名（用于 log/index 更新）。"""
    m = re.search(r"knowledge/01_survey/([^/]+)/", cfg["out"])
    return m.group(1) if m else "industry-research"


OPINION_KEYWORDS = ("观点", "业界观点", "商业观点", "供应链观点", "技术观点")


def is_opinion_section(name: str) -> bool:
    """True if the section name is an opinion-collection dimension (v1.6)."""
    return "观点" in (name or "")


def depth_of(cfg: dict) -> str:
    """产出档位: track（追踪档, 默认）| deep（深度档）。

    v1.8 分档规则（08-17 教训: 深度分析被追踪约束压缩）:
    · track = 轻量高频日报: 输出≤15KB / 总预算≤20K / 每源读前30行
    · deep  = 深度分析档:   输出目标≥30KB 无上限 / 总预算≤60K / 可读全文
    · 档位由配置 depth 字段控制，缺省 track；guide/plan/verify 按档位差异化提示
    """
    return cfg.get("depth", "track")


def depth_budget(cfg: dict) -> dict:
    """按档位返回 token/读取/大小预算。"""
    if depth_of(cfg) == "deep":
        return {
            "label": "深度档(deep)",
            "out_max_kb": None,        # 无上限，目标≥30KB
            "out_min_kb": 15.0,        # 低于 15KB 视为未达深度
            "read_lines": "全文（不截断）",
            "token_budget": "≤60K",
            "target_hint": "目标≥30KB：展开因果链/对比表/原理分析，勿压缩成短列表",
        }
    return {
        "label": "追踪档(track)",
        "out_max_kb": 15.0,
        "out_min_kb": 0.5,
        "read_lines": "前30行",
        "token_budget": "≤20K",
        "target_hint": "轻量高频：每条发现精炼，总量≤15KB",
    }


# ============================================================
# 子命令实现
# ============================================================

def cmd_plan(args):
    cfg = TASKS[args.task]
    out = resolve_path_display(cfg)
    print(f"=== 调研计划: {cfg['name']} [{args.task}] ===")
    print(f"推荐 Skill: {cfg['skill']}")
    print(f"输出路径: {cfg['out'].replace('YYYY-MM-DD', today())}  (专题独立目录，保持不变)")
    print(f"[硬规则] 只写入本任务自己的输出目录，严禁写入他人目录或共享文件")
    if cfg.get("kind") == "group":
        print(f"分组: {cfg['group']} | 专题数: {len(cfg['sections'])} | 每专题最低 {cfg['min_finds']} 条")
        print(f"第一步: python3 scripts/industry-research-tracker.py collect --group {cfg['group']}")
        print("        → 查看 tmp/industry-tracker-<group>-*.json 获取 URL 列表")
        print("        → 逐 URL 用 web_fetch 抓取（每源 1 次，失败跳过）")
        print("专题覆盖:")
        for i, s in enumerate(cfg["sections"], 1):
            tag = " [观点]" if is_opinion_section(s) else ""
            print(f"  {i}. {s}{tag}")
        opinion = [s for s in cfg["sections"] if is_opinion_section(s)]
        if opinion:
            print("[观点采集规范·v1.6] 观点维度 section 执行要求:")
            print("  · 定位: 收集**业界观点/判断/争论**（非新闻罗列），每条=一个观点主题")
            print("  · 来源分级: 行业专家(CEO/CTO/首席分析师/架构师/一线工程负责人) > 顶级专业媒体"
                  "(STH/The Next Platform/SemiAnalysis/爱集微/半导体行业观察/电子工程专辑) > 顶级会议"
                  "(OCP Summit/Hot Chips/SC/FMS/DTW/ISSCC/各类论坛演讲与 Q&A)")
            print("  · **正反两面**: 每个观点必须尝试找对立面——先记正方（支持方及其论据），再找反方/风险/质疑"
                  "（谁反对、为什么、什么条件下会反转）；找不到反方时明确标注「未见公开反对意见」")
            print("  · 时效优先: 技术动态优先感知近 3 日新发布/新路线/新标准；观点类可含本周内专家访谈/圆桌/财报电话会")
            print("  · 输出格式: - **<观点主题>**: 正方(<专家/媒体>,<来源URL>)——<论据>；"
                  "反方/风险(<专家/媒体>,<来源URL>)——<论据>；辨析:<本库判断/证据倾向>")
            print("  · verify 要求: 观点 section 至少 1 条含正反标记（正方/反方·支持/质疑·看多/看空），否则 WARN")
    else:
        print(f"搜索源 ({len(cfg['sources'])} 个, 每源仅 1 次, 失败立即跳过不重试):")
        for i, s in enumerate(cfg["sources"], 1):
            print(f"  {i}. {s}")
    if cfg.get("section"):
        print(f"输出章节: 追加到「{cfg['section']}」小节")
    b = depth_budget(cfg)
    print(f"\n[token 预算·{b['label']}] 每源≤1次抓取 · 读{b['read_lines']} · 输出{b['out_max_kb'] or '无上限'}KB · 总预算{b['token_budget']} tokens")
    print(f"  → {b['target_hint']}")
    print("[源可靠性] 官方>行业媒体>博客 · 每条发现必须含来源URL")
    print("[官网子页] 官网首页源若无新内容 → 改抓其 Blog/Press Room 子页(/blog /news /press)，公告/预告常只挂在子页（08-06 教训: UALink FMS 演讲预告仅见于 Blog 子页，首页 6 日无更新）")
    print("[执行链] plan → web_fetch×N → register → scaffold → 写入 → verify → update-log")
    print("[零产出] 全部无有效信息 → placeholder（规则内建）")


def resolve_path_display(cfg):
    """用于 plan 显示（不做文件系统解析）"""
    return cfg["out"].replace("YYYY-MM-DD", today())


def cmd_register(args):
    cfg = TASKS[args.task]
    os.makedirs(TMP_DIR, exist_ok=True)
    rec_file = os.path.join(TMP_DIR, f"research-src-{today()}.json")
    records = []
    if os.path.exists(rec_file):
        try:
            records = json.load(open(rec_file))
        except Exception:
            records = []
    records.append({
        "task": args.task, "name": cfg["name"], "source": args.source,
        "result": "success" if args.success else "fail",
        "ts": datetime.now().strftime("%H:%M"),
    })
    json.dump(records, open(rec_file, "w"), ensure_ascii=False, indent=1)
    ok = sum(1 for r in records if r["result"] == "success")
    print(f"[register] {cfg['name']} · {args.source} → {'✅' if args.success else '❌'} "
          f"(当日累计: {ok}成功/{len(records)-ok}失败)")


def cmd_scaffold(args):
    cfg = TASKS[args.task]
    out = resolve_out(cfg)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if cfg.get("kind") == "group":
        if os.path.exists(out):
            print(f"[scaffold] 共享文件已存在: {os.path.relpath(out, BASE_DIR)}")
            print(f"  → 不重建。检查以下专题小节是否已存在，缺失的追加到文件末尾:")
            for s in cfg["sections"]:
                print(f"    - {s}")
        else:
            lines = [
                f"# 📊 行业调研综合日报 ({today()})",
                "",
                f"> **执行时间**: {today()} CST",
                f"> **任务**: {cfg['name']} · 分组 {cfg['group']}",
                "",
                "---",
                "",
            ]
            for s in cfg["sections"]:
                if is_opinion_section(s):
                    lines += [f"## {s}", "",
                              "- **<观点主题1>**: 正方(<专家/媒体>,<来源URL>)——<论据>；反方/风险(<专家/媒体>,<来源URL>)——<论据>；辨析:<本库判断>",
                              "- （待填充：至少 1 条含正反标记，来源=行业专家/顶级专业媒体/顶级会议）", ""]
                else:
                    lines += [f"## {s}", "", "- （待填充）", ""]
            with open(out, "w") as f:
                f.write("\n".join(lines))
            print(f"[scaffold] 已创建共享文件骨架: {os.path.relpath(out, BASE_DIR)}")
    else:
        section = cfg.get("section")
        if section:
            if os.path.exists(out):
                print(f"[scaffold] 共享文件已存在: {os.path.relpath(out, BASE_DIR)}")
                print(f"  → 追加到「{section}」小节（若无此小节则在文件末尾新建）")
            else:
                with open(out, "w") as f:
                    f.write(f"# 📊 行业调研综合日报 ({today()})\n\n---\n\n")
                print(f"[scaffold] 已创建共享文件: {os.path.relpath(out, BASE_DIR)}")
        else:
            if os.path.exists(out):
                print(f"[scaffold] 独立文件已存在: {os.path.relpath(out, BASE_DIR)}")
                print("  → 直接追加今日发现（新增日期小节）")
            else:
                with open(out, "w") as f:
                    f.write(f"# {cfg['name']} ({today()})\n\n"
                            f"> **执行时间**: {today()} CST\n"
                            f"> **任务**: {cfg['name']}\n\n---\n\n")
                print(f"[scaffold] 已创建独立文件骨架: {os.path.relpath(out, BASE_DIR)}")


def cmd_verify(args):
    cfg = TASKS[args.task]
    out = resolve_out(cfg)
    checks = []
    if not os.path.exists(out):
        checks.append(("FAIL", "文件不存在", f"请先运行 scaffold 或写入内容: {out}"))
        print_verify_result(cfg, checks, args.task)
        sys.exit(1)
    content = open(out).read()
    # 占位文件（零产出）豁免非空/URL 硬校验（08-05 教训：placeholder 模板仅 ~0.4KB 且无 URL，
    # 若按常规 FAIL 会与「零产出 → 生成占位」内建流程自相矛盾，曾致每日零产出日需手工增强占位）
    is_placeholder = "搜索摘要（无新增内容）" in content
    # 观点双向校验（v1.6）: 观点维度 section 至少 1 条含正反标记
    if not is_placeholder and cfg.get("kind") == "group":
        opinion_sections = [s for s in cfg.get("sections", []) if is_opinion_section(s)]
        if opinion_sections:
            bi_markers = ("正方", "反方", "支持", "质疑", "看多", "看空", "利好", "利空", "pro:", "con:")
            opinion_ok = any(m in content for m in bi_markers)
            checks.append(("PASS" if opinion_ok else "WARN", "观点双向",
                           "观点 section 需含正反标记（正方/反方·支持/质疑·看多/看空），当前未检测到"
                           if not opinion_ok else f"检测到正反标记（{', '.join(m for m in bi_markers if m in content)[:40]}）"))
    size_kb = len(content.encode("utf-8")) / 1024
    checks.append(("PASS" if (size_kb > 0.5 or is_placeholder) else "FAIL", "文件非空",
                   f"{size_kb:.1f}KB" + ("" if size_kb > 0.5 else " (过小，疑似空壳)")))
    # 来源URL检查
    urls = re.findall(r"https?://[^\s\)\]>]+", content)
    checks.append(("PASS" if (urls or is_placeholder) else "FAIL", "含来源URL",
                   f"{len(urls)} 个链接" if urls else "无任何 http 链接，不可信"))
    # URL 真实性提醒（08-11 教训：本项仅校验存在性/计数，不校验可访问性；
    # 真实性须在写入前逐条 curl 验证 HTTP 200 / 站内搜索命中，404 或 Nothing Found 的条目应删除）
    if urls and not is_placeholder:
        checks.append(("INFO", "URL真实性",
                       "verify 仅计数不校验可访问性——真实性须在写入前逐条 curl 验证（200/站内搜索命中），404 或 Nothing Found 条目应删除"))
    # 丰度检查（v1.8 多维统计: 列表项 + 分析段落 + 表格行，深度档要求更高）
    finds = len(re.findall(r"^\s*[-*]\s+\*?\*?", content, re.M))
    paras = len(re.findall(r"\n\n[^#\n>][^\n]*[。:：]?\n", content))
    tables = len(re.findall(r"^\|", content, re.M))
    min_finds = cfg["min_finds"] * (len(cfg["sections"]) if cfg.get("per_section") else 1)
    is_deep = depth_of(cfg) == "deep"
    if is_deep:
        # 深度档: 列表项达标 + 至少 3 段分析性段落（防列表化浅文）
        ok = finds >= min_finds and paras >= 3
        detail = (f"{finds} 条发现 / {paras} 段分析 / {tables} 表格行"
                  if ok else
                  f"{finds} 条发现 / {paras} 段分析（需≥3段因果/对比展开，防列表化浅文）")
        checks.append(("PASS" if ok else "WARN", "内容丰度", detail))
    else:
        checks.append(("PASS" if finds >= min_finds else "WARN", "内容丰度",
                       f"{finds} 条发现 ≥ {min_finds} 最低要求" if finds >= min_finds
                       else f"{finds} 条 < {min_finds}，信息不足需标注或补采"
                            + "（丰度统计行首 `-`/`*` 列表项；编号列表/表格不计入——请把要点改写为 `-` 列表项后重跑 verify）"))
    # 占位检测（若只有占位模板则视为零产出）
    if is_placeholder:
        checks.append(("INFO", "零产出占位", "该文件为占位文件（无新增内容），豁免非空/URL 硬校验，符合零产出规则"))
    # 大小限制（v1.8 分档: track≤15KB；deep 无上限但提示深度目标）
    b = depth_budget(cfg)
    if b["out_max_kb"] is None:
        # 深度档: 无上限，低于 15KB 提示未达深度目标
        checks.append(("PASS" if size_kb >= b["out_min_kb"] else "WARN", "文件大小",
                       f"{size_kb:.1f}KB" + ("" if size_kb >= b["out_min_kb"]
                       else f" < 深度档目标 {b['out_min_kb']:.0f}KB，检查是否被压缩")))
    else:
        checks.append(("PASS" if size_kb <= b["out_max_kb"] else "WARN", "文件大小",
                       f"{size_kb:.1f}KB" + ("" if size_kb <= b["out_max_kb"]
                       else f" > {b['out_max_kb']:.0f}KB 预算，检查是否过度采集")))
    print_verify_result(cfg, checks, args.task)


def print_verify_result(cfg, checks, task_id=""):
    print(f"=== verify: {cfg['name']} [{task_id}] ===")
    n_fail = 0
    for status, item, detail in checks:
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}[status]
        print(f"  {icon} [{status}] {item}: {detail}")
        if status == "FAIL":
            n_fail += 1
    if n_fail:
        print(f"\n❌ {n_fail} 项 FAIL，必须修复后重跑 verify 直到全部 PASS")
    else:
        print("\n✅ 校验通过，可执行 update-log 完成归档")


def cmd_placeholder(args):
    cfg = TASKS[args.task]
    out = resolve_out(cfg)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rec_file = os.path.join(TMP_DIR, f"research-src-{today()}.json")
    sources_summary = "无记录"
    if os.path.exists(rec_file):
        try:
            records = json.load(open(rec_file))
            mine = [r for r in records if r["task"] == args.task]
            if mine:
                sources_summary = " ".join(f"[{r['source']}: {'ok' if r['result']=='success' else 'fail'}]" for r in mine)
        except Exception:
            pass
    # 找上次有产出日
    last = last_production_date(cfg)
    # 召回率自查（08-04 教训）：08-03 曾以 20 篇窄查询判零产出，08-04 放宽到 30 篇后
    # 补录回 9 篇 07-19~07-30 漏网论文——零产出前必须先放宽查询再下结论。
    print("[placeholder] ⚠️ 零产出前请先做召回率自查：arXiv 查询窗口扩至≥1个月 / max_results≥30 / 关键词 2 组变体；确认无遗漏后才生成占位")
    content = (
        f"## 📋 搜索摘要（无新增内容）\n"
        f"- **执行时间**: {today()} CST\n"
        f"- **搜索源**: {sources_summary}\n"
        f"- **结论**: 未发现值得归档的有效信息\n"
        f"- **召回率自查**: 已放宽查询（窗口≥1个月 / max_results≥30 / 关键词2组变体）仍无新增，才判定零产出\n"
        f"- **上次有产出日**: {last or '无记录'}\n"
    )
    if os.path.exists(out):
        with open(out, "a") as f:
            f.write("\n\n" + content)
        mode = "追加到"
    else:
        with open(out, "w") as f:
            f.write(f"# 📋 调研占位记录 ({today()})\n\n---\n\n" + content)
        mode = "创建"
    print(f"[placeholder] 零产出占位已{mode}: {os.path.relpath(out, BASE_DIR)}")


def last_production_date(cfg):
    """查找该任务输出目录下最近的 YYYY-MM-DD 生产文件（排除 index/log/占位）。"""
    d = os.path.dirname(resolve_out(cfg))
    if not os.path.isdir(d):
        return None
    dates = []
    for fn in os.listdir(d):
        if fn in ("index.md", "log.md") or "搜索摘要" in fn:
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})", fn)
        if m:
            # 跳过占位文件（零产出记录），只统计真正有产出的日期；
            # 否则占位日会把自己当天文件误判为"上次有产出日"（08-03 事故）。
            fp = os.path.join(d, fn)
            try:
                if "搜索摘要（无新增内容）" in open(fp, encoding="utf-8").read(2000):
                    continue
            except Exception:
                pass
            dates.append(m.group(1))
    return max(dates) if dates else None


def log_summary_of(cfg: dict, max_items: int = 3, max_len: int = 80) -> str:
    """从当日生产文件自动提取 log 摘要（前几条发现的加粗标题）。

    修复 08-05/08-06 两次事故：update-log 生成的条目以悬空" —"结尾且无摘要，
    需 AI 事后手工补全。本函数从文件提取前 max_items 条 "- **标题**" 作为摘要；
    提取失败（文件为空/占位/格式异常）返回空串，调用方据此省略" — "。
    """
    fp = resolve_out(cfg)
    try:
        text = open(fp, encoding="utf-8").read()
    except Exception:
        return ""
    items = []
    for m in re.finditer(r"-\s+\*\*(.+?)\*\*", text):
        t = m.group(1).strip()
        if not t or t.startswith("搜索摘要"):
            continue
        if len(t) > max_len:
            t = t[:max_len] + "…"
        items.append(t)
        if len(items) >= max_items:
            break
    return " · ".join(items)


def cmd_update_log(args):
    # 2026-08-19 系统改造（二次）：定时调研信息默认不更新 index.md/log.md——
    # 全库统一根 knowledge/index.md（kb-global-index.py 批量刷新）+ knowledge/log.md（kb-log-append.py 追加）。
    # 本命令保留为 no-op 锚点：调用链（guide/SKILL 描述）不破坏，但不写任何分布式 index/log（含 log.old.md）。
    cfg = TASKS[args.task]
    module = module_of(cfg)
    print(f"[update-log] 已跳过（定时调研默认不写 index/log，2026-08-19 起；深度分析请用 kb-log-append.py 追加 knowledge/log.md）· task={args.task} module={module}")


def cmd_check_gap(args):
    cfg = TASKS[args.task]
    last = last_production_date(cfg)
    if not last:
        print(f"[check-gap] {cfg['name']}: 无历史产出记录，首次执行正常")
        return
    gap = (datetime.now() - datetime.strptime(last, "%Y-%m-%d")).days
    if gap >= 7:
        print(f"[check-gap] ⚠️ {cfg['name']} 已静默 {gap} 天 (上次: {last})")
        print("  → 升级策略: 搜索源+2（追加 arXiv/Bing 宽泛搜索）· 关键词扩展 2 组变体 · 失败可重试 1 次")
    elif gap >= 3:
        print(f"[check-gap] ⚠️ {cfg['name']} 已静默 {gap} 天 (上次: {last})")
        print("  → 升级策略: 搜索源增至 5 个 · 关键词 2 组变体 · 每源失败可换词重试 1 次")
    else:
        print(f"[check-gap] ✅ {cfg['name']} 产出正常 (上次: {last}, {gap} 天前)")


def cmd_guide(args):
    """输出完整执行链（任务描述只引用本命令，规则全部内建）。"""
    cfg = TASKS[args.task]
    tid = args.task
    R = "python3 skills/industry-insight/scripts/research_task_runner.py"
    print(f"=== 调研任务执行指南: {cfg['name']} [{tid}] ===")
    print(f"输出路径: {cfg['out'].replace('YYYY-MM-DD', today())}（专题独立目录，保持不变）")
    print(f"[硬规则] 只写入本任务自己的输出目录；严禁写入他人目录或共享文件 industry-research/YYYY-MM-DD.md")
    if cfg.get("section"):
        print(f"输出章节: 追加到「{cfg['section']}」小节")
    b = depth_budget(cfg)
    print(f"推荐 Skill: {cfg['skill']} · 档位: {b['label']} · token预算: {b['token_budget']} · 输出{b['out_max_kb'] or '≥30KB(无上限)'}KB")
    print(f"  → {b['target_hint']}")
    print("")
    print("按序执行以下命令（搜索源/源可靠性/质量/丰度/格式/占位/index-log 规则已全部内建，无需阅读外部规则）：")
    print("")
    print("① 生成搜索计划（含源列表/关键词/顺序）:")
    print(f"   {R} plan --task {tid}")
    print("")
    b2 = depth_budget(cfg)
    print(f"② 按计划用 web_fetch 逐源抓取（每源仅1次·失败跳过·读{b2['read_lines']}），每源记录结果:")
    print("   ⚠️ 官网首页源若无新内容 → 改抓其 Blog/Press Room 子页（公告/预告常只在子页，08-06 UALink 教训）")
    print(f"   {R} register --task {tid} --source <源名> --success   # 或 --fail")
    print("")
    print("③ 生成当日文件骨架/章节定位（不覆盖已有内容）:")
    print(f"   {R} scaffold --task {tid}")
    print("")
    print("④ 将有效发现写入输出文件（每条: - **来源/标题**（日期）: 要点+量化数据；必须含来源URL）")
    b3 = depth_budget(cfg)
    if b3["out_max_kb"] is None:
        print("   ⚠️ 深度档丰度校验 = 列表项 + 分析段落 + 表格多维统计：每条发现用 `- ` 列表项，**另需 ≥3 段分析性段落**（因果链/对比/原理展开），可自由使用表格（08-04 曾因纯编号+表格致丰度不足，需列表项兜底）")
    else:
        print("   ⚠️ 每条发现必须用 `- ` 开头的 markdown 列表项书写——丰度校验只统计行首 `-`/`*` 列表项，编号列表/表格不计入（08-04 曾因用编号+表格致丰度不足）")
    print("   ⚠️ URL 必须来自实际抓取内容（web_fetch 原文/curl 提取 HTML/站内搜索命中），严禁按格式推测编造；写入前逐条 curl 验证 HTTP 200，无法验证的条目删除（08-11 教训: 3 条推测格式 URL 全 404）")
    print("   ⚠️ 跨组去重（08-15 教训: 13 条跨组重复被迫重写）: 组任务 hardware/tech/market 同日并行，写入前必须 grep 其他组同日文件")
    print("     （knowledge/01_survey/industry-research/<其他组>/YYYY-MM-DD.md），已被其他组收录的条目→一行交叉引用「（已由<组名>收录）」，不写大段剔除说明，篇幅留给本组增量")
    print("")
    print("⑤ 输出可靠性校验（FAIL 项必须修复后重跑直至全部 PASS）:")
    print(f"   {R} verify --task {tid}")
    print("")
    print("⑥ 自动更新 log.md + 检查 index.md 登记:")
    print(f"   {R} update-log --task {tid}")
    print("")
    print("零产出（无任何有效信息）→ 生成占位文件（参与日报审计）:")
    print(f"   {R} placeholder --task {tid}")


def cmd_list(args):
    print("=== 调研任务配置清单 (configs/research_topics.json) ===")
    groups = [tid for tid, c in TASKS.items() if c.get("kind") == "group"]
    topics = [tid for tid, c in TASKS.items() if c.get("kind") != "group"]
    print(f"\n组任务 ({len(groups)}):")
    for tid in sorted(groups):
        c = TASKS[tid]
        print(f"  [组] {tid} · {c['name']} · {len(c['sections'])}专题 · {c['out']}")
    print(f"\n单主题任务 ({len(topics)}):")
    for tid in sorted(topics):
        c = TASKS[tid]
        print(f"  [题] {tid} · {c['name']} · {c['out']}")


# ============================================================
# main
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="调研定时任务统一执行器 v1.4")
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name in ["plan", "scaffold", "verify", "placeholder", "update-log", "check-gap", "register", "guide"]:
        p = sub.add_parser(name, help=f"{name} 子命令")
        p.add_argument("--task", required=True, help="任务ID 或 任务名（见 configs/research_topics.json）")
        if name == "register":
            p.add_argument("--source", required=True, help="源名称")
            p.add_argument("--success", action="store_true", help="标记成功")
            p.add_argument("--fail", action="store_true", help="标记失败")

    sub.add_parser("list", help="列出全部任务配置")

    args = parser.parse_args()
    if args.cmd == "list":
        cmd_list(args)
        return
    if args.cmd == "register":
        if not (args.success or args.fail):
            print("register 需要 --success 或 --fail")
            sys.exit(1)
        args.task = resolve_task_id(args.task)
        cmd_register(args)
        return
    args.task = resolve_task_id(args.task)
    {"plan": cmd_plan, "scaffold": cmd_scaffold, "verify": cmd_verify,
     "placeholder": cmd_placeholder, "update-log": cmd_update_log,
     "check-gap": cmd_check_gap, "guide": cmd_guide}[args.cmd](args)


if __name__ == "__main__":
    main()
