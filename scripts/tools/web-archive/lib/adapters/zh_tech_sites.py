#!/usr/bin/env python3
"""中文技术社区合集适配器 — 掘金/博客园/思否/腾讯云开发者社区"""
from lib.adapters.base import AdapterBase


class JuejinAdapter(AdapterBase):
    name = "juejin"
    domain_patterns = [r"juejin\.cn"]

    def extract_meta(self, soup, url: str):
        meta = super().extract_meta(soup, url)
        if not meta.get("title"):
            el = soup.select_one("h1.article-title") or soup.select_one("h1")
            if el:
                meta["title"] = el.get_text(strip=True)
        if not meta.get("author"):
            el = soup.select_one(".author-name") or soup.select_one("[class*='author'] a")
            if el:
                meta["author"] = el.get_text(strip=True)
        if not meta.get("published"):
            el = soup.select_one("time")
            if el:
                dt = el.get("datetime") or el.get_text(strip=True)
                if dt:
                    meta["published"] = dt.strip()[:19]
        return meta

    def extract_main(self, soup, url: str):
        el = soup.select_one(".article-content") or soup.select_one(".markdown-body")
        if el and len(el.get_text(strip=True)) > 200:
            return el
        return super().extract_main(soup, url)


class CnblogsAdapter(AdapterBase):
    name = "cnblogs"
    domain_patterns = [r"cnblogs\.com"]

    def extract_meta(self, soup, url: str):
        meta = super().extract_meta(soup, url)
        if not meta.get("title"):
            el = soup.select_one("#cb_post_title_url") or soup.select_one("h1")
            if el:
                meta["title"] = el.get_text(strip=True)
        if not meta.get("published"):
            el = soup.select_one(".postDesc") or soup.select_one("#post-date")
            if el:
                meta["published"] = el.get_text(strip=True)[-20:]
        return meta

    def extract_main(self, soup, url: str):
        el = soup.select_one("#cnblogs_post_body") or soup.select_one(".postBody")
        if el and len(el.get_text(strip=True)) > 200:
            return el
        return super().extract_main(soup, url)

    def clean_content(self, container):
        container = super().clean_content(container)
        for sel in [".postDesc", ".blog_post_info", ".post-copyright",
                    ".feedback_area", ".cnblogs_code_toolbar"]:
            for el in container.select(sel):
                el.decompose()
        return container


class SegmentfaultAdapter(AdapterBase):
    name = "segmentfault"
    domain_patterns = [r"segmentfault\.com"]

    def extract_main(self, soup, url: str):
        el = soup.select_one(".article-content") or soup.select_one(".fmt")
        if el and len(el.get_text(strip=True)) > 200:
            return el
        return super().extract_main(soup, url)

    def clean_content(self, container):
        container = super().clean_content(container)
        for sel in [".article-footer", ".article-attach", ".copyright", ".recommend"]:
            for el in container.select(sel):
                el.decompose()
        return container


class TencentCloudAdapter(AdapterBase):
    name = "tencent-cloud"
    domain_patterns = [r"cloud\.tencent\.com"]

    def extract_meta(self, soup, url: str):
        meta = super().extract_meta(soup, url)
        if not meta.get("title"):
            el = soup.select_one("h1") or soup.select_one(".J-articleTitle")
            if el:
                meta["title"] = el.get_text(strip=True)
        if not meta.get("published"):
            el = soup.select_one(".time") or soup.select_one("time")
            if el:
                dt = el.get("datetime") or el.get_text(strip=True)
                if dt:
                    meta["published"] = dt.strip()[:19]
        return meta

    def extract_main(self, soup, url: str):
        el = soup.select_one(".J-articleContent") or soup.select_one(".article-content")
        if el and len(el.get_text(strip=True)) > 200:
            return el
        return super().extract_main(soup, url)

    def clean_content(self, container):
        container = super().clean_content(container)
        for sel in [".J-articleFooter", ".article-copyright", ".J-recommend",
                    ".author-info", ".article-actions"]:
            for el in container.select(sel):
                el.decompose()
        return container
