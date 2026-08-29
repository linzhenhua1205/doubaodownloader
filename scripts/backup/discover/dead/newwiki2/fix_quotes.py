import re

filepath = r'h:\github\cowkb\discover\newwiki2\enhance_batch3.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # 跳过三引号字符串
    if '"""' in line:
        fixed_lines.append(line)
        continue
    
    # 查找在双引号字符串内部的中文引号
    # 策略：找到所有 "..." 模式的字符串，替换内部的 " 为 「/」
    result = []
    i = 0
    in_string = False
    quote_count = 0
    
    while i < len(line):
        if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
            if not in_string:
                in_string = True
                quote_count = 1
                result.append(line[i])
            else:
                # 检查这是结束引号还是字符串内部的引号
                # 简单启发：如果后面还有 : 或 , 或 ] 等，可能是结束
                # 更简单的方法：统计该行的引号数量，如果是偶数个以上就有问题
                quote_count += 1
                # 先假设是结束引号
                in_string = False
                result.append(line[i])
            i += 1
        elif in_string and line[i] == '"':
            # 字符串内部的引号 - 替换为 「 或 」
            # 简单替换为「
            result.append('「')
            i += 1
        else:
            result.append(line[i])
            i += 1
    
    fixed_line = ''.join(result)
    fixed_lines.append(fixed_line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("已尝试修复引号")
