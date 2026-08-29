import re
import unicodedata

with open(r'h:\github\md\服务器架构全面解析.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all code blocks
lines_all = content.split('\n')
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

# Check each block for alignment issues
for start, end in blocks:
    lines = lines_all[start:end]
    # Check for ASCII diagrams (containing box-drawing chars)
    box_chars = set('┌┐└┘├┤┬┴┼│─')
    has_box = any(any(c in box_chars for c in l) for l in lines)
    if not has_box:
        continue

    # Remove empty lines at start/end
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]

    if not lines:
        continue

    def visual_width(s):
        w = 0
        for c in s:
            ea = unicodedata.east_asian_width(c)
            if ea in ('F', 'W'):
                w += 2
            else:
                w += 1
        return w

    widths = [visual_width(l) for l in lines]
    max_w = max(widths) if widths else 0
    min_w = min(widths) if widths else 0

    if len(set(widths)) > 1:
        print(f'Diagram at lines {start+1}-{end+1}:')
        print(f'  Widths: min={min_w}, max={max_w}, lines={len(widths)}')
        for j, (l, w) in enumerate(zip(lines, widths)):
            if w != max_w:
                diff = max_w - w
                short = l[:80] if len(l) <= 80 else l[:77] + '...'
                print(f'  Line {start+1+j}: width={w}, diff={diff}: [{short}]')
        print()

print("Done checking.")