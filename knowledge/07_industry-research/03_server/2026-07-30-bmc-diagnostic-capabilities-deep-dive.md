# 🔍 BMC 诊断能力深度规格：传感器·告警·日志·远程诊断·故障预测

> **概要**: 基于可服务性规格说明书 §3 的深度展开，覆盖BMC作为服务器带外"诊断大脑"的全套诊断能力设计——从传感器采集到故障预测，从当日日志到崩溃现场保存，从单机诊断到集群联动。
>
> **关键词**: BMC诊断 · 带外管理 · Redfish诊断 · IPMI · SEL · 传感器监控 · 故障预测 · 远程诊断 · OpenBMC · 服务器健康管理
>
> **适用范围**: 服务器BMC固件设计·诊断系统设计·运维平台对接
>
> **目标读者**: BMC固件架构师·固件开发·系统测试·运维开发
>
> **关联文档**: [可服务性规格总表](2026-07-30-server-serviceability-specification.md) · [调试系统设计](../../02_rd/01_product/01_software/2026-07-21-debug-system-design.md) · [运维软件市场格局](../../02_rd/03_management/2026-07-20-operations-software-market-landscape.md)

---

## 📑 目录

- [§0 执行摘要](#§0-执行摘要)
- [§1 传感器采集架构](#§1-传感器采集架构)
  - [1.1 传感器分类与覆盖](#11-传感器分类与覆盖)
  - [1.2 传感器采集参数规格](#12-传感器采集参数规格)
  - [1.3 传感器拓扑设计](#13-传感器拓扑设计)
  - [1.4 传感器数据完整性](#14-传感器数据完整性)
- [§2 告警引擎设计](#§2-告警引擎设计)
  - [2.1 告警分级与分类](#21-告警分级与分类)
  - [2.2 告警阈值管理](#22-告警阈值管理)
  - [2.3 告警策略（抑制·去重·延迟·升级）](#23-告警策略抑制去重延迟升级)
  - [2.4 告警推送机制](#24-告警推送机制)
  - [2.5 告警现场快照](#25-告警现场快照)
- [§3 日志系统设计](#§3-日志系统设计)
  - [3.1 日志分类与存储](#31-日志分类与存储)
  - [3.2 SEL系统事件日志](#32-sel系统事件日志)
  - [3.3 Debug日志系统](#33-debug日志系统)
  - [3.4 POST Code日志](#34-post-code日志)
  - [3.5 崩溃保留（Crash Preservation）](#35-崩溃保留crash-preservation)
  - [3.6 日志外发(syslog/Redfish Event)](#36-日志外发syslogredfish-event)
- [§4 远程诊断功能](#§4-远程诊断功能)
  - [4.1 远程故障定位](#41-远程故障定位)
  - [4.2 诊断套件](#42-诊断套件)
  - [4.3 KVM与SOL](#43-kvm与sol)
  - [4.4 远程BIOS诊断](#44-远程bios诊断)
  - [4.5 故障现场回放](#45-故障现场回放)
- [§5 预测性故障分析](#§5-预测性故障分析)
  - [5.1 趋势分析](#51-趋势分析)
  - [5.2 寿命预测](#52-寿命预测)
  - [5.3 异常检测](#53-异常检测)
  - [5.4 预测准确度要求](#54-预测准确度要求)
- [§6 BMC自诊断与恢复](#§6-bmc自诊断与恢复)
  - [6.1 BMC健康自检](#61-bmc健康自检)
  - [6.2 BMC固件恢复](#62-bmc固件恢复)
  - [6.3 BMC与BIOS协同诊断](#63-bmc与bios协同诊断)
- [§7 诊断接口标准化](#§7-诊断接口标准化)
  - [7.1 Redfish诊断模型](#71-redfish诊断模型)
  - [7.2 IPMI诊断扩展](#72-ipmi诊断扩展)
  - [7.3 指标导出(Prometheus)](#73-指标导出prometheus)
- [§8 BMC诊断能力验收](#§8-bmc诊断能力验收)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## §0 执行摘要

### 0.1 BMC在服务器诊断中的核心地位

BMC（基板管理控制器，Baseboard Management Controller）是服务器运维的**最后一道防线**——当OS崩溃、CPU挂死、网络不通时，BMC仍然是可访问的独立管理通道。

```text
                        +-----------------+
                        |    运维管理云     |
                        |  CMDB/Monitor/   |
                        |  Alert/Ticket    |
                        +--------+--------+
                                 |
                        +--------+--------+
                        |    Redfish      |
                        |   (RESTful)     |
                        +--------+--------+
                                 |
                        +--------+--------+    +---------------+
                        |  BMC SoC        |<---|  主机系统      |
                        |  (ARM/ARC)      |    |  (OS/KVM)     |
                        |  +-----------+   |    |               |
                        |  |诊断引擎    |   |    +---------------+
                        |  |传感器采集   |   |
                        |  |告警分析    |   |    +---------------+
                        |  |日志管理    |   |<---|  BIOS/UEFI    |
                        |  |预测分析    |   |    |  (POST Code)  |
                        |  +-----------+   |    +---------------+
                        +--------+--------+
                                 | I2C/PECI/PMBus/IPMB
                    +------------+------------+
                    |            |             |
              +-----+--+  +-----+--+   +-----+--+
              |  sensors |  | FRU    |   | PSU/Fan|
              |  (全板) |  | EEPROM |   |(PMBus) |
              +---------+  +--------+   +--------+
```

### 0.2 BMC诊断能力四层模型

| 层级 | 名称 | 能力描述 | 实时性要求 | 覆盖度 |
|:----:|:-----|:---------|:----------:|:------:|
| **L1** | 被动监控 | 传感器采集→阈值比较→告警 | <10秒 | 所有传感器 |
| **L2** | 主动诊断 | 按需/定时运行诊断套件 | <5分钟 | GPU/DIMM/PCIe/存储 |
| **L3** | 预测分析 | 趋势分析+寿命预测+异常检测 | <1天 | 关键部件(风扇/盘/GPU CE) |
| **L4** | 自愈恢复 | 看门狗+自动重启+固件回退 | <1分钟 | OS-Level故障 |

### 0.3 设计目标

| 指标 | 目标值 |
|:-----|:------|
| 传感器采集覆盖率 | ≥95%的可监控部件 |
| 告警延迟 | <30秒（告警产生→推送） |
| 故障定位准确率（到FRU粒度） | ≥95% |
| 预测提前量 | ≥72小时（风扇/盘/GPU寿命） |
| 日志完整率 | ≥99%的关键事件被记录 |
| BMC自身可用性 | 99.99%（独立于主机运行） |

---

## §1 传感器采集架构

### 1.1 传感器分类与覆盖

| 分类 | 传感器类型 | 数量参考(4U AI服务器) | 采集协议 | 精度要求 |
|:-----|:-----------|:---------------------:|:---------|:---------|
| **温度** | CPU/GPU/DIMM/PSU/VRM/CHIPSET/NVMe/Board Ambient/Inlet/Outlet | 30-50 | I2C/PECI/PMBus | ±1~2°C |
| **电压** | Vcore/Vmem/Vcc/Vaux/Vpp/P12V/P3V3/P5V/P12V_AUX | 15-25 | I2C/ADC | ±2% |
| **电流** | CPU/GPU/内存/风扇/整机输入 | 10-20 | PMBus/I2C | ±3% |
| **功耗** | 整机/CPU/GPU/内存/风扇/PSU | 10-15 | PMBus | ±3% |
| **风扇** | 转速/PWM占空比/在位检测 | 8-16 | PWM/Fan Tach | ±5% RPM |
| **电源** | PSU输入/输出/效率/温度/在位/冗余状态 | 4-6 | PMBus 1.3.1 | 按类型 |
| **存储** | SSD寿命/温度/读写量/SMART | 8-24 | NVMe-MI/SATA SES | 按类型 |
| **PCIe** | 槽位设备类型/链路速度/链路宽度/错误计数 | 10-16 | MCTP/PLDM | — |
| **液冷** | QD温度/供液温度/回液温度/泄漏检测 | 6-12 | I2C/sensor | 按类型 |

**AI服务器传感器总数预估**: 100-150个传感器/台（4U 8-GPU AI服务器）

### 1.2 传感器采集参数规格

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-SEN-001 | 传感器采样间隔 | 模拟传感器(温度/电压)采样间隔≤5秒 | MUST | 实际采样与配置偏差<10% |
| BMC-SEN-002 | 传感器刷新间隔 | 数字传感器(功耗/风扇)刷新间隔≤10秒 | MUST | — |
| BMC-SEN-003 | 传感器精度 | 温度±2°C·电压±2%·电流±3%·功耗±3% | MUST | 校准可追溯 |
| BMC-SEN-004 | 传感器范围 | 温度-10~150°C·电压0~60V·电流0~500A | MUST | 覆盖工作范围+裕量20% |
| BMC-SEN-005 | 传感器冗余 | 关键传感器(CPU温度/GPU温度)应有备份/冗余 | SHOULD | 冗余传感器一致性偏差<3% |
| BMC-SEN-006 | 传感器隔离 | 单个传感器故障不影响其他传感器采集 | MUST | 故障隔离成功率100% |
| BMC-SEN-007 | 传感器校准 | 传感器出厂校准数据存储在BMC NVRAM中 | MUST | 校准有效期≥3年 |
| BMC-SEN-008 | 传感器历史 | BMC保存每个传感器最近24小时的采样数据 | MUST | 历史数据可区间查询 |
| BMC-SEN-009 | 传感器扩展 | 支持通过I2C/SMBus动态添加新的传感器 | SHOULD | 新增传感器即插即测 |
| BMC-SEN-010 | 传感器降级采样 | BMC CPU负载>80%时自动降低采样频率 | SHOULD | 负载降低后恢复正常频率 |

### 1.3 传感器拓扑设计

```text
+------------------ 主机域 -------------------+
|                                              |
|  CPU0 PECI/hwmon    CPU1 PECI/hwmon          |
|     |                    |                    |
|     +--------+-----------+                    |
|              | I2C bus 0                     |
|              v                                |
|  +---------------------+                     |
|  |  BMC (Aspeed AST2600) |                     |
|  |  +-----------------+|                     |
|  |  |  Sensor Engine  ||                     |
|  |  |  (hardware)     ||                     |
|  |  +-----------------+|                     |
|  |  +-----------------+|                     |
|  |  |  IPMB/SMBus Ctrl ||                     |
|  |  +-----------------+|                     |
|  +---------------------+                     |
|              | I2C bus 1,2,3                 |
+--------------+--------------------------------+
|              v                               |
|  +------+ +------+ +------+ +------+        |
|  |DIMM  | |  GPU  | |  PSU  | |  Fan  |        |
|  |SPD   | |NVML/  | |PMBus  | |Tach   |        |
|  |TEMP  | |I2C    | |       | |       |        |
|  +------+ +------+ +------+ +------+        |
|                                              |
|  +------+ +------+ +----------+              |
|  |NVMe   | |  HDD  | | PCIe Slot|              |
|  |MCTP   | |  SES  | | MCTP    |              |
|  +------+ +------+ +----------+              |
+----------------------------------------------+
```

**I2C总线设计要点**:

- 不同类传感器分配到不同I2C总线，单总线故障不影响全局
- 高速传感器(温度/风扇)优选独立I2C总线
- 每个I2C总线上的设备数量≤8，避免地址冲突和总线负载
- I2C总线速率≥400kHz（快速模式），关键传感器总线支持1MHz（高速模式）

### 1.4 传感器数据完整性

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-SEN-INT-001 | 传感器有效性标记 | BMC标记每个传感器读值的有效性(Valid/Stale/Error/NaN) | MUST | 无效值不进入告警判断 |
| BMC-SEN-INT-002 | 传感器读值平滑 | 模拟传感器读值采用滑动平均(窗口=3-5次) | MUST | 尖峰噪声过滤后不影响告警 |
| BMC-SEN-INT-003 | 传感器故障检测 | 持续无效读数(>30秒)标记传感器故障 | MUST | 传感器故障≠系统故障 |
| BMC-SEN-INT-004 | 传感器数据持久化 | 关键传感器数据写入BMC持久存储 | MUST | 断电不丢失 |
| BMC-SEN-INT-005 | 传感器数据一致性 | BMC读值与其他路径(如NVML)偏差<3% | SHOULD | 偏差超限告警 |

---

## §2 告警引擎设计

### 2.1 告警分级与分类

**四级告警严重度**:

| 级别 | 名称 | 定义 | 推送方式 | 响应要求 |
|:----:|:-----|:-----|:---------|:---------|
| **Critical** | 严重 | 系统已宕机/即将宕机/数据已损坏 | 立即推送(电话/IM) | 15分钟内响应 |
| **Major** | 主要 | 系统功能受限/降级运行/有备用路径 | 立即推送(IM/Mail) | 30分钟内响应 |
| **Minor** | 次要 | 非关键指标异常/不影响业务 | 推送(Mail/工单) | 4小时内 |
| **Info** | 信息 | 正常状态变更/配置变更 | 记录即可 | 无需响应 |

**告警分类体系**:

| 大类 | 小类 | 示例 | 默认严重级 |
|:-----|:-----|:-----|:----------|
| **故障告警** | 电源故障 | PSU失效/N+1冗余丢失 | Critical |
| | 散热故障 | 风扇停转/温度超限 | Critical |
| | 存储故障 | 硬盘离线/SMART不可恢复错误 | Critical |
| | 内存故障 | UE错误/内存掉线 | Critical/Major |
| | GPU故障 | XID Fatal/GPU离线 | Critical |
| | PCIe故障 | PCIe链路失效 | Major |
| **性能告警** | 过温预警 | 温度>设计上限-10°C | Major |
| | 功耗超限 | 整机功耗>PSU额定容量 | Major |
| | 链路降速 | PCIe x16→x8 | Major |
| **寿命告警** | 风扇寿命 | 运行时间>MTBF×80% | Minor |
| | SSD寿命 | SSD写入量>80%额定 | Minor |
| | HBM CE | CE增速异常 | Minor→Major |
| **安全告警** | 登录异常 | 连续认证失败 | Major |
| | 固件篡改 | 固件签名校验失败 | Critical |
| | 配置变更 | 未授权配置修改 | Minor |

### 2.2 告警阈值管理

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-ALM-001 | 三层阈值 | 每传感器支持UpperCritical/UpperWarning/LowerCritical/LowerWarning三层阈值 | MUST | 可通过Redfish配置 |
| BMC-ALM-002 | 阈值可配置 | 所有传感器的所有阈值可通过IPMI/Redfish动态修改 | MUST | 修改后即时生效 |
| BMC-ALM-003 | 阈值持久化 | 修改后的阈值保存在BMC非易失存储 | MUST | 掉电不丢失 |
| BMC-ALM-004 | 阈值恢复出厂 | 支持恢复阈值到出厂默认值 | MUST | — |
| BMC-ALM-005 | 阈值分组 | 支持按传感器类型分组批量设置阈值 | SHOULD | 如"所有DIMM温度阈值设为85°C" |
| BMC-ALM-006 | 滞后(Hysteresis) | 支持阈值滞后值配置，防止阈值抖动 | MUST | 默认滞后=阈值×2% |
| BMC-ALM-007 | 阈值基线自适应 | BMC可学习正常运行阈值基线并建议调整 | SHOULD | 基线学习周期≥7天 |

**阈值配置案例（GPU温度）**:

```text
传感器: GPU0_TEMP
UpperCritical:  95°C  -> GPU过热临界，立即降频+告警
UpperWarning:   85°C  -> GPU过热预警，检查散热
LowerCritical:  -10°C -> 传感器异常或环境极低
LowerWarning:   0°C   -> 环境温度偏低
Hysteresis:     2°C   -> 从告警恢复的滞后值
                 ^ 触发告警点在95°C，恢复点93°C
```

### 2.3 告警策略（抑制·去重·延迟·升级）

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-ALM-POL-001 | 告警抑制 | 维护模式下(如固件升级中)抑制非关键告警 | MUST | 抑制期过后告警自动恢复 |
| BMC-ALM-POL-002 | 告警延迟 | 短暂抖动(如温度瞬跳)不立即告警，延迟窗口可配置 | MUST | 延迟窗口默认10秒 |
| BMC-ALM-POL-003 | 告警去重 | 相同告警30分钟内不重复推送 | MUST | 去重窗口可配置 |
| BMC-ALM-POL-004 | 告警升级 | 告警持续未确认自动升级严重级 | SHOULD | 升级策略可配置 |
| BMC-ALM-POL-005 | 告警关联 | 关联告警可合并推送(如同一FRU引发的多个告警) | SHOULD | 关联规则可配置 |
| BMC-ALM-POL-006 | 告警风暴防护 | 1分钟内告警超过50条触发风暴抑制 | MUST | 风暴抑制后按最高级推送 |

**告警风暴防护逻辑**:

```text
监控告警产生速率
    |
    +-- 正常速率(<10条/分钟) -> 正常推送
    |
    +-- 高速率(10-50条/分钟) -> 合并同类告警为「多条X类型告警」
    |
    +-- 风暴率(>50条/分钟) -> 触发风暴抑制：
        1. 暂停所有Minor告警推送
        2. 合并Major告警为聚合告警
        3. 仅推送Critical告警
        4. 标记「告警风暴」事件
        5. 速率恢复正常后恢复全量推送
```

### 2.4 告警推送机制

**三重冗余推送路径**:

| 推送方式 | 协议/格式 | 可靠度 | 延迟 | 适用场景 |
|:---------|:----------|:------:|:----:|:---------|
| SNMP Trap | SNMP v2c/v3 | ⭐⭐⭐ | <10秒 | 传统监控系统接入 |
| Redfish Events | Redfish SSE（Server-Sent Events） | ⭐⭐⭐⭐⭐ | <5秒 | 现代运维平台首选 |
| RESTful Webhook | HTTPS POST+JSON | ⭐⭐⭐⭐ | <10秒 | 自定义集成 |
| Syslog | RFC 5424 (TCP/UDP/TLS) | ⭐⭐⭐ | <30秒 | 日志归档+告警(备选) |

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-ALM-PUSH-001 | SNMP Trap | 支持SNMP v2c/v3 Trap推送 | MUST | Trap格式符合标准MIB |
| BMC-ALM-PUSH-002 | Redfish Event | 支持Redfish EventService(SSE) | MUST | 符合DMTF Redfish Event规范 |
| BMC-ALM-PUSH-003 | Webhook | 支持≥3个独立Webhook端点 | MUST | 每个端点URL+Secret可配置 |
| BMC-ALM-PUSH-004 | 推送重试 | 推送失败后重试(3次，间隔指数退避) | MUST | 3次重试后标记推送失败 |
| BMC-ALM-PUSH-005 | 推送超时 | 推送超时可配置(默认5秒) | MUST | 超时算一次失败 |
| BMC-ALM-PUSH-006 | 推送认证 | Webhook支持Bearer Token/HTTPS双向认证 | MUST | 认证失败告警 |
| BMC-ALM-PUSH-007 | 告警格式标准化 | 所有推送格式统一的告警载荷 | MUST | JSON格式含:ID/时间/级别/源/消息/FRU/建议动作 |

### 2.5 告警现场快照

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-ALM-SNAP-001 | Critical告警快照 | Critical告警触发时自动保存系统状态快照 | MUST | 快照包含:传感器读数+SEL+FRU+诊断日志 |
| BMC-ALM-SNAP-002 | 快照内容 | 快照包含:时间戳+所有传感器值+前50条SEL+FRU摘要+CPU/GPU状态 | MUST | 快照用于故障回放 |
| BMC-ALM-SNAP-003 | 快照存储 | 快照保存在BMC持久存储(≥256MB已分配) | MUST | 保留最近50次快照 |
| BMC-ALM-SNAP-004 | 快照导出 | 快照可通过Redfish导出 | MUST | 导出格式JSON/CSV |
| BMC-ALM-SNAP-005 | 快照关联告警 | 快照中有该告警的完整ID链(告警ID→关联SEL→关联诊断结果) | MUST | 关联可追溯 |

---

## §3 日志系统设计

### 3.1 日志分类与存储

| 日志类型 | 内容 | 存储位置 | 容量 | 保留策略 |
|:---------|:-----|:---------|:----:|:---------|
| **SEL** | 系统事件(硬件故障/告警/状态变更) | BMC Flash | ≥4096条 | 循环覆盖 |
| **BMC调试日志** | BMC内部运行日志(模块级) | BMC Flash | ≥32MB | 按时间轮转 |
| **Screenshot** | 主机OS/BIOS屏幕截图(崩溃时) | BMC Flash | ≥10张 | 保留最近 |
| **Core dump** | BMC/主机崩溃dump | BMC Flash | ≥256MB | 标记保留 |
| **诊断结果** | 诊断套件运行结果 | BMC Flash | ≥50次 | 按时间轮转 |
| **操作审计** | 用户管理操作 | BMC Flash | ≥10000条 | 不可篡改 |
| **POST Code** | 最近几次POST Code序列 | BMC Flash | ≥20次 | 按时间轮转 |

### 3.2 SEL系统事件日志

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-LOG-SEL-001 | SEL条目容量 | SEL≥4096条，满时覆盖最旧记录 | MUST | 容量实测验证 |
| BMC-LOG-SEL-002 | 事件类型覆盖 | 所有传感器阈值触发/FRU插入移除/电源状态/固件变更 | MUST | 事件类型覆盖率100% |
| BMC-LOG-SEL-003 | 时间戳 | 每条SEL含精确时间戳(精度1秒)，支持NTP同步 | MUST | 时间偏差<1秒 |
| BMC-LOG-SEL-004 | 事件关联 | SEL事件可关联到具体FRU/传感器 | MUST | 关联字段不可为空 |
| BMC-LOG-SEL-005 | SEL即时性 | 事件产生到写入SEL延迟<5秒 | MUST | 延迟>5秒视为性能问题 |
| BMC-LOG-SEL-006 | SEL导出 | 支持通过IPMI/Redfish导出全部SEL | MUST | 导出格式:IPMI raw/Redfish JSON |
| BMC-LOG-SEL-007 | SEL清空保护 | SEL清空操作需管理员权限+审计记录 | MUST | 误清空可恢复(软删除) |

### 3.3 Debug日志系统

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-LOG-DBG-001 | 模块化日志 | 按BMC模块(IPMI/Redfish/Sensor/FAN/FWUpdate/Security等)分级记录 | MUST | 模块清单完整 |
| BMC-LOG-DBG-002 | 日志级别 | 每模块支持DEBUG/INFO/WARNING/ERROR/CRITICAL五级 | MUST | 级别可动态切换 |
| BMC-LOG-DBG-003 | 日志轮转 | 调试日志自动轮转(默认每10MB轮转) | MUST | 保留最近5个轮转文件 |
| BMC-LOG-DBG-004 | 日志持久化 | 关键日志(ERROR/CRITICAL)写入持久存储 | MUST | 掉电不丢失 |
| BMC-LOG-DBG-005 | 生产模式 | 生产中默认日志级别为WARNING，DEBUG模式可远程开启 | MUST | DEBUG模式开启有审计日志 |
| BMC-LOG-DBG-006 | 日志远程访问 | 调试日志可通过Redfish/Syslog远程访问 | MUST | 仅管理员可读 |

### 3.4 POST Code日志

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-LOG-POST-001 | POST Code捕获 | BMC实时捕获BIOS POST Code (LPC/eSPI) | MUST | 捕获率100% |
| BMC-LOG-POST-002 | POST Code历史 | 保存最近20次POST的完整Code序列 | MUST | 序列可回溯 |
| BMC-LOG-POST-003 | POST Code解码 | BMC将POST Code解码为可读描述 | MUST | 解码表符合BIOS厂商定义 |
| BMC-LOG-POST-004 | 启动失败标记 | POST过程中止在特定Code处时BMC标记该Code为失败点 | MUST | 失败POST日志高亮 |
| BMC-LOG-POST-005 | POST时间线 | POST记录各阶段耗时(PEI/DXE/BDS/TSL) | SHOULD | 可发现启动瓶颈 |

### 3.5 崩溃保留（Crash Preservation）

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-LOG-CRS-001 | OS崩溃捕获 | 主机OS崩溃(pstore/ramoops)自动保存到BMC | MUST | 捕获率>99% |
| BMC-LOG-CRS-002 | BMC崩溃捕获 | BMC自身崩溃的core dump保存到持久存储 | MUST | 崩溃前诊断日志回刷 |
| BMC-LOG-CRS-003 | 崩溃时间标记 | 崩溃时间在BMC RTC+网络NTP双确认 | MUST | 时间精度<2秒 |
| BMC-LOG-CRS-004 | 崩溃分析 | BMC对崩溃原因做初步分析(内存错误/PCIe/超时等) | SHOULD | 分析结果附在崩溃记录中 |
| BMC-LOG-CRS-005 | 崩溃导出 | 崩溃dump可通过Redfish导出 | MUST | 导出支持分片下载 |

### 3.6 日志外发(syslog/Redfish Event)

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-LOG-OUT-001 | syslog | BMC日志实时发送到远程syslog服务器(TCP/UDP/TLS) | MUST | 支持多目标(≥2个) |
| BMC-LOG-OUT-002 | syslog格式 | 日志格式符合RFC 5424 | MUST | — |
| BMC-LOG-OUT-003 | syslog过滤 | 支持按日志级别/模块过滤发送 | MUST | 过滤规则可配置 |
| BMC-LOG-OUT-004 | 网络断开缓冲 | 远程日志目标不可达时本地缓冲≥24小时 | MUST | 恢复后自动补发 |
| BMC-LOG-OUT-005 | Redfish Event | 支持Redfish EventService日志订阅 | MUST | 符合Event Format规范 |

---

## §4 远程诊断功能

### 4.1 远程故障定位

**故障定位流程自动化**:

```text
用户/运维平台触发 -> BMC接收诊断请求
    |
    +-- 1. 收集现状 (Collect)
    |      +-- 传感器当前读数
    |      +-- SEL最近100条
    |      +-- POST Code历史
    |      +-- FRU信息
    |      +-- GPU/DIMM/PCIe状态
    |
    +-- 2. 分析 (Analyze)
    |      +-- 阈值超限检查
    |      +-- 错误计数趋势
    |      +-- 关联规则匹配
    |      +-- 自检诊断运行
    |
    +-- 3. 定位 (Isolate)
    |      +-- 输出故障FRU(精确到部件)
    |      +-- 故障类别(硬件/固件/配置)
    |      +-- 置信度评分
    |
    +-- 4. 建议 (Recommend)
           +-- 修复操作(更换/重启/升级/配置)
           +-- 操作步骤描述
           +-- 参考文档链接
```

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-DIAG-REMOTE-001 | 一键诊断 | 单API请求触发全系统诊断 | MUST | 诊断≤5分钟完成 |
| BMC-DIAG-REMOTE-002 | 诊断报告 | 诊断输出结构化报告(JSON格式) | MUST | 含结论+依据+建议 |
| BMC-DIAG-REMOTE-003 | 诊断历史 | 诊断结果保存(≥50次) | MUST | — |
| BMC-DIAG-REMOTE-004 | 渐进式诊断 | 先快检(30秒)→正常则停止→深入(5分钟) | SHOULD | 快检覆盖80%故障模式 |
| BMC-DIAG-REMOTE-005 | 诊断上下文 | 诊断报告含故障发生前后的传感器趋势数据 | SHOULD | 趋势窗口≥前30分钟 |

### 4.2 诊断套件

| 诊断类型 | 内容 | 时间 | 触发方式 |
|:---------|:-----|:----:|:---------|
| **快检(Quick)** | 传感器读值+SEL最近条目+FRU在位+BIOS POST状态 | <30秒 | 定时/按需 |
| **标准(Standard)** | 快检+DIMM读写测试+NVMe识别+PCIe链路检查+风扇功能+GPU DCGM L1 | <3分钟 | 按需/报警后自动 |
| **深度(Deep)** | 标准+内存全量测试+GPU DCGM L2-L3+NVLink全互联+存储SMART+网络连通性 | <30分钟 | 更换备件后/定期 |
| **烧机(Burn-in)** | 深度+CPU/GPU压力+内存压力+网络打流+存储IO | >1小时 | 新机验收/大修后 |

**BMC内建的诊断脚本**:

```text
/usr/local/bin/diag/
+-- quick_diag.sh         -> 30秒快检
+-- standard_diag.sh      -> 3分钟标准诊断
+-- deep_diag.sh          -> 30分钟深度诊断
+-- burnin_diag.sh        -> 烧机诊断
+-- diag_gpu.sh           -> GPU专项诊断(NVML/DCGM)
+-- diag_memory.sh        -> 内存专项诊断
+-- diag_storage.sh       -> 存储专项诊断
+-- diag_network.sh       -> 网络专项诊断
+-- diag_power.sh         -> 供电专项诊断
+-- diag_thermal.sh       -> 散热专项诊断
+-- diag_collect_logs.sh  -> 全量诊断日志收集
```

### 4.3 KVM与SOL

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-DIAG-KVM-001 | KVM over IP | 远程图形化控制台(HTML5) | MUST | 帧率≥30fps@1080p |
| BMC-DIAG-KVM-002 | 虚拟介质 | 支持ISO镜像挂载(远程安装OS/诊断工具) | MUST | 挂载类型:HTTP/CIFS/NFS |
| BMC-DIAG-KVM-003 | KVM录制 | 支持KVM会话录制(用于故障回放) | SHOULD | 录制存储在BMC |
| BMC-DIAG-KVM-004 | SOL | Serial Over LAN(串口重定向) | MUST | 波特率≥115200 |
| BMC-DIAG-KVM-005 | SOL多会话 | SOL支持≥2个并发会话 | SHOULD | — |
| BMC-DIAG-KVM-006 | SOL日志 | SOL输出自动记录日志 | MUST | 日志大小可配置 |

### 4.4 远程BIOS诊断

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-DIAG-BIOS-001 | 远程BIOS设置 | 通过BMC修改BIOS配置(下次重启生效) | MUST | 覆盖80%以上BIOS配置项 |
| BMC-DIAG-BIOS-002 | BIOS默认恢复 | 远程触发BIOS恢复默认设置 | MUST | 恢复后重启生效 |
| BMC-DIAG-BIOS-003 | BIOS诊断日志 | 通过BMC获取BIOS诊断日志(EDK2 Debug Log) | MUST | 日志分级(Error/Warning/Info) |
| BMC-DIAG-BIOS-004 | BIOS版本 | BMC查询BIOS版本+发布时间+校验和 | MUST | — |
| BMC-DIAG-BIOS-005 | SMBIOS查询 | BMC解析并提供SMBIOS各表(系统/主板/BIOS/内存/CPU) | MUST | 表内容完整 |

### 4.5 故障现场回放

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-DIAG-PLAY-001 | 传感器趋势图 | BMC WebUI提供传感器历史趋势图 | MUST | 支持24h/7d/30d视图 |
| BMC-DIAG-PLAY-002 | 时间线视图 | 将SEL事件+传感器异常+告警+操作记录显示在统一时间线上 | SHOULD | 时间线支持放大缩小 |
| BMC-DIAG-PLAY-003 | 故障时间线 | 围绕故障事件的前后60分钟时间线 | SHOULD | 显示故障前兆+故障瞬间+故障影响 |
| BMC-DIAG-PLAY-004 | 比对模式 | 同型号两台设备的传感器数据叠图对比 | SHOULD | 用于异常设备vs正常设备 |

---

## §5 预测性故障分析

### 5.1 趋势分析

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-PRED-001 | CE错误趋势 | 记录DIMM/GPU CE计数时间序列，按日/周汇报增速 | MUST | 增速>阈值预警 |
| BMC-PRED-002 | SMART趋势 | 记录SSD/HDD SMART属性时间序列(05/C5/C6/0E等) | MUST | 越界属性预警 |
| BMC-PRED-003 | 风扇趋势 | 记录风扇转速基线，转速持续下降预警 | MUST | 下降>10%预警 |
| BMC-PRED-004 | 温度趋势 | 记录运行温度基线，温度持续上升预警 | SHOULD | 散热性能退化检测 |
| BMC-PRED-005 | 功耗趋势 | 记录整机/GPU功耗基线，异常增长/下降预警 | SHOULD | 偏离基线>15% |

### 5.2 寿命预测

| 组件 | 预测方法 | 数据源 | 预测提前量 | 规格引用 |
|:-----|:---------|:-------|:----------:|:---------|
| **风扇** | 累计运行时长→MTBF剩余 | 风扇运行计数 | ≥1000小时 | BMC-PRED-011 |
| **SSD** | SMART 05(耗损)+0E(介质错误) | NVMe-MI | ≥14天 | BMC-PRED-012 |
| **HDD** | SMART 05+C5+C6+CRC | SATA SES | ≥7天 | BMC-PRED-013 |
| **PSU** | 运行时长+温度历史+12V输出抖动 | PMBus | ≥1000小时 | BMC-PRED-014 |
| **GPU HBM** | CE增速曲线(累计/每日) | NVML/DCGM | ≥72小时 | BMC-PRED-015 |
| **DIMM** | CE增速+温度+电压 | EDAC/SPD | ≥72小时 | BMC-PRED-016 |
| **RTC电池** | 电压监测 | I2C ADC | ≥30天 | BMC-PRED-017 |
| **GPU供电连接器** | 温度历史+插拔次数 | NTC+计数器 | ≥1000小时 | BMC-PRED-018 |

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-PRED-011 | 风扇寿命 | 基于运行时长预测风扇剩余寿命 | MUST | 预测提前量≥1000小时 |
| BMC-PRED-012 | SSD寿命 | 基于SMART预测SSD剩余寿命 | MUST | 预测提前量≥14天 |
| BMC-PRED-013 | HDD寿命 | 基于SMART预测HDD剩余寿命 | MUST | 预测提前量≥7天 |
| BMC-PRED-014 | PSU寿命 | 基于运行时长+温度预测PSU寿命 | SHOULD | 预测提前量≥1000小时 |
| BMC-PRED-015 | GPU寿命 | 基于HBM CE趋势预测GPU风险 | MUST | 预测提前量≥72小时 |
| BMC-PRED-016 | DIMM寿命 | 基于CE趋势预测DIMM风险 | MUST | 预测提前量≥72小时 |
| BMC-PRED-017 | 电池寿命 | 基于电压监测预警RTC电池 | SHOULD | 预测提前量≥30天 |

### 5.3 异常检测

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-PRED-AD-001 | 突然缺失 | 传感器读数突变为0/NaN | MUST | 检测延迟<1个采样周期 |
| BMC-PRED-AD-002 | 读数冻结 | 传感器读数持续不变(>30分钟) | MUST | 检测延迟≤30分钟 |
| BMC-PRED-AD-003 | 一致性偏差 | 冗余传感器偏差>3% | MUST | — |
| BMC-PRED-AD-004 | 模式异常 | 功耗/温度模式偏离历史模式 | SHOULD | 基线学习周期≥7天 |
| BMC-PRED-AD-005 | 抖动异常 | 传感器抖动幅度超出正常范围 | SHOULD | 抖动基线自动学习 |

### 5.4 预测准确度要求

| 指标 | 目标值 | 测量方法 |
|:-----|:------:|:---------|
| 故障预警准确率 | ≥80% | TP/(TP+FP) |
| 故障预警提前量 | ≥72小时 | 预警→实际故障的时间 |
| 漏报率 | <5% | FN/(TP+FN) |
| 误报率 | <20% | FP/(TP+FP) |
| 预警平均提前时间 | ≥96小时 | — |

---

## §6 BMC自诊断与恢复

### 6.1 BMC健康自检

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-SELF-001 | 开机自检 | BMC上电自检覆盖:内存/Flash/网络/I2C总线/IPMB | MUST | 自检失败标记并尝试恢复 |
| BMC-SELF-002 | 心跳监控 | BMC内部看门狗监控主进程健康 | MUST | 主进程死锁自动重启 |
| BMC-SELF-003 | 资源监控 | BMC监控自身CPU负载/内存使用/Flash剩余 | MUST | CPU负载>80%告警 |
| BMC-SELF-004 | I2C总线监控 | BMC监控I2C总线通信质量(超时/NAK计数) | MUST | 总线故障告警 |
| BMC-SELF-005 | 网络连通自检 | BMC定期检查管理网络连通性 | MUST | 网络不通告警 |
| BMC-SELF-006 | 传感器自检 | BMC定期读回传感器校验值(如可用) | SHOULD | 传感器自身故障标记 |

### 6.2 BMC固件恢复

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-REC-001 | 双镜像 | BMC固件双镜像(Active+Standby) | MUST | 主镜像损坏自动回退 |
| BMC-REC-002 | 恢复模式 | BMC支持U-Boot恢复模式(网络刷写) | MUST | 恢复模式可独立启动 |
| BMC-REC-003 | 恢复IP | 恢复模式下BMC有默认IP(如192.168.1.1) | MUST | 默认IP可恢复网络访问 |
| BMC-REC-004 | 配置保留 | 固件更新/恢复后保留配置(网络/IP/用户/阈值) | MUST | 配置备份寄存器受保护 |
| BMC-REC-005 | 回退成功率 | 主镜像故障→回退到备用镜像成功率>99% | MUST | 故障注入测试验证 |
| BMC-REC-006 | 恢复过程不中断主机 | BMC恢复过程中主机正常运行 | MUST | 主机不受影响 |

### 6.3 BMC与BIOS协同诊断

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-COOP-001 | BIOS-BMC通信通道 | eSPI/LPC/KCS/USB-HID通道正常 | MUST | 通信周期<100ms |
| BMC-COOP-002 | BIOS错误通知 | BIOS检测到硬件错误(CPU/内存/PCIe)立即通知BMC | MUST | BIOSSMI→BMC通知延迟<1秒 |
| BMC-COOP-003 | BMC POST监控 | BMC监控BIOS POST进度，POST挂起>30min告警 | MUST | — |
| BMC-COOP-004 | BIOS诊断日志转发 | BIOS调试日志通过eSPI通道发送到BMC存档 | SHOULD | BMC存储BIOS日志 |
| BMC-COOP-005 | POST失败协同诊断 | POST失败时BMC+BIO采集完整故障现场 | MUST | 含POST Code+传感器+错误寄存器 |

---

## §7 诊断接口标准化

### 7.1 Redfish诊断模型

| Redfish资源 | 路径(示例) | 用途 |
|:------------|:-----------|:-----|
| Chassis | /redfish/v1/Chassis/{ChassisId} | 机箱级传感器+FRU |
| Thermal | /redfish/v1/Chassis/{ChassisId}/Thermal | 温度传感器集合 |
| Power | /redfish/v1/Chassis/{ChassisId}/Power | 功耗传感器集合 |
| Sensors | /redfish/v1/Chassis/{ChassisId}/Sensors | 所有传感器统一接口(R2024.1+) |
| Systems | /redfish/v1/Systems/{SystemId} | 整机系统诊断 |
| LogServices | /redfish/v1/Managers/{BMCId}/LogServices/SEL | SEL日志服务 |
| EventService | /redfish/v1/EventService | 事件订阅(告警推送) |
| UpdateService | /redfish/v1/UpdateService | 固件升级管理 |
| TaskService | /redfish/v1/TaskService | 长时间任务(A同步) |

**Redfish诊断调用流程示例**:

```text
REST GET /redfish/v1/Systems/1/LogServices/SEL/Entries
  -> 获取SEL条目列表 (过滤最近24小时Critical事件)

REST POST /redfish/v1/Systems/1/Actions/ComputerSystem.Reset
  -> 远程重启

REST POST /redfish/v1/Systems/1/Actions/ComputerSystem.Diagnostics
  -> 触发系统诊断 (DMTF扩展)
```

### 7.2 IPMI诊断扩展

| IPMI命令 | 网卡功能代码 | 用途 |
|:----------|:------------|:-----|
| Get Sensor Reading | 0x2D | 单个传感器读值 |
| Get Sensor Thresholds | 0x27 | 传感器阈值查询 |
| Get SEL Entry | 0x43 | 读取SEL条目 |
| Get FRU Inventory Area Info | 0x10 | FRU信息查询 |
| Get Device ID | 0x01 | BMC自身版本信息 |
| Master Write-Read | 0x52 | I2C透传(诊断扩展) |
| Chassis Control | 0x02 | 电源控制 |

### 7.3 指标导出(Prometheus)

| 序号 | 规格项 | 需求描述 | 强制等级 | 验收标准 |
|:----:|:-------|:---------|:--------:|:---------|
| BMC-METRIC-001 | Prometheus Exporter | BMC内置/外挂Prometheus Metrics端点 | SHOULD | 指标命名符合Prometheus规范 |
| BMC-METRIC-002 | 指标覆盖 | 导出指标覆盖:温度/电压/功耗/风扇/存储/GPU/Link | SHOULD | 指标数≥200 |
| BMC-METRIC-003 | 指标标签 | 指标标签含:FRU类型/槽位号/设备型号 | SHOULD | 标签可用于过滤和聚合 |
| BMC-METRIC-004 | 指标元数据 | 指标含单位/描述/类型(Gauge/Counter/Histogram) | SHOULD | 符合OpenMetrics标准 |

---

## §8 BMC诊断能力验收

| 验收类别 | 测试项 | 通过标准 | 关联规格 |
|:---------|:-------|:---------|:---------|
| **传感器验收** | 全量传感器采集覆盖 | ≥95%的预期传感器可读 | BMC-SEN-001~010 |
| | 传感器精度验证 | 外接标准源对比偏差<规格 | BMC-SEN-003 |
| | 传感器刷新率 | 采样间隔符合配置值 | BMC-SEN-001 |
| **告警验收** | 阈值配置验证 | 每条阈值可独立+批量配置 | BMC-ALM-001~007 |
| | 告警推送验证 | SNMP/Redfish/Webhook三通 | BMC-ALM-PUSH-001~007 |
| | 告警去重验证 | 相同告警不在窗口内重复 | BMC-ALM-POL-003 |
| | 告警风暴测试 | 100条/分钟的告警量不淹没推送 | BMC-ALM-POL-006 |
| **日志验收** | SEL容量验证 | ≥4096条循环覆盖 | BMC-LOG-SEL-001 |
| | SEL时间戳验证 | NTP同步后偏差<1秒 | BMC-LOG-SEL-003 |
| | POST Code验证 | 不同启动场景下Code正确捕获 | BMC-LOG-POST-001~005 |
| **诊断验收** | 远程一键诊断 | API触发30秒返回结果 | BMC-DIAG-REMOTE-001 |
| | GPU诊断 | DCGM L1-L3可执行 | GPU-DIAG-001~007 |
| | 故障定位准确率 | 注入20种故障，定位准确率≥95% | BMC-DIAG-REMOTE-001~005 |
| **预测验收** | CE趋势预警 | 模拟CE增速，在阈值前预警 | BMC-PRED-001/DMC-PRED-015 |
| | SMART预警 | 模拟SMART阈值越界，预警触发 | BMC-PRED-002/BMC-PRED-012 |
| **自诊断验收** | BMC看门狗 | 主进程停止→自动重启<30秒 | BMC-SELF-002 |
| | 双镜像回退 | 损坏主镜像→自动回退备用 | BMC-REC-001 |

---

## 参考文献

- [可服务性需求规格说明书 §3](2026-07-30-server-serviceability-specification.md#§3-带外运维oobbmc可服务性规格)
- [调试系统设计深度分析](../../02_rd/01_product/01_software/2026-07-21-debug-system-design.md#4-bmc-调试方案)
- [整机柜/集群故障诊断规格体系](../../02_rd/00_shared/05_fault-diagnosis/2026-06-29-rack-cluster-fault-diagnosis-specs.md)
- DMTF: Redfish Specification DSP0266 (v2023.1+)
- DMTF: IPMI v2.0 Specification DSP0134
- DMTF: SMBIOS Reference Specification DSP0134 (v3.7+)
- OpenBMC: Phosphor Project Documentation
- OCP: OpenBMC Yocto/Phosphor Project Guidelines

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:-----|:----:|:---------|
| 2026-07-30 | v1.0 | 首次创建，覆盖8章BMC诊断能力规格 |
