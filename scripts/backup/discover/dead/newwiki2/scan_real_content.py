import os
import re
import json

BASE_DIR = r'h:\github\cowkb\discover\newwiki2\programming'

def analyze_file_real_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {
        'filename': os.path.basename(filepath),
        'title': '',
        'total_words': 0,
        'real_content_words': 0,
        'template_words': 0,
        'has_real_content': False,
        'real_content_ratio': 0,
        'quality': ''
    }
    
    # 提取标题
    h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if h1_match:
        info['title'] = h1_match.group(1).strip()
    
    # 总字数
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    english_words = len(re.findall(r'[a-zA-Z]+', content))
    info['total_words'] = chinese_chars + english_words
    
    # 提取"原始内容归档"之后的内容（真实内容）
    archive_match = re.search(r'## 8\. 原始内容归档(.*)', content, re.DOTALL)
    if archive_match:
        real_content = archive_match.group(1)
        real_chinese = len(re.findall(r'[\u4e00-\u9fff]', real_content))
        real_english = len(re.findall(r'[a-zA-Z]+', real_content))
        info['real_content_words'] = real_chinese + real_english
        info['template_words'] = info['total_words'] - info['real_content_words']
    
    if info['total_words'] > 0:
        info['real_content_ratio'] = info['real_content_words'] / info['total_words']
    
    # 判断是否有真实内容（原始归档中超过200字且不是纯索引页）
    archive_content = archive_match.group(1) if archive_match else ''
    is_index_page = '本卡片为知识索引页' in archive_content or '收录卡片' in archive_content
    info['is_index_page'] = is_index_page
    
    if info['real_content_words'] > 500 and not is_index_page:
        info['has_real_content'] = True
    
    # 真实质量评级（基于真实内容，而不是模板外壳）
    real_wc = info['real_content_words']
    if real_wc >= 2000 and not is_index_page:
        info['quality'] = 'A'
    elif real_wc >= 1000 and not is_index_page:
        info['quality'] = 'B'
    elif real_wc >= 400 and not is_index_page:
        info['quality'] = 'C'
    elif real_wc >= 100:
        info['quality'] = 'D'
    else:
        info['quality'] = 'D'
    
    return info

def main():
    files = [f for f in os.listdir(BASE_DIR) if f.endswith('.md') and f != 'index.md']
    files.sort()
    
    all_info = []
    for f in files:
        filepath = os.path.join(BASE_DIR, f)
        info = analyze_file_real_content(filepath)
        all_info.append(info)
    
    # 统计
    quality_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
    index_pages = []
    for info in all_info:
        quality_counts[info['quality']] += 1
        if info['is_index_page']:
            index_pages.append(info['filename'])
    
    print('=' * 70)
    print('  programming/ 目录真实内容质量扫描报告')
    print('  （基于"原始内容归档"中的真实内容，排除模板外壳）')
    print('=' * 70)
    print(f'  总文件数: {len(all_info)}')
    print(f'  索引页(无真实内容): {len(index_pages)} 个')
    print()
    print('  真实质量等级分布:')
    for q in ['A', 'B', 'C', 'D']:
        bar = '█' * quality_counts[q]
        print(f'    {q}级: {quality_counts[q]:2d} 个 {bar}')
    print()
    
    # 按真实内容字数排序，找出最有价值增强的
    print('\n  --- 有真实内容的文件（按真实字数排序）---')
    real_files = [info for info in all_info if info['has_real_content']]
    real_files.sort(key=lambda x: x['real_content_words'], reverse=True)
    for i, info in enumerate(real_files[:30]):
        ratio_pct = int(info['real_content_ratio'] * 100)
        print(f"    {i+1:2d}. {info['filename']:30s} | 真实{info['real_content_words']:4d}字 | 占比{ratio_pct:2d}% | {info['quality']}级")
    
    # 索引页列表
    print(f'\n  --- 索引页（无实质内容，共{len(index_pages)}个）---')
    for f in index_pages:
        print(f"    - {f}")
    
    # D级文件（真实内容极少的）
    d_files = [info for info in all_info if info['quality'] == 'D' and not info['is_index_page']]
    print(f'\n  --- D级文件（真实内容<400字，共{len(d_files)}个）---')
    for info in sorted(d_files, key=lambda x: x['real_content_words']):
        print(f"    - {info['filename']:30s} | 真实{info['real_content_words']:3d}字")
    
    # 保存JSON
    with open(os.path.join(BASE_DIR, '..', 'programming_real_quality.json'), 'w', encoding='utf-8') as f:
        json.dump(all_info, f, ensure_ascii=False, indent=2)
    
    print('\n' + '=' * 70)
    print(f'  详细数据已保存到 programming_real_quality.json')
    print('=' * 70)

if __name__ == '__main__':
    main()
