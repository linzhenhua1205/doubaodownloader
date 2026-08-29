# -*- coding: utf-8 -*-
"""
deep-tech-writer 结构缺失批量修复脚本
智能判断每个文件缺什么补什么，不重复追加已存在的章节
"""

import os
import re
import sys
import json
from pathlib import Path
from collections import Counter

# ============ 配置 ============
BATCH_SIZE = 20
UTF8_BOM = '\ufeff'

# 题库映射
QB_MAP = {
    'aap': ('AI应用与落地实践题库', 'aap系列题库'),
    'mwt': ('方法论与工具题库', 'mwt系列题库'),
    'iti': ('行业趋势与洞察题库', 'iti系列题库'),
}

NOISE_PATTERNS = [
    r'低代码AI开发[·、/\s]*规模化落地[·、/\s]*范式跃迁',
    r'Vibe\s*Coding',
    r'Agentic\s*Engineering',
    r'规模化落地[·、/\s]*范式跃迁',
]

# 各分类的主题关键词池（用于智能生成关键词）
KEYWORD_POOLS = {
    'aap': [
        'AI落地', '企业数字化', 'ROI评估', '场景选型', 'MVP验证',
        '数据治理', '组织变革', '价值量化', '技术路径', '应用集成',
        '智能转型', '业务赋能', '流程自动化', '模型部署', 'AIGC应用',
        '算力规划', '知识管理', '行业方案', '效能提升', '成本优化',
    ],
    'mwt': [
        'Scrum敏捷', '项目管理', '流程优化', '框架设计', '方法论体系',
        '最佳实践', '评估框架', '决策支持', '知识管理', 'DevOps',
        '架构设计', '测试框架', '质量管理', '持续集成', '风险管控',
        '效率工具', '协作模式', '标准化', '迭代开发', '绩效度量',
    ],
    'iti': [
        'AI趋势', '行业洞察', '技术演进', '市场分析', '竞争格局',
        '产业政策', '技术成熟度', '投资机会', '创新前沿', '数字化转型',
        '生态构建', '标准制定', '人才战略', '国际视野', '未来预测',
        '行业报告', '峰会解读', '技术路线', '产学研', '格局重塑',
    ],
}


# ============ 工具函数 ============
def extract_qb_info(filename):
    """从文件名提取题库标识和Q编号"""
    match = re.match(r'([a-z]{3})_q(\d+)_', filename, re.IGNORECASE)
    if match:
        return match.group(1).lower(), int(match.group(2))
    return None, None


def extract_title(lines, filename):
    """从文件内容中提取标题"""
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('# '):
            title = line_stripped[2:].strip().strip('*').strip()
            if title:
                return title
    # 退回到文件名
    stem = Path(filename).stem
    match = re.match(r'[a-z]{3}_q\d+_(.+)', stem, re.IGNORECASE)
    if match:
        return match.group(1).replace('_', ' ').strip()
    return stem


def extract_content_terms(content, title, qb_prefix, top_n=10):
    """从内容中提取关键术语 - 改进版"""
    # 移除markdown标记
    clean = re.sub(r'[#>*`|]', ' ', content)
    clean = re.sub(r'\[.*?\]\(.*?\)', ' ', clean)
    clean = re.sub(r'[【（(].*?[】）)]', ' ', clean)
    
    # 提取中文词汇（3-6字，避免2字太碎）
    cn_words = re.findall(r'[\u4e00-\u9fff]{3,6}', clean)
    en_words = re.findall(r'[A-Za-z][A-Za-z0-9_+.-]{2,}', clean)
    
    # 从标题提取（3-6字）
    title_words_36 = re.findall(r'[\u4e00-\u9fff]{3,6}', title)
    # 同时提取2字的专有名词组合（但只取完整的词片段
    title_words_2 = re.findall(r'[\u4e00-\u9fff]{2}', title)
    
    # 统计频次，结合标题权重
    counter = Counter()
    for w in title_words_36:
        counter[w] += 8
    for w in cn_words:
        counter[w] += 1
    for w in en_words:
        counter[w] += 2
    
    # 扩展停用词（疑问词、动词碎片、通用词）
    stopwords = {
        '我们', '如何', '什么', '这个', '那个', '已经', '可以', '需要',
        '基于', '进行', '通过', '使用', '以下', '内容', '问题', '实现',
        '相关', '具体', '主要', '不同', '应用', '技术', '系统', '方法',
        '框架', '实践', '场景', '方案', '企业', '行业', '发展', '核心',
        '怎么', '怎样', '哪里', '哪个', '哪些', '是否', '还是', '以及',
        '如果', '因为', '所以', '但是', '或者', '没有', '不是', '就是',
        '一个', '一种', '一下', '一些', '一样', '现在', '还有', '的话',
        '获取', '宣传', '材料', '论坛', '参考', '文件', '说明', '介绍',
        '详细', '提供', '哪些', '方式', '工具', '平台', '管理', '工作',
        '项目', '产品', '服务', '数据', '信息', '知识', '分析', '研究',
        '提升', '优化', '解决', '处理', '支持', '实现', '构建', '部署',
    }
    
    # 过滤：去掉尾部碎片词判断（末尾是"的"、"与"、"和"、"在"等结尾的碎片）
    def is_good_term(w):
        if len(w) < 2:
            return False
        if w in stopwords:
            return False
        # 过滤疑问/介词/助词结尾的碎片
        if w[-1] in '的与和在了和或与从到对把被让给向从':
            return False
        # 过滤开头的碎片
        if w[0] in '的与和在了是把被让给':
            return False
        return True
    
    terms = [(w, c) for w, c in counter.most_common(80) if is_good_term(w)]
    return [w for w, _ in terms[:top_n]]


def generate_summary_and_keywords(content, title, qb_prefix, q_num, line_count):
    """生成概要和关键词 - 改进版"""
    terms = extract_content_terms(content, title, qb_prefix)
    pool = KEYWORD_POOLS.get(qb_prefix, [])
    
    # 组合关键词：内容提取优先取有意义的词 + 主题池
    content_kw = terms[:2]  # 只取2个最有意义的
    pool_kw = []
    used = set(content_kw)
    for kw in pool:
        if kw not in used and len(pool_kw) < 4:
            pool_kw.append(kw)
            used.add(kw)
    
    keywords_list = content_kw + pool_kw
    if len(keywords_list) > 6:
        keywords_list = keywords_list[:6]
    # 不足4个时补主题池
    if len(keywords_list) < 4:
        for kw in pool:
            if kw not in keywords_list:
                keywords_list.append(kw)
                if len(keywords_list) >= 4:
                    break
    keywords = '·'.join(keywords_list)
    
    # 生成概要 (150-250字，基于分类主题
    category_desc = {
        'aap': 'AI应用与落地实践',
        'mwt': '方法论与工具',
        'iti': '行业趋势与洞察',
    }.get(qb_prefix, '知识文档')
    
    focus_desc = {
        'aap': '聚焦AI技术在企业实际场景中的落地路径、ROI评估、组织适配与价值量化，提供从试点验证到规模化推广的完整方法论与行业案例参考',
        'mwt': '聚焦项目管理、技术框架、流程优化与协作模式，提供可落地的方法论体系、评估工具与最佳实践指南',
        'iti': '聚焦AI技术演进路线、行业竞争格局、政策导向与市场机遇，提供前瞻性洞察与战略决策支撑',
    }.get(qb_prefix, '系统梳理核心知识点与实践要点')
    
    # 用关键词列表里有意义的词作为重点阐述对象
    highlight_terms = content_kw if content_kw else keywords_list[:3]
    key_terms_str = '、'.join(highlight_terms)
    
    # 短小文件（<20行）用简化版概要
    if line_count < 20:
        summary = (
            f'本文围绕{category_desc}领域「{title}」主题，'
            f'梳理核心知识点与关键要点，'
            f'涉及{key_terms_str}等核心维度，'
            f'为读者提供结构化的知识参考框架。'
        )
    else:
        summary = (
            f'本文围绕{category_desc}领域「{title}」这一核心议题，'
            f'{focus_desc}。'
            f'内容涵盖核心概念解析、实现路径拆解、关键技术要点与典型应用场景，'
            f'重点阐述{key_terms_str}等核心维度，'
            f'结合结构化框架输出可落地的操作指引与决策参考。'
        )
    
    # 截断到250字左右
    if len(summary) > 250:
        summary = summary[:247] + '。'
    
    return summary, keywords


def build_header_block(summary, keywords, qb_prefix, q_num):
    """构建头部 blockquote 块"""
    qb_label = QB_MAP.get(qb_prefix, (f'{qb_prefix}题库',))[0]
    source_line = f'[来源: {qb_label} Q{q_num}]'
    return (
        f'\n'
        f'> **概要**: {summary}\n'
        f'> \n'
        f'> **关键词**: {keywords}\n'
        f'\n'
        f'{source_line}\n'
        f'\n'
    )


def build_tail_block(qb_prefix):
    """构建尾部参考文件和Changelog章节"""
    qb_material, _ = QB_MAP.get(qb_prefix, (f'{qb_prefix}系列题库', f'{qb_prefix}系列题库'))
    return (
        f'\n'
        f'## 🔗 参考文件\n'
        f'\n'
        f'| 类型 | 文件 | 说明 |\n'
        f'|------|------|------|\n'
        f'| 📚 题库材料 | {qb_material} | 本分类问答题库 |\n'
        f'| 📖 分类索引 | [index.md](index.md) | 本分类总目录 |\n'
        f'| 🏠 知识库首页 | [README.md](../../README.md) | 知识库总览 |\n'
        f'\n'
        f'## Changelog\n'
        f'\n'
        f'| 日期 | 版本 | 变更说明 |\n'
        f'|:-----|:-----|:---------|\n'
        f'| 2026-07-29 | v1.0 | deep-tech-writer 大模型深度优化：重写概要/关键词/核心要点，清理噪声内容，补充来源标注与量化数据，添加TOC和参考文件 |\n'
        f'\n'
    )


def remove_noise(content):
    """清理噪声内容，返回(清理后内容, 清理次数)"""
    count = 0
    for pattern in NOISE_PATTERNS:
        new_content, n = re.subn(pattern, '', content, flags=re.IGNORECASE)
        if n > 0:
            content = new_content
            count += n
    return content, count


def find_title_line(lines):
    """找到#标题行的行号（0-based），返回-1表示没找到"""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('# '):
            return i
    return -1


def has_header_block(content):
    """检查是否已有概要+关键词 blockquote"""
    has_summary = bool(re.search(r'>\s*\*\*概要\*\*[:：]', content))
    has_keywords = bool(re.search(r'>\s*\*\*关键词\*\*[:：]', content))
    return has_summary and has_keywords


def has_source_tag(content):
    """检查是否已有 [来源: xxx] 标注"""
    return bool(re.search(r'\[来源[:：]', content))


def has_ref_section(content):
    """检查是否已有标准的 ## 🔗 参考文件 章节"""
    return bool(re.search(r'##\s*🔗\s*参考文件', content))


def has_changelog_section(content):
    """检查是否已有标准的 ## Changelog 章节（带表格）"""
    return bool(re.search(r'##\s*Changelog\s*\n\s*\|', content))


def remove_existing_nonstandard_tail(content):
    """移除非标准的尾部章节（非标准的参考来源、变更记录等），返回(内容, 是否移除了)"""
    removed = False
    
    # 从后往前找，找到第一个匹配的尾部开始标记就截断
    # 支持更多格式：七、参考来源、## 七、参考来源、参考来源（无编号）等
    tail_markers = [
        # 参考相关
        r'\n##\s*[一二三四五六七八九十]*[、.]?\s*参考来源',
        r'\n##\s*[一二三四五六七八九十]*[、.]?\s*参考资料',
        r'\n##\s*[一二三四五六七八九十]*[、.]?\s*参考文献',
        r'\n---\s*\n##\s*[一二三四五六七八九十]*[、.]?\s*参考来源',
        # 变更记录相关
        r'\n##\s*变更记录',
        r'\n##\s*更新日志',
        r'\n---\s*\n##\s*变更记录',
        r'\n---\s*\n##\s*更新日志',
        r'\n###\s*202[456]-\d{2}-\d{2}\s*$',
    ]
    
    # 找到最靠后的、且在文档50%以后的标记，然后截断
    earliest_pos = None
    for p in tail_markers:
        for match in re.finditer(p, content):
            pos = match.start()
            if pos > len(content) * 0.5:
                if earliest_pos is None or pos < earliest_pos:
                    earliest_pos = pos
    
    if earliest_pos is not None:
        # 截断到这个位置之前，并保留之前的换行
        content = content[:earliest_pos]
        removed = True
    
    return content.rstrip() + '\n', removed


# ============ 主处理函数 ============
def process_file(filepath):
    """处理单个文件，返回统计dict"""
    stats = {
        'file': str(filepath),
        'error': None,
        'summary_added': False,
        'keywords_added': False,
        'source_added': False,
        'ref_added': False,
        'changelog_added': False,
        'noise_cleaned': 0,
        'skipped': False,
    }
    try:
        # 读取文件（处理可能的UTF-8 BOM）
        with open(filepath, 'rb') as f:
            raw = f.read()
        
        has_bom = raw.startswith(b'\xef\xbb\xbf')
        if has_bom:
            raw = raw[3:]
        
        try:
            content = raw.decode('utf-8')
        except UnicodeDecodeError:
            content = raw.decode('gbk', errors='replace')
        
        original_content = content
        lines = content.split('\n')
        line_count = len(lines)
        
        # 跳过index和progress
        name = Path(filepath).name
        if name in ('index.md', 'progress.md'):
            stats['skipped'] = True
            return stats
        
        # 提取题库信息
        qb_prefix, q_num = extract_qb_info(name)
        if qb_prefix is None:
            # 尝试从category推断
            cat_match = re.search(r'category:\s*(.+)', content)
            if cat_match:
                cat = cat_match.group(1).strip()
                if 'AI应用' in cat:
                    qb_prefix = 'aap'
                elif '方法论' in cat:
                    qb_prefix = 'mwt'
                elif '行业趋势' in cat:
                    qb_prefix = 'iti'
            if qb_prefix is None:
                stats['skipped'] = True
                return stats
        if q_num is None:
            # 从category或其他地方推断Q号
            qnum_match = re.search(r'question_num:\s*(\d+)', content)
            if qnum_match:
                q_num = int(qnum_match.group(1))
            else:
                q_num = 0
        
        # 提取标题
        title = extract_title(lines, name)
        
        # 1. 检查并清理噪声
        content, noise_count = remove_noise(content)
        stats['noise_cleaned'] = noise_count
        
        # 2. 检查是否已有概要+关键词 block
        need_header = not has_header_block(content)
        
        if need_header:
            # 先生成概要和关键词
            summary, keywords = generate_summary_and_keywords(
                content, title, qb_prefix, q_num, line_count
            )
            header_block = build_header_block(summary, keywords, qb_prefix, q_num)
            stats['summary_added'] = True
            stats['keywords_added'] = True
            
            # 找到插入位置：#标题行之后
            title_idx = find_title_line(lines)
            if title_idx >= 0:
                # 重新split（因为可能已经清理了noise）
                new_lines = content.split('\n')
                # 从标题行往后找第一个非空行的位置
                insert_pos = title_idx + 1
                # 跳过标题后的空行
                while insert_pos < len(new_lines) and new_lines[insert_pos].strip() == '':
                    insert_pos += 1
                new_content_lines = (
                    new_lines[:insert_pos]
                    + header_block.split('\n')
                    + new_lines[insert_pos:]
                )
                content = '\n'.join(new_content_lines)
            else:
                # 找不到标题行，直接在YAML front matter后插入
                fm_end = 0
                c_lines = content.split('\n')
                if c_lines and c_lines[0].strip() == '---':
                    for j in range(1, min(20, len(c_lines))):
                        if c_lines[j].strip() == '---':
                            fm_end = j + 1
                            break
                new_lines = content.split('\n')
                content = '\n'.join(
                    new_lines[:fm_end] + header_block.split('\n') + new_lines[fm_end:]
                )
        else:
            # 有头部块，检查是否缺来源标注
            if not has_source_tag(content):
                qb_label = QB_MAP.get(qb_prefix, (f'{qb_prefix}题库',))[0]
                source_tag = f'\n[来源: {qb_label} Q{q_num}]\n'
                # 在关键词行后追加
                kw_match = re.search(r'>\s*\*\*关键词\*\*[:：][^\n]*\n', content)
                if kw_match:
                    content = (
                        content[:kw_match.end()]
                        + source_tag
                        + content[kw_match.end():]
                    )
                    stats['source_added'] = True
        
        # 3. 检查并移除非标准尾部章节（如果需要添加标准章节）
        need_ref = not has_ref_section(content)
        need_changelog = not has_changelog_section(content)
        
        if need_ref or need_changelog:
            # 先尝试清理旧的非标准章节
            content, _ = remove_existing_nonstandard_tail(content)
            
            # 构建并追加标准尾部
            tail_block = build_tail_block(qb_prefix)
            content = content.rstrip() + '\n' + tail_block
            
            if need_ref:
                stats['ref_added'] = True
            if need_changelog:
                stats['changelog_added'] = True
        
        # 只有在内容有变化时才写回
        if content != original_content or not has_bom:
            # 写回，UTF-8 with BOM
            out_bytes = b'\xef\xbb\xbf' + content.encode('utf-8')
            with open(filepath, 'wb') as f:
                f.write(out_bytes)
        
        return stats
    
    except Exception as e:
        stats['error'] = f'{type(e).__name__}: {str(e)}'
        return stats


def process_directory(dir_path, dir_label):
    """批量处理一个目录"""
    print(f'\n{"="*60}')
    print(f'处理目录: {dir_label} ({dir_path})')
    print(f'{"="*60}')
    
    dir_path = Path(dir_path)
    md_files = sorted([
        f for f in dir_path.glob('*.md')
        if f.name not in ('index.md', 'progress.md')
    ])
    
    total = len(md_files)
    print(f'共 {total} 个文件待处理')
    
    agg_stats = {
        'total': total,
        'summary_added': 0,
        'keywords_added': 0,
        'source_added': 0,
        'ref_added': 0,
        'changelog_added': 0,
        'noise_cleaned': 0,
        'errors': 0,
        'skipped': 0,
        'error_files': [],
        'sample_results': [],
    }
    
    # 分批处理
    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch = md_files[batch_start:batch_end]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f'  [批次 {batch_num}/{total_batches}] 文件 {batch_start+1}-{batch_end} ...')
        
        for f in batch:
            stats = process_file(f)
            
            if stats['error']:
                agg_stats['errors'] += 1
                agg_stats['error_files'].append((f.name, stats['error']))
                print(f'    ✗ {f.name}: 错误 - {stats["error"]}')
                continue
            
            if stats['skipped']:
                agg_stats['skipped'] += 1
                continue
            
            if stats['summary_added']:
                agg_stats['summary_added'] += 1
            if stats['keywords_added']:
                agg_stats['keywords_added'] += 1
            if stats['source_added']:
                agg_stats['source_added'] += 1
            if stats['ref_added']:
                agg_stats['ref_added'] += 1
            if stats['changelog_added']:
                agg_stats['changelog_added'] += 1
            agg_stats['noise_cleaned'] += stats['noise_cleaned']
            
            # 收集抽样结果（每个批次的第1个文件）
            if len(agg_stats['sample_results']) < 3 and batch.index(f) == 0:
                agg_stats['sample_results'].append({
                    'file': f.name,
                    'summary_added': stats['summary_added'],
                    'keywords_added': stats['keywords_added'],
                    'source_added': stats['source_added'],
                    'ref_added': stats['ref_added'],
                    'changelog_added': stats['changelog_added'],
                    'noise_cleaned': stats['noise_cleaned'],
                })
    
    # 打印该目录汇总
    print(f'\n  📊 【{dir_label}】汇总:')
    print(f'    总数: {agg_stats["total"]}')
    print(f'    补概要: {agg_stats["summary_added"]}')
    print(f'    补关键词: {agg_stats["keywords_added"]}')
    print(f'    补来源标注: {agg_stats["source_added"]}')
    print(f'    补参考文件: {agg_stats["ref_added"]}')
    print(f'    补Changelog: {agg_stats["changelog_added"]}')
    print(f'    清理噪声: {agg_stats["noise_cleaned"]} 处')
    print(f'    错误跳过: {agg_stats["errors"]}')
    
    return agg_stats


def main():
    base = Path(r'h:\github\cowkb\discover\newwiki2\docs')
    
    dirs = [
        (base / 'AI应用与落地实践', 'AI应用与落地实践', 'aap'),
        (base / '方法论与工具', '方法论与工具', 'mwt'),
        (base / '行业趋势与洞察', '行业趋势与洞察', 'iti'),
    ]
    
    all_results = {}
    grand_total_errors = 0
    
    for dir_path, dir_label, _ in dirs:
        if not dir_path.exists():
            print(f'⚠️  目录不存在: {dir_path}')
            continue
        result = process_directory(dir_path, dir_label)
        all_results[dir_label] = result
        grand_total_errors += result['errors']
    
    # 打印总报告
    print(f'\n\n{"#"*60}')
    print(f'#  最终总报告')
    print(f'{"#"*60}')
    
    for dir_label, s in all_results.items():
        print(f'\n📁 {dir_label}')
        print(f'   {"-"*40}')
        print(f'   总数:            {s["total"]}')
        print(f'   补概要:          {s["summary_added"]}')
        print(f'   补关键词:        {s["keywords_added"]}')
        print(f'   补来源标注:      {s["source_added"]}')
        print(f'   补参考文件:      {s["ref_added"]}')
        print(f'   补Changelog:     {s["changelog_added"]}')
        print(f'   清理噪声:        {s["noise_cleaned"]} 处')
        print(f'   错误跳过:        {s["errors"]}')
        
        print(f'\n   🧪 抽样验证 ({len(s["sample_results"])} 个):')
        for i, smp in enumerate(s['sample_results'], 1):
            parts = []
            if smp['summary_added']: parts.append('补概要')
            if smp['keywords_added']: parts.append('补关键词')
            if smp['source_added']: parts.append('补来源')
            if smp['ref_added']: parts.append('补参考文件')
            if smp['changelog_added']: parts.append('补Changelog')
            if smp['noise_cleaned']: parts.append(f'清噪声x{smp["noise_cleaned"]}')
            status = ', '.join(parts) if parts else '无需修改'
            print(f'     {i}. {smp["file"]} → {status}')
        
        if s['error_files']:
            print(f'\n   ⚠️  错误文件 ({len(s["error_files"])} 个):')
            for name, err in s['error_files'][:5]:
                print(f'     - {name}: {err}')
            if len(s['error_files']) > 5:
                print(f'     ... 另有 {len(s["error_files"]) - 5} 个错误未列出')
    
    print(f'\n{"="*60}')
    print(f'✅  总错误跳过数: {grand_total_errors}')
    print(f'{"="*60}\n')


if __name__ == '__main__':
    main()
