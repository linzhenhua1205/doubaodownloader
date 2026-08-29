import os
import re
import json

wiki_dir = r"h:\github\cowkb\discover\newwiki"

all_files_metadata = {
    "AI-Agent技术架构.md": {
        "title": "AI Agent 技术架构",
        "quality_level": "S+",
        "category": "人工智能",
        "tags": ["AI Agent", "智能体", "大模型应用", "多智能体", "RAG"]
    },
    "AI伦理与安全.md": {
        "title": "AI 伦理与安全",
        "quality_level": "S",
        "category": "人工智能",
        "tags": ["AI伦理", "AI安全", "对齐技术", "模型安全", "监管合规"]
    },
    "AI应用与落地实践.md": {
        "title": "AI 应用与落地实践",
        "quality_level": "S+",
        "category": "人工智能",
        "tags": ["AI应用", "落地实践", "企业数字化", "AIGC", "行业解决方案"]
    },
    "AI技能与职业发展.md": {
        "title": "AI 技能与职业发展",
        "quality_level": "S",
        "category": "职业发展",
        "tags": ["AI职业", "技能提升", "学习路径", "转型指南", "人才市场"]
    },
    "AI编程与开发工具.md": {
        "title": "AI 编程与开发工具",
        "quality_level": "S+",
        "category": "人工智能",
        "tags": ["AI编程", "开发工具", "代码生成", "Copilot", "IDE插件"]
    },
    "企业管理与运营.md": {
        "title": "企业管理与运营",
        "quality_level": "S+",
        "category": "企业管理",
        "tags": ["企业管理", "运营效率", "组织架构", "流程优化", "数字化转型"]
    },
    "大模型技术与原理.md": {
        "title": "大模型技术与原理",
        "quality_level": "S+",
        "category": "人工智能",
        "tags": ["大模型", "LLM", "Transformer", "预训练", "微调技术"]
    },
    "技术选型与方案对比.md": {
        "title": "技术选型与方案对比",
        "quality_level": "S+",
        "category": "技术架构",
        "tags": ["技术选型", "方案对比", "架构决策", "评估框架", "最佳实践"]
    },
    "数据与存储技术.md": {
        "title": "数据与存储技术",
        "quality_level": "S+",
        "category": "数据技术",
        "tags": ["数据存储", "数据库", "分布式存储", "数据仓库", "数据湖"]
    },
    "数据中心与基础设施.md": {
        "title": "数据中心与基础设施",
        "quality_level": "S+",
        "category": "基础设施",
        "tags": ["数据中心", "IDC", "基础设施", "云计算", "算力网络"]
    },
    "方法论与工具.md": {
        "title": "方法论与工具",
        "quality_level": "S+",
        "category": "工程方法",
        "tags": ["方法论", "工程实践", "开发工具", "项目管理", "效率提升"]
    },
    "服务器与硬件架构.md": {
        "title": "服务器与硬件架构",
        "quality_level": "S+",
        "category": "硬件技术",
        "tags": ["服务器", "硬件架构", "CPU", "GPU", "数据中心硬件"]
    },
    "网络与系统运维.md": {
        "title": "网络与系统运维",
        "quality_level": "S+",
        "category": "运维技术",
        "tags": ["网络技术", "系统运维", "DevOps", "监控告警", "自动化运维"]
    },
    "行业趋势与洞察.md": {
        "title": "行业趋势与洞察",
        "quality_level": "S+",
        "category": "行业分析",
        "tags": ["行业趋势", "技术洞察", "市场分析", "前沿技术", "产业发展"]
    },
    "其他_后端开发.md": {
        "title": "后端开发技术",
        "quality_level": "S",
        "category": "软件开发",
        "tags": ["后端开发", "服务端架构", "微服务", "云原生", "API设计"]
    },
    "其他_安全防护.md": {
        "title": "安全防护技术",
        "quality_level": "S",
        "category": "网络安全",
        "tags": ["网络安全", "安全防护", "渗透测试", "漏洞防护", "安全运维"]
    },
    "其他_数学算法.md": {
        "title": "数学与算法",
        "quality_level": "S+",
        "category": "计算机科学",
        "tags": ["数学基础", "算法设计", "数据结构", "计算理论", "优化方法"]
    },
    "其他_数据科学.md": {
        "title": "数据科学",
        "quality_level": "S+",
        "category": "数据技术",
        "tags": ["数据科学", "数据分析", "机器学习", "统计分析", "数据可视化"]
    },
    "其他_生活文化.md": {
        "title": "生活与文化",
        "quality_level": "S",
        "category": "综合知识",
        "tags": ["生活百科", "文化历史", "社会观察", "人文素养", "思维方式"]
    },
    "其他_综合技术.md": {
        "title": "综合技术",
        "quality_level": "S+",
        "category": "综合技术",
        "tags": ["综合技术", "跨领域", "技术融合", "系统思维", "工程实践"]
    },
    "其他_编程语言.md": {
        "title": "编程语言",
        "quality_level": "S+",
        "category": "软件开发",
        "tags": ["编程语言", "Python", "Java", "Go", "Rust"]
    },
    "其他_网络协议.md": {
        "title": "网络协议",
        "quality_level": "S",
        "category": "网络技术",
        "tags": ["网络协议", "TCP/IP", "HTTP", "DNS", "网络安全"]
    },
    "其他_职场管理.md": {
        "title": "职场管理",
        "quality_level": "S",
        "category": "职业发展",
        "tags": ["职场技能", "管理方法", "职业发展", "沟通技巧", "团队协作"]
    }
}

def clean_header_meta(content):
    lines = content.split('\n')
    result_lines = []
    found_h1 = False
    after_h1_skipping = False
    
    for line in lines:
        if not found_h1:
            if line.startswith('# '):
                found_h1 = True
                result_lines.append(line)
                after_h1_skipping = True
            continue
        
        if after_h1_skipping:
            if line.startswith('>'):
                continue
            if re.match(r'^---\s*$', line):
                continue
            if line.strip() == '':
                continue
            after_h1_skipping = False
            result_lines.append('')
            result_lines.append(line)
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)

def add_frontmatter(content, metadata):
    char_count = len(content)
    
    frontmatter = f"""---
title: {metadata['title']}
date: 2026-07-22
quality_level: {metadata['quality_level']}
word_count: 约{char_count:,}字
category: {metadata['category']}
tags: [{', '.join(metadata['tags'])}]
---

"""
    return frontmatter + content

def process_file(filename, metadata):
    filepath = os.path.join(wiki_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    
    if content.startswith('---\n'):
        parts = content.split('---\n', 2)
        if len(parts) >= 3:
            content = parts[2].lstrip('\n')
    
    content = clean_header_meta(content)
    content = add_frontmatter(content, metadata)
    
    new_len = len(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return original_len, new_len

results = []

for filename, metadata in sorted(all_files_metadata.items()):
    if os.path.exists(os.path.join(wiki_dir, filename)):
        try:
            orig_len, new_len = process_file(filename, metadata)
            diff = new_len - orig_len
            results.append({
                "filename": filename,
                "original_chars": orig_len,
                "new_chars": new_len,
                "diff_chars": diff,
                "status": "success"
            })
            sign = "+" if diff >= 0 else ""
            print(f"✅ {filename} - {sign}{diff:,} 字")
        except Exception as e:
            results.append({
                "filename": filename,
                "error": str(e),
                "status": "error"
            })
            print(f"❌ {filename} - 错误: {e}")
    else:
        print(f"⚠️  {filename} - 文件不存在")

print(f"\n处理完成: {len(results)} 个文件")
success_count = sum(1 for r in results if r['status'] == 'success')
print(f"成功: {success_count} 个")
print(f"失败: {sum(1 for r in results if r['status'] == 'error')} 个")

total_orig = sum(r['original_chars'] for r in results if r['status'] == 'success')
total_new = sum(r['new_chars'] for r in results if r['status'] == 'success')
print(f"总字数变化: {total_orig:,} → {total_new:,} ({total_new - total_orig:+,})")

with open(os.path.join(wiki_dir, 'frontmatter_add_results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
