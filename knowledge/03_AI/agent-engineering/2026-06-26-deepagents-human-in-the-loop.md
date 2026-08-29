# DeepAgents - Human in the Loop 人机协作实战

> **概要**: DeepAgents 的 HumanInTheLoop 中断与恢复机制和企业级人机协作实战 [来源: 1]
>
> **关键词**: DeepAgents · 人机协作 · 中断恢复 · Checkpoint · 审批

---

## 📑 目录

- [核心思想](#核心思想)
- [核心概念](#核心概念)
- [执行生命周期](#执行生命周期)
- [配置中断](#配置中断)
- [关键技巧：分辨"新消息" vs "中断恢复"](#关键技巧分辨新消息-vs-中断恢复)
- [invoke vs stream 模式](#invoke-vs-stream-模式)
- [进阶：when 谓词](#进阶when-谓词)
- [集成要点](#集成要点)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 核心思想

在企业级 Agent 应用中，**AI 在执行关键工具时必须经过人类审批**——避免误操作影响业务。DeepAgents 内置的 `HumanInTheLoopMiddleware` 将中断逻辑全部自动化：

- 只需配置一个 `interrupt_on` 字典
- 执行前自动暂停图执行，保存状态到 checkpointer
- 等待人类决策后通过 `Command(resume=)` 恢复

---

## 核心概念

| 概念 | 说明 |
|:-----|:------|
| **interrupt（中断）** | Agent 准备调用被监控的 tool 时，调用 LangGraph 的 `interrupt()` 暂停图执行，抛出包含 `action_requests` 和 `review_configs` 的请求 |
| **checkpoint（检查点）** | 中断时图状态被持久化（必须配置，否则中断后无法恢复）。生产用 `AsyncPostgresSaver`，测试用 `InMemorySaver` |
| **version="v2"** | LangGraph 1.0 v2 模式，`ainvoke()` 返回 `GraphOutput` 对象（含 `.interrupts` 属性），`astream()` 的 updates 流中出现 `__interrupt__` 事件 |
| **Command(resume=)** | 用户决策后，用 `Command(resume={"decisions": [...]})` 从断点恢复执行 |
| **Decision（决策）** | 四种类型：`approve`（批准）、`reject`（拒绝并反馈）、`edit`（修改参数后执行）、`respond`（人类直接回答，跳过 tool 执行） |

---

## 执行生命周期

```text
用户提问 -> Agent 调用 LLM 生成回复
-> LLM 决定调用 tool（如 execute_shell_command）
-> after_model 钩子：检查 tool 是否在 interrupt_on 中
-> 是：构建 HITLRequest -> interrupt() -> 暂停 ⌛
-> 否：继续执行
-> 人类做出决策（approve/reject/edit/respond）
-> 恢复执行 -> 执行/拒绝 tool -> LLM 生成最终回复 -> 返回
```

---

## 配置中断

```python
agent = create_deep_agent(
    model=llm,
    tools=[execute_shell_command],
    checkpointer=checkpointer,          # 必须！
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "execute_shell_command": {
                    "allowed_decisions": ["approve", "reject"]
                }
            }
        ),
    ],
)
```

**interrupt_on 配置项**（value）：

- `True` — 允许所有四种决策（approve / edit / reject / respond）
- `False` — 不拦截该 tool
- `{"allowed_decisions": [...]}` — 只允许指定决策类型
- 还支持 `when` 谓词（按参数条件判断是否拦截）、`description` 自定义提示文本

---

## 关键技巧：分辨"新消息" vs "中断恢复"

**核心判断**：通过 `state.next` 检查是否有待处理的中断

```python
state = await agent.aget_state(config)
if state.next:
    # 有待处理中断 → 本次消息是审批回复
    cmd = Command(resume={"decisions": [{"type": "approve"}]})
    await agent.ainvoke(cmd, config=config, version="v2")
else:
    # 无中断 → 正常对话
    resp = await agent.ainvoke(
        {"messages": [HumanMessage(content=query)]},
        config=config, version="v2"
    )
```

**`state.next` 不为空** → 图执行被暂停了（有中断等待处理）

---

## invoke vs stream 模式

| 模式 | 检测中断方式 | 恢复方式 |
|:-----|:-----------|:---------|
| **ainvoke** | `resp.interrupts` 属性（GraphOutput 对象） | 同 — 先检查 `state.next` |
| **astream** | `updates` 流中的 `__interrupt__` 事件 | 调用前先检查 `state.next` |

两种模式的核心逻辑一致，**推荐 stream 模式**（可同时输出 token 和中断提示）。

---

## 进阶：when 谓词

只拦截危险命令，普通命令自动放行：

```python
def is_dangerous_command(request: ToolCallRequest) -> bool:
    command = request.tool_call["args"].get("command", "")
    dangerous = {"rm ", "dd ", "mkfs", "shutdown", "reboot"}
    return any(d in command for d in dangerous)

HumanInTheLoopMiddleware(
    interrupt_on={
        "execute_shell_command": {
            "allowed_decisions": ["approve", "reject"],
            "when": is_dangerous_command,
        }
    }
)
```

**when 谓词**：返回 `True` 触发中断，返回 `False` 自动批准。（需 langchain >= 1.3.3）

---

## 集成要点

1. **创建 Agent 时**：配置 `interrupt_on` + 确保有 `checkpointer`
2. **每次调用前**：通过 `state.next` 判断是正常对话还是中断恢复
3. **恢复时**：用 `Command(resume={"decisions": [...]})` 传入用户决策
4. **封装到 AIAgent 类**：中断检测和恢复逻辑全部内部化，应用层（如 Chainlit）只需流式输出

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- (无)

### 外部资料引用

1. 来源: 花酒锄作田（博客园）
- 来源: 2026-06-14

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
