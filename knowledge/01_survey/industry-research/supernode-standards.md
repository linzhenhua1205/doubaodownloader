# 超节点标准与生态 (2026-08-05)

> **执行时间**: 2026-08-05 CST（周期跟踪任务，首版 2026-08-01）
> **任务**: 超节点标准与生态
> **输出规则**: 专题独立文件，只写本任务目录
> **源可靠性**: 官方(UALink Consortium) > 行业媒体 > 博客

---

## 1. 专题概览

- **核心主题**: AI 超节点开放标准与生态 — UALink scale-up 互联、OAM/OCP GPU baseboard、rack-scale 架构、NVIDIA DGX 对照
- **为什么跟踪**: 超节点是 AI 算力基础设施的顶层形态，开放标准（UALink/OCP）与封闭生态（NVLink/DGX）的竞争决定产业格局
- **本期关键判断**: UALink 组织进入**公司化+董事会扩容+规范体系化**三线并进阶段；事件日历显示 8-10 月为开放标准密集发布窗口

## 2. 本期有效发现

### 2.1 UALink 联盟动态（一手源 ✅）

| # | 发现 | 强度 | 来源 |
|:-|:-----|:----:|:-----|
| 1 | **UALink Consortium 发布 4 份新规范**，支持 multi-workload 环境部署，提升 AI 工作负载效率与易实现性 | ⭐⭐⭐⭐⭐ | https://ualinkconsortium.org/ |
| 2 | **阿里、苹果、Synopsys 加入 UALink 董事会** — 从芯片联盟扩展为全产业链标准组织 | ⭐⭐⭐⭐⭐ | https://ualinkconsortium.org/ |
| 3 | **UALink Consortium 完成公司化（Incorporates）**，宣布会员招募 — 组织治理升级 | ⭐⭐⭐⭐ | https://ualinkconsortium.org/ |
| 4 | **新白皮书发布**: TASK Consultancy UALink White Paper（可下载，分析 UALink 技术优势） | ⭐⭐⭐ | https://ualinkconsortium.org/ |
| 5 | **Demo 上线**: Database workload performance enhancement using CXL memory（CXL 内存加速数据库工作负载） | ⭐⭐⭐ | https://ualinkconsortium.org/ |
| 6 | Synopsys 发布**完整 UALink IP 方案**（controller + PHY + security + verification IP） | ⭐⭐⭐ | https://www.synopsys.com/designware-ip/interface-ip/ualink.html |

### 2.2 规范体系（Bing 检索 ✅）

| # | 发现 | 强度 | 来源 |
|:-|:-----|:----:|:-----|
| 7 | **UALink 200G 1.0 Specification** 已发布 + 多厂商支持声明（Statements of Support） | ⭐⭐⭐⭐ | https://ualinkconsortium.org/wp-content/uploads/（白皮书PDF） |
| 8 | **UALink Common 2.0** 引入**网络内计算（in-network compute）**、Chiplet 支持、管理性、降功耗 — 4 份规范同日发布 | ⭐⭐⭐⭐⭐ | https://zhuanlan.zhihu.com（UALink 2.0规范解读） |
| 9 | UALink 联盟 2024-10 成立，创始成员 AMD/Intel/Microsoft/Google/Meta/AWS/Cisco/HPE/Astera Labs | ⭐⭐⭐ | https://baike.baidu.com/item/UALink联盟 |
| 10 | UALink 使命: 开放标准提供可扩展/高性能/弹性/经济高效 Scale-up 连接，减少芯片面积占用、加速器互访延迟与功耗 | ⭐⭐⭐ | https://ualinkconsortium.org/ |

### 2.3 事件日历（开放标准发布窗口 🔭）

| 事件 | 日期 | 地点 | 关注点 |
|:-----|:----:|:-----|:-------|
| **FMS 2026** (Flash Memory Summit) | 8/4-8/6 | Santa Clara, CA | UALink/CXL 内存方案、Demo展示 |
| **OCP APAC Summit** | 8/11-8/12 | 台北 | GPU baseboard/OAM 标准亚太更新 |
| **Hot Interconnects** 🆕 | 8/19-8/21 | Virtual | 高速互联学术前沿 |
| **AI Infra Summit** 🆕 | 9/15-9/17 | Santa Clara, CA | AI 基础设施生态 |
| **OCP Global Summit** | 10/12-10/17 | Denver, CO | 年度最大开放计算盛会 |

> 来源: https://ualinkconsortium.org/（News & Events）

### 2.4 今日增量（2026-08-02 快照）

> 与 8/01 快照间隔 1 天，官网**无重大新事件**（4份规范+董事会扩容+公司化仍为置顶动态）。本次增量以**规范技术参数量化**与**日期锚点确认**为主：

| # | 发现 | 强度 | 来源 |
|:-|:-----|:----:|:-----|
| 11 | **UALink 1.0 规范技术参数**: 支持连接 **1024 个加速器**，每通道 **200 GT/s**（2025-04-09 发布） | ⭐⭐⭐⭐ | https://www.expreview.com（UALink 1.0发布报道） |
| 12 | **UALink 200G 1.0 Scale-Up 互联技术白皮书**（2025-08-22 PDF）— 使命/芯片面积/延迟/功耗目标官方文本 | ⭐⭐⭐ | https://ualinkconsortium.org/wp-content/uploads/ |
| 13 | **UALink 2.0 规范发布日期确认**: 2026-04-09 一口气发布 4 份规范（Common 2.0 引入在网计算/Chiplet/管理性） | ⭐⭐⭐⭐ | https://zhuanlan.zhihu.com（UALink 2.0解读） |
| 14 | **UALink 联盟成立时间线确认**: 2024-10 正式成立，创始成员 AMD/Intel/Microsoft/Google/Meta/AWS/Cisco/HPE/Astera Labs | ⭐⭐⭐ | https://baike.baidu.com/item/UALink联盟 |
| 15 | **UALink 1.0 首发厂商报道**: 联盟 2024 年由 AMD/Broadcom/Cisco/Google/HPE/Intel/Meta/Microsoft 宣布成立 | ⭐⭐⭐ | https://www.expreview.com |

**2026-08-02 源状态**: Baidu ❌（安全验证拦截）· OCP Blog ❌（HTTP 403）· Bing ✅ · UALink官网 ✅（一手源快照确认）

### 2.5 今日快照（2026-08-03）

> **连续第 3 日官网快照一致 — 无新事件发布**。UALink 官网非日更站，当前置顶动态（4份规范/董事会/公司化）自 7/29 起保持稳定。今日跟踪价值集中在**事件日历时间锚点**：

| 时间锚点 | 倒计时 | 关注点 |
|:---------|:------:|:-------|
| 🎯 **FMS 2026 (Flash Memory Summit)** | **明日开幕 (8/4-8/6)** | UALink/CXL 内存方案与 Demo 现场细节 — 官网事件日历确认 UALink 代表出席 |
| OCP APAC Summit | 8 天后 (8/11-8/12 台北) | GPU baseboard/OAM 标准亚太更新 |
| Hot Interconnects | 16 天后 (8/19-8/21 线上) | 高速互联学术前沿 |

**2026-08-03 源状态**: Baidu ❌ · OCP Blog ❌ · Bing ✅（结果与 8/02 一致，无新信号）· UALink官网 ✅（快照第3日一致）

> ⚠️ **判断**: 连续 3 日无新事件符合开放标准组织发布节奏（大事件驱动型）。**建议 FMS 8/4 开幕后切换为现场动态跟踪**，重点关注 UALink 展台 demo 与 CXL 内存方案实测数据。

### 2.6 今日增量（2026-08-04 — FMS 开幕日 🎯）

> **FMS 2026（Flash Memory Summit）今日开幕**（8/4-8/6, Santa Clara Convention Center & Hyatt Regency），UALink 官网事件日历确认 UALink 代表出席。本次为开放标准生态**年度首个实机展示窗口**。

| # | 发现 | 强度 | 来源 |
|:-|:-----|:----:|:-----|
| 16 | **FMS 2026 规模量化**: 3,500+ 参会者 / 1,500+ 组织 / **350+ 演讲者** / 100+ 展商 / **20+ 内容流** / 20周年 | ⭐⭐⭐⭐⭐ | https://www.terrapinn.com/conference/future-memory-storage/index.stm |
| 17 | **存储/内存厂商高管云集**: NVIDIA(Jason Hardy, VP Storage Tech)·AMD(Rita Gupta, Server Arch Fellow)·Intel(Richelle Ahlvers)·Samsung(Jin-Yub Lee/Taeksang Song)·SK hynix(Chunsung Kim)·KIOXIA(Neville Ichhaporia)·Micron(Jeremy Werner)·SanDisk(Jim Elliott/Karin Inbar) | ⭐⭐⭐⭐ | 同上 |
| 18 | **FMS 使命**: 先进内存/存储技术使能 AI 系统/数据中心/超大规模厂商以空前规模运行 — 存储作为 AI 基础设施核心主题 | ⭐⭐⭐ | 同上 |
| 19 | FMS 2026 新品牌（20周年 rebranding）+ CPD 认证（14 points） | ⭐⭐ | 同上 |

**2026-08-04 源状态**: Baidu ❌ · OCP ❌ · Bing ✅（UALink官网"17h前"为爬虫时间戳）· UALink官网 ✅（快照第4日一致）· FMS官网 ❌（403）· **FMS2026官方页 ✅（源发现，关键增量）**

> 📌 **关联判断**: FMS 以存储/内存为核心赛道，UALink 互联相关将主要出现在 **CXL 内存池化 / 存储扩展** session 中。UALink 官网未在首页显要位置列出 FMS 专属 demo 议程，**待 8/4-8/6 现场/媒体动态补充**。

### 2.7 今日快照（2026-08-05 — FMS 第2天）

> **官网快照第 5 日一致**，FMS 进行中但 UALink 官网首页未发布 FMS 现场/展台动态 — 符合开放标准组织"规范发布+展会静默"节奏。今日核心价值=**静默确认**与**数据质量观察**。

- **官网快照第5日一致**（2026-08-05）: 置顶动态（4份规范/董事会/公司化/200G 1.0）自 7/29 稳定，**无 FMS 专属议程** — 来源: https://ualinkconsortium.org/
- **Bing 检索无新信号**（2026-08-05）: 结果集与 8/02-8/04 一致，无 FMS 现场媒体增量 — 来源: https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026
- **OCP Global Summit 官网数据残留观察**（2026-08-05）: UALink 事件列表显示 "Oct 12th–17th, **2023**" — 旧数据未更新，2026 档期需另行确认 — 来源: https://ualinkconsortium.org/
- **FMS 第2天跟踪判断**（2026-08-05）: UALink 官网无现场动态 → 互联相关信息需从**媒体侧**采集（StorageNewsletter/Blocks & Files/SemiAnalysis 等 FMS 报道），官网渠道今日信息增益≈0
- **跟踪窗口更新**（2026-08-05）: OCP APAC Summit **6 天后**（8/11-12 台北）→ 官方档期已确认；Hot Interconnects 14 天后（8/19-21 线上） — 来源: https://ualinkconsortium.org/

**2026-08-05 源状态**: Baidu ❌（安全验证，连续5日）· OCP ❌（403，连续5日）· Bing ✅（无新信号）· UALink官网 ✅（快照第5日一致）

> 📌 **判断**: FMS 已进入第2天，UALink/CXL 现场实测数据大概率出现在第三方媒体报道而非官网 — **下轮建议补充媒体侧源**（如 StorageNewsletter / Blocks & Files / Tom's Hardware），官网渠道已进入边际收益递减区间。

### 2.8 今日增量（2026-08-06 — FMS 最后一天 & UALink 演讲日 🎯）

> **重大反转**: 前日判断\"官网渠道信息增益≈0\"被证伪 — 转向 **UALink Blog 子页面**（首页不显示）后发现 **7/29 发布的 FMS 2026 活动预告**，UALink 在 FMS 有明确展台+演讲安排。当前 CST 01:55 = PT 8/5 10:55，**演讲尚未开始**（PT 15:30 = CST 6:30），本文档为预告记录，现场结果待下轮补充。

| # | 发现 | 强度 | 来源 |
|:-|:-----|:----:|:-----|
| 20 | **UALink 是 FMS 2026 Organizational Sponsor（组织赞助商）**，设展于 **Open Standards Pavilion — Booth #725**（8/4-8/6 全程） | ⭐⭐⭐⭐ | https://ualinkconsortium.org/blog/join-the-ualink-consortium-at-fms-2026/ |
| 21 | **FMS 专题演讲预告**: 「The Future of AI Scale-Up: Latest Advancements in UALink Technology」8/5 **3:30-4:35pm PT** Ballroom C — 覆盖 **In-Network Collectives (INC) / Management Specifications / Chiplet Specifications** 三大更新方向 | ⭐⭐⭐⭐⭐ | 同上 |
| 22 | **Chat with the Experts**: 8/5 7:15-8:15pm PT FMS Conference Rooms UALink Table（非正式技术交流） | ⭐⭐⭐ | 同上 |
| 23 | **UALink Blog 系列时间线**（2025-08 → 2026-07 共 30+ 篇）: Roadmap Insights(3/6) · DMTF 互补标准(2/20) · 合规&互操作测试(1/14) · UALink+UEC 分工深度讨论(8/25/2025) · OCP EMEA(6/3) · Xcelerated Compute(5/6) | ⭐⭐⭐⭐ | https://ualinkconsortium.org/blog/ |
| 24 | **UALink 定位升级表述**: \"Accelerator fabrics 正在成为 AI memory hierarchy 的关键部分\" — 互联从\"通道\"升维为\"内存层级组件\" | ⭐⭐⭐ | https://ualinkconsortium.org/blog/join-the-ualink-consortium-at-fms-2026/ |
| 25 | **STH AMD Helios 架构深度解析**（8/3 Ryan Smith）: 72×MI455X 机架级系统深度剖析（直链404，标题确认存在，Helios 细节知识库已有归档） | ⭐⭐⭐⭐ | https://www.servethehome.com/?s=UALink |

**2026-08-06 源状态**: Bing ✅（UALink官网\"2天前\"=7/29博客索引时间戳）· UALink官网 ✅（首页快照第6日一致）· UALink Blog ✅（**源发现：FMS 2026 预告隐藏于此**）· STH ✅（Helios 深度解析标题确认）· OCP ❌（403，连续6日）· Baidu ❌（安全验证，连续6日）

> 📌 **判断**: ① 官网首页非全量——**Blog/Press Room 子页面是活动信息富矿**，下轮须纳入例行抓取；② UALink 演讲聚焦 INC/管理/Chiplet 三大方向，与 2.0 规范主题一致，**预计今日 CST 6:30 后有现场要点流出**；③ STH 的 AMD Helios 深度解析是 rack-scale 对标的重要二手源，直链待补。

### 2.9 今日增量（2026-08-10 — OCP APAC 前夜 🎯）

> **背景**: 08-07~08-09 三天空档后恢复跟踪。UALink FMS 演讲（8/5）已过 5 天，官网 Blog 无会后总结帖（最新仍为 7/29 预告）——**"展会静默"模式延续**，演讲要点未见公开详细记录。本轮核心增量=**UALink Blog 7/15 帖深读**（v1.5 缺失的实质内容）与**OCP APAC 明日开幕确认**（官网事件日历）。

- **UALink 会员数增至 115+ 家**（2026-07-15 博客，作者 Nolan Morgan）: 覆盖超大规模厂商/半导体/网络/IP 供应商/ODM/OEM/系统开发商；对比 2024-11 阿里云文章记录的"三十余家"，**18 个月增长约 3.8 倍**，生态规模扩张量化证据 — 来源: https://ualinkconsortium.org/blog/building-open-scalable-ai-infrastructure-with-ualink-1532/
- **UALink 技术定位关键澄清：基于 Ethernet 构建**（2026-07-15）: 非全新网络栈——在广泛部署的 Ethernet 技术之上增加 AI scale-up 所需的协议/内存语义/流控/可靠性特性，宣称"站在数十年 Ethernet 创新之上"实现低延迟高带宽 — 来源: https://ualinkconsortium.org/blog/building-open-scalable-ai-infrastructure-with-ualink-1532/
- **UALink 支持 AI Pod 最大 1,024 加速器**（2026-07-15 重申）: 与 200G 1.0 规范目标一致，为集合通信（collective operations）提供高效支撑 — 来源: 同上
- **UALink 官方路线图三方向重申**（2026-07-15）: INC（In-Network Compute）/增强管理性/Chiplet 支持，与 2.0 规范套件主题一致；规范体系扩至链路协议+软件栈+管理+合规四层 — 来源: 同上
- **OCP APAC Summit 明日开幕**（8/11-8/12 台北）: UALink 官网事件日历确认（UALink 代表通常出席行业活动演讲）；OCP 官网/专页均 403 无法获取议程细节，**下轮最大采集窗口** — 来源: https://ualinkconsortium.org/（Upcoming Industry Events）
- **UALink FMS 演讲（8/5）会后静默确认**（2026-08-10）: 官网 Blog 最新帖仍为 7/29 FMS 预告（无会后总结），STH UALink 搜索无 FMS 演讲独立报道（最新相关为 8/3 Helios Deep Dive）→ 现场要点或散落于厂商个别发布，无公开系统性记录 — 来源: https://ualinkconsortium.org/blog/ + https://www.servethehome.com/?s=UALink
- **UALink Blog 体系内容补全**（2026-08-10）: 除 7/15 帖外确认 6/24 帖「Exploring In-Network Compute: How UALink Is Redefining AI Scale-Up Architecture」（INC 主题深挖，3 min）——Blog 为官网技术内容富矿，共 30+ 篇 — 来源: https://ualinkconsortium.org/blog/exploring-in-network-compute-how-ualink-is-redefining-ai-scale-up-architecture-1509/

**2026-08-10 源状态**: Baidu ❌（安全验证，连续第7日）· OCP ❌（403，含专页，连续第7日）· Bing ✅（结果集与既往一致，无新信号）· UALink官网 ✅（快照第10日一致 + OCP APAC 8/11-12 事件确认）· UALink Blog ✅（7/15 帖深读，新增3条实质发现）· STH ✅（UALink 搜索无 FMS 演讲报道）

> 📌 **判断**: ① FMS 演讲（INC/管理/Chiplet 主题）现场要点 5 天未见于官网/STH → 信息增益≈0，不必再追；② **OCP APAC（8/11-12 台北）为下轮核心窗口**——需关注 UALink 是否派代表演讲、OAM/GPU baseboard 标准亚太更新；③ UALink 会员 115+ 与"基于 Ethernet"定位共同强化其**开放生态+低成本兼容**叙事，与 NVLink 封闭路线差异化明确。

### 2.10 今日增量（2026-08-11 — OCP APAC 开幕日 🎯 & TASK 白皮书全文深读）

> **背景**: OCP APAC Summit 今日（8/11-12）台北开幕。UALink 官网快照第11日一致（首页头条仍为 4/9 四规范发布旧闻），Blog 最新帖仍为 7/29 FMS 预告（无 8 月新帖，"展会静默"模式延续）。本轮核心增量 = **TASK Consultancy 独立白皮书全文深读**（16 页，2026-01 官网上传，此前仅首页推广条可见）——UALink 首次获得独立咨询机构级技术分析，含大量此前未记录的量化规格。

- **TASK Consultancy 独立白皮书发布**（2026-01 官网上传，16 页 PDF）: 第三方权威技术分析《UALink™: An Open, High-Efficiency Scale-Up Interconnect for AI》，作者 Jimmy Pike（TASK Consultancy 创始人/前 Dell SVP & Senior Fellow，45+ 年行业经验，70+ 专利）——UALink 技术叙事从"厂商自述"升级为"独立第三方背书" — 来源: https://ualinkconsortium.org/wp-content/uploads/2026/01/UALink_White_Paper_Publication_Candidate_FINAL_VERSION.pdf
- **93% 有效带宽效率目标量化**（TASK 白皮书）: 协议载荷/物理层容量 = 93% 目标（精简协议头+简化 MAC 处理）；<4m 铜缆约 1μs RTT、链路层处理数百 ns；事务大小 64-256 字节（确定性缓冲分配的基础） — 来源: 同上
- **128 PB fabric 级统一地址空间（57-bit）**: UALink 在**规范层**定义内存语义（而非各 XPU 各自处理）——任何厂商加速器可直接寻址他厂加速器内存，无需厂商间地址翻译协调；对照 SUE 明确"地址翻译由 XPU 在 SUE 实例外处理"，跨厂商需软件翻译层 — 来源: 同上
- **多层信用流控细节**（TASK 白皮书首次披露）: 每跳 3 个独立信用域（UPLI 协议→事务层 / TL 事务→物理链路 / switch ingress-core）→ 单跳（加速器→交换机→加速器）共 **6 个独立信用环**；背压逐环级联保证无损（switch core 满→停发 ingress 信用→停发 TL 信用→UPLI 停发）；vs 以太网 CBFC 每链路仅 1 个信用机制（2 个/单跳双向） — 来源: 同上
- **拓扑支持矩阵**（TASK 白皮书）: mesh/ring（4-16 节点小规模）· torus（中规模均衡带宽）· **switched-pod 主推**（数百至数千加速器，无损确定性保留）；管理栈 = **SAI（Switch Abstraction Interface）+ DMTF Redfish**，兼容现有数据中心编排工具免重训 — 来源: 同上
- **生态就绪度**（TASK 白皮书）: 交换硅多厂商开发中，**评估硬件预计 2026 后期**；物理层完全复用 IEEE 802.3 PAM4 PHY/线缆/连接器/retimer；光延伸（20m+ row-scale）**无需协议变更**（仅 PHY 级铜→光替换，同软件栈/固件/管理工具） — 来源: 同上
- **UALink vs NVLink 量化对比**（TASK 白皮书附录 A）: NVLink 5.0 = 1.8TB/s·GPU、sub-μs、标准 NVSwitch 配置 ≤256 GPU（DGX B100/HGX B100）；UALink = ≤1,024 加速器/pod（早期实现 576）、93% 效率目标、开放治理；**NVLink Fusion 许可计划（2025-05-18 推出）仍为专有治理**——NVIDIA 保留演进/认证/路线图控制权 — 来源: 同上
- **互联成本占比量化**（TASK 白皮书）: **$100M AI 部署中互联占 $15-25M（15-25%）**——"fabric 成本媲美加速器"是开放生态核心经济论据（解耦加速器与互联选择、避免复合锁定）；以太网 PHY 400G→800G→1.6T 演进红利被 UALink 直接继承（免代际重发明） — 来源: 同上
- **OCP APAC Summit 今日开幕**（8/11-12 台北）: 官网事件日历确认；Blog 无 8 月新帖（最新仍 7/29 FMS 预告）→ **开幕日静默，"展会静默"模式延续**；UALink 是否派代表演讲需会后观察 — 来源: https://ualinkconsortium.org/ + https://ualinkconsortium.org/category/blog/
- **Hot Interconnects 8/19-21 虚拟形式**（官网事件日历精确化）: 8 天后（虚拟），互联学术前沿，UALink 论文/演示潜在平台 — 来源: https://ualinkconsortium.org/

**2026-08-11 源状态**: Baidu ❌（安全验证，连续第8日）· OCP ❌（403，连续第8日）· Bing ✅（命中 UALink 官网"1天前"索引=首页推广条更新信号）· UALink官网 ✅（快照第11日一致 + OCP APAC 开幕确认 + TASK 白皮书推广条）· UALink Blog ✅（无 8 月新帖确认）· TASK白皮书 ✅（PDF 全文解析成功，16 页）

> 📌 **判断**: ① **TASK 白皮书是本月最实质的技术增量**——独立第三方（前 Dell SVP 执笔）给出了 UALink 迄今最完整的量化规格（93% 效率/128PB 地址空间/6 信用环/1,024 加速器）与 NVLink/Ethernet 双对比矩阵，可作为 UALink 技术底稿引用；② OCP APAC 开幕日官网静默，UALink 演讲信息大概率会后 1-3 天才出现（参考 FMS 教训），下轮重点扫 STH/Bing 的台北现场报道；③ UALink 白皮书"chiplet 无需许可即可实现兼容接口"论点直接回应 NVLink Fusion 许可模式——开放 vs 专有的治理叙事进一步清晰。

### 2.11 今日增量（2026-08-12 — OCTS 2026 新源深挖 & OCP APAC 会期确认 🎯）

> **背景**: 本轮最大增量 = **新源 ocpasia.org（OCP 中国区）首次纳入并全文抓取**——此前跟踪一直聚焦 UALink 官网/Blog/STH，**完全缺失 OCP 中国生态动态**。经查，**2026 开放计算技术大会（OCTS 2026 = OCP China Day 2026）已于 7/9 在北京国际饭店举行完毕**（非未来事件），UALink 董事会成员、阿里云 UALink 董事代表均在大会上发声，超节点主题议程密集。同时 UALink 官网确认 OCP APAC（8/11-12）已从 Upcoming Events 移除（会期进行/结束状态）。

- **新源：OCTS 2026 开放计算技术大会概况**（2026-07-09 北京国际饭店举行完毕）: OCP + OCTC（中国电子工业标准化技术协会开放计算标准工作委员会）联合主办，主题"智算无界：开放、多元、扩展"；规模 = **800+ AIDC 上下游企业 / 8000+ 现场与会者 / 230+ 场技术分享**；嘉宾含 OCP Foundation CEO George Tchaparian、UALink&CXL 董事会成员 Chris Petersen、阿里云 CXL&UCle 董事会代表陈健、NVIDIA 网络亚太区高级总监宋庆春 — 来源: https://ocpasia.org/index.html
- **UALink 董事会成员 Chris Petersen（Astera Labs）主论坛演讲**（OCTS 2026, 09:50-10:05）: 「灵活部署 XPU：面向最大推理性能与最低 Token 成本的开放机架架构」——UALink 代表在中国开放计算大会主论坛发声，开放 Scale-Up 叙事进入中国生态 — 来源: 同上
- **阿里云 UALink 联盟董事代表孔阳演讲**（OCTS 2026, Track4 14:00-14:20）: 「基于 UMX 统一内存存储扩展的 AI Scale Up 架构」——中国云厂商以 UALink 董事身份参与联盟治理并在国内大会披露架构实践，UALink 中国会员生态落地证据 — 来源: 同上
- **《吉瓦（GW）级开放智算中心框架技术报告》v1.0 发布**（OCTS 2026 现场发布，7/16 浪潮信息核心参编报道）: OCP 中国社区负责人叶毓睿发布——中国开放生态的 GW 级智算中心框架标准（对应 NVL72 级超节点规模化叙事） — 来源: 同上
- **超节点主题议程密集（OCTS 2026 全景）**: 主论坛「AI 超节点基石组件的创新：高速互连实践」（立讯技术 NPO/CPO/XPO + 庆虹电子）· Track4「XPU 模组标准化接口设计」（字节跳动+STE）· Track4「智算 Scale-up 互联的需求及演进思考」（中国移动研究院）· Track5「AI 超节点高速互连系统方案」（庆虹电子）· Track5「面向 AI 时代的整机柜解决方案：百度天池超节点」（百度）· Track5「开放解构超节点：筑牢可持续发展的 AI 算力基石」（中国移动）——**国内超节点高速互连（448G/NPO/CPO/XPO）与开放架构是本次大会主线之一** — 来源: 同上
- **浪潮信息发布多模融合超节点 + CPU 原生液冷整机柜**（2026-07-09 OCTS 2026 期间）: 浪潮以"Agent 基础设施核心底座"定位发布——国内整机厂超节点产品化动态，与 OAM/GPU baseboard 开放标准演进并行 — 来源: 同上
- **OCP APAC Summit（8/11-12 台北）从 UALink 官网 Upcoming Events 移除**（2026-08-12 确认）: 事件日历仅剩 Hot Interconnects（8/19-21 虚拟）/AI Infra Summit（9/15-17）/OCP Global Summit（10/12-17 残留条目）——OCP APAC 会期进行/结束状态确认；UALink 是否参与台北现场仍无公开记录 — 来源: https://ualinkconsortium.org/

**2026-08-12 源状态**: Baidu ❌（安全验证，连续第9日）· OCP ❌（403，连续第9日）· Bing ✅（**新源命中：ocpasia.org**）· UALink官网 ✅（快照第12日一致 + 事件日历 OCP APAC 移除确认）· ocpasia ✅（**新源首次纳入，全文抓取成功**）· UALink Blog ✅（无 8 月新帖）

> 📌 **判断**: ① **OCTS 2026 填补了中国开放计算生态空白**——UALink 董事（Petersen）与阿里云 UALink 董事代表（孔阳）同台，证明 UALink 在中国生态有实质布局（阿里云为创始会员/董事）；② **GW 级开放智算中心框架报告 v1.0** 是国内对标 NVL72 规模化叙事的标准化动作，与超节点主题直接相关，下轮可深挖报告原文；③ OCP APAC（台北）会期已确认但 UALink 现场参与无公开记录——本轮后**台北线索关闭**，转盯 8/19-21 Hot Interconnects（虚拟）与 9/15-17 AI Infra Summit；④ ocpasia.org 纳入例行源，弥补 Baidu/OCP 双源长期不可用造成的中国侧信息缺口。

### 2.12 今日增量（2026-08-14 — UALink Press Room 全量纳入 & 中国生态落地实证 🎯）

> **背景**: 本轮最大增量 = **UALink Press Room（/news/）首次全量纳入例行抓取**——此前仅跟踪官网首页快照/Blog/STH，导致 2026 年 4 月以来一批重要发布（四规范发布详情、6 份规范下载页、Member News 生态进展）被系统性遗漏。触发点 = 官网首页出现新横幅「UALink Consortium Publishes Four Specifications」（4/7 旧闻新挂首页），深挖后确认 Press Room 信息密度远超首页。同时 ODCC 微信文章（UALink 测试验证服务）与 Netforward 官网（世界首个 UALink 交换芯片）证实**中国 UALink 生态已从标准理解走向芯片落地**。

- **UALink 官网新横幅：四规范发布（BusinessWire 新闻稿 2026-04-07，首页横幅可见）**: 四规范 = Common 2.0（在网计算 INC）+ 200G Data Link/PHY 2.0 + Chiplet 1.01 + Manageability 1.0，宣称支持多负载环境部署、提升效率/性能/易实现性 — 来源: https://ualinkconsortium.org/
- **Specifications 页确认 6 份规范全部公开可下载（2026-08-14 核实）**: ① 200G 1.0 ② Common 2.0（In-Network Compute）③ **128G DL/PL 1.0**（此前未覆盖）④ 200G DL/PL 2.0（DL/PL 从 Common 拆分，加速新物理层/速率演进）⑤ Chiplet 1.01（完全兼容 UCIe 3.0，简化 chiplet 生态集成）⑥ Manageability 1.0（gNMI/Yang/SAI/Redfish 统一控制管理面）——**UALink 2.0 规范公开文本已可下载**（§5 待办实质进展） — 来源: https://ualinkconsortium.org/specification/
- **Netforward（深圳楠菲微电子）完成世界首个 UALink™ Switch/IP 全周期 IC 设计 + FPGA 原型验证**（2026-04-24）: 实现 UALink 1.0，规划支持 2.0 的 Link Resiliency/Link Folding；目标超节点内 100+ 加速器全 mesh 互联；集成在网计算（INC）+ 完整 RAS；验证平台 = FPGA-VU19P×2（模拟 GPU）+ VP1902（Switch），DAC 直连/交换组网双场景，X2/X4 模式，24h 持续测试，覆盖 PL/DL/TL/UPLI 四层——UALink 从规范走向工程实现的芯片级证据 — 来源: https://www.netforward-tech.com/xinwenzhongxin/23.html
- **ODCC 发布 UALink 测试验证服务，UALink 生态关键里程碑**（2026-04-02 ODCC 春季全会）: 发布人 = ODCC 新测组组长、中国信通院正高工郭亮 + ODCC 执行委员、阿里云服务器研发资深总监王伟；基于 UALink 1.0，分层验证 TL（Flit 打包/信用管理/地址压缩）/DL（Flit 封装/流控/重传纠错）/PL（多速率/复位热插拔/编解码）+ 异常注入（丢包/乱序/CRC 错误/链路断开）；**内测企业 = 楠菲微电子/瀚博半导体/星拓微电子/集益威**（IP 层互通完成）；UALink 联盟主席 Kurtis 视频致辞确认中国区测试服务；阿里云磐久超节点支持 UALink + 通过 ODCC AI Infra 方升项目适配；物理层路线 112G→224G→448G — 来源: https://mp.weixin.qq.com/s/jrq9_i8H5HMIxT3HixK8gg
- **Synopsys 发布 UALinkSec_200 安全模块**（2026-01-15）: UALink 链路安全强化（Member News，UALink 安全维度首次披露） — 来源: https://www.synopsys.com/articles/securing-ualink-security-module.html
- **Credo 发布业界首款 224G 多协议 AI Scale-Up Retimer**（2026-01-29）: 支持 UALink/ESUN/Ethernet 三协议（Member News，Press Room 列表确认；外链 BusinessWire 反爬 403，以 Press Room 为源） — 来源: https://ualinkconsortium.org/news/
- **Keysight 推出 Scale-Up 验证解决方案**（2026-02-18）: 覆盖 UALink 200G/PCIe 7.0/CXL 3 测试（Member News；外链 403，以 Press Room 为源） — 来源: https://ualinkconsortium.org/news/
- **国内技术社区规范消化热度信号**（2026-08-10~12，Bing 命中）: CSDN 连续发布《UALink_200G Rev 1.0 Specification》中文翻译系列（第 1 章引言 + 全文翻译，阅读数百次）——UALink 规范中文解读进入国内社区自传播阶段 — 来源: https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026
- **UALink 官方中文白皮书存在但直链不可用（数据缺口标注）**: Bing 索引到 ualinkconsortium.org 官方 UALink-1.0-White_Paper_CH_v2 PDF（2025-08-22 索引），但实测 wp-content 直链 404——官方中文文档确认存在，下载路径待下轮从 Resource Library/官网资料区核实（不编造链接） — 来源: 同上 Bing 结果页

**2026-08-14 源状态**: Baidu ❌（安全验证，**连续第10日**）· BusinessWire ❌（403 反爬）· UALink 官网 ✅（首页横幅新挂 + Press Room 首次全量纳入）· UALink Blog ✅（无 8 月新帖，静默第 16 天）· Netforward ✅ · ODCC微信 ✅ · Bing ✅ · STH ✅（UALink 无新独立报道，MI455X Deep Dive 8/12 为生态背景）

> 📌 **判断**: ① **Press Room 是本专题被低估的高密度源**——单页含 7 条 Press Release + 20+ 条媒体报道 + 14 条 Member News，信息密度远超首页/Blog，正式纳入例行抓取；② **中国 UALink 生态已从"标准理解"进入"芯片落地"阶段**——楠菲微（交换芯片原型）+ 瀚博/星拓/集益威（IP 内测）+ ODCC 官方测试认证三线并进，且阿里云以董事身份主导（磐久超节点 + 方升项目），这是此前跟踪完全缺失的维度；③ **四规范发布（4/7）与 6 规范可下载** 将 §5 待办"2.0 规范公开文本获取"从"待办"转为"已确认可获取"，下轮可直接下载 Common 2.0 原文校验 TASK 白皮书量化数据；④ OCP APAC（台北）会后官网/STH 均无 UALink 现场记录 → **台北线索正式关闭**，转盯 Hot Interconnects（8/19-21 虚拟）。

### 2.13 今日增量（2026-08-16 — 新源 OAII/GCC 维度纳入 🎯）

> **背景**: 本轮最大增量 = **新源命中「Open AI Infra Summit 2026 收官报道」（人工智能日报转载 IT时代网）**，全文抓取后确认这是此前跟踪**完全缺失的第二条中国开放标准平行线**——OCP/OCTC（OCTS 2026，8/12 已纳入）之外的 **GCC/OAII 社区**（全球计算联盟下属 Open AI Infra 社区）。两者同为中国超节点开放生态的标准化组织，但 OAII 侧重"从大用户需求出发的端到端规范"（AIDC 基础设施规范/ClusterBench/双零行动），与 OCTS 的"国际组织本土落地"定位互补。UALink 官网快照第 13 日一致（置顶仍为 4/9 四规范/董事会/公司化），Blog 静默第 18 天（最新 7/29 FMS 预告）。

- **新组织维度: OAII 社区（Open AI Infra）2025-10-28 成立于北京，全球计算联盟（GCC）分支机构**（2026-04-27 报道确认）: 定位"面向 AI 时代全栈智算基础设施的开放协作平台"，链接大用户与核心技术方推进技术规范制定——与 OCP China（OCTC）平行但独立运作的中国开放计算组织，超节点标准生态"双组织"格局确立 — 来源: https://www.rgznrb.com/yunjisuan/5622.html
- **Open AI Infra Summit 六大论坛全景**（2026 北京落幕，4/27 报道）: 高速互联 / 800V 供配电 / 全栈液冷 / 超节点生态 / GW 级 AIDC / 超节点性能 Benchmark——六大主题覆盖超节点全链路，与 UALink/OCP 三层标准架构（互联→板卡→机架）映射清晰 — 来源: 同上
- **高速互联论坛共识（百度/华为/Molex/阿里云/安费诺/庆虹/中科曙光/立讯/华工正源）**: 超节点向 **128 卡、256 卡规模化**演进下，PCB 损耗/线缆管理/连接器可靠性/光链路预算问题凸显；**铜互联柜内短距仍有优势，光互联为长距+液冷场景必然选择**；UALink 等开放协议 + CPO/NPO/XPO 多元光路 + SerDes 到系统级测试体系共同推动全链路协同——UALink 在中国高速互联论坛的核心议题地位再确认 — 来源: 同上
- **超节点生态论坛（字节/锐捷/Solidigm/阿里云/小红书/华为/新华三）**: 类 OCP 形态 **DPU 标准化**、XPU 模组设计、**QLC 应对 KV Cache 海量需求**、**CXL 与 UALink 加速存储与加速器互连**、**OpenUBMC 开源固件**——"超节点=覆盖芯片/模组/系统/集群的完整技术体系"叙事与中国实践对齐 — 来源: 同上
- **超节点性能 Benchmark 论坛: ClusterBench β版正式发布**（中国电子技术标准化研究院）: 通算超节点基准工具，涵盖大数据/数据库/AI 等 **6 类负载场景**——超节点性能评测标准化动作（关联: 知识库 cluster-training/compute-platform 已收录该工具，本组从标准生态角度关联） — 来源: 同上
- **浪潮信息 3D Mesh 架构 64 卡超节点 + 通信优化成果**（Benchmark 论坛披露）: 国内超节点系统级评测案例；天翼云展示通算超节点测试 + CXL 内存池化降本路径 — 来源: 同上
- **GW 级 AIDC 论坛: 《AIDC 基础设施规范》发布**（OAII 社区）: 明确机柜功率等级、供电接口等关键参数，推动液冷机房"即插即用"；同期发布《冷板液冷系统智能运维技术规范》——中国 GW 级智算中心规范体系从"框架报告"（OCTS 的 GW-Scale v1.0）细化到"基础设施参数级规范" — 来源: 同上
- **800V 供配电论坛量化锚点**: 单机柜功耗突破 **200kW 乃至 500kW** 驱动 800V HVDC 迁移；百度程冰（OAII AI 整机柜项目群供电项目组组长）披露 2026 供电项目规划——与 NVIDIA 800VDC V2.0（MEMORY 已归档）形成中美双线呼应 — 来源: 同上
- **Bing 新信号: CSDN 完成《UALink 200G 1.0 Specification》中文版全文翻译**（约 4 天前，8/12 前后）: 阅读 937 次，覆盖信号定义/协议格式/编码规则/示例图——UALink 规范中文解读从"引言+全文分章"进入"单篇完整译稿"阶段，国内社区消化深度升级 — 来源: https://blog.csdn.net/jw915086731/article/details/155225567
- **跨组去重标注（8/15 其他组同日文件核验）**: hardware 组已收录 SemiEngineering UALink 单跳分析（8/13）、tech 组已收录 STH 160-bay/Dryas 追踪引擎/TrendForce PCB（8/14）→ 本组不重复收录，仅保留 OAII 维度增量 — 来源: 本组核验
- **事件日历倒计时**: 🎯 **Hot Interconnects 8/19-21（虚拟）3 天后**；UALink 官网事件日历确认无更新（OCP Global Summit 残留条目仍为 2023 旧数据） — 来源: https://ualinkconsortium.org/

**2026-08-16 源状态**: Baidu ✅（**源复活：移动端 UA 抓取成功，9 条结果含新源命中**）· ocpasia ✅（OCTS 2026 静态页，与 8/12 一致无新动态）· UALink官网 ✅（快照第13日一致）· UALink Blog ✅（无 8 月新帖，静默第 18 天）· Bing ✅（结果集与既往一致，无新信号 + CSDN 新译稿命中）· 新增源 rgznrb ✅（Open AI Infra Summit 收官报道全文）

> 📌 **判断**: ① **OAII/GCC 是本专题迄今最大组织维度盲区**——中国超节点开放生态存在"OCP/OCTC（国际组织本土化）"与"GCC/OAII（本土组织自主化）"双轨，前者已跟踪、后者 8/16 首纳；② OAII 的 ClusterBench（性能评测）+ AIDC 基础设施规范（参数级规范）与 OCTS 的 GW-Scale 框架报告形成"评测/规范/框架"三层中国标准体系；③ Hot Interconnects 3 天后开幕，UALink 官网/Blog 在 8/19-21 前大概率维持静默，现场信号关注学术论文侧。

### 2.14 今日快照（2026-08-17 — Hot Interconnects 前夜 🎯）

> **背景**: 官网快照第 14 日一致（置顶仍为 4/9 四规范/董事会/公司化，TASK 白皮书推广条在位），Blog 静默第 19 天（最新 7/29 FMS 预告，8 月零新帖）。本轮为 **Hot Interconnects（8/19-21 虚拟）开幕前最后快照**，增量 = 静默确认 + 倒计时锚点 + ODCC 源可用性首测。

- **官网快照第 14 日一致**（2026-08-17）: 置顶动态（四规范发布 / 阿里苹果 Synopsys 入董事会 / 公司化 / 200G 1.0 / Statements of Support / TASK 白皮书下载横幅）自 7/29 起无变化——开放标准组织"大事件驱动型"发布节奏延续 — 来源: https://ualinkconsortium.org/
- **UALink Blog 静默第 19 天确认**（2026-08-17 Blog 全量列表快照）: 最新帖仍为 7/29「Join the UALink Consortium at FMS 2026」，8 月零新帖；Blog 共 37 帖（2025-02→2026-07 倒序），6/24 INC 深挖帖仍为最近技术主题帖——8/19 Hot Interconnects 前预计维持静默 — 来源: https://ualinkconsortium.org/blog/
- **🎯 Hot Interconnects 8/19-21（虚拟）2 天后开幕**（2026-08-17 事件日历）: 官网 Upcoming Events 唯一临近事件；上届有「UALink for Rack-Scale AI Interconnects」议题，本届 UALink 学术论文/演示为下一核心采集窗口；AI Infra Summit 9/15-17 倒计时 29 天；OCP Global Summit 残留条目仍为 2023 旧数据（未更新） — 来源: https://ualinkconsortium.org/
- **ODCC 官网首次纳入抓取失败**（2026-08-17, 30s 超时）: 此前 ODCC 动态仅经微信文章收录（8/14 UALink 测试验证服务）；odcc.org.cn 直连不可用，后续尝试移动端/镜像通道——ODCC 作为中国开放计算标准主力组织，其官网源价值高，值得恢复尝试 — 来源: https://www.odcc.org.cn/
- **Baidu 安全验证拦截连续第 11 日**（2026-08-17）: 与既往一致；中文检索依赖 Bing/ocpasia/rgznrb 三源补位 — 来源: https://www.baidu.com/
- **Bing 检索无新信号**（2026-08-17）: 结果集与 8/16 一致（UALink 2.0 知乎解读 4/9 / CSDN 200G 中译 / UALink 联盟百科 / 官方白皮书 CH 版）；CSDN 8/13 前后「NVLink/IB/UALink/UEC 深度对比」综合文为相对新信号，但搜索结果 URL 折叠无完整路径、无法验证 HTTP 200，按规则不收录为独立发现 — 来源: https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026

**2026-08-17 源状态**: Baidu ❌（安全验证，连续第11日）· ODCC ❌（30s 超时，首次纳入失败）· Bing ✅（无新信号）· UALink官网 ✅（快照第14日一致）· UALink Blog ✅（静默第19天，37帖全量列表快照）

> 📌 **判断**: ① 8/19-21 Hot Interconnects（虚拟）为本专题下一核心窗口——UALink 组织 2025 年起保持"展会演讲+会后 Blog 总结"模式（OCP EMEA/Xcelerated/SC25 均如此），本届若有 UALink 议程，官网 Blog 预计 8/19 当日或次日更新，可打破 19 天静默；② ODCC 官网超时暴露中国侧源缺口（当前仅微信文章单点），下轮尝试 ODCC 微信公众号文章检索补位；③ 8 月整体为 UALink 官方发布淡季，实质增量集中于第三方生态（ODCC 测试/国产芯片）与学术侧（Hot Interconnects），符合开放标准组织年度节奏。

### 2.15 今日增量（2026-08-18 — UALink 2.0 官方材料全文深读 & Hot Interconnects 开幕前夜 🎯）

> **背景**: 本轮最大增量 = **UALink 2.0 官方新闻稿 PDF 全文解析**（8/14 标记待办"下载原文校验量化数据"的实质推进）+ **2.0 Statements of Support 全文**（5 家厂商）+ **董事会 12 家完整名单确认** + **"互操作性与合规项目"计划新信号**。同时完成 Press Room 媒体线索补全（8/14 首次全量后的增量扫描）与跨组去重核验（hardware/tech 8/16-17 仅事件窗口提及，无规范细节重复）。官网快照第 15 日一致，**Hot Interconnects 明日（8/19）开幕**。

- **UALink 2.0 官方新闻稿全文解析（2026-04-07 发布，本轮 PDF 两页全文深读）**: ① Common 2.0 = 引入**在网计算（In-Network Compute）**，定义加速器间计算与通信协同，降低延迟、节省带宽、提升分布式训练/推理在复杂多负载环境下的扩展效率；② **200G DL/PL 2.0 = DL/PL 从 Common 规范拆分**，使新物理层/新速率可独立快速演进（无需牵动其他规范）；③ **Manageability 1.0** = 将 UALink 定义为带集中控制/管理平面的系统，采用 gNMI/Yang/SAI/Redfish 标准化协议与 API；④ **Chiplet 1.0** = 定义接口/形态/流控/chiplet 管理标准化，**完全兼容 UCIe 3.0**（简化既有 chiplet 生态集成） — 来源: https://ualinkconsortium.org/wp-content/uploads/2026/04/UALink-2.0-Specification-PR_FINAL.pdf
- **UALink 董事会 12 家完整名单确认**（新闻稿 About 段落官方文本）: Alibaba / AMD / Apple / Astera Labs / AWS / Cisco / Google / HPE / Intel / Meta / Microsoft / Synopsys——覆盖云厂商×5（阿里/AWS/Google/Meta/Microsoft）+ 芯片×3（AMD/Intel/Synopsys）+ 网通（Cisco/Astera Labs）+ 终端（Apple/HPE），全产业链治理结构；8/14 仅记录"阿里/苹果/Synopsys 加入"，本轮补全 12 家 — 来源: 同上
- **UALink 计划推出互操作性与合规项目（新信号）**: 新闻稿明确"Consortium plans to introduce **interoperability and compliance programs** designed to support a robust, multi-vendor ecosystem"——与 ODCC 中国测试验证服务（8/14 已收录）形成国际/国内双轨呼应，开放标准的"认证体系"建设进入官方议程 — 来源: 同上
- **UALink 2.0 Statements of Support 全文（5 家厂商，本轮全文抓取）**: AMD Kurtis Bowman（UALink 董事会主席兼 AMD 架构战略总监）称 2.0 为"开放高性能 AI 基础设施的重要里程碑"；Astera Labs Chris Petersen（董事会成员）强调 INC/标准化 chiplet/管理工具三合一、"开放标准让整个生态比任何单厂商跑得更快"；Google Cloud Amber Huffman 指出 gNMI+Redfish 管理性对规模/可靠性/互操作关键；Synopsys Priyank Shukla 以 224G+安全 IP 降低集成风险；UnifabriX CEO Ronen Hyatt 定位 UALink 为"开放内存中心 scale-up 使能者" — 来源: https://ualinkconsortium.org/news/statements-of-support-for-the-ualink-2-0-specification/
- **产业信号: UALink 2.0 规范先于 v1.0 硅片出货**（The Register 2026-04-07 标题「No-Nvidia interconnect club delivers 2.0 spec before v1.0 silicon ships」）: 开放标准迭代速度领先硅片落地时差；EETimes 5/4「AI Accelerator Spec Maintains Rapid Update Pace」呼应——规范快速演进 vs 生态硅片爬坡的节奏差是 2026 下半年关键观察点 — 来源: https://ualinkconsortium.org/news/（Press Room 媒体索引）
- **UALink 2.0 媒体报道线索补全**（Press Room 索引增量，8/14 未收录）: techstrong.ai「UALink 2.0 Targets NVIDIA's Grip on AI Interconnects」(4/8) · networkworld「New v2 UALink specification aims to catch up to NVLink」(4/7) · convergedigest「Q&A: UALink 2.0, In-Network Compute, and the Future of Open AI Interconnects」(4/7) · 「UALink roadmap plots course to optimized AI data center interconnects」(2/20) —— 2.0 发布获 4+ 独立媒体深度报道，NVLink 对标叙事是共同主线 — 来源: https://ualinkconsortium.org/news/
- **OCP-UALink 生态协同框架确认**（2025-04-29 Press Room 索引）: Open Compute Project Foundation 与 UALink 建立 **AI and HPC cluster framework**（双报道: "OCP and UALink team up to supercharge AI interconnect performance"）——OCP 板卡/机架标准与 UALink scale-up 互联标准的三层架构打通（Layer 1↔Layer 2/3），开放阵营协同证据 — 来源: https://ualinkconsortium.org/news/
- **官网快照第 15 日一致 + Hot Interconnects 明日开幕**（2026-08-18）: 置顶动态（四规范/董事会/公司化/200G 1.0/TASK 白皮书推广条）无变化；**Hot Interconnects 8/19-21（虚拟）明日开幕**——UALink 上届有「UALink for Rack-Scale AI Interconnects」议题，本届为下一核心采集窗口（Blog 静默 20 天，若 UALink 演讲将打破）；AI Infra Summit 9/15-17 倒计时 28 天（Santa Clara）；OCP Global Summit 残留条目仍为 2023 旧数据 — 来源: https://ualinkconsortium.org/

**2026-08-18 源状态**: Baidu ❌（安全验证，连续第12日）· ODCC ❌（30s 超时，连续第2日）· Bing ✅（UALink 官网"1天前"索引=四规范推广条时间戳）· UALink官网 ✅（快照第15日一致 + Press Room 媒体索引增量）· UALink 2.0 新闻稿 PDF ✅（全文解析，2 页）· UALink 2.0 Statements of Support ✅（全文）· BusinessWire ❌（403，与 8/14 一致）

> 📌 **判断**: ① **UALink 官方治理/规范材料已深读完毕**——董事会 12 家名单、4 份规范细节、互操作合规计划、5 家支持声明均已入库，UALink 侧信息底稿完整；② **"2.0 先于 v1.0 硅片"节奏差**是新增产业观察维度——开放标准组织以"规范速度"竞争，但生态落地取决于硅片（交换芯片/Retimer/IP）爬坡，ODCC 测试认证（中国）与互操作合规项目（国际）正是弥合这一时差的机制；③ **Hot Interconnects 明日开幕**为下轮唯一核心窗口，若 UALink 有议程，官网 Blog 将打破 20 天静默；④ 8 月官方淡季判断延续，本轮增量全部来自"官方材料深读"而非"新事件"，符合大事件驱动型组织节奏。

### 2.16 今日增量（2026-08-19 — ODCC 测试验证服务微信原文深读 & Hot Interconnects 开幕日 🎯）

> **背景**: 本轮最大增量 = **ODCC UALink 测试验证服务微信原文全文深读**（阿里云基础设施公众号，4089 字；08-14 仅从 Press Room 索引确认存在，本轮拿到发布人/分层验证/异常注入/产业定位全部机制细节）——中国 UALink 生态从"名单确认"走向"机制细节"。同时完成 UALink 2.0 新闻稿 PDF 二次抓取复核（与 08-18 收录逐项一致）与 Bing 中文生态新信号采集。**Hot Interconnects 今日（8/19）开幕**。

- **ODCC UALink 测试验证服务全文深读（2026-04-02 ODCC 春季全会发布，本轮微信原文 4089 字全解析）**: 发布人 = ODCC 新测组组长、中国信通院正高级工程师**郭亮** + ODCC 执行委员、阿里云服务器研发资深总监**王伟**；服务**基于 UALink 1.0 规范**搭建，对互连 IP、链路协议、事务交互、数据传输核心功能验证，保障不同厂商 Switch 芯片与接口 IP 在 Scale Up 组网中兼容互通 — 来源: https://mp.weixin.qq.com/s/jrq9_i8H5HMIxT3HixK8gg
- **分层验证机制（ODCC 原文技术细节）**: **TL 层**验证 Flit 打包、信用管理、地址压缩；**DL 层**覆盖 Flit 封装、流控、重传与纠错；**PL 层**进行多速率、复位/热插拔、编解码测试；并通过**异常注入**（丢包、乱序、CRC 错误、链路断开）全面检验协议支持完整度与健壮性——"分层验证 + 场景全覆盖 + 异常压力"三结合 — 来源: 同上
- **服务定位与产业意义（ODCC 原文）**: 为国内 UALink 生态提供**第三方公平公正的技术测试与产品认证**，让生态"有章可循（官方规范）+ 有证可依（测试认证）"，为兼容硬件研发、第三方检测、**招标选型及客户验收**提供统一依据——开放标准落地闭环的关键机制 — 来源: 同上
- **UALink 联盟主席 Kurtis Bowman 视频致辞原文（ODCC 发布会）**: "协议验证是发展和建立开放生态系统的关键之一。感谢 ODCC 与 UALink 联盟一起在中国地区发起 UALink 测试验证服务……感谢中国地区 UALink 成员单位为推动规范落地所做出的持续努力"——联盟官方背书中国区测试认证体系 — 来源: 同上
- **中国生态落地实证（ODCC 原文；08-14 名单确认 → 本轮机制确认）**: 内测企业**楠菲微电子、瀚博半导体、星拓微电子、集益威**已在 **IP 层**完成测试；**阿里云磐久服务器超节点支持 UALink 协议**，并通过 ODCC **AI Infra 方升开放项目**从硬件架构适配，未来将全面兼容通过测试验证服务的 AI 芯片、Switch 与其他互连部件 — 来源: 同上
- **物理层演进路线确认（ODCC 原文）**: UALink 物理层技术从 **112G → 224G → 448G** 演进；UALink 有望成为**以推理为主的 AI 时代 Scale Up 互连主流选择**（阿里云视角判断）— 来源: 同上
- **UALink 2.0 新闻稿 PDF 二次抓取复核（2026-08-19）**: 四规范细节（Common 2.0 在网计算 / 200G DL-PL 2.0 拆分 / Manageability 1.0 / Chiplet 1.0 兼容 UCIe 3.0）、董事会 12 家名单、互操作性与合规项目计划与 08-18 收录**逐项一致**——官方底稿复核通过，UALink 侧信息完整性确认 — 来源: https://ualinkconsortium.org/wp-content/uploads/2026/04/UALink-2.0-Specification-PR_FINAL.pdf
- **Bing 中文生态新信号（2026-08-19 检索）**: CSDN《UALink 200 Rev 1.0 Specification》中文版全文翻译（08-18 发布）+ 腾讯新闻《UALink，能否一战？》（2025-12-27）+ CSDN「深度解析 AI 互联技术：NVLink/InfiniBand/UALink 与 Ultra Ethernet」（2026-08-12）——中文技术社区对 UALink 200G 规范消化热度持续，规范技术细节进入中文工程实践语境 — 来源: https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026
- **Hot Interconnects 今日开幕（8/19-21 虚拟）**: 上届（2025-08-25）convergedigest「UALink for Rack-Scale AI Interconnects」议题索引确认；本届关注 UALink 学术论文/演讲是否出现（官网 Blog 静默第 21 天，若 UALink 有议程将打破）— 来源: https://ualinkconsortium.org/news/
- **跨组去重核验（tech 组 8/19）**: tech 组收录超节点"双轨格局"宏观分析（NVIDIA NVL72 闭源 vs AMD Helios/UALink/OCP 开放路线、物理约束重定义机架、Dell 主权 AI）——与本组 UALink/ODCC 标准本体细节**无条目级重复**，宏观格局见 tech 组（已由 tech 组收录）

**2026-08-19 源状态**: Baidu ❌（安全验证，连续第13日）· ODCC ❌（30s 超时，连续第3日）· Bing ✅（UALink 200 中文翻译/UALink 2.0 四规范/腾讯新闻命中）· UALink官网 Press Room ✅（全量条目+链接提取）· UALink 2.0 新闻稿 PDF ✅（复核一致）· ODCC 微信原文 ✅（wechat-fetch 全文 4089 字）

> 📌 **判断**: ① ODCC 微信原文是本轮最大增量——中国 UALink 生态从"名单确认"（08-14）到"机制细节"（分层验证/异常注入/招标认证定位），**国际（互操作合规项目）+ 国内（ODCC 测试认证）双轨认证体系完整入库**；② 阿里云磐久超节点 + 方升开放项目 = 中国超节点标准落地的具体载体，与 tech 组宏观"双轨"分析互补；③ Hot Interconnects 开幕为下轮唯一核心窗口，官网 Blog 静默 21 天是观察点。

### 2.17 今日快照（2026-08-20 — Hot Interconnects 第2天 🎯）

> **背景**: 官网快照第 16 日一致（置顶仍为 4/9 四规范/董事会/公司化，TASK 白皮书推广条在位），Blog 静默第 22 天（最新 7/29 FMS 预告，8 月零新帖）。**Hot Interconnects（8/19-21 虚拟）进行中第 2 天**，UALink 官网/STH/Press Room 三源均无会议参与或会后报道信号。本轮为静默确认轮，增量 = 三源无信号交叉确认 + 跨组去重核验 + 下一窗口倒计时。

- **UALink 官网快照第 16 日一致**（2026-08-20）: 置顶动态（四规范发布 / 阿里苹果 Synopsys 入董事会 / 公司化 / 200G 1.0 / Statements of Support / TASK 白皮书下载横幅）自 7/29 起无变化——开放标准组织"大事件驱动型"发布节奏延续，8 月官方淡季第 22 天 — 来源: https://ualinkconsortium.org/
- **UALink Blog 静默第 22 天确认**（2026-08-20 Blog 全量列表快照）: 最新帖仍为 7/29「Join the UALink Consortium at FMS 2026」，8 月零新帖；技术主题最近帖仍为 6/24 INC 深挖——Hot Interconnects 开幕 2 天未见 UALink 议程或会后总结帖，上届（2025-08-25 convergedigest 报道）曾有「UALink for Rack-Scale AI Interconnects」议题，本届无公开议程记录 — 来源: https://ualinkconsortium.org/blog/
- **UALink Press Room 无新条目确认**（2026-08-20 全量快照）: 最新 Press Release 仍为 2026-04-07 四规范发布（含 2.0 Statements of Support），"UALink in the News"最新为 5/4 EETimes；Member News 最新为 4/24 Netforward——Press Room 自 4 月以来无新增，组织发布活动完全停滞于 2.0 规范发布后节奏 — 来源: https://ualinkconsortium.org/news/
- **Hot Interconnects 官网抓取失败**（2026-08-20, 连接失败）: www.hotinterconnects.org 不可达；UALink 官网事件日历仍列 Hot Interconnects 8/19-21（虚拟）为 Upcoming Events 唯一临近事件，但 UALink 官网/Blog/STH/Bing 四源均无本届 UALink 论文/演讲信号——**本届 UALink 参与大概率无公开传播**，Hot Interconnects 线索倾向关闭（与 FMS/OCP APAC 同模式：会后静默） — 来源: https://ualinkconsortium.org/（Upcoming Industry Events）
- **STH UALink 搜索无新报道**（2026-08-20）: 最新 UALink 相关仍为 8/12 AMD MI455X Deep Dive（CDNA 5/Helios）；8/19 Cerebras CS-4 机架级系统（250 PFLOPS 稀疏 FP16）为机架级硬件动态，已由硬件组收录，本组不重复 — 来源: https://www.servethehome.com/?s=UALink
- **ODCC 官网连续第 4 日超时**（2026-08-20, 30s）: odcc.org.cn 直连持续不可用；中国侧 UALink 生态动态仍依赖微信文章（8/14/8/19 已收录 ODCC 测试验证服务全文）单点源——ODCC 官网源恢复价值高，下轮继续尝试移动端/镜像通道 — 来源: https://www.odcc.org.cn/
- **Baidu 安全验证拦截连续第 14 日**（2026-08-20）: 与既往一致；中文检索依赖 Bing/ocpasia/rgznrb 三源补位 — 来源: https://www.baidu.com/
- **Bing 检索无新信号**（2026-08-20，UALink Hot Interconnects 专项检索）: 结果集与既往一致（UALink 2.0 知乎解读 4/9 / CSDN 200G 中译 8/18 / UALink 联盟百科 / 官方白皮书 CH 版 / CSDN 深度对比文 8/12）——无 Hot Interconnects 相关 UALink 论文/演讲的任何报道命中 — 来源: https://www.bing.com/search?q=UALink+Hot+Interconnects+2026+paper+talk
- **跨组去重核验（tech 组 8/20）**: tech 组收录超节点机架级硬件（Cerebras CS-4/AMD MI455X Helios/NVIDIA NVL72 液冷整柜）+ 运维经济学（504 GPU 集群 55 天故障基线：top-3/63 节点集中 >50% 排除、checkpoint 加载达 NFS 带宽 21.5%、自动重试成功率 33.3%）+ 电网交互（Power-Flexible 130kW 集群）——均与本组 UALink/ODCC 标准本体**无条目级重复**，宏观格局与运维维度见 tech 组（已由 tech 组收录） — 来源: 本组核验
- **事件日历倒计时**: 🎯 **AI Infra Summit 9/15-17（Santa Clara）26 天后**——UALink 2025 年曾深度参与（2025-10-20 Blog「UALink Makes a Big Splash at AI Infra Summit 2025」），为本专题下一核心窗口；OCP Global Summit 残留条目仍为 2023 旧数据（未更新） — 来源: https://ualinkconsortium.org/

**2026-08-20 源状态**: Baidu ❌（安全验证，连续第14日）· ODCC ❌（30s 超时，连续第4日）· HotInterconnects官网 ❌（连接失败）· Bing ✅（专项检索无新信号）· UALink官网 ✅（快照第16日一致）· UALink Blog ✅（静默第22天）· UALink Press Room ✅（无新条目确认）· STH ✅（无 UALink 新报道）

> 📌 **判断**: ① **Hot Interconnects 线索倾向关闭**——开幕第 2 天，UALink 官网/Blog/Press Room/STH/Bing 五源零信号，延续 FMS（8/5 演讲后静默）与 OCP APAC（8/11-12 无现场记录）同模式，"展会静默"是本组织 2026 年的稳定行为模式；② 8 月官方淡季确认——Press Room 自 4 月零新增 + Blog 静默 22 天，UALink 组织发布节奏完全由"大事件"驱动（规范发布/董事会/公司化），下一大事件窗口为 **AI Infra Summit 9/15-17**（2025 年曾"Big Splash"）；③ 本专题近期实质增量全部来自第三方生态（ODCC 测试认证/国产芯片/学术侧）而非 UALink 官方，**跟踪重心应持续向中国生态与硅片落地侧倾斜**（楠菲微/瀚博/星拓/集益威 + ODCC 双轨认证）。

### 2.18 今日增量（2026-08-21 — Hot Interconnects 闭幕日 & ODCC 夏季全会全景 & 光学 Scale-Up 新维度 🎯）

> **背景**: 本轮核心增量 = ① **Hot Interconnects 33（8/19-21 虚拟）闭幕**——convergedigest（媒体伙伴）8/19-20 发布 6+ 篇密集报道，**推翻 8/20「线索倾向关闭」判断**：UALink 官方虽无议程信号，但光学 Scale-Up 标准（OCI MSA）与 NVIDIA Gigascale 架构（CPO 量产/NVLink 6/Fusion）在 HotI 系统性发声；② **ODCC 2026 夏季全会（6/24-26 景德镇）六大趋势全景**（Locsic 深析）——ODCC×UALink MOU + 六大 Scale-Up 协议路线竞赛；③ UALink 主席 Kurtis Bowman 访谈量化细节深读（[13] 补全）；④ Netforward 原型验证技术细节补全。

- **ODCC 2026 夏季全会六大趋势全景**（2026-06-24~26 景德镇；Locsic 深析 2026-07-04）: ① 供电：单机架>100kW 后 400V AC 达物理天花板，ODCC 设施 WG 明确 **800V DC 为主流方向**，OCP/ODCC ±400V HVDC sidecar 标准已完成，Meta/MSFT/Google/字节/腾讯下一代液冷机架全纳入 HVDC busbar；② 散热：xFusion 液冷产业促进组牵头**全机柜液冷标准化**（部件级→机架/设施级升维）；③ UEC 采用：华为 CloudEngine XH9000 获信通院**首个对齐 UEC 标准的国内测试证书**；④ Scale-Up：UALink 专设 Track、主席 Kurtis 亲临；⑤ 在网计算：华为提功能/性能/可靠性三维测试框架；⑥ Token 经济学：中国日 token 调用超 140 万亿（两年 1000x），网络设计从带宽/延迟转向 token 吞吐效率——功率密度 8 年 15-25x（2018 5-8kW → 2024 GB200 NVL72 120kW → 2026 讨论 200kW+） — 来源: https://locsic.com/thinking/odcc-2026-summer-overview/
- **ODCC × UALink 签署 MOU（2026-06 夏季全会）**: 跨组织协同 Scale-Up 互连协议标准；UALink 主席 Kurtis 将中国定位为「**最大收入中心之一**」，确认中国本地互操作测试合作（与 4/2 测试验证服务互证）——开放 Scale-Up 标准从「纸面规范」转向「工程验证」 — 来源: 同上
- **六大 Scale-Up 协议路线产业化竞赛**（ODCC 夏季全会口径）: UALink（+ODCC 互操作测试服务）/ 华为灵衢 2.0（Atlas 900 上 **300+ 套**大规模商用）/ 腾讯 ETH-X（全光互联）/ NVLink（NVIDIA 闭源）等六条路线加速竞赛；信通院郭亮（ODCC 新测 WG 主席）发布覆盖超节点全链系统报告——中国在 UALink 生态呈「标准参与者 + 最大收入中心」双角色，但 UEC/UALink 核心规范仍由西方主导，**标准制定权差距是结构性短板** — 来源: 同上
- **UALink 主席 Kurtis Bowman 访谈量化细节**（Converge Digest 2026-04-07 Q&A 深读，[13] 补全）: 在网计算（INC）对特定工作负载性能提升 **15-20%**；交换机目标 **256-512 通道**、双通道冗余下每交换机 **128-256 GPU**；混合 UALink/Ethernet 交换机硅面积多 **3-4 倍**（功耗代价，部分厂商走专用路线）；DL/PL 拆分后 PHY 可独立演进 **200G→400G→800G+ 无需软件变更**；完整生态（加速器+交换机+IP）预计 **2027 年**就绪；成员超 **100 家**；UALink=NVLink 开放等价物、基于 Ethernet PHY 但非包交换（原生 load/store + 原子操作） — 来源: https://convergedigest.com/qa-ualink-2-0-in-network-compute-and-the-future-of-open-ai-interconnects/
- **Hot Interconnects 33 主题 =「Scale-Up, Scale-Out, Scale-Across: Do they really differ?」**（8/19-21 虚拟）: convergedigest 媒体伙伴报道 6+ 篇——Meta Baldonado keynote（千兆瓦级 AI 舰队网络经验）/ NVIDIA Shainer keynote / Ciena Bilal Riaz（开放 AI 互联）/ Lightmatter BiDi DWDM / **OCI·Open CPX·SDM4·XPO 四大 MSA 专场** / Edge 数据中心面板——UALink 官方无议程，但 Scale-Up 标准生态（光学 MSA）在 HotI 系统性发声，**「展会静默」仅限 UALink 官方，非会议无内容**（修正 8/20 判断） — 来源: https://convergedigest.com/hot-interconnects-virtual-2026-scale-up-scale-out-scale-across/
- **OCI MSA 光学 Scale-Up 规范（HotI 8/20 发布，2026-03 由 AMD/Broadcom/Meta/MSFT/NVIDIA/OpenAI 成立）**: Gen1=200Gbps（**4×50G NRZ + DWDM + 双向单纤**）；目标 scale-up 从 in-rack 扩展到 **multi-rack & multi-row**，系统极限从电缆距离转向 **switch radix**；路线图 **Gen2 400G（2027）/ Gen3 800G（202x）**；电信号 400G 面临 PAM4/6/8 困境、800G 未解决——光学成为 400G+ scale-up 的候选路径；「We don't deploy innovation, we deploy products」（Alduino）；已向 OIF 提交 ELSFP 外形变更建议；避免跨厂商「forced marriages」专有依赖 — 来源: https://convergedigest.com/oci-msa-optical-scale-up-ai-clusters-outgrow-copper/
- **NVIDIA Gigascale 网络架构（HotI 8/20 Shainer keynote）**: Spectrum-X Ethernet Photonics **CPO 已量产**（microring modulator + TSMC COUPE；宣称光网络功耗 -5x、激光器 -4x、MTBI +10x vs 可插拔）；**光网络功耗接近 AI 系统计算功耗 10%**——光学本身成为固定电力包络内约束；**NVLink 6 = 每 GPU 3.6TB/s 全互联 + 130 TFLOPS 在网计算**（3x 低延迟/10x 高包率）；**NVLink Fusion** 开放第三方 XPU（chiplet + NVLink-C2C 接入 NVIDIA 机架）；Spectrum-XGS 跨数据中心 scale-across 性能近 2x；Spectrum-X 目标 ≥95% 有效带宽 — 来源: https://convergedigest.com/hot-interconnects-nvidia-gilad-shainer-gigascale-ai-factory-network-architecture/
- **Netforward（楠菲微）UALink 原型验证技术细节补全**（2026-04-24 官网全文；8/14 名单确认 → 本轮机制确认）: FPGA-VU19P×2 模拟 GPU + VP1902 作 UALink 交换芯片；Direct Connection（点对点 UALink 接口 IP，X2/X4 模式）与 Switched Networking（write/writefull/read/AtomicR/AtomicNR 全协议栈 + **24 小时持续验证**）两场景；将支持 UALink 2.0 **Link Resiliency 与 Link Folding**；超节点内 **100+ 加速器全互联**；集成在网计算 + 完整 RAS——UALink 从规范到工程实现的芯片级支撑 — 来源: https://www.netforward-tech.com/xinwenzhongxin/23.html
- **UALink 官网快照第 17 日一致**（2026-08-21）: 置顶仍为四规范/董事会/公司化/200G 1.0/TASK 白皮书；Press Room 自 4 月零新增（第 5 个月）；Blog 静默第 23 天——组织发布节奏完全「大事件驱动」，下一窗口 **AI Infra Summit 9/15-17（25 天后）** — 来源: https://ualinkconsortium.org/
- **跨组去重核验（tech/hardware 组 8/21）**: tech 组（MoE×硬件/云原生 AI/Qualcomm 模块化）与 hardware 组（电源架构/AMD Helios/MI350P/SK hynix CPO 路线图/硅光引擎）均**无 OCI MSA、HotI 2026 报道、NVIDIA CPO 量产、UALink 细节**条目——光学 scale-up 与 HotI 侧记为本科目独有增量；hardware 组 SK hynix CPO 路线图（内存供应商视角）与本组 NVIDIA CPO 量产（网络架构视角）互补，互不重复 — 来源: 本组核验

**2026-08-21 源状态**: Baidu ❌（安全验证，连续第15日）· ODCC ❌（30s 超时，连续第5日）· OCP ❌（403）· Bing ✅（UALink 2.0/ODCC 检索命中）· UALink官网/Press Room/规范页 ✅（快照第17日一致）· convergedigest ✅（Q&A 深读 + HotI 预告/OCI MSA/NVIDIA 3篇）· Locsic ✅（ODCC 夏季全会深析全文）· Netforward ✅（原型验证全文）

> 📌 **判断**: ① **Hot Interconnects 线索反转**——convergedigest 8/19-20 密集报道证明本届 HotI 是 Scale-Up 标准生态重要发声场（OCI/Open CPX/SDM4/XPO 四大 MSA + NVIDIA/Meta keynote），此前「五源零信号」仅说明 UALink 官方不参与，跟踪重心应从「UALink 官方议程」转向「convergedigest 等媒体伙伴会议侧记」；② **光学 Scale-Up 成为第三极**——Scale-Up 域标准从 UALink（铜/开放）× NVLink（铜/封闭）双极扩展为 + OCI MSA（光/开放，2027 Gen2 400G）三极，叠加中国灵衢/ETH-X 本地路线，与 ODCC「六大协议路线」图景互证——铜（7 米电域）与光（multi-rack/multi-row 光域）的分界线正在成为 scale-up 标准竞争的物理主轴；③ ODCC 夏季全会确立中国「标准参与者+最大收入中心」定位，但核心规范制定权仍由西方主导——**标准制定权差距是中国超节点生态结构性短板**，跟踪中国侧应聚焦测试认证落地（ODCC）与国产交换芯片（楠菲微/瀚博/星拓/集益威）而非规范起草。

### 2.19 今日增量（2026-08-22 — ODCC AI 存储实验室新源 & OCTC 官网首纳 & 夏季全会全文深读补全 🎯）

> **背景**: 本轮核心增量 = ① **新源 chaoqing-i.com（超擎数智）ODCC AI 存储实验室全文抓取**——ODCC 生态从「互联标准（UALink 测试认证）」「组织动态（夏季全会）」扩展到「存储标准」维度，且由同一人物（信通院郭亮）主导，超节点标准生态的中国组织版图进一步完整；② **OCTC 官网（octc.net）首次直接纳入**（此前仅经 ocpasia 转引 OCTS 2026）；③ **Locsic ODCC 夏季全会全文深读补全**（8/21 已收概要，本轮补齐器件级量化/耦合关系/结构性判断）；④ UALink 官网快照第 18 日一致，AI Infra Summit 倒计时 24 天。

- **ODCC AI 存储实验室成立详情**（2025-09 北京「2025 开放数据中心大会」成立）: 中国信通院主导，联合 **美团/NVIDIA/三星/Solidigm** 等产业链企业；使命 = 建立统一 **AI 存储评估规范与行业标准**，系统性解决「存力」瓶颈——ODCC 标准版图从互联（UALink 测试）扩展到存储评估维度 — 来源: https://www.chaoqing-i.com/odcc
- **三大核心技术方向 + 前沿探索**（ODCC AI 存储实验室）: **KV Cache 卸载 / 存算分离架构 / 高性能 SSD** 三大方向，并探索 **PD 分离（Prefill-Decode）与 DPU 网络处理/存储卸载**——与超节点 Scale-Up 内存语义（UALink 128PB 地址空间）构成「互联+存储」协同叙事 — 来源: 同上
- **首批 KV Cache 测试项目与验证环境**（ODCC AI 存储实验室）: 联合 **NVIDIA/超擎数智/焱融科技/大普微/XSKY/英韧科技/DaoCloud** 搭建跨厂商多元方案验证环境；基于 **NVIDIA Spectrum-X 高速网络（400G→1.6T）** 测试基础设施——存储标准从「纸面规范」进入「多厂商实测」阶段，与 UALink 测试验证服务同构 — 来源: 同上
- **已输出 4 份测试规范/报告**（ODCC AI 存储实验室，2026-08 时点）: ① **NVMe SSD RAID 性能测试技术报告**（联想）② **NVMe ZNS 测试规范**（大普微）③ **PCIe Gen5 SSD 应用报告**（三星）④ **FDP SSD 技术与应用报告**（三星）——存储评估标准率先落地，与超节点 OAM/HGX 板卡标准（Layer 2）形成配套 — 来源: 同上
- **超擎数智授牌合作单位**（2026-04-02 舟山 ODCC 春季全会）: 信通院云大所总工程师**郭亮**授牌「ODCC AI 存储实验室合作单位」，超擎为物理验证环境实际运营方（投入数千万设备）——**郭亮同时主导 UALink 测试验证服务与 AI 存储实验室**，中国信通院在超节点标准生态的枢纽角色确认（新测 WG 主席 + 存储实验室双线） — 来源: 同上
- **OCTC 官网首次直接纳入**（octc.net，2022 年成立）: 开放计算标准工作委员会聚焦 **计算/存储/网络/管理运维/数据中心基础设施** 五大领域，联合**最终用户/系统厂商/核心组件供应商/科研院校**建立先进技术标准——与 8/12 ocpasia 收录的 OCTS 2026（OCTC×OCP 联合大会）互证，OCTC 为 OCP 中国本土化组织主体 — 来源: https://www.octc.net
- **ODCC 夏季全会全文深读补全：正泰三级直流断路器矩阵量化**（Locsic 深析全文，2026-07-04）: 从 DCCB（传统直流专用）→ **SSHCB 混合式固态（100μs–10ms 响应）** → **SSCB 全固态（1μs–50μs 响应）** 三级演进——直流灭弧从器件到系统的工程解，800V DC 供电标准化的关键配套器件路线 — 来源: https://locsic.com/zh/thinking/odcc-2026-summer-overview/
- **ODCC 夏季全会全文深读补全：NPO 1024-lane 工程挑战 + 六方向耦合关系**（Locsic 深析全文）: 华为拆解 **1024-lane 超高密 NPO 交换机**工程挑战（连接器选型/物理尺寸/整机布局），NPO 进入真实工程验证阶段；六方向强耦合 = 供电↔散热（800V DC 触发液冷需求，风冷 COP 在 200kW/柜失效）· 网络↔供电（1024-lane NPO 供电需求或翻倍）· 超节点↔在网计算（域内内存语义 vs 域间以太网边界随 Scale-Up 域大小变化）· Token 经济学↔所有方向（统一度量）· UEC↔超节点（Scale-Out/Scale-Up 双层标准协同设计）——「标准需协同设计」成为系统级判断 — 来源: 同上
- **结构性判断：创新重心从芯片层下移到设施层**（Locsic 深析全文）: 「过去两年是'谁的 GPU 最强'，接下来两年可能是'谁的机房更高效'」——芯片性能逼近物理极限，系统效率（电网到芯片端到端能量转化）仍有巨大优化空间；谁率先跑通 800V DC/整机液冷/超节点互联/光互联的**标准化工程闭环**，谁掌握 AI 基础设施下一代定义权 — 来源: 同上
- **Locsic 超节点系列深度文章索引**（8/22 站内文章索引抓取，跟踪资源）: 「WAIC再观察：超节点的工程选择、技术兑现与企业决策」（7/22，企业采购超节点四条件：主力模型是否受通信瓶颈限制/能否承受百千瓦机柜/软件团队迁移能力/三年有效利用率）·「NVLink 的护城河与裂缝」（7/31，Scale-Up 七堵墙/内存语义五根柱子）·「灵衢协议深度分析」（5/30）·「超节点的心脏：灵衢服务层 8192 卡」（6/8）·「昇腾超节点架构跃迁」（5/25）·「AMD Helios 超节点拆解」（7/29）——灵衢/昇腾/Helios 三线深度拆解为后续 Scale-Up 竞品对照备用 — 来源: https://locsic.com/zh/thinking/
- **UALink 官网快照第 18 日一致 + AI Infra Summit 倒计时**（2026-08-22）: 置顶动态（四规范/董事会/公司化/200G 1.0/TASK 白皮书）无变化；**AI Infra Summit 9/15-17（Santa Clara）24 天后**——UALink 2025 年曾「Big Splash」，下轮核心窗口；OCP Global Summit 残留条目仍为 2023 旧数据 — 来源: https://ualinkconsortium.org/
- **跨组去重核验（hardware 组 8/22）**: hardware 组收录 AMD Pollara 400 UEC RDMA NIC（已出货）+ Vulcano 800G NIC（面向 UALink/UEC 规模扩展，产品视角）——与本组 UALink 标准本体/ODCC 生态**无条目级重复**，AMD 产品路线见 hardware 组（已由 hardware 组收录）；tech/market 组同日无超节点标准内容 — 来源: 本组核验

**2026-08-22 源状态**: Baidu ❌（web_search Zhipu key 失效 + 安全验证，连续第16日）· ODCC ❌（30s 超时，连续第6日）· Bing ✅（UALink/ODCC 双检索命中）· UALink官网 ✅（快照第18日一致 + AI Infra Summit 倒计时）· Locsic ✅（夏季全会全文 + 文章索引）· chaoqing-i ✅（ODCC AI 存储实验室全文，**新源**）· octc.net ✅（OCTC 官网，**新源**）

> 📌 **判断**: ① **ODCC 生态版图补全为「互联（UALink 测试认证）→ 存储（AI 存储实验室）→ 组织（夏季全会/OCTS/OAII）」三维结构**——信通院郭亮同时主导前两维，中国超节点标准生态的「组织枢纽+评测落地」双引擎格局清晰，跟踪应从「规范文本」转向「评测体系」（ClusterBench/AI 存储规范/UALink 测试三轨）；② **OCTC 官网（octc.net）纳入例行源**，与 ocpasia（OCP 中国区）、rgznrb（OAII）构成中国侧三源，弥补 Baidu/ODCC 双源长期不可用的缺口；③ Locsic 系列深度文章（灵衢/昇腾/Helios/NVLink 护城河）是 Scale-Up 竞品对照的现成底稿，下轮可选择性深读与 UALink 体系做三方对比；④ 8 月官方淡季延续（UALink Press Room 第 5 个月零新增），下一大事件窗口 = AI Infra Summit 9/15-17。

### 2.20 今日快照（2026-08-23 — 三线全静默确认 & 官方淡季判断强化 🔭）

> **背景**: 本轮为周期跟踪第 17 次。核心结论 = **UALink 官方三线（官网/Press Room/Blog）全静默确认**：官网快照第 19 日一致、Blog 静默第 25 天、Press Room 第 5 个月零新增——8 月官方淡季判断从「延续」强化为「结构性事实」。仅剩的活跃信号在**中文生态翻译热度**（CSDN 200G 中文版新帖）与**事件日历倒计时**（AI Infra Summit 9/15-17 仅 23 天）。Hot Interconnects（8/19-21）已闭幕且侧记已收录（v2.4），本轮会后总结源不可达，线索维持关闭。

- **UALink 官网快照第 19 日一致**（2026-08-23 抓取）: 置顶新闻仍为「四规范发布」（multi-workload 部署）、Recent Developments 五项（阿里/苹果/Synopsys 入董事会·公司化·发起人组·200G 1.0 发布·支持声明）无变化；TASK 白皮书下载位保留——**官方新闻面零新增第 19 天**，淡季判断强化 — 来源: https://ualinkconsortium.org/
- **UALink Blog 静默第 25 天（37 帖全量确认）**（2026-08-23 抓取）: 最新帖仍为 7/29「Join UALink at FMS 2026」（FMS 已闭幕 8/6，帖子成历史存档）；Blog 上一实质内容帖为 6/24 INC 深挖帖——**博客更新面静默 25 天**，事件驱动内容（INC/管理/Chiplet/互操作）均未发布新解读 — 来源: https://ualinkconsortium.org/blog/
- **AI Infra Summit 9/15-17 倒计时 23 天**（官网事件日历，2026-08-23）: UALink 官方参与页面仍仅列日期地点（Santa Clara, CA）；UALink 2025 年曾「Big Splash」（10/20 博客回顾帖），**9 月上旬议程发布期为下一观察窗口**；OCP Global Summit 10/12-17 条目年份仍残留 2023（官网数据维护异常，日期按 10/12-17 计） — 来源: https://ualinkconsortium.org/
- **ocpasia.org 快照：OCTS 2026 收官态确认**（2026-08-23 抓取）: 2026 开放计算技术大会（7/9 北京，OCP×OCTC 联合主办）官网仍为回顾态（大会简介/议程/直播回放/资料下载），无 8 月下旬新事件；Chris Petersen（UALink/CXL 董事）主论坛「灵活部署 XPU 开放机架架构」+ 孔阳（UALink 董事代表）Track4「UMX 统一内存存储扩展 Scale-Up」等 UALink 关联内容均停留在 7/9 快照——**OCP 中国区下一窗口 = OCTS 2027** — 来源: https://www.ocpasia.org/
- **Bing 中文生态信号：CSDN UALink_200Rev 中文版翻译新帖**（2026-08-23 Bing 检索命中，约 08-18 发布）: 「终于完成了《UALink_200Rev 1.0 Specification》的中文版」阅读 968 次，含信号定义/协议格式/编码规则翻译——与 8/12 收录的 jw915086731 中文版为**不同博主新帖**，国内工程界对 UALink 200G 实现关注度延续，与 ODCC UALink 测试验证服务（内测企业楠菲微/瀚博等）互证（⚠️ 帖子 URL Bing 未展示完整 ID，无法独立 curl 验证，仅作生态热度信号不单列引用） — 来源: https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026
- **跨组去重核验（hardware 组 8/23）**: hardware 组已收录**中诚华隆超节点智算集群**（爱集微 08-21，HL200 推理芯片+万卡集群，中标移动/电信）与 **arXiv PREFACE 预 FEC 纠错**（UALink 200G replay 语义，goodput +10.52%/P99 -50.75%）——均为产品/技术实现视角；**Cerebras CS-4 rack-scale 系统**（8/19 发布）自 8/20 起已由 hardware/tech/market 三组多日收录——本组标准/生态视角无条目级重复，仅交叉引用 — 来源: 本组核验

**2026-08-23 源状态**: Baidu ❌（安全验证，连续第17日）· ocpasia.org ✅（OCTS 2026 收官态，无新动态）· Bing ✅（UALink 官网更新信号→实为爬虫缓存，快照确认；CSDN 翻译新帖）· UALink官网 ✅（快照第19日一致）· UALinkBlog ✅（静默第25天，37帖全量）· STH ✅（Cerebras 已跨组收录，无新增）· ConvergeDigest ❌（403，Hot Interconnects 会后总结不可达）· UALink Industry Events 子页 ❌（404，以首页事件日历为准）

> 📌 **判断**: ① **「8 月官方淡季」从事件性判断升级为结构性事实**——UALink 官网/Press Room/Blog 三线自 7/29 起零新增，FMS（8/4-6）与 Hot Interconnects（8/19-21）两个窗口均未触发官方内容更新，标准组织内容节奏与展会解耦；② **跟踪策略建议调整为「隔日快照」**：三线静默期逐日快照边际收益递减，改为隔日检查直至 AI Infra Summit 议程发布（预计 9 月上旬）再恢复每日；③ **中文生态翻译热度是当前唯一活跃信号**（CSDN 双帖 200G 中文版+腾讯新闻+ODCC 测试服务），国内实现侧热度与官方静默形成反差——符合「规范已发布、工程在追赶」的生态阶段特征；④ 下一核心窗口 = AI Infra Summit 9/15-17（23 天后），其次 OCP Global Summit 10/12-17（50 天后）。

### 2.21 今日快照（2026-08-24 — 三线静默延续第4日 & 官方淡季结构性事实再确认 🔭）

> **背景**: 本轮为周期跟踪第 18 次。UALink 官方三线（官网/Press Room/Blog）静默延续第 4 轮：官网快照第 20 日一致、Blog 静默第 26 天、Press Room 第 5 个月（139 天）零新增——「8 月官方淡季」结构性事实再获确认。唯一活跃信号仍为事件日历倒计时（AI Infra Summit 9/15-17 仅 22 天）。跨组核验：hardware 组 PCIe 8.0 Draft 0.5 / ConnectX-8 SuperNIC 为开放互联标准家族（UALink 之外）进展，无条目级重复，仅交叉引用。

- **UALink 官网快照第 20 日一致**（2026-08-24 抓取）: 置顶新闻仍为「四规范发布」（multi-workload 部署）、Recent Developments 五项（阿里/苹果/Synopsys 入董事会·公司化·发起人组·200G 1.0 发布·支持声明）零变化；TASK 白皮书下载位保留——**官方新闻面零新增第 20 天** — 来源: https://ualinkconsortium.org/
- **UALink Blog 静默第 26 天（37 帖全量确认）**（2026-08-24 抓取）: 最新帖仍为 7/29「Join UALink at FMS 2026」（FMS 已闭幕 18 天，帖子成历史存档）；上一实质内容帖为 6/24 INC 深挖帖——**博客更新面静默 26 天**，事件驱动内容（INC/管理/Chiplet/互操作）均未发布新解读 — 来源: https://ualinkconsortium.org/blog/
- **UALink Press Room 第 5 个月零新增确认（139 天）**（2026-08-24 抓取）: Press Releases 最新仍为 4/7 2026（UALink 2.0 四规范 + 2.0 Statements of Support）；UALink in the News 最新 5/4 2026；Member News 最新 4/24（Netforward 原型验证，已收录 v1.8）——**新闻稿面静默 139 天，为三线中静默最久** — 来源: https://ualinkconsortium.org/news/
- **AI Infra Summit 9/15-17 倒计时 22 天**（官网事件日历，2026-08-24）: UALink 官方参与页仍仅列日期地点（Santa Clara, CA）；UALink 2025 年曾"Big Splash"（10/20 博客回顾帖），**9 月上旬议程发布期为下一观察窗口**；OCP Global Summit 10/12-17 条目年份仍残留 2023（官网数据维护异常，日期按 10/12-17 计） — 来源: https://ualinkconsortium.org/
- **ocpasia.org 快照：OCTS 2026 收官态延续**（2026-08-24 抓取）: 官网仍为 7/9 大会回顾态（议程/直播回放/资料下载），无 8 月下旬新事件；Track5 百度天池超节点/浪潮多模融合超节点/中国移动开放解构超节点等超节点主题议程已于 v1.7 收录——**OCP 中国区下一窗口 = OCTS 2027** — 来源: https://www.ocpasia.org/
- **Bing 检索无新信号（爬虫缓存干扰识别）**（2026-08-24 Bing 检索）: 命中以旧帖为主（CSDN fastboy_abc 5/19 NVLink/IB/UALink 对比文、ithome 2025-12 UALink 介绍）；官网条目"2 天之前"为爬虫缓存刷新（8/23 已识别同类干扰，快照确认内容未变）；UALink-1.0 中文白皮书 PDF（White_Paper_CH_v2）被索引但直链 URL 不完整，无法独立验证 — 来源: https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026
- **跨组去重核验（hardware/tech/market 组 8/24）**: hardware 组已收录 **PCIe 8.0 Draft 0.5**（64 GT/s/通道，为 Gen6 之后下一跳，STH）与 **ConnectX-8 SuperNIC**（PCIe Gen6 + 800G）——属开放互联标准家族（UALink 之外）的产品/实现视角，本组标准/生态视角无条目级重复，仅交叉引用；tech/market 组无本组视角冲突 — 来源: 本组核验

**2026-08-24 源状态**: Baidu ❌（安全验证，连续第18日）· UALink官网 ✅（快照第20日一致）· UALinkBlog ✅（静默第26天，37帖全量）· UALinkPressRoom ✅（139天零新增）· Bing ✅（无新信号）· ocpasia ✅（OCTS 2026 收官态延续）

> 📌 **判断**: ① **三线静默第 4 轮确认（官网 20 日 / Blog 26 天 / Press Room 139 天）**——「8 月官方淡季」已是结构性事实，标准组织内容节奏与展会（FMS 8/4-6、Hot Interconnects 8/19-21）完全解耦；② **跟踪节奏「隔日快照」建议维持**：距 AI Infra Summit 9/15-17 还有 22 天，**9 月上旬议程发布期为恢复每日快照的触发点**；③ **中文生态热度信号延续**（CSDN 200G 中文版双帖 + ODCC 测试验证服务）与官方静默反差保持——「规范已发布、工程在追赶」的生态阶段特征不变；④ 下一核心窗口 = AI Infra Summit 9/15-17（22 天后），其次 OCP Global Summit 10/12-17（49 天后）。

### 2.22 今日增量（2026-08-25 — IEEE 802.3 E4AI 新源首纳 & UALink 1.0 DL/PL 层技术细节补全 🎯）

> **背景**: 本轮为周期跟踪第 19 次。UALink 官方三线（官网/Press Room/Blog）静默延续第 5 轮：官网快照第 21 日一致、Blog 静默第 27 天、Press Room 第 5 个月（约 140 天）零新增。本轮核心增量来自 **Bing 命中的 IEEE 802.3 E4AI ad hoc 材料**（新源首次纳入）——UALink DL/PL TWG 联合主席在 IEEE 802.3 以太网 AI（E4AI）研究组的官方演示，首次补齐 UALink 1.0 的 **DL/PL 层技术参数**（此前只收录了 1024 加速器/200GT/s 等概要），并实证 **UALink 与以太网 PHY 生态的深度绑定**。跨组核验：tech 组今日收录为机柜/产品视角（Vera CPU/Cerebras CS-4/8×GB10/Monaka），hardware 组为 PCIe/ConnectX 产品视角，均与本组标准层细节无条目级重复。

- **IEEE 802.3 E4AI ad hoc 新源首纳**（2026-06-24 演示，2026-08-25 抓取）: UALink DL/PL Technical Working Group 联合主席 Dave Brown（AMD）+ Kent Lusted（Synopsys）在 IEEE 802.3 Ethernet for AI 研究组分享《UALink 200G 1.0 Specification Overview: DL & PL》（22 页 PDF）；材料明确 **UALink PL 基于 IEEE P802.3dj / 802.3 物理层规范**（200GBASE-KR1/CR1、400GBASE-KR2/CR2、800GBASE-KR4/CR4 + 100/200/400G 变体，仅做 680B FLIT 对齐微调）——**开放标准生态位实证：UALink 借力以太网 PHY 成熟生态，创新集中在 DL/TL/协议层**（初版协议以 AMD Infinity Fabric 为种子，注入 Promoter 部署经验）— 来源: https://www.ieee802.org/3/ad_hoc/E4AI/public/25_0624/lusted_e4ai_01_250624.pdf（HTTP 200 验证）📎 raw: tmp/raw/2026-08-25/ieee802.org-lusted-e4ai-ualink-dl-pl.pdf
- **UALink 1.0 DL 层量化参数补全**（同上材料）: 640B FLIT（Flit Hdr 3B + Segment Hdr 5B + CRC 4B）→ 有效载荷 628B，**链路效率 628/640 = 98.125%**；FEC codeword 680B；**212.5 GHz 信令速率**覆盖 FEC 开销（较 200G 数据率上浮 6.25%）— 来源: 同上（IEEE 802.3 E4AI PDF）
- **UALink TL 面积与打包机制**（同上材料）: TL 将请求/响应打包进同一 FLIT（多目的地可并包），减少延迟与面积——**TL 轻量实现仅 ~0.3 sqmm @ N3 工艺**；支持 256B 细粒度内存通道交错，最大化本地/对端 GPU 内存带宽；load/store/atomic 语义 + 软件一致性 — 来源: 同上（IEEE 802.3 E4AI PDF）
- **低延迟 FEC 交错模式（量化）**（同上材料）: 相比 IEEE 802.3 默认 FEC 交错，UALink 200G 1.0 提供低延迟模式——**400GBASE-KR2/CR2 2-way：RX 延迟 1 FEC symbol（默认 69）**；200GBASE-KR1/CR1 1-way/2-way：**RX 延迟 1 FEC symbol（默认 137）**；TX 路径无两 codeword 延迟——FEC 延迟削减 98%+ 为 RTT <1µs 目标服务 — 来源: 同上（IEEE 802.3 E4AI PDF）
- **机架尺度路由指引（UALink vs UEC 边界）**（同上材料）: **1-2 racks 用 UALink、3-4 racks UALink 或 UEC、>4 racks 用 UEC**——官方首次给出 scale-up/scale-out 边界量化（对照：以太网路线 1-2 racks UALink、3-4 racks UALink 或 Ethernet、>4 racks Ethernet）；性能目标：cable <4m、Req-To-Resp RTT <1µs、endpoints ≤1K、单层交换（switch plane 随带宽扩展）— 来源: 同上（IEEE 802.3 E4AI PDF）
- **虚拟 POD 隔离机制**（同上材料）: POD 可配置为多个虚拟 POD，**错误恢复隔离在 Virtual POD 内（Port/Station Reset）**，互不影响；但**内部交换错误影响整个 POD，需应用重启**——RAS 边界设计的官方口径（对超节点故障域规划有直接参考价值）— 来源: 同上（IEEE 802.3 E4AI PDF）
- **UALink 1.0 白皮书官方中文版 PDF 确认**（2026-08-25 抓取）: `UALink-1.0-White_Paper_CH.pdf`（2025-08 上传，343KB，HTTP 200）——官方首次提供中文版白皮书（此前仅英文 200G 1.0 白皮书）；Bing 索引摘要：物理通道支持多种宽度组合（最高 4x 单通道 x1 Link、2x 双通道 x2 Link、1x 四通道链路）——**中文生态信号从媒体翻译（CSDN）升级为官方材料供给** — 来源: https://ualinkconsortium.org/wp-content/uploads/2025/08/UALink-1.0-White_Paper_CH.pdf（HTTP 200 验证）
- **UALink 官网快照第 21 日一致 + Blog 静默第 27 天**（2026-08-25 抓取）: 置顶「四规范发布」+ Recent Developments 五项零变化；Blog 最新帖仍为 7/29 FMS 预告（37 帖全量确认）；Press Room 最新仍 4/7（约 140 天零新增）——**三线静默第 5 轮确认**；Bing 官网条目「1 天前」为爬虫缓存刷新（与 8/23、8/24 同类干扰，快照内容未变）— 来源: https://ualinkconsortium.org/ | https://ualinkconsortium.org/blog/
- **AI Infra Summit 9/15-17 倒计时 21 天**（官网事件日历，2026-08-25）: 9 月上旬议程发布期为下一观察窗口（UALink 2025 年该峰会曾「Big Splash」，10/20 博客回顾）；OCP Global Summit 10/12-17 条目年份残留 2023 bug 未修复 — 来源: https://ualinkconsortium.org/
- **Bing 检索补充验证**（2026-08-25）: 命中 CSDN fastboy_abc「深度解析 AI 互联技术：NVLink/IB/UALink/Ultra Ethernet」（2026-05-19）直链 521 反爬无法验证 → 按 URL 真实性规则不收录；zhihu/baike/Synopsys 等旧帖已收录，无新信号 — 来源: https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026

**2026-08-25 源状态**: Baidu ❌（安全验证，连续第19日）· ODCC ❌（官网 30s 超时，连续第2次失败，标记恢复尝试）· Bing ✅（IEEE E4AI 新源命中）· UALink官网 ✅（快照第21日一致）· UALinkBlog ✅（静默第27天，37帖全量）· IEEE 802.3 E4AI ✅（新源首纳，HTTP 200）

> 📌 **判断**: ① **三线静默第 5 轮确认（官网 21 日 / Blog 27 天 / Press Room ~140 天）**——「8 月官方淡季」结构性事实延续，标准组织内容节奏与展会解耦；② **本轮唯一增量亮点 = IEEE 802.3 E4AI 材料**：UALink 在以太网标准组织（802.3）的官方技术曝光，实证其「**标准以太网 PHY 生态 + 自研 DL/TL/协议层**」的生态策略——与 Ultra Ethernet（UEC，scale-out）构成互补而非竞争（3-4 racks 边界明确），这对超节点标准全景（三层架构 §4）是重要补强证据；③ **中文生态热度从媒体层升级到官方层**（中文白皮书 PDF），「规范已发布、工程在追赶」阶段特征持续；④ 下一核心窗口 = AI Infra Summit 9/15-17（21 天后），**9 月上旬议程发布期为恢复每日快照触发点**；跟踪节奏建议维持隔日快照。

### 2.23 今日增量（2026-08-26 — 三线静默第6轮 & Press Room 媒体直链批量核验 🔭）

> **背景**: 本轮为周期跟踪第 20 次。UALink 官方三线（官网/Press Room/Blog）静默延续第 6 轮：官网快照第 22 日一致、Blog 静默第 28 天、Press Room 第 5 个月（约 141 天）零新增——「8 月官方淡季」结构性事实第 6 轮确认。本轮核心增量 = **Press Room 引用的媒体直链首次批量 curl 核验**（此前 2.17 节仅收录 4 条媒体线索无 URL，本轮从 Press Room HTML 提取全部 href 并逐条验证 HTTP 200，剔除 403/404/000 不可达条目），同时 **Locsic ODCC 2026 夏季全会全文深读交叉验证**（v2.4 已收录主题，本轮确认 UALink-ODCC 互操作测试合作与 MOU 细节一致）。跨组核验：hardware 组今日收录 Helios 机架（UALink 驱动 72-GPU 无阻塞互联，STH 8/3）为产品/硬件视角，本组标准/生态视角无条目级重复。

- **UALink 官网快照第 22 日一致**（2026-08-26 抓取）: 置顶新闻仍为「四规范发布」（multi-workload 部署）、Recent Developments 五项（阿里/苹果/Synopsys 入董事会·公司化·发起人组·200G 1.0 发布·支持声明）零变化；TASK 白皮书下载位保留；事件日历 AI Infra Summit（9/15-17, Santa Clara）在列——**官方新闻面零新增第 22 天** — 来源: https://ualinkconsortium.org/
- **UALink Blog 静默第 28 天（37 帖全量确认）**（2026-08-26 抓取）: 最新帖仍为 7/29「Join UALink at FMS 2026」（FMS 已闭幕 20 天）；上一实质内容帖为 6/24 INC 深挖帖——**博客更新面静默 28 天**，事件驱动内容（INC/管理/Chiplet/互操作）均无新解读 — 来源: https://ualinkconsortium.org/category/blog/
- **UALink Press Room 第 5 个月零新增确认（约 141 天）**（2026-08-26 抓取）: Press Releases 最新仍为 4/7 2026（UALink 2.0 四规范 + 2.0 Statements of Support）；UALink in the News 最新 5/4 2026（EE Times「AI Accelerator Spec Maintains Rapid Update Pace」）；Member News 最新 4/24（Netforward 原型验证）——**新闻稿面静默 141 天，为三线中静默最久** — 来源: https://ualinkconsortium.org/news/
- **Press Room 媒体直链首次批量核验：The Register UALink 2.0 直链 HTTP 200**（2026-04-07, curl 验证 2026-08-26）: 「No-Nvidia interconnect club delivers 2.0 spec before v1.0 silicon ships」——2.0 规范先于 v1.0 硅片出货的产业节奏信号直链确认（v2.1 仅主题无 URL，本轮补全） — 来源: https://www.theregister.com/2026/04/07/ualink_2_specs/
- **SDxCentral 新条目直链 HTTP 200**（2026-04-08, curl 验证 2026-08-26）: 「UALink Consortium takes another swing at Nvidia's NVLink supremacy with specification 2.0」——此前完全未收录的独立媒体条目，与 techstrong.ai（4/8）共同构成 UALink 2.0 媒体覆盖的「NVLink 对标」叙事线 — 来源: https://www.sdxcentral.com/news/ualink-consortium-takes-another-swing-at-nvidias-nvlink-supremacy-with-specification-20/
- **Tom's Hardware UALink 路线图分析直链 HTTP 200**（2026-02-20, curl 验证 2026-08-26）: 「UALink roadmap plots course to optimized AI data center interconnects」——开放标准对抗 vendor lock-in、成本/性能优化双论点的媒体侧详述（v2.17 线索补 URL） — 来源: https://www.tomshardware.com/tech-industry/artificial-intelligence/ualink-roadmap-plots-course-to-optimized-ai-data-center-interconnects-examining-the-open-standard-designed-to-combat-vendor-lock-in-while-offering-cost-and-performance-optimization
- **SemiEngineering 新条目直链 HTTP 200**（2025-11-13, curl 验证 2026-08-26）: 「Multiple AI Scale-Up Options Emerge」——Scale-Up 多路线并存格局的行业级综述（UALink/NVLink/光互连路线矩阵），为「scale-up 从双极到多极」判断的早期证据 — 来源: https://semiengineering.com/multiple-ai-scale-up-options-emerge/
- **Converge Digest Hot Interconnects UALink 条目直链 HTTP 200**（2025-08-25, curl 验证 2026-08-26）: 「Hot Interconnects: UALink for Rack-Scale AI Interconnects」——与 2026 年 8/19-21 HotI 33 呼应：UALink 连续两年在 HI 发声，rack-scale 主题一致 — 来源: https://convergedigest.com/hot-interconnects-ualink-for-rack-scale-ai-interconnects/
- **Lightmatter 加入 UALink 生态直链 HTTP 200**（2025-01-03, curl 验证 2026-08-26, thefastmode）: 光学互连厂商（photonic interconnect）入盟——与 HotI 2026 光学 Scale-Up 第三极（OCI MSA）叙事呼应，光互连在 UALink 生态的布局早于 2025 年即已启动（DCD 原链 403 不可达，以 fastmode 为验证源） — 来源: https://www.thefastmode.com/technology-solutions/38704-lightmatter-joins-ualink-consortium-to-revolutionize-ai-interconnect-standards
- **Locsic ODCC 2026 夏季全会全文交叉验证**（2026-07-04 文, 2026-08-26 复核）: 确认 UALink 董事会主席 Kurtis 亲临景德镇 UALink Track 专场 + ODCC×UALink MOU + 中国本地互操作测试合作三事一致（与 v2.4 收录内容互证无出入）；补充细节：中国信通院郭亮（ODCC 新测组组长）主导《AI 计算节点发展研究报告》体系化覆盖超节点全链路、华为 CloudEngine XH9000 获国内首个对标 UEC 标准测评证书——中国在 UALink 生态「标准参与者+最大收入中心」双角色定位延续 — 来源: https://locsic.com/zh/thinking/odcc-2026-summer-overview/
- **AI Infra Summit 9/15-17 倒计时 20 天**（官网事件日历，2026-08-26）: UALink 官方参与页仍仅列日期地点；UALink 2025 年曾「Big Splash」（10/20 博客回顾帖），**9 月上旬议程发布期为恢复每日快照触发点**；OCP Global Summit 10/12-17 条目年份仍残留 2023（官网数据维护 bug 未修复） — 来源: https://ualinkconsortium.org/
- **跨组去重核验（hardware 组 8/26）**: hardware 组已收录 **AMD Helios 机架互联规模**（STH 8/3：scale-up 260TB/s / scale-out 43TB/s，UALink 驱动 72-GPU 无阻塞互联成为 rackscale 基线）——为硬件/产品视角，本组标准/生态视角无条目级重复，仅交叉引用；tech 组（K8s DRA/Gateway AI/MoE 硬件变异性）与 market 组（Vera Rubin NVL72 效率度量）均无本组视角冲突 — 来源: 本组核验
- **ODCC 官网连续第 3 次超时（30s）**（2026-08-26）: 官网直连持续不可达，中国侧信息依赖 Locsic 深析/微信/ocpasia 三替代源——ODCC 官网恢复尝试维持低频标记，不影响本专题信息完整性 — 来源: 抓取记录

**2026-08-26 源状态**: Baidu ❌（安全验证，连续第20日）· ODCC ❌（官网 30s 超时，连续第3次）· Bing ✅（UALink 官网「15小时前」=Press Room 爬虫缓存干扰识别，快照确认内容未变）· UALink官网 ✅（快照第22日一致）· UALinkBlog ✅（静默第28天，37帖全量）· UALinkPressRoom ✅（141天零新增 + **媒体直链批量核验 6 条 200**）· Locsic ✅（全文交叉验证一致）· BusinessWire ❌（403，连续）· DCD/Lightwave/Astera ❌（403）· EE Times/Network World ❌（000 连接失败）· Auradine ❌（404）

> 📌 **判断**: ① **三线静默第 6 轮确认（官网 22 日 / Blog 28 天 / Press Room ~141 天）**——「8 月官方淡季」结构性事实延续，标准组织内容节奏与展会（FMS/HotI 均已闭幕）完全解耦；② **本轮增量 = Press Room 媒体直链首次批量核验**：8 条媒体条目中 6 条 HTTP 200 验证通过（The Register/SDxCentral/Tom's Hardware/SemiEngineering/Converge Digest/fastmode），剔除 4 条不可达（EE Times/Network World 连接失败、DCD/Lightwave/Astera 403、Auradine 404）——**媒体覆盖图从「线索」升级为「可引用直链」**，UALink 2.0 的 NVLink 对标叙事（The Register/SDxCentral/TechStrong 三线并行）与 roadmap/vendor-lock-in 论据（Tom's）可作标准竞争叙事引用；③ **Lightmatter（光互连）2025-01 已入盟** + SemiEngineering「Multiple AI Scale-Up Options」（2025-11）构成「scale-up 多极竞争」的早期证据链，与 HotI 2026 光学第三极判断互证；④ 下一核心窗口 = AI Infra Summit 9/15-17（20 天），**9 月上旬议程发布期为恢复每日快照触发点**；跟踪节奏维持隔日快照。

### 2.24 今日增量（2026-08-27 — 东兴证券超节点全景首纳 & Baidu 移动端复活 🎯）

> **背景**: 本轮为周期跟踪第 21 次。官方三线静默延续第 7 轮：官网快照第 23 日一致、Blog 静默第 29 天、Press Room 约 142 天零新增——「8 月官方淡季」结构性事实第 7 轮确认（Bing 检索中官网条目标注「1 天前」为爬虫缓存干扰，快照核对内容未变）。本轮核心增量 = **东兴证券《超节点与 Scale-up 网络》研报全文首纳**（智通财经 2026-03-03，URL 已验证 HTTP 200）：首次以卖方研究视角量化四家头部厂商（英伟达/华为/谷歌/AMD）超节点标准与技术路线全景，其中 **UALink 2027 生态突破预测**（与 Kurtis 访谈「完整生态 2027 就绪」互证）、**工信部牵头 CLink 国内统一标准**、**华为 Atlas 950 放弃全光互联改铜光混合** 为本专题此前未收录的重要信号；同时 **Baidu 移动端在连续 21 日拦截后复活**（m.baidu.com 移动端 UA 成功），中文生态检索通道恢复。跨组核验：hardware/tech/market 三组 8/27 均无东兴研报内容（hardware 组 Helios 为产品视角、tech 组 Vera Rubin 为架构视角、market 组为市场视角），无条目级重复。

- **东兴证券研报: UALink 产业阶段判断「标准制定→产品落地，2027 生态突破」**（2026-03-03, 智通财经, URL 已验证 200）: 研报认为 UALink「正处于从标准制定阶段走向产品落地阶段，预计生态将在 2027 年迎来突破发展，被众多数据中心接纳」；**UALink 联盟成员截止 2026-01 底超 100 家**——与 Kurtis Bowman 访谈（Converge Digest 4/7「完整生态 2027 就绪」）双向互证，开放 Scale-Up 标准进入产品化兑现期 — 来源: https://news.qq.com/rain/a/20260303A02W8C00
- **东兴证券研报: 华为灵衢协议 2.0 起转开放 + 工信部牵头 CLink 统一国内 Scale-Up 标准**（2026-03-03）: 国内 Scale-Up 协议呈多元竞争格局——华为灵衢（2.0 起转向开放标准）、中移 OISA、腾讯 ETH-X、高通量以太网 ETH+、中兴 OLink；**工信部正牵头推动 CLink 协议，旨在形成统一国内标准**——中国 Scale-Up 标准「开放组织（UALink/OCP）+ 本土组织（CLink/OISA/ETH-X）双轨」格局的官方政策层面确认 — 来源: 同上
- **东兴证券研报: 华为 Atlas 950 超节点 2026Q4 发布，8 EFLOPS(FP8) 对标 NVL144 2.52 EFLOPS**（2026-03-03）: 内存容量 **1152TB**、互联带宽 **16.3PB/s** 大幅领先；关键架构变化：**不再使用全光互联架构**，改为「柜内正交铜互联 + 柜间光互联」混合设计（铜保可靠/低成本/低功耗，光保可扩展），显示华为超节点在标准化阶段 TCO 权衡修正——与 OCP/UALink 阵营「铜+光分层」路线趋同 — 来源: 同上
- **东兴证券研报: 英伟达超节点路线图量化**（2026-03-03）: 2025 年 GB200/300 NVL72 出货约 **2800 台**（大摩预测）；2026-27 计划 Vera Rubin NVL144 → **Rubin Ultra NVL576**（互联 GPU 72→576 颗）；新一代 **Kyber 机架引入 NVLink Switch Blade（NVLink 交换机刀片）**，通过 PCB 中板替代传统 5000+ 根有源铜缆——封闭生态内部也在做「铜缆→背板」的工程重构，与开放阵营 OAM/OCP baseboard 思路同源 — 来源: 同上
- **东兴证券研报: 谷歌 OCS 光互联超节点技术壁垒**（2026-03-03）: 全球首个将光电路交换机（OCS）大规模商用部署于 Scale-Up 网络（Palomar MEMS 微反射镜核心）；2026 年 Anthropic 将直接从博通采购近 **100 万颗 TPU v7 Ironwood** 本地部署；2027 第 8 代 TPU 对标 Vera Rubin——光互联路线（vs 电交换）构成与英伟达的不对称竞争，为 OCI MSA/光 Scale-Up 第三极判断提供商业侧证据 — 来源: 同上
- **UALink 官网快照第 23 日一致**（2026-08-27 抓取）: 置顶新闻「四规范发布」+ Recent Developments 五项（阿里/苹果/Synopsys 入董事会·公司化·发起人组·200G 1.0·支持声明）零变化；TASK 白皮书下载位保留；事件日历 AI Infra Summit（9/15-17）在列——**官方新闻面零新增第 23 天**；Bing 检索标注「1 天前」经快照核对为爬虫缓存干扰（与 v2.8 判断一致） — 来源: https://ualinkconsortium.org/
- **Baidu 移动端复活（连续 21 日拦截后首次成功）**（2026-08-27）: m.baidu.com 移动端 UA 检索「超节点标准 UALink OAM 液冷」成功返回中文生态信号（腾讯新闻 AMD 研报/中国日报 Kurtis 演讲/知乎阿里云 OAII 演讲/维科号三雄争霸等），桌面端仍被安全验证拦截——**中文生态检索通道恢复，Baidu 源从「持续拦截」降级为「移动端可用」** — 来源: https://m.baidu.com/s?word=超节点标准%20UALink%20OAM%20液冷%20开放标准%202026
- **ocpasia OCTS 2026 完整议程新细节: 字节跳动「XPU 模组标准化接口设计」**（2026-07-09 大会, 2026-08-27 快照）: Track4 开放系统设计论坛，字节郁雷/STE 孙国新演讲「XPU 模组标准化接口设计」——继 OAM/OCP GPU baseboard 之后，**XPU 模组标准化**成为中国超节点生态新议题（与 UALink/CXL 生态协同）— 来源: https://www.ocpasia.org/
- **ocpasia OCTS 2026 主论坛细节: Chris Petersen 演讲主题确认**（2026-07-09）: UALink/CXL 董事会成员 Petersen（Astera Labs）主论坛演讲「灵活部署 XPU：面向最大推理性能与最低 Token 成本的开放机架架构」——开放机架架构与「每 Token 成本」度量挂钩，与 market 组「每瓦 token 成新度量」判断同向 — 来源: https://www.ocpasia.org/
- **ODCC 官网连续第 4 次超时（30s）**（2026-08-27）: 官网直连持续不可达，中国侧信息仍依赖 Locsic 深析/微信/ocpasia 三替代源——恢复尝试维持低频标记 — 来源: 抓取记录
- **AI Infra Summit 9/15-17 倒计时 19 天**（官网事件日历, 2026-08-27）: UALink 官方参与页仍仅列日期地点；OCP Global Summit 10/12-17 条目年份仍残留 2023（官网维护 bug 未修复，连续第 2 轮确认）— 来源: https://ualinkconsortium.org/
- **跨组去重核验（8/27 三组）**: hardware 组（Helios 72-GPU 产品细节/ConnectX-8 SuperNIC）、tech 组（Vera Rubin 100MW AI 工厂架构）、market 组（Maia 200 市场分层采购）——东兴研报的超节点标准/生态全景（Atlas 950/CLink/TPU v7 采购/Kyber 背板）三组均未收录，无条目级重复，仅 Helios 一处与 hardware 组交叉引用 — 来源: 本组核验

**2026-08-27 源状态**: Baidu ❌（桌面端安全验证）→ ✅ **移动端复活（m.baidu.com 成功）**· ODCC ❌（官网 30s 超时，连续第4次）· Bing ✅（UALink 关键词检索约 5600 结果，官网「1 天前」=爬虫缓存干扰）· UALink官网 ✅（快照第23日一致）· ocpasia ✅（OCTS 2026 收官态 + 完整议程新细节）· 腾讯新闻 ✅（东兴研报全文，URL 验证 200）· web_search ❌（Zhipu key 失效，延续）

> 📌 **判断**: ① **三线静默第 7 轮确认（官网 23 日 / Blog 29 天 / Press Room ~142 天）**——「8 月官方淡季」结构性事实延续，下一恢复触发点仍是 AI Infra Summit（19 天）议程发布期；② **东兴证券研报 = 本轮最大增量**：UALink「2027 生态突破」预测获得卖方研究独立印证（标准→产品落地阶段切换）；**工信部牵头 CLink** 将中国 Scale-Up 标准从「多协议竞争」推向「政策收敛」；华为 Atlas 950 放弃全光改铜光混合，与开放阵营「铜+光分层」路线趋同——**中国超节点标准生态进入「开放组织（UALink/OCP）+ 本土收敛（CLink/OISA/ETH-X）+ 私有生态（NVLink/灵衢）」三层竞争格局确认**；③ **Baidu 移动端复活**恢复中文生态信号通道（本次命中腾讯研报/中国日报/知乎/维科号 4 类信源），后续跟踪可纳入「Baidu 移动端」为常驻源；④ 跟踪节奏维持隔日快照，重点观察 9 月上旬 OAII/AI Infra Summit 议程发布。

### 2.25 今日快照（2026-08-28 — 三线静默第8轮 & Blog 静默满30天里程碑 🔭）

> **背景**: 本轮为周期跟踪第 22 次。UALink 官方三线（官网/Press Room/Blog）静默延续第 8 轮：官网快照第 24 日一致、**Blog 静默满 30 天（月度级里程碑）**、Press Room 约 143 天零新增——「8 月官方淡季」结构性事实第 8 轮确认（Bing 检索中官网条目「2 天之前」为爬虫缓存干扰，快照核对内容未变）。本轮为纯静默确认轮，唯一弱信号 = Synopsys UALink IP 页 4 天前（8/24 前后）更新（IP 生态活跃度，页面主体未变）。跨组核验：tech 组 8/28「超节点标准」小节为宏观落地视角，与本组标准本体细节无条目级重复。

- **UALink 官网快照第 24 日一致**（2026-08-28 抓取）: 置顶新闻「四规范发布」（multi-workload 部署）+ Recent Developments 五项（阿里/苹果/Synopsys 入董事会·公司化·发起人组·200G 1.0·支持声明）零变化；TASK 白皮书下载位保留；事件日历 AI Infra Summit（9/15-17, Santa Clara）在列——**官方新闻面零新增第 24 天** — 来源: https://ualinkconsortium.org/
- **UALink Blog 静默满 30 天（37 帖全量确认）**（2026-08-28 抓取）: 最新帖仍为 7/29「Join UALink at FMS 2026」（FMS 已闭幕 22 天）；上一实质内容帖为 6/24 INC 深挖帖；**2026 年 8 月零新帖**——博客更新面静默达「月度级」里程碑，事件驱动内容（INC/管理/Chiplet/互操作）均无新解读 — 来源: https://ualinkconsortium.org/blog/
- **UALink Press Room 第 5 个月零新增确认（约 143 天）**（2026-08-28 抓取）: Press Releases 最新仍为 4/7 2026（四规范 + 2.0 Statements of Support）；UALink in the News 最新 5/4 2026（EETimes）；Member News 最新 4/24（Netforward 原型验证）——**新闻稿面静默 143 天，为三线中静默最久** — 来源: https://ualinkconsortium.org/news/
- **Bing 检索弱信号：Synopsys UALink IP Solution 页面「4 天前」更新**（2026-08-28 Bing 检索）: 「Consisting of controller, PHY, security and verification IP, the complete UALink IP solution is engineered for data-intensive AI…」——Synopsys IP 页微更新（8/5 #6 已收录该页主体），无新功能声明；UALink 2.0 知乎解读/CSDN 对比文/阿里云 2024 文等命中均与既往一致——**IP 生态持续活跃但无实质新信号** — 来源: https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026 | https://www.synopsys.com/designware-ip/interface-ip/ualink.html
- **AI Infra Summit 9/15-17 倒计时 18 天**（官网事件日历, 2026-08-28）: UALink 官方参与页仍仅列日期地点；UALink 2025 年曾「Big Splash」（10/20 博客回顾帖），**9 月上旬议程发布期为恢复每日快照触发点**；OCP Global Summit 10/12-17 条目年份仍残留 2023（官网维护 bug 未修复，连续第 3 轮确认） — 来源: https://ualinkconsortium.org/
- **跨组去重核验（tech 组 8/28）**: tech 组「超节点标准」小节收录宏观落地视角——STH 站内「supernode OAM OCP GPU baseboard」无结果、OCP 官网 403 反爬、NVL72/GB300 机柜生态扩展（ASRock VR NVL72 + Delta 150kW CDU）、分析判断「标准滞后于商业形态/机柜=超节点/开放标准可复用度下降」——与本组 UALink 标准本体（规范/董事会/测试认证）细节**无条目级重复**，tech 组宏观判断见 tech/2026-08-28.md（已由 tech 组收录） — 来源: 本组核验
- **ODCC 官网连续第 5 次超时（30s）**（2026-08-28）: 官网直连持续不可达，中国侧信息仍依赖 Locsic 深析/微信/ocpasia 三替代源——恢复尝试维持低频标记 — 来源: 抓取记录

**2026-08-28 源状态**: Baidu ❌（安全验证，连续第22日）· OCP ❌（403，延续）· ODCC ❌（30s 超时，连续第5次）· Bing ✅（UALink 关键词检索，Synopsys IP 页「4天前」弱信号）· UALink官网 ✅（快照第24日一致）· UALinkBlog ✅（静默第30天，37帖全量）· UALinkPressRoom ✅（约143天零新增）

> 📌 **判断**: ① **三线静默第 8 轮确认（官网 24 日 / Blog 30 天 / Press Room ~143 天）**——Blog 静默满 30 天达「月度级」里程碑，「8 月官方淡季」结构性事实延续，组织内容节奏与展会（FMS/HotI 均已闭幕）完全解耦；② **9 月上旬 AI Infra Summit 议程发布仍是唯一恢复触发点**（18 天倒计时）——UALink 2025 年该峰会曾「Big Splash」（10/20 回顾帖），若 2026 年延续参与模式，议程发布将首次打破月度静默；③ 中国侧跟踪重心（ODCC 测试认证/国产交换芯片/CLink 政策收敛）维持，与官方静默形成「外热内静」反差——「规范已发布、工程在追赶」阶段特征持续；④ 跟踪节奏维持隔日快照，重点观察 9 月上旬议程发布。

## 3. 交叉关联（知识库既有归档）

| 关联主题 | 内容 | 所在文件 |
|:---------|:-----|:---------|
| UALink 2.0 规范体系深度解读 | Common 2.0/在网计算/Chiplet/管理性 + 董事会扩容 | [`2026-07-29.md §7`](2026-07-29.md) |
| UALink 7/30 Webinar 完成 | Technical Deep Dive 首次技术披露（公开材料待放） | [`2026-07-30.md §7`](2026-07-30.md) |
| HGX B300 OAM baseboard OEM | ASRock Rack 4U16X-GNR2 最新实现 | [`2026-07-30.md §7`](2026-07-30.md) |
| OCP ORv3/48VDC busbar/1OU2N | 机架级开放架构标准 | [`2026-07-31-hardware.md §7`](2026-07-31.md) |
| NVIDIA DGX 对照 | Vera Rubin NVL72 量产爬坡、SOCAMM BOM 29% 压力减配 | [`2026-07-29.md §6`](2026-07-29.md) |

## 4. 标准全景三层架构

```
+-------------------------------------------------+
| Layer 3: Rack-scale 机架架构                     |
|   OCP ORv3 / 48VDC busbar / 1OU2N / NVL72       |
+-------------------------------------------------+
| Layer 2: GPU Baseboard 板卡标准                  |
|   OCP OAM / NVIDIA HGX (B300) / 液冷接口        |
+-------------------------------------------------+
| Layer 1: Scale-up 互联                           |
|   UALink 1.0/2.0 (开放) vs NVLink (封闭)        |
+-------------------------------------------------+
开放阵营 (UALink+OCP) 正向三层贯通演进，NVIDIA 以 DGX/NVL 垂直整合对抗
```

## 5. 下一步跟踪

- [x] 🎯 **UALink FMS 演讲现场结果**（8/5 已举行）— 5 天后官网 Blog/STH 均无会后总结，判定信息增益≈0，关闭跟踪
- [x] UALink Blog 子页面纳入例行抓取（7/15 帖已深读：115+ 会员/Ethernet 基础/1024 Pod）
- [x] 🎯 **OCP APAC Summit (8/11-12 台北)** — 会后官网/STH 无 UALink 现场记录，**台北线索正式关闭**（8/14 判定）
- [x] **UALink Press Room (/news/) 纳入例行抓取**（8/14 首轮全量：四规范详情/6 规范下载/Member News 14 条）
- [x] 🎯 **Hot Interconnects (8/19-21, 虚拟)** — 8/20 曾判「线索倾向关闭」；8/21 闭幕日经 convergedigest 侧记反转：本届实为 Scale-Up 标准生态重要发声场（OCI/Open CPX/SDM4/XPO 四大 MSA + NVIDIA/Meta keynote 6+ 篇报道），**「展会静默」仅限 UALink 官方**，会议侧记已收录，线索关闭
- [ ] 🆕 **OCI MSA 光学 Scale-Up 跟踪**（8/21 首纳）：Gen2 400G 2027 / Gen3 800G 202x；与 UALink（铜）竞争分界线、OIF ELSFP 提案进展、中国厂商是否加入——光学 scale-up 第三极
- [x] **ODCC 2026 夏季全会六大趋势追读**（8/21 首纳 → 8/22 全文深读完成）：800V DC 三级断路器量化/整机液冷/NPO 1024-lane/在网计算三维测试框架/Token 经济学/耦合关系——Locsic 全文已入库
- [ ] 🆕 **ODCC AI 存储实验室跟踪**（8/22 首纳）：KV Cache 卸载/存算分离/高性能 SSD 三方向；4 份测试规范原文下载（ZNS/RAID/PCIe Gen5/FDP）；与 UALink 内存语义协同——存储标准维度
- [ ] 🆕 **OCTC 官网纳入例行源**（8/22 首纳）：octc.net 与 ocpasia、rgznrb 构成中国侧三源；OCTS 2027 议程窗口
- [ ] 🆕 **Locsic 超节点系列深度文章选择性深读**（8/22 索引）：灵衢协议/灵衢服务层/昇腾超节点/AMD Helios/NVLink 护城河——Scale-Up 竞品三方对比底稿
- [ ] 🆕 **AI Infra Summit (9/15-17, Santa Clara)** — 下一核心窗口（18 天后，8/28 快照）；UALink 2025 年曾"Big Splash"，**预计 9 月上旬议程发布，届时恢复每日快照**
- [ ] 🆕 **跟踪节奏调整：UALink 三线静默期改「隔日快照」**（8/23 判定，8/24 第4轮续确认）——官网/Press Room/Blog 三线静默第 20/139 天+，逐日快照边际收益递减；AI Infra Summit 议程发布前按隔日执行
- [x] **Hot Interconnects 会后总结获取**（8/23 尝试 Converge Digest 403 不可达）——会议侧记已于 8/21 收录（v2.4），线索维持关闭，不再追
- [ ] 🆕 **OAII/GCC 社区深挖**（8/16 首纳）：Open AI Infra Summit 六大论坛细节、ClusterBench β版下载、AIDC 基础设施规范原文、双零行动——中国开放标准第二轨从"组织概览"走向"规范原文"
- [ ] 🆕 **OCTS 2026 vs OAII Summit 标准体系对比**：GW-Scale 框架报告（OCP 侧）vs AIDC 基础设施规范（OAII 侧）——中国超节点标准"双轨"格局的系统化梳理
- [ ] **UALink 2.0 规范公开文本下载**（Common 2.0 等 6 份已确认可下载）— 下载原文校验 TASK 白皮书量化数据（93% 效率/128PB 地址空间/6 信用环）
- [ ] UALink 官方中文白皮书（White_Paper_CH_v2）— 从官网 Resource Library 核实下载路径（Bing 索引存在，直链 404）
- [ ] **中国 UALink 芯片生态深挖**：楠菲微（交换芯片原型）/瀚博/星拓/集益威（IP 内测）——国产交换芯片进度是本专题新维度
- [ ] TASK Consultancy 白皮书（16 页）— 引用为 UALink 技术底稿
- [ ] UALink Blog 6/24 INC 深挖帖细读（INC 技术主题）
- [ ] STH AMD Helios 深度解析直链补全（rack-scale 对标参考）

---

## 参考文献

[1] UALink Consortium 官网 — https://ualinkconsortium.org/
[2] Synopsys UALink IP Solution — https://www.synopsys.com/designware-ip/interface-ip/ualink.html
[3] UALink 2.0 规范解读 (知乎) — https://zhuanlan.zhihu.com
[4] UALink 联盟 (百度百科) — https://baike.baidu.com/item/UALink联盟
[5] UALink Blog: Join the UALink Consortium at FMS 2026 (2026-07-29) — https://ualinkconsortium.org/blog/join-the-ualink-consortium-at-fms-2026/
[6] UALink Blog 列表 — https://ualinkconsortium.org/blog/
[7] ServeTheHome UALink 搜索 — https://www.servethehome.com/?s=UALink
[8] UALink Blog: Building Open, Scalable AI Infrastructure with UALink (2026-07-15) — https://ualinkconsortium.org/blog/building-open-scalable-ai-infrastructure-with-ualink-1532/
[9] UALink Blog: Exploring In-Network Compute (2026-06-24) — https://ualinkconsortium.org/blog/exploring-in-network-compute-how-ualink-is-redefining-ai-scale-up-architecture-1509/
[10] 人工智能日报网/IT时代网: 2026 Open AI Infra Summit 收官报道 (2026-04-27) — https://www.rgznrb.com/yunjisuan/5622.html
[11] CSDN: UALink 200G 1.0 Specification 中文版全文翻译 (2026-08-12 前后) — https://blog.csdn.net/jw915086731/article/details/155225567
[12] ODCC UALink 测试验证服务发布 (阿里云基础设施公众号, 2026-04-02) — https://mp.weixin.qq.com/s/jrq9_i8H5HMIxT3HixK8gg
[13] Converge Digest: Q&A: UALink 2.0, In-Network Compute, and the Future of Open AI Interconnects (2026-04-07) — https://convergedigest.com/qa-ualink-2-0-in-network-compute-and-the-future-of-open-ai-interconnects/
[14] TechStrong AI: UALink 2.0 Targets NVIDIA's Grip on AI Interconnects (2026-04-08) — https://techstrong.ai/features/ualink-2-0-targets-nvidias-grip-on-ai-interconnects/
[15] Locsic: The Infrastructure Generation Gap — AI Data Centers at ODCC 2026 (2026-07-04) — https://locsic.com/thinking/odcc-2026-summer-overview/
[16] Converge Digest: Hot Interconnects Goes Virtual Aug. 19–21 (2026-08-18) — https://convergedigest.com/hot-interconnects-virtual-2026-scale-up-scale-out-scale-across/
[17] Converge Digest: OCI MSA Targets Optical Scale-Up as AI Clusters Outgrow Copper (2026-08-20) — https://convergedigest.com/oci-msa-optical-scale-up-ai-clusters-outgrow-copper/
[18] Converge Digest: NVIDIA's Gilad Shainer Maps AI Network Architecture (2026-08-20) — https://convergedigest.com/hot-interconnects-nvidia-gilad-shainer-gigascale-ai-factory-network-architecture/
[19] Netforward: World's First UALink Switch/IP Product Design and Prototype Verification (2026-04-24) — https://www.netforward-tech.com/xinwenzhongxin/23.html
[20] 超擎数智: ODCC AI 存储实验室 (2026-08 访问) — https://www.chaoqing-i.com/odcc
[21] OCTC 开放计算标准工作委员会官网 — https://www.octc.net
[22] Locsic: ODCC 2026 夏季全会深析（/zh/ 路径确认）— https://locsic.com/zh/thinking/odcc-2026-summer-overview/
[23] OCP 中国区官网（OCTS 2026 大会回顾）— https://www.ocpasia.org/
[24] Bing 检索（UALink OCP OAM 超节点 2026）— https://www.bing.com/search?q=UALink+OCP+OAM+open+standard+supernode+2026
[25] ServeTheHome UALink 检索 — https://www.servethehome.com/?s=UALink
[26] The Register: UALink 2.0 specs (2026-04-07, HTTP 200) — https://www.theregister.com/2026/04/07/ualink_2_specs/
[27] SDxCentral: UALink takes another swing at NVLink (2026-04-08, HTTP 200) — https://www.sdxcentral.com/news/ualink-consortium-takes-another-swing-at-nvidias-nvlink-supremacy-with-specification-20/
[28] Tom's Hardware: UALink roadmap (2026-02-20, HTTP 200) — https://www.tomshardware.com/tech-industry/artificial-intelligence/ualink-roadmap-plots-course-to-optimized-ai-data-center-interconnects-examining-the-open-standard-designed-to-combat-vendor-lock-in-while-offering-cost-and-performance-optimization
[29] SemiEngineering: Multiple AI Scale-Up Options Emerge (2025-11-13, HTTP 200) — https://semiengineering.com/multiple-ai-scale-up-options-emerge/
[30] Converge Digest: Hot Interconnects UALink Rack-Scale (2025-08-25, HTTP 200) — https://convergedigest.com/hot-interconnects-ualink-for-rack-scale-ai-interconnects/
[31] The Fast Mode: Lightmatter joins UALink (2025-01-03, HTTP 200) — https://www.thefastmode.com/technology-solutions/38704-lightmatter-joins-ualink-consortium-to-revolutionize-ai-interconnect-standards

---

## 变更记录

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-28 | v3.1 | 周期跟踪第22次 — **三线静默第8轮确认 & Blog 静默满30天月度级里程碑**：官网快照第24日一致（置顶五动态零变化）+ Blog 静默满30天（37帖全量，2026-08 零新帖）+ Press Room 约143天零新增（Press Releases 4/7、in the News 5/4、Member News 4/24）——「8月官方淡季」结构性事实第8轮确认；Bing 弱信号 = Synopsys UALink IP 页「4天前」微更新（8/24 前后，无新功能声明，IP 生态活跃度）；AI Infra Summit 9/15-17 倒计时 18 天（9 月上旬议程发布为恢复触发点）；OCP Global Summit 残留 2023 bug 第3轮确认；ODCC 官网连续第5次超时；跨组去重核验（tech 组 8/28「超节点标准」宏观落地视角无条目级重复，仅交叉引用）；增量7条(164-170)；累计170条发现 |
| 2026-08-27 | v3.0 | 周期跟踪第21次 — **东兴证券超节点全景研报首纳 & Baidu 移动端复活**：官方三线静默第7轮确认（官网快照第23日一致/Blog 29天/Press Room ~142天，Bing「1天前」=爬虫缓存干扰）；核心增量 = 东兴证券《超节点与 Scale-up 网络》研报全文（智通财经 2026-03-03，URL curl 验证 HTTP 200）——UALink「2027 生态突破」预测（与 Kurtis 访谈互证）、联盟成员超 100 家（2026-01 底）、工信部牵头 CLink 统一国内 Scale-Up 标准（灵衢 2.0 开放化/OISA/ETH-X/ETH+/OLink 多元竞争）、华为 Atlas 950 2026Q4 发布 8 EFLOPS(FP8)/1152TB/16.3PB/s 且放弃全光改「柜内铜+柜间光」混合、英伟达 Kyber NVLink Switch Blade PCB 中板替代 5000+ 有源铜缆 + NVL576、谷歌 OCS Palomar/Anthropic 100 万颗 TPU v7——中国超节点标准生态「开放组织+本土收敛+私有生态」三层竞争格局确认；Baidu 移动端（m.baidu.com）连续 21 日拦截后复活，中文生态信号通道恢复（命中腾讯/中国日报/知乎/维科号）；ocpasia OCTS 2026 完整议程新细节（字节「XPU 模组标准化接口设计」、Petersen「灵活部署 XPU」演讲主题）；ODCC 官网连续第 4 次超时；跨组去重核验（三组 8/27 均无东兴内容，仅 Helios 交叉引用）；增量12条(152-163)；累计163条发现 |
| 2026-08-26 | v2.9 | 周期跟踪第20次 — **三线静默第6轮确认 & Press Room 媒体直链首次批量核验**：官网快照第22日一致 + Blog 静默第28天（37帖全量）+ Press Room 约141天零新增——「8月官方淡季」结构性事实第6轮确认；核心增量 = Press Room HTML 提取全部媒体 href 逐条 curl 验证（6 条 HTTP 200：The Register UALink 2.0「2.0先于1.0硅片出货」/SDxCentral「takes another swing」/Tom's Hardware roadmap「vendor lock-in」/SemiEngineering「Multiple AI Scale-Up Options」/Converge Digest「HotI Rack-Scale」/fastmode「Lightmatter 入盟 2025-01」——媒体覆盖从「线索」升级「可引用直链」；剔除 4 条不可达：EE Times/Network World 000、DCD/Lightwave/Astera 403、Auradine 404）；Locsic ODCC 夏季全会全文交叉验证一致（Kurtis 亲临/MOU/互操作测试互证 + 郭亮《AI 计算节点发展研究报告》细节补充）；Lightmatter 2025-01 入盟 + SemiEngineering 2025-11 综述构成「scale-up 多极竞争」早期证据链；跨组去重核验（hardware 组 Helios 72-GPU 产品视角，无重复）；ODCC 官网连续第3次超时；AI Infra Summit 倒计时 20 天；增量12条(140-151)；累计151条发现 | 周期跟踪第19次 — **IEEE 802.3 E4AI 新源首纳 & UALink 1.0 DL/PL 层技术细节补全**：Bing 命中 IEEE 802.3 Ethernet for AI 研究组材料（lusted_e4ai_01_250624.pdf，UALink DL/PL TWG 联合主席 AMD+Synopsys 官方演示，HTTP 200 验证，raw 已落盘）——首次补齐 DL/PL 层量化参数：640B FLIT 效率 98.125%（628/640，212.5GHz 覆盖 FEC）、TL ~0.3 sqmm @ N3、低延迟 FEC 交错（400G 2-way 1 vs 69、200G 1 vs 137 FEC symbol）、机架尺度路由（1-2 racks UALink / 3-4 UALink or UEC / >4 UEC）、虚拟 POD 隔离机制、PL 复用 P802.3dj 全速率族（生态位实证：标准以太网 PHY + 自研 DL/TL）；UALink 1.0 官方中文白皮书 PDF 确认（中文生态从媒体层升级官方层）；官网快照第21日一致 + Blog 静默第27天 + Press Room ~140天（三线静默第5轮）；Baidu 连续第19日拦截；ODCC 连续第2次超时；跨组去重核验（tech 组机柜/产品视角无重复）；增量10条(130-139)；累计139条发现 | 周期跟踪第18次 — **三线静默延续第4轮（官网20日/Blog26天/Press Room 139天）**：官网快照第20日一致（置顶五动态零变化）+ Blog 静默第26天（37帖全量确认，最新仍为 7/29 FMS 预告）+ Press Room 第5个月零新增确认（Press Releases 最新 4/7、in the News 5/4、Member News 4/24——三线中静默最久）；AI Infra Summit 9/15-17 倒计时 22 天（9 月上旬议程发布期为下窗口）；ocpasia 收官态延续（天池/多模融合/开放解构超节点已于 v1.7 收录，去重确认）；Bing 无新信号（官网"2天前"=爬虫缓存干扰识别，旧帖为主）；Baidu 连续第18日拦截；跨组去重核验（hardware 组 PCIe 8.0 Draft 0.5/ConnectX-8 SuperNIC 属 UALink 之外互联家族，仅交叉引用）；「隔日快照」节奏第4轮续确认；增量6条(124-129)；累计129条发现 |
| 2026-08-23 | v2.6 | 周期跟踪第17次 — **UALink 三线全静默确认 & 官方淡季判断升级为结构性事实**：官网快照第19日一致（置顶五动态无变化）+ Blog 静默第25天（37帖全量确认，最新仍为 7/29 FMS 预告）+ Press Room 第5个月零新增——FMS 与 Hot Interconnects 双窗口均未触发官方内容更新；AI Infra Summit 9/15-17 倒计时 23 天（9 月上旬议程发布期为下窗口）；ocpasia 快照确认 OCTS 2026 收官态（下一窗口 OCTS 2027）；Bing 中文生态热度信号（CSDN UALink_200Rev 中文版新帖约 08-18，URL 无法验证不单列）；Hot Interconnects 会后总结获取失败（Converge Digest 403，线索关闭）；跨组去重核验（hardware 组中诚华隆/arXiv PREFACE/Cerebras 均无本组视角重复）；跟踪策略建议改隔日快照；增量6条(118-123)；累计123条发现 |
| 2026-08-22 | v2.5 | 周期跟踪第16次 — **ODCC AI 存储实验室新源 + OCTC 官网首纳 + 夏季全会全文深读补全**：chaoqing-i（超擎数智）全文（2025-09 成立、信通院主导+美团/NVIDIA/三星/Solidigm、KV Cache 卸载/存算分离/高性能 SSD 三方向、首批 8 厂 KV Cache 测试、4 份测试规范输出、郭亮授牌合作单位）；OCTC 官网首次直接纳入（2022 成立、五大领域）；Locsic 夏季全会全文深读补全（正泰三级断路器 DCCB→SSHCB 100μs-10ms→SSCB 1μs-50μs、NPO 1024-lane 工程挑战、六方向耦合关系、创新重心下移结构性判断）；Locsic 超节点系列深度文章索引；UALink 官网快照第18日一致 + AI Infra Summit 9/15-17 倒计时 24 天；跨组去重核验（hardware 组 AMD Pollara/Vulcano 产品视角无重复）；增量11条(107-117)；累计117条发现 |
| 2026-08-19 | v2.2 | 周期跟踪第13次 — **ODCC 测试验证服务微信原文全文深读**（阿里云公众号 4089 字：发布人郭亮/王伟、分层验证 TL-DL-PL 机制、异常注入、招标认证定位、Kurtis 视频致辞、内测企业 IP 层确认、磐久超节点+方升项目、112G→224G→448G 演进）；UALink 2.0 新闻稿 PDF 二次抓取复核一致；Bing 中文生态新信号（CSDN 200G 中文版/腾讯新闻）；Hot Interconnects 今日开幕；跨组去重核验（tech 组宏观双轨 vs 本组标准细节无重复）；增量10条(77-86)；累计86条发现 |
| 2026-08-18 | v2.1 | 周期跟踪第12次 — **UALink 2.0 官方材料全文深读**：4 份规范细节（Common 2.0 在网计算/200G DL/PL 拆分/Manageability 1.0 gNMI-Yang-SAI-Redfish/Chiplet 1.0 UCIe 3.0 兼容）、董事会 12 家完整名单、互操作性与合规项目计划新信号、2.0 Statements of Support 全文（AMD/Astera/Google/Synopsys/UnifabriX）；产业信号"2.0 先于 v1.0 硅片出货"（The Register）；媒体线索补全 4 条；OCP-UALink 协同框架确认；官网快照第15日一致、Hot Interconnects 明日开幕；增量8条(69-76)；累计76条发现 |
| 2026-08-17 | v2.0 | 周期跟踪第11次 — **Hot Interconnects 前夜静默轮**：官网快照第14日一致、Blog 静默第19天（37帖全量列表确认）、Hot Interconnects 8/19-21 倒计时2天（核心窗口）；ODCC 官网首次纳入失败（30s 超时，标记恢复尝试）；Baidu 连续第11日拦截；Bing 无新信号（CSDN 对比文 URL 无法验证不收录）；增量6条(63-68)；累计68条发现 |
| 2026-08-16 | v1.9 | 周期跟踪第10次 — **新源 OAII/GCC 维度纳入**：Open AI Infra Summit 收官报道（rgznrb 全文，六大论坛：高速互联 128/256 卡规模化·超节点生态 DPU/QLC/CXL·ClusterBench β版发布·AIDC 基础设施规范·800V 200kW→500kW）；中国超节点标准生态"OCP/OCTC 国际组织本土化 + GCC/OAII 本土组织自主化"双轨格局确立；Baidu 源复活（移动端 UA）；Bing 命中 CSDN UALink 200G 全文中译；跨组去重 3 条（hardware/tech 8/15）；增量10条(53-62)；累计62条发现 |
| 2026-08-14 | v1.8 | 周期跟踪第9次 — **UALink Press Room 首次全量纳入**（四规范发布详情+6规范下载确认+Member News 14条）；中国生态落地实证：Netforward（楠菲微）世界首个 UALink Switch/IP 原型验证 + ODCC 测试验证服务（内测企业=楠菲微/瀚博/星拓/集益威）；Synopsys UALinkSec_200 安全模块；国内 CSDN 规范翻译热度信号；OCP APAC 台北线索关闭；增量10条(43-52)；累计52条发现 |
| 2026-08-12 | v1.7 | 周期跟踪第8次 — **新源 ocpasia.org（OCTS 2026）首次纳入**：UALink 董事 Petersen+阿里云董事代表孔阳同台、GW-Scale 开放智算中心框架报告 v1.0 发布、超节点主题议程密集；OCP APAC 会期确认；增量8条(35-42)；累计42条发现 |
| 2026-08-10 | v1.6 | 周期跟踪第7次 — **OCP APAC前夜**；UALink Blog 7/15帖深读（会员115+/基于Ethernet/1024加速器Pod/路线图INC·管理·Chiplet）；FMS演讲会后静默确认（关闭跟踪）；OCP APAC 8/11-12台北事件确认；增量7条(26-32)；累计32条发现 |
| 2026-08-06 | v1.5 | 周期跟踪第6次 — **FMS最后一天&UALink演讲日**；源发现UALink Blog子页面(7/29 FMS预告：Booth #725+演讲INC/管理/Chiplet+Cht with Experts)；STH Helios深度解析确认；增量6条(20-25)；累计25条发现 |
| 2026-08-04 | v1.3 | 周期跟踪第4次 — **FMS 2026开幕日**；增量4条(FMS规模3,500+/350+演讲者/20+流·厂商高管名单·使命·20周年品牌)；累计19条发现；FMS2026官方页源发现 |
| 2026-08-03 | v1.2 | 周期跟踪第3次 — 官网快照3日一致无新事件；Bing无新信号；增量=时间锚点(FMS明日开幕·OCP APAC 8天·Hot Interconnects 16天)+跟踪策略建议(FMS现场切换) |
| 2026-08-02 | v1.1 | 周期跟踪第2次 — 3源抓取(2失败1成功)+UALink官网快照；官网无新事件，增量5条(UALink 1.0参数/白皮书/2.0日期/成立时间线)；累计15条发现 |
| 2026-08-01 | v1.0 | 首次创建 — 3源抓取(2失败1成功)+源发现UALink官网；10条有效发现；事件日历5项 |
