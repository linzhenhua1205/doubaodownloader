import re

with open('h:/github/md/html/2df93dba-6dce-4de9-8020-f8fae2b69c4d.htm', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL)
content = re.sub(r'<[^>]+>', '\n', content)
content = re.sub(r'\s+', '\n', content)

lines = content.split('\n')

print("=== HTML文件内容预览 ===")
print(f"总行数: {len(lines)}")
print("\n前100行内容:")
for i, line in enumerate(lines[:100], 1):
    if line.strip():
        print(f"{i}: {line[:100]}")