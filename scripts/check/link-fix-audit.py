#!/usr/bin/env python3
"""
link-fix-audit.py — 链接修复事后审查验证工具

固化 2026-08-05 全库链接修复（67503→0）的审查方法论，用于验证
"链接修复提交只改动了路径/链接信息，无内容误修改"。

三种审查模式（可组合）:
  1. --diff COMMIT    git diff 审计: 行数配对 + 剥离链接对比剩余文本
                     （断言每处改动只涉及 [text](url) 链接部分）
  2. --working       同 --diff 但审计未提交的 working tree 改动
                     （link-fixer.py --audit 集成入口, 修复后即时验证）
  3. --scan          全库残缺残留扫描: `.md)` 前无配对 `(` 的截断残留
                     （2026-08-05 BUG: URL 含括号被正则截断的产物）
  4. --downgrade     降级目标存在性核查: 被降级为纯文本的链接目标
                     是否真的不存在（防误降级）

用法:
  python3 scripts/check/link-fix-audit.py --diff e4e3105d7
  python3 scripts/check/link-fix-audit.py --working          # 修复后即时审计
  python3 scripts/check/link-fix-audit.py --scan
  python3 scripts/check/link-fix-audit.py --downgrade --working
  python3 scripts/check/link-fix-audit.py --diff HEAD~1 --scan --downgrade
"""

import os
import re
import sys
import json
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = WORKSPACE_ROOT / 'knowledge'

# 链接正则: [text](url)，URL 支持一层嵌套括号（2026-08-05 修复后与 validator 一致）
LINK_RE = re.compile(r'\[([^\]]*)\]\(((?:[^()]|\([^)]*\))+)\)')

# 残缺残留: `.md)` 前最近的 `(` 不构成 `](` 结构
TRUNCATED_RE = re.compile(r'\.md\)')

# 嵌套链接: 链接文字内含未转义的 `[link](url)`（非法 markdown，降级合理）
# 特征: `[` 后文字内又出现 `[` 直到 `](`
NESTED_RE = re.compile(r'\[[^\]]*\[[^\]]*\]\(')


# ── 模式1: git diff 审计 ────────────────────────────────────────────────────

def is_residue(line, m_end):
    """真残缺判定: `.md)` 前完全无 `(` 才是截断残留。

    - `](path.md)` 前有 `](` → 正常链接
    - `(SKILL.md)` / `(index.md)` 前有其他 `(` → 正文文件名说明，正常
    - `xxx战略演进.md)` 前无任何 `(` → 正则截断残留（2026-08-05 BUG 特征）
    """
    pre = line[:m_end]
    return pre.rfind('(') < 0


def audit_diff(commit=None, working=False):
    """对 diff 做链接变更审计:
    1. -/+ 行数一一配对（新增/删除文件除外——整文件新增无 - 行, 整文件删除无 + 行）
    2. 剥离 [text](url) 后剩余文本一致 → 只改了链接

    commit 指定时审计 `commit^..commit`; working=True 审计未提交改动。
    """
    scope = "working tree (未提交)" if working else f"{commit}"
    print(f"🔍 审计 diff: {scope}")
    print("=" * 72)

    cmd = ['git', 'diff']
    if working:
        cmd.append('HEAD')  # working tree vs HEAD: 覆盖 staged + unstaged 改动
    elif commit:
        cmd.append(f'{commit}^..{commit}')
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE_ROOT)
    if result.returncode != 0:
        print(f"❌ git diff 失败: {result.stderr[:300]}")
        return 1

    # 按文件分流: knowledge/ 文档区严格配对; scripts/ 等工具区统计
    # （2026-08-05 经验: 工具增强有代码净增, 行数不配对是正常的）
    # 整文件新增/删除块的行跳过统计（无配对行, 计入豁免清单）
    doc_dels, doc_adds = [], []
    tool_dels, tool_adds = [], []
    added_files, deleted_files = [], []  # 整文件新增/删除（配对豁免）
    cur_file = None
    in_new_block = in_del_block = False
    for line in result.stdout.split('\n'):
        if line.startswith('diff --git'):
            m = re.search(r' b/(\S+)', line)
            cur_file = m.group(1) if m else None
            in_new_block = in_del_block = False  # 新文件块开始, 复位豁免标志
            continue
        if line.startswith('new file mode'):
            if cur_file:
                added_files.append(cur_file)
            in_new_block = True
            continue
        if line.startswith('deleted file mode'):
            if cur_file:
                deleted_files.append(cur_file)
            in_del_block = True
            continue
        if line.startswith('\\ No newline'):  # git 元信息行, 非真实 diff
            continue
        is_doc = cur_file and cur_file.startswith('knowledge/')
        if line.startswith('+') and not line.startswith('+++'):
            if in_new_block:
                continue  # 整文件新增块的行不参与配对
            (doc_adds if is_doc else tool_adds).append(line[1:])
        elif line.startswith('-') and not line.startswith('---'):
            if in_del_block:
                continue  # 整文件删除块的行不参与配对
            (doc_dels if is_doc else tool_dels).append(line[1:])

    print(f"   knowledge/ 文档区: 删除 {len(doc_dels)} / 新增 {len(doc_adds)}"
          + (f"（整文件新增 {len(added_files)}, 删除 {len(deleted_files)}, 已豁免配对）" if added_files or deleted_files else ""))
    print(f"   scripts/ 工具区:  删除 {len(tool_dels)} / 新增 {len(tool_adds)} (预期代码增强净增)")

    # 文档区必须严格配对（链接修复是成对替换）——整文件新增/删除已在解析时豁免
    if len(doc_dels) != len(doc_adds):
        print(f"⚠️  knowledge/ 文档区行数不配对! 删除 {len(doc_dels)} vs 新增 {len(doc_adds)} — 可能存在内容增删")
        return 2

    # 链接级对比（文档区）
    # 死链降级模式: [文字](死链) → 文字（链接文字保留）→ 自动识别为预期行为
    # 真异常: ① 链接文字在 + 行消失 ② + 行含 .md) 残缺残留（正则截断产物）
    mismatches = []
    downgrade_count = 0
    nested_count = 0
    link_change_count = 0
    for i, (d, a) in enumerate(zip(doc_dels, doc_adds)):
        sd = LINK_RE.sub('', d).strip()
        sa = LINK_RE.sub('', a).strip()
        if sd == sa:
            link_change_count += 1
            continue  # 纯链接路径/格式变化
        # 残缺特征: + 行含 .md) 残留（2026-08-05 BUG: URL含括号被正则截断）
        if TRUNCATED_RE.search(a) and is_residue(a, TRUNCATED_RE.search(a).end()):
            mismatches.append((i, d, a, 'TRUNCATED残缺'))
            continue
        # 嵌套链接降级: 原文链接文字内嵌未转义链接（非法格式, 降级合理）
        if NESTED_RE.search(d):
            nested_count += 1
            continue
        # 链接文字保留检查: d 中每个链接文字都应出现在 a 中（降级或换路径）
        # 嵌套链接: 文字内可能含内层链接标记, 先去内层链接再比较
        d_texts = set(t for t, _ in LINK_RE.findall(d))
        a_texts = set(t for t, _ in LINK_RE.findall(a))
        missing = []
        for t in d_texts:
            t_flat = LINK_RE.sub(lambda m: m.group(1), t)  # 去掉内层链接标记
            if t not in a and t_flat not in a and t not in a_texts:
                missing.append(t)
        if not missing:
            downgrade_count += 1  # 所有链接文字均保留（部分降级/部分修复）
            continue
        mismatches.append((i, d, a, f'文字丢失: {missing}'))

    print(f"   纯链接变化: {link_change_count} 处")
    print(f"   死链降级(预期): {downgrade_count} 处")
    print(f"   嵌套链接降级(预期): {nested_count} 处")
    print(f"   真异常(需人工): {len(mismatches)} 处")
    for i, d, a, reason in mismatches[:20]:
        print(f"\n   ── 第{i}处 [{reason}] ──")
        print(f"   - 原: {d[:120]}")
        print(f"   + 新: {a[:120]}")

    if mismatches:
        print(f"\n⚠️  发现 {len(mismatches)} 处文本差异（链接文字丢失或残缺残留），需人工核查")
        return 2
    else:
        print("\n✅ knowledge/ 全部改动均为链接变化或预期的死链降级，无内容误修改")
        return 0


# ── 模式2: 残缺残留扫描 ─────────────────────────────────────────────────────

def scan_residue(path=KNOWLEDGE_ROOT):
    """全库扫描 `.md)` 前无配对 `(` 的截断残留"""
    print(f"🔍 扫描残缺残留: {path}")
    print("=" * 72)
    issues = []
    md_files = list(path.rglob('*.md')) if path.is_dir() else [path]

    for fp in md_files:
        try:
            with open(fp, encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if '`' in line:  # 跳过含代码的行（粗筛）
                        continue
                    for m in TRUNCATED_RE.finditer(line):
                        if is_residue(line, m.end()):
                            issues.append((fp, i, line.strip()[:120]))
        except Exception:
            continue

    print(f"   共 {len(issues)} 处疑似残缺残留")
    seen = set()
    for fp, ln, txt in issues:
        key = (fp, ln)
        if key in seen:
            continue
        seen.add(key)
        print(f"   ⚠️  {fp}:{ln} | {txt}")

    if issues:
        print("\n⚠️  存在残缺残留（多为正文括号内文件名说明，需人工甄别；")
        print("   真残缺特征: 文本中 `xxx.md)` 无配对 `(`，如『…战略演进.md)』）")
        return 2
    print("\n✅ 未发现残缺残留")
    return 0


# ── 模式3: 降级目标核查 ────────────────────────────────────────────────────

def audit_downgrade(commit=None, working=False):
    """核查被降级（死链→纯文本）的链接目标是否真的不存在"""
    scope = "working tree (未提交)" if working else (commit or "HEAD")
    print(f"🔍 降级目标存在性核查 ({scope})")
    print("=" * 72)

    # 从 diff 中提取被降级的链接目标: - [text](path) / + text
    cmd = ['git', 'diff']
    if working:
        cmd.append('HEAD')  # working tree vs HEAD: 覆盖 staged + unstaged 改动
    elif commit:
        cmd.append(f'{commit}^..{commit}')
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE_ROOT)
    if result.returncode != 0:
        print(f"❌ git diff 失败: {result.stderr[:300]}")
        return 1

    downgraded = []
    dels, adds = [], []
    for line in result.stdout.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            adds.append(line[1:])
        elif line.startswith('-') and not line.startswith('---'):
            dels.append(line[1:])

    for d, a in zip(dels, adds):
        m_old = LINK_RE.search(d)
        if m_old and m_old.group(2) not in a:
            # 旧行有链接, 新行没有 → 降级
            target = m_old.group(2).split('#')[0]
            if target and not target.startswith(('http', '#')):
                downgraded.append((target, m_old.group(1)))

    print(f"   被降级链接: {len(downgraded)} 处")
    missing_all, exist_somewhere = 0, 0
    for target, text in downgraded[:50]:
        name = Path(target).name
        found = list(KNOWLEDGE_ROOT.rglob(name)) if name else []
        found = [f for f in found if 'bak/' not in str(f) and 'oldbak/' not in str(f)]
        if found:
            exist_somewhere += 1
            print(f"   ⚠️  目标存在但被降级: `{target}` → 实际位于 {found[0].relative_to(WORKSPACE_ROOT)}")
        else:
            missing_all += 1
            print(f"   ✅ 目标确实不存在: `{target}` (链接文字: {text[:30]})")

    print(f"\n   确实不存在: {missing_all} | 存在于他处(可进一步修复): {exist_somewhere}")
    if exist_somewhere:
        print("⚠️  部分降级目标存在他处——可运行 link-fixer.py 的 MOVED 修复找回链接")
        return 2
    print("✅ 降级目标均确实不存在，降级合理")
    return 0


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='🔍 链接修复事后审查验证工具（2026-08-05 方法论固化）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--diff', metavar='COMMIT', help='审计指定提交的 diff（只改链接断言）')
    parser.add_argument('--working', action='store_true',
                        help='审计未提交的 working tree 改动（link-fixer.py --audit 集成入口）')
    parser.add_argument('--scan', action='store_true', help='全库扫描残缺残留')
    parser.add_argument('--downgrade', action='store_true', help='核查死链降级目标存在性（配合 --diff/--working 使用）')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    args = parser.parse_args()

    results = {}
    if args.diff:
        results['diff'] = audit_diff(args.diff)
    if args.working:
        results['diff'] = audit_diff(working=True)
    if args.scan:
        results['scan'] = scan_residue()
    if args.downgrade:
        results['downgrade'] = audit_downgrade(args.diff, working=args.working)

    if not results:
        parser.print_help()
        return 1

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if all(v == 0 for v in results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
