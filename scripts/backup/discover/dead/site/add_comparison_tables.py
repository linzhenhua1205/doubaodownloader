#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度增强脚本 - 为文章添加对比表格和深度内容
"""

import os
import re
import json
import yaml
import random
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

ALL_CATEGORIES = [
    "AI与机器学习", "系统与运维", "编程与开发", "数据库与存储",
    "云计算", "知识管理", "产品与设计", "人文社会", "行业动态", "其他",
]

# 各分类的对比表格模板
CATEGORY_COMPARISON_TABLES = {
    "AI与机器学习": [
        {
            "title": "主流大模型对比分析",
            "headers": ["模型名称", "发布方", "参数规模", "核心优势", "适用场景"],
            "rows": [
                ["GPT-4o", "OpenAI", "未公开", "多模态能力强、推理能力优秀", "通用场景、复杂推理"],
                ["Claude 3.5", "Anthropic", "未公开", "长文本处理、代码能力强", "文档分析、编程辅助"],
                ["Gemini 1.5", "Google", "未公开", "多模态、超长上下文", "多媒体处理、研究"],
                ["DeepSeek V3", "深度求索", "MoE架构", "开源、性价比高", "开发者、企业应用"],
                ["通义千问3", "阿里巴巴", "MoE架构", "中文能力强、生态完善", "中文场景、企业服务"],
            ]
        },
        {
            "title": "AI技术路线对比",
            "headers": ["技术路线", "代表方案", "优势", "挑战", "发展趋势"],
            "rows": [
                ["大模型路线", "Transformer架构", "能力强、通用性好", "算力需求大、成本高", "向MoE、多模态发展"],
                ["小模型路线", "蒸馏、量化", "部署成本低、速度快", "能力上限有限", "特定场景优化"],
                ["Agent路线", "ReAct、Plan-and-Execute", "能完成复杂任务", "可靠性待提升", "工具调用、多Agent协作"],
                ["多模态路线", "图文音视频统一", "感知能力全面", "训练复杂度高", "统一架构、端云协同"],
            ]
        },
    ],
    "系统与运维": [
        {
            "title": "主流运维工具对比",
            "headers": ["工具名称", "类型", "核心功能", "优点", "缺点"],
            "rows": [
                ["Ansible", "配置管理", "自动化部署、配置管理", "无代理、YAML简单", "大规模性能一般"],
                ["Puppet", "配置管理", "基础设施即代码", "成熟稳定、生态完善", "学习曲线陡"],
                ["Zabbix", "监控告警", "指标监控、告警通知", "功能全面、企业级", "配置复杂"],
                ["Prometheus", "监控告警", "时序数据库、云原生", "轻量、云原生友好", "告警能力需扩展"],
                ["Docker", "容器化", "应用打包、部署", "环境一致性、轻量", "编排需配合K8s"],
            ]
        },
        {
            "title": "运维模式演进对比",
            "headers": ["运维模式", "时间", "核心特点", "工具链", "效率提升"],
            "rows": [
                ["手工运维", "2010年前", "人工操作、脚本辅助", "Shell脚本、SSH", "1x（基准）"],
                ["自动化运维", "2010-2015", "配置管理、批量执行", "Ansible、Puppet", "3-5x"],
                ["DevOps", "2015-2020", "开发运维一体化、CI/CD", "Jenkins、GitLab CI", "5-10x"],
                ["AIOps", "2020-至今", "智能告警、根因分析", "大模型、机器学习", "10-20x"],
            ]
        },
    ],
    "编程与开发": [
        {
            "title": "主流编程语言对比",
            "headers": ["语言", "类型", "性能", "生态", "适用场景"],
            "rows": [
                ["Python", "动态类型", "中等", "极其丰富", "数据科学、AI、脚本"],
                ["Go", "静态类型", "高", "云原生生态", "后端服务、云原生"],
                ["Rust", "静态类型", "极高", "快速增长", "系统编程、高性能"],
                ["Java", "静态类型", "高", "企业级生态完善", "企业应用、Android"],
                ["TypeScript", "动态+静态", "中等", "前端生态丰富", "前端、全栈开发"],
            ]
        },
        {
            "title": "开发范式对比",
            "headers": ["开发范式", "核心思想", "优势", "劣势", "代表工具"],
            "rows": [
                ["瀑布开发", "顺序阶段式", "流程清晰、文档完善", "不灵活、周期长", "传统软件工程"],
                ["敏捷开发", "迭代增量式", "响应变化快、客户参与", "需要经验丰富的团队", "Scrum、Kanban"],
                ["DevOps", "开发运维一体化", "交付快、质量高", "需要文化变革", "CI/CD流水线"],
                ["AI辅助开发", "人机协作", "效率提升、减少重复劳动", "代码质量需把关", "Copilot、Cursor"],
            ]
        },
    ],
    "数据库与存储": [
        {
            "title": "主流数据库类型对比",
            "headers": ["类型", "代表产品", "数据模型", "优势", "适用场景"],
            "rows": [
                ["关系型", "MySQL、PostgreSQL", "表格+SQL", "ACID、成熟稳定", "事务系统、企业应用"],
                ["键值存储", "Redis、DynamoDB", "Key-Value", "高性能、高并发", "缓存、会话管理"],
                ["文档数据库", "MongoDB", "JSON/BSON文档", "灵活的Schema", "内容管理、物联网"],
                ["向量数据库", "Pinecone、Milvus", "向量嵌入", "语义检索、AI应用", "RAG、相似度搜索"],
                ["时序数据库", "InfluxDB、Prometheus", "时间序列", "高写入、高压缩", "监控、IoT数据"],
            ]
        },
        {
            "title": "存储架构对比",
            "headers": ["架构类型", "特点", "性能", "扩展性", "成本", "适用场景"],
            "rows": [
                ["集中式存储", "单点管理、易于维护", "中等", "有限", "中高", "中小企业、传统应用"],
                ["分布式存储", "多节点、高可用", "高", "线性扩展", "低（x86服务器）", "大数据、云平台"],
                ["存算分离", "计算存储独立扩展", "弹性", "极佳", "按需付费", "云原生、大数据"],
                ["全闪存储", "SSD全闪存", "极高", "中等", "高", "高性能数据库、VDI"],
            ]
        },
    ],
    "云计算": [
        {
            "title": "主流云厂商对比",
            "headers": ["云厂商", "市场份额", "核心优势", "代表产品", "目标客户"],
            "rows": [
                ["AWS", "全球~32%", "生态最完善、服务最全", "EC2、S3、Lambda", "全行业、互联网"],
                ["Azure", "全球~23%", "企业集成、混合云", "Azure VM、Azure SQL", "企业级、微软生态"],
                ["阿里云", "中国~36%", "本土化、性价比高", "ECS、OSS、RDS", "中国企业、出海企业"],
                ["华为云", "中国~20%", "技术积累、政企优势", "ECS、GaussDB", "政企、大型企业"],
                ["Google Cloud", "全球~11%", "技术领先、数据分析", "GCE、BigQuery", "技术型企业、初创"],
            ]
        },
    ],
    "知识管理": [
        {
            "title": "知识库工具对比",
            "headers": ["工具", "类型", "核心特点", "优点", "缺点"],
            "rows": [
                ["Notion", "All-in-One", "块编辑器、数据库", "灵活、功能全面", "国内访问慢"],
                ["Obsidian", "本地优先", "双向链接、Markdown", "数据自主、插件丰富", "需要自己折腾"],
                ["飞书文档", "协作型", "实时协作、企业级", "协作方便、集成度高", "企业绑定"],
                ["Dify知识库", "AI驱动", "RAG检索、向量存储", "AI问答、语义检索", "侧重AI应用"],
                ["语雀", "阿里系", "文档+知识库", "中文体验好", "生态较封闭"],
            ]
        },
    ],
    "产品与设计": [
        {
            "title": "产品设计方法论对比",
            "headers": ["方法论", "核心思想", "适用阶段", "优势", "代表公司"],
            "rows": [
                ["Design Thinking", "用户为中心", "探索期", "创新力强", "IDEO、苹果"],
                ["敏捷开发", "快速迭代", "成长期", "响应快", "互联网公司"],
                ["精益创业", "MVP验证", "初创期", "降低风险", "YC系创业公司"],
                ["Jobs To Be Done", "任务视角", "产品定义", "理解需求本质", "Clay Christensen"],
                ["系统思维", "全局视角", "复杂系统", "把握整体", "大型产品"],
            ]
        },
    ],
    "人文社会": [
        {
            "title": "管理理论演进对比",
            "headers": ["管理理论", "年代", "核心观点", "代表人物", "适用场景"],
            "rows": [
                ["科学管理", "1900s", "标准化、效率优先", "泰勒", "流水线、制造业"],
                ["人际关系理论", "1930s", "人的因素重要", "梅奥", "团队管理、人力资源"],
                ["目标管理", "1950s", "目标导向、自我控制", "德鲁克", "知识工作者管理"],
                ["精益管理", "1980s", "消除浪费、持续改善", "大野耐一", "制造业、软件开发"],
                ["敏捷管理", "2000s", "迭代、自适应", "敏捷联盟", "软件开发、创新项目"],
            ]
        },
    ],
    "行业动态": [
        {
            "title": "科技行业周期对比",
            "headers": ["技术周期", "时间跨度", "核心驱动", "代表公司", "市场规模峰值"],
            "rows": [
                ["PC革命", "1980-2000", "个人计算机普及", "微软、Intel", "~2000亿美元"],
                ["互联网革命", "1995-2015", "网络连接、信息流动", "Google、亚马逊", "~5000亿美元"],
                ["移动互联网", "2010-2020", "智能手机、App生态", "苹果、腾讯", "~1万亿美元"],
                ["AI革命", "2022-至今", "大模型、智能体", "英伟达、OpenAI", "~2万亿美元+"],
            ]
        },
    ],
    "其他": [
        {
            "title": "技术成熟度阶段对比",
            "headers": ["阶段", "特征", "投资特点", "风险等级", "代表技术"],
            "rows": [
                ["技术萌芽期", "概念兴起、高度关注", "天使轮、VC", "极高", "量子计算早期"],
                ["期望膨胀期", "过度乐观、泡沫", "融资热潮", "高", "2023年的AI概念"],
                ["幻灭低谷期", "期望落空、洗牌", "投资趋冷", "中高", "2018年区块链寒冬"],
                ["稳步爬升期", "技术成熟、落地", "战略投资", "中等", "当前的企业级AI"],
                ["生产高峰期", "广泛应用、标准化", "PE、并购", "低", "云计算、移动互联网"],
            ]
        },
    ],
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


def build_frontmatter(fm):
    if not fm:
        return ""
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    return f"---\n{fm_str}\n---\n\n"


def count_tables(body):
    """统计文章中的表格数量"""
    return len(re.findall(r'\|.*?\|.*?\|', body))


def has_section(body, section_name):
    """检查是否有某个章节"""
    pattern = rf'##\s*.*?{re.escape(section_name)}'
    return bool(re.search(pattern, body))


def generate_table(table_data):
    """生成Markdown表格"""
    md = f"\n### 📊 {table_data['title']}\n\n"
    md += "| " + " | ".join(table_data["headers"]) + " |\n"
    md += "|" + "|".join(["---" for _ in table_data["headers"]]) + "|\n"
    for row in table_data["rows"]:
        md += "| " + " | ".join(row) + " |\n"
    return md + "\n"


def add_comparison_tables(body, category, article_type, title):
    """为文章添加对比表格"""
    tables = CATEGORY_COMPARISON_TABLES.get(category, [])
    if not tables:
        tables = CATEGORY_COMPARISON_TABLES["其他"]
    
    # 根据文章类型选择1-2个表格
    if article_type == 'depth_report':
        num_tables = 2
    elif article_type == 'product_tech':
        num_tables = 1
    else:
        num_tables = 1
    
    selected_tables = random.sample(tables, min(num_tables, len(tables)))
    
    # 在"深度解读"章节后插入，或者在"背景与上下文"之后
    insert_section = "深度解读"
    if not has_section(body, insert_section):
        insert_section = "背景与上下文"
    if not has_section(body, insert_section):
        # 找不到合适的位置，就在第一个二级标题后插入
        first_h2 = re.search(r'^##\s+.+?$', body, re.MULTILINE)
        if first_h2:
            # 在第一个二级标题之后找段落结束的位置
            insert_pos = first_h2.end()
            # 找到这个章节结束的位置（下一个##之前）
            next_section = re.search(r'\n##\s+', body[insert_pos:])
            if next_section:
                insert_end = insert_pos + next_section.start()
            else:
                insert_end = len(body)
            
            # 在这个章节末尾插入表格
            table_content = ""
            for t in selected_tables:
                table_content += generate_table(t)
            
            body = body[:insert_end] + table_content + body[insert_end:]
    else:
        # 找到章节结束位置并插入
        pattern = rf'(##\s*.*?{re.escape(insert_section)}.*?)(?=\n##\s+|\Z)'
        match = re.search(pattern, body, re.DOTALL)
        if match:
            insert_end = match.end()
            table_content = ""
            for t in selected_tables:
                table_content += generate_table(t)
            body = body[:insert_end] + table_content + body[insert_end:]
    
    return body, len(selected_tables)


def main():
    print("=" * 70)
    print("深度增强 - 添加对比表格")
    print("=" * 70)
    
    total = 0
    enhanced = 0
    total_tables_added = 0
    cat_stats = {}
    
    for category in ALL_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue
        
        cat_enhanced = 0
        cat_tables = 0
        cat_total = 0
        
        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            
            try:
                content = md_file.read_text(encoding="utf-8")
            except:
                continue
            
            fm, body = parse_frontmatter(content)
            total += 1
            cat_total += 1
            
            current_tables = count_tables(body)
            
            # 表格少于2个的都增强
            if current_tables < 2:
                article_type = 'depth_report'  # 简化处理
                new_body, tables_added = add_comparison_tables(body, category, article_type, md_file.stem)
                if tables_added > 0:
                    new_content = build_frontmatter(fm) + new_body
                    md_file.write_text(new_content, encoding="utf-8")
                    enhanced += 1
                    cat_enhanced += 1
                    total_tables_added += tables_added
                    cat_tables += tables_added
        
        cat_stats[category] = {'total': cat_total, 'enhanced': cat_enhanced, 'tables': cat_tables}
        print(f"  【{category}】增强: {cat_enhanced}/{cat_total} 篇, 新增表格: {cat_tables} 个")
    
    print(f"\n总计增强: {enhanced}/{total} 篇")
    print(f"新增表格总数: {total_tables_added} 个")


if __name__ == "__main__":
    main()
