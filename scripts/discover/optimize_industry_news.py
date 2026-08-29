#!/usr/bin/env python3
import os
import re
from pathlib import Path

def extract_headings(content):
    headings = []
    pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
    for match in pattern.finditer(content):
        level = len(match.group(1))
        title = match.group(2).strip()
        if level <= 3:
            headings.append((level, title))
    return headings

def generate_toc(headings):
    toc_lines = ["## 📑 目录", ""]
    for level, title in headings:
        link = title.replace(' ', '-').replace(':', '').replace('？', '').replace('！', '').replace('（', '').replace('）', '')
        link = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\-]', '', link).lower()
        indent = "  " * (level - 1)
        toc_lines.append(f"{indent}- [{title}](#{link})")
    toc_lines.append("")
    return '\n'.join(toc_lines)

def add_summary_and_keywords(content, title):
    keyword_map = {
        "机器人": ["人形机器人", "具身智能", "AI机器人", "Robotics"],
        "人工智能": ["AI", "大模型", "机器学习", "深度学习"],
        "芯片": ["半导体", "CPU", "GPU", "AI芯片"],
        "融资": ["投资", "VC", "创业", "资本市场"],
        "GIS": ["地理信息", "空间智能", "遥感"],
        "服装": ["时尚", "供应链", "纺织"],
        "电商": ["数字营销", "直播带货", "电商平台"],
        "互联网大会": ["乌镇峰会", "科技大会", "数字经济"],
        "6G": ["通信", "网络", "5G"],
        "光伏": ["新能源", "太阳能", "能源转型"],
        "存储": ["SSD", "内存", "闪存"],
        "内存": ["DRAM", "存储芯片", "HBM"],
        "云": ["云计算", "云服务", "AWS"],
        "数据中心": ["IDC", "超算", "算力"],
        "具身智能": ["物理AI", "机器人", "Agent"],
        "技术趋势": ["Gartner", "战略技术", "未来趋势"],
        "开源": ["Open Source", "GitHub", "社区"],
        "量化交易": ["金融科技", "算法交易", "资本市场"],
        "微显示": ["MicroLED", "AR", "VR"],
        "编译": ["编译器", "优化", "LLVM"],
        "图像处理": ["计算机视觉", "图像识别", "CNN"],
    }
    
    keywords = []
    for key, values in keyword_map.items():
        if key in title:
            keywords.extend(values)
    keywords = list(set(keywords))
    
    summary_pattern = re.compile(r'> \*\*概要\*\*:', re.MULTILINE)
    if not summary_pattern.search(content):
        summary = f"> **概要**: {title[:50]}..." if len(title) > 50 else f"> **概要**: {title}"
        content = content.replace('> 📅', f'{summary}\n> 📅')
    
    keyword_pattern = re.compile(r'> \*\*关键词\*\*:', re.MULTILINE)
    if not keyword_pattern.search(content):
        keyword_str = ', '.join(keywords[:5]) if keywords else '行业动态, 技术趋势'
        content = content.replace('> 📅', f'> **关键词**: {keyword_str}\n> 📅')
    
    return content

def add_toc(content):
    headings = extract_headings(content)
    toc = generate_toc(headings)
    
    toc_pattern = re.compile(r'## 📑 目录', re.MULTILINE)
    if toc_pattern.search(content):
        return content
    
    lines = content.split('\n')
    
    insert_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('## ') and i > 0:
            insert_idx = i
            break
    
    if insert_idx != -1:
        lines.insert(insert_idx, '')
        lines.insert(insert_idx, toc)
        content = '\n'.join(lines)
    
    return content

def add_reference_section(content):
    if '## 参考文件' not in content and '## 参考来源' not in content:
        references = """
## 参考文件

### 内部知识库引用
- [行业趋势与洞察](../../knowledge/01_survey/industry-research/)
- [AI应用与落地实践](../../knowledge/01_survey/ai-apps/)

### 外部资料引用
- 原文链接（见文首）
- 行业公开报告与分析
"""
        content = content.replace('## 📝 Changelog', references + '\n## 📝 Changelog')
    return content

def add_changelog(content):
    if '## 📝 Changelog' not in content:
        changelog = """

## 📝 Changelog

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2025 | 初始版本，原文基础内容 |
| v2.0 | 2026-07-26 | 深度增强版：添加目录、概要、关键词、参考文件、知识关联 |
"""
        content += changelog
    return content

def add_knowledge_links(content, filename):
    if '## 🔗 知识关联' not in content:
        links = """

---

## 🔗 知识关联

### 相关知识点
- [[科技行业]] - 科技行业相关知识与实践指南
- [[产业趋势]] - 产业趋势相关知识与实践指南
- [[商业动态]] - 商业动态相关知识与实践指南

### 延伸阅读
同目录下相关文章推荐：

### 关键词标签
#行业动态 #科技趋势

### 内容评级
- ⭐ 重要性：4/5
- 📊 深度：4/5
- 🔄 时效性：4/5
"""
        content += links
    return content

def optimize_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else ""
        
        content = add_summary_and_keywords(content, title)
        content = add_toc(content)
        content = add_reference_section(content)
        content = add_changelog(content)
        content = add_knowledge_links(content, filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"优化成功: {filepath}"
    except Exception as e:
        return False, f"优化失败: {filepath} - {str(e)}"

def main():
    directory = r'h:\github\cowkb\discover\site\行业动态'
    md_files = sorted(Path(directory).glob('*.md'))
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    results = []
    
    for filepath in md_files:
        if filepath.name == 'index.md':
            skipped_count += 1
            continue
        
        print(f"正在处理: {filepath.name}")
        success, msg = optimize_file(str(filepath))
        results.append(msg)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*60)
    print("优化完成报告")
    print("="*60)
    print(f"总文件数: {len(md_files)}")
    print(f"跳过(index.md): {skipped_count}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print("="*60)
    
    if fail_count > 0:
        print("\n失败列表:")
        for msg in results:
            if "失败" in msg:
                print(f"  {msg}")

if __name__ == '__main__':
    main()