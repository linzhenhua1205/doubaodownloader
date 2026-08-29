"""
主编排器

职责: 编排完整的导入管线，提供高级接口供 CLI 和将来 API 调用。
"""

from pathlib import Path
from typing import Optional

from .config import IMPORT_DIR, KNOWLEDGE_DIR
from .discover import (
    discover_all,
    discover_by_source,
    discover_one,
    parse_content,
    deduplicate,
    summary as scan_summary,
)
from .importer import import_file, import_batch, BatchResult, ImportResult


# ============================================================
# 管线选项
# ============================================================


class PipelineOptions:
    """管线执行选项"""

    def __init__(
        self,
        source: Optional[str] = None,
        file_path: Optional[str] = None,
        all_sources: bool = False,
        dry_run: bool = False,
        auto_archive: bool = False,
        dedup: bool = True,
        max_files: Optional[int] = None,
    ):
        self.source = source
        self.file_path = file_path
        self.all_sources = all_sources
        self.dry_run = dry_run
        self.auto_archive = auto_archive
        self.dedup = dedup
        self.max_files = max_files


# ============================================================
# 管线执行
# ============================================================


def run_pipeline(opts: PipelineOptions) -> BatchResult:
    """
    执行一次导入管线。

    Pipeline:
        1. 发现文件（全量/按来源/单文件）
        2. 加载内容 + 去重（可选）
        3. 分类 + 写入
        4. 更新索引
        5. 归档（可选）
        6. 返回结果
    """
    print("=" * 60)
    print("  🛠️  知识库导入管线 v1.0")
    print("=" * 60)
    if opts.dry_run:
        print("  ⚠️  预览模式 - 不会实际写入或归档\n")
    print()

    # Step 1: 文件发现
    print("📂 [Step 1/4] 文件发现 ...")
    if opts.file_path:
        files = [discover_one(Path(opts.file_path))] if opts.file_path else []
        files = [f for f in files if f is not None]
    elif opts.source:
        files = discover_by_source(opts.source)
    elif opts.all_sources:
        files = discover_all()
    else:
        files = discover_all()

    if not files:
        print("  ⚠️  未发现任何文件")
        return BatchResult()

    scan_info = scan_summary(files)
    print(f"  ✅ 发现 {scan_info['total']} 个文件 ({scan_info['total_size_mb']}MB)")
    for source_type, count in sorted(scan_info["by_type"].items()):
        print(f"     - {source_type}: {count}")
    print()

    # Step 2: 加载内容 + 去重
    print("📖 [Step 2/4] 内容加载 ...")
    for f in files:
        parse_content(f)

    if opts.dedup:
        before = len(files)
        files = deduplicate(files)
        after = len(files)
        dup_count = before - after
        if dup_count > 0:
            print(f"  🗑️  去重: 移除 {dup_count} 个重复文件 (剩余 {after})")
        else:
            print(f"  ✅ 无重复文件 ({after} 个)")
    print()

    # 限制数量（调试用）
    if opts.max_files and len(files) > opts.max_files:
        print(f"  ⚠️  限制处理前 {opts.max_files} 个文件 (共 {len(files)} 个)")
        files = files[: opts.max_files]
    print()

    # Step 3 + 4: 导入管线
    print("📦 [Step 3/4] 分类与导入 ...")
    batch = import_batch(
        files,
        dry_run=opts.dry_run,
        auto_archive=opts.auto_archive,
        batch_name=f"pipe_{opts.source or 'all'}",
    )
    print()
    if opts.dry_run:
        print(f"  📋 预览完成，共 {len(batch.results)} 个文件")
    else:
        print(f"  ✅ 导入完成: {batch.success_count} 成功, {batch.fail_count} 失败")
    print()

    # Step 5: 分类统计
    print("📊 [Step 4/4] 分类统计 ...")
    target_dirs: dict[str, int] = {}
    for r in batch.results:
        if r.success:
            target_dirs[r.target_dir] = target_dirs.get(r.target_dir, 0) + 1
    if target_dirs:
        for d, c in sorted(target_dirs.items(), key=lambda x: -x[1]):
            print(f"  📁 {d}: {c}")
    print()

    print("=" * 60)
    return batch
