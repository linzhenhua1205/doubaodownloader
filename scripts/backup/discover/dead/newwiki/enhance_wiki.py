import os
import re
from datetime import datetime

WIKI_DIR = r"h:\github\cowkb\discover\newwiki"

CORE_FILES = [
    "服务器与硬件架构.md",
    "数据中心与基础设施.md",
    "网络与系统运维.md",
    "方法论与工具.md",
]

MODULE_DESCRIPTIONS = {
    "技术实现": "具体技术方案、实现细节、代码示例",
    "其他": "综合类、跨领域问题",
    "基础概念": "核心定义、原理、基础理论",
    "工具框架": "常用工具、框架、平台使用",
    "应用场景": "行业案例、落地实践、场景方案",
    "发展趋势": "技术演进、未来方向、行业动态",
    "对比分析": "方案对比、技术选型、优劣分析",
    "性能优化": "性能调优、瓶颈分析、最佳实践",
    "实践建议": "实操指南、经验总结、避坑指南",
    "企业管理": "组织管理、战略规划、运营效率",
    "职业发展": "技能提升、 career path、行业洞察",
    "安全防护": "安全策略、风险防控、合规要求",
    "数学算法": "算法原理、数学模型、理论基础",
    "数据科学": "数据分析、机器学习、统计方法",
    "生活文化": "生活方式、文化趋势、社会观察",
    "综合技术": "跨领域技术、技术融合、综合应用",
    "编程语言": "语言特性、编程范式、开发技巧",
    "网络协议": "协议原理、网络架构、通信机制",
    "职场管理": "职场技能、团队管理、职业规划",
}


def parse_theme_distribution(content):
    match = re.search(r"\*\*主题分布\*\*：(.+?)\n", content)
    if not match:
        return [], 0

    distribution_str = match.group(1).strip()
    items = re.findall(r"([^(]+)\((\d+)个\)", distribution_str)

    themes = []
    total = 0
    for name, count in items:
        name = name.strip().lstrip(',').strip()
        count = int(count)
        total += count
        themes.append((name, count))

    themes.sort(key=lambda x: x[1], reverse=True)
    return themes, total


def generate_knowledge_structure(themes, total):
    module_count = len(themes)
    lines = [
        "## 知识体系结构",
        "",
        f"本专题知识分为以下 {module_count} 大模块，共 {total} 个问题：",
        "",
        "| 模块 | 问题数 | 占比 | 核心内容 |",
        "|------|:------:|:----:|:---------|",
    ]

    for name, count in themes:
        percentage = (count / total * 100) if total > 0 else 0
        desc = MODULE_DESCRIPTIONS.get(name, "相关领域知识与实践")
        lines.append(f"| {name} | {count} | {percentage:.1f}% | {desc} |")

    lines.append("")
    return "\n".join(lines)


def generate_quick_nav(themes):
    lines = [
        "## 快速导航",
        "",
        "按主题模块快速跳转到对应内容：",
        "",
    ]

    for name, count in themes:
        anchor = name  # 问题解答中的章节标题
        lines.append(f"- [{name}（{count}个问题）](#{anchor})")

    lines.append("")
    return "\n".join(lines)


def extract_questions(content, max_questions=15):
    questions = []
    pattern = r"\*\*Q\d+\.\s*(.+?)\*\*"

    for match in re.finditer(pattern, content):
        q_text = match.group(1).strip()
        q_pos = match.start()

        if q_text and len(q_text) > 5:
            questions.append((q_text, q_pos))
            if len(questions) >= max_questions * 3:
                break

    selected = []
    keywords_importance = [
        "什么是", "如何", "怎么", "为什么", "原理", "架构",
        "对比", "区别", "选型", "最佳实践", "优化", "趋势",
        "核心", "关键", "入门", "基础", "指南", "方法",
    ]

    scored = []
    for q_text, q_pos in questions:
        score = 0
        q_lower = q_text.lower()
        for kw in keywords_importance:
            if kw in q_lower:
                score += 1
        scored.append((score, q_text, q_pos))

    scored.sort(key=lambda x: x[0], reverse=True)

    for _, q_text, q_pos in scored[:max_questions]:
        selected.append(q_text)

    return selected


def generate_core_questions(content, filename):
    questions = extract_questions(content, max_questions=12)
    if not questions:
        return ""

    lines = [
        "## 核心问题精选",
        "",
        "以下是本专题最具代表性的核心问题，建议优先阅读：",
        "",
    ]

    for i, q in enumerate(questions, 1):
        summary = q[:50] + "..." if len(q) > 50 else q
        lines.append(f"{i}. **{q}**")

    lines.append("")
    lines.append("> 💡 更多详细解答请查看下方「问题解答」章节")
    lines.append("")
    return "\n".join(lines)


def generate_core_concepts_intro(topic_name, themes):
    theme_names = "、".join([t[0] for t in themes[:5]])
    return (
        "## 核心概念\n"
        "\n"
        f"> 💡 以下为按主题整理的核心概念问答，涵盖{topic_name}领域的关键知识点。"
        "建议结合上方的知识体系结构按需查阅。\n"
        "\n"
    )


def process_file(filepath):
    filename = os.path.basename(filepath)
    print(f"处理文件: {filename}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    themes, total = parse_theme_distribution(content)
    if not themes:
        print(f"  警告: 未找到主题分布，跳过")
        return False

    topic_match = re.search(r"# (.+?)\n", content)
    topic_name = topic_match.group(1).strip() if topic_match else "本专题"

    knowledge_structure = generate_knowledge_structure(themes, total)
    quick_nav = generate_quick_nav(themes)
    core_concepts_intro = generate_core_concepts_intro(topic_name, themes)

    is_core_file = filename in CORE_FILES

    if is_core_file:
        core_questions = generate_core_questions(content, filename)
    else:
        core_questions = ""

    if "## 核心概念" not in content:
        print(f"  警告: 未找到核心概念章节，跳过")
        return False

    if "## 知识体系结构" in content:
        print(f"  跳过: 已存在知识体系结构")
        return False

    insert_content = knowledge_structure + "\n---\n\n" + quick_nav + "\n---\n\n"
    if is_core_file and core_questions:
        insert_content += core_questions + "\n---\n\n"

    new_content = content.replace("## 核心概念", insert_content + "## 核心概念", 1)

    new_content = re.sub(
        r"## 核心概念\n\n",
        "## 核心概念\n\n"
        f"> 💡 以下为按主题整理的核心概念问答，涵盖{topic_name}领域的关键知识点。"
        "建议结合上方的知识体系结构按需查阅。\n\n",
        new_content,
        count=1
    )

    today = datetime.now().strftime("%Y-%m-%d")
    changelog_entry = f"### {today}\n"
    changelog_entry += "- 新增「知识体系结构」章节，可视化展示各模块问题分布\n"
    changelog_entry += "- 新增「快速导航」章节，便于按主题模块跳转\n"
    if is_core_file:
        changelog_entry += "- 新增「核心问题精选」章节，推荐高价值问题优先阅读\n"
    changelog_entry += "- 增强「核心概念」章节引导说明，提升阅读体验\n"

    if "## 变更记录" in new_content:
        new_content = new_content.replace(
            "## 变更记录\n\n",
            "## 变更记录\n\n" + changelog_entry + "\n",
            1
        )
    else:
        new_content += "\n\n---\n\n## 变更记录\n\n" + changelog_entry

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  完成: 模块数={len(themes)}, 总问题数={total}, 核心文件={'是' if is_core_file else '否'}")
    return True


def main():
    files = [
        "AI-Agent技术架构.md",
        "AI伦理与安全.md",
        "AI应用与落地实践.md",
        "AI技能与职业发展.md",
        "AI编程与开发工具.md",
        "企业管理与运营.md",
        "其他_后端开发.md",
        "其他_安全防护.md",
        "其他_数学算法.md",
        "其他_数据科学.md",
        "其他_生活文化.md",
        "其他_综合技术.md",
        "其他_编程语言.md",
        "其他_网络协议.md",
        "其他_职场管理.md",
        "大模型技术与原理.md",
        "技术选型与方案对比.md",
        "数据与存储技术.md",
        "数据中心与基础设施.md",
        "方法论与工具.md",
        "服务器与硬件架构.md",
        "网络与系统运维.md",
        "行业趋势与洞察.md",
    ]

    success_count = 0
    fail_count = 0

    for filename in files:
        filepath = os.path.join(WIKI_DIR, filename)
        if not os.path.exists(filepath):
            print(f"文件不存在: {filename}")
            fail_count += 1
            continue

        try:
            if process_file(filepath):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  错误: {e}")
            fail_count += 1

    print(f"\n{'='*50}")
    print(f"处理完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
