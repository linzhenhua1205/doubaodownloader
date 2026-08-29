# 🧠 Skills 使用手册

> Cow 系统中全部 Skills 的详细使用说明：触发条件、输入输出、工作流、注意事项。
>
> Skills 本身不提供 CLI 调用，而是通过 **AI 对话** 自动路由（系统根据用户意图匹配 Skill 描述后加载执行）。
> 本手册方便你了解每个 Skill 的能力边界和触发方式。
>
> 最后更新: 2026-08-03
> 总数: 96 skills（本地） + 33 外部引用 = 128 | 状态: ✅ 就绪 | ⚠️ 需配置环境变量 | 🔌 需 LINKAI_API_KEY

---

## 📑 目录

- [1 类：导入与归档](#-1-类导入与归档)
- [2 类：专题创作与写作](#-2-类专题创作与写作)
- [3 类：数据处理与提取](#-3-类数据处理与提取)
- [4 类：格式转换与排版](#-4-类格式转换与排版)
- [5 类：检查、审查与维护](#-5-类检查审查与维护)
- [6 类：数据查询与工具](#-6-类数据查询与工具)
- [7 类：平台集成](#-7-类平台集成)
- [8 类：系统/流程编排](#-8-类系统流程编排)
- [9 类：服务器/硬件分析](#-9-类服务器硬件分析)
- [10 类：科研与竞赛](#-10-类科研与竞赛)
- [11 类：技能生命周期管理](#-11-类技能生命周期管理)
- [12 类：插件（需 LINKAI_API_KEY）](#-12-类插件需-linkai_api_key)
- [可用但未就绪](#-可用但未就绪)

---

## 📥 1 类：导入与归档

### `doubao-share` — 豆包对话归档

解析豆包（Doubao）共享链接，提取内容并归档到知识库。

**触发条件**: 用户分享豆包对话 URL / 说"豆包" / 要求归档豆包对话

**工作流**: 访问链接 → 提取关键内容 → 生成 slug 文件名 → 写入 `knowledge/06_others/sources/` → 更新 index+log

```text
豆包 URL → doubao-share → knowledge/06_others/sources/<slug>.md
                                       ↓
                                index.md + log.md
```

**辅助脚本**: `skills/doubao-share/scripts/slugify.py`

---

### `web-archive` — Web 链接归档

将非豆包的网页 URL 归档到知识库。8 步工作流：访问→提取→格式规范化→index/log/roadmap 更新→链接验证。

**触发条件**: 用户粘贴 URL / 分享网页 / 说"归档"（非豆包链接）

**写入路径**: `knowledge/06_others/sources/`

**依赖**: `web-access`（底层浏览器/抓取）、`check/link-validator.py`（链接验证）

---

### `git-submodule-import` — GitHub 仓库 Submodule 导入

将外部 GitHub 仓库（书籍/资料/工具）以 submodule 方式导入 `import/<repo>/`，支持国内镜像通道（ghproxy 等）、版本固定、元信息归档与降级预案（网络不可达时登记元数据 + 待网络恢复一键填充）。

**触发条件**: 用户要求导入 GitHub 仓库 / 分享开源书籍或资料仓库 / 需要固定版本的外部参考代码

**脚本**: `scripts/git-submodule-import/import-repo.sh`（标准导入）、`update-submodules.sh`（批量更新）

**降级场景**: 直连不通时走 `git ls-remote` 探测镜像 → 手动登记 .gitmodules + gitlink → `git submodule update --init` 恢复

**经验备忘**: 探测用 git ls-remote（勿用 curl 网页码）；大仓库（>100MB）镜像下载不现实，登记元数据待网络

---

### `web-access` — 联网操作入口

所有联网操作的基础入口。提供真实浏览器环境（Selenium/ChromeDriver），处理搜索、网页抓取、登录后操作、动态渲染页面。

**触发条件**: 任何需要联网/浏览器/搜索的任务

**注意**: 登录状态通过 cookie/localStorage 持久化，一次登录后续复用

---

### `knowledge-wiki` — 知识 wiki 管理

管理和维护个人知识库（创建/更新/重组页面，维护 index/log），将有沉淀价值的信息结构化为知识页面。

**触发条件**: 用户分享文章/文档/问"整理知识"/对话产生值得保存的洞察

**写入路径**: `knowledge/concepts/`（跨模块概念）、`knowledge/methodology/`（方法论）

---

## 📝 2 类：专题创作与写作

### `deep-tech-writer` — 深度技术分析

创建深度技术文档（协议/芯片/系统），六步工作流：搜集权威源→原理深潜→强逻辑编排→量化数据+来源→自检迭代→格式打磨。

**触发条件**: 深度分析/原理深潜/技术调研/全面分析"不要流于形式"

**质量要求**: 每条断言有出处、量化数据有四要素(数值+单位+基线+条件)、代码块纯 ASCII、TOC 顶部 + Changelog 底部

**关联脚本**: `scripts/check/doc-quality.py`

---

### `knowledge-doc-writer` — 知识库文档写作

服务器/AI 专题知识库文档的通用写作 Skill。6 步标准化工作流：知识库提取→联网补充→内容编排→格式检查→索引更新→知识复用。

**触发条件**: 创建/扩充服务器/AI/基础设施技术文档、专题调研报告

**写入路径**: `knowledge/02_rd/`（服务器研发）、`knowledge/03_AI/`（AI 技术）

**关联脚本**:
- `skills/knowledge-doc-writer/scripts/check_paths.py` — 路径/数据源验证
- `skills/knowledge-doc-writer/scripts/check_format.py` — 通用格式规范检查

---

### `mckinsey-research` — 麦肯锡级市场研究

12 个专用提示词全流程市场研究与战略分析：TAM → 竞品 → 客户画像 → 定价 → GTM → 财务模型 → 风险评估 → SWOT → 市场准入。

**触发条件**: 市场调研/竞品分析/商业分析/TAM 分析/可行性研究/商业计划书

**输出**: 完整的战略分析报告（HTML 格式，保存至 artifacts/research/）

---

### `competitor-analysis` — 竞品 SEO/GEO 分析

竞品 SEO/GEO 差距分析：关键词、内容、反链、AI 引用、流量份额。

**触发条件**: 竞品分析/竞争对手/找 SEO 差距

---

### `thesis-helper` — 论文写作助手

论文大纲生成、文献综述框架、摘要生成、引用格式转换、格式规范检查、答辩准备。

**触发条件**: 写论文/论文大纲/文献综述/摘要/引用/答辩准备

---

### `official-writing` — 党政机关公文写作

国家标准格式规范（GB/T 9704）公文模板、写作技巧。

**触发条件**: 党政公文/通知/报告/请示/函/纪要等公文写作

**输出格式**: 严格按国标格式（标题/正文/附件/落款/页码）

---

### `fault-diagnosis` — 系统化故障排查

五层故障排查方法论：事件墙→鱼骨图+5Why→变更回溯→多维数据关联→AIOps 模式。

**触发条件**: 系统/软件/硬件故障、宕机、异常、RCA、排障

---

### `complex-system-function` — 复杂系统分析

"Function as Life-Giving Mechanism" 框架：输入→功能→输出→反馈四维分析、经验复用、成本校准决策。

**触发条件**: "活的系统"/function/输入输出/反馈/系统分析/经验复用/场景变量

---

### `method-analysis` — 方法论制定与固化

将 MECE/第一性原理/五看三定/鱼骨图等框架固化为知识库方法论文档。

**触发条件**: 方法论制定/固化/验证/优化

---

### `industry-insight` — 行业洞察与商业机会

基于"五看三定"方法论的行业深度洞察。技术原理→演进路径→商业化评估→落地路径→监控指标。

**触发条件**: 行业洞察/市场调研/商业机会/赛道分析/技术商业化

**输出**: 专题化报告归档至 `knowledge/01_survey/industry-research/`

---

### `arch-presentation-builder` — 架构汇报材料生成

从技术分析数据生成 PPT 风格的架构评审汇报材料。MECE 拆解竞争力→指标体系→技术指标分解。

**触发条件**: 汇报材料/汇报PPT/架构汇报/指标体系/竞争力拆解

---

## 🔄 3 类：数据处理与提取

### `light-data-engineering` — 数据处理与数据集构建

数据清洗、缺失/异常值处理、特征工程、数据增强、数据集划分与自建。

**触发条件**: 数据清洗/特征工程/数据集构建/标注规范

---

### `light-result-analysis` — 实验结果分析

对实验数据/模型输出/图表结果进行专业深入分析。不只描述好坏，而是解释原因、亮点、异常、可成为论文亮点之处。

**触发条件**: 实验跑完/需要解读数据/"这些结果说明什么"

---

### `light-file-reading` — 文件读取与理解

读取 Word/PDF/PPTX/Excel/CSV/图片/视频/代码/压缩包等文件，理解结构、逻辑、图表、数据、格式要求。

**触发条件**: 用户提供任何文件/问"这个文件讲了什么"

**常驻生效**: 自动触发，无需显式调用

---

### `markdown-converter` — 格式→Markdown 转换

将 PDF/DOCX/PPTX/XLSX/HTML/CSV/JSON/XML/图片(OCR)/音频(转录)/ZIP/YouTube/EPUB 转换为 Markdown。

**触发条件**: 需要将某格式文件转为 Markdown

**底层库**: `markitdown`（Microsoft 开源库）

---

### `conversation-topic-analyzer` — 对话主题分析

从对话日志中分析主题模式、知识维度提取、操作思维提取、聚类与意图分类。

**触发条件**: 对话分析/主题分析/话题聚类/意图分析/知识维度提取

---

### `session-intent-analysis` — 会话意图分析

定期分析会话日志，提取用户真实意图，识别话题边界和任务切换，生成意图分析报告。

**触发条件**: 意图分析/会话分析/用户需求分析/定期分析

**一键执行**: `bash scripts/intent_analysis/run_all.sh --since <日期>`（导出会话 → 用户问题 CSV → 报告骨架 → Agent 补 LLM 深度解析）

**输出**: `knowledge/weekly-reports/07_kb_stat/06_conversation/`（报告 md + 用户问题 CSV，含时间/问题描述/输入通道）

---

### `tech-learn` — 模式提取与知识保存

从会话中提取可复用的模式，保存为候选 Skill 或指南。

**触发条件**: "保存这个"/"记下来"/"下次遇到这个问题"/经验总结

---

### `tech-evolve` — 模式进化与结构生成

分析重复模式，建议或生成进化后的结构（命令/Skill/Agent）。

**触发条件**: 模式提取/技能进化/命令生成/工作流优化

---

## 🔧 4 类：格式转换与排版

### `pdf` — PDF 全生命周期操作

读取/合并/拆分/旋转/水印/创建/加密/OCR/表单填充。

**触发条件**: 提到 .pdf 文件

**内部脚本**: `skills/pdf/scripts/pdf_*.py`（8 个）

### `docx` — Word 文档创建与编辑

创建/读/编辑 DOCX 文件（样式/编号/追踪修订/表格/域/模板/图片/注释）。

**触发条件**: "Word"/"docx"/需要生成 Word 文档

内部脚本 17 个

### `Word---DOCX` — Word 高级操作

样式/编号/修订/表格/章节/兼容性校验。与 `docx` 互补。

**触发条件**: Word 高级操作/兼容性校验/修订处理

### `pptx` — PPT 创建与编辑

创建/读/编辑/合并/模板/备注/母版/幻灯片管理。

**触发条件**: 提到 .pptx / "幻灯片"/"presentation"/"deck"

**内部脚本**: 13 个

### `xlsx` — 电子表格操作

创建/读/编辑/公式/格式/图表/清洗 XLSX/XLSM/CSV/TSV。

**触发条件**: 提到 .xlsx/.csv/.tsv/需要处理表格数据

**内部脚本**: 11 个

### `light-slides` — PPT 内容与设计

从内容层面设计完整 PPT：封面/目录/过渡/内容/图表/流程/时间线/对比/团队/结论/致谢。按主题选择风格。

**触发条件**: 做 PPT/答辩/汇报/路演幻灯片

### `light-typesetting` — 论文排版

根据目标期刊/会议/学校/比赛要求做 LaTeX 或 Word 排版，编译导出最终 PDF/Word。

**触发条件**: 套模板/排版/编译错误/导出

### `markdown-format-standards` — Markdown 格式标准化

代码块纯 ASCII 规则、方框字符对齐、中文/ASCII 混排修复。

**触发条件**: Markdown 格式规范/对齐/代码块变形

**关联脚本**: `scripts/check/md-format.py`

### `markdown-converter` — 通用→Markdown 转换

见 3 类

---

## ✅ 5 类：检查、审查与维护

### `doc-reviewer` — 文档五层审查

五层审查：结构层(🔴)+ 逻辑层(🟡)+ 来源层(🔴)+ 知识层+ 推理层。覆盖 13 条逻辑谬误。

**触发条件**: 审查/评审/确认合理性/检查格式/review 文档

**关联脚本**: `scripts/check/doc-review.py`

---

### `light-self-review` — 自动反思与自检

常驻技能，任何产出交付前自动执行五层管道自检（L1信源→L2注意→L3知识→L4推理→L5输出+LX元层），覆盖 A-J 十类失效模式。

**触发条件**: 常驻，所有任务收尾自动触发

---

### `light-consistency` — 一致性维护

确保论文/PPT/图表/代码/项目文档之间术语、风格、逻辑线索、创新点表述一致。

**触发条件**: 常驻，所有多产出任务生效

**检测六大类**: SUBSTITUTION（替换）/ METRIC_NAME（指标名）/ METRIC_VALUE（指标值）/ CONTRIBUTION_DRIFT（贡献漂移）/ GROSS_MISMATCH（重大不匹配）/ COVERAGE_GAP（覆盖缺口）

---

### `light-research-ethics` — 科研伦理审查

检查学术不端、数据造假、图片重复使用、引用不规范、隐私泄露、结论夸大、过度包装等。

**触发条件**: 常驻，所有科研任务默认生效

---

### `constraint-verifier` — 约束验证器

检测 AI 行为是否偏离 AGENT.md/RULE.md/USER.md/MEMORY.md 等约束，按 A-J 十类失效模式归类。

**触发条件**: 怀疑"AI 没遵守约束"/需要做合规审计

---

### `depth-completer` — 内容深度补齐

检测文档是否停留在"框架堆名词"层面而非深入原理，基于知识库挖掘和第一性原理推导补充深度。

**触发条件**: "面面俱到但都不深"/"名词堆叠但无原理分析"

---

### `knowledge-health-check` — 知识库健康检查

6 维扫描：链接/表格/格式/日志排序/文件位置/整体健康度。

**关联脚本**: `scripts/check/kb-health.py`

---

### `knowledge-special-reports` — 专项报告生成

生成并维护 4 份专项报告：目录演化、代码提交分析、领域焦点迁移、维度完整性。

**触发条件**: 生成本/更新专项报告/知识库健康统计

**定时触发**: 飞书定时任务，每周/双周更新

---

### `roadmap-maintainer` — 服务器知识图谱维护

维护 14 域 × TR1-TR6 生命周期的知识矩阵、热图、交叉链接。

**触发条件**: 添加新域/重组矩阵/更新热图/清理格式

**关联脚本**: `scripts/check/roadmap-structure.py`

---

### `knowledge-index-manager` — 统一索引管理（合并技能，推荐）

> **替代了**原 `index-deep-analyzer` + `index-log-maintainer` + `index-rebuilder` 三个技能。统一入口，消除重叠。

4 种操作模式：**audit**（审计检查）· **rebuild**（全量重建）· **normalize**（6 阶段规范化）· **maintain**（增量修复）

**触发条件**: index 管理/index 重建/日志格式化/索引修复/知识库规范化/文件迁移/目录优化

**关联脚本**: `knowledge-normalizer.py`, `index-log-normalizer.py`, `analyze-index-coverage.py`, `link-validator.py`, `link-fixer.py`, `link-augmenter.py`, `md-format.py`, `reformat-log.py`, `directory-architect.py`, `subdir-nav-fixer.py`, `tools/mv-knowledge.py`

---

> **以下三个技能已废弃，保留仅用于向后兼容**。新操作请使用 `knowledge-index-manager`：

### ~~`index-deep-analyzer`~~ ⚠️ 已废弃

功能已合并至 `knowledge-index-manager`。使用原触发条件会自动路由到合并技能。

---

### ~~`index-log-maintainer`~~ ⚠️ 已废弃

功能已合并至 `knowledge-index-manager`。使用原触发条件会自动路由到合并技能。

---

### ~~`index-rebuilder`~~ ⚠️ 已废弃

功能已合并至 `knowledge-index-manager`。使用原触发条件会自动路由到合并技能。

---

### `log-reformatter` — log.md 格式统一

将 log.md 统一为标准 changelog 格式（三列表格，时间正序，2026-08-15 起）。

**触发条件**: 格式化 log/log 排序/log 重整

**关联脚本**: `scripts/check/reformat-log.py`

---

### `directory-optimizer` — 目录架构优化

MECE 分层、跨域耦合分析、阅读路径设计、决策框架索引。

**触发条件**: 目录优化/MECE 分析/关联矩阵/阅读路径/目录重构

---

### `profile-optimizer` — 身份文件优化

优化 AGENT.md/USER.md/MEMORY.md/RULE.md 四个身份文件的结构和内容。

**触发条件**: 优化身份文件/重构配置文件/从对话提取用户模式

---

### `weekly-report-generator` — 周报生成

生成结构化周报，汇总知识库活动与洞察。

**触发条件**: "生成周报"/每周日定时触发

**写入路径**: `knowledge/weekly-reports/`

---

### `monthly-report-generator` — 月度报告生成

生成覆盖 **5 大维度** 的知识库月度报告：① 知识库变更情况（提交增/删/改、规模变化、图表）② 领域侧重点 ③ 质量报告分析 ④ 月度关键行业洞察 ⑤ 待办事务列表。

**触发条件**: "生成月报"/"月度报告"/每月最后一天 23:20 定时触发

**依赖脚本**: `scripts/monthly-report-data-gather.sh`（采集 9 个数据文件到 `tmp/kb-monthly-data-{YYYY-MM}/`）

**写入路径**: `knowledge/weekly-reports/02_monthly/{YYYY-MM}-monthly-report.md`

```text
scheduled(last-day 23:20) -> monthly-report-data-gather.sh -> tmp/kb-monthly-data-{YM}/
                                                                    |
                                                                    v
                                                  monthly-report-generator(SKILL)
                                                                    |
                                                                    v
                              knowledge/weekly-reports/02_monthly/{YM}-monthly-report.md
```

---

### `session-keeper` — 会话持久化

保存多会话工作进度，支持断点续传。

**触发条件**: 跨会话任务/进度保存/恢复

---

## 🔍 6 类：数据查询与工具

### `weather-query` — 天气查询

中国各地实时天气/预报/温度/湿度/风速/空气质量。

**触发条件**: "天气"/"今天温度"/查询气象

### `data-query` — 多源数据查询

汇率/农历/历史事件/百科/油价/金价/化学元素。

**触发条件**: "汇率"/"农历"/"历史今天"/"百科"/"油价"/"金价"

### `daily-news-60s` — 每日新闻

每天 60 秒读懂世界——15 条精选国内外新闻 + 每日微语。

**触发条件**: "新闻"/"今天发生了什么"/"60秒"

### `github-activity-report` — GitHub 开源活动日报

每日 06:50 定时任务（ID `9d0458ca`）自动生成。聚合 8 领域（AI/部件/项目管理/Agent/算力平台/运维/云计算/操作系统）热点仓库的最新亮点项目与成熟项目关键提交，输出到 `knowledge/01_survey/github/YYYY-MM-DD.md`。数据策略：GitHub REST API（≤35 req/日）→ web_fetch 直连 trending/commits 页 → 聚合镜像兜底。

**触发条件**: "GitHub日报"/"开源项目进展"/"热点仓库"

### `hot-topics` — 热搜榜单

微博/知乎/百度/抖音/今日头条/B 站实时热搜。

**触发条件**: "热搜"/"热门"/"微博热榜"/"知乎热榜"

### `media-info` — 音乐与影视信息

网易云音乐排行榜/歌词搜索/电影票房/电视剧收视/网剧排行。

**触发条件**: "音乐排行"/"歌词"/"票房"/"收视率"

### `entertainment` — 娱乐内容

一言名句/英文笑话/中文段子/运势预测/KFC 梗文案/摸鱼日历。

**触发条件**: "来点段子"/"笑话"/"运势"/"摸鱼"/"KFC 文案"

### `wechat-article-search` — 公众号文章搜索

搜索微信公众号文章（科技/AI/社会/财经/教育/职场）。

**触发条件**: "公众号"/"微信文章"/找某主题的中文公众号内容

### `reddit-insights` — Reddit 洞察

通过 reddapi.dev API 语义搜索 Reddit 内容：用户痛点、利基市场、真实反馈、情感分析。

**触发条件**: Reddit 搜索/痛点发现/市场反馈/"what do people think about"

### `baidu-scholar-search` — 百度学术检索

中英文文献检索（学术期刊/会议论文/学位论文）。

**触发条件**: 找论文/文献调研/学术搜索

### `utility-tools` — 实用工具

IP 查询/文本翻译/二维码生成/哈希计算/网页元数据/域名 WHOIS/密码生成。

**触发条件**: "翻译"/"IP 查询"/"二维码"/"哈希"/"whois"/"生成密码"

---

## ☁️ 7 类：平台集成

### `notion` — Notion API 集成

通过官方 Notion API 操作页面和数据库（CRUD）。

**触发条件**: Notion 操作/页面管理/数据库查询

**依赖**: Notion API Key 配置

---

### `apple-reminders` — Apple 提醒事项

通过 `remindctl` CLI 管理 macOS 提醒事项（list/add/edit/complete/delete）。

**触发条件**: "提醒事项"/"reminder"/macOS 提醒

---

### `email-daily-summary` — 邮件摘要

登录邮箱（Gmail/Outlook/QQ Mail）生成每日邮件摘要。

**触发条件**: "邮件摘要"/"查看邮件"/"today's email"

**依赖**: 邮箱账号密码配置

---

### `bdpan-storage` — 百度网盘

百度网盘文件管理：上传/下载/转存/分享/搜索/移动/复制/重命名/创建文件夹。

**触发条件**: "百度网盘"/"网盘"涉及文件操作

**依赖**: 百度网盘 API 配置

---

### `feishu-workspace` ⚠️ — 飞书集成

通过飞书 OpenAPI 操作文档、表格、多维表格 CLI。

**触发条件**: 飞书文档/表格操作

**配置需求**: `FEISHU_APP_ID` + `FEISHU_APP_SECRET`

---

### `github` ⚠️ — GitHub 操作

仓库管理/Fork/PR/Release/Issue 评论。

**配置需求**: `GITHUB_TOKEN`

---

## 🏗️ 8 类：系统/流程编排

### `light-orchestrator` — 任务编排器

跨多阶段的大任务编排。按 CONVENTIONS 阶段主线调用对应技能，设强制检查点（决策点+确认点），维护产物台账。

**触发条件**: "从这个数据做到论文"/跨阶段大任务/"继续"/"接手"

**判断规则**: 大任务走 Pipeline，小任务（改摘要/画图/查引用）直接路由单技能

---

### `pipeline-orchestrator` — AI 生产流水线

串联 6 个阶段 Skill 的完整生产流水线：input-qa → multi-path → convergence → verification-loop → constraint-enforcer → expert-gate。

**触发条件**: "全流程"/"流水线"/"pipeline"/需断点续传的复杂任务

**不用于**: 单阶段任务、简单问答

---

### `pipeline-input-qa` — 流水线阶段 1：输入质量门

验证输入完整性、来源可信度、一致性、可行性。

---

### `pipeline-multi-path` — 流水线阶段 2：多路并行

将任务拆分为多个独立处理路径并行执行，隔离上下文和 Token 预算。

---

### `pipeline-convergence` — 流水线阶段 3：汇聚

合并多路并行结果——加权来源可信度冲突消解、最佳版本选择、Cross-validate。

---

### `pipeline-verification-loop` — 流水线阶段 4：Ralph 循环验证

Plan→Do→Check→Act 四步循环，自动迭代直到满足客观验证标准。

---

### `pipeline-constraint-enforcer` — 流水线阶段 5：约束引擎

三层约束强制执行：安全红线(不可触碰)+质量标线(必须遵守)+工程约束(最佳实践)。

---

### `pipeline-expert-gate` — 流水线阶段 6：专家把关（终审）

生成结构化专家审查清单、标注 AI 生成边界、提供退回路由。

---

## 🖥️ 9 类：服务器/硬件分析

### `si-analyzer` — 信号完整性分析

高速互连信号完整性分析：眼图/抖动/串扰/时序分析。覆盖 PCIe/SerDes/NVLink。

**触发条件**: 信号完整性/眼图/抖动/串扰

---

### `interconnect-analyzer` — 系统互连分析

CPU-GPU 互连分析：PCIe/CXL/UPI/QPI/系统拓扑/带宽/延迟。

**触发条件**: 互连分析/PCIe/CXL/UPI/QPI/系统拓扑

---

### `cache-coherence-analyzer` — 缓存一致性分析

多核/多插槽缓存一致性协议分析：MESI/MOESI/伪共享/NUMA。

**触发条件**: 缓存一致性/MESI/MOESI/NUMA/内存层次

---

### `rdma-analyzer` — RDMA 分析

高性能网络 RDMA 分析：RoCE/InfiniBand/NVLink 性能/延迟/带宽。

**触发条件**: RDMA/RoCE/InfiniBand/GPU 通信/远程内存访问

---

### `server-competitor-analysis` — 服务器竞品分析

服务器软/硬件/固件三维竞品分析框架：信息采集→维度对比→深度解读→报告生成。

**触发条件**: 服务器竞品对比/对标分析/AI 服务器竞品

---

## 🔬 10 类：科研与竞赛

### `light-idea-generation` — 研究 Idea 生成

根据项目实际情况提出有潜力、有差异化、有亮点的研究 Idea。结合已有基础、数据条件、技术能力、时间周期、发表/竞赛目标。

**触发条件**: "这个方向能做什么"/需要创新点/研究思路

---

### `light-idea-critique` — Idea 严格审查

以顶刊/顶会审稿人标准判断 Idea 是否真有突破。八维度加权打分、五视角对抗、反谄媚硬协议。

**触发条件**: "这个 idea 行不行"/"帮我挑刺"/m03 产出后必须用

---

### `light-research-plan` — 研究方案设计

将已确认可行的 Idea 拆解为完整可执行的科研流程。研究目标→技术路线→数据流程→实验设计→时间安排→风险备选。

**触发条件**: Idea 已通过审、需要做实验规划

---

### `light-paper-drafting` — 论文初稿撰写

撰写/重写/自检论文初稿或单章节（标题/摘要/引言/相关工作/方法/实验/结果/讨论/结论/局限/未来工作）。五种模式：full/outline-only/abstract-only/section-redraft/self-review。

**触发条件**: "写论文"/"写摘要"/"写引言"/重写某章

---

### `light-paper-polishing` — 论文润色

分模块润色：语言→逻辑→结构→创新点强化→论证补强→摘要精炼→实验分析深化→结论提升。

**触发条件**: "帮我改论文"/"这段话不通顺"/"创新点不突出"

---

### `light-figure-planning` — 图表规划

规划论文应该做哪些图/表、插在哪里、各起什么作用。从审稿人角度判断哪些必做、哪些冗余。

**触发条件**: "需要画什么图"/图表规划/论文配图

---

### `light-figure-drawing` — 专业绘图

用 Python(matplotlib/seaborn/plotly/altair)/R(ggplot2)/MATLAB/Visio/Origin/LaTeX TikZ/Illustrator/PowerPoint 绘制专业论文图表。

**触发条件**: "画图"/需要把规划好的图实际画出来

---

### `light-citation` — 引用规划与管理

审查引用关联度/真实性/权威性/时效性/数量。生成 BibTeX/EndNote/GB-T 7714/APA/IEEE。

**触发条件**: 参考文献/bibtex/引用格式

---

### `light-review-rebuttal` — 审稿模拟与返修

投稿前模拟审稿 + 收到真实意见后制定返修策略 + 逐条写 response letter。

**触发条件**: "帮我审审"/"模拟审稿"/收到审稿意见做返修

---

### `light-venue-matching` — 投稿定位

根据论文质量/方向/创新度/实验完整性/语言/预算推荐期刊/会议。给出冲刺/稳妥/保底分层选择。

**触发条件**: "投哪个期刊"/"投哪个会"/投稿规划

---

### `light-competition` — 竞赛与项目申报

写申报书/商业计划书/路演 PPT/答辩稿/技术路线/创新点/可行性分析/市场分析/研究基础/经费预算。

**触发条件**: 互联网+/挑战杯/大创/创新创业/建模竞赛

---

### `light-ip-application` — 软著与专利申请

软著：软件名称/功能说明/操作说明书/源代码/界面截图。专利：判断发明/实用新型/外观，权利要求草案。

**触发条件**: "申请软著"/"写专利"/知识产权申报

---

### `patent-disclosure-writer` — 专利交底书撰写

五段式格式（发明名称→技术领域→现有技术→发明内容→保护关键点）生成符合审查要求的交底书。

**触发条件**: "写专利交底书"/"技术交底书"

---

### `light-project-structure` — 项目文件夹整理

规划 data/src/models/results/figures/docs/paper/ppt/patent/experiments 等目录，保证可复现。

**触发条件**: 新建项目/整理项目结构

---

### `light-tool-selection` — 工具选择（常驻）

根据任务自动判断最适合的工具——搜索/Python/R/MATLAB/LaTeX/Word/Excel/PowerPoint 等。

**触发条件**: 常驻，所有任务后台生效

---

### `light-backend-coding` — 后端代码编写

实验代码/模型代码/数据处理/可视化/后端接口。逻辑清晰、安全、可读、可维护。

**触发条件**: 写代码/模型实现/数据处理/后端接口

---

### `light-frontend-design` — 前端界面设计

独特吸睛的前端设计。科技感/学术感/农业智慧化/数据可视化/极简/玻璃拟态等风格。

**触发条件**: 前端界面/项目展示页/大屏可视化/小程序 UI/答辩演示

**技术栈**: Tailwind v4 / shadcn/ui / Next.js / React / Vite

---

### `light-system-design` — 后端系统设计

ER 图/数据表/接口文档/权限/日志/异常/部署。适合科研系统/管理系统/数据分析平台。

**触发条件**: 系统架构/数据库设计/接口设计/部署方案

---

## 🔧 11 类：技能生命周期管理

### `skill-creator` — 技能创建/安装/更新

创建新 Skill、从 URL 安装、更新或重构现有 Skill。

**触发条件**: "安装这个 skill"/"创建一个 skill"/"更新技能"

---

### `open-source-skill-packer` — 开源→Skill 封装

将 GitHub 开源项目封装为可复用的 Skills。需求→搜索→封装→验证→迭代。

**触发条件**: 把一个 GitHub 项目变成 Skill

---

### `skill-security-vetter` — Skill 安全审查

安装或使用 Skill 前扫描恶意代码、API 密钥泄露、文件越权、shell 执行。

**触发条件**: 安装 Skill 前安全检查

---

### `skill-evolver` / `evolver` — Skill Agent 自进化引擎

自动识别短板、优化策略、迭代进化。基于 GEP 基因组进化协议。

**触发条件**: 自进化/自动优化/迭代进化

---

## 🔌 12 类：插件（需 LINKAI_API_KEY）

以下技能需要通过 LinkAI 平台 API Key 和特定插件进行调用：

| Skill | 能力 | 调用方式 |
|:------|:-----|:---------|
| `plugin-antv` | AntV 可视化（15 种图表） | AI 自动路由 |
| `plugin-chart` | 图表生成（折线/饼图/柱状） | AI 自动路由 |
| `plugin-baidu-map` | 百度地图（地理编码/路径规划） | AI 自动路由 |
| `plugin-bilibili-search` | B 站视频搜索 | AI 自动路由 |
| `plugin-enterprise-search` | 企业工商信息查询 | AI 自动路由 |
| `plugin-gemini-image` | Gemini 图片生成与编辑 | AI 自动路由 |

**配置方法**: `env_config set LINKAI_API_KEY <your_key>`

---

## ⏳ 可用但未就绪

### 缺 API Key / 环境变量

以下 Skill 已安装但**缺少环境变量**，配置后即可使用：

| Skill | 缺失配置 | 优先级 |
|:------|:----------|:------:|
| `github` | GITHUB_TOKEN | 🟠 高频 — PR/Issue 操作 |
| `baidu-search` | BAIDU_API_KEY | 🟡 备选 — 已有 web_access 替代 |
| `baidu-baike-data` | BAIDU_API_KEY | 🟡 备选 — 已有 web_fetch 替代 |
| `feishu-workspace` | FEISHU_APP_ID + FEISHU_APP_SECRET | 🟢 低频 — 飞书集成 |
| `image-generation` | 任一：OPENAI/GEMINI/ARK/DASHSCOPE/MINIMAX/LINKAI | 🟢 低频 — 偶需图片 |
| `plugin-bilibili-search` | LINKAI_API_KEY | 🟢 低频 |
| `plugin-gemini-image` | LINKAI_API_KEY | 🟢 低频 |
| `plugin-baidu-map` | LINKAI_API_KEY | 🟢 低频 |
| `plugin-enterprise-search` | LINKAI_API_KEY | 🟢 低频 |
| `plugin-antv` | LINKAI_API_KEY | 🟢 低频 |
| `plugin-chart` | LINKAI_API_KEY | 🟢 低频 |

### 缺运行时（降级可用）

以下 Skill 有**可选的运行时依赖**，缺失时核心功能仍可用，部分高级功能降级：

| Skill | 缺失运行时 | 影响范围 | 替代方案 |
|:------|:-----------|:---------|:---------|
| `light-slides` | LibreOffice（soffice） | pptx→PDF 转换 | 直接用 pptx 格式交付 |
| `markdown-converter` | Pandoc | 特定格式间转换（如 .docx→.md） | 已有 python 实现替代 |
| `light-typesetting` | LaTeX 发行版（pdflatex/xelatex） | PDF 编译 | 用 Word/docx 排版替代 |

---

## 🔍 附：按用途快速查找

### 我正在... | 适合的 Skill
|:---|:---|
| 写论文 | `light-paper-drafting` + `light-figure-planning` + `light-citation` + `light-typesetting` |
| 做 PPT 答辩 | `light-slides` + `light-consistency` + `arch-presentation-builder` |
| 做市场调研 | `industry-insight` / `mckinsey-research` |
| 做竞品分析 | `server-competitor-analysis` / `competitor-analysis` |
| 归档链接/文档 | `web-archive` / `doubao-share` / `knowledge-wiki` |
| 深度技术文档 | `deep-tech-writer` / `knowledge-doc-writer` |
| 文档检查 | `doc-reviewer` + `light-self-review` + `depth-completer` |
| 查资料 | `light-literature-search` / `baidu-scholar-search` / `wechat-article-search` |
| 数据分析 | `light-data-engineering` + `light-result-analysis` + `light-figure-drawing` |
| 竞赛/申报 | `light-competition` + `light-ip-application` + `light-frontend-design` |
| 系统设计 | `light-system-design` + `light-backend-coding` + `light-frontend-design` |
| 服务器分析 | `si-analyzer` / `interconnect-analyzer` / `cache-coherence-analyzer` / `rdma-analyzer` |
| 故障排查 | `fault-diagnosis` + `constraint-verifier` |
| 查天气/新闻/热搜 | `weather-query` / `daily-news-60s` / `hot-topics` |
| 文件格式转换 | `markdown-converter` + `pdf`/`docx`/`pptx`/`xlsx` |
| 知识库维护 | `knowledge-health-check` + `index-log-maintainer` + `log-reformatter` + `constraint-check` |

---

## 📊 总览指标

| 指标 | 数值 |
|:-----|:----:|
| **总技能数** | **120 个**（已配置） |
| **技能目录** | `skills/` 下 119 个目录 |
| **含内部脚本的技能** | ~51 个 |
| **来源分布** | custom(80) / clawhub(13) / cowhub(9) / github(8) / linkai(6) |
| **待激活**（缺 API Key / 环境变量） | 11 个 |
| **未就绪**（缺运行时，降级可用） | 3 个（soffice/pandoc/latex） |

---

## 📦 技能来源分布

| 来源 | 数量 | 说明 | 典型技能 |
|:-----|:----:|:------|:---------|
| 🏗️ **custom**（手写） | 80 | 通过对话逐步封装为可复用工作流，核心技能 | `deep-tech-writer` · `knowledge-wiki` · `doc-reviewer` |
| 📦 **clawhub**（导入） | 13 | 从 GitHub 开源项目封装 | `mckinsey-research` · `notion` · `apple-reminders` |
| 🤖 **cowhub**（生成） | 9 | 系统从对话中提取模式自动生成 | `knowledge-sync` · `session-keeper` · `light-memory-pm` |
| 🌐 **github**（直接） | 8 | GitHub 仓库直接引用 | `Architecture` · `frontend-design` · `karpathy-guidelines` |
| 🔌 **linkai**（插件） | 6 | LinkAI 平台插件（需 LINKAI_API_KEY） | `plugin-antv` · `plugin-chart` · `plugin-bilibili-search` |
| 🧬 **自进化** | 🚧 | `skill-evolver` 自动识别短板、优化策略、迭代进化 | 待激活 |

---

## 🧩 技能分类综述

| 分类 | 数量 | 核心 Skills | 典型场景 |
|:-----|:----:|:------------|:---------|
| 📝 **文档处理** | 8 | `docx` · `pptx` · `pdf` · `xlsx` · `markdown-converter` · `markdown-format-standards` | Word/PPT/PDF/Excel 全生命周期 |
| 🔬 **深度技术** | 16 | `deep-tech-writer` · `knowledge-doc-writer` · `industry-insight` · `depth-completer` · `fault-diagnosis` | 深度技术分析报告撰写 |
| 📊 **行业分析** | 6 | `mckinsey-research` · `competitor-analysis` · `server-competitor-analysis` · `reddit-insights` | 麦肯锡级市场研究/竞品分析 |
| 📖 **论文辅助** | 16 | `light-paper-drafting` · `light-paper-polishing` · `light-review-rebuttal` · `light-venue-matching` · `light-citation` · `light-figure-planning` · `thesis-helper` | 论文起草/润色/审稿/投稿全链路 |
| 💻 **研发编码** | 9 | `light-backend-coding` · `light-frontend-design` · `light-system-design` · `light-project-structure` · `tech-planner` | 后端/前端/系统/项目结构 |
| 🧩 **硬件分析** | 7 | `si-analyzer` · `interconnect-analyzer` · `rdma-analyzer` · `cache-coherence-analyzer` | SI/互联/RDMA/缓存一致性 |
| 🔍 **质量审查** | 9 | `doc-reviewer` · `knowledge-health-check` · `knowledge-index-manager` · `log-reformatter` · `markdown-format-standards` · `light-self-review` · `constraint-verifier` | 文档/知识库/格式/逻辑审查（原3Skill合并为1） |
| 💡 **创新辅助** | 8 | `light-idea-generation` · `light-idea-critique` · `light-research-plan` · `patent-disclosure-writer` · `light-ip-application` · `light-competition` | 想法生成/批判/研究计划/专利 |
| 🌐 **联网工具** | 8 | `web-access` · `web-archive` · `doubao-share` · `email-daily-summary` · `wechat-article-search` · `bdpan-storage` | 网页访问/归档/豆包/邮箱/网盘 |
| 📅 **日常工具** | 18 | `weather-query` · `daily-news-60s` · `hot-topics` · `media-info` · `entertainment` · `data-query` · `utility-tools` | 天气/新闻/热搜/影视/翻译/码 |
| 🔧 **系统引擎** | 12 | `skill-creator` · `open-source-skill-packer` · `skill-evolver` · `skill-security-vetter` · `light-memory-pm` · `light-orchestrator` · `pipeline-orchestrator` · `session-keeper` | Skills 管理/记忆/编排/流水线 |

---

---

## 🧩 技能关系架构

Skills 之间存在 5 种核心关系：**流水线链式**（前后串联）、**替代/合并**（新旧交替）、**互补组合**（同时使用）、**竞品替代**（按需选择）、**依赖调用**（一个依赖另一个）。

### 1. 流水线链式关系 (Pipeline Chains)

多个 Skills 按固定顺序串联，前一个的输出是后一个的输入：

```text
【研究全链路】
light-literature-search → knowledge-doc-writer → doc-reviewer → depth-completer → light-self-review
  搜索                   文档创作                质量审查        深度补全          自检

【论文全链路】
light-idea-generation → light-idea-critique → light-research-plan → light-paper-drafting
  Idea 生成              Idea 审查             研究方案设计          论文起草
  → light-figure-planning → light-figure-drawing → light-paper-polishing → light-review-rebuttal
     图表规划                    专业绘图                论文润色                 审稿返修
  → light-citation → light-venue-matching → light-typesetting
     引用管理          投稿定位                 排版

【数据→论文链】
light-data-engineering → light-result-analysis → light-figure-drawing → light-paper-drafting (实验章节)
   数据清洗                结果分析                  专业绘图                 论文

【深度技术文档链】
knowledge-doc-writer → deep-tech-writer → doc-reviewer → depth-completer → light-consistency → light-self-review
  素材收集                深度创作                 审查             深度补全        一致性         自检

【行业调研链】
industry-insight → knowledge-doc-writer → mckinsey-research (可选)
  行业洞察                文档沉淀                  战略分析

【归档链】
web-access → web-archive / doubao-share → knowledge-wiki (可选)
  网页访问                 归档                    知识整理

【模式发现链】
tech-learn → tech-evolve → skill-creator
  模式提取                 模式进化                  技能创建

【方法论文档链】
method-analysis → knowledge-wiki → depth-completer
  方法论制定                知识存储                  深度增强

【AI 生产流水线】— 最长的链（6 阶段）
pipeline-input-qa → pipeline-multi-path → pipeline-convergence
  → pipeline-verification-loop → pipeline-constraint-enforcer → pipeline-expert-gate
```

### 2. 替代/合并关系 (Supersede/Replace)

| 旧 Skill(s) | 被替代者 | 新 Skill | 合并日期 |
|:------------|:---------|:---------|:--------:|
| `index-deep-analyzer` | ❌ 废弃 | → `knowledge-index-manager` (audit+normalize 模式) | 2026-07 |
| `index-log-maintainer` | ❌ 废弃 | → `knowledge-index-manager` (audit+maintain 模式) | 2026-07 |
| `index-rebuilder` | ❌ 废弃 | → `knowledge-index-manager` (rebuild 模式) | 2026-07 |

### 3. 互补组合关系 (Complementary)

这些 Skills **常同时出现在同一任务链中**，每个负责不同维度：

| 组合名称 | 涉及 Skills | 分工说明 |
|:---------|:------------|:---------|
| **五层审查栈** | `doc-reviewer` + `depth-completer` + `light-self-review` + `light-consistency` + `constraint-verifier` | doc-reviewer → 逻辑谬误；depth-completer → 深度；self-review → 自检；consistency → 一致性；verifier → 约束合规 |
| **创作双引擎** | `deep-tech-writer` + `knowledge-doc-writer` | 前者从零创作，后者从知识库出发，可接力 |
| **图表双步** | `light-figure-planning` + `light-figure-drawing` | 先规划图表体系，再逐一绘制 |
| **内容+格式双轨** | `light-slides` + `pptx` | 前者生成内容骨架，后者实现格式与排版 |
| **PPT 汇报双模式** | `light-slides` + `arch-presentation-builder` | 前者通用PPT，后者专用架构评审汇报 |
| **商业分析三件套** | `mckinsey-research` + `industry-insight` + `competitor-analysis` | McK → 战略；Insight → 行业；Competitor → 竞品 |
| **服务器分析四件套** | `si-analyzer` + `interconnect-analyzer` + `cache-coherence-analyzer` + `rdma-analyzer` | 从信号完整性到互连到缓存到远程内存 |
| **Word 双 Skill** | `docx` + `Word---DOCX` | 前者通用，后者处理高级/兼容性场景 |
| **知识库治理全家桶** | `knowledge-index-manager` + `knowledge-health-check` + `log-reformatter` + `directory-optimizer` | 索引管理 + 健康扫描 + 日志格式化 + 目录优化 |
| **物联网关** | `web-access` + `web-fetch` + `browser` | 三种联网手段覆盖全场景 |

### 4. 竞品/替代关系 (Competing Alternatives)

同一任务类型有多个 Skill 可供选择，根据场景优先级选择：

| 任务场景 | 首选 Skill | 备选 Skill | 选择依据 |
|:---------|:-----------|:-----------|:---------|
| **深度技术文档** | `deep-tech-writer`（从零创作） | `knowledge-doc-writer`（从知识库出发） | 素材是否已在 KB 中 |
| **市场调研** | `industry-insight`（偏技术商业化） | `mckinsey-research`（偏战略财务） | 需要技术深度还是财务模型 |
| **竞品分析** | `server-competitor-analysis`（硬件方向） | `competitor-analysis`（SEO/GEO 方向） | 技术竞品还是市场竞品 |
| **故障排查** | `fault-diagnosis`（系统化方法） | 直接对话分析（快速判断） | 有足够时间还是快速响应 |
| **知识检索** | `memory_search`（语义检索） | `bash grep`（精准匹配） | 模糊定位还是精确查找 |
| **文件读取** | `light-file-reading`（AI 理解） | `markdown-converter`（格式转换） | 需要理解还是仅转换 |

### 5. 依赖调用关系 (Dependencies)

某些 Skill 在执行时需要调用其他 Skill 作为基础服务：

```text
web-archive ──依赖──→ web-access（获取网页内容）
doubao-share ──依赖──→ web-access（访问豆包链接）
knowledge-special-reports ──依赖──→ memory_search（查询记忆）
weekly-report-generator ──依赖──→ 多个 knowledge/ 读取 + memory_search
deep-tech-writer ──依赖──→ markdown-format-standards（格式检查）
skill-security-vetter ──依赖──→ 文件系统读权限
light-orchestrator ──可选──→ pipeline-orchestrator（大任务转为流水线）
```

---

## 📁 技能目录与路径体系

### 1. `skills/` 目录结构

```
skills/
├── README.md                    ← 本文件：技能使用手册
├── skills_config.json           ← Skill 分类/来源/版本配置元数据
├── doubao-share/                ← 每 Skill 一个目录（127 个）
│   ├── SKILL.md                 ← Skill 定义（触发条件+工作流）
│   └── scripts/                 ← 内嵌脚本（~51 个 Skill 含内部脚本）
├── deep-tech-writer/
│   ├── SKILL.md
│   └── scripts/
├── .../（124 个其他 Skill 目录）
└── extracted/                   ← 提取/暂存 Skill
```

### 2. `scripts/` 目录结构

```
scripts/
├── README.md                    ← 脚本使用说明
│
├── [根级脚本]                   ← 通用/全局脚本（16 个）
│   ├── check_tech_doc_quality.py      ← deep-tech-writer 质量检查
│   ├── knowledge_health_check.py      ← knowledge-health-check 调用
│   ├── review_doc.py                  ← doc-reviewer 文档审查
│   ├── strategy-compliance.py         ← 策略合规检查
│   ├── patch-task-search-strategy.py  ← 定时任务搜索策略补丁
│   ├── check_md_format.py / check_links.py / ...（格式/链接/索引）
│   ├── validate_structure.py          ← roadmap 结构验证
│   ├── reformat_log.py                ← log 格式化
│   ├── clean_duplicates.py / dedup_import.py / ...（去重）
│   └── force_add_toc.py / regenerate_toc.py（目录生成）
│
├── check/                       ← 知识库质量检查脚本群（26 个）
│   ├── link-validator.py        ←    内部链接有效性（H 类）
│   ├── link-fixer.py            ←    内部链接自动修复（H 类）
│   ├── link-augmenter.py        ←    裸文件名→链接增强（H 类）
│   ├── md-format.py             ←    Markdown 格式规范（H 类）
│   ├── kb-health.py             ←    知识库健康综合评分（H 类）
│   ├── reformat-log.py          ←    log 格式化（H 类）
│   ├── knowledge-normalizer.py  ←    6 阶段全量治理（H 类）
│   ├── index-log-normalizer.py  ←    索引日志规范化（H 类）
│   ├── analyze-index-coverage.py←    索引覆盖率分析（H 类）
│   ├── directory-architect.py   ←    目录架构分析（E/H 类）
│   ├── extract-content-metadata.py  ← 内容元数据提取（B 类）
│   ├── extract-index-metadata.py    ← 索引元数据提取（B 类）
│   ├── doc-quality.py           ←    文档质量评分（D 类）
│   ├── doc-review.py            ←    文档审查引擎（D 类）
│   ├── quantitative-check.py    ←    量化数据验证（D 类）
│   ├── ref-drift-detector.py    ←    引用漂移检测（L 类）
│   ├── relation-integrity.py    ←    关系完整性检查（L 类）
│   ├── strategy-compliance.py   ←    策略合规（A 类）
│   ├── roadmap-structure.py     ←    知识图谱结构（H 类）
│   ├── subdir-nav-fixer.py      ←    子目录导航修复（E/H 类）
│   ├── fix-index-urlencode.py   ←    URL 编码修复（H 类）
│   ├── fix-log-ordering.py      ←    log 排序修复（H 类）
│   ├── content-format-normalizer.py ← 内容格式规范化（H 类）
│   └── format-validator.py      ←    格式校验器（H 类）
│
├── discover/                    ← discover 加工管道脚本群（18+ 个）
│   ├── ai-classify.py           ←    AI 批量分类（C 类）
│   ├── ai-extract-keywords.py   ←    AI 提取关键字（C 类）
│   ├── ai-batch-extract-questions.py ← AI 提取问题（C 类）
│   ├── ai-batch-gen-docs.py     ←    问题→文档生成（C 类）
│   ├── ai-batch-enhance.py      ←    批量文档增强（C 类）
│   ├── extract-questions.py     ←    import 问题提取（C/F 类）
│   ├── import-to-knowledge.py   ←    discover→知识库导入（C 类）
│   ├── config.py                ←    共享配置（C 类）
│   ├── stats.py                 ←    统计信息（C 类）
│   └── ...（其他辅助脚本）
│
├── tools/                       ← 通用工具脚本（11 个）
│   ├── mv-knowledge.py          ←    ✅ 知识库文件迁移 CLI（E-01 实现）
│   ├── kb-metadb.py             ←    知识库元数据库构建（B-01 实现）
│   ├── execution-log.py         ←    执行状态日志记录（I-01 实现）
│   ├── errorcodes.py            ←    统一错误码定义（X-11 实现）
│   ├── check-align.py           ←    排版对齐检查
│   ├── fix-align.py             ←    排版对齐修复
│   ├── classify-questions.py    ←    问题分类
│   ├── extract-chat-content.py  ←    对话内容提取
│   ├── extract-user-questions.py←    用户问题提取
│   ├── chromedriver-setup.py    ←    ChromeDriver 安装
│   └── html-to-markdown.py      ←    HTML→Markdown 转换
│
├── autokb/                      ← 自动知识库导入（9 个）
│   ├── run_pipeline.py          ←    全流程管线入口
│   ├── pipeline.py              ←    管线引擎
│   ├── discover.py              ←    发现模块
│   ├── importer.py              ←    导入模块
│   ├── classifier.py            ←    分类模块
│   ├── index_updater.py         ←    索引更新
│   └── config.py / templates / __init__.py
│
├── search/                      ← 统一搜索（1 个 + 建设中）
│   └── unified-search.py        ←    ✅ 统一搜索脚本（A-01/G-01 实现）
│
├── intent_analysis/             ← 意图分析（5 个）
│   ├── main.py                  ←    分析入口
│   ├── analyze_topic_boundaries.py  ← 话题边界识别
│   ├── extract_user_questions.py    ← 用户问题提取
│   ├── generate_intent_report.py    ← 意图报告生成
│   └── __init__.py
│
├── indexkb/                     ← 知识库索引工具（16 个）
│   ├── db_builder.py / db_query.py / kg_generator.py / ...
│
├── kb-stat/                     ← 知识库统计（3 个）
│   ├── deep-analysis-summary.py
│   └── extract-deep-analysis-docs.py
│
├── backup/                      ← 备份/历史脚本（~80 个，**待清理**）
│
└── skills-scripts-mapping.md    ← Skills ↔ Scripts 完整映射文档
```

### 3. 相关目录路径

| 目录 | 用途 | 与 Skills 的关系 |
|:-----|:------|:----------------|
| `knowledge/` | 知识库 | 几乎所有 Skill 的读写目标 |
| `knowledge/01_survey/` | 22+ 个追踪领域的日产出 | 定时任务 G/I 类 Skill 的写入路径 |
| `knowledge/07_industry-research/` | 深度行业研究报告 | mckinsey-research/competitor-analysis/light-paper-drafting 产出 |
| `knowledge/07_industry-research/mckinsey/` | 麦肯锡战略报告 | ← mckinsey-research |
| `knowledge/07_industry-research/competitor/` | 竞品分析报告 | ← competitor-analysis |
| `knowledge/07_industry-research/papers/` | 论文体裁产出 | ← light-paper-drafting |
| `knowledge/06_others/sources/` | 归档素材 | ← doubao-share / web-archive |
| `knowledge/concepts/` | 核心概念 | ← knowledge-wiki |
| `knowledge/methodology/` | 方法论体系 | ← method-analysis |
| `knowledge/weekly-reports/` | 周报归档 | ← weekly-report-generator |
| `knowledge/index.md` + `log.md` | 全局索引（默认操作对象）+ 日志 | 查找/加工目标 |
| `knowledge/README.md` | 人工条目库（v1.1 由 index.md 更名） | 精选条目追加 |
| `spec/` | 规格设计文档 | 定义了 Skills 架构规范 |
| `spec/design-007-skills-scripts-design.md` | Skills/Scripts 设计文档 | 本 README 的架构参考 |
| `spec/sr-006-ai-task-processing-optimization.md` | 14 类任务优化分析 | Skills 系统的优化方向 |
| `scheduler/` | 定时任务配置+执行 | scheduler tool + 34 个定时任务 |
| `scheduler/tasks.json` | 34 个定时任务定义 | ← 调度 I 类 |
| `scheduler/update_task_reliability.py` | 任务可靠性更新 | ← 调度 I 类 |
| `discover/` | 素材加工管线中间产物 | ← discover skill + 7 scripts |
| `import/` | 原始素材 | ← autokb pipeline + doubao-share + web-archive |
| `memory/` | 每日记忆 | ← light-memory-pm / 系统自动 |
| `tmp/` | 临时文件/中间产物 | 所有 Skill 的暂存区 |
| `tmp/bak/` | 废弃文件回收站 | ← RULE.md 文件操作纪律 |

---

## 🔄 技能 ↔ 脚本完整映射

> 技能系统采用 **双引擎架构**：Skills（AI 处理引擎）与 Scripts（确定性脚本引擎）协同工作。Skills 负责需要 AI 理解和判断的任务，Scripts 负责可自动化、可复现的工程操作。
>
> 详细映射见 [`scripts/skills-scripts-mapping.md`](../scripts/skills-scripts-mapping.md)

### 映射总览

| 技能 | 内嵌脚本（Skill 目录内） | 调用的通用脚本（scripts/） | 相关产出目录 |
|:-----|:------------------------|:--------------------------|:------------|
| `docx` | 13 个（accept_changes/comment/office 验证） | `check/md-format.py` | 用户指定路径 |
| `pptx` | 12 个（add_slide/clean/office 验证） | — | 用户指定路径 |
| `pdf` | 8 个（表单/合并/拆分/OCR/旋转） | — | 用户指定路径 |
| `xlsx` | 11 个（recalc/office 验证） | — | 用户指定路径 |
| `deep-tech-writer` | `scripts/check_tech_doc_quality.py` | `check/md-format.py` | `knowledge/07_industry-research/` |
| `knowledge-doc-writer` | `check_paths.py` + `check_format.py` | `check/link-validator.py` | `knowledge/02_rd/`/`knowledge/03_AI/` |
| `doc-reviewer` | `scripts/review_doc.py` | `check/link-validator.py` | 当前文档就地审查 |
| `knowledge-health-check` | `scripts/knowledge_health_check.py` | 全 `check/*.py` | `knowledge/` 全库 |
| `knowledge-index-manager` | — | `check/*.py` 全套 | `knowledge/` 各目录 index.md/log.md |
| `roadmap-maintainer` | `validate_structure.py` | — | `knowledge/server_design_roadmap.md` |
| `complex-system-function` | `analyze_system_function.py` + `check_experience_reuse.py` | — | 对话产出 |
| `doubao-share` | `slugify.py` | `autokb/` 管线 | `knowledge/06_others/sources/` |
| `web-archive` | — | `check/link-validator.py` | `knowledge/06_others/sources/` |
| `mckinsey-research` | — | `web_search`, `web_fetch` | `knowledge/07_industry-research/mckinsey/` |
| `competitor-analysis` | — | `web_search`, `web_fetch` | `knowledge/07_industry-research/competitor/` |
| `bdpan-storage` | `install.sh`/`login.sh`/`update.sh`/`uninstall.sh` | — | 百度网盘 |
| `skill-creator` | `init_skill.py`/`package_skill.py`/`quick_validate.py` | — | `skills/` 新目录 |
| `wechat-article-search` | `search_wechat.js` | — | 对话产出 |
| `thesis-helper` | `script.sh`/`thesis.sh` | — | 用户指定路径 |
| `apple-reminders` | — | `remindctl` CLI | macOS 提醒事项 |
| `notion` | — | Notion API | Notion 平台 |

### 按脚本位置分组的 Skill 对应关系

#### A. 调用了 `scripts/` 根级脚本的 Skills

| 脚本 | 调用方 Skills | 功能 |
|:-----|:------------|:------|
| `check_tech_doc_quality.py` | `deep-tech-writer` | 深度技术文档质量检查 |
| `knowledge_health_check.py` | `knowledge-health-check` | 知识库 6 维健康扫描 |
| `review_doc.py` | `doc-reviewer` | 文档五层审查引擎 |
| `strategy-compliance.py` | 多个 Skill | 策略合规检查 |
| `validate_structure.py` | `roadmap-maintainer` | 知识图谱结构验证 |
| `patch-task-search-strategy.py` | 34 个定时任务 | 搜索策略增强 |

#### B. 依赖 `scripts/check/` 脚本群的 Skills

| 检查脚本 | 覆盖维度 | 调用方 |
|:---------|:---------|:-------|
| `link-validator.py` + `link-fixer.py` | 内部链接有效性 | `knowledge-index-manager`, `doc-reviewer`, `knowledge-health-check` |
| `md-format.py` | 代码块格式/ASCII 对齐 | `knowledge-index-manager`, `deep-tech-writer`, `docx` |
| `knowledge-normalizer.py` | 6 阶段全量治理 | `knowledge-index-manager`（normalize 模式） |
| `index-log-normalizer.py` | 索引/日志规范化 | `knowledge-index-manager`（audit 模式） |
| `directory-architect.py` | 目录架构 MECE 分析 | `directory-optimizer`, `knowledge-index-manager` |
| `doc-quality.py` | 文档质量评分 | `knowledge-health-check` |
| `quantitative-check.py` | 量化数据验证 | `doc-reviewer`（D-03 实现） |
| `extract-content-metadata.py` | 标题/摘要/关键词提取 | `knowledge-index-manager` |

#### C. Skill 内嵌脚本清单（>303 个脚本分布在 ~51 个 Skill 内）

| 技能 | 内嵌脚本 | 语言 | 行数估计 | 作用 |
|:-----|:---------|:----:|:--------:|:-----|
| `docx` | 13 个 | Python | ~2,500 | Word 文档操作 |
| `pptx` | 12 个 | Python | ~2,000 | PPT 操作 |
| `xlsx` | 11 个 | Python | ~1,800 | 电子表格操作 |
| `pdf` | 8 个 | Python | ~1,500 | PDF 全生命周期 |
| `bdpan-storage` | 4 个（.sh） | bash | ~200 | 百度网盘安装/登录 |
| `complex-system-function` | 2 个 | Python | ~400 | 系统函数分析 |
| `conversation-topic-analyzer` | 1 个 | Python | ~300 | 话题分析引擎 |
| `deep-tech-writer` | 1 个 | Python | ~250 | 质量检查 |
| `doubao-share` | 1 个 | Python | ~80 | slug 生成 |
| `knowledge-doc-writer` | 2 个 | Python | ~300 | 路径/格式检查 |
| `knowledge-health-check` | 1 个 | Python | ~400 | 健康检查 |
| `knowledge-special-reports` | 多个 | Python | ~500 | 专项报告 |
| `roadmap-maintainer` | 1 个 | Python | ~200 | 结构验证 |
| `skill-creator` | 3 个 | Python | ~500 | 初始化/打包/验证 |
| `thesis-helper` | 2 个（.sh） | bash | ~100 | 论文辅助 |
| `wechat-article-search` | 1 个（.js） | JS | ~200 | 微信搜索 |
| 其他 24 个 Skills | 1-2 个 | 混合 | ~5,000 | 各种辅助功能 |
| **合计** | **~51 个** | **混合** | **~16,600** | **内嵌脚本总规模** |

---

## 📝 变更记录

| 日期 | 变更说明 |
|:----|:---------|
| 2026-08-03 | ✨ 新增 `monthly-report-generator` 技能：知识库月度报告生成（5 大维度：变更/领域/质量/洞察/待办），配套 `scripts/monthly-report-data-gather.sh` 数据采集脚本 + 定时任务（每月最后一天 23:20，feishu 通道） |
| 2026-07-27 | ✨ 新增 3 大章节：技能关系架构（5 种关系类型+流水线链+互补/竞品/依赖图）、技能目录与路径体系（skills/ + scripts/ 完整目录结构+18 个相关目录映射）、技能↔脚本完整映射（双引擎架构+按位置分组+内嵌脚本清单）；更新总览指标至 127 skills |
| 2026-07-24 | 初版：120 skills 详细使用说明、触发条件、分类索引；追加总览指标、来源分布、分类综述、技能→脚本联动表；同步 SR-003 约束编码重构 |
