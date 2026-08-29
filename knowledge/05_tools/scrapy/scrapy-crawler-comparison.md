# 爬虫框架全景对比与选型指南

> 来源：基于 `import/` 教程材料的爬虫框架全景对比整理，覆盖 Python 静态/动态/分布式/其他语言方案。

---

## 一、核心框架/方案总览

### ① Python 静态爬虫（无 JS 渲染）

| # | 方案 | 类型 | 异步 | 调度/去重 | 学习曲线 | 最佳场景 |
|:-:|:-----|:----|:----|:----------|:---------|:---------|
| 1 | Requests + BeautifulSoup | 轻量组合 | ❌ | ❌ | 低 | 小静态页、快速脚本 |
| 2 | Requests + lxml | 轻量组合 | ❌ | ❌ | 中 | 静态、量大、XPath 偏好 |
| 3 | aiohttp + lxml | 异步组合 | ✅ | ❌ | 中 | 高并发静态/API |
| 4 | **Scrapy** | 完整框架 | ✅ | ✅ | 中 | 中大型、长期项目 |
| 5 | **Scrapy-Redis** | 分布式扩展 | ✅ | ✅(分布) | 中高 | 大规模分布式 |

### ② Python 动态爬虫（JS 渲染/SPA）

| # | 方案 | 类型 | 异步 | 适用场景 |
|:-:|:-----|:----|:----|:---------|
| 6 | Selenium | 浏览器驱动 | ❌ | 强 JS、复杂交互、登录验证码 |
| 7 | **Playwright** | 现代浏览器 | ✅ | SPA、稳定渲染、推荐替代 Selenium |
| 8 | Pyppeteer | Chrome 协议 | ✅ | 仅 Chromium、社区不活跃 |
| 9 | Splash | 渲染服务 | — | Scrapy + JS 渲染中间件 |

### ③ 一站式/低代码框架

| # | 方案 | 特点 |
|:-:|:-----|:------|
| 10 | **Pyspider** | Web UI 管理、分布式、JS 渲染 |
| 11 | Feapder | 国产轻量类 Scrapy、内置断点续爬 |
| 12 | Newspaper | 自动提取新闻正文，无需写 XPath |

### ④ 其他语言

| 语言 | 推荐框架 | 场景 |
|:-----|:---------|:-----|
| Java | WebMagic / Apache Nutch | 中小型 / 全网级 |
| Go | **Colly** | 高性能、简洁 API |
| Rust | spider | 极速、低内存、超大规模 |

---

## 二、Scrapy 与 BeautifulSoup 核心区别

### 定位差异

| 对比项 | BeautifulSoup | Scrapy |
|:-------|:--------------|:-------|
| 本质 | 纯 HTML/XML **解析库** | 工业级**爬虫框架**（全链路） |
| 网络请求 | 无，依赖 `requests` 等 | 内置异步下载器 |
| 任务调度 | 需手动写循环/队列 | 内置调度器，自动排队/去重/重试 |
| 运行模式 | 同步为主 | 异步 IO，高并发 |
| 数据持久化 | 手动写代码 | Item Pipeline 一键落地 |
| 反爬支持 | 手动加头/代理 | 中间件统一管理 UA/代理/Cookie |
| 项目结构 | 单脚本即可 | 标准化项目目录 |
| 上手难度 | 低 | 中等 |

### 混用方式

两者不冲突，Scrapy 内部可无缝集成 BS4 做解析：

```python
from bs4 import BeautifulSoup

def parse(self, response):
    soup = BeautifulSoup(response.text, "html.parser")
    # 用 BS 语法提取数据
```

### 选型原则

- **小任务、临时脚本** → Requests + BeautifulSoup（轻量灵活）
- **大规模、复杂爬虫、长期项目** → Scrapy（功能完备、易维护）

---

## 三、标准选型流程（五步决策）

### Step 1：判断页面类型

打开网页 → 右键查看源代码 → 搜索目标文本：
- **能搜到** → 静态页面 → 走「请求+解析」路线
- **搜不到** → JS 动态页面 → 走「浏览器渲染」路线

### Step 2：评估爬取规模与周期

| 场景 | 静态页推荐 | 动态页推荐 |
|:-----|:-----------|:-----------|
| 一次性脚本/少量数据 | Requests + BS4 | Playwright |
| 中规模/单机/长期 | **Scrapy** | Scrapy + Splash / Playwright |
| 大规模/十万+/多机 | **Scrapy-Redis** | 分布式 Playwright 集群 |

### Step 3：核对功能诉求

| 需求 | 推荐 |
|:-----|:------|
| 可视化任务管理 | Pyspider |
| 仅提取新闻正文 | Newspaper |
| Java 技术栈 | WebMagic / Nutch |
| 极致性能/低内存 | Go-Colly / Rust-spider |

### Step 4：资源约束

- 低配云机 → 禁用 Selenium/Playwright，优先纯 HTTP
- 高配服务器 → 可放心使用浏览器渲染

### Step 5：反爬强度

| 反爬等级 | 特征 | 推荐方案 |
|:---------|:-----|:---------|
| 基础 | UA/Cookie | 所有方案可适配 |
| 中级 | IP 限制/频次 | Scrapy 中间件 + 代理池 |
| 高级 | 验证码/滑块/设备指纹 | 真实浏览器（Playwright） |

---

## 四、分场景精准匹配表

### 静态页面场景

| 场景 | 推荐 | 不推荐 |
|:-----|:------|:-------|
| 临时小脚本、几十页数据 | requests + BS4 | Scrapy（太重） |
| 量大、追求解析速度 | requests + lxml | BS4（解析慢） |
| 企业项目、长期维护 | **Scrapy** | 手写同步脚本 |
| 多机分布式 | **Scrapy-Redis** | 单机框架 |

### 动态 JS/SPA 页面场景

| 场景 | 推荐 | 说明 |
|:-----|:------|:------|
| 少量页面、快速开发 | Playwright | 优于 Selenium |
| 复杂交互、高反爬 | Playwright / Selenium | 真实浏览器 |
| Scrapy 项目加 JS 渲染 | Scrapy + Splash | 资源轻 |
| 大规模动态页集群 | 分布式 Playwright | 进程隔离 |

---

## 五、选型避坑指南

1. **不要盲目上重型框架** — 几十条数据没必要搭 Scrapy 项目
2. **静态页不要强用浏览器渲染** — 纯 HTTP 效率高几十倍
3. **分布式必配 Redis** — 提前规划中间件服务
4. **新项目选 Playwright 而非 Pyppeteer** — 后者生态停滞
5. **企业项目选社区活跃框架** — Scrapy、Playwright、Colly

### 速选口诀

```
静态临时 → requests + BS4
静态正式 → Scrapy
静态海量 → Scrapy-Redis
JS动态常规 → Playwright
JS动态+Scrapy → Scrapy + Splash
可视化管理 → Pyspider
高性能非Python → Go-Colly
```

## 相关页面

- [Scrapy 框架概述](scrapy-framework-overview.md)
- [Scrapy 分布式部署](scrapy-distributed-deployment.md)
- [Scrapy 去重机制](scrapy-deduplication-mechanism.md)
- [Scrapy 进阶与实战](scrapy-advanced-practice.md)
