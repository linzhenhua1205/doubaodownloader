import os

# 读取几个待确认文件的前100行，检查内容
files_to_check = [
    '飞书.md',
    '研发协作痛点.md',
    '分布式系统并.md',
    '知识库沉淀.md',
    '简化即信心.md',
    '学习.md',
    '需求拆解与对.md',
]

dir_path = r'h:\github\cowkb\discover\newwiki2\programming'

for filename in files_to_check:
    filepath = os.path.join(dir_path, filename)
    print(f"\n{'='*80}")
    print(f"文件: {filename}")
    print(f"大小: {os.path.getsize(filepath)} bytes")
    print(f"{'='*80}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:60]):
            print(f"{i+1:3d}: {line.rstrip()}")
        if len(lines) > 60:
            print(f"... (共 {len(lines)} 行)")
