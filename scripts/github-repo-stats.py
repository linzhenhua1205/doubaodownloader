#!/usr/bin/env python3
"""
github-repo-stats.py — GitHub 仓库统计与 PR 分类分析 v1.0

参考 Higress Daily Report 方案（higress-group/higress-report-agent）：
  - 仓库维度: star/commit/issue/PR 增量统计（周期对比）
  - PR 维度: 按类型分类（feature/bugfix/doc/refactor/test）+ 技术看点提取
Higress 原方案用 MCP(github-mcp-serve) + Qwen LLM 做 PR 分类；
本脚本提供免 LLM 的确定性统计骨架（PR 标题/标签启发式分类），
LLM 深度分类留待 agent 消费数据后执行。

用法:
  # 统计单个仓库（近 7 天）
  python3 scripts/github-repo-stats.py --repo vllm-project/vllm --days 7

  # 统计多个仓库，输出 Markdown
  python3 scripts/github-repo-stats.py --repos vllm-project/vllm,pytorch/pytorch --days 3 --format md

  # 输出 JSON 到文件（供 ai-app-insight-daily.py 消费）
  python3 scripts/github-repo-stats.py --repo openai/openai-agents-python --days 7 --out tmp/gh-stats.json

依赖: 仅 Python 标准库（urllib）。GitHub 免认证限 60 req/h。
"""

import argparse
import json
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

UA = "Mozilla/5.0 (compatible; github-stats/1.0)"
API = "https://api.github.com"
TIMEOUT = 20

# PR 类型启发式关键词（标题匹配，Higress 五分类 + security）
PR_TYPE_KEYWORDS = {
    "feature": ["feat", "feature", "add", "new", "support", "implement", "introduce", "新增", "支持", "添加"],
    "bugfix": ["fix", "bug", "hotfix", "correct", "repair", "修复", "解决", "回退", "revert"],
    "doc": ["doc", "document", "readme", "docs", "文档"],
    "refactor": ["refactor", "cleanup", "optimize", "perf", "improve", "重构", "优化", "清理"],
    "test": ["test", "benchmark", "ci", "e2e", "测试", "基准"],
    "security": ["security", "cve", "vuln", "auth", "ssl", "tls", "inject", "安全", "漏洞"],
}


def api_get(path: str, params: dict | None = None) -> dict | list:
    """GitHub API GET（免认证）。"""
    url = f"{API}{path}"
    if params:
        qs = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        url += f"?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())


def classify_pr(title: str, labels: list[str]) -> str:
    """PR 类型启发式分类（Higress 五分类 + security）。"""
    text = f"{title} {' '.join(labels)}".lower()
    for ptype, kws in PR_TYPE_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in text:
                return ptype
    return "other"


def stat_repo(repo: str, days: int) -> dict:
    """统计单个仓库。"""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {"repo": repo, "days": days, "ok": False, "error": None}

    try:
        meta = api_get(f"/repos/{repo}")
        if isinstance(meta, dict) and "stargazers_count" in meta:
            result.update({
                "stars_total": meta["stargazers_count"],
                "forks": meta["forks_count"],
                "open_issues": meta["open_issues_count"],
                "language": meta.get("language"),
                "description": (meta.get("description") or "")[:200],
                "pushed_at": meta.get("pushed_at"),
            })
        else:
            result["error"] = f"仓库不存在或限流: {repo}"
            return result

        # commits（近 days 天）
        commits = api_get(f"/repos/{repo}/commits", {"since": since, "per_page": 30})
        if isinstance(commits, list):
            result["commits_7d"] = len(commits)
            result["recent_commits"] = [
                {"msg": (c.get("commit", {}).get("message", "") or "").split("\n")[0][:120],
                 "date": c.get("commit", {}).get("committer", {}).get("date", ""),
                 "sha": c.get("sha", "")[:7]}
                for c in commits[:10]
            ]

        # releases（近 days 天）
        releases = api_get(f"/repos/{repo}/releases", {"per_page": 10})
        if isinstance(releases, list):
            result["recent_releases"] = [
                {"tag": r.get("tag_name", ""), "name": (r.get("name") or "")[:80],
                 "date": r.get("published_at", "")}
                for r in releases[:5]
            ]

        result["ok"] = True
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def stat_prs(repo: str, days: int) -> dict:
    """PR 分类统计（Higress 方案核心）。"""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {"repo": repo, "pr_count": 0, "by_type": {}, "prs": []}

    try:
        prs = api_get(f"/repos/{repo}/pulls", {"state": "all", "sort": "updated", "direction": "desc", "per_page": 50})
        if not isinstance(prs, list):
            return result

        # 过滤近 days 天更新的 PR
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        recent = []
        for p in prs:
            updated = p.get("updated_at", "")
            try:
                if datetime.fromisoformat(updated.replace("Z", "+00:00")) >= cutoff:
                    recent.append(p)
            except ValueError:
                continue

        result["pr_count"] = len(recent)
        type_counter = Counter()
        type_prs = defaultdict(list)
        for p in recent:
            labels = [l.get("name", "") for l in p.get("labels", [])]
            ptype = classify_pr(p.get("title", ""), labels)
            type_counter[ptype] += 1
            type_prs[ptype].append({
                "number": p.get("number"),
                "title": (p.get("title") or "")[:120],
                "state": p.get("state"),
                "merged": p.get("merged_at") is not None,
                "user": (p.get("user") or {}).get("login", ""),
                "labels": labels[:5],
                "url": p.get("html_url", ""),
            })

        result["by_type"] = dict(type_counter.most_common())
        result["prs"] = {k: v[:8] for k, v in type_prs.items()}
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def to_markdown(stats: list[dict], pr_stats: dict[str, dict]) -> str:
    """输出 Markdown 报告（Higress changelog 风格）。"""
    lines = ["## 📊 GitHub 仓库统计（Higress Daily Report 方案）", ""]
    for s in stats:
        if not s.get("ok"):
            lines.append(f"- **{s['repo']}**: ⚠️ {s['error']}")
            continue
        lines.append(f"### {s['repo']}")
        lines.append(f"- ⭐ {s.get('stars_total', '?')} stars · {s.get('forks', '?')} forks · {s.get('language', '')}")
        lines.append(f"- 📝 近 {s.get('days', 7)} 天 commits: {s.get('commits_7d', 0)} 条")
        for c in s.get("recent_commits", [])[:5]:
            lines.append(f"  - `{c['sha']}` {c['msg']} · {c['date'][:10]}")
        for r in s.get("recent_releases", [])[:3]:
            lines.append(f"  - 🚀 release {r['tag']} · {r['date'][:10]}")
        lines.append("")

    lines.append("### PR 分类统计（Higress 五分类）")
    for repo, prs in pr_stats.items():
        lines.append(f"- **{repo}**: {prs.get('pr_count', 0)} PRs 近 7 天")
        by_type = prs.get("by_type", {})
        if by_type:
            lines.append(f"  - 分布: {', '.join(f'{k}={v}' for k, v in by_type.items())}")
        for ptype, items in prs.get("prs", {}).items():
            for it in items[:3]:
                mark = "✅merged" if it["merged"] else ("⏳open" if it["state"] == "open" else "❌closed")
                lines.append(f"  - [{ptype}/{mark}] #{it['number']} {it['title']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="GitHub 仓库统计（Higress Daily Report 方案）")
    parser.add_argument("--repo", type=str, help="单个仓库 owner/repo")
    parser.add_argument("--repos", type=str, help="多个仓库逗号分隔")
    parser.add_argument("--days", type=int, default=7, help="统计窗口（天）")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    parser.add_argument("--out", type=str, help="输出文件")
    args = parser.parse_args()

    repos = []
    if args.repo:
        repos = [args.repo]
    elif args.repos:
        repos = [r.strip() for r in args.repos.split(",") if r.strip()]

    if not repos:
        parser.print_help()
        sys.exit(1)

    stats = [stat_repo(r, args.days) for r in repos]
    pr_stats = {}
    for r in repos:
        pr_stats[r] = stat_prs(r, args.days)
        # 节省 API 配额：每仓库 PR 统计 1 次请求

    if args.format == "md":
        output = to_markdown(stats, pr_stats)
    else:
        output = json.dumps({
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "days": args.days,
            "repos": stats,
            "pr_stats": pr_stats,
        }, ensure_ascii=False, indent=2)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ 已写入 {args.out}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
