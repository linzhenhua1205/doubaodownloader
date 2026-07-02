# ⚙️ BMC与系统管理 — 行业跟踪框架

## 核心跟踪问题
- OpenBMC 新版本/新硬件支持
- Redfish 标准更新（DMTF）
- BMC 芯片（ASPEED/伏羲半导体）进展
- 带外管理安全漏洞/改进
- PLDM/SPDM/ MCTP 等管理协议更新

## 搜索关键词
- `OpenBMC new release` `OpenBMC latest` `OpenBMC 2.x`
- `Redfish standard update` `DMTF Redfish`
- `ASPEED AST2700` `BMC chip`
- `BMC security vulnerability` `PLDM` `SPDM`
- `服务器管理` `带外管理` `IPMI`

## 来源优先级

| 优先级 | 来源 | 说明 |
|:-----:|:-----|:-----|
| 🥇 Tier 1 | **OpenBMC GitHub Release** | 直接看 changelog |
| 🥇 Tier 1 | **DMTF Redfish 规范更新** | 标准进展 |
| 🥈 Tier 2 | **ASPEED / 伏羲半导体 官方发布** | 芯片路线图 |
| 🥈 Tier 2 | **OCP 硬件管理项目组** | 开放管理标准 |
| 🥉 Tier 3 | **Linux Foundation / Yocto 发布** | 构建系统更新 |

## 质量门槛
- ✅ **值得记录**：版本发布/新硬件支持/bug fix 安全修复
- ❌ **跳过**：无具体版本的旧闻

## 输出路径
- `knowledge/01_survey/bmc-system/YYYY-MM-DD.md`

## 交叉引用
- 远程管理 ↔ `server-hardware/` (整机设计)
- 管理协议 ↔ `distributed-os/` (带内/带外融合)
