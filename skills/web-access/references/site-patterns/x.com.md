---
domain: x.com
aliases: [X, Twitter, 推特, x.com, twitter.com, 推文, 时间线, tweet]
updated: 2026-08-12
---
## 平台特征
- X/Twitter 内容抓取反爬严格：网页层需登录态/动态渲染，WebFetch/curl 直抓基本不可行
- 本系统首选获取方式：**fetch-skill**（`skills/web-access/scripts/fetch-skill/fetch.py`）
- 核心零依赖路径：**FxTwitter API**（`api.fxtwitter.com`，实测 2026-08-12 可达 200）——单条推文无需登录、无需 API Key、仅 Python stdlib
- X/Twitter 数据源定位：**中等置信**（官方账号/大 V 声明可作信号，但量化数据/产品参数须交叉验证厂商一手来源）
- 增强功能（回复/时间线/X Article 长文）需要 **Camofox**（本地 Firefox 反检测服务，localhost:9377）+ Nitter——本系统服务器无桌面环境，默认不可用

## 有效模式
- **单条推文**（零依赖，已验证）：
  ```bash
  python3 skills/web-access/scripts/fetch-skill/fetch.py "https://x.com/<user>/status/<id>" -q -t
  # 或完整 JSON: 去掉 -t，加 --pretty
  ```
  输出：作者/时间/正文/❤️👁🔁🔖 互动数据（实测 jack/status/20 全字段正常）
- **X Article 长文**：单推文路径返回 tweet.article 时自动解析 DraftJS→Markdown（零依赖）；`x.com/i/article/<id>` 形式需 Camofox
- **推文回复**：`-r/--replies`（需 Camofox）
- **用户时间线**：`--user <name> --limit N`（需 Camofox，走 nitter.net——实测 nitter 不可达）
- **普通网页/微信**：同一脚本统一路由（web 回退链 Jina→defuddle→markdown.new→raw）

## 已知陷阱
- **本环境实测（2026-08-12）**：
  - ✅ `api.fxtwitter.com` 可达（单推文/用户信息正常）
  - ⚠️ `r.jina.ai` / `defuddle.md` 超时 → 普通网页回退链实际只到 markdown.new/raw
  - ⚠️ `nitter.net` 不可达 → 时间线/回复路径不可用（即使有 Camofox）
  - ❌ `web_search`（Zhipu key）不可用，无法用它找推文 ID
- 推文 ID 无效时（已删除/不存在）FxTwitter 返回 404，脚本自动 fallback 到 web 抓取（本环境会慢/失败）——**先用 `curl api.fxtwitter.com/<user>/status/<id>` 验证 ID 有效再跑 fetch.py**
- 微信路径的 WeSpy 自动克隆已禁用（安全策略，需 `FETCH_WESPY_DIR` 显式指定）；微信抓取仍走本系统 wechat-article-fetch（三要素绕过，更可靠）
- 单条推文零依赖路径 = fetch-skill 对本系统**唯一确定可用的核心增量**（X 数据源此前完全缺失）
