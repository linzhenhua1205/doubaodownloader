import ast

filepath = r'h:\github\cowkb\discover\newwiki2\enhance_batch3.py'

with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

try:
    ast.parse(code)
    print('语法检查通过')
except SyntaxError as e:
    print(f'语法错误: {e.msg}')
    print(f'行号: {e.lineno}')
    print(f'列号: {e.offset}')
    lines = code.split('\n')
    if e.lineno:
        print(f'内容: {lines[e.lineno-1][:150]}')
        # 打印前后几行
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        print('\n上下文:')
        for i in range(start, end):
            marker = '>>>' if i == e.lineno - 1 else '   '
            print(f'{marker} {i+1}: {lines[i][:120]}')
