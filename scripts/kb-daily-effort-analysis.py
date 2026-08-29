#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# kb-daily-effort-analysis.py v1 — 日报 v4 产出结构与 AI 健康度分析器
#
# 用途：对日报时间窗口内的产出做四维分析，供日报「📈 产出结构与
#       AI 健康度 / 🧑💻 用户干预评价 / 📐 内容质量评价」模块消费：
#       (1) 产出四分类：每日调研输出 / 深度分析专题 / 数据源处理 / 系统监控与管理
#       (2) AI 比重（双口径：提交数 + 变更文件数），目标 ≥90%
#       (3) 用户干预评价五维：问题输入 / 人工提交 / 数据源输入 / 工具维护 / 综合自动化率
#       (4) 内容质量三维：内容长度 / 单文件修订次数 / 同目录聚集度
#
# 时间窗口：[REPORT_DATE 08:00 → (REPORT_DATE+1) 08:10]（与 kb-daily-git-analysis.py 对齐）
#
# 用法：
#   python3 scripts/kb-daily-effort-analysis.py            # 上一日
#   python3 scripts/kb-daily-effort-analysis.py 2026-08-14 # 指定日期
#
# 输出：
#   - stdout：Markdown 片段（供日报直接嵌入）
#   - tmp/kb-daily-effort-analysis-{REPORT_DATE}.md：同内容落盘
#
# 依赖：
#   - git 全仓历史（修订次数统计用 --follow，逐文件查询）
#   - memory/long-term/index.db（sessions 表，统计问题输入；缺失则降级）
#
# 变更日志：
#   2026-08-14 v1 created（日报 v4：产出四分类 + AI 健康度 90% 口径 + 干预评价 + 质量评价）
#================================================================

import subprocess
import sys
import os
import re
import sqlite3
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta

WORKSPACE = os.path.expanduser("~/cow")
INDEX_DB = os.path.join(WORKSPACE, "memory/long-term/index.db")

# ─────────────────────────────────────────────
# 产出四分类规则（可配置；用户可微调后回写此处）
# 判定优先级：SYSTEM > DATA_SOURCE > DAILY_RESEARCH > DEEP_ANALYSIS
# ─────────────────────────────────────────────
SYSTEM_PATTERNS = [
    "skills/", "scripts/", "spec/", "scheduler/",
    "memory/", "conversation-log/",
    "knowledge/weekly-reports/",          # 日报/周报本身 = 管理产出
    "knowledge/index.md", "knowledge/log.md", "knowledge/README.md",
    "AGENT.md", "USER.md", "RULE.md", "MEMORY.md",
    "tmp/", ".gitignore", ".github/", "import/import_log",
]
DATA_SOURCE_PATTERNS = [
    "import/",                            # 用户素材输入目录
    "knowledge/sources/",                 # 采集归档（web-archive/wechat/doubao）
    "knowledge/06_others/sources/",
    "source-registry",
    "data/",                              # 数据/数据集
]
DAILY_RESEARCH_PATTERNS = ["knowledge/01_survey/"]   # 每日调研跟踪文件

CAT_NAMES = {
    "daily-research": "📡 每日调研输出",
    "deep-analysis": "📐 深度分析专题",
    "data-source": "🗄️ 数据源处理",
    "system-mgmt": "🔧 系统监控与管理",
}

def classify_path(path):
    """按路径把文件归入四类（优先级 SYSTEM > DATA_SOURCE > DAILY_RESEARCH）"""
    if any(p in path for p in SYSTEM_PATTERNS):
        return "system-mgmt"
    if any(p in path for p in DATA_SOURCE_PATTERNS):
        return "data-source"
    if any(p in path for p in DAILY_RESEARCH_PATTERNS):
        return "daily-research"
    # 其余 knowledge/** 正式文档（含 deep-analysis 命名）→ 深度分析专题
    if path.startswith("knowledge/") and path.endswith(".md"):
        return "deep-analysis"
    return "system-mgmt"   # 其他杂项归管理

# ─────────────────────────────────────────────
# git 基础
# ─────────────────────────────────────────────
def parse_date(report_date):
    d = datetime.strptime(report_date, "%Y-%m-%d")
    return d, d + timedelta(days=1)

def git_log(report_date, next_day):
    after = f"{report_date}T08:00:00"
    before = f"{next_day}T08:10:00"
    cmd = ["git", "log", f"--after={after}", f"--before={before}",
           "--format=%H%x1f%an%x1f%ad%x1f%s%x1f%b",
           "--date=format:%Y-%m-%d %H:%M:%S"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE)
    if r.returncode != 0:
        return []
    commits = []
    for line in r.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\x1f")
        if len(parts) < 5:
            continue
        commits.append({"hash": parts[0][:12], "author": parts[1],
                        "date": parts[2], "subject": parts[3], "body": parts[4].strip()})
    return commits

def is_ai(commit):
    return commit["subject"].startswith("[AI]")

# 定时任务/自动管道提交识别：无 [AI] 前缀但属于自动化调研/归档/抓取管道产出
# （每日追踪归档、rss 抓取、web-archive 归档等）。判定：subject 命中模式且文件数 ≤8
# （文件多 = 导入/迁移/重构 = 人工动作）。规则可配置，用户可微调后回写。
AUTO_PIPE_RE = re.compile(
    r"(追踪|跟踪|tracking|追踪归档|^survey[:：]|^data-analysis[:：]|^rss|^fetch|归档)",
    re.IGNORECASE,
)

def is_auto_pipe(commit, n_files):
    """定时/自动管道提交（无 [AI] 前缀但非人工干预）"""
    if n_files is None or n_files > 8:
        return False
    return bool(AUTO_PIPE_RE.search(commit["subject"]))

def get_commit_files(commits):
    """返回 {hash: [(path, add, del, status)]}，status 取 A/M/R/D
    稳健实现：--name-status 得状态，--numstat 得行数，两者按路径合并"""
    out = {}
    for c in commits:
        out[c["hash"]] = parse_files_fallback(c["hash"])
    return out

def parse_files_fallback(hash_):
    """稳健版：分别跑 --numstat 与 --name-status，合并"""
    files = []
    # name-status 得状态与路径
    r1 = subprocess.run(["git", "show", "--format=", "--name-status", hash_],
                        capture_output=True, text=True, cwd=WORKSPACE)
    status_map = {}
    for line in r1.stdout.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] in ("A", "M", "D", "R"):
            if parts[0] == "R" and len(parts) >= 3:
                status_map[parts[2]] = "R"
            else:
                status_map[parts[1]] = parts[0]
    # numstat 得行数
    r2 = subprocess.run(["git", "show", "--format=", "--numstat", hash_],
                        capture_output=True, text=True, cwd=WORKSPACE)
    for line in r2.stdout.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) == 3:
            path = parts[2]
            try:
                a, d = int(parts[0]), int(parts[1])
            except ValueError:
                a = d = 0
            st = status_map.get(path, "M")
            files.append((path, a, d, st))
    return files

def count_file_revisions(path):
    """单文件全历史修订次数（git log --follow），含重命名跟踪；超时保护"""
    try:
        r = subprocess.run(["git", "log", "--follow", "--oneline", "--", path],
                           capture_output=True, text=True, cwd=WORKSPACE, timeout=10)
        if r.returncode == 0:
            return len([l for l in r.stdout.strip().split("\n") if l.strip()])
    except subprocess.TimeoutExpired:
        pass
    return None

# ─────────────────────────────────────────────
# 问题输入统计（sessions 表）
# ─────────────────────────────────────────────
def count_user_sessions(report_date, next_day):
    """统计窗口内活跃的『用户会话』（排除 scheduler_ 定时任务渠道）"""
    if not os.path.exists(INDEX_DB):
        return None
    try:
        conn = sqlite3.connect(INDEX_DB)
        cur = conn.cursor()
        start = int(datetime.strptime(report_date + " 08:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
        end = int(datetime.strptime(next_day + " 08:10:00", "%Y-%m-%d %H:%M:%S").timestamp())
        cur.execute("""SELECT COUNT(*), COALESCE(SUM(msg_count),0) FROM sessions
                       WHERE last_active BETWEEN ? AND ?
                         AND (channel_type IS NULL OR channel_type NOT LIKE 'scheduler_%')""",
                    (start, end))
        n, msgs = cur.fetchone()
        # 渠道分布
        cur.execute("""SELECT channel_type, COUNT(*) FROM sessions
                       WHERE last_active BETWEEN ? AND ? GROUP BY channel_type""", (start, end))
        channels = dict(cur.fetchall())
        conn.close()
        return {"sessions": n, "msgs": msgs, "channels": channels}
    except Exception as e:
        return {"error": str(e)}

# ─────────────────────────────────────────────
# 主分析
# ─────────────────────────────────────────────
def main():
    report_date = sys.argv[1] if len(sys.argv) > 1 else (
        datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    d, next_day = parse_date(report_date)
    next_str = next_day.strftime("%Y-%m-%d")

    commits = git_log(report_date, next_str)
    if not commits:
        print(f"⚠️ 时间窗口 {report_date} 08:00 → {next_str} 08:10 内无提交")
        return

    files_by_commit = get_commit_files(commits)
    ai_commits = [c for c in commits if is_ai(c)]
    manual_commits = [c for c in commits if not is_ai(c)]
    n_ai, n_manual = len(ai_commits), len(manual_commits)
    total = len(commits)

    # ── 超大提交检测（批量治理/大导入，单独标注口径，不污染分类与 AI 比重）──
    # 依据 kb-effort-churn 技能统计铁律：单提交塞 300+ 文件会虚增，先识别并单独标注
    BIG_FILES, BIG_LINES = 300, 10000
    big_commits = []
    for c in commits:
        fl = files_by_commit.get(c["hash"], [])
        if len(fl) > BIG_FILES or sum(f[1] + f[2] for f in fl) > BIG_LINES:
            big_commits.append((c, len(fl), sum(f[1] + f[2] for f in fl)))
    big_hashes = {c["hash"] for c, _, _ in big_commits}
    normal_commits = [c for c in commits if c["hash"] not in big_hashes]

    # 常规提交归因：AI 自动提交 = [AI] 前缀 + 自动管道提交（定时调研/归档/rss）
    # 人工提交 = 其余（导入/迁移/重构/清理/手动修改）
    auto_commits, manual_commits = [], []
    for c in normal_commits:
        nf = len(files_by_commit.get(c["hash"], []))
        if is_ai(c) or is_auto_pipe(c, nf):
            auto_commits.append(c)
        else:
            manual_commits.append(c)
    n_ai_n, n_manual_n = len(auto_commits), len(manual_commits)
    total_n = len(normal_commits)

    # ── 1. 产出四分类（基于 normal 提交，排除超大治理提交）──
    cat_files = defaultdict(list)      # cat -> [(path, add, del, status)]
    cat_add = Counter(); cat_del = Counter(); cat_commits = Counter()
    for c in normal_commits:
        for (path, add, del_, st) in files_by_commit.get(c["hash"], []):
            cat = classify_path(path)
            cat_files[cat].append((path, add, del_, st))
            cat_add[cat] += add; cat_del[cat] += del_
    # 提交数按类（一个提交可能跨类，按主类计：首个文件类别）
    for c in normal_commits:
        flist = files_by_commit.get(c["hash"], [])
        if flist:
            cat_commits[classify_path(flist[0][0])] += 1
        else:
            cat_commits["system-mgmt"] += 1

    # ── 2. AI 比重（双口径，基于 normal 提交） ──
    all_paths = {f[0] for c in normal_commits for f in files_by_commit.get(c["hash"], [])}
    ai_n_commits = auto_commits
    ai_paths = {f[0] for c in ai_n_commits for f in files_by_commit.get(c["hash"], [])}
    ai_ratio_commit = n_ai_n * 100 // max(total_n, 1)
    ai_ratio_files = len(ai_paths) * 100 // max(len(all_paths), 1)

    # ── 3. 用户干预（基于 normal 提交 + 独立素材统计） ──
    sessions = count_user_sessions(report_date, next_str)
    # 数据源输入：全窗口 import/ 变更文件数（用户投放素材；大导入提交也计入——素材投放本身是用户动作）
    import_files = {f[0] for fl in files_by_commit.values() for f in fl if f[0].startswith("import/")}
    # 工具维护：skills/scripts/spec 变更，区分 AI/用户发起（按提交数统一口径）
    tool_files_ai = {f[0] for c in auto_commits for f in files_by_commit.get(c["hash"], [])
                     if any(f[0].startswith(p) for p in ("skills/", "scripts/", "spec/"))}
    tool_files_user = {f[0] for c in manual_commits
                       for f in files_by_commit.get(c["hash"], [])
                       if any(f[0].startswith(p) for p in ("skills/", "scripts/", "spec/"))}
    tool_user_commits = 0
    for c in manual_commits:
        fl = files_by_commit.get(c["hash"], [])
        if any(f[0].startswith(("skills/", "scripts/", "spec/")) for f in fl):
            tool_user_commits += 1
    # AI 自动化率（产出侧）：常规提交中自动化占比——『素材/问题输入』是喂给 AI 的原料，
    # 不算人工代劳产出；只有『人工提交 + 用户工具维护提交』是人工代劳
    manual_produce = n_manual_n
    auto_rate = (1 - manual_produce / max(total_n, 1)) * 100
    # 干预结构：输入型（问题/素材） vs 代劳型（人工提交/用户维护）
    n_input_type = (sessions.get("sessions", 0) if sessions and "error" not in sessions else 0) + len(import_files)
    n_delegate_type = manual_produce

    # ── 4. 内容质量 ──
    # 4a 内容长度：当日新增（A）知识文件（deep-analysis + daily-research）字节
    new_kb_files = []
    for fl in files_by_commit.values():
        for (path, add, del_, st) in fl:
            if st == "A" and path.startswith("knowledge/") and path.endswith(".md") \
               and classify_path(path) in ("deep-analysis", "daily-research"):
                new_kb_files.append(path)
    new_kb_files = sorted(set(new_kb_files))
    sizes = []
    for p in new_kb_files:
        full = os.path.join(WORKSPACE, p)
        try:
            sizes.append(os.path.getsize(full))
        except OSError:
            pass
    if sizes:
        sizes.sort()
        med = sizes[len(sizes)//2]
        mean = sum(sizes)//len(sizes)
        deep_ratio = sum(1 for s in sizes if s >= 10240) * 100 // len(sizes)   # ≥10KB 深度
        frag_ratio = sum(1 for s in sizes if s <= 1024) * 100 // len(sizes)    # ≤1KB 碎片
    else:
        med = mean = deep_ratio = frag_ratio = 0

    # 4b 单文件修订次数：当日涉及知识文件的历史修订次数
    # 账簿型文件（index/log/README）高频修订是记账正常行为，单独统计不并入 churn
    ACCOUNT_BOOK = {"index.md", "log.md", "README.md"}
    involved_kb = sorted({f[0] for fl in files_by_commit.values() for f in fl
                          if f[0].startswith("knowledge/") and f[0].endswith(".md")})
    rev_counts = {}
    rev_book = {}
    for p in involved_kb[:60]:   # 保护：最多 60 文件逐查
        n = count_file_revisions(p)
        if n is None:
            continue
        if p.split("/")[-1] in ACCOUNT_BOOK:
            rev_book[p] = n
        else:
            rev_counts[p] = n
    if rev_counts:
        rev_vals = list(rev_counts.values())
        rev_max = max(rev_vals); rev_mean = sum(rev_vals)/len(rev_vals)
        polished = sum(1 for v in rev_vals if 2 <= v <= 10) * 100 // len(rev_vals)  # 打磨 2-10 次
        churn = sum(1 for v in rev_vals if v > 10) * 100 // len(rev_vals)           # >10 次 churn 信号
    else:
        rev_max = rev_mean = polished = churn = 0

    # 4c 同目录聚集度：当日新增文件按二级目录
    new_all = [f[0] for fl in files_by_commit.values() for f in fl if f[3] == "A"]
    dir_counter = Counter()
    for p in new_all:
        parts = p.split("/")
        dir_counter["/".join(parts[:2]) if len(parts) >= 2 else parts[0]] += 1
    if dir_counter:
        top_dir, top_n = dir_counter.most_common(1)[0]
        top1_ratio = top_n * 100 // len(new_all)
        # 信息熵（聚集度反向指标）
        n_total = len(new_all)
        H = -sum((n/n_total) * math.log2(n/n_total) for n in dir_counter.values())
        H_max = math.log2(max(len(dir_counter), 1))
        norm_entropy = (H / H_max) if H_max > 0 else 0   # 0=完全聚集, 1=完全分散
    else:
        top_dir, top1_ratio, norm_entropy = "无", 0, 1.0

    # 质量综合分（0-100，口径可调）
    score = (0.4 * min(deep_ratio, 100) + 0.3 * polished + 0.3 * (100 * (1 - norm_entropy)))
    score = round(score, 1)

    # ── 渲染 ──
    L = []
    L.append(f"### 📈 产出结构与 AI 健康度（{report_date}）")
    L.append("")
    L.append(f"> 统计窗口: {report_date} 08:00 → {next_str} 08:10 · 总提交 {total}（常规 {total_n} + 批量治理 {len(big_commits)}）· 常规变更文件 {len(all_paths)}")

    # 超大提交口径标注
    if big_commits:
        big_desc = "、".join(f"`{c['subject'][:38]}`({nf}文件/{nl}行)" for c, nf, nl in big_commits[:3])
        L.append(f"> ⚠️ 已排除超大提交 {len(big_commits)} 个（>300 文件或 >10k 行，批量治理/大导入，单独口径）：{big_desc}")

    # 四分类表
    L.append("")
    L.append("**产出四分类**（按常规变更文件归集，判定优先级：系统 > 数据源 > 调研 > 深度）：")
    L.append("")
    L.append("| 产出类别 | 文件数 | 提交数 | 插入行 | 删除行 | 占比 |")
    L.append("|:---------|:------:|:------:|:------:|:------:|:----:|")
    for cat in ("daily-research", "deep-analysis", "data-source", "system-mgmt"):
        files = cat_files.get(cat, [])
        nf = len(set(f[0] for f in files))
        if nf == 0:
            continue
        bar = "█" * (nf * 20 // max(len(all_paths), 1))
        L.append(f"| {CAT_NAMES[cat]} | {nf} | {cat_commits[cat]} | +{cat_add[cat]} | -{cat_del[cat]} | {nf*100//max(len(all_paths),1)}% {bar} |")
    L.append("")

    # AI 比重
    health = "🟢 优秀（≥90%，目标达成）" if ai_ratio_commit >= 90 else \
             ("🟡 良好（80-90%，接近目标）" if ai_ratio_commit >= 80 else "🔴 待提升（<80%，AI 未充分接管例行产出）")
    L.append(f"**AI 比重**：按提交 **{ai_ratio_commit}%**（{n_ai_n}/{total_n}）· 按文件 **{ai_ratio_files}%**（{len(ai_paths)}/{len(all_paths)}）→ {health}")
    L.append(f"> 健康口径（2026-08-14 用户定义）：AI 自动提交占比目标 **≥90%**；用户干预应集中于『问题输入』，而非人工代劳产出。")
    L.append("")

    # 用户干预
    L.append("### 🧑💻 用户干预评价")
    L.append("")
    L.append("| 干预维度 | 当日量 | 说明 |")
    L.append("|:---------|:------:|:-----|")
    if sessions and "error" not in sessions:
        ch_parts = []
        for k, v in (sessions.get("channels") or {}).items():
            ch_parts.append(f"{k or '未知渠道'}:{v}")
        ch_str = "、".join(ch_parts) or "无"
        L.append(f"| ① 问题输入（用户会话） | {sessions['sessions']} 会话 / {sessions['msgs']} 消息 | 驱动 AI 产出的指令输入（渠道：{ch_str}） |")
    else:
        err = sessions.get("error", "index.db 不存在") if sessions else "index.db 不存在"
        L.append(f"| ① 问题输入（用户会话） | 数据不可用 | sessions 库缺失或异常：{err} |")
    L.append(f"| ② 人工提交 | {n_manual_n} 次 | 非 [AI]/非自动管道提交（导入/迁移/重构/清理/手动修改） |")
    L.append(f"| ③ 数据源输入 | {len(import_files)} 文件 | import/ 素材投放（用户提供原始素材，含大导入） |")
    L.append(f"| ④ 工具维护-用户发起 | {tool_user_commits} 提交/{len(tool_files_user)} 文件 | skills/scripts/spec 变更中人工部分 |")
    L.append(f"| ⑤ 工具维护-AI 自主 | {len(tool_files_ai)} 文件 | skills/scripts/spec 变更中自动化部分（自进化） |")
    L.append("")
    L.append(f"**AI 自动化率（产出侧）**：**{auto_rate:.1f}%**（自动化 {n_ai_n}/{total_n} = [AI] 提交 + 定时/归档管道提交；人工代劳 {n_manual_n} 次）")
    L.append(f"> 干预结构：输入型（问题 {sessions.get('sessions', 0) if sessions and 'error' not in sessions else 'N/A'} 会话 + 素材 {len(import_files)} 文件）vs 代劳型（{n_delegate_type} 提交）——健康形态=高自动化率且干预集中于『输入型』：用户只提问/喂料，AI 全自动完成调研/归档/分析/提交。")
    if manual_commits:
        samples = "、".join(f"`{c['subject'][:50]}`" for c in manual_commits[:4])
        L.append(f"> 人工提交示例：{samples}")
    L.append("")

    # 内容质量
    L.append("### 📐 内容质量评价（三维）")
    L.append("")
    L.append(f"**① 内容长度**：新增知识文档 {len(new_kb_files)} 篇 · 中位 **{med//1024}KB** · 均值 {mean//1024}KB · ≥10KB 深度占比 **{deep_ratio}%** · ≤1KB 碎片 {frag_ratio}%")
    if new_kb_files:
        names = "、".join(f"`{p.replace('knowledge/01_survey/','01_survey/')[:52]}`" for p in new_kb_files[:4])
        L.append(f"> 新增文档：{names}{'…' if len(new_kb_files)>4 else ''}")
    L.append("")
    if rev_book:
        book_desc = "、".join(f"`{p[:44]}`×{n}" for p, n in list(rev_book.items())[:3])
        L.append(f"**② 单文件修订次数**：当日涉及知识文件 {len(rev_counts)} 个（另账簿型 {len(rev_book)} 个：{book_desc}，记账高频属正常）· 业务文档历史修订 均值 {rev_mean:.1f} 次 · 最高 {rev_max} 次 · 打磨型(2-10次) **{polished}%** · churn 信号(>10次) {churn}%")
    else:
        L.append(f"**② 单文件修订次数**：当日涉及知识文件 {len(rev_counts)} 个 · 业务文档历史修订 均值 {rev_mean:.1f} 次 · 最高 {rev_max} 次 · 打磨型(2-10次) **{polished}%** · churn 信号(>10次) {churn}%")
    if rev_counts:
        top_rev = sorted(rev_counts.items(), key=lambda x: -x[1])[:3]
        L.append(f"> 反复修订文件：{'、'.join(f'`{p.split(chr(47))[-1][:36]}`×{n}' for p, n in top_rev)}")
    L.append("")
    agg_desc = "专题化聚集（体系化产出 ✅）" if top1_ratio >= 50 and norm_entropy < 0.6 else \
               ("较分散（覆盖面广，注意碎片化）" if norm_entropy > 0.8 else "中等聚集")
    L.append(f"**③ 同目录聚集度**：Top1 目录 `{top_dir}` 占 **{top1_ratio}%** · 归一化熵 {norm_entropy:.2f}（0=全聚集/1=全分散）→ {agg_desc}")
    L.append("")
    L.append(f"**内容质量综合分：{score}/100**（0.4×深度 + 0.3×打磨 + 0.3×体系化；口径可调）")
    L.append("")

    md = "\n".join(L)
    os.makedirs(f"{WORKSPACE}/tmp", exist_ok=True)
    out_path = f"{WORKSPACE}/tmp/kb-daily-effort-analysis-{report_date}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print(f"\n<!-- ✅ 已保存: {out_path} -->", file=sys.stderr)

if __name__ == "__main__":
    main()
