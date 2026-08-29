#!/usr/bin/env python3
"""
kb-metadb.py — 知识库内容元数据库构建/查询/更新

基于 sr-006 B-01 建议。遍历 knowledge/ 下所有 .md 文件，
提取标题/摘要/关键词/标签，建立可搜索的 JSON 索引。

功能:
  1. build    — 全量构建元数据库
  2. update   — 增量更新（仅新/修改的文件）
  3. query    — 通过 CLI 查询元数据库
  4. stats    — 元数据统计信息

用法:
  # 全量构建
  python3 scripts/tools/kb-metadb.py build

  # 增量更新
  python3 scripts/tools/kb-metadb.py update

  # 关键词查询
  python3 scripts/tools/kb-metadb.py query --keyword "CXL" --limit 10

  # 目录过滤查询
  python3 scripts/tools/kb-metadb.py query --dir "07_industry-research" --keyword "reliability"

  # 模块统计
  python3 scripts/tools/kb-metadb.py stats

  # 元数据库路径
  python3 scripts/tools/kb-metadb.py build --output knowledge/.metadb/index.json

依赖:
  - extract-index-metadata.py (check/ 下，用于单文件提取)
  - 要求 knowledge/ 目录结构完整
"""
import sys
import os
import json
import argparse
import re
import hashlib
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = REPO_ROOT / 'knowledge'
DEFAULT_METADB = KNOWLEDGE_DIR / '.metadb' / 'index.json'

sys.path.insert(0, str(REPO_ROOT / 'scripts'))
from tools.errorcodes import EC, exit_with

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

NOW = datetime.now()
TIMESTAMP = NOW.strftime('%Y-%m-%d %H:%M:%S')

# ── 排除文件模式 ──
EXCLUDE_PATTERNS = (
    'index.md', 'log.md', 'README.md', 'MIGRATIONS.md', '_search-track.json'
)
EXCLUDE_DIRS = (
    '.metadb', '__pycache__', '.git', 'node_modules', 'bak'
)

# ══════════════════════════════════════════════════════════
#  元数据提取
# ══════════════════════════════════════════════════════════

def extract_metadata(filepath: Path) -> dict:
    """从 .md 文件提取元数据"""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return None

    # 文件信息
    rel_path = filepath.relative_to(KNOWLEDGE_DIR)
    stat = filepath.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')

    # 内容 hash（用于增量检测）
    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    # 提取标题（第一个 # 行）
    title = ""
    summary = ""
    keywords = []
    tags = set()

    lines = content.split('\n')
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not title and line_stripped.startswith('# ') and '#' not in line_stripped[2:4]:
            title = line_stripped[2:].strip()
        if not summary and line_stripped and not line_stripped.startswith('#') \
                and not line_stripped.startswith('>') and not line_stripped.startswith('---'):
            # 取第一段有效正文
            summary = line_stripped[:200]

    # 从文件名和路径推断关键词
    stem = filepath.stem
    if stem and stem != 'index':
        # 文件名转关键词（如 "2026-07-27-gpu-analysis" → ["gpu", "analysis"]）
        parts = re.split(r'[-_\s]', stem)
        keywords.extend([p.lower() for p in parts if len(p) > 2 and not re.match(r'^\d{4}$', p)])

    # 从路径推断领域标签
    path_parts = rel_path.parts
    if len(path_parts) >= 2:
        tags.add(path_parts[0])  # 顶层目录
    if len(path_parts) >= 3:
        tags.add(path_parts[1])  # 子目录

    # 提取 "关键词" 或 "tags" 行
    for line in lines[:30]:  # 只看前30行
        line_s = line.strip().lower()
        if line_s.startswith('标签') or line_s.startswith('tags'):
            parts = re.split(r'[:：,，、\s]+', line_s, maxsplit=1)
            if len(parts) >= 2:
                for tag in re.split(r'[,，、\s/]+', parts[1]):
                    tag = tag.strip().strip('`"\'').lower()
                    if tag and len(tag) > 1:
                        tags.add(tag)
        if line_s.startswith('关键词') or line_s.startswith('keyword'):
            parts = re.split(r'[:：,，、\s]+', line_s, maxsplit=1)
            if len(parts) >= 2:
                for kw in re.split(r'[,，、\s/]+', parts[1]):
                    kw = kw.strip().strip('`"\'').lower()
                    if kw and len(kw) > 1:
                        keywords.append(kw)

    # 行数
    line_count = len(lines)

    return {
        "path": str(rel_path),
        "title": title or filepath.stem,
        "summary": summary[:300] if summary else "",
        "keywords": list(set(keywords)),
        "tags": sorted(tags),
        "lines": line_count,
        "mtime": mtime,
        "hash": content_hash,
    }


# ══════════════════════════════════════════════════════════
#  构建/更新
# ══════════════════════════════════════════════════════════

def build(output_path: Path, verbose: bool = False):
    """全量构建元数据库"""
    if not KNOWLEDGE_DIR.exists():
        exit_with(EC.DIR_NOT_FOUND, f"知识库目录不存在: {KNOWLEDGE_DIR}")

    md_files = []
    for f in KNOWLEDGE_DIR.rglob("*.md"):
        # 排除目录
        if any(excl in f.parts for excl in EXCLUDE_DIRS):
            continue
        if f.name in EXCLUDE_PATTERNS:
            continue
        md_files.append(f)

    total = len(md_files)
    print(f"📄 扫描到 {total} 个 .md 文件，开始提取元数据...")

    entries = []
    errors = 0
    for i, f in enumerate(md_files):
        if verbose and (i+1) % 200 == 0:
            print(f"  进度: {i+1}/{total}")
        meta = extract_metadata(f)
        if meta:
            entries.append(meta)
        else:
            errors += 1

    # 按路径排序
    entries.sort(key=lambda x: x["path"])

    result = {
        "version": 2,
        "built_at": TIMESTAMP,
        "total_files": len(entries),
        "errors": errors,
        "entries": entries,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 压缩版本（仅 path/title/tags 用于快速查询）
    compact = {
        "version": 2,
        "built_at": TIMESTAMP,
        "total_files": len(entries),
        "entries": [
            {"p": e["path"], "t": e["title"], "g": e["tags"], "l": e["lines"]}
            for e in entries
        ],
    }
    compact_path = output_path.with_suffix('.compact.json')
    with open(compact_path, 'w', encoding='utf-8') as f:
        json.dump(compact, f, ensure_ascii=False)

    print(f"✅ 元数据库构建完成")
    print(f"   完整版: {output_path} ({len(entries)} 条目, {os.path.getsize(output_path)//1024}KB)")
    print(f"   精简版: {compact_path} ({os.path.getsize(compact_path)//1024}KB)")
    print(f"   错误: {errors}")

    return result


def update(output_path: Path, verbose: bool = False):
    """增量更新元数据库"""
    if not output_path.exists():
        print(f"📭 元数据库不存在，执行全量构建...")
        return build(output_path, verbose)

    with open(output_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_map = {}
    for e in existing.get("entries", []):
        existing_map[e["path"]] = e

    # 扫描文件
    md_files = []
    for f in KNOWLEDGE_DIR.rglob("*.md"):
        if any(excl in f.parts for excl in EXCLUDE_DIRS):
            continue
        if f.name in EXCLUDE_PATTERNS:
            continue
        md_files.append(f)

    new_count = 0
    updated_count = 0
    errors = 0

    for f in md_files:
        rel_path = str(f.relative_to(KNOWLEDGE_DIR))
        meta = extract_metadata(f)
        if not meta:
            errors += 1
            continue

        if rel_path not in existing_map:
            new_count += 1
            existing["entries"].append(meta)
        elif existing_map[rel_path]["hash"] != meta["hash"]:
            # 内容已修改
            updated_count += 1
            for i, e in enumerate(existing["entries"]):
                if e["path"] == rel_path:
                    existing["entries"][i] = meta
                    break
        # 其他情况跳过（未变化）

    # 检查删除的文件
    current_paths = {str(f.relative_to(KNOWLEDGE_DIR)) for f in md_files}
    deleted = [e for e in existing["entries"] if e["path"] not in current_paths]
    if deleted:
        existing["entries"] = [e for e in existing["entries"] if e["path"] not in {d["path"] for d in deleted}]
        print(f"  已清理 {len(deleted)} 个已删除文件的记录")

    existing["built_at"] = TIMESTAMP
    existing["total_files"] = len(existing["entries"])
    existing["errors"] = errors

    existing["entries"].sort(key=lambda x: x["path"])

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"✅ 增量更新完成")
    print(f"   新增: {new_count}, 更新: {updated_count}, 删除: {len(deleted)}, 错误: {errors}")
    print(f"   总计: {existing['total_files']} 条目")

    return existing


# ══════════════════════════════════════════════════════════
#  查询
# ══════════════════════════════════════════════════════════

def query_metadb(output_path: Path, keyword: str = "", dir_filter: str = "",
                 tag: str = "", limit: int = 30, json_output: bool = False):
    """查询元数据库"""
    if not output_path.exists():
        exit_with(EC.FILE_NOT_FOUND, f"元数据库不存在，请先运行 build: {output_path}")

    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries = data.get("entries", [])
    results = []

    for e in entries:
        score = 0
        matched = False

        # 关键词匹配
        if keyword:
            kw_lower = keyword.lower()
            if kw_lower in e.get("title", "").lower():
                score += 10
                matched = True
            if kw_lower in e.get("summary", "").lower():
                score += 5
                matched = True
            if any(kw_lower in kw for kw in e.get("keywords", [])):
                score += 8
                matched = True
            if any(kw_lower in tag for tag in e.get("tags", [])):
                score += 3
                matched = True
            if kw_lower in e.get("path", "").lower():
                score += 2
                matched = True

        # 目录过滤
        if dir_filter:
            if dir_filter not in e.get("path", ""):
                continue
            score += 1
            matched = True

        # 标签过滤
        if tag:
            if tag not in e.get("tags", []):
                continue
            score += 1
            matched = True

        if (not keyword and not dir_filter and not tag):
            matched = True

        if matched:
            results.append((score, e))

    # 按分数排序
    results.sort(key=lambda x: -x[0])
    results = results[:limit]

    if json_output:
        print(json.dumps([r[1] for r in results], ensure_ascii=False, indent=2))
        return

    if not results:
        print(f"📭 未找到匹配结果")
        return

    print(f"\n🔍 查询结果 ({len(results)} 条)")
    print(f"{'='*60}")
    for score, e in results:
        path = e.get("path", "?")
        title = e.get("title", "?").replace("\n", " ")
        tags = ", ".join(e.get("tags", [])[:5])
        lines = e.get("lines", 0)
        summary = (e.get("summary", "") or "")[:80]
        print(f"\n  📄 {title}")
        print(f"     📍 {path} ({lines}行)")
        if tags:
            print(f"     🏷️  {tags}")
        if summary:
            print(f"     💬 {summary}")
        if keyword:
            print(f"     🔗 匹配度: {score}")


# ══════════════════════════════════════════════════════════
#  统计
# ══════════════════════════════════════════════════════════

def show_stats(output_path: Path):
    """元数据统计"""
    if not output_path.exists():
        exit_with(EC.FILE_NOT_FOUND, f"元数据库不存在: {output_path}")

    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    entries = data.get("entries", [])
    print(f"\n📊 知识库元数据统计")
    print(f"{'='*50}")
    print(f"  构建时间: {data.get('built_at', '?')}")
    print(f"  总文件数: {len(entries)}")

    # 按目录统计
    dir_counts = {}
    dir_lines = {}
    for e in entries:
        path_parts = e["path"].split('/')
        top = path_parts[0] if len(path_parts) >= 1 else "?"
        dir_counts[top] = dir_counts.get(top, 0) + 1
        dir_lines[top] = dir_lines.get(top, 0) + e.get("lines", 0)

    print(f"\n  目录分布:")
    for d in sorted(dir_counts.keys()):
        pct = dir_counts[d] / len(entries) * 100
        print(f"    {d:<30} {dir_counts[d]:>5} 文件 ({pct:5.1f}%)")

    # 标签统计
    tag_counts = {}
    for e in entries:
        for t in e.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1
    top_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:20]

    print(f"\n  热门标签 (Top 20):")
    for tag, count in top_tags:
        print(f"    {tag:<25} {count:>4} 文件")

    # 文件大小分布
    size_dist = {"tiny (<10行)": 0, "small (10-50行)": 0,
                 "medium (50-200行)": 0, "large (200-500行)": 0,
                 "huge (>500行)": 0}
    for e in entries:
        lines = e.get("lines", 0)
        if lines < 10: size_dist["tiny (<10行)"] += 1
        elif lines < 50: size_dist["small (10-50行)"] += 1
        elif lines < 200: size_dist["medium (50-200行)"] += 1
        elif lines < 500: size_dist["large (200-500行)"] += 1
        else: size_dist["huge (>500行)"] += 1

    print(f"\n  文件大小分布:")
    for cat, count in size_dist.items():
        pct = count / len(entries) * 100
        print(f"    {cat:<20} {count:>5} ({pct:5.1f}%)")


# ══════════════════════════════════════════════════════════
#  CLI
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='知识库内容元数据库 — 构建/查询/统计',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', default=str(DEFAULT_METADB),
                        help=f'元数据库路径 (默认: {DEFAULT_METADB})')

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # build
    p_build = subparsers.add_parser("build", help="全量构建元数据库")
    p_build.add_argument("--verbose", action="store_true", help="显示进度")

    # update
    p_update = subparsers.add_parser("update", help="增量更新元数据库")
    p_update.add_argument("--verbose", action="store_true", help="显示进度")

    # query
    p_query = subparsers.add_parser("query", help="查询元数据库")
    p_query.add_argument("--keyword", default="", help="关键词")
    p_query.add_argument("--dir", default="", help="目录过滤")
    p_query.add_argument("--tag", default="", help="标签过滤")
    p_query.add_argument("--limit", type=int, default=30, help="最大返回条数")
    p_query.add_argument("--json", action="store_true", help="JSON 输出")

    # stats
    p_stats = subparsers.add_parser("stats", help="元数据统计")

    args = parser.parse_args()
    output_path = Path(args.output)

    if args.command == "build":
        build(output_path, verbose=args.verbose)
    elif args.command == "update":
        update(output_path, verbose=args.verbose)
    elif args.command == "query":
        query_metadb(output_path, keyword=args.keyword, dir_filter=args.dir,
                     tag=args.tag, limit=args.limit, json_output=args.json)
    elif args.command == "stats":
        show_stats(output_path)
    else:
        parser.print_help()
        exit_with(EC.INVALID_ARGS, "请指定子命令")


if __name__ == "__main__":
    main()
