import os
import re

BASE_DIR = r'h:\github\cowkb\discover\newwiki2\ai-models'

def get_file_info(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {
        'filename': os.path.basename(filepath),
        'title': '',
        'word_count': 0,
        'quality': '',
        'structure_score': 0
    }
    
    # 提取标题
    h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if h1_match:
        info['title'] = h1_match.group(1).strip()
    
    # 统计字数（中文字符 + 英文单词）
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    english_words = len(re.findall(r'[a-zA-Z]+', content))
    info['word_count'] = chinese_chars + english_words
    
    # 结构检查
    required_sections = [
        '卡片定位', '核心要点', '深度', '最新进展',
        '应用场景', '相关资源', '参考来源', '更新日志'
    ]
    present = 0
    for section in required_sections:
        if section in content:
            present += 1
    info['structure_score'] = f'{present}/{len(required_sections)}'
    
    # 质量评级
    if info['word_count'] >= 1500 and present >= 6:
        info['quality'] = 'S级'
    elif info['word_count'] >= 800 and present >= 5:
        info['quality'] = 'A级'
    elif info['word_count'] >= 400 and present >= 4:
        info['quality'] = 'B级'
    elif info['word_count'] >= 200:
        info['quality'] = 'C级'
    else:
        info['quality'] = 'D级'
    
    # 标题是否损坏（包含特殊字符如 # 或 ](）
    if '#' in info['title'] and info['title'].count('#') > 1:
        info['title_damaged'] = True
    elif '](' in info['title']:
        info['title_damaged'] = True
    else:
        info['title_damaged'] = False
    
    return info

def main():
    files = [f for f in os.listdir(BASE_DIR) if f.endswith('.md') and f != 'index.md']
    files.sort()
    
    all_info = []
    for f in files:
        filepath = os.path.join(BASE_DIR, f)
        info = get_file_info(filepath)
        all_info.append(info)
    
    # 统计
    quality_counts = {'S级': 0, 'A级': 0, 'B级': 0, 'C级': 0, 'D级': 0}
    damaged_titles = []
    
    for info in all_info:
        quality_counts[info['quality']] += 1
        if info['title_damaged']:
            damaged_titles.append(info['filename'])
    
    print('=' * 60)
    print('  ai-models 目录质量统计报告')
    print('=' * 60)
    print(f'  总文件数: {len(all_info)}')
    print()
    print('  质量等级分布:')
    for q in ['S级', 'A级', 'B级', 'C级', 'D级']:
        bar = '█' * (quality_counts[q] // 2)
        print(f'    {q}: {quality_counts[q]:2d} 个 {bar}')
    print()
    print(f'  标题损坏: {len(damaged_titles)} 个')
    if damaged_titles:
        for f in damaged_titles:
            print(f'    - {f}')
    print()
    
    # 字数分布
    word_counts = [info['word_count'] for info in all_info]
    word_counts.sort()
    print(f'  字数范围: {min(word_counts)} - {max(word_counts)}')
    print(f'  平均字数: {sum(word_counts) // len(word_counts)}')
    print(f'  中位数: {word_counts[len(word_counts)//2]}')
    print()
    
    # 各等级代表文件
    print('  各质量等级示例文件:')
    for q in ['S级', 'A级', 'B级']:
        examples = [info for info in all_info if info['quality'] == q][:3]
        if examples:
            print(f'    {q}:')
            for ex in examples:
                print(f'      - {ex["filename"]} ({ex["word_count"]}字, 结构{ex["structure_score"]})')
    
    print()
    print('=' * 60)

if __name__ == '__main__':
    main()
