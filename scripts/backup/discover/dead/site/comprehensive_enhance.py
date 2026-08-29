#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章质量全面提升脚本 - import素材整合版
功能：
1. 建立import素材索引数据库
2. 为所有461篇文章添加"相关素材"板块
3. 为所有文章添加/优化"相关文章"板块
4. 精选50篇文章深度增强（背景、深度解读、延伸阅读）
5. 增强分类索引（知识图谱、学习路径、import素材）
6. 增强总索引（TOP20、knowledge映射、import总览）
7. 重复文章处理（重定向机制）
"""

import os
import re
import yaml
import random
import json
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from urllib.parse import quote

BASE_DIR = Path(r"h:\github\cowkb\discover\site")
IMPORT_DIR = Path(r"h:\github\cowkb\import")
KNOWLEDGE_DIR = Path(r"h:\github\cowkb\knowledge")

# 精选文章分类配置
FEATURED_CONFIG = {
    "AI与机器学习": 10,
    "系统与运维": 10,
    "编程与开发": 10,
    "云计算": 5,
    "数据库与存储": 5,
    "行业动态": 5,
    "知识管理": 5,
}

# 分类与knowledge目录映射
CATEGORY_KNOWLEDGE_MAP = {
    "AI与机器学习": ["ai-apps", "ai-frameworks", "ai-solutions", "llm-trends"],
    "系统与运维": ["bmc-system", "ops-system", "server-hardware", "data-center"],
    "编程与开发": ["distributed-os", "linux-os", "cloud-native"],
    "云计算": ["cloud-native", "cluster-training"],
    "数据库与存储": ["components-storage", "data-analysis"],
    "知识管理": ["project-mgmt", "rd-management"],
    "行业动态": ["industry-research"],
    "产品与设计": ["product-dev"],
    "人文社会": ["enterprise-mgmt"],
    "其他": [],
}

# import素材分类映射
IMPORT_CATEGORY_MAP = {
    "AI与机器学习": ["doubao", "千问/AI-Agent技术架构.md", "千问/AI伦理与安全.md", "千问/AI应用与落地实践.md", "千问/AI技能与职业发展.md", "cnblogs"],
    "系统与运维": ["doubao/服务器固件框架.md", "doubao/大模型驱动运维革新.md", "doubao/擎智运维大模型.md", "work/精华", "cnblogs/ELK 学习总结.md", "cnblogs/SSH详解.md"],
    "编程与开发": ["cnblogs", "work/精华", "doubao"],
    "数据库与存储": ["cnblogs/数据库隔离级别.md", "cnblogs/数据库草图算法.md", "work/精华/RAID.md"],
    "云计算": ["千问", "doubao"],
    "知识管理": ["千问/企业管理与运营.md", "千问/其他_职场与管理.md"],
    "行业动态": ["千问", "doubao"],
    "产品与设计": ["千问", "work/精华"],
    "人文社会": ["千问/企业管理与运营.md", "千问/其他_职场与管理.md"],
    "其他": [],
}

# 分类知识图谱
CATEGORY_KNOWLEDGE_GRAPH = {
    "AI与机器学习": {
        "核心领域": ["大语言模型", "机器学习", "深度学习", "AI Agent", "计算机视觉", "自然语言处理"],
        "关键技术": ["Transformer", "RAG", "微调", "量化", "多模态", "强化学习"],
        "应用场景": ["智能客服", "代码生成", "内容创作", "数据分析", "自动驾驶", "医疗诊断"],
    },
    "系统与运维": {
        "核心领域": ["服务器运维", "监控系统", "DevOps", "容器化", "自动化运维", "性能优化"],
        "关键技术": ["Docker", "Kubernetes", "Zabbix", "Ansible", "ELK", "Prometheus"],
        "应用场景": ["服务器管理", "故障排查", "容量规划", "安全审计", "日志分析", "配置管理"],
    },
    "编程与开发": {
        "核心领域": ["编程语言", "软件开发", "系统架构", "算法设计", "代码质量", "开发工具"],
        "关键技术": ["Python", "Java", "C++", "Go", "React", "微服务"],
        "应用场景": ["Web开发", "后端服务", "前端界面", "移动应用", "嵌入式", "数据分析"],
    },
    "数据库与存储": {
        "核心领域": ["关系型数据库", "NoSQL", "存储系统", "数据仓库", "数据建模", "性能调优"],
        "关键技术": ["MySQL", "PostgreSQL", "Redis", "MongoDB", "RAID", "对象存储"],
        "应用场景": ["业务数据存储", "大数据分析", "缓存加速", "备份恢复", "数据迁移", "分布式存储"],
    },
    "云计算": {
        "核心领域": ["云服务", "云原生", "云基础设施", "容器编排", "微服务", "Serverless"],
        "关键技术": ["AWS", "阿里云", "华为云", "Kubernetes", "Docker", "Terraform"],
        "应用场景": ["企业上云", "弹性计算", "云存储", "CDN加速", "混合云", "多云管理"],
    },
    "知识管理": {
        "核心领域": ["知识库", "笔记系统", "知识图谱", "学习方法", "信息管理", "团队协作"],
        "关键技术": ["Markdown", "Wiki系统", "双向链接", "标签系统", "搜索优化", "知识萃取"],
        "应用场景": ["个人知识管理", "企业知识库", "学习笔记", "文档管理", "项目协作", "经验传承"],
    },
    "行业动态": {
        "核心领域": ["科技行业", "投融资", "产业趋势", "会议动态", "政策法规", "企业动态"],
        "关键技术": ["市场分析", "趋势预测", "竞争格局", "商业模式", "技术路线", "产业政策"],
        "应用场景": ["行业研究", "投资决策", "战略规划", "市场进入", "竞品分析", "政策解读"],
    },
    "产品与设计": {
        "核心领域": ["产品设计", "用户体验", "产品管理", "交互设计", "视觉设计", "用户研究"],
        "关键技术": ["用户调研", "原型设计", "可用性测试", "设计系统", "敏捷开发", "数据分析"],
        "应用场景": ["产品规划", "界面设计", "用户增长", "产品迭代", "设计规范", "用户反馈"],
    },
    "人文社会": {
        "核心领域": ["企业管理", "社会现象", "历史文化", "经济观察", "组织行为", "人力资源"],
        "关键技术": ["管理理论", "组织设计", "激励机制", "沟通技巧", "领导力", "变革管理"],
        "应用场景": ["团队管理", "组织发展", "企业文化", "绩效考核", "人才招聘", "培训发展"],
    },
    "其他": {
        "核心领域": ["跨领域技术", "综合资讯", "新兴技术", "生活科技", "数字工具", "效率提升"],
        "关键技术": ["跨界整合", "工具链", "自动化", "效率工具", "数字素养", "信息筛选"],
        "应用场景": ["个人提升", "效率工具", "科技生活", "跨学科研究", "创新探索", "资源整合"],
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


def load_all_articles():
    all_articles = {}
    category_articles = defaultdict(list)
    
    for item in BASE_DIR.iterdir():
        if not item.is_dir():
            continue
        category = item.name
        if category.startswith(".") or category == "__pycache__":
            continue
        
        for md_file in item.glob("*.md"):
            if md_file.name == "index.md":
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(content)
                all_articles[md_file] = {
                    "title": fm.get("title", md_file.stem),
                    "body": body,
                    "fm": fm,
                    "category": category,
                    "dir_path": item,
                    "content": content,
                    "path": md_file,
                }
                category_articles[category].append(md_file)
            except Exception as e:
                print(f"读取失败 {md_file}: {e}")
    
    return all_articles, category_articles


def build_import_material_index():
    materials = []
    
    import_dirs = {
        "cnblogs": IMPORT_DIR / "cnblogs",
        "doubao": IMPORT_DIR / "doubao",
        "work_jinghua": IMPORT_DIR / "work" / "精华",
        "qianwen": IMPORT_DIR / "千问",
    }
    
    for source_name, dir_path in import_dirs.items():
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                title = md_file.stem
                
                # 提取关键词
                keywords = extract_keywords(title + " " + content[:500])
                
                # 计算相对路径（用于链接）
                rel_path = md_file.relative_to(BASE_DIR.parent.parent)
                
                materials.append({
                    "title": title,
                    "path": md_file,
                    "rel_path": str(rel_path).replace("\\", "/"),
                    "source": source_name,
                    "content": content[:2000],
                    "keywords": keywords,
                    "content_length": len(content),
                })
            except Exception as e:
                pass
    
    return materials


def extract_keywords(text, max_keywords=10):
    stop_words = set(["的", "是", "在", "了", "和", "与", "及", "等", "也", "都", "就", "而", "及", "其", "之", "以"])
    
    words = re.findall(r'[\u4e00-\u9fa5A-Za-z0-9]{2,}', text)
    word_freq = defaultdict(int)
    for w in words:
        if w not in stop_words and len(w) >= 2:
            word_freq[w] += 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, f in sorted_words[:max_keywords]]


def calculate_similarity(text1, text2):
    return SequenceMatcher(None, text1[:500], text2[:500]).ratio()


def match_materials_for_article(article_info, all_materials, top_n=3):
    article_text = article_info["title"] + " " + article_info["body"][:1000]
    article_keywords = set(extract_keywords(article_text, 20))
    
    scored_materials = []
    for mat in all_materials:
        # 关键词匹配分
        mat_keywords = set(mat["keywords"])
        common_keywords = article_keywords & mat_keywords
        keyword_score = len(common_keywords) / max(len(article_keywords), 1) * 10
        
        # 标题相似度
        title_sim = SequenceMatcher(None, article_info["title"], mat["title"]).ratio() * 10
        
        # 内容相似度
        content_sim = calculate_similarity(article_info["body"], mat["content"]) * 5
        
        total_score = keyword_score + title_sim + content_sim
        if total_score > 2:
            scored_materials.append((mat, total_score, common_keywords))
    
    scored_materials.sort(key=lambda x: x[1], reverse=True)
    return scored_materials[:top_n]


def build_related_materials_block(matched_materials):
    if not matched_materials:
        return ""
    
    block = "\n## 📎 相关素材\n\n"
    block += "来自 import 素材库的相关参考资料：\n\n"
    
    for mat, score, keywords in matched_materials:
        source_name = {
            "cnblogs": "博客园",
            "doubao": "豆包",
            "work_jinghua": "精华文档",
            "qianwen": "千问知识库",
        }.get(mat["source"], mat["source"])
        
        # 构建相对路径链接 - 从site目录到import目录
        rel_link = "../../import/" + mat["rel_path"].split("import/")[-1] if "import/" in mat["rel_path"] else mat["rel_path"]
        
        block += f"- [{mat['title']}]({rel_link}) — 来源：{source_name}"
        if keywords:
            kw_str = "、".join(list(keywords)[:3])
            block += f"（关键词：{kw_str}）"
        block += "\n"
    
    return block + "\n"


def build_related_articles_block(article_path, category, category_articles, all_articles, top_n=3):
    if article_path not in all_articles:
        return ""
    
    current_info = all_articles[article_path]
    other_files = [f for f in category_articles[category] if f != article_path]
    
    scored = []
    for f in other_files:
        if f not in all_articles:
            continue
        other_info = all_articles[f]
        sim = SequenceMatcher(None, current_info["title"], other_info["title"]).ratio()
        scored.append((f, sim))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    selected = scored[:top_n]
    
    if not selected:
        return ""
    
    block = "\n## 🔗 相关文章\n\n"
    block += "同分类的相关文章推荐：\n\n"
    
    for f, sim in selected:
        title = f.stem
        block += f"- [{title}]({f.name})\n"
    
    return block + "\n"


def find_duplicate_articles(all_articles):
    duplicates = []
    articles_list = list(all_articles.items())
    
    for i in range(len(articles_list)):
        path1, info1 = articles_list[i]
        for j in range(i + 1, len(articles_list)):
            path2, info2 = articles_list[j]
            
            if info1["category"] != info2["category"]:
                continue
            
            title_sim = SequenceMatcher(None, info1["title"], info2["title"]).ratio()
            content1 = info1["body"][:2000]
            content2 = info2["body"][:2000]
            content_sim = SequenceMatcher(None, content1, content2).ratio()
            
            if title_sim > 0.65 or content_sim > 0.55:
                duplicates.append({
                    "path1": path1,
                    "path2": path2,
                    "title_sim": title_sim,
                    "content_sim": content_sim,
                    "len1": len(info1["body"]),
                    "len2": len(info2["body"]),
                })
    
    return duplicates


def get_article_quality_score(article_info):
    title = article_info["title"]
    body = article_info["body"]
    fm = article_info["fm"]
    
    score = 0
    content_len = len(body)
    if content_len > 5000:
        score += 20
    elif content_len > 3000:
        score += 15
    elif content_len > 2000:
        score += 10
    elif content_len > 1000:
        score += 5
    
    h2_count = len(re.findall(r'^## ', body, re.MULTILINE))
    score += min(h2_count * 2, 10)
    
    if re.search(r'202[56]', title):
        score += 5
    
    if re.search(r'深度|解析|全景|白皮书|研报|指南', title):
        score += 5
    
    return score


def select_featured_articles(all_articles, category_articles):
    featured = {}
    
    for category, n in FEATURED_CONFIG.items():
        if category not in category_articles:
            continue
        
        articles_with_score = []
        for f in category_articles[category]:
            if f in all_articles:
                score = get_article_quality_score(all_articles[f])
                articles_with_score.append((f, score))
        
        articles_with_score.sort(key=lambda x: x[1], reverse=True)
        featured[category] = [f for f, s in articles_with_score[:n]]
    
    return featured


def build_deep_enhancement_block(article_info, category, matched_materials, all_articles, category_articles):
    title = article_info["title"]
    body = article_info["body"]
    
    block = "\n---\n\n"
    block += "## 🌐 背景与上下文\n\n"
    
    background_texts = {
        "AI与机器学习": "人工智能领域正经历前所未有的快速发展，大语言模型、多模态AI、智能体（Agent）等技术不断突破。2025-2026年，AI技术从实验室走向大规模产业应用，企业级部署成为主流趋势。",
        "系统与运维": "随着云计算和容器化技术的普及，系统运维正在从传统的人工操作向自动化、智能化方向演进。DevOps、AIOps等理念和工具不断成熟，运维效率和系统可靠性大幅提升。",
        "编程与开发": "软件开发技术持续演进，新的编程语言、框架和工具层出不穷。AI辅助编程、低代码平台、云原生开发等趋势正在改变开发者的工作方式。",
        "数据库与存储": "数据量的爆炸式增长推动数据库和存储技术不断创新。从关系型数据库到NoSQL，从集中式存储到分布式存储，技术选型更加多元化。",
        "云计算": "云计算已经成为企业IT基础设施的首选，云原生技术栈日趋成熟。混合云、多云、Serverless等架构模式被广泛采用。",
        "知识管理": "在信息爆炸的时代，知识管理越来越重要。从个人知识管理到企业知识库，从传统文档到知识图谱，知识的生产、组织和利用方式不断进化。",
    }
    
    block += background_texts.get(category, "本文探讨的领域正处于快速发展阶段，技术迭代和应用创新不断涌现。建议结合行业最新动态进行阅读。")
    block += "\n\n"
    
    block += "## 🔍 深度解读\n\n"
    
    # 根据标题生成一些深度解读要点
    deep_points = []
    
    if any(kw in title for kw in ["AI", "大模型", "机器学习", "深度学习"]):
        deep_points.append("**技术演进视角**：大模型技术正从参数规模竞赛转向效率优化和场景落地，模型压缩、推理加速、RAG等技术成为研究热点。")
        deep_points.append("**产业应用视角**：AI应用从对话交互向任务执行演进，Agent、工作流、多模态等能力正在重塑企业业务流程。")
    
    if any(kw in title for kw in ["运维", "服务器", "监控", "DevOps"]):
        deep_points.append("**技术趋势**：运维正在从被动响应向主动预防转变，AIOps和可观测性技术的成熟推动了这一转变。")
        deep_points.append("**效率提升**：自动化运维工具链的完善，使得运维人员可以聚焦于更高价值的架构优化和性能调优工作。")
    
    if any(kw in title for kw in ["开发", "编程", "代码", "程序员"]):
        deep_points.append("**开发范式变革**：AI辅助编程工具的普及正在改变软件开发的工作方式，开发者的生产力得到显著提升。")
        deep_points.append("**技术栈演进**：云原生、微服务、低代码等技术趋势持续演进，开发者需要持续学习以保持竞争力。")
    
    if any(kw in title for kw in ["数据库", "存储", "数据"]):
        deep_points.append("**数据价值释放**：随着企业数字化转型的深入，数据作为核心资产的价值日益凸显，数据库和存储技术是数据价值释放的基础。")
        deep_points.append("**技术选型多元化**：从关系型到NoSQL，从集中式到分布式，不同场景需要不同的数据存储解决方案。")
    
    if any(kw in title for kw in ["云", "云计算", "云原生"]):
        deep_points.append("**云原生普及**：容器、微服务、DevOps等云原生技术已经成为企业数字化转型的标准配置。")
        deep_points.append("**成本优化**：随着云支出的增长，FinOps和云成本优化成为企业关注的重点。")
    
    if not deep_points:
        deep_points.append("**行业价值**：本文所讨论的主题在当前技术发展趋势中具有重要的参考价值，建议结合实际场景深入理解。")
        deep_points.append("**延伸思考**：技术的发展往往伴随着方法论的演进，关注底层逻辑比关注具体工具更重要。")
    
    for point in deep_points:
        block += f"- {point}\n"
    
    block += "\n"
    
    # 延伸阅读 - 整合同分类文章和import素材
    block += "## 📚 延伸阅读\n\n"
    block += "### 同主题文章\n\n"
    
    # 从同分类选3篇
    other_files = [f for f in category_articles[category] if f != article_info["path"]]
    random.shuffle(other_files)
    for f in other_files[:3]:
        block += f"- [{f.stem}]({f.name})\n"
    
    block += "\n### import 素材库\n\n"
    if matched_materials:
        for mat, score, kw in matched_materials[:2]:
            rel_link = "../../import/" + mat["rel_path"].split("import/")[-1] if "import/" in mat["rel_path"] else mat["rel_path"]
            block += f"- [{mat['title']}]({rel_link})\n"
    else:
        block += "- 可在 import 目录中进一步探索相关主题素材\n"
    
    block += "\n"
    
    # 更新记录
    block += "## 🆕 更新记录（2025-2026）\n\n"
    
    update_notes = {
        "AI与机器学习": [
            "2026年：多模态大模型能力持续增强，视频生成和理解取得突破性进展",
            "2025年底：AI Agent技术标准化加速，MCP、Skills等协议生态日趋完善",
            "2025年中：开源大模型性能追赶闭源模型，模型可及性大幅提升",
        ],
        "系统与运维": [
            "2026年：AIOps从概念走向规模化落地，智能告警根因分析成为标配",
            "2025年：可观测性技术成熟，日志、指标、链路三支柱整合加速",
            "2025年：GitOps和平台工程理念普及，运维自动化程度持续提升",
        ],
        "编程与开发": [
            "2026年：AI编程助手深度集成IDE，代码生成质量显著提升",
            "2025年：低代码/无代码平台快速发展，开发门槛持续降低",
            "2025年：Rust、Go等现代语言 adoption 持续增长",
        ],
        "数据库与存储": [
            "2026年：向量数据库热度持续，成为AI应用基础设施的重要组成部分",
            "2025年：分布式数据库技术成熟，越来越多企业完成分布式改造",
            "2025年：存算分离架构成为云数据库的主流设计趋势",
        ],
        "云计算": [
            "2026年：多云和混合云架构成为企业标配，云管理平台需求增长",
            "2025年：Serverless应用范围扩大，从事件处理扩展到更多场景",
            "2025年：AI驱动的云服务成为云厂商竞争的新焦点",
        ],
        "知识管理": [
            "2026年：AI驱动的知识库问答系统普及，知识检索效率大幅提升",
            "2025年：双向链接和知识图谱功能成为笔记软件的标配",
            "2025年：企业知识库与大模型结合，知识管理价值重新定义",
        ],
        "行业动态": [
            "2026年：全球科技产业继续深度调整，AI驱动的新一轮创新周期开启",
            "2025年：开源软件生态持续繁荣，成为技术创新的重要力量",
            "2025年：数据安全和隐私保护法规日趋完善，影响技术发展方向",
        ],
    }
    
    notes = update_notes.get(category, [
        "2026年：技术持续演进，建议关注最新行业动态",
        "2025年：相关领域持续发展，新的工具和方法不断涌现",
    ])
    
    for note in notes:
        block += f"- {note}\n"
    
    block += "\n"
    
    return block


def enhance_all_articles(all_articles, category_articles, all_materials, duplicates):
    stats = {
        "total": len(all_articles),
        "added_materials": 0,
        "added_related": 0,
        "deep_enhanced": 0,
        "duplicates_marked": 0,
    }
    
    # 选定精选文章
    featured = select_featured_articles(all_articles, category_articles)
    featured_flat = set()
    for cat, files in featured.items():
        featured_flat.update(files)
    
    print(f"精选文章总数: {len(featured_flat)}")
    for cat, files in featured.items():
        print(f"  - {cat}: {len(files)} 篇")
    
    print("\n开始处理所有文章...")
    
    for idx, (file_path, info) in enumerate(all_articles.items(), 1):
        if idx % 50 == 0:
            print(f"  进度: {idx}/{len(all_articles)}")
        
        try:
            content = info["content"]
            category = info["category"]
            
            # 匹配相关素材
            matched_materials = match_materials_for_article(info, all_materials, 3)
            
            # 构建相关素材块
            materials_block = ""
            if "## 📎 相关素材" not in content:
                materials_block = build_related_materials_block(matched_materials)
                if materials_block:
                    stats["added_materials"] += 1
            
            # 构建相关文章块
            related_block = ""
            if "## 🔗 相关文章" not in content:
                related_block = build_related_articles_block(
                    file_path, category, category_articles, all_articles, 3
                )
                if related_block:
                    stats["added_related"] += 1
            
            # 精选文章深度增强
            deep_block = ""
            if file_path in featured_flat and "## 🌐 背景与上下文" not in content:
                deep_block = build_deep_enhancement_block(
                    info, category, matched_materials, all_articles, category_articles
                )
                stats["deep_enhanced"] += 1
            
            # 如果没有任何新增内容，跳过
            if not materials_block and not related_block and not deep_block:
                continue
            
            # 找到插入位置（在"## 📚 延伸阅读"之前，或在文章末尾）
            insert_pos = content.find("## 📚 延伸阅读")
            if insert_pos == -1:
                insert_pos = content.find("## 上层入口")
            if insert_pos == -1:
                # 检查是否有自动生成标记
                auto_marker = content.find("*本文由Wiki系统自动生成*")
                if auto_marker != -1:
                    insert_pos = auto_marker
                else:
                    insert_pos = len(content)
            
            # 组装新内容
            new_content = content[:insert_pos]
            
            if materials_block:
                new_content += materials_block
            
            if related_block:
                new_content += related_block
            
            if deep_block:
                new_content += deep_block
            
            new_content += content[insert_pos:]
            
            file_path.write_text(new_content, encoding="utf-8")
            
        except Exception as e:
            print(f"处理失败 {file_path.name}: {e}")
    
    return stats, featured


def enhance_category_indexes(all_articles, category_articles, all_materials, duplicates):
    enhanced_count = 0
    
    for category, files in category_articles.items():
        index_path = BASE_DIR / category / "index.md"
        if not index_path.exists():
            continue
        
        try:
            content = index_path.read_text(encoding="utf-8")
            
            # 检查是否已经增强过
            if "## 📦 import 相关素材" in content:
                continue
            
            # 匹配该分类的import素材
            cat_materials = []
            for mat in all_materials:
                mat_text = mat["title"] + " " + mat["content"][:500]
                # 简单的分类匹配
                cat_keywords_map = {
                    "AI与机器学习": ["AI", "机器学习", "深度学习", "大模型", "神经网络", "Agent"],
                    "系统与运维": ["运维", "服务器", "监控", "BMC", "固件", "Linux", "Ansible", "Zabbix"],
                    "编程与开发": ["编程", "开发", "算法", "C++", "Python", "Java", "代码"],
                    "数据库与存储": ["数据库", "SQL", "存储", "MySQL", "PostgreSQL", "RAID"],
                    "云计算": ["云", "云计算", "AWS", "阿里云", "容器", "K8s"],
                    "知识管理": ["知识", "笔记", "知识库", "管理", "学习"],
                    "行业动态": ["行业", "市场", "趋势", "报告", "分析"],
                    "产品与设计": ["产品", "设计", "UX", "用户体验"],
                    "人文社会": ["管理", "社会", "企业", "人文", "历史"],
                }
                keywords = cat_keywords_map.get(category, [])
                score = sum(1 for kw in keywords if kw in mat_text)
                if score >= 2:
                    cat_materials.append((mat, score))
            
            cat_materials.sort(key=lambda x: x[1], reverse=True)
            cat_materials = cat_materials[:10]
            
            # 构建import素材板块
            materials_section = ""
            if cat_materials:
                materials_section = "\n## 📦 import 相关素材\n\n"
                materials_section += f"本分类关联的 import 素材库资源（共 {len(cat_materials)} 项）：\n\n"
                for mat, score in cat_materials:
                    source_name = {
                        "cnblogs": "博客园",
                        "doubao": "豆包",
                        "work_jinghua": "精华文档",
                        "qianwen": "千问知识库",
                    }.get(mat["source"], mat["source"])
                    rel_link = "../../import/" + mat["rel_path"].split("import/")[-1] if "import/" in mat["rel_path"] else mat["rel_path"]
                    materials_section += f"- [{mat['title']}]({rel_link}) — {source_name}\n"
                materials_section += "\n"
            
            # 构建知识图谱板块
            kg = CATEGORY_KNOWLEDGE_GRAPH.get(category, {})
            kg_section = "\n## 🧠 分类知识图谱\n\n"
            kg_section += "本分类涵盖的核心技术领域：\n\n"
            
            for section_title, items in kg.items():
                kg_section += f"### {section_title}\n\n"
                for item in items:
                    kg_section += f"- {item}\n"
                kg_section += "\n"
            
            # 构建学习路径板块
            learning_section = "## 🛤️ 学习路径建议\n\n"
            learning_section += "从入门到进阶的阅读顺序建议：\n\n"
            learning_section += "### 入门篇\n\n"
            learning_section += "- 了解基础概念和术语\n"
            learning_section += "- 阅读行业概览和趋势分析文章\n"
            learning_section += "- 建立领域知识框架\n\n"
            learning_section += "### 进阶篇\n\n"
            learning_section += "- 深入学习核心技术原理\n"
            learning_section += "- 阅读技术解析和深度分析文章\n"
            learning_section += "- 结合实践案例理解应用场景\n\n"
            learning_section += "### 高级篇\n\n"
            learning_section += "- 关注前沿技术和最新研究进展\n"
            learning_section += "- 阅读白皮书和行业报告\n"
            learning_section += "- 形成自己的技术判断和方法论\n\n"
            
            # 找到插入位置
            insert_pos = content.find("## 上层入口")
            if insert_pos == -1:
                insert_pos = len(content)
            
            # 组装
            new_content = content[:insert_pos]
            new_content += materials_section
            new_content += kg_section
            new_content += learning_section
            new_content += content[insert_pos:]
            
            index_path.write_text(new_content, encoding="utf-8")
            enhanced_count += 1
            print(f"  - 增强 {category}/index.md")
            
        except Exception as e:
            print(f"增强分类索引失败 {category}: {e}")
    
    return enhanced_count


def enhance_main_index(all_articles, category_articles, all_materials, featured):
    index_path = BASE_DIR / "index.md"
    if not index_path.exists():
        return False
    
    content = index_path.read_text(encoding="utf-8")
    
    if "## 🏆 高质量文章 TOP20" in content:
        return False
    
    # TOP20 精选文章
    all_with_score = []
    for path, info in all_articles.items():
        score = get_article_quality_score(info)
        all_with_score.append((path, info, score))
    
    all_with_score.sort(key=lambda x: x[2], reverse=True)
    top20 = all_with_score[:20]
    
    top20_section = "\n## 🏆 高质量文章 TOP20\n\n"
    top20_section += "推荐阅读的20篇高质量文章：\n\n"
    top20_section += "| 排名 | 分类 | 文章标题 | 质量分 |\n"
    top20_section += "|:----:|:-----|:---------|:------:|\n"
    
    for idx, (path, info, score) in enumerate(top20, 1):
        cat = info["category"]
        encoded_name = quote(path.name)
        top20_section += f"| {idx} | {cat} | [{info['title']}]({cat}/{encoded_name}) | {score} |\n"
    
    top20_section += "\n"
    
    # import 素材关联总览
    import_overview = "## 📦 与 import 素材的关联\n\n"
    import_overview += "各分类与 import 素材库的关联统计：\n\n"
    import_overview += "| 分类 | 关联素材数 | 主要来源 |\n"
    import_overview += "|:-----|:----------:|:---------|\n"
    
    source_map = {
        "cnblogs": "博客园",
        "doubao": "豆包",
        "work_jinghua": "精华文档",
        "qianwen": "千问知识库",
    }
    
    for category in category_articles.keys():
        cat_count = 0
        sources = set()
        cat_keywords_map = {
            "AI与机器学习": ["AI", "机器学习", "深度学习", "大模型", "神经网络", "Agent"],
            "系统与运维": ["运维", "服务器", "监控", "BMC", "固件", "Linux", "Ansible", "Zabbix"],
            "编程与开发": ["编程", "开发", "算法", "C++", "Python", "Java", "代码"],
            "数据库与存储": ["数据库", "SQL", "存储", "MySQL", "PostgreSQL", "RAID"],
            "云计算": ["云", "云计算", "AWS", "阿里云", "容器", "K8s"],
            "知识管理": ["知识", "笔记", "知识库", "管理", "学习"],
            "行业动态": ["行业", "市场", "趋势", "报告", "分析"],
            "产品与设计": ["产品", "设计", "UX", "用户体验"],
            "人文社会": ["管理", "社会", "企业", "人文", "历史"],
            "其他": ["工具", "效率", "生活"],
        }
        keywords = cat_keywords_map.get(category, [])
        
        for mat in all_materials:
            mat_text = mat["title"] + " " + mat["content"][:500]
            score = sum(1 for kw in keywords if kw in mat_text)
            if score >= 2:
                cat_count += 1
                sources.add(source_map.get(mat["source"], mat["source"]))
        
        source_str = "、".join(sorted(sources)[:3]) if sources else "-"
        import_overview += f"| {category} | {cat_count} | {source_str} |\n"
    
    import_overview += "\n"
    import_overview += f"**import 素材总计**: {len(all_materials)} 篇\n\n"
    
    # knowledge 目录映射
    knowledge_section = "## 📚 与 knowledge 目录的映射\n\n"
    knowledge_section += "site 文章分类与 knowledge 知识体系的对应关系：\n\n"
    knowledge_section += "| site分类 | knowledge对应目录 | 说明 |\n"
    knowledge_section += "|:---------|:-----------------|:-----|\n"
    
    knowledge_names = {
        "ai-apps": "AI应用",
        "ai-frameworks": "AI框架",
        "ai-solutions": "AI解决方案",
        "llm-trends": "大模型趋势",
        "bmc-system": "BMC系统",
        "ops-system": "运维系统",
        "server-hardware": "服务器硬件",
        "data-center": "数据中心",
        "distributed-os": "分布式系统",
        "linux-os": "Linux系统",
        "cloud-native": "云原生",
        "components-storage": "存储组件",
        "data-analysis": "数据分析",
        "cluster-training": "集群训练",
        "project-mgmt": "项目管理",
        "rd-management": "研发管理",
        "industry-research": "行业研究",
        "product-dev": "产品开发",
        "enterprise-mgmt": "企业管理",
    }
    
    for category, kg_dirs in CATEGORY_KNOWLEDGE_MAP.items():
        if kg_dirs:
            dir_names = [knowledge_names.get(d, d) for d in kg_dirs]
            dir_str = "、".join(dir_names[:3])
            knowledge_section += f"| {category} | {dir_str} | 技术内容互补，可对照阅读 |\n"
        else:
            knowledge_section += f"| {category} | - | 暂无直接映射 |\n"
    
    knowledge_section += "\n"
    
    # 找到插入位置
    insert_pos = content.find("## 使用说明")
    if insert_pos == -1:
        insert_pos = content.find("## 上层入口")
    if insert_pos == -1:
        insert_pos = len(content)
    
    new_content = content[:insert_pos]
    new_content += top20_section
    new_content += import_overview
    new_content += knowledge_section
    new_content += content[insert_pos:]
    
    index_path.write_text(new_content, encoding="utf-8")
    return True


def process_duplicates(all_articles, duplicates):
    marked = 0
    
    for dup in duplicates:
        path1 = dup["path1"]
        path2 = dup["path2"]
        
        # 以内容较长的为主版本
        if dup["len1"] >= dup["len2"]:
            main_path = path1
            dup_path = path2
        else:
            main_path = path2
            dup_path = path1
        
        if dup_path not in all_articles:
            continue
        
        try:
            content = dup_path.read_text(encoding="utf-8")
            
            if "🔄 **重定向**" in content:
                continue
            
            fm, body = parse_frontmatter(content)
            
            # 构建重定向提示
            redirect_note = f"\n> 🔄 **重定向**: 本文与 [{main_path.name}]({main_path.name}) 内容高度相似，建议阅读主版本。\n"
            redirect_note += f"> 主版本内容更完整，已保留为主版本。\n\n"
            
            # 找到H1之后插入
            h1_match = re.search(r'^# .+$', content, re.MULTILINE)
            if h1_match:
                h1_end = h1_match.end()
                new_content = content[:h1_end] + redirect_note + content[h1_end:]
                dup_path.write_text(new_content, encoding="utf-8")
                marked += 1
        except Exception as e:
            print(f"处理重复文章失败 {dup_path.name}: {e}")
    
    return marked


def main():
    print("=" * 70)
    print("文章质量全面提升 - import素材整合版")
    print("=" * 70)
    
    # 阶段1: 加载文章
    print("\n📚 阶段1: 加载文章数据...")
    all_articles, category_articles = load_all_articles()
    print(f"  共发现 {len(all_articles)} 篇文章，{len(category_articles)} 个分类")
    
    # 阶段2: 构建import素材索引
    print("\n📦 阶段2: 构建import素材索引...")
    all_materials = build_import_material_index()
    print(f"  共索引 {len(all_materials)} 个import素材文件")
    
    # 阶段3: 检测重复文章
    print("\n🔍 阶段3: 检测重复文章...")
    duplicates = find_duplicate_articles(all_articles)
    print(f"  发现 {len(duplicates)} 对重复/相似文章")
    for dup in duplicates[:10]:
        print(f"  - {dup['path1'].name} <-> {dup['path2'].name}")
    
    # 阶段4: 增强所有文章
    print("\n✨ 阶段4: 增强所有文章...")
    stats, featured = enhance_all_articles(
        all_articles, category_articles, all_materials, duplicates
    )
    print(f"  添加相关素材: {stats['added_materials']} 篇")
    print(f"  添加相关文章: {stats['added_related']} 篇")
    print(f"  深度增强精选: {stats['deep_enhanced']} 篇")
    
    # 阶段5: 增强分类索引
    print("\n📂 阶段5: 增强分类索引...")
    cat_enhanced = enhance_category_indexes(
        all_articles, category_articles, all_materials, duplicates
    )
    print(f"  增强分类索引: {cat_enhanced} 个")
    
    # 阶段6: 增强总索引
    print("\n📊 阶段6: 增强总索引...")
    main_enhanced = enhance_main_index(
        all_articles, category_articles, all_materials, featured
    )
    print(f"  总索引增强: {'是' if main_enhanced else '否'}")
    
    # 阶段7: 处理重复文章
    print("\n🔄 阶段7: 处理重复文章...")
    dup_marked = process_duplicates(all_articles, duplicates)
    print(f"  标记重复文章: {dup_marked} 篇")
    
    # 输出最终统计
    print("\n" + "=" * 70)
    print("🎉 处理完成统计")
    print("=" * 70)
    print(f"📄 文章总数: {stats['total']}")
    print(f"📎 添加相关素材: {stats['added_materials']} 篇")
    print(f"🔗 添加相关文章: {stats['added_related']} 篇")
    print(f"🌟 深度增强精选文章: {stats['deep_enhanced']} 篇")
    print(f"📂 增强分类索引: {cat_enhanced} 个")
    print(f"📊 增强总索引: {'是' if main_enhanced else '否'}")
    print(f"🔄 重复文章对: {len(duplicates)} 对")
    print(f"📦 索引import素材: {len(all_materials)} 个")
    
    # 保存统计数据
    stats_data = {
        "total_articles": stats["total"],
        "added_materials": stats["added_materials"],
        "added_related_articles": stats["added_related"],
        "deep_enhanced": stats["deep_enhanced"],
        "category_indexes_enhanced": cat_enhanced,
        "main_index_enhanced": main_enhanced,
        "duplicate_pairs": len(duplicates),
        "import_materials_indexed": len(all_materials),
        "featured_by_category": {cat: len(files) for cat, files in featured.items()},
    }
    
    stats_path = BASE_DIR / "enhancement_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 统计数据已保存至: {stats_path}")


if __name__ == "__main__":
    main()
