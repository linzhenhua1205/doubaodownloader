"""Enhance generated document skeletons using LLM following deep-tech-writer SKILL.md workflow.

This script:
1. Reads existing document skeletons
2. Calls LLM to enhance content following the 6-step deep-tech-writer workflow
3. Supports checkpointing and resume
4. Handles errors gracefully and continues
"""
import json
import os
import re
import time
import traceback
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import openai

DISCOVER_NEWWIKI2 = Path(r"d:\123\cowkb\discover\newwiki2")
DOCS_DIR = DISCOVER_NEWWIKI2 / "docs"
PROGRESS_FILE = DISCOVER_NEWWIKI2 / "enhancement_progress.json"
ERROR_LOG_FILE = DISCOVER_NEWWIKI2 / "enhancement_errors.json"
QUESTIONS_FILE = DISCOVER_NEWWIKI2 / "all_questions.json"

SYSTEM_PROMPT = """You are a senior technical writer following the deep-tech-writer SKILL.md workflow.

Your task: Enhance the provided document skeleton with comprehensive, in-depth technical content.

FOLLOW THESE STRICT QUALITY RULES:
1. **原理深度**: Go deep into protocol/chip/physics level, explain WHY not just WHAT
2. **来源标注**: Every key assertion must have a source (paper/standard/whitepaper/report)
3. **强逻辑**: Argument → Evidence → Data → Conclusion, no contradictions
4. **取材优先**: Papers/standards > official whitepapers > engineering reports > industry analysis > general knowledge
5. **外部链接优先**: Compress general background knowledge into one sentence + external link
6. **审查闭环**: Self-review after writing

DOCUMENT STRUCTURE TO ENHANCE:
- 概述: Comprehensive overview with key insights
- 核心概念解析: Deep dive into key concepts with definitions and examples
- 原理深度剖析: First-principles analysis with data and sources
- 技术实现细节: Implementation details, code examples, architecture diagrams
- 应用场景与实践: Real-world use cases, best practices
- 对比分析: Compare multiple approaches with trade-offs
- 发展趋势与展望: Future trends and predictions
- 参考来源: Cited references with links

REQUIREMENTS:
- Include at least 3 quantified data points with units and baselines
- Include at least 2 references with proper citations
- Use tables for comparisons where appropriate
- Keep code blocks pure ASCII
- Add changelog at bottom
- Target: 800-1200 words per document
"""


def load_progress():
    """Load enhancement progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'started_at': datetime.now().isoformat(),
        'completed': [],
        'failed': [],
        'in_progress': []
    }


def save_progress(progress):
    """Save enhancement progress."""
    progress['updated_at'] = datetime.now().isoformat()
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')


def save_error(filepath, error):
    """Save enhancement error."""
    errors = load_errors()
    errors['errors'].append({
        'timestamp': datetime.now().isoformat(),
        'file': str(filepath),
        'error': str(error)[:500]
    })
    ERROR_LOG_FILE.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding='utf-8')


def load_errors():
    """Load enhancement errors."""
    if ERROR_LOG_FILE.exists():
        with open(ERROR_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'errors': []}


def get_question_for_file(filepath, questions_data):
    """Find the question data for a given document file."""
    filename = filepath.stem
    parts = filename.split('_')
    if len(parts) >= 2:
        cat_code = parts[0]
        q_num_part = parts[1]
        q_num = q_num_part.replace('q', '')
        
        for category, cat_data in questions_data['categories'].items():
            for q in cat_data['questions']:
                if str(q['q_num']) == q_num:
                    return q
    
    return None


def enhance_document(filepath, questions_data):
    """Enhance a single document using LLM."""
    file_key = str(filepath.relative_to(DOCS_DIR))
    
    try:
        content = filepath.read_text(encoding='utf-8')
        
        question = get_question_for_file(filepath, questions_data)
        if question:
            question_text = question['question']
            answer_text = question.get('answer', '')
        else:
            title_match = re.search(r'title:\s*(.+)', content)
            question_text = title_match.group(1) if title_match else "Unknown question"
            answer_text = ""
        
        user_prompt = f"""Document title: {question_text}

Existing answer (for reference):
{answer_text[:2000]}

---

Please enhance this document following the deep-tech-writer SKILL.md workflow. Focus on:
1. Comprehensive overview with key insights
2. Deep concept analysis with first-principles explanations
3. Technical implementation details
4. Real-world applications and best practices
5. Comparative analysis where applicable
6. Future trends and predictions

Include:
- At least 3 quantified data points with units and baselines
- At least 2 proper citations/references
- Tables for comparisons
- Code examples where relevant
- ASCII diagrams where helpful
- Changelog at the bottom

Target: 800-1200 words.
"""
        
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            enhanced_content = response.choices[0].message.content
            
            filepath.write_text(enhanced_content, encoding='utf-8')
            return {'status': 'success', 'file': file_key}
        except Exception as api_error:
            return {'status': 'api_error', 'file': file_key, 'error': str(api_error)[:300]}
            
    except Exception as e:
        save_error(filepath, str(e))
        return {'status': 'error', 'file': file_key, 'error': str(e)[:300]}


def main(batch_size=20, max_workers=2):
    """Main enhancement function."""
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
    
    progress = load_progress()
    
    all_files = []
    for md_file in DOCS_DIR.rglob('*.md'):
        file_key = str(md_file.relative_to(DOCS_DIR))
        if file_key in progress['completed']:
            continue
        if file_key == 'README.md':
            continue
        all_files.append(md_file)
    
    print(f"Total pending files: {len(all_files)}")
    
    total_completed = len(progress['completed'])
    total_failed = len(progress['failed'])
    
    for i in range(0, len(all_files), batch_size):
        batch = all_files[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}/{(len(all_files)+batch_size-1)//batch_size} ({len(batch)} files)")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(enhance_document, fp, questions_data): fp for fp in batch}
            
            completed_in_batch = 0
            failed_in_batch = 0
            
            for future in as_completed(futures):
                result = future.result()
                
                if result['status'] == 'success':
                    progress['completed'].append(result['file'])
                    completed_in_batch += 1
                    total_completed += 1
                else:
                    progress['failed'].append(result['file'])
                    failed_in_batch += 1
                    total_failed += 1
                
                if completed_in_batch % 5 == 0:
                    print(f"  Progress: {completed_in_batch}/{len(batch)} completed, {failed_in_batch} failed")
            
            save_progress(progress)
            print(f"Batch complete: {completed_in_batch} completed, {failed_in_batch} failed")
            print(f"Overall: {total_completed} completed, {total_failed} failed")
        
        time.sleep(5)


if __name__ == '__main__':
    main()
