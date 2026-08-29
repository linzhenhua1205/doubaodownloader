---
name: tech-learn
description: Extract reusable patterns from sessions and save them as candidate skills or guidance. Use when: (1) user asks to save knowledge from a session, (2) user wants to document a workaround/solution, (3) user wants to create a reference for future use, (4) 知识提取、模式保存、经验总结、最佳实践. Do NOT use for: trivial fixes, one-time issues, simple syntax errors.
metadata:
  requires:
    bins: ["python3"]
  emoji: 📚
---

# 技术学习技能 (Tech Learn)

## 概述

本技能用于**从会话中提取可复用模式并保存为候选技能或指导**。基于 ECC-main 的 learn.md 模板，将解决的非平凡问题转化为可复用的知识。

**核心原则**: 学完就记是本能，不要"记在心里"——文件才会在会话重启后保留。

---

## 提取框架

### 提取类型

| # | 类型 | 描述 | 示例 |
|:-:|:-----|:-----|:-----|
| 1 | **Error Resolution Patterns** | 错误解决模式 | 内存泄漏检测方法 |
| 2 | **Debugging Techniques** | 调试技巧 | 非明显调试步骤 |
| 3 | **Workarounds** | 变通方案 | 库缺陷、API 限制 |
| 4 | **Project-Specific Patterns** | 项目特定模式 | 代码库约定、架构决策 |

### 提取标准

**提取**:
- 解决的非平凡问题
- 可复用的模式/技巧
- 能在未来会话中节省时间的知识

**不提取**:
- 琐碎修复（拼写错误、简单语法错误）
- 一次性问题（特定 API 宕机等）
- 无复用价值的一次性操作

---

## 提取工作流

```
1️⃣ 审查会话 → 2️⃣ 识别价值 → 3️⃣ 起草技能文件 → 4️⃣ 用户确认 → 5️⃣ 保存归档
```

### 第1步：审查会话

回顾当前会话，寻找可提取的模式：
- 解决了什么问题？
- 根因是什么？
- 如何修复的？
- 是否可复用？

### 第2步：识别价值

识别最有价值/最可复用的洞察：
- 这个模式能解决什么类型的问题？
- 适用场景是什么？
- 能节省多少时间？

### 第3步：起草技能文件

创建技能文件，格式如下：

```markdown
# [Descriptive Pattern Name]

**Extracted:** [Date]
**Context:** [Brief description of when this applies]

## Problem
[What problem this solves - be specific]

## Solution
[The pattern/technique/workaround]

## Example
[Code example if applicable]

## When to Use
[Trigger conditions - what should activate this skill]

## Key Insights
- [Insight 1]
- [Insight 2]

## References
- [Link to related knowledge]
```

### 第4步：用户确认

在保存前询问用户确认。

### 第5步：保存归档

保存到 `knowledge/` 目录，并更新：
- `knowledge/log.md` — 记录操作日志（用 `kb-log-append.py`；`index.md`/`README.md` 不手工更新，由脚本批量刷新）

---

## 提取示例

### 示例1：内存泄漏检测模式

```markdown
# Memory Leak Detection Pattern

**Extracted:** 2026-06-27
**Context:** Node.js 后端服务内存泄漏排查

## Problem
服务运行一段时间后内存持续增长，导致 OOM 崩溃。

## Solution
1. 使用 `node --inspect` 启动调试
2. 定期获取 heap snapshot
3. 比较 snapshots 识别增长对象
4. 使用 Chrome DevTools Memory 面板分析
5. 追踪对象引用链找到泄漏源头

## Example
```bash
# 启动调试
node --inspect=0.0.0.0:9229 server.js

# 使用 clinodeheapdump 获取快照
curl http://localhost:9229/api/heapdump
```

## When to Use
- 服务内存持续增长
- GC 频繁触发
- 响应时间逐渐变慢

## Key Insights
- 快照间隔应足够长（>1小时）才能看到明显泄漏
- 关注 detached DOM 节点和全局变量
- 使用 comparison view 排除正常增长

## References
- [Chrome DevTools Memory Guide](https://developer.chrome.com/docs/devtools/memory/)
```

### 示例2：并发安全模式

```markdown
# Concurrent Access Safety Pattern

**Extracted:** 2026-06-27
**Context:** Redis 并发操作导致数据不一致

## Problem
多个请求同时修改同一 Redis key，导致数据覆盖丢失。

## Solution
使用 Redis Lua 脚本保证原子性：
```lua
-- 原子性递增并获取值
local current = redis.call('GET', KEYS[1])
if current then
    current = tonumber(current) + 1
else
    current = 1
end
redis.call('SET', KEYS[1], current)
return current
```

## When to Use
- 多个进程/线程并发修改同一资源
- 需要保证操作的原子性
- CAS（Compare-And-Swap）场景

## Key Insights
- Redis Lua 脚本在执行期间不会被中断
- 避免使用 GET + SET 组合
- 对于复杂操作，考虑使用分布式锁

## References
- [Redis Lua Scripting](https://redis.io/docs/interact/programmability/lua-scripts/)
```

---

## 命令接口

### `/tech-learn:extract` — 从会话提取模式

```bash
# 语义任务：分析当前会话提取模式（由 LLM 完成），再用 learn-manager save 持久化
python3 <base_dir>/scripts/tools/learn-manager.py save <pattern_name> --desc "<模式描述>"
```

分析当前会话并提取可复用模式。

### `/tech-learn:save` — 保存提取的模式

```bash
python3 <base_dir>/scripts/tools/learn-manager.py save <pattern_name> --desc "<模式描述>"
```

保存指定模式到知识库。

### `/tech-learn:list` — 列出已提取的模式

```bash
python3 <base_dir>/scripts/tools/learn-manager.py list
```

列出已提取并保存的所有模式。

---

## 质量评分体系

| # | 评分维度 | 检查项 | 权重 |
|:-:|:---------|:-------|:-----|
| 1 | **复用价值** | 是否真的能在未来节省时间 | 30% |
| 2 | **问题描述** | 问题描述是否具体清晰 | 25% |
| 3 | **解决方案** | 方案是否完整可操作 | 20% |
| 4 | **示例质量** | 示例是否有代表性 | 15% |
| 5 | **文档规范** | 是否符合 changelog/TOC/来源标注规则 | 10% |

**评分等级**：
- **优（85+）**: 可直接使用
- **良（70-84）**: 可使用，建议小修
- **需改进（50-69）**: 需重大修改
- **不合格（<50）**: 需重写