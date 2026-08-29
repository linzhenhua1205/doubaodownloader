"""知识库集成 — 语义检索、RAG、归档触发。"""

from __future__ import annotations

import os
from typing import Any

from config import settings
from utils import get_logger

log = get_logger("knowledge")


class KnowledgeRetriever:
    """
    知识库检索器 — 基于文件内容的语义检索 + 关键词匹配。

    当前实现: 文件系统全文搜索（简单模式）
    生产推荐: 接入向量库（Milvus/Qdrant）+ Embedding 模型
    """

    def __init__(self) -> None:
        self._kb_path = settings.KNOWLEDGE_PATH
        self._index_cache: dict[str, str] = {}  # path → content preview

    async def search(
        self, query: str, top_k: int = 5, module: str | None = None
    ) -> list[dict[str, Any]]:
        """
        搜索知识库。

        Args:
            query: 搜索关键词
            top_k: 返回的最大结果数
            module: 限定模块（如 "02_rd"），None 表示全部

        Returns:
            [{"path": "...", "title": "...", "snippet": "...", "score": 0.95}, ...]
        """
        results = []
        search_root = os.path.join(self._kb_path, module) if module else self._kb_path

        if not os.path.exists(search_root):
            return []

        query_lower = query.lower()

        for root, _dirs, files in os.walk(search_root):
            # 跳过 bak 目录
            if "/bak/" in root or root.endswith("/bak"):
                continue

            for fname in files:
                if not fname.endswith(".md"):
                    continue

                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(2000)  # 读前 2000 字符
                except Exception:
                    continue

                # 简单关键词匹配（生产环境应替换为向量检索）
                if query_lower in content.lower():
                    # 提取匹配片段
                    idx = content.lower().find(query_lower)
                    start = max(0, idx - 80)
                    end = min(len(content), idx + len(query) + 80)
                    snippet = content[start:end].replace("\n", " ")

                    # 计算简单匹配分数
                    score = min(1.0, query_lower.count(" ") / 5 + 0.3)

                    results.append({
                        "path": fpath,
                        "title": fname.replace(".md", ""),
                        "snippet": f"...{snippet}...",
                        "score": score,
                    })

        # 按分数倒序
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    async def get_context(
        self, paths: list[str], max_chars: int = 4000
    ) -> str:
        """获取指定文档的内容作为 LLM 上下文。"""
        contexts = []
        total_chars = 0

        for path in paths:
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            if total_chars + len(content) > max_chars:
                content = content[: max_chars - total_chars] + "\n...(truncated)"

            contexts.append(f"--- {path} ---\n{content}")
            total_chars += len(content)

            if total_chars >= max_chars:
                break

        return "\n\n".join(contexts)


class KnowledgeArchiver:
    """
    知识库归档器 — 将内容归档到 knowledge/06_others/sources/。
    """

    def __init__(self) -> None:
        self._sources_dir = os.path.join(settings.KNOWLEDGE_PATH, "sources")

    async def archive(
        self, content: str, title: str, source_url: str = "", tags: list[str] | None = None
    ) -> str:
        """
        归档内容到知识库。

        Returns: 文档路径
        """
        os.makedirs(self._sources_dir, exist_ok=True)

        # 生成 slug 文件名
        slug = title.lower().replace(" ", "-").replace("/", "-")[:60]
        fname = f"{slug}.md"
        fpath = os.path.join(self._sources_dir, fname)

        tags_str = ", ".join(tags or [])
        header = (
            f"---\n"
            f"title: {title}\n"
            f"source: {source_url}\n"
            f"tags: [{tags_str}]\n"
            f"archived_at: {__import__('datetime').datetime.now().isoformat()}\n"
            f"---\n\n"
        )

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(header + content)

        log.info("knowledge_archived", path=fpath, title=title)

        # TODO: 更新 index.md
        return fpath


# 全局单例
retriever = KnowledgeRetriever()
archiver = KnowledgeArchiver()
