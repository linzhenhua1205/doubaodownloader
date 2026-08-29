# PostgreSQL 客户端认证配置：pg_hba.conf 详解

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [knowledgedict - PostgreSQL 客户端认证配置](https://www.knowledgedict.com/tutorial/postgresql-client-authentication-config.html)
> **配套**: [远程连接配置与安全](2026-08-15-postgres-remote-access-security.md) / [允许 IP 远程访问](2026-08-15-postgres-ip-remote-access.md) / [权限配置与验证](2026-08-15-postgres-privilege-config-verify.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、设计哲学：为何用文本文件](#二设计哲学为何用文本文件)
- [三、记录格式与字段](#三记录格式与字段)
- [四、连接方式四兄弟](#四连接方式四兄弟)
- [五、认证方法谱系](#五认证方法谱系)
- [六、地址匹配规则](#六地址匹配规则)
- [七、典型配置案例](#七典型配置案例)
- [八、安全最佳实践](#八安全最佳实践)
- [九、2025-2026 演进](#九2025-2026-演进)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

`pg_hba.conf`（Host-Based Authentication）是 PostgreSQL **客户端认证的唯一入口**，控制"谁能连、从哪里连、用什么方式认证"：

| 维度 | 要点 |
|:-----|:-----|
| 位置 | 数据目录下，如 `/var/lib/pgsql/<版本>/data/pg_hba.conf` |
| 格式 | 每行一条规则：`连接方式 数据库 用户 地址 认证方法 [参数]` |
| 匹配 | **顺序匹配，命中即停**，未匹配则拒绝 |
| 生效 | 修改后 `pg_ctl reload`（或 `SELECT pg_reload_conf()`）即生效，无需重启 |

**核心结论**：
1. **认证策略与认证数据分离**：pg_hba.conf 管"谁能连"，`pg_authid` 表存"密码哈希"——数据库不可达时也能改文件恢复访问
2. **顺序匹配是最大安全陷阱**：宽松规则放前面会覆盖后面的严格规则，生产环境**拒绝规则置顶 + 兜底拒绝在末行**
3. **scram-sha-256 是事实标准**：PG10 引入、PG14 默认，2025 年超 80% 生产实例已迁移，md5 仅用于老客户端兼容
4. **认证方法安全谱系**：trust < password < md5 < scram-sha-256 < cert < ldap/pam

---

## 二、设计哲学：为何用文本文件

### 2.1 认证分离架构

| 组件 | 职责 | 位置 |
|:-----|:-----|:-----|
| pg_hba.conf | 谁能连、怎么认证 | 外部文本，离线可编辑 |
| pg_authid | 密码哈希 | 数据库系统表 |

- 与 MySQL 的 `mysql.user` 表不同，PG 将策略与数据分离
- **优势**：审计员可直接审查一个文本文件了解全部访问授权；数据库不可达时仍可调整策略

### 2.2 避免鸡生蛋问题

- 若认证策略存系统表，启动数据库需先连接读取策略——循环依赖
- 文本文件让数据库**启动前就能确定认证策略**，成为灾难恢复入口：忘记管理员密码时，改文件为 `trust` 重启进入重置

---

## 三、记录格式与字段

### 3.1 七种格式

| 格式 | 适用 |
|:-----|:-----|
| `local database user auth-method [opt]` | Unix 套接字 |
| `host database user CIDR auth-method [opt]` | TCP/IP（CIDR） |
| `host database user IP mask auth-method [opt]` | TCP/IP（IP+掩码） |
| `hostssl ...` | 仅 SSL 连接 |
| `hostnossl ...` | 仅非 SSL 连接 |
| `hostgssenc ...` | 仅 GSS 加密连接（PG12+） |
| `hostnogssenc ...` | 仅非 GSS 连接（PG12+） |

### 3.2 数据库/用户通配

| 写法 | 含义 |
|:-----|:-----|
| `all` | 匹配所有数据库/用户 |
| `db1,db2` | 逗号分隔多值 |
| `@filename` | 引用外部文件（如 `@admins`） |
| `+groupname` | 匹配组成员（如 `+support`） |
| `sameuser` | 仅匹配与数据库同名的用户 |
| `samerole` | 仅匹配与数据库同名的角色成员 |

### 3.3 基础查询与生效

```sql
-- show effective hba config
SELECT * FROM pg_hba_file_rules;

-- reload without restart
SELECT pg_reload_conf();
```

### 3.4 配置量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 记录格式 | 7 种 | local/host/hostssl/hostnossl/hostgssenc/hostnogssenc/host+掩码 |
| 连接方式 | 4 种基础 | local / host / hostssl / hostnossl |
| 认证方法 | 10+ 种 | trust/reject/password/md5/scram-sha-256/cert/ident/krb5/ldap/pam |
| 默认端口 | 5432 | 服务监听 TCP 端口 |
| reload 生效 | < 1s | `pg_reload_conf()` 无需重启 |

---

## 四、连接方式四兄弟

| 方式 | 说明 | 安全等级 |
|:-----|:-----|:--------:|
| `local` | Unix 域套接字（本机进程） | 高（OS 权限控制） |
| `host` | TCP/IP（SSL/非 SSL 均可） | 中 |
| `hostssl` | 仅 SSL 加密的 TCP/IP | 高（需 openssl 编译支持） |
| `hostnossl` | 仅非 SSL 的 TCP/IP | 低（明文风险） |

- **最佳实践**：远程访问一律用 `hostssl`，禁用 `hostnossl` 或仅限内网
- 检查 SSL 支持：`SHOW ssl;`（on 表示服务器已开启 SSL）

---

## 五、认证方法谱系

### 5.1 安全等级排序

| 等级 | 方法 |
|:----:|:-----|
| 低安全 | trust < password(明文) < md5 |
| 中安全 | scram-sha-256 |
| 高安全 | cert < ldap/pam |

### 5.2 方法详解

| 方法 | 机制 | 适用 |
|:-----|:-----|:-----|
| `trust` | 无条件放行，无需密码 | 仅限本机/调试，生产禁用 |
| `reject` | 无条件拒绝 | 过滤特定主机/网段 |
| `password` | 明文传密码 | 禁用于不安全网络 |
| `md5` | MD5 哈希口令 | 老客户端兼容 |
| `scram-sha-256` | 加盐 + nonce + channel binding | **PG10+ 推荐，PG14 默认** |
| `cert` | 客户端 SSL 证书 | 双向 TLS |
| `ident` | ident 协议映射 OS 用户名 | 内网可信环境 |
| `krb5` | Kerberos V5 | 企业 AD 域 |
| `ldap` / `pam` | 外部认证集成 | 统一身份管理 |

### 5.3 scram-sha-256 为何取代 md5

1. **防彩虹表攻击**：每用户独立盐值
2. **防重放攻击**：客户端 nonce 随机数
3. **防中间人攻击**：channel binding 绑定 TLS 通道
4. PG14 起 `password_encryption` 默认 `scram-sha-256`，新密码哈希自动采用

```sql
-- verify encryption method in use
SELECT rolname, rolpassword LIKE 'SCRAM%' AS is_scram
FROM pg_authid;
```

---

## 六、地址匹配规则

### 6.1 CIDR 格式

| 写法 | 匹配范围 |
|:-----|:---------|
| `172.20.143.89/32` | 精确单 IP |
| `192.168.0.0/16` | 192.168.x.x 整个网段 |
| `10.0.0.0/8` | 10.x.x.x 内网 |
| `0.0.0.0/0` | 所有 IPv4（危险） |
| `::1/128` | IPv6 回环 |

### 6.2 IP+掩码等价

- `127.0.0.1 255.255.255.255` ≡ `127.0.0.1/32`
- 两种写法等价，CIDR 更简洁推荐

---

## 七、典型配置案例

### 7.1 最小安全配置（生产基线）

```conf
# TYPE  DATABASE  USER  ADDRESS        METHOD
local   all       all                   scram-sha-256
host    all       all   127.0.0.1/32    scram-sha-256
host    all       all   ::1/128         scram-sha-256
host    all       all   192.168.0.0/16  scram-sha-256
hostssl all       all   0.0.0.0/0       scram-sha-256
```

### 7.2 特定 IP 授权（单库单用户）

```conf
host postgres all 192.168.12.10/32 md5
```

### 7.3 混合规则（本地+管理员组）

```conf
local sameuser all md5
local all @admins,+support md5
```

### 7.4 安全加固（拒绝置顶 + 兜底拒绝）

```conf
# deny unknown networks first
host all all 10.0.0.0/8 reject
host all all 172.16.0.0/12 reject
# then allow specific trusted ranges
hostssl all all 10.20.0.0/16 scram-sha-256
# fallback deny
host all all 0.0.0.0/0 reject
```

---

## 八、安全最佳实践

| # | 实践 | 理由 |
|:-:|:-----|:-----|
| 1 | 远程一律 `hostssl` | 防窃听 |
| 2 | 拒绝规则置顶、兜底拒绝在末行 | 顺序匹配防绕过 |
| 3 | 生产禁用 `trust` | 无认证 = 门户大开 |
| 4 | 新实例默认 `scram-sha-256` | 密码强度与防重放 |
| 5 | 最小网段授权（/32 > /16） | 缩小攻击面 |
| 6 | 定期审计 `pg_hba_file_rules` | 配置漂移检测 |
| 7 | 修改前备份 + reload 后验证 | 防锁死 |

### 灾难恢复流程

忘记管理员密码时：
1. 编辑 pg_hba.conf：临时改为 `local all all trust`
2. `pg_ctl reload` 重启
3. 连接后 `ALTER ROLE postgres PASSWORD 'newpass';`
4. 恢复原配置并 reload（**必须恢复**，否则留下后门）

---

## 九、2025-2026 演进

| 版本 | 变化 |
|:-----|:-----|
| PG17（2024-09） | `cert` 支持 SHA-256 证书指纹，替代 MD5 指纹 |
| PG18（2025-09 预计） | 计划引入 OAuth 2.0 bearer token 认证 |
| 生态 | scram-sha-256 迁移率 > 80%；云厂商（RDS/Azure/GCP）提供 pg_hba 可视化编辑 |

---

## 相关文档

- [远程连接配置与安全](2026-08-15-postgres-remote-access-security.md) — 完整远程访问链路
- [允许 IP 远程访问的配置步骤](2026-08-15-postgres-ip-remote-access.md) — 最小步骤实操
- [权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) — 认证之后的授权层
- [服务启动失败排查](2026-08-15-postgres-startup-failure-port5432.md) — 连接失败的另一个侧面

---

## 参考来源

- knowledgedict：PostgreSQL 客户端认证配置
- [PostgreSQL 官方文档：客户端认证（Chapter 21）](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
- [PostgreSQL 官方文档：密码认证方法](https://www.postgresql.org/docs/current/auth-password.html)
- [PostgreSQL 14 Release Notes（password_encryption 默认值）](https://www.postgresql.org/docs/14/release-14.html)

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（设计哲学 + 七种格式 + 认证谱系 + scram 演进 + 安全加固案例 + 灾难恢复 + 2025 演进）
