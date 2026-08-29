#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描第四、第五梯队文章（需要质量提升的文章）- 更严格的评估标准
"""

import os
import re
import json
import yaml
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"h:\github\cowkb\discover\site")
DISCOVER_DIR = Path(r"h:\github\cowkb\discover")

CATEGORIES = [
    "AI与机器学习",
    "云计算",
    "产品与设计",
    "人文社会",
    "其他",
    "数据库与存储",
    "知识管理",
    "系统与运维",
    "编程与开发",
    "行业动态",
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


def extract_quick_summary(body):
    """提取快速导读部分"""
    summary_data = {
        "has_summary": False,
        "core_points": [],
        "key_data": [],
        "target_audience": "",
        "read_time": "",
        "difficulty": "",
    }
    
    # 查找快速导读部分
    summary_pattern = r'##[ \t]*📋[ \t]*快速导读(.*?)(?=\n##[ \t]|$)'
    match = re.search(summary_pattern, body, re.DOTALL)
    if not match:
        return summary_data
    
    summary_data["has_summary"] = True
    summary_section = match.group(1)
    
    # 提取核心要点
    points_match = re.search(r'###[ \t]*核心要点(.*?)(?=\n###[ \t]|$)', summary_section, re.DOTALL)
    if points_match:
        points_text = points_match.group(1)
        points = re.findall(r'^[-*]\s+(.+)$', points_text, re.MULTILINE)
        summary_data["core_points"] = [p.strip() for p in points]
    
    # 提取关键数据
    data_match = re.search(r'###[ \t]*关键数据(.*?)(?=\n###[ \t]|$)', summary_section, re.DOTALL)
    if data_match:
        data_text = data_match.group(1)
        data_items = re.findall(r'^[-*]\s+(.+)$', data_text, re.MULTILINE)
        summary_data["key_data"] = [d.strip() for d in data_items]
    
    # 提取适合人群
    audience_match = re.search(r'👥[ \t]*适合人群[：:]\s*(.+)', summary_section)
    if audience_match:
        summary_data["target_audience"] = audience_match.group(1).strip()
    
    # 提取阅读时长
    time_match = re.search(r'⏱️[ \t]*阅读时长[：:]\s*(.+)', summary_section)
    if time_match:
        summary_data["read_time"] = time_match.group(1).strip()
    
    # 提取难度等级
    diff_match = re.search(r'🏷️[ \t]*难度等级[：:]\s*(.+)', summary_section)
    if diff_match:
        summary_data["difficulty"] = diff_match.group(1).strip()
    
    return summary_data


def check_summary_quality(summary_data, body, title):
    """检查快速导读质量"""
    issues = []
    
    # 1. 检查是否使用了通用模板要点（完全相同的话术）
    templated_points = [
        "规模化落地：2026年AI从技术验证转向生产级应用，企业关注ROI而非单纯的技术炫技",
        "效率优先：从参数规模竞赛转向推理效率、成本优化和场景适配，小模型与端侧推理快速发展",
        "Agent崛起：智能体成为新范式，大模型从聊天工具进化为任务执行者，自主完成复杂工作流",
    ]
    
    exact_match_count = 0
    for point in summary_data["core_points"]:
        for tp in templated_points:
            if point == tp or point.startswith(tp[:20]):
                exact_match_count += 1
                break
    
    if exact_match_count >= 2:
        issues.append(f"核心要点完全模板化（{exact_match_count}条通用模板）")
    
    # 2. 检查关键数据质量
    bad_data_count = 0
    for data_item in summary_data["key_data"]:
        # 去除表情符号
        clean_data = re.sub(r'[📊📈📉💹]', '', data_item).strip()
        
        # 检查是否是有效数据
        is_valid = False
        
        # 包含数字+单位/描述
        if re.search(r'\d+', clean_data):
            # 排除纯数字、只有百分比、不完整数据
            if re.match(r'^\d+[%％]?[）)]?$', clean_data):
                pass  # 无效
            elif re.match(r'^\d+$', clean_data):
                pass  # 无效
            elif len(clean_data) > 5:  # 有描述文字
                is_valid = True
        
        if not is_valid:
            bad_data_count += 1
    
    if bad_data_count > 0:
        issues.append(f"关键数据质量差（{bad_data_count}条无效/乱填）")
    
    # 3. 检查核心要点数量
    if len(summary_data["core_points"]) < 3:
        issues.append(f"核心要点不足（仅{len(summary_data['core_points'])}条）")
    
    # 4. 检查关键数据数量
    if len(summary_data["key_data"]) < 3:
        issues.append(f"关键数据不足（仅{len(summary_data['key_data'])}条）")
    
    return issues, exact_match_count, bad_data_count


def count_tables(body):
    """统计表格数量（完整的markdown表格）"""
    # 匹配表头+分隔行的表格
    table_pattern = r'^\|.*\|\n\|[-:\s|]+\|\n'
    tables = re.findall(table_pattern, body, re.MULTILINE)
    return len(tables)


def count_sections(body):
    """统计二级章节数量"""
    sections = re.findall(r'^##\s+', body, re.MULTILINE)
    return len(sections)


def check_content_substance(body):
    """检查内容充实度"""
    # 检查是否有实质性章节
    substantive_sections = 0
    section_pattern = r'##\s+(.+?)\n(.*?)(?=\n##\s+|\n###\s+|$)'
    
    for match in re.finditer(section_pattern, body, re.DOTALL):
        section_title = match.group(1)
        section_content = match.group(2).strip()
        
        # 跳过导读、目录等
        skip_keywords = ["快速导读", "核心要点", "目录", "索引", "changelog", "更新日志"]
        if any(kw in section_title for kw in skip_keywords):
            continue
        
        # 检查内容长度
        if len(section_content) > 200:
            substantive_sections += 1
    
    return substantive_sections


def check_structure_completeness(body):
    """检查结构完整性（8大模块）"""
    structure_keywords = {
        "背景与意义": ["背景", "意义", "概述", "引言"],
        "现状与格局": ["现状", "格局", "市场", "行业", "全景"],
        "核心技术/模式": ["核心技术", "技术原理", "架构", "模式", "解析"],
        "对比分析": ["对比", "比较", "选型", "差异"],
        "应用场景与案例": ["应用场景", "案例", "实践", "落地"],
        "挑战与风险": ["挑战", "风险", "问题", "困境"],
        "趋势与展望": ["趋势", "展望", "未来", "预测"],
        "建议与行动": ["建议", "指南", "策略", "行动"],
    }
    
    found_sections = []
    for section_name, keywords in structure_keywords.items():
        for kw in keywords:
            if kw in body:
                found_sections.append(section_name)
                break
    
    return found_sections


def assess_article(filepath, category):
    """评估单篇文章质量"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except:
        return None
    
    fm, body = parse_frontmatter(content)
    content_len = len(content)
    
    # 提取快速导读
    summary_data = extract_quick_summary(body)
    
    # 检查快速导读质量
    summary_issues, templated_count, bad_data_count = check_summary_quality(summary_data, body, fm.get("title", ""))
    
    # 统计表格
    table_count = count_tables(body)
    
    # 统计章节
    section_count = count_sections(body)
    
    # 实质性章节数
    substantive_sections = check_content_substance(body)
    
    # 结构完整性
    structure_sections = check_structure_completeness(body)
    
    # 计算质量得分（越低越需要提升，满分100）
    score = 100
    
    # 快速导读问题扣分（权重最高，因为这是用户最关注的）
    if not summary_data["has_summary"]:
        score -= 25
    else:
        score -= templated_count * 8  # 每条模板化扣8分
        score -= bad_data_count * 8  # 每条坏数据扣8分
        if len(summary_data["core_points"]) < 3:
            score -= 10
        if len(summary_data["key_data"]) < 3:
            score -= 10
    
    # 内容充实度扣分
    if content_len < 3000:
        score -= 20
    elif content_len < 5000:
        score -= 10
    elif content_len < 7000:
        score -= 5
    
    # 实质性章节扣分
    if substantive_sections < 3:
        score -= 15
    elif substantive_sections < 5:
        score -= 8
    
    # 表格数量扣分
    if table_count == 0:
        score -= 12
    elif table_count == 1:
        score -= 5
    
    # 结构完整性扣分
    if len(structure_sections) < 3:
        score -= 12
    elif len(structure_sections) < 5:
        score -= 6
    
    # 确定梯队
    if score >= 85:
        tier = "第一梯队（优质）"
    elif score >= 70:
        tier = "第二梯队（良好）"
    elif score >= 55:
        tier = "第三梯队（一般）"
    elif score >= 40:
        tier = "第四梯队（待提升）"
    else:
        tier = "第五梯队（需重点提升）"
    
    return {
        "title": fm.get("title", filepath.stem),
        "path": str(filepath),
        "category": category,
        "content_len": content_len,
        "score": score,
        "tier": tier,
        "table_count": table_count,
        "section_count": section_count,
        "substantive_sections": substantive_sections,
        "structure_sections": structure_sections,
        "has_summary": summary_data["has_summary"],
        "core_points_count": len(summary_data["core_points"]),
        "key_data_count": len(summary_data["key_data"]),
        "templated_count": templated_count,
        "bad_data_count": bad_data_count,
        "summary_issues": summary_issues,
    }


def main():
    all_articles = []
    category_stats = defaultdict(lambda: {"total": 0, "tiers": defaultdict(int)})
    
    for category in CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue
        
        for md_file in cat_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue
            
            result = assess_article(md_file, category)
            if result:
                all_articles.append(result)
                category_stats[category]["total"] += 1
                category_stats[category]["tiers"][result["tier"]] += 1
    
    # 按得分排序（从低到高）
    all_articles.sort(key=lambda x: x["score"])
    
    # 输出梯队统计
    print("=" * 80)
    print("文章梯队分布统计")
    print("=" * 80)
    for category in CATEGORIES:
        if category not in category_stats:
            continue
        stats = category_stats[category]
        print(f"\n【{category}】共 {stats['total']} 篇")
        for tier in ["第一梯队（优质）", "第二梯队（良好）", "第三梯队（一般）", "第四梯队（待提升）", "第五梯队（需重点提升）"]:
            count = stats["tiers"].get(tier, 0)
            if count > 0:
                print(f"  {tier}: {count} 篇")
    
    # 输出第四、第五梯队文章列表
    forth_fifth = [a for a in all_articles if "第四梯队" in a["tier"] or "第五梯队" in a["tier"]]
    print("\n" + "=" * 80)
    print(f"第四、第五梯队文章（共 {len(forth_fifth)} 篇）")
    print("=" * 80)
    
    for i, article in enumerate(forth_fifth[:60], 1):
        print(f"\n{i}. [{article['category']}] {article['title']}")
        print(f"   梯队: {article['tier']} | 得分: {article['score']} | 字数: {article['content_len']}")
        print(f"   表格: {article['table_count']} 个 | 实质章节: {article['substantive_sections']} 个")
        print(f"   模板化要点: {article['templated_count']} 条 | 坏数据: {article['bad_data_count']} 条")
        if article["summary_issues"]:
            print(f"   问题: {'; '.join(article['summary_issues'])}")
    
    # 保存结果
    output = {
        "total": len(all_articles),
        "forth_fifth_count": len(forth_fifth),
        "category_stats": {k: dict(v["tiers"]) for k, v in category_stats.items()},
        "forth_fifth_articles": forth_fifth,
        "all_articles_sorted": all_articles[:100],  # 保存前100篇
    }
    
    output_file = BASE_DIR / "forth_fifth_tier_scan.json"
    output_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n扫描结果已保存到: {output_file}")
    
    # 按类别选取推荐增强的文章（共40篇）
    print("\n" + "=" * 80)
    print("推荐优先增强的40篇文章（按类别均衡分布）")
    print("=" * 80)
    
    selected = []
    category_selected = defaultdict(list)
    
    # 优先从第四、第五梯队选
    for article in forth_fifth:
        cat = article["category"]
        if len(category_selected[cat]) < 5 and len(selected) < 45:
            selected.append(article)
            category_selected[cat].append(article)
    
    # 如果不够，从第三梯队补充
    if len(selected) < 40:
        third_tier = [a for a in all_articles if "第三梯队" in a["tier"]]
        for article in third_tier:
            cat = article["category"]
            if len(category_selected[cat]) < 5 and len(selected) < 45:
                selected.append(article)
                category_selected[cat].append(article)
    
    for cat in CATEGORIES:
        if cat in category_selected and category_selected[cat]:
            articles = category_selected[cat]
            print(f"\n【{cat}】{len(articles)} 篇:")
            for a in articles:
                print(f"  - {a['title']} (得分: {a['score']}, 字数: {a['content_len']})")
    
    print(f"\n共选择 {len(selected)} 篇文章进行增强")
    
    # 保存选中的文章列表
    selected_output = BASE_DIR / "selected_for_enhancement.json"
    selected_output.write_text(json.dumps([
        {"title": a["title"], "path": a["path"], "category": a["category"], "score": a["score"]}
        for a in selected
    ], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"选中文章列表已保存到: {selected_output}")


if __name__ == "__main__":
    main()
