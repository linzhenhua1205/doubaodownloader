# 🏗️ CowAgent CLI 批量问答与 Agent 重用架构设计

> **日期**: 2026-07-31 | **作者**: 小龙猫 | **上下文**: cowchat v2 → batch 扩展

---

## 目录

- [1. 问题定义](#1-问题定义)
- [2. 核心性能瓶颈分析](#2-核心性能瓶颈分析)
- [3. 方案设计](#3-方案设计)
- [4. 关键决策](#4-关键决策)
- [5. 实现计划](#5-实现计划)
- [6. 风险与缓解](#6-风险与缓解)

---

## 1. 问题定义

### 1.1 需求

> 实现批量问题的导入，针对每个问题以 agent 模式调用相关 skills 生成对应的知识库文档。
> 读取一个文件（每行一个问题），自动逐个处理。

### 1.2 约束

| # | 约束 | 说明 |
|:--|:-----|:------|
| 1 | **Agent 模式** | 每个问题必须走完整的 Agent 推理循环（调用 tools/skills），不只是 LLM 问答 |
| 2 | **批量处理** | 文件中有 N 个问题（N=10~100+），需自动逐个处理 |
| 3 | **Skills 可用** | Agent 必须加载技能（knowledge-wiki, deep-tech-writer 等），不只是 bare LLM |
| 4 | **输出知识库** | 每个问题的处理结果应生成为 `knowledge/` 下的结构化文档 |
| 5 | **性能可接受** | N=50 时总耗时不应远超 N × (单问题 LLM 推理时间) |

### 1.3 现有方案瓶颈

当前可用入口对比：

| 入口 | 初始化耗时 | 多轮重用 | 批量支持 | 适合场景 |
|:-----|:---------:|:--------:|:--------:|:---------|
| `cow chat "问..."` | **~0.3s/次** | ❌ 进程级隔离 | ❌ 需 shell loop | 单次问答 |
| `cow chat` 交互模式 | **~0.3s/次** | ✅ 同一进程多轮 | ❌ 需手动输入 | 交互对话 |
| Web 模式 (app.py) | **~3-5s** (全量) | ✅ 同一 agent 多轮 | ❌ 需 HTTP 调用 | 长运行服务器 |
| 直接 `python` | **0s** (import 后) | ✅ 代码内循环 | ✅ | **批量处理 ←我们的目标** |

**核心问题**: 每次 `cow chat "问..."` 创建一个新进程，Agent 初始化成本（~0.3s）重复 N 次。N=100 时 30s 纯 overhead。

---

## 2. 核心性能瓶颈分析

### 2.1 Agent 初始化耗时分解

```text
初始化超时分解（基于实测）：

Bridge()                        ~0.00s    轻量，仅设置 bot_type
AgentLLMModel(bridge)           ~0.22s    创建 LLM bot driver（含模型识别）
ToolManager.load_tools()        ~0.04s    扫描 import 14 个 tool 类
  +- create_tool(x14)           ~0.22s    实例化每个 tool（含依赖检查）
SkillManager()                  ~0.28s    扫描 ~/cow/skills/ 目录
PromptBuilder.build()           ~0.01s    拼接系统提示词
Agent()                         ~0.00s    纯内存对象创建
-----------------------------------
TOTAL (one-time)                ~0.77s
```

### 2.2 批量化前后对比

```text
N=50 场景：

per-process（当前）:
  total = 50 × (0.77s init + T_llm)  ≈  38.5s + 50×T_llm

agent-reuse（目标）:
  total = 0.77s init + 50 × T_llm

节省: 38.5s overhead （≈ 98% init 开销消除）
```

### 2.3 扩展性预估

| N | per-process init | agent-reuse init | 节省 |
|:-:|:----------------:|:----------------:|:----:|
| 10 | 7.7s | 0.77s | 6.9s |
| 50 | 38.5s | 0.77s | 37.7s |
| 100 | 77.0s | 0.77s | 76.2s |
| 500 | 385s | 0.77s | ~6.4min |

**结论**: N≥10 时 agent-reuse 模式的 init 开销已可忽略不计。

---

## 3. 方案设计

### 3.1 架构总图

```text
                cow batch --file questions.txt
                           |
                +----------+----------+
                |   Phase 1: Init     |    <- 一次性
                |  Bridge->Model->Agent |
                |  14 tools, 3 skills |
                +----------+----------+
                           |
                +----------+----------+
                |  Phase 2: Loop      |    <- N 次，agent 重用
                |                     |
                |  +-----------------+|
                |  | Read question   ||
                |  | agent.run_stream||
                |  | Capture output  ||
                |  | Save to KB      ||
                |  | Clear context   ||
                |  +-----------------+|
                |       ... × N       |
                +----------+----------+
                           |
                +----------+----------+
                |  Phase 3: Report    |    <- 一次性
                |  paths to generated |
                |  documents          |
                +---------------------+
```

### 3.2 Phase 1: 一次性初始化

```text
Input:
  - workspace_root (~/cow)

Output:
  - Agent 实例（带 tools + skills）
  - SkillManager 实例（skills 已加载）
  - workspace 就绪

流程:
  1. load_config()
  2. Bridge()
  3. AgentLLMModel(bridge)
  4. ToolManager -> load_tools() -> create all tools with cwd=workspace_root
  5. SkillManager(builtin_dir=~/CowAgent/skills, custom_dir=~/cow/skills)
  6. load_context_files() + PromptBuilder.build() with full tools+skills
  7. Agent(system_prompt, model, tools, skill_manager, enable_skills=True, ...)
```

### 3.3 Phase 2: 批处理循环

```text
每次迭代:

  +- Read line from input file ----------------------+
  |  question = "调研 NVIDIA Vera Rubin 架构并归档"    |
  +---------------------+-----------------------------+
                        |
  +- Clear context -----v-----------------------------+
  |  agent.messages.clear()  (独立问题，无需上下文)    |
  +---------------------+-----------------------------+
                        |
  +- Call agent --------v-----------------------------+
  |  response = agent.run_stream(                     |
  |      user_message=question,                       |
  |      on_event=progress_reporter.handle_event,     |
  |      clear_history=True,                          |
  |  )                                                |
  |                                                    |
  |  <- Agent 内部使用 read/write/search_files 等工具  |
  |    自行完成：搜索 -> 分析 -> 写入知识库               |
  +---------------------+-----------------------------+
                        |
  +- Capture result ----v-----------------------------+
  |  if response has error:                           |
  |    log_error(question, response)                  |
  |  else:                                            |
  |    log_success(question, "written to ...")         |
  +---------------------+-----------------------------+
                        |
                    ----+----  <- 循环至文件末尾或失败计数超限
```

### 3.4 Phase 3: 汇总报告

```text
处理后输出:

  Batch Report:
  +-- Total: 50 questions
  +-- Success: 48
  +-- Failed: 2
  +-- Total time: 8m 32s
  +-- Avg time/question: 10.2s
  +-- Generated files:
      +-- knowledge/01_survey/2026-07-31-nvidia-vera-rubin.md
      +-- knowledge/07_industry-research/03_server/2026-07-31-800V-vs-48V.md
      +-- ...
```

### 3.5 关键复用机制

```text
+-----------------------------------------------------+
|                  Agent 实例 (一次创建)                 |
|                                                      |
|  +--------------+  +--------------+                 |
|  |   model      |  |   tools[14]  |  <- 不变         |
|  |  (LLMModel)  |  |  read/write  |                 |
|  |              |  |  web_search  |                 |
|  |              |  |  web_fetch   |                 |
|  |              |  |  ...         |                 |
|  +--------------+  +--------------+                 |
|                                                      |
|  +--------------+  +--------------+                 |
|  |  skill_mgr   |  |  messages[]  |  <- 每轮清空      |
|  |  (3 skills)  |  |  [clear]     |                 |
|  +--------------+  +--------------+                 |
|                                                      |
|  +--------------------------------------+           |
|  |  system_prompt (不变)                 |           |
|  |  _get_current_time() (动态)           |           |
|  +--------------------------------------+           |
+-----------------------------------------------------+
```

**不变部分**（跨轮重用）：

- `model` — LLM bot driver，连接池复用
- `tools` — 14 个 tool 实例，cwd 固定
- `skill_manager` — 3 个已加载 skill
- `system_prompt` — 当前工作空间配置

**可变部分**（每轮重置）：

- `messages` — `agent.messages.clear()` 或 `clear_history=True`
- `messages_lock` — 自动
- `_last_run_new_messages` — 自动

---

## 4. 关键决策

### 4.1 输出路由策略

Agent 在执行任务时通过 `write` 工具和 `read` 工具操作文件。输出路由有三种模式：

| 模式 | 描述 | 优点 | 缺点 |
|:-----|:------|:-----|:-----|
| **A. Agent 自主写入** | Agent 自行调用 `write` 工具写入知识库 | ✅ 灵活 ✅ 与现有 skills 兼容 | ❌ 文件名/路径不可控 ❌ 依赖 Agent 遵循命名规范 |
| **B. 程序化捕获** | 不拦截 `write` 工具，让 Agent 自然输出，程序在外部捕获最终响应后写入 | ✅ 路径可控 | ❌ 与 Agent 内部 tool 链冲突（Agent 可能已写入） |
| **C. 混合模式** | Agent 使用工具自行操作，但输出格式化为 JSON/text，CLI 自动归档 | ✅ 两者兼顾 | ⚠️ 实现复杂度中等 |

**推荐: 模式 A（Agent 自主写入）**，理由：

- 现有 skills（`knowledge-wiki`、`knowledge-doc-writer` 等）已经内建了知识库写入逻辑
- Agent 的 `write` 工具可以写入任何路径，只需在 prompt 中约束"写入 knowledge/ 目录"
- 程序只需捕获 Agent 返回的响应文本以确认写入路径

### 4.2 上下文隔离策略

| 策略 | 实现 | 优点 | 缺点 |
|:-----|:------|:-----|:-----|
| `clear_history=True` | 每次 `run_stream` 传参 | ✅ 简单 ✅ Agent 内部路径 | ❌ 无法清除已注入的系统提示 |
| `agent.messages.clear()` | 在两次调用之间手动清除 | ✅ 彻底清空 ✅ 无歧义 | ❌ 需注意锁 |
| 新建 Agent | 每轮 `agent = Agent(...)` | ✅ 彻底隔离 | ❌ 重复 init 开销 |
| 深拷贝 Agent | `copy.deepcopy(agent)` | ✅ 隔离 ✅ 快 | ❌ model/tools 可能不可拷贝 |

**推荐: `agent.messages.clear()` + `clear_history=True` 双保险**

### 4.3 错误处理策略

| 异常类型 | 处理方式 | 影响 |
|:---------|:---------|:-----|
| LLM API 超时 | 重试 1 次，仍失败则跳过 | 仅影响当前问题 |
| Tool 执行错误 | Agent 内部自愈机制 | Agent 自行处理 |
| 文件写入冲突 | 追加时间戳后缀 | 仅影响当前文件 |
| 进程被中断 | SIGINT 清理当前轮 → 退出 | 已处理结果不丢 |

### 4.4 进度与成本

| 需求 | 实现方式 |
|:-----|:---------|
| 进度显示 | `[3/50] 正在处理: 调研 NVIDIA Vera Rubin...` |
| 实时输出 | 流式显示 Agent 的 tool call 和最终结论 |
| Token 预算 | 每轮 `max_steps=20`，`max_context_tokens=50000` |
| 成本预估 | 批处理前先 dry-run 1 个问题估算 |
| 暂停/恢复 | 任务文件 + `--resume-from` 跳过已处理行 |

---

## 5. 实现计划

### 5.1 文件结构

```text
cli/
+-- cli.py                    # + batch 子命令入口
+-- commands/
    +-- chat.py               # 现有（不变）
    +-- batch.py              # 新增：批量处理
```

### 5.2 `batch.py` 核心接口

```python
# cow batch --file questions.txt --output knowledge/
# cow batch --file questions.txt --resume-from 10 --max-questions 50
# cow batch --dry-run --file questions.txt

@click.command(name="batch")
@click.option("--file", "-f", required=True, help="问题文件（每行一个）")
@click.option("--output", "-o", default="knowledge/", help="输出根目录")
@click.option("--max-questions", "-n", default=0, help="最大处理数（0=全部）")
@click.option("--resume-from", "-r", default=0, help="从第几行开始")
@click.option("--dry-run", is_flag=True, help="仅显示问题列表，不执行")
@click.option("--concurrent", "-c", default=1, help="并发数（实验性）")
def batch(file, output, max_questions, resume_from, dry_run, concurrent):
    ...
```

### 5.3 核心逻辑

```python
def _run_batch(file_path: str, output_root: str, ...):
    # -- Phase 1: Init (one-time) --
    load_config()
    agent = _create_full_agent()    # 带 tools + skills

    # -- Phase 2: Pre-flight --
    questions = _read_questions(file_path)
    click.echo(f"共 {len(questions)} 个问题，从 #{resume_from} 开始")

    # -- Phase 3: Loop --
    results = []
    for i, q in enumerate(questions[resume_from:], start=resume_from):
        click.echo(f"[{i+1}/{len(questions)}] {q[:60]}...")

        # Clean context
        with agent.messages_lock:
            agent.messages.clear()

        # Execute
        try:
            response = agent.run_stream(
                user_message=q,
                on_event=_make_progress_handler(),
                clear_history=True,
            )
            results.append({"ok": True, "question": q, "response": response})
        except Exception as e:
            results.append({"ok": False, "question": q, "error": str(e)})

        # Rate limiting (optional)
        time.sleep(1)  # 避免 API 限流

    # -- Phase 4: Report --
    _print_report(results)
```

### 5.4 完整 Agent 创建（带 tools + skills）

此函数是 **`_create_minimal_agent()` 的扩展版**，添加了 tools 和 skills 加载：

```python
def _create_full_agent():
    """Create Agent with full tools + skills (one-time cost ~0.8s)."""
    from bridge.bridge import Bridge
    from bridge.agent_bridge import AgentLLMModel
    from agent.protocol import Agent
    from agent.prompt import PromptBuilder, load_context_files
    from agent.tools import ToolManager
    from agent.skills.manager import SkillManager
    from config import conf
    from common.utils import expand_path

    workspace_root = expand_path(conf().get("agent_workspace", "~/cow"))

    # Bridge + Model
    bridge = Bridge()
    model = AgentLLMModel(bridge)

    # Tools (14 tools, ~0.26s)
    tm = ToolManager()
    tm.load_tools()
    tools = []
    for name in tm.tool_classes:
        tool = tm.create_tool(name)
        if tool:
            tool.cwd = workspace_root
            tools.append(tool)

    # Skills (3 skills, ~0.28s)
    skill_manager = SkillManager()

    # Prompt
    context_files = load_context_files(workspace_root)
    prompt_builder = PromptBuilder(workspace_dir=workspace_root, language="zh")
    system_prompt = prompt_builder.build(
        tools=tools,
        context_files=context_files,
        skill_manager=skill_manager,
        memory_manager=None,
        runtime_info={},
    )

    # Agent
    agent = Agent(
        system_prompt=system_prompt,
        model=model,
        tools=tools,
        max_steps=conf().get("agent_max_steps", 20),
        output_mode="logger",
        workspace_dir=workspace_root,
        skill_manager=skill_manager,
        enable_skills=True,
        max_context_tokens=conf().get("agent_max_context_tokens", 50000),
    )
    return agent
```

### 5.5 与 `chat.py` 的代码复用

| 组件 | chat.py | batch.py | 复用方式 |
|:-----|:--------|:---------|:---------|
| 路径修复 | `_ensure_cowagent_path()` | 同 | 函数复用 |
| 样式 | `_get_style()` | 同 | 函数复用 |
| 配置加载 | `_load_config_if_needed()` | 同 | 函数复用 |
| 日志静音 | `_silence_console_logging()` | 同 | 函数复用 |
| 终端恢复 | `_restore_terminal()` | 同 | 函数复用 |
| **Agent 创建** | `_create_minimal_agent()`（无工具） | `_create_full_agent()`（有工具） | **各自独立** |
| **Agent 调用** | `_call_agent_direct()`（有渲染器） | `agent.run_stream()`（无渲染器） | **batch 简化版** |

### 5.6 `_call_agent_direct` vs `_call_batch_turn`

```python
# chat.py 版本（有流式渲染器）
def _call_agent_direct(agent, query, renderer, clear_history=False):
    cancel_ev = threading.Event()
    _cancel_event = cancel_ev
    try:
        response = agent.run_stream(
            user_message=query,
            on_event=renderer.handle_event,
            clear_history=clear_history,
            cancel_event=cancel_ev,
        )
    finally:
        _cancel_event = None
        renderer.finish()
    return response

# batch.py 版本（无渲染器，纯捕获）
def _call_batch_turn(agent, query):
    # 简洁版本 - 直接捕获文本输出
    response = agent.run_stream(
        user_message=query,
        clear_history=True,
        # 不传 on_event → 无实时渲染（更快）
        # 不传 cancel_event → 不支持中途取消（batch 场景允许）
    )
    return response

# batch.py 版本（有进度指示器）
def _call_batch_turn_with_progress(agent, query, turn_no, total):
    events = []  # 捕获事件用于后续分析
    def on_event(event):
        events.append(event)
        if event.get("type") == "tool_execution_start":
            name = event.get("data", {}).get("tool_name", "?")
            click.echo(f"  🔧 调用工具: {name}")
    response = agent.run_stream(
        user_message=query,
        on_event=on_event,
        clear_history=True,
    )
    return response, events
```

---

## 6. 风险与缓解

### 6.1 Token 成本失控

| 风险 | 影响 | 缓解 |
|:-----|:-----|:------|
| 单问题使用过多 token | 单条成本过高 | `max_steps=20` 硬限制 |
| Agent 进入死循环 | 无限 token 消耗 | `max_steps` 触发后强制返回 |
| 上下文积累（忘记 clear） | 后续问题上下文暴涨 | `agent.messages.clear()` + `clear_history=True` 双保险 |
| LLM API 调用失败 | 跳过当前问题 | try/except 捕获 + 记录失败原因 |

### 6.2 导入路径与 sys.path

`batch` 作为 CLI 子命令，与 `chat` 共享同样的 pip 安装入口问题。必须在函数体内 lazy import 所有 CowAgent 模块，并在入口处调用 `_ensure_cowagent_path()`。

### 6.3 Skills 目录变更

如果用户在工作目录 `~/cow/skills/` 中新增或修改了 skill，当前进程的 `SkillManager` 不会感知。缓解措施：

- 在 Phase 1 一次性加载，batch 处理期间不重载
- 如果 batch 处理耗时长，可在每 10 个问题后检查 `mtime`

### 6.4 并发处理（实验性）

`--concurrent N` 允许多个问题并行处理。风险：

- Agent 实例不是线程安全的（`messages_lock` 存在但 model/tools 可能有问题）
- 并发调用 LLM API 可能触发限流
- **建议**: 初期不实现并发，先做好串行处理

### 6.5 进程中断与恢复

| 场景 | 后果 | 处理 |
|:-----|:-----|:------|
| Ctrl+C 在 Agent 执行中 | 当前轮被 cancel | 损失当前问题结果 |
| Ctrl+C 在轮次之间 | 进程干净退出 | 已处理结果已在 knowledge/ 中 |
| 系统崩溃 | 丢失进度 | 通过文件系统状态可恢复（已写入的文件不丢） |

**恢复机制**: `--resume-from N` 参数允许从第 N 行继续。

---

## 7. 性能预估

### 7.1 批处理成本模型

```text
T_total = T_init + N × (T_llm + T_overhead)

其中：
  T_init     = ~0.8s  (Bridge + Model + Tools + Skills)
  T_llm      = 5-30s  (LLM 推理时间，取决于问题复杂度)
  T_overhead = ~0.01s (messages.clear + loop overhead)
```

### 7.2 典型场景

| 场景 | N | T_llm/题 | T_init | T_total |
|:-----|:-:|:--------:|:------:|:-------:|
| 小批量调研 | 5 | 10s | 0.8s | **~51s** |
| 中批量归档 | 20 | 8s | 0.8s | **~160s** |
| 大批量知识构建 | 50 | 12s | 0.8s | **~600s (10min)** |
| 全量重建 | 200 | 15s | 0.8s | **~3000s (50min)** |

### 7.3 对比：per-process vs agent-reuse

```text
N=50, T_llm=10s:

per-process:  50 × (0.8 + 10) = 540s (9min)
agent-reuse:  0.8 + 50 × 10   = 501s (8min 21s)

节省: 39s (7.2% of total)
```

当 `T_llm` 占主导时（通常如此），init overhead 的节省占总时间比例不大。**真正价值不在节省 39s，而在于**：

1. 进程管理简单（一个进程处理所有问题）
2. 上下文可控制（不依赖文件系统持久化）
3. 错误处理统一（统一 try/except，统一 report）
4. 可扩展（支持 `--dry-run`、`--resume-from`、自定义 prompt）

---

## 8. 与 Web/Server 架构对比

```text
                    Web 模式 (app.py)          Batch CLI (cow batch)
                    -----------------         ---------------------
Agent 生命周期      AgentBridge.agents 缓存     单一 Agent 实例
                    跨 HTTP 请求维持              跨问题维持
初始化时机          app.py 启动时（~5s 全量）   Phase 1 一次性（~0.8s）

上下文管理           每轮追加                     每轮清空（独立问题）
                     SQLite 持久化                无持久化
                     跨轮上下文延续                独立问题

Cancel 机制          cancel_registry              threading.Event
                     per-request cancel           per-turn cancel

流式输出             SSE/WebSocket 推送           控制台流式

Skills              全量加载                      全量加载（同）
Tools                全量加载                      全量加载（同）

会话持久化           SQLite（ConversationStore）   无（文件系统由 Agent 工具管理）

适用场景             多用户、持续对话               单用户、批量处理
```

---

> **分析日期**: 2026-07-31 | **作者**: 小龙猫
>
> **核心结论**: 实现批量问题导入的核心架构是 **「一次性创建带 tools+skills 的全功能 Agent → 复用同一实例 N 次调用 run_stream()」**，每次只清除 `messages` 实现问题隔离。init 成本从 per-process 的 N×0.8s 降到 0.8s（N≥10 时可忽略），实现上只需新增 `cli/commands/batch.py` 约 100 行代码，复用 chat.py 的 `_ensure_cowagent_path()` / `_load_config_if_needed()` 等基础设施。
