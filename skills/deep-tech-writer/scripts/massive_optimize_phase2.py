#!/usr/bin/env python3
"""
AI知识库文档批量深度优化框架 - Phase 2: LLM推理结果应用
将LLM生成的概要、关键词、背景、要点写入对应文件
"""

import re
import json
import sys
from pathlib import Path


def insert_blockquote_header(content, summary, keywords):
    """在frontmatter后、标题后插入blockquote的概要和关键词"""
    blockquote = f"> **概要**: {summary}\n> \n> **关键词**: {keywords}\n\n"
    
    fm_match = re.match(r"^(---\n.*?\n---\n)", content, re.DOTALL)
    if fm_match:
        fm_end = fm_match.end()
        after_fm = content[fm_end:]
        
        h1_match = re.search(r"^(#\s+.+?\n)", after_fm, re.MULTILINE)
        if h1_match:
            h1_end = fm_end + h1_match.end()
            return content[:h1_end] + "\n" + blockquote + content[h1_end:]
        else:
            return content[:fm_end] + "\n" + blockquote + after_fm
    else:
        h1_match = re.search(r"^(#\s+.+?\n)", content, re.MULTILINE)
        if h1_match:
            h1_end = h1_match.end()
            return content[:h1_end] + "\n" + blockquote + content[h1_end:]
        else:
            return blockquote + content


def insert_background_points(content, background, core_points):
    """在标题后/概述前插入🌐背景和💡核心要点"""
    section = f"\n## 🌐 背景\n\n{background}\n\n## 💡 核心要点\n\n"
    for i, pt in enumerate(core_points, 1):
        section += f"{i}. {pt}\n"
    section += "\n"
    
    after_h1 = None
    h1_match = re.search(r"^#\s+.+?\n", content, re.MULTILINE)
    if h1_match:
        after_h1 = h1_match.end()
    
    if after_h1:
        rest = content[after_h1:]
        overview_match = re.search(r"^##\s+(概述|一、核心概念)", rest, re.MULTILINE)
        if overview_match:
            idx = after_h1 + overview_match.start()
            return content[:idx] + section + content[idx:]
        else:
            return content[:after_h1] + section + rest
    return section + content


def apply_llm_result(file_path, summary, keywords, background=None, core_points=None):
    """将LLM结果应用到文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, f"读取失败: {e}"
    
    if re.search(r">\s*\*\*概要\*\*", content):
        return True, "已有概要，跳过"
    
    content = insert_blockquote_header(content, summary, keywords)
    
    if background and core_points:
        if "## 🌐 背景" not in content:
            content = insert_background_points(content, background, core_points)
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True, "成功"
    except Exception as e:
        return False, f"写入失败: {e}"


def apply_batch(batch_id, results):
    """批量应用结果
    results格式: {file_path: {"summary": str, "keywords": str, "background": str, "core_points": [str]}}
    """
    report = []
    ok = 0
    fail = 0
    skip = 0
    
    for fp, data in results.items():
        status, msg = apply_llm_result(
            fp,
            data.get("summary", ""),
            data.get("keywords", ""),
            data.get("background"),
            data.get("core_points"),
        )
        if status and msg == "成功":
            ok += 1
        elif status:
            skip += 1
        else:
            fail += 1
        report.append({"file": fp, "status": msg})
    
    print(f"Batch {batch_id} 结果: 成功={ok}, 跳过={skip}, 失败={fail}")
    return report, {"ok": ok, "skip": skip, "fail": fail}


def main():
    if len(sys.argv) < 3:
        print("用法: python massive_optimize_phase2.py <batch_id> <results_json>")
        print("results_json格式: {\"file_path\": {\"summary\": \"...\", \"keywords\": \"...\", \"background\": \"...\", \"core_points\": [...]}}")
        sys.exit(1)
    
    batch_id = sys.argv[1]
    results_file = Path(sys.argv[2])
    
    if not results_file.exists():
        print(f"错误: 结果文件不存在: {results_file}")
        sys.exit(1)
    
    with open(results_file, "r", encoding="utf-8") as f:
        results = json.load(f)
    
    report, stats = apply_batch(batch_id, results)
    
    out_report = results_file.parent / f"_report_{batch_id}.json"
    with open(out_report, "w", encoding="utf-8") as f:
        json.dump({"stats": stats, "detail": report}, f, ensure_ascii=False, indent=2)
    print(f"报告已保存至: {out_report}")


if __name__ == "__main__":
    main()
