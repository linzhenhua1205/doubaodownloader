---
name: tech-planner
description: Create comprehensive implementation plans for technical features and refactoring. Use when: (1) user asks to plan a new feature, (2) user wants to refactor code, (3) user needs architectural changes, (4) requirements are complex or ambiguous, (5) 技术规划、实现计划、架构设计、功能开发. Do NOT use for: trivial changes, bug fixes without design implications.
metadata:
  requires:
    bins: ["python3"]
  emoji: 📋
---

# 技术规划技能 (Tech Planner)

## 概述

本技能用于**创建技术功能和重构的综合实现计划**。基于 ECC-main 的 plan.md 和 prp-plan.md 模板，结合用户项目的深度技术分析需求。

**核心哲学**: 一份优秀的计划包含实现所需的所有信息，无需进一步提问。

**黄金法则**: 如果在实现过程中需要搜索代码库，现在就把这些知识捕获到计划中。

---

## 规划框架

### 规划阶段

```
Phase 0: DETECT  →  Phase 1: PARSE  →  Phase 2: EXPLORE  →  Phase 3: RESEARCH
     ↓                    ↓                    ↓                    ↓
 确定输入类型        提取需求               探索代码库             研究外部技术
     ↓                    ↓                    ↓                    ↓
 Phase 4: DESIGN  →  Phase 5: ARCHITECT  →  Phase 6: GENERATE
     ↓                    ↓                    ↓
 设计UX转换          定义架构方法           生成完整计划文档
```

### 复杂度评估

| 级别 | 指标 | 典型范围 |
|:-----|:-----|:---------|
| **Small** | 单个文件，孤立变更，无新依赖 | 1-3 文件，<100 行 |
| **Medium** | 多个文件，遵循现有模式，次要新概念 | 3-10 文件，100-500 行 |
| **Large** | 横切关注点，新模式，外部集成 | 10+ 文件，500+ 行 |
| **XL** | 架构变更，新子系统，需要迁移 | 20+ 文件，考虑拆分 |

---

## 详细规划步骤

### Phase 0: DETECT — 确定输入类型

| 输入模式 | 检测方式 | 操作 |
|:---------|:---------|:-----|
| 以 `.prd.md` 结尾的路径 | PRD 文件路径 | 解析 PRD，查找下一个待处理阶段 |
| 包含 "Implementation Phases" 的 `.md` 文件 | PRD 类文档 | 解析阶段，查找下一个待处理阶段 |
| 其他文件路径 | 参考文件 | 读取文件获取上下文，作为自由形式处理 |
| 自由形式文本 | 功能描述 | 直接进入 Phase 1 |
| 空输入 | 无输入 | 询问用户要规划什么功能 |

### Phase 1: PARSE — 提取需求

#### 功能理解

从输入中识别：
- **What**: 正在构建什么（具体交付物）
- **Why**: 为什么重要（用户价值）
- **Who**: 谁使用它（目标用户/系统）
- **Where**: 它适合哪里（代码库的哪个部分）

#### 用户故事

格式：
```
As a [type of user],
I want [capability],
So that [benefit].
```

#### 模糊性检查

如果以下任何一项不明确，**停止并询问用户**：
- 核心交付物模糊
- 成功标准未定义
- 有多种有效解释
- 技术方法有重大未知

### Phase 2: EXPLORE — 探索代码库

#### 代码库搜索（8个类别）

| 类别 | 搜索内容 | 目的 |
|:-----|:---------|:-----|
| **Similar Implementations** | 类似现有功能 | 寻找类比模式 |
| **Naming Conventions** | 文件、函数、变量命名 | 识别命名规范 |
| **Error Handling** | 错误捕获、传播、日志 | 了解错误处理模式 |
| **Logging Patterns** | 日志级别、格式 | 识别日志规范 |
| **Type Definitions** | 类型、接口、模式 | 了解类型组织 |
| **Test Patterns** | 测试文件位置、命名、设置 | 了解测试模式 |
| **Configuration** | 配置文件、环境变量 | 识别配置规范 |
| **Dependencies** | 包、导入、内部模块 | 了解依赖关系 |

#### 代码库分析（5个追踪）

1. **Entry Points** — 请求/动作如何进入系统
2. **Data Flow** — 数据如何在相关代码路径中移动
3. **State Changes** — 什么状态被修改以及在哪里
4. **Contracts** — 必须遵守什么接口、API 或协议
5. **Patterns** — 使用什么架构模式（repository、service、controller 等）

#### 统一发现表

```markdown
| Category | File:Lines | Pattern | Key Snippet |
|:---------|:-----------|:--------|:------------|
| Naming | `src/services/userService.ts:1-5` | camelCase services, PascalCase types | `export class UserService` |
| Error | `src/middleware/errorHandler.ts:10-25` | Custom AppError class | `throw new AppError(...)` |
```

### Phase 3: RESEARCH — 研究外部技术

如果功能涉及外部库、API 或不熟悉的技术：
1. 搜索官方文档
2. 查找使用示例和最佳实践
3. 识别版本特定的陷阱

格式：
```
KEY_INSIGHT: [学到的内容]
APPLIES_TO: [计划的哪个部分受此影响]
GOTCHA: [任何警告或版本特定问题]
```

### Phase 4: DESIGN — 设计

#### UX 转换（如适用）

```markdown
**Before:**
```
┌─────────────────────────────┐
│  [Current user experience]  │
└─────────────────────────────┘
```

**After:**
```
┌─────────────────────────────┐
│  [New user experience]      │
└─────────────────────────────┘
```
```

#### 交互变更

| Touchpoint | Before | After | Notes |
|:-----------|:-------|:------|:------|

### Phase 5: ARCHITECT — 架构

#### 战略设计

定义实现方法：
- **Approach**: 高层策略
- **Alternatives Considered**: 评估过的其他方法及其被拒绝的原因
- **Scope**: 将构建的具体边界
- **NOT Building**: 明确列出范围外的内容

### Phase 6: GENERATE — 生成计划

#### 计划模板

```markdown
# Plan: [Feature Name]

## Summary
[2-3 句话概述]

## User Story
As a [user], I want [capability], so that [benefit].

## Metadata
- **Complexity**: [Small | Medium | Large | XL]
- **Estimated Files**: [count]

## Files to Change
| File | Action | Justification |
|:-----|:-------|:--------------|

## NOT Building
- [范围外项目 1]
- [范围外项目 2]

## Step-by-Step Tasks
### Task 1: [Name]
- **ACTION**: [做什么]
- **IMPLEMENT**: [具体代码/逻辑]
- **MIRROR**: [遵循的模式]
- **IMPORTS**: [所需导入]
- **GOTCHA**: [已知陷阱]
- **VALIDATE**: [验证方法]

## Testing Strategy
### Unit Tests
| Test | Input | Expected Output |

## Validation Commands
```bash
# 静态分析
[命令]
# 单元测试
[命令]
```

## Risks
| Risk | Likelihood | Impact | Mitigation |
|:-----|:-----------|:-------|:-----------|

## Acceptance Criteria
- [ ] 所有任务完成
- [ ] 所有验证命令通过
- [ ] 测试编写并通过
```

---

## 计划验证检查清单

### 上下文完整性
- [ ] 所有相关文件已发现并记录
- [ ] 命名规范已捕获示例
- [ ] 错误处理模式已记录
- [ ] 测试模式已识别
- [ ] 依赖已列出

### 实现准备
- [ ] 每个任务都有 ACTION、IMPLEMENT、MIRROR、VALIDATE
- [ ] 没有任务需要额外搜索代码库
- [ ] 导入路径已指定
- [ ] 已知问题已记录

### 模式忠实度
- [ ] 代码片段是实际代码库示例
- [ ] SOURCE 引用指向真实文件和行号
- [ ] 模式覆盖命名、错误、日志、数据访问和测试
- [ ] 新代码与现有代码无法区分

### 无先验知识测试
一个不熟悉此代码库的开发人员应该能够仅使用此计划实现功能，无需搜索代码库或提问。

---

## 命令接口

### `/tech-plan:init` — 初始化规划会话

```bash
python3 <base_dir>/scripts/tools/session-manager.py init plan:<规划名>
```

输出 JSON 格式的项目信息，呈现为确认草稿：
```
Here's what I found — confirm or edit anything:
Project:     <name>
Description: <description>
Stack:       <stack>
```

### `/tech-plan:save` — 保存规划进度

```bash
python3 <base_dir>/scripts/tools/session-manager.py save plan:<规划名>
```

保存当前规划进度到 `skills/tech-planner/sessions/` 目录。

### `/tech-plan:resume` — 恢复规划会话

```bash
python3 <base_dir>/scripts/tools/session-manager.py resume plan:<规划名>
```

恢复之前保存的规划会话。

---

## 质量评分体系

| # | 评分维度 | 检查项 | 权重 |
|:-:|:---------|:-------|:-----|
| 1 | **需求完整性** | 是否覆盖 What/Why/Who/Where | 25% |
| 2 | **代码库探索** | 是否覆盖8个搜索类别和5个追踪 | 25% |
| 3 | **计划可执行性** | 每个任务是否有 ACTION/IMPLEMENT/MIRROR/VALIDATE | 25% |
| 4 | **风险识别** | 是否识别关键风险并提供缓解措施 | 15% |
| 5 | **文档规范** | 是否符合 changelog/TOC/来源标注规则 | 10% |

**评分等级**：
- **优（85+）**: 可直接执行
- **良（70-84）**: 可执行，建议小修
- **需改进（50-69）**: 需重大修改
- **不合格（<50）**: 需重写