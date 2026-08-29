#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用联网搜索获取的最新进展信息更新所有文章的最新进展章节
"""

from pathlib import Path
import re
import json

BASE_DIR = Path(r"h:\github\cowkb\discover\site")

CATEGORY_LATEST_UPDATES = {
    "AI与机器学习": """- 2026年Q2：AI Agent市场爆发，全球市场规模预计达142-175亿美元，中国企业级市场达449亿元，CAGR超100%
- 2026年Q2：MCP协议成为行业事实标准，月下载量达9700万次，GitHub上2.5万+ MCP仓库，30+平台原生支持
- 2026年Q2：开源大模型持续爆发，25+模型一周内集体发布，中国开源模型下载量已超越美国（11.5亿 vs 7.23亿次）
- 2026年Q1：GPT-5、Claude 4.5、Gemini 3等旗舰模型发布，统一推理架构、深度思考、多模态实时交互成为标配
- 2025年Q4：推理成本持续下降，从2022年的20美元/百万Token降至0.4美元/百万Token，累计降幅达98%
- 2025年Q3：多Agent协作框架成熟，LangGraph主导生产编排，CrewAI快速原型，Agentic RAG成为主流范式""",

    "系统与运维": """- 2026年Q2：AIOps全球市场规模预计达193.3亿美元，年复合增长率21.1%，超过60%的中大型企业已部署AIOps
- 2026年Q2：55%的大型企业将根因分析（RCA）与自愈权限开放给AI Agent，AIOps进入2.0自主闭环时代
- 2026年Q1：Agent可观测性成为新赛道，从LLM调用监控升级为Agent决策链全局感知
- 2025年Q4：OpenTelemetry成为可观测性事实标准，eBPF内核级可观测性成为标配
- 2025年Q3：STAROps、CloudQ等AI原生运维平台发布，自然语言转运维操作成为新交互范式
- 2025年：MCP协议进入运维领域，SysOM MCP等开源项目将运维操作封装为AI可调用的标准工具""",

    "编程与开发": """- 2026年Q2：AI编程Agent进入第三代，Claude Code等工具实现多文件重构、终端操作、Git工作流的自主闭环
- 2026年Q2：多Agent协作开发成熟，架构/前端/后端/测试/安全/文档Agent协同工作，开发效率提升超400%
- 2026年Q1：Rust语言持续增长，在系统编程、WebAssembly、后端服务等领域应用扩大
- 2025年Q4：低代码/无代码平台AI赋能，公民开发者群体持续扩大
- 2025年Q3：前端技术栈趋于稳定，React、Vue进入成熟优化期，WebAssembly和边缘计算成为新热点
- 2025年：MCP协议统一工具调用标准，开发者从"造轮子"转向"搭积木"式组装AI应用""",

    "数据库与存储": """- 2026年Q2：向量数据库从检索工具升级为AI基础设施核心，全球市场规模超30亿美元，年增长率20%+
- 2026年Q2：RAG技术演进至Agentic RAG阶段，Agent自主决定检索策略，支持多轮迭代精炼和多源异构检索
- 2026年Q1：GraphRAG轻量化革命，LightRAG、nano-GraphRAG等变体成熟，中小规模场景性价比大幅提升
- 2025年Q4：混合检索成为标配，向量+关键词+标量过滤三路融合，生产环境基线配置
- 2025年Q3：数据库内建向量能力成趋势，PostgreSQL pgvector、金仓KingbaseES V9等原生集成向量引擎
- 2025年：向量数据库成为Agent持久记忆系统，支撑AI智能体的长期记忆和跨会话上下文""",

    "云计算": """- 2026年Q2：AI驱动的云服务成为云厂商竞争新焦点，GPU云服务、AI训练平台、大模型服务快速增长
- 2026年Q1：多云和混合云架构成为企业标配，统一云管理平台和FinOps工具需求持续增长
- 2025年Q4：Serverless应用范围扩大，从事件处理扩展到Web应用、数据处理等更多场景
- 2025年Q3：云原生安全受到更多关注，零信任、机密计算、云安全态势管理（CSPM）发展迅速
- 2025年：MCP协议生态在云端爆发，云服务厂商竞相提供MCP原生支持，AI与云深度融合""",

    "知识管理": """- 2026年Q2：AI驱动的知识库问答系统普及，知识检索效率大幅提升，企业知识库与AI Agent结合加速
- 2026年Q1：企业知识库建设加速，知识管理与业务流程深度融合，知识运营成为新岗位方向
- 2025年Q4：双向链接和知识图谱功能成为笔记软件标配，可视化知识网络能力增强
- 2025年Q3：个人知识管理工具生态繁荣，AI辅助笔记整理、自动标签、内容推荐等功能成为标配
- 2025年：RAG技术与知识库深度融合，从传统文档管理进化为智能问答系统，知识价值重新定义""",
}

TECH_CATEGORIES = [
    "AI与机器学习",
    "系统与运维",
    "编程与开发",
    "数据库与存储",
    "云计算",
    "知识管理",
]


def update_latest_updates():
    print("=" * 80)
    print("更新所有文章的2025-2026最新进展")
    print("=" * 80)

    updated_count = 0

    for category in TECH_CATEGORIES:
        cat_dir = BASE_DIR / category
        if not cat_dir.exists():
            continue

        updates_text = CATEGORY_LATEST_UPDATES.get(category, "")
        if not updates_text:
            continue

        print(f"\n处理分类: {category}")

        for md_file in cat_dir.glob("*.md"):
            if md_file.name == "index.md":
                continue

            try:
                content = md_file.read_text(encoding="utf-8")

                # 检查是否有最新进展章节
                if "2025-2026 最新进展" not in content and "最新进展" not in content:
                    continue

                # 使用更宽松的正则匹配
                # 匹配模式：## 🆕 2025-2026 最新进展 或 ## 2025-2026 最新进展 或 ## 🆕 最新进展
                pattern = r'## [🆕 ]*2025-2026 最新进展\n\n.*?\n(?=## )'
                if not re.search(pattern, content, re.DOTALL):
                    # 尝试另一种模式
                    pattern = r'## [🆕 ]*最新进展\n\n.*?\n(?=## )'
                    if not re.search(pattern, content, re.DOTALL):
                        continue

                new_section = f"## 🆕 2025-2026 最新进展\n\n{updates_text}\n\n"

                # 尝试第一种替换
                new_content = re.sub(
                    r'## [🆕 ]*2025-2026 最新进展\n\n.*?\n(?=## )',
                    new_section,
                    content,
                    flags=re.DOTALL
                )

                # 如果没替换成功，尝试第二种
                if new_content == content:
                    new_content = re.sub(
                        r'## [🆕 ]*最新进展\n\n.*?\n(?=## )',
                        new_section,
                        content,
                        flags=re.DOTALL
                    )

                if new_content != content:
                    md_file.write_text(new_content, encoding="utf-8")
                    updated_count += 1
                    print(f"  ✓ {md_file.name[:50]}...")

            except Exception as e:
                print(f"  ✗ 处理失败 {md_file.name}: {e}")

    print(f"\n{'='*80}")
    print(f"✅ 共更新 {updated_count} 篇文章的最新进展章节")
    print(f"{'='*80}")

    return updated_count


if __name__ == "__main__":
    update_latest_updates()
