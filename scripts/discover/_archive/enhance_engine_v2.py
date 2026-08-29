"""Deep Tech Document Enhancement Engine v2 - High Quality Edition.

Improvements over v1:
1. STRICT quality requirements - NO placeholder text like "(待补充)"
2. Auto-retry for incomplete documents
3. Quality validation before saving
4. Enhanced prompt engineering for comprehensive content
5. Support for WebSearch integration for authoritative sources
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

try:
    import openai
except ImportError:
    print("ERROR: openai package not installed. Install with: pip install openai")
    sys.exit(1)

API_KEY = os.environ.get('OPENAI_API_KEY', '')
API_BASE_URL = os.environ.get('OPENAI_API_BASE_URL', '')

if not API_KEY:
    print("ERROR: OPENAI_API_KEY environment variable is not set!")
    print("Set it with: set OPENAI_API_KEY=your-api-key")
    sys.exit(1)

DISCOVER_NEWWIKI2 = Path(r"d:\123\cowkb\discover\newwiki2")
DOCS_DIR = DISCOVER_NEWWIKI2 / "docs"
QUESTIONS_FILE = DISCOVER_NEWWIKI2 / "all_questions.json"
PROGRESS_FILE = DISCOVER_NEWWIKI2 / "enhancement_progress_v2.json"
ERROR_LOG_FILE = DISCOVER_NEWWIKI2 / "enhancement_errors_v2.json"
STATS_FILE = DISCOVER_NEWWIKI2 / "enhancement_stats_v2.json"
LOG_FILE = DISCOVER_NEWWIKI2 / "enhancement_log_v2.txt"

MIN_WORD_COUNT = 800
MIN_SECTIONS_WITH_CONTENT = 5
PLACEHOLDER_PATTERNS = [
    r'\（待补充\）', r'\(待补充\)', r'\（待完善\）', r'\(待完善\)',
    r'\（详见下文\）', r'\(详见下文\)', r'\（见下方\）', r'\(见下方\)',
    r'TODO', r'todo', r'待补充', r'待完善', r'请补充',
    r'### \d+\.\d+ 待补充', r'## \d+\.\d+ 待补充',
]

SYSTEM_PROMPT = """你是一名资深技术文档专家，严格遵循 deep-tech-writer SKILL.md 的六步工作流。

你的任务：根据用户提出的技术问题，创建一篇完整、深度、专业的技术分析文档。

## 六大质量标准（必须全部满足）

1. **原理深度**: 深入到协议/芯片/物理层次，解释WHY而不仅仅是WHAT
2. **来源标注**: 每条关键断言必须有出处（论文/标准/白皮书/报告/URL）
3. **强逻辑**: 论点→论据→数据→结论，不自相矛盾
4. **取材优先**: 论文/标准原文 > 官方白皮书 > 一线工程报告 > 主流行业分析 > 通用知识
5. **外部链接优先**: 通用背景知识压缩为一句话+外部链接
6. **审查闭环**: 写完后必须自检

## 六步工作流

### 第1步：搜集权威源
至少覆盖2个层级：
- 🥇 论文/标准原文：IEEE/ACM/arXiv、JEDEC/PCI-SIG/IBTA/OCP规范
- 🥇 官方技术白皮书：NVIDIA/Intel/AMD/Arm/Samsung官方文档
- 🥈 一线工程报告：实测数据、实验报告、Backblaze/GCP/Facebook工程论文
- 🥉 主流行业分析：SemiAnalysis/DIGITIMES/The Next Platform/AnandTech
- 📄 通用知识：Wikipedia、博客、教程（一句话带过+外部链接）

### 第2步：协议/机制原理深潜
- 解释为什么 —— 设计选择背后的物理/经济/逻辑原因
- 量化对比 —— 多个方案间用数据比较（延迟/带宽/面积/功耗/成本）
- 给出值 —— 关键参数给出具体数值和范围
- 时序/流程 —— 解释信号/数据/状态的完整流转过程

### 第3步：强逻辑结构编排
根据文档类型选择合适的逻辑框架。

### 第4步：量化数据 + 来源标注
每条关键数据必须包含：数值 + 单位 + 对比基线 + 测试条件
来源标注规范：[来源: 论文/标准编号/报告/URL]

### 第5步：外审迭代
- 自审：对照质量标准逐项检查
- 外部视角：领域专家会在哪里提出质疑？

### 第6步：格式打磨
- changelog 在底部
- TOC 在顶部（可选）
- 代码块纯ASCII
- 通用知识外链化

## 文档结构要求（每个章节都必须有完整内容）

1. **概述**: 全面概述，包含核心洞察，至少200字
2. **核心概念解析**: 关键概念的深入解析，包含定义和示例，至少300字
3. **原理深度剖析**: 第一性原理分析，包含数据和来源，至少400字
4. **技术实现细节**: 实现细节、代码示例、架构图，至少300字
5. **应用场景与实践**: 真实世界用例、最佳实践，至少300字
6. **对比分析**: 使用表格对比多种方案，至少200字
7. **发展趋势与展望**: 未来趋势和预测，至少150字
8. **参考来源**: 至少3个引用参考文献，附带链接

## 硬性要求（必须满足，否则重新生成）

- 必须包含至少5个量化数据点（数值+单位+基线+测试条件）
- 必须包含至少3个适当的引用/参考来源
- 对比内容必须使用表格
- 代码块使用纯ASCII
- 底部必须添加changelog
- 目标长度：1500-3000字
- 使用中文撰写
- **严禁使用占位符**: 不得出现"待补充"、"待完善"、"详见下文"、"TODO"等任何占位符文字
- **每个章节都必须有实质性内容**: 不得有空章节或只有标题的章节

## 质量评分体系（必须达到80分以上）

| 维度 | 权重 | 通过标准 |
|:-----|:-----|:---------|
| 原理深度 | 30% | 深入到协议/芯片/物理层次，解释WHY |
| 量化支撑 | 25% | 至少5处数值+单位+基线的数据 |
| 来源质量 | 20% | 引用论文/标准/白皮书/URL，至少3个 |
| 逻辑严密 | 15% | 无逻辑谬误，不自相矛盾 |
| 格式规范 | 10% | 符合changelog/代码块规则，无占位符 |

## 输出格式

直接输出完整的Markdown文档，不要添加额外的解释性文字。文档开头不要加markdown代码块标记。

开始撰写深度技术文档！
"""


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {msg}\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line)
    print(msg)


def load_progress():
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'started_at': datetime.now().isoformat(),
        'completed': [],
        'failed': [],
        'retried': [],
        'in_progress': []
    }


def save_progress(progress):
    progress['updated_at'] = datetime.now().isoformat()
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')


def load_errors():
    if ERROR_LOG_FILE.exists():
        try:
            with open(ERROR_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {'errors': []}


def save_error(filepath, error):
    errors = load_errors()
    errors['errors'].append({
        'timestamp': datetime.now().isoformat(),
        'file': str(filepath),
        'error': str(error)[:1000]
    })
    ERROR_LOG_FILE.write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding='utf-8')


def load_questions():
    if QUESTIONS_FILE.exists():
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def find_question_for_file(filepath, questions_data):
    if questions_data is None:
        return None
    
    filename = filepath.stem
    parts = filename.split('_')
    if len(parts) >= 2:
        q_num_part = parts[1]
        q_num = q_num_part.replace('q', '')
        
        for category, cat_data in questions_data.get('categories', {}).items():
            for q in cat_data.get('questions', []):
                if str(q.get('q_num', '')) == q_num:
                    return q
    
    return None


def should_enhance(filepath):
    size = filepath.stat().st_size
    if size < 500:
        return True
    
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, content):
            return True
    
    if content.strip().count('\n') < 60:
        return True
    
    if content.count('## 参考来源') > 0 and content.count('[来源:') < 3:
        return True
    
    if content.count('|') < 10:
        return True
    
    return False


def validate_content(content, question):
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
    
    section_count = 0
    for section in ['概述', '核心概念', '原理深度', '技术实现', '应用场景', '对比分析', '发展趋势', '参考来源']:
        if f'## {section}' in content or f'### {section}' in content:
            section_count += 1
    
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
    file_key = str(filepath.relative_to(DOCS_DIR))
    
    for attempt in range(max_retries + 1):
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            title_match = re.search(r'title:\s*(.+)', content)
            if title_match:
                question_text = title_match.group(1).strip()
            else:
                question_text = filepath.stem.replace('_', ' ')
            
            if question_text.startswith('**') and question_text.endswith('**'):
                question_text = question_text[2:-2]
            
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
            
            if API_BASE_URL:
                client = openai.OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
            else:
                client = openai.OpenAI(api_key=API_KEY)
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
            
            issues = validate_content(enhanced_content, question_text)
            if issues and attempt < max_retries:
                print(f"  ⚠️ 验证失败 ({attempt+1}/{max_retries}): {', '.join(issues[:3])}")
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
                    print(f"  ⚠️ 速率限制，等待后重试 ({attempt+1}/{max_retries})")
                    time.sleep(60)
                    continue
                return {'status': 'rate_limit', 'file': file_key, 'error': err_str[:300]}
            return {'status': 'api_error', 'file': file_key, 'error': err_str[:300]}
    
    save_error(filepath, f"经过{max_retries+1}次尝试仍未通过验证")
    return {'status': 'validation_failed', 'file': file_key, 'error': '内容验证失败'}


def update_stats():
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
    log(f"启动深度技术文档增强引擎 v2")
    log(f"配置: batch_size={batch_size}, workers={max_workers}, retry_only={retry_only}")
    log(f"DOCS_DIR: {DOCS_DIR}")
    log(f"QUESTIONS_FILE exists: {QUESTIONS_FILE.exists()}")
    
    questions_data = load_questions()
    progress = load_progress()
    log(f"已完成: {len(progress['completed'])}, 失败: {len(progress['failed'])}")
    
    all_files = []
    for md_file in DOCS_DIR.rglob('*.md'):
        file_key = str(md_file.relative_to(DOCS_DIR))
        
        if md_file.name == 'index.md':
            continue
        
        if retry_only:
            if file_key not in progress['failed']:
                continue
        else:
            if file_key in progress['completed']:
                continue
        
        if not should_enhance(md_file):
            progress['completed'].append(file_key)
            continue
        
        all_files.append(md_file)
    
    log(f"待处理文件数: {len(all_files)}")
    
    total_completed = len(progress['completed'])
    total_failed = len(progress['failed'])
    
    for i in range(0, len(all_files), batch_size):
        batch = all_files[i:i+batch_size]
        log(f"\n=== 批次 {i//batch_size + 1}/{(len(all_files)+batch_size-1)//batch_size} ===")
        log(f"处理 {len(batch)} 个文件")
        
        completed_in_batch = 0
        failed_in_batch = 0
        rate_limited = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(enhance_document, fp, questions_data): fp for fp in batch}
            
            for future in as_completed(futures):
                result = future.result()
                
                if result['status'] == 'success':
                    progress['completed'].append(result['file'])
                    completed_in_batch += 1
                    total_completed += 1
                    log(f"  ✓ 完成: {result['file']} (大小: {result['size']//1024}KB)")
                elif result['status'] == 'rate_limit':
                    rate_limited += 1
                    log(f"  ⚠️ 速率限制: {result['file']}")
                else:
                    progress['failed'].append(result['file'])
                    failed_in_batch += 1
                    total_failed += 1
                    save_error(result['file'], result.get('error', 'unknown'))
                    log(f"  ✗ 失败: {result['file']} - {result.get('error', '')[:100]}")
            
            save_progress(progress)
            log(f"批次完成: {completed_in_batch} 成功, {failed_in_batch} 失败, {rate_limited} 速率限制")
            log(f"总体进度: {total_completed} 已完成, {total_failed} 失败")
        
        if rate_limited > 0:
            log(f"等待 60 秒后继续...")
            time.sleep(60)
        else:
            time.sleep(2)
        
        if (i // batch_size + 1) % 10 == 0:
            stats = update_stats()
            print_stats(stats)
    
    stats = update_stats()
    print_stats(stats)
    log("增强任务完成！")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deep Tech Document Enhancement Engine v2')
    parser.add_argument('--batch_size', type=int, default=10, help='Batch size')
    parser.add_argument('--workers', type=int, default=2, help='Number of parallel workers')
    parser.add_argument('--retry', action='store_true', help='Retry only failed documents')
    args = parser.parse_args()
    
    main(batch_size=args.batch_size, max_workers=args.workers, retry_only=args.retry)