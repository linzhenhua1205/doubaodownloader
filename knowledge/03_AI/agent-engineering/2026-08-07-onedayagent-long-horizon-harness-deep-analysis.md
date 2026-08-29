# OneDayAgent：长时程 Harness 三重工程深潜——跨天任务的状态持久化、恢复与验证

> **统一主线**：长时程自主 Agent（跨天级任务）的可靠性不在模型而在 harness——OneDayAgent 用「任务分解 + 执行记忆 + 全局验证修复」三重工程把开放式请求变成可管理执行过程，在 AgentIF-OneDay 上以 GLM-5.2 后端拿下 SOTA 0.821；其「子任务状态传递」「压缩阈值化」「验证对照原始意图」设计与 08-05「Harness 即适配层/Agent 与 OS 进程边界同构」论断形成**实证呼应**。同日 Argus（2608.05144）把同一哲学推进到「verified pivoting」（证据门禁的目标修订），构成长时程 harness 的两条互补路线。

- **素材**：OneDayAgent 全文（arXiv 2608.05013v1，2331 行 HTML 一手，含附录 A-G 全部配置/成本/安全/prompt）+ Argus 全文（arXiv 2608.05144v1，834 行 HTML 一手）
- **日期**：2026-08-07 | **领域**：Agent 工程 / 长时程 Harness
- **姊妹篇**：[Harness 实证化四篇](2026-08-07-harness-empirical-four-papers.md)（Skill-Use 主分析）· [技能使用评测缺口](2026-08-07-skill-use-eval-gap-deep-analysis.md)（可测性）· [Harness 进程边界同构](2026-08-05-harness-os-process-boundary-isomorphism.md)（08-05 论断）

## TOC

1. [两篇全景：长时程 harness 的两条互补路线](#1-两篇全景长时程-harness-的两条互补路线)
2. [OneDayAgent 问题定义：三特征 → 三失败模式](#2-onedayagent-问题定义三特征--三失败模式)
3. [架构：从任务意图到交付物的受控流水线](#3-架构从任务意图到交付物的受控流水线)
4. [三重工程深潜：分解 / 记忆 / 验证](#4-三重工程深潜分解--记忆--验证)
5. [主结果与消融：验证模块是性价比之王](#5-主结果与消融验证模块是性价比之王)
6. [执行行为与后端分析：同 harness 不同执行风格](#6-执行行为与后端分析同-harness-不同执行风格)
7. [运行时成本与案例：经济性与修复闭环](#7-运行时成本与案例经济性与修复闭环)
8. [Argus 对比：verified pivoting 的另一条路线](#8-argus-对比verified-pivoting-的另一条路线)
9. [与 08-05 论断的实证呼应](#9-与-08-05-论断的实证呼应)
10. [Skill-Use 增量：技能可测性设计的第二维度](#10-skill-use-增量技能可测性设计的第二维度)
11. [批判性审视](#11-批判性审视)
12. [本系统启示](#12-本系统启示)
13. [预测 P1-P5](#13-预测-p1-p5)
14. [参考来源](#14-参考来源)

---

## 1. 两篇全景：长时程 harness 的两条互补路线

2026-08-04/05 两天内两篇长时程 harness 论文同时出现，代表两条互补路线：

| 维度 | OneDayAgent（2608.05013） | Argus（2608.05144） |
|:--|:--|:--|
| 机构 | 浙大 zjunlp + 蚂蚁 | 微软 + 上海交大等 10 机构 |
| 场景 | everyday tasks（工作/学习/生活） | 长时程研究（数学/芯片/论文） |
| 核心机制 | 分解 + 记忆 + 验证修复 | verified pivoting + 运行时自进化 |
| 目标修订 | 无（意图固定，验证修复交付物） | 允许（证据门禁下修订操作目标） |
| 状态模型 | 子任务 checkpoint + 上下文压缩 | 持久项目状态 + 角色门禁提交 |
| 基准 | AgentIF-OneDay（104 任务）SOTA 0.821 | SWE-Bench Pro 78% vs Copilot 59%（1.41× tokens） |
| 共同哲学 | **可靠性由 harness 承担，模型可换** | **可靠性由验证门禁承担，目标可改** |

**统一主线**：跨天任务的两个硬约束——**上下文装不下**、**目标会漂移**——都必须由 harness 在运行时层解决，而非靠模型 prompt。OneDayAgent 选择「压缩 + checkpoint + 验证修复」，Argus 选择「持久状态 + 证据门禁」。两条路线共享同一个第一性原理：**长时程可靠性 = 状态管理（确定性） + 验证门禁（确定性）包住概率性模型**。

---

## 2. OneDayAgent 问题定义：三特征 → 三失败模式

长时程 everyday 请求（如「调研主题 A，编辑 PPT，附图表，产出报告」）有三个特征：

1. **long-horizon**：跨很多推理-行动步保持目标与约束
2. **cross-environment**：网页 → 本地文件 → 代码执行 → 外部服务
3. **multimodal**：文本、文档、图像、表格、附件

三个特征产生三个执行失败模式：

- **目标漂移（goal drift）**：早期约束在后期步骤被遗忘（如先调研后编辑时丢掉早先的格式要求）
- **状态丢失（state loss）**：跨环境切换时中间状态无法传递（如搜索证据在切到文件环境后丢失）
- **上下文溢出（context overflow）**：可用上下文在交付物完成前耗尽

**关键洞察**：这三者**交互并复合**——单独修一个不够。论文明确说：*"these failures interact and compound, so fixing one in isolation does not suffice."* 这是设计三重工程（而非单一模块）的理由。

---

## 3. 架构：从任务意图到交付物的受控流水线

OneDayAgent 把开放式请求变成流水线（图 2）：

```text
user request + attachments
   |  <- kept as global intent (stable anchor)
   v
Planner decompose -> ordered subtasks (<=6)
   |   each subtask = ReAct loop (reason -> tool -> observe -> update)
   v
subtask execution (unified action space: web/academic/compute/file/multimodal)
   |   intermediate findings + artifacts -> execution memory + workspace
   v
Synthesizer -> candidate deliverable
   |
   v
Global Verification (against original request + subtask answers + declared attachments)
   |  <- defects found?
   v
Targeted Repair (ReAct loop, fix defect only, no full restart)
   |  <- re-verify
   v
deliver
```

**设计要点**：
- **global intent 是锚**：原始请求全程保存，每个子任务只是局部目标，但端到端交付物始终是全局目标
- **子任务边界 = 上下文保存接口**：后续子任务继承任务级状态（提交答案 + 结果文件句柄），**不继承底层 ReAct trace**
- **验证是 artifact-level + task-global**：检查候选交付物对照原始请求、子任务答案、声明附件，而非只判最终文本

---

## 4. 三重工程深潜：分解 / 记忆 / 验证

### 4.1 Capability I：任务分解（Task Decomposition）

把过载请求变成有界可执行单元。每个子任务可调用工具、产生产物、提交紧凑答案。**动机是实用**：everyday 请求常混入隐式需求 + artifact 级约束，单一不间断 ReAct 轨迹易过载。

### 4.2 Capability II：全局验证与修复（Global Verification & Repair）

- **全局验证**：完成所有子任务 ≠ 满足原始请求——长时程执行仍会丢早期约束、跳过隐式需求、产生局部合理但全局不完整的产物。验证器对照原始请求 + 子任务答案 + 声明附件检查。
- **定向修复**：用验证器的缺陷描述修订缺失/不一致部分，**不重启全部子任务**；修复后重新验证——验证是**最终任务级守卫**而非被动打分步骤。

### 4.3 Capability III：执行记忆（Execution Memory）

三层机制（记忆的目标不是存每个 token，而是保留后续推理/工具/产物构建**真正依赖**的信息）：

| 层 | 机制 | 具体实现 |
|:--|:--|:--|
| 工具层 | **Summarized truncation** | 搜索→结构化 snippets；长页→有界 raw 前缀摘要；文件→模态感知预览 |
| 子任务层 | **Subtask state passing** | 提交答案 + 声明结果文件句柄 = 紧凑 checkpoint，跨环境/模态复用，不继承低层 trace |
| 对话层 | **Automatic context compression** | 超过 0.9× 上下文预算 → LLM 生成技术摘要（system prompt/原始任务/最近 3 轮保留）；接近硬限（0.95×）→ 确定性紧急剪枝 |

### 4.4 工具与环境接口

| 组 | 工具 | 作用 |
|:--|:--|:--|
| Web | search / visit | 检索证据（Serper/Jina 后端） |
| 学术 | google_scholar / openalex | 文献元数据 |
| 计算 | python_interpreter / execute_command | 代码执行 |
| 文件 | read_file / write_to_file / edit_file | 工作区持久化 |
| 多模态 | analyze_image / generate_image | 图像理解/生成（Qwen3-VL-235B / Qwen-Image-2512-Lightning） |

---

## 5. 主结果与消融：验证模块是性价比之王

### 5.1 主结果（AgentIF-OneDay，104 任务 / 767 实例级评分点 / OWE-LII-IR 三模式）

| 方法/后端 | 总体 | 说明 |
|:--|:--:|:--|
| **OneDayAgent + GLM-5.2** | **0.821** | SOTA，全任务类型/域/rubric 维度领先 |
| AutoClaw（官方基线） | 0.799 | |
| Codex (GPT-5.5 medium) | 0.664 | 论文新增 |
| Manus | 0.645 | |
| Genspark | 0.635 | |
| ChatGPT-Agent | 0.626 | |
| Minimax-Agent | 0.562 | |

OneDayAgent 后端变体：Gemini-3.1-Pro 0.743 / Qwen3.5-397B-A17B 0.708 / Qwen3.5-9B 0.624 / Qwen3.6-27B 0.613——**同一 harness 不调参跨 3 家族 5 后端全部有效**。

### 5.2 消融（2×2：分解 × 验证，记忆始终启用）

| 变体 | 移除模块 | 总体 | ΔDirect | 延迟(min) | Score/Lat |
|:--|:--|:--:|:--:|:--:|:--:|
| DIRECT | 分解+验证 | 0.771 | – | 27.6 | 2.80 |
| DECOMP | 验证 | 0.804 | +3.3pp | 38.1 | 2.11 |
| VERIFY | 分解 | 0.804 | +3.3pp | 29.7 | 2.71 |
| FULL | 无 | 0.821 | +5.0pp | 53.6 | 1.53 |

**三个关键发现**：

1. **两模块独立贡献且可叠加**：分解/验证单独都 +3.3pp，组合 +5.0pp（小于之和 → 部分恢复重叠失败场景）
2. **成本极不对称**：VERIFY 只加 2.2 分钟就达到 DECOMP 的分数，而 DECOMP 加 10.6 分钟且工具调用 +60%——**验证修复是性价比最优的 harness 模块**
3. **全开不是最优**：VERIFY 在 17 个任务上高于 FULL（DECOMP 13、DIRECT 12）——模块组合取决于目标是最高分还是最低成本

---

## 6. 执行行为与后端分析：同 harness 不同执行风格

### 6.1 执行行为（GLM-5.2 运行）

- **分解是常态**：104 任务中仅 16 个单子任务，多数 2-4 个；5 子任务 117.2 分钟/156 工具调用 vs 1 子任务 20.6 分钟/17——**分解深度与任务难度相关，是转化器而非成本因子**
- **验证使交付风险可观测**：95/104 首过验证，9 进入修复（6 恢复、3 仍失败）；修复集中在 IR 任务、study 域、长时预算任务——验证是**交付风险管理**而非通用提分器
- **上下文管理稳质量**：35/104 触发压缩，最高压力任务累积 ~350K tokens 跨多轮压缩；**压缩次数与分数近零相关**——压缩没有系统性质量损失

### 6.2 后端分析（同一 harness 5 后端）

| 后端 | 家族 | 规模 | 总体 | 延迟(s) |
|:--|:--|:--|:--:|:--:|
| GLM-5.2 | GLM/智谱 | 744B | 0.821 | 3216.8 |
| Gemini-3.1-Pro-Preview | Gemini/Google | 未公开 | 0.743 | 1281.6 |
| Qwen3.5-397B-A17B | Qwen/阿里 | 397B-A17B | 0.708 | 964.5 |
| Qwen3.5-9B | Qwen/阿里 | 9B | 0.624 | 1895.2 |
| Qwen3.6-27B | Qwen/阿里 | 27B | 0.613 | 1280.5 |

**三个结论**：

1. **harness 可迁移**：5 后端 3 家族全 104/104 完成，无单点坍缩
2. **弱 scaling 趋势非严格定律**：Qwen3.6-27B 不压 9B；Gemini 公认 >1T 却只第二——**参数规模不能预测 agentic 长时程性能**（与近期 agentic 评测发现一致）
3. **执行风格画像**：GLM-5.2 高成本（53.6min/51.6 tools/585.7KB context）拿最高分；Gemini 精简（21.4min/18.7 tools/118.1KB）；Qwen3.6-27B 修复率最高（56.7%）——**换后端改变 harness 的使用方式，不只改变分数**

---

## 7. 运行时成本与案例：经济性与修复闭环

### 7.1 运行时成本（Table 7，GLM-5.2 运行）

| 模型/服务 | 角色 | 每任务平均调用 | 每任务输入 tokens |
|:--|:--|:--:|:--:|
| GLM-5.2 | 后端 LLM（规划/执行/合成/验证/修复） | 86.5 | 2.81M |
| DeepSeek-V4-Pro | 摘要辅助 | 5.8 | 176.6K |
| Qwen3-VL-235B | 图像理解 | 6.1 | 7.0K |
| Qwen-Image-2512 | 图像生成 | 1.2 | 0 |

**每任务 2.81M 输入 tokens（GLM-5.2）**——长时程 harness 的成本大头是后端推理 token，压缩机制（8.6% 工具消息被处理）正是为压这个。**成本透明度是 harness 工程的一部分**。

### 7.2 案例：Language of Flowers PPT 编辑

- 分解为「研究子任务 + PPT 修改子任务」
- PPT 修改子任务以文件描述符错误失败——**合成阶段如实报告失败子任务而非标记整体完成**
- 验证器发现缺 PPT 文件，建议把收集的修改应用到真实 deck
- 修复阶段生成缺失演示文稿，二次验证确认幻灯片编辑 + 图像插入到位

**闭环价值**：失败子任务被验证器捕获并定向修复，而非整体重跑或静默交付次品。

---

## 8. Argus 对比：verified pivoting 的另一条路线

Argus（微软+上交等，2608.05144，08-05）回答 OneDayAgent 未问的问题：**长时程中目标本身错了怎么办？**

### 8.1 核心问题

> "Unrestricted pivoting is indistinguishable from rationalized failure."

允许目标修订 ≠ 纵容目标漂移。Argus 把「修订」与「漂移」分开的唯一机制是**验证门禁**：可接受的 pivot 必须有证据支持（前路线不可达/目标被误设）、经过角色边界（role-gated）、被记录（后续任务继承变更及其理由）。

### 8.2 架构：四角色 × 持久状态

- **Manager** 锚定 standing intent（用户意图 ι）与 campaign 状态
- **Planner / Engineer / Reviewer** 在共享工作区执行 bounded missions
- 工作契约 `K_t = (ι, o_t, c_t, v_t)`：稳定意图 vs 可修订的操作目标/约束/验证标准——**契约修订与意图变更显式分离**
- 三平面分离：控制（调度）/ 执行（工作）/ 记录（审计），保证职责可分离

### 8.3 验证门禁的运行时自进化

模型权重固定，**自进化发生在持久运行时状态与控制策略**：候选记忆/技能/验证器/路由决策/被拒路线——只有通过角色审查 + 任务原生验证器证据后才进入持久状态。**被证伪的路线保留**（后续可作「目标不可达」的证据）。

### 8.4 量化结果

- SWE-Bench Pro 78% vs Direct Copilot 59%（1.41× tokens）
- 成熟 Wave 比启动 Wave 每任务省 21% 输入 tokens、15% 活动时间（观测性，非受控消融）
- 731 任务中 466 独立 Reviewer / 265 自审；Reviewer 扣留 43 任务完成（34 后过官方验证器、22 完成严格审查环）
- 6 论文管线 254 missions / 16 Stage 回滚 → 全部达到投稿完成
- 外部采纳：RWKV6 内核合并入上游 Flash Linear Attention 仓库
- 数学 campaign：1 条被证伪路线 + 6 条定理前沿更新

### 8.5 两条路线对比结论

| | OneDayAgent | Argus |
|:--|:--|:--|
| 目标修订 | 固定意图，验证修复交付物 | 证据门禁下修订操作目标 |
| 状态 | 子任务 checkpoint（任务级） | 持久项目状态（跨任务） |
| 验证 | 交付物级（一次合成后） | 每步准入（admission gate） |
| 失败处理 | 修复缺陷 | 保留被证伪路线 + 回滚 |
| 适用 | everyday 确定性交付 | 研究性开放式探索 |

**互补**：OneDayAgent 解决「长任务怎么跑完」，Argus 解决「长任务跑着跑着方向错了怎么办」。下一代 harness 很可能融合两者——**验证门禁的「证据-授权-记录」三元组可以移植到 everyday 场景的目标修订**。

---

## 9. 与 08-05 论断的实证呼应

08-05 [Harness 即适配层/Agent 与 OS 进程边界同构](2026-08-05-harness-os-process-boundary-isomorphism.md) 提出核心命题：**Harness = LLM 之上的微内核，Agent = LLM 语义引擎 × 进程执行引擎复合体**，12 项结构同构映射（上下文↔地址空间、工具↔syscall、Loop↔调度、subagent↔fork 等）。

OneDayAgent 为这些映射提供**实证锚点**：

| 08-05 论断 | OneDayAgent 实证 |
|:--|:--|
| 上下文 = 地址空间，需管理 | 0.9×/0.95× 压缩阈值 + 紧急剪枝 = 虚拟内存的换页策略；~350K tokens 压缩不损质量 = 换页无 thrashing |
| subagent = fork/exec，隔离失败域 | 子任务 = 有界执行单元，边界 = 上下文保存接口（继承答案+文件句柄，不继承 trace）= fork 后 exec 新映像，仅继承文件描述符 |
| 工具 = syscall，白名单权限 | 统一动作空间 + 工作区 = 系统调用面；workspace artifacts = 文件系统持久化 |
| 进程 = 状态 + 文件描述符 | 子任务 checkpoint = 提交答案 + 结果文件句柄（正是「状态 + fd」的 Agent 版） |
| 崩溃恢复 | 验证-修复循环 = 异常处理；失败子任务如实报告 → 验证器捕获 → 定向修复 = 结构化错误传播而非静默 |
| 调度 | 分解 = 进程创建；serial 依赖 = 进程树拓扑 |

**一句话**：OneDayAgent 是「进程模型」在 Agent 运行时的一次忠实实现——**子任务即进程、checkpoint 即进程状态、验证器即监督者**。08-05 的理论推演在 08-04 的工程实现里得到独立验证（时间上论文先行，佐证推演方向的正确性）。

---

## 10. Skill-Use 增量：技能可测性设计的第二维度

今日早前 [技能使用评测缺口](2026-08-07-skill-use-eval-gap-deep-analysis.md) 已从**技能侧**给出可测性设计（Trigger/Compliance/Boundary 三分解 + SU 0.613 + 触发率自检 + 验证器双层）。OneDayAgent 补齐**harness 侧**的第二维度：

| 可测性维度 | 技能侧（Skill-Use） | harness 侧（OneDayAgent） |
|:--|:--|:--|
| 测什么 | 模型是否真的会用技能 | harness 模块是否真的贡献成功 |
| 方法 | 三分解指标 | 2×2 消融（DIRECT/DECOMP/VERIFY/FULL） |
| 关键发现 | 触发≠会用（0.613） | 模块叠加 < 之和（重叠恢复）；验证性价比最优 |
| 可测性设计启示 | 技能注册/路由/触发率统计 | **harness 模块级消融 = 组件的「单元测试」**；成本-收益表（Score/Lat） |

**对本地技能系统可测性设计的直接借鉴**（用户点名的价值点）：

1. **模块级消融可移植**：本系统 6 阶段 pipeline（input-qa→multi-path→convergence→verification→constraint→expert-gate）可做同样的 2×2 消融——测「每个阶段是否真的贡献最终质量」，而非默认全开
2. **成本-收益显式化**：Score/Lat 表 = 每模块「收益/成本」账本——与 08-05 产出经济学「毛利 vs 净利」同构，治理决策有数据支撑
3. **「全开不是最优」的工程含义**：约束/验证等重量级模块应有开关策略，按任务类型路由（简单任务 DIRECT 即可）
4. **执行风格画像**：换后端改变使用方式——本系统换模型时应有「执行画像」基线（工具调用数/修复率/上下文水位），防止静默退化

---

## 11. 批判性审视

1. **单基准泛化未验证**：仅 AgentIF-OneDay 104 任务（work/life/study），跨基准（SWE-Bench Pro 类）未报告——「长时程 harness 通用有效」的声明被限定
2. **judge 不可比风险**：官方基线用 Gemini-3-Pro-Preview judge，论文改用 Gemini-3.1-Pro-Preview（低 3.12pp，作者称保守）——但基线分数是旧 judge 打的，**对比基准并不完全对齐**
3. **记忆模块未消融**：论文明确「禁用执行记忆会导致上下文溢出/状态丢失无法完成任务」——三能力中记忆的**增量贡献**从未被量化（它是使能条件而非加分项）
4. **无 workspace 隔离**：附录 E 承认当前实现无隔离，跨环境 everyday 任务在真实部署中有安全风险（与 [Agent 可靠性 SDK 加固](../../07_industry-research/04_ai/2026-08-07-agent-reliability-sdk-hardening-deep-analysis.md) 的 sandbox 主题同构）
5. **经济性未讨论**：GLM-5.2 每任务 2.81M input tokens / 53.6 分钟——大规模部署成本惊人，无成本/收益分析
6. **修复能力有限**：9 个进修复任务只恢复 6——验证能发现问题但修复不是万能的（3 个修复后仍失败）
7. **分解深度非因果**：深层分解 = 更难任务（观测相关），「分解提高成功」的因果性被混淆
8. **SOTA 的模型贡献未剥离**：GLM-5.2（744B）比 Gemini（>1T）高 0.078——「harness 好」与「模型好」的分离仅靠「同 harness 跨后端有效」间接论证，未做「同模型不同 harness」对照
9. **Argus 评估不可比**：与 OneDayAgent 用不同基准/协议，不能横向比较；Argus 自进化数据是观测性非受控消融

---

## 12. 本系统启示

1. **子任务 checkpoint 落地**：本系统多阶段 pipeline（调研→加工→归档→索引同步）可引入「提交答案 + 结果文件句柄」式 checkpoint——阶段间传「产物引用」而非「全文」，省 token 且断点可恢复
2. **artifact-level 验证升级**：当前三同步验证偏「文本级」，可补「交付物级」——对照原始任务意图检查最终文档（与 OneDayAgent 验证器同构）
3. **模块级消融制度化**：对 6 阶段 pipeline 做成本-收益审计（Score/Lat 表），识别「默认全开但贡献低」的模块——与 08-05 治理诊断的 churn 分析互补
4. **压缩阈值已有基础**：记忆「context compaction 95% 水位」与 OneDayAgent 0.9×/0.95× 双阈值同构——可显式化「保留最近 N 轮 + 摘要上限」
5. **后端无关性验证**：CowAgent Harness「换模型=纯配置」已有，可补「执行风格画像」基线（工具调用/上下文水位/修复率），防换模型静默退化
6. **成本透明度**：Table 7 式 token 账本——与 [产出经济学](../../07_industry-research/04_ai/2026-08-05-ai-output-gross-vs-net-entropy.md)「毛利 vs 净利」配套，工具时间占比 ≤35% 监控已有

---

## 13. 预测 P1-P5

- **P1（高置信）**：12 个月内 AgentIF-OneDay 成为长时程 everyday harness 的标配评测，≥3 个新 harness 报告其分数（2027-08 核验）
- **P2（高置信）**：验证-修复模块成为长时程 harness 默认组件（消融证明性价比最优），「先验证后交付」成默认工作流（2027-08 核验）
- **P3（中置信）**：跨后端报告「执行风格画像」（延迟/工具调用/修复率）成为 harness 论文标配，模型评测从单分数走向多维度执行画像（2027-08 核验）
- **P4（中置信）**：「压缩数近零相关」结论将面临跨天级（>350K tokens、多会话）验证——上下文压缩是否仍保质量是长时程的下一个关键问题（2027-08 核验）
- **P5（中置信）**：verified pivoting（Argus 路线）进入 everyday harness：12 个月内出现带「证据门禁目标修订」的 everyday 级 harness（2027-08 核验）

---

## 14. 参考来源

- [OneDayAgent: Towards a Long-Horizon Harness for Autonomous Agents](https://arxiv.org/abs/2608.05013) — arXiv 2608.05013v1，2026-08-04（**全文一手抓取，含附录 A-G**）
- [Argus: A General-Purpose Agentic Runtime for Long-Horizon Reasoning](https://arxiv.org/abs/2608.05144) — arXiv 2608.05144v1，2026-08-05（**全文一手抓取**）
- [AgentIF-OneDay: A Task-Level Instruction-Following Benchmark for General AI Agents in Daily Scenarios](https://arxiv.org/abs/2601.20613) — 基准原文
- 本地：[Harness 进程边界同构](2026-08-05-harness-os-process-boundary-isomorphism.md)（08-05 论断）
- 本地：[技能使用评测缺口](2026-08-07-skill-use-eval-gap-deep-analysis.md)（Skill-Use 主篇）
- 本地：[Harness 实证化四篇](2026-08-07-harness-empirical-four-papers.md)

---

> **诚实标注**：OneDayAgent 与 Argus 均为 2026-08 初 preprint，未经同行评审；OneDayAgent 的 Gemini 3.1 judge 与官方基线 judge 差异已由作者标注（保守方向）；Argus 自进化数据为观测性非受控消融；两者基准不同不可横向比较。本分析为学术解读，非投资或采购建议。

---

## Changelog

- 2026-08-07：创建。素材=OneDayAgent 全文（含附录）+ Argus 全文一手抓取；主线=长时程 harness 三重工程（分解/记忆/验证）+ verified pivoting 对比；与 08-05 进程边界论断实证呼应；Skill-Use 可测性第二维度增量。
