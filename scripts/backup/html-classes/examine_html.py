import re

with open('h:/github/md/html/2df93dba-6dce-4de9-8020-f8fae2b69c4d.htm', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

lines = content.split('\n')

print("前50行内容:")
for i, line in enumerate(lines[:50], 1):
    if len(line) > 0:
        print(f"{i}: {line[:100]}")

print("\n\n搜索包含 'message' 的行:")
for i, line in enumerate(lines, 1):
    if 'message' in line.lower() and len(line) > 50:
        print(f"{i}: {line[:150]}")