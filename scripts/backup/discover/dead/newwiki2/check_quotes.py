import re

filepath = r'h:\github\cowkb\discover\newwiki2\enhance_batch3.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 找出所有问题行
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    # 简单检查：一行中有超过4个双引号可能有问题
    if line.count('"') > 4 and '"""' not in line:
        print(f'第{i}行（{line.count(chr(34))}个引号）: {line[:100]}')
