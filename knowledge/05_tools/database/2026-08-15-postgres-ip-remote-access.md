# PostgreSQL 允许 IP 远程访问的配置步骤## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 默认端口 | 5432（TCP） | PostgreSQL 监听端口 |
| 配置步骤 | 4 步（100% 需双文件） | 监听 + pg_hba + 重启 + 防火墙 |
| 安全网段 | 192.168.1.0/24（≈254 主机） | 最小授权网段 |
| 防火墙 | TCP+UDP 双协议（100% 放行） | Windows 需两条规则 |
| 配置生效 | reload < 1s / 重启 < 30s | pg_hba 热加载 vs listen 重启 |

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、远程访问四步链路](#二远程访问四步链路)
- [三、配置文件详解](#三配置文件详解)
- [四、防火墙放行](#四防火墙放行)
- [五、连接测试与验证](#五连接测试与验证)
- [六、安全实践](#六安全实践)
- [七、易错点与最佳实践](#七易错点与最佳实践)
- [量化速查](#量化速查)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 默认**只监听本机（localhost）**，开放远程访问需走通 **双文件 + 一服务 + 一防火墙** 四步链路：

| 步骤 | 对象 | 动作 |
|:-----|:-----|:-----|
| 1 | `postgresql.conf` | `listen_addresses = '*'`（监听所有网卡） |
| 2 | `pg_hba.conf` | 添加 `host` 规则（允许指定网段+认证） |
| 3 | 服务 | 重启或 reload 生效 |
| 4 | 防火墙 | 放行 TCP 5432 端口 |

**核心结论**：
1. **双文件缺一不可**：`listen_addresses` 决定"听不听"，`pg_hba.conf` 决定"放不放"，只改一个都会连不上
2. **安全三原则**：禁 `0.0.0.0/0 trust`、限特定网段（如 `/24`）、用 scram-sha-256/md5 认证
3. **重启 vs reload**：改 `listen_addresses` 需重启；改 `pg_hba.conf` 可 `pg_reload_conf()` 热加载
4. **防火墙是第四道门**：云服务器（安全组）+ 本机防火墙都要放行

---

## 二、远程访问四步链路

### 2.1 链路图

| 环节 | 配置 | 作用 |
|:-----|:-----|:-----|
| 监听层 | listen_addresses | 服务端监听哪些网卡 |
| 认证层 | pg_hba.conf host 规则 | 允许哪些 IP/网段 + 认证方式 |
| 服务层 | 重启/reload | 让配置生效 |
| 网络层 | 防火墙放行 | OS/云安全组放行 5432 |

任何一环缺失 → `Connection refused` 或 `no pg_hba.conf entry` 报错。

### 2.2 判断报错指向

| 报错 | 故障层 |
|:-----|:-------|
| `Connection refused` | 服务没起 / 监听地址错 / 防火墙拦 |
| `no pg_hba.conf entry for host` | pg_hba 规则缺失或顺序问题 |
| `password authentication failed` | 认证方法/密码问题 |

---

## 三、配置文件详解

### 3.1 postgresql.conf：修改监听地址

```conf
# default: only loopback
# listen_addresses = 'localhost'

# listen on all interfaces
listen_addresses = '*'

# or specific IPs (safer)
# listen_addresses = '192.168.1.10,127.0.0.1'
```

- `'*'` 监听所有网卡；指定 IP 列表更安全（只监听需要的网卡）
- 修改后**必须重启**：`sudo systemctl restart postgresql`

### 3.2 pg_hba.conf：添加远程规则

```conf
# TYPE  DATABASE  USER  ADDRESS           METHOD
host    all       all   127.0.0.1/32      scram-sha-256
host    all       all   192.168.1.0/24    scram-sha-256
```

- `host all all 192.168.1.0/24 md5`：允许该网段用密码连接
- 生产禁用 `0.0.0.0/0`（全开放），必须限定网段
- 修改后热加载：`SELECT pg_reload_conf();`

### 3.3 最小修改示例（局域网场景，u020 并入）

```conf
# IPv4 local connections:
host    all    all    127.0.0.1/32    scram-sha-256
host    all    all    192.168.1.0/24  scram-sha-256
```

---

## 四、防火墙放行

### 4.1 Linux（firewalld / iptables）

```bash
# firewalld
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
```

### 4.2 Windows Defender 防火墙

1. 高级设置 → 入站规则 → 新建规则
2. 规则类型选"端口" → 特定本地端口填 `5432`
3. 分别新建 **TCP 和 UDP** 两条规则（u020 经验）
4. 允许连接 → 应用到全部配置文件 → 命名保存

### 4.3 云服务器安全组

- 阿里云/腾讯云/AWS 需在**安全组**额外放行 5432 入方向
- 建议来源限定为你的办公 IP（如 `x.x.x.x/32`），而非 `0.0.0.0/0`

---

## 五、连接测试与验证

### 5.1 命令行测试

```bash
# from remote machine
psql -h <server-ip> -U <username> -d <database> -p 5432
```

### 5.2 可视化工具

- **pgAdmin 4**：添加新服务器 → 输入 IP + 端口 5432 + 用户名密码
- **Navicat / DBeaver**：同参数，确认 SSL 选项

### 5.3 服务端确认

```sql
-- check listening addresses
SHOW listen_addresses;

-- check active connections (remote clients)
SELECT client_addr, state FROM pg_stat_activity
WHERE client_addr IS NOT NULL;
```

---

## 六、安全实践

| 原则 | 实现 |
|:-----|:-----|
| 最小网段 | 只开放业务网段，不用 `0.0.0.0/0` |
| 强认证 | scram-sha-256（PG14 默认）> md5 |
| 传输加密 | 启用 SSL，pg_hba 用 hostssl 规则 |
| 端口收敛 | 非默认端口 5432 可降低扫描暴露 |
| 防火墙白名单 | 来源 IP 精确到 `/32` |
| 最小权限账号 | 远程账号只授所需库/表权限 |

---

## 七、易错点与最佳实践

### 易错点

| # | 场景 | 坑 | 对策 |
|:-:|:-----|:---|:-----|
| 1 | 只改 pg_hba 不改监听 | 远程 `Connection refused` | 双文件一起改 |
| 2 | 改监听不重启 | 配置不生效 | 重启服务 |
| 3 | 防火墙漏放行 | 云安全组/本机防火墙双道 | 两层都查 |
| 4 | 用 0.0.0.0/0 trust | 公网裸奔 | 限定网段 + 认证 |
| 5 | 只放 TCP 不放 UDP | Windows 下连接异常 | TCP+UDP 都放（u020） |
| 6 | 忽略 reload 与重启区别 | 以为都热生效 | 区分参数类型 |

### 最佳实践

1. **配置模板化**：把四步写进部署脚本/文档，新实例一键复制
2. **安全基线**：远程访问一律 hostssl + scram-sha-256 + 网段限定
3. **白名单动态管理**：办公 IP 变化时只改安全组/pg_hba 一处
4. **连接监控**：`pg_stat_activity.client_addr` 定期检查异常来源
5. **生产禁开公网**：优先 VPN/跳板机/内网穿透，避免直接暴露 5432

---

## 相关文档

- [远程连接配置与安全指南](2026-08-15-postgres-remote-access-security.md) — SSL 加密与三重防护
- [cpolar 内网穿透](2026-08-15-postgres-cpolar-tunnel.md) — 无公网 IP 的远程方案
- [客户端认证 pg_hba.conf](2026-08-15-postgres-hba-auth.md) — host 规则与认证谱系
- [权限配置与验证](2026-08-15-postgres-privilege-config-verify.md) — 连接后的授权层

---

## 参考来源

- 博客园：允许 IP 远程访问 PostgreSQL（Verite）
- 博客园：PostgreSQL 局域网访问配置（Fooo，u020 并入）
- [PostgreSQL 官方文档：连接设置](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [PostgreSQL 官方文档：客户端认证](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)

---

## 量化速查

| 维度 | 量化值 | 说明 |
|:-----|:-------|:-----|
| 默认端口 | 5432 | PostgreSQL 监听端口（TCP） |
| 配置步骤 | 4 步 | 监听 + pg_hba + 重启 + 防火墙 |
| 安全网段 | 192.168.1.0/24 | 建议最小授权网段（替代 0.0.0.0/0） |
| 防火墙规则 | TCP+UDP 双协议 | Windows 下需都放行（u020 经验） |

---

## Changelog

- 2026-08-15 v1.0: 首次深度加工（四步链路 + 双文件详解 + 防火墙三平台 + 报错定位 + 安全六原则 + 6 易错点；u020 局域网并入）
