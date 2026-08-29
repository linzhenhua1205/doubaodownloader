# Scrapy 分布式部署完整指南（Scrapy-Redis）

> 来源：基于 `import/` 教程材料的详细 Scrapy-Redis 分布式方案整理。
>
> **核心原理**：借助 Redis 统一管理请求队列、去重指纹、爬虫状态，多台机器共享任务池，实现分布式爬取。

---

## 一、前置环境准备

### 1. 统一依赖安装

所有爬虫节点执行：

```bash
pip install scrapy scrapy-redis redis
```

### 2. 部署 Redis 服务（核心中枢）

**Redis 单独部署在一台独立服务器**，所有爬虫节点需能连通。

修改 `redis.conf`：

```ini
# 允许外网访问
# bind 127.0.0.1
# 关闭保护模式（生产环境建议设密码）
protected-mode no
# 可选：设置访问密码
requirepass your_password
```

启动验证：

```bash
redis-server /etc/redis/redis.conf
# 爬虫节点验证连通
redis-cli -h RedisIP -p 6379 -a password
```

> ⚠️ 防火墙放行 Redis 默认端口 6379

---

## 二、改造 Scrapy 项目（关键步骤）

### 1. 修改爬虫文件（Spider）

**写法 1：继承 `RedisSpider`（推荐）**

```python
# spiders/demo_spider.py
from scrapy_redis.spiders import RedisSpider

class DemoSpider(RedisSpider):
    name = "demo"
    allowed_domains = ["example.com"]
    # Redis 队列键名，多爬虫务必唯一
    redis_key = "demo:start_urls"

    def parse(self, response):
        yield {"title": response.xpath("//title/text()").get()}
        # 新 Request 自动进入 Redis 队列
```

**写法 2：继承 `RedisCrawlSpider`（规则爬虫）**

```python
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

class DemoCrawlSpider(RedisCrawlSpider):
    name = "demo_crawl"
    redis_key = "demo_crawl:start_urls"
    rules = [
        Rule(LinkExtractor(), callback="parse_item", follow=True)
    ]

    def parse_item(self, response):
        pass
```

### 2. 核心配置 `settings.py`

**所有分布式节点配置必须完全一致：**

```python
# 1. 开启 Redis 调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 2. 开启 Redis 去重过滤器（全局 URL 去重）
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 3. 持久化队列：停止后保留任务队列，重启继续爬
SCHEDULER_PERSIST = True

# 4. 队列模式（推荐优先级队列）
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queues.PriorityQueue"

# 5. 连接 Redis
REDIS_HOST = "Redis服务器IP"
REDIS_PORT = 6379
REDIS_PASSWORD = "your_password"
REDIS_DB = 0

# 6. （可选）数据存入 Redis
# ITEM_PIPELINES = {
#     'scrapy_redis.pipelines.RedisPipeline': 300,
# }

# 7. 通用优化
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 16
```

---

## 三、项目打包与部署

### 1. 项目统一分发

保证所有爬虫节点的项目代码完全一致，通过 `scp/rsync` 分发。

### 2. 节点分类

| 节点类型 | 职责 |
|:---------|:------|
| **Redis 主节点** | 仅运行 Redis，不启动爬虫 |
| **爬虫工作节点** | 部署 Scrapy 项目，执行爬虫命令 |

---

## 四、启动分布式爬虫

### Step 1：向 Redis 推送起始 URL

```bash
redis-cli -h RedisIP -p 6379 -a password

# 推送起始 URL（和 redis_key 保持一致）
lpush demo:start_urls https://www.example.com
```

### Step 2：所有节点启动爬虫

```bash
scrapy crawl demo
```

- 多机同时执行，共享 Redis 任务队列，自动分布式协作
- 新增节点直接执行命令即可扩容，无需额外配置

### 生产环境后台运行

```bash
nohup scrapy crawl demo > log.txt 2>&1 &
# 查看进程
ps -ef | grep scrapy
# 停止
kill -9 PID
```

---

## 五、运维与监控

### 查看队列状态

```bash
# 待爬取请求数量
llen demo:start_urls
# 去重指纹数量
dbsize
```

### 断点续爬

配置了 `SCHEDULER_PERSIST = True`：
- 意外停止后，Redis 队列、去重数据保留
- 再次执行 `scrapy crawl demo` 自动从断点继续

### 清空任务（重置爬虫）

```bash
# 清空任务队列
del demo:start_urls
# 清空去重指纹
flushdb
```

---

## 六、常见问题

| 问题 | 原因 | 解决 |
|:-----|:------|:------|
| 节点无法连接 Redis | 防火墙/绑定配置 | 检查 6379 端口、`REDIS_HOST`、密码 |
| 多节点重复爬取同一 URL | 去重配置不一致 | 确认 `DUPEFILTER_CLASS` 和 `settings.py` 一致 |
| 爬虫卡死无请求 | 队列为空 / 被封 | 检查 `llen`，调整 `DOWNLOAD_DELAY` 和并发 |
| Redis 性能瓶颈 | 海量任务 | Redis 单独高配部署，定期持久化 RDB/AOF |

---

## 七、进阶扩展方案

1. **代理池**：下载中间件对接代理池，多节点共享
2. **数据持久化**：自定义 Pipeline 统一写入 MySQL/Elasticsearch
3. **容器化部署**：Docker 打包 Scrapy + Redis，Docker Compose 编排
4. **定时任务**：Crontab 实现定时启动/更新

## 相关页面

- [Scrapy 框架概述](scrapy-framework-overview.md)
- [Scrapy 进阶与实战](scrapy-advanced-practice.md)
- [爬虫框架对比与选型](scrapy-crawler-comparison.md)
