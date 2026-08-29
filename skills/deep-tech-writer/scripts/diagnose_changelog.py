# -*- coding: utf-8 -*-
import re
from pathlib import Path

TARGET_DIR = r"h:\github\cowkb\discover\newwiki2\docs\AI-Agent技术架构"
EXCLUDE_FILES = {"index.md", "progress.md"}

def read_file_md(filepath):
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return f.read()
    except Exception:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

test_file = Path(TARGET_DIR) / "aag_q10_agent_security.md"
content = read_file_md(str(test_file))

print("=== 查找所有 ## 级别的标题 ===")
for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", content, re.MULTILINE):
    level = len(m.group(1))
    title = m.group(2).strip()
    is_cl = any(kw in title.lower() for kw in ["changelog", "更新日志", "更新记录", "变更记录", "版本记录", "版本日志"])
    is_ref = "🔗" in title and "参考" in title
    mark = ""
    if is_cl: mark = " <<< CHANGELOG"
    if is_ref: mark = " <<< REF"
    print(f"  [{level}] '{title}'{mark}")

print()
print("=== 检查文件尾部重复内容 ===")
tail = content[-1500:]
count_cl = len(re.findall(r"^##\s+(Changelog|更新日志)", tail, re.MULTILINE))
count_ref = len(re.findall(r"^##\s+🔗\s*参考文件", tail, re.MULTILINE))
print(f"  尾部 Changelog 标题数: {count_cl}")
print(f"  尾部 参考文件 标题数: {count_ref}")
