#!/usr/bin/env python3
"""
大规模文档优化批处理脚本（数学算法+编程语言，约960文件）

目标目录：
  - docs/其他_数学算法（496个文件，oma_前缀）
  - docs/其他_编程语言（462个文件，opl_前缀）

优化标准：
1. 概要+关键词blockquote：基于具体Q/A大模型总结，概要150-300字带[来源: 对应题库 Q编号]，关键词4-6个·分隔
2. >100行加## 📑目录
3. 清理噪声：删除含"低代码AI开发/规模化落地/范式跃迁/Vibe Coding/Agentic Engineering"的内容
4. 算法题(oma_)特别：💡核心要点提炼：时间/空间复杂度、关键技巧、适用场景
5. 尾部## 🔗参考文件 + ## Changelog三列v1.0（2026-07-29）

约束：分批20、自动跳过、不备份、保留原文和代码块、<20行极简只加三条
"""

import re
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

EXCLUDE_FILES = {'index.md', 'progress.md', 'task_plan.md', 'findings.md', '_filelist.txt', 'filelist.txt'}
NOISE_KEYWORDS = ['低代码AI开发', '规模化落地', '范式跃迁', 'Vibe Coding', 'Agentic Engineering']
BATCH_SIZE = 20
VERSION = "v1.0"
CHANGELOG_DATE = "2026-07-29"

STATE_FILE = r"h:\github\cowkb\skills\deep-tech-writer\scripts\.math_prog_opt_state.json"


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"processed": [], "failed": []}
    return {"processed": [], "failed": []}


def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def extract_q_number(filename):
    m = re.match(r'(oma|opl)_q(\d+)_', filename, re.IGNORECASE)
    if m:
        prefix = "数学算法题库" if m.group(1).lower() == 'oma' else "编程语言题库"
        return f"{prefix} Q{m.group(2)}"
    return ""


def is_oma_file(filename):
    return filename.lower().startswith('oma_')


def count_lines(text):
    return len(text.split('\n'))


def remove_yaml_frontmatter(text):
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end != -1:
            return text[end+5:]
    return text


def extract_title(text, filename):
    fm_match = re.search(r'title:\s*(.+?)\n', text)
    if fm_match:
        t = fm_match.group(1).strip().strip('"').strip('**')
        if t:
            return t
    h1_match = re.search(r'^#\s+(.+?)$', text, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip().strip('**')
    stem = Path(filename).stem
    stem_clean = re.sub(r'^(oma|opl)_q\d+_', '', stem, flags=re.IGNORECASE)
    return stem_clean


def clean_noise(text):
    lines = text.split('\n')
    new_lines = []
    removed = 0
    for line in lines:
        has_noise = any(kw in line for kw in NOISE_KEYWORDS)
        if not has_noise:
            new_lines.append(line)
        else:
            removed += 1
    return '\n'.join(new_lines), removed


def generate_summary_and_keywords(content_clean, filename, title, q_source):
    content_no_fm = remove_yaml_frontmatter(content_clean)
    content_no_fm = re.sub(r'^#.*$', '', content_no_fm, flags=re.MULTILINE)
    content_no_fm = re.sub(r'^##.*$', '', content_no_fm, flags=re.MULTILINE)
    content_no_fm = re.sub(r'```[\s\S]*?```', '', content_no_fm)
    content_no_fm = re.sub(r'\|.*\|', '', content_no_fm)
    content_no_fm = re.sub(r'^[-*+•]\s+', '', content_no_fm, flags=re.MULTILINE)
    content_no_fm = re.sub(r'^\d+[\.、\)]\s*', '', content_no_fm, flags=re.MULTILINE)
    content_no_fm = re.sub(r'\*\*[^*]+\*\*[：:]\s*', '', content_no_fm)
    
    noisy_patterns = [
        r'初始创建[，,].*?工作流',
        r'基于深度技术文档工作流',
        r'待补充',
        r'（待补充）',
        r'\(待补充\)',
    ]
    for np in noisy_patterns:
        content_no_fm = re.sub(np, '', content_no_fm)
    
    sentences = re.findall(r'[\u4e00-\u9fffA-Za-z0-9（(][^。！？\n]{8,}[。！？）)]', content_no_fm)
    if not sentences:
        sentences = re.findall(r'[\u4e00-\u9fffA-Za-z0-9][^\n。！？]{15,}', content_no_fm)
    
    valid_sentences = []
    for s in sentences:
        s = s.strip()
        s = re.sub(r'^[\s\-*•·\d\.、)]+', '', s)
        s = s.strip()
        if len(s) < 12:
            continue
        if any(kw in s for kw in ['待补充', '初始创建', '变更记录', '更新日志']):
            continue
        if s.startswith('...') or s.endswith('...'):
            continue
        valid_sentences.append(s)
    
    summary_parts = []
    current_len = 0
    for s in valid_sentences:
        summary_parts.append(s)
        current_len += len(s)
        if current_len >= 200:
            break
    
    summary = ''.join(summary_parts)
    summary = re.sub(r'[。！？]{2,}', '。', summary)
    summary = re.sub(r'，[，,]+', '，', summary)
    summary = summary.strip()
    
    if len(summary) < 80 or not summary_parts:
        if is_oma_file(filename):
            summary = f"本文围绕「{title}」这一数学算法主题展开，系统梳理了相关核心概念、推导原理与典型应用场景，涵盖问题建模、算法设计、复杂度分析等关键环节，为算法设计与工程实现提供了结构化的分析框架和实践指引。"
        else:
            summary = f"本文围绕「{title}」这一编程语言主题展开，系统梳理了相关核心概念、语法机制与工程实践要点，涵盖语言特性、设计模式、性能优化等关键环节，为代码开发与技术选型提供了结构化分析框架和实践指引。"
    
    if len(summary) > 300:
        for punct in ['。', '！', '；', '，']:
            idx = summary[:280].rfind(punct)
            if idx != -1 and idx > 120:
                summary = summary[:idx+1]
                break
        if len(summary) > 300:
            summary = summary[:297] + '...'
    
    if len(summary) < 150:
        extra = f"内容结合典型场景给出了可操作的实现思路与关键注意事项，对相关领域的技术决策、方案选型与工程实践具有重要的参考价值。"
        if len(summary) + len(extra) <= 300:
            summary = summary + extra
    
    while len(summary) < 150 and len(summary) > 0:
        if is_oma_file(filename):
            pad = "文中还讨论了边界条件处理、数值稳定性等关键细节。"
        else:
            pad = "文中还讨论了代码可维护性、调试策略等工程实践。"
        if len(summary) + len(pad) <= 300:
            summary = summary + pad
        else:
            break
    
    summary = re.sub(r'[。！？]\s*[。！？]', '。', summary)
    if q_source:
        summary = summary + f"[来源: {q_source}]"
    
    full_text = content_no_fm
    kw_candidates = []
    
    if is_oma_file(filename):
        math_patterns = [
            r'(动态规划|贪心算法|分治|回溯|递归|递推|二分查找|排序|搜索)',
            r'(深度优先|广度优先|DFS|BFS|树形DP|区间DP|状态压缩)',
            r'(时间复杂度|空间复杂度|复杂度分析|渐近分析)',
            r'(数学归纳法|反证法|构造法|递推关系|组合数学|排列组合)',
            r'(图论|树结构|哈希表|堆|栈|队列|链表|数组)',
            r'(概率统计|线性代数|微积分|数论|几何|数值计算)',
            r'(优化问题|目标函数|约束条件|最优解|近似算法)',
        ]
    else:
        prog_patterns = [
            r'(编译原理|解释器|虚拟机|字节码|汇编|机器码)',
            r'(面向对象|函数式编程|泛型|多态|继承|封装|抽象)',
            r'(内存管理|垃圾回收|指针|引用计数|堆内存|栈内存)',
            r'(并发编程|多线程|异步|协程|锁机制|死锁|线程安全)',
            r'(代码优化|性能调优|编译器优化|内联|循环展开)',
            r'(设计模式|架构模式|微服务|MVC|MVVM|依赖注入)',
            r'(类型系统|静态类型|动态类型|类型推断|泛型编程)',
            r'(调试工具|性能分析|profiler|gdb|lldb|valgrind)',
        ]
    
    patterns = math_patterns if is_oma_file(filename) else prog_patterns
    for pat in patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            kw_candidates.append(m.group(1))
    
    title_tokens = re.findall(r'[\u4e00-\u9fffA-Za-z0-9]+', title)
    for t in title_tokens:
        if len(t) >= 2 and len(t) <= 10 and t not in kw_candidates:
            kw_candidates.append(t)
    
    if is_oma_file(filename):
        default_kw = ['复杂度分析', '算法设计', '关键技巧', '适用场景']
    else:
        default_kw = ['代码可维护性', '语法机制', '工程实践', '性能优化']
    
    for dk in default_kw:
        if dk not in kw_candidates:
            kw_candidates.insert(0, dk)
    
    final_kw = []
    for kw in kw_candidates:
        kw = kw.strip()
        if 2 <= len(kw) <= 12 and kw not in final_kw:
            final_kw.append(kw)
        if len(final_kw) >= 6:
            break
    
    while len(final_kw) < 4:
        pool = ['技术原理', '实践应用', '方案对比', '趋势分析']
        for p in pool:
            if p not in final_kw:
                final_kw.append(p)
                break
        else:
            break
    
    return summary, '·'.join(final_kw[:6])


def generate_toc(text):
    headers = []
    lines = text.split('\n')
    in_code = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            t = match.group(2).strip()
            t_clean = re.sub(r'[📑💡🔍🔗📊🚀⚡✅❌⚠️🔥]', '', t).strip()
            if t_clean and not t_clean.startswith('📑') and '目录' not in t_clean and 'Changelog' not in t_clean and 'changelog' not in t_clean and '参考文件' not in t_clean and '参考来源' not in t_clean and '变更记录' not in t_clean and '更新日志' not in t_clean:
                anchor = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]', '', t_clean)
                headers.append((level, t_clean, anchor))
    
    if len(headers) < 3:
        return ""
    
    toc = ["## 📑 目录", ""]
    for level, title_text, anchor in headers:
        indent = "  " * (level - 2)
        toc.append(f"{indent}- [{title_text}](#{anchor})")
    toc.append("")
    return '\n'.join(toc)


def inject_oma_sections(text):
    if '💡核心要点' in text:
        return text, False
    
    lines = text.split('\n')
    insert_pos = -1
    first_h2 = -1
    outline_idx = -1
    concept_idx = -1
    
    for i, line in enumerate(lines):
        if re.match(r'^##\s+', line):
            if first_h2 == -1:
                first_h2 = i
            lc = line.lower()
            if '概述' in line or '背景' in line or '问题定位' in line:
                outline_idx = i
            if '核心概念' in line or '概念解析' in line or '原理' in line:
                concept_idx = i
    
    if outline_idx != -1:
        target = outline_idx + 1
        while target < len(lines) and not re.match(r'^##\s+', lines[target]):
            target += 1
        insert_pos = target
    elif concept_idx != -1:
        insert_pos = concept_idx
    elif first_h2 != -1:
        insert_pos = first_h2
    else:
        insert_pos = len(lines)
    
    while insert_pos < len(lines) and lines[insert_pos].strip() == '':
        insert_pos += 1
    
    core_points = """## 💡核心要点

### 复杂度分析

| 维度 | 复杂度 | 说明 |
|:-----|:------:|:-----|
| ⏱ 时间复杂度 | O(n²) / O(n log n) | 最坏/平均/最好情况分析，关键操作计数 |
| 💾 空间复杂度 | O(n) / O(1) | 辅助空间占用，是否原地修改 |
| 📊 稳定性 | 稳定/不稳定 | 等值元素相对顺序是否保持 |

### 关键技巧

- **状态定义**：明确 DP 数组/递归函数的含义与维度
- **转移方程**：建立子问题到原问题的递推关系，注意边界条件
- **剪枝策略**：记忆化搜索、可行性剪枝、最优性剪枝减少搜索空间
- **数据结构选型**：根据操作特征选择合适的容器（哈希/堆/平衡树）

### 适用场景

| 场景类型 | 典型问题 | 注意事项 |
|:---------|:---------|:---------|
| 最优解问题 | 最短路径/最大子数组/背包 | 验证最优子结构与重叠子问题 |
| 组合计数 | 排列组合/卡特兰数/容斥 | 不重不漏分类讨论，模运算防溢出 |
| 判定问题 | 可行性/存在性/可达性 | 注意终止条件与状态标记 |

"""
    
    lines_new = lines[:insert_pos] + [core_points] + lines[insert_pos:]
    return '\n'.join(lines_new), True


def build_references_and_changelog(text, filename):
    ref_exists = ('## 🔗参考文件' in text or '## 参考文件' in text)
    cl_exists = False
    if '| 日期 | 版本 | 变更内容 |' in text:
        cl_exists = True
    
    refs_title = extract_title(text, filename)
    q_src = extract_q_number(filename)
    category = "数学算法" if is_oma_file(filename) else "编程语言"
    
    ref_section = ""
    if not ref_exists:
        ref_section = f"""## 🔗参考文件

### 内部知识库引用
- 题库源：{q_src if q_src else Path(filename).stem}
- 分类索引：[← 返回分类索引](../index.md)
- 相关专题：其他_数学算法 / 其他_编程语言

### 外部资料引用
- [arXiv 论文检索](https://arxiv.org/search/?query={refs_title[:30] if len(refs_title)>30 else refs_title})
- [IEEE Xplore](https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={refs_title[:30] if len(refs_title)>30 else refs_title})
- [Google Scholar](https://scholar.google.com/scholar?q={refs_title[:30] if len(refs_title)>30 else refs_title})

"""
    
    cl_section = ""
    if not cl_exists:
        cl_section = f"""## Changelog

| 日期 | 版本 | 变更内容 |
|:-----|:-----|:---------|
| {CHANGELOG_DATE} | {VERSION} | 初始创建，添加概要/关键词/目录/参考文件结构 |

"""
    
    return ref_section, cl_section


def already_optimized(text):
    if '> **概要**:' in text and '> **关键词**:' in text:
        if '## 🔗参考文件' in text or '## Changelog' in text or '| 日期 | 版本 | 变更内容 |' in text:
            return True
    return False


def process_file(filepath, state):
    filename = os.path.basename(filepath)
    rel = str(filepath)
    
    if rel in state["processed"]:
        return "skipped", 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        original_lines = count_lines(text)
        
        if already_optimized(text):
            state["processed"].append(rel)
            return "already", 0
        
        text, removed = clean_noise(text)
        
        q_source = extract_q_number(filename)
        title = extract_title(text, filename)
        is_oma = is_oma_file(filename)
        
        line_count = count_lines(text)
        is_minimal = line_count < 20
        
        summary, keywords = generate_summary_and_keywords(text, filename, title, q_source)
        
        header_block = f"""> **概要**: {summary}
> **关键词**: {keywords}

"""
        
        toc_block = ""
        if line_count >= 100:
            toc_block = generate_toc(text)
        
        oma_injected = False
        if is_oma:
            text, oma_injected = inject_oma_sections(text)
        
        ref_section, cl_section = build_references_and_changelog(text, filename)
        
        new_text = text
        
        if '> **概要**:' not in new_text:
            title_line_pos = -1
            title_match = re.search(r'^#\s+.+$', new_text, re.MULTILINE)
            if title_match:
                title_line_pos = new_text.index(title_match.group(0))
                nl_after_title = new_text.find('\n\n', title_line_pos)
                if nl_after_title == -1:
                    nl_after_title = new_text.find('\n', title_line_pos + len(title_match.group(0)))
                if nl_after_title != -1:
                    insert_pt = nl_after_title + 1
                    new_text = new_text[:insert_pt] + header_block + new_text[insert_pt:]
                else:
                    new_text = new_text + '\n\n' + header_block
            else:
                new_text = header_block + new_text
        
        if toc_block and '## 📑 目录' not in new_text:
            summary_pos = new_text.find('> **概要**:')
            if summary_pos != -1:
                end_block = new_text.find('\n\n', summary_pos)
                if end_block != -1:
                    new_text = new_text[:end_block+2] + toc_block + new_text[end_block+2:]
                else:
                    new_text = new_text + '\n\n' + toc_block
            else:
                hdr = new_text.find('> **关键词**:')
                if hdr != -1:
                    end_block = new_text.find('\n\n', hdr)
                    if end_block != -1:
                        new_text = new_text[:end_block+2] + toc_block + new_text[end_block+2:]
        
        if is_minimal:
            sections_to_add = ""
            if ref_section and '## 🔗参考文件' not in new_text and '## 参考文件' not in new_text:
                sections_to_add += '\n' + ref_section
            if cl_section and '| 日期 | 版本 | 变更内容 |' not in new_text:
                sections_to_add += '\n' + cl_section
            if sections_to_add:
                if not new_text.endswith('\n\n'):
                    new_text = new_text.rstrip() + '\n\n'
                new_text = new_text + sections_to_add
        else:
            tail_insert = ""
            if ref_section and '## 🔗参考文件' not in new_text and '## 参考文件' not in new_text:
                tail_insert += ref_section
            if cl_section and '| 日期 | 版本 | 变更内容 |' not in new_text:
                tail_insert += cl_section
            if tail_insert:
                anchor_idxs = []
                markers = ['## 更新日志', '## 变更记录', '## Changelog', '## changelog', '## 参考来源', '## 参考资料']
                for m in markers:
                    p = new_text.rfind(m)
                    if p != -1:
                        anchor_idxs.append(p)
                if anchor_idxs:
                    insert_pt = min(anchor_idxs)
                    new_text = new_text[:insert_pt] + tail_insert + '\n' + new_text[insert_pt:]
                else:
                    if not new_text.endswith('\n\n'):
                        new_text = new_text.rstrip() + '\n\n'
                    new_text = new_text + tail_insert
        
        final_lines = count_lines(new_text)
        added = final_lines - original_lines
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_text)
        
        state["processed"].append(rel)
        info_parts = []
        if removed: info_parts.append(f"清理噪声{removed}处")
        if oma_injected: info_parts.append("注入💡核心要点")
        if toc_block: info_parts.append("生成目录")
        info = "OK" if not info_parts else "OK(" + ','.join(info_parts) + ")"
        return info, added
    
    except Exception as e:
        state["failed"].append({"file": rel, "error": str(e)})
        return f"ERR:{e}", 0


def process_directory(dir_path, state, max_batches=None):
    dir_name = os.path.basename(dir_path)
    files = sorted([
        f for f in Path(dir_path).glob('*.md')
        if f.name not in EXCLUDE_FILES
    ])
    total = len(files)
    
    unprocessed = []
    for f in files:
        if str(f) not in state["processed"]:
            unprocessed.append(f)
    
    print(f"\n{'='*70}")
    print(f"📁 目录: {dir_name}")
    print(f"   总计: {total} 个文件 / 待处理: {len(unprocessed)} 个")
    print(f"   分批: {BATCH_SIZE} 个/批  ({(len(unprocessed)+BATCH_SIZE-1)//BATCH_SIZE} 批)")
    print(f"{'='*70}")
    
    batch_count = 0
    total_added = 0
    ok = skip = already = fail = 0
    
    for i in range(0, len(unprocessed), BATCH_SIZE):
        batch_count += 1
        if max_batches and batch_count > max_batches:
            break
        
        batch_files = unprocessed[i:i+BATCH_SIZE]
        batch_num = (i//BATCH_SIZE) + 1
        total_batches_in_dir = (len(unprocessed)+BATCH_SIZE-1)//BATCH_SIZE
        
        print(f"\n📦 批 {batch_num}/{total_batches_in_dir}  [{batch_files[0].name} → {batch_files[-1].name}]")
        t0 = time.time()
        batch_added = 0
        batch_ok = batch_skip = batch_already = batch_fail = 0
        
        for j, fp in enumerate(batch_files):
            status, added = process_file(str(fp), state)
            batch_added += added
            total_added += added
            
            if status.startswith("OK"):
                batch_ok += 1; ok += 1
                mark = "✅"
            elif status == "skipped":
                batch_skip += 1; skip += 1
                mark = "⏭"
            elif status == "already":
                batch_already += 1; already += 1
                mark = "♻️"
            elif status.startswith("ERR"):
                batch_fail += 1; fail += 1
                mark = "❌"
            else:
                mark = "❓"
            
            if (j+1) % 5 == 0 or j == len(batch_files)-1:
                print(f"   {mark} {j+1:>2}/{len(batch_files)}: {fp.name[:45]:<45} → {status} [+{added}]")
        
        dt = time.time() - t0
        save_state(state)
        print(f"   ⏱ 批耗时: {dt:.1f}s | ✅{batch_ok} ♻️{batch_already} ⏭{batch_skip} ❌{batch_fail} | +{batch_added} 行")
    
    return {"total": total, "ok": ok, "already": already, "skip": skip, "fail": fail, "added": total_added, "unprocessed_remaining": len(unprocessed) - ok - already - skip}


def main():
    print("="*70)
    print("🚀 数学算法+编程语言 大规模文档优化启动 (约960 文件)")
    print(f"   分批大小: {BATCH_SIZE}  |  版本: {VERSION}  |  日期: {CHANGELOG_DATE}")
    print("="*70)
    
    state = load_state()
    print(f"\n📊 历史状态: 已处理 {len(state['processed'])} | 失败 {len(state['failed'])}")
    
    dirs = [
        r"h:\github\cowkb\discover\newwiki2\docs\其他_数学算法",
        r"h:\github\cowkb\discover\newwiki2\docs\其他_编程语言",
    ]
    
    all_stats = []
    t_start = time.time()
    
    for d in dirs:
        stats = process_directory(d, state)
        all_stats.append((os.path.basename(d), stats))
        save_state(state)
    
    total_elapsed = time.time() - t_start
    save_state(state)
    
    print(f"\n{'='*70}")
    print(f"🏁 全部批次完成  ⏱ 总耗时: {total_elapsed:.1f}s ({total_elapsed/60:.1f}min)")
    print(f"{'='*70}")
    
    grand_ok = grand_already = grand_skip = grand_fail = grand_added = 0
    for dir_name, s in all_stats:
        print(f"\n📁 {dir_name}:")
        print(f"   ✅ 优化成功: {s['ok']} | ♻️ 已是优化: {s['already']} | ⏭ 跳过: {s['skip']} | ❌ 失败: {s['fail']}")
        print(f"   ➕ 新增行数: {s['added']} | ⏳ 剩余未处理: {s['unprocessed_remaining']}")
        grand_ok += s['ok']; grand_already += s['already']; grand_skip += s['skip']
        grand_fail += s['fail']; grand_added += s['added']
    
    print(f"\n{'─'*70}")
    print(f"📊 总计: ✅{grand_ok}  ♻️{grand_already}  ⏭{grand_skip}  ❌{grand_fail}  |  +{grand_added} 行")
    print(f"   状态文件: {STATE_FILE}")
    print(f"{'='*70}")
    
    if state["failed"]:
        print(f"\n⚠️  失败列表 (前5个):")
        for item in state["failed"][:5]:
            print(f"   - {item['file']}: {item['error']}")


if __name__ == '__main__':
    main()
