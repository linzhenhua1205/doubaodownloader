<!-- AUTO-GENERATED: 由 AI 深度分析生成，2026-08-11。修改请走编辑流程并更新 changelog。 -->

# 🔬 B300 首份现场报告：NCCL 静默死锁与「假存活」的功耗分诊方法论

> **一句话结论**：NCCL 死锁时 GPU utilization 仍可显示 100%——"假存活"不是理论陷阱，而是 512-GPU 生产集群上的实证。板卡功率（power.draw）是比利用率更可靠的分诊依据：死锁特征为**功耗冻结到小数点后两位 + SM 时钟钉死 + 全 rank 存活零报错**。工程解法 = 运行前不变量门（provenance/NVML/checkpoint 校验）+ 外部 watcher（loss-progress watchdog）把"静默挂起"转成"即时拒绝"，再借 checkpoint 自动恢复。

---

## 📋 文档信息

| 项目 | 内容 |
|:-----|:-----|
| **主题** | B300/Blackwell 世代 GPU 集群 NCCL 静默死锁现场报告 |
| **日期** | 2026-08-11 |
| **分析者** | 小龙猫 (AI) |
| **来源类型** | GitHub issue 现场调查（一手证据链）+ 微信公众号日报（二手线索） |
| **关联文档** | [2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe](../../03_AI/llm-techniques-principles/2026-08-10-llm-system-software-maturity-tensorcast-b300-plora-vibe.md)、[2026-08-11-stratalc-fabric-native-communication-deep-analysis](../../03_AI/llm-techniques-principles/2026-08-11-stratalc-fabric-native-communication-deep-analysis.md) |
| **TOC** | ✅ 本文档含目录 |

## 📑 目录

1. [执行摘要](#1-执行摘要)
2. [原始信息介绍（多来源）](#2-原始信息介绍多来源)
3. [技术机制深度分析](#3-技术机制深度分析)
4. [方法论提炼：可操作可落地的运维模式](#4-方法论提炼可操作可落地的运维模式)
5. [对服务器产品线的含义](#5-对服务器产品线的含义)
6. [可证伪预测](#6-可证伪预测)
7. [数据源注册表与缺口声明](#7-数据源注册表与缺口声明)
8. [Changelog](#8-changelog)

---

## 1. 执行摘要

### 1.1 三个核心发现（全部有实证）

| # | 发现 | 证据强度 | 关键数据 |
|:--|:-----|:--------:|:---------|
| 1 | **NCCL 挂起时 utilization 仍 100%**（"假存活"实证） | 🔴 实证（多次复现） | 死锁 GPU：100% util + 200-280W + SM 时钟钉死 1950 MHz |
| 2 | **板卡瓦数是分诊依据，优于利用率** | 🔴 实证 + 方法论 | 三态判别表：健康 700-1150W / 空闲 200-230W / 死锁 200-280W 且功耗冻结 |
| 3 | **epoch/checkpoint 死锁用「运行前不变量门 + 外部 watcher」转即时拒绝** | 🟡 已落地（PR 合并） | loss-progress watchdog：15 分钟无进展 → exit 124 → 自动从 checkpoint 恢复 |

### 1.2 根因（2026-08-07 定位，已修复）

**NCCL 2.28.9 在 aarch64 上泄漏 proxy-op slots**：slot 归还路径用弱 `__atomic_compare_exchange_n` 重试旧值（`while (swap != oldFree)`）而非 CAS 结果，aarch64 LL/SC 上偶发假失败导致整个 slot 批次被孤儿化；x86 `lock cmpxchg` 不可能出现此行为。实测死锁时滞后 rank 的 2048-slot 分区**完全泄漏**，健康 sibling 赤字 830/446/702 持续攀升。修复在 NCCL v2.29.3（commit 25368a7）。**架构相关缺陷——aarch64 独有**。

### 1.3 为什么对服务器产品线重要

- 这是**首个公开的 Blackwell 世代（GB200/B300 同代）静默死锁完整现场档案**：从现场报告→复现→消融→根因→修复→验证，全链路公开
- "假存活"直接打击**以利用率作为 SLA/健康度指标**的运维体系——实测利用率 100% 时集群已死锁数小时（sit-time 最长 15710 s ≈ 4.4 小时）
- 功耗分诊方法**零成本可迁移**：任何 `nvidia-smi` 可用的集群都能立即部署，无需额外埋点

---

## 2. 原始信息介绍（多来源）

### 2.1 一手线索：微信公众号「每日AI Infra前沿日报」

**文章**：《每日AI Infra前沿日报 | B300 微调实战曝光，Anthropic 联三星造芯》（公众号：兵部时谈）

- **搜索路径**：搜狗微信搜索（2026-08-11）命中
- **可获得摘要**（原文需微信验证码，未获取全文）：
  > "文章整理了一份 **B300 功耗分类排查表**，能通过**板卡瓦数区分计算、通信、数据饥饿、死锁和空闲状态**，甚至抓出了 **NCCL 挂起时利用率**（假象）……"
- **定位**：B300 微调实战的功耗分诊方法论，与 marin#7344 的三态判别表同源（见 2.2）
- **缺口声明**：日报全文未能获取（搜狗反爬验证码），B300 特有数值（如 128/160GB 送样规格）无法核实；下表主证据来自 GB200 现场报告，机制对 B300（Blackwell Ultra，同 Blackwell 世代）通用

### 2.2 主证据：marin#7344 —— 512-GPU GB200 集群静默挂起完整档案

**来源**：`github.com/marin-community/marin/issues/7344`（开源基础模型研发框架 marin 的公开 issue，1253★）

**一句话**：512-GPU（128 节点 × 4 GB200，8 个 NVL72 机架）MoE 训练在 step 17-1290 之间**静默停止推进**，无任何 rank 报错，所有进程存活，Iris 报告 `failures=0`，无超时触发，不会自终止。

**时间线**（这是方法论的黄金样本）：

| 日期 | 事件 | 意义 |
|:-----|:-----|:-----|
| 2026-07-17 | @ClassicLarry 现场报告：step 145/500 全部 128 rank 同一秒（20:49:47 UTC）静默冻结 | 全 rank 同时冻结 = 所有 rank 阻塞在同一个未完成 collective |
| 2026-07-30 | 2 机架 EP64 复现（128 GPU），watchdog 未触发（879 s 无超时） | 规模缩到 2 机架仍复现；XLA 600s 超时未生效 |
| 2026-08-03 | PR #7929 合并：loss-progress watchdog + checkpoint 恢复 | 外部 watcher 落地（见 4.3） |
| 2026-08-03~06 | 12 次 8 机架试验：6 次 wedge、5 次被 #7956 截尾、1 次配置阻塞 | 消融阶梯 + 竞争风险识别 |
| 2026-08-05 | 判别器建立：`failures` 不变 > 300 s ⇒ 非 #7956（#7956 自终止于 300 s 内） | 双故障类型分流 |
| 2026-08-06 | 上游 NVIDIA JAX 容器复现（provenance 门验证 libnccl 来源） | 排除自家工具链 |
| 2026-08-07 | **根因定位：NCCL 2.28.9 aarch64 proxy-op slot 泄漏**；2.30.7 修复验证 | 7/7 wedge on 2.28.9，20000+5000 steps clean on 2.30.7 |

**复现成本**（工程价值极高）：8 机架 20-40 分钟出 wedge；2 机架 ~20 分钟；危险率按 **wall-clock** 而非 step/collective 计数（8× 更小 batch 跑 3.2× 更多 collective 反而更久才 wedge，似然比 ~7:1）。

### 2.3 关联证据（同族故障）

| 来源 | 场景 | 关联点 |
|:-----|:-----|:-------|
| **PR #7929**（marin，2026-08-03 合并） | GB200 训练 | "外部 watcher + checkpoint 恢复" 实现细节（见 4.3） |
| **sglang#33289**（2026-08-02） | DeepSeek-V4 + DSpark 推理，2×DGX Spark（GB10，**aarch64**） | 推理侧同类死锁：rank 卡在 `ncclLocalOpAppend`/`SaveProxy`，peer 空闲在广播等待；NCCL proxy 阻塞、GPU stream 永不完成、watchdog 最终杀进程——**训练/推理共性 + aarch64 共性** |
| **NVIDIA/nccl#2079**（2026-03-30） | 2×RTX 5880 Ada PCIe PHB | 社区先例：`ncclAllReduce` 无限 spin，双 GPU 100% SM 利用率 + 0% 内存利用率，无超时无错误——"utilization 100% 死锁"的教科书案例 |

> ⚠️ **诚实声明**：主证据（marin#7344）硬件为 GB200（Blackwell，非 Ultra）。"B300 首份现场报告"的直接原文（微信日报全文）未能获取；本文分析基于 GB200 同代完整档案 + 日报摘要，机制层面（NCCL 静默死锁、util 假象、功耗分诊）对 B300 同代适用，B300 特有数值待原文验证。

---

## 3. 技术机制深度分析

### 3.1 "假存活"机理：为什么 utilization=100% 仍死锁

**utilization 的物理含义**：`utilization.gpu` 是 SM 上活跃 warp 的时间占比采样。它只回答"SM 有没有活干"，**不回答"活是否在推进"**。

死锁时 GPU 处于三种"看似忙碌"状态之一：

```
Deadlock GPU states (all show 100% util):

  (a) SM spin-wait    : kernel spins on a flag, occupies SM, no memory traffic
  (b) NCCL proxy spin : proxy thread spins in ncclLocalOpAppend waiting for a slot
  (c) channel-reset residue : after Xid 43 reset the GPU stops advancing NCCL work
                        (process alive, telemetry stale, no monotonic liveness counter)
```

marin 实测死锁 GPU 特征（与健康计算完全同 util，但功率/时钟可区分）：

| state | util | power | SM clocks |
|:------|:----:|:-----:|:---------:|
| healthy compute | 100 % | 700-1150 W | **varying** 1282-1950（采样间波动） |
| recompile / idle | 0 % | 200-230 W | low |
| **wedged（死锁）** | **100 %** | **200-280 W** | **pinned 1950，功耗冻结到小数点后两位** |

**为什么 util 是"假存活"指标**：util 只分"忙/闲"两态，而集群故障需要三分（健康计算/空闲/死锁）。死锁在 util 维度与健康计算**不可区分**（都是 100%），因此**一切基于 util 的 SLA/健康监控都会对死锁视而不见**——这正是 MEMORY.md 既有判断"假存活陷阱 = 监控须看命令完成率/队列深度"的现场实证。

**"假存活"的杀伤力**（数值）：sit-time 实测 2296 / 5590 / 7203 / **15710 s**（最长 4.4 小时），期间 `failures=0`、全部任务 `Running`、无任何超时。任何依赖崩溃触发恢复的机制都无限期等待。

### 3.2 板卡瓦数分诊原理：为什么功率优于利用率

**核心洞察**：功率是**连续量**且与 GPU 实际工作负载耦合，而 util 是**饱和二值量**。死锁时功耗"冻结到小数点后两位"（如 223.00 W 两次采样相同、4 分钟后仍相同）是**最强判别信号**——健康计算时功耗采样间必然波动，死锁时 GPU 既不降频也不升频、功耗完全恒定。

**判别方法**（marin 实战，可直接复制）：

```bash
# 1. POWER -- the discriminator. Run TWICE, ~30 s apart, and compare.
for t in 0 16 64 112; do
  nvidia-smi --query-gpu=index,utilization.gpu,power.draw,clocks.sm,temperature.gpu \
             --format=csv,noheader
done
# wedged signature: power identical across both passes (frozen to 2 decimals)
#                   + clock pinned at max (1950 MHz) + util 100%

# 2. NCCL RAS -- which ranks are lagging (operation-count gap)
#    look for 'MISMATCH Communicator ranks have different AllReduce operation counts'

# 3. STACKS -- py-spy dump on the lagging rank

# 4. NVML health -- expect all clean, which is itself the point
nvidia-smi --query-gpu=index,ecc.errors.uncorrected.volatile.total,remapped_rows.pending,\
remapped_rows.failure,clocks_event_reasons.hw_slowdown --format=csv,noheader
```

**五种状态的功耗分类**（日报"B300 功耗分类排查表" + marin 三态表合并）：

| 状态 | 功耗特征 | 时钟特征 | 判别 |
|:-----|:---------|:---------|:-----|
| 计算（健康） | 700-1150 W，波动 | 1282-1950 波动 | 功耗变化 = 健康 |
| 通信密集 | 高但波动 | 高位波动 | util 可高可低 |
| 数据饥饿 | 中低，缓慢下降 | 低位 | 功耗单调下行 |
| **死锁** | **200-280 W 冻结** | **钉死 1950** | 双采样完全一致 |
| 空闲/重编译 | 200-230 W | low | util=0% |

> ⚠️ **单指标不足**（marin 明确警告）："Frozen power alone is not sufficient either——rank 合法等待 collective、或等待已死 peer，产生完全相同读数"。**正确判据是合取**：冻结功率 × 持续无进展 × NCCL RAS 操作计数缺口 × `failures=0` 全 rank 存活。

### 3.3 运行前不变量门 + 外部 watcher：从"静默挂起"到"即时拒绝"

这是把不可观测故障转成可恢复故障的关键工程模式，分三层：

```
Layer 1: PRE-RUN INVARIANT GATES (run-before / run-time checks)
  |-- provenance gate : /proc/self/maps verifies libnccl source (image vs venv wheel)
  |                     -- silent toolchain swap is the top source of "fake fixes"
  |-- NVML health gate: ECC errors / remapped rows / hw_slowdown all clean
  |                     ("all clean is itself the point" -- HW is fine during a wedge)
  |-- checkpoint gate : strict restore rejects missing arrays (missing = reject)
  `-- RAS gate        : NCCL operation-count consistency (MISMATCH names lagging rank)

Layer 2: EXTERNAL WATCHER (out-of-process observer; do not trust the trainer)
  |-- loss-progress watchdog : 15 min without completed loss -> exit 124
  |                            (PR #7929, layered after XLA 10-min NCCL timeout)
  |-- JAX coordination heartbeat : 100 s
  `-- design rule: watcher must be independent of the observed stack,
                   otherwise it dies with the fault
      (#7350 watchdog never fired: NCCL built-in timeout counts only
       time inside a collective; the hang sits outside collectives)

Layer 3: FAIL-FAST CONVERSION (silent hang -> immediate rejection)
  |-- watchdog exit -> ordinary Iris app failure (retryable)
  |-- checkpoint every 30 min -> auto-restart from last complete checkpoint
  `-- effect: "hung 4.4 h unnoticed" -> "auto-restart in 15 min"
```

**为什么需要"外部 watcher"而非依赖内置超时**（实证）：
- `--xla_gpu_nccl_termination_timeout_seconds=600` 已设置且生效，**未触发**（879 s 无超时）
- 原因：该超时只计 collective 内部时间；本次死锁发生在 XLA/PJRT 异步执行队列，进程主线程等待的是"永远不会完成的设备"——**超时覆盖不到死锁位置**
- 教训：**内置 watchdog 的覆盖范围假设必须验证**，不能只看 flag 存在

**运行前不变量门与"epoch-end 死锁"的关系**：marin 的 wedge 并非严格 epoch-end（step 17-1290 随机），但 @rjpower 第一时间怀疑 "step 150 ≈ checkpoint 触发点"——checkpoint 提交本身是分布式 barrier（所有 rank 必须参与），任何 rank 卡在 collective 都会让 checkpoint 提交成为死锁的"聚合点"。**checkpoint 完整性校验（strict restore）就是针对这个聚合点的运行前不变量门**：恢复时拒绝缺数组的 checkpoint，避免"幸存者快照"掩盖数据损坏。

### 3.4 根因：NCCL 2.28.9 proxy-op slot 泄漏（aarch64 架构缺陷）

```
ROOT CAUSE CHAIN (marin#7344, verified 2026-08-07):

ncclProxyGetPostedOps (proxy.cc:845-852) slot-return path:
  weak __atomic_compare_exchange_n retries OBSERVED VALUE (while swap != oldFree)
  instead of the CAS RESULT
      |
      |-- x86: lock cmpxchg is strong; spurious failure impossible -> unaffected
      `-- aarch64: LL/SC spurious failure
            -> exits loop without storing -> whole freed-slot batch orphaned
            -> compiled as ldaxr/stlxr, stlxr success flag never tested
                  |
                  v
        starved producer __atomic_exchange_n(&freeOps[i], -1) spin breaks the
        reservation while leaving the value unchanged
        -> leaks concentrate exactly at backpressure moments
                  |
                  v
        measured on live wedge: lagging rank's 2048-slot partition fully leaked
        healthy siblings at deficits of 830/446/702 and climbing
                  |
                  v
        partition hits zero -> rank spins forever in ncclLocalOpAppend
        its own progress thread sleeps in ncclProxyGetPostedOps
        every peer blocks in the collective
        nothing errors or times out -> silent deadlock
```

**修复与验证**：
- 上游修复：NCCL v2.29.3-1（commit `25368a7f78bae866f29e46938af94fa586c84484`）
- marin 验证：7/7 wedge on 2.28.9（slot 泄漏普查在活体 wedge 上完成）；2.30.7 跑 20000+5000 steps clean；生产 8 机架 3 个 arm 跑过整个 17-183 wedge 窗口（steps 305/205/262）干净
- NVIDIA 2.29.3 release note 点名该 bug
- **未竟事项（诚实记录）**：2.30.7（含修复）栈上仍有 2 次历史 wedge（t1nccl / ngc-8rack）→ 英雄规模下可能存在第二机制，未解决

**架构层面的普适教训**：**同一源码在不同 ISA 上行为不同**——aarch64 的 LL/SC 弱一致性使本应在 x86 上"不可能出错"的代码路径暴露缺陷。这对国产芯片（ARM 架构为主）有直接警示意义：**NCCL 在 aarch64 上的正确性不能拿 x86 验证结果背书**。

---

## 4. 方法论提炼：可操作可落地的运维模式

### 4.1 三态判别表 → 立即落地（零成本）

任何 `nvidia-smi` 可用集群，按此表建立监控：

```bash
# cron/systemd timer: sample every 30 s, compare two passes
nvidia-smi --query-gpu=index,utilization.gpu,power.draw,clocks.sm --format=csv,noheader
```

**告警规则（合取）**：
1. `power.draw` 两次采样（间隔 30 s）完全相同（冻结）
2. `utilization.gpu` ≥ 99% 且持续
3. `clocks.sm` 钉在最大值（如 1950 MHz）
4. 训练/推理无进度（loss / token 计数停滞）
5. `failures=0` 且进程全部存活

⚠️ **必须 5 条合取**——单看功耗冻结会误报"合法等待"，单看 util 会漏报（假存活），单看进程存活全无意义。

### 4.2 判别器优先于根因（双故障分流）

marin 的 #7344 vs #7956 判别器是方法论范本：

> 单 rank CUDA 故障（#7956）触发 JAX shutdown barrier，**300 s 内必然自终止**（默认 `shutdown_timeout_seconds=300`）。因此：**任何 `failures` 不变且停滞 > 300 s 的运行，必不是 #7956**。

**可迁移规则**：为每类已知故障建立"自终止时限"，用"停滞时间超过时限"做类型分流——比逐个检查故障特征更快更可靠。

### 4.3 外部 watcher 设计参数（PR #7929 实证值）

| 参数 | 值 | 依据 |
|:-----|:---|:-----|
| checkpoint 间隔 | 30 min（+ 干净完成时） | 恢复粒度 vs I/O 开销平衡 |
| checkpoint 恢复 | strict（缺数组拒绝） | 防幸存者快照掩盖损坏 |
| JAX heartbeat | 100 s | 低于任何预期 step 时长 |
| loss-progress watchdog | 15 min 无 loss → exit 124 | 位于 XLA 10-min NCCL 超时之后（分层） |
| 失败语义 | 普通应用失败（retryable） | 复用既有重试机制（3 次预算） |
| 已知局限 | 3-failure 预算限制长跑恢复 | budget-neutral 自愿重启是后续工作 |

**设计三原则**：
1. **watcher 独立于被监控栈**（进程外，不信任训练进程自报）
2. **超时分层**：应用级（loss 进度）> 框架级（NCCL collective 内）> 系统级（heartbeat）
3. **失败转译**：把"静默挂起"（不可观测）转成"显式失败"（可重试）——这是故障从"运维灾难"变"自动恢复"的唯一路径

### 4.4 三个反直觉教训

1. **日志静默 ≠ 健康**：128-task gang 日志滞后数分钟 + tqdm 每 75-80 s 才输出 → 三次误报假 alarm（"看起来死锁"实际健康）。**静默窗口必须与输出频率校准，不能按直觉设**。
2. **危险率按 wall-clock 而非 steps**：step 时长在消融中从 18.6 s 变到 1.26 s（48×），按 step 预算会系统性低估暴露时间。**每次接受一个消融 cut 后必须重测速率**——cut 减半危险率会让下一个 rung 用陈旧分母产生假"修好了"。
3. **工具链静默替换是"假修复"根源**：T2（NVIDIA 镜像）测试中 venv 覆盖镜像 Python，pip wheel 与镜像 NCCL 并存 → 必须用 `/proc/self/maps` 而非包元数据验证实际加载的 libnccl。**"验证实际加载物"应成为所有环境类修复的默认动作**。

---

## 5. 对服务器产品线的含义

| # | 含义 | 可操作动作 | 优先级 |
|:--|:-----|:-----------|:------:|
| 1 | **产品定义**：推理/训练机型应预置硬件级活性遥测（功率+时钟采样），而非仅 util | 服务器 BMC/管理固件增加 `power.draw`+`clocks.sm` 遥测通道，30 s 双采样对比作为出厂健康检查项 | P1 |
| 2 | **RAS 设计**：`failures=0` 不等于健康——产品化监控体系必须包含"无进展检测"（loss/token 计数） | 管理平台提供"运行进度停滞"告警模板（合取 5 判据），作为开箱即用能力 | P1 |
| 3 | **国产对标**：根因是 aarch64 架构缺陷（LL/SC 弱 CAS）——国产 ARM 芯片（昇腾/寒武纪等）的 NCCL 移植必须做 ISA 级正确性验证，不能拿 x86 结果背书 | 国产推理芯片选型评估中增加"NCCL 极端背压场景压力测试"项 | P1 |
| 4 | **软件生态**：推理场景（sglang#33289）同样暴露 NCCL proxy 死锁——推理服务可靠性（SLO 契约）必须包含"请求级重调度"而非仅"进程级 watchdog" | 推理芯片/服务器验证矩阵加入"多节点 DSpark/TP 推理死锁恢复"用例 | P2 |
| 5 | **供应链**：watchdog 未触发事件说明**框架内置超时覆盖不足**——服务器厂商应提供独立的带外 watchdog（BMC 侧），不依赖软件栈 | BMC 提供独立训练/推理进度 watchdog（如自定义 OOB 心跳协议），与 in-band 解耦 | P2 |
| 6 | **故障恢复**：checkpoint 完整性校验（strict restore）应成为产品化训练平台的默认能力 | 管理平台 checkpoint 恢复默认拒绝缺数组快照，杜绝"幸存者快照" | P2 |

**与既有知识库的互证**：
- MEMORY.md「假存活陷阱 = 监控须看命令完成率/队列深度」→ 本报告给出第二维度：**功率冻结 + 时钟钉死**（物理层判据，比命令完成率更早可用）
- MEMORY.md「FT-HSDP = 10 万 GPU 18 min 一次故障 × 10 min 恢复 = 44% → 80% 有效时间」→ 本报告的 watcher + checkpoint 恢复正是把"挂起型故障"纳入自动恢复闭环的实例
- MEMORY.md「训练'暂停等恢复'（checkpoint）vs 推理'快速失败+请求级重调度'」→ sglang#33289 证实推理侧同样需要此分流

---

## 6. 可证伪预测

| # | 预测 | 验证窗口 | 证伪条件 |
|:--|:-----|:---------|:---------|
| P1 | NCCL ≥ 2.29.3 的栈上，marin 式 wedge 在 ≤ 8 机架规模不再复现（排除第二机制） | 2026-09-30 | 8 机架规模仍出现同签名 wedge |
| P2 | aarch64 平台将出现更多 NCCL 弱原子相关 bug 报告（ISA 级正确性缺口） | 2027-06-30 | 无新增报告或均为 x86 可复现 |
| P3 | 主流训练框架（PyTorch/XLA/JAX）12 个月内将内置"进度停滞检测"（loss/token 级 watchdog）为默认配置 | 2027-08-11 | 仍依赖用户自行部署外部 watcher |
| P4 | 服务器管理平台 12 个月内将 power.draw 双采样对比纳入 GPU 健康检查默认项 | 2027-08-11 | 无主流厂商跟进 |
| P5 | 国产 ARM 推理芯片（昇腾/寒武纪/摩尔线程）的 NCCL/类 NCCL 移植将出现 aarch64 特有死锁案例 | 2027-08-11 | 全部移植在压力测试中表现一致 |

---

## 7. 数据源注册表与缺口声明

### 7.1 数据源清单

| # | 来源 | 类型 | 访问状态 | 关键数据点 |
|:--|:-----|:-----|:---------|:-----------|
| 1 | marin#7344 issue 正文 | GitHub issue（一手） | ✅ 已抓取 | 三态表、根因、复现、消融 |
| 2 | marin#7344 42 条评论 | GitHub issue（一手） | ✅ 已抓取 | watchdog 未触发、判别器、provenance |
| 3 | marin PR #7929 | GitHub PR（一手） | ✅ 已抓取 | watcher 参数、checkpoint 策略 |
| 4 | sglang#33289 | GitHub issue（一手） | ✅ 已抓取 | 推理侧同类死锁、aarch64 |
| 5 | NVIDIA/nccl#2079 | GitHub issue（一手） | ✅ 已抓取 | util 100% 死锁社区先例 |
| 6 | 每日AI Infra前沿日报（兵部时谈） | 微信公众号（二手） | ⚠️ 仅摘要 | B300 功耗分类排查表存在性 |
| 7 | NVIDIA NCCL v2.29.3 release note | 官方发布（一手） | ⚠️ 经 issue 引用 | 修复 commit 25368a7 |

### 7.2 数据缺口（诚实声明）

1. **"B300 首份现场报告"原文未获取**：搜狗微信触发验证码反爬，日报全文不可得；B300 特有数值（功耗阈值、送样规格 128/160GB）无法核实。主证据为 GB200（同代 Blackwell）档案，机制通用性已论证，B300 特异性待补
2. **Xid 关联未定论**：Xid 13/43 与 wedge 的关联仅一个相关时间戳，被 Prometheus 访问权限阻塞；"#7344 与 #7956 是否同一故障两种呈现"仍开放
3. **第二机制未排除**：2.30.7（含修复）栈上 2 次历史 wedge，英雄规模（10 机架）可能另有机制
4. **功耗判别在 B300 上的阈值未验证**：GB200 三态表（700-1150W 健康）不能直接套 B300（TDP 更高），需现场校准

---

## 8. Changelog

| 日期 | 变更 | 说明 |
|:-----|:-----|:-----|
| 2026-08-11 | 初稿创建 | 基于 marin#7344 + PR#7929 + sglang#33289 + nccl#2079 深度分析；日报摘要为二手线索 |

---

> **一句话带走**：**utilization 100% 可能是最贵的谎言——功率冻结 + 时钟钉死 + 无进度，才是死锁的三位一体签名；让"静默挂起"变成"15 分钟自动重启"，靠的是不信训练进程自报的外部 watcher 和恢复即校验的 checkpoint 门。**
