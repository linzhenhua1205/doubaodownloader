# 🏷️ 三级 KV Cache 调优深度调研报告（五看三定全链路）

> **专题元信息**
> - 创建日期: 2026-08-25
> - 版本: v1.0
> - 方法: industry-insight（五看三定）+ knowledge-doc-writer（Q6 质量标准）
> - 覆盖范围: 三级 KV Cache（GPU HBM → CPU DRAM → SSD/远端存储）调优的技术原理、演进路径、厂商实现、商业机会与落地路径
> - 分析对象: NVIDIA / 华为 / 新华三（超节点设备）× 阿里 / 字节（互联网）× 无问芯穹 / 硅基流动（算力公司）+ 开源生态（vLLM / SGLang / Mooncake / LMCache）
> - 关联前作: [KV 内存墙前沿四件套（08-13）](../02_rd/02_project/01_superpod/2026-08-13-kv-cache-frontier-oasiskv-kvgov-spectra-cdb-deep-analysis.md) · [KV 保存实践全景（08-24）](../02_rd/02_project/01_superpod/2026-08-24-inference-kvcache-1h-retention-storage-planning-deep-analysis.md) · [KV 报文特征（08-24）](./2026-08-24-kv-cache-message-characteristics-inference-deep-analysis.md) · [LLM 上下文与 KV-Cache 机制（08-18）](../../03_AI/llm-techniques-principles/2026-08-18-llm-context-kvcache-mechanisms-deep-analysis.md) · [单位 Token 成本五看三定（08-13）](./2026-08-13-unit-token-cost-five-looks-three-decisions-deep-analysis.md)

---

## 目录

1. [专题概览](#1-专题概览)
2. [技术深潜：三级 KV Cache 原理 × 演进 × 成熟度](#2-技术深潜三级-kv-cache-原理--演进--成熟度)
   - 2.1 第一性原理：为什么需要三级
   - 2.2 三级架构定义与分层机制
   - 2.3 演进路径（Gen0→Gen3）
   - 2.4 技术成熟度评估
3. [厂商方案深度对比](#3-厂商方案深度对比)
   - 3.1 NVIDIA（超节点设备）
   - 3.2 华为昇腾（超节点设备）
   - 3.3 新华三（超节点设备）
   - 3.4 阿里（互联网/云）
   - 3.5 字节（互联网）
   - 3.6 月之暗面 Mooncake（开源标杆）
   - 3.7 无问芯穹（算力公司）
   - 3.8 硅基流动（算力公司）
   - 3.9 全量对比矩阵与架构哲学
4. [五看分析](#4-五看分析)
   - 4.1 看宏观（PESTEL + 产业链）
   - 4.2 看市场（TAM-SAM-SOM + 客户画像）
   - 4.3 看竞争（定位矩阵 + 波特五力）
   - 4.4 看自身（超节点项目能力盘点）
   - 4.5 看机会（SWOT + 机会优先级）
5. [三定：定战略 / 定目标 / 定策略](#5-三定定战略--定目标--定策略)
6. [应用场景与落地规范](#6-应用场景与落地规范)
   - 6.1 场景矩阵
   - 6.2 落地路径（L1-L5）
   - 6.3 可监控指标体系
   - 6.4 连贯性设计检查
7. [跟踪计划](#7-跟踪计划)
8. [参考文献与诚实标注](#8-参考文献与诚实标注)

---

## 1. 专题概览

| 维度 | 内容 |
|:-----|:-----|
| **核心主题** | 三级 KV Cache（HBM→DRAM→SSD/远端）的分层放置、调度与调优：如何在超节点/大规模推理集群上把 KV 缓存从"GPU 显存独占"升级为"集群级分层缓存基础设施" |
| **为什么跟踪** | ① KV cache 已取代权重成为长上下文推理的内存主导（32B GQA 每 token 256 KiB，单请求 8.6 GB @32.7K ctx [来源: OasisKV arXiv:2608.08097]）；② Agentic 负载把上下文从 12K 拉到 80K+ tokens，缓存命中率从 1.7% 可提升到 92.2%，吞吐差 3.8 倍 [来源: vLLM×Mooncake 官方博客 2026-05-06]；③ 国产算力（昇腾/摩尔线程等）与开放生态（vLLM/SGLang）正在把"三级 KV 池化"从论文推向生产 |
| **业务价值** | 对超节点项目：KV 池化直接决定推理服务的**吞吐上限、TTFT、缓存命中率、容量利用率**四大 SLA 指标；是"同样算力多卖 3-4 倍"的关键杠杆 |
| **关键判断** | ① 三级 KV Cache 已从研究走向生产，**2025-2026 是拐点年**（SGLang HiCache、vLLM×Mooncake、昇腾 KV 池同年落地）；② 演进方向是**"本地三级 + 集群分布式池"双轴**：本地 HBM→DRAM→SSD 解决容量，分布式池解决跨实例命中；③ 厂商分层清晰：芯片商做底层传输/池化内核，云厂商做缓存服务化，算力公司做成本优化，开源社区是事实标准层；④ 超节点（512 GPU 级）应把"三级 KV 池"作为第一公民设计，而非事后补丁 |

---

## 2. 技术深潜：三级 KV Cache 原理 × 演进 × 成熟度

### 2.1 第一性原理：为什么需要三级

**KV 内存墙的物理来源**：attention 必须重读全量历史，KV cache 与上下文长度线性相关，且**无法像权重一样被请求摊销** [来源: 08-13 四件套文档 §1.1]。

| 量 | 数值 | 条件 | 来源 |
|:--|:--|:--|:--|
| 32B GQA 模型每 token KV 足迹 | 256 KiB（BF16） | Qwen3-8B 级 | OasisKV §2.1 |
| 单请求 KV 需求 | ≈8.6 GB | 32.7K ctx | 计算 |
| 80 GB HBM 全给 KV 的最大 batch | 仅 9 请求 | 32B 模型 | OasisKV §2.1 |
| 100K 上下文 KV 体积 | ≈3.8 GB | Kimi-2.5 FP8 | vLLM×Mooncake 博客 |
| Agentic 平均上下文增长 | 2,242 tokens/轮 | Codex/SWE-bench Pro 610 traces | vLLM×Mooncake 博客 |

**为什么是"三级"而非"两级"**：单靠 GPU HBM（容量小）→ CPU DRAM（容量中）两级，仍受限于**主机内存容量**与**跨实例隔离**：
1. 本地 DRAM 容量有限：100K 上下文即 GB 级，繁忙实例上大量长会话很快塞满并触发淘汰 [来源: vLLM×Mooncake 博客 "Local KV cache offloading ... limited capacity and eviction"]；
2. 跨实例 miss：负载均衡下会话可能被调度到未缓存该前缀的实例，必须重算 [来源: 同上]；
3. SSD/远端提供**容量 + 共享**：本地盘/分布式池把缓存容量从"单机几十 GB"提升到"集群 TB-PB 级"，并天然支持跨实例共享（同前缀被多个实例复用）。

**物理分层依据（容量×带宽×成本三角）**：

| 层级 | 介质 | 典型容量/节点 | 带宽 | 延迟 | 成本/GB |
|:--|:--|:--|:--|:--|:--|
| L1 | GPU HBM | 80-288 GB（H100/GB200） | 3-8 TB/s | ~100 ns 级 | 最高 |
| L2 | CPU DRAM | 0.5-2 TB | 50-100 GB/s（PCIe/C2C） | ~µs 级 | 中 |
| L3 | NVMe SSD / 分布式池 | 1-30 TB+ / 集群级 | 3-14 GB/s（单盘）~190 GB/s（8×400G RDMA） | ms 级 | 低 |

> 数据 [来源: 08-24 KV 报文特征文档 §2；Mooncake README TE 性能]。**第一性结论**：三级调优的本质是**在"命中收益"与"搬运代价"之间做最优决策**——L1 命中收益最高但容量最小，L3 容量最大但搬运代价最高，核心问题转为"预测哪些 KV 会被复用、何时预取/驱逐"。

### 2.2 三级架构定义与分层机制

**业界事实标准定义**（SGLang HiCache，2025-09-10）：HiRadixTree 充当 page table 引用 KV cache，cache controller 自动管理跨层级加载/备份——**GPU 内存池 → CPU 内存池 → 外部层（磁盘/远端内存）** [来源: lmsys.org/blog/2025-09-10-sglang-hicache]。

```
+-------------------------------------------------------------------------+
|  Control plane: cache controller (hit detection / prefetch / writeback) |
|  Data plane: GPU-assist I/O kernels + RDMA + storage backend adapters   |
+-------------------------------------------------------------------------+
|  L1 GPU HBM pool      |  L2 CPU DRAM pool   |  L3 external storage     |
|  layer-first layout   |  page-first layout  |  Mooncake / 3FS / NIXL  |
|  (compute optimized)  |  (IO optimized)     |  / local file           |
+-------------------------------------------------------------------------+
```

**五大分层机制**（MECE 覆盖读写全链路）[来源: SGLang HiCache 博客 + vLLM×Mooncake 博客 + vLLM-Ascend KV 池文档]：

| # | 机制 | 实现 | 量化收益 |
|:-:|:-----|:-----|:---------|
| M1 | **L1↔L2 搬运加速** | GPU-assisted I/O kernels（替代 cudaMemcpyAsync） | CPU-GPU 传输吞吐 **3×** |
| M2 | **L2 布局优化** | page-first 布局（对齐 IO 效率，与 GPU layer-first 解耦）+ 零拷贝 | 典型部署 **2×** 吞吐 |
| M3 | **L2↔L3 预取策略** | 命中检测后 opportunistically 预取；best-effort / timeout / wait_complete 三档可配 | 按策略隐藏存储延迟 |
| M4 | **L1↔L2 加载重叠** | layer-wise overlapping（第 N+1 层加载与第 N 层执行并发） | 隐藏 L2 传输延迟 |
| M5 | **写回策略** | write-through / write-through-selective（热块跟踪）/ write-back | 按带宽预算选型 |

**关键设计洞察**：
1. **布局分离**：GPU 侧保持 layer-first（计算友好），CPU/存储侧用 page-first（IO 友好），是 HiCache 的核心创新 [来源: HiCache 博客]；
2. **RDMA 零拷贝**：vLLM×Mooncake 用 GPUDirect RDMA 直接在 GPU HBM 与远端 DRAM/SSD 之间搬 KV，**不占 SM、无 staging buffer**，且多 RNIC 聚合 + 拓扑感知选路 [来源: vLLM×Mooncake 博客]；
3. **异步化**：所有 RDMA 操作在专用后台 I/O 线程执行，避免阻塞主 CPU 路径（延迟 GPU kernel 启动）[来源: 同上]；
4. **失败回退**：KV 加载失败可配置 `recompute`（回滚到最后一个有效前缀重算）或 `fail`（vLLM 默认）[来源: vLLM-Ascend KV 池文档]。

### 2.3 演进路径（Gen0→Gen3）

| 代际 | 时间 | 标志 | 容量边界 | 驱动因素 |
|:--|:--|:--|:--|:--|
| **Gen0** 单机 HBM | ≤2023 | PagedAttention/vLLM、RadixAttention | ≤80 GB/卡 | 显存管理精细化 |
| **Gen1** CPU offload | 2024 | vLLM KV offload、TensorRT-LLM offload、OasisKV 类预取 | 主机 DRAM 级 | 长上下文需求、显存墙 |
| **Gen2** PD 分离 + 池化 | 2024-2025 | Mooncake（FAST'25）、LMCache、PD disaggregation | 集群 DRAM+SSD | 预填充/解码负载解耦、复用经济性 |
| **Gen3** 三级分层 + 分布式池 | 2025-2026 | SGLang HiCache、vLLM×Mooncake Store、昇腾 KV 池、PegaFlow | 集群级 TB-PB | Agentic 负载（131:1 输入输出比）、跨实例共享 |

**当前 S 曲线位置**：Gen3 早期——三级架构已开源可部署（HiCache/Mooncake Store/vLLM-Ascend），但**分布式磁盘 offload、cache-aware 路由、混合注意力模型（MLA 类）分层策略**仍是活跃研究项 [来源: vLLM×Mooncake 博客 "What's next" 四项]。

**下一代的工程挑战**：
1. **分布式磁盘 offload**：把层级从 CPU DRAM 扩展到 NVMe SSD + 分布式文件系统（vLLM 官方 roadmap）[来源: vLLM×Mooncake 博客]；
2. **Cache-aware 路由**：请求调度与 KV 池协同，把轮次调度到已持有前缀的实例 [来源: 同上]；
3. **MLA/混合注意力适配**：DeepSeek MLA 的 KV 体积下界（每 token 仅 1 个隐向量 + 解耦 RoPE）改变分层策略 [来源: 08-24 KV 保存实践 §6.7]。

### 2.4 技术成熟度评估

| 维度 | 评估 | 依据 |
|:--|:--|:--|
| TRL | 8-9（生产级） | Mooncake 支撑 Kimi 生产（+75% 请求量）；vLLM 官方集成；昇腾生产文档 |
| 生态成熟度 | 成长期 | 后端接口标准初现（get/exist/set 三函数即插即用 [来源: HiCache 博客]）；供应商 8+ 家 |
| 成本下降曲线 | 命中率驱动的非线性收益 | 1.7%→92.2% 命中率 → 3.8× 吞吐 [来源: vLLM×Mooncake] |

---

## 3. 厂商方案深度对比

### 3.1 NVIDIA（超节点设备）

**定位**：软硬全栈 + 开放生态接口，主推"KV 是 ephemeral 数据"的系统哲学。

| 组件 | 三级 KV 相关实现 |
|:--|:--|
| **TensorRT-LLM** | 内置 KV cache 管理（block 级分配、FP8 KV 量化）；已集成 Mooncake Transfer Engine 做 PD 分离 KV 传输（`cache_transmission/mooncake_utils`）[来源: Mooncake README 2025-12-19] |
| **Dynamo / NIXL** | NIXL 支持 Mooncake TE 作 backend plugin [来源: Mooncake README 2025-05-09]；Dynamo 生态与 HiCache NIXL 后端对接 [来源: HiCache 博客] |
| **GB200/GB300 NVLink-C2C** | CPU 内存经 C2C 高速访问（≈1.8 TB/s 级），天然支持"KV 放主机内存、低损耗访问"；vLLM 博客实证 GB200 上 Kimi-2.5 NVFP4 PD 分离 + Mooncake 池 [来源: vLLM×Mooncake 博客] |
| **GPUDirect RDMA** | 零拷贝 SM-free KV 传输的数据平面基础（vLLM×Mooncake 采用）[来源: 同上] |
| **硬件量化** | NVFP4/FP8 KV 把单 token 体积降 4-8 倍，是"容量×带宽"双赢 [来源: 08-24 保存实践 §6.2] |

**架构哲学**：NVIDIA 通过开放 KV connector 接口（vLLM KVConnector、NIXL）把**传输/池化层外包给生态**，自身聚焦计算内核与互联带宽；对 KV 的官方定位是 **ephemeral（临时）数据**——不追求持久化，只追求复用窗口内命中率 [来源: 08-24 保存实践 §6.2 G3.5 层定位]。

### 3.2 华为昇腾（超节点设备）

**定位**：国产生态中**三级 KV 池化落地最完整**的芯片+设备商（vLLM-Ascend + CANN + Atlas 超节点）。

**AscendStoreConnector 三后端** [来源: vLLM-Ascend KV 池文档（一手，v0.23+）]：

| 后端 | 存储介质 | 传输协议 | 特色 |
|:--|:--|:--|:--|
| **Mooncake** | 集群 DRAM + SSD offload（`enable_ssd_offload`） | ascend 协议（NPU） | 多租户配额（tenant quota）、SSD 逐出策略（fifo/lru）、PYTHONHASHSEED 统一哈希 |
| **MemCache**（华为自研，依赖 MemFabric） | 节点 DRAM 池（示例 640 GB/节点）+ SSD 缓存（UBS IO） | device_sdma / device_rdma / device_urma / device_uboe | 独立部署模式（先起 MemCache 再起 vLLM 预留大池）、L2.5 内存缓存、逐层 KV 保存（use_layerwise） |
| **元戎 Yuanrong**（openEuler 系） | 共享内存 + HugeTLB + 可远程 H2D | RPC/ZMQ + 批量化对象缓存 | 每租户 arena、worker 间批量 get、对象缓存线程池 |

**关键调优参数**（生产级证据）：
- SSD offload：`MOONCAKE_OFFLOAD_TOTAL_SIZE_LIMIT_BYTES` 默认 2 TB/rank 需覆盖为实际盘容（16 rank 在 1 TB NVMe 上会虚报 32 TB）[来源: vLLM-Ascend KV 池文档]；
- 租户配额：`tenant_quota_connector_type=file/etcd`，strict multi-tenant 模式拒绝未注册租户 [来源: 同上]；
- 多租户 TTL/驱逐：`default_kv_lease_ttl`、`eviction_high_watermark_ratio`、`eviction_ratio` [来源: 同上]；
- 硬件分级：A2（800I/800T A2）/ A3（HCCS 或 RoCE）/ A5（950PR/950DT，UBOE/UB 协议）——**同一套 KV 池代码跨三代 NPU** [来源: 同上]；
- MLA 模型：PD 分离下 Decode 节点可写回 KV 供 Prefill 复用（`consumer_is_to_put: true` + `prefill_pp_size`）[来源: 同上]；
- 华为另开源 **TransferQueue**（Ascend/TransferQueue）解耦推理-训练-RL 的状态搬运 [来源: Mooncake README]。

**MindIE（昇腾推理引擎）**：与 vLLM-Ascend 互补，提供图模式/动态分块流水线并行/AI QoS 等引擎级优化；KV 侧以"逐层 KV 池"（layerwise）与"分层与稀疏 KV 缓存卸载指南"为特色功能 [来源: vLLM-Ascend 文档功能矩阵]。

### 3.3 新华三（超节点设备）

**定位**：超节点设备商 + 全栈算力平台集成商；**公开的一手 KV cache 技术细节有限**（诚实标注：以下来自公开平台定位与生态推断，非官方 KV 白皮书）。

| 维度 | 情况 |
|:--|:--|
| 产品线 | 傲飞算力平台（AIOS）、UniServer G6/G7 训推一体机、超节点整机柜方案 |
| KV 实现路径 | ① 整机适配开源推理栈（vLLM/SGLang，继承 HiCache/Mooncake 三级能力）；② 国产卡适配（昇腾/沐曦/寒武纪等，继承各生态 KV 池能力）；③ 平台层提供模型服务/缓存策略管理 |
| 差异化 | 设备商优势在**整机工程**（供电/散热/互联拓扑）与**交付集成**，而非 KV 内核算法 |
| 判断 | 新华三的三级 KV 能力 = "开源内核 + 生态适配 + 平台封装"，核心竞争力在超节点整机的 KV 容量/带宽规划（对应本项目 08-20/08-24 的存储容量与带宽复核） |

### 3.4 阿里（互联网/云）

**定位**：KV 缓存"基础设施化"的推动者——LMCache 开源 + TairKVCache 云服务 + vLLM/SGLang 深度共建。

| 资产 | 三级 KV 相关 | 来源 |
|:--|:--|:--|
| **LMCache** | 跨引擎 KV 缓存层（vLLM 插件），支持本地/远端后端；与 Mooncake Store 集成作 remote connector；LMCache-Ascend 部署文档 | LMCache README；Mooncake README 2025-04-22；vLLM-Ascend 文档 |
| **TairKVCache** | 阿里云 Tair KV 缓存服务团队为 SGLang HiCache 提供 **DeepSeek 3FS 后端集成** | HiCache 博客致谢 |
| **阿里云 × vLLM×Mooncake** | 博客致谢含阿里云团队（Teng Ma 等），参与 MultiConnector 验证 | vLLM×Mooncake 博客 |
| **云厂商缓存保留期** | 5min~24h 实证（对齐本项目 1h 保留期口径） | 08-24 保存实践 §6.6 |

**架构哲学**：云厂商把 KV 缓存做成**托管服务**（TairKVCache 类），用户按命中率/容量付费——与"AI 算力按 token 计费"的商业模式对齐 [来源: 08-13 单位 Token 成本文档]。

### 3.5 字节（互联网）

**定位**：训练侧强（MegaScale）、推理侧走 EIC 社区共建，公开 KV cache 细节有限（诚实标注）。

| 资产 | 情况 |
|:--|:--|
| **MegaScale**（SOSP'24） | 万卡训练系统（25k GPU），展示大规模系统调度/容错能力，非 KV 推理方向 |
| **ByteDance EIC**（高效推理社区） | 与 SGLang 生态共建（HiCache 博客致谢 "ByteDance EIC teams"）；在 vLLM/SGLang 的 PD 分离、调度器方向有社区贡献 [来源: HiCache 博客致谢] |
| **豆包/火山引擎** | 大模型推理服务（云侧），KV 优化细节未公开 |
| **判断** | 字节在三级 KV 的公开一手材料薄弱；其价值主要在**大规模系统工程的参照系**（MegaScale 的调度/容错思想可迁移到 KV 池的分布式元数据管理） |

### 3.6 月之暗面 Mooncake（开源标杆）

**定位**：**KVCache-centric 架构的发明者与开源事实标准**（FAST'25 最佳论文）。

| 能力 | 数据 | 来源 |
|:--|:--|:--|
| 生产效果 | Kimi 在 SLO 内多处理 **75% 请求**；池化缓存命中率 **525%** | Mooncake README；08-24 保存实践 §6.4 |
| 传输性能 | 4×200G RoCE **87 GB/s**、8×400G **190 GB/s**（2.4×/4.6× TCP）；40 GB KV（LLaMA3-70B 128K）秒级搬运 | Mooncake README |
| 三级架构 | Mooncake Store **multi-tier cache**（DRAM + SSD/NVMe）；P2P Store（checkpoint-engine） | Mooncake README |
| 生态渗透 | vLLM / SGLang / TensorRT-LLM / vLLM-Ascend / LMDeploy / xLLM / NIXL / LMCache / TorchSpec 全接入 | Mooncake README Updates |
| 硬件覆盖 | NVIDIA / 华为昇腾 / AMD / 寒武纪 / 摩尔线程 / 沐曦 / 海光 / 壁仞 / 阿里云 | Mooncake README Supported Hardware |

**架构哲学**："用存储换计算"（Trading More Storage for Less Computation）——利用 GPU 集群闲置的 CPU/DRAM/SSD 建池，把 prefill 的重复计算变成 KV 缓存命中 [来源: FAST'25 论文]。

### 3.7 无问芯穹（算力公司）

**定位**：异构算力聚合平台（Infini-AI），目标"把大模型算力成本压缩 4 个数量级"（夏立雪）[来源: 微信文章标题级，待验证细节]。

| 信号 | 情况 | 可信度 |
|:--|:--|:--|
| 真武 PPU 卸载 | 微信文章《真武PPU卸载跑通：国产KV池化与超节点放量》（2026-08 前后）标题级信息——国产 KV 池化与超节点放量关联 | ⚠️ 标题级，正文被搜狗验证码拦截，**待一手验证** |
| Infini-AI 平台 | 异构算力调度（多厂商国产卡 + NVIDIA），推理优化以平台化方式提供 | 官网 SPA，细节未取到 |
| 判断 | 无问芯穹的三级 KV 价值在于**异构算力池上的 KV 缓存共享**（多卡种统一 KV 格式与池化），但公开技术细节需持续跟踪补证 |

### 3.8 硅基流动（算力公司）

**定位**：低成本推理算力服务商（DeepSeek 系列主力部署方之一），走开源引擎深度优化路线。

| 信号 | 情况 | 可信度 |
|:--|:--|:--|
| PD 分离异构混部白皮书 | 与摩尔线程联合发布《PD分离异构算力混部技术白皮书》（2026-08）：国产 GPU 2:1 等效对标国际高端 GPU；4 台 MTT S5000 等效顶替 2 台国际高端 GPU——PD 分离下 prefill/decode 分派到异构卡，KV 传输与缓存复用是核心机制 | ✅ 白皮书标题+摘要级（多篇微信报道交叉） |
| DeepSeek 系列部署 | 长期低成本运行 DeepSeek-R1/V3 系列，vLLM/SGLang 深度调优（量化 + PD 分离 + KV 缓存） | ✅ 公开服务事实 |
| 判断 | 硅基流动代表"算力服务商"路线：**用 KV 缓存命中率与 PD 分离提升单卡吞吐**，从而降低每 token 成本；其 ×摩尔线程合作证明国产卡同样吃三级 KV 优化红利 |

### 3.9 全量对比矩阵与架构哲学

| 厂商 | 层级覆盖 | 池化范围 | 传输平面 | 特色机制 | 商业模式 |
|:--|:--|:--|:--|:--|:--|
| NVIDIA | L1-L2（L3 交生态） | 节点内（C2C）+ 生态接口 | GPUDirect RDMA/NVLink | FP8/NVFP4 KV、Dynamo/NIXL 开放 | 芯片+软件栈 |
| 华为 | L1-L3 全栈 | 集群级（三后端） | ascend/MemFabric/URMA | 租户配额、逐层加载、SSD 驱逐策略、TransferQueue | 芯片+整机+平台 |
| 新华三 | L1-L3（生态继承） | 平台封装 | 生态 | 整机工程/交付集成 | 整机+平台 |
| 阿里 | L1-L3 | 云托管池 | RDMA | TairKVCache 服务化、3FS 后端 | 云服务订阅 |
| 字节 | 未公开 | — | — | EIC 社区共建 | 内部+云服务 |
| 月之暗面 | L1-L3 | 集群闲置资源池 | RDMA/多协议 | KV-centric 架构、P2P Store | 开源+自用 |
| 无问芯穹 | 待验证 | 异构池（推断） | 待验证 | 真武 PPU 卸载（待验证） | 算力平台 |
| 硅基流动 | L1-L2（推断 L3） | 节点内 | 生态 | PD 分离异构混部、量化 | 算力服务 |

**架构哲学三派**：
1. **内核派**（NVIDIA/华为）：控制传输与池化内核，硬件带宽即护城河；
2. **服务派**（阿里/云）：把 KV 缓存商品化为托管服务，按命中付费；
3. **效率派**（月之暗面/硅基流动/无问芯穹）：用缓存经济学压每 token 成本，吃尽复用红利。

---

## 4. 五看分析

### 4.1 看宏观（PESTEL + 产业链）

| PESTEL 维度 | 分析 |
|:--|:--|
| **P 政策** | 国产算力政策强推（昇腾/摩尔线程生态加速），三级 KV 池化是国产卡补性能差距的关键软件杠杆 |
| **E 经济** | AI 推理成本结构翻转：KV 主导内存预算 → 缓存命中率直接决定推理毛利（08-13 单位 Token 成本文档）；算力供给过剩期，"提效=省钱"诉求强 |
| **S 社会** | Agentic 应用（Claude Code/OpenClaw）爆发，多轮长上下文成为主流负载形态 |
| **T 技术** | 三级架构 2025-2026 集中落地；MLA/混合注意力改变 KV 体积；GPUDirect RDMA/URMA 成熟 |
| **E 环境** | KV 缓存减少重算 = 直接降低无效算力功耗（训练/推理碳排放） |
| **L 法律** | 多租户 KV 共享引入数据隔离合规要求（KVGov 类时序侧信道治理是安全研究前沿 [来源: 08-13 四件套 §3]） |

**产业链结构**：

```
Upstream: storage media (HBM/NVMe) + interconnect (RDMA/URMA/C2C)
  -> Midstream: accelerator (GPU/NPU) + inference engine (vLLM/SGLang/TRT-LLM)
  -> Downstream: KV pooling layer (Mooncake/LMCache/cloud) + compute platform
  -> End user: model service providers / enterprise Agent apps
```

### 4.2 看市场（TAM-SAM-SOM + 客户画像）

**市场规模估算**（基于推理优化市场，诚实标注为估算口径）：

| 指标 | 2026（估算） | 2029（预测） | CAGR | 依据 |
|:--|:--:|:--:|:--:|:--|
| TAM：全球 LLM 推理市场 | $50-80B | $150-250B | ~45% | 第三方推算（08-13 单位 Token 成本文档引用） |
| SAM：KV 缓存/推理优化软件+服务 | $3-6B | $15-30B | ~70% | KV 占比推理成本 20-40%（长上下文场景） |
| SOM：超节点/私有化 KV 池化 | $0.3-1B | $3-8B | ~100%+ | 国产算力渗透 + 超节点项目放量 |

> ⚠️ 以上为结构估算，非权威市场报告；真实数值需第三方数据交叉验证。

**客户画像与需求**：

| 客户类型 | 核心需求 | 痛点 | 付费意愿 |
|:--|:--|:--|:--|
| 大模型服务商（Kimi/DeepSeek 类） | 高命中率、低 TTFT | 长上下文缓存容量不足、跨实例 miss | 高（直接降成本） |
| 云厂商 | KV 托管服务 | 多租户隔离、配额管理 | 中高（增值服务） |
| 企业/超节点项目（本类） | 容量规划、带宽规划、SLA 达标 | 配额 vs 占用口径、保留期设定 | 中（随整机采购） |
| 算力服务商 | 每 token 成本最低 | 国产卡性能差距 | 高 |

### 4.3 看竞争（定位矩阵 + 波特五力）

```
                    Technical depth (in-house)
                          ^
    Niche leaders              Full-stack leaders
    SiliconFlow (tuning)       Huawei Ascend (full stack)
    Infini-AI (het pooling)    Moonshot (KV-centric)
                          +------------------------------+
    Participants               Integrators
    ByteDance (not public)     Alibaba (cloud managed)
    H3C (ecosystem-based)      NVIDIA (open ecosystem)
                          v
                    Ecosystem breadth
```

| 波特五力 | 强度 | 分析 |
|:--|:--:|:--|
| 现有竞争者 | 高 | 8+ 家厂商，且开源社区（vLLM/SGLang/Mooncake）是最大"竞争者"（免费提供 80% 能力） |
| 新进入者 | 中 | 内核研发门槛高（RDMA/调度/存储），但生态接口（get/exist/set）降低了接入门槛 |
| 替代品 | 中 | 模型架构替代（MLA 减 KV、状态空间模型免 KV）长期存在；量化压缩短期更普适 |
| 供应商议价力 | 中 | 依赖硬件传输能力（RDMA/URMA/C2C），但软件栈可跨硬件 |
| 客户议价力 | 高 | 开源免费方案强约束，商业价值必须体现在"命中率/吞吐增量"上 |

### 4.4 看自身（超节点项目能力盘点）

基于本项目（512 GPU 超节点）已有沉淀：

| 维度 | 现状 | 依据 |
|:--|:--|:--|
| KV 容量规划 | 5T/GPU 配额、1h 保留期（151T 满载需求）；E3.S×3 存储 2160T 余量 14× | 08-24 复核 v2.0 |
| KV 报文建模 | 双峰分布（小报文高频写+大报文低频读）、TP 语义 | 08-24 报文特征 |
| 生命周期分层 | 请求级/会话级/prefix 级/G3.5 四层 | 08-24 多方案设计 |
| 前沿跟踪 | OasisKV/SPECTRA/CDB/KVGov 五维覆盖 | 08-13 四件套 |
| 存储网络 | G4 本地盘 + 4×Gen5（671B FP8 加载 12s） | 08-24 复核 §5 |

**能力缺口**（三级 KV 调优视角）：① 无集群级分布式 KV 池规划（当前是存储级保留，非推理运行时池）；② 未选型 KV 池后端（Mooncake/自研/云托管）；③ 无命中率/TTFT 监控体系设计。

### 4.5 看机会（SWOT + 机会优先级）

| SWOT | 内容 |
|:--|:--|
| **S 优势** | 超节点整机工程能力（供电/散热/互联）；已有 KV 容量/带宽/报文深度建模；紧跟开源生态 |
| **W 劣势** | 无推理引擎内核研发能力；KV 池化依赖生态；多国产卡异构适配复杂 |
| **O 机会** | 国产算力放量（昇腾/摩尔线程）→ 三级 KV 池化成为标配卖点；Agentic 负载爆发；NVIDIA 生态开放接口 |
| **T 威胁** | 开源免费方案压缩商业价值；MLA 类架构降低 KV 调优杠杆；云厂商托管服务分流 |

| 机会 | 市场潜力 | 技术可行 | 竞争强度 | 自身匹配 | 优先级 |
|:--|:--:|:--:|:--:|:--:|:--:|
| 超节点内建三级 KV 池（Mooncake 类） | ★★★ | ★★★ | ★★ | ★★★ | **P0** |
| KV 池后端选型 + 容量/带宽再规划 | ★★★ | ★★★ | ★★ | ★★★ | **P0** |
| 命中率/TTFT 监控体系 | ★★ | ★★★ | ★ | ★★★ | **P1** |
| 多国产卡异构 KV 池适配 | ★★★ | ★★ | ★★★ | ★★ | P1 |
| KV 托管服务化（对外） | ★★★ | ★★ | ★★★ | ★ | P2 |

---

## 5. 三定：定战略 / 定目标 / 定策略

### 定战略（一句话）

> **本超节点为 Agentic 长上下文推理提供"HBM→DRAM→SSD/分布式池"三级 KV 缓存基础设施，通过开源内核（Mooncake/vLLM 生态）封装 + 整机工程优化，实现"同算力 3 倍吞吐、TTFT 一个数量级下降"的服务化能力。**

### 定目标（指标体系，含基线）

| 目标类别 | 指标 | 2026（当前基线） | 2027（目标） | 2028（目标） | 数据来源 |
|:--|:--|:--:|:--:|:--:|:--|
| **性能** | 前缀缓存命中率 | 1.7%（仅 system prompt） | ≥85% | ≥92% | 推理网关埋点 |
| **性能** | P50 TTFT 降低 | 1× | ≥20× | ≥40× | 网关 |
| **性能** | 吞吐提升 | 1× | ≥2.5× | ≥3.5× | 压测 |
| **容量** | KV 池容量 | 0（未建） | ≥64 TB/集群 | ≥256 TB/集群 | 池元数据 |
| **效率** | 有效 KV 复用率 | — | ≥70% | ≥80% | 池统计 |
| **商务** | 每 token 推理成本降幅 | 1× | ≥40% | ≥60% | 成本模型 |

> 基线参照：vLLM×Mooncake 实证 1.7%→92.2% 命中率、3.8× 吞吐、46× TTFT [来源: vLLM×Mooncake 博客]；HiCache 社区实证 40%→80% 命中率、TTFT −56%、吞吐 2×（Novita AI）[来源: HiCache 博客]。

### 定策略（落地路线图）

| 阶段 | 时间 | 关键任务 | 里程碑 | 风险 |
|:--|:--|:--|:--|:--|
| P0 | 0-6 月 | ① KV 池后端选型（Mooncake Store vs vLLM-Ascend 生态 vs 自研轻量）；② 三级容量/带宽再规划（合并 08-20/08-24 口径）；③ 本地 L1-L2 offload 试点 | 单节点 CPU offload + 前缀缓存命中率 ≥50% | 引擎版本兼容 |
| P1 | 6-12 月 | ① 集群分布式 KV 池（RDMA 平面）；② cache-aware 路由联动；③ 命中率/TTFT 监控体系 | 集群池命中率 ≥85%、TTFT −20× | 网络抖动/故障恢复 |
| P2 | 12-24 月 | ① SSD 级分布式 offload（L3 扩展）；② 多租户配额/隔离（对齐昇腾 tenant quota 设计）；③ 多国产卡异构适配 | L3 池化 + 多租户 SLA | 数据合规/侧信道 |

---

## 6. 应用场景与落地规范

### 6.1 场景矩阵

| 场景 | 客户类型 | 描述 | 紧迫度 | 付费成熟度 | 匹配度 | 优先级 |
|:--|:--|:--|:--:|:--:|:--:|:--:|
| Agent 长会话推理 | 模型服务商/企业 | 多轮工具调用，131:1 输入输出比，前缀缓存价值最大 | ★★★ | ★★★ | ★★★ | P0 |
| 代码助手/Coding Agent | 开发者工具 | 25K+ tokens/会话，8 轮+，复用窗口长 | ★★★ | ★★★ | ★★★ | P0 |
| 多租户 SaaS 推理 | 云厂商 | 共享前缀（system prompt）跨租户命中 + 隔离 | ★★★ | ★★★ | ★★ | P1 |
| 大规模 RAG/检索问答 | 企业 | 文档前缀重复命中 | ★★ | ★★★ | ★★★ | P1 |
| 异构国产卡混部 | 算力服务商 | PD 分离分派异构卡（硅基流动×摩尔线程模式） | ★★★ | ★★ | ★★ | P1 |

### 6.2 落地路径（L1-L5 成熟度）

| 级别 | 特征 | 判定标准 |
|:--|:--|:--|
| L1 探索 | 技术验证 | 单节点 CPU offload 跑通，命中率 ≥30% |
| L2 试点 | 单场景落地 | 一个 Agent 场景命中率 ≥70%、TTFT −10× |
| L3 推广 | 多场景复制 | 全场景命中率 ≥85%，池容量 ≥64 TB |
| L4 融合 | 业务深度嵌入 | cache-aware 路由 + 多租户 SLA |
| L5 引领 | 生态/标准 | 后端接口标准化（get/exist/set 生态位） |

### 6.3 可监控指标体系

**北极星指标**：

```
KV Service Value Index (KVI) = 0.5*(hit rate) + 0.3*(TTFT reduction/base) + 0.2*(throughput ratio/base)
```

| 层级 | 指标 | 数据源 | 频率 | 告警阈值 |
|:--|:--|:--|:--|:--|
| L0 北极星 | KVI | 系统计算 | 日 | 降 >10% |
| L1 业务 | 命中率、TTFT P50/P99、吞吐 | 网关 | 分钟 | 命中率 <70% |
| L2 技术 | 池命中/未命中、预取成功率、写回 I/O | 池监控 | 分钟 | 预取命中 <50% |
| L3 资源 | HBM KV 占用、DRAM 池水位、SSD 水位/带宽 | 基础设施 | 秒 | DRAM 水位 >85% |

### 6.4 连贯性设计检查

| 决策节点 | 检查问题 | 通过标准 |
|:--|:--|:--|
| D1 目的→目标 | 命中率/TTFT 目标能否反映"降本提效"目的 | 对应关系清晰 |
| D2 目标→方案 | 三级 KV 池方案能否直接支撑目标 | 因果链可验证（Mooncake 实证 3.8×） |
| D3 方案→指标 | 命中率是否真实反映方案效果 | 无代理偏差（区分池命中 vs 本地命中） |
| D4 指标→监控 | 采集频率 > 故障影响时间 | 分钟级监控覆盖 |
| D5 全链路 | 四者季度对齐审计 | 无偏移 |

---

## 7. 跟踪计划

| 跟踪项 | 频率 | 数据来源 | 下次更新 |
|:--|:--|:--|:--|
| 开源生态（vLLM/SGLang/Mooncake/LMCache） | 双周 | GitHub Releases/官方博客 | 2026-09-08 |
| NVIDIA（Dynamo/NIXL/TensorRT-LLM KV） | 双周 | NVIDIA 官方文档/博客 | 2026-09-08 |
| 华为昇腾（vLLM-Ascend KV 池/MindIE） | 双周 | vLLM-Ascend 文档/华为发布 | 2026-09-08 |
| 新华三/无问芯穹/硅基流动 | 月度 | 官网/微信/白皮书 | 2026-09-25 |
| 前沿论文（OasisKV/SPECTRA 后续） | 月度 | arXiv | 2026-09-25 |
| 市场数据（KV 市场规模） | 季度 | 第三方报告 | 2026-11 |

---

## 8. 参考文献与诚实标注

**一手来源（本次抓取）**：
1. [SGLang HiCache 官方博客](https://lmsys.org/blog/2025-09-10-sglang-hicache/) — 三级 KV 缓存定义、数据/控制平面、三后端（2025-09-10）
2. [vLLM × Mooncake Store 官方博客](https://vllm.ai/blog/2026-05-06-mooncake-store) — 分布式 KV 池、GPUDirect RDMA、3.8×/46×/8.6× 实证（2026-05-06）
3. [Mooncake GitHub README](https://github.com/kvcache-ai/Mooncake) — multi-tier 缓存、传输引擎性能、生态全景（2026-08 版）
4. [LMCache GitHub README](https://github.com/LMCache/LMCache) — 跨引擎 KV 缓存层（2026-08 版）
5. [vLLM-Ascend KV 池文档](https://docs.vllm.ai/projects/ascend/zh-cn/main/user_guide/feature_guide/kv_pool.html) — 昇腾三后端（Mooncake/MemCache/元戎）+ SSD offload + 租户配额（v0.23+）
6. [vLLM 官方博客：vLLM×Novita AI PegaFlow](https://vllm.ai/blog/2026-05-18-pegaflow) — 外部 KV cache 服务（Rust daemon/CUDA IPC/RDMA/SSD）

**知识库既有深度（交叉引用）**：
7. 08-13 KV 内存墙前沿四件套（OasisKV/KVGov/SPECTRA/CDB）— `02_rd/02_project/01_superpod/2026-08-13-kv-cache-frontier-oasiskv-kvgov-spectra-cdb-deep-analysis.md`
8. 08-24 KV 保存实践全景 v2.0（NVIDIA CMX/vLLM LRU/Mooncake 525%/LMCache/MLA）— `02_rd/02_project/01_superpod/2026-08-24-inference-kvcache-1h-retention-storage-planning-deep-analysis.md`
9. 08-24 KV 报文特征 — `04_ai/2026-08-24-kv-cache-message-characteristics-inference-deep-analysis.md`
10. 08-18 LLM 上下文与 KV-Cache 机制 — `03_AI/llm-techniques-principles/2026-08-18-llm-context-kvcache-mechanisms-deep-analysis.md`

**诚实标注（数据缺口）**：
- ⚠️ **新华三**：无公开 KV cache 一手技术文档，方案推断基于平台定位（整机+生态封装），标注为"推断"；
- ⚠️ **字节**：推理侧 KV 优化未公开，仅确认 EIC 社区共建（HiCache 致谢），不作为事实断言；
- ⚠️ **无问芯穹**：真武 PPU 信息为微信文章标题级（正文被搜狗验证码拦截），**待一手验证**；
- ⚠️ **市场规模**：TAM/SAM/SOM 为结构估算，非权威第三方数据；
- ⚠️ **硅基流动**：白皮书数据来自公开报道交叉（多篇微信摘要一致），未取到白皮书原文。

**素材落盘**：`tmp/raw/2026-08-25/github-kvcache-ai-mooncake-README.md`、`tmp/raw/2026-08-25/github-LMCache-LMCache-README.md`

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-25 | v1.0 | 首次创建：五看三定全链路深度调研（技术原理×演进×厂商矩阵×商业分析×落地规范） |
