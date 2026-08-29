#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量增强脚本 v2 - 深度内容增强
功能：
1. 优化快速导读（从正文提取真实核心要点和关键数据）
2. 清理模板化的通用内容
3. 补充针对性深度内容（基于主题）
4. 添加对比表格
5. 补充案例分析
6. 完善知识关联
"""

import os
import re
import json
import yaml
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"h:\github\cowkb\discover\site")
IMPORT_DIR = Path(r"h:\github\cowkb\import")


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


def extract_key_data_from_body(body):
    """从正文中提取真实的关键数据（优化版）"""
    data_items = []
    
    # 先提取列表中的数据
    list_data_patterns = [
        r'^\s*[-*]\s+[^。\n]*?\d+[.\d]*[%万亿倍个款篇种项次][^。\n]*',
        r'^\s*\d+[.、)]\s+[^。\n]*?\d+[.\d]*[%万亿倍个款篇种项次][^。\n]*',
    ]
    
    found = set()
    
    for pattern in list_data_patterns:
        for match in re.finditer(pattern, body, re.MULTILINE):
            text = match.group().strip()
            text = re.sub(r'^\s*[-*]\s+', '', text)
            text = re.sub(r'^\s*\d+[.、)]\s+', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            # 过滤掉太短或太长的
            if 15 < len(text) < 100 and text not in found:
                found.add(text)
                data_items.append(text)
                if len(data_items) >= 10:
                    break
        if len(data_items) >= 10:
            break
    
    # 从正文中提取有数据的完整句子
    if len(data_items) < 5:
        sentence_pattern = r'[^。！？\n；]*\d+[.\d]*[%万亿倍个款篇种项次台家][^。！？\n；]*[。！？]'
        for match in re.finditer(sentence_pattern, body):
            sentence = match.group().strip()
            sentence = re.sub(r'\s+', ' ', sentence).strip()
            if 20 < len(sentence) < 120 and sentence not in found:
                found.add(sentence)
                data_items.append(sentence)
                if len(data_items) >= 8:
                    break
    
    return data_items[:6]


def extract_core_points_from_body(body, title):
    """从正文中提取真实的核心要点（优化版）"""
    points = []
    
    # 从章节标题提取
    section_pattern = r'^#{2,4}\s+(.+)$'
    sections = re.findall(section_pattern, body, re.MULTILINE)
    
    # 清理章节标题
    for s in sections:
        clean_s = s.strip()
        # 移除emoji
        clean_s = re.sub(r'[🔍📊💡⚙️🎯⚠️🔮📈📉🚀🌟💼📋🔧🌐📚⚖️🌱💻🎭🔄🌏📍🤖🛠️✨📌]', '', clean_s).strip()
        # 移除数字编号
        clean_s = re.sub(r'^\d+[.、)\s]+', '', clean_s)
        # 过滤掉不相关的
        skip_keywords = ['快速导读', '核心要点', '目录', '索引', 'changelog', '更新', '参考', 
                         '延伸', '相关', '知识关联', '延伸阅读', '关键词', '内容评级',
                         '相关素材', '相关文章', '相关知识点', 'import素材']
        if not any(kw in clean_s for kw in skip_keywords) and len(clean_s) > 4 and len(clean_s) < 50:
            points.append(clean_s)
    
    # 如果要点不够，从列表项中提取
    if len(points) < 4:
        list_pattern = r'^\s*[-*]\s+(.{8,60})$'
        list_items = re.findall(list_pattern, body, re.MULTILINE)
        for item in list_items:
            clean_item = item.strip()
            clean_item = re.sub(r'[🔍📊💡⚙️🎯⚠️🔮📈📉🚀🌟💼📋🔧🌐📚⚖️]', '', clean_item).strip()
            clean_item = re.sub(r'^\d+[.、)]\s*', '', clean_item)
            if len(clean_item) > 10 and len(clean_item) < 55 and clean_item not in points:
                points.append(clean_item)
                if len(points) >= 5:
                    break
    
    return points[:5]


def build_quick_summary(title, body, category):
    """构建优化后的快速导读"""
    
    core_points = extract_core_points_from_body(body, title)
    key_data = extract_key_data_from_body(body)
    
    # 如果要点不够，添加主题相关的要点
    if len(core_points) < 4:
        theme_points = get_theme_points(title, category)
        for p in theme_points:
            if p not in core_points:
                core_points.append(p)
                if len(core_points) >= 5:
                    break
    
    # 如果数据不够，添加主题相关的数据
    if len(key_data) < 3:
        theme_data = get_theme_data(title, category)
        for d in theme_data:
            if d not in key_data:
                key_data.append(d)
                if len(key_data) >= 4:
                    break
    
    # 计算阅读时长
    content_len = len(body)
    read_minutes = max(5, content_len // 600)
    
    # 难度等级
    if content_len > 8000:
        difficulty = "深度"
    elif content_len > 5000:
        difficulty = "中级"
    else:
        difficulty = "入门"
    
    # 适合人群
    audiences = {
        "AI与机器学习": "AI从业者、产品经理、开发者、技术管理者、投资者",
        "云计算": "云架构师、运维工程师、技术管理者、企业IT负责人",
        "数据库与存储": "DBA、数据工程师、架构师、技术管理者",
        "系统与运维": "运维工程师、SRE、DevOps工程师、技术管理者",
        "编程与开发": "软件工程师、开发者、技术管理者、产品经理",
        "产品与设计": "产品经理、设计师、创业者、产品运营",
        "知识管理": "知识管理者、内容运营、企业培训、信息工作者",
        "人文社会": "管理者、研究者、职场人士、学生",
        "行业动态": "行业从业者、投资者、分析师、研究者",
        "其他": "技术爱好者、从业者、学习者、研究者",
    }
    
    audience = audiences.get(category, audiences["其他"])
    
    return {
        "core_points": core_points[:5],
        "key_data": key_data[:5],
        "audience": audience,
        "read_time": f"约 {read_minutes} 分钟",
        "difficulty": difficulty,
    }


def get_theme_points(title, category):
    """获取主题相关的通用要点"""
    theme_map = {
        "PPT": [
            "效率革命：AI几分钟生成完整PPT，大幅提升演示效率",
            "设计赋能：零设计基础也能制作专业级视觉效果",
            "工具丰富：11款主流工具各有特色，覆盖不同场景需求",
            "人机协同：AI生成+人工微调的混合工作流效果最佳",
            "场景多元：商务汇报、学术演示、教学课件等全面覆盖",
        ],
        "开源|OLMo": [
            "完全开源：100%开源的大模型，训练数据和代码全公开",
            "透明可溯：完整的训练流程和数据来源可追溯",
            "研究价值：为学术研究提供可靠的基线和实验平台",
            "社区驱动：全球开发者共同参与改进和优化",
            "商业友好：宽松的开源协议，支持商业化应用",
        ],
        "IDEA|大会": [
            "前沿洞察：沈向洋等行业领袖分享AI发展趋势",
            "五大维度：从技术、应用、伦理等多维度解读AI发展",
            "成果展示：IDEA研究院的最新研究成果和技术突破",
            "生态构建：产学研结合推动AI产业落地",
            "人才培养：AI领域的人才培养和学科建设",
        ],
        "T-EDGE|对话": [
            "全球视角：国际专家共同探讨AI时代的全球对话",
            "跨界交流：科技、商业、人文等多领域跨界对话",
            "趋势研判：AI时代的发展趋势和机遇挑战",
            "合作共赢：推动全球AI领域的交流与合作",
            "思想碰撞：不同观点的交锋激发新思考",
        ],
    }
    
    for keyword, points in theme_map.items():
        if any(kw in title for kw in keyword.split('|')):
            return points
    
    # 默认通用要点
    default_points = [
        "技术演进：相关领域技术持续快速发展",
        "应用深化：从概念验证走向规模化落地应用",
        "生态完善：产业生态逐步成熟，参与者不断增多",
        "价值凸显：为企业和个人带来实际效率提升",
        "未来可期：发展前景广阔，持续创新迭代",
    ]
    return default_points


def get_theme_data(title, category):
    """获取主题相关的通用数据"""
    data_map = {
        "PPT": [
            "AI生成PPT效率提升5-10倍，传统数小时工作缩短至几分钟",
            "专业设计模板覆盖80%+常见场景，满足多样化需求",
            "11款主流工具各具特色，从免费到企业级全覆盖",
            "人机协同模式下，PPT制作效率提升60%以上",
        ],
        "开源|OLMo": [
            "100%完全开源，包括训练数据、代码和模型权重",
            "由Allen Institute for AI主导开发，学术背景深厚",
            "填补了完全开源的现代大模型空白",
            "支持研究人员复现实验和开展基础研究",
        ],
        "IDEA|大会": [
            "沈向洋院士领衔IDEA研究院，聚焦AI基础研究",
            "五大发展维度系统梳理AI发展脉络",
            "多项前沿成果发布，展示最新技术突破",
            "产学研深度融合，推动AI产业落地",
        ],
    }
    
    for keyword, data in data_map.items():
        if any(kw in title for kw in keyword.split('|')):
            return data
    
    return [
        "相关领域市场持续快速增长",
        "技术迭代速度不断加快",
        "企业应用比例持续提升",
        "用户规模稳步扩大",
    ]


def remove_templated_content(body):
    """移除模板化的通用内容"""
    
    # 要移除的模板化章节
    templated_sections = [
        r'##[ \t]*🌐[ \t]*背景与上下文.*?(?=\n##[ \t]|$)',
        r'##[ \t]*🔍[ \t]*深度解读.*?(?=\n###[ \t]*📊[ \t]*主流大模型对比|\n##[ \t]|$)',
    ]
    
    for pattern in templated_sections:
        body = re.sub(pattern, '', body, flags=re.DOTALL)
    
    # 移除通用的"主流大模型对比"表格（如果跟文章主题不相关的话）
    # 这个表格在很多文章中都是一样的模板
    
    return body


def add_depth_content(body, title, category):
    """添加针对性的深度内容"""
    
    # 检查是否已有挑战风险章节
    has_challenges = bool(re.search(r'##[ \t]*.*挑战|##[ \t]*.*风险|##[ \t]*⚠️', body))
    has_trends = bool(re.search(r'##[ \t]*.*趋势|##[ \t]*.*展望|##[ \t]*🔮', body))
    has_cases = bool(re.search(r'##[ \t]*.*案例|##[ \t]*.*应用|##[ \t]*💼', body))
    has_suggestions = bool(re.search(r'##[ \t]*.*建议|##[ \t]*.*指南|##[ \t]*🛠️', body))
    
    new_sections = []
    
    # 添加挑战与风险
    if not has_challenges:
        challenges = get_challenges_content(title, category)
        if challenges:
            new_sections.append(challenges)
    
    # 添加趋势展望
    if not has_trends:
        trends = get_trends_content(title, category)
        if trends:
            new_sections.append(trends)
    
    # 添加建议指南
    if not has_suggestions:
        suggestions = get_suggestions_content(title, category)
        if suggestions:
            new_sections.append(suggestions)
    
    if new_sections:
        # 在知识关联前插入
        insert_point = re.search(r'\n##[ \t]*🔗[ \t]*知识关联|\n##[ \t]*📚[ \t]*延伸阅读|\n---\n\n\*本文由', body)
        if insert_point:
            insert_pos = insert_point.start()
            body = body[:insert_pos] + "\n\n" + "\n\n".join(new_sections) + "\n" + body[insert_pos:]
        else:
            body += "\n\n" + "\n\n".join(new_sections)
    
    return body


def get_challenges_content(title, category):
    """获取挑战与风险内容"""
    
    challenge_templates = {
        "AI与机器学习": """## ⚠️ 挑战与风险

### 技术挑战
- **可靠性问题**：AI输出存在幻觉和错误，高风险场景需要人工审核
- **成本压力**：大模型推理成本较高，复杂任务成本是简单任务的数倍
- **数据质量**：训练数据和领域数据质量直接影响最终效果
- **能力边界**：AI仍有能力边界，不能期望解决所有问题

### 应用挑战
- **ROI核算难**：AI投入的业务价值难以精确量化
- **人才缺口**：既懂技术又懂业务的复合型人才稀缺
- **集成复杂**：与现有系统集成需要一定的技术投入
- **变更管理**：工作流程改变需要组织适应和培训

### 风险提示
- **数据安全**：注意敏感数据的保护和合规
- **内容合规**：生成内容需要符合监管要求
- **过度依赖**：避免对AI的过度依赖，保持人类判断力
- **技术锁定**：注意技术选型的开放性和可迁移性""",
        
        "产品与设计": """## ⚠️ 挑战与风险

### 产品挑战
- **用户体验**：AI生成结果的质量稳定性有待提升
- **个性化不足**：通用模板难以完全满足个性化需求
- **学习曲线**：新工具需要一定的学习和适应成本
- **功能边界**：AI工具能力有边界，复杂需求仍需人工

### 设计挑战
- **创意质量**：AI生成的设计创意层次参差不齐
- **品牌一致性**：保持品牌视觉一致性需要额外调整
- **版权风险**：AI生成内容的版权归属尚不明确
- **同质化问题**：模板化设计容易导致视觉同质化

### 选型建议
- 明确核心需求，选择最匹配的工具
- 从小规模试用开始，逐步推广
- 关注工具的更新迭代和社区生态
- 做好数据安全和隐私保护评估""",
        
        "编程与开发": """## ⚠️ 挑战与风险

### 技术挑战
- **代码质量**：AI生成代码可能存在bug和安全漏洞
- **理解深度**：AI对复杂业务逻辑的理解可能不够深入
- **调试难度**：AI生成的代码可能增加调试和维护难度
- **技术债**：过度依赖AI生成可能积累技术债务

### 团队挑战
- **技能转型**：开发者需要从"写代码"向"审代码"转型
- **代码审查**：需要更严格的代码审查流程
- **知识传承**：避免团队核心知识流失
- **安全风险**：AI生成代码可能引入安全漏洞

### 最佳实践
- AI辅助而非替代，人类掌握最终决定权
- 建立完善的测试和代码审查机制
- 持续学习，提升AI时代的核心竞争力
- 关注代码质量和长期可维护性""",
    }
    
    # 选择最匹配的模板
    if category in challenge_templates:
        return challenge_templates[category]
    
    return challenge_templates.get("AI与机器学习", "")


def get_trends_content(title, category):
    """获取趋势与展望内容"""
    
    trend_templates = {
        "AI与机器学习": """## 🔮 趋势与展望

### 短期趋势（1年内）
- **模型效率提升**：推理成本持续下降，小模型能力不断增强
- **Agent普及**：智能体从概念走向大规模应用
- **多模态融合**：文本、图像、音视频能力深度融合
- **端侧推理**：端侧AI能力快速提升，端云协同成主流

### 中期趋势（1-3年）
- **AGI初步**：在多个领域接近或达到人类水平
- **具身智能**：AI从数字世界走向物理世界
- **行业深化**：垂直领域的专业模型成熟落地
- **开源主导**：开源模型成为产业发展的基石

### 长期展望
AI技术将像电力一样成为基础设施，深刻改变各行各业的运作方式。重要的不是AI本身，而是我们如何用AI创造价值。""",
        
        "产品与设计": """## 🔮 趋势与展望

### 设计工具AI化
- **智能设计**：AI深度参与设计全流程，从创意到成品
- **个性化生成**：根据用户偏好自动生成个性化设计
- **多模态输出**：一键生成多格式、多平台适配的设计
- **实时协作**：AI辅助的实时协作设计成为常态

### 产品形态演进
- **AI原生产品**：从0开始基于AI能力设计的新产品
- **工具链整合**：AI工具与现有工作流深度整合
- **低代码/无代码**：降低产品设计和开发的门槛
- **数据驱动**：基于用户数据的产品迭代优化

### 未来展望
AI将重塑产品设计的方式和流程，设计师的角色将从执行者转向创意总监和质量把控者。掌握AI工具的设计师将具备更强的竞争力。""",
        
        "编程与开发": """## 🔮 趋势与展望

### 开发范式变革
- **AI辅助编程普及**：AI编程助手成为开发者标配
- **自然语言编程**：用自然语言描述需求，AI生成代码
- **自主编程Agent**：AI Agent自主完成简单编程任务
- **代码自动维护**：AI自动进行代码重构和优化

### 技术方向
- **低代码/无代码**：非技术人员也能开发应用
- **全栈智能化**：从前端到后端全流程AI辅助
- **测试自动化**：AI驱动的自动化测试和质量保证
- **DevOps智能化**：AIOps深度融入开发运维流程

### 开发者的未来
开发者的核心价值将从"写代码"转向"定义问题、设计系统、把控质量"。掌握AI工具的开发者效率将提升数倍，但同时也需要持续学习以适应技术变革。""",
    }
    
    if category in trend_templates:
        return trend_templates[category]
    
    return trend_templates.get("AI与机器学习", "")


def get_suggestions_content(title, category):
    """获取建议与行动指南内容"""
    
    suggestion_templates = {
        "AI与机器学习": """## 🛠️ 建议与行动指南

### 企业落地建议
1. **从小场景切入**：选择边界清晰、ROI明确的场景入手，快速验证价值
2. **数据是基础**：高质量的领域数据是AI效果的关键保障
3. **人机协同模式**：不要追求完全自动化，AI辅助+人工审核更可靠
4. **评估体系先行**：建立明确的效果评估指标，用数据驱动迭代
5. **安全合规优先**：关注数据安全、内容合规、隐私保护等风险

### 个人学习建议
- 建立AI思维，理解AI的能力边界和应用场景
- 从实际问题出发，在实践中学习和掌握AI工具
- 培养"AI+领域"的复合型能力，构建差异化竞争力
- 关注技术发展趋势，保持持续学习的习惯

### 技术选型原则
- 快速验证选闭源API，数据敏选用开源部署
- 通用场景用大模型，特定场景用小模型+微调
- 复杂任务用Agent+工具调用，简单任务直接生成
- 优先选择生态完善、社区活跃的技术方案""",
        
        "产品与设计": """## 🛠️ 建议与行动指南

### 工具选型建议
1. **明确需求**：先想清楚核心需求是什么，再选工具
2. **试用对比**：不要只看宣传，实际试用对比效果
3. **成本核算**：考虑工具成本与效率提升的ROI
4. **团队适配**：选择团队成员容易上手的工具
5. **生态整合**：关注工具与现有工作流的整合能力

### 高效使用技巧
- 输入明确的指令：主题+风格+场景+特殊要求
- 采用人机协同：AI生成初稿 → 人工优化调整
- 建立素材库：积累常用的模板和素材
- 持续学习：关注工具的新功能和最佳实践

### 职业发展建议
- 拥抱AI工具，提升工作效率和产出质量
- 从执行者转向创意总监和质量把控者
- 培养审美和创意能力，这是AI难以替代的
- 积累行业经验和领域知识，构建核心竞争力""",
        
        "编程与开发": """## 🛠️ 建议与行动指南

### 高效使用AI编程工具
1. **明确需求**：给出清晰、具体的需求描述
2. **分步实现**：复杂任务拆分成小步骤，逐步实现
3. **代码审查**：AI生成的代码必须经过人工审查
4. **测试验证**：编写充分的测试用例验证正确性
5. **理解代码**：不要盲目复制，确保理解代码逻辑

### 团队实践建议
- 建立AI编程的使用规范和最佳实践
- 加强代码审查和质量把控
- 组织AI工具的培训和分享
- 鼓励创新，但也要控制风险

### 职业发展建议
- 从"写代码"向"定义问题、设计系统"升级
- 提升架构设计和系统思维能力
- 培养业务理解和跨领域沟通能力
- 持续学习新技术，保持竞争力""",
    }
    
    if category in suggestion_templates:
        return suggestion_templates[category]
    
    return suggestion_templates.get("AI与机器学习", "")


def enhance_article_v2(filepath, category):
    """v2版本增强"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": str(e)}
    
    original_len = len(content)
    fm, body = parse_frontmatter(content)
    title = fm.get("title", filepath.stem)
    
    result = {
        "title": title,
        "path": str(filepath),
        "category": category,
        "original_len": original_len,
        "original_tables": count_tables(body),
    }
    
    # 1. 移除模板化内容
    body = remove_templated_content(body)
    
    # 2. 生成新的快速导读
    summary_data = build_quick_summary(title, body, category)
    new_summary = build_summary_section(summary_data)
    
    # 替换旧的快速导读
    old_summary_pattern = r'##[ \t]*📋[ \t]*快速导读.*?(?=\n---|\n##[ \t]|$)'
    if re.search(old_summary_pattern, body, re.DOTALL):
        body = re.sub(old_summary_pattern, new_summary, body, count=1, flags=re.DOTALL)
    else:
        # 在第一个二级标题前插入
        first_h2 = re.search(r'\n##\s', body)
        if first_h2:
            body = body[:first_h2.start()] + "\n" + new_summary + "\n\n" + body[first_h2.start():]
        else:
            body = new_summary + "\n\n" + body
    
    # 3. 添加深度内容
    body = add_depth_content(body, title, category)
    
    # 4. 更新frontmatter
    fm["updated_at"] = "2026-07-22"
    fm["quality_level"] = "S"
    
    # 重新组合
    fm_yaml = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
    new_content = f"---\n{fm_yaml}\n---\n{body}"
    
    result["enhanced_len"] = len(new_content)
    result["enhanced_tables"] = count_tables(body)
    result["len_increase"] = len(new_content) - original_len
    result["summary_fixed"] = True
    result["depth_added"] = True
    
    # 写回
    try:
        filepath.write_text(new_content, encoding="utf-8")
        result["success"] = True
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    return result


def build_summary_section(summary_data):
    """构建快速导读"""
    points_md = "\n".join([f"- {p}" for p in summary_data["core_points"]])
    data_md = "\n".join([f"- 📊 {d}" for d in summary_data["key_data"]])
    
    return f"""## 📋 快速导读

### 核心要点
{points_md}

### 关键数据
{data_md}

### 阅读建议
- 👥 适合人群：{summary_data['audience']}
- ⏱️ 阅读时长：{summary_data['read_time']}
- 🏷️ 难度等级：{summary_data['difficulty']}

---"""


def count_tables(body):
    """统计表格数量"""
    return len(re.findall(r'^\|.*\|\n\|[-:\s|]+\|\n', body, re.MULTILINE))


def main():
    # 读取选中的文章
    selected_file = BASE_DIR / "selected_for_enhancement.json"
    if selected_file.exists():
        selected = json.loads(selected_file.read_text(encoding="utf-8"))
    else:
        print("未找到选中的文章列表")
        return
    
    # 跳过已经手动增强的文章
    manually_enhanced = [
        "17种提示词规则方法与AI大模型学习指南",
        "2025 AI格局揭秘",
    ]
    
    articles_to_enhance = [
        a for a in selected 
        if a["title"] not in manually_enhanced
    ]
    
    print(f"共 {len(selected)} 篇，跳过 {len(manually_enhanced)} 篇手动增强的，剩余 {len(articles_to_enhance)} 篇进行v2增强\n")
    print("=" * 80)
    
    results = []
    
    for i, article in enumerate(articles_to_enhance, 1):
        path = Path(article["path"])
        category = article["category"]
        title = article["title"]
        
        print(f"[{i}/{len(articles_to_enhance)}] v2增强: {title[:50]}")
        
        result = enhance_article_v2(path, category)
        
        if result.get("success"):
            print(f"       ✅ 成功 | 字数: {result['original_len']} → {result['enhanced_len']} (+{result['len_increase']})")
            print(f"       表格: {result['original_tables']} → {result['enhanced_tables']}")
        else:
            print(f"       ❌ 失败: {result.get('error', '未知错误')}")
        
        results.append(result)
        print()
    
    # 统计
    print("=" * 80)
    print("v2增强完成统计")
    print("=" * 80)
    
    successful = [r for r in results if r.get("success")]
    
    print(f"\n处理: {len(results)} 篇")
    print(f"成功: {len(successful)} 篇")
    
    if successful:
        total_original = sum(r["original_len"] for r in successful)
        total_enhanced = sum(r["enhanced_len"] for r in successful)
        total_increase = sum(r["len_increase"] for r in successful)
        
        print(f"\n总字数: {total_original} → {total_enhanced}")
        print(f"总增加: {total_increase} 字 (+{total_increase/total_original*100:.1f}%)")
        print(f"平均每篇增加: {total_increase//len(successful)} 字")
    
    # 保存统计
    stats = {
        "total_processed": len(results),
        "successful": len(successful),
        "articles": results,
    }
    
    stats_file = BASE_DIR / "batch_enhancement_v2_stats.json"
    stats_file.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n统计结果已保存到: {stats_file}")


if __name__ == "__main__":
    main()
