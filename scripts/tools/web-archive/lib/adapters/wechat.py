#!/usr/bin/env python3
"""微信公众号文章适配器 — mp.weixin.qq.com"""
from lib.adapters.base import AdapterBase


class WechatAdapter(AdapterBase):
    name = "wechat"
    domain_patterns = [r"mp\.weixin\.qq\.com"]

    def extract_meta(self, soup, url: str):
        meta = super().extract_meta(soup, url)
        if not meta.get("title"):
            el = soup.select_one("#activity-name") or soup.select_one("h1")
            if el:
                meta["title"] = el.get_text(strip=True)
        if not meta.get("author"):
            el = soup.select_one("#js_author_name") or soup.select_one("#js_name") or soup.select_one(".rich_media_meta_text")
            if el:
                meta["author"] = el.get_text(strip=True)
        if not meta.get("published"):
            el = soup.select_one("#publish_time") or soup.select_one(".publish_time")
            if el and el.get_text(strip=True):
                meta["published"] = el.get_text(strip=True)[:19]
            else:
                # 微信发布时间在 JS 变量 createTime / var ct 中 (unix 秒)
                import re as _re
                m = _re.search(r"var createTime\s*=\s*['\"]([^'\"]+)['\"]", str(soup)[:200000])
                if not m:
                    m = _re.search(r"var ct\s*=\s*['\"]([^'\"]+)['\"]", str(soup)[:200000])
                if m:
                    ts = m.group(1)
                    if ts.isdigit() and len(ts) == 10:
                        from datetime import datetime, timezone
                        meta["published"] = datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
                    else:
                        meta["published"] = ts[:19]
        return meta

    def extract_main(self, soup, url: str):
        el = soup.select_one("#js_content") or soup.select_one(".rich_media_content")
        if el and len(el.get_text(strip=True)) > 100:
            return el
        return super().extract_main(soup, url)

    def clean_content(self, container):
        container = super().clean_content(container)
        for sel in [".rich_media_tool", ".rich_media_area_extra", ".js_edit_content",
                    ".rich_media_meta", ".rich_media_title", "#js_article"]:
            for el in container.select(sel):
                el.decompose()
        return container

    def process_images(self, container, url: str):
        """微信图片: 优先取 data-src (微信 img 的 src 常为空或 data:URI,
        若按 base 逻辑先读 src 会把图片当无效 decompose 掉 → 图片 0 张)。
        保留 web 链接, 过滤表情/1px 图。"""
        from urllib.parse import urljoin
        imgs = []
        if container is None:
            return imgs
        for img in container.find_all("img"):
            src = (img.get("data-src") or img.get("data-original")
                   or img.get("src") or "")
            if not src or src.startswith("data:"):
                img.decompose()
                continue
            abs_url = urljoin(url, src)
            img["src"] = abs_url
            alt = img.get("alt", "").strip()
            imgs.append({"src": abs_url, "alt": alt})
        # 微信表情图 (emoji) 是 data: URI 已被过滤; 过滤 1px 图
        keep = []
        for img in imgs:
            if "1x1" in img["src"].lower() or "transparent" in img["src"].lower():
                continue
            keep.append(img)
        return keep
