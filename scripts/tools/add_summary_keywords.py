import os
import re
from typing import List, Tuple

TARGET_DIR = r"h:\github\cowkb\discover\site\产品与设计"
EXCLUDE_FILES = [
    "index.md",
    "2024年主流人形机器人产品对比与技术洞察 🤖.md",
    "华为智能情感陪伴电子宠物“憨憨”产品详情.md",
    "华为Pura80双十一价格调整与产品解析.md",
    "Frore Systems 推出数据中心级 DLC 冷板产品 LiquidJet.md"
]

def get_files_to_process() -> List[str]:
    """获取需要处理的文件列表"""
    files = []
    for f in os.listdir(TARGET_DIR):
        if f.endswith(".md") and f not in EXCLUDE_FILES:
            files.append(os.path.join(TARGET_DIR, f))
    return files

def has_summary(content: str) -> bool:
    """检查文件是否已有概要"""
    return re.search(r"> \*\*概要\*\*:", content) is not None

def extract_title(content: str) -> str:
    """从文件中提取标题"""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""

def extract_core_points(content: str) -> str:
    """提取核心要点部分作为生成摘要的依据"""
    match = re.search(r"##\s*💡\s*核心要点(.+?)(?=\n##|$)", content, re.DOTALL)
    if match:
        return match.group(1).strip()[:500]
    return ""

def generate_summary(title: str, core_points: str, content: str) -> str:
    """基于内容生成一句话概要（≤100字）"""
    # 优先使用核心要点
    if core_points:
        # 提取前几个要点
        points = re.findall(r"- (.+?)(?=\n-|\n$)", core_points)[:2]
        if points:
            summary = "；".join(p[:30] for p in points)
            return summary[:100]
    
    # 基于标题和内容生成
    if title:
        base_summary = f"{title}"
        return base_summary[:100]
    
    # 使用文件开头内容
    first_paragraph = content[:200].replace("\n", " ").strip()
    return first_paragraph[:100]

def generate_keywords(title: str, content: str) -> List[str]:
    """生成5个关键词"""
    keywords = []
    
    # 从标题提取
    title_keywords = re.findall(r"([\u4e00-\u9fa5a-zA-Z0-9_]+)", title)
    for kw in title_keywords[:3]:
        if len(kw) >= 2 and kw not in keywords:
            keywords.append(kw)
    
    # 从分类标签提取
    category_match = re.search(r"> \s*🏷️\s*\*\*分类\*\*:\s*(.+?)(?=\n|$)", content)
    if category_match:
        categories = [c.strip() for c in category_match.group(1).split(",")]
        for cat in categories[:3]:
            if cat and cat not in keywords:
                keywords.append(cat)
    
    # 从内容提取常见技术词汇
    tech_terms = [
        "Dify", "工作流", "知识库", "AI", "大模型", "RAG", "插件", 
        "自动化", "开发", "设计", "产品", "智能", "机器人", "系统",
        "运维", "云计算", "API", "工具", "模板", "变量", "节点",
        "部署", "配置", "解析", "优化", "实践", "指南", "教程",
        "架构", "功能", "应用", "案例", "数据", "处理", "生成",
        "检索", "召回", "参数", "插件", "导出", "循环", "执行",
        "性能", "Excel", "图文", "Word", "飞书", "多维表格", "文案",
        "小红书", "产品管理", "NioPD", "Sonar", "QuickAdd", "KBNF",
        "ECCO", "云店", "导购", "嵌入式", "无障碍", "可用性",
        "世界模型", "Marble", "FLUX", "图像生成", "创意", "工作流"
    ]
    
    for term in tech_terms:
        if term in content and term not in keywords:
            keywords.append(term)
        if len(keywords) >= 5:
            break
    
    # 确保至少有5个关键词，补充通用词汇
    while len(keywords) < 5:
        defaults = ["产品设计", "AI应用", "技术实践", "智能系统", "工作流"]
        for d in defaults:
            if d not in keywords:
                keywords.append(d)
                break
    
    return keywords[:5]

def find_insert_position(content: str) -> int:
    """找到插入位置：在 '## 💼 企业案例与应用实践' 之前"""
    match = re.search(r"\n##\s*💼\s*企业案例与应用实践", content)
    if match:
        return match.start()
    # 如果没有找到，则在文件末尾的参考来源或changelog之前
    match = re.search(r"\n##\s*(📖\s*)?参考来源", content)
    if match:
        return match.start()
    # 如果都没有，在最后一个 --- 分隔符之前
    matches = list(re.finditer(r"\n---\n", content))
    if matches:
        return matches[-1].start()
    # 否则在文件末尾
    return len(content)

def add_summary_and_keywords(file_path: str):
    """为单个文件添加概要和关键词"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if has_summary(content):
        print(f"✓ 跳过（已有概要）: {os.path.basename(file_path)}")
        return
    
    title = extract_title(content)
    core_points = extract_core_points(content)
    
    summary = generate_summary(title, core_points, content)
    keywords = generate_keywords(title, content)
    
    insert_pos = find_insert_position(content)
    
    # 构建要插入的内容
    insert_content = f"\n---\n\n> **概要**: {summary}\n> **关键词**: {' · '.join(keywords)}\n\n"
    
    new_content = content[:insert_pos] + insert_content + content[insert_pos:]
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✓ 已处理: {os.path.basename(file_path)}")
    print(f"  概要: {summary[:50]}...")
    print(f"  关键词: {' · '.join(keywords)}")

def main():
    files = get_files_to_process()
    print(f"共找到 {len(files)} 个需要处理的文件")
    
    for file_path in files:
        try:
            add_summary_and_keywords(file_path)
        except Exception as e:
            print(f"✗ 处理失败: {os.path.basename(file_path)} - {e}")
    
    print("\n处理完成！")

if __name__ == "__main__":
    main()