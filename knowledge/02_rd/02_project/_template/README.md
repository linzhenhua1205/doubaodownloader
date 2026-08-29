# 项目文件夹参考模板（AI 场景版）

> **用途**: 新项目文件夹的创建模板。复制本目录为 `02_project/<project_name>/`，按需填充。
> **设计依据**: 《项目文件夹的 AI 场景优化：从「五类标准结构」到「人机共写设计过程系统」》(2026-08-28)
> **核心原则**: 升级 5 类（管理/决策/过程/交付件/参考）+ 新增 3 层（SSOT/约束/检索）；人机共写、机器可读、跨文档一致。
> **维护**: 模板随试点项目反馈迭代修订（约束生命周期管理）。

---

## 目录结构

```text
02_project/<project_name>/
│
├── 00-management/          # ① 项目管理（升级：状态机+三向链接）
│   ├── plan.md             #    项目计划/WBS/里程碑
│   ├── risk-register.md    #    风险台账
│   ├── issue-tracker.md    #    问题清单（P0-P3 + SLA）
│   └── status.md           #    项目心跳（一句话状态摘要，AI 每轮更新）
│
├── 10-decisions/           # ② 决策（升级：结构化 ADR，编号连续）
│   └── adr-C01-xxx.md      #    模板见 _adr-template.md
│
├── 20-process/             # ③ 过程（升级：迭代轨迹）
│   ├── iterations/         #    评审/迭代轨迹记录（模板见 _iteration-log-template.md）
│   ├── meeting-notes/      #    会议纪要（头部关联 ADR 编号）
│   └── test-records/       #    测试/验证记录（关联交付件版本）
│
├── 30-deliverables/        # ④ 交付件（升级：验证状态+changelog）
│   ├── 00-design/          #    设计文档（SSOT 权威文档在此声明）
│   ├── 10-topology/        #    拓扑/框图（派生文档）
│   └── 20-reports/         #    报告/方案对比
│
├── 40-references/          # ⑤ 参考文档（升级：来源分级）
│   ├── standards/          #    一手：标准/规范/论文
│   ├── industry/           #    二手：行业分析/白皮书
│   └── notes/              #    三手：笔记/转载（批判使用）
│
├── 90-bak/                 # 废弃区（永不 rm，mv 至此）
│
├── _manifest/              # ➕ SSOT 权威源声明（模板见 _ssot-manifest-template.md）
├── _rules/                 # ➕ 约束 Harness 层（模板见 _ai-behavior-template.md）
└── _index.md               # ➕ 检索层：项目知识地图（模板见 _index-template.md）
```

---

## 各目录职责与文件规范

### 00-management/ — 项目管理

- 所有台账头部带「最后更新时间 + 更新者（人或 AI）」
- 问题清单条目格式：`[P0-P3] 主题 | 状态 | 关联 ADR | 关联文档`
- `status.md` 由 AI 在每次任务收尾时更新（一句话 + 变更点），防止僵尸状态
- 文件头部状态：`草稿/评审中/已裁决/生效/已失效`

### 10-decisions/ — 决策（ADR）

- 文件名：`adr-C<nn>-<slug>.md`，编号连续（本知识库 C1-C27 已连续）
- 模板字段：Context / Decision / Consequences / Status / **回写清单（强制）** / 防复发规则
- 无回写清单的 ADR 不允许标记「已接受」
- 状态可演进：新 ADR 可声明「取代 adr-Cxx」

### 20-process/ — 过程（迭代轨迹）

- 迭代轨迹记录必须包含：输入版本、评审意见（编号）、裁决（ADR 编号）、修正动作、验证结果
- 会议纪要头部关联：涉及主题、ADR 编号、受影响文档
- 过程与交付件分离：过程 = 怎么做的，交付件 = 做成了什么

### 30-deliverables/ — 交付件

- 每份文档头部元信息：状态、验证状态（✅ 门禁通过 / ⚠️ 待评审 / ❌ 存在已知矛盾）、AI 参与度、Changelog
- SSOT 权威文档在头部声明 `> SSOT: 本文件为 <参数域> 唯一权威源`，并在 _manifest 注册
- 派生文档不单独维护设计参数，变更走 SSOT 传播流程

### 40-references/ — 参考文档

- 文件头部记录：来源类型（一手/二手/三手）、原始出处、抓取日期、验证状态
- 引用必带 `[来源: 出处, 日期]`；关键可验证断言必须有外部出处（Q10 信源配比：内部 ≤60%）
- 外部资料与内部结论严格分离，防止口径污染

### _manifest/ — SSOT 权威源声明

- 声明每类设计参数的唯一权威源文档（Tier 0），派生文档为 Tier 1/2
- 定义 AI 行为准则：查询先读 SSOT、禁止从派生文档转引、不一致记录待同步、不自动修改非 SSOT 文档
- 变更传播流程：ADR 裁决 → 回写清单 → 逐项回写 → 交叉比对验证

### _rules/ — 约束 Harness 层

- 约束做成基础：项目级规则随项目存在，不随对话消失
- 建议文件：`quality.md`（质量标准与门禁）、`naming.md`（命名/编号/术语）、`ai-behavior.md`（AI 行为准则）
- 约束修订走「失败模式 → 规则 → 机制」转化链，每次修订留痕

### _index.md — 项目知识地图

- AI 每次开工第一读：一次读取获得项目全景
- 内容 = 当前状态摘要 + 文档地图 + 决策索引 + 待办

---

## 使用步骤

1. 复制本目录为 `02_project/<project_name>/`
2. 填充 `00-management/plan.md`（项目计划）+ `_index.md`（初始状态）
3. 定义 `_manifest/ssot-manifest.md`（关键参数权威源）
4. 按五步迭代环运作：盘点 → 定义 → AI 起草 → 人机裁决 → 一致性验证
5. 每次迭代产出落盘 + commit（未落盘 = 未完成）

## 模板文件清单

| 文件 | 用途 |
|:-----|:-----|
| `10-decisions/_adr-template.md` | ADR 决策记录模板 |
| `20-process/_iteration-log-template.md` | 迭代轨迹记录模板 |
| `_manifest/_ssot-manifest-template.md` | SSOT 权威源声明模板 |
| `_rules/_ai-behavior-template.md` | AI 行为准则模板 |
| `_index-template.md` | 项目知识地图模板 |

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-28 | v1.0 | 首次创建（基于 2026-08-28 深度分析 §4 参考结构） |
