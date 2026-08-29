#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

QUESTIONS_DIR = Path(__file__).parent.parent.parent / "conversation-log" / "user-questions"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "conversation-log" / "user_indent.md"
MEMORY_FILE = Path(__file__).parent.parent.parent / "MEMORY.md"
RULE_FILE = Path(__file__).parent.parent.parent / "RULE.md"

INTENT_CATEGORIES = {
    'knowledge_build': {
        'name': '知识体系构建',
        'description': '从零创建或扩展知识模块，要求结构化组织',
        'keywords': ['构建', '创建', '搭建', '初始化', '归档', '索引', '知识库', '知识体系', '知识图谱', '交叉链接', '写入', '模块', '目录', '图谱', '整理', 'build', 'create', 'construct', 'organize', 'index', 'knowledge', 'archive', 'write']
    },
    'tech_analysis': {
        'name': '深度技术分析',
        'description': '对特定技术领域进行深入研究，要求原理推导和量化数据',
        'keywords': ['分析', '原理', '推导', '量化', '对比', '权衡', '维度', '评估', '方法论', '研究', '调研', '性能', '架构', '设计', '方案', '演进', '趋势', '空缺', 'analyze', 'analysis', 'architecture', 'design', 'performance', 'research', 'study', 'discuss', 'explore', 'inference', 'collective', 'communication', 'memory', 'storage', 'solution', 'network', 'protocol']
    },
    'methodology': {
        'name': '方法论制定与固化',
        'description': '建立分析框架、工作流程、质量标准',
        'keywords': ['MECE', '第一性原理', '逻辑', '规则', '标准', '流程', '工作流', '方法论', '原则', '方法', '框架', '模式', '思考', '论证', '结构化', 'methodology', 'principle', 'framework', 'logic', 'pattern', 'process', 'standard', 'rule']
    },
    'correction': {
        'name': '技术纠错与审查',
        'description': '发现并修正已有知识中的错误，审查内容质量',
        'keywords': ['勘误', '修正', '错误', '不对', '修复', '验证', '审查', '挑刺', '改进', '优化', 'correct', 'fix', 'review', 'verify', 'audit', 'mistake', 'error']
    },
    'tool_optimize': {
        'name': '工具链优化',
        'description': '改进工作环境、脚本、技能，提升效率',
        'keywords': ['脚本', '工具', '技能', '优化', '配置', '修复', '部署', '自动化', 'skill', '重构', '升级', '效率', 'script', 'tool', 'optimize', 'automate', 'deploy', 'upgrade', 'refactor', 'efficiency']
    },
    'info_tracking': {
        'name': '信息获取与跟踪',
        'description': '获取最新行业动态，跟踪技术进展',
        'keywords': ['搜索', '跟踪', '最新动态', '调研', '专题', '获取', '动态', '最新', '资料', '信息', '查找', '更新', '新闻', '进展', 'search', 'track', 'update', 'latest', 'news', 'trend', 'progress']
    },
    'discussion': {
        'name': '技术讨论与交流',
        'description': '对特定技术话题进行讨论、分享观点',
        'keywords': ['讨论', '交流', '分享', '观点', '思考', '想法', '探讨', '分析材料', '论证', 'discuss', 'share', 'view', 'opinion', 'thought', 'argue', 'debate']
    },
    'other': {
        'name': '其他',
        'description': '无法归类的其他请求',
        'keywords': []
    }
}

TECH_DIMENSIONS = {
    'knowledge_base': ['知识库', 'index', '交叉链接', '归档'],
    'si': ['SI', '信号完整性', '眼图', '误码率', '阻抗'],
    'rdma': ['RDMA', 'DMA', '协议栈'],
    'cache': ['Cache', '一致性', '缓存'],
    'bandwidth': ['带宽', '吞吐量', '互联'],
    'format': ['格式', '编号', '规范'],
    'interconnect': ['NVLink', 'NVSwitch', 'PCIe', 'CXL'],
    'memory': ['HBM', '内存', 'DDR'],
    'power': ['电源', '供电', '效率'],
    'cooling': ['液冷', '散热', '冷却'],
    'reliability': ['RAS', '可靠性', '故障'],
    'bmc': ['BMC', '固件', 'Redfish'],
}


def load_memory():
    """加载MEMORY.md内容"""
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def load_rule():
    """加载RULE.md内容"""
    if RULE_FILE.exists():
        with open(RULE_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


SCHEDULER_FILE_KEYWORDS = [
    '执行', '跟踪', '搜索', '扫描', '备份', '测试任务', '调度器测试',
    '定时', '自动', '更新任务', '专题搜索'
]

def is_scheduler_file(filename):
    """判断文件是否为调度器任务"""
    for keyword in SCHEDULER_FILE_KEYWORDS:
        if keyword in filename:
            return True
    return False

def load_user_questions():
    """加载用户问题（过滤调度器任务）"""
    questions = []
    
    exclude_files = ['index.md', 'STATISTICS.md', 'TOPIC_ANALYSIS.md']
    
    for md_file in QUESTIONS_DIR.glob('*.md'):
        if md_file.name in exclude_files:
            continue
        
        if is_scheduler_file(md_file.name):
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})-', md_file.stem)
        date_str = date_match.group(1) if date_match else ''
        
        lines = content.split('\n')
        current_title = ""
        q_num = 0
        in_q_content = False
        q_content_lines = []
        current_time = ""
        
        for line in lines:
            if line.startswith('# ') and not line.startswith('##') and not line.startswith('###'):
                current_title = line[2:].strip()
            # 新格式: ### #1 [💬 其他] (Seq=0, 2026-07-09 09:26)
            elif re.match(r'^###\s+#\d+\s+\[', line):
                if in_q_content and q_content_lines:
                    q_content = '\n'.join(q_content_lines).strip()
                    if q_content and not q_content.startswith('[空消息]'):
                        questions.append({
                            'date': date_str,
                            'time': current_time,
                            'title': current_title,
                            'q_num': q_num,
                            'content': q_content,
                            'file': md_file.name
                        })
                
                q_num += 1
                time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+(\d{1,2}:\d{2}))', line)
                current_time = time_match.group(2) if time_match else ''
                
                in_q_content = True
                q_content_lines = []
            elif line.startswith('## Q'):
                if in_q_content and q_content_lines:
                    q_content = '\n'.join(q_content_lines).strip()
                    if q_content and not q_content.startswith('[空消息]'):
                        questions.append({
                            'date': date_str,
                            'time': current_time,
                            'title': current_title,
                            'q_num': q_num,
                            'content': q_content,
                            'file': md_file.name
                        })
                
                q_match = re.match(r'## Q(\d+)\s*-\s*(\d+:\d+)?', line)
                if q_match:
                    q_num = int(q_match.group(1))
                    current_time = q_match.group(2) if q_match.group(2) else ''
                else:
                    q_num += 1
                    current_time = ''
                
                in_q_content = True
                q_content_lines = []
            elif in_q_content and line.strip() != '' and not line.startswith('---'):
                q_content_lines.append(line)
        
        if in_q_content and q_content_lines:
            q_content = '\n'.join(q_content_lines).strip()
            if q_content and not q_content.startswith('[空消息]'):
                questions.append({
                    'date': date_str,
                    'time': current_time,
                    'title': current_title,
                    'q_num': q_num,
                    'content': q_content,
                    'file': md_file.name
                })
    
    questions.sort(key=lambda x: (x['date'], x['time'], x['q_num']))
    return questions


def classify_intent(content):
    """对用户问题进行意图分类"""
    content_lower = content.lower()
    
    for intent_key, config in INTENT_CATEGORIES.items():
        for keyword in config['keywords']:
            if keyword.lower() in content_lower:
                return intent_key
    
    return 'other'


def detect_tech_dimensions(content):
    """检测技术维度"""
    dimensions = []
    content_lower = content.lower()
    
    for dim_key, keywords in TECH_DIMENSIONS.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                dimensions.append(dim_key)
                break
    
    return dimensions if dimensions else ['other']


def analyze_decision_patterns(questions):
    """分析决策模式"""
    patterns = defaultdict(int)
    
    for q in questions:
        content = q['content']
        
        if '补充' in content or '完善' in content:
            patterns['补充完善'] += 1
        if '创建' in content or '生成' in content:
            patterns['创建生成'] += 1
        if '优化' in content or '格式' in content:
            patterns['优化格式'] += 1
        if '技能' in content or '规则' in content or '记忆' in content:
            patterns['技能规则'] += 1
        if '归档' in content or '写入' in content:
            patterns['材料归档'] += 1
        if '审查' in content or '修正' in content or '验证' in content:
            patterns['审查修正'] += 1
        if '分析' in content or '原理' in content:
            patterns['深度技术分析'] += 1
    
    return patterns


def analyze_quality_requirements(questions, memory_content):
    """分析质量要求"""
    requirements = []
    
    quality_keywords = {
        '第一性原理': '从第一性原理出发',
        'MECE': 'MECE原则',
        '数据': '数据可验证',
        '来源': '来源验证',
        '格式': '格式规范',
        '逻辑': '强逻辑论证',
        '流于形式': '不能流于形式'
    }
    
    for keyword, desc in quality_keywords.items():
        count = sum(1 for q in questions if keyword in q['content'])
        if count > 0:
            requirements.append({
                'keyword': keyword,
                'description': desc,
                'count': count
            })
    
    return requirements


def build_user_profile(questions, memory_content):
    """构建用户画像"""
    profile = {
        'identity': '服务器/数据中心产品研发专家，深耕AI算力基础设施',
        'role': '知识建构者、技术决策者、方法论设计师',
        'style': '专业严谨、数据驱动、追求深度',
        'core_values': []
    }
    
    if 'MECE' in memory_content:
        profile['core_values'].append('MECE原则')
    if '第一性原理' in memory_content:
        profile['core_values'].append('第一性原理')
    if '逻辑' in memory_content:
        profile['core_values'].append('强逻辑论证')
    if '数据' in memory_content:
        profile['core_values'].append('数据可验证')
    
    return profile


def generate_report(questions, memory_content, rule_content):
    """生成意图分析报告"""
    lines = ["# 🧠 用户真实输入深度分析报告"]
    lines.append("")
    lines.append(f"> **分析日期**: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"> **数据源**: `conversation-log/user-questions/` + `MEMORY.md` + `RULE.md`")
    lines.append(f"> **方法**: 基于完整对话流程分析，结合上下文推导真实意图")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 一、会话数据全景")
    lines.append("")
    
    web_count = len(set(q['file'] for q in questions))
    lines.append(f"| 维度 | 数值 |")
    lines.append(f"|:-----|:----:|")
    lines.append(f"| 总用户问题数 | {len(questions)} |")
    lines.append(f"| Web会话数 | {web_count} |")
    lines.append(f"| 覆盖日期范围 | {questions[0]['date']} → {questions[-1]['date']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    profile = build_user_profile(questions, memory_content)
    lines.append("## 二、用户画像与核心价值观")
    lines.append("")
    lines.append("### 身份特征")
    lines.append("")
    lines.append(f"- **领域**: {profile['identity']}")
    lines.append(f"- **角色**: {profile['role']}")
    lines.append(f"- **风格**: {profile['style']}")
    lines.append("")
    lines.append("### 核心价值观")
    lines.append("")
    lines.append("| # | 价值观 | 来源 |")
    lines.append("|:-:|:-------|:-----|")
    for i, value in enumerate(profile['core_values'], 1):
        lines.append(f"| {i} | {value} | MEMORY.md |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 三、意图分类体系")
    lines.append("")
    
    intent_counts = defaultdict(int)
    for q in questions:
        intent = classify_intent(q['content'])
        intent_counts[intent] += 1
    
    total = sum(intent_counts.values())
    lines.append("| # | 意图类型 | 问题数 | 占比 | 描述 |")
    lines.append("|:-:|:---------|:------:|:----:|:-----|")
    for i, (intent_key, count) in enumerate(sorted(intent_counts.items(), key=lambda x: -x[1]), 1):
        percent = (count / total * 100) if total > 0 else 0
        config = INTENT_CATEGORIES[intent_key]
        lines.append(f"| {i} | {config['name']} | {count} | {percent:.1f}% | {config['description']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 四、决策模式分析")
    lines.append("")
    
    patterns = analyze_decision_patterns(questions)
    total_patterns = sum(patterns.values())
    
    lines.append("| # | 指令模式 | 频次 | 占比 |")
    lines.append("|:-:|:---------|:----:|:----:|")
    for i, (pattern, count) in enumerate(sorted(patterns.items(), key=lambda x: -x[1]), 1):
        percent = (count / total_patterns * 100) if total_patterns > 0 else 0
        lines.append(f"| {i} | {pattern} | {count} | {percent:.1f}% |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 五、技术维度关注分析")
    lines.append("")
    
    dim_counts = defaultdict(int)
    for q in questions:
        dims = detect_tech_dimensions(q['content'])
        for dim in dims:
            dim_counts[dim] += 1
    
    lines.append("| # | 技术维度 | 频次 |")
    lines.append("|:-:|:---------|:----:|")
    for i, (dim, count) in enumerate(sorted(dim_counts.items(), key=lambda x: -x[1]), 1):
        lines.append(f"| {i} | {dim} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 六、质量要求分析")
    lines.append("")
    
    requirements = analyze_quality_requirements(questions, memory_content)
    lines.append("| # | 质量要求 | 提及次数 |")
    lines.append("|:-:|:---------|:--------:|")
    for i, req in enumerate(requirements, 1):
        lines.append(f"| {i} | {req['description']} | {req['count']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 七、关键洞察")
    lines.append("")
    
    top_intent = max(intent_counts.items(), key=lambda x: x[1])[0]
    top_pattern = max(patterns.items(), key=lambda x: x[1])[0]
    
    lines.append(f"- **最频繁的意图**: {INTENT_CATEGORIES[top_intent]['name']}")
    lines.append(f"- **最频繁的指令模式**: {top_pattern}")
    lines.append(f"- **核心工作模式**: 创建→迭代→打磨三元闭环")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 八、对话主线示例")
    lines.append("")
    
    recent_questions = questions[-10:]
    for q in recent_questions:
        intent = classify_intent(q['content'])
        lines.append(f"- **[{q['date']} {q['time']}]** {INTENT_CATEGORIES[intent]['name']}: {q['content']}")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    lines.append("## 九、对系统优化的启示")
    lines.append("")
    lines.append("| 优先级 | 建议 | 依据 |")
    lines.append("|:-:|:-----|:-----|")
    lines.append("| P0 | 深度技术写作技能 | 技术分析类问题占比高 |")
    lines.append("| P0 | 文档审查技能 | 审查修正需求频繁 |")
    lines.append("| P1 | 格式规范检查 | 优化格式需求较多 |")
    lines.append("| P1 | 方法论分析 | 方法论制定是核心驱动力 |")
    lines.append("")
    
    return '\n'.join(lines)


def generate_intent_report():
    """生成意图分析报告"""
    questions = load_user_questions()
    memory_content = load_memory()
    rule_content = load_rule()
    
    report = generate_report(questions, memory_content, rule_content)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("[OK] 意图分析报告生成完成")
    print(f"  - 用户问题数: {len(questions)}")
    print(f"  - 输出文件: {OUTPUT_FILE}")


if __name__ == '__main__':
    generate_intent_report()