#!/usr/bin/env python3
"""
conv-log-analyzer.py — 会话日志通用分析器（extract → analyze → visualize 一体化）

功能：
  将 conversation-log/db-sessions/ 导出的会话 Markdown（FORMAT.md 规范）全量解析入 SQLite，
  产出话题分布 / 行为分型 / 处理过程量化 / 工具模式 / 迭代纠偏等统计与图表。

用法：
  python3 scripts/kb-stat/conv-log-analyzer.py                    # 全流程（解析+统计+图表）
  python3 scripts/kb-stat/conv-log-analyzer.py --no-charts        # 只解析+统计（纯文本/JSON）
  python3 scripts/kb-stat/conv-log-analyzer.py --stats-only       # 跳过解析，复用已有 DB 出统计
  python3 scripts/kb-stat/conv-log-analyzer.py --src DIR          # 指定会话目录（默认 conversation-log/db-sessions）
  python3 scripts/kb-stat/conv-log-analyzer.py --db PATH          # 指定 SQLite 路径（默认 tmp/convlog.db）
  python3 scripts/kb-stat/conv-log-analyzer.py --out DIR          # 图表输出目录（默认 tmp/conv-charts）
  python3 scripts/kb-stat/conv-log-analyzer.py --json             # 统计结果另存 JSON（tmp/convlog-stats-YYYY-MM-DD.json）

依赖：Python3 标准库 + matplotlib/numpy（仅图表阶段需要，可用 --no-charts 跳过）
产出案例：knowledge/02_rd/02_project/03_kb_cowagent/2026-08-08-conversation-log-deep-analysis.md
"""

import argparse
import glob
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.workspace import WORKSPACE_ROOT, CONV_LOG_DIR, TMP_DIR  # sr-008

# ── 会话文件结构正则（FORMAT.md / EXPORT_README.md 规范） ─────────────────────

META_ID = re.compile(r'\*\*会话 ID\*\*: `(.+?)`')
META_CHAN = re.compile(r'\*\*渠道\*\*: (\S+)')
META_TIME = re.compile(r'\*\*创建时间\*\*: (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})')
META_MSGS = re.compile(r'\*\*消息数\*\*: (\d+)')
ROUND_RE = re.compile(r'^## 回合 (\d+) - (\d{2}:\d{2})\s*$', re.M)
SEC_RE = re.compile(r'^### (🗣️ 用户|💭 思考|🛠️ 工具调用|💬 回复)\s*$', re.M)
TOOL_ROW = re.compile(r'^\|\s*\d+\s*\|\s*([a-z_][\w]*)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', re.M)
TRAIL_SEP = re.compile(r'\n*---\s*$')

SCHEMA = """
DROP TABLE IF EXISTS sessions; CREATE TABLE sessions(
  id INTEGER PRIMARY KEY, file TEXT, session_id TEXT, channel TEXT,
  date TEXT, time TEXT, hour INT, msg_count INT, title TEXT,
  n_rounds INT, n_user_real INT, n_user_empty INT, n_think INT, think_chars INT,
  n_reply INT, reply_chars INT, n_toolcalls INT);
DROP TABLE IF EXISTS rounds; CREATE TABLE rounds(
  id INTEGER PRIMARY KEY, session_fk INT, round_no INT, time TEXT,
  user_text TEXT, think TEXT, reply TEXT, n_tools INT);
DROP TABLE IF EXISTS toolcalls; CREATE TABLE toolcalls(
  id INTEGER PRIMARY KEY, session_fk INT, round_no INT, tool TEXT, params TEXT);
CREATE INDEX idx_tc_sess ON toolcalls(session_fk);
CREATE INDEX idx_rounds_sess ON rounds(session_fk);
"""

# ── 分类规则（按序匹配，命中即止；可按业务演进扩充） ─────────────────────────

TOPIC_RULES = [
    ('行业调研/定时跟踪', r'搜索.*最新动态|专题跟踪|追踪|调研专题|跟踪.*动态|日报|每日'),
    ('超节点/服务器硬件', r'超节点|supernode|superpod|整机柜|服务器|GPU|NVLink|BMC|固件|散热|液冷|电源|I2C|JTAG|SPI|PCIe|CXL|HBM|存储|RAS|芯片|计算节点'),
    ('知识库工程/治理', r'知识库|knowledge|索引|归档|SSOT|index|wiki|文档体系|目录'),
    ('AI技术/Agent', r'大模型|LLM|Agent|RAG|推理|训练|MoE|prompt|提示词|skill|AI编程|cowagent|token'),
    ('方法论/规范', r'方法论|范式|原则|框架|spec|meth-|检查清单|checklist'),
    ('周报/报告', r'周报|月报|weekly|报告生成|工作总结'),
    ('职场/管理/个人', r'职业|团队|管理|冲突|面试|绩效|组织|人才'),
    ('系统排障/运维', r'修复|bug|挂死|失效|失败|排查|诊断|故障'),
    ('数据分析/处理', r'分析.*数据|统计|可视化|图表'),
]
TOPIC_DEFAULT = '其他'

ITER_PAT = re.compile(r'不对|不是|重新|再(来|次|生成|分析|优化)|修改|优化|补充|继续|不够|换个|调整|改进|完善|遗漏|缺失|不一致')


def classify_topic(text):
    for name, pat in TOPIC_RULES:
        if re.search(pat, text, re.I):
            return name
    return TOPIC_DEFAULT


def classify_behavior(tc):
    """按工具构成比分型：联网调研型 / 文档生产型 / 本地操作排障型 / 混合型 / 纯对话"""
    total = sum(tc.values())
    if total == 0:
        return '纯对话'
    web = tc.get('web_fetch', 0) + tc.get('web_search', 0) + tc.get('browser', 0)
    doc = tc.get('edit', 0) + tc.get('write', 0)
    shell = tc.get('bash', 0)
    rd = tc.get('read', 0) + tc.get('ls', 0) + tc.get('grep', 0) + tc.get('search_files', 0)
    if web / total > 0.45:
        return '联网调研型'
    if doc / total > 0.35:
        return '文档生产型'
    if (shell + rd) / total > 0.6:
        return '本地操作/排障型'
    return '混合型'


# ── 阶段 1：解析入库 ─────────────────────────────────────────────────────────

def parse_session_file(path):
    text = open(path, 'r', encoding='utf-8', errors='replace').read()
    fname = os.path.basename(path)
    title_m = re.match(r'# 💬 对话: (.+)', text)
    title = title_m.group(1).strip() if title_m else fname[:-3]
    sid = META_ID.search(text)
    chan = META_CHAN.search(text)
    ctime = META_TIME.search(text)
    nmsg = META_MSGS.search(text)
    dt, hm = (ctime.group(1), ctime.group(2)) if ctime else (fname[:10], '00:00')

    rounds = []
    marks = list(ROUND_RE.finditer(text))
    for i, rm in enumerate(marks):
        body = text[rm.end():marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        sec = {'user': '', 'think': '', 'reply': '', 'tools': []}
        smarks = list(SEC_RE.finditer(body))
        for j, sm in enumerate(smarks):
            content = body[sm.end():smarks[j + 1].start() if j + 1 < len(smarks) else len(body)].strip()
            name = sm.group(1)
            if name == '🗣️ 用户':
                sec['user'] = TRAIL_SEP.sub('', content).strip()
            elif name == '💭 思考':
                sec['think'] = content
            elif name == '💬 回复':
                sec['reply'] = content
            elif name == '🛠️ 工具调用':
                sec['tools'] = [(t.group(1), t.group(2)[:200]) for t in TOOL_ROW.finditer(content)]
        rounds.append({'no': int(rm.group(1)), 'time': rm.group(2), **sec})

    return {
        'file': fname, 'session_id': sid.group(1) if sid else '',
        'channel': chan.group(1) if chan else 'scheduler',
        'date': dt, 'time': hm, 'hour': int(hm[:2]),
        'msg_count': int(nmsg.group(1)) if nmsg else 0,
        'title': title[:120], 'rounds': rounds,
    }


def extract(src_dir, db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    cur = con.cursor()
    files = [f for f in sorted(glob.glob(os.path.join(str(src_dir), '*.md')))
             if not f.endswith('index.md')]
    for path in files:
        s = parse_session_file(path)
        rs = s['rounds']
        cur.execute("""INSERT INTO sessions(file,session_id,channel,date,time,hour,msg_count,title,
                       n_rounds,n_user_real,n_user_empty,n_think,think_chars,n_reply,reply_chars,n_toolcalls)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (s['file'], s['session_id'], s['channel'], s['date'], s['time'], s['hour'],
                     s['msg_count'], s['title'], len(rs),
                     sum(1 for r in rs if r['user'] and not r['user'].startswith('[空消息]')),
                     sum(1 for r in rs if r['user'].startswith('[空消息]')),
                     sum(1 for r in rs if r['think']), sum(len(r['think']) for r in rs),
                     sum(1 for r in rs if r['reply']), sum(len(r['reply']) for r in rs),
                     sum(len(r['tools']) for r in rs)))
        fk = cur.lastrowid
        for r in rs:
            cur.execute("INSERT INTO rounds(session_fk,round_no,time,user_text,think,reply,n_tools) VALUES(?,?,?,?,?,?,?)",
                        (fk, r['no'], r['time'], r['user'], r['think'], r['reply'], len(r['tools'])))
            for tool, params in r['tools']:
                cur.execute("INSERT INTO toolcalls(session_fk,round_no,tool,params) VALUES(?,?,?,?)",
                            (fk, r['no'], tool, params))
    con.commit()
    n = cur.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    con.close()
    print(f"[extract] {n} sessions -> {db_path}")
    return n


# ── 阶段 2：统计分析 ─────────────────────────────────────────────────────────

def analyze(db_path):
    import numpy as np
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    sessions = []
    for s in con.execute("SELECT * FROM sessions").fetchall():
        tools = {r['tool']: r['c'] for r in con.execute(
            "SELECT tool, COUNT(*) c FROM toolcalls WHERE session_fk=? GROUP BY tool", (s['id'],))}
        user_msgs = [r['user_text'] for r in con.execute(
            "SELECT user_text FROM rounds WHERE session_fk=? AND user_text!='' AND user_text NOT LIKE '[空消息]%'",
            (s['id'],))]
        blob = s['title'] + ' ' + ' '.join(m[:300] for m in user_msgs[:5])
        sessions.append({
            'date': s['date'], 'channel': s['channel'], 'topic': classify_topic(blob),
            'behavior': classify_behavior(tools), 'rounds': s['n_rounds'],
            'toolcalls': s['n_toolcalls'], 'tools': tools, 'user_real': len(user_msgs),
            'iter': sum(1 for m in user_msgs if ITER_PAT.search(m)),
            'empty': s['n_user_empty'],
        })

    n = len(sessions)
    stats = {'sessions_total': n}

    # 话题分布
    topic_cnt = Counter(s['topic'] for s in sessions)
    topic_tc = defaultdict(int)
    for s in sessions:
        topic_tc[s['topic']] += s['toolcalls']
    stats['topics'] = [{'topic': t, 'sessions': c, 'toolcalls': topic_tc[t],
                        'pct': round(100 * c / n, 1)} for t, c in topic_cnt.most_common()]

    # 行为分型
    beh_cnt = Counter(s['behavior'] for s in sessions)
    stats['behaviors'] = [{'behavior': b, 'sessions': c, 'pct': round(100 * c / n, 1)}
                          for b, c in beh_cnt.most_common()]

    # 话题×行为交叉
    cross = defaultdict(Counter)
    for s in sessions:
        cross[s['topic']][s['behavior']] += 1
    stats['topic_behavior_cross'] = {t: dict(cc) for t, cc in cross.items()}

    # 过程特征
    rounds_arr = np.array([s['rounds'] for s in sessions])
    tc_arr = np.array([s['toolcalls'] for s in sessions])
    stats['process'] = {
        'rounds_mean': round(float(rounds_arr.mean()), 1),
        'rounds_median': float(np.median(rounds_arr)),
        'rounds_p90': float(np.percentile(rounds_arr, 90)),
        'rounds_max': int(rounds_arr.max()),
        'toolcalls_mean': round(float(tc_arr.mean()), 1),
        'toolcalls_median': float(np.median(tc_arr)),
        'toolcalls_max': int(tc_arr.max()),
        'empty_ratio_mean': round(float(np.mean(
            [s['empty'] / (s['empty'] + s['user_real']) for s in sessions
             if s['empty'] + s['user_real'] > 0])) * 100, 1),
        'iter_sessions': sum(1 for s in sessions if s['iter'] > 0),
        'iter_sessions_pct': round(100 * sum(1 for s in sessions if s['iter'] > 0) / n),
    }

    # 月度趋势
    by_month = defaultdict(Counter)
    for s in sessions:
        by_month[s['date'][:7]][s['topic']] += 1
    stats['monthly'] = {m: dict(c) for m, c in sorted(by_month.items())}

    # 工具使用与转移
    all_tools = Counter()
    for s in sessions:
        all_tools.update(s['tools'])
    stats['tools_top'] = all_tools.most_common(15)
    bigrams = Counter()
    for s in con.execute("SELECT id FROM sessions").fetchall():
        seq = [r['tool'] for r in con.execute(
            "SELECT tool FROM toolcalls WHERE session_fk=? ORDER BY id", (s['id'],))]
        for a, b in zip(seq, seq[1:]):
            bigrams[(a, b)] += 1
    stats['tool_bigrams_top'] = [(f'{a}->{b}', c) for (a, b), c in bigrams.most_common(15)]

    # 渠道差异
    stats['channels'] = {}
    for ch in sorted({s['channel'] for s in sessions}):
        ss = [s for s in sessions if s['channel'] == ch]
        stats['channels'][ch] = {
            'sessions': len(ss),
            'rounds_mean': round(float(np.mean([x['rounds'] for x in ss]))),
            'toolcalls_mean': round(float(np.mean([x['toolcalls'] for x in ss]))),
            'iter_pct': round(100 * float(np.mean([1 if x['iter'] > 0 else 0 for x in ss]))),
        }

    con.close()
    return stats, sessions


def print_summary(stats):
    print('\n=== 话题分布 ===')
    for t in stats['topics']:
        print(f"  {t['topic']:<14} {t['sessions']:>4} 会话 ({t['pct']}%)  调用 {t['toolcalls']:>6}")
    print('\n=== 行为分型 ===')
    for b in stats['behaviors']:
        print(f"  {b['behavior']:<14} {b['sessions']:>4} ({b['pct']}%)")
    p = stats['process']
    print(f"\n=== 过程特征 ===\n回合 mean={p['rounds_mean']} median={p['rounds_median']} max={p['rounds_max']}")
    print(f"调用 mean={p['toolcalls_mean']} median={p['toolcalls_median']} max={p['toolcalls_max']}")
    print(f"空消息(自主继续)占比 mean={p['empty_ratio_mean']}%  纠偏会话 {p['iter_sessions']} ({p['iter_sessions_pct']}%)")
    print('\n=== 渠道差异 ===')
    for ch, c in stats['channels'].items():
        print(f"  {ch}: {c['sessions']} 会话, 均回合 {c['rounds_mean']}, 均调用 {c['toolcalls_mean']}, 纠偏占比 {c['iter_pct']}%")


# ── 阶段 3：可视化 ───────────────────────────────────────────────────────────

def visualize(stats, sessions, out_dir):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'WenQuanYi Zen Hei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    os.makedirs(out_dir, exist_ok=True)
    C = ['#2563eb', '#f59e0b', '#16a34a', '#7c3aed', '#dc2626', '#94a3b8', '#0ea5e9', '#f97316', '#65a30d']

    def savefig(name):
        plt.tight_layout()
        plt.savefig(os.path.join(str(out_dir), name), dpi=130, bbox_inches='tight')
        plt.close()
        print(f"  chart: {name}")

    # 1 话题分布双环
    items = [(t['topic'], t['sessions']) for t in stats['topics']]
    tc_items = [(t['topic'], t['toolcalls']) for t in stats['topics']]
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(13, 5.5))
    axl.pie([i[1] for i in items], labels=[f"{i[0]}\n{i[1]}个" for i in items],
            colors=C[:len(items)], autopct='%1.0f%%', startangle=90, textprops={'fontsize': 9})
    axl.set_title('话题分布（会话数）', fontsize=12)
    axr.pie([i[1] for i in tc_items], labels=[f"{i[0]}\n{i[1]/1000:.1f}K次" for i in tc_items],
            colors=C[:len(tc_items)], autopct='%1.0f%%', startangle=90, textprops={'fontsize': 9})
    axr.set_title('话题分布（工具调用量）', fontsize=12)
    savefig('c1_topic_distribution.png')

    # 2 行为分型
    fig, ax = plt.subplots(figsize=(8, 5))
    items = [(b['behavior'], b['sessions']) for b in stats['behaviors']]
    ax.barh([i[0] for i in items][::-1], [i[1] for i in items][::-1], color=C[:len(items)][::-1], alpha=0.85)
    for i, (k, v) in enumerate(items[::-1]):
        ax.text(v + 1, i, f'{v} ({100*v/stats["sessions_total"]:.0f}%)', va='center', fontsize=10)
    ax.set_xlabel('会话数')
    ax.set_title('会话行为分型（按工具构成）', fontsize=12)
    savefig('c2_behavior_types.png')

    # 3 月度趋势堆叠
    by_month_topic = defaultdict(Counter)
    for s in sessions:
        by_month_topic[s['date'][:7]][s['topic']] += 1
    months = sorted(by_month_topic)
    top_topics = [t['topic'] for t in stats['topics'][:4]]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bottom = np.zeros(len(months))
    for ti, t in enumerate(top_topics + ['其余']):
        vals = [by_month_topic[m].get(t, 0) if t != '其余'
                else sum(by_month_topic[m].values()) - sum(by_month_topic[m].get(x, 0) for x in top_topics)
                for m in months]
        ax.bar(months, vals, bottom=bottom, label=t, color=C[ti], alpha=0.85)
        bottom += np.array(vals)
    ax.set_ylabel('会话数')
    ax.legend(fontsize=9)
    ax.set_title('月度会话趋势', fontsize=12)
    savefig('c3_monthly_trend.png')

    # 4 工具 TOP + 转移
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(14, 5.5))
    top_t = stats['tools_top'][:10]
    axl.barh([t[0] for t in top_t][::-1], [t[1] for t in top_t][::-1], color=C[0], alpha=0.85)
    for i, (k, v) in enumerate(top_t[::-1]):
        axl.text(v + 80, i, f'{v:,}', va='center', fontsize=9)
    axl.set_title('工具调用 TOP10', fontsize=11)
    top_bi = stats['tool_bigrams_top'][:12]
    axr.barh([a for a, _ in top_bi][::-1], [c for _, c in top_bi][::-1], color=C[1], alpha=0.85)
    for i, (_, c) in enumerate(top_bi[::-1]):
        axr.text(c + 50, i, f'{c:,}', va='center', fontsize=9)
    axr.set_title('工具转移 TOP12', fontsize=11)
    savefig('c4_tool_patterns.png')

    # 5 回合与纠偏分布
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(13, 5))
    rounds_arr = [s['rounds'] for s in sessions]
    axl.hist([r for r in rounds_arr if r < 600], bins=40, color=C[0], alpha=0.8, edgecolor='white')
    axl.axvline(np.median(rounds_arr), color=C[4], ls='--',
                label=f"中位 {int(np.median(rounds_arr))}")
    axl.set_xlabel('会话回合数（截尾<600）')
    axl.set_ylabel('会话数')
    axl.legend()
    axl.set_title('会话规模分布', fontsize=11)
    iter_arr = [s['iter'] for s in sessions]
    bins = [0, 1, 2, 3, 5, 10, 10000]
    labels = ['0', '1', '2', '3-4', '5-9', '10+']
    cnts = [int(np.sum((np.array(iter_arr) >= bins[i]) & (np.array(iter_arr) < bins[i + 1])))
            for i in range(len(labels))]
    axr.bar(labels, cnts, color=[C[5], C[2], C[2], C[1], C[4], C[4]], alpha=0.85)
    for i, v in enumerate(cnts):
        axr.text(i, v + 1, str(v), ha='center', fontsize=10)
    axr.set_xlabel('用户迭代/纠偏信号次数')
    axr.set_ylabel('会话数')
    axr.set_title('用户纠偏分布', fontsize=11)
    savefig('c5_rounds_iteration.png')

    # 6 渠道对比
    chs = sorted(stats['channels'].keys())
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(chs))
    w = 0.35
    ax.bar(x - w / 2, [stats['channels'][c]['rounds_mean'] for c in chs], w, label='平均回合数', color=C[0], alpha=0.85)
    ax.bar(x + w / 2, [stats['channels'][c]['toolcalls_mean'] for c in chs], w, label='平均工具调用', color=C[1], alpha=0.85)
    for i, c in enumerate(chs):
        ax.text(i, max(stats['channels'][c]['rounds_mean'], stats['channels'][c]['toolcalls_mean']) + 15,
                f"n={stats['channels'][c]['sessions']}", ha='center', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(chs)
    ax.legend()
    ax.set_title('渠道差异', fontsize=12)
    savefig('c6_channel_compare.png')

    # 7 话题×行为热力
    topics_order = [t['topic'] for t in stats['topics'][:6]]
    behs = ['联网调研型', '文档生产型', '本地操作/排障型', '混合型']
    mat = np.zeros((len(topics_order), len(behs)))
    for s in sessions:
        if s['topic'] in topics_order and s['behavior'] in behs:
            mat[topics_order.index(s['topic']), behs.index(s['behavior'])] += 1
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(mat, cmap='Blues', aspect='auto')
    ax.set_xticks(range(len(behs)))
    ax.set_xticklabels(behs, fontsize=9)
    ax.set_yticks(range(len(topics_order)))
    ax.set_yticklabels(topics_order, fontsize=9)
    for i in range(len(topics_order)):
        for j in range(len(behs)):
            if mat[i, j] > 0:
                ax.text(j, i, int(mat[i, j]), ha='center', va='center', fontsize=10,
                        color='white' if mat[i, j] > mat.max() / 2 else 'black')
    ax.set_title('话题 × 行为分型矩阵', fontsize=11)
    savefig('c7_topic_behavior_matrix.png')

    # 8 自主放大散点
    ur = [s['user_real'] for s in sessions]
    tc = [s['toolcalls'] for s in sessions]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(ur, tc, alpha=0.4, color=C[0], s=25)
    ax.set_xlabel('真实用户输入条数')
    ax.set_ylabel('工具调用次数')
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 1200)
    mask = [(u < 120 and t < 1200) for u, t in zip(ur, tc)]
    xa = np.array([u for u, m in zip(ur, mask) if m])
    ya = np.array([t for t, m in zip(tc, mask) if m])
    if len(xa) > 2:
        z = np.polyfit(xa, ya, 1)
        ax.plot([0, 120], [z[1], 120 * z[0] + z[1]], color=C[4], ls='--', label=f'斜率≈{z[0]:.0f} 调用/输入')
        ax.legend()
    ax.set_title('自主放大系数：用户输入 vs 工具调用（截尾视图）', fontsize=11)
    savefig('c8_autonomy_amplification.png')


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='会话日志通用分析器（extract → analyze → visualize）')
    ap.add_argument('--src', default=str(CONV_LOG_DIR / 'db-sessions'), help='会话 md 目录')
    ap.add_argument('--db', default=str(TMP_DIR / 'convlog.db'), help='SQLite 输出路径')
    ap.add_argument('--out', default=str(TMP_DIR / 'conv-charts'), help='图表输出目录')
    ap.add_argument('--no-charts', action='store_true', help='跳过图表生成')
    ap.add_argument('--stats-only', action='store_true', help='跳过解析，复用已有 DB')
    ap.add_argument('--json', action='store_true', help='统计结果另存 JSON 到 tmp/')
    args = ap.parse_args()

    if not args.stats_only:
        extract(args.src, args.db)

    stats, sessions = analyze(args.db)
    print_summary(stats)

    if args.json:
        out = TMP_DIR / f'convlog-stats-{date.today().isoformat()}.json'
        out.write_text(json.dumps(stats, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
        print(f"\n[json] {out}")

    if not args.no_charts:
        visualize(stats, sessions, args.out)
        print(f"\n[charts] {args.out}")


if __name__ == '__main__':
    main()
