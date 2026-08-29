#!/usr/bin/env python3
"""cowchat — Command-line CowAgent chat client (direct mode)

通过直接加载 CowAgent 模块运行 Agent，不依赖 HTTP API。
支持流式输出、交互模式、管道输入。

用法:
  cowchat "你的问题"          # 一问一答
  echo "问题" | cowchat       # 管道输入
  cowchat                     # 交互模式 (输入 exit 退出)
  cowchat -s <session_id>     # 指定会话ID

环境:
  从 ~/CowAgent/config.json 读取配置
"""

import argparse
import json
import os
import sys
import threading
import time
import uuid

# ── 样式 ──

class Style:
    enabled = sys.stdout.isatty()
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    GRAY = "\033[90m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    @classmethod
    def wrap(cls, text, *codes):
        if not cls.enabled or not codes:
            return text
        return "".join(codes) + text + cls.RESET


# ── 流式渲染器 ──

class StreamRenderer:
    def __init__(self):
        self._reasoning_active = False
        self._answer_active = False
        self._has_output = False
        self._final_content = ""

    def _print(self, text, end="", flush=True):
        sys.stdout.write(text)
        if end:
            sys.stdout.write(end)
        if flush:
            sys.stdout.flush()
        self._has_output = True

    def _close_section(self):
        if self._reasoning_active:
            self._print("", end="\n")
            self._reasoning_active = False
        if self._answer_active:
            self._print("", end="\n")
            self._answer_active = False

    def handle_event(self, event: dict):
        etype = event.get("type")
        data = event.get("data", {}) or {}

        if etype == "reasoning_update":
            delta = data.get("delta", "")
            if not delta:
                return
            if self._answer_active:
                self._close_section()
            if not self._reasoning_active:
                self._print(Style.wrap("💭 ", Style.DIM, Style.MAGENTA))
                self._reasoning_active = True
            self._print(Style.wrap(delta, Style.DIM, Style.ITALIC))

        elif etype == "message_update":
            delta = data.get("delta", "")
            if not delta:
                return
            if self._reasoning_active:
                self._close_section()
            if not self._answer_active:
                self._answer_active = True
            self._print(delta)
            self._final_content += delta

        elif etype == "tool_execution_start":
            self._close_section()
            tool_name = data.get("tool_name", "tool")
            arguments = data.get("arguments", {})
            args_str = json.dumps(arguments, ensure_ascii=False)
            if len(args_str) > 200:
                args_str = args_str[:200] + "…"
            self._print(Style.wrap(f"🔧 {tool_name}", Style.BOLD, Style.CYAN))
            self._print(Style.wrap(f" {args_str}", Style.GRAY), end="\n")

        elif etype == "tool_execution_end":
            tool_name = data.get("tool_name", "tool")
            status = data.get("status", "success")
            result = str(data.get("result", ""))
            exec_time = data.get("execution_time", 0)
            icon = "✓" if status == "success" else "✗"
            color = Style.GREEN if status == "success" else Style.RED
            if len(result) > 500:
                result = result[:500] + "…"
            result = result.replace("\n", "\n   ")
            cost = f" ({exec_time:.2f}s)" if exec_time else ""
            self._print(
                Style.wrap(f"   {icon} {tool_name}{cost}", color), end=""
            )
            if result:
                self._print(Style.wrap(f"  {result}", Style.GRAY), end="\n")
            else:
                self._print(end="\n")

        elif etype == "tool_execution_progress":
            tool = data.get("tool_name", "tool")
            msg = str(data.get("message", ""))[:200]
            self._print(Style.wrap(f"   ⏳ {tool}: {msg}", Style.DIM), end="\n")

        elif etype == "file_to_send":
            self._close_section()
            fpath = data.get("path", "")
            fname = data.get("file_name", os.path.basename(fpath))
            self._print(Style.wrap(f"📎 文件: {fname}", Style.BLUE), end="\n")

        elif etype == "error":
            self._close_section()
            err = data.get("error", "unknown error")
            self._print(Style.wrap(f"❌ {err}", Style.BOLD, Style.RED), end="\n")

        elif etype == "agent_cancelled":
            self._close_section()
            self._print(Style.wrap("⏹ 已中止", Style.YELLOW), end="\n")

    def finish(self):
        self._close_section()
        return self._final_content


# ── Agent 初始化 ──

def init_agent():
    """初始化 CowAgent 环境并返回 agent_bridge"""
    # 切换到 CowAgent 目录
    cowagent_dir = os.path.expanduser("~/CowAgent")
    os.chdir(cowagent_dir)
    sys.path.insert(0, cowagent_dir)

    # 加载配置
    from config import load_config
    load_config()

    # 获取 Bridge 单例
    from bridge.bridge import Bridge
    bridge = Bridge()

    # 获取 AgentBridge
    agent_bridge = bridge.get_agent_bridge()
    return agent_bridge


def run_agent(agent_bridge, query: str, session_id: str) -> str:
    """运行 Agent 处理一条消息，返回回复文本"""
    from bridge.context import Context, ContextType

    renderer = StreamRenderer()
    context = Context(ContextType.TEXT, query)
    context["session_id"] = session_id
    context["receiver"] = session_id
    context["channel_type"] = "terminal"
    context["on_event"] = renderer.handle_event

    # 通过 agent_reply 处理（阻塞直到完成）
    reply = agent_bridge.agent_reply(
        query=query,
        context=context,
        on_event=renderer.handle_event,
        clear_history=False,
    )

    renderer.finish()

    if reply and reply.content:
        return str(reply.content)
    return renderer._final_content


# ── 交互模式 ──

def interactive(agent_bridge, session_id: str):
    print(f"\n{Style.wrap('🐄 CowAgent CLI', Style.BOLD, Style.GREEN)}")
    print(f"{Style.wrap(f'会话: {session_id}', Style.GRAY)}")
    print(f"{Style.wrap('输入 exit 或 Ctrl+C 退出', Style.GRAY)}\n")

    while True:
        try:
            sys.stdout.write(f"{Style.wrap('You: ', Style.BOLD, Style.BLUE)}")
            sys.stdout.flush()
            prompt = sys.stdin.readline()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not prompt:
            break
        prompt = prompt.strip()
        if prompt.lower() in ("exit", "quit", "/exit"):
            break
        if not prompt:
            continue

        try:
            agent_bridge.agent._current_session_id = session_id
        except Exception:
            pass

        sys.stdout.write(f"{Style.wrap('Agent: ', Style.BOLD, Style.GREEN)}")
        sys.stdout.flush()

        result = run_agent(agent_bridge, prompt, session_id)
        if result:
            print()
        print()

    print(Style.wrap("再见 👋", Style.GRAY))


# ── 一次性模式 ──

def oneshot(agent_bridge, query: str, session_id: str):
    sys.stdout.write(f"{Style.wrap('Agent: ', Style.BOLD, Style.GREEN)}")
    sys.stdout.flush()
    result = run_agent(agent_bridge, query, session_id)
    if result:
        print()
    return 0


# ── CLI 入口 ──

def main():
    parser = argparse.ArgumentParser(
        description="🐄 CowAgent CLI — 命令行与 CowAgent 对话",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("question", nargs="?", help="提问内容（省略则进入交互模式）")
    parser.add_argument("-s", "--session", default=None, help="会话 ID")

    args = parser.parse_args()

    # 确定 session_id
    session_id = args.session or f"cli_{uuid.uuid4().hex[:12]}"

    # 确定问题
    question = args.question
    if not question and not sys.stdin.isatty():
        question = sys.stdin.read().strip()

    # 初始化 Agent
    print(f"⏳ 启动 CowAgent 环境...", file=sys.stderr)
    try:
        agent_bridge = init_agent()
    except Exception as e:
        print(f"❌ 初始化失败: {e}", file=sys.stderr)
        return 1

    # 运行
    if question:
        return oneshot(agent_bridge, question, session_id)
    else:
        interactive(agent_bridge, session_id)
        return 0


if __name__ == "__main__":
    sys.exit(main())
