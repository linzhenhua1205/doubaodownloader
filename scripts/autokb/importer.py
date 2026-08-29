"""
导入管线模块

职责: 接收 SourceFile → 分类 → 生成 slug → 写入目标文件 → 归档已处理
"""

import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import (
    KNOWLEDGE_DIR,
    BAK_DIR,
)
from .discover import SourceFile, parse_content
from .classify import classify, generate_slug, generate_frontmatter
from .index_updater import update_index_and_log


# ============================================================
# 导入结果
# ============================================================


class ImportResult:
    """单个文件的导入结果"""

    def __init__(self, source: SourceFile):
        self.source = source
        self.success: bool = False
        self.target_path: Optional[Path] = None
        self.target_dir: str = ""
        self.slug: str = ""
        self.error: str = ""

    def __repr__(self):
        status = "✅" if self.success else "❌"
        return f"<ImportResult {status} {self.source.path.name} → {self.target_path}>"


class BatchResult:
    """批量导入的汇总结果"""

    def __init__(self):
        self.results: list[ImportResult] = []
        self.start_time: str = ""
        self.end_time: str = ""

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if not r.success)

    def add(self, r: ImportResult):
        self.results.append(r)

    def summary(self) -> str:
        lines = [
            f"## 导入结果摘要",
            f"",
            f"| 指标 | 数值 |",
            f"|:-----|:-----|",
            f"| 总计 | {len(self.results)} |",
            f"| ✅ 成功 | {self.success_count} |",
            f"| ❌ 失败 | {self.fail_count} |",
            f"| 开始 | {self.start_time} |",
            f"| 结束 | {self.end_time} |",
            f"",
        ]
        if self.fail_count > 0:
            lines.append("### 失败文件")
            for r in self.results:
                if not r.success:
                    lines.append(f"- `{r.source.path.name}`: {r.error}")
        return "\n".join(lines)


# ============================================================
# 导入管线
# ============================================================


def import_file(
    sf: SourceFile,
    dry_run: bool = False,
    auto_archive: bool = False,
    skip_index: bool = False,
) -> ImportResult:
    """
    导入单个文件到知识库。

    Args:
        sf: 源文件信息
        dry_run: 预览模式，不实际写入
        auto_archive: 导入后自动归档源文件到 bak/
        skip_index: 不更新 index.md/log.md（批量时由调度器统一处理）

    Returns:
        ImportResult
    """
    result = ImportResult(sf)

    try:
        # 1. 确保内容已加载
        if not sf.content:
            sf = parse_content(sf)

        # 2. 分类
        target_dir = classify(sf)
        result.target_dir = target_dir

        # 3. 生成 slug 文件名
        slug = generate_slug(sf)
        result.slug = slug

        # 4. 构建目标路径
        full_dir = KNOWLEDGE_DIR / target_dir
        target_path = full_dir / slug
        result.target_path = target_path

        # 5. 检查是否存在
        if target_path.exists():
            result.error = f"目标文件已存在: {target_path}"
            result.success = False
            return result

        # 6. 组装最终内容
        frontmatter = generate_frontmatter(sf, target_dir)
        final_content = frontmatter + "\n" + sf.content.strip() + "\n"

        # 7. 写入
        if not dry_run:
            full_dir.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(final_content)

        # 8. 更新索引
        if not dry_run and not skip_index:
            title_line = sf.title
            # 从 frontmatter 获取标题
            if frontmatter:
                import re
                m = re.search(r'title: "(.+)"', frontmatter)
                if m:
                    title_line = m.group(1)
            update_index_and_log(
                target_dir=target_dir,
                filename=slug,
                title=title_line,
                source_type=sf.source_type,
                operation="add",
            )

        # 9. 归档源文件
        if auto_archive and not dry_run:
            _archive_source(sf, target_dir)

        result.success = True

    except Exception as e:
        result.error = str(e)
        result.success = False

    return result


def import_batch(
    files: list[SourceFile],
    dry_run: bool = False,
    auto_archive: bool = False,
    batch_name: str = "",
) -> BatchResult:
    """
    批量导入文件。

    Args:
        files: 源文件列表
        dry_run: 预览模式
        auto_archive: 导入后归档源文件
        batch_name: 批次名称（用于日志）

    Returns:
        BatchResult
    """
    batch = BatchResult()
    batch.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, sf in enumerate(files):
        print(f"  [{i+1}/{len(files)}] {sf.path.name} ... ", end="", flush=True)
        result = import_file(sf, dry_run=dry_run, auto_archive=auto_archive, skip_index=True)
        batch.add(result)
        if result.success:
            print(f"✅ → {result.target_path}")
        else:
            print(f"❌ {result.error}")

    batch.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 批量索引更新（汇总写入）
    if not dry_run:
        _write_batch_index(batch, batch_name)

    return batch


# ============================================================
# 辅助函数
# ============================================================


def _archive_source(sf: SourceFile, target_dir: str) -> None:
    """归档已处理的源文件到 bak"""
    date_str = datetime.now().strftime("%Y%m%d")
    archive_subdir = BAK_DIR / f"imported-{date_str}" / target_dir
    archive_subdir.mkdir(parents=True, exist_ok=True)
    dest = archive_subdir / sf.path.name
    shutil.move(str(sf.path), str(dest))


def _write_batch_index(batch: BatchResult, batch_name: str) -> None:
    """批量导入后统一写入 index.md 和 log.md"""
    from .index_updater import update_index_bulk

    entries = []
    for r in batch.results:
        if r.success:
            entries.append({
                "target_dir": r.target_dir,
                "filename": r.slug,
                "title": r.source.title,
                "source_type": r.source.source_type,
            })

    if entries:
        update_index_bulk(entries, batch_name=batch_name or f"批量导入 {len(entries)} 文件")
