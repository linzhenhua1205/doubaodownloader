#!/usr/bin/env python3
"""
ai-app-insight-daily.py — AI 应用定时洞察数据采集器 v1.0

参考 CloudFlare-AI-Insight-Daily 方案（多数据源聚合 + 智能摘要）：
  CloudFlare 原方案: Cloudflare Workers 定时 → 多源抓取(github-trending/
  arxiv/新闻) → Gemini 批量摘要/翻译 → mdbook 生成 → GitHub Pages 发布。
  本脚本落地到本地: 定时采集 RSS + GitHub 统计 + weekly 周刊 → 生成
  洞察素材包（JSON/Markdown），供 AI 精炼为 knowledge/01_survey/ai-apps/ 日报。

数据源三通道:
  1. RSS 源（rss-fetch.py 复用）: OpenAI/DeepMind/arXiv/阮一峰/V2EX/HN/
     RSSHub(知乎热榜/微博/B站/GitHub Trending)
  2. GitHub 统计（github-repo-stats.py，Higress Daily Report 方案）:
     重点仓库 star/commit/release + PR 类型分类
  3. weekly 周刊（import/weekly/）: OpenGithubs 精选开源项目周刊，周更

用法:
  # 采集全部（RSS + GitHub + weekly），输出素材包
  python3 scripts/ai-app-insight-daily.py collect --all

  # 仅 RSS（快）
  python3 scripts/ai-app-insight-daily.py collect --rss-only --rss-limit 6

  # 指定 GitHub 仓库
  python3 scripts/ai-app-insight-daily.py collect --github-repos vllm-project/vllm,openai/openai-agents-python

  # 生成 Markdown 素材（供 AI 精炼日报）
  python3 scripts/ai-app-insight-daily.py collect --all --format md

  # 查看 weekly 最新周刊
  python3 scripts/ai-app-insight-daily.py weekly --latest

输出: tmp/ai-insight-YYYY-MM-DD/（素材包目录）
      └── 00-metadata.json / 01-rss.json / 02-github-stats.json / 03-weekly.md / 04-brief.md

依赖: scripts/rss-fetch.py, scripts/github-repo-stats.py（同目录）
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "cow"
SCRIPTS = WORKSPACE / "scripts"
IMPORT = WORKSPACE / "import"
TMP = WORKSPACE / "tmp"

# AI 应用追踪重点仓库（与 knowledge/01_survey/ai-apps/TRACKING.md 对齐）
DEFAULT_REPOS = [
    "openai/openai-agents-python",
    "langchain-ai/langgraph",
    "langchain-ai/langchain",
    "microsoft/autogen",
    "crewAIInc/crewAI",
    "vllm-project/vllm",
    "pytorch/pytorch",
]

# weekly 周刊目录（周更，取最新文件）
WEEKLY_DIR = IMPORT / "weekly"


def run_script(script: str, *args: str) -> str:
    """运行同目录脚本，返回 stdout。"""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{script} 失败: {result.stderr[:500]}")
    return result.stdout


def collect_rss(limit: int) -> list[dict]:
    """通道 1: RSS 聚合。"""
    out = run_script("rss-fetch.py", "--all", "--limit", str(limit))
    try:
        return json.loads(out).get("sources", [])
    except json.JSONDecodeError:
        print("⚠️ RSS 输出解析失败", file=sys.stderr)
        return []


def collect_github(repos: list[str], days: int) -> dict:
    """通道 2: GitHub 统计（Higress 方案）。"""
    if not repos:
        return {}
    out = run_script("github-repo-stats.py", "--repos", ",".join(repos), "--days", str(days))
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        print("⚠️ GitHub 输出解析失败", file=sys.stderr)
        return {}


def collect_weekly() -> dict:
    """通道 3: weekly 周刊最新一期。"""
    if not WEEKLY_DIR.exists():
        return {"error": "import/weekly/ 不存在"}
    files = sorted(WEEKLY_DIR.glob("*/*.md"))
    # 2024/2025 年文件命名不同，按修改时间取最新
    files = [f for f in files if f.name != "Readme.md"]
    if not files:
        return {"error": "weekly 无期刊文件"}
    latest = max(files, key=lambda f: f.stat().st_mtime)
    content = latest.read_text(encoding="utf-8", errors="ignore")[:6000]
    return {
        "file": str(latest.relative_to(WORKSPACE)),
        "name": latest.stem,
        "mtime": datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        "preview": content[:2000],
    }


def gen_brief(rss_sources: list[dict], gh_stats: dict, weekly: dict, rss_limit: int) -> str:
    """生成 Markdown 速览（供 AI 精炼日报的直接输入）。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# AI 应用洞察素材包（{now}）",
        "",
        "> 本文件由 scripts/ai-app-insight-daily.py 自动采集，供 AI 精炼为 ai-apps 日报。",
        "> 数据为原始素材，需经交叉验证/去重/AI 摘要后写入 knowledge/01_survey/ai-apps/YYYY-MM-DD.md",
        "",
        "## 一、RSS 聚合",
        "",
    ]
    ok = [s for s in rss_sources if s.get("reachable")]
    fail = [s for s in rss_sources if not s.get("reachable")]
    lines.append(f"源总数 {len(rss_sources)}，成功 {len(ok)}，失败 {len(fail)}")
    if fail:
        lines.append(f"⚠️ 不可达: {', '.join(s['id'] for s in fail)}")
    lines.append("")
    for s in ok:
        lines.append(f"### {s['name']}")
        for it in s.get("items", [])[:rss_limit]:
            date = (it.get("pub_date") or "")[:16]
            lines.append(f"- **{it['title']}** · {date}")
            if it.get("description"):
                lines.append(f"  {it['description'][:150]}")
            if it.get("link"):
                lines.append(f"  {it['link']}")
        lines.append("")

    lines.append("## 二、GitHub 统计（Higress Daily Report 方案）")
    lines.append("")
    repos = gh_stats.get("repos", [])
    prs = gh_stats.get("pr_stats", {})
    for r in repos:
        if not r.get("ok"):
            lines.append(f"- **{r['repo']}**: ⚠️ {r.get('error')}")
            continue
        lines.append(f"### {r['repo']}")
        lines.append(f"- ⭐ {r.get('stars_total', '?')} · 📝 commits近7天 {r.get('commits_7d', 0)}")
        for c in r.get("recent_commits", [])[:4]:
            lines.append(f"  - `{c['sha']}` {c['msg']} · {c['date'][:10]}")
        for rel in r.get("recent_releases", [])[:2]:
            lines.append(f"  - 🚀 {rel['tag']} · {rel['date'][:10]}")
        pr = prs.get(r["repo"], {})
        if pr.get("by_type"):
            lines.append(f"  - PR 分类(近7天): {', '.join(f'{k}={v}' for k, v in pr['by_type'].items())}")
        lines.append("")

    lines.append("## 三、weekly 周刊最新")
    lines.append("")
    if weekly.get("error"):
        lines.append(f"- ⚠️ {weekly['error']}")
    else:
        lines.append(f"- **{weekly['name']}** · {weekly.get('mtime', '')} · {weekly['file']}")
        lines.append("")
        lines.append("```markdown")
        lines.append(weekly.get("preview", ""))
        lines.append("```")

    lines.append("")
    lines.append("---")
    lines.append("**统计**: RSS {len(ok)}/{len(rss_sources)} 源 · GitHub {len(repos)} 仓库 · weekly {'有' if not weekly.get('error') else '无'}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AI 应用定时洞察数据采集器")
    sub = parser.add_subparsers(dest="cmd")

    collect = sub.add_parser("collect", help="采集洞察素材")
    collect.add_argument("--all", action="store_true", help="采集全部通道")
    collect.add_argument("--rss-only", action="store_true", help="仅 RSS")
    collect.add_argument("--rss-limit", type=int, default=6, help="每 RSS 源条目数")
    collect.add_argument("--github-repos", type=str, default="", help="GitHub 仓库列表(逗号分隔)")
    collect.add_argument("--github-days", type=int, default=7)
    collect.add_argument("--no-github", action="store_true", help="跳过 GitHub 通道")
    collect.add_argument("--no-weekly", action="store_true", help="跳过 weekly 通道")
    collect.add_argument("--format", choices=["json", "md"], default="json")

    weekly = sub.add_parser("weekly", help="查看 weekly 周刊")
    weekly.add_argument("--latest", action="store_true", help="最新一期")

    args = parser.parse_args()
    if args.cmd == "weekly":
        w = collect_weekly()
        if w.get("error"):
            print(f"⚠️ {w['error']}")
        else:
            print(f"最新周刊: {w['name']} ({w['mtime']})")
            print(f"路径: {w['file']}")
            print(f"\n--- 预览 ---\n{w['preview'][:1500]}")
        return

    if args.cmd != "collect":
        parser.print_help()
        sys.exit(1)

    # 默认全部通道
    do_rss = args.all or args.rss_only or not (args.no_github and args.no_weekly)
    do_gh = args.all or (not args.no_github and not args.rss_only)
    do_wk = args.all or not args.no_weekly

    repos = [r.strip() for r in args.github_repos.split(",") if r.strip()] if args.github_repos else DEFAULT_REPOS

    rss_sources = collect_rss(args.rss_limit) if do_rss else []
    gh_stats = collect_github(repos, args.github_days) if do_gh else {}
    weekly_data = collect_weekly() if do_wk else {}

    now = datetime.now()
    out_dir = TMP / f"ai-insight-{now.strftime('%Y-%m-%d')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    brief = gen_brief(rss_sources, gh_stats, weekly_data, args.rss_limit)

    if args.format == "md":
        output = brief
    else:
        output = json.dumps({
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "rss_sources": rss_sources,
            "github_stats": gh_stats,
            "weekly": weekly_data,
            "brief_md": brief,
        }, ensure_ascii=False, indent=2)

    # 落盘素材包
    suffix = ".md" if args.format == "md" else ".json"
    out_file = out_dir / f"insight-brief{suffix}"
    out_file.write_text(output, encoding="utf-8")
    print(f"✅ 素材包已生成: {out_file.relative_to(WORKSPACE)}")
    print(f"   RSS: {len(rss_sources)} 源 · GitHub: {len(gh_stats.get('repos', []))} 仓库 · weekly: {'有' if weekly_data else '无'}")
    if args.format == "md":
        print(output[:3000])


if __name__ == "__main__":
    main()
