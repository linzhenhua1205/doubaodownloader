import re

test_lines = [
    '🏗️ **查询执行架构变化**',
    '⚖️ **性能调优建议**',
    '📌 **核心结论**',
    '🔍 **实验验证方法**',
    '📊 **参数对比表**',
    '💡 **移除核心原因分析**',
]

pattern = r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]\s*\*\*(.+?)\*\*\s*$'

for line in test_lines:
    match = re.match(pattern, line)
    if match:
        print(f"✅ 匹配: {line} -> {match.group(1)}")
    else:
        print(f"❌ 不匹配: {line}")
        print(f"   首字符: {repr(line[0])}, U+{ord(line[0]):04X}")
