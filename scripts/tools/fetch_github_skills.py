#!/usr/bin/env python3
"""
GitHub Agent Skills 全量检索与下载脚本

功能:
  1. 通过 GitHub API 检索所有 Agent Skills 仓库（按 topic、关键词、已知列表）
  2. 下载到本地 tmp 目录
  3. 已有仓库自动 git pull 更新

用法:
  python fetch_github_skills.py              # 检索 + 下载全部
  python fetch_github_skills.py --list-only  # 仅列出仓库，不下载
  python fetch_github_skills.py --update     # 只更新已有仓库
  python fetch_github_skills.py --search     # 仅搜索新仓库

环境变量:
  GITHUB_TOKEN          GitHub Personal Access Token（可选，有则 API 限速更高）
  SKILLS_TARGET_DIR     目标目录（默认: ./skills）
"""

import os
import sys
import json
import time
import shutil
import hashlib
import argparse
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# ─── 配置 ───────────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
TARGET_DIR = Path(os.environ.get("SKILLS_TARGET_DIR", Path(__file__).parent / "skills"))
API_BASE = "https://api.github.com"
CACHE_FILE = TARGET_DIR / ".skills_cache.json"
MAX_PER_PAGE = 100
MIN_STARS = 5          # 最低星标过滤
REQUEST_DELAY = 1.2    # 未认证 API 限速 ~60次/小时，留足间隔
MAX_RETRIES = 3

# ─── 已知高质量 Skills 仓库（不依赖 API 也可以下载） ─────────
KNOWN_REPOS = [
    # 官方 Skills
    ("anthropics/skills",              "Anthropic 官方 Skills (文档/PPT/Excel/前端等)"),
    ("openai/skills",                  "OpenAI Codex Skills 目录"),
    ("vercel-labs/agent-skills",       "Vercel React/Next.js 最佳实践"),
    ("vercel-labs/skills",             "find-skills 发现工具"),
    ("expo/skills",                    "Expo React Native 开发"),
    ("kepano/obsidian-skills",         "Obsidian 知识管理"),
    ("stripe/ai",                      "Stripe 支付 Skills"),
    ("trailofbits/skills",             "Trail of Bits 安全审计"),
    ("vuejs-ai/skills",                "Vue.js 最佳实践"),
    ("supabase/agent-skills",          "Supabase PostgreSQL 最佳实践"),
    ("remotion-dev/skills",            "Remotion 视频动画制作"),
    ("heygen-com/skills",              "HeyGen 数字人视频"),
    ("squirrelscan/skills",            "网站安全审计 (230+ 规则)"),

    # 资源合集
    ("ComposioHQ/awesome-claude-skills", "Skills 精选列表"),
    ("affaan-m/everything-claude-code",  "Anthropic 黑客松冠军配置集"),

    # 工具 & 管理
    ("yusufkaraaslan/Skill_Seekers",     "多源抓取 → Agent Skills 生成器"),
    ("vercel-labs/agent-browser",         "浏览器自动化 Skill"),
    ("Kamalnrf/claude-plugins",          "Claude Plugins 注册表"),

    # 项目开发
    ("obra/superpowers",                 "AI 编程技能框架 (头脑风暴/计划/TDD/审查)"),
    ("OthmanAdi/planning-with-files",    "Markdown 文件外部记忆 (最强 Skill)"),
    ("nextlevelbuilder/ui-ux-pro-max-skill", "专业前端设计 Skill"),
    ("browser-use/browser-use",          "浏览器自动化操作"),

    # 内容创作
    ("JimLiu/baoyu-skills",              "宝玉老师 Skills 集 (公众号/PPT/漫画)"),
    ("blader/humanizer",                 "AI 文本人类化"),
    ("coreyhaines31/marketingskills",   "营销 Skills (25+ 个)"),
]


def get_headers() -> dict:
    """构建 API 请求头"""
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "skills-fetcher/1.0",
    }
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def api_request(url: str, retries: int = MAX_RETRIES) -> Optional[dict]:
    """带重试的 GitHub API 请求"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=get_headers())
            with urllib.request.urlopen(req, timeout=30) as resp:
                remaining = resp.headers.get("X-RateLimit-Remaining", "?")
                reset_ts = resp.headers.get("X-RateLimit-Reset", "0")
                reset_time = datetime.fromtimestamp(int(reset_ts)).strftime("%H:%M:%S")
                print(f"  [API] 剩余配额: {remaining}, 重置: {reset_time}")
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 403 and "rate limit" in str(e.read().decode(errors="ignore")).lower():
                print(f"  [API] 限速，等待 60 秒...")
                time.sleep(60)
                continue
            if e.code == 404:
                return None
            print(f"  [API] HTTP {e.code} at {url}")
            return None
        except urllib.error.URLError as e:
            print(f"  [API] 网络错误: {e.reason}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            return None
        except Exception as e:
            print(f"  [API] 错误: {e}")
            return None
    return None


def search_github_topics() -> list[dict]:
    """通过 GitHub topic 搜索 Skills 仓库"""
    repos = []
    topics = ["agent-skills", "claude-skills", "claude-code-skills", "agent-skills-spec"]
    keywords = ["agent-skills", "claude code skills", "SKILL.md", "claude-skills"]

    print("\n🔍 通过 GitHub Topic 搜索...")
    for topic in topics:
        print(f"  搜索 topic: {topic}")
        url = f"{API_BASE}/search/repositories?q=topic:{topic}+stars:>={MIN_STARS}&sort=stars&order=desc&per_page={MAX_PER_PAGE}"
        data = api_request(url)
        if data and "items" in data:
            for item in data["items"]:
                repos.append({
                    "full_name": item["full_name"],
                    "description": (item.get("description") or "")[:100],
                    "stars": item["stargazers_count"],
                    "url": item["clone_url"],
                    "updated": item["updated_at"],
                    "source": f"topic:{topic}",
                })
            print(f"    找到 {len(data['items'])} 个")
        time.sleep(REQUEST_DELAY)

    print(f"\n🔍 通过关键词搜索...")
    for kw in keywords:
        print(f"  搜索关键词: {kw}")
        url = f"{API_BASE}/search/repositories?q={kw}+stars:>={MIN_STARS}&sort=stars&order=desc&per_page={MAX_PER_PAGE}"
        data = api_request(url)
        if data and "items" in data:
            for item in data["items"]:
                repos.append({
                    "full_name": item["full_name"],
                    "description": (item.get("description") or "")[:100],
                    "stars": item["stargazers_count"],
                    "url": item["clone_url"],
                    "updated": item["updated_at"],
                    "source": f"keyword:{kw}",
                })
            print(f"    找到 {len(data['items'])} 个")
        time.sleep(REQUEST_DELAY)

    return repos


def search_github_code() -> list[dict]:
    """通过代码搜索 SKILL.md 文件来发现 Skills 仓库"""
    repos = []
    print(f"\n🔍 通过 SKILL.md 文件搜索...")
    url = f"{API_BASE}/search/code?q=SKILL.md+in:path+path:skills&sort=indexed&order=desc&per_page={MAX_PER_PAGE}"
    data = api_request(url)
    if data and "items" in data:
        seen = set()
        for item in data["items"]:
            repo_full = item["repository"]["full_name"]
            if repo_full not in seen:
                seen.add(repo_full)
                repos.append({
                    "full_name": repo_full,
                    "description": (item["repository"].get("description") or "")[:100],
                    "stars": item["repository"].get("stargazers_count", 0),
                    "url": item["repository"]["clone_url"],
                    "updated": item["repository"].get("updated_at", ""),
                    "source": "code:SKILL.md",
                })
        print(f"    找到 {len(repos)} 个")
    time.sleep(REQUEST_DELAY)
    return repos


def merge_repos(all_repos: list[dict]) -> list[dict]:
    """去重合并（按 full_name），保留最高星标版本"""
    merged = {}
    for r in all_repos:
        name = r["full_name"]
        if name not in merged or r["stars"] > merged[name]["stars"]:
            merged[name] = r
    return sorted(merged.values(), key=lambda x: x["stars"], reverse=True)


def load_cache() -> dict:
    """加载本地缓存"""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"repos": {}, "last_updated": None}


def save_cache(repos: list[dict]):
    """保存缓存"""
    cache = {
        "repos": {r["full_name"]: r for r in repos},
        "last_updated": datetime.now().isoformat(),
    }
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def get_repo_dir(full_name: str) -> Path:
    """获取仓库本地目录名"""
    name = full_name.replace("/", "-")
    return TARGET_DIR / name


def clone_or_pull(repo: dict, update_only: bool = False, dry_run: bool = False) -> str:
    """克隆或更新仓库。返回状态: 'cloned' | 'updated' | 'skipped' | 'failed'"""
    full_name = repo["full_name"]
    url = repo["url"]
    target = get_repo_dir(full_name)

    if dry_run:
        if target.exists():
            return "skipped"
        return "would_clone"

    if target.exists():
        if (target / ".git").exists():
            # 已有 git 仓库，尝试 pull
            try:
                result = subprocess.run(
                    ["git", "pull", "--ff-only"],
                    cwd=str(target),
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0:
                    if "Already up to date" in result.stdout or "Already up-to-date" in result.stdout:
                        return "skipped"
                    return "updated"
                else:
                    # pull 失败，尝试 reset + pull
                    subprocess.run(["git", "fetch", "origin"], cwd=str(target),
                                   capture_output=True, timeout=30)
                    subprocess.run(["git", "reset", "--hard", "origin/HEAD"],
                                   cwd=str(target), capture_output=True, timeout=30)
                    return "updated"
            except Exception as e:
                print(f"    ⚠ pull 失败: {e}")
                return "failed"
        else:
            # 目录存在但非 git 仓库，跳过
            return "skipped"
    elif update_only:
        return "skipped"
    else:
        # 新克隆
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, str(target)],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                return "cloned"
            else:
                print(f"    ⚠ clone 失败: {result.stderr.strip()[:200]}")
                # 清理失败的目录
                if target.exists():
                    shutil.rmtree(target, ignore_errors=True)
                return "failed"
        except Exception as e:
            print(f"    ⚠ clone 异常: {e}")
            return "failed"


def main():
    parser = argparse.ArgumentParser(description="GitHub Agent Skills 全量检索与下载")
    parser.add_argument("--list-only", action="store_true", help="仅列出仓库，不下载")
    parser.add_argument("--update", action="store_true", help="仅更新已有仓库")
    parser.add_argument("--search", action="store_true", help="仅搜索新仓库并保存缓存")
    parser.add_argument("--target-dir", type=str, default=str(TARGET_DIR),
                        help=f"目标目录 (默认: {TARGET_DIR})")
    parser.add_argument("--no-api", action="store_true", help="跳过 API 搜索，仅用已知列表")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际下载")
    args = parser.parse_args()

    global TARGET_DIR
    TARGET_DIR = Path(args.target_dir)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  GitHub Agent Skills 全量检索与下载")
    print(f"  目标目录: {TARGET_DIR}")
    print(f"  API Token: {'已配置' if GITHUB_TOKEN else '未配置 (限速 60次/时)'}")
    print("=" * 60)

    all_repos = []

    # 1. 加载已知列表
    print("\n📋 加载已知 Skills 仓库列表...")
    for full_name, desc in KNOWN_REPOS:
        all_repos.append({
            "full_name": full_name,
            "description": desc,
            "stars": 0,
            "url": f"https://github.com/{full_name}.git",
            "updated": "",
            "source": "known-list",
        })
    print(f"   已知列表: {len(KNOWN_REPOS)} 个")

    # 2. 加载本地缓存
    cache = load_cache()
    if cache["repos"]:
        cached_count = len(cache["repos"])
        print(f"   本地缓存: {cached_count} 个 (更新于 {cache['last_updated']})")
        for r in cache["repos"].values():
            if r["source"] != "known-list":
                all_repos.append(r)

    # 3. API 搜索（除非跳过）
    if not args.no_api:
        if not args.update:
            api_repos = []
            api_repos += search_github_topics()
            api_repos += search_github_code()
            if api_repos:
                all_repos += api_repos
                print(f"\n   API 搜索新增: {len(api_repos)} 个")
        else:
            print("\n   ⏭ 更新模式，跳过 API 搜索")

    # 4. 去重合并
    all_repos = merge_repos(all_repos)
    print(f"\n📊 去重后总计: {len(all_repos)} 个仓库")

    # 5. 保存缓存
    save_cache(all_repos)

    # 6. 按星标排序输出
    all_repos.sort(key=lambda x: x["stars"], reverse=True)

    if args.list_only or args.dry_run:
        print("\n📋 仓库列表:")
        for i, r in enumerate(all_repos, 1):
            star_str = f"⭐{r['stars']}" if r['stars'] else "   "
            print(f"  {i:3d}. {star_str:>8s}  {r['full_name']:<50s} {r['description'][:60]}")
        print(f"\n  总计: {len(all_repos)} 个")
        if args.list_only:
            return
        if args.dry_run:
            print("\n  (试运行模式，不实际下载)")

    if args.search:
        print("\n✅ 搜索完成，缓存已保存。")
        return

    # 7. 下载/更新
    action = "更新" if args.update else "下载"
    print(f"\n🚀 开始{action}...")
    print(f"   {'='*50}")

    stats = {"cloned": 0, "updated": 0, "skipped": 0, "failed": 0, "total": len(all_repos)}
    failed_list = []

    for i, repo in enumerate(all_repos, 1):
        name = repo["full_name"]
        status = clone_or_pull(repo, update_only=args.update, dry_run=args.dry_run)
        stats[status] = stats.get(status, 0) + 1

        if status == "cloned":
            print(f"  [{i:3d}/{stats['total']}] 🆕 {name}")
        elif status == "updated":
            print(f"  [{i:3d}/{stats['total']}] 🔄 {name}")
        elif status == "skipped":
            pass  # 静默跳过
        elif status == "failed":
            print(f"  [{i:3d}/{stats['total']}] ❌ {name}")
            failed_list.append(name)

    # 8. 总结
    print(f"\n{'='*60}")
    print(f"  完成!")
    print(f"    新增: {stats.get('cloned', 0)}")
    print(f"    更新: {stats.get('updated', 0)}")
    print(f"    跳过: {stats.get('skipped', 0)}")
    print(f"    失败: {stats.get('failed', 0)}")
    if failed_list:
        print(f"\n  失败列表 (可重试):")
        for f in failed_list:
            print(f"    - {f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()