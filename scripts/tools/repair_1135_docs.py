#!/usr/bin/env python3
"""
修复两个问题：
1. 重复H1标题（strip_h1保留了内部H1 + new_parts又加了一个H1）
2. >100行文件缺少目录（extract_core_h2_headings排除过严 + remove_existing_sections误删新目录）
对所有1135个文件进行修复重写
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = r'h:\github\cowkb'
PROGRESS_FILE = os.path.join(BASE_DIR, '_optimize_progress.json')
DOCS_ROOT = os.path.join(BASE_DIR, 'discover', 'newwiki2', 'docs')
TARGET_DIRS = ['AI编程与开发工具', '企业管理与运营']
EXCLUDE_FILES = {'index.md', 'progress.md', 'task_plan.md', 'findings.md'}

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


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            return text[3:end_pos].strip(), text[end_pos+4:].strip()
    return "", text


def extract_title(fm, body, fname):
    if fm:
        m = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
        if m:
            t = m.group(1).strip().strip('**').strip()
            return re.sub(r'^[\[\(\<]', '', t)
    m = re.search(r'^#\s+(.+?)\s*$', body, re.MULTILINE)
    if m:
        t = m.group(1).strip().strip('**').strip()
        return re.sub(r'^[\[\(\<]', '', t)
    return Path(fname).stem


def extract_q_number(fname):
    m = re.search(r'(adt|emo)_q(\d+)', fname, re.IGNORECASE)
    if m:
        return f"{m.group(1)}_q{m.group(2)}"
    return None


def clean_noise(body, is_emo_dir, title):
    title_lower = title.lower()
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
    """宽松提取：排除明显尾部章节即可，其他全收录"""
    lines = body.split('\n')
    headings = []
    non_core_keywords = [
        '参考文件', '参考资料', '参考来源', '参考文献',
        'changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '相关知识点', '延伸阅读',
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
                headings.append({'display': display_title, 'clean': clean_title})
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
    if len(unique_headings) < 2:  # 放宽到2个就可以
        return ""
    toc_lines = ["## 📑 目录", ""]
    for h in unique_headings:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', h['display'])
        toc_lines.append(f"- [{h['display']}](#{anchor})")
    toc_lines.append("")
    return '\n'.join(toc_lines)


def extract_and_clean_references(body):
    internal_refs, external_refs = [], []
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    all_links = link_pattern.findall(body)
    for text, url in all_links:
        if url.startswith('http'):
            external_refs.append((text, url))
        elif url.endswith('.md') or 'import/' in url or 'knowledge/' in url or '../' in url:
            internal_refs.append((text, url))
    seen_e = set()
    unique_e = []
    for t, u in external_refs:
        if u not in seen_e:
            seen_e.add(u)
            unique_e.append((t, u))
    seen_i = set()
    unique_i = []
    for t, u in internal_refs:
        if u not in seen_i:
            seen_i.add(u)
            unique_i.append((t, u))
    return unique_i[:8], unique_e[:8]


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
    return """## Changelog

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-07-29 | v1.0 | 首次标准化优化：添加概要关键词、目录、清理噪声、补充参考文件与版本记录 |

"""


def remove_existing_sections(body):
    """移除已有的概要/关键词/目录/参考文件/Changelog段落 + 所有重复H1"""
    patterns = [
        r'^>\s*\*?\*?概要\*?\*?[:：].*?\n',
        r'^>\s*\*?\*?关键词\*?\*?[:：].*?\n',
        r'^>\s*概要[:：].*?\n',
        r'^>\s*关键词[:：].*?\n',
        r'^##\s*(?:📑\s*)?目录.*?(?=\n## |\Z)',
        r'^##\s*(?:🔗\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)',
        r'^##\s*(?:📝\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)',
        r'^##\s*[Cc]hangelog.*?(?=\n## |\Z)',
        r'^##\s*变更(?:日志|记录).*?(?=\n## |\Z)',
        r'^##\s*版本记录.*?(?=\n## |\Z)',
        r'^##\s*更新日志.*?(?=\n## |\Z)',
    ]
    cleaned = body
    for pat in patterns:
        cleaned = re.sub(pat, '', cleaned, flags=re.MULTILINE | re.DOTALL)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def strip_all_h1(body):
    """修复：移除body中所有的H1标题（因为新文件开头会加统一的H1）"""
    lines = body.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            continue
        new_lines.append(line)
    result = '\n'.join(new_lines)
    return result


def repair_file(fpath, progress, old_info):
    is_emo = '企业管理' in fpath
    fname = os.path.basename(fpath)
    
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    title = extract_title(fm, body, fname)
    q_num = extract_q_number(fname)
    
    old_summary = ""
    old_keywords = ""
    summary_m = re.search(r'>\s*\*?\*?概要\*?\*?[:：]\s*(.+?)(?=\n|$)', text)
    if summary_m:
        old_summary = summary_m.group(1).strip()
    kw_m = re.search(r'>\s*\*?\*?关键词\*?\*?[:：]\s*(.+?)(?=\n|$)', text)
    if kw_m:
        old_keywords = kw_m.group(1).strip()
    
    if not old_summary or not old_keywords:
        return None  # 没有概要关键词的跳过（应该不会出现）
    
    body = remove_existing_sections(body)
    body, noise_removed = clean_noise(body, is_emo, title)
    body = strip_all_h1(body)  # 关键修复：去掉body内部所有H1
    line_count = len(body.split('\n'))
    is_minimal = line_count < 20
    toc = generate_toc(body, line_count) if not is_minimal else ""
    
    internal_refs, external_refs = extract_and_clean_references(body)
    ref_section = build_reference_section(internal_refs, external_refs)
    changelog = build_changelog()
    
    source_tag = f"题库 {q_num}" if q_num else "题库"
    
    src_m = re.search(r'\[来源[::]', old_summary)
    if '[来源:' not in old_summary:
        summary_line = f"> **概要**: {old_summary.rstrip('.。')} [来源: {source_tag}]"
    else:
        summary_line = f"> **概要**: {old_summary}"
    keywords_line = f"> **关键词**: {old_keywords}"
    
    new_parts = []
    if fm:
        new_fm = re.sub(
            r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
            "updated_at: '2026-07-29'",
            fm,
            flags=re.MULTILINE
        )
        if not re.search(r'^updated_at:', new_fm, re.MULTILINE):
            lines_fm = new_fm.split('\n')
            lines_fm.append("updated_at: '2026-07-29'")
            new_fm = '\n'.join(lines_fm)
        new_parts.append(f"---\n{new_fm}\n---")
    else:
        new_parts.append(f"---\ntitle: {title}\ndate: 2026-07-29\ncategory: {'企业管理与运营' if is_emo else 'AI编程与开发工具'}\nupdated_at: '2026-07-29'\n---")
    
    new_parts.append("")
    new_parts.append(f"# {title}")  # 唯一的H1在这里
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
        'noise_removed': noise_removed + (old_info.get('noise_removed', 0) if old_info else 0),
        'line_count': line_count,
        'is_minimal': is_minimal,
        'has_toc': bool(toc),
        'keywords': old_keywords,
    }
    return {'toc': bool(toc), 'line_count': line_count}


def main():
    progress = load_progress()
    all_files = []
    for subdir in TARGET_DIRS:
        dir_path = os.path.join(DOCS_ROOT, subdir)
        for root, dirs, files in os.walk(dir_path):
            for fn in sorted(files):
                if fn.endswith('.md') and fn not in EXCLUDE_FILES:
                    all_files.append(os.path.join(root, fn))
    
    print(f'📋 待修复文件: {len(all_files)} 个')
    print()
    
    fixed = 0
    toc_added = 0
    h1_fixed = 0
    errors = 0
    
    for i, fpath in enumerate(all_files):
        old_info = progress['processed'].get(fpath, {})
        try:
            result = repair_file(fpath, progress, old_info)
            if result:
                fixed += 1
                if result['toc']:
                    toc_added += 1
        except Exception as e:
            errors += 1
            print(f"❌ [{i+1}] {os.path.basename(fpath)[:40]}: {e}")
            continue
        
        if (i + 1) % 100 == 0:
            save_progress(progress)
            print(f"  ... 进度: {i+1}/{len(all_files)} | 已修复: {fixed} | 新增目录: {toc_added}")
    
    save_progress(progress)
    
    print()
    print('='*60)
    print(f'✅ 修复完成')
    print(f'   处理文件: {fixed}/{len(all_files)}')
    print(f'   含目录文件: {toc_added} 个 (>100行自动添加)')
    print(f'   错误: {errors} 个')
    print('='*60)


if __name__ == '__main__':
    main()
