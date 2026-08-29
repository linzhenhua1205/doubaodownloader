#!/usr/bin/env python3
"""
kb-rename-normalize — 知识库文件名规范化工具（YYYY-MM-DD-英文描述.md）

规范:
  - 文件名格式: YYYY-MM-DD-英文描述-使用-连接.md (如 2026-07-03-knowledge-scale-law.md)
  - 排除范围: 01_survey/ weekly-reports/ 分布式机制目录; index/log/README/INDEX 管理文件;
             oldbak/ *-bak/ 废弃归档区
  - 日期优先级: ①正文 ISO 日期(≥2025-01-01, 排除规范/标准发布日误报)
               ②头部元信息(Date/更新日期/Created)
               ③git 最早提交时间(commit date, 反映真实归档日)
               ④文件 mtime(最后兜底)
  - 描述: 已有英文文件名提取; 中文名翻译为英文 slug(内置映射表 + 规则)
  - 冲突: 重名加 -dup 后缀(不删除, 清理另议)

Usage:
    python3 scripts/tools/kb-rename-normalize.py --dry-run          # 生成映射表, 不执行
    python3 scripts/tools/kb-rename-normalize.py --apply            # 执行 git mv + 引用更新
    python3 scripts/tools/kb-rename-normalize.py --apply --no-links # 只改名, 不动引用
    python3 scripts/tools/kb-rename-normalize.py --csv tmp/kb-rename-mapping.csv
"""
import sys
import os
import re
import csv
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE = REPO_ROOT / 'knowledge'

# 排除: 分布式机制目录 / 管理文件 / 废弃归档区
EXCLUDE_DIRS = {'01_survey', 'weekly-reports', 'oldbak'}
EXCLUDE_FILES = {'index.md', 'log.md', 'README.md', 'MIGRATIONS.md', 'CHANGELOG.md'}

# 规范正则: YYYY-MM-DD-英文(字母数字开头, 可含-).md
NORM_RE = re.compile(r'^\d{4}-\d{2}-\d{2}-[A-Za-z0-9][A-Za-z0-9-]*\.md$')
DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')
ISO_RE = re.compile(r'\b(20\d{2}-\d{2}-\d{2})\b')
HEADER_DATE_RE = re.compile(r'^(?:Date|日期|更新日期|Created|创建日期|时间)[:：]\s*(\d{4}-\d{2}-\d{2})', re.M)
# 文件头部独立日期行: 前30行内, 整行只有日期 或 加粗日期 或 引用日期
HEAD_ISO_LINE_RE = re.compile(r'^[\*>]?\s*(\d{4}-\d{2}-\d{2})\s*[\*>]?$')

# 中文标题 → 英文 slug 映射（无法规则化的固定翻译，覆盖知识库全部中文文件名）
CN_SLUG_MAP = {
    '职业发展分析报告': 'career-development-analysis',
    '各年代大学生职业特征分析报告': 'generation-college-student-career-profile',
    '各年代大学生职业特征分析报告_完整版': 'generation-college-student-career-profile-full',
    '工作中常用方法论': 'common-methodology-in-work',
    '服务器整机研发后续工作点CHECK清单': 'server-dev-followup-check-list',
    '服务器整机研发规格列表': 'server-dev-spec-list',
    '服务器架构全面解析': 'server-architecture-full-analysis',
    '服务器架构演进': 'server-architecture-evolution',
    '服务器研发核心关注维度及要点': 'server-rd-core-dimensions-key-points',
    '工艺工序技术全景分析：从传统经验到智能制造的跨行业演进与实践': 'manufacturing-process-tech-panorama',
    'llm迁移记录': 'llm-migration-record',
    'nvidia-archives-迁移记录': 'nvidia-archives-migration-record',
}


def excluded(p: Path) -> bool:
    rel = p.relative_to(KNOWLEDGE)
    parts = rel.parts
    if parts[0] in EXCLUDE_DIRS:
        return True
    for part in parts[:-1]:
        if part.endswith('-bak') or part in EXCLUDE_DIRS:
            return True
    if p.name in EXCLUDE_FILES:
        return True
    return False


def git_first_commit(p: Path) -> str:
    """git 最早提交日期 (YYYY-MM-DD, --follow 追踪重命名链)。失败返回 None。"""
    try:
        r = subprocess.run(
            ['git', 'log', '--follow', '--diff-filter=A', '--format=%aI', '--', str(p.relative_to(REPO_ROOT))],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=30)
        lines = [l for l in r.stdout.strip().splitlines() if l]
        if lines:
            return lines[-1][:10]  # 最早(最后一个)提交
    except Exception:
        pass
    return None


# 批量 git 首次提交日期缓存: {相对路径: 'YYYY-MM-DD'} — 单次 git log -M 解析重命名链
_FIRST_COMMIT_CACHE = None


def load_first_commit_cache(files: list) -> dict:
    """单次 git log -M 解析全库 add/rename 事件, 追溯每个文件的真实首次提交日期。"""
    global _FIRST_COMMIT_CACHE
    if _FIRST_COMMIT_CACHE is not None:
        return _FIRST_COMMIT_CACHE
    cache = {}
    try:
        r = subprocess.run(
            ['git', 'log', '--reverse', '--format=%aI', '--name-status', '-M',
             '--diff-filter=AR', '--', 'knowledge/'],
            capture_output=True, text=True, cwd=REPO_ROOT, timeout=60)
        cur_date = None
        # 两遍: ①A事件记录首次add日期 ②R事件按时间序溯源(新路径继承旧路径日期)
        add_dates = {}    # path -> earliest date
        rename_events = []  # (date, old, new)
        for line in r.stdout.splitlines():
            if not line.strip():
                continue
            if re.match(r'^\d{4}-\d{2}-\d{2}T', line):
                cur_date = line[:10]
                continue
            parts = line.split('\t')
            if not parts:
                continue
            status = parts[0][:1]
            if status == 'A' and len(parts) >= 2:
                add_dates.setdefault(parts[1], cur_date)
            elif status == 'R' and len(parts) >= 3:
                rename_events.append((cur_date, parts[1], parts[2]))
        # 按时间序应用 rename 溯源: 新路径日期 = 旧路径日期(若旧路径已知)
        for date, old, new in rename_events:
            if old in add_dates:
                add_dates.setdefault(new, add_dates[old])
        # 提取 knowledge/ 下
        for path, d in add_dates.items():
            if path.startswith('knowledge/'):
                cache[path] = d
        # 补漏: 批量解析未命中的文件, 逐个 --follow 追溯(仅少量, 秒级)
        misses = [f for f in files if str(f.relative_to(REPO_ROOT)) not in cache]
        if misses:
            for f in misses:
                d = git_first_commit(f)
                if d:
                    cache[str(f.relative_to(REPO_ROOT))] = d
    except Exception:
        pass
    _FIRST_COMMIT_CACHE = cache
    return cache


def git_first_commit_cached(p: Path) -> str:
    """查缓存获取 git 最早提交日期。"""
    rel = str(p.relative_to(REPO_ROOT))
    return load_first_commit_cache([]).get(rel)


def pick_date(p: Path, body: str) -> tuple[str, str]:
    """返回 (date, source)。优先级: 头部明确日期 → git最早提交 → mtime。
    正文 ISO 日期仅在文件头部(前30行)作为独立日期行或元信息行时采信,
    防止正文内容中的引用日期/表格日期/规范发布日误报。"""
    lines = body.splitlines()[:30]
    head_text = '\n'.join(lines)
    # ① 头部元信息行: Date:/日期:/更新日期:/Created: 等
    hm = HEADER_DATE_RE.search(head_text)
    if hm and hm.group(1) >= '2025-01-01':
        return hm.group(1), 'header'
    # ② 头部独立日期行 (整行仅为日期, 或 *日期*/ >日期)
    for ln in lines:
        m = HEAD_ISO_LINE_RE.match(ln.strip())
        if m and m.group(1) >= '2025-01-01':
            return m.group(1), 'headline'
    # ③ git 最早提交时间 (反映真实归档日, 用户确认首选兜底)
    g = git_first_commit_cached(p)
    if g:
        return g, 'git'
    # ④ mtime (最后兜底)
    return datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d'), 'mtime'


def slugify(name_stem: str, cn_part: str) -> str:
    """生成英文 slug: 英文部分保留(小写-连接), 中文部分查映射表"""
    # 清理扩展名/日期前缀后缀/年份尾巴
    stem = name_stem
    stem = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', stem)   # 去日期前缀
    stem = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', stem)   # 去日期后缀
    stem = re.sub(r'^\d{8}-', '', stem)               # 去8位数字前缀
    stem = re.sub(r'[-_]?\d{4}$', '', stem)           # 去年份尾巴(_2026/-2026)
    slug = ''
    # 提取英文片段
    eng = re.findall(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', stem)
    for e in eng:
        if len(e) >= 2:  # 过滤单字符噪声
            slug = e.lower()
            break
    # 中文部分 (完整版等更长键先匹配: 按 key 长度降序)
    for cn, en in sorted(CN_SLUG_MAP.items(), key=lambda kv: -len(kv[0])):
        if cn in stem:
            slug = en if not slug else f'{en}-{slug}'
            break
    if not slug:
        slug = 'untitled'
    return slug


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='只生成映射表不执行')
    ap.add_argument('--apply', action='store_true', help='执行 git mv + 引用更新')
    ap.add_argument('--no-links', action='store_true', help='apply 时跳过引用更新')
    ap.add_argument('--csv', default=str(REPO_ROOT / 'tmp' / 'kb-rename-mapping.csv'))
    args = ap.parse_args()

    if not args.dry_run and not args.apply:
        ap.error('必须指定 --dry-run 或 --apply')

    files = sorted(p for p in KNOWLEDGE.rglob('*.md') if not excluded(p) and not NORM_RE.match(p.name))
    print(f'🔍 待改名文件: {len(files)}')

    # 预加载 git 首次提交缓存 (并发 --follow)
    load_first_commit_cache(files)
    print('📅 git 首次提交日期缓存加载完成')

    mappings = []  # (old_rel, new_name, date, date_source, dup)
    used_names = {}  # new_name -> count
    conflicts = []  # (old1, old2, content_identical)

    # 第一遍: 确定日期 + 新名(含冲突检测)
    for p in files:
        try:
            body = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            body = ''
        date, src = pick_date(p, body)
        stem = p.stem
        # 去掉已有日期前缀/后缀再生成描述
        desc_part = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', stem)
        desc_part = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', desc_part)
        desc_part = re.sub(r'^\d{8}-', '', desc_part)
        desc = slugify(desc_part, stem)
        new_name = f'{date}-{desc}.md'
        used_names[new_name] = used_names.get(new_name, 0) + 1
        mappings.append([str(p.relative_to(KNOWLEDGE)), new_name, date, src, ''])

    # 第二遍: 处理新名冲突(同目录/跨目录同名) — 加 -dup 消歧
    dup_counter = {}
    for m in mappings:
        if used_names[m[1]] > 1:
            dup_counter[m[1]] = dup_counter.get(m[1], 0) + 1
            m[4] = f'-dup{dup_counter[m[1]]}'
            # 重写新名
            stem, ext = m[1][:-3], '.md'
            m[1] = f'{stem}{m[4]}{ext}'

    # 第三遍: 内容完全相同组 — 保留最早日期原件, 其余加 -dup (用户要求重复文件加-dup后缀)
    import hashlib
    content_map = {}  # md5 -> [mapping]
    for m in mappings:
        try:
            h = hashlib.md5((KNOWLEDGE / m[0]).read_bytes()).hexdigest()
            content_map.setdefault(h, []).append(m)
        except Exception:
            pass
    content_dup_groups = 0
    for h, group in content_map.items():
        if len(group) > 1:
            content_dup_groups += 1
            # 按日期升序, 最早的保留原名, 其余加 -dup
            group.sort(key=lambda m: m[2])
            for idx, m in enumerate(group):
                if idx == 0 or m[4]:  # 原件 或 已加过dup
                    continue
                # 找未占用的 dup 编号
                n = 1
                base = m[1][:-3]
                while f'{base}-dup{n}.md' in {mm[1] for mm in mappings}:
                    n += 1
                m[4] = f'-dup{n}'
                m[1] = f'{base}-dup{n}.md'

    # 内容重复检测(同名不同路径, 供报告)
    name_map = {}
    for old, new, d, src, dup in mappings:
        name_map.setdefault(new, []).append(old)
    for new, olds in name_map.items():
        if len(olds) > 1:
            try:
                contents = set()
                for o in olds:
                    contents.add((KNOWLEDGE / o).read_text(encoding='utf-8', errors='ignore')[:500])
                conflicts.append((new, olds, len(contents) == 1))
            except Exception:
                pass

    # 输出 CSV
    Path(args.csv).parent.mkdir(parents=True, exist_ok=True)
    with open(args.csv, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['old_path', 'new_name', 'date', 'date_source', 'dup_suffix'])
        w.writerows(mappings)

    print(f'📄 映射表: {args.csv}')
    src_cnt = {}
    for m in mappings:
        src_cnt[m[3]] = src_cnt.get(m[3], 0) + 1
    print(f'📅 日期来源: {src_cnt}')
    print(f'🔀 新名冲突组(已加dup): {len([m for m in mappings if m[4] and m[4].startswith("-dup")])} 个文件')
    print(f'🔀 内容完全相同组: {content_dup_groups} 组')
    if conflicts:
        for new, olds, identical in conflicts[:15]:
            tag = '内容相同' if identical else '内容不同'
            print(f'   ⚠️ [{tag}] {new}:')
            for o in olds:
                print(f'      - {o}')

    if args.apply:
        print('\n🔄 执行 git mv ...')
        for old, new, d, src, dup in mappings:
            old_p = KNOWLEDGE / old
            new_p = old_p.parent / new
            if new_p.exists():
                print(f'   ❌ 目标已存在(跳过): {old} -> {new}')
                continue
            subprocess.run(['git', 'mv', str(old_p), str(new_p)],
                           capture_output=True, cwd=REPO_ROOT)
        print(f'✅ 完成 {len(mappings)} 个文件改名')
        if not args.no_links:
            update_refs(mappings)
    else:
        print('\n🔎 DRY-RUN 完成。审查映射表后执行: python3 scripts/tools/kb-rename-normalize.py --apply')


def update_refs(mappings):
    """更新全库引用: 旧文件名 → 新文件名。

    范围: knowledge/ 下所有 .md (活跃内容), 排除:
      - log.md / weekly-reports/ (历史快照, 保留旧名)
      - index.md (由 kb-global-index.py 重建, 不在此改)
      - README.md 例外: 其条目库文件名引用需同步更新(否则摘要注入失效), 纳入替换
    策略: 按旧名长度降序替换(防止子串误替换), 只替换独立文件名(前后非字母数字)。
    """
    print('   🔗 更新全库引用 ...')
    old_to_new = {}
    for old, new, d, src, dup in mappings:
        old_to_new[old.split('/')[-1]] = new  # 仅文件名级映射
    # 按旧名长度降序, 防止子串误替换 (如 a.md 是 ab.md 子串)
    items = sorted(old_to_new.items(), key=lambda kv: -len(kv[0]))
    updated_files = 0
    import re as _re
    for p in KNOWLEDGE.rglob('*.md'):
        rel = p.relative_to(KNOWLEDGE)
        parts = rel.parts
        if parts[0] in ('01_survey', 'weekly-reports', 'oldbak'):
            continue
        if p.name in ('log.md', 'index.md', 'MIGRATIONS.md'):
            continue
        if p.name == 'README.md' and p.parent != KNOWLEDGE:
            continue  # 仅根 README.md 纳入(子目录无 README 条目库)
        if any(pt.endswith('-bak') for pt in parts[:-1]):
            continue
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        orig = content
        for old, new in items:
            # 匹配独立文件名 (前后非字母数字/_/-), 覆盖 `old.md` / (old.md) / old.md#anchor 等
            content = _re.sub(
                rf'(?<![A-Za-z0-9_\-]){_re.escape(old)}(?![A-Za-z0-9_\-])', new, content)
        if content != orig:
            p.write_text(content, encoding='utf-8')
            updated_files += 1
    print(f'   ✅ 引用更新完成: {updated_files} 个文件, 需重跑 kb-global-index.py 刷新 index.md')


if __name__ == '__main__':
    main()
