import sys
sys.path.insert(0, r'h:\github\cowkb\discover\newwiki2')
from batch_deep_enhance import enhance_file
from pathlib import Path

BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2")

test_file = BASE_DIR / 'programming' / 'paperclip.md'
print(f"测试文件: {test_file}")
print(f"文件存在: {test_file.exists()}")

if test_file.exists():
    success, msg = enhance_file(test_file, 'programming')
    print(f"结果: {success}, {msg}")
