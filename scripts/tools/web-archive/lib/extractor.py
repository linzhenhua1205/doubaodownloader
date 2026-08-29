#!/usr/bin/env python3
"""正文提取与去噪 — 站点适配器优先, trafilatura 通用回退"""
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from bs4 import BeautifulSoup


@dataclass
class ExtractedArticle:
    title: str = ""
    url: str = ""
    author: str = ""
    published: str = ""
    description: str = ""
    text: str = ""                  # 纯文本 (去噪后)
    html: str = ""                  # 去噪后的正文 HTML (保留结构)
    images: list = field(default_factory=list)   # [{src, alt}]
    links: list = field(default_factory=list)    # [href]
    site: str = ""                  # 站点名
    adapter_name: str = "generic"
    source_snippet: str = ""        # 原文摘录 (供分析)


def extract_content(html: str, url: str, adapter=None) -> ExtractedArticle:
    """从 HTML 提取正文。策略:
      1. 站点适配器规则 (容器定位 + 去噪 + 图片/链接处理)
      2. 若适配器未找到正文容器 → trafilatura 通用提取兜底
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")

    # 站点预处理
    if adapter and adapter.preprocess_html:
        html2 = adapter.preprocess_html(html)
        if html2 != html:
            soup = BeautifulSoup(html2, "lxml")

    # 1. 元信息
    meta = {}
    if adapter:
        meta = adapter.extract_meta(soup, url)

    # 2. 定位正文容器
    container = None
    if adapter:
        container = adapter.extract_main(soup, url)
    if container is None:
        container = GenericFallback.extract_main(soup, url)

    article = ExtractedArticle(
        url=url,
        site=urlparse(url).netloc,
        adapter_name=adapter.name if adapter else "generic",
        title=meta.get("title", soup.title.string.strip() if soup.title and soup.title.string else url),
        author=meta.get("author", ""),
        published=meta.get("published", ""),
        description=meta.get("description", ""),
    )

    if container is not None:
        # 3. 去噪
        if adapter:
            container = adapter.clean_content(container)
        # 4. 图片处理 (web 链接)
        if adapter:
            article.images = adapter.process_images(container, url)
        else:
            article.images = GenericFallback.process_images(container, url)
        # 5. 链接规范化
        if adapter:
            adapter.transform_links(container, url)
        # 6. 转文本 + 保留 HTML
        article.html = str(container)
        text = container.get_text("\n", strip=True)
        article.text = normalize_text(text)
        article.links = [a["href"] for a in container.find_all("a")
                         if a.get("href") and a["href"].startswith(("http", "/"))][:200]
        article.source_snippet = article.text[:3000]
    else:
        # trafilatura 兜底
        article = GenericFallback.trafilatura_extract(html, url, article)

    # 后处理
    if adapter and adapter.postprocess_text:
        article.text = adapter.postprocess_text(article.text)
    return article


class GenericFallback:
    """通用提取策略 — 无适配器时的兜底"""

    @staticmethod
    def extract_main(soup, url: str):
        # 依次尝试容器选择器
        for sel in ["article", "[itemprop='articleBody']", ".article-content",
                    ".article_content", ".post-content", ".rich_media_content",
                    "#js_content", ".main-content", ".entry-content", "main"]:
            el = soup.select_one(sel)
            if el and len(el.get_text(strip=True)) > 200:
                return el
        # 最后: body 内文字密度最高的 div
        best = None
        best_len = 0
        for div in soup.find_all(["div", "section"]):
            t = div.get_text(strip=True)
            if len(t) > best_len:
                best_len = len(t)
                best = div
        return best if best_len > 500 else None

    @staticmethod
    def process_images(container, url: str):
        from urllib.parse import urljoin
        imgs = []
        for img in container.find_all("img"):
            src = img.get("src") or img.get("data-src") or ""
            if not src or src.startswith("data:"):
                img.decompose()
                continue
            abs_url = urljoin(url, src)
            img["src"] = abs_url
            imgs.append({"src": abs_url, "alt": img.get("alt", "").strip()})
        return imgs

    @staticmethod
    def trafilatura_extract(html: str, url: str, article: ExtractedArticle) -> ExtractedArticle:
        """trafilatura 全自动提取 (高质量通用回退)"""
        try:
            import trafilatura
            extracted = trafilatura.extract(html, url=url, include_comments=False,
                                            include_tables=True, favor_recall=False)
            if extracted:
                article.text = normalize_text(extracted)
                article.source_snippet = article.text[:3000]
                # 图片: 从原始 HTML 提取正文图片
                soup = BeautifulSoup(html, "lxml")
                main = soup.find("article") or soup
                article.images = GenericFallback.process_images(main, url)
        except Exception as e:
            article.text = f"[trafilatura 提取失败: {e}]"
        return article


def normalize_text(text: str) -> str:
    """文本规范化: 合并多余空行/空白"""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()
