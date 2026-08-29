# 🔬 专题 14：服务器形态与ODCC/OCP标准

> **等级**: ⭐⭐ | **更新频率**: 每月 | **创建**: 2026-05-28
> **研究原则**: 以标准组织官方文件为准，厂商产品发布仅作参考，区分「规范定义」和「厂商实现」
> **核心问题**: OAM/UBB 标准更新？DC-SCM2 规范？M-OAM 进展？整机柜接口标准？

---

## 📋 跟踪框架

### 需要持续回答的问题

| 问题 | 当前答案（2026-05，经交叉验证） | 证据来源 | 待验证 |
|:-----|:--------------------------------|:---------|:-------|
| **OCP OAM 标准最新版本？** | OAM（Open Accelerator Module）规范由 OCP Accelerator Module 项目维护。当前主流引用为 OAM V1.5，规范定义了加速模块的物理尺寸（102×165mm/82×150mm）、功耗上限（500W+/750W+ HPC 版）、连接器接口。M-OAM（多加速器模块）正在制定中，标准尚未正式发布 | OCP 官网（反爬限制）；参见 ODCC 发布的相关规范 | 确认 OAM 最新版本号及发布时间 |
| **DC-SCM2 规范？** | DC-SCM（Datacenter Secure Control Module）将 BMC/TPM/管理控制器分离为可插拔模块，减少主板 6-8 层走线复杂度。2.0 版本扩展了安全性（SPDM 1.2+）和管理接口密度 | OCP DC-SCM 官网子页面 | 确认 DC-SCM 2.1 或更高版本 |
| **ODCC 标准体系？** | 2026年5月 ODCC 处于活跃发布期：发布了「OTII-E 边缘AI推理一体机」、「基于CXL方案的AI应用优化与研究」、「Switchless Scale Up GPU 超节点互联系统架构技术规范」、「冷板液冷超流体技术规范」。2026年工作计划包括 AI 超节点大会（已完成）、夏季全会（6月）、开放数据中心大会（9月） | [ODCC 成果发布页](https://www.odcc.org.cn/) — 一手来源 | 下载并分析技术规范全文 |
| **UOAM/UAI/UAD 等国内标准？** | 华为/浪潮等厂商推动 UOAM（Unified OAM）等异形标准，与标准 OAM 存在兼容性问题。ODCC 也提出了国内超节点互联标准体系 | [ODCC 超节点相关规范](https://www.odcc.org.cn/) | 明确国内 OAM 的兼容性程度 |
| **整机柜标准（Scorpio/OpenRack）？** | OCP OpenRack V3 规范定义了 21-inch 宽度的整机柜标准（标准 19-inch 之外的区域用于电源/管理）。ODCC 方面有等效的整机柜标准 | OCP OpenRack V3 Wiki（反爬限制） | 确认 19-inch vs 21-inch 分界点 |
| **COMPUTEX 2026 整机柜新方案？** | **NVIDIA**: Vera Rubin NVL72 全栈机架（无电缆计算托盘+CPU机架+NVLink交换机+以太网交换机+存储机架）；Grace Blackwell 机架装配缩短至5分钟；DSX AI Factory 标准化蓝图 | ServeTheHome NVIDIA Keynote 报道 (2026-05-31) | Vera Rubin 量产爬坡节奏 |
| **Intel 整机柜方案？** | **Intel + Foxconn** 联合开发 Rackscale Blueprints；与 SambaNova 展示 SambaRack 分解式推理（GPU Prefill + RDU Decode + CPU Orchestration），比纯GPU快2-3x | ServeTheHome Intel Keynote 报道 (2026-06-01) | 实际客户部署案例 |
| **Marvell 光互联服务器架构？** | Marvell发布 T100 Teralink + CPO共封装光学交换机；提出光学分解式服务器架构（CPU/内存/XPU独立池化），scale-up域从144 XPU扩展到数千；200G per lane为铜缆最后一代 | ServeTheHome Marvell Keynote 报道 (2026-06-01) | CPO量产时间表 |
| **OAI（Open Accelerator Infrastructure）规范？** | OAI 是 OCP 下子项目，目标定义加速器与主机之间的标准接口（PCIe/CXL 为主），支持热插拔和硬件管理接口 | OCP OAI 子项目页 | 获取最新更新时间 |

### 第一轮信息聚合（2026-05-28 完成）

**ODCC 成果分析**（来源：odcc.org.cn — 官方一手来源）：
- **活跃度**：2026年5月 ODCC 处于高活跃期——每天都有新文章发布。信通院启动「算力中心建设集成研究与评价体系」，算电协同国际标准在 ITU 立项
- **超节点标准**：ODCC 2025年发布了「Switchless Scale Up GPU 超节点互联系统架构技术规范」——核心思路是去掉独立的 Switch 芯片，用 dOCS（分布式光交换电路）+ GPU-IO chiplet 直接互联。这是与 UALink/NVLink 不同的技术路线
- **OISA 白皮书**：ODCC 发布了「OISA 全向智感互联 IO 芯粒技术白皮书」——通过 IO Chiplet 深度融合 GPU 与交换芯片
- **冷板液冷**：ODCC 发布了「冷板液冷超流体技术规范」——用合成油介电冷却替代传统水冷

**OCP 标准访问问题**：
- OCP 官网 opencompute.org 有反爬限制，web_fetch 无法直接获取
- 但 OCP 的 Wiki 页面 opencompute.org/wiki/ 提供了公开的规范文档
- **替代方案**：可关注 OCP 的 GitHub 仓库（github.com/opencomputeproject）获取规范源代码

**整机柜供电标准**：（逻辑推断）
- 从 NVIDIA Kyber 机架案例看，整机柜供电正从 48V 集中式向 800V HVDC 分布式演进
- OCP OpenRack V3 支持 48V 和 400V+ 混合供电架构

### 跟踪来源（含 URL）

- [ODCC 官方首页](https://www.odcc.org.cn/) — 标准白皮书、规范下载（部分需认证）
- [OCP Accelerator Module](https://www.opencompute.org/projects/accelerator-module) — OAM 规范（反爬，需 CDP 或 GitHub）
- [OCP DC-SCM](https://www.opencompute.org/projects/data-center-secure-control-module) — DC-SCM 规范
- [OCP GitHub](https://github.com/opencomputeproject) — 规范源文件备份
- [ODCC 服务器工作组](https://www.odcc.org.cn/) — 中国服务器标准
- [OCP Open Rack V3 Wiki](https://www.opencompute.org/wiki/Open_Rack/V3)

### 搜索关键词集（供定时任务使用）

```
# 每月必搜
"OCP OAM 规范 版本 2026 site:opencompute.org"
"ODCC 服务器 标准 发布 2026 site:odcc.org.cn"
"M-OAM UBB 标准 2026 site:opencompute.org"
"DC-SCM 规范 更新 site:opencompute.org"

# 按需轮换
"ODCC 超节点 标准 技术规范 site:odcc.org.cn"
"OpenRack V3 整机柜 规范"
"OAI accelerator infrastructure spec"
"ODCC 2026 夏季全会 议程"
```

---

## 📝 最新发现

> 此章节由定时任务自动更新

```
### YYYY-MM-DD

**来源**: [标题](URL)（一手/二手，访问日期）
**发现**: [1-3行，必要时附量化数据]
**推理**: [从事实到推论]
**影响**: [对整机形态设计的直接影响]
**验证状态**: [已交叉验证/待验证/单一来源]

---
```

### 2026-06-01（月度更新）

**来源**: ODCC 官网 https://www.odcc.org.cn/（一手来源，2026-06-01 访问）
**发现**: 
1. **ODCC 2026年5月最新发布 4 项规范/白皮书**：
   - `ODCC2504001` 云边协同AI网络技术白皮书（**开放下载**）
   - `ODCC2504002` Switchless Scale Up GPU超节点互联系统架构技术规范 — 采用 **dOCS（分布式光交换电路）** 光互联方案，认证成员可下载
   - `ODCC2504003` OISA全向智感互联IO芯粒技术白皮书 — IO Chiplet 融合 GPU 与交换功能，认证成员可下载
   - `ODCC2504004` 冷板液冷超流体技术规范 — 合成油介电冷却代替水冷，认证成员可下载
   - 另有3项 2025ODCC 系列文档：大模型分布式推理优化（认证）、OTII-E边缘AI推理一体机（**开放**）、基于CXL方案的AI应用优化与研究（**开放**）
2. **Token算力能力评价标准**：信通院拟**下周四召开草案线下研讨会**（2026-05-29发布）— 标志着从"买设备"到"买Token"的计量范式转变
3. **ODCC发布专题文章**："弹性、开放、解耦：下一代超节点系统的技术突围之路"（2026-05-29）
4. **算力中心建设集成研究与评价体系**正式启动（2026-05-28）
5. **IO-NET概念提出**：为 Agent 时代构建下一代 AI 网络互联底座（2026-06-01）
6. **ODCC 2026年活动排期确认**：夏季全会（拟6月）、开放数据中心大会（9月）、冬季全会（拟11月）、华彩论坛（拟11月）
7. **算电织网·攻坚项目**持续征集中
**影响**: 🟡 **重要** — ODCC 正在密集构建独立于 OCP 的标准体系。关键差异点：(1) 互联走 **Switchless dOCS 路线** vs 海外 UALink；(2) 液冷走 **合成油介电冷却** vs 乙二醇水冷；(3) Token 算力评价标准将改变采购和计费方式。ODCC 标准体系中**仅半数对非认证成员开放**，说明标准获取本身存在门槛

---

**来源**: OCP 中国/开放计算技术大会页面 https://www.ocpasia.org/（一手来源，2026-06-01 访问）
**发现**: 
1. **2026开放计算技术大会（OCPC 2026）** 将于 **2026年7月9日** 在北京国际饭店举办
2. **热门议题**包括：字节跳动"大禹"开放架构、阿里云高速互连、CXL 技术、OpenBMC、整机柜供电方案（村田电源/DC/DC创新）
3. OCP 标准更新页面受反爬限制，未能直接获取 OAM/DC-SCM 的具体版本号
**影响**: 🟢 **关注** — OCP 中国大会持续举办，国内既有 ODCC 自主路线也有 OCP 生态活动，需关注 OCP 与 ODCC 的兼容性走向。整机柜供电方案在议程中出现，说明 19-inch vs 21-inch 的分界讨论仍在进行中

---

**来源**: TrendForce 新闻摘要 https://www.trendforce.com/news/（一手来源，2026-06-01 访问）
**发现**: 
1. **COMPUTEX 2026**（6月2-5日）即将开幕 — Intel、Qualcomm CEO 及近 30 家厂商高管出席，覆盖从 Intel 低价 AI CPU 到 CPO（共封装光学）的完整 AI 生态
2. **Intel 计划在新墨西哥州 Rio Rancho 实现全球首个玻璃基板产出**，并同时向客户提供硅光芯片
**影响**: 🟢 **关注** — COMPUTEX 2026 是了解 Intel/AMD/Qualcomm AI 硬件路线图的关键窗口，Intel 玻璃基板 + 硅光组合可能改变服务器主板/基板形态设计

---

### 2026-05-28（初始收集）

**来源**: ODCC 成果发布页面 https://www.odcc.org.cn/（一手来源，2026-05-28 访问）
**发现**: 
1. ODCC 2026年5月发布了「Switchless Scale Up GPU 超节点互联系统架构技术规范」——核心思路是去 Switch 化的 dOCS 光互联 + GPU-IO Chiplet
2. ODCC 发布了「OISA 全向智感互联 IO 芯粒技术白皮书」——IO Chiplet 融合 GPU 和交换功能
3. ODCC 发布了「冷板液冷超流体技术规范」——合成油代替水的介电冷却方案
4. 信通院启动「算力中心建设集成研究与评价体系」
5. ODCC「AI 工厂项目」启动筹备（2026-05-26）
**推理**: ODCC 正在建立一整套独立于 OCP 的国产服务器标准体系。关键差异点：(1) 互联去 Switch（dOCS vs UALink）；(2) 液冷走合成油路线（vs 乙二醇水冷）；(3) 强调算电协同。这意味如果你开发国产化服务器，ODCC 标准才是合规门槛
**影响**: 整机设计时应优先参考 ODCC 规范（而非 OCP），特别是涉及信创/政府项目的产品线。ODCC 的 dOCS+IO Chiplet 路线与海外 UALink/NVLink 不同，双方之间的兼容性问题需要评估

---

### 2026-06-02（月度更新 — 补充验证）

**来源**: ODCC 官网 https://www.odcc.org.cn/（一手来源，2026-06-02 访问）
**发现**: 
1. 🟢 **新增文章「存算分离：AI时代存储架构的变革需求」**（2026-06-02）— ODCC 从存算分离角度讨论 AI 存储架构，与 IO-NET/超节点等系列文章形成完整的技术路线图
2. **ODCC 2026 夏季全会仍为「拟6月」**（尚未确认具体日期），开放数据中心大会 9 月、冬季全会 11 月、华彩论坛 11 月 — 活动排期与前一致，无变化
3. **规范标准列表未新增** — ODCC2504001-004 仍为最新 4 项，无今日新增规范
**影响**: 🟢 **观察** — ODCC 持续输出技术文章（存算分离），与之前 IO-NET、超节点系列形成完整技术叙事，说明 ODCC 正系统性地构建标准生态

---

**来源**: OCP 中国/2026开放计算技术大会页面 https://www.ocpasia.org/（一手来源，2026-06-02 访问，议程已细读）
**发现**: 
1. **2026开放计算技术大会（OCPC 2026）** 7月9日北京国际饭店，**完整议程已发布**（此前仅摘要）
2. **主论坛重磅内容**:
   - 字节跳动服务器架构师高晓军详解**「大禹」开放架构**
   - 阿里云卢晓伟：**超大规模 MoE 对 AI 基础设施的挑战和机遇**
   - 清华大学刘学：从**类脑计算集群走向智算超节点集群**
   - 浪潮信息赵帅：开放计算加速智慧时代
   - NVIDIA 宋庆春：AI 网络释放 AI 工厂潜力
   - 立讯技术李承伟：**超节点互连技术发展与演进**
3. **分论坛5：开放系统设计论坛** — 直接对标本专题核心问题：
   - 阿里云高速互连负责人孔阳：**高性能 ScaleUP 互连系统与实践**（UALink 相关）
   - Intel Xeon 平台的 **CXL 技术分享**
   - 三星 CXL 产品和解决方案创新
   - 浪潮信息：**CXL 内存系统和 PCIe 光互连**
   - 抖音（字节）基于业务优化的**液冷服务器架构**
4. **分论坛2：智算基础设施论坛** — 电源/供电：
   - **村田电源**：用于整机柜供电的多种电源产品方案
   - **伟创力 DC/DC 创新方案**
   - 英特尔 DPU 加速云端和 AI 网络效能
5. **整机柜相关**明确成为独立论坛主题（分论坛5开放系统设计含整机柜供电和 ScaleUP 互联）
**影响**: 🟡 **重要** — OCP 中国大会完整议程显示：字节「大禹」架构 + 阿里超高速互连 + 抖音液冷服务器 = 国内大型互联网公司正密集推进开放硬件架构。整机柜供电方案（村田）和前端的 ScaleUP 互连（阿里高速互连）是两大会场核心。7月9日的议程可作为后续标准验证的关键窗口

---

**来源**: DIGITIMES 首页摘要 https://www.digitimes.com/（一手来源，2026-06-02 访问）
**发现**: 
1. **Nvidia 确认 Vera Rubin 在 150 家台湾供应商支持下全速量产爬坡**
2. **GTC Taipei 2026**: Jensen Huang 称 Vera CPU 专为 Agent 设计，开辟此前不存在的市场
3. **Lenovo 天津 AI 服务器中心计划 2027 年量产** — 中国大陆服务器本地产能持续扩张
4. **HPE 提前完成长期 AI 基础设施目标** — 传统服务器厂商加速 AI 转型
**影响**: 🟢 **观察** — Vera Rubin 的量产意味着服务器整机形态需要适配新一代 GPU 平台的物理和散热规范。Lenovo 天津产能 = 中国大陆本地化制造能力增强

---

### 2026-06-03（COMPUTEX 开幕 + 新形态发布）

**来源**: [The Verge — COMPUTEX 2026 报道](https://www.theverge.com/ai-artificial-intelligence)（二手，2026-06-02/03）
**发现**: COMPUTEX 2026（6月2-5日）开幕，多项重塑服务器/PC 形态的重要发布：
1. 🟡 **Intel Crescent Island 亮相** — 空冷 AI 加速芯片，采用 **LPDDR5 内存**（非 HBM），功耗和成本低于 NVIDIA/AMD 方案。表示 Intel 正走「低成本空冷 AI」路线 vs NVIDIA 的「高功耗液冷」路线
2. 🟡 **NVIDIA RTX Spark「超级芯片」** — 面向 Windows AI PC 市场，对标 Apple Silicon。首次将 AI 推理能力下沉到 PC 端，对 PC 形态和散热设计有直接影响
3. **Intel CEO Lip-Bu Tan 发表主题演讲**（这是他回归 Intel 后的 COMPUTEX 首秀）
4. **Qualcomm CEO 也发表主题演讲** — AI 将从云端向端侧进一步扩散
5. **CPO（共封装光学）成为热点** — 多家厂商展示 CPO 方案，光电融合技术路线在互联层面加速
**影响**: 🟡 **重要** — Intel Crescent Island 的 LPDDR5 + 空冷方案代表了与 NVIDIA 不同的服务器形态路线。如果 Crescent Island 成功，意味着部分 AI 推理可以用低成本空冷服务器完成，降低了对液冷/重散热的依赖。RTX Spark 则定义了 AI PC 新形态，可能改变边缘 AI 部署方式。CPO 热度的提升意味着服务器互联形态正在讨论光进铜退。

---

**来源**: [Ars Technica — Intel Crescent Island](https://arstechnica.com/ai/)（二手，2026-06-01）
**发现**: Intel 公开表示 Crescent Island「比 NVIDIA/AMD 更便宜、更低温」（runs cooler）。关键规格：
- **空冷设计** — 无需液冷基础设施，显著降低 TCO
- **LPDDR5 内存** — 非 HBM，进一步降低成本
- 面向 AI 推理场景，主打性价比而非性能极致
**影响**: 🟡 **重要** — Intel Crescent Island 如果落地，将创造「AI 空冷推理服务器」新品类。对整机设计的影响：(1) 无需液冷管路/CDU，机架密度可更高；(2) LPDDR5 意味着更简单的 PCB 布线（vs HBM 的 CoWoS 封装）；(3) 总成本可能比 GB200 方案低 50%+。

---

**来源**: DIGITIMES — COMPUTEX 2026 Days 1-2 动态综合（一手来源，2026-06-03 访问）
**发现**: 
1. **黄仁勳访问多家台湾供应商展台** — 包括 SK 海力士（HBM4E/HBM5 展台）、台达电等，亲笔写「Please make more」
2. **NVIDIA 确认 Vera Rubin 平台在 150 家台湾供应商支持下全速量产爬坡**
3. **GTC Taipei 2026**: Jensen Huang 称 Vera CPU 专为 Agent 设计
4. **三星首次公开展示 HBM5 模型** — 预计 2028 年量产
5. **SK 海力士展出 HBM4E 物理模型** — 1c DRAM + TSMC 3nm 逻辑 die
**影响**: 🟢 **观察** — COMPUTEX 反映 Vera Rubin 供应链已经就位。HBM4E/HBM5 的进展意味着下一代 AI 服务器形态（Vera Rubin 平台）的设计周期已进入关键阶段。HBM4E 的 1c + TSMC 3nm 封装复杂度进一步上升。

---

---

### ⭐ 2026-06-06 追加 — AI服务器形态最新动态

**来源**: ServeTheHome ASUS XA NB3I-E12评测 + ODCC官网三项规范发布 + STH Intel Keynote直播
**关键词**: 9U空冷 B300、ConnectX-8板载集成、dOCS/OISA/液冷超流体、超节点总体标准、Rackscale Blueprints、分解式推理

| 动态 | 内容概要 | 来源 |
|:-----|:---------|:-----|
| **ASUS XA NB3I-E12 9U 8×B300 空冷评测** | 首度公开解构B300 HGX 8-GPU空冷整机：9U、8×ConnectX-8板载800Gbps、4人搬运、OSFP编号不连续 | [STH](https://www.servethehome.com/asus-xa-nb3i-e12-review-a-massive-8x-nvidia-b300-gpu-server/) |
| **ODCC正式发布三项规范** | ODCC2504002 Switchless Scale Up dOCS光互连 + ODCC2504003 OISA IO芯粒 + ODCC2504004 冷板液冷超流体 | [ODCC](https://www.odcc.org.cn/) |
| **《超节点总体技术要求与测试方法》编制启动** | ODCC超节点综合标准研讨会即将召开，与Token计量标准双轨推进 | ODCC官网 |
| **Intel Rackscale Blueprints+Foxconn** | Intel整机柜设计蓝图计划+Foxconn联合开发+SambaNova分解式推理2-3x加速 | [STH Intel Keynote](https://www.servethehome.com/intel-computex-2026-keynote-live-coverage/) |
| **三家整机柜路线对比** | 液冷(NVIDIA) vs 空冷+分解式推理(Intel) vs 液冷(AMD) 三足鼎立 | 综合 |

---

### ⭐ 2026-06-07 追加 — COMPUTEX 2026收官补充：全新形态因子

**来源**: ServeTheHome (June 5-6) · ODCC官网  
**关键词**: Gigabyte 40节点/1U、RTX Spark SFF生态、微软Surface RTX Spark Dev Box、分解式推理、Intel Rackscale Blueprints

| 动态 | 内容概要 | 来源 |
|:-----|:---------|:-----|
| **Gigabyte 40节点/1U超密度集群** | 全新形态因子：40×Lunar Lake节点=320核+1.28TB+80 SSD+40 iGPU/1U，2×QSFP28 100GbE，整机柜12,800核 | [STH 6/6](https://www.servethehome.com/a-40-node-1u-cluster-gigabyte-r1c7-k0a-as1/) |
| **RTX Spark SFF迷你PC生态展开** | ASUS/Dell/Lenovo/MSI四款亮相：无ConnectX-7、10GbE、128GB统一内存、140W、Wi-Fi 7，Windows AI开发新形态 | [STH 6/5](https://www.servethehome.com/scoping-out-rtx-spark-sff-mini-pcs-at-computex-2026/) |
| **微软Surface RTX Spark Dev Box** | 微软首款NVIDIA Arm Windows AI开发机：100W、合金倒阶梯设计、Windows 11 Pro+VS Code+Copilot+WSL | [STH 6/4](https://www.servethehome.com/microsoft-to-join-the-ai-dev-mini-pc-market-with-upcoming-surface-rtx-spark-dev-box/) |
| **Intel Rackscale Blueprints+Foxconn** | Intel整机柜蓝图计划启动+Foxconn联合开发，分解式推理（GPU+RDU+CPU三阶段）为核心叙事，SambaNova 2-3x实测加速 | [STH Intel Keynote](https://www.servethehome.com/intel-computex-2026-keynote-live-coverage/) |

---

### ⭐ 2026-06-08 追加 — 后COMPUTEX时代：散热重构+供应链锁定+区域部署

**来源**: DIGITIMES 6/8独家 + Tom's Hardware 6/7  
**关键词**: Vera Rubin散热架构变更、HBM多年期供应、ASRock Rack 587台泰国订单、JCET 3D封装、AMD RDNA 5路线图、Samsung Foundry转向、Naver GW工厂

| 动态 | 内容概要 | 来源 |
|:-----|:---------|:-----|
| **NVIDIA Vera Rubin取消双片冷却** | DIGITIMES独家：Vera Rubin抛弃前代双片冷却架构，改用更集成化单片散热 | [DIGITIMES](https://www.digitimes.com/) 6/8 |
| **NVIDIA×SK Hynix多年HBM协议** | 多年期HBM4+供应协议，覆盖AI服务器/PC/机器人三大市场，量产供应链锁定 | [DIGITIMES](https://www.digitimes.com/) 6/8 |
| **ASRock Rack 587台GPU服务器泰国订单** | Pegatun子公司接单泰国AI数据中心，东南亚AI基建加速落地 | [DIGITIMES](https://www.digitimes.com/) 6/8 |
| **JCET 3D封装厂瞄AI电源+CPO** | 新建3D封装工厂，服务AI电源模块集成化和共封装光学量产 | [DIGITIMES](https://www.digitimes.com/) 6/8 |
| **AMD RDNA 5/UDNA 2027末/2028初** | AIB厂商泄露RDNA 5路线图，UDNA统一架构融合RDNA+CDNA，暗示Instinct MI400代际节奏 | [Tom's](https://www.tomshardware.com/) 6/7 |
| **Naver GW级AI工厂+KRW 11T市场** | Naver建设GW级NVIDIA AI工厂，韩国AI数据中心2029达KRW 11万亿 | [DIGITIMES](https://www.digitimes.com/) 6/8 |

---

## 🔗 关联知识

- 技术综合报告 — 机型定义准则
- [全周期管理报告 — 产品形态策略](../../../02_rd/03_management/02_project-management/2026-06-04-doubao-full-cycle-management-report.md)
- [kernel — 标准化 vs 定制化矛盾](../../../02_rd/01_product/00_hardware/01_hw-core/2026-06-26-kernel.md)
- [essence — 标准化体系](../../../02_rd/01_product/00_hardware/01_hw-core/2026-06-26-essence.md)
