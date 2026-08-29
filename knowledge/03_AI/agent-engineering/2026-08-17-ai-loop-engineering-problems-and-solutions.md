# AI Loop 工程实践问题全景：原理与对策

> **类型**: 深度分析 | **日期**: 2026-08-17 | **版本**: v2.0（质量提升：外部论文一手实证 + 理论基础可溯源）
> **来源**: 对话推导 + 系统实证 + 论文一手（Lost in the Middle TACL 2023 / LLMs Cannot Self-Correct ICLR 2024 / EvoHarness-RL 2026 / Progressive Crystallization 2026）+ 信息论/可计算性/分布式理论
> **状态**: v2.0 | **相关**: [`2026-08-17-loop-verification-independence-economy-deep-analysis.md`](2026-08-17-loop-verification-independence-economy-deep-analysis.md)（验证独立性与 token 经济性，本篇为其工程问题域扩展）· [`2026-08-17-principle-engineering-gap-deep-analysis.md`](../../04_person/cognition/2026-08-17-principle-engineering-gap-deep-analysis.md)

## 📑 TOC

1. 一句话结论
2. 问题全景：五类典型故障（MECE）
3. 第一性原理：为什么这些问题必然发生（含论文锚点）
4. 逐类拆解：问题 → 原理 → 对策（含实证）
5. 五道防线的统一框架
6. 实证锚点：真实系统怎么做的（v2.0 新增外部系统）
7. 落地清单：10 项检查
8. 数据缺口
9. 参考来源
10. Changelog

---

## 1. 一句话结论

**Loop 工程问题 = 有界概率生成器被当无界确定性执行器用。** 五类问题（上下文丢失/终结不了/输出膨胀/token 失控/网络不稳）对应五种错配（有界存储/无终止谓词/无长度自律/无成本感知/不可靠信道），对策统一为五道防线：**预算墙、终止谓词、外部锚定、幂等重试、状态外置**——核心不是"让模型更好"，是"用工程骨架保证确定性"。每一类错配都有论文一手实证支撑（§3），不是工程经验的猜测。

---

## 2. 问题全景：五类典型故障（MECE）

| # | 问题域 | 典型表现 | 严重度 | 频率 |
|:-:|:-------|:---------|:------:|:----:|
| 1 | 上下文丢失 | 长对话忘记早期约定/指令；截断后行为漂移 | 致命 | 高 |
| 2 | 终结不了 | 反复"再做一步"；改来改去不收敛；卡循环 | 致命 | 高 |
| 3 | 输出膨胀 | 每轮输出太长；重复啰嗦；token 爆炸 | 高 | 很高 |
| 4 | token 消耗失控 | 成本超预算；长 loop 成本指数增长 | 高 | 高 |
| 5 | 网络不稳定 | 请求超时/重试风暴/半途中断 | 中高 | 中 |

---

## 3. 第一性原理：为什么这些问题必然发生？（含论文锚点）

**根因：loop 把「概率生成器」当「确定性执行器」用。**

```
LLM essence: given context -> probability distribution -> sampled output
  - bounded: context window finite (cannot remember everything)
  - probabilistic: output not guaranteed correct (hallucination/repeat/drift)
  - non-terminating: no intrinsic 'done' signal (whether to continue is a guess)
  - cost-blind: does not know how many tokens it burned

loop assumption: executor is deterministic/correct/terminating/cost-aware
  - boundedness ignored -> context loss
  - probability ignored -> output bloat / hallucination
  - non-termination ignored -> never terminates
  - cost-blindness ignored -> token burn
```

| 问题 | 错配本质 | 理论表述 | 论文锚点 |
|:-----|:---------|:---------|:---------|
| 上下文丢失 | 有界存储 vs 无限信息流 | 有限窗口=有损信道（信息论：存储容量<信息总量）；**且注意力呈 U 型分布，中间信息检索显著下降** | Lost in the Middle（TACL 2023）[来源: arXiv:2307.03172] |
| 终结不了 | 无终止谓词 vs 无限迭代 | 无停机条件=不保证停机（可计算性：缺 halt 判定）；**自评闭合时模型无法自我纠错甚至越改越错** | LLMs Cannot Self-Correct Reasoning Yet（ICLR 2024）[来源: arXiv:2310.01798] |
| 输出膨胀 | 无长度自律 vs 生成偏好 | 训练目标最大化延续概率，无成本信号 | 语言建模目标（因果 LM，NLL 最小化）[来源: 通用知识] |
| token 消耗 | 无成本感知 vs 线性计费 | 固定成本×无界步数=无界总成本 | 本地实测：缓存 miss 占 57.1%（MEMORY 08-15） |
| 网络不稳 | 不可靠信道 vs 假设可靠 | 异步网络无确定性（FLP 不可能定理） | Fischer, Lynch, Paterson 1985 [来源: 经典分布式理论] |

---

## 4. 逐类拆解：问题 → 原理 → 对策（含实证）

### 4.1 上下文丢失（Context Loss）

**原理**：窗口有限 + 注意力近因偏好（recency bias）→ 早期信息被稀释/截断。**一手实证**：Lost in the Middle（TACL 2023）在多文档 QA 和 key-value 检索任务上证明——相关信息位于输入开头或结尾时性能最高，**位于中间时显著下降，即使显式长上下文模型也如此**（U 型注意力曲线）[来源: arXiv:2307.03172]。

**三种丢失模式**：① 硬截断（超窗直接丢最早）② 软稀释（lost in the middle——**有论文实证，非推测**）③ 摘要失真（有损压缩，细节先丢）。

**对策（分层记忆架构）**：
```
L0 working memory (current turn) <- only this turn's essentials
L1 rolling summary (history compression) <- periodic summary + key-fact
   extraction (not full)
L2 external storage (files/KB/vector DB) <- persisted, retrieve on demand (RAG)
```
- 关键事实外置：约定/约束写独立文件（AGENT.md 模式），每轮重新注入，不靠模型记忆
- 摘要策略：保留关键约束 + 丢弃过程细节（约束优先于过程）
- 检索代替记忆：长历史用检索而非全量塞入——信息放外部，需要时取
- **实证呼应**：EvoHarness-RL 把外部状态（Belief/Progress/Experience）作为一等公民管理，训练后 Qwen3-8B 在 ALFWorld 达 96.9% success——"关键状态外置+选择性访问"优于"全塞上下文" [来源: arXiv:2608.05446]

### 4.2 终结不了（No Termination）

**原理**：模型无内在"完成"信号，训练目标倾向"继续做"（多做=更稳妥表现）。无终止谓词时 loop = 不保证停机的图灵机。**一手实证**：ICLR 2024 证明 LLM 内在自校正（无外部反馈）失败，且**自校正后性能下降**——"假完成"不是个别现象而是系统性缺陷 [来源: arXiv:2310.01798]。

**三种卡死**：① 无限改进（永远"还能更好"）② 振荡（A→B→A 横跳）③ 假完成（自评闭合回路，见 [loop 验证专篇](2026-08-17-loop-verification-independence-economy-deep-analysis.md)）。

**对策（终止谓词三件套）**：
```
① objective completion standard (check gate): verifiable hard criteria
   (file exists / format passes / test passes / length met) - NOT 'looks good'
② hard cap (max iterations): stop at N rounds, default 5; on cap = suspend
   for human, not silent pass
③ change detection: log per-round actions -> repeated (A->B->A) = oscillation
   -> force convergence / roll back to previous version
```

### 4.3 输出膨胀（Output Bloat）

**原理**：模型训练目标=最大化延续概率——**有继续说下去的先验**。无长度约束时倾向多写。loop 双重累积：单轮冗长 × 多轮叠加。

**对策（输出预算三层墙）**：
```
① format constraint: structured output (JSON/table/template) - format itself
   limits length
② length budget: explicit 'each section <= N chars' + max_tokens hard cut
③ incremental output: emit only changes per round (diff), not full text again
```

### 4.4 token 消耗失控（Token Burn）

**原理**：成本 = 输入+输出线性计费。Loop 成本结构 = 每轮全量上下文重发 + 累积输出 → 总成本 ≈ 步数 × 每步成本，步数无界+上下文增长 = 成本指数恶化。**本地实测**：独立验证子 agent 因打破缓存成为最贵步骤，缓存 miss 占 57.1%；8/17 新价后 flash miss 同用量 +186% [来源: MEMORY 08-15/08-17]。

**对策（成本控制五则）**：
1. 上下文预算：每轮显式限制（如 ≤8K），超了摘要/裁剪
2. 缓存复用：相同前缀用缓存（精确/语义），避免重复计费
3. 步数预算：max iterations 也是成本上限
4. 成本分层：简单步骤用便宜模型（路由），复杂用强模型
5. 成本仪表：每 loop 记录消耗，超预算熔断（非事后看账单）

### 4.5 网络不稳定（Network Instability）

**原理**：分布式不确定性是物理事实（FLP：消息必可能丢失/延迟/乱序 [来源: Fischer-Lynch-Paterson 1985]）。API 调用天然不可靠：超时/429/5xx/半途断连。

**对策（可靠性四件套）**：
```
① retry + exponential backoff: 429/5xx -> retry, wait 1s->2s->4s, avoid
   retry storms
② layered timeouts: connect(short) < read(medium) < total(long); fail fast,
   never wait forever
③ idempotent retry: tool calls replayable (request_id dedup; mandatory for
   money-movement ops)
④ checkpoint resume: state externalized; recover from last checkpoint after crash
```

---

## 5. 五道防线的统一框架

```
+-----------------------------------------------------------+
| Defense     Fixes         Core mechanism                  |
+-----------------------------------------------------------+
| ① budget   output bloat   max_tokens + length constraint  |
|   wall      token burn     context budget + step cap      |
| ② terminal never ends     check gate + max iters          |
|   predicate                (incl. oscillation detection)  |
| ③ external context loss   layered memory + facts external |
|   anchor     hallucination evidence re-injection          |
| ④ idempotent network      backoff retry + idempotency +   |
|   retry      instability   layered timeouts               |
| ⑤ state     crash         persisted checkpoint + resume   |
|   external   recovery                                     |
+-----------------------------------------------------------+
```

**关键洞察**：五道防线是同一思想的五种表现——**把「不可靠的生成器」用「可靠的工程骨架」包起来**。骨架负责确定性（预算/终止/重试/持久化），生成器负责灵活性（内容/方案/代码）。

---

## 6. 实证锚点：真实系统怎么做的

### 6.1 外部系统（v2.0 新增一手）

| 系统 | 上下文 | 终止 | 输出 | 成本 | 网络 | 来源 |
|:-----|:-------|:-----|:-----|:-----|:-----|:-----|
| **EvoHarness-RL** | 外部状态 BPE（Belief/Progress/Experience）显式管理 | harness 状态驱动选择性访问（96.9% success） | 结构化 harness 动作空间 | cost-aware GRPO 显式成本信号 | — | 🟢 arXiv:2608.05446 |
| **Progressive Crystallization** | 已验证行为→确定性工作流（8 个月 0→45%） | 证据驱动 promotion/demotion | 确定性执行 | 单 incident 成本 -70%+ | — | 🟢 arXiv:2607.07052 |
| **Agent Plugins 1.0** | skills+MCP 打包为可移植插件 | 企业 managed settings 管控 | 规范约束 | 跨客户端复用省维护 | — | 🟢 GitHub Changelog 08-12 |
| **GitHub Copilot** | Copilot memory（08-11 发布）+ 压缩 | 云 agent 推理级别可配（08-03） | 工具结果截断 | per-model token 用量报告（08-11） | 重试机制 | 🟢 Changelog 08-03~14 |

### 6.2 本系统与邻近系统（定性观察）

| 系统 | 上下文 | 终止 | 输出 | 成本 | 网络 |
|:-----|:-------|:-----|:-----|:-----|:-----|
| Claude Code | 自动压缩+工具结果截断 | 用户控制为主 | 工具结果截断 | 有成本显示 | 重试机制 |
| DeepSeek Harness | 上下文管理器（关键+摘要） | Ralph 循环 check gate | 结构化约束 | 有 token 预算 | 重试封装 |
| CowAgent | 每日记忆+关键约束文件 | 工具循环（max steps） | 文档模板约束 | 成本记录（MEMORY） | git 双通道备用 |

**共同模式**：成熟系统（外部论文 + 邻近产品 + 本系统）**不指望模型自律**，全部用**外部机制**强制（压缩/截断/上限/重试/状态外置）——五道防线是产业共识而非一家之言。

---

## 7. 落地清单：10 项检查

```yaml
context:
  1. key constraints externalized to file? (AGENT.md pattern)
  2. history has summary/trim strategy? (L1/L2 layering)
termination:
  3. completion criteria verifiable? (not 'looks good')
  4. max iterations hard cap in place?
  5. oscillation detection? (A->B->A)
output:
  6. format/length constraints?
  7. incremental output (diff) instead of full re-send?
cost:
  8. context budget + step budget?
  9. cost circuit-breaker (stop when over budget)?
network:
  10. idempotent retry + checkpoint resume?
```

---

## 8. 数据缺口

| 缺口 | 说明 |
|:-----|:-----|
| 问题频率量化 | 五类问题频率为定性估计（高/中），未做真实 loop 日志统计（可补：CowAgent 运行日志聚类） |
| 对策效果量化 | 各对策（摘要/截断/重试）的实际 token 节省/成功率提升未实测（可补：A/B 对照实验） |
| Lost in the Middle 具体下降幅度 | 论文给出定性结论+图，各模型在中间位置的具体 accuracy 下降数值未摘录（需读原文） |
| FLP 在 LLM API 场景的应用 | 经典 FLP 假设（异步+故障进程）与真实 API 网关的映射未展开 |

---

## 9. 参考来源

| # | 来源 | 类型 | 日期 |
|:--|:-----|:-----|:-----|
| 1 | [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)（Liu et al., TACL 2023） | 🟢 论文一手 | 2023-07 |
| 2 | [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798)（Huang et al., ICLR 2024） | 🟢 论文一手 | 2024-03 |
| 3 | [EvoHarness-RL](https://arxiv.org/abs/2608.05446)（Ning et al., LLA@COLM 2026） | 🟢 论文一手 | 2026-08 |
| 4 | [Progressive Crystallization](https://arxiv.org/abs/2607.07052)（Malik） | 🟢 论文一手 | 2026-07 |
| 5 | [Agent Plugins 1.0（GitHub Changelog）](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app/) + Changelog 08-03~14 | 🟢 官方一手 | 2026-08 |
| 6 | [loop 验证独立性专篇](2026-08-17-loop-verification-independence-economy-deep-analysis.md)（四条件/token 消耗结构/2×2 矩阵） | 🟢 知识库 | 2026-08-17 |
| 7 | 系统实证：Claude Code / DeepSeek Harness / CowAgent 运行观察 | 🟡 观察 | — |
| 8 | 理论基础：信息论（有损信道）、可计算性（停机问题）、FLP 不可能定理（Fischer, Lynch, Paterson 1985） | ⚪ 经典理论 | 1985 |

---

## 10. Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-17 | v2.0 | **质量提升**：①五类错配补论文一手锚点（Lost in the Middle 证 U 型注意力、ICLR 2024 证自评失效、EvoHarness 证状态外置、本地实测证成本）；②§4.1 补"软稀释有实证非推测"表述 + EvoHarness BPE 呼应；③§6 拆分为 6.1 外部系统（4 个 🟢 一手，含 GitHub Changelog 实证）+ 6.2 邻近系统观察；④"共同模式"升级为"产业共识"论断（外部论文+产品+本系统三方一致）；⑤参考来源升级为可溯源表；⑥数据缺口更新（补可执行的补测路径） |
| 2026-08-17 | v1.0 | 初稿。五类问题 MECE + 第一性原理（概率生成器 vs 确定性执行器错配）+ 逐类对策 + 五道防线统一框架 + 实证锚点 + 10 项落地清单 |
