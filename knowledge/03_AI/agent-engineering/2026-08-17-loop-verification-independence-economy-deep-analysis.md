# Loop × 验证独立性 × Token 经济性：循环工程的完整判据

> **类型**: 深度分析 | **日期**: 2026-08-17 | **版本**: v2.0（质量提升：外部一手实证补全 + 核验状态标注 + 参考可溯源）
> **来源**: 对话推导 + Ralph 五要素框架 + 本地成本实测 + 论文一手（LLMs Cannot Self-Correct Reasoning Yet, ICLR 2024）
> **状态**: v2.0 | **相关**: [`2026-08-14-ralph-loop-deepseek-harness-loop-architecture-analysis.md`](../methodology/2026-08-14-ralph-loop-deepseek-harness-loop-architecture-analysis.md)（五要素 v2.0）· pipeline-verification-loop 技能 · MEMORY.md 成本实测 · [AI Loop 工程实践问题全景](2026-08-17-ai-loop-engineering-problems-and-solutions.md)

## 📑 TOC

1. 一句话结论
2. 为什么自评不可靠：反馈回路闭合（信息论第一性原理 + 论文实证）
3. 验证独立性四条件（可复用检查清单）
4. Loop 判据：「写清楚」的三层递进（L1/L2/L3）
5. Token 经济性：边际成本曲线与 loop 消耗结构
6. 决策矩阵：可验证性 × 经济性（2×2）
7. 循环工程第六要素：经济性（五要素 → 六要素）
8. 本地落地三条军规
9. 数据缺口
10. 参考来源
11. Changelog

---

## 1. 一句话结论

**Agent 自评 = 闭合反馈回路（信息论上零信息增益）；独立验证 = 打破回路（条件独立性）。** 该命题不是观点而是已被论文验证的事实：ICLR 2024 的《Large Language Models Cannot Self-Correct Reasoning Yet》证明 LLM 在无外部反馈时自校正失败，甚至**自校正后性能下降**（[来源: arXiv:2310.01798]）。Loop 适用判据不是「写得清楚」而是「完成标准可被机械验证（L3）且验证成本 < 生成成本」。Token 富人/穷人是边际成本曲线而非身份标签——独立验证子 agent 因打破缓存成为 loop 最贵一步（本地实测缓存 miss 占 57.1%），因此穷人上 loop 的铁律：**验证用脚本不用子 agent + iteration caps + 预算硬约束**。

---

## 2. 为什么自评不可靠：反馈回路闭合

### 2.1 失效四机制

| # | 机制 | 机理 | 类比 |
|:-:|:-----|:-----|:-----|
| 1 | 确认偏差 | 生成时锚定结论，评估时找支持证据忽略反例 | 作者审自己稿子 |
| 2 | 错误相关性 | 评估误差与生成误差共享先验，模式高度相关 | 同人测同一错题两遍 |
| 3 | 流利度替代正确性 | 自评回答"连贯吗"而非"符合事实吗" | 演讲者自我感觉良好 |
| 4 | 无外部参照 | 只能问"符合内部模型吗"，问不出"符合真实世界吗" | 闭路循环 |

### 2.2 信息论表述

设生成者 G、验证者 V、外部证据 E、产出 P。自评时 V=G（同一内部状态），则：

```
P(eval conclusion | G's internal belief, P) NOT conditionally independent of
P(generation | G's internal belief)
-> evaluation is a 'shadow' of generation, carries no new information
```

**验证产生信息增益 ⟺ V 的信息状态 ⊥ G 的信息状态 | E（条件独立）**。独立上下文的子 agent 有效不是因为更聪明，而是**信息状态解耦**。

### 2.3 论文一手实证（v2.0 升级）

> **Huang et al., ICLR 2024《Large Language Models Cannot Self-Correct Reasoning Yet》**（arXiv:2310.01798，Google DeepMind）：
> - 核心发现：LLM 的**内在自校正**（仅靠自身能力、无外部反馈）在推理任务上**失败**；
> - 更反直觉的量化结果：自校正后**性能不仅不提升，反而下降**（如 GSM8K 等推理基准上 accuracy 下降）——"越改越错"；
> - 论文结论：自校正有效的前提是**外部反馈**（如正确性信号/验证器），而非模型自我评估。
> - 机制解读：这与 §2.1 失效四机制完全一致——自评是"影子的影子"，不携带新信息。**"验证必须独立"不是工程偏好，是实证规律。**

**实证锚点二（转述，待核验 ⚠️）**：
> Lance Martin 测试转述：Fable 5 最好运行 73% 结论过独立验证 vs Opus 4.7 中位数仅 17%。**原文链接未附，已尝试 Bing 检索（2026-08-18）未找到原文，数据口径（验证覆盖率 or 通过率）待核验**。机制解读：差距本质不是模型能力，是"验证是否作为一等公民内置"——73% = pipeline 内置独立验证器逐项对照证据；17% = 验证缺失或自评式。**模型自评宣布完成，中位数 <1/5 扛得住独立验证**。⚠️ 该数据引用时须标注"转述待核验"，不作为决策唯一依据。

---

## 3. 验证独立性四条件（可复用检查清单）

```
① context isolation: V's context excludes G's generation-process memory
   (cannot see 'what I just wrote')
② evidence anchoring: V must access external evidence E (real files/test
   results); conclusions anchored on E
③ falsification incentive: V's role is fail-finding, not pass-approving
④ no vested interest: V is not incentivized to defend P (no 'my output must
   not be wrong' burden)
```

- ①+② = 信息论条件；③+④ = 激励条件
- 只满足① = "换个视角的自评"（仍共享错误先验）
- 只满足② = "查作业"（仍放过系统性错误）
- **类比**：财务审计——职责分离（④）+ 证伪导向（③）+ 证据独立（②）
- **论文印证**：ICLR 2024 的结论 = ②缺失时①无效——没有外部证据锚点，再"独立"的自评也是闭路（[来源: arXiv:2310.01798]）

### 3.1 自审的正确用法：证据再注入，而非判断

自审不可靠（它是自评），但"强制逐项对照真实文件和测试结果"这个**动作**可靠——强制模型重新接触 E，打破"凭记忆复述"闭路。

```
❌ "please check if your output has issues"  -> closed-loop self-eval (model passes everything)
✅ "check item by item: output #N vs actual file content vs actual test results,
    list PASS/FAIL for each" -> forced evidence access (judgment delegated to evidence)
```

---

## 4. Loop 判据：「写清楚」的三层递进

| 层 | 问题 | 示例 | 能否支撑 loop |
|:---|:-----|:-----|:-------------|
| L1 写清楚 | 完成标准能被语言表达 | "文档写完、格式规范、链接有效" | ❌ 只是前提 |
| L2 能验证 | 完成标准有客观判据 | "doc-final-check.sh 全部 PASS" | ⚠️ 人能判，模型会自欺 |
| **L3 能自动验证** | 判据可被脚本/测试机械执行 | "check gates 0 失败 + 死链 0" | ✅ **loop 门槛** |

**关键**：Ralph 双条件退出门的 completion_indicators 是模型输出的自然语言（L2，不可靠）——ICLR 2024 已证无外部反馈的自评会退化（[来源: arXiv:2310.01798]），Lance Martin 转述更给出"中位数 <1/5 扛得住独立验证"的量化估计（⚠️ 转述待核验）。**真正可靠的退出门只有 L3**。

> **loop 适用 ⟺ 完成标准可被机械验证（L3）且验证成本 < 生成成本**

"写不清楚"（L1 不达）→ 一步步来。更隐蔽陷阱：**写清楚但只能人验（L2）**——每轮人盯，省下的重复劳动赔回人工审查。

---

## 5. Token 经济性：边际成本曲线与 loop 消耗结构

### 5.1 富人/穷人 = 边际成本曲线

- **富人** = 边际成本低（便宜模型、缓存命中高、本地推理、批量折扣）
- **穷人** = 边际成本高（贵模型、缓存频繁 miss、无本地算力）
- 同一 loop：富人是印钞机，穷人是焚化炉

### 5.2 Loop 的 token 消耗结构（Ralph 原文未系统化）

| 消耗项 | 触发 | 成本特征 | 穷人占比 |
|:-------|:-----|:---------|:--------:|
| 主循环生成 | 每轮产出 | 线性（每轮固定） | 基准 |
| 自修正 | 每轮自审+重写 | 生成 × 2~3 | ↑ |
| **验证子 agent** | 独立上下文复核 | **全量新计算，缓存必 miss** | ↑↑↑ 最贵 |
| 重试 | 验证失败回炉 | 生成 × N（不收敛指数） | ↑↑↑ |
| 上下文重注入 | 每轮 PROMPT.md | 线性小头 | ~ |

### 5.3 最尖锐矛盾

**独立验证最可靠（上下文隔离 → 条件独立）⟺ 缓存必然 miss（最烧钱）**。本地实测：缓存未命中占总成本 57.1%（最大单项）；8/17 新价生效后 flash miss 输入 1→1.5/3.0、输出 2→4.5/9.0，**同用量 +186%**。

**推论**：loop 账单里，验证子 agent 不是"额外开销"，是**可靠性的标价**。穷人抉择：省钱（合并上下文自评）→ 退回 ICLR 2024 证实的自评退化区；保可靠性（独立验证）→ 57.1% 成本项放大。

---

## 6. 决策矩阵：可验证性 × 经济性（2×2）

| | **token 富人**（边际成本低） | **token 穷人**（边际成本高） |
|:--|:--|:--|
| **L3 可自动验证** | ✅ 全自动 loop：脚本验证+可烧，`while :; do … done` 正解 | ⚠️ **节俭 loop**：验证用脚本/check gates（低成本背压），不上子 agent；caps + 预算硬约束 |
| **L2 仅人可验证** | ⚠️ 半自动 loop：每轮人审，loop 只省生成不省审查 | ❌ 别上：每轮人工 + 高 token，双倍亏损 |
| **L1 说不清** | ❌ 别上：无退出门 = token 黑洞 | ❌❌ 绝对别上：烧钱且永不收敛 |

**本地定位**：token 穷人（flash +186%，无本地算力可用）✅ 但验证体系全部 L3 且低成本 → **"穷人 + L3"象限，可上节俭 loop**。

---

## 7. 循环工程第六要素：经济性

Ralph 五要素（目标注入/外部状态/背压验证/退出条件/失败调优）缺现实维度。$10.42/hour 是 token 趋零时代的富人假设——穷人视角下经济性是独立要素：

> **⑥ 经济性：每轮预算上限 + 总预算上限 + 验证成本 < 生成成本门槛检查 + 缓存策略（复用 > 重算）。**
> 缺它：富人"浪费但有效"，穷人"烧穿但无效"。

**六要素 MECE**：前五管"能不能收敛"，第六管"烧不烧得起"。（建议并入 Ralph 文档 v3.0）

---

## 8. 本地落地三条军规

1. **验证用脚本不用子 agent**：背压谱系取"结构化 check gates"档，不轻易上"独立验证子 agent"档（除非关键产出）
2. **iteration caps + 预算硬约束**：Ralph 断路器——连续 N 次失败强制退出，防 token 黑洞
3. **启动前默认检查"验证成本 < 生成成本"**（背压经济性，Ralph §9.3）

**验证独立性落地自查**（pipeline-verification-loop）：

| 条件 | 本地现状 | 风险 |
|:-----|:---------|:-----|
| ① 上下文隔离 | ⚠️ 生成与验证常同轮同上下文 | 同一模型"生成+自检"= 自评陷阱 |
| ② 证据锚定 | ✅ check gates 对照真实文件/测试 | 良好 |
| ③ 证伪激励 | ⚠️ 自检 prompt 确认式而非找错式 | 模型倾向 PASS |
| ④ 无利益关联 | ⚠️ 无独立验证者角色 | 无外部审计 |

改进：验证轮与生成轮上下文隔离（新开轮、只注入产出+证据）；验证 prompt 改证伪式（"逐项列出 FAIL，找不到也要给证据链"）；高价值产出加独立上下文第二意见。

---

## 9. 数据缺口

| 缺口 | 说明 | 处置 |
|:-----|:-----|:-----|
| Lance Martin 73%/17% | 原文链接未附，口径（验证覆盖率 or 通过率）未核验 | ⚠️ 已尝试 Bing 检索（08-18）未果；待用户补充链接后核验归档 |
| 验证子 agent 成本量化 | 本地未实测独立验证轮的实际增量成本 | 可用 deepseek_usage 落盘数据补测 |
| ICLR 2024 具体下降幅度 | 论文指出自校正后性能下降，各基准具体数字未逐一摘录 | 需读原文附录补量化 |

---

## 10. 参考来源

| # | 来源 | 类型 | 日期 |
|:--|:-----|:-----|:-----|
| 1 | [Ralph Wiggum as a "Software Engineer"](https://ghuntley.com/ralph/)（Huntley, 2025-07） | 博客一手 | 2025-07 |
| 2 | [Everything is a Ralph Loop](https://ghuntley.com/loop/)（Huntley, 2026-01） | 博客一手 | 2026-01 |
| 3 | [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798)（Huang et al., ICLR 2024） | 论文一手 | 2024-03 |
| 4 | ralph-claude-code（frankbria，双条件退出门/断路器/限速） | 开源一手 | — |
| 5 | DeepSeek Harness 架构（Model-visible means logged / seam 三角色） | 知识库 | — |
| 6 | MEMORY.md 08-15 缓存成本实测 + 08-16/17 新价模拟 | 内部实测 | 08-15 |
| 7 | Lance Martin 测试（转述，待核验 ⚠️） | 转述 | — |

---

## 11. Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-17 | v2.0 | **质量提升**：①新增论文一手实证（ICLR 2024 自校正失败/性能退化，替代纯理论推导）；②Lance Martin 数据明确标注"转述待核验"+ 已尝试 Bing 检索说明；③参考来源升级为可溯源表（带链接/日期/类型）；④§3 补论文印证（②缺失时①无效）；⑤数据缺口更新（ICLR 具体下降幅度待摘录） |
| 2026-08-17 | v1.0 | 初稿。命题「验证必须独立」+「loop 判据」+「token 经济性」三合一。新增：失效四机制（信息论条件独立表述）、验证独立性四条件、L1/L2/L3 三层递进、loop token 消耗结构表、可验证性×经济性 2×2 矩阵、循环工程第六要素（经济性） |
