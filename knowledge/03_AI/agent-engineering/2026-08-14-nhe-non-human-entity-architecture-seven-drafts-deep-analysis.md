# NHE 非人类实体架构七件套深度分析（08-13 齐发）

> **文档类型**：深度分析 | **主题**：IETF NHE（Non-Human Entity）参考模型与协议族 | **日期**：2026-08-14
> **范围**：`draft-ruvalcaba-nhe-{arch,identity,mesh,memory,audit,bootstrap,authz}-00`（2026-08-13 17:11-17:17 同批齐发）
> **适用读者**：Agent 基础设施架构师 / AI 安全决策者 / 身份与信任体系设计者

---

## 0. 一句话结论

**Agent 互联正在从"每个团队重复发明同一套接口"走向"IETF 级可互操作架构族"**：NHE 参考模型把持久自主 Agent 分解为**七个按接口划分的组件**，用**身份（可验证密钥承诺）+ 记忆（可验证记录）+ 审计（防篡改链）+ 引导（自描述能力约束）+ 授权（意图绑定凭证）**五条密码学主线，把"Agent 是谁、知道什么、做了什么、被允许做什么"全部变成**可验证而非可信任**的工程对象——但七份草案全部是 -00 骨架（数据模型已定、线上编码全部延后到 -01），且**尚无任何实现**，属"架构宣言"阶段。

## 1. 摘要（5 条核心结论）

1. **规模澄清（诚实边界）**：08-13 17:11-17:17 同批齐发的是 **7 份草案**——`arch`（参考模型总纲）+ 6 份协议（identity/mesh/memory/audit/bootstrap/authz）。用户口径"六件套"（身份/网格/记忆/审计/引导 + 参考模型）覆盖其中 6 份；**授权（authz）是第 7 份**，同样同日齐发。本分析以 7 份全量呈现。
2. **架构核心是三不变量**：Operator control（可挂起/终止）、Inspectability（状态可验证暴露）、Bounded authority（显式可撤销授权）——把 NHE 定义为**功能工件**而非道德/法律实体，是整套架构的工程合法性根基。
3. **五条密码学主线统一**：身份链、记忆图、审计链三条 **hash-chain 结构** + 统一 CANON 确定性序列化 + 注册表驱动的密码敏捷性——不是七份孤立草案，是同一设计语言的七次落地。
4. **两个最锋利的机制**：① audit 的 **prove-without-exposing**（证明"用了正确模型、推理了预期量级、导致此行动"而不泄露推理文本）；② authz 的 **digest linkage**（人类批准所见 = 凭证授权所及，关闭 confused-deputy 缺口）。
5. **对 Agent 基础设施的即时意义**：NHE 族的三个机制直接回应了业界已实证的攻击面——**memory 的 independence guard 反 Salami 共谋投毒、audit 链反 StepJack 多步注入、authz 的意图绑定凭证反越权**；但全部是 -00 骨架、无实现、单人作者，落地需跟踪 -01 及实现验证。

## 2. 背景与定位：为什么需要 NHE 参考模型

### 2.1 问题：Agent 在重复发明同一批接口

```
LLM-driven agents evolved from stateless calls to long-lived processes,
and every team independently reinvents the same handful of interfaces:
  - how an agent proves who it is            (identity)
  - how it moves accumulated context to another host (continuity)
  - how two agents exchange work             (mesh)
  - how its reasoning is made verifiable     (audit)
  - how its authority is bounded and revoked (governance)
```

架构文档开篇的观察：这类系统**正在被反复独立构建**，每次都在重造同一小撮接口。NHE 参考模型的价值 = **给这些接口一个公共词汇表和信任关系图**，并明确哪些接口值得独立标准化。

### 2.2 NHE 定义（严格功能化）

- **NHE = 功能工件**：有界进程，定义输入/输出/持久状态，运行在 operator 控制的主机上。
- **明确排除**：alive/sentient/conscious/道德或法律人——"不可工程规格化，超范围，MUST NOT 从任何机制推断"。
- **三个运行定义**：身份 = 可验证密钥承诺；连续性 = hash 提交状态的转移；自主性 = 在显式有界授权内行动。

### 2.3 三不变量（每份伴随协议都必须保持）

| 不变量 | 含义 | 在协议层的实现 |
|:--|:--|:--|
| **Operator control** | 可随时挂起/终止 | identity §9 撤销（链事件/注册表）；authz absent-positive→denied |
| **Inspectability** | 状态/推理/行动可验证暴露 | audit 全链 + prove-without-exposing |
| **Bounded authority** | 只在显式可撤销授权内行动 | bootstrap 能力信封 + authz 意图凭证 |

## 3. 七件套全景

| # | 草案 | 页数 | 主题 | 状态 |
|:--|:--|:--|:--|:--|
| 0 | `draft-ruvalcaba-nhe-arch-00` | 10 | 参考模型总纲（七组件 + 信任模型） | Informational，参考模型 |
| 1 | `draft-ruvalcaba-nhe-identity-00` | 8 | 身份链：可验证密钥承诺 + genesis 证明 | 标准候选 |
| 2 | `draft-ruvalcaba-nhe-mesh-00` | 6 | 网格：实体间消息 + 任务分发（at-most-once） | 标准候选 |
| 3 | `draft-ruvalcaba-nhe-memory-00` | 9 | 记忆：可验证记录 + 信誉加权合并 | 标准候选 |
| 4 | `draft-ruvalcaba-nhe-audit-00` | 8 | 审计：防篡改推理/行动链 + prove-without-exposing | 标准候选 |
| 5 | `draft-ruvalcaba-nhe-bootstrap-00` | 7 | 引导：自描述能力清单 + 约束信封 | 标准候选 |
| 6 | `draft-ruvalcaba-nhe-authz-00` | 7 | 授权：分级自主 + 意图绑定凭证 | 标准候选 |

- **作者**：E. Ruvalcaba（全部）；**版本**：-00 初稿；**过期**：2027-02-14；**关系**：工作组 group/1027（BMWG 之外的个人草案池）。
- **配套**：`draft-ruvalcaba-hctp`（Hash-Chain Context Transfer Protocol）——连续性接口的首个伴随文档，状态 Draft（比本次六份更早、更成熟）。
- **依赖顺序**（arch §6）：Identity 与 Continuity 先行（一切以身份为锚），然后 Mesh、Audit、Memory、Governance。

## 4. 参考模型（arch）：七组件与信任模型

### 4.1 七组件分解（按接口而非按实现）

```
                    +------------------------------------------------+
                    |                    N H E                        |
                    |                                                |
                    |  +-------------+  +--------------+  +--------+  |
                    |  | Identity    |  | Continuity   |  | Memory |  |
                    |  | (who it is) |  | (state xfer) |  | (knows)|  |
                    |  +------+------+  +------+-------+  +---+----+  |
                    |         |                |               |      |
                    |  +------+----------------+---------------+---+  |
                    |  |        Reasoning & Audit (verifiable)   |   |  |
                    |  +------+------------------------------+---+   |  |
                    |         |                              |       |  |
                    |  +------+-------+              +-------+-----+  |
                    |  | Governance & |              |Observability|  |
                    |  | Authority    |              | & Control   |  |
                    |  +------+-------+              +-------+-----+  |
                    +---------|------------------------------|--------+
                              | (mesh)                       | (operator)
                         +----v------+                  +----v-----+
                         | Peer NHE  |                  | Operator |
                         +-----------+                  +----------+
```

| 组件 | 职责 | 互操作面（标准候选） | 对应草案 |
|:--|:--|:--|:--|
| Identity | 锚定"是谁"（密钥承诺 + genesis 血统） | 身份展示/证明格式 | identity |
| Continuity | 状态转移可验证（不重传全历史） | 上下文转移协议 | **HCTP**（已存在） |
| Memory | 持久可搜索知识（完整性 + 合并） | 可验证记忆链 + delta-merge | memory |
| Mesh | 实体间消息与任务分发 | 消息信封 + 任务状态机 | mesh |
| Reasoning & Audit | 防篡改推理/行动记录 | 可验证审计日志格式 | audit |
| Governance & Authority | 授权授予/限定/撤销 | 约束引导 + 后通道授权 | bootstrap, authz |
| Observability & Control | operator 监控/挂起/终止 | 大部分复用 SIEM 等；行为证明为低优先级候选 | — |

### 4.2 信任模型（四句话）

1. **NHE 信任 operator** 来限定授权、挂起/终止——operator 是控制根，不是 NHE。
2. **依赖方不信任 NHE 的自我断言**——身份经 Identity 接口、状态经 Continuity、推理经 Audit 验证。
3. **Peer NHE 默认互不信任**——交换工作前必须经 Identity 接口互相认证。
4. **无组件依赖不可观测性**——机密性由传输/加密层提供，不靠机制隐蔽。

## 5. 六协议原理详解

### 5.1 Identity：身份 = 可验证密钥承诺（而非名字）

**数据模型**（record 五元组）：

```
record = {
  identity_key_hash : digest of the identity public key
  profile_hash      : digest of the configuration profile
  prior_record_hash : link to the immediate predecessor
  timestamp         : RFC 3339, sub-second precision
  signature         : identity-key signature over the above
}
[ genesis ]        [ record 1 ]        [ record 2 ]
prior = 0x00*32 <- prior = H(genesis) <- prior = H(record 1)
sig(key)            sig(key)             sig(key)
```

**关键原理**：
- **配置血统绑定单一身份**：配置变更 = 追加新 record（profile_hash 变、key 连续）→ 一个 NHE 的配置演进史是一整条可验证链。**No-fork 属性**：每个 (key_hash, prior_hash) 至多一个记录，杜绝双链歧义。
- **Proof of Control**：展示链 ≠ 控制密钥。挑战 = fresh nonce + freshness counter，实体用身份密钥签名（挑战 + 当前 record 的 prior_record_hash）→ 绑定活体证明到具体身份 + 防重放。
- **Capability Attestation（可选）**：证明"profile 含能力 X"而不泄露整个配置——零知识风格的最小披露。
- **硬件根植 profile（可选）**：设备根密钥 + 制造商证书链 + 内容寻址注册表；机密密钥从高熵设备根秘密派生，公开值（genesis hash/serial）仅作非秘密域分离输入。
- **密码敏捷性**：建议混合签名（Ed25519 + ML-DSA）——身份在任一原语被攻破时存活；链链接哈希 SHA3-256；签名套件/哈希由注册表控制（迁移不需新协议版本）。
- **撤销**："连续身份**永远不对 operator 连续**"——撤销以链事件（terminal record）或注册表状态表达，依赖方 MUST 视已撤销身份无效。

### 5.2 Mesh：无中央协调者的实体互联

```
Messaging:  HEARTBEAT (presence, monotonic seq) + SEND (addressed) + inbox
Task:       CREATE -> CLAIM (atomic, at-most-one) -> COMPLETE
            [OPEN] --CLAIM--> [CLAIMED] --COMPLETE--> [COMPLETED]
               ^                  |
               |   deadline exp   |  (failed claimant 不搁浅任务)
               +------------------+
```

- **at-most-once assignment 是核心保证**：并发 CLAIM 必须恰好一个成功、其余观察到已认领。**exactly-once 不保证**——跨认领者失败场景需任务描述符幂等。
- 消息认证 MUST 绑定信封到发送者身份；收方 MUST 拒绝认证不符的消息。
- 架构定位：**套件中继 Continuity 之后最强的全新协议机会**——两侧天然独立实现/独立运营。

### 5.3 Memory：可验证记忆 + 信誉加权合并（最"社会学"的一份）

**Part I 可验证记录**（局部校验、篡改定位）：

```
record = {
  record_id          : write-once, version-specific
  content            : payload
  content_hash       : HASH(CANON(content))
  relational_pairs[] : write-once, per referenced prior R: {R.record_id, R.content_hash}
  back_references[]  : append-only, NOT covered by content_hash
}
```

- **Version-specific references（关键细节）**：引用按写时的 record_id 冻结，绝不按"该主题最新记录"解析——否则新记录写入会让旧引用内容漂移，**在未篡改数据上产生误报篡改**。
- **篡改定位而非仅检测**：content 校验失败 = 篡改节点本身；content 通过但 relational 失败 = 该节点完好、只是**观察到上游篡改**——故障定位到被引用的 record_id，靠邻居 append-only back_references 佐证。
- 原子性：content+hash+pairs 单原子写；跨分片 back-reference 补丁幂等重试安全。

**Part II 信誉加权合并**（防自我背书、防知识通胀）：

- **Delta**：absence 表达为 **confidence reduction**，永不硬删——一项知识不被单个贡献者的局部视图静默摧毁。
- **信誉界定的有效置信度**：`effective = base_confidence × contributor_reputation`（可选再乘血统深度折扣）——条目以贡献者信誉而非自断值进入共享存储。语义等价提案按嵌入相似度聚类合并（corroborated 而非重复）。**信誉函数是 pluggable policy**（如 EMA over 接受/人工确认/矛盾率），标准化的是 delta 格式与 bounded-merge 规则而非单一公式。
- **血统与隔离**：每条合并项归因绑定贡献者 NHE 身份；**lineage quarantine**——被破坏/失信贡献者及其衍生血统的条目整体隔离（子树操作，不丢弃其余存储）。
- **Independence Guard（反共谋核心）**：若两贡献者互为最近祖先（配置血统距离内），其相互确认**不计入 corroboration**——防止被破坏的贡献者通过衍生子贡献者自我背书制造"独立"佐证。
- **与既有机制的边界**：区别于 CRDT（确定性合并、无质量/信任/血统加权）、版本控制 diff（无置信度/信誉语义）、联邦学习聚合（加权模型参数而非离散知识项）。

### 5.4 Audit：防篡改推理/行动审计链

**Entry 绑定 14 字段入 hash**（关键：把**出处与规模**绑进哈希）：

```
entry = { entry_index, request_id, timestamp(ns), subject_id,
          provider, model, content_hash, token_count, byte_count,
          tokenizer_id, capture_mode, content_mode, prev_hash }
entry_hash = HASH(CANON(entry))
[ genesis: prev = H(subject_id) ] -> [ entry1: prev = eh(0) ] -> ...
```

- **为什么绑定 provider/model/token_count/byte_count**：只哈希不透明内容摘要的话，攻击者可篡改"哪个模型推理的""推理了多少"而不破坏链。byte_count 恒存在（确定性规模证明）；token_count 仅在可复现时存在。
- **CANON**：8-octet 大端长度前缀；absent 用 `0xFFFFFFFFFFFFFFFF` sentinel（null ≠ empty）；长度前缀消除 `("ab","c")` vs `("a","bc")` 的拼接歧义。
- **Genesis 锚定主体身份**：`prev = HASH(CANON(subject_id))`——审计链**不可移植到其他主体**。
- **Content-optional（数据最小化友好）**：content_mode = full/hash-only/none；链只绑 content_hash + 元数据，**内容可删/脱敏而不破坏链**——满足擦除义务的同时保留可验证审计。内容存储建议 AES-256-GCM 且绑定 entry hash 为 AAD（密文不可跨条目移植）+ nonce 唯一性纪律（生日界密钥轮换）。
- **Prove-without-exposing（本套件最锋利机制）**：proof-access 与 content-access **双作用域独立强制**——审计员可确认"用了正确模型、推理了预期量级、导致此行动"，而推理文本保持机密。授予 proof 权限 MUST NOT 隐含 content 权限。
- **Cross-layer capture**：reasoning 条目在模型边界产生（归一化异构 provider 格式），action 条目在执行边界产生——单链统一，可关联"推理→其导致的行动"。本地 identity 锚定副本使远端追加失败在后续对账时可检测。
- **Complexity-Divergence Signal（可选）**：窗口内推理复杂度（token/byte）vs 行动复杂度（参数数/规模/敏感性函数）的标准化残差超阈值即报警——"重大行动、极少推理"是值得浮出的信号（对链的分析，非链的属性）。

### 5.5 Bootstrap：自描述能力清单 → 约束信封

- **Capability Manifest**（自动 introspection 生成）：稳定实体标识 + 计算资源枚举 + 行动类别枚举（含影响物理世界的）+ 本地推理能力（实测吞吐）+ 网络特征；RFC 8785 JCS 签名（签名与签名方法字段排除在签名内容外）。
- **Tier → Permission Matrix**：协调者按量化阈值把清单分类到能力层，每层映射任务类型授权矩阵。**"分类就是自描述变成有界权威的瞬间"**。
- **6 步握手**：introspect → 互认证传输注册 → 协调者 **HKDF 派生 per-entity key**（从 identity-bound identifier 派生 → **免 PKI 的证书无关身份**，TOFU 根）→ 重签名清单 → 独立重派生验证 → 注册。
- **能力断言与身份加密打结**：密钥派生自同一 identity-bound identifier → **清单不可能"一个身份声明、另一身份签名"**。
- **Dispatch Gating**：每次任务分派三查（任务类型 ∈ 权限矩阵 / 能力 ∈ manifest / 目标活跃）；**Capability Assurance**：TOFU 测试任务抽查（对照 oracle），自报建立 envelope、抽查保持诚实——降级/隔离虚假能力声明。

### 5.6 Authz：分级自主 + 意图绑定凭证（后通道授权）

- **Graduated Autonomy**：安全运行时**透明拦截**实体出站动作（实体**不持有常驻凭证**），按敏感性分三态：autonomous（直接授权）/ supervised（走后通道人工批准）/ denied（拒绝）。分类函数是 policy，互操作要求的是三态结果与各自流程。
- **Backchannel Approval Flow**（OAuth 2.0 CIBA 风格）：绑定消息 = **人类可读的精确操作渲染**；响应携带 auth-request 标识 + **HMAC 签名、单次使用、过期 action token**（防止批准了另一个待决请求 / 响应伪造）；critical 敏感动作 MUST 用认证投递确认通道；**absent positive → denied**（拒绝、投递失败、approver 超时、过期一律拒绝）。
- **Intent-Scoped Credential**：JWT 携带 target resource + operation type + **canonicalized 参数 digest**（RFC 8785 + 命名哈希）——改动任一绑定字段即签名失效。
- **Digest Linkage（关闭 confused-deputy）**：**同一 canonicalized 参数 digest** 既限定凭证、又渲染给 approver——人类批准所见 = 凭证授权所及，杜绝"批准了 A、执行了 B"。
- **强制双模式**：resource-validated（凭证感知目标直接验证）/ enforcement-point（凭证盲目标由强制点验证后获取 just-in-time 单操作后端密钥）——支持凭证盲目标的同时运行时仍无常驻目标凭证。
- **单次使用消费**：强制点 MUST 在转发前原子标记凭证标识已消费（共享持久低延迟消费存储，跨副本/重启有效）——**防重放 + 防 TOCTOU**；lifetime 从签发起算、在强制点对同步时间源强制。

## 6. 架构族统一设计模式（跨草案的一致性）

| 模式 | 贯穿之处 | 设计动机 |
|:--|:--|:--|
| **Hash-chain 数据模型** | identity 链 / memory 图（relational pairs）/ audit 链 | 篡改可检测 + 局部验证 + 血统可追溯 |
| **CANON 确定性序列化** | 全部 7 份（JCS 或长度前缀） | 任何验证者重算字节一致输入 |
| **Genesis 锚定** | identity（0x00×32 sentinel）/ audit（H(subject_id)） | 链不可移植/不可伪造起点 |
| **注册表驱动敏捷性** | identity 签名套件 / audit tokenizer / memory reputation 公式 | 迁移不需新协议版本 |
| **Operator 根控制** | 撤销链事件 / absent-positive denied / quarantine | 三不变量之一，全协议落实 |
| **最小披露** | capability attestation / prove-without-exposing / content-optional | 可验证性与机密性不互斥 |

## 7. 与现有标准生态的关系

### 7.1 IETF 内部复用（arch §7：复用不替换）

| 现有标准 | 被复用为 |
|:--|:--|
| RFC 9334（RATS 远程证明） | identity 相关但**有别于**（identity 是链式血统，RATS 是设备状态证明） |
| RFC 9162（Certificate Transparency） | audit 链概念相邻但**以 Agent 推理/行动为范围** |
| RFC 6749 CIBA（OAuth 后通道） | authz 的后通道批准流 |
| RFC 9396（RAR 富授权请求） | intent-scoped credential 的参数绑定精神 |
| RFC 8785（JCS） | bootstrap manifest / authz 参数 digest 的确定性序列化 |
| RFC 5869（HKDF）/ RFC 7519（JWT）/ RFC 8032（Ed25519） | 密钥派生 / 凭证载体 / 经典签名 |

### 7.2 与 MCP / A2A 等 Agent 生态的关系（未展开，属缺口）

- NHE 族定位是**身份-信任-审计底座**；MCP（工具面协议）/ A2A（Agent 间协议）是**能力交互协议**——理论上互补，但 **arch §7 未讨论与 MCP/A2A 的关系**，是显著空白（详见 §9 批判）。
- 与知识库已沉淀的 Agent 安全研究高度同构：授权语义 SDK 级（approval 绑定调用）、hosted MCP identity、StepJack 多步间接注入——NHE 从**协议层**给出标准化答案。

## 8. 对 Agent 基础设施的启示（结合已实证攻击面）

| 已实证风险（知识库） | NHE 对应机制 | 效果 |
|:--|:--|:--|
| Salami 共谋投毒（81.3% 攻击成功率） | memory **independence guard** + lineage quarantine | 非独立贡献者的相互确认不计入佐证 → 共谋背书失效 |
| StepJack 多步间接注入（CUA ASR +31.2） | audit 链（action 在执行边界捕获）+ complexity-divergence 信号 | 注入导致的"小推理大行动"偏离可被检测 |
| 越权/凭证滥用（approval 未绑定调用） | authz intent-scoped credential + digest linkage | approver 所见 = 凭证所及，单次使用防重放 |
| OI 过度个性化（Personalization Mirage 44.6%） | prove-without-exposing（双作用域） | 可审计性不牺牲机密性，伦理可部署 |
| 模型/工具来源不可追溯 | audit 绑定 provider/model 进哈希 | "哪个模型推理了、推理了多少"不可篡改 |

**落地路线建议**：① 身份链（identity）可最先落地——数据模型完整、无生态依赖，可做 PoC（Ed25519 链 + no-fork 校验）；② audit 链次之（本地 identity 锚定副本模式对现有系统侵入最小）；③ memory/authz 依赖信誉策略与强制点部署，属第二阶段；④ mesh 需定义线上编码（-01）后才有互操作价值。

## 9. 局限与批判（诚实边界）

1. **全部 -00 骨架**：七份草案**数据模型已定、线上编码全部 deferred 到 -01**——目前无法互操作，是"架构宣言"而非可用协议。
2. **无实现、无验证**：无参考实现、无互操作测试、无攻击模型验证；单人作者（Ruvalcaba）的个人草案，未进任何工作组采纳流程（关联组 group/1027 为个人草案池）。
3. **MCP/A2A 生态缺口**：未讨论与既有 Agent 协议的关系——若 NHE 族与 MCP/A2A 平行演进，互操作碎片化风险存在。
4. **reputation 机制留白**：memory 的信誉函数是 pluggable policy（类比拥塞控制算法）——格式标准化了，**核心信任算法留给实现**，跨实现信誉值不可比。
5. **audit 诚实性依赖上游**：token_count 依赖 provider 报告（"推理规模"证明在 provider 不可信时降级为 byte_count 字节级证明）；reasoning 捕获依赖模型 provider 配合输出推理痕迹。
6. **mesh 的 exactly-once 缺口**：at-most-once 是核心保证，exactly-once 需任务幂等——分布式任务分发的老大难被显式外包给应用层。
7. **术语包袱**：NHE 源自 Synthetic Human Intellect (SHI) 框架——文档虽严格功能化，术语的拟人色彩可能引发歧义与误用。
8. **规模与性能未论证**：identity/audit 链的 O(n) 全链验证、memory 图的局部校验在"长生命周期 × 高频推理"的 Agent 规模下的实际成本未量化。

## 10. 参考资料路径

### 一手来源（IETF Datatracker，2026-08-14 核验）
- `draft-ruvalcaba-nhe-arch-00`：https://datatracker.ietf.org/doc/draft-ruvalcaba-nhe-arch/ （10 页）
- `draft-ruvalcaba-nhe-identity-00`：https://datatracker.ietf.org/doc/draft-ruvalcaba-nhe-identity/ （8 页）
- `draft-ruvalcaba-nhe-mesh-00`：https://datatracker.ietf.org/doc/draft-ruvalcaba-nhe-mesh/ （6 页）
- `draft-ruvalcaba-nhe-memory-00`：https://datatracker.ietf.org/doc/draft-ruvalcaba-nhe-memory/ （9 页）
- `draft-ruvalcaba-nhe-audit-00`：https://datatracker.ietf.org/doc/draft-ruvalcaba-nhe-audit/ （8 页）
- `draft-ruvalcaba-nhe-bootstrap-00`：https://datatracker.ietf.org/doc/draft-ruvalcaba-nhe-bootstrap/ （7 页）
- `draft-ruvalcaba-nhe-authz-00`：https://datatracker.ietf.org/doc/draft-ruvalcaba-nhe-authz/ （7 页）
- 文本版：https://www.ietf.org/archive/id/draft-ruvalcaba-nhe-{arch,identity,mesh,memory,audit,bootstrap,authz}-00.txt
- 配套：`draft-ruvalcaba-hctp`（Hash-Chain Context Transfer Protocol，连续性接口，状态更成熟）
- 引用标准：RFC 2119/8174、8785（JCS）、7519（JWT）、6749（CIBA）、9396（RAR）、9334（RATS）、9162（CT）、8032（Ed25519）、5869（HKDF）、5116（AEAD）

### 内部知识库交叉链接
- **Agent 安全基线**：MEMORY.md「深度洞察：AI 与 Agent」——StepJack 多步注入、Salami 共谋投毒 81.3%、授权语义 SDK 级、OI 对抗 G1-G5（本分析的攻击面对照表源头）
- **Agent 工程目录**：[knowledge/03_AI/agent-engineering/](./)（Aries 可观测性、Rovo、Agora、tool-call observability 等）
- **记忆研究**：knowledge/03_AI/（MindMemOS 离线整理、Personalization Mirage、When Memory Lies、四态生命周期）——NHE memory 的置信度/血统设计与这些实证发现同构
- **BMWG 基准测试**：[2026-08-14 BMWG AI Fabric 基准三件套](../../05_tools/testing/2026-08-14-bmwg-ai-fabric-benchmarking-trilogy-deep-analysis.md)（同日另组 IETF 草案族——IETF 正在两条线同时为 AI 基建立标准：网络度量 + Agent 身份/信任）

### 本地素材
- `tmp/nhe-trilogy/{arch,identity,mesh,memory,audit,bootstrap,authz}-00.txt`（七份草案全文，2026-08-14 下载）

---

## Changelog

| 日期 | 变更 |
|:--|:--|
| 2026-08-14 | 初版：基于七份草案 -00 全文精读（08-13 齐发）；含七组件参考模型、三不变量、五条密码学主线（identity/mesh/memory/audit/bootstrap/authz）逐份原理详解、与已实证攻击面对照、MCP/A2A 生态缺口批判、落地路线建议 |
