#!/usr/bin/env python3
"""
质量优化版 - 最终打磨

修复：
1. 目录中包含非核心项（目录、参考文件、快速导读等）
2. 二级标题中残留的emoji
3. 概要质量提升（从核心要点/市场规模中提取更有信息量的句子）
4. 关键词质量优化
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
        "⚠️"
        "▶️"
        "✅"
        "📊"
        "📋"
        "📖"
        "🔬"
        "💼"
        "🔮"
        "🛠️"
        "🌐"
        "💡"
        "🔗"
        "📝"
        "📅"
        "🏷️"
        "⭐"
        "👥"
        "⏱️"
        "📚"
        "🎯"
        "🚀"
        "💰"
        "📈"
        "📉"
        "🔥"
        "💪"
        "🎨"
        "🧠"
        "🤖"
        "💻"
        "📱"
        "🏆"
        "🎓"
        "🔍"
        "📌"
        "💬"
        "🆕"
        "‼️"
        "❓"
        "➕"
        "➖"
        "➡️"
        "⬅️"
        "⬆️"
        "⬇️"
        "↗️"
        "↘️"
        "↙️"
        "↖️"
        "↕️"
        "↔️"
        "🔄"
        "🔁"
        "🔂"
        "⏩"
        "⏪"
        "⏫"
        "⏬"
        "◀️"
        "▶️"
        "🔼"
        "🔽"
        "⏸️"
        "⏯️"
        "⏹️"
        "⏺️"
        "⏏️"
        "🎦"
        "🔅"
        "🔆"
        "📶"
        "🛜"
        "📡"
        "🔋"
        "🔌"
        "💡"
        "🔦"
        "🕯️"
        "🪔"
        "📻"
        "📺"
        "📷"
        "📹"
        "🎥"
        "📽️"
        "🎞️"
        "📞"
        "☎️"
        "📟"
        "📠"
        "🔋"
        "🪫"
        "🔌"
        "💡"
        "🔦"
        "🕯️"
        "🪔"
        "🧯"
        "🛢️"
        "💸"
        "💵"
        "💴"
        "💶"
        "💷"
        "💰"
        "💳"
        "💎"
        "⚖️"
        "🧰"
        "🔧"
        "🔨"
        "⚒️"
        "🛠️"
        "🪓"
        "⛏️"
        "🔩"
        "⚙️"
        "🔗"
        "🧱"
        "🏗️"
        "🧲"
        "🔑"
        "🗝️"
        "🔐"
        "🔒"
        "🔓"
        "🪪"
        "💼"
        "📁"
        "📂"
        "🗂️"
        "📅"
        "📆"
        "🗒️"
        "🗓️"
        "📇"
        "📈"
        "📉"
        "📊"
        "📋"
        "📌"
        "📍"
        "📎"
        "🖇️"
        "📐"
        "📏"
        "🧮"
        "🔍"
        "🔎"
        "🔬"
        "🔭"
        "📡"
        "💉"
        "🩸"
        "💊"
        "🩹"
        "🩼"
        "🦽"
        "🩺"
        "🏥"
        "🏦"
        "🏨"
        "🏪"
        "🏫"
        "🏛️"
        "⛪"
        "🕌"
        "🛕"
        "🕍"
        "⛩️"
        "🏕️"
        "🏖️"
        "🏝️"
        "🏞️"
        "🏟️"
        "🏙️"
        "🌄"
        "🌅"
        "🌆"
        "🌇"
        "🌉"
        "🏗️"
        "🏭"
        "🏢"
        "🏬"
        "🏣"
        "🏤"
        "🏥"
        "🏦"
        "🏨"
        "🏩"
        "🏪"
        "🏫"
        "🏬"
        "🏭"
        "🏮"
        "🪔"
        "🎪"
        "🎭"
        "🩰"
        "🎨"
        "🎬"
        "📷"
        "📸"
        "📹"
        "🎥"
        "📽️"
        "🎞️"
        "📞"
        "☎️"
        "📟"
        "📠"
        "📱"
        "📲"
        "☎️"
        "📞"
        "📟"
        "📠"
        "📺"
        "📻"
        "🎙️"
        "🎚️"
        "🎛️"
        "🎤"
        "🎧"
        "📻"
        "🎷"
        "🎺"
        "🎸"
        "🪕"
        "🎻"
        "🪘"
        "🥁"
        "🎹"
        "🎹"
        "🎸"
        "🎻"
        "🎺"
        "🎷"
        "🥁"
        "🪘"
        "🎤"
        "🎧"
        "🎼"
        "🎵"
        "🎶"
        "🎹"
        "🥁"
        "🎷"
        "🎺"
        "🎸"
        "🪕"
        "🎻"
        "🪘"
        "🎹"
        "🎹"
        "🎸"
        "🎻"
        "🎺"
        "🎷"
        "🥁"
        "🪘"
        "🎤"
        "🎧"
        "🎼"
        "🎵"
        "🎶"
        "🎹"
        "🥁"
        "🎷"
        "🎺"
        "🎸"
        "🪕"
        "🎻"
        "🪘"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()


def clean_heading(text):
    """清理标题：移除emoji和多余符号"""
    t = remove_emoji(text)
    t = t.lstrip(' -—·•')
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def generate_better_summary(body, title):
    """生成更高质量的概要"""
    
    # 尝试从各个地方提取有价值的句子
    best_sentence = ""
    best_score = -1
    
    # 策略1: 从"背景与意义"/"市场规模"等章节提取段落
    high_value_sections = [
        r'##\s*(?:🌐\s*)?(?:背景与意义|背景介绍|研究背景|项目背景)[^\n]*\n(.+?)(?=\n## |\Z)',
        r'##\s*(?:📊\s*)?(?:市场规模|行业现状|市场格局|产业现状|发展现状)[^\n]*\n(.+?)(?=\n## |\Z)',
        r'##\s*(?:📋\s*)?(?:执行摘要|内容摘要|核心摘要)[^\n]*\n(.+?)(?=\n## |\Z)',
        r'##\s*(?:📖\s*)?(?:概述|简介|前言|引言)[^\n]*\n(.+?)(?=\n## |\Z)',
        r'##\s*(?:🔬\s*)?(?:核心技术解析|技术解析|技术原理)[^\n]*\n(.+?)(?=\n## |\Z)',
    ]
    
    for pattern in high_value_sections:
        match = re.search(pattern, body, re.DOTALL)
        if not match:
            continue
        
        section_text = match.group(1)
        paragraphs = extract_clean_paragraphs(section_text)
        
        for para in paragraphs:
            score = score_summary_sentence(para)
            if score > best_score:
                best_score = score
                best_sentence = para
    
    # 策略2: 从"核心要点"的第一条提取并扩展
    if best_score < 50:
        core_match = re.search(
            r'##\s*(?:📋\s*)?(?:核心要点|快速导读)[^\n]*\n(.+?)(?=\n## |\Z)',
            body, re.DOTALL
        )
        if core_match:
            # 提取第一个要点
            first_bullet = re.search(r'[-*•]\s+\**([^*]+?)\**[：:]\s*(.+?)(?=\n[-*•]|\n###|\n## |\Z)', 
                                     core_match.group(1), re.DOTALL)
            if first_bullet:
                combined = first_bullet.group(1).strip() + '：' + first_bullet.group(2).strip()
                score = score_summary_sentence(combined)
                if score > best_score:
                    best_score = score
                    best_sentence = combined
    
    # 策略3: 找包含数据的句子
    if best_score < 60:
        data_sentences = re.findall(
            r'[^。！？\n]*\d+[%万亿亿元美元][^。！？\n]*[。！？]',
            body
        )
        for sent in data_sentences:
            sent = sent.strip()
            if len(sent) >= 30 and len(sent) <= 100:
                score = score_summary_sentence(sent)
                if score > best_score:
                    best_score = score
                    best_sentence = sent
    
    if not best_sentence:
        best_sentence = f"本文围绕{title}主题展开深入分析，涵盖技术原理、应用实践与行业趋势等核心内容。"
    
    # 格式化为一句话
    summary = format_as_one_sentence(best_sentence)
    return summary


def extract_clean_paragraphs(text):
    """提取干净的段落"""
    paragraphs = []
    current = []
    in_code = False
    
    for line in text.split('\n'):
        s = line.strip()
        
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        
        if not s:
            if current:
                para = ' '.join(current).strip()
                if is_valid_paragraph(para):
                    paragraphs.append(para)
                current = []
            continue
        
        # 跳过列表
        if re.match(r'^[-*•]\s+', s) or re.match(r'^\d+[\.、)]\s+', s):
            if current:
                para = ' '.join(current).strip()
                if is_valid_paragraph(para):
                    paragraphs.append(para)
                current = []
            continue
        
        # 跳过表格
        if s.startswith('|'):
            continue
        
        # 跳过引用元信息
        if re.match(r'^>\s*[📅🏷️🔗📝⭐]', s):
            continue
        
        # 跳过小标题（纯加粗短语）
        if re.match(r'^\*\*[^*]{2,20}\*\*[：:]\s*$', s):
            continue
        
        current.append(s)
    
    if current:
        para = ' '.join(current).strip()
        if is_valid_paragraph(para):
            paragraphs.append(para)
    
    return paragraphs


def is_valid_paragraph(text):
    if not text or len(text) < 25:
        return False
    if text.startswith('原文') and 'http' in text:
        return False
    if text.startswith('>'):
        return False
    return True


def score_summary_sentence(text):
    """给句子打分，越高越适合做概要"""
    score = 0
    
    # 长度分
    if 40 <= len(text) <= 90:
        score += 30
    elif 30 <= len(text) <= 100:
        score += 20
    
    # 包含具体数据加分
    if re.search(r'\d+[%万亿亿元美元]', text):
        score += 30
    
    if re.search(r'\d+年', text):
        score += 10
    
    # 包含核心概念加分
    concepts = ['市场', '产业', '增长', '发展', '趋势', '规模', '技术', '应用',
                '大模型', 'Agent', 'AI', '开源', '算力']
    for c in concepts:
        if c in text:
            score += 5
    
    # 排除项
    if text.startswith('>'):
        score -= 50
    if text.startswith('原文'):
        score -= 50
    if text.startswith('-'):
        score -= 20
    if '详见' in text or '如图' in text or '下表' in text:
        score -= 20
    
    return score


def format_as_one_sentence(text):
    """格式化为完整的一句话，≤100字"""
    if not text:
        return text
    
    # 清理markdown
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 移除开头的标记
    text = re.sub(r'^[>+▶️🔍📊\s-]+', '', text)
    
    # 找到第一个完整句子
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


def fix_toc(body):
    """修复目录：只包含核心二级标题"""
    lines = body.split('\n')
    h2_headings = []
    
    # 明确排除的章节关键词
    exclude_patterns = [
        '目录', '参考文件', '参考资料', '参考来源', '参考文献',
        'Changelog', '变更日志', '变更记录', '版本记录',
        '知识关联', '延伸阅读', '相关文章', '相关素材',
        '快速导读', '核心要点', '内容', '执行摘要', '关键词标签',
        '内容评级', 'import素材融合', '阅读建议', '关键数据',
        '适合人群', '阅读时长', '难度等级',
    ]
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            title = stripped[3:].strip()
            clean = clean_heading(title)
            
            if not clean or len(clean) < 2:
                continue
            
            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.lower() in clean.lower():
                    should_exclude = True
                    break
            
            if not should_exclude:
                h2_headings.append(clean)
    
    # 去重
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


def clean_h2_headings(body):
    """清理所有二级及以下标题的emoji"""
    lines = body.split('\n')
    cleaned = []
    
    for line in lines:
        s = line.strip()
        if s.startswith('#') and not s.startswith('# '):  # 不是H1
            # 计算级别
            level = 0
            idx = 0
            while idx < len(s) and s[idx] == '#':
                level += 1
                idx += 1
            
            if level >= 2:
                title_text = s[idx:].strip()
                clean_title = clean_heading(title_text)
                if clean_title:
                    cleaned.append('#' * level + ' ' + clean_title)
                else:
                    cleaned.append(line)
            else:
                cleaned.append(line)
        else:
            cleaned.append(line)
    
    return '\n'.join(cleaned)


def process_file(filepath):
    """处理单个文件"""
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    
    if not fm:
        print(f"  ⚠️  无frontmatter，跳过: {filename}")
        return False
    
    # 提取标题
    title_match = re.search(r'^title:\s*(.+?)\s*$', fm, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filename.replace('.md', '')
    
    # 1. 清理二级标题的emoji
    body = clean_h2_headings(body)
    
    # 2. 生成更好的概要
    new_summary = generate_better_summary(body, title)
    
    # 3. 修复目录
    new_toc = fix_toc(body)
    
    # 4. 提取现有关键词（保留之前的）
    keywords = "大模型 · AI Agent · AIGC"
    kw_match = re.search(r'> \*\*关键词\*\*:\s*(.+)', body)
    if kw_match:
        keywords = kw_match.group(1).strip()
    
    # 5. 重建文档结构
    # 找到H1位置
    lines = body.split('\n')
    h1_idx = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            h1_idx = i
            break
    
    if h1_idx == -1:
        print(f"  ⚠️  无H1标题: {filename}")
        return False
    
    # 找到正文开始（跳过旧的概要、关键词、目录）
    content_start = h1_idx + 1
    in_toc = False
    for i in range(h1_idx + 1, min(h1_idx + 80, len(lines))):
        stripped = lines[i].strip()
        
        if stripped.startswith('> **概要**:') or stripped.startswith('> **关键词**:'):
            content_start = i + 1
            continue
        
        if stripped == '## 📑 目录' or (stripped.startswith('## ') and '目录' in clean_heading(stripped[3:])):
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
    new_body.append(f"> **概要**: {new_summary}")
    new_body.append(f"> **关键词**: {keywords}")
    new_body.append("")
    
    if new_toc:
        new_body.append(new_toc)
    
    # 添加正文（从content_start开始）
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
    
    print(f"  ✅ {filename[:45]}...")
    print(f"     {new_summary[:70]}...")
    return True


def main():
    if len(sys.argv) < 2:
        print('用法: python3 quality_polish.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 发现 {len(md_files)} 个markdown文件')
    print()
    
    success = 0
    fail = 0
    
    for fp in md_files:
        try:
            if process_file(str(fp)):
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ❌ {Path(fp).name}: {e}")
            import traceback
            traceback.print_exc()
            fail += 1
    
    print()
    print('=' * 60)
    print(f'📊 质量优化完成: {success} 成功, {fail} 失败')
    print('=' * 60)


if __name__ == '__main__':
    main()
