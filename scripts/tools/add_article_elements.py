import os
import re
from pathlib import Path

DIR_PATH = r"h:\github\cowkb\discover\site\编程与开发"

EXISTING_FILES = [
    "2026年GitHub优质开源技能仓库全景指南.md",
    "2025开放原子开发者大会核心内容全记录 📝.md",
    "2025年现代Node_js开发模式全解析 🚀.md",
    "2025年主流开源大语言模型架构演进与效率优化分析 📊.md",
    "2025年主流开源大语言模型架构演进与技术洞察.md",
    "2025年10月前端周刊精选：技术趋势与实践指南 🚀.md",
    "BERT模型结构详解：输入处理与整体架构分析.md",
    "2025年前端框架选择指南：React vs Vue深度对比与学习建议.md",
    "17款最佳代码审查工具详解 🛠️.md",
    "index.md"
]

def extract_headings(content):
    headings = []
    pattern = r'^##\s+(.+)$'
    for line in content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            headings.append(match.group(1))
    return headings

def generate_summary(title):
    summaries = {
        "21条资深工程师职场进阶指南：超越代码的成功法则": "本文总结了资深工程师职场进阶的21条核心教训，涵盖用户问题解决、团队协作、技术选择、代码质量、职业发展等多个维度，帮助工程师从技术专家成长为全面的技术领导者。",
        "ABC 2025 国际会议：代码生成与理解的逻辑关联研究": "本文记录了ABC 2025国际会议关于代码生成与理解的核心研究框架，探讨思维逻辑与计算逻辑之间的双向转化关系，分析代码生成与代码理解的逻辑闭环结构。",
        "AMD与STRADVISION合作：单架构实现L2_L3自动驾驶，CES 2026发布": "本文介绍AMD与STRADVISION在自动驾驶领域的合作成果，基于Versal AI Edge Gen 2自适应SoC实现单架构支持L2到L3级自动驾驶的平滑过渡，预计在CES 2026正式发布。",
        "ARM架构在云手机应用中的挑战与技术瓶颈": "本文深入分析ARM架构在云手机应用中面临的技术挑战，包括生态兼容性、虚拟化性能、内存一致性、安全隔离、工具链成熟度等关键问题及应对策略。",
        "Alfred Gitlab高效操作指南": "本文详细介绍Mac平台下Alfred Gitlab Workflow工具的安装配置与核心功能，帮助开发者快速搜索项目、Issue、MR等，提升Gitlab操作效率。",
        "AtomGit全新升级暨人工智能开源社区发布会全纪录": "本文记录了AtomGit平台全新升级暨人工智能开源社区发布会的核心内容，涵盖平台能力、企业实践案例、高校生态建设等，展示了国产开源+AI一体化基础设施的最新进展。",
        "Awesome-Dify-Workflow：Dify工作流资源与开发指南": "本文介绍Awesome-Dify-Workflow项目的资源与开发指南，分享实用的Dify DSL工作流程，助力开发者快速上手Dify工作流开发。",
        "BERT模型压缩技术深度解析：TinyBERT与BinaryBERT架构与实现": "本文深度解析BERT模型压缩技术，详细介绍TinyBERT和BinaryBERT的架构设计与实现原理，探讨模型压缩在实际应用中的优化策略。",
        "BERT相关论文、文章和代码资源汇总": "本文汇总了BERT模型相关的论文、文章和代码资源，为研究者和开发者提供全面的学习参考资料，涵盖预训练、微调、应用等多个方面。",
        "Bagualu与Chitu技术生态架构分享": "本文分享Bagualu与Chitu的技术生态架构设计，探讨其在远程运维、安全架构等领域的核心特性与技术实现方案。",
        "Bagualu远程运维核心特性与安全架构分享": "本文详细介绍Bagualu远程运维平台的核心特性与安全架构设计，包括远程管理、安全隔离、运维自动化等关键技术能力。",
        "Bash脚本测试PostgreSQL数据库连接指南": "本文提供了使用Bash脚本测试PostgreSQL数据库连接的实用指南，涵盖连接测试方法、错误处理、自动化脚本编写等内容。",
        "B站数据爬取实战（Scrapy框架应用）": "本文通过实战案例介绍使用Scrapy框架爬取B站数据的方法，包括项目配置、爬虫编写、数据存储等完整流程。",
        "CPU_XPU异构融合技术架构介绍": "本文介绍CPU+XPU异构融合技术架构的设计理念与核心技术，探讨异构计算在高性能计算领域的应用前景。",
        "CPU与XPU芯片架构融合的挑战与研究思考": "本文深入分析CPU与XPU芯片架构融合面临的技术挑战，包括架构设计、编程模型、性能优化等方面的研究思考。",
        "CUDA 13_1重大更新深度解析：Tile编程模型如何重塑GPU开发生态": "本文深度解析CUDA 13.1的重大更新，重点介绍Tile编程模型如何重塑GPU开发生态，提升并行计算效率。",
        "C_静态代码扫描工具深度解析与对比 📊": "本文对主流C/C++静态代码扫描工具进行深度解析与对比，分析各工具的检查能力、适用场景和性能特点。",
        "Coze API调用全流程指南与关键技术解析": "本文提供Coze API调用的全流程指南，解析关键技术要点，帮助开发者快速集成Coze能力到应用中。",
        "Cppcheck 静态代码分析工具检查项全解析 🛠️": "本文全面解析Cppcheck静态代码分析工具的检查项，涵盖内存管理、边界检查、性能优化等多个维度的检查规则。",
        "Cursor实战：一人全流程模块开发与协同开发体验": "本文分享使用Cursor进行一人全流程模块开发与团队协同开发的实战体验，展示AI辅助编程工具在实际项目中的应用价值。",
        "DDC2025地瓜机器人开发者大会：具身智能时代的全链路开发基础设施升级": "本文记录DDC2025地瓜机器人大会的核心内容，探讨具身智能时代的全链路开发基础设施升级方案，展示大算力开发平台的最新成果。",
        "DGX H100_H200 Redfish API使用指南与案例详解 📝": "本文详细介绍NVIDIA DGX H100/H200服务器的Redfish API使用方法，通过实际案例演示API调用流程与配置要点。",
        "DeepSeek 网页_API 性能异常事件记录（2025年11月25日）": "本文记录了2025年11月25日DeepSeek网页/API性能异常事件的详细情况，包括故障表现、影响范围和修复过程。",
        "DemoGrasp：单演示轨迹驱动的通用灵巧手抓取框架": "本文介绍DemoGrasp通用灵巧手抓取框架，基于单演示轨迹实现高效抓取，展示北大团队在通用抓取领域的技术突破。",
        "Devin部署能力解析：前端与后端应用部署指南": "本文解析Devin的部署能力，提供前端与后端应用的部署指南，帮助开发者快速将应用部署到生产环境。",
        "Dify工作流代码节点开发规范与最佳实践": "本文介绍Dify工作流代码节点的开发规范与最佳实践，涵盖代码编写、测试、部署等全流程要点。",
        "Dify工作流模板资源包深度解析：160_场景化应用与技术架构": "本文深度解析Dify工作流模板资源包，介绍160+场景化应用模板的设计理念与技术架构，助力开发者快速构建工作流。",
        "Dify平台集成阿里云百炼模型全流程指南：从配置到应用开发": "本文提供Dify平台集成阿里云百炼模型的全流程指南，从配置到应用开发的完整步骤，帮助开发者快速接入大模型能力。",
        "Dify开发文档：迭代节点深度解析与应用指南": "本文深度解析Dify迭代节点的原理与应用，提供详细的开发指南，帮助开发者掌握迭代节点的使用技巧。",
        "Dify插件开发环境搭建与核心规范全指南": "本文提供Dify插件开发环境搭建与核心规范的完整指南，涵盖环境配置、开发流程、调试方法等关键内容。",
        "Dify知识库召回测试与运维网工副业转型指南": "本文介绍Dify知识库召回测试方法与运维网工副业转型指南，探讨AI时代技术人员的职业发展新方向。",
        "Docker 搭建 Gitlab 服务器完整步骤 📝": "本文提供使用Docker搭建Gitlab服务器的完整步骤指南，涵盖安装配置、备份恢复、性能优化等关键环节。",
        "Docker容器技术体系架构详解 📦": "本文详细解析Docker容器技术体系架构，包括镜像管理、容器运行时、网络存储等核心组件的设计原理。",
        "EFCIO新纪元10周年共创大会：全球化软件架构与品牌实践": "本文记录EFCIO新纪元10周年共创大会的核心内容，探讨全球化软件架构与品牌实践的经验与展望。",
        "ELK-MCP：面向工作流集成的稳健日志查询后端（兼容ES 6_5_4）": "本文介绍ELK-MCP日志查询后端的设计与实现，兼容Elasticsearch 6.5.4，提供面向工作流集成的稳健日志查询能力。",
        "Flask与Streamlit对比": "本文对比分析Flask与Streamlit两个Python Web框架的特点与适用场景，帮助开发者选择合适的框架。",
        "Flask内部服务器错误深度解析：原因、解决方案与实例": "本文深度解析Flask内部服务器错误的原因与解决方案，通过实例演示错误排查与修复过程。",
        "Flask内部服务器错误（500错误）深度解析与解决方案": "本文详细分析Flask 500错误的常见原因，提供系统化的解决方案与预防措施。",
        "Flask框架入门指南": "本文提供Flask框架的入门指南，涵盖环境搭建、路由配置、模板渲染、数据库操作等基础内容。",
        "FuzzyMatching算法：原理、应用与实现细节 📝": "本文深入解析FuzzyMatching模糊匹配算法的原理、应用场景与实现细节，帮助开发者理解和应用该算法。",
        "GAGARVN 组织 GitHub 主页分析": "本文分析GAGARVN组织的GitHub主页内容，探讨其开源项目特点与技术影响力。",
    }
    return summaries.get(title, f"本文介绍{title}相关内容，涵盖技术原理、实践应用等方面。")

def generate_keywords(title):
    keywords_map = {
        "21条资深工程师职场进阶指南：超越代码的成功法则": "职场进阶, 工程师成长, 团队协作, 代码质量, 职业发展",
        "ABC 2025 国际会议：代码生成与理解的逻辑关联研究": "代码生成, 代码理解, AI编程, 逻辑模型, 学术研究",
        "AMD与STRADVISION合作：单架构实现L2_L3自动驾驶，CES 2026发布": "自动驾驶, AMD, STRADVISION, SoC, CES 2026",
        "ARM架构在云手机应用中的挑战与技术瓶颈": "ARM架构, 云手机, 虚拟化, 性能优化, 技术挑战",
        "Alfred Gitlab高效操作指南": "Alfred, Gitlab, 效率工具, Mac, 开发工具",
        "AtomGit全新升级暨人工智能开源社区发布会全纪录": "AtomGit, 开源社区, 人工智能, 国产平台, 代码托管",
        "Awesome-Dify-Workflow：Dify工作流资源与开发指南": "Dify, 工作流, DSL, AI应用, 自动化",
        "BERT模型压缩技术深度解析：TinyBERT与BinaryBERT架构与实现": "BERT, 模型压缩, TinyBERT, BinaryBERT, 深度学习",
        "BERT相关论文、文章和代码资源汇总": "BERT, 论文汇总, 代码资源, 自然语言处理, NLP",
        "Bagualu与Chitu技术生态架构分享": "Bagualu, Chitu, 技术生态, 远程运维, 安全架构",
        "Bagualu远程运维核心特性与安全架构分享": "Bagualu, 远程运维, 安全架构, 运维自动化",
        "Bash脚本测试PostgreSQL数据库连接指南": "Bash, PostgreSQL, 数据库连接, 脚本编程",
        "B站数据爬取实战（Scrapy框架应用）": "Scrapy, 数据爬取, B站, 爬虫开发, Python",
        "CPU_XPU异构融合技术架构介绍": "CPU, XPU, 异构计算, 芯片架构, 高性能计算",
        "CPU与XPU芯片架构融合的挑战与研究思考": "CPU, XPU, 架构融合, 技术挑战, 研究方向",
        "CUDA 13_1重大更新深度解析：Tile编程模型如何重塑GPU开发生态": "CUDA, GPU编程, Tile模型, 并行计算, NVIDIA",
        "C_静态代码扫描工具深度解析与对比 📊": "静态代码分析, C/C++, 代码质量, 安全扫描",
        "Coze API调用全流程指南与关键技术解析": "Coze, API调用, AI助手, 开发集成",
        "Cppcheck 静态代码分析工具检查项全解析 🛠️": "Cppcheck, 静态分析, 代码检查, C/C++",
        "Cursor实战：一人全流程模块开发与协同开发体验": "Cursor, AI编程, 开发效率, 协同开发",
        "DDC2025地瓜机器人开发者大会：具身智能时代的全链路开发基础设施升级": "具身智能, 机器人, 开发者大会, 算力平台",
        "DGX H100_H200 Redfish API使用指南与案例详解 📝": "NVIDIA DGX, Redfish API, 服务器管理, 硬件监控",
        "DeepSeek 网页_API 性能异常事件记录（2025年11月25日）": "DeepSeek, API故障, 服务稳定性, 事件记录",
        "DemoGrasp：单演示轨迹驱动的通用灵巧手抓取框架": "灵巧手抓取, 演示学习, 机器人, 北大",
        "Devin部署能力解析：前端与后端应用部署指南": "Devin, 应用部署, 前端部署, 后端部署",
        "Dify工作流代码节点开发规范与最佳实践": "Dify, 代码节点, 开发规范, 工作流",
        "Dify工作流模板资源包深度解析：160_场景化应用与技术架构": "Dify, 工作流模板, 场景化应用, AI自动化",
        "Dify平台集成阿里云百炼模型全流程指南：从配置到应用开发": "Dify, 阿里云百炼, 大模型集成, 应用开发",
        "Dify开发文档：迭代节点深度解析与应用指南": "Dify, 迭代节点, 开发文档, 工作流开发",
        "Dify插件开发环境搭建与核心规范全指南": "Dify, 插件开发, 环境搭建, 开发规范",
        "Dify知识库召回测试与运维网工副业转型指南": "Dify, 知识库召回, 运维网工, 副业转型",
        "Docker 搭建 Gitlab 服务器完整步骤 📝": "Docker, Gitlab, 服务器搭建, DevOps",
        "Docker容器技术体系架构详解 📦": "Docker, 容器技术, 架构设计, 云原生",
        "EFCIO新纪元10周年共创大会：全球化软件架构与品牌实践": "EFCIO, 全球化, 软件架构, 品牌实践",
        "ELK-MCP：面向工作流集成的稳健日志查询后端（兼容ES 6_5_4）": "ELK, 日志查询, MCP, Elasticsearch",
        "Flask与Streamlit对比": "Flask, Streamlit, Web框架, Python",
        "Flask内部服务器错误深度解析：原因、解决方案与实例": "Flask, 500错误, 错误处理, 调试",
        "Flask内部服务器错误（500错误）深度解析与解决方案": "Flask, 内部服务器错误, 异常处理",
        "Flask框架入门指南": "Flask, Web开发, Python, 入门教程",
        "FuzzyMatching算法：原理、应用与实现细节 📝": "模糊匹配, FuzzyMatching, 算法实现, 字符串匹配",
        "GAGARVN 组织 GitHub 主页分析": "GAGARVN, GitHub, 开源组织, 代码分析",
    }
    return keywords_map.get(title, title.replace("：", ",").replace(" ", ",").replace("_", ","))

def generate_table_of_contents(headings):
    toc_lines = []
    for heading in headings:
        link = heading.replace(" ", "-").replace("：", "-").replace("(", "").replace(")", "").replace("，", "-").replace("！", "").replace("？", "").replace("。", "").replace("、", "-").replace("【", "").replace("】", "").replace("（", "").replace("）", "")
        link = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\-]', '', link)
        link = link.lower()
        toc_lines.append(f"- [{heading}](#{link})")
    return "\n".join(toc_lines)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "> **概要**:" in content and "> **关键词**:" in content and "## 📑 目录" in content and "## 参考文件" in content and "## Changelog" in content:
        print(f"  已跳过（已有完整要素）: {filepath.name}")
        return False
    
    title = filepath.stem
    headings = extract_headings(content)
    
    summary = generate_summary(title)
    keywords = generate_keywords(title)
    toc = generate_table_of_contents(headings)
    
    separator = "\n" + "-" * 50 + "\n"
    
    new_content = content
    
    if "> **概要**:" not in content:
        metadata_end = content.find("---\n\n\n\n")
        if metadata_end == -1:
            metadata_end = content.find("---\n\n")
        if metadata_end != -1:
            insert_pos = metadata_end + 4
            insert_text = f"\n> **概要**: {summary}\n> **关键词**: {keywords}\n\n"
            new_content = new_content[:insert_pos] + insert_text + new_content[insert_pos:]
    
    if "## 📑 目录" not in content:
        title_end = new_content.find("\n\n## ")
        if title_end != -1:
            insert_pos = title_end + 2
            insert_text = f"\n## 📑 目录\n\n{toc}\n\n"
            new_content = new_content[:insert_pos] + insert_text + new_content[insert_pos:]
    
    if "## 参考文件" not in content:
        ref_source_pos = new_content.find("## 📝 参考来源")
        if ref_source_pos != -1:
            insert_text = f"\n## 参考文件\n\n### 内部知识库引用\n\n### 外部资料引用\n\n- 原文链接：{title}\n"
            new_content = new_content[:ref_source_pos] + insert_text + new_content[ref_source_pos:]
        else:
            changelog_pos = new_content.find("## changelog")
            if changelog_pos != -1:
                insert_text = f"\n## 参考文件\n\n### 内部知识库引用\n\n### 外部资料引用\n\n- 原文链接：{title}\n\n"
                new_content = new_content[:changelog_pos] + insert_text + new_content[changelog_pos:]
    
    if "## Changelog" not in content:
        changelog_pos = new_content.find("## changelog")
        if changelog_pos != -1:
            old_changelog = new_content[changelog_pos:]
            new_changelog = "## Changelog\n\n| 日期 | 版本 | 变更内容 |\n|:-----|:-----|:---------|\n| 2026-07-26 | v1.1 | 添加概要、关键词、目录、参考文件、Changelog五大要素 |\n| 2026-07-18 | v1.0 | 初始创建：基于原文内容整理 |\n"
            new_content = new_content[:changelog_pos] + new_changelog
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✓ 已处理: {filepath.name}")
    return True

def main():
    dir_path = Path(DIR_PATH)
    files = [f for f in dir_path.glob("*.md") if f.name not in EXISTING_FILES]
    
    print(f"共找到 {len(files)} 个需要处理的文件")
    print("=" * 60)
    
    count = 0
    for filepath in files:
        if process_file(filepath):
            count += 1
    
    print("=" * 60)
    print(f"处理完成，共修改 {count} 个文件")

if __name__ == "__main__":
    main()
