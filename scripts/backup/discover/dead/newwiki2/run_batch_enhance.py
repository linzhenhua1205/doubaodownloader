import sys
sys.path.insert(0, r'h:\github\cowkb\discover\newwiki2')
from batch_deep_enhance import process_directory
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r'h:\github\cowkb\discover\newwiki2')

target_dirs = [
    'programming',
    'project-mgmt',
    'security',
    'research',
]

all_results = {}
grand_total = 0
grand_success = 0

print("=" * 70)
print("7大模块深度增强 - 全量批量执行")
print("=" * 70)
print()

for dirname in target_dirs:
    print(f"【处理目录】{dirname}")
    print("-" * 50)
    
    results = process_directory(dirname)
    all_results[dirname] = results
    
    total = len(results)
    success = sum(1 for _, s, _ in results if s)
    grand_total += total
    grand_success += success
    
    print(f"  统计: 共{total}个文件，成功{success}个")
    print()

print("=" * 70)
print("【汇总统计】")
print(f"  处理目录: {len(target_dirs)}")
print(f"  处理文件: {grand_total} 个")
print(f"  成功增强: {grand_success} 个")
print(f"  跳过/失败: {grand_total - grand_success} 个")
print("=" * 70)

with open(BASE_DIR / 'batch_deep_enhance_report.json', 'w', encoding='utf-8') as f:
    json.dump({
        'date': datetime.now().isoformat(),
        'target_dirs': target_dirs,
        'grand_total': grand_total,
        'grand_success': grand_success,
        'results': {k: [{'file': n, 'success': s, 'message': m} for n, s, m in v] for k, v in all_results.items()},
    }, f, ensure_ascii=False, indent=2)

print(f"\n详细报告已保存到 batch_deep_enhance_report.json")
