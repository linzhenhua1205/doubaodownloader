#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤4: 增强所有文章 - 添加相关素材、相关文章、精选深度增强
"""
import os, re, json, random
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from urllib.parse import quote

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

# 加载索引数据
with open(BASE_DIR / "articles_index.json", "r", encoding="utf-8") as f:
    idx_data = json.load(f)
    all_articles = idx_data["articles"]
    category_articles = idx_data["categories"]

with open(BASE_DIR / "materials_index.json", "r", encoding="utf-8") as f:
    all_materials = json.load(f)

with open(BASE_DIR / "duplicates.json", "r", encoding="utf-8") as f:
    duplicates = json.load(f)

print("=" * 60)
print("步骤4: 增强所有文章")
print("=" * 60)

# 精选文章配置
FEATURED_CONFIG = {
    "AI与机器学习": 10,
    "系统与运维": 10,
    "编程与开发": 10,
    "云计算": 5,
    "数据库与存储": 5,
    "行业动态": 5,
    "知识管理": 5,
}

# 关键词提取
def extract_keywords(text, max_keywords=15):
    stop_words = set(["的", "是", "在", "了", "和", "与", "及", "等", "也", "都", "就", "而", "其", "之", "以", "中", "上", "下", "为", "从", "到", "对", "将", "把", "被", "让", "使", "由", "向", "于"])
    words = re.findall(r'[\u4e00-\u9fa5A-Za-z0-9]{2,}', text)
    word_freq = defaultdict(int)
    for w in words:
        if w not in stop_words and len(w) >= 2:
            word_freq[w] += 1
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, f in sorted_words[:max_keywords]]

# 素材匹配
def match_materials(title, body_preview, top_n=3):
    article_keywords = set(extract_keywords(title + " " + body_preview, 20))
    scored = []
    
    for mat in all_materials:
        mat_text = mat["title"] + " " + mat["content_preview"][:500]
        mat_keywords = set(extract_keywords(mat_text, 15))
        common = article_keywords & mat_keywords
        keyword_score = len(common) / max(len(article_keywords), 1) * 10
        
        title_sim = SequenceMatcher(None, title, mat["title"]).ratio() * 8
        
        total = keyword_score + title_sim
        if total > 2.5:
            scored.append((mat, total, list(common)[:5]))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]

# 相关文章匹配
def match_related_articles(article_path, category, article_title, top_n=3):
    cat_arts = category_articles.get(category, [])
    other = [p for p in cat_arts if p != article_path]
    
    scored = []
    for p in other:
        if p in all_articles:
            sim = SequenceMatcher(None, article_title, all_articles[p]["title"]).ratio()
            scored.append((p, sim))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]

# 计算文章质量分
def quality_score(article_info):
    score = 0
    if article_info["content_len"] > 5000:
        score += 20
    elif article_info["content_len"] > 3000:
        score += 15
    elif article_info["content_len"] > 2000:
        score += 10
    elif article_info["content_len"] > 1000:
        score += 5
    
    title = article_info["title"]
    if re.search(r'202[56]', title):
        score += 5
    if re.search(r'深度|解析|全景|白皮书|研报|指南|架构|原理', title):
        score += 5
    
    return score

# 选定精选文章
print("\n选定精选文章...")
featured = {}
featured_flat = set()

for cat, n in FEATURED_CONFIG.items():
    if cat not in category_articles:
        continue
    arts = []
    for p in category_articles[cat]:
        if p in all_articles:
            s = quality_score(all_articles[p])
            arts.append((p, s))
    arts.sort(key=lambda x: x[1], reverse=True)
    selected = [p for p, s in arts[:n]]
    featured[cat] = selected
    featured_flat.update(selected)
    print(f"  {cat}: {len(selected)} 篇")

print(f"总计精选: {len(featured_flat)} 篇")

# 构建相关素材块
def build_materials_block(matched):
    if not matched:
        return ""
    block = "\n## 📎 相关素材\n\n"
    block += "来自 import 素材库的相关参考资料：\n\n"
    source_names = {
        "cnblogs": "博客园",
        "doubao": "豆包知识库",
        "work_jinghua": "精华文档",
        "qianwen": "千问知识库",
    }
    for mat, score, keywords in matched:
        src = source_names.get(mat["source"], mat["source"])
        # 从site目录到import目录的相对路径
        rel_parts = mat["rel_path"].split("/")
        # rel_path 是 discover/import/... ，从 site 目录要 ../import/...
        rel_link = "../" + "/".join(rel_parts[1:]) if len(rel_parts) > 1 else mat["rel_path"]
        block += f"- [{mat['title']}]({rel_link}) — 来源：{src}"
        if keywords:
            block += f"（关键词：{'、'.join(keywords[:3])}）"
        block += "\n"
    return block + "\n"

# 构建相关文章块
def build_related_block(related, category):
    if not related:
        return ""
    block = "\n## 🔗 相关文章\n\n"
    block += "同分类的相关文章推荐：\n\n"
    for p, sim in related:
        if p in all_articles:
            title = all_articles[p]["title"]
            fname = all_articles[p]["name"]
            block += f"- [{title}]({fname})\n"
    return block + "\n"

# 构建深度增强块
def build_deep_block(title, body, category, matched_materials):
    block = "\n---\n\n"
    
    # 背景与上下文
    block += "## 🌐 背景与上下文\n\n"
    backgrounds = {
        "AI与机器学习": "人工智能领域正经历前所未有的快速发展。2025-2026年，大语言模型从参数竞赛转向效率优化和场景落地，AI Agent、多模态、RAG等技术不断突破，企业级AI应用进入规模化部署阶段。",
        "系统与运维": "随着云计算和容器化技术的普及，系统运维正在从传统人工操作向自动化、智能化方向演进。DevOps、AIOps、可观测性等理念和工具不断成熟，运维效率和系统可靠性大幅提升。",
        "编程与开发": "软件开发技术持续演进，新的编程语言、框架和工具层出不穷。AI辅助编程、低代码平台、云原生开发等趋势正在深刻改变开发者的工作方式和生产力。",
        "数据库与存储": "数据量的爆炸式增长推动数据库和存储技术不断创新。从关系型数据库到NoSQL，从集中式存储到分布式存储，向量数据库等新型存储引擎应运而生。",
        "云计算": "云计算已成为企业IT基础设施的首选，云原生技术栈日趋成熟。混合云、多云、Serverless等架构模式被广泛采用，云成本优化和安全治理成为新的关注点。",
        "知识管理": "在信息爆炸的时代，知识管理的价值日益凸显。从个人知识管理到企业知识库，从传统文档到知识图谱，AI驱动的知识检索和问答正在重塑知识管理的形态。",
        "行业动态": "科技行业正处于快速变革期，AI、云计算、半导体等领域持续火热。技术迭代加速，产业格局重塑，企业需要密切关注行业动态以保持竞争优势。",
    }
    block += backgrounds.get(category, "本文探讨的领域正处于快速发展阶段，技术迭代和应用创新不断涌现。建议结合行业最新动态进行阅读和思考。")
    block += "\n\n"
    
    # 深度解读
    block += "## 🔍 深度解读\n\n"
    deep_points = []
    
    ai_keywords = ["AI", "大模型", "机器学习", "深度学习", "Agent", "人工智能", "LLM", "GPT"]
    ops_keywords = ["运维", "服务器", "监控", "DevOps", "BMC", "固件", "Linux", "Zabbix", "Ansible", "Docker"]
    dev_keywords = ["开发", "编程", "代码", "程序员", "算法", "架构", "软件"]
    db_keywords = ["数据库", "SQL", "MySQL", "PostgreSQL", "存储", "数据", "Redis", "MongoDB"]
    cloud_keywords = ["云", "云计算", "AWS", "阿里云", "华为云", "容器", "Kubernetes", "K8s"]
    km_keywords = ["知识", "笔记", "知识库", "学习", "管理"]
    
    if any(kw in title for kw in ai_keywords):
        deep_points.append("**技术演进视角**：大模型技术正从参数规模竞赛转向效率优化和场景落地，模型压缩、推理加速、RAG、Agent等技术成为产业落地的关键。")
        deep_points.append("**产业应用视角**：AI应用从对话交互向任务执行演进，智能体、工作流编排、多模态能力正在重塑企业业务流程和生产力。")
    if any(kw in title for kw in ops_keywords):
        deep_points.append("**技术趋势**：运维正在从被动响应向主动预防转变，AIOps和可观测性技术的成熟推动了这一转变，故障自愈成为可能。")
        deep_points.append("**效率提升**：自动化运维工具链的完善，使得运维人员可以从重复性工作中解放出来，聚焦于更高价值的架构优化和性能调优。")
    if any(kw in title for kw in dev_keywords):
        deep_points.append("**开发范式变革**：AI辅助编程工具的普及正在改变软件开发的工作方式，代码生成、代码补全、自动测试等能力显著提升开发者生产力。")
        deep_points.append("**技术栈演进**：云原生、微服务、低代码等技术趋势持续演进，开发者需要持续学习以适应快速变化的技术生态。")
    if any(kw in title for kw in db_keywords):
        deep_points.append("**数据价值释放**：随着企业数字化转型的深入，数据作为核心资产的价值日益凸显，数据库和存储技术是数据价值释放的基础支撑。")
        deep_points.append("**技术选型多元化**：从关系型到NoSQL，从集中式到分布式，从传统数据库到向量数据库，不同场景需要不同的数据存储解决方案。")
    if any(kw in title for kw in cloud_keywords):
        deep_points.append("**云原生普及**：容器、微服务、DevOps等云原生技术已经成为企业数字化转型的标准配置，云原生平台工程成为新的热点。")
        deep_points.append("**成本优化**：随着云支出的持续增长，FinOps和云成本优化成为企业关注的重点，资源利用率和成本透明度至关重要。")
    if any(kw in title for kw in km_keywords):
        deep_points.append("**知识管理价值**：在信息过载的时代，有效的知识管理能够显著提升个人和组织的学习效率与决策质量。")
        deep_points.append("**AI赋能知识管理**：大语言模型正在改变知识的检索、组织和呈现方式，智能问答和知识图谱成为知识库的标配功能。")
    
    if not deep_points:
        deep_points.append("**行业价值**：本文所讨论的主题在当前技术发展趋势中具有重要的参考价值，建议结合实际场景深入理解。")
        deep_points.append("**延伸思考**：技术的发展往往伴随着方法论的演进，关注底层逻辑比关注具体工具更能建立持久的竞争力。")
    
    for point in deep_points:
        block += f"- {point}\n"
    
    block += "\n"
    
    # 更新记录
    block += "## 🆕 更新记录（2025-2026）\n\n"
    updates = {
        "AI与机器学习": [
            "2026年：多模态大模型能力持续增强，视频生成和理解取得突破性进展",
            "2025年底：AI Agent技术标准化加速，MCP、Skills等协议生态日趋完善",
            "2025年中：开源大模型性能追赶闭源模型，模型可及性大幅提升",
        ],
        "系统与运维": [
            "2026年：AIOps从概念走向规模化落地，智能告警根因分析成为运维标配",
            "2025年：可观测性技术成熟，日志、指标、链路三支柱整合加速",
            "2025年：GitOps和平台工程理念普及，运维自动化程度持续提升",
        ],
        "编程与开发": [
            "2026年：AI编程助手深度集成IDE，代码生成质量和实用性显著提升",
            "2025年：低代码/无代码平台快速发展，应用开发门槛持续降低",
            "2025年：Rust、Go等现代语言采用率持续增长",
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
            "2025年：企业知识库与大模型结合，知识管理价值被重新定义",
        ],
        "行业动态": [
            "2026年：全球科技产业继续深度调整，AI驱动的新一轮创新周期开启",
            "2025年：开源软件生态持续繁荣，成为技术创新的重要力量",
            "2025年：数据安全和隐私保护法规日趋完善，影响技术发展方向",
        ],
    }
    
    cat_updates = updates.get(category, [
        "2026年：技术持续演进，建议关注最新行业动态",
        "2025年：相关领域持续发展，新的工具和方法不断涌现",
    ])
    
    for note in cat_updates:
        block += f"- {note}\n"
    
    block += "\n"
    
    return block

# 开始处理文章
print("\n开始处理文章...")
stats = {
    "total": len(all_articles),
    "added_materials": 0,
    "added_related": 0,
    "deep_enhanced": 0,
}

for idx, (path, info) in enumerate(all_articles.items(), 1):
    if idx % 50 == 0:
        print(f"  进度: {idx}/{len(all_articles)}")
    
    try:
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        
        # 检查是否已处理
        has_materials = "## 📎 相关素材" in content
        has_related = "## 🔗 相关文章" in content
        has_deep = "## 🌐 背景与上下文" in content
        
        # 如果都有了，跳过
        if has_materials and has_related and (path not in featured_flat or has_deep):
            continue
        
        title = info["title"]
        category = info["category"]
        
        # 获取正文预览
        body_preview = content[:1500]
        
        # 匹配素材
        matched = match_materials(title, body_preview, 3)
        
        # 匹配相关文章
        related = match_related_articles(path, category, title, 3)
        
        # 构建新增块
        additions = ""
        
        if not has_materials and matched:
            additions += build_materials_block(matched)
            stats["added_materials"] += 1
        
        if not has_related and related:
            additions += build_related_block(related, category)
            stats["added_related"] += 1
        
        if path in featured_flat and not has_deep:
            additions += build_deep_block(title, content, category, matched)
            stats["deep_enhanced"] += 1
        
        if not additions:
            continue
        
        # 找到插入位置 - 在"延伸阅读"之前或文章末尾
        insert_pos = content.find("## 📚 延伸阅读")
        if insert_pos == -1:
            insert_pos = content.find("## 上层入口")
        if insert_pos == -1:
            insert_pos = content.find("*本文由Wiki系统自动生成*")
        if insert_pos == -1:
            insert_pos = len(content)
        
        new_content = content[:insert_pos] + additions + content[insert_pos:]
        
        file_path.write_text(new_content, encoding="utf-8")
        
    except Exception as e:
        print(f"  错误: {info['name']}: {e}")

print(f"\n✅ 文章增强完成!")
print(f"  添加相关素材: {stats['added_materials']} 篇")
print(f"  添加相关文章: {stats['added_related']} 篇")
print(f"  深度增强精选: {stats['deep_enhanced']} 篇")

# 保存精选文章列表
with open(BASE_DIR / "featured_articles.json", "w", encoding="utf-8") as f:
    json.dump({
        "featured_by_category": {k: [all_articles[p]["title"] for p in v] for k, v in featured.items()},
        "total_featured": len(featured_flat),
        "stats": stats,
    }, f, ensure_ascii=False, indent=2)

print(f"\n精选文章列表已保存到 featured_articles.json")
