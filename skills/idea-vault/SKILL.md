---
name: idea-vault
description: "Idea 暂存与管理（先暂存、后提取）。当用户提出想法/点子/灵感（尤其是知识库建设、系统改进、研究方向、待验证判断），或说'先记录下来''这个事值得研究''形成专题''先缓一缓'时使用。核心原则：idea 不直接写成正式知识库文档，先记入 knowledge/06_others/ideas/ 暂存区（与 sources 平级），保留内容记录+挖掘线索+待办+资源关系，格式从简；待挖掘成熟后再提取为正式文档。Use when: (1) 用户说'有个想法/idea/点子' (2) 用户要求'先记录下来再说' (3) 讨论产生新方向但尚未成体系 (4) 需要盘点/回顾已记录的 ideas (5) 需要把 idea 提取为正式知识库文档。"
---

# Idea Vault — Idea 暂存与管理

## 核心原则（为什么存在）

**Idea 不直接进知识库正式区。** 正式知识库文档要求 TOC/交叉链接/溯源/changelog，对未成熟的想法是沉重负担，且会把"点子"误当成"结论"固化下来（本工程已有教训：宏观化专题、AI认知专题都是直接写成正式文档，后被用户纠正应先暂存）。

Idea 区与正式区的分工：

| | Idea 暂存区 (`06_others/ideas/`) | 正式知识库 (各模块) |
|:--|:--|:--|
| 目的 | 快速捕获、不丢想法 | 沉淀可复用、可追溯的结论 |
| 格式 | 从简（无 TOC/changelog 要求） | 严格（TOC/交叉链接/溯源/changelog） |
| 状态 | draft/exploring/extracted/archived | 无状态，默认有效 |
| 生命周期 | 可更新、可废弃、可提取 | 一经入库即长期有效 |

## 暂存区

- 路径：`knowledge/06_others/ideas/`（与 `sources/` 平级，2026-08-06 建立）
- 命名：`YYYY-MM-DD-<kebab-slug>.md`
- 一个 idea 一个文件；同一讨论产生的多个 idea 可合并记录，但每个 idea 要有独立小节

## 记录模板（最小骨架，格式从简）

```markdown
# <Idea 标题>

> **状态**: draft | exploring | extracted | archived
> **来源**: <讨论/会话/链接/日期>
> **类型**: <知识库建设 | 系统改进 | 研究方向 | 待验证判断 | 记录归档>

## 内容记录
<原始想法，允许口语化、允许不完整；保留关键原话>

## 相关信息挖掘
<已知线索：相关文档/目录/技能/数据，可先列占位待补>

## 待办
- [ ] <事项>

## 周边资源关系
<关联的 knowledge 文档、skills、脚本、目录；用相对路径>

## 演化记录（可选）
- YYYY-MM-DD: 创建 / 补充 / 提取为 <正式文档路径>
```

## 状态流转

```
draft（刚捕获，想法未验证）
  ↓ 补充信息/找到关联资源
exploring（正在挖掘）
  ↓ 挖掘成熟，可成体系
extracted（已提取为正式文档；原文件保留并链接到正式文档）
  ↓ 确认无价值/被替代
archived（移入 06_others/oldbak/ 或标注废弃）
```

## 提取为正式文档的触发条件

满足任一即可提取（否则留在暂存区）：
1. 有明确结论 + 可验证的数据/来源支撑
2. 形成了可复用的方法/框架/专题
3. 用户明确要求"写成正式文档/专题"

提取动作：
1. 按 knowledge-wiki 规范创建正式文档（TOC/溯源/changelog/交叉链接）
2. 更新 idea 文件状态为 `extracted`，在演化记录中链接正式文档
3. 追加 `knowledge/log.md`（`kb-log-append.py`）——**不更新** `index.md` / `README.md`（脚本批量刷新）

## 同步义务（每次写入/变更 idea 文件后）

1. `knowledge/log.md` 对应日期分节追加一行（用 `kb-log-append.py`；`index.md`/`README.md` 不手工更新，由脚本批量刷新）
2. 当日记忆 `memory/YYYY-MM-DD.md` 记录本次 idea 捕获

## 与其他技能的分工

- **light-idea-generation**：生成新 idea（本技能不生成，只存储管理）
- **light-idea-critique**：按顶会标准批判 idea 是否成立（本技能不评判，只记录）
- **knowledge-wiki**：正式文档写入规范（idea 提取为正式文档时调用）
- **session-intent-analysis / conversation-topic-analyzer**：从历史会话挖掘 idea（挖掘线索可回填到 idea 文件）
- **light-memory-pm**：长期项目背景记忆（idea 属知识库层，不占 memory）

## 使用示例

**捕获**：用户说"我觉得 AI 挖掘能力不行，值得研究" →
1. 判断为 idea（未成体系）→ 不写正式文档
2. 在 `06_others/ideas/` 建 `2026-08-06-<slug>.md`，按模板记录
3. 追加 log.md / 当日记忆（index 由脚本批量刷新）

**提取**：挖掘成熟（如业界做法调研完成、优化方案验证）→
1. 创建正式文档（如 `05_tools/` 下方法论）
2. idea 文件状态改 `extracted` + 链接正式文档
3. 追加 log.md（index 由脚本批量刷新）
