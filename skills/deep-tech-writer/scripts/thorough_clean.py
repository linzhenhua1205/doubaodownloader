#!/usr/bin/env python3
"""
彻底清理版 - 最后一遍

1. 扩充emoji列表，彻底清理
2. 更彻底的H2去重
3. 确保所有重复章节都被合并
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime


MORE_EMOJIS = [
    '📑', '🔗', '📌', '📎', '📋', '📊', '📖', '📚', '📝',
    '🔬', '🔍', '🔎', '🔭',
    '💼', '💻', '📱', '🖥️', '⌨️', '🖱️',
    '🚀', '🔥', '💪', '✨', '⭐', '🌟', '💡',
    '🎯', '🎨', '🎭', '🎪', '🎬', '🎤', '🎧',
    '🧠', '🤖', '👾', '🧬', '🔮',
    '💰', '💸', '💵', '💎', '📈', '📉',
    '🏆', '🥇', '🥈', '🥉',
    '🎓', '✏️',
    '🌐', '🌍', '🌎', '🌏',
    '⚡', '🔔', '🔕', '📢', '📣',
    '🛡️', '🔒', '🔓', '🔑',
    '⚙️', '🔧', '🔨', '🛠️', '🧰',
    '📅', '📆', '⏰', '⏱️', '⏲️',
    '👥', '👤', '🧑', '👨', '👩',
    '❓', '❔', '❗', '❕',
    '➕', '➖', '➗', '✖️',
    '⬆️', '⬇️', '⬅️', '➡️',
    '↗️', '↘️', '↙️', '↖️',
    '🔄', '🔁', '🔂',
    '▶️', '⏸️', '⏹️', '⏺️',
    '🏷️', '🏷',
    '💬', '💭', '🗨️', '🗯️',
    '🎉', '🎊', '🎁', '🎂',
    '☕', '🍵', '🍺', '🍷',
    '📷', '📹', '🎥', '📺', '📻',
    '📞', '☎️', '📟',
    '🔋', '🪫', '🔌',
    '🧪', '🧫',
    '🌱', '🌿', '🍀', '🌸',
    '🚗', '🚙', '✈️', '🚢',
    '🏠', '🏢', '🏥', '🏫', '🏪',
    '⚖️', '🗂️', '📁', '📂',
    '🧩', '🧸', '🎮',
    '🆕', '🆓', '🆒', '🆙',
    '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '⚫', '⚪',
    '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '⬛', '⬜',
    '◻️', '◼️', '🔲', '🔳',
    '✓', '✔️', '✗', '✘', '❌', '✅',
    '⚠️', '⚠',
    '💡', '🔍', '⚙️', '📈', '🛡️',
    '⚙', '✏', '📋', '📖', '📚',
    '🌐', '💡', '🔬', '💼', '📊',
    '⚠', '️',
    '📝', '📌', '📎', '🔗',
    '🧲', '🧱', '🧰', '🧪', '🧫', '🧬',
    '🧠', '🧩', '🧸', '🧺', '🧻', '🧼', '🧽', '🧾', '🧿', '🪀', '🪁',
    '🪂', '🪃', '🪄', '🪅', '🪆', '🪇', '🪈', '🪉', '🪊', '🪋', '🪌',
    '🪍', '🪎', '🪏', '🪐', '🪑', '🪒', '🪓', '🪔', '🪕', '🪖', '🪗',
    '🪘', '🪙', '🪚', '🪛', '🪜', '🪝', '🪞', '🪟', '🪠', '🪡', '🪢',
    '🪣', '🪤', '🪥', '🪦', '🪧', '🪨', '🪩', '🪪', '🪫', '🪬', '🪭',
    '🪮', '🪯', '🪰', '🪱', '🪲', '🪳', '🪴', '🪵', '🪶', '🪷', '🪸',
    '🪹', '🪺', '🪻', '🪼', '🪽', '🪿',
]


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[3:end_pos].strip()
            body = text[end_pos+4:].strip()
            return fm, body
    return "", text


def remove_emoji(text):
    result = text
    for emoji in MORE_EMOJIS:
        result = result.replace(emoji, '')
    return result


def clean_heading(text):
    t = remove_emoji(text)
    t = t.lstrip(' -—·•')
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def clean_all_headings(body):
    lines = body.split('\n')
    cleaned = []
    
    for line in lines:
        s = line.strip()
        if s.startswith('#'):
            level = 0
            idx = 0
            while idx < len(s) and s[idx] == '#':
                level += 1
                idx += 1
            
            title_text = s[idx:].strip()
            clean_title = clean_heading(title_text)
            
            if clean_title:
                cleaned.append('#' * level + ' ' + clean_title)
            else:
                cleaned.append(line)
        else:
            cleaned.append(line)
    
    return '\n'.join(cleaned)


def deduplicate_h2_thorough(body):
    """彻底合并重复H2 - 基于清理后的标题比较"""
    lines = body.split('\n')
    
    sections = []
    current_title = None
    current_start = -1
    
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            if current_title is not None:
                sections.append({
                    'clean': clean_heading(current_title).lower(),
                    'display': clean_heading(current_title),
                    'start': current_start,
                    'end': i - 1,
                    'raw_title': current_title
                })
            
            current_title = s[3:].strip()
            current_start = i
    
    if current_title is not None:
        sections.append({
            'clean': clean_heading(current_title).lower(),
            'display': clean_heading(current_title),
            'start': current_start,
            'end': len(lines) - 1,
            'raw_title': current_title
        })
    
    if len(sections) <= 1:
        return body, 0
    
    # 分组：同clean标题的归为一组
    groups = {}
    for idx, sec in enumerate(sections):
        key = sec['clean']
        if key not in groups:
            groups[key] = []
        groups[key].append(idx)
    
    dupe_count = sum(len(v) - 1 for v in groups.values() if len(v) > 1)
    
    if dupe_count == 0:
        return body, 0
    
    # 构建新内容：保留每组第一个
    new_lines = []
    first_section_idx = sections[0]['start']
    for i in range(0, first_section_idx):
        new_lines.append(lines[i])
    
    # 按原始顺序处理，但跳过重复的
    processed_groups = set()
    
    for idx, sec in enumerate(sections):
        key = sec['clean']
        if key in processed_groups:
            continue
        processed_groups.add(key)
        
        # 标题行
        if sec['display']:
            new_lines.append(f"## {sec['display']}")
        else:
            new_lines.append(lines[sec['start']])
        
        # 内容行
        for i in range(sec['start'] + 1, sec['end'] + 1):
            new_lines.append(lines[i])
    
    # 末尾内容（如果有的话）
    last_end = sections[-1]['end']
    if last_end < len(lines) - 1:
        for i in range(last_end + 1, len(lines)):
            new_lines.append(lines[i])
    
    return '\n'.join(new_lines), dupe_count


def process_file(filepath):
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    
    if not fm:
        return False, 0, 0
    
    # 1. 彻底清理标题emoji
    body = clean_all_headings(body)
    
    # 2. 彻底合并H2重复
    body, h2_dupes = deduplicate_h2_thorough(body)
    
    # 更新frontmatter
    new_fm = re.sub(
        r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
        f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'",
        fm,
        flags=re.MULTILINE
    )
    
    final_text = f"---\n{new_fm}\n---\n\n{body}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    return True, h2_dupes


def count_h2_emoji(body):
    """统计H2中的emoji数量"""
    count = 0
    for line in body.split('\n'):
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            title = s[3:].strip()
            for emoji in MORE_EMOJIS:
                if emoji in title:
                    count += title.count(emoji)
    return count


def main():
    if len(sys.argv) < 2:
        print('用法: python3 thorough_clean.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 处理 {len(md_files)} 个markdown文件')
    print()
    
    success = 0
    fail = 0
    total_h2 = 0
    
    for fp in md_files:
        try:
            ok, h2_dupes = process_file(str(fp))
            if ok:
                success += 1
                total_h2 += h2_dupes
                print(f"  ✅ {Path(fp).name[:50]}... (H2重复:{h2_dupes})")
            else:
                fail += 1
                print(f"  ❌ {Path(fp).name}")
        except Exception as e:
            fail += 1
            print(f"  ❌ {Path(fp).name}: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print('=' * 60)
    print(f'📊 彻底清理完成: {success} 成功, {fail} 失败')
    print(f'   合并H2重复: {total_h2} 个')
    print('=' * 60)


if __name__ == '__main__':
    main()
