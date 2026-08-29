#!/usr/bin/env python3
"""
link-fixer.py — Smart Link Fix Engine

Batch-fixes broken links in the knowledge base using learned patterns.
Applies fixes in order: auto-safe first, then interactive for ambiguous cases.

Usage:
    python3 scripts/check/link-fixer.py                             # Interactive fix session
    python3 scripts/check/link-fixer.py --module 06_superpod       # Fix specific module
    python3 scripts/check/link-fixer.py --dry-run                   # Preview only
    python3 scripts/check/link-fixer.py --auto                      # Auto-fix safe fixes only
    python3 scripts/check/link-fixer.py --auto --downgrade --audit  # Fix + verify via git diff (recommended)
    python3 scripts/check/link-fixer.py --report                    # Generate fix report
    python3 scripts/check/link-fixer.py --stub                      # Create stubs for MISSING files
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

# ── Constants ──────────────────────────────────────────────────────────────────

LINK_VALIDATOR = Path(__file__).resolve().parent / "link-validator.py"
# 修复后审计工具（2026-08-05 固化: 通过 git diff 分析验证修改合理性）
LINK_AUDIT = Path(__file__).resolve().parent / "link-fix-audit.py"

# ├── src_dir          The directory containing source files
# ├── link_prefix      The prefix of the broken link (to match)
# ├── fix_pattern      Fix function: (src_file_path, link_path) -> new_link_path or None
# ├── confidence       'high'=auto-safe / 'medium'=needs review / 'low'=interactive
# └── description      Human-readable description

FIX_RULES = [
    # ── Rule: Fix depth+1 when ../ goes too far ──
    # Example: file at `arch/01-xxx.md` uses `../../hh_core/` but should be `../01_hw_core/`
    {
        "name": "depth_plus_one",
        "description": "Remove one ../ when file depth increased (e.g., moved into arch/)",
        "confidence": "high",
        "matcher": lambda src, link: (
            link.startswith('../') and
            not (src.parent / link).resolve().exists()
        ),
        "fixer": lambda src, link: link[3:] if link.startswith('../') else link,
    },
    # ── Rule: Fix depth-1 when file moved up ──
    {
        "name": "depth_minus_one",
        "description": "Add one ../ when link depth is insufficient",
        "confidence": "high",
        "matcher": lambda src, link: (
            not link.startswith('../') and '..' not in link and
            not (src.parent / link).resolve().exists() and
            (src.parent.parent / link).resolve().exists()
        ),
        "fixer": lambda src, link: f"../{link}",
    },
    # ── Rule: arch/ prefix missing (file moved into arch/ subdirectory) ──
    {
        "name": "add_arch_prefix",
        "description": "Add arch/ prefix when target was moved into arch/ subdirectory",
        "confidence": "high",
        "matcher": lambda src, link: (
            not link.startswith('arch/') and
            not (src.parent / link).resolve().exists() and
            (src.parent / f"arch/{link}").resolve().exists()
        ),
        "fixer": lambda src, link: f"arch/{link}",
    },
    # ── Rule: Remove arch/ prefix from link ──
    {
        "name": "remove_arch_prefix",
        "description": "Remove arch/ prefix when files are now at root level",
        "confidence": "high",
        "matcher": lambda src, link: (
            link.startswith('arch/') and
            not (src.parent / link).resolve().exists() and
            (src.parent / link[5:]).resolve().exists()
        ),
        "fixer": lambda src, link: link[5:] if link.startswith('arch/') else link,
    },
    # ── Rule: Directory renamed ──
    {
        "name": "dir_renamed",
        "description": "Fix links to renamed directories",
        "confidence": "high",
        "matcher": lambda src, link: any(
            old_dir in link for old_dir in ['knowledge/', '/knowledge/']
        ),
        "fixer": lambda src, link: re.sub(
            r'(\.\./)?knowledge/', '',
            link
        ),
    },
    # ── Rule: cross-module depth ──
    {
        "name": "cross_module_depth",
        "description": "Fix cross-module relative depth (../../ vs ../../../)",
        "confidence": "medium",
        "matcher": lambda src, link: (
            link.count('../') > 0 and
            any(mod in link for mod in
                ['01_survey', '02_rd', '03_AI', '04_person', '05_tools',
                 '06_others', '07_industry-research'])
        ),
        "fixer": None,  # Handled by caller with dynamic depth try
    },
    # ── Rule: redundant ../knowledge/ prefix ──
    {
        "name": "redundant_knowledge_prefix",
        "description": "Remove redundant knowledge/ prefix from relative links",
        "confidence": "high",
        "matcher": lambda src, link: '../knowledge/' in link,
        "fixer": lambda src, link: link.replace('../knowledge/', ''),
    },
    # ── Rule: Windows backslash → forward slash ──
    # 2026-08-05 全库修复: 569 处 `..\dir\file.md` 反斜杠路径
    # 注意: 格式修复不验证目标存在性（路径可能本身坏，但格式应先纠正）
    {
        "name": "backslash_to_slash",
        "description": "Convert Windows-style backslash paths to forward slashes",
        "confidence": "high",
        "verify_exists": False,
        "matcher": lambda src, link: '\\' in link,
        "fixer": lambda src, link: link.replace('\\', '/'),
    },
]


# ── Fix Engine ─────────────────────────────────────────────────────────────────

def try_fix(rule, src_file, link_path):
    """Try to apply a fix rule. Returns (fixed_link, confidence) or None."""
    if not rule["matcher"](src_file, link_path):
        return None
    if rule["fixer"] is None:
        return None  # Complex rules handled separately

    new_link = rule["fixer"](src_file, link_path)
    if new_link == link_path:
        return None

    # 格式修复类规则（如反斜杠→正斜杠）不验证目标存在性
    verify = rule.get("verify_exists", True)
    if not verify:
        return (new_link, rule["confidence"])

    # Verify the fix resolves correctly
    resolved = (src_file.parent / new_link).resolve()
    if resolved.exists():
        return (new_link, rule["confidence"])
    return None


def try_cross_module_fix(src_file, link_path):
    """Try adjusting cross-module depth by ±1."""
    for adjustment in [-1, 1]:
        if adjustment == -1 and link_path.count('../') > 0:
            adjusted = link_path.replace('../', '', 1)
        elif adjustment == 1:
            adjusted = '../' + link_path
        else:
            continue

        resolved = (src_file.parent / adjusted).resolve()
        if resolved.exists():
            return (adjusted, "medium")
    return None


def try_file_search_fix(src_file, link_path):
    """Search for the target filename anywhere in knowledge/."""
    link_name = Path(link_path).name
    if not link_name or not link_name.endswith('.md'):
        return None

    found = list(KNOWLEDGE_ROOT.rglob(link_name))
    found = [f for f in found if 'bak/' not in str(f)]

    if found:
        try:
            correct_rel = os.path.relpath(found[0], src_file.parent)
            return (correct_rel, "medium")
        except ValueError:
            pass
    return None


def suggest_fixes(src_file, link_path):
    """Try all fix strategies in order. Returns list of (fixed_link, confidence)."""
    fixes = []

    # Strategy 1: Apply FIX_RULES
    for rule in FIX_RULES:
        result = try_fix(rule, src_file, link_path)
        if result:
            fixes.append(result)

    # Strategy 2: Cross-module depth adjustment
    if not any(f[1] == 'high' for f in fixes):
        result = try_cross_module_fix(src_file, link_path)
        if result:
            fixes.append(result)

    # Strategy 3: File search
    if not fixes:
        result = try_file_search_fix(src_file, link_path)
        if result:
            fixes.append(result)

    # Strategy 4: Dead-link downgrade (MISSING 目标 → 降级为纯文本)
    # 2026-08-05 全库修复: 727 处死链降级（保留链接文字，丢失链接功能）
    # 有损操作 → 标记 DOWNGRADE，仅 --downgrade 显式启用时应用
    if not fixes:
        fixes.append(('__DOWNGRADE__', 'low'))

    return fixes


# ── Main Fix Orchestrator ──────────────────────────────────────────────────────

def run_validator(args):
    """Run link-validator.py and parse JSON output."""
    import subprocess
    cmd = [sys.executable, str(LINK_VALIDATOR)]
    if args.module:
        cmd.extend(['--module', args.module])
    if args.file:
        cmd.extend(['--file', args.file])
    cmd.append('--json')

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=KNOWLEDGE_ROOT.parent)
    if result.returncode not in (0, 1):
        if result.stderr:
            print(f"❌ Validator failed: {result.stderr.strip()}")
        return None

    # Find JSON in stdout (handle any remaining banner output)
    stdout = result.stdout.strip()
    if not stdout:
        if result.stderr:
            print(f"⚠️  Validator stderr: {result.stderr.strip()}")
        return None

    # Try to extract JSON object from the output
    json_start = stdout.find('{')
    json_end = stdout.rfind('}')
    if json_start >= 0 and json_end > json_start:
        json_str = stdout[json_start:json_end+1]
    else:
        json_str = stdout

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Can't parse validator output: {e}")
        print(f"   Raw output (first 300 chars): {stdout[:300]}")
        return None


def run_audit(audit_commit=None):
    """修复后审计: 分析 git diff 验证修改合理性（2026-08-05 方法论固化）。

    - 默认: --working 审计未提交改动（修复后立即验证）
    - 指定 --audit-commit: 审计已提交 commit（修复已提交后复核）

    返回审计工具退出码（0=通过, 非0=发现异常需人工核查）。
    """
    import subprocess
    cmd = [sys.executable, str(LINK_AUDIT), '--working', '--downgrade']
    if audit_commit:
        cmd = [sys.executable, str(LINK_AUDIT), '--diff', audit_commit, '--downgrade']

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE_ROOT)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(f"   (stderr) {result.stderr.strip()[:300]}")
    return result.returncode


def categorize_issues(data):
    """Categorize issues by fixability."""
    if not data or 'issues' not in data:
        return [], [], []

    auto_fixable = []
    needs_review = []
    unfixable = []

    for issue in data['issues']:
        itype = issue.get('type', 'MISSING')
        if itype == 'EXTERNAL':
            # Bare path — easy to fix
            auto_fixable.append(issue)
        elif itype == 'MOVED' and issue.get('suggestion', '').startswith('Replace'):
            auto_fixable.append(issue)
        elif itype == 'DEPTH':
            auto_fixable.append(issue)
        elif itype == 'DIR_RENAME':
            auto_fixable.append(issue)
        elif itype == 'MISSING':
            unfixable.append(issue)
        else:
            needs_review.append(issue)

    return auto_fixable, needs_review, unfixable


def apply_fixes(issues, dry_run=False, auto_mode=False, downgrade=False):
    """Apply fixes to files.

    downgrade=True 时允许死链降级（MISSING → 纯文本，有损操作）。
    所有写入带长度验证：新长度 < 原长度 50% 拒绝写入（防内容丢失，
    2026-08-05 经验：正则误匹配可导致内容大幅截断）。
    """
    by_file = defaultdict(list)
    for issue in issues:
        by_file[issue['file']].append(issue)

    fixed_count = 0
    files_modified = set()
    failed_fixes = []

    for fname in sorted(by_file.keys()):
        filepath = KNOWLEDGE_ROOT / fname
        if not filepath.exists():
            failed_fixes.append((fname, "File not found"))
            continue

        original = filepath.read_text(encoding='utf-8')
        content = original
        file_fixed = False

        file_issues = by_file[fname]
        for issue in file_issues:
            suggestion = issue.get('suggestion', '')
            link = issue.get('link', '')
            text = issue.get('text', '')

            # ── 死链降级: [text](dead) → text（保留链接文字，有损）──
            if issue['type'] == 'MISSING' and downgrade and text and link:
                old_pattern = f'[{text}]({link})'
                if old_pattern in content:
                    content = content.replace(old_pattern, text, 1)
                    if not dry_run:
                        file_fixed = True
                    fixed_count += 1
                    continue
                # 容错: link 含括号被截断时, 尝试按链接边界匹配
                # （正则误匹配防护: 用 [text]( 定位, 括号平衡找到真正结尾）
                idx = content.find(f'[{text}](')
                if idx >= 0:
                    content = content[:idx] + text + content[find_link_end(content, idx):]
                    if not dry_run:
                        file_fixed = True
                    fixed_count += 1
                    continue

            # Extract new link from suggestion
            m = re.search(r'`([^`]+)`\s*→\s*`([^`]+)`', suggestion)
            if m:
                old_link, new_link = m.group(1), m.group(2)

                # Try to replace the markdown link [text](old)
                old_pattern = f'({old_link})'
                new_pattern = f'({new_link})'

                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern, 1)
                    if not dry_run:
                        file_fixed = True
                    fixed_count += 1
                elif old_link in content:
                    # Try direct replacement
                    content = content.replace(old_link, new_link, 1)
                    if not dry_run:
                        file_fixed = True
                    fixed_count += 1
                else:
                    failed_fixes.append((fname, f"Can't find `{old_link}` in file"))
            elif issue['type'] == 'EXTERNAL':
                # Bare path → wrap as link
                bare_path = issue.get('link', '')
                old_pattern = bare_path
                new_pattern = f'[{bare_path}]({bare_path})'

                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern, 1)
                    if not dry_run:
                        file_fixed = True
                    fixed_count += 1

        if file_fixed:
            if not dry_run:
                # 写后长度验证（防正则误匹配截断导致内容丢失）
                if len(content) < len(original) * 0.5:
                    failed_fixes.append((fname, f"长度校验失败: {len(content)} < 50% 原始 {len(original)}（拒绝写入）"))
                    continue
                filepath.write_text(content, encoding='utf-8')
            files_modified.add(fname)

    return fixed_count, len(files_modified), failed_fixes


def find_link_end(content, start):
    """从 `[text](` 位置找到链接结尾（括号平衡），防 URL 含括号截断。

    返回链接结束后的下标（即 `)` 后的位置）。2026-08-05 正则误匹配 BUG 的
    根治方案：处理链接时用括号计数而非 `[^)]+`。
    """
    depth = 0
    for j in range(start, len(content)):
        c = content[j]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return j + 1
    return len(content)


def generate_stubs(issues, dry_run=False):
    """Create stub files for MISSING references."""
    stubs_created = 0
    for issue in issues:
        if issue['type'] != 'MISSING':
            continue
        link = issue.get('link', '')
        resolved = issue.get('resolved', '')

        if not resolved or resolved == 'None':
            continue

        stub_path = Path(resolved)
        if stub_path.exists():
            continue

        # Don't create stubs for files in bak/
        if 'bak/' in str(stub_path):
            continue

        if not dry_run:
            stub_path.parent.mkdir(parents=True, exist_ok=True)
            ref_from = issue['file']
            stub_content = f"""# Stub: {stub_path.name}

> ⚠️ This file is referenced from `{ref_from}` but does not exist.
> Created automatically by link-fixer.py on {datetime.now().strftime('%Y-%m-%d')}.

## TODO

- [ ] Add content for this file
- [ ] Verify cross-references
"""
            stub_path.write_text(stub_content, encoding='utf-8')
        stubs_created += 1

    return stubs_created


# ── Main CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='🔧 Knowledge Base Link Fix Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/check/link-fixer.py                        # Interactive fix session
  python3 scripts/check/link-fixer.py --module 06_superpod   # Fix specific module
  python3 scripts/check/link-fixer.py --dry-run               # Preview fixes
  python3 scripts/check/link-fixer.py --auto                  # Auto-fix safe ones only
  python3 scripts/check/link-fixer.py --auto --downgrade --audit   # Fix + auto-verify via git diff
  python3 scripts/check/link-fixer.py --stub                  # Create stubs for missing files
  python3 scripts/check/link-fixer.py --report                # Fix plan report
        """
    )
    parser.add_argument('--module', '-m', help='Scope to a module directory')
    parser.add_argument('--file', '-f', help='Scope to a single file')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Preview only, no changes')
    parser.add_argument('--auto', action='store_true', help='Auto-fix all safe fixes (non-interactive)')
    parser.add_argument('--stub', action='store_true', help='Create stub files for MISSING references')
    parser.add_argument('--downgrade', action='store_true', help='Allow dead-link downgrade to plain text (lossy, 2026-08-05)')
    parser.add_argument('--audit', action='store_true',
                        help='修复后自动审计: 分析 git diff 验证修改合理性（需 git 仓库; 需非 --dry-run）')
    parser.add_argument('--audit-commit', metavar='COMMIT',
                        help='配合 --audit: 审计指定已提交 commit 而非未提交改动（修复已提交后复核用）')
    parser.add_argument('--report', '-r', action='store_true', help='Generate fix plan report')
    parser.add_argument('--json', action='store_true', help='JSON output')
    args = parser.parse_args()

    # Step 1: Run validator to find issues
    scope_label = args.module or args.file or "knowledge/ (full)"
    print(f"🔍 Running link validator on {scope_label}...")
    data = run_validator(args)

    if not data or 'issues' not in data:
        print("❌ No issues found or validator failed")
        return 1

    issues = data['issues']
    if not issues:
        print("✅ No broken links found!")
        return 0

    # Step 2: Categorize
    auto_fixable, needs_review, unfixable = categorize_issues(data)

    print(f"\n📊 Fix Analysis:")
    print(f"   {'Auto-fixable':<25} {len(auto_fixable):>4}")
    print(f"   {'Needs review':<25} {len(needs_review):>4}")
    print(f"   {'Unfixable (missing)':<25} {len(unfixable):>4}")
    print(f"   {'─'*30}")
    print(f"   {'TOTAL':<25} {len(issues):>4}")
    print()

    # Step 3: Generate report if requested
    if args.report:
        print("=" * 72)
        print("  📋 Fix Plan Report")
        print("=" * 72)
        print()

        if auto_fixable:
            print(f"  ✅ AUTO-FIXABLE ({len(auto_fixable)}):")
            by_file = defaultdict(list)
            for issue in auto_fixable:
                by_file[issue['file']].append(issue)
            for fname in sorted(by_file.keys()):
                file_issues = by_file[fname]
                print(f"\n    📄 {fname}:")
                for issue in file_issues:
                    suggestion = issue.get('suggestion', '')
                    if '→' in suggestion:
                        parts = suggestion.split('→')
                        old = parts[0].strip().lstrip('Replace').strip().strip('`')
                        new = parts[-1].strip().strip('`')
                        print(f"      L{issue['line']:>4}  `{issue['link']}`")
                        print(f"            → `{new}`")

        if unfixable:
            print(f"\n  ❌ UNFIXABLE / MISSING ({len(unfixable)}):")
            uniq_targets = set()
            for issue in unfixable[:30]:
                uniq_targets.add(issue['link'])
            for t in sorted(uniq_targets)[:20]:
                print(f"      • `{t}`")
            if len(uniq_targets) > 20:
                print(f"      ... and {len(uniq_targets) - 20} more")

        print()

    # Step 4: Apply fixes
    files_affected = 0
    if args.auto or not args.report:
        # 死链降级（MISSING）需 --downgrade 显式授权 → 合并入修复候选
        # （2026-08-05 修复: 此前 MISSING 归入 unfixable, apply_fixes 只收
        #   auto_fixable, 导致 --downgrade 对死链从未生效——真实缺陷）
        fix_candidates = list(auto_fixable)
        if args.downgrade:
            fix_candidates += [i for i in unfixable if i.get('type') == 'MISSING']
        if fix_candidates:
            if args.dry_run:
                print(f"🔧 DRY RUN — Would fix {len(fix_candidates)} links:")
            else:
                print(f"🔧 Applying {len(fix_candidates)} fixes"
                      + (" (含死链降级)" if args.downgrade else "") + "...")

            fixed, files_affected, failed = apply_fixes(
                fix_candidates, dry_run=args.dry_run, auto_mode=args.auto,
                downgrade=args.downgrade
            )

            print()
            if args.dry_run:
                print(f"   📋 Would fix {fixed} links in {files_affected} files")
            else:
                print(f"   ✅ Fixed {fixed} links in {files_affected} files")
                if failed:
                    print(f"   ⚠️  {len(failed)} fixes failed:")
                    for fname, reason in failed[:10]:
                        print(f"       • {fname}: {reason}")
        else:
            print("✅ No auto-fixable issues found")

    # Step 5: Create stubs if requested
    if args.stub and unfixable:
        stubs = generate_stubs(unfixable, dry_run=args.dry_run)
        if args.dry_run:
            print(f"\n   📋 Would create {stubs} stub files")
        else:
            print(f"\n   📄 Created {stubs} stub files")

    # Step 6: 修复后审计 — 分析 git diff 验证修改合理性（2026-08-05 方法论固化）
    # 仅在非 dry-run 且确有改动时执行; --audit-commit 可审计已提交版本
    if args.audit and not args.dry_run:
        print()
        print("=" * 72)
        print("  🔍 修复后审计: 分析 git diff 验证修改合理性")
        print("=" * 72)
        if args.audit_commit:
            print(f"   (审计已提交 commit: {args.audit_commit})")
        elif files_affected:
            print("   (审计未提交改动; 若修复前工作区已有其他改动, 结果可能混合, 建议先提交基线再修复)")
        audit_rc = run_audit(args.audit_commit)
        if audit_rc != 0:
            print("\n⚠️  审计未通过——diff 中发现疑似异常（文字丢失/残缺残留/行数不配对等），")
            print("   请人工核查后再提交（自动修复不会被撤销）。")
            return 2
        print("\n✅ 审计通过: 全部改动均为链接变化或预期降级，可安全提交。")

    return 0


if __name__ == '__main__':
    sys.exit(main())
