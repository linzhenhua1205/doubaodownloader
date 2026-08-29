#!/usr/bin/env python3
"""
最终修复：
1. 修复remove_emoji清空中文标题的BUG - 采用保守的emoji移除方式
2. 去重逻辑改用display名而不是clean值
3. 放宽目录生成条件（unique>=2）
对所有1135个文件重写
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
    (r'低代码AI开发', 'n1'),
    (r'规模化落地', 'n2'),
    (r'范式跃迁', 'n3'),
    (r'Vibe\s*Coding', 'n4'),
    (r'Agentic\s*Engineering', 'n5'),
]
NOISE_PATTERNS_EMO_ONLY = [
    (r'Cursor估值', 'n6'),
    (r'马斯克.*?收购.*?Cursor', 'n7'),
    (r'600亿美元.*?Cursor', 'n8'),
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
    patterns_to_remove = []
    for pattern, tag in NOISE_PATTERNS_GENERAL:
        if re.search(pattern, title, re.IGNORECASE):
            continue
        if re.search(pattern, body, re.IGNORECASE):
            if len(re.findall(pattern, body, re.IGNORECASE)) <= 2:
                patterns_to_remove.append(pattern)
    if is_emo_dir:
        for pattern, tag in NOISE_PATTERNS_EMO_ONLY:
            patterns_to_remove.append(pattern)
    cleaned = body
    removed_count = 0
    for pattern in patterns_to_remove:
        def _replace(m):
            nonlocal removed_count
            removed_count += 1
            return ''
        cleaned = re.sub(pattern, _replace, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip(), removed_count


def safe_remove_emoji(text):
    """保守版emoji移除：只处理明确的emoji字符，不碰中文"""
    if not text:
        return text
    if not any(ord(c) > 0x1F000 for c in text):
        return text.strip()
    safe_chars = []
    for c in text:
        o = ord(c)
        if 0x1F000 <= o <= 0x1FFFF or 0x2600 <= o <= 0x27BF or o in (0x200d, 0xfe0f, 0x23cf, 0x23e9, 0x231a, 0x3030):
            continue
        safe_chars.append(c)
    return ''.join(safe_chars).strip()


def clean_heading_for_compare(heading):
    h = safe_remove_emoji(heading)
    # 去掉序号前缀：阿拉伯数字 或 中文数字，保留主体
    h = re.sub(r'^[\s]*\d+[\.、\s]+', '', h)
    h = re.sub(r'^[\s]*[一二三四五六七八九十百零〇两]+[\.、\s]+', '', h)
    h = re.sub(r'^[\s]*第[一二三四五六七八九十百\d]+[章节部分篇][\.、\s]*', '', h)
    prefix_chars = ' -—·•'
    while h and h[0] in prefix_chars:
        h = h[1:]
    return h.strip().lower()


def get_heading_display_name(heading):
    h = heading.strip()
    h_clean = safe_remove_emoji(h)
    return h_clean if h_clean else h


def extract_core_h2_headings(body):
    lines = body.split('\n')
    headings = []
    non_core = ['参考文件', '参考资料', '参考来源', '参考文献',
                'changelog', '变更日志', '变更记录', '版本记录',
                '知识关联', '相关知识点', '延伸阅读', '更新日志']
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            clean_title = clean_heading_for_compare(title)
            display_title = get_heading_display_name(title)
            is_non_core = False
            ct_lower = clean_title.lower()
            for kw in non_core:
                if kw.lower() in ct_lower:
                    is_non_core = True
                    break
            if not is_non_core and display_title and len(display_title) > 0:
                headings.append({
                    'display': display_title,
                    'clean': clean_title,
                    'raw': title,
                })
    return headings


def generate_toc(body, line_count):
    if line_count <= 100:
        return ""
    headings = extract_core_h2_headings(body)
    if not headings:
        return ""
    # 关键修复：去重用 display（实际显示名）而非clean值
    seen_display = set()
    unique_headings = []
    for h in headings:
        dkey = h['display'].strip().lower()
        if dkey and dkey not in seen_display:
            seen_display.add(dkey)
            unique_headings.append(h)
    if len(unique_headings) < 2:
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
    for text, url in link_pattern.findall(body):
        if url.startswith('http'):
            external_refs.append((text, url))
        elif url.endswith('.md') or 'import/' in url or 'knowledge/' in url or '../' in url:
            internal_refs.append((text, url))
    seen = set()
    u_e, u_i = [], []
    for t, u in external_refs:
        if u not in seen:
            seen.add(u)
            u_e.append((t, u))
    seen.clear()
    for t, u in internal_refs:
        if u not in seen:
            seen.add(u)
            u_i.append((t, u))
    return u_i[:8], u_e[:8]


def build_reference_section(internal_refs, external_refs):
    lines = ["## 🔗 参考文件", "", "### 内部知识库引用"]
    if internal_refs:
        for t, u in internal_refs[:6]:
            dt = t[:60] + "..." if len(t) > 60 else t
            lines.append(f"- [{dt}]({u})")
    else:
        lines.append("- 暂无内部引用")
    lines += ["", "### 外部资料引用"]
    if external_refs:
        for t, u in external_refs[:6]:
            dt = t[:60] + "..." if len(t) > 60 else t
            lines.append(f"- [{dt}]({u})")
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
    patterns = [
        r'^>\s*\*?\*?概要\*?\*?[:：].*?\n',
        r'^>\s*\*?\*?关键词\*?\*?[:：].*?\n',
        r'^##\s*(?:📑\s*)?目录.*?(?=\n## |\Z)',
        r'^##\s*(?:🔗\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)',
        r'^##\s*(?:📝\s*)?参考(?:文件|资料|来源|文献).*?(?=\n## |\Z)',
        r'^##\s*[Cc]hangelog.*?(?=\n## |\Z)',
        r'^##\s*变更(?:日志|记录).*?(?=\n## |\Z)',
        r'^##\s*版本记录.*?(?=\n## |\Z)',
        r'^##\s*更新日志.*?(?=\n## |\Z)',
        r'^##\s*[一二三四五六七八九十百\d]*[、\.]*\s*参考来源.*?(?=\n## |\Z)',
    ]
    cleaned = body
    for pat in patterns:
        cleaned = re.sub(pat, '', cleaned, flags=re.MULTILINE | re.DOTALL)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def strip_all_h1(body):
    lines = body.split('\n')
    return '\n'.join(l for l in lines if not (l.strip().startswith('# ') and not l.strip().startswith('## ')))


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
    m = re.search(r'>\s*\*?\*?概要\*?\*?[:：]\s*(.+?)(?=\n|$)', text)
    if m:
        old_summary = m.group(1).strip()
    m = re.search(r'>\s*\*?\*?关键词\*?\*?[:：]\s*(.+?)(?=\n|$)', text)
    if m:
        old_keywords = m.group(1).strip()
    if not old_summary or not old_keywords:
        return None
    
    body = remove_existing_sections(body)
    body, noise_removed = clean_noise(body, is_emo, title)
    body = strip_all_h1(body)
    line_count = len(body.split('\n'))
    is_minimal = line_count < 20
    toc = generate_toc(body, line_count) if not is_minimal else ""
    
    internal_refs, external_refs = extract_and_clean_references(body)
    ref_section = build_reference_section(internal_refs, external_refs)
    changelog = build_changelog()
    
    source_tag = f"题库 {q_num}" if q_num else "题库"
    if '[来源:' not in old_summary:
        summary_line = f"> **概要**: {old_summary.rstrip('.。')} [来源: {source_tag}]"
    else:
        summary_line = f"> **概要**: {old_summary}"
    keywords_line = f"> **关键词**: {old_keywords}"
    
    new_parts = []
    if fm:
        new_fm = re.sub(
            r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
            "updated_at: '2026-07-29'", fm, flags=re.MULTILINE
        )
        if not re.search(r'^updated_at:', new_fm, re.MULTILINE):
            lfm = new_fm.split('\n')
            lfm.append("updated_at: '2026-07-29'")
            new_fm = '\n'.join(lfm)
        new_parts.append(f"---\n{new_fm}\n---")
    else:
        cat = '企业管理与运营' if is_emo else 'AI编程与开发工具'
        new_parts.append(f"---\ntitle: {title}\ndate: 2026-07-29\ncategory: {cat}\nupdated_at: '2026-07-29'\n---")
    
    new_parts += ["", f"# {title}", "", summary_line, keywords_line, ""]
    if toc:
        new_parts.append(toc)
    new_parts += [body, "", ref_section, changelog]
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
        dp = os.path.join(DOCS_ROOT, subdir)
        for root, dirs, files in os.walk(dp):
            for fn in sorted(files):
                if fn.endswith('.md') and fn not in EXCLUDE_FILES:
                    all_files.append(os.path.join(root, fn))
    
    print(f'📋 待修复文件: {len(all_files)} 个')
    print()
    
    fixed = 0
    toc_added = 0
    errors = 0
    
    for i, fpath in enumerate(all_files):
        old_info = progress['processed'].get(fpath, {})
        try:
            r = repair_file(fpath, progress, old_info)
            if r:
                fixed += 1
                if r['toc']:
                    toc_added += 1
        except Exception as e:
            errors += 1
            print(f"❌ [{i+1}] {os.path.basename(fpath)[:40]}: {e}")
            continue
        if (i + 1) % 100 == 0:
            save_progress(progress)
            print(f"  ... {i+1}/{len(all_files)} | 修复:{fixed} | 目录:{toc_added}")
    
    save_progress(progress)
    print()
    print('='*60)
    print(f'✅ 修复完成')
    print(f'   处理文件: {fixed}/{len(all_files)}')
    print(f'   含目录文件: {toc_added} 个 (>100行)')
    print(f'   错误: {errors} 个')
    print('='*60)


if __name__ == '__main__':
    main()
