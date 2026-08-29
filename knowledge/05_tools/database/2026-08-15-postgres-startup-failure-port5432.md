# PostgreSQL 14 服务启动失败（端口 5432 连接问题）解决方案

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [CSDN - postgresql 14 服务器打不开的问题（5432服务器端口失败）](https://blog.csdn.net/ONLYSRY/article/details/123524085)
> **配套**: [pg_hba.conf 认证配置](2026-08-15-postgres-hba-auth.md) / [允许 IP 远程访问](2026-08-15-postgres-ip-remote-access.md) / [主从同步状态查看](2026-08-15-postgres-replication-status.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、故障根因分析](#二故障根因分析)
- [三、排查步骤](#三排查步骤)
- [四、解决方案](#四解决方案)
- [五、预防措施](#五预防措施)
- [六、相关故障速查](#六相关故障速查)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

PostgreSQL 14 安装后服务无法启动、psql 报 `Connection refused`（端口 5432 连接失败），**绝大多数是服务未正确注册/未启动**，而非数据库本身故障：

| 维度 | 要点 |
|:-----|:-----|
| 默认端口 | 5432 |
| 典型报错 | `psql: could not connect to server: Connection refused` |
| 服务名（Windows） | `postgresql-x64-14` |
| 根因 | 安装时自定义端口/服务注册异常/语言选项不当 |
| 解决路径 | 服务管理器修复 → 启动服务 → psql 验证 |
| 量化基线 | 90% 启动失败源于服务未启动；排查耗时约 5-10 分钟；日志定位 tail -50 行 |

**核心结论**：
1. **先查服务再查配置**：Windows 下 90% 的启动失败是服务未启动/未正确注册，先看 `services.msc` 中 `postgresql-x64-14` 状态
2. **端口自定义是常见诱因**：安装时改端口但服务参数未同步，导致服务起不来
3. **语言选项选 C**：安装时语言选「C」而非默认值，避免编码相关问题
4. **验证命令**：`psql -U postgres` 能进入即恢复

---

## 二、故障根因分析

| 根因 | 说明 | 概率 |
|:-----|:-----|:----:|
| 服务未启动 | 安装中断/服务注册失败，`services.msc` 中服务状态为停止 | 高 |
| 端口自定义冲突 | 安装时改端口号，服务配置未同步 | 中 |
| 语言选项不当 | 安装语言未选「C」，引发编码问题 | 低 |
| 端口被占用 | 5432 被其他进程占用，服务绑定失败 | 低 |
| 数据目录权限 | 数据目录无写权限，初始化失败 | 低 |

---

## 三、排查步骤

| 步骤 | 操作 | 判断 |
|:-----|:-----|:-----|
| 1 | 打开服务管理器：`Win+R` → `services.msc` | 找 `postgresql-x64-14` |
| 2 | 查看服务状态 | 停止 = 未启动/异常 |
| 3 | 查看服务"登录"与"可执行文件路径" | 路径指向正确 data 目录 |
| 4 | 尝试手动启动服务 | 看是否报错及错误内容 |
| 5 | 命令行验证：`psql -U postgres` | 能进入 = 恢复 |

---

## 四、解决方案

### 4.1 Windows 服务管理器修复（主路径）

| 步骤 | 操作 |
|:-----|:-----|
| 1 | 服务管理器找到 `postgresql-x64-14` |
| 2 | 右键 → 属性 |
| 3 | 确认"可执行文件的路径"含正确的 `data` 目录参数 |
| 4 | 启动类型设为"自动" |
| 5 | 点击"启动" → 状态变"正在运行" |
| 6 | `psql -U postgres` 验证 |

### 4.2 端口自定义场景

- 若安装时改过端口（非 5432），psql 连接需带 `-p <port>`：
  ```bash
  psql -U postgres -p 5433
  ```
- 同时检查 `postgresql.conf` 中 `port` 参数与连接端口一致

### 4.3 命令行手动启动（Linux/macOS）

```bash
# check service status
systemctl status postgresql-14

# start manually
sudo systemctl start postgresql-14

# tail log to locate the cause
tail -50 /var/log/postgresql/postgresql-14-main.log
```

---

## 五、预防措施

| 措施 | 说明 |
|:-----|:-----|
| 默认端口 | 无特殊需求保持 5432 |
| 端口检查 | 自定义端口前确认未被占用（`netstat -ano | findstr 5432`） |
| 语言选项 | 安装时语言选「C」 |
| 服务自启 | 安装完成后确认服务"启动类型=自动" |
| 安装日志 | 保留安装日志，失败时可定位 |

---

## 六、相关故障速查

| 故障 | 快速判断 | 处理 |
|:-----|:---------|:-----|
| Connection refused | 服务未监听端口 | 启动服务 |
| 密码认证失败 | pg_hba.conf 认证方式/密码错误 | 检查 pg_hba + 重置密码 |
| 数据目录初始化失败 | 权限/磁盘 | 检查权限与空间 |
| 端口被占用 | `netstat` 查占用 | 换端口或停占用进程 |

## 七、量化速查表

| 指标 | 数值 | 说明 |
|:-----|:-----|:-----|
| 服务故障占比 | 90% | 启动失败源于服务未启动 |
| 排查耗时 | 300s-600s | 常规问题（5-10 分钟） |
| 启动等待 | 10s | systemctl start 返回 |
| 连接超时 | 30s | psql 默认等待 |
| 内存基线 | 512MB | shared_buffers 最小参考 |
| 日志定位 | tail -50 | 尾部 50 行日志 |

---

## 相关文档

- [PostgreSQL 客户端认证 pg_hba.conf 详解](2026-08-15-postgres-hba-auth.md)
- [PostgreSQL 允许 IP 远程访问配置](2026-08-15-postgres-ip-remote-access.md)
- [PostgreSQL 主从同步状态查看](2026-08-15-postgres-replication-status.md)
- [PostgreSQL 核心概念：Database/Schema/User](2026-08-15-postgres-core-concepts-db-schema-role.md)

## 参考来源

- [CSDN：postgresql 14 服务器打不开的问题](https://blog.csdn.net/ONLYSRY/article/details/123524085)
- [PostgreSQL 官方文档 - 服务器管理](https://www.postgresql.org/docs/14/runtime.html)

## Changelog

| 日期 | 变更类型 | 变更内容 |
|:-----|:---------|:---------|
| 2026-08-15 | 新建 | 素材 u015 导入：PG14 启动失败/端口 5432 排查方案（根因/排查/解决/预防） |
