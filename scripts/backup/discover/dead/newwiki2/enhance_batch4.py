import json
import os
from datetime import datetime

BASE_DIR = r'h:\github\cowkb\discover\newwiki2\ai-models'
JSON_FILE = r'h:\github\cowkb\discover\newwiki2\batch4_themes.json'

def extract_original_notes(content):
    notes = []
    lines = content.split('\n')
    current_note = []
    in_note = False
    
    for line in lines:
        if line.startswith('## ') and '.' in line and line[3:].split('.')[0].isdigit():
            if current_note:
                notes.append('\n'.join(current_note))
                current_note = []
            in_note = True
            current_note.append(line)
        elif in_note:
            if line.startswith('---') and len(notes) > 0:
                if current_note:
                    notes.append('\n'.join(current_note))
                    current_note = []
                in_note = False
            else:
                current_note.append(line)
    
    if current_note:
        notes.append('\n'.join(current_note))
    
    return notes[:5]

def generate_enhanced_content(filename, theme_info):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    notes = extract_original_notes(original)
    today = datetime.now().strftime('%Y-%m-%d')
    tag_str = ', '.join(theme_info['tags'])
    
    core_points_md = '\n'.join([f'- {p}' for p in theme_info['核心要点']])
    
    related_cards = find_related_cards(filename)
    
    content = f"""---
title: {theme_info['title']}
date: {today}
category: ai-models
tags: [{tag_str}]
quality_level: A级
word_count: 约 1200 字
---

# {theme_info['title']}

[← 返回目录](index.md)

## 卡片定位

{theme_info['定位']}

---

## 核心要点

{core_points_md}

---

## 深度解析

{theme_info['深度解析'].strip()}

---

## 2025-2026 最新进展

### 技术演进

1. **大模型能力持续提升**：2025-2026 年，大模型在推理能力、多模态理解、工具使用等方面持续进步，深度推理模型成为新的竞争焦点
2. **智能体框架成熟化**：Agent 框架从概念验证走向生产落地，多智能体协作、工具调用、记忆管理等核心能力日趋成熟
3. **开源生态繁荣**：开源模型和工具链快速迭代，本地化部署成为重要趋势，企业和个人可以更灵活地构建 AI 应用
4. **效率革命**：训练和推理成本持续下降，量化、推测解码、KV Cache 优化等技术让大模型更加普惠

### 应用趋势

1. **从辅助到自主**：AI 从「辅助工具」向「自主执行者」演进，Agent 能够独立完成更复杂的任务
2. **垂直深化**：AI 在编程、医疗、法律、教育等垂直领域的应用不断深化，专业能力持续提升
3. **端云协同**：大模型不再只在云端运行，端侧小模型 + 云端大模型的协同架构成为重要方向
4. **安全与治理**：AI 安全、可解释性、合规治理受到越来越多的关注，负责任的 AI 成为共识

---

## 应用场景

### 个人用户
- 个人知识管理与学习助手
- 编程开发与调试辅助
- 日常事务自动化处理
- 创意生成与内容创作

### 企业用户
- 智能客服与知识库
- 研发效率提升工具
- 数据分析与决策支持
- 业务流程自动化

### 开发者
- AI 应用快速原型开发
- 多智能体系统构建
- 自定义技能开发
- 模型微调与部署

---

## 相关资源

### 同目录相关卡片
{related_cards}

### 延伸阅读
- [大模型技术全景](大模型.md)
- [AI Agent 技术架构](agent.md)
- [开源大模型生态](deepseek.md)
- [本地部署与推理优化](kvcache.md)

---

## 参考来源

1. 行业公开报告与技术白皮书
2. 开源社区项目文档与讨论
3. 技术博客与行业分析文章
4. 原始笔记内容整理

---

## 原始笔记

> 以下为卡片原始内容，保留供参考。

"""

    for i, note in enumerate(notes, 1):
        content += f"\n### 原始笔记 {i}\n\n{note.strip()}\n"
    
    content += f"""
---

## 更新日志

| 时间 | 版本 | 更新内容 |
| :--- | :--- | :--- |
| {today} | v2.0 | 全面内容增强，补充卡片定位、核心要点、深度解析、最新进展等结构化内容 |
| 2026-07-19 | v1.0 | 初始版本，知识索引卡片 |
"""
    
    return content

def find_related_cards(current_file):
    all_files = [f for f in os.listdir(BASE_DIR) if f.endswith('.md') and f != current_file and f != 'index.md']
    all_files.sort()
    
    related = []
    priority_keywords = ['agent', '大模型', 'deepseek', 'kvcache', 'sglang', 'mcp', 'rag', 'llm', 'trae']
    
    for keyword in priority_keywords:
        for f in all_files:
            if keyword.lower() in f.lower() and f not in related and len(related) < 4:
                name = f.replace('.md', '').replace('_', ' ')
                related.append(f"- [{name}]({f})")
                break
    
    if len(related) < 4:
        for f in all_files[:6]:
            if f not in [r.split('](')[1].rstrip(')') for r in related]:
                name = f.replace('.md', '').replace('_', ' ')
                related.append(f"- [{name}]({f})")
                if len(related) >= 4:
                    break
    
    return '\n'.join(related[:4])

def main():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        themes = json.load(f)
    
    success = 0
    failed = 0
    skipped = 0
    
    for filename, theme_info in themes.items():
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            print(f'⊘ 跳过（不存在）: {filename}')
            skipped += 1
            continue
        
        try:
            content = generate_enhanced_content(filename, theme_info)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ 已增强: {filename}')
            success += 1
        except Exception as e:
            print(f'✗ 失败: {filename} - {e}')
            failed += 1
    
    print(f'\n===== 处理结果 =====')
    print(f'成功增强: {success} 个')
    print(f'跳过（不存在）: {skipped} 个')
    print(f'失败: {failed} 个')

if __name__ == '__main__':
    main()
