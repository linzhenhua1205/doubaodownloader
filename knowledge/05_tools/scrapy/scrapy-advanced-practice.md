# Scrapy 进阶与实战

> 进阶场景：分布式爬虫、反爬对抗、JS 渲染集成、数据管道、监控与部署。

## 一、Scrapy + Playwright（JS 渲染）

现代网站大量使用 JS 动态渲染内容，需集成无头浏览器。推荐 **`scrapy-playwright`** 插件。

### 安装

```bash
pip install scrapy-playwright
playwright install chromium
```

### 配置

```python
# settings.py
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
```

### 使用

```python
class JsSpider(scrapy.Spider):
    name = "js_site"

    def start_requests(self):
        yield scrapy.Request(
            url="https://example.com/dynamic-page",
            meta={"playwright": True},   # 启用 Playwright 渲染
        )

    def parse(self, response):
        # 此时 response 已是 JS 渲染后的完整 HTML
        yield {"title": response.css("h1::text").get()}
```

### 适用判断

| 场景 | 方案 |
|:-----|:------|
| 页面内容在 HTML 中 | 原生 Scrapy（更快、更轻） |
| 页面内容由 JS 异步加载 | Scrapy + Playwright |
| 需点击/滚动/交互 | Playwright 直接驱动 |
| 需截图/性能数据 | Playwright 直接驱动 |

## 二、反爬对抗策略

### 常见反爬手段与应对

| 反爬手段 | 典型特征 | 应对方案 |
|:---------|:---------|:---------|
| User-Agent 检测 | 返回 403/503 | 随机 UA 池（如 `fake-useragent`） |
| IP 频率限制 | 请求过多后封 IP | 代理池（付费/自建）+ DOWNLOAD_DELAY |
| Cookie/Session 验证 | 需先访问首页获取 Cookie | `COOKIES_ENABLED=True` + 模拟登录 |
| 验证码 | 图形验证码/滑块 | ddddocr / 打码平台 / 手动介入 |
| JS 挑战 (Cloudflare) | 需执行 JS 才返回数据 | scrapy-playwright + 等待 |
| 请求头完整性检测 | 检查 Referer/Origin 等 | 补全常见请求头 |

### 代理池集成

```python
# middlewares.py
class ProxyMiddleware:
    def process_request(self, request, spider):
        request.meta["proxy"] = "http://your-proxy-pool:port"

    def process_response(self, request, response, spider):
        if response.status in (403, 429):
            # 代理被封，换一个重试
            request.meta["proxy"] = get_new_proxy()
            return request
        return response
```

## 三、数据持久化 Pipeline

```python
# pipelines.py - 多种存储后端

class MysqlPipeline:
    def open_spider(self, spider):
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        sql = "INSERT INTO quotes (text, author) VALUES (%s, %s)"
        self.cursor.execute(sql, (item["text"], item["author"]))
        self.conn.commit()
        return item


class MongoPipeline:
    def open_spider(self, spider):
        self.client = MongoClient(MONGO_URI)
        self.collection = self.client[DB_NAME][COLLECTION_NAME]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item


class DedupPipeline:
    """去重 Pipeline（基于 URL 或 ID）"""
    def __init__(self):
        self.seen = set()

    def process_item(self, item, spider):
        identifier = item.get("url") or item.get("id")
        if identifier in self.seen:
            raise DropItem(f"Duplicate item: {identifier}")
        self.seen.add(identifier)
        return item
```

## 四、爬虫监控与部署

### 监控指标

| 指标 | 意义 | 采集方式 |
|:-----|:------|:---------|
| 请求总数/秒 | 爬取速度 | Scrapy 统计收集器 |
| 成功/失败数 | 健康度 | 同上 |
| 抓取条目数 | 产出量 | Item Pipeline 计数器 |
| 内存使用 | 稳定性 | OS 级监控 |
| 代理成功率 | 代理池健康度 | 中间件统计 |

### Scrapyd 远程部署

```bash
# 安装
pip install scrapyd

# 启动服务
scrapyd

# 打包部署
# 在项目目录执行：
scrapyd-deploy <target> -p <project>
```

### Docker 化部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["scrapy", "crawl", "my_spider"]
```

## 五、大规模爬虫最佳实践

1. **分而治之**：按网站/模块拆分多个 Spider，每个负责一个数据源
2. **去重前置**：用 Redis 布隆过滤器做分布式去重，而非单机内存 Set
3. **断点续爬**：启用 `JOBDIR` 参数保存调度器状态，方便中断后恢复
4. **限速保活**：`AUTOTHROTTLE_ENABLED = True` 自动调优请求频率
5. **结构化 Item**：用 `scrapy.Item` + `Field` 强类型定义，而非裸 dict
6. **异常兜底**：Spider 中 try/except 包裹解析逻辑，避免单条解析失败导致整个 Spider 挂掉

## 六、典型常见错误

| 错误信息 | 原因 | 解决 |
|:---------|:------|:-----|
| `Spider must return Item, dict, Request or None` | `parse()` 返回了非预期类型 | 检查 `yield` 对象类型 |
| `ReactorNotRestartable` | 多次调用 `scrapy crawl` | 用 `CrawlerRunner` 而非 `CrawlerProcess` |
| `Dropped: IGNORED` | 被 `OffsiteMiddleware` 过滤 | 检查 `allowed_domains` |
| `403 Forbidden` | 被服务器拒绝 | 加 UA/代理/延迟 |
| `TimeoutError` | 下载超时 | 加 `DOWNLOAD_TIMEOUT` 或换代理 |

## 相关页面

- [Scrapy 框架概述](scrapy-framework-overview.md) — 基础概念、核心组件、快速入门
- [爬虫选型对比](../methodology-tools/programming-tools.md) — Scrapy vs BS vs Playwright 全景
