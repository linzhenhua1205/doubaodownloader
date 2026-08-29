#!/usr/bin/env python3
"""
token-consumption-analyzer.py — CowAgent 运行日志 Token 消耗通用分析器（extract → analyze → full-timeline 一体化）

功能：
  1. extract: run.log 全量事件解析入 SQLite（14 张事件表：requests/turns/tool_calls/compressions/...）
  2. analyze: 明细期统计（日趋势/压缩解剖/会话维度/工具维度/截断/思考/可靠性）
  3. full-timeline: 官方 N 天计费数据（DeepSeek 平台 JSON）+ 日志明细期估算 → 全周期时间线

用法：
  python3 scripts/kb-stat/token-consumption-analyzer.py                          # 全流程+全部图表
  python3 scripts/kb-stat/token-consumption-analyzer.py --no-charts              # 纯统计
  python3 scripts/kb-stat/token-consumption-analyzer.py --stats-only             # 复用已有 DB
  python3 scripts/kb-stat/token-consumption-analyzer.py --log tmp/run.log        # 指定日志
  python3 scripts/kb-stat/token-consumption-analyzer.py --official spec/scripts/deepseek_consumption.json
  python3 scripts/kb-stat/token-consumption-analyzer.py --json                   # 统计另存 JSON

Token 估算模型参数（可用参数覆盖）：
  --sys-pre 118000   优化前 system prompt 固定开销 tokens/请求
  --sys-post 18000   优化后固定开销 tokens/请求
  --opt-date 2026-08-07  优化切换日（当天起按 sys-post 计）
  --hist-per-msg 300     历史消息均量 tokens/条

依赖：Python3 标准库 + matplotlib/numpy（仅图表阶段，--no-charts 可跳过）
产出案例：
  knowledge/02_rd/02_project/03_kb_cowagent/2026-08-07-token-consumption-visual-analysis.md（明细期 v2.0）
  knowledge/02_rd/02_project/03_kb_cowagent/2026-08-08-token-consumption-full-timeline-analysis.md（全周期 v3.0）
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.workspace import TMP_DIR, SPEC_DIR  # sr-008

# ── 日志事件正则（agent_stream.py 等锚点，来自结构勘探） ─────────────────────

LINE_RE = re.compile(r'^\[(\w+)\]\[(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2})\]\[([\w.]+):(\d+)\] - (.*)$')
R_SEND = re.compile(r'Sending (\d+) messages \((\d+) turns\) to LLM')
R_TURN = re.compile(r'\[Agent\] Turn (\d+)')
R_TCALLS = re.compile(r'([a-z_][a-z_0-9]*)\(')
R_TRES = re.compile(r'✅ (\w+) \(([\d.]+)s\): (.*)$')
R_SESS = re.compile(r'🤖 (\S+) \| (💭 thinking \| )?👤 (.*)$')
R_DONE = re.compile(r'\[Agent\] 🏁 Done \((\d+) turns\)')
R_COMPA = re.compile(r'🔄 Context tokens exceeded: ~(\d+) > (\d+), trimmed to (\d+) turns \(removed (\d+)\)')
R_COMPB = re.compile(r'📦 Context tokens exceeded \(turns<5\): ~(\d+) > (\d+), compressed all (\d+) turns to plain text \((\d+) -> (\d+) messages, ~(\d+) -> ~(\d+) tokens\)')
R_COMPD = re.compile(r'Removed (\d+) turns \((\d+) -> (\d+) messages, ~(\d+) -> ~(\d+) tokens\)')
R_HISTR = re.compile(r'📎 Truncated (\d+) historical tool result\(s\) to (\d+) chars')
R_CURTR = re.compile(r"📎 Truncated tool result for '(\w+)': (\d+) -> (\d+) chars")
R_RTRUNC = re.compile(r'\[reasoning\] truncated for storage: (\d+) -> (\d+) chars')
R_FLUSH = re.compile(r'\[MemoryFlush\] Async flush dispatched \(reason=(\w+), msgs=(\d+)\)')
R_ART = re.compile(r'🗂  Artifact: (.*) \((\w+)\)')
R_SCHED = re.compile(r'\[Scheduler\] Executing task: (\w+) - (.*)$')

SCHEMA = """
DROP TABLE IF EXISTS requests;   CREATE TABLE requests(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, hour INT, n_msgs INT, n_turns INT, session_id INT);
DROP TABLE IF EXISTS turns;      CREATE TABLE turns(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, turn_no INT, session_id INT);
DROP TABLE IF EXISTS tool_calls; CREATE TABLE tool_calls(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, tool TEXT, session_id INT);
DROP TABLE IF EXISTS tool_results;CREATE TABLE tool_results(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, tool TEXT, dur_s REAL, out_chars INT, session_id INT);
DROP TABLE IF EXISTS sessions;   CREATE TABLE sessions(id INTEGER PRIMARY KEY, ts_start TEXT, date TEXT, model TEXT, thinking INT, query TEXT);
DROP TABLE IF EXISTS session_done;CREATE TABLE session_done(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, turns INT, session_id INT);
DROP TABLE IF EXISTS compressions;CREATE TABLE compressions(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, hour INT, kind TEXT, ctx_before INT, budget INT, msgs_before INT, msgs_after INT, tokens_after INT, turns_removed INT, session_id INT);
DROP TABLE IF EXISTS truncations;CREATE TABLE truncations(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, scope TEXT, tool TEXT, from_chars INT, to_chars INT, session_id INT);
DROP TABLE IF EXISTS thinking;   CREATE TABLE thinking(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, source TEXT, session_id INT);
DROP TABLE IF EXISTS reasoning_trunc;CREATE TABLE reasoning_trunc(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, from_chars INT, to_chars INT);
DROP TABLE IF EXISTS memflush;   CREATE TABLE memflush(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, reason TEXT, msgs INT);
DROP TABLE IF EXISTS artifacts;  CREATE TABLE artifacts(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, path TEXT, atype TEXT);
DROP TABLE IF EXISTS sched_tasks;CREATE TABLE sched_tasks(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, task_id TEXT, title TEXT);
DROP TABLE IF EXISTS errors;     CREATE TABLE errors(id INTEGER PRIMARY KEY, ts TEXT, date TEXT, level TEXT, loc TEXT, msg TEXT);
DROP TABLE IF EXISTS official_daily;CREATE TABLE official_daily(date TEXT, weekday TEXT, cost REAL);
"""


# ── 阶段 1：日志 → SQLite ────────────────────────────────────────────────────

def extract(log_path, db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    cur = con.cursor()
    sid = 0
    n = 0
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            n += 1
            m = LINE_RE.match(line)
            if not m:
                continue
            lvl, d, hh, mm, ss, mod, ln, msg = m.groups()
            ts = f"{d} {hh}:{mm}:{ss}"
            hour = int(hh)
            loc = f"{mod}:{ln}"
            if loc == 'agent_stream.py:563':
                sm = R_SESS.search(msg)
                if sm:
                    sid += 1
                    cur.execute("INSERT INTO sessions(ts_start,date,model,thinking,query) VALUES(?,?,?,?,?)",
                                (ts, d, sm.group(1), 1 if sm.group(2) else 0, sm.group(3)[:200]))
            elif loc == 'agent_stream.py:1056':
                sm = R_SEND.search(msg)
                if sm:
                    cur.execute("INSERT INTO requests(ts,date,hour,n_msgs,n_turns,session_id) VALUES(?,?,?,?,?,?)",
                                (ts, d, hour, int(sm.group(1)), int(sm.group(2)), sid))
            elif loc == 'agent_stream.py:609':
                sm = R_TURN.search(msg)
                if sm:
                    cur.execute("INSERT INTO turns(ts,date,turn_no,session_id) VALUES(?,?,?,?)",
                                (ts, d, int(sm.group(1)), sid))
            elif loc == 'agent_stream.py:739':
                for tm in R_TCALLS.finditer(msg):
                    cur.execute("INSERT INTO tool_calls(ts,date,tool,session_id) VALUES(?,?,?,?)",
                                (ts, d, tm.group(1), sid))
            elif loc == 'agent_stream.py:798':
                sm = R_TRES.search(msg)
                if sm:
                    cur.execute("INSERT INTO tool_results(ts,date,tool,dur_s,out_chars,session_id) VALUES(?,?,?,?,?,?)",
                                (ts, d, sm.group(1), float(sm.group(2)), len(sm.group(3)), sid))
            elif loc == 'agent_stream.py:964':
                sm = R_DONE.search(msg)
                if sm:
                    cur.execute("INSERT INTO session_done(ts,date,turns,session_id) VALUES(?,?,?,?)",
                                (ts, d, int(sm.group(1)), sid))
            elif loc == 'agent_stream.py:1954':
                sm = R_COMPA.search(msg)
                if sm:
                    cur.execute("INSERT INTO compressions(ts,date,hour,kind,ctx_before,budget,turns_removed,session_id) VALUES(?,?,?,?,?,?,?,?)",
                                (ts, d, hour, 'trim_turns', int(sm.group(1)), int(sm.group(2)), int(sm.group(4)), sid))
            elif loc == 'agent_stream.py:1938':
                sm = R_COMPB.search(msg)
                if sm:
                    cur.execute("INSERT INTO compressions(ts,date,hour,kind,ctx_before,budget,msgs_before,msgs_after,tokens_after,session_id) VALUES(?,?,?,?,?,?,?,?,?,?)",
                                (ts, d, hour, 'compress_all', int(sm.group(1)), int(sm.group(2)),
                                 int(sm.group(4)), int(sm.group(5)), int(sm.group(7)), sid))
            elif loc == 'agent_stream.py:1979':
                sm = R_COMPD.search(msg)
                if sm:
                    cur.execute("""UPDATE compressions SET turns_removed=?, msgs_before=?, msgs_after=?, tokens_after=?
                                   WHERE id=(SELECT MAX(id) FROM compressions)""",
                                (int(sm.group(1)), int(sm.group(2)), int(sm.group(3)), int(sm.group(5))))
            elif loc == 'agent_stream.py:1691':
                sm = R_HISTR.search(msg)
                if sm:
                    cur.execute("INSERT INTO truncations(ts,date,scope,tool,from_chars,to_chars,session_id) VALUES(?,?,?,?,?,?,?)",
                                (ts, d, 'history', f"n={sm.group(1)}", 0, int(sm.group(2)), sid))
            elif loc == 'agent_stream.py:824':
                sm = R_CURTR.search(msg)
                if sm:
                    cur.execute("INSERT INTO truncations(ts,date,scope,tool,from_chars,to_chars,session_id) VALUES(?,?,?,?,?,?,?)",
                                (ts, d, 'current', sm.group(1), int(sm.group(2)), int(sm.group(3)), sid))
            elif loc == 'agent_stream.py:1388':
                sm = R_RTRUNC.search(msg)
                if sm:
                    cur.execute("INSERT INTO reasoning_trunc(ts,date,from_chars,to_chars) VALUES(?,?,?,?)",
                                (ts, d, int(sm.group(1)), int(sm.group(2))))
            elif loc in ('agent_event_handler.py:70', 'agent_stream.py:693'):
                if msg.strip().startswith('💭'):
                    cur.execute("INSERT INTO thinking(ts,date,source,session_id) VALUES(?,?,?,?)", (ts, d, loc, sid))
            elif loc == 'summarizer.py:309':
                sm = R_FLUSH.search(msg)
                if sm:
                    cur.execute("INSERT INTO memflush(ts,date,reason,msgs) VALUES(?,?,?,?)",
                                (ts, d, sm.group(1), int(sm.group(2))))
            elif loc == 'agent_stream.py:421':
                sm = R_ART.search(msg)
                if sm:
                    cur.execute("INSERT INTO artifacts(ts,date,path,atype) VALUES(?,?,?,?)",
                                (ts, d, sm.group(1)[:200], sm.group(2)))
            elif loc == 'scheduler_service.py:89':
                sm = R_SCHED.search(msg)
                if sm:
                    cur.execute("INSERT INTO sched_tasks(ts,date,task_id,title) VALUES(?,?,?,?)",
                                (ts, d, sm.group(1), sm.group(2)[:100]))
            if lvl in ('ERROR', 'WARNING'):
                cur.execute("INSERT INTO errors(ts,date,level,loc,msg) VALUES(?,?,?,?,?)",
                            (ts, d, lvl, loc, msg[:150]))
            if n % 30000 == 0:
                con.commit()
    con.commit()
    cnt = cur.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    days = cur.execute("SELECT MIN(date), MAX(date) FROM requests").fetchone()
    con.close()
    print(f"[extract] {n} lines -> {db_path}  (requests={cnt}, span={days[0]} ~ {days[1]})")


# ── 阶段 2：明细期统计 ───────────────────────────────────────────────────────

def analyze(db_path, args):
    import numpy as np
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    q = lambda sql, a=(): con.execute(sql, a).fetchall()
    q1 = lambda sql, a=(): con.execute(sql, a).fetchone()[0]
    S = {}

    S['req_total'] = q1("SELECT COUNT(*) FROM requests")
    S['days'] = [r[0] for r in q("SELECT DISTINCT date FROM requests ORDER BY date")]
    S['sess_total'] = q1("SELECT COUNT(*) FROM sessions")
    S['comp_total'] = q1("SELECT COUNT(*) FROM compressions")
    S['think_total'] = q1("SELECT COUNT(*) FROM thinking")
    S['tc_total'] = q1("SELECT COUNT(*) FROM tool_calls")
    S['err_total'] = q1("SELECT COUNT(*) FROM errors WHERE level='ERROR'")
    S['warn_total'] = q1("SELECT COUNT(*) FROM errors WHERE level='WARNING'")
    r = q("SELECT AVG(n_msgs), MAX(n_msgs), AVG(n_turns) FROM requests")[0]
    S['msg_avg'], S['msg_max'], S['turns_avg'] = round(r[0], 1), r[1], round(r[2], 1)
    S['msg_median'] = q("SELECT n_msgs FROM requests ORDER BY n_msgs LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM requests)")[0][0]
    nm = sorted(r[0] for r in q("SELECT n_msgs FROM requests"))
    S['nmsg_p90'] = int(np.percentile(nm, 90)); S['nmsg_p99'] = int(np.percentile(nm, 99))

    # 日序列
    S['daily_req'] = {r['date']: r['c'] for r in q("SELECT date, COUNT(*) c FROM requests GROUP BY date")}
    S['daily_comp'] = {r['date']: r['c'] for r in q("SELECT date, COUNT(*) c FROM compressions GROUP BY date")}
    S['daily_think'] = {r['date']: r['c'] for r in q("SELECT date, COUNT(*) c FROM thinking GROUP BY date")}
    S['daily_trunc'] = {r['date']: r['c'] for r in q("SELECT date, COUNT(*) c FROM truncations GROUP BY date")}

    # 压缩解剖
    S['compA'] = q1("SELECT COUNT(*) FROM compressions WHERE kind='trim_turns'")
    S['compB'] = q1("SELECT COUNT(*) FROM compressions WHERE kind='compress_all'")
    r = q("SELECT AVG(ctx_before), MAX(ctx_before) FROM compressions")[0]
    S['ctx_avg'], S['ctx_max'] = round(r[0]), r[1]
    S['ctx_median'] = q("SELECT ctx_before FROM compressions ORDER BY ctx_before LIMIT 1 OFFSET (SELECT COUNT(*)/2 FROM compressions)")[0][0]
    S['ctx_gt100k_pct'] = round(100.0 * q1("SELECT COUNT(*) FROM compressions WHERE ctx_before>100000") / max(S['comp_total'], 1), 1)
    r = q("SELECT AVG(1.0*tokens_after/ctx_before), AVG(msgs_before), AVG(msgs_after) FROM compressions WHERE kind='compress_all' AND tokens_after IS NOT NULL")[0]
    S['compB_ratio'] = round(100 * r[0], 1)
    S['compB_msg_before'], S['compB_msg_after'] = round(r[1], 1), round(r[2], 1)
    S['ctx_vals'] = [r[0] for r in q("SELECT ctx_before FROM compressions")]

    # 会话维度（turns 表 MAX(turn_no) 为准）
    rows = q("SELECT session_id, MAX(turn_no) m FROM turns GROUP BY session_id")
    tv = [r['m'] for r in rows if r['m'] > 0]
    S['sess_n'] = len(tv)
    S['sess_avg'] = round(float(np.mean(tv)), 1)
    S['sess_med'] = int(np.median(tv))
    S['sess_max'] = int(np.max(tv))
    bins = [0, 10, 20, 40, 80, 100000]
    a = np.array(tv)
    S['sess_bins'] = [int(np.sum((a > bins[i]) & (a <= bins[i + 1]))) for i in range(5)]
    S['sess_gt40'] = int(np.sum(a > 40))
    S['sess_gt40_pct'] = round(100.0 * S['sess_gt40'] / S['sess_n'], 1)
    rpc = {r['session_id']: r['c'] for r in q("SELECT session_id, COUNT(*) c FROM requests GROUP BY session_id")}
    long_ids = {r['session_id'] for r in rows if r['m'] > 40}
    S['req_in_long_pct'] = round(100.0 * sum(c for k, c in rpc.items() if k in long_ids) / max(sum(rpc.values()), 1), 1)
    dur = [r['sec'] for r in q("""SELECT (strftime('%s', d.ts) - strftime('%s', s.ts_start)) sec
                                  FROM sessions s JOIN session_done d ON d.session_id=s.id WHERE sec>0""")]
    if dur:
        S['dur_med_min'] = round(float(np.median(dur)) / 60, 1)
        S['dur_max_min'] = round(max(dur) / 60, 1)

    # 工具维度
    S['tool_calls'] = {r['tool']: r['c'] for r in q("SELECT tool, COUNT(*) c FROM tool_calls GROUP BY tool ORDER BY c DESC LIMIT 12")}
    S['tool_out'] = {r['tool']: r['s'] for r in q("SELECT tool, SUM(out_chars) s FROM tool_results GROUP BY tool ORDER BY s DESC LIMIT 12")}
    S['trunc_cur'] = q1("SELECT COUNT(*) FROM truncations WHERE scope='current'")
    S['trunc_hist'] = q1("SELECT COUNT(*) FROM truncations WHERE scope='history'")
    S['trunc_by_tool'] = [(x['tool'], x['c'], x['saved']) for x in q(
        "SELECT tool, COUNT(*) c, SUM(from_chars-to_chars) saved FROM truncations WHERE scope='current' GROUP BY tool ORDER BY c DESC")]
    S['trunc_saved_chars'] = q1("SELECT COALESCE(SUM(from_chars-to_chars),0) FROM truncations WHERE scope='current'")
    r = q("SELECT COUNT(*) c, AVG(from_chars) af, MAX(from_chars) mf, SUM(from_chars-to_chars) saved FROM truncations WHERE tool='web_fetch'")[0]
    S['wf_n'], S['wf_avg_from'], S['wf_max_from'], S['wf_saved'] = r['c'], round(r['af'] or 0), r['mf'], r['saved'] or 0
    S['wf_saved_pct'] = round(100.0 * S['wf_saved'] / max(S['trunc_saved_chars'], 1), 1)

    # 思考与可靠性
    S['think_by_src'] = {r['source']: r['c'] for r in q("SELECT source, COUNT(*) c FROM thinking GROUP BY source")}
    r = q("SELECT AVG(from_chars), AVG(to_chars), SUM(from_chars-to_chars) FROM reasoning_trunc")[0]
    S['rt_from'], S['rt_to'], S['rt_saved'] = round(r[0] or 0), round(r[1] or 0), r[2] or 0
    S['sched_exec'] = q1("SELECT COUNT(*) FROM sched_tasks")
    S['sched_fail'] = q1("SELECT COUNT(*) FROM errors WHERE loc LIKE '%integration.py:71%'")
    S['err_top'] = [(r['loc'], r['c']) for r in q(
        "SELECT loc, COUNT(*) c FROM errors WHERE level='ERROR' GROUP BY loc ORDER BY c DESC LIMIT 8")]
    S['warn_top'] = [(r['loc'], r['c']) for r in q(
        "SELECT loc, COUNT(*) c FROM errors WHERE level='WARNING' GROUP BY loc ORDER BY c DESC LIMIT 8")]

    # Token 估算模型
    req_pre = q1("SELECT COUNT(*) FROM requests WHERE date<?", (args.opt_date,))
    req_post = q1("SELECT COUNT(*) FROM requests WHERE date>=?", (args.opt_date,))
    S['tok_fixed_pre'] = req_pre * args.sys_pre
    S['tok_fixed_post'] = req_post * args.sys_post
    S['tok_hist'] = int(q1("SELECT COALESCE(SUM(n_msgs),0) FROM requests") * args.hist_per_msg)
    S['tok_total'] = S['tok_fixed_pre'] + S['tok_fixed_post'] + S['tok_hist']
    S['tok_all_pre'] = int((req_pre + req_post) * args.sys_pre + S['tok_hist'])
    S['tok_all_post'] = int((req_pre + req_post) * args.sys_post + S['tok_hist'])
    S['save_pct'] = round(100 * (1 - S['tok_all_post'] / S['tok_all_pre']), 1)
    S['ndays'] = len(S['days'])

    con.close()
    return S


# ── 阶段 3：全周期拼接（官方 JSON + 日志期估算） ─────────────────────────────

def full_timeline(db_path, official_path, S, args):
    import numpy as np
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    F = {}
    off = json.load(open(official_path, encoding='utf-8'))
    con.execute("DELETE FROM official_daily")
    for r in off['daily_breakdown']:
        d = r['date'] if r['date'].startswith('20') else '2026-' + r['date']
        con.execute("INSERT INTO official_daily VALUES(?,?,?)", (d, r['weekday'], r['cost']))
    con.commit()

    F['off_total_cost'] = off['total_cost']
    F['off_total_req'] = off['total_requests']
    F['off_total_tokens'] = off['total_tokens']
    F['off_days'] = off['period_days']
    F['off_daily_cost'] = round(off['total_cost'] / off['period_days'], 2)
    F['off_daily_req'] = round(off['total_requests'] / off['period_days'])
    F['off_daily_tokens'] = round(off['total_tokens'] / off['period_days'] / 1e6, 1)
    F['off_price_per_m'] = off['total_cost'] / (off['total_tokens'] / 1e6)

    # 日志期逐日估算
    log_days = {}
    for r in con.execute("SELECT date, COUNT(*) c, SUM(n_msgs) m FROM requests GROUP BY date ORDER BY date"):
        sys_tok = args.sys_post if r['date'] >= args.opt_date else args.sys_pre
        est = r['c'] * sys_tok + (r['m'] or 0) * args.hist_per_msg
        log_days[r['date']] = {'req': r['c'], 'est_tokens': est,
                               'est_cost': round(est / 1e6 * F['off_price_per_m'], 2)}
    F['log_days'] = log_days
    F['log_est_cost_total'] = round(sum(v['est_cost'] for v in log_days.values()), 1)
    F['log_daily_req_avg'] = round(float(np.mean([v['req'] for v in log_days.values()])))
    F['log_daily_tokens_avg'] = round(sum(v['est_tokens'] for v in log_days.values()) / len(log_days) / 1e6, 1)

    off_series = {r['date']: r['cost'] for r in con.execute("SELECT date, cost FROM official_daily")}
    F['off_series'] = off_series
    all_dates = sorted(set(off_series) | set(log_days))
    F['all_dates'] = all_dates
    F['span'] = f"{all_dates[0]} ~ {all_dates[-1]}"
    F['span_days'] = len(all_dates)

    # 星期模式
    wd_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    wd_costs = {w: [] for w in wd_order}
    for r in con.execute("SELECT weekday, cost FROM official_daily"):
        wd_costs[r['weekday']].append(r['cost'])
    F['wd_order'] = wd_order
    F['wd_avg'] = [float(np.mean(wd_costs[w])) if wd_costs[w] else 0 for w in wd_order]
    F['wd_workday_avg'] = round(float(np.mean([c for w in wd_order[:5] for c in wd_costs[w]])), 2)
    F['wd_weekend_avg'] = round(float(np.mean([c for w in wd_order[5:] for c in wd_costs[w]])), 2)
    con.close()
    return F


# ── 阶段 4：可视化 ───────────────────────────────────────────────────────────

def visualize(S, F, out_dir, args):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    os.makedirs(out_dir, exist_ok=True)
    C_MAIN, C_WARN, C_OK, C_ACC, C_GRAY = '#2563eb', '#dc2626', '#16a34a', '#f59e0b', '#94a3b8'
    days = S['days']

    def savefig(name):
        plt.tight_layout()
        plt.savefig(os.path.join(str(out_dir), name), dpi=130, bbox_inches='tight')
        plt.close()
        print(f"  chart: {name}")

    # —— 明细期图表 ——
    # 01 日请求 vs 压缩
    fig, ax1 = plt.subplots(figsize=(10, 5))
    x = np.arange(len(days))
    reqs = [S['daily_req'].get(d, 0) for d in days]
    comps = [S['daily_comp'].get(d, 0) for d in days]
    ax1.bar(x, reqs, color=C_MAIN, alpha=0.75, label='API 请求数')
    ax1.set_ylabel('请求数', color=C_MAIN); ax1.tick_params(axis='y', labelcolor=C_MAIN)
    ax1.set_xticks(x); ax1.set_xticklabels([d[5:] for d in days], rotation=45)
    ax2 = ax1.twinx()
    ax2.plot(x, comps, color=C_WARN, marker='o', lw=2, label='压缩事件')
    ax2.set_ylabel('压缩事件数', color=C_WARN); ax2.tick_params(axis='y', labelcolor=C_WARN)
    ax1.set_title('每日 API 请求量 vs 上下文压缩事件', fontsize=11)
    fig.legend(loc='upper left', bbox_to_anchor=(0.10, 0.88))
    savefig('01_daily_requests_vs_compressions.png')

    # 02 token 结构
    fig, ax = plt.subplots(figsize=(9, 5))
    vals = [S['tok_fixed_pre'] / 1e9, S['tok_fixed_post'] / 1e9, S['tok_hist'] / 1e9]
    labels2 = ['固定开销(优化前)', '固定开销(优化后)', '历史消息回读']
    bars = ax.bar(labels2, vals, color=[C_WARN, C_OK, C_MAIN], alpha=0.8)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f'{v:.2f}B\n({100*v/sum(vals):.1f}%)', ha='center', fontsize=10)
    ax.set_ylabel('估算 input tokens (B)')
    ax.set_title(f'input tokens 结构拆解（总 ~{S["tok_total"]/1e9:.2f}B）', fontsize=11)
    savefig('02_token_structure.png')

    # 03 优化情景
    fig, ax = plt.subplots(figsize=(8, 5))
    scen = ['全程未优化', '实际混合', '全程已优化']
    toks = [S['tok_all_pre'] / 1e9, S['tok_total'] / 1e9, S['tok_all_post'] / 1e9]
    bars = ax.bar(scen, toks, color=[C_WARN, C_ACC, C_OK], alpha=0.85)
    for b, v in zip(bars, toks):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f'{v:.2f}B', ha='center', fontsize=11, fontweight='bold')
    ax.set_ylabel('估算 input tokens (B)')
    ax.set_title(f'优化效果情景对比：全程已优化可省 {S["save_pct"]}%', fontsize=11)
    savefig('03_optimization_scenarios.png')

    # 04 压缩上下文分布
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(S['ctx_vals'], bins=30, color=C_WARN, alpha=0.75, edgecolor='white')
    ax.axvline(np.median(S['ctx_vals']), color='black', ls=':', label=f'中位 {int(np.median(S["ctx_vals"]))//1000}K')
    ax.set_xlabel('压缩触发时上下文 tokens'); ax.set_ylabel('事件数')
    ax.set_title(f'压缩事件上下文分布（n={len(S["ctx_vals"])}，{S["ctx_gt100k_pct"]}% 超 100K）', fontsize=11)
    ax.legend()
    savefig('04_compression_context_hist.png')

    # 05 会话长度分布
    labels5 = ['≤10', '11-20', '21-40', '41-80', '>80']
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels5, S['sess_bins'], color=C_MAIN, alpha=0.85)
    for b, v in zip(bars, S['sess_bins']):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f'{v}\n({100*v/S["sess_n"]:.1f}%)', ha='center', fontsize=10)
    ax.set_xlabel('会话 turns 区间'); ax.set_ylabel('会话数')
    ax.set_title(f'会话长度分布（n={S["sess_n"]}，中位 {S["sess_med"]} turns）：>40 turns 占 {S["sess_gt40_pct"]}%，承载 {S["req_in_long_pct"]}% 请求', fontsize=11)
    savefig('05_session_turns_dist.png')

    # 06 工具调用与回读
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(12, 5))
    tools = list(S['tool_calls'].keys())[:8]
    axl.barh(tools[::-1], [S['tool_calls'][t] for t in tools][::-1], color=C_MAIN, alpha=0.8)
    axl.set_title('工具调用次数', fontsize=11)
    tools_o = list(S['tool_out'].keys())[:8]
    axr.barh(tools_o[::-1], [S['tool_out'][t] / 1000 for t in tools_o][::-1], color=C_ACC, alpha=0.85)
    axr.set_title('工具输出回读量（日志可见，K chars）', fontsize=11)
    savefig('06_tool_calls_output.png')

    # 09 截断分析
    fig, ax = plt.subplots(figsize=(9, 5))
    if S['trunc_by_tool']:
        tt = [t[0] for t in S['trunc_by_tool'][:8]]
        tc = [t[1] for t in S['trunc_by_tool'][:8]]
        ts_ = [(t[2] or 0) / 1000 for t in S['trunc_by_tool'][:8]]
        x = np.arange(len(tt))
        ax.bar(x - 0.2, tc, 0.4, color=C_MAIN, alpha=0.8, label='截断次数')
        ax.bar(x + 0.2, ts_, 0.4, color=C_OK, alpha=0.8, label='截断省下字符(K)')
        ax.set_xticks(x); ax.set_xticklabels(tt, rotation=30, ha='right')
        ax.legend()
    ax.set_title(f'当前轮工具结果截断：{S["trunc_cur"]} 次，累计截掉 {S["trunc_saved_chars"]/1e6:.1f}M chars（web_fetch 占 {S["wf_saved_pct"]}%）', fontsize=11)
    savefig('09_truncations.png')

    # 10 事件日趋势
    fig, ax = plt.subplots(figsize=(10, 5))
    xd = np.arange(len(days))
    ax.plot(xd, [S['daily_think'].get(d, 0) for d in days], marker='o', label='思考事件', color=C_ACC)
    ax.plot(xd, [S['daily_trunc'].get(d, 0) for d in days], marker='s', label='截断事件', color=C_OK)
    ax.plot(xd, comps, marker='^', label='压缩事件', color=C_WARN)
    ax.set_xticks(xd); ax.set_xticklabels([d[5:] for d in days], rotation=45)
    ax.set_ylabel('事件数'); ax.legend()
    ax.set_title('思考 / 截断 / 压缩 事件日趋势', fontsize=11)
    savefig('10_daily_events_trend.png')

    # 12 错误热点
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(13, 5))
    el = S['err_top'][:8]
    axl.barh([e[0] for e in el][::-1], [e[1] for e in el][::-1], color=C_WARN, alpha=0.8)
    axl.set_title('ERROR 热点 TOP8', fontsize=11)
    wl = S['warn_top'][:8]
    axr.barh([w[0] for w in wl][::-1], [w[1] for w in wl][::-1], color=C_ACC, alpha=0.85)
    axr.set_title('WARNING 热点 TOP8', fontsize=11)
    savefig('12_error_hotspots.png')

    # —— 全周期图表 ——
    if F:
        all_dates = F['all_dates']
        off_series = F['off_series']
        log_days = F['log_days']
        x = np.arange(len(all_dates))

        # v1 全时间线
        fig, ax = plt.subplots(figsize=(14, 5.5))
        ax.bar(x, [off_series.get(d, 0) for d in all_dates], color=C_MAIN, alpha=0.75, label='官方实际费用')
        ax.bar(x, [log_days.get(d, {}).get('est_cost', 0) for d in all_dates], color=C_ACC, alpha=0.85,
               label='日志期估算费用')
        log_start_idx = all_dates.index(days[0])
        ax.axvline(log_start_idx - 0.5, color=C_WARN, ls='--', alpha=0.7)
        ax.set_xticks(x[::3]); ax.set_xticklabels([all_dates[i][5:] for i in range(0, len(all_dates), 3)], rotation=45)
        ax.set_ylabel('费用（¥/天）')
        ax.set_title(f'全量时间线：每日 API 费用（{F["span"]}，{F["span_days"]} 天）', fontsize=12)
        ax.legend()
        savefig('v1_full_timeline_daily_cost.png')

        # v2 星期模式
        wd_map = {'Mon': '周一', 'Tue': '周二', 'Wed': '周三', 'Thu': '周四', 'Fri': '周五', 'Sat': '周六', 'Sun': '周日'}
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar([wd_map[w] for w in F['wd_order']], F['wd_avg'], color=[C_MAIN] * 5 + [C_GRAY] * 2, alpha=0.85)
        for b, v in zip(bars, F['wd_avg']):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.1, f'¥{v:.1f}', ha='center', fontsize=10)
        ax.axhline(F['wd_workday_avg'], color=C_MAIN, ls=':', label=f'工作日均 ¥{F["wd_workday_avg"]}')
        ax.axhline(F['wd_weekend_avg'], color=C_GRAY, ls=':', label=f'周末均 ¥{F["wd_weekend_avg"]}')
        ax.set_ylabel('平均每日费用（¥）')
        ax.set_title('星期模式：工作日 vs 周末', fontsize=11)
        ax.legend()
        savefig('v2_weekday_pattern.png')

        # v3 累计费用
        cum = np.cumsum([off_series.get(d, 0) for d in all_dates])
        log_cum = cum[-1] + np.cumsum([log_days.get(d, {}).get('est_cost', 0) for d in all_dates])
        fig, ax = plt.subplots(figsize=(11, 5))
        ax.plot(x, cum, color=C_MAIN, lw=2, label='官方累计（实际）')
        ax.plot(x, log_cum, color=C_ACC, lw=2, ls='--', label='日志期累计（估算）')
        ax.set_xticks(x[::3]); ax.set_xticklabels([all_dates[i][5:] for i in range(0, len(all_dates), 3)], rotation=45)
        ax.set_ylabel('累计费用（¥）')
        ax.set_title(f'累计费用曲线：官方 ¥{F["off_total_cost"]} + 日志期估算 ¥{F["log_est_cost_total"]}', fontsize=11)
        ax.legend()
        savefig('v3_cumulative_cost.png')

        # v4 两期对比
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
        periods = ['官方期', '日志期']
        metrics = [
            ('日均请求数', [F['off_daily_req'], F['log_daily_req_avg']]),
            ('日均 Token（M）', [F['off_daily_tokens'], F['log_daily_tokens_avg']]),
            ('日均费用（¥）', [F['off_daily_cost'], round(F['log_est_cost_total'] / len(log_days), 2)]),
        ]
        for ax, (title, vals) in zip(axes, metrics):
            bars = ax.bar(periods, vals, color=[C_MAIN, C_ACC], alpha=0.85)
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v * 1.01, f'{v}', ha='center', fontsize=11, fontweight='bold')
            ax.set_title(title, fontsize=11)
        plt.suptitle('两期日均对比', fontsize=12, y=1.03)
        savefig('v4_period_comparison.png')

        # v5 节省情景
        fig, ax = plt.subplots(figsize=(10, 5))
        scen = ['现状基线', 'P0 已落地', 'P0+P1 全落地']
        costs = [F['off_total_cost'], round(F['off_total_cost'] * 0.5, 1), round(F['off_total_cost'] * 0.35, 1)]
        bars = ax.bar(scen, costs, color=[C_WARN, C_ACC, C_OK], alpha=0.85)
        for b, v in zip(bars, costs):
            ax.text(b.get_x() + b.get_width() / 2, v + 3, f'¥{v}', ha='center', fontsize=11, fontweight='bold')
        ax.set_ylabel('30天费用（¥）')
        ax.set_title('全周期费用情景（官方基线）', fontsize=11)
        savefig('v5_savings_scenarios.png')


# ── 摘要输出 ─────────────────────────────────────────────────────────────────

def print_summary(S, F):
    print('\n========== 明细期统计 ==========')
    print(f"请求 {S['req_total']} | 会话 {S['sess_total']} | 压缩 {S['comp_total']} (trim {S['compA']} + 全压 {S['compB']}) | 思考 {S['think_total']}")
    print(f"压缩上下文 均{S['ctx_avg']}/中{S['ctx_median']}/max{S['ctx_max']}，>100K 占 {S['ctx_gt100k_pct']}%；全压 {S['compB_msg_before']}→{S['compB_msg_after']} msg")
    print(f"会话 turns 均{S['sess_avg']}/中{S['sess_med']}/max{S['sess_max']}；>40 turns {S['sess_gt40_pct']}% 会话承载 {S['req_in_long_pct']}% 请求")
    print(f"截断: 当前轮 {S['trunc_cur']} 次省 {S['trunc_saved_chars']/1e6:.1f}M chars（web_fetch {S['wf_saved_pct']}%，均原文 {S['wf_avg_from']}）")
    print(f"调度执行 {S['sched_exec']} / 投递失败 {S['sched_fail']}；ERROR {S['err_total']} / WARNING {S['warn_total']}")
    print(f"Token 估算: 实际混合 {S['tok_total']/1e9:.2f}B | 全程未优化 {S['tok_all_pre']/1e9:.2f}B → 全程已优化 {S['tok_all_post']/1e9:.2f}B（省 {S['save_pct']}%）")
    if F:
        print('\n========== 全周期 ==========')
        print(f"时间线 {F['span']}（{F['span_days']} 天）")
        print(f"官方期: ¥{F['off_total_cost']} / {F['off_total_req']} 请求 / {F['off_total_tokens']/1e9:.2f}B tokens（日均 ¥{F['off_daily_cost']}）")
        print(f"日志期估算: ¥{F['log_est_cost_total']}（日均 ¥{round(F['log_est_cost_total']/len(F['log_days']),2)}）")
        print(f"星期模式: 工作日 ¥{F['wd_workday_avg']} vs 周末 ¥{F['wd_weekend_avg']}")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='CowAgent 运行日志 Token 消耗通用分析器')
    ap.add_argument('--log', default=str(TMP_DIR / 'run.log'), help='run.log 路径')
    ap.add_argument('--db', default=str(TMP_DIR / 'runlog.db'), help='SQLite 输出路径')
    ap.add_argument('--official', default=str(SPEC_DIR / 'scripts' / 'deepseek_consumption.json'),
                    help='官方消耗 JSON（DeepSeek 平台导出）')
    ap.add_argument('--out', default=str(TMP_DIR / 'token-charts'), help='图表输出目录')
    ap.add_argument('--no-charts', action='store_true', help='跳过图表生成')
    ap.add_argument('--no-timeline', action='store_true', help='跳过全周期拼接（仅明细期）')
    ap.add_argument('--stats-only', action='store_true', help='跳过解析，复用已有 DB')
    ap.add_argument('--json', action='store_true', help='统计结果另存 JSON 到 tmp/')
    ap.add_argument('--sys-pre', type=int, default=118000, help='优化前 system 固定开销 tokens/请求')
    ap.add_argument('--sys-post', type=int, default=18000, help='优化后 system 固定开销 tokens/请求')
    ap.add_argument('--opt-date', default='2026-08-07', help='优化切换日（该日起按 sys-post 计）')
    ap.add_argument('--hist-per-msg', type=int, default=300, help='历史消息均量 tokens/条')
    args = ap.parse_args()

    if not args.stats_only:
        extract(args.log, args.db)

    S = analyze(args.db, args)

    F = None
    if not args.no_timeline and os.path.exists(args.official):
        F = full_timeline(args.db, args.official, S, args)

    print_summary(S, F)

    if args.json:
        def default(o):
            try:
                return dict(o)
            except Exception:
                return str(o)
        out = TMP_DIR / f'token-stats-{date.today().isoformat()}.json'
        payload = {'detail': {k: v for k, v in S.items() if k != 'ctx_vals'}, 'timeline': F}
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=default), encoding='utf-8')
        print(f"\n[json] {out}")

    if not args.no_charts:
        visualize(S, F, args.out, args)
        print(f"\n[charts] {args.out}")


if __name__ == '__main__':
    main()
