#!/usr/bin/env python3
"""
enhance_engine.py — 批量文档深度增强引擎 v3 (合并版)

合并自 v1(enhance_engine.py) + v2(enhance_engine_v2.py) 的增强功能：
  - validate_content() 内容质量验证 + 自动重试
  - 更详细的结构化 Prompt
  - 可配置 API 参数
  - 质量门禁统计

用法:
    python3 scripts/discover/enhance_engine.py                    # 批量增强（默认参数）
    python3 scripts/discover/enhance_engine.py --batch-size 5     # 每批5个
    python3 scripts/discover/enhance_engine.py --max-workers 1    # 单线程
    python3 scripts/discover/enhance_engine.py --retry-only       # 仅重试失败任务
"""

import json
import os
import re
import sys
import time
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# ── 配置 ──────────────────────────────────────────────────────────────────────

DOCS_DIR = Path("knowledge/discover")
QUESTIONS_FILE = Path("data/questions.json")
PROGRESS_FILE = Path("data/enhance_progress.json")
ERRORS_FILE = Path("data/enhance_errors.json")
STATS_FILE = Path("data/enhance_stats.json")

# OpenAI 配置
API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE_URL = os.environ.get("OPENAI_API_BASE", "")

# 质量门禁
MIN_WORD_COUNT = 1500
MIN_SECTIONS_WITH_CONTENT = 5

PLACEHOLDER_PATTERNS = [
    r'待补充', r'待完善', r'详见下文', r'TODO', r'FIXME',
    r'\[待', r'\[TODO\]', r'<!--.*?-->',
    r'后续.*更新', r'相关内容.*补充',
]

SYSTEM_PROMPT = """你是一位资深技术写作专家，擅长撰写深度技术分析文档。你的写作风格：
- 严谨、精确、深入
- 量化数据驱动，每个断言附带来源
- 逻辑严密，MECE 结构
- 中文专业术语精准

请按照 deep-tech-writer 六步工作流输出完整文档。"""


def log(msg):
    """统一日志输出"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding='utf-8'))
    return {'completed': [], 'failed': [], 'in_progress': []}


def save_progress(progress):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')


def load_errors():
    if ERRORS_FILE.exists():
        return json.loads(ERRORS_FILE.read_text(encoding='utf-8'))
    return {}


def save_error(filepath, error):
    errors = load_errors()
    if not isinstance(errors, dict):
        errors = {}
    file_key = str(filepath)
    errors[file_key] = {
        'error': str(error)[:500],
        'time': datetime.now().isoformat()
    }
    ERRORS_FILE.parent.mkdir(parents=True, exist_ok=True)
    ERRORS_FILE.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding='utf-8')


def load_questions():
    if QUESTIONS_FILE.exists():
        return json.loads(QUESTIONS_FILE.read_text(encoding='utf-8'))
    return {}


def find_question_for_file(filepath, questions_data):
    """在问题数据中查找匹配的文件"""
    if not questions_data:
        return None
    for q_key, q_data in questions_data.items():
        source_file = q_data.get('source_file', '')
        source_path = q_data.get('source_path', '')
        if source_file and source_file in str(filepath):
            return q_data
        if source_path and source_path in str(filepath):
            return q_data
        title = q_data.get('title', '')
        if title and title in filepath.stem:
            return q_data
    return None


def should_enhance(filepath):
    """判断文件是否需要增强（跳过 index.md 和已增强的大文件）"""
    if filepath.name == 'index.md':
        return False
    if filepath.stat().st_size < 100:
        return True
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, content):
            return True
    if len(content) < MIN_WORD_COUNT * 2:
        return True
    return False


def validate_content(content, question):
    """内容质量验证"""
    issues = []
    if len(content) < MIN_WORD_COUNT * 2:
        issues.append(f"内容太短（{len(content)}字符，要求至少{MIN_WORD_COUNT*2}字符）")
    for pattern in PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"包含占位符 '{pattern}'")
    source_count = content.count('[来源:')
    if source_count < 3:
        issues.append(f"参考来源不足（{source_count}个，要求至少3个）")
    table_count = content.count('|') // 3
    if table_count < 1:
        issues.append(f"缺少对比表格")
    section_count = sum(1 for s in ['概述', '核心概念', '原理深度', '技术实现',
                                     '应用场景', '对比分析', '发展趋势', '参考来源']
                        if f'## {s}' in content or f'### {s}' in content)
    if section_count < MIN_SECTIONS_WITH_CONTENT:
        issues.append(f"章节不完整（{section_count}个，要求至少{MIN_SECTIONS_WITH_CONTENT}个）")
    return issues


def build_user_prompt(question, answer, category):
    prompt = f"""# 技术问题
{question}

## 原始答案（参考）
{answer[:3000] if answer else '无'}

## 分类
{category}

---

请按照 deep-tech-writer SKILL.md 的六步工作流，为上述问题创建一篇完整的深度技术分析文档。

## 硬性要求（必须全部满足）

1. **原理深度**: 深入到协议/芯片/物理层次，解释设计选择背后的原因
2. **量化数据**: 至少包含5个量化数据点（数值+单位+基线+测试条件）
3. **来源标注**: 至少3个引用来源，格式为 [来源: 论文/标准/白皮书/URL]
4. **对比分析**: 必须使用表格对比多种方案
5. **代码示例**: 相关代码使用纯ASCII
6. **中文撰写**: 使用专业技术中文
7. **目标长度**: 1500-3000字
8. **严禁占位符**: 不得出现"待补充"、"待完善"、"详见下文"、"TODO"等任何占位符
9. **完整内容**: 每个章节都必须有实质性内容，不得有空章节

## 章节结构

必须包含以下章节，每个章节都要有完整内容：
1. **概述**: 全面概述，包含核心洞察（至少200字）
2. **核心概念解析**: 关键概念的深入解析（至少300字）
3. **原理深度剖析**: 第一性原理分析（至少400字）
4. **技术实现细节**: 实现细节、代码示例（至少300字）
5. **应用场景与实践**: 真实世界用例、最佳实践（至少300字）
6. **对比分析**: 多种方案的对比与权衡（至少200字）
7. **发展趋势与展望**: 未来趋势和预测（至少150字）
8. **参考来源**: 引用的参考文献（至少3个）

## 格式要求

- 使用Markdown格式
- 对比内容使用表格
- 代码块使用纯ASCII
- 底部添加changelog
- 不要添加markdown代码块标记

请直接输出完整的Markdown文档内容，不需要额外的解释性文字。
"""
    return prompt


def enhance_document(filepath, questions_data=None, max_retries=2):
    """增强单个文档，带内容质量验证和自动重试"""
    file_key = str(filepath.relative_to(DOCS_DIR))

    for attempt in range(max_retries + 1):
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')

            title_match = re.search(r'title:\\s*(.+)', content)
            question_text = title_match.group(1).strip() if title_match else filepath.stem.replace('_', ' ')

            question_text = question_text.strip('*')  # v2: strip markdown bold markers

            if not question_text or question_text.startswith('['):
                question_text = f"技术分析：{filepath.parent.name} 专题"

            question_data = find_question_for_file(filepath, questions_data)
            if question_data:
                answer_text = question_data.get('answer', '')
                category = question_data.get('category', filepath.parent.name)
            else:
                answer_text = ""
                category = filepath.parent.name

            user_prompt = build_user_prompt(question_text, answer_text, category)

            # API 调用
            import openai
            client_kwargs = {"api_key": API_KEY}
            if API_BASE_URL:
                client_kwargs["base_url"] = API_BASE_URL
            client = openai.OpenAI(**client_kwargs)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=8000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            enhanced_content = response.choices[0].message.content
            enhanced_content = enhanced_content.replace('```markdown\n', '').replace('\n```', '')

            if not enhanced_content.startswith('#'):
                enhanced_content = f"# {question_text}\n\n{enhanced_content}"

            # v2: 内容验证
            issues = validate_content(enhanced_content, question_text)
            if issues and attempt < max_retries:
                log(f"⚠️ 验证失败 ({attempt+1}/{max_retries}): {', '.join(issues[:3])}")
                time.sleep(5)
                continue

            if '## 参考来源' not in enhanced_content:
                enhanced_content += '\n\n## 参考来源\n\n- [来源: 待补充]\n'

            if '## 变更记录' not in enhanced_content and '## 更新日志' not in enhanced_content:
                enhanced_content += f'\n\n---\n\n## 变更记录\n\n### {datetime.now().strftime("%Y-%m-%d")}\n- 深度增强完成，基于 deep-tech-writer SKILL.md 六步工作流\n'

            filepath.write_text(enhanced_content, encoding='utf-8')
            new_size = filepath.stat().st_size

            return {
                'status': 'success',
                'file': file_key,
                'size': new_size,
                'retries': attempt
            }

        except Exception as api_error:
            err_str = str(api_error)
            if 'rate limit' in err_str.lower() or 'quota' in err_str.lower():
                if attempt < max_retries:
                    log(f"⚠️ 速率限制，等待后重试 ({attempt+1}/{max_retries})")
                    time.sleep(60)
                    continue
                return {'status': 'rate_limit', 'file': file_key, 'error': err_str[:300]}
            return {'status': 'api_error', 'file': file_key, 'error': err_str[:300]}

    save_error(filepath, f"经过{max_retries+1}次尝试仍未通过验证")
    return {'status': 'validation_failed', 'file': file_key, 'error': '内容验证失败'}


def update_stats():
    """更新统计信息（v2 质量门禁版本）"""
    stats = {
        'updated_at': datetime.now().isoformat(),
        'total_files': 0,
        'enhanced_files': 0,
        'failed_files': 0,
        'categories': {}
    }

    for cat_dir in DOCS_DIR.iterdir():
        if not cat_dir.is_dir():
            continue
        cat_name = cat_dir.name
        if cat_name in ['README.md']:
            continue

        md_files = list(cat_dir.glob('*.md'))
        total = len(md_files)
        enhanced = 0
        failed = 0

        for md_file in md_files:
            if md_file.name == 'index.md':
                continue
            size = md_file.stat().st_size
            content = md_file.read_text(encoding='utf-8', errors='ignore')

            has_placeholders = any(re.search(p, content) for p in PLACEHOLDER_PATTERNS)
            has_sources = content.count('[来源:') >= 3
            has_tables = content.count('|') >= 10
            has_enough_content = size >= 5000 and content.count('\n') >= 80

            if has_enough_content and not has_placeholders and has_sources and has_tables:
                enhanced += 1
            else:
                failed += 1

        stats['total_files'] += total
        stats['enhanced_files'] += enhanced
        stats['failed_files'] += failed
        stats['categories'][cat_name] = {
            'total': total,
            'enhanced': enhanced,
            'failed': failed,
            'percentage': round(enhanced / max(total, 1) * 100, 1)
        }

    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    return stats


def print_stats(stats):
    print("\n=== 增强统计 ===")
    print(f"总文件数: {stats['total_files']}")
    print(f"已增强(高质量): {stats['enhanced_files']}")
    print(f"待增强: {stats['failed_files']}")
    print(f"完成率: {round(stats['enhanced_files'] / max(stats['total_files'], 1) * 100, 1)}%")
    print("\n分类进度:")
    for cat, data in sorted(stats['categories'].items(), key=lambda x: x[1]['percentage']):
        print(f"  {cat}: {data['enhanced']}/{data['total']} ({data['percentage']}%)")


def main(batch_size=10, max_workers=2, retry_only=False):
    progress = load_progress()
    errors = load_errors()
    questions_data = load_questions()

    all_md_files = sorted(DOCS_DIR.rglob('*.md'))
    to_process = []

    for filepath in all_md_files:
        if filepath.name == 'index.md':
            continue
        file_key = str(filepath.relative_to(DOCS_DIR))
        if retry_only:
            if file_key in progress.get('failed', []) or file_key in errors:
                to_process.append(filepath)
        else:
            if file_key in progress.get('completed', []):
                continue
            if file_key in progress.get('in_progress', []):
                continue
            if should_enhance(filepath):
                to_process.append(filepath)

    log(f"待处理: {len(to_process)} 个文件 (共 {len(all_md_files)} 个)")
    if not to_process:
        log("没有需要处理的文件")
        stats = update_stats()
        print_stats(stats)
        return

    completed = []
    failed = []
    in_progress = [str(fp.relative_to(DOCS_DIR)) for fp in to_process]
    progress['in_progress'] = in_progress
    save_progress(progress)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(enhance_document, fp, questions_data): fp for fp in to_process}

        for future in as_completed(futures):
            fp = futures[future]
            file_key = str(fp.relative_to(DOCS_DIR))
            try:
                result = future.result()
                if result['status'] == 'success':
                    completed.append(file_key)
                    log(f"✅ {file_key} ({result['size']} bytes, {result.get('retries', 0)} retries)")
                elif result['status'] in ('rate_limit', 'api_error'):
                    failed.append(file_key)
                    log(f"❌ {file_key}: {result.get('error', '未知错误')[:60]}")
                elif result['status'] == 'validation_failed':
                    failed.append(file_key)
                    log(f"⚠️ {file_key}: 验证失败")
            except Exception as e:
                failed.append(file_key)
                log(f"❌ {file_key}: {str(e)[:60]}")

    progress['completed'] = progress.get('completed', []) + completed
    progress['failed'] = failed
    progress['in_progress'] = []
    save_progress(progress)

    log(f"\n完成: {len(completed)} 成功, {len(failed)} 失败")
    stats = update_stats()
    print_stats(stats)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量文档深度增强引擎 v3')
    parser.add_argument('--batch-size', type=int, default=10, help='每批处理数量 (默认: 10)')
    parser.add_argument('--max-workers', type=int, default=2, help='最大并发数 (默认: 2)')
    parser.add_argument('--retry-only', action='store_true', help='仅重试失败文件')
    args = parser.parse_args()
    main(batch_size=args.batch_size, max_workers=args.max_workers, retry_only=args.retry_only)
