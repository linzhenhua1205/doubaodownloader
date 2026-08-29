#!/usr/bin/env python3
"""
CLI 入口: 知识库导入管线

用法:
    # 全量导入
    python scripts/autokb/run_pipeline.py --all

    # 指定来源
    python scripts/autokb/run_pipeline.py --source doubao

    # 指定文件
    python scripts/autokb/run_pipeline.py --file import/md/some-file.md

    # 预览模式
    python scripts/autokb/run_pipeline.py --all --dry-run

    # 限制文件数（调试用）
    python scripts/autokb/run_pipeline.py --source md --max 10

    # 导入后归档源文件
    python scripts/autokb/run_pipeline.py --all --archive
"""

import sys
import argparse
from pathlib import Path

from scripts.shared.workspace import WORKSPACE_ROOT
sys.path.insert(0, str(WORKSPACE_ROOT))

from scripts.autokb.pipeline import run_pipeline, PipelineOptions


def main():
    parser = argparse.ArgumentParser(
        description="知识库导入管线 - 从 import/ 到 knowledge/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # 互斥的来源参数
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--all", "-a",
        action="store_true",
        dest="all_sources",
        help="导入所有来源",
    )
    source_group.add_argument(
        "--source", "-s",
        type=str,
        choices=["doubao", "doubao20260523", "fetched_markdown", "md"],
        help="指定来源目录",
    )
    source_group.add_argument(
        "--file", "-f",
        type=str,
        help="指定单个文件路径",
    )

    # 执行选项
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="预览模式，不实际写入",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="导入后归档源文件到 tmp/bak/",
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="禁用去重",
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=None,
        help="最大处理文件数（调试用）",
    )

    args = parser.parse_args()

    # 默认行为：如果未指定任何来源，则全量扫描
    if not args.all_sources and not args.source and not args.file:
        args.all_sources = True

    opts = PipelineOptions(
        source=args.source,
        file_path=args.file,
        all_sources=args.all_sources,
        dry_run=args.dry_run,
        auto_archive=args.archive,
        dedup=not args.no_dedup,
        max_files=args.max,
    )

    batch = run_pipeline(opts)

    # 输出摘要
    if batch.results:
        print()
        print(batch.summary())

    # 退出码
    if batch.fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
