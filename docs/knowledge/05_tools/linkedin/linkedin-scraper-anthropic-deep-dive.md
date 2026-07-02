# LinkedIn 爬虫参考实现：Anthropic 人才分析用例驱动版

> **前置**: 通用架构见 `linkedin-scraper-architecture.md`（3608 行），本文聚焦**数据产出需求驱动的后三部分深度设计**
> **数据驱动目标**: 5,306 profiles → 过滤 1,680 工程师 → 提取 7,986 段工作经历 → 产出 4 类分析洞察
> **免责声明**: 本文仅供技术研究与数据分析学习参考

---

## 📐 目录

1. [设计方法论：数据需求驱动架构](#1-设计方法论数据需求驱动架构)
2. [Part 3: 人才发现引擎](#2-人才发现引擎)
3. [Part 4: 个人资料抽取器](#3-个人资料抽取器)
4. [Part 5: 数据分析管道](#4-数据分析管道)
5. [完整 Pipeline 编排](#5-完整-pipeline-编排)
6. [风险研判与边界条件](#6-风险研判与边界条件)

---

## 1. 设计方法论：数据需求驱动架构

### 1.1 从分析目标倒推工程需求

Anthropic 案例中，Milan Griffes 产出 4 类核心洞察。每类洞察对数据采集有不同精度要求：

| # | 分析目标 | 所需数据字段 | 最低精度 | 样本量需求 |
|:-:|:---------|:-----------|:---------|:----------|
| ① | **资历分布**（中位数 12.2 年） | 每段工作经历的起止时间 | **月级**精度（年级不够） | ≥1,500 人 |
| ② | **前公司来源**（Google 18-22%） | 每段经历的公司名称 | 公司名标准化后 95%+ 准确 | ≥1,500 人 |
| ③ | **技能堆叠**（Infra 40%） | Profile 中的技能标签列表 | 标签分类映射准确 | ≥1,500 人 |
| ④ | **学历比例**（博士 13%） | 教育背景中的学位信息 | 学位提取 90%+ 召回 | ≥1,500 人 |

**关键推论**: Anhtropic 报告共 5,306 条原始 profiles，过滤后 1,680 名工程师。这意味着：
- 初始采集量 ≈ 最终分析量的 **3.2×**（因公司员工含非工程岗：运营/HR/销售）
- 每条 profile 的完整采集耗时 ≈ 2-8 秒（含限速）+ DOM 渲染 ≈ 10-30 秒
- 5,306 × 15s ≈ **22 小时** 纯爬取时间（单账号，不含失败重试）

### 1.2 工程约束矩阵

从分析目标出发，得到以下工程约束：

```
分析精度需求
    ├── 工作年限精度 → 需要月级日期解析，不能仅用"年"字段
    ├── 前后公司连续性 → 需要正确处理时间重叠（兼职、顾问）
    └── 技能标签聚类 → 需要标准化映射（如 "K8s" ≡ "Kubernetes"）
         ↓
数据采集约束
    ├── 5,306 条 → 需要 3 条发现路径（单一路径不够）
    ├── 1,680 工程师过滤 → Profile 必须包含 headeline 解析
    └── 高精度抽取 → DOM 解析比 API 更可靠（但更慢）
         ↓
系统反爬约束
    ├── LinkedIn 速率限制 → 自适应限速器 + 多账号轮换
    ├── 浏览器指纹检测 → stealth 补丁 + 指纹轮换
    └── 行为模式检测 → 人类行为模拟（随机延迟、鼠标轨迹）
```

### 1.3 数据质量目标

针对 Anthropic 分析的质量要求，定义以下指标：

| 指标 | 目标值 | 未达标影响 |
|:----|:------|:----------|
| Profile 解析成功率 | ≥95% | 样本偏差（被 ban 的账号可能集中在特定人群） |
| 工作年限日期提取率 | ≥98% | 中位数失真 |
| 公司名标准化准确率 | ≥97% | 前公司排名错误 |
| 技能标签召回率 | ≥85% | Top 20 技能排名不准确 |
| 学位提取召回率 | ≥90% | 博士占比估算误差 |
| 去重率 | 100%（URL 级） | 同一人多条致统计偏差 |

---

## 2. 人才发现引擎

### 2.1 从数据需求推导发现策略

Anthropic 5,306 条 profiles 的发现需要覆盖：

```
目标公司员工总数 ~3,000 人（含所有工种）
  ├── 工程团队 ~1,680 人（分析目标）
  ├── 研究团队 ~200 人
  ├── 产品/设计 ~200 人
  ├── 商业/销售 ~250 人
  ├── 运营/人事 ~200 人
  └── 政策/安全 ~100 人
```

三条发现路径的覆盖能力：

| 路径 | 单账号日产能 | 5,306 条达标所需天数 | 风险等级 | 补充能力 |
|:-----|:-----------|:-------------------|:--------|:--------|
| **A: LinkedIn 搜索** | 500-800 URLs/天 | 7-10 天 | ⚠️ 中等 | 精确过滤（可按公司+岗位） |
| **B: Google Dork** | 300-500 URLs/天 | 10-18 天 | ✅ 低 | 无需登录，适合初始扫描 |
| **C: Voyager API** | 1,000-2,000/天 | 3-5 天 | 🔴 高 | 快，但端点易变且限速严格 |

**设计决策**: 三路并行，各司其职
- B 做**初始批量扫描**（快速获取 URL 池）
- A 做**精准补漏**（按岗位关键词过滤，覆盖工程团队）
- C 做**详情提取**（不用于发现，用于获取已发现 URL 的详细信息）

### 2.2 路径 A：LinkedIn 搜索（核心路径）

#### 2.2.1 工程岗位关键词体系

Anthropic 分析的核心是过滤出 **工程师**。基于其技能分布，定义以下分类体系：

```python
# engineer_keywords.py — 工程岗位关键词分类体系

# === 第一层：岗位大类 ===
ENGINEERING_TITLES = {
    "infrastructure": [
        "infrastructure engineer", "sre", "site reliability",
        "platform engineer", "devops engineer", "cloud engineer",
        "systems engineer", "production engineer",
    ],
    "backend": [
        "software engineer", "backend engineer", "back-end engineer",
        "software developer", "full stack engineer",
    ],
    "distributed_systems": [
        "distributed systems engineer", "data infrastructure",
        "storage engineer", "database engineer",
        "compute engineer", "network engineer",
    ],
    "security": [
        "security engineer", "security researcher",
        "appsec", "security software engineer",
        "trust and safety engineer",
    ],
    "ml_ai": [
        "machine learning engineer", "ml engineer",
        "ai engineer", "deep learning engineer",
        "llm engineer",
    ],
    "agent": [
        "agent engineer", "agent runtime",
        "agent platform engineer", "agent infra",
    ],
    "data": [
        "data engineer", "analytics engineer",
        "data platform engineer",
    ],
}

# === 第二层：工程师 vs 非工程师的判别规则 ===
NON_ENGINEER_PATTERNS = [
    r"recruit", r"talent\s*(acquisition|partner)",
    r"hr", r"people\s*(ops|partner|team)",
    r"marketing", r"brand", r"communications",
    r"sales", r"account\s*(executive|manager)",
    r"finance", r"accountant", r"controller",
    r"legal", r"counsel", r"paralegal",
    r"office\s*manager", r"administrative",
    r"customer\s*success", r"support\s*engineer",  # 技术支持非研发工程
    r"technical\s*writer", r"content\s*strategist",
    r"designer", r"ux", r"ui", r"product\s*design",
    r"program\s*manager(?!\s*technical)",  # 非技术项目经理
    r"operations\s*(manager|specialist)",
]

def classify_engineer_role(headline: str) -> tuple[bool, str]:
    """
    根据 headline 判断是否属于工程师类别
    
    Returns:
        (is_engineer, category)
    """
    headline_lower = headline.lower()
    
    # 先排除非工程师模式
    for pattern in NON_ENGINEER_PATTERNS:
        if re.search(pattern, headline_lower):
            return False, "non_engineer"
    
    # 再匹配工程岗位
    for category, titles in ENGINEERING_TITLES.items():
        for title in titles:
            if title in headline_lower:
                return True, category
    
    # 无法判断时保守处理：保留（后续通过技能标签二次过滤）
    return True, "unclassified"
```

#### 2.2.2 搜索策略

```python
"""
linkedin_searcher_v2.py — Anthropic 用例优化的 LinkedIn 搜索

与通用版的关键差异：
  1. 岗位关键词按工程分类体系组织（便于统计分布）
  2. 支持公司+岗位+地点的布尔组合搜索
  3. 分阶段搜索（先扩面、再精筛）
  4. 集成实时分类过滤（不浪费 quota 在非工程师上）
"""

class AnthropicCompanySearcher:
    """
    面向 Anthropic 分析的搜索器
    
    搜索策略（经验证）：
      - Phase 1: 按公司名 + "software engineer" 搜索 → 获取 60-70% 面
      - Phase 2: 按公司名 + "infrastructure" / "sre" 搜索 → 补充 infra 类
      - Phase 3: 按公司名 + "security" / "agent" 搜索 → 补充小众类别
      - Phase 4: 无关键词搜索剩余员工 → 全覆盖
    """

    SEARCH_PHASES = [
        {"keywords": ["Software Engineer", "Software Developer"], "max_pages": 30},
        {"keywords": ["Infrastructure", "SRE", "Platform Engineer"], "max_pages": 20},
        {"keywords": ["Security Engineer", "Security Researcher"], "max_pages": 15},
        {"keywords": ["Machine Learning Engineer", "ML Engineer"], "max_pages": 15},
        {"keywords": ["Data Engineer", "Data Infrastructure"], "max_pages": 10},
        {"keywords": ["Agent Engineer", "Staff Engineer", "Principal Engineer"], "max_pages": 10},
        # Phase 7: 无关键词 — 获取剩余未覆盖的员工
        {"keywords": [], "max_pages": 10},
    ]

    def __init__(self, browser, rate_limiter):
        self._browser = browser
        self._rate_limiter = rate_limiter
        self._page = browser._page
        self._seen_urls: set[str] = set()

    async def discover_engineering_team(
        self,
        company: str,
        max_profiles: int = 2000,
    ) -> list[dict]:
        """
        分阶段搜索某公司的工程团队
        
        Anthropic 场景输入:
          company = "Anthropic"
          max_profiles = 2000 (目标 1680 人，留 20% 冗余)
        
        产出格式（直接对接 Profile 抽取器）:
          [
            {"name": "John Doe", "url": "...", "headline": "...",
             "is_engineer": True, "category": "infrastructure"},
            ...
          ]
        """
        results = []
        
        for phase_idx, phase in enumerate(self.SEARCH_PHASES):
            if len(results) >= max_profiles:
                break
            
            logging.info(f"Phase {phase_idx + 1}: keywords={phase['keywords'] or 'all'}")
            
            async for result in self._search_phase(
                company=company,
                keywords=phase["keywords"],
                max_pages=phase["max_pages"],
            ):
                # 实时分类 + 去重
                if result["url"] in self._seen_urls:
                    continue
                self._seen_urls.add(result["url"])
                
                is_eng, category = classify_engineer_role(result["headline"])
                result["is_engineer"] = is_eng
                result["engineer_category"] = category
                
                results.append(result)
                
                if len(results) >= max_profiles:
                    break
            
            logging.info(f"  → Found {len(results)} so far "
                         f"({sum(1 for r in results if r['is_engineer'])} engineers)")
        
        return results

    async def _search_phase(self, company: str, keywords: list[str],
                            max_pages: int) -> AsyncGenerator[dict, None]:
        """执行单个搜索阶段"""
        await self._rate_limiter.wait_if_needed(RateLimitTier.SEARCH)
        
        # 构造搜索 URL
        params = {
            "origin": "FACETED_SEARCH",
            "currentCompany": company,
        }
        if keywords:
            # 使用布尔 OR 组合关键词
            params["keywords"] = " OR ".join(f'"{kw}"' for kw in keywords)
        
        search_url = f"https://www.linkedin.com/search/results/people/?{urlencode(params)}"
        
        await self._page.goto(search_url, wait_until="networkidle")
        await asyncio.sleep(random.uniform(3, 5))
        
        for page_num in range(1, max_pages + 1):
            results = await self._parse_search_page()
            for r in results:
                yield r
            
            # 翻页
            if not await self._has_next_page():
                break
            await self._click_next()
        
    async def _parse_search_page(self) -> list[dict]:
        """
        解析搜索页面 — 增强版
        
        相比通用版，额外提取 headline 用于实时分类
        """
        html = await self._page.content()
        soup = BeautifulSoup(html, "lxml")
        
        results = []
        for card in soup.select("[data-view-name='search-entity-result']"):
            try:
                url_el = card.select_one("a[href*='/in/']")
                name_el = card.select_one("span[dir='ltr']")
                title_el = card.select_one(
                    "div[class*='entity-result__primary-subtitle']"
                )
                
                if not url_el:
                    continue
                    
                url = url_el.get("href", "")
                url_match = re.search(r"(/in/[^/?]+)", url)
                if not url_match:
                    continue
                
                results.append({
                    "name": name_el.get_text(strip=True) if name_el else "",
                    "url": f"https://www.linkedin.com{url_match.group(1)}",
                    "headline": title_el.get_text(strip=True) if title_el else "",
                })
            except Exception:
                continue
        
        return results

    async def _has_next_page(self) -> bool:
        btn = await self._page.query_selector("button[aria-label='Next']")
        if not btn:
            return False
        return not await btn.get_attribute("disabled")

    async def _click_next(self):
        await self._browser.human_mouse_move(self._page)
        await asyncio.sleep(random.uniform(2, 4))
        btn = await self._page.query_selector("button[aria-label='Next']")
        if btn:
            await btn.click()
            await self._page.wait_for_load_state("networkidle")
            await asyncio.sleep(random.uniform(1, 3))
```

### 2.3 路径 B：Google Dork（低风险初始扫描）

#### 2.3.1 Anthropic 场景的 Dork 策略

Google Dork 的核心作用不是替代 LinkedIn 搜索，而是 **在登录 LinkedIn 之前先建立基础 URL 池**，降低对 LinkedIn 搜索的依赖度。

```python
"""
google_dork_v2.py — Anthropic 用例 Dork 策略

设计原则：
  1. 先用 Dork 获取 20-30% 的 URL（约 1000-1500 条）
  2. 这些 URL 用于预热 Profile 抽取器
  3. LinkedIn 搜索只做"补充"而非"主路径"
"""

class AnthropicDorkEngine:
    """
    Anthropic 公司人才 Dork 发现引擎
    """

    # 多组 Dork 查询模板（轮换使用，避免 Google 检测模式）
    DORK_TEMPLATES = [
        # 模板 1：基础公司名
        'site:linkedin.com/in "{company}"',
        # 模板 2：公司名 + 工程师
        'site:linkedin.com/in "{company}" "engineer"',
        # 模板 3：公司名 + 特定技能（针对 Infra 标签）
        'site:linkedin.com/in "{company}" "infrastructure" -recruiter',
        # 模板 4：公司名 + 地点（旧金山）
        'site:linkedin.com/in "{company}" "San Francisco" "engineer"',
        # 模板 5：排除干扰人员
        'site:linkedin.com/in "{company}" (-recruiter -"talent acquisition" -hr)',
        # 模板 6：细分技能
        'site:linkedin.com/in "{company}" "distributed systems" OR "kubernetes"',
        # 模板 7：前员工模式（用于交叉验证来源公司）  
        'site:linkedin.com/in "formerly {company}" "engineer"',
        # 模板 8：纯 In 模式
        'site:linkedin.com/in "{company}" -recruiter -headhunter -"talent"',
    ]

    def __init__(self, page, rate_limiter):
        self._page = page
        self._rate_limiter = rate_limiter

    async def discover(
        self,
        company: str,
        max_results: int = 3000,
        templates: list[str] = None,
    ) -> set[str]:
        """
        多模板扫描，覆盖不同角度

        Anthropic 场景经验值：
          - 8 个模板轮换，每个约 200-400 条
          - 总 URL ≈ 1,500-2,500 条（去重后 ≈ 1,200-1,800）
          - 其中工程师比例 ≈ 50-60%（对比 LinkedIn 搜索的 70-80%）
        
        投入产出比决策：
          - Google Dork 投入：~3-4 小时
          - LinkedIn 搜索投入：~8-10 小时  
          Dork 先做 3 小时，减少 LinkedIn 搜索 4-5 小时需求量
        """
        all_urls: set[str] = set()
        templates = templates or self.DORK_TEMPLATES

        for i, template in enumerate(templates):
            if len(all_urls) >= max_results:
                break
            
            query = template.format(company=company)
            urls = await self._execute_single_dork(query, max_results // len(templates))
            all_urls.update(urls)
            
            logging.info(f"  Dork[{i}]: {len(urls)} urls → total {len(all_urls)}")
            
            # 模板间等待（避免 Google 检测模式）
            await asyncio.sleep(random.uniform(30, 60))

        return all_urls

    async def _execute_single_dork(
        self, query: str, max_results: int
    ) -> set[str]:
        """执行单个 Dork 查询"""
        urls: set[str] = set()
        results_per_page = 10
        max_pages = min(max_results // results_per_page + 1, 20)

        for page_num in range(max_pages):
            await self._rate_limiter.wait_if_needed(RateLimitTier.PAGE)
            
            start = page_num * results_per_page
            search_url = (
                f"https://www.google.com/search"
                f"?q={quote(query)}&start={start}&num={results_per_page}"
            )
            
            await self._page.goto(search_url, wait_until="networkidle")
            await asyncio.sleep(random.uniform(2, 4))
            
            html = await self._page.content()
            page_urls = self._extract_linkedin_urls(html)
            urls.update(page_urls)
            
            if not await self._has_next():
                break
        
        return urls

    @staticmethod
    def _extract_linkedin_urls(html: str) -> set[str]:
        """从 Google 结果提取 LinkedIn 资料 URL"""
        pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w-]+'
        urls = set()
        for url in re.findall(pattern, html):
            url = url.rstrip("/").split("?")[0]
            urls.add(url)
        return urls

    async def _has_next(self) -> bool:
        return await self._page.query_selector("a#pnnext") is not None
```

### 2.4 路径 C：Voyager API（高效详情获取）

#### 2.4.1 为什么 API 适合详情获取而非发现

Anthropic 场景中，Voyager API 的角色：

```
+-------------------+------------------+------------------+
|                   | DOM 解析 (Playwright) | Voyager API     |
+-------------------+------------------+------------------+
| 单 profile 耗时   | 10-30 秒          | 1-3 秒           |
| 数据结构化程度     | ❌ 需 DOM 解析    | ✅ 直接 JSON     |
| 限速严格程度       | 中等              | 严格（易 429）   |
| 端点稳定性         | ✅ 稳定（DOM 结构） | ❌ 客户端版本变更 |
| 适合场景           | 小批量高精度       | 大批量低精度      |
+-------------------+------------------+------------------+

决策:
  - 发现阶段: DOM 解析（稳定，虽慢但可靠）
  - 详情获取阶段: API（快，但需要处理限速）  
  - Anthropic 分析需要高精度工作年限 → DOM 解析仍是主方案
  - API 用于快速获取技能标签（DOM 解析技能部分较慢）
```

```python
"""
voyager_api_v2.py — 面向职业经历详情的 Voyager API 封装

关键优化：
  1. 批量请求（合并多个 profile 请求，减少 Cookie 交换次数）
  2. 自适应限速（基于 429 响应调整速率）
  3. 降级策略（API 失败时回退到 DOM 解析）
"""

class AnthropicVoyagerAPI:
    """
    Voyager API — 专注工作经历和技能标签提取
    """

    API_BASE = "https://www.linkedin.com/voyager/api"

    def __init__(self, browser, rate_limiter):
        self._browser = browser
        self._rate_limiter = rate_limiter
        self._csrf_token = None

    async def initialize(self):
        """从当前浏览器 session 获取 CSRF token"""
        page = self._browser._page
        cookies = await page.context.cookies()
        for cookie in cookies:
            if cookie["name"] == "JSESSIONID":
                self._csrf_token = cookie["value"].strip('"')
                break
        if not self._csrf_token:
            raise RuntimeError("Cannot get CSRF token — not logged in?")

    async def get_profile_work_history(
        self, profile_id: str
    ) -> Optional[dict]:
        """
        获取个人资料的工作经历（API 方式）
        
        Args:
            profile_id: 例如 "janedoe"（从 /in/ 路径提取）
        Returns:
            {
                "positions": [
                    {"company": "Anthropic", "title": "Staff Engineer",
                     "start": {"month": 1, "year": 2024},
                     "end": None,  # 在职
                     "duration_months": 29,
                     "description": "...",
                     "location": "San Francisco"},
                ],
                "education": [...],
                "skills": ["Kubernetes", "Python", ...],
                "error": None,
            }
        """
        await self._rate_limiter.wait_if_needed(RateLimitTier.API)

        url = (
            f"{self.API_BASE}/identity/profiles/{profile_id}/profileView"
        )

        result = await self._api_call("GET", url)
        return self._parse_positions(result)

    async def batch_get_profiles(
        self, profile_ids: list[str], batch_size: int = 5
    ) -> list[dict]:
        """
        批量获取 profiles
        
        策略：
          - 5 个一批并行发出（利用 HTTP/2 多路复用）
          - 批次间等待（限速）
          - 遇到 429 自动降速
        """
        results = []
        for i in range(0, len(profile_ids), batch_size):
            batch = profile_ids[i:i + batch_size]
            tasks = [self.get_profile_work_history(pid) for pid in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for pid, res in zip(batch, batch_results):
                if isinstance(res, Exception):
                    results.append({"profile_id": pid, "error": str(res)})
                else:
                    results.append(res)
            
            # 批次间长等待
            await asyncio.sleep(random.uniform(5, 10))
        
        return results

    def _parse_positions(self, raw: dict) -> dict:
        """解析 Voyager API 返回的职位信息"""
        try:
            profile = raw.get("data", {}).get("profile", {})
            positions = profile.get("position", {}).get("elements", [])
            
            parsed = []
            for pos in positions:
                company = pos.get("companyName", "")
                title = pos.get("title", "")
                
                # 时间解析
                date_range = pos.get("dateRange", {})
                start = date_range.get("start", {})
                end = date_range.get("end", {})
                
                parsed.append({
                    "company": company,
                    "title": title,
                    "start_month": start.get("month"),
                    "start_year": start.get("year"),
                    "end_month": end.get("month", None),
                    "end_year": end.get("year", None),
                    "is_current": pos.get("current", False),
                    "description": pos.get("description", ""),
                    "location": pos.get("location", ""),
                })
            
            return {"positions": parsed, "error": None}
        except Exception as e:
            return {"positions": [], "error": str(e)}

    async def _api_call(self, method: str, url: str) -> dict:
        """执行 Voyager API 调用"""
        page = self._browser._page
        code = f"""
        (async () => {{
            const resp = await fetch('{url}', {{
                method: '{method}',
                headers: {{
                    'csrf-token': '{self._csrf_token or ""}',
                    'x-restli-protocol-version': '2.0.0',
                    'accept': 'application/vnd.linkedin.normalized+json+2.1',
                }},
                credentials: 'include',
            }});
            if (resp.status === 429) {{
                return {{__rate_limited: true, retry_after: 
                    parseInt(resp.headers.get('Retry-After') || '60')}};
            }}
            if (!resp.ok) {{
                return {{__error: true, status: resp.status}};
            }}
            return await resp.json();
        }})()
        """
        try:
            result = await page.evaluate(code)
            if result.get("__rate_limited"):
                wait = result.get("retry_after", 60)
                logging.warning(f"API rate limited, waiting {wait}s")
                self._rate_limiter._configs[RateLimitTier.API]["requests_per_window"] = \
                    max(1, self._rate_limiter._configs[RateLimitTier.API]["requests_per_window"] // 2)
                await asyncio.sleep(wait)
                return await self._api_call(method, url)  # 重试
            if result.get("__error"):
                raise RuntimeError(f"API error: {result.get('status')}")
            return result
        except Exception as e:
            raise RuntimeError(f"Voyager API call failed: {e}")
```

### 2.5 三路调度器（含 Anthropic 场景参数）

```python
"""
discovery_orchestrator_v2.py — 面向 5,306 条目标的调度器

调度策略（基于 Anthropic 场景标定）：
  1. Dork 先行：3-4 小时 → ~1,500 URLs（低风险）
  2. LinkedIn 搜索：8-10 小时 → ~3,000 URLs（核心路径）
  3. Voyager API 补漏：1-2 小时 → ~500 URLs（快速补充）
  4. 去重合并 → ~5,000 条唯一 profiles
  5. 按工程师过滤 → ~1,800 条工程 profiles（超目标 10%）
"""

class DiscoveryOrchestratorV2:
    """
    三路调度器 — 带进度追踪和断点续传
    """

    def __init__(self, li_searcher, dork, voyager, rate_limiter,
                 db_path: str = "discovery_state.db"):
        self._li = li_searcher
        self._dork = dork
        self._voyager = voyager
        self._limiter = rate_limiter
        self._db = ProfileStore(db_path)  # SQLite 持久化

    async def discover_for_analysis(
        self,
        company: str = "Anthropic",
        target_profiles: int = 5306,
        resume: bool = True,
    ):
        """
        完整的公司人才发现流程
        
        参数说明:
          company: "Anthropic"
          target_profiles: 5306（Milan Griffes 的实际采集量）
          resume: 断点续传（从上一次中断处继续）
        
        产出:
          SQLite 数据库中 5000+ 条去重 profiles
        """
        if resume:
            existing = self._db.count_profiles(company)
            logging.info(f"Resuming: {existing} profiles already in DB")
            if existing >= target_profiles:
                logging.info("Target already met, skipping discovery")
                return

        # Phase 1: Google Dork（快速铺面）
        logging.info("=== Phase 1: Google Dork ===")
        dork_urls = await self._dork.discover(
            company=company, max_results=3000
        )
        saved = await self._bulk_save(dork_urls, company, "dork")
        logging.info(f"Dork → {saved} new profiles")
        
        # Phase 2: LinkedIn 搜索（核心路径）
        logging.info("=== Phase 2: LinkedIn Search ===")
        li_results = await self._li.discover_engineering_team(
            company=company, max_profiles=2000
        )
        li_urls = {r["url"] for r in li_results}
        saved = await self._bulk_save(li_urls, company, "linkedin_search")
        logging.info(f"LinkedIn → {saved} new profiles")
        
        # Phase 3: Voyager API 补充
        logging.info("=== Phase 3: Voyager API supplemental ===")
        # 从 DB 中选取还没有 headeline/详细信息的 profile 补充
        incomplete = self._db.get_incomplete_profiles(company, limit=500)
        for batch in self._chunks(incomplete, 10):
            ids = [p["profile_id"] for p in batch]
            details = await self._voyager.batch_get_profiles(ids)
            self._db.update_profile_details(details)
        
        # 最终统计
        total = self._db.count_profiles(company)
        engineer_count = self._db.count_engineers(company)
        logging.info(f"Done: {total} profiles, {engineer_count} engineers")
        
        return {
            "total_profiles": total,
            "engineer_count": engineer_count,
            "company": company,
        }

    async def _bulk_save(self, urls: set[str], company: str,
                         source: str) -> int:
        """批量保存 URL 到 DB（去重）"""
        count = 0
        for url in urls:
            profile_id = url.rstrip("/").split("/in/")[-1]
            if self._db.profile_exists(profile_id):
                continue
            self._db.insert_profile({
                "profile_id": profile_id,
                "url": url,
                "company_target": company,
                "source": source,
                "discovered_at": datetime.now().isoformat(),
            })
            count += 1
        return count

    @staticmethod
    def _chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
```

---

## 3. 个人资料抽取器

### 3.1 设计原则：从分析精度反推动作

Anthropic 报告中最关键的几个数据精度需求：

```
中位数 12.2 年工龄
  ├── 需要 < 3 个月的误差（12.2 ± 0.3 年）
  ├── 需要正确处理重叠工作经历（兼职、顾问、创业同时）
  └── 需要区分"在职"状态（无 end 日期 = 至今）
       ↓
7986 段工作经历的精确日期解析
  ├── DOM 中日期格式多样："Jan 2024" / "01/2024" / "2024" / "Present"
  ├── 需要统一标准化为 (start_year, start_month, end_year, end_month)
  ├── 重叠处理：取最长时间跨度（非重叠累加）
  └── 缺失月份处理：保守估计（缺月→取年中 6 月）
       ↓
公司名标准化
  ├── "Google" = "Google LLC" = "Google Inc." = "Google"
  ├── "DeepMind" ≠ "Google DeepMind"（收购前后区分）
  └── 需要归一化映射表，保持统计一致性
```

### 3.2 DOM 解析 + 工作经历提取

```python
"""
profile_extractor_v2.py — 面向高精度工作经历的 DOM 解析器

与通用版的关键差异：
  1. 专注工作经历日期精度（月级）
  2. 包含重叠检测和处理逻辑
  3. 公司名标准化映射
  4. 技能标签的分类归类（直接映射到 Anthropic 报告的 Top 20 体系）
"""

class AnthropicProfileExtractor:
    """
    LinkedIn 个人资料抽取器 — 专注工作经历精度
    """

    # ============================================================
    # 公司名标准化映射表（核心！直接影响前公司频率统计）
    # ============================================================
    COMPANY_NORMALIZE = {
        # Google 系列
        "google": "Google",
        "google llc": "Google",
        "google inc": "Google",
        "google inc.": "Google",
        "google cloud": "Google",
        "google research": "Google",
        # Meta 系列
        "meta": "Meta",
        "facebook": "Meta",
        "meta platforms": "Meta",
        "meta platforms inc": "Meta",
        # 微软系列
        "microsoft": "Microsoft",
        "microsoft corporation": "Microsoft",
        "azure": "Microsoft",
        # Amazon 系列
        "amazon": "Amazon / AWS",
        "amazon web services": "Amazon / AWS",
        "aws": "Amazon / AWS",
        # 特别处理
        "google deepmind": "DeepMind",  # 收购后
        "deepmind": "DeepMind",
        "openai": "OpenAI",
        "openai lp": "OpenAI",
        "openai global": "OpenAI",
        "stripe": "Stripe",
        "stripe inc": "Stripe",
        "databricks": "Databricks",
        "databricks inc": "Databricks",
        "snowflake": "Snowflake",
        "snowflake computing": "Snowflake",
        "palantir": "Palantir",
        "palantir technologies": "Palantir",
        "airbnb": "Airbnb",
        "uber": "Uber",
        "uber technologies": "Uber",
        "apple": "Apple",
        "apple inc": "Apple",
    }

    # ============================================================
    # DOM 选择器（LinkedIn 个人资料页布局）
    # ============================================================
    SELECTORS = {
        "name": "h1[class*='text-heading-xlarge']",
        "headline": "div[class*='text-body-medium']",
        "location": "span[class*='text-body-small-inline']",
        "about": "section#about ~ div[class*='display-flex'] p",
        
        # 工作经历区块
        "experience_section": "section#experience-section",
        "experience_list": "li[class*='pvs-list__item--line-separated']",
        "position_company": (
            "span[class*='visually-hidden']:has-text('Company Name') + span"
        ),
        "position_title": (
            "span[aria-hidden='true']"
        ),
        "position_date": (
            "span[class*='visually-hidden']:has-text('Date') + span"
        ),
        "position_duration": (
            "span[class*='visually-hidden']:has-text('Duration') + span"
        ),
        "position_location": (
            "span[class*='visually-hidden']:has-text('Location') + span"
        ),
        "position_description": (
            "div[class*='display-flex'] ul li div[class*='visually-hidden']"
        ),
        
        # 技能标签区
        "skills_section": "section#skills-section",
        "skill_items": (
            "span[class*='pvs-navigation__text']"
        ),
        
        # 教育背景
        "education_section": "section#education-section",
        "education_items": "li[class*='pvs-list__item--line-separated']",
    }

    # ============================================================
    # 日期格式正则模式
    # ============================================================
    DATE_PATTERNS = [
        # "Jan 2024 - Present"
        r"(?P<s_month>[A-Za-z]+)\s+(?P<s_year>\d{4})\s*-\s*Present",
        # "Jan 2024 - Dec 2025"
        r"(?P<s_month>[A-Za-z]+)\s+(?P<s_year>\d{4})\s*-\s*"
        r"(?P<e_month>[A-Za-z]+)\s+(?P<e_year>\d{4})",
        # "2024 - Present"
        r"(?P<s_year>\d{4})\s*-\s*Present",
        # "2024 - 2025"
        r"(?P<s_year>\d{4})\s*-\s*(?P<e_year>\d{4})",
        # "01/2024 - Present"
        r"(?P<s_month>\d{1,2})/(?P<s_year>\d{4})\s*-\s*Present",
        # "01/2024 - 12/2025"
        r"(?P<s_month>\d{1,2})/(?P<s_year>\d{4})\s*-\s*"
        r"(?P<e_month>\d{1,2})/(?P<e_year>\d{4})",
        # "2024" solo
        r"^(\d{4})$",
    ]

    MONTH_MAP = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }

    def __init__(self, browser, rate_limiter):
        self._browser = browser
        self._rate_limiter = rate_limiter
        self._page = browser._page

    async def extract_profile(self, url: str) -> dict:
        """
        提取单个 LinkedIn profile 的完整信息
        
        参数:
            url: "https://www.linkedin.com/in/janedoe"
        
        返回:
            {
                "profile_id": "janedoe",
                "name": "Jane Doe",
                "headline": "Staff Engineer at Anthropic",
                "location": "San Francisco...",
                "positions": [  # 工作经历列表
                    {
                        "company": "Anthropic",
                        "company_normalized": "Anthropic",
                        "title": "Staff Engineer",
                        "start_year": 2024, "start_month": 1,
                        "end_year": None, "end_month": None,
                        "is_current": True,
                        "duration_months": 29,
                        "description": "Led inference infra team...",
                        "location": "San Francisco",
                    },
                    ...
                ],
                "education": [...],
                "skills": ["Kubernetes", "Python", "Rust", ...],
                "extracted_at": "2026-06-17T15:21:27",
            }
        """
        await self._rate_limiter.wait_if_needed(RateLimitTier.PROFILE)
        
        # 导航到 profile 页面
        await self._page.goto(url, wait_until="networkidle")
        await asyncio.sleep(random.uniform(2, 5))
        
        # 模拟人类滚动（触发懒加载内容）
        await self._browser.human_scroll(self._page, target_scrolls=3)
        
        # 提取基本信息
        name = await self._extract_text(self.SELECTORS["name"])
        headline = await self._extract_text(self.SELECTORS["headline"])
        location = await self._extract_text(self.SELECTORS["location"])
        
        # 核心：提取工作经历
        positions = await self._extract_positions()
        
        # 教育背景
        education = await self._extract_education()
        
        # 技能标签
        skills = await self._extract_skills()
        
        # 计算工龄
        total_years = self._compute_total_experience(positions)
        
        profile_id = url.rstrip("/").split("/in/")[-1]
        
        return {
            "profile_id": profile_id,
            "url": url,
            "name": name,
            "headline": headline,
            "location": location,
            "positions": positions,
            "education": education,
            "skills": skills,
            "total_experience_years": round(total_years, 1),
            "company": self._get_current_company(positions),
            "extracted_at": datetime.now().isoformat(),
        }

    # ============================================================
    # 工作经历核心提取逻辑
    # ============================================================

    async def _extract_positions(self) -> list[dict]:
        """
        提取所有工作经历
        
        关键难点：LinkedIn DOM 布局变化频繁，需要多组选择器 fallback
        """
        positions = []
        html = await self._page.content()
        soup = BeautifulSoup(html, "lxml")
        
        # 定位到 Experience 区块
        exp_section = soup.select_one(self.SELECTORS["experience_section"])
        if not exp_section:
            # fallback: 尝试其他选择器
            exp_section = soup.select_one("section:has-text('Experience')")
        if not exp_section:
            return positions
        
        items = exp_section.select(self.SELECTORS["experience_list"])
        
        for item in items:
            try:
                position = await self._parse_single_position(item)
                if position:
                    positions.append(position)
            except Exception as e:
                logging.warning(f"Failed to parse a position: {e}")
                continue
        
        return positions

    async def _parse_single_position(self, item) -> Optional[dict]:
        """解析单条工作经历"""
        
        # --- 公司名提取（最外层） ---
        company_el = item.select_one("span[class*='visually-hidden']")
        company_text = company_el.get_text(strip=True) if company_el else ""
        # LinkedIn DOM 中公司名字段通常格式为 "Company Name\nAnthropic"
        company = self._extract_company_from_visually_hidden(company_text)
        
        # --- 职位、时间、地点 ---
        # LinkedIn 把多个信息渲染在 aria-hidden="true" 的 span 中
        aria_spans = item.select("span[aria-hidden='true']")
        
        # 通常 3-4 个 span: [职位], [公司], [时间], [地点]
        title = ""
        date_text = ""
        location = ""
        
        texts = [s.get_text(strip=True) for s in aria_spans if s.get_text(strip=True)]
        
        if len(texts) >= 1:
            title = texts[0]
        if len(texts) >= 3:
            date_text = texts[2]
        if len(texts) >= 4:
            location = texts[3]
        
        # 特殊情况：前两行分别是 title 和 company 的情况
        # fallback: 如果 title 为空，尝试更精确的选择器
        if not title:
            title_el = item.select_one(
                "div[class*='display-flex'] span[aria-hidden='true']"
            )
            if title_el:
                title = title_el.get_text(strip=True)
        
        # --- 时间解析 ---
        parsed_date = self._parse_date_range(date_text)
        
        return {
            "company": company,
            "company_normalized": self._normalize_company(company),
            "title": title,
            "start_year": parsed_date["start_year"],
            "start_month": parsed_date["start_month"],
            "end_year": parsed_date["end_year"],
            "end_month": parsed_date["end_month"],
            "is_current": parsed_date["is_current"],
            "duration_months": parsed_date["duration_months"],
            "location": location,
        }

    def _parse_date_range(self, date_text: str) -> dict:
        """
        解析日期范围文本
        
        输入示例:
          "Jan 2024 - Present" → {"start": (2024, 1), "end": None, "current": True}
          "2019 - 2023"       → {"start": (2019, 6), "end": (2023, 6), "current": False}
          "2024"              → {"start": (2024, 6), "end": None, "current": True?}
        
        精度要求:
          - 中位数 12.2 年 → 需要月级精度
          - 缺月份 → 保守估计为年中（6 月）
        """
        date_text = date_text.strip()
        
        for pattern in self.DATE_PATTERNS:
            match = re.match(pattern, date_text, re.IGNORECASE)
            if not match:
                continue
            
            groups = match.groupdict()
            
            # === 解析开始时间 ===
            s_month = groups.get("s_month")
            s_year = int(groups["s_year"])
            
            if s_month and s_month.isdigit():
                start_month = int(s_month)
            elif s_month:
                start_month = self.MONTH_MAP.get(s_month.lower()[:3], 6)
            else:
                start_month = 6  # 缺省值
            
            # === 解析结束时间 ===
            is_current = "Present" in date_text
            e_year = groups.get("e_year")
            e_month = groups.get("e_month")
            
            if is_current:
                end_year = None
                end_month = None
                # 用当前时间计算时长
                now = datetime.now()
                duration = (now.year - s_year) * 12 + (now.month - start_month)
            elif e_year:
                e_year = int(e_year)
                if e_month and e_month.isdigit():
                    end_month = int(e_month)
                elif e_month:
                    end_month = self.MONTH_MAP.get(e_month.lower()[:3], 6)
                else:
                    end_month = 6  # 缺省
                duration = (e_year - s_year) * 12 + (end_month - start_month)
            else:
                # 只有一年的情况（如 "2024"），视为当前岗位
                end_year = None
                end_month = None
                duration = 0
            
            return {
                "start_year": s_year,
                "start_month": start_month,
                "end_year": end_year,
                "end_month": end_month,
                "is_current": is_current,
                "duration_months": max(duration, 0),
            }
        
        # 无法解析时返回空
        return {
            "start_year": None, "start_month": None,
            "end_year": None, "end_month": None,
            "is_current": False, "duration_months": 0,
        }

    # ============================================================
    # 年限计算（核心方法 — 直接影响 12.2 年这个关键指标）
    # ============================================================

    def _compute_total_experience(self, positions: list[dict]) -> float:
        """
        计算总工作年限
        
        关键设计决策（影响中位数结果）：
          1. 重叠处理：重叠月份不重复计算（取并集而非累加）
          2. 在职岗位：用现在时间计算
          3. 缺失月份：保守估计为 6 月
          4. 短期兼职（<3 个月）：排除？（Anthropic 分析未排除）
        
        算法：
          1. 将每个岗位的时间段转为 (start, end) 月份元组
          2. 合并重叠区间
          3. 计算总月数
        """
        if not positions:
            return 0.0
        
        now = datetime.now()
        intervals = []
        
        for pos in positions:
            if not pos["start_year"]:
                continue
            
            start_month_num = pos["start_year"] * 12 + (pos["start_month"] or 6)
            
            if pos["is_current"]:
                end_month_num = now.year * 12 + now.month
            elif pos["end_year"]:
                end_month_num = pos["end_year"] * 12 + (pos["end_month"] or 6)
            else:
                continue  # 无结束日期且非当前，跳过
            
            intervals.append((start_month_num, end_month_num))
        
        if not intervals:
            return 0.0
        
        # 排序并合并重叠区间
        intervals.sort()
        merged = [intervals[0]]
        
        for start, end in intervals[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end + 1:  # 允许 1 个月的交叠
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))
        
        # 计算总月数
        total_months = sum(end - start for start, end in merged)
        return total_months / 12.0

    # ============================================================
    # 技能标签提取与分类
    # ============================================================

    async def _extract_skills(self) -> list[str]:
        """
        提取技能标签
        
        注意：LinkedIn 的技能列表可能懒加载
        需要滚动到技能区并触发加载
        """
        # 滚动到技能区
        skills_section = await self._page.query_selector(
            self.SELECTORS["skills_section"]
        )
        if skills_section:
            await skills_section.scroll_into_view_if_needed()
            await asyncio.sleep(1)
        
        html = await self._page.content()
        soup = BeautifulSoup(html, "lxml")
        
        skills = []
        section = soup.select_one("section#skills-section")
        if section:
            # 多种选择器尝试
            items = section.select("span[class*='pvs-navigation__text']")
            if not items:
                items = section.select("span[aria-hidden='true']")
            for item in items:
                skill = item.get_text(strip=True)
                if skill and len(skill) < 100:  # 过滤过长的非技能文本
                    skills.append(skill)
        
        return skills

    # ============================================================
    # 辅助：公司名标准化
    # ============================================================

    @staticmethod
    def _normalize_company(company: str) -> str:
        """公司名标准化"""
        if not company:
            return "Unknown"
        key = company.lower().strip()
        # 先尝试完全匹配
        if key in AnthropicProfileExtractor.COMPANY_NORMALIZE:
            return AnthropicProfileExtractor.COMPANY_NORMALIZE[key]
        # 尝试部分匹配
        for pattern, normalized in AnthropicProfileExtractor.COMPANY_NORMALIZE.items():
            if pattern in key:
                return normalized
        return company  # 未匹配则返回原始名称

    @staticmethod
    def _extract_company_from_visually_hidden(text: str) -> str:
        """从 'Company Name\nAnthropic' 格式中提取公司名"""
        lines = text.split("\n")
        # 取最后一行非空文本
        for line in reversed(lines):
            line = line.strip()
            if line and line != "Company Name" and line != "Company":
                return line
        return text

    @staticmethod
    def _get_current_company(positions: list[dict]) -> Optional[str]:
        """提取当前任职公司"""
        for pos in positions:
            if pos.get("is_current"):
                return pos.get("company_normalized") or pos.get("company")
        return None

    async def _extract_text(self, selector: str) -> str:
        """提取元素文本"""
        el = await self._page.query_selector(selector)
        if el:
            return await el.inner_text()
        return ""
```

### 3.3 技能过滤引擎（与 Anthropic Top 20 对齐）

```python
"""
skill_classifier.py — 技能标签分类引擎

映射到 Anthropic 报告的 Top 20 技能分类体系
"""

class SkillClassifier:
    """
    技能标签分类器
    
    输入: ["Kubernetes", "Python", "System Design", "TensorFlow"]
    输出: {"infrastructure": 1, "backend": 1, "ml_ai": 1, ...}
    """

    # ============================================================
    # Anthropic 报告 Top 20 技能映射
    # ============================================================
    SKILL_MAPPING = {
        "infrastructure": {
            "kubernetes", "k8s", "docker", "terraform", "ansible",
            "infrastructure", "sre", "site reliability",
            "monitoring", "prometheus", "grafana", "datadog",
            "ci/cd", "jenkins", "gitlab ci", "github actions",
            "helm", "istio", "envoy", "service mesh",
            "system design", "scalability",
        },
        "backend": {
            "python", "go", "golang", "rust", "java", "c++",
            "backend", "api", "rest", "grpc", "microservices",
            "postgresql", "redis", "kafka", "rabbitmq",
            "node.js", "typescript",
        },
        "distributed_systems": {
            "distributed systems", "consensus", "raft", "paxos",
            "mapreduce", "spark", "flink", "hadoop",
            "distributed computing", "distributed storage",
            "cap theorem", "consistency",
        },
        "database_storage": {
            "postgresql", "mysql", "mongodb", "cassandra",
            "sql", "database", "storage", "nosql",
            "rocksdb", "leveldb", "spanner", "cockroachdb",
            "delta lake", "apache iceberg", "hudi",
        },
        "security": {
            "security", "cybersecurity", "penetration testing",
            "cryptography", "authentication", "authorization",
            "oauth", "saml", "zero trust",
            "secure coding", "sbom", "supply chain security",
            "privacy", "gdpr", "fedramp",
        },
        "cloud": {
            "aws", "gcp", "azure", "cloud",
            "ec2", "s3", "lambda", "cloud run",
            "virtualization", "cloud architecture",
        },
        "systems_os": {
            "linux", "unix", "kernel", "operating system",
            "file system", "memory management", "networking",
            "tcp/ip", "dns", "load balancing", "cdn",
            "performance optimization", "profiling",
        },
        "ml_ai": {
            "machine learning", "deep learning", "ai",
            "tensorflow", "pytorch", "jax",
            "nlp", "llm", "transformer", "neural network",
            "training", "inference", "model serving",
            "triton", "vllm", "tensorrt",
        },
        "networking": {
            "networking", "tcp/ip", "dns", "http",
            "load balancing", "cdn", "vpc",
            "rdma", "roce", "infiniband", "nvlink",
        },
        "data_engineering": {
            "data engineering", "etl", "data pipeline",
            "airflow", "spark", "flink", "kafka",
            "data warehouse", "data lake", "olap",
        },
        "frontend": {
            "javascript", "typescript", "react", "angular",
            "frontend", "ui", "ux", "css", "html",
        },
        "reinforcement_learning": {
            "reinforcement learning", "rl", "rlhf",
            "dpo", "ppo", "grpo",
            "constitutional ai", "alignment",
        },
        "mobile": {
            "mobile", "ios", "android", "swift",
            "kotlin", "react native", "flutter",
        },
    }

    def __init__(self):
        # 构建反向索引（技能 → 分类）
        self._skill_to_category: dict[str, str] = {}
        for category, skills in self.SKILL_MAPPING.items():
            for skill in skills:
                self._skill_to_category[skill] = category

    def classify_skills(self, skills: list[str]) -> dict[str, int]:
        """
        分类技能标签
        
        返回: {"infrastructure": 42, "backend": 25, ...}
        （按出现次数统计，非按人数）
        """
        counts: dict[str, int] = {}
        for skill in skills:
            skill_lower = skill.lower().strip()
            matched = False
            for pattern, category in self._skill_to_category.items():
                if pattern in skill_lower or skill_lower == pattern:
                    counts[category] = counts.get(category, 0) + 1
                    matched = True
                    break
            if not matched:
                counts["other"] = counts.get("other", 0) + 1
        return counts

    def get_top_skills(self, all_skills: list[str], top_n: int = 20) -> list[dict]:
        """
        获取 Top N 技能排名（对应 Anthropic 报告的 Top 20）
        
        返回:
            [{"skill": "infrastructure", "count": 672, "percentage": 40.0}, ...]
        """
        classified = self.classify_skills(all_skills)
        sorted_skills = sorted(
            classified.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_n]
        
        total = len(all_skills)
        return [
            {"skill": skill, "count": count,
             "percentage": round(count / total * 100, 1)}
            for skill, count in sorted_skills
        ]

    def compute_skill_profile(self, person_skills: list[str]) -> dict:
        """
        计算单人的技能画像

        用于统计"Infra 背景占比 40%"这类指标
        """
        categories = self.classify_skills(person_skills)
        # Infra 相关类别（包含了 infra/backend/distributed_systems 等）
        infra_related = (
            categories.get("infrastructure", 0) +
            categories.get("backend", 0) +
            categories.get("distributed_systems", 0) +
            categories.get("systems_os", 0)
        )
        return {
            "infra_flag": infra_related > 0,
            "category_count": len(categories),
            "primary_category": max(categories, key=categories.get)
            if categories else "unknown",
        }

```

---

## 4. 数据分析管道

### 4.1 数据流架构

```
raw_profiles (SQLite, 5,306 条)
    │
    ▼
filter_engineers() ──→ 过滤条件: headline 匹配工程岗位
    │                   + 排除非工程师模式
    ▼
工程师子集 (1,680 条)
    │
    ├──→ compute_tenure_distribution()
    │       ├── 中位数、平均、百分位
    │       ├── <3 年占比、>13 年占比
    │       └── 直方图数据（便于绘图）
    │
    ├──→ compute_company_origin()
    │       ├── 前公司频率排名
    │       ├── 人才迁移矩阵
    │       └── Sankey 图数据
    │
    ├──→ compute_skill_distribution()
    │       ├── Top 20 技能排名
    │       ├── Infra/Backend/Security 等分类
    │       └── 技能组合分析
    │
    └──→ compute_education_stats()
            ├── 博士占比
            ├── 学历分布
            └── 学科分布
```

### 4.2 完整 Pipeline 实现

```python
"""
analysis_pipeline_v2.py — 面向 Anthropic 报告的数据分析管道

关键设计原则：
  1. 精度优先 — 每个统计量给出置信区间
  2. 可重现 — 随机种子固定，结果稳定
  3. 交叉验证 — 关键指标经多个独立来源验证
  4. 异常检测 — 自动标记偏离预期的数据点
"""

import sqlite3
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np


class AnthropicAnalysisPipeline:
    """
    人才分析完整管道 — 直接对标 Anthropic 报告
    """

    def __init__(self, db_path: str = "linkedin_profiles.db"):
        self._db = sqlite3.connect(db_path)
        self._db.row_factory = sqlite3.Row
        self._cursor = self._db.cursor()
        self._skill_classifier = SkillClassifier()

    # ============================================================
    # 第一步：数据加载与过滤
    # ============================================================

    def load_engineer_profiles(self) -> pd.DataFrame:
        """
        加载工程师 profiles
        
        Milan Griffes 的过滤方式：
          5,306 原始 profiles → 过滤掉非工程岗 → 1,680 工程师
        
        本实现采用双层过滤：
          L1: headline 关键字匹配（排除 recruit/HR/sales 等）
          L2: 技能标签二次过滤（补漏 L1 未识别的工程师）
        """
        query = """
        SELECT p.*, GROUP_CONCAT(s.skill_name, ',') as skills
        FROM profiles p
        LEFT JOIN profile_skills s ON p.profile_id = s.profile_id
        WHERE p.company_target = 'Anthropic'
        GROUP BY p.profile_id
        """
        df = pd.read_sql_query(query, self._db)

        def is_engineer(row):
            headline = str(row.get("headline", "")).lower()
            # L1: headline 过滤
            is_eng, _ = classify_engineer_role(headline)
            if is_eng:
                return True
            # L2: 技能标签补漏（对 headline 无法判断的情况）
            skills = str(row.get("skills", "")).lower()
            eng_skills = [
                "kubernetes", "python", "golang", "infrastructure",
                "distributed systems", "sre",
            ]
            return any(s in skills for s in eng_skills)

        df["is_engineer"] = df.apply(is_engineer, axis=1)
        engineers = df[df["is_engineer"]].copy()
        
        logging.info(
            f"Filter: {len(df)} profiles → {len(engineers)} engineers "
            f"({len(engineers)/len(df)*100:.1f}%)"
        )
        return engineers

    # ============================================================
    # 第二步：资历分布（对标报告第 2 节）
    # ============================================================

    def compute_tenure_distribution(
        self, engineers: pd.DataFrame
    ) -> dict:
        """
        计算工龄分布
        
        对标输出:
          - 中位工作经验: 12.2 年
          - 中间 50% 区间: 8.8 - 16.5 年
          - 工作经验 < 3 年: 3%
          - 工作经验 > 13 年: 44%
        """
        # 从 work_experiences 表计算每人总工龄
        query = """
        SELECT profile_id, 
               SUM(duration_months) as total_months
        FROM work_experiences
        WHERE is_engineer = 1
        GROUP BY profile_id
        """
        tenure_df = pd.read_sql_query(query, self._db)
        tenure_df["years"] = tenure_df["total_months"] / 12.0
        
        years = tenure_df["years"].dropna()
        
        # 核心统计量
        result = {
            "count": int(len(years)),
            "median": round(float(years.median()), 1),
            "mean": round(float(years.mean()), 1),
            "std": round(float(years.std()), 1),
            "p25": round(float(years.quantile(0.25)), 1),
            "p75": round(float(years.quantile(0.75)), 1),
            "p10": round(float(years.quantile(0.10)), 1),
            "p90": round(float(years.quantile(0.90)), 1),
            "p95": round(float(years.quantile(0.95)), 1),
            "lt_3_years_pct": round(
                float((years < 3).sum() / len(years) * 100), 1
            ),
            "gt_13_years_pct": round(
                float((years > 13).sum() / len(years) * 100), 1
            ),
            # 直方图数据（用于可视化）
            "histogram_bins": self._build_histogram(years),
        }
        
        # 置信区间（bootstrap 法）
        np.random.seed(42)
        boot_medians = []
        for _ in range(1000):
            sample = np.random.choice(years, len(years), replace=True)
            boot_medians.append(np.median(sample))
        
        result["median_ci_95"] = (
            round(float(np.percentile(boot_medians, 2.5)), 1),
            round(float(np.percentile(boot_medians, 97.5)), 1),
        )
        
        logging.info(
            f"Tenure: median={result['median']}y "
            f"(95% CI: {result['median_ci_95']}), "
            f"n={result['count']}"
        )
        return result

    @staticmethod
    def _build_histogram(years, bin_width: float = 1.0):
        """构建直方图数据"""
        max_year = int(np.ceil(years.max()))
        bins = []
        for i in np.arange(0, max_year + bin_width, bin_width):
            count = int(((years >= i) & (years < i + bin_width)).sum())
            bins.append({
                "range": f"{i:.0f}-{i+bin_width:.0f}",
                "count": count,
                "pct": round(count / len(years) * 100, 1),
            })
        return bins

    # ============================================================
    # 第三步：前公司来源（对标报告第 4 节）
    # ============================================================

    def compute_company_origin(
        self, engineers: pd.DataFrame
    ) -> dict:
        """
        计算前公司来源排名
        
        对标输出:
          - Google: 18-22%
          - Meta: 12-15%
          - Stripe: 6-8%
          ...
        
        关键设计决策：
          1. 每条工作经历中的"上一份工作"而非全部
          2. 公司名标准化（Google LLC → Google）
          3. 排除当前公司（Anthropic）
        """
        query = """
        SELECT profile_id, company_normalized,
               start_year, start_month,
               is_current
        FROM work_experiences
        WHERE is_engineer = 1
        ORDER BY profile_id, start_year, start_month
        """
        we_df = pd.read_sql_query(query, self._db)
        
        # 排除当前在 Anthropic 的这段经历
        we_df = we_df[~we_df["company_normalized"].str.contains(
            "Anthropic", case=False, na=False
        )]
        
        # 对每人只取"最近一家"（倒序第一行）
        we_df = we_df.sort_values(
            ["profile_id", "start_year", "start_month"],
            ascending=[True, False, False]
        )
        last_companies = we_df.groupby("profile_id").first()
        
        # 统计频率
        company_counts = last_companies["company_normalized"].value_counts()
        total = len(last_companies)
        
        result = {
            "total": int(total),
            "rankings": []
        }
        
        for company, count in company_counts.items():
            result["rankings"].append({
                "company": company,
                "count": int(count),
                "pct": round(count / total * 100, 1),
                # 映射到报告中的范围表述
                "range_label": self._pct_to_range_label(
                    count / total * 100
                ),
            })
        
        # 添加累计占比
        cumulative = 0
        for r in result["rankings"]:
            cumulative += r["pct"]
            r["cumulative_pct"] = round(cumulative, 1)
        
        # 人才迁移矩阵（用于 Sankey 图）
        result["transition_matrix"] = self._build_transition_matrix(we_df)
        
        return result

    @staticmethod
    def _pct_to_range_label(pct: float) -> str:
        """百分比 → 报告中使用的范围描述"""
        if pct >= 18:
            return "🥇 18-22%"
        elif pct >= 12:
            return "🥈 12-15%"
        elif pct >= 6:
            return "🥉 6-8%"
        elif pct >= 4:
            return "4-6%"
        elif pct >= 3:
            return "3-4%"
        elif pct >= 2:
            return "2-3%"
        else:
            return "1-2%"

    @staticmethod
    def _build_transition_matrix(we_df) -> list[dict]:
        """
        构建人才迁移矩阵（前公司 → 后公司）
        
        返回格式适合 Sankey 图:
            [{"source": "Google", "target": "Anthropic", "value": 320}, ...]
        """
        # 按 profile_id 分组，排序时间段，连 pair
        transitions = []
        for pid, group in we_df.sort_values("start_year").groupby("profile_id"):
            companies = group["company_normalized"].tolist()
            for i in range(len(companies) - 1):
                if companies[i] != companies[i + 1]:  # 排除同一公司内部调动
                    transitions.append({
                        "source": companies[i],
                        "target": companies[i + 1],
                    })
        
        # 统计频率
        matrix = defaultdict(int)
        for t in transitions:
            key = (t["source"], t["target"])
            matrix[key] += 1
        
        return [
            {"source": s, "target": t, "value": v}
            for (s, t), v in sorted(
                matrix.items(), key=lambda x: x[1], reverse=True
            )[:30]  # Top 30 迁移路径
        ]

    # ============================================================
    # 第四步：技能标签分布（对标报告第 3 节）
    # ============================================================

    def compute_skill_distribution(
        self, engineers: pd.DataFrame
    ) -> dict:
        """
        计算技能标签分布
        
        对标输出:
          - Infrastructure: 40%
          - Backend: ~22%
          - Distributed Systems: ~20%
          - Python: ~25%
          ...
        
        统计口径：技能在工程师中出现的比例，
        不是多选计数（一个人可能有多个技能）。
        """
        query = """
        SELECT profile_id, skill_name
        FROM profile_skills
        WHERE profile_id IN (
            SELECT profile_id FROM engineers_filtered
        )
        """
        skills_df = pd.read_sql_query(query, self._db)
        
        total_engineers = len(engineers)
        
        # === 按分类统计（对标报告 Top 20 排名）===
        category_counts = defaultdict(set)
        raw_skills = defaultdict(set)
        
        for _, row in skills_df.iterrows():
            pid = row["profile_id"]
            skill = row["skill_name"]
            raw_skills[pid].add(skill)
            
            # 分类映射
            categories = self._skill_classifier.classify_skills([skill])
            for cat in categories:
                category_counts[cat].add(pid)
        
        top_categories = sorted(
            category_counts.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )[:20]
        
        rankings = []
        for cat, engineers_set in top_categories:
            rankings.append({
                "skill": cat,
                "engineer_count": len(engineers_set),
                "pct": round(
                    len(engineers_set) / total_engineers * 100, 1
                ),
            })
        
        # === 特定指标 ===
        infra_count = len(category_counts.get("infrastructure", set()))
        rl_count = len(category_counts.get("reinforcement_learning", set()))
        
        result = {
            "total_engineers": total_engineers,
            "rankings": rankings,
            "highlights": {
                "infrastructure_pct": round(
                    infra_count / total_engineers * 100, 1
                ),
                "rl_pct": round(
                    rl_count / total_engineers * 100, 1
                ),
                "python_pct": self._compute_language_pct(
                    raw_skills, "python", total_engineers
                ),
                "go_pct": self._compute_language_pct(
                    raw_skills, "go", total_engineers
                ),
                "rust_pct": self._compute_language_pct(
                    raw_skills, "rust", total_engineers
                ),
                "k8s_pct": self._compute_language_pct(
                    raw_skills, "kubernetes", total_engineers
                ),
            },
        }
        
        return result

    @staticmethod
    def _compute_language_pct(
        raw_skills: dict, keyword: str, total: int
    ) -> float:
        """计算特定技能在工程师中的比例"""
        count = sum(
            1 for skills in raw_skills.values()
            if any(keyword in s.lower() for s in skills)
        )
        return round(count / total * 100, 1)

    # ============================================================
    # 第五步：学历比例（对标报告第 2 节）
    # ============================================================

    def compute_education_stats(
        self, engineers: pd.DataFrame
    ) -> dict:
        """
        计算学历分布
        
        对标输出:
          - 博士占比: 13%
        
        关键设计：学位提取与分类
          PhD / Doctorate / Doctor of Philosophy → 博士
          Master's / MS / MEng / MBA → 硕士
          Bachelor's / BS / BA → 学士
        """
        query = """
        SELECT profile_id, degree, field, school_name
        FROM education
        WHERE profile_id IN (
            SELECT profile_id FROM engineers_filtered
        )
        """
        edu_df = pd.read_sql_query(query, self._db)
        
        # === 学位分类 ===
        def classify_degree(degree: str) -> str:
            degree_lower = (degree or "").lower()
            if any(kw in degree_lower for kw in [
                "phd", "doctorate", "doctor of philosophy", "ph.d"
            ]):
                return "phd"
            if any(kw in degree_lower for kw in [
                "master", "ms ", "m.s.", "meng", "mba", "ma ", "m.a."
            ]):
                return "master"
            if any(kw in degree_lower for kw in [
                "bachelor", "bs ", "b.s.", "ba ", "b.a.", "beng"
            ]):
                return "bachelor"
            if any(kw in degree_lower for kw in [
                "associate", "aa", "a.s."
            ]):
                return "associate"
            return "other"
        
        edu_df["degree_level"] = edu_df["degree"].apply(classify_degree)
        
        # 每人取最高学历
        degree_order = {
            "phd": 5, "master": 4, "bachelor": 3,
            "associate": 2, "other": 1,
        }
        edu_df["degree_rank"] = edu_df["degree_level"].map(degree_order)
        highest_edu = edu_df.loc[
            edu_df.groupby("profile_id")["degree_rank"].idxmax()
        ]
        
        # === 统计 ===
        degree_counts = highest_edu["degree_level"].value_counts()
        total_with_edu = len(highest_edu)
        phd_count = degree_counts.get("phd", 0)
        
        # === 按学科细分 ===
        field_counts = Counter()
        for _, row in highest_edu.iterrows():
            field = str(row.get("field", "")).strip()
            if field:
                field_counts[field] += 1
        
        result = {
            "total_with_education": int(total_with_edu),
            "phd_count": int(phd_count),
            "phd_pct": round(phd_count / total_with_edu * 100, 1),
            "degree_distribution": {
                k: {
                    "count": int(v),
                    "pct": round(v / total_with_edu * 100, 1),
                }
                for k, v in degree_counts.items()
            },
            "top_fields": [
                {"field": field, "count": count}
                for field, count in field_counts.most_common(15)
            ],
        }
        
        return result

    # ============================================================
    # 第六步：生成对标报告
    # ============================================================

    def run_full_analysis(self) -> dict:
        """
        运行完整分析，生成对标报告
        
        返回包含所有分析结果的结构化字典
        """
        engineers = self.load_engineer_profiles()
        
        result = {
            "meta": {
                "company": "Anthropic",
                "total_profiles": int(len(engineers)),
                "analyzed_at": datetime.now().isoformat(),
                "data_quality": self._compute_data_quality(engineers),
            },
            "tenure": self.compute_tenure_distribution(engineers),
            "company_origin": self.compute_company_origin(engineers),
            "skills": self.compute_skill_distribution(engineers),
            "education": self.compute_education_stats(engineers),
        }
        
        # 添加交叉验证标记
        result["cross_validation"] = self._cross_validate(result)
        
        return result

    def _compute_data_quality(self, df: pd.DataFrame) -> dict:
        """数据质量评估"""
        total = len(df)
        return {
            "total_profiles": total,
            "with_positions": int(
                (df["positions"] is not None).sum()
            ),
            "with_skills": int(
                (df["skills"] is not None).sum()
            ),
            "with_education": int(
                (df["education"] is not None).sum()
            ),
            "completeness_pct": round(
                total / 5306 * 100, 1  # 对标 Milan 的 5306 条
            ),
        }

    def _cross_validate(self, result: dict) -> dict:
        """
        交叉验证关键指标
        
        与公开数据进行比较，标记偏差
        """
        validation = []
        
        # 1. 中位数工龄
        median = result["tenure"]["median"]
        expected = 12.2
        deviation = abs(median - expected) / expected
        validation.append({
            "metric": "median_tenure",
            "value": median,
            "expected": expected,
            "deviation_pct": round(deviation * 100, 1),
            "status": "✅" if deviation < 0.1 else "⚠️",
        })
        
        # 2. Google 来源比例
        google_pct = None
        for r in result["company_origin"]["rankings"]:
            if r["company"] == "Google":
                google_pct = r["pct"]
                break
        if google_pct:
            deviation = abs(google_pct - 20) / 20
            validation.append({
                "metric": "google_source_pct",
                "value": google_pct,
                "expected": "18-22%",
                "deviation_pct": round(deviation * 100, 1),
                "status": "✅" if deviation < 0.15 else "⚠️",
            })
        
        # 3. Infra 占比
        infra_pct = result["skills"]["highlights"]["infrastructure_pct"]
        deviation = abs(infra_pct - 40) / 40
        validation.append({
            "metric": "infra_pct",
            "value": infra_pct,
            "expected": 40,
            "deviation_pct": round(deviation * 100, 1),
            "status": "✅" if deviation < 0.15 else "⚠️",
        })
        
        return {"checks": validation}
```

### 4.3 可视化输出

```python
"""
visualization.py — 对标 Anthropic 报告的图表生成
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

matplotlib.rcParams["font.sans-serif"] = ["Arial Unicode MS", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False


class ReportVisualizer:
    """
    生成对标 Anthropic 人才报告的可视化图表
    """

    @staticmethod
    def plot_tenure_distribution(tenure_data: dict, save_path: str = None):
        """
        工龄分布直方图
        
        对标报告:
          - 中位数标注线
          - p25/p75 区间阴影
          - <3年/ >13年 高亮
        """
        bins = tenure_data["histogram_bins"]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 柱状图
        labels = [b["range"] for b in bins]
        values = [b["count"] for b in bins]
        
        # 着色：<3年蓝色，>13年红色，其余灰色
        colors = []
        for b in bins:
            low = float(b["range"].split("-")[0])
            if low < 3:
                colors.append("#3498db")  # 蓝
            elif low >= 13:
                colors.append("#e74c3c")  # 红
            else:
                colors.append("#bdc3c7")  # 灰
        
        bars = ax.bar(labels, values, color=colors, alpha=0.7)
        
        # 中位线
        median = tenure_data["median"]
        ax.axvline(x=labels.index(
            next(b["range"] for b in bins
                 if float(b["range"].split("-")[0]) <= median
                 < float(b["range"].split("-")[1]))
        ) + 0.4, color="darkorange", linestyle="--", linewidth=2,
                   label=f"Median: {median}y")
        
        # 统计信息
        stats_text = (
            f"n = {tenure_data['count']}\n"
            f"Median: {tenure_data['median']}y\n"
            f"P25-P75: {tenure_data['p25']} - {tenure_data['p75']}y\n"
            f"<3y: {tenure_data['lt_3_years_pct']}%\n"
            f">13y: {tenure_data['gt_13_years_pct']}%"
        )
        ax.text(0.95, 0.95, stats_text, transform=ax.transAxes,
                verticalalignment="top", horizontalalignment="right",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
                fontsize=10)
        
        ax.set_xlabel("Experience Range (years)")
        ax.set_ylabel("Number of Engineers")
        ax.set_title("Anthropic Engineering Team — Experience Distribution")
        ax.legend()
        
        # 旋转 x 轴标签
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()

    @staticmethod
    def plot_company_origin(origin_data: dict, top_n: int = 10,
                            save_path: str = None):
        """
        前公司来源条形图
        
        对标报告:
          - 按频率排序
          - 标注范围
          - 累计占比曲线
        """
        rankings = origin_data["rankings"][:top_n]
        
        fig, ax1 = plt.subplots(figsize=(12, 7))
        
        companies = [r["company"] for r in rankings][::-1]
        pcts = [r["pct"] for r in rankings][::-1]
        
        # 条形图
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(companies)))
        bars = ax1.barh(companies, pcts, color=colors)
        
        # 在每个柱子上标注百分比
        for bar, pct in zip(bars, pcts):
            ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                     f"{pct}%", va="center", fontsize=9)
        
        ax1.set_xlabel("Percentage of Engineers")
        ax1.set_title(f"Anthropic — Previous Company Origins "
                      f"(n={origin_data['total']})")
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()

    @staticmethod
    def plot_skill_rankings(skill_data: dict, top_n: int = 15,
                            save_path: str = None):
        """
        技能排名条形图
        
        对标报告: Top 20 技能排名
        """
        rankings = skill_data["rankings"][:top_n]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        skills = [r["skill"] for r in rankings][::-1]
        pcts = [r["pct"] for r in rankings][::-1]
        
        # 颜色按分类映射
        color_map = {
            "infrastructure": "#e74c3c",
            "backend": "#3498db",
            "distributed_systems": "#2ecc71",
            "security": "#f39c12",
            "cloud": "#9b59b6",
        }
        colors = [color_map.get(s, "#95a5a6") for s in skills]
        
        ax.barh(skills, pcts, color=colors, alpha=0.8)
        ax.set_xlabel("Percentage of Engineers")
        ax.set_title(f"Anthropic — Top {top_n} Skills")
        
        # 标注
        for i, (s, p) in enumerate(zip(skills, pcts)):
            ax.text(p + 0.5, i, f"{p}%", va="center", fontsize=8)
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()
```

---

## 5. 完整 Pipeline 编排

```python
"""
run_anthropic_analysis.py — 端到端执行脚本
"""

import asyncio
import logging
import json
from pathlib import Path


async def run_full_pipeline():
    """
    端到端执行 Anthropic 人才分析
    
    步骤:
      1. 发现人才（三路并行）
      2. 提取 profiles（带限速）
      3. 数据清洗与标准化
      4. 分析计算
      5. 生成报告
    """
    # === 配置 ===
    config = {
        "company": "Anthropic",
        "target_profiles": 5306,
        "target_engineers": 1680,
        "max_concurrent": 3,
        "db_path": "anthropic_analysis.db",
        "output_dir": "output/anthropic_2026",
    }
    
    # 初始化输出目录
    Path(config["output_dir"]).mkdir(parents=True, exist_ok=True)
    
    # === Phase 1: Discovery ===
    logging.info("=== Phase 1: Talent Discovery ===")
    orchestrator = setup_discovery(config)
    discovered = await orchestrator.discover_for_analysis(
        company=config["company"],
        target_profiles=config["target_profiles"],
    )
    logging.info(f"Discovered: {discovered}")
    
    # === Phase 2: Profile Extraction ===
    logging.info("=== Phase 2: Profile Extraction ===")
    extractor = setup_extractor(config)
    profiles = await extractor.extract_all(
        batch_size=3,  # 每批 3 个（受限于限速）
        max_profiles=config["target_profiles"],
    )
    logging.info(f"Extracted: {len(profiles)} profiles")
    
    # === Phase 3: Analysis ===
    logging.info("=== Phase 3: Analysis ===")
    pipeline = AnthropicAnalysisPipeline(db_path=config["db_path"])
    result = pipeline.run_full_analysis()
    
    # 保存结果
    output_path = Path(config["output_dir"]) / "analysis_result.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    logging.info(f"Analysis saved to {output_path}")
    
    # === Phase 4: Visualization ===
    logging.info("=== Phase 4: Visualization ===")
    viz = ReportVisualizer()
    viz.plot_tenure_distribution(
        result["tenure"],
        save_path=str(Path(config["output_dir"]) / "tenure_distribution.png"),
    )
    viz.plot_company_origin(
        result["company_origin"],
        save_path=str(Path(config["output_dir"]) / "company_origin.png"),
    )
    viz.plot_skill_rankings(
        result["skills"],
        save_path=str(Path(config["output_dir"]) / "skill_rankings.png"),
    )
    
    # === 输出关键指标 ===
    print("\n" + "=" * 60)
    print("Anthropic Talent Analysis — Key Metrics")
    print("=" * 60)
    print(f"Total Profiles:       {result['meta']['total_profiles']}")
    print(f"Median Tenure:        {result['tenure']['median']}y "
          f"(95% CI: {result['tenure']['median_ci_95']})")
    print(f"P25-P75:              {result['tenure']['p25']} - "
          f"{result['tenure']['p75']}y")
    print(f"<3y:                  {result['tenure']['lt_3_years_pct']}%")
    print(f">13y:                 {result['tenure']['gt_13_years_pct']}%")
    print(f"PhD:                  {result['education']['phd_pct']}%")
    print(f"Infrastructure:       {result['skills']['highlights']['infrastructure_pct']}%")
    print(f"RL:                   {result['skills']['highlights']['rl_pct']}%")
    print("\nCross-validation:")
    for check in result["cross_validation"]["checks"]:
        print(f"  {check['status']} {check['metric']}: "
              f"{check['value']} (expected: {check['expected']}, "
              f"deviation: {check['deviation_pct']}%)")
    print("=" * 60)


def setup_discovery(config):
    """初始化发现引擎（略，见上文各 engine 实现）"""
    pass


def setup_extractor(config):
    """初始化提取器（略，见上文 extractor 实现）"""
    pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    asyncio.run(run_full_pipeline())
```

---

## 6. 风险研判与边界条件

### 6.1 数据质量风险

| 风险 | 影响分析 | 缓解措施 |
|:----|:---------|:---------|
| **Date parsing 偏差** | 缺省月份设为 6 月 → 中位数偏大约 0.3 年 | 记录缺省比例，标注在报告中 |
| **短期兼职计入** | 多份兼职叠加 → 工龄高估 | 重叠区间合并算法（见上文） |
| **技能标签不完整** | 不是所有 LinkedIn 用户都填了技能 | 统计时标注"有技能标签的人数占比" |
| **公司名未标准化** | "Google" vs "Google LLC" 分开统计 | 标准化映射表 + 模糊匹配 fallback |
| **Dr 学位误判** | "Doctor of..." 包含医学博士 / JD | 过滤非 CS 领域的 Doctor 学位 |

### 6.2 样本偏差风险

```python
# sample_bias_analysis.py — 样本偏差检测

class SampleBiasDetector:
    """
    样本偏差检测
    
    LinkedIn 爬取数据天然存在偏差：
      1. 越资深的员工 LinkedIn 资料越完整
      2. 工程师比非技术岗更愿意填 LinkedIn
      3. 美国用户比非美国用户资料更完整
    
    Anthropic 报告的应对方式：
      - 明确标注"基于 LinkedIn 公开数据"
      - 不声称代表全公司，只代表"有 LinkedIn 资料的人群"
    """

    BIAS_FACTORS = [
        {
            "name": "tenure_completeness",
            "desc": "资深员工资料更完整 → 中位数可能被高估",
            "direction": "overestimate",
            "severity": "medium",
        },
        {
            "name": "title_bias",
            "desc": "Senior/Staff/Principal 更愿意标注标题",
            "direction": "overestimate_seniority",
            "severity": "low",
        },
        {
            "name": "company_bias",
            "desc": "大公司（Google/Meta）员工更可能保留 LinkedIn",
            "direction": "overestimate_big_co",
            "severity": "medium",
        },
        {
            "name": "location_bias",
            "desc": "美国员工占比可能被高估",
            "direction": "overestimate_us",
            "severity": "low",
        },
        {
            "name": "skills_bias",
            "desc": "有技能标签的人只占 ~70%",
            "direction": "skills_sample_not_representative",
            "severity": "high",
        },
    ]

    def estimate_bias_impact(self, result: dict) -> dict:
        """
        估算偏差对关键指标的影响
        
        返回: 每个指标的"可能真实值区间"
        """
        median = result["tenure"]["median"]
        return {
            "median_tenure_adjusted": {
                "reported": median,
                "likely_range": (max(10.5, median - 1.0), median + 0.5),
                "note": "资深员工资料更完整，实际中位数可能低 0.5-1.0 年",
            },
            "google_pct_adjusted": {
                "reported": None,  # 从 result 中提取
                "likely_range": "16-24%",
                "note": "大公司员工 LinkedIn 更活跃，实际占比可能略低",
            },
            "infra_pct_adjusted": {
                "reported": None,
                "likely_range": "35-42%",
                "note": "Infra 工程师填技能标签的意愿更高",
            },
        }
```

### 6.3 与 Milan Griffes 原始分析的对标问题

Milan Griffes 的分析方法中有几个关键细节官方未披露，需要做合理的推演假设：

| # | 未知细节 | 推演假设 | 影响 |
|:-:|:---------|:--------|:-----|
| 1 | 具体过滤规则 | 基于 headline 正则 + 公司列表过滤 | 容忍 ±5% 的误过滤 |
| 2 | 重叠经历处理 | 可能采用不同的合并策略 | 中位数 ±0.3 年 |
| 3 | 前公司统计口径 | "最近一份前 company" vs "所有前 company" | Google 排名可能差 2-3% |
| 4 | 技能统计方法 | "出现在简历中" vs "出现在 LinkedIn 技能区" | 可能差 5-10% |

**建议报告附注**: 标注"数据采集方法与原始分析存在差异，关键指标偏差在 ±10% 以内"。

### 6.4 对 AI 产业链的启示（反哺设计）

从爬虫实现的视角，Anthropic 分析本身对 AI 产业链有 5 条启示（也反向影响爬虫的设计）：

```
1. Infra 占 40% → 爬虫应当重点采集 Infra 相关技能标签
2. Google 是第一来源 → 公司名标准化表应该优先覆盖 Google 系列
3. 博士 13% 但研究部 >60% → 教育背景采集需区分学院/研究机构
4. 安全团队 ~250 人 → 安全技能标签分类需要更细致
5. Agent 团队 ~200 人 → 爬虫需要关注 Agent 相关新岗位词
```

---

## 关联知识

- `tools/linkedin-scraper-architecture.md` — 通用架构（3608 行全量实现）
- `enterprise-mgmt/ai-talent-strategy-anthropic.md` — Anthropic 人才分析原始报告
- `02_rd/03_hardware/08_storage/diagnostic-projects-survey.md` — 数据质量验证方法论
