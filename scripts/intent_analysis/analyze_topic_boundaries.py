#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

QUESTIONS_DIR = Path(__file__).parent.parent.parent / "conversation-log" / "user-questions"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "conversation-log" / "user-questions"

INTENT_KEYWORDS = {
    'knowledge_build': ['构建', '创建', '搭建', '初始化', '归档', '索引', '知识库', '知识体系'],
    'tech_analysis': ['分析', '原理', '推导', '量化', '对比', '权衡', '维度', '评估', '方法论'],
    'methodology': ['MECE', '第一性原理', '逻辑', '规则', '标准', '流程', '工作流', '方法论'],
    'correction': ['勘误', '修正', '错误', '不对', '修复', '验证', '审查', '挑刺'],
    'tool_optimize': ['脚本', '工具', '技能', '优化', '配置', '修复', '部署', '自动化'],
    'info_tracking': ['搜索', '跟踪', '最新动态', '调研', '专题', '获取'],
}

TOPIC_TRANSITION_SIGNALS = [
    '另外', '还有', '顺便', '换个', '转向', '接下来', '继续', '再',
    '回到', '切换', '现在', '开始', '接下来', '另外', '补充', '还有一个'
]


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
    """加载所有用户问题（过滤调度器任务）"""
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
        
        for line in lines:
            if line.startswith('# ') and not line.startswith('##'):
                current_title = line[2:].strip()
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
    intents = []
    content_lower = content.lower()
    
    for intent_type, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                intents.append(intent_type)
                break
    
    return intents if intents else ['other']


def detect_topic_transition(current_content, prev_content):
    """检测话题切换"""
    for signal in TOPIC_TRANSITION_SIGNALS:
        if signal in current_content:
            return True
    
    current_intents = classify_intent(current_content)
    prev_intents = classify_intent(prev_content)
    
    if not set(current_intents) & set(prev_intents):
        return True
    
    return False


def cluster_topics(questions):
    """将问题聚类为话题"""
    if not questions:
        return []
    
    topics = []
    current_topic = {
        'topic_id': 1,
        'start_date': questions[0]['date'],
        'end_date': questions[0]['date'],
        'start_time': questions[0]['time'],
        'end_time': questions[0]['time'],
        'title': questions[0]['title'],
        'questions': [questions[0]],
        'intents': classify_intent(questions[0]['content']),
        'keywords': extract_keywords(questions[0]['content'])
    }
    
    for q in questions[1:]:
        prev_q = current_topic['questions'][-1]
        
        if detect_topic_transition(q['content'], prev_q['content']):
            topics.append(current_topic)
            current_topic = {
                'topic_id': len(topics) + 1,
                'start_date': q['date'],
                'end_date': q['date'],
                'start_time': q['time'],
                'end_time': q['time'],
                'title': q['title'],
                'questions': [q],
                'intents': classify_intent(q['content']),
                'keywords': extract_keywords(q['content'])
            }
        else:
            current_topic['questions'].append(q)
            current_topic['end_date'] = q['date']
            current_topic['end_time'] = q['time']
            current_topic['intents'] = list(set(current_topic['intents'] + classify_intent(q['content'])))
            current_topic['keywords'].update(extract_keywords(q['content']))
    
    topics.append(current_topic)
    return topics


def extract_keywords(content):
    """提取关键词"""
    keywords = set()
    
    tech_keywords = [
        'RAS', 'BMC', 'SI', 'RDMA', 'DMA', 'Cache', 'NVLink', 'NVSwitch',
        'HBM', 'CXL', 'PCIe', '液冷', '超节点', 'GPU', 'CPU', '服务器',
        'MECE', '第一性原理', '方法论', '知识库', '技能', '脚本', '优化'
    ]
    
    for kw in tech_keywords:
        if kw.lower() in content.lower():
            keywords.add(kw)
    
    return keywords


def generate_topic_summary(topics):
    """生成话题摘要"""
    lines = ["# 🗺️ 对话主线分析"]
    lines.append("")
    lines.append(f"> **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> **话题总数**: {len(topics)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 话题列表")
    lines.append("")
    
    for topic in topics:
        lines.append(f"### 📌 话题 {topic['topic_id']}: {topic['title']}")
        lines.append("")
        lines.append(f"> **时间范围**: {topic['start_date']} {topic['start_time']} → {topic['end_date']} {topic['end_time']}")
        lines.append(f"> **问题数**: {len(topic['questions'])}")
        lines.append(f"> **意图类型**: {', '.join(topic['intents'])}")
        lines.append(f"> **关键词**: {', '.join(topic['keywords'])}")
        lines.append("")
        lines.append("**问题序列**:")
        lines.append("")
        
        for i, q in enumerate(topic['questions'], 1):
            lines.append(f"{i}. **[{q['date']} {q['time']}]** {q['content'][:100]}..." if len(q['content']) > 100 else f"{i}. **[{q['date']} {q['time']}]** {q['content']}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
    
    intent_stats = defaultdict(int)
    for topic in topics:
        for intent in topic['intents']:
            intent_stats[intent] += 1
    
    lines.append("## 📊 意图分布统计")
    lines.append("")
    lines.append("| 意图类型 | 话题数 | 占比 |")
    lines.append("|:-:|:------:|:----:|")
    
    total = sum(intent_stats.values())
    for intent, count in sorted(intent_stats.items(), key=lambda x: -x[1]):
        percent = (count / total * 100) if total > 0 else 0
        lines.append(f"| {intent} | {count} | {percent:.1f}% |")
    
    return '\n'.join(lines)


def analyze_topic_boundaries():
    """分析话题边界并生成报告"""
    questions = load_user_questions()
    topics = cluster_topics(questions)
    
    summary_content = generate_topic_summary(topics)
    summary_file = OUTPUT_DIR / "TOPIC_ANALYSIS.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print("[OK] 话题分析完成")
    print(f"  - 总问题数: {len(questions)}")
    print(f"  - 话题数: {len(topics)}")
    print(f"  - 输出文件: {summary_file}")
    
    return topics


if __name__ == '__main__':
    analyze_topic_boundaries()