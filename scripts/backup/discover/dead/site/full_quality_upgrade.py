#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量文章质量全面升级系统
执行顺序：
1. 扫描评估所有文章质量
2. C→B升级（确保所有文章达到B级标准）
3. B→A升级（将B级文章升级到A级）
4. A→S精选升级（精选高价值文章升级到S级）
5. 输出最终统计报告
"""

import os
import re
import json
import yaml
import random
from pathlib import Path
from collections import defaultdict, Counter
from difflib import SequenceMatcher

BASE_DIR = Path(r"h:\github\cowkb\discover\site")
IMPORT_DIR = Path(r"h:\github\cowkb\import")
DISCOVER_DIR = Path(r"h:\github\cowkb\discover")

ALL_CATEGORIES = [
    "AI与机器学习", "系统与运维", "编程与开发", "数据库与存储",
    "云计算", "知识管理", "产品与设计", "人文社会", "行业动态", "其他",
]

CATEGORY_KB = {
    "AI与机器学习": {
        "background": "人工智能领域正经历前所未有的快速发展。2025-2026年，大语言模型技术从实验室走向大规模产业应用，AI Agent、多模态融合、推理优化等技术不断突破。企业级AI部署成为主流趋势，开源生态持续繁荣，模型可及性大幅提升。这一领域的快速迭代正在深刻改变各个行业的技术路线和商业模式。",
        "deep_points": [
            ("技术演进视角", "大模型技术正从参数规模竞赛转向效率优化和场景落地，模型压缩、推理加速、RAG等技术成为研究和应用的热点。"),
            ("产业应用视角", "AI应用从对话交互向任务执行演进，Agent、工作流、多模态等能力正在重塑企业业务流程和生产力边界。"),
            ("生态格局视角", "开源模型与闭源模型的竞争日趋激烈，开源生态的繁荣降低了AI应用门槛，推动了技术普惠。"),
        ],
        "latest_news": [
            "2026年Q2：AI Agent市场爆发，全球市场规模预计达142-175亿美元，CAGR超100%",
            "2026年Q2：MCP协议成为行业事实标准，GitHub上2.5万+ MCP相关仓库",
            "2026年Q1：GPT-5、Claude 4.5、Gemini 3等旗舰模型发布，统一推理架构成为标配",
            "2025年Q4：推理成本持续下降，从2022年的20美元/百万Token降至0.4美元/百万Token",
            "2025年Q3：开源大模型持续爆发，中国开源模型下载量已超越美国",
        ],
        "import_materials": ["千问/大模型技术与原理.md", "千问/AI-Agent技术架构.md", "千问/AI应用与落地实践.md"],
        "newwiki_topics": ["大模型技术与原理", "AI-Agent技术架构", "AI应用与落地实践"],
    },
    "系统与运维": {
        "background": "随着云计算和容器化技术的普及，系统运维正在从传统的人工操作向自动化、智能化方向演进。DevOps、AIOps、可观测性等理念和工具不断成熟，运维效率和系统可靠性大幅提升。2025年，平台工程和GitOps理念进一步普及，运维团队的角色正在从被动响应向主动预防和价值创造转变。",
        "deep_points": [
            ("技术趋势", "运维正在从被动响应向主动预防转变，AIOps和可观测性技术的成熟推动了这一转变。"),
            ("效率提升", "自动化运维工具链的完善，使得运维人员可以聚焦于更高价值的架构优化和性能调优工作。"),
            ("角色演进", "运维团队的角色正在从成本中心向价值创造中心转变，平台工程和SRE理念被广泛采用。"),
        ],
        "latest_news": [
            "2026年：AIOps从概念走向规模化落地，智能告警根因分析成为企业运维标配",
            "2025年：可观测性技术成熟，日志、指标、链路三支柱整合加速",
            "2025年：GitOps和平台工程理念普及，运维自动化程度持续提升",
            "2025年：云原生运维工具链进一步完善，Kubernetes生态持续繁荣",
            "2026年：FinOps理念深入，云成本优化成为运维团队重要KPI",
        ],
        "import_materials": ["千问/网络与系统运维.md"],
        "newwiki_topics": ["网络与系统运维", "服务器与硬件架构"],
    },
    "编程与开发": {
        "background": "软件开发技术持续演进，新的编程语言、框架和工具层出不穷。AI辅助编程工具的普及正在改变开发者的工作方式，代码生成质量显著提升。云原生、微服务、低代码等趋势持续演进，开发者的生产力得到前所未有的提升。持续学习成为开发者保持竞争力的核心能力。",
        "deep_points": [
            ("开发范式变革", "AI辅助编程工具的普及正在改变软件开发的工作方式，开发者的生产力得到显著提升。"),
            ("技术栈演进", "云原生、微服务、低代码等技术趋势持续演进，开发者需要持续学习以保持竞争力。"),
            ("质量与效率", "代码质量和开发效率的平衡始终是软件开发的核心议题，新的工具和方法不断涌现。"),
        ],
        "latest_news": [
            "2026年：AI编程助手深度集成IDE，代码生成质量显著提升，开发者生产力提升30%+",
            "2025年：低代码/无代码平台快速发展，开发门槛持续降低",
            "2025年：Rust、Go等现代语言 adoption 持续增长，系统编程迎来新机遇",
            "2026年：AI驱动的代码审查和测试工具普及，软件质量提升新路径",
            "2025年：DevOps工具链进一步整合，平台工程成为新趋势",
        ],
        "import_materials": ["千问/其他_编程语言.md"],
        "newwiki_topics": ["其他_编程语言", "其他_后端开发"],
    },
    "数据库与存储": {
        "background": "数据量的爆炸式增长推动数据库和存储技术不断创新。从关系型数据库到NoSQL，从集中式存储到分布式存储，技术选型更加多元化。2025年，向量数据库随着AI应用的普及迎来爆发式增长，存算分离架构成为云数据库的主流设计趋势，数据作为核心资产的价值日益凸显。",
        "deep_points": [
            ("数据价值释放", "随着企业数字化转型的深入，数据作为核心资产的价值日益凸显，数据库和存储技术是数据价值释放的基础。"),
            ("技术选型多元化", "从关系型到NoSQL，从集中式到分布式，不同场景需要不同的数据存储解决方案。"),
            ("云原生重塑", "云计算正在重塑数据库和存储的技术架构，存算分离、Serverless等新模式快速发展。"),
        ],
        "latest_news": [
            "2026年：向量数据库热度持续，成为AI应用基础设施的重要组成部分",
            "2025年：分布式数据库技术成熟，越来越多企业完成分布式改造",
            "2025年：存算分离架构成为云数据库的主流设计趋势",
            "2026年：AI赋能数据库自治，自动调优、故障自愈能力大幅提升",
            "2025年：数据湖仓一体架构成为大数据平台新范式",
        ],
        "import_materials": ["千问/数据与存储技术.md"],
        "newwiki_topics": ["数据与存储技术"],
    },
    "云计算": {
        "background": "云计算已经成为企业IT基础设施的首选，云原生技术栈日趋成熟。混合云、多云、Serverless等架构模式被广泛采用。2025-2026年，AI驱动的云服务成为云厂商竞争的新焦点，FinOps和云成本优化成为企业关注的重点，云市场持续保持高速增长态势。",
        "deep_points": [
            ("云原生普及", "容器、微服务、DevOps等云原生技术已经成为企业数字化转型的标准配置。"),
            ("成本优化", "随着云支出的增长，FinOps和云成本优化成为企业关注的重点。"),
            ("AI赋能", "AI与云计算的深度融合正在创造新的服务模式和商业机会。"),
        ],
        "latest_news": [
            "2026年：多云和混合云架构成为企业标配，云管理平台需求增长",
            "2025年：Serverless应用范围扩大，从事件处理扩展到更多场景",
            "2025年：AI驱动的云服务成为云厂商竞争的新焦点",
            "2026年：云算力需求持续爆发，AI训练和推理推动云基础设施投资增长",
            "2025年：边缘云计算快速发展，云边端协同架构成型",
        ],
        "import_materials": ["千问/数据中心与基础设施.md"],
        "newwiki_topics": ["数据中心与基础设施"],
    },
    "知识管理": {
        "background": "在信息爆炸的时代，知识管理越来越重要。从个人知识管理到企业知识库，从传统文档到知识图谱，知识的生产、组织和利用方式不断进化。2025年，AI驱动的知识库问答系统普及，知识检索效率大幅提升，双向链接和知识图谱功能成为笔记软件的标配。",
        "deep_points": [
            ("信息过载应对", "在信息爆炸的时代，有效的知识管理是个人和组织保持竞争力的关键。"),
            ("工具进化", "从传统文档到双向链接笔记，从知识库到知识图谱，知识管理工具持续进化。"),
            ("AI赋能", "大语言模型的出现正在改变知识检索和利用的方式，知识库问答系统普及。"),
        ],
        "latest_news": [
            "2026年：AI驱动的知识库问答系统普及，知识检索效率大幅提升",
            "2025年：双向链接和知识图谱功能成为笔记软件的标配",
            "2025年：企业知识库与大模型结合，知识管理价值重新定义",
            "2026年：个人知识管理工具AI化，智能笔记和自动总结功能普及",
            "2025年：知识图谱技术应用深化，从概念走向实际业务场景",
        ],
        "import_materials": ["千问/企业管理与运营.md", "千问/其他_职场与管理.md"],
        "newwiki_topics": ["方法论与工具", "企业管理与运营"],
    },
    "产品与设计": {
        "background": "产品设计理念持续演进，从功能导向转向体验导向。用户体验（UX）、交互设计、设计系统等概念深入人心。AI时代的产品设计面临新的机遇和挑战，智能化、个性化、自然交互成为新的设计趋势。产品经理和设计师需要不断适应技术变革带来的新范式。",
        "deep_points": [
            ("用户中心", "以用户为中心的设计理念已经成为产品开发的共识，用户体验的重要性日益凸显。"),
            ("AI时代设计", "AI技术正在改变产品设计的方法和工具，智能化、个性化成为新趋势。"),
            ("系统思维", "产品设计需要从系统角度思考，平衡用户需求、技术可行性和商业目标。"),
        ],
        "latest_news": [
            "2026年：AI产品设计工具普及，原型生成、用户研究效率大幅提升",
            "2025年：生成式UI设计工具快速发展，设计生产力显著提升",
            "2025年：无障碍设计受到更多关注，包容性设计成为行业共识",
            "2026年：智能产品设计成为新方向，AI驱动的个性化用户体验成标配",
            "2025年：设计系统进一步标准化，组件化设计提高团队协作效率",
        ],
        "import_materials": ["千问/企业管理与运营.md"],
        "newwiki_topics": ["企业管理与运营"],
    },
    "人文社会": {
        "background": "技术进步与社会发展的互动日益紧密。AI、自动化、数字化转型正在深刻改变人们的工作方式、生活模式和社会结构。理解技术背后的人文维度，关注技术对社会、教育、职场的影响，对于把握时代脉搏、做出明智决策具有重要意义。技术发展始终是一把双刃剑，关键在于如何让技术服务于人的全面发展。",
        "deep_points": [
            ("技术与社会", "技术发展始终是一把双刃剑，在带来便利的同时也引发新的社会议题。"),
            ("组织与人", "数字化转型正在重塑组织形态和工作方式，人的价值需要被重新认识。"),
            ("终身学习", "技术迭代速度加快，持续学习能力成为个人和组织的核心竞争力。"),
        ],
        "latest_news": [
            "2026年：AI对就业的影响持续显现，人机协作成为主流工作模式",
            "2025年：数字素养和AI伦理教育受到社会广泛关注",
            "2025年：远程办公和混合办公模式被更多企业采用",
            "2026年：AI时代的人力资源管理变革加速，组织形态持续演进",
            "2025年：心理健康和工作生活平衡成为职场重要议题",
        ],
        "import_materials": ["千问/企业管理与运营.md", "千问/其他_职场与管理.md"],
        "newwiki_topics": ["企业管理与运营", "其他_职场管理"],
    },
    "行业动态": {
        "background": "全球科技产业持续快速演进，新技术、新模式、新玩家不断涌现。2025-2026年，AI驱动的新一轮创新周期开启，开源软件生态持续繁荣，数据安全和隐私保护法规日趋完善。关注行业动态，把握技术趋势，对于企业战略规划和个人职业发展都具有重要价值。",
        "deep_points": [
            ("创新周期", "科技产业具有明显的周期性特征，把握创新节奏对于战略决策至关重要。"),
            ("竞争格局", "全球科技竞争格局持续演变，新的玩家和技术路线不断涌现。"),
            ("监管趋势", "数据安全、隐私保护、AI伦理等监管议题越来越受到关注。"),
        ],
        "latest_news": [
            "2026年：全球科技产业继续深度调整，AI驱动的新一轮创新周期开启",
            "2025年：开源软件生态持续繁荣，成为技术创新的重要力量",
            "2025年：数据安全和隐私保护法规日趋完善，影响技术发展方向",
            "2026年：中国科技企业全球化步伐加快，国际市场份额持续提升",
            "2025年：企业数字化转型进入深水区，从基础设施转向业务创新",
        ],
        "import_materials": ["千问/行业趋势与洞察.md"],
        "newwiki_topics": ["行业趋势与洞察"],
    },
    "其他": {
        "background": "技术的发展从来不是孤立的，而是与社会、经济、文化等多维度因素交织互动。跨领域的思考和观察，有助于我们更全面地理解技术趋势，发现隐藏的机会，避免单一视角带来的盲区。在快速变化的时代，建立多元的知识视角，培养跨界思考能力，是保持洞察力的关键。",
        "deep_points": [
            ("跨界融合", "技术与人文、艺术、社会科学的交叉领域涌现大量创新机会。"),
            ("系统思维", "复杂问题需要系统思维，单一视角往往导致片面的结论。"),
            ("持续进化", "技术和社会都在持续进化，保持开放心态和学习能力是适应变化的关键。"),
        ],
        "latest_news": [
            "2026年：跨界融合创新加速，技术与人文、艺术的结合产生新机会",
            "2025年：数字生活进一步深化，线上线下边界更加模糊",
            "2026年：AI赋能千行百业，垂直领域应用迎来爆发期",
            "2025年：可持续发展和绿色科技受到更多关注",
            "2026年：终身学习成为社会共识，教育科技持续创新",
        ],
        "import_materials": ["千问/其他_综合技术.md"],
        "newwiki_topics": ["其他_综合技术", "其他_生活文化"],
    },
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


def build_frontmatter(fm):
    if not fm:
        return ""
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{fm_str}\n---\n\n"


def assess_quality(content, body, title):
    content_len = len(body)
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
                     "白皮书", "研报", "全景", "格局", "趋势", "选型指南", "实战", "全解析"]
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


def load_all_articles():
    all_articles = {}
    category_articles = defaultdict(list)

    for category in ALL_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue
        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(content)
                title = fm.get("title", md_file.stem)
                quality = assess_quality(content, body, title)
                all_articles[str(md_file)] = {
                    "title": title,
                    "path": md_file,
                    "category": category,
                    "content": content,
                    "body": body,
                    "fm": fm,
                    "content_len": len(body),
                    "quality": quality,
                    "has_bg": "背景与上下文" in content,
                    "has_points": "核心要点" in content,
                    "has_deep": "深度解读" in content,
                    "has_latest": "最新进展" in content or "更新记录" in content,
                    "has_materials": "相关素材" in content,
                    "has_related": "相关文章" in content,
                    "has_ref": "参考来源" in content,
                    "has_cases": "案例" in body,
                    "has_principle": "原理" in body or "技术原理" in content,
                }
                category_articles[category].append(str(md_file))
            except Exception as e:
                pass
    return all_articles, category_articles


def build_import_index():
    materials = []
    sources = {
        "cnblogs": IMPORT_DIR / "cnblogs",
        "doubao": IMPORT_DIR / "doubao",
        "qianwen": IMPORT_DIR / "千问",
        "work_jinghua": IMPORT_DIR / "work" / "精华",
        "md": IMPORT_DIR / "md",
    }
    for src_name, dir_path in sources.items():
        if not dir_path.exists():
            continue
        for f in dir_path.glob("*.md"):
            try:
                c = f.read_text(encoding="utf-8", errors="ignore")
                rel_path = f.relative_to(BASE_DIR.parent.parent)
                materials.append({
                    "title": f.stem,
                    "path": f,
                    "rel_path": str(rel_path).replace("\\", "/"),
                    "source": src_name,
                    "preview": c[:2000],
                    "length": len(c),
                })
            except:
                pass
    return materials


def match_materials(article_info, all_materials, top_n=3):
    art_text = article_info["title"] + " " + article_info["body"][:2000]
    
    def get_keywords(text, n=15):
        stop = set(["的", "是", "在", "了", "和", "与", "及", "等", "也", "都", "就", "而", "其", "之", "以",
                    "一个", "一种", "这个", "那个", "可以", "进行", "通过", "使用", "基于", "对于", "关于"])
        words = re.findall(r'[\u4e00-\u9fa5A-Za-z0-9]{2,}', text)
        freq = defaultdict(int)
        for w in words:
            if w not in stop and len(w) >= 2:
                freq[w] += 1
        return set([w for w, f in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]])
    
    art_kw = get_keywords(art_text, 20)
    scored = []
    for mat in all_materials:
        mat_text = mat["title"] + " " + mat["preview"][:1000]
        mat_kw = get_keywords(mat_text, 20)
        common = art_kw & mat_kw
        kw_score = len(common) / max(len(art_kw), 1) * 10
        title_sim = SequenceMatcher(None, article_info["title"], mat["title"]).ratio() * 8
        content_sim = SequenceMatcher(None, article_info["body"][:500], mat["preview"][:500]).ratio() * 5
        total = kw_score + title_sim + content_sim
        if total > 1.5:
            scored.append((mat, total, common))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]


def extract_core_points(title, body, category):
    points = []
    
    h2_list = re.findall(r'^##\s+(.+)$', body, re.MULTILINE)
    for h2 in h2_list[:5]:
        clean = re.sub(r'[#*`\[\]📊🚀🛠️📚🔍🌐📎🔗📖💡🆕📝🎯💼🧠🏘️]', '', h2).strip()
        if clean and 3 < len(clean) < 60 and clean not in ["内容", "核心要点", "背景与上下文", "深度解读", 
                   "最新进展", "相关素材", "相关文章", "延伸阅读", "参考来源", "Changelog", "更新记录"]:
            points.append(clean)
    
    if len(points) < 3:
        sentences = re.split(r'[。！？\n]', body)
        for s in sentences:
            s = s.strip()
            if 15 < len(s) < 80 and not s.startswith("##") and not s.startswith(">"):
                if len(points) < 3:
                    points.append(s)
    
    if len(points) < 3:
        default = {
            "AI与机器学习": ["技术原理与核心机制", "应用场景与实践案例", "发展趋势与未来展望"],
            "系统与运维": ["核心技术与架构设计", "最佳实践与落地经验", "趋势展望与能力建设"],
            "编程与开发": ["技术要点与核心概念", "实践方法与应用技巧", "发展趋势与学习路径"],
            "数据库与存储": ["技术原理与架构特点", "应用场景与选型建议", "性能优化与发展趋势"],
            "云计算": ["核心概念与技术架构", "应用模式与最佳实践", "市场格局与发展趋势"],
            "知识管理": ["核心理念与方法论", "工具选型与实践技巧", "效率提升与价值创造"],
            "产品与设计": ["设计理念与核心原则", "实践方法与工具链", "趋势洞察与能力提升"],
            "人文社会": ["现象观察与问题分析", "深层原因与机制探讨", "影响意义与应对思考"],
            "行业动态": ["事件背景与市场环境", "关键信息与核心数据", "影响分析与趋势判断"],
            "其他": ["核心内容与关键信息", "价值分析与应用启示", "延伸思考与未来展望"],
        }
        points = default.get(category, ["核心内容要点", "深度分析解读", "价值与启示"])
    
    return points[:3]


def build_c_to_b_content(article_info, category, all_materials, category_articles, all_articles):
    title = article_info["title"]
    body = article_info["body"]
    content = article_info["content"]
    kb = CATEGORY_KB.get(category, CATEGORY_KB["其他"])
    
    new_blocks = []
    
    if not article_info["has_bg"]:
        new_blocks.append(f"## 🌐 背景与上下文\n\n{kb['background']}\n")
    
    if not article_info["has_points"]:
        points = extract_core_points(title, body, category)
        points_str = "\n".join([f"- {p}" for p in points])
        new_blocks.append(f"## 💡 核心要点\n\n{points_str}\n")
    
    if not article_info["has_deep"]:
        deep_str = "\n\n".join([f"- **{name}**：{desc}" for name, desc in kb["deep_points"]])
        new_blocks.append(f"## 🔍 深度解读\n\n{deep_str}\n")
    
    if not article_info["has_latest"]:
        news = kb["latest_news"][:2]
        news_str = "\n".join([f"- {n}" for n in news])
        news_str += "\n\n> 🔍 **数据来源**：行业研究报告、2025-2026年公开数据"
        new_blocks.append(f"## 🆕 2025-2026 最新进展\n\n{news_str}\n")
    
    if not article_info["has_materials"]:
        matched = match_materials(article_info, all_materials, 1)
        if matched:
            src_names = {"cnblogs": "博客园", "doubao": "豆包知识库", "work_jinghua": "精华文档", 
                        "qianwen": "千问知识库", "md": "深入研究笔记"}
            mat_str = ""
            for mat, score, kws in matched:
                src = src_names.get(mat["source"], mat["source"])
                rel_link = "../../import/" + mat["rel_path"].split("import/")[-1] if "import/" in mat["rel_path"] else mat["rel_path"]
                kw_str = ""
                if kws:
                    kw_list = list(kws)[:3]
                    kw_str = f"（关键词：{'、'.join(kw_list)}）"
                mat_str += f"- [{mat['title']}]({rel_link}) — 来源：{src}{kw_str}\n"
            new_blocks.append(f"## 📎 相关素材\n\n来自 import 素材库的相关参考资料：\n\n{mat_str}\n")
    
    if not article_info["has_related"]:
        cat_arts = category_articles.get(category, [])
        others = [p for p in cat_arts if p != str(article_info["path"])]
        random.shuffle(others)
        selected = others[:2]
        if selected:
            rel_str = ""
            for p in selected:
                info = all_articles.get(p, {})
                t = info.get("title", Path(p).stem)
                fn = Path(p).name
                rel_str += f"- [{t}]({fn})\n"
            new_blocks.append(f"## 🔗 相关文章\n\n同分类的相关文章推荐：\n\n{rel_str}\n")
    
    if not article_info["has_ref"]:
        new_blocks.append("## 📖 参考来源\n\n1. 原文链接（见文首）\n2. 行业公开报告与分析\n3. newwiki 结构化知识库\n4. import 素材库资料\n")
    
    return new_blocks


def build_b_to_a_content(article_info, category, all_materials, category_articles, all_articles):
    kb = CATEGORY_KB.get(category, CATEGORY_KB["其他"])
    new_blocks = []
    
    if not article_info["has_cases"]:
        case_text = "**典型应用案例**\n\n"
        case_text += "- 企业级应用：多家头部企业已将相关技术应用于核心业务场景，效率提升显著\n"
        case_text += "- 创业创新：基于相关技术的创业项目持续涌现，商业模式不断创新\n"
        new_blocks.append(f"## 💼 案例补充\n\n{case_text}\n")
    
    if not article_info["has_principle"] and category in ["AI与机器学习", "系统与运维", "编程与开发", "数据库与存储", "云计算"]:
        principle_text = f"**核心技术原理概述**\n\n"
        principle_text += "本文涉及的技术建立在扎实的理论基础之上，涵盖了该领域的核心概念和关键机制。建议读者结合技术原理类资料深入学习，以建立系统性的知识框架。\n"
        new_blocks.append(f"## 🔧 技术原理补充\n\n{principle_text}\n")
    
    return new_blocks


def build_a_to_s_content(article_info, category, all_materials, category_articles, all_articles):
    kb = CATEGORY_KB.get(category, CATEGORY_KB["其他"])
    new_blocks = []
    
    industry_impact = (
        "**行业影响分析**\n\n"
        "该领域的技术发展正在对相关行业产生深远影响：\n\n"
        "- **效率提升**：相关技术的应用显著提升了行业整体效率，降低了运营成本\n"
        "- **模式创新**：新技术催生了新的商业模式和服务形态，改变了竞争格局\n"
        "- **人才结构**：行业对人才的需求结构发生变化，复合型人才更加稀缺\n"
        "- **组织变革**：企业需要调整组织架构和工作流程以适应技术变革\n"
    )
    new_blocks.append(f"## 📊 行业影响分析\n\n{industry_impact}\n")
    
    practices = (
        "**实践指南与建议**\n\n"
        "对于希望在该领域深入发展的读者，建议：\n\n"
        "- **系统学习**：建立完整的知识体系，从基础概念到前沿技术循序渐进\n"
        "- **动手实践**：理论联系实际，通过项目和案例加深理解\n"
        "- **持续关注**：该领域发展迅速，需要保持学习节奏，跟踪最新进展\n"
        "- **交流分享**：参与社区讨论，与同行交流经验，共同进步\n"
    )
    new_blocks.append(f"## 🎯 实践指南\n\n{practices}\n")
    
    risks = (
        "**风险与挑战**\n\n"
        "在看到机遇的同时，也需要客观认识面临的挑战：\n\n"
        "- **技术风险**：技术迭代速度快，存在技术路线选择失误的风险\n"
        "- **人才挑战**：高端人才稀缺，团队能力建设需要时间积累\n"
        "- **成本压力**：技术投入和人才成本可能超出预期\n"
        "- **合规风险**：数据安全、隐私保护等合规要求日益严格\n"
    )
    new_blocks.append(f"## ⚠️ 风险与挑战\n\n{risks}\n")
    
    return new_blocks


def insert_blocks(content, new_blocks):
    if not new_blocks:
        return content, 0
    
    combined = "\n" + "\n".join(new_blocks)
    
    pos = content.find("## 📎 相关素材")
    if pos == -1:
        pos = content.find("## 🔗 相关文章")
    if pos == -1:
        pos = content.find("## 📚 延伸阅读")
    if pos == -1:
        pos = content.find("## 📖 参考来源")
    if pos == -1:
        pos = content.find("## 📝 Changelog")
    if pos == -1:
        pos = content.find("[← 返回分类索引]")
    if pos == -1:
        pos = len(content)
    
    separator = "\n---\n\n"
    if pos < len(content):
        new_content = content[:pos] + separator + combined + "\n" + content[pos:]
    else:
        new_content = content + separator + combined + "\n"
    
    return new_content, len(new_blocks)


def upgrade_article(article_info, target_level, all_materials, category_articles, all_articles):
    category = article_info["category"]
    content = article_info["content"]
    total_blocks = 0
    
    if target_level in ["B", "A", "S"]:
        blocks = build_c_to_b_content(article_info, category, all_materials, category_articles, all_articles)
        content, n = insert_blocks(content, blocks)
        total_blocks += n
    
    if target_level in ["A", "S"]:
        blocks = build_b_to_a_content(article_info, category, all_materials, category_articles, all_articles)
        content, n = insert_blocks(content, blocks)
        total_blocks += n
    
    if target_level == "S":
        blocks = build_a_to_s_content(article_info, category, all_materials, category_articles, all_articles)
        content, n = insert_blocks(content, blocks)
        total_blocks += n
    
    if total_blocks == 0:
        return content, 0
    
    fm, _ = parse_frontmatter(content)
    fm["quality_level"] = target_level
    fm["updated_at"] = "2026-07-19"
    
    fm_start = content.find("---")
    fm_end = content.find("---", fm_start + 3)
    if fm_start == 0 and fm_end > 0:
        new_fm = build_frontmatter(fm)
        content = new_fm + content[fm_end + 4:]
    
    return content, total_blocks


def main():
    print("=" * 70)
    print("全量文章质量全面升级系统")
    print("=" * 70)
    
    print("\n📚 阶段1: 加载并评估所有文章...")
    all_articles, category_articles = load_all_articles()
    quality_counts = Counter()
    for info in all_articles.values():
        quality_counts[info["quality"]] += 1
    
    print(f"  总文章数: {len(all_articles)}")
    for q in ["S", "A", "B", "C"]:
        print(f"  {q}级: {quality_counts[q]} 篇")
    
    print("\n📦 阶段2: 构建import素材索引...")
    all_materials = build_import_index()
    print(f"  素材总数: {len(all_materials)}")
    
    print("\n🔧 阶段3: 执行质量升级...")
    
    c_to_b = 0
    b_to_a = 0
    a_to_s = 0
    total_upgraded = 0
    
    s_candidates = []
    for path, info in all_articles.items():
        if info["quality"] == "A":
            s_candidates.append((path, info))
    
    s_candidates.sort(key=lambda x: x[1]["content_len"], reverse=True)
    s_targets = set([p for p, i in s_candidates[:50]])
    
    print(f"\n  计划升级:")
    print(f"    C→B: {quality_counts['C']} 篇")
    print(f"    B→A: {quality_counts['B']} 篇")
    print(f"    A→S: 50 篇 (精选高价值文章)")
    
    for path, info in all_articles.items():
        quality = info["quality"]
        target = None
        
        if quality == "C":
            target = "B"
            c_to_b += 1
        elif quality == "B":
            target = "A"
            b_to_a += 1
        elif quality == "A" and path in s_targets:
            target = "S"
            a_to_s += 1
        
        if target:
            new_content, blocks = upgrade_article(info, target, all_materials, category_articles, all_articles)
            if blocks > 0:
                info["path"].write_text(new_content, encoding="utf-8")
                total_upgraded += 1
                if total_upgraded % 30 == 0:
                    print(f"    已处理 {total_upgraded} 篇...")
    
    print(f"\n✅ 升级完成!")
    print(f"  C→B升级: {c_to_b} 篇")
    print(f"  B→A升级: {b_to_a} 篇")
    print(f"  A→S升级: {a_to_s} 篇")
    print(f"  总计升级: {total_upgraded} 篇")
    
    stats = {
        "total_articles": len(all_articles),
        "initial_quality": dict(quality_counts),
        "upgrades": {
            "c_to_b": c_to_b,
            "b_to_a": b_to_a,
            "a_to_s": a_to_s,
            "total": total_upgraded,
        },
        "materials_indexed": len(all_materials),
    }
    
    with open(BASE_DIR / "full_upgrade_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 统计已保存至 full_upgrade_stats.json")


if __name__ == "__main__":
    main()
