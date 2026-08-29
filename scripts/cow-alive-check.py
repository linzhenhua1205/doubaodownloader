#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#================================================================
# cow-alive-check.py v1 — CowAgent 保活检测与自愈脚本
#
# 用途：检测 CowAgent（cow status）是否处于 running 状态；若挂死
#       （进程不存活 / PID 文件失效），自动执行 cow start 恢复。
#       同时可修复「进程存活但 PID 文件丢失/不匹配」的半死状态。
#
# 判据设计（第一性原理）：
#   cow status 输出 "is running" 的底层依据 = PID 文件存在 + kill -0 存活验证
#   （见 CowAgent cli/commands/process.py _read_pid()）。本脚本不依赖对
#   CLI 彩色文本的脆弱解析，直接用 pgrep -f <app.py> 探测进程真存活
#   （主判据），cow status 文本仅作辅判据交叉验证。
#
# 恢复动作（分级，防双实例）：
#   healthy     : 进程活 + PID 文件匹配            → 无动作，退出 0
#   pid-stale   : 进程活 + PID 文件缺失/不匹配      → 重建 PID 文件（不 start，防双实例）
#   dead        : 进程死                            → cow start（start 幂等：内部清理残留 PID 再启动）
#   multi       : 检测到多个 app.py 进程            → 仅告警不处理（多实例需人工裁决）
#
# 防抖：state 文件记录最近一次恢复时间，防抖窗口（默认 300s）内不重复
#       恢复，防止「启动即崩溃 → 反复重启」风暴。
#
# 用法：
#   python3 scripts/cow-alive-check.py                 # 检测 + 自愈（crontab 主机制）
#   python3 scripts/cow-alive-check.py --check-only     # 只检测不恢复；退出码 0=健康 1=异常
#   python3 scripts/cow-alive-check.py --check-only --fix-pid  # 检测 + 允许 PID 修复（进程内 hook 用）
#   python3 scripts/cow-alive-check.py --dry-run        # 模拟：打印将执行的动作，不真正执行
#   python3 scripts/cow-alive-check.py --interval 600   # 防抖窗口 600s
#   python3 scripts/cow-alive-check.py --quiet          # 减少 stdout（日志文件照常）
#
# 集成（两层保活）：
#   L1 crontab（进程外主机制，进程挂死也能救）：
#       */5 * * * * /usr/bin/python3 /home/lzh/cow/scripts/cow-alive-check.py >> /home/lzh/cow/tmp/logs/cow-alive-check.cron.log 2>&1
#   L2 scheduler 进程内 hook（辅机制，每任务执行前自检）：
#       CowAgent/agent/tools/scheduler/scheduler_service.py 中
#       _check_and_execute_tasks() 循环内调用本脚本 --check-only --fix-pid
#       （进程内绝不 start，防止双实例；只修复 PID 文件半死态）
#
# 变更日志：
#   2026-08-14 v1 created（系统加固：cow 保活 + 双实例防护 + 防抖 + 分级恢复）
#================================================================

import argparse
import os
import subprocess
import sys
import time

#----------------------------------------------------------------
# 常量（绝对路径，crontab 环境 PATH 不含 ~/.local/bin）
#----------------------------------------------------------------
HOME = os.path.expanduser("~")
COW_BIN = os.path.join(HOME, ".local", "bin", "cow")       # cow CLI
COW_APP_PY = os.path.join(HOME, "CowAgent", "app.py")      # CowAgent 主进程
COW_PID_FILE = os.path.join(HOME, "CowAgent", ".cow.pid")  # PID 文件
LOG_DIR = os.path.join(HOME, "cow", "tmp", "logs")
LOG_FILE = os.path.join(LOG_DIR, "cow-alive-check.log")
STATE_FILE = os.path.join(LOG_DIR, "cow-alive-check.state")  # 防抖时间戳
DEFAULT_INTERVAL = 300  # 防抖窗口（秒）


def _log(msg: str, quiet: bool = False):
    """写日志文件 + stdout（--quiet 时 stdout 静默）。"""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except OSError as e:
        line += f" (log write failed: {e})"
    if not quiet:
        print(line)


def _get_alive_pids() -> list:
    """返回存活中的 CowAgent 主进程 PID 列表。

    用 /proc/<pid>/cmdline 做 **精确 argv 匹配**（最后一个参数 == app.py 的
    realpath），而非 pgrep -f 的字符串子串匹配。子串匹配会把命令行文本中
    恰好含该路径的无关进程（grep/vi/bash -c/本脚本的 sed 测试等）误判为
    CowAgent 活进程——实测已复现该误匹配，故弃用 pgrep。
    """
    app_real = os.path.realpath(COW_APP_PY)
    pids = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                raw = f.read().split(b"\x00")
        except (OSError, FileNotFoundError):
            continue
        args = [a.decode(errors="ignore") for a in raw if a]
        if len(args) >= 2 and os.path.realpath(args[-1]) == app_real:
            try:
                os.kill(pid, 0)
                pids.append(pid)
            except (ProcessLookupError, PermissionError):
                continue
    return pids


def _read_pid_file():
    """读 PID 文件，返回 (pid, exists)。损坏文件返回 (None, True)。"""
    if not os.path.exists(COW_PID_FILE):
        return None, False
    try:
        with open(COW_PID_FILE) as f:
            return int(f.read().strip()), True
    except (ValueError, OSError):
        return None, True


def _write_pid_file(pid: int) -> bool:
    try:
        with open(COW_PID_FILE, "w") as f:
            f.write(str(pid))
        return True
    except OSError as e:
        _log(f"[ERR] 重建 PID 文件失败: {e}")
        return False


def _recently_recovered(interval: int) -> bool:
    """防抖：interval 秒内是否已执行过恢复动作。"""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                last = float(f.read().strip())
            if time.time() - last < interval:
                return True
    except (ValueError, OSError):
        pass
    return False


def _mark_recovered():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            f.write(str(time.time()))
    except OSError:
        pass


def _run_cow_start(quiet: bool) -> bool:
    """执行 cow start（--no-logs 防 tail 阻塞），返回是否成功。"""
    try:
        r = subprocess.run(
            [COW_BIN, "start", "--no-logs"],
            capture_output=True, text=True, timeout=90,
        )
        out = (r.stdout or "") + (r.stderr or "")
        _log(f"    cow start 输出: {out.strip()[:300]}")
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        _log("[ERR] cow start 超时（90s）")
        return False
    except OSError as e:
        _log(f"[ERR] cow start 无法执行: {e}")
        return False


def main():
    ap = argparse.ArgumentParser(description="CowAgent 保活检测与自愈")
    ap.add_argument("--check-only", action="store_true",
                    help="只检测不恢复；退出码 0=健康 1=异常（供进程内 hook）")
    ap.add_argument("--fix-pid", action="store_true",
                    help="允许修复 PID 文件半死态（配合 --check-only；绝不 start）")
    ap.add_argument("--dry-run", action="store_true",
                    help="模拟模式：只打印将执行的动作，不真正执行")
    ap.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                    help=f"防抖窗口秒数（默认 {DEFAULT_INTERVAL}）")
    ap.add_argument("--quiet", action="store_true", help="减少 stdout")
    args = ap.parse_args()

    #----------------------------------------------------------------
    # 1. 探测进程真存活（主判据）
    #----------------------------------------------------------------
    alive_pids = _get_alive_pids()

    # 辅判据：cow status 文本（仅日志参考，不参与决策）
    try:
        st = subprocess.run([COW_BIN, "status"], capture_output=True, text=True, timeout=15)
        status_txt = (st.stdout or "") + (st.stderr or "")
        cow_running = "is running" in status_txt and "is not running" not in status_txt
    except (subprocess.SubprocessError, OSError):
        status_txt, cow_running = "", None  # None = 无法确认

    #----------------------------------------------------------------
    # 2. 状态判定
    #----------------------------------------------------------------
    if len(alive_pids) > 1:
        _log(f"[WARN] 检测到 {len(alive_pids)} 个 CowAgent 进程 {alive_pids}（多实例异常，仅告警不处理）")
        sys.exit(1)

    pid_file_pid, pid_file_exists = _read_pid_file()
    healthy = bool(alive_pids) and pid_file_exists and alive_pids[0] == pid_file_pid

    if healthy:
        _log(f"[OK] CowAgent healthy (PID {alive_pids[0]}, cow status: {'running' if cow_running else '?未确认'})", args.quiet)
        sys.exit(0)

    #----------------------------------------------------------------
    # 3. 非健康 → 分级恢复
    #----------------------------------------------------------------
    state = "pid-stale" if alive_pids else "dead"
    _log(f"[!!] CowAgent {state}: alive={alive_pids}, pid_file={pid_file_pid if pid_file_exists else 'missing'}, "
         f"cow status: {status_txt.strip().splitlines()[0] if status_txt else '?无法获取'}", args.quiet)

    # 防抖：恢复窗口内不重复动作（check-only 除外，它无副作用）
    if not args.check_only and _recently_recovered(args.interval):
        _log(f"[SKIP] {args.interval}s 防抖窗口内已恢复过，跳过本次动作", args.quiet)
        sys.exit(0 if not args.check_only else 1)

    # 3a. pid-stale：进程活着但 PID 文件失效 → 重建 PID 文件（不 start）
    if alive_pids:
        if not (args.check_only and not args.fix_pid):
            action = f"重建 PID 文件 → {alive_pids[0]}"
            _log(f"[FIX] {action}", args.quiet)
            if not args.dry_run:
                if _write_pid_file(alive_pids[0]):
                    _mark_recovered()
                    _log(f"[OK] PID 文件已重建为 {alive_pids[0]}（半死态自愈）", args.quiet)
                    sys.exit(0)
                _log("[ERR] PID 文件重建失败", args.quiet)
                sys.exit(2)
            sys.exit(0)
        else:
            _log("[INFO] --check-only 模式：检测到 pid-stale，未执行修复", args.quiet)
            sys.exit(1)

    # 3b. dead：进程不存活 → cow start
    if args.check_only:
        _log("[INFO] --check-only 模式：检测到进程不存活，未执行重启", args.quiet)
        sys.exit(1)

    action = f"cow start 重启（{COW_BIN} start --no-logs）"
    _log(f"[RESTART] {action}", args.quiet)
    if args.dry_run:
        _log("[DRY-RUN] 模拟完成，未真正重启", args.quiet)
        sys.exit(0)

    if not _run_cow_start(args.quiet):
        _log("[ERR] cow start 失败，请人工检查（日志: ~/CowAgent/nohup.out）")
        sys.exit(2)

    # 4. 启动后验证
    time.sleep(3)
    new_pids = _get_alive_pids()
    if new_pids:
        _mark_recovered()
        _log(f"[OK] CowAgent 已恢复运行 (PID {new_pids[0]})")
        sys.exit(0)
    _log("[ERR] cow start 已执行但进程未出现，请人工检查")
    sys.exit(2)


if __name__ == "__main__":
    main()
