#!/usr/bin/env python3
"""
Detect reuse violations + audit new dependencies.
Usage: python3 check_reuse.py <file_path>
"""

import ast
import sys
import re
from pathlib import Path


def check_functions(file_path):
    """Detect newly written functions that duplicate existing utility functions."""
    with open(file_path) as f:
        tree = ast.parse(f.read())
    new_funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    # Compare against component inventory known functions
    known_funcs = {
        'format_date', 'parse_date', 'send_request', 'retry_call',
        'validate_input', 'read_config', 'write_output', 'log_error'
    }
    duplicates = new_funcs & known_funcs
    if duplicates:
        print(f"⚠️  Possible duplicate functions detected: {duplicates}")
        print("   Prioritize reusing existing components from component inventory")
        return False
    return True


def check_new_imports(file_path):
    """Detect new third-party dependencies requiring approval."""
    pattern = re.compile(r'^(import|from)\s+(\w+)')
    known_imports = {
        'os', 'sys', 'json', 're', 'datetime', 'pathlib',
        'typing', 'collections', 'math', 'random', 'time',
        'functools', 'itertools', 'copy', 'enum'
    }
    new_imports = set()
    with open(file_path) as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                pkg = m.group(2).split('.')[0]
                if pkg not in known_imports:
                    new_imports.add(pkg)
    if new_imports:
        print(f"⚠️  New dependencies detected (need approval): {new_imports}")
        return False
    return True


if __name__ == '__main__':
    file_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    ok = check_functions(file_path)
    ok = check_new_imports(file_path) and ok
    sys.exit(0 if ok else 1)
