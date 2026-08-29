---
domain: zhihu.com
aliases: [知乎, zhihu, 知乎热榜, 知乎搜索]
updated: 2026-08-12
---
## 平台特征
- 知乎内容（问题/回答/文章/热榜）是 **UGC 内容，属中等置信数据源**：观点、经验、行业动态、趋势信号有价值，但关键量化数据（算力/带宽/延迟/可靠性等）必须经独立源交叉验证（厂商官方、标准组织、可复现推导）后才能引用
- 反爬严格：WebFetch/curl 直接抓取 zhihu.com 页面极易被拦（登录墙、验证码、`window.__INITIAL_STATE__` 反爬），且不携带登录态
- 首选获取方式：**zhihu-cli**（`~/.local/bin/zhihu`，PyPI 包 `pyzhihu-cli` v0.2.4）——通过知乎官方 V4 API 取结构化 JSON，统一 Chrome 浏览器指纹（UA/sec-ch-ua 一致）降风控，比页面抓取稳定得多
- 登录态存 `~/.zhihu-cli/cookies.json`（权限 0600），凭证仅存本地、全程 HTTPS、无密码落地
- 登录方式：`zhihu login --qrcode`（二维码存 `~/.zhihu-cli/login_qrcode.png`，可发用户扫码）或 `zhihu login --cookie "z_c0=...; _xsrf=...; d_c0=..."`（需至少这三项）

## 有效模式
- **搜索**：`zhihu search "关键词"`（默认问题；`--type topic` 话题 / `--type people` 用户；`--json` 结构化输出）
- **热榜**：`zhihu hot -l 10 -a 0`（仅标题）或 `-a 3`（带回答）；`--json`
- **问题详情**：`zhihu question <question_id> --answers --limit N`
- **回答详情**：`zhihu answer <answer_id> -c -l 5`（带评论）
- **用户**：`zhihu user <url_token>` / `zhihu user-answers <url_token> --sort voteups` / `zhihu user-articles <url_token>`
- **话题**：`zhihu topic <topic_id> --questions`
- 所有数据命令支持 `--json` → 机器可读，便于结构化归档
- 用户 URL Token 即个人主页路径（zhihu.com/people/xxx 中的 xxx）

## 已知陷阱
- 所有命令（含 hot/search）**必须先登录**，未登录返回 `Not authenticated`
- 二维码登录为轮询模式，生成后需在知乎 App 扫码，注意二维码时效
- `--cookie` 至少需要 `z_c0`、`_xsrf`、`d_c0` 三项，否则登录失败
- 浏览器 Cookie 与 zhihu-cli 的 cookies.json 是两套体系：从浏览器手动复制 Cookie 时，需找全 z_c0/_xsrf/d_c0（Chrome DevTools → Application → Cookies → zhihu.com）
- `zhihu status` 只检查本地 cookie 文件存在性，不校验会话有效性；会话过期时命令会报错，需重新登录
- 知乎 V4 API 偶发限流（429），连续高频请求时加间隔重试
- 发现日期 2026-08-12：安装后实测 `zhihu hot` 未登录被拒；登录流程与命令细节以 README 为准（README 可能与实际命令略有出入，如 `feeds -c` 参数，以 `zhihu --help` 为准）
