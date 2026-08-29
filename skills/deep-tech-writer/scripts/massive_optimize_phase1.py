#!/usr/bin/env python3
"""
AI知识库文档批量深度优化框架 - Phase 1: 自动化处理
处理3个目标目录：AI-Agent技术架构、AI伦理与安全、AI应用与落地实践
功能：1. 清理噪声词 2. 自动生成目录(>100行) 3. 统一添加参考文件和Changelog 4. 标记需要LLM推理的文件
"""

import re
import os
import json
import sys
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(r"h:\github\cowkb\discover\newwiki2\docs")
SKILL_DIR = Path(r"h:\github\cowkb\skills\deep-tech-writer")
PROGRESS_FILE = SKILL_DIR / "scripts" / "_optimize_progress.json"
STATS_FILE = SKILL_DIR / "scripts" / "_optimize_stats.json"

TARGET_DIRS = ["AI-Agent技术架构", "AI伦理与安全", "AI应用与落地实践"]
EXCLUDE_NAMES = {"index.md", "progress.md", "task_plan.md", "findings.md"}

NOISE_PATTERNS = [
    r"低代码AI开发",
    r"规模化落地",
    r"范式跃迁",
    r"Vibe\s*Coding",
    r"Agentic\s*Engineering",
    r"通用市场数据",
]


def get_all_valid_files():
    """获取所有有效文件列表"""
    files = []
    for d in TARGET_DIRS:
        dpath = BASE_DIR / d
        if not dpath.exists():
            continue
        for f in dpath.rglob("*.md"):
            if f.name in EXCLUDE_NAMES:
                continue
            if f.name.startswith("_"):
                continue
            if "JSON" in str(f):
                continue
            files.append(f)
    return sorted(files)


def count_lines(content):
    """统计文件行数"""
    return len(content.splitlines())


def extract_q_number(filename):
    """从文件名提取Q编号，如aag_q12_a -> Q12, aap_q1_ai_nl -> Q1"""
    m = re.search(r"_q(\d+)", filename)
    if m:
        return f"Q{m.group(1)}"
    return "未识别"


def extract_title_and_category(content):
    """提取标题和分类"""
    title = ""
    category = ""
    
    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        t_match = re.search(r"title:\s*(.+)", fm)
        if t_match:
            title = t_match.group(1).strip().strip('"').strip("'")
        c_match = re.search(r"category:\s*(.+)", fm)
        if c_match:
            category = c_match.group(1).strip()
    
    if not title:
        h_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h_match:
            title = h_match.group(1).strip()
    
    return title, category


def clean_noise(content):
    """清理不相关噪声词"""
    cleaned = content
    for pattern in NOISE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)
    cleaned = re.sub(r" +", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned


def has_existing_blockquote_header(content):
    """检查是否已有概要/关键词blockquote"""
    return bool(re.search(r">\s*\*\*概要\*\*", content)) or bool(re.search(r">\s*\*\*关键词\*\*", content))


def has_existing_toc(content):
    """检查是否已有目录"""
    return "## 📑" in content or "## 目录" in content or "## 📑 目录" in content


def has_existing_references(content):
    """检查是否已有参考文件章节"""
    patterns = [r"##\s*🔗\s*参考文件", r"##\s*参考文件", r"##\s*参考来源", r"##\s*七、参考来源"]
    return any(re.search(p, content) for p in patterns)


def has_existing_changelog(content):
    """检查是否已有Changelog章节"""
    patterns = [r"##\s*Changelog", r"##\s*变更记录", r"##\s*更新日志", r"##\s*\d+\.\s*变更记录"]
    return any(re.search(p, content) for p in patterns)


def generate_toc(content):
    """基于##和###标题生成目录"""
    headers = []
    lines = content.splitlines()
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if stripped.startswith("## 📑") or stripped.startswith("## 目录"):
            continue
        match = re.match(r"^(#{2,3})\s+(.+)$", stripped)
        if match:
            level = len(match.group(1))
            h_title = match.group(2).strip()
            h_title_clean = re.sub(r"[一-龥0-9A-Za-z]|[（）()【】\[\]、，,。.：:；;！!？?_\-—/\|]","",h_title)
            anchor = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]", "", h_title)
            headers.append((level, h_title, anchor))
    
    if len(headers) < 3:
        return ""
    
    toc_lines = ["## 📑 目录", ""]
    for level, h_title, anchor in headers:
        indent = "  " * (level - 2)
        toc_lines.append(f"{indent}- [{h_title}](#{anchor})")
    toc_lines.append("")
    return "\n".join(toc_lines) + "\n"


def extract_references_from_content(content, filename):
    """从内容中提取引用的参考文件"""
    refs = []
    
    source_matches = re.findall(r"【来源：([^】]+)】", content)
    for s in source_matches:
        refs.append(f"- 原始素材: {s}")
    
    bracket_matches = re.findall(r"\[来源[：:]\s*([^\]]+)\]", content)
    for s in bracket_matches:
        refs.append(f"- 权威来源: {s}")
    
    url_matches = re.findall(r"https?://[^\s)\]>]+", content)
    for i, url in enumerate(url_matches[:10]):
        refs.append(f"- 外部链接: {url}")
    
    refs.append(f"- 题库来源: {filename[:-3]}")
    
    return list(dict.fromkeys(refs))


def generate_references_section(content, filename):
    """生成参考文件章节"""
    refs = extract_references_from_content(content, filename)
    section_lines = [
        "## 🔗 参考文件",
        "",
    ]
    for r in refs:
        section_lines.append(r)
    if not refs:
        section_lines.append("- 原始问答素材")
    section_lines.append("")
    return "\n".join(section_lines) + "\n"


def generate_changelog_section():
    """生成Changelog三列表格"""
    return """
## Changelog

| 版本 | 日期 | 变更说明 |
|:-----|:-----|:---------|
| v1.0 | 2026-07-29 | 全面深度优化：添加概要关键词blockquote、目录、背景要点、参考文件、Changelog统一格式 |
"""


def is_simple_qa(content):
    """判断是否为简略问答格式（内容少、结构简单）"""
    lines = content.splitlines()
    if len(lines) > 100:
        return False
    
    answer_patterns = [
        r"^\*\*A\d*\.\*\*",
        r"^A\s*[:：]",
        r"详细解答",
        r"^\*\*回答\*\*",
    ]
    has_answer = any(re.search(p, content, re.MULTILINE) for p in answer_patterns)
    
    has_many_sections = content.count("## ") >= 6
    
    return has_answer and not has_many_sections


def is_empty_template(content):
    """判断是否为空模板文件"""
    stripped = re.sub(r"[#\-\s>（）()【】\[\]、，,。.：:；;！!？?_\n]", "", content)
    stripped = re.sub(r"（待补充）|\.\.\.|待补充|详见.*", "", stripped)
    return len(stripped) < 200


def insert_after_frontmatter(content, new_text):
    """在frontmatter后面插入内容"""
    fm_match = re.match(r"^(---\n.*?\n---\n)", content, re.DOTALL)
    if fm_match:
        fm_end = fm_match.end()
        return content[:fm_end] + "\n" + new_text + content[fm_end:]
    else:
        return new_text + content


def insert_before_h1(content, new_text):
    """在第一个# 标题前插入内容"""
    h1_match = re.search(r"^#\s+", content, re.MULTILINE)
    if h1_match:
        idx = h1_match.start()
        return content[:idx] + new_text + "\n" + content[idx:]
    return new_text + "\n" + content


def find_section_end(content, section_patterns):
    """找到指定章节结束位置（下一个##章节或文件末尾）"""
    earliest = len(content)
    for pat in section_patterns:
        for m in re.finditer(pat, content):
            if m.start() < earliest:
                earliest = m.start()
    return earliest


def process_file(fpath):
    """处理单个文件 - Phase 1自动化处理
    返回: (处理状态, 是否需要LLM处理, 信息字典)
    """
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return "error_read", False, {"error": str(e)}
    
    original_len = len(content)
    filename = fpath.name
    q_num = extract_q_number(filename)
    title, category = extract_title_and_category(content)
    line_count = count_lines(content)
    
    needs_llm = False
    changes_made = []
    
    is_empty = is_empty_template(content)
    is_simple = is_simple_qa(content)
    
    cleaned = clean_noise(content)
    if cleaned != content:
        changes_made.append("clean_noise")
    content = cleaned
    
    if not has_existing_toc(content) and line_count > 100:
        toc = generate_toc(content)
        if toc:
            content = insert_after_frontmatter(content, toc)
            changes_made.append("add_toc")
    
    ref_added = False
    if not has_existing_references(content):
        ref_section = generate_references_section(content, filename)
        last_h2 = list(re.finditer(r"^##\s+", content, re.MULTILINE))
        if last_h2:
            insert_idx = last_h2[-1].start()
            while insert_idx > 0 and content[insert_idx-1] != "\n":
                insert_idx -= 1
            content = content[:insert_idx] + ref_section + "\n" + content[insert_idx:]
        else:
            content = content.rstrip() + "\n\n" + ref_section
        changes_made.append("add_references")
        ref_added = True
    
    cl_added = False
    if not has_existing_changelog(content):
        changelog = generate_changelog_section()
        content = content.rstrip() + "\n\n" + changelog
        changes_made.append("add_changelog")
        cl_added = True
    
    if not has_existing_blockquote_header(content):
        needs_llm = True
    
    if is_simple and not ("🌐" in content and "💡" in content):
        needs_llm = True
    
    if is_empty:
        needs_llm = True
    
    try:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return "error_write", False, {"error": str(e)}
    
    info = {
        "file": str(fpath),
        "filename": filename,
        "q_number": q_num,
        "title": title,
        "category": category,
        "lines": line_count,
        "orig_len": original_len,
        "new_len": len(content),
        "is_empty": is_empty,
        "is_simple_qa": is_simple,
        "changes": changes_made,
    }
    return "ok", needs_llm, info


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed": [], "llm_queue": [], "batches": [], "stats": {"total": 0, "processed": 0, "ok": 0, "errors": 0, "needs_llm": 0}}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def save_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def main():
    print(f"[{datetime.now()}] 开始 Phase 1 自动化处理...")
    progress = load_progress()
    
    all_files = get_all_valid_files()
    print(f"发现有效文件: {len(all_files)} 个")
    
    already_done = set(progress.get("processed", []))
    to_process = [f for f in all_files if str(f) not in already_done]
    print(f"待处理: {len(to_process)} 个 (已处理 {len(already_done)} 个)")
    
    stats = progress.get("stats", {"total": len(all_files), "processed": 0, "ok": 0, "errors": 0, "needs_llm": 0})
    stats["total"] = len(all_files)
    
    llm_queue = progress.get("llm_queue", [])
    
    batch_size = 20
    errors = []
    
    for i, fpath in enumerate(to_process):
        status, needs_llm, info = process_file(fpath)
        
        if status == "ok":
            stats["ok"] += 1
            stats["processed"] += 1
            progress["processed"].append(str(fpath))
            if needs_llm:
                stats["needs_llm"] += 1
                llm_queue.append(info)
        else:
            stats["errors"] += 1
            errors.append({"file": str(fpath), "status": status, "info": info})
        
        if (i + 1) % 50 == 0:
            print(f"  ... 进度 {i+1}/{len(to_process)}, OK={stats['ok']}, Error={stats['errors']}, NeedsLLM={stats['needs_llm']}")
            save_progress(progress)
    
    batches = []
    for i in range(0, len(llm_queue), batch_size):
        batch = llm_queue[i:i+batch_size]
        batch_id = f"batch_{len(batches)+1:03d}"
        batch_file = SKILL_DIR / "scripts" / f"_llm_{batch_id}.json"
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump({"batch_id": batch_id, "created_at": str(datetime.now()), "items": batch}, f, ensure_ascii=False, indent=2)
        batches.append({"batch_id": batch_id, "file": str(batch_file), "size": len(batch), "status": "pending"})
    
    progress["llm_queue"] = llm_queue
    progress["batches"] = batches
    progress["stats"] = stats
    save_progress(progress)
    save_stats(stats)
    
    print(f"\n{'='*60}")
    print(f"Phase 1 完成!")
    print(f"  总计:     {stats['total']}")
    print(f"  成功:     {stats['ok']}")
    print(f"  错误:     {stats['errors']}")
    print(f"  需LLM处理: {stats['needs_llm']}")
    print(f"  LLM批数:  {len(batches)} (每批 {batch_size} 个)")
    print(f"\n进度文件: {PROGRESS_FILE}")
    print(f"统计文件: {STATS_FILE}")
    for b in batches[:5]:
        print(f"  {b['batch_id']}: {b['file']} ({b['size']}个)")
    if len(batches) > 5:
        print(f"  ... 还有 {len(batches)-5} 个批次")
    
    if errors:
        error_file = SKILL_DIR / "scripts" / "_errors_phase1.json"
        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
        print(f"\n错误列表已保存至: {error_file}")
        for e in errors[:10]:
            print(f"  - {e['file']}: {e['status']}")


if __name__ == "__main__":
    main()
