# 🎣 DeepSeek Harness（dsh）：一切皆插件的 Agent 运行时深度分析

> **事件**: deepseek-ai/deepseek-harness 开源（08-13 爆发登顶 GitHub 新仓库第一）
> **类型**: Agent 工程 · Agent 运行时/Harness · 插件化架构 · 开源框架
> **关键词**: DeepSeek Harness, Cordis, 时空可组合性, 一切皆插件, append-only 会话日志, Agent Preset, 沙箱
> **一手核验**: GitHub repo（README + 架构文档 + Cordis primer + agent-presets + sandbox-local + providers 全文精读）+ Cordis 论文（北大×DeepSeek，2026-08-13 草稿）——共抓取 8 份一手文档

---

## 📑 目录

- [1. 核心结论](#1-核心结论)
- [2. 事件定位与一手核验](#2-事件定位与一手核验)
- [3. 第一性原理：为什么"一切皆插件"是 Agent 运行时的正确架构](#3-第一性原理为什么一切皆插件是-agent-运行时的正确架构)
- [4. 理论底座：Cordis 时空可组合性编程范式](#4-理论底座cordis-时空可组合性编程范式)
- [5. 技术框架：三层组成（Host Profile / Bundle / Agent Preset）](#5-技术框架三层组成host-profile--bundle--agent-preset)
- [6. 核心机制：append-only 会话日志（杀手级设计）](#6-核心机制append-only-会话日志杀手级设计)
- [7. 事件系统与 Turn 流程](#7-事件系统与-turn-流程)
- [8. 四预设详解](#8-四预设详解)
- [9. 安全模型：三级沙箱 + 审批 + 凭证](#9-安全模型三级沙箱--审批--凭证)
- [10. Provider 矩阵与委派机制（不绑定自家模型）](#10-provider-矩阵与委派机制不绑定自家模型)
- [11. 竞品语境分析](#11-竞品语境分析)
- [12. 与既有知识体系的呼应](#12-与既有知识体系的呼应)
- [13. 参考资料与诚实边界](#13-参考资料与诚实边界)

---

## 1. 核心结论

**一句话**: DeepSeek 开源的不是又一个 agent 框架，而是把**"一切皆插件"从口号变成可证明的运行时架构**——用 Cordis 的时空可组合性理论（可逆效应 + 反应式余效应）做底座，让模型适配器/工具注册表/会话日志/agent 循环**全部可替换且无特权核心**，并用 append-only 事件日志统一了 resume/fork/replay/telemetry。

**五大结论**:

1. **理论驱动而非工程堆叠**: dsh 的底层是北大×DeepSeek 的论文《A Programming Paradigm for Spatiotemporal Composability》——把"组件可动态组合"形式化为 **temporal composability（时间可组合性：完全撤销副作用）** 与 **spatial composability（空间可组合性：声明并响应式管理依赖）** 两个正交维度，lift 到运行时机制（revertible effects + reactive coeffects）。这是罕见"先有理论后造产品"的 agent 工程
2. **无特权核心是架构声明而非营销**: 模型适配器、工具注册表、会话日志、agent 循环本身**全是插件**；注册是"可逆效应"（reversible effects），插件卸载时自动 unwind——扩展 dsh 不需要 patch 核心，只需在旁边挂一个插件
3. **杀手级设计 = append-only 会话日志**: "Model-visible means logged"（模型可见即已记录）是运行时不变量——所有到达模型请求的输入**必须能从日志重建**。resume/fork/replay/telemetry/persistence **全部从单一事件流派生**，这从根上解决了 agent 系统的可追溯性/可恢复性问题
4. **不绑定自家模型是战略选择**: provider 含 Anthropic/OpenAI/Bedrock/Vertex/Azure/Gemini + 自定义 OpenAI-compatible 端点，且**可委派 Claude Code/Codex**（Codex 与 Claude Code providers 默认 dormant，由 Agent Preset 决定是否暴露委派工具）——Harness 走"模型中立"路线，与自家模型竞争由推理成本优势而非锁定取胜
5. **严格沙箱是工程底线**: Linux bwrap→Landlock、macOS Seatbelt、Windows ACL 三级 runner，**平台不可用即 fail closed（SANDBOX_UNAVAILABLE），绝不无约束静默执行**——agent 越权风险从架构层拦截

**规模事实**: 发布数小时 33K★（survey 08-14 记录 38.2K★）→ 本次抓取时 **46K★ / 3.6K forks / 12,293 commits**——commits 数量说明这是长期打磨后开源，非仓促发布；MIT 协议；developer preview 阶段（明确警告将有破坏性变更）。

---

## 2. 事件定位与一手核验

### 2.1 事件时间线

| 时间 | 事件 |
|:--|:--|
| 2026-07-28 前 | repo 创建（GitHub created 窗口起点） |
| 08-13 | 开源爆发，登顶 GitHub created>07-28 新仓库 ★ 榜第一 |
| 08-13 | 配套论文《A Programming Paradigm for Spatiotemporal Composability》Draft of August 13, 2026（cordiverse/paper）|
| 08-14 | 46K★（本次核验），survey 记录 38.2K★ |

### 2.2 一手核验清单（8 份文档）

| 文档 | 验证内容 |
|:--|:--|
| README.md / README.zh.md | 定位、运行方式（npx @deepseek-ai/dsh web → :3080）、MIT、dsh-plugin 话题 |
| docs/architecture.md | 插件树、Profile/Bundle、core packages、事件域、Turn flow、Session log、seams |
| docs/cordis-primer.md | Cordis 五思想、四 dispatch modes、waterfall 语义、loader |
| docs/user/guide/index.md + providers.md | Web UI、provider 配置、凭证存储 |
| packages/bundle/base/README.md | dsh-base 第一层、bash/pwsh 平台门控、Codex/Claude Code dormant |
| packages/preset/agent-presets/README.md | 四预设机制、standing mount、scope parent chain、copy-only authoring |
| packages/sandbox/sandbox-local/README.md | bwrap→Landlock/Seatbelt/ACL runner、fail closed、政策模型 |
| packages/mcp/README.md | MCP client 桥接（注册外部 server tools 到 ctx.tools）|

### 2.3 未核验项

- 未直接运行 dsh（无 Node 环境验证 Web UI 行为）
- 论文全文仅读摘要级信息（README 描述），未精读 PDF 证明细节
- 竞品对比（Qwen Code/Trae/Kimi CLI/ZCode）基于既有 survey 与记忆，非本轮一手

---

## 3. 第一性原理：为什么"一切皆插件"是 Agent 运行时的正确架构

### 3.1 经典 Agent 框架的架构债务

从第一性原理审视，传统 agent 框架（如早期 autogen/多 agent 编排）存在三类结构性债务：

| 债务 | 表现 | 后果 |
|:--|:--|:--|
| **特权核心** | agent 循环/上下文管理是框架内部实现，扩展需 fork 或 hook 私有 API | 升级冲突、生态碎片化 |
| **副作用不可逆** | 插件注册后无法干净卸载，热更新残留状态 | 长驻进程（agent 服务器）无法安全演进 |
| **状态不可重建** | 会话状态散落在内存/DB/文件，无单一事实源 | resume/fork/replay 脆弱，telemetry 需另建管道 |

### 3.2 为什么 agent 运行时比传统软件更需要可组合性

Agent 运行时的本质是**动态、长驻、可演进**的系统：

1. **动态组合**: 用户/agent 可能在运行时安装插件、切换工具集（dsh 的 recompose 机制）——不是编译期静态装配
2. **长驻进程**: Web UI + 服务器常驻，热更新/热卸载是常态而非例外
3. **可演进**: agent 自身就能改配置、加插件（self-evolving harness）——论文摘要明确提到 "self-evolving agent harnesses" 是动机之一

因此，**"插件能否干净卸载"（时间维度）与"插件依赖能否声明式解析"（空间维度）**成为 agent 框架的根基性问题——这正是 Cordis 论文的两个正交维度。

### 3.3 两个正交维度的定义（论文核心）

```
Composability = temporal x spatial (orthogonal)

[1] temporal composability
    = side effects of a component can be fully reverted upon removal
   -> runtime mechanism: revertible effects
      every context transformation carries an inverse the runtime tracks

[2] spatial composability
    = inter-component dependencies are declarable and reactively managed
   -> runtime mechanism: reactive coeffects
      every context change notifies a component per its coeffect spec

Unify: effect context and coeffect context merge into a single context type
-> constitutes a programming paradigm
-> compose into components + calculus of dynamic composition
-> metatheory lifts spatiotemporal composability from one component
   to a whole system of interleaved components
```

**工程落地**: Cordis 是这套理论的实现——核心库（effect tracking + coeffect resolution）+ 声明式组件加载器（配置调和 + 热模块替换 HMR）。

---

## 4. 理论底座：Cordis 时空可组合性编程范式

### 4.1 Cordis 五思想（primer 原文）

| # | 思想 | 内容 |
|:-:|:--|:--|
| 1 | **插件 = 实现 Service 的对象** | 函数（可选 inject/apply(ctx) 字段）或 Service 子类，生命周期由 Cordis 挂载到当前 context |
| 2 | **Context = Service 仓库** | 服务声明稳定的 `ctx.<key>`（如 ctx.tools/ctx.llm/ctx.sessions），其他插件按 key 查找而非 import 具体实现 |
| 3 | **inject 声明依赖** | 依赖服务不存在时插件等待——加载顺序由服务需求表达，而非手动 boot 排序 |
| 4 | **类型化事件通信** | 通过 TS declaration merging 声明事件名，以 emit/waterfall/parallel/serial 四种模式分发 |
| 5 | **注册 = 可逆效应** | prompt 段、工具 schema、适配器、provider、监听器都经 `ctx.effect()`/`ctx.on()` 安装，重载/卸载时按序 unwind |

### 4.2 四种分发模式（dispatch modes）

| 模式 | 等待? | 顺序 | 有返回值? | 语义 |
|:--|:--:|:--:|:--:|:--|
| `emit` | 否 | 注册序 | 否 | 观察（fire-and-forget）|
| `waterfall` | 否 | 注册序 | **是** | 包装/改写（around-middleware）|
| `parallel` | **是** | 并行 | 否 | 扇出 |
| `serial` | **是** | 注册序 | 是 | 按序决策 |

**waterfall 语义（关键）**: `ctx.waterfall` 是 around-middleware——监听器收到 `(...args, next)`，调用 `next()` 委托（可能被包装的）结果给下一服务；不调用 next() 即短路。单决策事件中，策略监听器可"拥有决策"（不 next()），注解/观察型监听器必须委托。

### 4.3 与知识库"AI 概率内核 × 工程确定性外壳"的呼应

Cordis 的可逆效应机制 = **工程确定性外壳的运行时实现**：插件卸载时副作用自动回退，保证"确定性外壳"本身可演进、可验证——这与本知识库 agent 协作协议（分层结论+依赖清单+置信度+验证路径）是同构的工程哲学。

---

## 5. 技术框架：三层组成（Host Profile / Bundle / Agent Preset）

### 5.1 整体分层

```
+---------------------------------------------------------+
|  Agent Plane (agent.cordis.yml - presets)               |
|  . tools/prompt sections/projection units, mounted once |
|  . scope parent chain: agent -> preset -> global        |
+---------------------------------------------------------+
|  Host Composition (base.cordis.yml + web.cordis.yml)    |
|  . registries/sandbox/approval/persistence/model route  |
|  . presets must not own (root-realm publish rejected)   |
+---------------------------------------------------------+
|  Cordis runtime (effect tracking + coeffect resolution) |
|  . declarative loader (config reconciliation + HMR)     |
+---------------------------------------------------------+
```

### 5.2 Profile 与 Bundle

| 概念 | 定义 |
|:--|:--|
| **Profile** | 命名组合（存于 Harness home）：列出堆叠的 bundles、持有 out-of-tree 插件、用户自己的 `cordis.patch.yml` |
| **Bundle** | Cordis 配置行 + 代码的分发格式；`dsh.profile` 列 bundles，`dsh.bundle` 指向 patch 文件 |
| **dsh-base** | 每个 profile 的第一层：model adapters / tools / persistence / sandbox / approval policy / settings / credentials / telemetry |
| **dsh-web-app** | 加浏览器应用（web 模板）|
| **dsh-headless** | 一次性 runner（无服务器，headless 模板）|

**分层覆盖规则**: 空条目列表上按序叠加——profile 列出的每个 bundle → profile 的 `cordis.patch.yml` → home 级 → 任何 `--patch` overlay。**patch 按行 id 替换整行 config（无 deep-merge）**——这是 dsh 的刻意设计：patch 语义简单可预测。

### 5.3 为什么两层（Host + Agent Plane）？

关键洞察来自架构文档：**"注册表/sandbox/审批/持久化/模型路由"是宿主资产，预设不得拥有**——因为服务若发布进 root realm 会进程全局化，第二个预设发布同名服务即冲突。预设内的服务必须放在 `isolate` realm（entry-local）内。这从架构上防止"预设污染全局"。

### 5.4 Core packages 一览

| Package | 拥有 | ctx key |
|:--|:--|:--|
| core/session | append-only SessionEvent 日志 + 内存 store | ctx.sessions |
| core/system-prompt | prompt 段 + 工具 schema 组装 | ctx.systemPrompt |
| core/tools | 作用域工具注册表 + 守卫执行流水线 | ctx.tools |
| core/agent | Agent 接口、live 注册表、agent/* 事件 | ctx.agents |
| core/agent-loop | 默认驱动（实现 Agent 接口）| ctx.agentLoop |
| core/scope | 每 agent 作用域注册原语 | 库（无 key）|
| llm/llm | 消息/流词汇 + 适配器缝 | ctx.llm |

---

## 6. 核心机制：append-only 会话日志（杀手级设计）

### 6.1 设计不变量

> **Model-visible means logged.**（模型可见即已记录）

架构文档原话: "Anything that reaches a model request must be reconstructable from the log, and a runtime invariant asserts it. This is why a new model-visible input requires a new session event."

**推论**: 新增任何"模型可见输入"类型 → 必须扩展 `SessionEventMap` + 从日志渲染——**架构强制可追溯性**，而非靠团队纪律。

### 6.2 单一事件流的派生能力

```
        append-only SessionEvent stream (durable facts)
                         |
        +--------+--------+--------+--------+
        v        v        v        v        v
   deriveMessages() fork()  resume() replay() telemetry
   (model history) (branch)(recover)(replay) (telemetry)
```

| 能力 | 机制 |
|:--|:--|
| **模型历史** | `deriveMessages()` 从日志投影；raw `assistant/chunk` 事件保留 UI 保真度 |
| **Fork** | `ctx.sessions.fork(source, boundary?, childSessionId?)` |
| **Resume** | 从日志重建会话上下文 |
| **Replay** | raw chunk 事件精确重放（含流式中间态）|
| **Telemetry** | 同源派生，无需另建管道 |

### 6.3 为什么这是杀手级

对比主流 agent 框架：会话状态通常存"渲染后的消息数组"（丢失中间工具流/流式 chunk/时序），resume 靠快照、replay 不可行、telemetry 另起炉灶。dsh 的**事件流即唯一事实源**意味着：

1. **审计完备**: 一切模型可见内容可重建 → 满足"可追溯→可审查→可审计"信任链（知识库 agent 产出信任链主线）
2. **恢复零成本**: 崩溃/重启后从日志重建，无快照一致性问题
3. **UI/编辑集成**: 任何 UI 只需读 `session/event` 渲染——`"Add UI or editor integration: drive ctx.agents and render from session/event"`
4. **模型切换安全**: 会话保留自身 log 中记录的模型（provider 删除时阻塞输入而非静默换模型）

---

## 7. 事件系统与 Turn 流程

### 7.1 事件三分域

| 域 | 事件 | 性质 | 用途 |
|:--|:--|:--|:--|
| **Session events** | turn/*, step/*, user/message, assistant/*, tool/* | **持久事实**，append 日志 + 广播 session/event | 必须 survive reload |
| **Agent events** | agent/*（inbox/step/status/request/validation/continuation）| live Agent | 观察/拦截在途工作 |
| **Capability events** | fs/*, tools/*, telemetry/* | 缝（seam）附加 | 不 import 循环即可附加策略/适配器 |

### 7.2 Turn 流程（step = 一次模型请求+调用的工具；turn = 零或多 step）

```
turn/start
  claim next-step input plus one queued message
  assemble prompt sections + tool schemas
  -> agent/pre-step (waterfall: rewrite/reject)
     step/start
     append entered messages as user/message
     derive model history from the log
     agent/request -> llm/stream -> assistant/chunk* -> assistant/message
     tool/call* -> tools/pre-execute -> tools/execute -> tools/post-execute -> tool/result*
     step/end
     tools owe another request, or next-step input arrived -> claim -> next step
  -> agent/turn-stopping (serial, no next())
turn/end
```

**关键设计**:
- 输入经**单一 inbox** 到达；部分消息立即唤醒，注入上下文在 inbox 等待直到下一条消息
- `agent/pre-step` 决定模型看到什么；**拒绝或空 claim 仍关闭一个未消耗 step 的持久 turn**——日志记录尝试本身
- waterfall 事件（agent/pre-step, agent/request, llm/stream, tools/*）必须调用 next() 委托

---

## 8. 四预设详解

### 8.1 预设机制（dsh-agent-presets）

- **Preset** = 含 `agent.cordis.yml` 的目录；roster 每进程**挂载一次**（standing mount），各会话经 scope parent chain 加入
- **Standing mount 的 KV 缓存效应**: 组合安装一次后运行期不再重读 → **prefix-stable for the life of an agent**（prompt 前缀稳定，利于 prefix caching）——这是 dsh 对推理成本优化的内置意识
- **recompose 仅限空白会话**: 切换已产出内容的会话会留下日志中已记录、新组合无法执行的工具调用——**产品规则源自日志不变量**（model-visible ⟺ logged）
- **authoring 是 copy-only**: 新预设 = 整目录复制现有预设（拒绝路径穿越 id、拒绝覆盖、拒绝未知源），复制后收紧为 owner-only 权限

### 8.2 四预设（shipped，apps/cli/config/agent-presets/）

| 预设 | 显示名 | 描述 | order |
|:--|:--|:--|:--:|
| **standard** | 标准模式 | 功能完整编码 Agent：文件编辑、Shell、文件与网页检索、Skills、计划、目标、子代理、工作流 | 1 |
| **code** | PTC 模式 | 标准全部能力 + **Code Mode SDK** 呈现工具（模型用 TypeScript 程序组合多步操作）| 2 |
| **minimal** | 极简模式 | 仅持久 bash + str_replace_editor 的**双工具**编码 Agent | 3 |
| **cordis** | **创造模式** | 标准全部能力 + 运行时检查、插件实验、**preset 创作指导**（用于创建自定义 Agent preset）| 4 |

**预设谱系洞察**: `cordis` 和 `code` 是 `standard` 的完整副本演化（文档明示 "cordis and code are full copies of standard"）——**预设 = 可读单文件的组合，继承=复制而非引用**，这保证了"整个装配可在一份文件中读懂"。

---

## 9. 安全模型：三级沙箱 + 审批 + 凭证

### 9.1 沙箱 runner 选择（dsh-sandbox-local）

| 平台 | 首选 | 备选 | 机制 |
|:--|:--|:--|:--|
| Linux | **bwrap**（Bubblewrap）| **Landlock** | Landlock 需 exit 125 + `landlock-run:` fatal line 识别；老 ABI 仅约束暴露的 access classes（partial）|
| macOS | **Seatbelt** | — | allow-default + `(deny file-write*)` + 写 allowlist（workspace root + /tmp + darwin temp）|
| Windows | **ACL restricted-token runner** | — | 确定性 write SID + 每会话随机私有 temp 目录（独立 SID + 可撤销 ACE）|

**铁律**: 平台不可用/runner 不可执行 → **fail closed（SANDBOX_UNAVAILABLE）**，绝不静默无约束执行。每次 wrap 报告 enforcement 完整度 + denial signatures + runner-failure 规则。

### 9.2 政策模型（每调用）

| 模式 | 授权 |
|:--|:--|
| `read-only` | 仅 /dev/null 字面量（Seatbelt）|
| `workspace-write` | workspace + 会话私有 temp 子目录（Windows: `<temp>\dsh-<hash>`，TMP/TEMP 为受限子进程重写）|

**bash/pwsh 平台门控**: base bundle 的 patch 用 `!!js process.platform` 表达式：bash-sandbox/tool-bash 在 win32 禁用，pwsh 双子反向——**同一 patch 文件、每主机恰好一个 shell 栈**；恢复 recipe 不完整会 load 时 loud fail。

### 9.3 审批与凭证

- **审批服务**: Web UI 在活动权限策略下对需审批操作先询问（approval service 随 host composition 运行，预设不可拥有）
- **凭证**: `$DSH_HOME/.credentials.yaml`，**write-only**（UI 收到 redacted descriptor，永不返回字面量密钥）；settings 仅保留 credential reference

---

## 10. Provider 矩阵与委派机制（不绑定自家模型）

### 10.1 Provider 清单

| Provider | 认证方式 | 备注 |
|:--|:--|:--|
| **DeepSeek** | API key | 默认卡 |
| **Anthropic / OpenAI** | API key | catalog 安装即供 endpoint/protocol/模型列表 |
| **Bedrock** | AWS credentials + region | 原生认证 |
| **Vertex** | ADC project | 原生认证 |
| **Azure** | api-version | 原生认证 |
| **Codex** | OAuth | 原生认证 |
| **自定义** | OpenAI-compatible | Provider ID 永久（requests/saved sessions/credentials 引用它）|

**Provider ID 永久性设计**: 请求、已存会话、模型默认值、凭证引用都用它——重命名 provider = 新增+删除，防止 ID 漂移破坏历史会话。

### 10.2 委派机制（Claude Code / Codex）

dsh-base README: **"Codex and Claude Code providers load dormant; Agent Presets independently decide whether their agent contributes either model-facing delegation tool."**

- 委派 provider **默认休眠**，由 Agent Preset 决定是否暴露"模型可见委派工具"
- 这是 **subagent providers 缝**（capability seam）的实例：同一接口后，从 fresh child agent 到**另一产品中的委托 turn**（Claude Code/Codex 域外执行）皆可变化
- 战略含义: **dsh 不替代 Claude Code/Codex，而是成为它们的编排层**——把"专业工具"当可插拔后端委派，规避生态对抗

### 10.3 MCP 生态

- `packages/mcp/mcp-client/`: **MCP client 桥接，把外部 server tools 注册到 ctx.tools**——工具 schema 自动进入 prompt 组装（"register on ctx.tools; its schema joins prompt assembly"）
- 与既有 MCP 主线（Agent Plugins 1.0.0 五巨头事实标准）呼应：dsh 以 **MCP client 而非 MCP server** 姿态接入生态

---

## 11. 竞品语境分析

### 11.1 开源 agent harness 竞争格局（2026-08）

| 竞品 | 定位 | 与 dsh 的差异 |
|:--|:--|:--|
| **Qwen Code** | 阿里编码 agent | 模型绑定强，插件化程度低 |
| **Trae** | 字节 AI IDE | IDE 形态 vs dsh 的 harness/服务器形态 |
| **Kimi CLI** | 月之暗面终端 agent | 终端 CLI 形态 |
| **ZCode** | 智谱编码 agent | 模型绑定强 |
| **Claude Code / Codex** | 闭源/半闭源专业编码 agent | **dsh 不直接竞争而是委派它们** |
| **yc-software/qm** | 多人 agent 工作台（13.4K★）| 协作形态差异 |
| **Cursor** | 闭源 IDE | 平台 vs 框架 |

### 11.2 dsh 的差异化定位

1. **架构深度**: 无其他开源 harness 有"时空可组合性"理论底座 + 可逆效应运行时——**可组合性不是特性而是架构公理**
2. **事件日志统一性**: append-only 会话日志把 resume/fork/replay/telemetry 全收敛到单一事件流——多数竞品仍是"快照式"会话
3. **模型中立 + 委派策略**: 不锁自家模型，反而委派 Claude Code/Codex——**"打不过就加入"的生态位策略**，把竞争转为共生
4. **暂不收外部 PR**: 社区入口是 Discussions/Discord/企微 + dsh-plugin 话题生态——**先立架构、再开生态**的保守节奏（与 46K★ 热度形成反差，说明 DeepSeek 有意控制演化质量）

### 11.3 风险

- **developer preview**: 明确警告 breaking changes——企业采用需锁定版本
- **无特权核心的另一面**: 全部可替换 → 用户配置错误面巨大，patch 无 deep-merge 易踩坑
- **竞品快速跟进风险**: "一切皆插件"架构理念可被模仿，dsh 的护城河是 Cordis 理论深度 + DeepSeek 品牌

---

## 12. 与既有知识体系的呼应

| 既有主线 | dsh 对应点 |
|:--|:--|
| Agent 编排六层（Prompt→Loop→工具面→Skills→编排→Channel）| dsh 的 Host/Agent Plane 分层 + seams 缝机制 |
| Agent 产出信任链（可追溯→可审查→可审计）| **Model-visible means logged** 不变量 + prove-without-exposing 思想 |
| NHE 非人类实体架构（identity/memory/audit）| dsh 的 append-only 日志 = audit 的工程实现路径；SessionEventMap 扩展点 = 审计事件注入点 |
| 上下文管理（context compaction 95% 水位）| standing mount prefix-stable（KV 缓存友好）+ deriveMessages 按需投影 |
| AI 概率内核 × 工程确定性外壳 | 可逆效应 = 确定性外壳的运行时实现 |
| Token 成本（合并 session>减请求>缩输出）| 事件流派生 session（无重复存储）+ prefix caching 意识 |
| Writer harness 降本实证（-40%）| **"harness 是跨组织所有模型倍增效率的组件"**——dsh 是该判断的开源验证 |
| 知识库 harness 架构（Bridge 枢纽 1204 行）| 本工作空间的 Bridge=协议适配解耦 ↔ dsh 的 seams=能力缝——同构工程哲学 |

---

## 13. 参考资料与诚实边界

### 13.1 一手来源

| # | 来源 | 类型 |
|:-:|:--|:--|
| 1 | [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | 官方 repo（README/架构/primer/presets/sandbox/providers/mcp）|
| 2 | [cordiverse/paper: A Programming Paradigm for Spatiotemporal Composability](https://github.com/cordiverse/paper) | 论文 repo（2026-08-13 draft，696★）|
| 3 | [STH/GitHub survey 08-14](https://github.com/deepseek-ai/deepseek-harness) | 本工作空间 survey 交叉验证（38.2K★ 记录）|

### 13.2 内部交叉链接

- [NHE 非人类实体架构七件套深度分析](2026-08-14-nhe-non-human-entity-architecture-seven-drafts-deep-analysis.md)
- [BMWG AI Fabric 基准三件套深度分析](../../05_tools/testing/2026-08-14-bmwg-ai-fabric-benchmarking-trilogy-deep-analysis.md)
- [AI 编排相关（Agent 编排主线）](../../03_AI/agent-engineering/)（目录索引）

### 13.3 诚实边界（缺陷与不确定性）

1. **未运行验证**: 未实际启动 dsh Web UI / 未执行插件编写——架构判断基于文档精读而非运行时观察
2. **论文未精读**: 时空可组合性的形式化证明（calculus 元理论）仅读 README 摘要级，未验证证明正确性
3. **竞品对比主观性**: Qwen Code/Trae/Kimi CLI/ZCode 对比基于既有 survey 与记忆，未逐一抓取一手——需注意时效（8 月快速迭代期）
4. **star 增长为快照**: 33K→38.2K→46K 是不同时间点快照（survey 08-14 早间 vs 本文抓取），非精确曲线
5. **"一切皆插件"的边界未验证**: 是否存在少量 host 层硬编码（如 app-boot 装配）未逐行审计——文档自述"no privileged core"，但 vendor/ 目录（vendored Cordis）本身即是隐含核心
6. **规模未见**: 未核验 12,293 commits 的时间分布与团队构成——"长期打磨"是推断

---

## Changelog

| 日期 | 变更 | 作者 |
|:--|:--|:--|
| 2026-08-14 | 初稿：GitHub repo + 8 份一手文档 + Cordis 论文摘要精读 | AI |
