# Dify 通过 MCP 协议连接 MySQL 实现数据库查询

> **类型**: knowledge | **日期**: 2026-08-15 | **版本**: v1.0
> **来源**: [掘金 - Dify+MCP 组合拳：根治 Excel 上传知识库回答数据不准的难题](https://juejin.cn/post/7496033842748440626)（2025-10-27）
> **配套**: [Dify 知识库调优](2026-08-15-dify-kb-tuning.md) / [Dify 版本演进 1.9.1-1.10.1](2026-08-15-dify-1.9.1-1.10.1-update.md) / [Dify 平台概览](2026-06-29-dify-platform-overview.md) / [RAG 工具选型](../../03_AI/llm-techniques-principles/2026-08-15-rag-tools-selection.md)

---

## 📑 目录

- [一、结论概要](#一结论概要)
- [二、核心问题：向量知识库的结构化数据短板](#二核心问题向量知识库的结构化数据短板)
- [三、MCP + 数据库架构](#三mcp--数据库架构)
- [四、实施步骤（MySQL 8.4 + Dify）](#四实施步骤mysql-84--dify)
- [五、测试效果与日志追踪](#五测试效果与日志追踪)
- [六、技术对比与最佳实践](#六技术对比与最佳实践)
- [七、安全与生产建议](#七安全与生产建议)
- [相关文档](#相关文档)
- [参考来源](#参考来源)
- [Changelog](#changelog)

---

## 一、结论概要

Dify 对接数据库的**推荐路径是 MCP（Model Context Protocol）**：让 AI 将自然语言转为 SQL，经 MCP Server 执行查询，精准解决传统向量知识库对结构化数据（Excel/表格）查询精度不足的问题。

| 维度 | 要点 |
|:-----|:-----|
| 问题 | 向量检索本质是相似度匹配，30 条结构化数据仅检索到 3 条，统计类问题答不准 |
| 方案 | Dify Agent 节点 → MCP SSE → mysql-mcp-server-sse → MySQL 8.4 |
| 架构 | 用户自然语言 → AI 转 SQL → MCP 执行 → 结果回传 AI 组织答案 |
| 关键配置 | MCP 服务地址 `http://host.docker.internal:3000/sse`，MySQL 默认 3306 端口 |
| 最佳实践 | 非结构化文本走 RAG，结构化数据走 MCP+DB，两者互补而非替代 |

**核心结论**：
1. **结构化数据查询是向量知识库的天然短板**：统计/筛选类问题（"共有多少条""库存低于多少"）依赖精确计算，相似度检索无能为力
2. **MCP 是标准化的数据库接入协议**：一次配置，Dify 内即可通过工具列表自动发现数据库能力
3. **代价是 Token 消耗**：大表查询结果回传占用上下文，需限定返回行数与字段

---

## 二、核心问题：向量知识库的结构化数据短板

### 2.1 失效场景

典型失败案例：将含 30 条记录的 Excel（水果表）上传 Dify 知识库，询问"表中共有多少条数据"：
- 向量检索按语义相似度召回，**只命中 3 条片段**，无法完成 COUNT 统计
- 答案依赖 LLM 对局部片段的推断，出现"张冠李戴"式错误

### 2.2 根因分析

| 环节 | 向量知识库 | 数据库直查 |
|:-----|:-----------|:-----------|
| 匹配机制 | 语义相似度（近似匹配） | SQL 精确执行（确定性） |
| 统计聚合 | 不支持 | COUNT/SUM/GROUP BY 原生支持 |
| 数据一致性 | 快照时点 | 实时 |
| 更新成本 | 需重新切片+embedding | 零（直接查库） |

**第一性原理**：RAG 解决的是"语义召回"问题，而结构化查询本质是"确定性计算"问题——用近似检索做精确计算，误差是结构性的。

---

## 三、MCP + 数据库架构

```
user(NL query) -> AI Model(to SQL) -> MCP Server(exec) -> MySQL DB
                                    ^                          |
                                    +---------- result back <-+
```

| 组件 | 职责 | 实现 |
|:-----|:-----|:-----|
| Dify Agent 策略节点 | 工具编排 + 提示词约束表结构 | MCP Agent 策略插件 |
| MCP 工具 | 获取工具列表 / 调用工具 | MCP SSE 插件 |
| MCP Server | 接收 SQL、执行查询、返回结果 | mysql-mcp-server-sse（GitHub） |
| 数据库 | 数据存储与计算 | MySQL 8.4.5 |

---

## 四、实施步骤（MySQL 8.4 + Dify）

### 4.1 MySQL 环境

1. 安装 MySQL 8.4.5（本文用一键安装包），默认账号 `root/123456`，端口 `3306`
2. 用 Navicat 验证连接成功
3. 新建数据库 `test`（字符集 `utf8mb4`），导入测试数据生成 `fruits` 表（字段：id/name/price/stock/origin）

### 4.2 MCP Server 部署

```bash
uv init            # init project
uv venv            # create virtual env
uv pip install -r requirements.txt   # install deps
```

配置 `.env`：

```ini
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=test
```

启动服务：`uv run -m src.server`（默认监听 3000 端口）

### 4.3 Dify 工作流配置

1. **安装插件**：MCP Agent 策略、MCP SSE
2. **Agent 策略节点**：
   - 工具选择：`获取MCP工具列表` + `调用MCP工具`
   - MCP 服务地址：`http://host.docker.internal:3000/sse`（Docker 内访问宿主机）
   - 提示词：声明 fruits 表结构（字段名+类型），约束 AI 只生成 SELECT 查询
3. **直接回复节点**：接收 AI 组织的自然语言答案

---

## 五、测试效果与日志追踪

| 测试项 | 结果 |
|:-----|:-----|
| 提问"表中共有多少条数据" | AI 生成 `SELECT COUNT(*) FROM fruits`，返回正确数值 |
| 服务端日志 | 显示 SQL 执行过程、耗时（<100ms 级）与返回行数 |
| 工作流追踪 | Dify 后台可查看完整调用链路 |

**调试要点**：
- 查询失败先看 MCP Server 日志（SQL 是否生成正确）
- Dify 容器内必须用 `host.docker.internal` 而非 `127.0.0.1` 访问宿主机服务
- 提示词中给出表结构可显著降低 AI 生成错误 SQL 的概率

---

## 六、技术对比与最佳实践

| 技术方案 | 优势 | 劣势 |
|:-----|:-----|:-----|
| 传统 RAG 知识库 | 适合非结构化文本检索，部署简单 | 结构化数据查询精度低（召回率 ~10%） |
| MCP + 数据库 | 统计查询 100% 精确，数据实时 | 大结果集消耗 Token，需限流 |

**最佳实践（分层策略）**：
1. 非结构化文档（PDF/手册）→ 向量知识库
2. 结构化数据（业务表/Excel）→ MCP + 数据库
3. 混合问题 → 先查库取事实，再用知识库补上下文

---

## 七、安全与生产建议

| 风险 | 缓解措施 |
|:-----|:-----|
| AI 生成 DROP/UPDATE 等危险 SQL | 提示词强制只读；DB 账号最小权限（仅 SELECT） |
| 敏感数据泄露 | 按用户角色过滤列/行级权限 |
| 查询超时/拖垮数据库 | 设置 statement_timeout（如 10s）、LIMIT 行数上限 |
| Token 爆炸 | 限制返回字段、分页查询、结果摘要化 |

**生产级建议**：MCP Server 与应用 DB 分离，走内网 + 独立只读账号，禁止 root 直连。

---

## 相关文档

- [Dify 知识库调优指南（分段/索引/检索）](2026-08-15-dify-kb-tuning.md)
- [Dify v1.9.1-v1.10.1 版本更新解析（多数据库+事件驱动）](2026-08-15-dify-1.9.1-1.10.1-update.md)
- [Dify 平台概览与定位](2026-06-29-dify-platform-overview.md)
- [PostgreSQL 表操作与数据操作全指南](../database/2026-08-15-postgres-table-dml-guide.md)
- [PostgreSQL 远程访问配置](../database/2026-08-15-postgres-ip-remote-access.md)

---

## 参考来源

- [掘金 - Dify+MCP 组合拳](https://juejin.cn/post/7496033842748440626)（2025-10-27）
- [mysql-mcp-server-sse GitHub](https://github.com/mangooer/mysql-mcp-server-sse)
- [MySQL 官方文档](https://dev.mysql.com/doc/)

---

## Changelog

| 日期 | 变更类型 | 变更内容 |
|:-----|:---------|:---------|
| 2026-08-15 | 新建 | 由 u047 素材导入，提炼 MCP+MySQL 架构与实施步骤 |
