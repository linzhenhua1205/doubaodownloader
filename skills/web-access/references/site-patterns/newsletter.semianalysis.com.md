---
domain: semianalysis.com
aliases: [SemiAnalysis, semianalysis, newsletter.semianalysis.com]
updated: 2026-08-14
---

## 平台特征
- **主站 semianalysis.com 是 WordPress**（wp-json API 可用，`x-nananana: Batcache-Hit` / `host-header: wpcloud`），**2025-09-16 起停更**（最新文章 xAI Colossus 2），wp-json `/wp/v2/posts` 只能拿到 2025-09 及以前。
- **内容已迁移到 Substack**：`newsletter.semianalysis.com`（`x-sub: semianalysis`，Cloudflare + Express + substackcdn）。
- 文章**全部付费墙**（`audience: only_paid`），公开可见标题/副标题/摘要/日期/字数/封面。
- **2025-12-04 至 2026-06-03 停更 6 个月**，恢复后频率加快（~9 篇/月，2026-06-03 起）。
- 页面内提及机构产品入口：Institutional Login 走 newsletter.semianalysis.com（非主站）。

## 有效模式
- **首选：Substack Archive API**（无需认证，返回 JSON，含全部元数据）：
  `https://newsletter.semianalysis.com/api/v1/archive?sort=new&offset={n}&limit=50`
  - 关键字段：`title` / `subtitle`（主题摘要）/ `post_date` / `audience`（everyone|members|only_paid）/ `canonical_url` / `wordcount` / `description` / `slug` / `type`（newsletter|post）
  - 分页：offset 步进 50；**当批次最后一条日期早于截止日期即可停止**（本 publication 全量仅 73 篇，offset=0 返回最新 23 篇后该页即结束，属正常——文章总数 < limit 时返回实际数）
  - 示例（2026-08-14 实测）：近半年（2026-02-14 起）23 篇，全 only_paid
- RSS：`https://newsletter.semianalysis.com/feed`（200，适合轻量订阅）；主站 `/rss`、`/feed` 200 但内容陈旧
- 链接验证：`canonical_url` 均为 `https://newsletter.semianalysis.com/p/{slug}`，2026-08-14 实测 23/23 返回 200（付费墙页面本身可访问）

## 已知陷阱
- **不要用主站 WordPress 数据判断"最新动态"**——主站 2025-09-16 已停更，会得出错误结论（2026-08-14 实测踩坑）
- archive API 返回的 `body_html` / `body_json` 字段对付费文章为空壳（仅付费可见内容预览），不要尝试从中提取正文
- 免费未订阅状态下 `audience=only_paid` 文章正文不可获取；如需正文须用户浏览器登录态（CDP）兜底，但违反付费墙的抓取需谨慎（尊重订阅制度）
- 抓取间隔建议 ≥0.5s/请求，批量时用并发但别超过 8 并发（Substack 无强反爬，但保持克制）
