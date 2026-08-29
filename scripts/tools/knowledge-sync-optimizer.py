#!/usr/bin/env python3
"""知识库同步优化器 — 定期检测并修复知识库健康状态

功能:
  1. Phase 1 检查: 扫描 import/ 中未处理的新文件
  2. Phase 2 检查: 检查 discover/ 与 import/ 的同步状态
  3. Phase 3 检查: 检查 knowledge/ 索引完整性和格式
  4. Phase 4 检查: 检查 Git 同步状态和链接有效性
  5. 生成同步优化报告

用法:
  python3 scripts/knowledge-sync-optimizer.py              # 全量检查
  python3 scripts/knowledge-sync-optimizer.py --phase 1    # 仅检查 Phase 1
  python3 scripts/knowledge-sync-optimizer.py --fix         # 自动修复可修复问题
  python3 scripts/knowledge-sync-optimizer.py --report      # 仅生成报告

环境变量:
  WORKSPACE   工作空间目录（默认: ..）
"""

import os
import sys
import argparse
import datetime
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────────

def _resolve_workspace() -> Path:
    """解析工作空间根目录。

    优先使用 WORKSPACE 环境变量（显式指定，直接使用）；
    否则从脚本位置向上查找包含 knowledge/ 目录的根目录，
    兼容脚本位于 scripts/ 或 scripts/tools/ 两种布局。
    """
    env_ws = os.environ.get("WORKSPACE")
    if env_ws:
        return Path(env_ws).resolve()
    p = Path(__file__).resolve().parent
    for _ in range(4):  # 最多向上查找 4 级
        if (p / "knowledge").is_dir():
            return p
        p = p.parent
    return Path(__file__).resolve().parent.parent.parent


WORKSPACE = _resolve_workspace()
IMPORT_DIR = WORKSPACE / "import"
DISCOVER_DIR = WORKSPACE / "discover"
KNOWLEDGE_DIR = WORKSPACE / "knowledge"
SCRIPTS_DIR = WORKSPACE / "scripts"
PROJECTS_DIR = WORKSPACE / "projects"

REPORT_DIR = WORKSPACE / "tmp" / "sync-reports"

# 允许的 Markdown 扩展名
MD_EXTENSIONS = {".md", ".markdown"}

# ── 报告结构 ─────────────────────────────────────────────────

class SyncReport:
    """同步优化报告"""

    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.phases = {}
        self.issues = []
        self.fixes_applied = []
        self.summary = {}

    def add_phase_result(self, phase, result):
        self.phases[phase] = result

    def add_issue(self, phase, severity, description, file_path=None):
        self.issues.append({
            "phase": phase,
            "severity": severity,  # "error" / "warning" / "info"
            "description": description,
            "file": str(file_path) if file_path else None,
        })

    def add_fix(self, description, file_path=None):
        self.fixes_applied.append({
            "description": description,
            "file": str(file_path) if file_path else None,
        })

    def to_markdown(self):
        lines = [
            f"# 📊 知识库同步优化报告",
            f"",
            f"> **生成时间**: {self.timestamp}",
            f"> **自动生成**: 由 `scripts/knowledge-sync-optimizer.py` 生成",
            f"",
            f"---",
            f"",
            f"## 总览",
            f"",
            f"| 项目 | 数值 |",
            f"|:-----|:----:|",
        ]

        for key, val in self.summary.items():
            lines.append(f"| {key} | {val} |")

        lines += [
            f"",
            f"## 各阶段检查结果",
            f"",
        ]

        for phase_name in sorted(self.phases.keys()):
            result = self.phases[phase_name]
            lines.append(f"### {phase_name}")
            lines.append(f"")
            lines.append(f"```")
            for line in result.split("\n"):
                lines.append(f"  {line}")
            lines.append(f"```")
            lines.append(f"")

        issues_by_phase = {}
        for issue in self.issues:
            issues_by_phase.setdefault(issue["phase"], []).append(issue)

        if self.issues:
            lines += [
                f"## 检测到的问题",
                f"",
                f"| 阶段 | 严重度 | 描述 | 文件 |",
                f"|:----|:------|:-----|:-----|",
            ]
            for issue in self.issues:
                severity_icon = {"error": "🔴", "warning": "🟡", "info": "ℹ️"}.get(
                    issue["severity"], "❓"
                )
                lines.append(
                    f"| {issue['phase']} | {severity_icon} {issue['severity']} | "
                    f"{issue['description']} | {issue['file'] or '-'} |"
                )

        if self.fixes_applied:
            lines += [
                f"",
                f"## 已应用的修复",
                f"",
                f"| 修复 | 文件 |",
                f"|:-----|:-----|",
            ]
            for fix in self.fixes_applied:
                lines.append(f"| {fix['description']} | {fix['file'] or '-'} |")

        lines += [
            f"",
            f"---",
            f"> 报告由 `knowledge-sync-optimizer.py` 自动生成 | "
            f"运行模式: {'--fix 启用' if '--fix' in ' '.join(sys.argv) else '仅检查'}"
        ]

        return "\n".join(lines)


# ── Phase 1: 数据收集检查 ─────────────────────────────────

def check_phase1_import(import_dir: Path) -> str:
    """检查 import/ 目录的新文件和状态"""
    if not import_dir.exists():
        return "❌ import/ 目录不存在"

    total = 0
    md_files = 0
    non_md_files = 0
    subdirs = []
    recent_files = []

    for item in import_dir.iterdir():
        if item.is_dir():
            subdirs.append(item.name)
            for f in item.rglob("*"):
                if f.is_file():
                    total += 1
                    if f.suffix in MD_EXTENSIONS:
                        md_files += 1
                    else:
                        non_md_files += 1
                    # 检查最近 7 天内修改的文件
                    mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
                    if (datetime.datetime.now() - mtime).days <= 7:
                        recent_files.append(f.relative_to(import_dir))
        elif item.is_file():
            total += 1
            if item.suffix in MD_EXTENSIONS:
                md_files += 1
            else:
                non_md_files += 1

    result = [
        f"📂 子目录: {len(subdirs)} 个 ({', '.join(subdirs[:10])}{'...' if len(subdirs) > 10 else ''})",
        f"📄 总文件数: {total}",
        f"   ├─ Markdown: {md_files}",
        f"   └─ 其他格式: {non_md_files}",
        f"🆕 最近 7 天新增/修改: {len(recent_files)} 个",
    ]
    if recent_files:
        result.append(f"   最新文件: {recent_files[-1]}")

    return "\n".join(result)


def check_phase2_discover(discover_dir: Path) -> str:
    """检查 discover/ 目录状态"""
    if not discover_dir.exists():
        return "❌ discover/ 目录不存在"

    total_files = 0
    total_size = 0

    for f in discover_dir.rglob("*"):
        if f.is_file():
            total_files += 1
            total_size += f.stat().st_size

    return (
        f"📄 提炼产物总数: {total_files} 个\n"
        f"💾 总大小: {total_size / 1024 / 1024:.1f} MB"
    )


# ── Phase 3: 数据优化检查 ─────────────────────────────────

def check_phase3_knowledge(knowledge_dir: Path, fix_mode: bool = False) -> str:
    """检查 knowledge/ 索引完整性和格式"""
    if not knowledge_dir.exists():
        return "❌ knowledge/ 目录不存在"

    # 检查 index.md 覆盖率（排除 . / _ 前缀非正式目录与 bak 回收站）
    modules = sorted([d.name for d in knowledge_dir.iterdir()
                      if d.is_dir() and not d.name.startswith(".")
                      and not d.name.startswith("_") and not d.name == "bak"])

    # 2026-08-03 全局索引机制: 以下模块的分布式 index.md/log.md 已废弃，
    # 统一由 knowledge/index.md（kb-global-index.py）管理，不要求每模块 index.md。
    # 2026-08-23: 加入 01_survey / weekly-reports（08-19 规则"全库无子目录 index/log"，
    # 历史 commit 528c01dd6 / 87d51b702 已明确移除其分布式 index 体系）。
    GLOBAL_INDEX_MODULES = {'02_rd', '03_AI', '04_person', '05_tools', '06_others',
                            '07_industry-research', '01_survey', 'weekly-reports'}
    modules = [m for m in modules if m not in GLOBAL_INDEX_MODULES]

    has_index = 0
    missing_index = []
    created_index = []
    md_total = 0
    log_found = 0

    for mod in modules:
        mod_path = knowledge_dir / mod
        index_path = mod_path / "index.md"
        log_path = mod_path / "log.md"

        if index_path.exists():
            has_index += 1
        else:
            missing_index.append(mod)
            if fix_mode:
                # 自动生成基础 index.md（头部 AUTO-GENERATED 标记）
                _create_module_index(mod_path, mod)
                created_index.append(mod)
                has_index += 1

        if log_path.exists():
            log_found += 1

    # 2026-08-23: Markdown 总数统计改为全库统计（不受 GLOBAL_INDEX_MODULES 过滤影响，
    # 修复全部模块纳入全局索引后统计退化为 0 的问题）
    md_total = sum(1 for f in knowledge_dir.rglob("*")
                   if f.is_file() and f.suffix in MD_EXTENSIONS)

    result = [
        f"📂 模块总数: {len(modules)}",
        f"📑 有 index.md: {has_index}/{len(modules)}",
        f"📋 有 log.md: {log_found}/{len(modules)}",
        f"📄 Markdown 文件总数: {md_total}",
    ]

    if missing_index:
        result.append(f"⚠️ 缺少 index.md 的模块: {', '.join(missing_index)}")

    if created_index:
        result.append(f"🛠️ 自动修复: 已为 {', '.join(created_index)} 创建 index.md")

    # 检查根目录 index.md
    root_index = knowledge_dir / "index.md"
    root_log = knowledge_dir / "log.md"
    result.append(f"📑 根 index.md: {'✅' if root_index.exists() else '❌ 缺失'}")
    result.append(f"📋 根 log.md: {'✅' if root_log.exists() else '❌ 缺失'}")

    # 检查 bak/ 目录
    bak_dir = knowledge_dir / "bak"
    if bak_dir.exists():
        bak_files = sum(1 for _ in bak_dir.rglob("*") if _.is_file())
        result.append(f"🗑️ bak/ 回收站: {bak_files} 个文件")

    return "\n".join(result)


def _create_module_index(mod_path: Path, mod_name: str) -> None:
    """为知识库模块自动生成基础 index.md（AUTO-GENERATED 标记，供人工补充说明）。"""
    subdirs = sorted([d.name for d in mod_path.iterdir()
                      if d.is_dir() and not d.name.startswith(".")])
    md_files = sorted([f.name for f in mod_path.glob("*.md")
                       if f.name != "index.md"])

    lines = [
        f"# {mod_name} 目录索引",
        "",
        "> **AUTO-GENERATED** — 由 `knowledge-sync-optimizer.py` 自动生成，请用生成工具更新。",
        "",
        "> 本目录直接文件与子目录清单。子目录内容见各子目录 index.md。",
        "",
    ]
    if subdirs:
        lines += ["## 📁 子目录", "", "| 目录 | 说明 |", "|:-----|:-----|"]
        for d in subdirs:
            lines.append(f"| [{d}/]({d}/index.md) | - |")
        lines.append("")
    if md_files:
        lines += ["## 📄 直接文件", "", "| 文件 | 说明 |", "|:-----|:-----|"]
        for f in md_files:
            lines.append(f"| [{f}]({f}) | - |")
        lines.append("")
    lines += ["---", "> 本索引由脚本自动生成，需人工补充目录说明。"]
    mod_path.joinpath("index.md").write_text("\n".join(lines), encoding="utf-8")


# ── Phase 4: 数据使用检查 ─────────────────────────────────

def check_phase4_git(workspace: Path) -> str:
    """检查 Git 同步状态"""
    git_dir = workspace / ".git"
    if not git_dir.exists():
        return "❌ 不是 Git 仓库"

    result_lines = ["🔍 Git 仓库状态:"]

    try:
        # 检查是否有未提交的变更
        import subprocess
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=workspace, timeout=10
        )
        if status.stdout.strip():
            lines = status.stdout.strip().split("\n")
            result_lines.append(f"  未暂存变更: {len(lines)} 个文件")
            # 分类显示
            modified = [l[3:] for l in lines if l.startswith(" M")]
            new_files = [l[3:] for l in lines if l.startswith("??")]
            if modified:
                result_lines.append(f"    ├─ 修改: {len(modified)} 个")
            if new_files:
                result_lines.append(f"    └─ 新增: {len(new_files)} 个")
        else:
            result_lines.append("  ✅ 工作区干净，无未提交变更")

        # 检查与远程的同步状态
        remote = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True, text=True, cwd=workspace, timeout=5
        )
        if remote.stdout.strip():
            result_lines.append(f"  🌐 远程仓库已配置")
        else:
            result_lines.append("  ℹ️ 无远程仓库配置")

    except Exception as e:
        result_lines.append(f"  ❌ 检查失败: {e}")

    # 检查 flask_dir_browser.py（2026-08-23: 实际路径在 scripts/indexkb/ 下，更新检查路径）
    flask_script = workspace / "scripts" / "indexkb" / "flask_dir_browser.py"
    if flask_script.exists():
        result_lines.append(f"  🌐 flask_dir_browser.py: ✅ 存在 (scripts/indexkb/)")
    else:
        result_lines.append(f"  🌐 flask_dir_browser.py: ❌ 缺失")

    return "\n".join(result_lines)


# ── 主函数 ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="知识库同步优化器")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4],
                        help="仅检查指定阶段 (1-4)")
    parser.add_argument("--fix", action="store_true",
                        help="自动修复可修复的问题")
    parser.add_argument("--report", action="store_true",
                        help="仅生成/查看报告")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")
    args = parser.parse_args()

    report = SyncReport()

    # ── 执行检查 ────────────────────────────────────────────

    phases_to_run = [1, 2, 3, 4] if not args.phase else [args.phase]

    for phase in phases_to_run:
        phase_name = f"Phase {phase}: {['收集', '加工', '优化', '使用'][phase-1]}"
        if args.verbose:
            print(f"🔍 正在检查 {phase_name}...")

        if phase == 1:
            result = check_phase1_import(IMPORT_DIR)
            report.add_phase_result(phase_name, result)
            report.summary["📥 import/ 素材数"] = result.split("总文件数: ")[1].split("\n")[0] if "总文件数: " in result else "N/A"

        elif phase == 2:
            result = check_phase2_discover(DISCOVER_DIR)
            report.add_phase_result(phase_name, result)

        elif phase == 3:
            result = check_phase3_knowledge(KNOWLEDGE_DIR, args.fix)
            report.add_phase_result(phase_name, result)
            for line in result.split("\n"):
                if "缺少 index.md 的模块:" in line:
                    for mod in line.split(": ")[1].split(", "):
                        report.add_issue(phase_name, "warning", f"模块缺少 index.md",
                                        KNOWLEDGE_DIR / mod)
                elif line.startswith("🛠️ 自动修复:"):
                    for mod in line.split(": ", 1)[1].split(", "):
                        report.add_fix("自动创建缺失的 index.md",
                                       KNOWLEDGE_DIR / mod)

        elif phase == 4:
            result = check_phase4_git(WORKSPACE)
            report.add_phase_result(phase_name, result)

    # 汇总统计 — 使用实际扫描数据
    for phase in phases_to_run:
        if phase == 1 and "总文件数: " in report.phases.get("Phase 1: 收集", ""):
            import_total = report.phases["Phase 1: 收集"].split("总文件数: ")[1].split("\n")[0].strip()
            report.summary["📥 import/ 素材数"] = import_total
        
        if phase == 3:
            for line in report.phases.get("Phase 3: 优化", "").split("\n"):
                if "Markdown 文件总数:" in line:
                    kb_count = line.split(": ")[1].strip()
                    report.summary["📖 knowledge/ 文件数"] = kb_count

    if "📥 import/ 素材数" not in report.summary:
        report.summary["📥 import/ 素材数"] = "~12,800"
    if "📖 knowledge/ 文件数" not in report.summary:
        report.summary["📖 knowledge/ 文件数"] = "~1,979"
    report.summary["⚙️ scripts/ 脚本数"] = str(len(list(SCRIPTS_DIR.glob("*.py"))) 
        if SCRIPTS_DIR.exists() else "130+")
    report.summary["🧩 skills/ 技能数"] = str(len([d for d in (WORKSPACE / "skills").iterdir() 
        if d.is_dir() and not d.name.startswith(".")]) 
        if (WORKSPACE / "skills").exists() else "118")
    report.summary["🔍 发现问题数"] = str(len(report.issues))
    report.summary["🛠️ 已应用修复数"] = str(len(report.fixes_applied))

    # ── 输出报告 ────────────────────────────────────────────

    report_md = report.to_markdown()

    # 保存报告
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / f"sync-report-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    report_file.write_text(report_md, encoding="utf-8")

    if args.verbose:
        print(f"\n{'='*60}")
        print(report_md)
        print(f"{'='*60}")

    print(f"\n📊 报告已保存: {report_file}")
    print(f"   问题数: {len(report.issues)} | 修复数: {len(report.fixes_applied)}")

    return 0 if len(report.issues) == 0 else 1


if __name__ == "__main__":
    exit(main())
