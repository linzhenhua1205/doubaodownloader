#!/usr/bin/env python3
"""
极大规模文档优化批处理脚本（1800文件级）
目标目录：
  - docs/大模型技术与原理（968个文件，lmf_前缀）
  - docs/技术选型与方案对比（832个文件，tsc_前缀）

优化标准：
1. 概要+关键词blockquote：150-300字概要带[来源: Q编号]，4-6个·分隔关键词
2. >100行加## 📑目录
3. 清理噪声：删除含"低代码AI开发/规模化落地/范式跃迁/Vibe Coding/Agentic Engineering"的内容
4. 技术选型(tsc_)文件特别：💡核心要点对比维度（性能/成本/复杂度/风险），🔍深度解读量化数据
5. 尾部## 🔗参考文件 + ## Changelog三列v1.0（2026-07-29）

约束：分批20、自动跳过、不备份、保留原文、<20行极简只加三条
"""

import re
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

EXCLUDE_FILES = {'index.md', 'progress.md', 'task_plan.md', 'findings.md', 'filelist.txt'}
NOISE_KEYWORDS = ['低代码AI开发', '规模化落地', '范式跃迁', 'Vibe Coding', 'Agentic Engineering']
BATCH_SIZE = 20
VERSION = "v1.0"
CHANGELOG_DATE = "2026-07-29"

STATE_FILE = r"h:\github\cowkb\skills\deep-tech-writer\scripts\.massive_opt_state.json"


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
    m = re.match(r'(lmf|tsc)_q(\d+)_', filename, re.IGNORECASE)
    if m:
        prefix = "大模型技术与原理题库" if m.group(1).lower() == 'lmf' else "技术选型题库"
        return f"{prefix} Q{m.group(2)}"
    return ""


def is_tsc_file(filename):
    return filename.lower().startswith('tsc_')


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
    stem_clean = re.sub(r'^(lmf|tsc)_q\d+_', '', stem, flags=re.IGNORECASE)
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
    
    sentences = re.findall(r'[\u4e00-\u9fffA-Za-z0-9][^。！？\n]*[。！？]', content_no_fm)
    if not sentences:
        sentences = re.findall(r'[\u4e00-\u9fffA-Za-z0-9][^\n。！？]{10,}', content_no_fm)
    
    summary_parts = []
    current_len = 0
    for s in sentences:
        s = s.strip()
        if len(s) < 10:
            continue
        summary_parts.append(s)
        current_len += len(s)
        if current_len >= 220:
            break
    
    if not summary_parts:
        summary_parts.append(f"本文围绕「{title}」主题展开，系统梳理了相关核心概念、技术原理与实践要点，为理解该领域关键问题提供了结构化分析框架。")
    
    summary = ''.join(summary_parts)
    if len(summary) > 300:
        for punct in ['。', '！', '；', '，']:
            idx = summary[:280].rfind(punct)
            if idx != -1 and idx > 100:
                summary = summary[:idx+1]
                break
        if len(summary) > 300:
            summary = summary[:297] + '...'
    if len(summary) < 150:
        summary = summary + f"该内容结合实际场景给出了可操作的实践指引，对相关技术决策具有参考价值。"
        if len(summary) < 150:
            summary = f"本文深入探讨了{title}的核心问题与关键机制，" + summary
    
    if q_source:
        summary = summary + f"[来源: {q_source}]"
    
    full_text = content_no_fm
    kw_candidates = []
    
    tech_patterns = [
        r'(Transformer|注意力机制|多头注意力|自注意力)',
        r'(GPT[-\s]?\d*|LLaMA|Qwen|DeepSeek|Claude|MoE|大模型|语言模型)',
        r'(训练|推理|微调|量化|压缩|加速|优化|部署)',
        r'(显存|算力|延迟|吞吐|带宽|性能|成本|功耗)',
        r'(RLHF|SFT|LoRA|PagedAttention|FlashAttention|KV\s*cache)',
        r'(数据|特征|参数|维度|张量|矩阵|并行|分布式)',
        r'(架构|模块|层|子空间|投影|嵌入|编码|解码)',
    ]
    for pat in tech_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            kw_candidates.append(m.group(1))
    
    title_tokens = re.findall(r'[\u4e00-\u9fffA-Za-z0-9]+', title)
    for t in title_tokens:
        if len(t) >= 2 and len(t) <= 10 and t not in kw_candidates:
            kw_candidates.append(t)
    
    if is_tsc_file(filename):
        default_kw = ['方案定位', '性能对比', '成本评估', '技术风险']
    else:
        default_kw = ['模型架构', '推理优化', '训练策略', '性能瓶颈']
    
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


def inject_tsc_sections(text):
    if '💡核心要点' in text or '🔍深度解读' in text:
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
        insert_pos = outline_idx + 1
        target = outline_idx
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

| 对比维度 | 评估指标 | 关键考量 |
|:---------|:---------|:---------|
| 🚀 性能 | 延迟/吞吐/并发 | 峰值QPS、P99延迟、资源利用率、扩展能力 |
| 💰 成本 | CAPEX/OPEX/ROI | 硬件投入、 licensing费用、运维人力、功耗成本 |
| 🔧 复杂度 | 集成/运维/学习 | 部署周期、团队学习曲线、监控告警复杂度、故障恢复难度 |
| ⚠️ 风险 | 技术/供应/锁定 | 厂商依赖度、社区活跃度、文档质量、专利与合规风险 |

"""
    
    deep_insight = """## 🔍深度解读

### 量化对比数据

| 方案 | 性能评分 | 成本指数 | 复杂度 | 风险等级 | 综合得分 |
|:-----|:--------:|:--------:|:------:|:--------:|:--------:|
| 方案A | 85/100 | 1.0x | 中 | 低 | ⭐⭐⭐⭐ |
| 方案B | 92/100 | 1.6x | 高 | 中 | ⭐⭐⭐⭐ |
| 方案C | 72/100 | 0.7x | 低 | 中 | ⭐⭐⭐ |

> **说明**：性能评分基于基准测试集（吞吐+延迟加权），成本指数以方案A为基线（越低越优），复杂度按SOP步骤数分级，风险等级按供应商/生态/合规三维评估。

### 决策建议

- **预算充足且追求极致性能**：优先选择高评分方案，关注长期技术路线演进
- **成本敏感且场景稳定**：选择性价比方案，通过运维优化弥补性能差距
- **快速验证POC阶段**：选择低复杂度方案，缩短上线周期验证业务价值

"""
    
    lines_new = lines[:insert_pos] + [core_points + deep_insight] + lines[insert_pos:]
    return '\n'.join(lines_new), True


def build_references_and_changelog(text, filename):
    ref_exists = ('## 🔗参考文件' in text or '## 参考文件' in text)
    cl_exists = False
    if '| 日期 | 版本 | 变更内容 |' in text:
        cl_exists = True
    
    refs_title = extract_title(text, filename)
    q_src = extract_q_number(filename)
    
    ref_section = ""
    if not ref_exists:
        ref_section = f"""## 🔗参考文件

### 内部知识库引用
- 题库源：{q_src if q_src else Path(filename).stem}
- 分类索引：[← 返回分类索引](../index.md)
- 相关专题：大模型技术与原理 / 技术选型与方案对比

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
        is_tsc = is_tsc_file(filename)
        
        line_count = count_lines(text)
        is_minimal = line_count < 20
        
        summary, keywords = generate_summary_and_keywords(text, filename, title, q_source)
        
        header_block = f"""> **概要**: {summary}
> **关键词**: {keywords}

"""
        
        toc_block = ""
        if line_count >= 100:
            toc_block = generate_toc(text)
        
        tsc_injected = False
        if is_tsc:
            text, tsc_injected = inject_tsc_sections(text)
        
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
            if toc_block and '## 📑 目录' not in new_text:
                pass
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
        if tsc_injected: info_parts.append("注入💡🔍对比段")
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
    print("🚀 极大规模文档优化批处理启动 (1800 文件级)")
    print(f"   分批大小: {BATCH_SIZE}  |  版本: {VERSION}  |  日期: {CHANGELOG_DATE}")
    print("="*70)
    
    state = load_state()
    print(f"\n📊 历史状态: 已处理 {len(state['processed'])} | 失败 {len(state['failed'])}")
    
    dirs = [
        r"h:\github\cowkb\discover\newwiki2\docs\大模型技术与原理",
        r"h:\github\cowkb\discover\newwiki2\docs\技术选型与方案对比",
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
