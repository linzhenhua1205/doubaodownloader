#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_skills_paths.py - 检测和修复 skills 目录中的绝对路径问题。

功能：
1. 检测 skills 目录中使用绝对路径的文件
2. 自动将绝对路径转换为相对路径（相对于工程根路径）

使用方法：
    # 检测模式（只报告问题）
    python scripts/fix_skills_paths.py --check
    
    # 自动修复模式（修改文件）
    python scripts/fix_skills_paths.py --fix
    
    # 指定目录
    python scripts/fix_skills_paths.py --check --skills-dir skills/

Author: Assistant
Date: 2026-06-28
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 绝对路径模式（Windows 和 Unix 风格）
ABSOLUTE_PATH_PATTERNS = [
    # Windows 风格：D:\path 或 D:/path 或 d:/path
    r'[A-Za-z]:[/\\](?:123[/\\]cowkb[/\\]|skill[/\\]|skill)',
    # Unix 风格（Git Bash）：/d/123/cowkb 或 /d/skill
    r'/[A-Za-z]/(?:123/cowkb|skill)',
]

# 工程根路径（假设脚本在 scripts/ 目录下，根路径是其父目录）
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class PathFixer:
    """绝对路径检测和修复工具"""
    
    def __init__(self, skills_dir: Path, project_root: Path):
        self.skills_dir = skills_dir
        self.project_root = project_root
        self.issues: List[Dict] = []
        
    def detect_absolute_paths(self) -> List[Dict]:
        """检测 skills 目录中的绝对路径"""
        self.issues = []
        
        # 遍历 skills 目录下的所有文件
        for file_path in self.skills_dir.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # 只检查文本文件（根据扩展名）
                if self._is_text_file(file_path):
                    self._check_file(file_path)
        
        return self.issues
    
    def _is_text_file(self, file_path: Path) -> bool:
        """判断是否为文本文件"""
        text_extensions = {
            '.md', '.txt', '.py', '.sh', '.json', '.yaml', '.yml',
            '.xml', '.html', '.css', '.js', '.ts', '.tsx', '.jsx',
            '.ini', '.cfg', '.conf', '.toml', '.env',
            '.md', '.markdown', '.rst', '.tex'
        }
        return file_path.suffix.lower() in text_extensions
    
    def _check_file(self, file_path: Path):
        """检查单个文件中的绝对路径"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern in ABSOLUTE_PATH_PATTERNS:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            absolute_path = match.group()
                            relative_path = self._convert_to_relative(absolute_path)
                            
                            self.issues.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': line_num,
                                'absolute_path': absolute_path,
                                'relative_path': relative_path,
                                'content': line.strip(),
                                'match_start': match.start(),
                                'match_end': match.end()
                            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    def _convert_to_relative(self, absolute_path: str) -> str:
        """将绝对路径转换为相对路径"""
        # 去除驱动器字母和路径前缀
        # Windows: D:/123/cowkb/skills/... -> skills/...
        # Unix: /d/123/cowkb/skills/... -> skills/...
        
        # 统一处理不同格式
        path = absolute_path
        
        # 去除 Windows 风格的驱动器
        if re.match(r'^[A-Za-z]:[/\\]', path):
            path = re.sub(r'^[A-Za-z]:[/\\]', '', path)
        
        # 去除 Unix 风格的 /d/ 前缀
        if re.match(r'^/[A-Za-z]/', path):
            path = re.sub(r'^/[A-Za-z]/', '', path)
        
        # 去除工程根路径部分
        # 123/cowkb/skills/... -> skills/...
        if '123/cowkb/' in path or '123\\cowkb\\' in path:
            path = re.sub(r'^123[/\\]cowkb[/\\]', '', path)
        
        # 处理 skill/Light 或 skill/ 情况
        if 'skill/Light' in path or 'skill\\Light' in path:
            # 替换为 skills 目录下的相对路径
            # 需要根据上下文判断具体替换目标
            # 这里简化处理，保留 skills 前缀
            pass
        
        # 确保路径是相对的
        if path.startswith('/') or re.match(r'^[A-Za-z]:', path):
            # 如果还有绝对路径前缀，尝试更彻底的处理
            path = re.sub(r'^.*?skills[/\\]', 'skills/', path)
        
        return path
    
    def fix_paths(self, dry_run: bool = False) -> int:
        """修复文件中的绝对路径"""
        if not self.issues:
            print("No issues found.")
            return 0
        
        # 按文件分组
        file_issues: Dict[str, List[Dict]] = {}
        for issue in self.issues:
            file_path = issue['file']
            if file_path not in file_issues:
                file_issues[file_path] = []
            file_issues[file_path].append(issue)
        
        fixed_count = 0
        
        for file_path, issues in file_issues.items():
            full_path = self.project_root / file_path
            
            if dry_run:
                print(f"\nWould fix {file_path}:")
                for issue in issues:
                    print(f"  Line {issue['line']}: {issue['absolute_path']} -> {issue['relative_path']}")
                continue
            
            # 读取文件内容
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 替换绝对路径
                for issue in issues:
                    content = content.replace(
                        issue['absolute_path'],
                        issue['relative_path']
                    )
                
                # 写回文件
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Fixed {file_path} ({len(issues)} changes)")
                fixed_count += len(issues)
                
            except Exception as e:
                print(f"Error fixing {file_path}: {e}")
        
        return fixed_count
    
    def generate_report(self) -> str:
        """生成检测报告"""
        if not self.issues:
            return "[OK] No absolute paths found in skills directory."
        
        report_lines = [
            f"🔍 Found {len(self.issues)} absolute path(s) in {len(set(i['file'] for i in self.issues))} files:",
            ""
        ]
        
        # 按文件分组显示
        file_issues: Dict[str, List[Dict]] = {}
        for issue in self.issues:
            file_path = issue['file']
            if file_path not in file_issues:
                file_issues[file_path] = []
            file_issues[file_path].append(issue)
        
        for file_path, issues in sorted(file_issues.items()):
            report_lines.append(f"\n[FILE] {file_path}")
            for issue in issues:
                report_lines.append(
                    f"  Line {issue['line']}: {issue['absolute_path']}"
                )
                report_lines.append(
                    f"    → {issue['relative_path']}"
                )
        
        report_lines.extend([
            "",
            "💡 Run with --fix to automatically convert these paths."
        ])
        
        return '\n'.join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Detect and fix absolute paths in skills directory'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Only check for issues (dry-run mode)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Automatically fix detected issues'
    )
    parser.add_argument(
        '--skills-dir',
        type=str,
        default='skills',
        help='Skills directory path (default: skills)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without actually modifying files'
    )
    
    args = parser.parse_args()
    
    # 确定工作模式
    if not args.check and not args.fix:
        # 默认为检测模式
        args.check = True
    
    # 确定技能目录路径
    skills_dir = Path(args.skills_dir)
    if not skills_dir.is_absolute():
        skills_dir = PROJECT_ROOT / skills_dir
    
    if not skills_dir.exists():
        print(f"❌ Skills directory not found: {skills_dir}")
        sys.exit(1)
    
    # 创建修复工具
    fixer = PathFixer(skills_dir, PROJECT_ROOT)
    
    # 检测问题
    print("[INFO] Scanning skills directory for absolute paths...")
    issues = fixer.detect_absolute_paths()
    
    # 生成报告
    print(fixer.generate_report())
    
    # 执行修复（如果指定）
    if args.fix and issues:
        print("\n[FIX] Fixing absolute paths...")
        fixed_count = fixer.fix_paths(dry_run=args.dry_run)
        print(f"\n[OK] Fixed {fixed_count} absolute path(s)")
    
    # 返回状态码
    sys.exit(0 if not issues else 1)


if __name__ == '__main__':
    main()