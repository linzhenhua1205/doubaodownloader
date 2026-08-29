# CowAgent 模块调用关系深度分析

> **归档**: knowledge/weekly-reports/07_kb_stat/05_kbsys/2026-08-03-cowagent-module-call-relationship-deep-analysis.md
> **分析日期**: 2026-08-03 | **源码基线**: `/home/lzh/CowAgent`（pyproject version 1.0.0，git 32b5b41）
> **方法**: 源码逐模块核实（app/bridge/channel/agent 四层）+ 调用链推导，所有行号均经 `read` 工具实测确认
> **关联文档**: [CowAgent 工程深度分析（07-30）](2026-07-30-cowagent-engineering-deep-analysis.md)（架构视角，本报告为调用关系专项视角）

---

## 目录 (TOC)

- [一、项目分层总览](#一项目分层总览)
- [二、顶层调用关系（app.py → ChannelManager → Bridge）](#二顶层调用关系apppy--channelmanager--bridge)
- [三、通道层调用关系（channel/）](#三通道层调用关系channel)
- [四、桥接层调用关系（bridge/）](#四桥接层调用关系bridge)
- [五、Agent 层内部调用关系](#五agent-层内部调用关系)
- [六、完整调用关系总图](#六完整调用关系总图)
- [七、关键设计要点](#七关键设计要点)
- [八、模块间耦合度分析](#八模块间耦合度分析)
- [附录：关键源码位置速查表](#附录关键源码位置速查表)

---

## 一、项目分层总览

CowAgent 采用 **五层解耦架构**，从外到内依次是：**入口层 → 通道层 → 桥接层 → Agent 层 → 基础设施层**。分层依据是"依赖方向单一化"：外层只依赖相邻内层，通道层不直接触碰 Agent 层（经桥接层转发），保证渲染器/通道可插拔。

```text
+--------------------------------------------------------------------------+
| Layer 1: Entry (entry layer)                                                   |
|   app.py  run() / ChannelManager / plugin loader / warmup                |
+--------------------------------------------------------------------------+
                    | startup() / send()
                    v
+--------------------------------------------------------------------------+
| Layer 2: Channel (channel layer)                                                 |
|   Channel <- ChatChannel <- WebChannel / TerminalChannel / FeiShuChanel  |
|   producer-consumer: handle() -> session queue -> consume()               |
+--------------------------------------------------------------------------+
                    | fetch_agent_reply(query, context, on_event)
                    v
+--------------------------------------------------------------------------+
| Layer 3: Bridge (bridge layer)                                                  |
|   Bridge (singleton) -> AgentBridge -> AgentInitializer / AgentEventHandler |
|   - session isolation (agents[session_id])                                         |
|   - event loop (on_event -> EventHandler -> channel render)                 |
+--------------------------------------------------------------------------+
                    | create_agent / run_stream
                    v
+--------------------------------------------------------------------------+
| Layer 4: Agent (agent layer)                                                 |
|   Agent / AgentStreamExecutor (turn loop)                                 |
|   - ToolManager (proc singleton)  MemoryManager  SkillManager  PromptBuilder |
+--------------------------------------------------------------------------+
                    | search / sync / flush / execute
                    v
+--------------------------------------------------------------------------+
| Layer 5: Infrastructure (infra layer)                                      |
|   LLM provider (AgentLLMModel -> COW bot)  SQLite (conversation store)   |
|   Embedding provider  MCP subprocess (npx/uvx)  Scheduler (cron)         |
+--------------------------------------------------------------------------+
```

**分层关键事实**（源码核实）：

| 层 | 代表模块 | 核心文件:行号 |
|:---|:---------|:-------------|
| 入口层 | ChannelManager | `app.py:44`（class），`app.py:397`（run） |
| 通道层 | Channel / ChatChannel / WebChannel | `channel/channel.py:12`，`channel/chat_channel.py:25`，`channel/web/web_channel.py:469` |
| 桥接层 | Bridge / AgentBridge / AgentInitializer | `bridge/bridge.py:13`，`bridge/agent_bridge.py:280`，`bridge/agent_initializer.py:21` |
| Agent 层 | Agent / AgentStreamExecutor | `agent/protocol/agent.py:13`，`agent/protocol/agent_stream.py:162` |
| 基础设施层 | ToolManager / MemoryManager / LLM | `agent/tools/tool_manager.py:31`，`agent/memory/manager.py:20`，`bridge/agent_bridge.py:90`（AgentLLMModel） |

---

## 二、顶层调用关系（app.py → ChannelManager → Bridge）

### 2.1 启动流程（app.py:397-447 run() 按顺序）

`run()` 是进程唯一入口，执行链（经核实，`run()` 实际位于 397-455，channel 启动调用在 447）：

```text
run()  [app.py:397]
  |-- 1. ensure_ca_bundle()              TLS CA fallback (packaged build)  [401]
  |-- 2. load_config()                   load config.json               [405]
  |-- 3. _warn_if_legacy_workspace_data_exists()  legacy-workspace warning      [406]
  |-- 4. sigterm_handler_wrap(SIGINT/SIGTERM)     signal handling              [408-410]
  |-- 5. parse channel_type -> channel_names (comma/list)      [413-420]
  |-- 6. web_console default on -> append "web"                 [423-425]
  |-- 7. _sync_builtin_skills()          sync builtin skills to workspace  [428]
  |-- 8. _warmup_mcp_tools()             MCP subprocess warmup (non-desktop) [434]
  |-- 9. _warmup_scheduler()             AgentBridge eager-init         [440-442]
  |        -> Bridge().get_agent_bridge()  [bridge.py:173] -> AgentBridge
  |           -> init_scheduler() (idempotent, cron thread starts now)              [agent_bridge.py:299]
  |           -> start_evolution_trigger() (self-evolution idle trigger)          [agent_bridge.py:307]
  |-- 10. _channel_mgr = ChannelManager()                               [446]
  |-- 11. _channel_mgr.start(channel_names, first_start=True)           [447]
  `-- 12. while True: sleep(1)            main thread stays alive            [449-450]
```

**关键点**：`_warmup_scheduler()` 使调度器/自进化在**首个用户消息前**启动；desktop 模式下移入后台线程避免阻塞 Web API 就绪（app.py:436-440）。

### 2.2 ChannelManager 多通道调度（app.py:44-139）

ChannelManager 是"多通道并发生命周期管理器"，每个通道在独立 daemon 线程中 `startup()`：

| 职责 | 方法 | 关键行为（源码:行号） |
|:-----|:-----|:----------------------|
| 创建+启动 | `start(channel_names, first_start)` | 先停同名旧通道防重复消费（76-79）；`channel_factory.create_channel(name)`（84）；web 先启、其余延时 0.1s（122-139） |
| 首通道选择 | `_primary_channel` | 首个非 web 通道为 primary（88-92），`channel` property 兼容旧代码（58-61） |
| 线程包装 | `_run_channel` | `channel.startup()` 异常隔离（141-146） |
| 优雅停止 | `stop(name)` | pop 后锁外 stop（154-160）；`ch.stop()` 优先，5s 超时后 `_interrupt_thread`（178-186） |
| 强制中断 | `_interrupt_thread` | `ctypes.PyThreadState_SetAsyncExc` 注入 SystemExit（188-205） |
| 热重启 | `restart` / `add_channel` / `remove_channel` | 清 singleton 缓存后重建（207-245）；`_clear_singleton_cache` 遍历闭包清空实例字典（248-289） |

**防重复消费设计**（注释原文，app.py:71-75）：并发路径可能已启动同一通道，若直接覆盖注册表会导致孤儿实例继续消费事件 → 每条消息被处理两次。因此 `start()` 前先停旧实例。

### 2.3 Bridge 单例与懒加载（bridge/bridge.py:12-91）

```text
Bridge (class, @singleton)          [bridge.py:13]
  |- btype = {chat, voice_to_text, text_to_voice, translate}  model routing table [15-22]
  |- bot_type resolution -> btype["chat"]  (openai/azure/baidu/qwen/gemini/glm/
  |                                   claude/moonshot/doubao/deepseek/mimo/
  |                                   qianfan/modelscope/minimax/linkai)  [24-87]
  |- bots = {}          bot instance cache (lazy)                              [89]
  |- chat_bots = {}                                                       [90]
  `- _agent_bridge = None   AgentBridge lazy load                            [91]
```

关键入口（bridge.py:173-197）：

```text
get_agent_bridge()                     [173-180]
  |-- _agent_bridge is None?
  |     -> from bridge.agent_bridge import AgentBridge
  |     -> self._agent_bridge = AgentBridge(self)
  `-- return _agent_bridge

fetch_agent_reply(query, context, on_event, clear_history)  [182-197]
  `-- agent_bridge = self.get_agent_bridge()
      `-- agent_bridge.agent_reply(query, context, on_event, clear_history)
```

**说明**：传统 bot（chat/voice/translate）经 `get_bot(typename)` 懒加载（134-145），与 Agent 路径完全分离——`fetch_agent_reply` 走 AgentBridge，`fetch_reply_content` 走传统 bot（150-151）。这是"通道只认 Bridge 统一入口"的解耦设计。

---

## 三、通道层调用关系（channel/）

### 3.1 四层继承结构

```text
+--------------------+   Channel (abstract base)          channel/channel.py:12
| startup/send/handle_text all NotImplementedError |
+--------------------+
        ^  extends
+--------------------+   ChatChannel (generic logic)   channel/chat_channel.py:25
| producer-consumer: sessions dict + consume thread |
| _compose_context / _handle / reply routing |
+--------------------+
        ^  extends (concrete channels, 15 impls)
+---------+  +---------+  +---------+  +-------------+
| Web     |  | Terminal|  | FeiShu  |  | WeChatMP    |  etc.
| Channel |  | Channel |  | Chanel  |  | /QQ/Slack/  |
+---------+  +---------+  +---------+  +-------------+
```

| 通道 | 类（文件:行号） | 渲染方式 |
|:-----|:----------------|:---------|
| Web | `WebChannel`（web_channel.py:469） | SSE 流式 + 轮询兜底 |
| Terminal | `TerminalChannel`（terminal_channel.py:190） | ANSI 彩色 + `TerminalAgentRenderer`（:39） |
| 飞书 | `FeiShuChanel`（feishu_channel.py:238） | 流式卡片（progress card） |
| 微信公众号 | `WechatMPChannel`（wechatmp_channel.py:39） | 被动回复 |
| 企微/QQ/Slack/Telegram/Discord/钉钉 | 各 `*Channel` | 平台原生消息 |

### 3.2 ChatChannel 的生产者-消费者模型（chat_channel.py:29-41）

```text
__init__ (per-instance, no cross-channel mixup) [29-41]
  |- self.futures = {}     Future tracking
  |- self.sessions = {}    session_id -> [Dequeue, Semaphore]
  |- self.lock = threading.Lock()
  `- threading.Thread(target=self.consume, daemon=True).start()   [39-41]
        ^ one consume thread per channel instance
```

> **历史教训**（注释 31-35）：sessions 曾是 class-level，导致 A 通道的 context 被 B 通道 consume 线程消费（"No request_id found in context"）。改为 instance-level 后彻底隔离。

消息流：平台回调 → `handle()` → `_compose_context()`（构造 Context，注入 channel_type/origin_ctype/session_id）→ `enqueue`（写入本通道 session 队列）→ `consume()` 线程取消息 → 判定 Agent/传统 bot 路由 → `Bridge().fetch_agent_reply(...)` 或 `fetch_reply_content(...)` → `send()` 回发。

### 3.3 on_event 协议统一（三种渲染器共用同一事件 schema）

事件由 AgentStreamExecutor `_emit_event`（agent_stream.py:382）发出，经 `AgentEventHandler`（bridge/agent_event_handler.py:12）转发到通道。事件类型（schema）与三种渲染映射（源码核实）：

| 事件类型 | WebChannel (SSE) | TerminalChannel (ANSI) | FeiShuChannel (流式卡片) |
|:---------|:-----------------|:-----------------------|:-------------------------|
| `turn_start` | SSE 帧 | 紫色斜体 reasoning | Reasoning 区 |
| `reasoning_update` | SSE 帧 | 紫色斜体（持续） | Reasoning 区（快照异步推送） |
| `message_update` | SSE 帧 | 正常色 | Content 区（push_queue 异步累加） |
| `message_end` | SSE 帧 | 结束本段 | 工具轮结束后原地刷新卡片 |
| `tool_execution_start/end` | SSE 帧 | 青色 + 绿/红勾叉 | Tools 区（每工具起止刷新） |
| `agent_end` | SSE `done` 帧 | 换行 + 耗时 | 关闭 streaming_mode 收尾卡片 |
| `agent_cancelled` | SSE 帧 | 取消提示 | 卡片标记取消 |
| `error` | SSE 帧 | 红色错误 | 卡片错误态 |

**统一协议实现**：`AgentEventHandler.handle_event`（agent_event_handler.py:35-55）按 event_type 分发 → 若 `context["on_event"]` 存在则直接回调（web 用，SSE 直推），否则走 `_send_to_channel` 通道发送（微信配额合并缓冲，:89-114）。

### 3.4 WebChannel 的 SSE 流式推送（web_channel.py:516-600 send()）

> 提纲标注 1035-1176，实测 SSE 推送核心在 `send()`（516-600）与 `sse_queues` 结构（483）；1035-1176 为 post_message 附件/取消处理区，一并核实。

```text
WebChannel.__init__                     [478-490]
  |- sse_queues = {}        request_id -> Queue (SSE streaming)
  |- sse_last_active = {}   janitor prevents long-stream kill
  `- _sse_janitor thread

send(reply, context)                    [516-600]
  |- request_id = context["request_id"]   (drop if missing)
  |- if request_id in sse_queues:         SSE mode
  |     |- sse_phase -> {"type":"phase"}  intermediate status (e.g. install-browser)
  |     |- file:// 回复 -> skip duplicate push, send done only
  |     |- http(s) 媒体 -> frontend renderMarkdown, skip
  |     `- 默认 -> {"type":"done", content, user_seq, bot_seq}
  |           + auto TTS: _maybe_dispatch_auto_tts()  (voice_attach event)
  `- else: polling fallback -> session_queues push
```

**流式链路**：LLM chunk → `_call_llm_stream` → `_emit_event("message_update", {delta})` → `AgentEventHandler` → `on_event` 回调 → `sse_queues[request_id].put(...)` → SSE 长连接推送。`done` 事件携带 `user_seq/bot_seq` 供前端编辑/重新生成按钮定位（web_channel.py:501-515）。

---

## 四、桥接层调用关系（bridge/）

### 4.1 AgentBridge 与 AgentInitializer 协作（agent_bridge.py:286-310）

```text
AgentBridge.__init__(bridge: Bridge)          [286-310]
  |- self.bridge = bridge        holds global singleton (back-ref)
  |- self.agents = {}            session_id -> Agent   [288] session isolation core
  |- self.default_agent = None   no-session fallback
  |- self.initializer = AgentInitializer(bridge, self)   [294] assembler
  |- init_scheduler(self)        scheduler eager start (idempotent) [299-301]
  `- start_evolution_trigger(self)  self-evolution idle trigger    [307-308]

get_agent(session_id=None)                    [374-394]
  |- session_id is None -> default_agent lazy init    [385-388]
  |- session_id not in agents -> _init_agent_for_session  [391-392]
  `- return agents[session_id]

_init_agent_for_session(session_id)           [401-404]
  `- agents[session_id] = initializer.initialize_agent(session_id)
```

**调用方向**：`AgentBridge` 持有 `AgentInitializer`（装配器），后者回调 `self.agent_bridge.create_agent()` 创建 Agent（agent_initializer.py:102），形成"桥接层内双向协作 + Agent 层单向被建"。

### 4.2 AgentInitializer 的四大组件装配（agent_initializer.py:41-127 按顺序）

`initialize_agent(session_id)` 是 Agent 的完整工厂（实测 41-127，含 4 大组件 + 2 附属）：

```text
initialize_agent(session_id)                  [41-127]
  |-- 0. workspace prep: _migrate_config_to_env + _load_env_file        [57-60]
  |         ensure_workspace(workspace_root, create_templates=True)     [63-64]
  |-- 1. MemoryManager: _setup_memory_system(workspace, session_id)     [70]
  |         + returns memory_tools (memory_search/memory_get/memory_add)
  |-- 2. ToolManager: _load_tools(workspace, memory_manager, tools)     [73]
  |         -> ToolManager().load_tools() + create instances for Agent
  |-- 3. Scheduler: _initialize_scheduler(tools, session_id)            [76]
  |-- 4. SkillManager: _initialize_skill_manager(workspace, session)    [82]
  |-- 5. PromptBuilder: build(tools, context_files, skill_manager,      [85-94]
  |         memory_manager, runtime_info) -> system_prompt
  |-- 6. create_agent(system_prompt, tools, max_steps=20,               [102-112]
  |         max_context_tokens=50000, skill_manager, enable_skills)
  |-- 7. agent.memory_manager = memory_manager  (attached later)            [115-118]
  |-- 8. _restore_conversation_history(agent, session_id)  history restore      [121-122]
  `-- 9. _start_daily_flush_timer()  daily distillation (once per proc)  [124-125]
```

> **组件装配顺序的意义**：memory/tools 先行（它们被 prompt 引用），scheduler/skill_manager 中间（tool 依赖），PromptBuilder 最后统一收集（tools + context_files + skill_manager + memory_manager + runtime_info）——五大输入在 build 时全部就位。

### 4.3 完整事件回路

```text
                    +-----------------------------+
                    |  AgentStreamExecutor        |
                    |  _emit_event(event_type)    |  agent_stream.py:382
                    +--------------+--------------+
                                   | event (dict: type + data)
                                   v
                    +--------------+--------------+
                    |  AgentEventHandler          |  agent_event_handler.py:12
                    |  handle_event(event)        |
                    |  |- turn_start / reasoning  |
                    |  |- message_update / end    |
                    |  |- tool_execution_*        |
                    |  `- agent_end / cancelled   |
                    +--------------+--------------+
                                   |
              +--------------------+--------------------+
              | on_event present?                        |
              v                                        v
  +-----------+-----------+              +-------------+--------------+
  | Web: pass through on_event |              | IM channels: _send_to_channel |
  | -> sse_queues.put     |              |   -> channel._send(reply)  |
  +-----------------------+              +----------------------------+
```

---

## 五、Agent 层内部调用关系

### 5.1 Agent 装配与持有关系（agent/protocol/agent.py:14-78）

> 提纲标注 `agent.py:14-78`，实测文件位于 `agent/protocol/agent.py`。

```text
Agent.__init__                                            [14-78]
  |- system_prompt    (rebuilt each turn, see 5.5)
  |- model: LLMModel  (AgentLLMModel, bridges COW bot infra)
  |- tools: list      (BaseTool instances, injected via add_tool) [42, 76-78]
  |- messages: list   (unified message history)                [49]
  |- messages_lock    (thread-safe)                            [50]
  |- memory_manager   (optional, attached by initializer)     [51]
  |- skill_manager    (created/injected when enable_skills)   [62-74]
  |- workspace_dir / runtime_info / extra_system_suffix
```

**关键设计**：Agent **不持有 ToolManager** —— ToolManager 是进程级单例（tool_manager.py:35-43），Agent 只持有工具实例列表；运行时通过 `sync_mcp_into_agent(agent)` 做增量同步（见 5.3），解耦了"工具注册表"与"工具实例集合"。

### 5.2 AgentStreamExecutor turn 循环（agent_stream.py:546-967）

`run_stream(user_message)` 是 Agent 推理主循环（实测 546-967 与提纲一致）：

```text
run_stream(user_message)                                  [546]
  |-- append user msg (content blocks, Claude fmt)  [566-574]
  |-- _trim_messages()        context trim (tool chains intact)      [579]
  |-- _validate_and_fix_messages()  orphan tool_use fix      [584]
  |-- _emit_event("agent_start")                           [586]
  |-- while turn < max_turns:                              [599]
  |     |- _check_cancelled()           safety point 1: turn start [602]
  |     |- _drain_steering() -> steer injection              [604-606]
  |     |- _emit_event("turn_start")                       [610]
  |     |- _call_llm_stream(retry_on_empty=True)           [613]
  |     |     `- streaming: cancel probe every 8 chunks (safety 3) [1127-1131]
  |     |- steer override: synth results for pending tool_calls [620-632]
  |     |- if not tool_calls: end loop                      [635]
  |     |     `- empty resp: inject "reply to user" prompt + retry [637-665]
  |     |- else: execute tools                                   [744+]
  |     |     |- _check_cancelled()    safety point 2: between tools [748]
  |     |     |- _drain_steering() -> steer interrupts remaining tools [749-755]
  |     |     |- _execute_tool(tool_call)                  [757]
  |     |     `- _check_consecutive_failures prevent repeated failure [475]
  |     `- turn += 1
  |-- max_turns: inject summary prompt, remove after use  [906-945]
  |-- AgentCancelledError -> _handle_cancelled patch history [951-956]
  |-- finally: emit agent_end + close steer_inbox           [961-967]
  `-- return final_response
```

**安全点设计**（三类，见 7.5）：turn 开始（602）、工具之间（748）、LLM 流式每 8 chunk（`_CANCEL_PROBE_EVERY = 8`，1127）。

### 5.3 ToolManager 的三层职责（agent/tools/tool_manager.py）

| 职责 | 方法 | 调用时机 |
|:-----|:-----|:---------|
| 加载 | `load_tools()`（:91） | AgentInitializer 初始化时（`_load_tools` → `initialize_agent` 第 2 步） |
| 创建实例 | `create_tool(name)` | AgentInitializer 装配 Agent 时（`create_agent` 内遍历 tool_classes） |
| 运行时同步 | `sync_mcp_into_agent(agent)`（:535） | 每个 turn 的 `_call_llm_stream` 前（MCP 延迟加载工具补注） |
| 热重载 | `refresh_mcp_if_changed()`（:357） | AgentBridge.agent_reply 收尾 `_schedule_mcp_hot_reload`（agent_bridge.py:660-683） |

**sync_mcp_into_agent 双形态支持**（:549-607）：`agent.tools` 为 list（Agent 类）或 dict（AgentStream 类）均兼容；跳过 `_evolution_restricted` 受限审查 agent（:558-566）；返回 `(added, removed)` 供日志。

**MCP 生命周期**（:262-357）：`_mcp_json_path` → `_read_mcp_json_signature`（mtime+sha256）→ 变更才重载 → `_mcp_active_configs` diff 级 reload；`_mcp_loaded` 幂等标志防止并发重复 fork 子进程（:57-62）。

### 5.4 MemoryManager 的三个接口（agent/memory/manager.py）

| 接口 | 调用方 | 场景 |
|:-----|:-------|:-----|
| `search(query, user_id, ...)`（:90） | `MemorySearchTool.execute()`（tools/memory/memory_search.py:81） | LLM 调用 memory_search 工具 |
| `sync(force=False)`（:251） | `AgentInitializer._sync_memory()`（agent_initializer.py:319） | 会话初始化/周期同步（两遍法批量 embed） |
| `flush_memory(messages, reason, ...)`（:410） | `AgentStreamExecutor._trim_messages()` | 上下文裁剪/溢出时蒸馏 |

**search 混合检索**（:112-120）：vector + keyword 双路，`include_shared` 控制范围。**sync 两遍法**（:257-270）：先扫文件收集变更 chunk，再单次 `embed_batch`（101 文件 ~100 HTTP 调用 → 1 批）。

### 5.5 PromptBuilder 的 8 个 Section（agent/prompt/builder.py:85-154）

`build_agent_system_prompt()` 每次 `agent.get_full_system_prompt()` 从零重建：

```text
Section order (builder.py docstring + code):
  1. Tooling       tooling defs (capability first, _build_tooling_section)
  2. Skills        skills guidance (needs read tool)
  3. Memory        memory capability docs
  3.5 Knowledge    structured KB (knowledge/index.md injected)
  4. Workspace     workspace description
  5. User identity user identity (optional)
  6. Project context  AGENT.md / USER.md / RULE.md / MEMORY.md / BOOTSTRAP.md
  7. Runtime info  runtime meta (time/model, dynamic)
  8. Response language  response-language rule (always appended)
```

**设计要点**：每次重建保证**磁盘修改立即生效**（AGENT.md 改完下轮 prompt 即变）；代价是每次请求都要读文件 + 重新拼装。`runtime_info` 通过 `_get_runtime_info`（agent_initializer.py:486）动态取时间/模型。

---

## 六、完整调用关系总图

```text
+----------------------------------------------------------------------+
| ENTRY (app.py)                                                       |
|  run() -> ChannelManager.start(channel_names)                        |
|          |  +-- _warmup_mcp_tools()   (ToolManager._load_mcp_tools)  |
|          |  `-- _warmup_scheduler()   (Bridge.get_agent_bridge)      |
+----------------------------------------------------------------------+
          | startup() per channel (daemon threads)
          v
+----------------------------------------------------------------------+
| CHANNEL (channel/)                                                   |
|  WebChannel / TerminalChannel / FeiShuChanel  ...                    |
|   handle() -> _compose_context() -> session queue -> consume()       |
|    |                                                                 |
|    | fetch_agent_reply(query, ctx, on_event)                         |
|    v                                                                 |
+----------------------------------------------------------------------+
| BRIDGE (bridge/)                                                     |
|  Bridge (singleton)                                                  |
|    |-- fetch_reply_content -> bot (legacy model path)                     |
|    `-- fetch_agent_reply -> AgentBridge                              |
|          |-- agents[session_id]  (lazy create)                            |
|          |-- AgentInitializer.initialize_agent(session_id)           |
|          |     |-- MemoryManager.setup / sync                        |
|          |     |-- ToolManager.load_tools / create_tool              |
|          |     |-- SkillManager / Scheduler / PromptBuilder.build    |
|          |     `-- create_agent -> Agent                             |
|          |-- AgentEventHandler (event loop -> channel render)          |
|          |-- _pre_persist_user_message (SQLite)                      |
|          `-- _persist_messages / _schedule_mcp_hot_reload            |
+----------------------------------------------------------------------+
          | agent_reply -> agent.run_stream (turn loop)
          v
+----------------------------------------------------------------------+
| AGENT (agent/protocol/)                                              |
|  AgentStreamExecutor.run_stream                                     |
|    |-- _call_llm_stream -> AgentLLMModel -> COW bot -> LLM provider  |
|    |-- _execute_tool -> ToolManager (tool instances/MCP)                   |
|    |-- _trim_messages -> MemoryManager.flush_memory                  |
|    |-- MemorySearchTool -> MemoryManager.search                      |
|    `-- _emit_event -> AgentEventHandler -> channel                   |
+----------------------------------------------------------------------+
```

---

## 七、关键设计要点

### 7.1 单例与懒加载层次

| 层级 | 单例/懒加载 | 文件:行号 |
|:-----|:------------|:----------|
| Bridge | `@singleton` 装饰器 | bridge.py:12-13 |
| AgentBridge | Bridge 持有，首次 `get_agent_bridge()` 创建 | bridge.py:173-180 |
| Agent（每 session） | `AgentBridge.agents[session_id]` 懒加载 | agent_bridge.py:374-394, 401-404 |
| Bot | `Bridge.bots[typename]` 懒加载 | bridge.py:134-145 |
| ToolManager | 进程级单例（`__new__` 拦截） | tool_manager.py:35-43 |

### 7.2 会话隔离机制

- **Agent 实例隔离**：`AgentBridge.agents: dict[session_id, Agent]`（agent_bridge.py:288）——每会话独立 Agent、独立消息历史、独立 memory_manager
- **消息队列隔离**：`ChatChannel.sessions: dict[session_id, [Dequeue, Semaphore]]`（chat_channel.py:37）——instance-level，防跨通道串扰
- **调度器会话特殊处理**（agent_bridge.py:529-534）：`scheduler_` 前缀 session 使用更小上下文窗口（`_trim_in_memory_to_turns`），跳过自进化

### 7.3 持久化策略

| 策略 | 实现 | 时机 |
|:-----|:-----|:-----|
| 预持久化 | `_pre_persist_user_message`（agent_bridge.py:811） | 用户消息在 agent 运行前落库（防崩溃丢失，切页/刷新不丢 in-flight 会话） |
| 后持久化 | `_persist_messages`（agent_bridge.py:853） | assistant/tool 消息运行结束后批量落库（跳过已预存的 user 首条） |
| 历史恢复 | `_restore_conversation_history`（agent_initializer.py:129） | 新会话从 SQLite 恢复，`_filter_text_only_messages` 仅取文本剥离工具链（:178） |
| 每日蒸馏 | `_start_daily_flush_timer`（agent_initializer.py:599） | 23:50-23:55 随机抖动，`_flush_all_agents` 内存摘要 + Deep Dream |

### 7.4 on_event 协议统一

三种渲染器共用同一事件 schema（见 3.3 表），实现"同协议、不同渲染"：

- WebChannel：SSE 帧（`sse_queues[request_id].put`）
- TerminalChannel：ANSI 彩色（`TerminalAgentRenderer`）
- FeiShuChannel：流式卡片（progress_state 快照 + push_queue 异步推送，feishu_channel.py:1197-1260）

### 7.5 turn 循环的安全点设计

cancel/steer 在三类安全点检查（agent_stream.py）：

1. **turn 开始**（:602）——两次 turn 之间到达的 cancel 立即短路
2. **工具之间**（:748）——取消剩余工具执行，steer 中断并补合成结果
3. **LLM 流式每 8 chunk**（`_CANCEL_PROBE_EVERY = 8`，:1127-1131）——流式中断时仅持久化 partial text（tool_use 参数截断会失败）

### 7.6 消息完整性兜底

| 兜底 | 实现（agent_stream.py） |
|:-----|:------------------------|
| 取消补全 | `_handle_cancelled`（:304）给孤立 tool_use 补 tool_result |
| 异常兜底 | finally 块给异常中断构造 emergency result |
| 注入提示清理 | 强制回复/总结 prompt 用完即从 messages 移除（:646-665, :940-945） |
| 孤儿修复 | `_validate_and_fix_messages`（:1615）修剪后修复 tool_use/tool_result 配对 |

---

## 八、模块间耦合度分析

```text
HIGH COUPLING (direct ownership / composition):
  Bridge ----------> AgentBridge ----------> Agent
  AgentInitializer --> MemoryManager / ToolManager / SkillManager / Agent

MEDIUM COUPLING (runtime association):
  AgentStreamExecutor --> ToolManager   (sync_mcp_into_agent per turn)
  AgentStreamExecutor --> MemoryManager (flush_memory on trim)

LOW COUPLING (event callback):
  Channel <--on_event--> AgentEventHandler <--> Agent
  Channel --> Bridge (fetch_agent_reply) --> AgentBridge

NO COUPLING (assembled at bridge layer):
  ToolManager  <-> Agent          (no direct ref; wired by bridge)
  SkillManager <-> ToolManager    (independently assembled by AgentInitializer)
```

**耦合度结论**（源码核实推导）：

1. **高耦合区集中在桥接层**——AgentBridge 是唯一同时知道 Channel 事件、Agent 实例、持久化、MCP 热重载的地方；这是刻意的"上帝对象"（单点编排），换取 Agent 层纯净。
2. **Agent 层与基础设施解耦**——Agent 不持 ToolManager 引用（仅工具实例列表），MemoryManager 通过 `agent.memory_manager` 后挂（agent_initializer.py:115-118），使 Agent 可脱离 COW 独立测试。
3. **通道层零依赖 Agent 层**——通道只调 `Bridge.fetch_agent_reply`，事件经回调反推，无 import 依赖（验证：chat_channel.py 无 `from agent` 导入）。
4. **潜在风险**：AgentBridge 承担过多职责（会话管理 + 事件 + 持久化 + MCP 热重载 + steer），agent_bridge.py 1204 行是桥接层最大文件，后续拆分可考虑按"会话生命周期 / 持久化 / 事件"三域。

---

## 附录：关键源码位置速查表

| 功能 | 文件:行号 |
|:-----|:----------|
| run() 启动流程 | app.py:397-455 |
| ChannelManager.start | app.py:66-139 |
| Bridge 单例 | bridge/bridge.py:12-13 |
| get_agent_bridge 懒加载 | bridge/bridge.py:173-180 |
| fetch_agent_reply | bridge/bridge.py:182-197 |
| AgentBridge 初始化 | bridge/agent_bridge.py:286-310 |
| get_agent 会话懒加载 | bridge/agent_bridge.py:374-394 |
| agent_reply 主流程 | bridge/agent_bridge.py:453+ |
| MCP 热重载调度 | bridge/agent_bridge.py:660-683 |
| 预持久化 | bridge/agent_bridge.py:811-851 |
| AgentInitializer 装配 | bridge/agent_initializer.py:41-127 |
| 每日蒸馏定时器 | bridge/agent_initializer.py:599-632 |
| Agent 构造 | agent/protocol/agent.py:14-78 |
| run_stream turn 循环 | agent/protocol/agent_stream.py:546-967 |
| cancel 探测 (8 chunk) | agent/protocol/agent_stream.py:1127-1131 |
| ToolManager 单例 | agent/tools/tool_manager.py:31-43 |
| sync_mcp_into_agent | agent/tools/tool_manager.py:535-610 |
| MemoryManager.search/sync/flush | agent/memory/manager.py:90/251/410 |
| PromptBuilder 8 sections | agent/prompt/builder.py:85-154 |
| AgentEventHandler | bridge/agent_event_handler.py:12-55 |
| ChatChannel 生产者-消费者 | channel/chat_channel.py:29-41 |
| WebChannel SSE send | channel/web/web_channel.py:516-600 |
| FeiShu 流式卡片 | channel/feishu/feishu_channel.py:1197-1260 |
| Terminal ANSI 渲染 | channel/terminal/terminal_channel.py:39-170 |

---

## Changelog

| 日期 | 版本 | 变更 |
|:-----|:-----|:-----|
| 2026-08-03 | v1.0 | 首次创建：五层架构 + 全链路调用关系源码级核实（23 个速查点） |

> **说明**：提纲中 `app.py run() 387-445`（实测 397-455）、`web_channel.py:1035-1176`（实测 SSE 核心在 516-600，1035+ 为 post_message 区）、`agent.py`（实测在 `agent/protocol/agent.py`）三处与源码有出入，本报告以实测为准。
