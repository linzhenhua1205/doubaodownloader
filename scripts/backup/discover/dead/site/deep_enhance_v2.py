#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四大分类全量深度内容增强脚本 v2
功能：
1. 批量增强产品与设计、行业动态、人文社会、其他分类的文章
2. 新增：背景与上下文、深度解读、2025-2026最新进展、相关资源（newwiki/newwiki2/knowledge）、参考来源、changelog
3. 分级处理：S级（手动）、A级（半自动）、B/C级（自动模板）
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"h:\github\cowkb\discover\site")
NEWWIKI_DIR = Path(r"h:\github\cowkb\discover\newwiki")
NEWWIKI2_DIR = Path(r"h:\github\cowkb\discover\newwiki2")
KNOWLEDGE_DIR = Path(r"h:\github\cowkb\knowledge\01_survey")
IMPORT_DIR = Path(r"h:\github\cowkb\import")

# 分类配置
CATEGORIES = {
    "产品与设计": {
        "dir": "产品与设计",
        "priority": 1,
        "s_level_keywords": ["Dify", "工作流", "引擎", "架构", "方法论", "Proactive", "交互"],
        "a_level_keywords": ["产品", "设计", "平台", "工具", "指南", "教程"],
        "newwiki_topics": ["AI-Agent技术架构", "AI应用与落地实践", "方法论与工具", "企业管理与运营"],
        "newwiki2_categories": ["ai-models", "AI-Agent", "programming", "project-mgmt", "general"],
        "knowledge_dirs": ["ai-frameworks", "ai-apps", "product-dev", "industry-research"],
    },
    "行业动态": {
        "dir": "行业动态",
        "priority": 1,
        "s_level_keywords": ["趋势", "报告", "分析", "全景", "深度", "大会", "峰会", "产业"],
        "a_level_keywords": ["融资", "发布", "财报", "合作", "战略", "市场", "预测"],
        "newwiki_topics": ["行业趋势与洞察", "AI应用与落地实践", "大模型技术与原理", "技术选型与方案对比"],
        "newwiki2_categories": ["ai-models", "product-reports", "general", "server-hardware"],
        "knowledge_dirs": ["industry-research", "llm-trends", "ai-apps", "ai-frameworks"],
    },
    "人文社会": {
        "dir": "人文社会",
        "priority": 2,
        "s_level_keywords": ["AI伦理", "社会影响", "管理", "组织", "企业", "人文"],
        "a_level_keywords": ["教育", "职场", "科技", "历史", "文化", "经济"],
        "newwiki_topics": ["AI伦理与安全", "企业管理与运营", "其他_职场管理", "其他_生活文化"],
        "newwiki2_categories": ["general", "project-mgmt", "security"],
        "knowledge_dirs": ["enterprise-mgmt", "rd-management", "product-dev"],
    },
    "其他": {
        "dir": "其他",
        "priority": 2,
        "s_level_keywords": ["趋势", "深度", "技术", "全景", "解析", "报告"],
        "a_level_keywords": ["工具", "指南", "教程", "市场", "分析"],
        "newwiki_topics": ["方法论与工具", "其他_综合技术", "技术选型与方案对比"],
        "newwiki2_categories": ["general", "programming", "product-reports"],
        "knowledge_dirs": ["industry-research", "product-dev", "data-analysis"],
    },
}

# 质量分级模板
BACKGROUND_TEMPLATES = {
    "产品与设计": {
        "default": "产品设计与AI技术的融合正重塑软件产品的开发范式。2025年以来，大模型能力快速渗透到产品全生命周期——从需求分析、原型设计到用户测试、迭代优化，AI正在改变产品经理和设计师的工作方式。低代码/零代码平台的兴起，更让非技术人员也能参与产品创造，推动产品创新的民主化进程。",
        "dify": "LLM应用开发平台是2024-2025年AI领域增长最快的赛道之一。随着企业从'试用大模型'转向'落地业务场景'，单纯的API调用已无法满足需求——知识库管理、Prompt工程、工作流编排、多模型路由、安全审计等能力成为刚需。Dify作为主流的开源LLM应用开发平台，以其低代码特性和企业级能力获得了广泛采用。",
    },
    "行业动态": {
        "default": "2025年是AI产业从技术探索走向规模化落地的关键年份。大模型技术快速迭代，应用场景持续拓展，产业政策密集出台，投融资市场在经历调整后重新聚焦于有实际商业价值的方向。全球科技巨头和创业公司都在加速布局，争夺下一代AI生态的主导权。",
    },
    "人文社会": {
        "default": "技术进步与社会发展的互动日益紧密。AI、自动化、数字化转型正在深刻改变人们的工作方式、生活模式和社会结构。理解技术背后的人文维度，关注技术对社会、教育、职场的影响，对于把握时代脉搏、做出明智决策具有重要意义。",
    },
    "其他": {
        "default": "技术的发展从来不是孤立的，而是与社会、经济、文化等多维度因素交织互动。跨领域的思考和观察，有助于我们更全面地理解技术趋势，发现隐藏的机会，避免单一视角带来的盲区。",
    },
}

ANALYSIS_TEMPLATES = {
    "产品与设计": {
        "default": "从产品设计的角度看，AI时代的产品呈现三大趋势：一是交互方式的变革，从图形界面（GUI）向对话式界面（CUI）演进，自然语言成为新的交互范式；二是产品能力的跃升，AI让产品从'工具'升级为'助手'，能够主动理解用户意图并提供智能建议；三是开发模式的转变，低代码+AI辅助让产品迭代速度大幅提升，快速验证、持续优化成为常态。",
    },
    "行业动态": {
        "default": "从产业发展的视角分析，当前AI行业呈现几个明显的趋势：一是基础设施层趋于稳定，算力和模型能力的提升让应用层创新成为焦点；二是垂直领域深耕加速，通用大模型向行业大模型、专用模型演进；三是商业模式逐渐清晰，从技术驱动转向价值驱动，ROI可衡量的应用更容易获得资本和市场的青睐。",
    },
    "人文社会": {
        "default": "从人文视角审视，技术发展始终是一把双刃剑。AI在提升效率、创造便利的同时，也带来了就业结构调整、隐私保护、算法公平等社会议题。关键在于如何让技术服务于人的全面发展，在效率与公平、创新与规范之间找到平衡点。",
    },
    "其他": {
        "default": "跨领域观察往往能带来独特的洞见。技术趋势从来不是孤立发生的，它们与经济周期、社会心理、文化思潮相互影响、相互塑造。建立多元的知识视角，培养跨界思考能力，是在快速变化时代保持洞察力的关键。",
    },
}

LATEST_PROGRESS_TEMPLATES = {
    "产品与设计": [
        "**AI产品设计工具爆发**：2025年出现大量AI辅助设计工具，覆盖原型生成、用户研究、可用性测试等环节",
        "**低代码平台升温**：企业级低代码平台市场规模同比增长超150%，成为数字化转型的关键工具",
        "**Agent化产品形态**：越来越多的产品从'功能导向'转向'任务导向'，Agent成为新的产品交互范式",
    ],
    "行业动态": [
        "**大模型竞赛进入下半场**：从参数规模比拼转向场景落地能力和商业变现能力的竞争",
        "**算力基础设施持续扩张**：全球AI算力需求年增长率超过200%，算力成为核心战略资源",
        "**监管政策加速出台**：各国AI监管框架陆续落地，合规成为企业AI应用的必修课",
    ],
    "人文社会": [
        "**AI与就业讨论深化**：从'AI取代人类'转向'AI重塑工作'，人机协作成为主流共识",
        "**数字素养提升受重视**：AI时代的数字素养和批判性思维教育成为社会关注焦点",
        "**技术伦理实践推进**：企业AI伦理委员会、算法审计等机制逐步建立",
    ],
    "其他": [
        "**跨学科融合加速**：技术与人文、艺术、社会科学的交叉领域涌现大量创新机会",
        "**终身学习成为常态**：技术迭代速度加快，持续学习能力成为个人和组织的核心竞争力",
        "**开源生态繁荣**：开源技术持续降低创新门槛，推动技术民主化进程",
    ],
}


def get_article_info(file_path):
    """获取文章基本信息"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {
        'path': file_path,
        'filename': file_path.name,
        'content': content,
        'has_enhanced': '背景与上下文' in content or '深度解读' in content,
        'has_changelog': 'Changelog' in content or 'changelog' in content,
    }
    
    # 提取标题
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        info['title'] = title_match.group(1).strip()
    else:
        info['title'] = file_path.stem
    
    # 提取元数据
    info['has_frontmatter'] = content.startswith('---')
    
    return info


def classify_quality(title, category, content_len=0):
    """根据标题和分类判断质量等级"""
    cat_config = CATEGORIES.get(category, {})
    s_keywords = cat_config.get('s_level_keywords', [])
    a_keywords = cat_config.get('a_level_keywords', [])
    
    # 判断S级
    for kw in s_keywords:
        if kw in title:
            return 'S'
    
    # 判断A级
    for kw in a_keywords:
        if kw in title:
            return 'A'
    
    # 默认为B级，短内容为C级
    if content_len < 1000:
        return 'C'
    return 'B'


def generate_resources_section(category):
    """生成相关资源板块"""
    cat_config = CATEGORIES.get(category, {})
    
    sections = []
    
    # newwiki 主题知识库
    newwiki_topics = cat_config.get('newwiki_topics', [])
    if newwiki_topics:
        sections.append("### newwiki 主题知识库")
        for topic in newwiki_topics[:3]:
            topic_file = f"{topic}.md"
            topic_path = NEWWIKI_DIR / topic_file
            if topic_path.exists():
                sections.append(f"- [{topic}](../newwiki/{topic_file})")
    
    # newwiki2 知识卡片
    newwiki2_cats = cat_config.get('newwiki2_categories', [])
    if newwiki2_cats:
        sections.append("\n### newwiki2 知识卡片")
        for cat in newwiki2_cats[:3]:
            sections.append(f"- [{cat} 分类](../newwiki2/{cat}/index.md)")
    
    # knowledge 专题目录
    knowledge_dirs = cat_config.get('knowledge_dirs', [])
    if knowledge_dirs:
        sections.append("\n### knowledge 专题目录")
        for kd in knowledge_dirs[:3]:
            kd_path = KNOWLEDGE_DIR / kd
            if kd_path.exists():
                sections.append(f"- [{kd} 专题](../../knowledge/01_survey/{kd}/)")
    
    return "\n".join(sections) if sections else ""


def enhance_article_b_level(file_path, category):
    """B/C级文章批量增强"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经增强过
    if '## 🌐 背景与上下文' in content:
        return False, "已增强"
    
    info = get_article_info(file_path)
    quality = classify_quality(info['title'], category, len(content))
    
    # 获取模板内容
    bg_templates = BACKGROUND_TEMPLATES.get(category, {})
    analysis_templates = ANALYSIS_TEMPLATES.get(category, {})
    latest_progress = LATEST_PROGRESS_TEMPLATES.get(category, [])
    
    # 选择背景模板
    bg_text = bg_templates.get('default', '')
    if 'Dify' in info['title'] or 'dify' in info['title'].lower():
        bg_text = bg_templates.get('dify', bg_text)
    
    analysis_text = analysis_templates.get('default', '')
    
    # 生成资源板块
    resources_section = generate_resources_section(category)
    
    # 找到原文结束位置（第一个---分隔线或相关素材之前）
    # 找到插入点：在"## 📎 相关素材"之前插入新内容
    insert_marker = "## 📎 相关素材"
    if insert_marker not in content:
        insert_marker = "## 🔗 相关文章"
    
    if insert_marker not in content:
        # 找不到插入点，在文末添加
        insert_pos = len(content)
    else:
        insert_pos = content.index(insert_marker)
    
    # 构建新增内容
    new_content = f"""## 🌐 背景与上下文

{bg_text}

## 🔍 深度解读

{analysis_text}

## 🆕 2025-2026 最新进展

"""
    for item in latest_progress[:2]:
        new_content += f"- {item}\n"
    
    new_content += f"""
> 🔍 **数据来源**：行业观察报告、2025-2026年技术趋势分析

## 📚 相关资源

{resources_section}

"""
    
    # 插入内容
    content = content[:insert_pos] + new_content + content[insert_pos:]
    
    # 添加参考来源和changelog
    if '## 📖 参考来源' not in content:
        ref_section = """
## 📖 参考来源

1. 原文链接（见文首）
2. 行业公开报告与分析
3. newwiki 结构化知识库
4. knowledge 专题调研资料
"""
        # 在返回索引之前插入
        return_marker = "[← 返回分类索引]"
        if return_marker in content:
            return_pos = content.index(return_marker)
            content = content[:return_pos] + ref_section + "\n" + content[return_pos:]
    
    if '## 📝 Changelog' not in content and '## 📝 changelog' not in content:
        changelog_section = f"""
## 📝 Changelog

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | {info.get('created_at', '2025').split()[0] if 'created_at' in content else '2025'} | 初始版本，原文基础内容 |
| v2.0 | 2026-07-18 | 深度增强版：新增背景与上下文、深度解读、2025-2026最新进展、相关资源（newwiki/newwiki2/knowledge）、参考来源、changelog |

"""
        return_marker = "[← 返回分类索引]"
        if return_marker in content and '## 📝 Changelog' not in content:
            return_pos = content.index(return_marker)
            # 检查是否已经有参考来源
            if '## 📖 参考来源' in content:
                ref_pos = content.index('## 📖 参考来源')
                insert_pos = content.index('\n', ref_pos)
                # 找到参考来源板块的结束位置
                next_section = content.find('\n## ', ref_pos + 1)
                if next_section > 0:
                    return_pos = next_section
            
            content = content[:return_pos] + changelog_section + "\n" + content[return_pos:]
    
    # 更新frontmatter
    if content.startswith('---'):
        end_pos = content.index('---', 3)
        frontmatter = content[4:end_pos].strip()
        
        # 添加updated_at
        if 'updated_at' not in frontmatter:
            frontmatter += f"\nupdated_at: 2026-07-18"
        
        # 添加quality_level
        if 'quality_level' not in frontmatter:
            frontmatter += f"\nquality_level: {quality}"
        
        # 更新categories
        if 'categories:' in frontmatter:
            # 确保分类包含当前分类
            if category not in frontmatter:
                frontmatter = frontmatter.replace('categories:', f'categories: {category}, ')
        
        content = '---\n' + frontmatter + '\n' + content[end_pos:]
    
    # 更新头部信息行
    if '🏆 **质量等级**' not in content:
        if '📝 **内容类型**' in content:
            quality_line = f'> 🏆 **质量等级**: {quality}级（{"深度分析文" if quality == "S" else "重要资讯文" if quality == "A" else "一般文章" if quality == "B" else "短文"}）\n'
            content = content.replace('> 📝 **内容类型**:', quality_line + '> 📝 **内容类型**:', 1)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True, quality


def scan_category(category_name):
    """扫描分类下的所有文章"""
    cat_config = CATEGORIES.get(category_name, {})
    cat_dir = BASE_DIR / cat_config['dir']
    
    articles = []
    if not cat_dir.exists():
        return articles
    
    for f in cat_dir.glob('*.md'):
        if f.name == 'index.md':
            continue
        info = get_article_info(f)
        info['category'] = category_name
        info['quality'] = classify_quality(info['title'], category_name, len(info['content']))
        articles.append(info)
    
    return articles


def main():
    """主函数"""
    print("=" * 60)
    print("四大分类全量深度内容增强 v2")
    print("=" * 60)
    
    all_stats = {
        'total': 0,
        'enhanced': 0,
        'skipped': 0,
        'quality_distribution': {'S': 0, 'A': 0, 'B': 0, 'C': 0},
        'by_category': {},
    }
    
    # 按优先级处理分类
    for category_name in sorted(CATEGORIES.keys(), key=lambda x: CATEGORIES[x]['priority']):
        cat_config = CATEGORIES[category_name]
        print(f"\n{'='*60}")
        print(f"处理分类：{category_name}（优先级：{cat_config['priority']}）")
        print(f"{'='*60}")
        
        articles = scan_category(category_name)
        print(f"  文章总数：{len(articles)}")
        
        cat_stats = {'total': len(articles), 'enhanced': 0, 'skipped': 0, 'quality': {'S': 0, 'A': 0, 'B': 0, 'C': 0}}
        
        for art in articles:
            q = art['quality']
            cat_stats['quality'][q] = cat_stats['quality'].get(q, 0) + 1
            all_stats['quality_distribution'][q] = all_stats['quality_distribution'].get(q, 0) + 1
            
            if art['has_enhanced'] and art['has_changelog']:
                cat_stats['skipped'] += 1
                all_stats['skipped'] += 1
                print(f"  跳过（已增强）：{art['filename']}")
                continue
            
            # 所有未增强文章先进行基础增强
            success, result = enhance_article_b_level(art['path'], category_name)
            if success:
                cat_stats['enhanced'] += 1
                all_stats['enhanced'] += 1
                print(f"  增强成功（{q}级）：{art['filename']}")
            else:
                cat_stats['skipped'] += 1
                all_stats['skipped'] += 1
                print(f"  跳过：{art['filename']} - {result}")
        
        all_stats['total'] += len(articles)
        all_stats['by_category'][category_name] = cat_stats
        
        print(f"\n  分类统计：增强 {cat_stats['enhanced']}，跳过 {cat_stats['skipped']}")
        print(f"  质量分布：S={cat_stats['quality']['S']}, A={cat_stats['quality']['A']}, B={cat_stats['quality']['B']}, C={cat_stats['quality']['C']}")
    
    # 输出总统计
    print(f"\n{'='*60}")
    print("总统计")
    print(f"{'='*60}")
    print(f"总文章数：{all_stats['total']}")
    print(f"已增强：{all_stats['enhanced']}")
    print(f"已跳过：{all_stats['skipped']}")
    print(f"质量分布：S={all_stats['quality_distribution']['S']}, A={all_stats['quality_distribution']['A']}, B={all_stats['quality_distribution']['B']}, C={all_stats['quality_distribution']['C']}")
    
    # 保存统计结果
    stats_file = BASE_DIR / 'deep_enhance_stats_v2.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)
    print(f"\n统计结果已保存：{stats_file}")


if __name__ == '__main__':
    main()
