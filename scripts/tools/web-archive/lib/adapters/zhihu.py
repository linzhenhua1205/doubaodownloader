#!/usr/bin/env python3
"""知乎专栏/回答适配器 — zhuanlan.zhihu.com / www.zhihu.com"""
from lib.adapters.base import AdapterBase


class ZhihuAdapter(AdapterBase):
    name = "zhihu"
    domain_patterns = [r"zhihu\.com"]

    def extract_meta(self, soup, url: str):
        meta = super().extract_meta(soup, url)
        if not meta.get("title"):
            el = soup.select_one("h1.Post-Title") or soup.select_one("h1")
            if el:
                meta["title"] = el.get_text(strip=True)
        return meta

    def extract_main(self, soup, url: str):
        el = soup.select_one(".Post-RichTextContainer") or soup.select_one(".RichText")
        if el and len(el.get_text(strip=True)) > 200:
            return el
        return super().extract_main(soup, url)

    def clean_content(self, container):
        container = super().clean_content(container)
        for sel in [".RichText-actions", ".Post-Author", ".Post-SideActions",
                    ".ContentItem-actions", ".QuestionButtonGroup"]:
            for el in container.select(sel):
                el.decompose()
        return container
