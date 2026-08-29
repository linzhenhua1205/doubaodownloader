#!/usr/bin/env python3
"""CSDN 博客适配器 — blog.csdn.net"""
from lib.adapters.base import AdapterBase


class CsdnAdapter(AdapterBase):
    name = "csdn"
    domain_patterns = [r"blog\.csdn\.net", r"www\.csdn\.net"]

    def extract_meta(self, soup, url: str):
        meta = super().extract_meta(soup, url)
        if not meta.get("title"):
            el = soup.select_one("h1.title-article") or soup.select_one("h1")
            if el:
                meta["title"] = el.get_text(strip=True)
        if not meta.get("published"):
            el = soup.select_one(".time") or soup.select_one("[class*='time']")
            if el:
                meta["published"] = el.get_text(strip=True)[:19]
        return meta

    def extract_main(self, soup, url: str):
        el = soup.select_one("#content_views") or soup.select_one(".article_content")
        if el and len(el.get_text(strip=True)) > 200:
            return el
        return super().extract_main(soup, url)

    def clean_content(self, container):
        container = super().clean_content(container)
        for sel in [".article-copyright", ".hide-article-box", ".toolbox",
                    ".more-toolbox", ".recommend-box", ".blog-footer-box",
                    ".follow-text", ".person-info-bottom"]:
            for el in container.select(sel):
                el.decompose()
        return container
