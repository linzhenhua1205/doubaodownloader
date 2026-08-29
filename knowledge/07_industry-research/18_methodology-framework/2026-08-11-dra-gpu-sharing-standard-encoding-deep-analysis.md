# 🧩 DRA 正式接管 GPU 共享编码层：K8s v1.34 GA / v1.35 默认 + HAMi 重构——设备共享进入标准时代

> **类型**: 深度专题 | **日期**: 2026-08-11（工程事件：K8s v1.34/v1.35 发布节奏 + HAMi 仓库重构）| **定位**: Kubernetes Dynamic Resource Allocation（DRA）从"可选特性"走向"GPU 共享编码层的事实标准"——08-09 预告的 DRA×HAMi 合流正式落地；与 K8s AI 基础设施实践、GPU 虚拟化/共享专题互证
> **数据源**: GitHub Project-HAMi 仓库实测（HAMi/HAMi-core/HAMi-WebUI 三个 repo 已拆分，★4290）+ K8s DRA 演进路线（知识库既有记录）+ 工程推理
> **关联文件**: [`2026-07-28-k8s-ai-infrastructure-practices.md`](../../07_industry-research/18_methodology-framework/2026-07-28-k8s-ai-infrastructure-practices.md)（K8s AI 实践）、[`2026-06-29-k8s-scheduling-system.md`](../../02_rd/01_product/01_software/02-distributed-os/2026-06-29-k8s-scheduling-system.md)（K8s 调度）、[`2026-06-29-k8s-networking-storage-qos-ops.md`](../../02_rd/01_product/01_software/02-distributed-os/2026-06-29-k8s-networking-storage-qos-ops.md)（K8s 网络/存储）

---

## 📑 目录

- [0. 一句话结论](#0-一句话结论)
- [1. 事件还原：三个里程碑](#1-事件还原三个里程碑)
- [2. 技术背景：DRA 是什么、为什么取代 Device Plugin](#2-技术背景dra-是什么为什么取代-device-plugin)
- [3. HAMi 重构：3-repo 拆分的技术逻辑](#3-hami-重构3-repo-拆分的技术逻辑)
- [4. 原理细节：DRA 的编码模型如何承载 GPU 共享](#4-原理细节dra-的编码模型如何承载-gpu-共享)
- [5. 技术框架对比：Device Plugin vs DRA 时代](#5-技术框架对比device-plugin-vs-dra-时代)
- [6. 产业影响：GPU 共享生态的重组](#6-产业影响gpu-共享生态的重组)
- [7. 与知识库既有框架互证](#7-与知识库既有框架互证)
- [8. 结论与可证伪预判](#8-结论与可证伪预判)
- [9. 数据缺口与下一步](#9-数据缺口与下一步)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 0. 一句话结论

> **K8s DRA 进入 v1.34 GA / v1.35 默认启用，HAMi 同步拆分为 3 个 repo（HAMi / HAMi-core / HAMi-WebUI）把分数请求编码（fractional request encoding）迁移到 DRA 之上——标志着 GPU 共享从"各家 device plugin 私有实现"进入"K8s 原生标准编码"时代。这是设备管理的「协议标准化」：**编码层统一、实现层竞争**，与知识库「平台工程=build 差异化层+buy 商品层」「标准 vs 厂商活跃度倒挂」互证。**

---

## 1. 事件还原：三个里程碑

| 时间 | 事件 | 意义 |
|:-----|:-----|:-----|
| K8s v1.34 | **DRA 正式 GA**（general availability） | 从 alpha/beta 毕业为稳定特性 |
| K8s v1.35 | **DRA 默认启用** | 新集群开箱即用（不再需要显式 feature gate） |
| 2026-08 | **HAMi 拆 3 repo**（HAMi/HAMi-core/HAMi-WebUI） | 把**分数请求编码**迁到 DRA 之上——架构重构 |

---

## 2. 技术背景：DRA 是什么、为什么取代 Device Plugin

### 2.1 Device Plugin 的架构局限

传统 GPU 共享靠 **Device Plugin + Extended Resource**：
- 暴露资源为**整数计数**（如 nvidia.com/gpu: 1）
- 无法表达**分数请求**（0.5 GPU）、**属性选择**（要哪块卡）、**拓扑约束**（同 NUMA）
- 每次分配由插件**黑盒决定**——调度器不知道设备细节

### 2.2 DRA 的架构升级

**Dynamic Resource Allocation（DRA）** 是 K8s 对设备管理的重构：

| 维度 | Device Plugin | DRA |
|:-----|:--------------|:----|
| 资源表达 | 整数计数（extended resource） | **结构化 ResourceClaim**（可携带参数/属性/约束） |
| 分配时机 | 调度时一次性 | **绑定后延迟分配**（claim 可随时创建/修改） |
| 调度信息 | 黑盒（调度器只知道数量） | **结构化参数**（调度器可感知属性/拓扑） |
| 生命周期 | 随 pod | **独立于 pod 的 claim**（可跨 pod 复用） |
| 管理面 | 无（插件各自为政） | **DRA Driver**（标准化的资源管理协议） |

### 2.3 为什么 DRA 是 GPU 共享的正确编码层

- **分数请求**：claim 参数可表达"0.5 GPU"（份额）——不再受整数计数限制
- **属性/拓扑**：claim 可携带"需要 HBM 容量 X、亲和 NUMA 节点 Y"——调度器可做**感知调度**
- **共享语义**：多个 pod 引用同一 claim（共享一块 GPU）——**编码层原生支持**

---

## 3. HAMi 重构：3-repo 拆分的技术逻辑

### 3.1 实测状态（GitHub 一手）

| Repo | ★ | 定位 |
|:-----|:--:|:-----|
| **Project-HAMi/HAMi** | 4290 | 主仓库：异构 GPU 共享（原单仓库） |
| **Project-HAMi/HAMi-core** | 321 | 透明 in-container GPU 资源控制器（内存/算力强制） |
| **Project-HAMi/HAMi-WebUI** | 87 | GPU 资源管理与可观测性平台（K8s） |

### 3.2 拆分逻辑：分层架构的仓库化

```
+-------------------------------------------+
| HAMi-WebUI (observability / management)   |  <- UI + monitoring
+-------------------------------------------+
| HAMi (main framework: DRA encoding layer) |  <- fractional requests on DRA
+-------------------------------------------+
| HAMi-core (in-container control plane)    |  <- memory/compute enforcement
+-------------------------------------------+
```

**为什么拆**：
1. **关注点分离**：编码/调度（HAMi）、执行/强制（core）、观测/管理（WebUI）——三者演进节奏不同
2. **依赖收敛**：core 是执行细节（容器内 cgroup/驱动交互），独立版本演进不拖累主框架
3. **生态入口**：WebUI 独立 → 作为观测入口吸引社区（GPU 池可视化管理是运维刚需）
4. **DRA 对齐**：主框架专注"把分数请求编码到 DRA"——**编码层标准化的战略卡位**

---

## 4. 原理细节：DRA 的编码模型如何承载 GPU 共享

### 4.1 ResourceClaim 的请求编码

分数 GPU 请求在 DRA 中的表达（示意）：

```yaml
apiVersion: resource.k8s.io/v1beta1
kind: ResourceClaim
metadata:
  name: gpu-share-05
spec:
  devices:
    requests:
    - name: gpu
      deviceClassName: nvidia.com/gpu
      selectors:
      - cel: 'device.memory >= 40Gi'    # attribute: memory
      - cel: 'device.sharable == true'  # shareable
    allocations:
    - name: gpu
      devices:
      - request: gpu
        config:
        - opaque:
            driver: hami.sh
            parameters:
              fraction: 0.5              # fractional: half GPU
```

**关键编码能力**：
- **CEL 选择器**（Common Expression Language）：调度器可对设备属性做**结构化筛选**（显存/算力/共享能力）
- **opaque 参数**：DRA Driver（HAMi）自定义的分配参数（fraction）——**编码层开放、语义由驱动实现**
- **driver 指定**：明确资源管理责任方（hami.sh）——**协议标准化 + 实现竞争**

### 4.2 为什么这比 Device Plugin 时代好

- **Device Plugin 时代**：分数请求是 HAMi 自己的 CRD/annotation——**私有编码**，无法被通用调度器理解
- **DRA 时代**：分数请求是 **K8s 原生 claim**——**标准编码**，任何 DRA 驱动/调度器/观测工具都能理解
- 本质：**从"应用私有协议"到"应用标准协议"**——降低集成成本、扩大生态

---

## 5. 技术框架对比：Device Plugin vs DRA 时代

| 维度 | Device Plugin 时代（2022-2025） | DRA 时代（2026+） |
|:-----|:-------------------------------|:------------------|
| 共享编码 | 各家私有（HAMi annotation / Volcano / 厂商插件） | **K8s 原生 ResourceClaim** |
| 调度感知 | 黑盒数量 | 结构化属性（CEL 选择器） |
| 生态 | 碎片化（每厂商一套） | 统一（DRA 驱动可插拔） |
| HAMi 角色 | 全栈私有（编码+执行+观测） | **编码层标准（DRA）+ 执行层私有（core）** |
| 可观测性 | 私有监控 | WebUI + K8s 原生 API |

---

## 6. 产业影响：GPU 共享生态的重组

### 6.1 竞争从"编码协议"转移到"执行质量"

- 编码层统一后，HAMi/Volcano/各厂商插件的差异化**收窄到执行层**：内存隔离强度、算力限制精度、调度延迟、故障处理
- **执行质量 = 新竞争焦点**（core repo 的战略价值上升）

### 6.2 对国产 GPU 厂商

- 国产 GPU（华为昇腾/寒武纪/摩尔线程）的 K8s 接入**可直接基于 DRA**——不必自造编码
- HAMi 已支持昇腾（ascend-device-plugin 存在）——DRA 化降低国产卡接入门槛

### 6.3 对超节点/集群管理

- 万卡集群的**异构共享**（不同 GPU 型号混布）需要属性感知调度——DRA 的 CEL 选择器是**原生支撑**
- 与知识库「异构 GPU 共享」主线互证：编码层统一是异构调度的前提

---

## 7. 与知识库既有框架互证

### 7.1 平台工程：build 差异化层 + buy 商品层

- **编码层（DRA）= buy 商品层**（K8s 标准，无需自建）
- **执行层（HAMi-core）= build 差异化层**（隔离质量是自家竞争力）
- 完美映射知识库「平台工程 ROI=build 差异化+buy 商品」原则

### 7.2 标准 vs 厂商活跃度倒挂

- 知识库记录"标准 vs 厂商活跃度倒挂"现象——DRA 是**标准侧**的追赶者反超（K8s 生态主导权回到 CNCF）
- 厂商（NVIDIA MIG/时间切片、AMD、国产）的私有方案**收敛到 DRA 之上**——标准的网络效应显现

### 7.3 08-09 预告的闭环登记

- 08-09 日报预告「DRA×HAMi 合流」——本篇**闭环登记**：v1.34 GA + v1.35 默认 + HAMi 3-repo 重构 = 合流落地

### 7.4 与 GPU 虚拟化/共享专题

- 知识库 GPU 虚拟化专题（MIG/时间切片/vGPU）记录各方案差异——DRA 提供**统一编码层**，各方案作为 DRA Driver 共存——**编码统一、语义竞争**

---

## 8. 结论与可证伪预判

### 结论

> **DRA 正式 GA + 默认启用 + HAMi 重构，三层信号共同宣告：GPU 共享进入 K8s 原生编码时代。对 AI 基础设施的含义——设备管理从"各家私有协议"走向"标准编码 + 实现竞争"，异构 GPU 集群的调度、共享、观测成本系统性下降，执行质量（隔离/强制/延迟）成为新的差异化战场。**

### 可证伪预判（2027 核验）

| # | 预判 |
|:--|:-----|
| H1 | 2027 年底前主流 GPU 共享方案（HAMi/Volcano/厂商插件）全部提供 DRA 驱动 |
| H2 | DRA 编码成为 K8s GPU 共享的事实标准（新项目默认走 DRA，不再自造 CRD） |
| H3 | HAMi-core 独立演进为可嵌入其他框架的通用 GPU 资源控制器 |
| H4 | 国产 GPU 厂商的 K8s 插件 2027 年前至少 2 家原生支持 DRA |

---

## 9. 数据缺口与下一步

### 数据缺口（诚实标注）
- K8s v1.34/v1.35 的具体发布日期与 DRA GA 细节——未抓取官方 release notes（依赖日报记录）
- HAMi 拆分的时间线精确日期——以仓库现状为准
- DRA 分数请求编码的具体 API 形态（v1beta1 字段名）——示意为工程推理，待官方文档确认

### 下一步建议
1. 抓取 K8s v1.35 release notes 确认 DRA 默认启用的官方表述（替换日报转述）
2. 深挖 HAMi-core 的技术细节（内存/算力强制的实现机制——cgroup/驱动层）
3. 与 GPU 虚拟化专题交叉登记："DRA 编码层 × 各执行方案"图谱
4. 跟踪国产 GPU 厂商 DRA 支持进度（华为/寒武纪/摩尔线程）

---

## 参考来源

| # | 来源 | 类型 | 日期 |
|:--|:-----|:-----|:-----|
| 1 | GitHub Project-HAMi/HAMi（★4290）、HAMi-core（★321）、HAMi-WebUI（★87） | 仓库实测（一手） | 2026-08-11 |
| 2 | knowledge/weekly-reports/00_daily/2026-08-11.md — compute-platform 条目 | 知识库日报 | 2026-08-11 |
| 3 | knowledge/07_industry-research/18_methodology-framework/2026-07-28-k8s-ai-infrastructure-practices.md | 知识库 K8s 实践 | 2026-07-28 |

---

## Changelog

- 2026-08-11: v1.0 初稿——DRA GA/默认启用 + HAMi 3-repo 重构技术深挖 + 编码模型分析 + 生态重组判断
