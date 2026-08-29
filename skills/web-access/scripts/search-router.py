#!/usr/bin/env python3
"""
search-router.py — 统一搜索路由 CLI（web-access 搜索层 SSOT）

三级搜索策略（2026-08-12 定型）:
  L1 专业网站站内搜索（优先）: 从 source-registry.json 匹配专业源，站内搜索直达
  L2 通用搜索引擎:           www.bing.com（国际）/ 中文查询自动附加参数
  L3 搜狗系兜底:             weixin.sogou.com（微信文章）→ zhihu.sogou.com（知乎）→ www.sogou.com（通用中文）

设计原则:
  - 专业站优先: 一手来源 > 聚合（MEMORY 网络应对链: 直连 > 搜索）
  - 配置下沉: 数据源注册表/网站信息全部在 skills/web-access/scripts/config/ 维护
  - 零浏览器: Playwright 全链路禁用（2026-08-12），仅 requests + bs4
  - Fail-Fast: 每个源最多 1 次请求，失败立即降级下一级，不重试不换词
  - 结构化输出: --json 统一契约（title/url/snippet/source/grade），供下游直接消费

用法:
  # 自动路由（专业站→Bing→搜狗）
  python3 search-router.py "NVIDIA GB300" 
  python3 search-router.py "HBM4 三星" --json
  python3 search-router.py "UALink 规范" --limit 8 --timeout 12

  # 指定源
  python3 search-router.py "server power" --source servethehome
  python3 search-router.py "AI chip" --source bing
  python3 search-router.py "微信文章关键词" --source sogou-weixin
  python3 search-router.py "知乎问题" --source sogou-zhihu

  # 列出可用源 / 检查源可达性
  python3 search-router.py --sources
  python3 search-router.py --check

依赖: requests, beautifulsoup4（.venv-web/bin/python 或系统 python3）
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus, urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ 依赖缺失: pip install requests beautifulsoup4 lxml")
    sys.exit(1)

# ── 路径 ──
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR / "config"
REGISTRY_FILE = CONFIG_DIR / "source-registry.json"

# 兼容: config 目录可能未创建
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# 默认 UA（专业站/Bing 均可用的通用浏览器 UA）
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


# ══════════════════════════════════════════════════════════════
# 源注册表（SSOT — 实际数据在 config/source-registry.json）
# ══════════════════════════════════════════════════════════════

def _default_registry() -> dict:
    """默认注册表（首次运行时生成，之后以 config 文件为准）"""
    return {
        "version": 1,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "policy": {
            "strategy": "L1 专业站站内搜索 → L2 Bing → L3 搜狗系兜底",
            "professional_first": True,
            "fail_fast": True,
            "max_sources_per_query": 3,
        },
        "professional_sites": [
            {
                "id": "servethehome", "name": "ServeTheHome", "grade": "A",
                "type": "hardware", "lang": "en",
                "search_url": "https://www.servethehome.com/?s={query}",
                "notes": "服务器硬件一手评测，电源/散热/架构实测",
            },
            {
                "id": "techcrunch", "name": "TechCrunch", "grade": "A",
                "type": "tech-news", "lang": "en",
                "search_url": "https://techcrunch.com/search/{query}",
                "notes": "AI编程工具/创业/AI Agent/开源动态",
            },
            {
                "id": "the-next-platform", "name": "The Next Platform", "grade": "B",
                "type": "deep-analysis", "lang": "en",
                "search_url": "https://www.nextplatform.com/?s={query}",
                "notes": "服务器/AI芯片深度分析",
            },
            {
                "id": "semiengineering", "name": "SemiEngineering", "grade": "B",
                "type": "industry", "lang": "en",
                "search_url": "https://semiengineering.com/?s={query}",
                "notes": "半导体/封装/EDA深度分析",
            },
            {
                "id": "hpcwire", "name": "HPCwire", "grade": "B",
                "type": "industry", "lang": "en",
                "search_url": "https://www.hpcwire.com/?s={query}",
                "notes": "高性能计算/AI集群/互联技术",
            },
            {
                "id": "tomshardware", "name": "Tom's Hardware", "grade": "B",
                "type": "hardware", "lang": "en",
                "search_url": "https://www.tomshardware.com/search?searchTerm={query}",
                "notes": "消费级/服务器硬件评测，GPU/CPU/SSD",
            },
            {
                "id": "ieee-spectrum", "name": "IEEE Spectrum", "grade": "B",
                "type": "academic", "lang": "en",
                "search_url": "https://spectrum.ieee.org/search?q={query}",
                "notes": "人工智能/芯片架构深度文章",
            },
            {
                "id": "theregister", "name": "The Register", "grade": "B",
                "type": "tech-news", "lang": "en",
                "search_url": "https://www.theregister.com/search/?q={query}",
                "notes": "IT企业级新闻",
            },
            {
                "id": "arxiv", "name": "arXiv", "grade": "A",
                "type": "academic", "lang": "en",
                "search_url": "https://arxiv.org/search/?query={query}&searchtype=all&start=0",
                "notes": "学术前沿，稳定可用",
            },
            {
                "id": "laoyaoba", "name": "老Yaob", "grade": "B",
                "type": "chinese-industry", "lang": "zh",
                "search_url": "https://www.laoyaoba.com/search?q={query}",
                "notes": "半导体/消费电子中文产业新闻",
            },
        ],
        "search_engines": {
            "bing": {
                "name": "Bing", "grade": "B",
                "search_url": "https://www.bing.com/search?q={query}&count={limit}",
                "notes": "国际通用；中文查询可用，Bing 国内版 RSS 更稳（format=rss）",
            },
            "sogou-weixin": {
                "name": "搜狗微信", "grade": "C",
                "search_url": "https://weixin.sogou.com/weixin?type=2&query={query}",
                "notes": "微信文章检索；验证码频繁，fail-fast 后跳下一级",
            },
            "sogou-zhihu": {
                "name": "搜狗知乎", "grade": "C",
                "search_url": "https://zhihu.sogou.com/zhihu?query={query}",
                "notes": "知乎内容检索",
            },
            "sogou-general": {
                "name": "搜狗通用", "grade": "C",
                "search_url": "https://www.sogou.com/web?query={query}",
                "notes": "中文通用兜底",
            },
        },
        "routing": {
            "default_chain": ["auto", "bing", "sogou-weixin", "sogou-zhihu", "sogou-general"],
            "zh_chain": ["auto", "bing", "sogou-weixin", "sogou-general"],
            "en_chain": ["auto", "bing", "sogou-general"],
        },
    }


def load_registry() -> dict:
    """加载源注册表；文件不存在则生成默认并落盘"""
    if not REGISTRY_FILE.exists():
        reg = _default_registry()
        REGISTRY_FILE.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[i] 已生成默认注册表: {REGISTRY_FILE}", file=sys.stderr)
        return reg
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"❌ 注册表损坏: {REGISTRY_FILE}", file=sys.stderr)
        sys.exit(1)


def save_registry(reg: dict):
    REGISTRY_FILE.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")


# ══════════════════════════════════════════════════════════════
# 抓取与解析
# ══════════════════════════════════════════════════════════════

def fetch(url: str, timeout: int = 10, referer: str = "") -> str | None:
    """GET 请求，超时/异常返回 None（Fail-Fast）"""
    import socket
    socket.setdefaulttimeout(timeout)  # 兜底: 覆盖 DNS/connect/TLS 全阶段
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "identity",
    }
    if referer:
        headers["Referer"] = referer
    try:
        resp = requests.get(url, headers=headers, timeout=(timeout, timeout))
        if resp.status_code != 200:
            return None
        # 只保留 HTML 主体（防超长页面耗尽内存）
        if len(resp.content) > 3_000_000:
            return resp.text[:3_000_000]
        return resp.text
    except Exception:
        return None


def parse_links(html: str, base_url: str, limit: int = 8) -> list[dict]:
    """从搜索结果 HTML 提取 (title, url, snippet)。按结果容器通用启发式解析。

    兼容:
      - 专业站站内搜索（WordPress ?s= / 自研 search）：<article>/<h2>/<a>
      - Bing 结果页：<li class="b_algo"> 或 <h2><a>
      - 搜狗结果页：<div class="vrwrap"> 或 <h3><a>
    提取不到时回退: 所有 <h2>/<h3> 下的链接
    """
    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()

    # 候选容器选择器（按优先级）
    containers = (
        soup.select("li.b_algo, li.b_ans, .b_algo"),       # Bing
        soup.select(".vrwrap, .results .vrwrap"),           # Sogou
        soup.select("article, .post, .search-result"),      # WordPress/通用
        soup.select("h2 a, h3 a"),                          # 通用回退
        soup.select("a[title]"),                            # 图片链接模式兜底（title 属性承载标题）
    )

    for group in containers:
        for el in group:
            # 第4组 h2 a/h3 a 返回的本身就是 a 元素；其余组是容器需 find
            a = el if el.name == "a" else el.find("a", href=True)
            if not a:
                continue
            url = a["href"]
            # 相对路径 → 绝对 URL（很多站用相对链接，如 HotHardware /news/...）
            if not url.startswith(("http://", "https://")):
                url = urljoin(base_url, url)
            # 标题：优先 a 文本，空则用 title 属性（图片链接模式，如 HotHardware）
            title = a.get_text(strip=True) or a.get("title", "").strip()
            if not title or not url.startswith(("http://", "https://")):
                continue
            if url in seen:
                continue
            # 摘要（Bing 的 p 或容器的文本）
            snippet = ""
            p = el.find("p")
            if p:
                snippet = p.get_text(" ", strip=True)[:300]
            elif el.name in ("article", "div"):
                snippet = el.get_text(" ", strip=True)[:200]
            results.append({
                "title": title[:200],
                "url": url,
                "snippet": snippet,
                "source": _guess_source(base_url),
            })
            seen.add(url)
            if len(results) >= limit:
                return results
    return results


def _guess_source(url: str) -> str:
    """从 URL 猜来源名（简化，供输出标注）"""
    m = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else url


# ══════════════════════════════════════════════════════════════
# 各级搜索
# ══════════════════════════════════════════════════════════════

def search_professional(query: str, reg: dict, limit: int, timeout: int) -> list[dict]:
    """L1 专业站站内搜索 — 按优先级最多尝试 max_sources_per_query 个源"""
    sites = reg.get("professional_sites", [])
    max_try = reg.get("policy", {}).get("max_sources_per_query", 3)
    # 中文查询优先中文站
    is_zh = bool(re.search(r"[\u4e00-\u9fff]", query))
    ordered = sorted(sites, key=lambda s: 0 if (s.get("lang") == "zh") == is_zh else 1)
    # 每源预算：timeout 扣 2s 留余量，最短 4s
    per_src_timeout = max(4, timeout - 2)
    tried = 0
    for site in ordered:
        if site.get("reachable") is False:
            continue  # 注册表标记不可达（requests 路径），自动跳过
        if tried >= max_try:
            break
        tried += 1
        tmpl = site.get("search_url", "")
        if not tmpl:
            continue
        url = tmpl.replace("{query}", quote_plus(query))
        html = fetch(url, timeout=per_src_timeout)
        if not html:
            continue
        results = parse_links(html, url, limit)
        if results:
            for r in results:
                r["source"] = site["id"]
                r["grade"] = site.get("grade", "")
            print(f"[L1] ✓ {site['name']} 命中 {len(results)} 条", file=sys.stderr)
            return results
        print(f"[L1] ✗ {site['name']} 无结果", file=sys.stderr)
    return []


def search_bing(query: str, limit: int, timeout: int) -> list[dict]:
    """L2 Bing 搜索"""
    url = f"https://www.bing.com/search?q={quote_plus(query)}&count={limit}"
    html = fetch(url, timeout=timeout)
    if not html:
        print("[L2] ✗ Bing 不可达", file=sys.stderr)
        return []
    results = parse_links(html, url, limit)
    for r in results:
        r["grade"] = "B"
    if results:
        print(f"[L2] ✓ Bing 命中 {len(results)} 条", file=sys.stderr)
    return results


def search_sogou(kind: str, query: str, reg: dict, limit: int, timeout: int) -> list[dict]:
    """L3 搜狗系（weixin/zhihu/general）"""
    engines = reg.get("search_engines", {})
    key = f"sogou-{kind}"
    cfg = engines.get(key)
    if not cfg:
        return []
    url = cfg["search_url"].replace("{query}", quote_plus(query))
    referer = url.split("/weixin")[0] if kind == "weixin" else ""
    html = fetch(url, timeout=timeout, referer=referer)
    if not html:
        print(f"[L3] ✗ {cfg['name']} 不可达", file=sys.stderr)
        return []
    results = parse_links(html, url, limit)
    for r in results:
        r["source"] = key
        r["grade"] = cfg.get("grade", "C")
    if results:
        print(f"[L3] ✓ {cfg['name']} 命中 {len(results)} 条", file=sys.stderr)
    else:
        print(f"[L3] ✗ {cfg['name']} 无结果", file=sys.stderr)
    return results


# ══════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════

def cmd_sources(reg: dict):
    """列出可用源"""
    print("── 专业站（L1 优先）──")
    for s in reg.get("professional_sites", []):
        mark = "" if s.get("reachable", True) else " ⚠️不可达"
        print(f"  [{s.get('grade','?')}] {s['id']:<22} {s['name']} ({s.get('lang','')}){mark}")
    print("── 内容源（feed/文档/政策，直连抓取）──")
    for s in reg.get("content_sources", []):
        mark = "" if s.get("reachable", True) else " ⚠️不可达"
        print(f"  [{s.get('grade','?')}] {s['id']:<22} {s['name']} ({s.get('lang','')}) [{s.get('access','')}]{mark}")
    print("── 搜索引擎（L2/L3）──")
    for k, v in reg.get("search_engines", {}).items():
        print(f"  [{v.get('grade','?')}] {k:<16} {v['name']}")
    print(f"\n策略: {reg.get('policy', {}).get('strategy', '')}")


def cmd_check(reg: dict, timeout: int):
    """源可达性检查（HEAD/GET 首页）"""
    print(f"可达性检查 (timeout={timeout}s) @ {datetime.now():%H:%M:%S}")
    sites = reg.get("professional_sites", [])
    engines = reg.get("search_engines", {})
    contents = reg.get("content_sources", [])
    all_src = [(s["id"], s.get("search_url", "").split("{query}")[0]) for s in sites] + \
              [(k, v["search_url"].split("{query}")[0]) for k, v in engines.items()] + \
              [(s["id"], s.get("url", "")) for s in contents]
    for sid, base in all_src:
        if not base:
            continue
        html = fetch(base, timeout=timeout)
        status = "✅" if html else "❌"
        print(f"  {status} {sid:<18} {base[:60]}")


def _extract_headlines(html: str, base_url: str, limit: int = 15) -> list[dict]:
    """SSR 标题兜底：提取 h2/h3 标题文本（无链接或链接 JS 渲染场景，如 maomu）

    返回 [{title, url(base_url), snippet, source}]，URL 指向源站首页，标题列表供 AI 摘要使用
    """
    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()
    for h in soup.select("h2, h3"):
        t = h.get_text(strip=True)
        if not t or len(t) < 4 or t in seen:
            continue
        seen.add(t)
        results.append({
            "title": t[:200],
            "url": base_url,
            "snippet": "",
            "source": _guess_source(base_url),
        })
        if len(results) >= limit:
            break
    return results


def fetch_content(content: dict, timeout: int = 10) -> list[dict]:
    """抓取内容源页面（按 access 类型分发）

    access: static → requests 直接抓(链接级); js → SSR 标题兜底 + 提示 browser;
            web_fetch_only → 提示用 web_fetch 工具
    返回 [{title, url, snippet}]
    """
    access = content.get("access", "static")
    url = content.get("url", "")
    if not url:
        return []
    html = fetch(url, timeout=timeout)
    if not html:
        print(f"[CONTENT] ✗ {content['name']} 不可达", file=sys.stderr)
        return []
    if access == "static":
        results = parse_links(html, url, limit=15)
        if results:
            for r in results:
                r["source"] = content["id"]
                r["grade"] = content.get("grade", "")
            print(f"[CONTENT] ✓ {content['name']} 抓取 {len(results)} 条链接", file=sys.stderr)
            return results
        print(f"[CONTENT] ⚠️ {content['name']} 无链接结构，回退标题摘要", file=sys.stderr)
    elif access == "js":
        print(f"[CONTENT] ⚠️ {content['name']} 为 JS 渲染站点，链接需 browser 工具；先输出 SSR 标题摘要", file=sys.stderr)
    elif access == "web_fetch_only":
        print(f"[CONTENT] ⚠️ {content['name']} 拦截 CLI 请求（curl/requests 403），请用 web_fetch 工具访问 {url}", file=sys.stderr)
        return []
    # 标题兜底（static 无链接 / js 型）
    results = _extract_headlines(html, url, limit=15)
    for r in results:
        r["source"] = content["id"]
        r["grade"] = content.get("grade", "")
    if results:
        print(f"[CONTENT] ✓ {content['name']} 标题摘要 {len(results)} 条（链接需浏览器渲染）", file=sys.stderr)
    return results


def main():
    parser = argparse.ArgumentParser(description="统一搜索路由（web-access）")
    parser.add_argument("query", nargs="?", help="搜索关键词")
    parser.add_argument("--source", "-s", default="auto",
                        help="指定源: auto|专业站id|bing|sogou-weixin|sogou-zhihu|sogou-general")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--limit", type=int, default=8, help="每源最多结果数")
    parser.add_argument("--timeout", type=int, default=10, help="请求超时秒数")
    parser.add_argument("--sources", action="store_true", help="列出可用源")
    parser.add_argument("--check", action="store_true", help="源可达性检查")
    parser.add_argument("--content", action="store_true", help="列出内容源（feed/文档/政策）")
    parser.add_argument("--fetch-content", metavar="ID", help="抓取内容源页面（如 ai-bot / maomu / cloud-tencent）")
    args = parser.parse_args()

    reg = load_registry()

    if args.sources:
        cmd_sources(reg)
        return
    if args.check:
        cmd_check(reg, args.timeout)
        return
    if args.content:
        cmd_sources(reg)
        return
    if args.fetch_content:
        for s in reg.get("content_sources", []):
            if s["id"] == args.fetch_content:
                results = fetch_content(s, args.timeout)
                if args.json:
                    print(json.dumps({"source": s["id"], "total": len(results), "results": results},
                                     ensure_ascii=False, indent=2))
                else:
                    print(f"\n📄 {s['name']} | 链接: {len(results)} 条\n")
                    for i, r in enumerate(results[:15], 1):
                        print(f"{i}. {r['title']}")
                        print(f"   {r['url']}")
                return
        print(f"❌ 未知内容源: {args.fetch_content}（--content 查看列表）")
        sys.exit(1)
    if not args.query:
        parser.print_help()
        return

    # 路由
    results = []
    if args.source != "auto":
        # 指定源
        if args.source in ("bing",):
            results = search_bing(args.query, args.limit, args.timeout)
        elif args.source.startswith("sogou-"):
            results = search_sogou(args.source.replace("sogou-", ""), args.query, reg, args.limit, args.timeout)
        else:
            # 专业站 id
            for s in reg.get("professional_sites", []):
                if s["id"] == args.source:
                    results = search_professional_site(s, args.query, args.limit, args.timeout)
                    break
            else:
                print(f"❌ 未知源: {args.source}（--sources 查看列表）")
                sys.exit(1)
    else:
        # 自动路由: L1 → L2 → L3（带总预算: L1 用 2/5 预算, L2/L3 各 1/5）
        budget = max(8, args.timeout * 3)
        t_start = time.time()
        l1_timeout = max(4, int(budget * 0.4))
        results = search_professional(args.query, reg, args.limit, l1_timeout)
        if not results and time.time() - t_start < budget - 2:
            l2_timeout = max(4, int(budget * 0.2))
            results = search_bing(args.query, args.limit, l2_timeout)
        if not results and time.time() - t_start < budget - 1:
            is_zh = bool(re.search(r"[\u4e00-\u9fff]", args.query))
            chain = ["weixin", "zhihu", "general"] if is_zh else ["general"]
            for kind in chain:
                l3_timeout = max(3, int(budget * 0.15))
                results = search_sogou(kind, args.query, reg, args.limit, l3_timeout)
                if results:
                    break

    # 输出
    if args.json:
        print(json.dumps({"query": args.query, "total": len(results), "results": results},
                         ensure_ascii=False, indent=2))
    else:
        print(f"\n🔍 查询: {args.query} | 结果: {len(results)} 条\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']}")
            print(f"   {r['url']}")
            if r.get("snippet"):
                print(f"   {r['snippet'][:120]}")
            print(f"   [源: {r.get('source','?')} | 级: {r.get('grade','?')}]\n")


def search_professional_site(site: dict, query: str, limit: int, timeout: int) -> list[dict]:
    """L1 指定单个专业站搜索"""
    tmpl = site.get("search_url", "")
    if not tmpl:
        return []
    url = tmpl.replace("{query}", quote_plus(query))
    html = fetch(url, timeout=timeout)
    if not html:
        print(f"[L1] ✗ {site['name']} 不可达", file=sys.stderr)
        return []
    results = parse_links(html, url, limit)
    for r in results:
        r["source"] = site["id"]
        r["grade"] = site.get("grade", "")
    if results:
        print(f"[L1] ✓ {site['name']} 命中 {len(results)} 条", file=sys.stderr)
    return results


if __name__ == "__main__":
    main()
