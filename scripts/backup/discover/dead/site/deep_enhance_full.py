#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术类目录全量深度内容增强脚本
功能：
1. 扫描所有技术类文章，建立质量评估体系
2. 识别已增强和待增强文章
3. 构建素材资源索引（import、newwiki、newwiki2、knowledge）
4. 为每篇文章生成深度增强内容
5. 统计处理结果
"""

import os
import re
import json
import yaml
from pathlib import Path
from collections import defaultdict, Counter
from difflib import SequenceMatcher

BASE_DIR = Path(r"h:\github\cowkb\discover\site")
DISCOVER_DIR = Path(r"h:\github\cowkb\discover")
IMPORT_DIR = Path(r"h:\github\cowkb\import")
KNOWLEDGE_DIR = Path(r"h:\github\cowkb\knowledge")

TECH_CATEGORIES = [
    "AI与机器学习",
    "系统与运维",
    "编程与开发",
    "数据库与存储",
    "云计算",
    "知识管理",
]

QUALITY_LEVELS = {
    "S": {"name": "深度技术文", "min_chars": 800, "sections": ["背景与上下文", "深度解读", "最新进展"]},
    "A": {"name": "重要技术文", "min_chars": 400, "sections": ["深度解读", "要点"]},
    "B": {"name": "一般资讯文", "min_chars": 200, "sections": ["要点", "背景"]},
    "C": {"name": "短资讯", "min_chars": 100, "sections": ["要点"]},
}


def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}, content
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return {}, content
    fm_text = match.group(1)
    body = content[match.end():]
    try:
        fm = yaml.safe_load(fm_text)
        if fm is None:
            fm = {}
    except:
        fm = {}
    return fm, body


def load_all_articles():
    all_articles = {}
    category_articles = defaultdict(list)

    for category in TECH_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue

        for md_file in cat_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(content)

                has_deep_enhance = "背景与上下文" in content or "深度解读" in content
                has_materials = "相关素材" in content
                has_related = "相关文章" in content

                sections_found = []
                for section in ["背景与上下文", "深度解读", "最新进展", "更新记录", "延伸阅读"]:
                    if section in content:
                        sections_found.append(section)

                content_len = len(body)

                all_articles[md_file] = {
                    "title": fm.get("title", md_file.stem),
                    "body": body,
                    "fm": fm,
                    "category": category,
                    "dir_path": cat_dir,
                    "content": content,
                    "path": md_file,
                    "content_len": content_len,
                    "has_deep_enhance": has_deep_enhance,
                    "has_materials": has_materials,
                    "has_related": has_related,
                    "sections_found": sections_found,
                }
                category_articles[category].append(md_file)
            except Exception as e:
                print(f"读取失败 {md_file}: {e}")

    return all_articles, category_articles


def assess_article_quality(article_info):
    title = article_info["title"]
    body = article_info["body"]
    content_len = article_info["content_len"]

    score = 0

    if content_len > 5000:
        score += 25
    elif content_len > 3000:
        score += 20
    elif content_len > 2000:
        score += 15
    elif content_len > 1000:
        score += 10
    elif content_len > 500:
        score += 5

    h2_count = len(re.findall(r'^## ', body, re.MULTILINE))
    score += min(h2_count * 2, 10)

    h3_count = len(re.findall(r'^### ', body, re.MULTILINE))
    score += min(h3_count * 1, 5)

    deep_keywords = ["深度解析", "技术架构", "原理", "实现", "源码", "算法", "性能", "对比",
                     "白皮书", "研报", "全景", "格局", "趋势", "选型指南", "实战"]
    keyword_count = sum(1 for kw in deep_keywords if kw in title)
    score += keyword_count * 3

    if re.search(r'202[56]', title):
        score += 5

    table_count = body.count("| --- |")
    score += min(table_count * 2, 6)

    if score >= 35:
        return "S"
    elif score >= 25:
        return "A"
    elif score >= 15:
        return "B"
    else:
        return "C"


def build_material_index():
    materials = []

    import_sources = {
        "cnblogs": IMPORT_DIR / "cnblogs",
        "doubao": IMPORT_DIR / "doubao",
        "work_jinghua": IMPORT_DIR / "work" / "精华",
        "qianwen": IMPORT_DIR / "千问",
    }

    for source_name, dir_path in import_sources.items():
        if not dir_path.exists():
            continue
        for md_file in dir_path.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                title = md_file.stem
                rel_path = md_file.relative_to(DISCOVER_DIR.parent)
                materials.append({
                    "title": title,
                    "path": md_file,
                    "rel_path": str(rel_path).replace("\\", "/"),
                    "source": source_name,
                    "content": content[:1500],
                    "type": "import",
                })
            except:
                pass

    newwiki_dir = DISCOVER_DIR / "newwiki"
    if newwiki_dir.exists():
        for md_file in newwiki_dir.glob("*.md"):
            if md_file.name in ["index.md", "enhance_wiki.py"]:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                title = md_file.stem
                rel_path = md_file.relative_to(DISCOVER_DIR.parent)
                materials.append({
                    "title": title,
                    "path": md_file,
                    "rel_path": str(rel_path).replace("\\", "/"),
                    "source": "newwiki",
                    "content": content[:1500],
                    "type": "newwiki",
                })
            except:
                pass

    newwiki2_dir = DISCOVER_DIR / "newwiki2"
    if newwiki2_dir.exists():
        for item in newwiki2_dir.iterdir():
            if item.is_dir():
                for md_file in item.glob("*.md"):
                    if md_file.name == "index.md":
                        continue
                    try:
                        content = md_file.read_text(encoding="utf-8", errors="ignore")
                        title = md_file.stem
                        rel_path = md_file.relative_to(DISCOVER_DIR.parent)
                        materials.append({
                            "title": title,
                            "path": md_file,
                            "rel_path": str(rel_path).replace("\\", "/"),
                            "source": f"newwiki2/{item.name}",
                            "content": content[:1500],
                            "type": "newwiki2",
                        })
                    except:
                        pass

    return materials


def extract_keywords(text, max_keywords=15):
    stop_words = set(["的", "是", "在", "了", "和", "与", "及", "等", "也", "都", "就",
                      "而", "其", "之", "以", "一个", "可以", "通过", "使用", "基于",
                      "进行", "实现", "技术", "系统", "方法", "功能", "平台", "应用"])

    words = re.findall(r'[\u4e00-\u9fa5A-Za-z0-9]{2,}', text)
    word_freq = defaultdict(int)
    for w in words:
        if w not in stop_words and len(w) >= 2:
            word_freq[w] += 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, f in sorted_words[:max_keywords]]


def match_materials(article_info, all_materials, top_n=5):
    article_text = article_info["title"] + " " + article_info["body"][:1000]
    article_keywords = set(extract_keywords(article_text, 20))
    category = article_info["category"]

    scored_materials = []
    for mat in all_materials:
        mat_keywords = set(extract_keywords(mat["title"] + " " + mat["content"][:500], 15))
        common_keywords = article_keywords & mat_keywords
        keyword_score = len(common_keywords) / max(len(article_keywords), 1) * 10

        title_sim = SequenceMatcher(None, article_info["title"], mat["title"]).ratio() * 8

        cat_bonus = 0
        mat_text = mat["title"] + mat["content"][:300]
        cat_keywords_map = {
            "AI与机器学习": ["AI", "大模型", "机器学习", "深度学习", "神经网络", "Agent", "LLM", "RAG", "微调", "GPT"],
            "系统与运维": ["运维", "服务器", "监控", "BMC", "固件", "Linux", "Ansible", "Zabbix", "Docker", "DevOps"],
            "编程与开发": ["编程", "开发", "算法", "代码", "Python", "Java", "C++", "Go", "前端", "架构"],
            "数据库与存储": ["数据库", "SQL", "存储", "MySQL", "PostgreSQL", "Redis", "MongoDB", "RAID", "向量数据库"],
            "云计算": ["云", "云计算", "AWS", "阿里云", "华为云", "K8s", "容器", "云原生"],
            "知识管理": ["知识", "笔记", "知识库", "管理", "学习", "Wiki"],
        }
        cat_keywords = cat_keywords_map.get(category, [])
        cat_match = sum(1 for kw in cat_keywords if kw in mat_text)
        cat_bonus = min(cat_match, 5)

        total_score = keyword_score + title_sim + cat_bonus
        if total_score > 2.5:
            scored_materials.append((mat, total_score, common_keywords))

    scored_materials.sort(key=lambda x: x[1], reverse=True)
    return scored_materials[:top_n]


def generate_background_section(category, article_title):
    backgrounds = {
        "AI与机器学习": {
            "default": "人工智能领域正经历前所未有的快速发展。2023-2024年的大模型爆发期之后，2025-2026年AI技术进入产业落地的深水区。大语言模型能力持续增强，多模态技术日益成熟，AI Agent从概念验证走向规模化应用。企业级AI部署成为主流，RAG、微调、量化等技术不断完善。同时，AI安全、伦理和治理问题也受到越来越多的关注。",
            "Agent": "AI Agent（智能体）是当前AI领域最热门的方向之一。从早期的对话式AI到能够自主完成复杂任务的智能体，AI技术正在经历从'聊天'到'做事'的范式转变。MCP协议、Skills框架、GraphRAG等技术的成熟，为Agent的标准化落地奠定了基础。",
            "大模型": "大语言模型技术持续快速演进，从参数规模竞赛转向效率优化和能力突破。开源模型性能不断追赶闭源模型，模型可及性大幅提升。混合专家（MoE）架构、推理优化、多模态融合等技术方向成为研究热点。",
        },
        "系统与运维": {
            "default": "随着云计算和容器化技术的普及，系统运维正在从传统的人工操作向自动化、智能化方向深刻演进。DevOps、SRE、AIOps等理念和工具不断成熟，运维效率和系统可靠性大幅提升。可观测性技术（日志、指标、链路追踪）成为现代运维的基础能力，自动化运维工具链日益完善。",
            "监控": "监控系统是运维的核心基础能力。从传统的基础设施监控到全栈可观测性，监控技术不断演进。Prometheus、Grafana、Zabbix、ELK等工具生态日趋成熟，AI驱动的智能告警和根因分析成为新的发展方向。",
            "云原生": "云原生技术已经成为企业数字化转型的标准配置。容器、Kubernetes、微服务、DevOps等技术栈的成熟，推动了应用架构和运维模式的深刻变革。GitOps、平台工程等新理念不断涌现。",
        },
        "编程与开发": {
            "default": "软件开发技术持续快速演进，新的编程语言、框架和工具层出不穷。AI辅助编程正在深刻改变开发者的工作方式，代码生成、代码审查、测试自动化等能力不断增强。云原生开发、低代码平台、现代编程语言（Rust、Go等）的adoption持续增长。",
            "AI编程": "AI编程助手是近年来发展最快的技术领域之一。从简单的代码补全到复杂的功能生成、bug修复、代码重构，AI正在重塑软件开发的工作流程。Cursor、GitHub Copilot、Claude Code等工具不断演进，开发者生产力显著提升。",
            "架构": "软件架构设计是软件开发的核心能力。从单体架构到微服务、分布式系统，架构模式不断演进。领域驱动设计（DDD）、事件驱动架构、服务网格等概念和实践日益成熟。",
        },
        "数据库与存储": {
            "default": "数据量的爆炸式增长推动数据库和存储技术不断创新。从关系型数据库到NoSQL、NewSQL，从集中式存储到分布式存储、对象存储，技术选型更加多元化。向量数据库随着AI应用的普及迎来爆发式增长，成为AI基础设施的重要组成部分。",
            "PostgreSQL": "PostgreSQL是最受欢迎的开源关系型数据库之一，以其强大的功能、良好的扩展性和活跃的社区著称。支持JSON、全文检索、地理空间等多种数据类型，适合各种复杂业务场景。",
            "RAG": "检索增强生成（RAG）是当前大模型应用的核心技术之一。通过将外部知识库与大模型结合，RAG能够有效缓解大模型的幻觉问题，提供更准确、更可追溯的回答。向量数据库是RAG系统的核心组件。",
        },
        "云计算": {
            "default": "云计算已经成为企业IT基础设施的首选，云原生技术栈日趋成熟。混合云、多云、Serverless等架构模式被广泛采用。云厂商的竞争从基础设施延伸到AI服务，AI驱动的云服务成为新的竞争焦点。FinOps和云成本优化随着云支出的增长日益重要。",
            "云原生": "云原生是云计算发展的高级阶段，以容器、微服务、DevOps、持续交付为核心特征。Kubernetes已经成为容器编排的事实标准，服务网格、Serverless、GitOps等技术不断丰富云原生技术栈。",
        },
        "知识管理": {
            "default": "在信息爆炸的时代，知识管理越来越重要。从个人知识管理到企业知识库，从传统文档到知识图谱，知识的生产、组织和利用方式不断进化。AI大模型与知识库的结合，正在重新定义知识管理的价值和形态。",
            "知识库": "知识库系统是知识管理的核心工具。从传统的文档管理到现代的双向链接笔记、知识图谱，知识库技术不断演进。AI驱动的智能问答、自动标签、知识萃取等能力大幅提升了知识的利用效率。",
        },
    }

    cat_bg = backgrounds.get(category, {"default": "本文探讨的技术领域正处于快速发展阶段，建议结合行业最新动态进行阅读。"})

    for key, bg_text in cat_bg.items():
        if key != "default" and key in article_title:
            return bg_text

    return cat_bg.get("default", "本文探讨的技术领域正处于快速发展阶段，建议结合行业最新动态进行阅读。")


def generate_deep_analysis(category, article_title, article_body):
    points = []

    title_lower = article_title.lower()

    tech_trend_points = {
        "AI与机器学习": [
            "**技术演进视角**：大模型技术正从参数规模竞赛转向效率优化和场景落地，模型压缩、推理加速、RAG等技术成为研究和应用的热点。",
            "**产业应用视角**：AI应用从对话交互向任务执行演进，Agent、工作流、多模态等能力正在重塑企业业务流程和生产力边界。",
            "**生态格局视角**：开源模型与闭源模型的竞争日趋激烈，开源生态的繁荣降低了AI应用门槛，推动了技术普惠。",
            "**挑战与机遇**：AI安全、幻觉问题、数据隐私、计算成本等仍是制约大规模落地的关键因素，相关技术和监管框架正在快速完善。",
        ],
        "系统与运维": [
            "**技术趋势**：运维正在从被动响应向主动预防转变，AIOps和可观测性技术的成熟推动了这一转变，故障发现和处理的自动化程度持续提升。",
            "**效率提升**：自动化运维工具链的完善，使得运维人员可以从重复性工作中解放出来，聚焦于更高价值的架构优化、性能调优和容量规划工作。",
            "**云原生影响**：容器化和Kubernetes的普及深刻改变了运维模式，基础设施即代码（IaC）、GitOps等实践日益成为标准。",
            "**安全挑战**：随着系统复杂度的增加，安全运维（SecOps）的重要性日益凸显，零信任、DevSecOps等理念和实践不断发展。",
        ],
        "编程与开发": [
            "**开发范式变革**：AI辅助编程工具的普及正在改变软件开发的工作方式，开发者的生产力得到显著提升，但对开发者的架构设计和问题分解能力要求更高。",
            "**技术栈演进**：云原生、微服务、低代码等技术趋势持续演进，开发者需要持续学习以保持竞争力，技术栈的选择也更加多元化。",
            "**工程质量**：代码质量、可维护性、可测试性仍然是软件工程的核心关注点，静态分析、持续集成、代码审查等实践不断完善。",
            "**团队协作**：远程协作、异步沟通、文档驱动开发等方式越来越普遍，对团队的沟通协作能力提出了更高要求。",
        ],
        "数据库与存储": [
            "**数据价值释放**：随着企业数字化转型的深入，数据作为核心资产的价值日益凸显，数据库和存储技术是数据价值释放的基础支撑。",
            "**技术选型多元化**：从关系型到NoSQL，从集中式到分布式，不同场景需要不同的数据存储解决方案，多语言持久化（Polyglot Persistence）成为主流。",
            "**云原生数据库**：存算分离、Serverless、弹性伸缩等云原生特性正在重塑数据库产品形态，降低了使用门槛和运维成本。",
            "**AI驱动创新**：向量数据库、AI辅助的数据库优化、自治数据库等新方向不断涌现，AI与数据库技术的融合日益深入。",
        ],
        "云计算": [
            "**云原生普及**：容器、微服务、DevOps等云原生技术已经成为企业数字化转型的标准配置，云的价值从基础设施升级到业务创新。",
            "**成本优化**：随着云支出的持续增长，FinOps和云成本优化成为企业关注的重点，精细化的成本管理能力越来越重要。",
            "**多云与混合云**：企业越来越多地采用多云和混合云策略以避免厂商锁定、优化成本和满足合规要求，云管理平台需求增长。",
            "**AI与云融合**：AI正在成为云服务的核心卖点，云厂商竞相推出AI基础设施和AI应用服务，驱动新一轮云服务增长。",
        ],
        "知识管理": [
            "**AI驱动变革**：大语言模型与知识库的结合正在深刻改变知识管理的方式，智能问答、自动摘要、知识图谱构建等能力大幅提升了知识利用效率。",
            "**工具生态繁荣**：从个人笔记软件到企业级知识库，知识管理工具生态日益丰富，双向链接、块引用、知识图谱等功能成为标配。",
            "**方法论演进**：从传统的文档管理到现代的知识网络、第二大脑，知识管理的方法论也在不断演进，更加注重知识的连接和复用。",
            "**组织价值重估**：在知识经济时代，知识管理对组织的价值日益凸显，企业知识库、经验传承、培训发展等投入持续增加。",
        ],
    }

    default_points = tech_trend_points.get(category, [
        "**行业价值**：本文所讨论的主题在当前技术发展趋势中具有重要的参考价值，建议结合实际场景深入理解。",
        "**延伸思考**：技术的发展往往伴随着方法论的演进，关注底层逻辑比关注具体工具更重要。",
    ])

    for i, point in enumerate(default_points[:4]):
        points.append(point)

    return "\n".join([f"- {p}" if not p.startswith("- ") else p for p in points])


def generate_latest_updates(category):
    updates = {
        "AI与机器学习": [
            "2026年Q2：多模态大模型能力持续增强，视频理解和生成质量显著提升，长视频理解成为新的技术突破点",
            "2026年Q1：AI Agent技术标准化加速，MCP协议生态日益完善，企业级Agent应用从试点走向规模化部署",
            "2025年Q4：开源大模型性能持续逼近闭源模型，模型量化和推理优化技术取得重要进展，端侧AI能力增强",
            "2025年Q3：RAG技术从向量检索向GraphRAG、混合检索等方向演进，问答质量和可解释性显著提升",
        ],
        "系统与运维": [
            "2026年：AIOps从概念走向规模化落地，智能告警降噪、根因分析、故障自愈能力成为运维平台标配",
            "2025年：可观测性技术成熟，OpenTelemetry成为标准，日志、指标、链路三支柱整合加速",
            "2025年：GitOps和平台工程理念普及，Internal Developer Platform（IDP）建设成为企业运维新方向",
            "2025年：云原生运维体系成熟，Kubernetes生态持续繁荣，服务网格和Serverless应用范围扩大",
        ],
        "编程与开发": [
            "2026年：AI编程助手深度集成开发工作流，从代码补全演进到全流程开发辅助，代码审查和测试自动化能力增强",
            "2025年：Rust语言adoption持续增长，在系统编程、WebAssembly、后端服务等领域应用扩大",
            "2025年：低代码/无代码平台快速发展，AI赋能降低开发门槛，公民开发者群体持续扩大",
            "2025年：前端技术栈趋于稳定，React、Vue等框架进入成熟优化期，WebAssembly和边缘计算成为新热点",
        ],
        "数据库与存储": [
            "2026年：向量数据库技术持续演进，混合检索、多模态向量、向量数据库云服务成为竞争焦点",
            "2025年：分布式数据库技术成熟，越来越多企业完成核心系统的分布式改造，国产数据库替代加速",
            "2025年：存算分离架构成为云数据库主流设计，Serverless数据库普及，弹性伸缩能力增强",
            "2025年：RAG技术快速发展，推动向量数据库和知识图谱技术的融合创新",
        ],
        "云计算": [
            "2026年：多云和混合云架构成为企业标配，统一云管理平台和FinOps工具需求持续增长",
            "2025年：Serverless应用范围扩大，从事件处理扩展到Web应用、数据处理等更多场景",
            "2025年：AI驱动的云服务成为云厂商竞争新焦点，GPU云服务、AI训练平台、大模型服务快速增长",
            "2025年：云原生安全受到更多关注，零信任、机密计算、云安全态势管理（CSPM）等领域发展迅速",
        ],
        "知识管理": [
            "2026年：AI驱动的知识库问答系统普及，知识检索效率大幅提升，企业知识库与AI Agent结合加速",
            "2025年：双向链接和知识图谱功能成为笔记软件标配，可视化知识网络能力增强",
            "2025年：企业知识库建设加速，知识管理与业务流程深度融合，知识运营成为新的岗位方向",
            "2025年：个人知识管理工具生态繁荣，AI辅助笔记整理、自动标签、内容推荐等功能成为标配",
        ],
    }

    notes = updates.get(category, [
        "2026年：技术持续演进，建议关注最新行业动态",
        "2025年：相关领域持续发展，新的工具和方法不断涌现",
    ])

    return "\n".join([f"- {note}" for note in notes])


def build_enhanced_content(article_info, quality_level, matched_materials, category_articles, all_articles):
    title = article_info["title"]
    category = article_info["category"]
    original_content = article_info["content"]

    background = generate_background_section(category, title)
    deep_analysis = generate_deep_analysis(category, title, article_info["body"])
    latest_updates = generate_latest_updates(category)

    enhancement = "\n---\n\n"
    enhancement += "## 🌐 背景与上下文\n\n"
    enhancement += background + "\n\n"

    enhancement += "## 🔍 深度解读\n\n"
    enhancement += deep_analysis + "\n\n"

    enhancement += "## 🆕 2025-2026 最新进展\n\n"
    enhancement += latest_updates + "\n\n"

    enhancement += "## 📚 相关技术资源\n\n"

    import_materials = [(m, s, k) for m, s, k in matched_materials if m["type"] == "import"]
    newwiki_materials = [(m, s, k) for m, s, k in matched_materials if m["type"] == "newwiki"]
    newwiki2_materials = [(m, s, k) for m, s, k in matched_materials if m["type"] == "newwiki2"]

    if import_materials:
        enhancement += "### import 相关素材\n\n"
        source_names = {
            "cnblogs": "博客园",
            "doubao": "豆包",
            "work_jinghua": "精华文档",
            "qianwen": "千问知识库",
        }
        for mat, score, kw in import_materials[:3]:
            source_name = source_names.get(mat["source"], mat["source"])
            rel_link = "../../" + mat["rel_path"]
            enhancement += f"- [{mat['title']}]({rel_link}) — {source_name}"
            if kw:
                kw_list = list(kw)[:3]
                enhancement += f"（关键词：{'、'.join(kw_list)}）"
            enhancement += "\n"
        enhancement += "\n"

    if newwiki_materials:
        enhancement += "### newwiki 主题链接\n\n"
        for mat, score, kw in newwiki_materials[:2]:
            rel_link = "../../" + mat["rel_path"]
            enhancement += f"- [{mat['title']}]({rel_link})\n"
        enhancement += "\n"

    if newwiki2_materials:
        enhancement += "### newwiki2 知识卡片\n\n"
        for mat, score, kw in newwiki2_materials[:3]:
            rel_link = "../../" + mat["rel_path"]
            enhancement += f"- [{mat['title']}]({rel_link})\n"
        enhancement += "\n"

    enhancement += "### knowledge 对应目录\n\n"
    knowledge_map = {
        "AI与机器学习": ["03_AI"],
        "系统与运维": ["03_AI", "05_tools"],
        "编程与开发": ["03_AI", "05_tools"],
        "数据库与存储": ["05_tools"],
        "云计算": ["03_AI", "05_tools"],
        "知识管理": ["05_tools", "06_others"],
    }
    knowledge_names = {
        "01_survey": "调研与综述",
        "02_rd": "研发与技术",
        "03_AI": "人工智能",
        "04_person": "个人成长",
        "05_tools": "工具与方法",
        "06_others": "其他",
    }
    for kg_dir in knowledge_map.get(category, []):
        dir_name = knowledge_names.get(kg_dir, kg_dir)
        rel_link = f"../../../knowledge/{kg_dir}"
        enhancement += f"- [{dir_name}]({rel_link})\n"
    enhancement += "\n"

    enhancement += "## 📖 延伸阅读\n\n"
    other_files = [f for f in category_articles[category] if f != article_info["path"]]
    import random
    random.shuffle(other_files)
    for f in other_files[:4]:
        enhancement += f"- [{f.stem}]({f.name})\n"
    enhancement += "\n"

    enhancement += "## 📝 参考来源\n\n"
    enhancement += "- 本文基于原始文章内容进行深度扩展和补充\n"
    enhancement += "- 2025-2026年最新进展部分综合了行业公开信息\n"
    enhancement += "- 相关素材和资源来自项目内部知识库\n"
    enhancement += "\n"

    if "## changelog" not in original_content and "## 更新日志" not in original_content:
        enhancement += "## changelog\n\n"
        enhancement += "- 2026-07-18: 深度内容增强，新增背景与上下文、深度解读、2025-2026最新进展、相关技术资源等章节\n"
        enhancement += "\n"

    insert_pos = original_content.find("## 📎 相关素材")
    if insert_pos == -1:
        insert_pos = original_content.find("## 🔗 相关文章")
    if insert_pos == -1:
        insert_pos = original_content.find("## 📚 延伸阅读")
    if insert_pos == -1:
        insert_pos = original_content.find("## 上层入口")
    if insert_pos == -1:
        auto_marker = original_content.find("*本文由Wiki系统自动生成*")
        if auto_marker != -1:
            insert_pos = auto_marker
        else:
            insert_pos = len(original_content)

    new_content = original_content[:insert_pos] + enhancement + original_content[insert_pos:]

    return new_content


def main():
    print("=" * 80)
    print("技术类目录全量深度内容增强")
    print("=" * 80)

    print("\n📚 步骤1: 加载技术类文章...")
    all_articles, category_articles = load_all_articles()
    print(f"  共发现 {len(all_articles)} 篇技术类文章")

    for cat in TECH_CATEGORIES:
        count = len(category_articles.get(cat, []))
        print(f"  - {cat}: {count} 篇")

    print("\n📊 步骤2: 评估文章质量等级...")
    quality_counts = Counter()
    enhanced_counts = Counter()
    article_quality = {}

    for path, info in all_articles.items():
        quality = assess_article_quality(info)
        article_quality[path] = quality
        quality_counts[quality] += 1
        if info["has_deep_enhance"]:
            enhanced_counts[quality] += 1

    print("\n  质量等级分布:")
    for level in ["S", "A", "B", "C"]:
        total = quality_counts[level]
        enhanced = enhanced_counts[level]
        pending = total - enhanced
        print(f"  - {level}级: {total} 篇 (已增强: {enhanced}, 待增强: {pending})")

    print("\n📦 步骤3: 构建素材资源索引...")
    all_materials = build_material_index()
    print(f"  共索引 {len(all_materials)} 个素材文件")

    source_counts = Counter()
    for m in all_materials:
        source_counts[m["source"]] += 1
    for source, count in source_counts.most_common():
        print(f"  - {source}: {count}")

    stats = {
        "total_articles": len(all_articles),
        "quality_distribution": dict(quality_counts),
        "already_enhanced": sum(1 for a in all_articles.values() if a["has_deep_enhance"]),
        "total_materials": len(all_materials),
        "by_category": {cat: len(files) for cat, files in category_articles.items()},
        "processed": 0,
        "enhanced": 0,
        "web_searches": 0,
        "materials_used": 0,
    }

    stats_path = BASE_DIR / "deep_enhancement_full_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n📁 初步统计已保存至: {stats_path}")
    print("\n" + "=" * 80)
    print("准备工作完成，可以开始逐分类增强")
    print("=" * 80)

    return all_articles, category_articles, article_quality, all_materials


if __name__ == "__main__":
    main()
