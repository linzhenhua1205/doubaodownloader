# Scrapy 爬虫框架概述

> 基于知识库 `programming-tools.md` 中 Scrapy 章节内容提取扩展，结合工程实践经验整理。

## 定位：完整爬虫框架

**Scrapy** 是一个**完整的异步爬虫框架**，覆盖请求调度 → 下载 → 解析 → 清洗 → 存储全流程——与 `BeautifulSoup` 这类仅做 HTML 解析的工具不在一个层级。

### 与 BeautifulSoup 对比

| 维度 | Scrapy | BeautifulSoup |
|:-----|:-------|:--------------|
| 定位 | 完整爬虫框架 | 仅网页解析工具 |
| 能力 | 请求+调度+下载+解析+存储 | 只解析 HTML |
| 异步 | 内置 Twisted 异步引擎 | 需搭配 aiohttp 等 |
| 适用场景 | 大规模、复杂爬虫、长期维护 | 小任务、临时爬取、快速原型 |
| 扩展性 | 中间件/Pipeline/扩展插件体系 | 无扩展机制 |

## 七大核心组件

| 组件 | 职责 |
|:-----|:------|
| **引擎 (Engine)** | 总调度中枢，控制信号/数据/请求在组件间传递 |
| **调度器 (Scheduler)** | 接收引擎发来的请求、排序入队、去重、失败重试 |
| **下载器 (Downloader)** | 发起 HTTP 请求，返回 Response 给引擎 |
| **Spider** | 用户代码主体：解析 Response，提取 Item 或生成新 Request |
| **Item Pipeline** | 处理、清洗、验证、持久化提取到的数据 |
| **下载中间件 (Downloader Middleware)** | Hook 请求发送前/响应返回后（代理、Cookie、重试等） |
| **Spider 中间件 (Spider Middleware)** | Hook Spider 输入/输出 |

### 运行流程

```
引擎获取初始请求
    → 调度器入队（去重/排序）
    → 调度器出队 → 引擎转发给下载器
    → 下载器发起 HTTP 请求
    → 响应返回引擎 → 转发给 Spider
    → Spider 解析 → 产生 Item（Pipeline）或新 Request（→ 调度器）
    → 循环直至队列为空
```

## 快速入门：一个完整爬虫

```python
# quotes_spider.py
import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall(),
            }

        # 翻页
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

运行：
```bash
scrapy runspider quotes_spider.py -o quotes.json
```

## Item Pipeline 典型用法

```python
# pipelines.py
from itemadapter import ItemAdapter

class CleanPipeline:
    """清洗层"""
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter["text"] = adapter["text"].strip()
        adapter["tags"] = [t.lower() for t in adapter.get("tags", [])]
        return item

class SavePipeline:
    """存储层"""
    def open_spider(self, spider):
        self.file = open("items.jsonl", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
```

## 下载中间件场景

```python
# middlewares.py
from scrapy import signals

class RandomUserAgentMiddleware:
    """随机 UA，防止被 ban"""
    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(USER_AGENTS)

class ProxyMiddleware:
    """代理切换"""
    def process_request(self, request, spider):
        request.meta["proxy"] = get_proxy()
```

## 选型建议

| 场景 | 推荐方案 |
|:-----|:---------|
| 小型任务、脚本一次运行 | `requests` + `BeautifulSoup`（轻量灵活） |
| 常规爬虫、需多页面跟进 | Scrapy 单 Spider + Item Pipeline |
| 大规模、反爬严格 | Scrapy + 中间件（UA池/代理/IP旋转） |
| 需 JS 渲染 | Scrapy + `scrapy-playwright` 或 Splash 中间件 |
| 需数据持久化 | Scrapy + Pipeline（写入 DB/文件/云存储） |

## 与 BeautifulSoup 混用

```python
from bs4 import BeautifulSoup

def parse(self, response):
    soup = BeautifulSoup(response.text, "html.parser")
    # Scrapy 拿到 response 后用 BS 解析
    for quote in soup.select("div.quote"):
        yield {
            "text": quote.select_one("span.text").get_text(strip=True),
        }
```

## 常见陷阱

| 陷阱 | 后果 | 解决 |
|:-----|:------|:-----|
| 未配置 `ROBOTSTXT_OBEY` | 默认 True，某些站被阻挡 | 按需设为 False |
| 并发数过高 | IP 被封 | 调小 `CONCURRENT_REQUESTS`（默认 16） |
| 未设置 `DOWNLOAD_DELAY` | 请求过快被限 | 设 0.5-2s 延迟 |
| 未处理反爬 | 403 响应 | 加 UA/Cookie/代理中间件 |
| 数据量过大且不 yield | 内存 OOM | 必须用 `yield` 而非 collect |
| 忘记 `response.follow(..., self.parse)` | 不翻页 | 确认递归调用 |

## 核心配置速查

```python
# settings.py 常见配置
BOT_NAME = "mybot"
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1.0
COOKIES_ENABLED = False
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 ...",
}
ITEM_PIPELINES = {
    "myproject.pipelines.CleanPipeline": 300,
    "myproject.pipelines.SavePipeline": 800,
}
```

## 相关页面

- [Scrapy 进阶与实战](scrapy-advanced-practice.md) — 分布式、反爬、JS渲染、监控
- [编程工具对比选型](../methodology-tools/programming-tools.md) — Scrapy vs BS vs Playwright 全景对比
