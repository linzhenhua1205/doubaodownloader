import re

filepath = r'h:\github\cowkb\discover\newwiki2\enhance_batch3.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixed_lines = []
in_triple_quote = False

for line_num, line in enumerate(lines, 1):
    # 处理三引号
    if '"""' in line:
        count = line.count('"""')
        if count % 2 == 1:
            in_triple_quote = not in_triple_quote
        fixed_lines.append(line)
        continue
    
    if in_triple_quote:
        fixed_lines.append(line)
        continue
    
    # 检查是否是包含中文字符串的行
    # 找出所有 "..." 模式
    # 简单策略：如果一行中双引号数量 > 2 且有中文字符，可能有问题
    
    quote_positions = []
    i = 0
    while i < len(line):
        if line[i] == '\\':
            i += 2
            continue
        if line[i] == '"':
            quote_positions.append(i)
        i += 1
    
    # 如果引号数量是偶数且 > 2，检查是否是嵌套问题
    # 简单启发式：找到 "xxx"yyy"zzz" 这种模式，把中间的换成「」
    if len(quote_positions) > 2 and len(quote_positions) % 2 == 0:
        # 把第2个到倒数第2个之间的引号替换
        chars = list(line)
        # 找到最外层的引号（第一个和最后一个）
        # 中间的都替换为「或」
        if len(quote_positions) >= 4:
            # 第2个引号（索引1）到倒数第2个引号（索引-2）之间的替换
            # 但这可能不准确，让我们用更简单的方法：
            # 把所有中文语境下的 "..." 替换为「...」
            
            # 重新构建：检测 "中文" 模式
            result = []
            i = 0
            while i < len(chars):
                if chars[i] == '"':
                    # 检查前后是否有中文字符
                    has_chinese_before = False
                    has_chinese_after = False
                    
                    # 往前看
                    for j in range(i-1, max(-1, i-10), -1):
                        if j >= 0 and '\u4e00' <= chars[j] <= '\u9fff':
                            has_chinese_before = True
                            break
                        if chars[j] not in ' \t':
                            break
                    
                    # 往后看
                    for j in range(i+1, min(len(chars), i+10)):
                        if '\u4e00' <= chars[j] <= '\u9fff':
                            has_chinese_after = True
                            break
                        if chars[j] not in ' \t':
                            break
                    
                    if has_chinese_before and has_chinese_after:
                        # 中文语境下的引号，替换为「或」
                        # 简单起见，都换成「，反正内容里用哪个都差不多
                        result.append('「')
                        i += 1
                        continue
                
                result.append(chars[i])
                i += 1
            
            fixed_line = ''.join(result)
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("已尝试修复所有中文语境下的引号问题")
