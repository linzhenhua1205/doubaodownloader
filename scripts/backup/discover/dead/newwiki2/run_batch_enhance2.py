import sys
sys.path.insert(0, r'h:\github\cowkb\discover\newwiki2')
from batch_deep_enhance import enhance_file
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r'h:\github\cowkb\discover\newwiki2')

targets = [
    ('papers-research', 'research'),
    ('编程语言', 'programming'),
    ('软件架构', 'architecture'),
    ('算法优化', 'algorithm'),
    ('研究与论文', 'research'),
]

all_results = {}
grand_total = 0
grand_success = 0

print("=" * 70)
print("7大模块深度增强 - 剩余目录批量执行")
print("=" * 70)
print()

for dirname, topic_type in targets:
    dir_path = BASE_DIR / dirname
    if not dir_path.exists():
        print(f"【跳过】{dirname} - 目录不存在")
        continue
    
    print(f"【处理目录】{dirname} (主题类型: {topic_type})")
    print("-" * 50)
    
    md_files = sorted([f for f in dir_path.glob('*.md') if f.name != 'index.md'])
    results = []
    
    for fpath in md_files:
        name = fpath.name
        success, msg = enhance_file(fpath, topic_type)
        results.append((name, success, msg))
        status_char = '✓' if success else '✗'
        print(f"  {status_char} {name}: {msg}")
    
    all_results[dirname] = results
    total = len(results)
    success = sum(1 for _, s, _ in results if s)
    grand_total += total
    grand_success += success
    
    print(f"  统计: 共{total}个文件，成功{success}个")
    print()

print("=" * 70)
print("【汇总统计】")
print(f"  处理目录: {len(targets)}")
print(f"  处理文件: {grand_total} 个")
print(f"  成功增强: {grand_success} 个")
print(f"  跳过/失败: {grand_total - grand_success} 个")
print("=" * 70)

with open(BASE_DIR / 'batch_deep_enhance_report2.json', 'w', encoding='utf-8') as f:
    json.dump({
        'date': datetime.now().isoformat(),
        'targets': targets,
        'grand_total': grand_total,
        'grand_success': grand_success,
        'results': {k: [{'file': n, 'success': s, 'message': m} for n, s, m in v] for k, v in all_results.items()},
    }, f, ensure_ascii=False, indent=2)

print(f"\n详细报告已保存到 batch_deep_enhance_report2.json")
