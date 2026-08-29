#!/usr/bin/env python3
"""
check-scheduled-tasks-compliance.py — 定时任务体系合规守护脚本

检测 scheduler/tasks.json 与 skills/industry-insight 配套实现（runner 脚本 +
research_topics.json 配置）是否符合设计文档
`knowledge/05_tools/task-automation/2026-07-31-scheduled-tasks-system-design.md`
的全部约束。

== 用法 ==

  # 完整检查
  python3 scripts/check/check-scheduled-tasks-compliance.py

  # 仅输出 JSON 报告
  python3 scripts/check/check-scheduled-tasks-compliance.py --json

  # 修复模式（输出建议命令，不自动改时间/描述）
  python3 scripts/check/check-scheduled-tasks-compliance.py --fix

  # 只跑单项检查
  python3 scripts/check/check-scheduled-tasks-compliance.py --check window

== 检查项 ==

  C1  (T001): tasks.json 可解析 & 任务数 & 全 enabled
  C2  (T002): 时间窗口 21:00~08:00（白名单: 用户指定日报 08:10）
  C3  (T003): 34 调研任务描述必须引用 research_task_runner.py guide 入口
  C4  (T004): 描述中 guide --task "X" 的名字能在 research_topics.json 精确解析
  C5  (T005): 34 任务输出路径两两唯一 & 不含废弃共享文件 industry-research/YYYY-MM-DD.md
  C6  (T006): 每个输出 module 目录存在 index.md + log.md
  C7  (T007): 调研任务描述长度 <= 400 chars（防规则回流膨胀）
  C8  (T008): 非调研任务描述非空
  C9  (T009): cron 表达式合法（5 段，分钟/小时字段范围）
  C10 (T010): research_task_runner.py 内建九项规则关键词齐全
  W1  (T011): 名字时间标签与 cron 一致性（WARN，历史遗留）

== 退出码 ==

  0 = 全部 PASS（可含 WARNING）
  1 = 有 FAIL
"""

import sys
import json
import argparse
import re
from pathlib import Path

# ── 路径 ───────────────────────────────────────────────────────────────────────
WORKSPACE_ROOT = (Path(__file__).resolve().parent.parent.parent).resolve()
TASKS_FILE = WORKSPACE_ROOT / "scheduler" / "tasks.json"
RUNNER = WORKSPACE_ROOT / "skills" / "industry-insight" / "scripts" / "research_task_runner.py"
CONFIG = WORKSPACE_ROOT / "skills" / "industry-insight" / "configs" / "research_topics.json"

# 设计文档路径（供报告引用）
DESIGN_DOC = "spec/design-011-scheduled-tasks-system-design.md"

# 时间窗口: 21:00 ~ 次日 08:00 → cron 小时 ∈ {21,22,23,0,1,2,3,4,5,6,7}
ALLOWED_HOURS = {21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7}

# 例外白名单: task_id -> 原因（用户指定，设计文档 §6.2）
EXCEPTIONS = {
    "443f5e47": "用户指定: 知识库日报 08:10（日报体系硬化窗口，见设计文档 §6.2）",
}

# 描述长度阈值（防规则回流/膨胀回归）
DESC_MAX_CHARS = 400

# runner 九项规则关键词（C10）
RULES_KEYWORDS = [
    "token 管理", "源可靠性", "文档质量", "内容丰度", "文档生成格式",
    "输出可靠性", "index/log", "零产出占位", "check-gap",
]

# 废弃共享文件模式（顶层 industry-research/YYYY-MM-DD.md）
SHARED_FILE_RE = re.compile(r"01_survey/industry-research/\d{4}-\d{2}-\d{2}\.md$")
# 名字中的时间标签模式，如 "(2:30)" "(12:30)" "(01:00)"
NAME_TIME_RE = re.compile(r"\((\d{1,2}):(\d{2})\)")


# ── 数据加载 ───────────────────────────────────────────────────────────────────

def load_tasks_json():
    """加载 scheduler/tasks.json → dict(task_id -> task)"""
    if not TASKS_FILE.exists():
        return None, f"tasks.json 不存在: {TASKS_FILE}"
    try:
        data = json.load(open(TASKS_FILE, encoding="utf-8"))
    except Exception as e:
        return None, f"tasks.json 解析失败: {e}"
    tasks = data if isinstance(data, list) else data.get("tasks", data)
    if not isinstance(tasks, dict) or not tasks:
        return None, "tasks.json 缺少 tasks 对象或为空"
    return tasks, None


def load_topics_config():
    """加载 research_topics.json → (tasks dict, err)"""
    if not CONFIG.exists():
        return None, f"主题配置缺失: {CONFIG}"
    try:
        data = json.load(open(CONFIG, encoding="utf-8"))
    except Exception as e:
        return None, f"主题配置解析失败: {e}"
    tasks = data.get("tasks")
    if not isinstance(tasks, dict) or not tasks:
        return None, "主题配置缺少 tasks 对象或为空"
    return tasks, None


def parse_cron(expr):
    """校验 cron 表达式 5 段合法性 → (ok, err_msg)
    支持: * / */n / a-b / a,b / 数字"""
    parts = expr.split()
    if len(parts) != 5:
        return False, f"cron '{expr}' 非 5 段"
    bounds = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
    for i, (p, (lo, hi)) in enumerate(zip(parts, bounds)):
        if p == "*":
            continue
        for token in p.split(","):
            if token == "*":
                continue
            step = None
            if "/" in token:
                base, _, step_s = token.partition("/")
                if not step_s.isdigit() or int(step_s) < 1:
                    return False, f"cron '{expr}' 第{i+1}段 '{p}' 步进非法"
                step = int(step_s)
                token = base
                if token == "*":
                    continue  # */n 合法（如 */2 = 每隔 2 个单位）
            rng = token
            if "-" in token:
                a_s, _, b_s = token.partition("-")
                if not (a_s.isdigit() and b_s.isdigit()):
                    return False, f"cron '{expr}' 第{i+1}段 '{p}' 范围非法"
                a, b = int(a_s), int(b_s)
                if not (lo <= a <= b <= hi):
                    return False, f"cron '{expr}' 第{i+1}段 '{p}' 超范围 [{lo},{hi}]"
            else:
                if not token.isdigit():
                    return False, f"cron '{expr}' 第{i+1}段 '{p}' 含非法 token '{token}'"
                v = int(token)
                if not (lo <= v <= hi):
                    return False, f"cron '{expr}' 第{i+1}段 '{p}' 超范围 [{lo},{hi}]"
    return True, ""


def extract_guide_task(desc):
    """从任务描述提取 guide --task 参数 → str|None
    支持两种形式: --task "任务名" 或 --task <task_id>（runner resolve_task_id 双支持）"""
    m = re.search(r'guide --task\s+"([^"]+)"', desc)
    if m:
        return m.group(1)
    m = re.search(r'guide --task\s+([A-Za-z0-9_\-]+)', desc)
    return m.group(1) if m else None


def classify_tasks(tasks):
    """按描述是否引用 runner 分为调研类/非调研类"""
    research, other = [], []
    for tid, t in tasks.items():
        desc = t.get("action", {}).get("task_description", "")
        (research if "research_task_runner.py" in desc else other).append((tid, t, desc))
    return research, other


# ── 检查函数 ───────────────────────────────────────────────────────────────────

def check_c1(tasks, err):
    results = []
    if err:
        results.append(("C1", "T001", "FAIL", err))
        return results, []
    n = len(tasks)
    disabled = [tid for tid, t in tasks.items() if not t.get("enabled", True)]
    ok = n >= 40 and not disabled
    msg = f"任务数 {n}，全 enabled" if ok else f"任务数 {n}，禁用: {disabled or '无'}"
    results.append(("C1", "T001", "PASS" if ok else "FAIL",
                    msg if ok else "任务数异常或存在禁用任务"))
    return results, (["scheduler enable 禁用任务"] if not ok and disabled else [])


def check_c2(tasks, err):
    results, fixes = [], []
    if err:
        results.append(("C2", "T002", "FAIL", err))
        return results, fixes
    bad = []
    for tid, t in tasks.items():
        if tid in EXCEPTIONS:
            continue
        cron = t.get("schedule", {}).get("expression", "")
        parts = cron.split()
        if len(parts) == 5:
            try:
                hour = int(parts[1])
            except ValueError:
                hour = -1
            if hour not in ALLOWED_HOURS:
                bad.append((tid, t.get("name", "?"), cron))
    if bad:
        for tid, name, cron in bad:
            results.append(("C2", "T002", "FAIL",
                            f"[{tid}] {name} cron={cron} 超出窗口 21:00~08:00"))
            fixes.append(f"重建 {name}: scheduler delete {tid} → create (cron 改为夜间)")
    else:
        results.append(("C2", "T002", "PASS", "全部任务在 21:00~08:00 窗口（白名单除外）"))
    return results, fixes


def check_c3(research, err):
    results = []
    if err:
        results.append(("C3", "T003", "FAIL", err))
        return results
    n = len(research)
    no_guide = [tid for tid, _, desc in research if "guide" not in desc]
    if no_guide:
        results.append(("C3", "T003", "FAIL",
                        f"调研任务 {n} 个，其中 {len(no_guide)} 个描述未含 guide 入口: {no_guide}"))
    else:
        results.append(("C3", "T003", "PASS", f"{n} 个调研任务描述均含 runner guide 入口"))
    return results


def check_c4(research, cfg, err):
    results = []
    if err:
        results.append(("C4", "T004", "FAIL", err))
        return results
    ids = set(cfg.keys())
    names = {c.get("name") for c in cfg.values()}
    unresolved = []
    for tid, _, desc in research:
        arg = extract_guide_task(desc)
        if arg is None or (arg not in ids and arg not in names):
            unresolved.append((tid, arg))
    if unresolved:
        results.append(("C4", "T004", "FAIL",
                        f"以下任务 guide --task 参数无法在配置中解析（须为配置 ID 或任务名）: "
                        + "; ".join(f"[{tid}]→{a}" for tid, a in unresolved)))
    else:
        results.append(("C4", "T004", "PASS", f"{len(research)} 个 guide --task 参数全部可解析（ID 或任务名）"))
    return results


def check_c5(cfg, err):
    results = []
    if err:
        results.append(("C5", "T005", "FAIL", err))
        return results
    outs = [c.get("out", "") for c in cfg.values()]
    from collections import Counter
    dup = {k: v for k, v in Counter(outs).items() if v > 1}
    shared = [o for o in outs if SHARED_FILE_RE.search(o)]
    if dup:
        results.append(("C5", "T005", "FAIL", f"输出路径重复: {dup}"))
    elif shared:
        results.append(("C5", "T005", "FAIL",
                        f"仍有任务指向废弃共享文件: {shared}"))
    else:
        results.append(("C5", "T005", "PASS",
                        f"{len(outs)} 任务输出路径两两唯一，无共享文件引用"))
    return results


def check_c6(cfg, err):
    results = []
    if err:
        results.append(("C6", "T006", "FAIL", err))
        return results
    missing = []
    for tid, c in cfg.items():
        out = c.get("out", "")
        # module 目录 = 去掉文件名后的目录（out 中 YYYY-MM-DD 为占位）
        dir_part = str(Path(out).parent)  # 如 knowledge/01_survey/switch
        d = WORKSPACE_ROOT / dir_part
        if not (d / "index.md").exists() or not (d / "log.md").exists():
            missing.append((tid, c.get("name"), dir_part))
    if missing:
        results.append(("C6", "T006", "FAIL",
                        "以下 module 目录缺 index.md/log.md: "
                        + "; ".join(f"[{tid}]{name}→{p}" for tid, name, p in missing)))
    else:
        results.append(("C6", "T006", "PASS", "所有输出 module 目录均含 index.md + log.md"))
    return results


def check_c7(research, err):
    results = []
    if err:
        results.append(("C7", "T007", "FAIL", err))
        return results
    long_ones = [(tid, t.get("name", "?"), len(desc))
                 for tid, t, desc in research if len(desc) > DESC_MAX_CHARS]
    if long_ones:
        results.append(("C7", "T007", "FAIL",
                        f"描述超 {DESC_MAX_CHARS} chars: "
                        + "; ".join(f"[{tid}]{name}={n}" for tid, name, n in long_ones)))
    else:
        maxlen = max(len(desc) for _, _, desc in research) if research else 0
        results.append(("C7", "T007", "PASS", f"调研任务描述全部 ≤{DESC_MAX_CHARS} chars（最大 {maxlen}）"))
    return results


def check_c8(other, err):
    results = []
    if err:
        results.append(("C8", "T008", "FAIL", err))
        return results
    empty = [tid for tid, _, desc in other if not desc.strip()]
    if empty:
        results.append(("C8", "T008", "FAIL", f"非调研任务描述为空: {empty}"))
    else:
        results.append(("C8", "T008", "PASS", f"{len(other)} 个非调研任务描述均非空"))
    return results


def check_c9(tasks, err):
    results = []
    if err:
        results.append(("C9", "T009", "FAIL", err))
        return results
    bad = []
    for tid, t in tasks.items():
        cron = t.get("schedule", {}).get("expression", "")
        ok, msg = parse_cron(cron)
        if not ok:
            bad.append((tid, t.get("name", "?"), msg))
    if bad:
        results.append(("C9", "T009", "FAIL", "; ".join(f"[{tid}]{name}: {m}" for tid, name, m in bad)))
    else:
        results.append(("C9", "T009", "PASS", f"{len(tasks)} 个 cron 表达式合法"))
    return results


def check_c10(err):
    results = []
    if err:
        results.append(("C10", "T010", "FAIL", err))
        return results
    if not RUNNER.exists():
        results.append(("C10", "T010", "FAIL", f"runner 脚本缺失: {RUNNER}"))
        return results
    src = RUNNER.read_text(encoding="utf-8")
    missing = [k for k in RULES_KEYWORDS if k not in src]
    if missing:
        results.append(("C10", "T010", "FAIL", f"runner 缺失规则关键词: {missing}"))
    else:
        results.append(("C10", "T010", "PASS", "runner 内建九项规则关键词齐全"))
    return results


def check_w1(tasks, err):
    """名字时间标签与 cron 一致性（WARN 级）"""
    results = []
    if err:
        results.append(("W1", "T011", "WARN", err))
        return results
    warns = []
    for tid, t in tasks.items():
        name = t.get("name", "")
        m = NAME_TIME_RE.search(name)
        if not m:
            continue
        name_hour = int(m.group(1))
        cron = t.get("schedule", {}).get("expression", "")
        parts = cron.split()
        if len(parts) != 5:
            continue
        try:
            cron_hour = int(parts[1])
        except ValueError:
            continue
        if name_hour != cron_hour:
            warns.append(f"[{tid}] {name} 标签={name_hour:02d}:00 实际 cron={cron}")
    if warns:
        results.append(("W1", "T011", "WARN",
                        "名字时间标签与 cron 不一致（历史遗留，改名=断链，暂缓）: "
                        + " | ".join(warns)))
    else:
        results.append(("W1", "T011", "PASS", "名字时间标签与 cron 一致"))
    return results


# ── 主流程 ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="定时任务体系合规检查")
    ap.add_argument("--json", action="store_true", help="输出 JSON 报告")
    ap.add_argument("--fix", action="store_true", help="输出修复建议")
    ap.add_argument("--check", choices=["window", "desc", "config", "dirs", "rules"],
                    help="只跑单项（window=C2, desc=C3/C4/C7/C8, config=C5/C9, dirs=C6, rules=C10）")
    args = ap.parse_args()

    tasks, terr = load_tasks_json()
    cfg, cerr = load_topics_config()
    research, other = classify_tasks(tasks) if tasks else ([], [])

    checks, fixes = [], []
    if args.check in (None, "window"):
        c2, f2 = check_c2(tasks, terr)
        checks += c2
        fixes += f2
    if args.check in (None, "desc"):
        checks += check_c3(research, terr)
        checks += check_c4(research, cfg, cerr)
        checks += check_c7(research, terr)
        checks += check_c8(other, terr)
    if args.check in (None, "config"):
        checks += check_c5(cfg, cerr)
        checks += check_c9(tasks, terr)
    if args.check in (None, "dirs"):
        checks += check_c6(cfg, cerr)
    if args.check in (None, "rules"):
        checks += check_c10(cerr)
    # C1 + W1 始终执行
    c1, _ = check_c1(tasks, terr)
    w1 = check_w1(tasks, terr)
    checks = c1 + checks + w1

    fails = [c for c in checks if c[2] == "FAIL"]
    warns = [c for c in checks if c[2] == "WARN"]

    if args.json:
        print(json.dumps({
            "design_doc": DESIGN_DOC,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "summary": {"total": len(checks), "fail": len(fails), "warn": len(warns)},
            "checks": [{"id": c[0], "code": c[1], "level": c[2], "msg": c[3]} for c in checks],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"🧭 设计文档: {DESIGN_DOC}")
        print("=" * 72)
        for cid, code, level, msg in checks:
            icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[level]
            print(f"{icon} [{cid}] ({code}) {level}: {msg}")
        print("=" * 72)
        print(f"📊 合计 {len(checks)} 项: PASS {len(checks)-len(fails)-len(warns)} · "
              f"FAIL {len(fails)} · WARN {len(warns)}")
        if fails and args.fix:
            print("\n🔧 修复建议:")
            for msg in fixes:
                print(f"  · {msg}")
        if fails:
            print("\n❌ 存在 FAIL，请修复后重跑（退出码 1）")
        else:
            print("✅ 全部 PASS（可含 WARNING）")

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
