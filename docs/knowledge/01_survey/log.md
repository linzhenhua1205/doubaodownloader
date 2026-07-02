# 📝 调研跟踪修订记录 `01_survey/log.md`

> **规则说明**:
> - 记录 `01_survey/` 下所有跟踪内容的变更（新增跟踪日志、更新跟踪框架等）
> - 格式：changelog 格式，按时间倒序，条目化
> - 每条条目格式：`- **操作** 📍 `路径` — 说明`
> - 跨域操作（涉及其他顶级目录）请在根级 `log.md` 中记录
> - 本文件不记录文件清单 —— 清单在 `index.md` 中

## 2026-07-01

- **追加** 📍 `cluster-training/2026-07-01.md` — 万卡集群与训推优化动态跟踪（12 条）：Omni-Flow 分布式 KV Cache 跨模态共享 · SeKV 分辨率自适应语义 KV Cache · RaBitQCache 旋转二值量化 KV Cache(ICML 2026) · BlockPilot 样本自适应扩散 SD 块大小 · SMART v2(ECCV 2026) 边际分析 SD 树 · EntMTP 熵引导 MTP 拓扑切换 · LASER 负载感知早退 · LLM 自动 Checkpoint 生成 · StreamGuard 非阻塞 Checkpoint · KV Cache Agent 安全审计
- **更新** 📍 `01_survey/index.md` — `cluster-training/` 文件数 25→26，跟踪日志新增 2026-07-01 前置

## 2026-07-02

- **追加** 📍 `bmc-system/2026-07-02.md` — BMC系统动态跟踪（4条）：bmcweb anti-pattern ast-grep检测规则 · phosphor-user-manager overlayfs预定义组丢失修复 · ARM OEM SSIF能力支持 · dbus-interfaces Redfish Update对齐+UserType枚举

- **追加** 📍 `server-hardware/2026-07-02.md` — 服务器硬件架构动态跟踪（5条）：NVIDIA Vera Rubin NVL4官方首发（7EF AI/5PF FP64/rack, Q4交付）· AMD Versal HBM停产转LPDDR5X（HBM供应枯竭扩散至FPGA生态）· OpenAI Jalapeño Broadcom平台（9个月流片, GPT-5.3跑通）· LineShine Arm纯CPU超算登顶Top500（2.2EF, 80% Linpack效率, 42MW）· Supermicro GB300 Super AI Station拆解（$125K, 1600W液冷, 252GB@7.1TB/s）
- **更新** 📍 `01_survey/index.md` — `server-hardware/` 跟踪日志新增 2026-07-02 前置
- **追加** 📍 `llm-trends/2026-07-02.md` — 大模型动态跟踪（4 头条 + 7 篇 arXiv 精选）：Claude Sonnet 5 发布（Agent 能力接近 Opus 4.8, $2/$10 定价）· Fable 5 全球回归（出口管制解除 + 行业 jailbreak 评分框架）· Google 限制 Meta Gemini 用量（算力短缺蔓延至巨头）· 加州 × Anthropic 全州合作 · arXiv: GPT-5 ToM 超越人类 · CoLT 潜在思维链 10.1×加速 · MRPO 医学推理失败 64%→13% · ERA 视觉 Token 剪枝 33.7% FLOPs 缩减

- **追加** 📍 `product-dev/2026-07-02.md` — 产品管理动态跟踪：AI Agent 三条件决策框架 · AI 实验方法论升级 · AI Builder 新角色范式 · Claude Code 对 PM 影响

- **追加** 📍 `enterprise-mgmt/2026-07-02.md` — 企业管理动态跟踪（12 条）：共识决策在 AI 时代失效 · C-Suite 被 AI 重塑 · 共情领导力与 AI 采纳 · Agentic 收敛陷阱 · 增强 vs 自动化战略分叉 · AI 战略匹配组织现实 · Big Tech 能力悖论 · 哲学领导力 · 文化是硬工具 · 坏摩擦好摩擦 · 自动化消灭职业通道 · Satisficing 跳跃与创新

- **追加** 📍 `ai-apps/2026-07-01.md` — AI 应用动态跟踪：Claude Sonnet 5 发布（Agent 能力平价化）· Fable 5 全球回归 + Anthropic 联合 Amazon/MS/Google 提出行业 jailbreak 评分框架 · Venice AI 以 $65M A 轮成为独角兽（$70M ARR + 已盈利）· Google Gemini Spark 登陆 Mac · Acti 键盘嵌入式 Agent · Cursor iOS 移动端 App · Cloudflare 出版商付费政策 · Trump 解除 Mythos/Fable 限制

- **追加** 📍 `industry-research/2026-07-02.md` — 服务器形态与液冷散热专题（第9节）：Qualcomm HBC堆叠内存+Dragonfly C1000·AMD Versal HBM停产转LPDDR5X·Wiwynn×TE 800V DC液冷母线排工程细节·GB300 1.6kW全液冷工作站两栖形态·五项综合趋势判断
- **追加（第11节）** 📍 `industry-research/2026-07-02.md` — ⚡ 电源架构与供电方案专题（11.1-11.7）：Super Flower Leadex 2800W双全桥拓扑拆解·IEEE Spectrum三联报800V DC供电转向·Lian Li智能化PSU灰尘检测·3000W PSU四厂齐推趋势·AI-HBM-供电正反馈·两级分化研判（消费级3000W逼近ATX极限 vs 机架级800V DC+液冷母线必选）

## 2026-07-01

- **可靠性与测试跟踪更新** 📍 `reliability-testing/2026-07-01.md` — 3 条新论文：ItoyoriFBC 动态SDC复制（<2×开销）·StreamGuard 弹性HPC流（ICS'26, ≤6×, <1%开销）·AI驱动透明C/R代码生成（50min/应用）
- **超节点专题跟踪更新** 📍 `supernode/2026-06-30.md` — NVIDIA Rubin Ultra 取消四芯片设计转向双芯片方案；Lenovo 在 ISC 2026 警告"RAMageddon"已成常态，记忆体市场结构性变化影响超节点 TCO
- **存储部件跟踪更新** 📍 `components-storage/2026-07-01.md` — 三星/SK 896 万亿韩元西南扩产确认；六月 DRAM 合约价 DDR4 月涨 25%；Apple 寻求 CXMT 供应锁定；消费电子全线涨价
- **修复超节点索引链接错误** 📍 `01_survey/index.md` — 超节点跟踪日志链接此前错误指向 bmc-system/ 目录，已修正为 supernode/
- **跟踪追加** ✅ `tools/2026-07-01.md` — Claude Sonnet 5 GA for Copilot/Copilot Agent 进 JetBrains/开源许可证合规 Public Preview/Per-user AI Credit Budgets/Code Coverage Merge Protection
- **新增跟踪日志** 📍 `data-analysis/2026-07-01.md` — Flink 2.3.0（15 FLIP 详析）+ Flink 原生 S3 FS 深潜 (~2× checkpoint, Hadoop-free, SDK v2) + Delta 4.3.0 (UC REST API 范式转换, replaceOn/replaceUsing, UniForm 增量 Iceberg) + Snowflake Cortex Sense/Snowpipe CoCo/Postgres Feature Store + arXiv Text-to-SQL 冲刺 (~20篇综述) + 数据架构论文精读 (Data Lake 15年反思/Hyperparam JS引擎/Bauplan正确性湖仓/Agent技能优化)

## 2026-06-30

- **新增** 📍 `data-analysis/2026-06-30.md` — 数据分析/大数据/数据湖仓动态跟踪：Spark 4.1.2正式发布+4.2.0-preview5·Databricks Lakehouse//RT Reyden引擎·DBCC数据库上下文压缩(2.6M→34.7K tokens)·On-Prem开源LLM T2S BIRD基准(一代胜规模·schema linking不显著)·CADENZA语义查询(SIGMOD 2027)·GRAB多表QA·Trellis Experience Graphs
- **更新** 📍 `01_survey/index.md` — data-analysis 21→22文件，跟踪日志加2026-06-30前置

- **迁移** 📦 `reliability-testing/2026-06-ras-monthly-report.md` → `02_rd/03_hardware/07_ras/` — 月报随 RAS 专题目录重组迁至服务器硬件目录（5个RAS文件集中管理）
- **更新** 📍 `01_survey/index.md` — 月报链接改为指向 07_ras 新位置，保留 reliability-testing 每日跟踪

- **新增** 📍 `cluster-training/2026-06-30.md` — 万卡集群与训推优化跟踪：KernelFlume(core-attention弹性扩展)·HMA-Serve(跨厂牌MemHA PD分离)·工业PD设计空间·HARD-KV(头自适应压缩)·HSAP(混合上下文序列感知并行)·CAEE(成本感知MoE专家剪枝)·KernelSight-LM(跨代GPU推理模拟器)·TraceLab(编码Agent负载特征)
- **更新** 📍 `01_survey/index.md` — cluster-training 24→25文件，跟踪日志加2026-06-30前置；修复22处指向bmc-system/cloud-native/components-storage的错误路径为cluster-training/

- **新增** 📍 `llm-trends/2026-06-30.md` — 大模型动态跟踪：Agents-A1 35B→1T级性能突破(arXiv:2606.30616)·Google限制Meta Gemini用量(基础设施瓶颈)·加州政府-Anthropic Claude合作·OpenAI Codex Micro硬件·Z.ai网络安全对标Mythos 5·MOPD多Teacher在线蒸馏·CORTEX本体语料图·LaaJ鲁棒性评测·临床推理图谱能力无一致性·On-Prem LLM Text-to-SQL五大发现·趋势研判5条
- **更新** 📍 `01_survey/index.md` — llm-trends 19→20文件，跟踪日志加2026-06-30；修复错误路径(bmc-system/→llm-trends/, cloud-native/→llm-trends/)

- **新增** 📍 `ai-frameworks/2026-06-30.md` — AI 框架跟踪：vLLM v0.24.0(571 commits·MiniMax-M3·DSv4成熟化·MRv2量化默认·DeepEP v2·CUTLASS FP8 180-290%加速)·TRT-LLM v1.3.0rc20(TensorRT最后RC!·DSv4准备·MXFP8 W8A8·Marlin NVFP4 Hopper)·SGLang v0.5.14(Waterfill+LPLB·KDA CuteDSL 1.08-1.52×·int8前缀缓存)·Megatron Core v0.18.0(A2A Combine重叠·MXFP8 FSDP)·PyTorch 2.12.1·Triton 3.7.1·8× KV Cache新论文(MemHA异构内存/Coverage驱逐/CompressKV头感知压缩/Nexus概率驱逐/HERALD CPU-GPU/Concordia故障检查点/Dustin投机解码/Cache-Resident LLC)·趋势研判5条
- **更新** 📍 `01_survey/index.md` — ai-frameworks 21→22文件，修复错误链接(bmc-system/→ai-frameworks/)，跟踪日志加2026-06-30
- **更新** 📍 `ai-frameworks/index.md` — 新增2026-06-30条目，移除空行

- **追加大型** 📍 `industry-research/2026-06-30.md` — 电源架构与供电方案专题（第12节，12.1-12.7）：Wiwynn×TE 800V DC液冷母线排(预组装drop-in+机器人装配)·Infineon GaN中国禁令·ATX12VO V3 PMBus标准·Super Flower 2800W评测·GB300 1.6kW液冷工作站·五项趋势研判·Corsair WS3000/$599 · 三星电源PMIC·FERC并网政策·中国GaN判决
- **新增** 📍 `industry-research/2026-06-30.md` — 市场格局动态（第20批）：TSMC 2Q毛利率近70%·3Q营收>+10%·三大厂DRAM集体诉讼·SK hynix/Kioxia ADR赴美·Apple全线提价·Xbox涨价·MLCC每30分钟变价·韩国CO2库存警报·柔佛数据中心40%用电
- **追加大型** 📍 `industry-research/2026-06-30.md` — 服务器形态与液冷散热专题（第10节，10.1-10.3）：AMD EPYC 8005 Sorano 84核Zen 5 SP6同插槽升级(drop-in)·Qualcomm HBC堆叠内存计算(AI250 2027)·Wiwynn×TE 800V DC液冷母线排预组装drop-in+机器人组装新细节·GB300 Super AI Station深度拆解(1.6kW全液冷·5U两栖·双400GbE)·中国42万卡集群强制液冷转型·五趋势研判
- **更新** 📍 `01_survey/index.md` — industry-research 23→24文件，跟踪日志加2026-06-30
- **新增** 📍 `components-storage/2026-06-30.md` — 存储/内存/HBM跟踪：三大厂美国反垄断集体诉讼·SK hynix/Kioxia ADR赴美·通用DRAM利润或超HBM·DDR5 RDIMM $1,335(+4.71%周涨)·Micron 3Q26 87%毛利率·Samsung HBM4营收超$10亿·韩国高纯CO2库存警报
- **新增** 📍 `bmc-system/2026-06-30.md` — BMC/固件跟踪：用户密码过期REST API(安全合规)·ipmid crash loop修复(损坏JSON自动恢复)·TPS25990 HSC固件远程更新(YV5验证)·OEM Chassis链接修复(RSV 766/0/0)
- **更新** 📍 `01_survey/index.md` — bmc-system 20→21文件, 跟踪日志加2026-06-30
- **新增** 📍 `server-hardware/2026-06-30.md` — 服务器硬件架构跟踪：AMD EPYC 8005 Sorano 84核Zen 5 SP6(DDR5-6400·CXL 2.0)·Supermicro GB300 Super AI Station深度拆解(1600W液冷·252GB HBM3e 7.1TB/s·ConnectX-8双400GbE)·Wiwynn×TE 800V DC液冷汇流排(机器人装配·2027实用化)·DIGITIMES GPU/ASIC新平台驱动2H26出货+20%
- **新增** 📍 `product-dev/2026-06-30.md` — 产品管理跟踪：AI Agent决策框架(三条件判断)·AI实验方法论(离线+对抗式+持续监控)·运营模型即产品(Product Partners)
- **新增** 📍 `enterprise-mgmt/2026-06-30.md` — 企业管理跟踪：Rao摩擦管理(好/坏摩擦+时间受托人)·Chatman&Carroll文化作为硬管理工具·Linda Hill创新领导力(创意摩擦结构)·Guilbeault Satisficing(保护混乱空间)
- **更新** 📍 `01_survey/index.md` — server-hardware 22→23文件, product-dev 21→22文件, enterprise-mgmt 21→22文件, 跟踪日志加2026-06-30；修复server-hardware索引路径错误(bmc-system→server-hardware)

## 2026-06-29

- **新增** 📍 `linux-os/2026-06-29.md` — Linux OS跟踪：7.2-rc1发布·allocation tokens+bootpatch-SLR内核加固·OSPM 2026 Day1-3全面报道·writeback提前触发讨论·Podman 6.0发布·Akrites漏洞缓解项目·K8s Headlamp CAPI/Volcano/Knative插件·安全更新
- **新增** 📍 `reliability-testing/2026-06-29.md` — 可靠性与测试跟踪：Varuna(RDMA故障类型感知failover, 65%重传减少)·校正型容错Reduce/Allreduce(理论证明型容错原语)
- **更新** 📍 `01_survey/index.md` — 可靠性测试24→25文件, 跟踪日志加2026-06-29
- **新增** 📍 `cluster-training/2026-06-29.md` — 万卡集群与训推优化跟踪：RolloutPipe(RLVR解耦流水线)·Moebius(MoE运行时TP/EP切换)·CrossPool(冷MoE KV-Cache+Weight分离池化)·CommFuse(通信分解消除尾延迟)·FoE(KV-Head粒度MoE推理通信优化)·FlexMoE(嵌套内剪枝全预算)·边缘云SD理论边界·Cluster-Route-Escalate级联服务
- **新增** 📍 `ai-apps/2026-06-29.md` — AI应用跟踪：Agent吞噬传统应用界面(Claude Tag→Slack队友·Notion Mail关停>50%用户用Agent管邮件·Superhuman收购GPTZero)·AI编程赛道$600亿收购(Cursor→SpaceX)实证Jevons悖论(工程师占新招55%)·Anthropic暂停Agent SDK Token计费+企业管控小任务刷预算·监管重塑格局(Mythos 5仅限100+组织·GPT-5.6逐客户审批)·Google限制Meta Gemini用量现算力瓶颈
- **新增** 📍 `industry-research/2026-06-29.md` — 行业调研：Micron 3QFY26财报($41.46B/毛利率84.9%/净利润15×至$28.24B)·HBM4三星首个$1B·SK hynix $30B Nasdaq ADR(7/10)·Kioxia 857%涨幅/ADR计划2027春·Samsung $648B芯片带投资·Qualcomm+ByteDance定制AI芯片·代工涨价全链传导(TSMC 3nm +15%/MCU/MLCC)·Lenovo 2030高位新常态
- **追加** 📍 `industry-research/2026-06-29.md` — 光互联/CPO/硅光子专题（第5节）：arXiv最新CPO安全(UF硬件指纹)·IMEC 64×100G Si WDM·μTP LiNbO₃ 200mm晶圆级集成(>95%良率)·UW C2PO 400G相干CPO·Intel PIUMA CPO 10年积淀·LC 6月双笔记(Advances in PIC Packaging/AI Reshaping China Optical)·CPO/NPO Conference 7.15预告·9厂商竞争格局表
- **新增** 📍 `bmc-system/2026-06-29.md` — BMC跟踪：bmcweb account_service PropertyValueNotInList参数颠倒修复·TelemetryService单元测试新增·其余来源无更新
- **新增** 📍 `server-hardware/2026-06-29.md` — 服务器硬件跟踪：Qualcomm Dragonfly C1000(250+核@5GHz)·HBC堆叠内存(AI250 2027)·Modular收购对标CUDA·FY29目标$40B·OpenAI Jalapeño(Broadcom/9月tape-out/GPT-5.3)·Intel Nova Lake 52核474W·Loongson 3C3000 16核40W·PCB/CCL供应链趋紧
- **新增** 📍 `components-storage/2026-06-29.md` — 存储跟踪：Lenovo预警高内存"新常态"到2030·Apple/Xbox全线涨价(Xbox 2.5×·iPhone涨价在即)·SK hynix龙仁三层立体Fab 2027年2月冲刺·Micron公开承认CXMT/YMTC进步(差距2-3年/5年)·ASUS PC累计涨30%·DRAM现货/合约价格更新
- **追加大型** 📍 `industry-research/2026-06-29.md` — AI编程/研发工具专题（第7节 6子节）：Cursor 3.7-3.9三连发(Cloud Subagents/Automations/Customize)·Bugbot 3×更快22%更便宜·Auto-review治理(4%阻断)·Notion用SDK嵌入Agent·GitHub Copilot 17项更新(MAI-Code-1-Flash全量/Auto mode开放/Agentic Workflows预览/Copilot for Jira GA/SearchLeak漏洞/定价调整)·Claude Code Token计费暂停·6天5版迭代·JetBrains Central·竞争格局三维争霸
- **追加** 📍 `industry-research/2026-06-29.md` — 服务器形态与液冷散热专题（第8节 8.1-8.5）：Wiwynn×TE 800V DC液冷母线排(8.1)·NVIDIA 45°C高温冷却液近零耗水(8.2)·Supermicro GB300 Super AI Station 1.6kW全液冷(8.3)·Frore LiquidJet Nexus·Supermicro 1,000×绝缘冷却液·CoolIT 4kW冷板(8.4)·6大趋势研判(8.5)
- **追加大型** 📍 `industry-research/2026-06-29.md` — 电源架构与供电方案专题（第10节 10.1-10.7）：Wiwynn×TE 800V DC液冷母线排机器人组装适配新细节·IEEE Spectrum Power Buffer(2026-04)·NVIDIA变电站旁建DC(2026-05)·FERC加速并网·3000W PSU成为AI工作站标配(5+厂商)·US电网容量利用率仅50%·GaN专利战(Infineon被禁)·五大趋势研判·六项跟踪清单

## 2026-06-28

- **新增** 📍 `ai-apps/2026-06-28.md` — AI应用跟踪：Claude Tag上线→Agent进化为团队队友·Mythos 5开放100+美企·SpaceX$600亿收购Cursor(Cursor估值刷新赛道认知)·Anthropic暂停Agent SDK Token计费·企业AI预算刷爆问题浮现·竞争格局更新
- **新增** 📍 `llm-trends/2026-06-28.md` — 大模型动态：NVIDIA Nemotron-TwoTower扩散LM开源(2.42×吞吐/98.7%质量)·SOLAR软token跨语言对齐(+17.7点)·MemStrata消除RAG过时事实(~0%错误率)·ConflictScore量化矛盾证据处理·Mythos 5恢复有限可用·Claude Tag发布·GPT-5.6发布但被限制·趋势研判
- **新增** 📍 `supernode/2026-06-28.md` — 超节点跟踪：Supermicro GB300 Super AI Station 桌面级超节点详细拆解(1600W液冷/$125K)·Wiwynn+TE 800V DC液冷busbar供电架构前瞻(60kW/通道/2027年实用化)
- **追加** 📍 `industry-research/2026-06-28.md` — **第6节 电源架构专题**：6.1 Wiwynn+TE 800V DC液冷busbar(关联supernode)·6.2 Intel ATX12VO V3(PMBus/新连接器)·6.3 IEEE Spectrum DC供电转型专题·6.4 GaN/SiC功率器件(Infineon中国禁售/英诺赛科)·6.5 大功率PSU(Corsair 3000W/Super Flower 2800W)与机架级方案演进·6.6 综合判断(ServeTheHome/Tom's HW/IEEE Spectrum)

- **新增** 📍 `components-storage/2026-06-28.md` — Micron 3Q26 $41.46B 创纪录 + $100B LTA + Anthropic战略合作 + DDR5 RDIMM $1,275 + TrendForce 价格快照

- **新增** 📍 `reliability-testing/2026-06-28.md` — 可靠性测试跟踪：AdaGC自适应梯度裁剪(ICML 2026, spike→0)·SDC生产节点实证(真实SDC硬件, 三验证体系闭环)·SPAM尖峰感知动量重置(1,000×梯度尖峰)·趋势研判：Loss Spike预防成独立研究热点·SDC三验证体系完成·合流成因论

- **新增** 📍 `industry-research/2026-06-28.md` — AI服务器/芯片/云服务市场格局跟踪：涨价潮全链传导·HBM4竞赛分化·代工格局重塑·AI芯片客户争夺（TrendForce/DIGITIMES多篇）
  - **追加** **AI研发工具动态跟踪**：Cursor 3.7→3.9三连发·SpaceX$600亿收购·GitHub Copilot 17+项更新(MAI-Code-1/Agent/安全)·Copilot SearchLeak漏洞·Claude Code 6天5版·JetBrains Central发布·市场格局分析（Cursor Blog/GitHub Changelog/Ars Technica/TechCrunch）

- **新增** 📍 `product-dev/2026-06-28.md` — C-Suite被AI重塑(HBR)·AI扼杀组织DNA(HBR)·员工不质疑AI建议(HBS)·管理者角色=目的设定而非预测(Stanford GSB)

- **新增** 📍 `enterprise-mgmt/2026-06-28.md` — C-Suite与董事会全面变革(HBR)·共情领导力决定AI落地(HBR Stanford)·AI摧毁竞争力·组织DNA保护策略(HBR)·刻意无知传染风险(HBS)

- **新增** 📍 `server-hardware/2026-06-28.md` — 服务器硬件架构跟踪：IBM Nanostack sub-1nm CFET晶体管·Arm服务器收入>45%·Qualcomm HBC内存堆叠·800VDC液冷Busbar·Supermicro GB300 DGX Station拆解

## 2026-06-27

- **新增** 📍 `linux-os/2026-06-27.md` — Linux稳定更新(7.1.2/7.0.14/6.18.37)·systemd v261·OSPM 2026 day 3·etcd 3.7.0-beta.0·K8s AI时代开源维护讨论

- **新增** 📍 `cluster-training/2026-06-27.md` — 万卡集群与训推优化跟踪：Piper可编程训练框架/Meta ScaleAcross跨DC训练/跨厂商Comm-Overlap/协作式CoSpec SD/S3对象存储KV Cache/FP16 KV Cache非等价性/Agent Serving三系统/双池Token Budget路由

- **新增** 📍 `llm-trends/2026-06-27.md` — GPT-5.6 发布(Sol/Terra/Luna) + Mythos 5 恢复有限可用 + Nemotron-TwoTower 开源扩散LM + arXiv精选8篇

- **跟踪追加** 📍 `ai-frameworks/2026-06-27.md` — **AI框架全面跟踪**：vLLM v0.23.0 (CUTLASS FP8 +20%/MoE-permute +9-14%)·SGLang v0.5.14 (DSv4 on GB300 5×/KDA 1.52×/LPLB)·TRT-LLM v1.3.0rc19·PyTorch 2.12·DeepSpeed v0.19.2 AutoEP·Triton 3.7 gfx1250·PersistentKV 1.4×·Cache-Resident LLM 11.5×
- **跟踪追加** 📍 `industry-research/2026-06-27.md` — 芯片/服务器/云服务市场格局动态：NVIDIA $4.66T市值·OpenAI GPT-5.6 + Jalapeño芯片·Anthropic Mythos 5受限+Claude Tag·Micron 3QFY26净利润暴增15×/毛利率84.9%/HBM4>$1B·AWS GPU涨价·Onsemi $7B收购Synaptics·Groq $650M·CXMT IPO·Samsung 2027年HBM领先·Oracle裁21K·DRAM 2027>$1.28T·AI ROI质疑升温
- **跟踪追加** 📍 `industry-research/2026-06-27.md` — **光互联/CPO/硅光子专题追加**：Marvell COMPUTEX 2026光互连战略·黄仁勋钦点"下一家万亿美元公司"·1.6Tbps 2nm相干光学2026H2送样·CPO 51.2T交换机展示·"铜墙"理论(200Gbps/2.5m)·$20亿NV投资·收购Celestial AI光子互连·LightCounting硅光模块份额2026年首超50%·CPO 2030年$100亿·Broadcom/NVIDIA 2026年CPO产品·Intel EMIB硅桥

- **跟踪追加** 📍 `industry-research/2026-06-27.md` — **电源架构与供电方案动态追加**（专题④双周更新）：800V HVDC加速·NVIDIA Rubin平台引领·Lite-On MW级AI工厂·GaN/SiC跨界渗透·Dynapack/AES BBU产能加倍·Intel ATX12VO V3发布·Power Buffer保护电网·Onsemi $7B收购Synaptics智能功率半导体·被动元件传导效应
- **跟踪追加** 📍 `tools/2026-06-27.md` — 研发工具跟踪：Cursor 3.9 Customize 统一管理页面 · v0 Platform API v2 + Annotations Mode · GitHub Actions 并行 Steps · GitHub Desktop 3.6 Worktrees · Copilot Code Review 效率更新 · MAI-Code-1-Flash 扩展至 Business/Enterprise
- **跟踪追加** 📍 `components-storage/2026-06-27.md` — DDR4重启生产(重返DDR4时代)·PCIe 6.0 SSD控制器竞赛(SMI 2027消费级/Phison 28GB/s 12月采样)·Lenovo预警高内存价格到2030·Samsung HBM4或涨2.5×·Kioxia Apple超级周期·Micron $100B LTA

- **跟踪追加** 📍 `server-hardware/2026-06-27.md` — NVIDIA Vera Rubin全面投产(88核/3nm)·IBM Nanostack sub-1nm(7Å/2×密度)·AMD EPYC Venice GX5000(81920核/rack)·Intel Xeon 6 SoC DPU(36-38核/200G)·ASUS 9U 8×B300服务器评测

- **跟踪追加** 📍 `product-dev/2026-06-27.md` — Claude Code for PM·AI Agent自治预算框架·Big Tech能力危机·Satisficing学习原理(Stanford GSB)
- **跟踪追加** 📍 `enterprise-mgmt/2026-06-27.md` — 领导者哲学素养(HBR)·AI Agent重塑知识工作组织(Stanford GSB)·能力危机反向信号(HBR)·满足化智能保护
- **跟踪追加** 📍 `bmc-system/2026-06-27.md` — phosphor-host-ipmid: corrupt user JSON crash loop修复·bmcweb OEM schema Chassis属性修复·OpenBMC v2.18.0稳定(无2.19)

## 2026-06-26

- **跟踪追加** 📍 `rd-management/2026-06-26.md` — Cursor 3.9 Customize统一管理+Plugin Canvases·Claude Code 33版本密集更新(Fable 5/Agent Teams/MCP CLI/企业治理)·Claude Agent for Jira发布(400组织研究·10-15% plateau)·Atlassian PM:Eng 1:4·Design Mode Multi-select+Voice
- **跟踪追加** 📍 `linux-os/2026-06-26.md` — Akrites漏洞修复项目·Podman 6.0·Git 2.55·RHEL Agent Skills·containerd多发行版安全更新
- **跟踪追加** 📍 `reliability-testing/2026-06-26.md` — DiffCp差分检查点(89.2%时间减少)·Lazarus MoE弹性容错(5.7×)
- **跟踪追加** 📍 `industry-research/2026-06-26.md` — ① Moebius运行时TP/EP切换·BOM成本跟踪·电源架构动态
- **跟踪追加** 📍 `industry-research/2026-06-26-domestic.md` — 国产替代跟踪（CXMT上市·平头哥注资等）
- **跟踪追加** 📍 `ai-apps/2026-06-26.md` — Claude付费+75%·Patronus AI $50M B轮
- **跟踪追加** 📍 `ai-frameworks/2026-06-26.md` — 新增
- **跟踪追加** 📍 `llm-trends/2026-06-26.md` — 新增
- **跟踪追加** 📍 `cluster-training/2026-06-26.md` — Moebius服务TP↔EP切换等
- **跟踪追加** 📍 `data-analysis/2026-06-27.md` — 新增
- **跟踪追加** 📍 `data-analysis/2026-06-26.md` — 新增
- **跟踪追加** 📍 `tools/2026-06-26.md` — 新增
- **跟踪追加** 📍 `ai-solutions/2026-06-26.md` — Amazon 🇮🇳 $13B AI云投资·Samsung $6480亿芯片计划·能源约束·Oracle债务融资模型

## 2026-06-25

- **跟踪追加** 📍 `rd-management/2026-06-25.md` — Cursor 3.8 Automations · Linear Agent · Copilot等
- **跟踪追加** 📍 `data-center/2026-06-25.md` — Lotus垂直供电 · Qualcomm HBC · NVIDIA 45°C液冷
- **跟踪追加** 📍 `industry-research/2026-06-25.md` — §⑤-§⑧ AI工具·BOM供应链·电源架构·服务器形态
- **跟踪追加** 📍 `industry-research/2026-06-25-interconnect.md` — 互联与光通信跟踪
- **跟踪追加** 📍 `industry-research/2026-06-25-domestic.md` — 国产替代跟踪
- **跟踪追加** 📍 `ai-apps/2026-06-25.md` — OpenAI Jalapeño芯片·Figma Code Layer
- **跟踪追加** 📍 `llm-trends/2026-06-25.md` — 13条大模型动态
- **跟踪追加** 📍 `cluster-training/2026-06-25.md` — 新增
- **跟踪追加** 📍 `product-dev/2026-06-25.md` — HBR/Product School产品管理跟踪
- **跟踪追加** 📍 `components-storage/2026-06-25.md` — HBM4三厂分化·SK hynix $29B
- **跟踪追加** 📍 `supernode/2026-06-25.md` — Qualcomm Dragonfly · LineShine LX2
- **跟踪追加** 📍 `tools/2026-06-25.md` — JetBrains Central · Claude Agent for Jira
- **跟踪追加** 📍 `cloud-native/2026-06-25.md` — 新增
- **跟踪追加** 📍 `linux-os/2026-06-25.md` — 新增
- **跟踪追加** 📍 `project-mgmt/2026-06-25.md` — 新增
- **跟踪追加** 📍 `enterprise-mgmt/2026-06-25.md` — AI重塑C-Suite · 共情领导力

## 2026-06-26（追）

- **跟踪追加** 📍 `project-mgmt/2026-06-26.md` — Linear「Issue tracking is dead」范式迁移·Coding Sessions全流程闭环·Auto-fix bug·Claude Agent for Jira编排层·400组织研究10-15%天花板·Ramp 60%+ Agent PRs

## 2026-06-24

- **跟踪追加** 📍 `ai-solutions/2026-06-24.md` — $1,300亿DC项目被阻·Oracle裁员
- **跟踪追加** 📍 `cloud-native/2026-06-24.md` — OTel Don't Wrap · Jaeger v2.18 ClickHouse
- **跟踪追加** 📍 `ops-system/2026-06-24.md` — K8s v1.36 PSI GA · Linux 7.2 · Systemd v261
- **跟踪追加** 📍 `linux-os/2026-06-24.md` — OSPM day two · KASAN for BPF · Jaeger ClickHouse
- **跟踪追加** 📍 `industry-research/2026-06-24.md` — §⑥-§⑧ 服务器形态·BOM·电源架构
- **跟踪追加** 📍 `industry-research/2026-06-24-interconnect.md` — Opus OCS · 3D CPO · 光纤抖动
- **跟踪追加** 📍 `industry-research/2026-06-24-domestic.md` — 国产替代跟踪
- **跟踪追加** 📍 `product-dev/2026-06-24.md` — AI Builder 56%工资溢价 · Autonomy Budget
- **跟踪追加** 📍 `supernode/2026-06-24.md` — TOP500 · LineShine登顶 · Vera Rubin NVL4
- **跟踪追加** 📍 `supernode/supernode-standards.md` — UALink 2.0·CXL生态·JEDEC LPDDR6
- **跟踪追加** 📍 `enterprise-mgmt/2026-06-24.md` — C-Suite被AI重塑 · 共情领导力
- **跟踪追加** 📍 `tools/2026-06-24.md` — 新增
- **跟踪追加** 📍 `llm-trends/2026-06-24.md` — Claude Tag · Superhuman收购GPTZero

## 2026-06-23

- **跟踪追加** 📍 `rd-management/2026-06-23.md` — Cursor /automate · Linear 30% Bug修复
- **跟踪追加** 📍 `linux-os/2026-06-23.md` — BPF协程化 · OSPM 2026 · systemd v261
- **跟踪追加** 📍 `cloud-native/2026-06-23.md` — AI Agent Auth · Jaeger ClickHouse
- **跟踪追加** 📍 `ops-system/2026-06-23.md` — K8s v1.36 PSI GA · Pod-Level RM
- **跟踪追加** 📍 `industry-research/2026-06-23.md` — §⑦BOM成本 · §⑧电源架构 · 芯片动态
- **跟踪追加** 📍 `industry-research/2026-06-23-interconnect.md` — Marvell CPO · TSMC COUPE
- **跟踪追加** 📍 `industry-research/2026-06-23-domestic.md` — 国产替代跟踪
- **跟踪追加** 📍 `supernode/supernode-standards.md` — 超节点标准第17次跟踪
- **跟踪追加** 📍 `cluster-training/2026-06-23.md` — 新增
- **跟踪追加** 📍 `ai-apps/2026-06-23.md` — 新增
- **跟踪追加** 📍 `llm-trends/2026-06-23.md` — 新增

## 2026-06-22

- **跟踪追加** 📍 `cluster-training/2026-06-22.md` — SAC CXL碎片化KV Cache · UltraQuant
- **跟踪追加** 📍 `industry-research/2026-06-22.md` — 国产GPU深度调研·电源架构第1期
- **跟踪追加** 📍 `ai-solutions/2026-06-22.md` — SK Hynix市值$1.35T·DC冲突升级
- **跟踪追加** 📍 `ai-frameworks/2026-06-22.md` — 新增
- **跟踪追加** 📍 `llm-trends/2026-06-22.md` — 新增
- **跟踪追加** 📍 `tools/2026-06-22.md` — 新增
- **跟踪追加** 📍 `project-mgmt/2026-06-22.md` — 新增

- **跟踪追加** 🤖 `industry-research/2026-06-27.md` — AI研发工具动态专题（Cursor 3.7-3.9/SpaceX收购/GitHub Copilot/Claude Code/JetBrains Central）
- **跟踪追加** 📍 `reliability-testing/2026-06-27.md` — AIReSim集群可靠性模拟器·Ampere GPU内存错误67.77M GPU-小时实证·LLM Checkpoint I/O liburing优化
- **跟踪追加** 🖥️ `industry-research/2026-06-27.md` — 服务器形态与液冷散热动态（Wiwynn 800V DC液冷母线排/NVIDIA 45°C高温冷却液/MGX歧管标准化/IcePack液冷网络机柜）

- **跟踪追加** 📍 `project-mgmt/2026-06-27.md` — Agent 生产数据（Linear 30% bug auto-fix）· AI-native SDLC 量化（+19% PRs, 2-3h/wk/dev）· @Jira Slack · Knowledge Architect

## 2026-06-17 ~ 2026-06-03

（此期间每日跟踪日志持续追加，涵盖 18+ 跟踪主题。详细记录请参考各子目录的 `YYYY-MM-DD.md` 文件）

- **跟踪追加** 📍 `project-mgmt/2026-06-28.md` — Cursor in Jira深度集成（Jira→Agent编排层）· AI坦诚悖论（10×懒-hi感知/-24pp推荐率）· 44%/48%上下文质量量化 | 2026-06-28
- **跟踪追加** 📍 `cluster-training/2026-06-28.md` — FoMoE联邦MoE训练/DMuon分布式Muon优化器/Epiphany-Aware免注意KV驱逐/Concordia推理容错Checkpoint/JetSpec并行树SD/ReMP运行时TP-PP重配/LUMEN协调恢复/SAC+CXL稀疏KV Cache/Serialized Bridge GPU机密计算性能根因/Cache-Resident LLM推理 | 2026-06-28
- **跟踪追加** 🧠 `tools/2026-06-28.md` — Copilot for Jira GA · Copilot CLI 新终端GA · Agentic Workflows Public Preview · BYOK+JetBrains Claude · GHES 3.21 | 2026-06-28
- **跟踪追加** 📍 `linux-os/2026-06-28.md` — BPF libarena库·KASAN for JIT BPF·K8s Device Management WG·K8s AI政策+CodeRabbit·Red Hat AI安全悖论·CXL无进展 | 2026-06-28

## 2026-06-29

- **跟踪追加** ✅ `product-dev/2026-06-29.md` — AI运营模型断层80%/AI Builder新角色/Satisficing学习机制/Claude Code for PM | 2026-06-29
- **跟踪追加** ✅ `enterprise-mgmt/2026-06-29.md` — AI让员工停止质疑传染风险/竞争DNA被AI侵蚀/增强vs自动化分叉路/Satisficing管理启示 | 2026-06-29
- **跟踪追加** 🧠 `ai-frameworks/2026-06-29.md` — TRT-LLM v1.3.0rc19·Triton 3.7·10× KV Cache论文(SAC CXL分解/AsymCache/CacheTune/OCTOPUS/Still/ObjectCache/PolyKV/ITME/Albireo超越Amdahl/RTP-LLM Alibaba)·DeepSpeed v0.19.2 Muon+AutoEP·PyTorch 2.12加速器Graph统一 | 2026-06-29
- 2026-06-30 | `tools/2026-06-30.md` | Cursor iOS App · Claude Opus 4.8 Fast in Copilot · Actions Read-Only Cache
- **跟踪追加** 📍 `reliability-testing/2026-06-30.md` — TRANSOM 工业级三引擎容错训练系统(20×CKPT, 28%时间减少)·GoCkpt 多步重叠检查点(38.4%吞吐·86.7%中断减少)·ECRM 纠删码替代检查点(88%开销减少·10.3×恢复·恢复期继续训练)·趋势研判：检查点六层+一替代完备格局·工业级容错四系统对抗·检查点优化vs替代两派分化

- 2026-06-30 | `rd-management/2026-06-30.md` | Cursor 3.9 iOS App · Atlassian Cursor in Jira + Teamwork Graph · GitHub Copilot HyDRA 路由引擎 · HBR AI建议抵触/能力悖论 · Claude Code classifyAllShell+CPU降37% | 2026-06-30

## 2026-07-01

- **跟踪追加** ✅ `product-dev/2026-07-01.md` — AI Agent自治预算框架(24维打分表)/C-Suite角色被AI重塑/产品启示：CPO→AI运营模型设计者 | 2026-07-01
- **跟踪追加** ✅ `linux-os/2026-07-01.md` — Secure Boot证书到期(MS KEK)·容器安全更新潮(Podman/Buildah/Runc)·Red Hat Agentic AI on OpenShift·Ansible Automation Platform 2.7 执行层定位 | 2026-07-01
- **跟踪追加** ✅ `rd-management/2026-07-01.md` — Cursor Team MCPs + Organization Groups 企业治理·Claude Sonnet 5默认模型(原生1M上下文)·Claude Code 2.1.196代码审查token降25%·HBR $7.37B市场(资深开发者更贵)·HBR能力悖论(AI减成本→需求激增)·Knowledge Architect新角色 | 2026-07-01
- **跟踪追加** ✅ `supernode/2026-07-02.md` — NVIDIA Build in America $500B AI制造/Rubin 100%液冷+零水耗/AMD Versal HBM→LPDDR5X被迫转向(HBM供给危机外溢) | 2026-07-02
