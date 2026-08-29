# 🗄️ MEMORY.md 深度洞察归档（2026-08-14 迁移）

> **类型**: archive | **日期**: 2026-08-14 | **来源**: MEMORY.md 全文迁移（原 24KB → 压缩至 5KB 规则）
> **背景**: 2026-08-14 用户规则「MEMORY.md 控制在 5K 以内，超额写入 Candidate.md，未经人工统一不再持续修改」。本文档为 MEMORY.md 原「深度洞察」三大块全文归档，供知识库检索使用；MEMORY.md 中仅保留一行指针。

---

## 一、深度洞察：AI 与 Agent（原 MEMORY.md §3）

- Agent编排：三大云架构趋同+MCP/A2A事实标准+Agent Plugins 1.0.0五巨头；否定路由式多代理；任务形状决定范式（窄深→单循环/宽浅→多代理）；推理成本第一杠杆（多代理15×vs单循环4×token）；五机制=flattened tools/渐进披露/context compaction 95%水位/child instances/分层prompt+前缀缓存；六层=Prompt→Loop→工具面→Skills→编排→Channel；agent产出信任链=可追溯→可审查→可审计；Salami共谋投毒81.3%
- 模型格局：Opus 5=61/GPT-5.6=59/Kimi K3=57（开放权重第一2.8T MoE）+vllm K3双栈深耕（AMD packed KDA kernel+AITER MLA fp8 KV，v0.27一日双发）；1M上下文标配；模型厂商全面芯片化（GB300预训练1,648 TFLOPs世界纪录）；边缘/本地未定论=Muse Glimmer 30B dense（120K ctx单卡>20K tok/s）vs Nemotron 3.5 Lightning 30B MoE/3B active（NVFP4+Bf16跨三代）官方同周对打；消费级MoE三维量化=RotaryQuant（dense 4-bit/路由2-bit/共享8-bit+LRU换页，arXiv 2608.08081）
- 可靠性测试：Resume契约五大框架全违反；FT-HSDP=10万GPU 18min故障×10min恢复44%→80%；恢复时延秒级赛（FlashBoot/Concordia）；KV分层迁移主旋律（HiSparse→OasisKV→ImpactHO）；共享GPU池隔离（MPS→ElastiCo→eIRWR）；容错走向机器可证明；Cascade SLO预算会计+B=S_TTFT−L+JFI六分位；调度范式→goodput（Cascade→MARS→TideRL）；**发布规律=Mon→Thu批次当天可见（连续四日验证）；Ray GCS Active-Passive 2.1+PyTorch c10d watchdog纯Python化=控制面/故障检测双线**
- LLM推理统一框架：四类冗余MECE（时间/IO/空间/计算），稀缺排序HBM带宽>容量>FLOPs>CPU；量化锚点=Orca/FlashAttention/vLLM/SGLang；Prefix Caching使system prompt稳定性转化为成本；KV搬家320KB/token线性；调度三级=排队器→编排器→HorizonServe/TAOT/PrefixPlace；MARS=MCTS前瞻调度=「调度器=目标优化器」范式信号；旋转×量化三支柱=OptR/GyRot/LightRot（同团队同日=学术范式确认）；池化内存NDP（PLoRA）；ViBE=token均衡≠延迟均衡；TensorCast=控制/数据面分离第三次落地
- 记忆研究：MindMemOS=Dreaming离线整理压缩19.4-23.5%+Skill Evolution蒸馏51.3→57.2%；Personalization Mirage=12/12模型OI 35-49%（本系统44.6%）；When Memory Lies=文本可解≠视觉落地（F1 0.887→0.067）；落地三层证据标注+四态生命周期+对抗OI五项机制G1-G5；可证伪预测H1=2026-12失真审计OI率<15%
- AI编程平台：平台从生成工具→交付系统、组织三权（判断/预算/集成）回收；Cursor Router（Compass预测器-68%成本）；JetBrains LSP=N×M→N+M；计量制→治理制；Live Tool-Call Durations=L0 turn→L1 duration_ms→L2 Task→L3三原则，MTTR数量级提升；**Agent五项技术突破=智能从prompt工程转向可进化系统工程（MOSS/FlowCompile/SIA）**
- Agent安全：越权→失控→假身份+UK AISI评估+能力管制（OpenAI停发Astra）+攻击逃逸测试（SANDBOXESCAPEBENCH/COBALT/OverEager）；授权语义SDK级（approval绑定调用+hosted MCP identity）；StepJack多步间接注入（CUA ASR +31.2、PID单步56.2%→多步22.9%）；vllm DoS修复+--api-key不gate所有端点警告=安全面扩至多模态/配置侧
- 决策方法论：条件命题=工程目标可达成依赖条件状态表；确定性制造=验证是唯一把可能性变确定性的操作（概念20-30%→验证90-99%）；AI协作协议=分层结论+依赖清单+置信度+验证路径（禁止裸断言）；快速路径=四维风险R=f(P,I,T,D)+六准则；防护通胀S曲线（少而严优于多而松，解药=检查自动化）
- Agentic AIOps：AIOps从分析引擎→执行引擎；Dynatrace crawl-walk-run信任阶梯；成功度量=永远不需要人的incident%；2027自主SRE元年；SkillProx=合成→演化→RL+τ=-0.001负效用+OOD 78.5/69.2；Agora=CPU收割0.74/GPU释放1/3+82%尾延迟（CORAL反噬−71%=盈亏边界）；共享"全局分配"第一性原理；**Agent负载颠覆平台假设（Aries：token指标漏检/上下文收益递减/sandbox空闲-突发）——Aries×CNCF同证可观测性缺口**
- AI产业四重门禁（08-10）：安全（Astra放缓+评估沙箱失控四例+Anthropic红队入侵三企业）/成本（Rippling自建ROI）/财务（Mirendil×GCP $100M+）/物理（TSMC CoWoS外包+Rubin降配+昆仑芯锁定+3300万吨CO₂）——从无限扩张进入约束优化；组织变革4C=Cortex×Alignment（未对齐拒绝立项）×Narrative×Closure；可观测性=观测权=认知塑造权
- 模型侧降本三路径=路由→稀疏化→专用化（嵌套非并列）；$/token三因子分解；GPT-5.5 $30/M vs DeepSeek V4 <$1/M（30×价差=中国模型占美企token 30%纯经济行为）；Inkling=975B/41B；Trainium $25B≈NVIDIA DC 13%；Frozen v2"模型进硅"时差（2028流片固化2027模型）；可证伪预测P1-P6
- AI悖论双生：工具时间占比稳定25-35%；knowledge 1065→2718→3085但素材层占79.4%；统计铁律=A/M/R/D由用户聚合+AI自报收益不可靠（仅31%测量）；AI产出=毛利非净利；约束脚本化=最高杠杆；AI变更四维耦合C=0.40
- 幻觉/注意力/理解三姊妹：幻觉=数据→训练→推理缺陷乘性累积（答非所实）；注意力=零和博弈、检索头<5%、剪除致幻觉（答非所依）；理解=统计相关表面加工（答非所悟）——三层失配框架

## 二、深度洞察：存储与基础设施（原 MEMORY.md §4）

- 存储行业+FMS：2026产值$803.9B首超逻辑；字节KV卸载batch+30%/GPU需求-87%；大普微R6060 512TB；三星路线图=V10 BV-NAND 400+层/zHBM垂直堆叠/HBM4E/HBM5/LPDDR5X-PIM；**YMTC首进NAND前三（AI消耗48%闪存，三星25%/SK 22%）、SK海力士中国扩产+50%&Solidigm IPO、Intel CEO暗示重返存储（CPU堆叠）**；DRAM涨价5×→CXL对冲；HBM定制化或脱周期；闪存内存化四路（HBF/zHBM/CXL池化/光内存）；KV SSD新三围=512B IOPS+有效DWPD+FDP流数；cuFile开源；U.2→EDSFF；G3.5分层温存储；液冷→DLC；PQC+TDISP
- 超级周期实证：Sandisk FY26 $20.25B/+175%、Phison 2Q26 NT$67.9B/+280%、Micron 3Q26 $41.6B/+347%、WD FY26 HDD+44%；涨价2/3+AI 1/3、已传导消费端；价值迁移三阶段=容量→架构→生态（②→③过渡）；$500B TAM批判→$380-420B中性基线
- 供应链约束+规格改写：2026史上首次八线同紧（GPU+HBM/DRAM+NAND+CPU+封装+MLCC+光模块+电力）；传导链=HBM挤DRAM→涨价→CXL→闪存→NAND→BOM全升；波浪式缓解=MLCC/NAND先、晶圆/封装/HBM后（2026H2-2027峰值）；规格改写C1-C3+T1-T5（Rubin Ultra 192GB降配=实证2、昆仑芯锁定腾讯至27年底=实证3）；Geoff Tate四大瓶颈=Foundry/存储/供电/激光；杰文斯悖论=效率是增长引擎非解药；退潮论2028-2030无模型支撑
- 超节点/互联+HVDC：Vera Rubin NVL72（NVLink6 3.6TB/s·GPU，**鸿海Q4量产确认+8层HBM4+10x Agent吞吐**）；Firebird亚美尼亚（>70K GPU/300MW）；DSX首次落地（footprint +40% GPU）；NVIDIA×六大机构$500B算力融资=算力资产化（MoU，"compute is revenue"）；xAI过剩产能变现（Anthropic $45B/220K GPU）；800V=GB200 54V验证（2222A vs 5280A容量利用率84%自洽）、40kW→1MW约4年25×、Kyber 576=NVL576域级；**8/11官方定调=NVIDIA+Google+Microsoft三方OCP（LVDC白皮书3月+SST Spec v0.3 7月80+厂商）、三阶段=Power Sidecar 2026H2→Row Power Center 2027→DC Power Block、纳入DSX reference designs；$500B口径澄清=非收入/非单一基金、H100租赁$1.70→$2.35/B200 $5.30-7.05、25%残值**；九道门G5唯一红灯；散热=GoCool-150 CDU桥接旧设施（自耗18kW排150kW≈12%开销）
- 1MW机架+光进铜退：**Mount Diablo=Google/Meta/MS OCP统一液冷/供电、±400V DC（借电动车产业链）；机架功率20年4kW→250kW→1MW；GPU峰值电流→本十年末10,000A（I²R平方律）；agentic=持续峰值功耗设计（不再按average）；Ayar Labs公开反对1MW=光scale-up至500K GPUs/10×200kW架；市场窗口1年/spec 1.5-2年；Synopsys：1MW架必经3D-IC die堆叠**；旧规则"scale-up=铜/scale-out=光"瓦解、新术语scale-in（单机箱GPU带宽）；200G铜上限5-7m、>10m必须光；scale-up保留定义=memory semantics；UALink跨机架仍单switch-hop（ToR/MoR）；Google torus+OCS vs leaf-and-spine；GPU效率~25%；Synopsys线性112G PHY（去DSP省50%模块功耗，LPO=CPO前置台阶）
- CPU故障/NCCL/HBM测试：存储四形态模型——没有任何形态完全存活；KV四层命运=L0 HBM/L1 CPU DRAM/L2持久/L3 checkpoint；训练"暂停等恢复"vs推理"快速失败+请求级重调度"；NVMe新动向=PQC/PCIe-exported NVM/电压遥测；假存活陷阱=监控看命令完成率/队列深度；NCCL假存活案（marin#7344）=死锁GPU 100%util+功耗冻结小数两位+SM时钟钉死→power.draw双采样5判据；watchdog=应用>框架>系统；根因=NCCL 2.28.9 proxy-op slot泄漏→国产ARM移植须ISA级验证；验证实际加载物=/proc/self/maps；HBM成3D组装良率测试试验场（HBM5 24层/微凸点<40µm→BiST+监控+冗余修复、in-system testing=walking wounded lane）
- KV缓存体系：`KV=2×L×D_eff×dtype×batch×seq`；每token KV=512KB(7B MHA)/128KB(8B GQA)/320KB(70B GQA)/137KB(V3 MLA)；主导权切换点T_cross=W/k（8B@131K/70B@452K/V3@10.3M——模型越小上下文越长KV越关键）；三场景=容量/吞吐/结构驱动；HiSparse合入SGLang（Qwen Quest GH200 200K 4.7×、每请求KV 13.09GB→0.4GB≈30×）；闪存级KV卸载实证（Dell XE7740+Solidigm D7-PS1030：峰值2.9×/2.2×、持续30K tok/s闪存94% vs 17K DRAM 42%、首token 13.9s→3.2s、Claude Code一周98.16%缓存读取、RAID10 3.2 DWPD/RAID0 1.6——决定性限制=耐久性非容量）；CoreWeave×Solidigm LTA=闪存成继GPU后第二个需提前数年签约组件；GB300 Grace ~480GB≤GPU HBM（P0=host DRAM≥8×GPU HBM）；decode带宽瓶颈→PD分离必要性；KV全量读超CXL/SSD带宽（128K×20=838GB/s vs CXL 64GB/s）→依赖注意力稀疏性
- AMD+国产化：Helios Q3 2026出货（72×MI455X=2.9 EFLOPS/31TB HBM4/1.7PB/s；CPU:GPU 1:4 vs NVIDIA 2:4）；**MI455X/CDNA 5单卡=TSMC N2 320B晶体管+72%、FP4/FP8 4×>40 PFLOPS、12堆HBM4 23.3TB/s/432GB、UAL 3.6TB/s聚合、>2kW/卡、Helios 245kW/4GPU tray、数据中心占AMD营收>50%**；CPU路线图=Zen7三家族2028/EPYC 9006/Default 400W vs Vera 450W、Intel Diamond Rapids推迟2027；国产化=长鑫LPDDR6 2026H2全球首发+DDR5进品牌PC、麒麟X90 Plus、CXL 3.2；国产AI芯片财报=摩尔线程H1 17.36亿+147.42%（毛利56.95% vs 爱芯元智29%）；CXMT 2030 30%=晶圆非比特（实际17-20%）；供应链三阶段渗透+采购分层地缘政治；资本三层模型=「合肥模式」；根节点=MATCH Act晴雨表
- DPU/互联/IPU：三大数据平面范式=软件(Arm核,Intel E2100 200G封顶)/固定硬件+可编程旁路(BF3 400G AI原生)/P4可编程流水线(Salina400 232MPU)；内存指纹48GB/16GB/128GB；三家中走向=Intel Xeon 6 SoC弃独立ASIC（修正：E2100实为Arm ASIC）、NVIDIA BF4 800G、AMD Helios前端+Vulcano；国产DPU=6创业+4云大厂、无护城河落后1代；产品规划=不自研芯片三路径（独立DPU/Soc集成/软件栈）；UALink白皮书=契约前置哲学（128PB统一地址空间）；互联成本$15-25M占15-25%
- 推理GPU竞争：Intel Crescent Island=容量型赛道（LPDDR5X 160GB风冷、规避HBM危机；官方口径160GB vs 中128GB）；三线=Intel容量/AMD scale-up/NVIDIA通吃；斯坦福AI指数2026=算力年增3.3×/NVIDIA 60%+/$581B；CPO测试三大缺口（连接器/STDF/ID可追溯）+NPO 12-18月/CPO 18-24月、Lightmatter+OCP开放设计1000万unit/年
- 本地推理小模型：8GB卡=Qwen2.5-7B INT4+32K可行~7.2GB（Qwen2.5无8B，真身Qwen3-8B但仅4-8K原生、128K宣传值不可达KV 7.5-19.3GB）；RTX 5060=GDDR7 448GB/s→8B decode 75-85 tok/s、FP4~109 tok/s、与5060 Ti同带宽=买容量非速度；Windows"16GB"=8GB专用+8GB共享WDDM分页（PCIe 5.0 x8单向31.5GB/s=显存1/14→上限6.7 tok/s）、CUDA OOM而DirectML/LM Studio静默溢出；正确姿势=CPU offload（CPU内存带宽50-80GB/s比PCIe快）；量化检测四层法+铁律≥2独立信号；FP8仅~240有限值易误判int8、BF16=非量化；GGUF实际大小高20%+

## 三、深度洞察：行业、方法与事件（原 MEMORY.md §5）

- 用户四重角色：系统架构9.5/AI协作9.5/深度调研/知识库治理，项目管理7.0需补强；偏工程化治理=方法论→Skills+脚本；README v4.1实测（08-12）=import 18,895/skills 96本地+33外部/scripts 256+220备份/spec 47文件/scheduler 49任务/git 1,374 commits/仓库9.3G；**index.db schema（08-13）=sessions 251/messages 85702/files 11311/chunks 130814、channel_type 83.3%空（209=scheduler_）、真实用户42（web 40+feishu 2）——上轮feishu 205/web 77口径需澄清；分析须过滤scheduler_前缀+COUNT(*)禁MAX(id)；user-questions v2=全量1937条/9列**
- 容量型SKU五看三定：总纲=5含义→5执行线+五条件C1-C5；国际版=战略TCO/token≤HBM机型1/2、最大威胁=B300 PCIe下探；国内版=芯片中立×智算中心交付、昇腾配额制；否决三条件；一手财报=NVIDIA FY2026 $215.9B/+65%（DC $193.7B/+68%）、Intel Q2 $16.1B/+25%（DCAI $6.3B/+59%、$15B增发=资金压力信号）
- 行业洞察：超节点2026E $70-110B；ODM Direct 53.2%；WAIC 2026 Agent取代大模型+物理AI元年；编排鸿沟（使用+65% vs 速度+10-15%）；三大会闭环GTC→FMS→ODCC；FCC拟禁中国光收发器（中际旭创27%、中国56%）；CSP $2T LTA主导分配；数据中心社会阻力；平台工程ROI；Discovered Materials=验证债（端到端<10×）；**Gartner 2026 AI IaaS +96%至$420亿（2027 $660亿）、推理支出$233亿首超训练$190亿（55%→59%）**；**先进制程三线分化=三星1.4nm→2029/Intel High-NA/TSMC保守Low-NA；Terafab $119B/1TW算力/挖角台积电3-5倍薪酬；斯坦福3.7万智能体获默克验证**
- 项目管理+AI采用：Jira三连跳（追踪→编排→委派）；Symphony=编排与工作锚点解耦；Teamwork Graph 200B+对象（grounding +44%准确-48%token）；Rovo ARR 2x；Linear连9期无发布→降级月度；漏斗85→29→14%；探索优先于卡收益；adoption≠usage三层（仅第三层持久）；创造优先于验证/修补；修补工具化=确定性外壳；接纳度=能力补齐×利益补偿×容错安全÷责任恐惧（任一为0则0）；平台三态=工具/治理/认知；AI概率内核×工程确定性外壳
- 沟通与冲突：文字自证陷阱三层（Kruger媒介丰富度/Cialdini承诺升级/Festinger自证防御）；升维沟通四物理机制（同步反馈/关系通道/承诺可逆/认知聚焦）；三回合规则（≥3轮未收敛→升维）+先目标后分歧+会后确认锚；批判性边界=文字异步价值不可替代、升维≠占理（电话暴政剥夺弱势方异步表达权）——双向开放
- 信息可信度（meth-018）：双层可信度=源级S/A/B/C/D×信息级一手/二手/营销/观点×断言级L1/L2/L3 + 5×5决策矩阵；grade(信任度)与reachable(可达性)正交——A级源不可达≠不可信、C级源可达≠可信；源生命周期状态机+四类变化类型学（T1-T4）；meth-017 v1.7三通道MECE→统一收敛Markdown
- N-L-I-L-V五化框架（08-13新增）：三重熵模型=体量O(n²)/空间异构/时间漂移；分治悖论k*=√(S/2)（切分非越多越好）；五化=归一化→分层化→索引化→关联化→校验化；内容分散+索引集中（O(n)维护换O(log n)查询）；校验化必须自动化（唯一边际成本递增环节）；场景=超节点五源整合（FRU/BMC/PMC/交换机/CMDB）+知识库评估（关联化薄弱）
- 本地import增强工具：用户本地机持久配置=16G/20核/512G NVMe/RTX 5060 8G、上下文上限32K（本地工具/模型按此约束）；import/实测=1.4G/19,864文件/~700M tokens（平均70KB≈35K超上限）→方案=分级L0/L1 3B/L2 7B+分片+无状态批处理；设计文档已落knowledge/05_tools/knowledge-management/4篇，脚本待确认
- 外部渠道+技能集成：①github-daily-rank=git submodule（.gitmodules登记、update --remote，直接clone会成gitlink须rm -rf .git）②github-researcher-daily静态 ③CSDN日报（PLAYWRIGHT_ENABLED=1绕过521反爬）；GitHub日报=日榜vs API互证+补领域外高增量；**Skill类爆款生命周期短（claude-red/human-writing/RealReplica/open-kimi-ppt连续停滞=第三/四例）**；④Google mantis安全审查=codereview-mantis-security Lite（9阶段静态默认）/Full（17阶段沙箱复现）+PoC仅容器沙箱+补丁不自动应用，与open-code-review双通道

---

## Changelog

- **2026-08-14**: 从 MEMORY.md 迁移（原因：MEMORY.md ≤5KB 管控规则生效，深度洞察属低频检索内容，移入知识库归档）
