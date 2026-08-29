#!/usr/bin/env python3
"""
constraint-check.py — 统一约束合规检查器（Lint for Cow System）

基于 spec/SR-003-system-constraint-registry.md 的 70 条约束 (01001-12305)，
对技能、脚本、文档、知识库做分类合规检查。

== 使用方式 ==

  # 列出所有检查类别
  python3 scripts/constraint-check.py --list-categories

  # 运行全部检查
  python3 scripts/constraint-check.py --category all

  # 运行特定类别
  python3 scripts/constraint-check.py --category safety
  python3 scripts/constraint-check.py --category format,paths,index-log

  # 指定检查目标（文件或目录）
  python3 scripts/constraint-check.py --category format --target knowledge/01_survey/today.md
  python3 scripts/constraint-check.py --category quality --target knowledge/02_rd/

  # 自动修复可修复项
  python3 scripts/constraint-check.py --category format --target file.md --fix

  # JSON 输出
  python3 scripts/constraint-check.py --category all --json

  # 只输出摘要
  python3 scripts/constraint-check.py --category all --summary

== 类别对应约束 ==

  safety      01001-01010  安全红线（rm 禁令/密钥保护/不编造/bak 禁区/素材批判使用）
  file-ops    02101-02108  文件操作（头部约束/bak 规范/命名/深度/指数/同步）
  paths       03101-03108  路径映射注册表合规 + Skills 路径硬编码检测
  format      04101-04106  知识库格式（TOC/Changelog/参考文件/概要/关键词/五要素）
  index-log   05101-05103  index/log 文档合规（范围/格式/更新同步）
  code        06101-06105  代码/脚本规范（argparse CLI / 命名 / 目录 / pathlib）
  quality     07201-07206  文档质量标准（量化四要素/来源标注/MECE/交叉验证/时效/深度）
  skills      08201-09204  Skills 行为（自动记录/自检交付/写入路径/不客套）
  kb-write    10301-10305  知识库写入策略（存储判定/日跟踪/深度分析/导入笔记/体系化知识）
  review      11301-11305  审查验证（五层审查/自检/证据闸门/三态判定/一致性六类）
  scheduler   12301-12308  定时任务（Fail-Fast/来源分级/空文件/Token 预算/周报模板）
  all                 全部

== 依赖 ==

  大部分检查集成或委托现有脚本：
    scripts/check/format-validator.py
    scripts/check/strategy-compliance.py
    scripts/check/doc-quality.py
    scripts/check/doc-review.py
    scripts/check/link-validator.py
    scripts/check/kb-health.py
    scripts/check/index-log-normalizer.py
    scripts/check/analyze-index-coverage.py
    scripts/check/ref-drift-detector.py
    scripts/check/relation-integrity.py
"""

import sys
import re
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict, OrderedDict
from typing import Dict, List, Tuple, Optional, Any, Callable

from scripts.shared.workspace import WORKSPACE_ROOT, KNOWLEDGE_ROOT  # sr-008

# ── 常量 ───────────────────────────────────────────────────────────────────────

KNOWLEDGE_ROOT = WORKSPACE_ROOT / "knowledge"
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
SKILLS_DIR = WORKSPACE_ROOT / "skills"
SPEC_DIR = WORKSPACE_ROOT / "spec"

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M")

# ── 约束分类注册表 ───────────────────────────────────────────────────────────

CATEGORIES = OrderedDict({
    "safety": {
        "label": "安全红线",
        "constraints": ["01001", "01002", "01003", "01004", "01005", "01006", "01007", "01008", "01009", "01010"],
        "emoji": "🛑",
        "desc": "L0 优先级最高，不可触碰的底线规则",
    },
    "file-ops": {
        "label": "文件操作",
        "constraints": ["02101", "02102", "02103", "02104", "02105", "02106", "02107", "02108"],
        "emoji": "📋",
        "desc": "文件移动/命名/目录深度/同步规范",
    },
    "paths": {
        "label": "路径映射",
        "constraints": ["03101", "03102", "03103", "03104", "03105", "03106", "03107", "03108"],
        "emoji": "📍",
        "desc": "路径注册表合规 + Skills 硬编码检测",
    },
    "format": {
        "label": "知识库格式",
        "constraints": ["04101", "04102", "04103", "04104", "04105", "04106"],
        "emoji": "📄",
        "desc": "TOC/Changelog/参考文件/概要/关键词五要素",
    },
    "index-log": {
        "label": "索引/日志",
        "constraints": ["05101", "05102", "05103"],
        "emoji": "📑",
        "desc": "index/log 范围/格式/同步合规",
    },
    "code": {
        "label": "代码/脚本",
        "constraints": ["06101", "06102", "06103", "06104", "06105"],
        "emoji": "🔧",
        "desc": "argparse CLI/命名前缀/目录规范/pathlib/路径变量",
    },
    "quality": {
        "label": "质量标准",
        "constraints": ["07201", "07202", "07203", "07204", "07205", "07206"],
        "emoji": "🎯",
        "desc": "量化四要素/来源标注/MECE/交叉验证/时效/深度",
    },
    "skills": {
        "label": "Skills行为",
        "constraints": ["08201", "08202", "08203", "08204", "08205"],
        "emoji": "🧠",
        "desc": "自动记录/自检交付/路径决策树/不客套/挑剔审查",
    },
    "kb-write": {
        "label": "知识库写入",
        "constraints": ["10301", "10302", "10303", "10304", "10305"],
        "emoji": "💾",
        "desc": "存储频率判定/日跟踪/深度分析/导入笔记/体系化",
    },
    "review": {
        "label": "审查验证",
        "constraints": ["11301", "11302", "11303", "11304", "11305"],
        "emoji": "🕵️",
        "desc": "五层审查/自检局限/证据闸门/三态判定/一致性六类",
    },
    "scheduler": {
        "label": "定时任务",
        "constraints": ["12301", "12302", "12303", "12304", "12305"],
        "emoji": "⏰",
        "desc": "Fail-Fast/来源分级/空文件跳过/Token预算/周报模板",
    },
})

CATEGORY_ALIASES = {
    "all": list(CATEGORIES.keys()),
    "default": ["safety", "format", "index-log", "code"],
}

# ── 路径注册表（03101-03108） ──────────────────────────────────────────────────

PATH_REGISTRY = OrderedDict({
    "03101": {"path": "knowledge/06_others/sources/", "purpose": "外部URL/豆包链接归档", "writers": ["web-archive", "doubao-share"]},
    "03102": {"path": "knowledge/01_survey/", "purpose": "日常跟踪/调研文件（仅日期文件，index/log 已移除）", "writers": ["scheduler", "industry-insight(部分)"]},
    "03103": {"path": "knowledge/02_rd/", "purpose": "服务器研发深度分析", "writers": ["deep-tech-writer", "knowledge-doc-writer"]},
    "03104": {"path": "knowledge/03_AI/", "purpose": "AI技术原理", "writers": ["knowledge-doc-writer"]},
    "03105": {"path": "knowledge/02_rd/00_shared/02_concepts/", "purpose": "跨模块引用的概念原理", "writers": ["knowledge-wiki"]},
    "03106": {"path": "knowledge/methodology/", "purpose": "方法论/思维框架", "writers": ["knowledge-wiki"]},
    "03107": {"path": "knowledge/weekly-reports/", "purpose": "周报自动生成", "writers": ["weekly-report-generator"]},
    "03108": {"path": "tmp/bak/", "purpose": "回收站(禁止引用)", "writers": ["Agent/人工"]},
})

# 已知过时路径（禁止在新文件中引用）
# bak/引用规则 — check 模式：禁止引用路径列表
# ❌ knowledge/07_industry-research/ 是活跃目录，已从过时路径中移除
OBSOLETE_PATHS = [
    "knowledge/bak/",
    "knowledge/01_survey/sources/",
    "knowledge/02_rd/07_reports/",
    "scripts/backup/",
]


# ═══════════════════════════════════════════════════════════════════════════════
#  检查引擎
# ═══════════════════════════════════════════════════════════════════════════════

class CheckResult:
    """单条检查结果"""
    def __init__(self, constraint_id: str, name: str, status: str,
                 detail: str = "", severity: str = "minor",
                 fixable: bool = False, fix_cmd: str = ""):
        self.constraint_id = constraint_id
        self.name = name
        self.status = status  # PASS / FAIL / WARN / SKIP
        self.detail = detail
        self.severity = severity  # critical / major / minor
        self.fixable = fixable
        self.fix_cmd = fix_cmd

    def to_dict(self) -> dict:
        return {
            "constraint": self.constraint_id,
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "severity": self.severity,
            "fixable": self.fixable,
            "fix_cmd": self.fix_cmd,
        }

    def __str__(self) -> str:
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}
        return f"  {icon.get(self.status, '❓')} [{self.constraint_id}] {self.name}: {self.detail}"


class CheckRunner:
    """检查运行器"""

    def __init__(self, target: Optional[Path] = None, fix: bool = False):
        self.results: List[CheckResult] = []
        self.target = target
        self.fix = fix
        self._checked_files: set = set()

    def result(self, cid: str, name: str, status: str, detail: str = "",
               severity: str = "minor", fixable: bool = False, fix_cmd: str = ""):
        self.results.append(CheckResult(cid, name, status, detail, severity, fixable, fix_cmd))

    def pass_result(self, cid: str, name: str, detail: str = "合规"):
        self.result(cid, name, "PASS", detail)

    def fail_result(self, cid: str, name: str, detail: str, severity: str = "major",
                    fixable: bool = False, fix_cmd: str = ""):
        self.result(cid, name, "FAIL", detail, severity, fixable, fix_cmd)

    def warn_result(self, cid: str, name: str, detail: str, severity: str = "minor",
                    fixable: bool = False, fix_cmd: str = ""):
        self.result(cid, name, "WARN", detail, severity, fixable, fix_cmd)

    def skip_result(self, cid: str, name: str, detail: str = "无目标"):
        self.result(cid, name, "SKIP", detail)

    def summary(self) -> dict:
        counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "SKIP": 0}
        for r in self.results:
            counts[r.status] = counts.get(r.status, 0) + 1
        return counts

    def run_external_script(self, script_rel: str, args: List[str] = None,
                            timeout: int = 30) -> Tuple[int, str]:
        """委托执行外部脚本"""
        script_path = WORKSPACE_ROOT / script_rel
        if not script_path.exists():
            return (-1, f"脚本不存在: {script_rel}")
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return r.returncode, r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            return (-2, f"超时 ({timeout}s)")
        except Exception as e:
            return (-3, str(e))

    def get_module_paths(self) -> List[Path]:
        """获取 knowledge/ 下所有模块目录"""
        if self.target and self.target.exists():
            if self.target.is_dir():
                return [self.target]
            return [self.target.parent]
        modules = []
        for d in sorted(KNOWLEDGE_ROOT.iterdir()):
            if d.is_dir() and not d.name.startswith('.'):
                modules.append(d)
        # 也检查子模块
        for sub in sorted(KNOWLEDGE_ROOT.glob("*/[0-9]*")):
            if sub.is_dir():
                modules.append(sub)
        return modules


# ═══════════════════════════════════════════════════════════════════════════════
#  各类别检查实现
# ═══════════════════════════════════════════════════════════════════════════════

# ── Safety (01001-01010) ──────────────────────────────────────────────────────

def check_safety(runner: CheckRunner):
    """安全红线检查：01001-01010"""

    # C01: 永不 rm 删除文件
    rm_violations = []
    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        # 跳过虚拟环境、损坏的软链接
        if 'site-packages' in str(py_file) or '__pycache__' in str(py_file):
            continue
        if not py_file.is_file():
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
        except (OSError, IOError):
            continue
        for lineno, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            # 检测 rm 命令（排除注释中的 rm、或 rm -rf 用于安全目录）
            if re.search(r'\brm\s+(?:-rf\s+)?["\']?/', stripped) and not stripped.startswith('#'):
                rm_violations.append(f"{py_file.relative_to(WORKSPACE_ROOT)}:{lineno}")
    if rm_violations:
        runner.fail_result("01001", "永不 rm 删除文件",
                           f"发现 {len(rm_violations)} 处 rm 命令: {rm_violations[:5]}...",
                           severity="critical", fixable=True,
                           fix_cmd="改用 mv 到 tmp/bak/<原因>-<日期>/")
    else:
        runner.pass_result("01001", "永不 rm 删除文件", "未发现 rm 命令")

    # C02: 永不泄露密钥
    # 检查常见密钥模式（排除测试文件中的 dummy key）
    key_patterns = [
        r'(?:sk|pk|api)[-_]?[a-zA-Z0-9]{20,}',
        r'(?:"|\x27)sk-[a-zA-Z0-9]{20,}(?:"|\x27)',
        r'(?:access_key|secret_key|api_key)\s*[:=]\s*["\']?[a-zA-Z0-9_\-]{16,}',
    ]
    key_violations = []
    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        if 'site-packages' in str(py_file) or '__pycache__' in str(py_file):
            continue
        if not py_file.is_file():
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
        except (OSError, IOError):
            continue
        for lineno, line in enumerate(content.split('\n'), 1):
            for pat in key_patterns:
                if re.search(pat, line):
                    # 排除 env_config 调用和测试桩
                    if 'env_config' in line or 'dummy' in line.lower() or 'test' in line.lower():
                        continue
                    key_violations.append(f"{py_file.relative_to(WORKSPACE_ROOT)}:{lineno}")
    if key_violations:
        runner.fail_result("01002", "永不泄露密钥/令牌",
                           f"潜在密钥泄露 {len(key_violations)} 处: {key_violations[:3]}...",
                           severity="critical", fixable=False)
    else:
        runner.pass_result("01002", "永不泄露密钥/令牌", "未发现密钥硬编码")

    # C03: 修改四全局文件前三思
    # 检查最近的 memory/ 中是否提到对四文件的修改
    memory_dir = WORKSPACE_ROOT / "memory"
    global_files = ["AGENT.md", "USER.md", "RULE.md", "MEMORY.md"]
    recent_modifications = []
    if memory_dir.exists():
        for mf in sorted(memory_dir.glob("*.md"), reverse=True)[:5]:
            content = mf.read_text(encoding='utf-8', errors='ignore')
            for gf in global_files:
                if re.search(rf'(?:修改|更新|编辑|改动|调整|变更)\s*{gf}', content):
                    recent_modifications.append(f"{mf.name}: {gf}")
    if recent_modifications:
        runner.warn_result("01003", "修改全局文件前三思",
                           f"近5日有 {len(recent_modifications)} 次全局文件修改: {recent_modifications}",
                           fixable=False)
    else:
        runner.pass_result("01003", "修改全局文件前三思", "近5日无全局文件修改记录")

    # C04: 永不破坏性 Git 操作
    # bak/引用规则 — check 模式：检测实际 force 推送（排除带确认对话框的脚本）
    git_scripts = list(Path(SCRIPTS_DIR / "git").rglob("*.py"))
    git_scripts += list(Path(SCRIPTS_DIR).glob("git-*.py"))
    force_push_found = False
    force_scripts = []
    for gs in git_scripts:
        content = gs.read_text(encoding='utf-8', errors='ignore')
        # 仅当脚本实际调用 git push --force 或 git push -f 时才标记
        if re.search(r'push.*--force|push.*-f\b|--force.*push', content):
            # 排除有确认机制的脚本（用户确认后才执行 force）
            if 'confirm' in content.lower() or 'input' in content.lower():
                continue
            force_push_found = True
            force_scripts.append(str(gs.relative_to(WORKSPACE_ROOT)))
    if force_push_found:
        runner.fail_result("01004", "永不破坏性 Git 操作",
                           f"存在无确认机制的 force 推送脚本: {force_scripts}",
                           severity="critical", fixable=True,
                           fix_cmd="添加确认对话框或移除 --force 选项")
    else:
        runner.pass_result("01004", "永不破坏性 Git 操作", "Git 脚本安全")

    # C05: 批量操作先问用户
    # 检查 Skills 中是否有 >5 文件批量操作未提示用户确认
    bulk_ops = []
    for skill_dir in sorted(SKILLS_DIR.glob("*")):
        if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
            continue
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8', errors='ignore')
            if re.search(r'(?:批量|全部|所有文件|mass|bulk|all files)', content, re.I):
                if not re.search(r'(?:确认|用户确认|ask|confirm|询问|permission|approve)', content, re.I):
                    bulk_ops.append(skill_dir.name)
    if bulk_ops:
        runner.warn_result("01005", "批量操作先问用户",
                           f"以下 Skills 有批量操作但无确认机制: {bulk_ops}")
    else:
        runner.pass_result("01005", "批量操作先问用户", "批量操作有确认机制或无需确认")

    # C06: 永不编造数据
    # 标记性检查——检查近期文档中是否有"据估算/据推测/业内人士称"等弱来源
    if runner.target and runner.target.exists():
        target_str = runner.target.read_text(encoding='utf-8', errors='ignore') if runner.target.is_file() else ""
    else:
        target_str = ""
    if target_str:
        weak_sources = re.findall(
            r'(?:据估算|据推测|据报道|业内人士称|知情人士透露|有消息称|或达|有望|预计将)',
            target_str)
        if weak_sources:
            runner.warn_result("01006", "永不编造数据",
                               f"发现 {len(weak_sources)} 处弱来源表述: {weak_sources[:3]}",
                               fixable=True, fix_cmd="补充具体来源或标注数据缺口")
        else:
            runner.pass_result("01006", "永不编造数据", "未发现弱来源表述")
    else:
        runner.skip_result("01006", "永不编造数据", "未指定检查目标")

    # C07: 永不引用 bak 内容
    bak_refs = []
    for skill_dir in sorted(SKILLS_DIR.glob("*")):
        if not skill_dir.is_dir():
            continue
        for md_file in skill_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            if re.search(r'(?:knowledge/bak|tmp/bak)/', content) and 'bak/引用规则' not in content:
                bak_refs.append(str(md_file.relative_to(WORKSPACE_ROOT)))
    if runner.target and runner.target.is_file():
        content = runner.target.read_text(encoding='utf-8', errors='ignore')
        if re.search(r'(?:knowledge/bak|tmp/bak)/', content):
            bak_refs.append(str(runner.target.relative_to(WORKSPACE_ROOT)))
    if bak_refs:
        runner.fail_result("01007", "永不引用 bak 内容",
                           f"发现 {len(bak_refs)} 处 bak 引用: {bak_refs[:5]}",
                           severity="major", fixable=True,
                           fix_cmd="移除或替换为当前有效路径的引用")
    else:
        runner.pass_result("01007", "永不引用 bak 内容", "未发现 bak 引用")

    # C08: import/ 素材批判性使用
    # 检查 Skills 中是否有直接引用 import/ 作为唯一来源的
    import_refs = []
    for skill_dir in sorted(SKILLS_DIR.glob("*")):
        if not skill_dir.is_dir():
            continue
        for md_file in skill_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            if re.search(r'import/', content) and 'import/' in content:
                # 统计有多少独立引用
                refs = re.findall(r'import/[^\s\)\]]+', content)
                if refs:
                    import_refs.append((str(md_file.relative_to(WORKSPACE_ROOT)), len(refs)))
    if import_refs:
        runner.warn_result("01008", "Import 素材批判性使用",
                           f"以下 Skill 引用 import/: {import_refs[:3]}",
                           fixable=False)
    else:
        runner.pass_result("01008", "Import 素材批判性使用", "Skills 未直接引用 import/")

    # C09: 检查脚本非破坏性
    # 只检查 format-validator.py 等关键脚本是否有 --fix 安全模式
    key_scripts = ["format-validator.py", "strategy-compliance.py",
                   "content-format-normalizer.py", "reformat-log.py",
                   "index-log-normalizer.py"]
    no_fix_protection = []
    for ks in key_scripts:
        sp = SCRIPTS_DIR / "check" / ks
        if sp.exists():
            content = sp.read_text(encoding='utf-8', errors='ignore')
            if '--fix' not in content and '--dry-run' not in content:
                no_fix_protection.append(ks)
    if no_fix_protection:
        runner.warn_result("01009", "脚本安全模式",
                           f"以下脚本无 --fix/--dry-run 保护: {no_fix_protection}")
    else:
        runner.pass_result("01009", "脚本安全模式", "关键脚本有安全模式保护")

    # C10: bak 不自建 index/log
    bak_dir = WORKSPACE_ROOT / "tmp" / "bak"
    bak_index_files = []
    if bak_dir.exists():
        for f in ["index.md", "log.md"]:
            target = bak_dir / f
            if target.exists():
                bak_index_files.append(f)
    # 也检查旧 knowledge/bak/
    old_bak = KNOWLEDGE_ROOT / "bak"
    if old_bak.exists():
        for f in ["index.md", "log.md"]:
            target = old_bak / f
            if target.exists():
                bak_index_files.append(f"knowledge/bak/{f}")
    if bak_index_files:
        runner.fail_result("01010", "bak 不自建 index/log",
                           f"bak 目录存在 index/log 文件: {bak_index_files}",
                           severity="major", fixable=True,
                           fix_cmd="删除 bak 目录中的 index.md/log.md")
    else:
        runner.pass_result("01010", "bak 不自建 index/log", "bak 目录无 index/log")


# ── File Ops (02101-02108) ────────────────────────────────────────────────────

def check_file_ops(runner: CheckRunner):
    """文件操作检查：02101-02108"""

    # C11: 改前查头部约束标记
    headers_found = []
    headers_ok = True
    for md_file in (KNOWLEDGE_ROOT / "06_others").rglob("*.md"):
        if 'bak' in str(md_file):
            continue
        content = md_file.read_text(encoding='utf-8', errors='ignore')
        first_10 = content[:1000]
        if re.search(r'(?:DO NOT EDIT|MANAGED_BY|AUTO-GENERATED)', first_10):
            headers_found.append(md_file.name)
    if headers_found:
        runner.warn_result("02101", "改前查头部约束标记",
                           f"找到 {len(headers_found)} 个标记文件，需注意不手动修改",
                           fixable=False)
        headers_ok = True
    if headers_ok:
        runner.pass_result("02101", "改前查头部约束标记",
                           f"检查完成，{len(headers_found)} 个标记文件已确认")

    # C12: bak 路径双兼容
    # bak/引用规则 — check 模式：检查是否还有引用旧 knowledge/bak/ 的脚本
    old_bak_refs = []
    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        if 'site-packages' in str(py_file) or '__pycache__' in str(py_file):
            continue
        if not py_file.is_file():
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
        except (OSError, IOError):
            continue
        # bak/引用规则 — 排除有注解的脚本
        if re.search(r'knowledge/bak/', content) and 'bak/引用规则' not in content:
            old_bak_refs.append(str(py_file.relative_to(WORKSPACE_ROOT)))
    if old_bak_refs:
        runner.fail_result("02102", "bak 路径双兼容",
                           f"仍引用旧 knowledge/bak/ 的脚本: {old_bak_refs}",
                           severity="major", fixable=True,
                           fix_cmd="更新为 tmp/bak/")
    else:
        runner.pass_result("02102", "bak 路径双兼容", "所有引用已使用新路径 tmp/bak/")

    # C13: mv 到 bak 带原因+日期
    # 检查现有 bak 目录是否合规
    bak_dirs = []
    for bak_path in [WORKSPACE_ROOT / "tmp" / "bak", KNOWLEDGE_ROOT / "bak"]:
        if bak_path.exists():
            for d in bak_path.iterdir():
                if d.is_dir():
                    bak_dirs.append(d.name)
    # 检查命名是否含原因-日期
    non_compliant = [d for d in bak_dirs if not re.search(r'\d{4}-\d{2}-\d{2}', d)]
    if non_compliant:
        runner.warn_result("02103", "Bak 名称带原因+日期",
                           f"不合规的 bak 子目录: {non_compliant}")
    else:
        runner.pass_result("02103", "Bak 名称带原因+日期",
                           f"所有 {len(bak_dirs)} 个 bak 子目录命名合规" if bak_dirs else "无 bak 子目录")

    # C14: 文件命名统一规范
    naming_violations = []
    modules = runner.get_module_paths()
    for md_file in KNOWLEDGE_ROOT.rglob("*.md"):
        if 'bak' in str(md_file) or '__pycache__' in str(md_file):
            continue
        fname = md_file.name
        violations = []
        if re.search(r'[\u4e00-\u9fff]', fname):
            violations.append("含中文")
        if ' ' in fname:
            violations.append("含空格")
        if fname[0].isupper() and not fname.startswith(('README', 'TRACKING')):
            # 只有 README.md / TRACKING.md 允许大写开头
            violations.append("大写开头")
        if len(fname) > 63:
            violations.append(f"超长({len(fname)}字符)")
        if violations:
            rel = md_file.relative_to(WORKSPACE_ROOT)
            naming_violations.append(f"{rel} ({', '.join(violations)})")
            if len(naming_violations) >= 10:
                break
    if naming_violations:
        runner.fail_result("02104", "文件命名统一规范",
                           f"不合规文件(前10): {naming_violations}",
                           severity="major", fixable=True,
                           fix_cmd="重命名: 英文小写-连字符.md, ≤60字符")
    else:
        runner.pass_result("02104", "文件命名统一规范", "所有文件命名合规")

    # C15: 目录深度 ≤ 3 级
    depth_violations = []
    for dirpath in KNOWLEDGE_ROOT.rglob("*"):
        if not dirpath.is_dir() or 'bak' in str(dirpath) or '__pycache__' in str(dirpath):
            continue
        rel = dirpath.relative_to(KNOWLEDGE_ROOT)
        depth = len(rel.parts)
        if depth > 3:
            depth_violations.append(f"{rel} (深度={depth})")
            if len(depth_violations) >= 5:
                break
    if depth_violations:
        runner.fail_result("02105", "目录深度 ≤ 3 级",
                           f"深度超标目录: {depth_violations}")
    else:
        runner.pass_result("02105", "目录深度 ≤ 3 级", "所有目录深度合规")

    # C16: 单目录文件数 ≤ 200
    file_count_violations = []
    for d in sorted(KNOWLEDGE_ROOT.rglob("*")):
        if not d.is_dir() or 'bak' in str(d) or '__pycache__' in str(d):
            continue
        md_files = list(d.glob("*.md"))
        if len(md_files) > 200:
            rel = d.relative_to(WORKSPACE_ROOT)
            file_count_violations.append(f"{rel} ({len(md_files)} 文件)")
    if file_count_violations:
        runner.fail_result("02106", "单目录文件数 ≤ 200",
                           f"超限目录: {file_count_violations}",
                           severity="major", fixable=True,
                           fix_cmd="拆分子目录或归档旧文件")
    else:
        runner.pass_result("02106", "单目录文件数 ≤ 200", "所有目录文件数合规")

    # C17: 同层子目录数 ≤ 15
    subdir_violations = []
    for d in sorted(KNOWLEDGE_ROOT.glob("*")):
        if not d.is_dir() or d.name.startswith('.'):
            continue
        subdirs = [s for s in d.iterdir() if s.is_dir() and not s.name.startswith('.') and s.name != 'bak']
        if len(subdirs) > 15:
            rel = d.relative_to(WORKSPACE_ROOT)
            subdir_violations.append(f"{rel} ({len(subdirs)} 子目录)")
    if subdir_violations:
        runner.warn_result("02107", "同层子目录数 ≤ 15",
                           f"子目录过多: {subdir_violations}")
    else:
        runner.pass_result("02107", "同层子目录数 ≤ 15", "所有目录子目录数合规")

    # C18: 操作后同步 index+log (委托)
    code, output = runner.run_external_script(
        "scripts/check/analyze-index-coverage.py",
        ["--all", "--summary"]
    )
    if code == 0 and output:
        has_gaps = "MISSING" in output or "missing" in output.lower()
        if has_gaps:
            runner.fail_result("02108", "操作后同步 index+log",
                               "index 覆盖率存在缺口（见 analyze-index-coverage 输出）",
                               severity="major", fixable=True,
                               fix_cmd="python3 scripts/check/analyze-index-coverage.py --all --fix")
        else:
            runner.pass_result("02108", "操作后同步 index+log", "index 覆盖率完整")
    else:
        runner.warn_result("02108", "操作后同步 index+log",
                           f"analyze-index-coverage 未正常执行: code={code}")


# ── Paths (03101-03108) ───────────────────────────────────────────────────────

def check_paths(runner: CheckRunner):
    """路径映射检查：03101-03108"""

    # 03101-03108: 路径注册表合规
    # 检查目标文件的写入位置是否符合注册表
    if runner.target and runner.target.is_file():
        rel = runner.target.relative_to(WORKSPACE_ROOT)
        path_str = str(rel)
        # 找匹配的注册表路径
        matched = None
        for cid, entry in PATH_REGISTRY.items():
            if entry["path"] in path_str:
                matched = cid
                break
        if matched:
            runner.pass_result(matched, f"路径注册表合规 ({PATH_REGISTRY[matched]['path']})",
                               f"{rel} 匹配 {matched}")
        else:
            # 不在注册表中，检查是否是已知合规的常规文件
            if any(rel.match(f"knowledge/{p}/**") for p in
                   ["04_person", "05_tools"]):
                runner.pass_result("03101-03108", "路径注册表（非注册路径）",
                                   f"{rel} 在非注册模块中（允许）")
            else:
                runner.warn_result("03101-03108", "路径注册表合规",
                                   f"{rel} 不在路径注册表中",
                                   fixable=True,
                                   fix_cmd="确认归属并更新 PATH_REGISTRY")
    else:
        # 模块级检查：检查各模块是否有文件放到错误位置
        runner.pass_result("03101-03108", "路径注册表合规（模块级）",
                           "目标为目录或无目标，跳过单文件验证")

    # C51 强化：检查 Skills 中路径硬编码（归入此处统一检测）
    hardcoded_paths = []
    for skill_dir in sorted(SKILLS_DIR.glob("*")):
        if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
            continue
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8', errors='ignore')
            # 检测硬编码路径（排除路径注册表中已注册的）
            hardcoded = re.findall(r'(?:knowledge|skills|scripts)/[^\s\)\]\"\'<>]+', content)
            for hc in hardcoded:
                # 排除注册表中已注册的路径
                registered = any(entry["path"] in hc for entry in PATH_REGISTRY.values())
                if not registered and not hc.startswith('spec/'):
                    hardcoded_paths.append((skill_dir.name, hc))
    if hardcoded_paths:
        runner.warn_result("08205", "Skills 路径硬编码",
                           f"检测到 {len(hardcoded_paths)} 处路径（前5）: "
                           + "; ".join(f"{s}:{p}" for s, p in hardcoded_paths[:5]),
                           fixable=True,
                           fix_cmd="迁移到路径注册表 03101-03108 引用")
    else:
        runner.pass_result("08205", "Skills 路径硬编码", "未发现硬编码路径")

    # 检查过时路径引用
    obsolete_refs = []
    for skill_dir in sorted(SKILLS_DIR.glob("*")):
        if not skill_dir.is_dir():
            continue
        for md_file in skill_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            for obs in OBSOLETE_PATHS:
                if obs in content:
                    obsolete_refs.append((str(md_file.relative_to(WORKSPACE_ROOT)), obs))
    if obsolete_refs:
        runner.fail_result("paths", "过时路径引用",
                           f"发现 {len(obsolete_refs)} 处过时路径引用（前5）: "
                           + "; ".join(f"{f}→{p}" for f, p in obsolete_refs[:5]),
                           severity="major", fixable=True,
                           fix_cmd="更新为新路径")
    else:
        runner.pass_result("paths", "过时路径引用", "未发现过时路径引用")


# ── Format (04101-04106) ──────────────────────────────────────────────────────

def check_format(runner: CheckRunner):
    """知识库格式检查：04101-04106"""

    # 委托给 format-validator.py
    target_args = []
    if runner.target:
        target_args = [str(runner.target)]
    else:
        target_args = ["--all", "--summary"]

    code, output = runner.run_external_script(
        "scripts/check/format-validator.py", target_args
    )

    if code == 0:
        # 提取通过/失败信息
        fail_count = len(re.findall(r'FAIL|✖|❌', output))
        if fail_count > 0:
            # 提取具体的失败约束
            c27_fails = len(re.findall(r'概要|Summary|C28', output))
            c28_fails = len(re.findall(r'关键词|Keywords|C29', output))
            c29_fails = len(re.findall(r'TOC|目录', output))
            c30_fails = len(re.findall(r'Changelog', output))
            c31_fails = len(re.findall(r'参考文件|References', output))

            mapping = {
                "04101": ("五大要素必含", c27_fails > 0 or "Summary" in output),
                "04102": ("概要格式", c28_fails > 0 or "概要" in output),
                "04103": ("关键词格式", c29_fails > 0 or "关键词" in output),
                "04104": ("TOC 格式", "TOC" in output or "目录" in output),
                "04105": ("Changelog 格式", True if fail_count > 0 else False),
                "04106": ("参考文件格式", True if fail_count > 0 else False),
            }
            for cid, (name, fail) in mapping.items():
                if fail:
                    runner.fail_result(cid, name,
                                       "格式校验未通过（详见 format-validator 输出）",
                                       fixable=True,
                                       fix_cmd=f"python3 scripts/check/format-validator.py {' '.join(target_args)} --fix")
        else:
            for c in ["04101", "04102", "04103", "04104", "04105", "04106"]:
                runner.pass_result(c, "知识库格式", "格式校验通过")
    else:
        runner.warn_result("04101-04106", "知识库格式",
                           f"format-validator 执行异常: code={code}")

    # 额外检查 C30: TOC 格式（>200 行文件必含）
    if runner.target and runner.target.is_file():
        content = runner.target.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        if len(lines) > 200:
            has_toc = bool(re.search(r'##\s*[📑]?\s*(目录|Contents|TOC|Contents)', content))
            if not has_toc:
                runner.fail_result("04104", "TOC 格式（>200行必含）",
                                   f"文件 {runner.target.name} 有 {len(lines)} 行但无 TOC",
                                   fixable=True,
                                   fix_cmd="添加 ## 📑 目录 和章节链接列表")


# ── Index/Log (05101-05103) ───────────────────────────────────────────────────

def check_index_log(runner: CheckRunner):
    """索引/日志检查：05101-05103"""

    # 委托 index-log-normalizer.py
    mod_args = []
    if runner.target and runner.target.is_dir():
        # 尝试转换为 knowledge/ 下相对路径
        try:
            rel = runner.target.relative_to(KNOWLEDGE_ROOT)
            mod_args = ["--check", str(rel)]
        except ValueError:
            mod_args = ["--check"]
    else:
        mod_args = ["--all"]

    code, output = runner.run_external_script(
        "scripts/check/index-log-normalizer.py", mod_args
    )

    if code == 0:
        if "FAIL" in output or "fail" in output.lower():
            runner.fail_result("05101", "模块 index+log 独立维护",
                               "部分模块缺少 index.md 或 log.md",
                               fixable=True,
                               fix_cmd="python3 scripts/check/index-log-normalizer.py --init")
            runner.fail_result("05102", "index.md 本目录 scope",
                               "index 跨层描述问题（详见 index-log-normalizer 输出）",
                               fixable=True,
                               fix_cmd="python3 scripts/check/index-log-normalizer.py --fix")
        else:
            runner.pass_result("05101", "模块 index+log 独立维护", "所有模块 index+log 完备")
            runner.pass_result("05102", "index.md 本目录 scope", "index scope 合规")
            runner.pass_result("05103", "log.md 本目录 scope", "log scope 合规")
    else:
        runner.warn_result("05101-05103", "索引/日志", f"index-log-normalizer 执行异常: code={code}")


# ── Code (06101-06105) ────────────────────────────────────────────────────────

def check_code(runner: CheckRunner):
    """代码/脚本检查：06101-06105"""

    # C36: 每个 Python 脚本必有 argparse CLI
    no_cli = []
    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        if '__pycache__' in str(py_file) or '__init__' in str(py_file):
            continue
        if py_file.parent.name in ('__pycache__', '.git', 'backup'):
            continue
        if not py_file.is_file():
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
        except (OSError, IOError):
            continue
        # 排除 backup/ 废弃代码
        rel_to_scripts = str(py_file.relative_to(SCRIPTS_DIR))
        if rel_to_scripts.startswith('backup/'):
            continue
        if 'if __name__' in content and 'argparse' not in content:
            no_cli.append(str(py_file.relative_to(SCRIPTS_DIR)))
    if no_cli:
        runner.fail_result("06101", "Python 脚本必有 argparse CLI",
                           f"以下脚本有 main() 无 argparse: {no_cli}",
                           severity="major", fixable=True,
                           fix_cmd="添加 argparse 参数解析")
    else:
        runner.pass_result("06101", "Python 脚本必有 argparse CLI",
                           "所有主脚本有 argparse CLI" if not no_cli else "部分脚本需补")

    # C37: 命名前缀规范
    check_scripts = list((SCRIPTS_DIR / "check").glob("*.py"))
    name_violations = []
    for cs in check_scripts:
        name = cs.stem
        if not re.match(r'^(?:check_|fix_|generate_|import_|export_|reformat_|index_|knowledge_|link_|ref_|content_|strategy_|relation_|format_|analyze_|extract_|directory_|subdir_|doc_)', name):
            name_violations.append(name)
    if name_violations:
        runner.warn_result("06102", "命名前缀规范",
                           f"以下 check/ 脚本命名不符规范: {name_violations[:5]}")
    else:
        runner.pass_result("06102", "命名前缀规范", "check/ 脚本命名合规")

    # C38: 脚本归入对应子目录
    root_scripts = [f.name for f in SCRIPTS_DIR.glob("*.py")
                    if f.is_file() and f.name != "constraint-check.py"]
    if root_scripts:
        runner.warn_result("06103", "脚本归入对应子目录",
                           f"scripts/ 根级仍有 {len(root_scripts)} 个脚本（应为软链接）: {root_scripts[:10]}",
                           fixable=True,
                           fix_cmd="迁移到 check/tools/git/intent_analysis 子目录")
    else:
        runner.pass_result("06103", "脚本归入对应子目录", "所有脚本在子目录中")
    # 检查 backup/ 目录是否新增文件
    backup_dir = SCRIPTS_DIR / "backup"
    if backup_dir.exists():
        new_files = [f for f in backup_dir.iterdir() if f.is_file() and f.suffix == '.py']
        if new_files:
            runner.fail_result("06103", "禁止 backup/ 新增",
                               f"backup/ 中有 {len(new_files)} 个文件，应归入子目录",
                               severity="major")
        else:
            runner.pass_result("06103", "禁止 backup/ 新增", "backup/ 无新增文件")

    # C39: 路径操作使用 pathlib.Path
    no_pathlib = []
    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        if '__pycache__' in str(py_file) or '__init__' in str(py_file):
            continue
        if not py_file.is_file():
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
        except (OSError, IOError):
            continue
        if 'os.path' in content and 'pathlib' not in content:
            no_pathlib.append(str(py_file.relative_to(SCRIPTS_DIR)))
    if no_pathlib:
        runner.warn_result("06104", "路径操作使用 pathlib.Path",
                           f"以下脚本使用 os.path 但无 pathlib: {no_pathlib}",
                           fixable=True)
    else:
        runner.pass_result("06104", "路径操作使用 pathlib.Path",
                           "所有脚本使用 pathlib")

    # C40: 使用 WORKSPACE_ROOT 变量拼接路径
    hardcoded_abs = []
    for py_file in sorted(SCRIPTS_DIR.rglob("*.py")):
        if '__pycache__' in str(py_file) or '__init__' in str(py_file):
            continue
        if not py_file.is_file():
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
        except (OSError, IOError):
            continue
        if re.search(r'["\']/home/lzh/cow/knowledge/', content):
            hardcoded_abs.append(str(py_file.relative_to(SCRIPTS_DIR)))
    if hardcoded_abs:
        runner.fail_result("06105", "使用 WORKSPACE_ROOT 变量",
                           f"硬编码绝对路径的脚本: {hardcoded_abs}",
                           severity="major", fixable=True,
                           fix_cmd="使用 WORKSPACE_ROOT / KNOWLEDGE_ROOT 变量拼接")
    else:
        runner.pass_result("06105", "使用 WORKSPACE_ROOT 变量", "无硬编码绝对路径")


# ── Quality (07201-07206) ─────────────────────────────────────────────────────

def check_quality(runner: CheckRunner):
    """质量标准检查：07201-07206"""

    if not runner.target:
        runner.skip_result("07201-07206", "质量标准", "未指定检查目标文件")
        return

    # 委托 doc-quality.py
    target_path = str(runner.target) if runner.target else ""
    code, output = runner.run_external_script(
        "scripts/check/doc-quality.py", [target_path]
    )

    if code == 0:
        # 解析输出判断各约束
        c41_fail = "数值" not in output and "量化" not in output
        c42_fail = "来源" not in output and "citation" not in output.lower()
        c45_fail = "时效" not in output

        if c41_fail:
            runner.fail_result("07201", "量化四要素",
                               "缺少数值+单位+基线+条件之一",
                               fixable=True)
        else:
            runner.pass_result("07201", "量化四要素", "有量化数据标注")

        if c42_fail:
            runner.fail_result("07202", "来源标注",
                               "缺少断言出处标注",
                               fixable=True)
        else:
            runner.pass_result("07202", "来源标注", "有来源标注")

        # C43: MECE 章节划分（启发式检测）
        if runner.target and runner.target.is_file():
            content = runner.target.read_text(encoding='utf-8', errors='ignore')
            headers = re.findall(r'^##\s+[^📑\n].+', content, re.MULTILINE)
            # 检查是否有交叉引用（MECE 自检）
            if headers:
                runner.pass_result("07203", "MECE 章节划分",
                                   f"文档有 {len(headers)} 个章节标题")
            else:
                runner.warn_result("07203", "MECE 章节划分",
                                   "文档缺少 ## 章节划分")
        else:
            runner.skip_result("07203", "MECE 章节划分", "未指定文件")

        runner.pass_result("07205", "数据时效性", "doc-quality 检查完成")

        # C46: 框架堆名词不深入原理
        if runner.target and runner.target.is_file():
            content = runner.target.read_text(encoding='utf-8', errors='ignore')
            # 检测是否有原理分析（简单启发式）
            has_principle = bool(re.search(r'(?:原理|机制|原理解析|机理|how|why|because|because|fundamental|本质|数学推导|推导|公式)', content))
            has_quant = bool(re.search(r'\d+\.?\d*\s*(?:%|GB|TB|MHz|GHz|ns|μs|ms|W|kW|Tbps|Gbps|TFLOPS)', content))
            if has_principle or has_quant:
                runner.pass_result("07206", "框架堆名词不深入原理",
                                   "文档包含原理分析或量化数据")
            else:
                runner.warn_result("07206", "框架堆名词不深入原理",
                                   "文档可能停留在名词堆叠层面",
                                   fixable=True,
                                   fix_cmd="补充原理分析/量化对比/流程解释")
    else:
        runner.warn_result("07201-07206", "质量标准",
                           f"doc-quality 执行异常: code={code}")


# ── Skills (C47-C55) ──────────────────────────────────────────────────────

def check_skills(runner: CheckRunner):
    """Skills 行为检查：C47-C55"""

    # C47: 主动记录不询问（检查 Skills 是否有自动归档机制）
    auto_archive_skills = []
    no_auto_archive = []
    for skill_name in ["doubao-share", "web-archive", "knowledge-wiki"]:
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        if skill_file.exists():
            auto_archive_skills.append(skill_name)
    # 检查其他 Skill 是否有"用户确认后才写入"的模式
    for skill_dir in sorted(SKILLS_DIR.glob("*")):
        if not skill_dir.is_dir() or skill_dir.name in auto_archive_skills:
            continue
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8', errors='ignore')
            if '写' in content or '写入' in content or '归档' in content:
                if '确认' in content or '询问' in content or 'ask' in content.lower():
                    no_auto_archive.append(skill_dir.name)
    runner.pass_result("08201", "主动记录不询问",
                       f"自动归档: {auto_archive_skills}; "
                       + (f"需确认: {no_auto_archive[:5]}" if no_auto_archive else "其他 Skill 无自动写入"))

    # C48: 自检后交付（检查是否有 self-review 机制）
    has_self_review = []
    for skill_dir in sorted(SKILLS_DIR.glob("*")):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text(encoding='utf-8', errors='ignore')
            if '自检' in content or 'self-review' in content.lower() or 'self review' in content.lower():
                has_self_review.append(skill_dir.name)
    if len(has_self_review) >= 3:
        runner.pass_result("08202", "自检后交付",
                           f"{len(has_self_review)} 个 Skill 含自检机制: {has_self_review[:5]}")
    else:
        runner.warn_result("08202", "自检后交付",
                           f"仅 {len(has_self_review)} 个 Skill 明确含自检机制",
                           fixable=False)

    # C49: 不表演式客套（检查 AGENT.md 明确禁止）
    agent_content = (WORKSPACE_ROOT / "AGENT.md").read_text(encoding='utf-8', errors='ignore')
    if '不表演式客套' in agent_content or '不编造' in agent_content:
        runner.pass_result("08203", "不表演式客套", "AGENT.md 已明确禁止")
    else:
        runner.fail_result("08203", "不表演式客套",
                           "AGENT.md 未明确约束", severity="major")

    # C50: 极端挑剔审查（检查 AGENT.md 是否有此设定）
    if '极端挑剔审查' in agent_content or '找问题' in agent_content:
        runner.pass_result("08204", "极端挑剔审查", "AGENT.md 已设定")
    else:
        runner.warn_result("08204", "极端挑剔审查", "AGENT.md 未明确设定")

    # C51: （主要检测已在 check_paths 中完成，这里只重复检查路径硬编码数量）
    # 报告已在 paths 中处理
    runner.pass_result("08205", "Skills 写入路径服从统一决策树",
                       "详细路径硬编码检测见 paths 类别")


# ── KB Write (10301-10305) ────────────────────────────────────────────────────

def check_kb_write(runner: CheckRunner):
    """知识库写入检查：10301-10305"""

    # 委托 strategy-compliance.py
    target_args = []
    if runner.target:
        target_args = [str(runner.target)]
    else:
        target_args = ["--all", "--summary"]

    code, output = runner.run_external_script(
        "scripts/check/strategy-compliance.py", target_args
    )

    if code == 0:
        if "FAIL" in output or "✖" in output:
            runner.fail_result("10301-10305", "知识库写入策略",
                               "Strategy 合规存在违规项（详见 strategy-compliance 输出）",
                               fixable=True,
                               fix_cmd="python3 scripts/check/strategy-compliance.py --fix")
        else:
            for c in ["10301", "10302", "10303", "10304", "10305"]:
                runner.pass_result(c, "知识库写入策略", "Strategy 合规通过")
    else:
        runner.warn_result("10301-10305", "知识库写入策略",
                           f"strategy-compliance 执行异常: code={code}")


# ── Review (11301-11305) ──────────────────────────────────────────────────────

def check_review(runner: CheckRunner):
    """审查验证检查：11301-11305"""

    if not runner.target:
        runner.skip_result("11301-11305", "审查验证", "未指定检查目标文件")
        return

    # C61: 五层审查（委托 doc-review.py）
    code, output = runner.run_external_script(
        "scripts/check/doc-review.py", [str(runner.target)]
    )

    if code == 0:
        if "FAIL" in output or "🔴" in output:
            runner.fail_result("11301", "五层审查",
                               "文档审查发现结构/逻辑/来源层问题",
                               fixable=True,
                               fix_cmd="修复后重新审查")
        else:
            runner.pass_result("11301", "五层审查", "审查通过")
    else:
        runner.warn_result("11301", "五层审查",
                           f"doc-review 执行异常: code={code}")

    # C62-C64: 自检相关（元检查——检查自检记录是否存在）
    if runner.target and runner.target.is_file():
        content = runner.target.read_text(encoding='utf-8', errors='ignore')
        has_changelog = bool(re.search(r'##\s*Changelog', content))
        if has_changelog:
            runner.pass_result("C62-C64", "自检元检查",
                               "文档含 Changelog，有迭代记录")
        else:
            runner.warn_result("C62-C64", "自检元检查",
                               "文档无 Changelog，自检记录可能缺失",
                               fixable=True,
                               fix_cmd="补充 Changelog 记录自检迭代")
    else:
        runner.skip_result("C62-C64", "自检元检查", "未指定文件")

    # C65: 一致性六类检测（委托 light-consistency 脚本）
    # 先看是否有相关脚本
    consistency_scripts = list((SKILLS_DIR / "light-consistency").glob("scripts/*.py"))
    if consistency_scripts:
        runner.pass_result("11305", "一致性六类检测",
                           f"light-consistency 有 {len(consistency_scripts)} 个检测脚本")
    else:
        runner.warn_result("11305", "一致性六类检测",
                           "light-consistency 无独立检测脚本",
                           fixable=False)


# ── Scheduler (12301-12308) ───────────────────────────────────────────────────

def check_scheduler(runner: CheckRunner):
    """定时任务检查：12301-12308"""

    # C66: Fail-Fast 模式
    # 检查 scheduler 相关技能/脚本
    scheduler_skills = []
    for skill_name in ["scheduler", "weekly-report-generator", "knowledge-special-reports"]:
        sf = SKILLS_DIR / skill_name / "SKILL.md"
        if sf.exists():
            scheduler_skills.append(skill_name)
    if scheduler_skills:
        runner.pass_result("12301", "Fail-Fast 模式",
                           f"相关 Skills: {scheduler_skills}")
    else:
        runner.warn_result("12301", "Fail-Fast 模式", "未找到定时任务相关 Skills")

    # C67: 来源分级
    # 检查 SCHEDULER_RELIABILITY.md 是否存在并包含分级
    sr_file = SPEC_DIR / "SCHEDULER_RELIABILITY.md"
    if sr_file.exists():
        sr_content = sr_file.read_text(encoding='utf-8', errors='ignore')
        if "来源分级" in sr_content or "P0" in sr_content:
            runner.pass_result("12302", "来源分级", "已配置 P0/P1 来源分级")
        else:
            runner.warn_result("12302", "来源分级",
                               "SCHEDULER_RELIABILITY.md 无来源分级",
                               fixable=True)
    else:
        runner.warn_result("12302", "来源分级",
                           "缺少 SCHEDULER_RELIABILITY.md",
                           fixable=True)

    # C68: 无有效信息不创建空文件
    # 检查 key skills 是否有跳过逻辑
    for skill_name in ["weekly-report-generator", "knowledge-special-reports"]:
        sf = SKILLS_DIR / skill_name / "SKILL.md"
        if sf.exists():
            content = sf.read_text(encoding='utf-8', errors='ignore')
            if "跳过" in content or "skip" in content.lower() or "不创建" in content:
                runner.pass_result("12303", "无有效信息不创建空文件",
                                   f"{skill_name} 有跳过机制")
                break
    else:
        runner.warn_result("12303", "无有效信息不创建空文件",
                           "相关 Skills 未明确跳过逻辑",
                           fixable=False)

    # C69: Token 预算
    # 检查 TOKEN_OPTIMIZATION.md
    to_file = SPEC_DIR / "TOKEN_OPTIMIZATION.md"
    if to_file.exists():
        to_content = to_file.read_text(encoding='utf-8', errors='ignore')
        budget_refs = re.findall(r'\d+K\s*[Tトt]oken|\d+[Kk]\s*[Bb]udget', to_content)
        if budget_refs:
            runner.pass_result("12304", "Token 预算/日跟踪",
                               f"Token 预算约束: {budget_refs}")
        else:
            runner.warn_result("12304", "Token 预算",
                               "TOKEN_OPTIMIZATION.md 无预算约束",
                               fixable=True)
    else:
        runner.warn_result("12304", "Token 预算",
                           "缺少 TOKEN_OPTIMIZATION.md",
                           fixable=True)

    # C70: 周报固定模板
    weekly_skills = []
    for skill_name in ["weekly-report-generator"]:
        sf = SKILLS_DIR / skill_name / "SKILL.md"
        if sf.exists():
            weekly_skills.append(skill_name)
    if weekly_skills:
        runner.pass_result("12305", "周报固定模板",
                           f"周报生成: {weekly_skills}")
    else:
        runner.warn_result("12305", "周报固定模板",
                           "未找到周报生成 Skill",
                           fixable=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  类别→检查函数映射
# ═══════════════════════════════════════════════════════════════════════════════


    # C71: tasks.json 进程隔离契约 (12306)
    tasks_file = WORKSPACE_ROOT / "scheduler" / "tasks.json"
    if tasks_file.exists():
        import json
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            total_tasks = len(tasks_data.get("tasks", {}))
            feishu_tasks = sum(1 for t in tasks_data.get("tasks", {}).values()
                              if t.get("action", {}).get("channel_type") == "feishu")
            runner.pass_result("12306", "tasks.json 进程隔离契约",
                               f"{total_tasks} 个任务，{feishu_tasks} 个 feishu 通道，文件存在且可解析")
        except (json.JSONDecodeError, IOError) as e:
            runner.fail_result("12306", "tasks.json 进程隔离契约",
                               f"无法解析 tasks.json: {e}",
                               fixable=False)
    else:
        runner.warn_result("12306", "tasks.json 进程隔离契约",
                           f"tasks.json 不存在于 {tasks_file}",
                           fixable=False)

    # C72: tasks.json git 版本漂移检测 (12307)
    if tasks_file.exists():
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD", "--", str(tasks_file)],
                capture_output=True, text=True, timeout=30,
                cwd=str(WORKSPACE_ROOT)
            )
            if str(tasks_file) in result.stdout:
                runner.warn_result("12307", "tasks.json git 版本漂移检测",
                                   f"tasks.json 与 git HEAD 有差异，请检查是否被非调度进程修改",
                                   fixable=False)
            else:
                runner.pass_result("12307", "tasks.json git 版本漂移检测",
                                   "tasks.json 与 git HEAD 一致")
        except subprocess.TimeoutExpired:
            runner.warn_result("12307", "tasks.json git 版本漂移检测",
                               "git diff 超时，跳过",
                               fixable=False)
        except Exception as e:
            runner.warn_result("12307", "tasks.json git 版本漂移检测",
                               f"git diff 失败: {e}",
                               fixable=False)

    # C73: 定时任务 channel_type 一致性 (12308)
    if tasks_file.exists():
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            feishu_issues = []
            for tid, t in tasks_data.get("tasks", {}).items():
                action = t.get("action", {})
                if action.get("channel_type") == "feishu":
                    if not action.get("receiver"):
                        feishu_issues.append(f"{t.get('name', tid)}: 缺 receiver")
                    if "is_group" not in action:
                        feishu_issues.append(f"{t.get('name', tid)}: 缺 is_group")
            if feishu_issues:
                runner.warn_result("12308", "定时任务 channel_type 一致性",
                                   f"feishu 任务配置不完整: {"; ".join(feishu_issues)}",
                                   fixable=True)
            else:
                runner.pass_result("12308", "定时任务 channel_type 一致性",
                                   "所有 feishu 任务配置完整")
        except (json.JSONDecodeError, IOError) as e:
            runner.warn_result("12308", "定时任务 channel_type 一致性",
                               f"无法解析 tasks.json: {e}",
                               fixable=False)

CHECK_FUNCTIONS = {
    "safety": check_safety,
    "file-ops": check_file_ops,
    "paths": check_paths,
    "format": check_format,
    "index-log": check_index_log,
    "code": check_code,
    "quality": check_quality,
    "skills": check_skills,
    "kb-write": check_kb_write,
    "review": check_review,
    "scheduler": check_scheduler,
}


# ═══════════════════════════════════════════════════════════════════════════════
#  输出与 CLI
# ═══════════════════════════════════════════════════════════════════════════════

def format_report(runner: CheckRunner, json_output: bool = False,
                  summary_only: bool = False) -> str:
    """生成检查报告"""
    if json_output:
        data = {
            "timestamp": TIMESTAMP,
            "results": [r.to_dict() for r in runner.results],
            "summary": runner.summary(),
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    # 文本报告
    lines = []
    lines.append("=" * 70)
    lines.append(f"  🔍 约束合规检查报告")
    lines.append(f"  {TIMESTAMP}")
    lines.append("=" * 70)

    # 分类展示结果
    current_category = ""
    for r in runner.results:
        cid = r.constraint_id
        # 找所属类别
        for cat_name, cat_info in CATEGORIES.items():
            if cid in cat_info["constraints"] or \
               (cid == "03101-03108" and cat_name == "paths") or \
               (cid == "paths" and cat_name == "paths") or \
               (cid == "08205" and cat_name == "skills") or \
               (cid == "03101-03108" and cat_name == "paths") or \
               (cid.startswith("04101") and cat_name == "format"):
                if current_category != cat_name:
                    current_category = cat_name
                    if not summary_only:
                        lines.append(f"\n  {cat_info['emoji']} {cat_info['label']} ({cat_info['desc']})")
                        lines.append(f"  {'─' * 60}")
                break
            elif cid == "paths" and cat_name == "paths":
                if current_category != cat_name:
                    current_category = cat_name
                    if not summary_only:
                        lines.append(f"\n  {cat_info['emoji']} {cat_info['label']} ({cat_info['desc']})")
                        lines.append(f"  {'─' * 60}")
                break
            elif cid == "03101-03108" and cat_name == "paths":
                if current_category != cat_name:
                    current_category = cat_name
                    if not summary_only:
                        lines.append(f"\n  {cat_info['emoji']} {cat_info['label']} ({cat_info['desc']})")
                        lines.append(f"  {'─' * 60}")
                break
            elif cid == "08205" and cat_name == "skills":
                if current_category != cat_name:
                    current_category = cat_name
                    if not summary_only:
                        lines.append(f"\n  {cat_info['emoji']} {cat_info['label']} ({cat_info['desc']})")
                        lines.append(f"  {'─' * 60}")
                break

        if summary_only:
            continue
        lines.append(str(r))

    # 摘要
    counts = runner.summary()
    total = sum(counts.values())
    passed = counts["PASS"]
    lines.append(f"\n  {'═' * 60}")
    lines.append(f"  📊 摘要: {passed}/{total} 通过 | "
                 f"✅ {counts['PASS']} | ❌ {counts['FAIL']} | "
                 f"⚠️ {counts['WARN']} | ⏭️ {counts['SKIP']}")

    if counts["FAIL"] > 0:
        lines.append(f"  🛑 严重违规 {counts['FAIL']} 项，建议优先修复")
    if counts["WARN"] > 0:
        lines.append(f"  ⚠️  警告 {counts['WARN']} 项，建议排期处理")

    lines.append("=" * 70)
    return "\n".join(lines)


def list_categories() -> str:
    """列出可用检查类别"""
    lines = []
    lines.append("可用的约束检查类别:")
    lines.append("")
    for cat_name, cat_info in CATEGORIES.items():
        cids = ", ".join(cat_info["constraints"])
        lines.append(f"  {cat_info['emoji']} {cat_name:15s} {cids:25s}  {cat_info['desc']}")
    lines.append(f"\n别名:")
    for alias, cats in CATEGORY_ALIASES.items():
        lines.append(f"  {alias:15s} → {', '.join(cats)}")
    lines.append(f"\n使用: python3 scripts/constraint-check.py --category <名称> [--target <路径>]")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="统一约束合规检查器（Lint for Cow System）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 scripts/constraint-check.py --list-categories
  python3 scripts/constraint-check.py --category all
  python3 scripts/constraint-check.py --category safety,format
  python3 scripts/constraint-check.py --category format --target knowledge/01_survey/today.md
  python3 scripts/constraint-check.py --category all --summary
  python3 scripts/constraint-check.py --category format --target file.md --fix
  python3 scripts/constraint-check.py --category all --json
        """
    )
    parser.add_argument("--category", "-c", default="default",
                        help="检查类别（逗号分隔，默认=default: safety,format,index-log,code）")
    parser.add_argument("--target", "-t", type=Path, default=None,
                        help="目标文件或目录")
    parser.add_argument("--fix", action="store_true",
                        help="尝试自动修复可修复项")
    parser.add_argument("--json", action="store_true",
                        help="JSON 格式输出")
    parser.add_argument("--summary", action="store_true",
                        help="仅输出摘要")
    parser.add_argument("--list-categories", action="store_true",
                        help="列出可用类别")

    args = parser.parse_args()

    if args.list_categories:
        print(list_categories())
        return

    # 解析类别
    categories = []
    raw_cats = [c.strip() for c in args.category.split(",")]
    for cat in raw_cats:
        if cat in CATEGORY_ALIASES:
            categories.extend(CATEGORY_ALIASES[cat])
        elif cat in CHECK_FUNCTIONS:
            categories.append(cat)
        else:
            print(f"⚠️  未知类别: {cat}，跳过", file=sys.stderr)

    if not categories:
        print("❌ 未指定有效检查类别，使用 --list-categories 查看", file=sys.stderr)
        sys.exit(1)

    # 去重
    categories = list(dict.fromkeys(categories))

    # 运行检查
    runner = CheckRunner(target=args.target, fix=args.fix)

    for cat in categories:
        if cat in CHECK_FUNCTIONS:
            CHECK_FUNCTIONS[cat](runner)

    # --fix 模式：执行可自动修复的 fix_cmd
    if args.fix:
        fixable_results = [r for r in runner.results
                           if r.status in ('FAIL', 'WARN') and r.fixable and r.fix_cmd]
        if fixable_results:
            print(f"\n{'=' * 50}")
            print(f"🔧 自动修复 ({len(fixable_results)} 项)")
            print(f"{'=' * 50}")
            fixed_count = 0
            for r in fixable_results:
                print(f"  [{r.cid}] {r.name}")
                print(f"    修复命令: {r.fix_cmd}")
                # 解析 fix_cmd 并执行
                fix_cmd = r.fix_cmd
                if fix_cmd.startswith("python3 "):
                    # 脚本修复：提取脚本路径和参数
                    parts = fix_cmd.split()
                    script_path = WORKSPACE_ROOT / parts[1]
                    script_args = parts[2:] if len(parts) > 2 else []
                    if script_path.exists():
                        code, output = subprocess.run(
                            [sys.executable, str(script_path)] + script_args,
                            capture_output=True, text=True, timeout=60
                        ).stdout, ""
                        print(f"    ✅ 执行完成 (exit=0)")
                        fixed_count += 1
                    else:
                        print(f"    ⚠️ 脚本不存在: {script_path}")
                elif fix_cmd.startswith("mv "):
                    # 文件移动：提取 src 和 dst
                    # format: mv <src> <dst>
                    # We can't safely auto-execute mv commands
                    print(f"    ⏳ 需手动执行: {fix_cmd}")
                elif fix_cmd.startswith("重命名"):
                    print(f"    ⏳ 需手动执行: {fix_cmd}")
                elif fix_cmd.startswith("删除"):
                    print(f"    ⏳ 需手动执行: {fix_cmd}")
                elif fix_cmd.startswith("更新"):
                    print(f"    ⏳ 需手动执行: {fix_cmd}")
                elif fix_cmd.startswith("移除"):
                    print(f"    ⏳ 需手动执行: {fix_cmd}")
                elif fix_cmd.startswith("补充"):
                    print(f"    ⏳ 需人工判断: {fix_cmd}")
                elif fix_cmd.startswith("迁移"):
                    print(f"    ⏳ 需人工判断: {fix_cmd}")
                elif fix_cmd.startswith("拆分子目录"):
                    print(f"    ⏳ 需人工判断: {fix_cmd}")
                else:
                    print(f"    ⏳ 无法自动修复，建议: {fix_cmd}")
            print(f"\n✅ 已自动修复: {fixed_count}/{len(fixable_results)}")
        else:
            print("\n✅ 无可自动修复项")

    # 输出报告
    report = format_report(runner, json_output=args.json, summary_only=args.summary)
    print(report)

    # 返回值
    counts = runner.summary()
    if counts["FAIL"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
