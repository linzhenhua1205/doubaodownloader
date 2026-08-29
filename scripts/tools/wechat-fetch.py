#!/usr/bin/env python3
"""
wechat-fetch — 微信公众号文章一条命令抓取+解析 (2026-08-06 新增)

背景: mp.weixin.qq.com 命中"环境异常"验证页时, 普通 UA / 浏览器渲染均失败;
唯一有效组合 = 微信内置浏览器 UA + URL 追加 chksm=0000000000000000 参数。
本脚本内置该绕过逻辑, 一条命令输出精简结构化结果 (无需把 3MB HTML 载入上下文, 省 token)。

用法:
    python3 scripts/tools/wechat-fetch.py --url "<微信文章URL>"          # 默认: 精简摘要
    python3 scripts/tools/wechat-fetch.py --url "<URL>" --full          # 全文 (去噪后 markdown)
    python3 scripts/tools/wechat-fetch.py --url "<URL>" --json out.json # 结构化 JSON
    python3 scripts/tools/wechat-fetch.py --url "<URL>" --md out.md     # 全文 markdown 落盘
    python3 scripts/tools/wechat-fetch.py --url "<URL>" --archive       # 走 web-archive 完整归档 (三同步)

依赖: requests beautifulsoup4 lxml (web-archive 的 .venv-web 已具备)
"""
import argparse
import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── 绕过参数 (实测必需, 见 fetcher.py 注释) ─────────────────────────
WECHAT_UA_LIST = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.44(0x18002c2b) NetType/WIFI Language/zh_CN",
    "Mozilla/5.0 (Linux; Android 12; SM-G9910 Build/SP1A.210812.016; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.127 "
    "Mobile Safari/537.36 MicroMessenger/8.0.32.2520(0x28002053) WeChat/arm64 "
    "Weixin NetType/WIFI Language/zh_CN ABI/arm64",
]
WECHAT_BLOCK_HINTS = ["环境异常", "完成验证", "去验证", "verify", "captcha"]


def ensure_bypass_param(url: str) -> str:
    """给微信 URL 追加 chksm 绕过参数, 并剥离 poc_token。

    实测 (2026-08-06): 带 poc_token (分享者 token) 的 URL 即使加 chksm 也命中
    验证页 (len≈17KB); 剥离 poc_token + chksm → 3.2MB 完整页面 ✅。
    """
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
    parsed = urlparse(url)
    qs = parse_qs(parsed.query, keep_blank_values=True)
    # 剥离分享者 token (触发更严格验证)
    qs.pop("poc_token", None)
    if "chksm" not in qs:
        qs["chksm"] = ["0000000000000000"]
    new_query = urlencode({k: v[0] for k, v in qs.items()}, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def fetch(url: str) -> str:
    """抓取微信文章完整 HTML。返回原始 HTML。"""
    url = ensure_bypass_param(url)
    last_err = ""
    for ua in WECHAT_UA_LIST:
        try:
            s = requests.Session()
            s.headers.update({
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://mp.weixin.qq.com/",
            })
            r = s.get(url, timeout=25, allow_redirects=True)
            html = r.text
            blocked = any(h in html[:30000] for h in WECHAT_BLOCK_HINTS)
            if r.status_code == 200 and not blocked and "js_content" in html:
                return html
            last_err = f"命中验证页 (len={len(html)})"
        except Exception as e:
            last_err = f"请求失败: {e}"
    raise RuntimeError(f"微信抓取失败: {last_err}")


def parse(html: str, url: str) -> dict:
    """从微信文章 HTML 提取结构化内容。"""
    soup = BeautifulSoup(html, "lxml")

    def _txt(el):
        return el.get_text(strip=True) if el else ""

    title = _txt(soup.select_one("#activity-name")) or _txt(soup.select_one("h1"))
    account = _txt(soup.select_one("#js_name"))
    author = _txt(soup.select_one("#js_author_name")) or account

    # 发布时间: #publish_time 或 JS 变量 createTime / var ct (unix 秒)
    published = _txt(soup.select_one("#publish_time"))
    if not published:
        for pat in [r"var createTime\s*=\s*['\"]([^'\"]+)['\"]",
                    r"var ct\s*=\s*['\"]([^'\"]+)['\"]",
                    r"createTime\s*[:=]\s*['\"]?(\d{10})"]:
            m = re.search(pat, html[:200000])
            if m:
                ts = m.group(1)
                if ts.isdigit() and len(ts) == 10:
                    from datetime import datetime, timezone
                    published = datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
                else:
                    published = ts[:19]
                break

    # 正文容器
    content = soup.select_one("#js_content") or soup.select_one(".rich_media_content")
    blocks = []
    images = []
    seen_texts = set()
    if content:
        for el in content.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "section"]):
            t = el.get_text(strip=True)
            if t and len(t) > 1 and t not in seen_texts:  # 去重 (li 嵌套 p 导致 double)
                seen_texts.add(t)
                blocks.append({"tag": el.name, "text": t})
        for img in content.find_all("img"):
            src = img.get("data-src") or img.get("src") or ""
            if src and src.startswith("http") and "qpic.cn" in src:
                images.append(src)

    full_text = "\n".join(b["text"] for b in blocks)
    return {
        "url": url,
        "title": title,
        "account": account,
        "author": author,
        "published": published,
        "text_len": len(full_text),
        "block_count": len(blocks),
        "image_count": len(images),
        "images": images,
        "blocks": blocks,
        "full_text": full_text,
    }


def render_summary(data: dict) -> str:
    lines = [
        f"📰 {data['title']}",
        f"   公众号: {data['account']} | 作者: {data['author']} | 发布: {data['published']}",
        f"   正文: {data['text_len']} 字符 / {data['block_count']} 块 / 图片 {data['image_count']} 张",
        "",
        "--- 正文预览 (前 2500 字符) ---",
        data["full_text"][:2500],
    ]
    return "\n".join(lines)


def render_markdown(data: dict) -> str:
    out = [f"# {data['title']}", ""]
    out.append(f"> **Source**: {data['url']}")
    out.append(f"> **Site**: 微信公众号({data['account']}) | **Author**: {data['author']} | **Published**: {data['published']}")
    out.append("")
    out.append("## 正文")
    out.append("")
    for b in data["blocks"]:
        if b["tag"] in ("h1", "h2", "h3", "h4", "h5", "h6"):
            lvl = int(b["tag"][1]) + 1
            out.append("#" * lvl + " " + b["text"])
        elif b["tag"] == "li":
            out.append("- " + b["text"])
        else:
            out.append(b["text"])
        out.append("")
    if data["images"]:
        out.append("## 图片")
        out.append("")
        for i, img in enumerate(data["images"], 1):
            out.append(f"![img{i}]({img})")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="微信公众号文章抓取+解析 (内置 chksm 绕过)")
    ap.add_argument("--url", required=True, help="微信文章 URL")
    ap.add_argument("--full", action="store_true", help="输出全文 markdown")
    ap.add_argument("--json", metavar="PATH", help="结构化 JSON 落盘")
    ap.add_argument("--md", metavar="PATH", help="全文 markdown 落盘")
    ap.add_argument("--archive", action="store_true", help="走 web-archive 完整归档 (三同步)")
    args = ap.parse_args()

    html = fetch(args.url)
    data = parse(html, args.url)

    if args.archive:
        # 复用 web-archive 主流程 (fetcher.py 已内置微信特化绕过)
        import subprocess
        wa = Path(__file__).resolve().parent / "web-archive" / "web-archive.py"
        subprocess.run([sys.executable, str(wa), "--url", args.url], check=False)
        return

    wrote_any = False
    if args.json:
        Path(args.json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"📦 JSON 已写入: {args.json}")
        wrote_any = True
    if args.md:
        md = render_markdown(data)
        Path(args.md).write_text(md, encoding="utf-8")
        print(f"📄 Markdown 已写入: {args.md} ({len(md)} chars)")
        wrote_any = True
    if args.full:
        print(render_markdown(data))
        wrote_any = True
    if not wrote_any:
        print(render_summary(data))


if __name__ == "__main__":
    main()
