#!/usr/bin/env python3
"""
mv-knowledge — 知识库文件迁移 CLI

将文件从一个 knowledge/ 目录迁移到另一个，自动处理：
  1. mv 移动文件
  2. 更新源目录 index.md（删除条目）+ log.md（记录迁出）
  3. 更新目标目录 index.md（添加条目）+ log.md（记录迁入）
  4. 若跨 knowledge/ 顶层模块，更新 knowledge/README.md 导航/统计
  5. 运行 link-fixer.py --auto 自动修复交叉引用
  6. 记录迁移到 knowledge/MIGRATIONS.md

Usage:
    python3 scripts/tools/mv-knowledge.py <src> <dst_dir>
    python3 scripts/tools/mv-knowledge.py <src1> <src2> <dst_dir>
    python3 scripts/tools/mv-knowledge.py knowledge/01_survey/old.md knowledge/07_industry-research/
    python3 scripts/tools/mv-knowledge.py --dry-run <src> <dst_dir>
    python3 scripts/tools/mv-knowledge.py --no-fix-links <src> <dst_dir>
"""
import sys
import os
import re
import argparse
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_DIR = REPO_ROOT / 'knowledge'
MIGRATIONS_FILE = KNOWLEDGE_DIR / 'MIGRATIONS.md'

# 2026-08-03 治理决策: 以下模块的分布式 index.md/log.md 已废弃，
# 统一由 knowledge/index.md（kb-global-index.py）+ knowledge/log.md（kb-global-log.py）管理。
# 仅 01_survey/ 与 weekly-reports/ 保留分布式机制。
GLOBAL_INDEX_MODULES = {'02_rd', '03_AI', '04_person', '05_tools', '06_others', '07_industry-research'}


def uses_global_index(p: Path) -> bool:
    """目录是否属于全局索引机制模块（其 index/log 已废弃，迁移时跳过局部更新）。"""
    try:
        rel = p.relative_to(KNOWLEDGE_DIR)
    except ValueError:
        return False
    return bool(rel.parts) and rel.parts[0] in GLOBAL_INDEX_MODULES
LINK_FIXER = REPO_ROOT / 'scripts' / 'check' / 'link-fixer.py'
NOW = datetime.now()
DATE_STR = NOW.strftime('%Y-%m-%d')
TIMESTAMP = NOW.strftime('%Y-%m-%d %H:%M')


def log(msg, dry_run=False):
    prefix = '🔷 DRY-RUN: ' if dry_run else ''
    print(f'{prefix}{msg}')


def run(cmd, dry_run=False, capture=False):
    if dry_run:
        log(f'[would run] {" ".join(cmd)}', dry_run=True)
        return ''
    try:
        r = subprocess.run(cmd, capture_output=capture, text=True, check=False)
        if r.returncode != 0:
            log(f'⚠️ 命令返回 {r.returncode}: {" ".join(cmd)}')
            if r.stderr:
                log(f'  stderr: {r.stderr.strip()}')
        return r.stdout.strip() if capture else ''
    except FileNotFoundError:
        log(f'❌ 命令未找到: {cmd[0]}')
        return ''


# ── 文件头提取 ──────────────────────────────────────────────

def extract_title(path):
    """从 .md 文件提取 H1 标题"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# ') and not line.startswith('# '):
                    return line[2:].strip()
                if line.startswith('# '):
                    return line[2:].strip()
    except Exception:
        pass
    return path.stem


def extract_summary(path):
    """从 .md 文件提取一句话摘要（> 或 H1 后第一段）"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('> '):
                return line[2:].strip()[:60]
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('>') and not line.startswith('---'):
                return line[:60]
    except Exception:
        pass
    return path.stem


# ── index.md 操作 ─────────────────────────────────────────────

def update_index_remove(path, filename, dry_run=False):
    """从 index.md 中删除指向 filename 的条目"""
    if not path.exists():
        log(f'  ⚠️ index.md 不存在: {path}', dry_run)
        return
    content = path.read_text(encoding='utf-8')
    # 匹配表格行: | [`filename`](path/filename.md) | ... |
    escaped = re.escape(filename)
    pattern = re.compile(
        r'^\|.*\[' + escaped.replace(r'\.md', r'(?:\.md)?') + r'\]\([^)]*' +
        re.escape(filename) + r'\).*\|.*$',
        re.MULTILINE
    )
    new_content = pattern.sub('', content)
    # 也匹配裸链接行
    pattern2 = re.compile(
        r'^\|.*\(' + re.escape(filename) + r'\).*\|.*$', re.MULTILINE
    )
    new_content = pattern2.sub('', new_content)
    # 清理多余空行
    new_content = re.sub(r'\n{3,}', '\n\n', new_content)

    if new_content != content:
        if not dry_run:
            path.write_text(new_content, encoding='utf-8')
            log(f'  ✅ 从 {path.name} 删除 {filename} 条目')
        else:
            log(f'  📝 会从 {path.name} 删除 {filename} 条目', dry_run=True)
    else:
        log(f'  ℹ️ 未在 {path.name} 中找到 {filename} 条目（可能无表格条目）', dry_run)


def update_index_add(path, filename, title, summary, dry_run=False):
    """向 index.md 添加文件条目"""
    if not path.exists():
        log(f'  ⚠️ index.md 不存在: {path}', dry_run)
        return

    content = path.read_text(encoding='utf-8')
    link = f'[{title}]({filename})'

    # 查找表格区域 — 找最后一个包含 | 的行
    lines = content.split('\n')
    last_table_line = -1
    in_table = False
    for i, line in enumerate(lines):
        if line.strip().startswith('|') and '---' not in line:
            in_table = True
            last_table_line = i
        elif in_table and not line.strip().startswith('|'):
            break  # 表格结束

    if last_table_line >= 0:
        entry = f'| [`{title}`]({filename}) | {summary} |'
        insert_pos = last_table_line + 1
        lines.insert(insert_pos, entry)
        new_content = '\n'.join(lines)
        if not dry_run:
            path.write_text(new_content, encoding='utf-8')
            log(f'  ✅ 向 {path.name} 添加 {filename} 条目')
        else:
            log(f'  📝 会向 {path.name} 添加 {filename} 条目', dry_run=True)
    else:
        log(f'  ⚠️ 未在 {path.name} 中找到表格区域，需手动添加', dry_run)


# ── log.md 操作 ─────────────────────────────────────────────

def update_log(path, entry, dry_run=False):
    """向 log.md 添加日志条目"""
    if not path.exists():
        # 2026-08-19 起全库无分布式 log.md：禁止新建子目录 log，迁移登记请走根 knowledge/log.md（kb-log-append.py）
        log(f'  ⚠️ log.md 不存在: {path}（2026-08-19 起子目录不再维护 log.md，登记走全局 knowledge/log.md）', dry_run)
        return

    content = path.read_text(encoding='utf-8')

    # 检查是否已有今天的日期标题
    date_header = f'## {DATE_STR}'
    if date_header in content:
        # 在日期标题后插入
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == date_header and not inserted:
                # 找到日期标题，在第一个空行后插入新条目
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                # 在 j 位置插入空行和条目
                if not lines[i+1].strip().startswith('-'):
                    new_lines.insert(j, '')
                    new_lines.insert(j+1, f'- {entry}')
                else:
                    new_lines.insert(j, f'- {entry}')
                inserted = True
        new_content = '\n'.join(new_lines)
    else:
        # 在文件末尾追加新日期
        new_content = content.rstrip() + f'\n\n## {DATE_STR}\n\n- {entry}\n'

    if not dry_run:
        path.write_text(new_content, encoding='utf-8')
        log(f'  ✅ 向 {path.name} 添加迁移日志')
    else:
        log(f'  📝 会向 {path.name} 添加迁移日志', dry_run=True)


def append_global_log(entry, dry_run=False):
    """向全局 knowledge/log.md 追加条目（2026-08-03 全局日志机制，替代分布式 log.md）。"""
    path = KNOWLEDGE_DIR / 'log.md'
    if not path.exists():
        if not dry_run:
            path.write_text(f'# knowledge 变更日志（全局）\n\n## {DATE_STR}\n\n{entry}\n', encoding='utf-8')
        return
    content = path.read_text(encoding='utf-8')
    date_header = f'## {DATE_STR}'
    if date_header in content:
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line.strip() == date_header and not inserted:
                new_lines.append('')
                new_lines.append(entry)
                inserted = True
        new_content = '\n'.join(new_lines)
    else:
        new_content = f'{content.rstrip()}\n\n## {DATE_STR}\n\n{entry}\n'
    if not dry_run:
        path.write_text(new_content, encoding='utf-8')
        log(f'  ✅ 向 knowledge/log.md 追加全局日志')
    else:
        log(f'  📝 会向 knowledge/log.md 追加全局日志', dry_run=True)


# ── knowledge/README.md 统计更新 ───────────────────────────

def update_knowledge_index(src_module, dst_module, dry_run=False):
    """更新 knowledge/README.md 中的文件数统计（如存在统计表）"""
    index_path = KNOWLEDGE_DIR / 'README.md'
    if not index_path.exists():
        return
    content = index_path.read_text(encoding='utf-8')

    # 匹配模块文件数行: | | *模块名* | **N** 个文件 |
    # 增加目标模块计数，减少源模块计数
    src_changed = False
    dst_changed = False

    def bump_count(line, delta):
        m = re.search(r'\*\*(\d+[+,]?\d*)\s*个文件', line)
        if m:
            old_count_str = m.group(1)
            try:
                old_count = int(old_count_str)
                new_count = max(0, old_count + delta)
                return line.replace(f'**{old_count_str}个文件', f'**{new_count}个文件'), True
            except ValueError:
                pass
        return line, False

    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if src_module in line and '个文件' in line:
            line, src_changed = bump_count(line, -1)
        if dst_module in line and '个文件' in line:
            line, dst_changed = bump_count(line, 1)
        new_lines.append(line)

    if src_changed or dst_changed:
        new_content = '\n'.join(new_lines)
        if not dry_run:
            index_path.write_text(new_content, encoding='utf-8')
            log(f'  ✅ 更新 knowledge/README.md 统计')
        else:
            log(f'  📝 会更新 knowledge/README.md 统计', dry_run=True)


# ── MIGRATIONS.md ────────────────────────────────────────────

def record_migration(src_path, dst_path, dry_run=False):
    """在 knowledge/MIGRATIONS.md 中记录迁移"""
    entry = f'| {DATE_STR} | `{src_path}` → `{dst_path}` | 文件迁移 |'

    if not MIGRATIONS_FILE.exists():
        content = (
            '# 知识库迁移记录\n\n'
            '> 记录 knowledge/ 中文件迁移的历史，便于追溯。\n\n'
            '## 迁移记录\n\n'
            '| 日期 | 迁移路径 | 说明 |\n'
            '|:-----|:---------|:-----|\n'
            f'{entry}\n'
        )
        if not dry_run:
            MIGRATIONS_FILE.write_text(content, encoding='utf-8')
            log(f'  ✅ 创建 MIGRATIONS.md 并记录迁移')
        else:
            log(f'  📝 会创建 MIGRATIONS.md 并记录迁移', dry_run=True)
        return

    content = MIGRATIONS_FILE.read_text(encoding='utf-8')
    # 查找表格区域，在第一行数据前插入
    lines = content.split('\n')
    separator_idx = -1
    for i, line in enumerate(lines):
        if '|:-----' in line:  # 表格分隔符行
            separator_idx = i
            break
    if separator_idx >= 0:
        lines.insert(separator_idx + 1, entry)
        new_content = '\n'.join(lines)
    else:
        new_content = content.rstrip() + f'\n{entry}\n'

    if not dry_run:
        MIGRATIONS_FILE.write_text(new_content, encoding='utf-8')
        log(f'  ✅ 在 MIGRATIONS.md 中记录迁移')
    else:
        log(f'  📝 会向 MIGRATIONS.md 添加迁移记录', dry_run=True)


# ── 交叉引用修复 ────────────────────────────────────────────

def fix_cross_references(dry_run=False):
    """调用 link-fixer.py 自动修复交叉引用"""
    if not LINK_FIXER.exists():
        log(f'  ⚠️ link-fixer.py 未找到: {LINK_FIXER}', dry_run)
        return

    cmd = ['python3', str(LINK_FIXER), '--auto']
    if dry_run:
        cmd.append('--dry-run')
    log(f'  🔧 修复交叉引用...', dry_run)
    run(cmd, dry_run=dry_run)


# ── 主流程 ──────────────────────────────────────────────────

def get_module(path):
    """从 knowledge/ 路径中提取顶层模块名"""
    try:
        rel = path.relative_to(KNOWLEDGE_DIR)
        return rel.parts[0] if rel.parts else None
    except ValueError:
        return None


def mv_knowledge(src_paths, dst_dir, dry_run=False, fix_links=True):
    """执行文件迁移"""
    dst_dir = Path(dst_dir).resolve()
    if not dst_dir.exists():
        log(f'❌ 目标目录不存在: {dst_dir}')
        return False
    try:
        dst_dir.relative_to(KNOWLEDGE_DIR)
    except ValueError:
        log(f'❌ 目标目录不在 knowledge/ 下: {dst_dir}')
        return False

    # 收集源模块信息
    src_modules = set()
    src_dirs = set()

    for src in src_paths:
        src = Path(src).resolve()
        if not src.exists():
            log(f'❌ 源文件不存在: {src}')
            return False
        try:
            src.relative_to(KNOWLEDGE_DIR)
        except ValueError:
            log(f'❌ 源文件不在 knowledge/ 下: {src}')
            return False
        src_modules.add(get_module(src))
        src_dirs.add(src.parent)

    dst_module = get_module(dst_dir)
    cross_module = len(src_modules - {dst_module}) > 0 or len(src_modules) > 1

    log(f'📋 迁移计划:')
    log(f'   源: {", ".join(str(s) for s in src_paths)}')
    log(f'   目标: {dst_dir}')
    log(f'   跨模块: {"是" if cross_module else "否"}')
    dst_global = uses_global_index(dst_dir)
    any_src_global = any(uses_global_index(Path(s).resolve().parent) for s in src_paths)
    log(f'   全局索引模块: 源={"是" if any_src_global else "否"} / 目标={"是" if dst_global else "否"}')
    log(f'')

    for src in src_paths:
        src = Path(src).resolve()
        src_dir = src.parent
        src_global = uses_global_index(src_dir)
        filename = src.name
        title = extract_title(src)
        summary = extract_summary(src)

        # 相对路径（用于 index.md 中的链接）
        src_rel = src.relative_to(KNOWLEDGE_DIR)
        dst_rel = dst_dir.relative_to(KNOWLEDGE_DIR)
        dst_file = dst_dir / filename

        log(f'📄 [{title}] {src} → {dst_file}', dry_run)

        # 0. 文件名规范检查 (design-003: YYYY-MM-DD-英文描述.md)
        # 若目标文件名不合规, 提示用户先用 kb-rename-normalize.py 规范化
        import re as _re
        _NORM = _re.compile(r'^\d{4}-\d{2}-\d{2}-[A-Za-z0-9][A-Za-z0-9-]*\.md$')
        if not _NORM.match(filename):
            log(f'  ⚠️ 文件名不合规({filename}): 期望 YYYY-MM-DD-英文描述.md。'
                f'建议迁移后运行 python3 scripts/tools/kb-rename-normalize.py --apply 规范化', dry_run)

        # 1. 移动文件
        if not dry_run:
            shutil.move(str(src), str(dst_file))
        log(f'  ✅ 文件已移动', dry_run)

        # 2-5. 更新源/目标目录 index.md/log.md（仅保留分布式机制的目录；全局模块由 index.md/log.md 统一管理）
        rel_from_src = src.relative_to(KNOWLEDGE_DIR)
        rel_to_dst = dst_file.relative_to(KNOWLEDGE_DIR)
        if not src_global:
            # 2. 更新源目录 index.md
            src_index = src_dir / 'index.md'
            update_index_remove(src_index, filename, dry_run)

            # 3. 更新源目录 log.md
            src_log = src_dir / 'log.md'
            update_log(src_log, f'**迁移** | `{rel_from_src}` → `{rel_to_dst}` — "{title}"', dry_run)

        if not dst_global:
            # 4. 更新目标目录 index.md
            dst_index = dst_dir / 'index.md'
            update_index_add(dst_index, filename, title, summary, dry_run)

            # 5. 更新目标目录 log.md
            dst_log = dst_dir / 'log.md'
            update_log(dst_log, f'**迁入** | `{rel_from_src}` → `{rel_to_dst}` — "{title}"', dry_run)

    # 6. 跨模块时更新 knowledge/README.md
    if cross_module:
        for src_mod in src_modules:
            if src_mod and src_mod != dst_module:
                update_knowledge_index(src_mod, dst_module, dry_run)

    # 7. 修复交叉引用
    if fix_links:
        fix_cross_references(dry_run)

    # 8. 记录迁移
    for src in src_paths:
        src = Path(src)
        # 但文件已移动，用原始路径记录
        record_migration(str(src), str(dst_dir / src.name), dry_run)

    # 9. 全局索引模块参与迁移 → 刷新全局 index.md + 追加全局 log.md
    if any_src_global or dst_global:
        if dry_run:
            log(f'  📝 会刷新 knowledge/index.md + 追加 knowledge/log.md（全局机制）')
        else:
            try:
                idx_script = REPO_ROOT / 'scripts' / 'tools' / 'kb-global-index.py'
                subprocess.run([sys.executable, str(idx_script)], cwd=REPO_ROOT, check=True)
                log(f'  ✅ 已刷新 knowledge/index.md')
            except Exception as e:
                log(f'  ⚠️ 刷新 index.md 失败: {e}')
            try:
                entry = (f'- **迁移** | `{src_paths[0]}` → `{dst_dir}` — 全局索引模块间迁移'
                         f'（详见 MIGRATIONS.md）')
                append_global_log(entry)
                log(f'  ✅ 已追加 knowledge/log.md')
            except Exception as e:
                log(f'  ⚠️ 追加全局 log.md 失败: {e}')

    log(f'\n✅ 迁移完成！' if not dry_run else '\n🔷 DRY-RUN 完成，以上为将执行的操作。使用 --fix 实际执行。')
    return True


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='mv-knowledge — 知识库文件迁移 CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            '示例:\n'
            '  python3 scripts/tools/mv-knowledge.py knowledge/01_survey/old.md knowledge/07_industry-research/\n'
            '  python3 scripts/tools/mv-knowledge.py --dry-run file.md target-dir/\n'
            '  python3 scripts/tools/mv-knowledge.py --no-fix-links file1.md file2.md target-dir/\n'
        )
    )
    parser.add_argument('sources', nargs='+', help='源文件路径（可指定多个）')
    parser.add_argument('destination', help='目标目录（必须是 knowledge/ 下目录）')
    parser.add_argument('--dry-run', '-n', action='store_true', help='预览模式，不实际修改')
    parser.add_argument('--no-fix-links', action='store_true', help='跳过交叉引用修复')
    args = parser.parse_args()

    # 分离源文件和目标目录
    *sources, dest = args.sources if len(args.sources) > 1 else [args.sources[0], args.destination]

    mv_knowledge(
        src_paths=sources,
        dst_dir=dest,
        dry_run=args.dry_run,
        fix_links=not args.no_fix_links,
    )


if __name__ == '__main__':
    main()
