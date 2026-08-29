#!/usr/bin/env python3
"""测试第一批优化（仅处理1批）"""

import sys
import os
import json
from pathlib import Path
import time

sys.path.insert(0, r"h:\github\cowkb\skills\deep-tech-writer\scripts")
import batch_optimize_math_prog_960 as opt

opt.STATE_FILE = r"h:\github\cowkb\skills\deep-tech-writer\scripts\.math_prog_opt_state_test.json"

def main():
    print("="*70)
    print("🧪 测试模式：仅处理第一批验证效果")
    print(f"   分批大小: {opt.BATCH_SIZE}")
    print("="*70)
    
    state = {"processed": [], "failed": []}
    
    dirs = [
        (r"h:\github\cowkb\discover\newwiki2\docs\其他_数学算法", 1),
        (r"h:\github\cowkb\discover\newwiki2\docs\其他_编程语言", 1),
    ]
    
    all_stats = []
    t_start = time.time()
    
    for d, max_b in dirs:
        stats = opt.process_directory(d, state, max_batches=max_b)
        all_stats.append((os.path.basename(d), stats))
    
    total_elapsed = time.time() - t_start
    
    print(f"\n{'='*70}")
    print(f"🏁 测试批次完成  ⏱ 总耗时: {total_elapsed:.1f}s")
    print(f"{'='*70}")
    
    grand_ok = grand_already = grand_skip = grand_fail = grand_added = 0
    for dir_name, s in all_stats:
        print(f"\n📁 {dir_name}:")
        print(f"   ✅ 优化成功: {s['ok']} | ♻️ 已是优化: {s['already']} | ⏭ 跳过: {s['skip']} | ❌ 失败: {s['fail']}")
        print(f"   ➕ 新增行数: {s['added']}")
        grand_ok += s['ok']; grand_already += s['already']; grand_skip += s['skip']
        grand_fail += s['fail']; grand_added += s['added']
    
    print(f"\n{'─'*70}")
    print(f"📊 测试总计: ✅{grand_ok}  ♻️{grand_already}  ⏭{grand_skip}  ❌{grand_fail}  |  +{grand_added} 行")
    print(f"{'='*70}")
    
    if state["failed"]:
        print(f"\n⚠️  失败列表:")
        for item in state["failed"]:
            print(f"   - {item['file']}: {item['error']}")

if __name__ == '__main__':
    main()
