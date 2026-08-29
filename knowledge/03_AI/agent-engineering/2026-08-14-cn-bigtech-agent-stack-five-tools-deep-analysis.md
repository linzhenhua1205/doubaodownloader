---
# 标题: 国产大厂 Agent 技术栈五件套深度分析（deer-flow / WeKnora / BrowserSkill / skill-up / vLLM-Kunlun）
# 类型: analysis
# 创建: 2026-08-14
# 更新: 2026-08-14
# 来源: GitHub API/README 一手抓取（bytedance/Tencent/alibaba/baidu）+ 本地知识库锚点
---

# 国产大厂 Agent 技术栈五件套深度分析

> **一句话**：字节（deer-flow ⭐79.9k，SuperAgent Harness）、腾讯（WeKnora ⭐19.9k，LLM 知识平台 + BrowserSkill ⭐1.0k，Agent 浏览器工具面）、阿里（skill-up，Agent Skills 评估进化）、百度（vLLM-Kunlun，昆仑 XPU 推理栈）——**中国头部厂商的 Agent/知识/推理基础设施已全面开源化**，且高度收敛到同一套设计语言：SKILL.md 技能协议、渐进式加载、沙箱化执行、评估驱动进化、硬件可插拔。本分析逐件拆解框架定位与技术原理，并对照本系统（cow）技能/知识体系找同构与差距。

> **关键词**: deer-flow · WeKnora · BrowserSkill · skill-up · vLLM-Kunlun · SuperAgent Harness · SKILL.md · Agent Skills 评估进化 · 知识平台 · RAG · Wiki Mode · 浏览器工具面 · 昆仑 XPU · 国产推理栈

> **数据源**: 🔵 GitHub REST API + raw README（2026-08-14 抓取，star/fork/语言/更新时间一手）· 🔵 本地知识库锚点（Agent 编排六层、技能三维查重、evolver/skill-evolver、web-access、CPO/推理栈）

> **日期**: 2026-08-14 | **领域**: Agent 工程 × 知识管理 × 国产推理栈

---

## 📑 目录

- [〇、结论概要](#〇结论概要)
- [一、五件套全景表](#一五件套全景表)
- [二、bytedance/deer-flow：SuperAgent Harness（⭐79.9k）](#二bytedancedeer-flowsuperagent-harness799k)
- [三、Tencent/WeKnora：LLM 知识平台（⭐19.9k）](#三tencentweknorallm-知识平台199k)
- [四、Tencent/BrowserSkill：Agent 浏览器工具面（⭐1.0k）](#四tencentbrowserskillagent-浏览器工具面10k)
- [五、alibaba/skill-up：Agent Skills 评估进化（⭐534）](#五alibabaskill-upagent-skills-评估进化534)
- [六、baidu/vLLM-Kunlun：昆仑 XPU 推理栈（⭐455）](#六baiduvllm-kunlun昆仑-xpu-推理栈455)
- [七、横向洞察：中国大厂 Agent 生态信号](#七横向洞察中国大厂-agent-生态信号)
- [八、与本系统（cow）对照：同构与差距](#八与本系统cow对照同构与差距)
- [九、可证伪预测](#九可证伪预测)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 〇、结论概要

1. **五件套覆盖 Agent 技术栈全链条**：编排（deer-flow）→ 知识（WeKnora）→ 工具面（BrowserSkill）→ 技能治理（skill-up）→ 推理底座（vLLM-Kunlun）。中国头部厂商从「消费开源」转向「产出开源」，且**全部是工程化程度极高、非 demo 级**的投入。
2. **SKILL.md 技能协议成为事实标准**：deer-flow（内置 skills 渐进加载）、skill-up（评估对象就是 SKILL.md）、BrowserSkill（自身就是一个 skill 分发给 8+ harness）、WeKnora（Agent Skills + sandboxed 执行）——四个项目**不约而同收敛到 Markdown 技能文件 + 渐进加载 + 沙箱执行**的设计，与本系统技能体系（skills/*/SKILL.md）同构。
3. **deer-flow 2.0 是范式信号**：从「Deep Research 框架」ground-up 重写为「SuperAgent Harness」（LangGraph/LangChain 底座，sub-agents + memory + sandbox + skills + session goals），79.9k star 说明社区已验证「harness > 框架」——**给 agent 的不是 API 拼接，而是完整运行时**。
4. **评估-进化闭环是下一代竞争力**：阿里 skill-up 的 Eval-to-Evolution Loop（评估 → 失败分析 → 自动修复 eval/技能 → 回归 → 迭代）与本系统 evolver/skill-evolver 方向一致，但 skill-up 把「评估自动化」做成了产品——**这是本系统的明确差距**（本系统有进化协议，缺系统化评估）。
5. **国产推理栈走「硬件插件化」路径**：vLLM-Kunlun 遵循 vLLM RFC 11162（hardware pluggable）解耦昆仑 XPU，连续三日推送 = 百度对国产推理栈的高强度投入——与昇腾/Moore Threads 一起构成国产芯片生态主战场。

---

## 一、五件套全景表

| 项目 | 厂商 | Star | Fork | 语言 | 定位 | 更新 |
|:--|:--|:--|:--|:--|:--|:--|
| [deer-flow](https://github.com/bytedance/deer-flow) | 字节 | **79,967** | 10,940 | Python | Long-horizon SuperAgent Harness | 08-14（今日） |
| [WeKnora](https://github.com/Tencent/WeKnora) | 腾讯 | **19,853** | 2,854 | Go | LLM 知识平台（RAG/Agent/Wiki） | 08-14（今日） |
| [BrowserSkill](https://github.com/Tencent/BrowserSkill) | 腾讯 | **1,031** | — | Rust | Agent 浏览器工具面（真实登录态） | 近期 |
| [skill-up](https://github.com/alibaba/skill-up) | 阿里 | **534** | — | Go | Agent Skills 评估与进化 | 近期 |
| [vLLM-Kunlun](https://github.com/baidu/vLLM-Kunlun) | 百度 | **455** | 96 | Python | vLLM 昆仑 XPU 硬件插件 | 08-13 |

> star 数据为 2026-08-14 GitHub API 抓取。deer-flow 79.8k→79.9k（用户提示「再涨」确认，今日仍有更新）。

---

## 二、bytedance/deer-flow：SuperAgent Harness（⭐79.9k）

### 2.1 定位与演进

- **DeerFlow = Deep Exploration and Efficient Research Flow**（缩写反向说明：从深度研究出发）
- **2.0 是 ground-up rewrite**：与 1.x 无共享代码；1.x 保留在 `main-1.x` 分支继续维护
- **范式转变**（README 原文逻辑）：社区把 1.x 从「Deep Research」推向数据管线/幻灯片/仪表盘/内容自动化等**超出设计预期**的用途 → 团队意识到它本质是 **harness（运行时）** 而非 research 工具 → 重写为「batteries included, fully extensible」的 **SuperAgent Harness**
- 底座：**LangGraph + LangChain**

### 2.2 技术原理（四支柱）

```
   DeerFlow 2.0 SuperAgent Harness
   +-----------------------------------------------------+
   |  Session Goals (top-level orchestration intent)     |
   +-----------------------------------------------------+
   |  Sub-agent orchestration                             |
   |   - parallel/serial routing (max_concurrent_subagents)|
   |   - read-only research parallel; shared-file serial  |
   +-----------------------------------------------------+
   |  Skills (progressive loading)                        |
   |   - SKILL.md = workflow + best practices + resources |
   |   - loaded only when task needs => lean context      |
   |   - built-in: research / report-generation /         |
   |     slide-creation / web-page / image-generation +   |
   |     claude-to-deerflow                               |
   +-----------------------------------------------------+
   |  Memory (cross-session persistence)                  |
   |   - DeerMem default local backend + opt-in mem0      |
   |   - profile/preferences/knowledge, local control     |
   +-----------------------------------------------------+
   |  Sandbox (isolated execution)                        |
   |   - E2BSandboxProvider (wait overflow policy)        |
   |   - AioSandboxProvider (container isolation)         |
   |   - LocalSandboxProvider (local, host bash disabled) |
   +-----------------------------------------------------+
```

**关键技术点**：
1. **Skill 目录即包边界**：找到 `SKILL.md` 后，包内嵌套 SKILL.md 不再注册为运行时技能（避免递归膨胀）；无 SKILL.md 的命名空间目录可分组嵌套技能
2. **渐进加载**：技能只在任务需要时加载——「context window lean，对 token 敏感模型友好」
3. **子代理编排策略**：并行路由仅在「墙钟节省 > 重复发现/综合成本」时启用；`max_concurrent_subagents=1` 时禁用并行，仅保留专家/上下文隔离委派
4. **Claude Code 集成**：`claude-to-deerflow` skill 让 Claude Code 直接向运行中的 DeerFlow 实例发任务/查状态/管线程

### 2.3 与本系统对照

| 维度 | deer-flow | 本系统（cow） |
|:--|:--|:--|
| Skill 协议 | SKILL.md（工作流+最佳实践+资源） | skills/*/SKILL.md（一致 ✅） |
| 渐进加载 | 任务需要时加载 | 系统提示词全量注入技能清单（❌ 差异：本系统未做运行时渐进加载，但有裁剪实践） |
| Memory | DeerMem 本地 + mem0 | memory/ 每日记忆 + MEMORY.md 索引（同构 ✅） |
| Sandbox | 三层沙箱 | bash 工具直接执行（⚠️ 无容器隔离） |
| 子代理 | LangGraph 编排 | 无子代理机制（单循环） |

---

## 三、Tencent/WeKnora：LLM 知识平台（⭐19.9k）

### 3.1 定位

企业级 LLM 知识框架（**Go 实现**），三大核心能力：
1. **RAG Quick Q&A**：日常查询
2. **ReAct Agent**：自主编排检索 + MCP 工具 + 网络搜索，处理多步复杂任务
3. **Wiki Mode**（v0.5 GA）：agent 把原始文档蒸馏为**自维护、互链的 Markdown 知识库** + 交互式知识图谱，支持手工编辑、修订历史、一键回滚

### 3.2 技术原理（工业化知识管线）

```
   docs -> parse -> chunk -> embed -> retrieve -> rerank -> LLM -> cite/output
   every stage swappable (modular architecture)
```

| 环节 | 能力 | 要点 |
|:--|:--|:--|
| 摄入 | 飞书 Wiki/Drive、Notion、语雀、RSS、云之家；10+ 格式（PDF/Word/Excel/图片/EPUB/MHTML） | 增量+全量同步；40k 文档 KB（任务队列 + DLQ） |
| 解析 | OpenDataLoader、PaddleOCR-VL、ASR（音频） | 自适应 3 层分块（v0.5.2）；per-upload process_config |
| 检索 | BM25 稀疏 / Dense / **GraphRAG** / 父子分块 / HNSW pgvector（1024-dim）/ OpenSearch / Milvus / Qdrant / Weaviate | 混合检索 + 重排（Tencent LKEAP / Volcengine rerank） |
| 推理 | 20+ LLM 提供商（OpenAI/DeepSeek/Qwen/Zhipu/Hunyuan/Gemini/MiniMax/NVIDIA/Ollama） | 多轮上下文、thinking 模式 |
| Agent | ReAct + MCP（29 工具，OAuth2 远程服务）、`@Skill/@MCP` 每轮作用域限定 | sandboxed 技能执行（v0.3.0 起） |
| 治理 | **4 层 RBAC**（Owner/Admin/Contributor/Viewer）+ per-KB 所有权 + 审计日志；scoped API key + principal model | 企业级 |
| 可观测 | Langfuse（OTLP/OTel，W3C traceparent） | RAG 管线 stage 级进度 |

### 3.3 知识管理工业化亮点

- **Chunk 编辑 + 修订历史**：检索分块像文档一样可编辑/diff/回滚/自动重建索引——**把「检索单元」纳入版本管理**
- **Wiki Mode 自维护知识库**：agent 蒸馏文档 → 互链 Markdown + 知识图谱——**与本系统 knowledge/ 体系高度同构**（都是「文档 → 结构化知识资产」的工业化）
- **每上传批次的 process_config**：解析器/分块/多模态/图谱抽取/问题生成全部可覆盖

### 3.4 与本系统对照

| 维度 | WeKnora | 本系统（cow） |
|:--|:--|:--|
| 知识库形态 | Wiki Mode 自动互链 Markdown + 图谱 | knowledge/ 手工维护 + 索引/日志三件套（同构 ✅，但 WeKnora 有图谱+可视化） |
| 检索 | 混合检索（BM25+稠密+GraphRAG+父子） | keyword-only（记忆：最高杠杆=启用 embedding，¥30-60 未启）⚠️ |
| 分块治理 | chunk 编辑+修订+重建索引 | 无分块概念（整文档粒度） |
| RBAC/审计 | 4 层角色+审计日志 | 单用户无 RBAC |
| 观测 | Langfuse 全链路 | 无 tracing |
| 摄入源 | 飞书/Notion/语雀/RSS 自动同步 | 手工归档 + web-archive skill |

> **借鉴点**：WeKnora 证明「企业级知识平台」的完整形态；本系统在检索（embedding）与观测（tracing）上存在明确差距。

---

## 四、Tencent/BrowserSkill：Agent 浏览器工具面（⭐1.0k）

### 4.1 定位

让 AI Agent（Cursor/Claude Code/Codex/OpenClaw/CodeBuddy/WorkBuddy/Pi/Hermes 等 **8+ shell-capable harness**）使用你**已登录的真实浏览器**，且不打断你的工作。

### 4.2 技术原理（本地桥架构）

```
   Agent Harness --shell: bsk--> bsk CLI --local IPC--> bsk daemon
                                                          |
                                              WebSocket 127.0.0.1
                                                          v
                                                 BrowserSkill extension
                                                          |
                                          +---------------+---------------+
                                          v                               v
                                   Agent Window (visible)      user windows (borrowed tab only)
```

**四个关键设计**：
1. **借标签页模式**：agent 需要触碰某个已开标签页时**显式借用**，任务完成归还，其余浏览器不动——最小侵入
2. **复用真实登录态**：agent 直接用你已登录的会话，无需独立测试账号
3. **Agent Window 隔离**：浏览器任务在独立可见窗口运行，你继续用自己浏览器
4. **内置 human-in-loop**：验证码/登录/确认对话框等人类专属步骤，agent 请求接管后继续

**实现**：Rust（Cargo workspace）——`crates/bsk-cli`（CLI+daemon）、`crates/bsk-protocol`（wire types + JSON schema）、`apps/extension`（浏览器扩展）；MIT。

### 4.3 与本系统对照（浏览器工具面）

| 维度 | BrowserSkill | 本系统（web-access/browser） |
|:--|:--|:--|
| 连接方式 | 扩展 + WebSocket 127.0.0.1 | CDP（需用户浏览器开远程调试）/ 独立 browser 工具（未装） |
| 登录态 | 复用真实已登录会话 | CDP 可复用 profile；云端禁微信自动登录 |
| 隔离 | Agent Window 独立窗口 + 借标签页 | 无窗口隔离概念 |
| Human-in-loop | 内置（验证码/确认接管） | 手动截图+询问 |
| 通用性 | 任何 shell-capable agent（bsk CLI） | 仅本系统 |

> **借鉴点**：「借标签页 + Agent Window + human-in-loop 接管」是浏览器工具面的产品化范式；本系统 browser 工具未安装是现实短板（用户需 `cow install-browser`）。

---

## 五、alibaba/skill-up：Agent Skills 评估进化（⭐534）

### 5.1 定位（用户重点：与本系统技能进化方向同构）

**Agent Skills 的评估与进化工具**（Go 1.25+，Apache 2.0）：
- **Evaluation**：声明式 YAML（`eval.yaml` + `cases/*.yaml`），跨多个 Agent Engine，规则/脚本/Agent 三类裁判，本地或 CI 产出结构化报告
- **Evolution**：**skill-upper**（随仓库分发的 Agent Skill）——对话式读取失败报告 → 自动修复/扩展 eval 套件 → 重跑 → 迭代（Eval-to-Evolution Loop）

### 5.2 技术原理（Eval-to-Evolution Loop）

```
   loop: conversation creates evals -> skill-up runs -> structured report
         -> skill-upper diagnoses failures -> fix SKILL.md or eval cases
         -> add regression cases -> rerun -> until key behaviors pass
```

| 组件 | 机制 |
|:--|:--|
| 声明式配置 | `eval.yaml`（环境/引擎/模型）+ `cases/*.yaml`（用例），替换 ad hoc 运行目录 |
| 多引擎 | 内置 Qoder CLI / Claude Code / Codex / qwen_code + `engine.custom`（本地 transport） |
| 三类裁判 | `rule_based`（规则）/ `script`（脚本）/ `agent_judge`（Agent 评审） |
| 报告 | Anthropic 兼容 `grading.json`/`benchmark.json`/`benchmark.md` + `result.json` + JUnit XML + HTML |
| 兼容 | `skill-up import evals.json` / `--auto` 自动检测（Anthropic 生态） |
| CI-Ready | 本地开发 + CI 流水线双场景 |

**核心洞察**：skill-up 把官方 [Agent Skills 评估指南](https://agentskills.io/skill-creation/evaluating-skills) 描述的循环（写真实用例 → 带/不带 Skill 各跑一次 → 评分 → 聚合 → 迭代）落地为**可复用 CLI + 对话式进化代理**。关键哲学：**「评估是进化的燃料」——没有可重复的评估，进化就是空转**。

### 5.3 与本系统对照（同构分析）

| 维度 | alibaba/skill-up | 本系统（cow） |
|:--|:--|:--|
| 进化机制 | Eval-to-Evolution Loop（评估驱动） | evolver/skill-evolver（GEP 基因组进化协议） |
| 评估 | 声明式 eval.yaml + 三裁判 + 结构化报告 | **无系统化技能评估**（有 doc-reviewer/light-self-review 但针对文档非技能）⚠️ |
| 进化代理 | skill-upper（对话式） | evolver（自动识别短板+迭代） |
| 多引擎 | Qoder/Claude Code/Codex/qwen_code/custom | 单一 harness |
| CI | 内置 CI 集成 | 无 |
| 兼容 | Anthropic evals.json | 无 |

> **结论**：方向同构（评估+进化闭环），但 **skill-up 把「评估」产品化是本系统的明确差距**——本系统有进化协议与注册治理（6 步注册/三维查重），缺「可重复、可度量、可回归」的评估套件。**可借鉴：为本系统技能引入 eval.yaml 式评估 + 裁判策略 + 回归用例。**

---

## 六、baidu/vLLM-Kunlun：昆仑 XPU 推理栈（⭐455）

### 6.1 定位

**vLLM 昆仑硬件插件**——让 vLLM 无缝跑在昆仑 XPU（Kunlun3 P800）上，是 vLLM 社区集成昆仑后端的推荐路径，遵循 [RFC Hardware pluggable（vllm-project/vllm#11162）](https://github.com/vllm-project/vllm/issues/11162)。

### 6.2 技术原理

- **硬件可插拔接口**：RFC 11162 定义的插件化接口把昆仑 XPU 与 vLLM 解耦——不改 vLLM 核心，以插件形式挂载
- **模型矩阵**：Transformer 类（Qwen2/2.5/3、Llama2 等）、**MoE（Qwen3-MoE/Qwen3-Next）**、Embedding、多模态；特性覆盖**量化 / LoRA / Piecewise Kunlun Graph（分段执行图）**
- **软件栈**：Python ≥3.10、PyTorch ≥2.5.1、vLLM 同版本对齐
- **时间线**：2025/12 首版 → 2026-08-13 仍高频更新（**连续三日推送** = 投入强度确认）

### 6.3 生态意义

- **国产推理栈的「插件化」路径**：不 fork vLLM 主线（避免分叉），而是以社区插件形式贡献——**融入国际生态而非另起炉灶**，这是国产芯片软件栈成熟度提升的信号
- **MoE 支持**（Qwen3-MoE + 量化 + LoRA）= 国产芯片对齐主流稀疏推理需求
- 与本地记忆互证：昆仑芯锁定腾讯至 27 年底（规格改写实证 3）、摩尔线程 H1 17.36 亿 +147%（国产 AI 芯片财报）——**国产推理栈（vLLM 适配）是国产替代主战场**

---

## 七、横向洞察：中国大厂 Agent 生态信号

1. **全面开源化且工程化**：五件套都不是 demo——deer-flow 79.9k star 的 harness、WeKnora 的企业级 RBAC/观测/40k 文档、BrowserSkill 的 Rust 双运行时、skill-up 的 CI 集成——**中国头部厂商从「消费开源」转向「产出开源」**
2. **SKILL.md 成为事实标准**：四个 Agent 侧项目（deer-flow/skill-up/BrowserSkill/WeKnora）收敛到同一技能协议——Markdown 技能文件 + 渐进加载 + 沙箱执行。**协议层已统一，差异化在治理/评估/生态**
3. **评估-进化闭环 = 下一竞争维度**：skill-up（阿里）+ evolver 类工具（社区）都在做「技能质量可度量 + 自动迭代」——技能数量竞赛之后是**技能质量竞赛**
4. **工具面创新**：BrowserSkill 的「真实登录态复用 + 借标签页 + human-in-loop」解决 Agent 浏览器的**信任与侵入性**问题——工具面从「能用到好用」演进
5. **国产推理栈走插件化**：vLLM-Kunlun 遵循 RFC 11162 而非 fork——**生态融合优先**，与昇腾（MindIE）、Moore Threads 形成国产推理栈三线

---

## 八、与本系统（cow）对照：同构与差距

| 能力域 | 行业标杆（本次分析） | 本系统现状 | 差距/行动 |
|:--|:--|:--|:--|
| 技能协议 | SKILL.md 事实标准（四项目一致） | skills/*/SKILL.md ✅ | 无 |
| 技能评估 | skill-up：eval.yaml+三裁判+回归 | 无系统化评估 ⚠️ | **P0 可借鉴：引入评估套件** |
| 技能进化 | skill-upper 对话式 / evolver | evolver/skill-evolver ✅ | 方向一致，评估补齐后闭环 |
| 知识检索 | WeKnora 混合检索（BM25+稠密+GraphRAG） | keyword-only ⚠️ | 启用 embedding（记忆：¥30-60，最高杠杆） |
| 知识治理 | WeKnora chunk 编辑/修订/图谱 | 三件套纪律+索引治理 ✅ | 图谱/分块是可选增强 |
| 浏览器工具面 | BrowserSkill（借标签页+human-in-loop） | browser 未安装 ⚠️ | `cow install-browser` |
| 沙箱隔离 | deer-flow 三层沙箱 | 无容器隔离 ⚠️ | 本地信任场景可缓 |
| 可观测 | WeKnora Langfuse 全链路 | 无 tracing ⚠️ | 可选 |

---

## 九、可证伪预测

| # | 预测 | 时间窗 | 证伪条件 |
|:--|:--|:--|:--|
| P1 | deer-flow 2.x 进入 LangGraph/LangChain 官方 showcase 或合入其生态教程 | 2027-06 前 | 未发生 |
| P2 | WeKnora 引入 embedding 检索本地化（非 API）或 GraphRAG 性能白皮书 | 2027-06 前 | 无动作 |
| P3 | alibaba/skill-up 被 Anthropic 官方评估指南引用为参考实现 | 2027-06 前 | 未被引用 |
| P4 | 国产推理栈（vLLM-Kunlun/昇腾 MindIE）在 2027 年智算中心招标份额显著上升 | 2027-12 | 份额无变化 |
| P5 | 本系统启用 embedding 检索（用户决策后）后，知识检索命中率显著提升（对照基线） | 决策后 1 月 | 无提升 |

---

## 参考来源

1. 🔵 GitHub API（2026-08-14 抓取）：[bytedance/deer-flow](https://github.com/bytedance/deer-flow) ⭐79,967 · [Tencent/WeKnora](https://github.com/Tencent/WeKnora) ⭐19,853 · [Tencent/BrowserSkill](https://github.com/Tencent/BrowserSkill) ⭐1,031 · [alibaba/skill-up](https://github.com/alibaba/skill-up) ⭐534 · [baidu/vLLM-Kunlun](https://github.com/baidu/vLLM-Kunlun) ⭐455
2. 🔵 各仓库 README 原文（raw.githubusercontent.com 抓取）：deer-flow 2.0（SuperAgent Harness/四支柱）、WeKnora v0.7.2 CHANGELOG 全量、skill-up 完整文档、BrowserSkill 架构图、vLLM-Kunlun 模型矩阵
3. 🔵 本地知识库锚点：Agent 编排六层/工具面、技能三维查重+6 步注册、evolver/skill-evolver、web-access（CDP）、embedding 检索决策（¥30-60）、昆仑芯锁定腾讯、摩尔线程财报
4. ⚠️ 信息缺口：deer-flow 2.0 的 SKILL.md 目录结构未全量核对（README 节选）；vLLM-Kunlun 性能数据（吞吐/延迟）未获取；skill-up 的 eval 用例质量未实测——均为后续可补项

## Changelog

- 2026-08-14：创建。GitHub API 一手抓取五件套元数据 + README 精读；逐件拆解框架与技术原理；与本系统对照找同构与差距（P0=技能评估套件、embedding 检索、browser 工具）。
