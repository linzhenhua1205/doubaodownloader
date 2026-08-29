# 🚀 AMD Advancing AI 2026 路线图：CPU 两年一代 × 机架每年一代

> **事件**: Advancing AI 2026 年度大会（2026-07-24 旧金山 Moscone Center West，AMD 最大规模活动，被 STH 称为"AMD 版 GTC"），苏姿丰主题演讲
> **归档日期**: 2026-08-05 | **关联**: [agentic-cpu-ppt](../../03_AI/train/agentic-cpu-ppt/slide_outline.md)（汇报 PPT 已据此补齐 Part 2/3/4）
> **来源分级**: ✅ STH《AMD Advancing AI 2026 Keynote Live Coverage》7/23 现场实况（一手）· ⚠️ 华泓智能微信《AMD 公布 AI/HPC 芯片路线图》7/24（二手编译，其中 Helios 600 配套细节与 "Ravenna" 拼写未在 STH 实况出现，以 STH 为准）

---

## 一、CPU 路线图（两年一代，Zen 微架构代际清晰）

| 代际 | 微架构 | 型号 | 时间 | 要点 |
|:-----|:-------|:-----|:-----|:-----|
| 当前 | Zen 5 | Turin（都灵） | 在售 | "世界上最好的服务器 CPU"（AMD 自称） |
| 2026 | **Zen 6** | **Venice**（威尼斯） | 2026H2 量产 | TSMC 2nm，最高 **256 核/socket**；"EPYC 史上最大代际提升之一" |
| 2027 | Zen 6 衍生 | **Verano**（韦拉诺） | 2027 | 下一代 rackscale（Helios 500）配套 CPU |
| 2028 | **Zen 7** | **Florence**（佛罗伦萨）+ Ferrara/Fidenza 变体 | 2028 | 支持最新内存技术 |
| 2030 | **Zen 8** | **Ravenna**（⚠️ 勘误：STH 实况转写 "Rivenna"，AMD 官方新闻稿正式拼写 "Ravenna"，以官方为准） | 2030 | 开发中 |

**Venice 家族四型（"多样性 CPU"策略）**：
- **Venice HF**：128 核高主频，Helios 机架内使用（GPU 引导 + Agent 执行）
- **Venice Dense**：**256 核** 密集吞吐型
- **Venice 通用**：128 核，通用计算
- **Venice-X**：**3D 堆叠缓存**（cache chiplets 在 compute chiplets 下方）

**性能锚点（AMD 声称，未独立验证）**：
- 2× perf/agents per watt vs 竞争；与 Arm 竞品差距更大
- vs NVIDIA Vera：**2.2× performance per socket**（AMD 强调全芯片吞吐而非单核）
- x86 软件兼容性叙事："Everything (still) runs on x86"

## 二、机架级系统路线（每年一代，替代 GPU 一年一代节奏）

| 系统 | GPU | CPU | 网络（Pensando） | 时间 |
|:-----|:-----|:-----|:-----------------|:-----|
| **Helios** | 72× MI455X（432GB HBM4/GPU） | Venice HF | Vulcano NIC | **2026Q3 出货**，2027H2 ramp（已全生产） |
| **Helios 500** | MI500（2027，史上最大代际跃升） | **Verano**（EPYC 9006 LP） | Como + Monza | 2027 |
| **Helios 600** | MI600（CDNA Next，2028） | **Ferrara**（Zen 7） | Palma + Levanzo | 2028（⚠️微信来源，STH 未详述） |

**配套 GPU 路线**：MI455X（在售）→ MI430X HPC（2027H1，288 TFLOPS FP64，FP64 硬件加速，与 MI455X 同内存）→ MI500（2027）→ MI600 CDNA Next（2028）。Instinct 每年一代。

**Helios 关键数据（STH 实况）**：50% 更多内存容量、15% 更多 FP4 性能、vs MI355X **34× token throughput**、10-15% 更高效、**30% 更多 tokens/$ vs 竞争**（均 AMD 声称）；容错=网络单点全补偿免 checkpoint 重载（✅知识库已有）。

**超低延迟解聚**：Cerebras × AMD——Helios + Wafer Scale Engine 解聚方案，5× WSE 单独性能，年内 Cerebras 云服务可用（类 NVIDIA×Groq 组合）。

## 三、市场叙事与数据（AMD 官方口径，⚠️未独立验证）

- **inference 已超过 training**："More AI compute capacity is used for inference than training"——推理成主战场（行业级关键信号）
- AMD 数据中心 CPU **营收份额 46%**（创新高），随 agentic AI 对 CPU 编排依赖加深将持续增长
- **AI accelerator TAM $1.4T（2030）** = 今天整个芯片市场规模
- **CPU 市场 $220B（2030）**："Agentic AI needs a lot of CPUs to actually handle the tasks the agents are running, never mind orchestrating the GPUs"（苏姿丰）
- 总 silicon TAM **$2T（2030）**，40% CAGR
- **大单验证**：Anthropic 2GW Helios 硬件采购（本周宣布）；OpenAI 去年宣布 6GW AMD 硬件（部署中）+ 年底开始部署 Helios、期待 MI500
- 客户观点：Meta（Santosh Janardhan）——"CPUs are becoming just as important as GPUs, if not more"；AT&T 月耗 ~1 万亿 token

## 四、软件栈提速（ROCm）

- ROCm 发布节奏：每 **6 周**一个 release（原数月）
- **ROCm.AI**：基于 Codex/Claude 等编码 Agent + AMD 自有工具（ROCm skills + Hyperloom 代码/性能优化工具）——AI 写 GPU kernel 已成内部实践
- **Hyperloom** demo：提升 token rate **38%**
- 最新 ROCm：推理性能 **+3.3×**（vs ROCm 7）、训练 **+2.4×**
- MI350P（PCIe HBM 加速卡）：企业推理部署；智能路由降 token 成本 43%（AMD 内部实践）

---

## 五、对服务器产品研判的含义（衔接 agentic-cpu-ppt）

1. **推理>训练确认**：行业级拐点由 AMD 官方站台——推理基础设施是当前与未来主战场，PPT Part 2 前提获一手背书
2. **CPU 叙事被头部厂商亲自强化**：苏姿丰"CPU 编排器" + Meta"CPU 与 GPU 一样重要" + CPU 市场 $220B——**Agentic CPU 需求不是推测而是共识**（与 NVIDIA Vera/Intel Xeon 三线汇合）
3. **AMD 路线图给出确定性时间窗**：Venice（2026H2）→ Verano（2027）→ Florence（2028）→ Rivenna（2030），两年一代可规划；**机架每年一代**（Helios→500→600）与 NVIDIA 的节奏对打，72-GPU 双雄竞争升级为路线图竞争
4. **开放生态获大单验证**：Anthropic 2GW / OpenAI 6GW——AMD 开放平台叙事落地，**开放 scale-up（UALink）卡位的机会面被验证**
5. **软件栈成为竞争主战场**：ROCm 6 周节奏 + ROCm.AI + Hyperloom——"软件是护城河"判断获厂商侧印证（PPT Part 4）
6. **超低延迟解聚是新形态**：Cerebras×AMD 解聚（ULL 推理）——推理形态分化（吞吐型/延迟型）正在催生异构组合

---

## 📝 变更记录

- 2026-08-05: 归档。来源=STH 实况全文 + 华泓智能微信文章（交叉验证，差异已标注）；用于补齐 agentic-cpu-ppt Part 2-4。
