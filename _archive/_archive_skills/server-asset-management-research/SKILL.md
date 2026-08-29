---
name: server-asset-management-research
description: Create deep technical analysis documents about server asset management. Use when the user asks to: (1) research server asset management systems covering BMC FRU/CMDB/network discovery, (2) create documents about IPMI FRU specifications, DCMI standards, Redfish asset models, (3) analyze asset inventory, topology discovery, AIOps fault diagnosis with asset data, (4) research component failure statistics (AFR/MTBF/FIT) and vendor implementations, (5) 服务器资产管理、FRU设计、CMDB、资产盘点、拓扑发现、失效统计分析、供应商实现调研. Do NOT use for: general server technology overview, BMC firmware tracking, simple IPMI command tutorials.
metadata:
  requires:
    bins: ["python3"]
  emoji: 📊
---

# 服务器资产管理深度调研文档创建技能

## 概述

本技能提供一套**标准化工作流**，用于创建符合高标准的质量服务器资产管理技术文档。

### 质量标准

| # | 原则 | 含义 |
|:-:|:-----|:------|
| 1 | **覆盖全面** | 同时覆盖 BMC FRU 侧 + 运维 CMDB 侧 + 网络自动发现侧三个维度 |
| 2 | **来源标注** | 每条关键断言必须有出处（标准/论文/白皮书/开源实现） |
| 3 | **量化数据** | 失效分析等数据必须给出具体数值和来源 |
| 4 | **供应商对比** | 至少覆盖 3 家主流供应商的具体实现差异 |
| 5 | **规格建议** | 最终输出应包含可供采购/RFP参考的规格条目 |
| 6 | **审查闭环** | 写完后必须自检格式和链接 |

### 创建前准备

在执行任何创建操作之前，先运行检查脚本确认路径和格式规范：

```bash
python3 <base_dir>/scripts/check_paths.py --document <目标路径>
```

## 调研数据源挖掘工作流

### 第1步：从已有知识库提取

按以下路径提取已有的相关信息：

| 优先级 | 知识路径 | 内容 |
|:-----:|:---------|:-----|
| 1 | `knowledge/02_rd/03_hardware/` | 服务器硬件含 BMC/可靠性/运维 |
| 2 | `knowledge/02_rd/06_O&M/software/` | 深度专题报告（资产管理/维护性/可观测性等） |
| 3 | `knowledge/01_survey/bmc-system/` | BMC 每日跟踪日志 |
| 4 | `import/`（⚠️ 素材用途，批判性使用） | 外部导入的原始材料（按 RULE.md §5-6 约束） |
| 5 | `knowledge/03_AI/tech-research-notes/notes-summary.md` | 技术研究笔记汇总 |

**搜索关键词**: FRU, CMDB, DCMI, IPMI, 资产管理, asset management, LLDP, SNMP, inventory, Redfish, SMBIOS, POH, MTBF, AFR

### 第2步：联网搜索补充

使用 `web_fetch` 搜索以下信息源：

| 来源 | 用途 | 网址 |
|:-----|:-----|:------|
| DMTF 标准 | FRU/Redfish/DCMI 官方规范 | https://www.dmtf.org/standards |
| IPMI 规范 | IPMI FRU 命令定义 | https://www.intel.com/content/www/us/en/products/docs/servers/ipmi/ipmi-specifications.html |
| OpenBMC GitHub | FRU 实现源码 | https://github.com/openbmc/entity-manager |
| 供应商文档 | 具体实现 | Dell iDRAC / HPE iLO / Huawei iBMC 文档页 |
| 学术论文 | 失效分析 | Google Scholar: "server failure analysis datacenter" |

### 第3步：内容组织与编排

推荐文档结构（根据实际需求调整）：

```markdown
# 标题

> 元信息（文件状态、版本、覆盖范围）

## 目录
...

## 1. 引言与范围

## 2. BMC FRU 设计
   - 2.1 IPMI FRU 数据格式
   - 2.2 FRU EEPROM 布局
   - 2.3 IPMI FRU 命令体系
   - 2.4 OpenBMC FRU 实现
   - 2.5 SMBIOS 互补

## 3. CMDB 配置管理数据库
   - 3.1 数据模型
   - 3.2 采集自动化
   - 3.3 方案对比

## 4. DCMI 标准
## 5. 网络自动发现
## 6. Redfish 资产管理
## 7. 资产盘点与拓扑呈现
## 8. AIOps 下的故障诊断
## 9. 失效统计分析
## 10. 供应商实现对比
## 11. 规格建议
## 12. 参考文献
```

### 第4步：文档格式要求

使用脚本检查文档格式：

```bash
python3 <base_dir>/scripts/check_format.py <文档路径>
```

**格式规则**:
- ✅ changelog 在底部（时间倒序，带链接）
- ✅ TOC 在顶部（>100行必须有）
- ✅ 交叉链接覆盖知识库已有相关文件
- ✅ 代码块纯英文（中文说明在外）
- ✅ 通用知识外链化
- ✅ 每条断言出处标注

### 第5步：索引与日志更新

创建文档后必须同步更新：

1. **index.md**: 在对应目录的 index.md 中添加文件索引条目
2. **log.md**: 在对应目录的 log.md 中添加变更记录

格式示例：

```markdown
## 2026-XX-XX

- **新增** 📊 `06_O&M/software/server-asset-management-deep-analysis.md` — 服务器资产管理深度分析 v1.0（69KB/12章），覆盖...
```

### 第6步：创建可复用的知识入口

如果该文档涉及的知识可在未来任务中复用，将其关键信息写入 knowledge 对应位置。

## 参考链接

- 知识库资产分析入口: `knowledge/02_rd/06_O&M/software/server-asset-management-deep-analysis.md`
- 标准规范索引: `knowledge/01_survey/bmc-system/`

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-06-26 | v1.0 | 首次创建 |
