#!/usr/bin/env python3
"""
路径验证脚本 - 检查目标路径是否合法、index.md和log.md是否存在
"""
import os
import sys
import argparse


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
        return False
    
    print(f"✅ 目标目录: {parent}")
    
    # 检查 index.md 是否存在
    index_path = os.path.join(parent, "index.md")
    if not os.path.exists(index_path):
        # 向上搜索 index.md
        current = parent
        while current != os.path.dirname(current):
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
        # 向上搜索
        current = parent
        while current != os.path.dirname(current):
            parent_log = os.path.join(current, "log.md")
            if os.path.exists(parent_log):
                print(f"⚠️  当前目录无 log.md, 使用上级: {parent_log}")
                break
            current = os.path.dirname(current)
        else:
            print("⚠️  未找到 log.md, 创建文档后需要手动更新")
    
    print(f"\n📋 文档将保存至: {abs_path}")
    return True


def check_knowledge_sources():
    """检查知识库中相关数据源"""
    workspace = os.environ.get("HOME", "/home/lzh") + "/cow/knowledge"
    
    sources_found = []
    
    # 搜索相关路径
    search_paths = [
        f"{workspace}/02_rd/03_hardware/",
        f"{workspace}/02_rd/07_reports/",
        f"{workspace}/01_survey/bmc-system/",
        f"{workspace}/03_AI/tech-research-notes/notes-summary.md",
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            sources_found.append(f"✅ {path}")
        else:
            sources_found.append(f"❌ {path} (不存在)")
    
    print("\n📚 知识库数据源检查:")
    for s in sources_found:
        print(f"  {s}")
    
    # 统计文件
    print("\n📊 知识库统计:")
    for root, dirs, files in os.walk(workspace):
        md_files = [f for f in files if f.endswith('.md')]
        if md_files:
            print(f"  {root[len(workspace)+1:]}: {len(md_files)} 个 md 文件")
        if len([f for f in files if 'FRU' in f or 'fru' in f or 'CMDB' in f or 'cmdb' in f or 'IPMI' in f or 'ipmi' in f or 'DCMI' in f or 'asset' in f or '资产管理' in f]):
            print(f"    ⚡ 包含资产管理相关内容")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="检查文档路径和数据源")
    parser.add_argument("--document", help="文档输出路径")
    parser.add_argument("--check-sources", action="store_true", help="检查知识库数据源")
    
    args = parser.parse_args()
    
    if args.document:
        check_document_path(args.document)
    
    if args.check_sources:
        check_knowledge_sources()
    
    if not args.document and not args.check_sources:
        parser.print_help()
