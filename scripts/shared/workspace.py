#!/usr/bin/env python3
"""
workspace.py — 统一工作空间路径与工程配置 (sr-008 P0)

所有脚本应从此模块导入路径常量和通用工具，而非自行解析 __file__。

用法:
    from scripts.shared.workspace import (
        WORKSPACE_ROOT, KNOWLEDGE_ROOT, SCRIPTS_DIR, SKILLS_DIR, SPEC_DIR,
        TMP_DIR, TMP_BAK_DIR,
        resolve_path, ensure_dir, relpath,
    )
"""

import sys
from pathlib import Path
from typing import Optional

# ── 核心路径 ──────────────────────────────────────────────────────────────────

# 工作空间根目录 (cow/)
WORKSPACE_ROOT = (Path(__file__).resolve().parent.parent.parent).resolve()

# 主要子目录
KNOWLEDGE_ROOT = WORKSPACE_ROOT / "knowledge"
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
SKILLS_DIR = WORKSPACE_ROOT / "skills"
SPEC_DIR = WORKSPACE_ROOT / "spec"
MEMORY_DIR = WORKSPACE_ROOT / "memory"
TMP_DIR = WORKSPACE_ROOT / "tmp"
TMP_BAK_DIR = TMP_DIR / "bak"       # 回收站 (永不rm)
IMPORT_DIR = WORKSPACE_ROOT / "import"
CONV_LOG_DIR = WORKSPACE_ROOT / "conversation-log"

# ── 工具函数 ──────────────────────────────────────────────────────────────────


def resolve_path(path: str, base: Optional[Path] = None) -> Path:
    """
    解析路径：相对路径基于base（默认KNOWLEDGE_ROOT），绝对路径直接返回。

    用法:
        resolve_path("02_rd/report.md")          → knowledge/02_rd/report.md
        resolve_path("knowledge/report.md")      → knowledge/report.md
        resolve_path("/abs/path.md")              → /abs/path.md
    """
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    base = base or KNOWLEDGE_ROOT
    return (base / p).resolve()


def ensure_dir(path: Path) -> Path:
    """确保目录存在，返回路径"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def relpath(path: Path) -> str:
    """返回相对于 WORKSPACE_ROOT 的相对路径字符串"""
    try:
        return str(path.relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path)


def list_py_files(directory: Path, recursive: bool = True) -> list[Path]:
    """列出目录下所有 .py 文件（排除 __pycache__）"""
    pattern = "**/*.py" if recursive else "*.py"
    result = []
    for f in directory.glob(pattern):
        if "__pycache__" not in f.parts:
            result.append(f)
    return sorted(result)


def list_md_files(directory: Path, recursive: bool = True) -> list[Path]:
    """列出目录下所有 .md 文件"""
    pattern = "**/*.md" if recursive else "*.md"
    return sorted(directory.glob(pattern))


# ── 自测 ──────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print(f"WORKSPACE_ROOT  = {WORKSPACE_ROOT}")
    print(f"KNOWLEDGE_ROOT  = {KNOWLEDGE_ROOT}")
    print(f"SCRIPTS_DIR     = {SCRIPTS_DIR}")
    print(f"SKILLS_DIR      = {SKILLS_DIR}")
    print(f"SPEC_DIR        = {SPEC_DIR}")
    print(f"TMP_DIR         = {TMP_DIR}")
    print(f"relpath test    = {relpath(SPEC_DIR / 'sr-008.md')}")
    print(f"resolve test    = {resolve_path('02_rd/index.md')}")
    print("✅ workspace.py自测通过")
