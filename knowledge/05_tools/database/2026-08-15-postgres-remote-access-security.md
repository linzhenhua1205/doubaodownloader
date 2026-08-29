# PostgreSQL 远程连接配置与安全指南## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 安全层级 | 3 层（100% 需同时） | 网络+认证+传输 |
| 强密码 | ≥16 位（约 10^30 组合） | 防爆破 |
| SSL 证书 | 365 天有效期 | 自签示例，生产用 CA |
| 缓存命中率 | ≥99%（OLTP 基线） | 监控参考 |
| 端口收敛 | 5432 → 非默认（0.1% 扫描概率） | 降暴露 |

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、三层安全模型](#二三层安全模型)
- [三、远程连接配置步骤](#三远程连接配置步骤)
- [四、SSL 加密配置](#四ssl-加密配置)
- [五、安全加固清单](#五安全加固清单)
- [六、生产环境禁忌](#六生产环境禁忌)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [量化速查](#量化速查)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 远程连接的安全核心是 **三层防护模型**：网络层（防火墙）+ 认证层（pg_hba）+ 传输层（SSL）：

| 层 | 手段 | 防护对象 |
|:---|:-----|:---------|
| 网络层 | 防火墙/安全组限定来源 | 未授权主机连接 |
| 认证层 | pg_hba + scram-sha-256 | 密码被破解/暴力破解 |
| 传输层 | SSL 加密 | 中间人窃听/篡改 |

**核心结论**：
1. **默认仅本地**：远程访问必须手动改 `listen_addresses` + `pg_hba.conf` + 防火墙，三处联动
2. **三重防护缺一不可**：IP 限制防"谁来"，密码认证防"谁登录"，SSL 防"看什么"
3. **生产环境三条红线**：禁 `0.0.0.0/0 trust`、禁明文 password 认证、禁不开 SSL
4. **scram-sha-256 + hostssl 是远程访问的事实标准组合**

---

## 二、三层安全模型

### 2.1 防护纵深

| 层 | 拦截点 | 被绕过后果 |
|:---|:-------|:-----------|
| 网络层 | 防火墙/安全组（IP 白名单） | 公网任意主机可连 |
| 认证层 | pg_hba 规则 + 密码 | 账号密码可被爆破 |
| 传输层 | SSL/TLS 加密 | 传输内容被窃听/篡改 |

### 2.2 攻击路径与防御

| 攻击 | 主要防御层 |
|:-----|:-----------|
| 端口扫描 + 未授权访问 | 网络层（限源） |
| 弱口令爆破 | 认证层（强密码 + scram） |
| 中间人窃听 | 传输层（SSL） |
| 应用层注入 | 应用侧（参数化查询，非数据库配置） |

---

## 三、远程连接配置步骤

### 3.1 修改 postgresql.conf

```conf
# /etc/postgresql/<version>/main/postgresql.conf
listen_addresses = '*'   # all interfaces
# or specific: listen_addresses = '192.168.1.10,127.0.0.1'
```

### 3.2 修改 pg_hba.conf

```conf
# /etc/postgresql/<version>/main/pg_hba.conf
# add at END (order matters: first match wins)
hostssl all all 192.168.1.0/24 scram-sha-256
```

### 3.3 重启与验证

```bash
sudo systemctl restart postgresql
# or reload for pg_hba only
sudo systemctl reload postgresql
```

```sql
SHOW listen_addresses;
SELECT * FROM pg_hba_file_rules;
```

---

## 四、SSL 加密配置

### 4.1 服务端开启 SSL

```conf
# postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

```bash
# generate self-signed cert (test/dev)
openssl req -new -x509 -days 365 -nodes \
  -text -out server.crt -keyout server.key \
  -subj "/CN=pg-server"
chmod 600 server.key
```

### 4.2 pg_hba 用 hostssl 强制加密

```conf
# only allow SSL-encrypted remote connections
hostssl all all 192.168.1.0/24 scram-sha-256
# optionally reject non-SSL explicitly
hostnossl all all 0.0.0.0/0 reject
```

### 4.3 客户端验证

```bash
# psql with SSL
psql "host=<ip> port=5432 dbname=postgres user=app_user sslmode=require"

# verify encryption in session
SELECT ssl, version FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

| 客户端参数 | 含义 |
|:-----------|:-----|
| `sslmode=require` | 必须加密，不验证证书 |
| `sslmode=verify-full` | 必须加密 + 校验证书主机名 |
| `sslmode=disable` | 不加密（禁用于生产） |

---

## 五、安全加固清单

| # | 项 | 建议 |
|:-:|:---|:-----|
| 1 | 强密码策略 | >16 位混合字符，禁用默认密码 |
| 2 | 认证方法 | scram-sha-256（PG14 默认） |
| 3 | IP 白名单 | 精确到 `/32` 或业务网段 `/24` |
| 4 | 传输加密 | hostssl + sslmode=require |
| 5 | 最小权限账号 | 远程账号只授所需库/表 |
| 6 | 版本更新 | 保持 PG 最新稳定版（安全补丁） |
| 7 | 连接审计 | pg_stat_activity 定期查异常来源 |
| 8 | 端口收敛 | 非 5432 降低扫描暴露 |

### 加固检查 SQL

```sql
-- active connections by client IP
SELECT client_addr, count(*) AS conns
FROM pg_stat_activity
GROUP BY client_addr ORDER BY conns DESC;

-- accounts with weak encryption
SELECT rolname, rolpassword LIKE 'SCRAM%' AS is_scram
FROM pg_authid WHERE rolcanlogin;
```

---

## 六、生产环境禁忌

| ❌ 禁忌 | 风险 | ✅ 替代 |
|:--------|:-----|:--------|
| `0.0.0.0/0 trust` | 无密码公网裸奔 | 网段限定 + scram-sha-256 |
| `password` 明文认证 | 密码被窃听 | scram-sha-256 |
| 不开 SSL | 数据明文传输 | hostssl + sslmode=require |
| 弱密码/默认密码 | 秒破 | 强密码 + 定期轮换 |
| 直接暴露 5432 到公网 | 攻击面巨大 | VPN/跳板机/云数据库 |

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 只限 IP 不开 SSL | 流量明文可窃听 | 三层都要 |
| 2 | SSL 证书权限错误 | 服务启动失败 | chmod 600 server.key |
| 3 | sslmode 不配 | 客户端未强制加密 | 客户端 sslmode=require |
| 4 | 强密码但认证弱 | md5 可被离线破解 | 升级 scram-sha-256 |
| 5 | 防火墙限了本机没限云 | 云安全组未同步 | 双层检查 |
| 6 | 审计只看本机 | 漏云侧连接日志 | 云安全组日志 + pg_stat_activity |

### 最佳实践

1. **三层同步加固**：IP + 密码 + SSL 一次性配齐，不留短板
2. **证书管理**：生产用可信 CA 证书，客户端 verify-full
3. **基线文档化**：远程访问配置写入部署文档，新实例照抄
4. **定期安全巡检**：查弱加密账号、异常来源、证书过期
5. **最小暴露原则**：能内网就不公网，能 VPN 就不直连

---

## 相关文档

- [允许 IP 远程访问](2026-08-15-postgres-ip-remote-access.md) — 四步链路实操
- [cpolar 内网穿透](2026-08-15-postgres-cpolar-tunnel.md) — 无公网 IP 方案
- [客户端认证 pg_hba.conf](2026-08-15-postgres-hba-auth.md) — hostssl 与认证谱系
- [权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) — 账号最小权限

---

## 参考来源

- 腾讯云开发者社区：远程连接 PostgreSQL：配置指南与安全建议
- [PostgreSQL 官方文档：SSL 支持](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [PostgreSQL 官方文档：客户端认证](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
- [PostgreSQL 官方文档：密码认证](https://www.postgresql.org/docs/current/auth-password.html)

---

## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 安全层级 | 3 层 | 网络 + 认证 + 传输 |
| 强密码长度 | ≥16 位 | 混合字符防爆破 |
| SSL 证书有效期 | 365 天 | 自签证书示例（生产用 CA） |
| 缓存命中率基线 | ≥99% | OLTP 健康阈值（监控参考） |

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（三层安全模型 + SSL 配置 + 加固清单 + 生产禁忌 + 6 易错点）
