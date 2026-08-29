#!/usr/bin/env python3
"""
Git 可靠推送脚本 — 解决 GitHub 网络问题导致的推送失败
跨平台 (Windows / macOS / Linux)

特性:
  - 自动重试（指数退避）
  - 多策略切换：HTTPS → SSH → HTTPS+代理
  - 大缓冲区 + 低压缩
  - 网络诊断
  - 自动 commit

用法:
  python git-push-robust.py                              # 推送当前分支
  python git-push-robust.py -b main                      # 推送指定分支
  python git-push-robust.py -n 10                        # 自定义重试次数
  python git-push-robust.py --proxy http://127.0.0.1:7890
  python git-push-robust.py --commit -m "update"        # 先 commit 再 push
  python git-push-robust.py --diagnose                   # 仅诊断网络
  python git-push-robust.py --force                      # 强制推送
"""

import argparse
import os
import sys
import time
import socket
import subprocess
import re
import platform


# ============================================================
#  工具函数
# ============================================================

def run_cmd(cmd, timeout=120):
    """执行命令，返回 (returncode, stdout, stderr)"""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace'
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', '命令超时'
    except Exception as e:
        return -2, '', str(e)


def git(args, timeout=120):
    """执行 git 命令"""
    return run_cmd(['git'] + args, timeout=timeout)


def info(msg):   print(f"[INFO]  {msg}")
def ok(msg):     print(f"\033[92m[OK]    {msg}\033[0m" if platform.system() != 'Windows' else f"[OK]    {msg}")
def warn(msg):   print(f"\033[93m[WARN]  {msg}\033[0m" if platform.system() != 'Windows' else f"[WARN]  {msg}")
def error(msg):  print(f"\033[91m[ERROR] {msg}\033[0m" if platform.system() != 'Windows' else f"[ERROR] {msg}")
def step(msg):   print(f"\n>>> {msg}")


def get_current_branch():
    code, out, _ = git(['rev-parse', '--abbrev-ref', 'HEAD'])
    return out.strip() if code == 0 else None


def get_remote_url(remote):
    code, out, _ = git(['remote', 'get-url', remote])
    return out.strip() if code == 0 else None


def set_remote_url(remote, url):
    git(['remote', 'set-url', remote, url])


def set_git_config(key, value):
    git(['config', key, value])


def unset_git_config(key):
    git(['config', '--unset', key])


def test_port(host, port, timeout=1):
    """检测端口是否可连接"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def https_to_ssh(url):
    """https://github.com/user/repo.git -> git@github.com:user/repo.git"""
    m = re.match(r'^https://([^/]+)/(.+)$', url)
    return f"git@{m.group(1)}:{m.group(2)}" if m else None


def ssh_to_https(url):
    """git@github.com:user/repo.git -> https://github.com/user/repo.git"""
    m = re.match(r'^git@([^:]+):(.+)$', url)
    return f"https://{m.group(1)}/{m.group(2)}" if m else None


# ============================================================
#  诊断
# ============================================================

def diagnose():
    step("网络诊断")

    # DNS
    info("DNS 解析 github.com...")
    try:
        ip = socket.gethostbyname('github.com')
        ok(f"DNS 解析成功: {ip}")
    except Exception as e:
        error(f"DNS 解析失败: {e}")

    # HTTPS 连通性
    info("HTTPS 连接测试 (https://github.com)...")
    code, out, err = run_cmd(
        ['git', 'ls-remote', '--heads', 'https://github.com/git/git.git'],
        timeout=15
    )
    if code == 0:
        ok("HTTPS 连接正常")
    else:
        warn(f"HTTPS 直连失败: {err[:100]}")
        info("可能需要代理或 VPN")

    # SSH 连通性
    info("SSH 连接测试 (git@github.com)...")
    code, out, err = run_cmd(
        ['ssh', '-T', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=no', 'git@github.com'],
        timeout=15
    )
    out_full = f"{out} {err}"
    if 'successfully authenticated' in out_full or 'successfully' in out_full:
        ok("SSH 连接正常 (已认证)")
    elif 'Permission denied' in out_full:
        warn("SSH 密钥未配置 — 运行: ssh-keygen -t ed25519")
    else:
        warn(f"SSH 连接失败: {out_full[:100]}")

    # Git 配置检查
    info("Git 配置检查...")
    for key in ['http.postBuffer', 'core.compression', 'http.proxy', 'http.version',
                'http.lowSpeedLimit', 'http.lowSpeedTime']:
        code, out, _ = git(['config', '--get', key])
        if out:
            ok(f"{key} = {out}")
        else:
            warn(f"{key} 未设置")

    # Remote
    remote_url = get_remote_url('origin')
    info(f"Remote 'origin' = {remote_url}")

    # 代理端口检测
    info("常见代理端口检测...")
    proxy_ports = [7890, 7891, 1080, 10809, 10808, 8080, 33210]
    for port in proxy_ports:
        if test_port('127.0.0.1', port):
            ok(f"检测到代理端口 127.0.0.1:{port} (可能是 Clash/V2Ray/SS)")

    print()
    info("诊断完成。")


# ============================================================
#  Git 配置优化
# ============================================================

def optimize_git_config():
    step("优化 Git 网络配置")

    set_git_config('http.postBuffer', '524288000')       # 500MB
    ok("http.postBuffer = 524288000 (500MB)")

    set_git_config('core.compression', '0')
    ok("core.compression = 0")

    set_git_config('http.version', 'HTTP/1.1')
    ok("http.version = HTTP/1.1")

    set_git_config('http.lowSpeedLimit', '1000')
    set_git_config('http.lowSpeedTime', '600')
    ok("http.lowSpeedLimit=1000, lowSpeedTime=600 (10分钟超时)")


# ============================================================
#  Commit
# ============================================================

def git_commit(message=''):
    step("Git Commit")

    code, status, _ = git(['status', '--porcelain'])
    if not status.strip():
        info("没有未提交的变更")
        return

    git(['add', '-A'])
    ok("git add -A")

    if not message:
        from datetime import datetime
        message = f"Auto commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    code, out, err = git(['commit', '-m', message])
    if code == 0:
        ok(f"git commit: {message}")
    else:
        error(f"commit 失败: {err}")


# ============================================================
#  推送策略
# ============================================================

def detect_local_proxy():
    """自动检测本地代理端口"""
    proxy_ports = [7890, 7891, 1080, 10809, 10808, 8080, 33210]
    for port in proxy_ports:
        if test_port('127.0.0.1', port):
            return f"http://127.0.0.1:{port}"
    return None


def build_strategies(original_url, proxy_arg):
    """构建推送策略列表"""
    strategies = []

    # 策略 1: 原始 URL 直连
    strategies.append({
        'name': '原始直连',
        'url': original_url,
        'proxy': ''
    })

    # 策略 2: 切换协议
    if original_url.startswith('https://'):
        ssh_url = https_to_ssh(original_url)
        if ssh_url:
            strategies.append({'name': 'SSH 协议', 'url': ssh_url, 'proxy': ''})
    elif original_url.startswith('git@'):
        https_url = ssh_to_https(original_url)
        if https_url:
            strategies.append({'name': 'HTTPS 协议', 'url': https_url, 'proxy': ''})

    # 策略 3: HTTPS + 代理
    proxy = proxy_arg or detect_local_proxy()
    if proxy:
        https_url = original_url
        if original_url.startswith('git@'):
            https_url = ssh_to_https(original_url)
        if https_url:
            strategies.append({
                'name': f'HTTPS + 代理 ({proxy})',
                'url': https_url,
                'proxy': proxy
            })

    return strategies


def git_push(branch, max_retries, force=False, remote='origin'):
    step(f"Git Push (分支: {branch}, 最大重试: {max_retries})")

    original_url = get_remote_url(remote)
    if not original_url:
        error(f"Remote '{remote}' 不存在")
        return False

    info(f"原始 Remote URL: {original_url}")

    strategies = build_strategies(original_url, None)
    # 如果用户指定了 --proxy，添加额外策略
    strategies_with_proxy = build_strategies(original_url, getattr(git_push, '_proxy_arg', None))

    for strategy in strategies_with_proxy:
        step(f"策略: {strategy['name']}")

        # 设置 remote URL
        set_remote_url(remote, strategy['url'])
        info(f"Remote URL => {strategy['url']}")

        # 设置代理
        if strategy['proxy']:
            set_git_config('http.proxy', strategy['proxy'])
            info(f"http.proxy => {strategy['proxy']}")
        else:
            unset_git_config('http.proxy')
            info("http.proxy => (清除)")

        # 重试循环
        for i in range(1, max_retries + 1):
            info(f"尝试 {i}/{max_retries} ...")

            push_args = ['push', remote, branch]
            if force:
                push_args.append('--force')

            code, out, err = git(push_args, timeout=300)
            if code == 0:
                ok("推送成功！")
                info(f"Remote URL 保持为: {strategy['url']}")
                return True

            output = f"{out} {err}"
            warn(f"失败 (exit={code}): {output[:200]}")

            # 不可恢复的错误，跳到下一个策略
            if any(kw in output for kw in [
                'permission denied', 'Authentication failed',
                'Could not read from remote', 'not a git repository',
                'Host key verification'
            ]):
                warn("认证/配置错误，切换策略")
                break

            # 可恢复的错误，指数退避重试
            wait_sec = 2 ** i + 2  # 4s, 6s, 10s, 18s, 34s...
            if i < max_retries:
                info(f"等待 {wait_sec}s 后重试...")
                time.sleep(wait_sec)

    # 所有策略失败
    error("所有策略均失败")

    # 恢复原始 URL
    set_remote_url(remote, original_url)
    info(f"Remote URL 恢复为: {original_url}")

    return False


# ============================================================
#  主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Git 可靠推送脚本 — 解决 GitHub 网络问题',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python git-push-robust.py                              # 推送当前分支
  python git-push-robust.py -b main                      # 推送指定分支
  python git-push-robust.py --commit -m "update docs"    # commit + push
  python git-push-robust.py --proxy http://127.0.0.1:7890
  python git-push-robust.py --diagnose                   # 仅诊断
  python git-push-robust.py -n 10 --force                # 10次重试 + 强制
        """
    )
    parser.add_argument('-b', '--branch', default='',
                        help='目标分支（默认当前分支）')
    parser.add_argument('-n', '--max-retries', type=int, default=5,
                        help='每个策略最大重试次数（默认 5）')
    parser.add_argument('--proxy', default='',
                        help='指定代理地址 (如 http://127.0.0.1:7890)')
    parser.add_argument('--commit', action='store_true',
                        help='推送前先执行 git add + commit')
    parser.add_argument('-m', '--message', default='',
                        help='commit 消息（配合 --commit 使用）')
    parser.add_argument('--diagnose', action='store_true',
                        help='仅诊断网络，不推送')
    parser.add_argument('--force', action='store_true',
                        help='强制推送 (--force)')
    parser.add_argument('-r', '--remote', default='origin',
                        help='远程仓库名称（默认 origin）')
    parser.add_argument('--async', dest='async_mode', action='store_true',
                        help='后台异步推送：nohup 分离执行，立即返回不阻塞（推荐 AI 触发用）')
    parser.add_argument('--log', default='',
                        help='异步模式日志文件（默认 ~/cow/tmp/git-push-async.log）')

    args = parser.parse_args()

    # ⚠️ 后台异步模式：立即 detach，主进程马上退出，不阻塞调用方
    if args.async_mode:
        import subprocess as sp
        import platform as _plat
        log_file = args.log or os.path.expanduser('~/cow/tmp/git-push-async.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        # 去掉 --async/--log，重新以本脚本普通模式后台运行
        argv = sys.argv[:]
        for i in range(len(argv) - 1, -1, -1):
            if argv[i] in ('--async', '--log'):
                del argv[i]
            elif argv[i].startswith('--async'):
                del argv[i]
        # 处理 --log 的值
        if '--log' in argv:
            idx = argv.index('--log')
            del argv[idx:idx + 2]
        cmd = [sys.executable] + argv
        with open(log_file, 'a', encoding='utf-8') as lf:
            if _plat.system() == 'Windows':
                sp.Popen(cmd, stdout=lf, stderr=sp.STDOUT, close_fds=True,
                         creationflags=getattr(sp, 'DETACHED_PROCESS', 0))
            else:
                devnull = open(os.devnull, 'w')
                sp.Popen(cmd, stdout=lf, stderr=sp.STDOUT, stdin=devnull,
                         start_new_session=True, close_fds=True)
        print(f"[ASYNC] 已在后台触发 push（日志: {log_file}），立即返回，不阻塞当前任务")
        print("[ASYNC] 推送结果由脚本后台执行并记录，无需等待；网络不佳会自动重试")
        sys.exit(0)

    print()
    print("=" * 50)
    print("  Git Robust Push v1.0 (Python)")
    print("=" * 50)

    # 确认在 git 仓库中
    code, _, _ = git(['rev-parse', '--git-dir'])
    if code != 0:
        error("当前目录不是 Git 仓库")
        sys.exit(1)

    # 诊断模式
    if args.diagnose:
        diagnose()
        sys.exit(0)

    # 确定分支
    branch = args.branch or get_current_branch()
    if not branch:
        error("无法确定当前分支")
        sys.exit(1)
    info(f"目标分支: {branch}")

    # 优化配置
    optimize_git_config()

    # Commit
    if args.commit:
        git_commit(args.message)

    # 传递 proxy 参数给 push
    git_push._proxy_arg = args.proxy

    # ⚠️ Force 推送确认
    if args.force:
        print()
        warn("⚠️  即将执行 --force 强制推送！覆盖远程历史不可逆。")
        branch_display = args.branch or get_current_branch() or "当前分支"
        print(f"    目标仓库: {args.remote}/{branch_display}")
        confirm = input("    确认强制推送？(yes/NO): ").strip().lower()
        if confirm not in ('yes', 'y'):
            error("已取消强制推送")
            sys.exit(0)
        ok("已确认，执行强制推送")

    # 推送
    success = git_push(branch, args.max_retries, force=args.force, remote=args.remote)

    if success:
        print()
        ok(f"完成！分支 {branch} 已推送到 {args.remote}")
        sys.exit(0)
    else:
        print()
        error("推送失败 — 请运行诊断: python git-push-robust.py --diagnose")
        sys.exit(1)


if __name__ == '__main__':
    main()
