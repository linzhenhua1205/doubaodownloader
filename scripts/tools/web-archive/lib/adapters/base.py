#!/usr/bin/env python3
"""适配器基类 — 站点适配框架核心

站点适配器职责 (针对各类网站加速处理):
  - domain_patterns: 匹配域名 (正则, 按序匹配)
  - extract_meta:     提取标题/作者/发布时间/描述
  - extract_main:     定位正文容器 (CSS 选择器或 XPath), 返回 BeautifulSoup 元素
  - clean_content:    去噪 (移除导航/广告/侧栏/页脚/推荐/脚本/样式)
  - process_images:   图片 URL 规范化 (相对→绝对, 保留 web 链接)
  - transform_links:  链接去噪 (保留正文内链, 丢弃追踪/广告链接)
  - preprocess_html:  站点特定预处理 (如注入容器标记)

通用适配器 GenericAdapter 用 trafilatura 自动提取, 作为未注册站点的回退。
"""
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse


class AdapterBase:
    """站点适配器基类 — 子类通过类属性覆盖 name/domain_patterns 并实现钩子方法。"""
    name = "generic"
    domain_patterns = []

    def match(self, url: str) -> bool:
        for pat in self.domain_patterns:
            if re.search(pat, url):
                return True
        return False

    # ── 元信息提取 (子类覆写) ──────────────────────────────
    def extract_meta(self, soup, url: str) -> dict:
        """默认: Open Graph / meta 标签回退"""
        meta = {}
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            meta["title"] = og_title["content"].strip()
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            meta["description"] = og_desc["content"].strip()
        # 发布时间
        for sel in ["meta[property='article:published_time']",
                    "meta[name='pubdate']", "meta[name='publishdate']",
                    "time[datetime]", "meta[itemprop='datePublished']"]:
            el = soup.select_one(sel)
            if el:
                dt = el.get("content") or el.get("datetime") or el.text
                if dt:
                    meta["published"] = dt.strip()[:19]
                    break
        # 作者
        for sel in ["meta[name='author']", "meta[property='article:author']"]:
            el = soup.select_one(sel)
            if el and el.get("content"):
                meta["author"] = el["content"].strip()
                break
        return meta

    # ── 正文容器定位 (子类覆写, 返回容器元素或 None) ────────
    def extract_main(self, soup, url: str):
        """默认: 尝试常见正文容器选择器; 返回 soup 元素或 None"""
        candidates = [
            "article", "[itemprop='articleBody']", ".article-content",
            ".article_content", ".article-detail", ".post-content",
            ".rich_media_content", "#js_content", ".content-area",
            ".main-content", ".entry-content", "main", ".page-content",
        ]
        for sel in candidates:
            el = soup.select_one(sel)
            if el:
                return el
        return None

    # ── 内容去噪 (子类可覆写补充规则) ───────────────────────
    NOISE_SELECTORS = [
        "script", "style", "noscript", "iframe", "nav", "header", "footer",
        "aside", ".ad", ".ads", ".advert", ".advertisement", ".banner",
        ".recommend", ".related", ".hot", ".sidebar", ".side-bar",
        ".share", ".social", ".comment", ".comments", ".comment-list",
        ".pagination", ".breadcrumb", ".toc", ".subscribe", ".newsletter",
        ".popup", ".modal", ".cookie", ".back-to-top", ".qr-code",
        "[class*='advert']", "[class*='recommend']", "[id*='advert']",
    ]

    def clean_content(self, container):
        """移除噪声节点 (导航/广告/侧栏/页脚/推荐等)"""
        if container is None:
            return container
        for sel in self.NOISE_SELECTORS:
            try:
                for el in container.select(sel):
                    el.decompose()
            except Exception:
                pass
        # 移除空段落 / 纯空白 (但保留包含图片的容器, 否则图被提前删掉)
        for p in container.find_all(["p", "div", "section"]):
            if not p.get_text(strip=True) and p.name != "br" and not p.find("img"):
                p.decompose()
        return container

    # ── 图片处理: 相对→绝对 URL, 保留 web 链接 (不下载) ─────
    def process_images(self, container, url: str):
        imgs = []
        if container is None:
            return imgs
        for img in container.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-original") or ""
            if not src or src.startswith("data:"):
                # data: URI 或空 — 无法转 web 链接, 移除
                img.decompose()
                continue
            abs_url = urljoin(url, src)
            img["src"] = abs_url
            # 懒加载: 补 data-src 属性
            for attr in ("data-src", "data-original", "data-lazy-src", "data-actualsrc"):
                ds = img.get(attr)
                if ds and not ds.startswith("data:"):
                    img["src"] = urljoin(url, ds)
                    break
            alt = img.get("alt", "").strip()
            imgs.append({"src": abs_url, "alt": alt})
        return imgs

    # ── 链接去噪 ────────────────────────────────────────────
    def transform_links(self, container, url: str):
        """将相对链接转绝对; 丢弃纯脚本/追踪链接"""
        if container is None:
            return
        for a in container.find_all("a"):
            href = a.get("href", "")
            if not href or href.startswith(("javascript:", "#", "mailto:")):
                a.decompose()
                continue
            a["href"] = urljoin(url, href)

    # ── 站点特定预处理 (子类覆写) ───────────────────────────
    def preprocess_html(self, html: str) -> str:
        return html

    # ── 站点特定后处理 (子类覆写, 如表格修复) ──────────────
    def postprocess_text(self, text: str) -> str:
        return text


class GenericAdapter(AdapterBase):
    """通用适配器 — trafilatura 全自动提取, 无需站点规则"""
    name = "generic"
    domain_patterns = []

    def extract_main(self, soup, url: str):
        # 尝试常见容器; 若全部失败返回 None (由 extractor 走 trafilatura 兜底)
        return super().extract_main(soup, url)
