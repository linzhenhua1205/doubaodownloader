# GitHub 知识类仓库全景调研：专题材料问答（2026-08）

> **类型**: 专题调研（开源资源全景盘点 + 知识库输入适配分析） | **日期**: 2026-08-18（v2.0-v6.0 补充 2026-08-22） | **版本**: v6.0
> **来源**: GitHub API 多轴检索（关键词×主题×语言，2026-08-18 批1-3 实测 46 组 + 2026-08-22 批4 通用 52 组 + 批5 领域定向 55 组 + 批6 基础学科 56 组 + 批7 高校课程 26 组 + 批8 哲学系统论方法论 42 组，api.github.com 直连 200）+ 经典仓库 core API 核录 + 本知识库既有沉淀（知识库本质篇 / 规模效益篇 / git-submodule-import 技能）
> **适用范围**: 知识库系统输入选型 / 开源资料导入决策 / 书单与学习资源盘点 / 芯片·服务器·硬件·AI·产品研发领域素材 / 基础学科（CS·数学·电子·半导体）素材 / 高校公开课资源 / 哲学·系统论·方法论元知识
> **核心命题**: GitHub 上"知识类仓库"按形态可 MECE 分为九类（电子书聚合/免费书籍清单/技术知识库/学习路径/PKM/AI知识库/知识图谱/面试题库/知识导航），不同形态对知识库系统的输入价值与导入方式完全不同——**清单类适合直接 submodule 导入，内容类适合批判加工后吸收，工具类只做链接参考**；v2.0 补充六大新形态（awesome 聚合/cheatsheet/文档手册/领域知识库/中文资源/资源聚合）；v3.0 按**业务领域轴**定向补充；v4.0 按**基础学科轴**补充；v5.0 按**高校公开课轴**补充；v6.0 按**元方法论轴**（哲学/系统论/方法论）补充
> **相关**: [git-submodule-import 技能](../../../skills/git-submodule-import/SKILL.md) · [知识库本质篇](../../03_AI/knowledge-system/2026-08-18-kb-essence-and-full-km-architecture.md) · [知识管理价值链](../18_methodology-framework/2026-08-05-knowledge-management-value-chain-deep-analysis.md) · [ebook-treasure-chest 元信息](../../../import/ebook-treasure-chest.info/README.md) · [补充素材区](../../../import/github-knowledge-survey-2026-08-22/README.md) · [组织能力补齐分析](./2026-08-22-fullstack-capability-gap-analysis.md)

---

## 📑 目录 (TOC)

- [§0 执行摘要](#§0-执行摘要)
- [§1 调研方法与规模](#§1-调研方法与规模)
- [§2 专题问答（Q1-Q10）](#§2-专题问答q1-q10)
  - [Q1 与 ebook-treasure-chest 直接同类的电子书聚合库有哪些？](#q1-与-ebook-treasure-chest-直接同类的电子书聚合库有哪些)
  - [Q2 有哪些高质量的免费书籍清单（体积小、适合直接导入）？](#q2-有哪些高质量的免费书籍清单体积小适合直接导入)
  - [Q3 哪些技术知识库/教程笔记可作知识输入？](#q3-哪些技术知识库教程笔记可作知识输入)
  - [Q4 学习路径/课程体系类有哪些？](#q4-学习路径课程体系类有哪些)
  - [Q5 个人知识管理（PKM/第二大脑）类有哪些值得关注？](#q5-个人知识管理pkm第二大脑类有哪些值得关注)
  - [Q6 AI 知识库/LLM 相关仓库有哪些？](#q6-ai-知识库llm-相关仓库有哪些)
  - [Q7 知识图谱相关有哪些？](#q7-知识图谱相关有哪些)
  - [Q8 面试题库类（知识测试形态）有哪些？](#q8-面试题库类知识测试形态有哪些)
  - [Q9 作为本知识库系统的输入，哪些优先导入（submodule）？](#q9-作为本知识库系统的输入哪些优先导入submodule)
  - [Q10 使用这些仓库有哪些合规/质量注意事项？](#q10-使用这些仓库有哪些合规质量注意事项)
- [§3 导入优先级建议](#§3-导入优先级建议)
- [§4 数据缺口与后续动作](#§4-数据缺口与后续动作)
- [§5 补充调研 v2.0（2026-08-22：52 组检索式 + 532 精选）](#§5-补充调研-v20-2026-08-2252-组检索式--532-精选)
- [§6 领域定向补充 v3.0（2026-08-22：芯片/服务器/硬件/AI/产品研发五轴）](#§6-领域定向补充-v30-2026-08-22芯片服务器硬件ai产品研发五轴)
- [§7 基础学科补充 v4.0（2026-08-22：CS/数学/电子/半导体四轴）](#§7-基础学科补充-v40-2026-08-22cs数学电子半导体四轴)
- [§8 高校公开课补充 v5.0（2026-08-22：国内外名校课程）](#§8-高校公开课补充-v50-2026-08-22国内外名校课程)
- [§9 元方法论补充 v6.0（2026-08-22：哲学/系统论/方法论）](#§9-元方法论补充-v60-2026-08-22哲学系统论方法论)
- [附录：完整仓库清单（353 个精选）](#附录完整仓库清单353-个精选)
- [参考资料](#参考资料)
- [素材边界声明](#素材边界声明)
- [Changelog](#changelog)

---

## §0 执行摘要

**GitHub 上知识类仓库已形成完整生态：从"电子书下载链接聚合"（ebook-treasure-chest 所属形态）到"免费书籍清单"、从"技术知识库"到"AI 知识库"，共九大形态。本次调研通过 GitHub API 三批 46 组检索式（英文关键词 × 中文关键词 × 主题轴 × 知名库确认），去重后得 421 个候选，精选 star≥400 的 353 个，按形态 MECE 分类整理** [来源: 本调研实测]。

**三个核心发现**：

1. **与 ebook-treasure-chest 直接同类的"电子书聚合库"有 76 个**——其中 kska32/ebooks（约 10 万本链接）、programthink/books、forthespada/CS-Books（1000+ 计算机经典书）是质量与体积最适配的导入候选 [来源: 本调研实测]。

2. **对知识库系统输入价值最高的是"免费书籍清单"类（10 个，多为 1-20MB 纯 md）**——EbookFoundation/free-programming-books（★394k）、justjavac/free-programming-books-zh_CN（★118k，1.1MB）、ruanyf/free-books（★16k，8.3MB）——体积小、纯文本、许可宽松，最适合 submodule 导入作为书目索引 [来源: 本调研实测]。

3. **九类形态的导入策略完全不同**：清单类 → 直接导入做索引；技术知识库类 → 体积大（CS-Notes 113MB / Python-100-Days 396MB），需评估后选择性导入或仅作链接；PKM/AI 工具类 → 只做链接参考（需要运行环境，非静态知识）；**绝不整库导入后直接当知识用——必须走 import/ 素材区批判加工（RULE.md §6）** [来源: 本文推导 + 知识库本质篇 §1.5]。

**v2.0 补充（2026-08-22）**：第二批 52 组检索式（awesome 聚合轴 × cheatsheet × 文档手册 × 领域知识库 × 中文资源 × 用户系列 × 资源聚合），合并去重后**总规模 722 个仓库（新增 609 个）**，精选补充 532 个（star≥800 非工具）。**三大补充发现**：

1. **awesome 聚合生态是最庞大的知识导航层**：`sindresorhus/awesome` 体系下按语言/领域细分的 awesome-* 清单（Node.js 66.6k/Flutter 61k/Rust 58.9k/Java 48.8k 等）构成"按主题找资源"的第一入口 [来源: 本调研实测]。
2. **cheatsheet/文档手册类是"工具型知识"的最佳载体**：tldr-pages（63.4k 协作速查表）/awesome-cheatsheets（46.4k）/OWASP CheatSheetSeries（32.9k）——体积小、结构规范，适合作为运维/安全场景的速查索引 [来源: 本调研实测]。
3. **中文社区学习资源（datawhalechina 系列 + 0voice 系列 + wx-chevalier 系列）构成独立的知识供给生态**：datawhalechina 已发布 20+ 门中文开源教程（hello-agents 74.1k/leedl-tutorial 16.7k/easy-rl 14.6k），0voice 覆盖 C/C++/嵌入式/Linux 等系统方向——**与本库服务器/AI 基础设施方向的培训素材需求高度匹配** [来源: 本调研实测]。

**v3.0 领域定向补充（2026-08-22）**：第三批 55 组领域检索式（芯片/服务器/硬件/AI/产品研发五轴），新增 1,150 个候选，文档型过滤 + 教学型保留后**精选 198 个**（AI 94/产品研发 34/硬件 20/芯片 19/服务器 6），合并后**全库 1,872 个仓库**。**三大领域发现**：

1. **芯片设计知识生态已成熟但分散**：tiny-gpu（12.9k，Verilog 学 GPU）/learn-fpga（3.6k，FPGA+yosys+RISC-V）/chisel-book（926，Chisel 数字设计教材）/rCore-Tutorial（2.1k，RISC-V OS）——**开源 ASIC/FPGA 学习链路（HDL→综合→验证）已闭环**，可作为芯片团队培训体系参考 [来源: 本调研实测]。
2. **BMC/服务器管理面有 OpenBMC 生态入口**：facebook/openbmc（OpenBMC 框架）+ facebookarchive/opencompute（OCP 社区）——**与 BMC 芯片/固件业务直接相关，建议纳入深度跟踪**（对应组织能力补齐主线：控制面纵深）[来源: 本调研实测]。
3. **AI 工程化知识（MLOps/LLM 工程/系统设计）是 AI 功底补齐的最佳输入**：ml-engineering 18.7k（ML 工程 Open Book）/ai-engineering-hub 37.1k（LLM/RAG 教程）/system-design-primer 365.3k——**与 08-22 组织能力分析"AI×推理/AI×RAS"嫁接点直接对应** [来源: 本调研实测]。

**v4.0 基础学科补充（2026-08-22）**：第四批 56 组检索式（CS/数学/电子/半导体四轴），新增 1,604 候选 → 文档型过滤 + 黑名单剔除 + 人工领域校准后**精选 90 个**（CS 39/数学 29/半导体 16/电子 6），合并后全库 **2,482 个**。**三大基础学科发现**：

1. **CS 全栈学习路径已闭环**：build-your-own-x（541.9k，造轮子大全）→ OSS University（208.3k，免费 CS 学位）→ dragon-book 习题（6.6k）→ xv6-riscv-book（942）——**直接服务「固件→驱动→kernel→OS」纵深补强** [来源: 本调研实测 + 本文推导]。
2. **数学是 AI 功底的地基**：mml-book（15.9k）+ 鸢尾花书系列（21k+）+ fastai NLA（11k）构成「数学→ML」完整路径——**建议加工入 03_AI 模块** [来源: 本调研实测 + 本文推导]。
3. **开源 EDA 生态已成型**：Yosys（4.7k）/OpenROAD（3k）/skywater-pdk（3.7k）——与 v3.0 芯片链路合并构成「逻辑设计→开源 EDA→流片验证」培训链路 [来源: 本调研实测 + 本文推导]。

**v5.0 高校公开课补充（2026-08-22）**：第五批 26 组检索式（MIT/Stanford/Berkeley/CMU/Harvard/ETH + 国内高校 + 课程聚合），新增 891 候选 → 课程关键词过滤 + 黑名单剔除 + 人工领域校准后**精选 84 个**（国外名校 48/国内高校 18/AI 课程 8/课程聚合 10）。**三大课程发现**：

1. **国外名校公开课是系统软件深度学习黄金素材**：MIT 6.824（分布式，多版本 3.3k+1.6k+2.8k）/MIT SICP 中文化（11.3k）/Stanford CS229/CS231n/CS224n 三件套——**建议 6.824+CS229 优先导入培训体系** [来源: 本调研实测 + 本文推导]。
2. **国内高校课程攻略是中文课程体系金矿**：浙大 40.9k/清华 37.4k/北大 33.9k/中科大 16.2k 课程攻略覆盖各校全课程——**注意部分含版权风险（试卷/教材扫描件），导入须筛选** [来源: 本调研实测 + 本文推导]。
3. **课程与书籍互补**：课程类（作业/Lab）适合实践训练，书籍类（体系化）适合系统学习——培训建议「书籍打底 + 课程实操」双轨 [来源: 本文推导]。

**v6.0 元方法论补充（2026-08-22）**：第六批 42 组检索式（哲学/系统论/方法论三轴）+ 经典仓库 core API 核录，新增 1,189 候选 → 严格领域过滤 + **人工精选**后**精选 28 个**（方法论 18/系统论 6/哲学 4），合并后全库 **3,690 个**。**三大元方法论发现**：

1. **方法论高杠杆输入**：awesome-falsehood（27.6k，程序员谬误清单）对应知识库「13 谬误自检」；danluu/post-mortems（12.3k）对应 RAS/故障诊断方法论——**外部验证源** [来源: 本调研实测 + 本文推导]。
2. **系统论工具稀缺但关键**：ncase/loopy（1.7k，系统因果回路可视化）是系统动力学经典；可结合知识库「五看三定」「复杂系统 function 框架」形成专题 [来源: 本调研实测 + 本文推导]。
3. **「方法论」关键词被 AI Skill 生态污染**：大量 Skill 仓库（毛选/文案/投资等）滥用方法论标签，实为 Prompt 模板——**方法论输入以经典书籍+学术资源为准，对 Skill 类保持警惕**（对应 import 素材批判使用原则）[来源: 本调研实测 + 本文推导]。

---

## §1 调研方法与规模

**方法**：GitHub Search API（`api.github.com/search/repositories`，直连 200 可用），三批 46 组检索式：

| 批次 | 检索轴 | 覆盖 |
|:-----|:-------|:-----|
| 批 1（16 组） | 英文关键词 | ebooks/free-ebooks/awesome-books/programming-books/knowledge-base/second-brain/pkm/notes 等 |
| 批 2（14 组） | 主题轴 + 中文 | topic:ebooks/topic:books/topic:awesome/中文电子书/中文书籍/读书笔记 等 |
| 批 3（16 组） | 知名库确认 + 补充轴 | OSSU/project-based-learning/system-design-primer/developer-roadmap/topic:cheatsheets 等 |
| 批 4（52 组，v2.0） | 补充轴 | awesome 聚合（topic:awesome×3 档）/cheatsheet×3/文档手册×4/领域知识库×15（devops/k8s/db/security/network/cloud-native/obs/ML/DL/LLM/RAG/agents/arch/proglang）/学习路径×5/中文资源×6/datawhalechina·0voice·wx-chevalier·ruanyf 用户系列×4/资源聚合×8/专项参考×2 |
| 批 5（55 组，v3.0） | 领域定向轴 | 芯片×12（chip/semiconductor/asic/fpga/soc/risc-v/verilog/vlsi/open-hardware/chisel/tapeout）/服务器×9（server/datacenter/ocp/bmc/redfish/rack/power-cooling）/硬件×12（hardware/embedded/electronics/pcb/kicad/iot/firmware/uefi/bootloader/rtos）/AI 基础设施×12（ai-infra/mlops/mlsys/gpu/inference/training/cuda/hpc/transformers/agents）/产品研发×10（product-mgmt/eng-mgmt/software-eng/system-design/architecture/tech-lead/ADR） |

**规模**：去重 421 个 → 精选 star≥400 的 353 个 → 按形态分类（脚本自动分类 + 人工校准）；**v2.0 批 4 补充 52 组后合并去重 722 个（新增 609 个），精选补充 532 个（star≥800 非工具）**；**v3.0 批 5 领域定向 55 组后新增 1,150 个候选，文档型过滤+教学型保留后精选 198 个，合并全库 1,872 个** [来源: 本调研实测]。

**分类分布**：

| 形态 | 数量 | 输入价值 | 导入方式 |
|:-----|:----:|:--------:|:---------|
| 电子书/书籍聚合 | 76 | 中（链接索引） | submodule 导入（选小体积） |
| 免费书籍清单 | 10 | **高**（书目索引） | submodule 导入 ✅ |
| 技术知识库/教程笔记 | 54 | 高（内容素材） | 批判加工后吸收 |
| 学习路径/课程 | 34 | 中（框架参考） | 链接 + 精选导入 |
| PKM/第二大脑 | 22 | 低-中（方法论） | 只做链接参考 |
| AI 知识库/LLM | 19 | 中-高（前沿素材） | 精选导入 + 追踪 |
| 知识图谱 | 7 | 中（方法论） | 链接 + 精选导入 |
| 面试题库 | 30 | 低（本库非求职向） | 选择性 |
| 其他知识导航 | 35+66 | 低-中 | 链接参考 |

---

## §2 专题问答（Q1-Q10）

### Q1 与 ebook-treasure-chest 直接同类的电子书聚合库有哪些？

**答**：共 76 个候选，最相近且高价值的 8 个 [来源: 本调研实测]：

| 仓库 | ★Star | 体积 | 特点 |
|:-----|:-----:|:----:|:-----|
| [kska32/ebooks](https://github.com/kska32/ebooks) | 7,323 | 4.3MB | 历史/政治/心理/哲学/数学/计算机，**约 10 万本**链接，最直接同类 |
| [forthespada/CS-Books](https://github.com/forthespada/CS-Books) | 27,173 | 0.3MB | **1000+ 计算机经典书籍**清单 + 个人笔记 |
| [programthink/books](https://github.com/programthink/books) | 20,191 | 1.1MB | 编程随想收藏，多学科电子书清单含下载链接 |
| [iamshuaidi/CS-Book](https://github.com/iamshuaidi/CS-Book) | 11,573 | — | 计算机类电子书整理 + 下载链接（Java/Python/Linux/Go/AI 全覆盖） |
| [Dujltqzv/Some-Many-Books](https://github.com/Dujltqzv/Some-Many-Books) | 22,466 | — | 个人收藏书籍列表 |
| [jobbole/awesome-programming-books](https://github.com/jobbole/awesome-programming-books) | 15,482 | — | 经典编程书籍大全（含系统架构/算法/前端/后端） |
| [sorenduan/awesome-java-books](https://github.com/sorenduan/awesome-java-books) | 7,075 | — | Java 开发者技术书籍大全 |
| [it-ebooks-0/geektime-books](https://github.com/it-ebooks-0/geektime-books) | 13,304 | — | 极客时间电子书（⚠️ 版权敏感） |

**对比 ebook-treasure-chest**：同为"链接聚合"形态，但大部分体积更小（0.3-8MB vs 21MB）、书目质量更聚焦技术领域；`kska32/ebooks` 学科广度最接近（历史/哲学/数学等非技术类）[来源: 本文推导]。

### Q2 有哪些高质量的免费书籍清单（体积小、适合直接导入）？

**答**：10 个，全部是"清单型"（md 链接列表），体积 1-21MB，是**知识库输入价值最高的一类** [来源: 本调研实测]：

| 仓库 | ★Star | 体积 | 特点 |
|:-----|:-----:|:----:|:-----|
| [EbookFoundation/free-programming-books](https://github.com/EbookFoundation/free-programming-books) | 394,666 | 21MB | 全球最大免费编程书清单（多语言），CC BY 4.0 |
| [justjavac/free-programming-books-zh_CN](https://github.com/justjavac/free-programming-books-zh_CN) | 118,376 | **1.1MB** | 中文编程书籍清单，最适导入 |
| [ruanyf/free-books](https://github.com/ruanyf/free-books) | 15,953 | 8.3MB | 阮一峰整理的互联网免费书籍 |
| [hackerkid/Mind-Expanding-Books](https://github.com/hackerkid/Mind-Expanding-Books) | 14,152 | — | 拓展思维的书单（科技/哲学/历史） |
| [EbookFoundation/free-science-books](https://github.com/EbookFoundation/free-science-books) | 2,233 | — | 免费科学书籍（free-programming-books 姊妹项目） |
| [revolunet/JSbooks](https://github.com/revolunet/JSbooks) | 2,523 | — | 免费 JavaScript 电子书目录 |
| [revolunet/PythonBooks](https://github.com/revolunet/PythonBooks) | 1,957 | — | 免费 Python 电子书目录 |
| [mhadidg/software-architecture-books](https://github.com/mhadidg/software-architecture-books) | 11,297 | — | 软件架构书籍清单 |
| [dariubs/GoBooks](https://github.com/dariubs/GoBooks) | 19,618 | — | Go 语言书籍清单 |
| [zero-equals-false/awesome-programming-books](https://github.com/zero-equals-false/awesome-programming-books) | 2,105 | — | 算法/数据结构精选书单 |

**导入推荐**：`justjavac/free-programming-books-zh_CN`（1.1MB）+ `ruanyf/free-books`（8.3MB）体积最小、中文友好，最适作为书目索引导入 [来源: 本文推导]。

### Q3 哪些技术知识库/教程笔记可作知识输入？

**答**：54 个候选，按主题分四组（本组体积普遍较大，**建议批判加工后吸收而非整库导入**）[来源: 本调研实测]：

**计算机基础/面试知识**：

| 仓库 | ★Star | 体积 | 特点 |
|:-----|:-----:|:----:|:-----|
| [CyC2018/CS-Notes](https://github.com/CyC2018/CS-Notes) | 185,421 | 113MB | 技术面试必备基础（OS/网络/系统设计） |
| [xiaolincoder/CS-Base](https://github.com/xiaolincoder/CS-Base) | 18,270 | — | 图解计算机网络/OS/数据库，1000 图 + 50 万字 |
| [huihut/interview](https://github.com/huihut/interview) | 38,131 | — | C/C++ 技术面试基础知识 |

**语言/框架教程**：

| 仓库 | ★Star | 体积 | 特点 |
|:-----|:-----:|:----:|:-----|
| [jackfrued/Python-100-Days](https://github.com/jackfrued/Python-100-Days) | 185,319 | 396MB | Python 100 天从新手到大师 |
| [sunface/rust-course](https://github.com/sunface/rust-course) | 30,798 | — | Rust 语言圣经（全面深入） |
| [qianguyihao/Web](https://github.com/qianguyihao/Web) | 28,662 | — | 前端入门到进阶图文教程 |
| [krahets/hello-algo](https://github.com/krahets/hello-algo) | 129,451 | — | 《Hello 算法》动画图解数据结构 |
| [Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide) | 157,851 | — | Java 面试 & 后端通用指南 |

**AI/机器学习笔记**：

| 仓库 | ★Star | 特点 |
|:-----|:-----:|:-----|
| [fengdu78/Coursera-ML-AndrewNg-Notes](https://github.com/fengdu78/Coursera-ML-AndrewNg-Notes) | 37,582 | 吴恩达机器学习课程笔记 |
| [fengdu78/deeplearning_ai_books](https://github.com/fengdu78/deeplearning_ai_books) | 20,985 | 吴恩达深度学习课程笔记 |
| [datawhalechina/pumpkin-book](https://github.com/datawhalechina/pumpkin-book) | 25,995 | 南瓜书：西瓜书公式详解 |
| [dair-ai/ML-Course-Notes](https://github.com/dair-ai/ML-Course-Notes) | 6,640 | ML 课程笔记 |

**大数据/后端**：

| 仓库 | ★Star | 特点 |
|:-----|:-----:|:-----|
| [heibaiying/BigData-Notes](https://github.com/heibaiying/BigData-Notes) | 16,950 | 大数据入门指南 |
| [wuyouzhuguli/SpringAll](https://github.com/wuyouzhuguli/SpringAll) | 28,951 | Spring 全家桶循序渐进 |
| [francistao/LearningNotes](https://github.com/francistao/LearningNotes) | 13,135 | 学习笔记 |

### Q4 学习路径/课程体系类有哪些？

**答**：34 个候选，核心 6 个 [来源: 本调研实测]：

| 仓库 | ★Star | 特点 |
|:-----|:-----:|:-----|
| [nilbuild/developer-roadmap](https://github.com/nilbuild/developer-roadmap) | 364,806 | 开发者路线图（原 kamranahmedse/developer-roadmap，含交互式图表） |
| [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | 364,572 | 系统设计入门（含 Anki 卡片） |
| [jwasham/coding-interview-university](https://github.com/jwasham/coding-interview-university) | 359,112 | 完整 CS 学习计划（自学成才路线） |
| [practical-tutorials/project-based-learning](https://github.com/practical-tutorials/project-based-learning) | 279,706 | 项目驱动学习教程清单 |
| [ossu/computer-science](https://github.com/ossu/computer-science) | 178,000+ | 开源 CS 学位课程体系（⚠️ 未在本批 top 命中，属知名确认） |
| [prakhar1989/awesome-courses](https://github.com/prakhar1989/awesome-courses) | 70,487 | 名校大学课程清单 |

**特点**：本类仓库是"知识的地图"而非"知识本身"——**最适合作为知识库的导航框架/学习路线参考，不适合作为内容源导入** [来源: 本文推导]。

### Q5 个人知识管理（PKM/第二大脑）类有哪些值得关注？

**答**：22 个候选，分**工具**与**方法论/模板**两组 [来源: 本调研实测]：

**工具类**（需要运行环境，只做链接参考）：

| 仓库 | ★Star | 特点 |
|:-----|:-----:|:-----|
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 71,645 | Notion+Miro 替代，本地优先 |
| [TriliumNext/Trilium](https://github.com/TriliumNext/Trilium) | 37,478 | 层级化个人知识库 |
| [khoj-ai/khoj](https://github.com/khoj-ai/khoj) | 36,542 | AI 第二大脑，自托管 |
| [foambubble/foam](https://github.com/foambubble/foam) | 17,360 | VSCode 内 PKM + 双链 |
| [dendronhq/dendron](https://github.com/dendronhq/dendron) | 7,462 | 层级化笔记 PKM |

**方法论/模板类**（静态 md，可借鉴）：

| 仓库 | ★Star | 特点 |
|:-----|:-----:|:-----|
| [oldwinter/knowledge-garden](https://github.com/oldwinter/knowledge-garden) | 2,456 | 中文第二大脑/数字花园（Obsidian 双链）实盘 |
| [KasperZutterman/Second-Brain](https://github.com/KasperZutterman/Second-Brain) | 1,829 | 公开 Zettelkasten/第二大脑清单 |
| [MaggieAppleton/digital-gardeners](https://github.com/MaggieAppleton/digital-gardeners) | 4,783 | 数字花园方法论资源 |
| [swyxio/brain](https://github.com/swyxio/brain) | 1,633 | Swyx 的第二大脑公开库 |
| [gnebbia/kb](https://github.com/gnebbia/kb) | 3,414 | 极简命令行知识库管理器 |

**对本知识库的启示**：`oldwinter/knowledge-garden` 与 `swyxio/brain` 是"公开第二大脑"的活样本——**可研究其组织结构作为本库目录治理的对照**（见 knowledge-index-manager / directory-optimizer 技能）[来源: 本文推导]。

### Q6 AI 知识库/LLM 相关仓库有哪些？

**答**：19 个候选，核心 8 个（**与 AI 基础设施方向 P0 最相关**）[来源: 本调研实测]：

| 仓库 | ★Star | 特点 |
|:-----|:-----:|:-----|
| [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book) | 38,885 | 《深入理解 AI Agent》开源全书（**本库已导入**） |
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 133,077 | 100+ AI Agents/RAG 应用开源 |
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | 92,513 | MCP 服务器清单（工具生态） |
| [labring/FastGPT](https://github.com/labring/FastGPT) | 29,385 | 基于 LLM 的知识库平台 |
| [chatchat-space/Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) | 38,550 | 基于 Langchain 的知识库问答 |
| [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki) | 16,500 | LLM Wiki 桌面应用 |
| [OpenSPG/KAG](https://github.com/OpenSPG/KAG) | 8,983 | 逻辑形式引导的推理检索框架（知识图谱 × LLM） |
| [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) | 3,387 | 自维护个人知识库 Agent |

**特别关注**：`awesome-llm-apps` 与 `awesome-mcp-servers` 属于"工具生态导航"——**与本库 Agent 技能体系（106 skills）直接相关，建议纳入每日调研跟踪源**（见 github-activity-report 技能）[来源: 本文推导]。

### Q7 知识图谱相关有哪些？

**答**：7 个候选 [来源: 本调研实测]：

| 仓库 | ★Star | 特点 |
|:-----|:-----:|:-----|
| [husthuke/awesome-knowledge-graph](https://github.com/husthuke/awesome-knowledge-graph) | 5,149 | 知识图谱学习资料（中文） |
| [liuhuanyong/QASystemOnMedicalKG](https://github.com/liuhuanyong/QASystemOnMedicalKG) | 7,349 | 医疗知识图谱 QA 系统实现 |
| [dkozlov/awesome-knowledge-distillation](https://github.com/dkozlov/awesome-knowledge-distillation) | 3,901 | 知识蒸馏论文清单 |
| [zjukg/KG-LLM-Papers](https://github.com/zjukg/KG-LLM-Papers) | 2,223 | KG×LLM 论文清单 |
| [totogo/awesome-knowledge-graph](https://github.com/totogo/awesome-knowledge-graph) | 1,881 | KG 学习材料（英文） |
| [FLHonker/Awesome-Knowledge-Distillation](https://github.com/FLHonker/Awesome-Knowledge-Distillation) | 2,684 | 知识蒸馏分类整理（2014-2021） |
| [BrambleXu/knowledge-graph-learning](https://github.com/BrambleXu/knowledge-graph-learning) | 778 | KG 教程与社区 |

**与本库的关系**：本库知识图谱建设处于"隐式图谱"阶段（交叉链接 + index 关系列），**这些仓库可作为显式图谱（实体/关系抽取）的方法论参考**——但注意知识管理价值链篇结论：图谱是仪表盘不是驾驶舱，优先完善检索与利用而非图谱本身 [来源: 知识管理价值链篇 §4.4]。

### Q8 面试题库类（知识测试形态）有哪些？

**答**：30 个候选，核心 5 个 [来源: 本调研实测]：

| 仓库 | ★Star | 特点 |
|:-----|:-----:|:-----|
| [yangshun/tech-interview-handbook](https://github.com/yangshun/tech-interview-handbook) | 141,952 | 编码面试准备手册 |
| [kdn251/interviews](https://github.com/kdn251/interviews) | 65,211 | Java 面试一站式 |
| [DopplerHQ/awesome-interview-questions](https://github.com/DopplerHQ/awesome-interview-questions) | 84,093 | 面试题清单之清单 |
| [0voice/interview_internal_reference](https://github.com/0voice/interview_internal_reference) | 37,233 | 大厂面试题 + 专家分析（阿里/腾讯/百度） |
| [huihut/interview](https://github.com/huihut/interview) | 38,131 | C/C++ 技术面试知识总结 |

**对本库的价值**：**低**——本库不是求职向；但"面试题=知识测试形态"可用于**新人培训/能力评估**场景（对照本质篇 §9.4 培训场景）[来源: 本文推导]。

### Q9 作为本知识库系统的输入，哪些优先导入（submodule）？

**答**：按"体积 × 许可 × 内容质量 × 更新频率"四维筛选，分三档 [来源: 本文推导 + git-submodule-import 技能]：

**A 档（强烈建议导入，体积小/纯 md/许可宽松）**：

| 仓库 | 体积 | 理由 |
|:-----|:----:|:-----|
| justjavac/free-programming-books-zh_CN | 1.1MB | 中文书目索引，★118k，最适 submodule |
| ruanyf/free-books | 8.3MB | 阮一峰书单，质量可靠 |
| forthespada/CS-Books | 0.3MB | 1000+ 计算机经典书清单 |
| kska32/ebooks | 4.3MB | 10 万本链接，学科广度最接近 ebook-treasure-chest |

**B 档（建议导入或精选吸收，体积较大）**：

| 仓库 | 体积 | 理由 |
|:-----|:----:|:-----|
| EbookFoundation/free-programming-books | 21MB | 全球最大书单（CC BY 4.0 许可明确） |
| programthink/books | 1.1MB | 多学科书单 |
| xiaolincoder/CS-Base | — | 图解 CS 基础（可作培训素材） |
| hello-algo | — | 算法图解（可作培训素材） |

**C 档（只做链接参考，不导入）**：PKM 工具类（AFFiNE/Trilium/khoj）、AI 平台类（FastGPT/Chatchat，需要运行环境）、大体积教程（Python-100-Days 396MB / CS-Notes 113MB / awesome-english-ebooks 14.7GB）[来源: 本文推导]。

### Q10 使用这些仓库有哪些合规/质量注意事项？

**答**：四条铁律 [来源: 本文推导 + RULE.md §6 + light-research-ethics 技能]：

1. **许可核查先行**：导入前检查 LICENSE——free-programming-books 系（CC BY 4.0）宽松；**无 LICENSE 的聚合库（如 kska32/ebooks、it-ebooks-0/geektime-books）只做书目索引，不转载内容**。
2. **版权红线**：电子书聚合库的下载链接指向的书籍可能涉盗版（帆书/微信读书/极客时间等平台付费内容被转载）——**入库仅存元数据/链接/摘要，不下载全文**（与本库 import/ 素材区原则一致）。
3. **内容批判使用**：教程/笔记类仓库是"二手加工品"——**关键量化数据须独立源交叉验证**（RULE.md §6），不直接当权威知识引用。
4. **不整库污染**：导入走 import/ 素材区 → 加工 → 沉淀的受控管线；**严禁"git submodule 拉进来就当知识用"**——素材不加工不得进入 knowledge/（知识加工流水线 §1.3）。

---

## §3 导入优先级建议

**建议动作（按 ROI 排序）** [来源: 本文推导]：

```text
P0: import 4 category-A list repos (free-programming-books-zh_CN, ruanyf/free-books,
    forthespada/CS-Books, kska32/ebooks) -> book index assets
P1: import category-B (free-programming-books) -> English book index
P2: curate category-C content (CS-Base/hello-algo training chapters) -> process into knowledge/
P3: add awesome-llm-apps / awesome-mcp-servers to daily tracking -> github-activity-report
P4: KG methodology reference (awesome-knowledge-graph) -> for explicit graph design
```

**预期收益**：书目索引资产（A 档）≈ 4-8MB 存储，换来"书籍导航"能力——检索"某主题有哪些经典书"时直接命中，无需重新调研 [来源: 本文推导]。

---

## §4 数据缺口与后续动作

| 缺口 | 说明 | 后续动作 |
|:-----|:-----|:---------|
| 许可未逐一核验 | 722 个仓库 LICENSE 未批量检查 | 导入前逐个查 LICENSE（git-submodule-import 元信息含此项） |
| star 门槛偏差 | star≥400 过滤可能漏掉"小而精"的新仓库 | 补充 topic:ebooks 的低 star 新库扫描 |
| 体积数据部分缺失 | API 返回 size 对 LFS/子模块仓库失真 | 导入前 du -sh 实测 |
| 中文社区视角验证（v2.0 部分解决）| web_search 因 key 失效不可用 | v2.0 已通过 datawhalechina/0voice/wx-chevalier 用户系列检索补充中文维度；知乎/B站文章交叉验证仍待恢复后补 |
| v2.0 新增：分类启发式误差 | 自动分类 20 类过细，部分边界仓库归类偏差 | 后续按实际使用反馈收敛分类；完整 722 数据在 import/ 素材区可随时重排 |

---

## §5 补充调研 v2.0（2026-08-22：52 组检索式 + 532 精选）

### 5.1 补充动机与范围

v1.0 九类形态聚焦"书籍/教程/笔记/PKM"等传统知识形态；v2.0 补充覆盖 **awesome 聚合生态、cheatsheet 速查表、文档手册 wiki、领域知识库（devops/k8s/db/security/network 等）、中文社区学习资源、资源聚合大全** 六大新形态——它们同为"知识类和文档类"素材，但 v1.0 检索轴未充分覆盖 [来源: 本调研推导]。

### 5.2 补充结果总览

| 维度 | v1.0（08-18） | v2.0 合并后（08-22） | 增量 |
|:-----|:-------------|:--------------------|:-----|
| 检索式 | 46 组 | 98 组 | +52 |
| 去重仓库 | 421 → 精选 353 | **722** | +301（新增 609 去重）|
| 精选门槛 | star≥400 | 原 353 + 补充 532（star≥800）| +532 |
| 形态类别 | 九类 | 九类 + 六类补充 | +6 |

[来源: 本调研实测]

### 5.3 补充发现（按价值排序）

**发现 1：awesome 生态 = 主题导航的第一入口（62 个新增）**
`sindresorhus/awesome` 体系（498.7k）衍生出按语言（Node.js 66.6k/Flutter 61k/Rust 58.9k/Java 48.8k/C++ 72.8k）与按领域（sysadmin 24.4k/scalability 73.4k）细分的清单网络。**对本库价值**：作为"某主题有哪些资源"的索引层，与免费书籍清单互为补充（书单→书，awesome→工具/库/教程）[来源: 本调研实测]。

**发现 2：cheatsheet/文档手册 = 运维与安全场景的速查资产（86 个新增）**
tldr-pages（63.4k，协作速查表，59.9MB）/awesome-cheatsheets（46.4k，8.7MB）/OWASP CheatSheetSeries（32.9k）/nginx-admins-handbook（14.3k）/trimstray/the-book-of-secret-knowledge（238.9k）。**对本库价值**：体积小、条目化，与运维/安全专题知识库的"速查索引"需求高度契合，适合 submodule 导入或精选加工 [来源: 本调研实测]。

**发现 3：中文社区知识供给生态 = 培训/入门素材富矿（57+ 个新增）**
- **datawhalechina 系列**（20+ 门中文教程）：hello-agents 74.1k / leedl-tutorial 16.7k / easy-rl 14.6k / fun-rec 7.3k / thorough-pytorch 3.8k / handy-ollama 2.5k / deepagents-in-action 1.7k——AI 方向全覆盖
- **0voice 系列**：interview_internal_reference 37.2k / learning_mind_map 2.8k / EmbeddedSoftwareLearn 2.4k / Career_planning_path 1.4k——系统软件方向
- **wx-chevalier 系列**：Developer-Zero-To-Mastery 3.2k / AI-Notes 785——知识图谱式学习笔记
**对本库价值**：与本库"服务器/AI 基础设施"培训场景匹配度高，0voice 嵌入式/驱动方向与本团队能力补齐主线（见 08-22 组织能力分析）直接相关 [来源: 本调研实测]。

**发现 4：领域知识库（devops/db/security/network）填补了 v1.0 技术分类的空白**
awesome-devops（milanm DevOps-Roadmap 20.3k）/awesome-database-learning（pingcap 11k）/awesome-security 系 /awesome-network 系——**与知识库 02_rd/06_O&M、03_hardware 等模块的输入需求对应**，可按模块定向加工 [来源: 本调研实测]。

### 5.4 导入优先级更新（v2.0）

| 档位 | v1.0 建议 | v2.0 增量建议 | 理由 |
|:-----|:---------|:--------------|:-----|
| P0 书目索引 | free-programming-books-zh_CN / free-books / CS-Books / ebooks | **+ tldr-pages**（协作速查表，运维场景即查即用）| 体积小/纯文本/许可宽松 |
| P1 精选吸收 | free-programming-books / CS-Base / hello-algo | **+ awesome-cheatsheets + 0voice/EmbeddedSoftwareLearn + datawhalechina/hello-agents** | 培训素材（嵌入式/驱动/AI Agent）与组织能力补齐主线匹配 |
| P2 领域加工 | KG 方法论参考 | **+ pingcap/awesome-database-learning + awesome-devops** | 对应知识库 O&M/数据库模块 |
| P3 追踪源 | awesome-llm-apps / awesome-mcp-servers | **+ awesome-claude-code 52.8k + awesome-openclaw-skills 52.1k + awesome-deepseek-integration 38.9k** | Agent 工具生态日新月异，纳入 github-activity-report 跟踪 |

### 5.5 素材落盘

完整 722 个仓库数据（含全部字段 JSON）与 532 个精选清单已落盘 **import/github-knowledge-survey-2026-08-22/**（素材区），供后续检索/导入决策直接使用 [来源: 本调研]。

---


---

## §6 领域定向补充 v3.0（2026-08-22：芯片/服务器/硬件/AI/产品研发五轴）

### 6.1 补充动机

v1.0/v2.0 按**知识形态**（书单/教程/笔记/清单）分类，适合通用选型；v3.0 按**业务领域轴**定向补充——聚焦与知识库主线（服务器/AI 基础设施，见 08-22 组织能力分析）直接相关的五个领域，为能力补齐提供素材弹药 [来源: 本调研推导]。

### 6.2 检索与筛选方法

55 组领域检索式（芯片×12/服务器×9/硬件×12/AI 基础设施×12/产品研发×10），新增 1,150 个候选。**筛选三步**：① 文档型过滤（排除功能性框架/引擎/SDK）→ ② 教学型保留（guide/tutorial/notes/book/learning/roadmap 等）→ ③ 黑名单清理（政治/无关/已在正文收录的重复项）。最终精选 198 个（star≥300）[来源: 本调研实测]。

### 6.3 五领域清单速览

| 领域 | 精选数 | 代表仓库 | 对本库价值 |
|:-----|:------:|:---------|:-----------|
| **AI 专项** | 94 | ml-engineering 18.7k / ai-engineering-hub 37.1k / Prompt-Engineering-Guide 77.7k / llama-cookbook 18.6k | AI 功底补齐（AI×推理/AI×RAS 嫁接点）|
| **产品研发/工程管理** | 34 | system-design-primer 365.3k / ADR 16.7k / Startup-CTO-Handbook 14.2k / awesome-software-architecture 11.6k | 研发流程/架构决策方法论 |
| **硬件/嵌入式** | 20 | cs249r_book 28k（ML Systems 教材）/ raspberry-pi-os 13.9k / Embedded-Engineering-Roadmap 12.9k / WireViz 5.2k | 固件/OS/嵌入式培训素材 |
| **芯片/半导体** | 19 | tiny-gpu 12.9k / learn-fpga 3.6k / chisel-book 926 / rCore-Tutorial 2.1k / open-fpga-verilog-tutorial 864 | 芯片设计学习链路（HDL→综合→验证）|
| **服务器/数据中心** | 6 | facebook/openbmc 684 / facebookarchive/opencompute 628 | **OpenBMC/OCP 生态入口（BMC 业务直接相关）** |

[来源: 本调研实测]

### 6.4 领域洞察（与组织能力补齐主线的映射）

1. **芯片领域：开源 ASIC/FPGA 学习链路已闭环**——tiny-gpu（Verilog 写 GPU）/learn-fpga（FPGA+yosys+nextpnr+RISC-V）/chisel-bootcamp（Chisel 生成器）/open-fpga-verilog-tutorial（开源工具综合验证）。**建议**：作为 BMC 芯片团队新人培训体系的参考教材（对应组织能力补齐"控制面纵深"）。注意：开源 EDA 工具链（yosys/nextpnr）与商业工具差距需评估 [来源: 本调研实测 + 本文推导]。

2. **服务器领域：OpenBMC 是必守阵地**——facebook/openbmc + OCP 社区是服务器管理面的事实标准生态。**建议**：纳入 github-activity-report 每日跟踪 + 评估团队向 OpenBMC 上游贡献的可行性（对应组织能力补齐"生态能力/开源杠杆"）[来源: 本调研实测 + 本文推导]。

3. **AI 领域：工程化知识直接服务 AI 功底补齐三嫁接**——ml-engineering（ML 工程 Open Book）→ AI×研发；system-design-primer → 方案能力；ai-engineering-hub → AI×推理场景。**建议**：精选加工入知识库 03_AI 模块 [来源: 本调研实测 + 本文推导]。

4. **产品研发领域：方法论资产**——ADR（架构决策记录）与知识库 ADR 实践直接对应；Startup-CTO-Handbook 可作为技术管理者参考 [来源: 本调研实测]。

### 6.5 素材落盘

第三批完整数据（1,150 候选 + 领域分类）与合并后全库 1,872 个仓库（all_items_v3.json）已落盘 **import/github-knowledge-survey-2026-08-22/**；领域精选 198 个清单已追加至本文附录 [来源: 本调研]。

## §7 基础学科补充 v4.0（2026-08-22：CS/数学/电子/半导体四轴）

### 7.1 补充动机

v3.0 按**业务领域轴**（芯片/服务器/硬件/AI/产品研发）补充了应用层素材；v4.0 按**基础学科轴**补充地基层——计算机科学/数学/电子/半导体四门基础学科，为团队能力补齐（固件→驱动→kernel→OS 纵深）和 AI 功底（数学地基）提供系统化学习素材 [来源: 本调研推导]。

### 7.2 检索与筛选方法

56 组基础学科检索式（CS×12/数学×12/电子×12/半导体×12/中文×8），新增 1,604 个候选（含 9 组失败查询补跑 + 40+ 经典仓库 API 核录）。**筛选三步**：① 文档型过滤（book/tutorial/notes/course 等关键词）→ ② 黑名单剔除（政治/破解软件/侵权 PDF 书库/无关工具）→ ③ 人工领域校准（修正启发式分类误判，如网络书误归电子、编译书误归 other）。最终精选 90 个（star≥300）[来源: 本调研实测]。

### 7.3 四领域清单速览

| 领域 | 精选数 | 代表仓库 | 对本库价值 |
|:-----|:------:|:---------|:-----------|
| **计算机科学** | 39 | build-your-own-x 541.9k / developer-roadmap 365.1k（已迁移 nilbuild）/ project-based-learning 280.3k / OSS University 208.3k / awesome-courses 70.6k | 全栈学习路径（造轮子→系统编程→分布式）|
| **数学** | 29 | 3b1b/manim 91.9k / MML-Book 15.9k / fastai NLA 11k / 鸢尾花书系列（矩阵 10k/数学要素 7.6k/统计至简 3.7k）/ OSS Math 9k / Think Stats 系列 | **AI 功底地基（数学→ML 完整路径）** |
| **半导体/芯片** | 16 | Yosys 4.7k / skywater-pdk 3.7k / OpenROAD 3k / logisim-evolution 7.5k / Digital 5.9k / iEDA 539 | 开源 EDA 链路（逻辑设计→综合→GDS）|
| **电子** | 6 | ThinkDSP 4.6k / Python-for-Signal-Processing 1.7k / CircuitVerse 1.2k / DSP 讲义 875 | 信号处理/数字逻辑（**开源生态薄弱，多为工具型**）|

[来源: 本调研实测]

### 7.4 领域洞察（与组织能力补齐主线的映射）

1. **CS 领域：全栈学习路径已闭环**——build-your-own-x（541.9k，造轮子大全：从零写数据库/OS/编译器）→ OSS University（208.3k，免费 CS 学位课程体系）→ dragon-book 习题解答（6.6k，编译原理）→ xv6-riscv-book（942，RISC-V OS）→ davidcallanan/os-series（878，从零写 OS）。**建议**：作为「固件→驱动→kernel→OS」纵深补强的培训教材库（对应 08-22 组织能力分析"哑铃策略"的杆部）[来源: 本调研实测 + 本文推导]。

2. **数学领域：AI 功底的地基**——mml-book（15.9k，《Mathematics for Machine Learning》官方网页）→ 鸢尾花书系列（Visualize-ML，三本共 21k+：矩阵/数学要素/统计至简）→ fastai/numerical-linear-algebra（11k，数值线性代数免费教材）→ ossu/math（9k，免费数学自学路径）。**建议**：精选加工入知识库 03_AI 模块，作为 AI×研发嫁接点的培训地基 [来源: 本调研实测 + 本文推导]。

3. **半导体领域：开源 EDA 生态已成型**——Yosys（4.7k，开源综合）/ OpenROAD（3k，RTL→GDS 全流程）/ skywater-pdk（3.7k，SkyWater 130nm PDK）/ efabless/caravel（406，SoC 模板）/ iEDA（539，国产开源 EDA）。**建议**：与 v3.0 芯片链路（tiny-gpu/learn-fpga/chisel）合并，构成「逻辑设计→开源 EDA→流片验证」完整培训链路 [来源: 本调研实测 + 本文推导]。

4. **电子领域：开源知识生态确为短板**——仅 6 个精选（ThinkDSP/信号处理/DSP 讲义/CircuitVerse 等），电子工程知识仍以专有教材（Art of Electronics 等）为主，开源化程度显著低于 CS。**建议**：电子知识输入以「经典教材+仿真工具实践」为主，不强求开源替代 [来源: 本调研实测 + 本文推导]。

### 7.5 素材落盘

第四批完整数据（1,604 候选 + 90 精选，v4_all_items.json / v4_final_selected.json）与合并后全库 2,482 个仓库（all_items_v5.json）已落盘 **import/github-knowledge-survey-2026-08-22/**；基础学科精选 90 个清单已追加至本文附录 [来源: 本调研]。

## §8 高校公开课补充 v5.0（2026-08-22：国内外名校课程）

### 8.1 补充动机

v4.0 基础学科提供了**教材/书籍**形态的素材；v5.0 补充**课程**形态——知名高校公开课（MIT/Stanford/Berkeley/CMU/Harvard/ETH + 国内清华/北大/浙大/中科大等），课程类资源与书籍互补：书籍重体系、课程重实践（作业/实验/Lab），是团队培训与个人自学的直接素材 [来源: 本调研推导]。

### 8.2 检索与筛选方法

26 组课程检索式（MIT×3/Stanford×2/Berkeley+CMU×4/Harvard+Princeton+ETH×4/清华北大×4/国内其他×6/课程聚合×5），新增 891 候选 + 经典课程仓库核录（raw 方式验证存在性）。**筛选三步**：① 课程关键词过滤（course/lecture/课程/攻略/notes 等）→ ② 黑名单剔除（刷课脚本/商业课程代码/培训机构文档）→ ③ 人工领域校准（PKUFlyingPig 系列为国外课程、cs231n.github.io 归国外）。最终精选 84 个（star≥400）[来源: 本调研实测]。

### 8.3 课程清单速览

| 分类 | 精选数 | 代表仓库 | 对本库价值 |
|:-----|:------:|:---------|:-----------|
| **国外名校公开课** | 48 | Learning-SICP 11.3k（MIT SICP 中文化）/ CS231n 官方 notes 11k / MIT 6.824 系列（chaozh 3.3k + OneSizeFitsQuorum 1.6k + feixiao 2.8k）/ CS229（maxim5 3.5k + cycleuser 中文翻译 3.5k）/ CS50 官方系列 | 全球顶级 CS 课程（OS/分布式/ML/编译）|
| **国内高校课程资料** | 18 | 浙大课程攻略 40.9k / 清华计算机系课程攻略 37.4k / 北大课程资料 33.9k / 中科大课程资源 16.2k / 上交课程资料 9.6k / 电子科大 4k | 国内名校课程攻略（含课件/作业/考试）|
| **AI/ML 课程** | 8 | 吴恩达 ML 笔记 37.6k / 吴恩达 DL 笔记 21k / datawhalechina llm-cookbook 24.6k / 李宏毅 ML 7.1k | AI 功底课程（ML/DL/LLM 系统学习）|
| **课程聚合/中文化** | 10 | Android 官方课程中文版 10.6k / CSAPP 字幕翻译 2.8k / 名校公开课评价网 3.2k / parallel101 高性能并行 4.2k | 课程导航与中文化入口 |

[来源: 本调研实测]

### 8.4 领域洞察（与组织能力补齐主线的映射）

1. **国外名校课程：系统软件深度学习的黄金素材**——MIT 6.824（分布式系统，chaozh 3.3k + 多版本翻译）、MIT SICP（程序构造，中文化 11.3k）、Stanford CS229/CS231n/CS224n（ML/NLP/CV 三件套）、CS50（哈佛入门）、CS6120（CMU 高级编译器 990）。**建议**：6.824 + CS229 系列优先导入培训体系（对应「分布式/内核」与「AI 功底」两条主线）[来源: 本调研实测 + 本文推导]。

2. **国内高校课程攻略：体系化课程资料金矿**——浙大（40.9k）/清华（37.4k）/北大（33.9k）/中科大（16.2k）/上交（9.6k）课程攻略覆盖各校培养方案全课程（课件+作业+考试），是中文语境下最完整的课程体系参考。**注意**：部分资料含版权风险（试卷/教材扫描件），导入须筛选 [来源: 本调研实测 + 本文推导]。

3. **课程与书籍的互补关系**：课程类（作业/Lab/项目导向）适合**实践训练**，书籍类（体系化理论）适合**系统学习**——团队培训建议「书籍打底 + 课程实操」双轨 [来源: 本文推导]。

### 8.5 素材落盘

第五批完整数据（891 候选 + 84 精选，v5_course_items.json / v5_final_selected.json）与合并后全库 2,482 个仓库（all_items_v5.json）已落盘 **import/github-knowledge-survey-2026-08-22/**；课程精选 84 个清单已追加至本文附录 [来源: 本调研]。

## §9 元方法论补充 v6.0（2026-08-22：哲学/系统论/方法论）

### 9.1 补充动机

v3.0-v5.0 按**业务/学科/课程**轴补充了「学什么」的素材；v6.0 补充**元方法论**——哲学/系统论/方法论维度，回答「怎么想」：对应知识库建设方法论（MECE/第一性原理/系统思维）与团队能力补齐的「AI 功底/判断力」主线。元知识类仓库数量少但杠杆高，是知识库的「操作系统层」素材 [来源: 本调研推导]。

### 9.2 检索与筛选方法

42 组检索式（哲学×10/系统论×10/方法论×10/中文×6/聚合×6），新增 1,189 候选（3 组中文查询因数据过大 ERR，以英文关键词替代覆盖）+ 经典仓库 core API 核录（ncase/loopy、gwern.net、awesome-falsehood、post-mortems、awesome-cold-showers、the-art-of-command-line、Allen Downey Think 系列等）。**筛选三步**：① 文档型过滤 → ② 严格领域关键词（哲学/系统/方法论专有词，排除机器学习误判）→ ③ **人工精选**（剔除 AI Skill 应用类噪音——毛选Skill/文案Skill/投资Skill 等，仅保留学术性/书籍/经典方法论资源）。最终精选 28 个（方法论 18/系统论 6/哲学 4）[来源: 本调研实测 + 人工判断]。

### 9.3 三领域清单速览

| 领域 | 精选数 | 代表仓库 | 对本库价值 |
|:-----|:------:|:---------|:-----------|
| **方法论/思维模型** | 18 | the-art-of-command-line 162.1k / awesome-falsehood 27.6k / post-mortems 12.3k / awesome-cold-showers 7.3k / awesome-concepts 628 / gwern.net 837 | 思维工具/编程谬误/故障复盘方法论 |
| **系统论/复杂性/控制论** | 6 | ncase/loopy 1.7k（系统思维工具）/ awesome-complexity 295 / 控制论资料 293 / ThinkComplexity 118 / 信号与系统讲义 382 | **系统思维×复杂系统（对应五看三定/架构方法论）** |
| **哲学/逻辑** | 4 | awesome-philosophy 270 / philoagents-course 1.5k（哲学×AI）/ Philosophy-Books 13 / aposd-vs-clean-code 1.8k（软件哲学） | 元认知/第一性原理的哲学地基 |

[来源: 本调研实测]

### 9.4 领域洞察（与知识库方法论主线的映射）

1. **方法论：编程谬误与故障复盘是高杠杆输入**——awesome-falsehood（27.6k，程序员常见错误假设清单）→ 直接对应知识库「13 谬误自检」的外部验证源；danluu/post-mortems（12.3k，真实故障复盘合集）→ 对应 RAS/故障诊断方法论素材；the-art-of-command-line（162.1k）→ 运维方法论速查 [来源: 本调研实测 + 本文推导]。

2. **系统论：系统思维工具稀缺但关键**——ncase/loopy（1.7k，系统因果回路可视化工具）是系统动力学教学经典；awesome-complexity（295）聚合复杂系统科学资源；ThinkComplexity 是复杂性科学教材。**建议**：结合知识库已有「五看三定」「复杂系统 function 框架」技能，形成「系统思维方法论」专题 [来源: 本调研实测 + 本文推导]。

3. **哲学/逻辑：GitHub 生态薄弱（仅 4 个精选）**——哲学类开源资源远少于技术类，本质是哲学知识以书籍/课程（非代码仓库）为主要载体。**建议**：哲学输入以经典书籍（波普尔/库恩/维特根斯坦等）+ 已收录的 OSS University 哲学课程为主，不强求 GitHub 覆盖 [来源: 本调研实测 + 本文推导]。

4. **重要发现：GitHub 上「方法论」关键词被 AI Skill 生态污染**——大量 Skill 仓库（毛选/文案/投资/简历等）滥用"方法论"标签，实际是 Prompt 模板而非方法论知识。**建议**：方法论类输入以经典书籍+学术资源为准，对 Skill 类保持警惕（对应知识库「import 素材批判使用」原则）[来源: 本调研实测 + 本文推导]。

### 9.5 素材落盘

第六批完整数据（1,189 候选 + 28 精选，v6_method_items.json / v6_final_selected.json / v6_classic_repos.json）与合并后全库 3,690 个仓库（all_items_v6.json）已落盘 **import/github-knowledge-survey-2026-08-22/**；方法论精选 28 个清单已追加至本文附录 [来源: 本调研]。

## 附录：完整仓库清单（353 个精选）

> 完整分类清单（按 star 降序，含仓库/Star/体积/语言/说明）——由调研脚本从全量 JSON 自动生成，共 353 个。

<details>
<summary>📋 展开查看完整清单（点击）</summary>

<!-- APPENDIX_START -->


### 免费书籍清单（10 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [EbookFoundation/free-programming-books](https://github.com/EbookFoundation/free-programming-books) | 394,666 | 21.2MB | Python | :books: Freely available programming books |
| [justjavac/free-programming-books-zh_CN](https://github.com/justjavac/free-programming-books-zh_CN) | 118,376 | 1.1MB | - | :books: 免费的计算机编程类中文书籍，欢迎投稿 |
| [ruanyf/free-books](https://github.com/ruanyf/free-books) | 15,953 | 8.3MB | - | 互联网上的免费书籍 |
| [Hack-with-Github/Free-Security-eBooks](https://github.com/Hack-with-Github/Free-Security-eBooks) | 4,974 | 0.1MB | - | Free Security and Hacking eBooks |
| [aluismoya/EbookFoundation-free-programming-books](https://github.com/aluismoya/EbookFoundation-free-programming-books) | 2,725 | 1.6MB | - |  |
| [revolunet/JSbooks](https://github.com/revolunet/JSbooks) | 2,523 | 6.6MB | CSS | Directory of free JavaScript ebooks |
| [EbookFoundation/free-science-books](https://github.com/EbookFoundation/free-science-books) | 2,233 | 0.3MB | - | Inspired by free-programming-books, here's free-science-books |
| [revolunet/PythonBooks](https://github.com/revolunet/PythonBooks) | 1,957 | 6.8MB | CSS | Directory of free Python ebooks |
| [yinhonggen/free-programming-books-zh_CN](https://github.com/yinhonggen/free-programming-books-zh_CN) | 685 | 0.3MB | JavaScript | https://github.com/justjavac/free-programming-books-zh_CN.git |
| [justinhartman/ui-ux-design-library](https://github.com/justinhartman/ui-ux-design-library) | 609 | 830.7MB | - | A collection of free eBooks and PDFs related to UI, UX and Interaction Design. |

### AI知识库/LLM（19 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 133,077 | 213.5MB | Python | 100+ AI Agents, Agent Skills and RAG Apps - Free and Open Source. |
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | 92,513 | 141.5MB | - | A collection of MCP servers. |
| [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book) | 38,885 | 748.7MB | Python | 《深入理解 AI Agent：设计原理与工程实践》（李博杰 著）开源主仓库：全书正文、编译版 PDF 与按章配套代码 |
| [chatchat-space/Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) | 38,550 | 141.1MB | Python | Langchain-Chatchat（原Langchain-ChatGLM）基于 Langchain 与 ChatGLM, Qwen 与 Llama 等语言 |
| [labring/FastGPT](https://github.com/labring/FastGPT) | 29,385 | 443.9MB | TypeScript | FastGPT is a knowledge-based platform built on the LLMs, offers a comprehensiv |
| [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki) | 16,500 | 39.2MB | TypeScript | LLM Wiki is a cross-platform desktop application that turns your documents int |
| [paperswithbacktest/awesome-systematic-trading](https://github.com/paperswithbacktest/awesome-systematic-trading) | 13,471 | 2.1MB | Python | A curated list of awesome libraries, packages, strategies, books, blogs, tutor |
| [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | 10,987 | 35.9MB | Python | Self-organizing AI second brain for Obsidian + Claude Code. Drop any source an |
| [yzhao062/anomaly-detection-resources](https://github.com/yzhao062/anomaly-detection-resources) | 9,365 | 0.4MB | Python | Anomaly detection related books, papers, videos, and toolboxes. Last update la |
| [OpenSPG/KAG](https://github.com/OpenSPG/KAG) | 8,983 | 186.9MB | Python | KAG is a logical form-guided reasoning and retrieval framework based on OpenSP |
| [PleasePrompto/notebooklm-skill](https://github.com/PleasePrompto/notebooklm-skill) | 7,641 | 0.2MB | Python | Use this skill to enable Claude Code to communicate directly with your Google  |
| [DataTalksClub/llm-zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp) | 7,063 | 9.6MB | Jupyter Notebook | LLM Zoomcamp - a free online course about real-life applications of LLMs. In 1 |
| [basicmachines-co/basic-memory](https://github.com/basicmachines-co/basic-memory) | 3,674 | 47.8MB | Python | AI conversations that actually remember. Never re-explain your project to your |
| [inkeep/open-knowledge](https://github.com/inkeep/open-knowledge) | 3,494 | 111.2MB | TypeScript | Beautiful, AI-native markdown IDE and LLM wiki |
| [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) | 3,387 | 0.4MB | Python | A personal knowledge base that builds and maintains itself. Drop in sources —  |
| [decodingai-magazine/second-brain-ai-assistant-course](https://github.com/decodingai-magazine/second-brain-ai-assistant-course) | 3,043 | 170.3MB | Jupyter Notebook | Learn to build your Second Brain AI assistant with LLMs, agents, RAG, fine-tun |
| [zjukg/KG-LLM-Papers](https://github.com/zjukg/KG-LLM-Papers) | 2,223 | 0.2MB | - | [Paper List] Papers integrating knowledge graphs (KGs) and large language mode |
| [satellitecomponent/Neurite](https://github.com/satellitecomponent/Neurite) | 2,119 | 22.2MB | JavaScript | Fractal Graph-of-Thought. Rhizomatic Mind-Mapping for Ai-Agents, Web-Links, No |
| [swarmclawai/swarmvault](https://github.com/swarmclawai/swarmvault) | 659 | 0.9MB | TypeScript | The local-first LLM Wiki: open-source knowledge graph builder, RAG knowledge b |

### 知识图谱（7 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [liuhuanyong/QASystemOnMedicalKG](https://github.com/liuhuanyong/QASystemOnMedicalKG) | 7,349 | 17.2MB | Python |  A tutorial and implement of disease centered Medical knowledge graph and qa s |
| [husthuke/awesome-knowledge-graph](https://github.com/husthuke/awesome-knowledge-graph) | 5,149 | 168.8MB | - | 整理知识图谱相关学习资料 |
| [dkozlov/awesome-knowledge-distillation](https://github.com/dkozlov/awesome-knowledge-distillation) | 3,901 | 0.3MB | - | Awesome Knowledge Distillation |
| [FLHonker/Awesome-Knowledge-Distillation](https://github.com/FLHonker/Awesome-Knowledge-Distillation) | 2,684 | 0.5MB | - | Awesome Knowledge-Distillation. 分类整理的知识蒸馏paper(2014-2021)。 |
| [totogo/awesome-knowledge-graph](https://github.com/totogo/awesome-knowledge-graph) | 1,881 | 0.1MB | - | A curated list of Knowledge Graph related learning materials, databases, tools |
| [heathersherry/Knowledge-Graph-Tutorials-and-Papers](https://github.com/heathersherry/Knowledge-Graph-Tutorials-and-Papers) | 1,068 | 4.5MB | - | Insightful Tutorials and Papers about Knowledge Graphs |
| [BrambleXu/knowledge-graph-learning](https://github.com/BrambleXu/knowledge-graph-learning) | 778 | 0.1MB | - | A curated list of awesome knowledge graph tutorials, projects and communities. |

### PKM/第二大脑（22 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 71,645 | 436.1MB | TypeScript | There can be more than Notion and Miro. AFFiNE(pronounced [ə‘fain]) is a next- |
| [TriliumNext/Trilium](https://github.com/TriliumNext/Trilium) | 37,479 | 634.7MB | TypeScript | Build your personal knowledge base with Trilium Notes |
| [khoj-ai/khoj](https://github.com/khoj-ai/khoj) | 36,542 | 114.5MB | Python | Your AI second brain. Self-hostable. Get answers from the web or your docs. Bu |
| [foambubble/foam](https://github.com/foambubble/foam) | 17,360 | 62.1MB | TypeScript | A personal knowledge management and sharing system for VSCode |
| [streetwriters/notesnook](https://github.com/streetwriters/notesnook) | 14,427 | 287.3MB | TypeScript | A fully open source & end-to-end encrypted note taking alternative to Evernote |
| [windingwind/zotero-better-notes](https://github.com/windingwind/zotero-better-notes) | 8,098 | 17.4MB | TypeScript | Everything about note management. All in Zotero. |
| [dendronhq/dendron](https://github.com/dendronhq/dendron) | 7,462 | 110.3MB | TypeScript | The personal knowledge management (PKM) tool that grows as you do! |
| [MaggieAppleton/digital-gardeners](https://github.com/MaggieAppleton/digital-gardeners) | 4,783 | 5.7MB | JavaScript | Resources, links, projects, and ideas for gardeners tending their digital note |
| [breferrari/obsidian-mind](https://github.com/breferrari/obsidian-mind) | 4,495 | 6.1MB | TypeScript | A self-organizing Obsidian vault that gives AI coding agents persistent memory |
| [eugeniughelbur/obsidian-second-brain](https://github.com/eugeniughelbur/obsidian-second-brain) | 4,081 | 21.6MB | Python | Persistent memory for Claude Code and 6 other CLI agents, stored as plain mark |
| [gnekt/My-Brain-Is-Full-Crew](https://github.com/gnekt/My-Brain-Is-Full-Crew) | 3,457 | 0.5MB | Shell | Built by a PhD whose memory was failing, whose diet was a mess, and whose anxi |
| [zk-org/zk](https://github.com/zk-org/zk) | 2,764 | 2.0MB | Go | A plain text note-taking assistant |
| [revezone/revezone](https://github.com/revezone/revezone) | 2,646 | 9.3MB | TypeScript | A lightweight local-first graphic-centric  productivity tool to build your sec |
| [oldwinter/knowledge-garden](https://github.com/oldwinter/knowledge-garden) | 2,456 | 369.6MB | TypeScript | 我的第二大脑 second brain，我的数字花园 digital garden，用obsidian双链笔记软件写作而成 |
| [KasperZutterman/Second-Brain](https://github.com/KasperZutterman/Second-Brain) | 1,829 | 0.2MB | - | A curated list of awesome Public Zettelkastens 🗄️ / Second Brains 🧠 / Digital  |
| [ballred/obsidian-claude-pkm](https://github.com/ballred/obsidian-claude-pkm) | 1,826 | 0.2MB | Shell | A complete starter kit for an Obsidian + Claude Code personal knowledge manage |
| [swyxio/brain](https://github.com/swyxio/brain) | 1,633 | 57.9MB | - | Swyx's second brain! |
| [alchaincyf/obsidian-ai-orange-book](https://github.com/alchaincyf/obsidian-ai-orange-book) | 1,406 | 19.8MB | - | Obsidian + Claude Code: Rebuild Your Second Brain with AI · 橙皮书系列 · 用AI重建你的第二大 |
| [your-papa/obsidian-Smart2Brain](https://github.com/your-papa/obsidian-Smart2Brain) | 1,213 | 8.6MB | TypeScript | An Obsidian plugin to interact with your privacy focused AI-Assistant making y |
| [mateaix/mateclaw](https://github.com/mateaix/mateclaw) | 1,001 | 33.1MB | Java | 🤖 MateClaw — Your second brain with Multi-Agent Orchestration, MCP Protocol, S |
| [huytieu/COG-second-brain](https://github.com/huytieu/COG-second-brain) | 924 | 0.4MB | HTML | Self-evolving second brain with 33 AI skills, 10 agents, and people CRM. Close |
| [churichard/notabase](https://github.com/churichard/notabase) | 910 | 41.6MB | TypeScript | A second brain for your knowledge, thoughts, and ideas. |

### 面试题库（30 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | 364,572 | 11.0MB | Python | Learn how to design large-scale systems. Prep for the system design interview. |
| [jwasham/coding-interview-university](https://github.com/jwasham/coding-interview-university) | 359,112 | 22.2MB | - | A complete computer science study plan to become a software engineer. |
| [CyC2018/CS-Notes](https://github.com/CyC2018/CS-Notes) | 185,421 | 113.5MB | - | :books: 技术面试必备基础知识、Leetcode、计算机操作系统、计算机网络、系统设计 |
| [Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide) | 157,851 | 179.6MB | JavaScript | Java 面试 & 后端通用面试指南，覆盖计算机基础、数据库、分布式、高并发、系统设计与 AI 应用开发 |
| [yangshun/tech-interview-handbook](https://github.com/yangshun/tech-interview-handbook) | 141,952 | 32.9MB | TypeScript | Curated coding interview preparation materials for busy software engineers |
| [DopplerHQ/awesome-interview-questions](https://github.com/DopplerHQ/awesome-interview-questions) | 84,093 | 0.5MB | - | :octocat: A curated awesome list of lists of interview questions. Feel free to |
| [kdn251/interviews](https://github.com/kdn251/interviews) | 65,211 | 23.9MB | Java | Everything you need to know to get the job. |
| [h5bp/Front-end-Developer-Interview-Questions](https://github.com/h5bp/Front-end-Developer-Interview-Questions) | 60,877 | 5.9MB | Nunjucks | A list of helpful front-end related questions you can use to interview potenti |
| [sudheerj/reactjs-interview-questions](https://github.com/sudheerj/reactjs-interview-questions) | 44,733 | 6.5MB | JavaScript | List of top 500 ReactJS Interview Questions & Answers....Coding exercise quest |
| [yangshun/front-end-interview-handbook](https://github.com/yangshun/front-end-interview-handbook) | 43,988 | 323.3MB | JavaScript | Front End interview preparation materials for busy engineers (updated for 2026 |
| [huihut/interview](https://github.com/huihut/interview) | 38,131 | 5.6MB | C++ | 📚 C/C++ 技术面试基础知识总结，包括语言、程序库、数据结构、算法、系统、网络、链接装载库等知识及面试经验、招聘、内推等信息。This reposito |
| [0voice/interview_internal_reference](https://github.com/0voice/interview_internal_reference) | 37,233 | 1.1MB | Python | 2025年最新总结，阿里，腾讯，百度，美团，头条等技术面试题目，以及答案，专家出题人分析汇总。 |
| [viraptor/reverse-interview](https://github.com/viraptor/reverse-interview) | 28,580 | 0.3MB | - | Questions to ask the company during your interview |
| [sudheerj/javascript-interview-questions](https://github.com/sudheerj/javascript-interview-questions) | 27,599 | 6.5MB | JavaScript | List of 1000 JavaScript Interview Questions |
| [Advanced-Frontend/Daily-Interview-Question](https://github.com/Advanced-Frontend/Daily-Interview-Question) | 27,396 | 0.2MB | JavaScript | 我是依扬（木易杨），公众号「高级前端进阶」作者，每天搞定一道前端大厂面试题，祝大家天天进步，一年后会看到不一样的自己。 |
| [haizlin/fe-interview](https://github.com/haizlin/fe-interview) | 26,255 | 7.9MB | JavaScript | 前端面试每日 3+1，以面试题来驱动学习，提倡每日学习与思考，每天进步一点！每天早上5点纯手工发布面试题（死磕自己，愉悦大家），6000+道前端面试题全面覆 |
| [checkcheckzz/system-design-interview](https://github.com/checkcheckzz/system-design-interview) | 23,624 | 0.3MB | - | System design interview for IT companies |
| [jbee37142/Interview_Question_for_Beginner](https://github.com/jbee37142/Interview_Question_for_Beginner) | 21,655 | 0.6MB | - | :boy: :girl: Technical-Interview guidelines written for those who started stud |
| [jobbole/awesome-programming-books](https://github.com/jobbole/awesome-programming-books) | 15,482 | 0.2MB | - | 经典编程书籍大全，涵盖：计算机系统与网络、系统架构、算法与数据结构、前端开发、后端开发、移动开发、数据库、测试、项目与团队、程序员职业修炼、求职面试等 |
| [liquidslr/system-design-notes](https://github.com/liquidslr/system-design-notes) | 12,703 | 81.1MB | - | Notes of the book System Desgin Interview - An Insider's Guide |
| [iamshuaidi/CS-Book](https://github.com/iamshuaidi/CS-Book) | 11,573 | 0.5MB | - | 计算机类常用电子书整理，并且附带下载链接，包括Java，Python，Linux，Go，C，C++，数据结构与算法，人工智能，计算机基础，面试，设计模式，数 |
| [YSGStudyHards/DotNetGuide](https://github.com/YSGStudyHards/DotNetGuide) | 10,805 | 5.3MB | C# | 🌈【C#/.NET/.NET Core学习、工作、面试指南】记录、收集和总结C#/.NET/.NET Core基础知识、学习路线、开发实战、编程技巧练习、学 |
| [sorenduan/awesome-java-books](https://github.com/sorenduan/awesome-java-books) | 7,075 | 0.1MB | - | Java开发者技术书籍大全 - Java入门书籍，Java基础及进阶书籍，框架与中间件，架构设计，设计模式，数学与算法，JVM周边语言，项目管理&领导力&流 |
| [JsonChao/Awesome-Android-Interview](https://github.com/JsonChao/Awesome-Android-Interview) | 4,609 | 22.5MB | - | :fire: A awesome  android expert interview questions and answers（continuous up |
| [PaddlePaddle/awesome-DeepLearning](https://github.com/PaddlePaddle/awesome-DeepLearning) | 3,644 | 489.7MB | Jupyter Notebook | 深度学习入门课、资深课、特色课、学术案例、产业实践案例、深度学习知识百科及面试题库The course, case and knowledge of Dee |
| [wx-chevalier/Developer-Zero-To-Mastery](https://github.com/wx-chevalier/Developer-Zero-To-Mastery) | 3,186 | 15.3MB | HTML | :books: To Be Professional Developer From Zero To Mastery, Interactive MindMap |
| [Snailclimb/JavaGuide-Interview](https://github.com/Snailclimb/JavaGuide-Interview) | 2,623 | 20.4MB | JavaScript | JavaGuide面试突击版，Java 学习&面试突击（Go、Python 后端面试通用,计算机基础面试总结） |
| [imkgarg/Awesome-Software-Engineering-Interview](https://github.com/imkgarg/Awesome-Software-Engineering-Interview) | 1,033 | 0.3MB | - |  |
| [bhartik021/SDE-Interview-Materials](https://github.com/bhartik021/SDE-Interview-Materials) | 792 | 252.0MB | - | An repository that contains all the Data Structures and Algorithms Notes, CS F |
| [JGPY/JavaGuideBooster](https://github.com/JGPY/JavaGuideBooster) | 644 | 508.1MB | - | Java 面试加速器，欢迎各位一起来完善，让更多的有心之人能够受益! |

### 电子书/书籍聚合（76 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [prakhar1989/awesome-courses](https://github.com/prakhar1989/awesome-courses) | 70,487 | 1.4MB | - | :books: List of awesome university courses for learning Computer Science! |
| [astaxie/build-web-application-with-golang](https://github.com/astaxie/build-web-application-with-golang) | 43,902 | 37.4MB | Go | A golang ebook intro how to build a web with golang |
| [lfnovo/open-notebook](https://github.com/lfnovo/open-notebook) | 37,019 | 21.2MB | TypeScript | An Open Source implementation of Notebook LM with more flexibility and feature |
| [hehonghui/awesome-english-ebooks](https://github.com/hehonghui/awesome-english-ebooks) | 34,999 | 14740.5MB | CSS | 经济学人(含音频)、纽约客、卫报、连线、大西洋月刊等英语杂志免费下载,支持epub、mobi、pdf格式, 每周更新 |
| [sunface/rust-course](https://github.com/sunface/rust-course) | 30,798 | 45.5MB | Rust | 什么？你敢放心的把后背交给 AI? 我赌你不敢，那就来学学 AI 时代最酷、最安全、最快的语言吧。本书拥有全面且深入的讲解、生动贴切的示例、德芙般丝滑的内容 |
| [koreader/koreader](https://github.com/koreader/koreader) | 29,091 | 70.9MB | Lua | An ebook reader application supporting PDF, DjVu, EPUB, FB2 and many more form |
| [koodo-reader/koodo-reader](https://github.com/koodo-reader/koodo-reader) | 27,898 | 92.3MB | JavaScript | A modern ebook manager and reader with sync and backup capacities for Windows, |
| [forthespada/CS-Books](https://github.com/forthespada/CS-Books) | 27,173 | 0.3MB | - | 🔥🔥超过1000本的计算机经典书籍、个人笔记资料以及本人在各平台发表文章中所涉及的资源等。书籍资源包括C/C++、Java、Python、Go语言、数据结构 |
| [datawhalechina/pumpkin-book](https://github.com/datawhalechina/pumpkin-book) | 25,995 | 11.0MB | - | 南瓜书：《机器学习》（西瓜书）公式详解 |
| [kovidgoyal/calibre](https://github.com/kovidgoyal/calibre) | 25,675 | 323.3MB | Python | The official source code repository for the calibre ebook manager |
| [wesm/pydata-book](https://github.com/wesm/pydata-book) | 24,827 | 63.7MB | Jupyter Notebook | Materials and IPython notebooks for "Python for Data Analysis" by Wes McKinney |
| [readest/readest](https://github.com/readest/readest) | 23,517 | 245.0MB | TypeScript | Readest is a modern, feature-rich ebook reader designed for avid readers offer |
| [Dujltqzv/Some-Many-Books](https://github.com/Dujltqzv/Some-Many-Books) | 22,466 | 2646.8MB | - | 个人收藏书籍列表　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 |
| [cat-milk/Anime-Girls-Holding-Programming-Books](https://github.com/cat-milk/Anime-Girls-Holding-Programming-Books) | 22,459 | 1084.0MB | - | Anime Girls Holding Programming Books |
| [fengdu78/deeplearning_ai_books](https://github.com/fengdu78/deeplearning_ai_books) | 20,985 | 571.4MB | HTML | deeplearning.ai（吴恩达老师的深度学习课程笔记及资源） |
| [programthink/books](https://github.com/programthink/books) | 20,191 | 1.1MB | - | 【编程随想】收藏的电子书清单（多个学科，含下载链接） |
| [chai2010/advanced-go-programming-book](https://github.com/chai2010/advanced-go-programming-book) | 20,081 | 20.1MB | Go | :books: 《Go语言高级编程》开源图书，涵盖CGO、Go汇编语言、RPC实现、Protobuf插件实现、Web框架实现、分布式系统等高阶主题(完稿) |
| [DrewThomasson/ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook) | 19,733 | 79.8MB | Python | Generate audiobooks from e-books, voice cloning & 1158+ languages! |
| [dariubs/GoBooks](https://github.com/dariubs/GoBooks) | 19,618 | 11.3MB | Go | List of Golang books |
| [BookStackApp/BookStack](https://github.com/BookStackApp/BookStack) | 18,992 | 50.7MB | PHP | NOW MANAGED ON CODEBERG |
| [janeczku/calibre-web](https://github.com/janeczku/calibre-web) | 17,888 | 117.7MB | Fluent | :books: Web app for browsing, reading and downloading eBooks stored in a Calib |
| [iamgio/quarkdown](https://github.com/iamgio/quarkdown) | 15,921 | 32.9MB | Kotlin | 🪐 Markdown with superpowers: from ideas to papers, presentations, websites, bo |
| [owainlewis/awesome-artificial-intelligence](https://github.com/owainlewis/awesome-artificial-intelligence) | 15,877 | 0.2MB | Python | A curated list of Artificial Intelligence (AI) courses, books, video lectures  |
| [apprenticeharper/DeDRM_tools](https://github.com/apprenticeharper/DeDRM_tools) | 15,300 | 24.3MB | Python | DeDRM tools for ebooks |
| [sbilly/awesome-security](https://github.com/sbilly/awesome-security) | 14,759 | 0.8MB | - | A collection of awesome software, libraries, documents, books, resources and c |
| [hackerkid/Mind-Expanding-Books](https://github.com/hackerkid/Mind-Expanding-Books) | 14,152 | 2.7MB | JavaScript |  :books: Find your next book to read! |
| [it-ebooks-0/geektime-books](https://github.com/it-ebooks-0/geektime-books) | 13,304 | 1536.9MB | - | :books: 极客时间电子书 |
| [0voice/expert_readed_books](https://github.com/0voice/expert_readed_books) | 12,337 | 6451.3MB | - | 2021年最新总结，推荐工程师合适读本，计算机科学，软件技术，创业，思想类，数学类，人物传记书籍 |
| [mhadidg/software-architecture-books](https://github.com/mhadidg/software-architecture-books) | 11,297 | 0.0MB | - | A comprehensive list of books on Software Architecture. |
| [phodal/github](https://github.com/phodal/github) | 11,144 | 25.6MB | Rich Text Format | GitHub 漫游指南- a Chinese ebook on how to build a good project on Github. Explore |
| [unicodeveloper/awesome-nextjs](https://github.com/unicodeveloper/awesome-nextjs) | 11,109 | 0.3MB | - | :notebook_with_decorative_cover: :books: A curated list of awesome resources : |
| [QianMo/Game-Programmer-Study-Notes](https://github.com/QianMo/Game-Programmer-Study-Notes) | 10,008 | 770.4MB | - | :anchor:  我的游戏程序员生涯的读书笔记合辑。你可以把它看作一个加强版的Blog。涉及图形学、实时渲染、编程实践、GPU编程、设计模式、软件工程等内 |
| [amejiarosario/dsa.js-data-structures-algorithms-javascript](https://github.com/amejiarosario/dsa.js-data-structures-algorithms-javascript) | 7,772 | 112.7MB | JavaScript | 🥞Data Structures and Algorithms explained and implemented in JavaScript + eBoo |
| [Vay-keen/Machine-learning-learning-notes](https://github.com/Vay-keen/Machine-learning-learning-notes) | 7,762 | 0.1MB | - | 周志华《机器学习》又称西瓜书是一本较为全面的书籍，书中详细介绍了机器学习领域不同类型的算法(例如：监督学习、无监督学习、半监督学习、强化学习、集成降维、特征 |
| [linsa-io/books](https://github.com/linsa-io/books) | 7,588 | 0.5MB | - | Awesome Books |
| [kska32/ebooks](https://github.com/kska32/ebooks) | 7,323 | 4.3MB | JavaScript | 收藏的一些经典的历史、政治、心理、哲学、数学、计算机方面电子书(约10万本） |
| [futurepress/epub.js](https://github.com/futurepress/epub.js) | 6,942 | 26.8MB | JavaScript | Enhanced eBooks in the browser. |
| [Sigil-Ebook/Sigil](https://github.com/Sigil-Ebook/Sigil) | 6,930 | 234.3MB | C++ | Sigil is a multi-platform EPUB ebook editor |
| [RongleXie/java-books-collections](https://github.com/RongleXie/java-books-collections) | 6,673 | 1062.5MB | - | :books:Java编程书籍收集分享。Java programming books collection to share.:rocket: |
| [keyvanakbary/learning-notes](https://github.com/keyvanakbary/learning-notes) | 6,463 | 1.7MB | SCSS | Notes on books I read, talks I watch, articles I study, and papers I love |
| [yeahhub/Hacking-Security-Ebooks](https://github.com/yeahhub/Hacking-Security-Ebooks) | 6,425 | 0.0MB | - | Top 100 Hacking & Security E-Books (Free Download)  |
| [bobbyiliev/introduction-to-bash-scripting](https://github.com/bobbyiliev/introduction-to-bash-scripting) | 6,305 | 17.2MB | HTML | Free Introduction to Bash Scripting eBook |
| [crocodilestick/Calibre-Web-Automated](https://github.com/crocodilestick/Calibre-Web-Automated) | 6,119 | 148.1MB | JavaScript | Calibre-Web but Automated and with tons of New Features! Fully automate and si |
| [secfigo/Awesome-Fuzzing](https://github.com/secfigo/Awesome-Fuzzing) | 5,896 | 0.2MB | - | A curated list of fuzzing resources ( Books, courses - free and paid, videos,  |
| [royeo/awesome-programming-books](https://github.com/royeo/awesome-programming-books) | 4,894 | 0.0MB | - | 📚 经典技术书籍推荐，持续更新... |
| … | 其余 31 个略 | | | |

### 技术知识库/教程笔记（54 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [awesome-selfhosted/awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) | 313,408 | 16.8MB | - | A list of Free Software network services and web applications which can be hos |
| [trimstray/the-book-of-secret-knowledge](https://github.com/trimstray/the-book-of-secret-knowledge) | 238,949 | 1.7MB | - | A collection of inspiring lists, manuals, cheatsheets, blogs, hacks, one-liner |
| [jackfrued/Python-100-Days](https://github.com/jackfrued/Python-100-Days) | 185,319 | 396.1MB | Jupyter Notebook | Python - 100天从新手到大师 |
| [krahets/hello-algo](https://github.com/krahets/hello-algo) | 129,451 | 467.1MB | Java | 《Hello 算法》：动画图解、一键运行的数据结构与算法教程。支持简中、繁中、English、日本語，提供 Python, Java, C++, C, C# |
| [microsoft/Web-Dev-For-Beginners](https://github.com/microsoft/Web-Dev-For-Beginners) | 96,366 | 2153.0MB | JavaScript | 24 Lessons, 12 Weeks, Get Started as a Web Developer |
| [sdmg15/Best-websites-a-programmer-should-visit](https://github.com/sdmg15/Best-websites-a-programmer-should-visit) | 76,273 | 2.0MB | - | :link: Some useful websites for programmers. |
| [jeecgboot/JeecgBoot](https://github.com/jeecgboot/JeecgBoot) | 47,416 | 96.4MB | Java | 【低代码迈入v2.0时代，一句话即可生成整个系统】企业级AI低代码平台，一键生成前后端代码甚至整个系统。 AI Skills 一句话画流程、设计表单、生成报 |
| [dypsilon/frontend-dev-bookmarks](https://github.com/dypsilon/frontend-dev-bookmarks) | 47,391 | 1.0MB | - | Manually curated collection of resources for frontend web developers. |
| [halo-dev/halo](https://github.com/halo-dev/halo) | 39,491 | 86.7MB | Java | Halo 是一款强大易用的开源建站工具，从个人博客、知识库，到企业官网、在线商城，Halo 都能助您轻松实现，一站式满足您的多样化建站需求。 |
| [fengdu78/Coursera-ML-AndrewNg-Notes](https://github.com/fengdu78/Coursera-ML-AndrewNg-Notes) | 37,582 | 647.1MB | HTML | 吴恩达老师的机器学习课程个人笔记 |
| [qianguyihao/Web](https://github.com/qianguyihao/Web) | 28,662 | 7.4MB | - | 千古前端图文教程，超详细的前端入门到进阶知识库。从零开始学前端，做一名精致优雅的前端工程师。 |
| [xiaolincoder/CS-Base](https://github.com/xiaolincoder/CS-Base) | 18,270 | 1.5MB | - | 图解计算机网络、操作系统、计算机组成、数据库，共 1000 张图 + 50 万字，破除晦涩难懂的计算机基础知识，让天下没有难懂的八股文！🚀 在线阅读：htt |
| [dexteryy/spellbook-of-modern-webdev](https://github.com/dexteryy/spellbook-of-modern-webdev) | 17,886 | 0.5MB | - | A Big Picture, Thesaurus, and Taxonomy of Modern JavaScript Web Development |
| [langbot-app/LangBot](https://github.com/langbot-app/LangBot) | 17,471 | 55.2MB | Python | Production-grade platform for building agentic IM bots - 生产级多平台智能机器人开发平台/ Agen |
| [geektutu/7days-golang](https://github.com/geektutu/7days-golang) | 16,977 | 1.0MB | Go | 7 days golang programs from scratch (web framework Gee, distributed cache GeeC |
| [heibaiying/BigData-Notes](https://github.com/heibaiying/BigData-Notes) | 16,950 | 23.5MB | Java | 大数据入门指南  :star: |
| [francistao/LearningNotes](https://github.com/francistao/LearningNotes) | 13,135 | 0.6MB | - | Enjoy Learning. |
| [codexu/note-gen](https://github.com/codexu/note-gen) | 12,653 | 17.0MB | TypeScript | Capture first. Organize later. A local-first Markdown app that turns scattered |
| [flxzt/rnote](https://github.com/flxzt/rnote) | 11,561 | 266.6MB | Rust | Sketch and take handwritten notes. |
| [roboticcam/machine-learning-notes](https://github.com/roboticcam/machine-learning-notes) | 10,331 | 176.3MB | Jupyter Notebook | My continuously updated Machine Learning, Probabilistic Models and Deep Learni |
| [hackmdio/codimd](https://github.com/hackmdio/codimd) | 10,131 | 28.2MB | JavaScript | CodiMD - Realtime collaborative markdown notes on all platforms. |
| [chaitin/PandaWiki](https://github.com/chaitin/PandaWiki) | 10,124 | 41.2MB | TypeScript | PandaWiki 是一款 AI 大模型驱动的开源知识库搭建系统，帮助你快速构建智能化的 产品文档、技术文档、FAQ、博客系统，借助大模型的力量为你提供 A |
| [AlloyTeam/Mars](https://github.com/AlloyTeam/Mars) | 9,715 | 0.2MB | - | 腾讯移动 Web 前端知识库 |
| [GcsSloop/AndroidNote](https://github.com/GcsSloop/AndroidNote) | 9,338 | 6.9MB | Java | 安卓学习笔记 |
| [fengdu78/Data-Science-Notes](https://github.com/fengdu78/Data-Science-Notes) | 8,583 | 51.4MB | Jupyter Notebook | 数据科学的笔记以及资料搜集 |
| [lining0806/PythonSpiderNotes](https://github.com/lining0806/PythonSpiderNotes) | 7,453 | 7.2MB | Python | Python入门网络爬虫之精华版 |
| [lijin-THU/notes-python](https://github.com/lijin-THU/notes-python) | 7,147 | 11.4MB | Jupyter Notebook | 中文 Python 笔记 |
| [dair-ai/ML-Course-Notes](https://github.com/dair-ai/ML-Course-Notes) | 6,640 | 0.1MB | - | 🎓 Sharing machine learning course / lecture notes. |
| [pbek/QOwnNotes](https://github.com/pbek/QOwnNotes) | 5,842 | 751.0MB | C++ | QOwnNotes is a plain-text file notepad and todo-list manager with Markdown sup |
| [Threekiii/Awesome-POC](https://github.com/Threekiii/Awesome-POC) | 5,151 | 834.9MB | Java | 一个漏洞 PoC 知识库。A knowledge base for vulnerability PoCs(Proof of Concept),  with  |
| [Threekiii/Awesome-Redteam](https://github.com/Threekiii/Awesome-Redteam) | 4,305 | 33.1MB | Python | 一个攻防知识库。A knowledge base for red teaming and offensive security. |
| [huangruiteng/CS-Notes](https://github.com/huangruiteng/CS-Notes) | 3,975 | 751.6MB | Python | 我的自学笔记，终身更新 |
| [ZiniuLu/Python-100-Days](https://github.com/ZiniuLu/Python-100-Days) | 3,809 | 33.3MB | Python | 出处：https://github.com/jackfrued/Python-100-Days.git |
| [shovanch/fullstack-web-developer-path](https://github.com/shovanch/fullstack-web-developer-path) | 3,474 | 0.0MB | - | 📚 A learning path for Full-stack web development |
| [sjsdfg/CS-Notes-PDF](https://github.com/sjsdfg/CS-Notes-PDF) | 2,607 | 84.5MB | - | https://github.com/CyC2018/CS-Notes PDF版本离线阅读 |
| [ligurio/sqa-wiki](https://github.com/ligurio/sqa-wiki) | 2,321 | 0.4MB | - | My own notes (drafts mostly) about software quality |
| [ermongroup/cs228-notes](https://github.com/ermongroup/cs228-notes) | 2,009 | 38.3MB | SCSS | Course notes for CS228: Probabilistic Graphical Models. |
| [ArchLinuxStudio/ArchLinuxTutorial](https://github.com/ArchLinuxStudio/ArchLinuxTutorial) | 1,894 | 25.4MB | JavaScript | ✨Arch Linux安装使用教程 每日实时更新！ \| 包含ArchLinux从安装到日常使用、娱乐、编程、媒体制作的各个方面，让Arch成为你的常用系统 |
| [appbrewery/100-days-of-python](https://github.com/appbrewery/100-days-of-python) | 1,758 | 0.2MB | - | 100 Days of Code - The Complete Python Pro Bootcamp |
| [stanfordnlp/cs224n-winter17-notes](https://github.com/stanfordnlp/cs224n-winter17-notes) | 1,605 | 11.4MB | TeX | Course notes for CS224N Winter17 |
| [vasanthk/css-refresher-notes](https://github.com/vasanthk/css-refresher-notes) | 1,588 | 0.2MB | - | CSS Refresher! |
| [CodeWithHarry/100-days-of-code-youtube](https://github.com/CodeWithHarry/100-days-of-code-youtube) | 1,555 | 47.4MB | Python | Source code for 100 days of code python course on YouTube |
| [Priyanshuu-2109/GATE-CSE-notes](https://github.com/Priyanshuu-2109/GATE-CSE-notes) | 1,551 | 340.4MB | - | Handwritten notes of all the subjects in GATE CSE. |
| [yunwei37/ZJU-CS-GIS-ClassNotes](https://github.com/yunwei37/ZJU-CS-GIS-ClassNotes) | 1,444 | 117.9MB | Jupyter Notebook | 一个浙江大学本科生的计算机、地理信息科学知识库 包含课程资料 学习笔记 大作业等（ 数据结构与算法、人工智能、地理空间数据库、计算机组成、计算机网络、图形学 |
| [nushackers/notes-to-cs-freshmen-from-the-future](https://github.com/nushackers/notes-to-cs-freshmen-from-the-future) | 1,434 | 0.1MB | - | Notes to (NUS) Computer Science Freshmen, From The Future (Original by @ejames |
| … | 其余 9 个略 | | | |

### 学习路径/课程（34 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [freeCodeCamp/freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp) | 454,237 | 566.5MB | TypeScript | freeCodeCamp.org's open-source codebase and curriculum. Learn math, programmin |
| [nilbuild/developer-roadmap](https://github.com/nilbuild/developer-roadmap) | 364,806 | 354.1MB | TypeScript | Interactive roadmaps, guides and other educational content to help developers  |
| [practical-tutorials/project-based-learning](https://github.com/practical-tutorials/project-based-learning) | 279,706 | 0.5MB | Python | Curated list of project-based tutorials |
| [microsoft/ML-For-Beginners](https://github.com/microsoft/ML-For-Beginners) | 89,476 | 2181.1MB | Jupyter Notebook | 12 weeks, 26 lessons, 52 quizzes, classic Machine Learning for all |
| [MunGell/awesome-for-beginners](https://github.com/MunGell/awesome-for-beginners) | 88,479 | 0.9MB | - | A list of awesome beginners-friendly projects. |
| [Asabeneh/30-Days-Of-Python](https://github.com/Asabeneh/30-Days-Of-Python) | 71,271 | 30.6MB | Python | The 30 Days of Python programming challenge is a step-by-step guide to learn t |
| [FreeCodeCampChina/freecodecamp.cn](https://github.com/FreeCodeCampChina/freecodecamp.cn) | 37,774 | 30.2MB | CSS | FCC China open source codebase and curriculum. Learn to code and help nonprofi |
| [milanm/DevOps-Roadmap](https://github.com/milanm/DevOps-Roadmap) | 20,270 | 27.5MB | - | DevOps Roadmap for 2026. with learning resources |
| [MoienTajik/AspNetCore-Developer-Roadmap](https://github.com/MoienTajik/AspNetCore-Developer-Roadmap) | 19,632 | 90.1MB | - | Roadmap to becoming an ASP.NET Core developer in 2026 |
| [adam-golab/react-developer-roadmap](https://github.com/adam-golab/react-developer-roadmap) | 18,929 | 15.4MB | JavaScript | Roadmap to becoming a React developer |
| [darius-khll/golang-developer-roadmap](https://github.com/darius-khll/golang-developer-roadmap) | 18,425 | 32.5MB | - | Roadmap to becoming a Go developer in 2020 |
| [trekhleb/learn-python](https://github.com/trekhleb/learn-python) | 18,205 | 0.0MB | Python | 📚 Playground and cheatsheet for learning Python. Collection of Python scripts  |
| [OffcierCia/DeFi-Developer-Road-Map](https://github.com/OffcierCia/DeFi-Developer-Road-Map) | 10,806 | 2.8MB | JavaScript | DeFi Developer roadmap is a curated Developer handbook which includes a list o |
| [skydoves/android-developer-roadmap](https://github.com/skydoves/android-developer-roadmap) | 7,779 | 24.6MB | Kotlin |  🗺 The Android Developer Roadmap offers comprehensive learning paths to help y |
| [techiescamp/kubernetes-learning-path](https://github.com/techiescamp/kubernetes-learning-path) | 7,618 | 1.0MB | - | A roadmap to learn Kubernetes from scratch (Beginner to Advanced level) |
| [Elfocrash/.NET-Backend-Developer-Roadmap](https://github.com/Elfocrash/.NET-Backend-Developer-Roadmap) | 6,851 | 7.9MB | - | Roadmap for a .NET Backend Developer working with Microservices |
| [BohdanOrlov/iOS-Developer-Roadmap](https://github.com/BohdanOrlov/iOS-Developer-Roadmap) | 6,418 | 34.8MB | Swift | Roadmap to becoming an iOS developer in 2018. |
| [Xtremilicious/projectlearn-project-based-learning](https://github.com/Xtremilicious/projectlearn-project-based-learning) | 6,219 | 14.1MB | TypeScript | A curated list of project tutorials for project-based learning. |
| [utilForever/game-developer-roadmap](https://github.com/utilForever/game-developer-roadmap) | 5,774 | 11.0MB | Rust | Roadmap to becoming a game developer in 2022 |
| [onlurking/awesome-infosec](https://github.com/onlurking/awesome-infosec) | 5,717 | 0.2MB | - |  A curated list of awesome infosec courses and training resources. |
| [LaravelDaily/Laravel-Roadmap-Learning-Path](https://github.com/LaravelDaily/Laravel-Roadmap-Learning-Path) | 5,620 | 0.1MB | - |  |
| [PanXProject/awesome-certificates](https://github.com/PanXProject/awesome-certificates) | 5,545 | 3.1MB | - | Curated list of 20,000+ hours and 200+ free courses with certificates in IT, C |
| [aliyr/Nodejs-Developer-Roadmap](https://github.com/aliyr/Nodejs-Developer-Roadmap) | 4,797 | 3.9MB | - | A Developer Roadmap to becoming a Node.js developer in 2019 |
| [s4kibs4mi/java-developer-roadmap](https://github.com/s4kibs4mi/java-developer-roadmap) | 4,523 | 8.8MB | Java | Roadmap to becoming a Java developer in 2026 |
| [brootware/awesome-cyber-security-university](https://github.com/brootware/awesome-cyber-security-university) | 3,269 | 0.2MB | - | 🎓 Because Education should be free. Contributions welcome! 🕵️  |
| [conanhujinming/comments-for-awesome-courses](https://github.com/conanhujinming/comments-for-awesome-courses) | 3,228 | 0.5MB | Python | 名校公开课程评价网 |
| [luspr/awesome-ml-courses](https://github.com/luspr/awesome-ml-courses) | 3,102 | 0.0MB | - | Awesome free machine learning and AI courses with video lectures. |
| [joebew42/study-path](https://github.com/joebew42/study-path) | 2,999 | 0.6MB | - | A curated, open, and ever-evolving learning path focused on practices of softw |
| [protofire/blockchain-learning-path](https://github.com/protofire/blockchain-learning-path) | 2,674 | 0.1MB | - | A suggested learning path for blockchain development |
| [aquadzn/learn-x-by-doing-y](https://github.com/aquadzn/learn-x-by-doing-y) | 1,949 | 0.5MB | Python | 🛠️ Learn a technology X by doing a project  - Search engine of project-based l |
| [imteekay/functional-programming-learning-path](https://github.com/imteekay/functional-programming-learning-path) | 1,041 | 53.3MB | Clojure | ✨ A Learning Path for Functional Programming |
| [kevingo/system-design-primer-zh-tw](https://github.com/kevingo/system-design-primer-zh-tw) | 961 | 4.3MB | Python | system-design-primer 繁體中文翻譯計畫。原作者：https://github.com/donnemartin/system-design |
| [ossu/computer-science-br](https://github.com/ossu/computer-science-br) | 816 | 0.1MB | - | 🇧🇷 Brazilian OSSU-like Community built on the same principles of openness, inc |
| [t-miller/ossu-computer-science-progress](https://github.com/t-miller/ossu-computer-science-progress) | 460 | 0.8MB | - | Progress tracking template for the OSSU CS degree |

### 其他知识导航（35 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | 497,196 | 1.5MB | - | 😎 Awesome lists about all kinds of interesting topics |
| [vinta/awesome-python](https://github.com/vinta/awesome-python) | 314,604 | 6.0MB | Python | The definitive list that answers "I want to do X in Python, which tool should  |
| [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) | 223,830 | 16.2MB | Python | All Algorithms implemented in Python |
| [avelino/awesome-go](https://github.com/avelino/awesome-go) | 181,370 | 11.7MB | Go | A curated list of awesome Go frameworks, libraries and software |
| [521xueweihan/HelloGitHub](https://github.com/521xueweihan/HelloGitHub) | 171,506 | 8.9MB | Python | :octocat: 分享 GitHub 上有趣、入门级的开源项目。Share interesting, entry-level open source pr |
| [Hack-with-Github/Awesome-Hacking](https://github.com/Hack-with-Github/Awesome-Hacking) | 118,541 | 1.4MB | - | A collection of various awesome lists for hackers, pentesters and security res |
| [jaywcjlove/awesome-mac](https://github.com/jaywcjlove/awesome-mac) | 111,343 | 52.9MB | Swift |  This project is dedicated to collecting high-quality macOS software and orga |
| [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) | 109,048 | 2.1MB | - | A collection of DESIGN.md files analysis by popular brand design systems. Drop |
| [papers-we-love/papers-we-love](https://github.com/papers-we-love/papers-we-love) | 108,808 | 225.4MB | Shell | Papers from the computer science community to read and discuss. |
| [awesomedata/awesome-public-datasets](https://github.com/awesomedata/awesome-public-datasets) | 78,131 | 1.3MB | - | A topic-centric list of HQ open datasets. |
| [enaqx/awesome-react](https://github.com/enaqx/awesome-react) | 74,313 | 2.5MB | - | A collection of awesome things regarding React ecosystem |
| [binhnguyennus/awesome-scalability](https://github.com/binhnguyennus/awesome-scalability) | 73,358 | 1.6MB | - | The Patterns of Scalable, Reliable, and Performant Large-Scale Systems |
| [fffaraz/awesome-cpp](https://github.com/fffaraz/awesome-cpp) | 72,811 | 2.6MB | - | A curated list of awesome C++ (or C) frameworks, libraries, resources, and shi |
| [tldr-pages/tldr](https://github.com/tldr-pages/tldr) | 63,416 | 59.9MB | Markdown | Collaborative cheatsheets for console commands 📚. |
| [LeCoupa/awesome-cheatsheets](https://github.com/LeCoupa/awesome-cheatsheets) | 46,369 | 8.7MB | JavaScript | 👩‍💻👨‍💻 Awesome cheatsheets for popular programming languages, frameworks and d |
| [OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries) | 32,919 | 2395.9MB | Python | The OWASP Cheat Sheet Series was created to provide a concise collection of hi |
| [Igglybuff/awesome-piracy](https://github.com/Igglybuff/awesome-piracy) | 26,924 | 2.1MB | HTML | A curated list of awesome warez and piracy links |
| [denisidoro/navi](https://github.com/denisidoro/navi) | 17,452 | 1.6MB | Rust | An interactive cheatsheet tool for the command-line |
| [ramitsurana/awesome-kubernetes](https://github.com/ramitsurana/awesome-kubernetes) | 16,054 | 7.2MB | Shell | A curated list for awesome kubernetes sources :ship::tada: |
| [trimstray/nginx-admins-handbook](https://github.com/trimstray/nginx-admins-handbook) | 14,305 | 80.3MB | Shell | How to improve NGINX performance, security, and other important things. |
| [cheat/cheat](https://github.com/cheat/cheat) | 13,429 | 10.2MB | Go | cheat allows you to create and view interactive cheatsheets on the command-lin |
| [pingcap/awesome-database-learning](https://github.com/pingcap/awesome-database-learning) | 10,957 | 0.1MB | - | A list of learning materials to understand databases internals |
| [Fechin/reference](https://github.com/Fechin/reference) | 10,785 | 69.6MB | EJS | ⭕ Share quick reference cheat sheet for developers. |
| [aalhour/awesome-compilers](https://github.com/aalhour/awesome-compilers) | 9,864 | 0.3MB | - | :sunglasses: Curated list of awesome resources on Compilers, Interpreters and  |
| [matter-labs/awesome-zero-knowledge-proofs](https://github.com/matter-labs/awesome-zero-knowledge-proofs) | 5,802 | 0.2MB | - | A curated list of awesome things related to learning Zero-Knowledge Proofs (ZK |
| [sshuair/awesome-gis](https://github.com/sshuair/awesome-gis) | 5,483 | 0.5MB | - | 😎Awesome GIS is a collection of geospatial related sources, including cartogra |
| [ChristianLempa/cheat-sheets](https://github.com/ChristianLempa/cheat-sheets) | 4,810 | 0.4MB | - | This is my personal knowledge-base. Here you'll find code-snippets, technical  |
| [AlexAnys/awesome-openclaw-usecases-zh](https://github.com/AlexAnys/awesome-openclaw-usecases-zh) | 4,421 | 0.6MB | - | 🇨🇳 OpenClaw中文用例大全 \| 50个真实场景 \| 国内特色 + 海外案例的国内适配 \| 自动化办公·内容创作·运维·AI助理·知识管理 \| |
| [StephenGrider/ReduxSimpleStarter](https://github.com/StephenGrider/ReduxSimpleStarter) | 3,531 | 0.1MB | JavaScript | Starter pack for an awesome Udemy course |
| [mariuszgil/awesome-eventstorming](https://github.com/mariuszgil/awesome-eventstorming) | 2,389 | 6.0MB | - | Awesome EventStorming |
| [MarcSkovMadsen/awesome-streamlit](https://github.com/MarcSkovMadsen/awesome-streamlit) | 2,282 | 117.6MB | HTML | The purpose of this project is to share knowledge on how awesome Streamlit is  |
| [kdeldycke/awesome-iam](https://github.com/kdeldycke/awesome-iam) | 2,256 | 1.6MB | - | 👤 Identity and Access Management knowledge for cloud platforms |
| [f2e-awesome/knowledge](https://github.com/f2e-awesome/knowledge) | 1,962 | 11.7MB | JavaScript | 文档着重构建一个完整的「前端技术架构图谱」，方便 F2E(Front End Engineering又称FEE、F2E) 学习与进阶。 |
| [cyb3rxp/awesome-soc](https://github.com/cyb3rxp/awesome-soc) | 1,800 | 23.2MB | - | A curated knowledge base to build, run and mature a SOC (including CSIRT). |
| [SpaceLearner/Awesome-DynamicGraphLearning](https://github.com/SpaceLearner/Awesome-DynamicGraphLearning) | 710 | 0.2MB | Shell | Awesome papers about machine learning (deep learning) on dynamic (temporal) gr |

### 其他（66 个）

| 仓库 | ★Star | 体积 | 说明 |
|:-----|:-----:|:----:|:-----|
| [DigitalPlatDev/FreeDomain](https://github.com/DigitalPlatDev/FreeDomain) | 194,079 | 1.1MB | Free domain registration and practical DNS learning resources for everyone. |
| [getify/You-Dont-Know-JS](https://github.com/getify/You-Dont-Know-JS) | 184,705 | 14.9MB | A book series (2 published editions) on the JS language. |
| [Chalarangelo/30-seconds-of-code](https://github.com/Chalarangelo/30-seconds-of-code) | 128,732 | 725.8MB | Coding articles to level up your development skills |
| [ruvnet/RuView](https://github.com/ruvnet/RuView) | 90,598 | 186.4MB | π RuView turns commodity WiFi signals into real-time spatial intelligence, vit |
| [fighting41love/funNLP](https://github.com/fighting41love/funNLP) | 82,523 | 170.1MB | 中英文敏感词、语言检测、中外手机/电话归属地/运营商查询、名字推断性别、手机号抽取、身份证抽取、邮箱抽取、中日文人名库、中文缩写库、拆字词典、词汇情感值、停 |
| [charlax/professional-programming](https://github.com/charlax/professional-programming) | 51,429 | 4.6MB | A collection of learning resources for curious software engineers |
| [dylanaraps/pure-bash-bible](https://github.com/dylanaraps/pure-bash-bible) | 41,718 | 0.2MB | 📖 A collection of pure bash alternatives to external processes. |
| [outline/outline](https://github.com/outline/outline) | 40,228 | 322.0MB | The fastest knowledge base for growing teams. Beautiful, realtime collaborativ |
| [denysdovhan/wtfjs](https://github.com/denysdovhan/wtfjs) | 37,677 | 1.5MB | 🤪 A list of funny and tricky JavaScript examples |
| [carbon-app/carbon](https://github.com/carbon-app/carbon) | 36,087 | 20.6MB | :black_heart: Create and share beautiful images of your source code |
| [JushBJJ/Mr.-Ranedeer-AI-Tutor](https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor) | 29,598 | 0.3MB | A GPT-4 AI Tutor Prompt for customizable personalized learning experiences. |
| [wuyouzhuguli/SpringAll](https://github.com/wuyouzhuguli/SpringAll) | 28,951 | 1.0MB | 循序渐进，学习Spring Boot、Spring Boot & Shiro、Spring Batch、Spring Cloud、Spring Cloud  |
| [harvard-edge/cs249r_book](https://github.com/harvard-edge/cs249r_book) | 27,950 | 2740.6MB | Machine Learning Systems |
| [zhaoxuya520/reverse-skill](https://github.com/zhaoxuya520/reverse-skill) | 26,184 | 3.8MB | Reverse Engineering / Authorized Penetration Testing / Security Research Skill |
| [ssloy/tinyrenderer](https://github.com/ssloy/tinyrenderer) | 24,106 | 62.5MB | A brief computer graphics / rendering course |
| [processing/p5.js](https://github.com/processing/p5.js) | 23,881 | 176.2MB | p5.js is a client-side JS platform that empowers artists, designers, students, |
| [virgiliojr94/book-to-skill](https://github.com/virgiliojr94/book-to-skill) | 22,703 | 1.9MB | Turn any technical book PDF into a Claude Code skill — ready to study, referen |
| [FallibleInc/security-guide-for-developers](https://github.com/FallibleInc/security-guide-for-developers) | 21,093 | 5.9MB | Security Guide for Developers |
| [jantic/DeOldify](https://github.com/jantic/DeOldify) | 18,483 | 69.7MB | A Deep Learning based project for colorizing and restoring old images (and vid |
| [xournalpp/xournalpp](https://github.com/xournalpp/xournalpp) | 15,250 | 68.5MB | Xournal++ is a handwriting notetaking software with PDF annotation support. Wr |
| [haiwen/seafile](https://github.com/haiwen/seafile) | 15,138 | 12.1MB | Beyond file syncing and sharing, a new way to organize your files with extensi |
| [virgili0/Virgilio](https://github.com/virgili0/Virgilio) | 14,944 | 33.1MB | Your new Mentor for Data Science E-Learning. |
| [seaswalker/spring-analysis](https://github.com/seaswalker/spring-analysis) | 13,749 | 4.8MB | Spring源码阅读 |
| [primer/css](https://github.com/primer/css) | 13,003 | 37.8MB | Primer is GitHub's design system. This is the CSS implementation |
| [trimstray/test-your-sysadmin-skills](https://github.com/trimstray/test-your-sysadmin-skills) | 11,835 | 1.1MB | A collection of Linux Sysadmin Test Questions and Answers. Test your knowledge |


### 2026-08-22 补充调研清单（535 个精选，star≥800 非工具）

> 第二批 52 组检索式新增（详见 §5），与原 353 个合并去重后共 722 个；此处为精选 532 个的补充清单，完整数据见 import/github-knowledge-survey-2026-08-22/all_items.json。


#### 补充类别：awesome-other（71 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [sindresorhus/awesome-nodejs](https://github.com/sindresorhus/awesome-nodejs) | 66,586 | 1.5 | - | :zap: Delightful Node.js packages and resources [BECAUSE OF TOO MUCH SPAM AND LOW-QUALITY SUBMISSION |
| [Solido/awesome-flutter](https://github.com/Solido/awesome-flutter) | 60,973 | 3.5 | Dart | An awesome list that curates the best Flutter libraries, tools, tutorials, articles and more. |
| [rust-unofficial/awesome-rust](https://github.com/rust-unofficial/awesome-rust) | 58,928 | 9.8 | Rust | A curated list of Rust code and resources. |
| [wasabeef/awesome-android-ui](https://github.com/wasabeef/awesome-android-ui) | 57,272 | 851.3 | - | A curated list of awesome Android UI/UX libraries |
| [vsouza/awesome-ios](https://github.com/vsouza/awesome-ios) | 53,125 | 16.9 | Swift | A curated list of awesome iOS ecosystem, including Objective-C and Swift Projects  |
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | 52,105 | 2.2 | - | The awesome collection of OpenClaw skills. 5,400+ skills filtered and categorized from the official  |
| [dkhamsing/open-source-ios-apps](https://github.com/dkhamsing/open-source-ios-apps) | 51,798 | 33.3 | - | :iphone: Collaborative List of Open-Source iOS Apps |
| [serhii-londar/open-source-mac-os-apps](https://github.com/serhii-londar/open-source-mac-os-apps) | 50,119 | 5.8 | - | 🚀 Awesome list of open source applications for macOS. https://t.me/s/opensourcemacosapps |
| [akullpp/awesome-java](https://github.com/akullpp/awesome-java) | 48,811 | 3.4 | - | A curated list of awesome frameworks, libraries and software for the Java programming language. |
| [brillout/awesome-react-components](https://github.com/brillout/awesome-react-components) | 48,241 | 1.3 | - | Curated List of React Components & Libraries. |
| [lukasz-madon/awesome-remote-job](https://github.com/lukasz-madon/awesome-remote-job) | 47,873 | 1.1 | - | A curated list of awesome remote jobs and resources. Inspired by https://github.com/vinta/awesome-py |
| [docker/awesome-compose](https://github.com/docker/awesome-compose) | 46,144 | 11.3 | HTML | Awesome Docker Compose samples |
| [goabstract/Awesome-Design-Tools](https://github.com/goabstract/Awesome-Design-Tools) | 40,955 | 18.8 | JavaScript | The best design tools and plugins for everything 👉 |
| [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | 40,634 | 2.9 | JavaScript | 📄  Configuration files that enhance Cursor AI editor experience with custom rules and behaviors |
| [deepseek-ai/awesome-deepseek-integration](https://github.com/deepseek-ai/awesome-deepseek-integration) | 38,906 | 78.3 | - | Integrate the DeepSeek API into popular software |
| [alebcay/awesome-shell](https://github.com/alebcay/awesome-shell) | 37,478 | 0.6 | - | A curated list of awesome command-line frameworks, toolkits, guides and gizmos. Inspired by awesome- |
| [ziadoz/awesome-php](https://github.com/ziadoz/awesome-php) | 32,666 | 1.4 | - | A curated list of amazingly awesome PHP libraries, resources and shiny things. |
| [ascoders/weekly](https://github.com/ascoders/weekly) | 31,078 | 8.6 | JavaScript | 前端精读周刊。帮你理解最前沿、实用的技术。 |
| [abhisheknaiidu/awesome-github-profile-readme](https://github.com/abhisheknaiidu/awesome-github-profile-readme) | 30,879 | 12.4 | - | 😎 A curated list of awesome GitHub Profile which updates in real time  |
| [herrbischoff/awesome-macos-command-line](https://github.com/herrbischoff/awesome-macos-command-line) | 30,842 | 0.0 | - | Use your macOS terminal shell to do awesome things. |
| [AllThingsSmitty/css-protips](https://github.com/AllThingsSmitty/css-protips) | 30,253 | 7.2 | - | ⚡️ A collection of tips to help take your CSS skills pro 🦾 |
| [imDazui/Tvlist-awesome-m3u-m3u8](https://github.com/imDazui/Tvlist-awesome-m3u-m3u8) | 29,899 | 1.5 | - | 直播源相关资源汇总 📺 💯 IPTV、M3U —— 勤洗手、戴口罩，祝愿所有人百毒不侵 |
| [viatsko/awesome-vscode](https://github.com/viatsko/awesome-vscode) | 28,965 | 10.7 | JavaScript | 🎨 A curated list of delightful VS Code packages and resources. |
| [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV) | 28,341 | 16.9 | TeX | :page_facing_up: Awesome CV is LaTeX template for your outstanding job application |
| [ashishps1/awesome-low-level-design](https://github.com/ashishps1/awesome-low-level-design) | 26,287 | 15.6 | Java | Learn Low Level Design (LLD) and prepare for interviews using free resources. |
| [alexpate/awesome-design-systems](https://github.com/alexpate/awesome-design-systems) | 25,760 | 0.4 | - | 💅🏻 ⚒ A collection of awesome design systems |
| [kahun/awesome-sysadmin](https://github.com/kahun/awesome-sysadmin) | 24,351 | 0.6 | - | A curated list of amazingly awesome open source sysadmin resources inspired by Awesome PHP. |
| [ashishps1/awesome-leetcode-resources](https://github.com/ashishps1/awesome-leetcode-resources) | 17,694 | 0.2 | Java | Awesome LeetCode resources to learn Data Structures and Algorithms and prepare for Coding Interviews |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | 14,765 | 0.0 | - | A curated list of awesome Claude Skills, resources, and tools for customizing Claude AI workflows —  |
| [taowen/awesome-lowcode](https://github.com/taowen/awesome-lowcode) | 14,713 | 2.2 | - | 国内低代码平台从业者交流 |
| [neutraltone/awesome-stock-resources](https://github.com/neutraltone/awesome-stock-resources) | 14,445 | 0.8 | Ruby | :city_sunrise: A collection of links for free stock photography, video and Illustration websites |
| [markets/awesome-ruby](https://github.com/markets/awesome-ruby) | 14,141 | 3.1 | - | 💎 A collection of awesome Ruby libraries, tools, frameworks and software |
| [lnishan/awesome-competitive-programming](https://github.com/lnishan/awesome-competitive-programming) | 14,132 | 6.9 | - | :gem: A curated list of awesome Competitive Programming, Algorithm and Data Structure resources |
| [bolshchikov/js-must-watch](https://github.com/bolshchikov/js-must-watch) | 13,605 | 0.1 | - | Must-watch videos about javascript |
| [alexandresanlim/Badges4-README.md-Profile](https://github.com/alexandresanlim/Badges4-README.md-Profile) | 13,413 | 2.0 | Markdown | :octocat: Improve your README.md profile with these amazing badges. |
| [YouMind-OpenLab/awesome-nano-banana-pro-prompts](https://github.com/YouMind-OpenLab/awesome-nano-banana-pro-prompts) | 13,252 | 355.9 | TypeScript | 🍌 World's largest Nano Banana Pro prompt library — 10,000+ curated prompts with preview images, 16 l |
| [phanan/htaccess](https://github.com/phanan/htaccess) | 13,180 | 0.2 | - | ✂A collection of useful .htaccess snippets. |
| [nestjs/awesome-nestjs](https://github.com/nestjs/awesome-nestjs) | 13,110 | 0.4 | - | A curated list of awesome things related to NestJS 😎 |
| [TonnyL/Awesome_APIs](https://github.com/TonnyL/Awesome_APIs) | 13,080 | 0.5 | - | :octocat: A collection of APIs |
| [rShetty/awesome-podcasts](https://github.com/rShetty/awesome-podcasts) | 13,077 | 0.8 | - | Collection of awesome podcasts |
| [m3y54m/Embedded-Engineering-Roadmap](https://github.com/m3y54m/Embedded-Engineering-Roadmap) | 12,893 | 3.8 | - | Comprehensive roadmap for aspiring Embedded Systems Engineers, featuring a curated list of learning  |
| [humiaozuzu/awesome-flask](https://github.com/humiaozuzu/awesome-flask) | 12,751 | 0.2 | - | A curated list of awesome Flask resources and plugins |
| [heynickc/awesome-ddd](https://github.com/heynickc/awesome-ddd) | 12,334 | 0.7 | - | A curated list of Domain-Driven Design (DDD), Command Query Responsibility Segregation (CQRS), Event |
| [JStumpp/awesome-android](https://github.com/JStumpp/awesome-android) | 12,292 | 0.6 | - | A curated list of awesome Android packages and resources. |
| [mezod/awesome-indie](https://github.com/mezod/awesome-indie) | 11,718 | 0.1 | - | Resources for independent developers to make money |
| [ai-boost/awesome-prompts](https://github.com/ai-boost/awesome-prompts) | 8,737 | 3.3 | - | Curated list of chatgpt prompts from the top-rated GPTs in the GPTs Store. Prompt Engineering, promp |
| [jobbole/awesome-go-cn](https://github.com/jobbole/awesome-go-cn) | 7,378 | 0.7 | - | Go 资源大全中文版， 内容包括：Web框架、模板引擎、表单、身份认证、数据库、ORM框架、图片处理、文本处理、自然语言处理、机器学习、日志、代码分析、教程和（电子）书等。由「开源前哨」和「Go开发大 |
| [shekhargulati/52-technologies-in-2016](https://github.com/shekhargulati/52-technologies-in-2016) | 7,320 | 63.4 | JavaScript | Let's learn a new technology every week. A new technology blog every Sunday in 2016. |
| [liuchong/awesome-roadmaps](https://github.com/liuchong/awesome-roadmaps) | 7,230 | 0.1 | - | A curated list of roadmaps. |
| [facundoolano/software-papers](https://github.com/facundoolano/software-papers) | 6,573 | 0.3 | Python | 📚 A curated list of papers for Software Engineers |
| [micromata/awesome-javascript-learning](https://github.com/micromata/awesome-javascript-learning) | 5,840 | 0.3 | - | A tiny list limited to the best JavaScript Learning Resources |
| [xialeiliu/Awesome-Incremental-Learning](https://github.com/xialeiliu/Awesome-Incremental-Learning) | 4,513 | 0.4 | - | Awesome Incremental Learning |
| [0voice/Campus_recruitment_interview_questions](https://github.com/0voice/Campus_recruitment_interview_questions) | 4,026 | 1.2 | - | 2025 最新校招面试题合集， 面向 2026 届应届生，全网最全整理！收录 1000+道真实面试题以及面经，涵盖阿里、腾讯、字节、美团、百度、华为、小米、英伟达、微软、米哈游等百家大中小厂。每题配备 |
| [micromata/awesome-css-learning](https://github.com/micromata/awesome-css-learning) | 3,849 | 0.4 | - | A tiny list limited to the best CSS Learning Resources |
| [huyingjie/Checklist-Checklist](https://github.com/huyingjie/Checklist-Checklist) | 2,961 | 1.5 | JavaScript | 🌈  A Curated List of Checklists ✔︎✔︎ |
| [YanjieZe/awesome-humanoid-robot-learning](https://github.com/YanjieZe/awesome-humanoid-robot-learning) | 2,707 | 1.3 | Python | A Paper List for Humanoid Robot Learning. |
| [wwxFromTju/awesome-reinforcement-learning-zh](https://github.com/wwxFromTju/awesome-reinforcement-learning-zh) | 2,190 | 25.8 | - | 中文整理的强化学习资料（Reinforcement Learning） |
| [wx-chevalier/Awesome-Books-Notes](https://github.com/wx-chevalier/Awesome-Books-Notes) | 2,180 | 13.1 | HTML | :books: Awesome CS Books(with Digests)/Series(.pdf by git lfs) Warehouse for Geeks, ProgrammingLangu |
| [shahednasser/awesome-resources](https://github.com/shahednasser/awesome-resources) | 1,958 | 1.1 | HTML | :sunglasses: List of helpful resources added by the community for the community! |
| [androiddevnotes/awesome-android-learning-resources](https://github.com/androiddevnotes/awesome-android-learning-resources) | 1,939 | 0.3 | Kotlin | 👓 A curated list of awesome android learning resources for android app developers.  |
| [artix41/awesome-transfer-learning](https://github.com/artix41/awesome-transfer-learning) | 1,776 | 0.2 | - | Best transfer learning and domain adaptation resources (papers, tutorials, datasets, etc.) |
| [lyfeyaj/awesome-resources](https://github.com/lyfeyaj/awesome-resources) | 1,742 | 0.4 | HTML | Awesome resources for coding and learning: open source projects, websites, books e.g. |
| [jackwener/CS-Awesome-Courses](https://github.com/jackwener/CS-Awesome-Courses) | 1,634 | 0.1 | - | 计算机的优秀课程 |
| [0voice/Awesome_c-cpp_Projects](https://github.com/0voice/Awesome_c-cpp_Projects) | 1,411 | 0.8 | C++ | 2025年 最新收录整理 500+ 个高质量的 C/C++ 项目，包括但不限于核心开发、基础工具、系统与并发、系统编程、图形处理、网络通信、数据处理、应用框架、开源工具、嵌入式开发等多个领域。适合学习 |
| [0voice/awesome_audio_video_learning](https://github.com/0voice/awesome_audio_video_learning) | 1,159 | 170.5 | - | 2025年音视频开发最新总结，提供全面的音视频开发学习资源，涵盖从基础知识到实战项目的资料、论文、书籍、项目和示例，帮助你快速热门并逐步进阶，持续更新维护中！ |
| [0xalpharush/awesome-MEV-resources](https://github.com/0xalpharush/awesome-MEV-resources) | 1,155 | 0.0 | - | Get up to speed on Maximum Extractable Value |
| [0voice/Awesome-QuantDev-Learn](https://github.com/0voice/Awesome-QuantDev-Learn) | 1,059 | 0.2 | - | 本仓库面向所有对量化分析或开发感兴趣的量化交易从业者，提供系统性学习量化开发的技术路线，从数据获取、策略开发、回测系统到实盘部署。 |
| [0voice/Awesome_Qt_Learning](https://github.com/0voice/Awesome_Qt_Learning) | 938 | 353.0 | - | 2025年 qt 开发最新总结，提供全面的 qt 开发学习资源，涵盖从基础知识到实战项目的资料、文献、书籍、项目和示例，帮助你快速入门并逐步进阶，持续更新维护中！ |
| [jbranchaud/awesome-react-design-systems](https://github.com/jbranchaud/awesome-react-design-systems) | 936 | 0.0 | - | A collection of awesome React-based design systems |
| [klaufel/awesome-design-systems](https://github.com/klaufel/awesome-design-systems) | 882 | 0.2 | - | 📒 A curated list of bookmarks, resources and articles about design systems focused on developers. |
| [ChessMax/awesome-programming-languages](https://github.com/ChessMax/awesome-programming-languages) | 828 | 2.5 | Markdown | The list of awesome programming languages that you might be interested in. |

#### 补充类别：awesome-ai（61 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [josephmisiti/awesome-machine-learning](https://github.com/josephmisiti/awesome-machine-learning) | 74,102 | 2.6 | Python | A curated list of awesome Machine Learning frameworks, libraries and software. |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | 38,110 | 102.2 | Python | Community-contributed instructions, agents, skills, and configurations to help you make the most of  |
| [ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code](https://github.com/ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code) | 36,441 | 0.9 | - | 500 AI Machine learning Deep learning Computer vision NLP Projects with code |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 30,774 | 0.8 | - | A curated collection of 1000+ agent skills from official dev teams and the community, compatible wit |
| [e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) | 29,609 | 115.2 | - | A list of AI autonomous agents |
| [wilsonfreitas/awesome-quant](https://github.com/wilsonfreitas/awesome-quant) | 29,036 | 7.3 | HTML | A curated list of insanely awesome libraries, packages and resources for Quants (Quantitative Financ |
| [aishwaryanr/awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide) | 28,849 | 173.9 | HTML | A one stop repository for generative AI research updates, interview resources, notebooks and much mo |
| [Hannibal046/Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM) | 27,274 | 14.2 | - | Awesome-LLM: a curated list of Large Language Model |
| [AiHubCN/Awesome-Chinese-LLM](https://github.com/AiHubCN/Awesome-Chinese-LLM) | 22,747 | 11.3 | - | 整理开源的中文大语言模型，以规模较小、可私有化部署、训练成本较低的模型为主，包括底座模型，垂直领域微调及应用，数据集与教程等。 |
| [EthicalML/awesome-production-machine-learning](https://github.com/EthicalML/awesome-production-machine-learning) | 20,858 | 2.9 | - | A curated list of awesome open source libraries to deploy, monitor, version and scale your machine l |
| [chiraggude/awesome-laravel](https://github.com/chiraggude/awesome-laravel) | 13,097 | 1.3 | - | A curated list of bookmarks, packages, tutorials, videos and other cool resources from the Laravel e |
| [steven2358/awesome-generative-ai](https://github.com/steven2358/awesome-generative-ai) | 12,525 | 0.5 | - | A curated list of modern Generative Artificial Intelligence projects and services |
| [WangRongsheng/awesome-LLM-resources](https://github.com/WangRongsheng/awesome-LLM-resources) | 8,857 | 66.9 | - | 🧑‍🚀 全世界最好的LLM资料总结（多模态生成、Agent、辅助编程、AI审稿、数据处理、模型训练、模型推理、o1 模型、MCP、小语言模型、视觉语言模型） / Summary of the worl |
| [hijkzzz/Awesome-LLM-Strawberry](https://github.com/hijkzzz/Awesome-LLM-Strawberry) | 6,900 | 1.8 | - | A collection of LLM papers, blogs, and projects, with a focus on OpenAI o1 🍓 and reasoning technique |
| [src-d/awesome-machine-learning-on-source-code](https://github.com/src-d/awesome-machine-learning-on-source-code) | 6,630 | 0.7 | - | Cool links & research papers related to Machine Learning applied to source code (MLonCode) |
| [wgwang/awesome-LLMs-In-China](https://github.com/wgwang/awesome-LLMs-In-China) | 6,471 | 4.5 | - | 中国大模型 |
| [jason718/awesome-self-supervised-learning](https://github.com/jason718/awesome-self-supervised-learning) | 6,412 | 0.4 | - | A curated list of awesome self-supervised methods |
| [tensorchord/Awesome-LLMOps](https://github.com/tensorchord/Awesome-LLMOps) | 5,917 | 1.0 | Shell | An awesome & curated list of best LLMOps tools for developers |
| [lauragift21/awesome-learning-resources](https://github.com/lauragift21/awesome-learning-resources) | 5,758 | 0.4 | - | 🔥 Awesome list of resources on Web Development. |
| [xlite-dev/Awesome-LLM-Inference](https://github.com/xlite-dev/Awesome-LLM-Inference) | 5,471 | 117.3 | Python | 📚A curated list of Awesome LLM/VLM Inference Papers with Codes: Flash-Attention, Paged-Attention, WI |
| [armankhondker/awesome-ai-ml-resources](https://github.com/armankhondker/awesome-ai-ml-resources) | 4,563 | 0.1 | - | Learn AI/ML for beginners with a roadmap and free resources.  |
| [jobbole/awesome-machine-learning-cn](https://github.com/jobbole/awesome-machine-learning-cn) | 4,483 | 0.1 | - | 机器学习资源大全中文版，包括机器学习领域的框架、库以及软件 |
| [GT-RIPL/Awesome-LLM-Robotics](https://github.com/GT-RIPL/Awesome-LLM-Robotics) | 4,454 | 0.3 | - | A comprehensive list of papers using large language/multi-modal models for Robotics/RL, including pa |
| [jphall663/awesome-machine-learning-interpretability](https://github.com/jphall663/awesome-machine-learning-interpretability) | 4,061 | 1.5 | - | A curated list of awesome responsible machine learning resources. |
| [grananqvist/Awesome-Quant-Machine-Learning-Trading](https://github.com/grananqvist/Awesome-Quant-Machine-Learning-Trading) | 3,991 | 0.0 | - | Quant/Algorithm trading resources with an emphasis on Machine Learning |
| [atfortes/Awesome-LLM-Reasoning](https://github.com/atfortes/Awesome-LLM-Reasoning) | 3,673 | 0.3 | - | From Chain-of-Thought prompting to OpenAI o1 and DeepSeek-R1 🍓 |
| [liyupi/free-programming-resources](https://github.com/liyupi/free-programming-resources) | 3,665 | 0.2 | HTML | 2026 年最新的免费编程资源大全，持续更新！🔥 覆盖各种语言和方向（Java / Python / C++ / JavaScript / TypeScript / Golang / 前端 / 后端  |
| [codefuse-ai/Awesome-Code-LLM](https://github.com/codefuse-ai/Awesome-Code-LLM) | 3,430 | 11.3 | - | [TMLR] A curated list of language modeling researches for code (and other software engineering activ |
| [yunlong10/Awesome-LLMs-for-Video-Understanding](https://github.com/yunlong10/Awesome-LLMs-for-Video-Understanding) | 3,269 | 13.5 | - | 🔥🔥🔥 [IEEE TCSVT] Latest Papers, Codes and Datasets on Vid-LLMs. |
| [weiaicunzai/awesome-image-classification](https://github.com/weiaicunzai/awesome-image-classification) | 3,062 | 0.0 | - | A curated list of deep learning image classification papers and codes |
| [rafska/awesome-local-llm](https://github.com/rafska/awesome-local-llm) | 2,678 | 0.4 | - | A curated list of awesome platforms, tools, practices and resources that helps run LLMs locally |
| [RManLuo/Awesome-LLM-KG](https://github.com/RManLuo/Awesome-LLM-KG) | 2,613 | 1.5 | - | Awesome papers about unifying LLMs and KGs |
| [DEEP-PolyU/Awesome-GraphRAG](https://github.com/DEEP-PolyU/Awesome-GraphRAG) | 2,604 | 11.2 | - | Awesome-GraphRAG: A curated list of resources (surveys, papers, benchmarks, and opensource projects) |
| [guyulongcs/Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising](https://github.com/guyulongcs/Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising) | 2,585 | 1120.9 | Python | Awesome Deep Learning papers for industrial Search, Recommendation and Advertisement. They focus on  |
| [luban-agi/Awesome-Domain-LLM](https://github.com/luban-agi/Awesome-Domain-LLM) | 2,580 | 1.1 | - | 收集和梳理垂直领域的开源模型、数据集及评测基准。 |
| [mbzuai-oryx/Awesome-LLM-Post-training](https://github.com/mbzuai-oryx/Awesome-LLM-Post-training) | 2,523 | 3.0 | Python | Awesome Reasoning LLM Tutorial/Survey/Guide |
| [XiaoxinHe/Awesome-Graph-LLM](https://github.com/XiaoxinHe/Awesome-Graph-LLM) | 2,447 | 0.2 | - | A collection of AWESOME things about Graph-Related LLMs. |
| [WLiK/LLM4Rec-Awesome-Papers](https://github.com/WLiK/LLM4Rec-Awesome-Papers) | 2,305 | 1.2 | - | A list of awesome papers and resources of recommender system on large language model (LLM). |
| [vaaaaanquish/Awesome-Rust-MachineLearning](https://github.com/vaaaaanquish/Awesome-Rust-MachineLearning) | 2,266 | 30.8 | JavaScript | This repository is a list of machine learning libraries written in Rust. It's a compilation of GitHu |
| [Jason2Brownlee/awesome-llm-books](https://github.com/Jason2Brownlee/awesome-llm-books) | 2,258 | 0.4 | - | Awesome LLM Books: Curated list of books on Large Language Models |
| [hyp1231/awesome-llm-powered-agent](https://github.com/hyp1231/awesome-llm-powered-agent) | 2,253 | 0.2 | - | Awesome things about LLM-powered agents. Papers / Repos / Blogs / ... |
| [ActiveVisionLab/Awesome-LLM-3D](https://github.com/ActiveVisionLab/Awesome-LLM-3D) | 2,251 | 14.4 | - | Awesome-LLM-3D: a curated list of Multi-modal Large Language Model in 3D world  Resources |
| [slavakurilyak/awesome-ai-agents](https://github.com/slavakurilyak/awesome-ai-agents) | 2,185 | 0.9 | Python | Awesome list of 300+ agentic AI resources |
| [imaurer/awesome-llm-json](https://github.com/imaurer/awesome-llm-json) | 2,173 | 0.2 | - | Resource list for generating JSON using LLMs via function calling, tools, CFG. Libraries, Models, No |
| [Xnhyacinth/Awesome-LLM-Long-Context-Modeling](https://github.com/Xnhyacinth/Awesome-LLM-Long-Context-Modeling) | 2,163 | 1.0 | - | 📰 Must-read papers and blogs on LLM based Long Context Modeling 🔥 |
| [horseee/Awesome-Efficient-LLM](https://github.com/horseee/Awesome-Efficient-LLM) | 2,036 | 66.2 | Python | A curated list for Efficient Large Language Models |
| [jim-schwoebel/awesome_ai_agents](https://github.com/jim-schwoebel/awesome_ai_agents) | 1,949 | 8.6 | - | 🤖 A comprehensive list of 1,500+ resources and tools related to AI agents. |
| [yenchenlin/awesome-adversarial-machine-learning](https://github.com/yenchenlin/awesome-adversarial-machine-learning) | 1,909 | 0.0 | - | A curated list of awesome adversarial machine learning resources |
| [ydyjya/Awesome-LLM-Safety](https://github.com/ydyjya/Awesome-LLM-Safety) | 1,901 | 8.3 | HTML | A curated list of safety-related papers, articles, and resources focused on Large Language Models (L |
| [Thinklab-SJTU/Awesome-LLM4AD](https://github.com/Thinklab-SJTU/Awesome-LLM4AD) | 1,891 | 2.6 | - | A curated list of awesome LLM/VLM/VLA/World Model for Autonomous Driving(LLM4AD) resources (continua |
| [HHHHHejia/Awesome-AgenticLLM-RL-Papers](https://github.com/HHHHHejia/Awesome-AgenticLLM-RL-Papers) | 1,874 | 0.1 | - |  |
| [HuangOwen/Awesome-LLM-Compression](https://github.com/HuangOwen/Awesome-LLM-Compression) | 1,863 | 1.2 | - | Awesome LLM compression research papers and tools. |
| [guillaume-chevalier/Awesome-Deep-Learning-Resources](https://github.com/guillaume-chevalier/Awesome-Deep-Learning-Resources) | 1,814 | 0.3 | - | Rough list of my favorite deep learning resources, useful for revisiting topics or for reference. I  |
| [zwang4/awesome-machine-learning-in-compilers](https://github.com/zwang4/awesome-machine-learning-in-compilers) | 1,686 | 0.6 | - | Must read research papers and links to tools and datasets that are related to using machine learning |
| [lizhe2004/Awesome-LLM-RAG-Application](https://github.com/lizhe2004/Awesome-LLM-RAG-Application) | 1,650 | 94.3 | - | the resources about the application based on LLM with RAG pattern |
| [caramaschiHG/awesome-ai-agents-2026](https://github.com/caramaschiHG/awesome-ai-agents-2026) | 1,599 | 0.1 | - | 🤖 The most comprehensive list of AI agents, frameworks & tools in 2026. 300+ resources · 20+ categor |
| [Danielskry/Awesome-RAG](https://github.com/Danielskry/Awesome-RAG) | 1,345 | 0.2 | - | 😎 Awesome list of Retrieval-Augmented Generation (RAG) applications in Generative AI. |
| [jxzhangjhu/Awesome-LLM-RAG](https://github.com/jxzhangjhu/Awesome-LLM-RAG) | 1,343 | 0.1 | - | Awesome-LLM-RAG: a curated list of advanced retrieval augmented generation (RAG) in Large Language M |
| [AgenticHealthAI/Awesome-AI-Agents-for-Healthcare](https://github.com/AgenticHealthAI/Awesome-AI-Agents-for-Healthcare) | 1,219 | 3.2 | - | Latest Advances on Agentic AI & AI Agents for Healthcare |
| [Jenqyang/Awesome-AI-Agents](https://github.com/Jenqyang/Awesome-AI-Agents) | 1,217 | 3.4 | CSS | A collection of autonomous agents 🤖️ powered by LLM. |
| [taishi-i/awesome-japanese-nlp-resources](https://github.com/taishi-i/awesome-japanese-nlp-resources) | 1,006 | 16.5 | - | A curated list of resources for Japanese natural language processing (NLP): Python libraries, LLMs,  |

#### 补充类别：learning（57 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [mlabonne/llm-course](https://github.com/mlabonne/llm-course) | 81,900 | 7.5 | - | Course to get into Large Language Models (LLMs) with roadmaps and Colab notebooks. |
| [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) | 74,142 | 230.7 | Python | 📚 《从零开始构建智能体》——从零开始的智能体原理与实践教程 |
| [datawhalechina/self-llm](https://github.com/datawhalechina/self-llm) | 31,806 | 202.7 | Jupyter Notebook | 《开源大模型食用指南》针对中国宝宝量身打造的基于Linux环境快速微调（全参数/Lora）、部署国内外开源大模型（LLM）/多模态大模型（MLLM）教程 |
| [AMAI-GmbH/AI-Expert-Roadmap](https://github.com/AMAI-GmbH/AI-Expert-Roadmap) | 31,217 | 0.4 | JavaScript | Roadmap to becoming an Artificial Intelligence Expert in 2022 |
| [datawhalechina/llm-cookbook](https://github.com/datawhalechina/llm-cookbook) | 24,575 | 230.8 | Jupyter Notebook | 面向开发者的 LLM 入门教程，吴恩达大模型系列课程中文版 |
| [TheAlgorithms/C](https://github.com/TheAlgorithms/C) | 22,331 | 19.9 | C | Collection of various algorithms in mathematics, machine learning, computer science, physics, etc im |
| [ruanyf/es6tutorial](https://github.com/ruanyf/es6tutorial) | 21,432 | 5.7 | JavaScript | 《ECMAScript 6入门》是一本开源的 JavaScript 语言教程，全面介绍 ECMAScript 6 新增的语法特性。 |
| [datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe) | 19,035 | 536.6 | JavaScript | 💻  vibe coding 101｜The first course for AI-native product builders. |
| [datawhalechina/leedl-tutorial](https://github.com/datawhalechina/leedl-tutorial) | 16,725 | 302.0 | Jupyter Notebook | 《李宏毅深度学习教程》（李宏毅老师推荐👍，苹果书🍎），PDF下载地址：https://github.com/datawhalechina/leedl-tutorial/releases |
| [winterbe/java8-tutorial](https://github.com/winterbe/java8-tutorial) | 16,723 | 0.1 | Java | Modern Java - A Guide to Java 8 |
| [leandromoreira/digital_video_introduction](https://github.com/leandromoreira/digital_video_introduction) | 16,295 | 26.4 | Jupyter Notebook | A hands-on introduction to video technology: image, video, codec (av1, vp9, h265) and more (ffmpeg e |
| [sundowndev/hacker-roadmap](https://github.com/sundowndev/hacker-roadmap) | 15,562 | 0.1 | - | A collection of hacking tools, resources and references to practice ethical hacking. |
| [iggredible/Learn-Vim](https://github.com/iggredible/Learn-Vim) | 15,188 | 1.8 | Dockerfile | Learning Vim and Vimscript doesn't have to be hard. This is the guide that you're looking for 📖 |
| [datawhalechina/easy-rl](https://github.com/datawhalechina/easy-rl) | 14,564 | 542.8 | Jupyter Notebook | 强化学习中文教程（蘑菇书🍄），在线阅读地址：https://datawhalechina.github.io/easy-rl/ |
| [jindongwang/transferlearning](https://github.com/jindongwang/transferlearning) | 14,348 | 36.3 | Python | Transfer learning / domain adaptation / domain generalization / multi-task learning etc. Papers, cod |
| [datawhalechina/llm-universe](https://github.com/datawhalechina/llm-universe) | 13,826 | 158.2 | Jupyter Notebook | 本项目是一个面向小白开发者的大模型应用开发教程，在线阅读地址：https://datawhalechina.github.io/llm-universe/ |
| [tangyudi/Ai-Learn](https://github.com/tangyudi/Ai-Learn) | 13,275 | 1.3 | - | 人工智能学习路线图，整理近200个实战案例与项目，免费提供配套教材，零基础入门，就业实战！包括：Python，数学，机器学习，数据分析，深度学习，计算机视觉，自然语言处理，PyTorch tensor |
| [datastacktv/data-engineer-roadmap](https://github.com/datastacktv/data-engineer-roadmap) | 12,749 | 3.5 | - | Roadmap to becoming a data engineer in 2021 |
| [nonstriater/Learn-Algorithms](https://github.com/nonstriater/Learn-Algorithms) | 8,982 | 3.7 | C | 算法学习笔记 |
| [github/roadmap](https://github.com/github/roadmap) | 8,850 | 0.0 | - | GitHub public roadmap |
| [mouredev/roadmap-retos-programacion](https://github.com/mouredev/roadmap-retos-programacion) | 8,693 | 52.5 | Python | Ruta de estudio basada en ejercicios de código de la comunidad MoureDev para aprender y practicar ló |
| [liyupi/codefather](https://github.com/liyupi/codefather) | 8,319 | 6.6 | TypeScript | 程序员鱼皮的编程宝典 ⭐️ 2026年最全编程学习路线图！包含Java学习路线、前端学习路线、Python学习路线、C++学习路线、算法学习路线、计算机基础学习路线、AI应用开发学习路线、AI Age |
| [datawhalechina/fun-rec](https://github.com/datawhalechina/fun-rec) | 7,294 | 188.3 | Python | 推荐系统入门教程，在线阅读地址：https://datawhalechina.github.io/fun-rec/ |
| [xiaobaiTech/golangFamily](https://github.com/xiaobaiTech/golangFamily) | 6,964 | 0.1 | Go | 【超全golang面试题合集+golang学习指南+golang知识图谱+入门成长路线】 一份涵盖大部分golang程序员所需要掌握的核心知识。常用第三方库(mysql,mq,es,redis等)+机 |
| [datawhalechina/Agent-Learning-Hub](https://github.com/datawhalechina/Agent-Learning-Hub) | 6,923 | 0.1 | HTML | AI Agent 学习路线与资料库收集 |
| [gonglei007/GameDevMind](https://github.com/gonglei007/GameDevMind) | 6,480 | 1870.4 | Python | 最全面的游戏开发技术图谱(Game Development Map)。帮助游戏开发者们在已知问题上节省时间，省出更多的精力投入到更有创造性的工作中去。 |
| [0voice/cpp_new_features](https://github.com/0voice/cpp_new_features) | 6,406 | 1.3 | C++ | 2021年最新整理， C++ 学习资料，含C++ 11 / 14 / 17 / 20 / 23 新特性、入门教程、推荐书籍、优质文章、学习笔记、教学视频等 |
| [datawhalechina/vibe-vibe](https://github.com/datawhalechina/vibe-vibe) | 5,931 | 405.5 | Dockerfile | AI for All: The First Systematic Vibe Coding Tutorial / From Zero to Full-Stack, Bring Your Ideas to |
| [LyleMi/Learn-Web-Hacking](https://github.com/LyleMi/Learn-Web-Hacking) | 5,505 | 2.2 | Python | Study Notes For Web Hacking / Web安全学习笔记 |
| [ruanyf/jstutorial](https://github.com/ruanyf/jstutorial) | 5,370 | 5.8 | CSS | Javascript tutorial book |
| [aws/containers-roadmap](https://github.com/aws/containers-roadmap) | 5,355 | 0.2 | Shell | This is the public roadmap for AWS container services (ECS, ECR, Fargate, and EKS).  |
| [datawhalechina/joyful-pandas](https://github.com/datawhalechina/joyful-pandas) | 5,184 | 62.6 | Jupyter Notebook | pandas中文教程 |
| [chenshenhai/koa2-note](https://github.com/chenshenhai/koa2-note) | 5,154 | 7.7 | - | 《Koa2进阶学习笔记》已完结🎄🎄🎄 |
| [tlbootcamp/tlroadmap](https://github.com/tlbootcamp/tlroadmap) | 5,133 | 32.2 | Vue | Тимлид – это ❄️, потому что в каждой компании он уникален и неповторим. |
| [miguelmota/golang-for-nodejs-developers](https://github.com/miguelmota/golang-for-nodejs-developers) | 4,768 | 0.2 | Go | Examples of Golang compared to Node.js for learning 🤓 By @miguelmota |
| [Quorafind/golang-developer-roadmap-cn-2021](https://github.com/Quorafind/golang-developer-roadmap-cn-2021) | 4,371 | 3.8 | - | [UNMAINTAINED] 在 2019 成为一名 Go 开发者的路线图。为学习 Go 的人而准备。 |
| [aadi1011/AI-ML-Roadmap-from-scratch](https://github.com/aadi1011/AI-ML-Roadmap-from-scratch) | 4,157 | 1.8 | - | Become skilled in Artificial Intelligence, Machine Learning, Generative AI, Deep Learning, Data Scie |
| [mobile-roadmap/android-developer-roadmap](https://github.com/mobile-roadmap/android-developer-roadmap) | 4,088 | 26.7 | - | Android Developer Roadmap 2020 |
| [datawhalechina/thorough-pytorch](https://github.com/datawhalechina/thorough-pytorch) | 3,755 | 86.6 | Jupyter Notebook | PyTorch入门教程，在线阅读地址：https://datawhalechina.github.io/thorough-pytorch/ |
| [milanm/DotNet-Developer-Roadmap](https://github.com/milanm/DotNet-Developer-Roadmap) | 3,710 | 99.6 | - | The comprehensive .NET Developer Roadmap for 2026 by seniority level. |
| [Overv/VulkanTutorial](https://github.com/Overv/VulkanTutorial) | 3,683 | 110.2 | C++ | Tutorial for the Vulkan graphics and compute API |
| [thecodeholic/php-developer-roadmap](https://github.com/thecodeholic/php-developer-roadmap) | 3,656 | 0.1 | - | This is PHP Developer Roadmap  |
| [salmer/CppDeveloperRoadmap](https://github.com/salmer/CppDeveloperRoadmap) | 3,533 | 9.8 | HTML | The roadmap for learning the C++ programming language for beginners and experienced devs. |
| [stemmlerjs/software-design-and-architecture-roadmap](https://github.com/stemmlerjs/software-design-and-architecture-roadmap) | 3,404 | 0.0 | - | 🧱 The software design and architecture roadmap for any developer |
| [datawhalechina/learn-nlp-with-transformers](https://github.com/datawhalechina/learn-nlp-with-transformers) | 3,359 | 41.1 | Shell | we want to create a repo to illustrate usage of transformers in chinese |
| [amitshekhariitbhu/android-developer-roadmap](https://github.com/amitshekhariitbhu/android-developer-roadmap) | 2,863 | 0.5 | Java | Android Developer Roadmap - A complete roadmap to learn Android App Development |
| [datawhalechina/handy-ollama](https://github.com/datawhalechina/handy-ollama) | 2,504 | 63.5 | Jupyter Notebook | 动手学Ollama，CPU玩转大模型部署，在线阅读地址：https://datawhalechina.github.io/handy-ollama/ |
| [LiZhengXiao99/Navigation-Learning](https://github.com/LiZhengXiao99/Navigation-Learning) | 2,394 | 682.8 | - | 我的导航算法学习笔记，内容涵盖导航定位开源程序的源码解读、开源项目梳理、书籍讲义、博客翻译、教程讲座推荐；所有内容都可以随意转载，原始文件都放在这里了，大家可以在我的基础上整理出自己的一些文档。（Ti |
| [0voice/EmbeddedSoftwareLearn](https://github.com/0voice/EmbeddedSoftwareLearn) | 2,355 | 8.6 | - | 欢迎来到本项目，这是一份面向中文社区的系统、全面且贴近实战的嵌入式软件开发学习路线和知识点总结。涵盖范围包括 C/C++、嵌入式开发、驱动开发、计算机网络原理、RTOS、嵌入式 Linux、网络通信与 |
| [datawhalechina/hello-claw](https://github.com/datawhalechina/hello-claw) | 2,189 | 74.6 | JavaScript | 哈喽！龙虾 🙋‍♀️ Adopt from scratch and build your first claw 🦞 来领养你的第一只龙虾！ |
| [DasyDong/developer-roadmap](https://github.com/DasyDong/developer-roadmap) | 1,974 | 28.7 | Python | developer-roadmap |
| [anshulrgoyal/rust-web-developer-roadmap](https://github.com/anshulrgoyal/rust-web-developer-roadmap) | 1,843 | 1.3 | Rust | Roadmap to becoming a Rust Web Developer in 2022 |
| [datawhalechina/deepagents-in-action](https://github.com/datawhalechina/deepagents-in-action) | 1,743 | 549.5 | Astro | 📚 《Deep Agents 实战》—— LangChain 官方大使出品，基于 LangChain / LangGraph 生态，从零构建生产级 AI Agent 的完整指南 |
| [prographon/graphics-developer-roadmap](https://github.com/prographon/graphics-developer-roadmap) | 1,336 | 5.2 | - | roadmap to becoming a graphics developer |
| [fullstack-development/developers-roadmap](https://github.com/fullstack-development/developers-roadmap) | 1,223 | 1.0 | Haskell | How to learn front-end or back-end development |
| [godrm/mobile-developer-roadmap](https://github.com/godrm/mobile-developer-roadmap) | 1,109 | 2.3 | - | 모바일 개발자 로드맵 |
| [eddycjy/go-developer-roadmap](https://github.com/eddycjy/go-developer-roadmap) | 1,094 | 1.0 | - | 【Go 学习路线图】涵盖业内 Go 面试题和所需要掌握的 Go 核心知识大全 |

#### 补充类别：docs-wiki（55 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [jlevy/the-art-of-command-line](https://github.com/jlevy/the-art-of-command-line) | 162,146 | 2.7 | - | Master the command line, in one page |
| [storybookjs/storybook](https://github.com/storybookjs/storybook) | 90,892 | 1067.9 | TypeScript | Storybook is the industry standard workshop for building, documenting, and testing UI components in  |
| [mermaid-js/mermaid](https://github.com/mermaid-js/mermaid) | 89,877 | 270.2 | TypeScript | Generation of diagrams like flowcharts or sequence diagrams from text in a similar manner as markdow |
| [AppFlowy-IO/AppFlowy](https://github.com/AppFlowy-IO/AppFlowy) | 75,822 | 91.7 | Dart | Bring projects, wikis, and teams together with AI. AppFlowy is the AI collaborative workspace where  |
| [facebook/docusaurus](https://github.com/facebook/docusaurus) | 66,038 | 1321.7 | TypeScript | Easy to maintain open source documentation websites. |
| [siyuan-note/siyuan](https://github.com/siyuan-note/siyuan) | 45,921 | 722.5 | TypeScript | An open-source, privacy-first, self-hosted knowledge workspace where humans and AI agents work toget |
| [freeCodeCamp/devdocs](https://github.com/freeCodeCamp/devdocs) | 39,341 | 32.1 | Ruby | API Documentation Browser |
| [satwikkansal/wtfpython](https://github.com/satwikkansal/wtfpython) | 37,055 | 1.4 | Python | What the f*ck Python? 😱 |
| [docsifyjs/docsify](https://github.com/docsifyjs/docsify) | 31,468 | 30.1 | JavaScript | 🃏 A magical documentation site generator. |
| [GitbookIO/gitbook](https://github.com/GitbookIO/gitbook) | 29,005 | 361.2 | TypeScript | The open source frontend for GitBook doc sites |
| [requarks/wiki](https://github.com/requarks/wiki) | 28,785 | 43.4 | Vue | Wiki.js / A modern and powerful wiki app built on Node.js |
| [hcengineering/platform](https://github.com/hcengineering/platform) | 27,411 | 306.5 | TypeScript | Huly — All-in-One Project Management Platform (alternative to Linear, Jira, Slack, Notion, Motion) |
| [squidfunk/mkdocs-material](https://github.com/squidfunk/mkdocs-material) | 27,311 | 143.4 | Python | Documentation that simply works |
| [pedronauck/docz](https://github.com/pedronauck/docz) | 23,583 | 9.8 | TypeScript | ✍ It has never been so easy to document your things! |
| [shimohq/chinese-programmer-wrong-pronunciation](https://github.com/shimohq/chinese-programmer-wrong-pronunciation) | 23,268 | 1.1 | JavaScript | 中国程序员容易发音错误的单词 |
| [mkdocs/mkdocs](https://github.com/mkdocs/mkdocs) | 22,364 | 32.5 | Python | Project documentation with Markdown. |
| [docmost/docmost](https://github.com/docmost/docmost) | 21,433 | 12.9 | TypeScript | Docmost is an open-source collaborative wiki and documentation software. It is an open-source altern |
| [Tencent/WeKnora](https://github.com/Tencent/WeKnora) | 20,318 | 109.9 | Go | Open-source LLM knowledge platform: turn raw documents into a queryable RAG, an autonomous reasoning |
| [nhn/tui.editor](https://github.com/nhn/tui.editor) | 18,007 | 80.6 | TypeScript | 🍞📝 Markdown WYSIWYG Editor. GFM Standard + Chart & UML Extensible. |
| [AsyncFuncAI/deepwiki-open](https://github.com/AsyncFuncAI/deepwiki-open) | 17,728 | 4.4 | Python | Open Source DeepWiki: AI-Powered Wiki Generator for GitHub/Gitlab/Bitbucket Repositories. Join the d |
| [suitenumerique/docs](https://github.com/suitenumerique/docs) | 16,744 | 164.5 | Python | Docs is an open-source text editor: web-native, made for real-time collaboration, cleanly structured |
| [architecture-decision-record/architecture-decision-record](https://github.com/architecture-decision-record/architecture-decision-record) | 16,708 | 0.5 | - | Architecture decision record (ADR) examples for software planning, IT leadership, and template docum |
| [scalar/scalar](https://github.com/scalar/scalar) | 15,958 | 360.3 | TypeScript | Scalar is an open-source API platform:　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　🌐 Modern REST API Clien |
| [github/opensource.guide](https://github.com/github/opensource.guide) | 15,642 | 19.8 | HTML | 📚 Community guides for open source creators |
| [sparanoid/chinese-copywriting-guidelines](https://github.com/sparanoid/chinese-copywriting-guidelines) | 15,641 | 0.4 | - | Chinese copywriting guidelines for better written communication／中文文案排版指北 |
| [jsdoc/jsdoc](https://github.com/jsdoc/jsdoc) | 15,451 | 27.5 | JavaScript | An API documentation generator for JavaScript. |
| [SimulatedGREG/electron-vue](https://github.com/SimulatedGREG/electron-vue) | 15,384 | 5.8 | JavaScript | An Electron & Vue.js quick start boilerplate with vue-cli scaffolding, common Vue plugins, electron- |
| [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | 14,794 | 20.4 | Python | Convert documentation websites, GitHub repositories, and PDFs into Claude AI skills with automatic c |
| [pandao/editor.md](https://github.com/pandao/editor.md) | 14,317 | 15.7 | JavaScript | The open source embeddable online markdown editor (component). |
| [gollum/gollum](https://github.com/gollum/gollum) | 14,312 | 134.6 | Ruby | A simple, Git-powered wiki with a local frontend and support for many kinds of markup and content. |
| [zealdocs/zeal](https://github.com/zealdocs/zeal) | 12,770 | 8.6 | C++ | Offline documentation browser. Your personal reference library, searchable in an instant. |
| [ruanyf/document-style-guide](https://github.com/ruanyf/document-style-guide) | 12,665 | 0.1 | - | 中文技术文档的写作规范 |
| [xgrommx/awesome-redux](https://github.com/xgrommx/awesome-redux) | 12,282 | 0.6 | - | Awesome list of Redux examples and middlewares |
| [mdn/content](https://github.com/mdn/content) | 10,948 | 492.8 | Markdown | The official source for MDN Web Docs content. Home to over 14,000 pages of documentation about HTML, |
| [brightmart/nlp_chinese_corpus](https://github.com/brightmart/nlp_chinese_corpus) | 9,909 | 4.0 | - | 大规模中文自然语言处理语料  Large Scale Chinese Corpus for NLP |
| [ctf-wiki/ctf-wiki](https://github.com/ctf-wiki/ctf-wiki) | 9,583 | 656.3 | Python | Come and join us, we need you! |
| [vimwiki/vimwiki](https://github.com/vimwiki/vimwiki) | 9,510 | 6.2 | Vim Script | Personal Wiki for Vim |
| [TiddlyWiki/TiddlyWiki5](https://github.com/TiddlyWiki/TiddlyWiki5) | 8,628 | 72.7 | JavaScript | A self-contained JavaScript wiki for the browser, Node.js, AWS Lambda etc. |
| [sysprog21/lkmpg](https://github.com/sysprog21/lkmpg) | 8,567 | 8.6 | TeX | The Linux Kernel Module Programming Guide (updated for 5.0+ kernels) |
| [0voice/linux_kernel_wiki](https://github.com/0voice/linux_kernel_wiki) | 7,777 | 145.5 | - | linux内核学习资料：200+经典内核文章，100+内核论文，50+内核项目，500+内核面试题，80+内核视频 |
| [mdn/learning-area](https://github.com/mdn/learning-area) | 7,597 | 85.0 | HTML | GitHub repo for the MDN Learning Area.  |
| [persepolisdm/persepolis](https://github.com/persepolisdm/persepolis) | 7,434 | 37.5 | Python | Persepolis is a download manager written in Python. |
| [Bogdan-Lyashenko/js-code-to-svg-flowchart](https://github.com/Bogdan-Lyashenko/js-code-to-svg-flowchart) | 7,116 | 13.9 | JavaScript | js2flowchart - a visualization library to convert any JavaScript code into beautiful SVG flowchart.  |
| [Juanpe/About-SwiftUI](https://github.com/Juanpe/About-SwiftUI) | 7,085 | 0.7 | Swift | Gathering all info published, both by Apple and by others, about new framework SwiftUI.  |
| [wikimedia/mediawiki](https://github.com/wikimedia/mediawiki) | 5,150 | 2592.6 | PHP | 🌻 The collaborative editing software that runs Wikipedia. Mirror from https://gerrit.wikimedia.org/g |
| [colanode/colanode](https://github.com/colanode/colanode) | 5,021 | 77.2 | TypeScript | Open-source and local-first Slack and Notion alternative that puts you in control of your data |
| [dokuwiki/dokuwiki](https://github.com/dokuwiki/dokuwiki) | 4,708 | 44.5 | PHP | The DokuWiki Open Source Wiki Engine |
| [LLMQuant/quant-wiki](https://github.com/LLMQuant/quant-wiki) | 4,066 | 160.7 | - | We are committed to the open-sourcing quantitative knowledge, aiming to bridge the information gap b |
| [BoostIO/BoostNote-App](https://github.com/BoostIO/BoostNote-App) | 4,049 | 79.4 | TypeScript | Boost Note is a document driven project management tool that maximizes remote DevOps team velocity. |
| [mapnik/mapnik](https://github.com/mapnik/mapnik) | 3,955 | 172.2 | C++ | Mapnik is an open source toolkit for developing mapping applications |
| [macro-inc/macro](https://github.com/macro-inc/macro) | 3,949 | 1696.9 | Rust | Macro is a unified workspace for teams: email, chat, docs, tasks, agents, calls, and CRM — @-linked  |
| [phachon/mm-wiki](https://github.com/phachon/mm-wiki) | 3,774 | 25.9 | Go | MM-Wiki 一个轻量级的企业知识分享与团队协同软件，可用于快速构建企业 Wiki 和团队知识分享平台。部署方便，使用简单，帮助团队构建一个信息共享、文档管理的协作环境。 |
| [cirosantilli/china-dictatorship](https://github.com/cirosantilli/china-dictatorship) | 3,156 | 103.0 | HTML | 反中共政治宣传库。Anti Chinese government propaganda. 住在中国真名用户的网友请别给星星，不然你要被警察请喝茶。常见问答集，新闻集和饭店和音乐建议。卐习万岁卐。冠状病 |
| [gege-circle/.github](https://github.com/gege-circle/.github) | 1,982 | 1.7 | - | 这里是GitHub的草场，也是戈戈圈爱好者的交流地，主要讨论动漫、游戏、科技、人文、生活等所有话题，欢迎各位小伙伴们在此讨论趣事。This is GitHub grassland, and the c |
| [0voice/k8s_awesome_document](https://github.com/0voice/k8s_awesome_document) | 1,611 | 78.3 | - | 【2021年新鲜出炉】K8s（Kubernetes）的工程师资料合辑，书籍推荐，面试题，精选文章，开源项目，PPT，视频，大厂资料 |

#### 补充类别：notes-zh（50 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [AccumulateMore/CV](https://github.com/AccumulateMore/CV) | 23,372 | 385.8 | Jupyter Notebook | ✅（已完结）超级全面的 深度学习 笔记【土堆 Pytorch】【李沐 动手学深度学习】【吴恩达 深度学习】【大飞 大模型Agent】 |
| [janishar/mit-deep-learning-book-pdf](https://github.com/janishar/mit-deep-learning-book-pdf) | 14,204 | 57.1 | Java | MIT Deep Learning Book in PDF format (complete and parts) by Ian Goodfellow, Yoshua Bengio and Aaron |
| [qyuhen/book](https://github.com/qyuhen/book) | 12,504 | 47.9 | - | 学习笔记 |
| [hackjutsu/Lepton](https://github.com/hackjutsu/Lepton) | 10,339 | 45.4 | JavaScript | 💻     Democratizing Snippet Management (macOS/Win/Linux) |
| [senghoo/golang-design-pattern](https://github.com/senghoo/golang-design-pattern) | 9,027 | 1.0 | Go | 设计模式 Golang实现－《研磨设计模式》读书笔记 |
| [applenob/Cpp_Primer_Practice](https://github.com/applenob/Cpp_Primer_Practice) | 8,749 | 3.0 | C++ | 搞定C++:punch:。C++ Primer 中文版第5版学习仓库，包括笔记和课后练习答案。 |
| [xwmx/nb](https://github.com/xwmx/nb) | 8,369 | 9.4 | Shell | CLI and local web plain text note‑taking, bookmarking, and archiving with linking, tagging, filterin |
| [jawil/blog](https://github.com/jawil/blog) | 7,819 | 0.1 | JavaScript | Too young, too simple. Sometimes, naive & stupid 🐌 |
| [hedgedoc/hedgedoc](https://github.com/hedgedoc/hedgedoc) | 7,376 | 113.8 | TypeScript | HedgeDoc - Ideas grow better together |
| [jrnl-org/jrnl](https://github.com/jrnl-org/jrnl) | 7,295 | 5.2 | Python | Collect your thoughts and notes without leaving the command line. |
| [taniarascia/takenote](https://github.com/taniarascia/takenote) | 7,128 | 10.8 | TypeScript | 📝  ‎ A web-based notes app for developers. |
| [qinjx/30min_guides](https://github.com/qinjx/30min_guides) | 7,105 | 0.1 | - | 覃健祥的学习笔记，各种几十分钟入门的文档 |
| [doocs/technical-books](https://github.com/doocs/technical-books) | 6,973 | 9.8 | TypeScript | 😆 国内外互联网技术大牛们都写了哪些书籍：计算机基础、网络、前端、后端、数据库、架构、大数据、深度学习... |
| [massCodeIO/massCode](https://github.com/massCodeIO/massCode) | 6,961 | 11.4 | TypeScript | A free, open-source developer workspace. Snippets, notes, HTTP requests, calculations, and dev tools |
| [chyingp/nodejs-learning-guide](https://github.com/chyingp/nodejs-learning-guide) | 6,868 | 1.1 | Ruby | Nodejs学习笔记以及经验总结，公众号"程序猿小卡" |
| [standardnotes/app](https://github.com/standardnotes/app) | 6,598 | 1741.6 | TypeScript | Think fearlessly with end-to-end encrypted notes and files. For issues, visit https://standardnotes. |
| [SmirkCao/Lihang](https://github.com/SmirkCao/Lihang) | 6,308 | 10.1 | Python | Statistical learning methods, 统计学习方法(第2版)[李航]  [笔记, 代码, notebook, 参考文献, Errata, lihang] |
| [JuanCrg90/Clean-Code-Notes](https://github.com/JuanCrg90/Clean-Code-Notes) | 6,119 | 0.1 | - | My notes of Clean Code book |
| [heyman/heynote](https://github.com/heyman/heynote) | 5,355 | 8.5 | JavaScript | A dedicated scratchpad for power users |
| [moranzcw/Computer-Networking-A-Top-Down-Approach-NOTES](https://github.com/moranzcw/Computer-Networking-A-Top-Down-Approach-NOTES) | 5,212 | 139.9 | Python | 《计算机网络－自顶向下方法(原书第6版)》编程作业，Wireshark实验文档的翻译和解答。 |
| [xinliangnote/Go](https://github.com/xinliangnote/Go) | 4,946 | 3.9 | Go | 【Go 从入门到实战】学习笔记，从零开始学 Go、Gin 框架，基本语法包括 26 个Demo，Gin 框架包括：Gin 自定义路由配置、Gin 使用 Logrus 进行日志记录、Gin 数据绑定和验 |
| [saber-notes/saber](https://github.com/saber-notes/saber) | 4,705 | 941.5 | Dart | The cross-platform open-source app built for handwriting |
| [brianway/java-learning](https://github.com/brianway/java-learning) | 4,287 | 0.8 | Java | 旨在打造在线最佳的 Java 学习笔记，含博客讲解和源码实例，包括 Java SE 和 Java Web |
| [nuttyartist/notes](https://github.com/nuttyartist/notes) | 4,266 | 14.8 | C++ | Fast and beautiful note-taking app written in C++. Write down your thoughts. |
| [GitJournal/GitJournal](https://github.com/GitJournal/GitJournal) | 4,208 | 12.5 | Dart | Mobile first Note Taking integrated with Git |
| [mgp/book-notes](https://github.com/mgp/book-notes) | 4,108 | 1.8 | - | Notes from books and other interesting things that I've read. Table of contents at the end 👇 |
| [skindhu/Build-A-Large-Language-Model-CN](https://github.com/skindhu/Build-A-Large-Language-Model-CN) | 3,972 | 184.5 | HTML | 《Build a Large Language Model (From Scratch)》是一本深入探讨大语言模型原理与实现的电子书，适合希望深入了解 GPT 等大模型架构、训练过程及应用开发的学习者 |
| [ShujiaHuang/Cpp-Primer-Plus-6th](https://github.com/ShujiaHuang/Cpp-Primer-Plus-6th) | 3,239 | 0.3 | C++ |  《C++ Primer Plus 第6版（中文版）》原书代码、习题答案和个人笔记，仅供学习和交流。 |
| [Miraclelucy/dive_into_deep_learning](https://github.com/Miraclelucy/dive_into_deep_learning) | 3,073 | 0.1 | Python | ✔️李沐 【动手学深度学习】课程学习笔记：使用pycharm编程，基于pytorch框架实现。 |
| [brianway/springmvc-mybatis-learning](https://github.com/brianway/springmvc-mybatis-learning) | 2,944 | 17.5 | Java | SpringMVC 和 MyBatis 学习笔记，搭配示例，主要讲解一些基础的概念、用法和配置 |
| [gatieme/LDD-LinuxDeviceDrivers](https://github.com/gatieme/LDD-LinuxDeviceDrivers) | 2,906 | 114.7 | C | Linux内核学习笔记 |
| [QianMo/Real-Time-Rendering-3rd-CN-Summary-Ebook](https://github.com/QianMo/Real-Time-Rendering-3rd-CN-Summary-Ebook) | 2,669 | 32.3 | - | :blue_book: 电子书 -《Real-Time Rendering 3rd》提炼总结 / 全书共9万7千余字。你可以把它看做中文通俗版的《Real-Time Rendering 3rd》，也可 |
| [ysyisyourbrother/SYSU_Notebook](https://github.com/ysyisyourbrother/SYSU_Notebook) | 2,542 | 2454.7 | Python | 本项目分享了中山大学计算机学院本科和研究生阶段的课程资料、笔记、期末考试卷和其他实用的相关资源。希望对同学们的学习有所帮助❤️，如果喜欢记得给个star🌟  |
| [riba2534/TCP-IP-NetworkNote](https://github.com/riba2534/TCP-IP-NetworkNote) | 2,510 | 33.4 | C | 📘《TCP/IP网络编程》(韩-尹圣雨)学习笔记 |
| [daohu527/dig-into-apollo](https://github.com/daohu527/dig-into-apollo) | 2,456 | 28.3 | - | Apollo notes (Apollo学习笔记) - Apollo learning notes for beginners.  |
| [szza/LearningNote](https://github.com/szza/LearningNote) | 2,446 | 166.7 | C++ | C++和Linux学习笔记 |
| [datawhalechina/team-learning](https://github.com/datawhalechina/team-learning) | 2,407 | 288.9 | - | 主要展示Datawhale的组队学习计划。 |
| [datawhalechina/team-learning-data-mining](https://github.com/datawhalechina/team-learning-data-mining) | 1,856 | 100.0 | Jupyter Notebook | 主要存储Datawhale组队学习中“数据挖掘/机器学习”方向的资料。 |
| [wx-chevalier/DistributedSystem-Notes](https://github.com/wx-chevalier/DistributedSystem-Notes) | 1,573 | 4.5 | HTML | :books: 深入浅出分布式基础架构，Linux 与操作系统篇 / 分布式系统篇 / 分布式计算篇 / 数据库篇 / 网络篇 / 虚拟化与编排篇 / 大数据与云计算篇 |
| [wx-chevalier/Database-Notes](https://github.com/wx-chevalier/Database-Notes) | 1,414 | 8.7 | HTML | 📚深入浅出数据库存储：数据库理论、关系型数据库、文档型数据库、键值型数据库、New SQL、搜索引擎、数据仓库与 OLAP、大数据与数据中台 |
| [ssnangua/ColorTxt](https://github.com/ssnangua/ColorTxt) | 1,315 | 49.8 | TypeScript | 「彩读 3.0 书源 × AI+」——一款会给内容上色的本地 TXT 小说阅读器，带给你不一样的阅读体验！（也支持打开常见的电子书格式，如 .epub）。还有章节识别、简繁互转、划线标注、记笔记、词典 |
| [jiacai2050/sicp](https://github.com/jiacai2050/sicp) | 1,235 | 14.1 | Scheme | 📖 SICP 读书笔记，习题解答 |
| [yifengyou/The-design-and-implementation-of-a-64-bit-os](https://github.com/yifengyou/The-design-and-implementation-of-a-64-bit-os) | 1,198 | 101.8 | C | 《一个64位操作系统的设计与实现》读书笔记&随书源码 |
| [ZhaoKaiQiang/AndroidDifficultAnalysis](https://github.com/ZhaoKaiQiang/AndroidDifficultAnalysis) | 1,165 | 0.1 | - | 安卓开发中遇到的重难点解析，也包括平常的读书笔记和知识点整理 |
| [0voice/Understanding_in_Rust](https://github.com/0voice/Understanding_in_Rust) | 1,135 | 14.6 | - | 【最安全的编程语言】Rust工程师枕边资料，大牛文章，开源框架，官方文档，视频，推荐书籍，学习干货，大牛语录 |
| [joeseesun/qiaomu-mondo-poster-design](https://github.com/joeseesun/qiaomu-mondo-poster-design) | 1,109 | 68.0 | Python | 一句话生成大师级海报、书籍封面、专辑封面和各类设计作品。无需懂PS、配色或艺术史，AI自动选择最佳风格（基于20位传奇海报设计师）。支持电影海报、读书笔记、公众号封面、小红书配图等。默认9:16竖版， |
| [arry-lee/wereader](https://github.com/arry-lee/wereader) | 955 | 1.0 | Python | 一个功能全面的微信读书笔记助手 wereader |
| [bluecity2048/learning-k8s-source-code](https://github.com/bluecity2048/learning-k8s-source-code) | 854 | 7.3 | Go | k8s、docker源码分析、读书笔记 |
| [wx-chevalier/Web-Notes](https://github.com/wx-chevalier/Web-Notes) | 846 | 4.9 | HTML | :books: 现代 Web 开发语法基础与工程实践，涵盖 Web 开发基础、前端工程化、应用架构、性能与体验优化、混合开发、React 实践、Vue 实践、WebAssembly 等多方面。 |
| [yifengyou/linux-0.12](https://github.com/yifengyou/linux-0.12) | 815 | 81.3 | C | 赵炯老师《linux-0.12 内核完全剖析》读书笔记及linux-0.12注释源码 |

#### 补充类别：cheatsheet（43 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [tiimgreen/github-cheat-sheet](https://github.com/tiimgreen/github-cheat-sheet) | 58,660 | 0.8 | - | A list of cool features of Git and GitHub. |
| [chubin/cheat.sh](https://github.com/chubin/cheat.sh) | 41,668 | 4.6 | Python | the only cheat sheet you need |
| [gto76/python-cheatsheet](https://github.com/gto76/python-cheatsheet) | 38,636 | 13.5 | Python | Comprehensive Python Cheatsheet |
| [mbeaudru/modern-js-cheatsheet](https://github.com/mbeaudru/modern-js-cheatsheet) | 25,613 | 0.3 | - | Cheatsheet for the JavaScript knowledge you will frequently encounter in modern projects. |
| [FavioVazquez/ds-cheatsheets](https://github.com/FavioVazquez/ds-cheatsheets) | 16,326 | 119.5 | - | List of Data Science Cheatsheets to rule the world |
| [kailashahirwar/cheatsheets-ai](https://github.com/kailashahirwar/cheatsheets-ai) | 15,427 | 29.3 | - | Essential Cheat Sheets for deep learning and machine learning researchers https://medium.com/@kailas |
| [rstacruz/cheatsheets](https://github.com/rstacruz/cheatsheets) | 14,455 | 39.3 | SCSS | Cheatsheets for web development - devhints.io |
| [kettanaito/naming-cheatsheet](https://github.com/kettanaito/naming-cheatsheet) | 14,184 | 0.1 | - | Comprehensive language-agnostic guidelines on variables naming. Home of the A/HC/LC pattern. |
| [DrkSephy/es6-cheatsheet](https://github.com/DrkSephy/es6-cheatsheet) | 13,324 | 0.2 | JavaScript | ES2015 [ES6] cheatsheet containing tips, tricks, best practices and code snippets |
| [skywind3000/awesome-cheatsheets](https://github.com/skywind3000/awesome-cheatsheets) | 12,555 | 0.3 | Shell | 超级速查表 - 编程语言、框架和开发工具的速查表，单个文件包含一切你需要知道的东西 :zap: |
| [detailyang/awesome-cheatsheet](https://github.com/detailyang/awesome-cheatsheet) | 8,531 | 9.3 | Python | :beers: awesome cheatsheet |
| [matplotlib/cheatsheets](https://github.com/matplotlib/cheatsheets) | 7,724 | 24.0 | Python | Official Matplotlib cheat sheets |
| [0nn0/terminal-mac-cheatsheet](https://github.com/0nn0/terminal-mac-cheatsheet) | 7,403 | 0.1 | - | List of my most used commands and shortcuts in the terminal for Mac |
| [EdOverflow/bugbounty-cheatsheet](https://github.com/EdOverflow/bugbounty-cheatsheet) | 6,534 | 0.1 | - | A list of interesting payloads, tips and tricks for bug bounty hunters. |
| [rstudio/cheatsheets](https://github.com/rstudio/cheatsheets) | 6,404 | 1311.2 | TeX | Posit Cheat Sheets - Can also be found at https://posit.co/resources/cheatsheets/. |
| [OlivierLaflamme/Cheatsheet-God](https://github.com/OlivierLaflamme/Cheatsheet-God) | 5,620 | 0.8 | - | Penetration Testing Reference Bank - OSCP / PTP & PTX  Cheatsheet |
| [enochtangg/quick-SQL-cheatsheet](https://github.com/enochtangg/quick-SQL-cheatsheet) | 5,448 | 0.0 | - | A quick reminder of all SQL queries and examples on how to use them.  |
| [aaronwangy/Data-Science-Cheatsheet](https://github.com/aaronwangy/Data-Science-Cheatsheet) | 5,443 | 4.5 | TeX | A helpful 5-page machine learning cheatsheet to assist with exam reviews, interview prep, and anythi |
| [tchapi/markdown-cheatsheet](https://github.com/tchapi/markdown-cheatsheet) | 5,289 | 0.0 | - | Markdown Cheatsheet for Github Readme.md |
| [tanprathan/MobileApp-Pentest-Cheatsheet](https://github.com/tanprathan/MobileApp-Pentest-Cheatsheet) | 5,256 | 0.3 | - | The Mobile App Pentest cheat sheet was created to provide concise collection of high value informati |
| [github/training-kit](https://github.com/github/training-kit) | 5,066 | 359.8 | HTML | Open source courseware for Git and GitHub |
| [cheatsnake/backend-cheats](https://github.com/cheatsnake/backend-cheats) | 5,055 | 10.3 | - | 📃 White paper for Backend developers |
| [labex-labs/python-cheatsheet](https://github.com/labex-labs/python-cheatsheet) | 4,951 | 50.9 | Vue | Python Cheatsheet - interactive hands-on course by LabEx. |
| [A-poc/BlueTeam-Tools](https://github.com/A-poc/BlueTeam-Tools) | 4,444 | 0.1 | - | Tools and Techniques for Blue Team / Incident Response |
| [mortennobel/cpp-cheatsheet](https://github.com/mortennobel/cpp-cheatsheet) | 3,556 | 0.0 | C++ | Modern C++ Cheatsheet |
| [kleiton0x00/Advanced-SQL-Injection-Cheatsheet](https://github.com/kleiton0x00/Advanced-SQL-Injection-Cheatsheet) | 3,246 | 0.1 | - | A cheat sheet that contains advanced queries for SQL Injection of all types. |
| [wzchen/probability_cheatsheet](https://github.com/wzchen/probability_cheatsheet) | 3,153 | 4.1 | TeX | A comprehensive 10-page probability cheatsheet that covers a semester's worth of introduction to pro |
| [bfortuner/ml-glossary](https://github.com/bfortuner/ml-glossary) | 3,131 | 8.2 | Python | Machine learning glossary |
| [mgeeky/Penetration-Testing-Tools](https://github.com/mgeeky/Penetration-Testing-Tools) | 3,000 | 17.1 | PowerShell | A collection of more than 170+ tools, scripts, cheatsheets and other loots that I've developed over  |
| [NoorQureshi/kali-linux-cheatsheet](https://github.com/NoorQureshi/kali-linux-cheatsheet) | 2,983 | 0.1 | - | Kali Linux Cheat Sheet for Penetration Testers |
| [w181496/Web-CTF-Cheatsheet](https://github.com/w181496/Web-CTF-Cheatsheet) | 2,982 | 0.4 | Ruby | Web CTF CheatSheet 🐈 |
| [rougier/matplotlib-cheatsheet](https://github.com/rougier/matplotlib-cheatsheet) | 2,907 | 4.3 | Python | Matplotlib 3.1 cheat sheet.  |
| [dafthack/CloudPentestCheatsheets](https://github.com/dafthack/CloudPentestCheatsheets) | 2,834 | 0.5 | - | This repository contains a collection of cheatsheets I have put together for tools related to pentes |
| [ml874/Data-Science-Cheatsheet](https://github.com/ml874/Data-Science-Cheatsheet) | 2,572 | 3.6 | TeX |  |
| [danielkummer/git-flow-cheatsheet](https://github.com/danielkummer/git-flow-cheatsheet) | 2,514 | 2.7 | HTML | A cheatsheet on the usage of git flow |
| [dennyzhang/cheatsheet-kubernetes-A4](https://github.com/dennyzhang/cheatsheet-kubernetes-A4) | 2,161 | 2.8 | Shell | :book: Kubernetes CheatSheets In A4 |
| [rochacbruno/py2rs](https://github.com/rochacbruno/py2rs) | 2,087 | 1.3 | CSS | A quick reference guide for the Pythonista in the process of becoming a Rustacean |
| [cheat/cheatsheets](https://github.com/cheat/cheatsheets) | 2,034 | 0.5 | Shell | Community-sourced cheatsheets |
| [akr3ch/BugBountyBooks](https://github.com/akr3ch/BugBountyBooks) | 1,991 | 82.9 | - | A collection of PDF/books about the modern web application security and bug bounty. |
| [andrewjkerr/security-cheatsheets](https://github.com/andrewjkerr/security-cheatsheets) | 1,394 | 0.0 | - | 🔒 A collection of cheatsheets for various infosec tools and topics. |
| [iwasrobbed/Objective-C-CheatSheet](https://github.com/iwasrobbed/Objective-C-CheatSheet) | 1,361 | 0.1 | - | A quick reference cheat sheet for common, high level topics in Objective-C. |
| [crescentpartha/CheatSheets-for-Developers](https://github.com/crescentpartha/CheatSheets-for-Developers) | 1,208 | 0.6 | - | A collection of programming CheatSheets for developers to boost your productivity and quick review t |
| [iwasrobbed/Swift-CheatSheet](https://github.com/iwasrobbed/Swift-CheatSheet) | 1,005 | 0.1 | - | A quick reference cheat sheet for common, high level topics in Swift. |

#### 补充类别：handbook-manual（43 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [jakevdp/PythonDataScienceHandbook](https://github.com/jakevdp/PythonDataScienceHandbook) | 49,667 | 42.6 | Jupyter Notebook | Python Data Science Handbook: full text in Jupyter Notebooks |
| [DataExpert-io/data-engineer-handbook](https://github.com/DataExpert-io/data-engineer-handbook) | 43,817 | 60.9 | Jupyter Notebook | This is a repo with links to everything you'd ever want to learn about data engineering |
| [zergtant/pytorch-handbook](https://github.com/zergtant/pytorch-handbook) | 21,676 | 146.0 | Jupyter Notebook | pytorch handbook是一本开源的书籍，目标是帮助那些希望和使用PyTorch进行深度学习开发和研究的朋友快速入门，其中包含的Pytorch教程全部通过测试保证可以成功运行 |
| [jordan-cutler/path-to-senior-engineer-handbook](https://github.com/jordan-cutler/path-to-senior-engineer-handbook) | 18,063 | 0.1 | - | All the resources you need to get to Senior Engineer and beyond |
| [ZachGoldberg/Startup-CTO-Handbook](https://github.com/ZachGoldberg/Startup-CTO-Handbook) | 14,192 | 6.2 | - | The Startup CTO's Handbook, a book covering leadership, management and technical topics for leaders  |
| [willwulfken/MidJourney-Styles-and-Keywords-Reference](https://github.com/willwulfken/MidJourney-Styles-and-Keywords-Reference) | 12,292 | 23481.0 | - | A reference containing Styles and Keywords that you can use with MidJourney AI. There are also pages |
| [jamiebuilds/babel-handbook](https://github.com/jamiebuilds/babel-handbook) | 12,096 | 2.8 | - | :blue_book: A guided handbook on how to use Babel and how to create plugins for Babel. |
| [rootsongjc/kubernetes-handbook](https://github.com/rootsongjc/kubernetes-handbook) | 11,611 | 438.2 | Mermaid | Kubernetes 架构与生态：从云原生到 AI 原生基础设施的构建指南 |
| [tpn/pdfs](https://github.com/tpn/pdfs) | 10,105 | 3548.8 | HTML | Technically-oriented PDF Collection (Papers, Specs, Decks, Manuals, etc) — browse & search it at tpn |
| [0voice/introduce_c-cpp_manual](https://github.com/0voice/introduce_c-cpp_manual) | 8,224 | 3.9 | C++ | 一个收集C/C++新手学习的入门项目，整理收纳开发者开源的小项目、工具、框架、游戏等，视频，书籍，面试题/算法题，技术文章。 |
| [dylanaraps/pure-sh-bible](https://github.com/dylanaraps/pure-sh-bible) | 7,733 | 0.1 | Shell | 📖 A collection of pure POSIX sh alternatives to external processes. |
| [astrid-runtime/handbook](https://github.com/astrid-runtime/handbook) | 7,409 | 0.0 | - | Contributor handbook for Astrid: the polyrepo, public contracts, contribution process, and release w |
| [slowmist/Blockchain-dark-forest-selfguard-handbook](https://github.com/slowmist/Blockchain-dark-forest-selfguard-handbook) | 6,839 | 23.3 | - | Blockchain dark forest selfguard handbook. Master these, master the security of your cryptocurrency. |
| [basecamp/handbook](https://github.com/basecamp/handbook) | 6,645 | 0.6 | - | 37signals Employee Handbook |
| [denysdovhan/bash-handbook](https://github.com/denysdovhan/bash-handbook) | 6,078 | 0.3 | JavaScript | :book: For those who wanna learn Bash |
| [apptension/developer-handbook](https://github.com/apptension/developer-handbook) | 5,960 | 0.7 | - | An opinionated guide on how to become a professional Web/Mobile App Developer. |
| [huggingface/alignment-handbook](https://github.com/huggingface/alignment-handbook) | 5,664 | 0.3 | Python | Robust recipes to align language models with human and AI preferences |
| [feiskyer/kubernetes-handbook](https://github.com/feiskyer/kubernetes-handbook) | 5,530 | 67.4 | Makefile | Kubernetes Handbook （Kubernetes指南）   https://kubernetes.feisky.xyz |
| [PacktPublishing/LLM-Engineers-Handbook](https://github.com/PacktPublishing/LLM-Engineers-Handbook) | 5,288 | 4.6 | Python | The LLM's practical guide: From the fundamentals to deploying advanced LLM and RAG apps to AWS using |
| [SylphAI-Inc/LLM-engineer-handbook](https://github.com/SylphAI-Inc/LLM-engineer-handbook) | 5,021 | 0.1 | - | A curated list of Large Language Model resources, covering model training, serving, fine-tuning, and |
| [microsoft/TypeScript-Handbook](https://github.com/microsoft/TypeScript-Handbook) | 4,850 | 7.1 | JavaScript | Deprecated, please use the TypeScript-Website repo instead |
| [eliaszon/Programmers-Overseas-Job-Interview-Handbook](https://github.com/eliaszon/Programmers-Overseas-Job-Interview-Handbook) | 4,799 | 13.9 | - | 🏂🏻 程序员海外工作/英文面试手册 |
| [riscv/riscv-isa-manual](https://github.com/riscv/riscv-isa-manual) | 4,770 | 59.8 | TeX | RISC-V Instruction Set Manual |
| [SLAM-Handbook-contributors/slam-handbook-public-release](https://github.com/SLAM-Handbook-contributors/slam-handbook-public-release) | 4,608 | 100.6 | TeX | Release repo for our SLAM Handbook |
| [browserify/browserify-handbook](https://github.com/browserify/browserify-handbook) | 4,591 | 0.2 | JavaScript | how to build modular applications with browserify |
| [jaywcjlove/handbook](https://github.com/jaywcjlove/handbook) | 4,386 | 40.8 | Markdown | 放置我的笔记、搜集、摘录、实践，保持好奇心。看文需谨慎，后果很严重。 |
| [FrontendMasters/front-end-handbook-2018](https://github.com/FrontendMasters/front-end-handbook-2018) | 4,183 | 13.0 | HTML | 2018 edition of our front-end development handbook |
| [XiaomingX/ai-money-maker-handbook](https://github.com/XiaomingX/ai-money-maker-handbook) | 4,163 | 4.2 | CSS | ai副业赚钱大集合，教你如何利用ai做一些副业项目，赚取更多额外收益。The Ultimate Guide to Making Money with AI Side Hustles: Learn ho |
| [FrontendMasters/front-end-handbook-2019](https://github.com/FrontendMasters/front-end-handbook-2019) | 4,085 | 17.3 | HTML | [Book] 2019 edition of our front-end development handbook |
| [0xsyr0/Awesome-Cybersecurity-Handbooks](https://github.com/0xsyr0/Awesome-Cybersecurity-Handbooks) | 4,065 | 12.8 | - | A huge chunk of my personal notes since I started playing CTFs and working as a Red Teamer. |
| [snowkylin/tensorflow-handbook](https://github.com/snowkylin/tensorflow-handbook) | 3,925 | 97.9 | Jupyter Notebook | 简单粗暴 TensorFlow 2 / A Concise Handbook of TensorFlow 2 / 一本简明的 TensorFlow 2 入门指导教程 |
| [FrontendMasters/front-end-handbook-2017](https://github.com/FrontendMasters/front-end-handbook-2017) | 3,780 | 6.7 | HTML | 2017 edition of our front-end development guide |
| [Acmesec/PromptJailbreakManual](https://github.com/Acmesec/PromptJailbreakManual) | 3,604 | 13.5 | - | Prompt越狱手册 |
| [Charmve/computer-vision-in-action](https://github.com/Charmve/computer-vision-in-action) | 2,859 | 296.0 | Jupyter Notebook | A computer vision closed-loop learning platform where code can be run interactively online. 学习闭环《计算机 |
| [skr-shop/manuals](https://github.com/skr-shop/manuals) | 2,469 | 2.3 | HTML | Do design No code 💻📱🛒📚  |
| [zero-to-mastery/complete-web-developer-manual](https://github.com/zero-to-mastery/complete-web-developer-manual) | 2,436 | 0.2 | - | All resources and notes from the Complete Web Developer: Zero to Mastery course |
| [datawhalechina/statistical-learning-method-solutions-manual](https://github.com/datawhalechina/statistical-learning-method-solutions-manual) | 2,079 | 11.7 | Jupyter Notebook | 机器学习方法习题解答，在线阅读地址：https://datawhalechina.github.io/statistical-learning-method-solutions-manual |
| [Bloomberg-Beta/Manual](https://github.com/Bloomberg-Beta/Manual) | 1,717 | 0.9 | - | You were probably looking for our website... this is it. We moved our website here, so you can see t |
| [riscv-non-isa/riscv-asm-manual](https://github.com/riscv-non-isa/riscv-asm-manual) | 1,637 | 0.1 | Makefile | RISC-V Assembly Programmer's Manual |
| [0voice/dpdk_engineer_manual](https://github.com/0voice/dpdk_engineer_manual) | 1,517 | 149.8 | - | 【冲破内核瓶颈，让I/O性能飙升】DPDK工程师手册，官方文档，最新视频，开源项目，实战案例，论文，大厂内部ppt，知名工程师一览表 |
| [ligi/SurvivalManual](https://github.com/ligi/SurvivalManual) | 1,280 | 7.6 | Kotlin | Libre Survival Manual for Android with offline in mind |
| [githubnext/copilot-workspace-user-manual](https://github.com/githubnext/copilot-workspace-user-manual) | 1,083 | 15.4 | - | 📖 The user manual for GitHub Copilot Workspace |
| [zhengqigao/PRML-Solution-Manual](https://github.com/zhengqigao/PRML-Solution-Manual) | 1,017 | 14.6 | - | My Own Solution Manual of PRML |

#### 补充类别：interview（30 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [trekhleb/javascript-algorithms](https://github.com/trekhleb/javascript-algorithms) | 196,535 | 14.6 | JavaScript | 📝 Algorithms and data structures implemented in JavaScript with explanations and links to further re |
| [bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises) | 84,198 | 7.8 | Python | Linux, Jenkins, AWS, SRE, Prometheus, Docker, Python, Ansible, Git, Kubernetes, Terraform, OpenStack |
| [youngyangyang04/leetcode-master](https://github.com/youngyangyang04/leetcode-master) | 62,235 | 98.0 | Shell | 《代码随想录》LeetCode 刷题攻略：200道经典题目刷题顺序，共60w字的详细图解，视频难点剖析，50余张思维导图，支持C++，Java，Python，Go，JavaScript等多语言版本，从 |
| [azl397985856/leetcode](https://github.com/azl397985856/leetcode) | 55,758 | 123.6 | JavaScript | LeetCode Solutions: A Record of My Problem Solving Journey.( leetcode题解，记录自己的leetcode解题之路。) |
| [poteto/hiring-without-whiteboards](https://github.com/poteto/hiring-without-whiteboards) | 51,445 | 3.6 | JavaScript | ⭐️  Companies that don't have a broken hiring process |
| [karanpratapsingh/system-design](https://github.com/karanpratapsingh/system-design) | 45,703 | 5.3 | - | Learn how to design systems at scale and prepare for system design interviews |
| [AobingJava/JavaFamily](https://github.com/AobingJava/JavaFamily) | 36,975 | 0.4 | - | 【Java面试+Java学习指南】 一份涵盖大部分Java程序员所需要掌握的核心知识。 |
| [donnemartin/interactive-coding-challenges](https://github.com/donnemartin/interactive-coding-challenges) | 31,742 | 7.6 | Python | 120+ interactive Python coding interview challenges (algorithms and data structures).  Includes Anki |
| [liquidslr/leetcode-company-wise-problems](https://github.com/liquidslr/leetcode-company-wise-problems) | 29,064 | 7.7 | - | Lists of company wise questions. Every csv file in the companies directory corresponds to a list of  |
| [afatcoder/LeetcodeTop](https://github.com/afatcoder/LeetcodeTop) | 20,007 | 0.6 | - | 汇总各大互联网公司容易考察的高频leetcode题🔥 |
| [perkfly/reverse-interview-zh](https://github.com/perkfly/reverse-interview-zh) | 18,511 | 0.1 | - | 技术面试最后反问面试官的话 |
| [Olshansk/interview](https://github.com/Olshansk/interview) | 18,355 | 0.1 | - | Everything you need to prepare for your technical interview |
| [InterviewMap/CS-Interview-Knowledge-Map](https://github.com/InterviewMap/CS-Interview-Knowledge-Map) | 18,257 | 10.6 | - | Build the best interview map. The current content includes JS, network, browser related, performance |
| [wolverinn/Waking-Up](https://github.com/wolverinn/Waking-Up) | 10,278 | 11.2 | - | 计算机基础（计算机网络/操作系统/数据库/Git...）面试问题全面总结，包含详细的follow-up question以及答案；全部采用【问题+追问+答案】的形式，即拿即用，直击互联网大厂面试；可用 |
| [lgwebdream/FE-Interview](https://github.com/lgwebdream/FE-Interview) | 7,198 | 3.4 | JavaScript | 🔥🔥🔥 前端面试，独有前端面试题详解，前端面试刷题必备，1000+前端面试真题，Html、Css、JavaScript、Vue、React、Node、TypeScript、Webpack、算法、网络与 |
| [amusi/AI-Job-Notes](https://github.com/amusi/AI-Job-Notes) | 6,141 | 4.1 | - | AI算法岗求职攻略（涵盖准备攻略、刷题指南、内推和AI公司清单等资料） |
| [liyupi/mianshiya](https://github.com/liyupi/mianshiya) | 5,771 | 0.3 | TypeScript | 持续维护的企业面试题库网站，帮你拿到满意 offer！⭐️ 2026年最新Java面试题、前端面试题、AI大模型面试题、AI Agent面试题、RAG面试题、C++面试题、Go面试题、Python面试 |
| [cirosantilli/x86-bare-metal-examples](https://github.com/cirosantilli/x86-bare-metal-examples) | 5,339 | 1.1 | Assembly | Dozens of minimal operating systems to learn x86 system programming. Tested on Ubuntu 17.10 host in  |
| [hello-java-maker/JavaInterview](https://github.com/hello-java-maker/JavaInterview) | 4,987 | 2.2 | - | 【Java面试+Java后端技术学习指南】：一份通向理想互联网公司的面试指南，包括 Java，技术面试必备基础知识、Leetcode、计算机操作系统、计算机网络、系统设计、分布式、数据库（MySQL、 |
| [iCSToCS/CSBook](https://github.com/iCSToCS/CSBook) | 4,765 | 0.0 | - | 计算机类常用电子书整理，并且附带下载链接，包括Java，Python，Linux，Go，C，C++，数据结构与算法，人工智能，计算机基础，面试，设计模式，数据库，前端等书籍 |
| [GrindGold/pdf](https://github.com/GrindGold/pdf) | 4,700 | 2.7 | - | 📚 计算机经典编程书籍、大黑书、编程电子书、电子书、编程书籍，包括计算机基础、C/C++、Java、Python、面试题、架构设计、算法系列等经典电子书。 |
| [NotFound9/interviewGuide](https://github.com/NotFound9/interviewGuide) | 4,005 | 60.8 | Java | 《大厂面试指北》——包括Java基础、JVM、数据库、mysql、redis、计算机网络、算法、数据结构、操作系统、设计模式、系统设计、框架原理。 |
| [datawhalechina/daily-interview](https://github.com/datawhalechina/daily-interview) | 3,797 | 27.2 | - | Datawhale成员整理的面经，内容包括机器学习，CV，NLP，推荐，开发等，欢迎大家star |
| [ninechapter-algorithm/leetcode-linghu-templete](https://github.com/ninechapter-algorithm/leetcode-linghu-templete) | 3,357 | 8.7 | - | 算法面试必备，推荐刷题网站www.lintcode.com。北大学霸的《LeetCode刷题模板》+V领取: jiuzhangfeifei |
| [0voice/campus_recruitmen_questions](https://github.com/0voice/campus_recruitmen_questions) | 2,668 | 1.2 | - | 2021年最新整理，5000道秋招/提前批/春招/常用面试题（含答案），包括leetcode，校招笔试题，面试题，算法题，语法题。 |
| [DarLiner/Algorithm_Interview_Notes-Chinese](https://github.com/DarLiner/Algorithm_Interview_Notes-Chinese) | 2,476 | 220.0 | Python | 2018/2019/校招/春招/秋招/自然语言处理(NLP)/深度学习(Deep Learning)/机器学习(Machine Learning)/C/C++/Python/面试笔记，此外，还包括创建 |
| [0voice/algorithm-structure](https://github.com/0voice/algorithm-structure) | 2,282 | 35.3 | C | 2021年最新总结 500个常用数据结构，算法，算法导论，面试常用，大厂高级工程师整理总结 |
| [0voice/ffmpeg_develop_doc](https://github.com/0voice/ffmpeg_develop_doc) | 2,182 | 226.3 | C | 2023年，最新音视频学习资料整理，项目（调试可用），ffmpeg命令手册，文章，编解码论文，视频讲解，面试题全套资料 |
| [LjyYano/Thinking_in_Java_MindMapping](https://github.com/LjyYano/Thinking_in_Java_MindMapping) | 1,682 | 35.2 | Python | 编程笔记、 AI 学习、观影指南、读书笔记、生活感悟、游戏记录 |
| [0voice/Career_planning_path](https://github.com/0voice/Career_planning_path) | 1,385 | 1.2 | - | 2025年程序员找工作求职最新总结，学生阶段的困境解决，从简历到面试的全方位解析，从实习到全职的学习规划，就业必备技能与资源推荐。 |

#### 补充类别：awesome-arch（23 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [DovAmir/awesome-design-patterns](https://github.com/DovAmir/awesome-design-patterns) | 48,642 | 0.1 | - | A curated list of software and architecture related design patterns. |
| [ashishps1/awesome-system-design-resources](https://github.com/ashishps1/awesome-system-design-resources) | 40,824 | 2.3 | Java | Learn System Design concepts and prepare for interviews using free resources. |
| [kuchin/awesome-cto](https://github.com/kuchin/awesome-cto) | 35,358 | 0.1 | - | A curated and opinionated list of resources for Chief Technology Officers, with the emphasis on star |
| [oxnr/awesome-bigdata](https://github.com/oxnr/awesome-bigdata) | 14,538 | 1.0 | - | A curated list of awesome big data frameworks, ressources and other awesomeness. |
| [mfornos/awesome-microservices](https://github.com/mfornos/awesome-microservices) | 14,489 | 1.3 | - | A curated list of Microservice Architecture related principles and technologies. |
| [dastergon/awesome-sre](https://github.com/dastergon/awesome-sre) | 13,453 | 1.2 | - | A curated list of Site Reliability and Production Engineering resources. |
| [madd86/awesome-system-design](https://github.com/madd86/awesome-system-design) | 12,426 | 1.8 | - | A curated list of awesome System Design (A.K.A. Distributed Systems) resources.  |
| [mehdihadeli/awesome-software-architecture](https://github.com/mehdihadeli/awesome-software-architecture) | 11,578 | 3.0 | - | 📚 A curated list of awesome articles, videos, and other resources to learn and practice software arc |
| [toutiaoio/awesome-architecture](https://github.com/toutiaoio/awesome-architecture) | 9,675 | 0.1 | - | 架构师技术图谱，助你早日成为架构师 |
| [greatfrontend/awesome-front-end-system-design](https://github.com/greatfrontend/awesome-front-end-system-design) | 8,439 | 0.3 | - | Curated front end system design resources for interviews and learning |
| [onmyway133/awesome-ios-architecture](https://github.com/onmyway133/awesome-ios-architecture) | 5,264 | 0.8 | - | :japanese_castle: Better ways to structure iOS apps |
| [cmhungsteve/Awesome-Transformer-Attention](https://github.com/cmhungsteve/Awesome-Transformer-Attention) | 5,049 | 5.8 | - | An ultimately comprehensive paper list of Vision Transformer/Attention, including papers, codes, and |
| [zhashkevych/awesome-backend](https://github.com/zhashkevych/awesome-backend) | 3,438 | 0.0 | - | 🚀 A curated and opinionated list of resources (English & Russian) for Backend developers / Структури |
| [simonaronsson/awesome-software-architecture](https://github.com/simonaronsson/awesome-software-architecture) | 2,872 | 0.2 | - | A curated list of resources on software architecture |
| [study8677/awesome-architecture](https://github.com/study8677/awesome-architecture) | 2,186 | 1.7 | Vue | 🧭 Architecture-first system design: 26 bilingual tutorials, 25 architecture templates, and 6 end-to- |
| [innovation-cat/Awesome-Federated-Machine-Learning](https://github.com/innovation-cat/Awesome-Federated-Machine-Learning) | 2,090 | 0.4 | - | Everything about federated learning, including research papers, books, codes, tutorials, videos and  |
| [chaoyanghe/Awesome-Federated-Learning](https://github.com/chaoyanghe/Awesome-Federated-Learning) | 2,016 | 0.2 | - | FedML - The Research and Production Integrated Federated Learning Library: https://fedml.ai |
| [lukemurraynz/awesome-azure-architecture](https://github.com/lukemurraynz/awesome-azure-architecture) | 1,720 | 2.0 | - | AWESOME-Azure-Architecture - https://aka.ms/AwesomeAzureArchitecture |
| [androiddevnotes/awesome-jetpack-compose-learning-resources](https://github.com/androiddevnotes/awesome-jetpack-compose-learning-resources) | 1,518 | 4.5 | Kotlin | 👓 A continuously updated list of learning Jetpack Compose for Android apps. |
| [Juude/Awesome-Android-Architecture](https://github.com/Juude/Awesome-Android-Architecture) | 1,513 | 0.0 | - | Android架构合集 |
| [DjangoEx/awesome-python-resources](https://github.com/DjangoEx/awesome-python-resources) | 1,454 | 3.6 | - | Awesome Python Resources |
| [gokayfem/awesome-vlm-architectures](https://github.com/gokayfem/awesome-vlm-architectures) | 1,306 | 53.5 | Markdown | Curated visual catalog of 155+ vision-language model (VLM/MLLM) architectures: papers, diagrams, tra |
| [markdtw/awesome-architecture-search](https://github.com/markdtw/awesome-architecture-search) | 1,190 | 0.1 | - | A curated list of awesome architecture search resources |

#### 补充类别：other（20 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [ruanyf/weekly](https://github.com/ruanyf/weekly) | 100,932 | 7.7 | - | 科技爱好者周刊，每周五发布 |
| [datawhalechina/happy-llm](https://github.com/datawhalechina/happy-llm) | 33,119 | 52.1 | Jupyter Notebook | 📚 从零开始构建大模型 |
| [ruanyf/jstraining](https://github.com/ruanyf/jstraining) | 20,018 | 4.0 | - | 全栈工程师培训材料 |
| [braydie/HowToBeAProgrammer](https://github.com/braydie/HowToBeAProgrammer) | 16,308 | 0.9 | - | A guide on how to be a Programmer - originally published by Robert L Read |
| [origin-bi/rust-by-practice](https://github.com/origin-bi/rust-by-practice) | 14,707 | 2.8 | Rust | Rust By Practice will evolve into Origin. |
| [talkgo/night](https://github.com/talkgo/night) | 12,289 | 60.8 | Go | Weekly Go Online Meetup via Bilibili｜Go 夜读｜通过 bilibili 在线直播的方式分享 Go 相关的技术话题，每天大家在微信/telegram/Slack 上 |
| [datawhalechina/all-in-rag](https://github.com/datawhalechina/all-in-rag) | 10,513 | 82.1 | Python | 🔍大模型应用开发实战一：RAG 技术全栈指南，在线阅读地址：https://datawhalechina.github.io/all-in-rag/ |
| [datawhalechina/so-large-lm](https://github.com/datawhalechina/so-large-lm) | 7,591 | 31.3 | - | 大模型基础: 一文了解大模型基础知识 |
| [datawhalechina/tiny-universe](https://github.com/datawhalechina/tiny-universe) | 5,022 | 23.1 | Jupyter Notebook | 《大模型白盒子构建指南》：一个全手搓的Tiny-Universe |
| [datawhalechina/competition-baseline](https://github.com/datawhalechina/competition-baseline) | 4,757 | 27.3 | Jupyter Notebook | 数据挖掘、计算机视觉、自然语言处理、推荐系统竞赛知识、代码、思路 |
| [datawhalechina/llms-from-scratch-cn](https://github.com/datawhalechina/llms-from-scratch-cn) | 4,333 | 40.9 | Jupyter Notebook | 仅需Python基础，从0构建大语言模型；从0逐步构建GLM4\Llama3\RWKV6， 深入理解大模型原理 |
| [foxsen/archbase](https://github.com/foxsen/archbase) | 3,335 | 232.5 | TeX | 教科书《计算机体系结构基础》（胡伟武等，第三版）的开源版本 |
| [datawhalechina/every-embodied](https://github.com/datawhalechina/every-embodied) | 3,301 | 952.6 | Python | 仅需Python基础，从0构建自己的具身智能机器人；从0逐步构建VLA/OpenVLA/SmolVLA/Pi0， 深入理解具身智能 |
| [datawhalechina/hugging-llm](https://github.com/datawhalechina/hugging-llm) | 3,063 | 156.0 | Jupyter Notebook | HuggingLLM, Hugging Future. |
| [datawhalechina/whale-quant](https://github.com/datawhalechina/whale-quant) | 2,731 | 33.2 | Jupyter Notebook | 本项目为量化开源课程，可以帮助人们快速掌握量化金融知识以及使用Python进行量化开发的能力。 |
| [ruanyf/simple-bash-scripts](https://github.com/ruanyf/simple-bash-scripts) | 1,935 | 0.1 | Shell | A collection of simple Bash scripts |
| [ruanyf/react-babel-webpack-boilerplate](https://github.com/ruanyf/react-babel-webpack-boilerplate) | 1,133 | 0.1 | JavaScript | a boilerplate for React-Babel-Webpack project |
| [ruanyf/articles](https://github.com/ruanyf/articles) | 1,021 | 19.4 | Makefile | personal articles |
| [ruanyf/es-checker](https://github.com/ruanyf/es-checker) | 1,019 | 0.6 | JavaScript | A feature detection library for ECMAScript in node.js and browser. |
| [wx-chevalier/web-examples](https://github.com/wx-chevalier/web-examples) | 873 | 42.2 | JavaScript | Lucid & Futuristic Production Boilerplates For Frontend(Web) Apps, React/RN/Vue, with TypeScript(Opt |

#### 补充类别：awesome-security（17 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [vitalysim/Awesome-Hacking-Resources](https://github.com/vitalysim/Awesome-Hacking-Resources) | 17,338 | 0.3 | - | A collection of hacking / penetration testing resources to make you better! |
| [qazbnm456/awesome-web-security](https://github.com/qazbnm456/awesome-web-security) | 13,717 | 1.2 | Python | 🐶 A curated list of Web Security materials and resources. |
| [k4m4/movies-for-hackers](https://github.com/k4m4/movies-for-hackers) | 11,870 | 0.3 | Shell | 🎬 A curated list of movies every hacker & cyberpunk must watch. |
| [apsdehal/awesome-ctf](https://github.com/apsdehal/awesome-ctf) | 11,778 | 0.6 | JavaScript | A curated list of CTF frameworks, libraries, resources and softwares |
| [jason5ng32/MyIP](https://github.com/jason5ng32/MyIP) | 11,721 | 776.6 | JavaScript | The best IP Toolbox. Check your IP address & geolocation, test IP for WebRTC and DNS IP leaks, run a |
| [ashishb/android-security-awesome](https://github.com/ashishb/android-security-awesome) | 9,629 | 0.4 | Makefile | A collection of android security related resources |
| [decalage2/awesome-security-hardening](https://github.com/decalage2/awesome-security-hardening) | 6,519 | 0.2 | - | A collection of awesome security hardening guides, tools and other resources |
| [jaredthecoder/awesome-vehicle-security](https://github.com/jaredthecoder/awesome-vehicle-security) | 4,454 | 1.2 | - | 🚗  A curated list of resources for learning about vehicle security and car hacking. |
| [husnainfareed/awesome-ethical-hacking-resources](https://github.com/husnainfareed/awesome-ethical-hacking-resources) | 3,725 | 0.1 | - | 😎 🔗 Awesome list about all kinds of resources for learning Ethical Hacking and Penetration Testing. |
| [vaib25vicky/awesome-mobile-security](https://github.com/vaib25vicky/awesome-mobile-security) | 3,528 | 0.4 | - | An effort to build a single place for all useful android and iOS security related stuff. All referen |
| [gmh5225/awesome-game-security](https://github.com/gmh5225/awesome-game-security) | 3,404 | 2869.1 | Python | awesome game security [Welcome to PR] |
| [lirantal/awesome-nodejs-security](https://github.com/lirantal/awesome-nodejs-security) | 3,025 | 0.3 | - | Awesome Node.js Security resources |
| [fkie-cad/awesome-embedded-and-iot-security](https://github.com/fkie-cad/awesome-embedded-and-iot-security) | 2,425 | 0.1 | - | A curated list of awesome embedded and IoT security resources. |
| [DropsOfZut/awesome-security-weixin-official-accounts](https://github.com/DropsOfZut/awesome-security-weixin-official-accounts) | 2,262 | 52.4 | - | 网络安全类公众号推荐，欢迎大家推荐 |
| [ExpLife0011/awesome-windows-kernel-security-development](https://github.com/ExpLife0011/awesome-windows-kernel-security-development) | 2,074 | 3.3 | - | windows kernel security development |
| [saeidshirazi/awesome-android-security](https://github.com/saeidshirazi/awesome-android-security) | 2,011 | 0.2 | - | A curated list of Android Security materials and resources For Pentesters and Bug Hunters |
| [hslatman/awesome-industrial-control-system-security](https://github.com/hslatman/awesome-industrial-control-system-security) | 2,003 | 0.1 | Python | A curated list of resources related to Industrial Control System (ICS) security. |

#### 补充类别：awesome-devops-cloud（14 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev) | 133,341 | 10.4 | HTML | A list of SaaS, PaaS and IaaS offerings that have free tiers of interest to devops and infradev |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 52,789 | 34.2 | Python | A hand-picked collection of the finest of resources for the most awesome of agents, Claude Code, the |
| [veggiemonk/awesome-docker](https://github.com/veggiemonk/awesome-docker) | 36,682 | 14.5 | - | :whale: A curated list of Docker resources and projects |
| [awesome-foss/awesome-sysadmin](https://github.com/awesome-foss/awesome-sysadmin) | 34,952 | 1.4 | - | A curated list of amazingly awesome open-source sysadmin resources. |
| [wmariuss/awesome-devops](https://github.com/wmariuss/awesome-devops) | 4,337 | 1.0 | Python | A curated list of awesome DevOps platforms, tools, practices and resources |
| [tomhuang12/awesome-k8s-resources](https://github.com/tomhuang12/awesome-k8s-resources) | 4,210 | 0.3 | - | A curated list of awesome Kubernetes tools and resources. |
| [4ndersonLin/awesome-cloud-security](https://github.com/4ndersonLin/awesome-cloud-security) | 2,480 | 0.1 | - | 🛡️ Awesome Cloud Security Resources ⚔️ |
| [rootsongjc/awesome-cloud-native](https://github.com/rootsongjc/awesome-cloud-native) | 2,434 | 2.2 | HTML | A curated list for awesome cloud native tools, software and tutorials. |
| [teamssix/awesome-cloud-security](https://github.com/teamssix/awesome-cloud-security) | 2,110 | 11.8 | - | awesome cloud security 收集一些国内外不错的云安全资源，该项目主要面向国内的安全人员 |
| [magnologan/awesome-k8s-security](https://github.com/magnologan/awesome-k8s-security) | 2,007 | 1.0 | - | A curated list for Awesome Kubernetes Security resources |
| [Lets-DevOps/awesome-learning](https://github.com/Lets-DevOps/awesome-learning) | 1,657 | 1.0 | - | A curated list for DevOps learning resources. Join the slack channel to discuss more. |
| [stephrobert/awesome-french-devops](https://github.com/stephrobert/awesome-french-devops) | 1,645 | 3.1 | - | Une liste de liens permettant de se former aux outils utilisés dans le domaine du Devops |
| [AcalephStorage/awesome-devops](https://github.com/AcalephStorage/awesome-devops) | 1,093 | 0.0 | - | A curated list of resources for Devops |
| [rohitg00/awesome-devops-mcp-servers](https://github.com/rohitg00/awesome-devops-mcp-servers) | 1,020 | 0.7 | - | A curated list of awesome MCP servers focused on DevOps tools and capabilities. |

#### 补充类别：awesome-network（14 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [ChristosChristofidis/awesome-deep-learning](https://github.com/ChristosChristofidis/awesome-deep-learning) | 28,793 | 0.6 | - | A curated list of awesome Deep Learning tutorials, projects and communities. |
| [terryum/awesome-deep-learning-papers](https://github.com/terryum/awesome-deep-learning-papers) | 26,177 | 0.1 | TeX | The most cited deep learning papers |
| [bharathgs/Awesome-pytorch-list](https://github.com/bharathgs/Awesome-pytorch-list) | 16,642 | 0.8 | - | A comprehensive list of pytorch related content on github,such as different models,implementations,h |
| [rshipp/awesome-malware-analysis](https://github.com/rshipp/awesome-malware-analysis) | 14,146 | 0.6 | - | Defund the Police. |
| [nashory/gans-awesome-applications](https://github.com/nashory/gans-awesome-applications) | 5,101 | 0.2 | - | Curated list of awesome GAN applications and demo |
| [krishnakumarsekar/awesome-quantum-machine-learning](https://github.com/krishnakumarsekar/awesome-quantum-machine-learning) | 3,648 | 9.8 | HTML | Here you can get all the Quantum Machine learning Basics, Algorithms ,Study Materials ,Projects and  |
| [louisfb01/best_AI_papers_2022](https://github.com/louisfb01/best_AI_papers_2022) | 3,183 | 0.2 | - | A curated list of the latest breakthroughs in AI (in 2022) by release date with a clear video explan |
| [zzw922cn/awesome-speech-recognition-speech-synthesis-papers](https://github.com/zzw922cn/awesome-speech-recognition-speech-synthesis-papers) | 3,128 | 0.2 | - | Automatic Speech Recognition (ASR), Speaker Verification, Speech Synthesis, Text-to-Speech (TTS), La |
| [endymecy/awesome-deeplearning-resources](https://github.com/endymecy/awesome-deeplearning-resources) | 3,023 | 296.5 | - | Deep Learning and deep reinforcement learning research papers and some codes |
| [ybayle/awesome-deep-learning-music](https://github.com/ybayle/awesome-deep-learning-music) | 2,981 | 6.0 | TeX | List of articles related to deep learning applied to music |
| [subeeshvasu/Awesome-Learning-with-Label-Noise](https://github.com/subeeshvasu/Awesome-Learning-with-Label-Noise) | 2,717 | 0.4 | - | A curated list of resources for Learning with Noisy Labels |
| [blanboom/awesome-home-networking-cn](https://github.com/blanboom/awesome-home-networking-cn) | 1,862 | 0.2 | - | 家庭网络知识整理 |
| [yassouali/awesome-semi-supervised-learning](https://github.com/yassouali/awesome-semi-supervised-learning) | 1,856 | 0.2 | - | 😎 An up-to-date & curated list of awesome semi-supervised learning papers, methods & resources. |
| [facyber/awesome-networking](https://github.com/facyber/awesome-networking) | 1,267 | 0.0 | - | A collection of awesome networking courses, books, tutorials and other resources |

#### 补充类别：papers（9 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [extreme-assistant/CVPR2024-Paper-Code-Interpretation](https://github.com/extreme-assistant/CVPR2024-Paper-Code-Interpretation) | 12,469 | 1.3 | - | cvpr2024/cvpr2023/cvpr2022/cvpr2021/cvpr2020/cvpr2019/cvpr2018/cvpr2017 论文/代码/解读/直播合集，极市团队整理 |
| [timzhang642/3D-Machine-Learning](https://github.com/timzhang642/3D-Machine-Learning) | 10,191 | 24.3 | - | A resource repository for 3D machine learning |
| [0voice/audio_video_streaming](https://github.com/0voice/audio_video_streaming) | 6,232 | 200.8 | - | 音视频流媒体权威资料整理，500+份文章，论文，视频，实践项目，协议，业界大神名单。 |
| [wzhe06/Ad-papers](https://github.com/wzhe06/Ad-papers) | 4,398 | 195.0 | Python | Papers on Computational Advertising |
| [DSXiangLi/DecryptPrompt](https://github.com/DSXiangLi/DecryptPrompt) | 3,433 | 2990.0 | - | 总结Prompt&LLM论文，开源数据&模型，AIGC应用 |
| [sbrugman/deep-learning-papers](https://github.com/sbrugman/deep-learning-papers) | 3,183 | 63.3 | - | Papers about deep learning ordered by task, date. Current state-of-the-art papers are labelled. |
| [DeepGraphLearning/LiteratureDL4Graph](https://github.com/DeepGraphLearning/LiteratureDL4Graph) | 3,102 | 0.2 | - | A comprehensive collection of recent papers on graph deep learning |
| [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | 3,068 | 1.0 | Python | A Model Context Protocol server for searching and analyzing arXiv papers |
| [0voice/kernel_memory_management](https://github.com/0voice/kernel_memory_management) | 1,282 | 139.4 | - | 总结整理linux内核的内存管理的资料，包含论文，文章，视频，以及应用程序的内存泄露，内存池相关 |

#### 补充类别：os-kernel（8 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [joshbuchea/HEAD](https://github.com/joshbuchea/HEAD) | 30,262 | 0.7 | - | A simple guide to HTML <head> elements |
| [ruanyf/react-demos](https://github.com/ruanyf/react-demos) | 16,445 | 1.9 | JavaScript | a collection of simple demos of React.js |
| [ruanyf/webpack-demos](https://github.com/ruanyf/webpack-demos) | 9,566 | 0.9 | JavaScript | a collection of simple demos of Webpack |
| [jgthms/css-reference](https://github.com/jgthms/css-reference) | 4,900 | 2.1 | HTML | CSS Reference: a free visual guide to the most popular CSS properties |
| [0voice/learning_mind_map](https://github.com/0voice/learning_mind_map) | 2,803 | 28.8 | - | 2021年【思维导图】盒子，C/C++，Golang，Linux，云原生，数据库，DPDK，音视频开发，TCP/IP，数据结构，计算机原理等 |
| [0voice/cpp_backend_awsome_blog](https://github.com/0voice/cpp_backend_awsome_blog) | 2,290 | 8.3 | - | 2023年最新整理 c++后端开发，1000篇优秀博文，含内存，网络，架构设计，高性能，数据结构，基础组件，中间件，分布式相关 |
| [0voice/kernel_new_features](https://github.com/0voice/kernel_new_features) | 1,911 | 73.9 | C | 一个深挖 Linux 内核的新功能特性，以 io_uring, cgroup, ebpf, llvm 为代表，包含开源项目，代码案例，文章，视频，架构脑图等 |
| [0voice/developkit_set](https://github.com/0voice/developkit_set) | 999 | 0.1 | - | 2021年最新总结，值得推荐的c/c++开源框架与库。持续更新中。 |

#### 补充类别：books（6 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [0voice/from_coder_to_expert](https://github.com/0voice/from_coder_to_expert) | 11,219 | 591.0 | - | 2021年最新总结，从程序员到CTO，从专业走向卓越，分享大牛企业内部pdf与PPT |
| [0voice/Introduction-to-Golang](https://github.com/0voice/Introduction-to-Golang) | 8,147 | 227.9 | Go | 【未来服务器端编程语言】最全空降golang资料补给包（满血战斗），包含文章，书籍，作者论文，理论分析，开源框架，云原生，大佬视频，大厂实战分享ppt |
| [xindoo/agentic-design-patterns](https://github.com/xindoo/agentic-design-patterns) | 7,791 | 8.7 | HTML | 谷歌新书Agent设计模式(agentic design patterns)最佳中文版，持续优化。附：在线阅读、pdf和epub电子书下载。  |
| [MuiseDestiny/zotero-reference](https://github.com/MuiseDestiny/zotero-reference) | 2,799 | 2.3 | JavaScript | PDF references add-on for Zotero. |
| [0voice/computer_expert_paper](https://github.com/0voice/computer_expert_paper) | 1,463 | 363.1 | - | 1000+份计算机paper，卡耐基梅隆大学，哈佛，斯坦福，芝加哥大学，MIT，facebook，google，微软，Amazon，twitter等大牛一作，持续更新中 |
| [ruanyf/reading-list](https://github.com/ruanyf/reading-list) | 1,403 | 0.2 | - | Some books I read |

#### 补充类别：resources（4 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [thedaviddias/Front-End-Checklist](https://github.com/thedaviddias/Front-End-Checklist) | 73,607 | 7.7 | MDX | 🗂 The essential checklist for modern web development, for humans and AI agents |
| [thedaviddias/Front-End-Performance-Checklist](https://github.com/thedaviddias/Front-End-Performance-Checklist) | 17,327 | 0.4 | - | 🎮 The only Front-End Performance Checklist that runs faster than the others |
| [thedaviddias/Front-End-Design-Checklist](https://github.com/thedaviddias/Front-End-Design-Checklist) | 5,328 | 0.2 | - | 💎 The Design Checklist for Creative Web Designers and Patient Front-End Developers |
| [jixserver/free-for-dev](https://github.com/jixserver/free-for-dev) | 5,112 | 0.3 | - |  A list of SaaS, PaaS and IaaS offerings that have free tiers of interest to devops and infradev  |

#### 补充类别：algorithm（4 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [greyireland/algorithm-pattern](https://github.com/greyireland/algorithm-pattern) | 15,464 | 4.1 | Go | Algorithm Patterns — the most scientific way to practice, the fastest path to an offer. You deserve  |
| [biaochenxuying/blog](https://github.com/biaochenxuying/blog) | 4,774 | 29.3 | HTML | 大前端技术为主，读书笔记、随笔、理财为辅，做个终身学习者。 |
| [nixzhu/dev-blog](https://github.com/nixzhu/dev-blog) | 3,905 | 1.6 | - | 翻译、开发心得或学习笔记 |
| [Sophia-11/Machine-Learning-Notes](https://github.com/Sophia-11/Machine-Learning-Notes) | 3,782 | 65.6 | - | 周志华《机器学习》手推笔记 |

#### 补充类别：awesome-database（2 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [xephonhq/awesome-time-series-database](https://github.com/xephonhq/awesome-time-series-database) | 889 | 2.7 | JavaScript | :clock7: A curated list of awesome time series databases, benchmarks and papers |
| [sujeet-agrahari/awesome-database-design](https://github.com/sujeet-agrahari/awesome-database-design) | 819 | 0.1 | - | :zap: A collection of resources and tutorials to design a better database schema. |

#### 补充类别：arch-design（1 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [rust-unofficial/patterns](https://github.com/rust-unofficial/patterns) | 8,877 | 5.2 | Handlebars | A catalogue of Rust design patterns, anti-patterns and idioms |


### 2026-08-22 领域定向补充清单（174 个精选：芯片/服务器/硬件/AI/产品研发）

> 第三批 55 组领域检索式新增（详见 §6），文档型过滤 + 教学型保留 + 黑名单清理；完整数据见 import/github-knowledge-survey-2026-08-22/all_items_v3.json（合并 v2 后共 1,872 个）。


### 领域：AI 专项（94 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [huggingface/transformers](https://github.com/huggingface/transformers) | 164,321 | 492.4 | Python | 🤗 Transformers: the model-definition framework for state-of-the-art machine learning models in text, |
| [fighting41love/funNLP](https://github.com/fighting41love/funNLP) | 82,589 | 170.1 | Python | 中英文敏感词、语言检测、中外手机/电话归属地/运营商查询、名字推断性别、手机号抽取、身份证抽取、邮箱抽取、中日文人名库、中文缩写库、拆字词典、词汇情感值、停用词、反动词表、暴恐词表、繁简体转换、英文模 |
| [opendatalab/MinerU](https://github.com/opendatalab/MinerU) | 78,184 | 154.0 | Python | Transforms complex documents like PDFs and Office docs into LLM-ready markdown/JSON for your Agentic |
| [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) | 77,673 | 80.8 | MDX | 🐙 Guides, papers, lessons, notebooks and resources for prompt engineering, context engineering, RAG, |
| [labmlai/annotated_deep_learning_paper_implementations](https://github.com/labmlai/annotated_deep_learning_paper_implementations) | 67,330 | 152.7 | Python | 🧑‍🏫 60+ Implementations/tutorials of deep learning papers with side-by-side notes 📝; including trans |
| [facebookresearch/segment-anything](https://github.com/facebookresearch/segment-anything) | 54,738 | 18.3 | Jupyter Notebook | The repository provides code for running inference with the SegmentAnything Model (SAM), links for d |
| [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) | 47,567 | 28.8 | Python | Learn it. Build it. Ship it for others. |
| [deepspeedai/DeepSpeed](https://github.com/deepspeedai/DeepSpeed) | 42,975 | 242.4 | Python | DeepSpeed is a deep learning optimization library that makes distributed training and inference easy |
| [patchy631/ai-engineering-hub](https://github.com/patchy631/ai-engineering-hub) | 37,080 | 279.2 | Jupyter Notebook | In-depth tutorials on LLMs, RAGs and real-world AI agent applications. |
| [fastai/fastai](https://github.com/fastai/fastai) | 28,118 | 857.6 | Jupyter Notebook | The fastai deep learning library |
| [facebookresearch/sam2](https://github.com/facebookresearch/sam2) | 19,739 | 135.0 | Jupyter Notebook | The repository provides code for running inference with the Meta Segment Anything Model 2 (SAM 2), l |
| [stas00/ml-engineering](https://github.com/stas00/ml-engineering) | 18,683 | 26.2 | Python | Machine Learning Engineering Open Book |
| [meta-llama/llama-cookbook](https://github.com/meta-llama/llama-cookbook) | 18,561 | 273.4 | Jupyter Notebook | Welcome to the Llama Cookbook! This is your go to guide for Building with Llama: Getting started wit |
| [sczhou/CodeFormer](https://github.com/sczhou/CodeFormer) | 18,107 | 17.2 | Python | [NeurIPS 2022] Towards Robust Blind Face Restoration with Codebook Lookup Transformer |
| [apache/brpc](https://github.com/apache/brpc) | 17,592 | 43.6 | C++ | brpc is an Industrial-grade RPC framework using C++ Language, which is often used in high performanc |
| [facebookresearch/detr](https://github.com/facebookresearch/detr) | 15,354 | 12.9 | Python | End-to-End Object Detection with Transformers |
| [ty4z2008/Qix](https://github.com/ty4z2008/Qix) | 15,190 | 2.4 | - | Machine Learning、Deep Learning、PostgreSQL、Distributed System、Node.Js、Golang |
| [seerge/g-helper](https://github.com/seerge/g-helper) | 14,812 | 43.0 | C# | Lightweight Armoury Crate alternative for Asus laptops with nearly the same functionality. Works wit |
| [deeplearning4j/deeplearning4j](https://github.com/deeplearning4j/deeplearning4j) | 14,245 | 797.5 | Java | Suite of tools for deploying and training deep learning models using the JVM. Highlights include mod |
| [apache/tvm](https://github.com/apache/tvm) | 13,675 | 139.3 | Python | Open Machine Learning Compiler Framework |
| [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) | 13,599 | 7.1 | TypeScript | Harness engineering beginner tutorial, from 0 to 1 |
| [NVIDIA/TensorRT](https://github.com/NVIDIA/TensorRT) | 13,273 | 141.8 | C++ | NVIDIA® TensorRT™ is an SDK for high-performance deep learning inference on NVIDIA GPUs. This reposi |
| [halfrost/Halfrost-Field](https://github.com/halfrost/Halfrost-Field) | 13,217 | 104.9 | Go | ✍🏻 Source Code Deep Dives, System Design & Engineering Blogs / Halfrost-Field 冰霜之地：源码解析、系统设计与工程实践笔记  |
| [srush/GPU-Puzzles](https://github.com/srush/GPU-Puzzles) | 12,420 | 0.6 | Jupyter Notebook | Solve puzzles. Learn CUDA. |
| [facebook/astryx](https://github.com/facebook/astryx) | 12,209 | 608.5 | TypeScript | An open source design system that's fully customizable and agent ready |
| [xlite-dev/LeetCUDA](https://github.com/xlite-dev/LeetCUDA) | 11,803 | 307.5 | Cuda | Modern CUDA Learn Notes with PyTorch for Beginners, 200+ CUDA Kernels, Tensor Cores, HGEMM, FA-2 MMA |
| [NielsRogge/Transformers-Tutorials](https://github.com/NielsRogge/Transformers-Tutorials) | 11,747 | 264.5 | Jupyter Notebook | This repository contains demos I made with the Transformers library by HuggingFace. |
| [pingcap/talent-plan](https://github.com/pingcap/talent-plan) | 10,988 | 4.0 | Rust | open source training courses about distributed database and distributed systems |
| [kedro-org/kedro](https://github.com/kedro-org/kedro) | 10,961 | 245.3 | Python | Kedro is a toolbox for production-ready data science. It uses software engineering best practices to |
| [Engineer1999/A-Curated-List-of-ML-System-Design-Case-Studies](https://github.com/Engineer1999/A-Curated-List-of-ML-System-Design-Case-Studies) | 10,950 | 0.2 | - | This repository contains a curated collection of 300+ case studies from over 80 companies, detailing |
| [facebookresearch/xformers](https://github.com/facebookresearch/xformers) | 10,542 | 42.8 | Python | Hackable and optimized Transformers building blocks, supporting a composable construction. |
| [chiphuyen/machine-learning-systems-design](https://github.com/chiphuyen/machine-learning-systems-design) | 10,538 | 1.4 | HTML | A booklet on machine learning systems design with exercises. NOT the repo for the book "Designing Ma |
| [NirantK/awesome-project-ideas](https://github.com/NirantK/awesome-project-ideas) | 9,281 | 0.1 | - | Curated list of Machine Learning, NLP, Vision, Recommender Systems Project Ideas |
| [catboost/catboost](https://github.com/catboost/catboost) | 9,072 | 1664.4 | C++ | A fast, scalable, high performance Gradient Boosting on Decision Trees library, used for ranking, cl |
| [VowpalWabbit/vowpal_wabbit](https://github.com/VowpalWabbit/vowpal_wabbit) | 8,705 | 169.6 | C++ | Vowpal Wabbit is a machine learning system which pushes the frontier of machine learning with techni |
| [facebookresearch/DiT](https://github.com/facebookresearch/DiT) | 8,689 | 6.3 | Python | Official PyTorch Implementation of "Scalable Diffusion Models with Transformers" |
| [poloclub/transformer-explainer](https://github.com/poloclub/transformer-explainer) | 8,435 | 2068.5 | JavaScript | Transformer Explained Visually: Learn How LLM Transformer Models Work with Interactive Visualization |
| [nl8590687/ASRT_SpeechRecognition](https://github.com/nl8590687/ASRT_SpeechRecognition) | 8,381 | 7.9 | Python | A Deep-Learning-Based Chinese Speech Recognition System 基于深度学习的中文语音识别系统 |
| [NirDiamant/Prompt_Engineering](https://github.com/NirDiamant/Prompt_Engineering) | 7,804 | 20.7 | Jupyter Notebook | 22 prompt engineering techniques with hands-on Jupyter Notebook tutorials, from fundamental concepts |
| [facebookresearch/dino](https://github.com/facebookresearch/dino) | 7,612 | 24.4 | Python | PyTorch code for Vision Transformers training with the Self-Supervised learning method DINO |
| [ed-donner/llm_engineering](https://github.com/ed-donner/llm_engineering) | 7,126 | 559.9 | Jupyter Notebook | Repo to accompany my mastering LLM engineering course |
| [deeppavlov/DeepPavlov](https://github.com/deeppavlov/DeepPavlov) | 6,990 | 32.1 | Python | An open source library for deep learning end-to-end dialog systems and chatbots. |
| [tensorflow/serving](https://github.com/tensorflow/serving) | 6,360 | 20.1 | C++ | A flexible, high-performance serving system for machine learning models |
| [WenyuChiou/awesome-agentic-ai-zh](https://github.com/WenyuChiou/awesome-agentic-ai-zh) | 6,201 | 119.0 | Python | A trilingual (繁中 / English / 简中) learning roadmap for agentic AI: from LLM basics to multi-agent sys |
| [ashishps1/learn-ai-engineering](https://github.com/ashishps1/learn-ai-engineering) | 5,944 | 0.0 | - | Learn AI and LLMs from scratch using free resources |
| [chiphuyen/dmls-book](https://github.com/chiphuyen/dmls-book) | 5,212 | 4.9 | - | Summaries and resources for Designing Machine Learning Systems book (Chip Huyen, O'Reilly 2022) |
| [openmlsys/openmlsys](https://github.com/openmlsys/openmlsys) | 4,845 | 50.0 | TeX | 《Machine Learning Systems: Design and Implementation》 (V2 is launching soon） |
| [CarperAI/trlx](https://github.com/CarperAI/trlx) | 4,753 | 46.7 | Python | A repo for distributed training of language models with Reinforcement Learning via Human Feedback (R |
| [facebookincubator/AITemplate](https://github.com/facebookincubator/AITemplate) | 4,724 | 6.7 | Python | AITemplate is a Python framework which renders neural network into high performance CUDA/HIP C++ cod |
| [alirezadir/Production-Level-Deep-Learning](https://github.com/alirezadir/Production-Level-Deep-Learning) | 4,659 | 15.1 | - | A guideline for building practical production-level deep learning systems to be deployed in real wor |
| [HuaizhengZhang/AI-Infra-from-Zero-to-Hero](https://github.com/HuaizhengZhang/AI-Infra-from-Zero-to-Hero) | 4,291 | 0.9 | - | 🚀 Awesome System for Machine Learning ⚡️ AI System Papers and Industry Practice. ⚡️ System for Machi |
| [NVIDIA/DIGITS](https://github.com/NVIDIA/DIGITS) | 4,177 | 50.0 | HTML | Deep Learning GPU Training System |
| [FedML-AI/FedML](https://github.com/FedML-AI/FedML) | 4,062 | 913.6 | Python | FEDML - The unified and scalable ML library for large-scale distributed training, model serving, and |
| [Infatoshi/cuda-course](https://github.com/Infatoshi/cuda-course) | 3,962 | 31.8 | Cuda |  |
| [PaddlePaddle/PARL](https://github.com/PaddlePaddle/PARL) | 3,452 | 47.3 | Python | A high-performance distributed training framework for Reinforcement Learning  |
| [Meirtz/Awesome-Context-Engineering](https://github.com/Meirtz/Awesome-Context-Engineering) | 3,277 | 3.4 | - |  🔥 Comprehensive survey on Context Engineering: from prompt engineering to production-grade AI syste |
| [determined-ai/determined](https://github.com/determined-ai/determined) | 3,235 | 202.9 | Go | Determined is an open-source machine learning platform that simplifies distributed training, hyperpa |
| [webdataset/webdataset](https://github.com/webdataset/webdataset) | 3,166 | 53.1 | Python | A high-performance Python-based I/O system for large (and small) deep learning problems, with strong |
| [mercari/ml-system-design-pattern](https://github.com/mercari/ml-system-design-pattern) | 2,927 | 7.7 | - | System design patterns for machine learning |
| [robi56/Deep-Learning-for-Recommendation-Systems](https://github.com/robi56/Deep-Learning-for-Recommendation-Systems) | 2,883 | 0.0 | - | This repository contains Deep Learning based articles , paper and repositories for Recommender Syste |
| [MichalDanielDobrzanski/DeepLearningPython](https://github.com/MichalDanielDobrzanski/DeepLearningPython) | 2,830 | 16.4 | Python | neuralnetworksanddeeplearning.com integrated scripts for Python 3.5.2 and Theano with CUDA support |
| [wzhe06/SparrowRecSys](https://github.com/wzhe06/SparrowRecSys) | 2,775 | 65.0 | Python | A Deep Learning Recommender System |
| [guyulongcs/Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising](https://github.com/guyulongcs/Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising) | 2,585 | 1120.9 | Python | Awesome Deep Learning papers for industrial Search, Recommendation and Advertisement. They focus on  |
| [dipanjanS/practical-machine-learning-with-python](https://github.com/dipanjanS/practical-machine-learning-with-python) | 2,383 | 118.4 | Jupyter Notebook | Master the essential skills needed to recognize and solve complex real-world problems with Machine L |
| [agno-agi/dash](https://github.com/agno-agi/dash) | 2,251 | 0.3 | Python | A self-learning data agent built with systems engineering principles. It grounds answers in 6 layers |
| [dyweb/papers-notebook](https://github.com/dyweb/papers-notebook) | 2,207 | 0.1 | - | :page_facing_up: :cn: :page_with_curl: 论文阅读笔记（分布式系统、虚拟化、机器学习）Papers Notebook (Distributed System, Vi |
| [luispedro/BuildingMachineLearningSystemsWithPython](https://github.com/luispedro/BuildingMachineLearningSystemsWithPython) | 2,133 | 183.3 | Python | Source Code for the book Building Machine Learning Systems with Python |
| [ICT-BDA/EasyML](https://github.com/ICT-BDA/EasyML) | 1,976 | 15.2 | Java | Easy Machine Learning is a general-purpose dataflow-based system for easing the process of applying  |
| [ashvardanian/less_slow.cpp](https://github.com/ashvardanian/less_slow.cpp) | 1,920 | 2.0 | C++ | Playing around "Less Slow" coding practices in C++ 20, C, CUDA, PTX, & Assembly, from numerics & SIM |
| [uber/petastorm](https://github.com/uber/petastorm) | 1,891 | 2.6 | Python | Petastorm library enables single machine or distributed training and evaluation of deep learning mod |
| [indigo-dc/udocker](https://github.com/indigo-dc/udocker) | 1,779 | 6.6 | Python | A basic user tool to execute simple docker containers in batch or interactive systems without root p |
| [basicmi/AI-Chip](https://github.com/basicmi/AI-Chip) | 1,714 | 116.0 | PHP | A list of ICs and IPs for AI, Machine Learning and Deep Learning. |
| [zwang4/awesome-machine-learning-in-compilers](https://github.com/zwang4/awesome-machine-learning-in-compilers) | 1,686 | 0.6 | - | Must read research papers and links to tools and datasets that are related to using machine learning |
| [intelligent-machine-learning/dlrover](https://github.com/intelligent-machine-learning/dlrover) | 1,677 | 208.1 | Python | DLRover: An Automatic Distributed Deep Learning System |
| [SciML/ModelingToolkit.jl](https://github.com/SciML/ModelingToolkit.jl) | 1,658 | 1347.1 | Julia | An acausal modeling framework for automatically parallelized scientific machine learning (SciML) in  |
| [benthecoder/yt-channels-DS-AI-ML-CS](https://github.com/benthecoder/yt-channels-DS-AI-ML-CS) | 1,620 | 0.1 | - | A comprehensive list of 180+ YouTube Channels for Data Science,  Data Engineering, Machine Learning, |
| [ai-infra-curriculum/ai-infra-engineer-learning](https://github.com/ai-infra-curriculum/ai-infra-engineer-learning) | 1,618 | 2.0 | Python | AI Infrastructure Engineer Learning Track - Production ML infrastructure curriculum (2-4 years exper |
| [JasperSnoek/spearmint](https://github.com/JasperSnoek/spearmint) | 1,392 | 0.6 | Python | Spearmint is a package to perform Bayesian optimization according to the algorithms outlined in the  |
| [DataTalksClub/ai-dev-tools-zoomcamp](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp) | 1,389 | 8.7 | Python | A free, hands-on course on using AI developer tools to build, test, deploy, extend, and audit softwa |
| [mallahyari/ml-practical-usecases](https://github.com/mallahyari/ml-practical-usecases) | 1,294 | 0.4 | - | A database of 650 Machine Learning (ML) system design case studies from 100+ companies. |
| [mlc-ai/modern-gpu-programming-for-mlsys](https://github.com/mlc-ai/modern-gpu-programming-for-mlsys) | 1,194 | 50.8 | HTML | A tutorial on modern GPU programming for machine learning systems |
| [dreddnafious/thereisnospoon](https://github.com/dreddnafious/thereisnospoon) | 1,185 | 3.1 | Python | A machine learning primer built from first principles. For engineers who want to reason about ML sys |
| [NVIDIA-Merlin/NVTabular](https://github.com/NVIDIA-Merlin/NVTabular) | 1,150 | 100.1 | Python | NVTabular is a feature engineering and preprocessing library for tabular data designed to quickly an |
| [Akramz/Hands-on-Machine-Learning-with-Scikit-Learn-Keras-and-TensorFlow](https://github.com/Akramz/Hands-on-Machine-Learning-with-Scikit-Learn-Keras-and-TensorFlow) | 1,058 | 70.2 | Jupyter Notebook | Notes & exercise solutions of Part I from the book: "Hands-On ML with Scikit-Learn, Keras & TensorFl |
| [junfanz1/Awesome-Senior-Engineer-Algorithms-Review](https://github.com/junfanz1/Awesome-Senior-Engineer-Algorithms-Review) | 982 | 7.0 | - | Data Structure Algorithms, (GenAI/ML) System Design, Machine Learning, DevOps coding interview pract |
| [wuwenjie1992/StarryDivineSky](https://github.com/wuwenjie1992/StarryDivineSky) | 945 | 22.9 | - | 精选了10K+项目，包括机器学习、深度学习、NLP、GNN、推荐系统、生物医药、机器视觉、前后端开发等内容。Selected more than 10k+ projects, including ma |
| [NVIDIA-Merlin/Merlin](https://github.com/NVIDIA-Merlin/Merlin) | 905 | 39.0 | Python | NVIDIA Merlin is an open source library providing end-to-end GPU-accelerated recommender systems, fr |
| [stratosphereips/StratosphereLinuxIPS](https://github.com/stratosphereips/StratosphereLinuxIPS) | 882 | 447.0 | Python | Slips, a free software behavioral Python intrusion prevention system (IDS/IPS) that uses machine lea |
| [dennisdoomen/CSharpGuidelines](https://github.com/dennisdoomen/CSharpGuidelines) | 776 | 22.7 | JavaScript | A set of coding guidelines for C# up to v14, design principles, layout rules and Agent Skills for im |
| [flink-extended/dl-on-flink](https://github.com/flink-extended/dl-on-flink) | 695 | 55.1 | Java | Deep Learning on Flink aims to integrate Flink and deep learning frameworks (e.g. TensorFlow, PyTorc |
| [tmulc18/Distributed-TensorFlow-Guide](https://github.com/tmulc18/Distributed-TensorFlow-Guide) | 641 | 0.1 | Python | Distributed TensorFlow basics and examples of training algorithms |
| [LambdaLabsML/distributed-training-guide](https://github.com/LambdaLabsML/distributed-training-guide) | 629 | 0.6 | Python | Best practices & guides on how to write distributed pytorch training code |
| [cerndb/dist-keras](https://github.com/cerndb/dist-keras) | 622 | 55.9 | Python | Distributed Deep Learning, with a focus on distributed training, using Keras and Apache Spark. |
| [product-on-purpose/pm-skills](https://github.com/product-on-purpose/pm-skills) | 559 | 50.1 | JavaScript | 68 plug-and-play, best-practice product management skills for AI agents: 30 Triple Diamond phase + 1 |

### 领域：产品研发/工程管理（34 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | 365,322 | 11.0 | Python | Learn how to design large-scale systems. Prep for the system design interview.  Includes Anki flashc |
| [karanpratapsingh/system-design](https://github.com/karanpratapsingh/system-design) | 45,703 | 5.3 | - | Learn how to design systems at scale and prepare for system design interviews |
| [DataTalksClub/data-engineering-zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) | 44,799 | 13.6 | Jupyter Notebook | Data Engineering Zoomcamp is a free 9-week course on building production-ready data pipelines. The n |
| [ashishps1/awesome-system-design-resources](https://github.com/ashishps1/awesome-system-design-resources) | 40,825 | 2.3 | Java | Learn System Design concepts and prepare for interviews using free resources. |
| [architecture-decision-record/architecture-decision-record](https://github.com/architecture-decision-record/architecture-decision-record) | 16,708 | 0.5 | - | Architecture decision record (ADR) examples for software planning, IT leadership, and template docum |
| [Sairyss/domain-driven-hexagon](https://github.com/Sairyss/domain-driven-hexagon) | 14,879 | 7.3 | TypeScript | Learn Domain-Driven Design, software architecture, design patterns, best practices. Code examples in |
| [ZachGoldberg/Startup-CTO-Handbook](https://github.com/ZachGoldberg/Startup-CTO-Handbook) | 14,192 | 6.2 | - | The Startup CTO's Handbook, a book covering leadership, management and technical topics for leaders  |
| [mehdihadeli/awesome-software-architecture](https://github.com/mehdihadeli/awesome-software-architecture) | 11,578 | 3.0 | - | 📚 A curated list of awesome articles, videos, and other resources to learn and practice software arc |
| [mhadidg/software-architecture-books](https://github.com/mhadidg/software-architecture-books) | 11,305 | 0.0 | - | A comprehensive list of books on Software Architecture. |
| [jasontang-ai/Context-Engineering](https://github.com/jasontang-ai/Context-Engineering) | 9,223 | 39.0 | Python | "Context engineering is the delicate art and science of filling the context window with just the rig |
| [greatfrontend/awesome-front-end-system-design](https://github.com/greatfrontend/awesome-front-end-system-design) | 8,439 | 0.3 | - | Curated front end system design resources for interviews and learning |
| [xirong/my-git](https://github.com/xirong/my-git) | 7,400 | 22.1 | HTML | Git as the control plane for AI-native software engineering / AI Native 软件工程的 Git 变更控制手册 |
| [gregorojstersek/resources-to-become-a-great-engineering-leader](https://github.com/gregorojstersek/resources-to-become-a-great-engineering-leader) | 7,336 | 0.1 | - | List of books, blogs, newsletters and people! |
| [0xZ0F/Z0FCourse_ReverseEngineering](https://github.com/0xZ0F/Z0FCourse_ReverseEngineering) | 5,899 | 30.3 | C++ | Reverse engineering focusing on x64 Windows. |
| [vicoyeh/pointers-for-software-engineers](https://github.com/vicoyeh/pointers-for-software-engineers) | 5,737 | 0.1 | - | A curated list of topics to start learning software engineering |
| [deusyu/harness-engineering](https://github.com/deusyu/harness-engineering) | 5,586 | 31.5 | JavaScript | Harness Engineering 学习指南 — 从概念理解到独立实践的深度学习档案 |
| [alexeygrigorev/ai-engineering-field-guide](https://github.com/alexeygrigorev/ai-engineering-field-guide) | 5,328 | 72.0 | HTML | Research into AI engineering interview assignments, take-home challenges, and hiring practices from  |
| [javabuddy/best-system-design-resources](https://github.com/javabuddy/best-system-design-resources) | 4,425 | 0.1 | - | A collection of best resources to learn System Design, Software architecture, and prepare for System |
| [nas5w/interview-guide](https://github.com/nas5w/interview-guide) | 4,305 | 16.6 | Astro | An opinionated, actionable guide for software engineering interviews. |
| [evolutionary-architecture/evolutionary-architecture-by-example](https://github.com/evolutionary-architecture/evolutionary-architecture-by-example) | 3,498 | 10.2 | C# | Navigate the complex landscape of .NET software architecture with our step-by-step, story-like guide |
| [stemmlerjs/software-design-and-architecture-roadmap](https://github.com/stemmlerjs/software-design-and-architecture-roadmap) | 3,404 | 0.0 | - | 🧱 The software design and architecture roadmap for any developer |
| [cuizhenjie/software-engineering-document](https://github.com/cuizhenjie/software-engineering-document) | 3,344 | 5.3 | - | 软件工程常用文档模板及示例：可行性分析报告、开发计划、需求分析文档、概要设计文档、详细设计文档、用户操作手册、测试计划、测试分析报告、开发进度报告、项目开发总结报告、软件维护手册等 |
| [joebew42/study-path](https://github.com/joebew42/study-path) | 3,002 | 0.6 | - | A curated, open, and ever-evolving learning path focused on practices of software development, princ |
| [event-catalog/eventcatalog](https://github.com/event-catalog/eventcatalog) | 2,836 | 219.9 | TypeScript | Documentation tool built for software architecture. Document your domains, services, events and sche |
| [engineering-management/awesome-engineering-management](https://github.com/engineering-management/awesome-engineering-management) | 2,758 | 0.2 | - | Pointers and tools for learning and day-to-day practice of engineering management & leadership. |
| [zero-equals-false/awesome-programming-books](https://github.com/zero-equals-false/awesome-programming-books) | 2,107 | 0.0 | - | 📚 A curated list of awesome programming books (Algorithms and data structures, Artificial intelligen |
| [Azure/Enterprise-Scale](https://github.com/Azure/Enterprise-Scale) | 1,953 | 100.0 | PowerShell | The Azure Landing Zones (Enterprise-Scale) architecture provides prescriptive guidance coupled with  |
| [jesselpalmer/the-engineering-managers-booklist](https://github.com/jesselpalmer/the-engineering-managers-booklist) | 1,690 | 0.2 | - | Books for people who are or aspire to manage/lead team(s) of software engineers |
| [Mahmoudz/Porto](https://github.com/Mahmoudz/Porto) | 1,638 | 81.7 | - | A software architectural pattern that provides a comprehensive set of guidelines, principles, and pa |
| [raylene/eng-handbook](https://github.com/raylene/eng-handbook) | 1,566 | 0.1 | - | A developer's guide to management: an open-sourced handbook for leading software engineering teams. |
| [18F/development-guide](https://github.com/18F/development-guide) | 1,469 | 4.3 | HTML | A set of guidelines and best practices for an awesome software engineering team |
| [arc42/arc42-template](https://github.com/arc42/arc42-template) | 1,268 | 161.6 | Dockerfile | arc42 - the template for software architecture documentation and communication |
| [ryanmcdermott/3rs-of-software-architecture](https://github.com/ryanmcdermott/3rs-of-software-architecture) | 1,116 | 0.1 | JavaScript | A guide on how to write readable, reusable, and refactorable software |
| [jafari-dev/oop-expert-with-typescript](https://github.com/jafari-dev/oop-expert-with-typescript) | 632 | 0.4 | HTML | A complete guide for learning object oriented programming pillars, SOLID principles and design patte |

### 领域：硬件/嵌入式（20 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [harvard-edge/cs249r_book](https://github.com/harvard-edge/cs249r_book) | 27,973 | 2731.5 | Python | Machine Learning Systems |
| [s-matyukevich/raspberry-pi-os](https://github.com/s-matyukevich/raspberry-pi-os) | 13,911 | 2.0 | C | Learning operating system development using Linux kernel and Raspberry Pi |
| [m3y54m/Embedded-Engineering-Roadmap](https://github.com/m3y54m/Embedded-Engineering-Roadmap) | 12,893 | 3.8 | - | Comprehensive roadmap for aspiring Embedded Systems Engineers, featuring a curated list of learning  |
| [wireviz/WireViz](https://github.com/wireviz/WireViz) | 5,226 | 20.0 | Python | Easily document cables and wiring harnesses. |
| [ruiqimao/keyboard-pcb-guide](https://github.com/ruiqimao/keyboard-pcb-guide) | 4,933 | 0.0 | - | Guide on how to design keyboard PCBs with KiCad |
| [jaredthecoder/awesome-vehicle-security](https://github.com/jaredthecoder/awesome-vehicle-security) | 4,454 | 1.2 | - | 🚗  A curated list of resources for learning about vehicle security and car hacking. |
| [huangyz0918/Hackintosh-Installer-University](https://github.com/huangyz0918/Hackintosh-Installer-University) | 3,992 | 116.4 | Rich Text Format | Open source tutorial & information collector for hackintosh installation. |
| [ace-trump-tech/MindPaw](https://github.com/ace-trump-tech/MindPaw) | 2,405 | 2.0 | C++ | 🐕 MindPaw — 基于 ESP8266 的桌面级四足机器狗，支持语音交互 (HLK-V20)、手势识别 (OV2640+轻量MLP)、AI 对话 (豆包大模型)、PAD 情感计算、WiFi 网页 |
| [0voice/EmbeddedSoftwareLearn](https://github.com/0voice/EmbeddedSoftwareLearn) | 2,355 | 8.6 | - | 欢迎来到本项目，这是一份面向中文社区的系统、全面且贴近实战的嵌入式软件开发学习路线和知识点总结。涵盖范围包括 C/C++、嵌入式开发、驱动开发、计算机网络原理、RTOS、嵌入式 Linux、网络通信与 |
| [wuxiaolie/Knowledge-Notes](https://github.com/wuxiaolie/Knowledge-Notes) | 1,747 | 317.5 | C | 开放个人技术学习过程中整理记录的所有笔记。包含C/C++，算法，Linux基础，Linux驱动，STM32+RTOS；嵌入式，总线协议，操作系统，计算机网络，人工智能；工程实践，项目开发，软件使用，校 |
| [hardware/mailserver](https://github.com/hardware/mailserver) | 1,288 | 0.9 | Shell | :warning: UNMAINTAINED - Simple and full-featured mail server using Docker  |
| [twelvesec/PwnPad](https://github.com/twelvesec/PwnPad) | 1,186 | 16.7 | C++ | PwnPad is an affordable, hands-on hardware hacking platform built for practical learning. It feature |
| [KiCad/kicad-library](https://github.com/KiCad/kicad-library) | 802 | 659.3 | HTML | The schematic and 3D libraries for KiCad 4.0.  Note that the footprint libraries are the *.pretty re |
| [skaiui2/SKRTOS_sparrow](https://github.com/skaiui2/SKRTOS_sparrow) | 492 | 26.3 | C | A modular RTOS microkernel with tutorials—built for embedded systems, teaching, and architecture res |
| [FidoProject/Fido](https://github.com/FidoProject/Fido) | 463 | 52.4 | C++ | A lightweight C++ machine learning library for embedded electronics and robotics. |
| [joaocarvalhoopen/Guides_Linux-Programming-Electronics-Aeronautics](https://github.com/joaocarvalhoopen/Guides_Linux-Programming-Electronics-Aeronautics) | 460 | 0.0 | - | All my little guides in one place. Linux, Programming, Embedded, Electronics, Aeronautics and Guitar |
| [xym-ee/electronics](https://github.com/xym-ee/electronics) | 456 | 14.0 | Python | 【笔记】电子学基础。电路分析、模拟电路、数字电路、电力电子。 |
| [zszszszsz/.config](https://github.com/zszszszsz/.config) | 349 | 0.0 | Shell | # # Automatically generated file; DO NOT EDIT. # OpenWrt Configuration # CONFIG_MODULES=y CONFIG_HAV |
| [phodal/awesome-iot-document](https://github.com/phodal/awesome-iot-document) | 346 | 1.5 | - | Awesome IoT Documents. [Deprecated] Internet of Things Document  |
| [chrisneagu/FTC-Skystone-Dark-Angels-Romania-2020](https://github.com/chrisneagu/FTC-Skystone-Dark-Angels-Romania-2020) | 304 | 78.1 | Java | NOTICE This repository contains the public FTC SDK for the SKYSTONE (2019-2020) competition season.  |

### 领域：芯片/半导体（19 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [mytechnotalent/Reverse-Engineering](https://github.com/mytechnotalent/Reverse-Engineering) | 14,133 | 342.4 | Assembly | A FREE comprehensive reverse engineering tutorial covering x86, x64, 32-bit/64-bit ARM, 8-bit AVR an |
| [adam-maj/tiny-gpu](https://github.com/adam-maj/tiny-gpu) | 12,860 | 8.5 | SystemVerilog | A minimal GPU design in Verilog to learn how GPUs work from the ground up |
| [facebook/chisel](https://github.com/facebook/chisel) | 9,179 | 3.5 | Python | Chisel is a collection of LLDB commands to assist debugging iOS apps. |
| [PaddlePaddle/Paddle-Lite](https://github.com/PaddlePaddle/Paddle-Lite) | 7,272 | 321.8 | C++ | PaddlePaddle High Performance Deep Learning Inference Engine for Mobile and Edge (飞桨高性能深度学习端侧推理引擎） |
| [BrunoLevy/learn-fpga](https://github.com/BrunoLevy/learn-fpga) | 3,644 | 233.8 | C++ | Learning FPGA, yosys, nextpnr, and RISC-V  |
| [tirthajyoti/Papers-Literature-ML-DL-RL-AI](https://github.com/tirthajyoti/Papers-Literature-ML-DL-RL-AI) | 2,937 | 506.7 | - | Highly cited and useful papers related to machine learning, deep learning, AI, game theory, reinforc |
| [rcore-os/rCore-Tutorial-v3](https://github.com/rcore-os/rCore-Tutorial-v3) | 2,099 | 50.9 | Rust | Let's write an OS which can run on RISC-V in Rust from scratch! |
| [freechipsproject/chisel-bootcamp](https://github.com/freechipsproject/chisel-bootcamp) | 1,150 | 1.7 | Jupyter Notebook | Generator Bootcamp Material: Learn Chisel the Right Way |
| [limbo018/DREAMPlace](https://github.com/limbo018/DREAMPlace) | 1,041 | 18.5 | C++ | Deep learning toolkit-enabled VLSI placement |
| [schoeberl/chisel-book](https://github.com/schoeberl/chisel-book) | 926 | 13.4 | TeX | Digital Design with Chisel |
| [Obijuan/open-fpga-verilog-tutorial](https://github.com/Obijuan/open-fpga-verilog-tutorial) | 864 | 37.5 | Verilog | Learn how to design digital systems and synthesize them into an FPGA using only opensource tools |
| [xiaop1/Verilog-Practice](https://github.com/xiaop1/Verilog-Practice) | 809 | 0.1 | Verilog | HDLBits website practices & solutions |
| [ucb-bar/chisel-tutorial](https://github.com/ucb-bar/chisel-tutorial) | 757 | 3.8 | Scala | chisel tutorial exercises and answers |
| [TerosTechnology/vscode-terosHDL](https://github.com/TerosTechnology/vscode-terosHDL) | 738 | 164.7 | VHDL | VHDL and Verilog/SV IDE: state machine viewer, linter, documentation, snippets... and more!  |
| [m3y54m/FPGA-ASIC-Roadmap](https://github.com/m3y54m/FPGA-ASIC-Roadmap) | 677 | 0.1 | - | A roadmap for those who want to build a career as an FPGA / ASIC Engineer |
| [openhwgroup/cvw](https://github.com/openhwgroup/cvw) | 606 | 49.3 | SystemVerilog | CORE-V Wally is a configurable RISC-V Processor associated with RISC-V System-on-Chip Design textboo |
| [zssloth/Embedded-Neural-Network](https://github.com/zssloth/Embedded-Neural-Network) | 568 | 0.1 | - |  collection of works aiming at reducing model sizes or the ASIC/FPGA accelerator for machine learnin |
| [abdelazeem201/ASIC-Design-Roadmap](https://github.com/abdelazeem201/ASIC-Design-Roadmap) | 551 | 5.9 | Verilog | The journey of designing an ASIC (application specific integrated circuit) is long and involves a nu |
| [kelu124/awesome-latticeFPGAs](https://github.com/kelu124/awesome-latticeFPGAs) | 360 | 0.1 | - | :book: List of FPGA Lattice boards using open tools |

### 领域：服务器/数据中心（6 个）

| 仓库 | ★Star | 体积MB | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [intel/ai-reference-models](https://github.com/intel/ai-reference-models) | 731 | 650.8 | Python | Intel® AI Reference Models: contains Intel optimizations for running deep learning workloads on Inte |
| [facebook/openbmc](https://github.com/facebook/openbmc) | 684 | 73.5 | C | OpenBMC is an open software framework to build a complete Linux image for a Board Management Control |
| [bespoyasov/solidbook](https://github.com/bespoyasov/solidbook) | 653 | 7.8 | MDX | Book about the SOLID principles and object-oriented software design. |
| [facebookarchive/opencompute](https://github.com/facebookarchive/opencompute) | 628 | 421.2 | TeX | A community of engineers whose mission is to design and enable the delivery of the most efficient se |
| [ruvnet/metaharness](https://github.com/ruvnet/metaharness) | 599 | 26.3 | TypeScript | 🛠️ The meta-harness for AI agents — scaffold your own focused, branded agent harness with its own np |
| [BMClab/BMC](https://github.com/BMClab/BMC) | 465 | 328.8 | Jupyter Notebook | Notes on Scientific Computing for Biomechanics and Motor Control |

<!-- APPENDIX_END -->

</details>

---

### 2026-08-22 基础学科补充清单（90 个精选：计算机科学/数学/电子/半导体）

> 第四批 56 组基础学科检索式（CS×12/数学×12/电子×12/半导体×12/中文×8）新增 1,604 候选 + 经典仓库核录，文档型过滤 + 黑名单剔除 + 人工领域校准；完整数据见 import/github-knowledge-survey-2026-08-22/all_items_v5.json（合并后共 2,482 个）。

### 基础领域：计算机科学（39 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) | 541,927 | - | Markdown | Master programming by recreating your favorite technologies from scratch. |
| [nilbuild/developer-roadmap](https://github.com/nilbuild/developer-roadmap) | 365,104 | - | TypeScript | Interactive roadmaps, guides and other educational content to help developers gr |
| [practical-tutorials/project-based-learning](https://github.com/practical-tutorials/project-based-learning) | 280,286 | - | Python | Curated list of project-based tutorials |
| [ossu/computer-science](https://github.com/ossu/computer-science) | 208,306 | - | HTML | 🎓 Path to a free self-taught education in Computer Science! |
| [prakhar1989/awesome-courses](https://github.com/prakhar1989/awesome-courses) | 70,580 | - | - | :books: List of awesome university courses for learning Computer Science! |
| [k88hudson/git-flight-rules](https://github.com/k88hudson/git-flight-rules) | 42,597 | - | - | Flight rules for git |
| [itcharge/AlgoNote](https://github.com/itcharge/AlgoNote) | 7,788 | - | Python | ⛽️「算法通关手册」：从零开始的「算法与数据结构」学习教程，200 道「算法面试热门题目」，1000+ 道「LeetCode 题目解析」，持续更新中！ |
| [fool2fish/dragon-book-exercise-answers](https://github.com/fool2fish/dragon-book-exercise-answers) | 6,649 | - | HTML | Compilers Principles, Techniques, & Tools (purple dragon book) second edition ex |
| [liuxinyu95/AlgoXY](https://github.com/liuxinyu95/AlgoXY) | 6,326 | - | TeX | Book of Elementary Functional Algorithms and Data structures |
| [cirosantilli/x86-bare-metal-examples](https://github.com/cirosantilli/x86-bare-metal-examples) | 5,339 | - | Assembly | Dozens of minimal operating systems to learn x86 system programming. Tested on U |
| [loiane/javascript-datastructures-algorithms](https://github.com/loiane/javascript-datastructures-algorithms) | 4,870 | - | TypeScript | :books: collection of JavaScript and TypeScript data structures and algorithms f |
| [feiyangqingyun/qtkaifajingyan](https://github.com/feiyangqingyun/qtkaifajingyan) | 4,667 | - | - | 自己总结的这十多年做Qt开发以来的经验，以及Qt相关武林秘籍电子书，会一直持续更新增加，欢迎各位留言增加内容或者提出建议，谢谢！公众号：Qt实战/Qt入门和进阶 |
| [SystemsApproach/book](https://github.com/SystemsApproach/book) | 3,380 | - | Python | Computer Networks: A Systems Approach -- Textbook |
| [pkivolowitz/asm_book](https://github.com/pkivolowitz/asm_book) | 3,312 | - | Assembly | A book teaching assembly language programming on the ARM 64 bit ISA. Along the w |
| [presmihaylov/booknotes](https://github.com/presmihaylov/booknotes) | 3,054 | - | Java | A collection of my book notes on various subjects, mainly computer science |
| [QMHTMY/RustBook](https://github.com/QMHTMY/RustBook) | 2,988 | - | Rust | A book about Rust Data Structures and Algorithms. |
| [mixu/distsysbook](https://github.com/mixu/distsysbook) | 2,675 | - | HTML | The book Distributed systems: for fun and profit |
| [m-ou-se/rust-atomics-and-locks](https://github.com/m-ou-se/rust-atomics-and-locks) | 1,617 | - | Rust | Code examples, data structures, and links from my book, Rust Atomics and Locks. |
| [IUCompilerCourse/Essentials-of-Compilation](https://github.com/IUCompilerCourse/Essentials-of-Compilation) | 1,596 | - | TeX | A book about compiling Racket and Python to x86-64 assembly |
| [wa-lang/ugo-compiler-book](https://github.com/wa-lang/ugo-compiler-book) | 1,536 | - | Go | :books: µGo语言实现(从头开发一个迷你Go语言编译器) |
| [brendandburns/designing-distributed-systems-labs](https://github.com/brendandburns/designing-distributed-systems-labs) | 1,310 | - | JavaScript | Labs for the Designing Distributed Systems book. |
| [davecom/ClassicComputerScienceProblemsInPython](https://github.com/davecom/ClassicComputerScienceProblemsInPython) | 1,121 | - | Python | Source Code for the Book Classic Computer Science Problems in Python |
| [IT-Book-Organization/Computer-Networking_A-Top-Down-Approach](https://github.com/IT-Book-Organization/Computer-Networking_A-Top-Down-Approach) | 1,070 | - | - | '컴퓨터 네트워킹: 하향식 접근(제8판)'을 읽고 공부하며 정리하는 저장소입니다. |
| [boazbk/tcs](https://github.com/boazbk/tcs) | 1,063 | - | TeX | Book in preparation: introduction to theoretical computer science |
| [brendandburns/designing-distributed-systems](https://github.com/brendandburns/designing-distributed-systems) | 1,048 | - | Python | Sample code and configuration files from the Designing Distributed Systems book. |
| [mit-pdos/xv6-riscv-book](https://github.com/mit-pdos/xv6-riscv-book) | 942 | - | TeX | Text describing xv6 on RISC-V |
| [zhouyanasd/or-pandas](https://github.com/zhouyanasd/or-pandas) | 880 | - | Jupyter Notebook | 【运筹OR帷幄 / 数据科学】pandas教程系列电子书 |
| [davidcallanan/os-series](https://github.com/davidcallanan/os-series) | 878 | - | C |  |
| [aimi-cn/AILearners](https://github.com/aimi-cn/AILearners) | 700 | - | Python | 机器学习、深度学习、自然语言处理、计算机视觉、各种算法等AI领域相关技术的路线、教程、干货分享。笔记有：机器学习实战、剑指Offer、cs231n、cs131、 |
| [Lularible/storage-book](https://github.com/Lularible/storage-book) | 555 | - | C | An open-source book on storage technology and file systems. From knot records to |
| [ethanhe42/Modern-Compiler-Implementation-in-C](https://github.com/ethanhe42/Modern-Compiler-Implementation-in-C) | 403 | - | C | book and codes for Modern Compiler Implementation in C |
| [jihoonerd/Data_Structures_and_Algorithms_in_Python](https://github.com/jihoonerd/Data_Structures_and_Algorithms_in_Python) | 400 | - | Jupyter Notebook | :book: Worked Solutions of "Data Structures & Algorithms in Python", written by  |
| [vincenzobaz/Computer-Networks-Notes](https://github.com/vincenzobaz/Computer-Networks-Notes) | 398 | - | - | Notes based on the book "Computer Networking, a top down approach" |
| [pdeitel/IntroToPython](https://github.com/pdeitel/IntroToPython) | 384 | - | - | Files associated with our book Intro to Python for Computer Science and Data Sci |
| [simonmar/parconc-examples](https://github.com/simonmar/parconc-examples) | 359 | - | Haskell | Sample code to accompany the book "Parallel and Concurrent Programming in Haskel |
| [keleshev/compiling-to-assembly-from-scratch](https://github.com/keleshev/compiling-to-assembly-from-scratch) | 356 | - | TypeScript | Source code for the book Compiling to Assembly from Scratch https://keleshev.com |
| [geekquad/AlgoBook](https://github.com/geekquad/AlgoBook) | 313 | - | Jupyter Notebook | A beginner-friendly project to help you in open-source contributions. Data Struc |
| [caisah/Sedgewick-algorithms-in-c-exercises-and-examples](https://github.com/caisah/Sedgewick-algorithms-in-c-exercises-and-examples) | 300 | - | C | Examples and exercises from Algorithms in C, Parts 1-4: Fundamentals, Data Struc |
| [nand2tetris/web-ide](https://github.com/nand2tetris/web-ide) | 231 | - | TypeScript | A web-based IDE for https://nand2tetris.org |

### 基础领域：数学（29 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [3b1b/manim](https://github.com/3b1b/manim) | 91,862 | - | Python | Animation engine for explanatory math videos |
| [MathFoundationRL/Book-Mathematical-Foundation-of-Reinforcement-Learning](https://github.com/MathFoundationRL/Book-Mathematical-Foundation-of-Reinforcement-Learning) | 17,522 | - | MATLAB | This is the homepage of a new book entitled "Mathematical Foundations of Reinfor |
| [mml-book/mml-book.github.io](https://github.com/mml-book/mml-book.github.io) | 15,910 | - | Jupyter Notebook | Companion webpage to the book "Mathematics For Machine Learning" |
| [fastai/numerical-linear-algebra](https://github.com/fastai/numerical-linear-algebra) | 10,962 | - | Jupyter Notebook | Free online textbook of Jupyter notebooks for fast.ai Computational Linear Algeb |
| [Visualize-ML/Book4_Power-of-Matrix](https://github.com/Visualize-ML/Book4_Power-of-Matrix) | 10,038 | - | Jupyter Notebook | Book_4_《矩阵力量》 / 鸢尾花书：从加减乘除到机器学习；上架 |
| [ossu/math](https://github.com/ossu/math) | 9,023 | - | - | 🧮  Path to a free self-taught education in Mathematics! |
| [Visualize-ML/Book3_Elements-of-Mathematics](https://github.com/Visualize-ML/Book3_Elements-of-Mathematics) | 7,582 | - | Jupyter Notebook | Book_3_《数学要素》 / 鸢尾花书：从加减乘除到机器学习；上架 |
| [AllenDowney/ThinkStats2](https://github.com/AllenDowney/ThinkStats2) | 4,227 | - | Jupyter Notebook | Text and supporting code for Think Stats, 2nd Edition |
| [Visualize-ML/Book5_Essentials-of-Probability-and-Statistics](https://github.com/Visualize-ML/Book5_Essentials-of-Probability-and-Statistics) | 3,730 | - | Jupyter Notebook | Book_5_《统计至简》 / 鸢尾花书：从加减乘除到机器学习；上架 |
| [pim-book/programmers-introduction-to-mathematics](https://github.com/pim-book/programmers-introduction-to-mathematics) | 3,654 | - | JavaScript | Code for A Programmer's Introduction to Mathematics |
| [mavam/stat-cookbook](https://github.com/mavam/stat-cookbook) | 2,306 | - | TeX | :orange_book: The probability and statistics cookbook |
| [little-book-of/linear-algebra](https://github.com/little-book-of/linear-algebra) | 1,995 | - | Jupyter Notebook | A concise, beginner-friendly introduction to the core ideas of linear algebra. |
| [AllenDowney/ThinkBayes](https://github.com/AllenDowney/ThinkBayes) | 1,702 | - | TeX | Code repository for Think Bayes. |
| [ilmoi/MML-Book](https://github.com/ilmoi/MML-Book) | 1,259 | - | Jupyter Notebook | Code / solutions for Mathematics for Machine Learning (MML Book) |
| [tuangauss/DataScienceProjects](https://github.com/tuangauss/DataScienceProjects) | 835 | - | Jupyter Notebook | The code repository for projects and tutorials in R and Python that covers a var |
| [malhotra5/Manim-Tutorial](https://github.com/malhotra5/Manim-Tutorial) | 819 | - | Python | A tutorial for manim, a mathematical animation engine made by 3b1b |
| [unpingco/Python-for-Probability-Statistics-and-Machine-Learning](https://github.com/unpingco/Python-for-Probability-Statistics-and-Machine-Learning) | 810 | - | Jupyter Notebook | Jupyter Notebooks for Springer book "Python for Probability, Statistics, and Mac |
| [leanprover-community/mathematics_in_lean](https://github.com/leanprover-community/mathematics_in_lean) | 580 | - | HTML | The user home repository for the Mathematics in Lean tutorial. |
| [jvanverth/essentialmath](https://github.com/jvanverth/essentialmath) | 441 | - | C | Example code and libraries for the book "Essential Mathematics for Games and Int |
| [mikexcohen/LinAlg4DataScience](https://github.com/mikexcohen/LinAlg4DataScience) | 440 | - | Jupyter Notebook | Code that accompanies the book "Linear Algebra for Data Science" |
| [HeinrichHartmann/Statistics-for-Engineers](https://github.com/HeinrichHartmann/Statistics-for-Engineers) | 429 | - | Jupyter Notebook | Statistics Tutorial for IT Operations Engineers |
| [cosmic-cortex/mathematics-of-machine-learning-book](https://github.com/cosmic-cortex/mathematics-of-machine-learning-book) | 415 | - | Jupyter Notebook | The official GitHub repository for the Mathematics of Machine Learning book! |
| [unpingco/Python-for-Probability-Statistics-and-Machine-Learning-2E](https://github.com/unpingco/Python-for-Probability-Statistics-and-Machine-Learning-2E) | 378 | - | Jupyter Notebook | Second edition of Springer Book Python for Probability, Statistics, and Machine  |
| [clam004/intro_continual_learning](https://github.com/clam004/intro_continual_learning) | 363 | - | Jupyter Notebook | This is a tutorial to connect the fundamental mathematics to a practical impleme |
| [AllenDowney/BayesMadeSimple](https://github.com/AllenDowney/BayesMadeSimple) | 360 | - | Jupyter Notebook | Code for a tutorial on Bayesian Statistics by Allen Downey. |
| [niuers/Linear-Algebra-and-Learning-from-Data](https://github.com/niuers/Linear-Algebra-and-Learning-from-Data) | 329 | - | Jupyter Notebook | Solutions to the problems in the book: Linear Algebra and Learning from Data by  |
| [bob-carpenter/prob-stats](https://github.com/bob-carpenter/prob-stats) | 324 | - | TeX | Probability and Statistics: a simulation-based introduction.  An open-access boo |
| [vbartle/MML-Companion](https://github.com/vbartle/MML-Companion) | 312 | - | Jupyter Notebook | This is a companion to the 'Mathematical Foundations' section of the book, Mathe |
| [nadvornix/calculus-made-easy](https://github.com/nadvornix/calculus-made-easy) | 307 | - | HTML | HTML conversion of a great beginner calculus book |

### 基础领域：半导体/芯片（16 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [logisim-evolution/logisim-evolution](https://github.com/logisim-evolution/logisim-evolution) | 7,463 | - | Java | Digital logic design tool and simulator |
| [hneemann/Digital](https://github.com/hneemann/Digital) | 5,930 | - | Java | A digital logic designer and circuit simulator. |
| [YosysHQ/yosys](https://github.com/YosysHQ/yosys) | 4,696 | - | C++ | Yosys Open SYnthesis Suite |
| [google/skywater-pdk](https://github.com/google/skywater-pdk) | 3,661 | - | Python | Open source process design kit for usage with SkyWater Technology Foundry's 130n |
| [The-OpenROAD-Project/OpenROAD](https://github.com/The-OpenROAD-Project/OpenROAD) | 3,000 | - | Verilog | OpenROAD's unified application implementing an RTL-to-GDS Flow. Documentation at |
| [olofk/fusesoc](https://github.com/olofk/fusesoc) | 1,452 | - | Python | Package manager and build abstraction tool for FPGA/ASIC development |
| [siliconcompiler/siliconcompiler](https://github.com/siliconcompiler/siliconcompiler) | 1,200 | - | Python | Modular hardware build system |
| [KastnerRG/pp4fpgas](https://github.com/KastnerRG/pp4fpgas) | 906 | - | TeX | Parallel Programming for FPGAs -- An open-source high-level synthesis book |
| [chipsalliance/firrtl](https://github.com/chipsalliance/firrtl) | 747 | - | Scala | Flexible Intermediate Representation for RTL |
| [cnrv/riscv-soc-book](https://github.com/cnrv/riscv-soc-book) | 566 | - | - | 关于RISC-V你所需要知道的一切 |
| [zhangyachen/ComputerArchitectureAndCppBooks](https://github.com/zhangyachen/ComputerArchitectureAndCppBooks) | 539 | - | - | 📚 计算机体系结构与C++书籍收集(持续更新) |
| [OSCC-Project/iEDA](https://github.com/OSCC-Project/iEDA) | 539 | - | C++ | An open-source EDA infrastructure and tools from netlist to GDS |
| [laforest/FPGADesignElements](https://github.com/laforest/FPGADesignElements) | 469 | - | HTML | A self-contained online book containing a library of FPGA design modules and rel |
| [d0iasm/rvemu-for-book](https://github.com/d0iasm/rvemu-for-book) | 421 | - | Rust | Reference implementation for the book "Writing a RISC-V Emulator in Rust". |
| [efabless/caravel](https://github.com/efabless/caravel) | 406 | - | Verilog | Caravel is a standard SoC template with on chip resources to control and read/wr |
| [ucb-bar/hammer](https://github.com/ucb-bar/hammer) | 324 | - | Python | Hammer: Highly Agile Masks Made Effortlessly from RTL |

### 基础领域：电子（6 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [AllenDowney/ThinkDSP](https://github.com/AllenDowney/ThinkDSP) | 4,611 | - | Jupyter Notebook | Think DSP: Digital Signal Processing in Python, by Allen B. Downey. |
| [unpingco/Python-for-Signal-Processing](https://github.com/unpingco/Python-for-Signal-Processing) | 1,745 | - | Jupyter Notebook | Notebooks for "Python for Signal Processing" book |
| [CircuitVerse/CircuitVerse](https://github.com/CircuitVerse/CircuitVerse) | 1,246 | - | JavaScript | CircuitVerse Primary Code Base |
| [spatialaudio/digital-signal-processing-lecture](https://github.com/spatialaudio/digital-signal-processing-lecture) | 875 | - | Jupyter Notebook | Digital Signal Processing - Theory and Computational Examples |
| [manjunath5496/Embedded-Systems-Books](https://github.com/manjunath5496/Embedded-Systems-Books) | 516 | - | - | "I am not the only person who uses his computer mainly for the purpose of diddli |
| [emilbjornson/massivemimobook](https://github.com/emilbjornson/massivemimobook) | 396 | - | MATLAB | Book PDF and simulation code for the monograph "Massive MIMO Networks: Spectral, |

### 2026-08-22 高校公开课补充清单（84 个精选：国内外名校课程）

> 第五批 26 组课程检索式（MIT/Stanford/Berkeley/CMU/Harvard/ETH + 国内高校 + 课程聚合）新增 891 候选 + 经典课程仓库核录（raw 验证），课程关键词过滤 + 黑名单剔除 + 人工领域校准；完整数据见 import/github-knowledge-survey-2026-08-22/all_items_v5.json（合并后共 2,482 个）。

### 课程：国内高校课程资料（18 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [QSCTech/zju-icicles](https://github.com/QSCTech/zju-icicles) | 40,881 | - | HTML | 浙江大学课程攻略共享计划 |
| [PKUanonym/REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT) | 37,441 | - | HTML | 清华大学计算机系课程攻略 Guidance for courses in Department of Computer Science an |
| [lib-pku/libpku](https://github.com/lib-pku/libpku) | 33,879 | - | TeX | 贵校课程资料民间整理 |
| [USTC-Resource/USTC-Course](https://github.com/USTC-Resource/USTC-Course) | 16,238 | - | C++ | :heart:中国科学技术大学课程资源 |
| [kxxwz/SJTU-Courses](https://github.com/kxxwz/SJTU-Courses) | 9,593 | - | - | 上海交通大学课程资料分享 |
| [ddy-ddy/cs-408](https://github.com/ddy-ddy/cs-408) | 6,155 | - | - | 计算机考研专业课程408相关的复习经验，资源和OneNote笔记 |
| [npubird/KnowledgeGraphCourse](https://github.com/npubird/KnowledgeGraphCourse) | 4,461 | - | - | 东南大学《知识图谱》研究生课程 |
| [Xovee/uestc-course](https://github.com/Xovee/uestc-course) | 3,966 | - | HTML | 🎓电子科技大学 📔课程资料 |
| [Salensoft/thu-cst-cracker](https://github.com/Salensoft/thu-cst-cracker) | 3,038 | - | C++ | 清华大学计算机系课程攻略 |
| [tongtzeho/PKUCourse](https://github.com/tongtzeho/PKUCourse) | 2,551 | - | C++ | 北大计算机课程大作业 |
| [ysyisyourbrother/SYSU_Notebook](https://github.com/ysyisyourbrother/SYSU_Notebook) | 2,542 | - | Python | 本项目分享了中山大学计算机学院本科和研究生阶段的课程资料、笔记、期末考试卷和其他实用的相关资源。希望对同学们的学习有所帮助❤️，如果喜欢记得 |
| [kiukotsu/ucore](https://github.com/kiukotsu/ucore) | 2,252 | - | C | 清华大学操作系统课程实验 (OS Kernel Labs) |
| [TheBloodthirster/BUAA_Course_Sharing](https://github.com/TheBloodthirster/BUAA_Course_Sharing) | 2,185 | - | Wolfram Language | 北京航空航天大学(北航)课程作业资料共享计划 |
| [fengdu78/WZU-machine-learning-course](https://github.com/fengdu78/WZU-machine-learning-course) | 2,081 | - | Jupyter Notebook | 温州大学《机器学习》课程资料（代码、课件等） |
| [Trinkle23897/THU-CST-Cracker](https://github.com/Trinkle23897/THU-CST-Cracker) | 1,055 | - | - | 清华大学计算机系课程攻略 Guidance for courses in Department of Computer Science an |
| [Wsky51/THU-CS912-kaoyan](https://github.com/Wsky51/THU-CS912-kaoyan) | 664 | - | - | 清华大学计算机类912考研的历年真题，清华本科生试卷以及清华相关课程ppt |
| [pku-minic/online-doc](https://github.com/pku-minic/online-doc) | 507 | - | Python | PKU compiler course online documentation. |
| [megvii-research/megvii-pku-dl-course](https://github.com/megvii-research/megvii-pku-dl-course) | 454 | - | Python | Homepage for the joint course of Megvii Inc. and Peking University on  |

### 课程：国外名校公开课（48 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [DeathKing/Learning-SICP](https://github.com/DeathKing/Learning-SICP) | 11,267 | - | Ruby | MIT视频公开课《计算机程序的构造和解释》中文化项目及课程学习资料搜集。 |
| [cs231n/cs231n.github.io](https://github.com/cs231n/cs231n.github.io) | 11,003 | - | Jupyter Notebook | Public facing notes page |
| [maxim5/cs229-2018-autumn](https://github.com/maxim5/cs229-2018-autumn) | 3,471 | - | Jupyter Notebook | All notes and materials for the CS229: Machine Learning course by Stan |
| [cycleuser/Stanford-CS-229](https://github.com/cycleuser/Stanford-CS-229) | 3,455 | - | MATLAB | A Chinese Translation of Stanford CS229 notes 斯坦福机器学习CS229课程讲义的中文翻译 |
| [chaozh/MIT-6.824](https://github.com/chaozh/MIT-6.824) | 3,260 | - | Go | Basic Sources for MIT 6.824 Distributed Systems Class |
| [feixiao/Distributed-Systems](https://github.com/feixiao/Distributed-Systems) | 2,757 | - | Go | MIT课程《Distributed Systems 》学习和翻译 |
| [cs50/libcs50](https://github.com/cs50/libcs50) | 2,160 | - | C | This is CS50's Library for C. |
| [forthespada/Awsome-Courses](https://github.com/forthespada/Awsome-Courses) | 1,848 | - | - | 😏国内外计算机的优秀课程，包含MIT、CMU等世界CS名校，🔥🔥其中包含计算机基础学科（操作系统、计算机网络、编译器、数据库、数据结构与算法 |
| [stanfordnlp/cs224n-winter17-notes](https://github.com/stanfordnlp/cs224n-winter17-notes) | 1,605 | - | TeX | Course notes for CS224N Winter17 |
| [OneSizeFitsQuorum/MIT6.824-2021](https://github.com/OneSizeFitsQuorum/MIT6.824-2021) | 1,600 | - | Shell | 4 labs + 2 challenges + 4 docs |
| [mbadry1/CS231n-2017-Summary](https://github.com/mbadry1/CS231n-2017-Summary) | 1,586 | - | Python | After watching all the videos of the famous Standford's CS231n course  |
| [lightaime/cs231n](https://github.com/lightaime/cs231n) | 1,405 | - | Jupyter Notebook | cs231n assignments sovled by https://ghli.org |
| [sampsyo/cs6120](https://github.com/sampsyo/cs6120) | 990 | - | HTML | advanced compilers |
| [tjumcw/6.824](https://github.com/tjumcw/6.824) | 875 | - | C++ | MIT 6.824 distributed system C++Version |
| [cs50/python-cs50](https://github.com/cs50/python-cs50) | 857 | - | Python | This is CS50's library for Python. |
| [percyliang/cs229t](https://github.com/percyliang/cs229t) | 723 | - | TeX | Statistical Learning Theory (CS229T) Lecture Notes |
| [visionNoob/CS231N_17_KOR_SUB](https://github.com/visionNoob/CS231N_17_KOR_SUB) | 699 | - | - | CS231N 2017 video subtitles translation project for Korean Computer Sc |
| [zhanlaoban/CS224N-Stanford-Winter-2019](https://github.com/zhanlaoban/CS224N-Stanford-Winter-2019) | 688 | - | - | The collection of ALL relevant materials about CS224N-Stanford/Winter  |
| [hankcs/CS224n](https://github.com/hankcs/CS224n) | 688 | - | Python | CS224n: Natural Language Processing with Deep Learning Assignments Win |
| [learning511/cs224n-learning-camp](https://github.com/learning511/cs224n-learning-camp) | 675 | - | Python |  |
| [Halfish/cs231n](https://github.com/Halfish/cs231n) | 667 | - | Jupyter Notebook | 斯坦福 cs231n 作业代码实践 |
| [ivanallen/thor](https://github.com/ivanallen/thor) | 653 | - | - | 雷神项目，翻译 mit 6.824 2020 |
| [bos/stanford-cs240h](https://github.com/bos/stanford-cs240h) | 650 | - | Haskell | Course materials for Stanford CS240h, "Functional Systems in Haskell" |
| [Burton2000/CS231n-2017](https://github.com/Burton2000/CS231n-2017) | 605 | - | Jupyter Notebook | Completed the CS231n 2017 spring assignments from Stanford university |
| [cthorey/CS231](https://github.com/cthorey/CS231) | 595 | - | Jupyter Notebook | My corrections for the Standford class assingments CS231n -  Convoluti |
| [csfive/CS50x](https://github.com/csfive/CS50x) | 592 | - | HTML | 🦍 Harvard CS50x Solutions |
| [whyscience/CS231n-Note-Translation_CN](https://github.com/whyscience/CS231n-Note-Translation_CN) | 557 | - | - | CS231课程笔记翻译 https://zhuanlan.zhihu.com/intelligentunit |
| [LooperXX/CS224n-Reading-Notes](https://github.com/LooperXX/CS224n-Reading-Notes) | 549 | - | - | CS224n Reading Notes in Chinese 中文阅读笔记 |
| [ZacBi/CS224n-2019-solutions](https://github.com/ZacBi/CS224n-2019-solutions) | 544 | - | Python | Complete solutions for Stanford CS224n, winter, 2019 |
| [cs50/submit50](https://github.com/cs50/submit50) | 532 | - | Python | This is submit50, CS50's command-line tool for submitting problems. |
| [priya-dwivedi/cs224n-Squad-Project](https://github.com/priya-dwivedi/cs224n-Squad-Project) | 530 | - | Jupyter Notebook |  |
| [mareksuscak/cs50](https://github.com/mareksuscak/cs50) | 516 | - | C | 🎓 Harvard CS50x — 2018 solutions 👨‍🏫 |
| [StanfordVL/CS131_release](https://github.com/StanfordVL/CS131_release) | 502 | - | Jupyter Notebook | Released assignments for the Stanford's CS131 course on Computer Visio |
| [cs231n/gcloud](https://github.com/cs231n/gcloud) | 501 | - | Python | Google Cloud tutorial and setup |
| [xixiaoyao/CS224n-winter-together](https://github.com/xixiaoyao/CS224n-winter-together) | 500 | - | JavaScript | an Open Course Platform for Stanford CS224n (2020 Winter) |
| [jariasf/CS231n](https://github.com/jariasf/CS231n) | 490 | - | Jupyter Notebook | My assignment solutions for CS231n - Convolutional Neural Networks for |
| [mantasu/cs231n](https://github.com/mantasu/cs231n) | 487 | - | Jupyter Notebook | Shortest solutions for CS231n 2021-2026 |
| [dongryul-kim/harvard_notes](https://github.com/dongryul-kim/harvard_notes) | 485 | - | - | Notes for courses taken at Harvard (2015--2019) |
| [isLinXu/Stanford-CS-Course](https://github.com/isLinXu/Stanford-CS-Course) | 468 | - | Python | Stanford-CS-Course |
| [ebatty/MathToolsforNeuroscience](https://github.com/ebatty/MathToolsforNeuroscience) | 466 | - | Jupyter Notebook | Materials for Mathematical Tools for Neuroscience course  at Harvard ( |
| [cs50/check50](https://github.com/cs50/check50) | 461 | - | Python | This is check50, a command-line program with which you can check the c |
| [duliodenis/cs193p-Winter-2017](https://github.com/duliodenis/cs193p-Winter-2017) | 453 | - | Swift | These are the lectures, slides, reading assignments, and problem sets  |
| [huihongxiao/MIT6.824](https://github.com/huihongxiao/MIT6.824) | 442 | - | - |  |
| [yzongyue/6.824-golabs-2020](https://github.com/yzongyue/6.824-golabs-2020) | 429 | - | Go | MIT 6.824 2020 |
| [CS50/lectures](https://github.com/CS50/lectures) | 400 | - | C | CS50 lecture source code |

### 课程：AI/ML 课程（8 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [fengdu78/Coursera-ML-AndrewNg-Notes](https://github.com/fengdu78/Coursera-ML-AndrewNg-Notes) | 37,602 | - | HTML | 吴恩达老师的机器学习课程个人笔记 |
| [datawhalechina/llm-cookbook](https://github.com/datawhalechina/llm-cookbook) | 24,575 | - | Jupyter Notebook | 面向开发者的 LLM 入门教程，吴恩达大模型系列课程中文版 |
| [fengdu78/deeplearning_ai_books](https://github.com/fengdu78/deeplearning_ai_books) | 20,994 | - | HTML | deeplearning.ai（吴恩达老师的深度学习课程笔记及资源） |
| [Fafa-DL/Lhy_Machine_Learning](https://github.com/Fafa-DL/Lhy_Machine_Learning) | 7,104 | - | Jupyter Notebook | 李宏毅2021/2022/2023春季机器学习课程课件及作业 |
| [Hoper-J/AI-Guide-and-Demos-zh_CN](https://github.com/Hoper-J/AI-Guide-and-Demos-zh_CN) | 4,451 | - | Python | 这是一份入门AI/LLM大模型的逐步指南，包含教程和演示代码，带你从API走进本地大模型部署和微调，代码文件会提供Kaggle或Colab在 |
| [zyds/transformers-code](https://github.com/zyds/transformers-code) | 4,051 | - | Jupyter Notebook | 手把手带你实战 Huggingface Transformers 课程视频同步更新在B站与YouTube |
| [Miraclelucy/dive_into_deep_learning](https://github.com/Miraclelucy/dive_into_deep_learning) | 3,073 | - | Python | ✔️李沐 【动手学深度学习】课程学习笔记：使用pycharm编程，基于pytorch框架实现。 |
| [LearnPrompt/LearnPrompt](https://github.com/LearnPrompt/LearnPrompt) | 2,589 | - | MDX | 永久免费开源的 AIGC 课程, 目前已支持Claude Code，Codex，Hermes，OpenClaw，Obsidian，Promp |

### 课程：课程聚合/中文化项目（10 个）

| 仓库 | ★Star | 体积 | 语言 | 说明 |
|:-----|:-----:|:----:|:----:|:-----|
| [kesenhoo/android-training-course-in-chinese](https://github.com/kesenhoo/android-training-course-in-chinese) | 10,601 | - | JavaScript | Android官方培训课程中文版 |
| [flink-china/flink-training-course](https://github.com/flink-china/flink-training-course) | 4,624 | - | - | Flink 中文视频课程（持续更新...） |
| [parallel101/course](https://github.com/parallel101/course) | 4,213 | - | C++ | 高性能并行编程与优化 - 课件 |
| [marmotedu/iam](https://github.com/marmotedu/iam) | 4,205 | - | Go | 企业级的 Go 语言实战项目：认证和授权系统（带配套课程） |
| [ZachL1/Bilibili-plus](https://github.com/ZachL1/Bilibili-plus) | 4,180 | - | C++ | 课程视频、PPT和源代码：侯捷C++系列；台大郭彦甫MATLAB |
| [liuyubobobo/Play-with-Algorithms](https://github.com/liuyubobobo/Play-with-Algorithms) | 3,715 | - | Java | Codes of my MOOC Course <Play with Algorithms>, Both in C++ and Java l |
| [conanhujinming/comments-for-awesome-courses](https://github.com/conanhujinming/comments-for-awesome-courses) | 3,228 | - | Python | 名校公开课程评价网 |
| [EugeneLiu/translationCSAPP](https://github.com/EugeneLiu/translationCSAPP) | 2,801 | - | Python | 为 CSAPP 视频课程提供字幕，翻译 PPT，Lab。 |
| [datawhalechina/whale-quant](https://github.com/datawhalechina/whale-quant) | 2,732 | - | Jupyter Notebook | 本项目为量化开源课程，可以帮助人们快速掌握量化金融知识以及使用Python进行量化开发的能力。 |
| [Octoday-Hub/Embodied-AI](https://github.com/Octoday-Hub/Embodied-AI) | 2,268 | - | - | 「Octoday Hub 星期八具身智能生态社区」聚合论文、项目、课程、工具、数据集、招聘等资源，连接全球开发者、研究者与产业伙伴。 |

</details>

### 2026-08-22 哲学/系统论/方法论补充清单（28 个精选）

> 第六批 42 组检索式（哲学×10/系统论×10/方法论×10/中文×6/聚合×6）+ 经典仓库 core API 核录，严格领域关键词过滤 + 黑名单清理 + 人工精选（剔除 AI Skill 应用类噪音）；完整数据见 import/github-knowledge-survey-2026-08-22/all_items_v6.json（合并后共 3,690 个）。

### 方法/哲学：方法论/思维模型（18 个）

| 仓库 | ★Star | 语言 | 说明 |
|:-----|:-----:|:----:|:-----|
| [jlevy/the-art-of-command-line](https://github.com/jlevy/the-art-of-command-line) | 162,146 | - | Master the command line, in one page |
| [kdeldycke/awesome-falsehood](https://github.com/kdeldycke/awesome-falsehood) | 27,635 | - | 😱 Falsehoods Programmers Believe in |
| [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire) | 15,747 | Python | AI 时代的伯克希尔：基于 Claude Code / Codex 的价值投资研究框架。巴菲特·芒格·段永平·李录四大师方法论 + 多Agent并行研 |
| [rShetty/awesome-podcasts](https://github.com/rShetty/awesome-podcasts) | 13,076 | - | Collection of awesome podcasts |
| [danluu/post-mortems](https://github.com/danluu/post-mortems) | 12,262 | - | A collection of postmortems. Sorry for the delay in merging PRs! |
| [easychen/one-person-businesses-methodology](https://github.com/easychen/one-person-businesses-methodology) | 8,361 | - | 一人公司方法论 |
| [hwayne/awesome-cold-showers](https://github.com/hwayne/awesome-cold-showers) | 7,344 | - | For when people get too hyped up about things |
| [hemansnation/AI-Engineer-Headquarters](https://github.com/hemansnation/AI-Engineer-Headquarters) | 3,672 | Jupyter Notebook | A collection of scientific methods, processes, algorithms, and systems to b |
| [AllenDowney/ThinkPython2](https://github.com/AllenDowney/ThinkPython2) | 2,644 | TeX | LaTeX source and supporting code for Think Python, 2nd edition, by Allen Do |
| [AllenDowney/ThinkBayes2](https://github.com/AllenDowney/ThinkBayes2) | 2,073 | Jupyter Notebook | Text and code for the second edition of Think Bayes, by Allen Downey. |
| [wgpsec/AboutSecurity](https://github.com/wgpsec/AboutSecurity) | 1,691 | Python | Everything for pentest. / 渗透测试知识库，以 AI Agent 可执行的格式沉淀安全方法论。 |
| [tjboudreaux/cc-thinking-skills](https://github.com/tjboudreaux/cc-thinking-skills) | 974 | JavaScript | 28 eval-informed mental models and critical-thinking skills for Claude Code |
| [AllenDowney/ModSimPy](https://github.com/AllenDowney/ModSimPy) | 937 | Jupyter Notebook | Text and supporting code for Modeling and Simulation in Python |
| [brettkromkamp/awesome-knowledge-management](https://github.com/brettkromkamp/awesome-knowledge-management) | 866 | - | A curated list of amazingly awesome articles, people, applications, softwar |
| [gwern/gwern.net](https://github.com/gwern/gwern.net) | 837 | JavaScript | Site infrastructure for gwern.net. Custom Hakyll website with unique link a |
| [lukasz-madon/awesome-concepts](https://github.com/lukasz-madon/awesome-concepts) | 628 | - |  Awesome list about all kinds of interesting topics: Laws, Principles, Ment |
| [simonhoo/pm](https://github.com/simonhoo/pm) | 227 | - | 项目管理经验，项目管理过程工具，各种方法论，文档模板，个人总结，PMP资料。 |
| [datawhalechina/reasoning-kingdom](https://github.com/datawhalechina/reasoning-kingdom) | 205 | - | 🌟 推理王国：关于 AI 推理机制的思想实验手册。从信息论、符号逻辑与表示学习出发，系统剖析大模型“智能”的本质。 |

### 方法/哲学：系统论/复杂性/控制论（6 个）

| 仓库 | ★Star | 语言 | 说明 |
|:-----|:-----:|:----:|:-----|
| [ncase/loopy](https://github.com/ncase/loopy) | 1,743 | JavaScript | A tool for thinking in systems |
| [espadrine/succinct-cybernetics](https://github.com/espadrine/succinct-cybernetics) | 1,593 | JavaScript | Computer Science Cheatsheets. |
| [spatialaudio/signals-and-systems-lecture](https://github.com/spatialaudio/signals-and-systems-lecture) | 382 | Jupyter Notebook | Continuous- and Discrete-Time Signals and Systems - Theory and Computationa |
| [sellisd/awesome-complexity](https://github.com/sellisd/awesome-complexity) | 295 | - | An awesome list of complex systems science resources |
| [navy2609/cybernetics](https://github.com/navy2609/cybernetics) | 293 | - | 控制论相关资料 |
| [AllenDowney/ThinkComplexity](https://github.com/AllenDowney/ThinkComplexity) | 118 | Jupyter Notebook | Code for Allen Downey's book Think Complexity, published by O'Reilly Media. |

### 方法/哲学：哲学/逻辑（4 个）

| 仓库 | ★Star | 语言 | 说明 |
|:-----|:-----:|:----:|:-----|
| [johnousterhout/aposd-vs-clean-code](https://github.com/johnousterhout/aposd-vs-clean-code) | 1,817 | - | A discussion between John Ousterhout and Robert Martin about differences be |
| [neural-maze/philoagents-course](https://github.com/neural-maze/philoagents-course) | 1,536 | Python | When Philosophy meets AI |
| [HussainAther/awesome-philosophy](https://github.com/HussainAther/awesome-philosophy) | 270 | - | A curated list of awesome philosophy |
| [manjunath5496/Philosophy-Books](https://github.com/manjunath5496/Philosophy-Books) | 13 | - | "One cannot conceive anything so strange and so implausible that it has not |

---

## 参考资料

[1] GitHub Search API（api.github.com/search/repositories），2026-08-18 实测直连 200 [来源: 本调研]

[2] git-submodule-import 技能，skills/git-submodule-import/SKILL.md [来源: 本系统]

[3] 知识库的本质与全生命周期知识管理架构，2026-08-18，knowledge/03_AI/knowledge-system/2026-08-18-kb-essence-and-full-km-architecture.md [来源: 本系统]

[4] 知识管理的价值链失衡，2026-08-05，knowledge/07_industry-research/18_methodology-framework/2026-08-05-knowledge-management-value-chain-deep-analysis.md [来源: 本系统]

[5] ebook-treasure-chest 元信息，import/ebook-treasure-chest.info/README.md [来源: 本系统]

[6] GitHub Search API 批 4 补充检索（52 组），2026-08-22 实测直连 200；完整数据 import/github-knowledge-survey-2026-08-22/all_items.json [来源: 本调研]

[7] GitHub Search API 批 5 领域定向检索（55 组：芯片/服务器/硬件/AI/产品研发），2026-08-22 实测直连 200；合并数据 import/github-knowledge-survey-2026-08-22/all_items_v3.json（1,872 个） [来源: 本调研]

[8] GitHub Search API 批 6 基础学科检索（56 组：CS/数学/电子/半导体）+ 经典仓库核录，2026-08-22 实测直连 200（部分查询因网络中断补跑）；合并数据 import/github-knowledge-survey-2026-08-22/all_items_v5.json（2,482 个） [来源: 本调研]

[9] GitHub Search API 批 7 高校课程检索（26 组：MIT/Stanford/Berkeley/CMU/Harvard/ETH/国内高校）+ 经典课程仓库 raw 验证，2026-08-22 实测直连 200（部分查询因网络中断补跑）；精选清单见本文 §8 [来源: 本调研]

[10] GitHub Search API 批 8 哲学/系统论/方法论检索（42 组）+ 经典仓库 core API 核录，2026-08-22 实测直连 200（3 组中文查询因数据过大 ERR，以英文关键词替代）；合并数据 import/github-knowledge-survey-2026-08-22/all_items_v6.json（3,690 个） [来源: 本调研]

---

## 素材边界声明

- **数据来源**：GitHub API 八批 277 组检索式（批1-3 为 2026-08-18 快照，批 4-8 为 2026-08-22 快照），合并全库 3,690 → 正文精选 353 + 附录补充 532 + 领域定向 198 + 基础学科 90 + 高校课程 84 + 方法论 28（补充批 star≥800/300/400/200）——**搜索快照时间不同，star 数/体积会随时间变化**；v4/v5 精选清单体积列为「-」（raw 验证获取不到真实 size，避免误导）。
- **分类为启发式**：脚本按名称/描述关键词自动分类 + 人工校准，边界仓库（如同时属"awesome"与"领域知识库"）可能归类偏差；v2.0 补充批自动分类 20 类过细，v3.0 领域定向已改单词边界匹配 + 文档型过滤（大幅降低子串误报），v4-v6 已人工领域校准（v6 尤其剔除大量 AI Skill 应用类"方法论"噪音），实际使用按需重排（完整数据在 import/ 素材区）。
- **star 门槛局限**：star≥200/400/800 可能漏掉新发布的优质小仓库；未覆盖 Gitee/其他平台。
- **许可未逐一核验**：文中许可信息（CC BY 4.0 等）来自仓库公开信息，导入前须逐个确认；**国内高校课程资料（清华/北大/浙大/中科大等攻略）部分含版权风险（试卷/教材扫描件），导入前必须筛选**。
- **web_search 因 key 失效不可用**：中文社区视角已通过用户系列检索部分补充（datawhalechina/0voice/wx-chevalier），知乎/B站/GitHub 精选文章交叉验证仍待恢复后补。
- **仓库改名实录**：kamranahmedse/developer-roadmap 已迁移至 nilbuild/developer-roadmap（★365k 不变）；mit-pdos/6.824 已不可访问（课程资料以 chaozh/MIT-6.824 等替代收录）。
- **v6 中文查询限制**：3 组中文检索式（思维模型/系统思维/第一性原理）因返回数据过大触发 IncompleteRead，已用英文关键词（mental models/systems thinking/first principles）替代覆盖——中文社区方法论资源可能仍有遗漏。

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-22 | v6.0 | 批 8 哲学/系统论/方法论 42 组检索式（哲学×10/系统论×10/方法论×10/中文×6/聚合×6），新增 1,189 候选 + 经典仓库 core 核录 → 严格过滤+人工精选 28 个（方法论 18/系统论 6/哲学 4），合并全库 3,690；新增 §9 元方法论章节；附录追加清单；发现「方法论」关键词被 AI Skill 生态污染 |
| 2026-08-22 | v5.0 | 批 7 高校课程 26 组检索式（MIT/Stanford/Berkeley/CMU/Harvard/ETH + 国内高校 + 课程聚合），新增 891 候选 → 精选 84 个（国外 48/国内 18/AI 8/聚合 10），合并全库 2,482；新增 §8 高校公开课章节；附录追加课程清单；识别国内课程攻略版权风险 |
| 2026-08-22 | v4.0 | 批 6 基础学科 56 组检索式（CS/数学/电子/半导体四轴），新增 1,604 候选 → 精选 90 个（CS 39/数学 29/半导体 16/电子 6），合并全库 2,482；新增 §7 基础学科章节；附录追加基础学科清单；识别电子领域开源知识生态短板 |
| 2026-08-22 | v3.0 | 批 5 领域定向 55 组检索式（芯片/服务器/硬件/AI/产品研发五轴），新增 1,150 候选→文档型过滤精选 198 个，合并全库 1,872；新增 §6 领域定向章节；附录追加领域清单；导入建议映射组织能力补齐主线 |
| 2026-08-22 | v2.0 | 批 4 补充 52 组检索式（awesome/cheatsheet/文档手册/领域知识库/中文资源/资源聚合六轴），合并去重 722 个（新增 609），附录追加补充精选 532 个；新增 §5 补充调研章节；导入优先级更新；素材落盘 import/github-knowledge-survey-2026-08-22/ |
| 2026-08-18 | v1.0 | 首次创建：GitHub API 三批 46 组检索 + 353 个精选仓库 MECE 分类 + 10 组专题问答 + 导入优先级建议 + 完整清单附录 |
