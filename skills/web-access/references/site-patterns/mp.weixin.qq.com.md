---
domain: mp.weixin.qq.com
aliases: [微信公众号, 微信文章, 公众号文章, 微信]
updated: 2026-08-12
---

# mp.weixin.qq.com — 微信公众号文章

## 平台特征

- **单篇公开文章**（`/s/...` 路径）无需登录即可抓取，但反爬严格：普通浏览器 UA 直连大概率命中「环境异常/完成验证」页（约 17KB）
- **反爬绕过两条已验证路径**（互补，非互斥）：
  1. **微信内置浏览器 UA + `chksm=0000000000000000` 参数 + 剥离 `poc_token`**（三要素，wechat-article-fetch skill，2026-08-06 实战验证）
  2. **curl_cffi 浏览器指纹模拟**（wechat-claw `read_wechat_article.py`，2026-08-12 本环境实测 200 + 完整正文 24652 字符）
- 公众号历史文章**全量提取**需微信公众平台（mp.weixin.qq.com 后台）登录凭证：`cookie` + `token`（URL 参数里的数字）
- 凭证**不具备持久性**（几小时内失效；变更 IP 后失效更快），世界上没有永久绕过扫码的方案

## 有效模式

## ① 单篇公开文章 — 纯文本正文（最快：curl_cffi 零依赖）

```bash
.venv-web/bin/python skills/web-access/scripts/wechat-claw/read_wechat_article.py "<article_url>"
# Output JSON: title / pub_time / author / content / source_url / logs
# Optional: --timeout / --max-retries / --retry-delay
```

## ①b 单篇公开文章 — 富元数据 + 错误诊断（Node wechat-extractor）

需封面/biz/sn/mid/文章类型，或精确错误诊断时使用（17 种错误码）。

```bash
node skills/web-access/scripts/wechat-extractor/cli.js "<URL>" --summary   # summary
node skills/web-access/scripts/wechat-extractor/cli.js "<URL>"             # full JSON
node skills/web-access/scripts/wechat-extractor/cli.js "<URL>" --md out.md # markdown
# Output: title/account(name/alias/biz/qrcode)/author/type(post|video|image|voice|text|repost)/cover/time/sn/mid
```

失败（`blocked_403`/`timeout`/`no_content`）时回退：

```bash
# ② wechat-article-fetch skill 3-key bypass (WeChat UA + chksm + strip poc_token)
.venv-web/bin/python scripts/tools/wechat-fetch.py --url "<URL>" --full
# ③ final CDP fallback (needs user browser login state)
```

## ② 公众号全量提取（需凭证，遵守云端红线）

```bash
# Cloud/server: NO auto-login! User must login mp.weixin.qq.com locally,
# then paste Cookie + token from browser devtools Network tab
.venv-web/bin/python skills/web-access/scripts/wechat-claw/crawler.py \
  --nickname "ACCOUNT_NAME" \
  --credentials '{"cookie":"...","token":"..."}' \
  [--max 10] [--since 2026-01-01] [--fakeid "MzI..."]
# Output: output/<ACCOUNT>_full_<TS>.json (title/url/pubtime/fulltext)
```

> `--nickname` 支持中文公众号名（如 `数字生命卡兹克`），直接传原名称即可。

- 本地个人电脑可自动弹窗扫码（`--headless` 仅截图二维码）
- **频率纪律**：单账号请求间隔默认 5s（已加固），老号数千篇任务勿高频，IP 可能被拦 24h

## 已知陷阱

- **已删除文章**：curl_cffi 仍返回 HTTP 200，但无 `#js_content` → 报 `no_content`，页面含「该内容已被发布者删除」——判定为文章失效，不是工具问题（2026-08-12 实测）
- **Node request 拿大页面**：wechat-extractor（Chrome 66 UA）对已删除文章可能拿到 2.28MB「空壳」页面（js_content 存在但内容异常）→ 报 1005 脚本解析失败而非 2005。此时回退 wechat-claw（curl_cffi 拿小错误页）确认状态（2026-08-12 实测）
- **`poc_token` 分享链接**：携带分享者 token 会触发更严格验证，三要素方案必须剥离；curl_cffi 方案本身带指纹模拟，对 poc_token 链接也可直接尝试
- **云端自动登录 = 封号**：机房 IP 风控极严，公众平台网页端登录权限可能被直接封禁；云服务器场景**必须**用户本地手工提取凭证注入
- **互动数据不可得**：阅读/点赞/评论数走手机客户端专属流量，外部抓取拿不到
- **正文为空但标题正常**：可能是验证页（`环境异常`）或反爬升级，按 ①→②→③ 回退链处理并更新本文件

## 与现有体系分工

| 路径 | 适用 | 依赖 |
|:-----|:-----|:-----|
| wechat-article-fetch skill（wechat-fetch.py） | 单篇 + web-archive 自动归档集成 | requests + bs4（`.venv-web`） |
| **wechat-claw read_wechat_article.py** | 单篇，curl_cffi 指纹直连，纯文本最快 | curl_cffi（已装） |
| **wechat-extractor cli.js** | 单篇富元数据（封面/biz/sn/mid/类型/17 错误码），Node 解析 | npm 依赖（cheerio/dayjs/request-promise/qs，已装） |
| wechat-claw crawler.py | 公众号全量（需凭证） | wechatarticles + playwright（⚠️ 2026-08-12 起默认禁用，需 `export WECHAT_PLAYWRIGHT_ENABLED=1` 启用；凭证改手工注入） |
