# -*- coding: utf-8 -*-
import re
from pathlib import Path

TARGET_DIR = r"h:\github\cowkb\discover\newwiki2\docs\AI-Agent技术架构"
EXCLUDE_FILES = {"index.md", "progress.md"}

V1_DATE = "2026-07-29"
V1_VERSION = "v1.0"
V1_DESC = "deep-tech-writer 标准化优化：统一 Changelog 格式为三列表格，补充参考文件章节，修正标题规范"

STANDARD_REF = """## 🔗 参考文件

| 类型 | 文件 | 说明 |
|------|------|------|
| 📚 题库材料 | aag_系列问答库 | AI-Agent技术架构分类问答题库 |
| 📖 分类索引 | [index.md](index.md) | 本分类总目录 |
| 🏠 知识库首页 | [README.md](../../README.md) | 知识库总览 |"""

STANDARD_CL_HEADER = "| 日期 | 版本 | 变更说明 |\n|------|------|----------|"

CHANGELOG_TITLE_KWS = [
    "changelog", "更新日志", "更新记录", "变更记录",
    "版本记录", "版本日志", "版本历史", "修订记录"
]

REF_TITLE_KWS = ["🔗", "参考文件"]


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


def is_changelog_title(text):
    t = text.strip().lower()
    return any(kw in t for kw in CHANGELOG_TITLE_KWS)


def is_ref_title(text):
    t = text.strip()
    has_link = "🔗" in t
    has_ref = "参考文件" in t or "参考资料" in t
    if has_link and ("参考" in t or "资料" in t):
        return True
    if re.match(r"^🔗\s*参考文件$", t):
        return True
    return False


def extract_changelog_entries(section_text):
    entries = []
    lines = section_text.split("\n")

    table_cells = []
    in_table = False
    for line in lines:
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 3:
                if any(h in cells[0].lower() for h in ["日期", "date", "时间"]):
                    in_table = True
                    continue
                if re.match(r"^[-:|\s]+$", s.replace("|", "").strip()):
                    continue
                date, ver, desc = cells[0], cells[1], cells[2] if len(cells) > 2 else ""
                if date or ver or desc:
                    table_cells.append((date, ver, desc))
                    in_table = True
                    continue
    if table_cells:
        for date, ver, desc in table_cells:
            if date == V1_DATE and ver == V1_VERSION:
                continue
            entries.append((date, ver, desc))

    if not entries or True:
        current_date = None
        for line in lines:
            s = line.strip()
            m = re.match(r"^#{1,6}\s*(\d{4}-\d{2}-\d{2})", s)
            if m:
                current_date = m.group(1)
                continue
            m = re.match(r"^(?:[-*•]|\d+\.)\s*(\d{4}-\d{2}-\d{2})(?:\s*[:：-]\s*(.*))?$", s)
            if m:
                current_date = m.group(1)
                if m.group(2):
                    d = m.group(2).strip()
                    if d:
                        entries.append((current_date, "", d))
                continue
            m = re.match(r"^(\d{4}-\d{2}-\d{2})\s*[:：-]\s*(.*)$", s)
            if m:
                current_date = m.group(1)
                d = m.group(2).strip()
                if d:
                    entries.append((current_date, "", d))
                continue
            m = re.match(r"^(?:[-*•]|\d+\.)\s+(.+)$", s)
            if m and current_date:
                d = m.group(1).strip()
                if d and not d.startswith("202"):
                    entries.append((current_date, "", d))
                continue

    seen = set()
    unique = []
    for e in entries:
        if e not in seen:
            seen.add(e)
            unique.append(e)

    return unique


def find_section_ranges(content):
    positions = []
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", content, re.MULTILINE):
        level = len(m.group(1))
        title = m.group(2).strip()
        positions.append((m.start(), level, title))

    sections = []
    for i, (start, level, title) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(content)
        sections.append({
            "start": start,
            "end": end,
            "level": level,
            "title": title,
            "is_h2": level == 2,
            "is_cl": is_changelog_title(title) and level == 2,
            "is_ref": is_ref_title(title) and level == 2,
        })
    return sections


def process_file(filepath):
    stats = {
        "title_fixed": 0,
        "v1_added": 0,
        "table_converted": 0,
        "sections_appended": 0,
        "ref_fixed": 0,
        "sections_removed": 0,
        "error": None,
    }
    sample_info = []

    try:
        content = read_file_md(str(filepath))
        original = content

        sections = find_section_ranges(content)

        cl_sections = [s for s in sections if s["is_cl"]]
        ref_sections = [s for s in sections if s["is_ref"]]

        all_entries = []

        if cl_sections:
            stats["title_fixed"] = 1
            stats["sections_removed"] += len(cl_sections)
            sample_info.append(f"清理 {len(cl_sections)} 个旧更新日志/Changelog 章节")

            had_table = False
            had_list = False

            for s in cl_sections:
                sec_text = content[s["start"]:s["end"]]
                entries = extract_changelog_entries(sec_text)
                if entries:
                    if "|" in sec_text and any(l.strip().startswith("|") for l in sec_text.split("\n")[1:5]):
                        had_table = True
                    else:
                        had_list = True
                all_entries.extend(entries)

            if had_list and not had_table:
                stats["table_converted"] = 1
                sample_info.append("列表格式 → 三列表格")

        if ref_sections:
            stats["sections_removed"] += len(ref_sections)
            sample_info.append(f"清理 {len(ref_sections)} 个旧参考文件章节")
            stats["ref_fixed"] = 1

        remove_ranges = []
        for s in cl_sections + ref_sections:
            remove_ranges.append((s["start"], s["end"]))

        remove_ranges.sort(key=lambda x: -x[0])
        new_content = content
        for start, end in remove_ranges:
            new_content = new_content[:start] + new_content[end:]

        new_content = new_content.rstrip()

        seen_e = set()
        clean_entries = []
        for e in all_entries:
            d, v, desc = e
            if d == V1_DATE and v == V1_VERSION:
                continue
            if not d and not v and not desc:
                continue
            key = (d, v, desc)
            if key in seen_e:
                continue
            seen_e.add(key)
            clean_entries.append(e)

        v1_exists = any(d == V1_DATE and v == V1_VERSION for d, v, _ in clean_entries)
        if not v1_exists:
            stats["v1_added"] = 1
            sample_info.append(f"补充 v1.0 + {V1_DATE} 条目")

        cl_lines = [f"## Changelog", "", STANDARD_CL_HEADER]
        v1_row = f"| {V1_DATE} | {V1_VERSION} | {V1_DESC} |"
        cl_lines.append(v1_row)
        for d, v, desc in clean_entries:
            ds = d if d else ""
            vs = v if v else ""
            descs = desc.replace("|", "\\|") if desc else ""
            row = f"| {ds} | {vs} | {descs} |"
            if row != v1_row:
                cl_lines.append(row)
        cl_block = "\n".join(cl_lines)

        if not stats["sections_removed"]:
            stats["sections_appended"] = 1
            sample_info.append("无旧章节，在末尾追加标准参考文件与 Changelog")
        else:
            stats["sections_appended"] = 1
            sample_info.append("在末尾重建标准参考文件与 Changelog")

        stats["ref_fixed"] = 1

        final = new_content + "\n\n---\n\n" + STANDARD_REF + "\n\n" + cl_block + "\n"

        if final != original:
            write_file_md(str(filepath), final)

        stats["sample"] = sample_info
        return stats

    except Exception as e:
        stats["error"] = str(e)
        stats["sample"] = [f"ERROR: {e}"]
        return stats


def main():
    target_path = Path(TARGET_DIR)
    md_files = sorted([f for f in target_path.glob("*.md") if f.name not in EXCLUDE_FILES])

    print(f"共发现 {len(md_files)} 个 .md 文件（排除 index.md / progress.md）")
    print("=" * 80)

    totals = {k: 0 for k in ["title_fixed", "v1_added", "table_converted",
                              "sections_appended", "ref_fixed", "sections_removed",
                              "total", "errors"]}
    samples = []
    all_changes = []

    for i, fp in enumerate(md_files):
        s = process_file(fp)
        totals["total"] += 1

        if s["error"]:
            totals["errors"] += 1
            print(f"[ERROR] {fp.name}: {s['error'][:100]}")
            continue

        for k in ["title_fixed", "v1_added", "table_converted",
                  "sections_appended", "ref_fixed", "sections_removed"]:
            totals[k] += s[k]

        changed = any(s[k] for k in ["title_fixed", "v1_added", "table_converted",
                                     "sections_appended", "ref_fixed", "sections_removed"])
        if changed:
            all_changes.append((fp.name, s))
            if len(samples) < 10:
                samples.append((fp.name, s))

    while len(samples) < 10 and len(all_changes) > len(samples):
        samples.append(all_changes[len(samples)])

    print()
    print("=" * 80)
    print("修复统计结果")
    print("=" * 80)
    print(f"总处理文件数:     {totals['total']}")
    print(f"存在问题文件数:   {len(all_changes)}")
    print(f"清理旧章节数:     {totals['sections_removed']}  (更新日志/Changelog + 参考文件)")
    print(f"改标题数:         {totals['title_fixed']}  (更新日志/变更记录 → 标准 Changelog)")
    print(f"补v1条目数:       {totals['v1_added']}  (补充 {V1_DATE} + {V1_VERSION})")
    print(f"转表格数:         {totals['table_converted']}  (列表/纯文字 → 三列表格)")
    print(f"参考文件修正数:   {totals['ref_fixed']}  (标准 🔗 参考文件 表格)")
    print(f"追加章节数:       {totals['sections_appended']}  (标准 参考文件+Changelog)")
    print(f"错误跳过数:       {totals['errors']}")

    print()
    print("=" * 80)
    print(f"抽样验证结果（{min(10, len(samples))} 个原问题文件）")
    print("=" * 80)

    for i, (fname, s) in enumerate(samples, 1):
        print(f"\n[{i}] {fname}")
        tags = []
        if s["title_fixed"]: tags.append("标题修正")
        if s["v1_added"]: tags.append("补v1条目")
        if s["table_converted"]: tags.append("转表格")
        if s["sections_appended"]: tags.append("重建章节")
        if s["ref_fixed"]: tags.append("参考文件")
        if s["sections_removed"]: tags.append(f"清{s['sections_removed']}旧节")
        print(f"  修复类型: {', '.join(tags)}")
        for info in s.get("sample", []):
            print(f"    • {info}")

    print()
    print("=" * 80)
    print("✅ 处理完成！")


if __name__ == "__main__":
    main()
