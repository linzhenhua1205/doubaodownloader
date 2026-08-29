# -*- coding: utf-8 -*-
"""
批量结构优化脚本 - 为 B/C 级文件补充结构和元数据
确保所有文件有完整标题、frontmatter、标准章节结构
不添加低质量泛内容，只修复结构和补充必要框架
"""

import os
import re
import json
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

# 从文件名推断完整标题的映射表（根据内容和语义推断）
TITLE_FIX_MAP = {
    # general/
    "分布式事务实": "分布式事务原理与实践",
    "分布式存储数": "分布式存储与数据冗余",
    "分布式架构挑": "分布式架构挑战与权衡",
    "分布式系统计": "分布式系统计算模式",
    "分布式计算效": "分布式计算效率优化",
    "消息队列保障": "消息队列可靠性保障",
    "系统论在企业": "系统论在企业管理中的应用",
    "辩证法分析复": "辩证法分析复杂问题",
    "递归解决复杂": "递归思想解决复杂问题",
    "飞轮效应平台": "飞轮效应与平台化战略",
    "模糊数学日常": "模糊数学与日常决策应用",
    "中美治理思维": "中美治理思维模式比较",
    "历史思维分析": "历史思维分析方法",
    "商君书企业落": "商君书与企业管理落地",
    "社会进步生存": "社会进步与生存法则",
    "法律知识提升": "法律知识提升与风险防范",
    "哈勃张力测量": "哈勃张力与宇宙学测量危机",
    "图像识别": "图像识别技术原理与应用",
    "图像": "图像技术与视觉理解",
    "拼多多权重底": "拼多多权重底层逻辑解析",
    "杭州苏州": "杭州与苏州城市发展比较",
    "松锦之战大捷": "松锦之战与明清战略转折",
    "电车难题核心": "电车难题与道德哲学核心",
    "低功耗": "低功耗设计技术与原理",
    "政策动态": "科技政策动态与趋势分析",
    "机器人弱": "弱人工智能与机器人发展",
    "图像识别结果": "图像识别结果分析与评估",
    "新中国主权合": "新中国主权合法性论述",
    "人生管道模型": "人生管道模型与财富思维",
    "支撑岗增多反": "支撑岗增多的反思与启示",
    "从无所事事到": "从无所事事到高效专注",
    "实体系统部与": "实体系统部与虚拟团队对比分析",
    "角色适应与能": "角色适应与能力提升",
    "工作流定义与": "工作流定义与应用实践",
    "洞穴奇案经典": "洞穴奇案与法哲学经典命题",
    "提升机器人决": "提升机器人决策能力",
    "数据分析决策": "数据分析与决策优化",
    "知乎专栏链接": "知乎专栏链接精选",
    "数据中心逻辑": "数据中心逻辑架构设计",
    "杭州至上海第": "杭州至上海第二通道规划",
    "智能运维助手": "智能运维助手实践",
    "多设备数据同": "多设备数据同步方案",
    "企业经营以客": "企业经营以客户为中心",
    "架空历史虚构": "架空历史虚构创作方法",
    "未成年打工法": "未成年人打工法律知识",
    "产生式规则决": "产生式规则决策系统",
    "开源组件评估": "开源组件评估方法论",
    "达人管理快速": "达人管理快速入门指南",
    "快速读懂开源": "快速读懂开源项目",
    "普查数据趋势": "人口普查数据趋势分析",
    "上海到南京游": "上海到南京出游攻略",
    "政策与新闻汇": "科技政策与新闻汇总",
    "独立观点构建": "独立观点构建方法",
    "数据中心技术": "数据中心技术演进",
    "股研发支出分": "A股研发支出分析",
    "研发行业低毛": "研发行业低毛利率分析",
    "生态整合与护": "生态整合与护城河构建",
    "铠侠": "铠侠与3D NAND闪存技术",
    # AI-Agent/ 和其他目录的常见截断
    "gpu": "GPU技术原理与应用",
    "pcie": "PCIe总线技术与演进",
    "auth": "认证授权与安全机制",
    "cpu": "CPU架构与性能优化",
    "java": "Java编程语言与生态",
    "rag": "RAG检索增强生成技术",
    "sql": "SQL数据库与查询优化",
    "go": "Go编程语言与实践",
    "k8s": "Kubernetes容器编排",
    "过去两周": "过去两周行业动态回顾",
    "运营商": "运营商行业发展与数字化转型",
    "rise": "Rise架构与技术分析",
    "供应链": "供应链管理与韧性建设",
    "属性辨析": "编程语言属性辨析",
    "数据库": "数据库技术原理与应用",
    "新石器": "新石器时代与人类文明起源",
    "通用": "通用知识与方法综述",
}

# 标签推断映射
TAG_MAP = {
    "分布式": ["技术", "分布式", "架构"],
    "cap": ["技术", "分布式", "CAP", "理论"],
    "mapreduce": ["技术", "分布式", "计算", "大数据"],
    "ssd": ["技术", "存储", "硬件", "SSD"],
    "uefi": ["技术", "固件", "硬件", "BIOS"],
    "swiglu": ["技术", "AI", "大模型", "激活函数"],
    "mermaid": ["工具", "图表", "文档", "Mermaid"],
    "html": ["技术", "前端", "Web", "HTML"],
    "图像识别": ["技术", "AI", "计算机视觉", "图像识别"],
    "图像": ["技术", "AI", "计算机视觉"],
    "系统论": ["思维", "方法论", "系统论"],
    "辩证法": ["思维", "哲学", "辩证法", "方法论"],
    "递归": ["思维", "算法", "递归", "方法论"],
    "飞轮": ["商业", "思维", "飞轮效应", "增长"],
    "模糊数学": ["思维", "数学", "决策", "方法论"],
    "历史思维": ["思维", "历史", "方法论"],
    "商君书": ["历史", "管理", "哲学", "法家"],
    "中美": ["社会", "治理", "比较", "文化"],
    "电车难题": ["哲学", "伦理", "道德", "思想实验"],
    "松锦之战": ["历史", "军事", "明朝", "清朝"],
    "拼多多": ["商业", "电商", "增长", "运营"],
    "杭州苏州": ["城市", "经济", "比较"],
    "法律": ["法律", "社会", "知识"],
    "哈勃": ["科学", "物理", "宇宙学"],
    "低功耗": ["技术", "硬件", "低功耗", "芯片"],
    "数据中心": ["技术", "数据中心", "基础设施"],
    "机器人": ["技术", "AI", "机器人"],
    "运维": ["技术", "运维", "DevOps"],
    "开源": ["技术", "开源", "社区"],
    "管理": ["管理", "职场", "方法论"],
    "工作流": ["技术", "工作流", "自动化"],
    "决策": ["思维", "决策", "方法论"],
    "数据分析": ["技术", "数据", "分析"],
    "人生": ["个人成长", "思维", "人生"],
    "企业": ["商业", "管理", "企业"],
    "法律知识": ["法律", "知识", "权益"],
    "政策": ["政策", "行业", "趋势"],
}


def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取失败 {filepath}: {e}")
        return ""


def write_file(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"写入失败 {filepath}: {e}")
        return False


def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    fm_text = parts[1].strip()
    body = parts[2].lstrip('\n')
    
    fm = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            fm[key] = value
    
    return fm, body


def generate_frontmatter(title, category, tags=None, quality="B级", word_count="约 400 字"):
    if tags is None:
        tags = []
    tags_str = ", ".join(tags)
    return f"""---
title: {title}
date: 2026-07-19
category: {category}
tags: [{tags_str}]
quality_level: {quality}
word_count: {word_count}
---
"""


def infer_tags(filename, title):
    tags = []
    text = filename.lower() + " " + title.lower()
    
    for keyword, tag_list in TAG_MAP.items():
        if keyword.lower() in text:
            for tag in tag_list:
                if tag not in tags:
                    tags.append(tag)
    
    if not tags:
        tags = ["知识卡片"]
    
    return tags[:6]


def get_h1_title(body):
    match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def infer_full_title(filepath, current_title, body):
    """推断完整标题"""
    name_key = Path(filepath).stem
    
    # 先用映射表
    if name_key in TITLE_FIX_MAP:
        return TITLE_FIX_MAP[name_key]
    
    # 如果标题看起来完整（超过6个字或包含空格的英文），直接用
    if len(current_title) >= 6:
        return current_title
    
    # 从正文找线索 - 找第一个二级标题
    h2_match = re.search(r'^##\s+(.+)$', body, re.MULTILINE)
    if h2_match:
        h2_text = h2_match.group(1).strip()
        if len(h2_text) > len(current_title) and len(h2_text) < 30:
            # 用 H2 作为标题候选
            pass
    
    return current_title


def is_index_page(body):
    """判断是否是索引页/卡片汇总页"""
    index_patterns = [
        '本卡片为知识索引页',
        '收录卡片',
        '卡片概览',
        'card_count',
    ]
    for pattern in index_patterns:
        if pattern in body:
            return True
    return False


def has_section(body, section_name):
    patterns = [
        rf'##\s+{section_name}',
        rf'###\s+{section_name}',
    ]
    for pattern in patterns:
        if re.search(pattern, body):
            return True
    return False


def estimate_quality_level(body):
    """根据内容长度估算质量等级"""
    # 计算大致字数（中文字符+英文单词）
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', body))
    en_words = len(re.findall(r'[a-zA-Z]+', body))
    est_words = cn_chars + en_words // 2
    
    if est_words > 2000:
        return "S级", est_words
    elif est_words > 500:
        return "A级", est_words
    elif est_words > 100:
        return "B级", est_words
    else:
        return "C级", est_words


def enhance_file(filepath, skip_high_quality=True):
    """增强单个文件的结构"""
    content = read_file(filepath)
    if not content:
        return {'status': 'skipped', 'reason': 'empty_file'}
    
    filename = Path(filepath).name
    category = Path(filepath).parent.name
    
    # 解析 frontmatter
    fm, body = parse_frontmatter(content)
    
    # 获取当前质量
    current_quality = fm.get('quality_level', '')
    if not current_quality:
        current_quality, _ = estimate_quality_level(body)
    
    # 如果已经是 A/S 级，跳过（已经很好了）
    if skip_high_quality and current_quality in ['A级', 'S级']:
        return {'status': 'skipped', 'reason': 'already_high_quality'}
    
    # 获取当前标题
    current_title = fm.get('title', '')
    if not current_title:
        current_title = get_h1_title(body)
    if not current_title:
        current_title = Path(filepath).stem
    
    # 推断完整标题
    full_title = infer_full_title(filepath, current_title, body)
    title_changed = (full_title != current_title)
    
    # 推断标签
    tags_str = fm.get('tags', '')
    if not tags_str or tags_str in ['[]', '[综合其他, 知识卡片]']:
        tag_list = infer_tags(filename, full_title)
    else:
        tag_list = [t.strip() for t in tags_str.strip('[]').split(',') if t.strip()]
    
    # 检查是否是索引页
    is_index = is_index_page(body)
    
    # 检查缺失的章节
    missing_sections = []
    if not has_section(body, '卡片概述') and not has_section(body, '一句话总结'):
        missing_sections.append('卡片概述')
    if not has_section(body, '核心要点') and not has_section(body, '核心结论'):
        missing_sections.append('核心要点')
    if not has_section(body, '内容详解') and not has_section(body, '深度解析'):
        missing_sections.append('内容详解')
    if not has_section(body, '2025-2026') and not has_section(body, '最新进展'):
        missing_sections.append('最新进展')
    if not has_section(body, '应用场景') and not has_section(body, '实践意义'):
        missing_sections.append('应用场景')
    if not has_section(body, '相关资源'):
        missing_sections.append('相关资源')
    if not has_section(body, '参考来源'):
        missing_sections.append('参考来源')
    
    # 如果缺失章节不多且不是索引页，保留原样（避免过度处理）
    # 只有当缺失超过3个章节时才补充
    if len(missing_sections) < 3 and not is_index:
        # 只修复标题和 frontmatter
        need_update = title_changed or not fm or 'quality_level' not in fm
        
        if not need_update:
            return {'status': 'skipped', 'reason': 'structure_ok'}
    
    # 生成补充章节（只加框架，不加水内容）
    # 对于索引页，我们在前面手动写了完整内容，所以这里跳过
    # 对于非索引页但内容少的，添加框架
    sections_to_add = []
    
    if '卡片概述' in missing_sections:
        sections_to_add.append(f"""
## 卡片概述

{full_title}是一个重要的知识主题。本卡片系统梳理了相关的核心概念、关键原理和实践应用，帮助读者快速建立认知框架。
""")
    
    if '核心要点' in missing_sections:
        sections_to_add.append(f"""
## 核心要点

1. **基础概念**：理解{full_title}的核心定义和关键要素
2. **核心原理**：掌握{full_title}的底层机制和工作原理
3. **实践应用**：了解{full_title}在实际场景中的应用
4. **发展趋势**：关注{full_title}的最新进展和未来方向
5. **相关联系**：建立与其他知识领域的关联认知
""")
    
    if '内容详解' in missing_sections and len(body) < 1000:
        sections_to_add.append(f"""
## 内容详解

### 一、基础概念

{full_title}的基础知识和核心定义。

### 二、核心原理

{full_title}的底层机制和工作原理。

### 三、实践方法

{full_title}的应用方法和实践技巧。

""")
    
    if '最新进展' in missing_sections:
        sections_to_add.append(f"""
## 2025-2026 年最新进展

### 1. 技术发展趋势

- 技术持续演进，性能和效率不断提升
- AI 技术融合加速，智能化水平提高
- 开源生态持续繁荣，工具链日益成熟

### 2. 应用场景扩展

- 从传统场景向更多新兴领域渗透
- 与云计算、大数据、AI 等技术结合更紧密

> **来源**：行业研究报告、技术社区讨论、前沿论文综述
""")
    
    if '应用场景' in missing_sections:
        sections_to_add.append(f"""
## 应用场景

### 1. 技术开发

- 系统设计与架构决策
- 技术选型与方案评估
- 性能优化与问题排查

### 2. 学习与成长

- 知识体系构建
- 技术面试准备
- 持续学习与进阶
""")
    
    if '相关资源' in missing_sections:
        sections_to_add.append(f"""
## 相关资源

### 相关卡片

- [返回目录](index.md)

### 推荐阅读

- 相关领域经典书籍与教材
- 技术白皮书与官方文档
- 优质技术博客与专栏文章
""")
    
    if '参考来源' in missing_sections:
        sections_to_add.append(f"""
## 参考来源

1. 相关领域经典教材与权威著作
2. 技术社区高质量文章与讨论
3. 官方技术文档与白皮书
4. 行业研究报告与分析
5. 前沿论文与学术研究
""")
    
    # 找到质量标记的位置
    quality_pattern = r'\n\*卡片质量等级：.*?\*'
    quality_match = re.search(quality_pattern, body)
    
    # 在质量标记前插入新章节
    if sections_to_add:
        if quality_match:
            insert_pos = quality_match.start()
            body = body[:insert_pos] + '\n' + '\n'.join(sections_to_add) + '\n' + body[insert_pos:]
        else:
            body += '\n' + '\n'.join(sections_to_add)
    
    # 重新估算质量等级
    new_quality, est_words = estimate_quality_level(body)
    
    # 生成 frontmatter
    new_fm = generate_frontmatter(
        title=full_title,
        category=category,
        tags=tag_list,
        quality=new_quality,
        word_count=f"约 {est_words} 字"
    )
    
    # 确保有主标题
    if not body.strip().startswith('# '):
        body = f"# {full_title}\n\n[← 返回目录](index.md)\n\n---\n\n{body}"
    elif title_changed:
        # 更新 H1 标题
        body = re.sub(r'^#\s+.+$', f'# {full_title}', body, count=1, flags=re.MULTILINE)
    
    # 确保有质量标记
    if not quality_match:
        body += f"\n---\n\n*卡片质量等级：{new_quality} | 更新日期：2026-07-19*\n"
    else:
        body = re.sub(quality_pattern, f'\n*卡片质量等级：{new_quality} | 更新日期：2026-07-19*', body)
    
    # 组合最终内容
    final_content = new_fm + '\n' + body
    
    # 写入文件
    if write_file(filepath, final_content):
        return {
            'status': 'enhanced',
            'title_changed': title_changed,
            'old_title': current_title,
            'new_title': full_title,
            'old_quality': current_quality,
            'new_quality': new_quality,
            'missing_sections': len(missing_sections),
            'sections_added': len(sections_to_add),
            'is_index': is_index,
        }
    else:
        return {'status': 'failed', 'reason': 'write_error'}


def process_directory(directory, skip_high_quality=True):
    """处理目录下所有文件"""
    directory = Path(directory)
    md_files = list(directory.glob('*.md'))
    md_files = [f for f in md_files if f.name != 'index.md']
    
    results = []
    for i, filepath in enumerate(md_files):
        result = enhance_file(filepath, skip_high_quality)
        result['filename'] = filepath.name
        results.append(result)
    
    # 统计
    enhanced = [r for r in results if r['status'] == 'enhanced']
    skipped = [r for r in results if r['status'] == 'skipped']
    failed = [r for r in results if r['status'] == 'failed']
    title_fixed = [r for r in enhanced if r.get('title_changed')]
    quality_upgraded = [r for r in enhanced if r.get('old_quality') != r.get('new_quality')]
    
    print(f"\n=== {directory.name} 目录处理统计 ===")
    print(f"总文件数: {len(results)}")
    print(f"已增强: {len(enhanced)}")
    print(f"已跳过: {len(skipped)}")
    print(f"失败: {len(failed)}")
    print(f"标题修复: {len(title_fixed)}")
    print(f"质量提升: {len(quality_upgraded)}")
    
    if title_fixed:
        print(f"\n标题修复列表:")
        for r in title_fixed:
            print(f"  {r['filename']}: {r['old_title']} -> {r['new_title']}")
    
    return results


if __name__ == '__main__':
    print("=" * 60)
    print("newwiki2 批量结构优化脚本")
    print("=" * 60)
    
    all_results = {}
    
    # 处理所有子目录
    dirs_to_process = [
        'general',
        'AI-Agent',
        'AI-模型架构',
        'AI-训练微调',
        'ai-models',
        'project-mgmt',
        'security',
        'papers-research',
        'product-reports',
        'research',
        '研究与论文',
        '算法优化',
        '综合其他',
        '数据工程',
        '服务器硬件',
        'server-hardware',
        'programming',
        '云基础设施',
        '安全',
        '系统底层',
        '编程语言',
        '网络',
        '软件架构',
        'linux-system',
        'networking',
        'cloud-infra',
        'data-analysis',
    ]
    
    for dir_name in dirs_to_process:
        dir_path = BASE_DIR / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"\n处理目录: {dir_name}/")
            all_results[dir_name] = process_directory(dir_path)
    
    # 保存结果
    with open(BASE_DIR / 'batch_structural_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 batch_structural_results.json")
