#!/usr/bin/env python3
"""
最终收尾修复

1. 清理二级及以下标题中的emoji
2. 合并重复的二级章节
3. 移除底部的标签行（#xxx #yyy 形式的，不是真正的H1）
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime


COMMON_EMOJIS = [
    '📊', '📋', '📖', '📚', '📌', '📎', '📐', '📏', '📝',
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
    '🔍', '⚙️', '📈', '🛡️',
    '⚙', '✏', '📋', '📖', '📚',
    '🌐', '💡', '🔬', '💼', '📊',
    '⚠', '️',
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
    for emoji in COMMON_EMOJIS:
        result = result.replace(emoji, '')
    return result


def clean_heading(text):
    t = remove_emoji(text)
    t = t.lstrip(' -—·•')
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def clean_all_headings(body):
    """清理所有标题中的emoji"""
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


def deduplicate_h2(body):
    """合并重复的二级章节"""
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
                    'end': i - 1
                })
            
            current_title = s[3:].strip()
            current_start = i
    
    if current_title is not None:
        sections.append({
            'clean': clean_heading(current_title).lower(),
            'display': clean_heading(current_title),
            'start': current_start,
            'end': len(lines) - 1
        })
    
    if len(sections) <= 1:
        return body, 0
    
    seen = {}
    dupe_indices = []
    
    for idx, sec in enumerate(sections):
        key = sec['clean']
        if key in seen:
            dupe_indices.append(idx)
        else:
            seen[key] = idx
    
    if not dupe_indices:
        return body, 0
    
    dupe_set = set(dupe_indices)
    new_lines = []
    
    for idx, sec in enumerate(sections):
        if idx in dupe_set:
            continue
        
        if idx == 0:
            for i in range(0, sec['start']):
                new_lines.append(lines[i])
        else:
            prev_idx = idx - 1
            while prev_idx >= 0 and prev_idx in dupe_set:
                prev_idx -= 1
            if prev_idx >= 0:
                for i in range(sections[prev_idx]['end'] + 1, sec['start']):
                    new_lines.append(lines[i])
        
        if sec['display']:
            new_lines.append(f"## {sec['display']}")
        else:
            new_lines.append(lines[sec['start']])
        
        for i in range(sec['start'] + 1, sec['end'] + 1):
            new_lines.append(lines[i])
    
    last_valid = len(sections) - 1
    while last_valid >= 0 and last_valid in dupe_set:
        last_valid -= 1
    if last_valid >= 0:
        for i in range(sections[last_valid]['end'] + 1, len(lines)):
            new_lines.append(lines[i])
    
    return '\n'.join(new_lines), len(dupe_indices)


def remove_tag_lines(body):
    """移除底部的标签行（#xxx #yyy 形式，不是真正的H1）"""
    lines = body.split('\n')
    new_lines = []
    removed = 0
    
    for line in lines:
        stripped = line.strip()
        # 检测标签行：以#开头但包含多个#标签，且不是真正的标题
        if stripped.startswith('# ') and not stripped.startswith('## '):
            # 检查是否包含多个#标签（如 "# AI Agent #机器学习 #大模型"）
            tag_count = len(re.findall(r'#[\w\u4e00-\u9fff]+', stripped))
            if tag_count >= 3:
                removed += 1
                continue
        
        new_lines.append(line)
    
    return '\n'.join(new_lines), removed


def process_file(filepath):
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    
    if not fm:
        return False, 0, 0, 0
    
    # 1. 清理标题emoji
    body = clean_all_headings(body)
    
    # 2. 合并重复H2
    body, h2_dupes = deduplicate_h2(body)
    
    # 3. 移除标签行
    body, tag_lines = remove_tag_lines(body)
    
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
    
    return True, h2_dupes, tag_lines, 0


def main():
    if len(sys.argv) < 2:
        print('用法: python3 final_polish.py <目录路径>')
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
    total_tags = 0
    
    for fp in md_files:
        try:
            ok, h2_dupes, tag_lines, _ = process_file(str(fp))
            if ok:
                success += 1
                total_h2 += h2_dupes
                total_tags += tag_lines
                print(f"  ✅ {Path(fp).name[:45]}... (H2重复:{h2_dupes}, 标签行:{tag_lines})")
            else:
                fail += 1
                print(f"  ❌ {Path(fp).name}")
        except Exception as e:
            fail += 1
            print(f"  ❌ {Path(fp).name}: {e}")
    
    print()
    print('=' * 60)
    print(f'📊 最终收尾完成: {success} 成功, {fail} 失败')
    print(f'   合并H2重复: {total_h2} 个')
    print(f'   移除标签行: {total_tags} 行')
    print('=' * 60)


if __name__ == '__main__':
    main()
