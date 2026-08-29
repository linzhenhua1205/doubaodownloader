#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path(__file__).parent.parent.parent / "conversation-log" / "db-sessions"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "conversation-log" / "user-questions"
SCHEDULER_KEYWORDS = [
    "执行", "跟踪", "搜索", "扫描", "备份", "测试任务", "调度器测试",
    "定时", "自动", "更新任务", "专题搜索"
]
EMPTY_MESSAGE_PATTERNS = [
    r"^\s*\[空消息\]\s*$",
    r"^\s*$",
    r"^\s*[-.=_~`*#]+\s*$",
]


def is_scheduler_task(title, content):
    """判断是否为定时任务"""
    text = (title + " " + content).lower()
    for keyword in SCHEDULER_KEYWORDS:
        if keyword.lower() in text:
            return True
    return False


def is_empty_message(content):
    """判断是否为空消息"""
    for pattern in EMPTY_MESSAGE_PATTERNS:
        if re.match(pattern, content.strip()):
            return True
    return False


def extract_user_messages(session_file):
    """从会话文件中提取用户消息"""
    with open(session_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    messages = []
    rounds = re.split(r'---\n', content)
    
    for round_content in rounds:
        if '### 🗣️ 用户' in round_content:
            match = re.search(r'### 🗣️ 用户\n\n(.+?)(\n### |\n---|\Z)', round_content, re.DOTALL)
            if match:
                user_content = match.group(1).strip()
                if not is_empty_message(user_content):
                    time_match = re.search(r'## 回合 \d+ - (\d+:\d+)', round_content)
                    time_str = time_match.group(1) if time_match else None
                    messages.append({
                        'content': user_content,
                        'time': time_str
                    })
    
    return messages


def parse_session_metadata(session_file):
    """解析会话元数据"""
    with open(session_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    meta = {}
    session_id_match = re.search(r'会话 ID.*?:\s*`(.+?)`', content)
    channel_match = re.search(r'渠道.*?:\s*(web|feishu|scheduler)', content)
    create_time_match = re.search(r'创建时间.*?:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', content)
    message_count_match = re.search(r'消息数.*?:\s*(\d+)', content)
    
    if session_id_match:
        meta['session_id'] = session_id_match.group(1)
    if channel_match:
        meta['channel'] = channel_match.group(1)
    if create_time_match:
        meta['create_time'] = create_time_match.group(1)
    if message_count_match:
        meta['message_count'] = int(message_count_match.group(1))
    
    return meta


def sanitize_filename(text):
    """清理文件名，移除非法字符"""
    text = re.sub(r'[\\/:*?"<>|]', '_', text)
    text = text.strip()
    if len(text) > 100:
        text = text[:100]
    return text


def export_user_questions():
    """导出用户问题，去除定时任务"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    session_files = list(SESSION_DIR.glob('*.md'))
    session_files.sort()
    
    web_sessions = []
    scheduler_sessions = []
    all_user_questions = []
    
    for session_file in session_files:
        filename = session_file.stem
        title_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)$', filename)
        if not title_match:
            continue
        
        date_str = title_match.group(1)
        title = title_match.group(2)
        
        meta = parse_session_metadata(session_file)
        user_messages = extract_user_messages(session_file)
        
        is_sched = meta.get('channel') == 'scheduler' or is_scheduler_task(title, str(user_messages))
        
        session_data = {
            'date': date_str,
            'title': title,
            'channel': meta.get('channel', ''),
            'session_id': meta.get('session_id', ''),
            'message_count': meta.get('message_count', len(user_messages)),
            'user_message_count': len(user_messages),
            'is_scheduler': is_sched,
            'user_messages': user_messages
        }
        
        if is_sched:
            scheduler_sessions.append(session_data)
        else:
            web_sessions.append(session_data)
            for msg in user_messages:
                all_user_questions.append({
                    'date': date_str,
                    'time': msg.get('time', ''),
                    'title': title,
                    'content': msg['content'],
                    'session_id': meta.get('session_id', '')
                })
    
    for session_data in web_sessions:
        safe_title = sanitize_filename(session_data['title'])
        output_file = OUTPUT_DIR / f"{session_data['date']}-{safe_title}.md"
        
        lines = [f"# {session_data['title']}"]
        lines.append("")
        lines.append(f"> **日期**: {session_data['date']}")
        lines.append(f"> **渠道**: {session_data['channel']}")
        lines.append(f"> **会话ID**: `{session_data['session_id']}`")
        lines.append(f"> **用户消息数**: {session_data['user_message_count']}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        for i, msg in enumerate(session_data['user_messages'], 1):
            lines.append(f"## Q{i} - {msg.get('time', '')}")
            lines.append("")
            lines.append(msg['content'])
            lines.append("")
            lines.append("---")
            lines.append("")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines('\n'.join(lines))
    
    index_lines = ["# 📋 用户问题导出索引"]
    index_lines.append("")
    index_lines.append(f"> **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    index_lines.append(f"> **数据来源**: `conversation-log/db-sessions/`")
    index_lines.append(f"> **总会话**: {len(session_files)} | **Web会话**: {len(web_sessions)} | **Scheduler会话**: {len(scheduler_sessions)}")
    index_lines.append("")
    index_lines.append("| # | 日期 | 渠道 | 会话标题 | 用户问题数 | 文件 |")
    index_lines.append("|:-:|:----|:-----|:---------|:----------:|:-----|")
    
    for i, session_data in enumerate(web_sessions, 1):
        safe_title = sanitize_filename(session_data['title'])
        index_lines.append(f"| {i} | {session_data['date']} | {session_data['channel']} | {session_data['title']} | {session_data['user_message_count']} | [{session_data['date']}-{safe_title}.md]({session_data['date']}-{safe_title}.md) |")
    
    index_lines.append("")
    index_lines.append("---")
    index_lines.append("")
    index_lines.append("## 📊 统计概览")
    index_lines.append("")
    index_lines.append(f"- **总会话数**: {len(session_files)}")
    index_lines.append(f"- **Web会话数**: {len(web_sessions)}")
    index_lines.append(f"- **Scheduler会话数**: {len(scheduler_sessions)}")
    index_lines.append(f"- **总用户问题数**: {len(all_user_questions)}")
    
    index_file = OUTPUT_DIR / "index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.writelines('\n'.join(index_lines))
    
    stats_lines = ["# 📊 用户问题统计分析"]
    stats_lines.append("")
    stats_lines.append(f"> **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    stats_lines.append(f"> **数据源**: `conversation-log/db-sessions/`")
    stats_lines.append("")
    stats_lines.append("## 📡 按渠道分布")
    stats_lines.append("")
    stats_lines.append("| 渠道 | 会话数 | 用户问题数 |")
    stats_lines.append("|:-:|:------:|:----------:|")
    stats_lines.append(f"| Web（人机交互） | {len(web_sessions)} | {sum(s['user_message_count'] for s in web_sessions)} |")
    stats_lines.append(f"| Scheduler（定时任务） | {len(scheduler_sessions)} | {sum(s['user_message_count'] for s in scheduler_sessions)} |")
    stats_lines.append("")
    stats_lines.append("## 📅 按日期活跃度")
    stats_lines.append("")
    
    date_counts = {}
    for q in all_user_questions:
        date_counts[q['date']] = date_counts.get(q['date'], 0) + 1
    
    for date in sorted(date_counts.keys()):
        count = date_counts[date]
        bar = '█' * min(count // 2, 50)
        stats_lines.append(f"| {date} | {count:3d} | {bar}")
    
    stats_file = OUTPUT_DIR / "STATISTICS.md"
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.writelines('\n'.join(stats_lines))
    
    print("[OK] 导出完成")
    print(f"  - Web会话: {len(web_sessions)}")
    print(f"  - Scheduler会话: {len(scheduler_sessions)}")
    print(f"  - 用户问题数: {len(all_user_questions)}")
    print(f"  - 输出目录: {OUTPUT_DIR}")


if __name__ == '__main__':
    export_user_questions()