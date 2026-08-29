# 默认 Web PPT 模板（深蓝科技风）

> **确立日期**：2026-08-12　|　**版本**：v1.0　|　**来源**：存储行业洞察汇报 PPT 沉淀

## 用途

所有基于 Web 的汇报 PPT **默认使用本模板**（单页 deck + 翻页交互），替代临时手写样式。

## 使用方式

1. 复制 `index.html` 到目标目录（如 `knowledge/03_AI/train/<项目>-ppt/`）
2. 修改 `<title>` 与所有 `<section class="slide">` 内容（替换示例块）
3. 配图使用**官方 web 直链**（img 加 `onerror="this.style.display='none'"` 兜底）
4. 直接浏览器打开 / F 全屏 / P 打印导出 PDF

## 组件速查

| 组件 | 类名 | 说明 |
|:-----|:-----|:-----|
| 封面 | `.cover` | 封面页（大标题 + meta 信息） |
| 过渡页 | `.part` | PART N 章节过渡 |
| 大数字卡 | `.card .num` | 核心量化指标展示 |
| 网格 | `.grid .g2/.g3/.g4` | 2/3/4 列卡片网格 |
| 表格 | `table` / `.tbl-scroll` | 数据表 / 横向滚动表 |
| 条形图 | `.bars .bar-row .bar-fill` | 比例对比 |
| 流程 | `.flow .step .arrow` | 步骤流程（`.cpu`/`.gpu` 高亮） |
| 强调列表 | `.points`（`.warn` 变体） | ✔/! 列表 |
| 对比双栏 | `.vs .a/.mid/.b` | A vs B 对比 |
| 配图卡片 | `.imgcard` | 官方配图 + 说明 |
| 标签 | `.tag .w/.g/.o/.r` | 优先级/状态彩色标签 |
| 来源脚注 | `.src` | 每页必填数据来源分级 |

## 数据纪律（强制）

- 每页 `.src` 标注来源分级：✅官方一手 / ⚠️行业共识转引 / 🔶第一性原理推导 / 🏷厂商声称
- 配图必须为官方源（厂商新闻室/标准组织官网），URL 先 curl 验证 HTTP 200
- 量化数据标注单位 + 基线 + 条件

## 实例

- `knowledge/03_AI/train/ai-storage-ppt/index.html`（33 页，2026-08-12 存储行业洞察）
- `knowledge/03_AI/train/agentic-cpu-ppt/index.html`（24 页，2026-08-05 AI 办公×CPU，模板前身）
