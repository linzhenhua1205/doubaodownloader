---
name: web-ppt-builder
description: 基于 Web 的单页翻页式汇报 PPT 生成器（深蓝科技风默认样式）。当用户需要创建/生成基于 web 的 PPT、汇报材料、演示页面，要求"单独一个页面、支持翻页"、"web ppt"、"汇报 ppt"、"五看三定 ppt"、"默认 ppt 样式"时使用。按 7 条铁律产出：①结论先行/自上而下/MECE 拆解 ②每页标题=本页要点（行动式标题） ③红/绿关键色语义（红色=需行动/风险、绿色=强调/已验证） ④汇报类材料用五看三定框架 ⑤结论页四维影响（总结+技术+产品+业务经营，各3~5点） ⑥数据标注来源链接 ⑦多用官方配图（web 直链）增加可信度。参考样式 knowledge/03_AI/train/agentic-cpu-ppt/index.html。
metadata:
  emoji: 📊
  requires:
    bins: ["curl"]
---

# Web PPT Builder（默认 Web PPT 生成样式）

## 概述

生成**单页面、支持翻页**的 Web 汇报 PPT（HTML 单文件，浏览器直接打开），默认深蓝科技风样式。模板：`<base_dir>/assets/template.html`（复制即用，含全部组件与示例页）。

适用场景：领导汇报、行业洞察、技术专题、项目进展、战略分析等一切**汇报类材料**。

## 7 条铁律（每次生成必须全部满足）

1. **结论先行、自上而下、MECE**：每部分先给结论（一句话）→ 再拆解证据 → 同层互斥且穷尽（MECE 自检）
2. **每页标题 = 本页要点**（行动式标题 action-title）：标题写成陈述句结论，不是话题标签——只读标题连起来能讲完整论证（幽灵 deck 测试）
3. **红/绿关键色语义**：
   - `红色 .red` = 需要行动 / 风险 / 必须关注（如"⚠ 需行动""P0 缺口""风险"）
   - `绿色 .green` = 强调 / 已验证 / 正向信号（如"✓ 已验证""已兑现"）
   - 每页关键信息用色 ≤ 3 处，其余保持 muted，避免整页变红绿
4. **汇报类材料用五看三定框架**：看宏观/行业 → 看市场/客户 → 看竞争 → 看自身 → 看机会 → 定战略/目标/策略（目录页与过渡页按此组织）
5. **结论页四维影响**（`.impact` 组件）：总结（全宽）+ 相关技术领域影响 + 相关产品领域影响 + 相关业务/经营领域影响；每维 **3~5 点**，条目化（自动编号）
6. **数据标注来源链接**：每页 `.src` 脚注放来源 URL（官方源优先），标注分级：✅官方一手 / ⚠️行业共识转引 / 🔶第一性推导 / 🏷厂商声称
7. **多用官方配图**：技术论证点旁放官方图（厂商新闻室/标准组织官网），web 直链 + `onerror="this.style.display='none'"` 兜底，`.imgcard` 组件内注明图片来源 URL

## 工作流

### Step 1 — 理解材料与定位
- 读用户提供的报告/素材（或知识库文档），确定：受众（领导/评审/团队）、汇报时长（决定页数：10 页≈8-12 分钟、20 页≈15-20 分钟）、叙事骨架（五看三定 / 问题-方法-结论 / 背景-现状-机会-行动）
- 提取**一句话核心结论** → 用于封面与总结页

### Step 2 — 规划大纲（MECE + 行动式标题）
- 按五看三定（汇报类）或领域逻辑（技术类）拆解到节
- 每页写行动式标题（陈述句结论），先做**幽灵 deck 测试**：只读标题能否讲完整论证
- 结论页四维影响（总结/技术/产品/业务经营）预留为最后一页

### Step 3 — 复制模板并填充
```bash
cp <base_dir>/assets/template.html <目标目录>/index.html
```
- 目标目录约定：`knowledge/03_AI/train/<主题>-ppt/`（与 agentic-cpu-ppt、ai-storage-ppt 并列）
- 用 `edit`/`write` 替换所有 `<section class="slide">` 内容，保留 `<style>` 与 `<script>` 不动
- 配图 URL **先 curl 验证 HTTP 200** 再嵌入：
```bash
curl -s -o /dev/null -w "%{http_code}" -L --max-time 15 -A "Mozilla/5.0" "<图片URL>"
```

### Step 4 — 质量校验
```bash
python3 <base_dir>/scripts/validate_ppt.py <目标目录>/index.html
```
脚本检查：HTML 标签闭合、section.slide 数量、每页是否有标题/来源脚注、红绿语义使用、结论页四维影响完整性（总结+技术+产品+业务经营）、imgcard 是否含官方源 URL。

### Step 5 — 渲染验证 + 交付
- 无头浏览器截图抽查（Chromium headless，参考 ai-storage-ppt 做法）：
```bash
CHROME=~/.cache/ms-playwright/chromium-1169/chrome-linux/chrome
"$CHROME" --headless --disable-gpu --no-sandbox --window-size=1600,900 \
  --screenshot=/tmp/ppt_check.png --hide-scrollbars "file://<绝对路径>/index.html"
```
- 通知用户路径与打开方式；归档：更新 `knowledge/log.md`（kb-log-append.py）+ git commit

### Step 6 — PPTX 导出（用户要求 PPT/PPTX 文档时）
当用户说「把 web ppt 转成 PPTX / 生成 ppt 格式的文档」时，用通用转换器：
```bash
# 依赖（一次性）：python3 -m pip install python-pptx beautifulsoup4 lxml
python3 <base_dir>/scripts/build_pptx.py <目标目录>/index.html <目标目录>/<主题>.pptx
```
- 转换器覆盖全部组件：cover/part 过渡页/table/flow 步骤箭头/grid 卡片/points/imgcard/impact 四维/src 脚注；红绿语义（.red 需行动/.green 已验证）保留
- 配图自动按 HTML 出现顺序 curl 下载（失败跳过不嵌图）；图片会放在 `tmp/ppt-pptx-images/`，可加第三个参数指定目录
- **QA（无 LibreOffice 环境时）**：用 python-pptx 读回验证——页数、图片数、关键文本、无占位符；抽查内容页与结论页
- 交付：与 HTML 同名目录归档 .pptx；log 追加 + git commit（`[AI] feat(ppt): <主题> pptx`）
- 已知边界：个别高密度页（如 RSS 补充页、结论页）字号偏小需人工微调；告知用户可指定页码调字号重生成

## 页面结构规范

| 页类型 | 用途 | 关键组件 |
|:-------|:-----|:---------|
| 封面 | 一句话结论 + 核心命题 | `.cover`，标题即结论 |
| 目录 | MECE 导航（五看三定） | `.slide` + 编号 h2 |
| 过渡页 | 每部分开头给结论 | `.part` + `.big` + `.sub` |
| 内容页 | 一页一要点 | 表格/卡片/流程/对比/配图 |
| 结论页 | 四维影响 | `.impact`（sum+3 维） |
| 附注页 | 参考文件/数据分级 | table + `.src` |

**内容页排版**：先结论（lead 一句话）→ 证据（数据/表格/图）→ 来源（.src）；每页要点 ≤7 条；量化数据带单位+基线+条件；避免整页纯文字（必须有卡片/表格/图之一）。

## 颜色与数据纪律

- **红绿语义全局一致**：全篇 `.red` 只表示"需行动/风险"，`.green` 只表示"强调/已验证"——不与装饰色混用
- **数据来源分级**（每页 .src 必填）：✅官方一手（厂商新闻室/标准组织官网，给 URL）/ ⚠️行业共识（TrendForce/IDC 等转引，给 URL）/ 🔶第一性推导（公式推导，注明依据）/ 🏷厂商声称（未独立验证，明确标注）
- **配图纪律**：只用官方源（news.skhynix.com / news.samsung.com / nvidia.com / computeexpresslink.org 等），web 直链不下载；URL 嵌入前 curl 验证 200；图片不可用时自动隐藏不影响排版
- **文档规范**：生成后更新知识库 log（三件套纪律：kb-log-append.py 追加）+ git commit（`[AI] feat(ppt): <主题>`）

## 参考实例

- `knowledge/03_AI/train/ai-storage-ppt/index.html`（33 页，存储行业五看三定领导汇报，2026-08-12）
- `knowledge/03_AI/train/agentic-cpu-ppt/index.html`（24 页，AI 办公×CPU 需求研判，2026-08-05，样式前身）

## 常见问题

- **页面溢出**：内容过多时缩小字号/拆两页，正文 ≥14px、表格 ≥12.5px 可投影
- **配图失效**：curl 非 200 则换官方替代图或删除 imgcard（保留文字说明）
- **翻页交互失效**：确认 `<script>` 块未被改动（show(0) 初始化在文件末尾）
