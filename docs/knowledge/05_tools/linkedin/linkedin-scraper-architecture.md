# LinkedIn 爬虫完整实现架构

> **目标**: 实现 Anthropic 人才分析类似的数据采集系统
> **数据来源**: Milan Griffes（招聘方向）的公开分析 + 工程化实现推导
> **技术栈**: Python 3.11+ / Playwright / asyncio / SQLite / Pandas
> **免责声明**: 本方案仅供技术研究和数据分析学习使用。爬取 LinkedIn 可能违反其 ToS，请自行评估合规风险。

---

## 目录

1. [整体架构图](#1-整体架构图)
2. [Part 1: 反检测基础设施层](#2-反检测基础设施层)
3. [Part 2: 浏览器会话管理层](#3-浏览器会话管理层)
4. [Part 3: 人才发现引擎](#4-人才发现引擎)
5. [Part 4: 个人资料抽取器](#5-个人资料抽取器)
6. [Part 5: 数据分析管道](#6-数据分析管道)
7. [部署与运维](#7-部署与运维)

---

## 1. 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LinkedIn 爬虫系统                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │     Part 1: 反检测基础设施层                                 │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │指纹模拟器 │  │代理池管理 │  │速率限制器 │  │Cookie池  │   │    │
│  │  │- Canvas  │  │- 住宅代理 │  │- Token桶 │  │- Session │   │    │
│  │  │- WebGL  │  │- 会话绑定 │  │- 自适应  │  │- 隔离   │   │    │
│  │  │- 时区   │  │- 健康检查 │  │- 退避策略│  │- 轮换   │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │     Part 2: 浏览器会话管理层                                 │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │Stealth层 │  │会话管理  │  │登录引擎  │  │上下文池  │   │    │
│  │  │- Patch  │  │- Cookie  │  │- 凭证    │  │- Browser │   │    │
│  │  │- Header │  │- Storage │  │- 2FA     │  │- Context │   │    │
│  │  │- Navigator│  │- Cache  │  │- CAPTCHA │  │- 复用   │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │     Part 3: 人才发现引擎                                     │    │
│  │  ┌──────────────────┐  ┌────────────────┐  ┌──────────┐   │    │
│  │  │ 路径A: LI搜索    │  │ 路径B: Google   │  │路径C:    │   │    │
│  │  │- Sales Nav API  │  │ Dork           │  │Voyager   │   │    │
│  │  │- 公司页面解析   │  │- site:li/in    │  │ GraphQL  │   │    │
│  │  │- 搜索过滤链    │  │- 标题关键词    │  │ REST API │   │    │
│  │  │- 结果分页      │  │- 批量URL提取   │  │ 限速调用 │   │    │
│  │  └──────────────────┘  └────────────────┘  └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │     Part 4: 个人资料抽取器                                   │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │DOM解析器 │  │经历提取  │  │技能过滤  │  │年限计算  │   │    │
│  │  │- 布局    │  │- 公司名  │  │- 关键词  │  │- 重叠    │   │    │
│  │  │- 动态    │  │- 岗位    │  │- 分类    │  │- 月历    │   │    │
│  │  │- 懒加载  │  │- 时间段  │  │- 评分    │  │- 交叉    │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │     Part 5: 数据分析管道                                     │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │资历分布  │  │公司图谱  │  │技能分析  │  │学位统计  │   │    │
│  │  │- 直方图  │  │- 迁移流  │  │- 标签云  │  │- 占比    │   │    │
│  │  │- 百分位  │  │- 前N源  │  │- 组合    │  │- 交叉    │   │    │
│  │  │- 可视化  │  │- Sankey  │  │- 趋势    │  │- 分布    │   │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│                    ┌──────────────────┐                             │
│                    │    SQLite 持久化   │                             │
│                    │  raw_profiles    │                             │
│                    │  work_experiences│                             │
│                    │  skills_tags     │                             │
│                    │  analytics_cache │                             │
│                    └──────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 反检测基础设施层

### 核心问题

LinkedIn 的反爬体系覆盖**三个层面**：

| 层面 | 检测点 | 惩罚措施 |
|:-----|:-------|:---------|
| **L1: 网络层** | IP 地理、ASN 分布、请求间隔规律、DNS 解析来源 | 限速(429)、验证码、空页面 |
| **L2: 浏览器指纹** | Canvas/WebGL/Font/Audio/时区/语言/UserAgent/屏幕 | 封禁 Session、踢出登录 |
| **L3: 行为层** | 鼠标轨迹、滚动模式、点击间隔、页面停留时间、HTTP Header 顺序 | 限制搜索、限制资料查看、账号限制("unusual activity") |

### 2.1 指纹模拟器

```python
"""
fingerprint_engine.py — 浏览器指纹生成与模拟
"""

import random
import json
from dataclasses import dataclass, field, asdict
from typing import Optional

# ============================================================
# 指纹配置文件库（基于真实浏览器采集数据构建）
# ============================================================

BROWSER_PROFILES = {
    "chrome_126_win": {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "Win32",
        "languages": ["en-US", "en"],
        "timezone": "America/Los_Angeles",
        "timezone_offset": -420,  # PDT
        "webgl_vendor": "Google Inc. (Intel)",
        "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics (0x00009BC4) Direct3D11 vs_5_0 ps_5_0)",
        "canvas_image_hash": "a1b2c3d4e5f6...",  # 预计算的 Canvas 指纹哈希
        "audio_context_hash": "f6e5d4c3b2a1...",
        "fonts": ["Arial", "Consolas", "Courier New", "Georgia", "Segoe UI", "Tahoma",
                  "Times New Roman", "Trebuchet MS", "Verdana", "Webdings", "Wingdings",
                  "Microsoft YaHei", "SimSun"],
        "screen_depth": 24,
        "screen_color_gamut": "srgb",
        "hardware_concurrency": 16,
        "device_memory": 8,
        "max_touch_points": 0,
    },
    "chrome_126_mac": {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "viewport": {"width": 1512, "height": 982},
        "platform": "MacIntel",
        "languages": ["en-US", "en"],
        "timezone": "America/New_York",
        "timezone_offset": -300,  # EDT
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M3 Pro, OpenGL 4.1)",
        "canvas_image_hash": "b2c3d4e5f6a7...",
        "audio_context_hash": "e5d4c3b2a1f6...",
        "fonts": ["AppleSystemUIFont", "Helvetica Neue", "Arial", "Courier New",
                  "Menlo", "Monaco", "Georgia", "Verdana", "Times New Roman",
                  ".AppleSystemUIFontMonospace", "PingFang SC", "Hiragino Sans GB"],
        "screen_depth": 24,
        "screen_color_gamut": "p3",
        "hardware_concurrency": 12,
        "device_memory": 16,
        "max_touch_points": 0,
    },
    "firefox_127_linux": {
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "Linux x86_64",
        "languages": ["en-US", "en"],
        "timezone": "Europe/London",
        "timezone_offset": 60,  # BST
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "AMD Radeon Graphics (RADV NAVI10)",
        "canvas_image_hash": "c3d4e5f6a7b8...",
        "audio_context_hash": "d4c3b2a1f6e5...",
        "fonts": ["DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono", "Liberation Sans",
                  "Liberation Serif", "Liberation Mono", "Noto Sans CJK SC", "Ubuntu"],
        "screen_depth": 24,
        "screen_color_gamut": "srgb",
        "hardware_concurrency": 8,
        "device_memory": 16,
        "max_touch_points": 0,
    },
}


@dataclass
class Fingerprint:
    """单个浏览器指纹的完整描述"""
    profile_name: str
    user_agent: str
    viewport: dict
    platform: str
    languages: list
    timezone: str
    timezone_offset: int
    webgl_vendor: str
    webgl_renderer: str
    canvas_image_hash: str
    audio_context_hash: str
    fonts: list
    screen_depth: int
    screen_color_gamut: str
    hardware_concurrency: int
    device_memory: int
    max_touch_points: int

    def to_patches(self) -> dict:
        """生成 Playwright stealth 补丁参数"""
        return {
            "user_agent": self.user_agent,
            "viewport": self.viewport,
            "locale": self.languages[0],
            "timezone_id": self.timezone,
            "geolocation": self._random_geolocation(),
            "permissions": ["geolocation"],
            "extra_http_headers": {
                "Accept-Language": ", ".join(self.languages),
                "Sec-CH-UA": self._sec_ch_ua(),
                "Sec-CH-UA-Platform": f'"{self.platform}"',
                "Sec-CH-UA-Mobile": "?0",
            },
        }

    def _random_geolocation(self) -> dict:
        """根据时区生成大致 GPS 坐标"""
        geo_map = {
            "America/Los_Angeles": (34.0522, -118.2437),
            "America/New_York": (40.7128, -74.0060),
            "Europe/London": (51.5074, -0.1278),
            "Asia/Tokyo": (35.6762, 139.6503),
            "Asia/Shanghai": (31.2304, 121.4737),
        }
        lat, lng = geo_map.get(self.timezone, (40.7128, -74.0060))
        # 加微小偏移
        return {"latitude": lat + random.uniform(-0.05, 0.05),
                "longitude": lng + random.uniform(-0.05, 0.05)}

    def _sec_ch_ua(self) -> str:
        brand_map = {
            "Chrome": '"Chromium";v="126", "Google Chrome";v="126", "Not.A/Brand";v="24"',
            "Firefox": '"Firefox";v="127"',
            "Edge": '"Microsoft Edge";v="126", "Chromium";v="126", "Not.A/Brand";v="24"',
        }
        for key in brand_map:
            if key in self.user_agent:
                return brand_map[key]
        return brand_map["Chrome"]


class FingerprintManager:
    """指纹池管理器 — 管理一组指纹并在每次新会话时轮换"""

    def __init__(self):
        self._profiles = []
        for name, data in BROWSER_PROFILES.items():
            self._profiles.append(Fingerprint(
                profile_name=name, **data
            ))

    def get_random(self) -> Fingerprint:
        """随机选取一个指纹"""
        return random.choice(self._profiles)

    def get_by_profile(self, name: str) -> Fingerprint:
        """按名称选取指纹"""
        for fp in self._profiles:
            if fp.profile_name == name:
                return fp
        raise ValueError(f"Profile {name} not found")
```

### 2.2 代理池管理

```python
"""
proxy_pool.py — 企业级代理池管理
"""

import asyncio
import time
import random
import aiohttp
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ProxyProtocol(Enum):
    HTTP = "http"
    SOCKS5 = "socks5"


class ProxyAnonymity(Enum):
    ELITE = "elite"        # 透明代理中最隐蔽
    ANONYMOUS = "anonymous"
    TRANSPARENT = "transparent"  # 会传递真实IP


@dataclass
class Proxy:
    host: str
    port: int
    protocol: ProxyProtocol = ProxyProtocol.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    region: str = "us"           # us/eu/asia
    provider: str = "brightdata"  # brightdata/oxylabs/smartproxy/自建
    anonymity: ProxyAnonymity = ProxyAnonymity.ELITE

    # 运行时状态
    last_used: float = 0.0
    fail_count: int = 0
    success_count: int = 0
    avg_latency_ms: float = 0.0
    is_banned: bool = False
    cooldown_until: float = 0.0

    @property
    def url(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.protocol.value}://{auth}{self.host}:{self.port}"

    @property
    def is_available(self) -> bool:
        if self.is_banned:
            return False
        if self.cooldown_until > time.time():
            return False
        return True


class ProxyPool:
    """代理池 — 带健康检查、自动轮换、粘性会话"""

    def __init__(self, min_pool_size: int = 10):
        self._proxies: list[Proxy] = []
        self._min_pool_size = min_pool_size
        self._lock = asyncio.Lock()
        self._proxy_regions: dict[str, list[str]] = {"us": [], "eu": [], "asia": []}

    async def add_proxy(self, proxy: Proxy):
        async with self._lock:
            self._proxies.append(proxy)
            self._proxy_regions[proxy.region].append(f"{proxy.host}:{proxy.port}")

    async def get_best(self, preferred_region: str = "us") -> Optional[Proxy]:
        """获取当前可用且延迟最低的代理"""
        async with self._lock:
            available = [p for p in self._proxies
                         if p.is_available and p.region == preferred_region]
            if not available:
                available = [p for p in self._proxies if p.is_available]
            if not available:
                return None
            # 按失败率升序、成功率降序排序
            available.sort(key=lambda p: (
                p.fail_count / max(p.success_count + p.fail_count, 1),
                -p.success_count,
                p.avg_latency_ms
            ))
            best = available[0]
            best.last_used = time.time()
            return best

    async def record_success(self, proxy_host: str, latency_ms: float):
        async with self._lock:
            for p in self._proxies:
                if p.host == proxy_host:
                    p.success_count += 1
                    # 指数移动平均
                    p.avg_latency_ms = p.avg_latency_ms * 0.7 + latency_ms * 0.3
                    break

    async def record_failure(self, proxy_host: str, is_ban: bool = False):
        async with self._lock:
            for p in self._proxies:
                if p.host == proxy_host:
                    p.fail_count += 1
                    if is_ban:
                        p.is_banned = True
                        p.cooldown_until = time.time() + 3600  # 冷却1小时
                    else:
                        p.cooldown_until = time.time() + 30   # 普通失败冷却30s
                    break

    async def health_check_loop(self, interval: int = 300):
        """定期检查代理健康状态 — 5分钟一次"""
        while True:
            await asyncio.sleep(interval)
            async with self._lock:
                for proxy in self._proxies:
                    if proxy.is_banned and time.time() > proxy.cooldown_until:
                        proxy.is_banned = False  # 冷却到期解除封禁
            # 异步并发检查
            check_tasks = []
            for proxy in self._proxies:
                check_tasks.append(self._check_single(proxy))
            await asyncio.gather(*check_tasks)

    @staticmethod
    async def _check_single(proxy: Proxy):
        """单个代理健康检点 — 访问 http://httpbin.org/ip 验证"""
        try:
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://httpbin.org/ip",
                    proxy=proxy.url,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        latency = (time.time() - start) * 1000
                        # 检查返回的 IP 是否和代理不同（匿名性验证）
                        # 实际做时要确保 data["origin"] 是代理 IP 而不是实际 IP
                        proxy.avg_latency_ms = latency
                        proxy.is_banned = False
                    else:
                        proxy.fail_count += 1
        except Exception:
            proxy.fail_count += 1
            if proxy.fail_count > 5:
                proxy.is_banned = True


# === 商业代理集成示例 ===
#
# BrightData 住宅代理（推荐）：
#   proxy = Proxy("zproxy.lum-superproxy.io", 22225, username="brd-customer-xxx",
#                 password="xxx", protocol=ProxyProtocol.HTTP, region="us")
#
# Oxylabs 住宅代理：
#   proxy = Proxy("pr.smartproxy.com", 10000, username="xxx", password="xxx")
#
# IPRoyal 静态住宅代理：
#   proxy = Proxy("geo.iproyal.com", 12321, username="xxx", password="xxx")
#
# 自建代理（基于 SOCKS5 隧道）：
#   proxy = Proxy("localhost", 9050, protocol=ProxyProtocol.SOCKS5)

```

### 2.3 速率限制器

```python
"""
rate_limiter.py — 多层级自适应速率限制

LinkedIn 的反爬阈值（经验值）：
  - 页面访问: 25-30 页/分钟（同一IP）
  - 个人资料: 100-150 个/天（同一账号）
  - 搜索: 50-80 次搜索/天（同一账号）
  - 登录会话: 最长 6-8 小时建议刷新
"""

import asyncio
import time
import random
from collections import defaultdict
from enum import Enum


class RateLimitTier(Enum):
    """不同操作的速率限制等级"""
    SEARCH = "search"           # 搜索请求 — 最严格
    PROFILE = "profile"         # 资料页面 — 中等
    PAGE = "page"               # 普通页面 — 宽松
    API = "api"                 # API 调用 — 按端点


# 基于实际爬取经验配置的基础速率
BASE_RATES = {
    RateLimitTier.SEARCH: {
        "requests_per_window": 3,       # 每个时间窗口的请求数
        "window_seconds": 60,           # 窗口大小
        "burst_max": 5,                 # 最大突发
        "cooldown_on_error": 120,       # 错误后冷却(s)
    },
    RateLimitTier.PROFILE: {
        "requests_per_window": 6,
        "window_seconds": 60,
        "burst_max": 10,
        "cooldown_on_error": 60,
    },
    RateLimitTier.PAGE: {
        "requests_per_window": 15,
        "window_seconds": 60,
        "burst_max": 25,
        "cooldown_on_error": 30,
    },
    RateLimitTier.API: {
        "requests_per_window": 5,
        "window_seconds": 60,
        "burst_max": 10,
        "cooldown_on_error": 60,
    },
}


class AdaptiveRateLimiter:
    """
    自适应速率限制器 — Token Bucket + 滑动窗口
    
    LinkedIn 爬取的关键：**不稳定低速率**比稳定高速率更安全。
    核心策略：在高请求之间穿插随机延迟，模拟人类浏览模式。
    """

    def __init__(self, base_rates: dict = None):
        self._configs = base_rates or BASE_RATES
        self._window: dict[str, list[float]] = defaultdict(list)  # tier -> timestamps
        self._error_counts: dict[str, int] = defaultdict(int)
        self._cooldown_until: dict[str, float] = defaultdict(float)
        self._lock = asyncio.Lock()

    async def wait_if_needed(self, tier: RateLimitTier):
        """等待直到可以发送请求"""
        await self._check_cooldown(tier)
        config = self._configs[tier]
        key = tier.value

        async with self._lock:
            now = time.time()
            # 清理过期记录
            cutoff = now - config["window_seconds"]
            self._window[key] = [t for t in self._window[key] if t > cutoff]

            current_count = len(self._window[key])

            if current_count >= config["requests_per_window"]:
                # 需要等待：计算最早记录过期的时间
                oldest = min(self._window[key])
                wait_time = oldest + config["window_seconds"] - now
                # 加入随机抖动，避免固定间隔模式
                jitter = random.uniform(0.5, 1.5)
                wait_time = max(0, wait_time * jitter)
                
                async with self._lock:
                    self._lock.release()
                    await asyncio.sleep(wait_time)
                    await self._lock.acquire()
                
                # 重试
                self._window[key].append(time.time())
            else:
                self._window[key].append(time.time())

        # 人类浏览行为模拟：随机短停顿
        human_delay = random.uniform(2.0, 8.0) if tier in (RateLimitTier.PROFILE, RateLimitTier.SEARCH) \
                      else random.uniform(1.0, 3.0)
        await asyncio.sleep(human_delay)

    async def record_error(self, tier: RateLimitTier, status_code: int = None):
        """记录错误，必要时触发冷却"""
        key = tier.value
        self._error_counts[key] += 1
        config = self._configs[tier]

        # 根据错误类型决定冷却时间
        if status_code == 429:  # Too Many Requests — 严重
            cool = config["cooldown_on_error"] * 5
            if self._error_counts[key] > 3:
                cool *= 3  # 累积错误指数退避
        elif status_code in (403, 401):  # 被 ban
            cool = 1800  # 30 分钟
        else:
            cool = config["cooldown_on_error"]

        self._cooldown_until[key] = time.time() + cool

        # 指数退避：错误次数越多越慢
        self._configs[tier] = {
            **config,
            "requests_per_window": max(1, int(config["requests_per_window"] * 0.7)),
        }

    async def _check_cooldown(self, tier: RateLimitTier):
        """检查是否处于冷却期"""
        key = tier.value
        if time.time() < self._cooldown_until[key]:
            wait = self._cooldown_until[key] - time.time()
            await asyncio.sleep(wait)

    async def reset(self):
        """重置限制器状态（用于切换代理/账号后）"""
        async with self._lock:
            self._window.clear()
            self._error_counts.clear()
            self._cooldown_until.clear()
            self._configs = dict(BASE_RATES)  # 恢复到初始值
```

### 2.4 Cookie 与 Session 管理

```python
"""
session_manager.py — 会话持久化与轮换
"""

import json
import time
import os
import hashlib
from pathlib import Path
from typing import Optional


class SessionStore:
    """会话持久化存储 — 管理多个 LinkedIn 账号的登录状态"""

    def __init__(self, storage_dir: str = "./sessions"):
        self._storage_dir = Path(storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def _account_path(self, account_email: str) -> Path:
        """为每个账号生成隔离存储路径"""
        safe_name = hashlib.sha256(account_email.encode()).hexdigest()[:16]
        return self._storage_dir / f"session_{safe_name}.json"

    def save_state(self, account_email: str, state: dict):
        """保存完整浏览器上下文状态"""
        path = self._account_path(account_email)
        metadata = {
            "email": account_email,
            "saved_at": time.time(),
            "state": state,
        }
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)

    def load_state(self, account_email: str) -> Optional[dict]:
        """加载浏览器上下文状态"""
        path = self._account_path(account_email)
        if not path.exists():
            return None
        with open(path, "r") as f:
            data = json.load(f)
        # 有效期检查：LinkedIn 登录通常 24 小时内有效
        if time.time() - data.get("saved_at", 0) > 24 * 3600:
            return None
        return data.get("state")

    def list_accounts(self) -> list[str]:
        """列出所有已保存的账号"""
        accounts = []
        for p in self._storage_dir.glob("session_*.json"):
            try:
                with open(p) as f:
                    data = json.load(f)
                    accounts.append(data.get("email", "unknown"))
            except (json.JSONDecodeError, KeyError):
                continue
        return accounts

    def remove_account(self, account_email: str):
        """移除失效账号的会话"""
        path = self._account_path(account_email)
        if path.exists():
            path.unlink()
```

---

## 3. 浏览器会话管理层

### 3.1 Playwright + Stealth 引擎

```python
"""
browser_engine.py — Playwright 浏览器管理核心
"""

import asyncio
import random
from pathlib import Path
from typing import Optional

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from fingerprint_engine import Fingerprint, FingerprintManager
from proxy_pool import Proxy, ProxyPool
from session_manager import SessionStore


class LinkedInBrowser:
    """
    LinkedIn 专用浏览器管理引擎
    
    全生命周期管理：
      1. 选择指纹 + 代理 → 2. 创建上下文 → 3. 注入 stealth 脚本
      → 4. 加载或创建会话 → 5. 执行操作 → 6. 保存会话
    """

    def __init__(
        self,
        fingerprint_mgr: FingerprintManager,
        proxy_pool: ProxyPool,
        session_store: SessionStore,
        headless: bool = False,
        user_data_dir: Optional[str] = None,
    ):
        self._fp_mgr = fingerprint_mgr
        self._proxy_pool = proxy_pool
        self._session_store = session_store
        self._headless = headless
        self._user_data_dir = user_data_dir

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._fingerprint: Optional[Fingerprint] = None
        self._current_account: Optional[str] = None

    # ============================================================
    # 浏览器启动与上下文创建
    # ============================================================

    async def start(self):
        """启动 Playwright 浏览器实例"""
        self._playwright = await async_playwright().__aenter__()
        self._browser = await self._playwright.chromium.launch(
            headless=self._headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",       # 需要跨域加载某些资源
                "--disable-features=IsolateOrigins,site-per-process",
                f"--window-size={random.randint(1850, 1950)},{random.randint(1020, 1080)}",
            ],
        )

    async def create_linkedin_context(self, account_email: str) -> BrowserContext:
        """为 LinkedIn 创建专门的浏览器上下文（隔离的 Cookie/存储）"""
        self._current_account = account_email
        self._fingerprint = self._fp_mgr.get_random()

        # 选择代理
        proxy = await self._proxy_pool.get_best(preferred_region="us")

        # 检查已保存的会话
        saved_state = self._session_store.load_state(account_email)

        # 创建上下文
        context_params = {
            "user_agent": self._fingerprint.user_agent,
            "viewport": self._fingerprint.viewport,
            "locale": self._fingerprint.languages[0],
            "timezone_id": self._fingerprint.timezone,
            "geolocation": self._fingerprint._random_geolocation(),
            "permissions": ["geolocation"],
            "extra_http_headers": {
                "Accept-Language": ", ".join(self._fingerprint.languages),
                "Sec-CH-UA": self._fingerprint._sec_ch_ua(),
                "Sec-CH-UA-Platform": f'"{self._fingerprint.platform}"',
                "Sec-CH-UA-Mobile": "?0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                          "image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        }

        if proxy:
            context_params["proxy"] = {"server": proxy.url}

        context = await self._browser.new_context(**context_params)

        # 如果有已保存的会话状态，恢复
        if saved_state:
            await context.add_cookies(saved_state.get("cookies", []))
            # 恢复 localStorage
            page = await context.new_page()
            await page.goto("https://www.linkedin.com")
            await page.evaluate(f"""() => {{
                const storage = {json.dumps(saved_state.get("local_storage", {{}}))};
                for (const [key, value] of Object.entries(storage)) {{
                    localStorage.setItem(key, value);
                }}
            }}""")
            await page.close()

        # 注入 Stealth 补丁
        await self._inject_stealth_patches(context)

        self._context = context
        self._page = await context.new_page()
        return context

    # ============================================================
    # Stealth 补丁 — 核心反检测手段
    # ============================================================

    async def _inject_stealth_patches(self, context: BrowserContext):
        """在上下文初始化前注入所有反检测补丁"""
        # 在每个新页面创建时自动注入
        await context.add_init_script(self._STEALTH_SCRIPT)

    _STEALTH_SCRIPT = """
    // ============================================================
    // Playwright Stealth 补丁 v2.0
    // 覆盖 Playwright 自动化特征的每个检测面
    // ============================================================

    (() => {
        'use strict';

        // ── 1. WebDriver 属性 ────────────────────────────────
        // Selenium/Puppeteer/Playwright 都会设置 navigator.webdriver=true
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
            configurable: true,
        });

        // ── 2. Chrome 运行时检测 ──────────────────────────────
        // window.chrome 是普通 Chrome 都有的对象，但自动化工具可能缺失
        if (!window.chrome) {
            window.chrome = {
                runtime: { onConnect: {}, onMessage: {}, sendMessage: () => {} },
                loadTimes: () => {},
                csi: () => {},
                app: {},
            };
        }

        // ── 3. Permissions API ────────────────────────────────
        // 自动化浏览器通常返回 'prompt' 而非 'granted'
        const originalQuery = navigator.permissions.query.bind(navigator.permissions);
        navigator.permissions.query = (params) => {
            const bypass = ['midi', 'midi-sysex', 'notifications', 'push', 'camera',
                           'microphone', 'background-sync', 'ambient-light-sensor',
                           'accelerometer', 'gyroscope', 'magnetometer', 'clipboard-read'];
            if (bypass.includes(params.name)) {
                return Promise.resolve({ state: 'prompt' });
            }
            return originalQuery(params);
        };

        // ── 4. Plugins Array ──────────────────────────────────
        // 真实的 Chrome 至少有 5 个插件
        const plugins = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
            { name: 'Native Client', filename: 'internal-nacl-plugin' },
        ];
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                const arr = plugins;
                arr.item = (i) => arr[i];
                arr.namedItem = (n) => arr.find(p => p.name === n) || null;
                arr.refresh = () => {};
                return arr;
            },
        });

        // ── 5. Languages ──────────────────────────────────────
        // 确保 languages 是完整的数组
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
            configurable: true,
        });

        // ── 6. Canvas Fingerprint 添加噪声 ──────────────────
        // 给 canvas 添加微小噪声，避免与标准自动化浏览器指纹匹配
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, attrs) {
            const context = originalGetContext.call(this, type, attrs);
            if (type === '2d') {
                const originalFillText = context.fillText;
                context.fillText = function(text, x, y, maxWidth) {
                    // 每 100 次调用添加一次 0.1px 偏移
                    if (Math.random() < 0.01) {
                        x += (Math.random() - 0.5) * 0.1;
                        y += (Math.random() - 0.5) * 0.1;
                    }
                    return originalFillText.call(this, text, x, y, maxWidth);
                };
            }
            return context;
        };

        // ── 7. WebGL Fingerprint ──────────────────────────────
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {
            // UNMASKED_VENDOR_WEBGL (37445)
            if (param === 37445) return 'Google Inc. (Intel)';
            // UNMASKED_RENDERER_WEBGL (37446)
            if (param === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)';
            return getParameter.call(this, param);
        };

        // ── 8. screen 属性 ────────────────────────────────────
        Object.defineProperties(screen, {
            colorDepth: { get: () => 24 },
            pixelDepth: { get: () => 24 },
        });

        // ── 9. Connection/RTT ─────────────────────────────────
        if (navigator.connection) {
            Object.defineProperty(navigator.connection, 'rtt', { get: () => 50 + Math.random() * 150 });
        }

        // ── 10. 移除 "webdriver" 跟踪属性 ────────────────────
        const descriptor = Object.getOwnPropertyDescriptor(Document.prototype, 'domain');
        // 某些自动化痕迹存在于 $chrome_asyncScriptInfo 等
    })();
    """

    # ============================================================
    # LinkedIn 登录流程
    # ============================================================

    async def login(self, email: str, password: str) -> bool:
        """
        执行 LinkedIn 登录流程。
        
        返回 True 表示登录成功或已有有效会话。
        返回 False 表示需要人工介入（2FA/CAPTCHA）。
        """
        if not self._page:
            raise RuntimeError("Browser not started. Call start() + create_linkedin_context() first.")

        # 检查是否已有有效登录会话
        await self._page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        current_url = self._page.url
        if "/feed" in current_url:
            return True  # 已有有效会话

        # 导航到登录页
        await self._page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(2, 4))

        # 模拟人类输入 — 逐个字符输入而不是 set_value
        email_input = await self._page.wait_for_selector("#username", timeout=10000)
        await email_input.click()
        await asyncio.sleep(random.uniform(0.3, 0.8))
        for char in email:
            await self._page.keyboard.press(char, delay=random.randint(40, 120))

        await asyncio.sleep(random.uniform(0.5, 1.2))

        pwd_input = await self._page.wait_for_selector("#password", timeout=5000)
        await pwd_input.click()
        await asyncio.sleep(random.uniform(0.3, 0.8))
        for char in password:
            await self._page.keyboard.press(char, delay=random.randint(40, 120))

        await asyncio.sleep(random.uniform(0.5, 1.5))

        # 点击登录按钮
        submit_btn = await self._page.wait_for_selector(
            'button[type="submit"]', timeout=5000
        )
        await submit_btn.click()

        # 等待跳转（最大 15 秒）
        await asyncio.sleep(random.uniform(3, 5))

        # 检查登录后状态
        final_url = self._page.url
        current_text = await self._page.content()

        if "/checkpoint" in final_url or "challenge" in final_url:
            # 需要 2FA 验证或 CAPTCHA — 人工介入
            return False

        if "/feed" in final_url:
            # 登录成功 — 保存会话状态
            await self._save_session_state()
            return True

        # 其他未知情况
        return False

    async def _save_session_state(self):
        """保存当前浏览器上下文状态到持久化存储"""
        if not self._context or not self._current_account:
            return

        cookies = await self._context.cookies()
        state = {
            "cookies": cookies,
        }
        self._session_store.save_state(self._current_account, state)

    # ============================================================
    # 人类行为模拟
    # ============================================================

    async def human_scroll(self, page: Page, target_scrolls: int = None):
        """
        模拟人类逐段滚动浏览页面
        
        人类的滚动是：快速扫→停→看→继续滚，有快有慢，有暂停。
        """
        if target_scrolls is None:
            target_scrolls = random.randint(3, 8)

        for i in range(target_scrolls):
            scroll_amount = random.randint(300, 800)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            # 阅读停顿
            pause = random.uniform(0.8, 3.5)
            await asyncio.sleep(pause)
            # 偶尔回滚
            if random.random() < 0.15:
                back_amount = random.randint(50, 200)
                await page.evaluate(f"window.scrollBy(0, -{back_amount})")
                await asyncio.sleep(random.uniform(0.3, 0.8))

    async def human_mouse_move(self, page: Page):
        """模拟鼠标随机移动"""
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 1800)
            y = random.randint(100, 900)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.1, 0.4))

    async def close(self):
        """关闭浏览器并保存状态"""
        if self._current_account and self._context:
            await self._save_session_state()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.__aexit__(None, None, None)
```

### 3.2 登录与账号管理

```python
"""
account_manager.py — LinkedIn 账号管理
"""

import asyncio
import random
from dataclasses import dataclass, field
from typing import Optional

from browser_engine import LinkedInBrowser
from rate_limiter import AdaptiveRateLimiter, RateLimitTier
from proxy_pool import ProxyPool


@dataclass
class LinkedInAccount:
    """LinkedIn 账号配置"""
    email: str
    password: str
    # 运行时状态
    daily_views: int = 0
    daily_searches: int = 0
    max_daily_views: int = 100    # 单个账号每日上限
    max_daily_searches: int = 50
    is_locked: bool = False
    proxy: Optional[str] = None
    cookies_valid: bool = False


class AccountRotator:
    """
    账号轮换管理器 — 多账号轮流使用，避免单一账号被限制
    
    核心策略：
      1. 每个账号每日有配额上限（经验值）
      2. 达到配额或检测到限制后自动切到下一个账号
      3. 所有账号共享代理池
    """

    def __init__(self, accounts: list[LinkedInAccount]):
        self._accounts = accounts
        self._current_idx = 0
        self._used_today = set()

    def get_next_account(self) -> Optional[LinkedInAccount]:
        """获取下一个可用账号（轮换调度）"""
        start = self._current_idx
        for offset in range(len(self._accounts)):
            idx = (start + offset) % len(self._accounts)
            acc = self._accounts[idx]
            if not acc.is_locked and acc.daily_views < acc.max_daily_views:
                self._current_idx = (idx + 1) % len(self._accounts)
                return acc
        return None  # 所有账号都已用尽

    def mark_account_limited(self, account: LinkedInAccount):
        """标记账号被 LinkedIn 限制，暂停使用"""
        account.is_locked = True
        # 24 小时后自动解锁
        asyncio.create_task(self._auto_unlock(account, 24 * 3600))

    @staticmethod
    async def _auto_unlock(account: LinkedInAccount, delay: int):
        await asyncio.sleep(delay)
        account.is_locked = False

    def reset_daily_counts(self):
        """每日重置配额计数"""
        for acc in self._accounts:
            acc.daily_views = 0
            acc.daily_searches = 0
```

---

## 4. 人才发现引擎

### 4.1 路径 A: LinkedIn 搜索（核心路径）

```python
"""
linkedin_searcher.py — LinkedIn 公司人才发现引擎
"""

import asyncio
import re
import json
import random
from typing import AsyncGenerator, Optional
from urllib.parse import quote, urlencode

from bs4 import BeautifulSoup
from browser_engine import LinkedInBrowser
from rate_limiter import AdaptiveRateLimiter, RateLimitTier


class LinkedInCompanySearcher:
    """
    按公司搜索在职员工的搜索引擎
    
    核心思路：
      1. 使用 LinkedIn Sales Navigator 搜索更精准
      2. 构造布尔搜索过滤链（公司+岗位+...）
      3. 逐页遍历搜索结果，提取 profile URL
    """

    # LinkedIn 搜索 URL 模板
    BASE_SEARCH_URL = "https://www.linkedin.com/search/results/people/"
    
    # 公司名称 -> LinkedIn 内部 ID 缓存
    _company_id_cache: dict[str, str] = {}

    def __init__(
        self,
        browser: LinkedInBrowser,
        rate_limiter: AdaptiveRateLimiter,
    ):
        self._browser = browser
        self._rate_limiter = rate_limiter
        self._page = browser._page  # 引用浏览器页面

    # ============================================================
    # 核心搜索方法
    # ============================================================

    async def search_by_company(
        self,
        company_name: str,
        keywords: list[str] = None,
        max_pages: int = 20,
    ) -> AsyncGenerator[dict, None]:
        """
        按公司搜索所有在职员工
        
        Args:
            company_name: 公司名称，如 "Anthropic"
            keywords: 岗位关键词过滤，如 ["software engineer", "infrastructure"]
            max_pages: 最大搜索页数（每页约 10 条结果）
            
        Yields:
            每条结果为 {"name": str, "url": str, "headline": str, ...}
        """
        await self._rate_limiter.wait_if_needed(RateLimitTier.SEARCH)

        # 第一步：构造搜索 URL
        search_params = self._build_search_params(company_name, keywords)
        search_url = f"{self.BASE_SEARCH_URL}?{urlencode(search_params, doseq=True)}"

        await self._page.goto(search_url, wait_until="networkidle")
        await self._browser.human_scroll(self._page, target_scrolls=2)

        # 第二步：遍历分页
        for page_num in range(1, max_pages + 1):
            results = await self._parse_search_results()
            for result in results:
                yield result

            # 检查是否有下一页
            next_btn = await self._page.query_selector('button[aria-label="Next"]')
            if not next_btn or await next_btn.get_attribute("disabled"):
                break

            # 人类翻页行为模拟
            await self._browser.human_mouse_move(self._page)
            await asyncio.sleep(random.uniform(2, 5))

            await next_btn.click()
            await self._page.wait_for_load_state("networkidle")
            await asyncio.sleep(random.uniform(1, 3))

    def _build_search_params(
        self,
        company_name: str,
        keywords: list[str] = None,
    ) -> dict:
        """构造 LinkedIn 搜索参数"""
        params = {
            "origin": "FACETED_SEARCH",
            "sid": "~cU",
        }

        # 公司过滤 — 使用公司名称直接搜索
        if company_name:
            params["currentCompany"] = self._resolve_company_name(company_name)

        # 岗位关键词
        if keywords:
            # LinkedIn 搜索支持布尔操作符
            keyword_query = " OR ".join(f'"{kw}"' for kw in keywords)
            params["keywords"] = keyword_query

        # 仅限在职员工
        # params["currentCompany"] 已经隐含在职

        return params

    @staticmethod
    def _resolve_company_name(name: str) -> str:
        """
        公司名称 -> LinkedIn 标准化名称
        实际做时应该通过 LinkedIn 公司页面获取精确名称
        """
        name_map = {
            "Anthropic": "Anthropic",
            "OpenAI": "OpenAI",
            "Google": "Google",
            "DeepMind": "DeepMind",
            "Meta": "Meta",
            "Microsoft": "Microsoft",
        }
        return name_map.get(name, name)

    # ============================================================
    # 搜索页面解析
    # ============================================================

    async def _parse_search_results(self) -> list[dict]:
        """从当前搜索页面解析搜索结果"""
        html = await self._page.content()
        soup = BeautifulSoup(html, "lxml")

        results = []
        # LinkedIn 搜索结果卡片的选择器
        cards = soup.select("li[class*='search-result']")

        for card in cards:
            try:
                profile_link = card.select_one("a[href*='/in/']")
                if not profile_link:
                    continue

                url = profile_link.get("href", "")
                # LinkedIn 的 URL 可能带有查询参数，只保留 /in/xxx 部分
                url_match = re.search(r"(/in/[^/?]+)", url)
                if not url_match:
                    continue

                name_elem = card.select_one("span[class*='actor-name']")
                headline_elem = card.select_one("span[class*='subline']")

                result = {
                    "name": name_elem.get_text(strip=True) if name_elem else "Unknown",
                    "url": f"https://www.linkedin.com{url_match.group(1)}",
                    "headline": headline_elem.get_text(strip=True) if headline_elem else "",
                    "source": "linkedin_search",
                }
                results.append(result)
            except Exception:
                continue

        return results

    # ============================================================
    # Sales Navigator 路径（更精确的搜索）
    # ============================================================

    async def search_with_sales_navigator(
        self,
        company_name: str,
        filters: dict = None,
    ) -> list[dict]:
        """
        使用 Sales Navigator 进行更精确的人才搜索
        
        Sales Navigator 的优势：
          - 支持按部门过滤
          - 支持按资历级别过滤（VP/Director/Senior/Entry）
          - 支持自定义列表
        
        Args:
            company_name: 公司名称
            filters: {
                "function": ["Engineering", "Operations"],
                "seniority": ["Director", "VP", "CXO"],
                "location": ["United States"],
                "years_in_role": [1, 20],
            }
        """
        # Sales Navigator URL 格式
        base_url = "https://www.linkedin.com/sales/search/people"
        params = {
            "query": f"(company:(name:{company_name}))",
        }

        # 应用过滤器
        if filters:
            filter_strings = []
            if "function" in filters:
                func_str = ",".join(f'"{f}"' for f in filters["function"])
                filter_strings.append(f"function:({func_str})")
            if "seniority" in filters:
                sen_str = ",".join(f'"{s}"' for s in filters["seniority"])
                filter_strings.append(f"seniority:({sen_str})")
            if filter_strings:
                params["query"] = f"(company:(name:{company_name})," + ",".join(filter_strings) + ")"

        await self._rate_limiter.wait_if_needed(RateLimitTier.SEARCH)
        sales_url = f"{base_url}?{urlencode(params)}"
        await self._page.goto(sales_url, wait_until="networkidle")
        await asyncio.sleep(random.uniform(3, 6))

        # 解析 Sales Navigator 结果（格式与普通搜索不同）
        results = await self._parse_sales_nav_results()
        return results

    async def _parse_sales_nav_results(self) -> list[dict]:
        """解析 Sales Navigator 搜索结果"""
        html = await self._page.content()
        soup = BeautifulSoup(html, "lxml")

        results = []
        # Sales Navigator 结果卡片
        cards = soup.select("li.search-result")

        for card in cards:
            try:
                link = card.select_one("a[href*='/sales/lead/']")
                if not link:
                    continue
                
                name = card.select_one(".name")
                title = card.select_one(".title")
                company = card.select_one(".company-name")

                results.append({
                    "name": name.get_text(strip=True) if name else "",
                    "url": link.get("href", ""),
                    "title": title.get_text(strip=True) if title else "",
                    "company": company.get_text(strip=True) if company else "",
                    "source": "sales_navigator",
                })
            except Exception:
                continue

        return results
```

### 4.2 路径 B: Google Dork

```python
"""
google_dork.py — 利用 Google 爬取 LinkedIn 公开资料链接
"""

import asyncio
import re
import random
from typing import AsyncGenerator

from playwright.async_api import Page
from rate_limiter import AdaptiveRateLimiter, RateLimitTier


class GoogleDorkEngine:
    """
    通过 Google 搜索发现 LinkedIn 公开资料
    
    原理：
      LinkedIn 的公开展示资料对 Google 爬虫是可见的。
      利用 site: 限定和关键词构造搜索，获取 Google 索引中的 LinkedIn 资料链接。
    
    优势：
      - 不需要 LinkedIn 登录
      - 直接得到大量 profile URL
      - Google 的反爬比 LinkedIn 宽松很多
    
    劣势：
      - 数据不完整（Google 索引有延迟）
      - 只能拿到公开资料的基础信息
      - 搜索结果有限制（Google 最多 20-30 页）
    """

    # Google 搜索 URL
    GOOGLE_SEARCH = "https://www.google.com/search"

    def __init__(
        self,
        page: Page,
        rate_limiter: AdaptiveRateLimiter,
    ):
        self._page = page
        self._rate_limiter = rate_limiter

    # ============================================================
    # 核心搜索 Dork 构造
    # ============================================================

    async def search_by_company(
        self,
        company_name: str,
        keyword: str = None,
        max_results: int = 500,
    ) -> list[str]:
        """
        搜索指定公司的 LinkedIn 公开资料
        
        Dork 示例:
          site:linkedin.com/in "Anthropic"
          site:linkedin.com/in "Anthropic" "Software Engineer"
          site:linkedin.com/in "Anthropic" -recruiter -"talent acquisition"
        """
        # 构造搜索查询
        dork_parts = ['site:linkedin.com/in', f'"{company_name}"']
        if keyword:
            dork_parts.append(f'"{keyword}"')
        # 排除干扰项
        dork_parts.append('-recruiter')
        dork_parts.append('-headhunter')
        dork_parts.append('-recruiting')

        query = " ".join(dork_parts)
        return await self._execute_dork_search(query, max_results)

    async def search_by_role_and_location(
        self,
        role: str,
        location: str,
        max_results: int = 300,
    ) -> list[str]:
        """
        搜索特定岗位+地点的 LinkedIn 资料
        
        Dork 示例:
          site:linkedin.com/in "Senior Infrastructure Engineer" "San Francisco"
        """
        query = f'site:linkedin.com/in "{role}" "{location}"'
        return await self._execute_dork_search(query, max_results)

    async def _execute_dork_search(
        self,
        query: str,
        max_results: int,
    ) -> list[str]:
        """执行 Google Dork 搜索，提取 LinkedIn profile URL"""
        urls = set()
        results_per_page = 10
        pages_to_fetch = min(max_results // results_per_page + 1, 30)

        for page_num in range(pages_to_fetch):
            await self._rate_limiter.wait_if_needed(RateLimitTier.PAGE)

            start = page_num * results_per_page
            params = {
                "q": query,
                "start": str(start),
                "num": str(results_per_page),
            }
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{self.GOOGLE_SEARCH}?{param_str}"

            await self._page.goto(url, wait_until="networkidle")
            await asyncio.sleep(random.uniform(1.5, 3.5))

            # 解析搜索结果
            html = await self._page.content()
            page_urls = self._extract_linkedin_urls(html)
            urls.update(page_urls)

            # 检查是否还有下一页
            has_next = await self._page.query_selector("a#pnnext")
            if not has_next:
                break

            if len(urls) >= max_results:
                break

        return list(urls)

    @staticmethod
    def _extract_linkedin_urls(html: str) -> set[str]:
        """从 Google 搜索结果中提取 LinkedIn 资料 URL"""
        # LinkedIn profile URL 模式: linkedin.com/in/用户名
        pattern = r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
        urls = re.findall(pattern, html)
        # 去重并标准化
        clean_urls = set()
        for url in urls:
            # 移除 URL 末尾的斜杠
            url = url.rstrip("/")
            # 移除查询参数
            url = url.split("?")[0] if "?" in url else url
            clean_urls.add(url)
        return clean_urls
```

### 4.3 路径 C: Voyager (GraphQL) API

```python
"""
voyager_api.py — LinkedIn Voyager API 接口
"""

import asyncio
import json
import random
from typing import Optional

from browser_engine import LinkedInBrowser
from rate_limiter import AdaptiveRateLimiter, RateLimitTier


class LinkedInVoyagerAPI:
    """
    LinkedIn Voyager (GraphQL) API 封装
    
    原理：
      LinkedIn 前端使用 GraphQL API（称为 Voyager）。
      登录后的 session 可以直接调用该 API 获取结构化数据。
      这比 DOM 解析快得多，也不需要等待页面渲染。
    
    关键 API 端点：
      - 搜索: /voyager/api/graphql?variables={queryId=searchResults}
      - 资料: /voyager/api/identity/profiles/{username}/profileView
      - 公司: /voyager/api/organization/companies?q=universalName&universalName={name}
    
    注意：
      - 需要有效的 Cookie（从 Playwright 登录获取）
      - 有更严格的限速
      - API 端点经常变化（需要定期更新）
    """

    # 已知的 Voyager API 端点
    API_BASE = "https://www.linkedin.com/voyager/api"

    ENDPOINTS = {
        "search_people": "/graphql?variables=(start:0,origin:GLOBAL_SEARCH_HEADER,q:${query},query:(keywords:${keywords},flagshipSearchIntent:SEARCH_SRP))",
        "profile_view": "/identity/profiles/{profile_id}/profileView",
        "company_info": "/organization/companies?q=universalName&universalName={name}",
        "search_sales_nav": "/sales/graphql?variables=(searchId:...,...)",
    }

    def __init__(
        self,
        browser: LinkedInBrowser,
        rate_limiter: AdaptiveRateLimiter,
    ):
        self._browser = browser
        self._rate_limiter = rate_limiter
        self._csrf_token: Optional[str] = None

    async def initialize(self):
        """初始化 API 客户端，获取 CSRF token"""
        page = self._browser._page
        if not page:
            raise RuntimeError("Browser page not initialized")

        # 从 cookie 中获取 CSRF token
        cookies = await page.context.cookies()
        for cookie in cookies:
            if cookie["name"] in ("JSESSIONID", "csrf_token"):
                self._csrf_token = cookie["value"].strip('"')
                break

    # ============================================================
    # 搜索 API
    # ============================================================

    async def search_people(
        self,
        company: str,
        keywords: str = None,
        start: int = 0,
        count: int = 48,
    ) -> dict:
        """通过 Voyager API 搜索人员"""
        await self._rate_limiter.wait_if_needed(RateLimitTier.API)

        # 构造 GraphQL 查询
        search_params = {
            "keywords": keywords or "",
            "currentCompany": [company],
        }

        # API 端点和参数
        query = json.dumps(search_params)
        url = f"{self.API_BASE}/graphql?variables=(start:{start},origin:GLOBAL_SEARCH_HEADER,q:{query})"

        # 发送请求
        result = await self._call_api("GET", url)
        return result

    # ============================================================
    # 个人资料 API
    # ============================================================

    async def get_profile_details(self, profile_id: str) -> dict:
        """
        获取详细资料（包含所有工作经历）
        
        profile_id: 从 profile URL 中提取的用户名，
                    例如 https://linkedin.com/in/janedoe → "janedoe"
        """
        await self._rate_limiter.wait_if_needed(RateLimitTier.PROFILE)

        url = f"{self.API_BASE}/identity/profiles/{profile_id}/profileView"
        result = await self._call_api("GET", url)

        # 处理返回数据...
        # 实际解析需要处理 LinkedIn 嵌套的 JSON 结构
        return result

    # ============================================================
    # API 调用核心
    # ============================================================

    async def _call_api(self, method: str, url: str, body: dict = None) -> dict:
        """执行 Voyager API 调用"""
        page = self._browser._page
        if not page:
            raise RuntimeError("No active page")

        # 通过 page.evaluate 使用 fetch API
        # 这样可以复用浏览器的 Cookie 和 session
        js_code = f"""
        (async () => {{
            const response = await fetch('{url}', {{
                method: '{method}',
                headers: {{
                    'csrf-token': '{self._csrf_token or ""}',
                    'x-restli-protocol-version': '2.0.0',
                    'accept': 'application/vnd.linkedin.normalized+json+2.1',
                }},
                credentials: 'include',
            }});
            if (!response.ok) {{
                throw new Error(`API error: ${{response.status}}`);
            }}
            return await response.json();
        }})()
        """

        try:
            result = await page.evaluate(js_code)
            return result
        except Exception as e:
            raise RuntimeError(f"Voyager API call failed: {e}")
```

### 4.4 路径汇总与调度

```python
"""
discovery_orchestrator.py — 三种发现路径的调度器
"""

import asyncio
import logging
from typing import AsyncGenerator

from linkedin_searcher import LinkedInCompanySearcher
from google_dork import GoogleDorkEngine
from voyager_api import LinkedInVoyagerAPI
from rate_limiter import AdaptiveRateLimiter, RateLimitTier


class DiscoveryOrchestrator:
    """
    人才发现调度器 — 三路并行/串行调度
    
    策略：
      1. 优先使用 Google Dork（低风险，无账号限制）
      2. 然后使用 LinkedIn 搜索（中等风险，账号配额）
      3. 最后用 Voyager API 补充详细信息（高风险）
    """

    def __init__(
        self,
        linkedin_searcher: LinkedInCompanySearcher,
        google_dork: GoogleDorkEngine,
        voyager_api: LinkedInVoyagerAPI,
        rate_limiter: AdaptiveRateLimiter,
    ):
        self._li_searcher = linkedin_searcher
        self._google_dork = google_dork
        self._voyager = voyager_api
        self._rate_limiter = rate_limiter

        self._discovered_urls: set[str] = set()
        self._profiles: list[dict] = []

    async def discover_all(
        self,
        company: str,
        keywords: list[str] = None,
        max_profiles: int = 2000,
    ) -> list[dict]:
        """
        三条路径全面发现指定公司的人才
        
        流程：
          1. Google Dork — 快速获取大量的 URL
          2. LinkedIn 搜索 — 获取结构化搜索结果
          3. 合并去重
          4. 对每个 profile 提取详细信息
        """
        logging.info(f"Starting discovery for {company} (target: {max_profiles})")

        # Phase 1: Google Dork（无需登录）
        logging.info("Phase 1: Google Dork search")
        dork_urls = await self._google_dork.search_by_company(
            company_name=company,
            keyword="engineer",
            max_results=min(max_profiles * 2, 5000),
        )
        self._discovered_urls.update(dork_urls)
        logging.info(f"  Google Dork found {len(dork_urls)} URLs")

        # Phase 2: LinkedIn 搜索
        logging.info("Phase 2: LinkedIn search")
        li_urls = set()
        async for result in self._li_searcher.search_by_company(
            company_name=company,
            keywords=keywords or ["Software Engineer", "Infrastructure"],
            max_pages=50,
        ):
            li_urls.add(result["url"])
            if len(li_urls) + len(dork_urls) >= max_profiles * 3:
                break

        self._discovered_urls.update(li_urls)
        logging.info(f"  LinkedIn search found {len(li_urls)} URLs")

        # Phase 3: Profile 详细信息提取
        logging.info(f"Phase 3: Fetching profile details ({len(self._discovered_urls)} total)")
        # 通过 Voyager API 获取详细信息（后续章节实现）
        # profile_details = await self._fetch_profiles_batch(list(self._discovered_urls))

        return list(self._discovered_urls)
```

---

## 5. 个人资料抽取器

### 5.1 DOM 解析 + 工作经历提取

```python
"""
profile_extractor.py — LinkedIn 个人资料详细信息的 DOM 提取
"""

import re
import json
from datetime import datetime, date
from typing import Optional
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

from bs4 import BeautifulSoup
from playwright.async_api import Page

from browser_engine import LinkedInBrowser
from rate_limiter import AdaptiveRateLimiter, RateLimitTier


class ProfileExtractor:
    """
    LinkedIn 个人资料抽取器
    
    从个人资料页面的 DOM 中提取结构化的：
      - 基本信息（姓名、头衔、所在地、行业）
      - 工作经历（公司、岗位、时间段、描述）
      - 教育背景
      - 技能标签（前 10-50 个）
      - 学历信息
    """

    def __init__(
        self,
        browser: LinkedInBrowser,
        rate_limiter: AdaptiveRateLimiter,
    ):
        self._browser = browser
        self._page = browser._page
        self._rate_limiter = rate_limiter

    # ============================================================
    # 核心提取方法
    # ============================================================

    async def extract_profile(
        self,
        profile_url: str,
        include_experience: bool = True,
        include_skills: bool = True,
        include_education: bool = True,
    ) -> Optional[dict]:
        """
        提取完整个人资料数据
        
        Args:
            profile_url: LinkedIn 资料 URL，如 https://www.linkedin.com/in/janedoe
            include_experience: 是否提取工作经历
            include_skills: 是否提取技能标签
            include_education: 是否提取教育背景
            
        Returns:
            结构化的个人资料字典，失败返回 None
        """
        await self._rate_limiter.wait_if_needed(RateLimitTier.PROFILE)
        await self._page.goto(profile_url, wait_until="networkidle")

        # 检查页面是否正常加载
        if await self._is_profile_not_found():
            return None

        # 人类浏览行为模拟
        await self._browser.human_scroll(self._page, target_scrolls=4)
        await self._browser.human_mouse_move(self._page)

        html = await self._page.content()
        soup = BeautifulSoup(html, "lxml")

        profile = {
            "profile_url": profile_url,
            "extracted_at": datetime.utcnow().isoformat(),
        }

        # 基本信息
        profile.update(self._extract_basic_info(soup))

        # 工作经历
        if include_experience:
            profile["work_experiences"] = self._extract_work_experiences(soup)
            profile["total_experience_years"] = self._calculate_total_years(
                profile.get("work_experiences", [])
            )

        # 技能
        if include_skills:
            profile["skills"] = self._extract_skills(soup)

        # 教育
        if include_education:
            profile["education"] = self._extract_education(soup)

        return profile

    # ============================================================
    # 基本信息提取
    # ============================================================

    def _extract_basic_info(self, soup: BeautifulSoup) -> dict:
        """提取基本个人资料信息"""
        info = {}

        # 姓名 — LinkedIn 最新布局
        name_selectors = [
            "h1[class*='top-card']",
            "h1[class*='text-heading']",
            ".profile-topcard-person-name",
            ".pv-top-card-section__name",
        ]
        for sel in name_selectors:
            el = soup.select_one(sel)
            if el:
                info["name"] = el.get_text(strip=True)
                break

        # 头衔 / 当前职位
        headline_selectors = [
            "div[class*='text-body-medium']",
            ".pv-top-card-section__headline",
            ".profile-topcard-person-entity__headline",
        ]
        for sel in headline_selectors:
            el = soup.select_one(sel)
            if el:
                info["headline"] = el.get_text(strip=True)
                break

        # 所在地
        location_selectors = [
            "span[class*='text-body-small']",
            ".pv-top-card-section__location",
            ".profile-topcard-person-entity__location",
        ]
        for sel in location_selectors:
            el = soup.select_one(sel)
            if el:
                info["location"] = el.get_text(strip=True)
                break

        return info

    # ============================================================
    # 工作经历提取（核心！）
    # ============================================================

    def _extract_work_experiences(self, soup: BeautifulSoup) -> list[dict]:
        """
        提取完整的工作经历列表
        
        这是整个爬虫最核心的部分。需要处理：
          - 当前 & 历史经历
          - 时间段解析（"2020年1月 - 2023年6月" → (2020-01, 2023-06)）
          - 公司名称标准化
          - 岗位职责描述提取
        """
        experiences = []

        # LinkedIn 工作经历段的选择器（多种布局版本兼容）
        exp_section = soup.select_one("section#experience-section")
        if not exp_section:
            # 备用选择器
            exp_section = soup.select_one("section[class*='experience']")
        if not exp_section:
            return experiences

        # 每一条工作经历
        exp_items = exp_section.select("li[class*='profile-section-card']")

        for item in exp_items:
            try:
                exp = self._parse_single_experience(item)
                if exp:
                    experiences.append(exp)
            except Exception:
                continue

        return experiences

    def _parse_single_experience(self, card_elem: BeautifulSoup) -> Optional[dict]:
        """解析单条工作经历卡片"""
        exp = {}

        # 公司名称
        company_el = card_elem.select_one(
            "span[class*='experience-company'], "
            ".pv-entity__secondary-title, "
            "span[class*='company-name']"
        )
        exp["company"] = company_el.get_text(strip=True) if company_el else ""

        # 岗位名称
        title_el = card_elem.select_one(
            "span[class*='experience-title'], "
            ".pv-entity__summary-title, "
            "h3[class*='profile-section']"
        )
        exp["title"] = title_el.get_text(strip=True) if title_el else ""

        # 时间段
        time_el = card_elem.select_one(
            "span[class*='date-range'], "
            ".pv-entity__date-range, "
            "span[class*='experience-date']"
        )
        if time_el:
            time_text = time_el.get_text(strip=True)
            exp["start_date"], exp["end_date"] = self._parse_date_range(time_text)
            # 判断是否是当前工作
            exp["is_current"] = self._is_current_position(exp["end_date"])

        # 持续时间（计算）
        if exp.get("start_date") and exp.get("end_date"):
            exp["duration_months"] = self._months_between(
                exp["start_date"], exp["end_date"]
            )

        # 岗位描述
        desc_el = card_elem.select_one(
            "div[class*='experience-description'], "
            ".pv-entity__description"
        )
        if desc_el:
            exp["description"] = desc_el.get_text(strip=True)

        return exp

    @staticmethod
    def _parse_date_range(text: str) -> tuple[Optional[str], Optional[str]]:
        """
        解析 LinkedIn 的时间段格式
        
        输入示例：
          "2020年1月 - 2023年6月"
          "Jan 2020 - Jun 2023"
          "2020 - Present"
          "Jan 2020 - Present"
          
        输出：
          ("2020-01", "2023-06")
        """
        # 中文格式
        if "年" in text and "月" in text:
            parts = re.split(r"[–\-—~～]", text)
            if len(parts) != 2:
                return None, None
            
            start_match = re.search(r"(\d{4})年(\d{1,2})月?", parts[0].strip())
            end_match = re.search(r"(\d{4})年(\d{1,2})月?", parts[1].strip())

            start = f"{start_match.group(1)}-{start_match.group(2).zfill(2)}" if start_match else None
            
            if "Present" in parts[1] or "至今" in parts[1]:
                end = None
            else:
                end = f"{end_match.group(1)}-{end_match.group(2).zfill(2)}" if end_match else None

            return start, end

        # 英文格式
        months = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04",
            "may": "05", "jun": "06", "jul": "07", "aug": "08",
            "sep": "09", "oct": "10", "nov": "11", "dec": "12",
        }
        
        parts = re.split(r"[–\-—~～]", text)
        if len(parts) != 2:
            return None, None

        def parse_part(part: str) -> Optional[str]:
            part = part.strip()
            m = re.match(r"(\w+)\s+(\d{4})", part)
            if m:
                month_name = m.group(1).lower()[:3]
                month = months.get(month_name, "01")
                return f"{m.group(2)}-{month}"
            m = re.match(r"(\d{4})", part)
            if m:
                return f"{m.group(1)}-01"
            return None

        start = parse_part(parts[0])
        end_str = parts[1].strip()
        if "Present" in end_str or "Now" in end_str:
            end = None
        else:
            end = parse_part(end_str)

        return start, end

    @staticmethod
    def _is_current_position(end_date: Optional[str]) -> bool:
        """判断是否是当前职位"""
        return end_date is None

    @staticmethod
    def _months_between(start: str, end: Optional[str]) -> int:
        """计算两个日期之间的月数"""
        if not start:
            return 0
        
        start_dt = datetime.strptime(start, "%Y-%m")
        if end:
            end_dt = datetime.strptime(end, "%Y-%m")
        else:
            end_dt = datetime.now()

        rd = relativedelta(end_dt, start_dt)
        return rd.years * 12 + rd.months

    def _calculate_total_years(self, experiences: list[dict]) -> float:
        """计算累计工作经验年限"""
        total_months = sum(
            exp.get("duration_months", 0) for exp in experiences
        )
        return round(total_months / 12, 1)

    # ============================================================
    # 技能标签提取
    # ============================================================

    def _extract_skills(self, soup: BeautifulSoup) -> list[str]:
        """提取技能标签"""
        skills = []
        skills_section = soup.select_one("section#skills-section")
        if not skills_section:
            return skills

        skill_items = skills_section.select("span[class*='skill-name'], li[class*='skill']")
        for item in skill_items:
            skill = item.get_text(strip=True)
            if skill:
                skills.append(skill)

        return skills

    # ============================================================
    # 教育背景提取
    # ============================================================

    def _extract_education(self, soup: BeautifulSoup) -> list[dict]:
        """提取教育背景"""
        education = []
        edu_section = soup.select_one("section#education-section")
        if not edu_section:
            return education

        edu_items = edu_section.select("li[class*='profile-section-card']")
        for item in edu_items:
            try:
                school = item.select_one("h3").get_text(strip=True)
                degree = item.select_one("span[class*='degree']")
                field = item.select_one("span[class*='field-of-study']")

                edu = {
                    "school": school or "",
                    "degree": degree.get_text(strip=True) if degree else "",
                    "field": field.get_text(strip=True) if field else "",
                }
                education.append(edu)
            except Exception:
                continue

        return education

    # ============================================================
    # 错误处理
    # ============================================================

    async def _is_profile_not_found(self) -> bool:
        """检查页面是否是 'Profile Not Found'"""
        html = await self._page.content()
        not_found_signals = [
            "Profile not found",
            "This page doesn't exist",
            "Page not found",
            "该页面不存在",
        ]
        for signal in not_found_signals:
            if signal in html:
                return True
        return False
```

### 5.2 工作经历解析器

```python
"""
experience_parser.py — 高级工作经历解析

重点功能：
  1. 时间线重叠检测与合并
  2. 公司名称标准化（同公司不同写法统一）
  3. 岗位标签化（Engineering / Research / Product 分类）
  4. 连续工作经验的计算
"""

import re
from datetime import datetime
from typing import Optional
from collections import defaultdict


class ExperienceParser:
    """
    工作经历的高级解析与清洗
    """

    # 公司名称标准化映射
    COMPANY_ALIASES = {
        "Google Inc.": "Google",
        "Google LLC": "Google",
        "Google, Inc.": "Google",
        "GOOGLE": "Google",
        "Facebook": "Meta",
        "Facebook Inc.": "Meta",
        "Meta Platforms, Inc.": "Meta",
        "Apple Inc.": "Apple",
        "Apple Computer": "Apple",
        "Microsoft Corporation": "Microsoft",
        "Microsoft Corp.": "Microsoft",
        "Amazon.com": "Amazon",
        "Amazon Web Services": "Amazon",
        "AWS": "Amazon",
        "Anthropic PBC": "Anthropic",
        "Anthropic, PBC": "Anthropic",
    }

    # 岗位关键词 → 技能分类
    SKILL_CATEGORIES = {
        "infrastructure": ["infra", "infrastructure", "devops", "sre", "site reliability",
                          "platform engineering", "kubernetes", "container", "orchestration"],
        "backend": ["backend", "back-end", "server", "api", "microservice", "service",
                    "distributed systems", "distributed system"],
        "frontend": ["frontend", "front-end", "ui", "ux", "web"],
        "data": ["data engineer", "data infrastructure", "data platform", "etl", "pipeline",
                "data science", "analytics"],
        "security": ["security", "privacy", "trust", "safety", "compliance"],
        "ml_ai": ["machine learning", "deep learning", "nlp", "llm", "generative",
                  "ai engineer", "research scientist"],
        "rl": ["reinforcement learning", "rl", "rlhf"],
        "hardware": ["hardware", "fpga", "asic", "chip", "silicon", "soc"],
        "product": ["product", "pm"],
        "research": ["research scientist", "applied research", "fundamental research"],
    }

    # 方向分类
    DIRECTION_MAP = {
        "software": [
            "software engineer", "sde", "swe", "developer", "programmer",
            "backend", "frontend", "full stack", "fullstack"
        ],
        "research": [
            "research scientist", "research engineer", "applied scientist",
            "ai researcher", "ml researcher"
        ],
        "infrastructure": [
            "infrastructure", "devops", "sre", "platform engineer",
            "production engineer", "reliability engineer"
        ],
        "data": [
            "data engineer", "data scientist", "analytics engineer",
            "data infrastructure"
        ],
        "management": [
            "engineering manager", "director of engineering", "vp of engineering",
            "cto", "head of engineering"
        ],
    }

    # 资历级别标签
    SENIORITY_LEVELS = {
        "junior": ["junior", "associate", "entry", "new grad", "graduate"],
        "mid": ["software engineer", "engineer", "developer"],
        "senior": ["senior", "staff", "lead"],
        "principal": ["principal", "distinguished", "fellow"],
        "manager": ["manager", "director", "head", "vp", "cto"],
    }

    @staticmethod
    def normalize_company_name(name: str) -> str:
        """标准化公司名称"""
        name = name.strip()
        if name in ExperienceParser.COMPANY_ALIASES:
            return ExperienceParser.COMPANY_ALIASES[name]
        return name

    @staticmethod
    def classify_title(title: str) -> list[str]:
        """根据岗位名称分类方向"""
        title_lower = title.lower()
        directions = []
        
        for direction, keywords in ExperienceParser.DIRECTION_MAP.items():
            if any(kw in title_lower for kw in keywords):
                directions.append(direction)

        return directions if directions else ["other"]

    @staticmethod
    def extract_skill_tags(title: str, description: str = "") -> list[str]:
        """从岗位和描述中提取技能标签"""
        combined = f"{title} {description}".lower()
        tags = []

        for category, keywords in ExperienceParser.SKILL_CATEGORIES.items():
            if any(kw in combined for kw in keywords):
                tags.append(category)

        return tags

    @staticmethod
    def infer_seniority(title: str) -> str:
        """从岗位名称推断资历级别"""
        title_lower = title.lower()
        
        for level, keywords in ExperienceParser.SENIORITY_LEVELS.items():
            if any(kw in title_lower for kw in keywords):
                return level

        return "mid"  # 默认为中级

    @staticmethod
    def merge_overlapping(experiences: list[dict]) -> list[dict]:
        """
        合并时间重叠的工作经历
        
        LinkedIn 上很多人有重叠的兼职/顾问经历，
        按时间线连贯性合并为主要的职业经历序列。
        """
        if not experiences:
            return []

        # 按公司+岗位分组，然后按时间排序
        grouped = defaultdict(list)
        for exp in experiences:
            key = (exp.get("company"), exp.get("title"))
            grouped[key].append(exp)

        merged = []
        for key, exps in grouped.items():
            # 按开始时间排序
            sorted_exps = sorted(
                exps,
                key=lambda e: e.get("start_date") or "0000-00",
            )
            
            # 合并连续/重叠的条目
            current = sorted_exps[0].copy()
            for next_exp in sorted_exps[1:]:
                # 如果下一个的开始时间在当前结束时间之前，视为重叠
                cur_end = current.get("end_date") or "9999-12"
                next_start = next_exp.get("start_date") or "0000-00"
                
                if next_start <= cur_end:
                    # 延长当前条目的结束时间
                    if next_exp.get("end_date") and (
                        not current.get("end_date") or
                        next_exp["end_date"] > current["end_date"]
                    ):
                        current["end_date"] = next_exp["end_date"]
                else:
                    merged.append(current)
                    current = next_exp.copy()
            merged.append(current)

        return merged

    @staticmethod
    def calculate_continuous_tenure(experiences: list[dict]) -> float:
        """
        计算连续工作年限（去除同行空档期 < 3 个月）
        
        这是计算"真实工作经验"的关键指标。
        例如：间隔 2 个月的两个工作视为连续。
        """
        if not experiences:
            return 0.0

        # 按开始时间排序
        sorted_exps = sorted(
            [e for e in experiences if e.get("start_date")],
            key=lambda e: e["start_date"],
        )

        total_months = 0
        last_end = None

        for exp in sorted_exps:
            start = exp.get("start_date")
            end = exp.get("end_date")

            if not start:
                continue

            start_dt = datetime.strptime(start, "%Y-%m")
            end_dt = datetime.strptime(end, "%Y-%m") if end else datetime.now()

            if last_end:
                # 计算空档期
                gap = relativedelta(start_dt, last_end)
                gap_months = gap.years * 12 + gap.months
                # 空档期 < 3 个月视为连续
                if 0 < gap_months < 3:
                    total_months += gap_months  # 补上空档期

            duration = relativedelta(end_dt, start_dt)
            total_months += duration.years * 12 + duration.months
            last_end = end_dt

        return round(total_months / 12, 1)

    @staticmethod
    def compute_seniority_stats(experiences: list[dict]) -> dict:
        """
        计算资历统计
        
        返回：
          {
              "total_experience_years": 12.2,
              "num_positions": 6,
              "num_companies": 4,
              "avg_tenure_per_company": 2.5,
              "is_staff_level_engineer": true,
              "has_manager_experience": false,
          }
        """
        if not experiences:
            return {}

        total_years = ExperienceParser.calculate_continuous_tenure(experiences)
        companies = set(
            ExperienceParser.normalize_company_name(e.get("company", ""))
            for e in experiences if e.get("company")
        )
        current_title = experiences[0].get("title", "") if experiences else ""
        seniority = ExperienceParser.infer_seniority(current_title)
        
        titles = [e.get("title", "").lower() for e in experiences]
        management_keywords = ["manager", "director", "vp", "cto", "head of"]
        has_management = any(
            any(kw in t for kw in management_keywords) for t in titles
        )

        return {
            "total_experience_years": total_years,
            "num_positions": len(experiences),
            "num_companies": len(companies),
            "avg_tenure_per_company": round(total_years / max(len(companies), 1), 1),
            "seniority_level": seniority,
            "has_management_experience": has_management,
            "current_title": current_title,
        }
```

### 5.3 技能过滤引擎

```python
"""
skill_filter.py — 基于 Elasticsearch 风格的技能过滤引擎
"""

import re
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class SkillFilter:
    """
    技能过滤条件
    
    示例：
      filter = SkillFilter(
          must_have=["infrastructure", "backend", "distributed systems"],
          must_not=["frontend"],
          min_experience_years=8,
          preferred_directions=["infrastructure", "backend"],
      )
    """
    must_have: list[str] = field(default_factory=list)
    should_have: list[str] = field(default_factory=list)
    must_not: list[str] = field(default_factory=list)
    min_experience_years: float = 0.0
    max_experience_years: float = 50.0
    preferred_directions: list[str] = field(default_factory=list)
    preferred_companies: list[str] = field(default_factory=list)


class SkillFilterEngine:
    """
    技能过滤引擎
    
    把粗略的工作经历数据，通过多维度打分，
    过滤出符合特定人才画像的候选人。
    """

    def __init__(self):
        self._parser = ExperienceParser()

    def score_profile(
        self,
        profile: dict,
        filters: SkillFilter,
    ) -> tuple[float, dict]:
        """
        对个人资料进行多维打分
        
        Returns:
            (总分, {各维度得分明细})
        """
        experiences = profile.get("work_experiences", [])
        skills = profile.get("skills", [])
        total_years = profile.get("total_experience_years", 0)
        
        scores = {}
        
        # 1. 技能关键词匹配（40% 权重）
        skill_score = self._score_skills(experiences, skills, filters)
        scores["skill_match"] = skill_score
        
        # 2. 工作经验年限（25% 权重）
        exp_score = self._score_experience_years(total_years, filters)
        scores["experience_years"] = exp_score
        
        # 3. 方向匹配（20% 权重）
        direction_score = self._score_direction(experiences, filters)
        scores["direction_match"] = direction_score
        
        # 4. 公司背景（15% 权重）
        company_score = self._score_company_background(experiences, filters)
        scores["company_background"] = company_score
        
        # 计算加权总分
        weights = {
            "skill_match": 0.40,
            "experience_years": 0.25,
            "direction_match": 0.20,
            "company_background": 0.15,
        }
        
        total = sum(
            scores[k] * weights.get(k, 0) for k in scores
        )
        
        return total, scores

    def _score_skills(
        self,
        experiences: list[dict],
        skills: list[str],
        filters: SkillFilter,
    ) -> float:
        """技能匹配评分（0-1）"""
        # 从工作经历中提取技能标签
        all_tags = set()
        for exp in experiences:
            title = exp.get("title", "")
            desc = exp.get("description", "")
            tags = self._parser.extract_skill_tags(title, desc)
            all_tags.update(tags)
        
        all_tags.update(s.lower() for s in skills)
        
        if not filters.must_have:
            return 0.5  # 无过滤条件则中性
        
        must_lower = [m.lower() for m in filters.must_have]
        matched = sum(1 for m in must_lower if m in all_tags)
        
        if filters.must_not:
            not_lower = [n.lower() for n in filters.must_not]
            if any(n in all_tags for n in not_lower):
                return 0.0  # 触犯排除条件
        
        # 计算匹配率（考虑 must_have 全覆盖）
        if matched == len(must_lower):
            return 1.0
        elif matched > 0:
            return 0.5 * (matched / len(must_lower))
        else:
            return 0.0

    def _score_experience_years(
        self,
        years: float,
        filters: SkillFilter,
    ) -> float:
        """经验年限评分（0-1）"""
        if years == 0:
            return 0.0
        
        # 理想范围 = [min, max]
        min_years = filters.min_experience_years
        max_years = filters.max_experience_years
        
        if min_years <= years <= max_years:
            if years >= min_years + 2:  # 超出最低要求 2 年以上
                return 1.0
            else:
                return 0.6 + 0.4 * (years - min_years) / 2
        elif years < min_years:
            return max(0, 0.6 * years / min_years)
        else:
            return max(0, 0.8 - 0.3 * (years - max_years) / max_years)

    def _score_direction(
        self,
        experiences: list[dict],
        filters: SkillFilter,
    ) -> float:
        """方向匹配评分（0-1）"""
        if not filters.preferred_directions:
            return 0.5
        
        # 提取最近 3 个经历的 title
        recent_titles = [e.get("title", "") for e in experiences[:3]]
        all_directions = set()
        for title in recent_titles:
            dirs = self._parser.classify_title(title)
            all_directions.update(dirs)
        
        preferred_lower = [d.lower() for d in filters.preferred_directions]
        matched = sum(1 for d in all_directions if d.lower() in preferred_lower)
        
        if matched > 0:
            return min(1.0, matched / len(preferred_lower) + 0.3)
        return 0.0

    def _score_company_background(
        self,
        experiences: list[dict],
        filters: SkillFilter,
    ) -> float:
        """公司背景评分（0-1）"""
        if not filters.preferred_companies:
            return 0.5
        
        # 标准化公司名
        std_companies = set()
        for exp in experiences:
            std_companies.add(
                self._parser.normalize_company_name(exp.get("company", ""))
            )
        
        preferred_lower = [c.lower() for c in filters.preferred_companies]
        matched = sum(1 for c in std_companies if c.lower() in preferred_lower)
        
        if matched > 0:
            return min(1.0, 0.5 + 0.25 * matched)
        return 0.3
```

---

## 6. 数据分析管道

### 6.1 完整 Pipeline

```python
"""
analysis_pipeline.py — 数据分析完整管道

实现 Anthropic 报告分析的 4 类洞察：
  1. 资历分布（工作年限直方图、百分位）
  2. 前公司来源（人才流动 Sankey 图）
  3. 技能标签分布
  4. 学历比例
"""

import sqlite3
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np


class TalentAnalysisPipeline:
    """
    人才分析完整管道
    
    流程：
      raw_profiles (JSON) 
        → extract_profiles() 
        → profiles_df
        → extract_experiences()
        → experience_df
        → compute_metrics()
        → analytics_results
        → export_report()
    """

    def __init__(self, db_path: str = "./linkedin_data.db"):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    # ============================================================
    # 数据库初始化
    # ============================================================

    def connect(self):
        """连接 SQLite 数据库"""
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()

    def _init_schema(self):
        """初始化数据库表结构"""
        cursor = self._conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS raw_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url TEXT UNIQUE,
                name TEXT,
                headline TEXT,
                location TEXT,
                raw_json TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS work_experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER REFERENCES raw_profiles(id),
                company TEXT,
                title TEXT,
                start_date TEXT,
                end_date TEXT,
                is_current INTEGER DEFAULT 0,
                description TEXT,
                duration_months INTEGER,
                direction_tags TEXT,
                skill_tags TEXT
            );
            
            CREATE TABLE IF NOT EXISTS skills_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER REFERENCES raw_profiles(id),
                skill TEXT
            );
            
            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER REFERENCES raw_profiles(id),
                school TEXT,
                degree TEXT,
                field TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_exp_company 
                ON work_experiences(company);
            CREATE INDEX IF NOT EXISTS idx_exp_profile 
                ON work_experiences(profile_id);
            CREATE INDEX IF NOT EXISTS idx_skills_profile 
                ON skills_tags(profile_id);
        """)
        self._conn.commit()

    # ============================================================
    # 数据导入
    # ============================================================

    def import_profiles(self, profiles: list[dict]):
        """批量导入爬取的个人资料"""
        for profile in profiles:
            self._import_single_profile(profile)

    def _import_single_profile(self, profile: dict):
        """导入单条个人资料"""
        cursor = self._conn.cursor()

        # 插入基本资料
        cursor.execute("""
            INSERT OR IGNORE INTO raw_profiles 
                (profile_url, name, headline, location, raw_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            profile.get("profile_url"),
            profile.get("name"),
            profile.get("headline"),
            profile.get("location"),
            json.dumps(profile),
        ))
        profile_id = cursor.lastrowid
        if not profile_id:
            return  # 已存在

        # 插入工作经历
        for exp in profile.get("work_experiences", []):
            # 计算技能标签
            skill_tags = ExperienceParser.extract_skill_tags(
                exp.get("title", ""),
                exp.get("description", ""),
            )
            direction_tags = ExperienceParser.classify_title(
                exp.get("title", "")
            )

            cursor.execute("""
                INSERT INTO work_experiences 
                    (profile_id, company, title, start_date, end_date, 
                     is_current, description, duration_months,
                     direction_tags, skill_tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                ExperienceParser.normalize_company_name(exp.get("company", "")),
                exp.get("title"),
                exp.get("start_date"),
                exp.get("end_date"),
                int(exp.get("is_current", False)),
                exp.get("description", ""),
                exp.get("duration_months"),
                json.dumps(direction_tags),
                json.dumps(skill_tags),
            ))

        # 插入技能标签
        for skill in profile.get("skills", []):
            cursor.execute("""
                INSERT INTO skills_tags (profile_id, skill) VALUES (?, ?)
            """, (profile_id, skill))

        # 插入教育背景
        for edu in profile.get("education", []):
            cursor.execute("""
                INSERT INTO education (profile_id, school, degree, field)
                VALUES (?, ?, ?, ?)
            """, (profile_id, edu.get("school"), edu.get("degree"), edu.get("field")))

        self._conn.commit()

    # ============================================================
    # 数据分析 — 5 个核心洞察
    # ============================================================

    def compute_all_metrics(self) -> dict:
        """
        计算所有分析指标（对应 Anthropic 报告的 5 个维度）
        """
        metrics = {}
        metrics["experience_distribution"] = self._experience_distribution()
        metrics["seniority_stats"] = self._seniority_stats()
        metrics["company_sources"] = self._company_sources()
        metrics["skill_distribution"] = self._skill_distribution()
        metrics["education_stats"] = self._education_stats()
        metrics["hiring_timeline"] = self._hiring_timeline()
        return metrics

    def _experience_distribution(self) -> dict:
        """
        资历分布分析
        
        输出：
          {
              "median_years": 12.2,
              "p25_years": 8.8,
              "p75_years": 16.5,
              "histogram": { "0-3": 50, "3-6": ..., "15+": ... },
              "count_sub_3_years": 50,
              "count_above_13_years": 739,
              "pct_above_13_years": 0.44,
          }
        """
        df = pd.read_sql_query("""
            SELECT p.id, p.name,
                   SUM(w.duration_months) / 12.0 as total_years
            FROM raw_profiles p
            JOIN work_experiences w ON w.profile_id = p.id
            GROUP BY p.id
        """, self._conn)

        years = df["total_years"].dropna()

        # 分桶
        bins = [0, 3, 6, 9, 12, 15, 20, 30, 50]
        labels = ["0-3", "3-6", "6-9", "9-12", "12-15", "15-20", "20-30", "30+"]
        df["bucket"] = pd.cut(years, bins=bins, labels=labels, right=False)
        hist = df["bucket"].value_counts().sort_index().to_dict()

        return {
            "count": int(len(years)),
            "median_years": round(float(years.median()), 1),
            "mean_years": round(float(years.mean()), 1),
            "p25_years": round(float(years.quantile(0.25)), 1),
            "p75_years": round(float(years.quantile(0.75)), 1),
            "histogram": {str(k): int(v) for k, v in hist.items()},
            "count_sub_3_years": int((years < 3).sum()),
            "count_above_13_years": int((years > 13).sum()),
            "pct_above_13_years": round(float((years > 13).mean()), 3),
        }

    def _seniority_stats(self) -> dict:
        """
        资历深度分析
        
        输出：
          {
              "entry_count": 50,       # 3年以下 50人
              "entry_pct": 0.03,
              "pct_with_phd": 0.13,    # 博士比例 13%
              "pct_with_masters": 0.35,
              "pct_without_degree": 0.02,
              "median_positions": 5.5,  # 中间跳槽次数
              "median_companies": 3.2,  # 呆过几家公司
              "median_tenure_per_company": 2.8,  # 每家公司平均待多久
          }
        """
        # 学历统计
        edu_df = pd.read_sql_query("""
            SELECT p.id,
                   MAX(CASE WHEN e.degree LIKE '%PhD%' OR e.degree LIKE '%Doctor%' THEN 1 ELSE 0 END) as has_phd,
                   MAX(CASE WHEN e.degree LIKE '%Master%' OR e.degree LIKE '%MS%' OR e.degree LIKE '%MSc%' THEN 1 ELSE 0 END) as has_masters,
                   MAX(CASE WHEN e.degree LIKE '%Bachelor%' OR e.degree LIKE '%BS%' OR e.degree LIKE '%BA%' THEN 1 ELSE 0 END) as has_bachelor
            FROM raw_profiles p
            LEFT JOIN education e ON e.profile_id = p.id
            GROUP BY p.id
        """, self._conn)

        phd_count = int(edu_df["has_phd"].sum())
        total = len(edu_df)

        # 公司统计
        company_df = pd.read_sql_query("""
            SELECT profile_id, COUNT(DISTINCT company) as num_companies,
                   COUNT(*) as num_positions
            FROM work_experiences
            GROUP BY profile_id
        """, self._conn)

        return {
            "phd_count": phd_count,
            "total_count": total,
            "pct_with_phd": round(phd_count / max(total, 1), 3),
            "pct_with_masters": round(float(edu_df["has_masters"].mean()), 3),
            "pct_with_bachelor": round(float(edu_df["has_bachelor"].mean()), 3),
            "entry_count": total,
            "median_positions": round(float(company_df["num_positions"].median()), 1),
            "median_companies": round(float(company_df["num_companies"].median()), 1),
        }

    def _company_sources(self) -> dict:
        """
        前公司来源分析
        
        核心发现：
          最大的人才来源不是 OpenAI，而是 Google。
          
        输出：
          {
              "top_previous_companies": [
                  {"company": "Google", "count": 342, "pct": 20.4},
                  {"company": "Meta", "count": 198, "pct": 11.8},
                  {"company": "Amazon", "count": 156, "pct": 9.3},
                  ...
              ],
              "flow_matrix": {  # 跨公司的人才流动
                  "Google": {"Anthropic": 342, "OpenAI": 89},
                  "Meta": {"Anthropic": 198},
                  ...
              }
          }
        """
        # 查询所有非当前公司的历史经历
        df = pd.read_sql_query("""
            SELECT w.company
            FROM work_experiences w
            JOIN raw_profiles p ON p.id = w.profile_id
            WHERE w.is_current = 0
              AND w.company != ''
        """, self._conn)

        company_counts = Counter(df["company"])
        total = sum(company_counts.values())

        top_companies = []
        for company, count in company_counts.most_common(50):
            top_companies.append({
                "company": company,
                "count": count,
                "pct": round(count / max(total, 1), 3),
            })

        return {
            "total_historical_positions": total,
            "unique_companies": len(company_counts),
            "top_companies": top_companies,
        }

    def _skill_distribution(self) -> dict:
        """
        技能标签分布分析
        
        关键指标：
          - Infrastructure: 40% (最大占比)
          - Backend: ~20%
          - Security: ~20%
          - RL: 3.3% (最小)
        """
        results = self._conn.execute("""
            SELECT w.skill_tags
            FROM work_experiences w
            WHERE w.skill_tags != '[]'
              AND w.skill_tags IS NOT NULL
        """).fetchall()

        category_counts = Counter()
        for (tags_json,) in results:
            try:
                tags = json.loads(tags_json)
                for tag in tags:
                    category_counts[tag] += 1
            except (json.JSONDecodeError, TypeError):
                continue

        total_occurrences = sum(category_counts.values())
        distribution = []
        for category, count in category_counts.most_common():
            distribution.append({
                "category": category,
                "count": count,
                "pct": round(count / max(total_occurrences, 1), 3),
            })

        return distribution

    def _education_stats(self) -> dict:
        """学历统计"""
        df = pd.read_sql_query("""
            SELECT p.id,
                   GROUP_CONCAT(e.degree, ' || ') as degrees,
                   GROUP_CONCAT(e.school, ' || ') as schools
            FROM raw_profiles p
            LEFT JOIN education e ON e.profile_id = p.id
            GROUP BY p.id
        """, self._conn)

        # 学位分类
        phd_count = 0
        masters_count = 0
        bachelors_count = 0
        no_degree = 0

        for _, row in df.iterrows():
            degrees = str(row.get("degrees", ""))
            if not degrees or degrees == "None":
                no_degree += 1
                continue
            if "PhD" in degrees or "Doctor" in degrees:
                phd_count += 1
            if "Master" in degrees or "MS" in degrees or "MSc" in degrees:
                masters_count += 1
            if "Bachelor" in degrees or "BS" in degrees or "BA" in degrees:
                bachelors_count += 1

        total = len(df)

        return {
            "total_profiles": total,
            "phd": {"count": phd_count, "pct": round(phd_count / max(total, 1), 3)},
            "masters": {"count": masters_count, "pct": round(masters_count / max(total, 1), 3)},
            "bachelor": {"count": bachelors_count, "pct": round(bachelors_count / max(total, 1), 3)},
            "no_degree_listed": {"count": no_degree, "pct": round(no_degree / max(total, 1), 3)},
        }

    def _hiring_timeline(self) -> dict:
        """
        招聘时间线分析
        
        基于入职时间的推断分析。
        
        由于 LinkedIn 不直接显示入职公司的时间，
        通过推断第一份非当前岗位到当前岗位的切换时间估算。
        """
        # 对于有当前岗位且不是最早期的人，
        # 判断当前公司的最早任职时间
        df = pd.read_sql_query("""
            SELECT p.id,
                   MIN(w.start_date) as first_at_current_company,
                   COUNT(*) as positions_at_current
            FROM raw_profiles p
            JOIN work_experiences w ON w.profile_id = p.id
            WHERE w.is_current = 1
            GROUP BY p.id
            HAVING first_at_current_company IS NOT NULL
        """, self._conn)

        # 按年份统计
        yearly_hires = Counter()
        for _, row in df.iterrows():
            year_str = str(row["first_at_current_company"])[:4]
            if year_str.isdigit():
                yearly_hires[int(year_str)] += 1

        timeline = []
        for year in sorted(yearly_hires.keys()):
            timeline.append({
                "year": year,
                "hires": yearly_hires[year],
            })

        return {
            "total_tracked": len(df),
            "yearly_hires": timeline,
            "hires_past_12_months": sum(
                v for k, v in yearly_hires.items()
                if k >= datetime.now().year - 1
            ),
        }

    # ============================================================
    # 报告生成
    # ============================================================

    def generate_report(self, output_path: str = "./talent_analysis_report.md") -> str:
        """生成 Markdown 分析报告"""
        metrics = self.compute_all_metrics()

        lines = []
        lines.append("# 人才结构分析报告\n")
        lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

        # 1. 资历分布
        exp = metrics["experience_distribution"]
        lines.append("## 📊 资历分布\n")
        lines.append(f"- **中位工作经验**: {exp['median_years']} 年")
        lines.append(f"- **均值工作经验**: {exp['mean_years']} 年")
        lines.append(f"- **P25-P75 区间**: {exp['p25_years']} - {exp['p75_years']} 年")
        lines.append(f"- **工作 < 3 年的人数**: {exp['count_sub_3_years']} 人")
        lines.append(f"- **工作 > 13 年的人数**: {exp['count_above_13_years']} 人 ({exp['pct_above_13_years']*100:.1f}%)\n")

        lines.append("| 年限区间 | 人数 |")
        lines.append("|:---------|:---:|")
        for bucket, count in exp["histogram"].items():
            bar = "█" * min(count // 5, 40)
            lines.append(f"| {bucket} 年 | {count} {bar} |")

        # 2. 前公司来源
        sources = metrics["company_sources"]
        lines.append("\n\n## 🏢 前公司来源\n")
        lines.append(f"- **总历史岗位数**: {sources['total_historical_positions']}")
        lines.append(f"- **涉及的独立公司数**: {sources['unique_companies']}\n")

        lines.append("| 排名 | 前公司 | 人数 | 占比 |")
        lines.append("|:----:|:-------|:---:|:----:|")
        for i, comp in enumerate(sources["top_companies"][:15], 1):
            bar = "█" * min(int(comp["pct"] * 100), 40)
            lines.append(f"| {i} | {comp['company']} | {comp['count']} | {comp['pct']*100:.1f}% {bar} |")

        # 3. 技能分布
        skills = metrics["skill_distribution"]
        lines.append("\n\n## 🛠️ 技能分布\n")
        lines.append("| 技能方向 | 出现次数 | 占比 |")
        lines.append("|:---------|:-------:|:----:|")
        for skill in skills:
            bar = "█" * min(int(skill["pct"] * 100), 40)
            lines.append(f"| {skill['category']} | {skill['count']} | {skill['pct']*100:.1f}% {bar} |")

        # 4. 学历统计
        edu = metrics["education_stats"]
        lines.append("\n\n## 🎓 学历分布\n")
        lines.append(f"- **博士**: {edu['phd']['count']} 人 ({edu['phd']['pct']*100:.1f}%)")
        lines.append(f"- **硕士**: {edu['masters']['count']} 人 ({edu['masters']['pct']*100:.1f}%)")
        lines.append(f"- **学士**: {edu['bachelor']['count']} 人 ({edu['bachelor']['pct']*100:.1f}%)")
        lines.append(f"- **未列出**: {edu['no_degree_listed']['count']} 人\n")

        # 5. 招聘时间线
        timeline = metrics["hiring_timeline"]
        lines.append("\n\n## 📅 招聘时间线\n")
        for entry in timeline["yearly_hires"]:
            bar = "█" * min(entry["hires"] // 5, 60)
            lines.append(f"- {entry['year']}: {entry['hires']} 人 {bar}")

        report = "\n".join(lines)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        return output_path

    def close(self):
        if self._conn:
            self._conn.close()
```

### 6.2 可视化输出

```python
"""
visualization.py — 分析结果可视化
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns


class TalentVisualizer:
    """人才分析结果的可视化生成器"""

    def __init__(self, output_dir: str = "./visualizations"):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置中文字体
        plt.rcParams["font.family"] = "DejaVu Sans"
        
        # Anthropic 风格配色
        self._colors = {
            "primary": "#1a73e8",
            "secondary": "#ea4335",
            "accent": "#34a853",
            "neutral": "#5f6368",
            "background": "#f8f9fa",
        }

    def plot_experience_histogram(self, years: list[float]) -> str:
        """资历分布直方图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bins = np.arange(0, 35, 2)
        ax.hist(years, bins=bins, color=self._colors["primary"],
                edgecolor="white", alpha=0.85)
        
        # 标注中位数
        median = np.median(years)
        ax.axvline(median, color=self._colors["secondary"],
                   linestyle="--", linewidth=2, label=f"中位数 = {median:.1f} 年")
        
        ax.set_xlabel("工作经验年限", fontsize=12)
        ax.set_ylabel("人数", fontsize=12)
        ax.set_title("人才资历分布", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
        
        path = self._output_dir / "experience_distribution.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(path)

    def plot_company_source_bar(self, companies: list[dict], top_n: int = 15) -> str:
        """前公司来源柱状图"""
        top = companies[:top_n]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        names = [c["company"] for c in top]
        values = [c["count"] for c in top]
        
        bars = ax.barh(range(len(names)), values, color=self._colors["primary"])
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        ax.invert_yaxis()
        
        # 标注数值
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                    str(val), va="center", fontsize=9)
        
        ax.set_xlabel("人数", fontsize=12)
        ax.set_title("前公司人才来源 Top 15", fontsize=14, fontweight="bold")
        
        path = self._output_dir / "company_sources.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(path)

    def plot_skill_distribution(self, skills: list[dict]) -> str:
        """技能分布水平柱状图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        names = [s["category"] for s in skills]
        values = [s["pct"] * 100 for s in skills]
        
        colors = [self._colors["primary"] if v > 10
                  else self._colors["neutral"] for v in values]
        
        bars = ax.barh(range(len(names)), values, color=colors)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        ax.invert_yaxis()
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f"{val:.1f}%", va="center", fontsize=9)
        
        ax.set_xlabel("出现频率 (%)", fontsize=12)
        ax.set_title("技能标签分布", fontsize=14, fontweight="bold")
        
        path = self._output_dir / "skill_distribution.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(path)

    def plot_hiring_timeline(self, timeline: list[dict]) -> str:
        """招聘时间线折线图"""
        fig, ax = plt.subplots(figsize=(12, 5))
        
        years = [t["year"] for t in timeline]
        hires = [t["hires"] for t in timeline]
        
        ax.plot(years, hires, marker="o", linewidth=2.5,
                color=self._colors["primary"], markersize=8)
        ax.fill_between(years, hires, alpha=0.15, color=self._colors["primary"])
        
        ax.set_xlabel("年份", fontsize=12)
        ax.set_ylabel("新增员工数", fontsize=12)
        ax.set_title("年度招聘趋势", fontsize=14, fontweight="bold")
        ax.grid(alpha=0.3)
        
        path = self._output_dir / "hiring_timeline.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(path)

    def plot_education_pie(self, edu_stats: dict) -> str:
        """学历分布饼图"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels = ["博士 (PhD)", "硕士 (Master)", "学士 (Bachelor)", "未列出"]
        sizes = [
            edu_stats["phd"]["pct"],
            edu_stats["masters"]["pct"],
            edu_stats["bachelor"]["pct"],
            edu_stats["no_degree_listed"]["pct"],
        ]
        colors = [self._colors["primary"], self._colors["accent"],
                  self._colors["neutral"], "#dadce0"]
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%",
            colors=colors, startangle=90,
            textprops={"fontsize": 11},
        )
        ax.set_title("学历分布", fontsize=14, fontweight="bold")
        
        path = self._output_dir / "education_distribution.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(path)
```

---

## 7. 部署与运维

### 7.1 完整启动脚本

```python
"""
main.py — LinkedIn 爬虫主入口

使用方式：
  python main.py --company Anthropic --keywords "Software Engineer" "Infrastructure" --max 2000 --headless
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# 所有模块的导入
from fingerprint_engine import FingerprintManager
from proxy_pool import ProxyPool
from rate_limiter import AdaptiveRateLimiter, RateLimitTier
from session_manager import SessionStore
from browser_engine import LinkedInBrowser
from account_manager import AccountRotator, LinkedInAccount
from linkedin_searcher import LinkedInCompanySearcher
from google_dork import GoogleDorkEngine
from voyager_api import LinkedInVoyagerAPI
from discovery_orchestrator import DiscoveryOrchestrator
from profile_extractor import ProfileExtractor
from experience_parser import ExperienceParser
from skill_filter import SkillFilter, SkillFilterEngine
from analysis_pipeline import TalentAnalysisPipeline
from visualization import TalentVisualizer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("./crawler.log"),
    ],
)
logger = logging.getLogger(__name__)


async def main(args):
    """爬虫主流程"""
    logger.info(f"Starting LinkedIn crawler for company: {args.company}")
    
    # ── 1. 初始化基础设施 ──────────────────────────────────
    fp_manager = FingerprintManager()
    proxy_pool = ProxyPool(min_pool_size=10)
    rate_limiter = AdaptiveRateLimiter()
    session_store = SessionStore(storage_dir="./sessions")
    
    # 添加代理（实际使用时应替换为真实代理）
    # proxy_pool.add_proxy(...)
    
    # ── 2. 账号管理 ────────────────────────────────────────
    accounts = [
        LinkedInAccount(
            email="your_email@gmail.com",
            password="your_password",
        ),
        # 多个账号轮流使用
        # LinkedInAccount(email="acc2@gmail.com", password="..."),
    ]
    account_rotator = AccountRotator(accounts)
    
    # ── 3. 启动浏览器 ──────────────────────────────────────
    browser = LinkedInBrowser(
        fingerprint_mgr=fp_manager,
        proxy_pool=proxy_pool,
        session_store=session_store,
        headless=args.headless,
    )
    await browser.start()
    
    # 获取第一个可用账号
    account = account_rotator.get_next_account()
    if not account:
        logger.error("No available accounts")
        return
    
    await browser.create_linkedin_context(account.email)
    login_success = await browser.login(account.email, account.password)
    
    if not login_success:
        logger.error("Login failed or requires manual intervention")
        # 进行截图，方便人工处理
        await browser._page.screenshot(path="./login_failed.png")
        return
    
    logger.info("Login successful")
    
    # ── 4. 人才发现 ────────────────────────────────────────
    li_searcher = LinkedInCompanySearcher(browser, rate_limiter)
    google_dork = GoogleDorkEngine(browser._page, rate_limiter)
    voyager_api = LinkedInVoyagerAPI(browser, rate_limiter)
    await voyager_api.initialize()
    
    orchestrator = DiscoveryOrchestrator(li_searcher, google_dork, voyager_api, rate_limiter)
    
    discovered_urls = await orchestrator.discover_all(
        company=args.company,
        keywords=args.keywords,
        max_profiles=args.max_profiles,
    )
    
    logger.info(f"Discovered {len(discovered_urls)} profile URLs")
    
    # ── 5. 资料提取 ────────────────────────────────────────
    extractor = ProfileExtractor(browser, rate_limiter)
    profiles = []
    
    for i, url in enumerate(discovered_urls[:args.max_profiles]):
        try:
            profile = await extractor.extract_profile(url)
            if profile:
                profiles.append(profile)
                logger.info(f"  [{i+1}/{len(discovered_urls)}] Extracted: {profile.get('name', 'unknown')}")
            
            # 每 50 个保存一次中间结果
            if (i + 1) % 50 == 0:
                _save_intermediate(profiles, f"./checkpoint_{i+1}.json")
        except Exception as e:
            logger.warning(f"  Failed to extract {url}: {e}")
            # 如果连续失败超过 5 次，切换账号
            continue
    
    logger.info(f"Successfully extracted {len(profiles)} profiles")
    
    # ── 6. 数据分析 ────────────────────────────────────────
    pipeline = TalentAnalysisPipeline(db_path="./linkedin_data.db")
    pipeline.connect()
    pipeline.import_profiles(profiles)
    
    metrics = pipeline.compute_all_metrics()
    report_path = pipeline.generate_report("./talent_analysis_report.md")
    logger.info(f"Report generated: {report_path}")
    
    # 可视化
    visualizer = TalentVisualizer(output_dir="./visualizations")
    # 生成图表...
    
    # ── 7. 清理 ────────────────────────────────────────────
    pipeline.close()
    await browser.close()
    
    logger.info("Crawler completed successfully")


def _save_intermediate(profiles: list[dict], path: str):
    """保存中间结果"""
    import json
    with open(path, "w") as f:
        json.dump(profiles, f, indent=2, default=str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Talent Crawler")
    parser.add_argument("--company", type=str, default="Anthropic",
                        help="Company name to crawl")
    parser.add_argument("--keywords", type=str, nargs="+",
                        default=["Software Engineer", "Infrastructure"],
                        help="Search keywords")
    parser.add_argument("--max-profiles", type=int, default=2000,
                        help="Maximum profiles to extract")
    parser.add_argument("--headless", action="store_true",
                        help="Run browser in headless mode")
    parser.add_argument("--proxy-file", type=str, default=None,
                        help="Proxy list file")
    
    args = parser.parse_args()
    asyncio.run(main(args))
```

### 7.2 Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

# 安装 Playwright 依赖
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium

# 应用代码
COPY . /app
WORKDIR /app

# 数据卷
VOLUME ["/app/data", "/app/sessions", "/app/visualizations"]

# 默认配置
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
```

```txt
# requirements.txt
playwright>=1.40.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
aiohttp>=3.9.0
python-dateutil>=2.8.0
```

---

## 延伸阅读

### 反检测技术演进方向

| 技术 | 当前状态 | 未来方向 |
|:-----|:---------|:---------|
| **指纹模拟** | 基于模板匹配（每会话一个固定指纹） | 动态指纹生成（每页面请求可变指纹） |
| **行为模拟** | 基于随机间隔的人类行为模拟 | 机器学习生成的人类行为模型（GAN） |
| **代理策略** | 静态代理池 + 轮换 | 基于强化学习的动态代理选择 |
| **CAPTCHA 处理** | 人工介入 | 视觉识别 + 行为推理 |
| **验证码短信** | 手动输入 | 自动化短信接收服务 |

### LinkedIn 反爬等级对照

| 反爬等级 | 行为特征 | 惩罚措施 | 恢复方法 |
|:---------|:---------|:---------|:---------|
| **L1: 速率限制** | 100+ 请求/分钟 | 429 Too Many Requests | 冷却 30-60 秒 |
| **L2: 账号限制** | 200+ 资料查看/天 | "Unusual activity" 弹窗 | 邮件验证重置 |
| **L3: 会话封禁** | 多个账号相同 IP | 403 Forbidden | 换 IP + 新 session |
| **L4: 账号锁定** | 频繁触发 L2 | 要求修改密码 | 修改密码 + 冷却 24h |
| **L5: 设备指纹封禁** | 检测到 Selenium/Puppeteer | 直接空结果 | 换指纹 + 干净 IP |

### 与 Anthropic 分析的数据规模对比

| 指标 | Milan Griffes（原版） | 本架构目标 |
|:-----|:----------------------|:-----------|
| 爬取员工总数 | 5,306 人 | 5,000-10,000 人 |
| 过滤工程师数 | 1,680 人 | 1,500-3,000 人 |
| 历史岗位记录 | 7,986 段 | 10,000+ 段 |
| 爬取时间 | 未知（可能 1-2 周） | 2-7 天（多账号并行） |
| 准确率 | 手工验证 | ~85-95%（需抽样验证） |
