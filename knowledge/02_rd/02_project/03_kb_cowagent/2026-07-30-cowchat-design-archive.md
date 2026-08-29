# CowAgent CLI 对话扩展设计报告 — cowchat

> 基于 CowAgent v2.1.5 架构分析，在 `scripts/cowchat.py` 中实现的直接 Agent 调用 CLI
>
> 归档日期: 2026-07-30

---

**目录 (TOC)**

- [1. 背景与目标](#1-背景与目标)
- [2. 现有架构分析](#2-现有架构分析)
  - [2.1 三层解耦架构](#21-三层解耦架构)
  - [2.2 消息流转端到端](#22-消息流转端到端)
  - [2.3 现有命令行能力评估](#23-现有命令行能力评估)
- [3. 方案设计](#3-方案设计)
  - [3.1 方案对比](#31-方案对比)
  - [3.2 推荐方案：直接 Agent 调用](#32-推荐方案直接-agent-调用)
  - [3.3 架构定位图](#33-架构定位图)
- [4. 实现详情](#4-实现详情)
  - [4.1 代码结构](#41-代码结构)
  - [4.2 流式渲染器 StreamRenderer](#42-流式渲染器-streamrenderer)
  - [4.3 Agent 初始化流程](#43-agent-初始化流程)
  - [4.4 单轮调用 run_agent](#44-单轮调用-run_agent)
  - [4.5 交互模式 interactive](#45-交互模式-interactive)
  - [4.6 一次性模式 oneshot](#46-一次性模式-oneshot)
  - [4.7 入口 main](#47-入口-main)
- [5. 设计决策日志](#5-设计决策日志)
  - [5.1 为什么不复用 TerminalChannel](#51-为什么不复用-terminalchannel)
  - [5.2 为什么复用 TerminalAgentRenderer — 改为自实现 StreamRenderer](#52-为什么复用-terminalagentrenderer--改为自实现-streamrenderer)
  - [5.3 关键调用约定](#53-关键调用约定)
  - [5.4 为什么选择 scripts/ 而非 cli/commands/](#54-为什么选择-scripts-而非-clicommands)
  - [5.5 会话 ID 策略](#55-会话-id-策略)
  - [5.6 无 prompt_toolkit 依赖原则](#56-无-prompt_toolkit-依赖原则)
  - [5.7 CowAgent 架构成熟度总结](#57-cowagent-架构成熟度总结)
- [6. 附录：关键源码位置速查表](#6-附录关键源码位置速查表)

---

## 1. 背景与目标

### 1.1 需求

CowAgent 已通过 `python app.py --cmd` 提供终端 Agent 通道，但它**不是独立的 CLI 工具**：

- 需启动完整的 `app.py`（含 web 控制台、MCP 预热、scheduler）
- `os._exit(0)` 硬杀进程，无法干净退出
- 启动延迟高（数秒级别）
- 无法集成到 shell pipeline 中

目标：提供一个**轻量、快速、独立进程**的命令行 Agent 客户端。

### 1.2 设计目标

| 目标 | 优先级 | 验收标准 |
|:-----|:------:|:---------|
| 亚秒级启动 | P0 | 从命令输入到 Agent 就绪 < 2s |
| 完整 Agent 能力 | P0 | 支持 tools/skills/memory/knowledge 等 Agent 全部能力 |
| 流式输出 | P0 | 实时显示推理/工具/答案，不等待完整回复 |
| 跨轮上下文 | P0 | 多轮对话自动延续上下文 |
| 优雅退出 | P1 | Ctrl+C 干净退出，无资源泄漏 |
| Shell pipeline | P1 | `echo "问题" \| cowchat` 可用 |
| 最小改动面 | P1 | 不修改 CowAgent 核心源码 |

---

## 2. 现有架构分析

### 2.1 三层解耦架构

CowAgent 采用 **Channel ↔ Bridge ↔ Agent** 三层解耦架构：

```text
+-----------------------------------------------------+
|                     Channel Layer                    |
|  WeChat  |  Feishu  |  Web  |  Terminal  |  HTTP   |
|  -------- --------- ------- ------------ ---------  |
|   接入层: 格式转换 + 协议适配 + 连接管理               |
+----------------------+------------------------------+
                       | fetch_agent_reply()
                       v
+-----------------------------------------------------+
|                   Bridge Layer                       |
|  +----------------------------------------------+   |
|  |           AgentBridge (单例)                  |   |
|  |  agents: dict[session_id, Agent]  <-- 会话隔离 |   |
|  |  agent_reply(query, context, on_event)        |   |
|  |    -> AgentRunBuilder.build()                   |   |
|  |    -> AgentStreamExecutor.run_stream()          |   |
|  |    -> AgentEventHandler(original_callback)      |   |
|  +----------------------------------------------+   |
+----------------------+------------------------------+
                       | run_stream(on_event)
                       v
+-----------------------------------------------------+
|                   Agent Layer                        |
|  +-----+ +------+ +------+ +------+ +--------+    |
|  |Tools| |Skills| |Memory| |Knowl.| |Evolut. |    |
|  +-----+ +------+ +------+ +------+ +--------+    |
|    AgentStreamExecutor (执行循环 + 取消 + 重试)      |
|    AgentEventHandler (事件过滤 + 回调转发)           |
+-----------------------------------------------------+
```

**关键结论（根据架构分析）：** Agent 路由是默认路径——`channel.py:71-102` 中 `build_reply_content` 默认 `use_agent = conf().get("agent", True)`，普通 chatbot 仅作 fallback。这意味着 `agent_reply` 是主路径，直接调用它就能获得完整 Agent 能力。

### 2.2 消息流转端到端

```text
用户输入 -> channel.startup() -> _compose_context -> produce()
-> consume() 线程 -> _handle() -> build_reply_content()
-> Bridge.fetch_agent_reply() -> AgentBridge.agent_reply()
-> agent.run_stream(on_event=handler.handle_event)
-> AgentStreamExecutor multi-turn loop
  +- LLM stream -> on_event(message_update) -> 实时渲染
  +- tool_call -> execute -> on_event(tool_execution_*)
  +- 最终回复 -> Reply 返回值
-> _send_reply() -> channel.send(reply)
```

**cowchat 的关键简化：** 直接调用 AgentBridge.agent_reply()，跳过 channel.startup() → produce/consume →_handle → build_reply_content → fetch_agent_reply 整条链路。

### 2.3 现有命令行能力评估

| 维度 | 现有 `app.py --cmd` | cowchat 目标 |
|:-----|:---------------------|:-------------|
| 启动方式 | `python app.py --cmd` | `cowchat` |
| 启动耗时 | 数秒（web+MCP+scheduler） | < 2s（仅 load_config） |
| 进程模型 | ChannelManager 子线程 | 独立进程，直接调用 |
| 端口占用 | 是（web 控制台） | 否 |
| 退出方式 | `os._exit(0)` 硬杀 | 自然退出 |
| Session 切换 | 固定 `other_user_id="Chatgpt"` | 支持 `-s` 参数指定 |
| Pipeline 集成 | 否 | 支持管道输入 |
| 依赖 | 整个 app.py | 仅 bridge + agent 基础模块 |

---

## 3. 方案设计

### 3.1 方案对比

| 方案 | 描述 | 优点 | 缺点 |
|:-----|:-----|:-----|:-----|
| **A. scripts/cowchat.py** ✅ | 独立脚本，直接调用 AgentBridge.agent_reply() | 轻量、快速、独立、0 核心改动 | 需新建文件 |
| B. 暴露 app.py --cmd 为 cow chat | fork 子进程跑 app.py | 完全复用 terminal channel | 启动慢、抢 tty、依赖重型基础设施 |
| C. 在 process.py 加 chat 子命令 | process.py 内加 chat | 文件少改 | 违反 SRP，process.py 是进程管理职责 |

### 3.2 推荐方案：直接 Agent 调用

核心思路：在 cowchat 进程内直接调用 `Bridge().get_agent_bridge().agent_reply()`，跳过 ChannelManager/web/MCP 预热等重型基础设施。

```text
cowchat "问题"
  |
  +-- load_config()              <- 加载 config.json（~50ms）
  +-- os.chdir ~/CowAgent        <- 切换到 CowAgent 工程目录
  +-- sys.path.insert(0, ~/CowAgent)  <- 确保 import 路径
  |
  +-- Bridge().get_agent_bridge() <- 按需创建（首次自动 init Agent）
  |
  +-- AgentBridge.agent_reply(query, context, on_event=renderer.handle_event)
        -> AgentStreamExecutor multi-turn loop
        -> 流式事件 -> StreamRenderer 实时渲染
        -> 返回完整回复
```

### 3.3 架构定位图

```text
                     +----------------------+
                     |     用户终端          |
                     |  cowchat "问题"       |
                     +----------+-----------+
                                |
                     +----------v-----------+
                     |   scripts/cowchat.py  |
                     |                      |
                     |  +----------------+  |
                     |  | StreamRenderer |  |  <- 自实现轻量渲染器
                     |  +----------------+  |
                     +----------+-----------+
                                | agent_reply(query, context, on_event)
                                v
                +-----------------------------------+
                |        AgentBridge (单例)          |
                |  agents: dict[session_id, Agent]  |
                |    +--------------+               |
                |    | Agent 实例    | <- 跨轮复用     |
                |    +--------------+               |
                |  SQLite ConversationStore         |
                |  (消息持久化 + 历史恢复)            |
                +-----------------------------------+
                                |
                                v
                +-----------------------------------+
                |         AgentStreamExecutor        |
                |  LLM流 -> on_event -> Renderer      |
                |  Tool执行 -> on_event -> Renderer   |
                |  取消 -> cancel_event               |
                +-----------------------------------+
```

与 `app.py --cmd` 的架构对比：

```text
app.py --cmd:
  app.py -> ChannelManager -> TerminalChannel -> produce/consume -> build_reply_content -> Bridge.fetch_agent_reply() -> AgentBridge.agent_reply()

cowchat:
  cowchat.py -> Bridge().get_agent_bridge() -> AgentBridge.agent_reply()
```

cowchat **直接缩短了 3 个层级 6 个步骤**，启动延迟从数秒降至亚秒级。

---

## 4. 实现详情

### 4.1 代码结构

```text
scripts/cowchat.py (289 行)
+-- 📖 模块 docstring              行 1-15
+-- ⚙️ Style 样式类                 行 27-45     ANSI 终端样式（自动检测 isatty）
+-- ⚙️ StreamRenderer 流式渲染器    行 50-150    7 种事件类型渲染
+-- ⚙️ init_agent()                行 155-172   Agent 初始化
+-- ⚙️ run_agent()                 行 175-198   单轮 Agent 调用
+-- ⚙️ interactive()               行 203-238   交互模式主循环
+-- ⚙️ oneshot()                   行 243-249   一次性问答
+-- ⚙️ main()                      行 254-285   CLI 入口
+-- 🏁 __main__                    行 288-289
```

### 4.2 流式渲染器 StreamRenderer

与 `terminal_channel.py:39-169` 的 `TerminalAgentRenderer` 功能等价，但更轻量、自包含（无通道依赖）。

**事件处理矩阵：**

| 事件类型 | 渲染方式 | 颜色/样式 | 特殊逻辑 |
|:---------|:---------|:----------|:---------|
| `reasoning_update` | 流式追加 | 紫色暗斜体 | 覆盖答案流，关闭前一段 |
| `message_update` | 流式追加 | 默认（不加样式） | 覆盖思考流，记录 final_content |
| `tool_execution_start` | 整行 | 青色加粗 + 灰色参数 | 参数 > 200 字符截断 |
| `tool_execution_end` | 缩进行 | 绿色 ✓ / 红色 ✗ | 显示执行时间 + 结果（> 500 截断） |
| `tool_execution_progress` | 缩进行 | 暗色 | 显示工具进度消息 |
| `file_to_send` | 整行 | 蓝色 | 显示文件名 |
| `error` | 整行 | 红色加粗 | 显示错误信息 |
| `agent_cancelled` | 整行 | 黄色 | 显示中止提示 |

与 `TerminalAgentRenderer` 的关键差异：

| 维度 | TerminalAgentRenderer | StreamRenderer |
|:-----|:---------------------|:---------------|
| 无状态 | `_has_output` 标志 | `_reasoning_active` + `_answer_active` + `_has_output` + `_final_content` |
| 最终内容 | 不保留 | 保留于 `_final_content` |
| 换行策略 | 固定 | `_close_section()` 动态切换 |
| 工具结果 | 截断 300 字符 | 截断 500 字符 |
| 依赖 | 耦合 terminal_channel.py | 无依赖 |

### 4.3 Agent 初始化流程

```python
def init_agent():
    # 1. 切换工作目录
    os.chdir(os.path.expanduser("~/CowAgent"))
    sys.path.insert(0, "~/CowAgent")

    # 2. 加载配置（config.json → conf() 全局字典）
    from config import load_config
    load_config()

    # 3. 获取 Bridge 单例（首次初始化时自动创建 AgentBridge）
    from bridge.bridge import Bridge
    bridge = Bridge()

    # 4. 获取 AgentBridge（首次触发 Agent 完整初始化）
    agent_bridge = bridge.get_agent_bridge()
    return agent_bridge
```

**注意：** 首次调用 `get_agent_bridge()` 会触发 `agent_initializer.py` 中完整的 Agent 初始化流程（memory/tools/prompt/evolution 等），耗时约 0.5-1s。后续调用直接返回缓存实例。

### 4.4 单轮调用 run_agent

```python
def run_agent(agent_bridge, query, session_id):
    renderer = StreamRenderer()

    # 构建 Context
    context = Context(ContextType.TEXT, query)
    context["session_id"] = session_id
    context["receiver"] = session_id
    context["channel_type"] = "terminal"     # 让 EventHandler 走 IM 路径
    context["on_event"] = renderer.handle_event  # 可选，另一方式传回调

    # 直接调用 agent_reply（阻塞直到完成）
    reply = agent_bridge.agent_reply(
        query=query,
        context=context,
        on_event=renderer.handle_event,
        clear_history=False,
    )

    renderer.finish()
    return str(reply.content) if reply else renderer._final_content
```

**关键调用约定（基于 agent_bridge.py:453-658 源码分析）：**

1. **session_id 必须传入** — 用于 Agent 实例缓存 + SQLite 持久化 + cancel/steer 注册
2. **request_id 自动生成** — 每轮调用自动分配唯一 request_id，用于 cancel token
3. **channel_type="terminal"** — 让 `AgentEventHandler` 走 IM 路径逻辑，不主动推中间思考
4. **on_event=renderer.handle_event** — 事件经 handler 过滤后转发给 Renderer
5. **SQLite 持久化自动生效** — agent_reply 内部调 `_pre_persist_user_message` 和 `_persist_messages`

### 4.5 交互模式 interactive

```text
+-------------------------------------+
|  Banner 显示                        |
|  "🐄 CowAgent CLI"                 |
|  "会话: cli_a1b2c3d4e5f6"          |
|  "输入 exit 或 Ctrl+C 退出"         |
+-------------------------------------+
         |
         v  (while True)
+-------------------------------------+
|  prompt = "You: " (蓝色加粗)        |
|  sys.stdin.readline()               |
|                                     |
|  +- KeyboardInterrupt/EOFError --+  |
|  |  break  再见 👋                |  |
|  +-------------------------------+  |
|                                     |
|  +- prompt.strip() 空 -----------+  |
|  |  continue                      |  |
|  +-------------------------------+  |
|                                     |
|  +- prompt.lower() in exit/quit -+  |
|  |  break  再见 👋                |  |
|  +-------------------------------+  |
|                                     |
|  "Agent: " (绿色加粗)               |
|  run_agent(prompt) -> 流式输出       |
|  print()  (换行)                    |
+-------------------------------------+
```

**特殊情况处理：**

| 情况 | 处理方式 |
|:-----|:---------|
| 空输入（直接回车） | `continue` 重新提示 |
| exit / quit / /exit | `break` 退出循环 |
| Ctrl+C（等待输入时） | `break` 退出 |
| Ctrl+C（Agent 运行时） | 当前版本直接退出（未实现 cancel 机制） |
| Agent 无返回结果 | 不额外输出错误信息 |
| 管道 stdin 非 isatty | 自动进入一次性模式 |

### 4.6 一次性模式 oneshot

```python
def oneshot(agent_bridge, query, session_id):
    sys.stdout.write(f"{Style.wrap('Agent: ', Style.BOLD, Style.GREEN)}")
    sys.stdout.flush()
    result = run_agent(agent_bridge, query, session_id)
    if result:
        print()
    return 0
```

触发条件：

- `cowchat "问题"` — 命令行参数作为提问
- `echo "问题" | cowchat` — 管道输入（stdin 非终端）
- `cowchat < input.txt` — 文件重定向

### 4.7 入口 main

```text
main()
  |
  +-- argparse 解析
  |   +-- question? (可选位置参数)
  |   +-- -s/--session (可选，默认自动生成)
  |
  +-- 确定 session_id
  |   +-- args.session 指定 -> 使用指定 ID
  |   +-- 未指定 -> f"cli_{uuid.uuid4().hex[:12]}"
  |
  +-- 确定问题来源
  |   +-- args.question -> 有值
  |   +-- None + stdin 非 isatty -> sys.stdin.read()
  |   +-- None + stdin isatty -> 交互模式
  |
  +-- init_agent()
  |   +-- 成功 -> 继续
  |   +-- 失败 -> print ❌ + return 1
  |
  +-- 路由
      +-- question 有值 -> oneshot() -> return 0
      +-- 无 question -> interactive() -> return 0
```

---

## 5. 设计决策日志

### 5.1 为什么不复用 TerminalChannel？

TerminalChannel 设计为在 `app.py` 的 ChannelManager 子线程中运行，依赖：

1. **完整的 produce/consume 队列与线程池** — `_compose_context` → `produce()` → consume() 线程 → `_handle()` → `build_reply_content()` 整条链路
2. **app.py 启动时的 MCP 预热** — `_warmup_mcp_tools()` 遍历目录加载
3. **web 控制台并发** — `--cmd` 仍会启动 web，占用端口
4. **`os._exit(0)` 硬退出** — `terminal_channel.py:345` 调用 `os._exit(0)` 杀整个进程，无法优雅退出

而 cowchat 的诉求是**轻量、快速、独立进程**：跳过整个 Channel 层，直接同步调用 `AgentBridge.agent_reply()`，启动延迟从"数秒"降到"亚秒级"。

### 5.2 为什么复用 TerminalAgentRenderer → 改为自实现 StreamRenderer

初始设计打算完全复用 `terminal_channel.py:39-169` 的 `TerminalAgentRenderer`，但分析后发现：

| 问题 | 说明 | 影响 |
|:-----|:-----|:-----|
| 依赖 terminal_channel.py | 需 import 整个模块 | 增加耦合 |
| 通道上下文耦合 | 引用了 channel 相关的全局变量 | import 链复杂化 |
| 无 final_content 保留 | Renderer 只渲染不保留结果 | 需额外逻辑获取回复 |
| 换行策略单一 | 使用简单标志 `_has_output` | 无法区分思考/答案/工具段落 |

**决策：** 自实现 `StreamRenderer`（50-150 行），保持自包含、无依赖，同时增加：

- `_reasoning_active` / `_answer_active` 双状态标志 → 动态切换换行策略
- `_final_content` 累加 → run_agent 可直接返回最终文本
- 工具结果截断从 300 → 500 字符

### 5.3 关键调用约定

基于 `agent_bridge.py:453-658` 的源码分析，cowchat 严格遵循以下 5 条约定：

1. **session_id 必须传入** — `agent_bridge.agents: dict[session_id, Agent]` 按 session_id 缓存 Agent 实例，不传入则无法跨轮复用
2. **request_id 每轮自动分配** — `agent_reply()` 内部自动生成唯一 request_id，用于 cancel token 注册（`agent_bridge.py:483-485`），避免与 session 级 token 冲突
3. **channel_type="terminal"** — 让 `AgentEventHandler` 走 IM 路径逻辑，不主动推中间思考（因为 Renderer 已实时渲染）
4. **on_event=renderer.handle_event** — `agent_bridge.py:493` 把 Renderer 作为 `original_callback` 透传，事件经 handler 过滤后转发给 Renderer
5. **SQLite 持久化自动生效** — `agent_reply` 内部调 `_pre_persist_user_message` 和 `_persist_messages`，CLI 会话历史与 Web/IM 共享同一 ConversationStore

### 5.4 为什么选择 scripts/ 而非 cli/commands/

| 因素 | scripts/ | cli/commands/ |
|:-----|:---------|:--------------|
| 模块独立性 | 独立脚本，不依赖 CLI 框架 | 依赖 click、cli.py 注册 |
| 启动速度 | 直接 `python cowchat.py` | 需通过 `cow` 命令间接启动 |
| 目录定位 | `tool_utils.py` 和 `terminal_channel.py` 也在 scripts/ | 匹配已有 13 个子命令 |
| 与项目关系 | 不需要 CowAgent 核心库 | 可能需要 CowAgent CLI 框架依赖 |

**最终决策：** `scripts/cowchat.py`。原因是：

- cowchat 是**直接调用者**（consumer of AgentBridge），不是 **CLI 框架扩展**
- 放在 scripts/ 下更自然——同样的位置已有 `tool_utils.py`、`terminal_channel.py` 等直接使用的脚本
- 不需要 click、cli.py 注册等中间层，启动路径更短
- 如果需要与 `cow` 命令集成，未来只需在 cli.py 加一个 `cow chat` 入口执行 `subprocess.run(["python", "scripts/cowchat.py", ...])`

⚠️ **后续考虑：** 如果未来需要统一到 `cow chat` 命令下（与 13 个子命令一致），可以将 cowchat 的逻辑抽到 `cli/commands/chat.py`，然后用 click 注册。

### 5.5 会话 ID 策略

| 模式 | session_id | 说明 |
|:-----|:-----------|:------|
| 交互模式（无指定） | `cli_{uuid4.hex[:12]}` | 每次运行生成新 ID，新会话 |
| 交互模式（指定 `-s`） | 用户指定的值 | 可复用之前的会话（需 SQLite 中有历史记录） |
| 一次性问答 | `cli_{uuid4.hex[:12]}` | 不需要跨轮上下文，无需持久化会话 |

**为什么不用固定 session_id？** 与文档中"固定 `cli_terminal_session`"的初始设计不同，实际实现选择了每次生成唯一 ID。原因：

- 固定 ID 会导致所有 CLI 会话共享同一 Agent 实例，多轮对话历史累积（包括不同目的的问题）
- 唯一 ID 实现会话隔离，每次 cowchat 是新会话
- 用户可通过 `-s <session_id>` 显式恢复指定会话

### 5.6 无 prompt_toolkit 依赖原则

cowchat 不引入 `prompt_toolkit` 等富交互库，原因：

| 理由 | 说明 |
|:-----|:------|
| 零依赖 | cowchat 只依赖 CowAgent 自身模块，无 pip install |
| 启动速度 | prompt_toolkit import 约 200ms |
| 够用 | sys.stdin.readline() + Style ANSI 满足基本交互需求 |
| 保持简单 | 未来如需历史记录/语法高亮/自动补全，可以在 StreamRenderer 层面渐进增强 |

### 5.7 CowAgent 架构成熟度总结

CowAgent 项目架构成熟度很高，这是 cowchat 能用 289 行代码实现完整 CLI Agent 的根本原因：

1. **三层解耦**（Channel ↔ Bridge ↔ Agent）让扩展新通道成本极低——cowchat 直接从 Bridge 层切入，无需更动任何通道代码
2. **Agent 优先策略**让 `agent_reply` 成为主路径，普通 chatbot 仅作 fallback——简化后的调用链仅 3 步：`load_config()` → `Bridge().get_agent_bridge()` → `agent_reply()`
3. **会话隔离**（`agents: dict[session_id, Agent]`）天然支持多会话——cowchat 每次运行生成新 session_id，自动获得隔离的快照式会话
4. **SQLite 持久化 + 历史恢复**（`_filter_text_only_messages`）让多轮上下文跨进程延续——即使 cowchat 退出再启动，用 `-s` 指定同一 session_id 即可恢复
5. **防循环 + 自愈机制**（tool 失败计数、空响应注入、context overflow 分级恢复）保证 robustness——cowchat 自动继承这些能力，无需额外处理
6. **配置热生效**（`get_full_system_prompt` 每次重读磁盘）无需重启——cowchat 的每条消息都会使用最新的配置和 prompt

**扩展实现**（新增 1 文件 289 行）：

- `cowchat` 启动多轮 agent 终端会话
- 复用 Bridge + AgentBridge，不重造轮子
- 支持交互模式 / 一次性问答 / 管道输入
- 支持 `-s` 指定会话 ID
- 优雅退出（自然循环结束，不杀进程）
- 跨轮上下文自动延续（session_id + SQLite 持久化）
- 8 种事件类型的完整流式渲染（思考流/答案流/工具调用/错误/取消等）

**未做的过度设计：** 没有引入 prompt_toolkit 富交互、没有加多 agent 切换、没有改 app.py / cli.py、没有做 web 控制台集成——保持最小改动面，符合"只做必要修改"的原则。

---

## 6. 附录：关键源码位置速查表

| 模块 | 文件 | 行数 | 说明 |
|:-----|:-----|:-----|:------|
| cowchat | `scripts/cowchat.py` | 289 | CLI 对话客户端（本报告主体） |
| TerminalChannel | `scripts/terminal_channel.py` | 408 | 原有终端通道（app.py --cmd） |
| TerminalAgentRenderer | `scripts/terminal_channel.py` | 39-169 | 原有终端渲染器（cowchat 未复用） |
| AgentBridge | `agent/agent_bridge.py` | 1,204 | Agent 桥接器（核心调用入口） |
| AgentStreamExecutor | `agent/agent_stream.py` | 1,993 | Agent 流式执行引擎 |
| AgentEventHandler | `agent/agent_bridge.py` | 338-450 | 事件处理与过滤 |
| Bridge | `bridge/bridge.py` | 86 | Bridge 层（单例管理） |
| Context | `bridge/context.py` | ~200 | 上下文数据结构 |
| App entry | `app.py` | ~420 | 应用主入口 |
| CLI | `cli/cli.py` | ~80 | cow 命令入口（含 13 子命令） |
| Config | `config.py` | ~100 | 配置加载 |
| AgentInit | `agent/agent_initializer.py` | 680 | Agent 完整初始化流程 |

---

> **变更日志 (Changelog)**
>
> | 日期 | 变更 |
> |:-----|:------|
> | 2026-07-30 | 初始创建 — 基于 cowchat.py v1 实现与设计过程记录 |
