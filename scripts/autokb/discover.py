"""
文件发现与基础解析模块

职责: 扫描 import/ 目录，识别文件类型，提取基础元数据（标题、来源、日期）。
"""

import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Generator, Optional
from .config import IMPORT_DIR, IMPORT_SOURCES, IMPORT_DUPLICATE, IGNORE_KEYWORDS

# ============================================================
# 数据结构
# ============================================================


class SourceFile:
    """单个源文件的信息"""

    def __init__(
        self,
        path: Path,
        source_type: str,  # "doubao" | "md" | "fetched" | "pdf"
        content: str = "",
        title: str = "",
        date: Optional[str] = None,
        size_bytes: int = 0,
    ):
        self.path = path
        self.source_type = source_type
        self.content = content
        self.title = title or path.stem
        self.date = date
        self.size_bytes = size_bytes or (path.stat().st_size if path.exists() else 0)
        self.fingerprint: str = ""  # 内容指纹，用于去重

    def __repr__(self):
        return f"<SourceFile {self.source_type}:{self.path.name}>"


# ============================================================
# 文件发现
# ============================================================


def discover_all() -> list[SourceFile]:
    """扫描所有来源目录，返回文件列表"""
    files = []
    for source_name, source_dir in IMPORT_SOURCES.items():
        for f in sorted(source_dir.rglob("*")):
            if not f.is_file():
                continue
            if _is_ignored(f):
                continue
            files.append(_make_source(f, source_name))
    # PDF 单独处理
    pdf = IMPORT_DIR / "100skill.pdf"
    if pdf.exists():
        files.append(_make_source(pdf, "pdf"))
    return files


def discover_by_source(source_name: str) -> list[SourceFile]:
    """按来源目录发现"""
    if source_name not in IMPORT_SOURCES:
        raise ValueError(f"未知来源: {source_name}, 可选: {list(IMPORT_SOURCES.keys())}")
    source_dir = IMPORT_SOURCES[source_name]
    files = []
    for f in sorted(source_dir.rglob("*")):
        if not f.is_file():
            continue
        if _is_ignored(f):
            continue
        files.append(_make_source(f, source_name))
    return files


def discover_one(file_path: Path) -> Optional[SourceFile]:
    """发现单个文件"""
    if not file_path.exists() or not file_path.is_file():
        return None
    # 推断来源类型
    rel = file_path.relative_to(IMPORT_DIR) if IMPORT_DIR in file_path.parents else None
    if rel:
        source_type = rel.parts[0] if len(rel.parts) > 0 else "unknown"
        # 标准化名称
        source_type = source_type.replace("import", "unknown")
    else:
        source_type = "external"
    return _make_source(file_path, source_type)


# ============================================================
# 核心操作
# ============================================================


def parse_content(sf: SourceFile) -> SourceFile:
    """读取文件内容到内存，自动解码 quoted-printable 编码"""
    try:
        with open(sf.path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        # 检测并解码 quoted-printable 编码（常见于邮件转存/嵌入式内容）
        if _looks_like_quoted_printable(raw):
            import quopri
            try:
                decoded = quopri.decodestring(raw.encode("utf-8", errors="replace"))
                raw = decoded.decode("utf-8", errors="replace")
            except Exception:
                pass  # 解码失败则保留原始内容
        sf.content = raw
    except Exception as e:
        sf.content = f"[读取失败: {e}]"
    sf.fingerprint = hashlib.md5(sf.content.encode("utf-8")).hexdigest()
    return sf


def extract_title(content: str, fallback: str) -> str:
    """从内容中提取标题，支持多种格式"""
    lines = content.split("\n")

    # ----- 豆包对话格式: # 我：\n\n<用户问题> -----
    if lines and lines[0].strip() in ("# 我：", "# 我:"):
        # 取"我："后面第一个有意义的非空行
        for line in lines[1:]:
            stripped = line.strip()
            if stripped and stripped not in ("# 豆包：", "# 豆包:", "豆包：", "豆包:"):
                # 去掉可能的前缀 "资讯：""问题："
                stripped = re.sub(r"^(资讯|问题|提问|需求)[：:]\s*", "", stripped)
                return stripped[:80]
        return "用户提问"

    # ----- 标准 markdown 格式: # 标题 -----
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        # 跳过 doubao 专有标题
        if title not in ("我", "我：", "我:", "豆包", "豆包：", "豆包:"):
            return title[:80]

    # ----- ## 标题 -----
    m = re.search(r"^##\s+(.+)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()[:80]

    # ----- 文件名兜底 -----
    return fallback[:80]


def extract_date(content: str, filename: str) -> Optional[str]:
    """从内容或文件名中提取日期"""
    # 文件名模式: 2026-03-25-xxx.md
    m = re.search(r"(\d{4})[-_]?(\d{2})[-_]?(\d{2})", filename)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        if 2000 <= int(y) <= 2030 and 1 <= int(mo) <= 12 and 1 <= int(d) <= 31:
            return f"{y}-{mo}-{d}"
    # 文件名中的时间戳: xxx_0613174400.md → 2026-06-13 (MMDDHHMMSS)
    m = re.search(r"_(\d{2})(\d{2})\d{4}\.md", filename)
    if m:
        mo, d = m.group(1), m.group(2)
        if 1 <= int(mo) <= 12 and 1 <= int(d) <= 31:
            return f"2026-{mo}-{d}"
    # 内容中的日期: 2026年1月4日、2026-01-04、2026/01/04
    m = re.search(r"\b(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})日?\b", content)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        if 2000 <= int(y) <= 2030 and 1 <= int(mo) <= 12 and 1 <= int(d) <= 31:
            return f"{y}-{int(mo):02d}-{int(d):02d}"
    return None


def estimate_file_type(content: str) -> str:
    """估算内容类型: doubao(dialogue) | article | note | data"""
    lines = content.strip().split("\n")
    # 豆包对话: "我：\n\n" 模式
    if re.search(r"^我[：:]", content, re.MULTILINE) and re.search(r"^豆包[：:]", content, re.MULTILINE):
        return "doubao_dialogue"
    # 简短笔记
    if len(lines) < 5:
        return "short_note"
    # 包含表格/数据
    if re.search(r"\|.*\|.*\|", content):
        return "data_document"
    return "article"


# ============================================================
# 辅助函数
# ============================================================


def _is_ignored(path: Path) -> bool:
    """检查文件是否应被忽略"""
    name = path.name.lower()
    for kw in IGNORE_KEYWORDS:
        if kw in name:
            return True
    # 跳过隐藏文件
    if name.startswith("."):
        return True
    # 跳过目录
    if path.is_dir():
        return True
    return False


def _make_source(path: Path, source_type: str) -> SourceFile:
    """从路径创建 SourceFile 对象（不读取内容）"""
    return SourceFile(
        path=path,
        source_type=source_type,
        title=path.stem,
        size_bytes=path.stat().st_size if path.exists() else 0,
    )


def _looks_like_quoted_printable(text: str) -> bool:
    """检测文本是否包含 quoted-printable 编码特征"""
    if not text:
        return False
    # QP特征：大量 =XX 模式（=后跟2位十六进制）
    qp_patterns = re.findall(r"=[0-9A-Fa-f]{2}", text[:2000])
    # 如果有至少5个 =XX 模式，视为QP编码
    return len(qp_patterns) >= 5


# ============================================================
# 去重
# ============================================================


def deduplicate(files: list[SourceFile]) -> list[SourceFile]:
    """基于内容指纹去重，保留每个指纹的第一个文件"""
    seen: set[str] = set()
    result = []
    for f in files:
        if not f.fingerprint:
            f = parse_content(f)
        if f.fingerprint not in seen:
            seen.add(f.fingerprint)
            result.append(f)
    return result


def find_duplicates(files: list[SourceFile]) -> dict[str, list[SourceFile]]:
    """找出重复文件组"""
    groups: dict[str, list[SourceFile]] = {}
    for f in files:
        if not f.fingerprint:
            f = parse_content(f)
        groups.setdefault(f.fingerprint, []).append(f)
    return {fp: group for fp, group in groups.items() if len(group) > 1}


def summary(files: list[SourceFile]) -> dict:
    """生成扫描摘要"""
    total = len(files)
    by_type: dict[str, int] = {}
    total_size = 0
    for f in files:
        by_type[f.source_type] = by_type.get(f.source_type, 0) + 1
        total_size += f.size_bytes
    return {
        "total": total,
        "by_type": by_type,
        "total_size_mb": round(total_size / 1024 / 1024, 1),
    }
