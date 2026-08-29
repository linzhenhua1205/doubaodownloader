#!/usr/bin/env python3
"""
Knowledge Base Normalizer — 一站式知识库规范化工具

执行完整的规范化流水线：
  1. Index.md 覆盖率分析与补全（analyze-index-coverage）
  2. Log.md 格式重排（reformat-log）
  3. 链接有效性检查与修复（link-validator --fix）
  4. 裸引用检测与链接补全（link-augmenter）
  5. Markdown 格式检查（md-format）
  6. Index/Log 每目录作用域与格式合规（index-log-normalizer）

安全策略：默认 dry-run，需 --fix 才实际修改文件。

Usage:
    python scripts/check/knowledge-normalizer.py
    python scripts/check/knowledge-normalizer.py --fix
    python scripts/check/knowledge-normalizer.py --module 02_rd
    python scripts/check/knowledge-normalizer.py --skip index,format
    python scripts/check/knowledge-normalizer.py --only links,augment
"""
import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

SCRIPT_DIR = Path(__file__).parent.resolve()

# Pipeline stages in execution order
STAGES = {
    'index': {
        'name': 'Index.md 覆盖率分析与补全',
        'script': 'analyze-index-coverage.py',
        'args_all': ['--all'],
        'args_module': lambda m: [m],
        'fix_flag': '--fix',
        'supports_knowledge_dir': True,
    },
    'log': {
        'name': 'Log.md 格式重排',
        'script': 'reformat-log.py',
        'args_all': ['--all', '--dry-run'],
        'args_module': lambda m: ['--dry-run', m + '/log.md'],
        'fix_flag': '__APPLY__',  # special: remove --dry-run instead of adding flag
    },
    'links': {
        'name': '链接有效性检查与修复',
        'script': 'link-validator.py',
        'args_all': [],
        'args_module': lambda m: ['--module', m],
        'fix_flag': '--fix',
    },
    'augment': {
        'name': '裸引用检测与链接补全',
        'script': 'link-augmenter.py',
        'args_all': ['--titles-only', '--min-len', '8'],
        'args_module': lambda m: ['--module', m, '--titles-only', '--min-len', '8'],
        'fix_flag': '--fix',
        'supports_knowledge_dir': True,
    },
    'format': {
        'name': 'Markdown 格式检查',
        'script': 'md-format.py',
        'args_all': ['knowledge', '-r', '--level', 'R1'],
        'args_module': lambda m: ['knowledge/' + m, '-r', '--level', 'R1'],
        'fix_flag': None,  # format check is read-only
    },
    'scope': {
        'name': 'Index/Log 每目录作用域与格式合规',
        'script': 'index-log-normalizer.py',
        'args_all': ['knowledge', '--all', '--check'],
        'args_module': lambda m: ['knowledge/' + m, '--check'],
        'fix_flag': '__CHECK_TO_FIX__',  # swap --check → --fix in fix mode
    },
}

STAGE_ORDER = ['index', 'log', 'links', 'augment', 'format', 'scope', 'content']


def run_stage(stage_key: str, fix: bool, module: str, knowledge_dir: Path,
              verbose: bool = False) -> dict:
    """Run a single normalization stage. Returns dict with stats."""
    stage = STAGES[stage_key]
    script_path = SCRIPT_DIR / stage['script']

    if not script_path.exists():
        return {'stage': stage_key, 'name': stage['name'],
                'status': 'SKIP', 'reason': f'script not found: {stage["script"]}',
                'output': ''}

    cmd = [sys.executable, str(script_path)]

    # Add target args
    if module:
        # Some scripts take module path, others take module name
        cmd += stage['args_module'](module)
    else:
        cmd += stage['args_all']

    # Add knowledge-dir if stage supports it
    if stage.get('supports_knowledge_dir'):
        cmd += ['--knowledge-dir', str(knowledge_dir)]

    # Add fix flag if requested and stage supports it
    fix_flag = stage.get('fix_flag')
    if fix_flag:
        if fix_flag == '__APPLY__':
            # Special: script defaults to apply, dry-run uses --dry-run flag
            # In fix mode: remove --dry-run (which is in args)
            if not fix:
                pass  # --dry-run already in args
            else:
                cmd = [a for a in cmd if a != '--dry-run']
        elif fix_flag == '__CHECK_TO_FIX__':
            # Special: dry-run uses --check, fix mode swaps --check → --fix
            if fix:
                cmd = ['--fix' if a == '--check' else a for a in cmd]
        else:
            if fix:
                cmd.append(fix_flag)

    # Run
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300,
            cwd=str(knowledge_dir.parent),
        )
        elapsed = time.time() - t0
        output = result.stdout + result.stderr
        returncode = result.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return {'stage': stage_key, 'name': stage['name'],
                'status': 'TIMEOUT', 'reason': f'timed out after {elapsed:.1f}s',
                'output': '', 'elapsed': elapsed, 'returncode': -1}
    except Exception as e:
        elapsed = time.time() - t0
        return {'stage': stage_key, 'name': stage['name'],
                'status': 'ERROR', 'reason': str(e),
                'output': '', 'elapsed': elapsed, 'returncode': -1}

    status = 'OK' if returncode == 0 else 'ISSUES'

    return {
        'stage': stage_key,
        'name': stage['name'],
        'status': status,
        'elapsed': round(elapsed, 1),
        'returncode': returncode,
        'output': output,
    }


def print_summary(results: list, fix: bool):
    """Print a nice summary table of all stages."""
    mode = 'FIX' if fix else 'DRY-RUN'
    print()
    print("=" * 70)
    print(f"  知识库规范化汇总 [{mode}]")
    print("=" * 70)
    print()
    print(f"| 阶段 | 名称 | 状态 | 耗时 |")
    print(f"|:-----|:-----|:----:|-----:|")

    for r in results:
        status_icon = {
            'OK': '✅',
            'ISSUES': '⚠️',
            'ERROR': '❌',
            'TIMEOUT': '⏰',
            'SKIP': '⏭️',
        }.get(r['status'], '❓')
        elapsed = f"{r.get('elapsed', 0):.1f}s" if 'elapsed' in r else '-'
        print(f"| {status_icon} {r['stage']} | {r['name']} | {r['status']} | {elapsed} |")

    print()
    ok_count = sum(1 for r in results if r['status'] == 'OK')
    issues_count = sum(1 for r in results if r['status'] == 'ISSUES')
    error_count = sum(1 for r in results if r['status'] in ('ERROR', 'TIMEOUT'))
    print(f"  ✅ 成功: {ok_count}  ⚠️ 有问题: {issues_count}  ❌ 失败: {error_count}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Knowledge Base Normalizer — 一站式知识库规范化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available stages: {', '.join(STAGE_ORDER)}

Examples:
  python knowledge-normalizer.py                  # dry-run all stages
  python knowledge-normalizer.py --fix            # apply all fixes
  python knowledge-normalizer.py --module 02_rd   # only one module
  python knowledge-normalizer.py --only links,augment
  python knowledge-normalizer.py --skip format
        """
    )
    parser.add_argument('--fix', action='store_true',
                        help='Apply fixes (default: dry-run only)')
    parser.add_argument('--module', '-m',
                        help='Only process a specific module')
    parser.add_argument('--only',
                        help='Comma-separated list of stages to run (only these)')
    parser.add_argument('--skip',
                        help='Comma-separated list of stages to skip')
    parser.add_argument('--knowledge-dir', default='knowledge',
                        help='Path to knowledge directory (default: knowledge/)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show full output from each stage')

    args = parser.parse_args()

    knowledge_dir = Path(args.knowledge_dir).resolve()
    if not knowledge_dir.is_dir():
        print(f"Error: {knowledge_dir} is not a directory")
        sys.exit(1)

    # Determine which stages to run
    stages_to_run = list(STAGE_ORDER)
    if args.only:
        only = [s.strip() for s in args.only.split(',')]
        stages_to_run = [s for s in stages_to_run if s in only]
        invalid = [s for s in only if s not in STAGE_ORDER]
        if invalid:
            print(f"Warning: unknown stages in --only: {', '.join(invalid)}", file=sys.stderr)
    if args.skip:
        skip = [s.strip() for s in args.skip.split(',')]
        stages_to_run = [s for s in stages_to_run if s not in skip]

    if not stages_to_run:
        print("Error: no stages to run")
        sys.exit(1)

    mode = 'FIX' if args.fix else 'DRY-RUN'
    target = args.module or 'all modules'
    print(f"🚀 知识库规范化启动 [{mode}] — 目标: {target}")
    print(f"   阶段: {', '.join(stages_to_run)}")
    print(f"   知识目录: {knowledge_dir}")
    print()

    # Run each stage
    results = []
    for stage_key in stages_to_run:
        stage = STAGES[stage_key]
        print(f"▶ [{stage_key}] {stage['name']}...")

        result = run_stage(stage_key, args.fix, args.module, knowledge_dir, args.verbose)
        results.append(result)

        if args.verbose or result['status'] != 'OK':
            # Print a brief excerpt
            output = result.get('output', '')
            if output:
                lines = output.strip().split('\n')
                # Print first 5 and last 5 lines for long output
                if len(lines) > 15:
                    excerpt = '\n'.join(lines[:5]) + '\n... (truncated) ...\n' + '\n'.join(lines[-5:])
                else:
                    excerpt = output.strip()
                print(f"  ── Output ──")
                for line in excerpt.split('\n'):
                    print(f"  {line}")
                print()

        status_icon = {'OK': '✅', 'ISSUES': '⚠️', 'ERROR': '❌', 'TIMEOUT': '⏰', 'SKIP': '⏭️'}.get(result['status'], '❓')
        elapsed = f"{result.get('elapsed', 0):.1f}s" if 'elapsed' in result else ''
        print(f"  {status_icon} {result['status']} {elapsed}")
        print()

    # Summary
    print_summary(results, args.fix)

    # Exit code
    has_errors = any(r['status'] in ('ERROR', 'TIMEOUT') for r in results)
    has_issues = any(r['status'] == 'ISSUES' for r in results)
    if has_errors:
        sys.exit(2)
    elif has_issues and not args.fix:
        # In dry-run, issues are expected (that's why we check!)
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
