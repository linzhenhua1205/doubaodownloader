---
name: tech-evolve
description: Analyze instincts and suggest or generate evolved structures (commands, skills, agents). Use when: (1) user wants to extract patterns from conversations, (2) user wants to create new skills/commands/agents from repeated patterns, (3) user wants to evolve existing workflows, (4) 模式提取、技能进化、命令生成、工作流优化. Do NOT use for: one-time tasks, trivial fixes.
metadata:
  requires:
    bins: ["python3"]
  emoji: 🦋
---

# 技术进化技能 (Tech Evolve)

## 概述

本技能用于**分析会话模式并生成进化结构**。基于 ECC-main 的 evolve.md 模板，将重复的模式和直觉进化为可复用的命令、技能和代理。

**核心价值**: 从重复工作中提取模式，自动化并固化为可复用的技能。

---

## 进化框架

### 进化类型

| 类型 | 定义 | 触发条件 |
|:-----|:-----|:---------|
| **Command（命令）** | 用户显式调用的操作 | 多个直觉描述"当用户要求..." |
| **Skill（技能）** | 自动触发的行为 | 模式匹配触发器、错误处理响应 |
| **Agent（代理）** | 复杂多步骤流程 | 需要深度/隔离的调试、重构、研究任务 |

### 进化规则

#### → Command（用户调用）

当直觉描述用户会明确请求的操作时：
- 多个直觉关于"when user asks to..."
- 直觉有"when creating a new X"这样的触发器
- 直觉遵循可重复的序列

**示例**:
- `new-table-step1`: "when adding a database table, create migration"
- `new-table-step2`: "when adding a database table, update schema"
- `new-table-step3`: "when adding a database table, regenerate types"

→ 创建: **new-table** 命令

#### → Skill（自动触发）

当直觉描述应该自动发生的行为时：
- 模式匹配触发器
- 错误处理响应
- 代码风格强制

**示例**:
- `prefer-functional`: "when writing functions, prefer functional style"
- `use-immutable`: "when modifying state, use immutable patterns"
- `avoid-classes`: "when designing modules, avoid class-based design"

→ 创建: `functional-patterns` 技能

#### → Agent（需要深度/隔离）

当直觉描述复杂多步骤流程时：
- 调试工作流
- 重构序列
- 研究任务

**示例**:
- `debug-step1`: "when debugging, first check logs"
- `debug-step2`: "when debugging, isolate the failing component"
- `debug-step3`: "when debugging, create minimal reproduction"
- `debug-step4`: "when debugging, verify fix with test"

→ 创建: **debugger** 代理

---

## 进化工作流

```
1️⃣ 检测项目上下文 → 2️⃣ 读取直觉 → 3️⃣ 分组聚类 → 4️⃣ 识别候选 → 5️⃣ 生成文件
```

### 第1步：检测项目上下文

识别当前项目类型、技术栈、现有技能和命令。

### 第2步：读取直觉

读取项目级和全局级直觉（项目级优先）。

### 第3步：分组聚类

按触发器/领域模式分组直觉：

| 聚类维度 | 说明 |
|:---------|:-----|
| **触发器模式** | 什么条件触发这个直觉 |
| **领域** | 属于哪个技术领域（前端、后端、测试等） |
| **置信度** | 直觉的置信度评分 |
| **作用域** | 项目级还是全局级 |

### 第4步：识别候选

识别：
- **Skill 候选**: 2+ 直觉的触发聚类
- **Command 候选**: 高置信度工作流直觉
- **Agent 候选**: 更大的高置信度聚类

### 第5步：生成文件

如果传递 `--generate`，写入文件到：
- 项目范围: `skills/evolved/`
- 全局回退: `skills/evolved/`

---

## 输出格式

### 分析输出

```
============================================================
  EVOLVE ANALYSIS - 12 instincts
  Project: my-app
  Project-scoped: 8 | Global: 4
============================================================

High confidence instincts (>=80%): 5

## SKILL CANDIDATES
1. Cluster: "adding tests"
   Instincts: 3
   Avg confidence: 82%
   Domains: testing
   Scopes: project

## COMMAND CANDIDATES (2)
  /adding-tests
    From: test-first-workflow [project]
    Confidence: 84%

## AGENT CANDIDATES (1)
  adding-tests-agent
    Covers 3 instincts
    Avg confidence: 82%
```

### 生成文件格式

#### Command

```markdown
---
name: new-table
description: Create a new database table with migration, schema update, and type generation
command: /new-table
evolved_from:
  - new-table-migration
  - update-schema
  - regenerate-types
---

# New Table Command

## Steps
1. ...
2. ...
```

#### Skill

```markdown
---
name: functional-patterns
description: Enforce functional programming patterns
evolved_from:
  - prefer-functional
  - use-immutable
  - avoid-classes
---

# Functional Patterns Skill

[Generated content based on clustered instincts]
```

#### Agent

```markdown
---
name: debugger
description: Systematic debugging agent
model: sonnet
evolved_from:
  - debug-check-logs
  - debug-isolate
  - debug-reproduce
---

# Debugger Agent

[Generated content based on clustered instincts]
```

---

## 命令接口

### `/tech-evolve:analyze` — 分析直觉并建议进化

```bash
# 语义任务（设计承诺，脚本待建）：分析所有直觉并建议进化方向，由 LLM 完成
# 替代: 直接调用 tech-evolve 技能流程（分析→建议），无需脚本
```

分析所有直觉并建议进化方向。

### `/tech-evolve:generate` — 分析并生成进化文件

```bash
# 语义任务（设计承诺，脚本待建）：分析直觉并生成进化文件，由 LLM 完成
# 替代: 按 tech-evolve 流程用 write 工具生成 skills/evolved/ 下文件
```

分析直觉并生成进化文件到 `skills/evolved/` 目录。

### `/tech-evolve:promote` — 提升项目级直觉到全局

```bash
# 语义任务（设计承诺，脚本待建）：提升项目级直觉到全局，由 LLM 完成
# 替代: 按 profile-optimizer 流程合并至 MEMORY.md/技能库
```

将项目级直觉提升为全局直觉。

---

## 质量评分体系

| # | 评分维度 | 检查项 | 权重 |
|:-:|:---------|:-------|:-----|
| 1 | **模式识别** | 是否准确识别重复模式 | 30% |
| 2 | **分类准确性** | 是否正确分类为 Command/Skill/Agent | 25% |
| 3 | **置信度评估** | 是否基于置信度筛选候选 | 20% |
| 4 | **生成质量** | 生成的文件是否完整可用 | 15% |
| 5 | **文档规范** | 是否符合 changelog/TOC/来源标注规则 | 10% |

**评分等级**：
- **优（85+）**: 可直接使用
- **良（70-84）**: 可使用，建议小修
- **需改进（50-69）**: 需重大修改
- **不合格（<50）**: 需重写