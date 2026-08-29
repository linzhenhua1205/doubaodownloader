#!/usr/bin/env python3
"""
修复脚本：解决换行丢失、目录未生成等问题
对所有161个文件重新整理格式
"""

import re
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime


BOM = '\ufeff'

TEMPLATE_SECTION_MAP = {
    '🌐背景': '背景与技术语境',
    '💡核心要点': '核心技术要点',
    '🔍深度解读': '技术机制深度解析',
    '🆕最新进展': '技术演进与最新突破',
    '快速导读': '内容导航',
    '核心要点': '核心技术要点',
    '深度解读': '技术机制深度解析',
    '最新进展': '技术演进与最新突破',
    '背景与意义': '背景与技术语境',
    '背景与上下文': '背景与技术语境',
    '卡片概述': '主题概述',
}

NOISE_PATTERNS = [
    r'低代码AI开发', r'规模化落地', r'范式跃迁',
    r'Vibe\s*Coding', r'Agentic\s*Engineering',
    r'290\.3\s*亿美元', r'6\s*万亿美元',
    r'范式革命', r'赋能千行百业', r'重新定义',
]


def extract_frontmatter(text):
    has_bom = text.startswith(BOM)
    if has_bom:
        text = text[1:]
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            fm = text[3:end].strip()
            body = text[end + 4:].strip()
            return fm, body, True, has_bom
    return "", text, False, has_bom


def clean_title(title):
    emoji_pattern = re.compile(
        "["
        u"\U0001F300-\U0001FAFF"
        u"\U0001F600-\U0001F64F"
        u"\U0001F680-\U0001F6FF"
        u"\U00002702-\U000027B0"
        u"\u2600-\u2B55"
        u"\ufe0f"
        "]+",
        flags=re.UNICODE
    )
    t = emoji_pattern.sub('', title).strip()
    t = t.replace('**', '').strip()
    t = t.strip(' -—·:：')
    return t.strip()


def fix_line_breaks(body):
    """修复挤在一行的内容，按语义重新加换行"""

    body = re.sub(r'\r\n', '\n', body)
    body = re.sub(r'\r', '\n', body)

    markers_h1 = []
    for m in re.finditer(r'(?<!#)# (?!#)', body):
        markers_h1.append(m.start())
    markers_h2 = []
    for m in re.finditer(r'(?<!#)## (?!#)', body):
        markers_h2.append(m.start())
    markers_h3 = []
    for m in re.finditer(r'(?<!#)### (?!#)', body):
        markers_h3.append(m.start())
    markers_h4 = []
    for m in re.finditer(r'(?<!#)#### ', body):
        markers_h4.append(m.start())

    all_markers = sorted(markers_h1 + markers_h2 + markers_h3 + markers_h4)

    if len(all_markers) >= 3 or (len(all_markers) >= 1 and any('\n' not in body[i:i+200] for i in all_markers[:3])):
        parts = []
        prev = 0
        for pos in all_markers:
            if pos > prev:
                segment = body[prev:pos].rstrip()
                if segment:
                    parts.append(segment)
            prev = pos
        if prev < len(body):
            segment = body[prev:].rstrip()
            if segment:
                parts.append(segment)
        body = '\n\n'.join(parts)

    lines = body.split('\n')
    result_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result_lines.append('')
            continue

        has_code_fence = stripped.startswith('```')

        if not has_code_fence:
            sub_parts = re.split(r'(?=\s###\s)|\s+(?=\|\s*:)|\s+(?=\*\*[^*]{2,30}\*\*\s*[：:])', stripped)
            if len(sub_parts) == 1:
                sub_parts = re.split(r'(?=\s###\s)|\s{3,}(?=\|\s)', stripped)
            if len(sub_parts) > 1:
                for i, sp in enumerate(sub_parts):
                    s = sp.strip()
                    if s:
                        result_lines.append(s)
                    if i < len(sub_parts) - 1:
                        result_lines.append('')
                continue

        if (not has_code_fence and
            not stripped.startswith('|') and
            not stripped.startswith('```') and
            len(stripped) > 200):
            sentence_parts = re.split(r'(?<=[。！？!?；;])\s+', stripped)
            if len(sentence_parts) > 1:
                acc = ""
                for sp in sentence_parts:
                    if len(acc) + len(sp) < 180:
                        acc += (" " if acc else "") + sp
                    else:
                        if acc:
                            result_lines.append(acc.strip())
                        acc = sp
                if acc:
                    result_lines.append(acc.strip())
                continue

        result_lines.append(line)

    body = '\n'.join(result_lines)
    body = re.sub(r'\n{4,}', '\n\n\n', body)
    return body


def extract_summary_and_keywords(body):
    """从现有 blockquote 中提取概要和关键词"""
    summary = None
    keywords = None
    lines_to_remove = set()

    lines = body.split('\n')
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('> **概要**:'):
            summary = s[len('> **概要**:'):].strip()
            lines_to_remove.add(i)
        elif s.startswith('> **关键词**:'):
            keywords = s[len('> **关键词**:'):].strip()
            lines_to_remove.add(i)

    new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
    body_clean = '\n'.join(new_lines)

    return summary, keywords, body_clean


def build_toc_for_body(body, total_file_lines):
    """为 >100 行的文件构建去重目录"""
    if total_file_lines <= 100:
        return ""

    lines = body.split('\n')
    h2_titles = []
    seen = set()

    excludes = [
        '目录', '📑', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录', '更新日志',
        '知识关联', '延伸阅读', '相关文章', '相关资源', '相关素材',
        '快速导读', '内容', '执行摘要', '关键词标签',
        '内容评级', 'import素材融合', '阅读建议', '关键数据',
        '适合人群', '阅读时长', '难度等级', '原始内容', '返回分类索引',
        '主题概述', '卡片定位',
    ]

    for line in lines:
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            title = s[3:].strip()
            clean = clean_title(title)
            if not clean or len(clean) < 2:
                continue
            skip = False
            for ex in excludes:
                if ex.lower() in clean.lower():
                    skip = True
                    break
            if skip:
                continue
            key = clean.lower()
            if key not in seen:
                seen.add(key)
                h2_titles.append(clean)

    if len(h2_titles) < 3:
        return ""

    toc_lines = ["## 📑 目录", ""]
    for t in h2_titles:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', t)
        toc_lines.append(f"- [{t}](#{anchor})")
    toc_lines.append("")
    return '\n'.join(toc_lines)


def clean_section_titles(body):
    """重写模板章节标题"""
    lines = body.split('\n')
    result = []
    for line in lines:
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            title = s[3:].strip()
            clean = clean_title(title)
            new_title = None
            for tmpl, repl in TEMPLATE_SECTION_MAP.items():
                if clean == tmpl or clean.startswith(tmpl) or tmpl in clean:
                    new_title = repl
                    break
            if new_title:
                result.append(f'## {new_title}')
            else:
                result.append(line)
        else:
            result.append(line)
    return '\n'.join(result)


def remove_noise(body):
    """清理噪声词"""
    for pat in NOISE_PATTERNS:
        body = re.sub(pat, '', body, flags=re.IGNORECASE)
    body = re.sub(r'，{2,}', '，', body)
    body = re.sub(r'。{2,}', '。', body)
    return body


def extract_title_from_body(body, fm, filename):
    if fm:
        m = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
        if m:
            return clean_title(m.group(1).strip().strip("'\""))
    m = re.search(r'^#\s+(.+?)\s*$', body, re.MULTILINE)
    if m:
        return clean_title(m.group(1))
    return clean_title(Path(filename).stem)


def extract_footer_and_rebuild(body, fm):
    """切分出正文并重建参考文件+Changelog，同时清除旧目录/返回链接等"""
    lines = body.split('\n')

    h1_idx = -1
    h1_title = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            m = re.match(r'^#\s+(.+?)(\s+\[←|$)', s)
            if m:
                h1_title = clean_title(m.group(1))
            h1_idx = i
            break

    if h1_idx == -1:
        return body, h1_title

    footer_markers = [
        '## 🔗 参考文件', '## 参考文件', '## 参考资料', '## 参考来源',
        '## Changelog', '## 变更日志', '## 变更记录',
        '## 更新日志', '## 版本记录',
    ]

    cut_idx = None
    for i in range(h1_idx + 1, len(lines)):
        s = lines[i].strip()
        for marker in footer_markers:
            if s == marker or s.startswith(marker):
                if cut_idx is None or i < cut_idx:
                    cut_idx = i
                    break

    body_lines = lines[h1_idx + 1: cut_idx] if cut_idx else lines[h1_idx + 1:]

    filtered_body_lines = []
    in_old_toc = False
    for line in body_lines:
        s = line.strip()
        if s.startswith('## ') and '目录' in clean_title(s[3:]):
            in_old_toc = True
            continue
        if in_old_toc:
            if s.startswith('## ') and not s.startswith('### '):
                in_old_toc = False
                filtered_body_lines.append(line)
            elif s.startswith('### '):
                in_old_toc = False
                filtered_body_lines.append(line)
            continue
        if s.startswith('[← '):
            continue
        if s.startswith('> **文档定位**:') or s.startswith('> **知识深度**:') or s.startswith('> **关联知识域**:'):
            continue
        if s == '---' or s == '----':
            continue
        filtered_body_lines.append(line)

    clean_body = '\n'.join(filtered_body_lines).strip()

    refs_section = build_references(body, fm)
    changelog_section = build_changelog()

    complete = (clean_body + '\n\n' + refs_section + '\n' + changelog_section)
    complete = re.sub(r'\n{4,}', '\n\n\n', complete)
    return complete, h1_title


def build_references(body, fm):
    lines = ["## 🔗 参考文件", ""]
    seen_urls = set()
    links = []

    for m in re.finditer(r'\[([^\]]+)\]\((https?://[^)]+)\)', body):
        name = clean_title(m.group(1))
        url = m.group(2).strip()
        if not name or len(name) > 80:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        links.append((name, url))

    src_patterns = [
        r'\[来源[：:]\s*([^\]]+)\]',
        r'>\s*\*\*来源\*\*[：:]\s*([^\n<]+)',
        r'来源[：:]\s*([^\n<]+)',
    ]
    sources = []
    seen_src = set()
    for pat in src_patterns:
        for m in re.finditer(pat, body):
            src = m.group(1).strip()
            src = re.sub(r'[，,。；;].*$', '', src).strip()
            key = re.sub(r'\s+', '', src).lower()
            if len(src) >= 4 and len(src) < 100 and key not in seen_src:
                seen_src.add(key)
                sources.append(src)

    items_out = []
    for name, url in links[:8]:
        items_out.append(f"- [{name}]({url})")
    for s in sources[:5]:
        items_out.append(f"- {s}")

    if not items_out:
        if fm:
            tag_m = re.search(r'^tags:\s*\[(.+?)\]', fm, re.MULTILINE)
            if tag_m:
                items_out.append(f"- 文档标签：{tag_m.group(1)}")
    if not items_out:
        items_out.append("- 原文链接（见文首）")

    for it in items_out:
        lines.append(it)
    lines.append("")
    return '\n'.join(lines)


def build_changelog():
    today = datetime.now().strftime('%Y-%m-%d')
    return f"""## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| {today} | v1.0 | 初始版本 |

"""


def process_single_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    fm, body, has_fm, has_bom = extract_frontmatter(raw_text)
    filename = Path(filepath).name

    body = fix_line_breaks(body)

    summary, keywords, body = extract_summary_and_keywords(body)

    if summary is None or keywords is None:
        return False, "缺少概要/关键词标记，跳过"

    body = clean_section_titles(body)
    body = remove_noise(body)

    body_content, h1_title = extract_footer_and_rebuild(body, fm)

    if h1_title is None:
        h1_title = extract_title_from_body(body, fm, filename)

    total_file_lines = len(raw_text.split('\n'))
    toc = build_toc_for_body(body_content, total_file_lines)

    header = [f"# {h1_title}", ""]
    header.append(f"> **概要**: {summary}")
    header.append(f"> **关键词**: {keywords}")
    header.append("")
    if toc:
        header.append(toc)

    final_body = '\n'.join(header) + body_content
    final_body = re.sub(r'\n{4,}', '\n\n\n', final_body).rstrip() + '\n'

    fm_lines = fm.strip().split('\n') if fm else []
    has_updated = False
    for li, fl in enumerate(fm_lines):
        if re.match(r'^updated_at:', fl.strip()):
            fm_lines[li] = f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'"
            has_updated = True
            break
    if not has_updated and fm:
        fm_lines.append(f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'")
    fm_updated = '\n'.join(fm_lines).strip()

    out = ""
    if has_bom:
        out += BOM
    if fm:
        out += f"---\n{fm_updated}\n---\n\n"
    out += final_body

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(out)

    return True, {
        'filename': filename,
        'title': h1_title,
        'summary_len': len(summary),
        'kw_count': keywords.count('·') + 1,
        'has_toc': bool(toc),
        'lines': total_file_lines,
    }


def process_batch(files, bn, total_bn, results):
    bs = 0
    bk = 0
    br = []
    print(f"\n{'='*60}")
    print(f"🔧 修复批次 {bn}/{total_bn} | 本批 {len(files)} 个文件")
    print(f"{'='*60}\n")
    for idx, fp in enumerate(files, 1):
        fn = Path(fp).name
        try:
            print(f"  [{idx}/{len(files)}] ⚙️  {fn[:50]}...", end=' ', flush=True)
            ok, info = process_single_file(str(fp))
            if ok:
                bs += 1
                mark = "📋" if info['has_toc'] else "  "
                print(f"✅ {mark} | {info['summary_len']}字 | {info['kw_count']}关键词")
                br.append(info)
            else:
                bk += 1
                print(f"⏭️  {info}")
                br.append({'filename': fn, 'skip': True, 'why': info})
        except Exception as e:
            bk += 1
            print(f"❌ {str(e)[:50]}")
            br.append({'filename': fn, 'err': True, 'why': str(e)[:60]})
    results.extend(br)
    print(f"\n  📊 本批：✅ {bs} 成功 | ⏭️ {bk} 跳过")
    return bs, bk


def main():
    base_dir = r'h:\github\cowkb\discover\newwiki2'
    dirs = ['AI-Agent', 'AI-模型架构', 'AI-训练微调', 'ai-models']
    BATCH_SIZE = 20

    print("\n" + "🔧" * 30)
    print("  修复换行丢失 & 目录生成问题")
    print("  目标：161 个已优化文件")
    print("🔧" * 30 + "\n")

    all_files = []
    for d in dirs:
        dp = Path(base_dir) / d
        if not dp.exists():
            continue
        mds = sorted([f for f in dp.glob('*.md') if f.name != 'index.md'])
        print(f"📁 {d}/ : {len(mds)} 文件")
        all_files.extend(mds)

    total = len(all_files)
    tb = (total + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\n📋 总计 {total} 文件 | {tb} 批次\n")

    results = []
    ts = 0
    tk = 0
    bstart = 0
    for bn in range(1, tb + 1):
        bend = min(bstart + BATCH_SIZE, total)
        bf = all_files[bstart:bend]
        s, k = process_batch(bf, bn, tb, results)
        ts += s
        tk += k
        bstart = bend
        time.sleep(0.1)

    gs = sum(1 for r in results if 150 <= r.get('summary_len', 0) <= 300)
    gk = sum(1 for r in results if 4 <= r.get('kw_count', 0) <= 6)
    wt = sum(1 for r in results if r.get('has_toc'))

    print("\n" + "🏁" * 30)
    print("  修复完成")
    print("🏁" * 30)
    print(f"\n📊 统计：")
    print(f"  处理：{total} | ✅ {ts} | ⏭️ {tk} | 成功率 {ts/total*100:.1f}%")
    print(f"\n🔍 质量：")
    print(f"  概要合规（150-300字）：{gs}/{ts} ({gs/max(ts,1)*100:.1f}%)")
    print(f"  关键词合规（4-6个）：   {gk}/{ts} ({gk/max(ts,1)*100:.1f}%)")
    print(f"  长文件已加目录：        {wt} 文件")

    report = {
        'time': datetime.now().isoformat(),
        'total': total, 'ok': ts, 'skip': tk,
        'quality': {'good_summaries': gs, 'good_keywords': gk, 'with_toc': wt},
        'details': results,
    }
    rp = Path(base_dir) / '_fix_report.json'
    with open(rp, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📋 报告：{rp}\n")


if __name__ == '__main__':
    main()
