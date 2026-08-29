#!/usr/bin/env python3
"""抓取器 — requests 优先, 浏览器回退 (登录/JS 渲染站点)"""
import re
import os
from dataclasses import dataclass
from urllib.parse import urlparse

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# 常见反爬站点: 需要浏览器渲染或特殊头
BROWSER_REQUIRED_HINTS = [
    "cf-challenge", "captcha", "verify", "access denied", "安全检查",
    "验证", "js-required", "challenge-platform",
]

# ── 微信特化 (2026-08-06 实战: mp.weixin.qq.com "环境异常"验证页绕过) ──
# 关键: 微信 UA + URL 追加 chksm=0000000000000000 (二者缺一不可, scene=27 非必需;
# 普通 Chrome UA 即使加参数也失败; 浏览器渲染同样命中验证)
WECHAT_UA_LIST = [
    # iPhone 微信内置浏览器 (实测有效)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.44(0x18002c2b) NetType/WIFI Language/zh_CN",
    # Android 微信内置浏览器
    "Mozilla/5.0 (Linux; Android 12; SM-G9910 Build/SP1A.210812.016; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.127 "
    "Mobile Safari/537.36 MicroMessenger/8.0.32.2520(0x28002053) WeChat/arm64 "
    "Weixin NetType/WIFI Language/zh_CN ABI/arm64",
]
WECHAT_BYPASS_PARAM = "chksm=0000000000000000"  # 实测必需的绕过参数
WECHAT_BLOCK_HINTS = ["环境异常", "完成验证", "去验证", "verify", "captcha"]


def _is_wechat_url(url: str) -> bool:
    return "mp.weixin.qq.com" in url


@dataclass
class FetchResult:
    ok: bool
    html: str = ""
    status: int = 0
    final_url: str = ""
    error: str = ""
    used_browser: bool = False


def _ensure_wechat_bypass_param(url: str) -> str:
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
        qs["chksm"] = [WECHAT_BYPASS_PARAM.split("=")[1]]
    new_query = urlencode({k: v[0] for k, v in qs.items()}, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def _fetch_wechat(url: str) -> FetchResult:
    """微信文章特化抓取: 微信 UA + chksm 绕过参数组合重试 (纯 requests, 无需浏览器)。

    背景 (2026-08-06 量子位 MindMemOS 文章实战):
    - requests 普通 UA 直连 → 17KB "环境异常"验证页
    - playwright 渲染 → 同样命中验证 (Target crashed / 环境异常)
    - 微信 UA + chksm=0000000000000000 → 3.2MB 完整页面 ✅
    """
    url = _ensure_wechat_bypass_param(url)
    last_err = ""
    for ua in WECHAT_UA_LIST:
        try:
            session = requests.Session()
            session.headers.update({
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://mp.weixin.qq.com/",
            })
            r = session.get(url, timeout=25, allow_redirects=True)
            html = r.text
            blocked = any(h in html[:30000] for h in WECHAT_BLOCK_HINTS)
            if r.status_code == 200 and not blocked and "js_content" in html:
                return FetchResult(ok=True, html=html, status=r.status_code,
                                   final_url=r.url or url)
            last_err = f"微信 UA 命中验证页 (len={len(html)})"
        except Exception as e:
            last_err = f"微信 UA 请求失败: {e}"
    return FetchResult(ok=False, error=last_err or "微信特化抓取失败")


def fetch_html(url: str, adapter=None, use_browser_fallback: bool = True) -> FetchResult:
    """抓取 HTML。先 requests, 失败或疑似反爬时回退浏览器。"""
    # 1. requests 直连
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        r = session.get(url, timeout=20, allow_redirects=True)
        # 编码检测修复 (2026-08-13 C114 GBK 乱码): headers 未声明 charset 时
        # requests 默认按 ISO-8859-1 解码中文页面 → 乱码; 改用内容探测
        if not r.encoding or r.encoding.lower() in ("iso-8859-1", "ascii", "windows-1252"):
            r.encoding = r.apparent_encoding or "utf-8"
        html = r.text
        blocked = any(h.lower() in html.lower()[:20000] for h in BROWSER_REQUIRED_HINTS)
        if r.status_code == 200 and not blocked:
            return FetchResult(ok=True, html=html, status=r.status_code,
                               final_url=r.url or url)
        # 微信文章: 普通 UA 直连失败 → 微信 UA + chksm 绕过 (纯 requests, 省 token)
        if _is_wechat_url(url):
            wx = _fetch_wechat(url)
            if wx.ok:
                return wx
            if not use_browser_fallback:
                return FetchResult(ok=False, html=html, status=r.status_code,
                                   error=f"微信直连+特化均失败: {wx.error}")
        if not use_browser_fallback:
            return FetchResult(ok=False, html=html, status=r.status_code,
                               error=f"疑似反爬/异常页面 (status={r.status_code})")
    except Exception as e:
        if not use_browser_fallback:
            return FetchResult(ok=False, error=f"requests 失败: {e}")

    # 2. 浏览器回退
    return _fetch_via_browser(url)


def _find_system_chromium() -> str:
    """自动发现系统已安装的 chromium 可执行文件。

    playwright 自带的浏览器版本常未安装 (报 "Executable doesn't exist"/
    "找不到 chromium-XXXX", 而系统只有其它版本), 此时必须显式传
    executable_path 指向真实存在的 chromium。参考路径:
    ~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome
    """
    import glob
    import os
    import shutil

    candidates = []
    for pat in (
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome"),
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-mac/Chromium"),
        os.path.expanduser("~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux*/chrome-headless-shell"),
    ):
        candidates += glob.glob(pat)
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        p = shutil.which(name)
        if p:
            candidates.append(p)
    return candidates[0] if candidates else ""


# 阿里云 WAF / 其它 JS 挑战页面特征 (返回混淆脚本而非正文)
WAF_CHALLENGE_HINTS = ["_waf_", "acw_sc__", "window._", "challenge", "slide", "滑动验证"]


def _looks_like_challenge(html: str) -> bool:
    return any(h in html[:50000].lower() for h in WAF_CHALLENGE_HINTS)


def _fetch_via_browser(url: str) -> FetchResult:
    """通过 playwright (若可用) 渲染抓取。

    反爬增强 (2026-08-05 雪球实战):
    1. 自动发现系统 chromium 并传 executable_path (playwright 自带版本常缺失)
    2. 命中 WAF/JS 挑战时先访问首页种 cookie, 再回目标页
       (阿里云 WAF 靠 JS 挑战验证 cookie, 首页种好 cookie 后同源请求可通过)
    """
    # ⚠️ Playwright 默认禁用 (2026-08-12)：无头环境启动浏览器会导致系统挂死
    if os.environ.get("PLAYWRIGHT_ENABLED") != "1":
        return FetchResult(ok=False, error="浏览器回退已禁用 (PLAYWRIGHT_ENABLED=1 可启用；2026-08-12 起默认禁用防挂死)")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return FetchResult(ok=False, error="浏览器回退不可用 (未安装 playwright)")
    try:
        with sync_playwright() as p:
            launch_kwargs = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            }
            exe = _find_system_chromium()
            if exe:
                launch_kwargs["executable_path"] = exe
            browser = p.chromium.launch(**launch_kwargs)
            page = browser.new_page(user_agent=UA)
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(1500)  # 等 JS 渲染
            if _looks_like_challenge(page.content()):
                # 首页种 cookie 后再访问目标页
                parsed = urlparse(url)
                home = f"{parsed.scheme}://{parsed.netloc}"
                try:
                    page.goto(home, timeout=30000, wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)
                    page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)
                except Exception:
                    pass  # 种 cookie 失败则返回当前内容, 由上层决定
            html = page.content()
            final_url = page.url
            browser.close()
            return FetchResult(ok=True, html=html, final_url=final_url, used_browser=True)
    except Exception as e:
        return FetchResult(ok=False, error=f"浏览器渲染失败: {e}")
