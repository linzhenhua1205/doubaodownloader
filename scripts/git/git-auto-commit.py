#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
git-auto-commit.py — AI 操作文件后的自动提交脚本

用途:
    AI (CowAgent) 完成一批知识库/脚本/文档操作后, 自动 git add + commit。
    提交信息规范化 (type(scope): summary + body 文件清单), 并用独立身份标记
    AI 提交, 便于后续区分人工与 AI 提交、追溯来源。

区分机制 (双保险):
    1. author/committer 身份:  AI 提交 = cowagent <cowagent@cowkb.local>;
                              人工提交 = 本机 git config 身份 (linzhenhua1205)
    2. commit message 前缀:   [AI] (脚本默认) vs [manual] (--manual 显式标注)

快速使用:
    # 默认: add 全部改动 + 自动推断 type/scope + AI 身份提交 (不推送)
    python3 scripts/git/git-auto-commit.py -m "FMS P2 系列 DRAM 供给传导深度分析"

    # 指定类型/范围
    python3 scripts/git/git-auto-commit.py -t knowledge -s 03_AI -m "..."

    # 只提交指定文件/目录
    python3 scripts/git/git-auto-commit.py --paths "knowledge/03_AI/train/ai-storage/" -m "..."

    # 提交后推送 (复用 git-push-robust.py 多策略)
    python3 scripts/git/git-auto-commit.py -m "..." --push

    # 人工规范提交 (本机身份 + [manual] 前缀)
    python3 scripts/git/git-auto-commit.py -m "..." --manual

    # 预览不执行
    python3 scripts/git/git-auto-commit.py -m "..." --dry-run

规范:
    commit message = "[AI] <type>(<scope>): <summary>\n\n<body 变更清单>"
    type 取值: knowledge / docs / feat / fix / chore / refactor / memory / spec
"""

import argparse
import os
import re
import subprocess
import sys

AI_NAME = "cowagent"
AI_EMAIL = "cowagent@cowkb.local"
PREFIX_AI = "[AI]"
PREFIX_MANUAL = "[manual]"

# 路径 → (type, scope) 推断规则 (按优先级)
PATH_RULES = [
    (r"^knowledge/02_rd",           ("knowledge", "02_rd")),
    (r"^knowledge/03_AI",           ("knowledge", "03_AI")),
    (r"^knowledge/04_person",       ("knowledge", "04_person")),
    (r"^knowledge/05_tools",        ("knowledge", "05_tools")),
    (r"^knowledge/06_others",       ("knowledge", "06_others")),
    (r"^knowledge/07_industry",     ("knowledge", "07_industry-research")),
    (r"^knowledge/01_survey",       ("knowledge", "01_survey")),
    (r"^knowledge/weekly-reports",  ("knowledge", "weekly-reports")),
    (r"^knowledge/(index\.md|log\.md|README\.md)$", ("knowledge", "meta")),
    (r"^memory/",                   ("memory", "daily")),
    (r"^scripts/",                  ("chore", "scripts")),
    (r"^skills/",                   ("chore", "skills")),
    (r"^spec/",                     ("docs", "spec")),
    (r"^conversation-log/",         ("chore", "logs")),
    (r"^websites/",                 ("docs", "websites")),
    (r"^tmp/",                      ("chore", "tmp")),
]

FALLBACK_TYPE, FALLBACK_SCOPE = "chore", "misc"


def run(cmd, check=True, capture=True):
    """执行命令, 返回 (returncode, stdout, stderr)。"""
    p = subprocess.run(cmd, capture_output=capture, text=True, encoding="utf-8",
                       errors="replace", cwd=os.getcwd())
    if check and p.returncode != 0:
        print(f"✗ 命令失败: {' '.join(cmd)}\n{p.stderr}", file=sys.stderr)
        sys.exit(p.returncode)
    return p.returncode, p.stdout, p.stderr


def git(*args):
    return run(["git"] + list(args))


def get_changed_files():
    """返回 (staged 文件列表, 未 staged 文件列表, 未跟踪文件列表)。"""
    _, staged, _ = git("diff", "--cached", "--name-only")
    _, unstaged, _ = git("diff", "--name-only")
    _, untracked, _ = git("ls-files", "--others", "--exclude-standard")
    return (staged.splitlines(), unstaged.splitlines(), untracked.splitlines())


def infer_type_scope(paths):
    """从文件路径集合推断 (type, scope), 统计出现次数取最多者。"""
    counts = {}
    for p in paths:
        p = p.replace("\\", "/").strip()
        matched = False
        for pattern, (t, s) in PATH_RULES:
            if re.match(pattern, p):
                key = (t, s)
                counts[key] = counts.get(key, 0) + 1
                matched = True
                break
        if not matched:
            key = (FALLBACK_TYPE, FALLBACK_SCOPE)
            counts[key] = counts.get(key, 0) + 1
    if not counts:
        return FALLBACK_TYPE, FALLBACK_SCOPE
    # 取出现次数最多的; 平局时按 PATH_RULES 顺序靠前的优先
    best = max(counts.items(), key=lambda kv: (kv[1], -list(counts).index(kv[0])))[0]
    return best


def format_body(all_paths, note=None, stats=None):
    """生成 commit body: 变更文件清单 + 说明。"""
    lines = []
    if note:
        lines.append(note.strip())
        lines.append("")
    if stats:
        lines.append("变更统计:")
        for line in stats.strip().splitlines():
            lines.append("  " + line)
        lines.append("")
    # 分类文件清单
    new_files, mod_files, del_files = [], [], []
    for p in all_paths:
        p = p.strip()
        if not p:
            continue
        if p.startswith("A\t") or p.startswith("??"):
            new_files.append(p.split("\t")[-1])
        elif p.startswith("D\t"):
            del_files.append(p.split("\t")[-1])
        elif p.startswith("M\t") or p.startswith("R\t"):
            mod_files.append(p.split("\t")[-1])
        elif os.path.exists(p):
            mod_files.append(p)
        else:
            new_files.append(p)
    if new_files:
        lines.append(f"新增 ({len(new_files)}):")
        lines += [f"- {f}" for f in new_files]
    if mod_files:
        lines.append(f"修改 ({len(mod_files)}):")
        lines += [f"- {f}" for f in mod_files]
    if del_files:
        lines.append(f"删除 ({len(del_files)}):")
        lines += [f"- {f}" for f in del_files]
    return "\n".join(lines)


def build_message(prefix, type_, scope, summary, body):
    head = f"{prefix} {type_}({scope}): {summary}"
    if body:
        return head + "\n\n" + body
    return head


def main():
    ap = argparse.ArgumentParser(
        description="AI 操作文件后的自动提交脚本 (规范 message + 身份区分)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python3 scripts/git/git-auto-commit.py -m \"FMS P2 系列深度分析\"\n"
               "  python3 scripts/git/git-auto-commit.py -t knowledge -s 03_AI -m \"...\" --push\n"
               "  python3 scripts/git/git-auto-commit.py -m \"...\" --manual\n")
    ap.add_argument("-m", "--message", help="commit summary (建议必填; 缺省自动生成)")
    ap.add_argument("-t", "--type", choices=["knowledge", "docs", "feat", "fix",
                                             "chore", "refactor", "memory", "spec"],
                    help="commit 类型 (缺省按路径自动推断)")
    ap.add_argument("-s", "--scope", help="commit 范围 (缺省按路径自动推断)")
    ap.add_argument("-n", "--note", help="body 附加说明 (如来源/质量检查结果)")
    ap.add_argument("--paths", action="append", default=[],
                    help="仅提交指定路径 (可多次; 缺省 git add -A 全部)")
    ap.add_argument("--push", action="store_true",
                    help="提交后调用 git-push-robust.py 推送")
    ap.add_argument("--manual", action="store_true",
                    help="人工提交: 本机身份 + [manual] 前缀 (默认 AI 身份 + [AI])")
    ap.add_argument("--dry-run", action="store_true", help="仅预览不执行")
    args = ap.parse_args()

    # 1. stage
    if args.paths:
        for p in args.paths:
            run(["git", "add", "--", p])
    else:
        run(["git", "add", "-A"])

    staged, unstaged, untracked = get_changed_files()
    if not staged:
        print("ℹ 没有待提交的变更 (staged 为空), 退出。")
        return 0
    # 若 --paths 后仍有未跟踪文件被 add 进来, staged 会包含; 正常

    # 2. 推断 type/scope
    type_ = args.type or infer_type_scope(staged)[0]
    scope = args.scope or infer_type_scope(staged)[1]

    # 3. 统计 (cached 全量)
    _, stats, _ = git("diff", "--cached", "--stat", "--no-color")
    stats = stats.strip() or ""

    # 4. 生成 message
    summary = args.message
    if not summary:
        summary = f"{len(staged)} files updated"
    prefix = PREFIX_MANUAL if args.manual else PREFIX_AI
    body = format_body(staged, note=args.note, stats=stats)
    msg = build_message(prefix, type_, scope, summary, body)

    print("═" * 60)
    print(f" 身份 : {('人工 [manual]' if args.manual else 'AI [cowagent]')}")
    print(f" type : {type_}   scope: {scope}")
    print("─" * 60)
    print(msg)
    print("─" * 60)
    if args.dry_run:
        print("ℹ --dry-run 预览, 未执行。")
        return 0

    # 5. 提交 (AI 身份用 -c 覆盖, 不改动全局 config)
    env_cmd = ["git"]
    if not args.manual:
        env_cmd += ["-c", f"user.name={AI_NAME}", "-c", f"user.email={AI_EMAIL}"]
    run(env_cmd + ["commit", "-m", msg])

    # 6. 可选推送 — 一律后台异步触发（不阻塞、不等待，网络不佳由后台自动重试）
    if args.push:
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "git-push-robust.py")
        # 复用 git-push-robust.py 的 --async 后台分离模式，立即返回
        run([sys.executable, script, "--async"])

    print(f"✓ 已提交: {prefix} {type_}({scope}): {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
