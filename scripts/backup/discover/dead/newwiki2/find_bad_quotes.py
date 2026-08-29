import ast

filepath = r'h:\github\cowkb\discover\newwiki2\enhance_batch3.py'

with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()
lines = code.split('\n')

in_triple_quote = False
problem_lines = []
for i, line in enumerate(lines, 1):
    if '"""' in line:
        count = line.count('"""')
        if count % 2 == 1:
            in_triple_quote = not in_triple_quote
        continue
    
    if in_triple_quote:
        continue
    
    count = 0
    j = 0
    while j < len(line):
        if line[j] == '\\':
            j += 2
            continue
        if line[j] == '"':
            count += 1
        j += 1
    
    if count % 2 != 0:
        problem_lines.append((i, count, line[:120]))

print(f'发现 {len(problem_lines)} 行有奇数个引号:')
for line_num, count, content in problem_lines:
    print(f'  第{line_num}行（{count}个引号）: {content}')
