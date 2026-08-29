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

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_RE = re.compile(r"^v?\d+(\.\d+)*")
DATE_H_RE = re.compile(r"^#{3,6}\s*(\d{4}-\d{2}-\d{2})")


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
    return "🔗" in t and "参考" in t


def extract_entries_block(text):
    entries = []
    lines = text.split("\n")

    in_changelog_table = False
    for line in lines:
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 3:
                if any(h in cells[0].lower() for h in ["日期", "date", "时间"]):
                    in_changelog_table = True
                    continue
                if re.match(r"^[-:|\s]+$", s.replace("|", "").strip()):
                    continue
                date_cell, ver_cell, desc_cell = cells[0], cells[1], (cells[2] if len(cells) > 2 else "")
                is_date_row = DATE_RE.match(date_cell) or (not DATE_RE.match(date_cell) and not date_cell.startswith("📚") and not date_cell.startswith("📖") and not date_cell.startswith("🏠") and not date_cell.startswith("类型"))
                if is_date_row and DATE_RE.match(date_cell):
                    if not (date_cell == V1_DATE and ver_cell == V1_VERSION):
                        entries.append((date_cell, ver_cell, desc_cell))
                    in_changelog_table = True
                    continue
                if not in_changelog_table:
                    continue

    current_date = None
    for line in lines:
        s = line.strip()
        m = DATE_H_RE.match(s)
        if m:
            current_date = m.group(1)
            continue
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
            if d:
                entries.append((current_date, "", d))
            continue

    seen = set()
    unique = []
    for e in entries:
        if not any(e):
            continue
        if e in seen:
            continue
        seen.add(e)
        unique.append(e)

    return unique


def remove_h2_sections(content):
    h2_positions = []
    for m in re.finditer(r"^##\s+(.+?)\s*$", content, re.MULTILINE):
        h2_positions.append((m.start(), m.group(1).strip()))

    to_remove = []
    extracted = []
    section_ranges = []

    for i, (start, title) in enumerate(h2_positions):
        end = h2_positions[i + 1][0] if i + 1 < len(h2_positions) else len(content)
        section_ranges.append((start, end, title))
        if is_changelog_title(title) or is_ref_title(title):
            sec_text = content[start:end]
            extracted.extend(extract_entries_block(sec_text))
            to_remove.append((start, end))

    return to_remove, extracted, section_ranges


def remove_stray_changelog_blocks(content):
    lines = content.split("\n")
    result_lines = []
    i = 0
    stray_entries = []
    removed_count = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        m = DATE_H_RE.match(stripped)
        if m:
            date_val = m.group(1)
            j = i + 1
            block_lines = [stripped]
            while j < len(lines):
                nxt = lines[j]
                ns = nxt.strip()
                if ns == "" or ns.startswith("---"):
                    if j + 1 < len(lines) and lines[j + 1].strip() == "":
                        break
                    if ns == "---":
                        break
                    block_lines.append(ns)
                    j += 1
                    continue
                if DATE_H_RE.match(ns):
                    break
                if re.match(r"^#{1,2}\s+", ns):
                    break
                if re.match(r"^(?:[-*•]|\d+\.)\s+", ns):
                    block_lines.append(ns)
                    j += 1
                    continue
                break
            block_text = "\n".join(block_lines)
            entries = extract_entries_block(block_text)
            if entries:
                stray_entries.extend(entries)
            removed_count += 1
            i = j
            continue

        result_lines.append(line)
        i += 1

    return "\n".join(result_lines), stray_entries, removed_count


def clean_excessive_hr(content):
    lines = content.split("\n")
    result = []
    hr_count = 0
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s == "---":
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip() == "---":
                i = j
                while i < len(lines) and (lines[i].strip() == "" or lines[i].strip() == "---"):
                    i += 1
                result.append("---")
                continue
            else:
                result.append(lines[i])
                i += 1
        else:
            result.append(lines[i])
            i += 1

    final = "\n".join(result)
    while "\n\n\n---\n\n\n" in final:
        final = final.replace("\n\n\n---\n\n\n", "\n\n---\n\n")
    while "\n\n---\n\n---\n\n" in final:
        final = final.replace("\n\n---\n\n---\n\n", "\n\n---\n\n")
    return final


def process_file(filepath):
    stats = {
        "title_fixed": 0,
        "v1_added": 0,
        "table_converted": 0,
        "sections_appended": 0,
        "ref_fixed": 0,
        "sections_removed": 0,
        "stray_removed": 0,
        "error": None,
        "history_preserved": 0,
    }
    sample_info = []

    try:
        content = read_file_md(str(filepath))
        original = content

        remove_ranges, h2_entries, section_ranges = remove_h2_sections(content)

        if remove_ranges:
            cl_count = 0
            ref_count = 0
            for r_start, r_end in remove_ranges:
                for s_start, s_end, s_title in section_ranges:
                    if s_start == r_start and s_end == r_end:
                        if is_changelog_title(s_title):
                            cl_count += 1
                        if is_ref_title(s_title):
                            ref_count += 1
            stats["sections_removed"] = len(remove_ranges)
            if cl_count:
                stats["title_fixed"] = 1
                sample_info.append(f"清理 {cl_count} 个旧更新日志/Changelog H2章节")
            if ref_count:
                stats["ref_fixed"] = 1
                sample_info.append(f"清理 {ref_count} 个旧参考文件 H2章节")

        remove_ranges.sort(key=lambda x: -x[0])
        step1 = content
        for start, end in remove_ranges:
            step1 = step1[:start] + step1[end:]

        step2, stray_entries, stray_removed = remove_stray_changelog_blocks(step1)
        if stray_removed:
            stats["stray_removed"] = stray_removed
            sample_info.append(f"清理 {stray_removed} 个孤立日期H3+日志块")

        all_entries = h2_entries + stray_entries

        clean_entries = []
        seen_e = set()
        had_list_format = False

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
            if not v:
                had_list_format = True

        if clean_entries:
            stats["history_preserved"] = len(clean_entries)

        v1_exists = any(d == V1_DATE and v == V1_VERSION for d, v, _ in clean_entries)
        if not v1_exists:
            stats["v1_added"] = 1
            sample_info.append(f"补充 v1.0 + {V1_DATE} 条目")

        if had_list_format and clean_entries:
            stats["table_converted"] = 1
            sample_info.append(f"列表格式 → 三列表格（保留 {len(clean_entries)} 条历史）")
        elif clean_entries:
            sample_info.append(f"保留 {len(clean_entries)} 条历史变更记录")

        if not stats["sections_removed"] and not stats["stray_removed"]:
            stats["sections_appended"] = 1
            sample_info.append("无旧日志/参考章节，在末尾追加标准")
        else:
            stats["sections_appended"] = 1
            sample_info.append("在末尾重建标准参考文件与 Changelog")

        stats["ref_fixed"] = 1

        cl_lines = ["## Changelog", "", STANDARD_CL_HEADER]
        v1_row = f"| {V1_DATE} | {V1_VERSION} | {V1_DESC} |"
        cl_lines.append(v1_row)

        added_rows = set()
        added_rows.add((V1_DATE, V1_VERSION, V1_DESC))
        for d, v, desc in clean_entries:
            ds = d if d else ""
            vs = v if v else ""
            descs = desc.replace("|", "\\|") if desc else ""
            if not ds:
                continue
            rk = (ds, vs, descs)
            if rk in added_rows:
                continue
            added_rows.add(rk)
            cl_lines.append(f"| {ds} | {vs} | {descs} |")
        cl_block = "\n".join(cl_lines)

        step2_clean = step2.rstrip()

        sep_count = 0
        for line in step2_clean.split("\n"):
            if line.strip() == "---":
                sep_count += 1

        final_body = clean_excessive_hr(step2_clean)
        final_body = final_body.rstrip()
        if not final_body.endswith("---"):
            pass
        while final_body.endswith("\n"):
            final_body = final_body[:-1]
        while final_body.endswith("---"):
            final_body = final_body[:-3].rstrip()

        final = final_body + "\n\n---\n\n" + STANDARD_REF + "\n\n" + cl_block + "\n"
        final = clean_excessive_hr(final)

        if final != original:
            write_file_md(str(filepath), final)

        stats["sample"] = sample_info
        return stats

    except Exception as e:
        import traceback
        stats["error"] = str(e) + "\n" + traceback.format_exc()[-400:]
        stats["sample"] = [f"ERROR: {e}"]
        return stats


def main():
    target_path = Path(TARGET_DIR)
    md_files = sorted([f for f in target_path.glob("*.md") if f.name not in EXCLUDE_FILES])

    print(f"共发现 {len(md_files)} 个 .md 文件（排除 index.md / progress.md）")
    print("=" * 80)

    totals = {k: 0 for k in ["title_fixed", "v1_added", "table_converted",
                              "sections_appended", "ref_fixed", "sections_removed",
                              "stray_removed", "total", "errors", "history_preserved"]}
    samples = []
    all_changes = []

    for i, fp in enumerate(md_files):
        s = process_file(fp)
        totals["total"] += 1

        if s["error"]:
            totals["errors"] += 1
            print(f"[ERROR] {fp.name}: {s['error'][:150]}")
            continue

        for k in totals:
            if k in s and k != "errors" and k != "total":
                totals[k] += s[k]

        changed = any(s[k] for k in ["title_fixed", "v1_added", "table_converted",
                                     "sections_appended", "ref_fixed",
                                     "sections_removed", "stray_removed"])
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
    print(f"清理旧H2章节数:   {totals['sections_removed']}  (更新日志/Changelog + 参考文件)")
    print(f"清理孤立日志块:   {totals['stray_removed']}  (H3+日期标题+列表)")
    print(f"改标题数:         {totals['title_fixed']}  (更新日志/变更记录 → 标准 Changelog)")
    print(f"补v1条目数:       {totals['v1_added']}  (补充 {V1_DATE} + {V1_VERSION})")
    print(f"转表格数:         {totals['table_converted']}  (列表/纯文字 → 三列表格)")
    print(f"保留历史记录数:   {totals['history_preserved']}  (原变更条目)")
    print(f"参考文件修正数:   {totals['ref_fixed']}  (标准 🔗 参考文件 表格)")
    print(f"追加/重建章节数:  {totals['sections_appended']}  (标准 参考文件+Changelog)")
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
        if s["sections_removed"]: tags.append(f"清H2×{s['sections_removed']}")
        if s["stray_removed"]: tags.append(f"清孤块×{s['stray_removed']}")
        if s["history_preserved"]: tags.append(f"留史×{s['history_preserved']}")
        print(f"  修复类型: {', '.join(tags)}")
        for info in s.get("sample", []):
            print(f"    • {info}")

    print()
    print("=" * 80)
    print("✅ 处理完成！")


if __name__ == "__main__":
    main()
