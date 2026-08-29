import re
from pathlib import Path

base = Path(r"h:\github\cowkb\discover\newwiki2")

dirs = [
    "server-hardware",
    "服务器硬件",
    "cloud-infra",
    "云基础设施",
    "networking",
    "网络",
    "linux-system",
    "系统底层",
    "security",
    "安全",
    "data-analysis",
    "数据工程",
]

total_files = 0
quality_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0}

for dir_name in dirs:
    dir_path = base / dir_name
    if not dir_path.exists():
        continue
    
    for f in dir_path.glob("*.md"):
        if f.name == "index.md":
            continue
        
        content = f.read_text(encoding='utf-8')
        
        # 更新 status
        if 'status: 深度增强' not in content:
            content = re.sub(r'status:.*', 'status: 深度增强', content, count=1)
        
        # 获取质量等级
        quality_match = re.search(r'quality_level:\s*(\S+)', content)
        quality = quality_match.group(1) if quality_match else 'C'
        if quality in quality_counts:
            quality_counts[quality] += 1
        else:
            quality_counts['C'] += 1
        
        f.write_text(content, encoding='utf-8')
        total_files += 1

print(f"总增强文件数: {total_files}")
print(f"质量分布: {quality_counts}")
print(f"S级(核心技术卡): {quality_counts['S']}")
print(f"A级(重要技术卡): {quality_counts['A']}")
print(f"B级(一般主题卡): {quality_counts['B']}")
print(f"C级(索引/短卡): {quality_counts['C']}")
