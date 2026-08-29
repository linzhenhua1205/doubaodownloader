import re

def generate_keywords(title, content):
    title_clean = re.sub(r'[🚀🔍📊📝📋🛠️💡🌍🔗📚📖]', '', title)
    
    primary_keywords = [
        ('OKR', ['OKR', '目标管理', 'KPI']),
        ('知识库', ['知识库', '知识系统', '知识管理平台', '企业知识库', '知识库搭建']),
        ('知识图谱', ['知识图谱', '图数据库', '图谱', 'GraphRAG', 'Memgraph', 'Kuzu']),
        ('RAG', ['RAG', '检索增强生成', '向量检索', '知识库问答']),
        ('笔记工具', ['OneNote', '笔记工具', '笔记软件', '语雀', 'Notion']),
        ('AI编程', ['AI编程', 'Agent', 'Copilot', '智能体工程']),
        ('效能提升', ['10倍效率', '程序员效能', '效能提升', '生产力提升']),
        ('FPGA', ['FPGA', '可编程逻辑']),
        ('项目管理', ['需求估算', '需求管理', '任务管理']),
        ('团队管理', ['团队管理', '人才管理', '组织管理']),
        ('学习方法', ['学习方案', '技能提升', '个人成长']),
        ('工具评测', ['工具评测', '工具选型', '工具对比', '深度评测']),
    ]
    
    keywords = []
    
    for canonical, variants in primary_keywords:
        for v in variants:
            if v.lower() in title_clean.lower():
                if canonical not in keywords:
                    keywords.append(canonical)
                break
    
    if len(keywords) < 3:
        title_words = re.findall(r'[\u4e00-\u9fff]{2,}', title_clean)
        skip_words = [
            '指南', '解析', '研究', '笔记', '方法', '系统', '技术', '实践', '深度', '全景', 
            '核心', '全流程', '入门', '进阶', '高级', '从零到', '到专家', '系统路线图',
            '从', '到', '的', '与', '及', '和', '中', '上', '下', '内', '外', '前', '后',
            '第一', '第二', '第三', '一个', '一种', '一次', '一些',
            '时代', '背景', '上下文', '最新', '进展', '解读', '摘要', '执行',
            '管理', '效能', '提升', '驱动', '组织', '目标', '路径', '进化',
            '企业级', '开源', '主流', '解决方案', '分析', '对比',
        ]
        for word in title_words:
            if len(word) >= 2 and word not in keywords and not any(word in k for k in keywords):
                should_skip = False
                for sw in skip_words:
                    if sw in word:
                        should_skip = True
                        break
                if not should_skip:
                    keywords.append(word)
                    if len(keywords) >= 5:
                        break
    
    keywords = keywords[:5]
    
    if len(keywords) < 3:
        keywords.append('知识管理')
    if len(keywords) < 3:
        keywords.append('方法论')
    
    return ' · '.join(keywords)

test_cases = [
    'OKR管理体系全景指南（2026）：从目标管理到AI驱动的组织效能提升',
    '企业知识库搭建工具深度解析（11款主流工具选型指南）',
    'AI时代程序员效能提升全景指南（2026）：从10x工程师到100x工程师的能力进化路径',
]

for title in test_cases:
    print('Title:', title)
    print('Keywords:', generate_keywords(title, ''))
    print()
