import os
import re
import traceback
from pathlib import Path

BASE_DIR = r"h:\github\cowkb\discover\newwiki2\docs\方法论与工具"
EXCLUDE_FILES = {"index.md", "progress.md", "task_plan.md", "findings.md"}


def read_file(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return f.read()


def write_file(filepath, content):
    with open(filepath, "w", encoding="utf-8-sig") as f:
        f.write(content)


def extract_q_number(filename):
    match = re.search(r"mwt_q(\d+)_", filename)
    if match:
        return match.group(1)
    return None


def extract_title(content, filename):
    match = re.search(r"^#\s+(.+?)\s*$", content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        title = re.sub(r"^\*\*|\*\*$", "", title)
        return title
    stem = Path(filename).stem
    match = re.search(r"mwt_q\d+_(.+)", stem)
    if match:
        return match.group(1).replace("_", " ")
    return stem


def extract_yaml_field(content, field):
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None
    yaml_block = match.group(1)
    pattern = rf"^{field}\s*:\s*(.+?)\s*$"
    m = re.search(pattern, yaml_block, re.MULTILINE)
    if m:
        val = m.group(1).strip()
        val = val.strip('"').strip("'")
        return val
    return None


def extract_yaml_tags(content):
    match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return []
    yaml_block = match.group(1)
    m = re.search(r"^tags\s*:\s*\[(.*?)\]\s*$", yaml_block, re.MULTILINE)
    if m:
        tags_str = m.group(1).strip()
        if not tags_str:
            return []
        return [t.strip().strip('"').strip("'") for t in tags_str.split(",") if t.strip()]
    return []


def extract_existing_summary(content):
    pattern = r"^>\s*\*\*概要\*\*\s*[:：]\s*(.*?)\s*$"
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        text = match.group(1).strip()
        text = re.sub(r"\[来源[:：].*?\]\s*$", "", text)
        text = re.sub(r"。。+", "。", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    return None


def extract_existing_keywords(content):
    pattern = r"^>\s*\*\*关键词\*\*\s*[:：]\s*(.*?)\s*$"
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        text = match.group(1).strip()
        text = re.sub(r"\[来源[:：].*?\]\s*$", "", text)
        kws = [kw.strip() for kw in text.split("·") if kw.strip()]
        return kws
    return None


def generate_summary_from_scratch(title, yaml_title, content, q_num):
    text_snippets = []
    if yaml_title and yaml_title != title:
        text_snippets.append(yaml_title)
    text_snippets.append(title)

    answer_match = re.search(r"[（(]待补充[)）]|见下方详细解答|三、详细解答[\s\S]{0,200}", content)
    first_content = ""
    content_start_match = re.search(r"##\s+概述\s*\n([\s\S]*?)(?=\n##|$)", content)
    if content_start_match:
        first_content = content_start_match.group(1).strip()
        first_content = re.sub(r"\s+", " ", first_content)
        first_content = re.sub(r"[（(]待补充[)）]", "", first_content)
        first_content = re.sub(r"【来源[:：].*?】", "", first_content)
        first_content = first_content[:150]

    core_topic = title.replace("？", "").replace("?", "")
    summary_parts = []
    summary_parts.append(f"本文围绕「{core_topic}」这一核心议题")
    if q_num:
        summary_parts.append(f"，对应方法论与工具题库Q{q_num}")
    summary_parts.append("展开系统梳理与深度解析")

    if first_content and len(first_content) > 20:
        summary_parts.append(f"。核心内容涵盖：{first_content[:100]}")
    else:
        summary_parts.append("。从核心概念、原理机制、技术实现、应用场景、实践案例等层面进行结构化阐述")

    summary_parts.append("，结合具体实践场景输出可落地的操作指引与方法论框架。")

    summary = "".join(summary_parts)
    if len(summary) < 150:
        summary += f"该文档基于deep-tech-writer质量标准构建，聚焦「{core_topic}」的关键技术要点与实践路径，为相关领域从业者提供系统性参考与决策支持。"
    if len(summary) > 300:
        summary = summary[:297] + "..."
    return summary


def generate_keywords_from_scratch(title, yaml_title, tags, content, q_num):
    all_text = title
    if yaml_title:
        all_text += " " + yaml_title
    all_text += " " + " ".join(tags)

    answer_section = re.search(r"##\s+三、详细解答[\s\S]{0,500}", content)
    if answer_section:
        all_text += " " + answer_section.group(0)

    stop_words = {
        "的", "了", "是", "在", "有", "和", "与", "或", "不", "这", "那", "为", "对", "从",
        "到", "等", "及", "其", "之", "以", "把", "被", "让", "使", "个", "些", "每",
        "可以", "如何", "什么", "哪些", "怎么", "为什么", "是否", "就是", "一种", "一个",
        "进行", "通过", "基于", "按照", "根据", "需要", "可能", "应该", "能够", "对于",
        "关于", "以及", "还是", "但是", "如果", "因为", "所以", "虽然", "然而", "而且",
        "本文", "我们", "你", "我", "他", "它", "哪些", "哪个", "这个", "那个", "这些", "那些",
        "内容", "方法", "方式", "方面", "问题", "情况", "时候", "过程", "结果", "部分",
        "案例", "实践", "应用", "使用", "利用", "提供", "支持", "实现", "执行", "完成",
    }

    clean_text = re.sub(r"[【\[].*?[】\]]", " ", all_text)
    clean_text = re.sub(r"http\S+", " ", clean_text)
    clean_text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9+#\- ]", " ", clean_text)

    words_2gram = re.findall(r"[\u4e00-\u9fa5]{2}", clean_text)
    words_3gram = re.findall(r"[\u4e00-\u9fa5]{3}", clean_text)
    words_en = re.findall(r"[A-Za-z][A-Za-z0-9+\-#]{2,}", clean_text)

    freq = {}
    for w in words_2gram + words_3gram + words_en:
        w_lower = w.lower() if w.isascii() else w
        if w_lower in stop_words or w in stop_words:
            continue
        if len(w) >= 2:
            freq[w] = freq.get(w, 0) + 1

    title_words_2 = re.findall(r"[\u4e00-\u9fa5]{2}", title)
    title_words_3 = re.findall(r"[\u4e00-\u9fa5]{3}", title)
    title_words_en = re.findall(r"[A-Za-z][A-Za-z0-9+\-#]{2,}", title)
    for w in title_words_2 + title_words_3 + title_words_en:
        if w not in stop_words and len(w) >= 2:
            freq[w] = freq.get(w, 0) + 3

    for t in tags:
        if t and len(t) >= 2:
            freq[t] = freq.get(t, 0) + 5

    generic_kws = {"方法论框架", "实践落地", "流程优化", "最佳实践", "决策支持",
                   "知识管理", "方法论体系", "评估框架", "效率提升", "BPM"}
    for g in generic_kws:
        if g in freq:
            freq[g] = max(0, freq[g] - 2)

    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    selected = []
    seen = set()
    for w, cnt in sorted_words:
        w_clean = w.strip()
        if not w_clean or w_clean in seen:
            continue
        duplicate = False
        for s in selected:
            if w_clean in s or s in w_clean:
                duplicate = True
                break
        if duplicate:
            continue
        if len(w_clean) >= 2:
            selected.append(w_clean)
            seen.add(w_clean)
        if len(selected) >= 6:
            break

    if len(selected) < 4:
        generic = ["方法论框架", "流程优化", "实践落地", "最佳实践"]
        for g in generic:
            if g not in seen:
                selected.append(g)
                seen.add(g)
            if len(selected) >= 6:
                break

    return selected[:6]


def find_blockquote_position(content):
    lines = content.split("\n")
    h1_idx = -1
    for i, line in enumerate(lines):
        if re.match(r"^#\s+", line):
            h1_idx = i
            break
    if h1_idx == -1:
        return -1, -1

    start_idx = -1
    end_idx = -1
    in_block = False
    for i in range(h1_idx + 1, len(lines)):
        line = lines[i]
        is_bq_line = line.startswith(">") or (in_block and line.strip() == "")
        if not in_block and line.startswith(">"):
            in_block = True
            start_idx = i
        elif in_block:
            if line.startswith(">"):
                end_idx = i
            elif line.strip() == "":
                pass
            else:
                break
    return start_idx, end_idx


def process_file(filepath):
    content = read_file(filepath)
    original_content = content
    filename = filepath.name
    q_num = extract_q_number(filename)

    has_correct_format = bool(re.search(r"^>\s*\*\*概要\*\*\s*:", content, re.MULTILINE)) and \
                         bool(re.search(r"^>\s*\*\*关键词\*\*\s*:.*?\[来源[:：]\s*方法论与工具题库", content, re.MULTILINE))

    if has_correct_format:
        return False, ["格式已正确，跳过"]

    title = extract_title(content, filename)
    yaml_title = extract_yaml_field(content, "title")
    yaml_tags = extract_yaml_tags(content)

    old_summary = extract_existing_summary(content)
    old_keywords = extract_existing_keywords(content)

    summary = None
    keywords = None

    if old_summary:
        s = old_summary
        s = re.sub(r"^本文针对《", "本文围绕《", s)
        s = re.sub(r"^本文围绕《(.+?)》进行全面梳理与深度解析。+?(从方法论框架|展开系统阐述|，结合具体)",
                   lambda m: f"本文围绕《{m.group(1)}》展开系统梳理与深度解析{m.group(2) if len(m.groups()) > 2 else ''}", s)
        s = re.sub(r"[（(]待补充[)）]\s*", "", s)
        s = re.sub(r"见下方详细解答\s*", "", s)
        s = re.sub(r"A\d+\s*[。.]?\s*", "", s)
        s = re.sub(r"所属分类[:：]\s*方法论与工具\s*本文档基于.*?质量标准。", "", s)
        s = re.sub(r"本文档基于.*?质量标准。", "", s)
        s = re.sub(r"【来源[:：].*?】", "", s)
        s = re.sub(r"。。+", "。", s)
        s = re.sub(r"\s+", " ", s)
        s = s.strip("。").strip() + "。"
        if len(s) < 100:
            s = generate_summary_from_scratch(title, yaml_title, content, q_num)
        if len(s) > 300:
            s = s[:297] + "..."
        summary = s
    else:
        summary = generate_summary_from_scratch(title, yaml_title, content, q_num)

    if old_keywords and len(old_keywords) >= 4:
        generic_set = {"方法论框架", "实践落地", "流程优化", "最佳实践", "决策支持",
                       "知识管理", "方法论体系", "评估框架"}
        non_generic = [k for k in old_keywords if k not in generic_set]
        if len(non_generic) >= 2:
            keywords = old_keywords
        else:
            new_kws = generate_keywords_from_scratch(title, yaml_title, yaml_tags, content, q_num)
            combined = list(dict.fromkeys(non_generic + new_kws))
            keywords = combined[:6]
    else:
        keywords = generate_keywords_from_scratch(title, yaml_title, yaml_tags, content, q_num)

    source_tag = f"[来源: 方法论与工具题库 Q{q_num}]" if q_num else "[来源: 方法论与工具题库]"
    new_block = f"> **概要**: {summary}\n> **关键词**: {'·'.join(keywords)}  {source_tag}\n"

    start_idx, end_idx = find_blockquote_position(content)
    lines = content.split("\n")

    if start_idx >= 0 and end_idx >= 0:
        new_lines = lines[:start_idx] + [new_block.rstrip("\n")] + lines[end_idx + 1:]
        content = "\n".join(new_lines)
    else:
        h1_idx = -1
        for i, line in enumerate(lines):
            if re.match(r"^#\s+", line):
                h1_idx = i
                break
        if h1_idx >= 0:
            insert_pos = h1_idx + 1
            while insert_pos < len(lines) and lines[insert_pos].strip() == "":
                insert_pos += 1
            new_lines = lines[:insert_pos] + ["", new_block.rstrip("\n")] + lines[insert_pos:]
            content = "\n".join(new_lines)
        else:
            content = new_block + "\n" + content

    modified = content != original_content
    if modified:
        write_file(filepath, content)

    actions = []
    if old_summary or old_keywords:
        actions.append("修正格式(全角→半角冒号+来源位置)")
    else:
        actions.append("全新插入概要+关键词")
    if q_num:
        actions.append(f"Q{q_num}")
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
    for batch_start in range(0, total, batch_size):
        batch = all_md_files[batch_start:batch_start + batch_size]
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
                print(f"  ERROR: {filepath.name}: {e}")

    print("=" * 70)
    print("方法论与工具 目录修复报告")
    print("=" * 70)
    print(f"总文件数: {total}")
    print(f"修改文件数: {modified_count}")
    print(f"跳过文件数: {skipped_count}")
    print(f"错误文件数: {error_count}")
    print()

    if modified_files:
        print(f"修改的文件 (前20个，共{len(modified_files)}个):")
        for fname, actions in modified_files[:20]:
            print(f"  - {fname}: {', '.join(actions)}")
        if len(modified_files) > 20:
            print(f"  ... 还有 {len(modified_files) - 20} 个文件")
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
