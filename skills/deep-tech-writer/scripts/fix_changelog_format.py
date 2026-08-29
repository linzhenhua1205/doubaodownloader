# -*- coding: utf-8 -*-
import os
import re
import traceback
from pathlib import Path

TARGET_DIR = r"h:\github\cowkb\discover\newwiki2\docs\AI-Agent技术架构"
EXCLUDE_FILES = {"index.md", "progress.md"}

V1_DATE = "2026-07-29"
V1_VERSION = "v1.0"
V1_DESC = "deep-tech-writer 标准化优化：统一 Changelog 格式为三列表格，补充参考文件章节，修正标题规范"

STANDARD_REF_SECTION = """## 🔗 参考文件

| 类型 | 文件 | 说明 |
|------|------|------|
| 📚 题库材料 | aag_系列问答库 | AI-Agent技术架构分类问答题库 |
| 📖 分类索引 | [index.md](index.md) | 本分类总目录 |
| 🏠 知识库首页 | [README.md](../../README.md) | 知识库总览 |
"""

STANDARD_CHANGELOG_HEADER = "## Changelog\n\n| 日期 | 版本 | 变更说明 |\n|------|------|----------|\n"


def read_file_md(filepath):
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return f.read()
    except Exception:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()


def write_file_md(filepath, content):
    with open(filepath, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(content)


def split_sections(content):
    lines = content.split("\n")
    sections = []
    current_title = None
    current_lines = []
    front_matter = []
    in_front_matter = False
    front_matter_done = False

    i = 0
    while i < len(lines):
        line = lines[i]
        if not front_matter_done:
            if line.strip() == "---" and not in_front_matter:
                in_front_matter = True
                front_matter.append(line)
                i += 1
                continue
            elif line.strip() == "---" and in_front_matter:
                in_front_matter = False
                front_matter_done = True
                front_matter.append(line)
                i += 1
                continue
            elif in_front_matter:
                front_matter.append(line)
                i += 1
                continue
            else:
                front_matter_done = True

        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m:
            if current_title is not None:
                sections.append((current_title, "\n".join(current_lines)))
            current_title = line
            current_lines = []
        else:
            if current_title is None:
                if front_matter:
                    sections.append(("__FRONT_MATTER__", "\n".join(front_matter)))
                    front_matter = []
                    current_title = "__PRE_CONTENT__"
                    current_lines = [line]
                else:
                    current_title = "__PRE_CONTENT__"
                    current_lines = [line]
            else:
                current_lines.append(line)
        i += 1

    if current_title is not None:
        sections.append((current_title, "\n".join(current_lines)))
    elif front_matter:
        sections.append(("__FRONT_MATTER__", "\n".join(front_matter)))

    return sections


def is_changelog_title(title_line):
    m = re.match(r"^#{1,6}\s+(.+?)\s*$", title_line)
    if not m:
        return False
    title_text = m.group(1).strip()
    title_clean = re.sub(r"^[\s\S]*?\s*", "", title_text)
    for kw in ["changelog", "更新日志", "更新记录", "变更记录", "版本记录", "版本日志"]:
        if kw.lower() in title_clean.lower():
            return True
    return False


def is_ref_title(title_line):
    m = re.match(r"^#{1,6}\s+(.+?)\s*$", title_line)
    if not m:
        return False
    title_text = m.group(1).strip()
    if "🔗" in title_text and "参考" in title_text:
        return True
    if title_text == "🔗 参考文件":
        return True
    if re.match(r"^🔗\s*参考文件$", title_text):
        return True
    return False


def parse_changelog_entries(section_body):
    lines = section_body.strip().split("\n")
    entries = []

    table_pattern = re.compile(r"^\s*\|(.+)\|\s*$")
    in_table = False
    header_seen = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if table_pattern.match(stripped):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= 3:
                if not header_seen and any(h in cells[0].lower() for h in ["日期", "date", "时间"]):
                    header_seen = True
                    in_table = True
                    continue
                if in_table or header_seen:
                    if re.match(r"^[-:|\s]+$", stripped.replace("|", "").strip()):
                        continue
                    date = cells[0] if len(cells) > 0 else ""
                    version = cells[1] if len(cells) > 1 else ""
                    desc = cells[2] if len(cells) > 2 else ""
                    if date or version or desc:
                        entries.append((date, version, desc))
                        in_table = True
                    continue

    if entries:
        return entries

    list_entries = []
    current_date = None
    for line in lines:
        stripped = line.strip()
        m_date = re.match(r"^#{1,6}\s*(\d{4}-\d{2}-\d{2})", stripped)
        if m_date:
            current_date = m_date.group(1)
            continue
        m_date2 = re.match(r"^[-*]\s*(\d{4}-\d{2}-\d{2})", stripped)
        if m_date2:
            current_date = m_date2.group(1)
            continue
        m_date3 = re.match(r"^(\d{4}-\d{2}-\d{2})\s*[:：-]?\s*(.*)", stripped)
        if m_date3:
            current_date = m_date3.group(1)
            desc = m_date3.group(2).strip()
            if desc:
                list_entries.append((current_date, "", desc))
            continue
        m_item = re.match(r"^[-*]\s+(.+)$", stripped)
        if m_item and current_date:
            desc = m_item.group(1).strip()
            list_entries.append((current_date, "", desc))
            continue
        if stripped and current_date and not stripped.startswith("|") and not stripped.startswith("#"):
            list_entries.append((current_date, "", stripped))

    return list_entries


def build_changelog_table(entries):
    has_v1 = False
    for date, ver, desc in entries:
        if date == V1_DATE and ver == V1_VERSION:
            has_v1 = True
            break

    if not has_v1:
        entries.insert(0, (V1_DATE, V1_VERSION, V1_DESC))

    lines = [STANDARD_CHANGELOG_HEADER.rstrip()]
    for date, ver, desc in entries:
        date_s = date if date else ""
        ver_s = ver if ver else ""
        desc_s = desc.replace("|", "\\|") if desc else ""
        lines.append(f"| {date_s} | {ver_s} | {desc_s} |")

    return "\n".join(lines) + "\n"


def process_file(filepath):
    stats = {
        "title_fixed": 0,
        "v1_added": 0,
        "table_converted": 0,
        "sections_appended": 0,
        "ref_fixed": 0,
        "skipped": False,
        "error": None,
    }
    sample_info = []

    try:
        content = read_file_md(filepath)
        original_content = content
        sections = split_sections(content)

        changelog_idx = None
        ref_idx = None
        changelog_title_line = None
        ref_title_line = None
        changelog_entries = []
        changelog_was_table = False

        for i, (title, body) in enumerate(sections):
            if title == "__FRONT_MATTER__" or title == "__PRE_CONTENT__":
                continue
            if is_changelog_title(title):
                changelog_idx = i
                changelog_title_line = title
                m = re.match(r"^#{1,6}\s+(.+?)\s*$", title)
                if m:
                    t = m.group(1).strip()
                    if t not in ["Changelog", "🔗 参考文件"]:
                        stats["title_fixed"] = 1
                        sample_info.append(f"标题修正: '{t}' -> 'Changelog'")
                entries = parse_changelog_entries(body)
                changelog_entries = entries
                if entries:
                    sample_info.append(f"解析到 {len(entries)} 条记录")
                    has_v1 = any(d == V1_DATE and v == V1_VERSION for d, v, _ in entries)
                    if not has_v1:
                        stats["v1_added"] = 1
                        sample_info.append(f"补充 v1.0 + {V1_DATE} 条目")
                else:
                    stats["table_converted"] = 1
                    stats["v1_added"] = 1
                    sample_info.append("Changelog 非表格格式，已转换为三列表格")
            elif is_ref_title(title):
                ref_idx = i
                ref_title_line = title
                m = re.match(r"^#{1,6}\s+(.+?)\s*$", title)
                if m:
                    t = m.group(1).strip()
                    if t != "🔗 参考文件":
                        stats["ref_fixed"] = 1
                        sample_info.append(f"参考文件标题修正: '{t}' -> '🔗 参考文件'")

        new_sections = []
        for i, (title, body) in enumerate(sections):
            if i == changelog_idx:
                new_body = build_changelog_table(changelog_entries).rstrip("\n")
                new_sections.append(("## Changelog", new_body))
                if changelog_was_table and not stats["title_fixed"] and not stats["v1_added"]:
                    pass
                continue
            if i == ref_idx:
                ref_body = body.strip()
                if not ref_body or "暂无" in ref_body or ref_body.startswith("-") or "| 类型 |" not in ref_body:
                    new_body = "\n".join(STANDARD_REF_SECTION.split("\n")[1:]).rstrip("\n")
                    stats["ref_fixed"] = 1
                    sample_info.append("参考文件章节已补充标准表格内容")
                else:
                    new_body = body
                new_sections.append(("## 🔗 参考文件", new_body))
                continue
            new_sections.append((title, body))

        if changelog_idx is None and ref_idx is None:
            stats["sections_appended"] = 1
            stats["v1_added"] = 1
            sample_info.append("Changelog 和 参考文件 章节都不存在，已在文件末尾追加")
            new_body_parts = []
            for title, body in new_sections:
                if title == "__FRONT_MATTER__":
                    new_body_parts.append(body)
                elif title == "__PRE_CONTENT__":
                    if body.strip():
                        new_body_parts.append(body)
                else:
                    new_body_parts.append(title)
                    if body.strip():
                        new_body_parts.append(body)

            result_content = "\n".join(new_body_parts)
            if not result_content.endswith("\n"):
                result_content += "\n"
            if not result_content.endswith("\n\n"):
                result_content += "\n"
            result_content += "\n" + STANDARD_REF_SECTION.rstrip() + "\n\n"
            result_content += build_changelog_table([]).rstrip() + "\n"
        else:
            if ref_idx is None and changelog_idx is not None:
                stats["sections_appended"] = 1
                stats["ref_fixed"] = 1
                sample_info.append("缺少参考文件章节，已在 Changelog 前插入")
                final_sections = []
                inserted = False
                for title, body in new_sections:
                    if title == "## Changelog" and not inserted:
                        final_sections.append(("## 🔗 参考文件", "\n".join(STANDARD_REF_SECTION.split("\n")[1:]).rstrip("\n")))
                        inserted = True
                    final_sections.append((title, body))
                new_sections = final_sections

            if changelog_idx is None and ref_idx is not None:
                stats["sections_appended"] = 1
                stats["v1_added"] = 1
                stats["table_converted"] = 1
                sample_info.append("缺少 Changelog 章节，已在参考文件后追加")
                final_sections = []
                inserted = False
                for title, body in new_sections:
                    final_sections.append((title, body))
                    if title == "## 🔗 参考文件" and not inserted:
                        cl_body = build_changelog_table([]).rstrip("\n")
                        final_sections.append(("## Changelog", cl_body))
                        inserted = True
                if not inserted:
                    cl_body = build_changelog_table([]).rstrip("\n")
                    final_sections.append(("## Changelog", cl_body))
                new_sections = final_sections

            if not stats["sections_appended"]:
                pass

            new_body_parts = []
            for title, body in new_sections:
                if title == "__FRONT_MATTER__":
                    new_body_parts.append(body)
                elif title == "__PRE_CONTENT__":
                    if body.strip():
                        new_body_parts.append(body)
                else:
                    new_body_parts.append(title)
                    if body.strip():
                        new_body_parts.append(body)

            result_content = "\n".join(new_body_parts)
            if not result_content.endswith("\n"):
                result_content += "\n"

        if result_content != original_content:
            write_file_md(filepath, result_content)

        stats["sample"] = sample_info
        return stats

    except Exception as e:
        stats["error"] = str(e)
        stats["skipped"] = True
        stats["sample"] = [f"ERROR: {str(e)}"]
        return stats


def main():
    target_path = Path(TARGET_DIR)
    md_files = sorted([f for f in target_path.glob("*.md") if f.name not in EXCLUDE_FILES])

    print(f"共发现 {len(md_files)} 个 .md 文件（排除 index.md / progress.md）")
    print("=" * 80)

    total_stats = {
        "title_fixed": 0,
        "v1_added": 0,
        "table_converted": 0,
        "sections_appended": 0,
        "ref_fixed": 0,
        "total_processed": 0,
        "errors": 0,
    }

    sample_results = []
    problem_files = []

    for i, fp in enumerate(md_files):
        s = process_file(str(fp))
        total_stats["total_processed"] += 1

        changed = s["title_fixed"] or s["v1_added"] or s["table_converted"] or s["sections_appended"] or s["ref_fixed"]

        if s["error"]:
            total_stats["errors"] += 1
            print(f"[ERROR] {fp.name}: {s['error'][:80]}")
            continue

        total_stats["title_fixed"] += s["title_fixed"]
        total_stats["v1_added"] += s["v1_added"]
        total_stats["table_converted"] += s["table_converted"]
        total_stats["sections_appended"] += s["sections_appended"]
        total_stats["ref_fixed"] += s["ref_fixed"]

        if changed:
            problem_files.append((fp.name, s))
            if len(sample_results) < 10:
                sample_results.append((fp.name, s))

    while len(sample_results) < 10 and len(problem_files) > len(sample_results):
        idx = len(sample_results)
        if idx < len(problem_files):
            sample_results.append(problem_files[idx])

    print("\n" + "=" * 80)
    print("修复统计结果")
    print("=" * 80)
    print(f"总处理文件数:     {total_stats['total_processed']}")
    print(f"存在问题文件数:   {len(problem_files)}")
    print(f"改标题数:         {total_stats['title_fixed']}  (更新日志/变更记录 → Changelog)")
    print(f"补v1条目数:       {total_stats['v1_added']}  (补充 {V1_DATE} + {V1_VERSION})")
    print(f"转表格数:         {total_stats['table_converted']}  (列表/纯文字 → 三列表格)")
    print(f"追加章节数:       {total_stats['sections_appended']}  (Changelog / 参考文件)")
    print(f"参考文件修正数:   {total_stats['ref_fixed']}  (标题/内容补充)")
    print(f"错误跳过数:       {total_stats['errors']}")

    print("\n" + "=" * 80)
    print(f"抽样验证结果（{min(10, len(sample_results))} 个原问题文件）")
    print("=" * 80)

    for i, (fname, s) in enumerate(sample_results, 1):
        print(f"\n[{i}] {fname}")
        tags = []
        if s["title_fixed"]: tags.append("标题修正")
        if s["v1_added"]: tags.append("补v1条目")
        if s["table_converted"]: tags.append("转表格")
        if s["sections_appended"]: tags.append("追加章节")
        if s["ref_fixed"]: tags.append("参考文件")
        print(f"  修复类型: {', '.join(tags)}")
        for info in s.get("sample", []):
            print(f"    • {info}")

    print("\n" + "=" * 80)
    print("处理完成！")


if __name__ == "__main__":
    main()
