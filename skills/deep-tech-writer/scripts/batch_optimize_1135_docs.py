#!/usr/bin/env python3
"""
批量优化 1135 文档主脚本
- 20个一批
- 进度追踪（自动跳过已处理）
- 机械性工作：清理噪声、生成目录、加参考文件+Changelog
- 外部输入：概要+关键词（大模型逐文件生成）
"""

import os
import re
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

BASE_DIR = r'h:\github\cowkb'
PROGRESS_FILE = os.path.join(BASE_DIR, '_optimize_progress.json')
DOCS_ROOT = os.path.join(BASE_DIR, 'discover', 'newwiki2', 'docs')

EXCLUDE_FILES = {'index.md', 'progress.md', 'task_plan.md', 'findings.md'}
TARGET_DIRS = ['AI编程与开发工具', '企业管理与运营']

NOISE_PATTERNS_GENERAL = [
    (r'低代码AI开发', 'noise_lowcode'),
    (r'规模化落地', 'noise_scale'),
    (r'范式跃迁', 'noise_paradigm'),
    (r'Vibe\s*Coding', 'noise_vibe'),
    (r'Agentic\s*Engineering', 'noise_agentic'),
]

NOISE_PATTERNS_EMO_ONLY = [
    (r'Cursor估值', 'noise_cursor_valuation'),
    (r'马斯克.*?收购.*?Cursor', 'noise_cursor_musk'),
    (r'600亿美元.*?Cursor', 'noise_cursor_60b'),
]


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'processed': {}, 'batches': {}, 'stats': {}}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def collect_all_files():
    all_files = []
    for subdir in TARGET_DIRS:
        dir_path = os.path.join(DOCS_ROOT, subdir)
        for root, dirs, files in os.walk(dir_path):
            for fname in sorted(files):
                if fname.endswith('.md') and fname not in EXCLUDE_FILES:
                    fpath = os.path.join(root, fname)
                    all_files.append({
                        'path': fpath,
                        'dir': subdir,
                        'name': fname,
                    })
    return all_files


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[3:end_pos].strip()
            body = text[end_pos+4:].strip()
            return fm, body
    return "", text


def extract_title(fm, body, fname):
    if fm:
        match = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
        if match:
            t = match.group(1).strip()
            t = t.strip('**').strip()
            return t
    h1_match = re.search(r'^#\s+(.+?)\s*$', body, re.MULTILINE)
    if h1_match:
        t = h1_match.group(1).strip()
        t = t.strip('**').strip()
        return t
    return Path(fname).stem


def extract_q_number(fname):
    m = re.search(r'(adt|emo)_q(\d+)', fname, re.IGNORECASE)
    if m:
        return f"{m.group(1)}_q{m.group(2)}"
    return None


def count_lines(body):
    return len(body.split('\n'))


def clean_noise(body, is_emo_dir, title):
    """清理噪声词，保留原文语义（如果直接相关则保留）"""
    title_lower = title.lower()
    body_lower = body.lower()
    
    patterns_to_remove = []
    
    for pattern, tag in NOISE_PATTERNS_GENERAL:
        if re.search(pattern, title, re.IGNORECASE):
            continue
        if re.search(pattern, body, re.IGNORECASE):
            match_count = len(re.findall(pattern, body, re.IGNORECASE))
            if match_count <= 2:
                patterns_to_remove.append((pattern, tag))
    
    if is_emo_dir:
        for pattern, tag in NOISE_PATTERNS_EMO_ONLY:
            patterns_to_remove.append((pattern, tag))
    
    cleaned = body
    removed_count = 0
    for pattern, tag in patterns_to_remove:
        def _replace(m):
            nonlocal removed_count
            removed_count += 1
            return ''
        cleaned = re.sub(pattern, _replace, cleaned, flags=re.IGNORECASE)
    
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip(), removed_count


def remove_emoji(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\ufe0f"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\u3030"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()


def clean_heading_for_compare(heading):
    h = remove_emoji(heading)
    h = re.sub(r'^[\s]*\d+[\.、\s]+', '', h)
    h = h.lstrip(' -—·•📋📊🔬💼⚠️🔮🛠️🔗📚📖📎💡🆕🌐📝⚙️🔍📈')
    return h.strip().lower()


def get_heading_display_name(heading):
    h = heading.strip()
    h_clean = remove_emoji(h)
    if h_clean:
        return h_clean
    return h


def extract_core_h2_headings(body):
    lines = body.split('\n')
    headings = []
    
    non_core_keywords = [
        '目录', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '相关知识点', '延伸阅读', '相关文章',
        '相关素材', '关键词标签', '内容评级', 'import素材融合',
        '快速导读', '核心要点', '内容', '执行摘要', '概要', '关键词',
    ]
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            clean_title = clean_heading_for_compare(title)
            display_title = get_heading_display_name(title)
            
            is_non_core = False
            for kw in non_core_keywords:
                if kw.lower() in clean_title:
                    is_non_core = True
                    break
            
            if not is_non_core and display_title and len(display_title) > 1:
                headings.append({
                    'display': display_title,
                    'clean': clean_title
                })
    
    return headings


def generate_toc(body, line_count):
    if line_count <= 100:
        return ""
    
    headings = extract_core_h2_headings(body)
    if not headings:
        return ""
    
    seen = set()
    unique_headings = []
    for h in headings:
        if h['clean'] not in seen and h['display']:
            seen.add(h['clean'])
            unique_headings.append(h)
    
    if len(unique_headings) < 3:
        return ""
    
    toc_lines = ["## 📑 目录", ""]
    for h in unique_headings:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', h['display'])
        toc_lines.append(f"- [{h['display']}](#{anchor})")
    
    toc_lines.append("")
    return '\n'.join(toc_lines)


def extract_and_clean_references(body):
    internal_refs = []
    external_refs = []
    
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    all_links = link_pattern.findall(body)
    
    for text, url in all_links:
        if url.startswith('http'):
            external_refs.append((text, url))
        elif url.endswith('.md') or 'import/' in url or 'knowledge/' in url or '../' in url:
            internal_refs.append((text, url))
    
    seen_external = set()
    unique_external = []
    for text, url in external_refs:
        if url not in seen_external:
            seen_external.add(url)
            unique_external.append((text, url))
    
    seen_internal = set()
    unique_internal = []
    for text, url in internal_refs:
        if url not in seen_internal:
            seen_internal.add(url)
            unique_internal.append((text, url))
    
    return unique_internal[:8], unique_external[:8]


def build_reference_section(internal_refs, external_refs):
    lines = ["## 🔗 参考文件", ""]
    
    lines.append("### 内部知识库引用")
    if internal_refs:
        for text, url in internal_refs[:6]:
            display_text = text[:60] + "..." if len(text) > 60 else text
            lines.append(f"- [{display_text}]({url})")
    else:
        lines.append("- 暂无内部引用")
    
    lines.append("")
    lines.append("### 外部资料引用")
    if external_refs:
        for text, url in external_refs[:6]:
            display_text = text[:60] + "..." if len(text) > 60 else text
            lines.append(f"- [{display_text}]({url})")
    else:
        lines.append("- 暂无外部引用")
    
    lines.append("")
    return '\n'.join(lines)


def build_changelog():
    date_str = "2026-07-29"
    changelog = f"""## Changelog

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| {date_str} | v1.0 | 首次标准化优化：添加概要关键词、目录、清理噪声、补充参考文件与版本记录 |

"""
    return changelog


def remove_existing_sections(body):
    """移除已有的概要/关键词/目录/参考文件/Changelog段落"""
    patterns = [
        r'^>\s*\*\*概要\*\*[:：].*?\n',
        r'^>\s*\*\*关键词\*\*[:：].*?\n',
        r'^>\s*概要[:：].*?\n',
        r'^>\s*关键词[:：].*?\n',
        r'^##\s*(?:📑\s*)?目录.*?(?=\n## |\Z)',
        r'^##\s*(?:🔗\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)',
        r'^##\s*(?:📝\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)',
        r'^##\s*[Cc]hangelog.*?(?=\n## |\Z)',
        r'^##\s*变更(?:日志|记录).*?(?=\n## |\Z)',
        r'^##\s*版本记录.*?(?=\n## |\Z)',
    ]
    
    cleaned = body
    for pat in patterns:
        cleaned = re.sub(pat, '', cleaned, flags=re.MULTILINE | re.DOTALL)
    
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def strip_h1(body, canonical_title):
    """移除重复的H1，保留规范的一个"""
    lines = body.split('\n')
    new_lines = []
    found_h1 = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            if not found_h1:
                new_lines.append(f"# {canonical_title}")
                found_h1 = True
            continue
        new_lines.append(line)
    
    result = '\n'.join(new_lines)
    if not found_h1:
        result = f"# {canonical_title}\n\n{result}"
    return result


def get_body_preview(body, max_chars=800):
    """获取正文预览供大模型分析"""
    lines = body.split('\n')
    preview_lines = []
    current_chars = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        preview_lines.append(line)
        current_chars += len(line)
        if current_chars >= max_chars:
            break
    
    preview = '\n'.join(preview_lines)
    if len(preview) > max_chars:
        preview = preview[:max_chars] + "..."
    return preview


def prepare_batch_info(batch_num, files_in_batch, progress):
    """准备批次信息，包含每个文件的分析上下文"""
    info = []
    for idx, f in enumerate(files_in_batch):
        fpath = f['path']
        
        with open(fpath, 'r', encoding='utf-8') as fh:
            text = fh.read()
        
        fm, body = extract_frontmatter(text)
        title = extract_title(fm, body, f['name'])
        q_num = extract_q_number(f['name'])
        line_count = count_lines(body)
        preview = get_body_preview(body)
        
        info.append({
            'batch_index': idx,
            'path': fpath,
            'dir': f['dir'],
            'name': f['name'],
            'title': title,
            'q_number': q_num,
            'line_count': line_count,
            'is_minimal': line_count < 20,
            'needs_toc': line_count > 100,
            'preview': preview,
            'source_tag': f"题库 {q_num}" if q_num else "题库",
        })
    
    return info


def apply_optimization(file_info, summary_text, keywords_text, progress):
    """对单个文件应用优化（写入磁盘）"""
    fpath = file_info['path']
    is_emo = file_info['dir'] == '企业管理与运营'
    is_minimal = file_info['is_minimal']
    
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    title = extract_title(fm, body, file_info['name'])
    
    body = remove_existing_sections(body)
    body, noise_removed = clean_noise(body, is_emo, title)
    body = strip_h1(body, title)
    line_count = count_lines(body)
    
    toc = generate_toc(body, line_count) if not is_minimal else ""
    
    internal_refs, external_refs = extract_and_clean_references(body)
    ref_section = build_reference_section(internal_refs, external_refs)
    changelog = build_changelog()
    
    source_tag = file_info.get('source_tag', '题库')
    summary_line = f"> **概要**: {summary_text} [来源: {source_tag}]"
    keywords_line = f"> **关键词**: {keywords_text}"
    
    new_parts = []
    if fm:
        new_fm = re.sub(
            r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
            f"updated_at: '2026-07-29'",
            fm,
            flags=re.MULTILINE
        )
        if not re.search(r'^updated_at:', new_fm, re.MULTILINE):
            lines_fm = new_fm.split('\n')
            lines_fm.append(f"updated_at: '2026-07-29'")
            new_fm = '\n'.join(lines_fm)
        new_parts.append(f"---\n{new_fm}\n---")
    else:
        new_parts.append(f"---\ntitle: {title}\ndate: 2026-07-29\ncategory: {file_info['dir']}\nupdated_at: '2026-07-29'\n---")
    
    new_parts.append("")
    new_parts.append(f"# {title}")
    new_parts.append("")
    new_parts.append(summary_line)
    new_parts.append(keywords_line)
    new_parts.append("")
    
    if toc:
        new_parts.append(toc)
    
    new_parts.append(body)
    new_parts.append("")
    new_parts.append(ref_section)
    new_parts.append(changelog)
    
    final_text = '\n'.join(new_parts)
    final_text = re.sub(r'\n{4,}', '\n\n\n', final_text)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    progress['processed'][fpath] = {
        'timestamp': datetime.now().isoformat(),
        'noise_removed': noise_removed,
        'line_count': line_count,
        'is_minimal': is_minimal,
        'has_toc': bool(toc),
        'keywords': keywords_text,
    }
    save_progress(progress)
    
    return noise_removed, line_count, bool(toc)


def main():
    progress = load_progress()
    
    all_files = collect_all_files()
    print(f"📋 收集到 {len(all_files)} 个文件")
    
    unprocessed = [f for f in all_files if f['path'] not in progress['processed']]
    print(f"⏭️  跳过已处理: {len(all_files) - len(unprocessed)} 个")
    print(f"📌 待处理: {len(unprocessed)} 个")
    
    if not unprocessed:
        print("✅ 所有文件已处理完成！")
        return
    
    BATCH_SIZE = 20
    total_batches = (len(unprocessed) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"📦 分 {total_batches} 批，每批 {BATCH_SIZE} 个")
    print()
    
    current_batch_idx = progress.get('stats', {}).get('current_batch', 0)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'prepare':
        batch_num = current_batch_idx
        if len(sys.argv) > 2:
            batch_num = int(sys.argv[2])
        
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(unprocessed))
        batch_files = unprocessed[start:end]
        
        print(f"=" * 80)
        print(f"📦 第 {batch_num + 1} / {total_batches} 批（文件 {start+1} - {end}）")
        print(f"=" * 80)
        print()
        
        batch_info = prepare_batch_info(batch_num, batch_files, progress)
        for item in batch_info:
            mark_min = " [极简]" if item['is_minimal'] else ""
            mark_toc = " [需目录]" if item['needs_toc'] else ""
            print(f"  [{item['batch_index']:2d}] {item['name']}")
            print(f"       标题: {item['title'][:80]}")
            print(f"       Q编号: {item['q_number']} | 行数: {item['line_count']}{mark_min}{mark_toc}")
            preview_short = item['preview'][:200].replace('\n', ' ⏎ ')
            print(f"       预览: {preview_short}")
            print()
        
        out_file = os.path.join(BASE_DIR, f'_batch_{batch_num + 1}_info.json')
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(batch_info, f, ensure_ascii=False, indent=2)
        print(f"💾 批次信息已保存到: {out_file}")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == 'apply':
        if len(sys.argv) < 4:
            print("用法: python batch_optimize_1135_docs.py apply <批次号> <结果JSON>")
            return
        
        batch_num = int(sys.argv[2])
        result_file = sys.argv[3]
        
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(unprocessed))
        batch_files = unprocessed[start:end]
        
        with open(result_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        success = 0
        fail = 0
        total_noise = 0
        
        for i, f_info in enumerate(batch_files):
            path_key = f_info['path']
            if str(i) not in results and str(i) not in {str(k) for k in results.keys()}:
                if f_info['name'] in results:
                    res = results[f_info['name']]
                else:
                    print(f"  ⚠️  找不到结果: {f_info['name']}")
                    fail += 1
                    continue
            else:
                res = results.get(str(i), {})
            
            summary = res.get('summary', '').strip()
            keywords = res.get('keywords', '').strip()
            
            if not summary or not keywords:
                print(f"  ⚠️  缺少概要/关键词: {f_info['name']}")
                fail += 1
                continue
            
            try:
                batch_item_info = {
                    'path': f_info['path'],
                    'dir': f_info['dir'],
                    'name': f_info['name'],
                    'is_minimal': count_lines(extract_frontmatter(open(f_info['path'], 'r', encoding='utf-8').read())[1]) < 20,
                }
                with open(f_info['path'], 'r', encoding='utf-8') as tf:
                    ttxt = tf.read()
                tfm, tbody = extract_frontmatter(ttxt)
                ttitle = extract_title(tfm, tbody, f_info['name'])
                qnum = extract_q_number(f_info['name'])
                batch_item_info['title'] = ttitle
                batch_item_info['source_tag'] = f"题库 {qnum}" if qnum else "题库"
                
                noise, lc, has_toc = apply_optimization(batch_item_info, summary, keywords, progress)
                total_noise += noise
                success += 1
                toc_mark = "📑" if has_toc else "  "
                noise_mark = f"🗑️{noise}" if noise > 0 else "    "
                print(f"  ✅ [{i:2d}] {toc_mark} {noise_mark} {f_info['name'][:50]}")
            except Exception as e:
                fail += 1
                print(f"  ❌ [{i:2d}] {f_info['name']}: {e}")
                import traceback
                traceback.print_exc()
        
        progress.setdefault('stats', {})['current_batch'] = batch_num + 1
        save_progress(progress)
        
        print()
        print(f"📊 第{batch_num+1}批完成: ✅ {success}  ❌ {fail}  🗑️ 清理噪声{total_noise}处")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        total_processed = len(progress['processed'])
        print(f"📊 处理进度: {total_processed} / {len(all_files)} ({100*total_processed/len(all_files):.1f}%)")
        print(f"⏳ 剩余: {len(all_files) - total_processed} 个文件")
        return
    
    print("用法:")
    print("  python batch_optimize_1135_docs.py prepare [批次号]   # 准备批次信息（默认下一批）")
    print("  python batch_optimize_1135_docs.py apply <批次号> <结果JSON>  # 应用优化结果")
    print("  python batch_optimize_1135_docs.py status            # 查看状态")


if __name__ == '__main__':
    main()
