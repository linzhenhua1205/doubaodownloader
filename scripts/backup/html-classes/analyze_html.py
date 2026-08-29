import re

with open('h:/github/md/html/2df93dba-6dce-4de9-8020-f8fae2b69c4d.htm', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("搜索包含 'user' 或 'assistant' 的行:")
lines = content.split('\n')
for i, line in enumerate(lines[:200], 1):
    if 'user' in line.lower() or 'assistant' in line.lower():
        print(f"{i}: {line[:150]}")