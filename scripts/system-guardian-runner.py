#!/usr/bin/env python3
"""
system-guardian-runner.py — 系统守护统一运行器

一键运行四重守护:
  1. Task Integrity (check-tasks-integrity.py)
  2. Skills Registration (check-skills-registration.py)
  3. Config Consistency (轻量检查)
  4. 引用契约 (link-ref-audit.py — 文档引用脚本须真实存在)

用法:
  python3 scripts/system-guardian-runner.py          # 全量检查
  python3 scripts/system-guardian-runner.py --json    # JSON 输出
  python3 scripts/system-guardian-runner.py --guard A # 仅 A
  python3 scripts/system-guardian-runner.py --guard B # 仅 B
  python3 scripts/system-guardian-runner.py --guard C # 仅 C
  python3 scripts/system-guardian-runner.py --guard D # 仅 D（引用契约）
"""

import json
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime

WORKSPACE = (Path(__file__).resolve().parent).resolve()
SCRIPTS_DIR = WORKSPACE
CHECK_DIR = SCRIPTS_DIR / "check"


def run_guard_a() -> dict:
    """Task Integrity"""
    script = CHECK_DIR / "check-tasks-integrity.py"
    if not script.exists():
        return {"guard": "A", "status": "⚠️ 脚本不存在", "details": str(script)}

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        return {"guard": "A", "status": "✅ 通过" if result.returncode == 0 else "⚠️ 有警告",
                "output": result.stdout.strip()[:200]}
    except subprocess.TimeoutExpired:
        return {"guard": "A", "status": "🔴 超时", "details": "check-tasks-integrity.py 执行超过 30s"}
    except Exception as e:
        return {"guard": "A", "status": "🔴 错误", "details": str(e)}


def run_guard_b() -> dict:
    """Skills Registration"""
    script = CHECK_DIR / "check-skills-registration.py"
    if not script.exists():
        return {"guard": "B", "status": "⚠️ 脚本不存在", "details": str(script)}

    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.stdout.strip():
            return json.loads(result.stdout)
        return {"guard": "B", "status": "✅ 通过"}
    except subprocess.TimeoutExpired:
        return {"guard": "B", "status": "🔴 超时"}
    except Exception as e:
        return {"guard": "B", "status": "🔴 错误", "details": str(e)}


def run_guard_c() -> dict:
    """Config Consistency (轻量)"""
    issues = []

    # C1: Git 工作漂移
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
            cwd=WORKSPACE
        )
        changes = result.stdout.strip().split("\n") if result.stdout.strip() else []
        # 过滤非关键文件
        critical_changes = [c for c in changes if not c.startswith("?? tmp/") and not c.startswith("?? memory/")]
        if critical_changes:
            issues.append(f"Git: {len(critical_changes)} 个文件有变更")
    except Exception:
        issues.append("Git: 检查失败")

    # C2: 映射表覆盖
    mapping_file = WORKSPACE / "scripts" / "skills-scripts-mapping.md"
    if mapping_file.exists():
        mapping_scripts = set()
        with open(mapping_file, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line and ".py" in line:
                    parts = line.split("|")
                    for p in parts:
                        p = p.strip()
                        if p.endswith(".py"):
                            mapping_scripts.add(p)
        # 扫描实际脚本
        actual_scripts = set()
        for py_file in SCRIPTS_DIR.rglob("*.py"):
            rel = py_file.relative_to(WORKSPACE)
            actual_scripts.add(str(rel))
        # 简单比对
        unmapped = [s for s in actual_scripts if s not in mapping_scripts and "__pycache__" not in s]
        if unmapped:
            issues.append(f"映射表: {len(unmapped)} 个脚本未在映射表中")

    # C3: 废弃文件
    bak_dir = WORKSPACE / "tmp" / "bak"
    if bak_dir.exists():
        bak_items = list(bak_dir.iterdir())
        if len(bak_items) > 20:
            issues.append(f"tmp/bak/: {len(bak_items)} 个条目，建议清理")

    return {
        "guard": "C",
        "status": "⚠️ 有建议" if issues else "✅ 干净",
        "issues": issues
    }


def run_guard_d() -> dict:
    """引用契约检测（link-ref-audit）"""
    script = CHECK_DIR / "link-ref-audit.py"
    if not script.exists():
        return {"guard": "D", "status": "⚠️ 脚本不存在", "details": str(script)}
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--scope", "all", "--json"],
            capture_output=True, text=True, timeout=60
        )
        if result.stdout.strip():
            data = json.loads(result.stdout)
            broken = data.get("broken_count", 0)
            total = data.get("stats", {}).get("total_refs", 0)
            status = "✅ 通过" if broken == 0 else f"🔴 {broken} 处断裂"
            return {
                "guard": "D",
                "status": status,
                "total_refs": total,
                "broken": broken,
                "ambiguous": data.get("ambiguous_count", 0),
            }
        return {"guard": "D", "status": "✅ 通过"}
    except subprocess.TimeoutExpired:
        return {"guard": "D", "status": "🔴 超时"}
    except Exception as e:
        return {"guard": "D", "status": "🔴 错误", "details": str(e)}


def main():
    parser = argparse.ArgumentParser(description="系统守护统一运行器")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--guard", choices=["A", "B", "C", "D", "ALL"], default="ALL")
    args = parser.parse_args()

    guards = {"A": run_guard_a, "B": run_guard_b, "C": run_guard_c, "D": run_guard_d}
    results = {}
    status_map = []

    for name, func in guards.items():
        if args.guard != "ALL" and args.guard != name:
            continue
        result = func()
        results[f"guard_{name}"] = result
        status_map.append(f"{result.get('status', '?')}")

    full_status = "✅" if all("🔴" not in s for s in status_map) else "⚠️" if any("⚠️" in s for s in status_map) else "🔴"

    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": full_status,
        "guards": results
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"\n🛡️  系统守护报告 — {report['timestamp']}")
        print(f"{'='*50}")
        print(f"总体状态: {full_status}\n")

        for name, r in results.items():
            label = {"guard_A": "A · Task Integrity", "guard_B": "B · Skills Registration", "guard_C": "C · Config Consistency"}
            print(f"  [{r.get('status', '?')}] {label.get(name, name)}")
            if r.get("orphaned"):
                print(f"     游离 Skill: {len(r['orphaned'])}")
            if r.get("dead_refs"):
                print(f"     死引用: {len(r['dead_refs'])}")
            if r.get("issues"):
                for issue in r["issues"]:
                    print(f"     ⚠️ {issue}")
            print()

        print(f"提示: 运行 --json 获取详细报告 | --guard A/B/C 单项运行")

    sys.exit(0 if "🔴" not in status_map else 1)


if __name__ == "__main__":
    main()
