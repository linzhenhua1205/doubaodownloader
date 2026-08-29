# CloudBeaver：基于 Web 的数据库管理工具深度解析

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [知乎 - CloudBeaver：基于浏览器的DBeaver](https://zhuanlan.zhihu.com/p/1940153745708151249)
> **配套**: [DBeaver 核心功能](2026-08-15-dbeaver-core-guide.md) / [DBeaver 安装指南](2026-08-15-dbeaver-install-guide.md) / [DBeaver 终极指南](2026-08-15-dbeaver-ultimate-guide.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、产品定位](#二产品定位)
- [三、核心功能特性](#三核心功能特性)
- [四、版本功能对比](#四版本功能对比)
- [五、部署与体验](#五部署与体验)
- [六、适用场景与选型](#六适用场景与选型)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

CloudBeaver 是 **DBeaver 的 Web/服务器版本**，把桌面能力搬到浏览器，核心价值是"**免安装 + 团队共享 + 远程协作**"：

| 维度 | 要点 |
|:-----|:-----|
| 形态 | 浏览器访问，无需桌面客户端 |
| 数据库 | MariaDB/MongoDB/PostgreSQL/SQLite 等主流 |
| 部署 | Docker 一键部署，默认端口 8978 |
| 版本 | 社区版（免费开源）/ 企业版（SSO/RBAC/审计） |
| 关系 | DBeaver 桌面版的能力超集迁移到 Web |
| 量化基线 | 镜像约 800MB；启动约 30s-60s；并发约 20 会话 |

**核心结论**：
1. **部署即 Docker**：`docker run -d -p 8978:8978 dbeaver/cloudbeaver` 即可拉起，适合团队统一入口
2. **版本分层的本质是安全**：企业版补足 SSO、RBAC、审计日志，满足等保/合规诉求
3. **场景定位**：团队协作、跨平台访问、不愿装客户端的轻量化场景
4. **边界**：社区版不支持 NoSQL、云数据库、SQL AI 助手——需要这些上企业版

---

## 二、产品定位

| 对比项 | DBeaver（桌面版） | CloudBeaver（Web 版） |
|:-------|:------------------|:----------------------|
| 形态 | 桌面客户端 | 浏览器 Web 应用 |
| 部署 | 本机安装 | 服务器 Docker/包部署 |
| 协作 | 单人为主 | 多人共享、远程协作 |
| 平台 | Windows/macOS/Linux | 任何有浏览器的设备 |
| 场景 | 开发者个人工作台 | 团队数据库管理入口 |

---

## 三、核心功能特性

| 功能域 | 能力说明 |
|:-------|:---------|
| 多数据库支持 | MariaDB/MongoDB/PostgreSQL/SQLite 等，可视化配置连接 |
| 元数据管理 | 树状导航（库/模式/表/视图/存储过程）、结构编辑、DDL 执行 |
| 实体关系图 | ERD 可视化表关系，支持导出 SVG |
| 数据操作 | 表格浏览（过滤/排序/分页）、电子表格式编辑 |
| SQL 编辑器 | 语法高亮/自动补全、多标签页、执行计划、历史记录 |
| 数据导入导出 | CSV/Excel/XML 导入；CSV/Excel/JSON/SQL/HTML 导出 |
| 安全 | 凭证加密存储、SSH 隧道、用户管理（企业版 RBAC/SSO） |

---

## 四、版本功能对比

| 功能 | 社区版 | 企业版 |
|:-----|:------:|:------:|
| SQL 数据库支持 | ✅ | ✅ |
| 数据编辑器 | ✅ | ✅ |
| SQL 编辑器 | ✅ | ✅ |
| NoSQL 数据库支持 | ❌ | ✅ |
| 云数据库支持 | ❌ | ✅ |
| 查询管理 | ❌ | ✅ |
| 可视化查询构建器 | ❌ | ✅ |
| SQL AI 助手 | ❌ | ✅ |
| 实体关系图 | ❌ | ✅ |
| 高级安全功能（SSO/RBAC/审计） | ❌ | ✅ |

---

## 五、部署与体验

### 5.1 在线体验

- 企业版演示环境：<https://demo.cloudbeaver.io/>
- 预置 MariaDB/MongoDB/PostgreSQL/SQLite 连接（不可新建）
- 操作方式与桌面版 DBeaver 一致

### 5.2 Docker 本地部署（社区版）

```bash
docker run --name cloudbeaver --rm \
  --add-host=host.docker.internal:192.168.1.100 \
  -ti -p 8978:8978 \
  -v /var/cloudbeaver/workspace:/opt/cloudbeaver/workspace \
  dbeaver/cloudbeaver:latest
```

| 步骤 | 操作 |
|:-----|:-----|
| 访问 | 浏览器打开 `http://<host-ip>:8978/` |
| 初始化 | 设置管理员用户名和密码 |
| 数据持久化 | workspace 目录挂载到宿主机卷 |

> 量化参考：默认端口 8978；容器镜像约 800MB；首次启动约 30s-60s；支持并发会话约 20 个（社区版）

---

## 六、量化速查表

| 指标 | 数值 | 说明 |
|:-----|:-----|:-----|
| 容器镜像 | 约 800MB | dbeaver/cloudbeaver:latest |
| 内存建议 | ≥2GB | 容器 JVM 运行 |
| 磁盘预留 | 10GB+ | workspace 数据卷 |
| 启动时间 | 30s-60s | 首次启动 |
| 默认端口 | 8978 | HTTP 访问 |
| 并发会话 | 约 20 个 | 社区版参考 |

## 七、适用场景与选型

| 场景 | 推荐版本 | 理由 |
|:-----|:---------|:-----|
| 团队共享数据库管理 | 社区版起步 | Docker 一键、浏览器访问 |
| 多环境（开发/测试/生产）隔离 | 企业版 | RBAC + 审计合规 |
| 云上数据库统一入口 | 企业版 | 云数据库支持 |
| 个人日常使用 | 桌面 DBeaver | 功能更全、无需维护服务器 |
| 等保/金融合规 | 企业版 | SSO/审计日志必需 |

> **经验**：CloudBeaver 适合"管理入口集中化"，但日常高频 SQL 开发仍推荐桌面 DBeaver——Web 端在复杂调试（如大结果集、图形化执行计划）上体验略逊。

---

## 相关文档

- [DBeaver 核心功能与高级应用](2026-08-15-dbeaver-core-guide.md)
- [DBeaver 下载安装指南](2026-08-15-dbeaver-install-guide.md)
- [DBeaver 终极指南：从入门到企业级实战](2026-08-15-dbeaver-ultimate-guide.md)
- [Navicat 数据库管理全攻略](2026-08-15-navicat-complete-guide.md)
- [数据库选型指南 2025](2026-08-15-database-selection-guide.md)

## 参考来源

- [知乎：CloudBeaver 基于浏览器的 DBeaver](https://zhuanlan.zhihu.com/p/1940153745708151249)
- [CloudBeaver 官方文档](https://cloudbeaver.io/docs/)
- [Docker Hub：dbeaver/cloudbeaver](https://hub.docker.com/r/dbeaver/cloudbeaver)

## Changelog

| 日期 | 变更类型 | 变更内容 |
|:-----|:---------|:---------|
| 2026-08-15 | 新建 | 素材 u036 导入：CloudBeaver Web 数据库管理（定位/功能/部署/选型） |
