# 🔬 专题 9：光互联（CPO/NPO/OCS）

> **等级**: ⭐⭐ | **更新频率**: 每月 | **创建**: 2026-05-28
> **核心问题**: CPO 商用进展？OCS 大规模集群采用？硅光成熟度？国内光互联产业链？

---

## 📋 跟踪框架

### 需要持续回答的问题

| 问题 | 当前答案（2026-05） | 待验证 / 搜索指令 |
|:-----|:-------------------|:------------------|
| **CPO 商用产品发布？** | ✅ **Ayar Labs × Wiwynn 量产级 CPO 机架参考设计完成**（OFC+Computex 验证，32 tray/racks×16 racks→1,024+ GPU）·**Broadcom Taurus 3nm 400G/lane DSP 已采样**（Late 2026量产）·**EDA 工具链就绪**（Siemens/Keysight/Cadence/Synopsys）·**OIP 2026 开幕**（NVIDIA/MS 双主题演讲→量产倒计时） | 搜索：`Ayar Labs Wiwynn CPO rack production 2026` |
| **CPO 量产拐点？** | **576 GPU = 铜拓扑断裂明确拐点**（Ayar Labs CSO）·铜→光拐点从问号变为时间线之争(2027-2028) | — |
| **OCS（光电路交换）最新案例？** | 谷歌 TPU 集群核心 | 搜索：`OCS 光电路交换 案例 谷歌 2026 集群|optical circuit switch datacenter` |
| **华为灵衢全光互联细节？** | 16.3 PB/s, 零线缆 | 搜索：`灵衢 全光 互联 16.3 PB 产品 上市 2026` |
| **全光大平层架构可行性？** | 终极目标—任意点单跳通信 | 搜索：`全光大平层 架构 研究 进展 2026|optical backplane` |
| **光互联 vs 电互联成本交叉点？** | — | 搜索：`copper vs fiber cost per Gbps 2026 数据中心` |
| **国内光互联产业链成熟度？** | — | 搜索：`国产 硅光 光互联 芯片 2026 供应商` |
| **OFC 2026 光互联关键发布？** | — | 搜索：`OFC 2026 光互联 CPO OCS silicon photonics` |
| **NPO 过渡方案主流供应商？** | — | 搜索：`NPO 近封装光学 产品 2026 供应商 vendor` |

### 跟踪来源（含 URL）

- [OFC 会议论文](https://www.ofcconference.org/)
- [LightCounting 光通信报告](https://www.lightcounting.com/)
- [CPO 联盟](https://www.cpoconsortium.org/)
- [华为光通信官网](https://carrier.huawei.com/)
- [谷歌 Research OCS](https://research.google/)

### 搜索关键词集（供定时任务使用）

```
# 每月必搜
"CPO 商用 量产 2026 site:ieee.org"
"OCS 光电路 交换机 2026 部署"
"硅光 光互联 芯片 2026 进展"
"OFC 2026 CPO NPO OCS 亮点"

# 按需轮换
"全光大平层 光背板 进展"
"光互联 电互联 成本 交叉点"
"国产 硅光 模块 供应商 2026"
"NPO 近封装 商用 产品"
```

---

## 📝 最新发现

> 此章节由定时任务自动更新。格式：

```
### YYYY-MM-DD

**来源**: [标题](URL)
**发现**: [1-2行概要]
**影响**: [对互联方案选型的影响]

---
```

### 2026-06-04 — 光互联/CPO/硅光子最新动态

> 重点来源：LightCounting、Marvell、OpenLight、Gazettabyte、OptiNet China 2026、COMPUTEX 2026

---

#### 一、Marvell：光互联全面出击 — 从102.4T交换机到硅光引擎

**① 业界首款102.4 Tbps AI交换机发布** (2026-06-01)
- **来源**: Marvell 官方新闻稿, COMPUTEX 2026
- **关键信息**: Marvell发布业界首款**102.4 Tbps交换机**，专为AI和云数据中心基础设施打造
- **影响**: 交换机容量的量级跃升，对光模块速率提出更高要求（800G/1.6T光口成为标配）

**② COMPUTEX 2026 主题演讲** (2026-05-26)
- **来源**: Marvell CEO Matt Murphy, COMPUTEX 2026 keynote
- **关键信息**: "The Future of AI Scaling Depends on Connectivity" — AI扩展的未来取决于互联
- **影响**: Marvell将互联定位为AI scaling的核心瓶颈

**③ 收购Polariton — 推进光互联** (2026-04-22)
- **来源**: Marvell 官方新闻
- **关键信息**: Marvell收购Polariton，增强光互联技术能力
- **影响**: 延续此前$3.25B收购Celestial AI（光学I/O）的战略，强化硅光子+光互联全栈布局

**④ NVIDIA $2B投资Marvell — NVLink Fusion生态扩展** (2026-03-31)
- **来源**: NVIDIA & Marvell 联合公告 (多个媒体报道)
- **关键信息**: NVIDIA投资$20亿入股Marvell，Marvell加入NVLink Fusion AI生态
- **影响**: NVIDIA将Marvell的互联方案（包括光互联）纳入NVLink生态体系，光互联在scale-up域的地位获巨头背书

**⑤ 1.6T Silicon Photonics Light Engine** (2026-02-13)
- **来源**: Marvell 媒体报道
- **关键信息**: Marvell发布1.6T硅光子光引擎，面向AI数据中心互联
- **影响**: 硅光子方案向1.6T演进，与CPO路线互补

**⑥ May 2026 博客系列 — 互联技术全景**
- **来源**: Marvell Blog (Open CPX / 224G SerDes / PCIe Switch / Photonic Fabric / Optical Test)
- **关键信息**: 
  - Open CPX: 更灵活、可扩展的互联架构
  - 224G Long-Range SerDes: 面向scale-up和scale-inside互联
  - PCIe-based Switching: AI scale-up网络新方向
  - Photonic Fabric™: 解决AI三大问题（带宽、功耗、延迟）

---

#### 二、OpenLight Photonics：硅光子量产里程碑

**① 业界首个3.2T DR8 Silicon Photonics PIC** (2026-03)
- **来源**: OpenLight 官方新闻 (OFC 2026)
- **关键信息**: OpenLight推出**3.2T DR8硅光子PIC**（业界首个），已向多家光模块厂商送样；同时推出**1.6T DR8 LRO/LPO变体**，已收到首批订单
- **影响**: 硅光子PIC首次达到3.2T速率，LRO（线性接收光）和LPO（线性可插拔光）双路线并行

**② 首批量产订单 — Tower Semi InP-on-Silicon平台** (2026-03)
- **来源**: OpenLight 官方新闻 (OFC 2026)
- **关键信息**: OpenLight收到NewPhotonics® 800G和1.6T激光集成PIC的**首批量产订单**，基于Tower Semiconductor PH18DA InP-on-Silicon平台
- **影响**: 异构集成（InP-on-Si）硅光子进入量产阶段，验证了III-V材料与硅光集成的商业可行性

**③ 与TFC合作推进后端集成** (2026-03)
- **来源**: OpenLight 官方新闻
- **关键信息**: OpenLight与TFC合作，在TGV（玻璃通孔）基板上实现400G数据速率的硅光子后端集成
- **影响**: TGV基板方案为CPO封装提供了新的集成路径

**④ Gazettabyte报道** (2026-05-19)
- **来源**: Gazettabyte "OpenLight: funding, customers and the shift to production"
- **关键信息**: OpenLight获得融资、新客户，正从研发转向规模化生产
- **影响**: 独立硅光子公司进入量产爬坡阶段

---

#### 三、LightCounting关键报告/洞察

| 报告/笔记 | 日期 | 核心信息 |
|:----------|:-----|:---------|
| Advances in PIC Packaging | June 2026 | PIC封装进展 |
| 2026 Is the Year of Silicon Photonics and InP | May 2026 | **2026是硅光子和InP之年** |
| NPO pursues optimal balance (FREE) | May 2026 | NPO在模块化和集成间寻求最优平衡 |
| CPO Waiting for Green Light from Customers | Jan 2026 | CPO仍在等待客户「绿灯」 |
| 2026 - The year of Silicon Photonics (FREE) | Nov 2025 | 预言2026是硅光子之年 |
| Marvell enters the CPO race | Dec 2025 | Marvell加入CPO竞赛 |
| AI creates new wave for optics, accelerates CPO | Jan 2026 | AI推动光收发器新需求，加速CPO采用 |
| $100B Market for AI Cluster Optics by 2030 | Mar 2026 | 预测AI集群光学市场2030年达$1000亿 |
| Sales of optical transceivers reached $23.8B in 2025 | Mar 2026 | 光收发器2025年销售$238亿 |
| OFC 2026: Bringing Order to AI's Scaling Challenges | Mar 2026 | OFC 2026为AI扩展挑战建立秩序 |

---

#### 四、OptiNet China 2026（北京，6月3-4日）

- **来源**: OptiNet China 2026 官方网站
- **主题**: "光助智算，网赋新能：共筑AI时代全光底座"
- **关键议程**:
  - 1.6T–3.2T光模块路线图、CPO/NPO/LPO技术产业化演进
  - 硅光子 vs. 薄膜铌酸锂技术辩论
  - 空芯光纤（HCF，降低时延30%以上）vs. 多芯光纤
  - 全光交换（OCS）重构智算中心拓扑
  - 「东数西算」战略下的光网络设计
- **出席方**: 中国电信韦乐平（主席）、LightCounting创始人Vladimir Kozlov（数据中心光互联论坛主席）
- **影响**: 中国光网络产业界正在积极讨论CPO/硅光的产业化时间表

---

#### 五、Intel：EMIB封装 + Ethernet控制器的光互联支撑

- **来源**: Intel Newsroom, 2026-05-28至2026-06-02
- **关键信息**:
  - **EMIB封装技术**（嵌入式多芯片互连桥接）创始人Ravi Mahajan受访，EMIB正成为AI时代基础封装技术，为异质芯片集成（包括光子芯片）提供高密度互联
  - **Ethernet E835控制器**（2026-06-02）面向数据中心/边缘/AI应用
- **影响**: Intel通过EMIB间接支撑光互联（电+光芯片的异构集成），Ethernet控制器为光模块提供电层接口

---

#### 六、Lightmatter + NVLink Fusion：硅光互联生态突破

- **来源**: DIGITIMES 7天新闻 (2026-06-04, 已在同文件GPU章节§五记录)
- **关键信息**: Lightmatter（硅光互联公司）加入NVIDIA NVLink Fusion生态
- **影响**: 硅光技术在AI scale-up域的应用获得NVIDIA官方生态认证，Mark了光互联从scale-out走向scale-up的关键转折

---

#### 七、基于arXiv的硅光/CPO技术突破

| 论文 | 时间 | 核心突破 |
|:-----|:-----|:---------|
| C2PO: 400Gb/s Coherent CPO (arXiv:2506.12160) | 2025-06 | 基于微环调制器的相干CPO发射机，400Gb/s @ 9.65dBm，面积比MZI方案小10-100x |
| 0.78 pJ/bit硅光发射机 (arXiv:2506.04820) | 2025-06 | 硅慢光调制器+开集电流模式驱动器，总位能0.78 pJ/bit，功耗50mW，面积0.66mm² |
| DSP-free CPR for CPO (arXiv:2505.18534) | 2025-05 | 针对CPO应用的DSP-free载波相位恢复方案，支持400Gb/s+的偏移QAM |
| 聚合物波导+硅光CPO集成 (arXiv:2503.02712) | 2025-03 | 高密度聚合物波导与硅光子集成，chip-to-chip耦合损耗<2dB |
| GRIN耦合器用于CPO (arXiv:2503.00121) | 2025-03 | 梯度折射率耦合器，chip-to-chip损耗<0.27dB，1-dB对准容差±2.24μm |

---

## 🔗 关联知识

- [AI 互联与算力网络架构](../../../02_rd/01_product/00_hardware/04_si-signal/2026-07-29-optical-interconnects.md)
- 微信超节点文章 — 光进铜退趋势
