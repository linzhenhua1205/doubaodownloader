#!/usr/bin/env python3
"""
session-manager.py — 通用会话持久化管理器（替代 16 个设计承诺的 session 脚本）

audit-002 封闭性加固：skills 文档承诺了 init_session/save_session/resume_session/
status_session/list_sessions/cancel_session 及 doc/method/plan/review 变体共 16 个脚本，
但从未实现。本脚本以单一入口 + 子命令方式提供全部能力，
消除"文档承诺确定性工具但未实现 → 回退 LLM 自由判断"的不确定性外溢。

用法:
  python3 scripts/tools/session-manager.py init <session_id> [--context KEY=VAL ...]
  python3 scripts/tools/session-manager.py save <session_id> [--context KEY=VAL ...]
  python3 scripts/tools/session-manager.py status <session_id>
  python3 scripts/tools/session-manager.py list [--filter doc|method|plan|review|generic]
  python3 scripts/tools/session-manager.py resume <session_id>   # 输出恢复上下文
  python3 scripts/tools/session-manager.py cancel <session_id>   # 标记废弃（不删除）

兼容旧命名: init_doc_session.py / save_method_session.py / ... 由 skills 文档引用
时可用别名: python3 scripts/tools/session-manager.py init doc:<id>  (类型前缀)

存储: ~/cow/tmp/sessions/<session_id>.json（工作区外 tmp/ 内，不污染知识库）
"""

import argparse
import json
import os
import sys
import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SESSIONS_DIR = WORKSPACE / "tmp" / "sessions"

# 类型前缀映射：doc/method/plan/review/generic
TYPE_PREFIXES = ("doc", "method", "plan", "review")


def ensure_dir():
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def session_path(session_id: str) -> Path:
    """session_id 规范化：允许 'doc:xxx' 或 'xxx'，统一为 safe filename"""
    safe = session_id.replace(":", "__").replace("/", "_").replace(" ", "_")
    return SESSIONS_DIR / f"{safe}.json"


def load(session_id: str):
    p = session_path(session_id)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save(session_id: str, context: dict, note: str = ""):
    ensure_dir()
    p = session_path(session_id)
    data = load(session_id) or {
        "session_id": session_id,
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "status": "active",
        "context": {},
        "history": [],
    }
    data["context"].update(context or {})
    data["status"] = "active"
    data["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    if note:
        data["history"].append({
            "at": data["updated_at"],
            "note": note,
        })
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def cmd_init(args):
    data = save(args.session_id, dict(kv for kv in (args.context or [])), note=f"init {args.session_id}")
    print(f"✅ 会话已初始化: {args.session_id} → {session_path(args.session_id)}")
    print(f"   上下文键: {', '.join(data['context'].keys()) if data['context'] else '(空)'}")


def cmd_save(args):
    data = save(args.session_id, dict(kv for kv in (args.context or [])), note=args.note or "save")
    print(f"✅ 会话已保存: {args.session_id} (上下文 {len(data['context'])} 键, 历史 {len(data['history'])} 条)")


def cmd_status(args):
    data = load(args.session_id)
    if not data:
        print(f"❌ 会话不存在: {args.session_id}（{session_path(args.session_id)}）")
        sys.exit(1)
    print(f"📋 会话: {args.session_id}")
    print(f"   状态: {data.get('status')} | 创建: {data.get('created_at')} | 更新: {data.get('updated_at')}")
    print(f"   上下文键 ({len(data['context'])}): {', '.join(data['context'].keys()) if data['context'] else '(空)'}")
    if data.get("history"):
        print(f"   最近历史: {data['history'][-1].get('note')}")


def cmd_list(args):
    ensure_dir()
    files = sorted(SESSIONS_DIR.glob("*.json"))
    if not files:
        print("(无会话)")
        return
    type_filter = args.filter
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        sid = data.get("session_id", f.stem)
        # 类型过滤：doc:xxx / method:xxx / 纯 xxx
        sid_type = "generic"
        if ":" in sid:
            sid_type = sid.split(":", 1)[0]
        if type_filter and sid_type != type_filter:
            continue
        status = data.get("status", "?")
        nctx = len(data.get("context", {}))
        print(f"  [{status}] {sid} (ctx={nctx}) {data.get('updated_at', '')}")


def cmd_resume(args):
    data = load(args.session_id)
    if not data:
        print(f"❌ 会话不存在: {args.session_id}")
        sys.exit(1)
    if data.get("status") == "cancelled":
        print(f"⚠️ 会话已废弃: {args.session_id}")
    print(f"# 恢复会话: {args.session_id}")
    print(f"状态: {data.get('status')} | 创建: {data.get('created_at')}")
    if data.get("context"):
        print("\n## 上下文（注入提示词）")
        for k, v in data["context"].items():
            print(f"- **{k}**: {v}")
    if data.get("history"):
        print("\n## 历史记录")
        for h in data["history"][-5:]:
            print(f"- [{h['at']}] {h['note']}")


def cmd_cancel(args):
    data = load(args.session_id)
    if not data:
        print(f"❌ 会话不存在: {args.session_id}")
        sys.exit(1)
    data["status"] = "cancelled"
    data["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    session_path(args.session_id).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"🗑️ 会话已废弃（文件保留）: {args.session_id}")


def parse_kv(items):
    """解析 KEY=VAL 列表"""
    for item in items or []:
        if "=" in item:
            k, v = item.split("=", 1)
            yield k, v


def main():
    parser = argparse.ArgumentParser(description="通用会话持久化管理器")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="初始化会话")
    p_init.add_argument("session_id")
    p_init.add_argument("--context", nargs="*", metavar="KEY=VAL")
    p_init.set_defaults(func=cmd_init)

    p_save = sub.add_parser("save", help="保存会话")
    p_save.add_argument("session_id")
    p_save.add_argument("--context", nargs="*", metavar="KEY=VAL")
    p_save.add_argument("--note", default="")
    p_save.set_defaults(func=cmd_save)

    p_status = sub.add_parser("status", help="查看会话状态")
    p_status.add_argument("session_id")
    p_status.set_defaults(func=cmd_status)

    p_list = sub.add_parser("list", help="列出会话")
    p_list.add_argument("--filter", choices=list(TYPE_PREFIXES) + ["generic"], default=None)
    p_list.set_defaults(func=cmd_list)

    p_resume = sub.add_parser("resume", help="恢复会话")
    p_resume.add_argument("session_id")
    p_resume.set_defaults(func=cmd_resume)

    p_cancel = sub.add_parser("cancel", help="废弃会话")
    p_cancel.add_argument("session_id")
    p_cancel.set_defaults(func=cmd_cancel)

    args = parser.parse_args()
    args.context = list(parse_kv(getattr(args, "context", None)))
    args.func(args)


if __name__ == "__main__":
    main()
