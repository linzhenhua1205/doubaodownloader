# 从 Claude Code 动态工作流看 Agent Harness 设计

> **概要**: 从 Claude Code 动态工作流看 Agent Harness 设计与六种工作流模式
>
> **关键词**: Claude Code · 动态工作流 · Harness · 上下文隔离 · 验证

---

## 📑 目录

- [核心命题](#核心命题)
- [一、Agent Harness 是什么](#一agent-harness-是什么)
- [二、单上下文执行的三大失败模式](#二单上下文执行的三大失败模式)
- [三、动态工作流 vs 静态工作流](#三动态工作流-vs-静态工作流)
- [四、六种典型工作流模式](#四六种典型工作流模式)
  - [1. Classify-and-act（分类再行动）](#1-classify-and-act分类再行动)
  - [2. Fanout-and-synthesize（拆开并行，最后汇总）](#2-fanout-and-synthesize拆开并行最后汇总)
  - [3. Adversarial verification（对抗式验证）](#3-adversarial-verification对抗式验证)
  - [4. Generate-and-filter（生成再筛选）](#4-generate-and-filter生成再筛选)
  - [5. Tournament（锦标赛式比较）](#5-tournament锦标赛式比较)
  - [6. Loop until done（直到完成为止）](#6-loop-until-done直到完成为止)
- [五、六大使用场景](#五六大使用场景)
  - [① 迁移和重构](#①-迁移和重构)
  - [② 深度研究](#②-深度研究)
  - [③ 深度验证](#③-深度验证)
  - [④ 大规模排序](#④-大规模排序)
  - [⑤ 记忆和规则遵守](#⑤-记忆和规则遵守)
  - [⑥ 根因分析](#⑥-根因分析)
- [六、局限性与使用建议](#六局限性与使用建议)
  - [局限性](#局限性)
  - [使用技巧](#使用技巧)
- [七、对 Agent Harness 设计的启示](#七对-agent-harness-设计的启示)
- [与已有知识交叉引用](#与已有知识交叉引用)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 核心命题

复杂任务不能只靠一个上下文一路做到底。任务需要拆分，上下文需要隔离，验证需要独立，流程也要能在中断后恢复。不同子任务还可以选择不同模型和预算，避免所有事情都挤在同一个执行路径里。

这些设计放在 Claude Code 里，是 Dynamic Workflows；放到更大的 Agent 系统里，就是 **Agent Harness** 要解决的问题 [来源: 1]。

> **实证锚点**：该设计思想在基准上有量化支撑——CaMeL（arXiv:2503.18813）在 AgentDojo 上通过"可信控制流 × 不可信数据流"分离实现 77% 任务可证明安全（基线 84%）；而"上下文隔离 + 独立验证"正是对抗 self-preferential bias 的工程化表达（同源：独立验证 Agent 与执行 Agent 不共享上下文，等价于阻断"自证"路径）[来源: 2]。

---

## 一、Agent Harness 是什么

Harness = 让 Agent 更有组织地干活的执行框架，它负责：

- 任务怎么拆
- Agent 怎么调用
- 上下文怎么隔离
- 结果怎么合并
- 中断后怎么恢复

Claude Code 本身有一套**默认 Harness**（面向编码），日常开发够用。但复杂任务（Research、安全分析、Agent Teams、Code Review）过去需要开发者手写自定义 Harness。Dynamic Workflows 的突破是：**Claude 可以现场生成 Harness，不再需要人手动搭流程。**

---

## 二、单上下文执行的三大失败模式

| 问题 | 表现 | 根因 |
|:-----|:-----|:------|
| **Agentic laziness** | 任务没做完就提前收尾（如 50 个问题只处理 35 个就宣告完成） | 上下文过长后 Agent 自行"收工" |
| **Self-preferential bias** | Agent 倾向于偏好自己的输出，自我验证时漏掉问题 | 验证和执行共享同一上下文 |
| **Goal drift** | 长任务中原始目标保持能力下降，边界条件、反例要求被压缩丢掉 | 上下文压缩导致信息损失 |

**共同根因**：一个上下文承担太多职责（规划+执行+验证+总结）。

---

## 三、动态工作流 vs 静态工作流

| 维度 | 静态工作流 | 动态工作流 |
|:-----|:----------|:----------|
| 写法 | 提前考虑各种边界，写得通用 | 根据当前任务现场定制 |
| 灵活性 | 固定流程，长尾场景照顾不到 | 任务级编排，灵活适配 |
| 类比 | 固定流水线 | 临时搭建的工程团队 |

---

## 四、六种典型工作流模式

### 1. Classify-and-act（分类再行动）

先分类 Agent 判断任务类型 → 交给对应 Agent 处理 → 末尾可选再分类。
**场景**：工单分派（Bug/产品反馈/咨询）。

### 2. Fanout-and-synthesize（拆开并行，最后汇总）

大任务拆成小步骤 → 各 Agent 独立处理 → 合并结果。
**关键**：不是"多开几个 Agent"，而是让每个 Agent 的上下文更干净。
**场景**：验证一篇文章 80 个技术说法，每条说法一个子 Agent。

### 3. Adversarial verification（对抗式验证）

Agent A 产出 → Agent B 按标准验证 → Agent C 专门从反方向检查。
**用来解决**：Same-context self-preferential bias。
**场景**：代码审查、安全分析、事实核查、方案评估。

### 4. Generate-and-filter（生成再筛选）

先批量生成候选 → 按评分/去重/验证流程筛选出最优。
**场景**：起名字、写方案、列备选架构、生成测试用例。

### 5. Tournament（锦标赛式比较）

多 Agent 用不同思路做同一任务 → 两两比较 → 评审选胜出 → 得最终方案。
**为什么好用**：让模型绝对打分不稳定，但比较 A 和 B 往往更可靠。
**场景**：CLI 工具命名、产品方案选择、架构路线比较。

### 6. Loop until done（直到完成为止）

持续启动 Agent 直到满足停止条件（如没有新发现、测试全通过）。
**解决**：提前写死轮次不够可靠——你事先不知道需要几轮。
**场景**：调试、根因分析、持续分拣、反复验证。

---

## 五、六大使用场景

### ① 迁移和重构

- 拆开工作：调用点/测试/模块/文档/类型定义各一个子 Agent
- 关键：独立 worktree 隔离修改，最后统一审查合并
- 案例：Bun 从 Zig 重写到 Rust [来源: 1]

### ② 深度研究

- 并行搜索、抓取来源、对抗式验证、合成带引用报告
- 模式：扩大搜索 → 核查质量 → 汇总报告
- 可迁移：代码库研究（路由/中间件/数据库模型/测试文件分别派 Agent）

### ③ 深度验证

1. Agent 抽取出所有待核查说法
2. 每条说法一个子 Agent 分别验证
3. 再加验证 Agent 判断引用来源质量

> **机制说明**：③ 本质是"对抗式验证"（Adversarial verification）在生产中的落地——每个子 Agent 的上下文只含"一条说法 + 证据来源"，不共享执行 Agent 的上下文，从结构上切断 self-preferential bias（同上下文自我验证的偏差）[来源: 2]。

### ④ 大规模排序

- 1000 行数据塞一个 prompt → 质量下降/超上下文
- 做法：两两比较，或先分组再排序合并
- 场景：工单/Bug/简历/需求池排序

### ⑤ 记忆和规则遵守

- 为 CLAUDE.md 每条规则配一个 verifier agent 检查
- 反向流程：从 session + code review 中提取反复纠正的点 → 聚类验证 → 沉淀回 CLAUDE.md
- **亮点**：把"人类反复纠错"变成可沉淀的规则更新流程

### ⑥ 根因分析

- 多 Agent 从不同证据提出独立假设（日志/文件/数据各一路）
- 验证 Agent + 反驳 Agent 分别检查
- 降低 self-preferential bias 导致的过早相信

---

## 六、局限性与使用建议

### 局限性

- 还很新，token 消耗更大
- 不适合简单任务（改一个函数、补一个测试）
- 适合：步骤多、要并行、需交叉验证、易遗漏、单个上下文放不下

### 使用技巧

- Prompt 尽量具体：说明任务结构、验证标准、停止条件
- 与 `/goal`、`/loop` 结合使用（周期性运行 + 明确完成条件）
- 可指定 token budget（如 `use 10k tokens`）
- Workflow 可保存复用：`s` 保存 → `~/.claude/workflows/` → 通过 skill 分发

---

## 七、对 Agent Harness 设计的启示

> 复杂任务的可靠性，不能只靠模型本身变强，也要靠**执行结构**来保证。

关键设计原则：

1. **任务拆分**：单一上下文承担太多职责 → 可靠性下降 [来源: 1]
2. **上下文隔离**：每个子 Agent 拥有干净、聚焦的上下文
3. **验证独立**：验证和执行分离，对抗式降低自我偏见 [来源: 2]
4. **中断恢复**：工作流可从中断位置继续执行
5. **模型差异化**：不同子任务选不同模型（轻/强），平衡成本和效果
6. **可沉淀**：好的工作流模式可保存、复用、分发为 skill

---

## 与已有知识交叉引用

- **Agent 工程化四件套**：与 [Agent CLI 报告](../../03_AI/agent-engineering/2026-06-26-agent-cli-architecture-report.md)、[Agent 自进化五层](2026-06-26-agent-self-evolution-five-layers.md)、Agent 工具链工程化、Agent OS 五种范式 形成互补——Harness 是四件套中"执行架构"维度的深化
- **[GEPA 架构拆解](../../07_industry-research/18_methodology-framework/2026-06-26-gepa-architecture.md)**：GEPA 关注 Prompt/Skill 自进化，Harness 关注执行结构组织，两者在 Agent 工程质量上是同一枚硬币的两面
- **[Event-Driven Agent 实战](2026-06-26-event-driven-agent-prometheus-recovery.md)**：Event-Driven + ReAct 是单 Agent 模式，Harness 是多 Agent 编排，可互补使用

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [Agent CLI 报告](../../03_AI/agent-engineering/2026-06-26-agent-cli-architecture-report.md) — 关联
- [Agent 自进化五层](2026-06-26-agent-self-evolution-five-layers.md) — 关联
- Agent 工具链工程化 — 关联
- Agent OS 五种范式 — 关联
- [GEPA 架构拆解](../../07_industry-research/18_methodology-framework/2026-06-26-gepa-architecture.md) — 关联
- [Event-Driven Agent 实战](2026-06-26-event-driven-agent-prometheus-recovery.md) — 关联

### 外部资料引用

- 来源: [博客园 - 小七-七牛开发者](https://www.cnblogs.com/Qiniu-developer/p/20423118) | **作者**: 小七-七牛开发者 | **日期**: 2026-06-10
- Debenedetti et al., [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813), arXiv:2503.18813, 2025 — 对抗式验证/上下文隔离的基准证据（AgentDojo 77% vs 84%）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-08-18 | v1.1 | 质量提升：正文补 4 处行内来源标注 + CaMeL 实证锚点（上下文隔离/对抗验证的 AgentDojo 基准证据） |
| 2026-07-24 | v1.0 | 初始版本 |
