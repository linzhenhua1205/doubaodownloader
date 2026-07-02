# 🔗 互联与光通信技术动态跟踪 — 2026-06-25

> **搜索范围**: arXiv(cs.NI, cs.AR) + DIGITIMES Asia + 光纤在线(c-fol.net) + LightCounting
> **本期焦点**: **空心光纤(HCF)保护倒换穿透分析 · CSA-UD: 通信语义感知RDMA丢包恢复，尾延迟降低>30% · RDMACell: Token级流微元负载均衡，FCT降低44% · Qualcomm Dragonfly数据中心CPU+Meta协议 · CFCF2026苏州开幕，CPO/硅光工艺深入对比 · LightCounting 6月双研报：AI重塑中国光网络+PIC封装进展**
> **写入时间**: 2026-06-25 09:15

---

## 一、arXiv 论文精选

### ① 混合空芯/单模光纤网络保护倒换：挑战、分析与缓解策略

- **论文**: [arXiv:2606.23554](https://arxiv.org/abs/2606.23554) (cs.NI, physics.optics)
- **机构**: 通讯作者 Zhiping Jiang
- **核心贡献**:

空芯光纤(HCF)已从实验室走向生产部署，云运营商已运营数千公里空芯链路。本文对**混合HCF+SMF网络中的保护倒换**做了全面分析。

**关键量化结论**:
| 指标 | 50% HCF部署(1+1保护) |
|:-----|:-------------------|
| 平均色散步进(CD step) | 4,000 - 22,000 ps/nm |
| GSNR代价 | 1.6 - 3.1 dB |
| 需降级调制格式的节点对 | 38 - 59% |
| 全HCF部署容量保留率 | 85 - 99% |

**不对称性发现** — 两个倒换方向根本不对称:
- **HCF→SMF**: CD步进加倍，GSNR代价约10dB
- **SMF→HCF**: 保护路径质量反而更高（负GSNR代价）

SBPP(共享备份路径保护)比1+1保护的CD步进高7%，稀疏拓扑中降级比例多4个百分点。

**缓解策略**: DSP预加载、频谱预均衡、混合部署优先使用1+1保护而非SBPP。

> **对数据中心网络的意义**: 超节点互联需要大量长距离光纤链路，混合光纤类型部署将成为常态，本文提供了定量工程指南。

---

### ② CSA-UD: 通信语义感知RDMA丢包恢复

- **论文**: [arXiv:2606.20582](https://arxiv.org/abs/2606.20582) (cs.NI)
- **机构**: 清华大学
- **核心贡献**:

万亿参数模型训练依赖RDMA的RC(可靠连接)模型，但每个进程对需要独立QP，RNIC仅缓存数千QP→超限时触发PCIe往返惩罚。

**CSA-UD方案** — 将数据传输与丢包恢复解耦，利用分布式训练的同步语义动态调整丢包检测间隔，加速尾恢复。支持多路径传输和位图引导重组。

**性能结果**: 高网络负载下，99%分位流完成时间(FCT)比现有方案**降低>30%**，且无需无损网络。

> **对AI集群的意义**: 在万卡集群中，QP扩展性已成为RDMA性能瓶颈，CSA-UD通过Unreliable Datagram模式实现了RC级别可靠性+UD级别可扩展性。

---

### ③ RDMACell: Token级流微元RDMA负载均衡

- **论文**: [arXiv:2606.20581](https://arxiv.org/abs/2606.20581) (cs.NI)
- **机构**: 清华大学（同组）
- **核心贡献**:

RDMA默认ECMP负载均衡因哈希碰撞和大象流而性能严重下降。现有flowlet方案缺时间间隙、packet级方案有重排序问题。

**RDMACell方案** — 主机侧流微元(flowcell)级负载均衡：主动将流分割为多个flowcell，通过原子化双WQE实现实时接收端反馈。无需修改NIC固件或交换机硬件。

**性能结果**(fat-tree, all-to-all, 80%负载):
| 对比方案 | 99%分位FCT降低 |
|:---------|:--------------|
| vs ECMP | **44%** |
| vs LetFlow | **42.2%** |
| vs 网内可编程方案 | 可比 |

> **对数据中心网络的意义**: 纯主机侧实现、零硬件修改，是实际可部署的RDMA负载均衡方案，对大规模AI训练的通信效率提升显著。

---

## 二、DIGITIMES 产业动态

### ④ Qualcomm Dragonfly数据中心CPU+Meta协议

- **来源**: [DIGITIMES](https://www.digitimes.com/news/a20260625VL201.html), Jun 25, 2026
- **要点**:

Qualcomm在6月24日投资者日上正式公布**数据中心CPU产品线(Dragonfly)**，并宣布与Meta达成**多代CPU合作协议**——这是继上周Qualcomm宣布收购Modular(对标CUDA)后的又一重大动作。

> 关键背景（来自已有知识库）: Dragonfly C1000 CPU拥有250+核心、PCIe Gen7、HBC内存堆叠架构，Arm服务器收入占比已超45%。此次Meta的深度绑定标志着Qualcomm在数据中心CPU领域的战略级突破。

---

## 三、光纤在线(C-FOL) 和 CFCF2026 动态

### ⑤ 第十一届光连接大会(CFCF2026)在苏州举行

- **来源**: [光纤在线](https://www.c-fol.net/), Jun 23-25, 2026
- **关键动态**:

**CFCF2026**于6月23-25日在苏州举行，1500+企业报名，围绕**AI算力架构与光互联方案**：

1. **中天科技发布17280芯超大芯数高密度光缆** — 刷新行业芯数纪录，为算力网络打造高密传输底座
2. **烽火通信"Fiber for AI"方案** — Fit MPO全光互联，覆盖机内/柜内/柜间/楼间/DC间全场景
3. **硅基光电子CPO元件制造之曝光制程比较研究** — 详细比较CPO工艺中ASIC/GPU与光学元件共封装的光刻制程选择
4. **"互连新技术—OCS测试主题技术研讨会"** — OCS(光电路交换)测试成为CFCF重点议题

### ⑥ LightCounting 6月双研报

- **来源**: [LightCounting Research Notes](https://www.lightcounting.com/research-notes)
- **6月最新报告(付费)**:

| 报告 | 重点 |
|:-----|:-----|
| **June 2026: AI to Reshape Optical Networking in China** | AI正在重塑中国光网络市场，数据中心互联需求驱动高速光模块升级 |
| **June 2026: Advances in PIC Packaging** | 光子集成电路(PIC)封装技术进展，CPO/NPO的量产工艺路线 |

- **免费报告**: "May 2026: NPO is pursuing an optimal balance between modularity and integration"
- **即将举行**: 2026年7月15日，**CPO/NPO Conference** (虚拟会议，免费)

---

## 四、综合洞察

### 三大趋势判断

| 方向 | 关键信号 | 产业影响 |
|:-----|:---------|:---------|
| **空心光纤实用化加速** | 云厂商已运营千公里级HCF链路，保护倒换策略成为工程焦点 | 超节点互联需要混合光纤类型，1+1保护是首选架构 |
| **RDMA可扩展性成为瓶颈** | CSA-UD+ RDMACell两项清华论文同日发布，聚焦QP scalability和负载均衡 | 万卡集群中RDMA协议栈已成为AI训练通信效率的关键制约 |
| **CPO产业链成熟度提升** | CFCF2026聚焦CPO工艺，LightCounting发布PIC封装专报，CPO/NPO研讨会7月举行 | 从"技术探索"全面进入"产业化验证"阶段 |

### 关键数据速查

- 空心光纤HCF→SMF切换GSNR代价 ≈ **10 dB** (需DSP预补偿)
- CSA-UD 99%分位FCT降低 > **30%** (vs RC, 高负载)
- RDMACell 99%分位FCT降低 **44%** (vs ECMP, 80%负载)
- Qualcomm Dragonfly CPU达成Meta多代合作
- 中天科技17280芯光缆 = 行业最高芯数纪录
- LightCounting 7月15日 CPO/NPO Conference (免费注册)

---

*下一期跟踪预计: 2026-06-26*
