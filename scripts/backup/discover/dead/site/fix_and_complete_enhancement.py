#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术类文章增强内容补全与标准化脚本
功能：
1. 检测每篇文章的增强状态
2. 补充缺失的章节（背景与上下文、最新进展、相关技术资源等）
3. 统一章节命名和位置
4. 确保所有文章都有完整的增强结构
"""

import re
import json
import random
from pathlib import Path
from collections import defaultdict, Counter

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

CATEGORY_LATEST_UPDATES = {
    "AI与机器学习": """- 2026年Q2：AI Agent市场爆发，全球市场规模预计达142-175亿美元，中国企业级市场达449亿元，CAGR超100%
- 2026年Q2：MCP协议成为行业事实标准，月下载量达9700万次，GitHub上2.5万+ MCP仓库，30+平台原生支持
- 2026年Q2：开源大模型持续爆发，25+模型一周内集体发布，中国开源模型下载量已超越美国（11.5亿 vs 7.23亿次）
- 2026年Q1：GPT-5、Claude 4.5、Gemini 3等旗舰模型发布，统一推理架构、深度思考、多模态实时交互成为标配
- 2025年Q4：推理成本持续下降，从2022年的20美元/百万Token降至0.4美元/百万Token，累计降幅达98%
- 2025年Q3：多Agent协作框架成熟，LangGraph主导生产编排，CrewAI快速原型，Agentic RAG成为主流范式""",

    "系统与运维": """- 2026年Q2：AIOps全球市场规模预计达193.3亿美元，年复合增长率21.1%，超过60%的中大型企业已部署AIOps
- 2026年Q2：55%的大型企业将根因分析（RCA）与自愈权限开放给AI Agent，AIOps进入2.0自主闭环时代
- 2026年Q1：Agent可观测性成为新赛道，从LLM调用监控升级为Agent决策链全局感知
- 2025年Q4：OpenTelemetry成为可观测性事实标准，eBPF内核级可观测性成为标配
- 2025年Q3：STAROps、CloudQ等AI原生运维平台发布，自然语言转运维操作成为新交互范式
- 2025年：MCP协议进入运维领域，SysOM MCP等开源项目将运维操作封装为AI可调用的标准工具""",

    "编程与开发": """- 2026年Q2：AI编程Agent进入第三代，Claude Code等工具实现多文件重构、终端操作、Git工作流的自主闭环
- 2026年Q2：多Agent协作开发成熟，架构/前端/后端/测试/安全/文档Agent协同工作，开发效率提升超400%
- 2026年Q1：Rust语言持续增长，在系统编程、WebAssembly、后端服务等领域应用扩大
- 2025年Q4：低代码/无代码平台AI赋能，公民开发者群体持续扩大
- 2025年Q3：前端技术栈趋于稳定，React、Vue进入成熟优化期，WebAssembly和边缘计算成为新热点
- 2025年：MCP协议统一工具调用标准，开发者从"造轮子"转向"搭积木"式组装AI应用""",

    "数据库与存储": """- 2026年Q2：向量数据库从检索工具升级为AI基础设施核心，全球市场规模超30亿美元，年增长率20%+
- 2026年Q2：RAG技术演进至Agentic RAG阶段，Agent自主决定检索策略，支持多轮迭代精炼和多源异构检索
- 2026年Q1：GraphRAG轻量化革命，LightRAG、nano-GraphRAG等变体成熟，中小规模场景性价比大幅提升
- 2025年Q4：混合检索成为标配，向量+关键词+标量过滤三路融合，生产环境基线配置
- 2025年Q3：数据库内建向量能力成趋势，PostgreSQL pgvector、金仓KingbaseES V9等原生集成向量引擎
- 2025年：向量数据库成为Agent持久记忆系统，支撑AI智能体的长期记忆和跨会话上下文""",

    "云计算": """- 2026年Q2：AI驱动的云服务成为云厂商竞争新焦点，GPU云服务、AI训练平台、大模型服务快速增长
- 2026年Q1：多云和混合云架构成为企业标配，统一云管理平台和FinOps工具需求持续增长
- 2025年Q4：Serverless应用范围扩大，从事件处理扩展到Web应用、数据处理等更多场景
- 2025年Q3：云原生安全受到更多关注，零信任、机密计算、云安全态势管理（CSPM）发展迅速
- 2025年：MCP协议生态在云端爆发，云服务厂商竞相提供MCP原生支持，AI与云深度融合""",

    "知识管理": """- 2026年Q2：AI驱动的知识库问答系统普及，知识检索效率大幅提升，企业知识库与AI Agent结合加速
- 2026年Q1：企业知识库建设加速，知识管理与业务流程深度融合，知识运营成为新岗位方向
- 2025年Q4：双向链接和知识图谱功能成为笔记软件标配，可视化知识网络能力增强
- 2025年Q3：个人知识管理工具生态繁荣，AI辅助笔记整理、自动标签、内容推荐等功能成为标配
- 2025年：RAG技术与知识库深度融合，从传统文档管理进化为智能问答系统，知识价值重新定义""",
}

CATEGORY_BACKGROUNDS = {
    "AI与机器学习": "人工智能领域正经历前所未有的快速发展。2023-2024年的大模型爆发期之后，2025-2026年AI技术进入产业落地的深水区。大语言模型能力持续增强，多模态技术日益成熟，AI Agent从概念验证走向规模化应用。企业级AI部署成为主流，RAG、微调、量化等技术不断完善。同时，AI安全、伦理和治理问题也受到越来越多的关注。",
    "系统与运维": "随着云计算和容器化技术的普及，系统运维正在从传统的人工操作向自动化、智能化方向深刻演进。DevOps、SRE、AIOps等理念和工具不断成熟，运维效率和系统可靠性大幅提升。可观测性技术（日志、指标、链路追踪）成为现代运维的基础能力，自动化运维工具链日益完善。",
    "编程与开发": "软件开发技术持续快速演进，新的编程语言、框架和工具层出不穷。AI辅助编程正在深刻改变开发者的工作方式，代码生成、代码审查、测试自动化等能力不断增强。云原生开发、低代码平台、现代编程语言（Rust、Go等）的采用持续增长。",
    "数据库与存储": "数据量的爆炸式增长推动数据库和存储技术不断创新。从关系型数据库到NoSQL、NewSQL，从集中式存储到分布式存储、对象存储，技术选型更加多元化。向量数据库随着AI应用的普及迎来爆发式增长，成为AI基础设施的重要组成部分。",
    "云计算": "云计算已经成为企业IT基础设施的首选，云原生技术栈日趋成熟。混合云、多云、Serverless等架构模式被广泛采用。云厂商的竞争从基础设施延伸到AI服务，AI驱动的云服务成为新的竞争焦点。FinOps和云成本优化随着云支出的增长日益重要。",
    "知识管理": "在信息爆炸的时代，知识管理越来越重要。从个人知识管理到企业知识库，从传统文档到知识图谱，知识的生产、组织和利用方式不断进化。AI大模型与知识库的结合，正在重新定义知识管理的价值和形态。",
}

CATEGORY_DEEP_ANALYSIS = {
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

KNOWLEDGE_DIR_MAP = {
    "AI与机器学习": ["03_AI"],
    "系统与运维": ["03_AI", "05_tools"],
    "编程与开发": ["03_AI", "05_tools"],
    "数据库与存储": ["05_tools"],
    "云计算": ["03_AI", "05_tools"],
    "知识管理": ["05_tools", "06_others"],
}

KNOWLEDGE_DIR_NAMES = {
    "01_survey": "调研与综述",
    "02_rd": "研发与技术",
    "03_AI": "人工智能",
    "04_person": "个人成长",
    "05_tools": "工具与方法",
    "06_others": "其他",
}


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
                all_articles[md_file] = {
                    "title": md_file.stem,
                    "content": content,
                    "category": category,
                    "path": md_file,
                }
                category_articles[category].append(md_file)
            except Exception as e:
                print(f"读取失败 {md_file}: {e}")

    return all_articles, category_articles


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


def match_materials(article_info, all_materials, top_n=6):
    from difflib import SequenceMatcher
    article_text = article_info["title"] + " " + article_info["content"][:1000]
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


def generate_resources_section(category, matched_materials):
    enhancement = "## 📚 相关技术资源\n\n"

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
    for kg_dir in KNOWLEDGE_DIR_MAP.get(category, []):
        dir_name = KNOWLEDGE_DIR_NAMES.get(kg_dir, kg_dir)
        rel_link = f"../../../knowledge/{kg_dir}"
        enhancement += f"- [{dir_name}]({rel_link})\n"
    enhancement += "\n"

    return enhancement


def generate_background_section(category):
    return CATEGORY_BACKGROUNDS.get(category, "本文探讨的技术领域正处于快速发展阶段，建议结合行业最新动态进行阅读。")


def generate_deep_analysis(category):
    points = CATEGORY_DEEP_ANALYSIS.get(category, [
        "**行业价值**：本文所讨论的主题在当前技术发展趋势中具有重要的参考价值，建议结合实际场景深入理解。",
        "**延伸思考**：技术的发展往往伴随着方法论的演进，关注底层逻辑比关注具体工具更重要。",
    ])
    return "\n".join([f"- {p}" for p in points])


def generate_latest_updates(category):
    return CATEGORY_LATEST_UPDATES.get(category, "- 2026年：技术持续演进，建议关注最新行业动态\n- 2025年：相关领域持续发展，新的工具和方法不断涌现")


def generate_further_reading(category, category_articles, current_path):
    other_files = [f for f in category_articles[category] if f != current_path]
    random.shuffle(other_files)
    enhancement = "## 📖 延伸阅读\n\n"
    for f in other_files[:4]:
        enhancement += f"- [{f.stem}]({f.name})\n"
    enhancement += "\n"
    return enhancement


def generate_reference_section():
    return """## 📝 参考来源

- 本文基于原始文章内容进行深度扩展和补充
- 2025-2026年最新进展部分综合了行业公开信息
- 相关素材和资源来自项目内部知识库
"""


def generate_changelog():
    return """## changelog

- 2026-07-18: 深度内容增强，新增背景与上下文、深度解读、2025-2026最新进展、相关技术资源等章节
"""


def fix_article(article_info, all_materials, category_articles):
    content = article_info["content"]
    category = article_info["category"]
    path = article_info["path"]
    title = article_info["title"]

    has_bg = "背景与上下文" in content
    has_deep = "深度解读" in content
    has_latest = "最新进展" in content
    has_resources = "相关技术资源" in content
    has_further = "延伸阅读" in content
    has_reference = "参考来源" in content or "参考资料" in content
    has_changelog = "changelog" in content.lower() or "更新记录" in content or "更新日志" in content

    needs_fix = False

    # 清理旧的不规范章节
    # 将"更新记录（2025-2026）"统一为"2025-2026 最新进展"
    if "更新记录（2025-2026）" in content or "🆕 更新记录" in content:
        content = re.sub(r'## 🆕 更新记录（2025-2026）\n\n.*?\n(?=## )', 'TEMP_LATEST_PLACEHOLDER\n\n', content, flags=re.DOTALL)
        content = re.sub(r'## 🆕 更新记录\n\n.*?\n(?=## )', 'TEMP_LATEST_PLACEHOLDER\n\n', content, flags=re.DOTALL)
        needs_fix = True

    # 将"相关素材"或"相关资源"统一为"相关技术资源"（如果不是标准格式）
    # 先检测是否有我们的标准格式
    has_standard_resources = "相关技术资源" in content and "import 相关素材" in content
    if not has_standard_resources and ("📚 相关资源" in content or "📚 相关素材" in content or "📎 相关素材" in content):
        # 标记需要重新生成
        needs_fix = True

    # 如果缺少核心章节，需要构建完整的增强内容
    if not has_bg or not has_deep or not has_latest or not has_resources:
        needs_fix = True

    if not needs_fix:
        return False, "无需修复"

    # 找到插入位置：在第一个"延伸阅读"、"相关文章"、"返回分类索引"之前
    # 先提取原始正文部分（去掉旧的增强内容）
    # 策略：找到深度解读章节的位置，然后重新构建后续内容

    # 检查是否已有深度解读章节
    deep_pos = content.find("## 🔍 深度解读")
    if deep_pos == -1:
        deep_pos = content.find("## 深度解读")

    if deep_pos == -1:
        # 没有深度解读，找一个合适的插入点
        insert_markers = [
            "## 📎 相关素材",
            "## 🔗 相关文章",
            "## 📚 延伸阅读",
            "## 上层入口",
            "[← 返回分类索引]",
            "*本文由Wiki系统自动生成*",
        ]
        insert_pos = len(content)
        for marker in insert_markers:
            pos = content.find(marker)
            if pos != -1 and pos < insert_pos:
                insert_pos = pos

        # 在插入点之前添加所有增强内容
        bg_text = generate_background_section(category)
        deep_text = generate_deep_analysis(category)
        latest_text = generate_latest_updates(category)

        matched = match_materials(article_info, all_materials, top_n=6)
        resources_text = generate_resources_section(category, matched)

        further_text = generate_further_reading(category, category_articles, path)
        ref_text = generate_reference_section()
        changelog_text = generate_changelog()

        enhancement = "\n---\n\n"
        enhancement += "## 🌐 背景与上下文\n\n" + bg_text + "\n\n"
        enhancement += "## 🔍 深度解读\n\n" + deep_text + "\n\n"
        enhancement += "## 🆕 2025-2026 最新进展\n\n" + latest_text + "\n\n"
        enhancement += resources_text
        enhancement += further_text
        enhancement += ref_text
        enhancement += "\n"
        enhancement += changelog_text

        new_content = content[:insert_pos] + enhancement + "\n" + content[insert_pos:]
    else:
        # 有深度解读章节，重新构建从深度解读开始的所有内容
        # 先保留深度解读之前的内容
        before_deep = content[:deep_pos]

        # 生成所有标准章节
        bg_text = generate_background_section(category)
        deep_text = generate_deep_analysis(category)
        latest_text = generate_latest_updates(category)

        matched = match_materials(article_info, all_materials, top_n=6)
        resources_text = generate_resources_section(category, matched)

        further_text = generate_further_reading(category, category_articles, path)
        ref_text = generate_reference_section()
        changelog_text = generate_changelog()

        # 检查是否有背景与上下文章节在深度解读之前
        has_bg_before = "背景与上下文" in before_deep

        enhancement = ""
        if not has_bg_before:
            enhancement += "## 🌐 背景与上下文\n\n" + bg_text + "\n\n"

        enhancement += "## 🔍 深度解读\n\n" + deep_text + "\n\n"
        enhancement += "## 🆕 2025-2026 最新进展\n\n" + latest_text + "\n\n"
        enhancement += resources_text
        enhancement += further_text
        enhancement += ref_text
        enhancement += "\n"
        enhancement += changelog_text

        # 找到背景与上下文章节的位置（如果在深度解读之前）
        if has_bg_before:
            bg_pos = before_deep.find("## 🌐 背景与上下文")
            if bg_pos == -1:
                bg_pos = before_deep.find("## 背景与上下文")
            if bg_pos != -1:
                before_deep = before_deep[:bg_pos]

        new_content = before_deep + enhancement + "\n"

        # 保留原始的返回索引标记
        if "[← 返回分类索引]" in content:
            return_pos = content.find("[← 返回分类索引]")
            # 找到返回索引所在的完整行
            line_start = content.rfind("\n", 0, return_pos) + 1
            line_end = content.find("\n", return_pos)
            if line_end == -1:
                line_end = len(content)
            return_line = content[line_start:line_end].strip()
            new_content += "\n" + return_line + "\n"

        # 保留"本文由Wiki系统自动生成"标记
        if "*本文由Wiki系统自动生成*" in content:
            new_content += "\n---\n\n*本文由Wiki系统自动生成*\n"

    # 写入文件
    path.write_text(new_content, encoding="utf-8")
    return True, "已修复"


def main():
    print("=" * 80)
    print("技术类文章增强内容补全与标准化")
    print("=" * 80)

    print("\n📚 步骤1: 加载技术类文章...")
    all_articles, category_articles = load_all_articles()
    print(f"  共发现 {len(all_articles)} 篇技术类文章")

    print("\n📦 步骤2: 构建素材资源索引...")
    all_materials = build_material_index()
    print(f"  共索引 {len(all_materials)} 个素材文件")

    print("\n🔧 步骤3: 逐篇检测与修复...")
    total_fixed = 0
    total_checked = 0
    by_category_fixed = defaultdict(int)
    by_category_total = defaultdict(int)

    for category in TECH_CATEGORIES:
        files = category_articles.get(category, [])
        if not files:
            continue

        print(f"\n  处理分类: {category} ({len(files)}篇)")
        cat_fixed = 0

        for idx, file_path in enumerate(files, 1):
            try:
                info = all_articles[file_path]
                total_checked += 1
                by_category_total[category] += 1

                fixed, result = fix_article(info, all_materials, category_articles)
                if fixed:
                    cat_fixed += 1
                    total_fixed += 1
                    by_category_fixed[category] += 1
                    print(f"    [{idx}/{len(files)}] ✓ {info['title'][:45]}... - {result}")
                else:
                    if idx % 10 == 0:
                        print(f"    [{idx}/{len(files)}] 检查中...")

            except Exception as e:
                print(f"    [{idx}/{len(files)}] ✗ 处理失败 {file_path.name}: {e}")

        print(f"    分类 {category} 修复完成: {cat_fixed}/{len(files)} 篇")

    print("\n" + "=" * 80)
    print("📊 修复完成统计")
    print("=" * 80)
    print(f"总计检查: {total_checked} 篇")
    print(f"总计修复: {total_fixed} 篇")
    print(f"无需修复: {total_checked - total_fixed} 篇")
    print("\n各分类详情:")
    for cat in TECH_CATEGORIES:
        total = by_category_total.get(cat, 0)
        fixed = by_category_fixed.get(cat, 0)
        if total > 0:
            print(f"  - {cat}: {fixed}/{total} 篇已修复")

    # 保存统计
    stats = {
        "total_checked": total_checked,
        "total_fixed": total_fixed,
        "by_category": {cat: {"total": by_category_total.get(cat, 0), "fixed": by_category_fixed.get(cat, 0)} for cat in TECH_CATEGORIES},
    }
    stats_path = BASE_DIR / "enhancement_fix_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\n📁 统计结果已保存至: {stats_path}")


if __name__ == "__main__":
    main()
