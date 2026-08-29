import os
import re
from pathlib import Path

base_dir = Path(r"h:\github\cowkb\discover\newwiki2")

dirs_to_check = [
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

results = {}

for dir_name in dirs_to_check:
    dir_path = base_dir / dir_name
    if not dir_path.exists():
        continue
    
    files = []
    for f in dir_path.glob("*.md"):
        if f.name == "index.md":
            continue
        try:
            content = f.read_text(encoding="utf-8")
        except:
            continue
        
        status_match = re.search(r"status:\s*(\S+)", content)
        quality_match = re.search(r"quality_level:\s*(\S+)", content)
        word_match = re.search(r"word_count:\s*(\d+)", content)
        
        status = status_match.group(1) if status_match else "unknown"
        quality = quality_match.group(1) if quality_match else "none"
        word_count = int(word_match.group(1)) if word_match else 0
        
        files.append({
            "name": f.name,
            "status": status,
            "quality": quality,
            "word_count": word_count,
        })
    
    results[dir_name] = files

# 输出统计
for dir_name, files in results.items():
    enhanced = [f for f in files if f["status"] in ["深度增强", "增强完成"]]
    pending = [f for f in files if f["status"] not in ["深度增强", "增强完成"]]
    print(f"\n=== {dir_name} ===")
    print(f"总文件数: {len(files)}")
    print(f"已增强: {len(enhanced)}")
    print(f"待增强: {len(pending)}")
    
    # 质量分布
    quality_counts = {}
    for f in files:
        q = f["quality"]
        quality_counts[q] = quality_counts.get(q, 0) + 1
    print(f"质量分布: {quality_counts}")
    
    # 待增强文件列表
    if pending:
        print("待增强文件:")
        for f in pending[:20]:
            print(f"  - {f['name']} (status={f['status']}, words={f['word_count']})")
        if len(pending) > 20:
            print(f"  ... 还有 {len(pending)-20} 个")
