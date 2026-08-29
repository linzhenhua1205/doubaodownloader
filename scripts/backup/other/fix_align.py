import unicodedata

with open(r'h:\github\md\服务器架构全面解析.md', 'r', encoding='utf-8') as f:
    content = f.read()

lines_all = content.split('\n')

def visual_width(s):
    w = 0
    for c in s:
        ea = unicodedata.east_asian_width(c)
        if ea in ('F', 'W'):
            w += 2
        else:
            w += 1
    return w

# Find all code blocks
blocks = []
in_block = False
block_start = 0
for i, line in enumerate(lines_all):
    if line.strip() == '```' and not in_block:
        in_block = True
        block_start = i + 1
    elif line.strip() == '```' and in_block:
        in_block = False
        blocks.append((block_start, i))

# Let's just debug the first boxed diagram
for start, end in blocks:
    block_lines = list(lines_all[start:end])
    box_chars = set('┌┐└┘├┤┬┴┼│─')
    has_box = any(any(c in box_chars for c in l) for l in block_lines)
    if not has_box:
        continue
    while block_lines and not block_lines[-1].strip():
        block_lines.pop()
    while block_lines and not block_lines[0].strip():
        block_lines.pop(0)
    if not block_lines:
        continue
    first = block_lines[0].lstrip()
    if not (first.startswith('┌') and first.endswith('┐')):
        continue
    
    print(f"Diagram at line {start+1}:")
    for i, l in enumerate(block_lines[:5]):
        w = visual_width(l)
        s = l.rstrip()
        print(f"  Line {i}: len={len(l)}, vw={w}, repr={repr(l[-10:])}")
        if s.endswith('│'):
            content = s[:-1].rstrip()
            print(f"    content_repr={repr(content[-10:])}, content_vw={visual_width(content)}")
    break