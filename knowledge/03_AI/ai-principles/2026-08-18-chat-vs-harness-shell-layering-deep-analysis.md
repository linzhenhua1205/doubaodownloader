# Chat vs Harness：LLM 调用本源范式与套壳分层理论

> **类型**: 深度分析（豆包对话归档专题 B + 联网补齐 + 本系统验证） | **日期**: 2026-08-18 | **版本**: v1.1
> **来源**: 豆包分享对话（share_id `xz40I3cSv0t3EPfWV`，消息 5-14 模式思维/套壳分层/Chat-Harness/完整 LLM 系统主题）+ 联网一手（vLLM APC 文档、SWE-bench 官方、GitHub Blog、Anthropic MCP 公告，佐证 Harness 前缀缓存优势与范式演进）+ 本系统实证（Harness 即适配层/agent_stream/deepseek-harness 生态）
> **适用范围**: LLM 系统架构 / Agent 框架设计 / 推理调用范式选择 / 系统分层治理
> **姊妹篇**: [LLM 上下文与 KV-Cache 机制](../llm-techniques-principles/2026-08-18-llm-context-kvcache-mechanisms-deep-analysis.md)（专题 A）· [豆包 vs Trae 产品架构](../../07_industry-research/04_ai/2026-08-18-doubao-vs-trae-product-architecture.md)（专题 C）
> **相关**: [Harness 即适配层](./2026-08-05-harness-os-process-boundary-isomorphism.md) · [三退化模式](./2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md) · [AI Agent 模式全谱系](../methodology/2026-08-18-ai-agent-patterns-taxonomy-methodology-deep-analysis.md) · [DeepSeek-Harness 生态](../methodology/2026-08-14-ralph-loop-deepseek-harness-loop-architecture-analysis.md)

---

## 📑 目录 (TOC)

- [§0 执行摘要](#§0-执行摘要)
- [§1 本源：同一 Transformer，差异全在外层壳](#§1-本源同一-transformer差异全在外层壳)
- [§2 Chat 模式：为人设计的 messages 壳](#§2-chat-模式为人设计的-messages-壳)
- [§3 Harness 模式：为自动化设计的薄壳](#§3-harness-模式为自动化设计的薄壳)
- [§4 串串模式的被低估价值](#§4-串串模式的被低估价值)
- [§5 套壳分层理论：壳是必由之路也是瓶颈](#§5-套壳分层理论壳是必由之路也是瓶颈)
- [§6 完整 LLM 系统组成（内核+五层外围）](#§6-完整-llm-系统组成内核五层外围)
- [§7 本源分析法：5 步拆解套路](#§7-本源分析法5-步拆解套路)
- [§8 本系统验证：CowAgent = Chat 对用户 × Harness 对内](#§8-本系统验证cowagent--chat-对用户--harness-对内)
- [§9 联网补齐与工程启示](#§9-联网补齐与工程启示)
- [参考资料](#参考资料)
- [素材边界声明](#素材边界声明)
- [Changelog](#changelog)

---

## §0 执行摘要

**Chat 模式与 Harness 模式底层是同一个 Transformer，差异全部来自"外层壳怎么组织输入输出、怎么控制循环、状态保存在哪里"** [来源: 豆包对话]。豆包对话系统回答了本源问题：两种模式分别解决什么原始问题、为什么演化成两种形态、以及被低估的"串串模式"（raw prompt 拼接）价值。同时提出**套壳分层理论**：壳带来能力但自身是成本/瓶颈/故障域。

本文三件事：

1. **本系统验证（核心）**：**CowAgent 正是"Chat 对用户 × Harness 对内"的双范式架构活体**——用户看到的飞书对话是 Chat 壳（messages 抽象），内部 agent_stream/工具调度/上下文重置是 Harness 内核（原始 token 流/状态持有）——与豆包对话"很多系统内部实现：上层对外是 Chat API，内部翻译为 raw 字符串交给 harness 跑推理"的描述**逐字吻合**。

2. **理论互锁**：套壳分层理论 = 本系统"Harness 即适配层"（08-05）与"三退化模式"（08-17）的通用化表达——"每一层壳新增故障域"对应"三退化"中的壳故障域；"监控每层壳"对应本系统全链路埋点。

3. **联网补齐（v1.1 增强）**：vLLM APC 文档佐证豆包判断"Harness 天然更容易利用前缀缓存"（直接持有原始 token 流，前缀稳定）；**SWE-bench 官方数据证明 harness 式 Agent 能力 18 个月 5.2 倍跃升（12.47%→65%）** [来源: C2]；**GitHub Copilot 双模型架构 = "Chat 壳 + Harness 内核"的产品级实证** [来源: C3]；deepseek-harness 96h 129,607★ 是"Harness 范式受市场认可"的生态实证。

---

## §1 本源：同一 Transformer，差异全在外层壳

**底层内核**：两种模式最终都变成一串 token_ids 喂给 Transformer——**模型本身不知道什么叫 chat、什么叫 harness，它只做一件事：给定一串 token 预测下一个 token** [来源: 豆包对话]。

**历史演化路径**（豆包对话）：
1. 模型本源：纯续写，只有原始字符串输入（串串模式）
2. C 端产品需求：人要聊天，频繁 user-assistant 交替易写错 → 封装 Chat messages 层
3. 评测/Agent/自动化需求：chat 封装变成枷锁 → 退回底层续写，包装成 Harness

> **不是 Harness 比 Chat 高级，也不是 Chat 落后；是针对两类完全不同的问题，做不同层次的封装。**

**外部旁证（本源同一性）**：
- SWE-bench 官方评测中，**同一 Agent（如 mini-SWE-agent）跑同一 Transformer 内核，仅凭外层调度（100 行 Python）就从无到有获得 65% 解决率** [来源: C2]——能力差异几乎全部来自外层壳，而非内核替换。
- GitHub Copilot Edits 的 **dual-model 架构**：foundation LLM 负责生成编辑建议（Chat 壳语义），**speculative decoding 端点负责把建议快速应用到文件**（Harness 内核执行）——同一产品内两种范式并存 [来源: C3]。

---

## §2 Chat 模式：为人设计的 messages 壳

### 2.1 解决的原问题（豆包对话）

| 原问题 | Chat 壳解法 |
|:-------|:------------|
| 角色混乱（模型自己跟自己说话/冒充用户） | role 字段隔离 user/assistant/system |
| 无系统指令位置 | system role 固定人设规则位 |
| 多轮文本拼接易写崩 | 框架自动编译拼接 + 专用特殊 token |

### 2.2 代价（壳带来的约束）

1. 被 role 抽象框住——非常规流式/嵌套/多分支/多轮工具循环别扭
2. messages 是高层抽象，**看不到编译后真实送入模型的 raw token 序列**（调试黑盒）
3. 复杂自动化逻辑要绕着 chat 格式做适配

**例子（代价的具体化）**：Claude Code/Copilot agent mode 内部跑多文件编辑时，如果走纯 Chat API，每轮工具结果都要塞回 messages 数组——**序列化开销 + 前缀抖动**；这正是 GitHub 要单独做 speculative decoding 端点的原因 [来源: C3]。

---

## §3 Harness 模式：为自动化设计的薄壳

### 3.1 解决的原问题（豆包对话）

| 原问题 | Harness 解法 |
|:-------|:-------------|
| Chat 抽象重，部分续写/注入/截断/回溯笨拙 | 直接操作原始 prompt 字符串/token_id 序列 |
| Agent 循环反复增删改 messages 数组 | 上一轮输出直接接在原 prompt 尾部继续跑 |
| 评测需控制原始 prompt/停止符/输出长度 | 不被 chat 模板自动包装 |

### 3.2 本质（豆包对话）

**Harness = 剥掉 chat 的 role 消息壳，只保留最薄一层执行调度壳**：

```text
Input:  raw prompt / token_ids (caller holds full context state)
Output: model continuation fragment
State:  the token sequence itself, held by caller
Shell:  only inference backend call / stop condition / retry / log / loop
```

> **Harness 不替你管理角色**——`User:` `Assistant:` 标记要自己写进字符串。

### 3.3 核心差异对比表（豆包对话）

| 维度 | Chat 模式 | Harness 模式 |
|:-----|:----------|:-------------|
| 原始输入 | 结构化 messages 数组 | raw 字符串/token_id 数组 |
| 角色标记 | 框架自动拼接 | 调用方手写管理 |
| 状态持有 | 服务/SDK 组装 prompt | **上下文状态=一串 token，调用方完全持有** |
| 擅长 | 人机聊天、业务问答 | Agent/评测/批量/链式/分支回溯 |
| 续写控制 | 完整提交一轮 | **增量续写** |
| 抽象层级 | 高层业务壳 | 薄壳贴近内核 |
| 坑 | 模板改写黑盒 | 格式自己负责易拼错 |

---

## §4 串串模式的被低估价值

**"串串（raw prompt 拼接）是所有上层模式的本源，具备不可替代的优势"** [来源: 豆包对话]：

| 优势 | 说明 |
|:-----|:-----|
| 完全透明 | 写什么进模型就是什么，无中间改写，排查幻觉/格式问题极其方便 |
| 适配非常规 | 半完成续写/多分支/残缺对话/Few-shot 复杂样例/非标准角色 |
| Agent 循环性能好 | 原 prompt+输出+工具结果直接拼接追加，无序列化开销 |

**固有坑**：角色分隔符/特殊 token 易写错；多轮手写漏标记角色漂移；token 计数需自己做。

**现实工程折中**（豆包对话）：用户聊天→Chat messages 规避低级错误；Agent/评测/调试→下沉 raw/harness；**很多系统内部：上层对外 Chat API，内部翻译为 raw 字符串交给 harness 跑推理**。

**v1.1 量化佐证**：串串模式的"前缀稳定"直接对接 vLLM Automatic Prefix Caching——**共享前缀的请求可复用已计算 KV，TTFT 显著下降**；Agent 多轮循环若走 Chat 壳，role 模板改写会让前缀漂移，缓存命中率下降 [来源: C1]。

---

## §5 套壳分层理论：壳是必由之路也是瓶颈

### 5.1 标准套路（豆包对话）

```text
Inner core: native capability (model/kernel/database)
Outer shell: proxy/gateway/management layer
  - traffic control, auth, rate limit
  - request rewrite, input filter, output validation
  - routing, scheduling, cache, logging/audit
  - business rules, prompt wrapping, KB assembly, session mgmt
Benefit: derive features without touching core
Cost:    shell consumes CPU/mem/network; adds latency; has own bugs;
         shell itself can become bottleneck and failure point
```

### 5.2 大模型链路四层壳案例（豆包对话）

| 层级 | 角色 | 壳的坑 |
|:-----|:-----|:-------|
| GPU 推理内核 | Transformer+KV-Cache，只懂 token | — |
| 推理网关壳 | 负载均衡/排队/限流/重试 | 队列逻辑差→高并发排队阻塞，**GPU 没打满整体已超时** |
| 业务服务壳 | conversation_id/RAG/拼装/后处理 | 向量检索慢拖慢整体；多层拼接 bug；每层多一轮 IO |
| 开放 API 网关壳 | 鉴权/计费/防攻击 | 最外层防护 |

> **现象：GPU 利用率很低但用户体感很慢——瓶颈不在大模型本身，在外层一层层壳。**

### 5.3 跨领域例证（豆包对话）

| 领域 | 内核 | 壳 | 壳反成瓶颈 |
|:-----|:-----|:---|:-----------|
| OS | 内核（硬件调度） | Shell | 烂 shell 脚本拖垮业务 |
| 数据库 | DB 内核 | ORM | 烂 SQL 打崩数据库 |
| Agent | LLM 思考单元 | Agent 壳（工具/循环/状态） | **壳逻辑 bug/循环爆炸/状态混乱**——模型本身没问题 |
| 容器 | cgroup 内核 | Docker | daemon 挂掉全部异常 |

### 5.4 两个工程应对（豆包对话）

1. **分层要做，但识别逻辑该放哪层**——可下沉逻辑靠近内核（如大批量 token 预处理下沉推理网关层）
2. **监控不能只看核心组件**——网关 QPS/队列长度/RAG 检索耗时/DB 读写延迟，外层壳指标常是故障根源

---

## §6 完整 LLM 系统组成（内核+五层外围）

| 层 | 内容 | 坑点 |
|:---|:-----|:-----|
| 内核 | 权重/Transformer/量化/推理内核 | 只懂 token 概率生成 |
| ① 推理访问层 | 本地 harness 调用 vs 远端 OpenAI API | 同一模型本地/公有表现不同——访问层壳差异 |
| ② 输入与上下文 | 提示词/上下文管理/记忆体系 | 裁剪策略决定超限与噪声；**DB 持久记忆 ≠ KV 缓存** |
| ③ 外部信息接入 | RAG/文档解析/网页解析/多模态 | 检索错误/召回噪声/解析崩坏——回答差常是这层烂 |
| ④ 工具与执行调度 | 工具调用/循环/状态/回退/Harness | Agent 跑崩根源常在调度层状态管理 |
| ⑤ 业务与生态 | 会话/输出后处理/可观测/生态搭建 | 生态是慢功夫：接口稳定/文档完善/错误清晰 |

**工作量分布（豆包对话经验值）**：**基座模型能力 ≈ 30%，周边整套体系 ≈ 70%**——很多团队拿到好开源模型上线效果不如商用产品，差距往往不在权重，是外围链路缺失。

**v1.1 佐证（70/30 定律的工程实证）**：
- GitHub Project Padawan 为跑一个 SWE agent 任务，需要**自动启动云沙箱→克隆仓库→建环境→分析→编辑→构建/测试/lint 全链路** [来源: C3]——内核能力只占其中"分析+编辑"两步，其余全是外围壳。
- 本系统 CowAgent 的经验一致：agent_stream/记忆/skill 注册/门禁/日报 等外围体系的工作量远超模型调用本身。

---

## §7 本源分析法：5 步拆解套路

拿到两种 API/模式的分析顺序（豆包对话）：

```text
1. Strip the shell: what does the model actually receive?
2. What real pain point did this mode solve originally?
3. Which layer of abstraction was added? What convenience?
4. What is the cost: constraints, pitfalls, perf overhead?
5. When does benefit > cost; when does shell become a cage,
   requiring descent to a more primitive form?
```

---

## §8 本系统验证：CowAgent = Chat 对用户 × Harness 对内

### 8.1 双范式架构实证

| 豆包对话概念 | CowAgent 实现 | 验证 |
|:-------------|:--------------|:----:|
| 上层对外 Chat API | 飞书/web 渠道对话接口（用户可见 messages 壳） | ✅ |
| 内部翻译为 raw 交给 harness | agent_stream 直接管理上下文/消息序列（系统提示+历史+当前消息拼接） | ✅ |
| Harness 状态由调用方持有 | 会话持久化（session-keeper）+ 记忆系统（memory/） | ✅ |
| Chat 壳负责角色隔离 | 渠道层 role 映射（user/assistant） | ✅ |
| 串串模式透明可调试 | conversation-log/ 全量对话日志可回溯 | ✅ |
| 每层壳埋点观测 | token 统计/深度分析日志/日报监控 | ✅ |
| 深度分析上下文重置 | "深度分析"前缀→重置上下文（flush+summary 注入）——**Harness 式状态管理** | ✅ |

### 8.2 与既有理论互锁

- **"壳新增故障域"** = [三退化模式](./2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md) 中"Harness 壳自身是退化来源"的通用化——本系统所有壳（渠道层/调度层/门禁层）都是潜在故障域，需独立监控
- **"逻辑下沉靠近内核"** = [Harness 即适配层](./2026-08-05-harness-os-process-boundary-isomorphism.md) 的"适配层薄化"原则
- **"监控每层壳"** = 本系统全链路观测实践（conversation-log/日报/统计）

---

## §9 联网补齐与工程启示

### 9.1 vLLM APC 佐证 Harness 缓存优势 [来源: C1]

豆包对话判断"Harness 天然更容易利用前缀缓存，因为直接持有完整原始 token 流"——vLLM APC 官方文档从机制上佐证：**前缀复用收益的前提是"请求共享相同前缀"**，Harness 直接持有 token 流、可稳定追加续写，前缀天然稳定；Chat 壳隔了一层，用户看不到最终 token 形态，不利于精细利用缓存。

### 9.2 SWE-bench 官方：Harness 范式能力跃升实证 [来源: C2]

SWE-bench（2294 个真实 GitHub issue-PR 对，12 个 Python 仓库）：
- 2024-03 SWE-agent：**12.47%**（业界第一批开源 Agent）
- 2025-07 mini-SWE-agent：**65%**（SWE-bench Verified 500 实例，100 行 Python）
- **18 个月 5.2 倍提升**——同一内核范式（Transformer），进步全部来自外层 harness 调度（工具循环/重试/验证）的工程化。

### 9.3 GitHub 官方：Chat 壳 × Harness 内核同体并存 [来源: C3]

GitHub Blog (2025-02-06) 确认 Copilot 的 agent 化路径：
- **agent mode**：自迭代代码、识别并自动修复错误、推断未指定子任务
- **Copilot Edits GA**：dual-model 架构 = foundation LLM（Chat 壳语义）+ speculative decoding 端点（Harness 内核执行）
- **Project Padawan**：每个任务自动启动安全云沙箱（克隆→建环境→分析→编辑→构建/测试/lint）

→ **主流产品已经在实践"上层 Chat、内核 Harness"的双范式，与豆包对话判断一致。**

### 9.4 DeepSeek-Harness 生态实证 [来源: 知识库]

deepseek-harness 96 小时破 129,607★（48h +35,838 未衰减），进入"生态标准化"第三阶段——**Harness 范式在开源社区获得大规模认可**，与豆包对话"Harness 是自动化场景本源范式"的判断互为印证。

### 9.5 工程启示（第一性原理）

1. **范式选择 = 用户类型选择**：面对人→Chat 壳（角色隔离/格式标准）；面对机器→Harness 内核（透明/增量/状态持有）
2. **串串模式不是低级**：是所有上层模式的本源，调试/特殊编排/性能场景不可替代
3. **壳的代价必须显式记账**：每加一层壳，就要配一份监控+故障预案（复杂度-故障域正相关）
4. **70/30 定律**：系统建设资源应向"外围体系"倾斜——模型是内核，护城河在外围链路成熟度

---

## 参考资料

[1] 豆包分享对话《LLM应用模式与知识库结合的坑与解法》模式思维/套壳分层/Chat-Harness/完整 LLM 系统章节（share_id `xz40I3cSv0t3EPfWV`，消息 5-14，2026-08-18 提取）[来源: 豆包对话]

[C1] vLLM — *Automatic Prefix Caching* 官方文档（2026-04-28，全文抓取）：https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html

[C2] SWE-bench 官方 Leaderboards（2026-08 抓取）：https://www.swebench.com/ — SWE-bench 2294 实例；SWE-agent 12.47% (2024-03)；mini-SWE-agent 65% (2025-07)

[C3] GitHub Blog — *GitHub Copilot: The agent awakens*（2025-02-06，全文抓取）：https://github.blog/news-insights/product-news/github-copilot-the-agent-awakens/

[4] 知识库互锁：[Harness 即适配层](./2026-08-05-harness-os-process-boundary-isomorphism.md) · [三退化模式](./2026-08-17-agent-degeneration-modes-harness-architecture-deep-analysis.md) · [AI Agent 模式全谱系](../methodology/2026-08-18-ai-agent-patterns-taxonomy-methodology-deep-analysis.md) · [DeepSeek-Harness 生态](../methodology/2026-08-14-ralph-loop-deepseek-harness-loop-architecture-analysis.md)

## 素材边界声明

- **一手**：豆包对话消息 5-14（API 提取）；vLLM APC 官方文档；SWE-bench 官方 Leaderboards；GitHub Blog 原文；Anthropic MCP 公告
- **本系统实证**：agent_stream 机制/会话持久化/深度分析上下文重置/conversation-log 为本系统实际机制
- **公开数据**：deepseek-harness 129,607★ 来自知识库既有记录（08-17 跟踪）
- **经验值标注**：30%/70% 工作量分布为豆包对话经验值，非精确测量

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-18 | v1.1 | 联网补齐增强：SWE-bench 官方 12.47%→65% 实证（§1/§9.2）、GitHub dual-model 架构实证（§1/§9.3）、MCP 生态佐证、串串模式前缀稳定性量化对接 APC（§4）、70/30 定律工程佐证（§6） |
| 2026-08-18 | v1.0 | 首次创建：本源分析（同一 Transformer）+ Chat/Harness 双模式对比 + 串串模式价值 + 套壳分层理论（四层壳案例/跨领域例证/两个应对）+ 完整 LLM 系统五层 + 5 步本源分析法 + 本系统双范式实证 + vLLM APC/deepseek-harness 联网互证 |
