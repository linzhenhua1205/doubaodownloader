import os
import re

dir_path = r'h:\github\cowkb\discover\newwiki2\programming'

# 检查几个模板化文件的原始内容
files = [
    '业智方舟.md',
    '产品力量理论.md', 
    '企业系统演化.md',
    '讯飞星辰.md',
    '超智能与未来.md',
    'ipd.md',
    'paperclip.md',
]

for filename in files:
    filepath = os.path.join(dir_path, filename)
    print(f"\n{'='*80}")
    print(f"文件: {filename}")
    print(f"{'='*80}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找原始内容归档部分
    match = re.search(r'## 8\. 原始内容归档\s*\n(.*)', content, re.DOTALL)
    if match:
        original = match.group(1).strip()
        # 打印前2000字
        print(original[:2000])
        if len(original) > 2000:
            print(f"\n... (原始内容共 {len(original)} 字)")
    else:
        print("没有找到原始内容归档部分")
        # 打印全文的后500字看看
        print("\n文件末尾500字:")
        print(content[-500:])
