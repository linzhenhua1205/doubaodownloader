#!/usr/bin/env python3
"""
最终修复版 - 解决残留问题

修复：
1. 所有二级及以下标题的emoji
2. 目录质量（重新生成干净的目录）
3. 二级章节重复
4. 低质量概要和关键词
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[3:end_pos].strip()
            body = text[end_pos+4:].strip()
            return fm, body
    return "", text


def remove_emoji(text):
    """移除emoji - 保守版，只移除常见的"""
    common_emojis = [
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
        '💡', '🔍', '⚙️', '📈', '🛡️',
    ]
    
    result = text
    for emoji in common_emojis:
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
        
        new_lines.append(f"## {sec['display']}")
        
        for i in range(sec['start'] + 1, sec['end'] + 1):
            new_lines.append(lines[i])
    
    last_valid = len(sections) - 1
    while last_valid >= 0 and last_valid in dupe_set:
        last_valid -= 1
    if last_valid >= 0:
        for i in range(sections[last_valid]['end'] + 1, len(lines)):
            new_lines.append(lines[i])
    
    return '\n'.join(new_lines), len(dupe_indices)


def generate_toc(body):
    """生成高质量目录"""
    lines = body.split('\n')
    h2_headings = []
    
    exclude_keywords = [
        '目录', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '延伸阅读', '相关文章', '相关素材',
        '快速导读', '核心要点', '内容', '执行摘要', '关键词标签',
        '内容评级', 'import素材融合', '阅读建议', '关键数据',
        '适合人群', '阅读时长', '难度等级', '快速导航',
        '写在前面', '写在最后', '致谢', '免责声明',
        '作者介绍', '关于作者', '联系我们',
    ]
    
    for line in lines:
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            title = s[3:].strip()
            clean = clean_heading(title)
            
            if not clean or len(clean) < 2:
                continue
            
            should_exclude = False
            for kw in exclude_keywords:
                if kw.lower() in clean.lower():
                    should_exclude = True
                    break
            
            if not should_exclude:
                h2_headings.append(clean)
    
    seen = set()
    unique = []
    for h in h2_headings:
        if h.lower() not in seen:
            seen.add(h.lower())
            unique.append(h)
    
    if len(unique) < 3:
        return ""
    
    toc = ["## 📑 目录", ""]
    for h in unique:
        anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', h)
        toc.append(f"- [{h}](#{anchor})")
    
    toc.append("")
    return '\n'.join(toc)


def improve_weak_summary(body, title, current_summary):
    """优化质量较差的概要"""
    if len(current_summary) >= 40 and '。' in current_summary:
        return current_summary
    
    # 找更好的句子
    # 从"内容"章节找
    content_match = re.search(
        r'##\s*内容[^\n]*\n(.+?)(?=\n## |\Z)',
        body, re.DOTALL
    )
    
    best = current_summary
    best_len = len(current_summary)
    
    if content_match:
        content = content_match.group(1)
        
        # 找加粗的小标题后面的内容
        bold_patterns = re.finditer(
            r'\*\*([^*]{4,20})\*\*[：:]\s*\n?([^\n]+(?:\n[-*•]\s+[^\n]+)*)',
            content
        )
        
        for m in bold_patterns:
            heading = m.group(1)
            detail = m.group(2).strip()
            
            # 合并成一句话
            combined = heading + '：' + re.sub(r'\n[-*•]\s+', '、', detail)
            combined = re.sub(r'\s+', ' ', combined).strip()
            
            if len(combined) > best_len and len(combined) <= 100:
                best = combined
                best_len = len(combined)
    
    # 如果还是太短，用标题生成
    if len(best) < 30:
        title_clean = clean_heading(title)
        parts = re.split(r'[：:—\-｜|]', title_clean)
        if len(parts) >= 2:
            main = parts[0].strip()
            sub = parts[1].strip()
            best = f"本文围绕{main}主题，深入探讨{sub}的核心内容与关键要点。"
        else:
            best = f"本文围绕{title_clean}展开深度分析，涵盖技术原理、应用实践与行业趋势。"
    
    # 格式化
    return format_summary(best)


def format_summary(text):
    """格式化为一句话，≤100字"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^[>+▶️🔍📊\s\-•*]+', '', text)
    
    sentences = re.split(r'([。！？!?；;])', text)
    result = ""
    
    for i in range(0, len(sentences), 2):
        if i >= len(sentences):
            break
        
        sent = sentences[i].strip()
        if not sent:
            continue
        
        punct = sentences[i + 1] if i + 1 < len(sentences) else '。'
        
        if len(result) + len(sent) + len(punct) <= 95:
            result += sent + punct
        else:
            remaining = 95 - len(result)
            if remaining > 10:
                result += sent[:remaining] + '...'
            break
        
        if result.endswith(('。', '！', '？', '!', '?')) and len(result) >= 25:
            break
    
    if not result:
        result = text[:97] + '...'
    
    result = result.strip()
    if not result.endswith(('。', '！', '？', '!', '?', '…', '...')):
        if len(result) < 98:
            result += '。'
        else:
            result = result[:96] + '...'
    
    if len(result) > 100:
        result = result[:97] + '...'
    
    return result


def process_file(filepath):
    """处理单个文件"""
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    
    if not fm:
        print(f"  ⚠️  无frontmatter: {filename}")
        return False
    
    # 提取标题
    title_match = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename.replace('.md', '')
    
    # 1. 清理所有标题的emoji
    body = clean_all_headings(body)
    
    # 2. 去重二级章节
    body, h2_dupes = deduplicate_h2(body)
    
    # 3. 提取现有的概要和关键词
    summary = ""
    keywords = ""
    
    sum_match = re.search(r'> \*\*概要\*\*:\s*(.+)', body)
    if sum_match:
        summary = sum_match.group(1).strip()
    
    kw_match = re.search(r'> \*\*关键词\*\*:\s*(.+)', body)
    if kw_match:
        keywords = kw_match.group(1).strip()
    
    # 4. 优化弱概要
    summary = improve_weak_summary(body, title, summary)
    
    # 5. 生成目录
    toc = generate_toc(body)
    
    # 6. 重建文档
    lines = body.split('\n')
    h1_idx = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            h1_idx = i
            break
    
    if h1_idx == -1:
        return False
    
    # 找到正文开始
    content_start = h1_idx + 1
    in_toc = False
    for i in range(h1_idx + 1, min(h1_idx + 100, len(lines))):
        stripped = lines[i].strip()
        
        if stripped.startswith('> **概要**:') or stripped.startswith('> **关键词**:'):
            content_start = i + 1
            continue
        
        if stripped.startswith('## ') and '目录' in clean_heading(stripped[3:]):
            in_toc = True
            content_start = i + 1
            continue
        
        if in_toc:
            if stripped.startswith('## ') and not stripped.startswith('### '):
                in_toc = False
                content_start = i
                break
            content_start = i + 1
            continue
        
        if stripped and not stripped.startswith('>') and not in_toc:
            content_start = i
            break
    
    # 构建新body
    new_body = [f"# {title}", ""]
    new_body.append(f"> **概要**: {summary}")
    new_body.append(f"> **关键词**: {keywords}")
    new_body.append("")
    
    if toc:
        new_body.append(toc)
    
    for i in range(content_start, len(lines)):
        new_body.append(lines[i])
    
    new_body_text = '\n'.join(new_body)
    
    # 更新frontmatter
    new_fm = re.sub(
        r'^updated_at:\s*[\'"]?\d{4}-\d{2}-\d{2}[\'"]?',
        f"updated_at: '{datetime.now().strftime('%Y-%m-%d')}'",
        fm,
        flags=re.MULTILINE
    )
    
    final_text = f"---\n{new_fm}\n---\n\n{new_body_text}"
    final_text = re.sub(r'\n{4,}', '\n\n\n', final_text)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    return True


def main():
    if len(sys.argv) < 2:
        print('用法: python3 final_fix_all.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 处理 {len(md_files)} 个markdown文件...')
    print()
    
    success = 0
    fail = 0
    
    for fp in md_files:
        try:
            if process_file(str(fp)):
                success += 1
                print(f"  ✅ {Path(fp).name[:45]}...")
            else:
                fail += 1
                print(f"  ❌ {Path(fp).name}")
        except Exception as e:
            fail += 1
            print(f"  ❌ {Path(fp).name}: {e}")
    
    print()
    print('=' * 60)
    print(f'📊 最终修复完成: {success} 成功, {fail} 失败')
    print('=' * 60)


if __name__ == '__main__':
    main()
