import os
import re

dir_path = r'h:\github\cowkb\discover\newwiki2\programming'

# 检查几个文件的结构，找到原始内容的正确位置
files = ['业智方舟.md', '产品力量理论.md', '讯飞星辰.md']

for filename in files:
    filepath = os.path.join(dir_path, filename)
    print(f"\n{'='*80}")
    print(f"文件: {filename}")
    print(f"{'='*80}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"总行数: {len(lines)}")
    
    # 查找所有的二级标题
    print("\n所有二级标题（##）:")
    for i, line in enumerate(lines):
        if line.startswith('## '):
            print(f"  行 {i+1}: {line}")
    
    # 找到"原始内容归档"的位置
    for i, line in enumerate(lines):
        if '原始内容' in line:
            print(f"\n找到'原始内容'在行 {i+1}: {line}")
            # 打印后面的10行
            print("后面10行:")
            for j in range(i, min(i+10, len(lines))):
                print(f"  {j+1}: {lines[j]}")
            break
