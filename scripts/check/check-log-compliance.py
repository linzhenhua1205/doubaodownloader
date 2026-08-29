#!/usr/bin/env python3
"""log.md 追加合规检测（S4 / W32-P1 / 日报 08-10 约束加固）

背景: 08-07 三件套单同步纪律——log.md 追加禁止 AI 直接 edit（edit 行首匹配
会拼接受损，P3 教训），统一走 `kb-log-append.py`。本脚本把该流程纪律变成
可检测检查：

  C1 格式合规: log.md 最新条目符合 `## YYYY-MM-DD` 分节 + `- **类型** | 路径 — 说明`
  C2 提交标记: 最近 N 个 [AI] 提交中，凡变更 knowledge/log.md 的，commit message
               应含追加标记（kb-log-append / log.md 追加 / log 追加）——无标记即提示
  C3 当日覆盖: 今天是否已有 log.md 条目（防止归档漏记）

用法: python3 scripts/check/check-log-compliance.py [--days 3] [--commits 30]
退出码: 0=全部通过, 1=有问题
"""
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
LOG_FILE = WORKSPACE / "knowledge" / "log.md"
COMMIT_DAYS = 3       # C2 检查窗口
COMMIT_N = 30         # C2 最多检查提交数
MARKERS = ("kb-log-append", "log.md 追加", "log 追加", "追加 log", "log.md", "三件套")

def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(WORKSPACE), *args],
                       capture_output=True, text=True, encoding="utf-8")
    return r.stdout.strip()

def c1_format(log_text: str) -> list:
    """最新条目格式: ## YYYY-MM-DD + - **类型** | 路径 — 说明"""
    issues = []
    if not log_text.strip():
        return ["log.md 为空"]
    # 取第一个日期分节
    m = re.search(r"^## (\d{4}-\d{2}-\d{2})", log_text, re.M)
    if not m:
        return ["log.md 无 `## YYYY-MM-DD` 分节"]
    sec_start = m.start()
    sec_end = log_text.find("\n## ", sec_start + 3)
    if sec_end == -1:
        sec_end = len(log_text)
    sec = log_text[sec_start:sec_end]
    items = [l for l in sec.splitlines() if l.strip().startswith("- ")]
    if not items:
        issues.append(f"最新分节 {m.group(1)} 无条目")
    for l in items[:3]:
        if not re.match(r"^- \*\*.+?\*\*.*\|.*—", l) and not re.match(r"^- \*\*.+?\*\*.*\|.*-", l):
            issues.append(f"条目格式疑似不合规: {l[:60]}")
            break
    return issues

def c2_commit_marker() -> list:
    """检测可疑 log.md 直接 edit 痕迹

    原理: kb-log-append.py 是纯追加（log.md 变更几乎只有 + 行）；
    直接 edit（行首匹配拼接/重排）会留下大量 - 行（删除/修改）。
    用 numstat 的 -N 列识别可疑提交，比「message 必须含标记」更贴近
    真实违规模式（P3 拼接事故即 edit 行首匹配产生 - 行）。
    """
    issues = []
    out = git("log", f"-{COMMIT_N}", "--format=%H|%s", "--numstat", "--", "knowledge/log.md")
    if not out:
        return []
    cur_msg, cur_hash = None, None
    for line in out.splitlines():
        if line.startswith("|"):
            cur_hash, cur_msg = line.split("|", 1)[0], line.split("|", 1)[1]
            continue
        if line.endswith("knowledge/log.md"):
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1].strip("-").isdigit():
                dels = int(parts[1]) if parts[1] != "-" else 0
                if dels > 10:  # 追加场景删除行极少；>10 = 直接 edit/重排痕迹
                    issues.append(f"{cur_hash[:8]} log.md 删除 {dels} 行（疑似直接 edit）: {cur_msg[:60]}")
    return issues

def c3_today() -> list:
    """今天是否已有 log.md 条目"""
    today = date.today().isoformat()
    text = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else ""
    if f"## {today}" not in text:
        return [f"今日 {today} 尚无 log.md 条目（归档漏记?）"]
    return []

def main() -> int:
    print("=" * 58)
    print("🧾 log.md 追加合规检测")
    print("=" * 58)
    all_issues = []
    text = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else ""
    for name, fn in (("C1 格式", lambda: c1_format(text)),
                     ("C2 提交标记", c2_commit_marker),
                     ("C3 当日覆盖", c3_today)):
        issues = fn()
        status = "✅" if not issues else "❌"
        print(f"{status} {name}: {'通过' if not issues else f'{len(issues)} 项'}")
        for i in issues:
            print(f"   ⚠️ {i}")
        all_issues += issues
    print("-" * 58)
    if all_issues:
        print(f"❌ 共 {len(all_issues)} 项不合规")
        return 1
    print("✅ 全部通过")
    return 0

if __name__ == "__main__":
    sys.exit(main())
