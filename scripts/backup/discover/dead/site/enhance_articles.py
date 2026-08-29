#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章质量提升脚本
功能：
1. 添加元数据头部
2. 提炼核心要点
3. 添加延伸阅读
4. 去重检测
5. 更新分类索引（精选文章、质量分级）
"""

import os
import re
import yaml
import random
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

# 重点分类
KEY_CATEGORIES = {
    "AI与机器学习": 10,
    "云计算": 5,
    "系统与运维": 10,
    "编程与开发": 10,
    "行业动态": 10,
}

# 内容类型判断关键词
CONTENT_TYPE_KEYWORDS = {
    "资讯文章": ["日报", "周报", "月报", "动态", "新闻", "融资", "发布", "会议", "峰会", "大会", "报道", "资讯", "裁员", "市场"],
    "技术分析": ["解析", "深度", "技术", "原理", "架构", "对比", "分析", "指南", "教程", "实践", "详解", "源码", "算法"],
    "产品评测": ["评测", "对比", "选型", "推荐", "测评", "横评", "工具", "插件", "产品"],
    "行业报告": ["报告", "研报", "榜单", "全景", "格局", "趋势", "分析", "白皮书", "蓝皮书", "市场"],
}


def parse_frontmatter(content):
    """解析frontmatter"""
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


def extract_original_link(body):
    """提取原文链接"""
    pattern = r'原文[：:]\s*\[([^\]]+)\]\(([^)]+)\)'
    match = re.search(pattern, body)
    if match:
        return match.group(2), match.group(1)
    return None, None


def determine_content_type(title, body):
    """判断内容类型"""
    text = title + body
    scores = {}
    for ctype, keywords in CONTENT_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[ctype] = score
    
    max_score = max(scores.values()) if scores else 0
    if max_score == 0:
        return "资讯文章"
    
    for ctype, score in scores.items():
        if score == max_score:
            return ctype
    return "资讯文章"


def calculate_star_rating(title, body, fm):
    """计算素材价值星级 (1-5星)"""
    score = 0
    
    # 内容长度
    content_len = len(body)
    if content_len > 5000:
        score += 2
    elif content_len > 2000:
        score += 1.5
    elif content_len > 1000:
        score += 1
    else:
        score += 0.5
    
    # 结构完整性（有多少个二级标题）
    h2_count = len(re.findall(r'^## ', body, re.MULTILINE))
    if h2_count >= 5:
        score += 1.5
    elif h2_count >= 3:
        score += 1
    elif h2_count >= 2:
        score += 0.5
    
    # 信息密度（列表项数量）
    list_count = len(re.findall(r'^[-*] ', body, re.MULTILINE))
    if list_count >= 15:
        score += 1
    elif list_count >= 8:
        score += 0.5
    
    # 是否有代码块
    if re.search(r'```', body):
        score += 0.5
    
    # 时效性（标题含年份的加分）
    if re.search(r'202[456]', title):
        score += 0.5
    
    # 转换为星级（满分5星）
    max_score = 5.5
    stars = min(5, max(1, round(score / max_score * 5)))
    return stars


def extract_key_points(body, min_points=2, max_points=5):
    """从文章中提取核心要点"""
    points = []
    
    # 移除frontmatter和基本信息表格后的内容
    content_start = body.find("## 内容")
    if content_start > 0:
        content = body[content_start:]
    else:
        content = body
    
    # 方法1: 提取加粗的小标题（带emoji的）
    emoji_pattern = r'[\U0001F300-\U0001F9FF\u2600-\u2B55\u2300-\u23FF]\s*\*\*([^*]+)\*\*'
    emoji_matches = re.findall(emoji_pattern, content)
    for m in emoji_matches:
        m = m.strip()
        if len(m) > 5 and len(m) < 50 and m not in points:
            points.append(m)
    
    # 方法2: 提取列表中的第一项（加粗的）
    bold_list_pattern = r'[-*]\s*\*\*([^*]+)\*\*'
    bold_matches = re.findall(bold_list_pattern, content)
    for m in bold_matches:
        m = m.strip().rstrip("：:")
        if len(m) > 5 and len(m) < 50 and m not in points:
            points.append(m)
    
    # 方法3: 提取二级标题
    h2_pattern = r'^##\s+(.+)$'
    h2_matches = re.findall(h2_pattern, content, re.MULTILINE)
    for m in h2_matches:
        m = m.strip()
        if m not in ["基本信息", "内容", "核心要点", "延伸阅读"] and m not in points:
            points.append(m)
    
    # 方法4: 提取带数字编号的标题
    num_pattern = r'^[一二三四五六七八九十\d]+[、.]\s*\*\*([^*]+)\*\*'
    num_matches = re.findall(num_pattern, content, re.MULTILINE)
    for m in num_matches:
        m = m.strip().rstrip("：:")
        if len(m) > 5 and len(m) < 50 and m not in points:
            points.append(m)
    
    # 如果不够，提取重要句子
    if len(points) < min_points:
        # 提取包含"核心"、"主要"、"关键"等词的句子
        important_pattern = r'[^。！？\n]*(核心|主要|关键|重要|重点)[^。！？\n]*[。！？]'
        imp_matches = re.findall(important_pattern, content)
        for m in imp_matches:
            if m not in points:
                points.append(m)
                if len(points) >= min_points:
                    break
    
    # 限制数量
    points = points[:max_points]
    
    # 如果还是不够，用默认的
    if len(points) < min_points:
        default_points = [
            "文章介绍了相关领域的重要信息",
            "包含有价值的行业动态和技术见解",
        ]
        for p in default_points:
            if len(points) < min_points:
                points.append(p)
    
    return points[:max_points]


def build_metadata_block(fm, original_link, content_type, stars):
    """构建元数据引用块"""
    created_at = fm.get("created_at", "未知")
    if not isinstance(created_at, str):
        created_at = str(created_at)
    lines = ["> 📅 **发布时间**: " + created_at]
    
    categories = fm.get("categories", "")
    if isinstance(categories, list):
        categories = ", ".join(categories)
    lines.append(f"> 🏷️ **分类**: {categories}")
    
    if original_link:
        lines.append(f"> 🔗 **原文链接**: {original_link}")
    
    lines.append(f"> 📝 **内容类型**: {content_type}")
    lines.append(f"> ⭐ **素材价值**: {'⭐' * stars}（可提炼为知识卡片）")
    
    return "\n" + "\n".join(lines) + "\n"


def build_key_points_block(points):
    """构建核心要点区块"""
    block = "\n## 💡 核心要点\n\n"
    for p in points:
        block += f"- {p}\n"
    return block + "\n"


def build_reading_more_block(category, current_file, all_files_in_category):
    """构建延伸阅读区块"""
    block = "\n## 📚 延伸阅读\n\n"
    
    # 选择同分类的其他文章
    other_files = [f for f in all_files_in_category if f != current_file]
    random.shuffle(other_files)
    selected = other_files[:2]
    
    for f in selected:
        # 从文件名提取标题
        title = f.stem
        block += f"- [{title}]({f.name})\n"
    
    block += f"\n[← 返回分类索引](index.md)\n"
    return block


def find_duplicate_articles(all_articles):
    """检测重复文章"""
    duplicates = []
    articles_list = list(all_articles.items())
    
    for i in range(len(articles_list)):
        path1, info1 = articles_list[i]
        for j in range(i + 1, len(articles_list)):
            path2, info2 = articles_list[j]
            
            # 同一分类才比较
            if info1["category"] != info2["category"]:
                continue
            
            # 标题相似度
            title_sim = SequenceMatcher(None, info1["title"], info2["title"]).ratio()
            
            # 内容相似度（取前1000字符）
            content1 = info1["body"][:1000]
            content2 = info2["body"][:1000]
            content_sim = SequenceMatcher(None, content1, content2).ratio()
            
            # 如果标题或内容高度相似
            if title_sim > 0.7 or content_sim > 0.6:
                duplicates.append((path1, path2, title_sim, content_sim))
    
    return duplicates


def get_article_quality_score(title, body, fm, stars):
    """计算文章质量评分（用于排序和精选）"""
    score = 0
    
    # 星级权重
    score += stars * 10
    
    # 内容长度
    content_len = len(body)
    if content_len > 5000:
        score += 20
    elif content_len > 3000:
        score += 15
    elif content_len > 2000:
        score += 10
    elif content_len > 1000:
        score += 5
    
    # 结构完整性
    h2_count = len(re.findall(r'^## ', body, re.MULTILINE))
    score += min(h2_count * 2, 10)
    
    # 时效性（越新越好）
    created_at = fm.get("created_at", "")
    if "2025" in str(created_at):
        score += 5
    if "2026" in str(created_at):
        score += 8
    
    return score


def process_all_articles():
    """处理所有文章"""
    print("=" * 60)
    print("开始文章质量提升处理")
    print("=" * 60)
    
    # 收集所有文章信息
    all_articles = {}  # path -> {title, body, fm, category, dir_path}
    category_articles = defaultdict(list)  # category -> [file paths]
    
    # 遍历所有子目录
    for item in BASE_DIR.iterdir():
        if not item.is_dir():
            continue
        
        category = item.name
        if category.startswith("."):
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
                }
                category_articles[category].append(md_file)
            except Exception as e:
                print(f"读取失败 {md_file}: {e}")
    
    print(f"\n共发现 {len(all_articles)} 篇文章")
    print(f"分类数量: {len(category_articles)}")
    
    # 检测重复
    print("\n正在检测重复文章...")
    duplicates = find_duplicate_articles(all_articles)
    print(f"发现 {len(duplicates)} 对重复/相似文章")
    for p1, p2, ts, cs in duplicates:
        print(f"  - {p1.name} <-> {p2.name} (标题相似: {ts:.2f}, 内容相似: {cs:.2f})")
    
    # 处理每篇文章
    stats = {
        "total": len(all_articles),
        "with_metadata": 0,
        "with_key_points": 0,
        "with_reading_more": 0,
        "duplicates_marked": 0,
    }
    
    print("\n正在处理文章...")
    for idx, (file_path, info) in enumerate(all_articles.items(), 1):
        if idx % 50 == 0:
            print(f"  进度: {idx}/{len(all_articles)}")
        
        try:
            content = info["content"]
            fm = info["fm"]
            body = info["body"]
            category = info["category"]
            
            # 提取原文链接
            original_link, _ = extract_original_link(body)
            
            # 判断内容类型
            content_type = determine_content_type(info["title"], body)
            
            # 计算星级
            stars = calculate_star_rating(info["title"], body, fm)
            
            # 提取核心要点
            key_points = extract_key_points(body)
            
            # 检查是否已经处理过（有核心要点就跳过）
            if "## 💡 核心要点" in content:
                continue
            
            # 构建元数据块 - 插入到H1标题之后
            metadata_block = build_metadata_block(fm, original_link, content_type, stars)
            
            # 构建核心要点块
            key_points_block = build_key_points_block(key_points)
            
            # 构建延伸阅读块
            reading_more_block = build_reading_more_block(
                category, file_path, category_articles[category]
            )
            
            # 检查是否是重复文章
            duplicate_note = ""
            for p1, p2, _, _ in duplicates:
                if file_path == p1:
                    other_name = p2.name
                    duplicate_note = f'\n> 🔄 **注意**: 本文与 [{other_name}]({other_name}) 内容高度相似，建议对照阅读。\n'
                    stats["duplicates_marked"] += 1
                    break
                elif file_path == p2:
                    other_name = p1.name
                    duplicate_note = f'\n> 🔄 **注意**: 本文与 [{other_name}]({other_name}) 内容高度相似，建议对照阅读。\n'
                    stats["duplicates_marked"] += 1
                    break
            
            # 组装新内容
            fm_text = content.split("---")[1] if content.startswith("---") else ""
            
            # 找到H1标题的位置
            h1_match = re.search(r'^# .+$', content, re.MULTILINE)
            if not h1_match:
                continue
            
            h1_end = h1_match.end()
            
            # 找到正文开始位置（跳过基本信息表格）
            content_section = content.find("## 内容")
            if content_section == -1:
                content_section = h1_end
            
            # 组装
            new_content = content[:h1_end]  # frontmatter + H1
            new_content += metadata_block  # 元数据
            
            # 重复提示（如果有）
            if duplicate_note:
                new_content += duplicate_note
            
            # 核心要点
            new_content += key_points_block
            
            # 正文部分（从## 内容开始）
            # 找到原来的内容部分起始
            content_start = content.find("## 内容")
            if content_start > 0:
                new_content += content[content_start:]
            else:
                new_content += content[h1_end:]
            
            # 在末尾添加延伸阅读（在"本文由Wiki系统自动生成"之前）
            auto_gen_marker = "*本文由Wiki系统自动生成*"
            if auto_gen_marker in new_content:
                new_content = new_content.replace(
                    auto_gen_marker,
                    reading_more_block + "\n---\n\n" + auto_gen_marker
                )
            else:
                new_content += reading_more_block
            
            # 写入文件
            file_path.write_text(new_content, encoding="utf-8")
            
            stats["with_metadata"] += 1
            stats["with_key_points"] += 1
            stats["with_reading_more"] += 1
            
        except Exception as e:
            print(f"处理失败 {file_path.name}: {e}")
    
    print(f"\n文章处理完成!")
    print(f"  - 添加元数据: {stats['with_metadata']} 篇")
    print(f"  - 添加核心要点: {stats['with_key_points']} 篇")
    print(f"  - 添加延伸阅读: {stats['with_reading_more']} 篇")
    print(f"  - 标记重复: {stats['duplicates_marked']} 篇")
    
    # 更新分类索引
    print("\n正在更新分类索引...")
    feature_count = update_category_indexes(all_articles, category_articles, duplicates)
    
    # 输出最终统计
    print("\n" + "=" * 60)
    print("处理完成统计")
    print("=" * 60)
    print(f"处理文章总数: {stats['total']}")
    print(f"添加元数据: {stats['with_metadata']}")
    print(f"添加核心要点: {stats['with_key_points']}")
    print(f"添加延伸阅读: {stats['with_reading_more']}")
    print(f"发现重复文章对: {len(duplicates)}")
    print(f"标记重复文章: {stats['duplicates_marked']}")
    print(f"精选文章总数: {feature_count}")
    
    return stats, duplicates


def update_category_indexes(all_articles, category_articles, duplicates):
    """更新分类索引"""
    total_featured = 0
    
    for category, files in category_articles.items():
        index_path = BASE_DIR / category / "index.md"
        if not index_path.exists():
            continue
        
        try:
            index_content = index_path.read_text(encoding="utf-8")
            
            # 计算每篇文章的质量分和星级
            articles_info = []
            for f in files:
                if f in all_articles:
                    info = all_articles[f]
                    stars = calculate_star_rating(info["title"], info["body"], info["fm"])
                    quality_score = get_article_quality_score(
                        info["title"], info["body"], info["fm"], stars
                    )
                    articles_info.append({
                        "path": f,
                        "title": info["title"],
                        "stars": stars,
                        "quality_score": quality_score,
                    })
            
            # 按质量分排序
            articles_info.sort(key=lambda x: x["quality_score"], reverse=True)
            
            # 解析原有表格 - 保留原始行的简要说明
            # 通过标题匹配来建立映射
            desc_map = {}  # title -> desc
            lines = index_content.split("\n")
            in_table = False
            for line in lines:
                if line.startswith("| 序号 |"):
                    in_table = True
                    continue
                if in_table and line.startswith("|") and ".md" in line:
                    parts = [p.strip() for p in line.split("|")]
                    # parts[0] is empty (before first |), parts[1] is 序号, parts[2] is 标题, parts[3] is 说明
                    if len(parts) >= 4:
                        title_col = parts[2]
                        desc_col = parts[3]
                        # 从标题列提取显示文本
                        title_match = re.search(r'\[([^\]]+)\]', title_col)
                        if title_match:
                            title_text = title_match.group(1)
                            desc_map[title_text] = desc_col
            
            # 构建新的文章清单表格
            new_table = "## 文章清单\n\n"
            new_table += f"共 **{len(files)}** 篇文章\n\n"
            new_table += "| 序号 | 质量 | 文章标题 | 简要说明 |\n"
            new_table += "|:----:|:----:|:---------|:---------|\n"
            
            for idx, art in enumerate(articles_info, 1):
                fname = art["path"].name
                # URL编码文件名
                from urllib.parse import quote
                encoded_name = quote(fname)
                
                title_display = art["title"]
                stars_display = "⭐" * art["stars"]
                
                # 尝试通过标题匹配找简要说明
                desc = desc_map.get(title_display, "")
                # 如果没找到，尝试模糊匹配
                if not desc:
                    for t, d in desc_map.items():
                        if t and title_display and (t in title_display or title_display in t):
                            desc = d
                            break
                
                new_table += f"| {idx} | {stars_display} | [{title_display}]({encoded_name}) | {desc} |\n"
            
            # 精选文章（仅重点分类）
            featured_block = ""
            if category in KEY_CATEGORIES:
                n_featured = KEY_CATEGORIES[category]
                featured = articles_info[:n_featured]
                total_featured += len(featured)
                
                featured_block = f"\n## 🌟 精选文章\n\n"
                featured_block += f"精选 {len(featured)} 篇高质量文章，优先阅读：\n\n"
                for idx, art in enumerate(featured, 1):
                    fname = art["path"].name
                    from urllib.parse import quote
                    encoded_name = quote(fname)
                    stars_display = "⭐" * art["stars"]
                    featured_block += f"{idx}. [{art['title']}]({encoded_name}) {stars_display}\n"
                featured_block += "\n"
            
            # 找到上层入口的位置
            upper_entry = index_content.find("## 上层入口")
            if upper_entry == -1:
                upper_entry = len(index_content)
            
            # 组装新内容
            # 保留前面的分类说明
            desc_end = index_content.find("## 文章清单")
            if desc_end == -1:
                continue
            
            new_index = index_content[:desc_end]
            new_index += new_table
            new_index += featured_block
            new_index += "\n" + index_content[upper_entry:]
            
            index_path.write_text(new_index, encoding="utf-8")
            print(f"  - 更新 {category}/index.md")
            
        except Exception as e:
            print(f"更新索引失败 {category}: {e}")
    
    return total_featured


if __name__ == "__main__":
    process_all_articles()
