# 🔬 专题 1：GPU 与 AI 芯片竞争格局

> **等级**: ⭐⭐⭐ | **更新频率**: 每周 | **创建**: 2026-05-28
> **核心问题**: 谁在 AI 芯片赛道上领先？供应、性能、生态如何变化？

---

## 📋 跟踪框架

### 需要持续回答的问题

| 问题 | 当前答案（2026-05） | 待验证 / 搜索指令 |
|:-----|:-------------------|:------------------|
| **NVIDIA 下一代是什么？Timeline？** | B200/GB200 当前，Rubin NVL576 规划 | 搜索：`NVIDIA Rubin Blackwell B300 B500 2026 site:nvidia.com OR site:anandtech.com` |
| **昇腾 910C/950PR 量产节奏？** | 910B 主力，950PR 2026Q1 发布 | 搜索：`昇腾 910C 950PR 量产 2026 site:huawei.com OR 华为` |
| **AMD MI350X/MI400 进展？** | UALink 联盟 100+成员 | 搜索：`AMD Instinct MI350 MI400 2026 site:amd.com` |
| **国产 AI 芯片市占率变化？** | 推理场景国产占比上升 | 搜索：`国产AI芯片 市场份额 2026 推理 训练` |
| **芯片出口管制/禁运动态？** | 持续存在 | 搜索：`BIS 出口管制 AI芯片 2026|美国 对华 芯片 制裁 政策` |
| **GPU 功耗趋势？** | H200=700W → B200=1000W → ? | 搜索：`GPU TDP 功耗 B300 B500 规格 2026` |
| **AI 芯片创新亮点（HBM封装/Die-to-Die 互联）？** | — | 搜索：`NVIDIA Rubin HBM4 封装 NVLink 带宽 2026` |

### 跟踪来源（含 URL）

- [NVIDIA 官方博客](https://developer.nvidia.com/blog/)
- [NVIDIA GTC 会议资料](https://www.nvidia.com/gtc/)
- [华为昇腾官网](https://www.hiascend.com/)
- [AMD Instinct 博客](https://ir.amd.com/news-releases)
- [半导体行业协会 SIA](https://www.semiconductors.org/)
- 券商研报：中信/天风/华泰/申万宏源（东方财富/雪球）

### 搜索关键词集（供定时任务使用）

```
# 每周必搜
"NVIDIA Blackwell B300 量产"
"昇腾 950PR 2026"
"AMD MI350 MI400 最新"
"AI 芯片 出口管制 BIS 制裁"
"GPU 功耗 TDP 2026 趋势"

# 按需轮换
"NVIDIA Rubin architecture"
"国产 AI 芯片 市占率 2026 推理"
"HBM4 封装 GPU 进展"
"华为昇腾 910C 对比 规格"
```

---

## 📝 最新发现

> 此章节由定时任务自动更新。每次搜索后按以下格式追加：

```
### YYYY-MM-DD

**发现概要**：[一句话总结]

**来源**：[标题](URL) （访问日期：YYYY-MM-DD）

**影响评估**：[对整机研发的影响，1-3句话]

---
```

_暂无数据 — 定时任务激活后自动填充_

### 2026-06-02

**来源**: [Taiwan's Industry Titans Turbocharge World's AI Infrastructure Buildout With NVIDIA](https://nvidianews.nvidia.com/news/taiwans-industry-titans-turbocharge-worlds-ai-infrastructure-buildout-with-nvidia) （访问日期：2026-06-02）

**发现**: NVIDIA 在 GTC Taipei 宣布 Vera Rubin 全面量产。台湾超过500家NVIDIA生态合作伙伴，**超过100万MGX机架组件在台湾25个工厂组装生产**，支持Vera Rubin基础设施。NVIDIA AI Cloud 生态全球扩展。

**影响**: Vera Rubin NVL72 量产节奏确认，MGX机架从25个工厂出货意味着供应量级已完全打开。整机研发的参考平台应从 B200/GB200 加速向 Vera Rubin 切换。

---

### 2026-06-02

**来源**: [AMD Instinct MI350 Series GPUs](https://www.amd.com/en/products/accelerators/instinct/mi350.html) （访问日期：2026-06-02）

**发现**: AMD MI350系列全线在售！**MI355X OAM** (288GB HBM3E, 8TB/s, MXFP4 10.1 PFLOPS, 256 CUs) 性能指标全面对标甚至超越 B200。**MI350P PCIe卡**（128 CUs, 144GB HBM3E, 4TB/s）专为企业级简易部署设计。MI350X/MI355X平台支持8 GPU OAM，2.3TB总内存，64TB/s聚合带宽。Dell/HPE/Cisco/Lenovo/Supermicro/Gigabyte等全部OEM齐站台。

**影响**: MI355X FP64性能2.1x B200，MXFP6/MXFP4 10.1 PFLOPS vs B200的9 PFLOPS。AMD在AI加速器硬件指标上首次全面对标NVIDIA。MI350P PCIe卡形态使企业无需改造基础设施即可部署AI加速，对整机设计的PCIe卡方案提供了新选择。

---

### 2026-06-02

**来源**: [AMD Announces Production Ramp of EPYC "Venice" on TSMC 2nm](https://ir.amd.com/news-releases) （访问日期：2026-06-02）

**发现**: AMD EPYC "Venice" 处理器在 **TSMC 2nm 工艺**上量产爬坡。AMD宣布在台湾生态投资超过 **$100亿美元** 加速AI基础设施建设。AMD与Meta战略合作部署 **6GW AMD GPU**。AMD与Nutanix战略合作推进开放可扩展企业AI平台。

**影响**: EPYC Venice 2nm量产标志着x86服务器CPU进入2nm时代。AMD在AI基础设施上投入巨大（$100亿台湾生态投资+Meta 6GW GPUs），将在数据中心AI市场持续形成竞争压力。

---

### 2026-06-02

**来源**: [AMD Announces First Quarter 2026 Financial Results](https://ir.amd.com/news-releases) （访问日期：2026-06-02）

**发现**: AMD Q1 FY2026财报显示数据中心业务增长。AMD宣布"Advancing AI 2026"大会（4月28日）。Maincode $3000万 MC-2 AI工厂采用MI355X GPUs构建（4月16日）。TensorWave AMD GPU云提供2x性能和40-60%成本节省。

**影响**: AMD AI生态系统（TensorWave云、Maincode AI工厂、Sonora大学超算）在加速构建，对NVIDIA形成生态层面的竞争。

---

### 2026-06-02

**来源**: [BIS Export Controls May 2026 - Advanced Computing Items Guidance](https://www.bis.gov/) （访问日期：2026-06-02）

**发现**: BIS 2026年5月发布"Advanced Computing Items"新指南——对Country Group D:5（含中国）和澳门实体的高级计算物品出口限制，**适用于最终母公司也在D:5组的情况**。Authorized IC Designer计划延期至2026年12月31日。Applied Materials因非法出口半导体设备被罚$2.52亿（2月12日）。

**影响**: 出口管制进一步收紧——B300/A完全封锁。Authorized IC Designer延期给国内设计公司缓期但非放松。Applied Materials的巨额罚款表明执法力度在加强。国产AI芯片（昇腾950PR、寒武纪等）的窗口期持续收窄但机会窗口更大。

---

### 2026-06-02

**来源**: [NVIDIA Announces Financial Results for First Quarter Fiscal 2027](https://nvidianews.nvidia.com/news/nvidia-announces-first-quarter-fiscal-2027-financial-results) （访问日期：2026-05-31）

**发现**: NVIDIA Q1 FY2027 营收 $816亿（+85% YoY, +20% QoQ），再创历史纪录。数据中心收入 $752亿（+92% YoY）。**Vera Rubin NVL72 平台正式发布**，Vera CPU 为全球首个专为 Agentic AI 设计的处理器。**NVIDIA Dynamo 1.0 开源**上线，Blackwell 推理性能最高提升 7x。与 Marvell 达成 NVLink Fusion 战略合作，加速 Scale-Up 互联开放化。与 Coherent、Corning、Lumentum 达成先进光学多年代协议。Q2 展望营收 $910亿。

**影响**: Vera Rubin正式进入生产周期，B300生命周期缩短（今年下半年Rubin量产后B300地位将微妙）。Dynamo开源大幅降低推理成本，利好在B300/Rubin平台上做整机推理服务器。NVLink Fusion开放化趋势可能影响Scale-Up互联选型。光学互联协议的签署预示大规模集群光学连接需求加速落地。

---

### 2026-05-31

**来源**: [B300深度解析：它到底比B200强在哪里？](https://www.msn.cn/zh-cn/技术/技术公司/B300深度解析) （访问日期：2026-05-31）

**发现**: NVIDIA B300 (Blackwell Ultra) 于 2026 年 1 月正式出货。配备 288GB HBM3e 高带宽内存，FP4 精度下可提供 14 PFLOPS。B300 服务器在中国大陆成交价飙升至约 700万元人民币/台（约100万美元），较去年底近乎翻倍。**B300/A 已被美国出口管制全面封锁**，导致黄仁勋公开表态"美国应该允许向中国出口"。

**影响**: B300 服务器整机价格暴涨（700万/台），一年期租赁 19万元/月仍需排队，反映 GPU 供需极度紧张。B300被全面封锁后，**中国自研 AI 芯片和国产替代方案需求更加迫切**，昇腾 950PR 推理专用芯片的部署窗口期已至。

---

### 2026-05-31

**来源**: [黄仁勋评价华为"韬定律"（新闻片段）](https://www.nvidia.com) （访问日期：2026-05-31）

**发现**: 黄仁勋 5月29日在台湾 COMPUTEX 期间评价华为 AI 战略："任何小看华为、低估中国制造能力的人都太天真了"。华为公布昇腾 950/960/970 三年路线图，首次公开自研 HBM 内存。DeepSeek V4 运行在昇腾 950PR 上（全球首个顶级大模型完全迁移至国产芯片）。

**影响**: NVIDIA CEO 公开表态正视华为竞争，华为自我研发 HBM 的突破将形成完整国产 AI 芯片堆叠体系。DeepSeek V4 迁移至 950PR 是**国产 AI 芯片生态的里程碑事件**。

---
### 2026-06-03

**来源**: [AMD Instinct MI355X Official Product Page](https://www.amd.com/en/products/accelerators/instinct/mi350/mi355x.html) （访问日期：2026-06-03）

**发现**: AMD MI355X 规格首次曝光细节——TSMC 3nm CDNA4 架构，1850亿晶体管，**288GB HBM3E / 8TB/s带宽 / 10.1 PFLOPS MXFP4**。配置1024个Matrix Cores和256个Compute Units。TBP功耗**1400W**。MI355X在FP64 Matrix方面达78.6 TFLOPS（比B200的37 TFLOPS高**2.1x**）。平台为PCIe 5.0 x16 + 7条Infinity Fabric链接（153 GB/s单向）。支持风冷及密集型DLC。**已于2025年6月发布**，目前为在售状态。

**影响**: MI355X在内存（288GB vs B200 180GB）、FP64（2.1x B200）、FP8 matrix（10.1 vs 4.5 PFLOPS Sparsity）等多项指标超越B200。1400W TDP是整机散热设计的关键参考——超过B200的1000W但低于上一代MI300X（约1600W）。**AMD在硬件规格上已全面对标NVIDIA**，是GPU供应链选型的现实备选。

---

### 2026-06-03

**来源**: [AMD Instinct MI350P PCIe Card Official Page](https://www.amd.com/en/products/accelerators/instinct/mi350/mi350p.html) （访问日期：2026-06-03）

**发现**: AMD MI350P PCIe卡**已在官网正式上架**，TBP功耗可配置：**450W（默认）至600W（最大）**。规格为144GB HBM3E / 4TB/s带宽 / 4.6 PFLOPS MXFP4。512个Matrix Cores / 128 CUs。TSMC 3nm CDNA4，73亿晶体管。PCIe 5.0 x16双槽卡，被动散热。Red Hat、Broadcom(VMware)、Akamai、Nutanix、Uniphore、Kamiwaza、Seekr等7家生态合作伙伴站台。

**影响**: **450W可配置的PCIe卡形态是重大差异化设计**——可在标准PCIe 5.0服务器中部署，无需改造基础设施。4.6 PFLOPS MXFP4约等于H200/B200的40-50%性能，但功耗仅450-600W。对整机研发意味着：多卡PCIe推理服务器有了AMD选项，20卡=92 PFLOPS AI推理性能，适合企业级推理部署场景。

---

### 2026-06-03

**来源**: [AMD Announces Production Ramp of EPYC Venice on TSMC 2nm](https://ir.amd.com/news-releases) （访问日期：2026-06-03）

**发现**: AMD于5月21日宣布**EPYC Venice处理器在TSMC 2nm工艺上量产爬坡**。同时宣布**超过$100亿台湾生态系统投资**加速AI基础设施。与Meta达成扩展战略合作部署**6GW AMD GPU**。Advancing AI 2026大会（6月）即将举行。

**影响**: **EPYC Venice在TSMC 2nm量产**是CPUServer的重大事件——预计带来30%+能效提升，为GPU host CPU提供更优选择。与Meta 6GW GPU合作是AMD在超大规模云市场的重要突破。$100亿台湾投资强化AMD在台湾的制造与设计生态。

---

### 2026-06-03

**来源**: [NVIDIA AI Cloud Ecosystem Expands Worldwide](https://nvidianews.nvidia.com/news/nvidia-ai-cloud-ecosystem-expands-worldwide-2026) （访问日期：2026-06-03）

**发现**: NVIDIA AI Cloud生态系统全球扩展。合作伙伴增加产能以应对企业、初创公司、各国、AI实验室的需求。Agentic AI应用的增长驱动AI工厂基础设施加速建设。**CSP 2026年资本支出上调至$8,300亿(+79% YoY)**。

**影响**: 全球AI基础设施投资仍在加速，$8,300亿CSP CapEx意味着GPU需求在2026-2027年不会降温。整机研发面临持续的产品迭代压力和供应不确定性。

---

⚠️ **重要发现**: AMD MI355X在硬件指标上（288GB/8TB/s/10.1 PFLOPS/FP64 2.1x B200）首次全面对标NVIDIA；MI350P PCIe卡450W可配置功耗是企业部署的游戏改变者。EPYC Venice在TSMC 2nm量产。B300市场供需极度紧张（700万/台），出口管制持续收紧。

---

## 🔗 关联知识

- 技术综合报告 — GPU与算力演进
- [NVIDIA GB200 NVL72](../../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-07-29-nvidia-gb200-nvl72.md)
- [华为 Atlas 900 / 昇腾超节点](../../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-07-29-huawei-atlas900.md)
- [Cerebras CS-3 (WSE-3)](../../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-07-29-cerebras-cs3.md)
- [AMD Instinct MI300X 平台](../../../02_rd/01_product/00_hardware/01_hw-core/aiserver/2026-07-29-amd-mi300x-platform.md)
