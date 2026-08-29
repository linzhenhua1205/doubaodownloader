#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web-access-log.py — Web 访问台账记录工具（知识库来源可追溯的全局访问日志）

用途：
  记录每次联网访问（web_fetch / search-router / curl / CDP / zhihu-cli /
  fetch-skill / wechat-claw / markdown-proxy / browser / web_search）的
  时间、URL、标题、渠道、用途、状态，追加到 CSV 台账。

位置：
  knowledge/weekly-reports/07_kb_stat/99_data/web-access-log.csv
  （2026-08-19 起 07_kb_stat 无独立 index/log，统一全局 knowledge/log.md）

设计原则：
  - 低摩擦：任务收尾时批量追加（--file 草稿），不打断单次访问
  - 去重：同 URL 在 RETENTION_DAYS（默认 30 天）内不重复记录
  - 机器可读：标准 CSV（csv 模块转义），周报/数据源质量评估直接消费
  - 同构 kb-log-append.py 模式：--file 草稿批量 / 单条参数追加

用法示例：
  # 单条追加
  python3 scripts/tools/web-access-log.py \
      --url "https://www.tomshardware.com/tech-industry/coreweave-a100..." \
      --title "CoreWeave A100 九年经济寿命" \
      --channel web_fetch --purpose 调研 --status success

  # 批量追加（草稿文件，每行一条，字段用 tab 分隔）
  python3 scripts/tools/web-access-log.py --file /tmp/web_draft.tsv

  # 汇总统计（按渠道/状态/域名）
  python3 scripts/tools/web-access-log.py --stats
  python3 scripts/tools/web-access-log.py --stats --by channel
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime, timedelta, timezone

DEFAULT_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..",
    "knowledge", "weekly-reports", "07_kb_stat", "99_data", "web-access-log.csv")
DEFAULT_CSV = os.path.normpath(DEFAULT_CSV)

HEADER = ["timestamp", "url", "title", "channel", "purpose", "status", "note"]

CHANNELS = {
    "web_fetch", "web_search", "search-router", "curl", "browser", "cdp",
    "zhihu-cli", "fetch-skill", "wechat-claw", "wechat-extractor",
    "markdown-proxy", "jina", "requests", "other",
}
PURPOSES = {"调研", "归档", "核验", "日报", "周报", "深度分析", "其他"}
STATUSES = {"success", "fail", "partial"}

TZ = timezone(timedelta(hours=8))  # Asia/Shanghai
RETENTION_DAYS = 30


def now_str():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")


def ensure_csv(path):
    """不存在则创建带表头的 CSV。"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
        return 0
    # 校验表头
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            first = next(reader)
        except StopIteration:
            first = []
    if first != HEADER:
        print(f"[WARN] CSV 表头不匹配: {path}", file=sys.stderr)
        print(f"       期望 {HEADER}", file=sys.stderr)
        print(f"       实际 {first}", file=sys.stderr)
    return count_rows(path)


def count_rows(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def load_urls(path, days=RETENTION_DAYS):
    """返回 {url: timestamp}，用于去重。"""
    if not os.path.exists(path):
        return {}
    cutoff = datetime.now(TZ) - timedelta(days=days)
    urls = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 2 or row[0] == "timestamp":
                continue
            try:
                ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
            except ValueError:
                continue
            if ts >= cutoff and row[1]:
                urls[row[1]] = row[0]
    return urls


def validate(record, idx):
    """字段校验，返回 (ok, err_msg)。"""
    url = record.get("url", "").strip()
    if not url:
        return False, f"第{idx}条缺 url"
    if not url.startswith(("http://", "https://")):
        return False, f"第{idx}条 url 非 http(s): {url[:60]}"
    ch = record.get("channel", "").strip() or "other"
    if ch not in CHANNELS:
        return False, f"第{idx}条 channel 未知: {ch}（可选: {sorted(CHANNELS)}）"
    st = record.get("status", "").strip() or "success"
    if st not in STATUSES:
        return False, f"第{idx}条 status 未知: {st}"
    return True, ""


def append_records(path, records, dedup=True):
    """追加记录。返回 (added, skipped_dup)。"""
    ensure_csv(path)
    seen = load_urls(path) if dedup else {}
    added, skipped = 0, 0
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for rec in records:
            url = rec.get("url", "").strip()
            if dedup and url in seen:
                skipped += 1
                continue
            seen[url] = now_str()
            writer.writerow([
                now_str(),
                url,
                rec.get("title", "").strip(),
                rec.get("channel", "other").strip(),
                rec.get("purpose", "其他").strip(),
                rec.get("status", "success").strip(),
                rec.get("note", "").strip(),
            ])
            added += 1
    return added, skipped


def parse_draft(path):
    """解析批量草稿：每行一条，字段 tab 分隔，顺序同 HEADER 后 6 列（url 必填）。"""
    records = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            url = parts[0].strip()
            rec = {
                "url": url,
                "title": parts[1].strip() if len(parts) > 1 else "",
                "channel": parts[2].strip() if len(parts) > 2 else "other",
                "purpose": parts[3].strip() if len(parts) > 3 else "其他",
                "status": parts[4].strip() if len(parts) > 4 else "success",
                "note": parts[5].strip() if len(parts) > 5 else "",
            }
            records.append((i, rec))
    return records


def stats(path, by="channel"):
    """汇总统计。by: channel / status / domain。"""
    if not os.path.exists(path):
        print("台账不存在，尚无记录")
        return
    counter = {}
    total = 0
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 6 or row[0] == "timestamp":
                continue
            total += 1
            if by == "channel":
                key = row[3] or "other"
            elif by == "status":
                key = row[5] or "success"
            elif by == "domain":
                m = re.match(r"https?://([^/]+)", row[1])
                key = m.group(1) if m else row[1]
            else:
                key = row[0][:10]  # 按日期
            counter[key] = counter.get(key, 0) + 1
    print(f"总记录数: {total}")
    for k, v in sorted(counter.items(), key=lambda x: -x[1]):
        print(f"  {k:40s} {v:5d}  ({v/total*100:.1f}%)")


def main():
    ap = argparse.ArgumentParser(description="Web 访问台账记录工具")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="CSV 路径（默认 07_kb_stat/99_data/web-access-log.csv）")
    ap.add_argument("--url", help="单条 URL")
    ap.add_argument("--title", default="", help="标题（可选）")
    ap.add_argument("--channel", default="other", help=f"渠道（可选: {sorted(CHANNELS)}）")
    ap.add_argument("--purpose", default="其他", help=f"用途（可选: {sorted(PURPOSES)}）")
    ap.add_argument("--status", default="success", help=f"状态（可选: {sorted(STATUSES)}）")
    ap.add_argument("--note", default="", help="备注（可选）")
    ap.add_argument("--file", help="批量草稿文件（每行 tab 分隔: url\\ttitle\\tchannel\\tpurpose\\tstatus\\tnote）")
    ap.add_argument("--no-dedup", action="store_true", help="关闭去重")
    ap.add_argument("--stats", action="store_true", help="汇总统计")
    ap.add_argument("--by", default="channel", choices=["channel", "status", "domain", "date"],
                    help="统计维度（默认 channel）")
    args = ap.parse_args()

    if args.stats:
        stats(args.csv, by=args.by)
        return

    if args.file:
        raw = parse_draft(args.file)
        records = []
        for idx, rec in raw:
            ok, err = validate(rec, idx)
            if not ok:
                print(f"[ERR] {err}", file=sys.stderr)
                sys.exit(1)
            records.append(rec)
    elif args.url:
        rec = {
            "url": args.url, "title": args.title, "channel": args.channel,
            "purpose": args.purpose, "status": args.status, "note": args.note,
        }
        ok, err = validate(rec, 1)
        if not ok:
            print(f"[ERR] {err}", file=sys.stderr)
            sys.exit(1)
        records = [rec]
    else:
        ap.print_help()
        sys.exit(1)

    added, skipped = append_records(args.csv, records, dedup=not args.no_dedup)
    total = count_rows(args.csv)
    print(f"✅ 已追加 {added} 条（去重跳过 {skipped} 条），台账当前共 {total} 条")
    print(f"📄 {args.csv}")


if __name__ == "__main__":
    main()
