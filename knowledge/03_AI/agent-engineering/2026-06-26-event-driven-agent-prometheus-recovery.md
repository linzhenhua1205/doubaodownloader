# Event-Driven Agent 实战：Prometheus 告警 → LLM → Tool Calling → 自动恢复

> **概要**: Prometheus 告警到 LLM 到 Tool Calling 到自动恢复的 Event-Driven Agent 实战
>
> **关键词**: Event-Driven · AIOps · Prometheus · 告警 · 自动恢复

---

## 📑 目录

- [文章概要](#文章概要)
- [一、代码结构与核心文件](#一代码结构与核心文件)
  - [工具定义（tools.py）](#工具定义toolspy)
  - [执行链路](#执行链路)
- [二、Event-Driven vs ReAct 对比](#二event-driven-vs-react-对比)
  - [Event-Driven 最适合的告警场景](#event-driven-最适合的告警场景)
- [三、成熟的 AIOps Agent 架构分层](#三成熟的-aiops-agent-架构分层)
- [四、核心判断](#四核心判断)
- [关联归档](#关联归档)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 文章概要

使用 Python 实现一个极简的 Event-Driven Agent，展示 **Prometheus 告警 → 事件总线 → LLM 推理 → Tool Calling → 自动恢复** 的完整链路。核心观点：**Event-Driven 和 ReAct 不是二选一，而是在不同层面组合使用。** [来源: 1]

---

## 一、代码结构与核心文件

```text
+-- agent.py       # EventDrivenAgent 主逻辑（接收事件、调用 LLM、执行工具）
+-- event_bus.py   # 极简事件总线（Python queue.Queue 模拟消息队列）
+-- main.py        # 入口（事件循环 + 模拟 Prometheus 告警）
+-- tools.py       # 工具注册中心（3 个工具 + Tool Schema）
```

### 工具定义（tools.py）

| 工具 | 职责 | 模拟返回 |
|:-----|:------|:---------|
| `query_pod_status` | 查 Pod 状态 | `order-service 有 2 个 Pod CrashLoopBackOff` |
| `query_logs` | 查服务日志 | `数据库连接超时 timeout` |
| `restart_service` | 重启服务 | `order-service 已成功重启` |

工具注册到 `_TOOL_REGISTRY` 并生成 OpenAI Function Calling Schema。

### 执行链路

```text
模拟告警事件 -> event_bus(queue) -> agent.handle_event()
    -> LLM 推理（Thought -> Action）
    -> 调用工具（Observation）
    -> LLM 再推理 -> Final Answer
```

---

## 二、Event-Driven vs ReAct 对比

| 模式 | 关注点 | 典型链路 | 适合场景 | 主要风险 |
|:-----|:-------|:---------|:---------|:---------|
| **ReAct** | 边推理边行动 | Thought → Action → Observation → Final | 排障、检索、代码修改、需要不断补充事实的任务 | 循环不可控，工具调用次数和 token 成本易升高 |
| **Event-Driven** | 由事件触发处理 | Event → Queue → Handler → Tools → Result | **告警处理**、消息消费、工单流转、CI/CD、业务事件自动化 | 需处理幂等、重试、并发、审计和自动动作风险 |

### Event-Driven 最适合的告警场景

- Pod CrashLoopBackOff
- 磁盘使用率超过 90%
- 证书即将过期
- 任务执行失败
- 服务发布完成

---

## 三、成熟的 AIOps Agent 架构分层

```text
Prometheus 告警事件触发 Agent         <- Event-Driven（触发层）
v
Agent 先生成排查计划                   <- Plan-and-Execute（规划层）
v
执行过程中根据日志和指标不断调整判断     <- ReAct（推理执行层）
v
需要恢复动作时走审批或白名单             <- Guardrail（安全层）
v
输出结论并写入工单 / 通知群             <- Workflow（输出层）
```

核心洞察：**Event-Driven、ReAct、Plan-and-Execute 不是三选一，而是在不同层面组合使用。**

---

## 四、核心判断

1. **Event-Driven 是最适合告警处理的 Agent 模式**——天然由事件触发，无需轮询 [来源: 1]
2. **成熟的 AIOps Agent 需要三层模式组合**：Event-Driven（触发）+ Plan-and-Execute（规划）+ ReAct（执行调整）
3. 自动恢复动作必须配 **Guardrail**（审批或白名单），否则自动化风险大于收益 [来源: 2]
4. 与 [事件墙归档](../../05_tools/observability/2026-06-18-event-wall-root-cause-analysis.md) 互补——事件墙解决**定位**（发生了什么变化），Event-Driven Agent 解决**响应**（怎么自动修复）

> **实证锚点**：事件驱动的自动恢复本质是"循环直到达成停止条件"（Loop until done）在运维域的实例化——监控事件持续流入、Agent 重复执行"诊断→修复→验证"直到告警消除。安全侧需同步考虑：自动动作的 Guardrail 与 CaMeL 的 capability 机制同构（工具调用前按来源/权限强制策略，防止恢复动作被注入内容劫持）[来源: 2][来源: 3]。

---

## 关联归档

- [事件墙为什么重要：根因定位不是查指标，而是找到'刚才变了什么'](../../05_tools/observability/2026-06-18-event-wall-root-cause-analysis.md)
- [GEPA 架构拆解：让 Prompt 和 Skill 优化不靠玄学](../../07_industry-research/18_methodology-framework/2026-06-26-gepa-architecture.md)

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [事件墙归档](../../05_tools/observability/2026-06-18-event-wall-root-cause-analysis.md) — 关联
- [GEPA 架构拆解：让 Prompt 和 Skill 优化不靠玄学](../../07_industry-research/18_methodology-framework/2026-06-26-gepa-architecture.md) — 关联

### 外部资料引用

- 来源: [博客园 - it排球君](https://www.cnblogs.com/MrVolleyball/p/20486368) | **归档**: 2026-06-18 | **标签**: `#Event-Driven` `#ReAct` `#AIOps` `#Agent` `#自动运维` `#Prometheus告警
- Debenedetti et al., [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813), arXiv:2503.18813, 2025 — Guardrail/capability 机制基准（AgentDojo 77% vs 84%）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-08-18 | v1.1 | 质量提升：正文补 3 处行内来源标注 + Loop-until-done/Guardrail 实证锚点 |
| 2026-07-24 | v1.0 | 初始版本 |
