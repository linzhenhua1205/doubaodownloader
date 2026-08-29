import re
from pathlib import Path

BASE_DIR = Path(r'h:\github\cowkb\discover\newwiki2')

target_dirs = [
    'programming',
    '编程语言',
    '软件架构',
    'project-mgmt',
    'security',
    '算法优化',
    '研究与论文',
    'research',
    'papers-research',
]

no_fm_files = []
has_fm_files = []

for dirname in target_dirs:
    dir_path = BASE_DIR / dirname
    if not dir_path.exists():
        continue
    for f in sorted(dir_path.glob('*.md')):
        if f.name == 'index.md':
            continue
        content = f.read_text(encoding='utf-8')
        if content.startswith('---'):
            has_fm_files.append(f)
        else:
            no_fm_files.append(f)

print(f"有frontmatter: {len(has_fm_files)} 个文件")
print(f"无frontmatter: {len(no_fm_files)} 个文件")
print()
if no_fm_files:
    print("无frontmatter的文件:")
    for f in no_fm_files[:30]:
        print(f"  {f.relative_to(BASE_DIR)}")
    if len(no_fm_files) > 30:
        print(f"  ... 还有 {len(no_fm_files) - 30} 个")
