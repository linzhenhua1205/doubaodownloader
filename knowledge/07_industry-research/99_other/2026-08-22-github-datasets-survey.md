# GitHub 公开数据集仓库全景调研：544 仓库 × 11 领域 × 全参数

> **类型**: 专题调研（开源数据集资源全景盘点 + 仓库参数完整采集） | **日期**: 2026-08-22 | **版本**: v1.0
> **来源**: GitHub Search API 49 组检索式（11 领域轴，2026-08-22 实测）+ core API 经典核录 40 仓库（成功 26）+ 数据后处理（噪声标注/领域分类/阈值精选）
> **适用范围**: 数据集选型 / 训练数据调研 / 数据工程参考 / 知识库素材 / AI 能力评估
> **相关**: [GitHub 知识类仓库全景调研](2026-08-18-github-knowledge-repos-survey-qa.md)（知识形态轴，本文为数据资源轴） · [知识库本质篇](../../03_AI/knowledge-system/2026-08-18-kb-essence-and-full-km-architecture.md) · [RULE.md 素材批判使用](../../../RULE.md)

---

## 📑 目录 (TOC)

- [§0 执行摘要](#§0-执行摘要)
- [§1 调研方法与规模](#§1-调研方法与规模)
- [§2 数据集参数体系说明](#§2-数据集参数体系说明)
- [§3 分领域结果总览](#§3-分领域结果总览)
- [§4 领域精选清单（Top 15/领域）](#§4-领域精选清单top-15领域)
- [§5 关键发现与洞察](#§5-关键发现与洞察)
- [§6 使用建议与合规注意事项](#§6-使用建议与合规注意事项)
- [§7 数据缺口与后续动作](#§7-数据缺口与后续动作)
- [附录 A：完整仓库清单（544 个全参数）](#附录-a完整仓库清单544-个全参数)
- [附录 B：原始数据文件](#附录-b原始数据文件)
- [参考资料](#参考资料)
- [素材边界声明](#素材边界声明)
- [Changelog](#changelog)

---

## §0 执行摘要

**GitHub 上公开数据集仓库已形成完整生态：本次调研以 49 组检索式覆盖 11 大领域（LLM 语料/NLP/CV/音频/科学/医疗/时序/图/Web/代码/通用聚合），合并去重后获 544 个仓库（数据集 381 + 数据工具生态 163），采集每个仓库的 16 项参数（星标/分叉/语言/许可/规模/创建/更新/推送/主题/链接等），总星标 168.7 万** [来源: GitHub API 2026-08-22 实测]。

**三个核心发现**：

1. **LLM 训练语料已成为数据集生态的第一大领域（107 个，占数据集 28%）**——从预训练语料（RedPajama/dolma/the-pile/MNBVC）到指令微调（stanford_alpaca/self-instruct/AlpacaDataCleaned）再到 RLHF 对齐与评测基准，全链路数据集在 GitHub 上均有开源仓库；**中文语料是独立且活跃的分支**（funNLP 82.6k 星/nlp_chinese_corpus/CLUE/MNBVC），与国产模型生态直接对应 [来源: 本调研实测]。

2. **GitHub 仓库 ≠ 数据集本身，仓库只是"入口"**——多数大型数据集（c4/falcon-refinedweb/roots/SlimPajama/cosmopedia 等）实际以 **Hugging Face Hub 为载体**，GitHub 仓库只承载代码/文档/下载脚本（如 allenai/dolma 64MB 代码仓对应 3T tokens 语料）。**选型时必须区分"载体"（HF Hub vs GitHub vs 官网）与"入口"（GitHub 仓库）**，本文 40 仓库核录中 13 个 MISS 均为此类 [来源: 本调研实测]。

3. **数据工具生态与数据集生态规模相当（163 个）**——标注（Label Studio 28.1k/doccano 10.8k/CVAT 16.6k）、采集（EasySpider 44.4k/TikTokDownloader 15.5k）、合成（Faker 19.4k/img2dataset/easy-dataset）、编排（DataX 17.3k/DataX 等）四类工具构成了数据集的上游产业链；**"造数据"的能力正在成为比"找数据"更稀缺的能力** [来源: 本调研实测]。

一句话结论：**GitHub 数据集生态已从"散点资源"走向"分领域全链路"**——按"领域轴 × 数据生命周期（采集→清洗→标注→合成→发布→基准）"可系统检索，本调研文档即此坐标系的全量索引。

---

## §1 调研方法与规模

### 1.1 检索设计（11 领域 × 49 组）

| 领域轴 | 检索式数 | 覆盖内容 |
|:-------|:--------:|:---------|
| general 通用聚合 | 5 | awesome dataset / dataset collection / open datasets / public dataset / topic:dataset |
| llm LLM 语料 | 6 | LLM dataset / instruction tuning / fine-tuning / pretraining / RLHF / alignment |
| nlp 文本 | 6 | NLP dataset / text / language model / QA / dialogue / sentiment |
| cv 视觉 | 6 | vision / image / object detection / multimodal / video / OCR |
| audio 音频 | 4 | audio / speech / ASR / music |
| science 科学 | 5 | scientific / math / physics / chemistry / protein |
| timeseries 时序 | 3 | time series / financial / stock market |
| graph 图 | 3 | graph / knowledge graph / recommendation |
| medical 医疗 | 3 | medical / healthcare / biomedical |
| vertical 垂直 | 5 | benchmark / ML / DL / network traffic / security |
| chinese 中文 | 3 | 中文数据集 / chinese nlp / 数据集 |

[来源: 本调研检索式设计]

### 1.2 数据采集与处理流水线

```
GitHub Search API (49 queries, sort=stars, per_page=15)
      -> raw_items.json (532 unique)
      -> noise tagging (name regex: spider/book/api/label/faker ...)
      -> domain refine (description keywords -> _main_cat)
      -> threshold select (per-category stars: 100-400)
      -> selected_items.json (369 datasets + 163 tools)
      -> core API classic verify (40 repos, 26 found)
      -> final_items.json (381 datasets + 163 tools = 544)
```

[来源: 本调研实测]

### 1.3 参数采集字段（16 项/仓库）

| 类别 | 字段 | 含义 |
|:-----|:-----|:-----|
| 身份 | full_name / html_url / default_branch / homepage | 仓库定位与主页 |
| 热度 | stargazers_count / forks_count / open_issues_count | 社区规模（★为主要筛选维度） |
| 技术 | language / topics / size(KB) / archived | 语言/主题/仓库体积/归档状态 |
| 许可 | license(spdx_id) | 开源许可证（⚠️ 数据集许可 ≠ 代码许可，见 §6） |
| 时间 | created_at / updated_at / pushed_at | 创建/更新/最近推送（活跃度信号） |

[来源: GitHub REST API /repos 字段定义]

---

## §2 数据集参数体系说明

**"数据集参数"应分两层理解**（本文均采集/标注）：

### 2.1 仓库参数（GitHub 元数据，16 项全部采集）

上表字段即仓库参数——用于评估：社区认可度（★）、维护活跃度（pushed_at）、技术栈（language/topics）、许可合规（license）、体积量级（size）。

### 2.2 数据集本体参数（须读 README 或访问载体）

| 参数 | 说明 | 本文标注方式 |
|:-----|:-----|:-------------|
| 样本量 | 如 1.3M 指令对 / 3T tokens | description 可提取则标注，否则标注"见载体" |
| 数据格式 | jsonl / parquet / csv / 图像目录 | 同上 |
| 载体 | HF Hub / GitHub LFS / 官网 / 云存储 | 40 仓库核录验证（13 个 MISS=载体非 GitHub） |
| 领域标签 | 数据内容领域 | 本文 _main_cat 分类 |
| 许可 | 数据集许可（CC/ODC 等） | 与仓库 license 字段区分 |

**关键提醒**：**GitHub 仓库的 license 字段通常指代码许可，不覆盖数据集内容许可**——数据集本体许可常在 README 或载体页标注（如 RedPajama 语料使用自己的许可条款）[来源: 本调研推导 + 各仓库 README]。

---

## §3 分领域结果总览

| 领域 | 数据集数 | 占比 | 头部代表（★） | 生态特征 |
|:-----|:--------:|:----:|:--------------|:---------|
| LLM/AI 语料 | 107 | 28% | funNLP 82.6k / stanford_alpaca 30.2k / HF datasets 21.8k | 全链路（预训练→指令→对齐→评测），增速最快 |
| NLP/文本 | 81 | 21% | AiHubCN 22.7k / faker 19.4k / ParlAI 10.6k | 经典任务+中文语料双主线 |
| 计算机视觉 | 70 | 18% | pytorch/vision 17.9k / CVAT 16.6k / fashion-mnist 12.8k | 标注工具与数据集共生，卫星/工业缺陷等垂直场景丰富 |
| 通用聚合 | 43 | 11% | public-apis 468k / awesome-public-datasets 78.4k / label-studio 28.1k | 导航层+数据平台层 |
| 音频/语音 | 24 | 6% | voice_datasets 2.2k / GigaSpeech 730 / MS-SNSD 600 | ASR/语音合成为主，规模普遍小于文本 |
| 图/推荐 | 17 | 4% | ogb 2.1k / RecSysDatasets 1.3k / SketchGraphs 479 | 基准数据集（OGB）与推荐数据源汇聚 |
| 时序/金融 | 13 | 3% | prediction-market 3.8k / TS-anomaly 3.2k / OpenLTM 550 | 异常检测与金融数据双热点 |
| 科学计算 | 11 | 3% | the_well 4.4k / awesome-ai-for-science 1.9k / MATH 1.4k | 物理仿真（15TB）与数学基准（MATH）代表 |
| 医疗健康 | 10 | 3% | Awesome-Medical-Dataset 2.1k / MIMIC-III 890 / MedMNIST 1.4k | 医学图像/临床数据，许可与隐私约束最严 |
| 代码 | 3 | 1% | CodeSearchNet 2.4k | 代码检索/生成基准 |
| Web/网页 | 2 | 1% | browser-compat-data 5.7k | 浏览器兼容性数据 |

[来源: 本调研实测统计]

---

## §4 领域精选清单（Top 15/领域）

### llm.LLM/AI 训练语料（精选 107 个中的 Top 15）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [fighting41love/funNLP](https://github.com/fighting41love/funNLP) | 82593 | Python | - | 170MB | 中英文敏感词、语言检测、中外手机/电话归属地/运营商查询、名字推断性别、手机号抽取、身份证抽取、邮箱抽取、中日文人名库、中文 |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 33540 | TypeScript | NOASSERTION | 210MB | 🪢 Open source AI engineering platform: LLM evals, observabilit |
| [tatsu-lab/stanford_alpaca](https://github.com/tatsu-lab/stanford_alpaca) | 30245 | Python | Apache-2.0 | 8MB | Code and documentation to train Stanford's Alpaca models, and  |
| [huggingface/datasets](https://github.com/huggingface/datasets) | 21846 | Python | Apache-2.0 | 113MB | 🤗 The largest hub of ready-to-use datasets for AI models with  |
| [hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset) | 20568 | HTML | NOASSERTION | 125MB | 1,324-exercise fitness dataset — animation GIFs, 180×180 thumb |
| [allenai/olmocr](https://github.com/allenai/olmocr) | 19369 | Python | Apache-2.0 | 349MB | Toolkit for linearizing PDFs for LLM datasets/training |
| [ConardLi/easy-dataset](https://github.com/ConardLi/easy-dataset) | 14812 | JavaScript | NOASSERTION | 19MB | A powerful tool for creating datasets for LLM fine-tuning 、RAG |
| [dataelement/bisheng](https://github.com/dataelement/bisheng) | 11901 | Python | Apache-2.0 | 203MB | BISHENG is an open LLM devops platform for next generation Ent |
| [brightmart/nlp_chinese_corpus](https://github.com/brightmart/nlp_chinese_corpus) | 9909 | - | MIT | 4MB | 大规模中文自然语言处理语料  Large Scale Chinese Corpus for NLP |
| [open-compass/opencompass](https://github.com/open-compass/opencompass) | 7327 | Python | Apache-2.0 | 7MB | OpenCompass is an LLM evaluation platform, supporting a wide r |
| [lonePatient/awesome-pretrained-chinese-nlp-models](https://github.com/lonePatient/awesome-pretrained-chinese-nlp-models) | 5582 | Python | MIT | 871KB | Awesome Pretrained Chinese NLP Models，高质量中文预训练模型&大模型&多模态模型&大语言 |
| [Kiln-AI/Kiln](https://github.com/Kiln-AI/Kiln) | 5031 | Python | NOASSERTION | 49MB | Build, Evaluate, and Optimize AI Systems. Includes evals, RAG, |
| [mlabonne/llm-datasets](https://github.com/mlabonne/llm-datasets) | 4747 | - | - | 72KB | Curated list of datasets and tools for post-training. |
| [yizhongw/self-instruct](https://github.com/yizhongw/self-instruct) | 4610 | Python | Apache-2.0 | 60MB | Aligning pretrained language models with instruction data gene |
| [CLUEbenchmark/CLUE](https://github.com/CLUEbenchmark/CLUE) | 4279 | Python | - | 3MB | 中文语言理解测评基准 Chinese Language Understanding Evaluation Benchmark |

### nlp.NLP/文本（精选 81 个中的 Top 15）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [AiHubCN/Awesome-Chinese-LLM](https://github.com/AiHubCN/Awesome-Chinese-LLM) | 22747 | - | - | 11MB | 整理开源的中文大语言模型，以规模较小、可私有化部署、训练成本较低的模型为主，包括底座模型，垂直领域微调及应用，数据集与教程等 |
| [Dujltqzv/Some-Many-Books](https://github.com/Dujltqzv/Some-Many-Books) | 22601 | - | - | 2.6GB | 个人收藏书籍列表　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　 |
| [joke2k/faker](https://github.com/joke2k/faker) | 19374 | Python | MIT | 12MB | Faker is a Python package that generates fake data for you. |
| [doccano/doccano](https://github.com/doccano/doccano) | 10753 | Python | MIT | 57MB | Open source annotation tool for machine learning practitioners |
| [facebookresearch/ParlAI](https://github.com/facebookresearch/ParlAI) | 10622 | Python | MIT | 146MB | A framework for training and evaluating AI models on a variety |
| [NirantK/awesome-project-ideas](https://github.com/NirantK/awesome-project-ideas) | 9281 | - | MIT | 113KB | Curated list of Machine Learning, NLP, Vision, Recommender Sys |
| [xiaobaiTech/golangFamily](https://github.com/xiaobaiTech/golangFamily) | 6965 | Go | - | 128KB | 【超全golang面试题合集+golang学习指南+golang知识图谱+入门成长路线】 一份涵盖大部分golang程序员所 |
| [SophonPlus/ChineseNlpCorpus](https://github.com/SophonPlus/ChineseNlpCorpus) | 6593 | Jupyter Notebook | - | 11MB | 搜集、整理、发布 中文 自然语言处理 语料/数据集，与 有志之士 共同 促进 中文 自然语言处理 的 发展。 |
| [niderhoff/nlp-datasets](https://github.com/niderhoff/nlp-datasets) | 5995 | - | - | 195KB | Alphabetical list of free/public domain datasets with text dat |
| [cirosantilli/x86-bare-metal-examples](https://github.com/cirosantilli/x86-bare-metal-examples) | 5339 | Assembly | NOASSERTION | 1MB | Dozens of minimal operating systems to learn x86 system progra |
| [togethercomputer/RedPajama-Data](https://github.com/togethercomputer/RedPajama-Data) | 4979 | Python | Apache-2.0 | 2MB | The RedPajama-Data repository contains code for preparing larg |
| [InsaneLife/ChineseNLPCorpus](https://github.com/InsaneLife/ChineseNLPCorpus) | 4610 | Python | - | 7MB | 中文自然语言处理数据集，平时做做实验的材料。欢迎补充提交合并。 |
| [CLUEbenchmark/CLUEDatasetSearch](https://github.com/CLUEbenchmark/CLUEDatasetSearch) | 4455 | Python | - | 9MB | 搜索所有中文NLP数据集，附常用英文NLP数据集 |
| [NAalytics/Assemblies-of-putative-SARS-CoV2-spike-encoding-mRNA-sequences-for-vaccines-BNT-162b2-and-mRNA-1273](https://github.com/NAalytics/Assemblies-of-putative-SARS-CoV2-spike-encoding-mRNA-sequences-for-vaccines-BNT-162b2-and-mRNA-1273) | 3353 | - | - | 492KB | RNA vaccines have become a key tool in moving forward through  |
| [CVI-SZU/Linly](https://github.com/CVI-SZU/Linly) | 3043 | Python | - | 7MB | Chinese-LLaMA 1&2、Chinese-Falcon 基础模型；ChatFlow中文对话模型；中文OpenLLa |

### cv.计算机视觉/图像（精选 70 个中的 Top 15）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [pytorch/vision](https://github.com/pytorch/vision) | 17873 | Python | BSD-3-Clause | 1.2GB | Datasets, Transforms and Models specific to Computer Vision |
| [cvat-ai/cvat](https://github.com/cvat-ai/cvat) | 16568 | Python | MIT | 371MB | Computer Vision Annotation Tool (CVAT) is a leading platform f |
| [lukas-blecher/LaTeX-OCR](https://github.com/lukas-blecher/LaTeX-OCR) | 16544 | Python | MIT | 9MB | pix2tex: Using a ViT to convert images of equations into LaTeX |
| [zalandoresearch/fashion-mnist](https://github.com/zalandoresearch/fashion-mnist) | 12808 | Python | MIT | 106MB | A MNIST-like fashion product database. Benchmark :point_down:  |
| [satellite-image-deep-learning/techniques](https://github.com/satellite-image-deep-learning/techniques) | 10234 | - | Apache-2.0 | 30MB | Techniques for deep learning with satellite & aerial imagery |
| [rom1504/img2dataset](https://github.com/rom1504/img2dataset) | 4442 | Python | MIT | 4MB | Easily turn large sets of image urls to an image dataset. Can  |
| [openimages/dataset](https://github.com/openimages/dataset) | 4376 | Python | Apache-2.0 | 3MB | The Open Images dataset |
| [Yochengliu/awesome-point-cloud-analysis](https://github.com/Yochengliu/awesome-point-cloud-analysis) | 4218 | - | - | 289KB | A list of papers and datasets about point cloud analysis (proc |
| [Charmve/Surface-Defect-Detection](https://github.com/Charmve/Surface-Defect-Detection) | 4099 | Python | MIT | 229MB | 📈 目前最大的工业缺陷检测数据库及论文集 Constantly summarizing open source datase |
| [M-3LAB/awesome-industrial-anomaly-detection](https://github.com/M-3LAB/awesome-industrial-anomaly-detection) | 3744 | - | - | 6MB | Paper list and datasets for industrial image anomaly/defect de |
| [uzh-rpg/event-based_vision_resources](https://github.com/uzh-rpg/event-based_vision_resources) | 3629 | - | - | 2MB | Event-based Vision Resources. Community effort to collect know |
| [linhandev/dataset](https://github.com/linhandev/dataset) | 3605 | - | - | 16MB | 医学影像数据集列表 『An Index for Medical Imaging Datasets』 |
| [ieee8023/covid-chestxray-dataset](https://github.com/ieee8023/covid-chestxray-dataset) | 3062 | Jupyter Notebook | - | 633MB | We are building an open database of COVID-19 cases with chest  |
| [microsoft/table-transformer](https://github.com/microsoft/table-transformer) | 2938 | Python | MIT | 333KB | Table Transformer (TATR) is a deep learning model for extracti |
| [facebookresearch/audio2photoreal](https://github.com/facebookresearch/audio2photoreal) | 2850 | Python | NOASSERTION | 64MB | Code and dataset for photorealistic Codec Avatars driven from  |

### audio.音频/语音（精选 24 个中的 Top 15）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [RedditSota/state-of-the-art-result-for-machine-learning-problems](https://github.com/RedditSota/state-of-the-art-result-for-machine-learning-problems) | 8894 | - | Apache-2.0 | 151KB | This repository provides state of the art (SoTA) results for a |
| [jim-schwoebel/voice_datasets](https://github.com/jim-schwoebel/voice_datasets) | 2221 | - | - | 139KB | 🔊 A comprehensive list of open-source datasets for voice and s |
| [uber/petastorm](https://github.com/uber/petastorm) | 1891 | Python | Apache-2.0 | 3MB | Petastorm library enables single machine or distributed traini |
| [zwang4/awesome-machine-learning-in-compilers](https://github.com/zwang4/awesome-machine-learning-in-compilers) | 1686 | - | CC0-1.0 | 593KB | Must read research papers and links to tools and datasets that |
| [krantiparida/awesome-audio-visual](https://github.com/krantiparida/awesome-audio-visual) | 777 | - | - | 60KB | A curated list of different papers and datasets in various are |
| [LAION-AI/audio-dataset](https://github.com/LAION-AI/audio-dataset) | 749 | Python | - | 84MB | Audio Dataset for training CLAP and other models |
| [SpeechColab/GigaSpeech](https://github.com/SpeechColab/GigaSpeech) | 730 | Shell | Apache-2.0 | 229KB | Large, modern dataset for speech recognition |
| [tbertinmahieux/MSongsDB](https://github.com/tbertinmahieux/MSongsDB) | 695 | Python | NOASSERTION | 30MB | Code for the Million Song Dataset, the dataset contains metada |
| [microsoft/MS-SNSD](https://github.com/microsoft/MS-SNSD) | 600 | HTML | MIT | 3.9GB | The Microsoft Scalable Noisy Speech Dataset (MS-SNSD) is a noi |
| [facebookresearch/libri-light](https://github.com/facebookresearch/libri-light) | 523 | Python | MIT | 373KB | dataset for lightly supervised training using the librivox aud |
| [Kyubyong/css10](https://github.com/Kyubyong/css10) | 491 | HTML | Apache-2.0 | 183MB | CSS10: A Collection of Single Speaker Speech Datasets for 10 L |
| [gemengtju/Tutorial_Separation](https://github.com/gemengtju/Tutorial_Separation) | 485 | MATLAB | - | 76MB | This repo summarizes the tutorials, datasets, papers, codes an |
| [double22a/speech_dataset](https://github.com/double22a/speech_dataset) | 468 | - | Apache-2.0 | 81KB | The dataset of Speech Recognition |
| [marcogdepinto/emotion-classification-from-audio-files](https://github.com/marcogdepinto/emotion-classification-from-audio-files) | 431 | Python | GPL-3.0 | 661MB | Understanding emotions from audio files using neural networks  |
| [SuperKogito/SER-datasets](https://github.com/SuperKogito/SER-datasets) | 420 | HTML | MIT | 4MB | A collection of datasets for the purpose of emotion recognitio |

### science.科学计算（精选 11 个中的 Top 11）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [PolymathicAI/the_well](https://github.com/PolymathicAI/the_well) | 4383 | Jupyter Notebook | BSD-3-Clause | 659MB | A 15TB Collection of Physics Simulation Datasets |
| [ai4s-research/awesome-ai-for-science](https://github.com/ai4s-research/awesome-ai-for-science) | 1893 | - | MIT | 1MB | A curated list of awesome AI tools, libraries, papers, dataset |
| [hendrycks/math](https://github.com/hendrycks/math) | 1384 | Python | MIT | 17MB | The MATH Dataset (NeurIPS 2021) |
| [TimoBolkart/FLAME-Universe](https://github.com/TimoBolkart/FLAME-Universe) | 696 | - | - | 6MB | Summary of publicly available ressources such as code, dataset |
| [OpenGeoscience/geojs](https://github.com/OpenGeoscience/geojs) | 470 | JavaScript | Apache-2.0 | 109MB | High-performance visualization and interactive data exploratio |
| [kjappelbaum/awesome-chemistry-datasets](https://github.com/kjappelbaum/awesome-chemistry-datasets) | 419 | - | CC0-1.0 | 42KB | overview of datasets for ML in chemistry |
| [jonathanking/sidechainnet](https://github.com/jonathanking/sidechainnet) | 366 | Python | BSD-3-Clause | 57MB | An all-atom protein structure dataset for machine learning. |
| [mochilang/mochi](https://github.com/mochilang/mochi) | 336 | Scheme | MIT | 185MB | Mochi is a small, fast, embeddable programming language design |
| [plinder-org/plinder](https://github.com/plinder-org/plinder) | 305 | Python | GPL-2.0 | 51MB | Protein Ligand INteraction Dataset and Evaluation Resource |
| [zwhe99/DeepMath](https://github.com/zwhe99/DeepMath) | 301 | Python | MIT | 24MB | A Large-Scale, Challenging, Decontaminated, and Verifiable Mat |
| [a-r-j/ProteinWorkshop](https://github.com/a-r-j/ProteinWorkshop) | 277 | Python | MIT | 22MB | Benchmarking framework for protein representation learning. In |

### medical.医疗健康（精选 10 个中的 Top 10）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [openmedlab/Awesome-Medical-Dataset](https://github.com/openmedlab/Awesome-Medical-Dataset) | 2093 | - | - | 223MB | Collection of awesome medical dataset resources. |
| [antontarasenko/smq](https://github.com/antontarasenko/smq) | 1538 | TSQL | Apache-2.0 | 120KB | A collection of SQL queries to social media datasets. |
| [adalca/medical-datasets](https://github.com/adalca/medical-datasets) | 923 | - | - | 70KB | tracking medical datasets, with a focus on medical imaging |
| [YerevaNN/mimic3-benchmarks](https://github.com/YerevaNN/mimic3-benchmarks) | 890 | Python | MIT | 17MB | Python suite to construct benchmark machine learning datasets  |
| [uni-medical/Project-Imaging-X](https://github.com/uni-medical/Project-Imaging-X) | 477 | Python | MIT | 60MB | Project Imaging-X: A Survey of 1000+ Open-Access Medical Imagi |
| [vinbigdata-medical/vindr-lab](https://github.com/vinbigdata-medical/vindr-lab) | 377 | - | MIT | 12MB | A Data Platform for Medical AI that enables building high-qual |
| [medtorch/awesome-healthcare-ai](https://github.com/medtorch/awesome-healthcare-ai) | 354 | - | CC0-1.0 | 68KB | A curated list of awesome open source healthcare tools, algori |
| [AstraZeneca/awesome-drug-discovery-knowledge-graphs](https://github.com/AstraZeneca/awesome-drug-discovery-knowledge-graphs) | 266 | - | Apache-2.0 | 429KB | A collection of research papers, datasets and software related |
| [xiangyue9607/BioNEV](https://github.com/xiangyue9607/BioNEV) | 231 | Python | MIT | 28MB | Graph Embedding Evaluation / Code and Datasets for  "Graph Emb |
| [rexrodeo/american-healthcare-conundrum](https://github.com/rexrodeo/american-healthcare-conundrum) | 230 | Python | MIT | 18MB | Investigative data journalism: quantifying fixable waste in US |

### timeseries.时序/金融（精选 13 个中的 Top 13）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [Jon-Becker/prediction-market-analysis](https://github.com/Jon-Becker/prediction-market-analysis) | 3766 | Python | MIT | 158MB | A framework for collecting and analyzing prediction market dat |
| [rob-med/awesome-TS-anomaly-detection](https://github.com/rob-med/awesome-TS-anomaly-detection) | 3161 | - | - | 144KB | List of tools & datasets for anomaly detection on time-series  |
| [financial-datasets/mcp-server](https://github.com/financial-datasets/mcp-server) | 2281 | Python | MIT | 23KB | An MCP server for interacting with the Financial Datasets stoc |
| [thuml/OpenLTM](https://github.com/thuml/OpenLTM) | 550 | Jupyter Notebook | MIT | 3MB | Implementations, Pre-training Code and Datasets of Large Time- |
| [GoogleCloudPlatform/covid-19-open-data](https://github.com/GoogleCloudPlatform/covid-19-open-data) | 488 | Python | Apache-2.0 | 10MB | Datasets of daily time-series data related to COVID-19 for ove |
| [Zdong104/FNSPID_Financial_News_Dataset](https://github.com/Zdong104/FNSPID_Financial_News_Dataset) | 456 | Python | NOASSERTION | 106MB | FNSPID: A Comprehensive Financial News Dataset in Time Series |
| [XiaoxiaoMa-MQ/Awesome-Deep-Graph-Anomaly-Detection](https://github.com/XiaoxiaoMa-MQ/Awesome-Deep-Graph-Anomaly-Detection) | 384 | - | MIT | 16MB | Awesome graph anomaly detection techniques built based on deep |
| [woshijielie/stock_prediction_and_recommendation](https://github.com/woshijielie/stock_prediction_and_recommendation) | 366 | Jupyter Notebook | - | 34MB | A comprehensive React-based stock market analysis dashboard th |
| [thedatumorg/TSB-AD](https://github.com/thedatumorg/TSB-AD) | 319 | Python | Apache-2.0 | 15MB | Time-Series Anomaly Detection / Algorithms + Datasets + Tutori |
| [rakshitha123/TSForecasting](https://github.com/rakshitha123/TSForecasting) | 242 | R | NOASSERTION | 304KB | This repository contains the implementations related to the ex |
| [wangtz19/Awesome-NTA](https://github.com/wangtz19/Awesome-NTA) | 196 | - | CC0-1.0 | 1MB | A curation of awesome papers, datasets and tools about network |
| [dineshresearch/Novel-Deep-Learning-Model-for-Traffic-Sign-Detection-Using-Capsule-Networks](https://github.com/dineshresearch/Novel-Deep-Learning-Model-for-Traffic-Sign-Detection-Using-Capsule-Networks) | 126 | Jupyter Notebook | MIT | 5MB | capsule networks that achieves outstanding performance on the  |
| [AbertayMachineLearningGroup/network-threats-taxonomy](https://github.com/AbertayMachineLearningGroup/network-threats-taxonomy) | 104 | TeX | GPL-3.0 | 885KB | Machine Learning based Intrusion Detection Systems are difficu |

### graph.图/推荐（精选 17 个中的 Top 15）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [philackm/ScrollableGraphView](https://github.com/philackm/ScrollableGraphView) | 5284 | Swift | MIT | 25MB | An adaptive scrollable graph view for iOS to visualise simple  |
| [snap-stanford/ogb](https://github.com/snap-stanford/ogb) | 2092 | Python | MIT | 4MB | Benchmark datasets, data loaders, and evaluators for graph mac |
| [RUCAIBox/RecSysDatasets](https://github.com/RUCAIBox/RecSysDatasets) | 1257 | Python | - | 430KB | This is a repository of public data sources for Recommender Sy |
| [caserec/Datasets-for-Recommender-Systems](https://github.com/caserec/Datasets-for-Recommender-Systems) | 1105 | Jupyter Notebook | - | 74MB | This is a repository of a topic-centric public data sources in |
| [yueliu1999/Awesome-Deep-Graph-Clustering](https://github.com/yueliu1999/Awesome-Deep-Graph-Clustering) | 1016 | Python | MIT | 672KB | [IEEE T-KDE 2026] Awesome Deep Graph Clustering is a collectio |
| [CRIPAC-DIG/SR-GNN](https://github.com/CRIPAC-DIG/SR-GNN) | 853 | Python | - | 130KB | [AAAI 2019] Source code and datasets for "Session-based Recomm |
| [futuredapp/donut](https://github.com/futuredapp/donut) | 551 | Kotlin | MIT | 940KB | Doughnut-like graph view capable of displaying multiple datase |
| [PrincetonLIPS/SketchGraphs](https://github.com/PrincetonLIPS/SketchGraphs) | 479 | Python | MIT | 11MB | A dataset of 15 million CAD sketches with geometric constraint |
| [THUDM/CogQA](https://github.com/THUDM/CogQA) | 457 | Python | MIT | 36MB | Source code and dataset for ACL 2019 paper "Cognitive Graph fo |
| [khanhnamle1994/movielens](https://github.com/khanhnamle1994/movielens) | 451 | Jupyter Notebook | MIT | 43MB | 4 different recommendation engines for the MovieLens dataset. |
| [HCIILAB/Scene-Text-Recognition-Recommendations](https://github.com/HCIILAB/Scene-Text-Recognition-Recommendations) | 354 | Python | MIT | 1MB | Papers, Datasets, Algorithms, SOTA for STR. Long-time Maintain |
| [librahu/HIN-Datasets-for-Recommendation-and-Network-Embedding](https://github.com/librahu/HIN-Datasets-for-Recommendation-and-Network-Embedding) | 352 | - | - | 25MB | Heterogeneous Information Network Datasets for Recommendation  |
| [easezyc/Multitask-Recommendation-Library](https://github.com/easezyc/Multitask-Recommendation-Library) | 348 | Python | MIT | 53KB | MTReclib provides a PyTorch implementation of multi-task recom |
| [THUDM/ComiRec](https://github.com/THUDM/ComiRec) | 310 | Python | - | 23KB | Source code and dataset for KDD 2020 paper "Controllable Multi |
| [TrustAGI-Lab/graph_datasets](https://github.com/TrustAGI-Lab/graph_datasets) | 300 | - | - | 41MB | A Repository of Benchmark Graph Datasets for Graph Classificat |

### web.Web/网页（精选 2 个中的 Top 2）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [NaiboWang/EasySpider](https://github.com/NaiboWang/EasySpider) | 44398 | JavaScript | AGPL-3.0 | 149MB | A visual no-code/code-free web crawler/spider易采集：一个可视化浏览器自动化测试 |
| [mdn/browser-compat-data](https://github.com/mdn/browser-compat-data) | 5723 | JSON | CC0-1.0 | 121MB | Browser compatibility data for Web technologies as displayed o |

### code.代码（精选 3 个中的 Top 3）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [minar09/awesome-virtual-try-on](https://github.com/minar09/awesome-virtual-try-on) | 3157 | - | - | 306KB | A curated list of awesome research papers, projects, code, dat |
| [github/CodeSearchNet](https://github.com/github/CodeSearchNet) | 2442 | Jupyter Notebook | MIT | 29MB | Datasets, tools, and benchmarks for representation learning of |
| [ENSTA-U2IS-AI/awesome-uncertainty-deeplearning](https://github.com/ENSTA-U2IS-AI/awesome-uncertainty-deeplearning) | 823 | - | MIT | 456KB | This repository contains a collection of surveys, datasets,  p |

### general.通用聚合（精选 43 个中的 Top 15）

| 仓库 | ★Stars | 语言 | 许可 | 仓库规模 | 说明 |
|:-----|:------:|:-----|:-----|:---------|:-----|
| [public-apis/public-apis](https://github.com/public-apis/public-apis) | 468180 | Python | MIT | 8MB | A collective list of free APIs |
| [awesomedata/awesome-public-datasets](https://github.com/awesomedata/awesome-public-datasets) | 78416 | - | MIT | 1MB | A topic-centric list of HQ open datasets. |
| [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) | 61654 | Python | GPL-3.0 | 32MB | ⭐AI-driven public opinion & trend monitor with multi-platform  |
| [HumanSignal/label-studio](https://github.com/HumanSignal/label-studio) | 28106 | TypeScript | Apache-2.0 | 2.8GB | Label Studio is a multi-type data labeling and annotation tool |
| [dianping/cat](https://github.com/dianping/cat) | 18943 | Java | Apache-2.0 | 111MB | CAT 作为服务端项目基础组件，提供了 Java, C/C++, Node.js, Python, Go 等多语言客户端，已 |
| [alibaba/DataX](https://github.com/alibaba/DataX) | 17327 | Java | NOASSERTION | 22MB | DataX是阿里云DataWorks数据集成的开源版本。 |
| [JoeanAmier/TikTokDownloader](https://github.com/JoeanAmier/TikTokDownloader) | 15500 | Python | GPL-3.0 | 27MB | 抖音 / TikTok 平台作品下载/数据采集工具 |
| [NVIDIA/cosmos](https://github.com/NVIDIA/cosmos) | 11584 | Jupyter Notebook | NOASSERTION | 257MB | NVIDIA Cosmos is an open platform of world models, datasets, a |
| [apachecn/apachecn-algo-zh](https://github.com/apachecn/apachecn-algo-zh) | 11147 | JavaScript | - | 1MB | ApacheCN 数据结构与算法译文集 |
| [fengdu78/Data-Science-Notes](https://github.com/fengdu78/Data-Science-Notes) | 8579 | Jupyter Notebook | - | 51MB | 数据科学的笔记以及资料搜集 |
| [kangvcar/InfoSpider](https://github.com/kangvcar/InfoSpider) | 8244 | Python | GPL-3.0 | 41MB | INFO-SPIDER 是一个集众多数据源于一身的爬虫工具箱🧰，旨在安全快捷的帮助用户拿回自己的数据，工具代码开源，流程透明 |
| [openlm-research/open_llama](https://github.com/openlm-research/open_llama) | 7527 | - | Apache-2.0 | 2MB | OpenLLaMA, a permissively licensed open source reproduction of |
| [cv-cat/Spider_XHS](https://github.com/cv-cat/Spider_XHS) | 7374 | Python | - | 18MB | 小红书爬虫数据采集，小红书全域运营解决方案 |
| [PAIR-code/facets](https://github.com/PAIR-code/facets) | 7337 | Jupyter Notebook | Apache-2.0 | 23MB | Visualizations for machine learning datasets |
| [luyishisi/Anti-Anti-Spider](https://github.com/luyishisi/Anti-Anti-Spider) | 7279 | Python | - | 147MB | 越来越多的网站具有反爬虫特性，有的用图片隐藏关键数据，有的使用反人类的验证码，建立反反爬虫的代码仓库，通过与不同特性的网站做 |

---

## §5 关键发现与洞察

### 5.1 LLM 语料全链路已开源（对 AI 训练最有价值）

从 GitHub 可检索到 LLM 数据全生命周期仓库：

| 阶段 | 代表仓库 | 说明 |
|:-----|:---------|:-----|
| 预训练语料 | RedPajama-Data / allenai/dolma / EleutherAI/the-pile / MNBVC(中文) | 数千亿~数万亿 tokens，GitHub 仓库多为代码入口 |
| 学术语料 | allenai/s2orc / peS2o / olmocr(PDF 线性化) | 论文 PDF → 训练语料的工程化管线 |
| 指令微调 | stanford_alpaca / self-instruct / AlpacaDataCleaned / yaodongC/awesome-instruction-dataset | 52k 指令对范式 → 数据清洗质量之争 |
| 对齐/RLHF | PKU-Alignment/beavertails / glgh/awesome-llm-human-preference-datasets | 偏好数据集聚合 |
| 评测基准 | opencompass / CLUE / MATH / beir | 能力评估标准化 |

[来源: 本调研实测]

**洞察**：**指令数据清洗（AlpacaDataCleaned 1.6k★）与合成数据（GPTeacher/cosmopedia）的出现，标志 LLM 数据从"采集时代"进入"加工时代"**——数据质量 > 数据规模成为新共识 [来源: 本调研推导]。

### 5.2 中文数据集是独立活跃分支（与国产模型生态对应）

| 类型 | 代表 |
|:-----|:-----|
| 中文 NLP 语料聚合 | funNLP 82.6k / SophonPlus/ChineseNlpCorpus / InsaneLife/ChineseNLPCorpus |
| 大规模语料 | brightmart/nlp_chinese_corpus / MNBVC(2.6T tokens) / SkyPile-150B(核录 MISS，载体迁移) |
| 中文基准 | CLUE / CLUEDatasetSearch / ChineseGLUE / GAOKAO-Bench / PromptCBLUE |
| 中文对话/医疗 | Chinese-medical-dialogue-data / Huatuo-26M / cMedQA2 |
| 中文 LLM 资源导航 | AiHubCN/Awesome-Chinese-LLM 22.7k |

[来源: 本调研实测]

**洞察**：中文数据生态与英文生态并行发展，**医疗/法律等垂直领域中文数据集是差异化富矿**（医学对话 1.75k★、法律资源 996★）[来源: 本调研实测]。

### 5.3 数据工具生态：造数据比找数据更稀缺

163 个工具/资料仓库中，标注（Label Studio 28.1k/CVAT 16.6k/doccano 10.8k）、采集（EasySpider 44.4k/TikTokDownloader 15.5k/InfoSpider 8.2k）、合成（Faker 19.4k/img2dataset 4.4k/easy-dataset 14.8k/autolabel 2.3k）、编排（DataX 17.3k）四类构成了数据上游产业链 [来源: 本调研实测]。

**洞察**：对本知识库场景（服务器/AI 基础设施），**loghub（2.8k★，日志数据集）与 Security-Datasets（1.8k★，安全事件数据集）是运维/RAS 方向的直接相关资产**；NVIDIA/cosmos（11.6k★）提供世界模型训练数据管线参考 [来源: 本调研实测]。

### 5.4 载体分化：GitHub 是入口，HF Hub 是主体

40 仓库经典核录中 13 个 MISS（c4/falcon-refinedweb/roots/SlimPajama/SkyPile/COIG/the-stack/cosmopedia/LAION 等）——**全部是 HF Hub 承载的大规模语料**。选型规则：**GitHub 仓库看代码与生态，HF Hub 看数据本体**；两者互补不互斥 [来源: 本调研实测]。

---

## §6 使用建议与合规注意事项

### 6.1 选型决策树

```
need -> dataset category (corpus/instruction/image/timeseries ...)
  -> size scale (GB+: HF Hub; MB: GitHub direct)
  -> license check (code license vs data license)
  -> activity (pushed_at < 1 year first)
  -> carrier download (HF datasets / git-lfs / official site)
```

### 6.2 合规五查（数据集使用前必查）

1. **许可分离**：仓库 license 字段 ≠ 数据内容许可；大语料（RedPajama/dolma 等）有自己的使用条款
2. **隐私与敏感数据**：医疗（MIMIC-III 需授权）、人脸、对话数据可能含个人信息——商用前必须审查
3. **爬取来源**：中文语料/爬虫类数据集的采集合规性需独立评估（RULE.md §6 素材批判使用）
4. **版本与更新**：数据集常有 v2/v3 修订（如 AlpacaDataCleaned 修正原 Alpaca 噪声），引用须注明版本
5. **质量门槛**：GitHub 仓库星标高 ≠ 数据质量高（工具仓库与数据仓库混流），关键数据须抽样验证

### 6.3 导入知识库策略

- **导航类**（awesome-* 聚合清单）→ 适合链接索引，不适合 submodule 导入（易过时）
- **工具类**（标注/采集/合成）→ 只做链接参考，需要运行环境
- **数据入口类**（dolma/the-pile 等代码仓）→ 可 submodule 导入代码做管线参考，**数据本体留 HF Hub**
- **中文语料类** → 批判使用，重点审查采集合规与隐私（RULE.md §6）

---

## §7 数据缺口与后续动作

| 缺口 | 说明 | 后续动作 |
|:-----|:-----|:---------|
| 数据集本体参数（样本量/格式） | 本次仅从 description 提取，未读 README | 对 Top 50 精选仓库补读 README，标注样本量/格式/载体 |
| HF Hub 载体数据未采集 | c4/refinedweb 等 13 个 MISS 仓库的数据参数 | 后续用 HF API 补采（datasets-server），形成 GitHub+HF 双载体视图 |
| 分类边界噪声 | 部分工具/平台仓库（langfuse/cat 等）混入数据集类 | 已标注，v2.0 可用 topics 二次校验 |
| 许可审计未逐仓完成 | 仅记录 spdx_id，未核数据条款 | 对高优先仓库（LLM 语料）逐个核 README 许可 |
| 时效性 | 星标/时间为 2026-08-22 快照 | 建立季度巡检（diff 星标变化识别新兴数据集） |

---

## 附录 A：完整仓库清单（544 个全参数）

### llm.LLM/AI 训练语料（107 个）

- [fighting41love/funNLP](https://github.com/fighting41love/funNLP) ★82593 [Python/-/170MB] 中英文敏感词、语言检测、中外手机/电话归属地/运营商查询、名字推断性别、手机号抽取、身份证抽取、邮箱抽取、中日文人名库、中文缩写库、拆字词典、词汇情感值、停用词
- [langfuse/langfuse](https://github.com/langfuse/langfuse) ★33540 [TypeScript/NOASSERTION/210MB] 🪢 Open source AI engineering platform: LLM evals, observability, metrics, prompt
- [tatsu-lab/stanford_alpaca](https://github.com/tatsu-lab/stanford_alpaca) ★30245 [Python/Apache-2.0/8MB] Code and documentation to train Stanford's Alpaca models, and generate the data.
- [huggingface/datasets](https://github.com/huggingface/datasets) ★21846 [Python/Apache-2.0/113MB] 🤗 The largest hub of ready-to-use datasets for AI models with fast, easy-to-use 
- [hasaneyldrm/exercises-dataset](https://github.com/hasaneyldrm/exercises-dataset) ★20568 [HTML/NOASSERTION/125MB] 1,324-exercise fitness dataset — animation GIFs, 180×180 thumbnails, muscle-grou
- [allenai/olmocr](https://github.com/allenai/olmocr) ★19369 [Python/Apache-2.0/349MB] Toolkit for linearizing PDFs for LLM datasets/training
- [ConardLi/easy-dataset](https://github.com/ConardLi/easy-dataset) ★14812 [JavaScript/NOASSERTION/19MB] A powerful tool for creating datasets for LLM fine-tuning 、RAG and Eval
- [dataelement/bisheng](https://github.com/dataelement/bisheng) ★11901 [Python/Apache-2.0/203MB] BISHENG is an open LLM devops platform for next generation Enterprise AI applica
- [brightmart/nlp_chinese_corpus](https://github.com/brightmart/nlp_chinese_corpus) ★9909 [-/MIT/4MB] 大规模中文自然语言处理语料  Large Scale Chinese Corpus for NLP
- [open-compass/opencompass](https://github.com/open-compass/opencompass) ★7327 [Python/Apache-2.0/7MB] OpenCompass is an LLM evaluation platform, supporting a wide range of models (Ll
- [lonePatient/awesome-pretrained-chinese-nlp-models](https://github.com/lonePatient/awesome-pretrained-chinese-nlp-models) ★5582 [Python/MIT/871KB] Awesome Pretrained Chinese NLP Models，高质量中文预训练模型&大模型&多模态模型&大语言模型集合
- [Kiln-AI/Kiln](https://github.com/Kiln-AI/Kiln) ★5031 [Python/NOASSERTION/49MB] Build, Evaluate, and Optimize AI Systems. Includes evals, RAG, agents, fine-tuni
- [mlabonne/llm-datasets](https://github.com/mlabonne/llm-datasets) ★4747 [-/-/72KB] Curated list of datasets and tools for post-training.
- [yizhongw/self-instruct](https://github.com/yizhongw/self-instruct) ★4610 [Python/Apache-2.0/60MB] Aligning pretrained language models with instruction data generated by themselve
- [CLUEbenchmark/CLUE](https://github.com/CLUEbenchmark/CLUE) ★4279 [Python/-/3MB] 中文语言理解测评基准 Chinese Language Understanding Evaluation Benchmark: datasets, baseli
- [esbatmop/MNBVC](https://github.com/esbatmop/MNBVC) ★4266 [-/MIT/674KB] MNBVC(Massive Never-ending BT Vast Chinese corpus)超大规模中文语料集。对标chatGPT训练的40T数据。MN
- [OpenCSGs/csghub](https://github.com/OpenCSGs/csghub) ★4098 [Vue/Apache-2.0/52MB] CSGHub is a brand-new open-source platform for managing LLMs, developed by the O
- [chrieke/awesome-satellite-imagery-datasets](https://github.com/chrieke/awesome-satellite-imagery-datasets) ★3916 [-/MIT/2MB] 🛰️ List of satellite image training datasets with annotations for computer visio
- [verazuo/jailbreak_llms](https://github.com/verazuo/jailbreak_llms) ★3789 [Jupyter Notebook/MIT/4MB] [CCS'24] A dataset consists of 15,140 ChatGPT prompts from Reddit, Discord, webs
- [codefuse-ai/Awesome-Code-LLM](https://github.com/codefuse-ai/Awesome-Code-LLM) ★3430 [-/-/11MB] [TMLR] A curated list of language modeling researches for code (and other softwa
- [Zjh-819/LLMDataHub](https://github.com/Zjh-819/LLMDataHub) ★3412 [-/MIT/5MB] A quick guide (especially) for trending instruction finetuning datasets 
- [yunlong10/Awesome-LLMs-for-Video-Understanding](https://github.com/yunlong10/Awesome-LLMs-for-Video-Understanding) ★3270 [-/-/13MB] 🔥🔥🔥 [IEEE TCSVT] Latest Papers, Codes and Datasets on Vid-LLMs.
- [cirosantilli/china-dictatorship](https://github.com/cirosantilli/china-dictatorship) ★3156 [HTML/CC-BY-SA-4.0/103MB] 反中共政治宣传库。Anti Chinese government propaganda. 住在中国真名用户的网友请别给星星，不然你要被警察请喝茶。常见问答集，新
- [FreedomIntelligence/Awesome-AI4Med](https://github.com/FreedomIntelligence/Awesome-AI4Med) ★2868 [-/-/656KB] A curated list of medical LLMs, multimodal systems, datasets, benchmarks, and mo
- [aaron-xichen/pytorch-playground](https://github.com/aaron-xichen/pytorch-playground) ★2716 [Python/MIT/47KB] Base pretrained models and datasets in pytorch (MNIST, SVHN, CIFAR10, CIFAR100, 
- [refuel-ai/autolabel](https://github.com/refuel-ai/autolabel) ★2327 [Python/MIT/53MB] Label, clean and enrich text datasets with LLMs.
- [snap-stanford/snap](https://github.com/snap-stanford/snap) ★2289 [C++/NOASSERTION/159MB] Stanford Network Analysis Platform (SNAP) is a general purpose network analysis 
- [openai/gpt-2-output-dataset](https://github.com/openai/gpt-2-output-dataset) ★2026 [Python/MIT/272KB] Dataset of GPT-2 outputs for research in detection, biases, and more
- [eosphoros-ai/DB-GPT-Hub](https://github.com/eosphoros-ai/DB-GPT-Hub) ★2005 [Python/MIT/63MB] A repository that contains models, datasets, and fine-tuning techniques for DB-G
- [gege-circle/.github](https://github.com/gege-circle/.github) ★1982 [-/-/2MB] 这里是GitHub的草场，也是戈戈圈爱好者的交流地，主要讨论动漫、游戏、科技、人文、生活等所有话题，欢迎各位小伙伴们在此讨论趣事。This is GitHub 
- [future-agi/future-agi](https://github.com/future-agi/future-agi) ★1785 [Python/Apache-2.0/143MB] Open-source, end-to-end platform for evaluating, observing, and improving LLM an
- [ChineseGLUE/ChineseGLUE](https://github.com/ChineseGLUE/ChineseGLUE) ★1782 [Python/-/3MB] Language Understanding Evaluation benchmark for Chinese: datasets, baselines, pr
- [SmartFlowAI/EmoLLM](https://github.com/SmartFlowAI/EmoLLM) ★1777 [Python/MIT/259MB] 心理健康大模型 (LLM x Mental Health), Pre & Post-training & Dataset & Evaluation & Depo
- [charent/ChatLM-mini-Chinese](https://github.com/charent/ChatLM-mini-Chinese) ★1725 [Python/Apache-2.0/13MB] 中文对话0.2B小模型（ChatLM-Chinese-0.2B），开源所有数据集来源、数据清洗、tokenizer训练、模型预训练、SFT指令微调、RLHF优化
- [njvisionpower/Safety-Helmet-Wearing-Dataset](https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset) ★1719 [Python/MIT/3MB] Safety helmet wearing detect dataset, with pretrained model
- [EleutherAI/the-pile](https://github.com/EleutherAI/the-pile) ★1672 [Python/MIT/265KB] 
- [teknium1/GPTeacher](https://github.com/teknium1/GPTeacher) ★1666 [Python/MIT/10MB] A collection of modular datasets generated by GPT-4, General-Instruct - Roleplay
- [gururise/AlpacaDataCleaned](https://github.com/gururise/AlpacaDataCleaned) ★1606 [Python/Apache-2.0/78MB] Alpaca dataset from Stanford, cleaned and curated
- [yueliu1999/Awesome-Jailbreak-on-LLMs](https://github.com/yueliu1999/Awesome-Jailbreak-on-LLMs) ★1598 [-/MIT/368KB] Awesome-Jailbreak-on-LLMs is a collection of state-of-the-art, novel, exciting j
- [allenai/dolma](https://github.com/allenai/dolma) ★1536 [Python/Apache-2.0/64MB] Data and tools for generating and inspecting OLMo pre-training data. 
- [openai/SWELancer-Benchmark](https://github.com/openai/SWELancer-Benchmark) ★1431 [-/-/54MB] This repo contains the dataset and code for the paper "SWE-Lancer: Can Frontier 
- [gokayfem/awesome-vlm-architectures](https://github.com/gokayfem/awesome-vlm-architectures) ★1306 [Markdown/CC0-1.0/54MB] Curated visual catalog of 155+ vision-language model (VLM/MLLM) architectures: p
- [yaodongC/awesome-instruction-dataset](https://github.com/yaodongC/awesome-instruction-dataset) ★1155 [-/-/34KB] A collection of open-source dataset to train instruction-following LLMs (ChatGPT
- [allenai/s2orc](https://github.com/allenai/s2orc) ★1080 [Python/-/4MB] S2ORC: The Semantic Scholar Open Research Corpus:  https://www.aclweb.org/anthol
- [facebookresearch/cc_net](https://github.com/facebookresearch/cc_net) ★1045 [Python/MIT/254KB] Tools to download and cleanup Common Crawl data
- [1adrianb/2D-and-3D-face-alignment](https://github.com/1adrianb/2D-and-3D-face-alignment) ★972 [Lua/NOASSERTION/39KB] This repository implements a demo of the networks described in "How far are we f
- [Yuan-ManX/ai-audio-datasets](https://github.com/Yuan-ManX/ai-audio-datasets) ★962 [-/MIT/1MB] AI Audio Datasets (AI-ADS) 🎵, including Speech, Music, and Sound Effects, which 
- [BinWang28/audio-ai-hub](https://github.com/BinWang28/audio-ai-hub) ★950 [Python/-/26MB] The hub for audio AI research: papers, open models, benchmarks & datasets across
- [THUDM/P-tuning](https://github.com/THUDM/P-tuning) ★939 [Python/MIT/6MB] A novel method to tune language models. Codes and datasets for paper ``GPT under
- [BatsResearch/bonito](https://github.com/BatsResearch/bonito) ★829 [Python/BSD-3-Clause/815KB] A lightweight library for generating synthetic instruction tuning datasets for y
- [coderonion/awesome-llm-and-aigc](https://github.com/coderonion/awesome-llm-and-aigc) ★814 [-/-/276KB] 🚀🚀🚀A collection of some awesome public projects about Large Language Model(LLM),
- [Mcompetitions/M4-methods](https://github.com/Mcompetitions/M4-methods) ★810 [R/-/1.4GB] Data, Benchmarks, and methods submitted to the M4 forecasting competition
- [facebookresearch/CodeGen](https://github.com/facebookresearch/CodeGen) ★778 [Python/MIT/14MB] Reference implementation of code generation projects from Facebook AI Research. 
- [huyvnphan/PyTorch_CIFAR10](https://github.com/huyvnphan/PyTorch_CIFAR10) ★695 [Python/MIT/7MB] Pretrained TorchVision models on CIFAR10 dataset (with weights)
- [ultralytics/assets](https://github.com/ultralytics/assets) ★660 [-/AGPL-3.0/102MB] Shared Ultralytics logos, media, sample images, pretrained model weights, datase
- [Q-Future/Q-Align](https://github.com/Q-Future/Q-Align) ★618 [Python/NOASSERTION/42MB] ③[ICML2024] [IQA, IAA, VQA] All-in-one Foundation Model for visual scoring. Can 
- [levyflux/AViD](https://github.com/levyflux/AViD) ★605 [Python/MIT/26MB] Framework that enables fine-tuning of vision-language grounding models on custom
- [xiyuanzh/awesome-llm-time-series](https://github.com/xiyuanzh/awesome-llm-time-series) ★519 [-/-/4MB] tracking papers, datasets, and models of "large language model (LLM) for time se
- [RenzeLou/awesome-instruction-learning](https://github.com/RenzeLou/awesome-instruction-learning) ★512 [Python/MIT/6MB] Papers and Datasets on Instruction Tuning and Following. ✨✨✨
- [PinataFarms/DAD-3DHeads](https://github.com/PinataFarms/DAD-3DHeads) ★510 [Python/NOASSERTION/64MB] Official repo for DAD-3DHeads: A Large-scale Dense, Accurate and Diverse Dataset
- [fynnfluegge/codeqai](https://github.com/fynnfluegge/codeqai) ★492 [Python/Apache-2.0/584KB] Local first semantic code search and chat | Leverage custom copilots with fine-t
- [Naman-ntc/Pytorch-Human-Pose-Estimation](https://github.com/Naman-ntc/Pytorch-Human-Pose-Estimation) ★485 [Python/MIT/569KB] Implementation of various human pose estimation models in pytorch on multiple da
- [YuanGongND/ltu](https://github.com/YuanGongND/ltu) ★478 [Python/-/28MB] Code, Dataset, and Pretrained Models for Audio and Speech Large Language Model "
- [skanti/Scan2CAD](https://github.com/skanti/Scan2CAD) ★476 [C++/NOASSERTION/31MB] [CVPR'19] Dataset and code used in the research project Scan2CAD: Learning CAD M
- [InternScience/Awesome-Scientific-Datasets-and-LLMs](https://github.com/InternScience/Awesome-Scientific-Datasets-and-LLMs) ★458 [-/MIT/9MB] A curated collection of papers, datasets, and resources on Scientific Datasets a
- [AI4Bharat/IndicLLMSuite](https://github.com/AI4Bharat/IndicLLMSuite) ★414 [Python/MIT/69KB] A blueprint for creating Pretraining and Fine-Tuning  datasets for Indic languag
- [SupritYoung/Zhongjing](https://github.com/SupritYoung/Zhongjing) ★399 [Python/Apache-2.0/11MB] A Chinese medical ChatGPT based on LLaMa, training from large-scale pretrain cor
- [michael-wzhu/PromptCBLUE](https://github.com/michael-wzhu/PromptCBLUE) ★393 [Python/-/2MB] PromptCBLUE: a large-scale instruction-tuning dataset for multi-task and few-sho
- [glgh/awesome-llm-human-preference-datasets](https://github.com/glgh/awesome-llm-human-preference-datasets) ★390 [-/MIT/12KB] A curated list of Human Preference Datasets for LLM fine-tuning, RLHF, and eval.
- [vasistalodagala/whisper-finetune](https://github.com/vasistalodagala/whisper-finetune) ★367 [Python/MIT/56KB] Fine-tune and evaluate Whisper models for Automatic Speech Recognition (ASR) on 
- [zhoubolei/moments_models](https://github.com/zhoubolei/moments_models) ★367 [Python/BSD-2-Clause/83KB] The pretrained models trained on Moments in Time Dataset
- [cirosantilli/china-dictatroship-7](https://github.com/cirosantilli/china-dictatroship-7) ★360 [HTML/CC-BY-SA-4.0/17MB] 反中共政治宣传库。Anti Chinese government propaganda. https://github.com/cirosantilli/chi
- [zhilizju/Awesome-instruction-tuning](https://github.com/zhilizju/Awesome-instruction-tuning) ★344 [Python/Apache-2.0/6MB] A curated list of awesome instruction tuning datasets, models, papers and reposi
- [haolpku/K12-KGraph](https://github.com/haolpku/K12-KGraph) ★342 [Python/NOASSERTION/976KB] A curriculum-aligned knowledge graph, benchmark, and multimodal training dataset
- [onejune2018/Awesome-Medical-Healthcare-Dataset-For-LLM](https://github.com/onejune2018/Awesome-Medical-Healthcare-Dataset-For-LLM) ★332 [-/MIT/134KB] A curated list of popular Datasets, Models and Papers for LLMs in Medical/Health
- [Project-AgML/AgML](https://github.com/Project-AgML/AgML) ★327 [Python/Apache-2.0/218MB] AgML is a centralized framework for agricultural machine learning. AgML provides
- [VSehwag/minimal-diffusion](https://github.com/VSehwag/minimal-diffusion) ★312 [Python/MIT/869KB] A minimal yet resourceful implementation of diffusion models (along with pretrai
- [CASIA-IVA-Lab/VALOR](https://github.com/CASIA-IVA-Lab/VALOR) ★309 [Python/MIT/77MB] [TPAMI2024] Codes and Models for VALOR: Vision-Audio-Language Omni-Perception Pr
- [sayantann11/all-classification-templetes-for-ML](https://github.com/sayantann11/all-classification-templetes-for-ML) ★297 [Python/-/52KB] Classification - Machine Learning This is ‘Classification’ tutorial which is a p
- [night-chen/ToolQA](https://github.com/night-chen/ToolQA) ★286 [Jupyter Notebook/Apache-2.0/311KB]  ToolQA, a new dataset to evaluate the capabilities of LLMs in answering challen
- [molyswu/hand_detection](https://github.com/molyswu/hand_detection) ★278 [Python/-/119MB] using Neural Networks (SSD) on Tensorflow.  This repo documents steps and script
- [Arsey/keras-transfer-learning-for-oxford102](https://github.com/Arsey/keras-transfer-learning-for-oxford102) ★277 [Python/MIT/40MB] Keras pretrained models (VGG16, InceptionV3, Resnet50, Resnet152) + Transfer Lea
- [yukimasano/PASS](https://github.com/yukimasano/PASS) ★269 [Python/MIT/7MB] The PASS dataset: pretrained models and how to get the data
- [raunak-agarwal/instruction-datasets](https://github.com/raunak-agarwal/instruction-datasets) ★261 [-/-/56KB] Datasets for Instruction Tuning of Large Language Models
- [abusufyanvu/6S191_MIT_DeepLearning](https://github.com/abusufyanvu/6S191_MIT_DeepLearning) ★259 [Jupyter Notebook/-/73MB] MIT Introduction to Deep Learning (6.S191) Instructors: Alexander Amini and Ava 
- [neuml/txtinstruct](https://github.com/neuml/txtinstruct) ★238 [Python/Apache-2.0/1MB] 📚 Datasets and models for instruction-tuning
- [Q-Future/Q-Instruct](https://github.com/Q-Future/Q-Instruct) ★238 [Python/NOASSERTION/17MB] ②[CVPR 2024] Low-level visual instruction tuning, with a 200K dataset and a mode
- [JIA-Lab-research/SDSD](https://github.com/JIA-Lab-research/SDSD) ★233 [Python/-/4MB] Seeing Dynamic Scene in the Dark: High-Quality Video Dataset with Mechatronic Al
- [xl1393/EMLDDMM](https://github.com/xl1393/EMLDDMM) ★231 [Jupyter Notebook/MIT/131MB] Robust medical image registration using EM-LDDMM for datasets with differing con
- [zw-zhtlab/Text2Dialog](https://github.com/zw-zhtlab/Text2Dialog) ★218 [Python/MIT/723KB] Automatically extracts long texts into structured dialogue datasets via LLMs, wi
- [mRFWq7LwNPZjaVv5v6eo/cihna-dictattorshrip-8](https://github.com/mRFWq7LwNPZjaVv5v6eo/cihna-dictattorshrip-8) ★203 [HTML/CC-BY-SA-4.0/12MB] 反中共政治宣传库。Anti Chinese government propaganda. https://github.com/cirosantilli/chi
- [KupynOrest/head_detector](https://github.com/KupynOrest/head_detector) ★201 [Python/MIT/50MB] Official repo for VGGHeads: 3D Multi Head Alignment with a Large-Scale Synthetic
- [allenai/citeomatic](https://github.com/allenai/citeomatic) ★197 [Jupyter Notebook/Apache-2.0/1MB] A citation recommendation system that allows users to find relevant citations fo
- [severian42/Vodalus-Expert-LLM-Forge](https://github.com/severian42/Vodalus-Expert-LLM-Forge) ★194 [Jupyter Notebook/-/3MB] Dataset Crafting w/ RAG/Wikipedia ground truth and Efficient Fine-Tuning Using M
- [Aastha2104/Parkinson-Disease-Prediction](https://github.com/Aastha2104/Parkinson-Disease-Prediction) ★194 [Python/-/45KB] Introduction  Parkinson’s Disease is the second most prevalent neurodegenerative
- [panbinibn/OpenPacketFix_](https://github.com/panbinibn/OpenPacketFix_) ★193 [-/MIT/558KB] 大陆修宪香港恶法台湾武统朝鲜毁约美中冷战等都是王沪宁愚弄习思想极左命运共同体的大策划中共窃国这半个多世纪所犯下的滔天罪恶，前期是毛泽东策划的，中期6.4前后是邓
- [google-research-datasets/RxR](https://github.com/google-research-datasets/RxR) ★189 [Python/CC-BY-4.0/30MB] Room-across-Room (RxR) is a large-scale, multilingual dataset for Vision-and-Lan
- [allenai/peS2o](https://github.com/allenai/peS2o) ★189 [Python/Apache-2.0/721KB] Pretraining Efficiently on S2ORC!
- [sarahESL/PubMedCLIP](https://github.com/sarahESL/PubMedCLIP) ★183 [Python/MIT/52MB] Fine-tuning CLIP using ROCO dataset which contains image-caption pairs from PubM
- [CorentinJ/librispeech-alignments](https://github.com/CorentinJ/librispeech-alignments) ★183 [Python/-/17KB] Word alignments generated by the Montreal Forced Aligner for the Librispeech dat
- [people-robots/Awesome-Video-Generation-Post-Training](https://github.com/people-robots/Awesome-Video-Generation-Post-Training) ★183 [-/MIT/85MB] [TMLR] Video Generation Models: A Survey of Post-Training and Alignment | 🔥 A co
- [PKU-Alignment/beavertails](https://github.com/PKU-Alignment/beavertails) ★182 [Makefile/Apache-2.0/2MB] BeaverTails is a collection of datasets designed to facilitate research on safet
- [himanshub1007/Alzhimers-Disease-Prediction-Using-Deep-learning](https://github.com/himanshub1007/Alzhimers-Disease-Prediction-Using-Deep-learning) ★177 [Python/-/555KB] # AD-Prediction  Convolutional Neural Networks for Alzheimer's Disease Predictio
- [AnanyaKumar/transfer_learning](https://github.com/AnanyaKumar/transfer_learning) ★153 [Jupyter Notebook/-/5MB] Framework code with wandb, checkpointing, logging, configs, experimental protoco
- [jettbrains/-L-](https://github.com/jettbrains/-L-) ★153 [-/GPL-3.0/31KB] W3C Strategic Highlights  September 2019  This report was prepared for the Septe
- [1adrianb/face-alignment-training](https://github.com/1adrianb/face-alignment-training) ★151 [Lua/NOASSERTION/16KB] Training code for the networks described in "How far are we from solving the 2D 
- [lightas/ICCV19_Pose_Guided_Occluded_Person_ReID](https://github.com/lightas/ICCV19_Pose_Guided_Occluded_Person_ReID) ★151 [Python/-/19MB] This is the pytorch implementation and dataset of the ICCV2019 paper "Pose-Guide

### nlp.NLP/文本（81 个）

- [AiHubCN/Awesome-Chinese-LLM](https://github.com/AiHubCN/Awesome-Chinese-LLM) ★22747 [-/-/11MB] 整理开源的中文大语言模型，以规模较小、可私有化部署、训练成本较低的模型为主，包括底座模型，垂直领域微调及应用，数据集与教程等。
- [Dujltqzv/Some-Many-Books](https://github.com/Dujltqzv/Some-Many-Books) ★22601 [-/-/2.6GB] 个人收藏书籍列表　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
- [joke2k/faker](https://github.com/joke2k/faker) ★19374 [Python/MIT/12MB] Faker is a Python package that generates fake data for you.
- [doccano/doccano](https://github.com/doccano/doccano) ★10753 [Python/MIT/57MB] Open source annotation tool for machine learning practitioners.
- [facebookresearch/ParlAI](https://github.com/facebookresearch/ParlAI) ★10622 [Python/MIT/146MB] A framework for training and evaluating AI models on a variety of openly availab
- [NirantK/awesome-project-ideas](https://github.com/NirantK/awesome-project-ideas) ★9281 [-/MIT/113KB] Curated list of Machine Learning, NLP, Vision, Recommender Systems Project Ideas
- [xiaobaiTech/golangFamily](https://github.com/xiaobaiTech/golangFamily) ★6965 [Go/-/128KB] 【超全golang面试题合集+golang学习指南+golang知识图谱+入门成长路线】 一份涵盖大部分golang程序员所需要掌握的核心知识。常用第三方库(m
- [SophonPlus/ChineseNlpCorpus](https://github.com/SophonPlus/ChineseNlpCorpus) ★6593 [Jupyter Notebook/-/11MB] 搜集、整理、发布 中文 自然语言处理 语料/数据集，与 有志之士 共同 促进 中文 自然语言处理 的 发展。
- [niderhoff/nlp-datasets](https://github.com/niderhoff/nlp-datasets) ★5995 [-/-/195KB] Alphabetical list of free/public domain datasets with text data for use in Natur
- [cirosantilli/x86-bare-metal-examples](https://github.com/cirosantilli/x86-bare-metal-examples) ★5339 [Assembly/NOASSERTION/1MB] Dozens of minimal operating systems to learn x86 system programming. Tested on U
- [togethercomputer/RedPajama-Data](https://github.com/togethercomputer/RedPajama-Data) ★4979 [Python/Apache-2.0/2MB] The RedPajama-Data repository contains code for preparing large datasets for tra
- [InsaneLife/ChineseNLPCorpus](https://github.com/InsaneLife/ChineseNLPCorpus) ★4610 [Python/-/7MB] 中文自然语言处理数据集，平时做做实验的材料。欢迎补充提交合并。
- [CLUEbenchmark/CLUEDatasetSearch](https://github.com/CLUEbenchmark/CLUEDatasetSearch) ★4455 [Python/-/9MB] 搜索所有中文NLP数据集，附常用英文NLP数据集
- [NAalytics/Assemblies-of-putative-SARS-CoV2-spike-encoding-mRNA-sequences-for-vaccines-BNT-162b2-and-mRNA-1273](https://github.com/NAalytics/Assemblies-of-putative-SARS-CoV2-spike-encoding-mRNA-sequences-for-vaccines-BNT-162b2-and-mRNA-1273) ★3353 [-/-/492KB] RNA vaccines have become a key tool in moving forward through the challenges rai
- [CVI-SZU/Linly](https://github.com/CVI-SZU/Linly) ★3043 [Python/-/7MB] Chinese-LLaMA 1&2、Chinese-Falcon 基础模型；ChatFlow中文对话模型；中文OpenLLaMA模型；NLP预训练/指令微调数据
- [google-deepmind/mathematics_dataset](https://github.com/google-deepmind/mathematics_dataset) ★1963 [Python/Apache-2.0/62KB] This dataset code generates mathematical question and answer pairs, from a range
- [visual-layer/fastdup](https://github.com/visual-layer/fastdup) ★1904 [Python/NOASSERTION/1.8GB] fastdup is a powerful, free tool designed to rapidly generate valuable insights 
- [corollari/linusrants](https://github.com/corollari/linusrants) ★1863 [Python/-/180KB] Dataset of Linus Torvalds' rants classified by negativity using sentiment analys
- [RoboVerseOrg/RoboVerse](https://github.com/RoboVerseOrg/RoboVerse) ★1809 [Python/Apache-2.0/477MB] RoboVerse: Towards a Unified Platform, Dataset and Benchmark for Scalable and Ge
- [didi/ChineseNLP](https://github.com/didi/ChineseNLP) ★1805 [HTML/-/896KB] Datasets, SOTA results of every fields of Chinese NLP
- [Toyhom/Chinese-medical-dialogue-data](https://github.com/Toyhom/Chinese-medical-dialogue-data) ★1753 [Python/MIT/145MB] Chinese medical dialogue data 中文医疗对话数据集
- [juand-r/entity-recognition-datasets](https://github.com/juand-r/entity-recognition-datasets) ★1574 [Python/MIT/3MB] A collection of corpora for named entity recognition (NER) and entity recognitio
- [google-deepmind/rc-data](https://github.com/google-deepmind/rc-data) ★1296 [Python/Apache-2.0/1MB] Question answering dataset featured in "Teaching Machines to Read and Comprehend
- [huhusmang/Awesome-LLMs-for-Vulnerability-Detection](https://github.com/huhusmang/Awesome-LLMs-for-Vulnerability-Detection) ★1244 [Python/MIT/235KB] The community's most comprehensive, continuously-updated index of research on La
- [AtmaHou/Task-Oriented-Dialogue-Research-Progress-Survey](https://github.com/AtmaHou/Task-Oriented-Dialogue-Research-Progress-Survey) ★1238 [-/-/286KB] A datasets and methods survey about task-oriented dialogue, including recent dat
- [KaihuaTang/Scene-Graph-Benchmark.pytorch](https://github.com/KaihuaTang/Scene-Graph-Benchmark.pytorch) ★1195 [Jupyter Notebook/MIT/27MB] A new codebase for popular Scene Graph Generation methods (2020). Visualization 
- [xid32/SoundMind](https://github.com/xid32/SoundMind) ★1113 [Python/MIT/17MB] We introduce the Audio Logical Reasoning (ALR) dataset, consisting of 6,446 text
- [google-research-datasets/wit](https://github.com/google-research-datasets/wit) ★1113 [-/NOASSERTION/5MB] WIT (Wikipedia-based Image Text) Dataset is a large multimodal multilingual data
- [thuml/Large-Time-Series-Model](https://github.com/thuml/Large-Time-Series-Model) ★1007 [Python/MIT/22MB] Official code, datasets and checkpoints for "Timer: Generative Pre-trained Trans
- [pengxiao-song/awesome-chinese-legal-resources](https://github.com/pengxiao-song/awesome-chinese-legal-resources) ★996 [-/-/14KB] 📝 An Awesome Collection of Chinese Legal Dataset and Relevant Resources. 致力于收集全面
- [OpenLMLab/GAOKAO-Bench](https://github.com/OpenLMLab/GAOKAO-Bench) ★791 [Python/Apache-2.0/13MB] GAOKAO-Bench is an evaluation framework that utilizes GAOKAO questions as a data
- [mlfoundations/datacomp](https://github.com/mlfoundations/datacomp) ★787 [Python/NOASSERTION/3MB] DataComp: In search of the next generation of multimodal datasets
- [thu-coai/CrossWOZ](https://github.com/thu-coai/CrossWOZ) ★725 [Python/Apache-2.0/24MB] A Large-Scale Chinese Cross-Domain Task-Oriented Dialogue Dataset
- [domesticatedviking/TextyMcSpeechy](https://github.com/domesticatedviking/TextyMcSpeechy) ★700 [Shell/MIT/767KB] Easily create Piper text-to-speech models in any voice.  Make a text-to-speech m
- [dapurv5/awesome-question-answering](https://github.com/dapurv5/awesome-question-answering) ★686 [-/-/27KB] Resources, datasets, papers on Question Answering
- [ydli-ai/CSL](https://github.com/ydli-ai/CSL) ★674 [Python/-/4MB] [COLING 2022] CSL: A Large-scale Chinese Scientific Literature Dataset 中文科学文献数据集
- [JailbreakBench/jailbreakbench](https://github.com/JailbreakBench/jailbreakbench) ★656 [Python/MIT/3MB] JailbreakBench: An Open Robustness Benchmark for Jailbreaking Language Models [N
- [wenet-e2e/WenetSpeech](https://github.com/wenet-e2e/WenetSpeech) ★629 [Shell/Apache-2.0/4MB] A 10000+ hours dataset for Chinese speech recognition
- [google-research-datasets/dstc8-schema-guided-dialogue](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue) ★608 [Python/CC-BY-SA-4.0/50MB] The Schema-Guided Dialogue Dataset
- [deepfates/memery](https://github.com/deepfates/memery) ★575 [Python/MIT/306MB] Search over large image datasets with natural language and computer vision
- [rajpurkar/SQuAD-explorer](https://github.com/rajpurkar/SQuAD-explorer) ★569 [JavaScript/MIT/52MB] Visually Explore the Stanford Question Answering Dataset
- [facebookresearch/EmpatheticDialogues](https://github.com/facebookresearch/EmpatheticDialogues) ★557 [Python/NOASSERTION/38KB] Dialogue model that produces empathetic responses when trained on the Empathetic
- [google-deepmind/narrativeqa](https://github.com/google-deepmind/narrativeqa) ★517 [Shell/Apache-2.0/5MB] This repository contains the NarrativeQA dataset. It includes the list of docume
- [thu-coai/KdConv](https://github.com/thu-coai/KdConv) ★499 [Python/Apache-2.0/22MB] KdConv: A Chinese Multi-domain Dialogue Dataset Towards Multi-turn Knowledge-dri
- [Jiaaqiliu/Awesome-VLA-Robotics](https://github.com/Jiaaqiliu/Awesome-VLA-Robotics) ★490 [-/MIT/219KB] A comprehensive list of excellent research papers, models, datasets, and other r
- [ranchlai/mandarin-tts](https://github.com/ranchlai/mandarin-tts) ★477 [Python/-/87MB] Chinese Mandarin tts text-to-speech  中文 (普通话) 语音 合成 , by fastspeech 2 , implemen
- [abachaa/MedQuAD](https://github.com/abachaa/MedQuAD) ★462 [-/NOASSERTION/11MB] Medical Question Answering Dataset of 47,457 QA pairs created from 12 NIH websit
- [ad-freiburg/large-qa-datasets](https://github.com/ad-freiburg/large-qa-datasets) ★440 [-/-/21KB] A collection of large question answering datasets
- [pubmedqa/pubmedqa](https://github.com/pubmedqa/pubmedqa) ★438 [Python/MIT/704KB] PubMedQA: A Dataset for Biomedical Research Question Answering
- [Alibaba-NLP/OmniSearch](https://github.com/Alibaba-NLP/OmniSearch) ★431 [Python/-/18MB] Repo for Benchmarking Multimodal Retrieval Augmented Generation with Dynamic VQA
- [MRzzm/HDTF](https://github.com/MRzzm/HDTF) ★429 [Python/GPL-3.0/3MB] the dataset and code for "Flow-guided One-shot Talking Face Generation with a Hi
- [ibrahimethemhamamci/CT-CLIP](https://github.com/ibrahimethemhamamci/CT-CLIP) ★414 [Python/-/4MB] Developing Generalist Foundation Models from a Multimodal Dataset for 3D Compute
- [zhangsheng93/cMedQA2](https://github.com/zhangsheng93/cMedQA2) ★386 [-/GPL-3.0/88MB] This is updated version of the dataset for Chinese community medical question an
- [quincyliang/nlp-public-dataset](https://github.com/quincyliang/nlp-public-dataset) ★369 [Python/-/13MB] Chinese, English NER, English-Chinese machine translation dataset. 中英文实体识别数据集，中英
- [mmalekzadeh/motion-sense](https://github.com/mmalekzadeh/motion-sense) ★368 [Jupyter Notebook/MIT/202MB] MotionSense Dataset for Human Activity and Attribute Recognition ( time-series d
- [Meituan-Dianping/asap](https://github.com/Meituan-Dianping/asap) ★355 [-/Apache-2.0/40MB] ASAP: A Chinese Review Dataset Towards Aspect Category Sentiment Analysis and Ra
- [microsoft/MSMARCO-Passage-Ranking](https://github.com/microsoft/MSMARCO-Passage-Ranking) ★346 [Jupyter Notebook/MIT/8MB] MS MARCO(Microsoft Machine Reading Comprehension) is a large scale dataset focus
- [FreedomIntelligence/Huatuo-26M](https://github.com/FreedomIntelligence/Huatuo-26M) ★345 [-/-/687KB] The Largest-scale Chinese Medical QA Dataset： with 26,000,000 question answer pa
- [Nealcly/MuTual](https://github.com/Nealcly/MuTual) ★335 [Python/-/8MB] A Dataset for Multi-Turn Dialogue Reasoning
- [rom1504/cc2dataset](https://github.com/rom1504/cc2dataset) ★321 [Python/MIT/52KB] Easily convert common crawl to a dataset of caption and document. Image/text Aud
- [abachaa/Existing-Medical-QA-Datasets](https://github.com/abachaa/Existing-Medical-QA-Datasets) ★319 [-/-/27KB] Multimodal Question Answering in the Medical Domain: A summary of Existing Datas
- [google-research-datasets/tydiqa](https://github.com/google-research-datasets/tydiqa) ★319 [Python/Apache-2.0/6MB] TyDi QA contains 200k human-annotated question-answer pairs in 11 Typologically 
- [villmow/datasets_knowledge_embedding](https://github.com/villmow/datasets_knowledge_embedding) ★297 [-/MIT/125MB] Datasets for Knowledge Graph Completion with textual information about the entit
- [medmcqa/medmcqa](https://github.com/medmcqa/medmcqa) ★294 [Jupyter Notebook/MIT/671KB] A large-scale (194k), Multiple-Choice Question Answering (MCQA) dataset designed
- [scutcyr/CPED](https://github.com/scutcyr/CPED) ★292 [Python/Apache-2.0/6MB] CPED: A Large-Scale Chinese Personalized and Emotional Dialogue Dataset for Conv
- [westlake-repl/MicroLens](https://github.com/westlake-repl/MicroLens) ★292 [Python/-/64MB] A Large Short-video Recommendation Dataset with Raw Text/Audio/Image/Videos (Tal
- [wang-tf/Chinese_OCR_synthetic_data](https://github.com/wang-tf/Chinese_OCR_synthetic_data) ★271 [Python/-/234MB] The progress was used to generate synthetic dataset for Chinese OCR.
- [siat-nlp/MAMS-for-ABSA](https://github.com/siat-nlp/MAMS-for-ABSA) ★268 [Python/Apache-2.0/936KB] A Multi-Aspect Multi-Sentiment Dataset for aspect-based sentiment analysis.
- [ocatak/malware_api_class](https://github.com/ocatak/malware_api_class) ★262 [Python/MIT/17MB] Malware dataset for security researchers, data scientists. Public malware datase
- [keonlee9420/DailyTalk](https://github.com/keonlee9420/DailyTalk) ★260 [Python/MIT/105MB] Official repository of DailyTalk: Spoken Dialogue Dataset for Conversational Tex
- [mandeep147/Amazon-Product-Recommender-System](https://github.com/mandeep147/Amazon-Product-Recommender-System) ★254 [Jupyter Notebook/-/966KB] Sentiment analysis on Amazon Review Dataset available at http://snap.stanford.ed
- [yangheng95/ABSADatasets](https://github.com/yangheng95/ABSADatasets) ★245 [HTML/MIT/91MB] Public & Community-shared datasets for Aspect-based sentiment analysis and Text 
- [skywalker023/sodaverse](https://github.com/skywalker023/sodaverse) ★244 [Python/MIT/1MB] 🥤🧑🏻‍🚀Code and dataset for our EMNLP 2023 paper - "SODA: Million-scale Dialogue D
- [openforcefield/protein-ligand-benchmark](https://github.com/openforcefield/protein-ligand-benchmark) ★241 [Python/MIT/310MB] Protein-Ligand Benchmark Dataset for Free Energy Calculations
- [z17176/Chinese_conversation_sentiment](https://github.com/z17176/Chinese_conversation_sentiment) ★233 [-/-/861KB] A Chinese sentiment dataset may be useful for sentiment analysis.
- [AlexanderVNikitin/tsgm](https://github.com/AlexanderVNikitin/tsgm) ★225 [Python/Apache-2.0/9MB] Generation and evaluation of synthetic time series datasets (also, augmentations
- [YouTaoBaBa/Chinese-Dialogue-Dataset](https://github.com/YouTaoBaBa/Chinese-Dialogue-Dataset) ★218 [-/-/9KB] 用于汇总目前的开源中文对话数据集
- [piyushpathak03/Recommendation-systems](https://github.com/piyushpathak03/Recommendation-systems) ★217 [Jupyter Notebook/GPL-3.0/7MB] Recommendation Systems This is a workshop on using Machine Learning and Deep Lea
- [docugami/KG-RAG-datasets](https://github.com/docugami/KG-RAG-datasets) ★214 [Jupyter Notebook/MIT/57MB] Knowledge Graph Retrieval Augmented Generation (KG-RAG) Eval Datasets
- [victorsungo/MMDialog](https://github.com/victorsungo/MMDialog) ★204 [Python/-/3MB] The official site of paper MMDialog: A Large-scale Multi-turn Dialogue Dataset T
- [Alibaba-NLP/Multi-CPR](https://github.com/Alibaba-NLP/Multi-CPR) ★204 [Python/-/240MB] [SIGIR 2022] Multi-CPR: A Multi Domain Chinese Dataset for Passage Retrieval

### cv.计算机视觉/图像（70 个）

- [pytorch/vision](https://github.com/pytorch/vision) ★17873 [Python/BSD-3-Clause/1.2GB] Datasets, Transforms and Models specific to Computer Vision
- [cvat-ai/cvat](https://github.com/cvat-ai/cvat) ★16568 [Python/MIT/371MB] Computer Vision Annotation Tool (CVAT) is a leading platform for building high-q
- [lukas-blecher/LaTeX-OCR](https://github.com/lukas-blecher/LaTeX-OCR) ★16544 [Python/MIT/9MB] pix2tex: Using a ViT to convert images of equations into LaTeX code.
- [zalandoresearch/fashion-mnist](https://github.com/zalandoresearch/fashion-mnist) ★12808 [Python/MIT/106MB] A MNIST-like fashion product database. Benchmark :point_down: 
- [satellite-image-deep-learning/techniques](https://github.com/satellite-image-deep-learning/techniques) ★10234 [-/Apache-2.0/30MB] Techniques for deep learning with satellite & aerial imagery
- [rom1504/img2dataset](https://github.com/rom1504/img2dataset) ★4442 [Python/MIT/4MB] Easily turn large sets of image urls to an image dataset. Can download, resize a
- [openimages/dataset](https://github.com/openimages/dataset) ★4376 [Python/Apache-2.0/3MB] The Open Images dataset
- [Yochengliu/awesome-point-cloud-analysis](https://github.com/Yochengliu/awesome-point-cloud-analysis) ★4218 [-/-/289KB] A list of papers and datasets about point cloud analysis (processing)
- [Charmve/Surface-Defect-Detection](https://github.com/Charmve/Surface-Defect-Detection) ★4099 [Python/MIT/229MB] 📈 目前最大的工业缺陷检测数据库及论文集 Constantly summarizing open source dataset and critical pap
- [M-3LAB/awesome-industrial-anomaly-detection](https://github.com/M-3LAB/awesome-industrial-anomaly-detection) ★3744 [-/-/6MB] Paper list and datasets for industrial image anomaly/defect detection (updating)
- [uzh-rpg/event-based_vision_resources](https://github.com/uzh-rpg/event-based_vision_resources) ★3629 [-/-/2MB] Event-based Vision Resources. Community effort to collect knowledge on event-bas
- [linhandev/dataset](https://github.com/linhandev/dataset) ★3605 [-/-/16MB] 医学影像数据集列表 『An Index for Medical Imaging Datasets』
- [ieee8023/covid-chestxray-dataset](https://github.com/ieee8023/covid-chestxray-dataset) ★3062 [Jupyter Notebook/-/633MB] We are building an open database of COVID-19 cases with chest X-ray or CT images
- [microsoft/table-transformer](https://github.com/microsoft/table-transformer) ★2938 [Python/MIT/333KB] Table Transformer (TATR) is a deep learning model for extracting tables from uns
- [facebookresearch/audio2photoreal](https://github.com/facebookresearch/audio2photoreal) ★2850 [Python/NOASSERTION/64MB] Code and dataset for photorealistic Codec Avatars driven from audio
- [unsplash/datasets](https://github.com/unsplash/datasets) ★2777 [Jupyter Notebook/-/93KB] 🎁  7,400,000+ Unsplash images made available for research and machine learning
- [sfikas/medical-imaging-datasets](https://github.com/sfikas/medical-imaging-datasets) ★2566 [-/-/47KB] A list of Medical imaging datasets.
- [abhineet123/Deep-Learning-for-Tracking-and-Detection](https://github.com/abhineet123/Deep-Learning-for-Tracking-and-Detection) ★2511 [HTML/-/1.9GB] Collection of papers, datasets, code and other resources for object tracking and
- [VisDrone/VisDrone-Dataset](https://github.com/VisDrone/VisDrone-Dataset) ★2508 [-/-/39KB] The dataset for drone based detection and tracking is released, including both i
- [google-research-datasets/Objectron](https://github.com/google-research-datasets/Objectron) ★2348 [Jupyter Notebook/NOASSERTION/40MB] Objectron is a dataset of short, object-centric video clips. In addition, the vi
- [wenhwu/awesome-remote-sensing-change-detection](https://github.com/wenhwu/awesome-remote-sensing-change-detection) ★2305 [-/-/1MB] A comprehensive and up-to-date compilation of datasets, tools, methods, review p
- [justmarkham/pandas-videos](https://github.com/justmarkham/pandas-videos) ★2251 [Jupyter Notebook/-/2MB] Jupyter notebook and datasets from the pandas video series
- [Niraj-Lunavat/Artificial-Intelligence](https://github.com/Niraj-Lunavat/Artificial-Intelligence) ★1857 [-/-/213MB] Awesome AI Learning with +100 AI Cheat-Sheets, Free online Books, Top Courses, B
- [google-deepmind/kinetics-i3d](https://github.com/google-deepmind/kinetics-i3d) ★1838 [Python/Apache-2.0/397MB] Convolutional neural network model for video classification trained on the Kinet
- [coderonion/awesome-yolo-object-detection](https://github.com/coderonion/awesome-yolo-object-detection) ★1783 [-/-/398KB] 🚀🚀🚀 A collection of some awesome public YOLO object detection series projects an
- [xiaobai1217/Awesome-Video-Datasets](https://github.com/xiaobai1217/Awesome-Video-Datasets) ★1659 [-/-/377KB] Video datasets
- [sudharsan13296/Awesome-Meta-Learning](https://github.com/sudharsan13296/Awesome-Meta-Learning) ★1554 [-/-/108KB]  A curated list of Meta Learning papers, code, books, blogs, videos, datasets an
- [facebookresearch/fastMRI](https://github.com/facebookresearch/fastMRI) ★1534 [Python/MIT/1MB] A large-scale dataset of both raw MRI measurements and clinical MRI images.
- [qfgaohao/pytorch-ssd](https://github.com/qfgaohao/pytorch-ssd) ★1430 [Python/MIT/1MB] MobileNetV1, MobileNetV2, VGG based SSD/SSD-lite implementation in Pytorch 1.0 /
- [MedMNIST/MedMNIST](https://github.com/MedMNIST/MedMNIST) ★1395 [Python/Apache-2.0/14MB] [pip install medmnist] 18x Standardized Datasets for 2D and 3D Biomedical Image 
- [streamlit/demo-self-driving](https://github.com/streamlit/demo-self-driving) ★1290 [Python/Apache-2.0/14MB] Streamlit app demonstrating an image browser for the Udacity self-driving-car da
- [dxli94/WLASL](https://github.com/dxli94/WLASL) ★1256 [Python/-/4MB] WACV 2020 "Word-level Deep Sign Language Recognition from Video: A New Large-sca
- [campusx-official/ML-Roadmap-for-2022](https://github.com/campusx-official/ML-Roadmap-for-2022) ★1223 [-/-/45KB] A curated list of Machine learning videos, links, projects and datasets to help 
- [cleanlab/cleanvision](https://github.com/cleanlab/cleanvision) ★1197 [Python/Apache-2.0/2MB] Automatically find issues in image datasets and practice data-centric computer v
- [declare-lab/MELD](https://github.com/declare-lab/MELD) ★1079 [Python/GPL-3.0/8MB] MELD: A Multimodal Multi-Party Dataset for Emotion Recognition in Conversation
- [unrealcv/synthetic-computer-vision](https://github.com/unrealcv/synthetic-computer-vision) ★1025 [Python/MIT/135KB] A list of synthetic dataset and tools for computer vision
- [modenaxe/awesome-biomechanics](https://github.com/modenaxe/awesome-biomechanics) ★1006 [-/-/2MB] A curated, public list of resources for biomechanics and human motion analysis: 
- [RuihengZhang/IFSOD-dataset](https://github.com/RuihengZhang/IFSOD-dataset) ★1005 [-/-/4MB] Dataset approched by A Benchmark and Frequency Compression Method for Infrared F
- [WenmuZhou/OCR_DataSet](https://github.com/WenmuZhou/OCR_DataSet) ★969 [Python/-/9MB] 收集并整理有关OCR的数据集并统一标注格式，以便实验需要
- [mlfoundations/MINT-1T](https://github.com/mlfoundations/MINT-1T) ★832 [-/-/23MB] 🍃 MINT-1T: A one trillion token multimodal interleaved dataset.
- [zcablii/SARDet_100K](https://github.com/zcablii/SARDet_100K) ★779 [Python/NOASSERTION/2MB]  [NeurIPS 2024 spotlight] Offical implementation of MSFA and release of SARDet_1
- [yeephycho/tensorflow-face-detection](https://github.com/yeephycho/tensorflow-face-detection) ★772 [Python/Apache-2.0/20MB] A mobilenet SSD based face detector, powered by tensorflow object detection api,
- [yuanmaoxun/Awesome-RGBT-Fusion](https://github.com/yuanmaoxun/Awesome-RGBT-Fusion) ★745 [-/-/100KB] A collection of deep learning based RGB-T-Fusion methods, codes, and datasets. T
- [vvincenttttt/Awesome-3D-Object-Detection](https://github.com/vvincenttttt/Awesome-3D-Object-Detection) ★692 [-/-/2MB] Papers, code and datasets about deep learning for 3D Object Detection.
- [open-edge-platform/datumaro](https://github.com/open-edge-platform/datumaro) ★685 [Python/MIT/371MB] Dataset Management Framework, a Python library and a CLI tool to build, analyze 
- [Jakobovski/free-spoken-digit-dataset](https://github.com/Jakobovski/free-spoken-digit-dataset) ★678 [Python/-/30MB] A free audio dataset of spoken digits. An audio version of MNIST.
- [yumingj/DeepFashion-MultiModal](https://github.com/yumingj/DeepFashion-MultiModal) ★663 [-/NOASSERTION/14MB] A large-scale high-quality human dataset with rich multi-modal annotations
- [roboflow/roboflow-python](https://github.com/roboflow/roboflow-python) ★624 [Python/Apache-2.0/14MB] The official Roboflow Python package. Manage your datasets, models, and deployme
- [jasonmanesis/Satellite-Imagery-Datasets-Containing-Ships](https://github.com/jasonmanesis/Satellite-Imagery-Datasets-Containing-Ships) ★604 [-/MIT/423KB] This repository provides a comprehensive list of radar and optical satellite dat
- [remyxai/VQASynth](https://github.com/remyxai/VQASynth) ★587 [Python/Apache-2.0/18MB] Compose multimodal datasets 🎹
- [CheyneyComputerScience/CREMA-D](https://github.com/CheyneyComputerScience/CREMA-D) ★547 [R/NOASSERTION/15MB] Crowd Sourced Emotional Multimodal Actors Dataset (CREMA-D)
- [Mohamedelrefaie/DrivAerNet](https://github.com/Mohamedelrefaie/DrivAerNet) ★540 [Python/NOASSERTION/1018KB] A Large-Scale Multimodal Car Dataset with Computational Fluid Dynamics Simulatio
- [xingyizhou/UniDet](https://github.com/xingyizhou/UniDet) ★517 [Python/-/9MB] Object detection on multiple datasets with an automatically learned unified labe
- [mint-lab/awesome-robotics-datasets](https://github.com/mint-lab/awesome-robotics-datasets) ★516 [-/-/13KB] A collection of useful datasets for robotics and computer vision
- [MultimodalUniverse/MultimodalUniverse](https://github.com/MultimodalUniverse/MultimodalUniverse) ★505 [Jupyter Notebook/MIT/167MB] Large-Scale Multimodal Dataset of Astronomical Data
- [clovaai/cord](https://github.com/clovaai/cord) ★488 [-/CC-BY-4.0/711KB] CORD: A Consolidated Receipt Dataset for Post-OCR Parsing
- [DLLXW/objectDetectionDatasets](https://github.com/DLLXW/objectDetectionDatasets) ★476 [Python/-/1MB] 目标检测数据集制作:VOC,COCO,YOLO等常用数据集格式的制作和互相转换脚本
- [F2Wang/ObjectDatasetTools](https://github.com/F2Wang/ObjectDatasetTools) ★450 [Python/MIT/9MB] Tools to create pixel-wise object masks, bounding box labels (2D and 3D) and 3D 
- [Demfier/multimodal-speech-emotion-recognition](https://github.com/Demfier/multimodal-speech-emotion-recognition) ★450 [Jupyter Notebook/MIT/12MB] Lightweight and Interpretable ML Model for Speech Emotion Recognition and Ambigu
- [mala-lab/ADBenchmarks-anomaly-detection-datasets](https://github.com/mala-lab/ADBenchmarks-anomaly-detection-datasets) ★447 [-/GPL-3.0/41MB] ADRepository: Real-world anomaly detection datasets, including tabular data (cat
- [ZumingHuang/awesome-ocr-resources](https://github.com/ZumingHuang/awesome-ocr-resources) ★437 [Python/MIT/11MB] A collection of resources (including the papers and datasets) of OCR (Optical Ch
- [witnessai/Awesome-Open-Vocabulary-Object-Detection](https://github.com/witnessai/Awesome-Open-Vocabulary-Object-Detection) ★423 [-/-/23KB] A curated list of papers, datasets and resources pertaining to open vocabulary o
- [UCSC-VLAA/MedTrinity-25M](https://github.com/UCSC-VLAA/MedTrinity-25M) ★410 [Python/-/1MB] [ICLR 2025] This is the official repository of our paper "MedTrinity-25M: A Larg
- [abin24/Surface-Inspection-defect-detection-dataset](https://github.com/abin24/Surface-Inspection-defect-detection-dataset) ★399 [-/-/20MB] This project include several different surfaces, each surface contains one or se
- [ZihengZZH/awesome-multimodal-knowledge-graph](https://github.com/ZihengZZH/awesome-multimodal-knowledge-graph) ★397 [TeX/MIT/422MB] A curated list of AWESOME papers, datasets and tutorials within Multimodal Knowl
- [fanq15/Few-Shot-Object-Detection-Dataset](https://github.com/fanq15/Few-Shot-Object-Detection-Dataset) ★394 [-/-/3MB] 
- [uni-medical/STU-Net](https://github.com/uni-medical/STU-Net) ★373 [Python/Apache-2.0/45MB] The largest pre-trained medical image segmentation model (1.4B parameters) based
- [Fang-Haoshu/Halpe-FullBody](https://github.com/Fang-Haoshu/Halpe-FullBody) ★372 [Jupyter Notebook/-/9MB] Halpe: full body human pose estimation and human-object interaction detection da
- [corentin-dfg/Satellite-Image-Time-Series-Datasets](https://github.com/corentin-dfg/Satellite-Image-Time-Series-Datasets) ★321 [-/-/119KB] This page presents a list of satellite imagery datasets with a temporal dimensio
- [Deci-AI/data-gradients](https://github.com/Deci-AI/data-gradients) ★312 [Python/Apache-2.0/30MB] Computer Vision dataset analysis

### audio.音频/语音（24 个）

- [RedditSota/state-of-the-art-result-for-machine-learning-problems](https://github.com/RedditSota/state-of-the-art-result-for-machine-learning-problems) ★8894 [-/Apache-2.0/151KB] This repository provides state of the art (SoTA) results for all machine learnin
- [jim-schwoebel/voice_datasets](https://github.com/jim-schwoebel/voice_datasets) ★2221 [-/-/139KB] 🔊 A comprehensive list of open-source datasets for voice and sound computing (95
- [uber/petastorm](https://github.com/uber/petastorm) ★1891 [Python/Apache-2.0/3MB] Petastorm library enables single machine or distributed training and evaluation 
- [zwang4/awesome-machine-learning-in-compilers](https://github.com/zwang4/awesome-machine-learning-in-compilers) ★1686 [-/CC0-1.0/593KB] Must read research papers and links to tools and datasets that are related to us
- [krantiparida/awesome-audio-visual](https://github.com/krantiparida/awesome-audio-visual) ★777 [-/-/60KB] A curated list of different papers and datasets in various areas of audio-visual
- [LAION-AI/audio-dataset](https://github.com/LAION-AI/audio-dataset) ★749 [Python/-/84MB] Audio Dataset for training CLAP and other models
- [SpeechColab/GigaSpeech](https://github.com/SpeechColab/GigaSpeech) ★730 [Shell/Apache-2.0/229KB] Large, modern dataset for speech recognition
- [tbertinmahieux/MSongsDB](https://github.com/tbertinmahieux/MSongsDB) ★695 [Python/NOASSERTION/30MB] Code for the Million Song Dataset, the dataset contains metadata and audio analy
- [microsoft/MS-SNSD](https://github.com/microsoft/MS-SNSD) ★600 [HTML/MIT/3.9GB] The Microsoft Scalable Noisy Speech Dataset (MS-SNSD) is a noisy speech dataset 
- [facebookresearch/libri-light](https://github.com/facebookresearch/libri-light) ★523 [Python/MIT/373KB] dataset for lightly supervised training using the librivox audio book recordings
- [Kyubyong/css10](https://github.com/Kyubyong/css10) ★491 [HTML/Apache-2.0/183MB] CSS10: A Collection of Single Speaker Speech Datasets for 10 Languages
- [gemengtju/Tutorial_Separation](https://github.com/gemengtju/Tutorial_Separation) ★485 [MATLAB/-/76MB] This repo summarizes the tutorials, datasets, papers, codes and tools for speech
- [double22a/speech_dataset](https://github.com/double22a/speech_dataset) ★468 [-/Apache-2.0/81KB] The dataset of Speech Recognition
- [marcogdepinto/emotion-classification-from-audio-files](https://github.com/marcogdepinto/emotion-classification-from-audio-files) ★431 [Python/GPL-3.0/661MB] Understanding emotions from audio files using neural networks and multiple datas
- [SuperKogito/SER-datasets](https://github.com/SuperKogito/SER-datasets) ★420 [HTML/MIT/4MB] A collection of datasets for the purpose of emotion recognition/detection in spe
- [kocohub/korean-hate-speech](https://github.com/kocohub/korean-hate-speech) ★398 [-/CC-BY-SA-4.0/93MB] Korean HateSpeech Dataset
- [KrishnaswamyLab/MAGIC](https://github.com/KrishnaswamyLab/MAGIC) ★388 [Jupyter Notebook/GPL-2.0/222MB] MAGIC (Markov Affinity-based Graph Imputation of Cells), is a method for imputin
- [gabolsgabs/DALI](https://github.com/gabolsgabs/DALI) ★381 [Python/NOASSERTION/32MB]  DALI: a large Dataset of synchronised Audio, LyrIcs and vocal notes.
- [hche11/VGGSound](https://github.com/hche11/VGGSound) ★358 [Python/NOASSERTION/6MB] VGGSound: A Large-scale Audio-Visual Dataset
- [hyp1231/AmazonReviews2023](https://github.com/hyp1231/AmazonReviews2023) ★295 [Python/MIT/340KB] Scripts for processing the Amazon Reviews 2023 dataset; implementations and chec
- [shsarv/Data-Analytics-Projects-in-python](https://github.com/shsarv/Data-Analytics-Projects-in-python) ★244 [Jupyter Notebook/MIT/6MB] A collection of data analysis and visualization projects designed to uncover ins
- [WenjieDu/TSDB](https://github.com/WenjieDu/TSDB) ★239 [Python/BSD-3-Clause/308KB] a Python toolbox loads 173 public time series datasets for machine/deep learning
- [lbdeoliveira/song-playlist-recommendation](https://github.com/lbdeoliveira/song-playlist-recommendation) ★217 [HTML/-/230KB] This project was a joint effort by Lucas De Oliveira, Chandrish Ambati, and Anis
- [fuhailin/Probabilistic-Matrix-Factorization](https://github.com/fuhailin/Probabilistic-Matrix-Factorization) ★178 [Python/Apache-2.0/14MB] Python Implementation of Probabilistic Matrix Factorization(PMF) Algorithm for b

### science.科学计算（11 个）

- [PolymathicAI/the_well](https://github.com/PolymathicAI/the_well) ★4383 [Jupyter Notebook/BSD-3-Clause/659MB] A 15TB Collection of Physics Simulation Datasets
- [ai4s-research/awesome-ai-for-science](https://github.com/ai4s-research/awesome-ai-for-science) ★1893 [-/MIT/1MB] A curated list of awesome AI tools, libraries, papers, datasets, and frameworks 
- [hendrycks/math](https://github.com/hendrycks/math) ★1384 [Python/MIT/17MB] The MATH Dataset (NeurIPS 2021)
- [TimoBolkart/FLAME-Universe](https://github.com/TimoBolkart/FLAME-Universe) ★696 [-/-/6MB] Summary of publicly available ressources such as code, datasets, and scientific 
- [OpenGeoscience/geojs](https://github.com/OpenGeoscience/geojs) ★470 [JavaScript/Apache-2.0/109MB] High-performance visualization and interactive data exploration of scientific an
- [kjappelbaum/awesome-chemistry-datasets](https://github.com/kjappelbaum/awesome-chemistry-datasets) ★419 [-/CC0-1.0/42KB] overview of datasets for ML in chemistry
- [jonathanking/sidechainnet](https://github.com/jonathanking/sidechainnet) ★366 [Python/BSD-3-Clause/57MB] An all-atom protein structure dataset for machine learning.
- [mochilang/mochi](https://github.com/mochilang/mochi) ★336 [Scheme/MIT/185MB] Mochi is a small, fast, embeddable programming language designed for agents, dat
- [plinder-org/plinder](https://github.com/plinder-org/plinder) ★305 [Python/GPL-2.0/51MB] Protein Ligand INteraction Dataset and Evaluation Resource
- [zwhe99/DeepMath](https://github.com/zwhe99/DeepMath) ★301 [Python/MIT/24MB] A Large-Scale, Challenging, Decontaminated, and Verifiable Mathematical Dataset 
- [a-r-j/ProteinWorkshop](https://github.com/a-r-j/ProteinWorkshop) ★277 [Python/MIT/22MB] Benchmarking framework for protein representation learning. Includes a large num

### medical.医疗健康（10 个）

- [openmedlab/Awesome-Medical-Dataset](https://github.com/openmedlab/Awesome-Medical-Dataset) ★2093 [-/-/223MB] Collection of awesome medical dataset resources.
- [antontarasenko/smq](https://github.com/antontarasenko/smq) ★1538 [TSQL/Apache-2.0/120KB] A collection of SQL queries to social media datasets.
- [adalca/medical-datasets](https://github.com/adalca/medical-datasets) ★923 [-/-/70KB] tracking medical datasets, with a focus on medical imaging
- [YerevaNN/mimic3-benchmarks](https://github.com/YerevaNN/mimic3-benchmarks) ★890 [Python/MIT/17MB] Python suite to construct benchmark machine learning datasets from the MIMIC-III
- [uni-medical/Project-Imaging-X](https://github.com/uni-medical/Project-Imaging-X) ★477 [Python/MIT/60MB] Project Imaging-X: A Survey of 1000+ Open-Access Medical Imaging Datasets for Fo
- [vinbigdata-medical/vindr-lab](https://github.com/vinbigdata-medical/vindr-lab) ★377 [-/MIT/12MB] A Data Platform for Medical AI that enables building high-quality datasets and a
- [medtorch/awesome-healthcare-ai](https://github.com/medtorch/awesome-healthcare-ai) ★354 [-/CC0-1.0/68KB] A curated list of awesome open source healthcare tools, algorithms, datasets and
- [AstraZeneca/awesome-drug-discovery-knowledge-graphs](https://github.com/AstraZeneca/awesome-drug-discovery-knowledge-graphs) ★266 [-/Apache-2.0/429KB] A collection of research papers, datasets and software related to knowledge grap
- [xiangyue9607/BioNEV](https://github.com/xiangyue9607/BioNEV) ★231 [Python/MIT/28MB] Graph Embedding Evaluation / Code and Datasets for  "Graph Embedding on Biomedic
- [rexrodeo/american-healthcare-conundrum](https://github.com/rexrodeo/american-healthcare-conundrum) ★230 [Python/MIT/18MB] Investigative data journalism: quantifying fixable waste in US healthcare, one i

### timeseries.时序/金融（13 个）

- [Jon-Becker/prediction-market-analysis](https://github.com/Jon-Becker/prediction-market-analysis) ★3766 [Python/MIT/158MB] A framework for collecting and analyzing prediction market data, including the l
- [rob-med/awesome-TS-anomaly-detection](https://github.com/rob-med/awesome-TS-anomaly-detection) ★3161 [-/-/144KB] List of tools & datasets for anomaly detection on time-series data.
- [financial-datasets/mcp-server](https://github.com/financial-datasets/mcp-server) ★2281 [Python/MIT/23KB] An MCP server for interacting with the Financial Datasets stock market API.
- [thuml/OpenLTM](https://github.com/thuml/OpenLTM) ★550 [Jupyter Notebook/MIT/3MB] Implementations, Pre-training Code and Datasets of Large Time-Series Models
- [GoogleCloudPlatform/covid-19-open-data](https://github.com/GoogleCloudPlatform/covid-19-open-data) ★488 [Python/Apache-2.0/10MB] Datasets of daily time-series data related to COVID-19 for over 20,000 distinct 
- [Zdong104/FNSPID_Financial_News_Dataset](https://github.com/Zdong104/FNSPID_Financial_News_Dataset) ★456 [Python/NOASSERTION/106MB] FNSPID: A Comprehensive Financial News Dataset in Time Series
- [XiaoxiaoMa-MQ/Awesome-Deep-Graph-Anomaly-Detection](https://github.com/XiaoxiaoMa-MQ/Awesome-Deep-Graph-Anomaly-Detection) ★384 [-/MIT/16MB] Awesome graph anomaly detection techniques built based on deep learning framewor
- [woshijielie/stock_prediction_and_recommendation](https://github.com/woshijielie/stock_prediction_and_recommendation) ★366 [Jupyter Notebook/-/34MB] A comprehensive React-based stock market analysis dashboard that enables users t
- [thedatumorg/TSB-AD](https://github.com/thedatumorg/TSB-AD) ★319 [Python/Apache-2.0/15MB] Time-Series Anomaly Detection | Algorithms + Datasets + Tutorials
- [rakshitha123/TSForecasting](https://github.com/rakshitha123/TSForecasting) ★242 [R/NOASSERTION/304KB] This repository contains the implementations related to the experiments of a set
- [wangtz19/Awesome-NTA](https://github.com/wangtz19/Awesome-NTA) ★196 [-/CC0-1.0/1MB] A curation of awesome papers, datasets and tools about network traffic analysis.
- [dineshresearch/Novel-Deep-Learning-Model-for-Traffic-Sign-Detection-Using-Capsule-Networks](https://github.com/dineshresearch/Novel-Deep-Learning-Model-for-Traffic-Sign-Detection-Using-Capsule-Networks) ★126 [Jupyter Notebook/MIT/5MB] capsule networks that achieves outstanding performance on the German traffic sig
- [AbertayMachineLearningGroup/network-threats-taxonomy](https://github.com/AbertayMachineLearningGroup/network-threats-taxonomy) ★104 [TeX/GPL-3.0/885KB] Machine Learning based Intrusion Detection Systems are difficult to evaluate due

### graph.图/推荐（17 个）

- [philackm/ScrollableGraphView](https://github.com/philackm/ScrollableGraphView) ★5284 [Swift/MIT/25MB] An adaptive scrollable graph view for iOS to visualise simple discrete datasets.
- [snap-stanford/ogb](https://github.com/snap-stanford/ogb) ★2092 [Python/MIT/4MB] Benchmark datasets, data loaders, and evaluators for graph machine learning
- [RUCAIBox/RecSysDatasets](https://github.com/RUCAIBox/RecSysDatasets) ★1257 [Python/-/430KB] This is a repository of public data sources for Recommender Systems (RS).
- [caserec/Datasets-for-Recommender-Systems](https://github.com/caserec/Datasets-for-Recommender-Systems) ★1105 [Jupyter Notebook/-/74MB] This is a repository of a topic-centric public data sources in high quality for 
- [yueliu1999/Awesome-Deep-Graph-Clustering](https://github.com/yueliu1999/Awesome-Deep-Graph-Clustering) ★1016 [Python/MIT/672KB] [IEEE T-KDE 2026] Awesome Deep Graph Clustering is a collection of SOTA, novel d
- [CRIPAC-DIG/SR-GNN](https://github.com/CRIPAC-DIG/SR-GNN) ★853 [Python/-/130KB] [AAAI 2019] Source code and datasets for "Session-based Recommendation with Grap
- [futuredapp/donut](https://github.com/futuredapp/donut) ★551 [Kotlin/MIT/940KB] Doughnut-like graph view capable of displaying multiple datasets with assignable
- [PrincetonLIPS/SketchGraphs](https://github.com/PrincetonLIPS/SketchGraphs) ★479 [Python/MIT/11MB] A dataset of 15 million CAD sketches with geometric constraint graphs.
- [THUDM/CogQA](https://github.com/THUDM/CogQA) ★457 [Python/MIT/36MB] Source code and dataset for ACL 2019 paper "Cognitive Graph for Multi-Hop Readin
- [khanhnamle1994/movielens](https://github.com/khanhnamle1994/movielens) ★451 [Jupyter Notebook/MIT/43MB] 4 different recommendation engines for the MovieLens dataset.
- [HCIILAB/Scene-Text-Recognition-Recommendations](https://github.com/HCIILAB/Scene-Text-Recognition-Recommendations) ★354 [Python/MIT/1MB] Papers, Datasets, Algorithms, SOTA for STR. Long-time Maintaining
- [librahu/HIN-Datasets-for-Recommendation-and-Network-Embedding](https://github.com/librahu/HIN-Datasets-for-Recommendation-and-Network-Embedding) ★352 [-/-/25MB] Heterogeneous Information Network Datasets for Recommendation and Network Embedd
- [easezyc/Multitask-Recommendation-Library](https://github.com/easezyc/Multitask-Recommendation-Library) ★348 [Python/MIT/53KB] MTReclib provides a PyTorch implementation of multi-task recommendation models a
- [THUDM/ComiRec](https://github.com/THUDM/ComiRec) ★310 [Python/-/23KB] Source code and dataset for KDD 2020 paper "Controllable Multi-Interest Framewor
- [TrustAGI-Lab/graph_datasets](https://github.com/TrustAGI-Lab/graph_datasets) ★300 [-/-/41MB] A Repository of Benchmark Graph Datasets for Graph Classification (31 Graph Data
- [guocheng2025/Sequential-Recommendation-Datasets](https://github.com/guocheng2025/Sequential-Recommendation-Datasets) ★228 [Python/Apache-2.0/190KB] Download and preprocess popular sequential recommendation datasets
- [SCUT-DLVCLab/Document-AI-Recommendations](https://github.com/SCUT-DLVCLab/Document-AI-Recommendations) ★210 [-/-/7MB] Algorithms, papers, datasets, performance comparisons for Document AI.

### web.Web/网页（2 个）

- [NaiboWang/EasySpider](https://github.com/NaiboWang/EasySpider) ★44398 [JavaScript/AGPL-3.0/149MB] A visual no-code/code-free web crawler/spider易采集：一个可视化浏览器自动化测试/数据采集/网页爬虫软件，可以无代码
- [mdn/browser-compat-data](https://github.com/mdn/browser-compat-data) ★5723 [JSON/CC0-1.0/121MB] Browser compatibility data for Web technologies as displayed on MDN

### code.代码（3 个）

- [minar09/awesome-virtual-try-on](https://github.com/minar09/awesome-virtual-try-on) ★3157 [-/-/306KB] A curated list of awesome research papers, projects, code, dataset, workshops et
- [github/CodeSearchNet](https://github.com/github/CodeSearchNet) ★2442 [Jupyter Notebook/MIT/29MB] Datasets, tools, and benchmarks for representation learning of code.
- [ENSTA-U2IS-AI/awesome-uncertainty-deeplearning](https://github.com/ENSTA-U2IS-AI/awesome-uncertainty-deeplearning) ★823 [-/MIT/456KB] This repository contains a collection of surveys, datasets,  papers, and codes, 

### general.通用聚合（43 个）

- [public-apis/public-apis](https://github.com/public-apis/public-apis) ★468180 [Python/MIT/8MB] A collective list of free APIs
- [awesomedata/awesome-public-datasets](https://github.com/awesomedata/awesome-public-datasets) ★78416 [-/MIT/1MB] A topic-centric list of HQ open datasets.
- [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) ★61654 [Python/GPL-3.0/32MB] ⭐AI-driven public opinion & trend monitor with multi-platform aggregation, RSS, 
- [HumanSignal/label-studio](https://github.com/HumanSignal/label-studio) ★28106 [TypeScript/Apache-2.0/2.8GB] Label Studio is a multi-type data labeling and annotation tool with standardized
- [dianping/cat](https://github.com/dianping/cat) ★18943 [Java/Apache-2.0/111MB] CAT 作为服务端项目基础组件，提供了 Java, C/C++, Node.js, Python, Go 等多语言客户端，已经在美团点评的基础架构中间件框架（M
- [alibaba/DataX](https://github.com/alibaba/DataX) ★17327 [Java/NOASSERTION/22MB] DataX是阿里云DataWorks数据集成的开源版本。
- [JoeanAmier/TikTokDownloader](https://github.com/JoeanAmier/TikTokDownloader) ★15500 [Python/GPL-3.0/27MB] 抖音 / TikTok 平台作品下载/数据采集工具
- [NVIDIA/cosmos](https://github.com/NVIDIA/cosmos) ★11584 [Jupyter Notebook/NOASSERTION/257MB] NVIDIA Cosmos is an open platform of world models, datasets, and tools that enab
- [apachecn/apachecn-algo-zh](https://github.com/apachecn/apachecn-algo-zh) ★11147 [JavaScript/-/1MB] ApacheCN 数据结构与算法译文集
- [fengdu78/Data-Science-Notes](https://github.com/fengdu78/Data-Science-Notes) ★8579 [Jupyter Notebook/-/51MB] 数据科学的笔记以及资料搜集
- [kangvcar/InfoSpider](https://github.com/kangvcar/InfoSpider) ★8244 [Python/GPL-3.0/41MB] INFO-SPIDER 是一个集众多数据源于一身的爬虫工具箱🧰，旨在安全快捷的帮助用户拿回自己的数据，工具代码开源，流程透明。支持数据源包括GitHub、QQ邮
- [openlm-research/open_llama](https://github.com/openlm-research/open_llama) ★7527 [-/Apache-2.0/2MB] OpenLLaMA, a permissively licensed open source reproduction of Meta AI’s LLaMA 7
- [cv-cat/Spider_XHS](https://github.com/cv-cat/Spider_XHS) ★7374 [Python/-/18MB] 小红书爬虫数据采集，小红书全域运营解决方案
- [PAIR-code/facets](https://github.com/PAIR-code/facets) ★7337 [Jupyter Notebook/Apache-2.0/23MB] Visualizations for machine learning datasets
- [luyishisi/Anti-Anti-Spider](https://github.com/luyishisi/Anti-Anti-Spider) ★7279 [Python/-/147MB] 越来越多的网站具有反爬虫特性，有的用图片隐藏关键数据，有的使用反人类的验证码，建立反反爬虫的代码仓库，通过与不同特性的网站做斗争（无恶意）提高技术。（欢迎提交难
- [TonyChen56/WeChatRobot](https://github.com/TonyChen56/WeChatRobot) ★7183 [C++/-/36MB] 微信HOOK、微信机器人   wxhook，数据库解密 微信公众号采集 微信公众号爬虫，企业微信HOOK
- [scikit-learn-contrib/imbalanced-learn](https://github.com/scikit-learn-contrib/imbalanced-learn) ★7120 [Python/MIT/23MB]  A Python Package to Tackle the Curse of Imbalanced Datasets in Machine Learning
- [xiangyuecn/AreaCity-JsSpider-StatsGov](https://github.com/xiangyuecn/AreaCity-JsSpider-StatsGov) ★6835 [JavaScript/MIT/5MB] 省市区县乡镇三级或四级城市数据，带拼音标注、坐标、行政区域边界范围；2026年04月03日最新采集，提供csv格式文件，支持在线转成多级联动js代码、通用jso
- [googlecreativelab/quickdraw-dataset](https://github.com/googlecreativelab/quickdraw-dataset) ★6803 [-/NOASSERTION/153KB] Documentation on how to access and use the Quick, Draw! Dataset.
- [yangchong211/YCBlogs](https://github.com/yangchong211/YCBlogs) ★6517 [-/Apache-2.0/68MB] 技术博客笔记大汇总，包括Java基础，线程，并发，数据结构；Android技术博客等等；常用设计模式；常见的算法；网络协议知识点；部分flutter笔记；还包括
- [tensorflow/datasets](https://github.com/tensorflow/datasets) ★4580 [Python/Apache-2.0/976MB] TFDS is a collection of datasets ready to use with TensorFlow, Jax, ...
- [jdorfman/awesome-json-datasets](https://github.com/jdorfman/awesome-json-datasets) ★3612 [JavaScript/CC0-1.0/252KB] A curated list of awesome JSON datasets that don't require authentication.
- [waymo-research/waymo-open-dataset](https://github.com/waymo-research/waymo-open-dataset) ★3392 [Python/NOASSERTION/97MB] Waymo Open Dataset
- [meagmohit/EEG-Datasets](https://github.com/meagmohit/EEG-Datasets) ★3088 [-/-/115KB] A list of all public EEG-datasets
- [bytewax/awesome-public-real-time-datasets](https://github.com/bytewax/awesome-public-real-time-datasets) ★2885 [-/CC0-1.0/73KB] A list of publicly available datasets with real-time data maintained by the team
- [Trusted-AI/AIF360](https://github.com/Trusted-AI/AIF360) ★2856 [Python/Apache-2.0/7MB] A comprehensive set of fairness metrics for datasets and machine learning models
- [logpai/loghub](https://github.com/logpai/loghub) ★2800 [-/NOASSERTION/7MB] A large collection of system log datasets for AI-driven log analytics [ISSRE'23]
- [huggingface/evaluate](https://github.com/huggingface/evaluate) ★2478 [Python/Apache-2.0/2MB] 🤗 Evaluate: A library for easily evaluating machine learning models and datasets
- [beir-cellar/beir](https://github.com/beir-cellar/beir) ★2275 [Python/Apache-2.0/40MB] A Heterogeneous Benchmark for Information Retrieval. Easy to use, evaluate your 
- [WillKoehrsen/feature-selector](https://github.com/WillKoehrsen/feature-selector) ★2230 [Jupyter Notebook/GPL-3.0/5MB] Feature selector is a tool for dimensionality reduction of machine learning data
- [zhu-xlab/GlobalBuildingAtlas](https://github.com/zhu-xlab/GlobalBuildingAtlas) ★2195 [Python/NOASSERTION/64MB] GlobalBuildingAtlas: an open global and complete dataset of building polygons, h
- [nvkelso/natural-earth-vector](https://github.com/nvkelso/natural-earth-vector) ★2181 [HTML/NOASSERTION/11.4GB] A global, public domain map dataset available at three scales and featuring tigh
- [Thinklab-SJTU/Bench2Drive](https://github.com/Thinklab-SJTU/Bench2Drive) ★1927 [Python/NOASSERTION/112MB] [NeurIPS 2024 Datasets and Benchmarks Track] Closed-Loop E2E-AD Benchmark Enhanc
- [OTRF/Security-Datasets](https://github.com/OTRF/Security-Datasets) ★1802 [PowerShell/MIT/810MB] Re-play Security Events
- [yuhonas/free-exercise-db](https://github.com/yuhonas/free-exercise-db) ★1784 [Vue/Unlicense/96MB] Open Public Domain Exercise Dataset in JSON format, over 800 exercises with a br
- [awslabs/open-data-registry](https://github.com/awslabs/open-data-registry) ★1770 [Python/Apache-2.0/12MB] A registry of publicly available datasets on AWS
- [WillKoehrsen/machine-learning-project-walkthrough](https://github.com/WillKoehrsen/machine-learning-project-walkthrough) ★1300 [Jupyter Notebook/-/22MB] An implementation of a complete machine learning solution in Python on a real-wo
- [jbrownlee/Datasets](https://github.com/jbrownlee/Datasets) ★1246 [-/-/221MB] Machine learning datasets used in tutorials on MachineLearningMastery.com
- [Azure/AzurePublicDataset](https://github.com/Azure/AzurePublicDataset) ★1181 [Jupyter Notebook/CC-BY-4.0/106MB] Microsoft Azure Traces
- [NEU-Gou/awesome-reid-dataset](https://github.com/NEU-Gou/awesome-reid-dataset) ★1103 [-/-/25MB] Collection of public available person re-identification datasets
- [doc-analysis/TableBank](https://github.com/doc-analysis/TableBank) ★1083 [-/Apache-2.0/800KB] TableBank: A Benchmark Dataset for Table Detection and Recognition
- [PhantomInsights/baby-names-analysis](https://github.com/PhantomInsights/baby-names-analysis) ★563 [Python/MIT/10MB] Data ETL & Analysis on the dataset 'Baby Names from Social Security Card Applica
- [gfek/Real-CyberSecurity-Datasets](https://github.com/gfek/Real-CyberSecurity-Datasets) ★481 [-/-/95KB] Public datasets to help you address various cyber security problems.

### 数据工具与生态（163 个，含采集/标注/合成/低星数据集）

- [ultralytics/flickr_scraper](https://github.com/ultralytics/flickr_scraper) ★294 [Python/AGPL-3.0] Python Flickr image scraper for building keyword-based computer vision
- [SHI-Labs/Agriculture-Vision](https://github.com/SHI-Labs/Agriculture-Vision) ★259 [-/-] [CVPR 2020 & 2021 & 2022 & 2023] Agriculture-Vision Dataset, Prize Cha
- [pengfei-luo/multimodal-knowledge-graph](https://github.com/pengfei-luo/multimodal-knowledge-graph) ★251 [-/-] A collection of resources on multimodal knowledge graph, including dat
- [xinke-wang/OCRDatasets](https://github.com/xinke-wang/OCRDatasets) ★225 [-/-] A collection of OCR-related datasets
- [Messi-Q/Smart-Contract-Dataset](https://github.com/Messi-Q/Smart-Contract-Dataset) ★202 [-/-] Datasets for evaluating smart contract security analysis tools ( conti
- [tsafavi/codex](https://github.com/tsafavi/codex) ★179 [Python/MIT] CoDEx: A set of knowledge graph Completion Datasets Extracted from Wik
- [icsdataset/hai](https://github.com/icsdataset/hai) ★179 [Jupyter Notebook/-] HIL-based Augmented ICS (HAI) Security Dataset
- [facebookresearch/MathsFromExamples](https://github.com/facebookresearch/MathsFromExamples) ★178 [Python/NOASSERTION] Source code, datasets and trained models for the paper Learning Advanc
- [microsoft/FS-Mol](https://github.com/microsoft/FS-Mol) ★177 [Python/NOASSERTION] FS-Mol  is A Few-Shot Learning Dataset of Molecules, containing molecu
- [awslabs/service-workbench-on-aws](https://github.com/awslabs/service-workbench-on-aws) ★174 [JavaScript/Apache-2.0] A platform that provides researchers with one-click access to collabor
- [Future-House/ether0](https://github.com/Future-House/ether0) ★167 [Python/Apache-2.0] A scientific reasoning model, dataset, and reward functions for chemis
- [cgpotts/dynasent](https://github.com/cgpotts/dynasent) ★165 [Jupyter Notebook/Apache-2.0] DynaSent: Dynamic Sentiment Analysis Dataset
- [leap-stc/ClimSim](https://github.com/leap-stc/ClimSim) ★164 [Jupyter Notebook/Apache-2.0] An open large-scale dataset for training high-resolution physics emula
- [Kamino666/watermark-tracer](https://github.com/Kamino666/watermark-tracer) ★162 [Python/GPL-3.0] 一个基于可视水印检测识别的数字媒体溯源应用系统，是我的大作业项目，包含这个系统以及一个开源的大规模常见水印图像数据集（Large-scale
- [microsoft/OpenKP](https://github.com/microsoft/OpenKP) ★159 [Python/MIT] Automatically extracting keyphrases that are salient to the document m
- [pinder-org/pinder](https://github.com/pinder-org/pinder) ★158 [Python/Apache-2.0] PINDER: The Protein INteraction Dataset and Evaluation Resource
- [TheophileBlard/french-sentiment-analysis-with-bert](https://github.com/TheophileBlard/french-sentiment-analysis-with-bert) ★157 [Jupyter Notebook/MIT]  How good is BERT ? Comparing BERT to other state-of-the-art approache
- [BboyHanat/TextGenerator](https://github.com/BboyHanat/TextGenerator) ★149 [Python/MIT] OCR dataset Text-Detection dataset Font-Classification dataset generat
- [BEAM-Labs/FoldBench](https://github.com/BEAM-Labs/FoldBench) ★148 [Python/MIT] FoldBench is a low-homology benchmark spanning proteins, nucleic acids
- [ahammadmejbah/Awesome-Datasets-Hub](https://github.com/ahammadmejbah/Awesome-Datasets-Hub) ★147 [-/-] A curated collection of datasets for Large Language Models (LLMs), cov
- [AmanPriyanshu/Awesome-AI-For-Security](https://github.com/AmanPriyanshu/Awesome-AI-For-Security) ★147 [-/CC0-1.0] A curated list of tools, papers, and datasets for applying AI to cyber
- [BeiCunNan/Sentiment_Analysis_Imdb](https://github.com/BeiCunNan/Sentiment_Analysis_Imdb) ★146 [Python/-] Using Bert/Roberta + LSTM/GRU/BiLSTM/TextCNN to do the sentiment analy
- [ds4v/NomNaOCR](https://github.com/ds4v/NomNaOCR) ★146 [Jupyter Notebook/MIT] Leverage Deep Learning to digitize old Vietnamese handwritten for hist
- [bytesc/Image-Recognition-system](https://github.com/bytesc/Image-Recognition-system) ★144 [Python/MIT] ✨基于 3D 卷积神经网络(CNN)的阿尔兹海默智能诊断 Web 应用  Alzheimer's Intelligent Diagnosis
- [doguilmak/Drone-Detection-YOLOv8x](https://github.com/doguilmak/Drone-Detection-YOLOv8x) ★144 [Jupyter Notebook/MIT] This repository provides a dataset and model for real-time drone detec
- [xv44586/Chinese-instruction-datasets](https://github.com/xv44586/Chinese-instruction-datasets) ★143 [-/-] 中文 Instruction tuning datasets
- [chakki-works/chABSA-dataset](https://github.com/chakki-works/chABSA-dataset) ★143 [Jupyter Notebook/MIT] chakki's Aspect-Based Sentiment Analysis dataset
- [mathllm/MATH-V](https://github.com/mathllm/MATH-V) ★142 [Python/MIT] [NeurIPS 2024] MATH-Vision dataset and code to measure multimodal math
- [geniusrise/awesome-healthcare-datasets](https://github.com/geniusrise/awesome-healthcare-datasets) ★140 [-/CC0-1.0] Healthcare and biomedical datasets, for AI/ML
- [NoorBayan/Frahidi](https://github.com/NoorBayan/Frahidi) ★138 [Python/MIT] Frahidi is a comprehensive system for performing prosodic analysis of 
- [bio2rdf/bio2rdf-scripts](https://github.com/bio2rdf/bio2rdf-scripts) ★137 [Java/NOASSERTION] Scripts that Bio2RDF users have created to generate RDF versions of sc
- [open-h/open-h-embodiment](https://github.com/open-h/open-h-embodiment) ★135 [Python/NOASSERTION] Open-H-Embodiment is a community‑driven dataset initiative building th
- [drqiaojin/biomedical-qa-datasets](https://github.com/drqiaojin/biomedical-qa-datasets) ★132 [-/MIT] Biomedical Question Answering Datasets.
- [instadeepai/tunbert](https://github.com/instadeepai/tunbert) ★131 [Python/MIT] TunBERT is the first release of a pre-trained BERT model for the Tunis
- [shreyasharma04/HealthChatbot](https://github.com/shreyasharma04/HealthChatbot) ★131 [Python/-] 🤖 HealthCare ChatBot Major -1 (4th year - 7th semester)  Health Care C
- [BIMCV-CSUSP/BIMCV-COVID-19](https://github.com/BIMCV-CSUSP/BIMCV-COVID-19) ★130 [HTML/MIT] Valencia Region Image Bank (BIMCV) that combines data from the PadChes
- [baldassarreFe/graph-network-explainability](https://github.com/baldassarreFe/graph-network-explainability) ★127 [Jupyter Notebook/-] Explainability techniques for Graph Networks, applied to a synthetic d
- [Future-House/LAB-Bench](https://github.com/Future-House/LAB-Bench) ★126 [Python/CC-BY-SA-4.0] Evaluation dataset for AI systems intended to benchmark capabilities f
- [nickls/awesome-healthcare-datasets](https://github.com/nickls/awesome-healthcare-datasets) ★123 [-/MIT] A curated list of awesome healthcare datasets in the public domain.
- [ERDDAP/erddap](https://github.com/ERDDAP/erddap) ★122 [Java/CC0-1.0] ERDDAP is a scientific data server that gives users a simple, consiste
- [zpc1314521/PCL2](https://github.com/zpc1314521/PCL2) ★120 [-/MIT] [stays mad] 反PCL宣传库。Anti PCL propaganda. 大陆修宪香港恶法台湾武统朝鲜毁约美中冷战等都是王沪宁愚弄习
- [usail-hkust/UUKG](https://github.com/usail-hkust/UUKG) ★119 [Python/MIT] UUKG: Unified Urban Knowledge Graph Dataset for Knowledge-Enhanced Urb
- [Lum1104/MER-Factory](https://github.com/Lum1104/MER-Factory) ★118 [Python/MIT] 🚀 Pre-process, annotate, evaluate, and train your Affect Computing (e.
- [Santosh-Gupta/ScientificSummarizationDataSets](https://github.com/Santosh-Gupta/ScientificSummarizationDataSets) ★116 [Jupyter Notebook/-] Datasets I have created for scientific summarization, and a trained Be
- [open-compass/MathBench](https://github.com/open-compass/MathBench) ★116 [-/Apache-2.0] [ACL 2024 Findings] MathBench: A Comprehensive Multi-Level Difficulty 
- [THU-KEG/MetaKGR](https://github.com/THU-KEG/MetaKGR) ★116 [Python/-] Source codes and datasets for EMNLP 2019 paper "Adapting Meta Knowledg
- [BorgwardtLab/proteinshake](https://github.com/BorgwardtLab/proteinshake) ★115 [Python/BSD-3-Clause] Protein structure datasets for machine learning.
- [muhaochen/seq_ppi](https://github.com/muhaochen/seq_ppi) ★115 [Python/Apache-2.0] This is the repository for PIPR. This repository contains the source c
- [OSU-NLP-Group/LLM4Chem](https://github.com/OSU-NLP-Group/LLM4Chem) ★113 [Python/MIT] Official code repo for the paper "LlaSMol: Advancing Large Language Mo
- [declare-lab/flacuna](https://github.com/declare-lab/flacuna) ★112 [Python/-] Flacuna was developed by fine-tuning Vicuna on Flan-mini, a comprehens
- [declare-lab/red-instruct](https://github.com/declare-lab/red-instruct) ★111 [Python/Apache-2.0] Codes and datasets of the paper Red-Teaming Large Language Models usin
- [LLM360/MegaMath](https://github.com/LLM360/MegaMath) ★110 [XSLT/Apache-2.0] [COLM 2025] An Open Math Pre-trainng Dataset with 370B Tokens.
- [mattmacy/torchbiomed](https://github.com/mattmacy/torchbiomed) ★110 [Python/BSD-3-Clause] Datasets, Transforms and Utilities specific to Biomedical Imaging
- [Wei-ZENG1020/Value-Alignment-Agentic-AI-Papers-Survey-Taxonomy](https://github.com/Wei-ZENG1020/Value-Alignment-Agentic-AI-Papers-Survey-Taxonomy) ★109 [-/-] This repository is created to support the survey paper Application-Dri
- [anton-bushuiev/PPIRef](https://github.com/anton-bushuiev/PPIRef) ★109 [Jupyter Notebook/MIT] Dataset and package for working with protein-protein interactions in 3
- [minwoosun/biomedica-etl](https://github.com/minwoosun/biomedica-etl) ★108 [Python/MIT] [CVPR 2025] BIOMEDICA: An Open Biomedical Image-Caption Archive, Datas
- [avbiswas/text-albumentations](https://github.com/avbiswas/text-albumentations) ★106 [Python/MIT] A simple library for generating instruction tuning datasets locally
- [Max-Fu/tvl](https://github.com/Max-Fu/tvl) ★101 [Python/Apache-2.0] [ICML 2024] A Touch, Vision, and Language Dataset for Multimodal Align
- [FabioYanezRomero/Knowledge-Graph-Builder](https://github.com/FabioYanezRomero/Knowledge-Graph-Builder) ★100 [Python/MIT] Repository for building knowledge graphs from specific datasets using 
- [robinhad/kruk](https://github.com/robinhad/kruk) ★96 [Jupyter Notebook/Apache-2.0] Ukrainian instruction-tuned language models and datasets
- [Mr-Pepe/iscx-analysis](https://github.com/Mr-Pepe/iscx-analysis) ★96 [Python/-] Analysis of the ISCX VPN-nonVPN Dataset 2016 for Encrypted Network Tra
- [Iretha/IoT23-network-traffic-anomalies-classification](https://github.com/Iretha/IoT23-network-traffic-anomalies-classification) ★94 [Python/MIT] AI & Machine Learning: Detection and Classification of Network Traffic
- [eth-nlped/mathdial](https://github.com/eth-nlped/mathdial) ★93 [Python/-] 🧮 MathDial: A Dialog Tutoring Dataset with Rich Pedagogical Properties
- [cogtoolslab/physics-benchmarking-neurips2021](https://github.com/cogtoolslab/physics-benchmarking-neurips2021) ★93 [Jupyter Notebook/MIT] Repo for "Physion: Evaluating Physical Prediction from Vision in Human
- [Aryia-Behroziuan/neurons](https://github.com/Aryia-Behroziuan/neurons) ★93 [-/-] An ANN is a model based on a collection of connected units or nodes ca
- [vibhavnirmal/Knowledge-Graph-based-QnA](https://github.com/vibhavnirmal/Knowledge-Graph-based-QnA) ★93 [Python/MIT] Developing a Knowledge Graph-based Question and Answering program to e
- [noewangjy/csprd_dataset](https://github.com/noewangjy/csprd_dataset) ★91 [Python/-] This is the repository for the paper CSPRD: A Financial Policy Retriev
- [facebookresearch/iGSM](https://github.com/facebookresearch/iGSM) ★90 [Python/MIT] The code for creating the iGSM datasets in papers "Physics of Language
- [gptechday/openai-academy-kg-recipe](https://github.com/gptechday/openai-academy-kg-recipe) ★89 [Python/MIT] A recipe for building a knowledge graph and deploying a knowledge grap
- [MLMI2-CSSI/foundry](https://github.com/MLMI2-CSSI/foundry) ★87 [Python/MIT] Simplifying the discovery and usage of machine-learning ready datasets
- [seukgcode/MELBench](https://github.com/seukgcode/MELBench) ★87 [-/MIT] Multimodal entity linking (MEL) aims to utilize multimodal information
- [plinder-org/runs-n-poses](https://github.com/plinder-org/runs-n-poses) ★86 [Jupyter Notebook/Apache-2.0] A benchmark dataset for protein-ligand co-folding prediction
- [THGLab/HiQBind](https://github.com/THGLab/HiQBind) ★84 [Jupyter Notebook/MIT] Workflow to clean up and fix structural problems in protein-ligand bin
- [NiteshMethani/PlotQA](https://github.com/NiteshMethani/PlotQA) ★83 [-/MIT] Dataset introduced in PlotQA: Reasoning over Scientific Plots
- [NJUxlj/Travel-Agent-based-on-Qwen2-RLHF](https://github.com/NJUxlj/Travel-Agent-based-on-Qwen2-RLHF) ★81 [Python/-] A travel agent based on Qwen2.5, fine-tuned by SFT + DPO/PPO/GRPO usin
- [gem-pasteur/macsyfinder](https://github.com/gem-pasteur/macsyfinder) ★80 [Python/GPL-3.0] MacSyFinder - Detection of macromolecular systems in protein datasets 
- [harshilpatel1799/Iot-Cyber-Security-with-Machine-Learning-Research-Project](https://github.com/harshilpatel1799/Iot-Cyber-Security-with-Machine-Learning-Research-Project) ★80 [Jupyter Notebook/-] IoT networks have become an increasingly valuable target of malicious 
- [jinbo0906/Awesome-MLLM-Datasets](https://github.com/jinbo0906/Awesome-MLLM-Datasets) ★78 [-/MIT] This project aims to collect and collate various datasets for multimod
- [ajitrajasekharan/unsupervised_NER](https://github.com/ajitrajasekharan/unsupervised_NER) ★78 [Python/MIT] Self-supervised NER prototype - updated version (69 entity types - 17 
- [YJiangcm/Chinese-sentence-pair-modeling](https://github.com/YJiangcm/Chinese-sentence-pair-modeling) ★78 [Jupyter Notebook/Apache-2.0] Use deep models including BiLSTM, ABCNN, ESIM, RE2, BERT, etc.  and ev
- [rafiattrach/m3](https://github.com/rafiattrach/m3) ★77 [Python/MIT] 🏥🤖 Query MIMIC-IV medical data using natural language through Model Co
- [ahlashkari/ISCXFlowMeter](https://github.com/ahlashkari/ISCXFlowMeter) ★76 [Java/NOASSERTION] ISCXFlowMeter is an Ethernet traffic flow generator and analyzer for a
- [Aabishkar2/nepse-data](https://github.com/Aabishkar2/nepse-data) ★75 [Python/-] Historical and current datasets of Nepal Stock Market listed companies
- [SynthLabsAI/big-math](https://github.com/SynthLabsAI/big-math) ★74 [Python/MIT] A Large-Scale, High-Quality Math Dataset for Reinforcement Learning in
- [junioralive/Indian-Medicine-Dataset](https://github.com/junioralive/Indian-Medicine-Dataset) ★74 [-/MIT] A curated dataset of Indian medicines, organized by brand. Essential f
- [cyzhh/MMOS](https://github.com/cyzhh/MMOS) ★73 [Python/-] Mix of Minimal Optimal Sets (MMOS) of dataset has two advantages for t
- [nhs-r-community/NHSRdatasets](https://github.com/nhs-r-community/NHSRdatasets) ★72 [R/CC0-1.0] NHS and healthcare related datasets for training and learning R
- [apluka34/Bud500](https://github.com/apluka34/Bud500) ★71 [-/Apache-2.0] Bud500: A Comprehensive Vietnamese ASR Dataset
- [IdahoLabResearch/5GAD](https://github.com/IdahoLabResearch/5GAD) ★71 [Jupyter Notebook/MIT] This is a dataset of 5G network traffic for use with machine learning 
- [youzanai/trexpark](https://github.com/youzanai/trexpark) ★70 [Python/-] T‘rex Park is a Youzan sponsored project. Offering Chinese NLP and ima
- [MaliParag/TFD-ICDAR2019](https://github.com/MaliParag/TFD-ICDAR2019) ★69 [Python/-] TDF-ICDAR 2019 Dataset for Typeset Math Formula Detection
- [google-research-datasets/GSM-IC](https://github.com/google-research-datasets/GSM-IC) ★67 [-/-] Grade-School Math with Irrelevant Context (GSM-IC) benchmark is an ari
- [YZY010418/CPSea](https://github.com/YZY010418/CPSea) ★66 [Python/-] A cyclic peptide-protein complex dataset derived from AFDB.
- [zonghui0228/BioMedical-NLP-corpus](https://github.com/zonghui0228/BioMedical-NLP-corpus) ★63 [-/-] Biomedical NLP Corpus or Datasets.
- [harshilpatel1799/IoT-Network-Intrusion-Detection-and-Classification-using-Explainable-XAI-Machine-Learning](https://github.com/harshilpatel1799/IoT-Network-Intrusion-Detection-and-Classification-using-Explainable-XAI-Machine-Learning) ★61 [Jupyter Notebook/-] The continuing  increase of Internet of Things (IoT) based networks ha
- [ECNU-ICALK/EduChat-Math](https://github.com/ECNU-ICALK/EduChat-Math) ★59 [Python/-] [MM 2025] CMM-Math: A Chinese Multimodal Math Dataset To Evaluate and 
- [tongjingqi/MathTrap](https://github.com/tongjingqi/MathTrap) ★59 [Python/Apache-2.0] In this work, we investigate the compositionality of large language mo
- [NVIDIA/physicsnemo-curator](https://github.com/NVIDIA/physicsnemo-curator) ★59 [Python/Apache-2.0] Accelerated ETL toolkit for building AI-ready datasets across multiple
- [socrateai-official/nepse-open-data](https://github.com/socrateai-official/nepse-open-data) ★59 [-/NOASSERTION] Open-source NEPSE stock market data including index, ohlcv, and floors
- [IDEA-XL/ChemCoTBench](https://github.com/IDEA-XL/ChemCoTBench) ★56 [Python/-] LLM Reasoning Benchmark & Chain-of-Thoughts Dataset for Chemistry
- [CatOn60Hz/Real-time-Network-Traffic-Classifier-IDS](https://github.com/CatOn60Hz/Real-time-Network-Traffic-Classifier-IDS) ★55 [Python/MIT] This project develops and deploys a robust, multi-class Network Intrus
- [thu-spmi/ASR-Benchmarks](https://github.com/thu-spmi/ASR-Benchmarks) ★54 [-/-] An effort to track benchmarking results over widely-used datasets for 
- [jay-johnson/network-pipeline](https://github.com/jay-johnson/network-pipeline) ★53 [Python/Apache-2.0] Network traffic data pipeline for real-time predictions and building d
- [ZMH-SDUST/PhysLab](https://github.com/ZMH-SDUST/PhysLab) ★52 [-/-] PhysLab: A Benchmark Dataset for Multi-Granularity Visual Parsing of P
- [halleewong/MultiverSeg](https://github.com/halleewong/MultiverSeg) ★52 [Jupyter Notebook/Apache-2.0] [ICCV 2025] MultiverSeg: Scalable Interactive Segmentation of Biomedic
- [Open-Speech-EkStep/ULCA-asr-dataset-corpus](https://github.com/Open-Speech-EkStep/ULCA-asr-dataset-corpus) ★51 [-/CC-BY-4.0] 
- [freds0/data_augmentation_for_asr](https://github.com/freds0/data_augmentation_for_asr) ★49 [Python/GPL-3.0] A set of audio augmentation techniques to perform noise insertion in d
- [CESNET/cesnet-datazoo](https://github.com/CESNET/cesnet-datazoo) ★49 [Python/BSD-3-Clause] CESNET DataZoo: A toolset for large network traffic datasets
- [EchoseChen/SPA-VL-RLHF](https://github.com/EchoseChen/SPA-VL-RLHF) ★48 [Python/MIT] The reinforcement learning codes for dataset SPA-VL
- [klintan/swedish-asr-dataset](https://github.com/klintan/swedish-asr-dataset) ★46 [Jupyter Notebook/MIT] Jupyter Notebooks for creating Speech datasets
- [karamouche/noisekit](https://github.com/karamouche/noisekit) ★45 [Python/MIT] Generate degraded speech datasets for noise-robust ASR benchmarking
- [gyunggyung/LLM-Ko-Datasets](https://github.com/gyunggyung/LLM-Ko-Datasets) ★44 [-/Apache-2.0] 🇰🇷 Korean LLM Datasets | Pre-training, SFT, DPO, RLHF, CoT | 한국어 LLM 데
- [persiandataset/PersianSpeech](https://github.com/persiandataset/PersianSpeech) ★44 [-/MIT] Persian ASR dataset
- [alicank/Translation-Augmented-LibriSpeech-Corpus](https://github.com/alicank/Translation-Augmented-LibriSpeech-Corpus) ★44 [Python/-] Large scale (>200h) and publicly available read audio book corpus. Thi
- [AlexSWong/COVID-Net](https://github.com/AlexSWong/COVID-Net) ★43 [-/-] Launched in March 2020 in response to the coronavirus disease 2019 (CO
- [tubexchat/Rocky-wechatbot](https://github.com/tubexchat/Rocky-wechatbot) ★42 [C/MIT] WeChatBot with ASR & LLM: Integrated with Gemini API and Microsoft ASR
- [IoBT-VISTEC/MetaSleepLearner](https://github.com/IoBT-VISTEC/MetaSleepLearner) ★42 [Python/-] Meta-Learning for EEG, Sleep Staging, Transfer Learning, Pre-trained E
- [vohidjon123/google](https://github.com/vohidjon123/google) ★42 [-/-] (function(sttc){/*     Copyright The Closure Library Authors.   SPDX-L
- [mravanelli/pytorch_MLP_for_ASR](https://github.com/mravanelli/pytorch_MLP_for_ASR) ★40 [Perl/-] This code implements a basic MLP for speech recognition. The MLP  is t
- [Hazrat-Ali9/Domain-Specific-ML-for-Researchers](https://github.com/Hazrat-Ali9/Domain-Specific-ML-for-Researchers) ★40 [-/-] 🍊 A curated 🍎 hands on 🍏 tailored 🍑 researchers 🫑 applying 🍔 Machine 🍘
- [asreview/asreview-datatools](https://github.com/asreview/asreview-datatools) ★39 [Python/MIT] Tool to preprocess datasets for ASReview
- [WM-JayLab/NetBench](https://github.com/WM-JayLab/NetBench) ★37 [-/-] Related code and datasets on NetBench: A Large-Scale and Comprehensive
- [CHILab1/MedPix-2.0](https://github.com/CHILab1/MedPix-2.0) ★36 [Python/-] MedPix 2.0: A Comprehensive Multimodal Biomedical Dataset for Advanced
- [DanielLin94144/DUAL-textless-SQA](https://github.com/DanielLin94144/DUAL-textless-SQA) ★35 [Python/CC-BY-SA-4.0] Textless (ASR-transcript free) Spoken Question Answering. The official
- [uw-biomedical-ml/uwhvf](https://github.com/uw-biomedical-ml/uwhvf) ★35 [-/BSD-3-Clause] Open source dataset of more than 25 thousand Humphrey Visual Fields (H
- [biyoml/End-to-End-Mandarin-ASR](https://github.com/biyoml/End-to-End-Mandarin-ASR) ★34 [Python/-] End-to-end speech recognition on AISHELL dataset.
- [NVlabs/ProfBench](https://github.com/NVlabs/ProfBench) ★34 [Python/MIT] PhD/MBA-level human-annotated rubrics dataset across Physics, Chemistr
- [ajayshewale/Sentiment-Analysis-of-Text-Data-Tweets-](https://github.com/ajayshewale/Sentiment-Analysis-of-Text-Data-Tweets-) ★34 [HTML/-] This project addresses the problem of sentiment analysis on Twitter. T
- [naiksrinu/UAV_DataSet_NetworkCommunication](https://github.com/naiksrinu/UAV_DataSet_NetworkCommunication) ★33 [Python/-] UAV Network Communication Experimental dataset is a collection of netw
- [rronan/IntPhys-Baselines](https://github.com/rronan/IntPhys-Baselines) ★30 [Python/-] Code for paper "IntPhys: A Benchmark and Dataset for Intuitive Physics
- [PLAID-lib/plaid](https://github.com/PLAID-lib/plaid) ★29 [Python/BSD-3-Clause] PLAID (Physics-Learning AI Datamodel), a flexible and extensible frame
- [lishiqianhugh/GlobalTomo](https://github.com/lishiqianhugh/GlobalTomo) ★28 [Python/Apache-2.0] The first global synthetic dataset for physics-ML seismic wavefield mo
- [yhc-1/MetaGraspNet](https://github.com/yhc-1/MetaGraspNet) ★27 [Python/Apache-2.0] MetaGraspNet: a large-scale benchmark dataset for vision-driven roboti
- [zacharykzhao/CA4P-483](https://github.com/zacharykzhao/CA4P-483) ★26 [HTML/NOASSERTION] NLP dataset: Chinese Android Privacy Policy Dataset
- [JoJo0217/rlhf_korean_dataset](https://github.com/JoJo0217/rlhf_korean_dataset) ★25 [Python/-] For the rlhf learning environment of Koreans
- [argilla-io/awesome-llm-datasets](https://github.com/argilla-io/awesome-llm-datasets) ★25 [-/Apache-2.0] 👩🤝🤖 A curated list of datasets for large language models (LLMs), RLHF 
- [ashishpatel26/NYSE-STOCK_MARKET-ANALYSIS-USING-LSTM](https://github.com/ashishpatel26/NYSE-STOCK_MARKET-ANALYSIS-USING-LSTM) ★25 [Jupyter Notebook/GPL-3.0] Stock market data can be interesting to analyze and as a further incen
- [xz6014/FORCE_dataset](https://github.com/xz6014/FORCE_dataset) ★24 [Python/-] Dataset for FORCE - Physics-aware Human-object Interaction (3DV 2025)
- [sowide/bankruptcy_dataset](https://github.com/sowide/bankruptcy_dataset) ★22 [-/CC-BY-4.0] Bankruptcy prediction dataset related to the american companies in the
- [howl-anderson/corpus_dataset_for_Chinese_NLP](https://github.com/howl-anderson/corpus_dataset_for_Chinese_NLP) ★20 [-/MIT] 中文 NLP 语料库数据集
- [brandonhimpfen/awesome-chemistry](https://github.com/brandonhimpfen/awesome-chemistry) ★18 [Python/-] A curated list of resources for chemistry, spanning theory, computatio
- [csxrzhang/NLPDataSet](https://github.com/csxrzhang/NLPDataSet) ★18 [Python/-] chinese NLP dataset
- [haolunc/iGSM-Replication-physics-LLM](https://github.com/haolunc/iGSM-Replication-physics-LLM) ★17 [Python/MIT] This repository contains the replication of the iGSM dataset generatio
- [d-f/llm-summarization](https://github.com/d-f/llm-summarization) ★14 [Python/-] LoRA supervised fine-tuning, RLHF (PPO) and RAG with llama-3-8B on the
- [nfdi-de/chem-dcat-ap](https://github.com/nfdi-de/chem-dcat-ap) ★14 [Python/MIT] This is an extension of the DCAT Application Profile PLUS LinkML schem
- [ShravanChintha/Stock-Market-prediction-using-daily-news-headlines](https://github.com/ShravanChintha/Stock-Market-prediction-using-daily-news-headlines) ★14 [Python/-] The project is about predicting the stock market movement based on the
- [ZN1010/PEaCE](https://github.com/ZN1010/PEaCE) ★13 [Python/-] [LREC-COLING 2024] PEaCE: A Chemistry-Oriented Dataset for Optical Cha
- [nttstar/guustock](https://github.com/nttstar/guustock) ★13 [Ruby/-] Guustock platform is recommended for Chinese stock traders interested 
- [Lekshmi2003-glitch/market-auto-logit-analysis](https://github.com/Lekshmi2003-glitch/market-auto-logit-analysis) ★13 [-/-] R-based analysis applying logistic regression to two datasets: Weekly 
- [aryan-harsh/Stock-Market-Predictor](https://github.com/aryan-harsh/Stock-Market-Predictor) ★12 [Jupyter Notebook/-] This contains our project for the course Data Mining, titled Stock Mar
- [Daniblit/Ensemble-Predictive-Model-Forecasting-AMGEN-stock-price-at-year-end-31s](https://github.com/Daniblit/Ensemble-Predictive-Model-Forecasting-AMGEN-stock-price-at-year-end-31s) ★12 [-/-] The basis of this project involves analyzing Amgen future profitabilit
- [wassname/awesome-rlhf](https://github.com/wassname/awesome-rlhf) ★10 [-/-] Lists of datasets, training, and evals for RLHF and similar
- [DaehanKim/EasyRLHF](https://github.com/DaehanKim/EasyRLHF) ★9 [Python/-] EasyRLHF aims to provide an easy and minimal interface to train aligne
- [sparks-baird/matsci-opt-benchmarks](https://github.com/sparks-baird/matsci-opt-benchmarks) ★9 [Jupyter Notebook/MIT] A collection of benchmarking problems and datasets for testing the per
- [Sid-darthvader/Machine-Learning-for-Thermoelectrics-Discovery](https://github.com/Sid-darthvader/Machine-Learning-for-Thermoelectrics-Discovery) ★8 [R/-] Transition metal oxides are attractive materials for high temperature 
- [digital-chemistry/Curated_POMs](https://github.com/digital-chemistry/Curated_POMs) ★7 [JavaScript/CC0-1.0] This dataset contains a curated collection of Polyoxometalate (POM) fo
- [gemphis71/openchemprocess](https://github.com/gemphis71/openchemprocess) ★7 [HTML/NOASSERTION] Machine-readable process-review and risk-interpretation dataset for pr
- [RyanMeg123/ShopBot-SFT-Dataset](https://github.com/RyanMeg123/ShopBot-SFT-Dataset) ★6 [Python/NOASSERTION] 电商客服对话数据集 - SFT & RLHF 训练数据
- [FabioLousJay/lexpref-ptbr](https://github.com/FabioLousJay/lexpref-ptbr) ★6 [Jupyter Notebook/-] LexPref-PTBR: A Brazilian Portuguese Legal Preference Dataset and RLHF
- [SJ9VRF/Reinforcement-Learning-for-Human-Feedback-RLHF](https://github.com/SJ9VRF/Reinforcement-Learning-for-Human-Feedback-RLHF) ★5 [Python/-] This repository contains the implementation of a Reinforcement Learnin
- [AnthropicBots/dpo-vs-rlhf-alignmet-study](https://github.com/AnthropicBots/dpo-vs-rlhf-alignmet-study) ★4 [Python/MIT] Empirical comparison of DPO vs RLHF alignment for LLMs | GPT-2 | HH-RL
- [aayushkrm/auto-cheminstruct](https://github.com/aayushkrm/auto-cheminstruct) ★3 [Python/MIT] Multi-agent pipeline generating physically-validated RLHF data for che
- [tsyncIO/Movie_Recommender_System_RLHF](https://github.com/tsyncIO/Movie_Recommender_System_RLHF) ★2 [Python/-] Reinforcement Learning-based Recommender System using the MovieLens da
---

## 附录 B：原始数据文件

| 文件 | 路径 | 说明 |
|:-----|:-----|:-----|
| 原始检索结果 | import/github-datasets-survey-2026-08-22/raw_items.json | 532 仓库全字段（含查询归属） |
| 精选+分类 | import/github-datasets-survey-2026-08-22/final_items.json | 544 仓库（含 _main_cat/_noise） |
| 核录结果 | import/github-datasets-survey-2026-08-22/classic_items.json | 40 仓库核录（26 found/13 missing） |
| 检索脚本 | import/github-knowledge-survey-2026-08-22/search_datasets.py | 49 组检索式可复用 |
| 处理脚本 | import/github-knowledge-survey-2026-08-22/process_datasets.py | 分类/精选逻辑可复用 |

---

## 参考资料

1. GitHub REST API（/search/repositories + /repos），2026-08-22 实测，未认证配额 search 10/min + core 60/h
2. 经典数据集核录清单（40 仓库）：The Pile/RedPajama/dolma/MNBVC/CLUE/stanford_alpaca/MedMNIST/ogb/M4/SNAP 等
3. 姊妹文档：2026-08-18-github-knowledge-repos-survey-qa.md（GitHub 知识类仓库全景 v6.0，3690 仓库）
4. 数据集载体认知：HF Hub 承载大规模语料（c4/refinedweb/roots 等 13 个 MISS 实证）
5. RULE.md §6（import/ 素材批判使用）与 MEMORY.md（开源选型三重校验：活跃度+描述+内容）

---

## 素材边界声明

- 本调研数据全部来自 GitHub 公开 API 快照（2026-08-22），仓库参数（星标/语言/许可/规模）为采集时点值，会随时间变化
- 数据集本体参数（样本量/格式/内容质量）未逐仓核读 README，**星标与描述不代表数据质量**——关键选型须回到载体页验证
- 中文语料/爬虫类仓库的采集合规性未评估，引用前须独立审查
- 检索式为关键词组合，**必然存在漏检**（description 不含关键词的仓库）；核录覆盖 40 个已知经典，不保证穷尽

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-08-22 | v1.0 | 首次创建：49 组检索式 × 11 领域 + 40 仓库核录 → 544 仓库全参数（16 字段/仓）+ 领域精选表 + 完整附录 + 5 项合规建议 |
