# 代码质量评估维度、方法与工具

> **概要**: 完整覆盖代码质量的**评估维度 → 评估方法 → 参考提示词 → 配套工具**全链路
>
> **关键词**: (待补充)

---

## 📑 目录

- [一、代码质量七维评估模型](#一代码质量七维评估模型)
  - [1.1 各维度定义](#11-各维度定义)
  - [1.2 维度权重参考（按项目类型）](#12-维度权重参考按项目类型)
- [二、各维度的评估方法](#二各维度的评估方法)
  - [2.1 正确性评估](#21-正确性评估)
  - [2.2 安全性评估](#22-安全性评估)
  - [2.3 性能评估](#23-性能评估)
  - [2.4 可维护性评估](#24-可维护性评估)
  - [2.5 可读性评估](#25-可读性评估)
  - [2.6 可测试性评估](#26-可测试性评估)
  - [2.7 可部署性/可靠性评估](#27-可部署性可靠性评估)
- [三、质量评估参考提示词（Prompt）](#三质量评估参考提示词prompt)
  - [3.1 通用质量审查 Prompt](#31-通用质量审查-prompt)
- [总评](#总评)
- [各维度详情](#各维度详情)
  - [正确性（X/5）](#正确性x5)
  - [安全性（X/5）](#安全性x5)
- [优先级排序](#优先级排序)
  - [3.2 安全性专项 Prompt](#32-安全性专项-prompt)
  - [3.3 性能审查 Prompt](#33-性能审查-prompt)
  - [3.4 可读性/可维护性 Prompt](#34-可读性可维护性-prompt)
  - [3.5 完整 CR Prompt（含上下文感知）](#35-完整-cr-prompt含上下文感知)
- [项目信息](#项目信息)
- [PR 信息](#pr-信息)
- [审查要求](#审查要求)
- [四、配套工具与集成方案](#四配套工具与集成方案)
  - [4.1 工具矩阵](#41-工具矩阵)
  - [4.2 典型 CI 集成流水线](#42-典型-ci-集成流水线)
  - [4.3 pre-commit Hooks 推荐配置](#43-pre-commit-hooks-推荐配置)
  - [4.4 质量门禁（Quality Gate）阈值建议](#44-质量门禁quality-gate阈值建议)
- [五、AI 时代的质量评估新视角](#五ai-时代的质量评估新视角)
  - [5.1 质量评估的新维度](#51-质量评估的新维度)
  - [5.2 质量观的转变](#52-质量观的转变)
  - [5.3 AI 生成代码的常见陷阱](#53-ai-生成代码的常见陷阱)
- [六、代码审查效能度量指标体系](#六代码审查效能度量指标体系)
  - [6.1 核心度量指标](#61-核心度量指标)
  - [6.2 度量数据采集方式](#62-度量数据采集方式)
  - [6.3 质量仪表盘示例（Grafana / Datadog）](#63-质量仪表盘示例grafana-datadog)
- [七、静态分析工具深度配置指南](#七静态分析工具深度配置指南)
  - [7.1 SonarQube 质量门禁配置](#71-sonarqube-质量门禁配置)
  - [7.2 Semgrep 规则配置示例](#72-semgrep-规则配置示例)
  - [7.3 CodeQL 查询配置示例（GitHub Actions）](#73-codeql-查询配置示例github-actions)
  - [7.4 Trivy + Snyk 安全扫描配置](#74-trivy-snyk-安全扫描配置)
  - [7.5 Lizard 圈复杂度 CLI 配置](#75-lizard-圈复杂度-cli-配置)
- [八、OWASP Top 10 代码审查安全清单（深度版）](#八owasp-top-10-代码审查安全清单深度版)
  - [8.1 A01: 失效的访问控制](#81-a01-失效的访问控制)
  - [8.2 A02: 加密机制失效](#82-a02-加密机制失效)
  - [8.3 A03: 注入](#83-a03-注入)
  - [8.4 A04: 不安全的设计](#84-a04-不安全的设计)
  - [8.5 A05: 安全配置错误](#85-a05-安全配置错误)
  - [8.6 A06: 易受攻击和过时的组件](#86-a06-易受攻击和过时的组件)
  - [8.7 A07: 身份验证与会话管理失效](#87-a07-身份验证与会话管理失效)
  - [8.8 A08: 软件和数据完整性失效](#88-a08-软件和数据完整性失效)
  - [8.9 A09: 安全日志与监控不足](#89-a09-安全日志与监控不足)
  - [8.10 A10: 服务端请求伪造（SSRF）](#810-a10-服务端请求伪造ssrf)
- [九、AI 代码审查集成实践](#九ai-代码审查集成实践)
  - [9.1 AI CR Skill 的典型架构](#91-ai-cr-skill-的典型架构)
  - [9.2 AI 审查的量化成果参考](#92-ai-审查的量化成果参考)
  - [9.3 AI CR 分级策略](#93-ai-cr-分级策略)
  - [9.4 定制团队专属审查规则](#94-定制团队专属审查规则)
  - [9.5 CI/CD 集成 AI CR](#95-cicd-集成-ai-cr)
- [十、高级审查提示词模式](#十高级审查提示词模式)
  - [10.1 思维链审查 Prompt](#101-思维链审查-prompt)
- [步骤 1: 理解变更背景](#步骤-1-理解变更背景)
- [步骤 2: 代码逻辑验证](#步骤-2-代码逻辑验证)
- [步骤 3: 安全影响分析](#步骤-3-安全影响分析)
- [步骤 4: 性能影响评估](#步骤-4-性能影响评估)
- [步骤 5: 整合审查结论](#步骤-5-整合审查结论)
  - [10.2 多视角审查 Prompt（模拟不同角色）](#102-多视角审查-prompt模拟不同角色)
- [视角 1: 安全工程师](#视角-1-安全工程师)
- [视角 2: 性能架构师](#视角-2-性能架构师)
- [视角 3: 业务 Owner](#视角-3-业务-owner)
- [最终综合](#最终综合)
  - [10.3 假名代码审查 Prompt（消除偏见）](#103-假名代码审查-prompt消除偏见)
  - [10.4 AI 生成代码专用审查 Prompt](#104-ai-生成代码专用审查-prompt)
  - [10.5 增量审查 Prompt（大型 PR）](#105-增量审查-prompt大型-pr)
- [优先级排序](#优先级排序)
  - [第一层 (阻塞级) — 必须修复](#第一层-阻塞级-必须修复)
  - [第二层 (重要级) — 建议修复](#第二层-重要级-建议修复)
  - [第三层 (改进级) — 备注](#第三层-改进级-备注)
- [输出要求](#输出要求)
- [十一、多语言审查要点速查表](#十一多语言审查要点速查表)
  - [11.1 Python](#111-python)
  - [11.2 Java](#112-java)
  - [11.3 Go](#113-go)
  - [11.4 JavaScript / TypeScript](#114-javascript-typescript)
  - [11.5 Rust](#115-rust)
- [十二、基于 AST + 知识图谱的深度代码分析](#十二基于-ast-知识图谱的深度代码分析)
  - [12.1 分析框架对比](#121-分析框架对比)
  - [12.2 在 Code Review 中的应用场景](#122-在-code-review-中的应用场景)
  - [12.3 推荐工具](#123-推荐工具)
- [十三、代码审查反模式](#十三代码审查反模式)
  - [13.1 流程反模式](#131-流程反模式)
  - [13.2 沟通反模式](#132-沟通反模式)
  - [13.3 质量评估反模式](#133-质量评估反模式)
- [十四、审查质量自动化保障体系](#十四审查质量自动化保障体系)
  - [14.1 多层次自动化门禁架构](#141-多层次自动化门禁架构)
  - [14.2 门禁配置模板（YAML）](#142-门禁配置模板yaml)
  - [14.3 超时自动升级机制](#143-超时自动升级机制)
- [十五、代码坏味道（Code Smell）速查与修复指引](#十五代码坏味道code-smell速查与修复指引)
  - [15.1 命名相关坏味道](#151-命名相关坏味道)
  - [15.2 函数相关坏味道](#152-函数相关坏味道)
  - [15.3 类相关坏味道](#153-类相关坏味道)
  - [15.4 架构坏味道](#154-架构坏味道)
- [交叉引用](#交叉引用)
- [参考文件](#参考文件)
- [Changelog](#changelog)

---

---

## 一、代码质量七维评估模型

将代码质量分解为 **7 个独立维度**，每个维度有明确的定义与评估标准：

```text
+---------------------------------------------+
|              代码质量评估                     |
|  +-----+------+------+------+------+------+ |
|  |正确性|安全性|性能  |可维护|可读性|可测试| |
|  |     |      |      | 性   |      | 性   | |
|  +-----+------+------+------+------+------+ |
|  +------------------------------------------+ |
|  |             可部署性/可靠性                | |
|  +------------------------------------------+ |
+---------------------------------------------+
```

### 1.1 各维度定义

| # | 维度 | 定义 | 反面（低质量信号） |
|:-:|:-----|:-----|:------------------|
| 1 | **正确性** | 代码实现了预期的功能，处理了所有边界情况和异常路径 | 单元测试失败、边界值未处理、异常未捕获 |
| 2 | **安全性** | 代码无已知漏洞，敏感信息受保护，遵循最小权限原则 | SQL注入、XSS、硬编码密钥、越权访问 |
| 3 | **性能** | 代码在合理的时间和空间消耗内完成任务 | N+1查询、内存泄漏、不必要的重复计算 |
| 4 | **可维护性** | 代码易于修改、扩展和重构 | 高圈复杂度、深度嵌套、魔法数字、重复代码 |
| 5 | **可读性** | 代码易于人类阅读理解 | 命名晦涩、缺少注释、过长函数、混乱格式 |
| 6 | **可测试性** | 代码易于编写自动化测试 | 紧耦合、全局状态、硬编码依赖、难以 Mock |
| 7 | **可部署性/可靠性** | 代码在生产环境稳定运行，易回滚、易监控 | 缺少日志、配置硬编码、无健康检查、幂等问题 |

### 1.2 维度权重参考（按项目类型）

| 项目类型 | 正确性 | 安全性 | 性能 | 可维护性 | 可读性 | 可测试性 | 可部署性 |
|:---------|:------:|:------:|:----:|:--------:|:------:|:--------:|:--------:|
| 金融/支付系统 | 30% | 25% | 10% | 10% | 5% | 10% | 10% |
| 高并发中间件 | 20% | 15% | 30% | 10% | 5% | 10% | 10% |
| SaaS 业务系统 | 20% | 15% | 10% | 20% | 10% | 15% | 10% |
| 嵌入式/固件 | 25% | 20% | 20% | 10% | 5% | 10% | 10% |
| AI/ML 管线 | 25% | 10% | 20% | 10% | 10% | 15% | 10% |
| 内部工具/原型 | 25% | 10% | 5% | 15% | 15% | 15% | 15% |

> **原则**: 不同项目类型权重应不同。CR 时先确认项目类型，再按权重分配审查精力。

---

## 二、各维度的评估方法

### 2.1 正确性评估

| 方法 | 方式 | 工具 |
|:-----|:-----|:------|
| **自动化测试** | 跑单元测试/集成测试，检查通过率和覆盖率 | pytest, Jest, JUnit, Go test |
| **边界值分析** | 检查数组越界、空指针、数值溢出等边界情况 | 静态分析工具 + 人工 |
| **异常路径审查** | 检查 try-catch、错误返回码、fallback 逻辑 | 人工审查 + AI CR |
| **Diff 对比** | 对比修改前后的行为差异 | Reviewable, GitLab diff |
| **形式化验证** | 对关键路径用 TLA+/Alloy 建模验证高阶逻辑 | TLA+ Toolbox |

**AI 辅助技巧**:
> "让 AI 从**反向测试**角度审查：'这段代码在什么输入下会崩溃？API 在什么并发场景下会返回错误？' — 这种逆向思维比正向检查更高效。"

### 2.2 安全性评估

| 方法 | 方式 | 工具 |
|:-----|:-----|:------|
| **SAST（静态应用安全测试）** | 自动扫描源码发现漏洞模式 | SonarQube, Semgrep, CodeQL, Fortify |
| **SCA（软件成分分析）** | 检测依赖库的已知漏洞 | Snyk, Dependabot, Trivy, OWASP DC |
| **Secret 检测** | 扫描硬编码密钥/密码/Tokens | GitLeaks, TruffleHog |
| **权限审计** | 检查接口是否有鉴权和权限校验 | 人工 + AI |
| **OWASP Top 10 检查** | 逐项对照最关键的 10 类风险 | OWASP 检查清单 |

**参考规则**:

- 所有用户输入必须校验和转义
- 所有数据库查询必须参数化
- 所有凭据必须通过环境变量/密钥管理服务注入
- 所有对外 API 必须有认证和限流

### 2.3 性能评估

| 方法 | 指标 | 工具 |
|:-----|:-----|:------|
| **复杂度分析** | 圈复杂度、认知复杂度、大 O 时间复杂度 | lizard, radon, CodeClimate |
| **热点检测** | 检测 N+1 查询、循环内调用、不必要的深拷贝 | New Relic, SkyWalking, pprof |
| **内存分析** | 检测内存泄漏、大对象分配、GC 压力 | Valgrind, heapprof, memory_profiler |
| **压测验证** | 关键路径做基准测试，对比改前改后 | k6, wrk, ab, JMeter |
| **SQL 分析** | 分析慢查询、缺少索引、全表扫描 | EXPLAIN ANALYZE, pg_stat_statements |

**圈复杂度阈值参考**:

| 等级 | 范围 | 含义 | 建议 |
|:-----|:-----|:------|:------|
| 🟢 低 | 1–10 | 结构清晰 | 无需重构 |
| 🟡 中 | 11–20 | 有一定复杂度 | 建议拆分 |
| 🟠 高 | 21–50 | 复杂，易出 Bug | 必须重构 |
| 🔴 极高 | 50+ | 不可测试 | 必须重写 |

### 2.4 可维护性评估

| 方法 | 指标 | 工具 |
|:-----|:-----|:------|
| **重复代码检测** | 重复率、Copy-Paste 片段 | PMD CPD, Simian, jscpd |
| **模块耦合度** | 扇入/扇出数、循环依赖 | Structure101, Dependency-Check |
| **代码行数** | 函数/文件/类的长度 | cloc, scc, SonarQube |
| **注释率** | 必要注释 vs 冗余注释的平衡 | 人工 + AI 判断 |
| **技术债评估** | 静态分析打出的技术债指数 | SonarQube Technical Debt Ratio |

**函数长度建议**:

| 语言类型 | 建议最大行数 | 理想行数 |
|:---------|:-----------:|:---------:|
| Python/JS/TS | 50 行 | 10–25 行 |
| Java/C# | 60 行 | 15–30 行 |
| Go | 80 行 | 20–40 行 |
| C/C++ | 80 行 | 20–40 行 |
| Rust | 60 行 | 15–30 行 |

### 2.5 可读性评估

| 方法 | 检查点 | 工具/方式 |
|:-----|:-------|:----------|
| **命名审查** | 变量/函数/类名是否自描述 | AI CR + 人工 |
| **格式化检查** | 是否符合语言的 Style Guide | prettier, black, gofmt, clang-format |
| **注释审查** | "为什么做"而非"做了什么" | 人工 |
| **文档同步** | 代码变更是否同步更新了文档 | AI 可检测 |
| **Review 友好性** | Diff 是否太大、是否混合了重构与业务变更 | GitLab review stats |

**核心原则**:
> 代码的可读性标准不是"我能看懂"，而是**"团队里最不熟悉这段代码的人能否在 5 分钟内理解它"**。

### 2.6 可测试性评估

| 方法 | 检查点 | 工具 |
|:-----|:-------|:------|
| **依赖注入** | 是否使用了依赖注入而非硬编码 new | 静态分析 + 人工 |
| **接口隔离** | 函数是否只依赖必要的参数 | 人工 |
| **全局状态** | 是否依赖全局变量/单例/静态方法 | 静态分析 |
| **Mock 友好** | 外部依赖是否可 Mock | 人工 |
| **测试覆盖** | 新增代码是否有对应测试 | JaCoCo, pytest-cov, istanbul |

**可测试性自检三问**:

1. 这个函数能否不启动整个系统就能单独测试？
2. 这个函数的外部依赖能否替换为 Mock/Stub？
3. 这个函数的输入输出是否清晰可验证？

### 2.7 可部署性/可靠性评估

| 方法 | 检查点 | 工具 |
|:-----|:-------|:------|
| **配置检查** | 配置是否外置、是否有配置校验 | 人工 + CI 检查 |
| **日志检查** | 错误路径是否有日志、日志级别是否合理 | 人工 + AI |
| **健康检查** | 是否有 /healthz、/readyz 端点 | 人工 |
| **幂等性** | 同一请求重复执行是否安全 | 人工 |
| **回滚检查** | 数据迁移/API 变更是否前向兼容 | 人工 |
| **优雅关闭** | 进程收到 SIGTERM 是否能优雅关闭 | 测试验证 |

---

## 三、质量评估参考提示词（Prompt）

以下提示词可直接用于 **AI Code Review 工具**（Cursor、Copilot、CodeReview Agent、自定义 LLM 脚本）或作为 **人类审查者的思考框架**。

### 3.1 通用质量审查 Prompt

```text
你是一位资深软件工程师，正在对以下代码变更进行 Code Review。
请按以下 7 个维度逐一评估，每维度给出：评分（1-5）、发现的问题、改进建议。

评估维度：
1. 正确性（Correctness）—— 逻辑是否正确，边界情况是否处理
2. 安全性（Security）—— 是否有安全漏洞
3. 性能（Performance）—— 是否有性能隐患
4. 可维护性（Maintainability）—— 代码是否易于修改扩展
5. 可读性（Readability）—— 代码是否清晰易懂
6. 可测试性（Testability）—— 代码是否易于测试
7. 可部署性（Deployability）—— 是否符合生产环境要求

输出格式：
## 总评
- 整体评分: X/5
- 最需关注维度: [维度名称]

## 各维度详情
### 正确性（X/5）
- ✅/⚠️/❌ [问题描述] — [改进建议]

### 安全性（X/5）
...

## 优先级排序
列出 TOP 3 最重要的问题及其修改建议。

代码 Diff：
```diff
[粘贴代码 diff]
```

```text

### 3.2 安全性专项 Prompt

```

你是一位安全工程师，请对以下代码进行安全审查。
严格对照 OWASP Top 10 检查以下风险：

1. 🔴 注入攻击（SQL/NoSQL/OS 命令/LDAP 注入）
2. 🔴 失效的认证和会话管理
3. 🔴 跨站脚本（XSS）
4. 🔴 失效的访问控制（越权/未授权）
5. 🔴 安全配置错误
6. 🔴 敏感数据暴露
7. 🔴 不安全的反序列化
8. 🔴 使用含已知漏洞的组件
9. 🔴 不足的日志与监控
10. 🔴 SSRF（服务端请求伪造）

对每个发现的风险：

- 标记风险等级 (Critical/High/Medium/Low)
- 指出具体的代码位置（行号）
- 给出修复示例代码

代码：
[粘贴代码]

```text

### 3.3 性能审查 Prompt

```

你是一位性能优化专家，请审查以下代码的性能问题。

重点关注：

1. 🔴 时间复杂度 —— 是否有不必要的循环/递归/重复计算
2. 🔴 N+1 查询 —— 循环内数据库或 API 调用
3. 🟡 内存使用 —— 不必要的对象创建、大对象持有、内存泄漏
4. 🟡 并发问题 —— 锁竞争、死锁、线程安全
5. 🟢 IO 优化 —— 不必要的序列化/反序列化、批量处理机会
6. 🟢 缓存机会 —— 热点数据是否可缓存

对每个问题：

- 严重程度 (Blocker/Critical/Major)
- 预期影响（如"每次请求多 50ms 延迟"）
- 优化后的预估效果
- 优化示例代码

代码：
[粘贴代码]

```text

### 3.4 可读性/可维护性 Prompt

```

你是一位技术专家，请审查以下代码的**可读性**和**可维护性**。

评分维度（1-5分）：

- 命名清晰度：函数/变量/类名是否自描述
- 函数粒度：函数长度是否适当、职责是否单一
- 注释质量：注释是否解释"为什么做"，而非重复"做了什么"
- 设计模式：是否使用了适当的模式、是否过度设计
- 一致性：是否遵循了项目的既有风格和约定

对每个问题：

- 给出改进前后的代码示例
- 说明改进后的可读性/可维护性提升在哪

代码：
[粘贴代码]

```text

### 3.5 完整 CR Prompt（含上下文感知）

```

你正在审查一个 Pull Request，项目上下文如下：

## 项目信息

- 项目类型: [金融/高并发/SaaS/嵌入式/AI管线/内部工具]
- 语言: [Python/Go/Java/TS/...]
- 框架: [Django/Spring/Next.js/...]
- 团队规范: [链接到团队编码规范]

## PR 信息

- 变更范围: [前端/后端/数据库/配置]
- 变更类型: [新功能/Bug修复/重构/性能优化]
- 关联 Issue: #[issue编号]

## 审查要求

1. 按 7 维度质量模型逐一评估（正确性·安全性·性能·可维护性·可读性·可测试性·可部署性）
2. 对每个问题标注严重级别（Critical/Major/Minor/Suggestion）
3. 对 Critical 和 Major 问题必须给出修复代码示例
4. 最后给出 TOP 3 必须修复的问题（基于项目类型权重）

代码 Diff:
[粘贴代码 diff]

```text

---

## 四、配套工具与集成方案

### 4.1 工具矩阵

| 类别 | 工具 | 适用语言 | 集成方式 |
|:-----|:-----|:---------|:---------|
| **综合静态分析** | SonarQube | 全语言 | CI Pipeline / IDE 插件 |
| **综合静态分析** | CodeClimate | 全语言 | GitHub / GitLab 集成 |
| **综合静态分析** | Codacy | 全语言 | GitHub / GitLab / Bitbucket |
| **安全扫描** | Semgrep | 全语言 | CLI / CI / pre-commit |
| **安全扫描** | CodeQL | 全语言 | GitHub Actions |
| **安全扫描** | Snyk | 全语言 | CLI / CI / IDE |
| **安全扫描** | Trivy | 全语言 | CLI / CI |
| **Secret 检测** | GitLeaks | 全语言 | pre-commit / CI |
| **Secret 检测** | TruffleHog | 全语言 | CLI / CI |
| **复杂度分析** | Radon | Python | CLI / CI |
| **复杂度分析** | Lizard | 多语言 | CLI |
| **重复代码** | PMD CPD | Java/Python/JS/... | Maven/Gradle/CLI |
| **重复代码** | jscpd | 多语言 | CLI |
| **格式化检查** | Prettier | JS/TS/CSS/... | pre-commit / VSCode |
| **格式化检查** | Black | Python | pre-commit |
| **格式化检查** | gofmt | Go | pre-commit / IDE |
| **测试覆盖** | pytest-cov | Python | CI |
| **测试覆盖** | JaCoCo | Java | Maven/Gradle |
| **测试覆盖** | Istanbul | JS/TS | npm/CI |
| **依赖审查** | Dependabot | 全语言 | GitHub |
| **依赖审查** | Renovate | 全语言 | GitHub/GitLab |
| **AI CR** | CodeReview Agent | 全语言 | CLI / Git Webhook |
| **AI CR** | Cursor CR Skill | 全语言 | Cursor IDE |

### 4.2 典型 CI 集成流水线

```

PR 提交
  |
  +-- ① 格式化检查 (prettier/black/gofmt) -- ❌ -> 自动修复或阻塞
  |
  +-- ② Secret 扫描 (GitLeaks/TruffleHog) -- ❌ -> 阻塞 ❗
  |
  +-- ③ 安全扫描 (Semgrep/CodeQL/Snyk) ---- ❌ -> 阻塞 (Critical 级)
  |
  +-- ④ 静态分析 (SonarQube/Radon) --------- ❌ -> 标记 + 报告
  |
  +-- ⑤ 单元测试 + 覆盖率 ------------------ ❌ -> 阻塞
  |
  +-- ⑥ AI Code Review --------------------- > 自动评论到 PR
  |
  +-- ⑦ 人工 Review ------------------------ ✅ -> 合并

```text

### 4.3 pre-commit Hooks 推荐配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.7
    hooks:
      - id: bandit
        args: [-ll, -c, pyproject.toml]
```

### 4.4 质量门禁（Quality Gate）阈值建议

| 指标 | 🟢 绿 | 🟡 黄 | 🔴 红 |
|:-----|:-----:|:-----:|:-----:|
| 圈复杂度（函数级） | ≤ 10 | 11–20 | > 20 |
| 重复代码率 | ≤ 3% | 3–10% | > 10% |
| 单元测试覆盖率 | ≥ 80% | 60–80% | < 60% |
| 新增 Bug 密度 | 0 / KLOC | ≤ 2 / KLOC | > 2 / KLOC |
| 安全漏洞 (Critical) | 0 | 0 | ≥ 1 |
| 技术债比率 | ≤ 5% | 5–20% | > 20% |
| 圈复杂度（文件级） | ≤ 30 | 30–60 | > 60 |
| 注释率 | 15–30% | 10–15% / 30–40% | < 10% / > 40% |

---

## 五、AI 时代的质量评估新视角

> **核心矛盾**: AI 生成代码的速度已超过人对代码的理解速度 — 这是 AI 辅助编程时代质量评估面临的最根本挑战。 — import/doubao/AI时代的软件质量观.md

### 5.1 质量评估的新维度

| 新维度 | 说明 |
|:-------|:------|
| **AI 可理解性** | AI 生成的代码是否能被人类审查者快速理解 |
| **上下文一致性** | 代码与项目既有风格、约束是否一致（AI 易"遗忘"上下文） |
| **幻觉检测** | AI 是否生成了不存在的 API/库/功能 |
| **测试充分性** | AI 代码是否配套了足够的测试（AI 常跳过测试） |

### 5.2 质量观的转变

| 传统 | AI 时代 |
|:-----|:--------|
| "写出正确的代码" | "审查并确认 AI 生成了正确的代码" |
| 代码质量是写出来的 | 代码质量是**审查出来的** |
| 审查重点: 语法和逻辑 | 审查重点: 业务上下文一致性 + 边界条件 |
| 测试是验证手段 | 测试是**对抗认知退化的锚定工具** |

### 5.3 AI 生成代码的常见陷阱

| 陷阱 | 表现 | 检测方式 |
|:-----|:------|:---------|
| **幻觉 API** | 调用不存在的库函数 | 编译检查 + 人工 |
| **忽略边界** | 不处理 Null/空值/异常 | 静态分析 + AI CR |
| **上下文丢失** | 风格/命名不一致 | AI CR 项目级审查 |
| **过度抽象** | 不必要的设计模式/过度工程 | 可读性评估 |
| **测试真空** | 生成功能但不生成测试 | 覆盖率检查 |

> 💡 **关键提醒**: 在 AI 辅助编程环境下，**测试不是质量保障的负担，而是维护团队认知掌控感的唯一手段**。写测试的过程，是迫使工程师真正理解 AI 生成代码行为边界的关键环节。

---

---

## 六、代码审查效能度量指标体系

> CR 的质量本身也需要度量 —— "如果不知道 CR 做得好不好，你就无法改进它。"

### 6.1 核心度量指标

| # | 指标 | 定义 | 目标值 | 衡量什么 |
|:-:|:-----|:-----|:------|:---------|
| 1 | **Review 覆盖率** | 被 CR 的 PR 数 / 总 PR 数 | ≥ 95% | 是否所有变更都经过审查 |
| 2 | **Review 参与率** | 实际参与 CR 人数 / 团队总人数 | ≥ 80% | 团队参与度，避免"一个人审所有" |
| 3 | **首次响应时间** | PR 提交到第一次 Review 评论的时间 | ≤ 4 小时 (业务日) | Review 是否及时 |
| 4 | **Review 周期** | PR 提交到合并的总时间 | ≤ 24 小时 (小变更) | 整体效率 |
| 5 | **缺陷拦截率** | CR 发现的 Bug / (CR发现的 + 线上发现的) | ≥ 80% | CR 的实际有效性 |
| 6 | **评论密度** | Review 评论数 / KLOC | 3–8 条/KLOC | Review 深入程度 |
| 7 | **评论采纳率** | 被采纳的评论 / 总评论 | ≥ 85% | Review 质量与团队信任 |
| 8 | **严重 Bug 漏检率** | 线上严重 Bug 中未在 CR 发现的占比 | ≤ 3% | CR 的底线有效性 |
| 9 | **平均 PR 大小** | 每次 PR 变更的行数 | ≤ 250 行/PR | PR 粒度是否合理 |
| 10 | **重新打开率** | 合并后重新打开的 Bug / 总 Bug | ≤ 5% | Reviewer 是否尽责 |

### 6.2 度量数据采集方式

```yaml
# 工具数据源映射
指标:
  首次响应时间: GitLab/GitHub API (MR/PR 时间线)
  Review 周期: GitLab/GitHub API (创建→合并时间差)
  覆盖率: GitLab/GitHub API (reviewed PRs / total PRs)
  评论密度: GitLab/GitHub API (comments / lines changed)
  PR 大小: GitLab/GitHub API (total lines added + deleted)
  缺陷拦截率: SonarQube + Bug 追踪系统 (BI 层面)
  参与率: GitLab/GitHub API (unique reviewers / team size)
```

### 6.3 质量仪表盘示例（Grafana / Datadog）

```text
+------------------------------------------------------+
|  📊 Code Review Quality Dashboard - W26              |
+------------------------------------------------------+
| Review Coverage  ################## 96%  🟢          |
| Avg First Response ################ 2.3h 🟢          |
| Review Cycle      ################ 5.7h 🟢          |
| Bug Leakage       ################ 1.2% 🟢           |
| PR Size (avg)     ################ 189 lines  🟡     |
| Participation     ################ 65%  🟡           |
| Comment Adoption  ################ 91%  🟢           |
+------------------------------------------------------+
| 🚨 Alerts: None  |  Top Reviewer: @alice (142 PRs)   |
+------------------------------------------------------+
```

---

## 七、静态分析工具深度配置指南

### 7.1 SonarQube 质量门禁配置

SonarQube 是最广泛使用的综合静态分析平台，其质量门禁（Quality Gate）是代码质量自动化的核心。

```yaml
# sonar-project.properties — 质量门禁配置示例
sonar.projectKey=my-service
sonar.projectName=My Service
sonar.language=python
sonar.sources=src/
sonar.tests=tests/
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.flake8.reportPaths=flake8-report.txt
sonar.python.pylint.reportPaths=pylint-report.txt

# 质量门禁阈值 (Quality Gate)
sonar.qualitygate.wait=true           # CI 等待门禁结果
sonar.qualitygate.timeout=300          # 超时时间（秒）

# 代码分析配置
sonar.exclusions=**/migrations/**,**/tests/**
sonar.sourceEncoding=UTF-8
sonar.cpd.exclusions=**/models.py    # 排除自动生成文件的重复检测
```

**质量门禁规则（Quality Gate Condition）**:

| 条件 | 阈值 | 行动 |
|:-----|:-----|:------|
| 新增代码覆盖率 | < 80% | ❌ 门禁失败 |
| 新增代码重复率 | > 3% | ❌ 门禁失败 |
| 新增代码通过率 | < 100% (阻塞级问题) | ❌ 门禁失败 |
| 新增 Bug | ≥ 1 | ❌ 门禁失败 |
| 新增安全热点 | ≥ 1 (Critical) | ❌ 门禁失败 |
| 技术债比率 | > 5% 新增 | ⚠️ 警告 |

### 7.2 Semgrep 规则配置示例

Semgrep 是新一代 SAST 工具，支持自定义规则和跨文件分析。

```yaml
# .semgrep/rules/python-security.yaml
rules:
  - id: sql-injection-django
    patterns:
      - pattern: |
          $QUERY = "SELECT ..." + $USER_INPUT + "..."
          ...
          cursor.execute($QUERY)
    message: "⚠️ SQL 注入风险: 用户输入直接拼接 SQL 查询"
    languages: [python]
    severity: ERROR

  - id: hardcoded-secret
    patterns:
      - pattern-regex: |
          (?:api_key|secret|password|token)\s*=\s*["'][A-Za-z0-9_-]{16,}["']
      - pattern-not-regex: |
          \b(?:test|example|dummy|placeholder)\b
    message: "⚠️ 发现硬编码密钥"
    languages: [python, javascript, typescript, go, java]
    severity: ERROR

  - id: dangerous-eval
    pattern: eval($X)
    message: "⚠️ eval() 使用危险，可能导致代码注入"
    languages: [python]
    severity: WARNING
```

```bash
# CI 中的执行命令
semgrep --config=./.semgrep/rules/ \
        --error \
        --metrics=off \
        --output=semgrep-report.sarif \
        src/
```

### 7.3 CodeQL 查询配置示例（GitHub Actions）

CodeQL 是 GitHub 的语义代码分析引擎，支持深度数据流分析。

```yaml
# .github/workflows/codeql.yml
name: "CodeQL Security Scan"
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # 每周一凌晨

jobs:
  analyze:
    name: CodeQL Analyze
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      actions: read
      contents: read

    strategy:
      fail-fast: false
      matrix:
        language: ['python', 'javascript', 'go']

    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: +security-and-quality  # 启用安全+质量查询包
      - uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{matrix.language}}"
```

### 7.4 Trivy + Snyk 安全扫描配置

```yaml
# .trivy.yml
severity: HIGH,CRITICAL
vulnerability:
  type:
    - os
    - library
ignore:
  - id: CVE-2023-XXXXX   # 已验证不影响当前使用场景
    reason: "不在代码路径中"
```

```bash
# CI pipeline 中的调用
trivy fs --severity HIGH,CRITICAL --exit-code 1 .
trivy image --severity HIGH,CRITICAL --exit-code 1 myapp:latest
trivy repo --severity HIGH,CRITICAL --exit-code 1 https://github.com/org/repo
```

### 7.5 Lizard 圈复杂度 CLI 配置

```bash
# 安装
pip install lizard

# 生成复杂度报告（支持多语言）
lizard src/ --languages python,javascript,java --html > complexity-report.html

# CI 门禁检查
lizard src/ --threshold_warnings 20 --threshold_cn 30
# 退出码: 0=通过, 1=警告, 2=有函数超过阈值
```

---

## 八、OWASP Top 10 代码审查安全清单（深度版）

> 以下每一项都可在 CR 中逐项对照检查，特别适合安全敏感项目。

### 8.1 A01: 失效的访问控制

| 检查项 | 审查要点 |
|:-------|:---------|
| 未授权访问 | 所有敏感接口是否有鉴权？未登录是否能访问管理后台？ |
| IDOR | URL 中的 ID 是否属于当前用户？`/api/order/123` 是否校验属于当前用户？ |
| 权限提升 | 普通用户能否通过模拟 Header/参数获得管理员权限？ |
| CORS 配置 | `Access-Control-Allow-Origin` 是否限制为白名单而非 `*`？ |

### 8.2 A02: 加密机制失效

| 检查项 | 审查要点 |
|:-------|:---------|
| 传输加密 | 敏感数据是否仅通过 HTTPS/TLS 传输？HTTP 页面是否重定向到 HTTPS？ |
| 存储加密 | 密码是否使用 bcrypt/argon2/scrypt 哈希？而非 MD5/SHA1？ |
| 证书验证 | HTTP 客户端是否验证了服务端证书？是否禁用了证书校验？ |

### 8.3 A03: 注入

| 检查项 | 审查要点 |
|:-------|:---------|
| SQL 注入 | 所有 SQL 是否使用参数化查询/ORM？有无任何字符串拼接？ |
| NoSQL 注入 | MongoDB 查询是否使用 `$regex` + 用户输入？ |
| 命令注入 | `subprocess.run(user_input, shell=True)` → 必须禁止 |
| LDAP 注入 | LDAP 查询过滤器是否转义了用户输入？ |
| SSTI | 模板中是否嵌入了用户输入？Jinja2 的 `{{ }}` 是否被滥用？ |

### 8.4 A04: 不安全的设计

| 检查项 | 审查要点 |
|:-------|:---------|
| 缺少限流 | 登录/注册/API 端点是否有速率限制？ |
| 滥用客户端控制 | 后端是否依赖前端传的"价格"/"角色"字段？ |
| 多步骤缺少状态 | 多步骤操作的每一步是否验证了上一步已完成？ |

### 8.5 A05: 安全配置错误

| 检查项 | 审查要点 |
|:-------|:---------|
| 调试模式 | 生产环境是否关闭了 DEBUG/错误堆栈？ |
| 默认凭据 | 是否有未修改的默认密码/密钥？ |
| 不必要的功能 | 是否开启了不必要的端点/端口/服务？ |
| 目录列表 | Web 服务器是否禁用了目录列表？ |

### 8.6 A06: 易受攻击和过时的组件

| 检查项 | 审查要点 |
|:-------|:---------|
| 依赖版本 | 检查 `package.json`/`requirements.txt` 中的版本是否最新 |
| 已知漏洞 | NPM Audit / pip-audit / Trivy 扫描结果是否有 CVE？ |
| 废弃功能 | 使用了已废弃的 API/框架版本？ |

### 8.7 A07: 身份验证与会话管理失效

| 检查项 | 审查要点 |
|:-------|:---------|
| 密码策略 | 是否有密码复杂度要求？是否检查了常见密码黑名单？ |
| 重放攻击 | 会话 Token 是否有过期机制？刷新 Token 是否轮换？ |
| Session 固定 | 登录成功后是否生成了新 Session ID？ |
| 多因素认证 | 敏感操作是否需要 MFA？ |

### 8.8 A08: 软件和数据完整性失效

| 检查项 | 审查要点 |
|:-------|:---------|
| CI/CD 篡改 | Pipeline 是否签名了构建产物？ |
| 反序列化 | `pickle`/`yaml.load` / Java `readObject` 是否存在？ |
| 第三方 CDN | 是否使用 SRI（子资源完整性）Hash 验证？ |

### 8.9 A09: 安全日志与监控不足

| 检查项 | 审查要点 |
|:-------|:---------|
| 审计日志 | 敏感操作是否有日志？是否有用户 ID/时间/IP？ |
| 告警 | 异常登录/大量 403 是否有告警？ |
| 日志脱敏 | 日志中是否隐藏了密码/ Token/身份证号？ |

### 8.10 A10: 服务端请求伪造（SSRF）

| 检查项 | 审查要点 |
|:-------|:---------|
| URL 白名单 | 请求外部 URL 时是否校验了域名白名单？ |
| 元数据服务 | 是否阻止了 `169.254.169.254`（云元数据）请求？ |
| 内网探测 | 用户可控 URL 是否能访问内网服务？ |

---

## 九、AI 代码审查集成实践

> 来源：import/doubao/打造跨语言AI代码审查官.md — 真实项目验证数据：PR 审查时间 ↓74%、严重 Bug 漏检率 ↓83%

### 9.1 AI CR Skill 的典型架构

```text
universal-code-reviewer/
+-- SKILL.md              # 核心指令文件（定义审查SOP）
+-- config.json            # 审查配置（语言/规则/阈值）
+-- scripts/
|   +-- python_review.py   # Python 审查脚本
|   +-- java_review.py     # Java 审查脚本
|   +-- go_review.py       # Go 审查脚本
|   +-- js_review.py       # JavaScript/TS 审查脚本
+-- rules/
    +-- security/          # 安全规则库
    +-- style_guides/      # 风格规则（PEP8/Google Style 等）
    +-- anti_patterns/     # 反模式检测
```

### 9.2 AI 审查的量化成果参考

| 指标 | 引入 AI CR 前 | 引入 AI CR 后 | 改善 |
|:-----|:------------:|:------------:|:----:|
| 平均 PR 审查时间 | 4.2 小时 | 1.1 小时 | ↓ 74% |
| 严重 Bug 漏检率 | 18% | 3% | ↓ 83% |
| 团队规范遵守率 | 65% | 92% | ↑ 42% |
| 新人上手速度 | 2 周 | 3 天 | ↑ 333% |

### 9.3 AI CR 分级策略

| 等级 | 谁执行 | 覆盖范围 | 耗时 | 适合场景 |
|:-----|:-------|:---------|:----:|:---------|
| **L1 - 自动初筛** | AI | 格式/命名/基础安全/代码规范 | < 30秒 | 所有 PR |
| **L2 - AI 深度审查** | AI | 逻辑缺陷/边界情况/性能问题/安全检查 | 1–3分钟 | 中等复杂度 PR |
| **L3 - 人工聚焦** | Senior Engineer | 架构合理性/业务逻辑/设计模式/AI 报告确认 | 10–30分钟 | 所有 PR（终审） |

### 9.4 定制团队专属审查规则

```yaml
# rules/style_guides/python_custom.yaml — 团队自定义规则
custom_rules:
  - id: no-print-in-prod
    pattern: "print("
    message: "使用 logging 模块替代 print()"
    severity: WARNING

  - id: no-bare-except
    pattern: |
      try:
        ...
      except:
        ...
    message: "禁止裸 except，必须指定异常类型"
    severity: ERROR

  - id: function-too-long
    pattern: "def "
    metric: lines
    threshold: 50
    message: "函数超过 50 行，建议拆分"
    severity: WARNING

  - id: import-order
    pattern: |
      import os
      ...
      import requests  # 标准库与第三方库未分隔
    message: "标准库、第三方库、本地库导入应用空行分隔"
    severity: STYLE
```

### 9.5 CI/CD 集成 AI CR

```yaml
# .github/workflows/ai-code-review.yml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run AI Code Review
        uses: ai-skills-hub/universal-code-reviewer@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          languages: python,javascript,go
          severity: ERROR,WARNING
          auto-comment: true        # 自动在 PR 添加 Review 评论
          auto-label: true          # 自动标注问题类型标签
          fail-on-severity: ERROR   # ERROR 级阻塞合并

      - name: Upload SARIF Report
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: review-report.sarif
```

---

## 十、高级审查提示词模式

### 10.1 思维链审查 Prompt

利用 Chain-of-Thought 引导 AI 逐步推理，减少遗漏。

```text
你正在执行一次结构化代码审查。请按以下步骤完成：

## 步骤 1: 理解变更背景
- 分析这个 PR 的变更范围和意图
- 列出所有修改的文件和主要变更类型

## 步骤 2: 代码逻辑验证
- 逐段分析修改后的代码逻辑
- 识别是否有潜在的回归路径
- 检查是否有未处理的 else/默认分支

## 步骤 3: 安全影响分析
- 检查是否有用户输入的变更路径
- 识别数据流的可信边界
- 标记所有安全敏感操作

## 步骤 4: 性能影响评估
- 分析新增循环、SQL 查询、网络 IO
- 估算变更对响应时间的影响

## 步骤 5: 整合审查结论
- 汇总所有发现的问题
- 按严重程度排序 (Critical/Major/Minor/Suggestion)
- 对每个问题给出修复建议

代码 Diff:
[粘贴代码 diff]
```

### 10.2 多视角审查 Prompt（模拟不同角色）

通过切换视角发现不同类型的问题。

```text
请以以下 3 个不同角色的视角分别审查这段代码，输出各自的审查结论：

## 视角 1: 安全工程师
- 关注: 注入/CORS/认证/鉴权/密钥/数据泄露
- 评分标准: 按 OWASP Top 10

## 视角 2: 性能架构师
- 关注: 时间复杂度/N+1/内存/缓存/并发
- 评分标准: 响应时间估算 + 容量评估

## 视角 3: 业务 Owner
- 关注: 逻辑正确性/边界条件/兼容性/幂等性
- 评分标准: 功能完备度 + 异常处理覆盖率

## 最终综合
- 合并三个视角的发现
- 标记每个问题的最高优先级
- 输出 Critical 问题的合并方案

代码:
[粘贴代码]
```

### 10.3 假名代码审查 Prompt（消除偏见）

```text
请匿名审查以下代码，不要关注代码风格/命名（这些已通过 Linter 检查）：
- 只关注逻辑正确性、安全漏洞和性能问题
- 对每个发现的问题，给出该问题的具体触发条件
- 说明该问题在什么输入/场景下才会暴露
- 评估该问题的实际危害程度（需要满足哪些条件才会被利用）

代码（已做变量脱敏）：
[脱敏后的代码]
```

### 10.4 AI 生成代码专用审查 Prompt

```text
你正在审查一段 AI 生成的代码。请特别关注 AI 代码的常见陷阱：

1. 🔴 幻觉检测
   - 是否存在不存在的 API/库/模块名？
   - 函数签名是否与官方文档一致？
   - 是否有虚构的配置参数/环境变量？

2. 🔴 上下文一致性
   - 代码风格是否与项目已有代码一致？
   - 命名约定是否遵循项目规范？
   - 是否有重复实现已有功能？

3. 🟡 边界完整性
   - 是否处理了 null/None/空数组的输入？
   - 是否有异常处理和 fallback 逻辑？
   - 日志输出是否足够？

4. 🟡 测试覆盖
   - AI 是否生成了对应的单元测试？
   - 测试是否覆盖了边界情况？
   - 测试本身是否正确（不测试错误行为）？

5. 🔶 过度工程
   - 是否引入不必要的抽象/设计模式？
   - 复杂度是否与问题匹配？

对每个发现：
- 标注问题类型 (幻觉/上下文/边界/测试/过度)
- 代码行号
- 修复建议
- 置信度评分 (1-10)

代码:
[粘贴 AI 生成代码]
```

### 10.5 增量审查 Prompt（大型 PR）

```text
这是一个大 PR（超过 300 行变更）。请采用增量审查策略：

## 优先级排序
自动识别以下层次的问题，各层独立输出：

### 第一层 (阻塞级) — 必须修复
- 安全漏洞
- 逻辑错误（导致功能异常）
- 数据一致性/完整性破坏

### 第二层 (重要级) — 建议修复
- 性能隐患
- 可维护性问题
- 明显违反项目架构约定

### 第三层 (改进级) — 备注
- 可读性改善
- 测试补充建议
- 后续优化方向

## 输出要求
- 阻塞级问题：必须包含修复代码示例
- 重要级问题：必须包含修复方向说明
- 改进级问题：只列建议，无需代码示例

PR Diff:
[粘贴代码 diff]
```

---

## 十一、多语言审查要点速查表

### 11.1 Python

| 检查维度 | 典型问题 | 检测方式 |
|:---------|:---------|:---------|
| 类型安全 | 缺少类型注解、隐式类型转换 | mypy + --strict |
| 并发 | GIL 陷阱、asyncio 中阻塞调用 | 人工审查 |
| 异常 | 裸 `except:`、`except Exception` 太宽泛 | ruff/bandit |
| 性能 | 循环中 `for i in range(len(list))`、不必要的 `list()` | ruff/perflint |
| 安全 | `eval()`/`exec()`/`pickle.loads()`/`yaml.load()` | bandit/semgrep |
| 内存 | `__del__` 陷阱、循环引用 | gc 模块 + 人工 |
| 导入 | 循环导入、`from x import *` | ruff/isort |

### 11.2 Java

| 检查维度 | 典型问题 | 检测方式 |
|:---------|:---------|:---------|
| 资源管理 | 未使用 try-with-resources、连接未关闭 | SpotBugs/PMD |
| 空安全 | `NullPointerException`、`Optional` 滥用 | SpotBugs/人工 |
| 并发 | 未使用 `ConcurrentHashMap`、`synchronized` 误用 | FindBugs/人工 |
| 性能 | 循环中 `String +` 拼接、`Stream` 滥用 | SonarQube |
| 继承 | `@Override` 缺失、继承层级过深 | Checkstyle/PMD |
| 序列化 | `Serializable` 未定义 `serialVersionUID` | SpotBugs |
| 测试 | Mockito 误用、测试不够隔离 | 人工审查 |

### 11.3 Go

| 检查维度 | 典型问题 | 检测方式 |
|:---------|:---------|:---------|
| 错误处理 | 错误被忽略 (`_`)、错误信息不包含上下文 | revive/golangci-lint |
| 并发 | goroutine 泄漏、`sync.WaitGroup` 未完成 | go vet -race/人工 |
| 接口 | 接口太大、接口定义位置不当（消费者侧 vs 实现侧） | 人工 |
| 内存 | `append` 陷阱、slice 共享底层 array | 人工 |
| 性能 | `defer` 在循环中、不必要的 `fmt.Sprintf` | golangci-lint |
| 资源 | `http.Response.Body` 未 Close | go vet |
| 测试 | 表驱动测试未写全、t.Helper() 缺少 | 人工 |

### 11.4 JavaScript / TypeScript

| 检查维度 | 典型问题 | 检测方式 |
|:---------|:---------|:---------|
| 类型安全 | `any` 滥用、类型断言过多 | TypeScript strict 模式 |
| 异步 | Promise 未被 catch、async 中缺少 await | ESLint/no-floating-promises |
| 安全 | `innerHTML`、`eval()`、原型污染 | ESLint 安全插件/Semgrep |
| 性能 | 不必要的 `useEffect` 依赖、重渲染 | React DevTools/人工 |
| 模块 | 循环依赖、`import *` 过多 | import/no-cycle |
| 兼容性 | 浏览器兼容性、polyfill 缺失 | browserslist + 人工 |
| 包体积 | lodash 全量导入、moment.js | bundle-analyzer |

### 11.5 Rust

| 检查维度 | 典型问题 | 检测方式 |
|:---------|:---------|:---------|
| 借用检查 | `unsafe` 滥用、裸指针使用不当 | clippy + 额外注意 |
| 生命周期 | 生命周期标注错误、`'static` 误用 | rustc 检查 + 人工 |
| 错误处理 | `unwrap()` 过多、`expect()` 信息不足 | clippy |
| 并发 | `Arc<Mutex<T>>` 粒度不合理 | 人工 |
| 性能 | `clone()` 过多、不必要的 Box | clippy/perf lints |
| 测试 | 测试隔离性不足、benchmark 缺失 | cargo test/bench |

---

## 十二、基于 AST + 知识图谱的深度代码分析

> 来源：GitNexus（纯本地代码情报引擎）的设计理念

传统 RAG 做代码理解的问题：向量检索"模糊匹配"无法精准追踪调用链、继承关系和依赖路径。"这段代码影响谁？"只能用 Graph RAG 回答。

### 12.1 分析框架对比

| 维度 | 传统文本 RAG | AST + Graph RAG |
|:-----|:------------|:----------------|
| 分析粒度 | 文本块级（模糊） | 节点+关系级（精确） |
| 调用链追踪 | 无法精准定位 | 可沿边遍历 N 层 |
| 影响范围分析 | 依赖关键词匹配 | 精确计算修改爆炸半径 |
| 跨文件关系 | 弱（文本相似度） | 强（有向图边） |
| 循环依赖检测 | 不支持 | AST 图可达性分析 |
| 死代码识别 | 不支持 | 零入度节点检测 |
| 代码幻觉 | 高（向量相似≠语义正确） | 低（图遍历保证正确） |

### 12.2 在 Code Review 中的应用场景

| 场景 | Graph 分析 | 审查价值 |
|:-----|:-----------|:---------|
| **修改影响范围** | 从修改的函数出发，沿调用链遍历 | 准确告知 Reviewer 需要回归的范围 |
| **循环依赖检测** | 模块间有向图的强连通分量分析 | 提前阻止架构腐化 |
| **死代码识别** | 标注零入度/零引用的函数和文件 | 清理技术债 |
| **架构合规** | 检查新增导入是否违反分层规则 | 架构守护自动化 |
| **变更一致性** | 同接口的所有实现是否都修改了 | 防止遗漏改动 |

### 12.3 推荐工具

| 工具 | 类型 | 适用场景 | 安装方式 |
|:-----|:-----|:---------|:---------|
| **GitNexus** | AST + Graph RAG | 纯本地代码理解/审计/重构安全评估 | Cli/Web/MCP |
| **Sourcegraph** | 代码搜索 + 依赖图 | 企业级代码库浏览与影响分析 | 云端/自托管 |
| **dep-tree** | 依赖树分析 | 循环依赖检测/死代码识别 | npm i -g dep-tree |
| **pyright/pylance** | 类型推导 + AST | Python 代码错改检测 | pip install pyright |
| **Structured101** | 架构依赖图 | Java 项目架构腐化检测 | IDE 插件 |

---

## 十三、代码审查反模式

> 好的 CR 流程需要避免的常见错误做法

### 13.1 流程反模式

| # | 反模式 | 表现 | 后果 | 纠正方法 |
|:-:|:-------|:-----|:-----|:---------|
| 1 | **橡皮图章** | Reviewer 只看不评论，直接 Approved | 代码质量失控 | 设置最小评论数/KLOC 要求 |
| 2 | **马拉松 Review** | PR 超过 400 行 Review 效率暴跌 | 漏检率升高 | 设置 PR 大小上限(250行) |
| 3 | **单点瓶颈** | 只有一个人能 Approve 某个模块 | 阻塞团队 | 培养 Backup Reviewer |
| 4 | **异步过夜** | PR 提交后等待 24h+ 才有反馈 | 上下文切换成本高 | SLA: 4h 内首次回复 |
| 5 | **事后 CR** | 代码已合并才"补"Review 评论 | 失去拦截时机 | 合并前强制 CR 通过 |
| 6 | **完美主义** | Reviewer 苛求完美，不接受渐进改进 | 开发节奏被打断 | 区分 "必须改" vs "建议改" |
| 7 | **审查疲劳** | 单次 Review 超过 60 分钟 | 注意力下降，漏检增多 | 单次 Review ≤ 1h |

### 13.2 沟通反模式

| # | 反模式 | 表现 | 纠正方法 |
|:-:|:-------|:-----|:---------|
| 1 | **人身攻击** | "这段代码写得真烂"→ 指向人而非代码 | "这段逻辑有 NPE 风险"→ 指向代码 |
| 2 | **知识藏私** | "这个问题你自己应该知道" | 明确分享知识，建立团队规范文档 |
| 3 | **指手画脚** | "如果是我，我会用 XX 模式"（风格偏好非逻辑问题） | 区分"阻塞问题"与"个人偏好" |
| 4 | **沉默拒绝** | 不评论不拒绝，挂着一周 | 设置超时自动升级机制 |
| 5 | **争论不休** | 评论区变成设计讨论会 | 重大问题线下会议，评论只做结论记录 |

### 13.3 质量评估反模式

| # | 反模式 | 表现 | 纠正方法 |
|:-:|:-------|:-----|:---------|
| 1 | **唯覆盖率论** | 只盯着覆盖率数字，用 mock 刷覆盖率 | 关注测试质量：是否验证了真实行为 |
| 2 | **唯行数论** | "我审了 500 行所以我很认真" | 关注问题质量而非评论行数 |
| 3 | **唯工具论** | "SonarQube 没报警所以没问题" | 静态分析有盲区，必须人工补位 |
| 4 | **新人放水** | "新人的代码，差不多就行" | 统一标准，新人更需要严格审查（学习机会） |
| 5 | **老将免审** | "他写了 10 年代码，不用审" | 人人需 Review，老将更易有盲区 |

---

## 十四、审查质量自动化保障体系

### 14.1 多层次自动化门禁架构

```text
+-----------------------------------------------------+
|               PR 提交流程                             |
+-----------------------------------------------------+
|                                                      |
|  Pre-commit Hooks                                    |
|  +-- 格式化检查 (prettier/black/gofmt)               |
|  +-- Lint 检查 (ruff/eslint/pylint)                 |
|  +-- Secret 扫描 (gitleaks/trufflehog)               |
|                                                      |
|  CI Pipeline                                         |
|  +-- 单元测试 + 覆盖率 ≥ 80%                        |
|  +-- 集成测试                                        |
|  +-- SAST (Semgrep/CodeQL) - Critical 阻塞          |
|  +-- SCA (Trivy/Snyk/Dependabot)                    |
|  +-- 复杂度分析 (lizard) - 函数 >20 警告             |
|  +-- 重复代码检测 (jscpd) - 重复 >3% 阻塞           |
|                                                      |
|  AI Code Review                                      |
|  +-- 自动评论到 PR                                   |
|  +-- 标记严重级别                                    |
|  +-- 生成审查报告                                    |
|                                                      |
|  人工 Review (聚焦 20% 高价值判断)                   |
|  +-- 架构合理性                                      |
|  +-- 业务逻辑正确性                                  |
|  +-- AI 报告确认                                     |
|  +-- 安全关键路径签字                                |
|                                                      |
|  Quality Gate (合并前检查)                            |
|  +-- 所有门禁通过                                    |
|  +-- 至少 1 位 Reviewer Approved                     |
|  +-- 无未解决的 Critical 评论                        |
|                                                      |
|  ✅ 自动合并 / 🚫 自动关闭 + 通知                    |
+-----------------------------------------------------+
```

### 14.2 门禁配置模板（YAML）

```yaml
# .review-gate.yml
# 代码审查质量门禁配置

gate:
  pre_commit:
    formatting: true          # 格式化检查
    lint: true                # Lint 检查
    secrets: true             # Secret 扫描

  ci:
    coverage:
      min: 80                 # 新增代码覆盖率门限
      blocking: true
    static_analysis:
      min_quality_gate: passed # SonarQube QG
      blocking: true
    security:
      critical_zero: true     # Critical 漏洞 = 0
      high_zero: true         # High 漏洞 = 0
      blocking: true
    complexity:
      function_max: 20        # 圈复杂度函数级上限
      file_max: 60            # 圈复杂度文件级上限
      blocking: false         # 仅警告
    duplicates:
      max_percent: 3          # 重复率上限
      blocking: true

  review:
    required_approvers: 1     # 最少 Approve 人数
    required_lgtm: true       # 需要明确 LGTM
    auto_merge: true          # 通过后自动合并
    merge_sla_hours: 48       # 超过 48h 未合并自动升级

  blocking_severities:
    - CRITICAL
    - HIGH

  auto_label:
    security_review: true
    performance_review: true
    architecture_review: true
```

### 14.3 超时自动升级机制

```text
PR 提交
  |
  +-- [0–4h]  首次回复 SLA
  |     +-- 超时 -> 自动 @ 指定 Reviewer + 通知技术负责人
  |
  +-- [4–24h] Review 中
  |     +-- 超时 -> 自动 @ Backup Reviewer
  |
  +-- [24–48h] 第二次 Reviewer 提醒
  |     +-- 超时 -> 自动升级到技术总监
  |
  +-- [> 48h]  强制关闭或绕过审批
        +-- 超时 -> 记录到 Review SLA 违规统计
```

---

## 十五、代码坏味道（Code Smell）速查与修复指引

> 坏味道不是 Bug，但往往是 Bug 的前兆。能在 CR 阶段识别坏味道，是 Senior 与 Junior 的分水岭。

### 15.1 命名相关坏味道

| 坏味道 | 症状 | 修复指引 |
|:-------|:-----|:---------|
| 太短的名字 | `x`, `tmp`, `data`, `val` | 用有业务含义的名字，即使长一点 |
| 太长/冗余的名字 | `UserServiceInMemoryImpl` | 控制在 3–4 个词内 |
| 类型名字嵌入 | `strName`, `intCount` | 用类型注解（type hints）代替 |
| 不一致的缩写 | `idx` vs `index`, `conf` vs `config` | 统一缩写词表 |
| 误导性名字 | `isActive()` 实际会修改状态 | 命名必须真实反映行为 |
| 双关语 | `add()`有时"添加"有时"求和" | 不同语义用不同动词 |

### 15.2 函数相关坏味道

| 坏味道 | 症状 | 修复指引 |
|:-------|:-----|:---------|
| 过长函数 | 超过 50 行，有多个缩进层级 | 按职责拆分：提取方法 |
| 过多参数 | 超过 5 个参数 | 用 Parameter Object 封装 |
| 布尔参数 | `processUser(..., isAdmin, isActive)` | 拆分为两个独立方法 |
| 输出参数 | 函数修改传入的可变对象 | 返回新对象，而非修改输入 |
| 标志参数 | `getData(cached=false)` | 两个方法：`getCached()` / `getFresh()` |
| 上帝函数 | 一个函数做 3+ 件不同的事 | 遵循单一职责拆解 |

### 15.3 类相关坏味道

| 坏味道 | 症状 | 修复指引 |
|:-------|:-----|:---------|
| 上帝类 | 一个类 1000+ 行 | 按职责拆分为多个类 |
| 数据类 | 只有 getter/setter，无行为 | 将相关操作移入类中 |
| 拒绝继承 | 子类不需要父类的接口/方法 | 用组合替代继承 |
| 过度耦合 | 一个类依赖 10+ 其他类 | 引入 Facade/Interface 解耦 |
| 笨重的初始化 | 构造函数需要 8+ 参数 | 用 Builder 模式 |

### 15.4 架构坏味道

| 坏味道 | 症状 | 修复指引 |
|:-------|:-----|:---------|
| 循环依赖 | A→B→C→A | 提取共同依赖到新模块 |
| 依赖泛滥 | 一个 util 类被 50+ 模块引用 | 提炼为独立服务 |
| 层渗透 | UI 层直接访问 DAO 层 | 保证严格分层调用 |
| 蔓延的上帝包 | 一个包里有 30+ 不相关的类 | 按功能域拆分包 |
| 复制粘贴继承 | 5 个类有几乎相同的代码 | 模板方法模式 |

---

## 交叉引用

- [CR 检查清单](2026-06-29-codereview-checklist.md) — 具体的检查项（"查什么"）
- [CR 基础理念](2026-06-29-codereview-overview.md) — 左移范式、人机分工、常见误区
- [AI CR 三大路径](2026-06-29-ai-codereview-landscape.md) — AI 辅助 CR 的选型决策
- [CodeReview Agent 工具链](2026-06-29-codereview-agent-tools.md) — Agent 工具详情
- AI 时代的软件质量观 — import 质量观 PPT 归档

---

## 参考文件

> 本文件调用的外部文件与资料（不含被引用情况）。

### 内部知识库引用

- [CR 检查清单](2026-06-29-codereview-checklist.md) — 关联
- [CR 基础理念](2026-06-29-codereview-overview.md) — 关联
- [AI CR 三大路径](2026-06-29-ai-codereview-landscape.md) — 关联
- [CodeReview Agent 工具链](2026-06-29-codereview-agent-tools.md) — 关联
- AI 时代的软件质量观 — 关联

### 外部资料引用

- (无)

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----|:-----|
| 2026-07-24 | v1.0 | 初始版本 |
