import os
import re
from pathlib import Path

BASE_DIR = r"h:\github\cowkb\discover\newwiki2\docs\方法论与工具"
EXCLUDE_FILES = {"index.md", "progress.md", "task_plan.md", "findings.md"}


def read_file(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return f.read()


def diagnose_file(content):
    issues = []

    has_summary_half = bool(re.search(r"^>\s*\*\*概要\*\*\s*:", content, re.MULTILINE))
    has_summary_full = bool(re.search(r"^>\s*\*\*概要\*\*\s*：", content, re.MULTILINE))
    has_keywords_half = bool(re.search(r"^>\s*\*\*关键词\*\*\s*:", content, re.MULTILINE))
    has_keywords_full = bool(re.search(r"^>\s*\*\*关键词\*\*\s*：", content, re.MULTILINE))

    if not (has_summary_half or has_summary_full):
        issues.append("缺少概要")
    if not (has_keywords_half or has_keywords_full):
        issues.append("缺少关键词")

    if has_summary_full:
        issues.append("概要使用全角冒号")
    if has_keywords_full:
        issues.append("关键词使用全角冒号")

    keywords_line = re.search(r"^(>\s*\*\*关键词\*\*\s*[:：].*)$", content, re.MULTILINE)
    if keywords_line:
        kw_text = keywords_line.group(1)
        if "[来源:" not in kw_text and "[来源：" not in kw_text:
            issues.append("关键词行末尾无来源标注")
        elif "方法论与工具题库" not in kw_text:
            issues.append("关键词来源格式不对(应为'方法论与工具题库 QX')")

    summary_line = re.search(r"^(>\s*\*\*概要\*\*\s*[:：].*)$", content, re.MULTILINE)
    if summary_line:
        s_text = summary_line.group(1)
        if "[来源:" in s_text or "[来源：" in s_text:
            issues.append("概要行含来源(应放在关键词行)")

    return issues


def extract_q_number(filename):
    match = re.search(r"mwt_q(\d+)_", filename)
    if match:
        return match.group(1)
    return None


def main():
    base_path = Path(BASE_DIR)
    all_md_files = sorted([f for f in base_path.glob("*.md") if f.name not in EXCLUDE_FILES])

    total = len(all_md_files)
    clean_count = 0
    issue_count = 0
    issues_summary = {}
    sample_issues = []
    missing_both = []

    for filepath in all_md_files:
        try:
            content = read_file(filepath)
            issues = diagnose_file(content)
            if not issues:
                clean_count += 1
            else:
                issue_count += 1
                for issue in issues:
                    issues_summary[issue] = issues_summary.get(issue, 0) + 1
                if len(sample_issues) < 8:
                    sample_issues.append((filepath.name, issues))
                if "缺少概要" in issues and "缺少关键词" in issues:
                    missing_both.append(filepath.name)
        except Exception as e:
            print(f"Error reading {filepath.name}: {e}")

    print("=" * 70)
    print("方法论与工具 目录 概要+关键词 全面诊断报告")
    print("=" * 70)
    print(f"总文件数: {total}")
    print(f"格式完全正确: {clean_count}")
    print(f"存在格式问题: {issue_count}")
    print()

    print("问题统计:")
    for issue, cnt in sorted(issues_summary.items(), key=lambda x: -x[1]):
        print(f"  - {issue}: {cnt} 个文件")
    print()

    if sample_issues:
        print(f"问题抽样 ({len(sample_issues)} 个):")
        for fname, issues in sample_issues:
            q_num = extract_q_number(fname)
            print(f"  - {fname} (Q{q_num}): {'; '.join(issues)}")
    print()

    if missing_both:
        print(f"完全缺少概要+关键词的文件 ({len(missing_both)} 个):")
        for fname in missing_both[:10]:
            print(f"  - {fname}")
        if len(missing_both) > 10:
            print(f"  ... 还有 {len(missing_both)-10} 个")

    return issues_summary, missing_both


if __name__ == "__main__":
    main()
