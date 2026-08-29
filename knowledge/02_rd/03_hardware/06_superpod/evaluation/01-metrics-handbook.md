# 📊 超节点 AI 训练与推理性能指标手册

> **版本**: v1.0 | **创建**: 2026-06-29 | **分类**: 超节点 · 性能评估
>
> **本文定位**: 超节点智算场景下训练/推理任务的性能指标完整手册。涵盖指标定义、测量方法、参考阈值与标准工具链，**不依赖其他文档即可独立使用**。

---

## 📑 目录

- [1. 评估框架总览](#1-评估框架总览)
- [2. 训练任务核心指标群](#2-训练任务核心指标群)
- [3. 存储与 IO 指标群（训练）](#3-存储与-io-指标群训练)
- [4. 推理任务核心指标群](#4-推理任务核心指标群)
  - [4.7 KV Cache 共享存储评估与测试方案](#47-kv-cache-共享存储评估与测试方案)
- [5. 网络维度指标](#5-网络维度指标)
- [6. 系统级综合指标](#6-系统级综合指标)
- [7. 度量方案与工具链](#7-度量方案与工具链)
- [8. 快速诊断：指标交叉关联表](#8-快速诊断指标交叉关联表)

---

## 1. 评估框架总览

### 1.1 三维矩阵

超节点作为百卡/千卡级 GPU 集群，评估必须从 **单卡 → 单节点 → 集群 → 端到端** 四个层次展开，覆盖 **计算 / 存储 / 网络** 三个维度。

| 维度 \ 层次 | **计算（算力）** | **存储（数据）** | **网络（通信）** |
|:-----------|:---------------|:---------------|:---------------|
| **单卡/片** | TFLOPS / HBM 带宽 / 显存容量 | HBM 内部带宽 | PCIe 上行带宽 |
| **节点内** | GPU-GPU 通信效率 / SHARP 卸载 | 本地缓存 Miss 代价 | NVLink / HCCS / UALink 环内带宽 |
| **跨节点** | 扩展效率 / 负载均衡 | 并行文件系统吞吐 | Scale-Out 有效带宽 / 跨节点 AllReduce |
| **端到端** | MFU / Effective MFU / Goodput | Checkpoint 开销 / 数据管道 | 通信-计算重叠效率 |

### 1.2 评估方法论路线

完整的性能评估路径分 5 步：

```
负载模型 → 系统模型 → 帕累托描边 → 校准验证 → 边界地图
```

- **负载模型**：定义需求侧的压力画像——选定模型（GPT/LLaMA/MoE）、并行策略（TP/PP/DP/EP/SP）、batch size、sequence length 等关键变量
- **系统模型**：建立资源与拓扑的数学映射——GPU 算力、网络带宽、存储吞吐的理论极限
- **帕累托描边**：遍历关键变量区间，描出性能边界曲面，找出权衡最优区域
- **校准验证**：用真实 benchmark 数据校准模型预测值，修正偏差
- **边界地图**：产出可操作的设计空间图，指导系统选型与优化方向

### 1.3 训练 vs 推理的差异化关注点

| 维度 | **训练** | **推理** |
|:-----|:---------|:---------|
| **瓶颈类型** | 计算密集型 + 通信密集型 | Prefill 计算密集 / Decode 显存带宽受限 |
| **关键指标** | MFU / 收敛速度 / 吞吐 | TTFT / TPOT / 服务质量 |
| **批处理** | 固定大 batch（吞吐优先） | 动态 batch（延迟 + 吞吐平衡）|
| **并行策略** | TP + PP + DP + EP 混合 | TP + DP（重量级推理引擎）|
| **容错要求** | 故障恢复 / 检查点 | 高可用 / 快速故障切换 |
| **KV Cache** | 不适用 | 核心瓶颈（显存占用 + 读取带宽）|

---

## 2. 训练任务核心指标群

### 2.1 MFU（Model FLOPs Utilization）

**定义**：模型实际产出的计算量占硬件理论峰值的比例。**训练效率的最重要综合指标**。

$$
MFU = \frac{\text{实际产出的 model FLOPs}}{\text{硬件峰值 FLOPS} \times \text{GPU 数量} \times \text{时间}}
$$

#### 测量方案

| 要素 | 方法 | 工具 |
|:-----|:-----|:-----|
| 理论 FLOPs | 根据模型架构计算 per-step FLOPs（Attention + FFN） | `flops-counter` / Megatron Profiler / 自定义公式 |
| 实际产出的 FLOPs | `理论 per-step FLOPs / step_time` | TensorBoard / Nsight Systems |
| 硬件峰值 | GPU 规格参数（BF16/FP8 Tensor Core） | `nvidia-smi` / PyTorch abstract |

#### MFU 公式细化（GPT / LLaMA 类 Dense 模型）

```
per_step_FLOPs = 6 × N_params × seq_len × global_batch_size
                 + 2 × N_layers × seq_len² × d_head × n_heads × global_batch_size
```

- 第一项：Forward + Backward 的矩阵乘 FLOPs
- 第二项：Attention 的 QKV + 注意力得分计算（不计 Flash Attention 近似）

#### FP8 vs BF16 口径

- **BF16 MFU**：用 BF16 Tensor Core 峰值（如 H100 SXM: 989 TFLOPS）计算分母
- **FP8 MFU**：用 FP8 Tensor Core 峰值（如 H100 SXM: 1,979 TFLOPS）计算分母
- 同一模型 BF16 MFU 通常高于 FP8 MFU（FP8 峰值翻倍但利用率更低）
- 建议**同时报告两个口径**，并注明计算方式

#### 参考阈值

| 规模 | 典型 MFU（BF16） | 说明 |
|:-----|:---------------|:-----|
| 单 GPU 微基准 | 75-85% | 仅计算，无通信 |
| 单节点 8 GPU | 55-70% | 节点内通信引入开销 |
| 4 节点 32 GPU | 50-60% | 跨节点 AllReduce |
| 64 节点 512 GPU | 40-55% | 通信 + 负载均衡 |
| 256+ 节点（万卡） | 30-50% | 包含故障 / Checkpoint / 等待 |

### 2.2 HFU（Hardware FLOPS Utilization）

**定义**：硬件实际被利用的计算量占理论峰值的比例。**与 MFU 的差值反映计算-通信重叠效率**。

$$
HFU = \frac{\text{模型理论 FLOPs} + \text{额外开销 FLOPs}}{\text{硬件峰值 FLOPS} \times \text{GPU 数} \times \text{时间}}
$$

**额外开销包括：**
- Activation Recomputation 引入的额外计算
- 通信操作（AllReduce / ReduceScatter / AllGather）中占用 SM 的部分
- 数据预处理 / Tokenization 等

**MFU vs HFU 诊断关系：**

| 状态 | 含义 |
|:-----|:------|
| MFU ≈ HFU | 额外计算开销极小，利用率高 |
| MFU << HFU | 大量计算浪费在重算/通信上，需优化 |
| HFU - MFU > 20% | **计算-通信重叠差**，需要检查通信库设置 |

### 2.3 Step Time 分解

**定义**：一个训练 step 的端到端耗时，拆解为子阶段。

```
StepTime = Forward + Backward + Optimizer + Communications + IOWait + SyncBarrier
```

| 子项 | 含义 | 参考占比 | 瓶颈判定 | 诊断工具 |
|:-----|:-----|:---------|:---------|:---------|
| **Forward** | 前向传播计算 | 30-40% | — | Nsight Compute kernel trace |
| **Backward** | 反向传播计算 | 45-55% | — | Nsight Systems timeline |
| **Optimizer** | 权重更新（SGD/AdamW） | 5-10% | — | PyTorch Profiler hooks |
| **Communications** | NCCL AllReduce/RS/AG | 理想 <15% | 若 >20% 为通信瓶颈 | Nsight Systems + `NCCL_DEBUG=TRACE` |
| **IO Wait** | 数据加载阻塞 | 理想 <5% | >10% 为存储瓶颈 | `perf stat -e block:*` / `iostat -x` |
| **Sync Barrier** | 卡间/节点间等待 | 理想 <3% | >5% 负载不均 | 自定义 CUDA event hook |
| **空闲（Idle）** | GPU 无事可做 | 理想 <5% | — | CUDA runtime API trace |

#### 诊断阈值的工程经验

- **Communications + SyncBarrier > 25%** → 网络为瓶颈，需检查拓扑/通信算法
- **IO Wait > 10%** → 存储系统跟不上计算，需检查数据加载管道
- **SyncBarrier > 5%** → 负载严重不均，需检查并行策略（TP/PP load balance）

#### 测量代码示例（PyTorch）

```python
import torch
import torch.cuda.profiler as profiler

start = torch.cuda.Event(enable_timing=True)
end = torch.cuda.Event(enable_timing=True)

start.record()
loss = model(input)
end.record()
torch.cuda.synchronize()
fwd_time = start.elapsed_time(end)  # ms
```

### 2.4 吞吐指标

| 指标 | 单位 | 公式 | 说明 |
|:-----|:-----|:-----|:------|
| **Tokens/s（per GPU）** | tokens/s/GPU | 总训练 tokens / 总时间 / GPU 数 | 单卡产出率，便于横向对比 |
| **Tokens/s（cluster）** | tokens/s | 总训练 tokens / 总时间 | 集群总产出 |
| **Samples/s** | samples/s | batch_size × GPU_num / step_time | 核心吞吐指标 |
| **TFLOPs/utilized** | TFLOPs/s | model FLOPs / step_time | 直接反映计算产出速率 |
| **Tokens/sec/GB** | tokens/s/GB | 吞吐 / 显存容量 | 显存效率，用于对比异构方案 |

### 2.5 扩展效率（Scaling Efficiency）

**定义**：多 GPU 规模扩展时的吞吐保持率。

$$
SE = \frac{\text{实际吞吐提升倍数}}{\text{理想线性提升倍数}} \times 100\%
$$

**测量方法**：固定 per-GPU batch size（弱扩展）或固定 global batch size（强扩展），递增 GPU 数。

| 扩展倍率 | 典型 SE（强扩展） | 典型 SE（弱扩展） | 主要损耗来源 |
|:---------|:----------------|:----------------|:------------|
| 2×→4× | 95-98% | 97-99% | 通信引入 |
| 8×→64× | 85-92% | 90-95% | AllReduce Ring 带宽衰减 |
| 64×→512× | 70-85% | 80-90% | 全局通信 + 负载不均 |
| 512×→2048× | 55-75% | 65-80% | 通信墙 + 故障损失 |

**关于强扩展与弱扩展**：
- **弱扩展（Weak Scaling）**：GPU 越多 = 总 batch size 越大，SE 保持较好
- **强扩展（Strong Scaling）**：固定总 batch size，GPU 越多 = per-GPU batch 越小，通信占比上升更快

**MoE 模型扩展的特殊性**：

| 因素 | 对扩展效率的影响 |
|:-----|:----------------|
| All-to-All 通信 | MoE 中 All-to-All 随 GPU 数线性增长 |
| Expert 负载不均 | 路由偏好导致部分 expert 过载 |
| 容量因子（Capacity Factor） | 值越大，通信量越大 |

### 2.6 内存带宽利用率

**定义**：实际 HBM 带宽利用率与理论峰值的比例。

**测量方法**：

```bash
# BabelStream 基准
python babel_stream.py --device cuda --size 1G

# PyTorch 中直接测量
torch.cuda.reset_peak_memory_stats()
output = model(input)
bandwidth = torch.cuda.max_memory_allocated() / elapsed_time
```

**H100 SXM（HBM3, 3.35 TB/s）典型利用层级：**

| 场景 | 利用率 | 说明 |
|:-----|:-------|:------|
| 纯访存 benchmark | ~85% | HBM 读写峰值 |
| Attention 层 | ~60-75% | 受 Flash Attention v2/v3 影响 |
| MLP 层 | ~40-55% | 计算-访存混合，非纯访存模式 |
| Decode 阶段（推理） | ~80-90% | 显存带宽是绝对瓶颈 |

### 2.7 显存容量与利用率

**训练显存占用公式**：
```
total_memory = model_weights + optimizer_states + gradients + activations + buffers
```

| 组件 | 计算方式 | 典型值（175B, FP16） |
|:-----|:---------|:---------------------|
| **Model Weights** | N_params × dtype_bytes | 175B × 2 = 350 GB |
| **Optimizer States (Adam)** | N_params × 2 × 4 (fp32) | 175B × 8 = 1,400 GB（ZeRO 可分区）|
| **Gradients** | N_params × dtype_bytes | 175B × 2 = 350 GB |
| **Activations** | seq_len² × n_layers × d_head × n_heads × dtype | 随 seq_len 平方增长 |
| **总计（未 ZeRO）** | — | ~2,100 GB（远超单 GPU 80GB）|

**ZeRO 阶段后显存占用**：

| ZeRO Stage | Weight | Grad | Optimizer | Act |
|:-----------|:-------|:-----|:----------|:----|
| Stage 1 | 全量 | 全量 | 分片 | 全量 |
| Stage 2 | 全量 | 分片 | 分片 | 全量 |
| Stage 3 | 分片 | 分片 | 分片 | 全量 |
| Stage 3 + Act offload | 分片 | 分片 | 分片 | 分片 |

**参考目标**：
- **Peak Memory Utilization**（峰值占用 / 总显存）> 90%
- 若 < 70% 说明 batch size 可以加大

---

## 3. 存储与 IO 指标群（训练）

### 3.1 Checkpoint 指标

| 指标 | 公式 | 说明 | 参考目标 |
|:-----|:-----|:-----|:---------|
| **Checkpoint Write BW** | model_ckpt_size / write_time | 将权重+优化器状态写入持久化存储 | >20 GB/s（NVMe）<br>>100 GB/s（并行 FS）|
| **Checkpoint Read BW** | model_ckpt_size / load_time | 故障恢复/续训练读入速度 | >30 GB/s |
| **Checkpoint Interval** | 两次 ckpt 间 step 数 | 太短降效率，太长增故障损失 | 50-200 steps |
| **Checkpoint Overhead** | ckpt_time / total_time | 写检查点占训练时间比例 | 理想 <2% |
| **Checkpoint Size** | 单次检查点大小 | 权重+优化器+随机状态 | 100-800 GB（700B 模型）|

**Checkpoint 大小估算公式**：
```
ckpt_size = weights(fp16) + optimizer(fp32) + random_state
          = N × 2 + N × 2 × 4 + small
          ≈ N × 10 bytes  ≈ 10× 模型参数量
```

**前沿优化方向（2026 年）**：
- **Async Checkpoint**：后台异步写入，零写入开销
- **DiffCp**：差分压缩，利用梯度稀疏性，减少 89.2% 写入量

### 3.2 数据加载指标

| 指标 | 含义 | 理想值 | 测量方法 |
|:-----|:------|:-------|:--------|
| **Data Loading Throughput** | 每秒预处样本供给 | ≥ 模型消耗速度 × 1.2 | DataLoader 计时 hook |
| **IO Prefetch Hit Rate** | 预取命中率 | >90% | 自定义 prefetch 计数器 |
| **Storage Read BW** | 并行 FS 读带宽 | ≥ 训练峰值需求 | `fio --rw=read --numjobs=64` |
| **Caching Efficiency** | 内存/SSD 缓存命中率 | ≥ 70% | 缓存层统计 |
| **Dataloader Stall** | GPU 等数据时间占比 | <5% | NVTX range 标注 |

### 3.3 并行文件系统基准

| 基准 | 测试内容 | 命令示例 |
|:-----|:---------|:---------|
| **IOR** | 并行 I/O 带宽（N-1 / N-N） | `mpirun -np 128 ior -w -r -b 16m -t 1m -F` |
| **mdtest** | 元数据性能 | `mpirun -np 128 mdtest -n 100000 -d /path` |
| **fio** | 单节点吞吐上限 | `fio --name=test --bs=1M --rw=read --numjobs=16` |
| **Darshan** | 应用层 I/O 模式诊断 | 自动记录，`darshan-parser` 分析 |

---

## 4. 推理任务核心指标群

### 4.1 延迟指标

| 指标 | 全称 | 单位 | 含义 | 在线场景目标 |
|:-----|:-----|:-----|:-----|:------------|
| **TTFT** | Time To First Token | ms | 用户发送请求到收到第一个 token | <200ms（对话）<br><500ms（流式）|
| **TPOT** | Time Per Output Token | ms/token | 每生成一个 token 的时间 | <30ms（对话）<br><50ms（通用）|
| **ITL** | Inter-Token Latency | ms | 连续输出 token 的间隔时间 | <50ms |
| **E2E Latency** | End-to-End | s | 完整请求耗时 | 取决于输出长度 |

**关于延迟分布**：仅报告平均值不够，必须报告 P50 / P95 / P99 分位值。

### 4.2 Prefill vs Decode 分解

推理的两个阶段资源瓶颈完全不同，必须分开测量：

```
Total Latency = Prefill Time + Sum(Decode Time for each token)
```

| 阶段 | 瓶颈类型 | 核心指标 | 典型值（70B LLaMA, H100） |
|:----|:---------|:---------|:--------------------------|
| **Prefill** | 计算密集型（Attention 矩阵乘） | **Prefill Throughput** = input_tokens / prefill_time | >50,000 tokens/s/GPU |
| **Decode** | 显存带宽受限（KV Cache 读取） | **Decode Throughput** = 1 / TPOT | 30-50 tokens/s/GPU |

**Prefill 的影响因素**：
- 输入长度越长，Prefill 效率越高（有效计算比例大）
- Flash Attention v2/v3 显著提升长序列 Prefill 效率

**Decode 的影响因素**：
- Batch size 越大，decode latency 越高（但总吞吐越高）
- GQA / MQA 可减轻 KV Cache 读取带宽压力
- FP8 / INT8 KV Cache 压缩可提升 decode 吞吐

### 4.3 吞吐指标

| 指标 | 公式 | 说明 |
|:-----|:-----|:------|
| **RPS（Requests Per Second）** | concurrent_users / avg_latency | 系统服务能力 |
| **Output Token Throughput** | generated_tokens / total_time | 核心产出指标 |
| **Input Token Throughput** | input_tokens / total_time | Prefill 阶段能力 |
| **Batch Throughput** | batch_size × seq_len / total_time | 动态批处理性能 |
| **QPS（Queries Per Second）** | 请求数 / 时间 | **必须附带延迟约束一同报告** |

**QPS 报告规范**：
```
QPS = 100 @ P99 TTFT < 200ms, P99 TPOT < 30ms
QPS = 500 @ P99 TTFT < 500ms, P99 TPOT < 50ms
```

### 4.4 服务质量（SLO/SLA）指标

| 指标 | 定义 | 目标 |
|:-----|:-----|:-----|
| **SLO Attainment** | 满足延迟 SLO 的请求占比 | >99%（在线）/ >95%（离线）|
| **P50 TTFT** | TTFT 中位延迟 | <200ms |
| **P99 TTFT** | TTFT 尾部延迟 | <500ms |
| **P50 TPOT** | TPOT 中位延迟 | <30ms |
| **P99 TPOT** | TPOT 尾部延迟 | <50ms |
| **TTFT Jitter** | TTFT 方差 / 均值 | <30% |
| **Timeout Rate** | 超时请求占比 | <0.1% |
| **Error Rate** | 返回错误请求占比 | <0.01% |

### 4.5 KV Cache 相关指标

KV Cache 是推理系统的核心瓶颈——显存占用和读取带宽共同制约 decode 吞吐。

| 指标 | 说明 | 估算公式 / 测量方法 |
|:-----|:-----|:---------------------|
| **KV Cache Size per Token** | 每 token KV 缓存字节 | `num_layers × d_model × 2 (K+V) × dtype_bytes × 2` |
| **KV Cache per Request** | 完整请求占用 | `token_count × KV_Cache_size_per_token` |
| **KV Cache Hit Rate** | 前缀/共享缓存命中率 | Prometheus counter / 缓存层统计 |
| **KV Cache Transfer Latency** | 跨节点迁移延迟 | Disaggregated Serving 场景微基准 |
| **KV Cache Eviction Rate** | 淘汰率 | 缓存管理日志（LRU / LFU）|
| **KV Cache Compression Ratio** | 量化压缩比 | 原始 size / 压缩 size |

**典型计算示例（LLaMA-3.1 405B）**：
- num_layers = 126, d_model = 16,384, per head = 128, n_heads = 128
- KV Cache per token（FP16）≈ `126 × 16,384 × 2 × 2` ≈ **8.2 MB/token**
- 4,096 tokens 的单请求 ≈ **32 GB** KV Cache

**前沿优化方向（2026 年）**：
- **KV Cache 共享**：Prefix Caching / Radix Cache 减少重复 prefill
- **KV Cache 量化**：FP8 (2×) / INT4 (4×) / Block-GTQ (3.24×) 压缩
- **Disaggregated Serving**：Prefill / Decode 分离架构，KV Cache 在节点间迁移
- **KV Cache offload**：SSD KV Cache 交换（CacheWise 减少驱逐 2-2.6×）

### 4.6 批处理与系统效率

| 指标 | 含义 | 测量方法 |
|:-----|:-----|:---------|
| **Dynamic Batching Efficiency** | 批处理累积时延 vs 静态批处理比 | 不同 QPS 下对比 |
| **Continuous Batching 增益** | 流水线式批处理 vs 传统批处理 | 逐 batch 计时对比 |
| **Time-to-First-Token 拐点** | 批处理达到某个 size 后 TTFT 急剧上升 | QPS 压力测试 |
| **Max Concurrency** | 不违反 SLO 的最大并发数 | 逐步加压测试 |
| **GPU Utilization（推理）** | 推理阶段 GPU 利用率 | `nvidia-smi` / DCGM |
| **Compute vs Memory Stall Ratio** | 计算等待 vs 访存等待比 | Nsight Compute |

### 4.7 KV Cache 共享存储评估与测试方案

KV Cache 共享存储（如 NVIDIA CMX G3.5 / Disaggregated Serving 中的 KV Cache 池）通过将 KV Cache 从 HBM 卸载到共享存储层，解耦 Prefill 和 Decode 阶段的显存需求，提升集群利用率。本节提供全套评估方案。

#### 4.7.1 评估维度总览

KV Cache 共享存储的评估需从 **容量 / 带宽 / 延迟 / 一致性 / 可靠性** 五个维度展开：

```
┌──────────────────────────────────────────────────────────────────┐
│                    KV Cache 共享存储评估矩阵                        │
├────────────┬────────────────────┬──────────────────┬─────────────┤
│   维度     │      核心指标       │     关键约束      │  影响面     │
├────────────┼────────────────────┼──────────────────┼─────────────┤
│ 容量       │ 可用容量 / GPU / 池 │ 每 token 字节数    │ 并发度上限   │
│ 带宽       │ 读/写吞吐 (GB/s)   │ 共享存储总带宽     │ Decode 延迟  │
│ 延迟       │ P2P 获取延迟 (μs)  │ HBM 延迟 vs 网络   │ TPOT tail   │
│ 一致性     │ Cache 版本 / 过期   │ 写透/回写策略      │ 推理正确性   │
│ 可靠性     │ 数据损坏率 / 恢复   │ ECC / 副本策略     │ 服务可用性   │
└────────────┴────────────────────┴──────────────────┴─────────────┘
```

**核心权衡**：KV Cache 共享存储的收益来源于 HBM 容量扩展 × 集群利用率提升，代价是引入存储层延迟和带宽瓶颈。评估目标是在可接受的 TPOT 劣化幅度内最大化有效并发度。

#### 4.7.2 容量评估

**单请求 KV Cache 占用**：

```
KV_Cache_bytes = num_layers × (d_model × 2 × dtype_bytes) × seq_len ÷ num_kv_heads_group
```

其中：
- `d_model × 2`：K 和 V 各一份
- `dtype_bytes`：FP16=2, FP8=1, INT4=0.5
- `num_kv_heads_group`：MQA=1, GQA=group_size

**典型值速查表**：

| 模型 | 参数 | 每 token KV Cache (FP16) | 4K seq 单请求 | 32K seq 单请求 |
|:-----|:-----|:------------------------:|:-------------:|:--------------:|
| LLaMA-3.1 8B | 32层×4096d×8KV | ~2.1 MB | ~8.2 GB | ~65.5 GB |
| LLaMA-3.1 70B | 80层×8192d×8KV | ~10.5 MB | ~41.0 GB | ~328 GB |
| LLaMA-3.1 405B | 126层×16384d×8KV | ~32.8 MB | ~128 GB | ~1,024 GB |
| GPT-4 class | 120层×16384d×16KV | ~62.9 MB | ~246 GB | ~1,966 GB |

**共享存储容量评估公式**：

```
Required_Capacity = Concurrent_Requests × Avg_KV_Cache_Per_Request × Replication_Factor
                  / Compression_Ratio

举例（405B, 4K seq, FP16, 1024 并发, 2×副本）:
  = 1024 × 128 GB × 2 / 1
  = 262,144 GB ≈ 256 TB （未压缩）
  
  = 1024 × 128 GB × 2 / 4 （INT4 量化）
  = 65,536 GB ≈ 64 TB
```

**容量评估测试方案**：

| 测试项 | 方法 | 指标 |
|:-------|:-----|:------|
| **单请求占用验证** | 用目标模型实际推理，`torch.cuda.memory_allocated()` 对比公式估算 | 偏差率 <10% |
| **并发容量扫描** | 逐步增加并发请求数，监控共享存储池容量水位 | Max Concurrent w/o OOM |
| **压缩比实测** | 同模型不同量化方案（FP16/FP8/INT4/Block-GTQ）对比实际 KV Cache 大小 | 压缩率 / PPL 损失 |
| **容量利用率** | 池化容量中有效 KV Cache 占比（考虑碎片 + 预热空间） | >70% 为健康 |

```python
# 容量评估脚本骨架
import torch

def measure_kv_cache_per_token(model, input_ids):
    """测量每 token 的 KV Cache 实际占用"""
    torch.cuda.reset_peak_memory_stats()
    past_kv = model(input_ids, use_cache=True).past_key_values
    kv_bytes = torch.cuda.max_memory_allocated() / input_ids.shape[1]
    return kv_bytes  # bytes/token

def scan_concurrent_capacity(model_cls, kv_pool_size_GB, seq_lens, quant_levels):
    """扫描不同并发数下的容量拐点"""
    for seq_len in seq_lens:
        for quant in quant_levels:
            concurrent = 1
            while concurrent * kv_per_request(seq_len, quant) < kv_pool_size_GB * 0.9:
                concurrent *= 2
            print(f"seq={seq_len}, {quant}: max_concurrent ≈ {concurrent}")
```

#### 4.7.3 带宽评估

**带宽需求模型**：

```
读带宽需求 = Concurrent_Decode_Tokens/s × KV_Cache_Per_Token
写带宽需求 = Concurrent_Prefill_Tokens/s × KV_Cache_Per_Token

举例（405B, FP16, 1024 并发, 平均 decode 30 tokens/s/req）:
  读 = 1024 × 30 × 32.8 MB ≈ 1,006 GB/s ≈ 1 TB/s
  写 = 每个 prefill 写入一次 128 GB (4K seq), 10 req/s → 1,280 GB/s
```

**注意**：KV 共享存储的读写带宽需求可能超过单个存储节点的能力，需分布式并行化。

**带宽评估测试方案**：

| 测试项 | 方法 | 指标 | 健康阈值 |
|:-------|:-----|:------|:---------|
| **读取峰值带宽** | 纯读压测：多线程读取不同 seq_len 的 KV Cache 块 | Read BW (GB/s) | >模型消耗需求的 1.5× |
| **写入峰值带宽** | 纯写压测：多线程写入 KV Cache 条目 | Write BW (GB/s) | >模型消耗需求的 1.5× |
| **读写混合场景** | 模拟 Prefill 写入 + Decode 读取同时进行 | Mixed BW / 读写冲突率 | 读降速 <20% |
| **不同块大小带宽** | KV Cache 块大小从 1MB 到 1GB 步进 | BW vs 块大小曲线 | 小块场景 ≤64KB 时须关注 |
| **带宽饱和度拐点** | 逐步增加并发读写流数，记录带宽趋于饱和 | Max 有效并发带宽 | 拐点前满足峰值需求 |

**微基准测试脚本**：

```bash
# 1. 读取带宽测试（模拟 decode 读取）
fio --name=kv-cache-read \
    --ioengine=libaio --direct=1 \
    --rw=randread --bs=32M --numjobs=32 \
    --size=10G --runtime=60 \
    --iodepth=16 --time_based

# 2. 写入带宽测试（模拟 prefill 写入）
fio --name=kv-cache-write \
    --ioengine=libaio --direct=1 \
    --rw=write --bs=128M --numjobs=16 \
    --size=10G --runtime=60 \
    --iodepth=8 --time_based

# 3. 块大小扫描
for bs in 1M 4M 16M 32M 64M 128M 256M; do
    fio --name=kv-bs-scan --rw=randread \
        --bs=$bs --numjobs=16 --size=10G --runtime=30 --time_based
done

# 4. 延迟-IOPS 曲线
fio --name=kv-lat-curve --rw=randread --bs=32M \
    --numjobs=1 --size=10G --runtime=60 \
    --lat_percentiles=1 --output-format=json
```

**存储网络+节点级集成测试**：

```bash
# NVMe-oF 场景：GPU → PCIe → CX7 → RoCE → 存储节点
# 使用 perftest 测试 RDMA 读写带宽 + 延迟
ib_read_bw -d mlx5_0 --report_gbits   # RDMA 读带宽
ib_write_bw -d mlx5_0 --report_gbits  # RDMA 写带宽
ib_read_lat -d mlx5_0                  # RDMA 读延迟（关键！）
```

#### 4.7.4 延迟评估

KV Cache 共享存储的访问延迟直接影响 Decode 阶段 TPOT，是**决定方案是否可行的关键约束**。

**延迟预算分解**：

```
TPOT_increase = KV_Cache_Read_Latency + Transfer_Latency + Deserialize_Latency

典型分解:
  ┌─ KV Cache 存储读延迟:    50-200 μs (NVMe-oF) / 10-50 μs (CXL)
  ├─ 网络传输延迟:           5-20 μs (RoCE/InfiniBand)
  ├─ 反序列化/内存拷贝:      5-10 μs (FP16→FP16直传)
  └─ 总增量:                 60-230 μs / token

对比基线:
  ┌─ HBM 本地 KV Cache 读取:  <1 μs
  └─ 共享存储引入的增量:      60-230× 延迟放大
```

**然而**，HBM 容量限制使得 KV Cache 共享成为**必要性**方案。关键在于 TPOT 劣化是否可控在 SLO 范围内。

**延迟评估测试方案**：

| 测试项 | 方法 | 输出 |
|:-------|:-----|:------|
| **单次 KV Cache 块读延迟** | 读取固定大小 KV 块（16MB/32MB/64MB/128MB），记录 P50/P95/P99 | 延迟分布曲线 |
| **网络往返延迟** | 存储端 ping-pong 测试（`ib_read_lat`），排除存储介质延迟 | RDMA RTT |
| **端到端 P2P 取回延迟** | GPU 侧直接读取远端 KV Cache 块 → GPU HBM | End-to-end latency |
| **并发读延迟退化** | 逐步增加并发读取流，观察延迟拐点 | 延迟 vs 并发曲线 |
| **块大小与延迟关系** | 不同 KV Cache 块大小对延迟的影响 | 最优块大小识别 |
| **Preload vs On-Demand** | 预取策略（提前加载到本地 HBM）vs 按需读取的延迟对比 | 缓存命中率收益 |
| **TPOT 实际劣化测量** | 端到端推理：在启用/关闭共享存储下分别测量 TPOT | ΔTPOT |

**关键工程经验**：

- 当 KV Cache 块大小 ≤ 4MB 时，**网络协议开销占比 >50%** → 应合并小请求
- 预取（Prefetch）策略可将感知延迟降低 3-5×
- FP8 KV Cache 不仅节省容量，还减少读取带宽需求 → 间接降低延迟
- NVMe-oF over RDMA 在块大小 16-64MB 区间达到最佳效率（带宽/延迟比最优）

**端到端 TPOT 劣化容忍度参考**：

| 场景 | TPOT 劣化容忍度 | 共享存储策略 | 量化需求 |
|:-----|:---------------|:------------|:---------|
| **在线对话（SLO 严格）** | <20% (6ms @ 30ms baseline) | Preload 优先 + 本地缓存 | INT4/FP8 必须 |
| **离线批处理** | <50% (15ms @ 30ms) | On-Demand 按需读取 | FP8 推荐 |
| **长序列推理** | 可接受更高（HBM 不足时唯一方案） | 可全量 On-Demand | 量化后压缩传输 |

#### 4.7.5 一致性评估

KV Cache 共享存储面临的主要一致性问题是：**Prefill 实例写入的 KV Cache 何时对 Decode 实例可见**（Read-After-Write 语义）。

**一致性模型**：

| 模型 | 说明 | 适用场景 | 实现复杂度 |
|:-----|:------|:---------|:-----------|
| **写透 (Write-Through)** | Prefill 写完立即同步到共享存储，Decode 读到最新 | 在线对话 | 高（需同步屏障） |
| **写回 (Write-Back)** | Prefill 本地缓存 → 异步刷回，Decode 可能读到旧版本 | 离线批处理 | 中 |
| **版本控制** | 每个 KV Cache 带版本号，Decode 检查版本一致性 | 混合负载 | 高 |
| **前缀哈希** | 基于输入前缀哈希的确定性 KV Cache，无一致性问题 | Prefix Caching | 低 |

**一致性测试方案**：

| 测试项 | 方法 | 通过条件 |
|:-------|:-----|:---------|
| **Read-After-Write 延迟** | Prefill 完成 → Decode 读到最新 KV Cache 的时间间隔 | <100ms（在线）/<1s（离线）|
| **Stale Read Rate** | Decode 读到过期 KV Cache 的比例 | <0.01%（在线）/<1%（离线）|
| **版本冲突检测** | 并发写入同一个 KV Cache slot 时检测冲突 | 检测率 100% |
| **因果一致性验证** | 模拟多轮对话，检查 Decode 结果是否基于最新上下文 | 输出与本地 HBM 结果一致 |
| **并发读写正确性** | 多个 Decode 实例同时读取同一个 Prefill 产出的 KV Cache | 所有 Decode 结果一致 |

```python
# 一致性验证脚本骨架
def verify_consistency(model, prefill_input, decode_inputs):
    """验证共享 KV Cache 读写的语义一致性"""
    # 1. 本地 HBM 基准（无共享存储）
    ref_output = model(prefill_input + decode_inputs)
    
    # 2. 共享存储解耦模式
    kv_cache = prefills_on_shared_store(model, prefill_input)
    shard_outputs = []
    for inp in decode_inputs:
        out = decode_with_shared_kv(model, inp, kv_cache)
        shard_outputs.append(out)
    
    # 3. 逐 token 比较
    for i, (ref, shard) in enumerate(zip(ref_output, torch.cat(shard_outputs))):
        if not torch.allclose(ref, shard, atol=1e-5):
            print(f"Consistency FAIL at position {i}: {ref.item():.6f} vs {shard.item():.6f}")
            return False
    return True
```

#### 4.7.6 可靠性评估

| 测试项 | 方法 | 指标 | 通过条件 |
|:-------|:-----|:------|:---------|
| **数据损坏率** | 长时间读写后，逐 byte 校验 KV Cache 数据 | UBER (Uncorrectable Bit Error Rate) | <10⁻¹⁵ |
| **存储节点故障恢复** | 随机 Kill 存储节点，观察 KV Cache 可用性 | Recovery Time / 丢失比例 | <30s / <1% |
| **网络中断容忍** | 断网重连后 KV Cache 的一致性 | Cache 热恢复时间 | <10s |
| **持久化与重放** | 检查 KV Cache 是否可持久化到 NVMe 并恢复 | 恢复正确性 | 100% 一致 |
| **ECC 错误注入** | 注入存储介质 ECC 错误，观察感知与修复 | 错误检测率 / 修复率 | >99.99% |

#### 4.7.7 综合评估流程

```text
KV Cache 共享存储评估 7 步流程

Step 1: 容量规划
  ├─ 目标模型参数量 + KV Cache 量化方案
  ├─ 期望并发度 + 序列长度分布
  └─ 输出: Required Pool Capacity

Step 2: 存储介质选型测试
  ├─ NVMe SSD (本地) vs NVMe-oF (远端) vs CXL 内存
  ├─ 评测: BW / Latency / 并发扩展 / 成本
  └─ 输出: 存储层级推荐方案

Step 3: 网络传输标定
  ├─ RDMA 读/写带宽 + 延迟基线（ib_read_bw/ib_read_lat）
  ├─ 消息大小扫描（1MB → 256MB 寻找最佳块大小）
  └─ 输出: 网络层性能基线

Step 4: 单请求端到端验证
  ├─ 完整 Prefill → 共享存储写入 → Decode 读取 pipeline
  ├─ 对比本地 HBM 模式的 TTFT/TPOT 差异
  └─ 输出: ΔTPOT（劣化量）

Step 5: 并发压力测试
  ├─ 逐步增加并发请求数至目标并发度
  ├─ 监控：延迟、带宽饱和、缓存命中率、一致性
  └─ 输出: SLO Attainment vs 并发数曲线

Step 6: 故障注入测试
  ├─ 存储节点 Kill / 网络抖动 / ECC 错误注入
  ├─ 评估恢复时间和数据完整性
  └─ 输出: MTTR / 数据可靠性

Step 7: 规模化验证
  ├─ 满配并发（目标并发度 × 目标模型）运行 24h+
  ├─ 记录：TPOT 分布、缓存命中率、故障事件
  └─ 输出: 最终评估报告 + 推荐配置
```

#### 4.7.8 评估工具链速查

| 工具 | 用途 | 命令/代码 |
|:-----|:------|:----------|
| **fio** | 存储微基准（带宽/延迟/IOPS） | `fio --rw=randread --bs=32M --numjobs=32` |
| **perftest** | RDMA 网络微基准 | `ib_read_bw` / `ib_read_lat` / `ib_write_bw` |
| **nvme-cli** | NVMe 设备级性能 | `nvme list` / `nvme smart-log` |
| **vLLM benchmark** | 端到端推理 + KV Cache 策略 | 见§7 |
| **自定义 Python 脚本** | KV Cache 块大小扫描 / 一致性验证 | §4.7.2 / §4.7.5 代码示例 |
| **DCGM** | GPU 显存使用量追踪 | `dcgmi dmon -e 1009,1010` |
| **Prometheus + Grafana** | 共享存储池监控面板 | 自定义 metrics endpoint |
| **chaos-mesh** | 故障注入（Kill 存储节点/网络抖动） | `chaos-cli create network delay` |

#### 4.7.9 业界参考基线

| 方案 | 存储介质 | 访问延迟 | 有效带宽 | 典型应用 |
|:-----|:---------|:---------|:---------|:---------|
| NVIDIA CMX G3.5 | BF4 DPU + NVMe SSD + Spectrum-X | ~100 μs (全链路) | ~200 GB/s (单 tray) | DGX GB300 解耦推理 |
| CacheWise (2026) | RDMA + NVMe-oF + 预取引擎 | ~50 μs (hit) / ~200 μs (miss) | P99 TPOT < 50ms | 通用 Disaggregated Serving |
| CXL 3.1 Shared Memory | CXL Switch + CXL 内存模块 | ~1-5 μs | ~100 GB/s per link | 低延迟共享方案 |
| NCCL P2P + SSD | GPU-Direct RDMA → NVMe SSD | ~200 μs | ~7 GB/s (单盘) | 轻量实验方案 |

**总结**：KV Cache 共享存储的核心评估决策链是 **容量缺口 → 量化方案 → 延迟预算 → 预取策略 → 并发拐点**，建议按 §4.7.7 的 7 步流程推进，最终以端到端 SLO Attainment 作为验收标准。

---

## 5. 网络维度指标

### 5.1 通信微基准

| 指标 | 测量方法 | 工具 | 参考理想值 |
|:-----|:---------|:-----|:----------|
| **Uni-directional BW** | ping-pong 测试 | `ib_write_bw` / perftest | ~400 Gbps per link |
| **Bi-directional BW** | 双向 ping-pong | `ib_write_bw --bidir` | ~800 Gbps per link |
| **Message Latency** | 小消息 RTT | `ib_write_lat` / `osu_latency` | <1.5μs（节点内）<3μs（节点间）|
| **AllReduce BW（intra-node）** | 8 GPU allreduce | NCCL-Tests / osu_allreduce | >400 GB/s（NVLink5）|
| **AllReduce BW（inter-node）** | 跨 8 节点 allreduce | `nccl-tests -n 8` | >50 GB/s（IB NDR800）|
| **All-to-All BW（intra）** | 节点内 MoE 模式 | `nccl-tests --alltoall` | >200 GB/s |
| **All-to-All BW（inter）** | 跨节点 MoE 模式 | `nccl-tests --alltoall -n 8` | >30 GB/s |
| **Ring Latency** | 环拓扑端到端延迟 | 自定义 barrier timing | <10μs（节点内）<50μs（跨节点）|
| **GPU Direct P2P BW** | 跨节点 P2P | `cuda-samples/p2pBandwidthLatencyTest` | 受网络拓扑影响 |

**注意事项**：
- 测量结果需**注明消息大小**（128B / 1MB / 128MB / 1GB 差异极大）
- NCCL-tests 报告 **BusBW**（总线带宽）和 **AlgoBW**（算法带宽）两个口径
- NCCL-tests 输出示例：`# nThread 1 nGpus 8 minBytes 128M maxBytes 128M`

### 5.2 通信模式扩展效率

| 通信模式 | N 卡扩展曲线 | 关键瓶颈 | 优化方案 |
|:---------|:------------|:---------|:---------|
| **AllReduce（同步训练）** | 对数增长，N=512 后趋平 | Ring 算法带宽受限于单链路 | Tree/Ring 混合 / SHARP 卸载 |
| **All-to-All（MoE）** | 线性增长（随 expert 数） | 拥塞 + Outcast 超时 | Hierarchical A2A / MSCC |
| **ReduceScatter** | BW = busBW / (N-1) | chip-to-chip 带宽 | NVLink SHARP |
| **AllGather** | BW = busBW × (N-1) / N | 接收端竞争 | 拓扑感知调度 |
| **P2P Send/Recv** | 延迟随跳数线性增长 | 拓扑跳数 / 拥塞 | GPU-Direct RDMA / 自适应路由 |

### 5.3 网络拥塞指标

| 指标 | 含义 | 测量方法 | 健康阈值 |
|:-----|:-----|:---------|:---------|
| **ECN Marking Rate** | 拥塞信号频率 | 交换机计数器 | <1% |
| **CNP Rate** | 拥塞通知包频率 | 网卡统计（`mlx5_perf`）| <0.1% |
| **Tail Latency Inflation** | P99 vs P50 延迟比 | 通信库内置统计 | <3× |
| **Packet Drop Rate** | 丢包率 | 交换机日志 / 网卡计数器 | 理想 0 |
| **Outcast Timeout** | 流冲突导致的重传超时 | NCCL debug 统计 | 0 |
| **Hol Blocking Ratio** | 头阻塞（HOL）比例 | 端口级延迟分布 | <5% |

### 5.4 NCCL 内部指标

| 指标 | 含义 | 获取方式 |
|:-----|:-----|:----------|
| **NCCL Algorithm BW** | 算法层有效带宽 | `NCCL_DEBUG=TRACE` / nccl-tests 输出 |
| **NCCL Protocol Overhead** | 协议栈开销占比 | trace 中 non-payload 时间 |
| **NCCL Ring Rounds** | 环算法通信轮数 | `nccl-tests --verbose` |
| **NCCL NVLink Error Rate** | NVLink 链路错误率 | `nvidia-smi nvlink -e` |
| **NCCL CollNet 对比** | SHARP 卸载 vs 纯 SW 对比 | 开关测试 `NCCL_COLLNET_ENABLE=1` |

---

## 6. 系统级综合指标

### 6.1 有效利用率

| 指标 | 公式 | 说明 |
|:-----|:-----|:------|
| **Goodput** | (总时间 − 故障损失 − 空等待) / 总时间 | 真正干"有用计算"的占比 |
| **Effective MFU** | MFU × Goodput | 考虑故障的现实 MFU |
| **Training Efficiency** | 实际收敛速度 / 理论最优收敛 | 包含 batch size 影响（梯度噪声尺度）|
| **GPU Hours Wasted** | 总 GPU 小时 − 有效 GPU 小时 | 绝对值度量 |
| **Idle GPU Ratio** | 空闲 GPU 时间 / 总时间 | <10% |

### 6.2 故障恢复相关

| 指标 | 含义 | 计算 |
|:-----|:-----|:------|
| **MTTI** | 故障平均检测时间 | 从故障发生到被检测到的时间 |
| **MTTR** | 故障平均恢复时间 | 从检测到恢复训练的时间 |
| **MTBF** | 平均无故障时间 | 集群正常运行时间 / 故障次数 |
| **Wasted Work** | 故障到上次 ckpt 间的计算量 | `ckpt_interval × step_time × (#fails)` |
| **Wasted Ratio** | 浪费计算 / 总计算 | <5% |
| **Cluster Availability** | 集群可用 GPU 占比 | 正常 GPU / 总 GPU × 100% |
| **Silent Data Corruption Rate** | 静默数据损坏率 | 极低 <10⁻¹⁰ |

**故障率的经验数据（2026 年公开报告）**：
- 万卡集群每周 1-3 次 GPU 显存 ECC 错误
- 网络链路抖动每 48 秒一次（3M GPU 规模）
- 典型 ckpt interval 50-100 steps → 故障平均损失 25-50 steps

### 6.3 成本效率

| 指标 | 公式 | 说明 |
|:-----|:-----|:------|
| **Cost per Token（训练）** | 总成本 / 总训练 tokens | 每 token 训练成本 |
| **Cost per Token（推理）** | 时租成本 × 推理耗时 / tokens | 每 token 推理成本 |
| **$/GPU-Hour Effective** | 总成本 / (GPU 数 × Goodput) | 有效时租（考虑了故障/等待）|
| **TCO Efficiency** | tokens/dollar / 集群生命周期 | 长期经济性 |

### 6.4 能效指标

| 指标 | 公式 | 说明 | 参考值 |
|:-----|:-----|:------|:-------|
| **Energy Efficiency** | tokens/s / kW | 每千瓦 token 产出 | H100: ~10 tokens/s/kW（训练）|
| **TFLOPS/W** | 实际 TFLOPS / 功耗 | 每瓦计算效率 | H100: ~60 TF/W（BF16）|
| **TDP Utilization** | 实际功耗 / TDP | 功率利用充分性 | 理想 >90% |
| **PUE** | 总能耗 / IT 设备能耗 | 基础设施效率 | 理想 <1.2 |
| **Carbon Intensity** | gCO₂eq / token | 碳排放 | 取决于电网 |

---

## 7. 度量方案与工具链

### 7.1 各维度推荐工具速查

| 维度 | 工具（2026 年有效） | 关键能力 | 获取方式 |
|:-----|:--------------------|:---------|:----------|
| **GPU 微基准** | babel-stream / ncu / pure PyTorch | HBM 带宽、峰值 TFLOPS | `pip install babel-stream` |
| **网络通信** | NCCL-Tests / OSU Micro-Benchmarks / perftest | AllReduce / All-to-All / P2P | `git clone` + `make` |
| **端到端训练** | Megatron-LM Profiler / DeepSpeed Profiler / torch.profiler | Step time / MFU / 通信占比 | 随框架自带 |
| **端到端推理** | vLLM Benchmarks / LLMPerf / TGI Benchmark | TTFT / TPOT / QPS / 并发 | `pip install vllm` |
| **存储 IO** | fio / IOR / mdtest / Darshan | 带宽 / IOPS / 延迟分布 | OS 包管理器 |
| **全栈链路追踪** | Nsight Systems / Perfetto / HTA | 端到端 timeline / 瓶颈归因 | NVIDIA 开发者 / `pip install holistic-trace-analysis` |
| **集群监控** | DCGM-exporter + Prometheus + Grafana / W&B | GPU 温度/功耗/利用率 | GitHub / docker |
| **通信 Profiling** | NCCL DEBUG TRACE / Nsight Compute | Ring 拓扑 / 流追踪 / kernel 级分析 | 环境变量 / SDK |
| **分布式 Profiling** | HTA / TensorBoard | 全节点 trace 聚合分析 | `pip install holistic-trace-analysis` |

### 7.2 端到端训练性能评估流程

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: 环境标定                                             │
│  ├─ 单卡理论峰值确认 (ncu)                                   │
│  ├─ 单卡显存带宽 (babel-stream)                              │
│  └─ 网络 BW/Latency 基线 (nccl-tests)                        │
├──────────────────────────────────────────────────────────────┤
│  Step 2: 负载初始化                                           │
│  ├─ 选定模型（GPT-175B / LLaMA-70B / MoE-1T）               │
│  ├─ 选定并行策略（TP/PP/DP/EP/SP 混合）                      │
│  └─ 选定 batch size / seq length                              │
├──────────────────────────────────────────────────────────────┤
│  Step 3: Profiling Run                                        │
│  ├─ 预热 50-100 steps                                         │
│  ├─ 记录 100+ steps 的 trace                                  │
│  └─ 保存 NCCL trace + timeline JSON                           │
├──────────────────────────────────────────────────────────────┤
│  Step 4: 分析产出的指标                                       │
│  ├─ MFU/HFU → 框架计算效率                                   │
│  ├─ Step time 分解 → 各阶段占比                              │
│  ├─ Communication Overhead → 通信是否瓶颈                    │
│  ├─ Memory Bandwidth Utilization → 是否显存带宽受限          │
│  └─ Scaling Efficiency → 多节点扩展效率损失                  │
├──────────────────────────────────────────────────────────────┤
│  Step 5: 瓶颈定位与优化                                       │
│  ├─ 计算瓶颈: Kernel 优化 / Flash Attention / FP8 切换       │
│  ├─ 通信瓶颈: 拓扑优化 / SHARP 卸载 / 计算-通信重叠          │
│  ├─ 存储瓶颈: 并行 FS 扩吞吐 / 异步数据加载                   │
│  └─ 负载不均: 均衡 token 分配 / expert 重路由                │
└──────────────────────────────────────────────────────────────┘
```

### 7.3 推理性能评估标准流程

```
┌──────────────────────────────────────────────────────┐
│  Step 1: 环境标定                                     │
│  ├─ Prefill vs Decode 理论最大吞吐推算               │
│  └─ KV Cache 容量上限计算                            │
├──────────────────────────────────────────────────────┤
│  Step 2: 负载初始化                                   │
│  ├─ 选定模型 + 量化方案 (FP8 / INT4 / INT8)          │
│  ├─ 设定 SLO 约束 (TTFT < 200ms, TPOT < 30ms)       │
│  └─ 选定 Request Rate / 并发数 / 输出长度分布        │
├──────────────────────────────────────────────────────┤
│  Step 3: 持续负载测试                                 │
│  ├─ 恒定 QPS 发送请求（60s+ 预热后 300s 采样）      │
│  ├─ 记录每个请求的 TTFT / TPOT / E2E                │
│  └─ 收集系统资源指标 (GPU util → decode/prefill 比)  │
├──────────────────────────────────────────────────────┤
│  Step 4: 性能分析                                     │
│  ├─ TTFT 分布 (P50/P95/P99) → Prefill 瓶颈判定      │
│  ├─ TPOT 分布 → Decode 瓶颈判定                     │
│  ├─ SLO Attainment → 服务质量                        │
│  └─ QPS vs Latency 曲线 → 拐点定位                  │
├──────────────────────────────────────────────────────┤
│  Step 5: 系统调优                                     │
│  ├─ Dynamic Batching 参数优化                        │
│  ├─ Continuous Batching / PagedAttention 效果评估    │
│  ├─ Disaggregated Serving (Prefill/Decode 分离)      │
│  └─ 缓存策略 (KV Cache Prefix Cache / Radix Cache)   │
└──────────────────────────────────────────────────────┘
```

### 7.4 典型评估脚本示例

**训练 MFU 快速测量：**

```bash
# 1. 单卡标定
ncu --metrics sm__throughput.avg.pct python train.py --model gpt-175b --profile

# 2. NCCL 基线
mpirun -np 64 --hostfile hosts.txt ./build/all_reduce_perf -b 128M -e 8G -f 2

# 3. 端到端训练 Profiling
nsys profile -o trace_64gpu \
  -t cuda,nvtx,osrt -c cudaProfilerApi \
  python train.py --model gpt-175b \
    --tensor-parallel 8 --pipeline-parallel 8 \
    --data-parallel 4 --global-batch-size 1024 --seq-length 8192
```

**推理端到端测试：**

```bash
# 1. 启动 vLLM 服务
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-405B \
  --tensor-parallel-size 8 --pipeline-parallel-size 4 \
  --max-num-seqs 256 --max-model-len 8192 \
  --gpu-memory-utilization 0.90

# 2. 持续负载测试
python benchmarks/benchmark_serving.py \
  --model meta-llama/Llama-3.1-405B \
  --request-rate 10 --num-prompts 1000 \
  --max-concurrency 64 --result-dir ./bench_results/

# 3. 单一请求延迟测试（基准）
python benchmarks/benchmark_latency.py \
  --model meta-llama/Llama-3.1-405B \
  --num-prompts 1 --input-len 128 --output-len 128
```

**网络通信速查脚本：**

```bash
# NCCL 测试（节点内）
mpirun -np 8 ./build/all_reduce_perf -b 8 -e 256M -f 2 -g 1

# NCCL 测试（跨节点）
mpirun -np 64 --hostfile hosts.txt \
  -x NCCL_ALGO=Ring \
  ./build/all_reduce_perf -b 128M -e 8G -f 2

# RDMA 延迟测试
ib_write_lat -d mlx5_0 --report_gbits
```

---

## 8. 快速诊断：指标交叉关联表

| 现象 | 可能瓶颈 | 需检查的指标对 |
|:-----|:---------|:--------------|
| **MFU 低 + GPU 利用率高** | 通信瓶颈 | Step Time 分解中 Communication 占比 vs AllReduce BW |
| **MFU 低 + GPU 利用率低** | 数据加载瓶颈 | IO Wait + Storage Read BW |
| **MFU 持续下降** | 负载不均 / 节点漂移 | P50 vs P99 Step Time 差距 |
| **扩展效率骤降** | 全局同步开销 | AllReduce BW vs 理论线性值 |
| **TTFT 高 + TPOT 正常** | Prefill 瓶颈 | Prefill Throughput / KV Cache 容量 |
| **TTFT 正常 + TPOT 抖动大** | KV Cache miss / 网络拥塞 | P99 vs P50 TPOT + ECN Marking Rate |
| **TPOT 随时间上升** | KV Cache 容量不足 / 碎片 | KV Cache 命中率 + 显存碎片率 |
| **训练 Goodput 差** | 故障频繁 / 检查点开销大 | MTTI / MTTR + ckpt_overhead |
| **QPS 低 + 延迟不稳定** | 并发调度算法低效 | Dynamic Batching 效率 / Continuous Batching 开关对比 |
| **All-to-All 性能差** | MoE 通信拥塞 | Outcast Timeout + A2A BW |
| **Checkpoint 耗时异常高** | 存储带宽不足 / 网络拥塞 | Checkpoint Write BW vs 并行 FS 理论带宽 |
| **Latency ≥ 理论极限** | 系统漂移 / 散热降频 | 实际 GPU clock vs 理论 clock |

---

> **注意：** 本文档独立覆盖所有常用指标定义与测量方法，不依赖知识库内其他文档。若需深入了解超节点四网架构级性能评估方法论、网络拓扑选择、或延迟分析框架，可查阅同类目录下的配套文档。

---

## 📝 修订记录

| 日期 | 操作 | 说明 |
|:-----|:-----|:------|
| 2026-06-29 | 创建 | 超节点 AI 训练与推理性能指标手册 v1.0，独立覆盖 8 章 50+ 指标 |
| 2026-06-29 | 新增 | §4.7 KV Cache 共享存储评估与测试方案（9 子节：评估维度/容量/带宽/延迟/一致性/可靠性/综合流程/工具链/业界基线）v1.1 |
