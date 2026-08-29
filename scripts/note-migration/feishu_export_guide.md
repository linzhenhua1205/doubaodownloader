# 飞书知识库导出指南

> 飞书个人空间知识库 → Markdown 迁移。两种路径：API（推荐，可自动化）/ 手动导出。

---

## 方案 A：开放平台 API（推荐）

### 前提
- 飞书开放平台（open.feishu.cn）创建企业自建应用
- 开通权限：`wiki:wiki:readonly`（知识库）、`docs:doc:readonly`、`drive:drive:readonly`
- 获取 app_id / app_secret → tenant_access_token

### 导出流程（参考脚本）

```python
# 伪代码: 用 requests 调飞书 API 递归导出
# 1. 获取知识空间列表
GET https://open.feishu.cn/open-apis/wiki/v2/spaces
# 2. 获取空间下节点树
GET https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes
# 3. 获取节点内容 (docx 内容块)
GET https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}
# 4. 把内容块渲染为 Markdown (标题/段落/表格/列表/代码块映射)
```

### 渲染映射参考

| 飞书块类型 | Markdown |
|:-----------|:---------|
| heading1-9 | # ~ ###### |
| paragraph | 段落 |
| bullet_list_item | - 列表 |
| ordered_list_item | 1. 列表 |
| table | Markdown 表格 |
| code_block | ```代码块``` |
| image | ![alt](URL)（图片 URL 化，不下载） |
| file | 链接（附件清单） |

### 注意
- 个人空间知识库需要应用有权限（把应用加为空间成员）
- 分页拉取（page_token）；限流（QPS 约束）需加退避重试
- 图片保留 URL（web 链接），不下载本地

## 方案 B：手动导出（无 API 权限时）

1. 飞书 Web/客户端 → 打开知识库
2. 每篇文档：右上角 `...` → 下载为 → **Markdown**（飞书已支持导出 .md）
3. 目录结构按知识库层级手动建立
4. 附件/图片：下载为时选择包含资源

> 飞书新版客户端支持「下载为 Markdown + 图片资源」，批量时逐篇操作即可。

## 迁移后映射

飞书知识库目录结构 → knowledge/ 模块（示例）：

| 飞书目录 | knowledge/ 目标 |
|:---------|:----------------|
| 服务器技术 | 02_rd/ 对应子目录 |
| AI 调研 | 07_industry-research/ |
| 个人管理 | 04_person/ |
| 工具方法 | 05_tools/ |

## 质量检查

- [ ] 目录结构完整保留（缺失的建 README 说明）
- [ ] 图片为 web 链接
- [ ] 附件清单已生成
- [ ] frontmatter 已补（source: feishu）
