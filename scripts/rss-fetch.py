#!/usr/bin/env python3
"""
rss-fetch.py — 通用 RSS 抓取器 v1.0

聚合抓取官方 RSS 与 RSSHub 路由，输出规范化 JSON/Markdown。
供 web-access skill 与 ai-app-insight-daily.py 复用。

数据源（SSOT，修改只改本文件 RSS_SOURCES）：
  - 官方 RSS: V2EX / HN / IT之家 / 少数派 / 阮一峰 / OpenAI / DeepMind / arXiv
  - RSSHub 路由: 知乎热榜 / 微博热搜 / B站排行榜 / GitHub Trending
  - RSSHub 多实例 fallback: rsshub.app(主) → rsshub.rssforever.com(备)

用法:
  # 列出全部可用源
  python3 scripts/rss-fetch.py --list

  # 抓取单个源（输出 JSON 到 stdout）
  python3 scripts/rss-fetch.py --fetch v2ex-hot

  # 抓取多个源（逗号分隔）
  python3 scripts/rss-fetch.py --fetch openai,deepmind,arxiv-ai

  # 抓取全部源（每源最多 N 条，默认 10）
  python3 scripts/rss-fetch.py --all --limit 8

  # 输出 Markdown（供日报/洞察直接引用）
  python3 scripts/rss-fetch.py --fetch ruanyifeng --format md

  # 保存到文件
  python3 scripts/rss-fetch.py --all --out tmp/rss-YYYY-MM-DD.json

依赖: 仅 Python 标准库 (urllib + xml.etree)
"""

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html import unescape

# ============================================================
# RSS 源注册表（SSOT）
# ============================================================
# access: static(直连) / rsshub(走 RSSHub 路由)
RSS_SOURCES = [
    # ---- 官方 RSS ----
    {"id": "v2ex-hot", "name": "V2EX 热门", "type": "tech-community",
     "access": "static", "url": "https://www.v2ex.com/feed/tab/hot.xml", "lang": "zh"},
    {"id": "hn-front", "name": "Hacker News 首页", "type": "tech-community",
     "access": "static", "url": "https://hnrss.org/frontpage", "lang": "en"},
    {"id": "ithome", "name": "IT之家", "type": "tech-news",
     "access": "rsshub", "url": "https://rsshub.app/ithome", "lang": "zh"},
    {"id": "sspai", "name": "少数派", "type": "tech-news",
     "access": "rsshub", "url": "https://rsshub.app/sspai/matrix", "lang": "zh"},
    {"id": "ruanyifeng", "name": "阮一峰博客", "type": "tech-blog",
     "access": "static", "url": "https://www.ruanyifeng.com/blog/atom.xml", "lang": "zh"},
    {"id": "openai", "name": "OpenAI 博客", "type": "ai-org",
     "access": "static", "url": "https://openai.com/blog/rss.xml", "lang": "en"},
    {"id": "deepmind", "name": "Google DeepMind 博客", "type": "ai-org",
     "access": "static", "url": "https://deepmind.google/blog/rss.xml", "lang": "en"},
    {"id": "arxiv-ai", "name": "arXiv cs.AI 论文", "type": "ai-paper",
     "access": "static", "url": "https://rss.arxiv.org/rss/cs.AI", "lang": "en"},
    {"id": "arxiv-ml", "name": "arXiv cs.LG 论文", "type": "ai-paper",
     "access": "static", "url": "https://rss.arxiv.org/rss/cs.LG", "lang": "en"},

    # ---- RSSHub 路由 ----
    {"id": "zhihu-hot", "name": "知乎热榜", "type": "hot-topic",
     "access": "rsshub", "url": "https://rsshub.app/zhihu/hot", "lang": "zh"},
    {"id": "weibo-hot", "name": "微博热搜", "type": "hot-topic",
     "access": "rsshub", "url": "https://rsshub.app/weibo/search/hot", "lang": "zh"},
    {"id": "bilibili-rank", "name": "B站排行榜", "type": "hot-topic",
     "access": "rsshub", "url": "https://rsshub.app/bilibili/ranking/0/3/1", "lang": "zh"},
    {"id": "github-trending", "name": "GitHub Trending 日榜", "type": "github-trend",
     "access": "rsshub", "url": "https://rsshub.app/github/trending/daily", "lang": "en"},
]

# RSSHub 多实例 fallback（rsshub.app 主实例可能不可达）
RSSHUB_FALLBACKS = [
    "https://rsshub.rssforever.com",
    "https://rsshub.app",
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
TIMEOUT = 12
MAX_ITEMS = 10


def fetch_url(url: str) -> bytes:
    """抓取 URL，带 UA 与超时。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def resolve_rsshub_url(url: str) -> str:
    """RSSHub 路由多实例 fallback：返回第一个可用的实例 URL。
    用 GET 试探（HEAD 部分 RSSHub 实例不支持/慢），成功即返回。"""
    if not url.startswith("https://rsshub.app"):
        return url
    path = url[len("https://rsshub.app"):]
    for base in RSSHUB_FALLBACKS:
        candidate = base + path
        try:
            req = urllib.request.Request(candidate, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status < 400:
                    return candidate
        except Exception:
            continue
    return url  # 全部失败则回退主实例（由主流程报错）


def parse_rss(data: bytes) -> list[dict]:
    """解析 RSS/Atom XML，提取条目列表。兼容 RSS 2.0 与 Atom（含 namespace）。"""
    items = []
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return items

    def _local(tag: str) -> str:
        """去除 XML namespace 前缀，返回本地标签名。"""
        return tag.rsplit("}", 1)[-1]

    # 统一查找条目节点：RSS <item> / Atom <entry>（兼容带 namespace 的 Atom）
    entries = [el for el in root.iter() if _local(el.tag) in ("item", "entry")]

    for e in entries:
        children = {_local(c.tag): c for c in e}

        def _text(tag: str) -> str:
            el = children.get(tag)
            return unescape(el.text or "").strip() if el is not None and el.text else ""

        # Atom 用 <link href="">，RSS 用 <link>text</link>
        link = ""
        link_el = children.get("link")
        if link_el is not None:
            link = link_el.get("href", "") or (link_el.text or "").strip()

        title = _text("title")
        desc = _text("description") or _text("summary")
        pub = _text("pubDate") or _text("published") or _text("updated")

        # 清理 description 中的 HTML 标签
        desc_clean = re.sub(r"<[^>]+>", " ", desc)
        desc_clean = re.sub(r"\s+", " ", desc_clean).strip()[:500]

        if title:
            items.append({
                "title": title,
                "link": link,
                "description": desc_clean,
                "pub_date": pub,
            })
    return items[:MAX_ITEMS]


def fetch_source(src: dict, limit: int = MAX_ITEMS) -> dict:
    """抓取单个源。返回 {id, name, url, reachable, items}。
    RSSHub 源按 fallback 实例顺序尝试，首个成功即用（数据直接复用，不重复下载）。"""
    global MAX_ITEMS
    MAX_ITEMS = limit
    result = {
        "id": src["id"],
        "name": src["name"],
        "type": src["type"],
        "lang": src["lang"],
        "url": src["url"],
        "reachable": False,
        "items": [],
        "error": None,
    }
    urls = []
    if src["access"] == "rsshub":
        path = src["url"][len("https://rsshub.app"):]
        urls = [base + path for base in RSSHUB_FALLBACKS] + [src["url"]]
    else:
        urls = [src["url"]]

    last_err = None
    for url in urls:
        try:
            data = fetch_url(url)
            items = parse_rss(data)
            if items or url == urls[-1]:
                result["url"] = url
                result["items"] = items
                result["reachable"] = True
                return result
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
    result["error"] = last_err
    return result


def to_markdown(results: list[dict], limit: int = 8) -> str:
    """将抓取结果转为 Markdown 摘要（供日报/洞察引用）。"""
    lines = []
    for r in results:
        lines.append(f"\n### {r['name']} ({r['id']})")
        if not r["reachable"]:
            lines.append(f"- ⚠️ 不可达: {r['error']}")
            continue
        if not r["items"]:
            lines.append("- （无条目）")
            continue
        for it in r["items"][:limit]:
            date = it["pub_date"][:16] if it["pub_date"] else ""
            lines.append(f"- **{it['title']}** · {date}")
            if it["link"]:
                lines.append(f"  {it['link']}")
            if it["description"]:
                desc = it["description"][:120]
                lines.append(f"  {desc}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="通用 RSS 抓取器")
    parser.add_argument("--list", action="store_true", help="列出全部源")
    parser.add_argument("--fetch", type=str, help="抓取指定源（逗号分隔 id，或 all）")
    parser.add_argument("--all", action="store_true", help="抓取全部源")
    parser.add_argument("--limit", type=int, default=10, help="每源最多条目数")
    parser.add_argument("--format", choices=["json", "md"], default="json", help="输出格式")
    parser.add_argument("--out", type=str, help="输出文件路径（默认 stdout）")
    args = parser.parse_args()

    if args.list:
        print(f"{'id':<20} {'name':<24} {'type':<18} {'access':<10} {'lang':<5} url")
        for s in RSS_SOURCES:
            print(f"{s['id']:<20} {s['name']:<24} {s['type']:<18} {s['access']:<10} {s['lang']:<5} {s['url']}")
        return

    # 确定要抓取的源
    if args.all or args.fetch == "all":
        targets = RSS_SOURCES
    elif args.fetch:
        ids = [x.strip() for x in args.fetch.split(",")]
        by_id = {s["id"]: s for s in RSS_SOURCES}
        targets = [by_id[i] for i in ids if i in by_id]
        missing = [i for i in ids if i not in by_id]
        if missing:
            print(f"⚠️ 未知源: {missing}", file=sys.stderr)
    else:
        parser.print_help()
        sys.exit(1)

    if not targets:
        print("没有匹配的源", file=sys.stderr)
        sys.exit(1)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda s: fetch_source(s, args.limit), targets))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if args.format == "md":
        output = f"# RSS 聚合快照（{now}）\n\n> 抓取 {len(results)} 源，成功 {sum(1 for r in results if r['reachable'])} 个\n" + to_markdown(results)
    else:
        output = json.dumps({
            "generated_at": now,
            "source_count": len(results),
            "reachable_count": sum(1 for r in results if r["reachable"]),
            "sources": results,
        }, ensure_ascii=False, indent=2)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ 已写入 {args.out}（{len(output)} 字符）", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
