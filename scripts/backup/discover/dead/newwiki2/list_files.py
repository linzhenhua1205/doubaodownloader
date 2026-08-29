import os

dir_path = r'h:\github\cowkb\discover\newwiki2\programming'
files = os.listdir(dir_path)

print(f"总文件数: {len(files)}")
print("\n所有文件:")
for f in sorted(files):
    if f.endswith('.md'):
        full_path = os.path.join(dir_path, f)
        size = os.path.getsize(full_path)
        print(f"  {f:<40} {size:>8} bytes")

# 查找特定文件
print("\n\n查找包含'飞书'的文件:")
for f in files:
    if '飞书' in f:
        print(f"  找到: {f}")

print("\n查找包含'研发'的文件:")
for f in files:
    if '研发' in f:
        print(f"  找到: {f}")
