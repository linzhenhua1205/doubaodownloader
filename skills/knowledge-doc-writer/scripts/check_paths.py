#!/usr/bin/env python3
"""
路径验证脚本 - 知识库文档创建前的路径、数据源、目录结构检查

功能:
  - 验证文档输出路径合法性和父目录存在
  - 检查目标目录及上级的 index.md / log.md
  - 检查知识库数据源（按模块统计文件）
  - 统计 import/ 下的相关文件
  - 搜索知识库中与主题关键词匹配的文件
"""
import os
import sys
import re
import argparse

WORKSPACE = os.environ.get("COW_HOME",
    os.path.join(os.environ.get("HOME", "/home/lzh"), "cow"))

# 知识库核心搜索路径（通用版）
DEFAULT_KB_PATHS = [
    f"{WORKSPACE}/knowledge/02_rd/",
    f"{WORKSPACE}/knowledge/03_AI/",
    f"{WORKSPACE}/knowledge/01_survey/",
]

# import 数据源路径
IMPORT_PATHS = [
    # knowledge/import/ 已不存在（已整合到标准模块），保留 import/ 做素材检查
    f"{WORKSPACE}/import/",
]


def check_document_path(document_path):
    """验证文档输出路径"""
    if not document_path:
        print("❌ 错误: 未指定文档路径")
        return False

    abs_path = os.path.abspath(document_path)

    # 检查父目录是否存在
    parent = os.path.dirname(abs_path)
    if not os.path.exists(parent):
        print(f"❌ 错误: 父目录不存在: {parent}")
        print(f"   建议: mkdir -p {parent}")
        return False

    print(f"✅ 目标目录: {parent}")

    # 检查 index.md 是否存在
    index_path = os.path.join(parent, "index.md")
    if not os.path.exists(index_path):
        current = parent
        while current and current != os.path.dirname(current):
            parent_index = os.path.join(current, "index.md")
            if os.path.exists(parent_index):
                print(f"⚠️  当前目录无 index.md, 使用上级: {parent_index}")
                break
            current = os.path.dirname(current)
        else:
            print("⚠️  未找到 index.md, 创建文档后需要手动更新")
    else:
        print(f"✅ index.md 存在: {index_path}")

    # 检查 log.md 是否存在
    log_path = os.path.join(parent, "log.md")
    if os.path.exists(log_path):
        print(f"✅ log.md 存在: {log_path}")
    else:
        current = parent
        while current and current != os.path.dirname(current):
            parent_log = os.path.join(current, "log.md")
            if os.path.exists(parent_log):
                print(f"⚠️  当前目录无 log.md, 使用上级: {parent_log}")
                break
            current = os.path.dirname(current)
        else:
            print("⚠️  未找到 log.md, 创建文档后需要手动更新")

    print(f"\n📋 文档将保存至: {abs_path}")
    return True


def check_knowledge_sources(keywords=None):
    """检查知识库数据源，按模块统计文件"""
    workspace_kb = f"{WORKSPACE}/knowledge"
    
    if not os.path.exists(workspace_kb):
        print(f"❌ 知识库路径不存在: {workspace_kb}")
        return

    print(f"\n📚 知识库数据源检查 (基准: {workspace_kb}):")
    print()

    # 核心模块统计
    for path in DEFAULT_KB_PATHS:
        if os.path.exists(path):
            md_count = 0
            for root, dirs, files in os.walk(path):
                md_files = [f for f in files if f.endswith('.md')]
                md_count += len(md_files)

            # 显示子目录分布
            rel = os.path.relpath(path, workspace_kb)
            print(f"  📁 {rel}/ ({md_count} 个 .md 文件)")
            for root, dirs, files in os.walk(path):
                if root == path:
                    for d in sorted(dirs):
                        d_md = len([f for f in os.listdir(os.path.join(root, d))
                                   if f.endswith('.md')])
                        print(f"     ├── {d}/ ({d_md} files)")
        else:
            print(f"  ❌ {os.path.relpath(path, workspace_kb)}/ (不存在)")

    # import 数据源检查
    print(f"\n📥 import 数据源检查:")
    for ipath in IMPORT_PATHS:
        if os.path.exists(ipath):
            md_count = len([f for f in os.listdir(ipath) if f.endswith('.md')])
            rel = os.path.relpath(ipath, WORKSPACE)
            print(f"  ✅ {rel}/ ({md_count} files)")
        else:
            print(f"  ❌ {os.path.relpath(ipath, WORKSPACE)}/ (不存在)")

    # 关键词搜索（可选）
    if keywords:
        search_keywords = [k.strip() for k in keywords.split(",")]
        print(f"\n🔍 关键词搜索: {search_keywords}")
        for path in DEFAULT_KB_PATHS:
            if not os.path.exists(path):
                continue
            for kw in search_keywords:
                try:
                    result = os.popen(
                        f'find {path} -name "*.md" | xargs grep -li "{kw}" 2>/dev/null | head -20'
                    ).read().strip()
                    if result:
                        files_found = result.split('\n')
                        print(f"  [{kw}] 在 {os.path.relpath(path, workspace_kb)}/ 找到 {len(files_found)} 个文件:")
                        for f in files_found[:5]:
                            print(f"    → {os.path.relpath(f, workspace_kb)}")
                        if len(files_found) > 5:
                            print(f"    ... 还有 {len(files_found)-5} 个")
                except Exception as e:
                    print(f"  [{kw}] 搜索出错: {e}")

    # import 关键词搜索
    if keywords:
        for ipath in IMPORT_PATHS:
            if not os.path.exists(ipath):
                continue
            for kw in search_keywords:
                try:
                    result = os.popen(
                        f'find {ipath} -name "*.md" | xargs grep -li "{kw}" 2>/dev/null | head -10'
                    ).read().strip()
                    if result:
                        files_found = result.split('\n')
                        print(f"  [{kw}] 在 import/ 找到 {len(files_found)} 个文件")
                except:
                    pass

    # 全 KB 规模统计
    print(f"\n📊 知识库规模:")
    total_md = 0
    for root, dirs, files in os.walk(workspace_kb):
        md_files = [f for f in files if f.endswith('.md')]
        total_md += len(md_files)
    print(f"  总计: {total_md} 个 .md 文件")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="知识库文档路径与数据源检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --document knowledge/02_rd/07_reports/my-report.md
  %(prog)s --document knowledge/03_AI/my-analysis.md --check-sources
  %(prog)s --check-sources --keywords "PCIe,CXL,interconnect"
  %(prog)s --document path/to/doc.md --keywords "BMC,FRU,Redfish"
        """)
    parser.add_argument("--document", help="文档输出路径")
    parser.add_argument("--check-sources", action="store_true",
                       help="检查知识库数据源")
    parser.add_argument("--keywords", help="搜索关键词（逗号分隔）")

    args = parser.parse_args()

    if args.document:
        check_document_path(args.document)

    if args.check_sources or args.keywords:
        check_knowledge_sources(keywords=args.keywords)

    if not args.document and not args.check_sources and not args.keywords:
        parser.print_help()
        print()
        print("=== 快速用法 ===")
        print("  检查特定文档的路径:")
        print("    python3 check_paths.py --document knowledge/02_rd/07_reports/my-report.md")
        print()
        print("  检查路径 + 搜索关键词:")
        print("    python3 check_paths.py --document path/to/doc.md --keywords \"PCIe,CXL\"")
