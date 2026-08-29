#!/usr/bin/env python3
"""
质量检查与统计报告

检查每个文件的：
1. H1标题重复情况
2. 概要质量（是否是一句话、长度、是否包含数据）
3. 关键词质量（数量、是否有意义）
4. 目录质量（是否只含核心二级标题）
5. 二级标题emoji清理情况
6. 重复章节情况
"""

import re
import os
import sys
import json
from pathlib import Path


def extract_frontmatter(text):
    if text.startswith('---'):
        end_pos = text.find('\n---', 3)
        if end_pos != -1:
            fm = text[3:end_pos].strip()
            body = text[end_pos+4:].strip()
            return fm, body
    return "", text


def check_file(filepath):
    """检查单个文件的质量"""
    filename = Path(filepath).name
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    fm, body = extract_frontmatter(text)
    
    result = {
        'file': filename,
        'h1_count': 0,
        'has_duplicate_h1': False,
        'summary': '',
        'summary_quality': 0,  # 0-100
        'summary_reason': '',
        'keywords': '',
        'keyword_count': 0,
        'keyword_quality': 0,  # 0-100
        'keyword_reason': '',
        'toc_entries': 0,
        'toc_quality': 0,  # 0-100
        'h2_with_emoji': 0,
        'h2_total': 0,
        'duplicate_h2': 0,
        'overall_quality': 0,  # 0-100
    }
    
    # 1. 检查H1
    h1s = []
    for line in body.split('\n'):
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            h1s.append(s[2:].strip())
    
    result['h1_count'] = len(h1s)
    result['has_duplicate_h1'] = len(h1s) > 1
    
    # 2. 检查概要
    sum_match = re.search(r'> \*\*概要\*\*:\s*(.+)', body)
    if sum_match:
        summary = sum_match.group(1).strip()
        result['summary'] = summary
        
        # 评分
        score = 0
        reasons = []
        
        # 长度检查
        if 30 <= len(summary) <= 100:
            score += 30
        elif len(summary) < 30:
            reasons.append('太短')
        else:
            reasons.append('太长')
        
        # 是否是完整句子
        if summary.endswith(('。', '！', '？', '!', '?', '…', '...')):
            score += 20
        else:
            reasons.append('非完整句子')
        
        # 是否包含数据
        if re.search(r'\d+[%万亿亿元美元万]', summary):
            score += 25
        else:
            pass  # 不扣分，只是没有加分
        
        # 是否是模板化内容
        template_phrases = [
            '规模化落地：2026年AI从技术验证转向生产级应用',
            '大语言模型技术正经历从技术验证向规模化落地',
        ]
        is_template = False
        for tp in template_phrases:
            if tp in summary:
                is_template = True
                break
        if not is_template:
            score += 25
        else:
            reasons.append('模板化')
        
        result['summary_quality'] = min(score, 100)
        result['summary_reason'] = '、'.join(reasons) if reasons else '良好'
    
    # 3. 检查关键词
    kw_match = re.search(r'> \*\*关键词\*\*:\s*(.+)', body)
    if kw_match:
        kw_text = kw_match.group(1).strip()
        result['keywords'] = kw_text
        
        keywords = [k.strip() for k in kw_text.split('·') if k.strip()]
        result['keyword_count'] = len(keywords)
        
        score = 0
        reasons = []
        
        # 数量检查
        if 3 <= len(keywords) <= 5:
            score += 30
        elif len(keywords) < 3:
            reasons.append(f'数量不足({len(keywords)})')
        else:
            reasons.append(f'数量过多({len(keywords)})')
        
        # 质量检查
        bad_keywords = [
            '下跌', '支持', '价格', '亿美元', '万次', '个月', '场景', '自动化',
            '生成', '核心定位', '与可视化', '监控', '次浏览', '下载量', '数据亮点',
            '完全免费', '调试', '助手', '对话', '亿元', '集群', '资本支出',
            '基础设施', '未来十年',
        ]
        
        good_count = 0
        for kw in keywords:
            kw_clean = kw.strip()
            is_bad = False
            for bk in bad_keywords:
                if bk in kw_clean:
                    is_bad = True
                    break
            if not is_bad and len(kw_clean) >= 2:
                good_count += 1
        
        if good_count == len(keywords):
            score += 50
        else:
            score += int(50 * good_count / max(len(keywords), 1))
            reasons.append(f'{len(keywords)-good_count}个质量低')
        
        # 用 · 分隔
        if '·' in kw_text:
            score += 20
        else:
            reasons.append('分隔符错误')
        
        result['keyword_quality'] = min(score, 100)
        result['keyword_reason'] = '、'.join(reasons) if reasons else '良好'
    
    # 4. 检查目录
    toc_match = re.search(r'##\s*(?:📑\s*)?目录[^\n]*\n(.+?)(?=\n## |\Z)', body, re.DOTALL)
    if toc_match:
        toc_text = toc_match.group(1)
        entries = re.findall(r'-\s*\[([^\]]+)\]', toc_text)
        result['toc_entries'] = len(entries)
        
        score = 0
        # 数量合适
        if 3 <= len(entries) <= 10:
            score += 40
        
        # 不包含非核心项
        non_core = ['目录', '参考文件', '快速导读', '核心要点', 'Changelog', '参考资料']
        has_non_core = False
        for e in entries:
            for nc in non_core:
                if nc in e:
                    has_non_core = True
                    break
            if has_non_core:
                break
        
        if not has_non_core:
            score += 60
        
        result['toc_quality'] = min(score, 100)
    
    # 5. 检查二级标题emoji
    h2_headings = []
    for line in body.split('\n'):
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            h2_headings.append(s[3:].strip())
    
    result['h2_total'] = len(h2_headings)
    
    emoji_count = 0
    emoji_pattern = re.compile(
        "[" u"\U0001F300-\U0001FAFF" u"\U00002700-\U000027BF" u"\u2600-\u2B55" u"\ufe0f" "]+",
        flags=re.UNICODE
    )
    
    for h in h2_headings:
        if emoji_pattern.search(h):
            emoji_count += 1
    
    result['h2_with_emoji'] = emoji_count
    
    # 6. 检查重复H2
    seen = set()
    dupes = 0
    for h in h2_headings:
        # 清理后比较
        h_clean = emoji_pattern.sub('', h).strip().lower()
        h_clean = re.sub(r'^\s*\d+[\.、]\s*', '', h_clean)
        h_clean = h_clean.strip()
        if h_clean in seen:
            dupes += 1
        else:
            seen.add(h_clean)
    
    result['duplicate_h2'] = dupes
    
    # 7. 综合评分
    overall = 0
    overall += result['summary_quality'] * 0.30
    overall += result['keyword_quality'] * 0.25
    overall += result['toc_quality'] * 0.15
    
    # H1
    if not result['has_duplicate_h1']:
        overall += 10
    else:
        overall += 0
    
    # H2 emoji
    if result['h2_with_emoji'] == 0:
        overall += 10
    else:
        overall += max(0, 10 - result['h2_with_emoji'] * 2)
    
    # H2重复
    if result['duplicate_h2'] == 0:
        overall += 10
    else:
        overall += max(0, 10 - result['duplicate_h2'])
    
    result['overall_quality'] = round(overall, 1)
    
    return result


def main():
    if len(sys.argv) < 2:
        print('用法: python3 quality_check.py <目录路径>')
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f'❌ 路径不存在: {target_dir}')
        sys.exit(1)
    
    md_files = sorted([f for f in Path(target_dir).glob('*.md') if f.name != 'index.md'])
    
    print(f'🔍 检查 {len(md_files)} 个markdown文件...')
    print()
    
    results = []
    
    for fp in md_files:
        r = check_file(str(fp))
        results.append(r)
    
    # 统计
    total = len(results)
    
    # H1重复
    h1_dupes = sum(1 for r in results if r['has_duplicate_h1'])
    
    # 概要质量分布
    good_summary = sum(1 for r in results if r['summary_quality'] >= 70)
    mid_summary = sum(1 for r in results if 50 <= r['summary_quality'] < 70)
    bad_summary = sum(1 for r in results if r['summary_quality'] < 50)
    
    # 关键词质量分布
    good_kw = sum(1 for r in results if r['keyword_quality'] >= 70)
    mid_kw = sum(1 for r in results if 50 <= r['keyword_quality'] < 70)
    bad_kw = sum(1 for r in results if r['keyword_quality'] < 50)
    
    # 目录质量
    good_toc = sum(1 for r in results if r['toc_quality'] >= 70)
    
    # 标题emoji
    files_with_emoji = sum(1 for r in results if r['h2_with_emoji'] > 0)
    total_emoji = sum(r['h2_with_emoji'] for r in results)
    
    # H2重复
    files_with_h2_dupe = sum(1 for r in results if r['duplicate_h2'] > 0)
    total_h2_dupe = sum(r['duplicate_h2'] for r in results)
    
    # 综合质量
    avg_quality = sum(r['overall_quality'] for r in results) / max(total, 1)
    excellent = sum(1 for r in results if r['overall_quality'] >= 85)
    good = sum(1 for r in results if 70 <= r['overall_quality'] < 85)
    fair = sum(1 for r in results if 50 <= r['overall_quality'] < 70)
    poor = sum(1 for r in results if r['overall_quality'] < 50)
    
    print('=' * 70)
    print('📊 深度重构质量检查报告')
    print('=' * 70)
    print()
    print(f'  检查文件总数: {total} 个')
    print()
    
    print('  【H1标题重复】')
    print(f'    有重复H1的文件: {h1_dupes} 个')
    print()
    
    print('  【概要质量】')
    print(f'    优秀(≥70分): {good_summary} 个 ({good_summary/total*100:.1f}%)')
    print(f'    中等(50-69): {mid_summary} 个 ({mid_summary/total*100:.1f}%)')
    print(f'    待优化(<50): {bad_summary} 个 ({bad_summary/total*100:.1f}%)')
    print()
    
    print('  【关键词质量】')
    print(f'    优秀(≥70分): {good_kw} 个 ({good_kw/total*100:.1f}%)')
    print(f'    中等(50-69): {mid_kw} 个 ({mid_kw/total*100:.1f}%)')
    print(f'    待优化(<50): {bad_kw} 个 ({bad_kw/total*100:.1f}%)')
    print()
    
    print('  【目录质量】')
    print(f'    合格(≥70分): {good_toc} 个 ({good_toc/total*100:.1f}%)')
    print()
    
    print('  【二级标题Emoji】')
    print(f'    有残留emoji的文件: {files_with_emoji} 个')
    print(f'    残留emoji总数: {total_emoji} 个')
    print()
    
    print('  【二级章节重复】')
    print(f'    有重复章节的文件: {files_with_h2_dupe} 个')
    print(f'    重复章节总数: {total_h2_dupe} 个')
    print()
    
    print('  【综合质量评分】')
    print(f'    平均分数: {avg_quality:.1f} / 100')
    print(f'    优秀(≥85): {excellent} 个 ({excellent/total*100:.1f}%)')
    print(f'    良好(70-84): {good} 个 ({good/total*100:.1f}%)')
    print(f'    一般(50-69): {fair} 个 ({fair/total*100:.1f}%)')
    print(f'    较差(<50): {poor} 个 ({poor/total*100:.1f}%)')
    print()
    
    # 列出质量较差的文件
    print('  【质量待优化文件】')
    poor_files = [r for r in results if r['overall_quality'] < 70]
    poor_files.sort(key=lambda x: x['overall_quality'])
    if poor_files:
        for r in poor_files[:10]:
            issues = []
            if r['summary_quality'] < 70:
                issues.append(f'概要({r["summary_reason"]})')
            if r['keyword_quality'] < 70:
                issues.append(f'关键词({r["keyword_reason"]})')
            if r['h2_with_emoji'] > 0:
                issues.append(f'H2 emoji({r["h2_with_emoji"]})')
            if r['duplicate_h2'] > 0:
                issues.append(f'H2重复({r["duplicate_h2"]})')
            print(f'    - {r["file"][:40]}: {r["overall_quality"]}分 | {"、".join(issues)}')
    else:
        print('    全部达到良好以上！🎉')
    
    print()
    print('=' * 70)
    
    # 保存详细报告
    report_path = os.path.join(target_dir, '_quality_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'📝 详细报告: {report_path}')


if __name__ == '__main__':
    main()
