#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱覆盖率快速验证工具
用法: python verify_kg.py [--dir 目录路径]
"""

import os
import sys
from pathlib import Path

KNOWLEDGE_ROOT = Path(r"h:\github\cowkb\knowledge")
EXCLUDE_DIRS = {"01_survey", "bak", "import-modules", "oldbak"}
EXCLUDE_FILES = {"index.md", "log.md", "README.md", "TRACKING.md"}


def verify(target_dir: str = None):
    dirs_with_content = {}
    dirs_with_graph = {}
    dirs_without_index = []
    
    root = KNOWLEDGE_ROOT
    if target_dir:
        root = KNOWLEDGE_ROOT / target_dir
    
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, KNOWLEDGE_ROOT).replace("\\", "/")
        
        excluded = False
        for part in Path(rel).parts:
            if part in EXCLUDE_DIRS:
                excluded = True
                break
        if excluded:
            continue
        
        md_files = [f for f in filenames 
                    if f.endswith(".md") and f not in EXCLUDE_FILES]
        if not md_files:
            continue
        
        dirs_with_content[rel] = len(md_files)
        
        if "index.md" in filenames:
            idx_path = os.path.join(dirpath, "index.md")
            with open(idx_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "文件详情与关系图谱" in content:
                    dirs_with_graph[rel] = len(md_files)
        else:
            dirs_without_index.append(rel)
    
    total = len(dirs_with_content)
    covered = len(dirs_with_graph)
    coverage = covered / total * 100 if total > 0 else 0
    
    print("=" * 60)
    print("🔍 知识图谱覆盖率验证")
    print("=" * 60)
    print(f"\n📊 有内容的目录: {total}")
    print(f"✅ 有知识图谱: {covered}")
    print(f"📄 无 index.md: {len(dirs_without_index)}")
    print(f"📈 覆盖率: {coverage:.1f}%")
    
    missing = set(dirs_with_content.keys()) - set(dirs_with_graph.keys())
    if missing:
        print(f"\n⚠️  缺失知识图谱的目录 ({len(missing)}):")
        for d in sorted(missing):
            count = dirs_with_content.get(d, 0)
            has_idx = d not in dirs_without_index
            status = "有index.md但无图谱" if has_idx else "无index.md"
            print(f"   - {d} ({count}个文件, {status})")
    
    if dirs_without_index:
        print(f"\n📄 无 index.md 的目录 ({len(dirs_without_index)}):")
        for d in sorted(dirs_without_index):
            count = dirs_with_content.get(d, 0)
            print(f"   - {d} ({count}个文件)")
    
    print()
    return coverage == 100.0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    success = verify(target)
    sys.exit(0 if success else 1)
