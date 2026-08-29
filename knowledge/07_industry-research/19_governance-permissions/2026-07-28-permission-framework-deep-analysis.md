# 多层级权限框架深度分析：飞书平台、BMC、OS 与 AI Agent 交互

> **版本**: v1.0 | **更新**: 2026-07-28
> **覆盖范围**: 飞书(Lark)企业协作平台 × BMC服务器管理 × 操作系统安全 × RBAC体系 × AI Agent权限边界
> **文档状态**: 初版 — 理论框架 + 技术实现 + 工程实践
> **概要**: 飞书(Lark)企业平台/BMC服务器管理/操作系统/Linux安全/AI Agent 六层权限框架深度分析 + RBAC 体系 + 「用后即丢」数据处理机制
> **关键词**: 权限, RBAC, BMC, Redfish, 飞书, Feishu, SELinux, Access Control, 用后即丢, Ephemeral Data, PEP, 策略执行点

## 📑 目录

- [1. 引言：权限问题的多层级本质](#1-引言权限问题的多层级本质)
- [2. 权限模型基础分类](#2-权限模型基础分类)
- [3. 飞书(Lark)平台权限体系](#3-飞书lark平台权限体系)
- [4. BMC 权限框架](#4-bmc-权限框架)
- [5. 操作系统权限框架](#5-操作系统权限框架)
- [6. RBAC 深度分析](#6-rbac-深度分析)
- [7. 「用后即丢」数据处理与安全机制](#7-用后即丢数据处理与安全机制)
- [8. AI Agent 在企业系统中的权限设计](#8-ai-agent-在企业系统中的权限设计)
- [9. 跨层权限传播与冲突](#9-跨层权限传播与冲突)
- [10. 设计建议与最佳实践](#10-设计建议与最佳实践)
- [参考文献](#参考文献)
- [变更记录](#变更记录)

---

## 1. 引言：权限问题的多层级本质

### 1.1 问题定位

当 AI Agent（或人类驱动的自动化系统）与飞书平台交互时，面临的是**多层嵌套的权限问题**：

```text
用户 -> 飞书 -> API Gateway -> 服务端 -> BMC -> 服务器硬件
  v       v         v           v       v       v
身份    组织     应用       服务     带外    物理
认证    角色     权限       账号     管理    访问
                 授权       授权    权限     控制
```

每一层都有自己的权限模型——认证机制不同、授权粒度和范围不同、审计追踪能力不同。AI Agent 要完成的**一次操作**可能需要跨越 3-5 层权限检查，任意一层失败则操作中断。

### 1.2 核心张力

| 张力维度 | 平台/企业侧需求 | AI Agent 需求 | 冲突点 |
|:---------|:---------------|:-------------|:-------|
| **权限粒度** | 最小权限原则，细粒度控制 | 能灵活完成任务，避免频繁授权失败 | 过细的权限导致 Agent 频繁失败 |
| **数据持久性** | 有据可查，审计追踪 | 临时数据处理后自动清除 | 保存太多：隐私风险；保存太少：不可审计 |
| **时效性** | 权限定期复审，过期回收 | 需要稳定的权限上下文 | 权限过期导致任务中断 |
| **身份锚定** | 以自然人身份为最终责任主体 | Agent 需要独立身份标识 | Agent 行为是否可归责到人？ |

> **核心问题**: 不是「建一个统一的权限系统」，而是**理解七层权限框架的各自约束和交互方式**，让 AI Agent 在每层的权限范围内执行操作。

---

## 2. 权限模型基础分类

### 2.1 四种经典权限模型

| 模型 | 原理 | 管理复杂度 | 精细化程度 | 适用场景 |
|:-----|:------|:---------:|:---------:|:---------|
| **DAC** (自主访问控制) | 资源所有者自主决定谁可以访问 | 低 | 低 | 个人文件系统 |
| **MAC** (强制访问控制) | 系统强制策略，用户不可绕过 | 高 | 中 | 军事/政府系统, SELinux |
| **RBAC** (基于角色的访问控制) | 角色→权限映射，用户赋角色 | 中 | 高 | 企业系统(80%以上采用) |
| **ABAC** (基于属性的访问控制) | 用户/资源/环境属性动态计算 | 高 | 极高 | 大型云平台, 物联网 |

### 2.2 权限模型的选择边界

```text
              简单管理              复杂管理
              +---------------------+
   粗粒度     |  DAC              MAC |  细粒度
              |  (Windows文件权限)  (SELinux) |
              |                     |
              |  RBAC           ABAC |
              |  (飞书/HR系统)   (AWS IAM) |
              +---------------------+
              低灵活性            高灵活性
```

> **选择规律**: 团队规模 <50 人 → DAC 足够；50-5000 人 → RBAC 最优；>5000 人且高度管制 → RBAC+ABAC 混合。

### 2.3 认证 vs 授权 vs 审计（AAA）

| A | 功能 | 典型协议/标准 | 失败后果 |
|:-:|:-----|:-------------|:---------|
| **Authentication** | 你是谁？ | OAuth 2.0, SAML, LDAP, HTTP Basic, X.509 | 身份冒用 |
| **Authorization** | 你能做什么？ | RBAC, ABAC, ACL, Redfish PrivilegeMap | 越权操作 |
| **Accounting** | 你做了什么？ | Syslog, Redfish EventService, AuditD | 不可追溯 |

---

## 3. 飞书(Lark)平台权限体系

### 3.1 飞书的三层权限结构

飞书的权限体系分为三层，每层独立但可联动：

```text
                    +------------------------------+
      L1: 组织层    |  企业管理员 -> 部门管理员      |
      --------     |  -> 普通成员                   |
                    |  权限项: 通讯录可见范围        |
                    |          应用安装权限          |
                    |          数据导出权限          |
                    +------------------------------+
                                | 联动 (继承)
                                v
                    +------------------------------+
      L2: 空间层    |  知识库/文档/多维表格空间管理员 |
      --------     |  -> 创作者 -> 编辑者 -> 阅读者   |
                    |  权限项: 文档读写权限           |
                    |          空间成员管理           |
                    |          内容审批权             |
                    +------------------------------+
                                | 联动 (授权)
                                v
                    +------------------------------+
      L3: 应用层    |  应用管理员 -> 普通用户         |
      --------     |  (通过开放平台API)             |
                    |  权限项: 应用API调用权限        |
                    |          数据访问范围           |
                    |          Webhook事件订阅        |
                    +------------------------------+
```

### 3.2 开放平台权限（OAuth 2.0 实现）

飞书开放平台的权限授权基于**标准 OAuth 2.0**，但增加了企业租户特有的 scope 机制：

| 组件 | 说明 |
|:-----|:------|
| **App ID + App Secret** | 应用身份标识 |
| **Tenant Access Token** | 租户级访问凭证（代表企业身份） |
| **User Access Token** | 用户级访问凭证（代表具体用户身份） |
| **Scope** | 权限范围声明（如 `contact:user.readonly`） |
| **权限审批** | 管理员在管理后台授权应用访问特定数据 |

**关键 Scope 类型**（与 AI Agent 相关）：

| Scope | 资源 | 典型用途 | AI 交互风险 |
|:------|:-----|:---------|:-----------|
| `contact:user:readonly` | 通讯录 | 读取组织架构 | 用户隐私数据泄露 |
| `drive:drive` | 云空间 | 读取/写入文件 | 误写/覆盖文件 |
| `docx:document` | 文档 | 编辑文档 | 内容篡改 |
| `im:message` | 消息 | 发送/读取消息 | 信息泄露/误发 |
| `calendar:calendar` | 日历 | 读写日程 | 日程信息泄露 |
| `bitable:app` | 多维表格 | 操作数据表 | 数据误修改 |

### 3.3 AI Agent 与飞书交互时的权限挑战

```text
+---------------------------------------------------------+
| AI Agent (小龙猫) -> 飞书消息 -> API调用                   |
|                                                         |
| 权限检查链:                                              |
|  1. Agent 在飞书中以"机器人"身份注册                      |
|  2. 机器人有固定 App ID / App Secret                      |
|  3. 用户@机器人 -> 机器人收到消息事件 (需要 event:message)  |
|  4. 机器人处理 -> 调用 API -> 需要对应 scope 权限           |
|  5. API 请求->飞书验证 Tenant Access Token 对应的 scope   |
|  6. 有些 API 需要 User Access Token (代表用户而非机器人)  |
|                                                         |
| 典型断点:                                                |
|  - 机器人没有某个文档的权限 (需要放在对应文件夹)           |
|  - 有些 API 需要用户授权 (OAuth 2.0 用户授权流程)         |
|  - 跨租户操作不可能 (机器人绑定到单一租户)                 |
+---------------------------------------------------------+
```

### 3.4 数据保存与合规

| 数据类型 | 飞书默认存储策略 | AI 交互注意事项 |
|:---------|:---------------|:---------------|
| 消息内容 | 永久保存，可按消息ID回溯 | 确保消息不可被非授权读取 |
| 文档内容 | 版本化管理，可回溯 | AI 修改需创建版本快照 |
| 文件附件 | 存储于云空间，生命周期可配置 | 临时文件需手动清理 |
| API 调用日志 | 飞书侧保存 180 天 | 企业需自建审计系统补齐 |
| 用户操作日志 | 飞书管理后台可导出 | 需定期导出存档 |

---

## 4. BMC 权限框架

### 4.1 BMC 的基本角色

BMC（Baseboard Management Controller）是服务器上独立于主 CPU 运行的管理处理器，拥有**对服务器的最高操作权限**——即使主机关机、操作系统崩溃，BMC 仍能：

- 强制开关机/重启
- 挂载虚拟介质（远程挂载 ISO 安装系统）
- 接管 KVM（键盘/视频/鼠标）
- 读取传感器数据（温度/电压/功耗）
- 修改 BIOS/UEFI 设置
- 更新固件

> **安全意义**: BMC 权限失控 = 物理服务器完全失控。

### 4.2 Redfish 标准的认证与授权（DSP0266 v1.22 §13）

Redfish（DMTF 标准 DSP0266）是当前 BMC 管理的事实标准接口，替代了旧的 IPMI。

#### 4.2.1 认证机制

Redfish 支持四种认证方式（按安全等级排序）：

| 认证方式 | 安全等级 | 实现复杂度 | 适用场景 |
|:---------|:-------:|:---------:|:---------|
| **Session Login** (§13.3.4) | 🟢 高 | 低 | **推荐首选** — 标准方式 |
| **Client Certificate (mTLS)** (§13.3.5) | 🟢 最高 | 高 | 数据中心自动管理 |
| **HTTP Basic** (§13.3.3) | 🔴 低 | 最低 | 旧设备兼容（禁用于生产） |
| **OAuth 2.0 Delegated** (§13.4.4) | 🟡 中 | 高 | 企业级集成 |

**Session Login 工作流程**：

```text
POST /redfish/v1/SessionService/Sessions
  Headers: Authorization: Basic <base64(user:pass)>
  -> 201 Created
  -> Headers: X-Auth-Token: <session_token>

后续请求:
  GET /redfish/v1/Systems/1
  Headers: X-Auth-Token: <session_token>

登出:
  DELETE /redfish/v1/SessionService/Sessions/<session_id>
```

#### 4.2.2 Redfish 授权模型（§13.4）

Redfish 使用**基于角色的访问控制（RBAC）**：

| 预定义角色 | 权限等级 | 可执行操作 |
|:----------|:--------|:-----------|
| **Administrator** | 🔴 全部权限 | 所有操作，包括固件更新、账号管理、安全配置修改 |
| **Operator** | 🟡 操作权限 | 开关机、重启、虚拟介质挂载、传感器查看 |
| **ReadOnly** | 🟢 只读 | 查看传感器、系统信息、事件日志 |
| **OEM 自定义角色** | 厂商定义 | 各厂商自主定义（如 iDRAC 的"配电管理"角色） |

**操作到权限的映射**（§13.4.3 RedfishPrivileges）：

| HTTP Method | 资源类型 | 所需权限 |
|:------------|:---------|:---------|
| `GET` | 系统信息 | `Login` |
| `GET` | 传感器 | `Login` |
| `POST` | Session创建 | `Login` |
| `PATCH` | 系统状态(开关机) | `ConfigureManager` |
| `PATCH` | 网络设置 | `ConfigureNetworking` |
| `POST` | VirtualMedia挂载 | `ConfigureManager` |
| `PATCH` | 账号管理 | `ConfigureUsers` |
| `POST` | 固件更新 | `ConfigureComponents` |
| `DELETE` | 任何资源 | `ConfigureComponents` |

#### 4.2.3 账号服务（AccountService）

```text
/redfish/v1/AccountService/
+-- Accounts/                    # 用户账号列表
|   +-- <user_id>/               # 单个用户
|   |   +-- UserName
|   |   +-- RoleId               # 关联的角色
|   |   +-- Locked               # 锁定状态
|   |   +-- Password             # (Write-only)
|   |   +-- Oem                  # 厂商扩展
+-- Roles/                       # 角色定义
|   +-- Administrator/           # 预定义角色
|   +-- Operator/
|   +-- ReadOnly/
+-- LDAP/Certificate/AD          # 外部认证源配置
+-- PrivilegeRegistry/           # 操作权限映射表
```

### 4.3 各厂商 BMC 权限实现对比

| 厂商 | BMC 名称 | 权限模型 | 特有角色 | 额外安全特性 |
|:-----|:---------|:---------|:---------|:------------|
| **Dell** | iDRAC | RBAC (14个预定义角色) | 配电管理、存储管理、日志管理员 | 双因素认证、安全企业证书管理 |
| **HPE** | iLO | RBAC + 基于目录服务 | 虚拟电源管理、机箱管理员 | 安全恢复、硬件根信任 |
| **Huawei** | iBMC | RBAC (5个默认角色) | 监控用户、安全管理 | 信任启动、安全启动 |
| **浪潮** | InCloud BMC | RBAC (3个默认角色) | 无特有 | 基于IPMI 2.0 + Redfish混合 |
| **Supermicro** | BMC | RBAC (4个默认角色) | 无特有 | — |

### 4.4 OpenBMC 权限实现

OpenBMC 是开源 BMC 固件实现，其权限模型更具参考价值：

```text
OpenBMC 权限检查链:
  REST API 请求
    -> HTTP 认证层 (Session/Basic/Cookie)
    -> PAM (Pluggable Authentication Modules)
    -> phosphor-user-manager 角色检查
    -> 操作权限映射 (privilege_registry)
    -> 资源级访问控制
    -> 审计日志记录
```

**关键组件**:

| 组件 | 功能 | 对应 Redfish 标准 |
|:-----|:------|:-----------------|
| `phosphor-user-manager` | 用户/角色/特权管理 | AccountService |
| `phosphor-session-manager` | Session 生命周期 | SessionService |
| `entity-manager` | 硬件资源发现 | Chassis/System 资源树 |
| `obmc-console` | SOL (Serial-over-LAN) | ManagerNetworkProtocol |
| `phosphor-webui` | Web 界面 | Redfish GUI |

### 4.5 BMC 权限与 AI Agent 交互场景

```text
AI Agent (自动化运维) -> Redfish API
  |
  +- 只读场景 (Monitor) ✅ 安全
  |   GET /Systems/1/Processors
  |   GET /Chassis/1/Sensors
  |   -> 只需要 ReadOnly 角色
  |
  +- 运维场景 (Operate) ⚠️ 受控
  |   POST /Systems/1/Actions/ComputerSystem.Reset
  |   POST /Managers/1/VirtualMedia/InsertMedia
  |   -> 需要 Operator 角色 + 操作审批流程
  |
  +- 配置场景 (Configure) 🚨 高风险
      PATCH /Managers/1/NetworkProtocol/HTTPS/Certificates
      POST /Managers/1/Actions/Manager.Reset
      -> 需要 Administrator + 双人复核
```

> **AI 特有的风险**: Agent 可能被 prompt 注入操纵去执行 BMC 的高危操作。需要在飞书 ↔ Agent 之间设置策略执行点（PEP），限制 Agent 对 BMC 发出的指令类型。

---

## 5. 操作系统权限框架

### 5.1 Linux 权限体系全景

Linux 操作系统的权限体系是**多层叠加**的，从最底层到最上层：

```text
第5层: 应用层安全                  (DAC, Namespace, Seccomp)
第4层: Linux Security Modules     (SELinux/AppArmor, 强制访问控制)
第3层: Capabilities               (细粒度特权拆分)
第2层: 传统 DAC                   (User/Group/Other, rwx)
第1层: 内核安全                   (系统调用过滤, 地址随机化)
```

### 5.2 传统 Unix 权限（DAC）

**最小单位**: `rwx`（读/写/执行），按 `User:Group:Other` 三元组分配。

```text
-rw-r--r--  1 root  staff  1024 Jul 28 10:00 file.txt
 |  |  |      |     |
 |  |  |      |     +- 所属组 (staff) 的权限: r-- (只读)
 |  |  |      +- 所有者 (root) 的权限: rw- (读写)
 |  |  +- 其他用户权限: r-- (只读)
 |  +- 所属组权限: r-- (只读)
 +- 所有者权限: rw- (读写)
```

**局限**: 粒度过粗，无法表达「用户A只能读这个目录不能写，但能写这个文件」。

### 5.3 Linux Capabilities（特权拆分）

传统 Unix 中 root 拥有**全部特权**（二进制 0/1）。Capabilities 将 root 的超权拆分成 40+ 个独立权能：

| Capability | 作用 | 安全意义 |
|:-----------|:-----|:---------|
| `CAP_NET_RAW` | 创建 RAW socket | 避免赋予完整网络控制 |
| `CAP_NET_BIND_SERVICE` | 绑定低于 1024 端口 | Web 服务器无需 root |
| `CAP_SYS_ADMIN` | **大权能**：挂载/namespace | 拆分的"万能钥匙"（应避免） |
| `CAP_SYS_BOOT` | 重启/关机 | 限制物理操作 |
| `CAP_SYS_RAWIO` | I/O 端口/内存操作 | **极高风险** |
| `CAP_DAC_OVERRIDE` | 绕过 DAC 权限检查 | 文件访问权限绕过 |

**最佳实践**: 容器/服务应计算所需最小 capabilities，删除全部后用 `--cap-drop=ALL --cap-add=NEEDED` 逐个添加。

### 5.4 Linux Security Modules（LSM）

| LSM | 类型 | 策略配置复杂度 | 适用场景 |
|:----|:-----|:------------:|:---------|
| **SELinux** | MAC (强制) | 🔴 极高 | 政府/军事/银行 |
| **AppArmor** | MAC (强制) | 🟡 中 | Ubuntu/Debian 默认 |
| **Smack** | MAC (简化) | 🟢 低 | 嵌入式/IoT |
| **TOMOYO** | MAC (行为学习) | 🟡 中 | 学习模式适合初始配置 |
| **Yama** | 进程权限管控 | 🟢 低 | ptrace 限制 |
| **Landlock** | 非特权沙箱 | 🟢 低 | (相对新, v5.13+) |

**SELinux 的 RBAC 扩展**：

SELinux 不只是 MAC，还实现了**基于角色的访问控制扩展**（RBAC）：

```text
User (Linux用户) -> Role (角色, 如 user_r/sysadm_r)
  -> Type (域/类型) -> Permission (读/写/执行/信号等)
```

每次系统调用都经过以下检查路径：

```text
系统调用
  -> DAC 检查 (标准Linux权限)
  -> LSM hook
    -> SELinux: 检查 source_type:target_type:class:permission
    -> 允许/拒绝 + AUDIT日志
```

### 5.5 容器安全：Namespace + Cgroups + Seccomp

| 机制 | 隔离对象 | 突破风险 |
|:-----|:---------|:---------|
| **PID Namespace** | 进程列表可见性 | 低（单独突破较难） |
| **Mount Namespace** | 文件系统挂载点 | 🔴 可访问宿主机文件系统（需--privileged） |
| **Network Namespace** | 网络栈 | 低（配置不当可逃逸） |
| **User Namespace** | 用户 ID 映射 | 🟡 内核漏洞可突破 |
| **Cgroups** | 资源限制 | 低（资源耗尽攻击） |
| **Seccomp** | 系统调用过滤 | 低（配置不当可绕过） |

**AI Agent 运行在容器中的权限推荐**：

```text
docker run --cap-drop=ALL \
  --cap-add=NET_RAW \
  --cap-add=NET_BIND_SERVICE \
  --security-opt=no-new-privileges:true \
  --security-opt=seccomp=default.json \
  --read-only-rootfs \
  --tmpfs /tmp:noexec,nosuid,size=64m \
  my-ai-agent-image
```

### 5.6 Windows 权限体系（简要对比）

| 概念 | Linux 对应 | Windows 等效 |
|:-----|:----------|:-------------|
| SID (安全标识符) | UID/GID | SID (Unique) |
| ACL (访问控制列表) | 无原生(unix有setfacl) | DACL/SACL |
| Token | UID+GID+groups | 访问令牌 (含SID+特权) |
| 特权 (Privilege) | Capabilities | 用户权限(SeShutdownPrivilege等) |
| 完整性级别 | SELinux 安全级别 | IL (低/中/高/系统) |
| UAC | sudo | UAC (用户账户控制) |

---

## 6. RBAC 深度分析

### 6.1 RBAC 核心模型（NIST 标准）

NIST RBAC 标准定义四个层级，逐级增加复杂度：

```text
RBAC₀: 最小核心
  用户 -> 角色 <- 权限          (最简单的映射)

RBAC₁: 角色分层
  角色之间继承关系             (管理角色 > 基础角色)

RBAC₂: 职责分离 (SoD)
  +--- 静态SoD: 用户不能同时拥有冲突角色
  +--- 动态SoD: 同一会话中不能同时激活冲突角色

RBAC₃: 约束 + 分层 (综合)
  同时支持分层和职责分离
```

### 6.2 角色设计的 MECE 原则

好的角色设计应满足 MECE（Mutually Exclusive, Collectively Exhaustive）：

```text
❌ 坏的设计:                    ✅ 好的设计:
  管理员 (可以做一切)              只读用户 (只能读)
  操作员 (大部分操作)              运维操作员 (写操作、不管理)
  用户 (很少的操作)               配置管理员 (配置、不操作)
                                  审计员 (只读、专看日志)
                                  系统管理员 (全部)

  问题: 边界模糊                  原则: 每个角色有明确的
  操作员和管理员的重叠             操作边界，不存在"大部分"操作
  定义不清                        这种模糊概念
```

### 6.3 角色发现的通用方法论

```text
步骤1: 职责分析（功能分解）
  v  每个岗位的职责清单 -> 去重 -> 候选角色
步骤2: 权限聚类（操作分组）
  v  相似操作 -> 权限组 -> 关联角色
步骤3: SoD 检查
  v  冲突角色 -> 拆分或限制组合规则
步骤4: 角色层次优化
  v  继承关系 -> 减少重复授权
步骤5: 验证与迭代
     用户调查 -> 操作审计 -> 权限调整
```

### 6.4 常见 RBAC 反模式

| 反模式 | 现象 | 后果 | 修正方案 |
|:-------|:-----|:-----|:---------|
| **角色爆炸** | 50 人 → 47 个角色 | 管理成本爆增 | 权限组 + 角色分层标准化 |
| **权限滥用** | 所有人都分配管理员 | 安全形同虚设 | 最小权限原则强制执行 |
| **僵尸角色** | 角色创建后永不使用 | 审计发现不了 | 定期角色复审，90 天无使用自动回收 |
| **代理授权** | 用户间频繁共享账号/令牌 | 不可审计 | 支持 OAuth 2.0 委托授权 |
| **静态 SoD 死锁** | 冲突角色太多导致无法分配 | 阻碍正常工作 | `静态 SoD` → `动态 SoD` 转换 |

---

## 7. 「用后即丢」数据处理与安全机制

### 7.1 概念与类型

「用后即丢」（ephemeral data / use-and-discard）指数据在其使用目的达成后即被彻底清除，不留持久化痕迹。

| 类型 | 定义 | 示例 |
|:-----|:------|:-----|
| **会话级** | 会话结束后立即清除 | 飞书 OAuth 2.0 临时令牌 |
| **任务级** | 任务完成后清除 | AI Agent 处理过的临时文件 |
| **请求级** | 单一请求/响应完成后清除 | HTTP 请求日志截断 |
| **时间级** | 设置 TTL 到期自动清除 | 容器临时存储、缓存数据 |

### 7.2 「用后即丢」的实现机制

#### 7.2.1 会话令牌生命周期（BMC 最佳实践）

基于 Redfish 标准 §13.3.4.3 Session Lifetime：

```text
创建: POST /redfish/v1/SessionService/Sessions
  -> 返回 X-Auth-Token, 服务端记录 Session 创建时间 + 最后活跃时间

使用: 每次请求刷新 Session 超时计时 (Redfish 要求)
  -> 无操作超时: 默认 15-30 分钟 (可配置)

清理: 超时 -> 服务端自动清除 Session 记录
  -> 登出 -> DELETE 请求删除 Session

安全要求:
  - 令牌不得记入日志
  - 令牌不得在 URL 中传递
  - 令牌长度 ≥ 32 字节随机数
  - 创建/销毁/超时均记录审计日志
```

#### 7.2.2 临时文件自动清理

```text
+-----------------------------------------------------+
| AI Agent 处理流程中的临时文件生命周期                |
|                                                      |
|  用户上传 -> Agent 下载到 tmp/ -> 处理 -> 返回结果     |
|                |                              |      |
|                v                              v      |
|          tmp/工作文件                   结果持久化    |
|          TTL: 任务完成+5min            到 knowledge/  |
|          过期 -> systemd timer 清理                    |
|                                                      |
| 安全措施:                                            |
|  - tmpfs/memfs (不落盘)                               |
|  - 文件加密 (密钥仅存在于会话上下文中)                 |
|  - 安全删除 (shred 覆盖后再 unlink)                   |
|  - 不可执行权限 (noexec 挂载选项)                     |
+-----------------------------------------------------+
```

#### 7.2.3 飞书平台中的「用后即丢」

| 场景 | 数据 | 清除机制 | Agent 注意事项 |
|:-----|:-----|:---------|:--------------|
| Webhook 事件 | 消息事件体 | 飞书不再保留历史事件 | Agent 必须在收到后决定保存/丢弃 |
| 临时授权令牌 | OAuth 2.0 Token | 到期自动失效 | 使用 Refresh Token 轮换 |
| API 请求参数 | 请求中的敏感字段 | 飞书侧可配置日志脱敏 | Agent 不应在日志中记录敏感参数 |
| 推送消息 | 一次性消息卡片 | 开发者控制 | Agent 决定是否需要回执留存 |

### 7.3 与持久化的平衡

```text
                   安全要求高
                      |
         用后即丢 <---+---> 长期保存
         (隐私)       |      (审计)
                      |
                   安全要求低
```

| 维度 | 用后即丢 | 长期保存 | 妥协方案 |
|:-----|:---------|:---------|:---------|
| 审计需求 | ❌ 不可追溯 | ✅ 完全可追溯 | 保存元数据不保存内容 |
| 隐私合规 | ✅ 无泄露风险 | ❌ 数据堆积 | 自动过期 + 数据脱敏 |
| 问题排查 | ❌ 无法复盘 | ✅ 可完全回放 | 保留日志摘要 + 关键上下文 |
| 存储成本 | ✅ 极低 | ❌ 线性增长 | 分级存储 (热数据存完即删) |

**推荐策略**: 元数据持久化 + 数据负载用后即丢。

---

## 8. AI Agent 在企业系统中的权限设计

### 8.1 Agent 身份模型（三种范式）

| 范式 | 身份锚定 | 权限范围 | 审计责任 | 代表实现 |
|:-----|:---------|:---------|:---------|:---------|
| **A: 机器人身份** | Agent 拥有独立的 App ID | 固定 scope 集合 | Agent 负有全部责任 | 飞书机器人、Slack Bot |
| **B: 用户代理身份** | Agent 以用户名义操作 | 继承用户的权限 | 用户负有监督责任 | OpenAI Assistants API |
| **C: 混合身份** | Agent 独立身份 + 用户授权 | 角色权限 + 用户委托范围 | Agent 与用户共同负责 | Coze Bot、Dify |

### 8.2 策略执行点（PEP）设计

在 Agent 和平台之间引入策略执行点：

```text
用户指令
   |
   v
+---------------------+
| 策略执行点 (PEP)     |
|                      |
|  1. 意图分类         | <- 这个操作属于什么类型？
|  2. 权限评估         | <- Agent 有这个权限吗？
|  3. 数据范围限制     | <- 只能访问这个空间的数据
|  4. 风险评级         | <- 这是高危操作吗？
|  5. 审批/拦截/放行  |
|                      |
|  策略来源:           |
|  - 静态策略 (YAML)   |
|  - 管理员配置         |
|  - 用户授权           |
+---------------------+
   |
   v
目标平台 (飞书/BMC/OS)
```

**PEP 策略示例（YAML）**：

```yaml
policies:
  - name: "文档操作"
    scope: "docx:document"
    rules:
      - action: "read"
        allowed: true
        rate_limit: 100/hour
      - action: "write"
        allowed: true
        require_approval: true  # 写操作需要审批
      - action: "delete"
        allowed: false          # Agent 不能删除文档

  - name: "服务器操作"
    scope: "redfish:/Systems/"  # 通过 Redfish 管理服务器
    rules:
      - method: "GET"
        allowed: true           # 允许全部只读
      - method: "POST"
        action: "Reset"
        allowed: true
        require_approval: true  # 重启需要审批
        time_window: "09:00-18:00"  # 仅工作时间可执行
      - method: "PATCH"
        allowed: false          # Agent 不能修改服务器配置
```

### 8.3 Agent 权限的六大原则

| # | 原则 | 说明 | 实施方法 |
|:-:|:-----|:------|:---------|
| 1 | **最小权限** | Agent 只获得完成任务所需的最小权限集 | Scope 最小化 + RBAC 最低角色 |
| 2 | **微令牌化** | 每次任务获取临时令牌，而非长期 Token | OAuth 2.0 short-lived token |
| 3 | **操作可审计** | Agent 的每一个操作都产生审计记录 | 第三方审计 + 日志不可篡改 |
| 4 | **职责分离** | Agent 不能既创建又审批自己的操作 | SoD 规则禁止执行+审批同角色 |
| 5 | **意图验证** | 关键操作前确认用户意图 | 用户确认对话框 (confirmation) |
| 6 | **降级生存** | 权限不足时优雅降级而非崩溃 | 告知用户缺少什么权限，请求补充 |

### 8.4 当前本工程的 Agent 权限现状（小龙猫）

| 层面 | 当前权限 | 风险等级 | 改进方向 |
|:-----|:---------|:-------:|:---------|
| **飞书机器人** | 应用的 Tenant Token，可发送消息 | 🟢 低 | 无写文档权限 |
| **知识库读写** | 工作空间内任意读写 | 🟡 中 | 需明确知识库写权限的红线（别改别删） |
| **Bash 执行** | **工作空间内无限制** | 🔴 **高** | 最需要约束的权限 |
| **文件操作** | mv 到 tmp/bak 为「软删除」 | 🟢 规则保护 | 已有 RULE.md 约束 |
| **Web 访问** | browser 可访问任意 URL | 🟡 中 | 需限制内网/敏感资源 |
| **定时任务** | 由用户创建，Agent 执行 | 🟢 低 | 由用户指定的执行逻辑 |

> **当前最高风险**: Bash 执行在工作空间内有完整权限。虽然 RULE.md 中有「永不 rm」的安全红线，但防御层是**信任 Agent 的规则遵守能力**而非系统级沙箱。

---

## 9. 跨层权限传播与冲突

### 9.1 权限传播链

一个典型操作需要跨越的权限层：

```text
用户通过飞书对小龙猫说:
  "帮我重启 10.0.1.100 这台服务器"

权限链:
  L1. 飞书组织层:  用户是 AI 团队 -> 可以使用机器人
  L2. 飞书应用层:  机器人有 Tenant Token + im:message scope
  L3. 网络访问层:  Agent 可访问 10.0.1.0/24 网段
  L4. BMC 认证:    Redfish Session Login (具有 Operator 角色)
  L5. BMC 授权:    Operator 角色是否允许 Reset 操作？-> ConfigureManager ✓
  L6. 操作审计:    Redfish EventService 记录操作 + 飞书消息归档
```

### 9.2 常见的跨层权限冲突

| 冲突场景 | 表现 | 根因 |
|:---------|:-----|:------|
| L2 有权限但 L4 没有 | 飞书应用可调用 API，但 BMC 返回 401 | Token 过期或角色不足 |
| L4 有权限但 L3 没有 | BMC 配置了 Operator 权限，但 Agent 不能访问管理网络 | 网络隔离未打通 |
| L1 有权限但 L2 没有 | 用户是管理员，但机器人没有安装到该部门 | 应用可见范围未配置 |
| L5 审计发现 L4 未记录 | Redfish 操作成功但审计日志缺失 | BMC 审计配置不完整 |

### 9.3 跨层权限模型映射

每一层的权限模型不同，跨层映射时会发生语义丢失：

```text
  飞书层 (ABAC + RBAC)                BMC层 (RBAC)
  +------------------+               +------------------+
  | AI Team 管理员    |------->        | Administrator    |
  |  -> 应用管理权     | 推荐映射      |  -> 完整的 API 权  |
  | AI Team 普通成员  |--------->     | Operator          |
  |  -> 应用使用权限   |              |  -> 运维操作权      |
  | 外部合作者         |--------->    | ReadOnly          |
  |  -> 受限查看权限   |              |  -> 只读传感器      |
  +------------------+               +------------------+

  问题: 飞书里的"部门管理员"和 BMC 里的"Operator"
  权限边界不一致，导致"有权限但操作失败"或"无权限但能操作"
```

---

## 10. 设计建议与最佳实践

### 10.1 飞书 + AI Agent 权限架构建议

```text
                    +--------------------------+
                    | 组织身份提供商 (IdP)      |
                    |  飞书/LDAP/AD              |
                    +------------+-------------+
                                 | SAML/OIDC
                                 v
              +----------------------------------+
              | 统一权限网关 (OAuth 2.0 + PEP)    |
              |                                   |
              |  Token 管理   策略执行  审计日志   |
              |  +--------+  +-------+ +-------+ |
              |  |短期Token|->|PEP检查 |->|审计记录| |
              |  +--------+  +-------+ +-------+ |
              +----------------+-----------------+
                               |
         +---------------------+---------------------+
         |                     |                     |
         v                     v                     v
   +-------------+   +--------------+   +-----------------+
   | 飞书平台     |   | 服务器 (BMC) |   | 知识库/存储     |
   | OAuth Token  |   | Redfish/RBAC |   | 读写权限        |
   | scope 限制   |   | 角色控制     |   | ACL 控制        |
   +-------------+   +--------------+   +-----------------+
```

### 10.2 权限设计检查清单

| 检查项 | 描述 | 飞书层 | BMC层 | OS层 |
|:-------|:-----|:------|:------|:------|
| 是否有默认 deny？ | 默认拒绝，白名单模式 | ✅ | ✅ (Redfish) | ✅ (SELinux) |
| 最小权限可枚举？ | 能否列出需要的全部权限 | 部分 | ✅ | ✅ (Capabilities) |
| 是否有 SoD 约束？ | 冲突角色是否分离 | ❌ | ✅ | 部分 |
| 是否有审计日志？ | 所有操作是否可追溯 | ✅ (管理后台) | ✅ (EventService) | ✅ (auditd) |
| 是否有超时机制？ | 权限/令牌是否自动过期 | ✅ (OAuth 2.0) | ✅ (Session) | ✅ (sudo) |
| 是否有紧急通道？ | 权限失效时是否有后备方案 | ✅ (管理员) | ✅ (IPMI LAN+) | ✅ (物理控制) |

### 10.3 本工程可落地的改进

基于当前工作空间（~/cow）的 Agent 运行环境，按优先级：

**P0 🚨 安全沙箱增强**：

```text
当前: Agent 在工作空间内 bash 无限制
改进:
  - 容器化运行 (Docker with --cap-drop=ALL)
  - 文件系统只读 (除 tmp/ 和 knowledge/ 外)
  - 限制 outbound 网络 (仅放行 deepseek/飞书)
```

**P1 🟠 操作审计**：

```text
当前: 无系统级审计，依赖 Agent 自主记录
改进:
  - 所有 bash 执行前先记录到审计日志文件
  - AI Agent 的每个关键决策点写入 structured audit log
  - 飞书消息带请求ID，形成端到端追踪链
```

**P2 🟡 飞书权限声明**：

```text
当前: 使用 Tenant Token，scope 范围由管理员一次设定
改进:
  - 区分「只读任务」和「写操作任务」
  - 写操作前通过飞书卡片确认用户意图
  - 定期复审 Token 的 scope 是否仍然最小
```

---

## 参考文件

### 外部资料引用

[1] DMTF. *Redfish Specification DSP0266 v1.22.0*. 2025-02-05. §13 Security details, §13.4 Authorization, §13.3 Authentication.
[2] NIST. *Role Based Access Control (RBAC)*. NIST Standard 359-2012.
[3] 飞书开放平台. *权限概述与 scope 机制*. open.feishu.cn.
[4] OpenBMC Project. *Security Model Design*. GitHub - openbmc/docs.
[5] Linux Kernel Documentation. *Linux Security Module Usage*. kernel.org/doc/html/latest/admin-guide/LSM/.
[6] Kubernetes Documentation. *Pod Security Standards*. kubernetes.io.
[7] Docker Documentation. *Docker Security*. docs.docker.com/engine/security/.
[8] Red Hat. *SELinux User's and Administrator's Guide*. access.redhat.com.
[9] Ferraiolo, D.F., Kuhn, D.R., Chandramouli, R. *Role-Based Access Control (2nd Edition)*. Artech House, 2007.

### 内部知识库引用

- `spec/design-001-knowledge-strategy.md` — 知识库策略体系
- `knowledge/concepts/2026-07-20-meeting-management-analysis.md` — 组织协作基础能力
- `knowledge/05_tools/knowledge-management/2026-06-26-knowledge-system.md` — 知识体系方法论
- `knowledge/03_AI/tech-research-notes/2026-06-26-notes-summary.md` — 技术研究笔记汇总
- `RULE.md` — 工作空间安全红线与文件操作规则
- `AGENT.md` — AI Agent 行为准则与自检清单

[1] DMTF. *Redfish Specification DSP0266 v1.22.0*. 2025-02-05. §13 Security details, §13.4 Authorization, §13.3 Authentication.
[2] NIST. *Role Based Access Control (RBAC)*. NIST Standard 359-2012.
[3] 飞书开放平台. *权限概述与 scope 机制*. open.feishu.cn.
[4] OpenBMC Project. *Security Model Design*. GitHub - openbmc/docs.
[5] Linux Kernel Documentation. *Linux Security Module Usage*. kernel.org/doc/html/latest/admin-guide/LSM/.
[6] Kubernetes Documentation. *Pod Security Standards*. kubernetes.io.
[7] Docker Documentation. *Docker Security*. docs.docker.com/engine/security/.
[8] Red Hat. *SELinux User's and Administrator's Guide*. access.redhat.com.
[9] Ferraiolo, D.F., Kuhn, D.R., Chandramouli, R. *Role-Based Access Control (2nd Edition)*. Artech House, 2007.

---

## Changelog

| 日期 | 版本 | 变更说明 |
|:----|:----:|:---------|
| 2026-07-28 | v1.0 | 首次创建 — 覆盖飞书/BMC/OS/RBAC/AI Agent权限框架、「用后即丢」数据处理、跨层权限传播分析 |
