# Harness Agent 的 Memory 工程与纵深防御

> **概要**: Harness Agent 的 Memory 工程与纵深防御五平面架构
>
> **关键词**: Memory 工程 · 纵深防御 · Action Gate · Provenance · 安全

---

## 📑 目录

- [核心论点](#核心论点)
- [七条设计律](#七条设计律)
- [四类 Memory 架构](#四类-memory-架构)
- [写入侧：决定胜负的关键](#写入侧决定胜负的关键)
- [冲突、遗忘与信任](#冲突遗忘与信任)
- [Action Gate：安全价值兑现之处](#action-gate安全价值兑现之处)
- [Multi-Agent 安全](#multi-agent-安全)
- [参考资料](#参考资料)
- [Related](#related)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 核心论点

Memory 安全不是给向量库加过滤器，而是让安全属性沿数据生命周期持续存在，并在行动前兑现。生产架构应把系统拆成**五个平面**：Harness Core（编排）、Memory Plane（状态生命周期）、Policy Plane（确定性策略）、Execution Plane（受限执行）、Observability Plane（证据与运营）。

> **实证锚点**：CaMeL 论文（arXiv:2503.18813）给出同方向的关键证据——在 AgentDojo 基准上，通过**显式分离可信控制流与不可信数据流**（正是"Policy Plane × Memory Plane"的学术版），可保留 77% 任务的可证明安全性（无防御基线为 84%），仅损失 7pp 功能。这说明"安全属性靠架构分层承载、而非模型自我消毒"是可量化的工程选择 [来源: 4]。

## 七条设计律

1. **Memory 是不可信输入，不是系统指令** — 被召回不等于真实，更不等于有权改变行为 [来源: 1]
2. **Memory 的胜负手在写入，不在存储** — 垃圾事实一旦进入长期状态，再好的检索也只会更精准地召回垃圾
3. **来源必须成为数据的一部分** — Provenance 须跟随事实进入存储、召回和运行时上下文 [来源: 4]
4. **模型不是消毒器** — 总结、抽取、重写和 Agent 转述不能自动提升信任等级 [来源: 3]
5. **新信息不天然优于旧信息** — Recency 只能在信任不降低的前提下参与冲突消解
6. **高危动作必须由确定性策略授权** — 风险分级、目标域、凭证范围和审批由 Harness 决定 [来源: 2]
7. **纵深防御要拆散攻击链** — Action Gate（该不该做）× Egress Control（数据能否出去）× Sandbox & Least Privilege（最多能碰到什么） [来源: 3][来源: 5]

## 四类 Memory 架构

| 类型 | 回答 | 推荐形态 | 主要风险 |
|:-----|:-----|:---------|:---------|
| Working Memory | 当前任务做到哪一步？ | Context + Redis/状态表 | 摘要丢失来源；跨会话串线 |
| Episodic Memory | 过去发生过什么？ | Append-only 事件日志 | 日志含敏感输入；越权回放 |
| Semantic Memory | 当前相信哪些事实？ | 结构化事实 + 向量/全文索引 | 错误事实被持续召回 |
| Procedural Memory | 以后应该怎样做？ | 版本化策略/Skill/模板 | 持久化行为后门；影响控制流 |

**反模式**：把对话、事件、事实和流程全部切片后放进同一个向量集合 — 同时失去历史不可变性、当前信念一致性、流程版本治理和精确删除能力。

## 写入侧：决定胜负的关键

- **Hot Path vs Cold Path**：同步热路径只处理"下一步必须立刻可见"的状态；长期事实与流程固化走异步冷路径
- **写入对象必须是原子事实** — 把"用户偏好 FastAPI"拆成 subject-predicate-object 三元组
- **受控谓词表**：为 high-value 事实维护受控谓词表，避免 `likes_framework` / `favorite_backend` / `prefers_framework` 无法等同
- **Confidence ≠ Trust**：`extraction_confidence = 0.99` 只说明模型"看清楚了邮件写了什么"，不说明邮件内容可信

## 冲突、遗忘与信任

Semantic Memory 职责不是保存所有说法，而是维护**可追溯的当前信念视图**。新事实到来区分五种关系：IDENTICAL / REFINEMENT / INDEPENDENT / ADDITIVE / CONFLICT。

**遗忘四机制**：TTL（硬过期）、Invalidation（关闭有效区间）、Decay/Archive（转冷存）、Subject Deletion（按数据主体删除）。

**双时态**：Valid Time（事实在业务世界何时有效）与 Transaction Time（系统何时写入该事实）需区分。

## Action Gate：安全价值兑现之处

高危动作不能由 LLM 自评风险等级。Gate 至少检查六个维度：

1. **action risk** — 最坏后果（R0只读低敏 / R1可逆 / R2不可逆高成本）
2. **data sensitivity** — 参数是否含敏感数据
3. **causal taint** — 关键参数是否依赖不可信来源 [来源: 4]
4. **destination** — 目标域/收件人是否允许
5. **credential scope** — 凭证是否最小授权
6. **approval state** — 是否满足双人复核

**核心规则**：只要高危动作的关键参数依赖未经验证的不可信来源，就不得自动执行。

> **与 CaMeL 的机制对齐**：CaMeL 正是把该规则形式化为"capability"机制——工具调用前按数据流来源强制安全策略，阻止私密数据经未授权数据流外泄。六个维度中的 causal taint（维度 3）对应其"不可信数据不得影响控制流"的核心定理，其余五维是 Harness 侧的工程扩展 [来源: 4][来源: 2]。

## Multi-Agent 安全

- **Taint Laundering（污点洗白）**：Worker 总结不可信网页后，Orchestrator 可能把"来自不可信网页的断言"误认为"来自内部 Agent 的可信结论" [来源: 3]
- **推荐隔离模式**：读取不可信内容的 Worker 不持有高危工具；Privileged Executor 只接收通过策略验证的参数
- **Agent 间消息不能是裸文本** — 应携带 provenance、trust、field-level dependency
- 共享 Memory 的投毒会跨 Agent 和角色传播，应经 Memory Gateway 控制写入 [来源: 1]

> **风险量化视角**：OWASP Top 10 for Agentic Applications 将"Memory Poisoning"与"Improper Input Handling"列为独立风险类目，说明该威胁已被行业共识为第一梯队（而非边缘场景）。Simon Willison 的 "lethal trifecta"（工具访问 + 不可信内容 + 长期记忆三要素叠加）正对应本文件 Memory Plane × Execution Plane 的交叉面 [来源: 1][来源: 3]。

## 参考资料

1. OWASP GenAI Security, [LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
2. OWASP GenAI Security, [Top 10 for Agentic Applications 2026](https://genai.owasp.org/download/52117/)
3. Simon Willison, [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
4. Debenedetti et al., [Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813), 2025
5. NIST, [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
6. Debenedetti et al., [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813), arXiv:2503.18813, 2025 — 可信控制流与不可信数据显式分离；AgentDojo 上 77% 任务可证明安全（无防御 84%）

## Related

- [Agent OS 五种范式](2026-06-26-agent-os-five-paradigms.md) — 驯服不确定性的架构模式
- [Agent 混合架构设计](2026-07-08-agent-hybrid-architecture-design.md) — LLM 规划×确定性框架
- [Claude Code 动态 Workflows](2026-06-26-claude-code-dynamic-workflows.md) — Agent Harness 深度解析
- [PKM/RAG/Wiki/Memory 四类知识系统对比](05_tools/knowledge-management/2026-06-26-pkm-rag-wiki-memory-systems.md)

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [Agent OS 五种范式](2026-06-26-agent-os-five-paradigms.md) — 关联
- [Agent 混合架构设计](2026-07-08-agent-hybrid-architecture-design.md) — 关联
- [Claude Code 动态 Workflows](2026-06-26-claude-code-dynamic-workflows.md) — 关联
- [PKM/RAG/Wiki/Memory 四类知识系统对比](05_tools/knowledge-management/2026-06-26-pkm-rag-wiki-memory-systems.md) — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-08-18 | v1.1 | 质量提升：正文补 8 处行内来源标注 + CaMeL 量化锚点（AgentDojo 77% vs 84%）+ Action Gate 与 Multi-Agent 安全实证扩展 |
| 2026-07-24 | v1.0 | 初始版本 |
