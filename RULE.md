# RULE.md — 工作空间规则

## 📁 目录
~/cow/: memory/ knowledge/ spec/ scripts/ skills/ websites/ tmp/(bak) conversation-log/ import/

## 🚨 文件铁律
1. 永不 rm — mv 到 tmp/bak/<原因>-<日期>/
2. 改前查头部标记（AUTO-GENERATED/DO NOT EDIT/MANAGED_BY）→ 生成工具改
3. 破坏性操作先问用户
4. tmp/bak 是废弃区 — 不引用，确认未替代并迁出后方可用
5. 改四全局文件前三思 — 不确定写 Candidate.md 提案人工审核导入
6. import/ 素材批判使用 — 关键量化数据须独立源交叉验证

## ⚖️ 优先级（冲突自上而下）
L1🛑安全红线（否定，不可覆盖）> L2📋本文件 > L3🧠AGENT.md > L4🤖系统默认；负面>正面，具体>模糊；永不泄露密钥，不确定先问

## 🧠 MEMORY.md 管控
≤5KB；**仅人工维护**——禁止 Agent 自动写入/覆写；Agent 自动记忆（每对话+Deep Dream 蒸馏）一律写 `Candidate.md`，人工审核后并入 MEMORY.md；RULE/AGENT/USER 同理（修改提案走 Candidate.md）

## 📦 存储规则（按频率）
| 类型 | 位置 | 频率 |
|:--|:--|:--:|
| Agent/用户 | AGENT·USER.md | 季/年 |
| 长期决策（人工审核后） | MEMORY.md | 月 |
| 自动记忆提案 | Candidate.md | 日~随用 |
| 当天进展 | memory/YYYY-MM-DD.md | 日 |
| 行业动态/归档 | 01_survey·sources | 日~一次 |
| 方法论/临时 | concepts·tmp | 月/随用 |
判据：>1周不放 memory/；<1月不放 MEMORY.md；自动记忆一律 Candidate.md（人工审核后才可入 MEMORY.md）

## 🔄 工作流
1. 技术材料→立即归档 knowledge/；建文档→先查库避免重复；输出自检：出处/格式/深度
2. 专题输出→commit（cowagent，[AI] <type>(<scope>): <summary>）+ 一次异步 push（--async）；日报(6:55)前检查同步；收尾查未归档
3. git：origin=HTTPS；origin-old=SSH 备用
4. 三件套（根 README/index/log 禁编辑）：知识文件→摘要写 tmp/→kb-log-append.py 追加根 log.md（tmp 不含分节头，--section 传参）；根 index 由 kb-global-index.py 刷新；2026-08-19 起全库无子目录 index/log（不写任何子目录 index.md/log.md），子目录 README.md 保留（描述长期内容）
5. 调研类更新→只写 01_survey/<子目录>/YYYY-MM-DD.md（定时调研不写 log；深度分析追加摘要到根 log.md）

## 🎯 深度分析铁律（08-17 质量事故后定，优先于一切 token 节约）
1. **必须走 knowledge-doc-writer skill**：深度分析启动即 read SKILL.md，按 6 步工作流 + Q6 质量标准执行；禁止裸写
2. **未落盘 = 未完成**：Done 前 check gate——文档已 write + log 已追加 + git 已 commit，任一缺失禁止收尾
3. **最小工作量**：深度分析 ≥8 turns 或 ≥3 次工具调用（检索+读+写）才允许完成；浅层回答不叫深度分析
4. **质量 > token**：质量不合格的输出再省 token 也是浪费；上下文臃肿时优先压缩/检索而非牺牲质量
5. **当轮分析当轮落盘**：不拖到"遗留事项"；分析产出即落库+log+commit（08-17 曾有 4 个会话 write=0 草草 Done 的教训）
