import os
import re
import traceback
from pathlib import Path

BASE_DIR = r"h:\github\cowkb\discover\newwiki2\docs\AI伦理与安全"
EXCLUDE_FILES = {"index.md", "progress.md", "findings.md", "task_plan.md"}

REFERENCE_SECTION = """## 🔗 参考文件

| 类型 | 文件 | 说明 |
|------|------|------|
| 📚 题库材料 | AI伦理与安全题库 | 本分类问答题库 |
| 📖 分类索引 | [index.md](index.md) | 本分类总目录 |
| 🏠 知识库首页 | [README.md](../../README.md) | 知识库总览 |
"""

CHANGELOG_SECTION = """## Changelog

| 日期 | 版本 | 变更说明 |
|:-----|:-----|:---------|
| 2026-07-29 | v1.0 | deep-tech-writer 大模型深度优化：重写概要/关键词/核心要点，清理噪声内容，补充来源标注与量化数据，添加TOC和参考文件 |
"""

CHANGELOG_V1_ENTRY = "| 2026-07-29 | v1.0 | deep-tech-writer 大模型深度优化：重写概要/关键词/核心要点，清理噪声内容，补充来源标注与量化数据，添加TOC和参考文件 |"


def read_file(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return f.read()


def write_file(filepath, content):
    with open(filepath, "w", encoding="utf-8-sig") as f:
        f.write(content)


def has_section(content, section_title):
    pattern = rf"^##\s+{re.escape(section_title)}\s*$"
    return re.search(pattern, content, re.MULTILINE) is not None


def extract_changelog_table(content):
    pattern = r"##\s+Changelog\s*\n(.*?)(?=\n##\s|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1)
    return None


def has_v1_entry(changelog_table_text):
    return "v1.0" in changelog_table_text and "2026-07-29" in changelog_table_text


def insert_v1_to_changelog(content):
    pattern = r"(##\s+Changelog\s*\n\|.*?\|.*?\|.*?\|\s*\n\|[-: ]+\|[-: ]+\|[-: ]+\|\s*\n)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        header_end = match.end()
        before = content[:header_end]
        after = content[header_end:]
        new_content = before + CHANGELOG_V1_ENTRY + "\n" + after
        return new_content, True
    return content, False


def process_file(filepath):
    content = read_file(filepath)
    original_content = content
    modified = False
    actions = []

    has_ref = has_section(content, "🔗 参考文件")
    has_changelog = has_section(content, "Changelog")

    if not has_ref and not has_changelog:
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + REFERENCE_SECTION + "\n" + CHANGELOG_SECTION
        modified = True
        actions.append("追加参考文件+Changelog")
    elif not has_ref:
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + REFERENCE_SECTION
        modified = True
        actions.append("追加参考文件")
    elif not has_changelog:
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + CHANGELOG_SECTION
        modified = True
        actions.append("追加Changelog")
    else:
        changelog_table = extract_changelog_table(content)
        if changelog_table and not has_v1_entry(changelog_table):
            content, inserted = insert_v1_to_changelog(content)
            if inserted:
                modified = True
                actions.append("Changelog插入v1.0条目")

    if modified and content != original_content:
        write_file(filepath, content)

    return modified, actions


def main():
    base_path = Path(BASE_DIR)
    all_md_files = sorted([f for f in base_path.glob("*.md") if f.name not in EXCLUDE_FILES])

    total = len(all_md_files)
    modified_count = 0
    skipped_count = 0
    error_count = 0
    errors = []
    modified_files = []

    batch_size = 20
    for i in range(0, total, batch_size):
        batch = all_md_files[i:i + batch_size]
        for filepath in batch:
            try:
                modified, actions = process_file(filepath)
                if modified:
                    modified_count += 1
                    modified_files.append((filepath.name, actions))
                else:
                    skipped_count += 1
            except Exception as e:
                error_count += 1
                errors.append((filepath.name, str(e), traceback.format_exc()))

    print("=" * 60)
    print("AI伦理与安全 目录修复报告")
    print("=" * 60)
    print(f"总文件数: {total}")
    print(f"修改文件数: {modified_count}")
    print(f"跳过文件数: {skipped_count}")
    print(f"错误文件数: {error_count}")
    print()

    if modified_files:
        print("修改的文件:")
        for fname, actions in modified_files:
            print(f"  - {fname}: {', '.join(actions)}")
        print()

    if errors:
        print("错误详情:")
        for fname, err, tb in errors:
            print(f"  - {fname}: {err}")

    return {
        "total": total,
        "modified": modified_count,
        "skipped": skipped_count,
        "errors": error_count,
        "modified_files": modified_files,
        "error_details": errors,
    }


if __name__ == "__main__":
    main()
