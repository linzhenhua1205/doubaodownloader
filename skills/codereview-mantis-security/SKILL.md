---
name: codereview-mantis-security
description: >
  代码走读安全专项审查。基于 Google mantis（import/mantis/）17 阶段安全审查
  流水线，对走读目标执行威胁建模→漏洞挖掘→误报过滤→复现验证的深度安全审查。
  Use when: (1) 代码走读中用户要求"安全审查/漏洞挖掘/威胁建模/安全检查"，
  (2) 走读目标是安全敏感代码（BMC 固件/网络栈/认证授权/加密/解析器/权限边界），
  (3) 发布前专项安全审查（三阶段走读体系阶段三），
  (4) 与 open-code-review 协同：OCR 做通用质量审查，本 skill 做安全专项纵深。
  提供 Lite（静态分析，默认）与 Full（含沙箱复现/补丁，需 Docker）两种模式。
license: Apache-2.0
metadata:
  author: google (adapted)
  homepage: https://github.com/google/mantis
  version: "1.0.0"
  requires:
    bins: ["python3"]
  compatibility: >
    依赖 import/mantis/ 子工程（18 个 skill 目录）。Full 模式需 Docker +
    可选 gVisor(runsc)。所有阶段由宿主 agent 执行 LLM 推理，无需额外 CLI。
---

# 代码走读安全专项审查（Mantis 集成）

## Overview

将 Google 官方 **mantis** 安全审查流水线嵌入本工作区代码走读体系：
- **通用质量审查** → `codereview-open-code-review` / `codereview-open-code-review-delegate`（diff 级、行级评论）
- **安全专项纵深** → 本 skill（全库级、威胁模型驱动、漏洞发现→验证→评级）

mantis 核心哲学：**"Model + Harness = Agent"** 在安全域的落地 —— 用 17 个
顺序 Skill 模拟一支安全团队（架构师→威胁建模师→策略师→审计员→去重→审查→
批评→复现→链式利用→补丁→校准→反思→报告），每个阶段读/写共享磁盘状态
（`workspace/` 目录），阶段间通过 JSON/Markdown 契约解耦。

## 何时启用（触发判断）

1. 用户显式要求安全审查 / 漏洞挖掘 / 威胁建模 / 安全专项走读
2. 走读目标含安全敏感组件（按知识库 CodeReview 风险矩阵）：
   - **认证/授权/会话**、加密实现、密钥管理
   - 网络边界（协议解析、输入校验、序列化/反序列化）
   - 权限提升路径、供应链依赖、配置文件注入面
   - BMC/固件类（IPMI/Redfish/安全启动/镜像签名）
3. 发布前专项审查（三阶段走读体系阶段三，`gate_level: strict`）
4. 通用走读（OCR）发现疑似安全问题时，升级到本 skill 做纵深确认

## 模式选择

| 模式 | 阶段数 | 适用 | 前置条件 |
|:-----|:------:|:-----|:---------|
| **Lite**（默认） | 9 核心阶段 | 日常走读安全增强 | 无（纯静态分析） |
| **Full** | 17 全阶段 | 发布前/高危目标 | Docker（复现/补丁需沙箱） |

- 默认 **Lite**：`architecture → threat-model → plan → researcher → dedupe → review → critic → calibrate → report`
- **Full** 在 Lite 基础上追加：`history`（VCS 历史漏洞）、`structural-index`（跨引用索引）、`summarize`（目录地图）、`reproduce`（沙箱 PoC 复现）、`chain`（利用链）、`patch`（最小修复）、`reflect`（学习沉淀）
- 用户说"深度/完整/发布前/复现漏洞/要补丁" → Full 模式
- 环境无 Docker 且目标高危 → 提示用户，或降级 Lite + 标注"复现验证缺失"

## 工作流

### Step 1: 初始化审查工作区

```bash
# 在走读目标仓库内创建 mantis 状态目录（不污染目标源码）
mkdir -p workspace/kb workspace/findings workspace/report workspace/archive
echo '{"pass_number": 1, "snapshot_pinned": false}' > workspace/.mantis_state.json
```

- `workspace/` 相对目标仓库根目录（mantis 默认约定）
- 若目标仓库已有 `workspace/`，检查是否被 git 忽略；未忽略则加入 `.gitignore`

### Step 2: 按流水线顺序执行各阶段

每个阶段：**读取 `import/mantis/<skill>/SKILL.md` → 按其 Instructions 执行 →
写入共享状态**。Lite 模式阶段及调用要点：

| 序 | Skill | 读取 | 写入 | 执行要点 |
|:--:|:------|:-----|:-----|:---------|
| 1 | `mantis-architecture` | 代码结构+learnings | `kb/architecture.md`, `kb/entities/*.md`, `kb/dependencies.json` | 梳理组件边界/信任边界/数据流，不写威胁模型 |
| 2 | `mantis-threat-model` | KB | `kb/THREAT_MODEL.md` | 按 STRIDE/资产/攻击面迭代威胁模型，结合领域规则（BMC/网络/认证） |
| 3 | `mantis-plan` | KB+威胁模型 | `plan.json` | 映射外部边界→扫描路线图，按依赖扇出排优先级 |
| 4 | `mantis-researcher` | plan.json+源码 | `findings/<uuid>.json` | 对目标文件做静态审计：边界检查/前置条件/缺失净化/接口违规 |
| 5 | `mantis-dedupe` | findings/ | 合并后 findings | 按 CWE+文件+代码模式聚类去重，保留代表性 finding |
| 6 | `mantis-review` | findings+源码 | findings 状态更新 | 独立复核，过滤误报（对照真实代码） |
| 7 | `mantis-critic` | findings+KB | findings 状态更新 | 评估生产可用性（排除 debug-only/断言陷阱） |
| 8 | `mantis-calibrate` | findings | 风险评级矩阵 | 按 CVSS 维度（利用复杂度/影响/权限）定级 |
| 9 | `mantis-report` | findings/archive | `report/review_packet*.md` | 生成人类可读安全审查包 |

**Full 模式追加阶段**：

| 序 | Skill | 说明 | 安全要求 |
|:--:|:------|:-----|:---------|
| 0 | `mantis-history` | 分析 VCS 历史提取历史漏洞模式 | 只读 |
| 0.5 | `mantis-structural-index` | 构建调用图/符号表索引 | 只读 |
| 1 | `mantis-summarize` | 生成目录映射摘要 | 只读 |
| 10 | `mantis-reproduce` | 生成 PoC 并在**隔离沙箱**运行 | ⚠️ Docker + `--network none`，禁止宿主执行 |
| 11 | `mantis-chain` | 组合多步利用链 | 沙箱内 |
| 12 | `mantis-patch` | 生成最小修复并验证阻止复现 | ⚠️ 补丁只生成到 workspace/，**不自动应用** |
| 13 | `mantis-reflect` | 提取执行轨迹洞察到 learnings | 只读 |

### Step 3: 结果汇入走读报告

将 `report/review_packet*.md` 的核心结论融入标准走读报告（模板见
`knowledge/02_rd/01_product/01_software/13-codereview-project/2026-07-09-codereview-system-overview.md` §4.2）：

```markdown
## 🔐 安全专项审查（Mantis）

**模式**: Lite / Full | **覆盖**: N 个组件 / M 个文件

### 威胁模型摘要
- 主要攻击面: ...
- 信任边界: ...

### 发现清单（按风险评级）
| # | 严重度 | CWE | 位置 | 摘要 | 状态 |
|---|:------:|:----|:-----|:-----|:-----|
| 1 | Critical | CWE-89 | path:line | SQL 注入... | 已确认 |

### 复现/验证
- 已验证: 2 个（Full 模式含沙箱 PoC）
- 待人工确认: 1 个（复现失败≠误报，需人工研判）

### 修复建议
- P0: ...（建议阻塞合入）
- P1: ...
```

### Step 4: 分类上报（对齐走读分级）

- **Critical/High** → 走读 P0（阻塞合入），列出证据链
- **Medium** → P1（限期修复），给出修复方向
- **Low/疑似误报** → P2 或标注待确认，不阻塞

## 安全红线（mantis 官方强调，强制执行）

1. **绝不在宿主直接运行 PoC/补丁代码** —— reproduce/patch 阶段必须容器沙箱
   （`docker run --network none` + gVisor runsc 更佳）
2. **发现必须人工复核** —— AI 可能幻觉；不向外部维护者批量提交未验证报告
3. **复现失败 ≠ 误报**，成功复现 ≠ 全场景可利用 —— 报告需注明条件与限制
4. **补丁不自动应用** —— 生成到 `workspace/patches/`，由用户审阅后手动合入
5. 目标含生产系统/内部网络/敏感数据时，**先隔离再审查**（用快照副本）
6. 禁止 `--yolo` / 自动审批敏感操作

## 与现有体系协同

- **OCR 先行**：先跑 `codereview-open-code-review`（diff 级通用审查），其
  High 级安全发现触发本 skill 纵深确认
- **威胁模型复用**：`workspace/kb/THREAT_MODEL.md` 可沉淀到知识库
  `knowledge/02_rd/01_product/01_software/13-codereview-project/` 作为项目
  级资产，跨轮次复用
- **learnings 沉淀**：Full 模式 `mantis-reflect` 产出写入目标仓库
  `workspace/learnings.jsonl`，随走读历史积累项目专属漏洞模式

## References

- mantis 源码与全部 SKILL.md: `import/mantis/`（18 个 skill 目录）
- Agent 参考指南（流水线架构/契约/部署）: `import/mantis/README_AGENTS.md`
- 官方仓库: https://github.com/google/mantis
- 本工作区调研基线: `knowledge/02_rd/01_product/01_software/13-codereview-project/2026-07-23-codereview-github-skills-survey.md`
- 集成分析文档: `knowledge/02_rd/01_product/01_software/13-codereview-project/2026-08-13-codereview-mantis-security-integration.md`
