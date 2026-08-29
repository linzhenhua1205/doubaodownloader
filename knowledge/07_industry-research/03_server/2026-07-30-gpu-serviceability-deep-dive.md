# 🖥️ GPU 可服务性深度规格：安装·供电·散热·诊断·更换·固件

> **概要**: 基于可服务性规格说明书 §1.4 (SVC-GPU-001~010) 的深度展开，覆盖GPU从物理安装到远程诊断的全生命周期可服务性设计，面向AI训练/推理场景的大型互联网数据中心。
>
> **关键词**: GPU Serviceability · GPU诊断 · GPU热插拔 · HBM ECC · NVLink诊断 · GPU供电设计 · AI服务器运维
>
> **适用范围**: AI服务器/GPU服务器 中GPU子系统的可服务性设计
>
> **目标读者**: 硬件架构师·结构工程师·BMC固件工程师·AI系统运维
>
> **关联文档**: [GPU故障检测全景分析](../../02_rd/01_product/00_hardware/05_ras/2026-07-23-gpu-fault-detection-comprehensive-analysis.md) · [可服务性规格总表](2026-07-30-server-serviceability-specification.md)

---

## 📑 目录

- [§0 执行摘要](#§0-执行摘要)
- [§1 GPU物理安装与结构可服务性](#§1-gpu物理安装与结构可服务性)
  - [1.1 GPU基座与固定方式](#11-gpu基座与固定方式)
  - [1.2 GPU供电连接器设计](#12-gpu供电连接器设计)
  - [1.3 GPU辅助支架与抗震设计](#13-gpu辅助支架与抗震设计)
  - [1.4 GPU安装/更换操作流程](#14-gpu安装更换操作流程)
- [§2 GPU散热可服务性](#§2-gpu散热可服务性)
  - [2.1 GPU散热器免工具设计](#21-gpu散热器免工具设计)
  - [2.2 液冷GPU可服务性](#22-液冷gpu可服务性)
  - [2.3 GPU热传感器独立监控](#23-gpu热传感器独立监控)
  - [2.4 GPU导热介质管理](#24-gpu导热介质管理)
- [§3 GPU电源与功耗管理](#§3-gpu电源与功耗管理)
  - [3.1 GPU供电链路监控](#31-gpu供电链路监控)
  - [3.2 GPU功耗遥测](#32-gpu功耗遥测)
  - [3.3 GPU电源异常保护与告警](#33-gpu电源异常保护与告警)
- [§4 GPU诊断与故障定位](#§4-gpu诊断与故障定位)
  - [4.1 PCIe AER错误诊断](#41-pcie-aer错误诊断)
  - [4.2 GPU XID/SXID错误诊断](#42-gpu-xidsxid错误诊断)
  - [4.3 GPU显存ECC诊断](#43-gpu显存ecc诊断)
  - [4.4 NVLink互联诊断](#44-nvlink互联诊断)
  - [4.4 GPU温度/功耗异常诊断](#44-gpu温度功耗异常诊断)
  - [4.5 GPU一致性测试与健康检查](#45-gpu一致性测试与健康检查)
- [§5 GPU固件管理](#§5-gpu固件管理)
  - [5.1 GPU VBIOS管理](#51-gpu-vbios管理)
  - [5.2 GPU FW批量更新](#52-gpu-fw批量更新)
  - [5.3 GPU FW版本兼容性管理](#53-gpu-fw版本兼容性管理)
- [§6 GPU远程运维场景](#§6-gpu远程运维场景)
  - [6.1 GPU健康巡检](#61-gpu健康巡检)
  - [6.2 GPU故障远程诊断](#62-gpu故障远程诊断)
  - [6.3 GPU故障备件更换](#63-gpu故障备件更换)
  - [6.4 GPU固件批量升级](#64-gpu固件批量升级)
- [§7 GPU可服务性验收](#§7-gpu可服务性验收)
  - [7.1 GPU可服务性规格总表](#71-gpu可服务性规格总表)
  - [7.2 验收测试用例](#72-验收测试用例)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## §0 执行摘要

### 0.1 GPU可服务性的特殊性

GPU（特别是AI训练用GPU，如NVIDIA H100/B200/Blackwell Ultra、AMD MI300X/MI400X）在可服务性设计上有**四个显著区别于通用部件**的特征：

| 特征 | 特殊性 | 可服务性影响 |
|:-----|:-------|:-------------|
| **高功耗** | 单GPU功耗300-1200W | 供电链路复杂(12VHPWR×多路)·散热必须液冷·操作安全风险 |
| **高价值** | GPU占服务器BOM 60-80% | 备件策略保守·维修避免报废·更换需极高操作标准 |
| **精细化互联** | NVLink 5/IF4链路速度>900GB/s | 链路对齐极其敏感·少量偏差即降速·拆卸/安装影响互联 |
| **HBM集成** | HBM与GPU核心一体化封装 | 显存故障=整卡报废·ECC不可关闭·故障模式特殊 |

### 0.2 核心设计哲学：三原则

| 原则 | 内涵 | 设计决策示例 |
|:-----|:------|:-------------|
| **1. 接触可靠性 > 拆装速度** | GPU信号完整性对连接器接触极度敏感，不可为了快牺牲接触质量 | 辅助固定支架必须有扭矩控制·供电连接器必须锁扣到位检测 |
| **2. 远程诊断 > 现场操作** | GPU故障诊断链路极长（芯片→板级→PCIe→OS→训练框架），现场难以诊断 | BMC必须完整读回XID/ECC/NVLink/功耗四维数据 |
| **3. 预防 > 修复** | 单GPU故障即可导致多GPU训练任务中断 | 显存CE计数趋势预警·NVLink退化提前发现·温度偏移早期告警 |

### 0.3 与其他文档的差异化定位

| 已有文档 | 本文档 |
|:---------|:-------|
| GPU故障检测全景分析 | 聚焦检测机制→聚焦**可服务性设计规格和运维操作** |
| 芯片级RAS实现 | 芯片内部RAS硬件→**系统级可服务性设计** |
| 超节点系统可靠性 | 集群/系统级可靠性→**单GPU物理可服务性+BMC级运维** |

---

## §1 GPU物理安装与结构可服务性

### 1.1 GPU基座与固定方式

**设计目标**: 单GPU更换时间(MTTR) ≤ 15分钟（含诊断、确认、物理更换、验证全过程）

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 | 执行部门 |
|:----:|:-------|:---------|:--------:|:---------|:---------|
| GPU-PHY-001 | GPU基座快拆 | GPU基座(底座)采用按压式卡扣/旋转锁扣固定，徒手操作无需工具 | MUST | DT(基座拆卸)<30秒 | 结构设计 |
| GPU-PHY-002 | GPU安装导向 | GPU基座/插槽有物理导向槽，保证GPU插入方向唯一 | MUST | 错误方向物理不可插入 | 结构设计 |
| GPU-PHY-003 | GPU锁紧指示 | GPU锁紧到位有清晰指示（卡嗒声/色标对齐/触觉反馈） | MUST | 到位标识清晰可辨，色标偏差<0.5mm | 结构设计 |
| GPU-PHY-004 | GPU接触确认 | 基座与GPU金手指接触到位后有电气确认信号（BMC可读Presence） | MUST | Presence检测准确率100% | 硬件+BMC |
| GPU-PHY-005 | 高密度GPU排列间距 | 8路GPU（如4U 8-GPU）相邻GPU间距满足徒手操作空间 | MUST | 相邻GPU间距≥15mm（手指可伸入） | 结构设计 |
| GPU-PHY-006 | GPU金手指防尘 | 服务器未安装GPU的槽位有防尘盖 | SHOULD | 防尘盖材料不产生碎屑/静电 | 结构设计 |
| GPU-PHY-007 | GPU金手指保护 | GPU金手指在运输/存储中有保护盖 | MUST | 保护盖适配金手指形状不脱落 | 结构设计 |

### 1.2 GPU供电连接器设计

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 | 执行部门 |
|:----:|:-------|:---------|:--------:|:---------|:---------|
| GPU-PWR-001 | 12VHPWR连接器品质 | 12VHPWR连接器符合PCIe CEM 5.1/6.0规范，额定≥600W | MUST | 通过IEC 60529 IP2X防触电测试 | 硬件设计 |
| GPU-PWR-002 | 供电连接器锁扣到位检测 | 12VHPWR插头锁扣到位后有电气信号返回BMC | MUST | 锁扣未到位时BMC告警 | 硬件+BMC |
| GPU-PWR-003 | 供电线缆盲插导向 | GPU供电线缆连接器有物理导向/防呆，盲插正确率≥99.5% | MUST | 错误方向不可插入 | 结构设计 |
| GPU-PWR-004 | 供电连接器独立 | 每GPU独立供电连接器，不可并联共享 | MUST | GPU故障不导致其他GPU掉电 | 硬件设计 |
| GPU-PWR-005 | 供电连接器更换 | 供电线缆为可更换FRU，现场备件可替换 | MUST | 供电线缆DT<2分钟 | 结构设计 |
| GPU-PWR-006 | 供电连接器温度监控 | 12VHPWR连接器处有温度传感器(NTC)监测过热 | MUST | 温度>105°C触发告警 | 硬件+BMC |
| GPU-PWR-007 | 供电连接器寿命计数 | 12VHPWR插拔次数BMC可记录，>30次预警更换 | SHOULD | 记录精度±1次 | BMC固件 |

**12VHPWR连接器的历史教训**: 2023-2024年间GPU 12VHPWR连接器熔化事故频发，根本原因在于插头未完全入位导致接触电阻增大→局部高温→熔化。因此供电连接器**锁扣到位检测**和**温度监控**是强制项，不可省略。

### 1.3 GPU辅助支架与抗震设计

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 | 执行部门 |
|:----:|:-------|:---------|:--------:|:---------|:---------|
| GPU-BRK-001 | GPU辅助固定支架 | 4U及以上GPU服务器配备辅助固定支架，防止运输/震动导致GPU接触不良 | MUST | 支架可承受≥10G震动冲击而不松动 | 结构设计 |
| GPU-BRK-002 | 支架免工具 | GPU辅助支架采用免工具拆装 | MUST | DT<30秒 | 结构设计 |
| GPU-BRK-003 | 支架扭矩控制 | 支架螺丝（如需要）有扭矩限值标记/自限扭矩设计 | SHOULD | 扭矩值在螺丝旁丝印或自动限扭 | 结构设计 |
| GPU-BRK-004 | GPU减震垫 | GPU基座与机箱支撑之间配备减震垫 | SHOULD | 减震频率匹配机箱共振频率 | 结构设计 |
| GPU-BRK-005 | 运输锁扣 | 服务器运输时有GPU运输锁扣，防止基座松动 | MUST | 运输锁扣有醒目的"移除"标记 | 结构设计 |

### 1.4 GPU安装/更换操作流程

**标准8-GPU服务器更换单颗GPU的操作流程**:

| 步骤 | 操作 | 预期时间 | 依赖规格 |
|:-----|:-----|:--------:|:---------|
| S1 | BMC确认故障GPU槽位 | 1min | GPU-PCI-003(GPU PCIe AER) |
| S2 | 通知AI任务停止/排空 | 5min | (集群调度) |
| S3 | 关机（Graceful Shutdown） | 1min | BMC远程关机 |
| S4 | 服务器从机柜拉出至维护位 | 1min | 滑轨 |
| S5 | 断开故障GPU供电线缆 | 30s | GPU-PWR-002/003 |
| S6 | 松故障GPU辅助支架 | 30s | GPU-BRK-001/002 |
| S7 | 松GPU基座卡扣并取出GPU | 30s | GPU-PHY-001/003 |
| S8 | 将新GPU装入基座到位 | 30s | GPU-PHY-002/003 |
| S9 | 装回辅助支架 | 30s | GPU-BRK-001/002 |
| S10 | 接回供电线缆（确认锁扣到位） | 30s | GPU-PWR-002 |
| S11 | 推回机柜 | 30s | - |
| S12 | 上电 | 1min | BMC远程 |
| S13 | POST确认GPU识别 | 2min | GPU-PCI-006 |
| S14 | 运行GPU健康检查（GPU_Health_Check） | 3min | GPU-DIAG-010 |
| S15 | 恢复AI训练任务 | 2min | (集群调度) |
| | **总计MTTR** | **~19min** | |

**移动维护位（Maintenance Position）要求**: 导轨须支持服务器拉出至维护位后稳定停留（不晃动），维护位的深度须满足：

- 4U服务器: GPU可完全从机箱取出，且PCIe保持连接（可选带电维护）
- 1U服务器: 上盖板可打开且GPU可更换

---

## §2 GPU散热可服务性

### 2.1 GPU散热器免工具设计

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 | 执行部门 |
|:----:|:-------|:---------|:--------:|:---------|:---------|
| GPU-THM-001 | GPU散热器快拆 | GPU散热器采用按压锁扣/旋转卡扣固定，无需螺丝 | MUST | DT<30秒 | 结构/散热 |
| GPU-THM-002 | 散热器防呆定向 | 散热器只能以一个方向安装，错误方向不可装配 | MUST | 错误安装不可行 | 结构设计 |
| GPU-THM-003 | 散热器接触压力自平衡 | 散热器安装压力自平衡，避免单侧过压/欠压 | SHOULD | 弹簧负载保证压力均匀性>90% | 散热团队 |
| GPU-THM-004 | 散热器热管防损伤 | 热管外露部分有保护套/骨架，避免运输/维护中磕碰 | SHOULD | 热管无裸露>5mm长度 | 结构设计 |
| GPU-THM-005 | 风冷GPU风道不干扰 | 更换GPU时导风罩/风扇不互相阻塞，恢复后风道正常 | MUST | 更换后风道阻力变化<5% | 结构/散热 |

### 2.2 液冷GPU可服务性

液冷GPU（冷板式液冷）的可服务性设计远复杂于风冷：

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-LC-001 | QD快接头 | 液冷GPU使用快接头(Quick Disconnect)连接冷却液管，断开水路自动密封 | MUST | 断开时泄漏量<0.1mL |
| GPU-LC-002 | QD寿命 | QD快接头插拔寿命≥100次 | MUST | 100次后密封性能不变 |
| GPU-LC-003 | 液体颜色区分 | 供液/回液管使用不同颜色快接头（红/蓝或红/白） | MUST | 颜色符合行业惯例 |
| GPU-LC-004 | 漏液检测 | GPU冷板下方有漏液检测绳/传感器，报警至BMC | MUST | 漏液检测响应<10秒 |
| GPU-LC-005 | 冷板免工具固定 | GPU冷板采用弹簧柱/卡扣固定，螺丝最少化 | SHOULD | DT<1分钟 |
| GPU-LC-006 | 液冷排空/填充 | 更换GPU前可远程(通过BMC/液冷CDU)排空该路冷却液 | SHOULD | 排空时间<5分钟 |
| GPU-LC-007 | 液冷GPU湿度监控 | GPU周围有湿度传感器监测冷凝风险 | SHOULD | 露点温度+2°C触发警告 |
| GPU-LC-008 | 液冷更换培训 | 液冷GPU更换需要专门培训，标识在机箱面板 | MUST | 面板有"液冷维护需培训"标记 |
| GPU-LC-009 | QD操作空间 | QD快接头周围≥50mm操作空间，可戴手套单手操作 | MUST | 盲操作连接确认有触觉反馈 |
| GPU-LC-010 | 冷板温度监控 | 冷板入口/出口各有温度传感器 | MUST | 温差>10°C触发告警 |

**液冷GPU更换时间估算**: 冷板式液冷GPU的MTTR期望值约30-45分钟（vs 风冷15-20分钟），主要增加在：QD接头操作+排空/填充水路+漏液检测确认。

### 2.3 GPU热传感器独立监控

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-TPS-001 | GPU核心温度 | GPU Die温度可读回BMC，精度±2°C，刷新率<5秒 | MUST | 与NVIDIA-smi读数偏差<2°C |
| GPU-TPS-002 | GPU显存(HBM)温度 | HBM温度独立传感器，精度±2°C | MUST | HBM温度与核心温度独立上报 |
| GPU-TPS-003 | GPU热点温度 | GPU Hot Spot温度读取（Die上最高温度点） | MUST | 热点温度可区分于核心温度 |
| GPU-TPS-004 | GPU VRM温度 | GPU VRMOSFET/电感温度传感器 | MUST | 独立于GPU芯片温度 |
| GPU-TPS-005 | GPU PCB温度 | GPU板卡PCB温度传感器 | MUST | 位置在GPU背面/供电区域 |
| GPU-TPS-006 | GPU环境进风温度 | GPU模组前方进风温度 | SHOULD | 可辅助判断液冷/风冷效率 |
| GPU-TPS-007 | 温度偏移检测 | BMC记录GPU各温度基线，持续偏移>5°C预警 | SHOULD | 基线自动学习或人工标定 |

### 2.4 GPU导热介质管理

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-TIM-001 | 导热介质免清洁 | 采用相变材料(PCM)/导热垫片替代导热硅脂 | MUST | 不残留、不可回用 |
| GPU-TIM-002 | 相变材料一次性 | 相变材料一次性使用，更换GPU时自动附着在旧散热器上带离 | MUST | 新GPU与新PCM同时安装，无需额外清洁 |
| GPU-TIM-003 | 导热垫片预贴 | 导热垫片预贴在散热器上，现场无需单独粘贴 | SHOULD | 垫片位置精度±1mm |
| GPU-TIM-004 | 导热垫片厚度公差 | 导热垫片厚度公差≤0.1mm | MUST | 确保不同GPU高度差异下接触良好 |

---

## §3 GPU电源与功耗管理

### 3.1 GPU供电链路监控

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-PWR-M-001 | GPU实时功耗读取 | BMC可读每GPU瞬时功耗(1Hz采样) | MUST | 精度±5% |
| GPU-PWR-M-002 | GPU平均功耗统计 | BMC可读每GPU过去1min/5min/30min平均功耗 | MUST | 统计周期可配置 |
| GPU-PWR-M-003 | GPU供电电压监控 | GPU核心电压/辅助电压可读 | MUST | 精度±2% |
| GPU-PWR-M-004 | GPU供电电流监控 | GPU供电电流可读 | MUST | 精度±3% |
| GPU-PWR-M-005 | GPU供电效率 | GPU功耗/输入功耗比值(供电效率) | SHOULD | 精度±3% |
| GPU-PWR-M-006 | GPU功耗限制 | 支持通过BMC设置GPU功耗上限(TDP%) | SHOULD | TDP限制与nvidia-smi -pl一致 |

### 3.2 GPU功耗遥测路径

```text
GPU芯片内部传感器 (NVML/DCGM)
        |
        +---> GPU驱动 -> nvidia-smi/dcgmi (OS内的带内路径)
        |
        +---> I2C/SMBus -> BMC (带外路径，主用诊断路径)
        |       |
        |       +---> Redfish Chassis/PowerSubsystem
        |       +---> IPMI Sensor (功耗类)
        |       +---> 本地缓存 -> 告警/趋势分析
        |
        +---> PMBus (供电模组) -> BMC (物理功耗测量)
```

**双路径设计原则**:

- 带内路径(NVML)用于性能分析和训练优化
- 带外路径(Redfish/IPMI)用于运维诊断和告警，主机死机时仍可用
- 两路径读数偏差应<3%（若偏差大→告警，可能供电链路异常）

### 3.3 GPU电源异常保护与告警

| 告警类型 | 触发条件 | 动作 | 严重级别 |
|:---------|:---------|:-----|:--------:|
| GPU过流 | GPU电流>1.2×TDP | 立即告警+BMC记录+自动降频(如支持) | Critical |
| GPU供电电压异常 | Vcore偏差>±5%保持>5秒 | 告警+BMC记录+建议检查供电模组 | Major |
| 12VHPWR连接器过热 | 连接器温度>105°C | 立即告警+建议关机检查 | Critical |
| GPU功耗异常 | 功耗偏离基线>±30%且持续>5分钟 | 告警+建议排查 | Major |
| GPU供电丢失 | GPU供电电压=0 | 告警+BMC记录时间戳 | Critical |
| 供电效率骤降 | GPU供电效率<80% | 告警+建议更换PSU/VRM | Warning |

---

## §4 GPU诊断与故障定位

### 4.1 PCIe AER错误诊断

**PCIe AER（Advanced Error Reporting）是GPU故障的第一道防线**，大多数GPU故障首先表现为PCIe链路错误。

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-PCI-001 | PCIe AER捕获 | BMC捕获并记录所有GPU所在PCIe槽的AER错误 | MUST | Correctable/Uncorrectable/Non-Fatal/Fatal均记录 |
| GPU-PCI-002 | AER错误分类上报 | 区分Corrected(CE)/Non-Fatal/Uncorrected且按类型分类 | MUST | 分类准确率100% |
| GPU-PCI-003 | PCIe链路降级告警 | GPU PCIe链路宽度/速度降级(如x16→x8)立即告警 | MUST | 告警延迟<1min |
| GPU-PCI-004 | PCIe链路错误计数 | BMC维护每个GPU PCIe链路的累计错误计数 | MUST | 计数可清零(维护后) |
| GPU-PCI-005 | PCIe Replay计数 | PCIe链路Replay超时/重试次数可查 | MUST | Replay Rate>0.1%告警 |
| GPU-PCI-006 | GPU PCIe槽位定位 | AER错误精确映射到物理槽位(丝印编号+BMC定位) | MUST | 映射表一致性校验100% |
| GPU-PCI-007 | PCIe链路健康评分 | BMC基于链路错误/降级历史给出链路健康评分(Green/Yellow/Red) | SHOULD | 评分算法可解释 |

**PCIe AER常见错误与GPU故障关联表**:

| AER错误类型 | 可能GPU故障 | 处理建议 |
|:------------|:------------|:---------|
| Correctable Error (CE) | 链路噪声/接触轻微不良 | 监控趋势，CE Rate正常<1e-12/hour |
| Non-Fatal Uncorrectable | 链路严重退化/DRAM错误 | 准备备件，计划维护窗口 |
| Fatal Uncorrectable | GPU完全离线/PCIe总线错误 | 立即排查，大概率需要更换 |
| Replay Timeout | NVLink/PCIe链路时序问题 | 检查线缆/连接器/背板S参数 |
| Completion Timeout | GPU无响应（Hang） | 尝试GPU Reset，失败则更换 |
| Poisoned TLP | GPU向PCIe总线发送损坏数据 | 立即隔离，SDC风险极高 |

### 4.2 GPU XID/SXID错误诊断

NVIDIA GPU通过XID（GPU错误码）和SXID（NVSwitch错误码）报告GPU级错误。

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-XID-001 | XID捕获 | BMC捕获主机OS/dmesg中所有XID错误 | MUST | XID捕获率>99% |
| GPU-XID-002 | XID分类映射 | BMC内置XID→故障分类→建议操作映射表 | MUST | 覆盖≥30类XID错误码 |
| GPU-XID-003 | XID严重分级 | XID按严重度分级(INFO/WARNING/CRITICAL/FATAL) | MUST | 分级映射表可配置更新 |
| GPU-XID-004 | SXID捕获 | NVSwitch SXID错误BMC可捕获上报 | MUST | SXID捕获率>99% |
| GPU-XID-005 | XID/SXID与GPU关联 | XID/SXID错误与具体物理GPU槽位关联 | MUST | 关联准确率>99% |
| GPU-XID-006 | XID趋势分析 | BMC记录XID频率趋势，频率爆发预警 | SHOULD | 频率>基线3倍告警 |

**关键XID错误码速查表**:

| XID | 含义 | 严重度 | 典型动作 |
|:---:|:-----|:------:|:---------|
| 1 | GPU Hang | FATAL | GPU Reset→若无效→更换 |
| 13 | GPU Memory Page Fault | CRITICAL | 检查显存→更换 |
| 31 | GPU Temperature Limit | WARNING | 检查散热→降频 |
| 32 | GPU Power Limit | WARNING | 检查供电→PSU |
| 43 | GPU Stopped Processing | FATAL | GPU Reset→更换 |
| 44 | GPU Internal Error | FATAL | 整卡更换 |
| 45 | GPU Preemptive Cleanup | INFO | 训练任务被抢占(正常) |
| 48 | GPU Double Bit ECC | CRITICAL | 整卡更换 |
| 62 | GPU NVLink Error | MAJOR | NVLink降速→检查互联 |
| 63 | GPU NVLink CRC Error | MAJOR | 检查线缆/背板 |
| 64 | GPU NVLink Failure | FATAL | 整卡更换 |
| 79 | GPU is Hung | FATAL | GPU Reset→更换 |
| 94 | GPU Contained Error | CRITICAL | 计划维护 |

### 4.3 GPU显存ECC诊断

HBM显存ECC错误是GPU故障的最常见前兆（约60%的GPU故障始于HBM）。

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-ECC-001 | CE计数读取 | BMC通过NVML/DCGM/寄存器读取每GPU HBM CE计数 | MUST | 读值与nvml一致 |
| GPU-ECC-002 | UE计数读取 | BMC读取每GPU HBM UE计数 | MUST | UE>0立即告警 |
| GPU-ECC-003 | CE位置记录 | CE错误对应的HBM堆栈/地址可查询 | SHOULD | 定位到HBM stack |
| GPU-ECC-004 | CE趋势预警 | CE计数增速超过阈值告警(如>10CE/小时) | MUST | 阈值可配置 |
| GPU-ECC-005 | 显存健康评分 | BMC基于CE/UE/使用时间/工作温度综合评估显存健康度 | SHOULD | 评分分级:Good/Fair/Poor |
| GPU-ECC-006 | ECC状态查询 | 每GPU当前ECC状态(启用/禁用/支持)可查询 | MUST | Redfish查询响应<3秒 |
| GPU-ECC-007 | ECC不可逆损伤 | UE计数>0且不可清除，标记该GPU为降级状态 | MUST | 标记持久化在BMC |

**显存ECC错误诊断流程**:

```text
获取GPU ECC计数
        |
        +-- UE > 0 ? -> 立即告警(CRITICAL) -> GPU标记为降级 -> 安排更换
        |
        +-- 仅CE计数 > 0 ?
                |
                +-- CE增速 < 阈值 -> Green -> 继续监控
                |
                +-- CE增速 > 阈值 -> Yellow -> 预警 -> 计划维护
                |
                +-- CE增速 > 3×阈值 -> Red -> 紧急预警 -> 24h内更换
```

**值得注意**:

- NVIDIA Hopper/Blackwell GPU的HBM3e ECC具有**行级保持（Row-level Retention）**能力，可标记故障行而非整个页面
- 但HBM3e的"行级修复"并非无限，修复尝试超过阈值后仍须更换

### 4.4 NVLink互联诊断

AI服务器中GPU之间通过NVLink/NVSwitch互联，链路健康对训练性能至关重要。

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-NVL-001 | NVLink链路状态 | BMC读取每GPU所有NVLink链路状态(Active/Disabled/Degraded/Failed) | MUST | 查询响应<5秒 |
| GPU-NVL-002 | NVLink带宽监控 | BMC读回每NVLink链路的实际带宽利用率 | MUST | 精度±5% |
| GPU-NVL-003 | NVLink CRC错误 | 每NVLink链路的CRC错误计数可读 | MUST | 错误率>1e-15告警 |
| GPU-NVL-004 | NVLink重训练计数 | NVLink链路重训练(Retraining)次数记录 | SHOULD | 重训练>3次/天告警 |
| GPU-NVL-005 | NVSwitch状态 | NVSwitch芯片温度/功耗/链路状态BMC可读 | MUST | 与GPU同样的监控精细度 |
| GPU-NVL-006 | NVSwitch SXID错误 | NVSwitch SXID错误捕获并关联到GPU | MUST | SXID映射到受影响GPU列表 |
| GPU-NVL-007 | NVLink拓扑完整性 | BMC验证当前NVLink拓扑与预期拓扑一致 | SHOULD | 拓扑变更自动告警 |

**NVLink诊断场景**:

| 场景 | 现象 | 诊断步骤 | 根因可能 |
|:-----|:-----|:---------|:---------|
| 训练吞吐下降 | NCCL AllReduce性能降50% | 查NVLink链路x4→x2/CRC突增 | GPU/背板连接器接触不良 |
| 单GPU频繁断开 | SXID NVLink Failure | 查SXID+物理链路 | GPU板级故障→更换 |
| 跨机柜互联抖动 | 跨节点NCCL超时 | 查光纤/光模块/交换机 | 光模块故障→非GPU问题 |
| 训练Hash不一致 | SDC+NVLink错误 | 查Poisoned TLP | GPU内存损坏→更换 |

### 4.4 GPU温度/功耗异常诊断

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-TDI-001 | 温度偏差诊断 | BMC对比同机箱内所有GPU温度，偏差>10°C告警 | MUST | 温度一致性检查周期≤5min |
| GPU-TDI-002 | 温度突变诊断 | GPU温度变化率>5°C/分钟告警 | MUST | 可能散热失效或传感器故障 |
| GPU-TDI-003 | 功耗一致性诊断 | 同型号GPU功耗偏差>30%告警 | MUST | 可能供电异常或GPU故障 |
| GPU-TDI-004 | 功耗温度联合诊断 | 功耗低+温度高→散热失效；功耗高+温度高→工作正常 | SHOULD | 联合诊断准确率>90% |
| GPU-TDI-005 | 热节流检测 | 检测到GPU Thermal Throttling立即告警 | MUST | 与nvidia-smi throttle一致 |

### 4.5 GPU一致性测试与健康检查

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-DIAG-001 | 快速健康检查 | 开机后GPU快速检查(PCIe识别+链路速度+显存量)≤30秒 | MUST | 可与POST并行 |
| GPU-DIAG-002 | 标准诊断套件 | BMC提供/调用GPU标准诊断(DCGM Level 1-3) | MUST | Level 1诊断<2min |
| GPU-DIAG-003 | 显存全量测试 | 支持full显存测试(离线)，覆盖HBM全地址空间 | SHOULD | 全量测试<30min/GPU |
| GPU-DIAG-004 | NVLink连通性测试 | 验证GPU之间NVLink全部连接正常 | MUST | 全互联带宽测试<5min |
| GPU-DIAG-005 | GPU烧机测试 | 更换后自动运行GPU压力测试验证散热/供电/性能 | MUST | 压力运行≥15分钟 |
| GPU-DIAG-006 | 诊断结果持久化 | 诊断结果保存到BMC持久存储 | MUST | 保留最近50次诊断记录 |
| GPU-DIAG-007 | 诊断触发方式 | 支持BMC主动触发/Redfish API触发/OS工具触发 | MUST | 触发方式≥3种 |

**DCGM诊断等级**:

| Level | 内容 | 时间 | 用途 |
|:------|:-----|:----:|:-----|
| Level 1 | GPU基本识别+PCIe链路+NVLink链路 | <30秒 | 日常巡检 |
| Level 2 | 显存ECC+温度+功耗+性能基线 | <2min | 故障快速定位 |
| Level 3 | 显存全量+NVLink带宽+GPU压力 | <30min | 更换后验证 |
| Level 4 | 密集压力+跨节点互联+长期稳定性 | >1h | 出厂/大修后 |

---

## §5 GPU固件管理

### 5.1 GPU VBIOS管理

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-FW-001 | GPU VBIOS版本查询 | BMC可查询每GPU的VBIOS版本号+日期 | MUST | 与nvidia-smi版本一致 |
| GPU-FW-002 | GPU FW版本查询 | GPU所有固件版本(BootROM/PEX/HSS等)可查 | MUST | 版本清单完整可读 |
| GPU-FW-003 | VBIOS远程更新 | 支持通过BMC/带外更新GPU VBIOS | MUST | 更新后重启生效 |
| GPU-FW-004 | VBIOS双镜像 | GPU VBIOS双镜像，更新失败自动回退 | MUST | 回退成功率>99% |
| GPU-FW-005 | VBIOS签名验证 | 所有VBIOS更新须通过数字签名验证 | MUST | 未签名固件拒绝更新 |
| GPU-FW-006 | VBIOS回退 | 支持VBIOS回退到已知稳定版本 | MUST | 回退操作≤2步 |

### 5.2 GPU FW批量更新

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-BFU-001 | 批量更新接口 | 支持通过BMC Redfish批量更新同机型GPU固件 | MUST | 批量接口返回Task ID |
| GPU-BFU-002 | 更新不影响管理 | GPU固件更新过程中BMC管理功能不中断 | MUST | 管理接口持续可用 |
| GPU-BFU-003 | 灰度更新 | 支持按GPU槽位/节点灰度更新 | MUST | 单GPU更新不影响同节点其他GPU |
| GPU-BFU-004 | 更新进度监控 | GPU FW更新进度可查询(百分比) | MUST | 进度更新间隔<30秒 |
| GPU-BFU-005 | 更新后验证 | FW更新后自动触发GPU健康检查 | MUST | 验证失败标记并告警 |

**大规模集群GPU FW更新的关键挑战**:

- NVIDIA GPU VBIOS/FW更新时，该GPU必须停止工作（训练任务需排空）
- 万卡集群下GPU FW更新通常需要数天，需设计批量调度策略
- H100/B200的FW更新通常不中断同节点其他GPU，但有些早期型号不支持

### 5.3 GPU FW版本兼容性管理

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| GPU-COM-001 | 版本基线 | BMC内置GPU固件版本兼容性矩阵 | MUST | 矩阵覆盖GPU FW×Driver×CUDA |
| GPU-COM-002 | 版本不匹配告警 | 检测到GPU FW与驱动不匹配时告警 | MUST | 不匹配检测准确率100% |
| GPU-COM-003 | 版本一致性检查 | 同集群内GPU固件版本一致性检查 | MUST | 不一致告警 |
| GPU-COM-004 | 混合版本支持 | 支持同一节点内不同GPU FW版本共存（升级过渡期） | MUST | 过渡期不超过30天 |

---

## §6 GPU远程运维场景

### 6.1 GPU健康巡检

| 巡检项 | 检查方式 | 巡检周期 | 告警条件 |
|:-------|:---------|:--------:|:---------|
| GPU在线状态 | BMC读Presence | 5分钟 | 预期在线但不在→告警 |
| PCIe链路宽度 | BMC读PCIe config | 10分钟 | 非预期降速/降宽 |
| NVLink链路状态 | BMC读NVLink status | 5分钟 | 链路数量少于预期 |
| CE错误计数 | BMC读ECC计数器 | 30分钟 | CE增速>10/hour |
| GPU温度 | BMC读温度传感器 | 1分钟 | 核心温度>85°C |
| GPU功耗 | BMC读功耗传感器 | 1分钟 | 空载功耗>30W(异常) |
| GPU风扇转速 | BMC读Fan PWM | 5分钟 | 风扇转速异常(叶片断裂) |
| XID检查 | 检查最近XID记录 | 15分钟 | 新XID出现→分析+告警 |
| GPU时钟频率 | BMC读GPU clock | 30分钟 | 频率低于Base Clock→节流 |
| GPU供电连接器温度 | BMC读12VHPWR NTC | 5分钟 | 温度>75°C预警,>105°C紧急 |

### 6.2 GPU故障远程诊断

**场景1: GPU训练任务异常中断**

```text
1. 训练框架报NCCL Timeout/Failure
   |
2. 查GPU XID日志是否有新错误 -> 是 -> 转XID处理
   |
3. 查GPU PCIe AER -> 查链路降级 -> 查找Replay/Timeout
   |
4. 查GPU功耗/温度/BIOS -> 排除散热/供电问题
   |
5. 查NVLink/SXID -> 确定是否互联问题
   |
6. 收集GPU诊断日志 -> 上报运维平台
```

**场景2: GPU性能下降**

```text
1. NCCL AllReduce benchmark吞吐下降>20%
   |
2. 查NVLink带宽利用率 -> 部分链路降速？
   |   +-- 是 -> 查CRC/NVLink重训练 -> 排线缆背板
   |   +-- 否
   |
3. 查GPU温度 -> Thermal Throttling?
   |   +-- 是 -> 查散热
   |   +-- 否
   |
4. 查GPU功耗/频率 -> 供电限制?
   |   +-- 是 -> 查PSU/供电链路
   |   +-- 否
   |
5. 查PCIe链路 -> x16->x8降级?
   |   +-- 是 -> 查背板/连接器
   |   +-- 否 -> GPU老化->安排计划更换
```

### 6.3 GPU故障备件更换

| 操作步骤 | 远程可执行 | 现场需执行 | 涉及规格 |
|:---------|:----------:|:----------|:---------|
| 确认故障GPU | ✅ BMC诊断+日志 | - | GPU-PCI-003, GPU-XID-001 |
| 标记故障GPU | ✅ Redfish标记 | - | - |
| 排空训练任务 | ✅ 集群调度 | - | - |
| 确认备件可用 | ✅ 查询备件库存 | - | - |
| 关机 | ✅ 远程关机 | - | - |
| 物理更换 | - | ✅ 现场操作 | GPU-PHY-001~007, GPU-BRK-001~005 |
| GPU供电连接 | - | ✅ 确认锁扣到位 | GPU-PWR-002 |
| 上电 | ✅ 远程上电 | - | - |
| POST验证 | ✅ BMC确认识别 | - | GPU-PCI-006 |
| 健康检查 | ✅ 远程诊断 | - | GPU-DIAG-001~007 |
| 恢复训练 | ✅ 集群调度 | - | - |

### 6.4 GPU固件批量升级

| 步骤 | 操作 | 可服务化需求 |
|:-----|:-----|:-------------|
| 1 | 确认当前FW版本和兼容性 | BMC版本清单 |
| 2 | 规划升级批次(每批≤10%集群) | Redfish批量接口 |
| 3 | 排空第一批GPU训练任务 | 集群调度集成 |
| 4 | 单GPU更新FW | VBIOS双镜像保障安全 |
| 5 | 健康检查 | 自动触发DCGM |
| 6 | 恢复训练 | 验证通过后自动恢复 |
| 7 | 下一批次 | 灰度策略保障 |

---

## §7 GPU可服务性验收

### 7.1 GPU可服务性规格总表

| 模块 | 规格数 | MUST | SHOULD | 执行部门 |
|:-----|:------:|:----:|:------:|:---------|
| GPU物理安装 | 7 | 6 | 1 | 结构设计 |
| GPU供电连接器 | 7 | 6 | 1 | 硬件+BMC |
| GPU辅助支架 | 5 | 3 | 2 | 结构设计 |
| GPU散热器 | 5 | 3 | 2 | 结构/散热 |
| 液冷GPU | 10 | 6 | 4 | 结构/散热 |
| GPU热传感器 | 7 | 5 | 2 | 硬件+BMC |
| GPU导热介质 | 4 | 3 | 1 | 散热团队 |
| 供电链路监控 | 6 | 5 | 1 | BMC固件 |
| PCIe AER诊断 | 7 | 6 | 1 | BMC固件 |
| XID/SXID诊断 | 6 | 5 | 1 | BMC固件 |
| 显存ECC诊断 | 7 | 5 | 2 | BMC固件 |
| NVLink诊断 | 7 | 5 | 2 | BMC固件 |
| 温度功耗诊断 | 5 | 4 | 1 | BMC固件 |
| 一致性测试 | 7 | 5 | 2 | BMC固件 |
| GPU FW管理 | 6 | 5 | 1 | BMC固件 |
| 批量升级 | 5 | 4 | 1 | BMC+系统软件 |
| 版本兼容性 | 4 | 3 | 1 | BMC固件 |
| **合计** | **105** | **78(74%)** | **27(26%)** | |

### 7.2 验收测试用例

**EVT阶段 — 物理结构验证**:

| 测试项 | 测试方法 | 通过标准 | 关联规格 |
|:-------|:---------|:---------|:---------|
| GPU安装计时 | 5次安装+拆卸时间记录 | 平均DT<规定值 | GPU-PHY-001~007 |
| GPU防呆验证 | 错误方向安装尝试 | 安装成功率0% | GPU-PHY-002 |
| GPU供电插拔 | 12VHPWR插拔≥50次 | 无锁扣损坏 | GPU-PWR-001~007 |
| GPU震动测试 | 机柜震动+GPU接触测试 | 震动前后Presence不变 | GPU-BRK-001~005 |
| 液冷QD测试 | QD插拔≥100次+泄漏测试 | 泄漏量<0.1mL | GPU-LC-001~010 |
| 散热器拆装 | 散热器拆装≥20次 | 接触压力一致性>90% | GPU-THM-001~005 |
| 导热介质验证 | 温度测试 | 温度差<3°C | GPU-TIM-001~004 |

**DVT阶段 — 诊断功能验证**:

| 测试项 | 测试方法 | 通过标准 | 关联规格 |
|:-------|:---------|:---------|:---------|
| PCIe AER注入 | 故障注入工具模拟AER | BMC正确捕获+分类 | GPU-PCI-001~007 |
| XID模拟 | 注入XID错误 | BMC正确捕获+映射 | GPU-XID-001~006 |
| ECC计数验证 | 与nvidia-smi读值对比 | 偏差<1% | GPU-ECC-001~007 |
| NVLink CRC注入 | 链路错误注入 | BMC正确计数+告警 | GPU-NVL-001~007 |
| 温度诊断验证 | 加热GPU模拟过热 | 告警正确触发 | GPU-TDI-001~005 |
| GPU诊断套件 | 全量运行DCGM L1-L3 | 所有测试功能正常 | GPU-DIAG-001~007 |
| 远程固件更新 | BMC远程更新VBIOS | 更新成功+回退验证 | GPU-FW-001~006 |

---

## 参考文献

### 内部知识库

- [GPU故障检测全景分析](../../02_rd/01_product/00_hardware/05_ras/2026-07-23-gpu-fault-detection-comprehensive-analysis.md) — GPU故障检测机制全面分析
- [可服务性需求规格说明书 §1.4](2026-07-30-server-serviceability-specification.md#14-gpu与加速器卡) — GPU可服务性基础规格
- [处理器调试能力演进](../../02_rd/01_product/00_hardware/01_hw-core/2026-07-02-processor-debug-capabilities.md) — GPU芯片级调试
- [整机柜/集群故障诊断规格](../../02_rd/00_shared/05_fault-diagnosis/2026-06-29-rack-cluster-fault-diagnosis-specs.md) — 集群级诊断体系

### 厂商参考

- [1] NVIDIA: "NVIDIA DCGM User Guide" — Diagnostic and monitoring for NVIDIA GPUs
- [2] NVIDIA: "NVIDIA NVLink and NVSwitch Error Reporting" — SXID error codes
- [3] NVIDIA: "NVIDIA Blackwell RAS — Architecture and Implementation" — Blackwell RAS engine
- [4] AMD: "AMD MI300X RAS Features and Error Reporting" — RAS for AMD GPUs
- [5] Intel: "Intel Data Center GPU — Diagnostic and Monitoring Guide"

### 标准与规范

- [6] PCI-SIG: "PCI Express Base Specification 6.0" — AER and error handling
- [7] PCI-SIG: "PCIe CEM Specification 5.1/6.0" — 12VHPWR connector spec
- [8] NIST SP 800-88: "Guidelines for Media Sanitization" — GPU DRAM erasure

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:-----|:----:|:---------|
| 2026-07-30 | v1.0 | 首次创建，覆盖7章105条GPU可服务性规格 |
