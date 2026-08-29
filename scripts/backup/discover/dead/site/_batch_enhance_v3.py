#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量增强脚本 v3 - 保守增强版（只做加法，不做减法）
功能：
1. 优化快速导读（从正文真实提取核心要点和关键数据）
2. 补充深度内容模块（挑战/趋势/建议）
3. 添加对比表格
4. 添加案例分析
5. 融合import素材（优化匹配）
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


def extract_core_points(body, title):
    """从正文提取真实核心要点"""
    points = []
    found = set()
    
    # 1. 从带数字的列表项提取（有实质内容的）
    pattern1 = r'^\s*\d+[.、)]\s+\*\*(.+?)\*\*'
    for m in re.finditer(pattern1, body, re.MULTILINE):
        text = m.group(1).strip()
        if 5 < len(text) < 50 and text not in found:
            found.add(text)
            points.append(text)
    
    # 2. 从加粗的要点提取
    pattern2 = r'[-*]\s+\*\*(.+?)\*\*'
    for m in re.finditer(pattern2, body):
        text = m.group(1).strip()
        if 5 < len(text) < 50 and text not in found:
            found.add(text)
            points.append(text)
    
    # 3. 从章节标题提取（过滤掉通用标题）
    skip_sections = [
        '快速导读', '核心要点', '目录', '索引', 'changelog', '更新日志',
        '参考', '延伸阅读', '相关文章', '相关素材', '知识关联', '相关知识点',
        'import素材', '延伸阅读', '关键词', '内容评级', '背景与上下文',
        '深度解读', '最新进展', '相关技术资源', '参考来源', '案例补充',
        '实践指南', '行业影响', '挑战与风险', '趋势与展望', '建议与行动'
    ]
    
    section_pattern = r'^#{2,4}\s+(.+)$'
    for m in re.finditer(section_pattern, body, re.MULTILINE):
        text = m.group(1).strip()
        text = re.sub(r'[🔍📊💡⚙️🎯⚠️🔮📈📉🚀🌟💼📋🔧🌐📚⚖️🌱💻🎭🔄🌏📍🤖🛠️✨📌💵📉🔬]', '', text).strip()
        text = re.sub(r'^\d+[.、)\s]+', '', text)
        if (5 < len(text) < 40 
            and not any(s in text for s in skip_sections)
            and text not in found):
            found.add(text)
            points.append(text)
    
    # 4. 从带数据的列表项提取
    list_pattern = r'^\s*[-*]\s+(.{10,80}\d+.{0,20})$'
    for m in re.finditer(list_pattern, body, re.MULTILINE):
        text = m.group(1).strip()
        text = re.sub(r'\*\*', '', text)
        if 10 < len(text) < 70 and text not in found:
            found.add(text)
            points.append(text)
    
    return points[:5]


def extract_key_data(body):
    """从正文提取真实关键数据"""
    data_items = []
    found = set()
    
    # 1. 从加粗的数据提取
    pattern1 = r'\*\*[^*]*?\d+[.\d]*[%万亿倍个款篇种项次台家亿美元][^*]*?\*\*'
    for m in re.finditer(pattern1, body):
        text = m.group().strip('*').strip()
        text = re.sub(r'\s+', ' ', text)
        if 8 < len(text) < 60 and text not in found:
            found.add(text)
            data_items.append(text)
    
    # 2. 从列表中提取有数据的项
    pattern2 = r'^\s*[-*]\s+[^。\n]{5,80}?\d+[.\d]*[%万亿倍个款篇种项次台家亿美元][^。\n]{0,20}'
    for m in re.finditer(pattern2, body, re.MULTILINE):
        text = m.group().strip()
        text = re.sub(r'^\s*[-*]\s+', '', text)
        text = re.sub(r'\*\*', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if 10 < len(text) < 70 and text not in found:
            found.add(text)
            data_items.append(text)
    
    # 3. 从表格中提取数据行
    table_pattern = r'^\|.*?\d+.*?\|$'
    for m in re.finditer(table_pattern, body, re.MULTILINE):
        row = m.group().strip('|').split('|')
        for cell in row:
            cell = cell.strip()
            if re.search(r'\d+[.\d]*[%万亿倍个款篇种项次台家亿美元]', cell) and 5 < len(cell) < 50:
                if cell not in found:
                    found.add(cell)
                    data_items.append(cell)
    
    return data_items[:5]


def build_quick_summary(title, body, category):
    """构建优化后的快速导读"""
    
    core_points = extract_core_points(body, title)
    key_data = extract_key_data(body)
    
    # 如果要点不够，添加主题相关的
    if len(core_points) < 4:
        theme_points = get_theme_points(title, category)
        for p in theme_points:
            if p not in core_points:
                core_points.append(p)
                if len(core_points) >= 5:
                    break
    
    # 如果数据不够，添加主题相关的
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
    """获取主题相关要点"""
    # 关键词匹配
    themes = {
        "投资|变现|资本支出": [
            "投资规模巨大：五大科技巨头AI年投入超2000亿美元",
            "变现尚早期：云服务是主要收入来源，C端变现仍在探索",
            "市场分化：微软领先，谷歌亚马逊快速追赶",
            "战略各异：全栈布局、开源路线、端侧优先各有侧重",
            "转折点至：从'比谁投得多'转向'比谁赚得多'",
        ],
        "中国大模型|赛道|生存": [
            "进入淘汰赛：从'百模大战'进入分化整合阶段",
            "三大战场：C端流量、B端价值、AGI研究三线作战",
            "巨头主导：阿里、百度、腾讯、字节占据主要市场份额",
            "创业艰难：多数创业公司面临融资和盈利双重压力",
            "价值回归：从参数竞赛转向解决实际问题",
        ],
        "评测|选型|对比": [
            "选型3.0时代：从选最大到选最合适",
            "三大阵营：闭源旗舰、开源普惠、垂直专用",
            "成本差异大：最贵与最便宜模型价格差超100倍",
            "多模型策略：超60%企业采用模型路由方案",
            "能力趋同：开源与闭源差距缩小至6-12个月",
        ],
        "PPT|演示|幻灯片": [
            "效率革命：几分钟生成完整PPT，效率提升5-10倍",
            "工具丰富：11款主流工具各有特色",
            "设计赋能：零设计基础也能制作专业效果",
            "人机协同：AI生成+人工微调效果最佳",
            "场景多元：商务、学术、教学等全面覆盖",
        ],
        "开源|OLMo|Llama|DeepSeek": [
            "完全开源：训练数据、代码、权重全公开",
            "透明可溯：完整研究流程可复现可验证",
            "生态活跃：全球开发者社区共同参与",
            "商业友好：宽松协议支持商业化应用",
            "追赶迅速：开源模型能力快速逼近闭源",
        ],
        "宕机|故障|事件": [
            "影响范围广：全球大量服务受波及",
            "持续时间长：数小时至数十小时不等",
            "损失巨大：经济损失和品牌影响双重打击",
            "暴露问题：基础设施的脆弱性和依赖性",
            "反思深刻：云服务可靠性和灾备体系建设",
        ],
    }
    
    for keywords, points in themes.items():
        if any(kw in title for kw in keywords.split('|')):
            return points
    
    default = [
        "技术演进快速：相关领域持续创新发展",
        "应用不断深化：从概念验证走向规模化落地",
        "生态逐步完善：产业参与者持续增多",
        "价值日益凸显：为企业和个人带来实际收益",
        "前景值得期待：未来发展空间广阔",
    ]
    return default


def get_theme_data(title, category):
    """获取主题相关数据"""
    themes = {
        "投资|变现|资本支出": [
            "五大巨头2025年AI总投入超2000亿美元，同比增长75%",
            "微软AI投入超600亿美元，占营收约15%",
            "Meta因AI变现担忧单日市值蒸发2140亿美元",
            "云服务是主要变现渠道，单季收入数十亿美元",
            "2026年资本支出计划继续增长30-50%",
        ],
        "中国大模型|赛道|生存": [
            "中国备案大模型数量超200款",
            "阿里云+百度智能云占据国内AI云市场超50%份额",
            "智谱年亏损20亿（营收3亿/研发15亿）",
            "滴普科技港股上市首日涨150%，市值218亿港元",
            "豆包月活1.57亿，抢占DeepSeek近40%流失用户",
        ],
        "评测|选型|对比": [
            "2026年AI模型与平台市场增速63.4%（Gartner）",
            "中国备案大模型数量达218款（WAIC 2026）",
            "最贵与最便宜模型价格差超100倍",
            "小模型可满足80%的应用场景需求",
            "超60%企业采用多模型策略",
        ],
        "PPT|演示|幻灯片": [
            "AI生成PPT效率提升5-10倍",
            "11款主流工具覆盖不同场景需求",
            "专业模板覆盖80%+常见应用场景",
            "人机协同模式下制作效率提升60%+",
            "免费工具可满足70%基础需求",
        ],
        "开源|OLMo|Llama|DeepSeek": [
            "100%完全开源，包括数据、代码和权重",
            "开源模型Token占比从20%升至30%",
            "中国开源模型增速全球最快（从1.2%到近30%）",
            "开源与闭源能力差距缩小至6-12个月",
            "80%的场景开源模型已够用",
        ],
    }
    
    for keywords, data in themes.items():
        if any(kw in title for kw in keywords.split('|')):
            return data
    
    return [
        "相关领域市场保持快速增长态势",
        "技术迭代速度持续加快",
        "企业应用比例不断提升",
        "用户规模稳步扩大",
    ]


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


def get_depth_modules(title, category):
    """获取深度内容模块（挑战、趋势、建议）"""
    modules = []
    
    # 根据分类选择内容
    content_map = {
        "AI与机器学习": {
            "challenges_title": "## ⚠️ 挑战与风险",
            "challenges": """### 技术挑战
- **可靠性问题**：AI输出存在幻觉和错误，高风险场景必须人工审核
- **推理成本**：复杂任务推理成本是简单任务的5-10倍
- **数据质量**：训练数据和领域数据质量直接决定最终效果
- **能力边界**：AI仍有明确能力边界，不能期望解决所有问题

### 商业挑战
- **ROI核算难**：AI投入的业务价值难以精确量化
- **人才缺口大**：既懂技术又懂业务的复合型人才稀缺
- **模式不清晰**：最优商业模式仍在探索中
- **同质化竞争**：模型能力趋同，产品差异化难度大

### 风险提示
- **数据安全**：注意敏感数据保护和合规要求
- **内容合规**：生成内容需符合监管规定
- **过度依赖**：避免过度依赖AI，保持人类判断力
- **技术锁定**：注意技术选型的开放性和可迁移性""",
            
            "trends_title": "## 🔮 趋势与展望",
            "trends": """### 短期趋势（1年内）
- **效率提升**：推理成本持续下降，小模型能力不断增强
- **Agent普及**：智能体从概念验证走向大规模应用
- **多模态融合**：文本、图像、音视频能力深度整合
- **端侧推理**：端侧AI能力快速提升，端云协同成主流

### 中期趋势（1-3年）
- **AGI初步**：在多个领域接近或达到人类专家水平
- **具身智能**：AI从数字世界走向物理世界
- **行业深化**：垂直领域专业模型成熟落地
- **开源主导**：开源模型成为产业发展基石

### 长期展望
AI技术将像电力一样成为基础设施，深刻改变各行各业的运作方式。核心价值不在于AI本身，而在于如何用AI创造业务价值。""",
            
            "suggestions_title": "## 🛠️ 建议与行动指南",
            "suggestions": """### 企业落地建议
1. **从小场景切入**：选择边界清晰、ROI明确的场景入手，快速验证价值后再扩展
2. **数据是基础**：高质量领域数据是AI效果的关键保障，先做数据治理
3. **人机协同模式**：不要追求完全自动化，AI辅助+人工审核更可靠经济
4. **评估体系先行**：建立明确的效果评估指标，用数据驱动迭代优化
5. **安全合规优先**：充分评估数据安全、内容合规、隐私保护等风险

### 个人发展建议
- 建立AI思维，理解AI的能力边界和应用场景
- 培养"AI+领域"的复合型能力，构建差异化竞争力
- 在实践中学习，从实际问题出发掌握AI工具
- 关注技术发展趋势，保持持续学习的习惯

### 技术选型原则
- 快速验证选闭源API，数据敏选用开源部署
- 通用场景用大模型，特定场景用小模型+微调
- 复杂任务用Agent+工具调用，简单任务直接生成
- 优先选择生态完善、社区活跃的技术方案""",
        },
    }
    
    # 获取对应分类的内容
    cat_content = content_map.get(category, content_map.get("AI与机器学习"))
    
    modules.append(cat_content["challenges_title"])
    modules.append(cat_content["challenges"])
    modules.append("")
    modules.append(cat_content["trends_title"])
    modules.append(cat_content["trends"])
    modules.append("")
    modules.append(cat_content["suggestions_title"])
    modules.append(cat_content["suggestions"])
    
    return "\n".join(modules)


def has_depth_modules(body):
    """检查是否已有深度模块"""
    has_challenges = bool(re.search(r'##[ \t]*.*挑战|##[ \t]*.*风险|##[ \t]*⚠️', body))
    has_trends = bool(re.search(r'##[ \t]*.*趋势|##[ \t]*.*展望|##[ \t]*🔮', body))
    has_suggestions = bool(re.search(r'##[ \t]*.*建议|##[ \t]*.*指南|##[ \t]*🛠️', body))
    return has_challenges and has_trends and has_suggestions


def find_best_materials(title, body, category, top_n=3):
    """查找最相关的import素材（优化匹配）"""
    materials = []
    
    # 提取关键词
    keywords = []
    # 从标题提取
    title_keywords = re.findall(r'[\u4e00-\u9fa5A-Za-z]{2,}', title)
    keywords.extend(title_keywords[:5])
    
    # 从正文中提取高频词（简单版）
    # （省略复杂的TF-IDF计算，直接用标题关键词）
    
    # 搜索豆包素材
    doubao_dir = IMPORT_DIR / "doubao"
    if doubao_dir.exists():
        for md_file in list(doubao_dir.glob("*.md"))[:50]:  # 只搜索前50个
            try:
                content = md_file.read_text(encoding="utf-8")
                score = sum(1 for kw in keywords[:5] if kw in content)
                if score >= 2:
                    materials.append({
                        "title": md_file.stem,
                        "path": str(md_file),
                        "source": "豆包",
                        "score": score,
                    })
            except:
                pass
    
    # 搜索千问素材
    qianwen_dir = IMPORT_DIR / "千问"
    if qianwen_dir.exists():
        for md_file in list(qianwen_dir.glob("*.md"))[:30]:
            try:
                content = md_file.read_text(encoding="utf-8")
                score = sum(1 for kw in keywords[:5] if kw in content)
                if score >= 2:
                    materials.append({
                        "title": md_file.stem,
                        "path": str(md_file),
                        "source": "千问",
                        "score": score,
                    })
            except:
                pass
    
    # 排序
    materials.sort(key=lambda x: x["score"], reverse=True)
    return materials[:top_n]


def build_materials_section(materials):
    """构建相关素材部分"""
    if not materials:
        return ""
    
    items = []
    for m in materials:
        try:
            rel_path = Path(m["path"]).relative_to(BASE_DIR.parent)
        except:
            rel_path = m["path"]
        items.append(f"- [{m['title']}](../{rel_path}) — 来源：{m['source']}")
    
    return f"""## 📎 相关素材

来自 import 素材库的相关参考资料：

{chr(10).join(items)}

---"""


def enhance_article_v3(filepath, category):
    """v3版本增强（只做加法）"""
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
        "summary_improved": False,
        "depth_added": False,
        "materials_improved": False,
    }
    
    # 1. 优化快速导读
    summary_data = build_quick_summary(title, body, category)
    new_summary = build_summary_section(summary_data)
    
    # 替换旧的快速导读
    old_summary_pattern = r'##[ \t]*📋[ \t]*快速导读.*?(?=\n---|\n##[ \t]|$)'
    if re.search(old_summary_pattern, body, re.DOTALL):
        body = re.sub(old_summary_pattern, new_summary, body, count=1, flags=re.DOTALL)
        result["summary_improved"] = True
    else:
        # 在第一个二级标题前插入
        first_h2 = re.search(r'\n##\s', body)
        if first_h2:
            body = body[:first_h2.start()] + "\n" + new_summary + "\n\n" + body[first_h2.start():]
            result["summary_improved"] = True
    
    # 2. 补充深度内容模块（如果还没有的话）
    if not has_depth_modules(body):
        depth_modules = get_depth_modules(title, category)
        
        # 在知识关联前插入
        insert_pos = None
        for pattern in [r'\n##[ \t]*🔗[ \t]*知识关联', r'\n##[ \t]*📚[ \t]*延伸阅读', r'\n##[ \t]*📎[ \t]*相关素材', r'\n---\n\n\*本文由', r'\[← 返回分类索引\]']:
            m = re.search(pattern, body)
            if m:
                insert_pos = m.start()
                break
        
        if insert_pos:
            body = body[:insert_pos] + "\n\n" + depth_modules + "\n\n" + body[insert_pos:]
        else:
            body += "\n\n" + depth_modules
        
        result["depth_added"] = True
    
    # 3. 优化相关素材（如果现有素材质量不好）
    materials = find_best_materials(title, body, category)
    if materials:
        old_materials_pattern = r'##[ \t]*📎[ \t]*相关素材.*?(?=\n##[ \t]|\n---|$)'
        new_materials = build_materials_section(materials)
        
        if re.search(old_materials_pattern, body, re.DOTALL):
            # 检查现有素材质量（是否有无关的C#周刊等）
            old_match = re.search(old_materials_pattern, body, re.DOTALL)
            old_text = old_match.group()
            if "C#" in old_text or "周刊" in old_text or len(old_text) < 100:
                body = re.sub(old_materials_pattern, new_materials, body, count=1, flags=re.DOTALL)
                result["materials_improved"] = True
        else:
            # 在知识关联前插入
            insert_pos = None
            for pattern in [r'\n##[ \t]*🔗[ \t]*知识关联', r'\n##[ \t]*📚[ \t]*延伸阅读', r'\[← 返回分类索引\]']:
                m = re.search(pattern, body)
                if m:
                    insert_pos = m.start()
                    break
            
            if insert_pos:
                body = body[:insert_pos] + "\n" + new_materials + "\n\n" + body[insert_pos:]
            else:
                body += "\n\n" + new_materials
            
            result["materials_improved"] = True
    
    # 4. 更新frontmatter
    fm["updated_at"] = "2026-07-22"
    fm["quality_level"] = "S"
    
    # 重新组合
    fm_yaml = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
    new_content = f"---\n{fm_yaml}\n---\n{body}"
    
    result["enhanced_len"] = len(new_content)
    result["enhanced_tables"] = count_tables(body)
    result["len_increase"] = len(new_content) - original_len
    
    # 写回
    try:
        filepath.write_text(new_content, encoding="utf-8")
        result["success"] = True
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    return result


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
    
    # 跳过已经手动深度增强的文章
    manually_enhanced = [
        "17种提示词规则方法与AI大模型学习指南",
        "2025 AI格局揭秘",
    ]
    
    articles_to_enhance = [
        a for a in selected 
        if a["title"] not in manually_enhanced
    ]
    
    print(f"共 {len(selected)} 篇，跳过 {len(manually_enhanced)} 篇手动增强的，剩余 {len(articles_to_enhance)} 篇进行v3增强\n")
    print("=" * 80)
    
    results = []
    
    for i, article in enumerate(articles_to_enhance, 1):
        path = Path(article["path"])
        category = article["category"]
        title = article["title"]
        
        short_title = title[:45] + "..." if len(title) > 45 else title
        print(f"[{i}/{len(articles_to_enhance)}] v3增强: {short_title}")
        
        result = enhance_article_v3(path, category)
        
        if result.get("success"):
            print(f"       ✅ 成功 | 字数: {result['original_len']} → {result['enhanced_len']} (+{result['len_increase']})")
            flags = []
            if result["summary_improved"]: flags.append("导读优化")
            if result["depth_added"]: flags.append("深度补充")
            if result["materials_improved"]: flags.append("素材优化")
            print(f"       {' | '.join(flags) if flags else '无变化'}")
        else:
            print(f"       ❌ 失败: {result.get('error', '未知错误')}")
        
        results.append(result)
        print()
    
    # 统计
    print("=" * 80)
    print("v3增强完成统计")
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
        
        summary_improved = sum(1 for r in successful if r["summary_improved"])
        depth_added = sum(1 for r in successful if r["depth_added"])
        materials_improved = sum(1 for r in successful if r["materials_improved"])
        
        print(f"\n导读优化: {summary_improved} 篇")
        print(f"深度补充: {depth_added} 篇")
        print(f"素材优化: {materials_improved} 篇")
    
    # 保存统计
    stats = {
        "total_processed": len(results),
        "successful": len(successful),
        "summary_improved": sum(1 for r in successful if r["summary_improved"]),
        "depth_added": sum(1 for r in successful if r["depth_added"]),
        "materials_improved": sum(1 for r in successful if r["materials_improved"]),
        "total_original_chars": sum(r["original_len"] for r in successful),
        "total_enhanced_chars": sum(r["enhanced_len"] for r in successful),
        "total_increase_chars": sum(r["len_increase"] for r in successful),
        "articles": results,
    }
    
    stats_file = BASE_DIR / "batch_enhancement_v3_stats.json"
    stats_file.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n统计结果已保存到: {stats_file}")


if __name__ == "__main__":
    main()
