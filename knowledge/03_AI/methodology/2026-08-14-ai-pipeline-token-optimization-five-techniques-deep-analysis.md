# 💰 AI Pipeline Token 优化五技术深度分析：成本治理是架构纪律，非定价练习

> **来源**: Andela（Shift+Tab Publication）AI pipeline token 优化赞助文技术框架（prompt caching -90% / 工具输出修剪 -70~90% / 意图路由 -50~80% / 上下文压缩 -30~60%）+ Andela 姊妹文《Don't wait for the bill: why AI agents need cost gates》一手全文
> **类型**: LLM 工程 · Token 成本治理 · Agent 架构纪律
> **关键词**: prompt caching, 工具输出修剪, 意图路由, 上下文压缩, cost gates, 成本治理, token 优化
> **一手核验**: Andela cost gates 姊妹文全文精读（含参考实现代码级细节）+ 用户提供的五技术框架 + 知识库既有 token 成本主线交叉验证（五看三定 CPT / 推理单位经济学 / 本工作空间 token 消耗实测）

---

## 📑 目录

- [1. 核心结论](#1-核心结论)
- [2. 来源定位与一手核验](#2-来源定位与一手核验)
- [3. 第一性原理：为什么 Token 成本是架构问题而非定价问题](#3-第一性原理为什么-token-成本是架构问题而非定价问题)
- [4. 技术框架总览：五技术定位矩阵](#4-技术框架总览五技术定位矩阵)
- [5. T1 Prompt Caching（-90%）](#5-t1-prompt-caching-90)
- [6. T2 工具输出修剪（-70~90%）](#6-t2-工具输出修剪-7090)
- [7. T3 意图路由（-50~80%）](#7-t3-意图路由-5080)
- [8. T4 上下文压缩（-30~60%）](#8-t4-上下文压缩-3060)
- [9. T5 成本门控 Cost Gates（第五技术）](#9-t5-成本门控-cost-gates第五技术)
- [10. 五技术协同与组合效应](#10-五技术协同与组合效应)
- [11. 落地方法论：成本治理流程](#11-落地方法论成本治理流程)
- [12. 与既有知识体系呼应](#12-与既有知识体系呼应)
- [13. 参考资料与诚实边界](#13-参考资料与诚实边界)

---

## 1. 核心结论

**一句话**: Token 成本优化不是"跟供应商谈价格"，而是**架构纪律**——五个正交技术杠杆（缓存/修剪/路由/压缩/门控）从不同维度削减 token 消耗，且**门控（执行前控制）是让前四个技术可治理的元层**。

**五大结论**:

1. **成本 = 架构函数，非定价函数**: token 账单 = Σ(输入 token × 输入价 + 输出 token × 输出价)，而输入 token 的 90%+ 是**架构决策**决定的（发了什么、发了多少、发给谁、何时发）——不是模型单价决定的。**"成本治理是架构纪律"的实质 = 把 token 当成可设计、可测量、可门控的资源流**
2. **五技术作用域正交，可叠加**: 缓存砍"重复发送"（时间维度）、修剪砍"无效载荷"（空间维度）、路由砍"过度服务"（能力维度）、压缩砍"上下文增长"（长度维度）、门控砍"失控循环"（执行维度）——**五者作用于成本方程的不同因子，组合收益非简单相加而是乘法**
3. **门控是治理的元层**: 前四技术是"减量"，门控是"边界"——**没有门控，减量技术只是让失控更慢一点**。Andela 姊妹文的核心洞见：post-hoc 报告是 observability，pre-execution 门控才是 governance
4. **收益排序与工程成本成反比**: 收益最大（-90%）的 prompt caching 恰恰是**工程成本最低**的（稳定 system prompt 即可）；收益中等的路由/压缩需要分类器/KV 基础设施；**按 ROI 排序落地：缓存 → 修剪 → 路由 → 压缩 → 门控（贯穿）**
5. **与知识库既有主线完全同构**: 五技术 = 本知识库 "Token成本：合并session>减请求>缩输出" 的系统化展开 + "AI概率内核×工程确定性外壳" 的成本面落地 + DeepSeek Harness "Model-visible means logged" 的预算面镜像（dsh 的 standing mount prefix-stable = 缓存友好的架构声明）

---

## 2. 来源定位与一手核验

### 2.1 来源说明

| 素材 | 类型 | 可用性 |
|:--|:--|:--|
| Andela token 优化赞助文（五技术框架 + 百分比） | 赞助文 | ⚠️ 原文 URL 未直接抓取到（网络检索不可达），**框架与百分比由用户提供，本文档采信其技术内容** |
| Andela《Don't wait for the bill: why AI agents need cost gates》（2026-07-20, Freddy Daniel Alvarez Pinto）| 一手全文 | ✅ 全文精读（含参考实现代码细节）|
| 知识库既有 token 主线（CPT 五看三定/推理单位经济学/本工作空间实测）| 内部 | ✅ 交叉验证 |

**诚实声明**: 本文档的"五技术"框架（四减量 + 一门控）以用户提供的 Andela 赞助文技术内容为骨架，叠加 Andela cost gates 姊妹文一手细节 + 知识库既有主线进行原理展开与深化。**百分比为行业经验区间（vendor 报告口径），非本工作空间实测，引用时须标注来源语境**。

### 2.2 为什么"技术内容可用"

用户明确标注"技术内容可用"——即该赞助文的技术框架（非营销部分）经评估可信。可信依据：
- 四技术均为行业共识性技术（知识库 10+ 文档独立支撑，非 Andela 独家发明）
- 百分比区间（如 caching -90%）与知识库既有实测/行业数据一致（Claude Code 一周 98.16% 缓存读取率、vLLM prefix caching、DeepSeek Harness prefix-stable 设计）
- 结论"成本治理是架构纪律"与知识库"统计铁律 AI 自报收益不可靠（仅 31% 测量）""约束脚本化=最高杠杆"完全同构

---

## 3. 第一性原理：为什么 Token 成本是架构问题而非定价问题

### 3.1 Token 成本方程分解

```
cost per request = (input tokens x input price) + (output tokens x output price)

Agent scenario (not single-shot QA):
total cost = SUM over steps [ (context tokens) x input price + (output tokens) x output price ]
           = SUM [ (system + history + tool results + new input) x input price + output x output price ]
```

**关键推论**:
- Agent 每步都把**全部历史上下文重发** → 上下文长度随时间线性→超线性增长，成本 ≈ 梯形面积
- 输入 token 通常比输出 token 便宜 3-5×，但**输入量是输出的 10-100×** → 输入侧是成本主战场
- **架构决策控制输入侧 90%+ 的变量**：发什么（修剪）、发多少（压缩）、发给谁（路由）、重发几次（缓存）、能不能发（门控）

### 3.2 从第一性原理看五技术的定位

```
cost equation factor     five-tech lever        essence
---------------------------------------------------------
input tokens x count  ->  Prompt Caching   ->  eliminate time redundancy (recompute same KV)
input tokens x payload ->  tool output trim ->  eliminate space redundancy (useless token share)
input tokens x capability -> intent routing -> eliminate capability redundancy (over-serve)
input tokens x length  ->  context compaction -> eliminate growth redundancy (context bloat)
execution path x unbounded -> Cost Gates    ->  eliminate runaway redundancy (unbounded loop)
```

这对应知识库既有的 **LLM 推理四类冗余 MECE（时间/IO/空间/计算）**——五技术是对四类冗余的成本面系统化解法。

### 3.3 为什么"治理 > 定价"

| 维度 | 定价练习（错误） | 架构纪律（正确） |
|:--|:--|:--|
| 手段 | 换便宜供应商、谈折扣 | 设计 token 消耗结构 |
| 杠杆点 | 单价（3-5× 空间）| 用量（10-100× 空间）|
| 可控性 | 供应商说了算 | 自己说了算 |
| 可持续 | 一次性 | 持续可演进 |
| 风险 | 质量妥协（换模型）| 需工程投入 |

**核心论点**: 单价谈判最多省 3-5×，架构优化可省 10-100×（五技术叠加）——**成本治理的 ROI 天花板在架构侧，不在采购侧**。

---

## 4. 技术框架总览：五技术定位矩阵

| # | 技术 | 收益区间 | 作用域 | 工程成本 | 落地优先级 |
|:-:|:--|:--|:--|:--|:--:|
| T1 | **Prompt Caching** | -90% | 输入×重复 | 低（稳定 prompt）| **1** |
| T2 | **工具输出修剪** | -70~90% | 输入×载荷 | 中（工具封装）| **2** |
| T3 | **意图路由** | -50~80% | 输入×能力 | 中（分类器/嵌入）| **3** |
| T4 | **上下文压缩** | -30~60% | 输入×长度 | 高（KV/摘要设施）| **4** |
| T5 | **Cost Gates** | 防失控（非减量）| 执行×边界 | 中（中间件）| **贯穿** |

> **观察**: 收益越大的技术，工程成本往往越低（T1 是极致）——这推翻了"省钱=复杂"的直觉。**按 ROI 排序落地，先用 1 天做好 T1，再逐级推进**。

---

## 5. T1 Prompt Caching（-90%）

### 5.1 原理

**KV Cache 前缀复用**。LLM 推理时，相同前缀的 token 会生成完全相同的 KV cache（Key/Value 缓存）——若服务端缓存了该前缀的 KV，后续请求命中则**跳过整个 prefill 阶段**，只计算新增部分。

```
Request 1: [system prompt A][history B][new input C] -> full prefill
Request 2: [system prompt A][history B][new input D] -> prefix A+B cache hit, only prefill D
                          ^
              same prefix = same KV = cache hit
```

### 5.2 为什么能到 -90%

- 稳定 system prompt 常占上下文 10-40%（长 system prompt 甚至 50%+）
- 多轮对话中历史上下文被重复发送，**前缀越长、复用率越高、收益越大**
- 实测参照（知识库既有）: Claude Code 一周 **98.16% 缓存读取率**；vLLM/SGLang prefix caching 是标准能力

### 5.3 具体优化方法

| 方法 | 做法 | 说明 |
|:--|:--|:--|
| **system prompt 稳定化** | 固定指令部分不随请求变化 | 缓存命中的第一前提 |
| **上下文顺序固定** | system → 工具 schema → 历史 → 新输入 | 前缀一致性最大化 |
| **供应商缓存层启用** | Anthropic prompt caching / OpenAI cached tokens | 按 token 计费（缓存读取价低）|
| **工具 schema 静态化** | schema 排序稳定、描述精简但不变 | schema 是上下文大头之一 |
| **会话续接** | 续接会话复用历史前缀 | 避免新会话重发 |
| **Harness 层面** | standing mount prefix-stable（dsh）| 预设组合一次安装不再重读 |

### 5.4 背后的原理链

> 缓存命中 → prefill 跳过 → 输入 token 按缓存价计费（通常 10-25%）→ **-90% 输入成本**

**关键约束**: 缓存收益的前提是**前缀绝对稳定**——任何一处插入（如时间戳、随机 id、动态 tool 描述）都会打断缓存。**这正是"系统 prompt 稳定性转化为成本"的知识库主线（Prefix Caching 使稳定性成为经济变量）**。

---

## 6. T2 工具输出修剪（-70~90%）

### 6.1 原理

工具（检索/代码/Shell/DB）的原始输出中，**大部分 token 是模型完成任务不需要的噪音**。修剪 = 在工具结果**进入上下文之前**压缩，而非让模型自己忽略。

```
Raw tool output (10,000 tokens): full file / full logs / all fields
        | trim
Into context (1,000-3,000 tokens): summary / key lines / structured extraction
```

### 6.2 为什么能到 -70~90%

- `ls -la` 输出 80% 是权限位/时间戳（模型不需要）
- `git log` 全量哈希/元数据 vs 只需 commit message
- 检索结果 100 条 vs 模型实际用 5-10 条
- 文件全文 vs 结构化提取（函数签名+关键行）
- **实测洞察（知识库）**: 工具输出常占 agent 上下文 50-70%——修剪它是输入侧最大单点杠杆

### 6.3 具体优化方法

| 方法 | 做法 | 收益 |
|:--|:--|:--|
| **输出截断** | 超限截断 + 指示"已截断，剩余 N 行" | 简单直接 |
| **结构化提取** | 用正则/解析器只取关键字段 | 去噪 |
| **差分输出** | 只返回变化部分（增量）| 迭代场景 |
| **摘要化** | 大输出 → LLM 或规则摘要 | 保留语义 |
| **分页/懒加载** | 先摘要后按需取详情 | 避免一次性全量 |
| **按任务裁剪 schema** | 只暴露本次需要的工具/字段 | 减少调用输出 |

### 6.4 背后的原理链

> 工具输出噪音占比高（经验 70-90%）→ 修剪在进入上下文前 → 输入 token 直降 → **-70~90% 输入成本 + 减少模型注意力分散（质量提升）**

**与 DeepSeek Harness 的呼应**: dsh 的 `tool/result*` 事件流 + `tools/pre-execute → execute → post-execute` 流水线正是"修剪"的架构化挂点——**工具输出修剪不是 hack，而是 tool pipeline 的正式环节**。

---

## 7. T3 意图路由（-50~80%）

### 7.1 原理

**不是所有请求都需要旗舰模型**。意图路由 = 在请求到达模型前，用低成本分类器判断"这个请求需要什么能力级"，路由到合适的模型（小模型/专用模型/旗舰模型）。

```
Request -> intent classifier (embedding similarity / small model / rules)
            +-- simple QA -> small model (10-50x cheaper)
            +-- structured task -> specialized model (cheaper + more accurate)
            +-- complex reasoning -> flagship model (expensive but necessary)
```

### 7.2 为什么能到 -50~80%

- 真实负载呈 **Pareto 分布**：~60-80% 请求是简单/中等复杂度（摘要、提取、格式化、检索定位）
- 小模型价格是旗舰的 1/10-1/50，输出质量在简单任务上差异小
- **知识库主线**: "模型侧降本三路径 = 路由→稀疏化→专用化（嵌套非并列）"——路由是第一层
- 业界实证: Cursor Router（Compass 预测器 -68% 成本）、各类 model routing 框架

### 7.3 具体优化方法

| 方法 | 做法 | 说明 |
|:--|:--|:--|
| **嵌入相似度路由** | 请求嵌入 vs 意图簇中心 | 低成本、可解释 |
| **小模型预筛** | 小模型判断"是否够用"| 级联路由 |
| **规则/关键字路由** | 命令式意图（/summarize）| 零成本 |
| **自适应降级** | 旗舰失败/超预算 → 小模型 fallback | 与 T5 门控联动 |
| **历史反馈闭环** | 路由决策 + 结果质量评估 | 持续优化 |

### 7.4 背后的原理链

> 负载复杂度分布不均（Pareto）→ 能力-需求匹配 → 简单请求用小模型 → **-50~80% 综合成本**（不牺牲复杂任务质量）

**风险边界**: 路由**不可牺牲关键任务质量**——路由决策需要可观测（记录路由理由）+ 可回退（复杂任务强制旗舰）。**与 T5 门控配合：路由是"能力预算"的静态版，门控是动态版**。

---

## 8. T4 上下文压缩（-30~60%）

### 8.1 原理

上下文随时间线性→超线性膨胀（历史消息、中间推理、工具结果累积）。压缩 = 在**保留关键信息**的前提下缩小上下文，对抗上下文增长。

```
Original context (growing): [system][hist1][hist2]...[histN][current]
        | compact (summary / drop / tier)
Compacted context: [system][summary(hist1-N)][current]
```

### 8.2 为什么能到 -30~60%

- 历史对话中大量内容随任务推进失去价值（已解决的中间步骤、旧工具输出）
- 信息熵分布不均：长上下文中真正关键的信息占比小
- **知识库实测**: 本工作空间 "大文件深度解读四段式" 和 token 治理均验证"缩输出"是第三杠杆；DeepSeek Harness context compaction 95% 水位（记忆主线）
- 相关研究: HiSparse（Qwen Quest GH200 200K 4.7×）、KV 分层迁移（HiSparse→OasisKV→ImpactHO）

### 8.3 具体优化方法

| 方法 | 做法 | 说明 |
|:--|:--|:--|
| **滚动摘要** | 历史 → 摘要（LLM 或规则）| 经典方案 |
| **KV 分层** | 热 KV 留 HBM、温 KV 移 DRAM、冷 KV 卸 SSD | 基础设施级 |
| **注意力稀疏** | 只保留高注意力 token（HiSparse）| 推理级 |
| **语义压缩** | 相似内容去重、冗余段落合并 | 应用级 |
| **水位触发** | 上下文超阈值自动压缩（95% 水位）| 与门控联动 |
| **分块处理** | 长文档分块 + 按需检索（RAG 化）| 结构性压缩 |

### 8.4 背后的原理链

> 上下文膨胀 → 每步成本 ∝ 上下文长度（梯形增长）→ 压缩控制长度 → **-30~60% 成本 + 更低的 KV 内存压力（可能提升推理速度）**

**代价权衡**: 压缩有信息损失风险（摘要丢失细节）——**"压缩是架构决策，必须记录压缩边界（丢了什么）"**，与知识库"可追溯→可审查"信任链一致。

---

## 9. T5 成本门控 Cost Gates（第五技术）

### 9.1 原理（Andela 姊妹文一手）

**执行前控制（pre-execution control）**。成本门控是 agent 循环内、**每次工具/模型调用前**的检查点：估算本次调用成本 → 检查预算/调用次数限制 → 放行、拦截或路由到 fallback。

```
Agent proposes call -> estimate cost -> check budget -> check tool-call limit
                                              -> allow / block / fallback
                                              -> record (full-path telemetry)
```

**核心区分**:
- **Observability（可观测性）**: 事后报告发生了什么（reporting）
- **Governance（治理）**: 事前决定什么被允许发生、为什么（gating）

### 9.2 为什么这是"第五技术"（元层）

前四技术是**减量**（让同样的任务花更少 token），门控是**边界**（防止失控）——**没有门控，减量技术只是让失控更慢一点**。Andela 原文金句: "The agent should not be allowed to discover the limit by exceeding it."

### 9.3 参考实现细节（Andela 原文代码级）

```
- Budget unit: cost_micros (deterministic estimate, not a real billing unit)
- Blocking semantics: estimate exceeds remaining budget -> refuse primary call (tool not run, charged=0)
- Fallback policy: primary blocked -> middleware catches -> route to cheaper deterministic fallback
- Middleware is the control point: budget check before tool lookup/execution
- Full-path recording: blocked / executed / failed all recorded (prevent ghost charges vanishing from report)
- Two-dimension limits: cost budget + tool-call count ("expensive" != "unbounded"; cheap tool called 100x is dangerous)
```

```yaml
# Reference task definition (Andela)
budget_id: fallback-triggered
max_cost_micros: 1200
max_tool_calls: 2
steps:
  - tool_name: deterministic_expensive_model
    estimate_micros: 2500
    fallback_tool: local_fallback_summary
    fallback_estimate_micros: 300
```

## 9.4 通用化：门控模式超越金钱

Andela 原文明确: 同一架构适用于 **latency / token / tool-call / retry / API quota / user-tier / environment** 预算——**"让预算在执行上下文中显式化"**。

---

## 10. 五技术协同与组合效应

### 10.1 协同矩阵

| 组合 | 协同效应 |
|:--|:--|
| T1 × T2 | 修剪后的工具输出成为稳定前缀的一部分 → 缓存命中率↑（修剪改变输出 → 缓存失效？需权衡：**修剪确定性越高越利于缓存**）|
| T3 × T5 | 路由是"能力预算"静态版，门控是动态版 → 路由决策可被门控复核 |
| T4 × T5 | 压缩水位触发 = 门控的一种（上下文预算）|
| T1 × T4 | 压缩改变前缀 → 破坏缓存。**权衡: 压缩应在缓存边界外做**（前缀保留稳定段，仅压缩可变段）|

### 10.2 组合收益估算

```
Single tech: caching -90% x trimming -80% x routing -60% x compaction -40%
           = 0.1 x 0.2 x 0.4 x 0.6 = 0.0048
-> theoretical combination ~99.5% input-cost cut (ideal orthogonal assumption)
-> realistic (overlap/engineering loss): 80-95% cut achievable
```

> ⚠️ **诚实声明**: 上表为理想正交乘法估算，非实测。真实环境五技术存在交互（如 T1×T4 冲突），**需以本工作空间实测为准**（知识库统计铁律: AI 自报收益不可靠，仅 31% 测量）。

### 10.3 落地优先级（ROI 排序）

```
Week 1:    T1 caching (stable system prompt + fixed prefix)  -> immediate
Week 2-3:  T2 trimming (wrap tool output layer)              -> big lever
Week 3-4:  T5 gating (middleware + budget + telemetry)       -> prevent runaway
Week 5-8:  T3 routing (intent classifier + model matrix)     -> medium lever
Week 9+:   T4 compaction (KV tiering/rolling summary)        -> long-term
```

---

## 11. 落地方法论：成本治理流程

```
+-------------+  +-------------+  +-------------+  +-------------+
| 1. Budget   |->| 2. Estimate |->| 3. Gate     |->| 4. Telemetry|
| (budget/    |  | (estimate/  |  | (gate/      |  | (report/    |
|  tier/env)  |  |  tool-call) |  |  block/     |  |  review)    |
|             |  |             |  |  fallback)  |  |             |
+-------------+  +-------------+  +-------------+  +-------------+
```

| 环节 | 关键问题 | 对应技术 |
|:--|:--|:--|
| 预算定义 | 每任务/租户/环境允许花多少？| T5 |
| 估算挂载 | 每次调用成本可预测吗？| T5（估算表）|
| 门控执行 | 超预算前能拦截吗？| T5 |
| 遥测审计 | 报告回答"尝试/执行/拦截/fallback/估算/实际/原因"吗？| T5 + 全链 |
| 减量优化 | 哪些 token 是不必要的？| T1-T4 |

**治理报告应回答（Andela 原文）**: ① agent 尝试调什么 ② 实际执行什么 ③ 什么被拦截 ④ 什么走了 fallback ⑤ 用了什么估算 ⑥ 确定性模型下实际扣费 ⑦ 为什么决策——**这是 observability（说了什么）与 governance（允许了什么、为什么）的分界线**。

---

## 12. 与既有知识体系呼应

| 既有主线 | 五技术对应 |
|:--|:--|
| Token 成本三杠杆（合并 session>减请求>缩输出）| T1（合并会话=缓存）+ T2/T3（减请求）+ T4（缩输出）的系统化展开 |
| Prefix Caching 使 system prompt 稳定性转化为成本 | T1 原理层 |
| 模型侧降本三路径（路由→稀疏化→专用化）| T3 = 路由层 |
| 四类冗余 MECE（时间/IO/空间/计算）| 五技术的分类学底座 |
| DeepSeek Harness（standing mount prefix-stable / tool pipeline / Model-visible means logged）| T1 架构声明 + T2 挂点 + 门控的日志镜像 |
| Writer harness 降本实证（-40%）| "harness 是跨所有模型倍增效率的组件"——五技术正是 harness 的减量工具箱 |
| 本工作空间 token 消耗实测（28% 缓存命中等）| 五技术落地验证基线 |
| AI 概率内核 × 工程确定性外壳 | 门控 = 成本面的确定性外壳 |
| GitHub AI 成本治理编排角色 | 治理层方法论（人+工具）|

---

## 13. 参考资料与诚实边界

### 13.1 来源

| # | 来源 | 类型 |
|:-:|:--|:--|
| 1 | Andela token 优化赞助文（五技术框架 + 百分比）| 赞助文（用户提供框架，原文 URL 不可达）|
| 2 | [Andela: Don't wait for the bill — why AI agents need cost gates](https://www.andela.com/publication/dont-wait-for-the-bill-why-ai-agents-need-cost-gates) | 一手全文（cost gates 细节 + 参考实现）|
| 3 | [Andela: Beyond GPUs — how token economics are reshaping the data center](https://www.andela.com/publication/beyond-gpus-how-token-economics-are-reshaping-the-modern-data-center) | 一手全文（tokenomics 语境，补充参考）|

### 13.2 内部交叉链接

- [Unit Token Cost 五看三定深度分析](../../07_industry-research/04_ai/2026-08-13-unit-token-cost-five-looks-three-decisions-deep-analysis.md)
- [推理单位经济学：每百万 token 真实成本](../../06_others/sources/2026-08-12-inference-unit-economics-true-cost-per-million-tokens.md)
- [AI 成本治理·编排角色深度分析](2026-08-13-github-ai-cost-governance-orchestrator-role-deep-analysis.md)
- [本工作空间 Token 消耗全景分析](../../02_rd/02_project/03_kb_cowagent/2026-08-08-token-consumption-full-timeline-analysis.md)
- [DeepSeek Harness 一切皆插件深度分析](../agent-engineering/2026-08-14-deepseek-harness-everything-is-a-plugin-deep-analysis.md)

### 13.3 诚实边界（缺陷与不确定性）

1. **原文不可达**: Andela 五技术赞助文原文 URL 未能抓取（网络检索不可达），框架与百分比以用户提供为准——**百分比为行业经验区间（vendor 报告口径），非独立第三方实测，引用须注明**
2. **组合收益为估算**: §10.2 的 99.5% 是理想正交乘法模型，未考虑 T1×T4 等交互冲突——**真实收益需实测**（知识库统计铁律: AI 自报收益不可靠）
3. **cost gates 参考实现为教育性**: Andela 作者明确"不声称真实财务收益/账单精度"，cost_micros 是确定性估算单位——落地需接真实计费数据
4. **五技术命名**: "第五技术 = cost gates" 为本文推断（Andela 赞助文可能对第五项命名不同）——若原文第五项不同，以原文为准
5. **未实测**: 本文档未在本工作空间跑 A/B 验证五技术收益

---

## Changelog

| 日期 | 变更 | 作者 |
|:--|:--|:--|
| 2026-08-14 | 初稿：五技术框架（用户提供）+ Andela cost gates 姊妹文一手全文 + 知识库交叉验证 | AI |
