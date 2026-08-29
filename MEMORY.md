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
- 批量导入质量门禁：量化检测按行计≥3行、数字+单位紧邻；代码块内中文一律违规（含中文占位符）；跨目录交叉链接需../../前缀；死链检查必跑
- Token成本：缓存未命中57.1%最大成本（08-15实测）；8/17峰谷新价生效同用量+186%（flash miss输入1→1.5/3.0、输出2→4.5/9.0；pro输出6→13.5/27.0）；deepseek_usage固定名落盘可增量复用
- 架构：Harness=Bridge枢纽；五层依赖单向化；持久化三级+每日23:50蒸馏；检索keyword-only（高杠杆=启用embedding ¥30-60）
- git+定时：AI操作后自动add+commit（cowagent+[AI]）；push只触发动作绝不等待（git-push-robust.py --async）；日报前6:55检查同步；HTTPS/SSH双通道交替备用
- 网络应对：web_fetch直连>搜索；微信三要素=iPhone UA+chksm清零+剥离poc_token；中文搜索不稳（Baidu移动端/Bing时好时坏）；web_search因Zhipu key失效不可用；DCD全渠道403；稳定源=TechCrunch/STH/爱集微/NVIDIA Newsroom/arXiv/CNCF；访问方式查表source-access-lookup.py：rss/api>jina>static>web_fetch>js>browser>local
- 工具环境：Agent Reach v1.5.0+mcporter；playwright默认禁用；云端禁微信自动登录；agent_max_steps 50→120（新会话生效）
