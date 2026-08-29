# Lowfreq 机制评估与解决方案：技能注入优先级分级的成本-可用性权衡

> **类型**: 方案文档 | **日期**: 2026-08-14（v1.0）→ 2026-08-18（v2.0 全面升级）| **状态**: v2.0 提交评审，**待人工决策**
> **决策入口**: 本文档输出方案与决策矩阵，人工评估确认后再决定是否实施
> **v2.0 升级**: 补外部数据源（Anthropic Context Engineering / Lost in the Middle）+ 完整 MECE 决策矩阵 + 同类机制对照案例 + 量化测算细化
> **相关**: [Token 每轮消耗源清单](2026-08-14-token-per-turn-source-inventory-sourcecode-audit.md) · [工程规模评估全谱系](2026-08-14-engineering-scale-assessment-full-spectrum-plan.md) · [Token 优化五技术](2026-08-14-ai-pipeline-token-optimization-five-techniques-deep-analysis.md) · [上下文污染与重复执行](2026-08-14-context-pollution-repeat-execution-analysis.md)

---

## 📑 目录 (TOC)

- [结论先行（四点）](#结论先行四点)
- [1. 现状调查（源码 + 磁盘实证）](#1-现状调查源码--磁盘实证)
  - [1.1 加载机制（CowAgent 源码）](#11-加载机制cowagent-源码)
  - [1.2 磁盘实测（2026-08-14）](#12-磁盘实测2026-08-14)
  - [1.3 量化：token 收益上限](#13-量化token-收益上限)
- [2. 价值论证：收益端 / 成本端 / 机会成本](#2-价值论证收益端--成本端--机会成本)
  - [2.1 收益端（极薄）](#21-收益端极薄)
  - [2.2 成本端（沉重）](#22-成本端沉重)
  - [2.3 机会成本（关键洞察）](#23-机会成本关键洞察)
- [3. 外部对照：行业如何治理技能/工具注入膨胀](#3-外部对照行业如何治理技能工具注入膨胀)
  - [3.1 Anthropic：工具集膨胀是最常见失败模式](#31-anthropic工具集膨胀是最常见失败模式)
  - [3.2 Lost in the Middle：注入量越大，注意力稀释越严重](#32-lost-in-the-middle注入量越大注意力稀释越严重)
  - [3.3 三级对照：业界方案与本系统现状映射](#33-三级对照业界方案与本系统现状映射)
- [4. 解决方案（三案 + 推荐 + MECE 决策矩阵）](#4-解决方案三案--推荐--mece-决策矩阵)
  - [4.1 方案 A：软二级化（推荐）](#41-方案-a软二级化推荐)
  - [4.2 方案 B：分组注入（中期）](#42-方案-b分组注入中期)
  - [4.3 方案 C：动态索引（终极，暂缓）](#43-方案-c动态索引终极暂缓)
  - [4.4 三方案 MECE 对比矩阵](#44-三方案-mece-对比矩阵)
- [5. 决策点清单（人工评估）](#5-决策点清单人工评估)
- [6. 数据与证据](#6-数据与证据)
- [Changelog](#changelog)

---

## 结论先行（四点）

1. **lowfreq 机制实际未生效**——`tmp/lowfreq/` 里 22 个技能是 6 月的**过期副本**，而 `skills/` 里同名 22 个技能依然存在且全量注入 desc。省 token 目标**零实现**，只留下了 22 个陈旧备份 + 认知混淆 [来源: 磁盘实测 2026-08-14]。

2. **即使按原设想"物理移走"，收益也极小**——22 个技能 desc 压缩后仅 ~658 tokens/轮，占固定系统提示词 5%、占整轮成本 ~2%。**代价却是 22 个技能从注册表消失、功能不可用**。收益/代价严重失衡 [来源: §1.3 测算]。

3. **用户判断正确**："从 skills 的使用机制看上去价值不大"——且机制设计有更优解：**软二级化**（保留可用性，只降注入优先级），而非物理移出。这与 Anthropic 官方对工具集治理的建议方向一致：**最小可行工具集 + 元数据（名称+触发词）按需展开**，而非物理删除 [来源: Anthropic Context Engineering, 2025-09-29]。

4. **注意力的真实瓶颈在别处**：Lost in the Middle 研究证明，模型对长上下文中段信息的利用能力显著劣化 [来源: arXiv:2307.03172]——**技能 desc 从 3,204 tok 压到 2,750 tok 只省 14% 技能块，但把"低频技能"降级为极简清单，能同时改善注意力分配**（少 22 条 desc 挤占注意力预算），这是物理移走方案不具备的隐性收益。

---

## 1. 现状调查（源码 + 磁盘实证）

### 1.1 加载机制（CowAgent 源码）

```
SkillManager(custom_dir=workspace/skills/)     [agent_initializer.py:480]
  +-- refresh_skills()                         [manager.py:49]
  |    +-- loader.load_all_skills(builtin, custom)  <- scans skills/ only, NOT tmp/lowfreq/
  |    +-- _sync_skills_config()               <- removes skills missing on disk from cfg
formatter.format_skills_for_prompt(skills)     [formatter.py:95]
  +-- all enabled skills' desc compressed into system prompt
  |    +-- _condense_description_for_prompt()  <- ~300 chars -> ~100-200 keyword level
  +-- full SKILL.md read on demand (only after selection)
```

**关键结论**：
- 技能加载路径 = `workspace/skills/` **单目录**
- `tmp/lowfreq/` **不在扫描路径** → 其中的技能永远不会被加载
- desc 已压缩注入（非全文）——省 token 的收益**大部分已被 formatter 实现**
- **认知混淆成本**：`tmp/lowfreq/` 与 `skills/` 重名副本长期共存，任何人（含 AI）在排查时都可能误读目录结构

### 1.2 磁盘实测（2026-08-14）

| 位置 | 技能数 | 状态 |
|:-----|:------:|:-----|
| `skills/`（实际加载） | **104** | 含 22 个"低频"技能，全部注册注入 |
| `tmp/lowfreq/`（未被加载） | **22** | 6 月副本，与 skills/ 重名 |
| `skills_config.json` | 104 条 | 全部 enabled，包含 22 个低频名 |

**重名验证**：`skills/` 与 `tmp/lowfreq/` 有 **22 个同名目录** → lowfreq 不是"移走"而是"复制"（移走失败/被还原）。

**内容漂移证据**：

| 技能 | skills/ SKILL.md | lowfreq/ SKILL.md | 时间戳 |
|:-----|:-----------------|:------------------|:-------|
| light-typesetting | `6a4c2097` | `1d098ff2` ❌ | skills/ 08-14 更新 |
| thesis-helper | `64882c38` | `64882c38` ✅ | — |
| xlsx | `0f7b2727` | `e6dfd717` ❌ | skills/ 08-14 更新 |

→ `tmp/lowfreq/` 是 **6 月旧版备份**，与现行版本已有漂移。若误从 lowfreq 恢复会得到过时技能 [来源: 磁盘 hash 实测]。

### 1.3 量化：token 收益上限

| 指标 | 值 | 占比 |
|:-----|:---|:-----|
| 104 技能 desc 压缩后 | 9,612 字符 ≈ **3,204 tok** | 固定 prompt 12.5K 的 25.7% |
| 22 个"低频"技能 desc | 1,974 字符 ≈ **658 tok** | 固定 prompt 的 5.3% |
| 整轮成本（12.5K + 历史 19.2K） | ~31.7K tok | — |
| **物理移走的理论节省** | **658 tok/轮** | **整轮 ~2.1%** |

> 即使完美实施"物理移走"，每轮也只省 2.1% token。而代价是 22 个技能功能消失 [来源: 源码级 token 审计，见关联文档]。

---

## 2. 价值论证：收益端 / 成本端 / 机会成本

### 2.1 收益端（极薄）

- 理论最大节省：658 tok/轮 = 整轮 2.1%
- 实际节省：**0**（机制未生效，技能仍在注入）
- 边际收益递减：desc 已被 formatter 压缩（3,204 tok 是压缩后），再砍 658 属"压无可压"的末位优化

### 2.2 成本端（沉重）

| 成本 | 说明 |
|:-----|:-----|
| **功能不可用** | 22 个技能从注册表消失，模型不知其存在 → 用户要排版/写专利/画图时，Agent 用通用工具硬做，质量下降 |
| **关键技能误伤** | 名单里含**关键时刻刚需**技能：image-generation（出图）、frontend-design（前端）、light-figure-drawing（画图）、xlsx（表格）、light-typesetting（排版）、thesis-helper（论文）、patent-disclosure-writer（专利）——这些低频但**高价值** |
| **维护分裂** | 技能拆两个目录 → 更新时改哪份？副本漂移（已发生：light-typesetting/xlsx） |
| **恢复成本** | 需要时要从 lowfreq 手工搬回 + 刷新 cfg，反模式 |

### 2.3 机会成本（关键洞察）

省 token 的正解**已经存在于机制内**：
- formatter 压缩 ✅ 已实现（desc ~300字→~150字）
- 全文按需 read ✅ 已实现（SKILL.md 不注入）
- `unavailable_skills` 机制 ✅ 已实现（requires 不满足的技能只给 setup 提示）

lowfreq 的"移走"思路与这套机制**重复且冲突**——它在 formatter 已经压过的基础上，用"物理消失"换 5% 固定成本，得不偿失。

---

## 3. 外部对照：行业如何治理技能/工具注入膨胀

### 3.1 Anthropic：工具集膨胀是最常见失败模式

Anthropic 在《Effective context engineering for AI agents》（2025-09-29）中明确指出 [来源: Anthropic 官方博客]：

> "One of the most common failure modes we see is **bloated tool sets** that cover too much functionality or lead to ambiguous decision points about which tool to use. If a human engineer can't definitively say which tool should be used in a given situation, an AI agent can't be expected to do better."

**Anthropic 的治理方向**（与本系统 lowfreq 设想同源但不同解）：
1. **最小可行工具集（minimal viable set）**：不是"全部注入"，而是"只注入必要工具"，且**宁可维护更少但更清晰的工具**
2. **工具元数据按需展开**：工具/技能只保留"轻量标识符"（名称+用途），运行时按需加载——即"just-in-time"策略
3. **工具输出 token 效率**：工具返回信息必须 token 高效——对应本系统 formatter 的 desc 压缩

**对照结论**：Anthropic 反对的是"**模糊决策点的膨胀**"（工具太多且边界不清），解决方案是**分层/按需**，**从未建议物理删除工具**——与本系统方案 A（软二级化）方向一致，与"物理移走"方向相悖。

**例子**：Claude Code 的 CLAUDE.md 采用"naive 注入 + 按需探索"混合策略——`CLAUDE.md` 文件直接注入上下文（高频），而 `glob/grep` 等原语让 Agent **按需检索**文件（低频内容不注入）[来源: Anthropic Context Engineering]。这正是"高频全量 + 低频按需"的工程实例——lowfreq 想做的事，Anthropic 用"索引式检索"实现了。

### 3.2 Lost in the Middle：注入量越大，注意力稀释越严重

Stanford/UC Berkeley 研究（Liu et al., 2023, TACL）实证 [来源: arXiv:2307.03172]：

- 在**多文档问答**与**键值检索**两类任务上，模型对上下文**中段**信息的利用显著劣化
- 性能在"相关信息位于开头/结尾"时最高，**位于中段时显著下降**（即使对长上下文模型）
- 推论：**系统提示词里塞的 desc 越多，每条 desc 的"被注意概率"越低**——多注入 22 条低频技能 desc 不是"免费背景"，而是**在稀释所有技能的注意力权重**

**对照结论**：物理移走 vs 软二级化的差异不仅是 token 数量，更是**注意力分配**：
- 物理移走：22 条 desc 消失 → 其余 82 条注意力集中（但 22 个技能不可用）
- 软二级化：22 条 desc 变极简清单（~10-15 tok/条）→ 注意力损失小 + 可用性保留
- **"移走"省的是 token，"分级"省的是注意力**——后者是 Lost in the Middle 研究的直接应用

### 3.3 三级对照：业界方案与本系统现状映射

| 层级 | 业界方案 | 代表实现 | 本系统对应 | 状态 |
|:-----|:---------|:---------|:-----------|:----:|
| L1 压缩 | desc 精简注入 | Anthropic 工具文档规范 | formatter 压缩 | ✅ 已实现 |
| L2 按需 | 轻量标识 + 运行时加载 | Claude Code CLAUDE.md + glob/grep | 全文按需 read | ✅ 已实现 |
| L3 分级 | 高频全量 / 低频极简 | Claude Code 混合注入 | **方案 A（未实施）** | ⚠️ 缺口 |

**结论**：本系统已实现 L1/L2，唯一缺口是 **L3 分级**——这正是方案 A 的价值：补齐行业最佳实践的最后一层，而不是重复 L1/L2。

---

## 4. 解决方案（三案 + 推荐 + MECE 决策矩阵）

### 4.1 方案 A：软二级化（推荐 ⭐）

**思路**：技能**物理保留**在 `skills/`，用配置字段降注入优先级——低频技能只注入"名称+关键词"，命中后按需 read 全文。

```
before (current): <available_skills> injects 104 desc (3,204 tok)
after:
  <available_skills>       <- level=1 skills desc (82 items, 2,546 tok)
  <lowfreq_skills>         <- level=2 minimal list (22 name+keywords, ~200 tok)
    note: low-frequency but usable; when keywords match user need,
          read the SKILL.md via read tool before use
```

**实施步骤**：
1. `skills_config.json` 为 22 个低频技能加 `"level": 2`（默认 1）——数据标注，不动目录
2. `formatter.py` 增加分级逻辑：level=2 技能走极简模板（name + 首条触发关键词，单行 ~10-15 tok/个）
3. system prompt 技能节增加一行 lowfreq 使用说明（~50 tok）
4. `tmp/lowfreq/` 22 个过期副本 → 按铁律 mv 至 `tmp/bak/lowfreq-20260814/`（确认 skills/ 版为最新后）

**收益**：3,204 → ~2,750 tok/轮（省 ~450 tok，14% 技能块 / 3.6% 固定）+ 注意力分配改善（22 条 desc 降为极简清单）
**代价**：改 formatter ~40 行 + config 标注 + 清理副本；可用性 **100% 保留**
**风险**：低（纯增量字段，兼容旧 config）

**例子（触发路径）**：用户在对话中提出"帮我排版这篇论文到 IEEE 模板"→ 模型从极简清单识别 `light-typesetting`（命中关键词"排版/论文/IEEE"）→ read 其 SKILL.md 全文 → 按技能流程执行。**功能完整保留，只是触发路径从"全量注入"变为"关键词命中→按需加载"**——与 Claude Code 的 `glob/grep` 按需探索同构。

### 4.2 方案 B：分组注入（中期）

在 A 基础上，按 `category` 分场景组（research/writing/coding/data/competition/…），系统提示词只注入"高频组全量 + 其他组 name-only"。104 个技能需先打 category 标签（一次性成本 ~30 分钟），且需要**使用频率数据**支撑分组（当前无埋点）。

**适合**：技能数继续增长（>150）或引入使用统计后。

### 4.3 方案 C：动态索引（终极，暂缓）

system prompt 不注入任何 desc，只注入"技能索引路径"（skills/README.md），模型每轮先 read 索引再决策。省全部 3,204 tok，但**每轮多 1-2 次工具调用**（read 索引），且模型少一次"全局感知"。

**适合**：技能 >150 个或 desc >5K tok 时启用。当前 104 个/3.2K tok 未到阈值。

### 4.4 三方案 MECE 对比矩阵

| 维度 | A 软二级化 | B 分组注入 | C 动态索引 |
|:-----|:----------|:----------|:----------|
| **省 token** | ~450 tok（14% 技能块） | ~800-1,000 tok | ~3,204 tok（100%） |
| **可用性保留** | ✅ 100% | ✅ 100%（组内） | ✅ 100%（索引可查） |
| **注意力改善** | 中（22 条降级） | 高（组外极简） | 最高（全极简） |
| **工程成本** | 低（formatter ~40 行） | 中（打标签 30min + 埋点） | 中（索引维护 + 每轮 read） |
| **每轮新增开销** | ~50 tok 说明 | ~50 tok 说明 | +1-2 次工具调用 |
| **依赖数据** | 无（人工圈定 22 个） | 需要使用频率埋点 | 无 |
| **演进风险** | 低（增量字段） | 中（组划分需重调） | 中（丢全局感知） |
| **落地时间** | 1-2 小时 | 1-2 天 | 1 天 |

**选择逻辑**：C 的省 token 最多但引入每轮工具调用 + 丢全局感知（Lost in the Middle 的"索引检索"替代"全量注入"是终极形态，但当前 3.2K tok 未到阈值）；B 依赖埋点数据；**A 是当前 ROI 最高且与 Anthropic 最佳实践对齐的增量改造**。

---

## 5. 决策点清单（人工评估）

| # | 决策项 | 选项 | 建议 |
|:-:|:-------|:-----|:-----|
| D1 | `tmp/lowfreq/` 22 个过期副本 | a) 归档到 bak b) 保留 | **a)**（已确认 skills/ 为最新，副本有漂移风险） |
| D2 | 是否实施方案 A（软二级化） | a) 实施 b) 暂缓 | 若追求极致轻量（低 bit 本地模型）→ **a)**；否则可先只做 D1 |
| D3 | 22 个低频名单是否合理 | 重新评估 | **建议修正**：image-generation/frontend-design/light-figure-drawing/xlsx/light-typesetting 属"低频但刚需"，考虑留在 level=1 |
| D4 | 是否引入使用频率埋点 | a) 埋点 b) 不埋 | 若实施 B → a)；否则 b)（避免过度工程） |

**我的倾向**：D1 立即做（清理过期副本，消除漂移风险）；D2 视 token 压力决定——当前整轮成本大头在历史回读（19.2K）而非技能 desc（3.2K），**先解决历史窗口问题（ROI 更高），技能二级化排后**。D3 需要修正名单——22 个里至少 7 个是"低频但刚需"，不能一锅端降级。

---

## 6. 数据与证据

- 源码：`agent_initializer.py:480`（custom_dir=skills/）、`agent/skills/manager.py:49-55`（refresh）、`agent/skills/formatter.py:95-129`（desc 压缩注入）、`agent/skills/loader.py:222-249`（扫描路径）
- 实测：skills/ 104 目录 vs tmp/lowfreq/ 22 目录，22 个重名；SKILL.md hash 漂移（light-typesetting/xlsx）；desc 字符统计（9,612/1,974）
- 外部源：Anthropic《Effective context engineering for AI agents》(2025-09-29)；Liu et al.《Lost in the Middle》(TACL 2023, arXiv:2307.03172)；Anthropic《Building Effective AI Agents》(2024-12-19)
- 关联：`knowledge/03_AI/methodology/2026-08-14-token-per-turn-source-inventory-sourcecode-audit.md`（技能 desc 2,981 tok 审计）、`2026-08-14-engineering-scale-assessment-full-spectrum-plan.md`（L1 轻量化方案）

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-14 | v1.0 | 初版，lowfreq 机制现状调查 + 价值论证 + 三方案 + 决策点 |
| 2026-08-18 | v2.0 | **全面升级**：补外部数据源（Anthropic Context Engineering 工具集膨胀治理/Lost in the Middle 注意力稀释）+ §3 三级对照（业界方案与本系统映射）+ §4.4 三方案 MECE 对比矩阵 + 触发路径例子 + D3 名单修正建议 |
