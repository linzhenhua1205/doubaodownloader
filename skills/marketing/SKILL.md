---
name: marketing
description: 营销技能组。包含45+个专业营销技能，覆盖SEO、内容营销、转化率优化、广告投放、邮件营销、社交媒体等领域。基于 Corey Haines 的 marketingskills 项目，已适配本工程使用。
category: Marketing
user_invocable: true
version: 2.0
author: Corey Haines
homepage: https://github.com/coreyhaines31/marketingskills
requires: []
provides: []
---

# Marketing Skills

## Overview

This skill pack contains **45+ specialized marketing skills** for AI agents. Each skill provides frameworks, workflows, and best practices for specific marketing tasks.

## 🎯 领域适配标注

针对**服务器/AI 基础设施 B2B** 场景，47 个子技能的适用性分级：

| 适用性 | 子技能 | 数量 |
|:-------|:-------|:----:|
| ✅ **高相关** — 直接影响服务器产品定位/竞争分析 | `competitor-profiling`, `competitors`, `customer-research`, `pricing`, `product-marketing`, `analytics`, `content-strategy` | 7 |
| 🔶 **中相关** — 可为技术内容/渠道策略提供框架 | `seo-audit`, `ai-seo`, `copywriting`, `copy-editing`, `launch`, `public-relations`, `revops`, `sales-enablement` | 8 |
| ⚪ **低相关** — B2C 为主，偶需参考 | 其余 32 个（ads/email/social/video/popups/sms 等） | 32 |

> **建议**: 高相关子技能可直接使用；中相关需适配 B2B 语境；低相关子技能可保留但不主动触发。

## Skill Categories

### SEO & Discovery
- **seo-audit** - Technical and on-page SEO audit
- **ai-seo** - AI search optimization (AEO, GEO, LLMO)
- **programmatic-seo** - Scaled page generation for SEO
- **site-architecture** - Page hierarchy and URL structure
- **schema** - Structured data / JSON-LD
- **competitors** - Comparison and alternative pages
- **aso** - App Store Optimization

### Content & Copy
- **copywriting** - Marketing page copy
- **copy-editing** - Edit and polish existing copy
- **cold-email** - B2B cold outreach emails
- **emails** - Automated email flows
- **social** - Social media content
- **video** - Video content creation
- **image** - AI image generation

### Conversion Optimization
- **cro** - Pages and forms optimization
- **signup** - Registration flows
- **onboarding** - Post-signup activation
- **popups** - Modals and overlays
- **paywalls** - In-app upgrade moments

### Paid & Distribution
- **ads** - Google, Meta, LinkedIn ad campaigns
- **ad-creative** - Bulk ad creative generation
- **public-relations** - Press coverage and media strategy

### Measurement & Testing
- **analytics** - Event tracking setup
- **ab-testing** - Experiment design

### Growth & Retention
- **referrals** - Referral and affiliate programs
- **free-tools** - Marketing tools and calculators
- **churn-prevention** - Cancel flows and save offers
- **community-marketing** - Community building

### Strategy & Monetization
- **marketing-plan** - Comprehensive marketing plans
- **marketing-ideas** - SaaS marketing ideas
- **marketing-psychology** - Mental models and psychology
- **launch** - Product launches
- **pricing** - Pricing and monetization strategy
- **offers** - Offer design and value framing

### Sales & RevOps
- **revops** - Lead lifecycle and scoring
- **sales-enablement** - Sales decks and one-pagers
- **prospecting** - B2B prospecting
- **customer-research** - Customer research

### Other
- **content-strategy** - Content planning
- **lead-magnets** - Lead generation
- **co-marketing** - Partnership campaigns
- **directory-submissions** - Startup directory submissions
- **competitor-profiling** - Competitor analysis
- **sms** - SMS marketing

## Usage

Each skill is self-contained and can be invoked independently. Many skills reference `product-marketing` for context first, so consider creating that document for best results.

## Related Skills

- **knowledge-wiki** - For storing research findings and insights
- **analytics** - For measuring campaign performance
- **competitor-analysis** - For competitive research

---

## 📂 完整子技能索引

| 分类 | 子技能目录 | B2B适配度 | 适用场景 |
|:-----|:-----------|:--------:|:---------|
| **SEO & Discovery** (7) | `seo-audit`, `ai-seo`, `programmatic-seo`, `site-architecture`, `schema`, `competitors`, `aso` | 🔶 中 | 官网SEO、AI搜索优化、技术内容排名 |
| **Content & Copy** (7) | `copywriting`, `copy-editing`, `cold-email`, `emails`, `social`, `video`, `image` | 🔶 中 | 技术白皮书、客户案例、社交媒体 |
| **Conversion** (5) | `cro`, `signup`, `onboarding`, `popups`, `paywalls` | ⚪ 低 | B2B试用转化（网站试用流程） |
| **Paid & Distribution** (3) | `ads`, `ad-creative`, `public-relations` | 🔶 中 | 行业媒体PR、定向广告、技术会议 |
| **Measurement** (2) | `analytics`, `ab-testing` | ✅ 高 | 营销效果度量、A/B测试设计 |
| **Growth** (5) | `referrals`, `free-tools`, `churn-prevention`, `community-marketing`, `prospecting` | 🔶 中 | 社区运营、客户推荐、流失预防 |
| **Strategy** (6) | `marketing-plan`, `marketing-ideas`, `marketing-psychology`, `launch`, `pricing`, `offers` | ✅ 高 | 产品定价、市场计划、发布会策略 |
| **Sales & RevOps** (4) | `revops`, `sales-enablement`, `customer-research`, `product-marketing` | ✅ 高 | 客户调研、销售材料、产品定位 |
| **Other** (7) | `content-strategy`, `lead-magnets`, `co-marketing`, `directory-submissions`, `competitor-profiling`, `sms`, `community-marketing` | 🔶 中 | 内容规划、竞品分析、合作伙伴 |

> **注**: 共 47 个子技能目录。B2B 高相关 7 个 + 中相关 24 个 + 低相关 16 个。首次使用建议从 `analytics`(度量) + `customer-research`(客户) + `competitor-profiling`(竞品) 开始。

---

## 🔄 使用模式建议

| 阶段 | 推荐子技能 | 目标 |
|:-----|:-----------|:------|
| **调研期** | `customer-research`, `competitor-profiling`, `analytics` | 建立市场基线 |
| **策略期** | `marketing-plan`, `pricing`, `product-marketing`, `content-strategy` | 制定营销策略 |
| **执行期** | `copywriting`, `seo-audit`, `ads`, `cold-email`, `social` | 投放与内容产出 |
| **度量期** | `analytics`, `ab-testing`, `revops` | 优化与归因 |

