import os
import re
from pathlib import Path

BASE_DIR = r"h:\github\cowkb\discover\newwiki2\docs\方法论与工具"
EXCLUDE_FILES = {"index.md", "progress.md", "task_plan.md", "findings.md"}


def read_file(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return f.read()


def has_summary_keywords(content):
    has_summary = bool(re.search(r"^>\s*\*\*概要\*\*\s*:", content, re.MULTILINE))
    has_keywords = bool(re.search(r"^>\s*\*\*关键词\*\*\s*:", content, re.MULTILINE))
    return has_summary and has_keywords


def extract_q_number(filename):
    match = re.search(r"mwt_q(\d+)_", filename)
    if match:
        return match.group(1)
    return None


def main():
    base_path = Path(BASE_DIR)
    all_md_files = sorted([f for f in base_path.glob("*.md") if f.name not in EXCLUDE_FILES])

    total = len(all_md_files)
    missing_count = 0
    has_count = 0
    missing_files = []
    sample_missing = []
    sample_has = []

    for filepath in all_md_files:
        try:
            content = read_file(filepath)
            if has_summary_keywords(content):
                has_count += 1
                if len(sample_has) < 3:
                    sample_has.append(filepath.name)
            else:
                missing_count += 1
                missing_files.append(filepath.name)
                if len(sample_missing) < 5:
                    sample_missing.append(filepath.name)
        except Exception as e:
            print(f"Error reading {filepath.name}: {e}")

    print("=" * 60)
    print("方法论与工具 目录 概要+关键词检查报告")
    print("=" * 60)
    print(f"总文件数: {total}")
    print(f"已有概要+关键词: {has_count}")
    print(f"缺少概要+关键词: {missing_count}")
    print()

    if sample_missing:
        print(f"缺少的文件抽样 ({len(sample_missing)}/{missing_count}):")
        for fname in sample_missing:
            q_num = extract_q_number(fname)
            print(f"  - {fname} (Q{q_num})")
        print()

    if sample_has:
        print(f"已有的文件抽样 ({len(sample_has)}/{has_count}):")
        for fname in sample_has:
            q_num = extract_q_number(fname)
            print(f"  - {fname} (Q{q_num})")

    return missing_files


if __name__ == "__main__":
    main()
