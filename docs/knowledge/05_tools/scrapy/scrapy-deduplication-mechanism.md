# Scrapy 去重机制深度解析

> 来源：基于 `import/` 教程材料的调度器去重讲解整理。
>
> 核心结论：调度器不是直接比对 URL 字符串，而是给每个请求算一个**唯一指纹**，用一个「已见过指纹集合」来判断重复。

---

## 一、核心角色

| 角色 | 职责 |
|:-----|:------|
| **调度器（Scheduler）** | 管队列，入队前必问去重器 |
| **RFPDupeFilter（默认去重器）** | 负责算指纹、查重复 |
| **request_fingerprint（指纹函数）** | 把请求变成一串 SHA1 哈希 |
| **seen = set()（内存集合）** | 存所有已见过的指纹 |

### 生活化比喻

```
调度器 = 接单台
DupeFilter = 带黑名单的登记员
指纹集合 = 黑名单本子
每个请求 = 一个外卖订单
```

流程：
1. 每来一个新订单，登记员把订单浓缩成一个**唯一编号（指纹）**
2. 查**黑名单本子**：编号已存在 → 撕掉（不进队列）；不存在 → 登记入本 → 进队列

---

## 二、去重判断流程

### 入队时刻

每次往调度器塞请求时执行：

```python
# 调度器入队伪代码
def enqueue_request(self, request):
    if not request.dont_filter and self.df.request_seen(request):
        return False  # 重复，丢弃
    self.queue.push(request)
    return True       # 新请求，入队
```

### 完整流程

```
引擎把 Request 交给调度器
    → 调度器调用 dupefilter.request_seen(request)
    → request_seen 做两件事：
        (1) 调用 request_fingerprint(request) 算出指纹 fp
        (2) 检查 fp 是否在 self.seen 集合中：
            - 在 → 返回 True（重复，丢弃）
            - 不在 → 把 fp 加入 self.seen → 返回 False（新请求，入队）
    → 调度器根据返回值决定是否入队
```

---

## 三、指纹怎么算？（决定"什么算重复"）

默认指纹由以下 **4 部分序列化后用 SHA1 哈希**得到：

| 因子 | 说明 |
|:-----|:------|
| 请求方法 | GET / POST |
| URL（标准化后） | `?a=1&b=2` 和 `?b=2&a=1` 标准化为相同指纹 |
| 请求体（body） | POST 表单数据不同 → 指纹不同 |
| 部分请求头（可选） | 可配置是否加入指纹 |

> 一句话：**只要"方法 + URL + 请求体"有一点不一样，指纹就不一样，就不会被当成重复。**

---

## 四、边界情况分析

| 场景 | 是否会判重复 | 原因 |
|:-----|:------------|:------|
| URL 相同、参数顺序不同 | **会** | 标准化后相同 |
| GET vs POST 同一个 URL | **不会** | 方法不同，指纹不同 |
| URL 带动态参数（如 timestamp） | **不会** | URL 变了，指纹变 |
| 同一 URL 第二次请求 | **会** | 指纹已存在 |
| 显式指定 `dont_filter=True` | **不会** | 跳过去重检查 |

### 强制跳过去重

```python
yield scrapy.Request(url, dont_filter=True)
```

---

## 五、分布式场景下的去重

| 模式 | 去重存储 | 原理 |
|:-----|:---------|:------|
| 单机 | 内存 set | 进程内去重 |
| 分布式 | **Redis Set**（scrapy-redis） | 所有爬虫实例共享同一 Redis 集合 → **全局去重** |

分布式去重配置：

```python
# settings.py
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
```

---

## 六、自定义去重器（进阶）

如需自定义去重逻辑（如只按 URL 去重，忽略参数），可实现：

```python
from scrapy.dupefilters import BaseDupeFilter

class CustomDupeFilter(BaseDupeFilter):
    def __init__(self):
        self.seen = set()

    def request_seen(self, request):
        # 只取 URL 的 path 部分做去重
        fp = request.url.split("?")[0]
        if fp in self.seen:
            return True
        self.seen.add(fp)
        return False
```

然后在 `settings.py` 中指定：

```python
DUPEFILTER_CLASS = "myproject.filters.CustomDupeFilter"
```

---

## 七、一句话总结

**给每个请求算指纹 → 查指纹黑名单 → 有就丢、没有就登记+入队**，默认按「方法 + URL + 请求体」判重，`dont_filter=True` 可跳过检查。

## 相关页面

- [Scrapy 框架概述](scrapy-framework-overview.md)
- [Scrapy 分布式部署](scrapy-distributed-deployment.md)
