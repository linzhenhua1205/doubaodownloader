# 存储行业洞察 × 服务器整机研发方向 — Web PPT 结构大纲

> 基于「五看三定」方法论 · 2026-08-12 · 汇报对象：领导层
> 源材料：`knowledge/07_industry-research/03_server/04_industry/2026-08-12-storage-industry-insight-leadership-report.md`（v1.2）+ `knowledge/03_AI/train/ai-storage/2026-08-03-ai-storage-insight-report.md`（v1.5）
> 样式：默认 Web PPT 模板（`websites/ppt-default-template/index.html`）

## 页面清单（33 页）

| # | 页类型 | 标题 | 核心内容 |
|:-:|:------|:-----|:---------|
| 1 | 封面 | 存储行业洞察 × 服务器整机研发方向 | 五看三定 · 软件栈=整机差异化主战场 |
| 2 | 目录 | 五看三定 AGENDA | 七部分导航 |
| 3 | 过渡 | Part 1 看宏观 | 数据仓库 → AI 算力的扩展内存 |
| 4 | 内容 | 1.1 历史性拐点 | $803.9B 超逻辑芯片；SK hynix 财报配图；8/12 实时信号 |
| 5 | 内容 | 1.2 五大推动力 | 四堵墙（内存/带宽/成本/可靠性）→ G3.5 诞生 |
| 6 | 内容 | 1.3 四大统一信号 | 三角验证：GTC×FMS×ODCC 收敛 |
| 7 | 过渡 | Part 2 看市场 | KV Cache 第一性需求 |
| 8 | 内容 | 2.1 KV Cache 公式与硬件诉求 | 320KB/token；838GB/s decode；host DRAM ≥8×GPU HBM |
| 9 | 内容 | 2.2 三类负载场景 | A 容量/B 吞吐/C 结构 → SKU 化第一原则 |
| 10 | 内容 | 2.3 客户分层 | 推理云/CSP/私有化付费意愿 |
| 11 | 过渡 | Part 3 看竞争 | 三条路线并存分层 |
| 12 | 内容 | 3.1 NVIDIA CMX/G3.5 | Storage-Next/cuFile 开源/ICMS 五层；GTC 配图 |
| 13 | 内容 | 3.2 Intel CXL/JBOF | Crescent Island 160GB LPDDR5X；CXL 联盟配图 |
| 14 | 内容 | 3.3 中国 ODCC 路线 | 强制标准/NHA/大普微 512TB/长鑫 LPDDR6 |
| 15 | 内容 | 3.4 竞争格局小结 | 差异化在中间层：硬件可买软件不可买 |
| 16 | 过渡 | Part 4 看自身 | 软件栈=最大短板=最大机会 |
| 17 | 内容 | 4.1 能力盘点 | P0 五条需求全部是软件栈 |
| 18 | 过渡 | Part 5 看机会 | G3.5·LPDDR·CXL·KV 分层 |
| 19 | 内容 | 5.1 G3.5 共享闪存层 | 定义/规格/是什么≠不是什么 |
| 20 | 内容 | 5.1b G3.5 14 条需求 | 5 组 MECE，P0 五条高亮 |
| 21 | 内容 | 5.2 LPDDR 应用机会 | Intel 160GB/长鑫 LPDDR6/PIM；Samsung 配图 |
| 22 | 内容 | 5.3 CXL 及配套软件 | 四大池化系统；memkind/透明分层 |
| 23 | 内容 | 5.4 KV 分层设计 | 四层命运 L0-L3；HiSparse 实证；SK AI 配图 |
| 24 | 内容 | 5.5 软件设计与故障诊断 | NCCL 假存活案；I/O 层监控 |
| 25 | 过渡 | Part 6 会议信号 | 五大会闭环 |
| 26 | 内容 | 6.1 五大会矩阵 | GTC/FMS/ODCC/OCP/AI Advanced；FMS 配图 |
| 27 | 内容 | 6.2 FMS 2026 深度 | 五大信号；P1-P10 零证伪；P11-P15 |
| 28 | 内容 | 6.3 信号一致性+研发动作 | 六信号收敛表；五条研发动作 |
| 29 | 过渡 | Part 7 三定 | 存储=AI 性能与成本第一杠杆 |
| 30 | 内容 | 7.1 定战略 | 一句话战略定位 |
| 31 | 内容 | 7.2 定目标 | 量化指标 2026H2-2028 |
| 32 | 内容 | 7.3 定策略 | P0/P1/P2 落地路径 |
| 33 | 结论 | 结论与下一步 | A1-A5 行动建议 |

## 官方配图（6 张，web 直链，全部 curl 验证 200）

| 页 | 配图 | 官方源 |
|:--:|:-----|:-------|
| 4 | SK hynix 2Q26 财报 | news.skhynix.com |
| 12 | NVIDIA GTC 2026 | nvidia.com/gtc |
| 13 | CXL 联盟 | computeexpresslink.org |
| 21 | Samsung 3D 内存愿景 | news.samsung.com |
| 23 | SK hynix AI 基础设施 | news.skhynix.com |
| 26 | SK hynix FMS 2026 | news.skhynix.com |

## 操作方式

- 浏览器直接打开 `index.html`，或 `python3 -m http.server` 后访问
- 翻页：键盘 ← → / 空格 / PageUp Down；点击左右半区；触摸滑动
- ESC 缩略目录；F 全屏；P 打印导出 PDF
