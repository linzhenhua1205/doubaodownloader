#!/usr/bin/env python3
"""
Git 可靠拉取脚本 — 解决 GitHub 网络问题导致的 pull/fetch 失败
跨平台 (Windows / macOS / Linux)

特性:
  - 自动重试（指数退避）
  - 多策略切换：HTTPS → SSH → HTTPS+代理
  - 大缓冲区 + 低压缩
  - 网络诊断
  - 支持 pull / fetch / clone
  - 冲突自动处理（rebase/merge 可选）

用法:
  python git-pull-robust.py                              # 拉取当前分支
  python git-pull-robust.py -b main                      # 拉取指定分支
  python git-pull-robust.py -n 10                        # 自定义重试次数
  python git-pull-robust.py --proxy http://127.0.0.1:7890
  python git-pull-robust.py --fetch                      # 仅 fetch 不 merge
  python git-pull-robust.py --rebase                     # pull --rebase
  python git-pull-robust.py --diagnose                   # 仅诊断网络
  python git-pull-robust.py --clone https://github.com/user/repo.git
"""

import argparse
import sys
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
            cmd, capture_output=True, text=True, timeout=timeout,
            encoding='utf-8', errors='replace'
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', '命令超时'
    except FileNotFoundError:
        return -2, '', f'命令不存在: {cmd[0]}'
    except Exception as e:
        return -3, '', str(e)


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
    info("HTTPS 连接测试...")
    code, out, err = run_cmd(
        ['git', 'ls-remote', '--heads', 'https://github.com/git/git.git'],
        timeout=15
    )
    if code == 0:
        ok("HTTPS 连接正常")
    else:
        warn(f"HTTPS 直连失败: {err[:100]}")

    # SSH 连通性
    info("SSH 连接测试...")
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
    for key in ['http.postBuffer', 'core.compression', 'http.proxy', 'http.version']:
        code, out, _ = git(['config', '--get', key])
        if out:
            ok(f"{key} = {out}")
        else:
            warn(f"{key} 未设置")

    # Remote
    remote_url = get_remote_url('origin')
    if remote_url:
        info(f"Remote 'origin' = {remote_url}")
    else:
        warn("Remote 'origin' 未配置")

    # 代理端口检测
    info("常见代理端口检测...")
    proxy_ports = [7890, 7891, 1080, 10809, 10808, 8080, 33210]
    for port in proxy_ports:
        if test_port('127.0.0.1', port):
            ok(f"检测到代理端口 127.0.0.1:{port}")

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
#  策略构建
# ============================================================

def detect_local_proxy():
    """自动检测本地代理端口"""
    proxy_ports = [7890, 7891, 1080, 10809, 10808, 8080, 33210]
    for port in proxy_ports:
        if test_port('127.0.0.1', port):
            return f"http://127.0.0.1:{port}"
    return None


def build_strategies(original_url, proxy_arg):
    """构建拉取策略列表"""
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


# ============================================================
#  拉取前安全检查
# ============================================================

def check_local_state():
    """检查本地工作区状态，防止 pull 覆盖未提交的变更"""
    step("检查本地工作区状态")

    code, status, _ = git(['status', '--porcelain'])
    if status.strip():
        warn("本地有未提交的变更:")
        lines = status.strip().split('\n')
        for line in lines[:10]:
            print(f"  {line}")
        if len(lines) > 10:
            print(f"  ... 共 {len(lines)} 个文件")
        warn("拉取可能导致冲突，建议先 commit 或 stash")
        return False
    else:
        ok("工作区干净，可以安全拉取")
        return True


def auto_stash():
    """自动 stash 未提交的变更"""
    step("自动 stash")
    code, out, err = git(['stash', 'push', '-m', 'auto-stash before pull'])
    if code == 0 and 'No local changes' not in out:
        ok(f"已 stash: {out}")
        return True
    elif 'No local changes' in out:
        info("无变更需要 stash")
        return False
    else:
        warn(f"stash 失败: {err}")
        return False


def auto_unstash():
    """恢复 stash"""
    step("恢复 stash")
    code, out, err = git(['stash', 'pop'])
    if code == 0:
        ok("stash 已恢复")
    else:
        warn(f"stash 恢复失败: {err}")
        warn("手动运行: git stash pop")


# ============================================================
#  拉取核心逻辑
# ============================================================

# 不可恢复错误关键词
FATAL_KEYWORDS = [
    'permission denied', 'Authentication failed',
    'Could not read from remote', 'not a git repository',
    'Host key verification', 'Repository not found',
    'fatal: unable to access'
]


def do_fetch(remote, branch, timeout=300):
    """执行 git fetch"""
    return git(['fetch', remote, branch], timeout=timeout)


def do_pull(remote, branch, rebase=False, timeout=300):
    """执行 git pull"""
    args = ['pull', remote]
    if branch:
        args.append(branch)
    if rebase:
        args.append('--rebase')
    return git(args, timeout=timeout)


def do_clone(url, target_dir, timeout=600):
    """执行 git clone"""
    args = ['clone', url]
    if target_dir:
        args.append(target_dir)
    return git(args, timeout=timeout)


def git_pull_robust(branch, max_retries, rebase=False, fetch_only=False,
                    remote='origin', proxy_arg=None, auto_stash_enabled=False):
    step(f"Git {'Fetch' if fetch_only else 'Pull'} (分支: {branch or '(所有)'}, "
         f"最大重试: {max_retries}, rebase: {rebase})")

    original_url = get_remote_url(remote)
    if not original_url:
        error(f"Remote '{remote}' 不存在")
        return False

    info(f"原始 Remote URL: {original_url}")

    strategies = build_strategies(original_url, proxy_arg)

    # 拉取前安全检查（非 clone/fetch-only 场景）
    stashed = False
    if not fetch_only:
        if not check_local_state():
            if auto_stash_enabled:
                stashed = auto_stash()
            else:
                warn("跳过拉取。使用 --stash 自动暂存，或手动 commit/stash 后重试")
                return False

    for strategy in strategies:
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
        import time
        for i in range(1, max_retries + 1):
            info(f"尝试 {i}/{max_retries} ...")

            if fetch_only:
                code, out, err = do_fetch(remote, branch)
            else:
                code, out, err = do_pull(remote, branch, rebase=rebase)

            if code == 0:
                ok("拉取成功！")
                if out:
                    # 显示拉取摘要
                    for line in out.split('\n')[:5]:
                        if line.strip():
                            print(f"  {line.strip()}")
                # 恢复 stash
                if stashed:
                    auto_unstash()
                info(f"Remote URL 保持为: {strategy['url']}")
                return True

            output = f"{out} {err}"
            warn(f"失败 (exit={code}): {output[:200]}")

            # 检查冲突（pull 特有）
            if 'CONFLICT' in output or 'merge conflict' in output.lower():
                error("检测到合并冲突！")
                error("请手动解决冲突后运行: git add + git commit")
                if stashed:
                    warn("注意: stash 仍未恢复，解决冲突后运行: git stash pop")
                return False

            # 不可恢复的错误，跳到下一个策略
            if any(kw in output for kw in FATAL_KEYWORDS):
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

    # 恢复 stash
    if stashed:
        auto_unstash()

    return False


def git_clone_robust(clone_url, target_dir, max_retries, proxy_arg=None):
    step(f"Git Clone (URL: {clone_url}, 最大重试: {max_retries})")

    strategies = build_strategies(clone_url, proxy_arg)

    import time
    for strategy in strategies:
        step(f"策略: {strategy['name']}")

        # 设置代理
        if strategy['proxy']:
            set_git_config('http.proxy', strategy['proxy'])
            info(f"http.proxy => {strategy['proxy']}")
        else:
            unset_git_config('http.proxy')
            info("http.proxy => (清除)")

        for i in range(1, max_retries + 1):
            info(f"尝试 {i}/{max_retries} ...")

            code, out, err = do_clone(strategy['url'], target_dir, timeout=600)

            if code == 0:
                ok("Clone 成功！")
                return True

            output = f"{out} {err}"
            warn(f"失败 (exit={code}): {output[:200]}")

            if any(kw in output for kw in FATAL_KEYWORDS):
                warn("认证/配置错误，切换策略")
                break

            wait_sec = 2 ** i + 2
            if i < max_retries:
                info(f"等待 {wait_sec}s 后重试...")
                time.sleep(wait_sec)

    error("所有策略均失败")
    return False


# ============================================================
#  主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Git 可靠拉取脚本 — 解决 GitHub 网络问题',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python git-pull-robust.py                              # 拉取当前分支
  python git-pull-robust.py -b main                      # 拉取指定分支
  python git-pull-robust.py --fetch                      # 仅 fetch 不 merge
  python git-pull-robust.py --rebase                     # pull --rebase
  python git-pull-robust.py --stash                      # 自动 stash 后拉取
  python git-pull-robust.py --proxy http://127.0.0.1:7890
  python git-pull-robust.py --diagnose                   # 仅诊断
  python git-pull-robust.py --clone https://github.com/user/repo.git
        """
    )
    parser.add_argument('-b', '--branch', default='',
                        help='目标分支（默认当前分支）')
    parser.add_argument('-n', '--max-retries', type=int, default=5,
                        help='每个策略最大重试次数（默认 5）')
    parser.add_argument('--proxy', default='',
                        help='指定代理地址 (如 http://127.0.0.1:7890)')
    parser.add_argument('--fetch', action='store_true',
                        help='仅 fetch 不 merge')
    parser.add_argument('--rebase', action='store_true',
                        help='使用 pull --rebase（默认 merge）')
    parser.add_argument('--stash', action='store_true',
                        help='拉取前自动 stash 未提交变更，拉取后自动恢复')
    parser.add_argument('--diagnose', action='store_true',
                        help='仅诊断网络，不拉取')
    parser.add_argument('--clone', metavar='URL', default='',
                        help='克隆远程仓库（而非 pull/fetch）')
    parser.add_argument('-d', '--dir', default='',
                        help='clone 目标目录（配合 --clone 使用）')
    parser.add_argument('-r', '--remote', default='origin',
                        help='远程仓库名称（默认 origin）')

    args = parser.parse_args()

    print()
    print("=" * 50)
    print("  Git Robust Pull v1.0 (Python)")
    print("=" * 50)

    # 诊断模式
    if args.diagnose:
        diagnose()
        sys.exit(0)

    # 优化配置
    optimize_git_config()

    # Clone 模式
    if args.clone:
        success = git_clone_robust(
            args.clone, args.dir, args.max_retries, proxy_arg=args.proxy
        )
        if success:
            print()
            ok(f"Clone 完成: {args.clone}")
            sys.exit(0)
        else:
            print()
            error("Clone 失败 — 请运行诊断: python git-pull-robust.py --diagnose")
            sys.exit(1)

    # Pull / Fetch 模式
    # 确认在 git 仓库中
    code, _, _ = git(['rev-parse', '--git-dir'])
    if code != 0:
        error("当前目录不是 Git 仓库")
        sys.exit(1)

    # 确定分支
    branch = args.branch or get_current_branch()
    if not branch and not args.fetch:
        error("无法确定当前分支")
        sys.exit(1)
    if branch:
        info(f"目标分支: {branch}")

    success = git_pull_robust(
        branch=branch,
        max_retries=args.max_retries,
        rebase=args.rebase,
        fetch_only=args.fetch,
        remote=args.remote,
        proxy_arg=args.proxy if args.proxy else None,
        auto_stash_enabled=args.stash
    )

    if success:
        print()
        action = 'Fetch' if args.fetch else 'Pull'
        ok(f"完成！{action} {branch or '所有分支'} 从 {args.remote}")
        sys.exit(0)
    else:
        print()
        error("拉取失败 — 请运行诊断: python git-pull-robust.py --diagnose")
        sys.exit(1)


if __name__ == '__main__':
    main()
