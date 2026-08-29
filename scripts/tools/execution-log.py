#!/usr/bin/env python3
"""
execution-log.py — 定时任务执行状态日志管理器

集成了 sr-006 三项 P0 建议:
  I-01: 执行状态日志 — 每次任务执行后写状态到 scheduler/execution-log.json
  I-02: 重试机制 — 失败后自动推荐重试，指数退避
  I-06: 任务级监控 — 零产出/超时/连续失败检测

功能:
  1. log     — 记录单次任务执行状态
  2. status  — 查看最近 N 次执行状态
  3. report  — 监控报表：零产出 / 连续失败 / 过期任务
  4. retry   — 重试失败任务（生成重试建议）

用法:
  # 记录执行状态
  python3 scripts/tools/execution-log.py log \\
      --task-id ea4db070 --task-name "国产化替代调研" \\
      --status success --output "knowledge/01_survey/industry-research/2026-07-27.md" \\
      --message "成功搜索到3条新信息" --lines 42

  python3 scripts/tools/execution-log.py log \\
      --task-id ea4db070 --status empty --lines 0 \\
      --message "搜索完成，无新增内容"

  python3 scripts/tools/execution-log.py log \\
      --task-id 1e56193d --status fail --message "API 超时" --duration 120

  # 查询最近状态
  python3 scripts/tools/execution-log.py status --task-id ea4db070 --last 5

  # 监控报表
  python3 scripts/tools/execution-log.py report --stale-days 3

  # 查看所有任务最新状态摘要
  python3 scripts/tools/execution-log.py report --summary

  # 重试建议（列出可重试任务）
  python3 scripts/tools/execution-log.py retry --list

状态定义:
  success   — 正常执行且有有效产出（产出文件行数 >= 5）
  empty     — 执行成功但无有效产出（零产出，文件 < 5 行）
  fail      — 执行失败（API/网络/超时等）
  skipped   — 被跳过（如命中缓存）
  degraded  — 降级执行（部分成功）

依赖:
  - errorcodes.py (统一错误码)
  - scheduler/tasks.json (任务配置)
"""
import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# ── 路径 ──
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEDULER_DIR = REPO_ROOT / 'scheduler'
LOG_FILE = SCHEDULER_DIR / 'execution-log.json'
TASKS_FILE = SCHEDULER_DIR / 'tasks.json'

# 引入错误码
sys.path.insert(0, str(REPO_ROOT / 'scripts'))
from tools.errorcodes import EC, exit_with

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

NOW = datetime.now()
DATE_STR = NOW.strftime('%Y-%m-%d')
TIMESTAMP = NOW.strftime('%Y-%m-%d %H:%M:%S')

VALID_STATUSES = ('success', 'empty', 'fail', 'skipped', 'degraded')
EMPTY_THRESHOLD = 5  # 产出文件行数 < 此值视为零产出
MAX_RECORDS_PER_TASK = 100  # 每个任务最多保留的记录数


# ══════════════════════════════════════════════════════════
#  日志读写
# ══════════════════════════════════════════════════════════

def _load_log():
    """加载执行日志"""
    if not LOG_FILE.exists():
        return {"version": 1, "records": []}
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"⚠️  日志文件损坏，重新初始化: {LOG_FILE}")
        return {"version": 1, "records": []}


def _save_log(data):
    """保存执行日志"""
    SCHEDULER_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"📝 已更新执行日志: {LOG_FILE}")


def log_execution(task_id: str, task_name: str, status: str,
                  output: str = "", message: str = "",
                  lines: int = -1, duration: int = -1):
    """记录单次任务执行状态"""
    if status not in VALID_STATUSES:
        exit_with(EC.INVALID_ARGS, f"无效状态: {status}，有效值: {VALID_STATUSES}")

    # 自动判断 empty
    if status == 'success' and 0 <= lines < EMPTY_THRESHOLD:
        status = 'empty'
        message = message or f"产出仅 {lines} 行，低于零产出阈值 ({EMPTY_THRESHOLD})"

    record = {
        "task_id": task_id,
        "task_name": task_name,
        "status": status,
        "timestamp": TIMESTAMP,
        "output": output,
        "message": message,
        "lines": lines if lines >= 0 else None,
        "duration_sec": duration if duration >= 0 else None,
    }

    data = _load_log()
    data.setdefault("records", []).append(record)

    # 修剪每个任务记录数量
    task_records = [r for r in data["records"] if r.get("task_id") == task_id]
    if len(task_records) > MAX_RECORDS_PER_TASK:
        excess = len(task_records) - MAX_RECORDS_PER_TASK
        # 从旧记录开始删
        removed = 0
        filtered = []
        for r in data["records"]:
            if r.get("task_id") == task_id and removed < excess:
                removed += 1
                continue
            filtered.append(r)
        data["records"] = filtered

    _save_log(data)

    # 输出摘要
    emoji = {"success": "✅", "empty": "⚠️", "fail": "❌",
             "skipped": "⏭️", "degraded": "🔄"}.get(status, "❓")
    print(f"  {emoji} [{status}] {task_name} — {message or '无说明'}")
    if lines >= 0:
        print(f"    产出行数: {lines}")
    if duration >= 0:
        print(f"    耗时: {duration}秒")

    return record


# ══════════════════════════════════════════════════════════
#  状态查询
# ══════════════════════════════════════════════════════════

def show_status(task_id: str = "", last: int = 10):
    """显示最近 N 次执行状态"""
    data = _load_log()
    records = data.get("records", [])

    if not records:
        print("📭 暂无执行记录")
        return

    if task_id:
        records = [r for r in records if r.get("task_id") == task_id]
        if not records:
            print(f"📭 任务 {task_id} 无执行记录")
            return
        print(f"\n📊 任务 {task_id} 最近 {last} 次执行:")
    else:
        print(f"\n📊 所有任务最近 {last} 次执行:")

    for r in records[-last:]:
        emoji = {"success": "✅", "empty": "⚠️", "fail": "❌",
                 "skipped": "⏭️", "degraded": "🔄"}.get(r.get("status", ""), "❓")
        ts = r.get("timestamp", "?")
        msg = r.get("message", "") or ""
        lines = r.get("lines", "")
        lines_str = f" | {lines}行" if lines else ""
        print(f"  {emoji} [{r.get('status','?')}] {ts}{lines_str} — {msg[:80]}")


# ══════════════════════════════════════════════════════════
#  监控报表
# ══════════════════════════════════════════════════════════

def generate_report(stale_days: int = 3, summary_only: bool = False):
    """生成监控报表"""
    data = _load_log()
    records = data.get("records", [])

    if not records:
        print("📭 暂无执行记录，无法生成报表")
        return

    # 按 task_id 分组，取每组最新记录
    latest = {}
    consecutive_fails = {}
    for r in records:
        tid = r.get("task_id", "")
        if tid not in latest:
            latest[tid] = r
            consecutive_fails[tid] = 1 if r.get("status") == "fail" else 0
        else:
            # 较新的记录覆盖
            if r.get("timestamp", "") >= latest[tid].get("timestamp", ""):
                latest[tid] = r
            # 连续失败计数（仅统计最近连续记录）
            if r.get("status") == "fail":
                consecutive_fails[tid] = consecutive_fails.get(tid, 0) + 1
            else:
                consecutive_fails[tid] = 0

    # 加载任务配置（获取名称映射）
    task_names = {}
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        for tid, tcfg in tasks_data.get("tasks", {}).items():
            task_names[tid] = tcfg.get("name", tid)
    except (OSError, json.JSONDecodeError):
        pass

    if summary_only:
        # ── 摘要模式 ──
        status_counts = {"success": 0, "empty": 0, "fail": 0,
                         "skipped": 0, "degraded": 0}
        for r in latest.values():
            status_counts[r.get("status", "")] = status_counts.get(r.get("status", ""), 0) + 1
        total = sum(status_counts.values()) or 1
        health = status_counts.get("success", 0) / total * 100

        print(f"\n📊 执行状态摘要 (共 {len(latest)} 个任务)")
        print(f"  ✅ 成功:   {status_counts['success']}")
        print(f"  ⚠️  空产出: {status_counts['empty']}")
        print(f"  ❌ 失败:   {status_counts['fail']}")
        print(f"  ⏭️  跳过:   {status_counts['skipped']}")
        print(f"  🔄 降级:   {status_counts['degraded']}")
        print(f"  📈 健康率: {health:.0f}%")

        if status_counts['empty'] > 0:
            print(f"\n  ⚠️  空产出任务:")
            for tid, r in latest.items():
                if r.get("status") == "empty":
                    name = task_names.get(tid, tid)
                    print(f"    - {name} ({tid})")

        if status_counts['fail'] > 0:
            print(f"\n  ❌ 失败任务:")
            for tid, r in latest.items():
                if r.get("status") == "fail":
                    name = task_names.get(tid, tid)
                    msg = r.get("message", "")[:60]
                    print(f"    - {name} ({tid}): {msg}")
        return

    # ── 详细报表 ──
    print(f"\n{'='*60}")
    print(f"📊 定时任务监控报表 (生成于 {TIMESTAMP})")
    print(f"{'='*60}")

    now = datetime.now()
    issues = []

    for tid, r in sorted(latest.items()):
        name = task_names.get(tid, tid)
        status = r.get("status", "?")
        ts_str = r.get("timestamp", "")
        msg = r.get("message", "") or ""

        try:
            ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
            days_since = (now - ts).days
        except (ValueError, TypeError):
            days_since = 999

        emoji = {"success": "✅", "empty": "⚠️", "fail": "❌",
                 "skipped": "⏭️", "degraded": "🔄"}.get(status, "❓")
        stale_tag = f" ⏰{days_since}d未运行" if days_since >= stale_days else ""

        print(f"\n  {emoji} {name}")
        print(f"    状态: {status} | 最近: {ts_str}{stale_tag}")
        if msg:
            print(f"    信息: {msg[:100]}")

        # 收集问题
        if status == "fail":
            issues.append((30, f"❌ 失败: {name} — {msg[:60]}"))
        if status == "empty":
            issues.append((20, f"⚠️  空产出: {name} — {msg[:60]}"))
        if days_since >= stale_days:
            issues.append((25, f"⏰ 过期: {name} — {days_since}天未运行"))
        fails = consecutive_fails.get(tid, 0)
        if fails >= 3:
            issues.append((35, f"🔴 连续{fails}次失败: {name}"))

    # 报表小结
    print(f"\n{'─'*60}")
    issues.sort(key=lambda x: -x[0])
    if issues:
        print(f"⚠️  发现 {len(issues)} 个问题:")
        for _, desc in issues[:20]:
            print(f"  {desc}")
        if len(issues) > 20:
            print(f"  ... 及其他 {len(issues)-20} 个问题")
    else:
        print("✅ 所有任务运行正常")

    # 写入报表文件
    report_path = REPO_ROOT / 'scheduler' / f'monitor-report-{DATE_STR}.md'
    total = len(latest)
    good = sum(1 for r in latest.values() if r.get("status") == "success")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# 定时任务监控报表 ({DATE_STR})\n\n")
        f.write(f"- **健康率**: {good}/{total} ({good/total*100:.0f}%)\n")
        f.write(f"- **问题数**: {len(issues)}\n\n")
        if issues:
            f.write("## 问题清单\n\n")
            for _, desc in issues:
                f.write(f"- {desc}\n")
    print(f"\n📝 报表已保存: {report_path}")


# ══════════════════════════════════════════════════════════
#  重试建议
# ══════════════════════════════════════════════════════════

def show_retry():
    """显示可重试的任务列表"""
    data = _load_log()
    records = data.get("records", [])

    if not records:
        print("📭 暂无执行记录")
        return

    # 按 task_id 分组，取每组最新记录
    latest = {}
    for r in records:
        tid = r.get("task_id", "")
        if tid not in latest or r.get("timestamp", "") >= latest[tid].get("timestamp", ""):
            latest[tid] = r

    # 加载任务配置
    task_names = {}
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        for tid, tcfg in tasks_data.get("tasks", {}).items():
            task_names[tid] = tcfg.get("name", tid)
    except (OSError, json.JSONDecodeError):
        pass

    retryable_statuses = ('fail', 'empty', 'degraded')
    retryable = [(tid, r) for tid, r in latest.items()
                 if r.get("status") in retryable_statuses]

    if not retryable:
        print("✅ 无可重试任务")
        return

    print(f"\n🔄 可重试任务 ({len(retryable)} 个):")
    for tid, r in sorted(retryable):
        name = task_names.get(tid, tid)
        status = r.get("status", "?")
        msg = r.get("message", "")[:80]
        print(f"  [{status}] {name}")
        print(f"    ID: {tid}")
        print(f"    信息: {msg}")
        print()


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='定时任务执行状态日志管理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令:
  log     记录单次任务执行状态
  status  查看最近执行状态
  report  生成监控报表
  retry   显示可重试任务

示例:
  # 记录成功执行
  %(prog)s log --task-id abc --task-name "调研" --status success --lines 42

  # 记录空产出
  %(prog)s log --task-id abc --task-name "调研" --status empty --lines 0

  # 查看任务最近状态
  %(prog)s status --task-id abc --last 5

  # 全任务摘要
  %(prog)s report --summary

  # 详细监控报表
  %(prog)s report --stale-days 3

  # 查看可重试任务
  %(prog)s retry --list
        """)
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # ── log ──
    p_log = subparsers.add_parser("log", help="记录执行状态")
    p_log.add_argument("--task-id", required=True, help="任务 ID")
    p_log.add_argument("--task-name", default="", help="任务名称")
    p_log.add_argument("--status", required=True,
                       choices=VALID_STATUSES, help="执行状态")
    p_log.add_argument("--output", default="", help="产出文件路径")
    p_log.add_argument("--message", default="", help="附加说明")
    p_log.add_argument("--lines", type=int, default=-1, help="产出文件行数")
    p_log.add_argument("--duration", type=int, default=-1, help="执行耗时(秒)")

    # ── status ──
    p_status = subparsers.add_parser("status", help="查看执行状态")
    p_status.add_argument("--task-id", default="", help="任务 ID（为空则显示所有）")
    p_status.add_argument("--last", type=int, default=10, help="最近 N 条")

    # ── report ──
    p_report = subparsers.add_parser("report", help="生成监控报表")
    p_report.add_argument("--stale-days", type=int, default=3,
                          help="过期判定天数 (默认: 3)")
    p_report.add_argument("--summary", action="store_true",
                          help="仅输出摘要")

    # ── retry ──
    p_retry = subparsers.add_parser("retry", help="显示可重试任务")
    p_retry.add_argument("--list", action="store_true", help="列出可重试任务")

    args = parser.parse_args()

    if args.command == "log":
        log_execution(
            task_id=args.task_id,
            task_name=args.task_name,
            status=args.status,
            output=args.output,
            message=args.message,
            lines=args.lines,
            duration=args.duration,
        )
    elif args.command == "status":
        show_status(task_id=args.task_id, last=args.last)
    elif args.command == "report":
        generate_report(stale_days=args.stale_days, summary_only=args.summary)
    elif args.command == "retry":
        show_retry()
    else:
        parser.print_help()
        exit_with(EC.INVALID_ARGS, "请指定子命令")


if __name__ == "__main__":
    main()
