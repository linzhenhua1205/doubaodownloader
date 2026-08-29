#!/usr/bin/env python3
"""技术栈 (jishuzhan.net) 站点适配器 — 针对技术栈文章页加速处理"""
from lib.adapters.base import AdapterBase


class JishuzhanAdapter(AdapterBase):
    name = "jishuzhan"
    domain_patterns = [r"jishuzhan\.net"]

    def extract_meta(self, soup, url: str):
        meta = super().extract_meta(soup, url)
        # 技术栈标题常在 h1.article-title / .article-title
        if not meta.get("title"):
            for sel in ["h1.article-title", ".article-title h1", "h1"]:
                el = soup.select_one(sel)
                if el and el.get_text(strip=True):
                    meta["title"] = el.get_text(strip=True)
                    break
        # 发布时间: 常见 .article-info time
        if not meta.get("published"):
            for sel in [".article-info time", ".publish-time", ".article-date",
                        "meta[name='publishdate']"]:
                el = soup.select_one(sel)
                if el:
                    dt = el.get("datetime") or el.get("content") or el.get_text(strip=True)
                    if dt:
                        meta["published"] = dt.strip()[:19]
                        break
        return meta

    def extract_main(self, soup, url: str):
        # 技术栈正文容器候选
        for sel in [".article-content", ".article_detail", ".article-detail",
                    ".markdown-body", ".content", "article"]:
            el = soup.select_one(sel)
            if el and len(el.get_text(strip=True)) > 300:
                return el
        return super().extract_main(soup, url)

    def clean_content(self, container):
        container = super().clean_content(container)
        # 技术栈特定噪声: 复制声明/版权/编辑推荐
        for sel in [".article-copyright", ".copyright", ".reprint", ".editor-tip",
                    ".article-footer", ".article-end", ".tip", ".notice",
                    ".article-tags", ".tag-list"]:
            for el in container.select(sel):
                el.decompose()
        return container

    def process_images(self, container, url: str):
        """技术栈图片: 处理懒加载 (data-src), 保留 web 链接"""
        imgs = super().process_images(container, url)
        # 移除占位图 (1x1 透明 gif)
        keep = []
        for img in imgs:
            if "data:image" in img["src"] or "pixel" in img["src"].lower():
                continue
            keep.append(img)
        return keep
