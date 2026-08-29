#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户问题提炼脚本 v2 — 全量导出为 CSV

从 CowAgent 会话数据库 (memory/long-term/index.db) 提炼用户真实提问，
输出 CSV 到 knowledge/weekly-reports/07_kb_stat/06_conversation/ 目录。

【v2 改进】
  1. 全量导出：覆盖全部 42 个真实用户会话（2026-05-09 起），不再默认仅近期
  2. 完整字段：时间/问题/通道/会话ID/会话标题/会话创建时间/消息seq/消息ID/角色
  3. 不截断问题文本（移除 500 字符限制，保留全文，便于分析）
  4. 移除"开始/执行/追踪/搜索"短句粗过滤（曾误删真实提问）
  5. 通道判定统一走 session_id 前缀映射（scheduler_oc_=feishu定时,
     scheduler_session_=web定时, session_=web, ou_/oc_=feishu）
  6. 明确区分用户会话 / 定时任务会话（is_scheduler 列）

CSV 列:
  用户输入时间 | 问题描述 | 输入通道 | 会话ID | 会话标题 | 会话创建时间 | 消息seq | 消息ID | 是否定时任务

过滤规则（仅保留真正的用户提问）:
  - 仅 role='user' 的消息
  - 剔除 session_id 以 scheduler_ 开头的定时任务会话（可 --include-scheduler 保留）
  - 剔除 content JSON 中 type=tool_result / tool_use / thinking 的消息
  - 剔除空内容消息
  - 保留 content 首元素 type='text' 或纯文本（真实用户输入）

用法:
  python3 scripts/intent_analysis/export_user_questions_csv.py                     # 全量用户会话
  python3 scripts/intent_analysis/export_user_questions_csv.py --since 2026-08-07  # 指定起始日
  python3 scripts/intent_analysis/export_user_questions_csv.py --out /path/x.csv   # 指定输出
  python3 scripts/intent_analysis/export_user_questions_csv.py --include-scheduler # 含定时任务会话
"""
import sqlite3
import json
import os
import csv
import argparse
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
DB_PATH = os.path.expanduser("~/cow/memory/long-term/index.db")
DEFAULT_OUT_DIR = os.path.expanduser("~/cow/knowledge/weekly-reports/07_kb_stat/06_conversation")


def infer_channel(session_id: str):
    """按 session_id 前缀推断通道，权威口径（见 index-db-schema-analysis 报告 §4.1）"""
    if session_id.startswith("scheduler_oc_"):
        return "feishu(定时)"
    if session_id.startswith("scheduler_session_"):
        return "web(定时)"
    if session_id.startswith("ou_") or session_id.startswith("oc_"):
        return "feishu"
    if session_id.startswith("session_"):
        return "web"
    return "unknown"


def extract_user_text(content: str):
    """从 messages.content 提取用户文本; 非用户提问返回 None"""
    if not content:
        return None
    content = content.strip()
    if not content:
        return None
    # 纯文本（非 JSON）
    if not content.startswith("["):
        if content.startswith("tool_") or content.startswith("{"):
            return None
        return content
    try:
        items = json.loads(content)
    except Exception:
        return content
    if not isinstance(items, list):
        return None
    texts = []
    has_text = False
    for it in items:
        if not isinstance(it, dict):
            continue
        t = it.get("type", "")
        if t in ("tool_result", "tool_use", "thinking"):
            # 只要消息里包含工具结果, 视为系统消息而非用户提问
            if not has_text:
                return None
            continue
        if t == "text":
            has_text = True
            txt = it.get("text", "")
            if txt and txt.strip():
                texts.append(txt.strip())
    if not has_text:
        return None
    return " ".join(texts) if texts else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="起始时间 YYYY-MM-DD")
    ap.add_argument("--out", default="", help="CSV 输出路径")
    ap.add_argument("--include-scheduler", action="store_true",
                    help="包含 scheduler 定时任务会话（默认排除）")
    args = ap.parse_args()

    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    # 会话元信息
    sess_meta = {}
    for sid, title, created_at in cur.execute(
            "SELECT session_id, title, created_at FROM sessions").fetchall():
        sess_meta[sid] = {"title": title, "created_at": created_at}

    # 消息查询（仅 user 角色，减少扫描量）
    sql = """SELECT m.session_id, m.role, m.content, m.created_at, m.seq, m.id
             FROM messages m WHERE m.role = 'user' ORDER BY m.created_at ASC, m.seq ASC"""
    params = ()
    if args.since:
        ts0 = int(datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=TZ).timestamp())
        sql = """SELECT m.session_id, m.role, m.content, m.created_at, m.seq, m.id
                 FROM messages m WHERE m.role = 'user' AND m.created_at >= ?
                 ORDER BY m.created_at ASC, m.seq ASC"""
        params = (ts0,)

    rows = []
    for sid, role, content, ts, seq, mid in cur.execute(sql, params).fetchall():
        if role != "user":
            continue
        is_scheduler = sid.startswith("scheduler_")
        if is_scheduler and not args.include_scheduler:
            continue
        q = extract_user_text(content)
        if not q:
            continue
        dt = datetime.fromtimestamp(ts, tz=TZ)
        meta = sess_meta.get(sid, {})
        created = datetime.fromtimestamp(meta.get("created_at", 0), tz=TZ) if meta.get("created_at") else None
        rows.append({
            "time": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "question": q,
            "channel": infer_channel(sid),
            "session": sid,
            "title": meta.get("title", ""),
            "sess_created": created.strftime("%Y-%m-%d %H:%M:%S") if created else "",
            "seq": seq,
            "mid": mid,
            "is_scheduler": "是" if is_scheduler else "否",
        })

    out_dir = os.path.dirname(args.out) if args.out else DEFAULT_OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    out_file = args.out or os.path.join(out_dir, f"user-questions-{datetime.now(TZ).strftime('%Y-%m-%d')}.csv")
    with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["用户输入时间", "问题描述", "输入通道", "会话ID",
                    "会话标题", "会话创建时间", "消息seq", "消息ID", "是否定时任务"])
        for r in rows:
            w.writerow([r["time"], r["question"], r["channel"], r["session"],
                        r["title"], r["sess_created"], r["seq"], r["mid"], r["is_scheduler"]])
    # 统计
    user_rows = [r for r in rows if r["is_scheduler"] == "否"]
    sched_rows = [r for r in rows if r["is_scheduler"] == "是"]
    print(f"✅ 导出 {len(rows)} 条用户提问 → {out_file}")
    print(f"   其中: 用户会话 {len(user_rows)} 条 / 定时任务会话 {len(sched_rows)} 条"
          f"{'（已过滤）' if not args.include_scheduler else ''}")


if __name__ == "__main__":
    main()
