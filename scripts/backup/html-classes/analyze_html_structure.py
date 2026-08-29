import re

with open('h:/github/md/html/2df93dba-6dce-4de9-8020-f8fae2b69c4d.htm', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

lines = content.split('\n')

print("=== HTML结构分析 ===")
print(f"总行数: {len(lines)}")

user_patterns = ['"user"', "'user'", 'role.*user', 'user.*role']
assistant_patterns = ['"assistant"', "'assistant'", 'role.*assistant', 'assistant.*role']

user_count = 0
assistant_count = 0

for i, line in enumerate(lines[:100], 1):
    for pattern in user_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            user_count += 1
            print(f"第{i}行 (用户): {line[:100]}")
            break
    for pattern in assistant_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            assistant_count += 1
            print(f"第{i}行 (AI): {line[:100]}")
            break

print(f"\n找到用户消息标记: {user_count}")
print(f"找到AI消息标记: {assistant_count}")

print("\n=== 搜索消息内容 ===")
for i, line in enumerate(lines[:150], 1):
    if len(line) > 50 and '<div' not in line.lower() and '<span' not in line.lower():
        print(f"第{i}行: {line[:80]}")