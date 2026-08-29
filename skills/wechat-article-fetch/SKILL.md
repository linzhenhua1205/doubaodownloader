---
name: wechat-article-fetch
description: "微信公众号文章抓取与解析。当用户分享 mp.weixin.qq.com 链接（含 poc_token 分享链接）需要读取/归档内容时使用。内置微信反爬绕过（微信UA + chksm参数 + 剥离poc_token），一条命令输出精简摘要/全文/JSON，避免把 3MB HTML 载入上下文浪费 token。也适用于 web-archive 主流程的微信自动绕过。| 微信公众号, mp.weixin.qq.com, 微信文章, 抓取微信, 微信反爬, 环境异常, 绕过验证"
metadata:
  bins: ["python3", ".venv-web/bin/python"]
---

# WeChat Article Fetch — 微信公众号文章抓取 skill

## 何时触发
- 用户分享 `mp.weixin.qq.com/s?...` 链接（**含 poc_token 分享链接**）需要读取内容
- 用户要求归档微信文章（与 web-archive 配合）
- 直接访问微信文章命中「环境异常/完成验证」反爬页

## 核心知识（2026-08-06 实战验证）

微信 mp.weixin.qq.com 反爬特征与绕过：

| 场景 | 结果 |
|:-----|:-----|
| 普通 Chrome UA 直连 | ❌ 17KB「环境异常」验证页 |
| playwright 浏览器渲染 | ❌ 同样命中验证 (Target crashed) |
| 微信内置浏览器 UA | ❌ 单独不够 |
| 微信 UA + `chksm=0000000000000000` 参数 | ✅ 3.2MB 完整页面 |
| URL **带 poc_token**（分享者 token） | ❌ 即使加 chksm 也命中验证页 |
| 剥离 poc_token + chksm + 微信 UA | ✅ 完整页面 |

**关键三要素（缺一不可）**：
1. 微信内置浏览器 UA（iPhone/Android MicroMessenger）
2. URL 追加 `chksm=0000000000000000`（scene=27 非必需）
3. **剥离 `poc_token` 参数**（分享链接携带，触发更严格验证）

## 快速使用

```bash
# ① 精简摘要 (标题/公众号/字数/图片数 + 正文预览 2500 字符) — 默认
.venv-web/bin/python scripts/tools/wechat-fetch.py --url "<微信URL>"

# ② 全文 markdown (去噪后, 结构保留) 打印
.venv-web/bin/python scripts/tools/wechat-fetch.py --url "<URL>" --full

# ③ 结构化 JSON 落盘 (供二次加工)
.venv-web/bin/python scripts/tools/wechat-fetch.py --url "<URL>" --json out.json

# ④ 全文 markdown 落盘
.venv-web/bin/python scripts/tools/wechat-fetch.py --url "<URL>" --md out.md

# ⑤ 完整归档 (走 web-archive 主流程, 含单同步) — 注意: 归档后仍需 kb-log-append.py 追加 log.md
.venv-web/bin/python scripts/tools/wechat-fetch.py --url "<URL>" --archive
```

## 与 web-archive 集成（自动绕过）

`scripts/tools/web-archive/lib/fetcher.py` 已内置微信特化逻辑：
- `fetch_html()` 对 mp.weixin.qq.com URL：普通 UA 直连失败 → 自动 `_fetch_wechat()`（微信 UA + chksm + 剥 poc_token）→ 仍失败才回退浏览器
- 因此 `web-archive.py --url <微信URL>` 直接可用，无需手动处理

```bash
# 直接归档 (web-archive v2.0 框架, 含批判分析/原理/市场机会)
.venv-web/bin/python scripts/tools/web-archive/web-archive.py --url "<微信URL>"
```

## 输出内容（wechat-fetch.py parse）

| 字段 | 说明 |
|:-----|:-----|
| title | `#activity-name`（h1） |
| account | `#js_name`（公众号名） |
| author | `#js_author_name`（兜底公众号名） |
| published | `#publish_time` 或 JS 变量 createTime/ct（unix 秒）——**部分文章不暴露，可为空** |
| blocks | 正文块（h1-h6/p/li/section），已去重（li 嵌套 p 导致 double） |
| images | 9 张左右 web 链接（`data-src`，过滤 1px/表情图） |
| full_text | 拼接后的纯文本 |

## 注意事项
- 发布时间字段可能为空（该文章 HTML 未暴露），归档时人工补或留空
- 微信图片 URL 为 `mmbiz.qpic.cn`，直接可访问（无需登录）
- 若脚本仍失败（反爬升级）：fallback 链 = requests 微信UA > 浏览器渲染 > 搜狗微信搜索定位 > 人工复制
- 独立脚本依赖 requests + beautifulsoup4（`.venv-web` 已具备）

## 文件结构
```
scripts/tools/wechat-fetch.py                    # 独立快捷脚本 (一条命令)
scripts/tools/web-archive/lib/fetcher.py         # 微信特化抓取 (web-archive 集成)
scripts/tools/web-archive/lib/adapters/wechat.py # 微信适配器 (data-src 图片/作者/时间)
scripts/tools/web-archive/lib/adapters/base.py   # 空段落清理保留含图容器
```

## Quality Checklist
- [ ] 脚本抓取成功（无「环境异常」页）
- [ ] 标题/公众号/作者提取正确
- [ ] 正文无重复段落（去重生效）
- [ ] 图片为 web 链接（mmbiz.qpic.cn）且数量合理（非 0）
- [ ] 归档后完成单同步（kb-log-append.py 追加 log.md）
