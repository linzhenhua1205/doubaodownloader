# 🔍 Web 与飞书 Channel 响应慢定位报告

> **触发**: 用户反馈 web 与飞书 channel 响应慢，要求定位
> **归档**: 2026-08-10 | **模块**: 05_tools/devops/（故障诊断）
> **方法**: 事件墙法 + 分层隔离 + 量化实测（fault-diagnosis 方法论）
>
> **概要(v2 修正)**: 定位 web/飞书 channel"响应慢"。实测**消息到达→agent 开始处理无排队延迟（同秒）**；用户感知的 ~20 分钟 = **深度分析任务总执行时长**（步数 × 单 turn 耗时）。雪球核心=**用户 session 上下文跨任务累积不裁剪**（6→144 条，单 turn 9s→60s）+ enable_thinking 单次调用慢 + embedding 全量失败重试 64 次 + 1.8G 内存/92% 磁盘资源紧张。v1 误判"排队串行"为主因，实为任务执行本身慢。
>
> **关键词**: 响应慢、RCA、故障定位、agent推理链路、enable_thinking、embedding失效、内存不足、性能调优

## 📑 目录

- [摘要（TL;DR）](#摘要tldr)
- [一、响应链路与影响范围](#一响应链路与影响范围)
- [二、根因分析（按影响排序）](#二根因分析按影响排序)
- [三、因果链](#三因果链)
- [四、定位过程（关键步骤与数据）](#四定位过程关键步骤与数据)
- [五、修复建议（按优先级）](#五修复建议按优先级)
- [六、复盘](#六复盘)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 📑 摘要（TL;DR）

**核心结论（v2 修正）**：web 与飞书 channel"响应慢"的真相是——**没有排队/调度延迟，用户消息到达后 agent 立即开始处理（日志实测同秒）**；用户等待的 ~20 分钟是**深度分析任务本身的总执行时长**。

**执行时长公式**：`任务耗时 ≈ turns 数 × 单 turn 耗时`
- turns 数：深度分析任务动辄 20-40 turns（`agent_max_steps=40` 跑满）
- 单 turn 耗时：8s → 60s，**随 session 上下文跨任务累积线性恶化**

**雪球核心（v2 新发现）**：同一 session（用户对话）的 `agent.messages` **跨任务累积且不裁剪**（6→48→100→144 条，日志实证），`_trim_in_memory_to_turns` 只对 `scheduler_` 前缀 session 生效，用户 session 不裁剪 → 每个任务都比上一个更慢，单 turn 从 9s 涨到 60s，40 turns 的任务从 ~6 分钟恶化到 ~20 分钟。

**量化铁证**：
- 消息到达→Turn 1：19:06:13 / 19:11:26 / 19:19:13 / 19:23:42 **全部同秒**（无排队）
- 任务 1（21 turns）5.2min → 任务 2（27 turns）7.8min → 任务 3（14 turns）4.5min → 任务 A（40 turns 到顶）~13min → 任务 B（29 turns，继承 100 条上下文）~6min
- 单 turn 耗时：6 条消息 ≈9s → 72-76 条消息 51-58s → 100+ 条消息 40-52s（19:13-19:16 与 21:01-21:07 实测）
- 叠加：enable_thinking=True（每次请求带 reasoning）+ embedding 全量失败重试（本日 64 次 × 2171 文件）+ 1.8G 内存无 swap + 磁盘 92%

---

## 一、响应链路与影响范围

### 1.1 链路同一性（关键前提）

```
用户消息 → [web_channel / feishu_channel] → chat_channel.handle() → agent_stream（唯一推理引擎）→ 工具执行 → 流式返回
```

- web 和 feishu 只是**前端接入层**（收消息、发卡片/SSE 流），核心推理都在 `agent/agent_stream.py`；
- **两者慢 = 同源**，不是某一个 channel 的实现缺陷。

### 1.2 影响范围与时间
- 影响：web 聊天 + 飞书机器人所有对话
- 无独立时间窗（非突发现象，为持续性的慢），与 agent 模式多步任务强相关

---

## 二、根因分析（按影响排序）

### 🔴 根因 1：用户 session 上下文跨任务累积、不裁剪（雪球核心，v2 新发现）

| 证据 | 数值 |
|:-----|:-----|
| session 消息数轨迹 | 6 → 48 → 100 → 144 条（同一用户 session，日志实测）|
| `_trim_in_memory_to_turns` 作用域 | **仅 `session_id.startswith("scheduler_")` 生效**，用户 session 不裁剪（agent_bridge.py 代码实证）|
| 单 turn 耗时随上下文 | 6 条≈9s → 72-76 条 51-58s → 100+ 条 40-52s |
| 上下文重置点 | 仅 19:23:42 出现一次 123→7（新会话/clear_history），此后 7→57→144 再次累积 |

**机制**：
- Agent 实例按 session 常驻（`self.agents[session_id]`），`messages` 只增不减；
- 用户连续发多个深度任务（如"保存URL"→"看到一阶"→"深度分析meth-016"→"七维分析"），历史 100+ 条全部带进新任务；
- 上下文越大 → 单次 LLM 请求 prefill 越长 → TTFB 越慢（实测 60s 级）→ 40 turns 任务总时长 13-20 分钟；
- **每个任务都比上一个更慢**，是"响应越来越慢"的直接原因。

### 🟠 根因 2：深度任务步数多 × 单 turn 推理慢（主执行成本）

| 证据 | 数值 |
|:-----|:-----|
| 日志统计 LLM 调用间隔 | **平均 9.6s / 中位 8s / 最大 59s**（13,722 次）|
| 实测极简 deepseek 请求 | **0.17s** |
| 实测带 thinking 大请求（41 条消息+697 token 输出）| **9.39s** |
| config `enable_thinking` | **True**（推理模型）|
| config `agent_max_steps` | **40**（任务 A 实测跑满 40 turns）|

**机制**：
- `enable_thinking=True` → agent 用推理模型，每个请求带 reasoning，**单次 9.4s 起**；
- agent 每执行一个工具 = 一次 LLM 往返；深度分析任务 20-40 步（任务 A 实测 40 步到顶）；
- 上下文越大 prefill 越长 → 单 turn 从 9s 涨到 60s → 40 turns 累积 13-20 分钟；
- **"慢"的本质 = 任务执行时长，不是排队**（消息到达→处理同秒，见定位过程）。

### 🟡 根因 3：embedding 全量同步失败重试（持续资源消耗）

| 证据 | 数值/说明 |
|:-----|:-----------|
| 本日 `Batch embedding failed` | **64 次**（01:10-09:36+，约每 10-15 分钟一次，随任务周期触发）|
| 单次失败规模 | **23,614 chunks × 2,171 文件**（全量扫描）|
| 失败源 | 连接 **Doubao ark**（`ark.cn-beijing.volces.com/api/v3/embeddings/multimodal`）SSL EOF；zhipu key 亦无效（`"42"`）|
| config `embedding_provider` | `zhipu`（key=`"42"`、model=`123`，均无效）|

**机制**：
- 无效配置 → 每次 sync 全量扫描 2171 文件后失败，**"Index left untouched; will retry on next sync"**；
- 失败重试消耗 CPU/IO/内存（1.8G 内存下加剧抖动），并制造日志噪音；
- 记忆向量检索退化为 keyword-only（影响检索质量，非致命但降级）。

### 🟢 根因 4：系统资源紧张（内存/磁盘/无 swap）

| 证据 | 数值 |
|:-----|:-----|
| 总内存 | **1.8 GiB** |
| 进程 RSS（pid 5771）| **328 MB（17%）**，峰值曾 711MB（36.8%）|
| free 内存 | 87-121 MB（告急）|
| Swap | **0B**（无）|
| 磁盘 | 40G 用 37G（**92% 满**，剩 3.3G）|
| 历史佐证 | 08-09 `git gc --aggressive` **OOM killed（signal 9）**|

**机制**：
- 1.8G 内存 + 无 swap，大上下文（144 条消息）+ embedding 批处理（2.3 万 chunks）同时发生时内存压力陡增；
- 磁盘 92% 满 → 日志/索引/checkpoint 写入受限，可能引起 IO 卡顿。

---

## 三、因果链

```text
用户 session 上下文跨任务累积不裁剪（6→48→100→144 条）
        ↓
单次 LLM 请求 prefill 越来越长（6 条≈9s → 100+ 条 40-60s）
        ↓
enable_thinking=True 每次请求带 reasoning（基线 9.4s）
        ↓
深度分析任务 20-40 turns（agent_max_steps=40 跑满）× 单 turn 8-60s
        ↓
任务总执行时长 13-20 分钟  ←── 用户感知的"响应慢"（无排队，到达即处理）
        ↑
embedding 全量失败重试（64 次 × 2171 文件）持续消耗 CPU/IO/内存
        ↑
1.8G 内存无 swap + 磁盘 92% 满 → 资源紧张加剧
```

**为什么 web 和飞书都慢**：两者共用同一 `agent_stream` 推理引擎 + 同一 session 的 Agent 实例，任务执行时长不受渠道影响。

---

## 四、定位过程（关键步骤与数据）

| 步骤 | 动作 | 关键发现 |
|:-----|:-----|:---------|
| 1 场景澄清 | 用户追问"任务启动到响应约 20 分钟" | 目标从"单次调用慢"转为"任务总执行时长构成" |
| 2 代码追踪 | chat_channel.py / agent_bridge.py | 每 session 串行队列（concurrency=1）；`_trim_in_memory_to_turns` 仅 scheduler session 生效 |
| 3 时间线提取 | run.log 全量 grep | **消息到达→Turn 1 全部同秒**（19:06:13 / 19:11:26 / 19:19:13 / 19:23:42）→ **无排队延迟** |
| 4 任务时长统计 | Done 标记 + Sending N messages | 任务1 5.2min(21t) → 任务2 7.8min(27t) → 任务3 4.5min(14t) → 任务A ~13min(**40t 到顶**) → 任务B ~6min(29t) |
| 5 上下文轨迹 | Sending N messages 序列 | **6→48→100→144 条跨任务累积**；19:23:42 曾重置 123→7（新会话）|
| 6 单 turn 量化 | turn 间隔计算 | 6 条≈9s → 72-76 条 51-58s → 100+ 条 40-52s |
| 7 embedding 统计 | grep 失败次数 | **64 次**全量失败（23614 chunks × 2171 文件，Doubao ark SSL EOF）|
| 8 资源复核 | free/df/ps | 1.8G 内存（free 87MB）、无 swap、磁盘 92%、pid 5771 RSS 328MB |
| 9 配置复核 | config.json | thinking=True、steps=40、embedding key/model 无效（"42"/123）|
| 10 推送机制 | agent_event_handler.py | 每 turn thinking 会推送到飞书（`_send_to_channel`）、web 走流式 on_event；但最终完整回复要等任务结束 |

> **v1→v2 关键认知修正**：v1 假设"消息排队导致延迟"，v2 实测证明**无排队**（到达即处理）；真正的 20 分钟 = 任务执行时长，且随上下文累积逐任务恶化。

---

## 五、修复建议（按优先级）

### P0 短期止血（直接解决"20 分钟"）
1. **用户 session 上下文裁剪**（最高杠杆）：将 `_trim_in_memory_to_turns` 从"仅 scheduler session"扩展到用户 session——每个新任务只保留最近 N turns（如 8-12），历史任务压缩为摘要或丢弃工具消息；预期单 turn 9s→60s 的雪球消失，任务时长直接下降 40-60%；
2. **修复/置空 embedding 配置**：填入有效 key+model，或 `embedding_provider` 置空进 keyword-only——止住 64 次全量失败重试（每次扫 2171 文件）；
3. **降低 `sync_on_search` 频率**：避免每次搜索触发全量 sync，改定时/手动。

### P1 响应提速
4. **评估 `enable_thinking`**：简单/低风险任务关闭 thinking（非推理模型），仅复杂任务启用——单次 9.4s→~3s；
5. **收敛 `agent_max_steps`**（40 过大）：深度任务拆阶段（每阶段 ≤20 turns），或按任务复杂度降为 15-20；实测 40 turns 任务 13 分钟，30 turns 6 分钟；
6. **飞书进度透明度**：progress card 显示"第 N/40 步 + 已用时长"，避免用户误判为卡死（当前 thinking 片段已推送，但无进度比例）。

### P2 资源治理
7. **内存扩容或加 swap**：1.8G 明显不足（大上下文 + embedding 批处理），建议 ≥4G 或加 2G swap；
8. **磁盘清理**：92% 满（剩 3.3G），清理 tmp/、日志轮转；
9. **性能探针**：记录每 turn LLM 耗时 + 上下文条数/token，超出阈值告警——本次正是靠日志"裸奔"才需要事后人工统计。

---

## 六、复盘

### 为什么 v1 没定位准
- v1 拿到"平均 9.6s/次 + 40 步"就下了"多步累加"结论，**没有验证"消息到达→开始处理"是否即时**——默认假设了排队，实际无排队；
- 未统计**同一 session 上下文跨任务累积**（v2 新证据：6→144 条）——这才是"任务越来越慢、20 分钟级"的雪球根源；
- 教训：RCA 要区分**排队延迟**与**执行时长**两类"慢"，先用时间线实测到达→处理间隔。

### 建议跟进
- 增加**性能探针**：每 turn 记录 LLM 耗时、上下文条数/token、内存水位，超阈值告警；
- **配置校验**：启动时校验 embedding provider 的 key/model 有效性，无效显式告警并降级 keyword-only（避免 64 次静默失败重试）；
- 将"用户 session 上下文裁剪"纳入 Agent 上下文治理（呼应 MEMORY 的 Token 治理：合并 session>减请求>缩输出）。

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- MEMORY.md — Token 治理 meth-015、Agent 评测成本权重、认知寄生
- [`2026-08-10-agent-evaluation-methodology.md`](../../03_AI/agent-engineering/2026-08-10-agent-evaluation-methodology.md) — 评测方法论（成本权重：一次任务几十次调用）

### 外部资料引用

- 一手实测数据（本报告各步骤 curl/python 实测）
- `/home/lzh/CowAgent/run.log` / `nohup.out`（13,722 次调用间隔统计、282 次 embedding 失败）
- `/home/lzh/CowAgent/config.json`（thinking/steps/embedding 配置）

## Changelog
| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-10 | v2.0 | **核心结论修正**：实测消息到达→处理同秒（无排队延迟）；用户感知 ~20 分钟 = 深度任务总执行时长（turns × 单turn）。新增根因 1=用户 session 上下文跨任务累积不裁剪（6→144 条，单turn 9s→60s 雪球）；embedding 失败修正为 64 次全量（23614 chunks×2171 文件，Doubao ark SSL EOF）；修复建议升级 P0=用户 session 上下文裁剪。复盘 v1 教训（未区分排队延迟 vs 执行时长） |
| 2026-08-10 | v1.0 | 创建。定位 web/飞书响应慢：主因=推理模型单次 LLM 9.6s + agent 多步累加；次因=embedding key 失效 282 次重试 + 记忆退化；环境=1.8G 内存无 swap + 磁盘 92%。附 P0-P2 修复建议 |
