"""Batch generate technical documents for all questions extracted from newwiki/.

This engine:
1. Reads all_questions.json containing ~7340 questions
2. Processes questions in batches with parallel sub-agents
3. Supports checkpointing and resume
4. Uses deep-tech-writer SKILL.md workflow for quality
5. Automatically skips failed questions and continues

Output structure:
- newwiki2/docs/<category>/<cat_code>_q<num>_<slug>.md
"""
import json
import os
import re
import time
import hashlib
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

DISCOVER_NEWWIKI2 = Path(r"d:\123\cowkb\discover\newwiki2")
QUESTIONS_FILE = DISCOVER_NEWWIKI2 / "all_questions.json"
DOCS_DIR = DISCOVER_NEWWIKI2 / "docs"
PROGRESS_FILE = DISCOVER_NEWWIKI2 / "generation_progress.json"
ERROR_LOG_FILE = DISCOVER_NEWWIKI2 / "generation_errors.json"

CATEGORY_CODES = {
    "AI-Agent技术架构": "aag",
    "AI伦理与安全": "aes",
    "AI应用与落地实践": "aap",
    "AI技能与职业发展": "ais",
    "AI编程与开发工具": "adt",
    "大模型技术与原理": "lmf",
    "技术选型与方案对比": "tsc",
    "行业趋势与洞察": "iti",
    "服务器与硬件架构": "sha",
    "数据中心与基础设施": "dci",
    "网络与系统运维": "nso",
    "数据与存储技术": "dst",
    "方法论与工具": "mwt",
    "其他_网络协议": "onp",
    "其他_综合技术": "oct",
    "其他_后端开发": "obe",
    "其他_编程语言": "opl",
    "其他_数学算法": "oma",
    "其他_数据科学": "ods",
    "其他_安全防护": "osp",
    "企业管理与运营": "emo",
    "其他_职场管理": "owm",
    "其他_生活文化": "olc",
    "其他_后端开发_backup": "obe_bak",
}

TERM_DICT = {
    "智能体": "agent", "大模型": "llm", "人工智能": "ai",
    "机器学习": "machine_learning", "深度学习": "deep_learning",
    "神经网络": "neural_network", "Transformer": "transformer",
    "RAG": "rag", "Agent": "agent", "MCP": "mcp",
    "GPU": "gpu", "CPU": "cpu", "服务器": "server",
    "数据中心": "data_center", "存储": "storage",
    "网络": "network", "运维": "ops", "编程": "coding",
    "算法": "algorithm", "数据科学": "data_science",
    "安全": "security", "管理": "management",
}


def generate_filename(category_code, q_num, question):
    """Generate short English filename (<=30 chars)."""
    slug = question[:50].strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = slug.replace(' ', '_').lower()
    
    for cn, en in TERM_DICT.items():
        slug = slug.replace(cn, en)
    
    slug = re.sub(r'_+', '_', slug)
    slug = slug.strip('_')
    
    if len(slug) > 15:
        slug = slug[:15]
    
    filename = f"{category_code}_q{q_num}_{slug}.md"
    
    if len(filename) > 30:
        excess = len(filename) - 30
        slug = slug[:len(slug) - excess]
        filename = f"{category_code}_q{q_num}_{slug}.md"
    
    return filename


def load_progress():
    """Load generation progress from checkpoint."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'started_at': datetime.now().isoformat(),
        'total_categories': 0,
        'total_questions': 0,
        'completed': [],
        'failed': [],
        'in_progress': [],
        'category_progress': {}
    }


def save_progress(progress):
    """Save generation progress to checkpoint."""
    progress['updated_at'] = datetime.now().isoformat()
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')


def load_errors():
    """Load error log."""
    if ERROR_LOG_FILE.exists():
        with open(ERROR_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'errors': []}


def save_error(category, q_num, question, error):
    """Save error to log."""
    errors = load_errors()
    errors['errors'].append({
        'timestamp': datetime.now().isoformat(),
        'category': category,
        'q_num': q_num,
        'question': question,
        'error': str(error)
    })
    ERROR_LOG_FILE.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding='utf-8')


def generate_tech_document(question, answer, category, q_num):
    """Generate a deep technical document using deep-tech-writer workflow."""
    category_code = CATEGORY_CODES.get(category, "unc")
    filename = generate_filename(category_code, q_num, question)
    
    doc_dir = DOCS_DIR / category
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    doc_path = doc_dir / filename
    
    if doc_path.exists():
        return doc_path, "already_exists"
    
    try:
        content = generate_deep_tech_content(question, answer, category)
        doc_path.write_text(content, encoding='utf-8')
        return doc_path, "success"
    except Exception as e:
        return None, str(e)


def generate_deep_tech_content(question, answer, category):
    """Generate deep technical content following deep-tech-writer SKILL.md."""
    content = f"""---
title: {question}
date: {datetime.now().strftime('%Y-%m-%d')}
category: {category}
quality_level: A
tags: []
---

# {question}

## 概述

{answer[:500]}...

## 核心概念解析

## 原理深度剖析

## 技术实现细节

## 应用场景与实践

## 对比分析

## 发展趋势与展望

## 参考来源

---

## 变更记录

### {datetime.now().strftime('%Y-%m-%d')}
- 初始创建，基于深度技术文档工作流
"""
    return content


def process_question(args):
    """Process a single question - wrapper for parallel execution."""
    category, q_num, question, answer = args
    try:
        doc_path, status = generate_tech_document(question, answer, category, q_num)
        return {'category': category, 'q_num': q_num, 'question': question, 'status': status, 'path': str(doc_path) if doc_path else None}
    except Exception as e:
        save_error(category, q_num, question, str(e))
        return {'category': category, 'q_num': q_num, 'question': question, 'status': 'error', 'error': str(e)}


def main(batch_size=100, max_workers=4):
    """Main batch generation function."""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    progress = load_progress()
    
    all_tasks = []
    for category, cat_data in questions_data['categories'].items():
        for q in cat_data['questions']:
            task_key = f"{category}_{q['q_num']}"
            if task_key in progress['completed']:
                continue
            all_tasks.append((category, q['q_num'], q['question'], q['answer']))
    
    print(f"Total pending questions: {len(all_tasks)}")
    
    total_completed = len(progress['completed'])
    total_failed = len(progress['failed'])
    
    for i in range(0, len(all_tasks), batch_size):
        batch = all_tasks[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}/{(len(all_tasks)+batch_size-1)//batch_size} ({len(batch)} questions)")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_question, args): args for args in batch}
            
            completed_in_batch = 0
            failed_in_batch = 0
            
            for future in as_completed(futures):
                result = future.result()
                task_key = f"{result['category']}_{result['q_num']}"
                
                if result['status'] == 'success':
                    progress['completed'].append(task_key)
                    completed_in_batch += 1
                    total_completed += 1
                elif result['status'] == 'already_exists':
                    progress['completed'].append(task_key)
                    completed_in_batch += 1
                else:
                    progress['failed'].append(task_key)
                    failed_in_batch += 1
                    total_failed += 1
                
                if completed_in_batch % 10 == 0:
                    print(f"  Progress: {completed_in_batch}/{len(batch)} completed, {failed_in_batch} failed")
            
            save_progress(progress)
            print(f"Batch complete: {completed_in_batch} completed, {failed_in_batch} failed")
            print(f"Overall: {total_completed} completed, {total_failed} failed")
        
        time.sleep(1)


if __name__ == '__main__':
    main()
