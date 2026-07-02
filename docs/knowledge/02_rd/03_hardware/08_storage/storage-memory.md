# 🔬 专题 8：存储层级与内存架构

> **等级**: ⭐⭐ | **更新频率**: 每月 | **创建**: 2026-05-28
> **研究原则**: 第一性原理 → 厂商数据为主，arXiv 论文为辅，TrendForce 定价为参考
> **核心问题**: HBM 产能和价格趋势？KV Cache 存储方案？CXL 内存池化落地案例？远端内存（JBOF/SCM）在推理中的角色？

---

## 📋 跟踪框架

### 需要持续回答的问题

| 问题 | 当前答案（2026-06，经过交叉验证） | 证据来源 | 待验证 |
|:-----|:----------------------------------|:---------|:-------|
| **HBM4 量产时间线？** | JEDEC 将 HBM4 微凸点方案推迟混合键合：HBM4 继续使用微凸点，混合键合推迟到 HBM5（SemiEngineering, 2026-01-13）；Synopsys 2026年4月展示首颗 HBM4 IP 测试芯片，在 9.2 Gbps 完成硅验证 | [JEDEC公告 via SemiEngineering](https://semiengineering.com/hbm4-sticks-with-microbumps-postponing-hybrid-bonding/) ; [Synopsys HBM4 验证](https://semiengineering.com/early-hbm4-validation-points-the-way-for-next-generation-ai-and-hpc-systems/) | 三星/SK 量产时间实际落地 |
| **HBM3E 价格趋势？** | HBM 产能紧张延续至 2026H2，主要产能被 NVIDIA/AMD 锁定（TrendForce 持续报道） | [TrendForce 存储价格](https://www.trendforce.com/) | 现货价格波动 |
| **KV Cache 独立存储方案？** | 2026年5月 arXiv 论文集中爆发：KVDrive（多层级 GPU→DRAM→SSD 管理）、ObjectCache（S3 对象存储存 KV Cache）、AlignedServe（CPU 大内存做 KV Cache 调度）——学术方向已明确向 tiered storage 演进。腾讯发布 DDR 内存池方案，在 Scale-Up 网络上向每 GPU 提供 300-600 GB/s TB 级容量 | [KVDrive](https://arxiv.org/abs/2605.18071) ; [ObjectCache](https://arxiv.org/abs/2605.22850) ; [AlignedServe](https://arxiv.org/abs/2605.23389) ; [腾讯 ODCC DDR内存池](https://www.odcc.org.cn/news/p-2046780371761913857.html) | 腾讯原型测试结果 |
| **CXL 内存池化量产案例？** | 阿里 Beluga（SIGMOD'26）——目前唯一披露的 CXL 2.0 生产级案例。新华三发布首个国内商用 CXL 2.0 方案。ODCC 发布「基于 CXL 方案的 AI 应用优化白皮书」 | [Beluga 论文](../../../03_AI/industry-research/alibaba-beluga.md); [ODCC](https://www.odcc.org.cn/) | 更多量产案例 |
| **存算分离架构工程化进展？** | ODCC 发布 ODCC2505006 规范：基于 BlueField-3 DPU + 三星 PM1743 PCIe Gen5 SSD 的 Ceph 存算分离方案。通过重构 CRUSH 规则消除东西向流量，随机读 +176%，随机写 +50%，硬件需求降低 67% | [ODCC 存算分离](https://www.odcc.org.cn/news/p-2061643023256416258.html) | 实际生产部署效果 |
| **GDS（GPU直通存储）标准化进展？** | ODCC AOSA 发布 GPU与存储直通技术研究报告，识别四大挑战（接口规范、评估工具、复杂度、安全），提出标准化路径。中国 GPU 厂商（昇腾/寒武纪/海光）GDS 适配将在该框架下推进 | [ODCC GDS](https://www.odcc.org.cn/news/p-2043876917141856258.html) | 统一接口规范制定 |
| **NVMe SSD 大规模部署可靠性？** | ODCC 发布 NVMe 子系统全息健康评估（NHA），6 维权重（介质 40%/控制器 25%/电容 10%/链路 10%/事件 5%/其他 10%），Log Page E4h 固定地址，支持带内/带外访问。美团+忆联+华为+佰维等联合制定 | [ODCC NHA](https://www.odcc.org.cn/news/p-2049330659312033794.html) | AI 预测模型引入 |
| **DDR 内存池在 GPU 存储体系角色？** | 腾讯在 ODCC 春季全会提出 DDR 内存池是「GPU 存储体系最后一块拼图」：Scale-Up 网络部署，向每 GPU 提供 300-600 GB/s TB 级访存能力。2026 年进入正式研发 | [ODCC 腾讯DDR内存池](https://www.odcc.org.cn/news/p-2046780371761913857.html) | 原型测试与生产验证 |
| **KV Cache 压缩/量化技术前沿？** | 2026年5月 arXiv 出现大量方法：CONF-KV（置信度感知量化 + 混合精度）、TriAxialKV（INT2/INT4 三轴混合精度，面向 Agent 推理）、VeriCache（压缩KV做 draft → 全精度 verify，保证无损）、AMS（区域感知分段裁剪） | [CONF-KV](https://arxiv.org/abs/2605.24786); [TriAxialKV](https://arxiv.org/abs/2605.17170); [VeriCache](https://arxiv.org/abs/2605.17613); [AMS](https://arxiv.org/abs/2605.23200) | 各方法实际工程落地的收敛情况 |
| **远程 KV Cache 传输对推理延迟的影响？** | ObjectCache 在 100Gbps RoCE 下，64K 上下文额外延迟仅 5.6%；CacheTune 3.72-4.86× TTFT 加速（通过异步计算-I/O 重叠）；但 4K 短上下文时 ObjectCache 额外增加 56-75ms | [ObjectCache 量化数据](https://arxiv.org/abs/2605.22850); [CacheTune](https://arxiv.org/abs/2605.24022) | 集群规模下扩展性 |
| **Agent 推理对 KV Cache 的特殊需求？** | TriAxialKV 报告 Agent 工作负载（工具调用/多模态）产生结构化 KV Cache——时间、模态、语义角色三维不均等，需要差异化精度。SiDP 报告 DP 场景下 KV Cache 占用成为最大约束 | [TriAxialKV Agent分析](https://arxiv.org/abs/2605.17170); [SiDP](https://arxiv.org/abs/2605.28095) | 更多场景验证 |

### 第一轮信息聚合（2026-05-28 完成）

**HBM4 现状**（来源：JEDEC/Press/Synopsys 一手资料）：
- HBM4 16-high stack 仍然用微凸点，不加 hybrid bonding → 对 TSV 封装良率和成本更友好
- Synopsys 2026年4月展示首颗 HBM4 IP 测试硅片，9.2 Gbps 眼图干净；IP 架构设计可扩展到更高速率（待 HBM4 DRAM 更成熟后）
- KAIST TERALAB 2025年6月发表 371页 HBM 路线图白皮书

**KV Cache 系统架构趋势**（来源：arXiv 2026年5月论文——一手学术来源）：
- **多层分级**：GPU HBM → DRAM → SSD 的三级 KV Cache 管理架构已成学术共识
- **无损 vs 有损**：VeriCache 首次提出「压缩KV做Draft，全精度Verify」的无损方案（与GPU算力验证类似思路）
- **Agent 特殊需求**：TriAxialKV 指出 Agent 推理中 KV Cache 按三个维度（时间/模态/角色）分布不均，一刀切量化会严重损失质量
- **CXL + 对象存储**：ObjectCache 探索将 KV Cache 放到 S3 对象存储（Ceph/RGW），NVMe over RDMA 优化协议流

**CXL 内存池化**（来源：学术论文 + ODCC 白皮书）：
- 阿里 Beluga 是唯一公开的 CXL 2.0 生级案例
- ODCC 已发布「基于 CXL 方案的 AI 应用优化与研究」白皮书（2025年）
- 厂商级 CXL 3.0 内存池化产品尚未公开看到量产案例

### 跟踪来源（含 URL）

- [JEDEC HBM 标准](https://www.jedec.org/standards-documents/focus/memory)
- [SemiEngineering HBM4 tag](https://semiengineering.com/tag/hbm4/)
- [TrendForce DRAMeXchange](https://www.trendforce.com/)
- [arXiv KV Cache 最新论文](https://arxiv.org/search/?query=KV+cache+LLM+inference&searchtype=all)
- [CXL Consortium](https://www.computeexpresslink.org/)
- [ODCC 存储相关白皮书](https://www.odcc.org.cn/)
- [ODCC AI 存储实验室](https://www.odcc.org.cn/)

### 搜索关键词集（供定时任务使用）

```
# 每月必搜 — 一手来源优先
"HBM4 site:jedec.org OR site:semiengineering.com"
"KV cache storage offload 2026 site:arxiv.org"
"CXL memory pooling production site:computeexpresslink.org"

# 按需轮换
"DRAMeXchange HBM price trend"
"LMCache github release"
"KV cache quantization 2026 site:arxiv.org"
"Samsung HBM4 timeline"
```

---

## 📝 最新发现

> 此章节由定时任务自动更新。格式：来源（URL）→ 发现概要 → 对整机研发的影响

```
### YYYY-MM-DD

**来源**: [标题](URL)（一手/二手，访问日期）
**发现**: [1-3行，含量化数据]
**推理过程**: [事实→推理→结论]
**影响**: [对整机设计中存储架构/内存拓扑的影响]
**验证状态**: [已交叉验证/待验证/单一来源]

---
```

### 2026-05-28（初始收集）

**来源**: [Early HBM4 Validation Points The Way For Next Generation AI And HPC Systems](https://semiengineering.com/early-hbm4-validation-points-the-way-for-next-generation-ai-and-hpc-systems/)（一手，Synopsys 博客转载于 SemiEngineering，2026-04-09）
**发现**: Synopsys 完成首颗 HBM4 IP 测试芯片硅验证，9.2 Gbps 眼图合格；IP 架构可扩展到更高速率（具体数值待 HBM4 成熟后公布）
**推理**: HBM4 生态向前推进，但 JEDEC 决定保留微凸点 → 良率压力降低 → 量产更可控。但要等到三星/SK 实际量产芯片才到整机验证阶段
**影响**: 2027年 HBM4 整机大概率可行，信号完整性设计需留余量到 12+ Gbps

**来源**: [HBM4 Sticks With Microbumps, Postponing Hybrid Bonding](https://semiengineering.com/hbm4-sticks-with-microbumps-postponing-hybrid-bonding/)（一手，JEDEC 决定）
**发现**: JEDEC 确认 HBM4 16-high 仍然用微凸点，混合键合推迟到 HBM5
**推理**: 微凸点方案对 DDR4/5 的控制器兼容性更好，整机设计时可以复用前代 SI 设计经验
**影响**: HBM4 的 SI 设计不会比 HBM3E 有本质性的复杂度跃升，这对整机研发是利好

**来源**: arXiv 2026年5月多篇论文（一手学术来源）
**发现**: KV Cache 存储架构在学术层面达成共识——三级分层（GPU→DRAM→SSD）；同时出现4+种压缩方法（CONF-KV, TriAxialKV, VeriCache, AMS）
**推理**: 不同方法有不同 tradeoff：无损方案（VeriCache）增加验证开销但保证精度，有损方案（CONF-KV）更节省但需场景校验。目前都在论文阶段，尚未看到某方法形成工程垄断
**影响**: 对整机研发而言：KV Cache 对远端存储的需求确定性上升→ PCIe lane 预算中需要为 KV Cache JBOF 预留带宽（类似 Intel G3.5 方案）

### 2026-05-29

**来源**: [JEDEC HBM4 DRAM 标准正式发布 (JEDEC)](https://www.jedec.org/standards-documents/docs/)
**发现**: JEDEC 于 **2026年5月18日** 正式发布 HBM4 DRAM 标准。HBM4 采用 2048-bit 宽接口（从 HBM3 的 1024-bit 翻倍），每通道 64-bit DDR 总线设计。三星提供 >2.8TB/s 带宽/堆叠，美光发布 >11.0 Gbps 速度等级。Synopsys 此前展示的首颗 HBM4 IP 测试硅片在 9.2 Gbps 完成验证。三大厂竞赛加速：三星 HBM4 在 NVIDIA 测试中得分最高（2025年12月报道）；SK 海力士采用台积电代工逻辑芯片。
**影响**: HBM4 标准正式落地，2026H2 将进入量产冲刺。对 AI 服务器整机设计而言，HBM4 的 2.8TB/s 带宽将显著推动下一代 GPU 性能跃升，需要提前规划配套的散热和供电方案。

**来源**: [TrendForce/DRAMeXchange 存储市场报告](https://www.dramexchange.com)
**发现**: HBM 产能紧张格局延续至 2026H2，主要产能被 NVIDIA/AMD 长期锁定。DRAM 现货价格仍处于高位，PC DRAM 连涨四个月。
**影响**: HBM 供应紧张短期无缓解，AI 服务器 BOM 中 HBM 成本占比持续上升，需关注 TrendForce 每月合约价更新。

**来源**: [CXL 内存池化量产方案 — 新华三发布 (H3C)](https://www.h3c.com)
**发现**: 新华三于 2026年4月30日正式发布 **CXL 2.0 内存池化解决方案**，主打打破内存墙和 IO 墙限制，支持动态分配内存。CXL 3.0 正从标准走向实现（4.0 规范已达 128GT/s）。腾讯新闻 2026年5月22日报道 Penguin Solutions 推出 **MemoryAI KV 缓存服务器** 基于 CXL 3.0。但 EET-China 分析指 CXL 仍面临延迟瓶颈（逼近 HBM 难）、软件生态差（250家联盟成员深度适配有限）、商用节奏慢三大死穴。
**影响**: CXL 内存池从概念走向产品落地（新华三/阿里Beluga/Penguin MemoryAI），但大规模部署仍受限于软件生态成熟度。对 AI 服务器整机研发应保持 CXL 接口预留，但短期不可依赖 CXL 解决显存瓶颈。

**来源**: [vLLM 文档 — LMCache 集成 (vllm.com.cn)](https://docs.vllm.com.cn/examples/others/lmcache.html)
**发现**: vLLM v1 文档已正式收录 LMCache 集成示例（2026年4月），支持**解耦预填充 (Disaggregated Prefill)**、CPU 卸载和 KV Cache 共享三大场景。LMCache 作为开源 KV Cache 管理层实现 GPU→DRAM→本地磁盘三级缓存，在长上下文场景下实现 3-10× 性能提升。百度开发者中心 2026年5月1日发布 LMCache 深度实践指南。
**影响**: LMCache 从学术原型进入工程落地阶段，已被 vLLM 和 SGLang 两大主流推理框架支持。这是 KV Cache 层级存储从论文走向生产的关键信号，对推理服务器存储架构设计有直接参考价值。

⚠️ **重要发现**: HBM4 标准落地的同时，CXL 内存池和 KV Cache 存储方案同步推进——2026年5月是存储层级架构的"标准/产品/框架"三重里程碑月。HBM4 标准 + 新华三 CXL 方案 + vLLM LMCache 集成 = 存储层级从理论走向实践的加速拐点。

---

## 🔗 关联知识

- [技术综合报告 — 推理上下文存储架构](../../../03_AI/industry-research/inference-context-memory-storage.md)
- [essence — 存储方案精华](../../../03_AI/notes/essence.md)
- [kernel — 存储层级矛盾](../../../03_AI/notes/kernel.md)
