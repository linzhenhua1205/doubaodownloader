# 🗺️ 高质量数据源图谱：本系统调研基础设施复用手册

> **概要**: 盘点本系统（CowAgent 工作空间）实际验证过的高质量数据源——基于 ①知识库调研区 URL 实证引用统计（01_survey+07_industry-research 全量 md，2026-08-05 快照）②`tmp/source-registry.json` 系统源注册表 ③记忆沉淀的网络应对经验。按 8 类 MECE 分类，标注一手性/抓取方式/稳定性/已知缺口，附复用路由表与新源评估六维
>
> **关键词**: 数据源 · 调研基础设施 · 一手来源 · 抓取技术栈 · 源可靠性 · 复用路由
>
> **版本**: v1.0 | **创建**: 2026-08-05 | **配套**: [`industry-insight` 技能](../../../skills/industry-insight/SKILL.md)（源注册表运行时）| **姊妹篇**: [`2026-08-05-knowledge-management-value-chain-deep-analysis.md`](2026-08-05-knowledge-management-value-chain-deep-analysis.md)（知识摄取维度）

---

## 📑 目录

- [§1 定位与四步用法](#1-定位与四步用法)
- [§2 数据源全景：8 类 MECE 分类](#2-数据源全景8-类-mece-分类)
- [§3 实证引用榜 TOP40](#3-实证引用榜-top40)
- [§4 高质量源详表（按分类）](#4-高质量源详表按分类)
  - [4.1 学术论文](#41-学术论文)
  - [4.2 标准与开源联盟](#42-标准与开源联盟)
  - [4.3 厂商官方一手](#43-厂商官方一手)
  - [4.4 国际行业媒体](#44-国际行业媒体)
  - [4.5 中文行业媒体与社区](#45-中文行业媒体与社区)
  - [4.6 市场数据与咨询](#46-市场数据与咨询)
  - [4.7 管理咨询与商业研究](#47-管理咨询与商业研究)
  - [4.8 会议议程与活动](#48-会议议程与活动)
- [§5 系统源注册表（source-registry.json）](#5-系统源注册表source-registryjson)
- [§6 抓取技术栈与 fallback 链](#6-抓取技术栈与-fallback-链)
- [§7 已知缺口与替代方案](#7-已知缺口与替代方案)
- [§8 复用路由表（场景 → 源）](#8-复用路由表场景--源)
- [§9 新源质量评估六维](#9-新源质量评估六维)
- [§10 维护机制](#10-维护机制)
- [§11 交叉链接](#11-交叉链接)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## §1 定位与四步用法

本专题是**本系统调研的"输入侧基础设施"**：回答"要调研某主题时，去哪找可信数据、怎么抓、遇到反爬怎么办"。

**四步用法**：

```text
Step 1  Locate   ->  see routing table (S8): primary + backup + fallback
Step 2  Fetch    ->  pick method (S6): web_fetch / browser / API / RSS / curl
Step 3  Verify   ->  6-dimension eval (S9) + multi-source triangulation
Step 4  Record   ->  update source-registry.json (auto downgrade, S5/S10)
```

| 步骤 | 动作 | 依据 |
|:--|:--|:--|
| 1 定位场景 | 查 §8 复用路由表 → 确定首选源 + 备选源 + fallback | §8 |
| 2 抓取 | 按 §6 技术栈选手段（web_fetch/browser/API/RSS/curl） | §6 |
| 3 验证 | 按 §9 六维评估 + 多源三角（RULE.md 强制） | §9 |
| 4 记录 | 结果写入 source-registry.json（自动降级机制） | §5/§10 |

> 与 RULE.md 的关系：本清单是"素材批判性使用"规则的**正向索引**——它告诉你**哪些源值得信任、哪些只能当线索**，配合 `import/` 素材批判性使用原则使用。

---

## §2 数据源全景：8 类 MECE 分类

| 类别 | 定位 | 一手性 | 代表源 | 典型用途 |
|:--|:--|:--|:--|:--|
| **A 学术论文** | 原理/前沿 | ✅ 一手 | arXiv·IEEE Spectrum·LWN | 技术原理、算法、系统论文 |
| **B 标准与开源联盟** | 规范/生态 | ✅ 一手 | UALink·ODCC·OCP·CNCF·Linux | 标准卡位、生态动向 |
| **C 厂商官方** | 产品/路线图 | ✅ 一手 | AMD IR·NVIDIA News·Anthropic docs | 产品规格、技术路线图 |
| **D 国际行业媒体** | 动态/解读 | ⚠️ 二手但高质 | STH·Tom's·TechCrunch·The Verge | 行业动态、深度拆解 |
| **E 中文媒体社区** | 本土/供应链 | ⚠️ 二手 | 36氪·集微网·知乎·微信·掘金 | 国产化、供应链、本土生态 |
| **F 市场数据咨询** | 量化/预测 | ⚠️ 混合 | TrendForce·DRAMeXchange·LightCounting·Digitimes | 市场规模、价格、出货量 |
| **G 管理咨询商业** | 战略/人才 | ⚠️ 二手高质 | McKinsey·BCG·HBR·WEF·Atlassian | 战略分析、人才趋势 |
| **H 会议议程活动** | 一手现场 | ✅ 一手 | Sessionize API·大会官网 | 官方议程、演讲人、技术方向 |

**MECE 完备性说明**：8 类按"内容生产者的角色"切分（学者/标准组织/厂商/媒体/数据商/咨询/活动主办），互斥且覆盖调研信息的全部生产者；其中 D/E 是"转述者"（二手），其余为"原创者"（一手）——**一手源优先，二手源做交叉验证**是本图谱的核心使用原则。

---

## §3 实证引用榜 TOP40

**统计口径**：`grep -rhoE "https?://..." knowledge/01_survey/ knowledge/07_industry-research/ --include="*.md"`，按域名聚合（2026-08-05 快照）。引用数 = 本系统调研文档中该域名出现次数（含链接与来源标注），**是"实际用过且留下痕迹"的实证证据**。

| # | 域名 | 引用数 | 类别 | 质量级 |
|:--:|:--|:--:|:--:|:--:|
| 1 | <www.36kr.com> | 1703 | E 中文 | A |
| 2 | arxiv.org | 1291 | A 学术 | A |
| 3 | juejin.cn | 521 | E 中文 | B |
| 4 | github.com | 425 | 开源生态 | A |
| 5 | <www.servethehome.com> | 392 | D 国际 | A |
| 6 | <www.techweb.com.cn> | 390 | E 中文 | B |
| 7 | zhuanlan.zhihu.com | 300 | E 中文 | B |
| 8 | github.blog | 272 | 开源生态 | A |
| 9 | <www.cncf.io> | 266 | B 标准 | A |
| 10 | lwn.net | 241 | A 学术 | A |
| 11 | <www.tomshardware.com> | 236 | D 国际 | B |
| 12 | <www.digitimes.com> | 205 | F 市场 | A |
| 13 | techcrunch.com | 205 | D 国际 | A |
| 14 | <www.trendforce.com> | 180 | F 市场 | A |
| 15 | <www.atlassian.com> | 170 | G 商业 | A |
| 16 | hbr.org | 164 | G 商业 | A |
| 17 | mp.weixin.qq.com | 162 | E 中文 | B |
| 18 | <www.theverge.com> | 161 | D 国际 | A |
| 19 | <www.odcc.org.cn> | 101 | B 标准 | A |
| 20 | <www.databricks.com> | 83 | C 厂商 | A |
| 21 | kubernetes.io | 77 | B 标准 | A |
| 22 | arstechnica.com | 72 | D 国际 | B |
| 23 | <www.cursor.com> | 68 | C 厂商 | B |
| 24 | <www.utilitydive.com> | 48 | D 国际 | B |
| 25 | docs.anthropic.com | 47 | C 厂商 | A |
| 26 | <www.gsb.stanford.edu> | 46 | G 商业 | A |
| 27 | <www.datacenterknowledge.com> | 45 | D 国际 | B |
| 28 | linear.app | 43 | C 厂商 | B |
| 29 | opentelemetry.io | 41 | B 标准 | A |
| 30 | <www.bcg.com> | 40 | G 商业 | A |
| 31 | semiengineering.com | 39 | D 国际 | B |
| 32 | <www.powerelectronicsnews.com> | 38 | D 国际 | B |
| 33 | <www.dramexchange.com> | 35 | F 市场 | A |
| 34 | <www.storagenewsletter.com> | 26 | D 国际 | B |
| 35 | nvidianews.nvidia.com | 23 | C 厂商 | A |
| 36 | developer.nvidia.com | 23 | C 厂商 | A |
| 37 | <www.phoronix.com> | 22 | D 国际 | B |
| 38 | pytorch.org | 22 | B 标准 | A |
| 39 | ualinkconsortium.org | 18 | B 标准 | A |
| 40 | <www.mckinsey.com> | 14 | G 商业 | A |

> 注：36kr/juejin/zhihu 等中文源引用数高（多为转载/链接），**质量级标 B 不代表不可信，而是"需交叉验证"**——与 §4.5 详表一致。

---

## §4 高质量源详表（按分类）

### 4.1 学术论文

| 源 | 定位 | 抓取方式 | 状态 | 备注 |
|:--|:--|:--|:--|:--|
| **arXiv.org**（arxiv.org / export.arxiv.org） | 论文预印本主源，本系统引用第 1 | web_fetch 直连 PDF/abs 页；API 可批量；**LaTeX 源码提取**（`scripts/markdown-proxy/scripts/extract_tex.py`，保章节/公式/图表/文献） | ✅ 稳定 | 免认证；export 镜像适合批量；注意预印本未经同行评审 |
| **LWN.net**（lwn.net） | Linux 内核深度分析（每周内核周报） | web_fetch | ✅ 稳定 | 内核/子系统动向第一手解读 |
| **IEEE Spectrum**（spectrum.ieee.org） | 工程科普+前沿 | web_fetch | ✅ 稳定 | 论文的通俗化解读，可作入口 |
| **kernel.org** | Linux 内核官方 | web_fetch | ✅ 稳定 | 版本/发布节奏权威 |

### 4.2 标准与开源联盟

| 源 | 定位 | 抓取方式 | 状态 | 备注 |
|:--|:--|:--|:--|:--|
| **CNCF**（www.cncf.io） | 云原生基金会，K8s 生态权威 | web_fetch + 官方博客 RSS | ✅ 稳定 | 云原生路线图/毕业项目 |
| **UALink Consortium**（ualinkconsortium.org） | 开放互联标准组织 | web_fetch | ✅ 稳定 | UALink 规格/成员动态（超节点关键） |
| **ODCC**（www.odcc.org.cn） | 中国开放数据中心委员会 | web_fetch | ✅ 稳定 | 中国算力标准卡位第一现场 |
| **OCP**（ocpasia.org / opencomputeproject） | 开放计算项目 | ⚠️ 部分反爬 | ⚠️ 缺口 | 主站反爬 403 长期；ocpasia 可用 |
| **Kubernetes**（kubernetes.io） | K8s 官方文档/博客 | web_fetch | ✅ 稳定 | 版本特性权威 |
| **PyTorch / Prometheus / Flink / Spark 官方** | 各自生态权威 | web_fetch | ✅ 稳定 | 版本发布/架构文档 |

### 4.3 厂商官方一手

| 源 | 定位 | 抓取方式 | 状态 | 备注 |
|:--|:--|:--|:--|:--|
| **AMD IR**（ir.amd.com） | AMD 投资者关系/新闻稿 | web_fetch | ✅ 稳定 | 技术路线图一手（Advancing AI 报告主力源） |
| **NVIDIA News**（nvidianews.nvidia.com）+ Developer（developer.nvidia.com） | NVIDIA 官方新闻/技术文档 | web_fetch | ✅ 稳定 | GTC 发布/产品规格 |
| **Intel / Marvell / Astera Labs / Huawei 官网** | 各自产品/路线图 | web_fetch | ✅ 稳定 | 厂商白皮书/产品页 |
| **Anthropic Docs**（docs.anthropic.com）+ Anthropic 官网 | Claude 能力/最佳实践 | web_fetch | ✅ 稳定 | 官方文档一手 |
| **Databricks / Snowflake / Atlassian / Linear 官方** | 产品/商业模式一手 | web_fetch | ✅ 稳定 | 数据湖仓/项目管理叙事 |
| **Microsoft Azure**（azure.microsoft.com） | 云产品/案例 | web_fetch | ✅ 稳定 | WTI 报告等一手 |

### 4.4 国际行业媒体

| 源 | 定位 | 抓取方式 | 状态 | 备注 |
|:--|:--|:--|:--|:--|
| **ServeTheHome**（www.servethehome.com） | 服务器硬件深度拆解之王 | web_fetch + RSS | ✅ 稳定 | 本系统服务器调研主力；AMD Helios 解剖一手 |
| **Tom's Hardware**（www.tomshardware.com） | 消费+服务器硬件 | web_fetch | ✅ 稳定 | 覆盖广，深度一般 |
| **TechCrunch**（techcrunch.com） | 科技创业/融资 | RSS（稳定双主源之一） | ✅ 稳定 | 硅谷动态第一快讯 |
| **The Verge**（www.theverge.com） | 科技消费 | RSS（稳定双主源之二） | ✅ 稳定 | 与 TC 互补 |
| **The Register**（www.theregister.com） | IT 行业毒舌评论 | web_fetch | ✅ 稳定 | 观点尖锐，常挖独家 |
| **SemiEngineering**（semiengineering.com） | 半导体制造/EDA | web_fetch | ⚠️ 部分反爬 | 深度技术分析 |
| **Data Center Knowledge / Data Center Dynamics** | 数据中心运营 | web_fetch | ✅ 稳定 | 机房/能耗/制冷 |
| **Phoronix**（www.phoronix.com） | Linux/硬件性能测试 | web_fetch | ✅ 稳定 | 性能基准一手 |
| **ArsTechnica / The New Stack / UtilityDive / FacilitiesDive** | 泛科技/云原生/电力 | web_fetch | ✅ 稳定 | 补位媒体 |
| **HPCwire** | HPC 高性能计算 | ⚠️ 反爬 403 | ⚠️ 缺口 | 长期缺口，需浏览器或替代 |
| **The Next Platform**（thenextplatform.com） | 基础设施深度分析 | ⚠️ 反爬 403 | ⚠️ 缺口 | 高质量但难抓，长期缺口 |

### 4.5 中文行业媒体与社区

| 源 | 定位 | 抓取方式 | 状态 | 备注 |
|:--|:--|:--|:--|:--|
| **36氪**（www.36kr.com） | 科技创投中文第一入口 | web_fetch | ✅ 稳定 | 引用第 1 中文源；快讯+深度 |
| **集微网**（www.ijiwei.com） | 半导体产业中文权威 | web_fetch | ✅ 稳定 | 半导体供应链/国产化 |
| **老杳吧**（www.laoyaoba.com） | 半导体产业观察 | web_fetch | ✅ 稳定 | 供应链细节 |
| **TechWeb**（www.techweb.com.cn） | 科技新闻聚合 | web_fetch | ✅ 稳定 | 广而浅，作线索 |
| **知乎**（zhihu.com / zhuanlan.zhihu.com） | UGC 深度长文/热榜/问答 | **zhihu-cli**（`~/.local/bin/zhihu`，V4 API，需登录） | ✅ zhihu-cli 可用 | **中等置信数据源**：观点/经验/趋势信号有价值，量化数据须交叉验证；2026-08-12 集成 web-access skill |
| **X/Twitter**（x.com / twitter.com） | 官方账号声明/大V观点/产品发布 | **fetch-skill**（`scripts/fetch-skill/fetch.py`，FxTwitter API 零依赖） | ✅ 单推文可用 | **中等置信数据源**：官方账号可作信号，量化数据须交叉验证；回复/时间线需 Camofox（服务器不可用）；2026-08-12 集成 |
| **微信公众号**（mp.weixin.qq.com） | 行业深度/官方号 | **wechat-claw**（`scripts/wechat-claw/read_wechat_article.py`，curl_cffi 纯文本）· **wechat-extractor**（`scripts/wechat-extractor/cli.js`，Node 富元数据+17 错误码） | ✅ 单篇可用 | **中等置信数据源**：行业深度/官方号有独家内容；全量提取需凭证（crawler.py，云端禁自动登录）；2026-08-12 集成 web-access skill |
| **掘金**（juejin.cn） | 技术社区 | web_fetch | ✅ 稳定 | 前端/后端/AI 工程 |
| **EET-China**（www.eet-china.com） | 电子工程 | web_fetch | ✅ 稳定 | 硬件工程 |
| **ODCC 中文**（www.odcc.org.cn） | 中国标准 | web_fetch | ✅ 稳定 | 见 §4.2 |

### 4.6 市场数据与咨询

| 源 | 定位 | 抓取方式 | 状态 | 备注 |
|:--|:--|:--|:--|:--|
| **TrendForce**（www.trendforce.com） | 存储/面板/半导体市场数据 | web_fetch 新闻页 | ✅ 稳定 | 集邦咨询；DRAM/NAND 供需预测主力 |
| **DRAMeXchange**（www.dramexchange.com） | DRAM 现货价 | web_fetch | ✅ 稳定 | 价格数据权威 |
| **LightCounting**（www.lightcounting.com） | 光模块市场 | web_fetch | ✅ 稳定 | 光通信出货/预测 |
| **Digitimes**（www.digitimes.com） | 台湾电子供应链 | web_fetch | ✅ 稳定 | 供应链独家（大陆产能/订单） |
| **SIA**（www.semiconductors.org） | 美国半导体产业协会 | web_fetch | ✅ 稳定 | 半导体销售额官方统计 |
| **IDC / Gartner / Counterpoint** | 市场预测（间接引用） | 新闻转述 | ⚠️ 付费墙 | 需经媒体转述，注意二手 |

### 4.7 管理咨询与商业研究

| 源 | 定位 | 抓取方式 | 状态 | 备注 |
|:--|:--|:--|:--|:--|
| **WEF**（www.weforum.org） | 世界经济论坛报告 | web_fetch 出版物页 | ✅ 稳定 | Future of Jobs 等权威报告（2026-08-05 实测直连成功） |
| **McKinsey**（www.mckinsey.com） | 战略咨询 | web_fetch | ✅ 稳定 | 行业洞察 |
| **BCG**（www.bcg.com） | 战略咨询 | web_fetch | ✅ 稳定 | 技术/人才洞察 |
| **HBR**（hbr.org） | 哈佛商业评论 | web_fetch | ✅ 稳定 | 管理思想 |
| **Stanford GSB / Wharton**（gsb.stanford.edu / knowledge.wharton.upenn.edu） | 商学院研究 | web_fetch | ✅ 稳定 | AI 经济/组织研究 |
| **Microsoft WorkLab**（microsoft.com/en-us/worklab） | 微软工作趋势 | web_fetch | ✅ 稳定 | WTI 报告一手（2026-08-05 实测） |

### 4.8 会议议程与活动

| 源 | 定位 | 抓取方式 | 状态 | 备注 |
|:--|:--|:--|:--|:--|
| **Sessionize API**（sessionize.com/api/v2/{code}/view/All） | 会议官方议程 JSON | API 直连 | ✅ 稳定 | 拿官方议程/演讲人/时间线（记忆验证） |
| **大会官网**（GTC/FMS/ODCC/OCP/WAIC 等） | 议程+新闻稿 | web_fetch | ✅ 稳定 | 三大会闭环：GTC→FMS→ODCC |
| **AMD IR / NVIDIA News** | 发布会新闻稿 | web_fetch | ✅ 稳定 | 发布会后 24h 内一手 |

---

## §5 系统源注册表（source-registry.json）

**运行时位置**：`tmp/source-registry.json`（由 industry-insight 技能/`industry-research-tracker.py` 自动维护，v3）

**结构**：`version / sources / topics / discovery_log`；`topics` 下按专题（hardware/tech/market...）记录每源的 `success_count / fail_count / last_success / last_fail / consecutive_fails`

**预定义源 34 个**（含注册表与执行器分层）：ServeTheHome（含 HVDC/电源/液冷/GPU 细分）、Tom's Hardware（形态/GPU 细分）、SemiEngineering、HPCwire、TrendForce、Data Center Dynamics、The Register、TechCrunch、Reuters、arXiv、CNCF Blog、K8s Blog、GitHub Trending、OCP Blog、36氪、集微网等

**执行器 tier 分层**（`industry-research-tracker.py` 内建，按专题）：

| 专题 | tier1（首选） | tier2（备选） |
|:--|:--|:--|
| 服务器形态 | ServeTheHome·Tom's·AnandTech | SemiEngineering·HPCwire·TheRegister |
| 互联/网络 | SemiEngineering·HPCwire·DCD | TheRegister·TechCrunch |
| 芯片微架构 | TheNextPlatform·SemiEngineering | ServeTheHome·HPCwire |
| 市场动态 | Reuters·TechCrunch | TheRegister·36kr |
| 软件/云原生 | TechCrunch·TheRegister | Reuters |
| 论文 | arXiv·IEEE Spectrum | SemiEngineering |
| CPU/GPU | WikiChip·arXiv | ServeTheHome |
| 存储 | TrendForce·Reuters | 36kr·Reuters |
| 开源 | GitHub Trending·TechCrunch | TheRegister |

**自动降级规则**：连续 3 次失败 → 源降一级（A→C, B→D），自动发现替代源并跨专题推荐（如电源源全失效→自动推荐 cncf-blog/k8s-blog/techcrunch）

> 本专题 §3-§4 是注册表的**人工质量标注层**（实证引用数+一手性+状态），注册表是**自动运行层**（成功率+降级），二者互补。

---

## §6 抓取技术栈与 fallback 链

| 手段 | 适用 | 优先级 | 失败 fallback |
|:--|:--|:--|:--|
| **web_fetch 直连** | 静态页/官方/文档/PDF | 🥇 首选 | → browser → curl 列表页 |
| **browser（CDP）** | 动态渲染/登录墙（微信/知乎） | 🥈 | → 截图+vision 读图 |
| **RSS** | 快讯类稳定源（TechCrunch/The Verge） | 🥉 快讯场景 | → web_fetch 主页 |
| **API** | GitHub REST（60req/h 免认证）·Sessionize·arXiv | 批量场景 | → 网页版 → 镜像（export.arxiv.org） |
| **MCP 渠道** | Jina/RSS/B站/YouTube（Agent Reach 4/15 渠道可用） | 特定平台 | → browser 直访 |
| **curl + grep href** | 猜 URL 404 时探测列表页 | 兜底 | → web_search（如有 key） |

**已验证的 fallback 经验**：

- web_search key 失效 → **web_fetch 直连目标站点 > 搜索**（记忆经验，2026-08-05 WEF/微软实测有效）
- 猜具体文章 URL 常 404 → 先 curl 列表页 grep href 找真实链接
- 论文批量 → export.arxiv.org 镜像；GitHub 批量 → api.github.com 免认证 60req/h
- pip 超时 → 清华镜像；npm 无 root → `~/.npm-global`

---

## §7 已知缺口与替代方案

| 缺口源 | 状态 | 替代方案 |
|:--|:--|:--|
| **The Next Platform** | 反爬 403 长期 | 经媒体转述（Tom's/STH 常引用）；browser 偶可解 |
| **HPCwire** | 反爬 403 长期 | SemiEngineering/STH 的 HPC 报道；Google 缓存（如可用） |
| **OCP 主站**（opencomputeproject.org） | 反爬 | ocpasia.org；会议新闻稿；成员公司转述 |
| **Bing web_search** | 密钥失效 + RSS 空壳重定向 | 双主源 TechCrunch/The Verge RSS；web_fetch 直连 |
| **Baidu 搜索** | 安全验证拦截 | 36氪/集微网/知乎直连；wechat-article-search 技能 |
| **GitHub token** | 失效待重配 | 免认证 REST 60req/h 够日常；重配后解锁 5000/h |
| **小红书/Reddit/OpenCLI** | 服务器无桌面受限 | 放弃或 browser 尝试（受限标记） |
| **知乎/微信** | 登录墙/反爬 | browser 登录态（会话持久化）；专门技能（doubao-share/web-archive） |
| **IDC/Gartner 原始报告** | 付费墙 | 媒体转述 + 标注二手；TrendForce 免费替代 |

---

## §8 复用路由表（场景 → 源）

| 调研场景 | 首选 | 备选 | fallback |
|:--|:--|:--|:--|
| 服务器整机/硬件形态 | ServeTheHome | Tom's·AnandTech | 厂商官网规格页 |
| GPU/AI 芯片路线图 | AMD IR·NVIDIA News | STH·WikiChip | 大会新闻稿（GTC/Advancing AI） |
| 互联标准（UALink/CXL/PCIe） | UALink Consortium·标准组织官网 | SemiEngineering | 成员厂商白皮书 |
| 存储市场/价格 | TrendForce·DRAMeXchange | LightCounting·Digitimes | 存储厂商财报 |
| 电源/散热架构 | STH（HVDC 专题）·PowerElectronicsNews | EENewsPower·UtilityDive | 厂商白皮书 |
| 论文/算法前沿 | arXiv | IEEE Spectrum·LWN | 会议论文集（Sessionize 找议程） |
| 云原生/K8s | CNCF·K8s 官方 | The New Stack | GitHub 趋势 |
| 国产化/供应链 | 集微网·老杳吧 | Digitimes·ODCC | 36氪·TechWeb |
| 大厂战略/商业模式 | 36氪·TechCrunch | The Verge·Atlassian | 官方 IR |
| 人才/组织/技能趋势 | WEF·Microsoft WorkLab | McKinsey·BCG·HBR | Stanford GSB·Wharton |
| 大会前瞻/复盘 | Sessionize API·大会官网 | STH 现场实况 | 官方新闻稿 |
| 开源项目动态 | GitHub Trending·GitHub API | CNCF·Phoronix | 官方 blog |

---

## §9 新源质量评估六维

遇到新数据源时，按六维打分（每维 1-5），**总分 ≥24 才纳入清单**：

| 维度 | 问题 | 高分特征 |
|:--|:--|:--|
| ① 一手性 | 是原创还是转述？ | 原创内容/独家数据 |
| ② 权威性 | 发布者身份？ | 标准组织/厂商官方/知名机构 |
| ③ 时效性 | 更新频率？截断日期？ | 日更/周更，标注日期 |
| ④ 稳定性 | 历史可抓取率？ | 免认证直连成功率高 |
| ⑤ 可溯性 | 引用是否可验证？ | 给出处/原始数据/链接 |
| ⑥ 可抓取性 | 有无反爬/登录墙？ | web_fetch 直连可达 |

> 补充规则：**关键量化数据必须多源三角验证**（RULE.md）——新源即使高分，其数据也要与标准组织/厂商官方/可复算推导交叉验证后才能进正式文档。

---

## §10 维护机制

1. **自动层**（已运行）：`industry-research-tracker.py` 每次抓取记录 success/fail → 连续 3 败自动降级 + 自动发现替代源（§5）
2. **人工层**（本专题）：每季度按 §3 实证统计刷新引用榜，核对 §4 详表状态（反爬变化/新增源）
3. **验证流程**：新源 → §9 六维评估 → 记录到 source-registry.json → 试用 3 次 → 稳定则升入详表
4. **变更纪律**：数据源状态变化（如 GitHub token 重配、Bing 恢复）→ 更新本专题 + log.md 记录

---

## §11 交叉链接

| 关联 | 关系 |
|:--|:--|
| [`2026-08-05-knowledge-management-value-chain-deep-analysis.md`](2026-08-05-knowledge-management-value-chain-deep-analysis.md) | 摄取维度：本图谱是"摄取质量"的输入侧落地 |
| [`2026-07-20-information-depth-ai-mastery.md`](2026-07-20-information-depth-ai-mastery.md) | 信息认知：判断来源可信度的方法论基础 |
| [`2026-08-05-ai-era-human-capability-special-report.md`](../../03_AI/methodology/2026-08-05-ai-era-human-capability-special-report.md) | 批评检查支柱：多源三角/溯源标注的操作清单 |
| [`industry-insight` 技能](../../../skills/industry-insight/SKILL.md) | 源注册表运行时（source-registry.json） |
| `RULE.md` | import 素材批判性使用 + 多源三角验证约束 |
| [`doubao-share` 技能](../../../skills/doubao-share/SKILL.md) | 豆包对话归档（自有知识源） |
| [`wechat-article-search` 技能](../../../skills/wechat-article-search/SKILL.md) | 微信公众号文章检索 |

---

## 参考来源

- 实证统计：`grep -rhoE "https?://..." knowledge/01_survey/ knowledge/07_industry-research/ --include="*.md"`（2026-08-05 快照，域名聚合）
- `tmp/source-registry.json`（v3，2026-07-31 最后更新）
- `scripts/industry-research-tracker.py` tier 分层定义（第 72-123 行）
- `skills/industry-insight/SKILL.md` §源可靠性数据库/跨专题源共享/自动降级规则
- 记忆沉淀：网络不可用应对策略（TechCrunch/The Verge 双主源、Sessionize API、GitHub 免认证 60req/h、TNP/HPCwire/OCP 反爬缺口、Bing/百度缺口）

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-08-05 | v1.0 | 初始版本：8 类 MECE 数据源全景 + 实证引用榜 TOP40 + 详表（一手性/抓取/状态）+ 系统注册表说明 + 抓取技术栈 fallback 链 + 缺口与替代 + 复用路由表 + 新源评估六维 + 维护机制 |
