import os
import json

# 候选文章列表 - AI与机器学习类
ai_candidates = [
    r'site\AI与机器学习\2025 开发者AI编程工具选型推荐：从技术适配到场景应用的落地选型指南.md',
    r'site\AI与机器学习\2025-2026年AI行业发展趋势及企业部署挑战分析.md',
    r'site\AI与机器学习\2025世界人工智能大会（WAIC 2025）全景洞察.md',
    r'site\AI与机器学习\2025Q3美国科技巨头AI投资与变现报告.md',
    r'site\AI与机器学习\100位老年人与大模型的1年实践：用「活法」定义「算法」.md',
    r'site\AI与机器学习\2025京东11_11成交额创新高及AI应用成果.md',
    r'site\AI与机器学习\2025天猫双11：AI与大消费驱动的商业模式变革.md',
    r'site\AI与机器学习\2025全球AI产业研报：技术演进、生态重构与商业突围.md',
]

# 系统运维类候选
ops_candidates = [
    r'site\系统与运维\2025CMDB平台建设与选型指南：从数据治理到智能运维的价值实现.md',
    r'site\系统与运维\2025H1中国服务器市场格局分析（IDC报告）.md',
    r'site\系统与运维\Ansible自动化运维：从原理到企业级实践的深度解构.md',
    r'site\系统与运维\CMDB与Zabbix监控系统融合方案与运维思考 🛠️.md',
    r'site\系统与运维\Docker Compose 性能优化与资源管理全解析.md',
    r'site\系统与运维\FusionDirector IT智能运维软件深度解析：功能特性与技术优势.md',
]

# 行业动态类候选
industry_candidates = [
    r'site\行业动态\2025年世界互联网大会乌镇峰会成果总结.md',
    r'site\行业动态\2025年资本市场与产业趋势全景分析.md',
    r'site\行业动态\2025年美国能源转型报告：光伏爆发引领电力结构重塑.md',
    r'site\行业动态\2025美团机器人研究院学术年会全记录：具身智能的技术突破与产业落地.md',
    r'site\行业动态\2025中国具身智能机器人大会核心洞察与产业趋势.md',
    r'site\行业动态\Anthropic与微软、英伟达达成战略合作：150亿美元投资_300亿美元算力采购.md',
    r'site\行业动态\AMD CEO苏姿丰谈人工智能泡沫担忧：投资不足比过度更危险.md',
    r'site\行业动态\Arm 收购 DreamBig 拓展数据中心业务并发布强劲财报.md',
]

def analyze_article(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    char_count = len(content.replace(' ', '').replace('\n', ''))
    has_good_summary = '核心要点' in content and '关键数据' in content
    table_count = content.count('|:---')
    has_template = '规模化落地：2026年AI从技术验证转向生产级应用' in content
    
    quality_level = 'unknown'
    if 'quality_level: S' in content:
        quality_level = 'S'
    elif 'quality_level: A' in content:
        quality_level = 'A'
    elif 'quality_level: B' in content:
        quality_level = 'B'
    
    return {
        'file': os.path.basename(filepath),
        'path': filepath,
        'char_count': char_count,
        'table_count': table_count,
        'quality_level': quality_level,
        'has_template': has_template,
        'has_good_summary': has_good_summary
    }

print('=== AI与机器学习类候选文章 ===')
for f in ai_candidates:
    result = analyze_article(f)
    if result:
        print(f"  {result['file'][:50]:50s} | 字数:{result['char_count']:5d} | 表格:{result['table_count']:2d} | 质量:{result['quality_level']} | 模板化:{result['has_template']}")
    else:
        print(f"  [不存在] {f}")

print()
print('=== 系统运维类候选文章 ===')
for f in ops_candidates:
    result = analyze_article(f)
    if result:
        print(f"  {result['file'][:50]:50s} | 字数:{result['char_count']:5d} | 表格:{result['table_count']:2d} | 质量:{result['quality_level']} | 模板化:{result['has_template']}")
    else:
        print(f"  [不存在] {f}")

print()
print('=== 行业动态类候选文章 ===')
for f in industry_candidates:
    result = analyze_article(f)
    if result:
        print(f"  {result['file'][:50]:50s} | 字数:{result['char_count']:5d} | 表格:{result['table_count']:2d} | 质量:{result['quality_level']} | 模板化:{result['has_template']}")
    else:
        print(f"  [不存在] {f}")
