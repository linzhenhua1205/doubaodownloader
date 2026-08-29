#!/usr/bin/env python3
"""InfoQ 中文站适配器 — www.infoq.cn"""
from lib.adapters.base import AdapterBase


class InfoqAdapter(AdapterBase):
    name = "infoq"
    domain_patterns = [r"infoq\.cn"]

    def extract_meta(self, soup, url: str):
        meta = super().extract_meta(soup, url)
        if not meta.get("title"):
            el = soup.select_one("h1.article-title") or soup.select_one("h1")
            if el:
                meta["title"] = el.get_text(strip=True)
        if not meta.get("published"):
            el = soup.select_one("time") or soup.select_one("[class*='time']")
            if el:
                dt = el.get("datetime") or el.get_text(strip=True)
                if dt:
                    meta["published"] = dt.strip()[:19]
        return meta

    def extract_main(self, soup, url: str):
        el = soup.select_one(".article-content") or soup.select_one("article")
        if el and len(el.get_text(strip=True)) > 200:
            return el
        return super().extract_main(soup, url)

    def clean_content(self, container):
        container = super().clean_content(container)
        for sel in [".article-info", ".author-info", ".article-tags", ".recommend",
                    ".subscribe", ".article-action", ".infoq-footer"]:
            for el in container.select(sel):
                el.decompose()
        return container
