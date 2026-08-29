# 🌍 推理 GPU「容量型 SKU」五看三定 — 国际版

> **版本**: v1.0
> **日期**: 2026-08-11
> **地理范围**: 北美 / 欧洲 / 中东 / 东南亚（非中国）
> **核心问题**: 在 NVIDIA 生态碾压 + HBM 危机 + tokens-as-a-service 爆发的国际市场，服务器厂商如何落地「容量型推理 SKU」（E1-E5 五条执行线）？
> **概要**: 国际版五看三定——以一手财报数据（NVIDIA FY2026 全公司总营收 $215.9B，其中 Data Center 段 $193.7B / Intel DCAI $6.3B / AMD 数据中心 $30B 预测）与机构预测（AI 服务器 +31%、超节点 $136B）为底座，论证「容量型 SKU」在国际市场是 **「成本 × 供应确定性 × 长尾场景」三角驱动的差异化补位**：NVIDIA 统治训练+高吞吐推理，容量型 SKU 吃「大内存低带宽 + 风冷」的长尾——tokens-as-a-service 服务商、主权 AI、企业私有化三块市场。
> **关键词**: 容量型 SKU · 国际版 · tokens-as-a-service · 主权 AI · LPDDR5X · CXL · NVIDIA 生态 · B300 PCIe
> **适用对象**: 海外产品线负责人、国际业务、AI 基础设施架构师
> **关联**: [总纲框架](2026-08-11-inference-gpu-capacity-sku-strategy-framework.md) · [Intel Crescent Island 分析](2026-08-11-intel-crescent-island-inference-gpu-competitive-analysis.md)

---

## 目录

- [0. 一句话结论](#0-一句话结论)
- [一、看宏观/行业](#一看宏观行业)
- [二、看市场/客户](#二看市场客户)
- [三、看竞争](#三看竞争)
- [四、看自身](#四看自身)
- [五、看机会](#五看机会)
- [六、定战略](#六定战略)
- [七、定目标](#七定目标)
- [八、定策略（P0/P1/P2 执行）](#八定策略p0p1p2-执行)
- [九、风险与应对](#九风险与应对)
- [十、监控与迭代](#十监控与迭代)
- [参考文件](#参考文件)
- [变更记录](#变更记录)

---

## 0. 一句话结论

**国际市场上，「容量型 SKU」不是跟 Intel 的赌注，而是对 NVIDIA 统治的「成本套利」——NVIDIA Data Center FY2026 营收 $193.7B (+68%，占 NVIDIA 全公司 $215.9B 总营收约 90%) 证明高端市场由它垄断，但 HBM 危机（DRAM 涨价 5×）+ tokens-as-a-service 服务商对单位 token 成本的极致追求，正在撕开「大内存低带宽 + 风冷」的容量型窗口。服务器厂商应以 B300 PCIe / MI350P / Intel 平台为基座，把「容量型 SKU」做成对推理云与主权 AI 客户的成本武器，目标 TCO/token ≤ NVIDIA HBM 机型的 1/2。**

---

## 一、看宏观/行业

### 1.1 PESTEL 分析

| 维度 | 现状（2026-08） | 数据/依据 | 对容量型 SKU 的意义 |
|:-----|:---------------|:---------|:-------------------|
| **P 政策** | 美国 CHIPS Act 持续注资；出口管制收紧（H20 已两次受挫）；主权 AI 成为各国战略 | 知识库 08-10 出口管制双供应链 + Intel 财报提及 | 非 NVIDIA 路线在主权市场获得政策偏好（供应安全） |
| **E 经济** | AI 投资 $581B（2025，斯坦福 AI 指数）；九大 CSP CapEx +90%（口径待定）；HBM/DRAM 超级周期（涨价 5×） | 斯坦福 2026 指数 + 知识库 08-07 CSP CapEx + 08-10 存储超级周期 | HBM 危机推高高端机型成本 → 容量型成本优势放大 |
| **S 社会** | Agentic AI 采用爆发（"enterprise adoption of agents is skyrocketing"—黄仁勋）；tokens-as-a-service 商业模式成型 | NVIDIA FY2026 财报高管原话 | 推理 token 消耗量级跃升 → 容量型需求端成立 |
| **T 技术** | 推理主导时代（"Grace Blackwell with NVLink is the king of inference today"）；Rubin 推理 token 成本 -10×；LPDDR5X 大容量路线被 Intel 验证 | NVIDIA FY2026 财报 + Intel Crescent Island 发布 | 推理架构正从"训练附属"变为"一等公民"，容量型是其中一支 |
| **E 环境** | 数据中心功耗/碳约束升级；风冷低功耗价值上升 | 知识库 800V HVDC/液冷专题 | 风冷容量型 = 低 PUE 部署（无液冷改造） |
| **L 法律** | 出口管制影响中国业务（NVIDIA 指引"不假设中国 Data Center 收入"）；主权 AI 数据本地化立法 | NVIDIA FY2026 财报 outlook 原话 | 主权 AI 市场成为非中国+非美国的第三极 |

### 1.2 产业链结构

```text
[Upstream memory]        [Midstream silicon]       [System]            [Customers]
LPDDR5X (SK hynix,        Intel Crescent Island     OEM/ODM              Inference clouds
 Samsung, Micron)    --->  AMD Instinct MI350P  ---> (Dell/SMCI/HPE/ ---> (Together/Baseten/
CXL (Samsung/Micron/       NVIDIA B300 PCIe          Quanta/Wiwynn)       Fireworks/DeepInfra)
 Astera/CXL 3.2)           Xeon 6 CPU (AMX)                              Sovereign AI
                                                                         Enterprise private
```

| 环节 | 玩家 | 壁垒 | 利润水平 | 对容量型 SKU 的意义 |
|:-----|:-----|:-----|:---------|:-------------------|
| 上游内存 | 三星/海力士/美光（LPDDR5X/CXL） | 制程+产能 | 高（超级周期） | LPDDR5X 供应充裕，成本低于 HBM |
| 中游芯片 | NVIDIA（垄断）/ AMD / Intel | 架构+生态 | 极高（NVIDIA 71% GM） | 容量型路线 = 非 HBM 芯片的差异化机会 |
| 系统集成 | OEM/ODM（Dell/Quanta/Wiwynn/鸿海） | 规模+交付 | 低（5-10%） | 服务器厂商在此环节竞争 |

### 1.3 行业阶段判断

**S 曲线定位**：推理 GPU 处于成长期中段——技术路线未收敛（HBM 高带宽 vs LPDDR5X 大容量 vs CXL 池化三线并进），市场高速增长但格局未定。**容量型是"成长中的细分"，不是"成熟后的替换"**——这正是入局窗口。

---

## 二、看市场/客户

### 2.1 市场规模（TAM-SAM-SOM）

| 指标 | 2026E | 2027E | 2028E | 来源 |
|:-----|:-----:|:-----:|:-----:|:-----|
| 全球 AI 服务器出货 | ~330-390 万台 (+31%) | ~430-500 万台 | — | 知识库 08-07（TrendForce 口径） |
| 全球 AI GPU 出货 | 700 万颗 | 900 万颗 | 1,100 万颗 | 知识库超节点市场分析 |
| 超节点本体市场 | $136B | $225B | $330B | 知识库超节点市场分析 |
| AI 服务器占整体服务器 | 25-30% | — | — | 知识库 06-26 归档 |
| NVIDIA Data Center 营收 | $193.7B（FY26 实际） | $260B+（Q1 指引 $78B 外推） | — | NVIDIA 官方财报 |

**推理细分市场（容量型可服务）**：

| 细分 | 规模估计 | 容量型适配度 | 依据 |
|:-----|:---------|:------------|:-----|
| **tokens-as-a-service 推理云** | 快速增长的数十亿美元级 | ⭐⭐⭐ 高（成本敏感+长上下文） | Baseten/DeepInfra/Fireworks/Together 在 NVIDIA Blackwell 上成本 -10×（NVIDIA 财报） |
| **主权 AI**（欧洲/中东/东南亚） | 数百亿美元级（各国 1-10GW 规划） | ⭐⭐⭐ 高（供应安全+风冷易部署） | 知识库 08-07 APAC 主权算力经济学 |
| **企业私有化推理** | 中速增长 | ⭐⭐ 中（偏好标准 HBM） | — |
| **CSP 边缘推理** | 大但 NVIDIA 占主导 | ⭐ 低（生态锁定） | — |

**TAM-SAM-SOM 估算**（⚠️ 推算，参数显式）：
- **TAM**：全球推理服务器市场 2026E ≈ $120-150B（AI 服务器总盘子的推理占比 40-50%，知识库 08-07 训练/推理构成分析）
- **SAM**：非 NVIDIA 生态可服务的推理市场 ≈ $20-30B（Intel/AMD/开放硬件份额，2026）
- **SOM**：容量型 SKU 2027E 可获 ≈ $1-2B（1-2% 推理市场，需 2-3 个标杆客户）

### 2.2 客户画像与需求

| 客户类型 | 核心需求 | 痛点 | 付费意愿 | 容量型卖点 |
|:---------|:---------|:-----|:---------|:-----------|
| **推理云**（Together/Baseten/Fireworks/DeepInfra） | 单位 token 成本最低、长上下文支持、vLLM 生态 | HBM 机型太贵、容量不够跑 128K+ 上下文 | 高（成本直接决定毛利） | TCO/token ≤ 1/2、160GB 级容量、风冷免液冷 |
| **主权 AI** | 供应安全、本地部署、合规 | NVIDIA 供货受限/地缘风险 | 高（战略投资） | 非 NVIDIA 依赖、开放硬件、本地化服务 |
| **企业私有化** | 易部署、TCO、隐私 | 液冷改造成本高、运维复杂 | 中 | 风冷即插即用、低功耗 |
| **CSP 边缘** | 规模、成本 | 生态锁定 | 中 | —（非目标市场） |

**付费意愿验证**：NVIDIA 财报原话——"leading inference providers, including Baseten, DeepInfra, Fireworks AI and Together AI, cut AI costs by up to 10x with open source models on NVIDIA Blackwell"——证明推理云对成本的极致敏感；容量型 SKU 提供的是**非 NVIDIA 路线的成本替代**。

---

## 三、看竞争

### 3.1 竞争格局（2026-08，数据驱动）

| 竞争者 | 产品/状态 | 数据 | 优势 | 劣势 | 对容量型 SKU 的威胁 |
|:-------|:---------|:-----|:-----|:-----|:-------------------|
| **NVIDIA** | B300/GB300 统治；Rubin 2026H2 出货；**B300 PCIe 风冷版本** | FY2026 DC $193.7B (+68%)、GM 71%、Q1 FY27 指引 $78B | 生态垄断、推理架构显式优化、Rubin token 成本 -10× | 价格高、HBM 供应受限、功耗高 | ⚠️ B300 PCIe 是容量型最大对手（NVIDIA 也在做风冷 PCIe） |
| **AMD** | MI350P（HBM PCIe 卡）、Helios 72×MI455X、ROCm 追赶 | 数据中心 2026E $30B → 2028E $81B（预测） | 性价比、开放、HBM4 路线 | 生态弱于 CUDA、推理优化晚 | 🟡 MI350P 与容量型定位接近（PCIe+风冷） |
| **Intel** | Crescent Island 160GB LPDDR5X 风冷（2026H2 送样/2027 上市）；Xeon 6 AMX 推理；DCAI $6.3B (+59%) | Intel Q2 2026 财报；**8/10 宣布 $15B 增发** | 容量型首创、风冷、CPU 协同 | 算力未知、资金紧张（$15B 增发）、生态弱 | 🟢 Crescent Island 是容量型"活体验证" |
| **Groq** | LPU 推理芯片；与 NVIDIA 非排他授权合作 | NVIDIA 财报提及 | 超低延迟推理 | 单点、生态封闭 | 🟡 高端低延迟细分，不与容量型直接竞争 |
| **SambaNova** | 与 Intel/Foxconn 合作机架级推理 | Intel Q2 财报 highlight | 大容量推理专精 | 生态小 | 🟢 容量型路线早期同行者 |

### 3.2 竞争定位矩阵

```text
                    Technical depth (memory capacity per GPU)
                              ^
        [Intel Crescent 160GB] |  [NVIDIA HBM 288GB Rubin]
        (niche leader)         |  (dominant, training+inference)
        -----------------------+----------------------
        [CPU inference Xeon]   |  [B300 PCIe/GB300]
        (low-cost entry)       |  (high-volume mainstream)
                              +---------------------->
                              Market breadth
```

**容量型 SKU 的定位**：左上象限（高容量 × 窄场景）——与 Intel Crescent Island 同象限，差异化在于**系统级能力**（整机+散热+软件集成）而非芯片级。

### 3.3 波特五力

| 力量 | 强度 | 分析 |
|:-----|:----:|:-----|
| 现有竞争者 | 高 | NVIDIA 垄断高端；AMD/Intel 争第二；Dell/SMCI 同质化 |
| 新进入者 | 中 | 芯片门槛高，但系统集成门槛低（大量 ODM 涌入） |
| 替代品 | 中 | CPU 推理（Xeon AMX/EPYC）、CXL 内存池、Groq LPU |
| 供应商议价力 | 高 | HBM 垄断（三星/海力士/美光）；LPDDR5X 相对充裕 |
| 客户议价力 | 高 | 推理云/主权 AI 是大客户，比价能力极强 |

---

## 四、看自身

> 以服务器厂商（ODM/OEM 能力者）视角评估。评分 1-5。

| 维度 | 评估 | 依据 |
|:-----|:----:|:-----|
| 整机集成能力 | ⭐⭐⭐⭐⭐ | 风冷/液冷机架、供电、结构设计成熟 |
| 供应链整合 | ⭐⭐⭐⭐ | 内存/CPU/GPU 多源采购经验；LPDDR5X 模组供应链可快速建立 |
| 软件适配 | ⭐⭐⭐ | vLLM/SGLang 集成有基础，但深度调优需投入 |
| 客户渠道 | ⭐⭐⭐ | 企业/云客户有积累；推理云/主权 AI 需新建 |
| 认证能力 | ⭐⭐⭐⭐ | OCP/CE/FCC/安全认证流程成熟 |
| 价格竞争力 | ⭐⭐⭐⭐ | ODM 成本结构优于品牌 OEM |

**自身定位判断**：服务器厂商的差异化不在芯片（没有自研），而在**系统级成本工程 + 软件集成深度 + 交付速度**——容量型 SKU 恰好放大了这三个优势（风冷系统比液冷简单、非 NVIDIA 芯片需要更强的系统集成能力）。

---

## 五、看机会

### 5.1 SWOT

```text
       Strengths                     Weaknesses
   S1 System-level cost eng.   W1 No in-house silicon
   S2 Air/Liquid cooling       W2 Shallow non-CUDA SW stack
   S3 ODM scale & speed        W3 Weak inference-cloud relations
   S4 Multi-vendor platform    W4 Weaker brand than Dell/SMCI

       Opportunities                 Threats
   O1 HBM crisis raises cost   T1 NVIDIA B300 PCIe down-market
   O2 tokens-as-a-service boom T2 Intel NEX direct sales
   O3 Sovereign AI non-NVDA    T3 Inference clouds self-build
   O4 Air-cooled deployment    T4 DRAM price erodes cost edge
```

### 5.2 机会优先级矩阵

| 机会 | 市场潜力 | 技术可行 | 竞争强度 | 自身匹配 | 优先级 |
|:-----|:--------:|:--------:|:--------:|:--------:|:------:|
| 容量型推理 SKU（B300 PCIe/MI350P 基座） | ★★★ | ★★★ | ★★ | ★★★ | **P0** |
| CXL 内存池扩展（容量型 + CXL 混合） | ★★★ | ★★ | ★★ | ★★★ | **P1** |
| 主权 AI 项目（供应安全叙事） | ★★★ | ★★★ | ★★ | ★★ | **P1** |
| tokens-as-a-service 生态合作（与推理云联合开发） | ★★ | ★★★ | ★★★ | ★★ | **P1** |
| Groq/SambaNova 等替代芯片合作 | ★★ | ★★ | ★★ | ★★ | P2 |

---

## 六、定战略

**一句话战略定位**：

> **我们为推理云与主权 AI 客户提供「TCO/token ≤ HBM 机型 1/2 的容量型推理服务器」——用大内存（128-160GB 级）+ 风冷 + 开放芯片（Intel/AMD/替代）避开 NVIDIA 高端垄断与 HBM 危机，以系统级成本工程与交付速度取胜。**

**战略三支柱**：
1. **容量优先**：128GB+ 大内存 + CXL 扩展，锚定长上下文/大批量推理（场景 A）
2. **成本武器**：非 HBM 内存路线 + 风冷系统 → TCO/token 减半
3. **开放生态**：vLLM/SGLang 优先适配，芯片中立（Intel/AMD/替代灵活切换）

**战略边界（不做）**：
- ❌ 不做训练级 SKU（NVIDIA/AMD 已垄断，无差异化空间）
- ❌ 不做自研芯片（资本与技术门槛过高）
- ❌ 不追求与 NVIDIA 在高端推理正面竞争（Rubin 生态不可撼动）

---

## 七、定目标

| 目标类别 | 指标 | 2026（当前） | 2027 | 2028 | 数据来源 |
|:---------|:-----|:----------:|:----:|:----:|:---------|
| **收入** | 容量型 SKU 年营收 | $0（未立项） | $50-100M | $200-300M | 内部财务 |
| **市场** | 非 NVIDIA 推理市场占比 | <2% | 3-5% | 5-8% | IDC/Omdia |
| **客户** | 推理云+主权 AI 客户数 | 0 | 5-10 | 15-25 | CRM |
| **产品** | 容量型 SKU 型号数 | 0 | 2-3 | 4-6 | 产品路线图 |
| **效率** | TCO/token vs HBM 机型 | — | ≤ 1/2 | ≤ 1/3 | 实测基准 |
| **生态** | vLLM/SGLang 支持矩阵覆盖 | — | 主要模型 80% | 95%+ | GitHub/官方 |

**里程碑（Gates）**：
- **G1**（2026Q4）：C2 供应协议 + C3 软件 POC 通过 → 立项正式启动
- **G2**（2027Q2）：首批 50 台试点客户验收，TCO 数据达标 → P1 转 P2
- **G3**（2027Q4）：年化出货 ≥ 1,000 台、2+ 标杆客户 → 稳态经营

---

## 八、定策略（P0/P1/P2 执行）

### 8.1 P0 验证期（0-6 月，2026Q3-2027Q1）

| 任务 | 具体动作 | 产出 | 负责人 | 验证标准 |
|:-----|:---------|:-----|:-------|:---------|
| 负载画像 | 与 3 家推理云客户联合实测 KV 容量分布（128K/1M 上下文占比） | KV 容量画像报告 | 架构师 | ≥30% 负载 KV > 80GB |
| 内存供应 | LPDDR5X 模组 2 家+ 报价与产能确认；CXL 3.2 方案评估 | 供应可行性报告 | 供应链 | 成本 ≤ HBM 1/3 |
| 软件验证 | B300 PCIe / MI350P 上 vLLM/SGLang 跑 128K 长上下文 POC | POC 报告 | 软件工程师 | 吞吐达标、无崩溃 |
| 芯片选型 | Intel Crescent Island（2026H2 送样）跟踪；MI350P vs B300 PCIe 对比 | 选型建议书 | 产品经理 | 决策矩阵完成 |

### 8.2 P1 试点期（6-12 月，2027Q1-Q3）

| 任务 | 具体动作 | 产出 | 验证标准 |
|:-----|:---------|:-----|:---------|
| 参考设计 | 容量型 SKU 参考设计（2U/4U 风冷、128-160GB×N、CXL 扩展槽） | 冻结规格书 | 散热仿真通过 |
| 联合调优 | 与芯片厂商（Intel/AMD）+ 推理云客户三方联合调优 | 调优报告 | 性能提升 ≥20% |
| 试点部署 | 首批 10-50 台，2-3 个客户 | 验收报告 | TCO/token ≤ HBM 1/2 |
| 生态认证 | vLLM/SGLang 官方支持推动、OCP 认证 | 认证证书 | 官方支持列表收录 |

### 8.3 P2 放量期（12-24 月，2027Q4-2028Q4）

| 任务 | 具体动作 | 产出 | 验证标准 |
|:-----|:---------|:-----|:---------|
| 产品发布 | 容量型 SKU 正式发布（价格策略：对标 HBM 机型 1/2-1/3） | 上市 | 季度订单达标 |
| 供应链锁定 | 内存第二源协议、CXL 部件量产协议 | 合同 | 双源 ≥30% 产能 |
| 主权 AI 拓展 | 欧洲/中东/东南亚主权项目投标（供应安全叙事） | 项目中标 | ≥2 项目 |
| 规模优化 | 生产降本（BOM -15%/年）、软件栈产品化 | 成本报告 | 毛利率达标 |

### 8.4 关键风险预控

| 风险 | 触发信号 | 预案 |
|:-----|:---------|:-----|
| NVIDIA B300 PCIe 下探容量型 | B300 PCIe 出货放量+降价 | 转向 CXL 混合方案差异化 |
| Intel Crescent Island 跳票/失败 | 2027H1 未上市 | 以 MI350P 为主力平台 |
| DRAM 涨价侵蚀成本优势 | LPDDR5X 价格环比 +20% | 锁长协、CXL 内存池替代 |
| 推理云自研 | 客户开始自建芯片 | 绑定 2-3 家"长期合作型"客户 |

---

## 九、风险与应对

| 风险类别 | 风险 | 概率 | 影响 | 应对 |
|:---------|:-----|:----:|:----:|:-----|
| 竞争 | NVIDIA 生态碾压 | 高 | 高 | 差异化定位（成本+风冷+服务），不打正面战 |
| 技术 | LPDDR5X 带宽不足导致场景 B 失败 | 中 | 高 | 严格按场景 A（容量驱动）选型，不做带宽敏感负载 |
| 供应链 | 内存超级周期持续 | 高 | 中 | 长协锁价 + CXL 池化 + 国产备选 |
| 市场 | 推理云客户自研/转向 NVIDIA | 中 | 中 | 深度绑定 2-3 家 + 开放芯片中立 |
| 组织 | 软件适配资源不足 | 中 | 中 | P0 阶段即组建专职软件团队 |

---

## 十、监控与迭代

- **月度**：容量型 SKU 北极星健康度（总纲 §5.1）+ 竞争情报看板刷新（§5.3 国际版）
- **季度**：五看更新（市场数据刷新：IDC/Omdia/TrendForce）；战略对齐审计（目的→目标→方案→监控连贯性）
- **半年**：S 曲线定位复审（容量型是否被 NVIDIA 吸收/被 CXL 替代）；五条件判定重评

**退出/调整信号**：
- 容量型 SKU 连续 2 季度毛利率 < 产品线均值 −10ppts → 收缩为利基定制
- NVIDIA 推出同等容量+成本产品 → 战略转 CXL 池化差异化
- 推理负载向带宽驱动转移（场景 A→B）→ 产品线重心回 HBM

---

## 参考文件

### 外部（一手，已实测）

[1] [NVIDIA Q4 & FY2026 Financial Results](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026)（2026-02-25）
[2] [Intel Reports Q2 2026 Financial Results](https://www.intc.com/news-events/press-releases/detail/1776/intel-reports-second-quarter-2026-financial-results)（2026-07-23）
[3] [Intel $15B Common Stock Offering](https://www.intc.com/news-events/press-releases/detail/1778/intel-announces-proposed-15-billion-common-stock-offering)（2026-08-10）
[4] [Intel Newsroom: Crescent Island](https://newsroom.intel.com/artificial-intelligence/intel-to-expand-ai-accelerator-portfolio-with-new-gpu)（2025-10-14）
[5] [AMD Advancing AI 2026 前瞻](https://www.amd.com/zh-cn/solutions/data-center/insights/what-to-expect-at-amd-advancing-ai-2026.html)（2026-07-15）
[6] [Tom's Hardware: Crescent Island](https://www.tomshardware.com/pc-components/gpus/intel-unveils-crescent-island-an-inference-only-gpu-with-xe3p-architecture-and-160gb-of-memory)（2025-10-14）
[7] [斯坦福 AI 指数 2026（腾讯转述）](https://news.qq.com/rain/a/20260427A06E5Y00)（2026-04-27）

### 内部知识库

[8] [总纲框架：容量型 SKU 五看三定](2026-08-11-inference-gpu-capacity-sku-strategy-framework.md)
[9] [Intel Crescent Island 深度分析](2026-08-11-intel-crescent-island-inference-gpu-competitive-analysis.md)
[10] [三类 KV Cache 推理场景](../../03_AI/llm-techniques-principles/2026-08-11-kv-cache-three-scenarios-workload-driven-machine-design.md)
[11] [CSP CapEx 与 AI 服务器出货](../03_server/04_industry/2026-08-07-csp-capex-90pct-ai-server-shipments-deep-analysis.md)
[12] [供应链约束改写规格](../03_server/04_industry/2026-08-10-supply-constraint-rewrites-spec-deep-analysis.md)
[13] [AMD CPU 路线图](../03_server/04_industry/2026-08-05-amd-cpu-roadmap-deep-analysis.md)

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-11 | v1.0 | 首次创建：国际版五看三定（PESTEL+产业链 → TAM-SAM-SOM+客户画像 → NVIDIA/AMD/Intel/Groq 竞争格局 → 自身评估 → SWOT+机会优先级 → 三定），数据底座为一手财报（NVIDIA $215.9B/Intel DCAI $6.3B）+ 机构预测 |
