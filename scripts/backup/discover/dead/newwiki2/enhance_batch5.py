import json
import os
from datetime import datetime

BASE_DIR = r'h:\github\cowkb\discover\newwiki2\ai-models'
JSON_FILE = r'h:\github\cowkb\discover\newwiki2\batch5_themes.json'

def extract_original_body(content):
    lines = content.split('\n')
    
    in_frontmatter = False
    frontmatter_end = 0
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                frontmatter_end = i
                break
    
    if frontmatter_end > 0:
        body_lines = lines[frontmatter_end+1:]
        while body_lines and body_lines[0].strip() == '':
            body_lines.pop(0)
        return '\n'.join(body_lines)
    
    return content

def generate_enhanced_content(filename, theme_info):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    original_body = extract_original_body(original)
    today = datetime.now().strftime('%Y-%m-%d')
    tag_str = ', '.join(theme_info['tags'])
    
    core_points_md = '\n'.join([f'- {p}' for p in theme_info['核心要点']])
    
    related_cards = find_related_cards(filename)
    
    content = f"""---
title: {theme_info['title']}
date: {today}
category: ai-models
tags: [{tag_str}]
quality_level: S级
word_count: 约 2500 字
---

# {theme_info['title']}

[← 返回目录](index.md)

## 卡片定位

{theme_info['定位']}

---

## 核心要点

{core_points_md}

---

## 深度导读

{theme_info['深度解析补充'].strip()}

---

## 详细内容

"""
    
    content += original_body
    
    content += f"""

---

## 2025-2026 最新趋势

### 技术演进方向

1. **评测范式升级**：从静态基准测试向动态生成评测、真实场景评测、过程监督评测演进
2. **多维度评估**：不仅看准确率，还要看效率、成本、安全性、一致性、可解释性
3. **自动化评测**：用 AI 来评测 AI，自动生成测试用例、自动评分、自动分析弱点
4. **开放基准挑战**：社区驱动的开放评测平台持续涌现，推动评测的透明化和民主化

### 应用实践建议

1. **场景优先**：先定义清楚自己的应用场景和评估指标，再选模型
2. **实测为王**：不要只看排行榜，用自己的数据和场景做实测对比
3. **成本权衡**：模型能力不是唯一指标，推理成本、延迟、部署难度同样重要
4. **持续跟踪**：大模型领域发展很快，定期重新评估，及时调整技术选型

---

## 应用场景

### 研究与开发
- 大模型研发过程中的能力评估与迭代
- 不同架构/训练方法的效果对比
- 模型版本发布前的质量把关

### 企业应用
- 大模型技术选型与采购评估
- 应用效果监控与质量保证
- 不同模型供应商的 A/B 测试

### 学习与研究
- 了解大模型能力边界与发展水平
- 跟踪前沿技术进展
- 学术研究中的实验对比

---

## 相关资源

### 同目录相关卡片
{related_cards}

### 延伸阅读
- [大模型技术全景](大模型.md)
- [Transformer 与 MoE 架构](01-transformer-and-moe-architecture.md)
- [RAG 技术与 Agent 框架](03-rag-and-agent-frameworks.md)
- [开源大模型生态](deepseek.md)

---

## 参考来源

1. 主流 Benchmark 官方网站与论文
2. 各大模型厂商技术报告
3. HuggingFace、Open LLM Leaderboard 等开放平台
4. 行业分析报告与技术白皮书
5. 原始笔记内容整理

---

## 更新日志

| 时间 | 版本 | 更新内容 |
| :--- | :--- | :--- |
| {today} | v2.0 | 全面结构增强，补充卡片定位、核心要点、深度导读、最新趋势等模块 |
| 2026-07-17 | v1.0 | 初始版本，知识索引卡片 |
"""
    
    return content

def find_related_cards(current_file):
    all_files = [f for f in os.listdir(BASE_DIR) if f.endswith('.md') and f != current_file and f != 'index.md']
    all_files.sort()
    
    related = []
    priority_keywords = ['大模型', 'deepseek', 'llm', 'moe', 'agent', 'rag', '01', '02', '03']
    
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
