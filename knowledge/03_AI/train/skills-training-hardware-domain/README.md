# 🧩 面向服务器硬件领域的 Skills 培训专题 v0.2

> **版本**: v0.2 | **更新**: 2026-07-29 | **定位**: 面向服务器硬件研发团队的 AI Skills 全面进阶指南
> **相关技能**: `skill-creator` · `open-source-skill-packer` · `evolver` · `doc-reviewer` · `knowledge-doc-writer`
> **前置阅读**: 推荐先阅读 [`supernode-storage-requirements-training/README.md`](../supernode-storage-requirements-training/README.md)（存储需求培训）了解具体技术背景

---

## 📑 目录

- [§1 Prompt → Skills → MCP → Scripts 四层架构](#1-prompt--skills--mcp--scripts-四层架构)
- [§2 Skill Creator & 六步创建流程](#2-skill-creator--六步创建流程)
- [§3 好 Skills 的特征：七维评估矩阵](#3-好-skills-的特征七维评估矩阵)
- [§4 服务器硬件领域可 Skills 化的全景图](#4-服务器硬件领域可-skills-化的全景图)
- [§5 GitHub 硬件相关开源项目（扩展篇）](#5-github-硬件相关开源项目扩展篇)
  - [5.1 BMC/IPMI/Redfish 管理工具链](#51-bmcipmiredfish-管理工具链)
  - [5.2 GPU 集群监控与诊断](#52-gpu-集群监控与诊断)
  - [5.3 存储性能基准与 NVMe 工具](#53-存储性能基准与-nvme-工具)
  - [5.4 服务器/数据中心模拟](#54-服务器数据中心模拟)
  - [5.5 系统监控与可观测性](#55-系统监控与可观测性)
- [§6 基于本地知识库的 Skills 编写方法（借鉴 spec 方法论体系）](#6-基于本地知识库的-skills-编写方法借鉴-spec-方法论体系)
  - [6.1 核心思想：从模式提取到 Skill 固化](#61-核心思想从模式提取到-skill-固化)
  - [6.2 方法一：知识库模式提取法（借鉴 meth-006）](#62-方法一知识库模式提取法借鉴-meth-006)
  - [6.3 方法二：两阶段生产法（借鉴 meth-009）](#63-方法二两阶段生产法借鉴-meth-009)
  - [6.4 方法三：Skills-Scripts 双引擎设计（借鉴 design-007）](#64-方法三skills-scripts-双引擎设计借鉴-design-007)
  - [6.5 方法四：SSOT 治理约束法](#65-方法四ssot-治理约束法)
  - [6.6 方法五：会话记录挖掘法](#66-方法五会话记录挖掘法)
  - [6.7 六种方法的选择决策树](#67-六种方法的选择决策树)
  - [6.8 实操案例：从知识库中提取超节点存储设计 Skill](#68-实操案例从知识库中提取超节点存储设计-skill)
- [§7 针对 Trae 的 Skills 编写方法（基于本工程 125+ Skills 经验）](#7-针对-trae-的-skills-编写方法基于本工程-125-skills-经验)
  - [7.1 Trae 的 Skills 局限与四种弥补策略](#71-trae-的-skills-局限与四种弥补策略)
  - [7.2 策略一：Custom Instructions 常驻规则法](#72-策略一custom-instructions-常驻规则法)
  - [7.3 策略二：.trae/rules/ 项目规则矩阵法](#73-策略二traerules-项目规则矩阵法)
  - [7.4 策略三：多阶段 Pipeline 注入法](#74-策略三多阶段-pipeline-注入法)
  - [7.5 策略四：Open-Source-Skill-Packer 封装法](#75-策略四open-source-skill-packer-封装法)
  - [7.6 Trae 技能编写的质量门禁](#76-trae-技能编写的质量门禁)
- [§8 Skill 样例库（扩展至 8 个）](#8-skill-样例库扩展至-8-个)
  - [8.1 BMC 固件交叉编译](#81-bmc-固件交叉编译)
  - [8.2 NVMe SSD 性能基准测试](#82-nvme-ssd-性能基准测试)
  - [8.3 服务器 RAS 故障诊断](#83-服务器-ras-故障诊断)
  - [8.4 超节点存储方案设计](#84-超节点存储方案设计)
  - [8.5 GPU 集群健康检查](#85-gpu-集群健康检查)
  - [8.6 网络互联架构分析（UALink/CXL/PCIe）](#86-网络互联架构分析ualinkcxlpcie)
  - [8.7 训练任务 Hang 排查](#87-训练任务-hang-排查)
  - [8.8 服务器功耗建模与 PUE 估算](#88-服务器功耗建模与-pue-估算)
- [§9 从对话日志提取 Skill 的工业级工作流](#9-从对话日志提取-skill-的工业级工作流)
  - [9.1 自动化脚本辅助的提取流程](#91-自动化脚本辅助的提取流程)
  - [9.2 skill-evolver：自进化机制的应用](#92-skill-evolver自进化机制的应用)
  - [9.3 Skill 生命周期管理](#93-skill-生命周期管理)
  - [9.4 125 Skills 实践的经验教训](#94-125-skills-实践的经验教训)
  - [9.5 本工程 7 个对话案例精粹](#95-本工程-7-个对话案例精粹)
  - [9.6 Skill 失效模式与对策](#96-skill-失效模式与对策)
- [§10 Skill 的约束持久化与工程可靠性](#10-skill-的约束持久化与工程可靠性)
  - [10.1 约束持久化的必要性](#101-约束持久化的必要性)
  - [10.2 约束的三层部署策略](#102-约束的三层部署策略)
  - [10.3 与 meth-007 精确细节控制的联动](#103-与-meth-007-精确细节控制的联动)
  - [10.4 Skills 质量保证完整自检清单（v2.0）](#104-skills-质量保证完整自检清单v20)
- [参考文档与延伸阅读](#参考文档与延伸阅读)
- [Changelog](#changelog)

---

## §1 Prompt → Skills → MCP → Scripts 四层架构

### 1.1 四者关系总览

```text
+---------------------------------------------------------+
|  用户 Prompt（"帮我排查这台服务器的 BMC 故障"）          |
+-------------------------+-------------------------------+
                          v
+---------------------------------------------------------+
|  Skills 系统 — 可复用的知识/工作流封装                    |
|  -> description 匹配 -> SKILL.md 加载 -> 逐步执行          |
+-------------------------+-------------------------------+
          +---------------+---------------+
          v               v               v
+-----------------+ +----------+ +--------------+
| MCP 工具         | | Scripts  | | 知识库查询    |
| (标准接口协议)    | | (确定性) | | (历史案例)    |
+-----------------+ +----------+ +--------------+
```

| 角色 | 一句话 | 类比 | 在 CowAgent 中的形态 |
|:-----|:-------|:-----|:-------------------|
| **Prompt** | "我要做什么" | 需求描述 | `MEMORY.md` + 当前对话 |
| **Skill** | "我有什么可复用的知识/流程" | 操作手册 | `skills/<name>/SKILL.md` |
| **MCP** | "我能用什么工具" | API 接口 | 外部 MCP Server 进程 |
| **Script** | "我怎么确定性地执行" | 自动化脚本 | `scripts/check_*/fix_*/` |

### 1.2 选择决策指南

```text
1. 一次性简单对话? -> 直接写 Prompt
2. 任务经常出现? -> 继续
3. 需要外部数据源? -> 考虑 MCP Server
4. 包含多步流程或领域知识? -> 创建 Skill
   +- 内部有确定性操作? -> 加 Scripts/
```

---

## §2 Skill Creator & 六步创建流程

### 2.1 六步流程

```text
Step 1: 理解 (Understand) — 明确用例和触发词
Step 2: 规划 (Plan) — 需要哪些资源
Step 3: 初始化 (Initialize) — 运行 init_skill.py 生成模板
Step 4: 编辑 (Edit) — 写 SKILL.md + 添加资源
Step 5: 验证 (Validate) — 运行 quick_validate.py
Step 6: 迭代 (Iterate) — 使用中发现问题 -> 改进
```

### 2.2 Skill 目录结构规范

```text
skill-name/
+-- SKILL.md          # 必须 — YAML 头部 + Markdown 正文
+-- scripts/          # 可选 — 可执行脚本
+-- references/       # 可选 — 大型参考文档（>500行时）
+-- assets/           # 可选 — 输出用模板
```

### 2.3 description 触发机制关键

好 description 三要素：**做什么 + 什么时候用(触发词) + 什么时候不用(反例)**

```yaml
# ✅ 好 description
description: "BMC 固件交叉编译与刷写 — 支持 OpenBMC/Yocto 构建流程。
  Use when: (1) 编译 BMC 镜像, (2) 配置 OpenBMC 构建环境, (3) 调试 bitbake 编译错误。
  Do NOT use: 通用嵌入式 Linux 编译、非 BMC 场景的 Yocto 编译。"

# ❌ 坏 description
description: "BMC 操作"
```

---

## §3 好 Skills 的特征：七维评估矩阵

| 维度 | 标准 | 自检问题 |
|:-----|:------|:---------|
| 🎯 **精准触发** | description 清晰区分"何时用/何时不用" | 能否给出一组测试用例全部正确命中/不命中？ |
| 📏 **单一职责** | 一个 Skill 只做一类事 | 能否用一句话说清做什么？ |
| 🔬 **具体可执行** | 指令是动作不是概念 | 每条指令是否以动词开头？ |
| ✅ **可验证** | 明确的 pass/fail 标准 | "代码质量高" ❌ → "无 ESLint 错误" ✅ |
| 📐 **不超过 7±2 条** | 主规则不超过 7 条 | 超了则分层 |
| 🔗 **有触发边界** | 明确 Do/Do NOT | 列出"什么情况下不要用" |
| ♻️ **可迭代** | 版本号和 changelog | 标注版本 + 变更记录 |

### 硬件 Skill 的特殊要求

| 硬件领域特点 | 对 Skill 的要求 |
|:------------|:---------------|
| 涉及物理设备 | **必须有安全红线**（"禁止直接写寄存器"、"必须先模拟验证"） |
| 数据来源多样 | 必须指定数据源优先级（官方文档 > 实测 > 推算） |
| 操作不可逆 | 破坏性操作前加确认步骤 |
| 量化指标关键 | 所有性能断言必须有「数值 + 单位 + 基线 + 条件」四要素 |

---

## §4 服务器硬件领域可 Skills 化的全景图

### P0（高价值 + 高频 + 知识密集）

| 方向 | 知识库参考 | 可参考 GitHub 项目 |
|:-----|:----------|:-----------------|
| BMC/IPMI 故障诊断 | `fault-diagnosis` Skill | bmc-adapters, OpenBMC |
| 超节点存储方案设计 | 存储需求培训材料 | SPDK, DOCA 示例 |
| GPU 集群训练排障 | knowledge/02_rd 目录 | DCGM, cluster-smi, GPU-Health-eXpert |
| RAS 可靠性分析 | knowledge/02_rd/06_O&M | rasdaemon, mcelog |
| NVMe 存储性能分析 | 存储培训材料 | fio, SPDK, nvme-cli |

### P1（中价值 + 周期性出现）

| 方向 | 知识库参考 |
|:-----|:----------|
| 信号完整性分析 | knowledge/02_rd |
| 散热方案设计 | knowledge/07_industry-research |
| 固件编译环境 | OpenBMC/Yocto |
| 互联架构分析（UALink/CXL/PCIe） | knowledge/07_industry-research |
| 竞品分析报告 | `server-competitor-analysis` Skill |

### P2（有潜力但频率低）

| 方向 | 说明 |
|:-----|:------|
| 功耗建模与 PUE 估算 | 整机能耗估算、Power Capping |
| 供电架构分析 | 800V HVDC/48V/12V |
| CXL 内存池配置 | Beluga 方案、内存池规模规划 |
| 数据中心级监控集成 | Prometheus + DCGM + Grafana |

---

## §5 GitHub 硬件相关开源项目（扩展篇）

> 基于 GitHub 搜索 + 已知开源生态，按 Skills 化方向分类整理。

### 5.1 BMC/IPMI/Redfish 管理工具链

| 项目 | ⭐ | 语言 | 说明 | Skills 化方向 |
|:-----|:-:|:----|:-----|:-------------|
| [OpenBMC/openbmc](https://github.com/openbmc/openbmc) | 1.3k | C/Python | 开源 BMC 固件框架 | BMC 编译/配置/调试 Skill |
| [KVMFleet/bmc-adapters](https://github.com/KVMFleet/bmc-adapters) | 1 | Python | 异步 Redfish/iDRAC/iLO/Supermicro 管理 | 带外管理统一接口 Skill |
| [vpatelsj/dc-simulator](https://github.com/vpatelsj/dc-simulator) | 1 | Shell/Docker | 数据中心模拟器（BMC+IPMI+Redfish+PXE） | 数据中心模拟测试 Skill |
| [jacobweinstock/bmctool](https://github.com/jacobweinstock/bmctool) | 2 | Go | BMC CLI 交互工具 | BMC 快速诊断 CLI Skill |
| [StainlessSteve/redfish-rs](https://github.com/StainlessSteve/redfish-rs) | — | Rust | Redfish API Rust 客户端 | Redfish API 调用 Skill |
| [tblakex01/mcp_troubleshooter](https://github.com/tblakex01/mcp_troubleshooter) | 1 | Python | MCP Server 故障诊断 | 服务器故障诊断 MCP 后端 |
| [nsfcac/OpenHPC-BMC-MAC](https://github.com/nsfcac/Automating-the-scale-up-process-in-OpenHPC) | 8 | Python | 通过 Redfish/IPMI 自动采集 MAC 地址 | 数据中心自动化上架 Skill |

### 5.2 GPU 集群监控与诊断

| 项目 | ⭐ | 语言 | 说明 | Skills 化方向 |
|:-----|:-:|:----|:-----|:-------------|
| [NVIDIA/DCGM](https://github.com/NVIDIA/DCGM) | 2k | C/Go | NVIDIA 数据中心 GPU 管理器 | GPU 集群健康检查 Skill |
| [msalvaris/gpu_monitor](https://github.com/msalvaris/gpu_monitor) | 163 | Python | GPU 集群监控（InfluxDB+Grafana） | GPU 监控部署 Skill |
| [FanKang2021/GPU-Health-eXpert](https://github.com/FanKang2021/GPU-Health-eXpert) | 86 | C | GPU 健康诊断（覆盖 86 星~） | GPU 诊断 Skill |
| [PatWie/cluster-smi](https://github.com/PatWie/cluster-smi) | 84 | Go | 整个 GPU 集群的 nvidia-smi | 集群 GPU 状态查询 Skill |
| [eBay/nvidiagpubeat](https://github.com/eBay/nvidiagpubeat) | 55 | Go | Elastic Beat GPU 指标采集 | GPU 指标接入 ES Skill |
| [whats2000/nvnodetop](https://github.com/whats2000/nvnodetop) | 6 | Shell | 无需 sudo 的节点 GPU 监控 | 轻量 GPU 监控 Skill |
| [deepaksatna/LLM-Observability-Stack](https://github.com/deepaksatna/LLM-Observability-Stack) | 7 | Python | LLM 训练/推理可观测栈 | LLM 训练监控 Skill |

### 5.3 存储性能基准与 NVMe 工具

| 项目 | ⭐ | 语言 | 说明 | Skills 化方向 |
|:-----|:-:|:----|:-----|:-------------|
| [spdk/spdk](https://github.com/spdk/spdk) | 3.2k | C | 存储性能开发套件（用户态 NVMe 驱动） | NVMe 性能基准 Skill |
| [axboe/fio](https://github.com/axboe/fio) | 5.2k | C | 灵活的 I/O 测试工具 | 存储性能测试 Skill |
| [linux-nvme/nvme-cli](https://github.com/linux-nvme/nvme-cli) | 1.5k | C | NVMe 命令行管理工具 | NVMe 设备管理 Skill |
| [timoheimonen/macOS-memory-benchmark](https://github.com/timoheimonen/macOS-memory-benchmark) | 17 | C | 内存带宽/延迟微基准测试（可移植 Linux） | 内存性能基准 Skill |

### 5.4 服务器/数据中心模拟

| 项目 | ⭐ | 说明 | Skills 化方向 |
|:-----|:-:|:-----|:-------------|
| [vpatelsj/dc-simulator](https://github.com/vpatelsj/dc-simulator) | 1 | 仿真 BMC+IPMI+Redfish+PXE 服务 | 数据中心仿真测试 Skill |
| [Xuan-yangyi/Serial_ssh_bridge](https://github.com/Xuan-yangyi/Serial_ssh_bridge) | 5 | 通过 SSH 连接硬件串口调试 | 串口调试 Skill |
| [piyushbag/awesome-pcb-workflow](https://github.com/piyushbag/awesome-pcb-workflow) | 10 | PCB 设计工作流 + AI EDA | 参考其工具链组织方式 |
| [ManishSkr/Agentic_RTL_Coder](https://github.com/ManishSkr/Agentic_RTL_Coder) | 3 | AI 生成 Verilog RTL 代码 | 硬件 AI 编码参考 |

### 5.5 系统监控与可观测性

| 项目 | ⭐ | 说明 | Skills 化方向 |
|:-----|:-:|:-----|:-------------|
| [netdata/netdata](https://github.com/netdata/netdata) | 72k | 实时系统健康监控 | 系统健康监控 Skill |
| [prometheus/node_exporter](https://github.com/prometheus/node_exporter) | 11k | 主机指标采集 | 服务器指标采集 Skill |
| [nicolargo/glances](https://github.com/nicolargo/glances) | 27k | 跨平台系统监控 | 快速系统状态 Skill |
| [munin-monitoring/munin](https://github.com/munin-monitoring/munin) | 2k | 网络资源监控 | 服务器资源趋势分析 Skill |

### 可重复利用的开源 Skill（本工程已有）

| Skill | 类型 | 说明 |
|:------|:-----|:------|
| `fault-diagnosis` | 已安装 | 系统化故障排查方法论 |
| `server-competitor-analysis` | 已安装 | 服务器三维竞品分析 |
| `knowledge-doc-writer` | 已安装 | 深度技术文档创建 |
| `arch-presentation-builder` | 已安装 | 架构评审汇报材料 |
| `open-source-skill-packer` | 已安装 | 将 GitHub 开源项目封装为 Skill |

---

## §6 基于本地知识库的 Skills 编写方法（借鉴 spec 方法论体系）

### 6.1 核心思想：从模式提取到 Skill 固化

```text
本地知识库 (knowledge/)     spec/ 方法论体系 (9 meth+)
        |                           |
        v                           v
  模式提取                   设计模式借鉴
  (重复性任务识别)           (36种设计模式)
        |                           |
        +-------+-------------------+
                v
          Skill 固化
    (SKILL.md + Scripts)
```

本工程的 `spec/` 目录下有 **9 个 meth- 方法论文档 + 7 个 design- 设计文档 + 8 个 sr- 需求文档**，从中提取了 **5 种** Skills 编写方法：

### 6.2 方法一：知识库模式提取法（借鉴 meth-006）

**核心**: meth-006 定义 36 种知识库搭建设计模式（6 类）。其中的 **E-01 (Skills + Scripts 职责分离)**、**A-01 (14 类任务分类处理框架)**、**G-02 (五类写入策略)** 可直接指导 Skill 设计。

**操作步骤**:

```text
Step 1: 扫描知识库 -> 识别高频任务模式
  $ grep -l "故障\|诊断\|排查" knowledge/02_rd/*.md  # 找故障模式
  $ grep -l "带宽\|延迟\|吞吐" knowledge/01_survey/*.md  # 找性能数据

Step 2: 归类 -> 同类任务聚合（参考 meth-006 A-01 14 类分类）
  - 诊断类 -> 用 E-01 模式：Skill 负责工作流 + Script 负责检测
  - 分析类 -> 用 A-03 模式：质量门禁 + 分级输出

Step 3: 提取通用流程 -> 参数化 -> 写 SKILL.md
  - 固定步骤 -> 写为指令
  - 变化部分 -> 定义为参数（$BMC_IP, $DEVICE）

Step 4: 验证 -> 用全新场景测试
```

**适用场景**: 知识库中已有丰富的领域知识，需要打包为可复用 Skill。

### 6.3 方法二：两阶段生产法（借鉴 meth-009）

**核心**: meth-009 定义「自由生成 → 集中维护」两阶段。对应到 Skill 编写：

**第一阶段：自由生成（聚焦内容质量）**

```text
保留的约束（质量线）:
  ✅ 逻辑 MECE、数据有出处、格式规范
  ✅ 安全红线（硬件必加）
  ✅ 可验证的 pass/fail 标准

忽略的约束（维护事务，第二阶段做）:
  ❌ 不要想着一次写完美
  ❌ 不要预先考虑与其他 Skill 的冲突
  ❌ 不要琢磨 index/目录放置
```

**第二阶段：集中维护（批量处理）**

```text
用脚本检查+修复:
  1. check-description-conflict.py  — 检查 description 冲突
  2. check-skill-format.py          — 检查 YAML/Markdown 格式
  3. fix-index-skill.py             — 自动注册到 skill 索引
```

**适用场景**: 需要快速产出多个 Skill，不求一次完美，允许迭代。

### 6.4 方法三：Skills-Scripts 双引擎设计（借鉴 design-007）

**核心**: design-007 定义 **125 Skills + 154 Scripts** 的双引擎架构。Skill 负责「做什么」的推理，Script 负责「怎么算」的确定性。

**映射关系类型**:

```text
类型 A: Skill 直接调用 Script
  例: "NVMe 基准测试 Skill" -> 调用 scripts/nvme-benchmark.py

类型 B: Skill 包含内联脚本（适合小型操作）
  例: SKILL.md 中直接写 bash/python 代码块

类型 C: Skill 指导 AI 手动操作（无脚本）
  例: "架构分析 Skill" -> AI 推理为主
```

**判断标准**:

| 放入 Script | 留在 SKILL.md |
|:------------|:--------------|
| 需要确定性结果 | 指导性/分析性任务 |
| 反复执行的重复操作 | 一次性决策流程 |
| 需要精确计算 | 知识性内容 |
| 复杂参数组合 | 简单模板输出 |

**适用场景**: 需要将任务拆分为「AI 推理部分」和「确定性执行部分」的复合 Skill。

### 6.5 方法四：SSOT 治理约束法

**核心**: 从本工程的约束注册表（sr-003, 87 条 CCLRR 约束）和 SSOT 治理体系（meth-003）提取的 Skill 编写原则。

**8 条硬规则**:

```text
1. 🔴 头部注解 — SKILL.md 必须有 YAML frontmatter
2. 🔴 不重复造轮子 — 搜索已有 Skill，复用或扩展
3. 🟡 description 唯一 — 不与已有 Skill 的触发词重叠
4. 🟡 版本标记 — 每次更新更新版本号和 changelog
5. 🟡 量化断言 — 所有性能数据必须有「来源+基线+条件」
6. 🟢 不超过 500 行 — >500 行拆分为 references/
7. 🟢 测试例 — 至少 3 个测试输入输出对
8. 🟢 交叉链接 — 引用知识库相关文档
```

### 6.6 方法五：会话记录挖掘法

**核心**: 从 `conversation-log/` 和 `memory/` 中挖掘重复模式。

**自动化挖掘流程**:

```bash
# Step 1: 找出高频主题
grep -c "BMC\|IPMI\|RAS\|ECC\|故障" conversation-log/*.md | sort -t: -k2 -rn | head -10

# Step 2: 提取重复命令序列
grep -A3 -B1 "ipmitool\|nvidia-smi\|fio\|nvme" memory/2026*.md > tmp/pattern-candidates.txt

# Step 3: 参数化 → 写 Skill 草案
# Step 4: 测试 → 用新类似问题验证复用性
```

**适用场景**: 已有大量会话记录但知识库尚未覆盖的新领域。

### 6.7 六种方法的选择决策树

```text
你的场景是什么？
|
+- 知识库已有丰富内容，需打包 -> 方法一（模式提取法）
|
+- 需要从 0 快速产出多个 Skill -> 方法二（两阶段法）
|
+- 任务有确定性操作（命令/Script）-> 方法三（双引擎法）
|
+- 需要严格质量控制 -> 方法四（SSOT 约束法）
|
+- 有大量会话记录但无知识沉淀 -> 方法五（会话挖掘法）
|
+- 复合场景 -> 方法组合：
    方法四(约束) -> 方法一(提取) -> 方法三(脚本化) -> 方法二(迭代)
```

### 6.8 实操案例：从知识库中提取超节点存储设计 Skill

**知识库内容**: `knowledge/03_AI/train/supernode-storage-requirements-training/README.md`
**源方法**: 方法一（模式提取法）+ 方法三（双引擎法）

**Step 1：扫描知识库找模式**:

```text
高频模式识别:
  "BF3 vs BF4 对比" — 出现了十几次
  "带宽计算" — 多处重复的计算公式
  "场景评估" — 相同的评估矩阵结构
```

**Step 2：提取通用流程**:

```text
固定的决策流程:
  1. 输入系统参数（GPU 数、模型大小、KV Cache 量）
  2. 计算带宽需求
  3. 匹配 BF3/BF4 方案
  4. 输出推荐配置

可参数化的变量:
  GPU 数、节点数、模型大小、KV Cache 大小、Checkpoint 窗口
```

**Step 3：设计 Skill 结构**:

```yaml
name: supernode-storage-design
description: "超节点存储方案设计决策
  Use when: (1) 设计超节点存储架构, (2) 对比 BF3/BF4 方案,
  (3) 评估 JBOF 规划, (4) 计算存储带宽需求。
  Do NOT use: 单机存储方案、纯软件定义存储。"
```

**Step 4：Scripts 设计（双引擎）**:

```bash
scripts/storage-bandwidth-calc.py  # 确定性：带宽计算
scripts/jbof-sizer.py              # 确定性：JBOF 数量估算
# SKILL.md 负责：方案选择推理、架构权衡分析
```

---

## §7 针对 Trae 的 Skills 编写方法（基于本工程 125+ Skills 经验）

### 7.1 Trae 的 Skills 局限与四种弥补策略

Trae 作为字节跳动的 AI 编程 IDE，其 Skills 机制**轻于 CowAgent**：

| 能力 | CowAgent | Trae |
|:-----|:---------|:-----|
| 正式 Skill 系统 | ✅ 125 Skills (SKILL.md) | ❌ 不支持 |
| 自动触发 (description) | ✅ | ❌ 需手动引用 |
| 可执行脚本 | ✅ Scripts/ 目录 | ✅ 可在项目中放脚本 |
| 项目级规则 | AGENT.md + RULE.md | ✅ `.trae/rules/` |
| 常驻规则 | ✅ 系统级 | ⚠️ Custom Instructions |

**四种弥补策略**:

### 7.2 策略一：Custom Instructions 常驻规则法

适用于：需要在 Trae 所有对话中生效的通用约束。

```text
操作路径: Trae -> 设置 -> AI -> Custom Instructions -> 编辑

模板（硬件开发场景）:
"""
## 🎯 角色设定
你是服务器硬件领域的资深 AI 工程师。所有回答需基于工程数据，
给出「数值+单位+基线+条件」的四要素断言。

## 🔴 安全红线
1. 涉及寄存器写入操作必须先提问确认
2. 固件刷写前必须校验 checksum
3. 所有硬件操作建议必须有实验验证步骤

## 📐 代码规范
1. 每函数 ≤ 30 行，必须有错误处理
2. 所有硬件相关代码必须有注释说明寄存器地址/位域
3. 优先使用 Python 或 Rust，避免 C++

## 📊 测试要求
1. 硬件抽象层必须有 Mock 测试
2. 每次提交前运行 `make check`
3. 测试覆盖率 ≥ 80%
"""
```

### 7.3 策略二：.trae/rules/ 项目规则矩阵法

适用于：特定项目约束，只在本项目生效。

```text
项目根目录/.trae/rules/
+-- hardware-rules.md      # 硬件项目通用规则（常驻）
+-- bmc-rules.md           # BMC 固件开发专用（按需触发）
+-- storage-rules.md       # 存储性能测试专用（按需触发）
+-- gpu-cluster-rules.md   # GPU 集群训练规则（按需触发）
+-- README.md              # 规则使用说明
```

**规则文件模板** (`.trae/rules/hardware-rules.md`):

```markdown
# 硬件项目规则 v1.0

## 编码规范
1. 🔴 所有寄存器操作必须有 bit-field 注释
2. 🔴 敏感配置项（频率/电压/时序）必须校验范围
3. ⚠️ 接口定义优先使用 Protocol Buffers
4. 💡 多线程场景使用 `std::atomic` 而非 `volatile`

## 测试规范
1. ⚠️ 硬件抽象层必须有 Mock 测试
2. ⚠️ 每次提交前运行 `make check && make test`
3. 💡 性能敏感代码基准测试纳入 CI

## 文档规范
1. ⚠️ 每个模块必须有 README 列出硬件依赖
2. 💡 API 文档使用 Doxygen 格式
3. 💡 寄存器映射表放在单独 .md 文件

## 安全红线
1. 🔴 禁止直接操作生产环境设备
2. 🔴 不能自动执行固件刷写
3. 🔴 电压/时序修改必须经硬件团队审核
```

### 7.4 策略三：多阶段 Pipeline 注入法

适用于：复杂硬件开发任务，需要分阶段注入不同规则。

借鉴工程中 AI Production Pipeline 的设计（pipeline-orchestrator 的 6 阶段编排），在 Trae 中手动分阶段注入：

```text
阶段 1 — 需求分析:
  -> 注入 hardware-rules.md（通用规则）
  -> 输出: 需求文档

阶段 2 — 架构设计:
  -> 注入 + architecture-design-rules.md
  -> 输出: 架构图 + 接口定义

阶段 3 — 编码实现:
  -> 注入 + bmc-rules.md（BMC 专用）
  -> 输出: 代码 + 测试

阶段 4 — 审查:
  -> 注入 + review-rules.md
  -> 输出: 审查报告
```

用户只需在每次阶段转换时告诉 Trae：

> "现在进入架构设计阶段，请加载 .trae/rules/architecture-design-rules.md 的规则。"

### 7.5 策略四：Open-Source-Skill-Packer 封装法

适用于：将 GitHub 上的硬件相关开源项目封装为 Trae 中可复用的交互模板。

**操作流程**:

```text
Step 1: 找项目 — GitHub 上搜索与硬件任务匹配的开源工具
  -> 如 [cluster-smi](https://github.com/PatWie/cluster-smi) 适合 GPU 集群状态查询

Step 2: 提取使用模式 — 分析项目的典型使用方法

Step 3: 封装为 Trae 规则文件
  -> 写入 .trae/rules/gpu-cluster-check.md

Step 4: 添加交互模板
  -> 在规则中加入典型的用户说->AI 做的映射
```

**示例 — 封装 cluster-smi 为 GPU 集群检查 Skill**:

```markdown
# GPU 集群状态检查规则 v1.0
# 来源: https://github.com/PatWie/cluster-smi

## 触发条件
当用户说以下内容时激活此规则：
- "检查 GPU 集群状态"
- "所有 GPU 是否正常"
- "GPU 集群健康检查"

## 执行流程
1. 运行 `cluster-smi` 查看全集群 GPU 状态
2. 检查是否有 GPU 处于 "OFF" 或 "FAILED" 状态
3. 提取异常 GPU 的节点名、设备索引
4. 生成集群健康报告（正常/异常/离线计数）

## 输出格式
```json
{
  "total_gpus": 256,
  "healthy": 254,
  "degraded": 1,
  "offline": 1,
  "details": [
    {"node": "gpu-12", "gpu_idx": 3, "status": "Degraded", "cause": "ECC threshold exceeded"},
    {"node": "gpu-07", "gpu_idx": 0, "status": "Offline", "cause": "NVLink error"}
  ]
}
```

```text

### 7.6 Trae 技能编写的质量门禁

借鉴工程中的 `sr-007-content-quality-standards.md`（8 级质量分级）和 `meth-007-ai-detail-precision-control.md`（AI 细节精控），Trae 规则文件的质量门禁：

| 级别 | 要求 | 适用 |
|:-----|:------|:-----|
| **L1** 🛑 | 安全红线 — 绝不可能被覆盖 | 所有硬件规则 |
| **L2** ⚠️ | 必须遵守 — 违反即有明确后果 | 编码规范、测试要求 |
| **L3** 💡 | 最佳实践 — 建议遵守 | 文档格式、命名约定 |
| **L4** ℹ️ | 参考信息 — 仅提供上下文 | 技术背景、术语解释 |

**自检清单（每次创建规则文件后检查）**:
```

□ 所有 🔴 红线是否真正不可绕过？
□ ⚠️ 警告是否可验证（是否有明确 pass/fail 标准）？
□ 💡 建议是否真的有益（不是噪音）？
□ 是否超过 30 条规则？（超了分多个文件）
□ 是否有和其他规则文件的冲突？

```text

---

## §8 Skill 样例库（扩展至 8 个）

### 8.1 BMC 固件交叉编译

```yaml
name: bmc-firmware-build
description: "BMC 固件交叉编译与刷写 — 支持 OpenBMC/Yocto 构建流程。
  Use when: (1) 编译 BMC 镜像, (2) 配置 OpenBMC 构建环境,
  (3) 调试 bitbake 编译错误, (4) 刷写 BMC 固件。
  Do NOT use: 通用嵌入式 Linux 编译。"
metadata:
  requires: { bins: ["git", "docker"], env: ["BMC_SDK_PATH"] }
  emoji: 🔧
---
工作流: 环境检查 → 拉取源码 → 配置目标 → bitbake → 固件打包 → 刷写
```

### 8.2 NVMe SSD 性能基准测试

```yaml
name: nvme-performance-benchmark
description: "NVMe SSD 性能基准测试 — fio/SPDK 两种模式。
  Use when: (1) 新硬盘性能摸底, (2) 对比 SSD 型号, (3) 验证 RAID 影响。
  Output: 标准化报告（带宽/IOPS/延迟分位数）。"
metadata:
  requires: { bins: ["fio", "nvme-cli"] }
  emoji: 💾
---
测试维度: 4K随机读/写 → 128K顺序读/写 → 混合读写
输出: JSON 格式报告，包含带宽/IOPS/P50/P99/P999
```

### 8.3 服务器 RAS 故障诊断

```yaml
name: server-ras-diagnosis
description: "服务器 RAS 故障诊断 — ECC 错误、PCIe 错误、内存 CE/UE、CPU 故障。
  Use when: (1) 报 ECC/PCIe 错误, (2) UE/CE 计数增长, (3) RMA 判定。
  Do NOT use: 通用 Linux 系统故障。"
metadata:
  requires: { bins: ["ras-mc-ctl", "mcelog", "edac-util"] }
  emoji: 🩺
---
五步诊断: 收集症状 → 匹配模式 → 确定测试 → 定位根因 → 处理建议
```

### 8.4 超节点存储方案设计

```yaml
name: supernode-storage-design
description: "超节点存储方案决策设计 — 从系统指标到硬件选型的映射。
  Use when: (1) 存储架构设计, (2) BF3/BF4/IPU 方案对比,
  (3) 需求规格制定, (4) DOCA/SPDK 软件栈评估。
  Do NOT use: 单机存储、纯软件定义存储。"
metadata:
  requires: { bins: ["python3"] }
  emoji: 🗄️
---
决策流: 指标梳理 → 方案选择 → 需求优先级 → 测试计划
```

### 8.5 GPU 集群健康检查 ⭐

```yaml
name: gpu-cluster-health-check
description: "GPU 集群健康检查 — 基于 DCGM/cluster-smi/nvidia-smi。
  Use when: (1) 例行 GPU 集群巡检, (2) 训练前健康预检,
  (3) 排查 GPU 异常（ECC/Power/NVLink）, (4) 生成集群健康报告。
  Do NOT use: 单 GPU 诊断、应用层性能分析。"
metadata:
  requires: { bins: ["nvidia-smi", "dcgmi"] }
  emoji: 🖥️
---
检查清单:
  1. 全集群 GPU 状态（nvidia-smi -L / cluster-smi）
  2. ECC 错误计数（nvidia-smi -q -d ECC）
  3. NVLink 健康（nvidia-smi nvlink --status）
  4. GPU 温度/功耗（nvidia-smi -q -d TEMPERATURE）
  5. DCGM 诊断（dcgmi diag -r 1-3）
输出: JSON 报告，包含健康评分+异常列表
```

### 8.6 网络互联架构分析（UALink/CXL/PCIe）⭐

```yaml
name: interconnect-architecture-analysis
description: "服务器互联架构分析 — UALink/CXL/PCIe/NVLink 方案对比。
  Use when: (1) 对比不同互联方案, (2) 评估拓扑设计,
  (3) 分析延迟/带宽瓶颈, (4) 制定互联演进路线。
  Do NOT use: 单组件规格查询（用数据查询）。"
metadata:
  emoji: 🔗
---
分析维度:
  1. 协议对比（延迟/带宽/拓扑/生态）
  2. 超节点四网中的位置（计算网/存储网/管理网/同步网）
  3. 与 GPU/NIC/DPU 的搭配
  4. 当前瓶颈与演进路径
```

### 8.7 训练任务 Hang 排查 ⭐

```yaml
name: training-hang-diagnosis
description: "分布式训练任务 Hang/超慢排查 — NCCL timeout/通信 hang。
  Use when: (1) 训练进程 hang 住, (2) NCCL 报 timeout,
  (3) 训练速度突然下降, (4) 多机训练卡在某步。
  Do NOT use: 单机训练故障、推理引擎问题。"
metadata:
  requires: { bins: ["nvidia-smi", "nccl-tests", "ipmitool"] }
  emoji: ⏳
---
排查流程:
  L1: 进程状态（ps/gpu-util/NCCL 环境变量）
  L2: 网络状态（NIC/IB/RDMA 计数器）
  L3: 存储状态（IO hang 检查）
  L4: 系统日志（dmesg/内核日志）
  L5: NCCL Debug 模式复盘
```

### 8.8 服务器功耗建模与 PUE 估算 ⭐

```yaml
name: server-power-modeling
description: "服务器功耗建模与 PUE 估算 — 基于组件规格的能耗计算。
  Use when: (1) 估算整机功耗, (2) 对比散热方案能效,
  (3) Power Capping 策略, (4) 数据中心 PUE 预估。
  Do NOT use: 实测功耗分析（用 IPMI 传感器）。"
metadata:
  requires: { bins: ["python3"] }
  emoji: ⚡
---
计算模型:
  总功耗 = Σ(GPU × N) + CPU + Memory + NIC + Disk + Misc
  PUE ≈ 总输入功率 / IT 设备功率
  Power Capping 建议 = (GPU TDP × 利用率 × 节点数) × 1.2
```

---

## §9 从对话日志提取 Skill 的工业级工作流

### 9.1 自动化脚本辅助的提取流程

**Step 1: 扫描会话记录找高频模式**

```bash
# 找高频技术关键词
grep -oP "(BMC|IPMI|RAS|ECC|NCCL|SPDK|NVMe|fio)" conversation-log/*.md | \
  sort | uniq -c | sort -rn | head -15

# 找重复问题模式
grep -c "^用户.*故障\|^用户.*问题\|^用户.*排查" memory/2026*.md
```

**Step 2: 提取 AI 回答中的固定序列**

```text
从对话中提取的固定操作序列:
  1. ipmitool sel list -> 获取 SEL 日志
  2. grep CE/UE -> 分类错误类型
  3. ras-mc-ctl --errors -> 确认位置
  4. 匹配故障模式库 -> 定位根因
  5. 给出处理建议 -> 记录到 memory
```

**Step 3: 参数化 → 生成 SKILL.md**

### 9.2 skill-evolver：自进化机制的应用

本工程中的 `skill-evolver` 和 `evolver` Skill 展示了**技能自进化**的理念：

```text
Skill 使用 -> 记录失败模式 -> 分析短板 -> 优化 -> 新版本
```

在 Trae 场景下，可以通过定期审查 `.trae/rules/` 文件的使用效果来实现类似的自进化：

```bash
# 每月检查规则文件命中率
grep -c "加载.*rules" conversation-log/*.md | sort -t: -k2 -rn

# 低命中率的规则 → 删除或合并
# 高误触发的规则 → 优化触发条件
```

### 9.3 Skill 生命周期管理

借鉴 design-007 中 125 Skills 的管理经验，为本地 Skill 建立生命周期：

| 阶段 | 状态 | 动作 |
|:-----|:-----|:------|
| **起草** | Draft | 在 `skills/` 下的 `_drafts/` 目录 |
| **可用** | Active | 注册到系统，description 常驻 |
| **需要审查** | Review | 运行审计脚本，检查 7 维度 |
| **废弃** | Deprecated | 移到 `_archive/`，保留 description 指向替代 Skill |
| **删除** | Deleted | 确认无引用后，`mv tmp/bak/` |

### 9.4 125 Skills 实践的经验教训

基于本工程 125 Skills 的真实运行经验：

| # | 经验教训 | 数据支持 |
|:-:|:---------|:---------|
| 1 | **description 精准度 > 内容深度** | 触发偏差是最大的 Token 浪费 |
| 2 | **一个 Skill 只做一类事** | 多职责 Skill 的维护成本呈指数增长 |
| 3 | **有脚本的 Skill 比纯推理 Skill 可靠** | Skills+Scripts 的可靠性是纯推理的 2-3× |
| 4 | **定期审计 vs 技能膨胀** | 不审计的 Skills 半年内 30% 会过时 |
| 5 | **从对话中提取的 Skill 最实用** | 源自有真实需求的 Skill 存活率 > 80% |
| 6 | **不要将一次性任务写成 Skill** | 一次性的 Skill 一写就废弃，零收益 |
| 7 | **Skill 也需要版本管理** | 无版本的 Skill 无法回滚，出问题难定位 |
| 8 | **创建前必须查重** | knowledge-sync 与已有 Skill 重叠 80%，维护成本翻倍 |
| 9 | **草稿 Skill 必须注册** | 3 个未注册 Skill 永远无法被系统识别，零触发 |
| 10 | **跨进程约束必须硬编码** | tasks.json 覆写事件：软约束在调度器面前形同虚设 |

### 9.5 本工程 7 个对话案例精粹

以下案例来自本工程 2026-07 的真实运行记录，与 skills-creation-from-conversation-analysis.md 中的完整分析对应，此处做培训化提炼。

#### 案例 ①：server-competitor-analysis — 有方法论还翻车（P0 级教训）

```text
背景: 用户要求基于已有的方法论文档创建竞品分析 Skill
翻车: 初版引用了方法论框架但没有严格遵循其步骤
       -> 用户说"初版效果与方法论差距极大"
根因: 方法论文档在引用时被"软化"了
修复: 在 SKILL.md 中显式写出"必须严格按方法论 §X 执行"
       + 步骤中加入检查点: "完成步骤 2 后，对照方法论 §3 验证覆盖率"
       + 输出加 QC 报告: "方法论遵循度自检表"

🔑 教训: 有方法论文档 ≠ Skill 会自动遵循。
        必须将方法论执行检查点显式嵌入 SKILL.md。
```

#### 案例 ②：discover Skill — 从管线碎片到标准化 Skill

```text
背景: 多次对话中开发了 discover/ 批量化知识加工管线
问题: 翻看多次记录，同一管线的执行方式每次都不同
       -> 有时 5 步，有时跳 2 步，输出格式不统一，错误处理各异
修复: 从多次翻车中提取"最佳实践序列" -> 固化为 7 步标准管道

🔑 教训: 跨越多次对话的碎片化工作流，
        只有系统化提取"做过的最佳路径"才能标准化。
        Skill = 最佳实践集合，不是设计文档。
```

#### 案例 ③：32 个废弃 Skill 批量生命周期终结

```text
发现: skills/ 下有 32 个 Skill 从未触发或已被替代
处置: 移入 _archive/，从 skills_config.json 移除
收益: 节省 ~10-13K tokens 系统 prompt 空间
       ≈ 每天减少 ¥1.5-2 的 token 成本

废弃原因分布:
  - 50% 被新 Skill 替代（如多个 discover Skill -> 统一一个）
  - 20% 逻辑已硬编码到代码（变为脚本化 CI check）
  - 15% 需求不再存在
  - 15% 从未被使用（实验性创建后未注册）

🔑 教训: 一次成功 Skill 生态治理 =
        新增 + 优化 + 废弃，三者缺一不可。
```

#### 案例 ④：用户问题分析 — AI 自主感知可 Skill 化信号

```text
背景: 用户说"帮我分析用户问题数据"，没提创建 Skill
执行过程:
  第 1 次 -> AI 从零构思分析框架
  第 2 次 -> 发现又是同样的数据读取->维度提取->分布统计
  第 3 次 -> 自主创建分析模板 Skill 草稿（不等用户说）
  之后   -> 每次调用草稿，输出格式一致，可跨期对比

🔑 教训: 什么时候该创建 Skill？
        不是等用户说"帮我做个 Skill"，
        而是第 2 次做同类任务时就自主感知到"这活儿值得 Skill 化"。
```

#### 案例 ⑤：knowledge-sync — 创建前没有查重的代价

```text
问题: 创建了 knowledge-sync Skill，功能覆盖 80%
      与 knowledge-health-check + knowledge-index-manager 重叠
根因: 创建前没做 grep 查重、没看已有 Skill 的 description
后果: 多余维护成本，增加检索噪声

🔑 教训: 创建任何 Skill 前的必做查重：
        grep -rl "<关键词>" skills/*/SKILL.md
        grep "<触发词>" skills_config.json
```

#### 案例 ⑥：weekly-report-generator — 迭代进化的四次浪潮

```text
v0 (碎片): AI 每次手动生成周报，输出格式每期不同，耗时 ~30min
v1 (Skill化): 创建 SKILL.md，固定结构，耗时降至 ~15min
v2 (时间窗口): 发现窗口定义错误（全天制->上一日08:00->当日08:10）
v3 (三支柱): 解决输出混杂问题，定型为 3 支柱结构 + 3 个配套脚本
v4 (计划): 链接路径自动化、memory 关联

🔑 教训: 迭代进化判断标准：
        效果差距 < 50% 工作量 -> 优化（路径④）
        效果差距 > 50% 工作量 -> 重建（路径①）
```

#### 案例 ⑦：spec-consistency-checker — 有意识创建但缺最后一公里

```text
过程: 在执行 spec 治理任务时，发现每次都要做相同检查
       在第 2 次做同类检查时识别到可 Skill 化信号
       创建草稿 + 5 个检测脚本（共 914 行代码）

          然而——没有注册到 skills_config.json
          系统 dispatch 引擎不识别，永远无法自动触发

🔑 教训: 有意识创建的草稿 -> 必须在草稿转正式时
       加入"注册检查"步骤，否则草稿永远是游离状态。
```

### 9.6 Skill 失效模式与对策

> **来源**: 本工程 t08 深度分析 + `scheduler/tasks.json` 覆写事件 + `constraint-verifier` A-J 十类失效体系

#### 9.6.1 两大失效根源

| 根源 | 表现 | 典型链路 | 轻量测试方法 |
|:-----|:-----|:---------|:------------|
| **上下文丢失** | SubAgent 只收到"分析文章"没收到 Skill 的完整约束 | 主 Agent 加载 Skill → 创建 SubAgent → 裁剪 token 只传素材 → SubAgent 裸指令运行 | 创建 SubAgent 后检查其 System Prompt 是否有 Skill 步骤 |
| **约束穿透失败** | 约束在当前 session 有效，跨 session 或跨进程后丢失 | Skill 说"不要覆写"→ 调度器独立进程不读 SKILL.md → 照覆不误 | 重启后验证：上次的约束是否仍然生效 |

#### 9.6.2 A-J 十类失效在 Skill 场景的映射

| 失效类 | 含义 | Skill 场景体现 | 自检方法 |
|:-------|:-----|:---------------|:---------|
| **A** 注意力衰减 | 长对话后约束稀释 | 8+ 轮后输出逐渐缺少格式、缺出处 | 第 4/8 轮后停检：输出是否有 changelog？ |
| **B** 优先级错乱 | 用户催促时跳步骤 | 用户说"快点"→ 跳过验证步骤直接出结果 | 检查是否每步都有执行证据 |
| **C** 架构漂移 | 模型升级后不一致 | 同一个 Skill 在不同模型版本输出格式不同 | 双版本对比测试 |
| **D** 行为绕过 | 说执行了实际跳过 | "已按 Skill 执行"但关键步骤证据缺失 | 校验：断言是否有指定格式？ |
| **E** 方向锁定 | 只按单一模板输出 | 多分支 Skill 只深入一个分支，忽略其他 | 检查输出是否覆盖所有分支 |
| **G** 知识层幻觉 | 引用不存在的内容 | Skill 输出了不存在的数据/来源 | 引用必验证（至少确认来源存在） |
| **H** 推理失效 | 逻辑跳跃 | 从 A 直接跳到 Z，缺少中间推导 | 检查推理链是否每步可追溯 |
| **I** 输出失效 | 过度自信/偏见 | 不确定的数据用肯定语气表述 | 不确定处必须标注置信度 |
| **J** 成本失效 | Token 浪费 | 每次重建而不是复用已有分析结果 | 检查是否有跨 session 缓存复用 |

#### 9.6.3 四种工程规避方案（轻量版）

| # | 方案 | 对应场景 | 操作要点 |
|:-:|:-----|:---------|:---------|
| **1** | 显式内联 | SubAgent 上下文丢失 | 创建 SubAgent 时强制全套 Skill 规范塞入初始 Prompt，不是只传素材 |
| **2** | 限制嵌套 | 多层 Agent 递归衰减 | 高规范任务限制 Agent 嵌套 ≤2 层；每层结束时做约束符合性检查 |
| **3** | 后置校验 | 输出质量不稳定 | 新增校验 Agent：加载原 Skill 标准 → 复核输出 → 不通过打回重做 |
| **4** | 约束硬编码 | 跨 session/跨进程失效 | 判断标准：需要跨 session/跨进程 → 必须硬编码到代码/脚本层级 |

#### 9.6.4 三层联动 fallback chain

当单层 Skill 失效时，靠三层联动兜底：

```text
Layer 1: knowledge-doc-writer（创作层）
  -> 即使输出不够深（Skill 失效），

Layer 2: depth-completer（深度补全层）
  -> 可以检测到"框架堆名词"并补充原理深度

Layer 3: doc-reviewer（审查层）
  -> 可以检查逻辑谬误、来源可靠性、格式规范

三层互为 fallback chain，
单层失效不会导致全链路崩塌。
```

---

## §10 Skill 的约束持久化与工程可靠性

### 10.1 约束持久化的必要性

来自 tasks.json 覆写事件（2026-07-30）的关键教训：

```text
失效链路:
  AI 提示词约束（软）-> session 终止 -> 约束丢失
  -> 下次执行无保护 -> tasks.json 被覆写

修复链路:
  识别"跨 session / 跨进程"的约束需求
  v
  将约束从 SKILL.md 移到脚本/配置文件/代码层
  v
  约束成为可检测、可恢复的硬约束
```

**判断标准**（何时需要硬编码）：

```text
✅ 需要跨 session 生效 -> 必须硬编码到代码/脚本
✅ 需要跨进程生效   -> 必须硬编码到代码/脚本
✅ 需要持续保护     -> 必须硬编码（如文件不被覆写）
❌ 只在当前对话生效 -> 可放在 SKILL.md 中
```

### 10.2 约束的三层部署策略

借鉴 t08 的三层分发模型，将 Skill 约束分三层部署：

```text
+===============================================================+
|  持久化约束层（代码/脚本/配置文件）                             |
|                                                               |
|  作用: 跨 session / 跨进程生效，不受 AI 会话生命周期影响           |
|  形式: o 调度器代码保护逻辑                                     |
|         o 定时检测脚本（检测文件是否被意外修改）                   |
|         o CI check / Git hook                                  |
|         o JSON schema 校验                                     |
╟---------------------------------------------------------------╢
|  Layer 1: Skill 执行规范（每次会话强制加载）                      |
|                                                               |
|  作用: 控制当次会话中 AI 的行为                                 |
|  形式: o SKILL.md 中的步骤 + 约束 + 输出规范                    |
|         o description（触发+不触发条件）                         |
|         o 质量门禁（Q1-Q6）                                     |
|  🚫 不可被 token 预算裁剪                                      |
╟---------------------------------------------------------------╢
|  Layer 2: 业务上下文（按需传递）                                  |
|                                                               |
|  作用: 提供执行 Skill 所需的具体材料                              |
|  形式: o 待处理的文档 / URL / 数据                              |
|         o 历史结论 / 前置分析                                   |
|  ⚠️ 可被裁剪，但不影响 Skill 核心流程                            |
╟---------------------------------------------------------------╢
|  Layer 3: 冗余草稿（禁止下发）                                   |
|                                                               |
|  作用: 不传递，避免注意力稀释                                   |
|  形式: o 无关闲聊 / 临时中间结果 / 系统日志                      |
+===============================================================+
```

### 10.3 与 meth-007 精确细节控制的联动

meth-007（三阶段分离协议）在 Skill 创建和使用的应用：

| meth-007 阶段 | Skill 场景 | 具体操作 |
|:-------------|:-----------|:---------|
| **阶段一：方向探索** | 测试 Skill 行为稳定性 | 用 3-5 个不同场景测试触发边界和行为稳定性 |
| **阶段二：方向锁定** | 创建不可变区域 | 锁定 SKILL.md 的 description 和核心约束段，创建批准基线 |
| **阶段三：细节精调** | 逐项优化+回归检测 | 每次只改一处，改完后检查已有约束是否被破坏 |

**在 Skill 创建中的应用流程**：

```yaml
# 1. 方向探索：用 3 个不同场景测试 Skill
#    场景 A：正常输入 → 期望：标准输出
#    场景 B：边缘输入 → 期望：触发"不适用"分支
#    场景 C：多输入 → 期望：批量处理

# 2. 方向锁定：标记为不可变更改的区域
#    - description（锁定，改了触发不准确）
#    - 安全红线（锁定，破了出事故）
#    - 核心步骤顺序（锁定，乱了逻辑不通）

# 3. 细节精调：每次只改一处
#    - 改步骤 3 的表述 → 只改步骤 3
#    - 改后跑回归测试 → 确认步骤 1-2,4-5 没受影响
```

### 10.4 Skills 质量保证完整自检清单（v2.0）

每次创建/修改 Skill 后的最终检查：

```text
□ 精准触发
   - description 是否能在 3 秒内判断是否适用？
   - Do NOT use 部分是否已填？
   - 是否测试了 3 个边缘场景（触发/不触发/误触发）？

□ 步骤可执行
   - 每步是否以动词开头（避免概念描述）？
   - 是否有 skip/fail 条件？
   - 是否有明确完成标志？

□ 安全红线
   - 涉及硬件操作吗？
   - 破坏性操作前有确认步骤吗？

□ 量化约束
   - 性能断言有「数值+单位+基线+条件」四要素吗？
   - 评估标准可验证吗（不是"质量好"而是"无 ESLint 错误"）？

□ 来源追溯
   - 从哪段对话/哪个任务提取的？
   - 是否标注了来源日期和关联文档？

□ 版本管理
   - 有版本号吗？
   - changelog 更新了吗？

□ 重复检测（★★ 新增 ★★）
   - grep -rl "<关键词>" skills/*/SKILL.md 确认无重叠？
   - skills_config.json 中是否有类似触发条件？

□ 注册完成（★★ 新增 ★★）
   - skills_config.json 是否已注册？
   - 是否做了 init_skill.py 的格式验证？
   - 草稿->正式：已走完注册流程？

□ 约束分层（★★ 新增 ★★）
   - 哪些约束需要跨 session 生效？（-> 硬编码）
   - 哪些约束在当前 session 生效？（-> SKILL.md）
   - 跨进程约束是否有脚本/代码层保护？
```

---

## 参考文档

| 文档 | 路径 | 用途 |
|:-----|:-----|:------|
| 知识库搭建设计模式 (meth-006) | `../../spec/meth-006-kb-construction-patterns.md` | §6 方法一参考 |
| 两阶段知识生产法 (meth-009) | `../../spec/meth-009-generate-then-maintain.md` | §6 方法二参考 |
| Skills/Scripts 设计 (design-007) | `../../spec/design-007-skills-scripts-design.md` | §6 方法三参考 |
| AI 细节精控 (meth-007) | `../../spec/meth-007-ai-detail-precision-control.md` | §7 质量门禁参考 |
| 内容质量标准 (sr-007) | `../../spec/sr-007-content-quality-standards.md` | §7 自检清单参考 |
| 约束注册表 (sr-003) | `../../spec/sr-003-system-constraint-registry.md` | §6 方法四约束来源 |
| 超节点存储培训 | `../supernode-storage-requirements-training/README.md` | §6 实操案例知识源 |
| Skill 审计方法 (meth-002) | `../../spec/meth-002-skills-scripts-audit-method.md` | §9 技能审计参考 |
| 系统挑战与实践 (sr-008) | `../../spec/sr-008-system-challenges-and-practices.md` | §9 经验教训参考 |
| Skill 失效根因分析 (t08) | `../../llm-techniques-principles/2026-07-30-t08-skill-failure-root-cause.md` | §9.6、§10 失效分析与约束持久化 |
| Skills 创建方法分解 | `./2026-07-30-skills-creation-from-conversation-analysis.md` | §9.5 7 个对话案例完整版 |

## Changelog

| 日期 | 版本 | 变更 |
|:----|:----|:------|
| 2026-07-30 | v0.3 | **v0.2→v0.3 深化更新**：**§9.4 新增 3 条经验教训**（创建前查重/草稿注册/跨进程约束硬编码，总数 10 条）；**§9.5 新增 7 个本工程对话案例精粹**（server-competitor-analysis 翻车修复/discover 管线标准化/32个废弃Skill批量终结/用户问题分析自主感知/knowledge-sync 重叠教训/weekly-report 四次迭代/spec-consistency-checker 游离教训，每个含背景→翻车→修复→🔑教训四段式）；**§9.6 新增 Skill 失效模式与对策**（两大失效根源/A-J十类失效Skill映射表/四种工程规避/三层联动fallback chain）；**§10 新增完整§10 约束持久化与工程可靠性**（约束持久化必要性/三层部署策略/meth-007三阶段联动/完整质量自检清单 v2.0）。文档从 9 章扩展至 10 章，字数约 24,000 字。 |
| 2026-07-29 | v0.2 | **v0.1→v0.2 扩展更新**：§5 GitHub 开源项目扩展至 15+ 项目（5 分类）；**§6 新增基于 spec 方法论的 5 种 Skills 编写方法**（模式提取法/两阶段法/双引擎法/SSOT 约束法/会话挖掘法，含决策树 + 实操案例）；**§7 新增针对 Trae 的 4 种编写策略**（Custom Instructions/项目规则矩阵/Pipeline 注入/开源封装法，含质量门禁）；**§8 Skill 样例从 4 个扩展至 8 个**（新增 GPU 集群健康检查/互联架构分析/训练 Hang 排查/功耗建模）；**§9 新增工业级工作流**（自动化脚本辅助提取/skill-evolver 自进化/生命周期管理/125 Skills 经验教训）。文档从 6 章扩展至 9 章，字数约 18,000 字。 |
| 2026-07-29 | v0.1 | 初始版本 — 面向服务器硬件领域的 AI Skills 入门与实践指南（6 章 ~9,000 字） |
