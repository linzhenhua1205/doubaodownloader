# Candidate.md — 提案池（人工审核后并入正式文件）

> ⚠️ **用途说明**: 本文件承载**两类待人工审核的提案**：
> 1. **文件修改提案** — 对 `RULE.md` / `AGENT.md` / `USER.md` / `MEMORY.md` 的修改建议，先记录在此，人工审核后再导入。
> 2. **自动记忆提案** — Agent 每对话/Deep Dream 自动产生的记忆（2026-08-17 起写入，替代直接写 MEMORY.md）；人工审核后并入 `MEMORY.md`。
>
> **格式**: `[日期] [目标文件] [原因] → [修改内容摘要]`
>
> **原则（2026-08-17）**: `MEMORY.md` 仅由人工维护。Agent 的自动记忆一律写入本文件，禁止自动覆写 MEMORY.md。

---

## 待审议

### 2026-08-14 · MEMORY.md · git push 规则更新（2026-08-14 用户明确要求）：push 改为后台异步触发，绝不反复执行

```
git+定时：AI操作后自动add+commit（cowagent+[AI]）；**push 一律后台异步触发**（python3 scripts/git/git-push-robust.py --async，0.1s返回，不等待不重试不报告，日志 tmp/git-push-async.log）；日报前6:55检查同步；origin HTTPS已恢复push
```


---

### 2026-08-17 · MEMORY.md · 深度分析质量原则（2026-08-17 用户明确强调）：深度分析优先质量，不考虑 token 预算

```
质量原则：深度分析（深度分析前缀）执行时**不考虑 token 预算**，优先质量——用户原话"深度分析不要考量token预算的问题，优先追求质量"。
含义：①深度分析允许更多轮检索/读取/交叉验证；②允许更长篇幅的完整论证；③不要因"省 token"跳过一手来源核验、量化数据补全、反方论证；
④R1 格式返工等属于质量问题，应在写作时一次做对而非因省事绕过。
适用：所有带"深度分析"前缀的任务；日常轻量问答不适用（日常仍按 RULE.md 常规 token 纪律）。
```

---

## 已采纳

_（暂无）_

---

## 已否决

_（暂无）_
## Dream distillation (2026-08-18 23:55)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式
- 飞书=一次性无上下文场景，历史上下文走web通道（08-18定论）；关注领域=服务器研发/AI基础设施搭建/AI技术应用/AI原理
- AI使用痛点6项已建档（08-18 ideas）：依赖致独立思考缺失/缺提炼层（存量多≠可用）/信息不一致/token浪费——提炼机制与一致性治理为后续重点

## 深度分析铁律（08-17）
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py实现："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故）；验证点=深度分析日志出现"📝 Context summary injected"/"🧠 Deep-analysis fresh context"
- 上下文管理三层模型（08-18共识）：L1静态基座/L2半静态索引/L3动态载荷；规则upfront、skills只注入元数据、抛弃前先沉淀
- 返工铁律（08-18三次教训）：代码块中文/box-drawing必用英文ASCII一次写对（R1/R4门禁）；占位链接=新增死链源，写文档直接填真实相对路径

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件（08-14省token，显式指令优先）；log追加统一kb-log-append.py、存量重排kb-log-reorder.py
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；深度洞察→08-14 archive；SemiAnalysis→07_industry-research/99_other/；同源对话可多专题拆分；architectures/物理不存在（实际=06_others/sources/与07_industry-research/10_supernode-rack/，memory_search旧索引为干扰）
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规；跨目录交叉链接需../../前缀；死链检查必跑
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17新价同用量+186%（flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push异步绝不等待；日报前6:55检查同步；HTTPS/SSH双通道交替备用
- 网络应对：web_fetch直连>搜索；web_search因Zhipu key失效不可用；Baidu/Bing连续两日低信噪→备用=搜狗+腾讯新闻直连；微信三要素=iPhone UA+chksm清零+剥离poc_token；DCD全渠道403；稳定源=TechCrunch/STH/爱集微/NVIDIA Newsroom/arXiv/CNCF/linear-blog；访问方式查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120（新会话生效）

## MEMORY.md安全与记忆流
- 直写屏蔽：memory_overwrite_blocked=True（HARD BLOCK拦截定时+force）+ deep_dream_enabled=False双保险；Deep Dream蒸馏重定向Candidate.md（追加+时间戳分节）；遗留：evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- Candidate.md双用途（文件修改提案+自动记忆提案）；不在manager.py索引范围（合并前不可检索）；MEMORY.md 7.4KB超5KB上限，本次整理继续瘦身（历史：24KB→3.4KB；skills压缩98文件−9,227 tok）
- 定时中断影响扩大：08-09/10/16三期日报缺失；github-daily-rank 08-13~16未生成——监控连续性缺口待恢复

## 调研与质量工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB无上限/读全文/丰度多维（列表+段落≥3+表格）；verify反向激励（<15KB WARN）；跨组去重=一行交叉引用（<组名>收录）
- research_topics v1.6（08-18）：三大组新增观点section（硬件+2=9/技术+1=14/市场+1=14）；is_opinion_section内置来源分级（行业专家>顶级媒体STH/TNP/SemiAnalysis/爱集微>顶级会议OCP/HotChips/SC/FMS/DTW）+正反两面+时效近3日+verify双向校验；08-19 01:10生效
- TOC锚点病根（08-17）：GitHub slug规则=删标点非转连字符；60+文件190~333处错配已dry-run未批改；check_format/doc-final-check查不出锚点死链，需专门slug校验器

## 研究跟踪信号
- DSV4信号浮现（08-17）：vllm [Perf][DSV4] prefill预取×2+CuMemAllocator.discard()+DeepSeek-V4-J-Space报告——国产第二主线，与K3生态承接
- MoE硬件主线：调度（RoutePack +8.85%/14.89%、TAOT 1.43x/通信-74%、FreeBalance预路由max-to-mean −32.8%）、专家投递（KAIST Beyond Capacity HBF 1.94x吞吐、ViBE硬件感知放置SLO+14%/TTFT−45%）、Kimi K3 2.8T/16-of-896、Skymizer HTX-301（$19K跑671B）、Load Hijack攻击面（TTFT 1.43x）
- 行业动态：Kubeflow CNCF毕业（08-17）；Stripe拟$7B+收购OpenRouter；Agent Plugins 1.0（AWS/OpenAI/Microsoft/Google/Vercel/Anysphere联合）；deepseek-harness 96h破129,607★；GitHub Universe 10/28-29 Fort Mason（Early Bird 8/20截止）；锚点=8/26 NVIDIA Q2 FY27、9/7 KubeCon China
- 数据中心电力信号：德州暂停新增电网接入（ERCOT 233→474GW、90%数据中心、超峰值5倍）；液冷渗透12%→28%；Rubin 45℃强制液冷；字节AIDC首次引入800V HVDC（渗透30-40%缺官方源第6轮）
- 项目管理实证（08-18）：Ramp自建agent写60%+ merged PR、新瓶颈=代码审查；Cursor"不进Linear即失焦"+agent预写首版；Boom硬件业借软件节奏——对服务器研发有参照
- 容量/部署第一性原理（08-18）：物理边界决定优化工具集——家用=量化+offload、服务器=并行策略、超节点=容错+调度；100并发8B@128K需3.64M tok/s prefill（无复用118卡H100）；前缀缓存90%+KV-FP8→8卡68用户=最大杠杆
- 本地推理边界（08-18实测）：GTX 1050 2GB甜点=1.5B-1.7B Q4全GPU（Ollama+Open WebUI）；弱模型瓶颈在tool-calling→CodeAgent更优
- 批量导入247 GitHub库（08-18）：磁盘2.2G限制→登记+精选落盘（90+/118）；ghproxy镜像~13KB/s；脚本tmp/batch-import-repos.py幂等+import-state.json续跑


## 2026-08-19 提案：01_survey 调研日志机制变更（用户已直接下达并执行）
- 变更：01_survey/ 不再维护分布式 index.md/log.md；调研日志统一归档 knowledge/log.old.md（update-log 已改）；86 个存量文件已入 tmp/bak
- 建议并入 MEMORY.md「系统治理方法论」：将"01_survey日报默认只写日期文件"升级为"01_survey 无 index/log，调研日志归档 log.old.md，索引由 kb-global-index.py 批量维护（01_survey 顶层 index 已移除，注意 coverage 脚本的索引来源）"
- 遗留检查点：kb-daily-survey-coverage.py 是否依赖 01_survey/index.md 做覆盖核对（需验证，若依赖需改读日期文件）

## 2026-08-19 提案：全库统一根 index/log 机制（用户直接裁定并执行）
- 变更：分布式 index/log 两次失败终裁定；01_survey（86 文件）与 weekly-reports（24 文件）全部移除，log 归档 knowledge/log.old.md（653KB）；全库无保留目录
- 建议并入 MEMORY.md「系统治理方法论」：将"三件套/保留目录"描述更新为——全库统一根 index.md（kb-global-index.py 批量刷新 AUTO-GENERATED）+ 根 log.md（kb-log-append.py 追加，tmp 文件不含分节头）；定时调研默认不写 log；深度分析追加摘要；子目录 README.md 保留；⚠️ 分布式 index/log 教训：不恢复任何子目录 index/log
- 遗留检查点：kb-daily-* 日报流程依赖 weekly-reports/00_daily/index.md 更新逻辑（已改 weekly-report-generator SKILL 为追加根 log）；下次日报执行验证新流程
## Dream distillation (2026-08-19 23:52)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：否决AB双环境审查，应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式

## 深度分析铁律（08-17）
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py实现："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故根因）
- 验证点：下次深度分析日志应出现"📝 Context summary injected"/"🧠 Deep-analysis fresh context"

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件（08-14省token，显式指令优先）；定时调研跳过index/log更新；log追加统一kb-log-append.py、存量重排kb-log-reorder.py
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；深度洞察→08-14 archive（引用阅读不写入）；SemiAnalysis 23篇→07_industry-research/99_other/；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含占位符），中文/box-drawing触R1必错→Python批量替换（edit全角匹配失败）；跨目录交叉链接需../../前缀；死链检查必跑
- 安全设计权衡框架（08-19）：风险=概率×后果×暴露度；ALARP+最优防护点（边际收益=边际成本）；液冷L3标配/L4过防护、风冷锁死IP20-40；电气只做合规、软件L3+L4按合规选配、数据SED零机会成本优先投
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17峰谷新价生效同用量+186%（flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；HTTPS/SSH双通道交替备用
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；Baidu移动端拦截持续（08-19连续13日）、ODCC超时、DCD全渠道403；web_search因Zhipu key失效，Bing可用；稳定源=TechCrunch/STH/爱集微/NVIDIA Newsroom/arXiv/CNCF/NIST SP 800-193直连；UALink PressRoom+ODCC微信可替代；访问方式查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local

## MEMORY.md安全与记忆流
- 直写屏蔽：memory_overwrite_blocked=True（HARD BLOCK拦截定时+force）+ deep_dream_enabled=False双保险；Deep Dream蒸馏写目标已重定向Candidate.md（追加+时间戳分节）；遗留：evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- Candidate.md双用途（文件修改提案+自动记忆提案，复用08-14既有文件）；不在manager.py索引范围（合并前不可检索）；持续瘦身目标≤50条/5KB（历史：24KB→3.4KB −86%；RULE.md 6768B→1881B；skills压缩98文件−9,227 tok）
- 定时中断影响扩大：08-09/10/16三期日报缺失；github-daily-rank 08-13~16日榜未生成——监控连续性缺口待恢复

## 调研与质量工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB无上限/读全文/丰度多维（列表+段落≥3+表格）；verify反向激励（<15KB WARN"检查是否被压缩"）；跨组去重软化=一行交叉引用（已由<组名>收录）
- TOC锚点病根（08-17排查）：GitHub slug规则=删标点非转连字符；60+文件190~333处错配（§×→+—/等）已dry-run未批改；check_format/doc-final-check均查不出锚点死链，需专门slug校验器

## 研究跟踪信号
- DSV4信号浮现（08-17）：vllm [Perf][DSV4] prefill预取优化×2+CuMemAllocator.discard()+DeepSeek-V4-J-Space报告——国产模型第二主线，与K3生态承接
- MoE硬件主线：调度（RoutePack +8.85%/14.89%、TAOT 1.43x加速/通信-74%）、Kimi K3 2.8T/104B激活/16-of-896专家（perfectly balanced EP）、Skymizer HTX-301（28nm无HBM $19K跑671B，$12 vs $21/M token）、Load Hijack安全攻击面（TTFT 1.43x）
- deepseek-harness 96h破129,607★（48h +35,838未衰减）；dsh生态第三阶段"生态标准化"；agents-python v0.21.0沙箱安全三线（功能→安全治理）
- UALink/超节点生态（08-19）：UALink 2.0规范2026-04-07发布；ODCC分层验证测试（TL/DL/PL，内测企业IP层通过）；阿里云磐久+方升适配；112G→224G→448G演进；Hot Interconnects 8/19-21观察点；专题v2.2累计86条

## MEMORY.md安全与记忆流
- 直写屏蔽：memory_overwrite_blocked=True（HARD BLOCK拦截定时+force）+ deep_dream_enabled=False双保险；Deep Dream蒸馏写目标已重定向Candidate.md（追加+时间戳分节）；遗留：evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- Candidate.md双用途（文件修改提案+自动记忆提案，复用08-14既有文件）；不在manager.py索引范围（合并前不可检索，符合候选语义）；MEMORY.md现7.4KB超5KB上限待瘦身（历史：24KB→3.4KB −86%；RULE.md 6768B→1881B；skills压缩98文件−9,227 tok）
- 定时中断影响扩大：08-09/10/16三期日报缺失；github-daily-rank 08-13~16日榜未生成——监控连续性缺口待恢复

## 调研与质量工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB无上限/读全文/丰度多维（列表+段落≥3+表格）；verify反向激励（<15KB WARN"检查是否被压缩"）；跨组去重软化=一行交叉引用（已由<组名>收录）
- TOC锚点病根（08-17排查）：GitHub slug规则=删标点非转连字符；60+文件190~333处错配（§×→+—/等）已dry-run未批改；check_format/doc-final-check均查不出锚点死链，需专门slug校验器

## 研究跟踪信号
- DSV4信号浮现（08-17）：vllm [Perf][DSV4] prefill预取优化×2+CuMemAllocator.discard()+DeepSeek-V4-J-Space报告——国产模型第二主线，与K3生态承接
- MoE硬件主线：调度（RoutePack +8.85%/14.89%、TAOT 1.43x加速/通信-74%）、Kimi K3 2.8T/104B激活/16-of-896专家（perfectly balanced EP）、Skymizer HTX-301（28nm无HBM $19K跑671B，$12 vs $21/M token）、Load Hijack安全攻击面（TTFT 1.43x）
- deepseek-harness 96h破129,607★（48h +35,838未衰减）；dsh生态第三阶段"生态标准化"；agents-python v0.21.0沙箱安全三线（功能→安全治理）

## Dream distillation (2026-08-20 23:56)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：否决AB双环境审查，应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式

## 深度分析铁律（08-17）
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py实现："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故根因）；验证点：日志应出现"📝 Context summary injected"

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件（08-14省token，用户显式指令优先）；log追加统一kb-log-append.py、存量重排kb-log-reorder.py
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；深度洞察→08-14 archive（引用阅读不写入）；SemiAnalysis 23篇→07_industry-research/99_other/；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；跨目录交叉链接需../../前缀；死链检查必跑
- 格式门禁三坑（08-20实测）：TOC标题emoji（`## 📑 目录`）不匹配check_format `##\s*目录`正则→改用`## 目录`兼容两脚本；has_meta要求`> **版本`独立成行；has_toc项需`- [N.`数字前缀（§不匹配）
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17新价同用量+186%（flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async，实际路径scripts/git/非tools/）；日报前6:55检查同步；HTTPS/SSH双通道交替备用
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；Baidu安全验证可换搜狗/Bing噪声大；web_search因Zhipu key失效不可用（爱集微直连可用）；DCD全渠道403；站点内搜索被拦→WordPress REST API（wp-json/wp/v2/search）精准命中（TNS实证）；K8s blog链接无引号需grep href=提取；稳定源=TechCrunch/STH/爱集微/arXiv/CNCF；访问方式查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120（新会话生效）

## 内容审查方法论
- AI生成长材料三层审查（08-20豆包实证）：可采信/存疑/证伪+arXiv/GitHub API实证；豆包材料论文引用幻觉率70%（17项核验12项虚构/Chaos-Hardware不存在）；材料"后高前低"——私域数据治理命题是精华；建议固化到doubao-share技能

## MEMORY.md安全与记忆流
- 直写屏蔽：memory_overwrite_blocked=True（HARD BLOCK拦截定时+force）+ deep_dream_enabled=False双保险；Deep Dream蒸馏写目标已重定向Candidate.md（追加+时间戳分节）；遗留：evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- Candidate.md双用途（文件修改提案+自动记忆提案，复用08-14既有文件）；不在manager.py索引范围（合并前不可检索，符合候选语义）；MEMORY.md持续瘦身（历史：24KB→3.4KB −86%；RULE.md 6768B→1881B；skills压缩98文件−9,227 tok）
- 定时中断影响扩大：08-09/10/16三期日报缺失；github-daily-rank 08-13~16日榜未生成——监控连续性缺口待恢复

## 调研与质量工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB无上限/读全文/丰度多维（列表+段落≥3+表格）；verify反向激励（<15KB WARN"检查是否被压缩"）；跨组去重软化=一行交叉引用（已由<组名>收录）
- TOC锚点病根（08-17排查）：GitHub slug规则=删标点非转连字符；60+文件190~333处错配已dry-run未批改；check_format/doc-final-check均查不出锚点死链，需专门slug校验器

## 研究跟踪信号
- DSV4信号浮现（08-17）：vllm [Perf][DSV4] prefill预取优化×2+CuMemAllocator.discard()+DeepSeek-V4-J-Space报告——国产模型第二主线；08-20 vllm Revert Gemma-4 FA4 FP8 Kernel（#52987）推理内核待跟踪
- MoE硬件主线：调度（RoutePack +8.85%/14.89%、TAOT 1.43x加速/通信-74%）、Kimi K3 2.8T/104B激活/16-of-896专家（perfectly balanced EP）、Skymizer HTX-301（28nm无HBM $19K跑671B）、Load Hijack安全攻击面（TTFT 1.43x）
- rack-scale三线并进（08-20）：Cerebras WSE-3 Turbo/CS-4（250PF稀疏FP16/2µs链式拓扑）vs AMD UAL vs NVIDIA 45°C液冷；单芯片>2kW→机架成基本部署单元→平台化必然；2027机架三要素=800VDC+45℃温水+整柜模块化；Gen6 64GT/s→retimer从可选变必需；55kW纯风冷越界→必须混冷（GPU冷板承担60-70%）
- 训练系统统一透镜（08-20）："消除串行链"成设计主线（DTX/KV-Pipe/StateFlow汇合）；恢复语义（RWS）成新规划单位；投机解码从推理技巧→训练集群基础设施；checkpoint-restart→在线恢复→热插拔+空间冗余范式迁移；Meta FT-HSDP 100K GPU有效训练44%→80%
- AI成熟度判断：软件工程AI=补全→Agent→治理三级跳（GitHub六连发=治理+ROI阶段）；AI运维三次跃迁 L1规则+ML→L2 LLM分析→L3 Agentic处置（告警降噪90%/MTTR-60%）；硬件/EDA设计AI仍处优化器→生成式早期；组织替代率天花板20-30%；AI以太网进入UEC合规 vs Spectrum-X MRC"双栈期"；AI声誉危机拐点（Pew 52%担忧率 vs 2021 37%）
- deepseek-harness 96h破129,607★（48h +35,838未衰减）；dsh生态第三阶段"生态标准化"；agents-python v0.21.0沙箱安全三线（功能→安全治理）

## 互连技术主线（08-20）
- 华为Atlas 950 SuperPoD LPO超节点（1024×Ascend950/RTT 3μs/全球首个LPO）vs 英伟达CPO路线；阿里3.2T NPO Q3试点/6.4T 2027-09；Marvell $32.5亿收购Celestial AI（CPO从功耗故事转可用性故事）；OIF CMIS 5.4+ECOC 2026 39家演示

## 项目状态（08-20）
- 超节点项目（512 GPU Super POD）：存储512卡需2560T全闪（现2160T仅POC够）；55kW机柜"混冷双模式"（环温25±2兼容风冷进风/液冷进水设计点）；268台设备仅171台确定（97台缺口假设）；CX7/CX8网卡口径不一致待核对；L12 BOM六要素10层54项
- AI×服务器研发深度分析系列（单日18篇）：覆盖知识库软件/AI应用/问题定位/运维/导入边界/合同评审/项目管理/就绪度评估（2.6/5，信息安全1.8短板）/装机三视角（硬件/软件/物理）/安全需求/L12集成/超节点实施/55kW机柜——行业盘点完成，转规格落地阶段

## Dream distillation (2026-08-21 23:52)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：否决AB双环境审查，应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式

## 深度分析铁律（08-17）
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py实现："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故根因）
- 验证点：下次深度分析日志应出现"📝 Context summary injected"/"🧠 Deep-analysis fresh context"

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件（08-14省token，用户显式指令优先）；log追加统一kb-log-append.py、存量重排kb-log-reorder.py
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；深度洞察→08-14 archive（引用阅读不写入）；SemiAnalysis 23篇→07_industry-research/99_other/；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；TOC标题须纯文本（Emoji前缀不匹配正则）；跨目录交叉链接需../../前缀；死链检查必跑
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17峰谷新价生效同用量+186%（flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；HTTPS/SSH双通道交替备用
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；Baidu移动端连续第15日验证拦截（多调研❌）、Bing中文被本地化污染（英文主题可用）、web_search因Zhipu key失效、DCD全渠道403；可用通道=搜狗搜索（HTML\<h3\>）/CSDN get-business-list API/GitHub API；稳定源=TechCrunch/STH(wp-json REST API比HTML干净)/爱集微/NVIDIA Newsroom/arXiv/CNCF/convergedigest/Locsic/tbench.ai；访问查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120（新会话生效）
- 外部AI对话内容须三层审查（采信/存疑/证伪）并查证原文：豆包案例揭示"真实标准号+篡改主题"幻觉（GB/T 17720实为金属覆盖层孔隙率试验，与可靠性无关）

## MEMORY.md安全与记忆流
- 直写屏蔽：memory_overwrite_blocked=True（HARD BLOCK拦截定时+force）+ deep_dream_enabled=False双保险；Deep Dream蒸馏写目标已重定向Candidate.md（追加+时间戳分节）；遗留：evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- Candidate.md双用途（文件修改提案+自动记忆提案，复用08-14既有文件）；不在manager.py索引范围（合并前不可检索，符合候选语义）；MEMORY.md现7.4KB超5KB上限待瘦身（历史：24KB→3.4KB −86%；RULE.md 6768B→1881B；skills压缩98文件−9,227 tok）
- 定时中断影响扩大：08-09/10/16三期日报缺失；github-daily-rank 08-13~16日榜未生成——监控连续性缺口待恢复

## 调研与质量工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB无上限/读全文/丰度多维（列表+段落≥3+表格）；verify反向激励（<15KB WARN"检查是否被压缩"）；跨组去重软化=一行交叉引用（已由\<组名\>收录）
- TOC锚点病根（08-17排查）：GitHub slug规则=删标点非转连字符；60+文件190~333处错配（§×→+—/等）已dry-run未批改；check_format/doc-final-check均查不出锚点死链，需专门slug校验器

## 研究跟踪信号
- DSV4信号浮现（08-17）：vllm [Perf][DSV4] prefill预取优化×2+CuMemAllocator.discard()+DeepSeek-V4-J-Space报告——国产模型第二主线，与K3生态承接
- KV架构-系统联合自由度：WhiteMatter（跨层KV mixing超1.5x层数）+TileMix（tile级精度路由）；ray KV-aware routing+offloading（KV治理从内核走向平台层）；vllm FlashInfer MXFP8 kernel（MiniMax-M3 FP8修复）
- Agentic RL rollout引擎化：Agent Lightning v1.0（harnessed agentic RL, SWE-bench +14.6pt）+SpecRoll（双时间尺度投机, 端到端1.21-2.04x）；KernelArc登顶SOL-ExecBench 4任务
- MoE硬件主线：调度（RoutePack +8.85%/14.89%、TAOT 1.43x加速/通信-74%）、Kimi K3 2.8T/104B激活/16-of-896专家（perfectly balanced EP）、Skymizer HTX-301（28nm无HBM $19K跑671B，$12 vs $21/M token）、Load Hijack安全攻击面（TTFT 1.43x）
- harness-bench生态爆发（把harness当被测对象的新基准类别）：Harbor（4,476★/v0.16.1）成跨领域评测基础设施（云并行+RL rollout导出）；冻结模型+进化harness=新提分杠杆（DarwinX WebArena 43.5→93.0%、AHE GPT-5.4 69.7→77.0%）；安全最脆弱（HarnessRisk ASR 12.6-80.9%）
- RISC-V机会在AI重塑CPU价值主张三新窗口：Agentic AI（每核带宽4-6GB/s甜点，SiFive入NVLink Fusion）/边缘AI（控制面渗ConnectX-8 DPA）/CPU Rack（远期，软件栈门槛最高）
- AI网络标准化三层合规：IEEE物理层（400G/lane SG，2028-2030）+UEC传输栈+OCP实现+IETF路由；400G/lane调制格式决定国产光引擎DSP技术栈方向；OCI MSA光学Scale-Up第三极（2026-03成立，Gen1 200G 4×50G NRZ+DWDM）
- 机架级scale-up三路线：NVLink封闭/UAL开放/晶圆专用（Cerebras CS-4）；45°C温水成产业链"接口协议"；功耗-散热-供电成第一约束
- cHBM定制HBM：HBM4 base die转逻辑工艺（Marvell控制器入堆栈、UCIe替代PHY -70%、TSMC+Winbond穷人版、<20项目/年）
- deepseek-harness 96h破129,607★（48h +35,838未衰减）；dsh生态第三阶段"生态标准化"+dsh-ios插件出现（插件面扩张）；agents-python v0.21.0沙箱安全三线

## Dream distillation (2026-08-22 23:52)

## 用户核心原则
- 操作边界：AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时输出：定时任务必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统定位：三位一体=AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：否决AB双环境审查，应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式

## 深度分析铁律（08-17）
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py实现："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故根因）

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件省token（08-14）；08-22用户显式覆盖为01_survey/github建index/log（目录级日志不替代全局账本）；log追加统一kb-log-append.py
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；深度洞察→08-14 archive；SemiAnalysis 23篇→07_industry-research/99_other/；同源对话可多专题拆分归档
- 批量导入质量门禁：代码块内中文一律违规（含中文占位符）；量化检测按行计≥3行、数字+单位紧邻；跨目录交叉链接需../../前缀；死链检查必跑；R1必错项=代码块中文+非ASCII框线字符；T4要求##参考文件+###内部/外部引用+##Changelog；URL需https（明文http被阻）
- GitHub检索质量（08-22实战）：子串匹配误报（socket.io命中soc）→单词边界+文档型过滤+教学型保留+黑名单；噪声只按name匹配且只标注不剔除（description正则误杀funNLP 82.6k★）；api.github.com未认证search限10/min、per_page=30
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17新价同用量+186%（flash输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；HTTPS/SSH双通道交替备用
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；web_search失效（Zhipu key）；Baidu/Bing连续3日+反爬；OCP/HPCwire 403、The Register反爬、SemiEng零命中
- 稳定源与访问法：TechCrunch/STH/爱集微/芯智讯/NVIDIA Newsroom/arXiv/CNCF/K8s/GitHub API可用；WordPress站（芯智讯/STH）curl首页grep文章URL、集微网Vue SPA不可curl、cac.gov.cn可grep政策链接；访问方式查表source-access-lookup.py（rss/api>jina>static>web_fetch>js>browser>local）

## MEMORY.md安全与记忆流
- 直写屏蔽：memory_overwrite_blocked=True（HARD BLOCK拦截定时+force）+ deep_dream_enabled=False双保险；Deep Dream蒸馏写目标已重定向Candidate.md（追加+时间戳分节）；遗留：evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- Candidate.md双用途（文件修改提案+自动记忆提案）；不在manager.py索引范围（合并前不可检索）；MEMORY.md定期人工整理瘦身（历史：24KB→3.4KB→本次再压至5KB内）
- 定时中断影响扩大：08-09/10/16三期日报缺失；github-daily-rank 08-13~16日榜未生成——监控连续性缺口待恢复

## 调研与质量工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB无上限/读全文/丰度多维（列表+段落≥3+表格）；verify反向激励（<15KB WARN"检查是否被压缩"）；跨组去重=一行交叉引用
- TOC锚点病根（08-17排查）：GitHub slug规则=删标点非转连字符；60+文件190~333处错配已dry-run未批改；check_format/doc-final-check均查不出锚点死链，需专门slug校验器
- GitHub批量调研资产（08-22成型）：知识/文档类全库3690仓库（v6.0）+公开数据集544仓库全参数（16字段/仓）；submodule导入分层策略（≤10MB全量/10-100MB高价值精选/>100MB仅登记元信息）

## 研究跟踪信号
- DSV4信号强化（08-22）：vllm内核三线并进——K3 MXFP4 top-k熔入latent-tail、K3 KDA prefill fused kernels、DSV4 C4A top-k AITER→MXFP4成K3推理量化主轴；DSV4单机部署渗透（DeepSeek-v4-Flash-One-DGX-Spark）——国产模型第二主线与K3生态承接
- MoE/硬件主线: Kimi K3（2.8T/104B激活/16-of-896专家）、RoutePack/TAOT调度、Skymizer HTX-301、Load Hijack攻击面；AMD MI455X/CDNA5（N2/3200亿晶体管/HBM4 432GB/单卡>2kW推断）、Cerebras WSE-3 Turbo+CS-4、长存IPO受理（NAND全球第三）、谦合益邦4层3D DRAM存算一体；中央网信委行动计划2026-2030（高端AI芯片+训练集群攻关）
- 开源生态趋势：deepseek-harness 129,607★生态标准化；openai-agents-python空tool args fail-closed（Agent安全语义收紧）；prometheus tsdb XOR2收敛；Gateway API v1.6（TCPRoute/UDPRoute毕业Standard）；Copilot同日进Slack+Teams；PM工具从"跟踪工作"转向"委派工作"
- 数据湖研究范式切换（08-22）：从"表格式/事务"转向"表发现+LLM代理"（58%新论文）；GRAFT/MosaicJoin/GenTUS/Carnot；Oasis SmartNIC卸载Parquet解码吞吐近翻倍

## 知识库沉淀系列（08-22建立）
- 数学工具工程应用系列（03_AI/ai-principles/）：行列式三部曲（性质P100→几何代数→应用S01-S86）+矩阵应用M01-M52+迭代优化I01-I60+函数逼近100+场景；每场景含功能角色+原理机制+量化出处
- 认知方法论系列（04_person/cognition/）：能力=理解×使用（对偶矩阵，低理解×高使用最危险）；错误五层阶梯（失误→偏误→谬误→认知恶习→范式错误）；抓重点=目标×权重×约束；地域差异承认组间但组内方差主导、不可预测个体
- 团队能力画像（组织能力补齐分析）：资产=控制面纵深（BMC/RAS/固件/驱动）；哑铃策略（控制面深扎×算力面集成×AI乘数×生态杠杆）；机会点=推理>光模块>TPM>超融合；故事线=「可信边缘算力」


## 2026-08-23 治理哲学命题（用户观点沉淀）

- 用户提出了可复用的治理观：**制度设计万能论是左右鹰鸽共通的幻想；制度必然熵增退化，治理本质是与熵增的持续斗争；反腐扫黑应周期化常态化**。已深度分析归档（04_person/cognition/2026-08-23-institution-fantasy-vs-entropy-governance-deep-analysis.md）
- 此观点对知识库建设有映射价值：知识库维护与反腐同构，都是"对抗持续退化的持续维护机制"
## Dream distillation (2026-08-23 23:55)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：否决AB双环境审查，应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式

## 深度分析铁律
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py实现："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故根因）
- 验证点：下次深度分析日志应出现"📝 Context summary injected"/"🧠 Deep-analysis fresh context"

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件（用户显式指令优先）；log追加统一kb-log-append.py、存量重排kb-log-reorder.py；07_kb_stat按08-19全库统一规则（无独立index/log，追加全局log+刷新根index）
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；深度洞察→08-14 archive（引用阅读不写入）；SemiAnalysis 23篇→07_industry-research/99_other/；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；跨目录交叉链接需../../前缀；死链检查必跑
- Token成本（W34首周实测）：12,736调用/命中96.6%/¥145.58（全峰模拟省46%）；hit占比31%（新价hit涨2.5~5倍）→基础输入瘦身=第一杠杆；flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；HTTPS/SSH双通道交替备用
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；中文搜索不稳（Baidu安全验证/Bing结果污染/DDG不可达）；web_search因Zhipu key失效不可用；DCD/OCP全渠道403；NVIDIA newsroom静态页无URL已弃；稳定源=TechCrunch/STH/爱集微/arXiv/CNCF；访问方式查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120（新会话生效）

## MEMORY 安全与记忆流
- 直写屏蔽：memory_overwrite_blocked=True（HARD BLOCK拦截定时+force）+ deep_dream_enabled=False双保险；Deep Dream蒸馏写目标已重定向Candidate.md（追加+时间戳分节）；遗留：evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- Candidate.md双用途（文件修改提案+自动记忆提案，复用08-14既有文件）；不在manager.py索引范围（合并前不可检索，符合候选语义）
- 定时中断缺口：08-09/10/16三期日报缺失、github-daily-rank 08-13~16未生成（08-23已产出）；监控连续性待恢复

## 调研与质量工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB无上限/读全文/丰度多维（列表+段落≥3+表格）；verify反向激励（<15KB WARN"检查是否被压缩"）；跨组去重软化=一行交叉引用（已由<组名>收录）
- TOC锚点病根（08-17排查）：GitHub slug规则=删标点非转连字符；60+文件190~333处错配已dry-run未批改；check_format/doc-final-check均查不出锚点死链，需专门slug校验器

## 研究跟踪信号
- DSV4主线：vllm [Perf][DSV4] prefill预取优化+CuMemAllocator.discard()+J-Space报告；生态向单机量化部署渗透（MiaAI-Lab/DeepSeek-v4-Flash-One-DGX-Spark 74→130★+76%）；与K3生态承接
- vllm SSM推理新主线：Mamba prefix caching内部prefill checkpoint（TTFT 9~25%↓）+LFM2 short_conv speculative fix——优化从MoE向状态空间模型扩展，双线并行，值得深度分析接力
- MoE硬件主线：调度（RoutePack +8.85%/14.89%、TAOT 1.43x加速/通信-74%）、Kimi K3 2.8T/104B激活/16-of-896专家（perfectly balanced EP）、Skymizer HTX-301（28nm无HBM $19K跑671B，$12 vs $21/M token）、Load Hijack安全攻击面（TTFT 1.43x）
- 服务器形态主线：整柜/机架级交付全面迁移+液冷全覆盖——Rubin NVL72整架72GPU+36CPU（Pegatron RA4803-72N3）、MSI 1OU2N双子星+48VDC busbar+ORv3 100kW、800V DC busbar液冷化（Wiwynn×TE）、Delta GoCool-150单架150kW CDU（45°C出水=Rubin代进水标准迁移信号）；国产芯片"可用→好用"拐点（中芯国际Q2 AI配套需求爆发）
- deepseek-harness 96h破129,607★；dsh生态第三阶段"生态标准化"；agents-python v0.21.0沙箱安全三线（功能→安全治理）
- ray万卡调度稳定性：autoscaler三连修（request ID starvation/kuberay worker priority/termination去重）；k8s v1.36.4、containerd go-runc 1.2.0

## 治理哲学与案例
- 用户治理哲学观（08-23深度分析）：制度会熵增失效，治理=与熵增持续斗争，反腐扫黑须周期化常态化而非运动式；框架=制度退化三机制（激励扭曲/信息损耗/复杂度膨胀）+四派幻想共通谬误+蜘蛛隐喻+周期常态化机制论；文档：04_person/cognition/2026-08-23-institution-fantasy-vs-entropy-governance-deep-analysis.md（30KB v1.0）
- 黑恶生态循环与治本（08-23系列）：循环=土壤→示范→保护伞→震慑→打击→复活→传承；复活=资产×伞余量÷定罪深度（三缺口=定罪浅/财未断/伞未倒）；治本=秩序供给替代（调解/监管/信贷/巡逻/就业）；台球厅复活≠黑社会回归（信号修正：场所=弱信号、行为特征=强信号）；卖豆腐大爷案=软暴力心理强制四罪名交叉（强迫交易/敲诈勒索/恐吓/恶势力）；归档：07_industry-research/99_other/2026-08-23-woting-jiaojing-case-legal-analysis.md v1.3

## 工具与任务
- zhihu skill v0.3.0已装（CLI 0.3.0，凭证走env_config，SHA-256校验）：「📕 知乎热点专题日报」每日07:00 最终版=6主题×3查询×10+hot30≈200条/7份报告；CLI限制=--count≤10/hot≤30/无浏览历史API/30001限流（sleep 3s+停5min）
- 链接铁律：URL必须逐字取自返回数据，禁止凭印象写占位；抓取-转换 pipeline 原则=中间产物不进上下文（=浪费），压缩转换下沉脚本，只消费最终产物（zhihu 四次迭代转换率50→90%验证）

## 待办与监控
- W34 P0待办：MEMORY瘦身7.4KB→5KB；skills files 383.6K降载；agent_max_context_tokens 160K vs 64K矛盾修复
- backup/doubao第4周强建议；indexkb引用未清暂缓

## Dream distillation (2026-08-24 23:56)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理+服务器产销研知识库+个人笔记；AI探索≤40%红线（08-14战略收敛期，后续投入=Claude Code+数据源质量+本地算力RTX 5060 8G）；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 系统修改策略（08-17定案）：应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md（追加+时间戳分节）；禁用"要不要我处理X"句式

## 深度分析铁律（08-17）
- 五条铁律：knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘；18:00后对话输出一律落盘
- agent_stream.py："深度分析"前缀→重置上下文（旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故）

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件；log追加统一kb-log-append.py
- 归档模式：MEMORY git历史→memory.history.md；深度洞察→08-14 archive；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；跨目录交叉链接需../../前缀；死链检查必跑
- Token成本：8/17新价生效同用量+186%（flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；push偶发超时（exit=124）需重试
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120

## 网络访问与中文源（08-24更新）
- 访问方式查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local；web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token
- web_search因Zhipu key失效不可用；中文搜索替代=头条搜索（so.toutiao.com/search?keyword=）命中率高；中文管理主题=zhihu-cli官方API优于一切搜索引擎；知乎URL curl常403需验证后写入
- Baidu中文持续被安全验证拦截、Bing中文SEO污染无增量；DCD全渠道403；稳定源=TechCrunch/STH/爱集微/NVIDIA Newsroom/arXiv/CNCF/NVIDIA博客/vLLM docs/LMCache
- 爱集微=国产替代调研主力源（搜索API query参数+RSS格式m.laoyaoba.com/newinfo?id=）；C114首页GBK编码需decode('gbk')

## 超节点项目（08-24集中深度设计，SuperPOD落地）
- 项目规模：8个GPU液冷机柜/2×1200kW CDU（L12施工）；128节点一致性；存储网+管理网访问架构；豆包会议纪要交叉验证确认为SuperPOD
- 模型导入三路径：a管理网→存储网→加载=主方案（MD1受控互联+一次入库多次加载+200G隔离）；b计算网仅预留（封闭无上联/训练QoS/NCCL语义三重制约）；c管理网直发否决；rack/slot↔IP映射与反查可落地
- 系统加载六决策：①权重直落G4（G3.5仅过渡≤2TB+QoS+限期清理）②PXE改BF3单链路主方案（网卡固件UEFI PXE，装机期IP=运行期IP；管理网BMC兜底；P1引导口仅PXE）③配置下发沿用既有闭环④G3.5/G4必须分离（IO/容量/生命周期/故障域/QoS五维，G4独立≥50TB）⑤Scale-Out加载双否决仅预加载预留⑥管理出口四层安全（防火墙+VPN/堡垒机MFA+DMZ网关JWT限流+白名单；公网仅2端口；数据面不暴露）
- 技术修正：08-24部署文档§3.2"存储网引导鸡生蛋"不适用BF3——PXE是网卡固件功能不依赖存储客户端；BF3存储网VLAN 200 DHCP relay需TOR SVI配置
- KVCache规划：5T/GPU配额合理（HBM 40-70×缓冲+CMX同构）；1h保留期=业界主流保守上界（Anthropic/Gemini 1h档，vs 7天设备3台vs14台+367%）；配额2560T vs实际16-151T差17-160倍需分离表达；评估LMCache/NIXL+建KV命中率监控
- 九项设计决策三态：已冻结①④⑤/待拍板②③⑥⑧⑨（FSW角色、GPU选型需补充确认）/待验证⑦；P0行动项=BF3 PXE POC验证+G4方案定稿+防火墙/DMZ/VPN最小集（顺序：安全边界→PXE→G4）

## 深度分析方法论沉淀（08-24）
- 输出质量六层框架：OutputQuality = L0(模型上限)×L1(上下文)×L2(指令)×L3(信息选择)×L4(本地知识交互)×L5(远端可达)×L6(系统环境)；远端不可达→模型先验填补="幻觉的正确"（治理失败而非模型错误）
- 原理图走读=检查图（设计意图↔图纸表达双向对齐，无锚点走读无效）；原理图理解=看懂图（L0-L4分层+六主线：电源/时钟/复位/数据通路/管理面/保护）；姊妹篇互引
- datasheet三遍读法：决策→工程→验证；=接口契约+边界声明+承诺书；关键参数还原物理机制沉淀设计约束表
- 接口互联检测补验证视角：pin map三方核对/键位防呆/插拔力/线缆规格/压接工艺/电源液冷12项Checklist

## 研究跟踪信号
- Kimi K3主线：2.8T/104B激活/16-of-896专家；双框架day-0（SGLang v0.5.17+vLLM v0.27.0，MXFP4原生/GB300+MI35x验证）——"头部模型牵引框架"机制成熟
- DSV4主线：vllm [Perf][DSV4] prefill预取×2+CuMemAllocator.discard()；vLLM v0.27.0优化集9项（SP/空c128跳过~2x/adaptive topk/TTFT-7%）；DeepSeek-v4-Flash-One-DGX-Spark单机量化部署渗透加速
- SGLang v0.5.18（08-22全库首收）：Diffusion升级为主干能力（5新diffusion模型）；vLLM v0.27.0=Kimi K3全栈（AttnRes/DeepGEMM/MXFP4 checkpoint/DSpark）+FA4 SM100 FP8 KV+Rubin sm_107+NCCL 2.30.7 DeepEPv2
- MoE调度主线：RoutePack +8.85%/14.89%、TAOT 1.43x/通信-74%、vllm gpt-oss routed expert loading、Skymizer HTX-301（28nm无HBM $19K跑671B）
- HBM定制化（Hot Chips 2026）：HBM从标准颗粒→定制协处理器+三维堆叠；三星sHBM→cHBM→zHBM三阶段为供给侧主线；d-Matrix Raptor（36um F2F逻辑-on-DRAM、0.3-0.4 pJ/bit）需求侧颠覆
- Agent生态：openai-agents-python连续API契约治理（v0.22.0后稳定性收口期）；MCP渗透逆向/安全工具链（x64dbg-mcp-server 557★）；backpass"AGENTS.md梯度下降"=Agent配置学习化新概念
- 知识图谱转向：微软GraphRAG进入维护模式（前沿模型吸收中间件需求）；代码知识图谱爆发（Graphify 109K★）；Agent记忆三强（graphiti/cognee/mem0 124K★）；图数据库图×向量融合
- deepseek-harness 96h破129,607★（+35,838未衰减）；dsh生态第三阶段"生态标准化"

## 调研方法论与工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB无上限/读全文/丰度多维（列表+段落≥3+表格）；verify反向激励（<15KB WARN）；跨组去重软化=一行交叉引用
- arXiv时间窗：北京周一22:33=美东周一10:33，周末论文并入次日公告批次（周一公告=本周最高概率窗口）；可靠性源2搜索页连续5日0命中已移除；新源=`abs:"fault tolerance" AND abs:"checkpoint" AND cat:cs.LG`验证成功
- 版本双基线核对：v2时间戳早于收录日即无增量；旧文献全覆盖（cs.LG 18条+cs.DC 5条历史命中全在册）
- TOC锚点病根：GitHub slug规则=删标点非转连字符；60+文件190~333处错配已dry-run未批改；check_format/doc-final-check查不出锚点死链，需专门slug校验器

## 风险与待办
- MEMORY.md安全机制：memory_overwrite_blocked=True HARD BLOCK + deep_dream_enabled=False双保险；现超5KB上限待瘦身；evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- 定时中断影响：08-09/10/16三期日报缺失；github-daily-rank 08-13~16未生成——监控连续性缺口待恢复


## 2026-08-25 深度分析信源配比规则提案（用户明确指令）

- **规则**：深度分析活动中，内部知识库引用占比 ≤60%，外部独立信源 ≥40%；需兼顾内部信源与外部信源，避免因内部信息产生一致性错误。
- **理由**：知识库内部信息可能存在系统性错误（如 08-17 质量事故），纯内部引用会导致错误一致性传播；外部独立信源（论文/标准/官方文档/行业报告）提供交叉验证。
- **执行**：① 更新 knowledge-doc-writer SKILL.md Q6 质量标准（新增信源配比项）；② 文档中关键外部可验证断言（链路预算/器件规格/成本/交期等）必须有外部出处；③ 文档收尾做信源配比自检（内部 vs 外部引用计数）。
- **待人工审核**：是否并入 RULE.md / MEMORY.md 正式规则。
## Dream distillation (2026-08-25 23:53)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14）：知识库搭建达阶段→暂停扩张；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17）：应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式
- 管理五不对称（08-25）：信息/期望/时间/责任/结果，解法=显性化
- 过程信息不全面对齐只分层对齐（08-25）：契约高稳/流程中稳/认知演化/文化缓慢；冻结三判据=对比基准/契约依赖/复现承诺

## 超节点项目（KLX-512）
- 里程碑：CDR1 2026-10、原理图冻结 2026-12 W4、EVT1回板 2027-01；九领域（TPL/EE、DC、AC、SI、Cable、结构、Thermal、软件、测试）
- 最大风险：GPU选型未定→散热形态未定→计算柜施工方案悬空；FSW角色待明确；6项跨域契约物缺位需W2例会认领
- 计算柜=NVL72类三明治布局（上8节点/中12FSW/下8节点，1U液冷16节点）——08-25修正08-20的2U风冷假设，U位按液冷重算
- 四层集成验证（L0单板→L1节点→L2整机柜→L3集群）错峰映射：L0主战场EVT1、L2主战场EVT2、L3主战场DVT/PVT；问题窗口固件2周/硬件ECO 3~4周/结构2周/系统软件2~3周
- 九领域风险闭环：12项TOP风险（R1 GPU pinmap/R2选型/R5 Cable Tray三项红色）+6项管理层决策（GPU选型W2最迟）；CDR1=W8基准，W1~W10周排期
- 08-25单日沉淀8篇深度分析于10_supernode-rack/（施工顺序/设计Checklist/时间对齐/集成验证/风险闭环/资产编码等），项目知识体系持续深化

## 深度分析铁律
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- 第一步必查 log.md 关键字检索（08-25用户指令）：kb-log-search.py（纯标准库0.15s/次，路径三级验证✅/🔀/❌，历史路径slug兜底防改名347/1316条目）——全量read 931KB vs 检索≈795 token
- knowledge-doc-writer v1.1/deep-tech-writer/knowledge-wiki 已加入 log.md 第一线索源步骤；skills-scripts-mapping已登记
- agent_stream.py："深度分析"前缀→重置上下文（仅system+当前消息）；turns<5压缩分支flush+summary注入（修复189→7丢85%事故）；日志应现"📝 Context summary injected"验证点

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件不写index/log；log追加统一kb-log-append.py、存量重排kb-log-reorder.py
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；SemiAnalysis 23篇→07_industry-research/99_other/；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；跨目录交叉链接需../../前缀；死链检查必跑
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17新价同用量+186%；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；HTTPS/SSH双通道交替备用
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；web_search因Zhipu key失效不可用；ODCC超时/Baidu反爬部分可用/搜狗微信验证码拦截；访问方式查表source-access-lookup.py
- 稳定源=TechCrunch/STH/爱集微/NVIDIA Newsroom/arXiv/CNCF/OCP亚洲(ocpasia.org)/UALink/OIF官网；OCP/JEDEC/PCI-SIG官网Cloudflare 403连续多日、Bing中文污染
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120；pip需--break-system-packages+清华源

## MEMORY.md安全与记忆流
- 直写屏蔽：memory_overwrite_blocked=True + deep_dream_enabled=False双保险；Deep Dream蒸馏写目标已重定向Candidate.md（追加+时间戳分节）；遗留：evolution _ALLOWED_TOOLS需显式排除MEMORY.md
- Candidate.md双用途（文件修改提案+自动记忆提案）；不在manager.py索引范围（合并前不可检索符合候选语义）；MEMORY.md现7.4KB超5KB上限待瘦身
- 定时中断影响：08-09/10/16三期日报缺失；github-daily-rank 08-13~16未生成——监控连续性缺口待恢复

## 调研与质量工具
- 调研runner v1.8分档：39任务depth字段（11 deep/28 track）；deep档≥30KB读全文/丰度多维；verify反向激励（<15KB WARN）；跨组去重软化=一行交叉引用
- TOC锚点病根（08-17）：GitHub slug=删标点非转连字符；60+文件190~333处错配已dry-run未批改；需专门slug校验器
- 调研教训（08-25）：版本登记必须回查API时间戳勿凭提交直觉（SPARe登记v1实为v3），核心论文版本列绑定id_list轮询；关键词盲区兜底="最近提交+关键词扫描"（BSR语义簇逃逸三查询面被捕捉）

## 研究跟踪信号
- KVCache三级（HBM→DRAM→SSD/远端）2025-2026拐点年：SGLang HiCache定义范式、Mooncake开源事实标准、华为vLLM-Ascend三后端最完整；vLLM×Mooncake实证命中1.7%→92.2%=3.8×吞吐+46×TTFT
- MoE主线：vllm K3 Refactor三日连发（08-23~25）K3生态信号增强；Kimi K3 2.8T/104B激活/16-of-896专家；调度RoutePack +8.85%/14.89%、TAOT 1.43x；Skymizer HTX-301 $19K跑671B；Load Hijack安全攻击面
- 新方向：walgit 915★/2天单二进制无状态git server（S3/GCS后端无DB/无leader）；UALink进入"落地验证"（4规范族4/7+ODCC测试服务+Netforward原型）；存储超级周期财报+价格双印证（佰维71.66亿扭亏/大普微+531%/库存4周/价格12倍）
- DSV4：vllm prefill预取优化+CuMemAllocator.discard()、DSV4-DGX-Spark 216★（三日+131）单机量化渗透；deepseek-harness 96h破129,607★、dsh生态"标准化"阶段
- 可靠性追踪（08-25）：周一公告批次验证兑现，训练侧容错/checkpoint零新论文=平台期第二数据点待09-01复核；VCCL仍v2降频轮询；FT-HSDP v1稳定7个月+；源2搜索页连续第六日失败已正式移除
- openai-agents-python v0.21.0沙箱安全三线+审批resume修复；OpenBMC 2.18.0（Yocto 5.2新增NVIDIA/Qualcomm/AMD）；openUBMC 26.06社区版

## Dream distillation (2026-08-26 23:53)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：否决AB双环境审查，应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式

## 深度分析铁律
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢）；"帮我深度分析"不触发=保守策略；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故根因）
- **声称完成≠真正落实**：changelog声明未全文档链同步已四次重演（PXE口径/G6拆层/M2·M9/C17~C20），修复必须回写清单+逐文档核验闭环

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件（用户显式指令优先）；log追加统一kb-log-append.py、存量重排kb-log-reorder.py
- 归档模式：MEMORY git历史→memory.history.md；深度洞察→08-14 archive（引用阅读不写入）；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；跨目录交叉链接需../../前缀；死链检查必跑
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17新价同用量+186%；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；HTTPS/SSH双通道交替备用（push脚本缺失时用HTTPS origin通道）
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；web_search因Zhipu key失效持续不可用；DCD全渠道403；Baidu安全验证频繁拦截；稳定源=TechCrunch/STH/爱集微/NVIDIA Newsroom/arXiv/CNCF/SemiEngineering/Bing；TI官网+PDF直连可用，mouser/digikey/onsemi/FTDI 403；访问方式查表source-access-lookup.py
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120（新会话生效）

## 🖥️ 超节点项目（08-26 密集推进，当前主战场）
- 关键拍板：OOB端口位置判定柜号（PMC固件不可改）；计算节点CX7预留CX8；FSW=柜内scale-up交换节点、柜间DAC相邻互联；Storage TOR在存储柜内；交换网络柜纯scale-out无OOB（spine远端/leaf近端）；保留已有备
- Scale-Out每节点4×CX7（08-26 19:30拍板，2 rail×2卡）：编址P1=`10.3.<R>.<S>`/P2=`S+128`/P3=`S+64`/P4=`S+192`，台账2353→2609零重叠复验；脚本四件套同步（plan.yaml/gen_ip_plan.py/scaleout_net_config.sh/verify_net_config.sh，IP路由表31~34/4 rule/systemd/NM）
- 上电模型v1.3：阶段P0~P7含P4.5冷却/P5.5固件基线/P6.5节点主电（12V→54V GPU，coolant-gated，4节点/组）；G4拆G4a(骨干,P4)/G4b(下联,P6.5)；P1 DHCP=Kea HA failover pair；WDT移P7末步；P0新增inter-rack topology matrix；四视图时序图已落盘
- 待决策5项：scale-up形态A/B（决定10.4编址）；OOB交换机option82注入能力（G2柜ID自动化前提）；OOB汇聚台数（推荐2+2 HA）；MAC去rack化（推荐，柜ID载体泛滥根因对策）；SD1独立OOB接入（推荐ACC-09）；板载BMC供电域需硬件确认；gate SSOT落点未定
- 上电原则：先冷后电（与08-07固件先例一致）；G4.5硬gate五级就绪；CDU供电来源未定义、flag信号链未设计、泵N+1关联缺失、漏液联动未定义、风冷阈值缺失等7类执行缺口（P0×3/P1×3/P2×1）
- 整改映射（08-26）：13项建议（H/M/L/R编号）三态=6已固化需验收/4已论证待执行/3新增待冻结；关键路径POC=BF3 PXE T1~T8+Scale-Up语义（须M2~M5窗口完成）；编址回写4处修订为P0

## 行业趋势锚点
- 模型竞争从「综合智能」转向「agentic性价比/每任务成本」；安全范式从「拦截」转向「降级路由」；四厂商版本管理分化（Google数字快跑/OpenAI代号变体/Anthropic双轨/DeepSeek快照流水线）——「版本去仪式化」延续（08-25主线）
- 液冷渗透率：AI芯片2025 33%→2026 53%→2027~60%（TrendForce）；NVIDIA 15%提价→HBM 2027或+50%；钽电容近3倍涨幅（AI需求CAGR 62%，刚果(金)占51%矿产，替代=固体铝电解）
- AMD客户端x86份额首破30%（Q2 30.3%，1995年以来Intel首破70%）；燧原科创板IPO（募资60亿，国产GPU四小龙资本化加速）；Gemini 3.7 Flash发布（agentic性价比新维度）；Claude Opus 5同价加量
- 硬件化容错新趋势（scarHW+VCCL primary-backup QP汇聚）；arXiv搜索页连续7日0命中→改用cs.DC/cs.LG recent全量扫描（连续两日验证有效）
- 调研节奏：学术活跃/产业沉寂错位第3日（CNCF零增量第2日、国产源连续5日空缺）；可靠性平台期第三数据点；KubeCon China 09-07上海（PyTorch Conference首次并入）
- 跨组去重惯例：硬件规格类（Helios/Intel三架构/NVIDIA提价/zHBM）归hardware组，架构机制/软件栈/云原生归tech组，厂商资本动态归market/vendor组——各日期文件一行交叉引用不重写

## Dream distillation (2026-08-27 23:57)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：否决AB双环境审查，应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式

## 深度分析铁律（08-17）
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py实现："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故根因）
- 验证点：下次深度分析日志应出现"📝 Context summary injected"/"🧠 Deep-analysis fresh context"

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件（08-14省token，用户显式指令优先）；log追加统一kb-log-append.py、存量重排kb-log-reorder.py；跨组调研需去重核验（重复仅交叉引用不重收）
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；深度洞察→08-14 archive（引用阅读不写入）；SemiAnalysis 23篇→07_industry-research/99_other/；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；跨目录交叉链接需../../前缀；死链检查必跑
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17峰谷新价生效同用量+186%（flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；HTTPS/SSH双通道交替备用；push失败检查~/.git-credentials与token有效性（08-27双通道失效教训）
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；DCD全渠道403；访问方式查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local
- 源状态：web_search因Zhipu key失效不可用；中文源波动大（Baidu桌面连续被拦/Bing中文分词失效），sogou-general为稳定中文渠道、Baidu移动端08-27复活可作常驻源；稳定源=TechCrunch/STH/爱集微/NVIDIA Newsroom/arXiv/CNCF/TechTarget/Asset Panda
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120（新会话生效）
- URL验证与定位：标题级条目URL必须先经API/RSS验证再写入（STH猜slug致404教训）；WP REST API `wp-json/wp/v2/search?search=<kw>`可精确定位文章URL；arXiv URL经export.arxiv.org API二次验证

- **提案（2026-08-28）kb-daily-effort-analysis.py 性能优化**：今日运行 >17min 卡死被 kill（git log --follow 对 89 文件逐文件全历史遍历，每文件最多 10s 超时）。建议改为单次 `git log --all --follow --name-only` 或 `git rev-list` 批量解析代替逐文件 --follow；或增加 --fast 模式（跳过修订次数统计，仅四分类+AI 比重）。日报产出结构/AI 健康度模块目前依赖该脚本，超时会导致模块降级。
- **提案（2026-08-28）日报采集竞态防护**：data-gather 在 07:52 运行，而 07:55 仍有 [AI] 提交（313300120）落在窗口内——日报脚本建议延迟到 08:15 运行，或在 data-gather 前先 `git status` 补查未提交文档（技能已有此检查，但脚本本身未集成）。
## Dream distillation (2026-08-28 23:53)

## 用户核心原则
- AI不直接删任务/如实报告/不替用户做准入判断；文件操作=改前查头部标记、永不rm用mv+日期后缀、改后更新index/log
- 定时任务输出必须飞书（web渠道session中断即失效）；周报周日15:00、专项报告周日22:00；任务名=稳定锚点
- 系统三位一体：AI×知识管理探索+服务器产销研知识库+个人笔记；AI探索是手段、业务沉淀是主线、投入≤40%红线；内容经受控管线（暂存→加工→沉淀）
- 文档验收=结论先行+MECE+上下文加注+数据来源三层依据；开源选型=活跃度+描述+内容三重校验（防star通胀）
- AI工具观：AI是工具非目标；产出=毛利非净利需二次加工；防降智=判断力/第一性原理/跨域联想不可外包；文档多≠懂得多
- 战略收敛期（08-14决策）：知识库搭建达阶段→暂停扩张让系统正常运行；后续投入=Claude Code+数据源质量+本地算力（RTX 5060 8G跑7B INT4）
- 深度分析：质量>token（"没有质量的输出再节约token也是浪费"）；默认落盘+commit永不问"要不要处理"；当轮分析当轮落盘；18:00后对话输出一律落盘
- 系统修改策略（08-17定案）：否决AB双环境审查，应用环境直改+强保护（git回滚+tmp/bak+log）；改前确认可回滚→改后立即commit→异步push→log追加；破坏性操作先问用户
- MEMORY.md仅人工维护；自动记忆与文件修改提案统一走Candidate.md；禁用"要不要我处理X"句式
- 价值闭环（08-28洞察）：系统瓶颈=消费+治理（生产超载）；内容价值V=消费×决策×执行；矛盾双重复利指数积累（Lehman第2定律+回写率52%实证）；三层裁判L1自动化门禁→L2用户决策点→L3外部评审；KPI应从产出量切为决策点关闭数/回写执行率/矛盾存量、决策积压率>产生率触发降产（提议待用户定夺）

## 深度分析铁律（08-17）
- 五条铁律：必须走knowledge-doc-writer skill；未落盘=未完成（write+log+commit三缺一禁止收尾）；≥8 turns或≥3次工具调用才允许完成；质量>token；当轮分析当轮落盘
- agent_stream.py实现："深度分析"前缀→重置上下文（仅system+当前消息，旧历史flush_memory不丢；"帮我深度分析"不触发=保守策略）；turns<5压缩分支已补flush+summary注入（修复189→7丢85%事故根因）
- 验证点：下次深度分析日志应出现"📝 Context summary injected"/"🧠 Deep-analysis fresh context"
- ASCII图/代码块必须一次写纯英文（中文注释→R1违规；08-28 29处修复教训）

## 系统治理方法论
- 文档SSOT：TOC倒序/log正序/ASCII图/断言出处/交叉链接/头部注解；13谬误自检；不编造引用/百分比；多源三角验证
- 索引治理：README条目库+index自动生成+log全局账本三职责分离；01_survey日报默认只写日期文件（08-14省token，用户显式指令优先）；log追加统一kb-log-append.py、存量重排kb-log-reorder.py；日报前必须跑git status补查晚提交（08-28竞态教训：commit晚于data-gather漏计2深度文档）
- 归档模式：MEMORY git历史→memory.history.md（956KB只读）；深度洞察→08-14 archive（引用阅读不写入）；SemiAnalysis 23篇→07_industry-research/99_other/；同源对话可多专题拆分归档
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；跨目录交叉链接需../../前缀；死链检查必跑（08-28发现路径层级错误是纯机械错误，应进交付门禁）
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17峰谷新价生效同用量+186%（flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push异步触发绝不等待（git-push-async.log）；远程固定SSH 443（github.com HTTPS直连超时不可达）；自动化环境密钥必须无passphrase（带passphrase→BatchMode无法签名）、凭据导入即验证（PAT 401/gh token失效）；待用户将cowkb-main-push公钥添加至GitHub后恢复push
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；中文搜索不稳（Baidu持续安全验证拦截）；web_search因Zhipu key失效不可用；DCD全渠道403；稳定源=TechCrunch/STH/爱集微/NVIDIA Newsroom/arXiv/CNCF/DCK/TrendForce/LWN；访问方式查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120（新会话生效）
- 超节点一致性治理：consistency-scan.py v2.0（R1-R27全规则/6维度/全库基线296篇1749处）+ consistency-rectify.py（--plan/--apply/--verify三模式闭环）；治理总纲master v2.1三合一（登记表58条+审计v2.0+扫描工具）；DECISIONS.md已建（DEC-001~009）；C系列锚点文档已加取代声明
- 扫描脚本经验：R20术语用"文档级混用检测"（权威+变体并存才报）防爆炸；R21链接解析先剥#锚点；R22版本头格式兼容`版本=`/`文件状态=`变体；--rules子集时独立规则（R13）需兜底防StopIteration
- 治理元层教训（M1-M8）：治理资产（index/log/登记表）自身更新无事件驱动→5日失守；SSOT换代需反向取代标注；编号前缀需注册表统一；审计快照可能过时（反馈基于早间状态需核对时间基准）

## 工程目录与项目快照
- 超节点目录已迁移：07_industry-research/10_supernode-rack（110文件）→02_rd/02_project/01_superpod（109个git mv平铺，保内部互链2776+处）；冲突文件备份tmp/bak/supernode-rack-merge-2026-08-28/；绝对形式链接迁移需按新基准重算
- 项目知识场景（08-28）：五类升级（管理→状态机/决策→ADR/过程→迭代轨迹/交付件→验证状态/参考→来源分级）+新增_manifest/_rules/_index三层；模板在02_rd/02_project/_template/
- 超节点存储G3.5（08-28）：BF3无硬件KV引擎（vs BF4）→SPDK自研软件路径唯一可行；容量口径2台实配1474T vs 配额2560T待P0确认；存储网VLAN 102/10.2
- ⏳ 待办：用户添加SSH公钥后验证push；超节点P0冻结会（D1 BF3文档/D2 matrix口径/D3 功耗）

