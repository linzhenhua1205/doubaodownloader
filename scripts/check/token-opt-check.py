#!/usr/bin/env python3
"""
Token 优化检查脚本 — token-opt-check.py

集成 scripts/tools/token-estimator.py 到检查管线。
检测大文件读取、上下文预算、阈值预警。

用法:
  python scripts/check/token-opt-check.py <file.md>
  python scripts/check/token-opt-check.py <dir/> --warn-at 0.7
  python scripts/check/token-opt-check.py --check-context <file1> <file2>
"""

import argparse
import os
import sys
import json
from pathlib import Path

from scripts.shared.workspace import WORKSPACE_ROOT, SCRIPTS_DIR

# 加载 token-estimator
TOOLS_DIR = SCRIPTS_DIR / 'tools'
sys.path.insert(0, str(TOOLS_DIR))

try:
    from token_estimator import TokenEstimator, estimate_tokens, CONTEXT_WINDOW
    HAS_ESTIMATOR = True
except ImportError:
    HAS_ESTIMATOR = False


def main():
    parser = argparse.ArgumentParser(
        description='Token 优化检查 — 集成 token-estimator.py',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('targets', nargs='*', default=[],
                        help='文件或目录')
    parser.add_argument('--warn-at', type=float, default=0.7,
                        help='预警阈值（占上下文比例，默认 0.7）')
    parser.add_argument('--check-context', action='store_true',
                        help='检查多个文件的累计上下文占用')
    parser.add_argument('--json', action='store_true',
                        help='JSON 输出')
    parser.add_argument('--large-only', type=int, default=500,
                        help='仅报告超过此行数的文件（默认 500）')
    args = parser.parse_args()

    if not HAS_ESTIMATOR:
        msg = "[ERROR] token_estimator 未安装或导入失败"
        print(msg, file=sys.stderr)
        sys.exit(1)

    # 收集文件
    files = []
    for t in args.targets:
        p = Path(t)
        if p.is_file() and p.suffix in ('.md', '.py', '.sh', '.txt'):
            files.append(p)
        elif p.is_dir():
            for ext in ('*.md', '*.py', '*.sh', '*.txt'):
                files.extend(p.rglob(ext))

    if not files:
        print("[INFO] 无目标文件，自动检测当前目录大文件")
        # 自动检测
        for ext in ('*.md', '*.py', '*.sh'):
            for f in Path('.').rglob(ext):
                try:
                    lines = len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
                    if lines >= args.large_only:
                        files.append(f)
                except Exception:
                    pass

    results = []
    for fpath in sorted(set(files)):
        try:
            text = fpath.read_text(encoding='utf-8', errors='ignore')
            lines = text.count('\n') + 1
            tokens = estimate_tokens(text)
            ratio = tokens / CONTEXT_WINDOW

            entry = {
                'file': str(fpath),
                'lines': lines,
                'tokens': tokens,
                'context_ratio': round(ratio, 3),
                'level': 'OK' if ratio < args.warn_at else 'WARN'
            }
            if ratio >= 0.9:
                entry['level'] = 'CRITICAL'
            results.append(entry)
        except Exception as e:
            results.append({
                'file': str(fpath),
                'error': str(e)[:80],
                'level': 'ERROR'
            })

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    # 文本输出
    warn_files = [r for r in results if r.get('level') in ('WARN', 'CRITICAL')]
    ok_files = [r for r in results if r.get('level') == 'OK']

    print(f"📊 Token 优化检查")
    print(f"{'=' * 50}")
    print(f"  上下文窗口: {CONTEXT_WINDOW:,} tokens")
    print(f"  预警阈值: {args.warn_at:.0%}")
    print(f"  检查文件: {len(results)}")
    print(f"  ✅ 正常: {len(ok_files)}")

    if warn_files:
        print(f"  ⚠️ 超阈值: {len(warn_files)}")
        for r in sorted(warn_files, key=lambda x: x.get('context_ratio', 0), reverse=True):
            sym = '🔴' if r['level'] == 'CRITICAL' else '🟠'
            print(f"  {sym} [{r['level']}] {r['file']}")
            print(f"     {r['tokens']:,} tokens / {r['lines']} 行 = {r['context_ratio']:.1%}")

    if not args.targets and warn_files:
        print(f"\n💡 提示: 大文件建议使用 lazy-reader.py 分段读取; "
              f"或使用 read 工具时指定 offset/limit 参数")


if __name__ == '__main__':
    main()
