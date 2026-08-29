# 🌐 AI 浏览器赛道爆发：基础设施巨头抢占 AI 入口与第一方模型护城河（2026-08）

> **概要**: 2026-08 第一周，AI 浏览器赛道三连发——Cloudflare 发布 agent-first 浏览器 **Kitesurf**（官方博客 8/6，全文一手）、**Hark** 预览浏览器使用 agent Handoff（TechCrunch 8/5，$700M Series A）、**Canva** 砍 2026 收入预测 1/3（过度依赖第三方模型）。本文回答：①AI 浏览器赛道如何从「初创已死」演进到「基础设施巨头入局」（三波演进）；②Kitesurf 的技术框架与原理（Rust/Wasm/三组件架构/性能量化）；③为什么基础设施巨头抢占 AI 入口（入口经济学）；④第一方模型护城河的技术本质（与「模型厂商芯片化」同构）。**核心论断：浏览器正在从「人类的网页查看器」变成「agent 的操作面」——谁控制 agent 的操作面，谁就控制 AI 时代的入口；而入口的长期护城河是第一方模型/垂直整合，不是 UI。**
>
> **关键词**: AI 浏览器 · agent 浏览器 · Kitesurf · Cloudflare · 浏览器基础设施 · 入口经济学 · 第一方模型 · 垂直整合 · computer-use agent · 护城河
>
> **数据时点**: 2026-08（Kitesurf 官方博客 8/6 全文一手 + Hark TechCrunch 8/5 全文一手 + Canva 08-09 日报告转述）
>
> **关联知识库**: [模型厂商全面芯片化](./2026-08-10-model-vendor-chip-integration-deep-analysis.md)（垂直整合=第一方护城河的上游镜像）· [AI Agent 深度分析](../../03_AI/agent-engineering/2026-08-03-ai-agent-deep-analysis.md)（工具面/无头浏览器）· [CSP CapEx 专题](../03_server/04_industry/2026-08-07-csp-capex-90pct-ai-server-shipments-deep-analysis.md)（算力需求）· [01_survey/tools 浏览器自动化追踪](../../01_survey/tools/2026-07-30.md)（ego-lite 趋势）· [01_survey/ai-apps 浏览器洗牌](../../01_survey/ai-apps/2026-07-11.md)（Dia/SigmaOS/Browserbase）

---

## 📑 目录

- [1. 核心命题](#1-核心命题)
- [2. 赛道全景：三波演进](#2-赛道全景三波演进)
- [3. Cloudflare Kitesurf 技术深潜（一手全文）](#3-cloudflare-kitesurf-技术深潜一手全文)
  - [3.1 为什么 Cloudflare 自建浏览器](#31-为什么-cloudflare-自建浏览器)
  - [3.2 架构三组件与设计决策](#32-架构三组件与设计决策)
  - [3.3 性能量化与边界](#33-性能量化与边界)
  - [3.4 CDP 兼容=生态策略](#34-cdp-兼容生态策略)
- [4. Hark Handoff：agent 专用模型路线](#4-hark-handoffagent-专用模型路线)
- [5. 入口经济学：为什么基础设施巨头抢占 AI 入口](#5-入口经济学为什么基础设施巨头抢占-ai-入口)
- [6. Canva 教训：第三方模型依赖的三重风险](#6-canva-教训第三方模型依赖的三重风险)
- [7. 护城河矩阵：垂直整合 × 入口控制](#7-护城河矩阵垂直整合-入口控制)
- [8. 对行业格局的影响](#8-对行业格局的影响)
- [9. 风险与批判](#9-风险与批判)
- [10. 路标：P1-P6 可证伪预测](#10-路标p1-p6-可证伪预测)
- [11. 对 AI 基础设施业务的启示](#11-对-ai-基础设施业务的启示)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

## 1. 核心命题

> **AI 浏览器赛道的爆发信号不是「又一款浏览器」，而是「控制 AI 入口的战争」——Cloudflare 用 Kitesurf 把「浏览器」从客户端软件改写成边缘计算负载，基础设施巨头的入场改变了赛道的经济结构。**

三个核心论断：

1. **浏览器正在从「人类的网页查看器」变成「agent 的操作面」**：Kitesurf 的设计哲学说得最直白——「AI 不关心 tabs、主题、扩展、跨设备同步；AI 关心 token 数、上下文窗口、可扩展性、性能、成本」。**浏览器为 agent 重新设计=赛道的新定义**。
2. **入口的长期护城河是垂直整合（第一方模型），不是 UI**：Canva 砍 1/3 收入预测=第三方模型依赖的代价；Hark 从 post-trained 走向 pre-train=agent 专用模型；OpenAI 收购 Browserbase+自研芯片、Anthropic 自研芯片=模型厂商向入口/硬件纵深——**「第一方模型=护城河」与「模型厂商芯片化」是同一条垂直整合逻辑的两端**。
3. **基础设施巨头入局改变了经济结构**：Kitesurf 把浏览器跑在 Workers 边缘（Wasm）——CPU/内存比 Chromium 省 3-7×——**「浏览器」从客户端软件变成「按 token 计费的边缘负载」**，这正是 Cloudflare（边缘网络）而非浏览器公司（Chrome）能赢的物理基础。

---

## 2. 赛道全景：三波演进

| 波次 | 时间 | 玩家 | 命运 | 知识库锚点 |
|:-----|:-----|:-----|:-----|:-----------|
| 第一波：AI 原生浏览器初创 | 2024-2026 | Dia、SigmaOS、Opera Aria、Sidekick | **已死或转型**——「AI 原生浏览器不是好生意」（07-11 结论） | [ai-apps/2026-07-11](../../01_survey/ai-apps/2026-07-11.md) |
| 第二波：浏览器基础设施 | 2026 | OpenAI 收购 **Browserbase**、Playwright、Browser Run、ego-lite（⭐5.9k） | **好生意**——「AI 浏览基础设施（Browserbase/Playwright 类）是好生意」 | [ai-apps/2026-07-11](../../01_survey/ai-apps/2026-07-11.md) · [tools/2026-07-30](../../01_survey/tools/2026-07-30.md) |
| 第三波：基础设施巨头 + agent 专用 | 2026-08 | **Cloudflare Kitesurf**（边缘巨头自建浏览器）、**Hark**（$700M agent 专用）、Google/OpenAI/Anthropic computer-use | **爆发**——基础设施化+模型化两条线同时打通 | [ai-dev-tools/2026-08-08](../../01_survey/ai-dev-tools/2026-08-08.md) |

**三波演进的第一性解释**：

```text
Wave 1 (AI native browser, dead): AI-in-UI
  -> failed because: humans already have browsers; AI-in-UI is a
     feature, not a product (users won't switch browsers for it)

Wave 2 (browser infra, good): browsers for agents
  -> OpenAI buys Browserbase: agents NEED browsers as tools
  -> ego-lite (5.9k stars): login-state sharing for Codex/Claude

Wave 3 (infra giant + agent-native): rewrite for agents
  -> Cloudflare Kitesurf: browser as edge workload (Wasm on Workers)
  -> Hark: agent-specific model (predicts next ACTION not token)
  -> why now: agent adoption reached scale where browser cost/efficiency
     is the binding constraint (memory/CPU per agent session)
```

**关键转折点**：第一波失败的教训（AI 原生浏览器不是好生意）+ 第二波的验证（浏览器基础设施是好生意）→ 第三波的基础设施巨头入场——**Cloudflare 不做「AI 浏览器 UI」，做「agent 浏览器引擎」**，直接复用了第二波的认知。

---

## 3. Cloudflare Kitesurf 技术深潜（一手全文）

> 来源：Cloudflare 官方博客 8/6「Introducing Kitesurf: The agent-first browser that runs in V8 isolates on Cloudflare Workers」（Celso Martinho 等，16 分钟长文，本文为全文一手提取）。URL: blog.cloudflare.com/kitesurf/

### 3.1 为什么 Cloudflare 自建浏览器

**背景**：Cloudflare 内部「要不要自建浏览器」的问题问了很多年，一直搁置。转折=三个条件同时成熟：

1. **平台成熟**：Workers 跑 Wasm 成熟、Dynamic Workers、SQLite-based Durable Objects、Worker-to-worker RPC、更高 NodeJS 兼容性——「更宏大复杂的应用成为可能」
2. **需求爆发**：Browser Run（无头浏览器自动化 API）随 AI 增长爆发——「**agents 需要浏览器执行任务，没有浏览器很多任务无法完成**」
3. **认知转变**：Chromium 为人类设计，带来 agent 不需要的开销——「给每个 agent 一个 Chromium 实例贵到不可行，把大部分 Web 锁在了最昂贵模型的门外」

**设计哲学（原文金句）**：

```text
"AI doesn't care about tabs, themes, browser extensions, or
 synchronization across devices. It cares about token count,
 context windows, scalability, performance, and costs."

"Structured, machine-readable content is important, but visual
 perfection, smooth 60-fps scrolling is not."

"The threat model ... is different. New problems like prompt
 injection and tool safety are top priorities."
```

**推论**：为 agent 设计的浏览器=**按「模型视角」裁剪的浏览器**——保留 DOM/HTML/CSS/selection/SVG/XHR（agent 需要的），砍掉视觉完美/流式滚动（人类需要的）。

### 3.2 架构三组件与设计决策

**请求生命周期**（原文图）：

```text
                 +------------------------------------------+
  CDP/HTTP  -->  |  ENGINE (only stateful component)        |
                 |  - CDP WebSocket + REST API              |
                 |  - session state storage                 |
                 +----+---------------------+---------------+
                      | RPC                  | RPC
                      v                      v
              +---------------+      +------------------+
              | PAGESCRIPT    |      | PAGERENDERER     |
              | (per-page     |      | (stateless,      |
              |  isolate via  |      |  disposable)     |
              |  Dynamic      |      |  - rasterize     |
              |  Workers)     |      |  - blitz-paint   |
              |  - DOM + JS   |      |  - Parley glyphs |
              +-------+-------+      +------------------+
                      |
              +-------+-------+
              | SANDBOXOUTBOUND |
              | (only network   |
              |  egress point)  |
              +-----------------+
```

**三组件**：

| 组件 | 职责 | 关键特性 |
|:-----|:-----|:---------|
| **Engine** | 唯一有状态组件：CDP WebSocket/REST API、session 存储 | 客户端兼容（Puppeteer/Playwright 直接用）；「最简组件」 |
| **PageScript** | 每页一个 Dynamic Worker isolate：DOM 文档对象 + 运行 JS | **blitz 渲染引擎**（Rust）+ **Stylo**（Firefox CSS 解析器，Rust）+ **Boa JS**（eval 运行时 on runtime）；OOPIF 支持 |
| **PageRenderer** | 从页面对象生成像素：rasterize→PNG/JPEG/PDF | blitz-paint + **Parley**（字体排版）；无状态可随意 kill/重启 |
| **SandboxOutbound** | 唯一网络出口 worker：CORS 强制、浏览器头注入、响应过滤、每页 cookie jar | 不可信输入原则：**每页都是 untrusted input，每会话全新开始** |

**设计决策（五条，原文）**：

1. **测试驱动 AI 开发**：用 Web Platform Tests（WPT）作为 agent 开发的成功判据——「人工做架构+审查，agent 跑功能实现」；WPT 之外补集成测试+视觉回归（Puppeteer 多步真实网站测试，Chromium vs Kitesurf 逐帧对比）
2. **Rust 优先**：原生 Rust 编译 Wasm（wasm-bindgen），避免 Emscripten 模拟层——「尽可能贴近金属」
3. **异常处理=生存法则**：任何失败降级为空白帧/缺失元素，**绝不 dead session**——「catch faults at every boundary, default to safe and empty」
4. **隔离默认**：每页面 untrusted input——组件间最小权限，配合 Workers isolate 边界
5. **无状态优先**：无状态=可丢弃+可并行+按需伸缩——「kill the moment it stalls, run a thousand at once」

### 3.3 性能量化与边界

**性能（14-URL 语料库，5 次中位数，对比 Chromium warm pool）**：

| 指标 | Kitesurf | Chromium | 相对 |
|:-----|:---------|:---------|:-----|
| CPU：截图 | 380 ms | 1,173 ms | **3.1× 更省 CPU** |
| CPU：HTML 提取 | 229 ms | 877 ms | **3.8× 更省 CPU** |
| 内存：截图 | 57.8 MiB | 271.0 MiB | **4.7× 更省内存** |
| 内存：HTML 提取 | 39.4 MiB | 273.7 MiB | **7.0× 更省内存** |
| 墙钟：截图 | 1,148 ms | 637 ms | 1.8× 慢 |
| 墙钟：HTML 提取 | 820 ms | 472 ms | 1.7× 慢 |

**第一性解读**：Chromium 的 JIT 见过页面后总是快（墙钟胜 1.7×），但**账单由 CPU/内存驱动**——Kitesurf 省 3-7× 意味着「同样预算跑 3-7× 更多 agent 会话」。**效率优势=成本结构优势，这正是 agent 规模化后的瓶颈**（agent 会话数×每会话浏览器开销）。

**当前边界（不能做什么）**：视频、WebGL、bot-challenge 握手（真实 TLS 指纹）、需要持久状态的长会话（10 分钟）——这些仍走 Chromium 默认。**兼容策略=「能做的用 Kitesurf，不能做的回退 Chromium」**。

**成熟度**：215,000+ WPT 测试通过（每周数百新增）；TodoMVC（vanilla/React/Vue/Angular/Preact）、Wikipedia、HN、Cloudflare Blog 渲染正确；**跑通 Doom**（「项目不完整直到 Doom 跑起来」）。

### 3.4 CDP 兼容=生态策略

**关键设计**：Engine 实现 Chrome DevTools Protocol（CDP）——Puppeteer、Playwright、chrome-remote-interface、Chrome DevTools frontend **全部直接可用**。

```json
// Connect: Browser Run endpoint with browser=kitesurf param
{
  "mcp": { "kitesurf": {
    "type": "local",
    "command": ["npx", "-y", "chrome-devtools-mcp@latest",
      "--wsEndpoint=wss://api.cloudflare.com/.../browser?browser=kitesurf"]
  }}
}
```

**战略含义**：CDP 是浏览器的「事实 API」——**用 CDP 兼容换取生态零迁移**（agent 工具链/MCP 客户端直接可用），同时保持引擎完全自主（Rust/Wasm）。计划开源（「hopefully soon」），让客户自部署——**开源+CDP 兼容=对抗 Chromium 生态锁定的双保险**。

---

## 4. Hark Handoff：agent 专用模型路线

> 来源：TechCrunch 8/5（Ivan Mehta）全文一手。URL: techcrunch.com/2026/08/05/hark-previews-its-browser-use-agent-for-completing-tasks/

**事实层**：
- Hark 2026-05 完成 **$700M Series A**（重大融资）
- 发布 agent **Hark Handoff**：浏览器使用 agent，自动完成网页任务
- 能力：无官方 API 网站（Target/Walmart/OpenTable/LinkedIn）——「看网站结构和视觉数据决定是否点击/输入」
- 演示：按指令建花束，能处理模糊指令（「some of the florist's choice」）
- **当前用 post-trained 模型，计划今年晚些时候 pre-train**——「post-train 先打磨数据管道/训练基建/技术，再 pre-train」
- 声称比 GPT 5.5/Opus 4.8 更快更便宜
- 竞品：Google/OpenAI/Anthropic computer-use + Browser Use/Polar/Strawberry/Aside
- 夏末发布（waitlist）

**技术亮点：next-action 预测模型**：

```text
Standard LLM:  predict next TOKEN  (autoregressive language)
Hark Handoff:  predict next ACTION (a click / keyboard input
                at a specific location)

-> action space = (action_type, x, y, text, element_ref)
-> browser-use as FIRST-CLASS output, not serialized text
-> post-trained on browser trajectories -> pre-train later
```

**第一性解读**：LLM 的 next-token 训练目标与「在网页上正确操作」之间存在**表示缝隙**（token 序列 ≠ 动作序列）。Hark 直接预测动作=**消除表示缝隙**（与 Kitesurf 的「为 agent 重写浏览器」是同一逻辑的两端：一个改模型输出空间，一个改浏览器输入空间）。post-train→pre-train 路径说明：**先用现有底座验证数据管道，再全栈自研**——与 OpenAI/Anthropic 芯片策略（先 Broadcom/合作，后自研）同构。

---

## 5. 入口经济学：为什么基础设施巨头抢占 AI 入口

**浏览器=数字入口的历史**：Netscape（1990s 入口战）→ IE → Chrome（浏览器=OS 之上最厚的层）——**控制浏览器=控制分发=控制利润池**（Chrome 的广告/搜索默认位）。AI 时代入口逻辑不变，但形态变了：

```text
HUMAN ERA                          AGENT ERA
browser = human reads pages        browser = agent operates pages
entry = URL bar + tabs             entry = agent's tool surface
distribution = default search      distribution = agent's default browser
monetization = ads + subscriptions monetization = per-token/per-action
competition = UI + speed           competition = cost + compatibility
```

**入口三层结构**：

| 层 | 玩家 | 入口资产 | 护城河 |
|:---|:-----|:---------|:-------|
| 模型层 | OpenAI/Anthropic/Google | 推理能力=agent 大脑 | 模型质量+数据飞轮 |
| 浏览器层 | Chrome/Cloudflare Kitesurf/Hark | agent 操作面 | 成本结构+兼容性+生态 |
| 基础设施层 | Cloudflare/边缘网络 | 全球边缘+隔离+算力 | 分发+信任+规模 |

**Cloudflare 的战略逻辑**：Cloudflare 不做模型（模型层无优势），但它的边缘网络（全球 300+ 城市）、Workers 隔离模型、Browser Run 存量客户=**浏览器层的物理基础**。Kitesurf 把浏览器变成「边缘负载」（Wasm on Workers）——**这是浏览器第一次按「基础设施」而非「客户端软件」构建**：无状态、可伸缩、按用付费、全球分发。基础设施巨头抢占 AI 入口的方式=**把入口做成自己的主场负载**。

**为什么是现在**：agent 采用达到规模（Browser Run 增长、computer-use 成为标配）→ 浏览器成本成为绑定约束 → 成本结构（3-7× 效率差）变成竞争武器。

---

## 6. Canva 教训：第三方模型依赖的三重风险

> 素材：08-09 日报告转述「Canva 砍 2026 收入预测 1/3：过度依赖第三方模型」——**一手细节待补充**（仅知识库日报告一句话，已标注）。

**Canva 案例的教训（第一性展开）**：

```text
Third-party model dependency = renting someone else's moat

Risk 1: COST is priced by upstream
  -> model API price changes directly hit your margin
  -> you cannot optimize the model layer (it's a black box)

Risk 2: CAPABILITY is decided by upstream
  -> model roadmap gates your product roadmap
  -> "AI features" are commoditized: everyone using GPT-5.6
     ships the same features (no differentiation)

Risk 3: PROFIT POOL is captured upstream
  -> value flows to the model owner (who also has distribution)
  -> your product becomes a thin UI on someone else's moat
  -> the model owner can integrate your use case natively
```

**为什么「第一方模型=护城河」**：垂直整合（模型+产品+分发）把三层风险内部化——Google（TPU+Gemini+Chrome/搜索/YouTube）、OpenAI（模型+ChatGPT 入口+芯片计划）、Meta（MTIA+Llama+社交分发）都是全栈；Canva 是反例（设计工具依赖第三方模型，功能可被模型厂商/竞品复制）。

**第一方模型的边界（不万能）**：
1. 成本门槛：自研模型 = 训练算力 + 人才 + 数据——只有规模玩家付得起
2. 时间门槛：从建团队到模型可用 1-2 年（芯片则 3-5 年）——窗口期风险
3. 分化风险：第一方模型若质量落后，护城河变成本坑（Hark 的 post-train→pre-train 就是「先验证再全栈」的保守路径）

---

## 7. 护城河矩阵：垂直整合 × 入口控制

```text
                 HIGH vertical integration (own model)
                 +----------------------------------+
                 |  Google (TPU+Gemini+Chrome)      |
                 |  OpenAI (model+ChatGPT+chip)     |
                 |  Meta (MTIA+Llama+distribution)  |
  LOW entry  ----+----------------------------------+---- HIGH entry
  control        |  Canva (design product only)     |    control
                 |  (third-party model)             |    (browser/infra)
                 +----------------------------------+
                 |  Cloudflare Kitesurf (no model,  |
                 |   but owns agent browser+edge)   |
                 |  Hark (own agent model + browser)|
                 +----------------------------------+
                 LOW vertical integration
```

**象限分析**：

| 象限 | 代表 | 护城河逻辑 | 风险 |
|:-----|:-----|:-----------|:-----|
| 高整合×高入口 | Google | 全栈闭环（模型+云+浏览器+分发） | 反垄断+组织惯性 |
| 高整合×中入口 | OpenAI/Anthropic | 模型质量+入口（ChatGPT）+向硬件纵深（芯片化） | 芯片 3-5 年交期 |
| 低整合×高入口 | Cloudflare | agent 浏览器+边缘=入口成本结构 | **无模型=入口是「管道」非「终点」**——模型厂商可自建 |
| 低整合×低入口 | Canva（警示） | 产品体验 | **第三方模型依赖=最脆弱象限** |
| 中整合×中入口 | Hark | agent 专用模型+浏览器 agent | $700M 融资=烧钱验证期，竞争激烈（Google/OpenAI/Anthropic 都在做） |

**关键张力**：Cloudflare 的「入口+基础设施无模型」模式（低整合×高入口）——**入口如果是纯管道，护城河有限**（模型厂商可自建浏览器/浏览器可被模型厂商收购）；但 Cloudflare 的**成本结构优势（3-7×）+ 边缘规模**是模型厂商短期难复制的物理资产。**长期看：入口控制 × 垂直整合会收敛——没有模型的入口玩家要么向上整合（做模型），要么被有模型的玩家夹击**。

---

## 8. 对行业格局的影响

1. **Chrome 的 AI 化防御**：Google 不会坐视 agent 浏览器（Kitesurf/专用引擎）绕过 Chrome——Chrome 的 AI 功能（内置 agent/会话）是防御线；但 Chrome 的「为人类设计」架构（内存/CPU 开销）与 agent 效率需求存在根本张力。
2. **浏览器基础设施标准化**：CDP 是事实标准（Kitesurf 兼容），MCP+CDP 成为 agent 浏览器接入方式——**标准层在固化**（与知识库「协议边界」判断一致）。
3. **广告/分发模式变革**：agent 浏览器按 token/action 计费（非广告）——若 agent 成为主要入口，**广告商业模式被侵蚀**（Google 的核心风险），分发从「搜索默认位」变「agent 默认工具」。
4. **模型厂商的浏览器化**：OpenAI 已收购 Browserbase（浏览器基础设施）；ChatGPT 浏览器化/computer-use 是模型厂商的入口野心——**模型厂商×基础设施巨头在浏览器层正面相遇**。
5. **算力需求形态变化**：agent 浏览器=每 agent 会话的持续算力消耗（渲染/推理）——**agent 规模×会话时长=新算力负载形态**，对超节点/AI 基础设施是需求增量（但 Kitesurf 的 3-7× 效率也意味着单位任务算力需求下降——两者对冲，净效应待观察）。

---

## 9. 风险与批判

1. **Canva 素材薄弱**：仅知识库日报告一句话（「砍 2026 收入预测 1/3：过度依赖第三方模型」）——**一手原文未获取**，本文 §6 的「三重风险」为第一性展开而非 Canva 官方表述，引用需谨慎（待补 Canva 财报/声明原文）。
2. **Kitesurf 是 12 周产物**：beta 阶段（免费+per-account 限制），215K WPT 通过但「不能做的很多」（视频/WebGL/长会话）——**生产级成熟度未验证**；性能对比是 Cloudflare 自测（14-URL 语料库），独立验证缺位。
3. **Hark 性能声称无独立验证**：「比 GPT 5.5/Opus 4.8 更快更便宜」为厂商声称；视频演示只展示部分过程（TechCrunch 原文「can't really gauge its effectiveness」）。
4. **单一来源风险**：Kitesurf 技术细节全出自 Cloudflare 官方博客（利益叙事）；Hark 出自 TechCrunch 单篇。
5. **「入口战争」叙事可能高估**：agent 浏览器是新增市场，不必然替代人类浏览器——Chrome 仍是人类主入口；「入口=利润池」的历史类比需谨慎（agent 浏览器商业模式（按量计费）尚未验证）。
6. **垂直整合反向风险**：第一方模型若拖累产品（质量/成本），护城河变负担——Hark 的 post-train→pre-train 说明连 Hark 都意识到「先验证再全栈」。

---

## 10. 路标：P1-P6 可证伪预测

| 预测 | 内容 | 证伪条件 | 核验窗口 |
|:----:|:-----|:---------|:---------|
| P1 | Kitesurf 开源后成为 agent 浏览器事实标准之一：GitHub star ≥10K 且被 ≥3 家独立部署 | star <10K 或部署 <3 | 2027-06 |
| P2 | 2027 年前 ≥1 家模型厂商（OpenAI/Anthropic/Google）发布自研 agent 浏览器引擎（不依赖 Chromium） | 无厂商发布 | 2027-06 |
| P3 | Canva 事件后，≥2 家大型 SaaS 宣布自研/收购模型团队（第一方模型扩散） | 宣布 <2 | 2027-06 |
| P4 | agent 浏览器计费模式定型为「按量」（token/action），广告模式占比下降 | 广告仍是主要变现 | 2027-06 |
| P5 | Hark Handoff 夏末发布后 6 个月内 MAU 达 100 万级或融资/被收购（$700M 验证路径） | 6 个月无规模信号 | 2027-06 |
| P6 | Chrome 发布 agent 专用模式（降低内存/CPU 的 agent 模式）作为防御 | Chrome 无 agent 模式 | 2027-06 |

**P1-P6 逻辑**：P1 验证开源策略，P2 验证「模型厂商入口野心」，P3 验证「第一方模型扩散」，P4 验证商业模式变革，P5 验证 Hark 路线，P6 验证 Chrome 防御。

---

## 11. 对 AI 基础设施业务的启示

1. **agent 浏览器=新算力负载形态**：每 agent 会话的持续渲染/推理消耗——**超节点/AI 基础设施的负载画像需加入「agent 会话」维度**（agent 规模×会话时长），与训练/推理并列。
2. **效率是 agent 规模化的瓶颈**：Kitesurf 的 3-7× 效率差说明——**单位任务算力需求下降 vs agent 数量增长的对冲**决定 AI 基础设施的真实需求曲线；基础设施设计应假设「高并发小任务」（agent 会话）而非「大任务低并发」（训练）。
3. **浏览器/渲染=新的边缘负载**：Kitesurf 把渲染放边缘（Wasm on Workers）——**边缘计算从 CDN 缓存扩展到渲染/agent 执行**，对网络基础设施（边缘节点/算力）是增量需求。
4. **垂直整合的镜像参考**：第一方模型护城河（Canva 反例）+ 模型厂商芯片化（上篇）——**对国产生态的启示：入口（浏览器/操作系统）× 模型 × 芯片的三层垂直整合是长期护城河形态**（华为鸿蒙+昇腾=同一逻辑）。
5. **CDP/MCP 标准红利**：浏览器基础设施标准化（CDP 事实标准+MCP 接入）——**国内 agent 浏览器/自动化工具应尽早对齐 CDP/MCP**，避免生态分裂成本（与知识库「协议化得生态」判断一致）。

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [模型厂商全面芯片化](./2026-08-10-model-vendor-chip-integration-deep-analysis.md) — 垂直整合=第一方护城河的上游镜像，与本文入口护城河同构
- [AI Agent 深度分析](../../03_AI/agent-engineering/2026-08-03-ai-agent-deep-analysis.md) — 工具面/无头浏览器场景
- [CSP CapEx 专题](../03_server/04_industry/2026-08-07-csp-capex-90pct-ai-server-shipments-deep-analysis.md) — 算力需求侧背景
- [01_survey/tools 浏览器自动化追踪](../../01_survey/tools/2026-07-30.md) — ego-lite 趋势
- [01_survey/ai-apps 浏览器洗牌](../../01_survey/ai-apps/2026-07-11.md) — Dia/SigmaOS/Browserbase 复盘

### 外部资料引用

- 来源: Cloudflare 官方博客「Introducing Kitesurf: The agent-first browser that runs in V8 isolates on Cloudflare Workers」(2026-08-06), blog.cloudflare.com/kitesurf/（全文一手提取：三组件架构/WPT 215K/性能对比表/CDP 兼容/五设计决策/边界）
- 来源: TechCrunch「Hark previews its browser use agent for completing tasks」(2026-08-05, Ivan Mehta), techcrunch.com/2026/08/05/hark-previews-its-browser-use-agent-for-completing-tasks/（全文一手提取：$700M Series A/Handoff/next-action 模型/post-train→pre-train）
- 来源: 知识库日报告 2026-08-09（Canva 砍 1/3 收入预测，一手原文待补）

> **验证声明**：Kitesurf 与 Hark 为本次 web_fetch 一手全文（高可信）；Canva 为知识库日报告转述（低可信，一手原文未获取）；赛道演进（第一波/第二波）来自知识库 07-11 归档。性能数字为 Cloudflare 自测（14-URL 语料库），标注为厂商口径。

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-08-10 | v1.0 | 初稿：三波演进全景 + Kitesurf 技术深潜（一手全文）+ Hark next-action 模型 + 入口经济学 + 第一方模型护城河矩阵 + P1-P6 路标 |
| 2026-08-22 | v1.1 | 提升：补齐 std-002 五元素 + 跨文件交叉链接与一致性勘误 |
