#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量文章质量扫描与分类脚本
功能：
1. 扫描所有文章的字数、结构完整性
2. 按类型分类（深度报告/产品技术/新闻资讯）
3. 评估质量等级（S/A/B/C）
4. 生成分类清单和质量报告
"""

import os
import re
import json
import yaml
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

ALL_CATEGORIES = [
    "AI与机器学习", "系统与运维", "编程与开发", "数据库与存储",
    "云计算", "知识管理", "产品与设计", "人文社会", "行业动态", "其他",
]

# 深度报告/分析文章关键词
DEPTH_REPORT_KEYWORDS = [
    "全景", "深度", "解析", "报告", "指南", "趋势", "格局", "研报",
    "白皮书", "蓝皮书", "洞察", "分析", "研究", "全面", "完整",
    "选型", "对比", "评测", "市场", "产业", "行业", "战略",
    "发展历程", "技术路线", "商业化", "落地", "应用全景",
]

# 产品/技术介绍文章关键词
PRODUCT_TECH_KEYWORDS = [
    "发布", "推出", "上线", "版本", "更新", "升级", "新功能",
    "产品", "技术", "平台", "工具", "框架", "模型", "系统",
    "公司", "企业", "融资", "收购", "合作", "战略",
    "教程", "指南", "使用", "实践", "搭建", "部署", "配置",
    "详解", "原理", "架构", "设计", "实现",
]

# 新闻资讯/动态类关键词
NEWS_KEYWORDS = [
    "日报", "周报", "月报", "汇总", "动态", "新闻", "资讯",
    "快讯", "速递", "早报", "晚报", "晨报",
    "会议", "大会", "峰会", "论坛", "展会",
    "裁员", "融资", "上市", "财报", "业绩",
    "事件", "事故", "宕机", "漏洞", "安全",
    "今日", "昨日", "本周", "本月",
]


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


def classify_article(title, body, content_len):
    """
    分类文章类型
    返回: 'depth_report' | 'product_tech' | 'news'
    """
    title_lower = title.lower()
    text = title + " " + body[:500]
    
    depth_score = 0
    product_score = 0
    news_score = 0
    
    for kw in DEPTH_REPORT_KEYWORDS:
        if kw in text:
            depth_score += 2 if kw in title else 1
    
    for kw in PRODUCT_TECH_KEYWORDS:
        if kw in text:
            product_score += 2 if kw in title else 1
    
    for kw in NEWS_KEYWORDS:
        if kw in text:
            news_score += 3 if kw in title else 1
    
    # 字数权重
    if content_len > 4000:
        depth_score += 3
    elif content_len > 2500:
        depth_score += 1
        product_score += 1
    elif content_len < 1500:
        news_score += 2
    
    scores = {
        'depth_report': depth_score,
        'product_tech': product_score,
        'news': news_score,
    }
    
    return max(scores, key=scores.get), scores


def assess_quality(content_len, sections, has_summary, has_knowledge_enhance, article_type, body=""):
    """
    评估文章质量等级
    返回: 'S' | 'A' | 'B' | 'C'
    """
    score = 0
    
    # 字数得分（最高30分）
    if content_len >= 4000:
        score += 30
    elif content_len >= 3000:
        score += 25
    elif content_len >= 2500:
        score += 20
    elif content_len >= 2000:
        score += 15
    elif content_len >= 1500:
        score += 10
    elif content_len >= 1000:
        score += 5
    else:
        score += 0
    
    # 结构完整性（最高30分）
    section_set = set(sections)
    important_sections = [
        "核心要点", "背景与上下文", "深度解读", "最新进展",
        "相关素材", "延伸阅读", "参考来源", "案例补充",
        "技术原理", "行业影响", "实践指南", "风险与挑战"
    ]
    section_count = sum(1 for s in important_sections if s in section_set)
    score += min(section_count * 3, 30)
    
    # 摘要完整性（最高15分）
    if has_summary:
        score += 15
    
    # 知识增强（最高15分）
    if has_knowledge_enhance:
        score += 15
    
    # 表格数量（最高10分）
    table_count = len(re.findall(r'\|.*?\|.*?\|', body[:5000]))
    if table_count >= 5:
        score += 10
    elif table_count >= 3:
        score += 7
    elif table_count >= 1:
        score += 4
    
    # 类型加权
    if article_type == 'depth_report':
        if score >= 75:
            grade = 'S'
        elif score >= 55:
            grade = 'A'
        elif score >= 35:
            grade = 'B'
        else:
            grade = 'C'
    elif article_type == 'product_tech':
        if score >= 70:
            grade = 'S'
        elif score >= 50:
            grade = 'A'
        elif score >= 30:
            grade = 'B'
        else:
            grade = 'C'
    else:  # news
        if score >= 65:
            grade = 'S'
        elif score >= 45:
            grade = 'A'
        elif score >= 25:
            grade = 'B'
        else:
            grade = 'C'
    
    return grade, score


def extract_sections(body):
    """提取所有二级标题"""
    sections = []
    pattern = r'^##\s+(.+?)\s*$'
    for match in re.finditer(pattern, body, re.MULTILINE):
        title = match.group(1).strip()
        title = re.sub(r'^[^\w\u4e00-\u9fa5]+', '', title)
        sections.append(title)
    return sections


def has_quick_summary(body):
    """检查是否有快速导读/结构化摘要"""
    patterns = [
        r'##\s*[📋🎯]?\s*快速导读',
        r'##\s*[📋🎯]?\s*执行摘要',
        r'##\s*[📋🎯]?\s*内容摘要',
        r'###\s*核心要点',
        r'###\s*关键数据',
        r'###\s*阅读建议',
    ]
    for p in patterns:
        if re.search(p, body):
            return True
    return False


def has_knowledge_enhancement(body):
    """检查是否有文尾知识增强"""
    patterns = [
        r'##\s*[🔗📚]?\s*知识关联',
        r'##\s*[🔗📚]?\s*相关知识点',
        r'###\s*延伸阅读',
        r'###\s*关键词标签',
        r'###\s*内容评级',
        r'重要性[:：].*/5',
    ]
    for p in patterns:
        if re.search(p, body):
            return True
    return False


def main():
    results = {
        'total': 0,
        'quality_distribution': {'S': 0, 'A': 0, 'B': 0, 'C': 0},
        'type_distribution': {'depth_report': 0, 'product_tech': 0, 'news': 0},
        'category_stats': {},
        'articles': [],
        'b_articles': [],
        'c_articles': [],
        'a_articles': [],
        's_articles': [],
    }
    
    for category in ALL_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue
        
        cat_stats = {
            'count': 0,
            'quality': {'S': 0, 'A': 0, 'B': 0, 'C': 0},
            'type': {'depth_report': 0, 'product_tech': 0, 'news': 0},
            'avg_len': 0,
            'total_len': 0,
            'has_summary': 0,
            'has_knowledge': 0,
        }
        
        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            
            try:
                content = md_file.read_text(encoding="utf-8")
            except:
                continue
            
            fm, body = parse_frontmatter(content)
            content_len = len(body)
            sections = extract_sections(body)
            article_type, type_scores = classify_article(md_file.stem, body, content_len)
            has_summary = has_quick_summary(body)
            has_knowledge = has_knowledge_enhancement(body)
            grade, score = assess_quality(content_len, sections, has_summary, has_knowledge, article_type, body)
            
            article_info = {
                'title': md_file.stem,
                'path': str(md_file),
                'category': category,
                'content_len': content_len,
                'sections': sections,
                'section_count': len(sections),
                'article_type': article_type,
                'type_scores': type_scores,
                'quality': grade,
                'quality_score': score,
                'has_summary': has_summary,
                'has_knowledge': has_knowledge,
                'table_count': len(re.findall(r'\|.*?\|.*?\|', body)),
            }
            
            results['total'] += 1
            results['quality_distribution'][grade] += 1
            results['type_distribution'][article_type] += 1
            results['articles'].append(article_info)
            
            cat_stats['count'] += 1
            cat_stats['quality'][grade] += 1
            cat_stats['type'][article_type] += 1
            cat_stats['total_len'] += content_len
            if has_summary:
                cat_stats['has_summary'] += 1
            if has_knowledge:
                cat_stats['has_knowledge'] += 1
            
            if grade == 'S':
                results['s_articles'].append(article_info)
            elif grade == 'A':
                results['a_articles'].append(article_info)
            elif grade == 'B':
                results['b_articles'].append(article_info)
            else:
                results['c_articles'].append(article_info)
        
        if cat_stats['count'] > 0:
            cat_stats['avg_len'] = int(cat_stats['total_len'] / cat_stats['count'])
        results['category_stats'][category] = cat_stats
    
    # 按类别输出统计
    print("=" * 80)
    print("全量文章质量扫描与分类报告")
    print("=" * 80)
    print(f"\n📊 总文章数: {results['total']}")
    
    print(f"\n🏆 质量分布:")
    for grade in ['S', 'A', 'B', 'C']:
        count = results['quality_distribution'][grade]
        pct = count / results['total'] * 100 if results['total'] > 0 else 0
        print(f"  {grade}级: {count} 篇 ({pct:.1f}%)")
    
    print(f"\n📝 类型分布:")
    type_names = {'depth_report': '深度报告/分析', 'product_tech': '产品/技术介绍', 'news': '新闻资讯/动态'}
    for t, name in type_names.items():
        count = results['type_distribution'][t]
        pct = count / results['total'] * 100 if results['total'] > 0 else 0
        print(f"  {name}: {count} 篇 ({pct:.1f}%)")
    
    print(f"\n📁 分类详情:")
    for cat in ALL_CATEGORIES:
        if cat not in results['category_stats']:
            continue
        cs = results['category_stats'][cat]
        print(f"\n  【{cat}】({cs['count']}篇)")
        print(f"    平均字数: {cs['avg_len']}")
        print(f"    质量: S={cs['quality']['S']} A={cs['quality']['A']} B={cs['quality']['B']} C={cs['quality']['C']}")
        print(f"    类型: 深度={cs['type']['depth_report']} 产品技术={cs['type']['product_tech']} 资讯={cs['type']['news']}")
        print(f"    有摘要: {cs['has_summary']}  有知识增强: {cs['has_knowledge']}")
    
    print(f"\n⚠️  B级文章 ({len(results['b_articles'])}篇):")
    for a in results['b_articles'][:20]:
        print(f"  - [{a['category']}] {a['title']} ({a['content_len']}字)")
    if len(results['b_articles']) > 20:
        print(f"  ... 还有 {len(results['b_articles']) - 20} 篇")
    
    print(f"\n❌ C级文章 ({len(results['c_articles'])}篇):")
    for a in results['c_articles'][:20]:
        print(f"  - [{a['category']}] {a['title']} ({a['content_len']}字)")
    if len(results['c_articles']) > 20:
        print(f"  ... 还有 {len(results['c_articles']) - 20} 篇")
    
    # 保存结果
    output_file = BASE_DIR / 'quality_scan_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 详细结果已保存到: {output_file}")
    
    return results


if __name__ == "__main__":
    main()
