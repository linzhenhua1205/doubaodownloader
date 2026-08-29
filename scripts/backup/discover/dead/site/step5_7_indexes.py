#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤5-7: 分类索引增强、总索引增强、重复文章处理
"""
import os, re, json, random
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from urllib.parse import quote

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

with open(BASE_DIR / "articles_index.json", "r", encoding="utf-8") as f:
    idx_data = json.load(f)
    all_articles = idx_data["articles"]
    category_articles = idx_data["categories"]

with open(BASE_DIR / "materials_index.json", "r", encoding="utf-8") as f:
    all_materials = json.load(f)

with open(BASE_DIR / "duplicates.json", "r", encoding="utf-8") as f:
    duplicates = json.load(f)

with open(BASE_DIR / "featured_articles.json", "r", encoding="utf-8") as f:
    featured_data = json.load(f)

# 分类知识图谱
KNOWLEDGE_GRAPH = {
    "AI与机器学习": {
        "核心领域": ["大语言模型", "机器学习", "深度学习", "AI Agent", "计算机视觉", "自然语言处理"],
        "关键技术": ["Transformer", "RAG检索增强", "模型微调", "量化压缩", "多模态", "强化学习"],
        "应用场景": ["智能客服", "代码生成", "内容创作", "数据分析", "自动驾驶", "医疗诊断"],
    },
    "系统与运维": {
        "核心领域": ["服务器运维", "监控系统", "DevOps", "容器化", "自动化运维", "性能优化"],
        "关键技术": ["Docker", "Kubernetes", "Zabbix", "Ansible", "ELK Stack", "Prometheus"],
        "应用场景": ["服务器管理", "故障排查", "容量规划", "安全审计", "日志分析", "配置管理"],
    },
    "编程与开发": {
        "核心领域": ["编程语言", "软件开发", "系统架构", "算法设计", "代码质量", "开发工具"],
        "关键技术": ["Python", "Java", "C/C++", "Go语言", "微服务", "云原生"],
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
        "关键技术": ["Markdown", "Wiki系统", "双向链接", "标签系统", "智能检索", "知识萃取"],
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

# 分类学习路径
LEARNING_PATHS = {
    "AI与机器学习": [
        "1. 基础入门：了解AI基本概念、发展历史、应用场景",
        "2. 技术原理：学习机器学习基础算法、深度学习原理",
        "3. 实践应用：动手实践模型训练、RAG应用开发",
        "4. 前沿探索：关注大模型、Agent、多模态等前沿方向",
    ],
    "系统与运维": [
        "1. 基础入门：操作系统基础、网络原理、服务器硬件",
        "2. 工具掌握：学习Linux命令、Shell脚本、常用运维工具",
        "3. 系统架构：理解集群、负载均衡、高可用架构",
        "4. 进阶提升：自动化运维、监控告警、性能调优",
    ],
    "编程与开发": [
        "1. 基础入门：选择一门编程语言，掌握基本语法和数据结构",
        "2. 实践项目：通过小项目巩固知识，学习版本控制",
        "3. 架构设计：学习设计模式、系统架构、代码质量",
        "4. 持续成长：关注新技术、参与开源、建立技术影响力",
    ],
    "数据库与存储": [
        "1. 基础入门：SQL基础、关系型数据库原理",
        "2. 实践应用：数据库设计、查询优化、备份恢复",
        "3. 扩展学习：NoSQL数据库、分布式存储、数据仓库",
        "4. 进阶提升：性能调优、架构设计、数据治理",
    ],
    "云计算": [
        "1. 基础入门：云计算概念、服务模式（IaaS/PaaS/SaaS）",
        "2. 核心服务：计算、存储、网络三大基础服务",
        "3. 云原生：容器、Kubernetes、微服务架构",
        "4. 进阶实践：云架构设计、成本优化、安全治理",
    ],
    "知识管理": [
        "1. 理念认知：理解知识管理的价值、建立个人知识体系",
        "2. 工具选择：选择适合的笔记工具、知识库系统",
        "3. 方法实践：学习笔记方法、知识萃取、信息整理技巧",
        "4. 持续优化：形成知识闭环、定期回顾、体系迭代",
    ],
    "行业动态": [
        "1. 广泛涉猎：关注多个领域的动态，建立行业认知",
        "2. 重点聚焦：选择2-3个重点方向深入跟踪",
        "3. 分析思考：不仅看新闻，更要分析背后的逻辑和趋势",
        "4. 形成洞察：建立自己的行业判断和认知框架",
    ],
}

print("=" * 60)
print("步骤5: 增强分类索引")
print("=" * 60)

cat_enhanced = 0

for category in category_articles.keys():
    index_path = BASE_DIR / category / "index.md"
    if not index_path.exists():
        continue
    
    try:
        content = index_path.read_text(encoding="utf-8", errors="ignore")
        
        if "## 📦 import 相关素材" in content:
            continue
        
        # 匹配该分类的import素材
        cat_keywords_map = {
            "AI与机器学习": ["AI", "机器学习", "深度学习", "大模型", "神经网络", "Agent", "LLM", "GPT", "人工智能"],
            "系统与运维": ["运维", "服务器", "监控", "BMC", "固件", "Linux", "Ansible", "Zabbix", "Docker", "ELK"],
            "编程与开发": ["编程", "开发", "算法", "C++", "Python", "Java", "代码", "程序", "软件"],
            "数据库与存储": ["数据库", "SQL", "存储", "MySQL", "PostgreSQL", "RAID", "数据", "Redis"],
            "云计算": ["云", "云计算", "AWS", "阿里云", "容器", "K8s", "Kubernetes", "云原生"],
            "知识管理": ["知识", "笔记", "知识库", "学习", "管理", "Wiki", "文档"],
            "行业动态": ["行业", "市场", "趋势", "报告", "分析", "融资", "发布会"],
            "产品与设计": ["产品", "设计", "UX", "用户体验", "交互", "UI"],
            "人文社会": ["管理", "社会", "企业", "人文", "历史", "经济", "组织"],
            "其他": ["工具", "效率", "生活", "科技"],
        }
        
        keywords = cat_keywords_map.get(category, [])
        cat_materials = []
        
        for mat in all_materials:
            mat_text = mat["title"] + " " + mat["content_preview"][:500]
            score = sum(1 for kw in keywords if kw in mat_text)
            if score >= 2:
                cat_materials.append((mat, score))
        
        cat_materials.sort(key=lambda x: x[1], reverse=True)
        cat_materials = cat_materials[:10]
        
        # import素材板块
        materials_section = ""
        if cat_materials:
            materials_section = "\n## 📦 import 相关素材\n\n"
            materials_section += f"本分类关联的 import 素材库资源（精选 {len(cat_materials)} 项）：\n\n"
            source_names = {
                "cnblogs": "博客园",
                "doubao": "豆包知识库",
                "work_jinghua": "精华文档",
                "qianwen": "千问知识库",
            }
            for mat, score in cat_materials:
                src = source_names.get(mat["source"], mat["source"])
                rel_parts = mat["rel_path"].split("/")
                rel_link = "../" + "/".join(rel_parts[1:]) if len(rel_parts) > 1 else mat["rel_path"]
                materials_section += f"- [{mat['title']}]({rel_link}) — {src}\n"
            materials_section += "\n"
        
        # 知识图谱板块
        kg = KNOWLEDGE_GRAPH.get(category, {})
        kg_section = "## 🧠 分类知识图谱\n\n"
        kg_section += "本分类涵盖的核心技术领域：\n\n"
        for section_title, items in kg.items():
            kg_section += f"### {section_title}\n\n"
            for item in items:
                kg_section += f"- {item}\n"
            kg_section += "\n"
        
        # 学习路径板块
        lp = LEARNING_PATHS.get(category, [
            "1. 基础入门：了解基本概念和核心术语",
            "2. 实践应用：通过实践加深理解",
            "3. 深入学习：掌握核心技术和原理",
            "4. 持续进阶：关注前沿动态和最佳实践",
        ])
        
        lp_section = "## 🛤️ 学习路径建议\n\n"
        lp_section += "从入门到进阶的阅读顺序建议：\n\n"
        for step in lp:
            lp_section += f"- {step}\n"
        lp_section += "\n"
        
        # 找到插入位置
        insert_pos = content.find("## 上层入口")
        if insert_pos == -1:
            insert_pos = len(content)
        
        new_content = content[:insert_pos]
        new_content += materials_section
        new_content += kg_section
        new_content += lp_section
        new_content += content[insert_pos:]
        
        index_path.write_text(new_content, encoding="utf-8")
        cat_enhanced += 1
        print(f"  ✓ {category}/index.md （关联 {len(cat_materials)} 个素材）")
        
    except Exception as e:
        print(f"  ✗ {category}: {e}")

print(f"\n增强分类索引: {cat_enhanced} 个")

print("\n" + "=" * 60)
print("步骤6: 增强总索引")
print("=" * 60)

main_index_path = BASE_DIR / "index.md"
if main_index_path.exists():
    content = main_index_path.read_text(encoding="utf-8", errors="ignore")
    
    if "## 🏆 高质量文章 TOP20" not in content:
        # 计算所有文章质量分
        def quality_score(info):
            score = 0
            if info["content_len"] > 5000:
                score += 20
            elif info["content_len"] > 3000:
                score += 15
            elif info["content_len"] > 2000:
                score += 10
            elif info["content_len"] > 1000:
                score += 5
            title = info["title"]
            if re.search(r'202[56]', title):
                score += 5
            if re.search(r'深度|解析|全景|白皮书|研报|指南|架构|原理', title):
                score += 5
            return score
        
        all_scored = []
        for path, info in all_articles.items():
            s = quality_score(info)
            all_scored.append((path, info, s))
        
        all_scored.sort(key=lambda x: x[2], reverse=True)
        top20 = all_scored[:20]
        
        # TOP20板块
        top20_section = "\n## 🏆 高质量文章 TOP20\n\n"
        top20_section += "推荐阅读的20篇高质量文章：\n\n"
        top20_section += "| 排名 | 分类 | 文章标题 | 质量分 |\n"
        top20_section += "|:----:|:-----|:---------|:------:|\n"
        
        for idx, (path, info, score) in enumerate(top20, 1):
            cat = info["category"]
            fname = info["name"]
            encoded_name = quote(fname)
            title_display = info["title"][:50]
            top20_section += f"| {idx} | {cat} | [{title_display}]({cat}/{encoded_name}) | {score} |\n"
        
        top20_section += "\n"
        
        # import素材关联总览
        cat_keywords_map = {
            "AI与机器学习": ["AI", "机器学习", "深度学习", "大模型", "神经网络", "Agent", "LLM", "GPT", "人工智能"],
            "系统与运维": ["运维", "服务器", "监控", "BMC", "固件", "Linux", "Ansible", "Zabbix", "Docker", "ELK"],
            "编程与开发": ["编程", "开发", "算法", "C++", "Python", "Java", "代码", "程序", "软件"],
            "数据库与存储": ["数据库", "SQL", "存储", "MySQL", "PostgreSQL", "RAID", "数据", "Redis"],
            "云计算": ["云", "云计算", "AWS", "阿里云", "容器", "K8s", "Kubernetes", "云原生"],
            "知识管理": ["知识", "笔记", "知识库", "学习", "管理", "Wiki", "文档"],
            "行业动态": ["行业", "市场", "趋势", "报告", "分析", "融资", "发布会"],
            "产品与设计": ["产品", "设计", "UX", "用户体验", "交互", "UI"],
            "人文社会": ["管理", "社会", "企业", "人文", "历史", "经济", "组织"],
            "其他": ["工具", "效率", "生活", "科技"],
        }
        
        source_names = {
            "cnblogs": "博客园",
            "doubao": "豆包",
            "work_jinghua": "精华文档",
            "qianwen": "千问",
        }
        
        import_section = "## 📦 与 import 素材的关联\n\n"
        import_section += "各分类与 import 素材库的关联统计：\n\n"
        import_section += "| 分类 | 关联素材数 | 主要来源 |\n"
        import_section += "|:-----|:----------:|:---------|\n"
        
        total_matched = 0
        for category in category_articles.keys():
            keywords = cat_keywords_map.get(category, [])
            cat_count = 0
            sources = set()
            for mat in all_materials:
                mat_text = mat["title"] + " " + mat["content_preview"][:500]
                score = sum(1 for kw in keywords if kw in mat_text)
                if score >= 2:
                    cat_count += 1
                    sources.add(source_names.get(mat["source"], mat["source"]))
            total_matched += cat_count
            source_str = "、".join(sorted(sources)[:3]) if sources else "-"
            import_section += f"| {category} | {cat_count} | {source_str} |\n"
        
        import_section += f"\n**import 素材总计**: {len(all_materials)} 篇\n"
        import_section += f"**可匹配素材**: 约 {total_matched} 篇次（含跨分类重复）\n\n"
        
        # knowledge目录映射
        knowledge_map = {
            "AI与机器学习": "AI应用、AI框架、AI解决方案、大模型趋势",
            "系统与运维": "BMC系统、运维系统、服务器硬件、数据中心",
            "编程与开发": "分布式系统、Linux系统、云原生",
            "数据库与存储": "存储组件、数据分析",
            "云计算": "云原生、集群训练",
            "知识管理": "项目管理、研发管理",
            "行业动态": "行业研究",
            "产品与设计": "产品开发",
            "人文社会": "企业管理",
            "其他": "-",
        }
        
        knowledge_section = "## 📚 与 knowledge 目录的映射\n\n"
        knowledge_section += "site 文章分类与 knowledge 知识体系的对应关系：\n\n"
        knowledge_section += "| site分类 | knowledge对应领域 | 说明 |\n"
        knowledge_section += "|:---------|:-----------------|:-----|\n"
        
        for cat, km in knowledge_map.items():
            knowledge_section += f"| {cat} | {km} | 技术内容互补，可对照阅读 |\n"
        
        knowledge_section += "\n"
        knowledge_section += "> 💡 **使用建议**：site 侧重资讯和时效性内容，knowledge 侧重系统化知识体系，两者结合阅读效果更佳。\n\n"
        
        # 插入内容
        insert_pos = content.find("## 使用说明")
        if insert_pos == -1:
            insert_pos = content.find("## 上层入口")
        if insert_pos == -1:
            insert_pos = len(content)
        
        new_content = content[:insert_pos]
        new_content += top20_section
        new_content += import_section
        new_content += knowledge_section
        new_content += content[insert_pos:]
        
        main_index_path.write_text(new_content, encoding="utf-8")
        print("  ✓ 总索引已增强")
    else:
        print("  - 总索引已增强过，跳过")
else:
    print("  - 总索引不存在")

print("\n" + "=" * 60)
print("步骤7: 处理重复文章")
print("=" * 60)

dup_marked = 0

for dup in duplicates:
    path1 = Path(dup["path1"])
    path2 = Path(dup["path2"])
    
    # 以内容较长的为主版本
    if dup["len1"] >= dup["len2"]:
        main_path = path1
        dup_path = path2
    else:
        main_path = path2
        dup_path = path1
    
    if not dup_path.exists():
        continue
    
    try:
        content = dup_path.read_text(encoding="utf-8", errors="ignore")
        
        if "🔄 **重定向**" in content:
            continue
        
        # 构建重定向提示
        redirect_note = f"\n> 🔄 **重定向**: 本文与 [{main_path.name}]({main_path.name}) 内容高度相似，建议阅读主版本。\n"
        redirect_note += f"> 主版本内容更完整，已保留为主要阅读版本。\n\n"
        
        # 找到H1之后插入
        h1_match = re.search(r'^# .+$', content, re.MULTILINE)
        if h1_match:
            h1_end = h1_match.end()
            new_content = content[:h1_end] + redirect_note + content[h1_end:]
            dup_path.write_text(new_content, encoding="utf-8")
            dup_marked += 1
            print(f"  ✓ {dup_path.name[:40]} → {main_path.name[:40]}")
    except Exception as e:
        print(f"  ✗ {dup_path.name}: {e}")

print(f"\n标记重复文章: {dup_marked} 篇")

print("\n" + "=" * 60)
print("🎉 步骤5-7完成统计")
print("=" * 60)
print(f"📂 增强分类索引: {cat_enhanced} 个")
print(f"📊 增强总索引: 1 个")
print(f"🔄 标记重复文章: {dup_marked} 篇")

# 保存最终统计
final_stats = {
    "category_indexes_enhanced": cat_enhanced,
    "main_index_enhanced": True,
    "duplicates_marked": dup_marked,
    "total_duplicate_pairs": len(duplicates),
}

with open(BASE_DIR / "final_stats.json", "w", encoding="utf-8") as f:
    json.dump(final_stats, f, ensure_ascii=False, indent=2)

print(f"\n统计已保存到 final_stats.json")
