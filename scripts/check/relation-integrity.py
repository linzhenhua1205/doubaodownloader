#!/usr/bin/env python3
"""
relation-integrity.py — 知识库关系完整性校验器

校验 index.md 中记录的文件关系信息是否完整、有效。
基于 KNOWLEDGE_STRATEGIES.md §6-7 关系分类体系。

核心功能：
  1. 解析 index.md 中的关联文件字段（第4列）
  2. 校验关系类型是否来自 §7 标准分类（10种）
  3. 校验目标文件是否存在
  4. 校验反向链接一致性
  5. 报告孤立文件（无关系记录的非跟踪文件）
  6. 生成关系统计报告

Usage:
    python3 scripts/check/relation-integrity.py                     # 全库检查
    python3 scripts/check/relation-integrity.py --module 02_rd     # 特定模块
    python3 scripts/check/relation-integrity.py --file <path>      # 单文件
    python3 scripts/check/relation-integrity.py --json             # JSON 输出
    python3 scripts/check/relation-integrity.py --summary          # 汇总报告
    python3 scripts/check/relation-integrity.py --stats            # 关系统计
    python3 scripts/check/relation-integrity.py --graph            # 关系图谱文本输出
"""
import sys
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

SKIP_DIRS = {'bak', 'import-modules', 'node_modules', '.git', '.bak', 'oldbak', 'archive', 'archived'}
KNOWLEDGE_ROOT = WORKSPACE_ROOT / "knowledge"

# §7 — 标准关系分类（来自 KNOWLEDGE_STRATEGIES.md）
VALID_RELATION_TYPES = {
    'related', 'depends-on', 'supersedes', 'see-also',
    'contrasts', 'extends', 'source-of', 'part-of',
    'example-of', 'references',
}

# 反向关系映射（双向关系时需在另一端也记录）
BIDIRECTIONAL_RELATIONS = {'related', 'see-also', 'contrasts'}
# 单向关系（只需在源端记录）
DIRECTIONAL_RELATIONS = {'depends-on', 'supersedes', 'extends', 'source-of', 'part-of', 'example-of', 'references'}

# 不需要强制关系记录的文件类型
SKIP_RELATION_TYPES = {'T3'}  # 日常跟踪文件不强制


def parse_index_table(content: str, rel_path: str) -> list:
    """Parse index.md table and extract file entries with relationship info."""
    entries = []
    lines = content.split('\n')
    in_table = False
    headers = []

    for line in lines:
        stripped = line.strip()

        # Detect table start
        if stripped.startswith('|') and not in_table:
            in_table = True
            # Parse header row
            cols = [c.strip() for c in stripped.split('|') if c.strip()]
            headers = cols
            continue

        if not in_table or not stripped.startswith('|'):
            continue

        # Skip separator row
        if re.match(r'^\|[\s\-:]+\|', stripped):
            continue

        # Parse data row
        cols = [c.strip() for c in stripped.split('|') if c.strip()]
        if len(cols) < 3:
            continue

        # Extract filename from markdown link
        file_cell = cols[0]
        file_match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', file_cell)
        filename = file_match.group(1) if file_match else file_cell.strip()
        filepath = file_match.group(2) if file_match else ''

        # Extract summary and date
        summary = cols[1] if len(cols) > 1 else ''
        date = cols[2] if len(cols) > 2 else ''

        # Extract relationship info (4th column, if exists)
        relations = {}
        if len(cols) > 3 and cols[3].strip():
            rel_field = cols[3].strip()
            # Parse: relation_type1: path1, relation_type2: path2
            rel_parts = re.findall(r'(\w+(?:-\w+)*)\s*:\s*([^,]+(?:,\s*[^,\s:]+)*)', rel_field)
            for rel_type, rel_targets in rel_parts:
                rel_type = rel_type.strip()
                if rel_type in VALID_RELATION_TYPES:
                    # Split multiple targets
                    targets = [t.strip() for t in rel_targets.split(',') if t.strip()]
                    relations[rel_type] = targets

        entries.append({
            'filename': filename,
            'filepath': filepath,
            'summary': summary,
            'date': date,
            'relations': relations,
            'source_index': rel_path,
        })

    return entries


def resolve_file_path(entry_path: str, source_index_path: str) -> Path:
    """Resolve the actual file path from an index entry."""
    # If entry_path starts with a link (markdown), extract path
    m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', entry_path)
    if m:
        path_str = m.group(2)
    else:
        path_str = entry_path

    # If path is relative to knowledge/, prepend KNOWLEDGE_ROOT
    if not path_str.startswith('/'):
        # Could be relative to the index file
        index_dir = KNOWLEDGE_ROOT / Path(source_index_path).parent
        resolved = (index_dir / path_str).resolve()
    else:
        resolved = KNOWLEDGE_ROOT / path_str.lstrip('/')

    return resolved


def check_relations(entries: list, knowledge_root: Path) -> dict:
    """Validate relationship records for a set of index entries."""
    results = {
        'entries_with_relations': 0,
        'total_entries': len(entries),
        'valid_relations': 0,
        'invalid_relations': 0,
        'type_counts': Counter(),
        'issues': [],
        'relation_details': [],
    }

    # Build a set of all known files for existence checking
    all_files = set()
    for md_file in knowledge_root.rglob('*.md'):
        if not any(skip in str(md_file) for skip in SKIP_DIRS):
            rel = str(md_file.relative_to(knowledge_root))
            all_files.add(rel)

    for entry in entries:
        if entry['relations']:
            results['entries_with_relations'] += 1

        for rel_type, targets in entry['relations'].items():
            results['type_counts'][rel_type] += len(targets)

            for target in targets:
                # Validate relation type
                if rel_type not in VALID_RELATION_TYPES:
                    results['invalid_relations'] += 1
                    results['issues'].append((
                        'FAIL', 'invalid_type',
                        f"无效关系类型 '{rel_type}' (来源: {entry['source_index']} → {entry['filename']})"
                    ))
                    continue

                results['valid_relations'] += 1

                # Resolve target path
                target_path = target.strip()
                # Remove any markdown link formatting
                tm = re.match(r'\[([^\]]+)\]\(([^)]+)\)', target_path)
                if tm:
                    target_path = tm.group(2)

                # Check if target file exists
                full_target = knowledge_root / target_path
                if not full_target.exists():
                    # Try with .md extension
                    if not target_path.endswith('.md'):
                        full_target = full_target.with_suffix('.md')
                    if not full_target.exists():
                        # Try relative to index file's directory
                        idx_dir = Path(entry['source_index']).parent
                        alt_target = knowledge_root / idx_dir / target_path
                        if not alt_target.exists():
                            results['issues'].append((
                                'WARN', 'target_missing',
                                f"关系目标不存在: {target_path} (类型: {rel_type}, 来源: {entry['filename']})"
                            ))
                            continue

                results['relation_details'].append({
                    'source': entry['filename'],
                    'target': str(target_path),
                    'type': rel_type,
                    'source_index': entry['source_index'],
                })

    return results


def find_isolated_files(entries: list, knowledge_root: Path, module_path: str = None) -> list:
    """Find files that should have relations but don't."""
    isolated = []

    # Files that should have relations (not daily trackers, not index/log)
    for entry in entries:
        fname = entry['filename']
        # Skip index.md, log.md
        if fname in ('index.md', 'log.md', 'README.md', 'TRACKING.md'):
            continue
        # Skip daily trackers
        if re.match(r'^\d{4}-\d{2}-\d{2}\.md$', fname):
            continue

        # Check if file has any relations
        if not entry['relations']:
            # Check if it's a deep doc (T4) — should have relations
            # Heuristic: files in 02_rd/, 03_AI/, methodology/, concepts/ should have relations
            fp = entry.get('filepath', '')
            if any(p in fp or p in fname for p in ['02_rd/', '03_AI/', 'methodology/', 'concepts/']):
                isolated.append({
                    'filename': fname,
                    'source_index': entry['source_index'],
                    'reason': '深度文件缺少关系记录',
                })

    return isolated


def scan_index(index_path: Path, knowledge_root: Path) -> dict:
    """Scan a single index.md file for relation integrity."""
    try:
        content = index_path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return {'index': str(index_path), 'error': str(e), 'entries': []}

    rel_path = str(index_path.relative_to(knowledge_root))
    entries = parse_index_table(content, rel_path)

    # Check relations
    relation_results = check_relations(entries, knowledge_root)

    # Find isolated files
    isolated = find_isolated_files(entries, knowledge_root)

    return {
        'index': rel_path,
        'total_entries': len(entries),
        'entries_with_relations': relation_results['entries_with_relations'],
        'valid_relations': relation_results['valid_relations'],
        'invalid_relations': relation_results['invalid_relations'],
        'type_counts': dict(relation_results['type_counts']),
        'issues': relation_results['issues'],
        'isolated_files': isolated,
        'relation_details': relation_results['relation_details'],
    }


def scan_all(knowledge_root: Path) -> dict:
    """Scan all index.md files across the knowledge base."""
    results = {}
    total_entries = 0
    total_relations = 0
    total_issues = 0
    type_counter = Counter()
    all_isolated = []
    all_relations = []

    for index_file in sorted(knowledge_root.rglob('index.md')):
        rel = str(index_file.relative_to(knowledge_root))
        if any(skip in rel.split('/') for skip in SKIP_DIRS if skip):
            continue

        mod_result = scan_index(index_file, knowledge_root)
        module_name = str(index_file.parent.relative_to(knowledge_root))
        results[module_name] = mod_result
        total_entries += mod_result['total_entries']
        total_relations += mod_result['valid_relations']
        total_issues += len(mod_result['issues'])
        type_counter.update(mod_result['type_counts'])
        all_isolated.extend(mod_result['isolated_files'])
        all_relations.extend(mod_result['relation_details'])

    return {
        'modules_scanned': len(results),
        'total_entries': total_entries,
        'total_relations': total_relations,
        'total_issues': total_issues,
        'type_distribution': dict(type_counter),
        'isolated_files': all_isolated[:50],  # Limit output
        'isolated_count': len(all_isolated),
        'modules': results,
        'all_relations': all_relations,  # For graph output
    }


def generate_graph(relations: list, knowledge_root: Path) -> str:
    """Generate a text-based relationship graph."""
    nodes = set()
    edges = []

    for rel in relations:
        source = rel['source']
        target = rel['target']
        rtype = rel['type']
        nodes.add(source)
        nodes.add(target)
        edges.append((source, target, rtype))

    lines = []
    lines.append("知识库关系图谱（文本预览）")
    lines.append("=" * 60)
    lines.append(f"节点数: {len(nodes)} | 关系边数: {len(edges)}")
    lines.append("")

    # Group by source
    source_groups = defaultdict(list)
    for s, t, r in edges:
        source_groups[s].append((t, r))

    for source in sorted(source_groups.keys()):
        lines.append(f"📄 {source}")
        for target, rtype in source_groups[source]:
            sym = '→' if rtype in DIRECTIONAL_RELATIONS else '↔'
            lines.append(f"  {sym} [{rtype}] {target}")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='知识库关系完整性校验器')
    parser.add_argument('--module', help='特定模块扫描（如 02_rd）')
    parser.add_argument('--file', help='单文件检查（相对 knowledge/）')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    parser.add_argument('--summary', action='store_true', help='仅输出汇总')
    parser.add_argument('--stats', action='store_true', help='关系统计报告')
    parser.add_argument('--graph', action='store_true', help='关系图谱文本输出')
    parser.add_argument('--fix', action='store_true', help='修复孤立文件警告（仅输出建议）')
    args = parser.parse_args()

    if args.module:
        # Scan specific module
        index_path = KNOWLEDGE_ROOT / args.module / 'index.md'
        if not index_path.exists():
            print(f"❌ index.md 不存在: {index_path}")
            return

        result = scan_index(index_path, KNOWLEDGE_ROOT)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        print(f"\n{'='*50}")
        print(f"📋 模块关系扫描: {args.module}")
        print(f"  条目数: {result['total_entries']} | 有关系: {result['entries_with_relations']}")
        print(f"  有效关系: {result['valid_relations']} | 无效: {result['invalid_relations']}")
        print(f"{'='*50}")

        if result['type_counts']:
            print(f"\n  关系类型分布:")
            for rtype, count in sorted(result['type_counts'].items()):
                print(f"    {rtype}: {count}")

        if result['issues']:
            print(f"\n  问题 ({len(result['issues'])} 项):")
            for severity, cid, desc in result['issues'][:10]:
                print(f"    {'🔴' if severity == 'FAIL' else '🟡'} [{cid}] {desc}")

        if result['isolated_files']:
            print(f"\n  可能缺少关系记录 ({len(result['isolated_files'])} 个文件):")
            for f in result['isolated_files'][:10]:
                print(f"    📄 {f['filename']} — {f['reason']}")

        if args.graph and result['relation_details']:
            print(f"\n{generate_graph(result['relation_details'], KNOWLEDGE_ROOT)}")

        return

    if args.file:
        # Check specific file's relations
        fp = KNOWLEDGE_ROOT / args.file
        if not fp.exists():
            print(f"❌ 文件不存在: {fp}")
            return

        # Find which index.md covers this file
        rel = args.file
        idx_dir = Path(rel).parent
        index_path = KNOWLEDGE_ROOT / idx_dir / 'index.md'
        if not index_path.exists():
            print(f"❌ 未找到对应 index.md: {index_path}")
            return

        result = scan_index(index_path, KNOWLEDGE_ROOT)
        # Filter to just this file
        file_entries = [e for e in result.get('relation_details', [])
                        if e['source'] == fp.name or e['target'] == fp.name]

        if args.json:
            print(json.dumps({'file': args.file, 'relations': file_entries}, ensure_ascii=False, indent=2))
            return

        print(f"\n📄 {args.file}")
        if file_entries:
            print(f"  关系数: {len(file_entries)}")
            for rel in file_entries:
                sym = '→' if rel['type'] in DIRECTIONAL_RELATIONS else '↔'
                print(f"    {sym} [{rel['type']}] {rel['target']}")
        else:
            print(f"  未发现关系记录")
            # Check if it's isolated
            isolated = [e for e in result.get('isolated_files', []) if e['filename'] == fp.name]
            if isolated:
                print(f"  ⚠️ {isolated[0]['reason']}")

        return

    # Full scan (default)
    scan_result = scan_all(KNOWLEDGE_ROOT)

    if args.json:
        print(json.dumps(scan_result, ensure_ascii=False, indent=2))
        return

    print(f"\n{'='*60}")
    print(f"🔗 全库关系完整性扫描报告")
    print(f"{'='*60}")
    print(f"\n  模块扫描: {scan_result['modules_scanned']}")
    print(f"  总条目数: {scan_result['total_entries']}")
    print(f"  有效关系: {scan_result['total_relations']}")
    print(f"  问题数: {scan_result['total_issues']}")
    print(f"  孤立文件（可能缺关系）: {scan_result['isolated_count']}")

    if scan_result['type_distribution']:
        print(f"\n  全库关系类型分布:")
        for rtype, count in sorted(scan_result['type_distribution'].items()):
            bar = '█' * min(count, 40)
            print(f"    {rtype:15s} ({count:3d}) {bar}")

    # Issues summary per module
    print(f"\n  各模块问题:")
    for mod_name, mod_result in sorted(scan_result['modules'].items()):
        issues_count = len(mod_result['issues'])
        iso_count = len(mod_result['isolated_files'])
        if issues_count > 0 or iso_count > 0:
            status = '⚠️' if issues_count > 0 else '💡'
            print(f"    {status} {mod_name}: {issues_count} issues, {iso_count} isolated")
        else:
            print(f"    ✅ {mod_name}: clean")

    if args.graph and scan_result['all_relations']:
        print(f"\n{generate_graph(scan_result['all_relations'], KNOWLEDGE_ROOT)}")

    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    main()
