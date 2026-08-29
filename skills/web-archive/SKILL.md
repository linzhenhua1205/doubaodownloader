---
name: web-archive
description: "Archive web page URLs (non-Doubao) into the knowledge base with proper markdown formatting, image-as-web-link, noise filtering, critical dialectical analysis + principles + market opportunity, index/log/roadmap updates, and link verification. Framework-based with site-specific adapters for accelerated processing. Use when: (1) user pastes a URL to archive/save/record, (2) user shares an article or web page and asks to keep it, (3) user says 归档 with a URL that is NOT a Doubao shared link. Do NOT use for Doubao (豆包) shared links — use doubao-share skill instead."
metadata:
  bins: ["python3", ".venv-web/bin/python"]
---

# Web Archive Skill v2.0（框架化网页归档）

Archive web page URLs into the knowledge base with standardized markdown format, **image-as-web-link**, **content denoising**, **critical dialectical analysis + first-principles + market opportunity**, automatic index/log updates, and link integrity validation.

## When to Trigger

- User pastes a URL and says "归档"/"保存"/"存档"/"记录"/"archive"/"save"
- User shares an article/document page for the knowledge base
- **Do NOT trigger** for Doubao (豆包) shared URLs — those go to `doubao-share` skill

## 核心能力（v2.0 七项要求）

| # | 要求 | 实现 |
|:--|:-----|:-----|
| 1 | Markdown 格式存储 | 自动生成结构化 Markdown（摘要/正文/图片/分析/链接） |
| 2 | 图片 web 链接方式 | 相对→绝对 URL 转换，**不下载图片**；data:URI/占位图过滤 |
| 3 | 过滤非内容信息 | 站点适配器去噪（导航/广告/侧栏/页脚/推荐/脚本/样式） |
| 4 | 批判辩证分析+底层原理+市场机会 | LLM 增强（DeepSeek/OpenAI），无 LLM 时规则模板兜底 |
| 5 | 尽量用 scripts 实现 | `scripts/tools/web-archive/` 全脚本框架，一条命令归档 |
| 6 | 框架化+站点针对性加速 | 站点适配器注册表（9+ 站点），通用 trafilatura 回退 |
| 7 | 保存到 `knowledge/06_others/sources/` | 默认输出目录，文件名 `YYYY-MM-DD-英文描述.md` |

## 快速使用

```bash
# 推荐: 用项目 venv 运行 (含 trafilatura/pypinyin 依赖)
cd /home/lzh/cow
.venv-web/bin/python scripts/tools/web-archive/web-archive.py --url "<URL>"

# 系统 python 也可运行 (缺依赖时自动降级: trafilatura→bs4, pypinyin→拼音fallback)
python3 scripts/tools/web-archive/web-archive.py --url "<URL>"

# 常用参数
--dry-run       # 只提取预览, 不写入
--no-analyze    # 跳过 LLM 批判分析 (离线场景)
--slug <name>   # 自定义文件名 slug (默认由标题智能生成)
--out <path>    # 自定义输出路径
```

**环境准备（首次）**:
```bash
uv venv .venv-web && uv pip install --python .venv-web/bin/python \
  trafilatura html2text requests beautifulsoup4 lxml pypinyin \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**LLM 分析密钥**: 自动读取 `DEEPSEEK_API_KEY`（或 `OPENAI_API_KEY`）环境变量；无密钥时自动降级为规则模板（批判分析骨架 + 领域原理匹配 + 市场机会提示）。

## 工作流

### Step 1: 运行归档脚本

```bash
.venv-web/bin/python scripts/tools/web-archive/web-archive.py --url "<the_url>"
```

脚本自动完成：适配器识别 → 抓取（requests→浏览器回退）→ 正文提取 → 去噪 → 图片 URL 化 → LLM 批判分析 → Markdown 渲染 → 保存。

### Step 2: 单同步（脚本完成后必须执行，2026-08-07 起取代三同步）

> ⚠️ **2026-08-07 单同步纪律**：`06_others/` 属于全局索引模块；README.md/index.md/log.md 三文件**禁止 AI 直接编辑**，统一走脚本。归档后只做一件事——把全面摘要写到 `tmp/` 草稿，用 `kb-log-append.py` 追加 log.md：

```bash
cat > tmp/kb-log-draft-<date>.md <<'EOF'
- **ingest** 📥 [knowledge/06_others/sources/YYYY-MM-DD-英文描述.md](06_others/sources/YYYY-MM-DD-英文描述.md) — 站点 — 标题 — 归档说明(@HH:MM)
EOF
python3 scripts/tools/kb-log-append.py --file tmp/kb-log-draft-<date>.md --section 06_others/sources
```

（README.md 条目库与 index.md 由脚本批量处理，不在单次归档时更新——`kb-global-index.py` 定期批量刷新，无需归档时手动运行）

### Step 3: 格式与链接验证

```bash
python3 scripts/check/format-validator.py 06_others/sources/<文件>.md
python3 scripts/check/link-validator.py --file knowledge/06_others/sources/<文件>.md
```

### Step 4: 人工审查（质量门）

- [ ] 文件名符合 `YYYY-MM-DD-英文描述.md`？
- [ ] 正文是否混入导航/广告/推荐等噪声？（若有，手工清理）
- [ ] 图片是否为 web 链接？（若含本地路径，修复）
- [ ] 批判辩证分析是否合理？（LLM 生成需人工复核事实）
- [ ] 摘要 ≤120 字符？

## 归档文件结构

```markdown
# 标题

> **Source**: <原始URL>
> **Site**: 站点 | **Archived**: 归档日期 | **Author**: 作者 | **Published**: 发布时间
> **Adapter**: 使用的站点适配器

## 内容摘要
1-2 句话概述（自动由 description 生成，可人工完善）

## 原文核心内容
去噪后的正文（结构保留）

## 图片（web 链接）
![alt](https://绝对URL)   ← 仅 web 链接，不下载

## 批判辩证分析
论点强度/数据可信度/反方视角/时效性（LLM 或规则生成）

## 底层原理补充
第一性原理解释（LLM 或领域规则匹配）

## 市场机会
需求侧/落地路径/风险（LLM 或规则生成）

## 原文链接
原始 URL + 正文相关链接

> 📥 Archived by web-archive v2.0 | 日期 | 适配器
```

## 框架架构（扩展新站点）

```
scripts/tools/web-archive/
├── web-archive.py          # CLI 入口
├── lib/
│   ├── fetcher.py          # 抓取 (requests→browser 回退)
│   ├── extractor.py        # 正文提取与去噪
│   ├── markdown.py         # Markdown 渲染 + slug 生成
│   ├── analyzer.py         # 批判分析 + 原理 + 市场机会
│   ├── adapter_registry.py # 适配器注册表 (自动发现)
│   └── adapters/           # 站点适配器 (按域名注册)
│       ├── base.py         # 基类 + 通用适配器
│       ├── jishuzhan.py    # 技术栈
│       ├── wechat.py       # 微信公众号
│       ├── csdn.py         # CSDN
│       ├── infoq.py        # InfoQ
│       ├── zhihu.py        # 知乎
│       └── zh_tech_sites.py # 掘金/博客园/思否/腾讯云
```

**新增站点适配器**（3 步，约 10 分钟）：
1. 在 `lib/adapters/` 新建 `<site>.py`，继承 `AdapterBase`
2. 覆写 `extract_meta`（标题/作者/时间）/ `extract_main`（正文容器选择器）/ `clean_content`（站点噪声）
3. 适配器自动发现（无需注册表手工登记），验证：
```bash
.venv-web/bin/python -c "
import sys; sys.path.insert(0, 'scripts/tools/web-archive')
from lib.adapter_registry import get_adapter
print(get_adapter('https://<新站点>/xxx').name)"
```

**适配器钩子方法**（base.py）：
| 方法 | 用途 | 默认实现 |
|:-----|:-----|:---------|
| `match(url)` | 域名匹配 | 正则匹配 domain_patterns |
| `extract_meta(soup, url)` | 标题/作者/时间 | OG meta 回退 |
| `extract_main(soup, url)` | 正文容器定位 | 常见选择器列表 |
| `clean_content(container)` | 去噪 | 通用噪声选择器 |
| `process_images(container, url)` | 图片 URL 化 | 相对→绝对, 过滤 data:URI |
| `transform_links(container, url)` | 链接规范化 | 相对→绝对, 丢 javascript: |
| `preprocess_html(html)` | 站点预处理 | 原样返回 |
| `postprocess_text(text)` | 文本后处理 | 原样返回 |

## 降级策略（健壮性）

| 场景 | 降级路径 |
|:-----|:---------|
| 无 trafilatura | bs4 + 容器选择器提取 |
| 无 pypinyin | 英文词提取，中文弃用 |
| 无 LLM 密钥 | 规则模板批判分析（标注"建议 LLM 增强"） |
| requests 反爬 | playwright 浏览器渲染回退（自动发现系统 chromium 传 executable_path，命中 WAF/JS 挑战时先访问首页种 cookie 再回目标页） |
| 正文容器未命中 | trafilatura 全自动提取 |

## Quality Checklist

- [ ] 文件名符合 `YYYY-MM-DD-英文描述.md`（design-003）
- [ ] Markdown 结构完整（摘要/正文/图片/批判分析/原理/市场/链接）
- [ ] 图片全部为 web 链接（无本地路径/无 data:URI）
- [ ] 噪声已过滤（无导航/广告/推荐/页脚残留）
- [ ] 批判辩证分析已生成（LLM 或规则）
- [ ] 单同步完成（kb-log-append.py 已追加 log.md）
- [ ] format-validator 通过（100%）
- [ ] link-validator 通过
- [ ] Source URL 保留在文件头部

## Notes

- This skill does NOT handle Doubao share links — redirect those to `doubao-share` skill
- 若 URL 需登录：脚本自动回退浏览器；仍失败则记录缺口，建议手动复制内容
- 反爬站点（雪球/阿里云 WAF 类）：fetcher 已自动处理 —— playwright 自动发现系统 chromium（`~/.cache/ms-playwright/chromium-*/`，不再依赖 playwright 自带版本）；命中 JS 挑战时先访问首页种 cookie 再回目标页。若浏览器仍被 WAF 拦截，可改用同源 JSON API（如雪球 `/statuses/show.json?id=...`）直接拿结构化数据
- **微信公众号（mp.weixin.qq.com）反爬绕过（2026-08-06 实战验证）**：当直抓/换 UA/playwright 渲染全部命中「环境异常」验证页时，用 **微信内置浏览器 UA**（含 `MicroMessenger/` 标识，如 `Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.44(0x18002c2b) NetType/WIFI Language/zh_CN`）+ URL 追加 `&chksm=0000000000000000` + **剥离 `poc_token` 参数**（分享链接携带的分享者 token，实测即使加 chksm 也命中验证页；剥离后才可通过），三要素缺一不可（`scene=27` 非必需）。sn 短链形式无效；验证页特征为返回 17KB 左右、无 `#js_content` 正文容器。失败顺序建议：直抓 → 微信 UA+chksm+剥 poc_token（优先，成功率最高，纯 requests 免浏览器）→ playwright → 搜狗微信按公众号 ID 定位。**一键命令**：`scripts/tools/wechat-fetch.py --url <微信URL>`（内置全部绕过逻辑，输出精简摘要，避免 3MB HTML 进上下文）
- 大型页面提取精华而非全文复制（trafilatura 默认 recall 适中）
- 归档后如内容与既有知识库文档重叠，在 README 条目中标注 related
