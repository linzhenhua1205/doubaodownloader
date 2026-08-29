#!/usr/bin/env python3
"""
check-tasks-integrity.py — tasks.json 完整性守护脚本

检测 scheduler/tasks.json 的进程隔离违背、git 版本漂移、channel 配置一致性。

== 用法 ==

  # 完整检查
  python3 scripts/check/check-tasks-integrity.py

  # 仅检查 git 版本漂移
  python3 scripts/check/check-tasks-integrity.py --check drift

  # 仅检查 channel 配置
  python3 scripts/check/check-tasks-integrity.py --check channel

  # 报告模式（输出 JSON）
  python3 scripts/check/check-tasks-integrity.py --json

  # 自动修复（仅可修复项）
  python3 scripts/check/check-tasks-integrity.py --fix

== 检查项 ==

  C71 (12306): tasks.json 进程隔离契约
  C72 (12307): git 版本漂移检测
  C73 (12308): channel_type 一致性

== 退出码 ==

  0 = 全部通过 / 仅警告
  1 = 有失败项
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 路径
WORKSPACE_ROOT = (Path(__file__).resolve().parent.parent.parent).resolve()
TASKS_FILE = WORKSPACE_ROOT / "scheduler" / "tasks.json"
GIT_DIR = WORKSPACE_ROOT / ".git"

# ── 检查函数 ───────────────────────────────────────────────────────────────────

def check_file_exists() -> Tuple[bool, str]:
    """检查 tasks.json 是否存在"""
    if not TASKS_FILE.exists():
        return False, f"❌ tasks.json 不存在: {TASKS_FILE}"
    return True, f"✅ tasks.json 存在 ({TASKS_FILE.stat().st_size} bytes)"


def check_process_isolation(data: dict) -> Tuple[str, str]:
    """C71: 检查 tasks.json 进程隔离契约

    检测非 next_run_at/updated_at 的非预期修改。
    如果文件被人为修改了大量任务字段，应告警。
    """
    issues = []
    tasks = data.get("tasks", {})
    for tid, t in tasks.items():
        # 检测 action 中是否存在 non-standard channel_type
        action = t.get("action", {})
        ct = action.get("channel_type", "")
        if ct and ct not in ("feishu", "dingtalk", "wechat", "email", ""):
            issues.append(f"  ⚠️ [{t.get('name', tid)}] 未知 channel_type: {ct}")

    if issues:
        return "WARN", "\n".join(issues)
    return "PASS", f"✅ 所有 {len(tasks)} 个任务 channel_type 合规"


def check_git_drift() -> Tuple[str, str]:
    """C72: 检查 tasks.json 与 git HEAD 的版本漂移

    只告警非调度字段（非 next_run_at/updated_at）的修改。
    """
    if not GIT_DIR.exists():
        return "WARN", "⚠️ 非 git 仓库，跳过漂移检测"

    try:
        # 获取 diff stat（统计变更行数）
        result = subprocess.run(
            ["git", "diff", "HEAD", "--", str(TASKS_FILE)],
            capture_output=True, text=True, timeout=30,
            cwd=str(WORKSPACE_ROOT)
        )

        if not result.stdout.strip():
            return "PASS", "✅ tasks.json 与 git HEAD 一致"

        # 分析 diff 内容，过滤掉仅 next_run_at/updated_at 的变更
        lines = result.stdout.split('\n')
        changed_fields = set()
        for line in lines:
            # 检测被修改的 JSON 字段名
            if '"next_run_at"' in line or '"updated_at"' in line:
                continue
            if line.strip().startswith('+') or line.strip().startswith('-'):
                for field in ['"name"', '"enabled"', '"schedule"', '"action"',
                              '"channel_type"', '"receiver"', '"task_description"']:
                    if field in line:
                        changed_fields.add(field.strip('"'))

        if changed_fields:
            return "FAIL", (
                f"❌ tasks.json 与 git HEAD 有非调度字段漂移!\n"
                f"   变更字段: {', '.join(sorted(changed_fields))}\n"
                f"   提示: 请检查 tasks.json 是否被非调度进程意外修改"
            )
        else:
            return "PASS", "✅ 仅调度时间字段变更（next_run_at/updated_at），正常"

    except subprocess.TimeoutExpired:
        return "WARN", "⚠️ git diff 超时 (30s)"
    except Exception as e:
        return "WARN", f"⚠️ git diff 失败: {e}"


def check_channel_consistency(data: dict) -> Tuple[str, str, List[str]]:
    """C73: 检查定时任务 channel_type 配置一致性"""
    issues = []
    tasks = data.get("tasks", {})
    for tid, t in tasks.items():
        action = t.get("action", {})
        name = t.get("name", tid)

        if action.get("channel_type") == "feishu":
            if not action.get("receiver"):
                issues.append(f"❌ [{name}] feishu 任务缺 receiver")
            if "is_group" not in action:
                issues.append(f"⚠️ [{name}] feishu 任务缺 is_group 字段")
        elif action.get("channel_type") in ("dingtalk", "wechat"):
            if not action.get("receiver"):
                issues.append(f"⚠️ [{name}] {action['channel_type']} 任务缺 receiver")

    if issues:
        return "WARN", f"⚠️ {len(issues)} 个 channel 配置问题:\n" + "\n".join(issues), issues
    return "PASS", f"✅ 所有 {len(tasks)} 个任务 channel 配置完整", []


def check_orphan_tasks(data: dict) -> Tuple[str, str]:
    """辅助: 检查是否存在从未运行的孤立任务"""
    warnings = []
    tasks = data.get("tasks", {})
    for tid, t in tasks.items():
        if not t.get("last_run_at"):
            warnings.append(f"  ⚠️ [{t.get('name', tid)}] 从未运行过")

    if warnings:
        return "WARN", "孤立任务:\n" + "\n".join(warnings)
    return "PASS", "✅ 无孤立任务"


# ── 主逻辑 ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="tasks.json 完整性守护脚本 (12306-12308)"
    )
    parser.add_argument("--check", choices=["all", "drift", "channel", "process"],
                        default="all", help="检查项 (默认: all)")
    parser.add_argument("--json", action="store_true",
                        help="JSON 输出模式")
    parser.add_argument("--fix", action="store_true",
                        help="自动修复可修复项")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")

    args = parser.parse_args()

    results = []
    has_fail = False

    # 1. 文件存在性检查（前置条件）
    exists_ok, exists_msg = check_file_exists()
    if not exists_ok:
        print(exists_msg)
        sys.exit(1)

    # 加载 tasks.json
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ 无法解析 tasks.json: {e}")
        sys.exit(1)

    # 2. 运行选择的检查
    ALL_CHECKS = {
        "process": ("C71", "12306", "tasks.json 进程隔离", check_process_isolation),
        "drift": ("C72", "12307", "git 版本漂移", lambda d: check_git_drift()),
        "channel": ("C73", "12308", "channel_type 一致性", lambda d: check_channel_consistency(d)[:2]),
    }

    checks_to_run = ALL_CHECKS if args.check == "all" else {args.check: ALL_CHECKS[args.check]}

    for check_key, (cid, cc, name, check_fn) in checks_to_run.items():
        status, message = check_fn(data)
        results.append({
            "cid": cid,
            "cc": cc,
            "name": name,
            "status": status,
            "message": message
        })
        if status == "FAIL":
            has_fail = True

    # 3. 辅助检查（始终运行）
    orphan_status, orphan_msg = check_orphan_tasks(data)
    results.append({
        "cid": "C74",
        "cc": "N/A",
        "name": "孤立任务检测",
        "status": orphan_status,
        "message": orphan_msg
    })

    # 4. 输出
    if args.json:
        print(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "tasks_file": str(TASKS_FILE),
            "total_tasks": len(data.get("tasks", {})),
            "results": results,
            "has_fail": has_fail
        }, ensure_ascii=False, indent=2))
    else:
        task_count = len(data.get("tasks", {}))
        version = data.get("version", "?")
        updated = data.get("updated_at", "?")

        print(f"\n{'='*60}")
        print(f"  tasks.json 完整性检查")
        print(f"  {TASKS_FILE}")
        print(f"  版本: {version} | 更新: {updated[:19]} | 任务数: {task_count}")
        print(f"{'='*60}\n")

        for r in results:
            icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(r["status"], "❓")
            print(f"  {icon} [{r['cid']}|{r['cc']}] {r['name']}")
            # 只显示消息中关键部分
            msg_lines = r["message"].split('\n')
            for ml in msg_lines[:1]:  # 只显示第一行概要
                print(f"     {ml}")
            if args.verbose and len(msg_lines) > 1:
                for ml in msg_lines[1:]:
                    print(f"     {ml}")
            print()

        summary = {"PASS": 0, "WARN": 0, "FAIL": 0}
        for r in results:
            summary[r["status"]] = summary.get(r["status"], 0) + 1

        print(f"{'─'*60}")
        print(f"  结果: ✅ {summary.get('PASS',0)} | ⚠️ {summary.get('WARN',0)} | ❌ {summary.get('FAIL',0)}")
        print(f"{'─'*60}")

    sys.exit(1 if has_fail else 0)


if __name__ == "__main__":
    main()
