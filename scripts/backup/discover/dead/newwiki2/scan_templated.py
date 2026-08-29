"""
批量检测并统计服务器硬件目录下的模板化文件
"""
import os
import re
import json

def check_templated(filepath):
    """检测文件是否为严重模板化"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None
    
    # 模板化标志
    templated_markers = [
        '（以下为原始内容，已整合到增强版中）',
        '主流方案对比\n\n| 维度 | 方案A | 方案B | 方案C |',
        '代际技术对比\n\n| 代际 | 年份 | 关键特性 | 性能提升 | 代表产品 |',
        '不同规模场景对比\n\n| 规模 | 小型 | 中型 | 大型 | 超大型 |',
        '成本构成对比\n\n| 成本项 | 占比 | 说明 | 优化空间 |',
        '选型决策流程\n```\n',
        '案例一：大型互联网公司',
        '案例二：金融企业',
        '案例三：初创企业',
        '入门级（1-2个月）\n  │\n  ├─ 基础概念和术语',
    ]
    
    score = 0
    found_markers = []
    for marker in templated_markers:
        if marker in content:
            score += 1
            found_markers.append(marker[:30])
    
    # 检查frontmatter状态是否虚高
    status_match = re.search(r'status:\s*(.+?)\n', content)
    status = status_match.group(1).strip() if status_match else ''
    
    # 计算真实内容字数（去掉模板部分）
    # 粗略估计：有多少真实内容
    
    return {
        'filepath': filepath,
        'templated_score': score,
        'found_markers': found_markers,
        'status': status,
        'is_severely_templated': score >= 4,  # 4个以上模板标志
        'total_length': len(content),
    }

def scan_directory(dirpath):
    """扫描目录下所有md文件"""
    results = []
    for root, dirs, files in os.walk(dirpath):
        for file in files:
            if file.endswith('.md') and file != 'index.md':
                filepath = os.path.join(root, file)
                result = check_templated(filepath)
                if result:
                    results.append(result)
    return results

def main():
    base_dir = r'h:\github\cowkb\discover\newwiki2'
    
    dirs_to_check = [
        'server-hardware',
        '服务器硬件',
    ]
    
    all_results = []
    for d in dirs_to_check:
        dirpath = os.path.join(base_dir, d)
        if os.path.exists(dirpath):
            results = scan_directory(dirpath)
            all_results.extend(results)
            print(f'\n=== {d} 目录统计 ===')
            print(f'总文件数: {len(results)}')
            severe = [r for r in results if r['is_severely_templated']]
            print(f'严重模板化: {len(severe)}')
            for r in severe:
                print(f"  - {os.path.basename(r['filepath'])} (模板分: {r['templated_score']}, 状态: {r['status']})")
    
    # 保存结果
    output_file = os.path.join(base_dir, 'templated_files_scan.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f'\n结果已保存到: {output_file}')

if __name__ == '__main__':
    main()
